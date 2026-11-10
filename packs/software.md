# Pack: General software

## Intake questions

- Repo path, language, how to build, run and test (exact commands). If unknown, a Scout finds them.
- Bug: steps to reproduce and expected result. Feature: acceptance criteria.
- Constraints: versions, platforms, dependencies allowed, style rules.
- Git rules for this repo: branch, commit format, who pushes.

## Rules

- Read versions from the project files before relying on any API. Check unfamiliar APIs against current official docs or the installed package source, and cite it.
- Bug fixes start with a failing reproduction (test or script). The same reproduction passing is the proof.
- Smallest diff that meets the criteria. No new dependency without approval at G2.
- Follow the patterns of the nearest existing code (cite the file you modelled on).
- Run the project's own tests and linters; paste the output.

## Acceptance checks

Build passes · tests pass (output pasted) · reproduction passes · diff contains only planned files.

## Lessons
