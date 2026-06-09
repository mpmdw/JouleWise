# JouleWise Task Queue

This is the live queue for JouleWise work. When the user gives a new task, first
triage it here instead of assuming it should happen immediately.

## Intake Rule For New Tasks

For every new user task:

1. Read `RUN_STATE.md`.
2. Read this file.
3. Check `git status --short --branch`.
4. Review the last 2-3 commits with `git log --oneline --decorate -3`.
5. Check relevant handoffs in `docs/run_reports/`.
6. Decide whether the task is:
   - urgent workspace hygiene,
   - Phase 1 evidence work,
   - Phase 2 implementation prep,
   - later-phase research work,
   - documentation/reporting,
   - or unrelated/new scope.
7. Place or update the task in the queue with priority, rationale, evidence,
   and blockers.
8. If executing it now, say why it outranks the current top task.

## Priority Scale

- **P0 Safety**: prevents accidental data loss, bad commits, broken handoffs, or
  corrupted repo state.
- **P1 Phase Gate**: required to close the current phase or unblock the next
  phase responsibly.
- **P2 Next Slice**: next implementation slice after current phase gates are
  adequately planned or closed.
- **P3 Research Expansion**: useful experiment or feature, but not needed for
  current gate.
- **P4 Polish**: quality-of-life, dashboard polish, formatting, cleanup, or
  presentation work.

## Ranking Factors

Rank higher when a task:

- Prevents accidental loss or bad Git history.
- Produces evidence for `docs/phase_1/phase_1_exit_checklist.md`.
- Removes ambiguity for multiple later steps.
- Is required before physical hardware time is spent.
- Is cheap to verify and reduces future confusion.
- Matches the current phase better than jumping ahead.

Rank lower when a task:

- Depends on unavailable hardware or supervisor input.
- Is a later-phase feature.
- Adds polish before a runnable vertical slice exists.
- Produces code without a clear run-bundle or test artifact.

## Current Queue

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---:|---|---|---|---|---|
| 1 | Q-000 | P0 Safety | open | Resolve the local `Energy_Benchmark_Architecture.docx` deletion decision | User confirms restore/remove/ignore; no accidental commit of deletion |
| 2 | P1-001 | P1 Phase Gate | open | Capture supervisor approval and scope notes | Dated notes in `docs/phase_1/phase_1_exit_checklist.md`; `RUN_STATE.md` updated if scope changes |
| 3 | P1-002 | P1 Phase Gate | partial | Complete Mac-local Phase 1 telemetry/runtime evidence | `powermetrics` binary/help/privilege behavior and MLX absence recorded; privileged sample fields and MLX install path still pending |
| 4 | P1-003 | P1 Phase Gate | open | Record wall-meter decision | Meter make/model or "unavailable" verdict plus measurement/export method |
| 5 | P1-004 | P1 Phase Gate | partial | Fill network/interconnect topology plan | Controller command/tool status recorded; physical topology, link-speed paths, and throughput method still pending |
| 6 | P1-005 | P1 Phase Gate | open | Complete Hailo feasibility verdict | Verdict code and evidence recorded in `docs/phase_1/hailo_feasibility.md` |
| 7 | P1-006 | P1 Phase Gate | open | Confirm NVIDIA/Orin telemetry access paths | SSH/runtime/telemetry command evidence recorded or marked pending with blocker |
| 8 | P1-007 | P1 Phase Gate | open | Perform Phase 2 readiness review | `docs/phase_1/phase_1_exit_checklist.md` states mock-first Phase 2 can begin |
| 9 | P2-001 | P2 Next Slice | queued | Implement mock run-bundle vertical slice | One command creates a complete mock run bundle and tests pass |
| 10 | P2-002 | P2 Next Slice | queued | Implement reducer for deterministic synthetic traces | Reducer test computes gross and idle-subtracted energy from known samples |
| 11 | P2-003 | P2 Next Slice | queued | Begin Mac MLX + powermetrics vertical slice | Only after mock bundle/reducer path exists |

## Current Do-Not-Do-Yet List

- Do not start dashboard polish before the mock bundle/reducer path exists.
- Do not start live MLX/powermetrics implementation before the mock lifecycle is
  runnable.
- Do not commit the local Word-doc deletion without explicit user approval.
- Do not spend time on Hailo implementation until feasibility has a verdict.

## Queue Maintenance

At the end of substantial work:

- Update statuses in this file.
- Add new tasks discovered during the run.
- Move completed tasks below or mark them `done`.
- Update `RUN_STATE.md` with the next highest-ranked task.
