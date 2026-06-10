# Phase 1 Continuation Plan

This plan starts from the current Phase 1 state after the scaffold, handoff
protocol, and evidence gates were added.

## Start-Of-Run Reflection

Goal:

- Continue Phase 1 by converting pending evidence gates into recorded decisions,
  command evidence, or explicit blockers.

Prior state to inspect before acting:

- `RUN_STATE.md`
- `TASK_QUEUE.md`
- `AGENT_PLAN.md`
- `docs/planning_reflection_protocol.md`
- `docs/phase_1/phase_1_exit_checklist.md`
- Latest 2-3 Git commits
- Current `git status --short --branch`

Inherited assumptions:

- JouleWise is still in Phase 1.
- The implementation should remain mock-first before physical telemetry work.
- Physical hardware evidence may be unavailable in a given run; if so, record a
  blocker rather than pretending the item is complete.
- (Resolved 2026-06-09, queue item Q-000:) the
  `Energy_Benchmark_Architecture.docx` deletion was confirmed unrelated to
  the project and committed in `a5d7404`; it is no longer a workspace
  concern.

What should not change during Phase 1 continuation:

- Do not change schemas or adapter interfaces unless a Phase 1 evidence item
  proves the current contract is wrong.
- Do not implement dashboard or live telemetry yet.
- Do not change the Git history or author identity unless requested.

## Continuation Steps

### Step 0: Workspace Safety Check

Status: resolved 2026-06-09. The Word-doc question (queue item Q-000) was
answered by the user - the file was unrelated to the project - and the
deletion was committed in `a5d7404`. The general habit this step encoded
(check `git status` before substantial work; never commit unrelated local
state) is now a standing rule in `RUN_STATE.md` and needs no per-run step
here.

Original step retained below for the audit trail:

Objective:

- Prevent accidental commits of unrelated or destructive state.

Inputs:

- `git status --short --branch`
- `TASK_QUEUE.md`

Actions:

- Check whether `Energy_Benchmark_Architecture.docx` is still deleted locally.
- Ask the user before restoring, removing, or committing that deletion.
- Keep all Phase 1 planning commits scoped to docs/planning files.

Evidence:

- Run report notes the working-tree state.
- No staged deletion unless explicitly requested.

Acceptance criteria:

- The Word-doc deletion is either explicitly resolved or remains documented and
  unstaged.

Fallback:

- If the user is unavailable, leave it unstaged and continue only with unrelated
  docs/planning changes.

### Step 1: Supervisor Scope Evidence

Objective:

- Close or update the highest-impact Phase 1 gate: what the capstone must
  deliver.

Inputs:

- Supervisor meeting/email.
- Current proposal.
- `AGENT_PLAN.md`
- `docs/phase_1/phase_1_exit_checklist.md`

Actions:

- Record approved must-haves.
- Record stretch items.
- Record out-of-scope items.
- Record whether Hailo is a must-succeed backend or feasibility finding.
- Record whether Phase 2 mock-first work may proceed before all hardware checks.

Evidence:

- Dated note in `docs/phase_1/phase_1_exit_checklist.md`.
- `RUN_STATE.md` updated if scope changes.

Acceptance criteria:

- Future implementation can distinguish required deliverables from stretch work.

Fallback:

- If supervisor input is unavailable, mark the gate blocked and proceed only
  with hardware-independent mock harness work.

### Step 2: Mac-Local Evidence

Objective:

- Make the first real vertical-slice target concrete enough for Phase 2.

Inputs:

- Current MacBook.
- `powermetrics` binary.
- MLX install status or planned install path.

Actions:

- Record `powermetrics` path.
- Determine whether `powermetrics` requires sudo/password interaction.
- Record a sample command that exposes power or thermal fields.
- Check whether MLX is installed or needs installation.
- Record any permission blockers.

Evidence:

- Updated `docs/phase_1/instrumentation_checklist.md`.

Acceptance criteria:

- Mac target has known runtime and telemetry status:
  `supported`, `pending_install`, or `permission_blocked`.

Fallback:

- If MLX is not installed and network/dependency installation is not approved,
  record `pending_install` and continue with mock-first Phase 2 planning.

### Step 3: Wall-Meter Decision

Objective:

- Decide whether system-level AC power is available for calibration/fallback.

Inputs:

- Lab equipment answer or purchase decision.
- Any available meter documentation.

Actions:

- Record meter make/model.
- Record sample rate, precision, and export/manual logging method.
- Record which targets need wall-meter fallback.

Evidence:

- Updated `docs/phase_1/instrumentation_checklist.md`.

Acceptance criteria:

- Wall-meter path is either available, to-buy, or unavailable with consequence
  documented.

Fallback:

- If unknown, keep targets needing wall power marked pending and avoid claiming
  full measurement coverage.

### Step 4: Network Plan Evidence

Objective:

- Make Phase 3 interconnect experiments executable before hardware time.

Inputs:

- Known nodes.
- Switch/adapters/cables.
- Campus or local network constraints.

Actions:

- Fill topology in `docs/phase_1/network_plan.md`.
- Record which link speeds have hardware paths.
- Record verification commands for macOS/Linux interfaces.
- Record throughput test method.

Evidence:

- Updated `docs/phase_1/network_plan.md`.

Acceptance criteria:

- The interconnect sweep has a known topology and verification method, or a
  documented blocker.

Fallback:

- If hardware is unavailable, record the planned topology and mark physical
  verification pending.

### Step 5: Hailo Verdict

Objective:

- Decide whether Pi + Hailo enters implementation or becomes an unsupported
  applicability finding.

Inputs:

- Pi/Hailo access.
- Hailo toolchain/version.
- Hailo docs or candidate workload.

Actions:

- Record toolchain status.
- Attempt or document inability to attempt an LLM-shaped compile/runtime.
- Assign a verdict code.

Evidence:

- Updated `docs/phase_1/hailo_feasibility.md`.

Acceptance criteria:

- Future phases can include or exclude Hailo without re-opening feasibility.

Fallback:

- If device access is unavailable, keep `pending` but record exactly what access
  is missing.

### Step 6: Remote NVIDIA/Orin Evidence

Objective:

- Know which remote targets can be used for Phase 2 baselines and Phase 3 splits.

Inputs:

- SSH access details.
- NVIDIA and Orin nodes.

Actions:

- Record whether SSH works.
- Record runtime availability or install blocker.
- Record telemetry command availability.
- Record memory/device limits when known.

Evidence:

- Updated `docs/phase_1/instrumentation_checklist.md`.

Acceptance criteria:

- Each target is classified as supported, pending, or blocked for runtime and
  telemetry.

Fallback:

- If access is unavailable, mark pending and keep the next implementation step
  mock-first/local-only.

### Step 7: Phase 2 Readiness Review

Objective:

- Decide whether the repo can start Phase 2 implementation responsibly.

Inputs:

- `docs/phase_1/phase_1_exit_checklist.md`
- `TASK_QUEUE.md`
- Current tests.

Actions:

- Confirm examples validate.
- Confirm adapter contracts and run-bundle layout exist.
- Confirm all hardware/supervisor gaps have evidence, a verdict, or a blocker.
- Confirm the top implementation task is `P2-001` mock run-bundle vertical slice.

Evidence:

- Phase 2 readiness note in `docs/phase_1/phase_1_exit_checklist.md`.
- `TASK_QUEUE.md` updated.
- `RUN_STATE.md` updated.

Acceptance criteria:

- Phase 2 can start with mock bundle/controller/reducer work without depending
  on unverified hardware.

Fallback:

- If major Phase 1 gates remain unknown, continue Phase 1 evidence work and do
  not start live hardware integrations.
