import unittest
from experiments.common import load_frozen, ROOT
from experiments.diagnosis import collect_evidence


class UnknownFixtureTests(unittest.TestCase):
    def test_unknown_premise_fixture_has_no_observed_failure(self):
        name = "b_cases_v3.json" if (ROOT / "data/b_cases_v3.json").exists() else "b_cases_v2.json" if (ROOT / "data/b_cases_v2.json").exists() else "b_cases.json"
        case = next(c for c in load_frozen(name) if c["id"] == "b09")
        self.assertTrue(case["unclear"])
        self.assertNotIn("允许全负数", case["statement"])
        self.assertTrue(all(e["passed"] for e in collect_evidence(case).values()))


if __name__ == "__main__":
    unittest.main()
