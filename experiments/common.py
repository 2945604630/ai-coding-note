"""Independent references, contracts, freeze verification and append-only runs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import uuid

ROOT = Path(__file__).resolve().parent


def valid_args(task, args, domain="default"):
    if not isinstance(args, list) or len(args) != 1:
        return False, "one argument required"
    value = args[0]
    if task == "inclusive_sum":
        return (type(value) is int and 0 <= value <= 8), "n must be an integer in [0,8]"
    if task not in {"max", "min", "sum_items", "copy_items"}:
        return False, "unsupported contract"
    if not isinstance(value, list) or len(value) > 8 or any(type(x) is not int or abs(x) > 20 for x in value):
        return False, "short bounded integer list required"
    if task in {"max", "min"} and not value:
        return False, "nonempty list required"
    if domain == "unknown_sign" and any(x < 0 for x in value):
        return False, "negative input eligibility not specified"
    return True, "valid"


def oracle(task, args):
    value = args[0]
    if task == "max":
        return max(value)
    if task == "min":
        return min(value)
    if task == "inclusive_sum":
        return value * (value + 1) // 2
    if task == "sum_items":
        return sum(value)
    if task == "copy_items":
        return list(value)
    raise ValueError("unsupported independent reference")


def is_correct(row, expected):
    return row["status"] == "ok" and row.get("value") == expected


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path):
    # Publication manifests use explicit repository paths, independent of cwd.
    # Absolute historical paths remain supported in local archived manifests.
    if isinstance(path, str) and path.startswith("repo://"):
        base = ROOT.parent.resolve()
        target = (base / path[len("repo://"):]).resolve()
        if not target.is_relative_to(base):
            raise ValueError("Repository manifest path escapes project")
        path = target
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_frozen(name):
    manifest = json.loads((ROOT / "data/frozen_manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["sha256"].items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"Frozen input changed: {relative}. Register a new protocol; do not silently overwrite.")
    for version in ["v2", "v3"]:
        amended = ROOT / f"data/frozen_amendment_b_{version}.json"
        if not amended.exists():
            continue
        amendment = json.loads(amended.read_text(encoding="utf-8"))
        if amendment["original_manifest_sha256"] != digest(ROOT / "data/frozen_manifest.json"):
            raise ValueError("Original frozen manifest changed")
        if "previous_amendment_sha256" in amendment and amendment["previous_amendment_sha256"] != digest(ROOT / "data/frozen_amendment_b_v2.json"):
            raise ValueError("Previous frozen amendment changed")
        for relative, expected in amendment["sha256"].items():
            if digest(ROOT / relative) != expected:
                raise ValueError(f"Frozen amendment changed: {relative}")
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def new_run(experiment):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory = ROOT / "results" / f"{experiment}_{stamp}_{uuid.uuid4().hex[:6]}"
    directory.mkdir(parents=True)
    dump(directory / "environment.json", {
        "utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
        "platform": platform.platform(), "protocol_sha256": digest(ROOT / "PROTOCOL.md"),
        "baseline_details_sha256": digest(ROOT / "BASELINE_RULES.md") if (ROOT / "BASELINE_RULES.md").exists() else None,
        "manifest_sha256": digest(ROOT / "data/frozen_manifest.json"),
        "b_amendment_manifest_sha256": digest(ROOT / "data/frozen_amendment_b_v2.json") if (ROOT / "data/frozen_amendment_b_v2.json").exists() else None,
        "b_contract_manifest_sha256": digest(ROOT / "data/frozen_amendment_b_v3.json") if (ROOT / "data/frozen_amendment_b_v3.json").exists() else None,
        "implementation_sha256": {p.name: digest(p) for p in ROOT.glob("*.py")},
        "source": "reviewed_local_fixtures", "live_model": {"status": "not_run", "reason": "no_provider_config",
            "calls": 0, "tokens": 0, "cost": 0, "cost_unit": "no_request_sent"},
    })
    return directory
