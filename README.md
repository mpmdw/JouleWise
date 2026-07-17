# JouleWise

JouleWise is an extensible measurement harness for energy-wise LLM inference
across heterogeneous local hardware. The benchmark layered on that harness is
the frozen workload suite, run rules, and strict validator. The name is a
deliberate nod to JouleSort and Splitwise: energy measurement as the spine,
split inference as the first major research application.

The harness is designed around three stable ideas:

- Typed experiment configs define what should run.
- Runtime and telemetry adapters define how each hardware target is exercised
  and measured.
- Run bundles preserve raw traces, events, metadata, logs, and summary metrics
  for later audit and analysis.

**Status:** research prototype. The Mac (Apple M3 Max) measurement harness has
cleared its pre-campaign software review, the analysis path is implemented,
and the comprehensive audit is closed on `main`. The post-audit landings also
include the AXI-SA burst-decode contract, SITE-02 D1/D2, the SPLIT-AP Part I
pre-registration freeze, and the AXI-SB `supported` static-batch verdict with
its Mac C5-2.2 leg; `PROJECT_STATUS.md` carries the dated merge pointers.
This summary does not select work: the generated state-kernel regions in
`RUN_STATE.md` and `TASK_QUEUE.md` own the live gate and next-task state.
Quiet-machine execution still requires the lead-controlled hardware lane with
Ed. The AXI-SB live probes are runtime-feasibility evidence, not an energy
measurement or claim-bearing campaign. The verified end-user quickstart
remains a Phase 5 deliverable.

## Current State

Phase 1 is in its final stretch; **Phase 2's Mac vertical slice is complete
and the project has its first real energy measurements** (2026-07-06). From a
typed config, one command produces a complete, schema-valid, auditable run
bundle and reduces it to energy/latency summary metrics — proven first on
deterministic mock adapters, and now live on real hardware: the MLX runtime +
`powermetrics` telemetry adapters measured Qwen2.5-1.5B-Instruct (4-bit) on an
Apple M3 Max. **P2-003, gross energy — M3 Max / powermetrics SoC rails:**
~47.2 J per 512-token request. **P2-003, idle-subtracted energy — M3 Max /
powermetrics SoC rails:** ~44.4 J per request and ~79-90 mJ per generated
output token (mean 86.8 mJ). Throughput was 257 tok/s. These are legacy L1
preliminary observations (pre-2M, manual review) under
`docs/contracts/claims_ladder.md`; metric bases per
`docs/contracts/token_normalization.md`. The six real corpus bundles pass `validate-bundle --strict`
read-only and unrewritten: strict re-derives the recorded powermetrics power
trace from raw plist evidence, re-derives summary metrics from the recorded
trace and event log, checks the legacy additive summary comparison, and
requires shape-valid provenance for new-era bundles. This validates the
recorded evidence path; it does not independently rerun the hardware session.

Unless a figure explicitly states otherwise, JouleWise uses gross measured
energy within the named measurement boundary as the headline basis. Gross
energy retains the idle, model-residency, and runtime overhead present during
the measured interval, so comparisons across devices, configurations, and
split versus monolithic execution use gross energy. Idle-subtracted energy is
reported separately as a within-device secondary view of activity above the
measured idle baseline; it is not used to rank devices or configurations. In
Q4, the fixed term is estimated from the gross-energy workload sweep and is
not set equal to measured idle energy. The advisor-review rationale and full
basis/boundary rule are recorded in
[`PROJECT_STATUS.md`](PROJECT_STATUS.md#measurement-methodology-highlights).

Under D-070, static batching, speculative decoding / native MTP, MoE versus
dense execution, quantization, and reasoning-length variance are five stress
tests of Q4's single thesis. The harness must instrument all five axes and all
five have strict-valid L0 smoke-bundle support plus characterization
commitments, but every study remains floor-gated, capped at L2, and sequenced
after Window A. See the fuller
[Q4 architectural stress-test agenda](PROJECT_STATUS.md#summary)
in `PROJECT_STATUS.md`.

Window A is software-unblocked but still requires Ed and a quiet Mac. Its
fixed order is P2-038 live closure → P2-015-SMOKE → P2-015 floors → baselines.
Outside that quiet-machine lane, the current agent heads are AXI-SB-ADAPTER,
AXI-SC, and AXI-SD.

Remaining backends plug into the same adapter interfaces: the fixture-first
2K NVIDIA stack (SSH transport, node worker, nvidia-smi + vLLM adapters)
includes NV-GATE-2 software hardening: per-backend raw-lineage verifier
registration, usage-first vLLM streaming, and identity-aware process-survival
handling. The NV-5 localhost lead gate passed 3/3, but ALL remote protocol
pins remain PROVISIONAL pending first live hardware contact; Jetson Orin (2L)
remains gated on device access.

The landed C-028 arc includes the frozen analysis manifest, the
production-uncertainty path, the campaign-verdict split, idle-dependence/HAC
uncertainty, the inter-token metric, doctor preflight, and the contrast/claim
engine. The analysis trio—manifest, verdict split, and contrast/claim
engine—is complete. The six frozen legacy arms and 0.3.x/0.4.x dispatch rules
remain explicit; landed software is not being presented as new live evidence.
P0-003 closed with an iCloud Drive backup and a fresh restore that was
strict-valid and byte-identical. No new live NVIDIA or quiet-Mac measurement
is claimed here.

The post-audit landings add request-scoped AXI-SA burst/decode semantics,
freeze SPLIT-AP Part I before outcomes, close SITE-02's discovery and
emitted-code regression work, and establish AXI-SB's `supported` verdict from
lead-run B=2/B=4 Metal probes. The probes establish runtime feasibility and
request observability only; they add no energy result.

The repository currently contains:

- Typed config and output schemas with JSON-Schema export and validation.
- Runtime, telemetry, and transport interface contracts, with shipped mock
  adapters and a backend registry.
- The runnable harness: bundle writer, controller lifecycle, reducer, a
  shared bundle read layer, static HTML report generator, and a CLI
  (`run`, `validate-bundle`, `reduce`, `report`).
- Example Mac-local and mock-local configs.
- Phase 1 methodology, feasibility, and measurement-design docs.
- A test suite run in CI on every push, including a mock end-to-end run and
  bundle validation. The canonical command below and CI output own the current
  result; reader docs intentionally do not copy its volatile count.

## Verify

```bash
python3 -m unittest discover -s tests
```

The command's output is the current result. CI runs the same suite; this page
does not pin a pass or skip count that would drift as coverage grows.

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
substantial work; its generated state-kernel region is the current
work-selection view. Future phase starts should use
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
`docs/council_log.md`. Agents never regenerate or deploy the status site:
sessions that change front-facing state refresh `docs/site/DRIFT.md`, and Ed
deploys manually (D-068).
