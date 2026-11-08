# eng-bytesexport handoff — 2026-11-08

Branch: `perf/2026-11-08-eng-bytesexport`.
Code commit: `8066b1783` — `perf(bytes): bound export verification and cache immutable reads`.
Base/oracle: `912cf8c3a998b5d9d82c6b96e215871cf21288f4` (PR #701 lane).
Local commits only; nothing pushed or deployed.

Profile, timings, reproduction commands, limitations and the D9 placement
answer: [engineering report](../perf/2026-11-08-eng-bytesexport.md).

Final paired synthetic medians: compressed 16-reference/7-science export
3.055 → 1.892 s (4 workers); compressed 16-reference/128-science export
10.016 → 6.289 s; plain 16-reference/7-science export 0.677 → 0.278 s.
CSV, sidecar and withheld-store output bytes matched the original exporter
exactly. Production and Air duration remain unmeasured.

## Changes and authority

Implemented bounded source-verification workers, streaming SHA-256 over logical
plain/zstd bytes, a lexical inventory index, export-local successful-read reuse,
and one parsed compression journal per export. Key operations and publication
remain serial; worker results preserve serial refusal order. Default is one
worker, with opt-in `--read-workers 1..8`.

Changed files:

- `joulewise/b6/export_runs.py`
- `joulewise/desk_restore.py`
- `scripts/b6_export_runs.py`
- `scripts/profile_bytes_export.py`
- `tests/b6/export_profile_support.py`
- `tests/b6/test_export_read_workers.py`
- `docs/perf/2026-11-08-eng-bytesexport.md`
- this handoff

M0 intake found no active stop card or global gate. This explicit [AGENT]
engineering brief overrides ordinary queue selection. Per Ed's standing rules,
no kernel task was registered and `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, and `tests/test_gen_state.py` were preserved.
The estimator, manifest and registration are unchanged. No delegated agents,
network, real archives, external user paths, model weights or sealed outcomes
were used. The existing analysis job was not operated on.

## Verification

Commands ran one unittest invocation at a time with `PYTHONNOUSERSITE=1`:

| Command after `python3.13 -B -m unittest` | Result |
|---|---|
| `tests.b6.test_export_read_workers` | 13 tests, OK, 9.312 s |
| `tests.b6.test_export_runs` | 55 tests, OK, 5.870 s; baseline also OK (9.027 s) |
| `tests.test_restore_run_to_scratch` | 19 tests, OK, 1.266 s; 2 skipped |
| `tests.test_desk_compressed_readers.CompressedReaderTests.test_archive_json_and_export_events_read_the_compressed_sibling` | 1 test, OK, 0.520 s |
| `tests.test_bytes_stage1` | 16 tests, OK, 49.296 s; executed with a 180 s subprocess timeout and private synthetic TMPDIR |

`PYTHONNOUSERSITE=1 PYTHONPYCACHEPREFIX=/private/tmp/bytes-export-pycache python3.13 -m compileall -q joulewise tests scripts/b6_export_runs.py scripts/profile_bytes_export.py`
passed. `git diff --check` and staged diff checks passed.

The broader `tests.test_desk_compressed_readers` invocation was interrupted,
not counted as green: two tests completed, then its synthetic native-shaped
instrument-calibration/refit fixture was still running. Ctrl-C was sent only to
that tool session to bound test time; a process-list-based interrupt attempt
was denied by the sandbox. No assertion failure was observed before the
interrupt. The focused compressed-export test above replaced that broad run.
No full suite was run, per the explicit machine-load instruction. Python 3.11
and native MLX were not run here; no MLX code changed.

Failing-first evidence: the new module failed before the read-worker API
existed; exact oracle comparisons then caught a missing-file refusal text
difference, corrected before final checks. The journal-dedup test independently
failed `3 != 1` before the journal cache was added. Final tests cover byte
identity of CSV/sidecar/withheld output at 1/2/4 workers, preserved key/archive
bytes, bounded streaming, invalidation, malformed/corrupt inputs, worker overlap,
first-refusal identity and caller-thread-only key/publication operations.

## Open points and next exact step

The Air can perform stage-1 desk work after a complete approved closed-input
handoff; CSVs alone are insufficient. Archive rereads/refits remain necessary
on the Air. Absolute compression-journal paths, thermal-view symlink sources,
existing group keys/session bindings/withheld stores and a single writer must
be retained. This run neither authorizes nor performs a key transfer.

Next: lead reviews these two local commits, confirms the Air copy's custody
owner and path layout, then validates native powermetrics-backed synthetic
archive parity at 1/2/4 workers on the non-measuring host
before adopting the optimization. Also run the interrupted native-shaped
`tests.test_desk_compressed_readers.CompressedReaderTests.test_bundle_read_reduce_strict_validation_and_survivor_screen_are_identical`
outside this sandbox's time budget and the normal CI
checks. Keep the registered estimator/run-checkout selection from the owning
stage-1 plan. Production duration and Air throughput remain unmeasured.
