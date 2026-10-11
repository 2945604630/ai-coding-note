import importlib.util
import unittest


class RunnerTests(unittest.TestCase):
    def runner(self):
        self.assertIsNotNone(importlib.util.find_spec("experiments.runner"), "runner not implemented")
        from experiments.runner import execute
        return execute

    def test_actual_value_and_runtime_failure(self):
        execute = self.runner()
        result = execute("def solve(xs):\n    return xs[0]\n", [[[]], [[7]]])
        self.assertEqual([r["status"] for r in result], ["runtime_error", "ok"])
        self.assertEqual(result[1]["value"], 7)
        self.assertIn("IndexError", result[0]["error"])

    def test_import_is_not_executed(self):
        result = self.runner()("import os\ndef solve(xs):\n    return 0\n", [[[1]]])
        self.assertEqual(result[0]["status"], "rejected_source")

    def test_timeout_and_output_limit_are_not_values(self):
        execute = self.runner()
        r = execute("def solve(n):\n    while True:\n        n += 1\n", [[1]], timeout=0.25)
        self.assertEqual(r[0]["status"], "timeout")
        r = execute("def solve(n):\n    return [0] * 1024\n", [[1]], output_limit=100)
        self.assertEqual(r[0]["status"], "output_limit")

    def test_environment_and_resource_enforcement(self):
        result = self.runner()("def solve(n):\n    return n + 1\n", [[2]])
        self.assertEqual(result[0]["value"], 3)
        self.assertTrue(result[0]["limits"]["memory_enforced"])
        self.assertEqual(result[0]["limits"]["max_processes"], 1)

    def test_memory_cap_failure_is_not_a_program_verdict(self):
        result = self.runner()("def solve(n):\n    return [0] * (1024 * 1024 * 1024)\n", [[1]])
        self.assertIn(result[0]["status"], {"resource_limit", "environment_error"})
        self.assertNotIn(result[0]["status"], {"ok", "runtime_error"})


if __name__ == "__main__":
    unittest.main()
