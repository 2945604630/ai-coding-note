"""Small deterministic guards, not extra teaching scenarios."""
from pathlib import Path
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from experiments.common import digest
from . import verifier as v


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='f03_guard_tests_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Formal regression preserves complete execution/error packets, including guard failures.
        artifacts = os.environ.get('F03_REGRESSION_ARTIFACTS')
        if artifacts:
            self.addCleanup(shutil.copytree, self.root, Path(artifacts) / self._testMethodName)

    def run_check(self, case, args, **kwargs):
        return v.verify(case, args, record_dir=self.root / ('record' + str(len(list(self.root.iterdir())))), **kwargs)

    def test_bounded_program_fact_is_supported_by_real_execution(self):
        try:
            result = self.run_check('A', [3], claim={'kind': 'output_equals', 'value': 3})
        except NotImplementedError:
            self.fail('F03 real execution verification is not implemented')
        self.assertEqual(result['actual_output'], 3)
        self.assertEqual(result['reference_output'], 6)
        self.assertEqual(result['verification']['status'], 'supported')
        self.assertFalse(result['matches_reference'])

    def test_illegal_input_never_executes(self):
        for args in [[True], [9], [[-21]], [[]]]:
            case = 'C' if isinstance(args[0], list) else 'A'
            with patch.object(v, 'execute', side_effect=AssertionError('must not execute')):
                result = self.run_check(case, args)
            self.assertFalse(result['allowed_to_execute'])
            self.assertEqual(result['error_reason'], 'illegal_input')

    def test_unknown_version_and_mismatched_hash_never_use_old_results(self):
        for kwargs in [{'source_version': 'student_unprovided'}, {'expected_source_hash': 'wrong_hash'},
                       {'source_version': 'local_patch', 'claim': {'kind': 'output_equals', 'value': 5,
                         'source_hash': v.load_registry()['B']['versions']['original']['source_hash']}}]:
            with patch.object(v, 'execute', side_effect=AssertionError('must not execute')):
                result = self.run_check('B', [3], **kwargs)
            self.assertFalse(result['allowed_to_execute'])
            self.assertIn(result['error_reason'], ['unknown_source_version', 'source_hash_mismatch', 'claim_version_mismatch'])
            self.assertEqual(result['verification']['status'], 'inconclusive')

    def test_one_passing_patch_input_does_not_support_complete_fix(self):
        result = self.run_check('B', [1], source_version='local_patch', claim={'kind': 'all_inputs_correct'})
        self.assertTrue(result['matches_reference'])
        self.assertEqual(result['verification']['status'], 'inconclusive')
        self.assertIsNone(result['program_overall_correct'])
        self.assertFalse(result['unique_root_cause_confirmed'])

    def test_actual_timeout_is_not_support_or_refutation(self):
        result = self.run_check('G_TIMEOUT', [1], timeout=0.25, claim={'kind': 'output_equals', 'value': 1})
        self.assertEqual(result['execution']['status'], 'timeout')
        self.assertEqual(result['verification']['status'], 'inconclusive')
        self.assertTrue(Path(result['evidence_files']['execution']).exists())

    def test_actual_exception_and_output_limit_are_preserved(self):
        result = self.run_check('G_EXCEPTION', [[]], claim={'kind': 'output_equals', 'value': []})
        self.assertEqual(result['execution']['status'], 'runtime_error')
        self.assertIn('IndexError', result['execution']['error'])
        self.assertEqual(result['verification']['status'], 'inconclusive')
        result = self.run_check('G_OUTPUT', [1], output_limit=100)
        self.assertEqual(result['execution']['status'], 'output_limit')
        self.assertIsNone(result['actual_output'])

    def test_boolean_prediction_is_not_equal_to_numeric_zero(self):
        result = self.run_check('A', [0], claim={'kind': 'output_equals', 'value': False})
        self.assertEqual(result['actual_output'], 0)
        self.assertEqual(result['verification']['status'], 'refuted')

    def test_untrusted_reference_and_relaxed_limits_are_blocked(self):
        for kwargs in [{'reference_output': 99}, {'timeout': 5}, {'output_limit': 9000}]:
            with patch.object(v, 'execute', side_effect=AssertionError('must not execute')):
                result = self.run_check('A', [3], **kwargs)
            self.assertFalse(result['allowed_to_execute'])

    def test_existing_evidence_cannot_be_overwritten(self):
        directory = self.root / 'first'
        v.verify('A', [3], record_dir=directory)
        old_hash = digest(directory / 'result.json')
        with self.assertRaises(FileExistsError):
            v.verify('A', [3], record_dir=directory)
        self.assertEqual(digest(directory / 'result.json'), old_hash)


if __name__ == '__main__':
    unittest.main()
