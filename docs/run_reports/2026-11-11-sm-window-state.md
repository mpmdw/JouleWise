# sm-window-state — 2026-11-11

Built the new read-only shadow module and its synthetic unittest module.
Work stays on `feat/2026-11-11-sm-window-state`. No writer or existing import
was changed. No network, host connection, model download, measurement pipeline,
real custody or results/records ref was used. Coordination files were preserved
as instructed by the seat brief. There was no active stop card at intake.

## Sources and changes

Read the specified audit sections, including sections 0, 4.1, 4.2, 4.6, 7 and 8,
and the state-machine lane plan through their remote-tracking refs. Read
`run_night.py`, watchdog and hazard-driver code on both `origin/main`
(`54eb4ba30`) and `origin/align/2026-11-08-v4-r11` (`b4a6c217f`). Also inspected
the installer, plan writer, W1 R1 payload writer and W1 program courier.
The historical tests reconstruct structural facts from the audit descriptions.
They contain no copied study records or outcomes.

Files:

- `joulewise/window_state.py`: enums, frozen observation/plist facts, pure state
  derivation, one outcome implementation, eight named invariant checks, safe
  observer and standalone CLI. The module docstring maps states to markers and
  their writers on both generations.
- `tests/test_window_state.py`: 32 tests. Tables cover all 14 lifecycle states
  and six outcomes. Tests cover both record generations, both historical
  failures, each invariant passing/failing, tri-state plist facts, deadlines,
  payload locations, exit contracts, malformed records, conflicting records,
  symlinks and read races. A fixed seed samples 252 marker subsets, including
  the empty/full sets. No subset without `chain.started` can measure.
- `CANONICAL.md`: one tool-map row.
- `scripts/test_timings.json`: exactly one alphabetically inserted line.
  The 1.7-second value is a local scheduling hint, not hardware evidence.
- This report.

## Decisions and limits

`GO` is arm admission. It never overrides a nonzero chain exit, a missing start
marker or an incomplete payload. Contradictory/malformed structural inputs
return `UNKNOWN` with stable diagnostics. Unknown vocabulary never grants
measurement success. Explicit `ABORTED` remains an abort. A recognized
non-complete payload with exit zero is `CHAIN_FAILED`. A complete payload with
missing slots is `MEASURED_WITH_FLAGS` and carries the slots invariant.

The default exit success is zero. The optional mapping has the closed words
`complete`, `refused`, `aborted`, `failed`, `stopped`. Undeclared codes fail.
Unknown words return `UNKNOWN`. Declaring a nonzero code `complete` cannot
make it measured. No result is cached.

Only the observer reads files. It uses anchored descriptors, a fixed allowlist,
regular-file checks and no-follow opens for every path component. It rejects
even internal symlinks. It does not enumerate custody or follow paths from
records. Explicit payload paths are allowed and receive the same checks.
R1 defaults cover adjacent files and W1's `night/align-r1/` layout. Slots files
are checked for existence only. Duplicate JSON keys and oversized records
(over 4 MiB) fail closed. Reports omit arbitrary fault text, measured fields,
message IDs, paths from records and exception messages.

W1's structured git-push receipt counts as recorded delivery. Legacy mail IDs
also count. A bare `sent: true`, a courier filename, or `transport: file` alone
does not prove delivery. The observer accepts an explicit optional plan
`courier_mode: file-only` declaration; neither inspected writer emits this
declaration today. Callers can also supply the observation's delivery waiver.
Receipt validation is structural. It does not verify a remote ref or recompute
the receipt's result digest.

Completion uses the writers' `t0 + window_max_s + 300` deadline. Without plan
timing, `result.ended_epoch_s` is the fallback. Stranded requires a result,
delivery/waiver, and a retained label strictly later than completion + 3600.
The loaded-label invariant also warns when delivery is still owed; that case
stays `DeadmanTail` under the seat's explicit Stranded definition.

States that files alone cannot fully prove:

- `Installed`: custody has no authoritative loaded-label receipt. Both loaded
  facts must be supplied by the caller. Disk presence alone is insufficient.
- `Uninstalled`: there is no durable uninstall marker. It is inferred only
  with a terminal marker and both labels explicitly absent and unloaded. This
  proves current absence, not that an installation occurred historically.
- `DriverStarted`: census/admission records prove the driver ran, not that it
  remains alive. There is no separate driver-started marker.
- `DeadmanTail`: a failure record or expired completion deadline shows delivery
  is owed, not that a dead-man process is currently running.
- `LaunchAbandoned`: elapsed time cannot supply the watchdog's process-census
  proof. The durable abandonment marker is required.

`ChainUnkilled` and an open chain outrank later terminal/delivery markers until
an exit marker provides closure. Neither cleanup nor label removal is attempted.

The eight checks cover GO/start, exit/start, nonzero/fault, payload/exit,
slots/exit, courier/delivery, courier/result and retained labels. The other
audit 8.3 lines need facts outside this observation: host settings/lock holders,
watchdog dry runs, offload queue/receipts, series finality, harvest journals,
analysis admission/commit identity, and coordination freshness. They are not
silently treated as satisfied. No live or MLX validation is claimed.

## Verification

All test modules ran individually. No full suite ran.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_window_state` | Final: 32 tests, 1.248 s, OK. Earlier 27-, 30- and 31-test iterations also passed. |
| Standard-library `sys.settrace` diagnostic over `tests.test_window_state` | 30 tests, 1.523 s, OK. Identified one unvisited post-open file-type guard; added the directory-replacement race test. This was not a mutation test. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | 14 tests, 0.156 s, OK; two existing live `ps` tests skipped by the sandbox. |
| `python3.13 -B -m unittest tests.test_gen_state` | 44 tests, 3.136 s, OK. No coordination source was edited. |
| `python3.13 -m compileall -q joulewise tests scripts` | Exit 0. |
| `git diff --check` and staged diff review | Clean; only the five listed paths. |

Purity tests replace OS/clock access and subprocess modules with raising guards,
and patch `Path.exists`, `Path.open` and `open` to raise. Observation tests guard
against write flags, subprocesses and sockets and compare source bytes before
and after reading. All pass. Fixtures live only in temporary directories.

## Handoff

No blocking questions. Python 3.11 was not available on PATH. The lead should
run `python3.11 -B -m unittest tests.test_window_state` in a permitted environment
and rerun the two existing live census tests where `ps` is allowed. No new
native MLX test is needed for this standard-library module. Cold lane review
remains with the lead before any PR. No commit was pushed.

The implementation and this report are committed together with message
`Add read-only shadow window lifecycle and outcome classifier`.
