# Phase 1 Exit Checklist

Phase 1 is complete only when every required item below has evidence. This
file is the phase's proof dossier: it defines the required evidence *and*
records it (per the project convention, evidence lives in the phase exit
checklist until a topic outgrows it, in which case it moves to a dedicated
file under the phase directory and is linked from here).

Companion plan: `docs/phase_1/phase_1_plan.md`.

## Current Phase 1 Status

Status: in progress.

Already complete:

- Repo-local agent plan and per-phase plan/exit-checklist structure.
- Draft typed config contract and standardized summary-output contract.
- Runtime, telemetry, and transport adapter interfaces.
- Run-bundle layout (`docs/contracts/run_bundle_layout.md`).
- Measurement methodology incl. boundaries, clocks, co-residency,
  repetition/thermal, statistics (`docs/contracts/measurement_methodology.md`).
- Mac-local and mock-local example configs validate.
- Schema, interface, and CLI tests pass.
- Run-report protocol, task queue, decision log (D-001..D-019), risk
  register (R-001..R-015), milestone map.

Still required:

- Supervisor approval and scope confirmation (Step 1).
- Mac telemetry/runtime evidence completion (Step 2).
- Wall-meter decision (Step 3).
- Network/interconnect plan with physical topology (Step 4).
- Hailo feasibility verdict (Step 5).
- NVIDIA/Orin access evidence (Step 6).
- Calendar mapping (Step 7).
- Phase 2 readiness review (Step 8).

## Evidence Matrix

| Item | Status | Required Evidence | Recorded In |
|---|---|---|---|
| Supervisor approval and scope | pending | Written notes from meeting/email listing approved must-haves, stretch items, and out-of-scope items | Supervisor section below; `RUN_STATE.md` if scope changes |
| Mac telemetry permissions | partially checked | `powermetrics` binary path and privilege requirement recorded; privileged sample fields + sudoers rule pending the 2026-06-10 auth session | Instrumentation section below |
| Mac runtime (MLX) | pending | Install path decided; install or documented procedure | Instrumentation section below |
| Wall-meter availability | pending | Meter make/model, resolution, export/manual logging method, lab-or-purchased | Wall-meter section below |
| Network plan | partially checked | Controller tool status recorded; topology, link-speed paths, isolation plan, throughput method still pending | Network section below |
| Hailo feasibility | pending | Toolchain/version check plus one documented compile/runtime attempt or official limitation finding; verdict code | Hailo section below |
| NVIDIA telemetry permissions | pending | SSH access, `nvidia-smi` path, power-query support, sample command output | Instrumentation section below |
| Orin telemetry permissions | pending | SSH access, selected telemetry source, sample command output, wall-meter fallback | Instrumentation section below |
| Pi/Hailo telemetry permissions | pending | SSH access, wall-meter path, Hailo runtime verdict | Instrumentation + Hailo sections below |
| Calendar mapping | pending | Dates in `docs/milestones.md`; phase targets derived | `docs/milestones.md` |
| Phase 2 readiness | pending | Review confirming mock-first Phase 2 can begin without hardware access | Readiness section below |

## Supervisor Approval

Objective: lock what the capstone must deliver and what can slip.

Questions to put to the supervisor (one meeting should close this gate):

- Is the primary artifact JouleWise, the reusable benchmark harness, with
  disaggregation as the validating study?
- What is the required hardware scope?
- Is Hailo a feasibility finding rather than a must-succeed backend?
- Are split quantization and a minimal router stretch items?
- Are the final deliverables repo + report + raw traces/configs +
  colloquium?
- May mock-first Phase 2 implementation proceed before all hardware
  checks complete?

Recorded evidence: none yet. Add dated meeting/email notes here.

Acceptance: must-haves, stretch items, and out-of-scope items written
down; no Phase 2 work depends on an unstated expectation.

## Hailo Feasibility

The Raspberry Pi 5 + Hailo-8L path is a feasibility investigation, not a
headline dependency (R-009). If it cannot run an LLM-shaped autoregressive
workload, that outcome is documented as a hardware-applicability result.

Questions to resolve:

- Can the Hailo toolchain compile any autoregressive decoder-only model?
- Does the supported operator set cover attention and KV-cache access
  patterns?
- Is there a supported runtime path for repeated token-by-token decode?
- Can power be measured at useful resolution with available equipment?
- If no LLM path exists, what exact blocker applies?

Verdict codes: `supported` (include in Phase 2/3 backend work),
`runtime_unavailable`, `format_unavailable`, `unsupported_workload`,
`telemetry_unavailable`, `pending`.

Current verdict: `pending`.

Recorded evidence: none yet (toolchain version, command outputs, and the
attempted-or-blocked compile path go here).

Acceptance: a final verdict future phases can consume without
re-litigating feasibility.

## Wall Meter

Objective: know whether system-level AC power can be measured and how; the
meter is the boundary equalizer for cross-target comparisons (D-018) and
the only telemetry path for Pi/Hailo.

To record: meter make/model; sample rate or manual logging method;
precision/resolution; digital export availability; how readings align with
run timestamps; lab equipment or purchase.

Recorded evidence: none yet.

Acceptance: each target has platform telemetry, wall-meter telemetry, or a
documented telemetry gap.

## Network And Interconnect

Objective: make the Phase 3 interconnect sweep executable and measurable
before hardware time. Used again at Phase 3 start.

Target links:

- 1GbE: baseline commodity Ethernet.
- 2.5GbE: planned switch/adapter path.
- 10GbE: optional extension if adapters are available.

Planned topology - pending physical hardware confirmation. To record:
controller node; prefill node; decode node; switch model (or direct
cabling per R-011); adapter models; cable type/length; whether the
benchmark link is isolated from general traffic.

Recorded controller evidence from 2026-06-09:

- `ifconfig` is available and shows an active `en0` interface with
  `media: autoselect`.
- `networksetup -listallhardwareports` failed in that execution context
  with `AuthorizationCreate() failed: -60008` (retry in a normal terminal
  if needed).
- `iperf3` is not installed on the current controller.
- Do not treat the current Wi-Fi/home-network interface as the benchmark
  interconnect; the sweep needs a dedicated physical topology.

Link verification - record per node the command and result:

- macOS: `networksetup -listallhardwareports` (currently
  authorization-blocked in agent context), `ifconfig <interface>` (works).
- Linux: `ethtool <interface>` (pending Linux node access).

Evidence template per link:

```text
interface:
configured speed:
negotiated speed:
duplex:
date checked:
```

Throughput verification - `iperf3` if installed (currently not), else a
fixed-size file transfer. Evidence template:

```text
link target:
tool:
payload size:
measured throughput:
run count:
notes:
```

Transfer measurement policy (aligned with the bundle layout and the
Phase 3 plan's stage accounting): every split/disaggregated run records
payload size in bytes; serialization start/end; transfer start/end;
deserialization start/end; link speed label; measured throughput;
transfer-stage energy method (measured, modeled, or unavailable).

Open items: choose/confirm the 2.5GbE switch or adapters; decide whether
10GbE is in scope; identify controller/prefill/decode nodes per
experiment; decide isolation vs direct cabling; install `iperf3` or pin
the fixed-size transfer procedure.

Acceptance: all intended link speeds have a concrete hardware path or are
explicitly unavailable; verification commands known per node; throughput
method selected; transfer-event fields align with the bundle layout.

## Instrumentation And Telemetry Permissions

Objective: prove each physical target can expose usable power data or
fail cleanly. Phase 1 records *access* evidence here; Phase 2's
implementation verdicts land in the Phase 2 exit checklist's
applicability table.

### Apple Silicon / Mac

- Runtime target: MLX. Telemetry target: powermetrics. Transport: local.
- Status: partially checked on the current Apple Silicon controller;
  repeat on the final M3 Max measurement target before claiming support.
- Observed 2026-06-09:
  - Architecture: `arm64`; current user id non-root (`501`).
  - `powermetrics` found at `/usr/bin/powermetrics`.
  - `powermetrics --help` lists machine-readable `plist` output and
    samplers: `thermal`, `cpu_power`, `gpu_power`, `ane_power`.
  - Direct sample attempt
    (`powermetrics -n 1 -i 100 --samplers thermal,cpu_power,gpu_power,ane_power`)
    failed with: `powermetrics must be invoked as the superuser`.
  - Python import checks: `mlx` and `mlx_lm` not installed in the current
    environment.
- Evidence commands run 2026-06-09:

```bash
which powermetrics
powermetrics --help
powermetrics -n 1 -i 100 --samplers thermal,cpu_power,gpu_power,ane_power
python3 -c "import importlib.util; print(importlib.util.find_spec('mlx') is not None)"
uname -m
id -u
```

- Checks:
  - [x] `powermetrics` binary present.
  - [x] Superuser requirement identified.
  - [ ] D-004 scoped sudoers rule installed and verified via `sudo -n`.
  - [ ] Privileged sample captured; power/thermal field names recorded
    (these pin the Slice 2H parser).
  - [ ] Thermal fields available in captured samples.
  - [ ] Output parser target selected: `plist` (expected; confirm framing
    against the captured sample).
  - [ ] MLX install path decided (dedicated venv, `[mac]` extra).
  - [ ] MLX/MLX-LM installed or installation procedure documented.
- Current verdict: telemetry binary present; permission-blocked until the
  sudo workflow is in place; runtime pending install.
- Next owner/action: user handles local auth on 2026-06-10; then capture
  the privileged sample and record field names here, and install the
  D-004 sudoers line.

### NVIDIA 3050

- Runtime target: vLLM (llama.cpp-CUDA fallback per Slice 2K). Telemetry:
  nvidia-smi, optional wall meter. Transport: ssh.
- Status: pending device access. Controller-side note from 2026-06-09:
  `nvidia-smi` is absent locally, which is expected on the Mac controller
  and must be checked on the NVIDIA node itself.
- Checks:
  - [ ] SSH access.
  - [ ] CUDA runtime present.
  - [ ] vLLM install path (or llama.cpp-CUDA decision recorded).
  - [ ] `nvidia-smi --query-gpu=power.draw` sampling works; sample output
    captured.
  - [ ] VRAM limit documented (8 GB expected; informs D-016).
  - [ ] Wall-meter comparison path noted.

### NVIDIA 3080 Ti (borrow)

- Same checks as the 3050, plus:
  - [ ] Borrow window confirmed and entered in `docs/milestones.md`
    (R-006: schedule only after Stage 3.0 verdicts + rehearsed runbook).
  - [ ] Memory limit documented.

### Jetson Orin Nano Super

- Runtime target: TBD (decided with D-016/Slice 2L evidence). Telemetry:
  INA3221 rails preferred, `tegrastats` fallback, wall meter last resort
  (R-008). Transport: ssh.
- Status: pending device access.
- Checks:
  - [ ] SSH access.
  - [ ] Runtime path selected and recorded.
  - [ ] Rail telemetry accessible (sysfs paths or tegrastats output
    captured; actual rail recorded per D-018).
  - [ ] Wall-meter fallback available.

### Raspberry Pi 5 + Hailo-8L

- Runtime target: Hailo if viable (see Hailo section). Telemetry: wall
  meter only. Transport: ssh.
- Status: pending Hailo feasibility verdict.
- Checks:
  - [ ] SSH access.
  - [ ] Hailo toolchain installed; version recorded.
  - [ ] LLM-shaped workload feasibility tested (or blocker cited).
  - [ ] Verdict recorded in the Hailo section above.

## Phase 2 Readiness Gate

Objective: decide whether implementation can move from Phase 1 planning
into the mock vertical slice.

Phase 2 can start when:

- Schemas validate examples; adapter contracts exist; bundle layout is
  documented (all true).
- Open hardware questions have evidence plans, even if not all hardware is
  physically available (the steps above each carry a fallback).
- The next implementation target is explicitly mock-first: slices 2A-2E
  per `docs/phase_2/phase_2_plan.md`.

Phase 2 must NOT start with: live MLX/powermetrics integration,
NVIDIA/vLLM integration, Hailo work, or report-generator polish - those
follow the mock bundle/reducer path, and the hardware slices additionally
wait on their gates.

Recorded readiness review: none yet (Step 8 writes it here).
