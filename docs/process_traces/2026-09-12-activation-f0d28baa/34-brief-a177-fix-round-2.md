# Fix-round brief — FIXTURE-SENTINEL-CONTROLLER-01 round 2 (delta re-audit 33 R1: the regression does not protect its own stress injection)

WRITE_SCOPE: ["tests/test_controller.py","tests/test_run_campaign.py","tests/test_idle_admission.py","tests/fixtures/fake_powermetrics_process.py","tests/fixtures/**"]

Fix-round seat in the linked worktree you were started in (branch
`fix/2026-09-12-fixture-sentinel-controller`, HEAD `8a5d1169`, PR #324).
Tests/fixtures only (kernel fence; production out of scope → NEEDS_RULING).
Never move HEAD, never push, never touch `/Users/edr/code/JouleWise`
(read-only use of `/Users/edr/code/JouleWise/.venv/bin/python3` is allowed)
or `/Users/edr/JouleWise-measurement-20260913-derivation`. `python3 -m
unittest` only. Read first, in this order, from
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/`:
33 (delta re-audit: the per-cut table and R1), 31 (round-1 report), 30
(round-1 brief with the CI failure). This is a DIFFERENT defect class from
round 1 (round 1: stress on the wrong capture → CI-red; round 2: the test's
stress wiring is unprotected, so the test passes with the cure removed once
the wiring is cut).

## R1 (blocker) — what must become true

Delta 33 shows these in-memory cuts SURVIVE the selected regression
`HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`:
`registry` (delete `registry.adapter_type = StressedSentinelAdapter` → pass,
AND still pass with `--no-sleep` removed: 71 samples, scale 1, 15.3 s timeout),
`floor` (12 → 3.5), `default` ("12" → "1"), `env_override`, `stress_patch`
(bounded `str(scale)` → "1"), plus `strict_compute`, `strict_expectation`,
`drift_message`. Per the isolation rule every clause that decides whether the
regression can detect report 19's defect needs exactly one selected test
that fails when it is cut.

Cure shape (choose the smallest that kills all the listed cuts; say why):
- Make the stress OBSERVABLE and ASSERTED: the stressed adapter records the
  effective bounded sleep scale and the bounded capture's requested count /
  wall time; the regression asserts (a) the recorded scale ≥ the floor, (b)
  the arithmetic that makes the cure necessary holds for THIS run —
  `count × interval_s × scale > the production bounded-capture timeout`
  (quote the production timeout formula, `joulewise/adapters/powermetrics.py`
  ~:1470 `max(15.0, nominal_s * 1.5 + 10.0)`), so that a cut which removes
  or weakens the stress fails the arithmetic assertion instead of silently
  passing; (c) the bounded capture actually ran with `--no-sleep` (the
  recorded argv) while the continuous capture did not.
- For `strict_compute` / `strict_expectation`: the strict-validation
  assertion must be load-bearing — assert the exact `[]` and that the
  validator was actually invoked on the reduced bundle (e.g. the result
  object is the validator's, not a default).
- Do NOT add real sleeps to the test's own critical path; do not change any
  production deadline; do not weaken the defect shape (report 19's
  counterfactual must still FAIL with TimeoutExpired / post_idle_unavailable
  / both strict mismatches — re-run the killed cut and paste both lines).

## Verify
Re-run delta 33's cut list yourself IN MEMORY (its harness may still be at
`/private/tmp/a177_delta_audit.py` — reuse or rewrite; never leave it in the
tree) and paste the per-cut table: every cut from the R1 list must now FAIL
(name the assertion that catches it). `python3 -B -m unittest
tests.test_controller -q` with the venv interpreter AND system 3.14; paste
result lines. `git diff --check`. Do NOT commit; report `git status
--short` and `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
Cure shape and why; per-cut table; killed-cut lines; per-interpreter
results; any NEEDS_SCOPE/NEEDS_RULING. Under 8000 bytes.
