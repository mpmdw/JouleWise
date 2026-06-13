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

Phase 1 is in its final stretch; **Phase 2's hardware-independent core is
complete and runnable**. From a typed config, the harness produces a complete,
schema-valid, auditable run bundle and reduces it to energy/latency summary
metrics — today from deterministic mock adapters (so the controller, bundle
contract, and reducer math are proven without hardware). Real backends (Mac
MLX + powermetrics, NVIDIA/vLLM, Jetson Orin) plug into the same adapter
interfaces and are the next, hardware-gated slices.

The repository currently contains:

- Typed config and output schemas with JSON-Schema export and validation.
- Runtime, telemetry, and transport interface contracts, with shipped mock
  adapters and a backend registry.
- The runnable harness: bundle writer, controller lifecycle, reducer, static
  HTML report generator, and a CLI (`run`, `validate-bundle`, `report`).
- Example Mac-local and mock-local configs.
- Phase 1 methodology, feasibility, and measurement-design docs.
- A test suite (169 tests) run in CI on every push, including a mock
  end-to-end run + bundle validation.

## Verify

```bash
python3 -m unittest discover -s tests
```

(8 tests skip unless the `[analysis]` extra is installed — they are the
report-generator chart tests.)

## Run The Harness (mock target — no hardware or extras needed)

```bash
# Produce a complete run bundle from the mock target (deterministic):
python3 -m joulewise run configs/examples/mock_local.json --runs-dir runs

# Structurally verify any bundle:
python3 -m joulewise validate-bundle runs/example-mock-local

# Render a static HTML run browser (needs: pip install 'joulewise[analysis]'):
python3 -m joulewise report runs --output report
```

A run bundle (`runs/<run_id>/`) contains the normalized `config.json`,
`metadata.json`, the `events.jsonl` lifecycle/phase/token log, the raw
`power_trace.csv`, model outputs, per-component logs, and the reduced
`summary_metrics.json` (written last; its presence marks a complete bundle).

## Config And Schema Verbs

```bash
python3 -m joulewise validate-config configs/examples/mock_local.json
python3 -m joulewise print-config-schema
python3 -m joulewise print-output-schema
```
