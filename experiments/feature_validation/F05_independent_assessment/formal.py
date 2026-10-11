"""One formal three-scenario run; no model generation or learning-effect claims."""
from datetime import datetime, timezone
import json
import platform

from experiments.common import digest
from .catalog import ROOT, load
from . import core, records as log


def teacher_record(text):
    return {'interpretation': '冻结模拟教学记录，非真实模型输出。', 'answer_quotes': [],
        'evidence_sufficiency': 'partial', 'next_action': 'tiered_hint', 'student_message': text,
        'decision_basis': '仅用于检验帮助记录和来源关联。', 'uncertainties': ['没有真实学习者数据。'],
        'evidence_refs': ['SOURCE', 'CONTRACT'], 'execution_requests': [],
        'question_intent': '冻结的帮助暴露事件', 'stop_questioning': True, 'stop_reason': 'await_new_evidence'}


def main():
    registry = load()
    directory = ROOT / 'results/formal_v1'
    directory.mkdir(exist_ok=False)
    log.write(directory / 'environment.json', {'utc': datetime.now(timezone.utc).isoformat(),
        'platform': platform.platform(), 'python': platform.python_version(), 'model_calls': 0,
        'command': 'python -X utf8 -m experiments.feature_validation.F05_independent_assessment.formal',
        'freeze_sha256': digest(ROOT / 'freeze.json'),
        'implementation_sha256': {p.name: digest(p) for p in ROOT.glob('*.py')},
        'F03_verifier_sha256': digest(ROOT.parent / 'F03_evidence_verification/verifier.py'),
        'F04_core_sha256': digest(ROOT.parent / 'F04_self_modification/core.py')})
    scenarios = log.read(ROOT / 'data/scenarios.json')
    results = []
    for item in scenarios:
        d = core.create(directory / item['scenario_id'], coverage=item['coverage'],
                        origin='frozen_simulated_assessment_not_real_student', learner_id='SIM_' + item['scenario_id'])
        for event in item['events']:
            if event['kind'] == 'question_seen':
                core.record_help(d, event['kind'], event['target'], event['content'],
                                 provenance={'origin': 'frozen_simulated_prior_display'})
            else:
                core.record_teacher_action(d, teacher_record(event['content']), event['target'],
                    exposure_type=event['kind'], origin='frozen_simulated_teacher_action_not_real_AI')
        code = registry['MAX']['versions'][item['first_version']]['source']
        first = core.freeze_first(d, item['first_version'], code, submission_origin='frozen_simulated_submission')
        initial_hash = digest(d / 'first/result.json')
        if item.get('revision_version'):
            code = registry['MAX']['versions'][item['revision_version']]['source']
            core.revise(d, item['revision_version'], code)
        view = core.view(d)
        matches = (first['eligibility_at_freeze']['status'] == item['expected_eligibility'] and
                   first['score']['passed'] == item['expected_first_passed'] and
                   view['current_eligibility']['status'] == item['expected_eligibility'] and
                   digest(d / 'first/result.json') == initial_hash)
        if item.get('revision_version'):
            matches = matches and view['revisions'][0]['comparison']['summary']['after_passed'] == item['expected_revision_passed']
        # Store each case in its own file, then preserve progress via unique case records.
        record = {'scenario_id': item['scenario_id'], 'matches_frozen_expectation': matches,
                  'first_result_sha256_unchanged': initial_hash, 'view': view}
        log.write(directory / (item['scenario_id'] + '_view.json'), record)
        results.append(record)
        print(item['scenario_id'], first['eligibility_at_freeze']['status'], 'first=', first['score'],
              'revisions=', len(view['revisions']), 'expected_match=', matches)
    actual_executions = sum(len(r['view']['first']['tests']) + sum(
        len(c['comparison']['tests']) * 2 for c in r['view']['revisions']) for r in results)
    summary = {'formal_cases': 3, 'eligibility_correct': sum(r['matches_frozen_expectation'] for r in results),
               'independent_first_pass_by_records': sum(r['view']['independent_first_pass_by_records'] for r in results),
               'actual_executions': actual_executions, 'first_scores_preserved': 3,
               'help_events_preserved': sum(len(r['view']['help_records']) for r in results),
               'model_calls': 0, 'real_learners': 0, 'learning_effect_validated': False}
    log.write(directory / 'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not all(r['matches_frozen_expectation'] for r in results):
        raise SystemExit('Formal mismatch preserved; no replacement or silent rerun')


if __name__ == '__main__':
    main()
