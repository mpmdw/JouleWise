# NV-GATE-2 CODE-NOW Implementation

Date: 2026-07-10
Branch/worktree: `impl/nvgate2-codenow`
Authority: `docs/specs/c027/nv-gate-2_live_promotion.md`, amended by
`docs/specs/c027/ADJUDICATION.md`
Lane: `[AGENT]`; no live NVIDIA measurement or quiet-machine work performed.

## Baseline

Before edits:

```text
python3 -m unittest discover -s tests
Ran 910 tests in 32.549s
OK (skipped=12)
```

## Implemented units

- NV-3: `cli.py` now dispatches strict raw-to-trace checks through a
  per-telemetry-backend registry. Powermetrics and NVIDIA have real verifiers;
  mock has an explicit registry exemption; unregistered production backends
  fail strict with a named error. NVIDIA re-derivation shares the adapter's
  parser, node-time offset, controller clock alignment, source, and rail logic.
- NV-1: streamed vLLM completions request `include_usage` first. Terminal
  `usage.completion_tokens` wins and is labeled `server_usage`; explicit
  unknown-field rejection retries once without the field and labels the result
  `stream_chunk_fallback`. Chunk rows are labeled `record_unit=sse_chunk`.
  Reducer per-token metrics are nulled and the per-token claim gate is
  ineligible for fallback counts.
- NV-4: the node client ingests collected flat artifacts before deleting local
  staging, cleans remote task/run directories, and accumulates cleanup rows.
  File/directory failures remain succeeded with
  `measurement_quality.remote_cleanup_failed`; any surviving worker-started
  vLLM or sampler process reports `cleanup_failed` and demotes the run.
- NV-5: `tests/test_node_worker_subprocess.py` drives the real shipped worker
  through `NodeWorkerClient` with fake vLLM and nvidia-smi executables and
  asserts logical/physical artifact-name parity, SSE-chunk token output,
  usage-source metadata, telemetry artifact collection, and cleanup. The test
  is normally always-on; a localhost socket denial prints a loud acceptance-
  gate message before skipping.

NV-2 was already merged and was not changed.

## Focused verification

```text
python3 -m unittest tests.test_cli_run tests.test_node_client \
  tests.test_node_worker tests.test_node_worker_subprocess \
  tests.test_nvidia_node_integration tests.test_vllm_runtime \
  tests.test_reduce tests.test_controller tests.test_schemas
Ran 232 tests in 6.085s
OK (skipped=2)
```

The NV-5 test printed:

```text
NV-5 ACCEPTANCE GATE SKIP: localhost sockets unavailable; real client-worker
subprocess parity was not exercised (PermissionError: [Errno 1] Operation not permitted)
```

Final canonical suite:

```text
python3 -m unittest discover -s tests
Ran 922 tests in 33.551s
OK (skipped=13)
```

The first final-suite attempt exposed two stale amplification-test transports
that rejected the newly expected remote cleanup command. The fake transport
was extended to execute `rm -rf -- <paths>`; both failures passed focused, and
the full suite above is the clean rerun.

## Deviations and live fence

- The prompt allowed a guarded NV-5 skip, while the adjudicated spec prefers
  always-on. This environment denied localhost bind, so the narrow documented
  fallback fired loudly; the test remains always-on where the probe succeeds.
- No live SSE transcript, non-streamed twin, NVIDIA bundle, process listing, or
  protocol de-provisionalization was claimed. NV-GATE-2 live rows 16–20 remain
  open for the lead-controlled first-contact session.
- No commit, push, merge, deployment, or hardware operation was performed.
- During the interrupted session `origin/main` advanced, leaving this branch
  eleven commits behind at final audit. No rebase/merge was attempted because
  the user requested completion of the bounded worktree diff for lead landing.

## Next exact step

The lead should review and land the bounded paths, run NV-5 in an environment
that permits localhost sockets, then execute the live-promotion checklist only
when P1-006 access is available.
