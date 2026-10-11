"""Post-hoc label scoring; intentionally separate from diagnosis verification."""
from collections import Counter

ACCEPTED = {"accepted_unverified", "supported_local"}


def summarize(cases, rows):
    by_id = {c["id"]: c for c in cases}
    accepted = [r for r in rows if r["status"] in ACCEPTED]
    true = [r for r in accepted if r["scope"] == "program" and r["cause"] in by_id[r["case_id"]]["gold_causes"]]
    false = [r for r in accepted if r["scope"] == "program" and not by_id[r["case_id"]]["unclear"]
             and r["cause"] not in by_id[r["case_id"]]["gold_causes"]]
    correct_ids = {c["id"] for c in cases if not c["gold_causes"] and not c["unclear"]}
    return {
        "programs": len(cases), "claims": len(rows), "buggy_cases": sum(bool(c["gold_causes"]) for c in cases),
        "gold_causes": sum(len(c["gold_causes"]) for c in cases), "correct_programs": len(correct_ids),
        "accepted": len(accepted), "accepted_true_causes": len(true), "accepted_false_causes": len(false),
        "unsupported_learner_assertions": sum(r["scope"] != "program" for r in accepted),
        "accepted_unassessable_claims": sum(by_id[r["case_id"]]["unclear"] for r in accepted),
        "covered_buggy_cases": len({r["case_id"] for r in true}),
        "covered_gold_causes": len({(r["case_id"], r["cause"]) for r in true}),
        "false_positive_correct_programs": len({r["case_id"] for r in false if r["case_id"] in correct_ids}),
        "withheld": len(rows) - len(accepted), "status_counts": dict(Counter(r["status"] for r in rows)),
        "injected_reference_issues": dict(Counter(r["reference_issue"] for r in rows if r["reference_issue"])),
        "reference_issues_still_accepted": sum(bool(r["reference_issue"]) for r in accepted),
        "verified_predictions": sum(r["prediction_verified"] for r in rows),
        "prediction_verified_but_cause_not_supported": sum(r["prediction_verified"] and r["status"] != "supported_local" for r in rows),
        "valid_counterexamples": sum(r["status"] == "refuted" for r in rows),
        "extra_executions": sum(r["extra_executions"] for r in rows),
        "extra_processes": sum(r["extra_processes"] for r in rows),
        "verifier_ms": round(sum(r["elapsed_ms"] for r in rows), 3),
        "model_calls": 0, "model_status": "not_run", "trial_type": "fixed_output_fault_injection",
    }
