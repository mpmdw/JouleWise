# PR #661: R0 step-duration ruling

Implemented the laptop lead's 2026-11-05 ruling on the already checked-out
`lane/2026-11-05-align-r0-desk`, starting at `d01cbe3b1`. One local commit;
no push, network, real measurement reads, analysis pipeline, or hardware work.
The working tree was clean at intake. M0 intake found no active stop card;
this explicit task is the work-selection authority. Coordination files and
kernel tasks were left untouched as instructed. No delegation was used.

## Changes and clause map

- `docs/align/r0_desk.example.json`: configurable `smc_step` defaults to
  idle/load/recovery 300/900/600 seconds. Omitted fields receive these defaults.
- `joulewise/align/r0_step.py`: validates positive integer durations; load
  <900 s refuses with `smc_step.load_below_tau_upper_bound`. Implements offline
  load-only first-order fits: S_fast tau <30 s from the first 120 s; S_slow
  120 <tau <900 s from load, confirmed on recovery without refitting tau.
  Retains #658's amplitude/noise, per-phase coverage and R2 diagnostic bars;
  confirmation uses the same R2 >=0.8 bar against the load-fit prediction.
- `joulewise/align/r0_runner.py`: normalizes config, records profile/budget
  and ruling authority, passes configured phases to the hook, and records an
  early structured refusal for short profiles before host/model/capture work.
  The CLI exits 2 with the refusal code before constructing its guard.
- `joulewise/align/r0_host.py`: passes durations explicitly to #658, uses
  phase total +600 s subprocess timeout, verifies saved journal SHA-256 and
  phase durations, and re-ranks using the ruled windows. Retains the original
  #658 response alongside the new result. A passing source process alone is
  insufficient. R0's >99% valid 1 Hz slots over >=600 s bar remains.
- `joulewise/align/r0_host.py` and `joulewise/align/r0.py`: disk receipts and
  Markdown include the full 1,800 s capture and a 16 KiB/slot planning journal
  allowance (29,491,200 bytes). Require 80 GB plus that allowance after present
  weights; longer profiles scale both estimates. The row size is an estimate,
  not measured evidence or a journal-size cap.
- `docs/align/r0_desk_runbook.md`: ruled profile, config/refusal behavior,
  5.5–6.5 h total desk planning budget including the 30 min, disk allowance,
  fitting/confirmation rules and live limitations.
- `docs/align/r0_step_test_ruling.md`: short authority note citing Amendment 1
  A5.3 at `6eb1ff5be` and #658's selection rule at `274fec2cb`; includes the
  matching #658 integration note. Both source texts were read from permitted
  local Git objects. No PR comments were posted in this offline lane.
- `tests/align/test_r0_step.py` and `tests/align/test_r0_host.py`: synthetic
  analytic responses, early refusal, config propagation, dynamic timeout and
  budgeting, journal validation, fast-window isolation, recovery confirmation,
  missing slots and phase mismatch. Synthetic tau 800 s guards against the
  former tau <recovery-duration restriction.

## Verification

Targeted unittest modules ran separately, sequentially with Python 3.13.
All final runs passed: **65 tests**. Each module's reported test time was
under one second; total test time including baseline/repeats was far below
the requested ~20-minute ceiling.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_r0_step` | 12 passed |
| `python3.13 -B -m unittest tests.align.test_r0_host` | 16 passed |
| `python3.13 -B -m unittest tests.align.test_r0_checks` | 25 passed |
| `python3.13 -B -m unittest tests.align.test_r0_progress` | 3 passed |
| `python3.13 -B -m unittest tests.align.test_r0_integration` | 2 passed |
| `python3.13 -B -m unittest tests.align.test_r0_documentation` | 2 passed |
| `python3.13 -B -m unittest tests.align.test_r0_mlx` | 5 passed; fake native APIs only |
| `git diff --check` | Passed |
| `ast.parse` on all six changed/new Python files; `json.loads` on example config | Passed |

Pre-edit baseline: `tests.align.test_r0_host`, 14 passed. The full suite was
intentionally not run, per the user's machine-load instruction. Python 3.11
and CI were not exercised. No MLX import or native execution was attempted.

## Interpretation, uncertainty and handoff

The brief asks for synthetic tau 60 s /400 s to pass but also fixes S_fast
tau <30 s. Those traces both pass the load-fit and recovery checks, and 400 s
qualifies as slow; the pair alone correctly leaves fast selection inconclusive.
A separate 20 s /400 s fixture verifies complete selection. No scientific
threshold was relaxed to label 60 s as fast.

Sensor anatomy and all native behavior remain **PROVISIONAL**. #658's capture
script/module are absent on this checkout and were not ported by this change.
The adapter consumes the source commit's existing report/journal format;
integration and live behavior have not been tested. The 16 KiB journal-row
allowance must be checked against actual enumeration size. Recovery R2 can
reject real multi-timescale/noisy responses; fake fits prove no hardware gate.

Next exact step for the lead: integrate the admitted #658 lane and its matching
ruling note in the measurement checkout, review this commit, then run
`python3.13 -B -m unittest tests.align.test_r0_mlx_native` on the pinned
Metal-capable stack outside the sandbox. After the analysis job and all agent
sessions have stopped, run the guarded R0 SMC check with 300/900/600 and review
the actual load/recovery traces, >99% slot coverage, journal size and sensor
roles. No live gate is claimed here.
