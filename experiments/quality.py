"""Independent exercise-pack checks. Gold quality labels are not consulted."""
import ast
import time
from experiments.common import valid_args, oracle, is_correct
from experiments.runner import execute, audit_source
from experiments.transforms import generic_mutants


def behavior(row):
    if row["status"] == "ok":
        return ("ok", row.get("value"))
    if row["status"] == "runtime_error":
        return ("runtime_error", row.get("error", "").split(":", 1)[0])
    return (row["status"], "infrastructure_or_limit")


def union_inputs(*groups):
    result = []
    for group in groups:
        for args in group:
            if args not in result:
                result.append(args)
    return result


class Runs:
    def __init__(self):
        self.logs = []

    def run(self, source, inputs, purpose):
        rows = execute(source, inputs)
        self.logs.append({"purpose": purpose, "source": source, "inputs": inputs, "results": rows})
        return rows

    def stats(self):
        rows = [r for log in self.logs for r in log["results"]]
        return {"process_batches": len(self.logs), "function_evaluations": len(rows),
                "infrastructure_failures": sum(r["status"] not in {"ok", "runtime_error"} for r in rows),
                "execution_log": self.logs}


def validate_pack(pack, variant):
    if variant not in {"C0", "C1", "C2", "C2_without_target"}:
        raise ValueError("unknown pack gate")
    start = time.perf_counter()
    runs = Runs()
    result = {"accepted": False, "checks": {}, "target_check": "not_checked", "mutants": []}

    def finish(accepted, reason):
        return {**result, "accepted": accepted, "reason": reason, **runs.stats(),
                "elapsed_ms": round((time.perf_counter() - start) * 1000, 3)}

    required = ["task", "statement", "reference", "starter", "tests", "witness_inputs"]
    if any(k not in pack for k in required) or not pack["tests"]:
        return finish(False, "invalid_structure")
    for source in [pack["reference"], pack["starter"]]:
        if audit_source(source):
            return finish(False, "unreviewable_source")
    tests = pack["tests"]
    if any(not valid_args(pack["task"], t.get("args"))[0] or "expected" not in t for t in tests):
        return finish(False, "invalid_test_input")
    witness = pack["witness_inputs"]
    if not witness or any(not valid_args(pack["task"], a)[0] for a in witness):
        return finish(False, "invalid_witness_input")
    test_args = [t["args"] for t in tests]
    reference = runs.run(pack["reference"], test_args, "reference_declared_tests")
    starter = runs.run(pack["starter"], test_args, "starter_declared_tests")
    if any(r["status"] not in {"ok", "runtime_error"} for r in reference + starter):
        return finish(False, "basic_execution_not_checked")
    reference_pass = all(is_correct(r, t["expected"]) for r, t in zip(reference, tests))
    starter_fail = all(not is_correct(r, t["expected"]) for r, t in zip(starter, tests))
    result["checks"].update(reference_pass=reference_pass, starter_fails_all=starter_fail)
    if not reference_pass:
        return finish(False, "basic_reference_mismatch")
    if not starter_fail:
        return finish(False, "starter_already_passes")
    if variant == "C0":
        return finish(True, "basic_checks_pass")

    reference_witness = runs.run(pack["reference"], witness, "reference_frozen_witness")
    if any(r["status"] not in {"ok", "runtime_error"} for r in reference_witness):
        return finish(False, "reference_execution_not_checked")
    if variant == "C1":
        if any(r["status"] != "ok" for r in reference_witness):
            return finish(False, "reference_runtime_failure_on_valid_witness")
        combined = union_inputs(witness, test_args)
        for index, mutation in enumerate(generic_mutants(pack["reference"])):
            rows = runs.run(mutation["source"], combined, f"generic_mutant_{index}")
            by_input = {str(r["args"]): r for r in rows}
            if any(r["status"] not in {"ok", "runtime_error"} for r in rows):
                status = "not_checked"
            else:
                non_equivalent = any(behavior(by_input[str(a)]) != behavior(ref) for a, ref in zip(witness, reference_witness))
                killed = any(not is_correct(by_input[str(t["args"])], t["expected"]) for t in tests)
                status = "killed" if non_equivalent and killed else "survived" if non_equivalent else "witness_equivalent"
            result["mutants"].append({"id": index, **mutation, "status": status})
        counts = {s: sum(m["status"] == s for m in result["mutants"]) for s in ["killed", "survived", "witness_equivalent", "not_checked"]}
        result["checks"]["generic_counts"] = counts
        target = pack.get("target_source")
        if target:
            normalized = ast.dump(ast.parse(target), include_attributes=False)
            result["checks"]["target_present_in_generic"] = any(ast.dump(ast.parse(m["source"]), include_attributes=False) == normalized for m in result["mutants"])
        if counts["not_checked"]:
            return finish(False, "generic_execution_not_checked")
        if not counts["killed"] and not counts["survived"]:
            return finish(False, "no_non_equivalent_mutant")
        return finish(not counts["survived"], "generic_mutant_survives" if counts["survived"] else "all_finite_non_equivalent_mutants_killed")

    reference_conflicts = [{"args": a, "expected": oracle(pack["task"], a), "actual": r}
                          for a, r in zip(witness, reference_witness) if not is_correct(r, oracle(pack["task"], a))]
    test_conflicts = [t for t in tests if t["expected"] != oracle(pack["task"], t["args"])]
    result["checks"].update(independent_reference_conflicts=reference_conflicts, test_expectation_conflicts=test_conflicts)
    if reference_conflicts:
        return finish(False, "independent_reference_conflict")
    if test_conflicts:
        return finish(False, "test_expectation_conflict")
    review = pack.get("rubric_review", {})
    if review.get("status") != "approved_fixture":
        return finish(False, "missing_review")
    if not pack.get("requested_concept") or not review.get("concept_match"):
        return finish(False, "off_concept")
    if variant == "C2_without_target":
        return finish(True, "independent_reference_and_review_pass; target_ablated")
    target = pack.get("target_source")
    if not target or audit_source(target):
        return finish(False, "target_not_checked")
    combined = union_inputs(witness, test_args)
    target_rows = runs.run(target, combined, "target_mutant")
    if any(r["status"] not in {"ok", "runtime_error"} for r in target_rows):
        return finish(False, "target_execution_not_checked")
    by_input = {str(r["args"]): r for r in target_rows}
    is_fault = any(not is_correct(by_input[str(a)], oracle(pack["task"], a)) for a in witness)
    killed = any(not is_correct(by_input[str(t["args"])], t["expected"]) for t in tests)
    result["target_check"] = "killed" if is_fault and killed else "survived" if is_fault else "witness_equivalent"
    if not is_fault:
        return finish(False, "target_not_a_witnessed_fault")
    return finish(killed, "target_killed" if killed else "target_survives")


def audit_pack(pack):
    """Offline measurement only; not supplied to C0/C1 decision rules."""
    runs = Runs()
    combined = union_inputs(pack["witness_inputs"], [t["args"] for t in pack["tests"]])
    refs = runs.run(pack["reference"], combined, "audit_independent_reference")
    targets = runs.run(pack["target_source"], combined, "audit_target")
    by_input = {str(r["args"]): r for r in targets}
    return {"reference_conflict": any(not is_correct(r, oracle(pack["task"], r["args"])) for r in refs),
            "test_conflict": any(t["expected"] != oracle(pack["task"], t["args"]) for t in pack["tests"]),
            "target_is_fault": any(not is_correct(by_input[str(a)], oracle(pack["task"], a)) for a in pack["witness_inputs"]),
            "target_killed_by_existing_tests": any(not is_correct(by_input[str(t["args"])], t["expected"]) for t in pack["tests"]),
            **runs.stats()}
