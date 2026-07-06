# Project Status Review - 2026-07-06

Reviewer stance: independent project/status review. I first reviewed the
high-level docs (`README.md`, `PROJECT_STATUS.md`, `AGENT_PLAN.md`,
`TASK_QUEUE.md`, `RUN_STATE.md`, root docs under `docs/`, Phase 1/2
checklists and contracts) before inspecting source, tests, and verification
commands.

## Findings

### P1 - Reducer and validator do not fully type-check event timestamps

`BundleReader` parses event records but leaves field type validation to later
consumers. The measured-window and token/phase accessors cast `timestamp_s`
directly with `float(...)` (`joulewise/bundle_read.py:267`,
`:271`, `:294`, `:301`, `:307`). `reduce_bundle` only converts
`BundleReadError` and `_ReduceError` into structured failed summaries
(`joulewise/reduce.py:264-267`), so a malformed event timestamp can raise a raw
`ValueError` instead of producing a schema-valid failed summary.

I reproduced this by corrupting a completed mock bundle's `sampling_started`
timestamp to `"not-a-number"` and calling `reduce_bundle`; it raised:
`ValueError: could not convert string to float: 'not-a-number'`.

Related validator impact: `_check_events` accepts records with the right five
keys and then compares raw timestamp values (`joulewise/bundle_read.py:449-450`).
A nonnumeric or mixed-type timestamp can crash `validate_bundle` with `TypeError`
instead of returning an `invalid:` problem.

Suggested fix: make event parsing validate required field types centrally in
`BundleReader.events()` or a shared helper. Invalid timestamps should become
`BundleReadError` in strict readers and problem strings in
`BundleReader.problems()`. Add tests for nonnumeric, missing, bool, and
non-finite timestamps.

### P2 - `validate-bundle` can bless bundles whose derived metrics no longer match raw evidence

The current validator checks required artifacts, JSON parseability,
`config.json` re-validation, summary status/reason consistency, event shape,
event ordering, and only the CSV header for `power_trace.csv`
(`joulewise/bundle_read.py:349-356`, `:417-455`). It does not require that a
`succeeded` bundle still has a reducer-consumable measured window and summed
power curve, and it does not compare `summary_metrics.json` against a fresh
post-hoc reduction.

I reproduced two variants:

- Changing a succeeded bundle's `metadata.device.rail_manifest` to `[]` made
  `validate_bundle(bundle)` return `[]`, even though the report would omit the
  chart and a re-reduction would not have the same energy basis.
- Changing a succeeded bundle's `summary_metrics.json` `energy_request_j` to a
  nonsense value still made `validate_bundle(bundle)` return `[]`.

This is not urgent for the current mock slice, but it matters before Phase 5
dataset publication and any "all bundles intended for analysis pass
validate-bundle" gate.

Suggested fix: either broaden default `validate-bundle` or add a
`validate-bundle --analysis-strict` mode. For `status=succeeded`, it should at
least call `measured_window()` and `summed_curve()`, require enough samples for
the reducer, and optionally re-run `reduce_bundle` and compare derived fields
against `summary_metrics.json`.

### P3 - Raw-evidence immutability is documented but not enforceable for adapter writes

`RunBundleWriter.write_raw()` enforces no overwrite and no post-finalize writes,
but adapters receive only `RunContext.raw_dir` and write directly. The mock
telemetry adapter writes `raw/mock_samples.json` via direct `Path.write_text`,
which would overwrite if called twice in the same context. This is consistent
with the "context is data, not capability" decision, but it means the raw
immutability rule depends on every adapter remembering to check paths.

Suggested fix: add a tiny helper, for example `write_raw_artifact(context,
name, data)`, that validates plain filenames and refuses overwrites without
handing adapters the whole bundle writer. Use it in mocks and require future
real telemetry adapters to use it.

## What Is Good

- The documentation layer is unusually coherent. Status, queue, decisions,
  risks, phase plans, exit checklists, and contracts have clear ownership rules
  and mostly agree with each other.
- The project is correctly mock-first. The core harness, bundle writer,
  controller, reducer, report generator, CLI, and shared read layer are proven
  without spending hardware time.
- The Slice 2N hardening work addressed the right pre-hardware risks:
  `RunContext`, raw evidence preservation, marker-bounded measured windows,
  rail alignment failures, post-hoc reduction, schema round-trip stability, and
  shared bundle reading.
- The failure model is strong. Unsupported/failed outcomes produce complete
  bundles, and the controller catches unexpected runtime failures after bundle
  creation.
- The tests are broad for the current risk surface: controller lifecycle,
  reducer math, rail policy, bundle invariants, CLI exit codes, experiment
  manifests, report behavior, schema export, and mock adapters.
- Dependency discipline is clean. The core has no required third-party
  dependencies; `[analysis]` and `[mac]` are optional, and missing analysis
  dependencies fail with an actionable message.

## Current Project Status

Phase 1 remains open because the remaining gates need external evidence:
supervisor scope confirmation, wall-meter decision, calendar mapping, network
topology, NVIDIA/Orin access evidence, and a privileged Mac `powermetrics`
sample.

Phase 2 software-only work is in good shape. Slices 2A-2F, 2J, and 2N are
implemented and tested. The remaining Phase 2 tasks are appropriately gated:
D-016 model selection, MLX runtime, powermetrics telemetry, Mac vertical slice,
remote targets, and homogeneous baselines.

The next highest-risk repo task remains P0-002: define the measurement-corpus
backup protocol before first real measurement data. The next implementable
desk-work task is the related-work draft. Hardware work should wait for the
documented gates.

## Verification Performed

- `python3 -m unittest discover -s tests` -> `Ran 216 tests`, `OK`,
  `skipped=10`.
- `python3 -m joulewise validate-config configs/examples/mock_local.json` ->
  valid.
- `python3 -m joulewise validate-config configs/examples/mac_mlx_local.json` ->
  valid.
- Mock smoke run in `/tmp`: `python3 -m joulewise run ...` ->
  `status=succeeded`.
- `python3 -m joulewise validate-bundle <mock bundle>` -> valid.
- `python3 -m joulewise reduce <mock bundle>` -> `status=succeeded`.
- `python3 -m joulewise print-config-schema` and `print-output-schema` ->
  emitted JSON schemas.
- `python3 -m joulewise report <runs>` without `[analysis]` -> failed as
  expected with a message naming `pip install 'joulewise[analysis]'`.
- `git status --short --branch` -> clean on `main...origin/main` before this
  report file was added.

## Suggested Fix Order

1. Harden event type validation in `BundleReader` and `validate-bundle`.
2. Add strict analysis validation for succeeded bundles, including a re-reduce
   comparison or at least reducer-consumability checks.
3. Add a raw artifact helper for adapters and convert mock telemetry to use it.
4. Then proceed with P0-002 backup protocol and gated hardware evidence work.

## Bottom Line

The project is in a credible pre-hardware state. The architecture is well
factored, the docs are better than typical capstone handoffs, and the core
mock harness is demonstrably runnable. I would not start real measurement
collection until the validator/reducer timestamp hardening and the backup
protocol are closed, but the remaining issues are contained and fixable.
