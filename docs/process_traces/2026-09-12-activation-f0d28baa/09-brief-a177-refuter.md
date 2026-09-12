# Refuter brief — FIXTURE-SENTINEL-CONTROLLER-01 landing (execution lens)

SESSION_MODE: delegated
WRITE_SCOPE: []

You are a READ-ONLY refuter (sandbox read-only; run tests, never edit).
Branch `fix/2026-09-12-fixture-sentinel-controller` in this worktree, one
commit over origin/main `ace4cc3c`: `git diff ace4cc3c..HEAD`. Seat report:
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/04-seat-a177-astra-report.md`;
seat brief `03-brief-a177-fixture-sentinel-controller.md` beside it (read
its Problem and Acceptance). Root-cause record:
`docs/process_traces/2026-09-10-activation-96bfeca7/19-rootcause-controller-idle-drift-local-astra-report.md`.
Never touch `/Users/edr/code/JouleWise` or
`/Users/edr/JouleWise-measurement-20260913-derivation` (fenced). Use
`python3 -m unittest` (no pytest on this host).

Kernel fence: TEST AND FIXTURE FILES ONLY; production deadlines and strict
comparisons unchanged. Acceptance: shared `--no-sleep` policy with the
campaign helper (PR #310, consult 87), no second policy fork; defect-shaped
regression (byte-exact promotion, bounded post drift, strict validation
clean, timeout reproduces without the cure); third instance recorded.

Try to BREAK it:
1. Policy sharing: is there now exactly ONE place that appends `--no-sleep`
   for bounded captures across `tests/test_controller.py`,
   `tests/test_run_campaign.py`, `tests/test_idle_admission.py`,
   `tests/fixtures/fake_powermetrics_process.py`? grep and quote. If the
   campaign helper's removed `unpaced_sentinel` patch had any behaviour the
   adapter override lacks (e.g. it patched a DIFFERENT adapter class than the
   one `produce_retry_powermetrics_bundle` instantiates), that is a blocker.
2. Defect shape: the regression now forces `FAKE_POWERMETRICS_SLEEP_SCALE`
   ≥ 3.5 via `patch.dict`. Confirm the fixture honours that variable (quote
   the line in `tests/fixtures/fake_powermetrics_process.py`) and that the
   cure removal really fails: with the tree read-only, replay the seat's
   killed cut yourself by copying the two test modules to /tmp is NOT
   possible (imports); instead run the regression with the override
   neutralised via an environment-free harness if one exists, else re-read
   the seat's V5 evidence and say whether the killed-cut script (seat left
   it at `/private/tmp/a177-killed-cut.py` if still present) restores bytes
   by hash.
3. Assertion soundness: the new `post_sample_count` expectations in both
   files mirror production's derivation (`joulewise/adapters/powermetrics.py`
   ~1030). Quote the production lines and confirm the formula
   (`max(3, ceil(max(3*0.05, min(5.0, baseline_s)) / 0.05))`) is the same
   arithmetic; a mismatch on any boundary (baseline < 0.15 s, = 5.0 s) is a
   should-fix.
4. Regressions elsewhere: does any OTHER test in the three modules assert
   that continuous captures carry no `--no-sleep` or that the adapter's argv
   is unchanged, such that the override changes their meaning? Run
   `python3 -B -m unittest tests.test_controller -q` once and paste the
   result line (about 75 s). Skip the 245 s campaign run unless step 1
   raises a doubt.
5. Anything that reads as a production-code change or a weakened strict
   comparison is a blocker; quote it.

Report (claude-codex-report/v1, genre review): findings tiered
blocker / should-fix / nit with the reproducing command or quoted line;
explicit "no blocker found" if none. Under 8000 bytes.
