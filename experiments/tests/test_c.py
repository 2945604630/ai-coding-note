import unittest
from experiments.common import load_frozen
from experiments.quality import validate_pack


class QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packs = {p["id"]: p for p in load_frozen("c_packs.json")}

    def test_weak_tests_fail_both_strong_generic_and_target_gate(self):
        pack = self.packs["c05"]
        self.assertTrue(validate_pack(pack, "C0")["accepted"])
        self.assertFalse(validate_pack(pack, "C1")["accepted"])
        result = validate_pack(pack, "C2")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "target_survives")

    def test_shared_wrong_reference_is_not_its_own_oracle(self):
        pack = self.packs["c09"]
        self.assertTrue(validate_pack(pack, "C1")["accepted"])
        result = validate_pack(pack, "C2")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "independent_reference_conflict")

    def test_semantics_and_concept_review_are_distinct(self):
        pack = self.packs["c12"]
        self.assertTrue(validate_pack(pack, "C1")["accepted"])
        self.assertEqual(validate_pack(pack, "C2")["reason"], "off_concept")

    def test_strict_starter_policy_false_reject_is_retained(self):
        result = validate_pack(self.packs["c01"], "C0")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "starter_already_passes")
        self.assertTrue(result["checks"]["reference_pass"])

    def test_good_pack_remains_accepted(self):
        for variant in ["C0", "C1", "C2", "C2_without_target"]:
            with self.subTest(variant=variant):
                self.assertTrue(validate_pack(self.packs["c02"], variant)["accepted"])

    def test_target_ablation_is_really_removed(self):
        pack = self.packs["c07"]
        self.assertTrue(validate_pack(pack, "C2_without_target")["accepted"])
        self.assertFalse(validate_pack(pack, "C2")["accepted"])


if __name__ == "__main__":
    unittest.main()
