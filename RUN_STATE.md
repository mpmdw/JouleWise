# JouleWise Run State

Last updated: 2026-06-09

## Start Here For Every Big Run

Before starting substantial work:

1. Read this file.
2. Read `TASK_QUEUE.md`.
3. Read `AGENT_PLAN.md` (phase index) and the active phase's plan doc under
   `docs/phase_N/`.
4. Read `docs/planning_reflection_protocol.md`.
5. Check `docs/decision_log.md` before re-deciding anything; check
   `docs/risk_register.md` if starting a phase or a hardware-dependent task.
6. Check the last 2-3 commits with `git log --oneline --decorate -3`.
7. Check `git status --short --branch`.
8. Run `python3 -m unittest discover -s tests` unless the task is docs-only.
9. Do not commit local deletions or unrelated changes unless the user asks.

At the end of substantial work:

1. Update this file with what changed.
2. Update `TASK_QUEUE.md` with completed, added, or re-ranked tasks.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, blockers, and the next best task.
5. Record new decision-log entries and any risk-register status changes.
6. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

JouleWise is in Phase 1: approval, feasibility, and measurement design.

The repo has a scaffolded, tested foundation (schemas, adapter interfaces,
example configs, CLI helpers) and - as of this run - a fully built-out,
evidence-shaped plan for Phases 2 through 5, plus a decision log, risk
register, and milestone map. There is not yet a runnable measurement
harness; that is Phase 2 slice work, which is now specified in detail.

## What This Run Did (2026-06-09, planning buildout)

User-directed planning audit and buildout. Found that Phases 2-5 failed the
repo's own planning bar (checklist-shaped, no evidence/acceptance per step,
ordering drift vs the queue, undecided design questions, no risk/calendar
tracking) and fixed it:

- Added per-phase plans + exit checklists:
  - `docs/phase_2/phase_2_plan.md` (13 slices, mock-first, gates) +
    exit checklist with conditional-exit rules and applicability table.
  - `docs/phase_3/phase_3_plan.md` (feasibility-first ladder per D-015,
    KV-size model with worked tables, stages 3.0-3.4) + exit checklist.
  - `docs/phase_4/phase_4_plan.md` (protocol ratification, aggregation,
    figure registry F1-F8, claims-to-evidence index, sensitivity audit) +
    exit checklist.
  - `docs/phase_5/phase_5_plan.md` (verified quickstart/guide/samples,
    dataset freeze, slides, report) + exit checklist.
- Added `docs/decision_log.md` with D-001..D-019, each with options
  considered and considerations (per user request for structural
  auditability).
- Added `docs/risk_register.md` (R-001..R-015) including the descope ladder
  and the KV-portability risks the user flagged.
- Added `docs/milestones.md` (calendar skeleton; dates TBD pending P1-008).
- Amended `docs/phase_1/measurement_methodology.md`: measurement
  boundaries table, clock sync/multi-node alignment, controller
  co-residency, repetition/thermal protocol, statistical protocol,
  `deserialize` phase label + split-stage accounting.
- Amended `docs/phase_1/run_bundle_layout.md`: `config.json` (D-001),
  `raw/` dir, completion-marker semantics (D-011), experiment manifests
  (D-005), composite split-bundle preview.
- Restructured `AGENT_PLAN.md` into the phase index with a single-source-
  of-truth map; fixed the Phase 2 mock-first ordering drift; removed the
  stale Word-doc ground rule.
- Marked the resolved Word-doc step in
  `docs/phase_1/phase_1_continuation_plan.md`.
- Updated `TASK_QUEUE.md`: new tasks P1-008 (calendar), P2-004 (model
  selection), P3-000 (KV spikes); slice references; expanded
  do-not-do-yet list; PLAN-001 and CI-001 recorded complete.
- Added `.github/workflows/ci.yml` (D-017: core tests on 3.11/3.14 +
  config-validation smoke).
- Added `.DS_Store` to `.gitignore`; README points to the new docs.

Anomaly noted: two transient `EPERM: operation not permitted` errors while
accessing `docs/phase_1/measurement_methodology.md` and listing
directories mid-run (macOS Desktop permissions hiccup, most likely);
access recovered on retry without intervention. If it recurs, check
System Settings privacy permissions for the terminal.

## Current Verification

Command:

```bash
python3 -m unittest discover -s tests
```

Result (this run, docs-only changes - expected unchanged):

```text
Ran 14 tests
OK
```

CLI smoke:

```bash
python3 -m joulewise validate-config configs/examples/mac_mlx_local.json
```

## Known Workspace State

- Remote: `git@github.com:mpmdw/JouleWise.git`
- Branch: `main`, tracking `origin/main`
- Use `git log --oneline --decorate -3` for the latest pushed commit.

## What Is Next

Follow `TASK_QUEUE.md`. The top items:

1. P1-001: capture supervisor approval/scope notes in
   `docs/phase_1/phase_1_exit_checklist.md`.
2. P1-002 (after the user's 2026-06-10 auth session): capture one
   privileged `powermetrics` sample, record available power/thermal fields
   in `docs/phase_1/instrumentation_checklist.md`, and install/record the
   D-004 scoped sudoers rule. Key command:
   `powermetrics -n 1 -i 100 --samplers thermal,cpu_power,gpu_power,ane_power`
   (and the same via `sudo -n` to verify the rule).
3. P1-008: enter colloquium/report dates and the borrow window in
   `docs/milestones.md` when the user provides them.
4. First implementation work when prioritized: P2-001 = slices 2A-2E per
   `docs/phase_2/phase_2_plan.md`, in order, one slice per session.

## Open Decisions And Blockers

- Supervisor approval and scope confirmation pending (P1-001, R-001).
- Calendar dates pending user input (P1-008, R-012).
- Hailo feasibility pending (P1-005; expected-negative is fine, R-009).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates slices 2K/2L).
- Mac evidence partially captured; privileged powermetrics sample waits on
  the 2026-06-10 auth session (P1-002, R-002).
- D-016 (model selection) is open with criteria fixed; closes during
  Phase 2 at the model checkpoint.
- Git author identity was auto-selected as `Edr <edr@Edrs-MacBook-Air.local>`
  for the first commit. Amend future commits if a different identity is
  needed.
