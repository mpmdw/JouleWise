# JouleWise: Project Status, Plan, And Architecture

Audience: capstone advisor. This is the compact current view. Historical
updates are preserved in `docs/project_status_history.md`; live work selection
and required checks are generated from `docs/process/state_kernel.json` into
`RUN_STATE.md` and `TASK_QUEUE.md`. This document promises sequence, not dates.
Live status is in `RUN_STATE.md`.

Terms used on this page:

- *Immutable* evidence is never rewritten. *Frozen* means saved, fingerprinted,
  and thereafter immutable. *Prospective* means rules and thresholds were
  fingerprinted before the data they judge; *registered* means recorded there.
- *Admitted* evidence passed every registered check. *Authenticated* evidence
  also passed its required identity, origin, and unchanged-content checks.
- A *gate* is a pass/fail check that stops the next step on failure. A *cold
  gate* uses a fixed readiness record. *Governed* work follows a recorded,
  reviewable procedure; a *refusal* records why it issued no result.
- A *measurement window* is one uninterrupted calibrated collection session.
  *Calibration* maps readings to physical quantities; *attribution* assigns a
  power-trace portion to a workload interval; a *time anchor* aligns their
  timestamps.
- A *run bundle* is an immutable directory holding one run's configuration,
  readings, events, outputs, and summary. An *artifact* is an evidence or
  decision file. A *pack* is a frozen plan with authenticated supporting files.
- A *detection floor* is the largest false energy difference the admitted
  system can create. *Repeatability* is the spread among repeated unchanged
  measurements. An *uncertainty interval* retains the range consistent with
  quantified measurement uncertainty.
- *Prefill* processes the input prompt before output generation; a *token* is a
  unit of text. A *rung* is a candidate prompt length. An *arm* is a registered
  workload or comparison track. A *phase contrast* is the energy difference
  between two workload intervals.
- A *block* is four runs in small/large/large/small model order. A *component*
  is one workload's energy or a paired models' energy difference. The *ordinary*
  analysis moves each block's timing independently; a *shared-shift replay*
  applies one common move. The *dominance ratio* divides the timing-aware floor,
  which moves timing boundaries, by the naive floor, which does not.
- *Strict validation* rebuilds results from raw evidence without changing it.
  *Finalization* binds a frozen plan to collected evidence without selecting a
  favorable outcome. *Claim close-out* maps authenticated evidence to permitted
  wording; a *results fill* inserts only that wording or authenticated numbers.
- A *mint* authenticates source evidence and issues a detection-floor artifact.
  A *transaction* is prospective claim-bearing collection. *Claim-bearing* data
  may support capstone conclusions; *diagnostic* data may only exercise the
  system or choose a condition.
- A *probe* is diagnostic collection. A *shakedown* rehearses the real frozen
  pack. A *desk check* runs with no measurement active. A *throwaway clone* is
  a temporary repository copy used to expose unrecorded dependencies. *Custody*
  preserves evidence identity and integrity through analysis.
- A *controller* coordinates measurement. An *adapter* connects its programs or
  instruments; *telemetry* includes power, clocks, sampling rate, and thermal
  state; a *reducer* derives a summary without changing raw evidence.
- *Provisional* means not yet past the required live gate. *Gross energy* is all
  measured energy inside the boundary; *idle-subtracted energy* removes
  estimated idle use. *Voided for claim use* means retained for audit but
  permanently excluded from quantitative conclusions.
- *Inference* is a trained model producing output from input. MLX is Apple's
  machine-learning framework; `powermetrics` records Apple hardware readings;
  Qwen3 is the model family. In model names, 1.7B and 8B are parameter counts
  and 4bit means each stored weight uses four bits. *Split inference* divides
  inference across machines; *cache replay* reuses stored intermediate state.
- The *magistrate* is the independent readiness reviewer. A *synthetic-transfer
  result* combines measured computation with modeled transfer instead of
  claiming a live split-machine measurement.

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

- Deterministic mock adapters proved that a structured configuration can drive
  measurement and produce an auditable run bundle. The MLX plus `powermetrics`
  path subsequently produced run bundles that passed strict validation on real
  Apple hardware.
- Every pre-repair energy value is permanently **VOIDED for claim use** because
  power and workload events were joined through a defective time anchor. Raw
  bundles remain immutable evidence of the defect; validation does not repair
  physical attribution (`docs/reviews/2026-07-19-measurement-soundness-audit.md`).
- The repaired instrument is attribution-limited at approximately 1 J:
  boundary placement contributes about 0.7–1.0 J per run versus roughly
  0.29–0.49 J repeatability on approximately 50 J points. Both the detection
  floor and the uncertainty interval around the claimed difference retain their
  attribution terms, making the practical clearable phase contrast about 5 J
  (measurement-soundness decision D-078, clause 11).
- Five post-repair measurement windows passed the contamination screening and
  uncertainty accounting, establishing that the mechanism can pass. They are
  diagnostic or rule-establishing evidence, not substitutes for prospective
  Qwen3 data.

## Gate Matrix

| gate | pass condition | consequence of failure |
|---|---|---|
| Four-rung prompt probe | At least five small-model runs at a rung, each with at least five overlapping prefill power records; choose the shortest qualifying 512/1024/2048/4096-token rung | Preserve the probe and register the 4096-token prefill refusal; never lower the rule after seeing data |
| Desk freeze | Hash the selected rung, generate all Qwen3 packs, and reproduce their admission in a throwaway clone | No shakedown or transaction |
| Real-pack shakedown | One small-model/large-model/large-model/small-model block passes calibration, a check of the full measurement window, the desk check, and a check that deliberately incomplete evidence is refused | Stop; no claim-bearing collection |
| Transaction opening | The magistrate approves the fixed readiness record under unattended-transaction decision D-171; an Ed email reply also counts but is not required | Transaction stays closed |
| Nightly custody | Strict validation and the registered desk check pass before the next arm | Preserve/refuse the night; do not silently retry |
| Claim close-out | Authenticated floors, finalization, comparison, dominance ratios, and results-fill contract agree | Emit the registered non-dominance wording or no claim; never hand-fill prose |

The dominance claim requires the timing-aware floor divided by the naive floor
to be at least 2 for all
eight ordinary components and all four registered shared-shift replay ratios.
The authenticated close-out artifact, not prose judgment, selects the permitted
paper wording (falsifiability decision D-165 and close-out decision D-168).

## Artifact State

| artifact | current posture | owner |
|---|---|---|
| Instrument and immutable run bundle | implemented; mock and Apple M3 Max paths exercised | `joulewise/`, `docs/contracts/run_bundle_layout.md` |
| Qwen3 campaign design | prospective design and identity rules fixed; final packs await the measured prefill selector and open implementation gates | `configs/campaigns/d117_contrast_v5/`, `docs/process/v5-artifact-flow.md` |
| Live gates and next work | machine-generated; never copied here | `docs/process/state_kernel.json`, `RUN_STATE.md` |
| Paper claims and fill slots | pre-written contract; numerical fills await authenticated campaign artifacts | `docs/paper/results-fill-registry.md`, `docs/contracts/claims_ladder.md` |
| Remote targets and split inference | provisional or planned pending live access and feasibility gates | `docs/phase_2/`, `docs/phase_3/` |
| Public status site | repository is authoritative; drift is recorded and Ed deploys manually | `docs/site/DRIFT.md` |

The controller composes adapters for moving data, executing the model, and
collecting telemetry, then writes self-contained run bundles containing the
normalized configuration, environment and device identity, workload events,
raw power readings, outputs, and derived summaries. Reducers and reporting are
downstream and read-only with respect to raw evidence.

## Advisor Decisions And Risks

Required external inputs are the authoritative final report and colloquium
dates, confirmation of the remaining capstone scope, and access decisions for
any optional wall-meter, network, or borrowed-device work. No advisor
permission to open the transaction is requested: unattended-transaction
decision D-171 allows the magistrate's readiness gate to open it while
retaining Ed's stop authority and ownership of physical actions or actions that
require credentials.

Principal risks and responses:

- If no prompt rung qualifies, preserve the data and issue the registered
  refusal rather than weakening the sampling rule.
- If contamination, identity, calibration, custody, or nightly checks fail,
  stop and preserve the evidence; replacements require a recorded decision
  through the governed procedure.
- If timing attribution does not dominate repeatability by two, use the
  pre-written non-dominance wording. A negative result remains a valid capstone
  instrument result.
- If close-out or rendering is incomplete when data arrive, the claim waits;
  no manual prose bypass is allowed.
- If remote access or cache replay fails, use the synthetic-transfer result or
  omit the optional split demonstration.

## Next Milestone

The next scientific milestone is the four-rung prompt-length probe,
after the required desk work and the unattended overnight workflow's
re-authorization gates are complete. It is a quiet-machine measurement and
must not run while an agent session is active. The fixed sequence after it is:
checked rung selection and pack freeze; throwaway-clone proof; real-pack
shakedown; magistrate-gated transaction opening; claim-bearing nights with a
desk check after each; floor mint, finalization, comparison and dominance
close-out; then the governed results fill. Calendar dates belong in
`docs/milestones.md` once the authoritative academic dates are supplied.

## Evidence Links

- Current restart, dependencies, and work-selection categories: `RUN_STATE.md`,
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
