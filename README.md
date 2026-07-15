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
has cleared its pre-campaign software review. C-028 is closed: PRs #41-#58
are merged, the analysis trio is complete, and the reducer compatibility
lattice now terminates at 0.4.2. PR #59 is an open integration-review
follow-up, not an unlanded Window-A prerequisite. All Window-A software
gates are satisfied; execution begins with the C-019 shakedown and
P2-015-SMOKE in a lead-controlled quiet-machine session with Ed. The P0-003
external-backup gate is satisfied. The verified end-user quickstart remains
a Phase 5 deliverable.

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

The C-028 merge arc landed P2-042's frozen analysis manifest (PR #46), the
P2-040 remainder and reducer 0.3.1 compatibility arm (PR #47), P2-038's
production-uncertainty software path (PR #48), P2-041's verdict split and
reducer 0.4.0 (PR #54), idle-dependence/HAC uncertainty and reducer 0.4.1
(PR #55), the 0.4.2 inter-token metric (PR #56), doctor preflight (PR #57),
and the P2-037 contrast/claim engine (PR #58). The analysis trio—manifest,
verdict split, and contrast/claim engine—is complete. The six frozen legacy
arms and 0.3.x/0.4.x dispatch rules remain explicit; landed software is not
being presented as new live evidence. P0-003 closed with an iCloud Drive
backup and a fresh restore that was strict-valid and byte-identical. No new
live NVIDIA or quiet-Mac measurement is claimed here.

The repository currently contains:

- Typed config and output schemas with JSON-Schema export and validation.
- Runtime, telemetry, and transport interface contracts, with shipped mock
  adapters and a backend registry.
- The runnable harness: bundle writer, controller lifecycle, reducer, a
  shared bundle read layer, static HTML report generator, and a CLI
  (`run`, `validate-bundle`, `reduce`, `report`).
- Example Mac-local and mock-local configs.
- Phase 1 methodology, feasibility, and measurement-design docs.
- A test suite (current main: 1,220 tests OK, 10 skipped; PR #59 branch:
  1,224 tests OK in its worktree convention; count authority:
  `RUN_STATE.md` Current Verification) run in CI on every push, including a
  mock end-to-end run + bundle validation.

## Verify

```bash
python3 -m unittest discover -s tests
```

(The canonical result on current main is 1,220 tests OK with 10
optional/environment-gated skips and zero expected failures. Both historic
intermittent failure classes are fixed on main: the fake-nvidia-smi idle
deadline now begins at sampler readiness, and the P2-038 rail-only fixture
deterministically supplies the right-edge sample.)

## Release

The ordered publication path, including private-corpus, network, Node/Lakebed,
and credential boundaries, is in
[`docs/publication_release_checklist.md`](docs/publication_release_checklist.md).
Its clean-clone fixture/component gate is
`python3 scripts/release_check.py --dry-run`; it performs real temporary-directory
builds and never deploys.

## Run The Harness (mock target — no hardware or extras needed)

```bash
# Produce a complete run bundle from the mock target (deterministic):
python3 -m joulewise run configs/examples/mock_local.json --runs-dir runs

# Structurally verify any bundle:
python3 -m joulewise validate-bundle runs/example-mock-local

# Re-derive summary metrics from a bundle's recorded trace/events (post-hoc):
python3 -m joulewise reduce runs/example-mock-local

# Render a static HTML run browser (first: pip install -e '.[analysis]'):
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
