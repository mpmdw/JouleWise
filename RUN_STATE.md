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
6. Refresh `PROJECT_STATUS.md` if advisor-visible state changed (phase or
   gate closed, verdict landed, schedule moved).
7. Call out any dirty working-tree state that should not be accidentally
   committed.

## Current Project Status

JouleWise is in Phase 1: approval, feasibility, and measurement design.

Every phase now follows one documentation scheme:
`docs/phase_N/phase_N_plan.md` (steps with objectives, evidence, acceptance,
fallbacks) + `docs/phase_N/phase_N_exit_checklist.md` (evidence dossier).
Cross-phase contracts live in `docs/contracts/` (methodology, bundle layout,
adapter contracts); cross-phase registries live in `docs/` (decision log,
risk register, milestones). The repo has a scaffolded, tested foundation;
the runnable harness is Phase 2 slice work, fully specified in its plan.

## What This Run Did (2026-06-09, advisor status doc + sketch audit)

User-directed follow-up to the doc unification:

- Added root-level `PROJECT_STATUS.md`: standalone advisor-facing status,
  plan, and architecture document, shaped after the original
  "Energy Benchmark Architecture And Expanded Plan" sketch (found at
  `../Energy_Benchmark_Architecture.docx`, the source of the user's
  paste) and extended with status-at-a-glance, methodology highlights,
  the experiment plan, risk/floor summary, timeline asks, and a
  repository map. Maintenance rule added to `AGENT_PLAN.md` ground rules
  and this file's end-of-run list: refresh it when advisor-visible state
  changes.
- Audited the original sketch against current thinking: architecture
  survives intact; refinements are documented decisions (JSON/stdlib over
  YAML/Pydantic for now, mock-first before the Mac slice, static-HTML
  dashboard, KV feasibility ladder with same-runtime rule replacing the
  implicit GPU-to-Apple live-split assumption, added
  boundaries/clock/statistics rigor). No contradictions found; the
  audit's mapping table lives in `PROJECT_STATUS.md` ("Evolution From The
  Original Architecture Sketch") and the run report.
- Note: queue history (Q-000) records the repo *copy* of that .docx as
  removed per user instruction; the file in the parent folder is the
  proposal-era sketch and remains outside the repo. Its content is
  superseded by the in-repo plans; `PROJECT_STATUS.md` is now the
  maintained equivalent.

## Prior Run (2026-06-09, Phase 1 doc-scheme unification)

User-directed: make Phase 1's documentation structurally uniform with
Phases 2-5 by consolidation.

- Moved the cross-phase contracts out of `docs/phase_1/` into
  `docs/contracts/` (git mv, history preserved):
  `measurement_methodology.md` (retitled from "Draft", living-contract
  header added), `run_bundle_layout.md`, `adapter_contracts.md`.
- Created `docs/phase_1/phase_1_plan.md` in the uniform format: goal,
  deliverables, agent protocol, constraints, and Steps 1-8 (supervisor
  scope, Mac evidence, wall meter, network, Hailo, NVIDIA/Orin, calendar,
  readiness review) with objective/inputs/actions/evidence/acceptance/
  fallback each, statuses matching the queue.
- Rewrote `docs/phase_1/phase_1_exit_checklist.md` as the phase's evidence
  dossier: it now defines required evidence *and* records it - absorbing
  the full recorded evidence from the former `hailo_feasibility.md`,
  `network_plan.md`, and `instrumentation_checklist.md` (all 2026-06-09
  observations preserved verbatim: powermetrics path/privilege/samplers,
  MLX absence, arm64/uid, ifconfig/networksetup/iperf3 status, per-target
  checkbox states, verdict codes).
- Deleted the five superseded files: `docs/phase_1/README.md`,
  `phase_1_continuation_plan.md`, `hailo_feasibility.md`,
  `network_plan.md`, `instrumentation_checklist.md` (content merged; git
  history retains the originals; old run reports intentionally keep their
  historical references).
- Stated the evidence-location convention (in the Phase 1 plan): evidence
  lives in the phase exit checklist until a topic outgrows it, then moves
  to a dedicated file under the phase dir (Phase 3's `kv_feasibility.md`
  is the pattern).
- Updated every live cross-reference: `AGENT_PLAN.md` (source-of-truth map
  rows -> `docs/contracts/`, adapter-contracts row added, Phase 1 detail
  line made uniform), `TASK_QUEUE.md` (P1-002..P1-006 evidence
  destinations -> exit-checklist sections), `docs/decision_log.md`
  (D-001/D-004), `docs/risk_register.md` (R-002/R-009),
  `docs/phase_2/phase_2_plan.md` (contract paths; Phase 1 access evidence
  vs Phase 2 applicability-table destinations split correctly),
  `docs/phase_2/phase_2_exit_checklist.md`, `docs/phase_3/phase_3_plan.md`.

## Current Verification

Command:

```bash
python3 -m unittest discover -s tests
```

Result (docs-only change set):

```text
Ran 14 tests
OK
```

Reference check: `grep -rn 'phase_1/\(measurement_methodology\|run_bundle_layout\|adapter_contracts\|instrumentation_checklist\|network_plan\|hailo_feasibility\|phase_1_continuation_plan\|README\)'`
returns only historical run reports.

## Known Workspace State

- Remote: `git@github.com:mpmdw/JouleWise.git`
- Branch: `main`, tracking `origin/main`
- Use `git log --oneline --decorate -3` for the latest pushed commit.
- Known prior anomaly (2026-06-09, earlier run): transient `EPERM` errors
  reading files under `docs/` that recovered on retry; suspected macOS
  Desktop privacy hiccup. Watch for recurrence.

## What Is Next

Follow `TASK_QUEUE.md`. The top items:

1. P1-001: capture supervisor approval/scope notes in the supervisor
   section of `docs/phase_1/phase_1_exit_checklist.md` (the question list
   is in that section).
2. P1-002 (after the user's 2026-06-10 auth session): capture one
   privileged `powermetrics` sample, record the available power/thermal
   field names in the exit checklist's instrumentation section, and
   install/verify the D-004 scoped sudoers rule. Key command:
   `powermetrics -n 1 -i 100 --samplers thermal,cpu_power,gpu_power,ane_power`
   (then the same via `sudo -n` to verify the rule).
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
