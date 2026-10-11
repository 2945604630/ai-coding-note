"""Exactly one formal three-case run. Frozen expectations are not supplied to feedback."""
from datetime import datetime, timezone
import json
import platform

from experiments.common import digest, dump
from .catalog import ROOT, load
from .core import compare


def main():
    load()
    directory = ROOT / 'results/formal_v1'
    directory.mkdir(exist_ok=False)
    scenarios = json.loads((ROOT / 'data/scenarios.json').read_text(encoding='utf-8'))
    dump(directory / 'environment.json', {'started_utc': datetime.now(timezone.utc).isoformat(),
         'python': platform.python_version(), 'platform': platform.platform(), 'model_calls': 0,
         'freeze_sha256': digest(ROOT / 'freeze.json'),
         'implementation_sha256': {p.name: digest(p) for p in ROOT.glob('*.py')},
         'F03_verifier_sha256': digest(ROOT.parent / 'F03_evidence_verification/verifier.py'),
         'command': 'python -X utf8 -m experiments.feature_validation.F04_self_modification.formal'})
    rows = []
    for item in scenarios:
        result = compare(item['case_id'], item['before_version'], item['after_version'],
                         inputs=item['inputs'], context=item['context'],
                         record_dir=directory / item['scenario_id'], origin='frozen_simulated_modification_not_real_student')
        matches = (result['status'] == item['expected_status'] and
                   [t['classification'] for t in result['tests']] == item['expected_classifications'] and
                   result['feedback_validation']['display_safe'])
        rows.append({'scenario_id': item['scenario_id'], 'matches_frozen_expectation': matches, 'record': result})
        dump(directory / 'raw_results.json', rows)
        print(item['scenario_id'], result['status'], result['summary'], 'expected_match=', matches)
    summary = {'formal_cases': len(rows), 'paired_checks': sum(len(r['record']['tests']) for r in rows),
               'all_expected_match': all(r['matches_frozen_expectation'] for r in rows),
               'model_calls': 0, 'needs_human_review': True}
    for key in ['improved', 'regression', 'remaining_failure', 'maintained_pass', 'unable_to_compare']:
        summary[key] = sum(r['record']['summary'].get(key, 0) for r in rows)
    dump(directory / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary['all_expected_match']:
        raise SystemExit('Formal failures retained; do not mark PASS or overwrite this run')


if __name__ == '__main__':
    main()
