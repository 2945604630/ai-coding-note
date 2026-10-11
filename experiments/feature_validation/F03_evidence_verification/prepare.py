"""Freeze three reused cases and nine checks before the one formal run."""
import ast
from datetime import datetime, timezone
import json
from pathlib import Path

from experiments.common import digest, dump
from experiments.runner import audit_source, source_hash

ROOT = Path(__file__).resolve().parent
EXPERIMENTS = ROOT.parents[1]
F02 = ROOT.parent / 'F02_dynamic_questioning'
UI = EXPERIMENTS / 'round5_ui_model'


def main():
    if (ROOT / 'freeze.json').exists():
        raise FileExistsError('Do not overwrite frozen F03 inputs')
    # Allow recovery from an initialization failure, never overwrite partial inputs.
    if (ROOT / 'data').exists() and any((ROOT / 'data').iterdir()):
        raise FileExistsError('Partial F03 inputs exist; inspect them rather than overwrite')
    (ROOT / 'data').mkdir(exist_ok=True)
    (ROOT / 'results').mkdir(exist_ok=True)
    dependencies = [EXPERIMENTS / 'runner.py', EXPERIMENTS / 'worker.py', EXPERIMENTS / 'common.py']
    entries = {}
    for ident, path, freeze in [('A', F02 / 'cases/C01.json', F02 / 'freeze_manifest.json'),
                                 ('B', F02 / 'cases/C03.json', F02 / 'freeze_manifest.json'),
                                 ('C', UI / 'cases/05.json', UI / 'freeze_manifest.json')]:
        raw = json.loads(path.read_text(encoding='utf-8'))
        frozen = {k.replace('\\', '/'): v for k, v in
                  json.loads(freeze.read_text(encoding='utf-8'))['sha256'].items()}
        base = freeze.parent
        assert digest(path) == frozen[str(path.relative_to(base)).replace('\\', '/')]
        entry = {'case_id': ident, 'historical_case_id': raw['case_id'], 'task': raw['task'],
                 'statement': raw['statement'], 'input_contract': raw['input_contract'],
                 'domain': raw.get('domain', 'default'), 'review_origin': str(path.resolve()),
                 'review_origin_sha256': digest(path), 'versions': {}}
        for version, data in [('original', raw), *raw.get('versions', {}).items()]:
            assert source_hash(data['source']) == data['source_sha256']
            assert audit_source(data['source']) is None
            entry['versions'][version] = {'source': data['source'], 'source_hash': data['source_sha256']}
        entries[ident] = entry
        dependencies.extend([path, freeze])
    # Existing deterministically reviewed guard fixtures, not additional teaching cases.
    guard_file = EXPERIMENTS / 'tests/test_runner.py'
    constants = {n.value for n in ast.walk(ast.parse(guard_file.read_text(encoding='utf-8')))
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    guards = {'G_TIMEOUT': ('inclusive_sum', 'def solve(n):\n    while True:\n        n += 1\n'),
              'G_EXCEPTION': ('copy_items', 'def solve(xs):\n    return xs[0]\n'),
              'G_OUTPUT': ('inclusive_sum', 'def solve(n):\n    return [0] * 1024\n')}
    for ident, (task, source) in guards.items():
        assert source in constants and audit_source(source) is None
        entries[ident] = {'case_id': ident, 'task': task, 'domain': 'default',
            'statement': '既有执行器守卫夹具，非教学题', 'input_contract': task,
            'guard_fixture': True, 'review_origin': str(guard_file.resolve()), 'review_origin_sha256': digest(guard_file),
            'versions': {'original': {'source': source, 'source_hash': source_hash(source)}}}
    dependencies.append(guard_file)
    dump(ROOT / 'data/registry.json', entries)
    checks = []

    def claim(ident, case_id, args, kind, expected, path=None, field=None, quote=None,
              origin='historical_real_AI_statement', version='original', value=None, claim_version=None):
        item = {'check_id': ident, 'case_id': case_id, 'args': args, 'source_version': version,
                'expected_verification': expected}
        cv = claim_version or version
        sha = entries[case_id]['versions'][cv]['source_hash']
        info = {'kind': kind, 'text': quote, 'args': args, 'source_hash': sha, 'source_version': cv,
                'origin': origin, 'mapping_origin': 'author_explicit_mapping_not_NL_model_judgment'}
        if kind == 'output_equals':
            info['value'] = value
        if path:
            raw_text = path.read_text(encoding='utf-8')
            text = raw_text
            if field:
                text = json.loads(raw_text)
                for part in field.split('/'):
                    text = text[int(part)] if isinstance(text, list) else text[part]
            assert quote and quote in text
            metadata = path.parent / 'metadata.json' if path.suffix == '.json' else path.with_suffix('.meta.json')
            meta = json.loads(metadata.read_text(encoding='utf-8'))
            assert digest(path) == meta.get('raw_sha256', meta.get('original_cli_last_message_sha256'))
            info['source'] = {'path': str(path.resolve()), 'sha256': digest(path), 'field': field,
                              'metadata_path': str(metadata.resolve()), 'metadata_sha256': digest(metadata)}
            dependencies.extend([path, metadata])
        item['claim'] = info
        checks.append(item)

    first = F02 / 'responses/S1_C01_FIRST/raw_response.json'
    claim('A01', 'A', [3], 'output_equals', 'supported', first, 'decision_basis',
          'E3 显示实际返回 3，而题目要求返回 6。', value=3)
    claim('A02', 'A', [3], 'output_equals', 'refuted', quote='原版solve(3)返回6。',
          origin='author_negative_control_not_model_output', value=6)
    claim('A03', 'A', [3], 'non_executable', 'inconclusive', first, 'uncertainties/0',
          '尚不清楚学生如何理解 range 的终点边界。')
    wrong = F02 / 'responses/S1_C03_wrong_T2/raw_response.json'
    claim('B01', 'B', [1], 'output_equals', 'supported', wrong, 'student_message',
          'local_patch 在 n=1 时通过', version='local_patch', value=1)
    claim('B02', 'B', [3], 'all_inputs_correct', 'refuted', wrong, 'answer_quotes/0',
          '局部改动版在n=1通过，说明它已经修好了，其它返回部分不用看。',
          origin='frozen_simulated_student_quoted_by_real_AI_not_AI_own_judgment', version='local_patch')
    different = F02 / 'responses/S1_C03_unexpected_T2/raw_response.json'
    claim('B03', 'B', [3], 'output_equals', 'inconclusive', different, 'student_message',
          '原版的 5', version='local_patch', claim_version='original', value=5)
    correct = UI / 'responses/generation_v4/S2_05.md'
    claim('C01', 'C', [[-3]], 'output_equals', 'supported', correct, None,
          '预测`solve([-3])`返回`-3`', value=-3)
    claim('C02', 'C', [[-3, 0]], 'output_equals', 'supported', correct, None,
          '`solve([-3,0])`返回`0`', value=0)
    claim('C03', 'C', [[-5, -2]], 'non_executable', 'inconclusive',
          UI / 'responses/generation_v4/S1_05.md', None,
          '未发现符合题目输入前提的正确性错误')
    dump(ROOT / 'data/checks.json', checks)
    dump(ROOT / 'data/protocol.json', {'version': 'F03_v1', 'before_formal_run': True, 'formal_runs': 1,
         'formal_cases': ['A', 'B', 'C'], 'checks_per_case': 3, 'new_model_calls': 0,
         'metrics': ['verifiable', 'correct_support', 'correct_refutation', 'wrong_support_or_refutation',
                     'inconclusive', 'version_mismatch_block', 'illegal_input_block', 'execution_exception'],
         'unsupported_scopes': ['learner_intent', 'learner_understanding', 'unique_root_cause', 'global_correctness_from_passes'],
         'limits': {'timeout_s': 1.5, 'output_bytes': 8192, 'memory_bytes': 134217728, 'Windows_job_process_limit': 1},
         'architecture': 'Thin wrapper around experiments.runner.execute + common.valid_args/oracle; no new executor',
         'plan': ['freeze three cases/claims', 'red test for wrapper', 'implement guarded wrapper and CLI',
                  'one formal run', 'necessary deterministic regression and short reports'],
         'comparison_truth': 'frozen explicit predicates, checked source trace and actual execution, no AI ratings',
         'natural_language_mapping': 'author-reviewed explicit mapping; verifies normalized predicate, not arbitrary prose',
         'guard_fixtures': 'three exact source strings already in experiments/tests/test_runner.py; not teaching cases'})
    dependencies = sorted(set(dependencies))
    dump(ROOT / 'prior_dependencies.json', {'sha256': {str(p.resolve()): digest(p) for p in dependencies}})
    data = [ROOT / 'data/registry.json', ROOT / 'data/checks.json', ROOT / 'data/protocol.json']
    dump(ROOT / 'freeze.json', {'utc': datetime.now(timezone.utc).isoformat(),
         'sha256': {str(p.relative_to(ROOT)): digest(p) for p in data}, 'model_calls': 0})
    print('Frozen: 3 cases, 9 checks; guards reused from existing runner tests; model calls 0')


if __name__ == '__main__':
    main()
