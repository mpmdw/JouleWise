# meter-audit handoff

Task brief: 2026-11-08. Branch: `align/2026-11-08-v5-meter-audit`.
Base: `d600baba029f70592bb8e792098338e4cd6811d3` (W1/R10 squeeze lane).
Code commit: `b8cfd1fa6` — `fix(align): report harvested whole-request meter evidence beside rails`.
The separate documentation commit contains this report and the coverage map.

## Delivered

[METER-COVERAGE.md](../METER-COVERAGE.md) audits the acquisition/reduction route
families across ALIGN v4, R0/R1, squeeze simulation, BYTES, B5/B6 and independent
recompute, interp-energy, generic telemetry and calibration. It names every
reviewed snapshot, separates wired capture from demonstrated live coverage,
and lists larger lead work L1–L5.

The important correction to earlier reviews: W1 sessions inherit the KM003C
reader from the shared HAZARD_PACK driver. Missing `km003c` text in the ALIGN
kit does not prove missing capture. This still does not guarantee a usable
stream: the driver does not wait for reader readiness and deliberately
continues when capture is absent. R1 inheritance depends on its actual outer
plan; standalone R0/R1 tools do not independently start/join the meter.

Small code fix: join the existing harvested whole-controller-request meter
record into both ALIGN desk entry points and print DC beside rail evidence.
Retain raw DC, signed battery, corrected machine totals, rail delta, meter
flags, RAW bounds, stream provenance and exact record digest separately.
Unavailable/nonfinite/overflowing evidence stays null; missing battery never
turns the legacy meter-only fallback into complete machine energy. An
unreadable episode can retain DC evidence; a skipped/failed harvest cannot
reuse a stale meter record. No frozen fit, threshold or check consumes the new
diagnostic fields.

Files touched:

- `joulewise/align/apple/meter_desk.py` (new harvested-record join).
- `joulewise/align/apple/thermal_desk.py` (adjacent DC Markdown table).
- `scripts/align_pilot_session.py` (automatic successful-harvest join and console/JSON output).
- `scripts/align_v4_thermal_desk.py` (explicit manifest `meter_record` / `meter_run_id`).
- `tests/align/test_meter_desk.py` (synthetic regression module).
- `docs/align/squeeze/METER-COVERAGE.md` and this report.

## Verification

One unittest module per process, synthetic inputs only; total test execution
was well below one minute and below the 20-minute cap. Final results:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_meter_desk` | 8 passed (0.539 s final run) |
| `python3.13 -B -m unittest tests.align.test_thermal_desk` | 24 passed (1.728 s) |
| `python3.13 -B -m unittest tests.align.test_pilot3` | 7 run, 1 skipped; OK (4.494 s) |
| `python3.13 -B -m unittest tests.align.test_pilot4` | 18 run, 1 skipped; OK (21.548 s) |
| `python3.13 -B -m compileall -q joulewise/align/apple/meter_desk.py joulewise/align/apple/thermal_desk.py scripts/align_pilot_session.py scripts/align_v4_thermal_desk.py tests/align/test_meter_desk.py` | Passed |
| `git diff --check` / staged equivalent | Passed |

Failing first: the new test module failed with missing `meter_desk` before
implementation. A subsequent overflow regression reproduced `OverflowError`
on `10**400`; the finite-number adapter now returns unavailable instead.
One test-harness issue (reusing a checks dictionary mutated by the existing
desk) was corrected to return a fresh dictionary per invocation.

No full suite, sealed analysis pipeline, real meter/powermetrics capture,
model load/download, network, push or merge ran. Explicit focused checks
replace the repository's normal full-suite expectation under the task's
standing rule. Local commits suppress Git hooks so an incidental hook cannot
start a forbidden full suite or network operation. No fresh non-author review
is claimed; lead review is still required before integration.

## Lead rulings used and limits

- All wall-to-machine power through MagSafe passes the KM003C; its physical
  boundary is DC at the brick output, with adapter AC loss excluded. Keep the
  signed battery term distinct. Whole-member energy owns small-effect claims.
- v5 adds to frozen v4. New desk fields are descriptive; no v4 energy model,
  settings, thermal policy, cohort or registration was changed. Full sealed
  transcripts and the off-box API monitor are other fan-out work; no transcript
  was scored here.
- `m >= 39` per pair plus held-out tests, maximum thresholds, unmediated
  physical positive controls and per-attempt escape rate remain binding. This
  lane does not implement or certify those v5 gates.
- D-139 A1's scoped sandboxed adversary amendment was assumed, but no adversary
  or agent workload was launched.
- RUN_STATE, TASK_QUEUE, state kernel, `tests/test_gen_state.py`, sealed B5
  analysis code and R1's integrated lane were untouched. No tasks registered.

Uncertainty: this is a static audit of local snapshots, not proof of the
current remote heads or any night's actual capture. The packet requested a
fetch, but the binding no-network rule prevented it. No external data paths
in configs were followed. Existing core parser/harvest/recompute machine
labels have legacy fallback semantics; the new join guards its own output
without changing their sealed behavior.

An initial commentary claim that interp's `parents[2]` pointed one directory
too shallow was wrong. A pure path check established that it resolves to repo
root; the finding was withdrawn before documentation commit. There is no
interp path-fix recommendation. Its actual gaps are optional capture and
missing measured DC reduction/binding.

## Exact next step

Lead reviews/cherry-picks the code and documentation commits, then assigns
coverage map L1–L3: prospective meter readiness/support qualification, the v5
whole-request DC consumer and standalone/R0/R1 joins. Interp changes belong on
its owning integration branch (L4); do not import partial modules from it.
BYTES baseline-drop handling and any sealed-path consequence need the lead's
prospective registration/custody decision, not an in-place patch here.

Native handoff outside this sandbox, with no active agent measurement load:
run `JW_REAL_METER_SMOKE=1 python3.13 -B -m unittest tests.external.test_km003c_monitor.RealMeterSmokeTests`
on the lead-controlled meter host, then a separately authorized tiny-workload
window proving complete capture/custody, clock mapping, signed battery handling,
PDTR/rails comparison and loss/restart behavior. This smoke alone does not
qualify a small-effect bound. No new MLX code was written; any native replay/
interp capture must use tiny synthetic work and the owning branch's tests,
without downloading weights or opening sealed data.
