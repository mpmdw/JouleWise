# Record 49 — fix-forward after PR #375: a slot-id assertion matched the runner's random temporary directory (2026-09-20 16:05–16:15 PDT)

## §1 Defect (executed evidence)
Post-merge run 35542767131 on main `790cce67`: `test (3.13, 3)` FAILURE (nine shards cancelled by fail-fast). Job 106163653130: `tests.test_issue_calibration_acceptance_generation.DerivationChainSkeletonTests.test_window_exhausted_refuses_next_slot_and_aborts_once` — `assertNotIn("d03", str(python))` matched `/tmp/tmp69h2kd03/ledger.jsonl` inside the argv string. The test's intent (slot d03 never reserved or captured after the window is exhausted) is unaffected; the assertion form is the defect — the same class as the 07:57 "t3" incident (record 26 §1: random temp names colliding with asserted substrings). B2 (PR #375) changed only `joulewise/evidence_night.py`; the module passes at the bench at `790cce67` (114 OK; the single test OK); the PR head's shard 3 was green because its temp name did not contain "d03".

## §2 Fix (branch `fix/2026-09-20-slot-assertion-tempdir`, `184516b2`, one assertion; diff gate by the magistrate)
The assertion now checks the `--slot` argument values of the recorded python calls (the module's own established pattern at :568/:648): `assertNotIn("d03", [call["args"][call["args"].index("--slot") + 1] for call in python if "--slot" in call["args"]])`. Bench:
```
module at 184516b2: Ran 114 tests in 54.140s OK
single test with TMPDIR=/tmp/tmp-d03-proof at 184516b2: OK
single test with TMPDIR=/tmp/tmp-d03-proof at main 790cce67 (stash): FAILED (failures=1)   ← the counterfactual
```
Replay for row 9: the delta is one test assertion; the module alone at the bench plus the counterfactual; the hosted matrix on the PR head and post-merge are the platform proof.

## §3 Counter-review (rows 1/2/6/10)
(appended: Opus review)

## §4 Terminal review (row 12) and hosted result (row 11)
(appended before merge)

## §5 Lesson (for the codex-delegation field notes)
Two post-merge reds today came from random temporary names colliding with asserted substrings ("t3" via the generator's census guard; "d03" via a slot-id assertion). Assertions must target the specific argument, and fixtures that feed name-sensitive guards must draw census-clean names (`_census_clean_tempdir`). A sweep of `assertNotIn("<short literal>", str(...))` across tests/ is a cheap successor nit lane.
