#!/usr/bin/env python3
"""Verify that citations in a markdown file point at something real.

A citation is a backticked token  `ALIAS/relative/path:LINE`  or  `ALIAS/path:LINE-LINE`
or just `ALIAS/path`. ALIAS is declared with --root ALIAS=/folder or in a
'<!-- roots: ALIAS=/folder; ... -->' comment in the file.
If the line continues with  > "quoted text"  the quote must appear in the cited lines
(2 lines of slack, whitespace-insensitive) and be long enough to mean something.

Modes
  default          check every citation found; fail any path:LINE written without an alias
  --require-quote  also fail citations that have a line number but no quote
  --strict         for fact sheets and claims tables: every content line must be a claim line
                   (F1. / C1. ...) that carries a quoted citation, or the label UNVERIFIED,
                   or 'user (brief' ; free prose is only allowed as '- ' items under the
                   '## Conflicts' and '## NOT FOUND' headings. Implies --require-quote.

Usage: check_citations.py FILE [FILE...] [--root ALIAS=/folder ...] [--require-quote | --strict]
"""
import argparse, os, re
from _common import parse_roots, norm, finish

MIN_QUOTE = 12  # characters, after whitespace is collapsed

ap = argparse.ArgumentParser()
ap.add_argument("files", nargs="+")
ap.add_argument("--root", action="append", default=[])
ap.add_argument("--require-quote", action="store_true")
ap.add_argument("--strict", action="store_true")
a = ap.parse_args()
need_quote = a.require_quote or a.strict

failures, warnings, checked = [], [], 0
bare = re.compile(r"(?<![\w/])([\w.\-]+(?:/[\w.\- ]+)*\.[A-Za-z]{1,8}):(\d+)(?:-\d+)?\b")
for fname in a.files:
    if not os.path.isfile(fname):
        failures.append(f"{fname}: file does not exist"); continue
    text = open(fname, encoding="utf-8").read()
    roots = parse_roots(a.root, text)
    if not roots:
        failures.append(f"{fname}: no roots declared"); continue
    alias_re = "|".join(re.escape(k) for k in sorted(roots, key=len, reverse=True))
    cite = re.compile(r"`(" + alias_re + r")/([^`]+?)(?::(\d+)(?:-(\d+))?)?`")
    section, in_code = "", False
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```"): in_code = not in_code; continue
        if in_code or not s or s.startswith("<!--"): continue
        if s.startswith("#"): section = s.lstrip("# ").lower(); continue
        cites = list(cite.finditer(line))
        # citations written without an alias are invisible to this tool: refuse them
        rest = cite.sub("", line)
        for b in bare.finditer(rest):
            failures.append(f"{fname}:{n} '{b.group(0)}' -> looks like a citation but has no alias; write `ALIAS/{b.group(0)}`")
        good_quote = False
        for m in cites:
            checked += 1
            alias, rel, l1, l2 = m.groups()
            where = f"{fname}:{n} `{alias}/{rel}{':'+l1 if l1 else ''}{'-'+l2 if l2 else ''}`"
            path = os.path.join(roots[alias], rel)
            if not os.path.exists(path):
                failures.append(f"{where} -> path does not exist"); continue
            if not l1: continue
            if os.path.isdir(path):
                failures.append(f"{where} -> is a folder, cannot have a line"); continue
            src = open(path, encoding="utf-8", errors="replace").read().splitlines()
            lo, hi = int(l1), int(l2 or l1)
            if lo < 1 or hi > len(src) or lo > hi:
                failures.append(f"{where} -> file has {len(src)} lines"); continue
            q = re.search(r'>\s*"(.+?)"\s*(?:;|$)', line[m.end():])
            if q:
                quote = norm(q.group(1).replace('\\"', '"'))
                if len(quote) < MIN_QUOTE or len(re.findall(r"[A-Za-z0-9_]{2,}", quote)) < 2:
                    failures.append(f"{where} -> quote too short to prove anything ({len(quote)} chars)")
                elif quote not in norm(" ".join(src[max(0, lo-3):hi+2])):
                    failures.append(f"{where} -> quote not found at those lines")
                else:
                    good_quote = True
            elif need_quote:
                failures.append(f"{where} -> no quote given")
        if a.strict:
            if s.startswith("Checked with"): continue
            is_claim = re.match(r"^(?:[-*]\s*)?[FC]\d+\.", s)
            labelled = "UNVERIFIED" in s or "user (brief" in s
            if is_claim:
                checked += 0 if cites else 1
                if not (good_quote or labelled) and not any(f.startswith(f"{fname}:{n} ") for f in failures):
                    failures.append(f"{fname}:{n} claim has no quoted citation and no UNVERIFIED label")
            elif section.startswith(("conflicts", "not found")) and (s.startswith(("-", "*")) or s.lower().startswith("none")):
                pass
            else:
                failures.append(f"{fname}:{n} statement outside a claim line (F<n>. / C<n>.): '{s[:60]}'")
finish("check_citations", failures, checked, warnings)
