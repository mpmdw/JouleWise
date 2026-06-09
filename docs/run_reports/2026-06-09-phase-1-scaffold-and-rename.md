# 2026-06-09: Phase 1 Scaffold And JouleWise Rename

## Context

The project began from an empty Git repo plus a Word document. The user wanted
the research and implementation plans turned into an agent-friendly local repo,
then wanted the project renamed from the temporary EnergyBench identity to
JouleWise as a nod to JouleSort and Splitwise.

## What I Did

- Created `AGENT_PLAN.md` with a phase-by-phase checklist and acceptance
  criteria.
- Created Phase 1 docs:
  - Measurement methodology.
  - Run-bundle layout.
  - Adapter contracts.
  - Hailo feasibility checklist.
  - Instrumentation checklist.
- Added the `joulewise` package with:
  - Draft typed schemas in `joulewise/schemas.py`.
  - Adapter protocol contracts in `joulewise/interfaces.py`.
  - CLI helpers in `joulewise/cli.py`.
- Added example configs for:
  - Mock-local validation.
  - Mac-local MLX + powermetrics vertical slice.
- Added tests for:
  - Config validation.
  - Summary-output validation.
  - Adapter protocol satisfaction.
  - CLI commands.
- Renamed the project identity to JouleWise:
  - Package: `joulewise`.
  - CLI: `python3 -m joulewise`.
  - Project metadata: `pyproject.toml`.
  - README, docs, tests, and config metadata.
- Added `.gitignore` for Python caches, virtualenvs, and future run bundles.
- Committed and pushed the initial scaffold.
- Added `RUN_STATE.md` and `docs/run_reports/` so future runs have a durable
  "what I did and what is next" handoff.
- Audited the Phase 1 plan and found that the remaining items were too
  checklist-shaped.
- Added `docs/planning_reflection_protocol.md` so every future phase or major
  step starts with an evidence/assumption/acceptance-criteria review.
- Added `docs/phase_1/phase_1_exit_checklist.md` to turn the remaining Phase 1
  work into explicit evidence gates.
- Added `docs/phase_1/network_plan.md` to make interconnect planning concrete
  before Phase 3.

## Verification Performed

Unit tests:

```bash
python3 -m unittest discover -s tests
```

Result:

```text
Ran 14 tests
OK
```

CLI smoke test:

```bash
python3 -m joulewise validate-config configs/examples/mac_mlx_local.json
```

Result:

```text
valid config: configs/examples/mac_mlx_local.json target=macbook_m3_max runtime=mlx telemetry=powermetrics
```

Schema smoke test:

```bash
python3 -m joulewise print-config-schema
```

Result: emitted a JSON Schema titled `JouleWise BenchmarkConfig`.

## Git State At End Of Run

- Commit: `6a11142 Initialize JouleWise benchmark scaffold`
- Branch: `main`
- Remote: `origin git@github.com:mpmdw/JouleWise.git`
- Push: succeeded to `origin/main`

Important caution:

- The working tree later showed `Energy_Benchmark_Architecture.docx` as deleted
  locally. That deletion was not committed or pushed. Do not include it in a
  future commit unless the user explicitly confirms that the Word document
  should be removed.

## What Is Next

The next run should first use `docs/planning_reflection_protocol.md`, then work
through the evidence gates in `docs/phase_1/phase_1_exit_checklist.md`.

After Phase 1 evidence gates are updated, Phase 2 preparation should begin
without jumping directly into physical telemetry:

1. Implement a run-bundle writer.
2. Implement a mock controller lifecycle.
3. Implement deterministic mock runtime and telemetry adapters.
4. Implement a basic reducer for synthetic power traces.
5. Make a single mock command produce:
   - `config.json` or `config.yaml`
   - `metadata.json`
   - `events.jsonl`
   - `power_trace.csv`
   - `summary_metrics.json`
   - logs and outputs directories
6. Add tests proving the mock run bundle can be created and reduced.

After the mock vertical slice works, move to the Mac-local MLX + powermetrics
vertical slice.

## Open Items

- Supervisor scope confirmation.
- Hailo feasibility verdict.
- Wall-meter availability.
- Network plan for 1GbE, 2.5GbE, and optional 10GbE experiments.
- Physical telemetry permission checks on Mac, NVIDIA nodes, Orin, and Pi/Hailo.
- Phase 1 exit checklist needs real evidence from hardware/supervisor access.
