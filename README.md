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

See `AGENT_PLAN.md` for the phase-by-phase implementation checklist.

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
