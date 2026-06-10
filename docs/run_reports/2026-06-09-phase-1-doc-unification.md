# 2026-06-09: Phase 1 Doc-Scheme Unification

## Start-Of-Run Reflection

Goal:

- User-directed: enforce uniformity across the phase documentation scheme.
  Phase 1 predated the per-phase plan/exit-checklist structure introduced
  for Phases 2-5 and had a different shape (overview README, a
  differently-named continuation plan, three loose evidence docs, and
  cross-phase contracts mixed into the phase directory). Shrink it to the
  uniform shape.

Prior state inspected:

- `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENT_PLAN.md`
- All of `docs/phase_1/` (pre-change), the Phase 2-5 plan docs
- Grep map of every reference to the old Phase 1 paths

Queue decision:

- Triaged as DOC-001 (P4 polish by the scale, but user-directed and
  cheap-to-verify); executed immediately because the user requested it
  this session and because structural drift between phase docs is exactly
  the failure mode the single-source-of-truth map exists to prevent -
  fixing it now is cheaper than after Phase 1 evidence lands in the old
  files.

Design decision for the consolidation (recorded here; no decision-log
entry because it binds documentation shape, not implementation):

- Cross-phase contracts do not belong inside a phase directory. Moved
  `measurement_methodology.md`, `run_bundle_layout.md`, and
  `adapter_contracts.md` to `docs/contracts/` via `git mv` (history
  preserved); each gained a living-contract header line; methodology
  dropped "Draft" from its title.
- Phase planning material consolidated to exactly two files, matching
  Phases 2-5: `phase_1_plan.md` (goal, deliverables, agent protocol,
  constraints, Steps 1-8 in the uniform objective/inputs/actions/
  evidence/acceptance/fallback format) and `phase_1_exit_checklist.md`
  (the evidence dossier: required evidence definitions *and* recorded
  evidence in one place).
- Convention stated in the plan so the scheme stays coherent: evidence
  lives in the phase exit checklist until a topic outgrows it, then moves
  to a dedicated file under the phase dir linked from the checklist
  (Phase 3's planned `kv_feasibility.md` already follows this).
- Phase 1 records *access* evidence; Phase 2 implementation verdicts go to
  the Phase 2 exit checklist's applicability table. References in the
  Phase 2 plan were split accordingly.

## What Changed

Moved (git mv): `docs/phase_1/{measurement_methodology,run_bundle_layout,adapter_contracts}.md`
-> `docs/contracts/`.

Created: `docs/phase_1/phase_1_plan.md` (Steps 1-8 absorb the former
continuation plan and README, statuses synced to the queue, plus the new
calendar step).

Rewritten: `docs/phase_1/phase_1_exit_checklist.md` - now the dossier,
absorbing all recorded evidence from the former `hailo_feasibility.md`
(questions, verdict codes, `pending` verdict), `network_plan.md` (target
links, topology fields, 2026-06-09 controller evidence: `ifconfig`/`en0`
works, `networksetup` AuthorizationCreate -60008 failure, no `iperf3`;
link-verification and throughput templates; transfer measurement policy;
open items), and `instrumentation_checklist.md` (Mac observations:
`/usr/bin/powermetrics`, superuser requirement, plist + samplers, MLX/
MLX-LM absent, arm64, uid 501, evidence command block; NVIDIA 3050 /
3080 Ti / Orin / Pi+Hailo check states). No recorded evidence was dropped.

Deleted (content merged): `docs/phase_1/README.md`,
`phase_1_continuation_plan.md`, `hailo_feasibility.md`, `network_plan.md`,
`instrumentation_checklist.md`.

Reference updates: `AGENT_PLAN.md` (map -> `docs/contracts/`, adapter
contracts row added, Phase 1 detail line uniform), `TASK_QUEUE.md`
(P1-002..P1-006 destinations -> exit-checklist sections),
`docs/decision_log.md` (D-001 path, D-004 destinations),
`docs/risk_register.md` (R-002, R-009), `docs/phase_2/phase_2_plan.md`
(contract paths; access-vs-applicability destination split),
`docs/phase_2/phase_2_exit_checklist.md` (applicability-table
destinations), `docs/phase_3/phase_3_plan.md` (network references).
`RUN_STATE.md` rewritten for this run.

Intentionally unchanged: historical run reports (they reference the old
paths as they existed at their dates); `joulewise/` code and tests;
schemas; `docs/planning_reflection_protocol.md`.

## Commands Run

```bash
git mv docs/phase_1/{measurement_methodology,run_bundle_layout,adapter_contracts}.md docs/contracts/
git rm docs/phase_1/{README,phase_1_continuation_plan,hailo_feasibility,network_plan,instrumentation_checklist}.md
grep -rn "phase_1/(...old names...)"   # reference map before; re-run after = only historical reports
python3 -m unittest discover -s tests  # 14 tests, OK
```

## What Passed / Failed / Was Uncertain

- Tests: 14 OK (docs-only).
- Post-change grep confirms no live references to the old paths remain
  (only dated run reports, which are historical records).
- Interpretation note: the user's request said "testing suite" but
  specified the doc scheme for Phase 1 vs 2-5; this run treated it as the
  evidence/exit-checklist documentation scheme. The Python test suite was
  already uniform and untouched.

## What The Next Agent Should Do First

Unchanged from the queue: P1-001 (supervisor notes - the question list now
lives in the exit checklist's supervisor section), then P1-002 after the
2026-06-10 auth session (record the privileged sample fields in the exit
checklist's instrumentation section). The uniform rule of thumb now holds
everywhere: read `docs/phase_N/phase_N_plan.md` for what to do, record
proof in `docs/phase_N/phase_N_exit_checklist.md`.
