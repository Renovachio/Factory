#!/usr/bin/env python3
"""Tests for the Factory check scripts. Each case is an attempt to get bad work past a check
(must FAIL) or a correct piece of work (must PASS). Run after any change to tools/:

    python3 tools/tests/run_tests.py
"""
import os, shutil, subprocess, sys, tempfile, time

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = tempfile.mkdtemp(prefix="factory-tests-")
results = []

def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "w", encoding="utf-8").write(text); return path
def sh(cmd, cwd):
    subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True)
def run(script, *args, tools=TOOLS):
    r = subprocess.run([sys.executable, os.path.join(tools, script)] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr
def case(name, want_pass, code_out, needle=None):
    code, out = code_out
    ok = (code == 0) == want_pass and (needle is None or needle in out)
    results.append(ok); print(("ok   " if ok else "BAD  ") + name + ("" if ok else "\n" + out))

# ---------- fixtures
src = os.path.join(T, "src"); w(os.path.join(src, "config.txt"), "name=demo\nconfig/features=PackedStringArray(\"4.7\")\nmode=fast\n")
R = f"<!-- roots: S={src} -->\n"
good = 'F1. Version is 4.7 — `S/config.txt:2` > "config/features=PackedStringArray(\\"4.7\\")"\n'

# ---------- check_citations
c = "check_citations.py"
case("citations: correct fact sheet passes strict", True, run(c, "--strict", w(f"{T}/c1.md", R + "# Facts\n" + good + "\n## NOT FOUND\n- nothing else\n")))
case("citations: uncited statement fails strict", False, run(c, "--strict", w(f"{T}/c2.md", R + good + "The engine exposes Shop.EvtInvented() and RTP is 96.2%.\n")), "outside a claim line")
case("citations: claim line without citation fails strict", False, run(c, "--strict", w(f"{T}/c3.md", R + "F1. RTP is 96.2%.\n")), "no quoted citation")
case("citations: UNVERIFIED label is accepted", True, run(c, "--strict", w(f"{T}/c4.md", R + "F1. UNVERIFIED: RTP is 96.2%.\n")))
case("citations: path:line without alias fails", False, run(c, w(f"{T}/c5.md", R + "See scripts/foo/nope.gd:12 for details.\n")), "no alias")
case("citations: trivial quote fails", False, run(c, w(f"{T}/c6.md", R + 'F1. x — `S/config.txt:2` > "="\n')), "too short")
case("citations: wrong line fails", False, run(c, w(f"{T}/c7.md", R + "F1. x — `S/config.txt:99`\n")), "file has")
case("citations: quote not at that line fails", False, run(c, w(f"{T}/c8.md", R + 'F1. x — `S/config.txt:2` > "config/features=PackedStringArray(\\"4.6\\")"\n')), "quote not found")
case("citations: missing file fails", False, run(c, w(f"{T}/c9.md", R + "F1. x — `S/nope.txt:1`\n")), "does not exist")

# ---------- run_checks (lock)
k = "run_checks.py"; rd = os.path.join(T, "run"); flag = os.path.join(T, "built.flag")
w(f"{rd}/checks.txt", f"built | fail | test -f {flag}\n")
case("checks: after-stage without a lock fails", False, run(k, f"{rd}/checks.txt", "--stage", "after"), "NO LOCK")
case("checks: preflight passes and locks", True, run(k, f"{rd}/checks.txt", "--stage", "before", "--lock"), "locked")
open(flag, "w").close()
case("checks: after-stage passes with lock intact", True, run(k, f"{rd}/checks.txt", "--stage", "after"))
w(f"{rd}/checks.txt", "built | fail | true\n")
case("checks: checks edited after approval fail", False, run(k, f"{rd}/checks.txt", "--stage", "after"), "LOCK MISMATCH")
w(f"{T}/run2/checks.txt", "already | fail | true\n")
case("checks: a 'new behaviour' check that already passes fails preflight", False, run(k, f"{T}/run2/checks.txt", "--stage", "before"), "WRONG")
w(f"{T}/run3/checks.txt", "tool | pass | definitely_not_a_command_xyz\n")
case("checks: command that cannot run fails preflight", False, run(k, f"{T}/run3/checks.txt", "--stage", "before"), "NOT RUNNABLE")

# ---------- repo fixture
repo = os.path.join(T, "repo"); os.makedirs(repo)
w(f"{repo}/a.gd", "class_name Shop\nfunc EvtShopOpened():\n\tpass\nfunc start():\n\tpass\n")
w(f"{repo}/w.gd", "class_name Wallet\nfunc EvtBalanceChanged():\n\tpass\n")
w(f"{repo}/use.gd", "func boot():\n\tShop.start()\n\tBus.listen(Wallet.EvtBalanceChanged(), boot)\n")
sh("git init -q && git add -A && git -c user.email=t@t -c user.name=t commit -qm base", repo)

# ---------- check_identifiers
i = "check_identifiers.py"
w(f"{repo}/new.gd", "func go():\n\tShop.start()\n\tBus.listen(Wallet.EvtBalanceChanged(), go)\n")
case("identifiers: change using only known names passes", True, run(i, "--repo", repo))
w(f"{repo}/new.gd", "func go():\n\tWallet.EvtShopOpened()\n")
case("identifiers: real member on the wrong class fails", False, run(i, "--repo", repo), "Wallet.EvtShopOpened")
w(f"{repo}/new.gd", "func go():\n\tShop.call(\"totally_invented_method\")\n")
case("identifiers: invented name hidden in a string fails", False, run(i, "--repo", repo), "totally_invented_method")
w(f"{repo}/new.gd", "func go():\n\tInventedService.do_magic()\n")
case("identifiers: invented class fails", False, run(i, "--repo", repo), "InventedService")
os.remove(f"{repo}/new.gd")

# ---------- check_scope
s = "check_scope.py"
plan = w(f"{T}/plan.md", "| # | Work order | Files out (max 3) | Turns green |\n|---|---|---|---|\n| 1 | add feature | `feature/new.gd` | built |\n")
w(f"{repo}/feature/new.gd", "func x():\n\tpass\n")
case("scope: planned file passes", True, run(s, "--repo", repo, "--plan", plan))
w(f"{repo}/other.gd", "func y():\n\tpass\n")
case("scope: unplanned file fails", False, run(s, "--repo", repo, "--plan", plan), "other.gd")
case("scope: catch-all allow list fails", False, run(s, "--repo", repo, "--allow", w(f"{T}/allow.txt", "*\n")), "matches too much")
os.remove(f"{repo}/other.gd"); w(f"{repo}/feature/.env", "SECRET=1\n")
case("scope: secret file fails even inside a planned folder", False, run(s, "--repo", repo, "--allow", w(f"{T}/allow2.txt", "feature/\n")), "secret")
os.remove(f"{repo}/feature/.env")

# ---------- check_handoff
h = "check_handoff.py"; hd = os.path.join(T, "hand")
body = "Result: done\nChanged or produced (paths): feature/new.gd\nChecks: see checks-after.md\nUNVERIFIED: none\nNOT RUN (and why): none\nQuestions for the user: none\n"
w(f"{hd}/handoff-1.md", body)
case("handoff: 'done' with no checks file fails", False, run(h, f"{hd}/handoff-1.md"), "no checks-after.md")
w(f"{hd}/checks-after.md", "Overall: FAIL (1 checks, 1 not as required)\n")
case("handoff: 'done' with failing checks fails", False, run(h, f"{hd}/handoff-1.md"), "Overall: PASS")
w(f"{hd}/checks-after.md", "Overall: PASS (1 checks, 0 not as required)\n")
case("handoff: 'done' with passing checks passes", True, run(h, f"{hd}/handoff-1.md", "--repo", repo))
time.sleep(1.1); w(f"{repo}/feature/new.gd", "func x():\n\treturn 1\n")
case("handoff: file edited after the checks ran fails", False, run(h, f"{hd}/handoff-1.md", "--repo", repo), "edited after")

# ---------- check_integrity (on a throwaway copy of the Factory layout)
fac = os.path.join(T, "factory"); shutil.copytree(TOOLS, f"{fac}/tools", ignore=shutil.ignore_patterns("__pycache__", "tests"))
w(f"{fac}/core/rules.md", "rules\n"); w(f"{fac}/runs/x/ledger.md", "l\n")
sh("git init -q && git add -A && git -c user.email=t@t -c user.name=t commit -qm base", fac)
w(f"{fac}/runs/x/ledger.md", "changed\n")
case("integrity: changes under runs/ are fine", True, run("check_integrity.py", tools=f"{fac}/tools"))
w(f"{fac}/core/rules.md", "rules, relaxed\n")
case("integrity: a rule edited during a task fails", False, run("check_integrity.py", tools=f"{fac}/tools"), "core/rules.md")

shutil.rmtree(T, ignore_errors=True)
print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
