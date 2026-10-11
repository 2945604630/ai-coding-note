import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.common import digest
from ..F03_evidence_verification import verifier as f03
from . import core


class ModificationTests(unittest.TestCase):
    def setUp(self):
        artifacts = os.environ.get('F04_REGRESSION_ARTIFACTS')
        if artifacts:
            self.root = Path(artifacts) / self._testMethodName
            self.root.mkdir(parents=True, exist_ok=False)
        else:
            temp = tempfile.TemporaryDirectory(prefix='f04_tests_')
            self.addCleanup(temp.cleanup)
            self.root = Path(temp.name)

    def compare(self, **kwargs):
        return core.compare('SUM', 'original', 'corrected', record_dir=self.root / 'record', **kwargs)

    def test_approved_change_links_both_versions_and_does_not_claim_mastery(self):
        try:
            r = self.compare(inputs=[[0], [1]])
        except NotImplementedError:
            self.fail('F04 must compare real before/after evidence')
        self.assertEqual(r['summary']['improved'], 1)
        self.assertEqual(r['summary']['maintained_pass'], 1)
        self.assertTrue(r['modification']['changed'])
        self.assertTrue(r['modification']['locations'])
        self.assertNotEqual(r['before']['source_hash'], r['after']['source_hash'])
        self.assertEqual(r['after']['parent_source_hash'], r['before']['source_hash'])
        self.assertEqual(r['status'], 'specified_tests_passed')
        self.assertIsNone(r['overall_repair_confirmed'])
        self.assertIsNone(r['student_mastery_confirmed'])
        self.assertTrue(r['feedback_validation']['display_safe'])
        self.assertTrue(r['feedback']['stop_questioning'])
        self.assertNotEqual(r['feedback']['stop_reason'], 'understanding_sufficient')

    def test_pasted_unknown_code_is_saved_but_never_executed(self):
        source = 'import os\nprint("unreviewed")\n'
        with patch.object(f03, 'execute', side_effect=AssertionError('must not execute')):
            r = core.compare('SUM', 'original', 'student_v2', submitted_source=source, record_dir=self.root/'record')
        self.assertEqual(r['status'], 'pending_review')
        self.assertEqual(r['tests'], [])
        self.assertEqual(Path(r['after']['source_file']).read_text(encoding='utf-8'), source)
        self.assertEqual(r['after']['parent_source_hash'], r['before']['source_hash'])

    def test_claimed_registered_version_with_different_code_is_not_executed(self):
        with patch.object(f03, 'execute', side_effect=AssertionError('must not execute')):
            r = self.compare(submitted_source='def solve(n):\n    return 99\n')
        self.assertEqual(r['status'], 'pending_review')
        self.assertEqual(r['error_reason'], 'submitted_source_not_registered')

    def test_unknown_before_hash_illegal_input_and_unapproved_input_are_blocked(self):
        for i, kwargs in enumerate([{'before_hash': 'wrong'}, {'inputs': [[True]]}, {'inputs': [[2]]}, {'inputs': []}]):
            with patch.object(f03, 'execute', side_effect=AssertionError('must not execute')):
                r = core.compare('SUM', 'original', 'corrected', record_dir=self.root/str(i), **kwargs)
            self.assertEqual(r['status'], 'blocked')
            self.assertEqual(r['tests'], [])

    def test_same_source_is_not_a_new_fix_and_record_cannot_be_overwritten(self):
        r = core.compare('SUM','original','original',inputs=[[0]],record_dir=self.root/'record')
        self.assertFalse(r['modification']['changed'])
        old = digest(self.root/'record/result.json')
        with self.assertRaises(FileExistsError):
            core.compare('SUM','original','corrected',record_dir=self.root/'record')
        self.assertEqual(old,digest(self.root/'record/result.json'))

    def test_actual_execution_failure_is_retained_and_not_called_improvement(self):
        r = core.compare('G_EXCEPTION','original','original',inputs=[[[]]],record_dir=self.root/'record')
        self.assertEqual(r['status'],'execution_incomplete')
        self.assertEqual(r['summary']['unable_to_compare'],1)
        self.assertEqual(r['summary']['improved'],0)
        self.assertEqual(r['tests'][0]['after']['execution']['status'],'runtime_error')
        self.assertTrue(Path(r['tests'][0]['after']['evidence_files']['failure']).exists())


if __name__ == '__main__':
    unittest.main()
