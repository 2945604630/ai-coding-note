"""Durable submission before asynchronous execution; retries are new attempts."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import threading
import time
import traceback

from . import teaching, provenance, execution_context
from .store import Store, decode, uid, utc
from .demo import DemoAdapter
from .ai_provider import make_provider
from .sandbox_service import SandboxService

RUNNING = {'queued', 'connecting', 'generating'}


class Conflict(ValueError):
    pass


class Service:
    def __init__(self, root, model_runner=None):
        teaching.verify_engines()
        self.store = Store(root)
        self.demo = DemoAdapter(self.store)
        self.runner = model_runner or make_provider()
        self.sandbox = SandboxService(self.store)
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='aic-model')
        self.rule_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='aic-rules')
        self.recover()

    def close(self):
        self.sandbox.close()
        self.pool.shutdown(wait=True)
        self.rule_pool.shutdown(wait=True)

    def dispatch(self, aid, mode):
        (self.rule_pool if mode == 'S0' else self.pool).submit(self.run, aid)

    def recover(self):
        with self.store.connection(write=True) as db:
            rows = db.execute("SELECT a.*,t.experiment_id FROM attempts a JOIN turns t USING(turn_id) "
                              "WHERE a.status IN ('queued','connecting','generating')").fetchall()
            for row in rows:
                error = 'server_restarted：服务上次退出时调用未完成；保留工件，请明确重试。'
                artifact = self.store.root / row['artifact_dir']
                artifact.mkdir(parents=True, exist_ok=True)
                self.capture_raw(artifact)
                raw = self.read_raw(artifact)
                (artifact / 'recovery.json').write_text(json.dumps({'error': error, 'utc': utc()}, ensure_ascii=False), encoding='utf-8')
                self.store.update(db, 'attempts', 'attempt_id', row['attempt_id'],
                                  {'status': 'failed', 'error': error, 'completed_at': utc(), 'raw_output': raw})
                self.store.update(db, 'turns', 'turn_id', row['turn_id'],
                                  {'status': 'failed', 'error': error, 'completed_at': utc()})
                db.execute("UPDATE experiments SET status='failed',end_reason='server_restarted' "
                           "WHERE experiment_id=? AND status NOT IN ('completed','paused')", (row['experiment_id'],))
                self.store.event(db, row['experiment_id'], 'call_interrupted_on_restart', {'attempt_id': row['attempt_id']})

    def create(self, payload):
        case = teaching.load_case(payload['feature'], payload['case_id'])
        model_config = teaching.config(payload['feature'], payload['mode'])
        if hasattr(self.runner, 'public_config'):
            provider_config = self.runner.public_config()
            model_config['ai_provider'] = provider_config
            if payload['mode']=='S1':
                model_config['model_requested'] = provider_config['model']
                if provider_config['provider']!='codex_cli':
                    model_config.update(transport=provider_config['provider'],auth='server_configuration',
                                        timeout_seconds=provider_config['timeout_seconds'],reasoning_effort=None)
        schedule = None
        with self.store.connection(write=True) as db:
            key = payload.get('request_id')
            existing = db.execute('SELECT * FROM experiments WHERE create_request_id=?', (key,)).fetchone() if key else None
            if existing:
                for field in ['feature', 'case_id', 'mode', 'source_type']:
                    if field in payload and payload[field] != existing[field]:
                        raise Conflict('新建请求 ID 已用于不同的实验')
                if (payload.get('name') or teaching.LABELS[payload['case_id']]) != existing['name']:
                    raise Conflict('新建请求 ID 已用于不同的实验名称')
                return self.store.experiment(db, existing['experiment_id'])
            eid, version = uid(), uid()
            source_type = payload.get('source_type', 'real_user')
            if self.runner.provenance == 'simulated_model':
                source_type = 'automated_test'
            self.store.insert(db, 'experiments', {
                'experiment_id': eid, 'name': payload.get('name') or teaching.LABELS[payload['case_id']],
                'feature': payload['feature'], 'case_id': payload['case_id'], 'mode': payload['mode'],
                'source_type': source_type, 'model_provenance': self.runner.provenance if payload['mode'] == 'S1' else 'frozen_S0_rules',
                'created_at': utc(), 'ended_at': None, 'status': 'active', 'end_reason': None,
                'current_code_version_id': version, 'case_snapshot': case,
                'model_config': model_config,
                'version_snapshot': teaching.case_versions(case), 'create_request_id': key})
            sources = {'original': case, **case.get('versions', {})}
            for label, data in sources.items():
                self.store.insert(db, 'code_versions', {'version_id': version if label == 'original' else uid(),
                    'experiment_id': eid, 'label': label, 'source': data['source'],
                    'source_sha256': data['source_sha256'], 'verification_status': 'verified_fixture',
                    'execution_allowed': True, 'created_at': utc()})
            self.store.event(db, eid, 'experiment_created', {'source_type': source_type, 'case_id': case['case_id'],
                'entry_point': payload.get('entry_point','experiment'), 'input_origin': provenance.record(payload.get('input_origin'))})
            initial = self.store.experiment(db, eid)
            self.store.update(db, 'experiments', 'experiment_id', eid, {
                'initial_input_snapshot': teaching.make_public(initial, [], '')})
            if payload['feature'] == 'F02':
                schedule = self.new_turn(db, self.store.experiment(db, eid), '', 'initial_question')
        if schedule:
            self.dispatch(schedule, payload['mode'])
        return self.store.get(eid)

    def new_turn(self, db, experiment, answer, request_id, input_origin=None):
        if experiment['feature'] == 'DEMO':
            experiment['demo_evidence_operations'] = [decode(r) for r in db.execute(
                'SELECT * FROM demo_operations WHERE session_id=? ORDER BY created_at,rowid',
                (experiment['experiment_id'],))]
            rows = [decode(r) for r in db.execute(
                'SELECT * FROM sandbox_jobs WHERE session_id=? AND version_id=? '
                'ORDER BY created_at DESC,rowid DESC LIMIT 1',
                (experiment['experiment_id'], experiment['current_code_version_id']))]
            stale = db.execute('SELECT count(*) FROM sandbox_jobs WHERE session_id=? AND version_id!=?',
                               (experiment['experiment_id'], experiment['current_code_version_id'])).fetchone()[0]
            experiment['teaching_execution_context'] = execution_context.project(
                experiment, rows, image_id=self.sandbox.runtime.image_id, stale_count=stale)
        origin = provenance.record(input_origin, experiment)
        value = teaching.make_public(experiment, experiment['turns'], answer, origin)
        # Only a configured exact server secret is redacted; it is never supplied
        # as context, even if student text/program output happens to echo it.
        secret = getattr(getattr(self.runner, 'config', None), 'api_key', '')
        if secret:
            def redact(item):
                if isinstance(item, str): return item.replace(secret, '[REDACTED]')
                if isinstance(item, list): return [redact(x) for x in item]
                if isinstance(item, dict): return {redact(k): redact(v) for k, v in item.items()}
                return item
            redacted = redact(value)
            if redacted != value:
                value = redacted
                value['server_secret_redacted'] = True
        tid = uid()
        self.store.insert(db, 'turns', {'turn_id': tid, 'experiment_id': experiment['experiment_id'],
            'number': len(experiment['turns']) + 1, 'request_id': request_id,
            'question_shown': value['previous_question'], 'answer_raw': answer, 'public_input': value,
            'code_version_id': experiment['current_code_version_id'], 'status': 'queued', 'submitted_at': utc()})
        self.store.event(db, experiment['experiment_id'], 'answer_received', {'turn_id': tid,
            'code_version_id': experiment['current_code_version_id'], 'input_origin': origin})
        if value.get('execution_context') is not None:
            self.store.event(db, experiment['experiment_id'], 'teaching_execution_context_saved', {
                'turn_id': tid, 'version_id': value['current_code_version_id'],
                'source_sha256': value['current_source_sha256'],
                'task_id': value['execution_context']['task_id'], 'status': value['execution_context']['status'],
                'public_input_sha256': hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()})
        return self.new_attempt(db, experiment['experiment_id'], tid, 1, request_id, None)

    def new_attempt(self, db, eid, tid, number, request_id, reason):
        aid = uid()
        self.store.insert(db, 'attempts', {'attempt_id': aid, 'turn_id': tid, 'number': number,
            'status': 'queued', 'requested_at': utc(), 'retry_reason': reason, 'request_id': request_id,
            'artifact_dir': f'artifacts/{eid}/{tid}/A{number:02d}'})
        self.store.update(db, 'turns', 'turn_id', tid, {'status': 'queued', 'error': None, 'completed_at': None,
            'started_at': None, 'generation_started_at': None, 'output': None, 'checks': None,
            'selected_attempt_id': aid, 'elapsed_seconds': None})
        self.store.event(db, eid, 'call_queued', {'turn_id': tid, 'attempt_id': aid, 'retry_reason': reason})
        return aid

    def submit(self, eid, answer, request_id, parent_turn_id, input_origin=None):
        with self.store.connection(write=True) as db:
            e = self.store.experiment(db, eid)
            old = next((t for t in e['turns'] if t['request_id'] == request_id), None)
            if old:
                if old['answer_raw'] != answer:
                    raise Conflict('请求 ID 已用于不同回答')
                return old
            if e['status'] != 'active':
                raise Conflict('实验已暂停、结束或失败，请先恢复或重试')
            turns = e['turns']
            if turns and turns[-1]['status'] in RUNNING:
                raise Conflict('本实验已有调用正在进行')
            if turns and turns[-1]['status'] != 'succeeded':
                raise Conflict('上一轮失败，请使用人工重试')
            if (turns[-1]['turn_id'] if turns else None) != parent_turn_id:
                raise Conflict('页面已过期，请刷新后再回答最新问题')
            limit = {'F01': 1, 'DEMO': 2}.get(e['feature'], 3)
            if len(turns) >= limit:
                raise Conflict('已达到本功能轮次上限')
            aid = self.new_turn(db, e, answer, request_id, input_origin)
        self.dispatch(aid, e['mode'])
        return self.store.get(eid)['turns'][-1]

    def retry(self, tid, reason, request_id):
        with self.store.connection(write=True) as db:
            row = db.execute('SELECT experiment_id FROM turns WHERE turn_id=?', (tid,)).fetchone()
            if not row:
                raise KeyError('轮次不存在')
            e = self.store.experiment(db, row['experiment_id'])
            turn = next(t for t in e['turns'] if t['turn_id'] == tid)
            old = next((a for a in turn['attempts'] if a['request_id'] == request_id), None)
            if old:
                if old['retry_reason'] != reason:
                    raise Conflict('重试请求 ID 已用于不同原因')
                return old
            if turn['status'] not in {'failed', 'blocked'} or turn != e['turns'][-1] or e['status'] == 'completed':
                raise Conflict('只能明确重试当前失败轮次；原输出始终保留')
            aid = self.new_attempt(db, e['experiment_id'], tid, len(turn['attempts']) + 1, request_id, reason)
            self.store.update(db, 'experiments', 'experiment_id', e['experiment_id'],
                              {'status': 'active', 'end_reason': None, 'ended_at': None})
        self.dispatch(aid, e['mode'])
        return {'attempt_id': aid}

    @staticmethod
    def capture_raw(artifact):
        raw, invocation = artifact / 'raw_response.json', artifact / 'invocation.json'
        if not raw.exists() and invocation.exists():
            try:
                args = json.loads(invocation.read_text(encoding='utf-8'))['argv']
                for flag in ['-o', '--output-last-message']:
                    if flag in args:
                        last = Path(args[args.index(flag) + 1])
                        if last.is_file():
                            raw.write_bytes(last.read_bytes())
                        break
            except (OSError, ValueError, KeyError, IndexError):
                pass

    @staticmethod
    def read_raw(artifact):
        raw = artifact / 'raw_response.json'
        return raw.read_text(encoding='utf-8-sig', errors='replace') if raw.exists() else None

    def run(self, aid):
        with self.store.connection(write=True) as db:
            a = decode(db.execute('SELECT * FROM attempts WHERE attempt_id=?', (aid,)).fetchone())
            if not a or a['status'] != 'queued':
                return
            t = decode(db.execute('SELECT * FROM turns WHERE turn_id=?', (a['turn_id'],)).fetchone())
            e = self.store.experiment(db, t['experiment_id'])
            self.store.update(db, 'attempts', 'attempt_id', aid, {'status': 'connecting', 'started_at': utc()})
            self.store.update(db, 'turns', 'turn_id', t['turn_id'], {'status': 'connecting', 'started_at': utc()})
        artifact = self.store.root / a['artifact_dir']
        artifact.parent.mkdir(parents=True, exist_ok=True)
        # This sibling survives even if the transport fails before creating its directory.
        snapshot = artifact.parent / (artifact.name + '_submission.json')
        snapshot.write_text(json.dumps(t['public_input'], ensure_ascii=False, indent=2), encoding='utf-8')
        started = time.perf_counter()
        result, error = None, None
        done = threading.Event()
        def observe_generation():
            while not done.wait(.3):
                events = artifact / 'events.jsonl'
                if events.exists():
                    with events.open('rb') as stream:
                        if b'turn.started' in stream.read(32768):
                            with self.store.connection(write=True) as db:
                                observed = utc()
                                db.execute("UPDATE attempts SET status='generating',generation_started_at=? "
                                           "WHERE attempt_id=? AND status='connecting'", (observed, aid))
                                db.execute("UPDATE turns SET status='generating',generation_started_at=? "
                                           "WHERE turn_id=? AND status='connecting'", (observed, t['turn_id']))
                            return
        observer = threading.Thread(target=observe_generation, daemon=True)
        if e['mode'] == 'S1':
            observer.start()
        try:
            # Legacy DEMO snapshots also bind a saved version, including retries
            # created before the Docker projection existed. Never refresh them.
            version_sensitive = e['feature'] == 'DEMO'
            version_changed = version_sensitive and not execution_context.matches(t['public_input'], e)
            if version_changed:
                result = {'output': None, 'checks': {'display_safe': False, 'issues': ['current_version_changed'],
                          'requests': [], 'teaching_claim_verified': False},
                          'metadata': {'provider_success': True, 'actual_model_call': False,
                                       'provenance': 'version_guard_before_provider'}}
            elif e['mode'] == 'S0':
                result = teaching.rule_result(e['feature'], t['public_input'])
                artifact.mkdir(exist_ok=False)
                for name, content in [('raw_response.json', result['output']), ('validation.json', result['checks'])]:
                    (artifact / name).write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding='utf-8')
            else:
                result = self.runner(e['feature'], t['public_input'], artifact)
            if not version_changed and t['public_input'].get('execution_context') is not None:
                original = result.get('checks') or {}
                checked = teaching.validate_reply(e['feature'], result.get('output'), t['public_input'])
                if not original.get('display_safe'):
                    checked['issues'] = list(dict.fromkeys(checked['issues'] + original.get('issues', ['provider_guard_blocked'])))
                    checked['display_safe'] = False
                result['checks'] = checked
            metadata = result.get('metadata') or {}
            if e['mode'] == 'S1' and not metadata.get('provider_success', metadata.get('CLI_success')):
                error = ('模型调用超时' if metadata.get('timeout') else 'AI Provider 调用未成功或事件完整性检查未通过')
                audit = artifact / 'events_audit.json'
                if audit.exists():
                    errors = json.loads(audit.read_text(encoding='utf-8')).get('errors', [])
                    if errors:
                        error += '；' + json.dumps(errors, ensure_ascii=False)[:2000]
                if metadata.get('parse_error'):
                    error += '；输出解析错误：' + str(metadata['parse_error'])
            elif not result['checks'].get('display_safe'):
                error = '输出被结构、引用或执行事实守卫阻断：' + ', '.join(result['checks'].get('issues', []))
        except Exception as exc:
            error = type(exc).__name__ + ': ' + str(exc)
            artifact.mkdir(parents=True, exist_ok=True)
            (artifact / 'service_error.log').write_text(traceback.format_exc(), encoding='utf-8')
            self.capture_raw(artifact)
        finally:
            done.set()
            if observer.is_alive():
                observer.join(timeout=2)
        elapsed = round(time.perf_counter() - started, 4)
        artifact.mkdir(parents=True, exist_ok=True)
        if error:
            (artifact / 'failure_summary.json').write_text(json.dumps({'error': error, 'utc': utc(),
                'no_fabricated_answer': True}, ensure_ascii=False, indent=2), encoding='utf-8')
        output = result.get('output') if result else None
        checks = result.get('checks') if result else None
        metadata = result.get('metadata') if result else None
        status = 'blocked' if error and checks and not checks.get('display_safe') and (metadata or {}).get('provider_success', (metadata or {}).get('CLI_success', e['mode'] == 'S0')) else 'failed' if error else 'succeeded'
        with self.store.connection(write=True) as db:
            current = self.store.experiment(db, e['experiment_id'])
            if version_sensitive and not execution_context.matches(t['public_input'], current):
                checks = checks or {'issues': [], 'requests': []}
                checks.update(display_safe=False, teaching_claim_verified=False)
                checks['issues'] = list(dict.fromkeys(checks.get('issues', []) + ['current_version_changed']))
                status = 'blocked'
                error = '当前保存版本已变化；原输入与回复保留，禁止作为新版教学结果展示。'
                (artifact / 'failure_summary.json').write_text(json.dumps({'error': error, 'utc': utc(),
                    'no_fabricated_answer': True}, ensure_ascii=False, indent=2), encoding='utf8')
            if checks is not None:
                (artifact / 'web_validation.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf8')
            self.store.update(db, 'attempts', 'attempt_id', aid, {'status': status, 'completed_at': utc(),
                'output': output, 'checks': checks, 'metadata': metadata, 'raw_output': self.read_raw(artifact),
                'elapsed_seconds': elapsed, 'error': error})
            self.store.update(db, 'turns', 'turn_id', t['turn_id'], {'status': status, 'completed_at': utc(),
                'output': output, 'checks': checks, 'selected_attempt_id': aid, 'elapsed_seconds': elapsed, 'error': error})
            self.store.event(db, e['experiment_id'], 'call_finished', {'attempt_id': aid, 'status': status, 'error': error})
            # Manual lifecycle decisions made during a call are respected.
            if current['status'] == 'active':
                reason = teaching.stop_reason(e['feature'], output, t['number']) if not error else 'model_call_failed' if status == 'failed' else 'guard_blocked'
                if reason != 'continue':
                    self.store.update(db, 'experiments', 'experiment_id', e['experiment_id'], {
                        'status': 'failed' if error else 'paused' if reason == 'await_new_evidence' else 'completed',
                        'end_reason': reason, 'ended_at': None if reason == 'await_new_evidence' else utc()})
        if e['feature'] == 'DEMO':
            try:
                self.demo.sync(e['experiment_id'])
            except Exception as exc:
                self.demo.event(e['experiment_id'], 'assistance_import_failed',
                                {'attempt_id': aid, 'error': str(exc), 'validation_status': 'incomplete'})

    def detail(self, eid):
        e = self.store.get(eid)
        e['sandbox'] = {**self.sandbox.status(), 'jobs':self.sandbox.jobs(eid)}
        if e['feature'] == 'DEMO':
            e['demo'] = self.demo.detail(eid)
            # Imported assistance events must be included in the same response.
            e['events'] = self.store.get(eid)['events']
        e['action_labels'] = teaching.ACTION_ZH
        for turn in e['turns']:
            turn['runtime_phase'] = turn['status']
            if turn['status'] == 'connecting' and turn['attempts']:
                events = self.store.root / turn['attempts'][-1]['artifact_dir'] / 'events.jsonl'
                if events.exists():
                    with events.open('rb') as stream:
                        stream.seek(max(0, events.stat().st_size - 32768))
                        tail = stream.read()
                    if b'turn.started' in tail or b'item.' in tail:
                        turn['runtime_phase'] = 'generating'
            if turn['status'] in RUNNING and turn['attempts']:
                log = self.store.root / turn['attempts'][-1]['artifact_dir'] / 'stderr.log'
                if log.exists():
                    with log.open('rb') as stream:
                        stream.seek(max(0, log.stat().st_size - 16384))
                        tail = stream.read().decode('utf-8', errors='replace')
                    if 'request timed out' in tail or 'stream disconnected' in tail:
                        turn['connection_notice'] = 'Codex 出现网络超时，CLI 正在重连；尚未取得有效回复。日志持续保存。'
                    elif 'usage_limit' in tail or 'quota' in tail.lower():
                        turn['connection_notice'] = 'Codex 提示用量 / 额度限制，请查看 stderr.log；尚未取得有效回复。'
        return e

    def control(self, eid, action, input_origin=None):
        with self.store.connection(write=True) as db:
            e = self.store.experiment(db, eid)
            if e['status'] == 'completed':
                raise Conflict('已结束的实验不能继续；请新建实验')
            if action == 'resume':
                if e['status'] != 'paused':
                    raise Conflict('仅暂停实验可恢复')
                if e['turns'] and e['turns'][-1]['status'] in {'failed', 'blocked'}:
                    raise Conflict('请明确重试失败轮次')
                values = {'status': 'active', 'end_reason': None, 'ended_at': None}
                if e['turns'] and e['turns'][-1]['status'] == 'succeeded':
                    last = e['turns'][-1]
                    reason = teaching.stop_reason(e['feature'], last['output'], last['number'])
                    if reason not in {'continue', 'await_new_evidence'}:
                        values = {'status': 'completed', 'end_reason': reason, 'ended_at': utc()}
            else:
                values = {'status': 'paused' if action == 'pause' else 'completed',
                          'end_reason': {'pause': 'manual_pause', 'end': 'manual_end', 'complete': 'manual_early_complete'}[action],
                          'ended_at': None if action == 'pause' else utc()}
            self.store.update(db, 'experiments', 'experiment_id', eid, values)
            self.store.event(db, eid, 'manual_' + action, {'input_origin': provenance.record(input_origin,e)})
        return self.detail(eid)

    def add_code(self, eid, source, parent_version_id=None, input_origin=None):
        row = {'version_id': uid(), 'experiment_id': eid, 'label': '用户提交版本', 'source': source,
               'source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
               'verification_status': 'unverified', 'execution_allowed': False, 'created_at': utc()}
        with self.store.connection(write=True) as db:
            e = self.store.experiment(db, eid)
            parent = next((v for v in e['code_versions']
                           if v['version_id'] == (parent_version_id or e['current_code_version_id'])), None)
            if parent is None:
                raise ValueError('修改来源版本不属于当前会话')
            self.store.insert(db, 'code_versions', row)
            self.store.update(db, 'experiments', 'experiment_id', eid, {'current_code_version_id': row['version_id']})
            from experiments.feature_validation.F04_self_modification.core import difference
            self.store.event(db, eid, 'unverified_code_recorded', {'version_id': row['version_id'],
                'source_hash': row['source_sha256'], 'parent_version_id': parent['version_id'],
                'parent_source_hash': parent['source_sha256'], 'modification': difference(parent['source'], source),
                'execution_allowed': False, 'source': 'user_text', 'validation_status': 'pending_review',
                'input_origin': provenance.record(input_origin,e)})
        return row

    def feedback(self, tid, values):
        origin = values.pop('input_origin',None)
        with self.store.connection(write=True) as db:
            row = db.execute('SELECT * FROM turns WHERE turn_id=?', (tid,)).fetchone()
            if not row:
                raise KeyError('轮次不存在')
            result = {'feedback_id': uid(), 'turn_id': tid, 'created_at': utc(), **values}
            self.store.insert(db, 'feedback', result)
            self.store.event(db, row['experiment_id'], 'feedback_revision_added', {'feedback_id': result['feedback_id'],
                'input_origin': provenance.record(origin)})
        return result

    def note(self, eid, text, input_origin=None):
        result = {'note_id': uid(), 'experiment_id': eid, 'created_at': utc(), 'text': text}
        with self.store.connection(write=True) as db:
            self.store.experiment(db, eid)
            self.store.insert(db, 'notes', result)
            self.store.event(db, eid, 'note_added', {'note_id': result['note_id'], 'source': 'user_text',
                'input_origin': provenance.record(input_origin)})
        return result

    def ui_action(self, eid, action, input_origin=None):
        with self.store.connection(write=True) as db:
            e=self.store.experiment(db,eid)
            value={'action':action,'code_version_id':e['current_code_version_id'],
                   'input_origin':provenance.record(input_origin,e)}
            self.store.event(db,eid,'learning_ui_action',value)
        return {'session_id':eid,'recorded':True,**value}
