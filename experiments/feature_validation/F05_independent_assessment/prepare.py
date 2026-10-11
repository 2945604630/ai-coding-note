"""Freeze three record scenarios using two existing reviewed maximum implementations."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from experiments.common import digest, dump
from experiments.runner import audit_source, source_hash
from ..F03_evidence_verification import verifier as f03
from ..F04_self_modification.catalog import load as load_f04

ROOT = Path(__file__).resolve().parent


def main():
    if (ROOT / 'freeze.json').exists():
        raise FileExistsError('F05 already frozen')
    (ROOT / 'data').mkdir(exist_ok=False)
    (ROOT / 'results').mkdir(exist_ok=False)
    (ROOT / 'history').mkdir(exist_ok=False)
    load_f04()
    base = f03.load_registry()['C']
    ui = ROOT.parents[1] / 'round5_ui_model'
    wrong_path = ui / 'cases/07.json'
    wrong = json.loads(wrong_path.read_text(encoding='utf-8'))
    frozen = json.loads((ui / 'freeze_manifest.json').read_text(encoding='utf-8'))['sha256']
    assert digest(wrong_path) == frozen['cases/07.json']
    assert source_hash(wrong['source']) == wrong['source_sha256'] and audit_source(wrong['source']) is None
    assert wrong['task'] == base['task'] and wrong['domain'] == base['domain']
    registry = {'MAX': {k: v for k, v in base.items() if k != 'versions'}}
    registry['MAX'].update(case_id='MAX', approved_inputs=[[[-5, -2]], [[2, 9]]],
        versions={'correct': base['versions']['original'],
                  'buggy': {'source': wrong['source'], 'source_hash': wrong['source_sha256']}},
        version_origins={'correct': base['review_origin'], 'buggy': str(wrong_path.resolve())})
    identity = {k: registry['MAX'][k] for k in ['task', 'statement', 'input_contract']}
    content_hash = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    question = {'question_id': 'F05_MAX_01', 'question_version': 'v1', 'case_id': 'MAX',
        'content_hash': content_hash, 'statement': base['statement'], 'input_contract': base['input_contract'],
        'source': {'path': base['review_origin'], 'sha256': base['review_origin_sha256']},
        'original_task': {'question_id': 'F04_SUM', 'version': 'F04_v1', 'task': 'inclusive_sum',
            'evidence_path': str((ROOT.parent / 'F04_self_modification/results/formal_v1/M01/result.json').resolve())},
        'relationship': 'Different reviewed task from the original inclusive_sum; not a validated equivalent transfer test',
        'novelty_scope': 'not previously displayed in this simulated learner session; historically reused research item'}
    covered = {'history_complete': True, 'prior_exposure_checked': True, 'source_record_complete': True,
               'external_help_declaration': 'none'}
    scenarios = [
        {'scenario_id': 'T01', 'coverage': covered, 'first_version': 'correct',
         'expected_eligibility': 'eligible_by_records', 'expected_first_passed': 2,
         'events': [{'kind': 'ai_help', 'target': 'original', 'content': '原题的循环边界教学记录，非本题提示。'}]},
        {'scenario_id': 'T02', 'coverage': covered, 'first_version': 'correct',
         'expected_eligibility': 'assisted_or_exposed', 'expected_first_passed': 2,
         'events': [{'kind': 'question_seen', 'target': 'assessment', 'content': '提交前曾提前见过本题。'},
                    {'kind': 'hint', 'target': 'assessment', 'content': '先核对返回值是否来自输入列表。'},
                    {'kind': 'full_answer', 'target': 'assessment', 'content': base['versions']['original']['source']}]},
        {'scenario_id': 'T03', 'coverage': dict(covered, external_help_declaration='unknown'),
         'first_version': 'buggy', 'revision_version': 'correct',
         'expected_eligibility': 'unknown', 'expected_first_passed': 1, 'expected_revision_passed': 2,
         'events': []}]
    dump(ROOT / 'data/registry.json', registry)
    dump(ROOT / 'data/question.json', question)
    dump(ROOT / 'data/scenarios.json', scenarios)
    dump(ROOT / 'data/protocol.json', {'version': 'F05_v1', 'formal_runs': 1, 'formal_cases': 3, 'model_calls': 0,
        'states': ['eligible_by_records', 'assisted_or_exposed', 'unknown'],
        'policy': {'normal_assessment_presentation_allowed': True,
                   'original_only_help_not_automatically_new_task_help': True,
                   'pre_first_hint_answer_AI_external_help_or_prior_view_disqualifies': True,
                   'missing_history_source_or_external_declaration_is_unknown': True,
                   'revisions_never_replace_first_code_score_or_frozen_qualification': True,
                   'later_disclosed_pre_first_help_can_only_downgrade_current_view': True},
        'metrics': ['first_code_preserved', 'help_records_retained', 'qualification_correct',
                    'first_score_unchanged_after_revision', 'version_evidence_match', 'unreviewed_not_executed'],
        'truth': 'frozen explicit record rules + actual F03 execution, not AI rating or learning truth',
        'limitations': ['no proof of absent external help', 'local append-only API plus hash checks, not OS immutable storage',
                       'target and relevance labels require trustworthy input/human review', 'no real learner data'],
        'plan': ['freeze cases and policy', 'red test', 'append-only record and eligibility module',
                 'one formal run', 'necessary deterministic regression', 'short reports']})
    dependencies = json.loads((ROOT.parent / 'F04_self_modification/historical_manifest.json').read_text(encoding='utf-8'))['sha256']
    for p in [wrong_path, ROOT.parent / 'F04_self_modification/freeze.json',
              ROOT.parent / 'F04_self_modification/data/registry.json', Path(question['original_task']['evidence_path'])]:
        dependencies[str(p.resolve())] = digest(p)
    previous = {}
    for name, file in [('F03_verifier', Path(f03.__file__)), ('F04_core', ROOT.parent / 'F04_self_modification/core.py')]:
        archived = ROOT / ('history/' + name + '_before_F05.py.txt')
        archived.write_bytes(file.read_bytes())
        previous[name] = {'original': str(file), 'archive': str(archived), 'sha256': digest(archived)}
    historical = {}
    for stage in ['F03_evidence_verification', 'F04_self_modification']:
        directory = ROOT.parent / stage
        for sub in ['results', 'data']:
            for p in (directory / sub).rglob('*'):
                if p.is_file(): historical[str(p.resolve())] = digest(p)
        for p in directory.glob('*.md'): historical[str(p.resolve())] = digest(p)
    dump(ROOT / 'historical_manifest.json', {'sha256': dependencies, 'previous_implementations': previous,
         'prior_records_sha256': historical})
    files = [* (ROOT / 'data').glob('*.json'), ROOT / 'historical_manifest.json', * (ROOT / 'history').glob('*')]
    dump(ROOT / 'freeze.json', {'utc': datetime.now(timezone.utc).isoformat(),
        'sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in files}})
    print('Frozen T01/T02/T03 and record policy; historical reviewed code only; no execution/model call')


if __name__ == '__main__':
    main()
