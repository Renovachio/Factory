#!/usr/bin/env python3
"""Report how the Factory is performing, computed from files the roles cannot simply assert.

Per run folder (EXAMPLE-* is skipped):
  size, pack           from the header line of brief.md
  verified first time  verify-1.md starts with 'Verdict: PASS' and checks-after.md says 'Overall: PASS'
  fix rounds           number of verify-<n>.md files minus one
  user corrections     rows in gates.csv whose decision is 'change'
  delivered            gates.csv has a G4 row with decision 'approve'
gates.csv holds the user's own words per gate: gate,date,decision,user_words
A clean run = delivered, verified first time, no user corrections, no defect logged for it.

Usage: scorecard.py [--runs /path/to/Factory/runs]
"""
import argparse, csv, glob, os, re, collections

ap = argparse.ArgumentParser()
ap.add_argument("--runs", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs"))
a = ap.parse_args()
def read(p): return open(p, encoding="utf-8").read() if os.path.isfile(p) else ""
defects = list(csv.DictReader(open(os.path.join(a.runs, "defects.csv"), encoding="utf-8"))) if os.path.isfile(os.path.join(a.runs, "defects.csv")) else []
tasks = []
for d in sorted(glob.glob(os.path.join(a.runs, "*", ""))):
    name = os.path.basename(d.rstrip("/"))
    if name.startswith("EXAMPLE") or not os.path.isfile(os.path.join(d, "brief.md")): continue
    brief = read(os.path.join(d, "brief.md"))
    g = lambda k: (re.search(rf"\b{k}:\s*([\w-]+)", brief) or [None, "?"])[1]
    gates = list(csv.DictReader(open(os.path.join(d, "gates.csv"), encoding="utf-8"))) if os.path.isfile(os.path.join(d, "gates.csv")) else []
    verifies = glob.glob(os.path.join(d, "verify-*.md"))
    first = read(os.path.join(d, "verify-1.md")).lstrip().startswith("Verdict: PASS") and "Overall: PASS" in read(os.path.join(d, "checks-after.md"))
    t = dict(task=name, size=g("size"), pack=g("pack"), first=first, fix=max(0, len(verifies) - 1),
             corrections=sum(1 for r in gates if r["decision"].strip() == "change"),
             delivered=any(r["gate"].strip() == "G4" and r["decision"].strip() == "approve" for r in gates),
             defects=sum(1 for r in defects if r["task"] == name))
    t["clean"] = t["delivered"] and t["first"] and t["corrections"] == 0 and t["defects"] == 0
    tasks.append(t)
n = len(tasks); done = [t for t in tasks if t["delivered"]]
print(f"Tasks: {n} | delivered: {len(done)}")
if done:
    print(f"Verified first time: {sum(t['first'] for t in done)}/{len(done)}")
    print(f"Fix rounds: {sum(t['fix'] for t in done)} | user corrections: {sum(t['corrections'] for t in done)}")
    clean = collections.Counter(t["pack"] for t in done if t["clean"])
    print("Clean runs per pack: " + (", ".join(f"{k}={v}" for k, v in clean.items()) or "none"))
for t in tasks:
    print(f"  {t['task']}: size {t['size']}, pack {t['pack']}, first-pass {'yes' if t['first'] else 'no'}, "
          f"fix rounds {t['fix']}, corrections {t['corrections']}, defects {t['defects']}, {'delivered' if t['delivered'] else 'open'}")
print(f"Defects logged: {len(defects)}")
for k, v in collections.Counter(r["category"] for r in defects).most_common(): print(f"  {k}: {v}")
open_ = [r for r in defects if not r.get("new_check_or_rule", "").strip()]
print(f"Defects with no check or rule added yet: {len(open_)}")
for r in open_: print(f"  {r['date']} {r['task']}: {r['description']}")
