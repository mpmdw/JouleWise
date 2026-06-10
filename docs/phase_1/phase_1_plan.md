# Phase 1 Plan: Approval, Feasibility, And Measurement Design

Status: in progress - contracts and planning infrastructure are complete;
the remaining steps are evidence gates, most waiting on user, supervisor,
or hardware access.

Companion docs:

- Exit gates + recorded evidence: `docs/phase_1/phase_1_exit_checklist.md`
- Decisions referenced as `D-NNN`: `docs/decision_log.md`
- Risks referenced as `R-NNN`: `docs/risk_register.md`
- Contracts this phase produced (living documents, project-wide):
  `docs/contracts/measurement_methodology.md`,
  `docs/contracts/run_bundle_layout.md`,
  `docs/contracts/adapter_contracts.md`, plus the typed schemas in
  `joulewise/schemas.py` and interfaces in `joulewise/interfaces.py`

## Goal

Lock the benchmark contract before building the full harness: make the
measurement methodology explicit, classify hardware feasibility with
evidence, and leave Phase 2 ready to implement the mock-first path toward
the Mac MLX + powermetrics vertical slice.

## Deliverables

Complete (see `AGENT_PLAN.md` Phase 1 checklist and the run reports for
the trail):

- Benchmark config contract and standardized run-output contract, with
  validation tests and CLI helpers.
- Runtime/telemetry/transport adapter contracts.
- Run-bundle layout (now in `docs/contracts/`).
- Measurement methodology incl. boundaries, clock sync, co-residency,
  repetition/thermal, and statistical protocol (now in `docs/contracts/`).
- Example Mac-local and mock-local configs that validate.
- Planning infrastructure: per-phase plans and exit checklists, decision
  log, risk register, milestone map.

Remaining (the steps below; evidence recorded in the exit checklist):

- Supervisor approval and scope confirmation.
- Mac telemetry/runtime evidence completion.
- Wall-meter decision.
- Network/interconnect plan with physical topology.
- Hailo feasibility verdict.
- NVIDIA/Orin access evidence.
- Calendar mapping.
- Phase 2 readiness review.

## How To Execute This Plan (Agent Protocol)

- Steps here are evidence-gathering, not implementation: each closes when
  its evidence is recorded in the named section of
  `phase_1_exit_checklist.md`. Several are `waiting-user`; an agent run
  that cannot advance them should record exactly what input is missing and
  pick hardware-independent work instead (Phase 2 slices 2A-2F are always
  safe once prioritized).
- Convention for evidence location (applies to all phases): evidence is
  recorded in the phase exit checklist; when a topic's evidence outgrows
  the checklist, it moves to a dedicated file under the phase directory
  and the checklist links it (Phase 3's `kv_feasibility.md` is the
  pattern).
- Steps may complete in any order except Step 8, which consumes the rest.

## Constraints During Phase 1

- Do not change schemas or adapter interfaces unless a Phase 1 evidence
  item proves the current contract wrong (then: decision-log entry plus
  same-run doc updates).
- Do not implement live telemetry, dashboards, or runtime adapters yet;
  the queue's do-not-do-yet list governs.
- Do not alter Git history or author identity unless requested.

## Steps

### Step 1: Supervisor Scope Evidence (queue P1-001)

Status: open. This is the highest-impact gate (R-001).

Objective: lock what the capstone must deliver and what can slip.

Inputs: supervisor meeting/email; current proposal; `AGENT_PLAN.md`;
the exit checklist's supervisor section (it lists the exact questions).

Actions: confirm the primary artifact (JouleWise harness) and the
validating study (disaggregation); required hardware scope; Hailo's status
as feasibility-finding rather than must-succeed backend; stretch items
(split quantization, minimal router); final deliverables (repo, report,
raw traces/configs, colloquium); whether mock-first Phase 2 work may
proceed before all hardware checks.

Evidence: dated notes in the exit checklist's supervisor section;
`RUN_STATE.md` updated if scope changes.

Acceptance criteria: must-haves, stretch items, and out-of-scope items are
written down; no Phase 2 work depends on an unstated expectation.

Fallback: if approval is delayed, continue only hardware-independent
harness work and mark hardware purchases/borrows blocked-on-approval.

### Step 2: Mac-Local Evidence (queue P1-002)

Status: partially complete; waiting-user (auth session 2026-06-10).
Captured so far (full detail in the exit checklist's instrumentation
section): `powermetrics` present but requires superuser; useful samplers
identified; MLX/MLX-LM not installed.

Objective: make the first real vertical-slice target concrete for Phase 2.

Inputs: the MacBook; the 2026-06-10 auth session; D-004 (privilege
workflow).

Actions (post-auth): capture one privileged `powermetrics` sample
(`powermetrics -n 1 -i 100 --samplers thermal,cpu_power,gpu_power,ane_power`);
record the available power/thermal field names (they pin the Slice 2H
parser); install and verify the D-004 scoped sudoers rule via `sudo -n`;
decide and record the MLX install path (dedicated venv, `[mac]` extra).

Evidence: updated instrumentation section of the exit checklist.

Acceptance criteria: Mac target classified for runtime and telemetry:
`supported`, `pending_install`, or `permission_blocked` - with the
privileged sample's field list recorded.

Fallback: if MLX installation is not approved, record `pending_install`
and keep Phase 2 mock-first; if the sudoers rule is declined, R-002
fallbacks apply.

### Step 3: Wall-Meter Decision (queue P1-003)

Status: open.

Objective: decide whether system-level AC power is available for boundary
calibration (D-018) and Pi/Hailo coverage.

Inputs: lab equipment answer or purchase decision; meter documentation.

Actions: record meter make/model, sample rate, precision, export/manual
logging method, and which targets need wall-meter fallback; define how
readings align with run timestamps.

Evidence: wall-meter section of the exit checklist.

Acceptance criteria: wall-meter path is `available`, `to-buy`, or
`unavailable` with consequences documented per target.

Fallback: if unavailable, platform telemetry stands alone; cross-target
comparisons carry the D-018 boundary caveat permanently (R-007).

### Step 4: Network Plan Evidence (queue P1-004)

Status: partial - controller-side tool status captured 2026-06-09; the
physical topology, link-speed paths, and throughput method are pending.

Objective: make the Phase 3 interconnect sweep executable before hardware
time is spent.

Inputs: available nodes, switch/adapters/cables, campus or local network
constraints.

Actions: record the physical topology (controller/prefill/decode nodes,
switch and adapter models, cable types, isolation status - direct
node-to-node cabling preferred per R-011); confirm which link speeds have
hardware paths (1GbE, 2.5GbE, optional 10GbE); record the link-speed
verification command per node and the throughput method (`iperf3` or
fixed-size transfer).

Evidence: network section of the exit checklist.

Acceptance criteria: the sweep has a known topology and verification
method, or a documented blocker; transfer-event fields align with the
bundle layout.

Fallback: if hardware is unavailable, record the planned topology and mark
physical verification pending.

### Step 5: Hailo Verdict (queue P1-005)

Status: open. Expected-negative is an acceptable outcome by design
(R-009): the verdict itself is a reportable applicability finding.

Objective: decide whether Pi + Hailo enters implementation or becomes an
unsupported-hardware finding.

Inputs: Pi 5 + Hailo-8L access; Hailo toolchain and docs; a candidate
LLM-shaped workload.

Actions: record SDK/toolchain version; check supported operator families
against attention/KV access patterns; attempt one minimal LLM-shaped
compile or runtime path if plausible, else cite the exact limitation;
record whether energy could be measured (wall meter) even if the runtime
works.

Evidence: Hailo section of the exit checklist - verdict code
(`supported`, `runtime_unavailable`, `format_unavailable`,
`unsupported_workload`, `telemetry_unavailable`) plus the supporting
commands/notes.

Acceptance criteria: future phases can include or exclude Hailo without
re-litigating feasibility.

Fallback: if device access is unavailable, keep `pending` and record
exactly what access is missing.

### Step 6: Remote NVIDIA/Orin Evidence (queue P1-006)

Status: open. Gates Phase 2 slices 2K and 2L.

Objective: know which remote targets can serve Phase 2 baselines and
Phase 3 splits.

Inputs: SSH access details; the 3050 machine; Orin Nano; 3080 Ti borrow
arrangement (R-006).

Actions: per target record - SSH reachability; runtime availability or
install blocker (vLLM vs llama.cpp-CUDA per the 2K fallback); telemetry
command evidence (`nvidia-smi --query-gpu=power.draw` support; Orin
INA3221 sysfs paths or `tegrastats`); memory limits; for the 3080 Ti, the
borrow-window constraints.

Evidence: instrumentation section of the exit checklist.

Acceptance criteria: each target classified supported/pending/blocked for
runtime and telemetry.

Fallback: mark pending with the missing access named; Phase 2 proceeds
mock-first/Mac-local.

### Step 7: Calendar Mapping (queue P1-008)

Status: waiting-user.

Objective: anchor the phase plan to real deadlines (R-012).

Inputs: colloquium date, report due date, borrow window, from the user.

Actions: enter dates in `docs/milestones.md`; derive phase target dates
backwards (slides want frozen figures >=1 week ahead; report wants the
claims-index pass >=1 week ahead); flag any phase whose runway looks
short and apply the descope ladder proactively.

Evidence: `docs/milestones.md` dates filled; exit checklist row closed.

Acceptance criteria: every phase has a target end date and the critical
hardware windows are scheduled or explicitly floating.

Fallback: none - this is pure user input; until provided, the dependency
structure in `docs/milestones.md` is the schedule.

### Step 8: Phase 2 Readiness Review (queue P1-007)

Status: open; last step - consumes all the others.

Objective: decide whether implementation can responsibly start.

Inputs: this plan's steps 1-7 outcomes; the exit checklist; current tests.

Actions: confirm examples validate and tests pass; confirm every gate
above has evidence, a verdict, or a documented blocker; confirm the top
implementation task is P2-001 (slices 2A-2E) and that gated slices (2G+)
have their gate evidence or remain explicitly blocked.

Evidence: Phase 2 readiness note in the exit checklist; `TASK_QUEUE.md`
and `RUN_STATE.md` updated.

Acceptance criteria: Phase 2 can start with mock work without depending on
unverified hardware; the Phase 2 plan's gate lines are all accurate.

Fallback: if major gates remain unknown, continue Phase 1 evidence work;
do not start live hardware integrations.

## Exit

Governed by `docs/phase_1/phase_1_exit_checklist.md`: every required item
in its evidence matrix has evidence, a verdict, or a documented blocker,
and the Phase 2 readiness review is recorded.
