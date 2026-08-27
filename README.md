# JouleWise

Terms used on this page: a *measurement window* is one uninterrupted,
calibrated collection session; a *pack* is the frozen campaign plan and its
authenticated supporting files; a *detection floor* is the largest false
difference the admitted measurement system can produce; a *mint* is the
governed process that issues a floor artifact; an *arm* is one pre-registered
workload or comparison track; a *verdict* is the final governed decision to
admit or refuse evidence; and a *refusal* is a recorded decision not to issue a
result when a required gate or piece of evidence fails.

**Status:** the instrument's clock-anchor correction is complete, the
successor measurement campaign family is frozen, and that work has now
passed all four of its review gates and been merged to this main branch
(2026-08-20). A council also ruled how the remaining reserved
configuration values install: together with the next campaign family,
whose evidence-freshness clock forces it to be built before any new
measurement windows run. The readiness re-audit and the plan for that
next family are in progress; measurement windows that produce the
paper's results data follow them.
Live state, gates, and work selection are owned by
[`RUN_STATE.md`](RUN_STATE.md) and its generated state-kernel regions
(`docs/process/state_kernel.json`); this summary does not duplicate them.

## Current activity (refreshed each work block; last: 2026-08-27)

**Just completed (2026-08-27): a one-day verification sprint.** Before
running the week-long measurement campaign, we checked every rule the
project had decided on against the code that is supposed to enforce it.
One in four had never been installed. The most important one — the
statistical plan for the two model comparisons — had been agreed on
2026-08-17 but never written into the plan the campaign would freeze, so
the campaign would have run for a week and then refused to report. That
is now fixed, and the freeze step checks for it. We also built a
minutes-long end-to-end check of the pipeline so this class of defect
fails loudly at the desk instead of after a campaign, and rewrote the
paper around its actual scientific finding (where the phase boundary
lands, not run-to-run noise, sets the smallest energy difference the
instrument can resolve), cutting it from 30k to 10k words.

**Now:** one small operator edit remains before the campaign can freeze
(a reviewed digest that only human hands may change), then a ten-minute
clone rehearsal, then the campaign night — earliest 2026-08-29/30.

**Next:** the campaign (about a week of nights), the paper's results
section from its output, and a 20-minute live end-to-end check the
evening before.

## Current State

Phase 1 is in its final stretch; **Phase 2's Mac vertical slice is complete
and the project has proved its live measurement path on real hardware**
(2026-07-06). From a
typed config, one command produces a complete, schema-valid, auditable run
bundle and reduces it to energy/latency summary metrics — proven first on
deterministic mock adapters, and now live on real hardware: the MLX runtime +
`powermetrics` telemetry adapters measured Qwen2.5-1.5B-Instruct (4-bit) on an
Apple M3 Max. The energy values originally reported from that corpus are
**VOIDED permanently for claim use** because its power trace and workload
events were joined through the defective pre-repair time anchor (D-078).
They are not under re-adjudication and must not be quoted. The six real corpus
bundles pass `validate-bundle --strict`
read-only and unrewritten: strict re-derives the recorded powermetrics power
trace from raw plist evidence, re-derives summary metrics from the recorded
trace and event log, checks the legacy additive summary comparison, and
requires shape-valid provenance for new-era bundles. This validates the
recorded evidence path; it does not repair the physical time attribution or
make the voided energy values usable.

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

D-075 now folds a ranked extension-axis evaluation into that same agenda
without proliferating theses: DSpark/DFlash break-even and control riders,
on-device quantized KV, one named hybrid pair, and attached
cache/context/kernel/backend provenance work. Every admitted unit remains a
floor-gated candidate at or below L2 with a named forbidden upgrade; unresolved
runtime and device-fit questions remain pending current external verification
(`NEEDS-WEB`), and Ed retains commitment
authority. Separate lead-run DSpark/DFlash smokes established native MLX
execution and per-round observability only. Their thinking-mode,
unmatched-output throughput inversion is hypothesis-generating, not energy
evidence.

Quiet-machine windows still require Ed and a quiet Mac, and each one follows
the run-book: issue, or mint, the governed drift-bound artifact inside the window, then collect a start
triplet, midpoint reference, and end triplet around the science members. That
protocol ran five times and passed five times — windows C, D, a10, the 7B
floor window, and the contrast window — under the merged screening and
uncertainty-budget rules (D-078 clause 10). One record-keeping caveat: for
a10 (and its reference window a9) the machine-readable verdict files were
not retained, so those "passed" results rest on the written close-out
record until a verdict is re-derived from the retained data. Those
pre-genesis results are
diagnostic or rule-establishing evidence, not the live claim path. Claim
authority can arise only from the prospective alpha, beta, and gamma windows
under D-117; the separately named Window C characterization night remains Ed
ruling #1. The a8 retrospective path is closed, and the earlier
222-bundle floor publication is a permanently voided historical record under
D-078. Use the
generated state kernel—not this summary—to select the next live or agent-lane
step.

A separate nine-bundle follow-on remains as a historical, unmatched
instrument record. All nine bundles are strict-valid as stored evidence, but
their energy values are **VOIDED permanently for claim use** by the same
pre-repair time-anchor defect (D-078), not merely exploratory and not under
re-adjudication. Each model ran three repetitions of the fixed five-item
sentinel shape and emitted 1,280 generated output tokens per bundle.

| unmatched configuration | energy disposition | runtime-observed output throughput |
|---|---|---:|
| OLMoE-1B-7B BF16 | **VOIDED — time-anchor defect (D-078)** | 122.361 tok/s |
| Qwen3-4B INT4 | **VOIDED — time-anchor defect (D-078)** | 106.519 tok/s |
| Qwen3.5-122B-A10B INT4 | **VOIDED — time-anchor defect (D-078)** | 39.473 tok/s |

These points differ in model scale, architecture, tokenizer, and
quantization, so they do not establish a controlled scaling relation,
architecture effect, or efficiency comparison. The
[bundle-cited extraction](docs/process_traces/2026-07-17-exploratory-block/results.md)
preserves the original figures as historical evidence only; D-078 bars their
quotation or claim use.

Remaining backends plug into the same adapter interfaces: the fixture-first
2K NVIDIA stack (SSH transport, node worker, nvidia-smi + vLLM adapters)
includes NV-GATE-2 software hardening: per-backend raw-lineage verifier
registration, usage-first vLLM streaming, and identity-aware process-survival
handling. The NV-5 localhost lead gate passed 3/3, but ALL remote protocol
pins remain PROVISIONAL pending first live hardware contact; Jetson Orin (2L)
remains gated on device access.

The landed C-028 implementation and review cycle includes the frozen analysis manifest, the
production-uncertainty path, the campaign-verdict split, idle-dependence/HAC
uncertainty, the inter-token metric, doctor preflight, and the contrast/claim
engine. The analysis trio—manifest, verdict split, and contrast/claim
engine—is complete. The six frozen legacy arms, meaning the pre-registered
workload tracks, and 0.3.x/0.4.x dispatch rules
remain explicit; landed software is not being presented as new live evidence.
P0-003 closed with an iCloud Drive backup and a fresh restore that was
strict-valid and byte-identical. No new live NVIDIA or quiet-Mac measurement
is claimed here.

The post-audit landings add request-scoped AXI-SA burst/decode semantics,
freeze SPLIT-AP Part I before outcomes, close SITE-02's discovery and
emitted-code regression work, and establish AXI-SB's `supported` verdict from
lead-run B=2/B=4 Metal probes. The probes establish runtime feasibility and
request observability only; they add no energy result. The corresponding
AXI-SC pinned-runtime spike returned `unsupported_for_joulewise`: the external-
draft path lacks the full proposal/acceptance/decode-boundary observability
contract, and native MTP lacks a usable generation surface. No Mac energy leg
was minted from that negative applicability result.

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
