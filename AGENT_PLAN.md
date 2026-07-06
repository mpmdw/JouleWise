# Agent Implementation Plan

This repository implements JouleWise, an extensible energy-characterization
benchmark for LLM inference across heterogeneous local hardware. The name is a
nod to JouleSort and Splitwise: energy measurement as the spine, split inference
as the first research application that validates the harness.

## Ground Rules For Agents

- At the start of every substantial run, read `RUN_STATE.md` first.
- For any new/random user task, triage it in `TASK_QUEUE.md` before deciding
  whether it outranks the current phase work.
- At the start of each phase or major step, apply
  `docs/planning_reflection_protocol.md` before implementation.
- At the end of every substantial run, update `RUN_STATE.md` and add or update a
  detailed report in `docs/run_reports/`. If advisor-visible state changed (a
  phase or gate closed, a verdict landed, the schedule moved), refresh
  `PROJECT_STATUS.md` too.
- Check `docs/decision_log.md` before re-deciding anything; record new design
  decisions there with options and considerations.
- Per-item phase status is asserted only in
  `docs/phase_N/phase_N_exit_checklist.md` (D-023); this file's checkboxes
  are a coarse mirror updated at slice/phase closes.
- Review `docs/risk_register.md` at phase starts and when a trigger fires.
- Keep run artifacts self-contained and reproducible.
- Prefer small vertical slices that produce complete run bundles.
- Treat unsupported hardware/model combinations as structured outcomes, not
  crashes.
- Keep runtime adapters separate from telemetry adapters.
- Make every result traceable to a config, raw power trace, event log, and
  reducer output.

## Single Source Of Truth Map

Detail lives in exactly one place; everything else links to it. When
documents disagree, fix the drift in the same run and note it in the run
report.

| Artifact | Owns |
|---|---|
| `AGENT_PLAN.md` (this file) | phase index, coarse status mirror, acceptance criteria (per-item status authority: the exit checklists, D-023) |
| `PROJECT_STATUS.md` | advisor-facing status/plan/architecture summary (derived; update when advisor-visible state changes) |
| `docs/phase_N/phase_N_plan.md` | step/slice detail: objectives, design, actions, evidence, fallbacks |
| `docs/phase_N/phase_N_exit_checklist.md` | evidence gates for closing phase N, and per-item status (the authority, D-023) |
| `TASK_QUEUE.md` | what to do next, and why it outranks the rest |
| `docs/agent_playbook.md` | per-mission execution guides for agents: read-first lists, code-level routes, verification, handoff checklists |
| `RUN_STATE.md` | current handoff: state, verification, next step |
| `docs/decision_log.md` | design decisions, options, considerations |
| `docs/risk_register.md` | risks, triggers, mitigations, descope ladder |
| `docs/milestones.md` | calendar constraints and phase target dates |
| `docs/contracts/measurement_methodology.md` | measurement rules (boundaries, clocks, statistics) |
| `docs/contracts/run_bundle_layout.md` | bundle artifact contract |
| `docs/contracts/adapter_contracts.md` | adapter behavior contracts |

## Canonical Architecture

```text
typed config
  -> controller
    -> transport adapter: local or ssh
    -> runtime adapter: mlx, vllm, llama.cpp, hailo-if-viable
    -> telemetry adapter: powermetrics, nvidia-smi, jetson rails, wall meter
  -> run bundle
    -> reducers
    -> dashboard / notebooks / report figures
```

## Phase Index

### Phase 1: Approval, Feasibility, And Measurement Design

Status: in progress (most design/feasibility items closed; the remaining
gates need external/hardware input). Detail: `docs/phase_1/phase_1_plan.md`.
Exit: `docs/phase_1/phase_1_exit_checklist.md` (the evidence dossier). The
contracts this phase produced live in `docs/contracts/`.

- [x] Create repo-local agent plan.
- [x] Add reusable planning reflection protocol.
- [x] Add evidence-based Phase 1 exit checklist.
- [x] Add task queue protocol for prioritizing new work against repo state and
  recent handoffs.
- [x] Define draft typed benchmark config contract.
- [x] Define draft standardized run output contract.
- [x] Define runtime/telemetry/transport adapter interfaces.
- [x] Define run-bundle layout.
- [x] Add example configs for Mac-local and mock-local runs.
- [x] Add schema/interface tests.
- [x] Add Phase 1 CLI helpers for config validation and schema printing.
- [x] Extend measurement methodology: boundaries, clock sync, co-residency,
  repetition/thermal protocol, statistical protocol.
- [x] Establish decision log, risk register, and milestone map.
- [x] Complete Hailo feasibility investigation — verdict
  `unsupported_workload` (2026-06-12, desk research; Hailo-8L has no
  autoregressive-LLM path, the GenAI path is Hailo-10H-only).
- [x] Confirm Phase 2 readiness (mock-first can begin) — recorded
  2026-06-12.
- [ ] Confirm supervisor expectations and final proposal scope.
- [ ] Confirm wall-meter availability.
- [ ] Confirm local network plan for interconnect sweep.
- [ ] Confirm telemetry permissions on each physical target.
- [ ] Map phases to the academic calendar (`docs/milestones.md`).

Acceptance criteria:

- Example configs validate.
- Mock adapter tests pass.
- Measurement methodology is documented.
- `docs/phase_1/phase_1_exit_checklist.md` has evidence for every required
  Phase 1 item.
- Every hardware target is classified as supported, pending, or intentionally
  unsupported.
- Phase 2 can start with a clear mock-first path toward the Mac MLX +
  powermetrics vertical slice.

### Phase 2: Harness, Mac Vertical Slice, And Homogeneous Baselines

Status: in progress — the hardware-independent core (2A-2F, 2J) is complete
and runnable (2026-06-12); Slice 2N (pre-hardware hardening, ungated) is
next; the remaining slices are hardware-gated. Detail:
`docs/phase_2/phase_2_plan.md`. Exit: `docs/phase_2/phase_2_exit_checklist.md`.
Gated-slice specs: `docs/phase_2/hardware_slice_implementation_guide.md`.

Mock-first ordering (matches `TASK_QUEUE.md`; the real-hardware slices are
gated on Phase 1 evidence). The hardware-independent core (2A-2F, 2J) is
complete and runnable as of 2026-06-12; code-level specs for the gated
slices live in `docs/phase_2/hardware_slice_implementation_guide.md`.

- [x] 2A Run-bundle writer.
- [x] 2B Clock seam + built-in mock adapters.
- [x] 2C Controller lifecycle with structured failure paths.
- [x] 2D Reducer v1 with closed-form tests.
- [x] 2E One-command run + `validate-bundle` (mock end-to-end in CI).
- [x] 2F Repetitions, experiment manifests, cooldown gate.
- [ ] Model selection checkpoint (decision D-016) — gated on P1-001 scope.
- [ ] 2G MLX runtime adapter (gated: D-016 + `[mac]` install).
- [ ] 2H powermetrics telemetry adapter (gated on privileged-sample
  evidence + D-004 sudoers).
- [ ] 2I Mac vertical slice integration with variance (gated: 2F+2G+2H).
- [x] 2J Static report generator v1.
- [ ] 2N Pre-hardware hardening (ungated; land before 2G/2H) — added
  2026-07-05 from the external code review; see the Phase 2 plan.
- [ ] 2K NVIDIA/vLLM + nvidia-smi + SSH transport (gated on P1-006).
- [ ] 2L Orin adapter (gated on P1-006).
- [ ] 2M Homogeneous baselines + prefill/decode qualitative reproduction.

Acceptance criteria:

- One command creates a complete Mac run bundle.
- Dashboard displays the run trace and summary metrics.
- Repeated runs report variance.
- Unsupported combos fail with structured failure reasons.

### Phase 3: Disaggregation, Offline KV Replay, And Interconnect Sweep

Status: planned. Detail: `docs/phase_3/phase_3_plan.md`. Exit:
`docs/phase_3/phase_3_exit_checklist.md`. Feasibility-first per decision
D-015: spikes before hardware scheduling, synthetic-transfer floor
guarantees a crossover dataset.

- [ ] 3.0 KV persistence feasibility spikes (kv-size helper; mlx-lm;
  llama.cpp incl. cross-machine portability; vLLM time-boxed; verdict
  consolidation).
- [ ] 3.1 Schema v0.2 (`run_kind` + `split_plan`) + transfer
  microbenchmark with both-end energy.
- [ ] 3.2 Offline split runs with per-stage decomposition
  (prefill/transfer/deserialize/decode).
- [ ] 3.3 Live split (stretch; droppable).
- [ ] 3.4 Interconnect sweep + crossover dataset (1GbE, 2.5GbE, optional
  10GbE; 3080 Ti borrow window per runbook).

Acceptance criteria:

- Split runs decompose prefill, transfer, and decode energy.
- Offline replay produces valid decode-energy measurements (or its
  documented fallback was exercised).
- Interconnect data supports a crossover curve.

### Phase 4: Core Characterization And Analysis

Status: planned. Detail: `docs/phase_4/phase_4_plan.md`. Exit:
`docs/phase_4/phase_4_exit_checklist.md`.

- [ ] 4.0 Statistical protocol ratification against observed variance.
- [ ] 4.1 Aggregation layer with exclusion-log discipline.
- [ ] 4.2 Deterministic figure pipeline (registry F1-F8).
- [ ] 4.3 Claims-to-evidence index.
- [ ] 4.4 Results and limitations draft.
- [ ] 4.5 Uncertainty and sensitivity audit.
- [ ] 4.6 Background and related-work draft (ungated desk work; may start
  any time).

Acceptance criteria:

- Claims trace back to raw run bundles.
- Figures regenerate from repository scripts.
- Results identify where splitting wins, loses, and why.

### Phase 5: Presentation, Repository Polish, And Final Submission

Status: planned. Detail: `docs/phase_5/phase_5_plan.md`. Exit:
`docs/phase_5/phase_5_exit_checklist.md`.

- [ ] 5.0 Verified README quickstart.
- [ ] 5.1 Backend-extension guide verified by a shipped tutorial adapter.
- [ ] 5.2 Sample bundle publication with CI validation.
- [ ] 5.3 Dataset freeze and release tag.
- [ ] 5.4 Colloquium slides on frozen figures.
- [ ] 5.5 Final report assembly with claims-index final pass.
- [ ] 5.6 Repository final pass and project-complete handoff.

Acceptance criteria:

- A new user can run one local benchmark from the README.
- A new developer can add a backend from the adapter guide.
- Final figures regenerate from published data.

## Current Verification Command

```bash
python3 -m unittest discover -s tests
```

Useful commands:

```bash
# Phase 1: config + schema verbs
python3 -m joulewise validate-config configs/examples/mock_local.json
python3 -m joulewise print-config-schema
python3 -m joulewise print-output-schema

# Phase 2: run the harness (mock, deterministic) and verify the bundle
python3 -m joulewise run configs/examples/mock_local.json --runs-dir runs
python3 -m joulewise validate-bundle runs/example-mock-local
python3 -m joulewise report runs --output report   # needs the [analysis] extra
```

## Run Report Protocol

Every big run must leave a human-readable handoff note. The report should cover:

- Planning reflection performed at the start of the run.
- What changed.
- What commands were run.
- What passed or failed.
- What local workspace state needs care.
- What the next agent should do first.
- New or updated decision-log entries and risk-register statuses.

The root `RUN_STATE.md` is the current handoff. Dated reports live in
`docs/run_reports/`.

Every new phase also needs an exit checklist or equivalent section that states
the evidence required to close that phase. See
`docs/planning_reflection_protocol.md` for the reusable format.

## Task Queue Protocol

Random or newly discovered work should be ranked in `TASK_QUEUE.md` before it is
executed. The queue ranks tasks against:

- Current repo state.
- Recent commits.
- Recent run reports.
- Current phase exit gates.
- Safety risk and implementation dependency order.

If a task is executed immediately, the run report should state why it outranked
the current top queued task.
