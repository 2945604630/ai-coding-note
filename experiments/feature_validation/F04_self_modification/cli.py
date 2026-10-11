"""One-command registered trial or save-only student submission."""
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import argparse
import json
from experiments.feature_validation.F04_self_modification.catalog import ROOT
from experiments.feature_validation.F04_self_modification.core import compare


def main():
    parser = argparse.ArgumentParser(description='F04: compare reviewed versions; save unknown code without execution')
    parser.add_argument('--scenario', choices=['M01', 'M02', 'M03'], default='M01')
    parser.add_argument('--new-code', type=Path, help='Read the complete student code file as UTF-8; unknown code stays pending')
    parser.add_argument('--student-version', default='student_unreviewed')
    parser.add_argument('--paste', action='store_true', help='Paste code, then enter END_CODE on a separate line; saved without execution')
    ns = parser.parse_args()
    if ns.paste and ns.new_code:
        parser.error('Choose --paste or --new-code')
    scenarios = json.loads((ROOT / 'data/scenarios.json').read_text(encoding='utf-8'))
    selected = next(s for s in scenarios if s['scenario_id'] == ns.scenario)
    source = None
    if ns.new_code:
        source = ns.new_code.read_bytes().decode('utf-8')
    elif ns.paste:
        print('Paste complete code. Type END_CODE on its own line to save. No unreviewed execution.')
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == 'END_CODE':
                break
            lines.append(line)
        source = '\n'.join(lines) + '\n'
    r = compare(selected['case_id'], selected['before_version'],
         ns.student_version if source is not None else selected['after_version'],
         submitted_source=source, inputs=selected['inputs'], context={},
         origin='user_code_submission' if source is not None else 'manual_registered_fixture_trial_not_learner_data')
    print(json.dumps({k: r[k] for k in ['status', 'error_reason', 'before', 'after', 'modification',
          'summary', 'feedback', 'needs_human_review', 'elapsed_ms', 'evidence_files']}, ensure_ascii=False, indent=2))
    return 0 if r['status'] not in ['blocked', 'execution_incomplete', 'feedback_protocol_failed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
