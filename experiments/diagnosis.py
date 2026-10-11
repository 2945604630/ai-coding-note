"""Evidence validation. Ground-truth labels are not read by this module."""
import time
from experiments.common import oracle, valid_args, is_correct
from experiments.runner import execute, source_hash
from experiments.transforms import intervention


def collect_evidence(case):
    results = execute(case["source"], case["inputs"])
    evidence = {}
    for i, row in enumerate(results):
        valid, reason = valid_args(case["task"], row["args"], case.get("domain", "default"))
        expected = oracle(case["task"], row["args"]) if valid else None
        evidence[f"e{i}"] = {**row, "input_valid": valid, "input_reason": reason,
                              "expected": expected, "passed": valid and is_correct(row, expected)}
    return evidence


def reference_issue(case, evidence, claim):
    refs = claim.get("evidence_ids")
    if not isinstance(refs, list) or not refs or any(ref not in evidence for ref in refs):
        return "invalid_reference"
    if claim.get("code_hash") != source_hash(case["source"]) or any(evidence[r]["code_hash"] != claim.get("code_hash") for r in refs):
        return "stale"
    if any(not evidence[r]["input_valid"] or evidence[r]["status"] not in {"ok", "runtime_error"} for r in refs):
        return "unusable_evidence"
    return None


def verify_claim(case, evidence, claim, variant):
    started = time.perf_counter()
    result = {"cause": claim.get("cause"), "scope": claim.get("scope"), "status": None,
              "prediction_verified": False, "cause_supported": False, "extra_executions": 0, "extra_processes": 0}

    def finish(status, reason):
        result.update(status=status, reason=reason, elapsed_ms=round((time.perf_counter() - started) * 1000, 3))
        return result

    if variant == "B0":
        return finish("accepted_unverified", "fixed free-analysis candidate; no verifier")
    if not all(k in claim for k in ["cause", "scope", "evidence_ids", "code_hash"]):
        return finish("invalid_structure", "missing structured fields")
    issue = reference_issue(case, evidence, claim)
    if issue:
        return finish(issue, "citation or version check")
    usable = [r for r in evidence.values() if r["input_valid"] and r["status"] in {"ok", "runtime_error"}]
    failed = any(not r["passed"] for r in usable)
    if variant == "B1":
        return finish("accepted_unverified" if failed else "inconclusive", "facts constrain failure verdict, not cause")
    if variant != "B2":
        raise ValueError("unknown variant")
    if claim["scope"] != "program":
        return finish("inconclusive", "program behavior does not verify learner understanding")
    valid, reason = valid_args(case["task"], claim.get("probe_args"), case.get("domain", "default"))
    if not valid:
        return finish("invalid_probe", reason)
    prediction = claim.get("predicted")
    if not isinstance(prediction, dict) or prediction.get("status") not in {"ok", "runtime_error"}:
        return finish("inconclusive", "no supported behavior prediction")
    probe = execute(case["source"], [claim["probe_args"]])[0]
    result.update(probe=probe, extra_executions=1, extra_processes=1)
    if probe["status"] not in {"ok", "runtime_error"}:
        return finish("inconclusive", "probe infrastructure/limit failure")
    matches = probe["status"] == prediction["status"]
    if prediction["status"] == "ok":
        matches = matches and probe.get("value") == prediction.get("value")
    elif prediction.get("error_type"):
        matches = matches and probe.get("error", "").startswith(prediction["error_type"] + ":")
    if not matches:
        return finish("refuted", "real program behavior contradicts the hypothesis prediction")
    result["prediction_verified"] = True
    changed = intervention(case["source"], claim["cause"])
    if changed is None:
        return finish("inconclusive", "matching symptoms without a supported local mechanism")
    args = [r["args"] for r in usable]
    before = list(usable)
    if claim["probe_args"] not in args:
        args.append(claim["probe_args"])
        before.append({**probe, "passed": is_correct(probe, oracle(case["task"], claim["probe_args"]))})
    after = execute(changed, args)
    result.update(intervention_source=changed, intervention_results=after)
    result["extra_processes"] += 1
    result["extra_executions"] += len(args)
    if any(r["status"] not in {"ok", "runtime_error"} for r in after):
        return finish("inconclusive", "intervention could not be evaluated")
    after_pass = [is_correct(r, oracle(case["task"], r["args"])) for r in after]
    improved = sum(not b["passed"] and p for b, p in zip(before, after_pass))
    regressed = sum(b["passed"] and not p for b, p in zip(before, after_pass))
    result.update(improved_cases=improved, regressed_cases=regressed)
    if improved and not regressed:
        result["cause_supported"] = True
        return finish("supported_local", "single local intervention fixes observed failures without observed regression")
    return finish("inconclusive", "intervention is masked, unnecessary, or regresses tested behavior")
