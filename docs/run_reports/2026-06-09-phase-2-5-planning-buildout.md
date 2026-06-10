# 2026-06-09: Phase 2-5 Planning Buildout

## Start-Of-Run Reflection

Goal:

- User-directed: audit the whole plan, and if planning is lacking, build
  verbose, evidence-shaped, agent-executable plans for all phases, with
  every design decision recorded alongside its considerations
  (structural auditability), reviewed with the user before execution.

Prior state inspected:

- `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENT_PLAN.md`
- `docs/planning_reflection_protocol.md`
- All of `docs/phase_1/`
- All six prior run reports
- `joulewise/` source, tests (executed: 14 OK), example configs,
  `pyproject.toml`
- Git log and status

Inherited assumptions:

- Phase 1 remains the active phase; this run changes plans and docs, not
  schemas or code (additive `.github/` and `.gitignore` changes aside).
- Mock-first Phase 2 ordering is settled and correct.

Queue decision (intake rule applied):

- This work was triaged as user-directed planning (PLAN-001) and executed
  immediately. Why it outranked P1-001 (the standing top task): the user
  explicitly requested it this session; P1-001 and most other P1 gates are
  blocked on user/supervisor/hardware input that no agent action can
  produce today; and the buildout de-risks every later phase (it is the
  "removes ambiguity for multiple later steps" ranking factor at maximum).

## Planning Gaps Found (the audit result)

1. Phases 2-5 were checklist-shaped, failing the repo's own
   planning-reflection bar (steps without evidence/acceptance criteria).
2. Ordering drift: `AGENT_PLAN.md` Phase 2 listed MLX work before the
   reducer/mock path, contradicting the mock-first decision recorded in
   `TASK_QUEUE.md`/`RUN_STATE.md`.
3. Undecided design questions silently blocking Phase 2: adapter
   composition, telemetry concurrency, run-ID scheme, failed-run bundle
   semantics, repetition semantics, dashboard definition, dependency
   policy, sudo workflow, YAML-vs-JSON contradiction between the layout
   doc and the CLI.
4. Phase 3 carried the project's biggest feasibility risk (KV-cache
   extraction/portability) with no spike plan, no clock-sync methodology,
   no transfer-energy attribution policy, and a config schema that cannot
   express a split run.
5. Phase 4 had no statistical protocol (CI method, n, outliers, thermal
   ordering).
6. Methodology gaps: measurement boundaries across backends; controller-
   as-DUT contamination on Mac-local runs.
7. No risk register; no calendar mapping despite hard external dates.
8. Stale text: ground rule for the deleted Word doc; unresolved Step 0 in
   the continuation plan.
9. No CI on the remote.

## What Changed

New documents:

- `docs/decision_log.md` - D-001..D-019, each with context, options
  considered, considerations, consequences, and revisit triggers.
- `docs/risk_register.md` - R-001..R-015 with triggers, mitigations,
  fallbacks, and the project descope ladder.
- `docs/milestones.md` - calendar skeleton (dates TBD; task P1-008).
- `docs/phase_2/phase_2_plan.md` + `phase_2_exit_checklist.md` - slices
  2A-2M with gates, module map, cross-slice contracts (lifecycle stages,
  event taxonomy, status mapping, metric formulas), workload matrix.
- `docs/phase_3/phase_3_plan.md` + `phase_3_exit_checklist.md` -
  feasibility ladder (D-015), KV-size model + transfer-time tables,
  stages 3.0-3.4, composite bundle layout, borrow-window runbook
  requirement, hardware-independent floor.
- `docs/phase_4/phase_4_plan.md` + `phase_4_exit_checklist.md` -
  statistical ratification, aggregation with exclusion-log discipline,
  figure registry F1-F8 with pinned crossover/Pareto definitions,
  claims-to-evidence index, sensitivity audit.
- `docs/phase_5/phase_5_plan.md` + `phase_5_exit_checklist.md` - verified
  (not asserted) quickstart, by-construction extension guide, sample
  bundles, dataset freeze, slides, report, final handoff.
- `.github/workflows/ci.yml` - D-017 core CI.
- `docs/run_reports/2026-06-09-phase-2-5-planning-buildout.md` - this
  report.

Modified documents:

- `AGENT_PLAN.md` - restructured into the phase index + single-source-of-
  truth map; Phase 2 ordering fixed to mock-first; stale Word-doc rule
  removed; decision-log/risk-register ground rules added.
- `docs/phase_1/measurement_methodology.md` - added: Measurement
  Boundaries (D-018 table), Clock Synchronization (D-003), Controller
  Co-Residency (D-013), Repetition/Ordering/Thermal (D-005/D-014),
  Statistical Protocol (D-014); `deserialize` phase label + split-stage
  accounting definitions.
- `docs/phase_1/run_bundle_layout.md` - `config.json` (D-001), `raw/`
  directory (D-002), completion-marker semantics (D-011), experiment
  manifests (D-005/D-010), composite split-bundle preview (D-008).
- `docs/phase_1/phase_1_continuation_plan.md` - Step 0 and the inherited
  assumption marked resolved (Q-000, commit `a5d7404`).
- `TASK_QUEUE.md` - added P1-008 (calendar), P2-004 (model selection,
  D-016), P3-000 (KV spikes); P2 rows now reference plan slices;
  do-not-do-yet list extended (schema v0.2 timing, borrow-window
  scheduling, live-split ordering); PLAN-001/CI-001 recorded complete.
- `RUN_STATE.md` - full handoff update; start/end checklists now include
  the decision log and risk register.
- `README.md` - pointers to the new planning docs.
- `.gitignore` - `.DS_Store`.

Explicitly not changed: `joulewise/` source, tests, example configs,
schemas, the planning reflection protocol, Phase 1 evidence gates and
their statuses, git history.

## Commands Run

```bash
python3 -m unittest discover -s tests   # 14 tests, OK (before and after)
python3 -m joulewise validate-config configs/examples/mock_local.json
python3 -m joulewise validate-config configs/examples/mac_mlx_local.json
```

## What Passed / Failed / Was Uncertain

- Tests: 14 OK (docs-only change set; verified unchanged).
- Anomaly: transient `EPERM` errors accessing
  `docs/phase_1/measurement_methodology.md` and listing directories
  mid-run; recovered on retry without intervention. Suspected macOS
  Desktop privacy/permissions hiccup. Watch for recurrence.
- Uncertainties deliberately encoded as open items rather than resolved by
  fiat: D-016 (model selection) is `open` with criteria; the KV table's
  per-model dimensions must be verified against real model configs when
  D-016 closes; mlx-lm/llama.cpp cache API surfaces are recorded as
  "verify against installed version" in the spike specs.

## Planning Reflection Outcome

The plan-quality gap this run was created to fix is the run's own finding:
the repo enforced evidence-shaped planning for Phase 1 but not for the
phases where the hard risks live (KV portability, clock sync, statistics).
The fix follows the repo's existing pattern rather than inventing a new
one: per-phase plan + exit checklist mirroring `docs/phase_1/`, with two
new cross-cutting registries (decisions, risks) because those concerns
span phases. Net duplication decreased: `AGENT_PLAN.md` no longer
duplicates step detail it cannot keep in sync.

## What The Next Agent Should Do First

1. Read the new `RUN_STATE.md` next-steps list (P1-001, then P1-002 after
   the 2026-06-10 auth session, then P1-008 dates).
2. When implementation is prioritized: P2-001 = slice 2A per
   `docs/phase_2/phase_2_plan.md`, one slice per session, evidence per the
   exit checklist.
3. On the first push, confirm the CI workflow goes green (CI-001's
   remaining evidence).
