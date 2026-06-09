# JouleWise Run State

Last updated: 2026-06-09

## Start Here For Every Big Run

Before starting substantial work:

1. Read this file.
2. Read `AGENT_PLAN.md`.
3. Check `git status --short --branch`.
4. Run `python3 -m unittest discover -s tests` unless the task is docs-only.
5. Do not commit local deletions or unrelated changes unless the user asks.

At the end of substantial work:

1. Update this file with what changed.
2. Add or update a detailed report in `docs/run_reports/`.
3. Record tests, commands, blockers, and the next best task.
4. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

JouleWise is in Phase 1: approval, feasibility, and measurement design.

The repo has a scaffolded, tested foundation but not yet a runnable energy
measurement harness. The current implementation covers schemas, adapter
interfaces, docs, example configs, and CLI helpers.

## What I Did

- Created the repo-local agent implementation plan in `AGENT_PLAN.md`.
- Created Phase 1 methodology docs under `docs/phase_1/`.
- Added the `joulewise` Python package.
- Added typed schema skeletons for benchmark configs and summary outputs.
- Added runtime, telemetry, and transport adapter protocol contracts.
- Added example configs:
  - `configs/examples/mock_local.json`
  - `configs/examples/mac_mlx_local.json`
- Added CLI helpers:
  - `python3 -m joulewise validate-config`
  - `python3 -m joulewise print-config-schema`
  - `python3 -m joulewise print-output-schema`
- Added unit tests for schemas, interfaces, and CLI helpers.
- Renamed the project from the temporary `energybench` identity to JouleWise.
- Committed and pushed the scaffold to `origin/main`.

## Current Verification

Last verified command:

```bash
python3 -m unittest discover -s tests
```

Result:

```text
Ran 14 tests
OK
```

CLI smoke command:

```bash
python3 -m joulewise validate-config configs/examples/mac_mlx_local.json
```

Result:

```text
valid config: configs/examples/mac_mlx_local.json target=macbook_m3_max runtime=mlx telemetry=powermetrics
```

## Known Workspace State

- Remote: `git@github.com:mpmdw/JouleWise.git`
- Branch: `main`, tracking `origin/main`
- Latest pushed commit: `6a11142 Initialize JouleWise benchmark scaffold`
- Current local caution: `Energy_Benchmark_Architecture.docx` appears deleted in
  the working tree after the push. Do not commit that deletion unless the user
  confirms it should be removed from the repo.

## What Is Next

The next substantive implementation step is Phase 2 preparation:

1. Add a run-bundle writer that creates the documented directory layout.
2. Add a mock controller lifecycle:
   `prepare -> idle -> warmup -> measured_run -> cleanup -> reduce`.
3. Add a deterministic mock runtime and mock telemetry adapter.
4. Add reducer logic for simple synthetic power traces.
5. Make one command produce a complete mock run bundle.
6. Only after that, begin the Mac-local MLX + powermetrics vertical slice.

## Open Decisions And Blockers

- Supervisor approval and scope confirmation remain pending.
- Hailo feasibility remains pending.
- Wall-meter availability remains pending.
- Local network plan for interconnect sweep remains pending.
- Physical-target telemetry permissions remain pending.
- Git author identity was auto-selected as `Edr <edr@Edrs-MacBook-Air.local>`
  for the first commit. Amend future commits if a different identity is needed.
