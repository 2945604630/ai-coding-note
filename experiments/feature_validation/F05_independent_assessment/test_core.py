import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.common import digest
from ..F03_evidence_verification import verifier as f03
from . import core

COVERED = {'history_complete': True, 'prior_exposure_checked': True, 'source_record_complete': True,
           'external_help_declaration': 'none'}


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        artifacts = os.environ.get('F05_REGRESSION_ARTIFACTS')
        if artifacts:
            self.root = Path(artifacts) / self._testMethodName
            self.root.mkdir(parents=True, exist_ok=False)
        else:
            temp = tempfile.TemporaryDirectory(prefix='f05_test_')
            self.addCleanup(temp.cleanup)
            self.root = Path(temp.name)

    def new(self, coverage=None):
        return core.create(self.root/'session', coverage=COVERED if coverage is None else coverage,
                           origin='simulated_regression_not_real_student')

    def source(self, version):
        from .catalog import load
        return load()['MAX']['versions'][version]['source']

    def submit(self, directory, version='correct'):
        return core.freeze_first(directory, version, self.source(version), submission_origin='frozen_simulated_submission')

    def test_first_submission_freezes_record_qualification_separately_from_score(self):
        try:
            d = self.new()
        except NotImplementedError:
            self.fail('F05 must freeze first submission and separate qualification from execution')
        first = self.submit(d)
        self.assertEqual(first['eligibility_at_freeze']['status'], 'eligible_by_records')
        self.assertEqual(first['score']['passed'], 2)
        self.assertFalse(first['absence_of_external_help_proven'])
        self.assertIsNone(first['student_mastery_confirmed'])
        sha = digest(d/'first/source.py')
        with self.assertRaises(FileExistsError): self.submit(d, 'buggy')
        self.assertEqual(digest(d/'first/source.py'), sha)

    def test_recorded_help_and_prior_display_disqualify_even_passing_code(self):
        d = self.new()
        core.record_help(d, 'question_seen', 'assessment', '此前展示')
        core.record_help(d, 'full_answer', 'assessment', '完整答案暴露')
        first = self.submit(d)
        self.assertEqual(first['eligibility_at_freeze']['status'], 'assisted_or_exposed')
        self.assertEqual(first['score']['passed'], 2)

    def test_eligible_records_do_not_turn_failing_code_into_a_pass(self):
        d = self.new()
        first = self.submit(d, 'buggy')
        self.assertEqual(first['eligibility_at_freeze']['status'], 'eligible_by_records')
        self.assertEqual(first['score']['passed'], 1)
        self.assertFalse(core.view(d)['independent_first_pass_by_records'])

    def test_original_task_help_does_not_silently_disappear_or_disqualify_new_task(self):
        d = self.new()
        core.record_help(d, 'ai_help', 'original', '原题范围提示')
        first = self.submit(d)
        self.assertEqual(first['eligibility_at_freeze']['status'], 'eligible_by_records')
        self.assertEqual(len(core.view(d)['help_records']), 1)

    def test_revision_success_cannot_replace_unknown_first_result(self):
        d = self.new(dict(COVERED, external_help_declaration='unknown'))
        first = self.submit(d, 'buggy')
        sha = digest(d/'first/result.json')
        rev = core.revise(d, 'correct', self.source('correct'))
        self.assertEqual(first['score']['passed'], 1)
        self.assertEqual(rev['comparison']['summary']['after_passed'], 2)
        self.assertEqual(core.view(d)['first']['score']['passed'], 1)
        self.assertEqual(core.view(d)['current_eligibility']['status'], 'unknown')
        self.assertFalse(rev['is_first_submission'])
        self.assertEqual(digest(d/'first/result.json'), sha)

    def test_unreviewed_code_is_saved_and_never_executes(self):
        d = self.new({})
        source = 'import os\nprint("not executed")\n'
        with patch.object(f03, 'execute', side_effect=AssertionError('must not execute')):
            first = core.freeze_first(d, 'unknown_version', source)
        self.assertEqual(first['execution_state'], 'pending_review')
        self.assertEqual(first['eligibility_at_freeze']['status'], 'unknown')
        self.assertEqual((d/'first/source.py').read_text(encoding='utf-8'), source)

    def test_late_pre_submission_help_downgrades_view_without_rewriting_first(self):
        d = self.new()
        self.submit(d)
        sha = digest(d/'first/result.json')
        core.record_help(d, 'external_help', 'assessment', '补充披露提交前曾咨询他人', applies_before_first=True)
        self.assertEqual(core.view(d)['current_eligibility']['status'], 'assisted_or_exposed')
        self.assertEqual(digest(d/'first/result.json'), sha)

    def test_post_submission_help_does_not_relabel_frozen_first_attempt(self):
        d = self.new()
        self.submit(d)
        core.record_help(d, 'hint', 'assessment', '提交后提示')
        self.assertEqual(core.view(d)['current_eligibility']['status'], 'eligible_by_records')

    def test_missing_history_or_uncertain_help_scope_never_becomes_eligible(self):
        d = self.new(dict(COVERED, history_complete=False))
        core.record_help(d, 'ai_help', 'unknown', '帮助是否相关尚不明确')
        self.assertEqual(self.submit(d)['eligibility_at_freeze']['status'], 'unknown')

    def test_tampering_and_illegal_test_inputs_are_not_silently_accepted(self):
        d = self.new()
        with patch.object(f03,'execute',side_effect=AssertionError('must not execute')):
            first = core.freeze_first(d,'correct',self.source('correct'), inputs=[[[]]], submission_origin='frozen_simulated_submission')
        self.assertEqual(first['execution_state'],'blocked_inputs')
        (d/'first/source.py').write_text('tampered',encoding='utf-8')
        with self.assertRaises(ValueError): core.view(d)


if __name__ == '__main__':
    unittest.main()
