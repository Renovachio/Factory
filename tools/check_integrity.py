#!/usr/bin/env python3
"""Verify that nobody changed the Factory's own rules or tools during a task.

The Factory folder is a git repository. During a task, only runs/ and packs/ (lessons, generated
indexes) may change. Any uncommitted change under core/, agents/, tools/, templates/, AGENTS.md
or .claude/ fails. Changing those is a separate task, approved by the user.

Usage: check_integrity.py            (run from anywhere)
"""
import os
from _common import git, finish

factory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTECTED = ["core", "agents", "tools", "templates", "bin", "hooks", "packs/*.md", "AGENTS.md", "CLAUDE.md", ".claude"]
rc, out = git(["status", "--porcelain", "--untracked-files=all", "--"] + PROTECTED, factory)
if rc != 0:
    finish("check_integrity", ["the Factory folder is not a git repository; run: git init && git add -A && git commit -m baseline"], 0)
lines = [l for l in out.splitlines() if "__pycache__" not in l]
finish("check_integrity", [f"{l[3:]} -> changed during a task ({l[:2].strip()})" for l in lines], len(PROTECTED))
