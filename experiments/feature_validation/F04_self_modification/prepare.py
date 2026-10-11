"""Register historical reviewed code and freeze the three-case protocol before execution."""
from datetime import datetime, timezone
import json
from pathlib import Path

from experiments.common import digest, dump, load_frozen
from experiments.runner import audit_source, source_hash
from ..F03_evidence_verification import verifier as f03

ROOT = Path(__file__).resolve().parent


def main():
    if (ROOT / 'freeze.json').exists():
        raise FileExistsError('F04 frozen data already exists')
    data = ROOT / 'data'
    data.mkdir(exist_ok=False)
    (ROOT / 'results').mkdir(exist_ok=False)
    old = f03.load_registry()
    reviewed = next(x for x in load_frozen('b_cases_v3.json') if x['id'] == 'b07')
    code = reviewed['source']
    assert reviewed['task'] == old['A']['task'] and audit_source(code) is None
    original = old['A']['versions']['original']
    registry = {'SUM': {k: v for k, v in old['A'].items() if k != 'versions'}}
    registry['SUM'].update(case_id='SUM', versions={
        'original': original, 'corrected': {'source': code, 'source_hash': source_hash(code)},
        'compensated_original': old['B']['versions']['original'],
        'compensated_patch': old['B']['versions']['local_patch']},
        approved_inputs=[[0], [1], [3]],
        version_origins={'original': old['A']['review_origin'],
                        'corrected': str((f03.ROOT.parents[1] / 'data/b_cases_v3.json').resolve()) + '#b07',
                        'compensated_original': old['B']['review_origin'],
                        'compensated_patch': old['B']['review_origin']})
    # Existing F03 exception fixture is used only by a regression guard test.
    registry['G_EXCEPTION'] = dict(old['G_EXCEPTION'], approved_inputs=[[[]]])
    scenarios = []
    for ident, before, after, expected, classification in [
        ('M01', 'original', 'corrected', 'specified_tests_passed', ['maintained_pass', 'improved', 'improved']),
        ('M02', 'compensated_original', 'compensated_patch', 'partial_success', ['remaining_failure', 'improved', 'remaining_failure']),
        ('M03', 'corrected', 'compensated_patch', 'regression_detected', ['regression', 'maintained_pass', 'regression'])]:
        scenarios.append({'scenario_id': ident, 'case_id': 'SUM', 'before_version': before,
            'after_version': after, 'inputs': [[0], [1], [3]], 'expected_status': expected,
            'expected_classifications': classification, 'context': {
                'data_origin': 'author_frozen_simulated_modification_not_real_student',
                'previous_question': '请自行修改并保留理由；核验原失败输入，也保留原本通过的输入。',
                'student_answer': '我提交了一个修改版本，请核对前后结果。'}})
    dump(data / 'registry.json', registry)
    dump(data / 'scenarios.json', scenarios)
    dump(data / 'protocol.json', {
        'version': 'F04_v1', 'formal_runs': 1, 'cases': 3, 'checks_per_case': 3, 'model_calls': 0,
        'plan': ['freeze reviewed historical versions and evaluation', 'red test',
                 'add version diff and F03 comparison wrapper', 'one formal run', 'deterministic regression', 'short reports'],
        'architecture': 'F03 execution + F01 action protocol + F02 validation/termination; deterministic fact feedback',
        'metrics': ['before_after_identity', 'improved', 'regression', 'remaining_failure',
                    'maintained_pass', 'execution_unavailable', 'pending_unknown_code', 'feedback_protocol_valid'],
        'truth': 'actual F03 execution and frozen independent oracle; no AI grading',
        'safe_boundary': 'Only registered historical reviewed code and approved inputs; pasted unknown code is saved, never executed',
        'feedback_scope': 'specified inputs only; no global repair, learner mastery, unique cause, or new question generation',
        'human_review': 'Teaching wording needs human review; no real learner outcome data',
        'approval_origin': 'historical author-reviewed frozen fixtures; not independent human certification'})
    # Preserve the exact previous F03 implementation before its additive catalog extension.
    archive = ROOT / 'history'
    archive.mkdir(exist_ok=False)
    (archive / 'F03_verifier_before_extension.py.txt').write_bytes(Path(f03.__file__).read_bytes())
    prior = json.loads((f03.ROOT / 'prior_dependencies.json').read_text(encoding='utf-8'))['sha256']
    for p in [f03.ROOT / 'freeze.json', f03.ROOT / 'prior_dependencies.json', f03.ROOT / 'data/registry.json',
              f03.ROOT.parents[1] / 'data/b_cases_v3.json', f03.ROOT.parents[1] / 'data/frozen_amendment_b_v3.json',
              ROOT.parent / 'F01_response_adaptation/core.py', ROOT.parent / 'F02_dynamic_questioning/core.py']:
        prior[str(p.resolve())] = digest(p)
    dump(ROOT / 'historical_manifest.json', {'sha256': prior,
        'previous_F03_verifier_sha256': digest(archive / 'F03_verifier_before_extension.py.txt'),
        'historical_F03_results_sha256': {str(p.resolve()): digest(p) for p in (f03.ROOT / 'results').rglob('*') if p.is_file()}})
    frozen = [*data.glob('*.json'), ROOT / 'historical_manifest.json', archive / 'F03_verifier_before_extension.py.txt']
    dump(ROOT / 'freeze.json', {'utc': datetime.now(timezone.utc).isoformat(),
         'sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in frozen}})
    print('Frozen 3 scenarios, 9 paired checks; historical code only, no execution or model call')


if __name__ == '__main__':
    main()
