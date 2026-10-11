import unittest
from experiments.metrics_b import summarize


class BMetricsTests(unittest.TestCase):
    def test_rejecting_everything_has_zero_coverage(self):
        cases = [{"id": "x", "gold_causes": ["init_zero"], "unclear": False}]
        rows = [{"case_id": "x", "claim_id": "a", "cause": "init_zero", "scope": "program",
                 "status": "inconclusive", "reference_issue": None, "extra_executions": 0,
                 "extra_processes": 0, "elapsed_ms": 0, "prediction_verified": True}]
        result = summarize(cases, rows)
        self.assertEqual(result["covered_buggy_cases"], 0)
        self.assertEqual(result["accepted_true_causes"], 0)

    def test_duplicate_true_claims_do_not_inflate_cause_coverage(self):
        cases = [{"id": "x", "gold_causes": ["init_zero"], "unclear": False}]
        base = {"case_id": "x", "cause": "init_zero", "scope": "program", "status": "supported_local",
                "reference_issue": None, "extra_executions": 1, "extra_processes": 1,
                "elapsed_ms": 1, "prediction_verified": True}
        result = summarize(cases, [{**base, "claim_id": "a"}, {**base, "claim_id": "b"}])
        self.assertEqual(result["accepted_true_causes"], 2)
        self.assertEqual(result["covered_gold_causes"], 1)


if __name__ == "__main__":
    unittest.main()
