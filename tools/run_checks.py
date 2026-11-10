#!/usr/bin/env python3
"""Run a task's acceptance checks and record real output.

checks.txt, one check per line:   name | before | command
  before = fail  -> new behaviour: must FAIL before the build (proves the check can detect the work)
  before = pass  -> regression guard: must PASS before and after

Usage: run_checks.py runs/<id>/checks.txt --stage before|after [--cwd DIR] [--timeout 300] [--lock]
  --stage before  preflight: every command must be runnable and match its 'before' value
  --lock          with --stage before, after the user approved the checks at Gate 2: writes
                  checks.lock (sha256 of checks.txt). Show the hash in the gate report.
  --stage after   every command must pass, and checks.txt must still match checks.lock
Writes checks-<stage>.md beside checks.txt with command, exit code and the last 15 lines of output.
"""
import argparse, os, subprocess, sys, datetime, hashlib

ap = argparse.ArgumentParser()
ap.add_argument("checks"); ap.add_argument("--stage", choices=["before", "after"], required=True)
ap.add_argument("--cwd", default="."); ap.add_argument("--timeout", type=int, default=300)
ap.add_argument("--lock", action="store_true")
a = ap.parse_args()
run_dir = os.path.dirname(os.path.abspath(a.checks)); lock_path = os.path.join(run_dir, "checks.lock")
digest = hashlib.sha256(open(a.checks, "rb").read()).hexdigest()

rows, bad, notes = [], 0, []
if a.stage == "after":
    if not os.path.isfile(lock_path):
        notes.append("NO LOCK: checks.lock is missing, so these checks were never approved at Gate 2"); bad += 1
    elif open(lock_path).read().split()[0] != digest:
        notes.append("LOCK MISMATCH: checks.txt was changed after it was approved"); bad += 1
for raw in open(a.checks, encoding="utf-8"):
    raw = raw.strip()
    if not raw or raw.startswith("#"): continue
    parts = [p.strip() for p in raw.split("|", 2)]
    if len(parts) != 3 or parts[1] not in ("fail", "pass"):
        rows.append((raw, "-", "MALFORMED", "expected: name | fail|pass | command")); bad += 1; continue
    name, before, cmd = parts
    try:
        r = subprocess.run(cmd, shell=True, cwd=os.path.expanduser(a.cwd), capture_output=True,
                           text=True, timeout=a.timeout)
        code, out = r.returncode, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        code, out = -1, f"TIMEOUT after {a.timeout}s"
    tail = "\n".join(out.strip().splitlines()[-15:])
    if code in (126, 127) or code == -1:
        verdict = "NOT RUNNABLE"; bad += 1
    elif a.stage == "before":
        ok = (code == 0) == (before == "pass")
        verdict = ("OK " if ok else "WRONG ") + ("passes" if code == 0 else "fails") + f" (expected to {before})"
        bad += 0 if ok else 1
    else:
        verdict = "PASS" if code == 0 else "FAIL"; bad += 0 if code == 0 else 1
    rows.append((name, cmd, f"{verdict} [exit {code}]", tail))
if not rows:
    notes.append("NO CHECKS: checks.txt is empty"); bad += 1

overall = "FAIL" if bad else "PASS"
out_path = os.path.join(run_dir, f"checks-{a.stage}.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"# Checks, stage: {a.stage} — {datetime.datetime.now():%Y-%m-%d %H:%M}\n\n")
    f.write(f"Overall: {overall} ({len(rows)} checks, {bad} not as required) | checks.txt sha256 {digest[:12]}\n\n")
    for nline in notes: f.write(nline + "\n\n")
    for name, cmd, verdict, tail in rows:
        f.write(f"## {name}: {verdict}\n\n$ {cmd}\n\n```\n{tail}\n```\n\n")
for nline in notes: print(nline)
for name, cmd, verdict, _ in rows: print(f"{verdict:45} {name}")
if a.stage == "before" and a.lock:
    if bad: print("not locked: preflight did not pass")
    else:
        open(lock_path, "w").write(f"{digest}  checks.txt\n"); print(f"locked: sha256 {digest[:12]} -> checks.lock")
print(f"run_checks ({a.stage}): {overall} ({len(rows)} checks, {bad} not as required) -> checks-{a.stage}.md")
sys.exit(1 if bad else 0)
