#!/usr/bin/env python3
"""Verify that the working tree changed only what the approved plan allows.

Usage: check_scope.py --repo /path/to/repo (--plan runs/<id>/plan.md | --allow FILE) [--base REF]
  --plan   reads the allowed paths from the plan's 'Files out' column (backticked paths). Preferred.
  --allow  one path or glob per line. Catch-all globs are rejected.
Reports every changed, added, deleted or untracked path that is not allowed, and anything that
looks like a secret or local config regardless of the list.
"""
import argparse, fnmatch, re
from _common import expand, git, finish

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True); ap.add_argument("--allow"); ap.add_argument("--plan")
ap.add_argument("--base", default=None, help="also include commits since this ref")
a = ap.parse_args()
repo = expand(a.repo)
failures, allow = [], []
if a.plan:
    col = None
    for line in open(a.plan, encoding="utf-8"):
        if not line.lstrip().startswith("|"): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if col is None:
            for i, c in enumerate(cells):
                if c.lower().startswith("files out"): col = i
            continue
        if col < len(cells): allow += re.findall(r"`([^`]+)`", cells[col])
elif a.allow:
    allow = [l.strip() for l in open(a.allow, encoding="utf-8") if l.strip() and not l.startswith("#")]
if not allow:
    finish("check_scope", ["no allowed paths found (give --plan with a 'Files out' column, or --allow)"], 0)
for g in allow:
    if len(re.sub(r"[*?/.\[\]]", "", g)) < 3 or g.startswith("*"):
        failures.append(f"allow entry '{g}' matches too much; name the folder or file")
FORBIDDEN = [r"\.env$", r"\.local\.json$", r"(^|/)id_[a-z0-9]+$", r"\.pem$", r"\.key$"]

paths = set()
rc, out = git(["status", "--porcelain", "--untracked-files=all"], repo)
if rc != 0:
    finish("check_scope", [f"{repo} is not a git repository"], 0)
for l in out.splitlines():
    paths.add(l[3:].split(" -> ")[-1].strip().strip('"'))
if a.base:
    rc, out = git(["diff", "--name-only", a.base + "...HEAD"], repo)
    paths.update(x for x in out.splitlines() if x)
for p in sorted(paths):
    if any(re.search(f, p) for f in FORBIDDEN):
        failures.append(f"{p} -> secret or local config, must never be changed or staged"); continue
    if not any(p == g or fnmatch.fnmatch(p, g) or p.startswith(g.rstrip("/") + "/") for g in allow):
        failures.append(f"{p} -> changed but not in the approved plan")
finish("check_scope", failures, len(paths))
