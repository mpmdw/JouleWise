# Air offload implementation — 2026-11-08

Task: prepare MBP-push/Air-SSD option 2 for the unattended v4/v5 loop, using
only synthetic evidence in this blinded clone. Branch:
`ops/2026-11-08-air-offload`, initially clean at `origin/main` (`8fb75b316`).
Implementation commit: `5e870361b20e` — **Add verified MBP-to-Air offload and
second-copy retention**. This report is committed separately. Nothing pushed.

## Delivered

- `scripts/offload_to_air.py`: stdlib-only `push`, forced-command `serve`, and
  Air-only `backup-once`. Injected command execution; resumable/checksummed rsync;
  SHA-256 manifest/inventory verification; immutable publication; fresh
  challenge-bound hashed receipts over pinned SSH; durable background jobs and
  deletion journals; recovery from interrupted transfer/deletion.
- `tests/test_offload_to_air.py`: 35 tiny synthetic tests, including fake
  transport, corrupt/missing/extra files, partial/wrong receipts, lost receipts,
  duplicate calls, armed/terminal refusals, shared locks, deadline/state changes,
  symlinks/escapes, backup failures, disk pressure and two-copy-only deletion.
  Also real local Python subprocess tests for the CLI and process-group cleanup,
  including a surviving grandchild after its direct parent exits.
- `docs/ops/AIR-OFFLOAD.md`: one-time Air Remote Login/key/rrsync/worker setup,
  exact magistrate lock/lease interface, invocation, failure/retention policy,
  receipt semantics, timing estimates and deployment rehearsal checklist.
- `CANONICAL.md`: one tool-map row, explicitly PROVISIONAL.
- This run report. No coordination-state files changed or kernel tasks registered.

A one-copy Air receipt queues the second copy and leaves the MBP record intact.
Only a fresh two-copy receipt plus matching local verification permits removal.
Disk pressure can hold the next arm, and never relaxes the copy requirement.
The second-disk implementation is the chosen allowed alternative to iCloud;
there is no claim that an iCloud upload queue proves server persistence.

The new cool-down lease and native watchdog `fenced_checkouts` are both checked.
The lease attests completed commit/push; this tool performs neither. The caller
must serialize all arm/measurement/dwell transitions with the same stable lock.
Budget admission includes five worst-case checksum/hash passes; process alarms,
monotonic deadlines and transport-group cleanup bound normal cancellation.

The existing SSD-P1 manifest was inspected **from Git code objects only** at
`origin/align/2026-11-08-ssd-hooks` (`a9261df4ddaa`),
`scripts/ssd_permanent.py`. Its `ssd-closed.json` /
`joulewise.ssd_closed_record.v1` shape is supported directly and is the CLI
default, so the two storage options can use the same closed envelope. Also
supported: the explicit sized `joulewise.closed_record.v1` envelope and the
existing `joulewise.harvest_window.v1` archive inventory. Absolute source paths
inside a harvest are ignored, never followed. Unknown schemas refuse.

## Verification

Final code checks:

```text
python3.13 -B -m unittest tests.test_offload_to_air
Ran 35 tests in 1.969s — OK

python3.13 -B -m compileall -q scripts/offload_to_air.py tests/test_offload_to_air.py
exit 0

git diff --cached --check
exit 0 (before implementation commit)
```

Earlier focused iterations also passed after their changes; total test execution
was seconds, well below the 20-minute limit. No full/quick suite or unrelated
test modules were run, per the explicit instruction protecting the ongoing
8-worker blinded job. Python 3.11 was not on PATH and was not tested; CI still
owns that version check. No MLX or model code changed, so no native MLX tests
apply. Git hooks were disabled for these local commits to avoid unrequested
hook activity; no signing, network or integration installation was performed.

Distinct-device success cases use **explicitly mocked device IDs**. The
unmocked test with two directories on the same real filesystem refuses. These
are fixture results, not physical-disk or live SSH evidence. No real network,
SSH host, measurement pipeline, model download, hardware probe or study data
was used. No forbidden custody path was opened or searched.

## Timing and remaining gates

Ideal transfer-only times for 18.6–26.4 decimal GB:

| Rate | Seconds | Minutes |
|---|---:|---:|
| 50 MB/s | 372–528 | 6:12–8:48 |
| 100 MB/s | 186–264 | 3:06–4:24 |
| 300 MB/s | 62–88 | 1:02–1:28 |

These exclude verification. At the default conservative 100 MB/s hash estimate,
five passes plus 30-second overhead make total admission estimates 22:12–31:18,
19:06–26:54, and 17:02–23:58 respectively. Actual sustained rates and available
cool-down duration are unmeasured. Offload must overlap cool-down and finish
before a fresh full dwell; a short budget refuses, never consumes dwell.

**Next exact step:** the lead wires this hook's stable shared lock and fresh
lease into the actual magistrate arm/dwell transitions, provisions the Air
account/forced key/rrsync and independent backup destination, then conducts the
operator doc's **unarmed synthetic** end-to-end rehearsal. These deployment
steps were intentionally not attempted under the no-network/no-hardware brief.
Until then the implementation is PROVISIONAL and must not be treated as an
installed interlock or a demonstrated unattended cadence.

Other limits/uncertainties: different filesystem IDs are checked, but physical
disk independence is an owner setup fact (two APFS volumes on one SSD do not
qualify). Receipts are hashed and SSH-authenticated, not offline digital
signatures. A stuck kernel I/O call has no strict real-time interruption
guarantee; the magistrate must await actual hook/transport exit before dwell.
No unresolved science/registration decision was taken. The lead retains the
production, hardware, integration and merge gates; this run made local commits
only and did not alter `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json` or `tests/test_gen_state.py`.
