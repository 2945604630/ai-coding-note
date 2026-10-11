import unittest
from experiments.common import load_frozen
from experiments.state import replay


class StateTests(unittest.TestCase):
    def test_all_frozen_expected_trajectories(self):
        for trace in load_frozen("a_traces.json"):
            with self.subTest(trace=trace["id"]):
                result = replay(trace["events"], "A2")
                for key, value in trace["expected"].items():
                    self.assertEqual(result[key], value, key)

    def test_answer_exposure_survives_attempt_reset(self):
        events = [{"type": "answer_seen", "family": "f"}, {"type": "reset_attempts"},
                  {"type": "submit", "role": "new", "correct": True, "family": "f", "reviewed": True,
                   "concept_match": True, "external_assistance": "none", "runtime_status": "ok"}]
        result = replay(events, "A2")
        self.assertEqual(result["new_success"], 0)
        self.assertEqual(result["kinds"], ["assisted_success"])

    def test_invalid_probe_never_confirms_gap(self):
        events = [{"type": "hypothesis", "id": "h", "concept": "loop_end", "program_id": "p"},
                  {"type": "probe", "hypothesis_id": "h", "correct": False, "reviewed": False}]
        self.assertEqual(replay(events, "A2")["supported_gaps"], [])

    def test_program_refutation_revokes_contextual_recommendation(self):
        events = [{"type": "program", "id": "p", "cause": "init_zero", "status": "supported"},
                  {"type": "hypothesis", "id": "h", "concept": "initialization", "program_id": "p"},
                  {"type": "probe", "hypothesis_id": "h", "correct": False, "reviewed": True},
                  {"type": "recommend", "hypothesis_id": "h"},
                  {"type": "program", "id": "p", "cause": "init_zero", "status": "refuted"}]
        result = replay(events, "A2")
        self.assertEqual(result["active_recommendations"], 0)
        self.assertEqual(result["revoked_recommendations"], 1)
        self.assertEqual(result["supported_gaps"], ["h"])  # independent probe evidence remains


if __name__ == "__main__":
    unittest.main()
