"""Explicit denominators and traceable exports; no model self-scoring."""
import base64
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

from .store import utc
from . import provenance

ARTIFACT_NAMES = {'prompt.md', 'schema.json', 'input.json', 'invocation.json', 'events.jsonl',
    'stderr.log', 'raw_response.json', 'events_audit.json', 'validation.json', 'metadata.json',
    'transport_metadata_original.json', 'f02_input.json', 'f02_validation.json', 'f02_provenance.json',
    'failure.json', 'service_error.log', 'failure_summary.json', 'recovery.json', 'web_validation.json'}
DIMENSIONS = ['on_topic', 'repetitive', 'fact_error', 'full_repair', 'used_previous']


def artifact_files(root, attempt):
    root = Path(root).resolve()
    folder = (root / attempt['artifact_dir']).resolve()
    if not folder.is_relative_to(root / 'artifacts'):
        raise ValueError('工件目录越界')
    files = {}
    for name in ARTIFACT_NAMES:
        path = folder / name
        if path.is_file() and not path.is_symlink():
            files[name] = path
        prepared = folder.parent / (folder.name + '_input') / name
        if prepared.is_file() and not prepared.is_symlink():
            files['input_' + name] = prepared
    submission = folder.parent / (folder.name + '_submission.json')
    if submission.is_file() and not submission.is_symlink():
        files['submission.json'] = submission
    return files


def export_json(store, eid=None):
    experiments = [store.get(eid)] if eid else store.list(full=True)
    for e in experiments:
        for t in e['turns']:
            for attempt in t['attempts']:
                attempt['artifacts'] = []
                attempt['artifacts_may_be_partial'] = attempt['status'] in {'queued', 'connecting', 'generating'}
                for name, path in sorted(artifact_files(store.root, attempt).items()):
                    raw = path.read_bytes()
                    attempt['artifacts'].append({'name': name, 'relative_path': str(path.relative_to(store.root)),
                        'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
                        'encoding': 'base64', 'content': base64.b64encode(raw).decode('ascii')})
    return {'schema_version': 1, 'exported_at': utc(), 'timezone_for_calendar_filters': 'Asia/Shanghai',
            'data_scope': 'web_lab_V1_only; historical_F01_F02_not_migrated',
            'evaluation_policy': 'objective_execution / user_subjective / ai_auxiliary / independent_human / unrated',
            'semantic_accuracy_certified': False, 'experiments': experiments}


def latest_subjective(turn):
    rows = [f for f in turn['feedback'] if f['evaluation_source'] == 'user_subjective']
    return rows[-1] if rows else {}


def stats(experiments):
    turns = [t for e in experiments for t in e['turns']]
    attempts = [(e, a) for e in experiments for t in e['turns'] for a in t['attempts']]
    statuses = Counter(e['status'] for e in experiments)
    feedback = {}
    for key in DIMENSIONS:
        counts = Counter(latest_subjective(t).get(key) or 'unrated' for t in turns)
        feedback[key] = {'denominator': len(turns), **{v: counts[v] for v in ['yes', 'no', 'uncertain', 'unrated']},
                         'source': 'user_subjective_latest_revision_per_turn'}
    rated = sum(any(latest_subjective(t).get(k) is not None for k in DIMENSIONS + ['satisfaction'])
                or bool(latest_subjective(t).get('notes')) for t in turns)
    real = [a for e, a in attempts if e['model_provenance'] == 'real_official_Codex_CLI' and e['mode'] == 'S1']
    simulated = [a for e, a in attempts if e['model_provenance'] == 'simulated_model']
    finished_real = [a for a in real if a['status'] not in {'queued', 'connecting', 'generating'}]
    durations = sorted(a['elapsed_seconds'] for a in finished_real if a['elapsed_seconds'] is not None)
    return {'total': len(experiments), 'completed': statuses['completed'], 'failed': statuses['failed'],
        'unfinished': statuses['active'] + statuses['paused'], 'status_counts': dict(statuses),
        'by_feature': dict(Counter(e['feature'] for e in experiments)),
        'by_case': dict(Counter(e['feature'] + '/' + e['case_id'] for e in experiments)),
        'by_source': dict(Counter(e['source_type'] for e in experiments)), 'turns': len(turns),
        'by_source_meaning': 'creation_tags_not_authenticated_real_students',
        'answer_origins': dict(Counter(provenance.answer_origin(t)['kind'] for t in turns if t['answer_raw'])),
        'origin_certification': 'per_input_declarations; legacy_unrecorded_inputs_unknown; no_authenticated_student_claim',
        'evaluated_turns': rated, 'unrated_turns': len(turns) - rated, 'feedback': feedback,
        'evaluation_sources': dict(Counter(f['evaluation_source'] for t in turns for f in t['feedback'])),
        'objective_checks': {'denominator': len(turns), 'passed': sum(bool((t['checks'] or {}).get('display_safe')) for t in turns),
                             'meaning': '仅结构、引用、受控执行检查；不认证教学语义'},
        'ai_calls': {'denominator': len(real), 'success': sum(bool((a['metadata'] or {}).get('CLI_success')) for a in finished_real),
                     'failed': sum(not (a['metadata'] or {}).get('CLI_success') for a in finished_real),
                     'pending': len(real) - len(finished_real), 'source': 'real_official_Codex_CLI'},
        'simulated_calls': {'denominator': len(simulated), 'success': sum(a['status'] == 'succeeded' for a in simulated),
                            'failed': sum(a['status'] in {'failed', 'blocked'} for a in simulated)},
        's0_attempts': sum(e['mode'] == 'S0' for e, a in attempts),
        'latency': {'denominator': len(durations), 'source': 'real_official_Codex_CLI_finished_attempts',
                    'average_seconds': sum(durations) / len(durations) if durations else None,
                    'min_seconds': durations[0] if durations else None,
                    'max_seconds': durations[-1] if durations else None},
        'semantic_accuracy_certified': False}


def safe_cell(value):
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value


def export_csv(store, kind, eid=None):
    experiments = [store.get(eid)] if eid else store.list(full=True)
    rows = []
    base = ['experiment_id', 'name', 'feature', 'case_id', 'mode', 'source_type', 'model_provenance']
    if kind == 'experiments':
        fields = base + ['created_at', 'ended_at', 'status', 'end_reason', 'current_code_version_id',
                         'turn_count', 'evaluated_turn_count', 'attempt_count', 'version_snapshot', 'model_config']
        for e in experiments:
            rows.append({**e, 'turn_count': len(e['turns']),
                'evaluated_turn_count': stats([e])['evaluated_turns'],
                'attempt_count': sum(len(t['attempts']) for t in e['turns'])})
    elif kind == 'turns':
        fields = base + ['turn_id', 'number', 'question_shown', 'answer_raw', 'input_origin', 'status', 'submitted_at',
                        'started_at', 'generation_started_at', 'completed_at', 'elapsed_seconds', 'error', 'code_version_id',
                        'ai_reply', 'next_action', 'evidence_refs', 'uncertainties', 'checks', 'attempt_count',
                        'feedback_source', *DIMENSIONS, 'satisfaction', 'notes']
        for e in experiments:
            for t in e['turns']:
                output = t['output'] or {}
                feedback = latest_subjective(t)
                rows.append({**{k: e[k] for k in base}, **t, **{k: feedback.get(k) for k in DIMENSIONS + ['satisfaction', 'notes']},
                    'feedback_source': 'user_subjective' if feedback else 'unrated', 'ai_reply': output.get('student_message'),
                    'next_action': output.get('next_action'), 'evidence_refs': output.get('evidence_refs'),
                    'input_origin': provenance.answer_origin(t),
                    'uncertainties': output.get('uncertainties'), 'attempt_count': len(t['attempts'])})
    else:
        fields = base + ['turn_id', 'attempt_id', 'number', 'status', 'requested_at', 'started_at', 'generation_started_at', 'completed_at',
                         'retry_reason', 'elapsed_seconds', 'error', 'artifact_dir', 'metadata', 'raw_output']
        for e in experiments:
            for t in e['turns']:
                for a in t['attempts']:
                    rows.append({**{k: e[k] for k in base}, **a})
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows({k: safe_cell(v) for k, v in row.items()} for row in rows)
    return stream.getvalue().encode('utf-8-sig')
