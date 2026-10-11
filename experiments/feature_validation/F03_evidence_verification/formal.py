"""One frozen nine-check run, with append-only raw evidence and origin-separated counts."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform

from experiments.common import digest, dump
from .verifier import ROOT, load_registry, verify


def main():
    load_registry()
    directory = ROOT / 'results/formal_v1'
    directory.mkdir(exist_ok=False)  # Even incomplete/failed formal runs may not be silently rerun.
    checks = json.loads((ROOT / 'data/checks.json').read_text(encoding='utf-8'))
    dump(directory / 'environment.json', {'started_utc': datetime.now(timezone.utc).isoformat(),
         'platform': platform.platform(), 'python': platform.python_version(), 'model_calls': 0,
         'freeze_sha256': digest(ROOT / 'freeze.json'), 'prior_dependencies_sha256': digest(ROOT / 'prior_dependencies.json'),
         'implementation_sha256': {p.name: digest(p) for p in ROOT.glob('*.py')},
         'command': 'python -X utf8 -m experiments.feature_validation.F03_evidence_verification.formal'})
    records = []
    for check in checks:
        result = verify(check['case_id'], check['args'], source_version=check['source_version'],
                        claim=check['claim'], record_dir=directory / check['check_id'])
        row = {'check_id': check['check_id'], 'case_id': check['case_id'],
               'claim_origin': check['claim']['origin'], 'expected_status': check['expected_verification'],
               'actual_status': result['verification']['status'],
               'decision_matches_frozen_expectation': result['verification']['status'] == check['expected_verification'],
               'record': result}
        records.append(row)
        dump(directory / 'raw_results.json', records)  # Preserve partial formal progress on a later failure.
        print(check['check_id'], result['verification']['status'],
              'actual=', result['actual_output'], 'reference=', result['reference_output'],
              'error=', result['error_reason'])
    executions = [r for r in records if r['record']['execution'] is not None]
    decided = [r for r in records if r['actual_status'] in ['supported', 'refuted']]
    summary = {'checks': len(records), 'actual_execution_count': len(executions),
               'verifiable_claims': len(decided),
               'correct_support': sum(r['actual_status'] == 'supported' and r['decision_matches_frozen_expectation'] for r in records),
               'correct_refutation': sum(r['actual_status'] == 'refuted' and r['decision_matches_frozen_expectation'] for r in records),
               'wrong_support_or_refutation': sum(not r['decision_matches_frozen_expectation'] for r in decided),
               'inconclusive': sum(r['actual_status'] == 'inconclusive' for r in records),
               'version_mismatch_block': sum(r['record']['error_reason'] == 'claim_version_mismatch' for r in records),
               'illegal_input_block': sum(r['record']['error_reason'] == 'illegal_input' for r in records),
               'execution_exception': sum(not r['record']['execution_success'] for r in executions),
               'all_frozen_expectations_match': all(r['decision_matches_frozen_expectation'] for r in records),
               'origin_counts': {}, 'model_calls': 0}
    for origin in sorted({r['claim_origin'] for r in records}):
        own = [r for r in records if r['claim_origin'] == origin]
        summary['origin_counts'][origin] = {status: sum(r['actual_status'] == status for r in own)
                                          for status in ['supported', 'refuted', 'inconclusive']}
    dump(directory / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary['all_frozen_expectations_match'] or summary['execution_exception']:
        raise SystemExit('Formal verification has failures; preserve this run and do not mark PASS')


if __name__ == '__main__':
    main()
