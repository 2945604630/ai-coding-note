"""Exclusive append, hash-linked events, and sealed snapshots. Not OS immutable storage."""
from datetime import datetime, timezone
import json
from pathlib import Path

from experiments.common import digest


def write(path, value):
    with Path(path).open('x', encoding='utf-8') as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write('\n')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def events(directory):
    directory = Path(directory)
    previous = digest(directory / 'session.json')
    rows = []
    for index, path in enumerate(sorted((directory / 'events').glob('*.json')), 1):
        row = read(path)
        if path.name != f'{index:06d}.json' or row['seq'] != index or row['previous_sha256'] != previous:
            raise ValueError('Event sequence/hash changed: ' + str(path))
        rows.append(row)
        previous = digest(path)
    return rows


def append(directory, kind, payload):
    directory = Path(directory)
    rows = events(directory)
    sequence = len(rows) + 1
    previous = digest(directory / 'events' / f'{len(rows):06d}.json') if rows else digest(directory / 'session.json')
    path = directory / 'events' / f'{sequence:06d}.json'
    write(path, {'seq': sequence, 'utc': datetime.now(timezone.utc).isoformat(), 'kind': kind,
                 'payload': payload, 'previous_sha256': previous})
    return sequence


def seal(directory):
    directory = Path(directory)
    files = {p.relative_to(directory).as_posix(): digest(p) for p in directory.rglob('*') if p.is_file()}
    write(directory / 'seal.json', {'sha256': files})


def check_seal(directory):
    directory = Path(directory)
    expected = read(directory / 'seal.json')['sha256']
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file() and p != directory / 'seal.json'}
    if actual != set(expected):
        raise ValueError('Sealed snapshot file set changed: ' + str(directory))
    for relative, sha in expected.items():
        if digest(directory / relative) != sha:
            raise ValueError('Sealed snapshot changed: ' + str(directory / relative))


def eligibility(meta, rows, submission_origin):
    before = [r for r in rows if r['kind'] == 'help' and r['payload']['applies_before_first']]
    affected = [r for r in before if r['payload']['target'] == 'assessment']
    uncertain = [r for r in before if r['payload']['target'] == 'unknown']
    coverage = meta.get('coverage', {})
    reasons = []
    if affected:
        reasons += ['recorded_' + r['payload']['help_kind'] for r in affected]
    if coverage.get('external_help_declaration') == 'used':
        reasons.append('external_help_declared_used')
    if reasons:
        status = 'assisted_or_exposed'
    else:
        reasons = [key + '_not_confirmed_in_records' for key in
                   ['history_complete', 'prior_exposure_checked', 'source_record_complete'] if coverage.get(key) is not True]
        if coverage.get('external_help_declaration') != 'none':
            reasons.append('external_help_declaration_missing_or_unknown')
        if submission_origin not in ['frozen_simulated_submission', 'student_self_declared']:
            reasons.append('submission_origin_unknown')
        if uncertain:
            reasons.append('help_relevance_unknown')
        status = 'unknown' if reasons else 'eligible_by_records'
    return {'status': status, 'reasons': reasons, 'evaluation_scope': 'first submission, current recorded evidence only',
            'through_event_seq': len(rows), 'prior_display_recorded': any(r['payload']['help_kind'] == 'question_seen' for r in affected),
            'original_only_help_records': sum(r['payload']['target'] == 'original' for r in before),
            'absence_of_external_help_proven': False}
