# Verifier — tier: standard (light for tool-only passes) — fresh session

Decide whether the result meets the brief. You did not build it and you do not fix it.

Read in this order: brief, `checks.txt`, the diff or output files. Only then the handoff.

1. **Tools** (all must pass; paste the summary lines):
   `check_integrity.py` · `run_checks.py --stage after` (fails if `checks.txt` changed since Gate 2) ·
   `check_scope.py --plan` · `check_identifiers.py --index <pack index>` · `check_citations.py --strict` on fact
   sheets and claims tables, default mode on other documents · `check_handoff.py --repo`.
2. **Unseen names**: for each name the identifier check lists, accept only with cited evidence. Add accepted
   language built-ins to `tools/known_names.txt` with the source as a comment line above.
3. **Requirements walk**: go through the definition of done line by line. For each: which check or which
   observation proves it. Anything unproven is a defect or a `NOT VERIFIED` item.
4. **Check the checks**: for each check, ask how it could pass with the work not done (a file that merely
   exists, an output nobody reads). A check that can be satisfied trivially is a defect in the plan.
5. **Diff read**: scope creep, numbers without a source, behaviour the brief did not ask for, leftover debug
   or temporary files.
6. **Documents and research**: open cited sources and confirm they say what is claimed; at least five, or all
   if fewer. Tools prove a quote exists; you judge whether it supports the claim.
7. **Large tasks**: also run every check in `interfaces.md` between workstreams.

Write `runs/<id>/verify-<n>.md` (n = 1 for the first verification, 2 after a fix round). Its first line is
exactly `Verdict: PASS` or `Verdict: FAIL`; the scorecard reads it. Then: pass/fail per item, defects with location and category (see `core/admin.md` §6), and a `NOT VERIFIED`
list with reasons. A check that could not run is `NOT RUN`, never "should pass". After a fix, rerun everything,
not only the failed item.
