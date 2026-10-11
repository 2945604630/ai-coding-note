"""Unit fixtures are validator inputs, never independent model results."""
import importlib
import unittest

try:
    core = importlib.import_module('experiments.feature_validation.F01_response_adaptation.core')
except ModuleNotFoundError:
    core = None


class CoreTests(unittest.TestCase):
    def test_feature_available(self):
        self.assertIsNotNone(core, 'F01 implementation has not been written')

    @unittest.skipIf(core is None, 'implementation missing')
    def test_program_prediction_is_not_normative_error(self):
        output = core.baseline('07', '我说的是代码输出0，不是题目的答案；想先用一个负数检验。')
        self.assertEqual(output['next_action'], 'show_counterexample')
        self.assertNotIn('你不懂', output['student_message'])

    @unittest.skipIf(core is None, 'implementation missing')
    def test_hedged_zero_answer_needs_clarification(self):
        output = core.baseline('07', '0大概没问题吧，我说不清。')
        self.assertEqual(output['next_action'], 'clarify_meaning')
        self.assertEqual(output['evidence_sufficiency'], 'insufficient')

    @unittest.skipIf(core is None, 'implementation missing')
    def test_reject_illegal_test_without_execution(self):
        case = core.read(core.ROOT/'cases/07.json')
        row = core.check_request(case, {'args':[[]], 'predicted_actual':0, 'predicted_expected':0})
        self.assertFalse(row['input_legal'])
        self.assertIsNone(row['execution'])

    @unittest.skipIf(core is None, 'implementation missing')
    def test_predict_original_not_repaired_program(self):
        case = core.read(core.ROOT/'cases/07.json')
        row = core.check_request(case, {'args':[[-8]], 'predicted_actual':-8, 'predicted_expected':-8})
        self.assertTrue(row['input_legal'])
        self.assertFalse(row['actual_prediction_correct'])
        self.assertTrue(row['expected_prediction_correct'])
        self.assertEqual(row['execution']['value'], 0)

    @unittest.skipIf(core is None, 'implementation missing')
    def test_public_prompts_have_same_facts_and_no_private_labels(self):
        public = {'student_answer':'只说明这句话', 'evidence':[]}
        a,b = core.prompt(public,'S1'),core.prompt(public,'S2')
        self.assertEqual(core.public_from_prompt(a),core.public_from_prompt(b))
        for token in ('allowed_actions','expected_interpretation','private_marker'):
            self.assertNotIn(token,a+b)

    @unittest.skipIf(core is None, 'implementation missing')
    def test_invalid_quote_not_treated_as_verified(self):
        output = core.baseline('07', '说不清')
        output['answer_quotes'] = ['我完全理解了']
        case = core.read(core.ROOT/'cases/07.json')
        checked = core.validate_output(output, {'student_answer':'说不清','case':case})
        self.assertFalse(checked['answer_quotes_valid'])
        self.assertFalse(checked['display_safe'])


if __name__ == '__main__': unittest.main()
