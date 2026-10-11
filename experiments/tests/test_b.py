import importlib.util
import unittest
from experiments.runner import source_hash

SOURCE = "def solve(n):\n    s = 0\n    for i in range(1, n):\n        s += i\n    return s\n"


class DiagnosisTests(unittest.TestCase):
    def test_resource_failure_is_not_an_observed_program_error(self):
        from experiments.common import load_frozen
        from experiments.diagnosis import collect_evidence, verify_claim
        from experiments.runner import source_hash
        case = next(c for c in load_frozen("b_cases_v3.json") if c["id"] == "b09")
        evidence = collect_evidence(case)
        evidence["e1"].update(status="resource_limit", passed=False, error="MemoryError: injected evidence status")
        claim = {"cause": "init_zero", "scope": "program", "evidence_ids": ["e0"],
                 "code_hash": source_hash(case["source"]), "probe_args": [[2, 3]],
                 "predicted": {"status": "ok", "value": 3}}
        self.assertEqual(verify_claim(case, evidence, claim, "B1")["status"], "inconclusive")
        self.assertEqual(verify_claim(case, evidence, claim, "B2")["status"], "inconclusive")

    def api(self):
        self.assertIsNotNone(importlib.util.find_spec("experiments.diagnosis"), "diagnosis not implemented")
        from experiments.diagnosis import collect_evidence, verify_claim
        return collect_evidence, verify_claim

    def setup_claim(self, cause="loop_end_excluded", predicted=6):
        collect, verify = self.api()
        case = {"task": "inclusive_sum", "domain": "default", "source": SOURCE, "inputs": [[3], [1]]}
        evidence = collect(case)
        claim = {"cause": cause, "scope": "program", "evidence_ids": ["e0"], "code_hash": source_hash(SOURCE),
                 "probe_args": [4], "predicted": {"status": "ok", "value": predicted}, "next_action": "test_prediction"}
        return verify, case, evidence, claim

    def test_true_cause_survives_while_competitor_is_refuted(self):
        verify, case, evidence, claim = self.setup_claim()
        self.assertEqual(verify(case, evidence, claim, "B2")["status"], "supported_local")
        claim.update(cause="accumulator_overwrite", predicted={"status": "ok", "value": 4})
        self.assertEqual(verify(case, evidence, claim, "B1")["status"], "accepted_unverified")
        self.assertEqual(verify(case, evidence, claim, "B2")["status"], "refuted")

    def test_missing_stale_and_invalid_probe(self):
        verify, case, evidence, claim = self.setup_claim()
        claim["evidence_ids"] = ["never_existed"]
        self.assertEqual(verify(case, evidence, claim, "B2")["status"], "invalid_reference")
        claim["evidence_ids"] = ["e0"]
        claim["code_hash"] = "old_version"
        self.assertEqual(verify(case, evidence, claim, "B2")["status"], "stale")
        claim["code_hash"] = source_hash(SOURCE)
        claim["probe_args"] = [-1]
        self.assertEqual(verify(case, evidence, claim, "B2")["status"], "invalid_probe")

    def test_correct_behavior_prediction_does_not_confirm_unsupported_cause(self):
        verify, case, evidence, claim = self.setup_claim("careless_reading", 6)
        result = verify(case, evidence, claim, "B2")
        self.assertEqual(result["status"], "inconclusive")
        self.assertTrue(result["prediction_verified"])
        self.assertFalse(result["cause_supported"])

    def test_program_error_never_proves_learner_misunderstanding(self):
        verify, case, evidence, claim = self.setup_claim()
        claim["scope"] = "learner"
        self.assertEqual(verify(case, evidence, claim, "B2")["status"], "inconclusive")
