# JouleWise: Project Status, Plan, And Architecture

Audience: capstone advisor. This is the compact current view. Historical
updates are preserved in `docs/project_status_history.md`; live work selection
and gates are generated from `docs/process/state_kernel.json` into
`RUN_STATE.md` and `TASK_QUEUE.md`. This document promises sequence, not dates.
Live status is in `RUN_STATE.md`.

## Current Claim And Scope

JouleWise is a reusable instrument for measuring the energy and latency of
local large-language-model inference. Its capstone contribution is a governed
path that can say what it resolves, refuse what it cannot, and trace every
quantitative sentence to immutable raw evidence. The current prospective
campaign compares Qwen3-1.7B-4bit and Qwen3-8B-4bit on an Apple M3 Max. It asks
whether timing-attribution uncertainty dominates repeatability and whether the
registered model comparison clears the instrument's detection floor.

No claim-bearing data from this Qwen3 campaign exist yet. The campaign design,
thresholds, refusal conditions, and two permitted paper outcomes were fixed
before collection. Split inference and remote NVIDIA or Jetson targets remain
optional demonstrations; they cannot redefine capstone completion or upgrade a
provisional hardware claim.

The headline basis is gross measured energy inside a named boundary. Idle-
subtracted energy is a secondary within-device view, not a cross-device ranking
basis. A claim must clear its registered floor and uncertainty interval; a
below-floor difference is unresolved, not evidence of equality.

## Measured Evidence

- Deterministic mock adapters proved the typed-config-to-auditable-bundle path.
  The MLX plus `powermetrics` path subsequently produced strict-valid bundles
  on real Apple hardware.
- Every pre-repair energy value is permanently **VOIDED for claim use** because
  power and workload events were joined through a defective time anchor. Raw
  bundles remain immutable evidence of the defect; validation does not repair
  physical attribution (`docs/reviews/2026-07-19-measurement-soundness-audit.md`).
- The repaired instrument is attribution-limited at approximately 1 J:
  boundary placement contributes about 0.7–1.0 J per run versus roughly
  0.29–0.49 J repeatability on approximately 50 J points. Both the floor and
  the claim-side interval retain their attribution terms, making the practical
  clearable phase contrast about 5 J (D-078 clause 11).
- Five post-repair windows passed the screening and uncertainty-budget path,
  establishing that the mechanism can pass. They are diagnostic or
  rule-establishing evidence, not substitutes for prospective Qwen3 data.

## Gate Matrix

| gate | pass condition | consequence of failure |
|---|---|---|
| Four-rung prompt probe | At least five small-model runs at a rung, each with at least five overlapping prefill power records; choose the shortest qualifying 512/1024/2048/4096-token rung | Preserve the probe and register the 4096-token prefill refusal; never lower the rule after seeing data |
| Desk freeze | Hash the selected rung, generate all Qwen3 packs, and reproduce their admission in a throwaway clone | No shakedown or transaction |
| Real-pack shakedown | One A/B/B/A block passes calibration, whole-window, desk, and expected-incomplete-finalization checks | Stop; no claim-bearing collection |
| Transaction GO | The magistrate's cold-gate-adjudicated readiness record supplies GO under D-171; an Ed email reply also counts but is not required | Transaction stays closed |
| Nightly custody | Strict validation and the registered desk check pass before the next arm | Preserve/refuse the night; do not silently retry |
| Claim close-out | Authenticated floors, finalization, comparison, dominance ratios, and results-fill contract agree | Emit the registered non-dominance wording or no claim; never hand-fill prose |

The dominance claim requires timing-aware floor / naive floor >= 2 for all
eight ordinary components and all four registered shared-shift replay ratios.
The authenticated close-out artifact, not prose judgment, selects the permitted
paper wording (D-165/D-168).

## Artifact State

| artifact | current posture | owner |
|---|---|---|
| Instrument and immutable run bundle | implemented; mock and Mac paths exercised | `joulewise/`, `docs/contracts/run_bundle_layout.md` |
| Qwen3 campaign design | prospective design and identity rules fixed; final packs await the measured prefill selector and open implementation gates | `configs/campaigns/d117_contrast_v5/`, `docs/process/v5-artifact-flow.md` |
| Live gates and next work | machine-generated; never copied here | `docs/process/state_kernel.json`, `RUN_STATE.md` |
| Paper claims and fill slots | pre-written contract; numerical fills await authenticated campaign artifacts | `docs/paper/results-fill-registry.md`, `docs/contracts/claims_ladder.md` |
| Remote targets and split inference | provisional or planned pending live access and feasibility gates | `docs/phase_2/`, `docs/phase_3/` |
| Public status site | repository is authoritative; drift is recorded and Ed deploys manually | `docs/site/DRIFT.md` |

The controller composes transport, runtime, and telemetry adapters, then writes
self-contained bundles containing normalized configuration, environment and
device identity, workload events, raw power readings, outputs, and derived
summaries. Reducers and reporting are downstream and read-only with respect to
raw evidence.

## Advisor Decisions And Risks

Required external inputs are the authoritative final-report and colloquium
dates, remaining capstone-scope confirmation, and access decisions for any
optional wall-meter, network, or borrowed-device work. No advisor transaction
permission is requested: D-171 delegates unattended transaction GO to the
magistrate's readiness gate while retaining Ed's stop authority and ownership
of physical or credential-bound actions.

Principal risks and responses:

- If no prompt rung qualifies, preserve the data and issue the registered
  refusal rather than weakening the sampling rule.
- If contamination, identity, calibration, custody, or nightly checks fail,
  stop and preserve the evidence; replacements require a governed disposition.
- If timing attribution does not dominate repeatability by two, use the
  pre-written non-dominance wording. A negative result remains a valid capstone
  instrument result.
- If close-out or rendering is incomplete when data arrive, the claim waits;
  no manual prose bypass is allowed.
- If remote access or cache replay fails, use the synthetic-transfer result or
  omit the optional split demonstration.

## Next Milestone

The next scientific milestone is the bracketed four-rung prompt-length probe,
after the generated agent-lane prerequisites and unattended-night re-arming
gates are satisfied. It is a quiet-machine measurement and must not run while
an agent session is active. The fixed sequence after it is: checked rung
selection and pack freeze; throwaway-clone proof; real-pack shakedown;
magistrate-gated transaction opening; claim-bearing nights with a desk check
after each; floor mint, finalization, comparison and dominance close-out; then
the governed results fill. Calendar dates belong in `docs/milestones.md` once
the authoritative academic dates are supplied.

## Evidence Links

- Current restart, dependencies, and work-selection lanes: `RUN_STATE.md`,
  `TASK_QUEUE.md`, and `docs/process/state_kernel.json`.
- Binding choices and measurement rules: `docs/decision_log.md` (especially
  D-078, D-164–D-171) and `docs/contracts/measurement_methodology.md`.
- Probe-to-paper mechanism: `docs/process/v5-artifact-flow.md` and
  `docs/paper/results-fill-registry.md`.
- Phase evidence and optional-scope boundaries: `docs/phase_1/` through
  `docs/phase_5/` and `docs/contracts/capstone_scope.md`.
- Historical advisor updates and retired process prose:
  `docs/project_status_history.md`; current process: `docs/orchestration.md`.
- Front-facing drift: `docs/site/DRIFT.md`. Ed alone regenerates or deploys
  the public status site.
