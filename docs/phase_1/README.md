# Phase 1: Approval, Feasibility, And Measurement Design

## Goal

Lock the benchmark contract before building the full harness. Phase 1 should
make the measurement methodology explicit, classify hardware feasibility, and
leave Phase 2 ready to implement the Mac MLX + powermetrics vertical slice.

## Deliverables

- Benchmark config contract.
- Standard run output contract.
- Runtime, telemetry, and transport adapter contracts.
- Run-bundle layout.
- Measurement methodology.
- Hailo feasibility verdict.
- Instrumentation and permission checklist.

## Acceptance Criteria

- Example configs validate.
- Mock runtime and telemetry adapters satisfy the interface contracts.
- `phase_1_exit_checklist.md` contains evidence for every required Phase 1
  decision.
- Hardware targets are classified as supported, pending, or intentionally
  unsupported.
- The Mac-local Phase 2 vertical slice has a clear target contract:
  local transport, MLX runtime, powermetrics telemetry.

## Phase 1 Files

- `joulewise/schemas.py`: draft typed schemas.
- `joulewise/interfaces.py`: adapter protocol contracts.
- `configs/examples/`: example benchmark configs.
- `docs/phase_1/measurement_methodology.md`: measurement protocol draft.
- `docs/phase_1/hailo_feasibility.md`: Hailo feasibility checklist.
- `docs/phase_1/instrumentation_checklist.md`: target telemetry checklist.
- `docs/phase_1/network_plan.md`: interconnect sweep planning checklist.
- `docs/phase_1/phase_1_continuation_plan.md`: ordered plan for closing
  remaining Phase 1 evidence gates.
- `docs/phase_1/phase_1_exit_checklist.md`: evidence gates for Phase 1 exit.
- `docs/phase_1/run_bundle_layout.md`: required artifact layout.
