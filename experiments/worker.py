"""Trusted worker bootstrap, never a provider-generated script."""
import json
import os
import sys
import time

payload = json.load(sys.stdin)
if os.name != "nt":
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (payload["memory_bytes"], payload["memory_bytes"]))
allowed = {"range": range, "len": len, "max": max, "min": min, "sum": sum,
           "list": list, "abs": abs, "enumerate": enumerate}
rows = []
for args in payload["args_list"]:
    original = json.loads(json.dumps(args))
    namespace = {"__builtins__": allowed}
    started = time.perf_counter()
    try:
        exec(compile(payload["source"], "<reviewed-fixture>", "exec"), namespace)
        value = namespace["solve"](*args)
        encoded = json.dumps(value, allow_nan=False)
        if len(encoded.encode()) > payload["output_limit"]:
            row = {"args": original, "status": "output_limit", "error": "value exceeds JSON limit"}
        else:
            row = {"args": original, "status": "ok", "value": value}
    except MemoryError as exc:
        row = {"args": original, "status": "resource_limit", "error": f"MemoryError: {exc}"[:1024]}
    except Exception as exc:
        row = {"args": original, "status": "runtime_error", "error": f"{type(exc).__name__}: {exc}"[:1024]}
    row["function_elapsed_ms"] = round((time.perf_counter() - started) * 1000, 4)
    rows.append(row)
json.dump(rows, sys.stdout, allow_nan=False)
