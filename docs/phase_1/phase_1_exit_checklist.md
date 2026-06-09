# Phase 1 Exit Checklist

Phase 1 is complete only when the remaining planning items have evidence. This
file turns the open checklist into a proof-oriented dossier for future agents.

## Current Phase 1 Status

Status: in progress.

Already complete:

- Repo-local agent plan exists.
- Draft typed config contract exists.
- Draft standardized summary-output contract exists.
- Runtime, telemetry, and transport adapter interfaces exist.
- Run-bundle layout is documented.
- Mac-local and mock-local example configs validate.
- Schema, interface, and CLI tests pass.
- Run-report protocol exists.

Still required:

- Supervisor approval and scope confirmation.
- Hailo feasibility verdict.
- Wall-meter decision.
- Network/interconnect experiment plan.
- Telemetry permission checks for each physical target.
- Phase 2 readiness review.

## Evidence Matrix

| Item | Status | Required Evidence | Where To Record It |
|---|---|---|---|
| Supervisor approval and scope | pending | Written notes from meeting/email listing approved must-haves, stretch items, and out-of-scope items | This file and `RUN_STATE.md` |
| Hailo feasibility | pending | Toolchain/version check plus one documented compile/runtime attempt or official limitation finding | `docs/phase_1/hailo_feasibility.md` |
| Wall-meter availability | pending | Meter make/model, measurement resolution, export/manual logging method, and whether lab or purchased | `docs/phase_1/instrumentation_checklist.md` |
| Network plan | partially checked | Controller command/tool status recorded; topology, devices/adapters, isolation plan, and throughput method still pending | `docs/phase_1/network_plan.md` |
| Mac telemetry permissions | partially checked | `powermetrics` binary path and privilege requirement recorded; privileged sample fields still pending | `docs/phase_1/instrumentation_checklist.md` |
| NVIDIA telemetry permissions | pending | SSH access, `nvidia-smi` path, power-query support, sample command output | `docs/phase_1/instrumentation_checklist.md` |
| Orin telemetry permissions | pending | SSH access, selected telemetry source, sample command output, wall-meter fallback | `docs/phase_1/instrumentation_checklist.md` |
| Pi/Hailo telemetry permissions | pending | SSH access, wall-meter path, Hailo runtime verdict | `docs/phase_1/instrumentation_checklist.md` |
| Phase 2 readiness | pending | Review confirming mock vertical slice can begin without hardware access | This file |

## Supervisor Approval Checklist

Objective: lock what the capstone must deliver and what can slip.

Inputs:

- Current proposal.
- `AGENT_PLAN.md`.
- Phase 1 docs.

Actions:

- Ask supervisor to confirm the primary artifact is JouleWise, the reusable
  benchmark harness.
- Confirm disaggregation is the validating study.
- Confirm required hardware scope.
- Confirm whether Hailo is a feasibility finding rather than a must-succeed
  backend.
- Confirm stretch items: split quantization and minimal router.
- Confirm final deliverables: repo, report, raw traces/configs, colloquium.

Evidence:

- Add dated meeting/email notes here.
- Update `RUN_STATE.md` if scope changes.

Acceptance criteria:

- Must-haves, stretch items, and out-of-scope items are written down.
- No Phase 2 work depends on an unstated supervisor expectation.

Fallback:

- If approval is delayed, continue only with hardware-independent harness work:
  schemas, mock controller, run-bundle writer, reducer tests.

## Hailo Feasibility Checklist

Objective: determine whether Pi + Hailo participates as a backend or as an
unsupported hardware finding.

Inputs:

- Raspberry Pi 5 + Hailo-8L access.
- Hailo toolchain docs and installed version.
- Candidate small decoder-only or LLM-shaped workload.

Actions:

- Record Hailo SDK/toolchain version.
- Check supported model/operator families.
- Attempt one minimal LLM-shaped compile or runtime path if a plausible path
  exists.
- If no plausible path exists, cite the exact operator/runtime limitation.
- Record whether energy can be measured with a wall meter even if Hailo runtime
  works.

Evidence:

- Command outputs or notes in `docs/phase_1/hailo_feasibility.md`.
- Final verdict code: `supported`, `runtime_unavailable`,
  `format_unavailable`, `unsupported_workload`, or `telemetry_unavailable`.

Acceptance criteria:

- Hailo has a final verdict that future phases can consume without re-litigating
  feasibility.

Fallback:

- If Hailo is unsupported, keep it out of headline comparisons and include the
  verdict as an applicability finding.

## Wall-Meter Checklist

Objective: know whether system-level AC power can be measured and how.

Inputs:

- Lab equipment list or purchased meter.
- Device targets.

Actions:

- Record meter make/model.
- Record sample rate or manual logging method.
- Record precision/resolution if known.
- Record whether data can be exported digitally.
- Define how wall-meter readings align with run timestamps.

Evidence:

- Updated instrumentation checklist.
- Optional photo/manual link or notes if available.

Acceptance criteria:

- Each target has either platform telemetry, wall-meter telemetry, or a
  documented telemetry gap.

Fallback:

- If no meter is available, use platform telemetry for supported targets and
  mark targets requiring wall power as pending or telemetry-limited.

## Network Plan Checklist

Objective: make the interconnect sweep executable and measurable.

Inputs:

- Nodes available.
- Switches/adapters.
- Ethernet cables.
- Campus/local network constraints.

Actions:

- Draw the physical topology.
- List link speeds: 1GbE, 2.5GbE, optional 10GbE.
- Decide whether links are isolated from general traffic.
- Define how link speed is confirmed.
- Define how throughput is measured.
- Define where transfer events and payload sizes are recorded.

Evidence:

- `docs/phase_1/network_plan.md`.
- Command outputs from link-speed checks when hardware is available.

Acceptance criteria:

- Phase 3 can run the interconnect sweep without inventing topology or
  verification policy on the fly.

Fallback:

- If isolated networking is unavailable, record traffic-control limitations and
  treat measurements as less controlled.

## Telemetry Permission Checklist

Objective: prove each physical target can expose usable power data or fail
cleanly.

Inputs:

- Access to Mac, NVIDIA nodes, Orin nodes, and Pi/Hailo if available.
- Runtime account credentials.

Actions:

- For Mac: record `which powermetrics`, privilege requirement, and one sample
  command that exposes useful power/thermal fields.
- For NVIDIA: record `which nvidia-smi` and whether power draw queries work.
- For Orin: record the selected rail telemetry command or wall-meter fallback.
- For Pi/Hailo: record wall-meter availability and Hailo runtime verdict.

Evidence:

- Updated `docs/phase_1/instrumentation_checklist.md`.
- Captured command snippets or summarized outputs.

Acceptance criteria:

- Every physical target is classified as `supported`, `pending`, or
  `unsupported` for telemetry.

Fallback:

- If telemetry requires privileges, document the privilege workflow rather than
  bypassing it in code.

## Phase 2 Readiness Gate

Objective: decide whether implementation can move from Phase 1 planning into
the mock vertical slice.

Phase 2 can start when:

- Schemas validate examples.
- Adapter contracts exist.
- Run-bundle layout is documented.
- Phase 1 open hardware questions have evidence plans, even if not all hardware
  is physically available.
- The next implementation target is explicitly mock-first:
  run-bundle writer, mock controller, mock runtime, mock telemetry, reducer.

Phase 2 should not start with:

- Live MLX/powermetrics integration.
- NVIDIA/vLLM integration.
- Hailo work.
- Dashboard polish.

Those come after the mock run bundle can be produced and reduced.
