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
- `docs/phase_1/run_bundle_layout.md`: required artifact layout.
