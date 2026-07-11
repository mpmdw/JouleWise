# NV-GATE-2 Accepted-Findings Fix Round

Date: 2026-07-10
Branch/worktree: `impl/nvgate2-codenow`
Lane: `[AGENT]`; no live NVIDIA or quiet-machine measurement was performed.
Authority: lead-accepted findings in `rev-nvgate2.md`.

## Planning audit

The exact goal was to close FIX-1 through FIX-5 plus FIX-NW-FAKE and
FIX-NV5-FAKE, after integrating current main and the pending P2-040 reducer
dispatch. Intake covered the active stop card, current queue, M0, orchestration
rules, the source-of-truth map, the original NV-GATE report, and the full review
packet. The inherited constraints were: preserve PROVISIONAL hardware labels,
perform no quiet-machine work, make no commits, keep the 80 ms NV-5 request,
and preserve the union of state/queue bookkeeping. Passing focused and
canonical tests, the PID-reuse mutation, real stubborn-child tests, exact
artifact maps/bytes, strict-version fixtures, and three consecutive historic
flake runs were the acceptance evidence.

## Integration source and conflict resolution

- `origin/main` was integrated first. Its content conflicted only in
  `RUN_STATE.md`; that file was resolved as a union and `TASK_QUEUE.md` merged
  automatically.
- The post-main tree did not contain `ADDED_SINCE_0_3_0` or the 0.3.1 reducer
  dispatch. Per the review contract, the dispatch therefore came from
  `origin/impl/p2040-remainder`.
- The sibling integration conflicts in `RUN_STATE.md`, `joulewise/reduce.py`,
  and `joulewise/schemas.py` were resolved as semantic unions: both cleanup
  quality fields remain in `MeasurementQuality`, both are emitted by the
  reducer, and both are present in the output schema.

The managed sandbox could read but not write the shared Git worktree metadata
under `/Users/edr/code/JouleWise/.git/worktrees/nvgate2`; direct `git merge`
failed before changing files at `ORIG_HEAD.lock`. The exact no-commit merge was
therefore materialized and conflict-resolved through a writable shadow Git
directory in `/private/tmp/nvgate2-merge-shadow` against this worktree. The
working-tree content is the resolved integration, but the real branch has no
`MERGE_HEAD`/merge ancestry. The lead must recreate or record the merge in an
unrestricted Git session before landing.

## Per-FIX status

- **FIX-1 — complete.** Uncached cleanup preserves the original pidfile
  fingerprint through the SIGTERM wait, pre-SIGKILL validation, and final
  survival decision. Command/start mismatch means the original exited, so no
  SIGKILL or demotion occurs. Cached processes use `Popen.poll()`. The mutation
  test changes start identity after SIGTERM and proves only SIGTERM was sent.
- **FIX-2 — complete.** `measurement_quality.remote_cleanup_failed` and
  `measurement_quality.runtime_cleanup_ok` are both in the schema and
  `ADDED_SINCE_0_3_0`. A pinned 0.3.0 summary lacking both passes strict;
  current 0.3.1 summaries lacking either fail.
- **FIX-3 — complete.** A real child ignoring SIGTERM reaches SIGKILL under the
  same fingerprint and, with SIGKILL deliberately suppressed, makes the real
  worker emit `cleanup_failed`. A real fake NVIDIA child exercises actual
  `start_sampling`/`stop_sampling` and the same survival path.
- **FIX-4 — complete.** NV-5 now invokes real NVIDIA start/stop handlers and
  asserts exact logical maps for `nvidia_smi_pidfile` and `nvidia_smi_csv`,
  plus collected pidfile and CSV bytes. The managed sandbox still loudly skips
  this localhost acceptance gate.
- **FIX-5 — complete.** Accepted streaming with an untouched usage accumulator
  performs no retry and records `stream_chunk_fallback`, two SSE chunks, and
  `record_unit=sse_chunk`. A controller-to-reducer test proves null per-token
  metrics and an ineligible per-token claim.
- **FIX-NW-FAKE / FIX-NV5-FAKE — complete.** Both fakes use a shell emitter to
  write five parseable rows before the first sleep, removing Python-interpreter
  startup from readiness. The 80 ms NV-5 request is unchanged.

## Verification

Pre-change canonical failing-first evidence:

```text
Ran 922 tests in 33.731s
FAILED (failures=1, skipped=13)
failure: test_telemetry_measure_idle_with_fake_nvidia_smi
```

Focused node-worker/subprocess/controller/reducer/schema surface:

```text
Ran 229 tests in 4.995s
OK (skipped=2)
```

The historic fake-sampler test then passed three consecutive fresh-process
runs. Final canonical suite:

```text
Ran 1022 tests in 34.406s
OK (skipped=13)
```

`python3 -m py_compile` on changed Python surfaces and `git diff --check` were
clean. The skips include the loud retained-corpus gate and the loud NV-5
localhost denial; no live hardware claim was made.

## Deviations and next step

- The only implementation deviation is the shadow Git metadata workaround
  described above. Content integration and conflict unions are complete; real
  merge ancestry is not recorded because the sandbox cannot write the shared
  worktree metadata.
- The real-process tests use actual stubborn subprocesses. Their identity
  sensor values are pinned in-process because this sandbox denies reliable
  process inspection; signal delivery and survival are real, and SIGKILL is
  suppressed only to make the survival/demotion branch observable and safely
  asserted.
- NV-5 remains unexecuted here because localhost bind is denied. The lead's
  next exact step is to recreate/record the two merges in order (main, then
  P2-040 remainder), inspect this diff, run NV-5 where localhost is permitted,
  and only then land. Hardware promotion remains gated by P1-006.
