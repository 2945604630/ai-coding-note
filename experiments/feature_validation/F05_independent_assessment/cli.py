"""Inspect saved formal cases or freeze a new code file with explicit declarations."""
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import argparse
from datetime import datetime, timezone
import json
import uuid
from experiments.feature_validation.F05_independent_assessment.catalog import ROOT
from experiments.feature_validation.F05_independent_assessment import core


def main():
    parser = argparse.ArgumentParser(description='F05 record qualification is separate from code correctness')
    parser.add_argument('--show', choices=['T01', 'T02', 'T03'], help='Read saved simulated formal records, no execution')
    parser.add_argument('--code', type=Path, help='Student UTF-8 code file; unregistered code is saved without execution')
    parser.add_argument('--version', default='student_unreviewed')
    parser.add_argument('--external-help', choices=['none', 'used', 'unknown'], default='unknown')
    parser.add_argument('--history-complete', action='store_true')
    parser.add_argument('--prior-exposure-checked', action='store_true')
    parser.add_argument('--source-record-complete', action='store_true')
    ns = parser.parse_args()
    if bool(ns.show) == bool(ns.code):
        parser.error('Choose --show or --code')
    if ns.show:
        d = ROOT / 'results/formal_v1' / ns.show
    else:
        d = ROOT / 'user_trials' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ_') + uuid.uuid4().hex[:8])
        core.create(d, coverage={'history_complete': ns.history_complete,
             'prior_exposure_checked': ns.prior_exposure_checked, 'source_record_complete': ns.source_record_complete,
             'external_help_declaration': ns.external_help}, origin='user_code_file_declarations_not_independently_certified')
        core.freeze_first(d, ns.version, ns.code.read_bytes().decode('utf-8'), submission_origin='student_self_declared')
    v = core.view(d)
    first = v['first']
    print(json.dumps({'directory': str(d.resolve()), 'data_origin': v['session']['data_origin'],
        'question': v['session']['question'], 'current_eligibility': v['current_eligibility'],
        'first_eligibility_at_freeze': first['eligibility_at_freeze'], 'first_source_hash': first['source_hash'],
        'execution_state': first['execution_state'], 'first_score': first['score'],
        'revision_scores': [r['comparison'].get('summary', {}) for r in v['revisions']],
        'help_record_count': len(v['help_records']), 'independent_first_pass_by_records': v['independent_first_pass_by_records'],
        'absence_of_external_help_proven': False, 'student_mastery_confirmed': None}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
