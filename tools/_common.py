"""Shared helpers for Factory check scripts. Standard library only."""
import os, re, subprocess, sys

def expand(p):
    return os.path.abspath(os.path.expanduser(p))

def parse_roots(args_roots, text=""):
    """Roots map an alias to a folder: ALIAS=/abs/path. Also read from a
    '<!-- roots: A=/x; B=/y -->' comment inside the checked file."""
    roots = {}
    m = re.search(r"<!--\s*roots:\s*(.*?)-->", text, re.S)
    pairs = [s.strip() for s in m.group(1).split(";")] if m else []
    for pair in pairs + list(args_roots or []):
        if "=" in pair:
            k, v = pair.split("=", 1)
            roots[k.strip()] = expand(v.strip())
    return roots

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                       env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    return r.returncode, r.stdout

def finish(name, failures, checked, warnings=()):
    for w in warnings:
        print("WARN  " + w)
    for f in failures:
        print("FAIL  " + f)
    status = "FAIL" if failures else "PASS"
    print(f"{name}: {status} ({checked} checked, {len(failures)} failed, {len(warnings)} warnings)")
    sys.exit(1 if failures else 0)
