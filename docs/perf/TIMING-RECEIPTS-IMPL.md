# Timing boundary receipts implementation

2026-11-08. Implementation against `origin/align/2026-11-08-v4-r11`;
reader/spec pinned to `dc684b308` on `origin/fix-timing`. Ed's markers-only
rule in `origin/main:docs/perf/SPEED-TOOLBOX.md` supersedes the proposal's
new-sidecar/durable-write language. **Prospective capture change, pending
Opus review and registration. Not a completed live timing ledger.**

## Recorded boundaries

| Owner | Boundary and journal |
|---|---|
| `scripts/run_night.py` | Pack arm, evidence authoring, receipt generation/verification; broad arm-only admission; actual OFF-settle envelope/residual sleep; derivation clean dwell; result inventory/write and post-chain preparation; reporting hand-off; publication, results copy, local commit and push. Uses the existing `night/chain-stages.jsonl`, opened before admission and retained until driver cleanup. |
| `joulewise/hazards/arm.py` | Hazard arm, including refused returns and terminal `arm.json` persistence; actual clean dwell. Uses the caller's driver journal. |
| `joulewise/b5/driver.py` | Arm dispatch (including existing worker startup/join) and post-chain monitor hold. Copies the receipt context into the already-existing arm worker; starts no additional worker. |
| `joulewise/align/apple/thermal_gates.py` | G0 call start, terminal outcome, timeout and exceptions, including a collector fault before the native interval exists. Uses the member's existing `events.jsonl` handle. G1/H retain their existing native receipts; H's actual dispatch/resume endpoint is preserved. No duplicate per-turn series. |
| `joulewise/bundle.py`, `joulewise/controller.py` | Bind each ALIGN member's existing event journal before execution; bracket final summary persistence. The terminal boundary follows the write without rewriting its result. Non-ALIGN event bytes retain their existing behavior. |
| `scripts/magistrate_watchdog.py` | Observed holds (`FENCED`, census/unsafe/clock/network holds, backoff, stopped), including changes of reason, activation or fenced plan. Close at release/launch; record a paired terminal-release milestone. These are watchdog holds, not thermal cooling or model idle. |

Each marker is one JSONL record with schema `joulewise.timing_boundary.v1`:
`start`/`end`, phase, activity, producer/producer ID, sequence, span/parent
ID, plan/member/stage/attempt, clock domain, boot ID, both resolutions and
integer `epoch_ns`, `monotonic_before_ns`, `monotonic_after_ns`. Production
reads the wall clock inside the monotonic bracket. Ends retain status and
return code where available. Requested sleeps appear only as `requested_s`.
Identity unavailable from the existing owner is explicitly null; no extra
boot probe or inferred identity is introduced.

The helper performs only boundary stamping/encoding/appending. It computes
no durations, ledger, gate decision, inventory or hash. It creates no file,
thread or process. The owners extend existing journal-handle lifetimes;
no additional journal basename is introduced. Parent and shell stage writers
operate before/after the chain respectively; markers have no `stage_id`, so
existing stage consumers ignore them. Each member has its own producer and
journal. The existing arm worker uses the same serialized writer.

Member markers are buffered. Ordinary event writes and final close drain the
buffer; there is no added marker flush or fsync inside a measured member.
An interrupted member may therefore have a missing start/end until the
existing owner drains its buffer. Turnaround appends flush the driver handle
without fsync. Watchdog markers share the existing transition append/sync;
reason-only boundaries add no fsync. There are tens of markers per W1,
not sample-rate markers. Existing admission decisions, waits, batch sizes,
generated chains, episode records, thermal journals and scientific reducers
are unchanged.

## Offline reader projection

The pinned reader does **not** ingest generic markers directly. On an
authorized unblinded export, decode the explicitly named journals and call
`joulewise.timing_receipts.project(rows)`. It accepts plain JSONL records or
the member events' five-key `metadata` envelope and returns completed timed
documents plus diagnostics. Original integer stamps and brackets remain in
each document. Open, duplicate, reversed, cross-domain and cross-boot pairs
are not converted into completed intervals.

Pass completed documents through `reader_projection(documents)` before
feeding them as named `--span` records to the pinned reader's `read_window`.
This offline step partitions nested envelopes at observed wall boundaries:
for example, dwell refines arm, rather than becoming an equal-priority
conflict. Unrelated overlaps remain explicitly unattributed. Preserve both
diagnostic lists and the original pair documents alongside the reader
report; the projection does not invent monotonic stamps for wall-axis cuts.
Use the originals for the reader's elapsed-clock diagnostic. Unknown gaps
stay unknown. For native stage attribution, supply a separate stage-only
export to the legacy `--chain-journal` input, preserving the original mixed
journal alongside it: that reader otherwise warns about each standalone
boundary's absent timed-object fields. No runtime path calls either
projection function.

Push completion remains in the local driver journal. This change does not
broaden the structure-only courier's export or publish timing journals.
The custodian must explicitly export authorized R1/W1/D timing records later;
never export sealed Block 5 records. A push cannot include its own completion
receipt, and no recursive push is added.

## Verification and remaining integration

`tests/align/test_timing_receipts.py` requires **reader code only** from
`dc684b308` in the local Git object store (including CI); it never fetches
that dependency or silently skips the required integration check. Invented nested turnaround operations
reconcile to 647 seconds with zero unattributed wall in that reader. Other
tests cover malformed/open/cross-boot receipts, timeout/interruption,
emission failure, refused arm, G0 faults, overlapping OFF/dwell,
failed finalize, failed push then successful retry, and watchdog reason changes.
The measured-marker test instruments the real bundle callback and forbids
open, flush, fsync, process creation and thread startup during its emission.

The capture comparison runs the existing W1 synthetic capture path twice at
the same temporary root: markers disabled, then enabled. It compares every
file byte for byte, removing only added timing-boundary JSONL lines. With
`JW_WP22_FULL=1`, this includes every member and all existing fault injections.
The synthetic driver now supplies the existing battery-runner and clock
seams too, preventing host battery reads and nondeterministic battery stamps.
This compares receipt enablement at one source tree; it does not claim that
source/provenance digests equal those of an older registered source tree.

A final software-only overhead check wrote 2,000 markers to an already-open
`StringIO`: 20,165,875 ns total, approximately 10.1 microseconds per marker,
1,363,783 encoded bytes. Earlier runs took 11.4 and 19.3 microseconds per marker.
These are in-memory observations under concurrent host load, not a disk-I/O
or native-capture timing claim and not a speedup.
Test commands/results and the full touched-file list are in
`docs/run_reports/2026-11-08-timing-receipts.md`.

**Blocking integration:** the specified R16 cool-down evaluator is absent
from this checkout and the inspected `origin/main` ALIGN code. Its actual
operation must be wrapped using the existing owner's open writer and
`span('idle', 'cooldown')`, including its terminal/error path, once its owning
code/ref is supplied. The existing R1 `idle-until-soak` is not silently
substituted for R16. Manual harvest/backup/push work outside this driver still
needs its own existing Python owner's boundary calls; the reporting hand-off
is not evidence of downstream completion. No helper process was added to
the shell backup or frozen chain.

The qualification dwell source contains only monotonic stamps and boot ID;
these are retained in its projection receipt, without inventing wall stamps
or rerunning dwell. Its historical wall placement requires an authenticated
clock bridge. Direct calls outside a bound existing journal produce no new
journal. R0/R1-only insertion points and launch-capability barriers outside
the W1/D driver path are not expanded by this patch.

Consequently the synthetic completeness test proves the receipt geometry,
not completeness of all native/external turnaround sources. Lead next step:
supply/integrate R16 and external desk boundaries, run the native verification
outside this sandbox, complete the Opus review, then register every changed
capture dependency before W1. No live measurement or registration was run.

The existing native array qualification command is
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`.
It uses small synthetic streams and no model weights. Run it only outside
this no-Metal sandbox under lead-controlled machine-state conditions.
