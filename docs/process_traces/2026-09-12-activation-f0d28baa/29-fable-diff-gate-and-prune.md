# Record 29 — apex Fable code-reading diff gate (ledger row 7), overbuild / merge-ability prune (row 8), and fresh-eyes pass on post-review commits (row 10)

Written by the resident magistrate (Fable 5.1, activation f0d28baa) 2026-09-12 ~04:40 PDT, after reading each PR's full diff (`git diff ace4cc3c..<head>`) at the bench, not from the reports.

## PR #324 — A177, head c85a171d (tests/test_controller.py +56/−5, tests/test_run_campaign.py +40/−30)

Design questions asked of the diff:
- Is there ONE policy home for "bounded synthetic captures skip sleeping"? Yes: `RetryAdmissionPowermetricsAdapter._command` (test_controller.py:669–678) appends `--no-sleep` iff `count is not None`; the campaign helper's local `patch.object` of the same class is deleted (test_run_campaign.py:9545–9554). Continuous captures (`count=None`) stay paced, pinned by the new `test_powermetrics_fixture_command_only_unpaces_bounded_captures` (None, 3, 7, 100) and by `assertNotIn("--no-sleep", command)` at :1716.
- Does the regression prove the defect rather than a timing accident? The stressed run (`FAKE_POWERMETRICS_SLEEP_SCALE` ≥ 3.5 via `patch.dict`) asserts bounded drift, the production-derived post count, byte-exact promotion, strict validation `[]`, and the admitted digest after fresh reduction; the seat's killed cut (cure removed → `unknown != bounded`, `post_idle_unavailable`) is the counterfactual; it is a one-off replay by the brief's own licence because a permanent timeout test would itself sleep against a real deadline.
- Overbuild: the post-count formula is now written three times (production :1029–1031, controller :1651–1657, campaign :9627–9632) — Opus counter-review 25 nit. Pruning it into a shared test helper would be a fourth file touching a lane that is closed; recorded as a nit, not pruned here (the two test copies are assertions that the fixture's count equals production's derivation, which is the point of writing the formula out).
- Merge-ability: disjoint files from #325 and #326; no production code; fence honoured (`git diff --stat -- joulewise scripts` empty, refuter 24 V-check).
Verdict: MERGE.

## PR #325 — A184, head 50cf73c5 (five files +53/−1 at 7014dd0e; runbook paragraph rewritten twice after)

- Is the new code the smallest correct change? One enum member, one description, membership in exactly the two sets the three siblings share (`_ABORT`, `_WRITER_COMPONENT`; refuter 13's census of every registry set), one map entry, one registry row that the projection freshness test accepts unchanged (the table is projected FROM `REFUSAL_INVENTORY` by `RefusalInventoryTests`, no separate generator — seat 02 §1c). Nothing else in the diff.
- Could the test pass for the wrong reason? The `session-refusal` observer in `WITNESS_CASES` is dispatched to a real `_run("session-refusal", …)` (refuter 13 §4); the `terminal_result == "session_aborted"` branch applies only to the new observer, so the 71 sibling cases' assertions are untouched. Process exit asserted against the new code's own record (resume seat fixed the inherited `SAMPLER_NEVER_READY` reference).
- Prose: the runbook paragraph went seat → bench → cold gate 28 (rule 11 trigger, two consecutive blockers in one paragraph). The ruled text is applied verbatim at 50cf73c5; I verified its load-bearing claim at the bench (`grep -c window_exhausted scripts/recover_calibration_ledger.py`: 0 at f90cb8c0, 1 at HEAD). Opus pairing refuter 12 is the fresh-eyes pass on that post-review commit (row 10); it reads the same lines a fresh reviewer would.
- Overbuild: none. Merge-ability: the armed night's frozen clone is unaffected by main by construction; the paragraph says so in terms the operator can test.
Verdict: MERGE, conditional on pairing refuter 12 not overturning ruling 28.

## PR #326 — gitfix, head 87039749 (tests/test_git_fixture_maintenance.py, tests/test_identity_pins.py, new tests/test_git_fixture_hygiene.py)

- Smallest correct change? The baseline already had the shared initializer (`tests/git_fixture.py`) and 48 routed sites; the diff routes the last raw site (identity_pins) and replaces the census's string-literal heuristic with an alias-resolving argv scanner (`_CommandLiterals`), a shell-string tokenizer (`_shell_git_init`), and by-name maintenance-ON exceptions for the two fenced calibration-exits tests. That is the kernel row's acceptance ("an enumeration test fails if a module creates a git fixture repository without the tuple").
- Overbuild: round 1 added a constant folder with list/tuple folding that no test needed (delta 18: 13 untested clauses); round 2 pruned it to string-Add only (29 → 14 clauses, each with a killing test, independently re-enumerated by delta 27 with zero survivors). The `_CommandLiterals` resolver is larger than a heuristic but every branch is exercised by the hygiene module's thirteen unsafe forms; I do not prune further.
- Fence: no product code; no pre-existing assertion changed (refuter 08 AST comparison 177/177 and 6/6; delta 27 re-check 0 changed). The by-name exception cannot exempt a sibling test (`test_named_maintenance_exceptions_do_not_exempt_other_tests`).
- Merge-ability: disjoint from #324/#325 except that #326's census scans `tests/` including files #324 touches; the census over the integration tree is exercised by the integration replay (row 9).
Verdict: MERGE.

## Row 10 — fresh-eyes on post-review commits
- #324: none after review (single commit c85a171d).
- #325: ca7346e4 (bench fix) → delta 22; 50cf73c5 (ruled text) → Opus pairing refuter 12 + this reading.
- #326: 59873a5c (round 1) → delta 18; 87039749 (round 2) → delta 27.
