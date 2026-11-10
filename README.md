# Factory

A tool-agnostic set of agent roles and rules that takes a request, questions you until the brief is complete,
and delivers a verified result with an approval gate at every stage.

## How to start a task

In any tool, open a session with this folder available and say:

> Read ~/Documents/Factory/AGENTS.md. You are the Admin. My request: …

The Admin questions you, writes `runs/<id>/brief.md`, and stops at Gate 1.

| Tool | Setup |
|---|---|
| Claude Code | Run it in this folder, or copy `.claude/agents/*` to `~/.claude/agents/` to use the roles from any repo. |
| Claude desktop/web app | Connect this folder (plus the project folder) and use the sentence above. |
| Codex | It reads `AGENTS.md` on its own when started in this folder. From another repo, use the sentence above. |
| Cursor / other | Use the sentence above. Fill in the model names in `core/tiers.md`. |

## How a task flows

Intake (the Admin questions you until the brief is ready) → Scout writes a fact sheet of quoted, located facts →
Planner cuts the work into small work orders and writes the checks → a pre-mortem attacks the plan and the
checks → preflight proves the checks can run and currently fail, and they are locked when you approve →
Builder does one work order at a time → Verifier, in a fresh session, runs the tools and walks the
requirements → Reviewer for large or risky work → close with defect log, lessons and scorecard.
You approve at gates G1 to G4; your exact words are recorded in `gates.csv`.

## Shape

Flat by default: the Admin gives each role only the pointers it needs. A large task with separable
workstreams (a whole new game: art, code, rules, documents) adds one level of Leads, three levels at most,
five children per node. Facts go down as pointers, results come up as a verdict plus files, checking stays
outside the branch, and only the Admin talks to you.

## How it avoids invented facts

- Fact sheets are machine-checked line by line: each claim needs a real file, line and quote, or the label `UNVERIFIED`.
- Builders may only use names from the fact sheet or the name index; a script lists every name, `Class.member`
  pair and string-passed name the repo has never seen.
- Checks are written first, must fail before the work and pass after, and cannot be edited after you approve them.
- Only files named in the approved plan may change.
- Maker and checker never share a session. The Reviewer's first pass is blind to the plan and the handoffs.
- The Factory's own rules and tools are under git and read-only during a task.
- Every defect is logged with the check or rule that will stop it next time.

## How it stays cheap

- One small file is always loaded; everything else is loaded only by the role that needs it.
- Light models locate and extract, standard models build, heavy models are for unclear or risky work.
- Commands do what commands can do. State is in files, so each stage starts in a fresh session.
- Small work orders fail cheaply. Two fix rounds, then the step stops and returns to the Admin.
- Task size decides how many stages, gates and levels run. A pack with five clean runs can earn one fewer gate, if you agree.

## Measuring and maintaining it

- `python3 tools/scorecard.py`: first-pass rate, fix rounds, your corrections, clean runs per pack, open defects.
- `python3 tools/tests/run_tests.py`: 29 attempts to cheat the checks; all must be caught.
- `python3 tools/check_integrity.py`: confirms nobody edited rules or tools during a task.
- The folder is a git repository. `runs/` and `packs/private/` are ignored, so project details never leave your
  machine. Commit after any approved change to the Factory itself.

## Folders

`core/` rules, admin, tiers · `agents/` six roles · `templates/` eleven documents · `tools/` check scripts and
their tests · `packs/` generic domain knowledge · `packs/private/` packs and name indexes about your own projects (not in git) ·
`runs/` one folder per task and the defect log (not in git) · `.claude/agents/` thin Claude Code wrappers.

## Packs

After each task the Admin appends one-line lessons to the pack it used. Keep packs under about 120 lines;
when one grows past that, split it. Check the model mapping in `core/tiers.md` when your tools change.
