"""Small event state machine. No claims about actual learning gains."""
from copy import deepcopy

CAUSE_TO_CONCEPT = {"init_zero": "initialization", "loop_end_excluded": "loop_end",
                    "accumulator_overwrite": "accumulation", "index_off_by_one": "index_boundary"}


def replay(events, variant="A2"):
    if variant not in {"A0", "A1", "A2"}:
        raise ValueError("unknown state rule")
    programs, gaps, recommendations = {}, {}, []
    exposure, attempted = set(), set()
    hint_count, blocked, revoked = 0, 0, 0
    performances, positive, history = [], [], []

    def revoke(hid):
        nonlocal revoked
        for rec in recommendations:
            if rec["hypothesis_id"] == hid and rec["status"] == "active":
                rec["status"] = "revoked"
                revoked += 1

    def snapshot():
        return {"programs": deepcopy(programs), "gaps": deepcopy(gaps),
                "recommendations": deepcopy(recommendations), "performances": deepcopy(performances),
                "positive_updates": list(positive), "answer_or_assistance_families": sorted(exposure)}

    for index, event in enumerate(events):
        kind = event["type"]
        if kind == "program":
            programs[event["id"]] = {"cause": event["cause"], "status": event["status"]}
            if variant == "A2" and event["status"] == "refuted":
                for hid, gap in gaps.items():
                    if gap["program_id"] == event["id"]:
                        revoke(hid)
        elif kind == "hypothesis":
            program = programs.get(event["program_id"], {})
            status = "supported" if variant == "A1" and program.get("status") == "supported" else "pending"
            if variant != "A0":
                concept = CAUSE_TO_CONCEPT.get(program.get("cause"), event["concept"]) if variant == "A1" else event["concept"]
                gaps[event["id"]] = {"concept": concept, "program_id": event["program_id"],
                                      "status": status, "evidence": ["fixed_program_tag"] if status == "supported" else []}
        elif kind == "probe" and variant == "A2":
            gap = gaps.get(event["hypothesis_id"])
            if gap and event.get("reviewed") and event.get("external_assistance", "none") == "none":
                gap["evidence"].append({"event_index": index, "correct": event["correct"], "type": "reviewed_probe"})
                if not event["correct"]:
                    gap["status"] = "supported"
                elif gap["status"] == "supported":
                    gap["status"] = "withdrawn"
                    revoke(event["hypothesis_id"])
        elif kind == "recommend":
            hid = event["hypothesis_id"]
            gap = gaps.get(hid)
            if gap and gap["status"] == "supported":
                recommendations.append({"hypothesis_id": hid, "status": "active", "event_index": index,
                                        "program_id": gap["program_id"]})
            else:
                blocked += 1
        elif kind == "withdraw" and variant == "A2":
            gap = gaps.get(event["hypothesis_id"])
            if gap:
                gap.update(status="withdrawn", withdrawal_reason=event.get("reason", "explicit withdrawal"))
                revoke(event["hypothesis_id"])
        elif kind in {"ai_patch", "answer_seen", "hint"}:
            exposure.add(event["family"])
            hint_count += 1
        elif kind == "self_rating" and variant == "A0" and event.get("rating", 0) >= 4:
            positive.append(index)
        elif kind == "reset_attempts":
            pass
        elif kind == "submit":
            family, correct = event["family"], event["correct"]
            if variant == "A0":
                performance = "legacy_positive" if correct and event["role"] == "original" else "legacy_no_update"
                if performance == "legacy_positive":
                    positive.append(index)
            elif variant == "A1":
                score = max(0, 100 - 3 * hint_count) if correct else 0
                performance = "legacy_positive" if correct and score >= 80 else "legacy_no_update"
                if performance == "legacy_positive":
                    positive.append(index)
            else:
                runtime = event.get("runtime_status")
                external = event.get("external_assistance", "unknown")
                if runtime not in {"ok", "runtime_error"}:
                    performance = "environment_failure"
                elif not event.get("reviewed") or not event.get("concept_match"):
                    performance = "invalid_assessment"
                elif external == "unknown":
                    performance = "independence_unknown"
                elif external != "none" or family in exposure:
                    performance = "assisted_success" if correct else "assisted_failure"
                elif event["role"] == "new" and family in attempted:
                    performance = "repeated_new_attempt"
                elif event["role"] == "new":
                    performance = "new_independent_success" if correct else "new_failure"
                else:
                    performance = "original_independent_success" if correct else "original_failure"
                if performance in {"new_independent_success", "original_independent_success"}:
                    positive.append(index)
            performances.append({"event_index": index, "kind": performance, "family": family,
                                 "role": event["role"], "correct": correct})
            attempted.add(family)
        history.append({"event_index": index, "event": deepcopy(event), "state": snapshot()})
    result = snapshot()
    result.update(supported_gaps=sorted(h for h, gap in gaps.items() if gap["status"] == "supported"),
                  withdrawn=sorted(h for h, gap in gaps.items() if gap["status"] == "withdrawn"),
                  program_causes=[p["cause"] for p in programs.values()],
                  kinds=[p["kind"] for p in performances],
                  new_success=sum(p["kind"] == "new_independent_success" for p in performances),
                  active_recommendations=sum(r["status"] == "active" for r in recommendations),
                  revoked_recommendations=revoked, blocked_recommendations=blocked,
                  hint_count=hint_count, history=history)
    return result
