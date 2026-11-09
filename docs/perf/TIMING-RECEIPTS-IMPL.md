# Timing boundary receipts implementation

2026-11-08. Prospective capture instrumentation; **pending delta review,
STRICT re-registration, and native validation**. The integration includes
`origin/align/2026-11-08-v4-r11` at `a67de02f27328d77f7f40fac931f4b95f6c39dee`
by merge. The Opus review of `5fc873136` supplied the correction scope.
Ed's markers-only rule in `origin/main:docs/perf/SPEED-TOOLBOX.md` controls.
No live or sealed measurement record was used.

## Recorded boundaries

| Owner | Boundary and destination |
|---|---|
| `scripts/run_night.py` | Pack arm/evidence/receipt authoring and verification; OFF-settle and residual sleep; clean dwell; result preparation/persistence; reporting and publication. Uses the driver's existing `night.log`, opened without `O_CREAT` and with `O_APPEND`. The child exclusively owns `night/chain-stages.jsonl`. If no driver log exists (including arm-only), observations remain in memory and no file is created. |
| `joulewise/hazards/arm.py` | Hazard arm and clean dwell. The start marker precedes `dwell_started`, the boot read and the first clock sample; no marker append occurs within that dwell. |
| `joulewise/b5/driver.py` | Arm dispatch and existing worker join, post-chain monitor hold. Only receipt identity crosses into the existing worker. |
| `joulewise/align/apple/thermal_gates.py` | G0 entry/return/timeout/error. Native G1/H receipts remain the detailed source; no per-turn marker series was added. |
| `joulewise/controller.py`, `joulewise/bundle.py` | ALIGN markers are `RuntimeEvent`s in the controller's ordinary in-memory event list. The existing stable sort orders them after `run_started`. `bundle_finalize` brackets final log flushes, and both boundaries flush before `run_finalized`. Final event and summary persistence retain the base writer behavior. |
| `scripts/align_v4_session.py` | Whole v4 install, arm checks, packet rebuild, live meter probe, disk gate and installer handoff. Install markers buffer until the operation exits, then append JSON lines to already-open CLI stdout. Retain that existing CLI transcript for offline timing; no sidecar is created. Direct `arm_checks` calls use their caller's receipt context. |
| `joulewise/b5/chain.py` | Each unmeasured chain settle. One Python sleeping process replaces the existing `/bin/sleep` process; it appends boundaries to the chain's already-existing `window-chain.log`, without `O_CREAT`. There is no additional process alongside the sleep, sampler, timer or thread. Sleep duration remains `SETTLE_S`. |
| `scripts/run_night.py` launcher | A launch-barrier span opens before spawning the blocked launcher, closes before sending its `G` release, and closes on refusal/error unwinding. No marker write is added to the collection loop. |
| `scripts/magistrate_watchdog.py` | Existing observed hold/reason transitions, release and terminal-release paired stamp; unchanged in this correction round. |

Each marker retains schema `joulewise.timing_boundary.v1`, phase/activity,
sequence, span/parent identity, plan/member/attempt/stage, producer, clock
identity/resolutions, and paired integer wall/monotonic stamps. Ends retain
status and return code where available. Requested sleep is descriptive only.
The injected-clock seam additionally retains the original float timestamp
for event ordering: a round trip through epoch nanoseconds must not move an
equal-time marker ahead of its preceding event.

Member appends perform no open, write, flush, fsync, process launch or thread
startup. The controller's existing event drain persists them after measurement.
A process death can lose buffered markers; missing ends remain missing. The
bundle writer no longer holds an extra event stream or relies on a destructor
to close it. Driver and chain turnaround markers add no fsync. These are
boundary observations, never per-sample or per-token markers. No gate decision,
batching, caching, measured episode, or duration policy changed.

## Offline reader

`joulewise/align/window_timing.py` is brought in from the local code object
`dc684b308`, with the following targeted corrections:

- Read member boundary envelopes directly from `events.jsonl`; read driver
  JSON boundary lines mixed with its ordinary ISO text in `night.log`.
- Project complete, validated pairs; report missing/reversed/cross-identity
  pairs and clock disagreement. Refine parent spans at observed boundaries;
  unrelated overlaps stay ambiguous.
- Give observed spans priority over broad `measured_run`/episode envelopes,
  below native turn/tool/gate intervals. Generic projected spans retain their
  member identity and activity.
- Place native G0/G1/H intervals against the member envelope using the
  episode's recorded clock mapping. A G0 timeout before episode start
  remains gate time. A gate outside the member is rejected, never clipped.
- Account for sampler startup/teardown from existing sampling/stage events,
  and the runtime's explicit zero-generation stop-observation phase. No gap
  becomes a known phase just because it lies inside `measured_run`.

For other existing logs (chain settle log, v4 CLI transcript), extract the
explicit JSON marker lines, call `timing_receipts.project(rows)` and then
`reader_projection(documents)`, and pass the resulting documents as `--span`
inputs. Preserve original markers and both diagnostic lists. Only explicitly
authorized, committed records may enter `GitRecords`; its sealed-path fence
is retained. Runtime producers never call the offline projection/reader.

## Synthetic proof and limits

The cross-tree capture test exports code/config from `1a2574b49` without a
fetch or another working tree. Two separate subprocesses run the complete
W1 synthetic at the same temporary output path, one against that base and
one against the current source. Both receive the same tiny synthetic battery
response and deterministic source provenance. Traceback source locations are
removed at the formatting seam in both trees; actual exception types/messages
are retained and compared.
Only process RSS and source-worktree paths are normalized after capture;
only added timing-boundary lines are removed. File sets and every normalized
file's bytes (SHA-256) must match. All **20** bundles (18 W1 members plus two
pilot references) must return `[]` from `validate_bundle` on both trees.
Strict/physics eligibility is not asserted by that structural check.

A second cross-tree check compares the complete structure JSON, actual
harvest yield JSON, stage-journal result, collection-presence decision and
its flags on happy and pre-chain-refusal fixtures. It uses an empty synthetic
roster and the real stage/yield methods; it does not run a production harvest.
Neither consumer implementation was edited.

The actual W1 synthetic output, including its G0 timeout and fault cases,
must have at most **1 ms total unattributed in-member time** across the 18
W1 members in the corrected reader. Native clock diagnostics and deliberately
unclosed failure stages remain visible. This is producer evidence, distinct
from the retained 647-second invented nested-span test against the old reader.

`joulewise/timing_receipts.py` is now in `EXECUTED_CLOSURE` and the committed
dynamic trace. The trace preserves its prior scenarios and unions a fresh,
single-module minimal W1 execution as `timing_receipts_delta`; it is not a
claim that every historical scenario was rerun together. Targeted module
results, all receipt-bound paths, and handoff gates are recorded in
`docs/run_reports/2026-11-08-receipts-fix.md`.

No throughput or live overhead claim is made. The real R16 condition-wait arm,
manual off-machine harvest/backup/push completion, and native MLX/capture
remain lead-owned integration gates. No model weights were obtained, no
quiet-machine session was started, and coordination state was not edited.
