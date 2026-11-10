#!/usr/bin/env python3
"""Lint a Builder handoff against the files around it.

Fails unless: the sections exist; a 'done' handoff has a real checks-after.md beside it whose
overall result is PASS; and (with --repo) that file is newer than every changed file, so the
checks were run after the last edit. Hedged wording is reported as a warning only.

Usage: check_handoff.py runs/<id>/handoff-<n>.md [--repo /path/to/changed/repo] [--max-words 200]
"""
import argparse, os, re
from _common import expand, git, finish

ap = argparse.ArgumentParser(); ap.add_argument("file")
ap.add_argument("--repo"); ap.add_argument("--max-words", type=int, default=200)
a = ap.parse_args()
text = open(a.file, encoding="utf-8").read()
run_dir = os.path.dirname(os.path.abspath(a.file))
failures, warnings = [], []
for section in ["Result:", "Changed or produced", "Checks", "UNVERIFIED:", "NOT RUN", "Questions for the user:"]:
    if section not in text: failures.append(f"missing section '{section}'")
result = (re.search(r"Result:\s*(\w+)", text) or [None, ""])[1].lower()
if result not in ("done", "blocked", "partial"):
    failures.append("Result must be done, blocked or partial")
after = os.path.join(run_dir, "checks-after.md")
if result == "done":
    if not os.path.isfile(after):
        failures.append("Result is 'done' but there is no checks-after.md beside the handoff (run tools/run_checks.py --stage after)")
    else:
        body = open(after, encoding="utf-8").read()
        if "Overall: PASS" not in body:
            failures.append("checks-after.md does not say 'Overall: PASS'")
        if a.repo:
            repo = expand(a.repo); t = os.path.getmtime(after)
            rc, out = git(["status", "--porcelain", "--untracked-files=all"], repo)
            for l in out.splitlines():
                p = os.path.join(repo, l[3:].split(" -> ")[-1].strip().strip('"'))
                if os.path.isfile(p) and os.path.getmtime(p) > t:
                    failures.append(f"{l[3:]} was edited after the checks were run; run them again")
        else:
            warnings.append("no --repo given: could not confirm the checks ran after the last edit")
prose = re.sub(r"```.*?```", "", text, flags=re.S)
for m in re.finditer(r"\b(should|ought to|probably|presumably|confident|I (believe|assume|think)|seems? to)\b", prose, re.I):
    warnings.append(f"hedged wording '{m.group(0)}': if it is not proven by the checks, it belongs under UNVERIFIED")
if len(prose.split()) > a.max_words:
    warnings.append(f"{len(prose.split())} words of prose (limit {a.max_words})")
finish("check_handoff", failures, 1, warnings)
