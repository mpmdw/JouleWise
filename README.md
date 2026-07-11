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

**Status:** research prototype. The Mac (Apple M3 Max) measurement harness
has cleared its pre-campaign software review. Window A begins with the
C-019 shakedown and P2-015-SMOKE once P2-041/P2-037 land, the cross-stream
integration review passes, and the machine is quiet. The P0-003
external-backup gate is satisfied. Through
`main@73489a9` (2026-07-11), PRs #41-#49 are merged; the verified end-user
quickstart remains a Phase 5 deliverable.

## Current State

Phase 1 is in its final stretch; **Phase 2's Mac vertical slice is complete
and the project has its first real energy measurements** (2026-07-06). From a
typed config, one command produces a complete, schema-valid, auditable run
bundle and reduces it to energy/latency summary metrics — proven first on
deterministic mock adapters, and now live on real hardware: the MLX runtime +
`powermetrics` telemetry adapters measured Qwen2.5-1.5B-Instruct (4-bit) on an
Apple M3 Max at ~47.2 J gross rail energy per 512-token request (~44.4 J
idle-subtracted; ~79-90 mJ per generated output token on the idle-subtracted
basis, mean 86.8 mJ; 257 tok/s). These are legacy L1 preliminary
observations (pre-2M, manual review) under
`docs/contracts/claims_ladder.md`; metric bases per
`docs/contracts/token_normalization.md`. The six real corpus bundles pass `validate-bundle --strict`
read-only and unrewritten: strict re-derives the recorded powermetrics power
trace from raw plist evidence, re-derives summary metrics from the recorded
trace and event log, checks the legacy additive summary comparison, and
requires shape-valid provenance for new-era bundles. This validates the
recorded evidence path; it does not independently rerun the hardware session.
Remaining backends plug into the same adapter interfaces: the
fixture-first 2K NVIDIA stack (SSH transport, node worker, nvidia-smi +
vLLM adapters) now includes NV-GATE-2 code-now hardening from PR #49:
per-backend raw-lineage verifier registration, usage-first vLLM streaming,
and identity-aware process-survival handling. The NV-5 localhost lead gate
passed 3/3, but ALL remote protocol pins remain PROVISIONAL pending first
live hardware contact; Jetson Orin (2L) remains gated on device access.

The C-028 merge arc also landed P2-042's frozen analysis manifest (PR #46),
the P2-040 remainder and reducer 0.3.1 (PR #47), and P2-038's production
uncertainty software path (PR #48). P0-003 closed with an iCloud Drive
backup and a fresh restore that was strict-valid and byte-identical; Ed
ratified D-060; and the hardening proposal was adjudicated into nine queue
rows. P2-041's vetted rebuild and P2-037's contrast/claim engine remain in
progress on separate branches. No new live NVIDIA or quiet-Mac measurement
is claimed here.

The repository currently contains:

- Typed config and output schemas with JSON-Schema export and validation.
- Runtime, telemetry, and transport interface contracts, with shipped mock
  adapters and a backend registry.
- The runnable harness: bundle writer, controller lifecycle, reducer, a
  shared bundle read layer, static HTML report generator, and a CLI
  (`run`, `validate-bundle`, `reduce`, `report`).
- Example Mac-local and mock-local configs.
- Phase 1 methodology, feasibility, and measurement-design docs.
- A test suite (lead-run at `main@73489a9`: 1,041 tests OK, 12 skipped;
  current count authority: `RUN_STATE.md` Current Verification) run in CI on
  every push, including a mock end-to-end run + bundle validation.

## Verify

```bash
python3 -m unittest discover -s tests
```

(The lead-run canonical result at `main@73489a9` is 1,041 tests OK with
12 optional/environment-gated skips and zero expected failures. Both historic
intermittent failure classes are fixed on main: the fake-nvidia-smi idle
deadline now begins at sampler readiness, and the P2-038 rail-only fixture
deterministically supplies the right-edge sample.)

## Run The Harness (mock target — no hardware or extras needed)

```bash
# Produce a complete run bundle from the mock target (deterministic):
python3 -m joulewise run configs/examples/mock_local.json --runs-dir runs

# Structurally verify any bundle:
python3 -m joulewise validate-bundle runs/example-mock-local

# Re-derive summary metrics from a bundle's recorded trace/events (post-hoc):
python3 -m joulewise reduce runs/example-mock-local

# Render a static HTML run browser (needs: pip install 'joulewise[analysis]'):
python3 -m joulewise report runs --output report
```

A run bundle (`runs/<run_id>/`) contains the normalized `config.json`,
`metadata.json`, the `events.jsonl` lifecycle/phase/token log, the raw
`power_trace.csv`, model outputs, per-component logs, and the reduced
`summary_metrics.json` (written last; its presence marks a complete bundle).

Bundles are immutable evidence: re-running the same config into the same
`--runs-dir` fails by design with a run-ID collision (D-010/D-022). To rerun
a member, move the old bundle aside, change `run_id`, or use a fresh runs
dir; collisions are refusals, not bugs.

## Config And Schema Verbs

```bash
python3 -m joulewise validate-config configs/examples/mock_local.json
python3 -m joulewise print-config-schema
python3 -m joulewise print-output-schema
```

## Documentation Map

**Advisor / high-level view:** `PROJECT_STATUS.md` is the standalone status,
plan, and architecture document - start there for a monitoring view of the
project.

See `AGENT_PLAN.md` for the phase index; each phase has a detailed plan and
an evidence-based exit checklist under `docs/phase_N/` — the exit checklist
is the per-item status authority (D-023). See `RUN_STATE.md` before starting
substantial work; it is the current handoff note for what was done and what
should happen next. Future phase starts should use
`docs/planning_reflection_protocol.md` to audit whether each step has evidence
and acceptance criteria before implementation begins.

**Agents executing "the next step" start with `docs/agent_playbook.md`** —
self-contained, ordered mission guides (read-first lists, code-level routes,
verification commands, handoff checklists) for every remaining step of the
project.

Use `TASK_QUEUE.md` to triage new tasks against the current repo state, recent
handoffs, recent commits, and active phase gates. Design decisions (with the
options and considerations behind them) live in `docs/decision_log.md`; risks,
triggers, and the descope ladder live in `docs/risk_register.md`; calendar
constraints live in `docs/milestones.md`; cross-model review sessions
(implementer/reviewer positions, votes, resolutions - see D-031) live in
`docs/council_log.md`.
