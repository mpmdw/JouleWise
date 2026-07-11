# PR #49 P2-038 Rail-Only Gate Flake Root Cause

Date: 2026-07-10  
Branch/head at intake: `impl/nvgate2-codenow` / `13f6c9e`  
Lane: `[AGENT]` fixture/root-cause work; no quiet-machine measurement

## Outcome

The failure is a pre-existing main-side race in
`tests/fixtures/fake_powermetrics_process.py`, not an interaction with the
NV-GATE changes in PR #49. The fixture promised a sample after the controller's
stop marker, but SIGTERM could arrive after a sample write and before the loop
condition. The signal handler then cleared `RUNNING`, so the child exited
without writing a new right-edge sample.

That leaves the measured stop marker later than the final trace timestamp.
Reducer `_bracketing_gap_s` consequently returns `None` for the end edge. The
gross-request gate fails closed for the two stable reasons
`cadence_ratio_unrecorded` and `interpolation_bound_unrecorded`. The rail-only
contamination behavior remains correct: `idle_drift` is unknown with
`contamination_evidence_unknown`, and only the idle-subtracted gate adds
`drift_term_unknown`.

The minimal fix is test-fixture-only. The child records the monotonic SIGTERM
instant and does not exit until it has emitted a sample endpoint at least one
requested interval later. No production reducer, evidence, contamination, or
claim-gate semantics changed.

## Timing and scheduling inputs traced

- `SystemClock.now`, `stamp`, and `sleep`: epoch reads, paired monotonic reads,
  clock resolution, and scheduler-dependent sleep completion.
- Controller sampling markers: `sampling_started` after first-parse readiness
  and `sampling_stopped` immediately after the runtime returns.
- Mock runtime duration: one 32 ms prefill sleep plus 200 decode sleeps of
  10 ms each; real `SystemClock` makes the measured duration sensitive to
  oversleep and runner scheduling.
- Powermetrics launch/readiness: Popen scheduling, monotonic readiness deadline,
  10 ms polling, file visibility, and the first-parse paired clock stamp.
- Fake sampler records: real monotonic interval endpoints/`elapsed_ns`, real
  sleeps, native wall-clock plist timestamps, SIGTERM delivery, and final-frame
  completion.
- Idle captures: interval-rounded sample counts, subprocess capture duration,
  scheduler-derived `elapsed_ns`, and post-idle count derived from the measured
  pre-idle duration.
- Evidence derivation: five paired stamps, wall-minus-monotonic envelope,
  first/last interval-support bounds, native whole-second consistency, and the
  effective clock-anchor bound.
- Reducer timing gates: measured-window duration, in-window count, in-window
  p95 gap, both edge-bracketing gaps, cadence ratio, quarter-window clock
  threshold, and joint-edge interpolation availability.

## Gross-request reason audit

The gross gate can emit:

- `nonpositive_window_duration` — unreachable in a succeeded bundle because
  reduction rejects the window first;
- `cadence_ratio_unrecorded` — timing-reachable, and observed here when the
  end bracket was missing;
- `cadence_ratio_below_threshold` — timing-reachable if the governing sample
  gap exceeds one quarter of the request window;
- `clock_bound_unrecorded` — reachable on invalid/inconsistent clock evidence,
  but not produced by the rail-only content itself;
- `clock_bound_exceeds_quarter_window` — timing-reachable under a sufficiently
  wide launch/edge bound;
- `interpolation_bound_unrecorded` — timing-reachable, and observed here from
  the same missing end bracket; and
- `cooldown_cap_hit` — unreachable in this direct-run fixture because it
  supplies no campaign cooldown-cap metadata.

`insufficient_in_window_samples`, `drift_term_unknown`, and
`idle_baseline_unrecorded` cannot make this gross gate false: request sample
count is not required, and P2-040 deliberately disabled drift/idle-baseline
requirements for `gross_request`.

## Reproduction evidence

- Exact test at PR head, 100 fresh processes before the fix: 96 pass, 4 fail.
- Retained diagnostic failure, iteration 27: window duration
  `2.4420013427734375`; 42 in-window samples; p95 gap
  `0.06186342239379883`; clock bound `0.10814642906188965` (well below the
  `0.6105003356933594` quarter-window boundary); bracketing max and cadence
  ratio `null`; reasons exactly `cadence_ratio_unrecorded` and
  `interpolation_bound_unrecorded`.
- Strategic capture compression (remove the last complete measured plist
  frame): final trace `1783752473.6418893` before stop marker
  `1783752473.7183008`; the same two reasons were emitted deterministically.
- Archived `origin/main` reproduced the original assertion on iteration 6.
  The P2-038 test, fixture, evidence module, and powermetrics adapter were
  byte-identical to the PR head before this fix.

## PR #49 interaction audit

The test selects local transport, mock runtime, and powermetrics telemetry.
PR #49's identity-aware survival handling and NVIDIA worker/sampler paths are
not instantiated. `remote_cleanup_failed` and `runtime_cleanup_ok` are quality
fields only; the 0.3.1 additive-absence union changes schema/strict dispatch,
not `_window_claim_eligibility`. The branch's reducer delta versus main adds
remote cleanup quality and NVIDIA token-source handling, with no change to the
request gate or gap/interpolation functions. Main reproduces independently.

## Verification after fixture fix

- Exact rail-only test, 100 fresh processes: 100 pass, 0 fail. Tail:

  ```text
  .
  ----------------------------------------------------------------------
  Ran 1 test in 4.020s

  OK
  ```

- Focused module:

  ```text
  .....
  ----------------------------------------------------------------------
  Ran 5 tests in 30.480s

  OK
  ```

- Canonical suite, unpiped to a file:

  ```text
  Ran 1041 tests in 66.509s

  OK (skipped=13)
  ```

  The skips are the existing retained-corpus, localhost-socket, and optional
  analysis gates. No production or live hardware claim was made.

## Files changed

- `tests/fixtures/fake_powermetrics_process.py`
- `docs/run_reports/2026-07-10-pr49-p2038-flake-root-cause.md`
- `RUN_STATE.md`
- `TASK_QUEUE.md`

No commit was created. The next exact step is lead diff review, then rerun PR
#49 CI and merge only if both Python jobs remain green.
