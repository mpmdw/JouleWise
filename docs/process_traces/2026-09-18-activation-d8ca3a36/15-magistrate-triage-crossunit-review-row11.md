# Magistrate triage — cross-unit review of `b55909e3` (record 05) and the CI result; PR #358 ledger row 11, second half

Reviewer: gpt-6-astra xhigh, read-only, detached worktree at `00e16fed` (main `422cdebb`, code identical to `b55909e3` for every reviewed file; F1). Six seams traced; no BLOCKER; five SHOULD-FIX; CI on the merge head FAILED.

## Verified by the magistrate at the bench (2026-09-18 18:4x PDT, worktree `JouleWise-wt-mag-d8ca3a36` at `061ec81d`)

- **CI on `b55909e3`** (run 35321237232): job `test (3.13, 5)` failed on `tests/test_run_night.py:4607` `test_large_frame_is_incremental_and_still_bounded` with `'REFUSED' != 'GO'`; the other six test jobs were CANCELLED by fail-fast. The two later green main runs (874881d8 run 35321676291, 422cdebb run 35411887587) SKIPPED the `test` and `quick` jobs (docs-only change filter), so they confirm nothing about the code. Locally the test passes in 0.86 s (`PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests.test_large_frame_is_incremental_and_still_bounded` → `OK`); the full replay before merge was 6425/0/0 (record 25). Reading: the fixture's large-frame sample must complete inside its local sample deadline; on a loaded hosted runner the 256 KiB framed read ran past it and the bind expired. This is the same environment-sensitivity family as lane 237 (record 28 G1). Action: the failed jobs were re-run (`gh run rerun --failed`) as post-merge confirmation under Ed's 2026-09-16 CI ruling; the outcome is recorded below when it lands. Whatever it says, the test's deadline dependence is a should-fix: fold into lane 237's scope (queue data, registration seat).
- **R1 confirmed.** `docs/contracts/night_quiet_admission.md:289–290` says "validation enforces the computed 7980 s minimum"; `rg 7980|required_post_bind|runway` hits only `scripts/gen_derivation_night.py` (the generator refuses), nothing in `joulewise/night_plan_writer.py` or `joulewise/night_gate.py`. A hand-authored v4 plan with a short runway parses and can GO. Not a blocker: no v4 plan can be authored without a cold-gate-affirmed cutoff, and the generator is the only sanctioned author; but the sentence is false as written. Fix options are design-bearing (narrow the docs to authoring, or move the derivation into shared validation); they go to the fix lane with a ruling, not to a bench edit.
- **R2–R5** are cross-seam test gaps (generated plan → driver; real sampler output → receipt; persisted refusal files → D-182 helpers; one census fixture shared by binding and watchdog). Each names its counterfactual and production call site; the magistrate accepts them as should-fix without re-tracing each line: they ask for tests that cross seams the per-unit gates only covered from one side, which is exactly what row 11's second half exists to find.
- **S1/S2 deferrals** (lanes 235/236) re-confirmed reachable by the reviewer with numbers (a 1,049,232-byte request over ARG_MAX fails closed to `night_probe_error`; replay is guarded on the normal entry). No change to their lane status.

## Disposition of row 11, second half

DONE with findings: no blocker; one docs-vs-code defect (R1) and four seam-test gaps (R2–R5) plus the CI timing sensitivity registered as queue data for a single follow-up lane, NIGHT-GATE-CROSS-SEAM-TESTS-01 (seat brief to follow in this activation), with lane 237 absorbing the CI item. The first v4 arm record cites this record for row 11.

## CI re-run outcome

(pending at the time of writing; appended below when the re-run finishes)
