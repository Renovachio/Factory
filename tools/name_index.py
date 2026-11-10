#!/usr/bin/env python3
"""Build an index of names that already exist in a code base, with one location each.

Use it when the source or docs of a dependency are not available: the index is the list
of names agents are allowed to use without further evidence.

Usage: name_index.py --root /repo/scripts --ext .gd --pattern 'REGEX' [--pattern ...] --out FILE --alias CM=/repo
Each pattern's first group (or whole match) is the name. Output is a markdown table:
name, number of uses, first location as a checkable citation.
"""
import argparse, os, re, datetime
from _common import expand

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True); ap.add_argument("--ext", nargs="+", required=True)
ap.add_argument("--pattern", action="append", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--alias", required=True, help="ALIAS=/folder used to write citations")
a = ap.parse_args()
alias, base_raw = a.alias.split("=", 1); base = expand(base_raw); root = expand(a.root)
pats = [re.compile(p) for p in a.pattern]
seen = {}
for d, _, files in os.walk(root):
    for fn in sorted(files):
        if os.path.splitext(fn)[1] not in a.ext: continue
        p = os.path.join(d, fn)
        for n, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            for pat in pats:
                for m in pat.finditer(line):
                    name = m.group(1) if m.groups() else m.group(0)
                    e = seen.setdefault(name, [0, f"{alias}/{os.path.relpath(p, base)}:{n}"])
                    e[0] += 1
with open(a.out, "w", encoding="utf-8") as f:
    f.write(f"<!-- roots: {alias}={base_raw} -->\n# Name index — generated {datetime.date.today()} by tools/name_index.py\n\n")
    f.write(f"Source: `{alias}/{os.path.relpath(root, base)}` ({', '.join(a.ext)}). Patterns: {' ; '.join('`'+p+'`' for p in a.pattern)}\n")
    f.write("Regenerate instead of editing. A name not listed here needs its own evidence.\n\n| Name | Uses | First seen |\n|---|---|---|\n")
    for name, (c, loc) in sorted(seen.items()):
        f.write(f"| {name} | {c} | `{loc}` |\n")
print(f"name_index: {len(seen)} names -> {a.out}")
