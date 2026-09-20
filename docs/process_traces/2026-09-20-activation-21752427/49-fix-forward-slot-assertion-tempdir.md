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

## §3 Counter-review (rows 1/2/6/10) — Opus 5 subagent, read-only; verbatim
FIX-FIRST (the committed fix is correct; an identical, bench-proven-failing sibling remains two tests below it in the same file).
R1 — the new assertion proves the intent, with one nuance. Only the capture carries `--slot` (`scripts/night_chains/calibration_derivation_only.zsh:259` `--slot "$slot"`, `:260` `--attempt-id "${SESSION_ID}-${slot}"`). The reservation carries `--slot-count` (`:194`), not `--slot`, and `"--slot" in call["args"]` is exact element membership, so the reservation call is filtered out. No coverage is lost: the reservation never names an individual slot id; the only place a slot id can appear is the capture pair. The abort carries no slot id. `:543` pins the call count and `:557–561` pins `slot_unused slot=d03`, so an unexpected d03 capture fails three ways. Exact-value comparison replaces substring matching — strictly stronger.
R2 — same-class substring assertions: `tests/test_issue_calibration_acceptance_generation.py:610` `assertNotIn("d03", str(calls))` — LIVE FLAKE, identical class, reproduced: under `TMPDIR=/tmp/tmp-d03-proof`, `test_slot_count_override_and_writer_error_stop` FAILS. Safe (literals too long / characters mkdtemp cannot produce): same file `:598`, `:612`/`:651`/`:675`, `:676`; siblings `tests/test_identity_pins.py:1444`, `tests/test_launch_window.py:2481`, `tests/test_family_marker.py:1525`, `tests/test_paper_custody.py:685`, `tests/test_arm_readiness_evidence_packauth.py:389`.
R3 — Module: `Ran 114 tests in 54.294s / OK`. Single test with `TMPDIR=/tmp/tmp-d03-proof`: OK. Worktree clean; canonical untouched.
Recommendation: fold the `:610` two-line change into this commit and merge.

Disposition: folded as the second commit (sibling reproduced failing under the d03 TMPDIR before the change; module 114 OK after). The safe list is the sweep the lead's §5 lesson asked for — done by the review; no further lane needed.

## §4 Terminal review (row 12) and hosted result (row 11)
(appended before merge)

## §5 Lesson (for the codex-delegation field notes)
Two post-merge reds today came from random temporary names colliding with asserted substrings ("t3" via the generator's census guard; "d03" via a slot-id assertion). Assertions must target the specific argument, and fixtures that feed name-sensitive guards must draw census-clean names (`_census_clean_tempdir`). A sweep of `assertNotIn("<short literal>", str(...))` across tests/ is a cheap successor nit lane.
