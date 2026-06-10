# JouleWise

JouleWise is an extensible benchmark for energy-wise LLM inference across
heterogeneous local hardware. The name is a deliberate nod to JouleSort and
Splitwise: energy measurement as the spine, split inference as the first major
research application.

The benchmark is designed around three stable ideas:

- Typed experiment configs define what should run.
- Runtime and telemetry adapters define how each hardware target is exercised
  and measured.
- Run bundles preserve raw traces, events, metadata, logs, and summary metrics
  for later audit and analysis.

**Advisor / high-level view:** `PROJECT_STATUS.md` is the standalone status,
plan, and architecture document - start there for a monitoring view of the
project.

See `AGENT_PLAN.md` for the phase index and status summary; each phase has a
detailed plan and an evidence-based exit checklist under `docs/phase_N/`. See
`RUN_STATE.md` before starting substantial work; it is the current handoff note
for what was done and what should happen next. Future phase starts should use
`docs/planning_reflection_protocol.md` to audit whether each step has evidence
and acceptance criteria before implementation begins.

Use `TASK_QUEUE.md` to triage new tasks against the current repo state, recent
handoffs, recent commits, and active phase gates. Design decisions (with the
options and considerations behind them) live in `docs/decision_log.md`; risks,
triggers, and the descope ladder live in `docs/risk_register.md`; calendar
constraints live in `docs/milestones.md`.

## Current State

Phase 1 is underway. The repository currently contains:

- Draft config and output schemas.
- Runtime, telemetry, and transport interface contracts.
- Example Mac-local and mock-local configs.
- Phase 1 methodology and feasibility docs.
- Unit tests for the schema and interfaces.

## Verify

```bash
python3 -m unittest discover -s tests
```

## Phase 1 CLI

Validate an example config:

```bash
python3 -m joulewise validate-config configs/examples/mock_local.json
```

Print the draft config schema:

```bash
python3 -m joulewise print-config-schema
```

Print the draft output schema:

```bash
python3 -m joulewise print-output-schema
```
