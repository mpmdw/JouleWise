# Seat brief — FIXTURE-SENTINEL-CONTROLLER-01 (kernel lane A177)

WRITE_SCOPE: ["tests/test_controller.py","tests/fixtures/fake_powermetrics_process.py","tests/test_run_campaign.py","tests/test_idle_admission.py","tests/fixtures/**"]

You are a root-cause-then-cure seat in the linked worktree you were started in
(branch `fix/2026-09-12-fixture-sentinel-controller`, from origin/main
`ace4cc3c`). TEST AND FIXTURE FILES ONLY: production code under `joulewise/`
and `scripts/` is out of scope by design (the lane cures a test fixture, not
the instrument). If you conclude production must change, return NEEDS_RULING
with the exact reason and do not edit it. Never run git commands that move
HEAD, never push, never touch `/Users/edr/code/JouleWise` or
`/Users/edr/JouleWise-measurement-20260913-derivation` (a measurement night is
armed there; both are fenced). Do not run anything that needs sudo or the real
`powermetrics`.

## Problem

`tests/test_controller.py::…::test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
(~line 1599) fails on this loaded local host and passes in CI. Root-cause
report `docs/process_traces/2026-09-10-activation-96bfeca7/19-rootcause-controller-idle-drift-local-astra-report.md`
(read §Remediation and §Residual risk in full, and the lead note
`19-lead-note-local-controller-failure.md`): the fixture sleeps through its
post-idle capture against a real deadline, the capture times out, salvaged raw
records rederive a drift that disagrees with the stored (unknown) drift, and
strict validation fails. PR #310 (consult 87) already cured the same class in
the campaign-test helper with a bounded `--no-sleep` policy in
`tests/fixtures/fake_powermetrics_process.py` (see `tests/test_run_campaign.py`
and `tests/test_idle_admission.py` for how callers use it); this controller
path never received that cure ("incomplete propagation").

## Acceptance (kernel)

"The fixture uses the bounded --no-sleep policy shared with the campaign-test
helper (PR #310, consult 87); defect-shaped regression per report 19
§Remediation (byte-exact promotion, bounded post drift, strict validation
clean, timeout reproduces without the cure); third instance of the host-timing
fixture class (87, 99, 19) recorded."

## Work

1. Close report 19's residual-risk gap first: run the failing test alone under
   `python -m pytest tests/test_controller.py -q -k test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`
   and record whether it fails here now; then a targeted replay that records
   the `_run_bounded_capture` exception, requested post count, stored drift and
   salvaged post count (instrument the test temporarily or use a scratch
   script under /tmp — never leave instrumentation in the tree). Paste the
   numbers. If it does NOT reproduce on this host, say so and still apply the
   cure (CI-green + local-flaky is the defect).
2. Cure: make the controller fixture path use the SAME bounded `--no-sleep`
   fixture command policy the campaign helper uses (share the helper; do not
   fork a second policy). Keep production deadlines and strict comparisons
   unchanged. Continuous admission/measured sampling keeps pacing; derive the
   post count from the baseline duration (do not pin 100 universally).
3. Defect-shaped regression asserting, under the established sleep stress:
   second-attempt raw promotion byte-exact; stored post drift bounded; strict
   validation returns no problems; fresh reduction retains the admitted
   attempt's source digest; and that removing bounded `--no-sleep` reproduces
   the timeout/unknown-drift failure (that last one may be a counterfactual
   run you paste rather than a permanent test if a permanent one would itself
   sleep against a real deadline — say which and why).
4. Killed cut: revert the cure bytes, run the regression (must FAIL), restore
   (hash-check the bytes), run again (PASS). Paste both result lines.
5. `python -m pytest tests/test_controller.py -q` whole file, and the two
   campaign/idle-admission files if you touched the helper; `git diff --check`.
   Do NOT commit. Report `git status --short` and `git diff --stat`.

## Report (final message, claude-codex-report/v1 envelope per --genre)

Root-cause replay numbers; the cure and which helper policy it shares (cite
lines); killed-cut evidence; whole-file results; any NEEDS_SCOPE/NEEDS_RULING;
anything unsure. Under 8000 bytes.
