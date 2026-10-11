"""Separate record eligibility from first code results and subsequent changes."""
from datetime import datetime, timezone
from pathlib import Path
import traceback

from experiments.common import digest, valid_args
from experiments.runner import source_hash
from ..F02_dynamic_questioning import core as f02
from ..F03_evidence_verification import verifier as f03
from ..F04_self_modification import core as f04
from .catalog import load, question
from . import records as log


def create(directory, *, coverage=None, origin='user_trial_unverified', learner_id='unverified'):
    directory = Path(directory).resolve()
    q = question()
    directory.mkdir(parents=True, exist_ok=False)
    (directory / 'events').mkdir()
    (directory / 'revisions').mkdir()
    log.write(directory / 'session.json', {'assessment_id': directory.name, 'learner_id': learner_id,
        'created_utc': datetime.now(timezone.utc).isoformat(), 'data_origin': origin, 'question': q,
        'coverage': coverage or {}, 'qualification_policy': 'F05_v1', 'help_record_scope': 'this ledger and imported declarations'})
    log.append(directory, 'assessment_presentation', {'question_id': q['question_id'],
         'question_version': q['question_version'], 'content_hash': q['content_hash'],
         'first_authorized_presentation': True})
    return directory


def record_help(directory, kind, target, content, *, applies_before_first=None, provenance=None):
    directory = Path(directory)
    if kind not in ['hint', 'full_answer', 'ai_help', 'external_help', 'question_seen']:
        raise ValueError('Unknown help type')
    if target not in ['original', 'assessment', 'unknown']:
        raise ValueError('Help target must be explicit or unknown')
    if applies_before_first is not None and type(applies_before_first) is not bool:
        raise ValueError('Before-first marker must be bool or unspecified')
    q = log.read(directory / 'session.json')['question']
    before = not (directory / 'first').exists() if applies_before_first is None else applies_before_first
    return log.append(directory, 'help', {'help_kind': kind, 'target': target, 'content': content,
          'applies_before_first': before, 'question_content_hash': q['content_hash'],
          'provenance': provenance or {'origin': 'caller_declared_not_independently_certified'}})


def record_teacher_action(directory, output, target, *, exposure_type='ai_help', origin='unverified_teacher_record'):
    """Keep F01/F02 output verbatim; never execute its suggested code/requests."""
    if output.get('next_action') not in f02.ACTIONS or type(output.get('stop_questioning')) is not bool:
        raise ValueError('Not a supported F01/F02 action record')
    return record_help(directory, exposure_type, target, output.get('student_message', ''),
        provenance={'origin': origin, 'full_teacher_output': output, 'F02_termination': f02.termination(output, 1),
                    'exposure_label_origin': 'caller_annotation_not_automatic_NL_certification'})


def _meta(directory):
    meta = log.read(directory / 'session.json')
    if meta['question'] != question():
        raise ValueError('Question identity/version/source changed')
    return meta


def _run_first(directory, version, source, inputs):
    entry = load()['MAX']
    reviewed = entry['versions'].get(version)
    if reviewed is None or source_hash(source) != reviewed['source_hash']:
        return [], 'pending_review', 'unknown_or_mismatched_reviewed_source'
    selected = entry['approved_inputs'] if inputs is None else inputs
    if not isinstance(selected, list) or not selected or any(
        not valid_args(entry['task'], a, entry['domain'])[0] or
        not any(f03.same_value(a, b) for b in entry['approved_inputs']) for a in selected):
        return [], 'blocked_inputs', 'illegal_or_unapproved_input'
    if len({str(a) for a in selected}) != len(selected):
        return [], 'blocked_inputs', 'duplicate_input'
    results = [f03.verify('MAX', args, source_version=version, expected_source_hash=source_hash(source),
               record_dir=directory / f'execution/T{index}', catalog='F05') for index, args in enumerate(selected, 1)]
    return results, 'completed' if all(r['execution_success'] for r in results) else 'execution_incomplete', None


def freeze_first(directory, version, source, *, submission_origin='unknown', inputs=None):
    directory = Path(directory).resolve()
    if not isinstance(source, str):
        raise ValueError('Complete source text required; do not fill it from a reference')
    meta = _meta(directory)
    previous = log.events(directory)
    qualification = log.eligibility(meta, previous, submission_origin)
    first = directory / 'first'
    first.mkdir(exist_ok=False)  # An unfinished or failed first attempt is also never overwritten.
    (first / 'source.py').write_bytes(source.encode('utf-8'))
    manifest = {'source_version': version, 'source_hash': source_hash(source),
                'question_id': meta['question']['question_id'], 'question_version': meta['question']['question_version'],
                'question_content_hash': meta['question']['content_hash'], 'session_sha256': digest(directory / 'session.json'),
                'submission_origin': submission_origin, 'eligibility_at_freeze': qualification,
                'preceding_event_count': len(previous)}
    log.write(first / 'frozen_submission.json', manifest)
    log.append(directory, 'first_submission_frozen', {'manifest_sha256': digest(first / 'frozen_submission.json'),
               'source_hash': manifest['source_hash'], 'source_version': version})
    try:
        tests, state, error = _run_first(first, version, source, inputs)
    except Exception:
        tests, state, error = [], 'execution_incomplete', 'parent_exception'
        log.write(first / 'parent_failure.json', {'traceback': traceback.format_exc()})
    result = {**manifest, 'source_file': str(first / 'source.py'), 'is_first_submission': True,
              'execution_state': state, 'error_reason': error, 'tests': tests,
              'score': {'passed': sum(t['matches_reference'] is True for t in tests), 'tested': len(tests),
                        'execution_unavailable': sum(not t['execution_success'] for t in tests)},
              'absence_of_external_help_proven': False, 'student_mastery_confirmed': None,
              'program_overall_correct_confirmed': None, 'new_model_calls': 0}
    if error:
        log.write(first / 'failure.json', {'error_reason': error, 'source_preserved': True})
    log.write(first / 'result.json', result)
    log.seal(first)
    log.append(directory, 'first_submission_completed', {'seal_sha256': digest(first / 'seal.json')})
    return result


def _snapshot(directory, rows):
    first = directory / 'first'
    log.check_seal(first)
    manifest = log.read(first / 'frozen_submission.json')
    if manifest['session_sha256'] != digest(directory / 'session.json'):
        raise ValueError('Session context changed after first submission')
    completed = [r for r in rows if r['kind'] == 'first_submission_completed']
    frozen = [r for r in rows if r['kind'] == 'first_submission_frozen']
    if (len(completed) != 1 or len(frozen) != 1 or
        completed[0]['payload']['seal_sha256'] != digest(first / 'seal.json') or
        frozen[0]['payload']['manifest_sha256'] != digest(first / 'frozen_submission.json')):
        raise ValueError('First submission/event seal mismatch')
    return log.read(first / 'result.json')


def view(directory):
    directory = Path(directory).resolve()
    meta = _meta(directory)
    rows = log.events(directory)
    first = _snapshot(directory, rows) if (directory / 'first').exists() else None
    revisions = []
    previous_hash = first['source_hash'] if first else None
    for child in sorted((directory / 'revisions').iterdir()):
        log.check_seal(child)
        record = log.read(child / 'result.json')
        linked = [r for r in rows if r['kind'] == 'revision_saved' and r['payload']['revision_id'] == child.name]
        if (len(linked) != 1 or linked[0]['payload']['seal_sha256'] != digest(child / 'seal.json')
                or record['parent_source_hash'] != previous_hash):
            raise ValueError('Revision lineage/event seal mismatch')
        previous_hash = record['source_hash']
        revisions.append(record)
    current = log.eligibility(meta, rows, first['submission_origin'] if first else 'unknown')
    if first:
        frozen = first['eligibility_at_freeze']
        rank = {'eligible_by_records': 0, 'unknown': 1, 'assisted_or_exposed': 2}
        if rank[current['status']] < rank[frozen['status']]:
            current = frozen  # Late events may restrict, never promote the frozen first attempt.
    return {'session': meta, 'question_was_presented_now': True,
            'help_records': [r for r in rows if r['kind'] == 'help'], 'events': rows,
            'first': first, 'revisions': revisions, 'current_eligibility': current,
            'independent_first_pass_by_records': bool(first and current['status'] == 'eligible_by_records'
                and first['score']['tested'] > 0 and first['score']['passed'] == first['score']['tested']),
            'absence_of_external_help_proven': False, 'student_mastery_confirmed': None}


def revise(directory, version, source):
    directory = Path(directory).resolve()
    before = view(directory)
    if before['first'] is None:
        raise ValueError('Freeze first submission before recording changes')
    previous = before['revisions'][-1] if before['revisions'] else before['first']
    child = directory / 'revisions' / f'{len(before["revisions"]) + 1:06d}'
    child.mkdir(exist_ok=False)
    (child / 'source.py').write_bytes(source.encode('utf-8'))
    compared = f04.compare('MAX', previous['source_version'], version, submitted_source=source,
        before_hash=previous['source_hash'], record_dir=child / 'comparison', catalog='F05',
        origin='assessment_revision_not_first_attempt')
    result = {'revision_id': child.name, 'source_version': version, 'source_hash': source_hash(source),
        'source_file': str(child / 'source.py'), 'parent_source_hash': previous['source_hash'],
        'is_first_submission': False, 'eligible_as_independent_first': False,
        'comparison': compared, 'first_submission_source_hash': before['first']['source_hash']}
    log.write(child / 'result.json', result)
    log.seal(child)
    log.append(directory, 'revision_saved', {'revision_id': child.name, 'seal_sha256': digest(child / 'seal.json')})
    return result
