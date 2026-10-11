"""Repair of existing guarded CLI; reuse F02 protocol, executor and transport."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import uuid

from experiments.common import digest, dump
from .. import core, baseline, cli_guard, native
from ..run import teacher_entry

TRIAL_ROOT = core.ROOT.parent / 'F02_user_trials'
MAX_TEACHER_TURNS = 3


def utc():
    return datetime.now(timezone.utc).isoformat()


def save(folder, record):
    # Atomic replacement in this new session only. Old sessions cannot be reused.
    target = folder / 'interaction.json'
    temp = folder / 'interaction.pending.json'
    dump(temp, record)
    temp.replace(target)


def versions(case):
    serialized = json.dumps(case['evidence'], ensure_ascii=False, sort_keys=True).encode('utf-8')
    return {'case_id': case['case_id'], 'case_sha256': digest(core.ROOT / 'cases' / (case['case_id'] + '.json')),
            'sources': {'original': case['source_sha256'],
                        **{k: v['source_sha256'] for k, v in case['versions'].items()}},
            'evidence_sha256': hashlib.sha256(serialized).hexdigest(),
            'evidence_source_versions': {e['evidence_id']: e['source_version'] for e in case['evidence']},
            'adopted_unprovided_student_code': False,
            'version_boundary': 'only_frozen_reviewed_versions; self_report_is_not_executed_code'}


def generate(value, artifact, transport_fn=None):
    """Same official first-response transport, all trial inputs in trial directory."""
    artifact = Path(artifact)
    if artifact.exists():
        raise FileExistsError('First attempt already exists; no resampling')
    prepared = artifact.parent / (artifact.name + '_input')
    prepared.mkdir(parents=True, exist_ok=False)
    dump(prepared / 'f02_input.json', deepcopy(value))
    (prepared / 'prompt.md').write_text(core.prompt(value), encoding='utf-8')
    (prepared / 'schema.json').write_bytes((core.ROOT / 'schema.json').read_bytes())
    caller = transport_fn or native.transport.generate
    try:
        meta, out, _ = caller(prepared / 'prompt.md', prepared / 'schema.json', artifact, 'F02_user_trial', None)
    except BaseException as exc:
        # The reused transport retains stderr/events. Also preserve last-message
        # bytes on interruption without reconstructing or inventing an answer.
        failure = {'type': type(exc).__name__, 'message': str(exc), 'utc': utc(),
                   'data_origin': value['data_origin'], 'no_fabricated_answer': True,
                   'raw_available': False, 'last_message_bytes_captured_on_exception': False}
        if artifact.exists():
            raw = artifact / 'raw_response.json'
            captured = False
            invocation = artifact / 'invocation.json'
            if not raw.exists() and invocation.exists():
                argv = core.read(invocation)['argv']
                for flag in ['-o', '--output-last-message']:
                    if flag in argv:
                        last = Path(argv[argv.index(flag) + 1])
                        if last.exists():
                            raw.write_bytes(last.read_bytes()); captured = True
                        break
            failure.update(raw_available=raw.exists(), last_message_bytes_captured_on_exception=captured)
            dump(artifact / 'failure.json', failure)
        dump(prepared / 'failure.json', failure)
        raise
    original_meta = artifact / 'metadata.json'
    if original_meta.exists():
        (artifact / 'transport_metadata_original.json').write_bytes(original_meta.read_bytes())
    meta = deepcopy(meta)
    meta['transport_default_origin'] = meta.get('data_origin')
    meta['data_origin'] = value['data_origin']
    meta['purpose'] = 'F02_actual_interaction'
    dump(original_meta, meta)
    checked = cli_guard.validate(out, value)
    dump(artifact / 'f02_input.json', value)
    dump(artifact / 'f02_validation.json', checked)
    dump(artifact / 'f02_provenance.json', {'data_origin': value['data_origin'],
         'public_input_sha256': digest(prepared / 'f02_input.json'), 'prompt_sha256': digest(prepared / 'prompt.md'),
         'same_path_history_explicitly_supplied': True, 'OS_file_denial': False,
         'exact_server_context_attested': False, 'no_gold_or_scores_supplied': True})
    return {'output': out, 'metadata': meta, 'checks': checked, 'artifact': str(artifact)}


def semantic_fields(turn):
    return {'uses_previous_new_information': 'N/A' if turn == 1 else 'needs_human_review',
            'repeats_answered_question': 'N/A' if turn == 1 else 'needs_human_review',
            'unsupported_judgment': 'needs_human_review', 'full_repair_leak': 'needs_human_review',
            'interpretation_accuracy': 'needs_human_review',
            'prose_source_version_alignment': 'needs_human_review', 'independent_human_review': False}


def run_session(case, folder, arm='S1', *, generate=generate, read_input=input, emit=print,
                origin='interactive_user_unverified_role'):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    record = {'record_version': 3, 'start_utc': utc(), 'data_origin': origin,
              'not_formal_simulation_sample': True, 'case_id': case['case_id'], 'arm': arm,
              'max_teacher_turns': MAX_TEACHER_TURNS, 'max_student_reply_cycles': 2,
              'history': [], 'turns': [], 'commands': [], 'feedback': {},
              'termination': None, 'exception': None, 'elapsed_seconds': None,
              'knowledge_mastery_certified': False, 'teaching_accuracy_certified': False,
              'evidence_version': versions(case),
              'runtime_sha256': {'trial_cli.py': digest(Path(__file__)),
                                'cli_guard.py': digest(core.ROOT / 'cli_guard.py')}}
    dump(folder / 'case.json', case)
    save(folder, record)
    active = None
    try:
        emit(case['statement']); emit(case['input_contract']); emit('original：\n' + case['source'])
        for version, data in case['versions'].items():
            emit(version + '（审核过的对照版本）：\n' + data['source'])
        for e in case['evidence']:
            emit(f"{e['evidence_id']} [{e['source_version']}] n={e['args'][0]} 实际={e['actual']} 预期={e['expected']}")
        emit('最多三次导师输出；理解足够时提前转入自行修改。/quit退出；/feedback 你的意见记录本轮反馈。')
        for turn in range(1, MAX_TEACHER_TURNS + 1):
            timer = time.perf_counter()
            value = cli_guard.public_snapshot(case, record['history'], origin)
            artifact = folder / 'calls' / f'T{turn:02d}'
            active = {'turn': turn, 'status': 'calling', 'start_utc': utc(),
                      'public_input': value, 'student_answer_raw': value['student_answer'],
                      'previous_teacher_question': value['previous_question'], 'artifact': str(artifact),
                      'evidence_version': versions(case), 'semantic_review': semantic_fields(turn),
                      'user_feedback': [], 'output': None, 'adopted_next_action': None}
            record['turns'].append(active)
            save(folder, record)
            if arm == 'S1':
                emit(f'第{turn}次真实模型调用中；历史调用通常约两分钟。Ctrl+C可结束并保留记录。')
                item = generate(value, artifact)
            else:
                out = baseline.decide(value)
                item = {'output': out, 'metadata': None, 'checks': cli_guard.validate(out, value)}
            active.update(deepcopy(item))
            active['elapsed_seconds'] = round(time.perf_counter() - timer, 4)
            active['end_utc'] = utc()
            metadata = item.get('metadata') or {}
            active['connection_anomalies'] = {'timeout': metadata.get('timeout'),
                                             'warnings': metadata.get('warnings'),
                                             'exit_code': metadata.get('exit_code'),
                                             'details': 'artifact stderr.log/events.jsonl when present'}
            if not item['checks']['display_safe'] or arm == 'S1' and not metadata.get('CLI_success'):
                active['status'] = 'blocked'
                record['termination'] = 'model_call_failed' if arm == 'S1' and not metadata.get('CLI_success') else 'guard_blocked'
                save(folder, record)
                emit('本轮输出未通过检查，停止展示。首次原文和失败记录已保留；没有重试。')
                break
            out = item['output']
            active['status'] = 'displayed'
            active['ai_question_or_message'] = out['student_message']
            active['adopted_next_action'] = out['next_action']
            active['student_action_performed'] = 'not_observed'
            record['history'].append(deepcopy(teacher_entry(out, item['checks'])))
            save(folder, record)
            emit('\n动作：' + core.ACTION_ZH[out['next_action']]); emit(out['student_message'])
            emit('依据（模型解释，未认证）：' + out['decision_basis'])
            emit('尚不确定：' + '；'.join(out['uncertainties']))
            for checked in item['checks']['requests']:
                req = checked['request']
                emit(f"独立执行 [{req['source_version']}] {req['args']}：实际={checked['execution']['value']}，预期={checked['expected']}")
            end = core.termination(out, turn)
            if end != 'continue':
                record['termination'] = end
                active['session_transition'] = end
                if end == 'understanding_sufficient':
                    emit('本次追问结束，请自行修改代码。这不是长期掌握判定，修改结果尚未核验。')
                elif end == 'await_new_evidence':
                    emit('等待当前完整代码及最新输入/错误；旧版事实不能认证修改后的代码。本入口不执行未经审核的新源码。')
                elif end == 'budget_limited':
                    emit('已达到本次三次导师输出上限。最后问题可能仍未回答；不代表已理解或已修好。')
                save(folder, record)
                break
            while True:
                input_timer = time.perf_counter()
                answer = read_input('你的回答（/quit退出；/feedback 意见）：')
                duration = round(time.perf_counter() - input_timer, 4)
                if answer.strip().startswith('/feedback '):
                    active['user_feedback'].append({'raw': answer, 'utc': utc(), 'elapsed_seconds': duration})
                    save(folder, record)
                    continue
                if answer.strip() == '/quit':
                    record['commands'].append({'raw': answer, 'utc': utc()})
                    record['termination'] = 'user_quit'
                else:
                    record['history'].append({'role': 'student', 'text': answer, 'data_origin': origin,
                                              'utc': utc(), 'input_elapsed_seconds': duration,
                                              'source_version_claim_verified': False})
                    active['student_reply_raw'] = answer
                    active['student_reply_elapsed_seconds'] = duration
                save(folder, record)
                break
            if record['termination']:
                break
        if record['termination'] is None:
            record['termination'] = 'budget_limited'
    except (EOFError, KeyboardInterrupt) as exc:
        record['exception'] = type(exc).__name__
        record['termination'] = 'input_closed' if isinstance(exc, EOFError) else 'user_interrupt'
        if active and active['status'] == 'calling':
            active['status'] = 'interrupted'
            active['end_utc'] = utc()
    except Exception as exc:
        record['exception'] = type(exc).__name__ + ': ' + str(exc)
        record['termination'] = 'connection_or_runtime_failure'
        if active and active['status'] == 'calling':
            active['status'] = 'failed'
            active['end_utc'] = utc()
            active['connection_anomalies'] = {'exception': record['exception'], 'raw_artifacts_retained': True}
        emit('调用或记录处理失败，已保留当前会话；没有生成替代回答。')
    finally:
        if active and 'elapsed_seconds' not in active:
            active['elapsed_seconds'] = round(time.perf_counter() - timer, 4)
        record['end_utc'] = utc()
        record['elapsed_seconds'] = round(time.perf_counter() - start, 4)
        save(folder, record)
        emit('记录：' + str(folder))
    return record


def main():
    p = argparse.ArgumentParser(description='真实 F02 多轮体验；旧实验不可覆盖')
    p.add_argument('--case', choices=['C01', 'C02', 'C03'])
    p.add_argument('--arm', choices=['S0', 'S1'], default='S1')
    p.add_argument('--scripted-smoke', action='store_true', help='工程冒烟标记，记录与真实用户隔离')
    args = p.parse_args()
    core.verify()
    cid = args.case
    while cid not in ['C01', 'C02', 'C03']:
        try:
            cid = input('选择案例 C01/C02/C03 [C01]：').strip() or 'C01'
        except (EOFError, KeyboardInterrupt):
            return
        if cid not in ['C01', 'C02', 'C03']:
            print('请输入 C01、C02 或 C03。')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '_' + uuid.uuid4().hex[:8]
    root = core.ROOT / 'validation_repair/engineering_runs' if args.scripted_smoke else TRIAL_ROOT
    origin = 'scripted_engineering_smoke' if args.scripted_smoke else 'interactive_user_unverified_role'
    folder = root / stamp
    record = run_session(core.read(core.ROOT / 'cases' / (cid + '.json')), folder, args.arm, origin=origin)
    try:
        for key, label in [('on_topic', '回复是否切题'), ('understood_intent', '是否理解系统意图'),
            ('want_to_continue', '是否希望继续使用')]:
            timer = time.perf_counter()
            raw = input(label + '（是/否/留空）：')
            record['feedback'][key] = {'raw': raw, 'value': {'是': True, '否': False}.get(raw.strip()),
                                      'elapsed_seconds': round(time.perf_counter() - timer, 4), 'utc': utc()}
            save(folder, record)
    except (EOFError, KeyboardInterrupt):
        record['feedback_collection_interrupted'] = True
        save(folder, record)


if __name__ == '__main__':
    main()
