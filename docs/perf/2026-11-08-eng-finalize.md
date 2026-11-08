# Finalize and custody hashing — eng-finalize

Branch: `perf/2026-11-08-eng-finalize`, based on `origin/main` at `c07b388e9`.
Authority: latency synthesis §4 rank 3; RUN_STATE 213–215; engineering only.
All execution used synthetic files. No network, model weights, measurement
pipeline or sealed data were used. Coordination state is unchanged.

Review follow-up: branch `fix-finalize` addresses F-L1/F-L2 from the
Opus cold review at `f551a6749`. F-M1 limits the performance claim: this
branch is **not on the R1/v4 lane**. Its relevant prospective v4 saving is
repeated terminal inventories of `night/` and `night/evidence/`; it does not
speed the large ALIGN archive/copy path. See the
[unapplied v4 port note](eng-finalize-port-to-v4-lane.md) for pinned code
evidence and a separate synthetic archive-inventory experiment.

## Change and equality boundary

- `joulewise/file_hashes.py`: 1 MiB streaming reads; bounded 1/2/4/8 threads,
  results and failures consumed in original input order. Readers are joined
  before return/error. No persistent digest sidecar or manifest format change.
- `scripts/run_night.py`: terminal inventories share hashes across result and
  courier publication within one CLI invocation. Newly written courier files
  and modified logs are hashed when discovered. Admission/gate hashes never
  use the cache. `run`, `rehearse` and `dead-man` accept `--hash-workers`.
- `scripts/harvest_window.py`: original source close and post-copy source
  inventories share hashes. Destination and existing-archive verification use
  fresh independent readers. Source/copy mismatch refusal, staging, lock,
  uninstall, fsync and atomic rename remain in their existing order.
  `--hash-workers` selects concurrency here too. Default is 1 in both tools.

Reuse is deliberately **operation-local**, keyed by path plus device, inode,
mode, link count, size, mtime_ns and ctime_ns for link and target. Before/opened/
after file identities are checked; failures never cache a digest. Same-length
rewrites with restored mtime invalidate through ctime; replacements invalidate
through identity. Reuse now requires Darwin `statfs` to identify APFS for
both link and target devices, and both observed timestamps to have
sub-microsecond components. Unknown or non-APFS volumes, failed detection,
and coarse-looking timestamps disable reuse; streaming and worker selection
still work, with fresh byte reads on every inventory. The timestamp test is
conservative: an APFS timestamp that happens to align to a microsecond also
loses reuse. This relies on ordinary filesystem metadata behavior for
already closed files, not a cryptographic proof of storage immutability.
Every new process/harvest and every destination authentication reads all bytes
again. Reuse across restarts would require an authenticated immutable-object
contract; trusting a persisted size/mtime cache would weaken custody.

Harvest manifests retain exact sorted JSON bytes, digests, modes, sizes,
timestamps and literal symlink text. Night artifacts retain their existing
ordering, missing-file omission and unreadable-file diagnostic behavior; their
historical symlink-target policy is unchanged. A file detected changing while
being hashed gets an initial attempt plus up to three retries, with 10/20/30 ms
backoffs and fresh fingerprints/digests. Persistent mutation fails closed
with `OSError` naming the file; the night inventory keeps its path and error
entry, and publishes no digest for it. Missing files, ordinary read failures
and interruption are not retried. Uncached admission hashes use the same
stable-snapshot retry policy. No failed attempt populates the cache.
No claim is made that arbitrary concurrent mutation has byte-identical race
timing to the old whole-file read.

F-L3 remains a documented limitation: interruption that unwinds the worker
pool joins in-flight readers before returning, so it can wait for whole-file
reads (and bounded mutation retries). Cooperative cancellation would require
a separate change; no reader is abandoned here. F-L4 is documented and tested:
an unrelated new thread does not inherit `hash_scope` and gets a fresh
instance. Do not globalize the cache to remove that harmless loss of reuse.

The existing Git copy/commit/push sequence and raw-log disclosure filter are
unchanged. Tests mock that transport. Compression, cloud confirmation, second
copy requirements and deletion authority are untouched. No push-time saving
has been measured. This change does not alter Block-5 harvest or analysis.

## Synthetic timing

Command: `python3.13 -B scripts/benchmark_finalize_hashes.py --files 32 --mib 8 --passes 3 --repeats 3`.
32 closed files, 256 MiB total; medians of three runs. The three passes model
close plus two repeated inventories; each optimized trial gets a new cache.
The benchmark compares **exact canonical manifest bytes on every pass**.
Page-cache warmth is uncontrolled (generated files are warm); these are local
synthetic timings, not an MBP/SSD or production turnaround qualification.

| Mode / workers | Close, s | Two later passes, s | Three-pass total, s |
|---|---:|---:|---:|
| Original serial `read_bytes` | 0.195208 | 0.396904 | 0.599074 |
| Streaming + incremental / 1 | 0.205460 | 0.003635 | 0.208397 |
| Streaming + incremental / 2 | 0.125109 | 0.008735 | 0.135789 |
| Streaming + incremental / 4 | 0.059729 | 0.008246 | 0.067971 |
| Streaming + incremental / 8 | 0.047019 | 0.009899 | 0.057458 |

Each column is an independent median, so column medians need not add up.
All 45 inventories were byte-identical. Eight workers gave about 10.4× less
three-pass hashing wall time here; even one worker avoided the duplicate reads.
One-worker first-close overhead increased slightly because of identity checks.

## Verification

Tests ran one command at a time, about 6.6 minutes total unittest wall time
including baseline checks and reruns. The full repository suite was deliberately
not run because the brief reserves the machine for its blinded analysis job.

- Tests were authored before implementation. First
  `python3.13 -B -m unittest tests.test_finalize_hashes` failed importing the
  missing new module; final run: **13 passed**, 0.274 s. Covers exact manifests,
  symlinks/hardlinks, restored-mtime corruption, missing files, mid-read
  interruption/replacement, bounded readers, ordered errors, incremental
  publication, CLI cache scope and uncached admission reads.
- `python3.13 -B -m unittest tests.test_harvest_window`: **39 passed**,
  42.089 s on the final implementation. Complete delivered tree equality
  against the original serial inventory at all four worker counts; source
  rewrite, copy corruption, missing copy, hash/copy interruption, publication
  failure, retry and uninstall ordering are covered.
- `python3.13 -B -m unittest tests.test_run_night`: 292 tests, 185.905 s;
  3 failures, 1 error, 9 skips. One failure was an old `read_bytes` fault
  injection bypassed by streaming; it now injects read-only `Path.open`.
  The other three failures are the native process-group cases below.
- Targeted driver rerun:
  `python3.13 -B -m unittest tests.test_run_night.CourierDeliveryBoundaryTests tests.test_run_night.NightDriverTests tests.test_run_night.EvidenceProbeTests tests.test_run_night.Ruling76DriverTests`:
  179 tests, 77.384 s, one test-fixture error (the new open hook also blocked
  fixture writes). The other 178 passed. After restricting the hook to reads,
  `python3.13 -B -m unittest tests.test_run_night.CourierDeliveryBoundaryTests`:
  **19 passed**, 11.639 s. No production repair was needed for either injection.
- The three native failures reproduced with **unchanged** `origin/main`
  driver source loaded from an owned temporary file under `scripts/`, removed
  afterward: 3 tests, 32.312 s, the same 2 failures and 1 error. They are
  `HazardPackPrimitiveTests.test_dead_man_stops_the_hazard_monitor_a_dead_driver_left_running`
  (child wait timed out), `test_natural_exit_census_proves_survivors_gone_before_recording_the_exit`
  and `test_supervision_stop_terminates_the_group_and_returns_its_refusal`
  (termination not proven). This establishes a baseline/environment limitation;
  the exact OS/sandbox cause was not investigated. Lead must run
  `python3.13 -B -m unittest tests.test_run_night.HazardPackPrimitiveTests`
  outside the sandbox before treating native process handling as verified.
- Targeted `python3.13 -m compileall -q` on the seven changed Python files and
  `git diff --check`: passed. Python 3.11 was not executed here; new code uses
  only stdlib APIs available on 3.11/3.13.

## Magistrate: next exact step, in a gap

Run this read-only command against a deliberately selected **closed record
tree**, after measurement has ended, before the next quiet dwell:

```sh
python3.13 -B scripts/benchmark_finalize_hashes.py \
  --closed-root "$CLOSED_WINDOW_RECORD_ROOT" \
  --workers 1 2 4 8 --passes 3 --repeats 3
```

The variable is an operator-supplied path, not a default study-data location.
The script reads that tree and emits counts, timings and equality; it does not
write it, analyze outcomes, push, copy or delete evidence. It cannot itself
establish that the machine is in a gap or that the tree has closed. Use an
authorized non-study engineering record if the selected tree is still sealed.

Record first-pass and repeat times separately, SSD/cache condition, filesystem,
file count/bytes and contention. Choose the fastest bounded worker count from
that MBP evidence; eight workers may lose on one SSD. Separately time actual
finalize, one copy/compression, independent destination re-read, commit and
server-confirmed push plus required second copy. Those phases and quiet-state
recovery can dominate and must not be credited to hash-only speedups.
Installed launchd argv is unchanged and therefore stays at one worker; opting
an installed invocation into a different count is a magistrate integration step.
No MLX code changed or MLX execution is needed for this lane. Native MBP
filesystem/transport timing remains the required outside-sandbox check.

## Handoff and files

Implementation: `joulewise/file_hashes.py`, `scripts/run_night.py`,
`scripts/harvest_window.py`. Benchmark: `scripts/benchmark_finalize_hashes.py`.
Tests: `tests/test_finalize_hashes.py`, `tests/test_harvest_window.py`,
`tests/test_run_night.py` (fault injection moved to `Path.open` to cover
streaming). This report and its run-report pointer complete the handoff.

No scientific ruling is requested. Remaining uncertainty is production I/O,
transport latency and worker selection; no 2–5 minute finalize or 30–45 minute
turnaround claim is established by these synthetic results.
