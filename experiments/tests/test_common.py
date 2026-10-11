import importlib.util
import unittest


class ReferenceTests(unittest.TestCase):
    def common(self):
        self.assertIsNotNone(importlib.util.find_spec("experiments.common"), "references not implemented")
        from experiments import common
        return common

    def test_independent_reference_boundaries(self):
        c = self.common()
        self.assertEqual(c.oracle("max", [[-5, -2]]), -2)
        self.assertEqual(c.oracle("min", [[2, 7]]), 2)
        self.assertEqual(c.oracle("inclusive_sum", [0]), 0)
        self.assertEqual(c.oracle("inclusive_sum", [4]), 10)
        self.assertEqual(c.oracle("sum_items", [[-2, 4]]), 2)
        self.assertEqual(c.oracle("copy_items", [[]]), [])

    def test_invalid_probe_and_unknown_precondition(self):
        c = self.common()
        self.assertFalse(c.valid_args("max", [[]])[0])
        self.assertFalse(c.valid_args("inclusive_sum", [-1])[0])
        self.assertFalse(c.valid_args("inclusive_sum", [True])[0])
        self.assertFalse(c.valid_args("max", [[-1]], "unknown_sign")[0])
        self.assertTrue(c.valid_args("max", [[1]], "unknown_sign")[0])

