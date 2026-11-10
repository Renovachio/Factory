# Tools

Python 3, standard library only. They turn the Factory's rules into pass/fail results. Exit code 0 = pass.
After changing any script: `python3 tools/tests/run_tests.py` (29 cases, each an attempt to cheat a check).

| Script | Proves | Run by |
|---|---|---|
| `check_integrity.py` | Rules, roles, tools and templates were not changed during the task | Admin at start, Verifier |
| `check_citations.py FILE… [--require-quote\|--strict]` | Every `` `ALIAS/path:LINE` `` exists, quotes are really on those lines and long enough, no citation is written without an alias; with `--strict` every line is a cited claim or labelled `UNVERIFIED` | Admin (packs, fact sheets), Verifier (documents) |
| `run_checks.py checks.txt --stage before\|after [--lock]` | Checks are runnable; new-behaviour checks fail before and pass after; `checks.txt` unchanged since it was locked at Gate 2 | Admin (preflight, lock), Builder, Verifier |
| `check_scope.py --repo DIR --plan plan.md` | Only paths in the plan's `Files out` column changed; no secrets or local config; no catch-all allow entries | Admin or Lead after each work order, Verifier |
| `check_identifiers.py --repo DIR [--paths …] [--ext …] [--index FILE]` | Lists names, `Class.member` pairs and string-passed names the repo has never seen | Builder, Verifier |
| `check_handoff.py FILE [--repo DIR]` | A "done" handoff has a passing `checks-after.md` that is newer than every changed file | Admin or Lead |
| `name_index.py …` | Builds the list of names that already exist, with locations | Admin at task start |
| `scorecard.py` | First-pass rate, fix rounds, corrections, clean runs per pack, open defects, computed from `gates.csv`, `verify-<n>.md`, `checks-after.md` and `defects.csv` | Admin at close |

Aliases: declare them once at the top of a document, `<!-- roots: APP=~/code/my-app -->`,
or pass `--root APP=/path` (overrides the document).

Name index example (run from the Factory folder; each pattern's first group is the name):

    python3 tools/name_index.py --root ~/code/my-app/src --ext .py \
      --pattern '\b(events\.[A-Z_]+)\b' \
      --out packs/private/generated/my-app-names.md --alias APP=~/code/my-app

## What the tools cannot do

- A quote that exists is not a quote that supports the claim. The Verifier judges that.
- The identifier check works on text. It does not understand scope or types, and it reports real built-ins the
  repo has not used yet. Accepted built-ins go in `known_names.txt` with their source.
- A check that passes is only as good as the check. The pre-mortem and the Verifier both ask how each check
  could pass with the work not done.
- An agent with write access can still rewrite a lock or the gate record. Git history and the user reading the
  gate report are what expose that; the tools make it visible, not impossible.
- Web citations are not checked yet. Visual results (screens, animation, feel) are not checked at all.
