# 2026-06-09: Advisor Status Doc And Original-Sketch Audit

## Start-Of-Run Reflection

Goal:

- User-directed: (a) create a high-level status + plan/architecture
  document for the project advisor to monitor the project, shaped after a
  pasted reference document; (b) verify whether that reference plan is
  still coherent and mirrors current project thinking.

Prior state inspected:

- `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENT_PLAN.md`, all per-phase plans,
  decision log, risk register, milestones.
- The pasted reference did not transmit (placeholder only). Located the
  likely source in the project parent folder:
  `../Energy_Benchmark_Architecture.docx` ("Energy Benchmark Architecture
  And Expanded Plan"), alongside `JouleSort_Rivoire.pdf`. Extracted its
  text (stdlib zipfile + XML strip) and used it as the shape reference
  and audit subject. Note: queue item Q-000 recorded the *repo copy* of
  this .docx as removed per user instruction; the parent-folder original
  is the proposal-era sketch and stays outside the repo.

Queue decision:

- Triaged as DOC-002 (P4 by scale, user-directed); executed immediately.
  It also partially serves P1-001: `PROJECT_STATUS.md` is written to be
  the artifact the advisor reads before/at the scope-confirmation
  meeting.

## What Changed

- Added root-level `PROJECT_STATUS.md` - standalone advisor-facing
  document mirroring the sketch's shape (Summary -> Architecture ->
  Plan -> Verification -> Assumptions) extended with: status at a
  glance, blocked-on/asks list, methodology highlights, experiment plan
  (feasibility ladder + KV size intuition), per-phase status, the
  sketch-evolution audit table, risk/minimum-viable-outcome summary,
  timeline asks, deliverables, repository map, and a maintenance policy.
- Maintenance wiring: `AGENT_PLAN.md` ground rule + source-of-truth map
  row; `RUN_STATE.md` end-of-run checklist item (refresh on
  advisor-visible change); README pointer at the top.
- `TASK_QUEUE.md`: DOC-002 recorded complete.

## Audit: Original Sketch vs Current Thinking

Method: extracted sketch read section-by-section against the current
plans and decision log.

Intact (no drift): harness-first framing with disaggregation as the
validating study; the architecture flow (config -> controller -> runtime
+ telemetry adapters -> run bundle -> reducers -> dashboard/figures);
single controller with local/ssh transports; the two-layer adapter split
and target-as-composition model (the example compositions match the
shipped example configs); the run-bundle artifact list; typed schemas
with emitted JSON Schema; the run lifecycle (prepare -> idle -> warmup ->
measured_run -> cleanup -> reduce); phase events incl. transfer;
measurement-quality fields; read-only dashboard scope; structured Hailo
failure modes; the test-plan ladder (schema -> mock determinism ->
reducer-on-known-traces -> Mac 3-rep -> later experiments); every
"Assumptions And Defaults" bullet except the YAML one.

Documented refinements (decision-log backed, no contradictions):

1. YAML/Pydantic -> JSON-only input + stdlib dataclasses for now; bundle
   stores `config.json` (D-001, D-007, D-009).
2. "Mac slice first" -> mock vertical slice first, Mac immediately after
   as the first real backend (harness proven with exact arithmetic before
   real telemetry can confound it).
3. Dashboard "DuckDB/SQLite if needed" -> static HTML generator + CSV/
   pandas aggregation in Phase 4; no DB planned (D-006).
4. The sketch's offline-first KV bridge is kept and hardened into the
   three-rung feasibility ladder (synthetic floor -> offline replay ->
   live stretch) with per-runtime spikes and a same-runtime rule; the
   sketch's implicit GPU-to-Apple live pairing is reachable only via a
   portable runtime pending an explicit cross-machine portability spike
   (D-015, R-004, R-005).
5. Additions the sketch did not cover: measurement boundaries (D-018),
   multi-node clock discipline (D-003), controller co-residency (D-013),
   statistical protocol (D-014), evidence-gated phase exits, risk
   register + descope ladder, CI.

Verdict: the sketch remains coherent; current thinking mirrors it with
recorded refinements. The audit table is published in `PROJECT_STATUS.md`
("Evolution From The Original Architecture Sketch") so the advisor sees
the evolution story explicitly.

## Commands Run

```bash
python3 - <<EOF  # stdlib docx text extraction (zipfile + regex)
...
EOF
python3 -m unittest discover -s tests   # 14 tests, OK
```

## What Passed / Failed / Was Uncertain

- Tests: 14 OK (docs-only).
- Uncertainty: the pasted text itself never transmitted; the parent-folder
  .docx (11 KB, modified 2026-06-09 04:33, before the repo scaffold
  commits) is almost certainly its source given the name, location,
  timing, and content match to the request. If the user's paste was a
  different document, they should say so and the audit will be redone
  against it.

## What The Next Agent Should Do First

Unchanged queue top: P1-001 (advisor scope notes - `PROJECT_STATUS.md` is
the pre-read artifact for that meeting), then P1-002 after the 2026-06-10
auth session. Keep `PROJECT_STATUS.md` fresh per the new maintenance rule.
