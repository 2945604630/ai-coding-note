"""Run reviewed single functions only. This is not a hostile-code sandbox."""
import ast
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

BUILTINS = {"range", "len", "max", "min", "sum", "list", "abs", "enumerate"}
ALLOWED = {
    "Module", "FunctionDef", "arguments", "arg", "Return", "Assign", "AugAssign",
    "For", "While", "If", "Expr", "Pass", "Break", "Continue", "Name", "Load",
    "Store", "Constant", "BinOp", "UnaryOp", "Compare", "BoolOp", "Call", "List",
    "Tuple", "Subscript", "Slice", "ListComp", "comprehension", "IfExp", "Add",
    "Sub", "Mult", "FloorDiv", "Mod", "USub", "UAdd", "Not", "Eq", "NotEq",
    "Lt", "LtE", "Gt", "GtE", "And", "Or", "Attribute", "keyword",
}


def audit_source(source):
    if not isinstance(source, str) or len(source) > 4096:
        return "source length/type"
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return f"syntax: {exc.msg}"
    nodes = list(ast.walk(tree))
    if len(nodes) > 512:
        return "AST budget"
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        return "exactly one function required"
    fn = tree.body[0]
    if fn.name != "solve" or fn.decorator_list or fn.returns or fn.args.defaults or fn.args.kw_defaults:
        return "plain solve function required"
    for node in nodes:
        if type(node).__name__ not in ALLOWED:
            return f"node forbidden: {type(node).__name__}"
        if isinstance(node, (ast.Name, ast.arg)) and (getattr(node, "id", getattr(node, "arg", "")).startswith("_")):
            return "private names forbidden"
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, bool, type(None))) or (type(node.value) is int and abs(node.value) > 1024):
                return "literal forbidden"
        if isinstance(node, ast.Attribute) and node.attr != "append":
            return "attribute forbidden"
        if isinstance(node, ast.Call):
            normal = isinstance(node.func, ast.Name) and node.func.id in BUILTINS
            append = isinstance(node.func, ast.Attribute) and node.func.attr == "append" and isinstance(node.func.value, ast.Name)
            if not (normal or append) or node.keywords:
                return "call forbidden"
    return None


def source_hash(source):
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _windows_job(process, memory_bytes):
    from ctypes import wintypes
    size = ctypes.c_size_t

    class Basic(ctypes.Structure):
        _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                    ("flags", wintypes.DWORD), ("min_working", size), ("max_working", size),
                    ("active", wintypes.DWORD), ("affinity", size),
                    ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]

    class IO(ctypes.Structure):
        _fields_ = [(n, ctypes.c_uint64) for n in ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

    class Extended(ctypes.Structure):
        _fields_ = [("basic", Basic), ("io", IO), ("process_memory", size),
                    ("job_memory", size), ("peak_process", size), ("peak_job", size)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.CreateJobObjectW(None, None)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    info = Extended()
    info.basic.flags = 0x100 | 0x8 | 0x2000  # process memory, active processes, kill on close
    info.basic.active = 1
    info.process_memory = memory_bytes
    if not kernel.SetInformationJobObject(handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
        error = ctypes.WinError(ctypes.get_last_error())
        kernel.CloseHandle(handle)
        raise error
    if not kernel.AssignProcessToJobObject(handle, int(process._handle)):
        error = ctypes.WinError(ctypes.get_last_error())
        kernel.CloseHandle(handle)
        raise error
    return lambda: kernel.CloseHandle(handle)


def execute(source, args_list, timeout=1.5, output_limit=8192):
    """Fresh namespace per case, bounded subprocess per batch; capture real results."""
    started = time.perf_counter()
    limits = {"timeout_s": timeout, "output_bytes": output_limit, "memory_bytes": 128 * 1024 * 1024,
              "memory_enforced": False, "max_processes": None}
    base = {"code_hash": source_hash(source), "runtime": sys.version.split()[0]}

    def failure(status, error):
        return [{**base, "args": args, "status": status, "error": error,
                 "limits": dict(limits), "batch_elapsed_ms": round((time.perf_counter() - started) * 1000, 3)}
                for args in args_list]

    issue = audit_source(source)
    if issue:
        return failure("rejected_source", issue)
    payload = json.dumps({"source": source, "args_list": args_list, "output_limit": output_limit,
                          "memory_bytes": limits["memory_bytes"]}).encode()
    worker = Path(__file__).with_name("worker.py")
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    close_job = lambda: None
    process = subprocess.Popen([sys.executable, "-I", "-S", str(worker)], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
    try:
        if os.name == "nt":
            close_job = _windows_job(process, limits["memory_bytes"])
            limits.update(memory_enforced=True, max_processes=1)
        else:
            limits["memory_enforced"] = True  # trusted worker sets RLIMIT_AS before functions
        stdout, stderr = process.communicate(payload, timeout=timeout)
        if process.returncode != 0:
            return failure("environment_error", stderr.decode("utf-8", errors="replace")[:4096] or f"exit={process.returncode}")
        if len(stdout) > max(32768, len(args_list) * (output_limit + 1024)):
            return failure("output_limit", "worker packet too large")
        data = json.loads(stdout)
        return [{**base, **row, "limits": dict(limits),
                 "batch_elapsed_ms": round((time.perf_counter() - started) * 1000, 3)} for row in data]
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return failure("timeout", "wall-clock deadline")
    except Exception as exc:
        if process.poll() is None:
            process.kill()
            process.communicate()
        return failure("environment_error", f"{type(exc).__name__}: {exc}")
    finally:
        close_job()

