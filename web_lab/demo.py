"""Thin session adapters around the frozen F03/F04/F05 implementations.

There is deliberately no arbitrary-source execution or runtime approval API.
"""
import base64
import hashlib
import json
import threading
import traceback

from experiments.feature_validation.F04_self_modification import core as f04
from experiments.feature_validation.F05_independent_assessment import core as f05, records, catalog
from .store import decode, uid, utc
from . import provenance


def sha(source):
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


class DemoAdapter:
    def __init__(self, store):
        self.store = store
        self.lock = threading.RLock()
        with store.connection(write=True) as db:
            pending = db.execute("SELECT * FROM demo_operations WHERE status='running'").fetchall()
            for row in pending:
                store.update(db, 'demo_operations', 'operation_id', row['operation_id'],
                    {'status': 'interrupted', 'completed_at': utc(), 'error': 'server_restarted; evidence may be partial'})
                store.event(db, row['session_id'], 'demo_operation_interrupted',
                            {'operation_id': row['operation_id'], 'validation_status': 'incomplete'})

    def session(self, eid):
        e = self.store.get(eid)
        if e['feature'] != 'DEMO':
            raise ValueError('此接口仅适用于 F01～F05 Demo 会话')
        return e

    def event(self, eid, kind, payload):
        with self.store.connection(write=True) as db:
            self.store.event(db, eid, kind, payload)

    def operations(self, eid):
        with self.store.connection() as db:
            out=[decode(r) for r in db.execute(
                'SELECT * FROM demo_operations WHERE session_id=? ORDER BY created_at,rowid', (eid,))]
            corrections=[decode(r) for r in db.execute("SELECT * FROM events WHERE experiment_id=? AND type='input_origin_corrected' ORDER BY created_at,rowid",(eid,))]
            for op in out:
                op['effective_input_origin']=op['payload'].get('input_origin',provenance.record())
                for c in corrections:
                    if c['payload'].get('scope')=='verification' and c['payload'].get('operation_id')==op['operation_id']:
                        op['input_origin_correction']={**c['payload'],'event_id':c['event_id']}
                        op['effective_input_origin']={'kind':c['payload']['kind'],'basis':'append_only_source_correction',
                            'correction_event_id':c['event_id'],'real_student_verified':False}
            return out

    def verify(self, eid, version_id, input_origin=None):
        with self.lock:
            e = self.session(eid)
            origin=provenance.record(input_origin,e)
            version = next((v for v in e['code_versions'] if v['version_id'] == version_id), None)
            if version is None:
                self.event(eid, 'verification_rejected', {'requested_version_id': version_id,
                    'error': 'version_not_in_session', 'validation_status': 'blocked', 'executed': False})
                raise ValueError('源码版本不属于当前会话')
            linked = next((r['payload'] for r in reversed(e['events'])
                           if r['type'] == 'unverified_code_recorded' and r['payload'].get('version_id') == version_id), {})
            parent = next((v for v in e['code_versions'] if v['version_id'] == linked.get('parent_version_id')), None)
            parent = parent or next(v for v in e['code_versions'] if v['label'] == 'original')
            registry = f04.load()['SUM']['versions']
            approved = lambda h: next((k for k, v in registry.items() if v['source_hash'] == h), None)
            before, after = approved(parent['source_sha256']), approved(version['source_sha256'])
            oid = uid()
            folder = self.store.root / 'demo' / 'evidence' / oid
            row = {'operation_id': oid, 'session_id': eid, 'kind': 'F04_F03_version_comparison',
                'status': 'running', 'version_id': version_id, 'parent_version_id': parent['version_id'],
                'artifact_dir': str(folder.relative_to(self.store.root)), 'created_at': utc(),
                'payload': {'source_hash': version['source_sha256'], 'parent_source_hash': parent['source_sha256'],
                            'input_origin':origin,
                            'case_id': e['case_id'], 'case_version': e['version_snapshot'], 'catalog': 'F04'}}
            with self.store.connection(write=True) as db:
                self.store.insert(db, 'demo_operations', row)
                self.store.event(db, eid, 'verification_started', {'operation_id': oid, **row['payload']})
            try:
                # compare itself refuses an unknown source/hash before execution.
                result = f04.compare('SUM', before or 'unreviewed_parent', after or 'unreviewed_submission',
                    submitted_source=version['source'], before_hash=parent['source_sha256'],
                    after_hash=version['source_sha256'], inputs=[[0], [1], [3]], record_dir=folder,
                    context={'session_id': eid, 'student_answer': e['turns'][-1]['answer_raw'] if e['turns'] else '',
                             'previous_question': e['case_snapshot']['teaching_question']},
                    origin=provenance.data_label(origin))
                payload = {**row['payload'], 'result': result,
                           'executed': bool(result['tests']), 'source': 'frozen_F04_compare_using_F03'}
                status = result['status']
                if not after and not result['tests']:
                    status = 'pending_review'
                error = result.get('error_reason')
            except Exception:
                folder.mkdir(parents=True, exist_ok=True)
                error = traceback.format_exc()
                (folder / 'adapter_failure.log').write_text(error, encoding='utf-8')
                payload = {**row['payload'], 'executed': None, 'partial_evidence_possible': True}
                status = 'failed'
            with self.store.connection(write=True) as db:
                self.store.update(db, 'demo_operations', 'operation_id', oid,
                    {'status': status, 'completed_at': utc(), 'error': error, 'payload': payload})
                if result_safe := (payload.get('result') or {}).get('tests'):
                    if all(t['after']['execution_success'] for t in result_safe):
                        self.store.update(db, 'code_versions', 'version_id', version_id,
                            {'verification_status': 'reviewed_execution_recorded', 'execution_allowed': True})
                self.store.event(db, eid, 'verification_finished', {'operation_id': oid, 'version_id': version_id,
                    'parent_version_id': parent['version_id'], 'source_hash': version['source_sha256'],
                    'validation_status': status, 'executed': payload['executed'], 'error': error})
            self.sync(eid)
            return {'session_id': eid, 'operation_id': oid, 'status': status, **payload}

    def directory(self, eid):
        with self.store.connection() as db:
            row = db.execute('SELECT * FROM demo_assessments WHERE session_id=?', (eid,)).fetchone()
        if row is None:
            raise ValueError('请先建立新题验收记录')
        folder = (self.store.root / row['directory']).resolve()
        if not folder.is_relative_to(self.store.root / 'demo' / 'f05'):
            raise ValueError('验收记录目录越界')
        return folder

    def begin(self, eid, external_help, coverage, input_origin=None):
        with self.lock:
            e = self.session(eid)
            with self.store.connection() as db:
                exists = db.execute('SELECT 1 FROM demo_assessments WHERE session_id=?', (eid,)).fetchone()
            if exists:
                from .service import Conflict
                raise Conflict('该会话的新题记录已建立；不会重置暴露记录')
            q = catalog.question()
            folder = self.store.root / 'demo' / 'f05' / uid()
            folder.parent.mkdir(parents=True, exist_ok=True)
            # Explicit DB link and ledger event, independent of folder naming.
            with self.store.connection(write=True) as db:
                self.store.insert(db, 'demo_assessments', {'session_id': eid,
                    'directory': str(folder.relative_to(self.store.root)), 'question_id': q['question_id'],
                    'question_version': q['question_version'], 'created_at': utc()})
                self.store.event(db, eid, 'assessment_creation_started', {'question_id': q['question_id'],
                    'question_version': q['question_version'], 'content_hash': q['content_hash']})
            try:
                f05.create(folder, coverage={**coverage, 'external_help_declaration': external_help},
                           origin=provenance.data_label(provenance.record(input_origin,e)), learner_id='user_role_not_certified')
                records.append(folder, 'web_demo_link', {'session_id': eid, 'original_case_id': e['case_id'],
                    'original_case_version': e['version_snapshot'], 'original_source_hash': e['case_snapshot']['source_sha256'],
                    'module': 'web_lab.demo', 'version': 1})
                self.sync(eid)
                self.event(eid, 'assessment_presented', {'question_id': q['question_id'],
                    'question_version': q['question_version'], 'content_hash': q['content_hash'],
                    'validation_status': 'recorded_not_independently_observed'})
            except Exception as exc:
                self.event(eid, 'assessment_creation_failed', {'error': str(exc), 'validation_status': 'incomplete'})
                raise
            return self.detail(eid)['assessment']

    def sync(self, eid):
        """Import saved teacher/evidence availability once, preserving its source ID."""
        with self.lock:
            try:
                folder = self.directory(eid)
            except ValueError:
                return
            if not (folder / 'session.json').exists():
                return
            e = self.session(eid)
            imported = {r['payload'].get('provenance', {}).get('web_record_id') for r in records.events(folder)
                        if r['kind'] == 'help'}
            presented = records.read(folder / 'session.json')['created_utc']
            items = [('fixed_first_question', 'hint', e['case_snapshot']['demo_initial_output'], 'original')]
            # Subsequent free-form chat may concern the new assessment. Without a
            # human relevance judgment, it cannot silently remain original-only.
            items += [(t['selected_attempt_id'], 'ai_help' if e['mode'] == 'S1' else 'hint', t['output'],
                       'unknown' if t['completed_at'] >= presented else 'original')
                      for t in e['turns'] if t['status'] == 'succeeded']
            items += [(op['operation_id'], 'hint', op['payload']['result']['feedback'], 'original')
                      for op in self.operations(eid) if op['payload'].get('result', {}).get('feedback')]
            for ident, kind, output, target in items:
                if ident in imported:
                    continue
                record = f05.record_help(folder, kind, target, output['student_message'],
                    provenance={'session_id': eid, 'web_record_id': ident, 'full_teacher_output': output,
                                'exposure_basis': 'available_in_session_not_proof_of_reading',
                                'source': 'stored_output_no_regeneration', 'semantic_review': 'needs_human_review'})
                self.event(eid, 'help_record_linked', {'help_event_seq': record, 'web_record_id': ident,
                    'target': target, 'kind': kind, 'validation_status': 'recorded'})

    def help(self, eid, kind, target, content, before, input_origin=None):
        with self.lock:
            self.session(eid)
            row = f05.record_help(self.directory(eid), kind, target, content, applies_before_first=before,
                                 provenance={'session_id': eid, 'input_origin': provenance.record(input_origin),
                                             'origin': 'user_declaration_not_certified'})
            event = records.events(self.directory(eid))[-1]
            self.event(eid, 'help_declared', {'help_event_seq': row, 'target': target, 'kind': kind,
                'input_origin':provenance.record(input_origin),
                'validation_status': 'user_declared', 'applies_before_first': event['payload']['applies_before_first']})
            return event

    def submit(self, eid, source, first=True, input_origin=None):
        with self.lock:
            e = self.session(eid)
            self.sync(eid)
            folder = self.directory(eid)
            if first and (folder / 'first').exists():
                from .service import Conflict
                self.event(eid, 'first_overwrite_rejected', {'attempted_source': source, 'source_hash': sha(source),
                    'validation_status': 'blocked', 'executed': False})
                raise Conflict('首次提交已冻结，不能覆盖；请使用后续修改')
            version = next((k for k, v in catalog.load()['MAX']['versions'].items()
                            if v['source_hash'] == sha(source)), 'unreviewed_' + uid())
            origin = provenance.record(input_origin,e)
            self.event(eid, 'assessment_submission_started', {'is_first': first, 'source_hash': sha(source),
                'source_version': version, 'validation_status': 'pending', 'source': 'user_text',
                'question_id': catalog.question()['question_id'], 'question_version': catalog.question()['question_version'],
                'input_origin': origin})
            try:
                out = (f05.freeze_first(folder, version, source, submission_origin=(
                           'student_self_declared' if origin['kind']=='manual_browser' else
                           'unknown' if origin['kind']=='unknown' else 'frozen_simulated_submission'))
                       if first else f05.revise(folder, version, source))
            except Exception as exc:
                self.event(eid, 'assessment_submission_failed', {'is_first': first, 'error': str(exc),
                    'source_hash': sha(source), 'validation_status': 'incomplete'})
                raise
            self.event(eid, 'assessment_submission_saved', {'is_first': first, 'source_hash': sha(source),
                'source_version': version, 'validation_status': out.get('execution_state', out.get('comparison', {}).get('status')),
                'question_id': catalog.question()['question_id'], 'question_version': catalog.question()['question_version']})
            return {'session_id': eid, **out}

    def detail(self, eid):
        with self.lock:
            e=self.session(eid)
            self.sync(eid)
            assessment, error, locked = None, None, False
            try:
                folder = self.directory(eid)
            except ValueError:
                folder = None
            if folder:
                locked = (folder / 'first').exists()
                try:
                    assessment = {'session_id': eid, **f05.view(folder)}
                    links = [r for r in assessment['events'] if r['kind'] == 'web_demo_link']
                    if len(links) != 1 or links[0]['payload']['session_id'] != eid:
                        raise ValueError('F05 ledger/session identity mismatch')
                    for record in assessment['events'] + assessment['help_records']:
                        record['session_id'] = eid
                    if assessment['first']:
                        assessment['first']['source_text'] = (folder / 'first' / 'source.py').read_text(encoding='utf-8')
                except Exception as exc:
                    error = str(exc)
            return {'session_id': eid, 'operations': self.operations(eid), 'assessment': assessment,
                    'assessment_error': error, 'first_submission_locked': locked,
                    'version_readiness': self.version_readiness(e),
                    'execution_policy': 'exact_frozen_reviewed_hashes_only', 'learning_outcome_verified': False}

    @staticmethod
    def version_readiness(e):
        """Read-only registry lookup; never grants arbitrary code approval."""
        approved={v['source_hash'] for v in f04.load()['SUM']['versions'].values()}
        original=next(v for v in e['code_versions'] if v['label']=='original')
        out=[]
        for v in e['code_versions']:
            link=next((r['payload'] for r in reversed(e['events']) if r['type']=='unverified_code_recorded'
                       and r['payload'].get('version_id')==v['version_id']),{})
            parent=next((p for p in e['code_versions'] if p['version_id']==link.get('parent_version_id')),original)
            out.append({'version_id':v['version_id'],'source_registered':v['source_sha256'] in approved,
                        'can_verify':v['source_sha256'] in approved and parent['source_sha256'] in approved,
                        'parent_version_id':parent['version_id']})
        return out

    def export_files(self, eid):
        folders = [self.store.root / op['artifact_dir'] for op in self.operations(eid)]
        try:
            folders.append(self.directory(eid))
        except ValueError:
            pass
        out = []
        for folder in folders:
            for path in sorted(folder.rglob('*')):
                if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(self.store.root / 'demo'):
                    continue
                raw = path.read_bytes()
                out.append({'session_id': eid, 'relative_path': str(path.relative_to(self.store.root)),
                    'sha256': hashlib.sha256(raw).hexdigest(), 'encoding': 'base64',
                    'bytes': len(raw), 'content': base64.b64encode(raw).decode('ascii')})
        return out
