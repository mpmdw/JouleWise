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
- Run-report protocol, task queue, decision log, risk register, milestone
  map (ID ranges live in those files; they grow).

Still required:

- Calendar mapping (Step 7).

The original Phase 1 paperwork gates for supervisor scope, the wall-meter
decision, the network plan, and NVIDIA/Orin access now have disposition
evidence below. A recorded blocker means that the planning gate is answered;
it does not turn missing hardware into live validation. Physical acquisition,
contact, and promotion remain later gates under their owning plans.

Complete since the last revision:

- Mac telemetry/runtime evidence (Step 2) — complete 2026-07-06:
  privileged sample captured and pinned, D-004 sudoers installed and
  `sudo -n` verified, MLX installed and generating (see instrumentation
  section; exercised live by Slices 2H/2I).
- Hailo feasibility verdict (Step 5) - `unsupported_workload`, recorded
  2026-06-12 in the Hailo section below from official-source desk
  research (optional local reproduction noted there).
- Phase 2 readiness review (Step 8) - recorded 2026-06-12 in the
  readiness section below; mock-first Phase 2 implementation began the
  same day.

## Evidence Matrix

| Item | Status | Required Evidence | Recorded In |
|---|---|---|---|
| Supervisor approval and scope | complete by later authority (2026-07-30) | Written notes from meeting/email listing approved must-haves, stretch items, and out-of-scope items | Supervisor section below; D-091; `docs/contracts/capstone_scope.md` |
| Mac telemetry permissions | complete (2026-07-06) | Privileged 5-sample plist captured by the user on the M3 Max (`tests/fixtures/powermetrics_sample.plist`); framing + field names recorded below and pin the 2H parser; D-004 sudoers line installed and verified via `sudo -n`; exercised live by the 2I flagship run | Instrumentation section below |
| Mac runtime (MLX) | complete (2026-07-06) | Install path decided; install or documented procedure | Instrumentation section below (installed in `.venv`, versions pinned, real generation verified via Slice 2G) |
| Wall-meter decision | complete; acquisition pending (2026-07-30) | The accepted `to-buy` decision and its measurement boundary are recorded; procurement and characterization remain separate later gates | Wall-meter section below; D-092 |
| Network plan | blocker recorded; physical confirmation pending | Controller tool status, candidate link paths, verification methods, transfer fields, and the missing hardware facts are recorded | Network section below |
| Hailo feasibility | complete (2026-06-12, desk research) | Toolchain/version check plus one documented compile/runtime attempt or official limitation finding; verdict code | Hailo section below (`unsupported_workload`) |
| NVIDIA telemetry permissions | pending with recorded blocker | SSH access, `nvidia-smi` path, power-query support, sample command output, or the missing access named explicitly | Instrumentation section below |
| Orin telemetry permissions | pending with recorded blocker | SSH access, selected telemetry source, sample command output, wall-meter fallback, or the missing access named explicitly | Instrumentation section below |
| Pi/Hailo telemetry permissions | pending | SSH access, wall-meter path, Hailo runtime verdict | Instrumentation + Hailo sections below |
| Calendar mapping | pending | Dates in `docs/milestones.md`; phase targets derived | `docs/milestones.md` |
| Phase 2 readiness | complete (2026-06-12) | Review confirming mock-first Phase 2 can begin without hardware access | Readiness section below |

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

Recorded evidence:

- On 2026-07-30, D-091 recorded the supervisor-ratified change to a
  metrology-centred capstone: the measurement instrument is the product and
  model comparisons are demonstration studies.
- `docs/contracts/capstone_scope.md` is the binding scope record. It identifies
  the protected minimum deliverables, the split-inference stretch path, the
  conditions that force cuts, and the claims that are out of scope without
  stronger evidence.

These dated authorities supersede the empty meeting-note placeholder. They
record the scope content that P1-001 requested without reconstructing or
inventing meeting minutes.

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

Current verdict: `unsupported_workload` (desk research, 2026-06-12;
confidence high; optional local reproduction step recorded below).

Recorded evidence (2026-06-12, official-source desk research):

- Hailo staff state the Hailo-8/8L cannot run LLMs by design: the 8-class
  parts have no DDR interface, so a multi-billion-parameter model would
  need 100+ host-managed context switches; they redirect LLM users to the
  Hailo-10H, which "adds a DDR interface and local DDR memory".
  Sources: community.hailo.ai/t/running-local-llm-using-hailo-8l/1093 and
  community.hailo.ai/t/can-the-raspberry-pi-ai-kit-support-running-large-language-models-llms/1217
  (the second names the Pi AI Kit / Hailo-8L specifically).
- A documented compile attempt of a real decoder-only LLM on the 8-class
  toolchain fails at parse: Llama-3-8B translation aborts with
  `UnsupportedModelError: Unexpected zero dimension in shape [-1, 0]`
  (dynamic shapes); staff add that multi-head self-attention "looks
  different than what the SW knows how to parse".
  Source: community.hailo.ai/t/translating-llm-llama-3-8b-fails/1754.
- The Hailo-8/8L Model Zoo (github.com/hailo-ai/hailo_model_zoo) contains
  zero decoder-only LLMs; its transformers are all vision/embedding
  encoders (ViT, DETR, CLIP/SigLIP, SegFormer, ...). LLMs live in a
  separate GenAI zoo (github.com/hailo-ai/hailo_model_zoo_genai) whose
  models all list the Hailo-10H module as a prerequisite.
- Hailo's own product positioning draws the line on exactly this
  capability: the 10H GA announcement says it brings LLM/VLM inference to
  the edge "for the first time", complementing Hailo-8's vision-AI role
  (hailo.ai/products/ai-accelerators/hailo-10h-ai-accelerator/).
- Anti-confusion note: the 8L does run encoder transformers and the
  Whisper encoder-decoder demo; only the decoder-only autoregressive
  token-by-token workload class is unsupported. The 8L shares the
  Hailo-8's dataflow architecture, compiler, and no-DRAM memory model, so
  the 8-class findings apply to it.

Per-question answers: toolchain cannot compile decoder-only models (parse
failure on dynamic shapes/attention); operator set covers encoder
attention only, no KV-cache access pattern; no token-by-token decode
runtime path exists on the 8L (HailoRT GenAI serving is 10H-only); power
measurement is moot for an unrunnable workload (wall-meter path remains
for any non-LLM Pi work).

Optional hardening (not required to consume the verdict): on the actual
Pi 5 + Hailo-8L, compile any small decoder-only ONNX (GPT-2/TinyLlama)
through the Dataflow Compiler and record the parse failure, converting
"documented limitation" into "reproduced locally". Re-check the GenAI
zoo's device matrix at whatever toolchain version is installed, in case
attention-op coverage changes.

Consequence for scope (R-009 expected-negative case): `pi5_hailo` is
reported as a hardware-applicability finding, not implemented as a
backend; Slice 2-era work for it is limited to the wall-meter path if the
Pi is kept as a non-LLM comparison point at all.

Acceptance: a final verdict future phases can consume without
re-litigating feasibility.

## Wall Meter

Objective: know whether system-level AC power can be measured and how; the
meter is the boundary equalizer for cross-target comparisons (D-018) and
the only telemetry path for Pi/Hailo.

To record: meter make/model; sample rate or manual logging method;
precision/resolution; digital export availability; how readings align with
run timestamps; lab equipment or purchase.

Recorded decision (2026-07-30): D-092 answers P1-003 with `to-buy`. The
external meter is required only for the conditional whole-machine validation
claim; it cannot validate phase allocation. No meter is currently available,
so all other claims must stand on the internal instrument characterization.
Purchase or loan, exact make/model selection, safe fixture qualification,
timestamp alignment, and characterization remain later execution gates; they
are not silently treated as complete here.

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

P1-004 disposition: the Phase 1 planning acceptance permits a documented
blocker. That blocker is the absent physical hardware assignment: node roles,
switch or direct-cable choice, adapters, cables, and supported link speeds are
not yet known. The section already fixes the verification choices and the
fields every later transfer must record. Actual topology confirmation must be
opened with the future split-inference hardware work; this record does not
claim that a link was measured.

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
  - ADDENDUM (2026-07-09, DOC-009 reconciliation): superseded — the
    binding verdict below (this file, "Current verdict" section) is
    **supported, end to end (2026-07-06)** per the Slice 2I flagship
    (3 strict-valid real energy bundles). This earlier "partially
    checked" line reflects the pre-2I snapshot and is retained for
    history only.
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
  - [x] D-004 scoped sudoers rule installed and verified via `sudo -n`
    (2026-07-06: `/etc/sudoers.d/joulewise-powermetrics`, scoped to
    `/usr/bin/powermetrics` only; verified by a passwordless `sudo -n`
    probe and by the live 2I runs).
  - [x] Privileged sample captured (2026-07-06, user session, M3 Max):
    `sudo /usr/bin/powermetrics -i 1000 -n 5 --samplers
    cpu_power,gpu_power,ane_power,thermal --format plist -o
    tests/fixtures/powermetrics_sample.plist` → 269,059 bytes, 5
    documents. Field names (pin the 2H parser): power rails live under
    the top-level `processor` dict as `cpu_power` / `gpu_power` /
    `ane_power` (floats, **milliwatts**), with `combined_power` equal to
    their exact sum (verified: 484.971+52.906=537.877) — confirming the
    D-018 `rail_manifest` sum; companion `cpu_energy`/`gpu_energy`/
    `ane_energy` ints (mJ) cross-check (1492 mJ / 1.011 s ≈ 1476 mW).
    Per-doc `timestamp` is a UTC datetime with **1-second resolution**;
    `elapsed_ns` carries the precise interval — the parser must derive
    sample times from the first timestamp + cumulative `elapsed_ns`.
  - [x] Thermal fields available in captured samples: top-level
    `thermal_pressure` string (`"Nominal"` observed).
  - [x] Output parser target selected: `plist` — framing CONFIRMED
    against the capture: NUL-separated XML plist documents (4 NUL
    bytes / 5 docs), each parses with stdlib `plistlib.loads`.
  - [x] MLX install path decided (dedicated venv, `[mac]` extra) —
    2026-07-06, on the M3 Max measurement target: repo-local `.venv`
    (gitignored), Python 3.13.1.
  - [x] MLX/MLX-LM installed or installation procedure documented —
    `mlx` 0.31.2, `mlx_lm` 0.31.3, `transformers` 5.12.1. Compat
    finding: `transformers` 5.13.0 breaks `mlx_lm` 0.31.3 at import
    (`AutoTokenizer.register` signature change); the `[mac]` extra now
    pins `mlx-lm>=0.31.3` + `transformers<5.13`. Real generation
    verified: 328 tok/s CLI smoke, then the Slice 2G bundle
    (`example-mac-mlx-mock-telemetry`, 265.8 tok/s through the full
    harness).
- Current verdict: **supported, end to end** (2026-07-06) — runtime and
  telemetry both exercised live by the Slice 2I flagship (3 strict-valid
  real energy bundles; see run report
  `2026-07-06-slice-2i-first-real-energy.md`). Nothing remains open in
  this section.
- Next owner/action: none — closed. Future Mac-target work (2M
  baselines, Phase 3 spikes) builds on it.

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

P1-006 NVIDIA disposition: pending with blocker. No SSH credential or device
contact is available in the repository evidence, so CUDA, Video Random
Access Memory (VRAM), and live `nvidia-smi` power sampling cannot be checked.
The fixture-first implementation is not live evidence; the protocol pins stay
provisional until the live-promotion checklist is executed on the device.

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

P1-006 Orin disposition: pending with blocker. No SSH credential or device
contact is available in the repository evidence, so the runtime and the
INA3221 or `tegrastats` telemetry path cannot be selected from observation.
No support or measurement claim is made.

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

Recorded readiness review (2026-06-12, Step 8):

- Schemas validate both example configs; adapter contracts exist
  (`docs/contracts/adapter_contracts.md` + `joulewise/interfaces.py`);
  bundle layout is documented (`docs/contracts/run_bundle_layout.md`).
  Verified by the passing test suite and `validate-config` on both
  examples.
- Every open hardware question (Steps 1-7) carries an evidence plan and a
  fallback in `docs/phase_1/phase_1_plan.md`; none of them gates the mock
  vertical slice (the Phase 2 plan marks slices 2A-2F and 2J
  hardware-independent).
- The next implementation target is explicitly mock-first: slices 2A-2E
  per `docs/phase_2/phase_2_plan.md`, then 2F/2J.

Verdict: **mock-first Phase 2 implementation may begin.** The hardware
slices (2G/2H/2K/2L) remain gated on their Phase 1 evidence (P1-002,
P1-006, D-016) and are untouched by this verdict. Phase 1 itself stays
open: Steps 1-7 still need their external evidence.
