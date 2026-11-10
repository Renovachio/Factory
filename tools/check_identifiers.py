#!/usr/bin/env python3
"""List names that a change uses but that the repo has never seen.

For every added line (git diff against --base, plus untracked files) it collects:
  1. called names             foo(
  2. member accesses          thing.member
  3. Class.member pairs       Class.member   (Class starts with a capital)
  4. names passed as strings  call("x"), call_deferred("x"), emit_signal("x"), connect("x"),
                              has_method("x"), get("x"), set("x"), getattr(o, "x"), setattr(o, "x")
Each is looked up in the repo at --base, in definitions made by the change itself, in
--index files (name indexes from tools/name_index.py) and in tools/known_names.txt.
A Class.member pair must have been seen as that pair, or the member must be defined in the
file that declares the class; a real member on the wrong class is reported.

A reported name is not proven wrong. It is UNSEEN: attach evidence for it or remove it.

Usage: check_identifiers.py --repo /path [--base HEAD] [--paths scripts ...] [--ext .gd .py] [--index FILE ...]
"""
import argparse, os, re, subprocess
from _common import expand, git, finish

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True); ap.add_argument("--base", default="HEAD")
ap.add_argument("--paths", nargs="*", default=[]); ap.add_argument("--ext", nargs="*", default=[])
ap.add_argument("--index", nargs="*", default=[])
a = ap.parse_args()
repo = expand(a.repo)
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")

def seen(fixed):
    return subprocess.run(["git", "grep", "-qwF", "-e", fixed, a.base, "--"] + a.paths, cwd=repo, env=ENV).returncode == 0

added = []
rc, out = git(["diff", "-U0", a.base, "--"] + a.paths, repo)
cur = None
for l in out.splitlines():
    if l.startswith("+++ "): cur = l[6:] if l.startswith("+++ b/") else None
    elif l.startswith("+") and not l.startswith("+++") and cur: added.append((cur, l[1:]))
rc, out = git(["ls-files", "--others", "--exclude-standard", "--"] + a.paths, repo)
for f in out.splitlines():
    try:
        for l in open(os.path.join(repo, f), encoding="utf-8").read().splitlines(): added.append((f, l))
    except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
        pass
if a.ext:
    added = [(f, l) for f, l in added if os.path.splitext(f)[1] in a.ext]

DYN = re.compile(r"\b(?:call|call_deferred|callv|emit_signal|connect|disconnect|has_method|has_signal|get|set|getattr|setattr|hasattr)\s*\(\s*(?:[\w.]+\s*,\s*)?[\"']([A-Za-z_]\w*)[\"']")
dynamic = {}
for f, l in added:
    for m in DYN.finditer(l.split("#")[0]): dynamic.setdefault(m.group(1), f)

code = [(f, re.sub(r'"(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\'', '""', l.split("#")[0])) for f, l in added]
defined = set()
for _, l in code:
    for m in re.finditer(r"\b(?:func|def|class|class_name|var|const|signal|enum|function|let|static var)\s+([A-Za-z_]\w*)", l):
        defined.add(m.group(1))
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*(?::[^=]*)?=(?!=)", l): defined.add(m.group(1))
    if re.search(r"\benum\b", l) or re.fullmatch(r"\s*[A-Z][A-Z0-9_]*\s*(=\s*[-\w]+)?\s*,?\s*", l):
        defined.update(re.findall(r"\b[A-Z][A-Z0-9_]*\b", l))
names, pairs = {}, {}
for f, l in code:
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", l): names.setdefault(m.group(1), f)
    for m in re.finditer(r"\b[A-Za-z_]\w*\.([A-Za-z_]\w*)", l): names.setdefault(m.group(1), f)
    for m in re.finditer(r"\b([A-Z][A-Za-z0-9]+)\.([A-Za-z_]\w*)", l):
        names.setdefault(m.group(1), f); pairs.setdefault((m.group(1), m.group(2)), f)
KEYWORDS = set("if elif else for while match return func def class var const and or not in is as await print "
               "self super new range len str int float bool true false null None assert preload load".split())
here = os.path.dirname(os.path.abspath(__file__))
known = set()
for kf in [os.path.join(here, "known_names.txt")] + [expand(i) for i in a.index]:
    if os.path.exists(kf):
        for l in open(kf, encoding="utf-8"):
            l = l.strip()
            if l.startswith("|"): l = l.split("|")[1].strip()      # name index table row
            if l and not l.startswith("#"): known.add(l)
known_members = {k.split(".")[-1] for k in known} | {k.split(".")[0] for k in known if "." in k}

failures = []
for name, f in sorted(names.items()):
    if name in KEYWORDS or name in defined or name in known or name in known_members or len(name) < 3: continue
    if not seen(name):
        failures.append(f"{name} (first used in {f}) -> never seen in repo at {a.base}; attach evidence")
for (cls, mem), f in sorted(pairs.items()):
    pair = f"{cls}.{mem}"
    if pair in known or cls in defined or not seen(cls) or seen(pair): continue   # unseen class already reported
    rc, out = git(["grep", "-lE", rf"class_name\s+{cls}\b|^class\s+{cls}\b", a.base, "--"] + a.paths, repo)
    files = [x.split(":", 1)[1] for x in out.splitlines() if ":" in x]
    ok = any(subprocess.run(["git", "grep", "-qwF", "-e", mem, a.base, "--", fp], cwd=repo, env=ENV).returncode == 0 for fp in files)
    if not ok:
        failures.append(f"{pair} (first used in {f}) -> '{mem}' was never seen on '{cls}'; attach evidence")
for name, f in sorted(dynamic.items()):
    if name in defined or name in known or name in known_members: continue
    if not seen(name):
        failures.append(f'"{name}" passed as a string to a dynamic call (in {f}) -> never seen in repo; attach evidence')
finish("check_identifiers", failures, len(names) + len(pairs) + len(dynamic))
