# JouleWise: Project Status, Plan, And Architecture

Audience: capstone advisor. This is the standalone account of what JouleWise
is, how its measurement instrument works, what evidence is valid, and what
happens next. Repository links provide the audit trail but are not required to
understand the mechanism.

Plain-language terms used throughout:

- *Frozen* means written to disk, fingerprinted, and thereafter unchangeable,
  so the rule is fixed on the record before measurement.
- *Prospective* means the plan, rules, and pass/fail thresholds were written
  down and fingerprinted before any data they judge were collected.
- *Admitted* means passed every registered check and therefore permitted to
  contribute to a result.
- A *gate* is a mechanical pass/fail check that must succeed before the next
  step may run; failure stops the work rather than merely warning about it.
- *Governed* means executed only through a recorded, reviewable procedure with
  a registered path for refusing invalid evidence.
- A *measurement window* is one uninterrupted, calibrated collection session.
- A *run bundle* is one immutable directory containing the exact configuration,
  raw power readings, workload events, outputs, and derived summary for a run.
- A *pack* is the campaign plan and its authenticated supporting files after
  they are frozen.
- A *detection floor* is the largest false energy difference that the admitted
  measurement system can create.
- A *mint* is the governed program that authenticates source evidence and
  issues a detection-floor artifact.
- An *arm* is one pre-registered workload or comparison track.
- A *verdict* is the final governed decision to admit or refuse evidence. A
  *refusal* records why no result was issued when evidence or a gate failed.
- A *cell* is one pre-registered combination of model, workload phase, and
  which registered analysis method computes the number: the ordinary method,
  which treats each paired block on its own, or the shared-shift variant used in
  the replay described later (`joulewise/floor_extraction.py:1165-1171` admits
  exactly those two). A *component* is either an absolute measurement of one
  workload or a comparative measurement built from paired workloads; every cell
  carries both components.
- The *state kernel* is the machine-readable table of live tasks, dependencies,
  and machine-access lanes. A *manifest* is a list of required artifacts and
  their content fingerprints.
- *Strict validation* is a read-only program that rebuilds recorded results
  from raw evidence and refuses any inconsistency. *Finalization* binds a
  frozen plan to the identities of the evidence actually collected without
  choosing a favorable outcome. A *results fill* is controlled substitution of
  authenticated numbers or one of the pre-written branch sentences into the
  paper.
- A *transaction* is the governed opening and execution of the prospective,
  claim-bearing collection; diagnostic probes do not belong to it. *Telemetry*
  means instrument readings such as power, clocks, sampling rate, and thermal
  state. A *tokenizer* is the program that converts text into numeric model
  tokens.

Freshness and authority:

- The state kernel, `docs/process/state_kernel.json`, generates live gates and
  work selection into `RUN_STATE.md` and `TASK_QUEUE.md`.
  This document states the sequence and scientific posture, not volatile task
  or test counts.
- The first paper draft, `docs/paper/draft-v1.md`, is frozen as a historical
  writing baseline. It predates the current model pair and is not the current
  campaign specification.
- The repository is `github.com/mpmdw/JouleWise`, with `main` as the integration
  branch. The public status site is an Ed-deployed snapshot; the repository is
  authoritative, `docs/site/DRIFT.md` records differences, and Ed alone
  regenerates or deploys the site.
- Project phase: Phases 1 and 2 remain in progress; the Mac instrument and
  analysis path exist, while the current claim-bearing campaign is sequenced
  but has no results data yet.

## Current Repository View — 30-second read

**As of 2026-09-01, JouleWise is ready for the first machine step of a new
prospective campaign, but no claim-bearing data from that campaign exist.**
The campaign now compares the Qwen3 1.7-billion-parameter and
8-billion-parameter models using MLX, Apple's machine-learning framework, on
an Apple M3 Max. Their quantized weights store each numeric value in four bits,
so they are named Qwen3-1.7B-4bit and Qwen3-8B-4bit. Ed selected this pair on
2026-08-28. The experimental design did not change: the internal label `_v5`
marks a regeneration of the same frozen design under the new model pair, and
the superseded `_v4` family will not be collected (newer-model decision D-164).

The plan preparation is code-complete, but its final generated pack must wait
for one measured input: the prompt length for the prompt-processing, or
*prefill*, arm. The pack records the pass/fail rule itself—the floor formulas,
thresholds, and refusal conditions the analysis must use—as a body of text
called the *frozen analysis semantics*. Those bytes are hashed with SHA-256, a
cryptographic fingerprint that changes if any byte changes, so an edit after
data arrive would be visible. In addition, a golden readback—a test that reads
the generated registration back and compares it byte-for-byte with an
independently frozen copy—pins the exact pass/fail threshold and refusal
behavior
(`configs/campaigns/d117_contrast_v5/generate_configs.py:2597-2603`).

**The paper's headline test was made genuinely falsifiable before collection.**
Three blind reviewers found that the earlier rule would pass almost any
positive timing uncertainty. The replacement compares two floors:

- the *naive floor*, which applies the registered false-difference formula to
  the measured point values without moving any timing boundary. For an
  absolute component, a residual is one run's energy minus the mean energy for
  that cell; the formula keeps the larger of the largest residual magnitude
  and the 95% prediction from their scatter. For a comparative component, one
  paired *block* is four consecutive runs in small, large, large, small order,
  placing each model on both sides of the pair so slow drift tends to cancel.
  The input is each block's small-versus-large energy difference, and the
  formula keeps the larger of the largest magnitude of such a difference and
  the 95% prediction from the differences' mean and scatter; and
- the *timing-aware floor*. The code displaces the start boundary and the end
  boundary independently to the low and high limits of the calibrated timing
  uncertainty—two boundaries at two limits each, so four combinations—and at
  each combination scans the remaining shared clock shift across the exact
  power-trace breakpoints.
  This gives each run or block difference an allowed low-to-high energy
  interval. The floor code then chooses the low or high end of every interval,
  recomputes the full false-difference floor for every resulting combination,
  and keeps the largest false energy difference. The timing-aware floor is the
  larger of that result and the naive floor; the two are not added
  (falsifiability decision D-165).

The *dominance ratio* is the timing-aware floor divided by the naive floor. For
the paper to say that error in placing the measurement boundaries in time
matters more than the spread seen when the same run is repeated with nothing
changed, this ratio must be at least two for exactly eight ordinary cases—an
absolute and a comparative component in each of four registered cells. Four
additional comparative ratios apply one shared timing displacement across all
blocks while allowing each block's remaining uncertainty to move independently.
This *replay* is a recomputation from stored, authenticated inputs, not another
experiment; a shared-shift ratio below two withdraws the sentence.

Illustrative, not campaign data: if an ordinary case has a naive floor of 2.0
joules and a timing-aware floor of 4.8 joules, its ratio is 4.8 / 2.0 = 2.4 and
that case passes. If its shared-shift recomputation instead gives 3.6 / 2.0 =
1.8, the paper sentence is withdrawn even though the ordinary case passed. All
eight ordinary ratios and all four required shared-shift ratios must pass
(close-out decision D-168). A
machine-readable close-out artifact—not prose judgment—decides which of the
two permitted paper wordings may be filled. Missing, unauthenticated, or
zero-denominator inputs license neither wording and stop the fill.

**Next machine step: one instrumented evening, waiting on Ed.** The machine
will measure four candidate prefill lengths—512, 1,024, 2,048, and 4,096
tokens. Each candidate length is called a *rung*. At least five Qwen3-1.7B runs
are required at each rung; a rung with fewer than five small-model runs is
unevaluable and cannot be selected. Qwen3-8B probes are retained but do not
choose the length. A checked program selects the shortest rung for which every
small-model run contains at least five power records overlapping prefill. One
power record physically represents one sampling interval of the Apple power
meter—requested every 100 milliseconds, with its actual interval stored in the
run (`configs/campaigns/d117_contrast_v5/generate_configs.py:494`;
`joulewise/adapters/powermetrics.py:1461-1462`). Five is three plus two: three
is the fewest power samples the energy-integration program can compute a
phase's energy from at all, and two is a safety factor declared in advance. If
no rung qualifies, the campaign
still records the 4,096-token arm but refuses the prefill claim honestly rather
than lowering the rule after seeing data (workload decision D-166).

The remaining order is fixed, not date-promised. The probe evening is followed
by a *desk day*: analysis work done away from the measured machine, with no
measurement running, so the work cannot contaminate a power reading. That day
pins and hashes the selection, generates the final packs, and re-proves them in
a throwaway clone. Next comes a *shakedown*: one short run on the real, frozen
pack that proves the machine, plan, and refusal checks behave as registered
before claim-bearing data are collected. Ed then explicitly authorizes the
claim-bearing transaction; about a week of collection follows with a desk check
after each night; then floor production, claim close-out, and the registered
results fill. `RUN_STATE.md` is the live status authority.

**A fresh-model repository review began from scratch on 2026-09-01.** A new
lead model coordinated four independent reviewers across code, tests, process,
paper, and research questions. The reviewers were blind to each other and ran
as separate sessions across more than one vendor's large-language model. Their
shared verdict was that the repository can support a defensible undergraduate
computer-science capstone, provided that the campaign and remaining claim
gates are completed. Separate branches currently hold in-flight desk work: a
paper skeleton for the next draft; a dependence-sensitivity analysis for the
ten-block direction test, which is the ten-block test of *which* model uses
more energy—its direction, not its size—and checks whether relationships among
the blocks could change that result; a transfer-fiducial plan that inserts a
known timing marker into real inference work; the dominance close-out core; and
programs that generate configurations for the four-rung probe. These are not
described as landed results.

Standing soundness facts remain unchanged:

- Every energy value collected before the timing repair is permanently
  **VOIDED for claim use** because power readings and workload events were
  timestamped by two different clocks, and the program that joined them—the
  *time anchor*—could integrate the wrong slice of the power trace against a
  workload phase (measurement-soundness decision D-078).
- The repaired instrument is attribution-limited at approximately 1 joule:
  uncertainty about the exact start and end boundaries, 0.7-1.0 J per run,
  matters more than its 0.29-0.49 J repeatability noise on ~50 J points. The
  floor and each claim's decision interval separately charge that attribution
  bound, so the effective clearable effect is floor plus claim-side bound
  (~5 J for phase contrasts), not the floor alone (measurement-soundness
  decision D-078, clause 11). The registered rules require this disclosure
  wherever an attribution-limited floor is published. Longer workloads increase
  signal without pretending that this physical limit disappeared.
- Retained run bundles and corpora are immutable. Validation may re-derive
  their recorded summaries, but it never rewrites the evidence.

### Voided July 2026 calibration floor record

The floor table from the July 2026 calibration campaign—222 run bundles
(`docs/council_log.md:1536`), internally labelled Window A—and every energy
value derived from it at any granularity—per request, per workload phase, per
item, per suite, and for both paired-comparison and reference measurements—are
permanently void for claims.
The raw record remains immutable evidence of the timing defect described
above. It was replaced by repaired meter-timestamp alignment, explicit timing
uncertainty in every result, authenticated calibration, and prospective
collection. Technical record:
`docs/reviews/2026-07-19-measurement-soundness-audit.md`.

### 2026-07-19 re-calibration with machine-contamination screening — VOIDED

The machine-environment guard refuses a run if anything else on the machine,
such as a screensaver or background process, could add power draw. The guarded
re-calibration corpora were structurally valid and repeatable, but
their energy values and provisional floors are void for the same pre-repair
time-anchor defect; one early corpus also came from an uncommitted collection
tree. A clean source record cannot repair incorrect physical time attribution.
Fresh collection under the repaired timing and calibration path replaced these
records.
Plain-language account:
`docs/advisor_briefs/2026-07-20-timing-defect-explainer.md`.

### Historical exploratory follow-on — energy values voided

Nine OLMoE and Qwen bundles that were never collected as matched pairs remain
useful only as proof that the live runtime and evidence path executed. Their
model size, architecture, tokenizer, and quantization differ, and their energy
values are also void under the same time-anchor ruling. They support no
efficiency ordering or scaling claim.
Custody record:
`docs/process_traces/2026-07-17-exploratory-block/results.md`.

<!-- ## Previous Update sections collapsed into the Update Ledger below. -->

## Update Ledger

| date | what changed |
|---|---|
| 2026-09-01 | The live work selector was reconciled to the Qwen3 `_v5` chain; the results-fill registry was regenerated; a fresh-model whole-repository review launched the paper skeleton, dependence, timing-marker, close-out, and probe-configuration follow-ups. |
| 2026-08-30/31 | The Qwen3 plan preparation completed adversarial review; exact model and tokenizer identities, the two-times dominance rule, and the four-rung checked selector were pinned. |
| 2026-08-28 | Ed selected Qwen3-1.7B-4bit and Qwen3-8B-4bit; three blind reviewers prompted the pre-data tightening of the paper's pass/fail rule. |
| 2026-08-20 | The predecessor campaign preparation passed its review gates and merged; its model family was later superseded, while the repaired instrument and frozen-design discipline remained. |
| 2026-08-15/16 | A readiness review refused measurement, converted every finding into repair work, and the mergeable repair program then landed. |
| 2026-08-13 | The predecessor three-pack campaign froze successfully; those packs are retained as process evidence but are not the current Qwen3 campaign. |
| 2026-07-30/31 | The first floor artifact and a passed head-to-head diagnostic demonstrated the governed path; later decisions made both non-claim-bearing and required prospective replacement. |
| 2026-07-25/26 | The repaired screening and uncertainty-budget rules merged, and the first post-repair windows passed. |
| 2026-07-22 | The defective trace-time anchor was repaired and verified end to end. |
| 2026-07-19 | The soundness audit voided all pre-repair energy values and defined the repair. |
| 2026-07-17/18 | The environment guard and exploratory runtime evidence landed; their pre-repair energy values are historical and void. |
| 2026-07-09 | A whole-project review found reader-facing claim drift and analysis gaps; the advisor status view remained repository-backed. |
| 2026-07-07/08 | Source-identity tracking, statistical uncertainty, contamination detection, telemetry, campaign automation, the mock-first NVIDIA stack, and a cache-replay feasibility result landed through reviewed streams. |
| 2026-07-06 | The MLX plus `powermetrics` Mac path first produced strict-valid hardware bundles; its pre-repair energy values were later voided. |
| 2026-06-12 | The mock vertical slice proved the typed-config-to-auditable-bundle path before hardware measurement. |

<!-- ADVISOR-PAGE-END -->

## Summary

JouleWise is a reusable, typed instrument for measuring the energy and latency
of local large-language-model inference. Its capstone contribution is not one
model leaderboard. It is a governed measurement path that can state what it
can resolve, refuse what it cannot, and trace every quantitative sentence back
to immutable raw evidence.

The first working target is an Apple M3 Max running MLX and Apple's
`powermetrics` power telemetry. Deterministic mock adapters first proved the
controller and arithmetic without hardware. Remote NVIDIA and Jetson targets
fit the same interfaces but remain provisional until live device access.

The current paper is metrology-centered: it asks whether the instrument places
measurement boundaries correctly in time, repeated runs agree when nothing is
changed, and drift, linearity, and additivity are controlled well enough for a
model comparison to be meaningful. Split inference—processing the prompt on
one machine, transferring the model's attention cache, then generating output
on another—is an optional demonstration rather than a capstone completion
requirement. The claim hierarchy and minimum viable stop line are in
`docs/contracts/capstone_scope.md`.

The research program remains organized around six questions:

- When can split inference reduce total energy relative to either whole-model
  placement?
- Where does interconnect speed change that answer?
- What energy-versus-latency trade-off results?
- Can energy be modeled as a fixed cost plus prompt-processing and token-
  generation terms?
- When do model, workload, and quantization rankings change?
- Does measuring chip subsystems rather than wall power change a conclusion?

The live wording, gates, aliases, and permitted claim strength for each
question are in `docs/research_question_registry.md`.

Five architectural variations—static batching, speculative multi-token
generation, sparse mixture-of-experts models, quantization, and reasoning-
length variation—stress-test the single fixed-plus-marginal energy model. They
do not create five additional capstone claims. Each variation must first prove
that the runtime and evidence path work; any comparative result remains bound
by the detection floor and its registered claim limit.

## Status At A Glance

| Phase | Scope | Status |
|---|---|---|
| 1. Approval, feasibility, and measurement design | contracts, methodology, hardware feasibility, advisor and calendar inputs | **in progress** — core contracts are settled; advisor/calendar and remote-hardware inputs remain external |
| 2. Instrument and Apple-Silicon campaign | runnable harness, repaired Mac measurement path, Qwen3 `_v5` campaign | **in progress** — instrument and plan preparation are complete; the four-rung prompt probe is the next machine step and waits on Ed |
| 3. Split-inference demonstration | cache transfer, offline replay, optional live split | **planned** — feasibility-first and not required for capstone completion |
| 4. Analysis and paper | authenticated floors, claim close-out, figures, results, limitations | **in progress** — fill contract is landed and desk scaffolding is in flight; numerical fills wait on prospective data |
| 5. Presentation and release | reproducible archive, final report, colloquium | **planned** — follows the claims audit and figure freeze |

## Capstone Artifact Map

| chapter or artifact | repository owner | live status | missing evidence |
|---|---|---|---|
| Background and related work | `docs/phase_4/related_work_draft.md` | drafted from verified sources | final chapter integration |
| Measurement methodology | `docs/contracts/measurement_methodology.md` | implemented and repaired | final paper wording against observed campaign behavior |
| Harness and instrument | `joulewise/` | runnable on mock and Mac; strict validation and claim analysis exist | remote adapters remain provisional until live contact |
| Current campaign plan | `configs/campaigns/d117_contrast_v5/` | Qwen3 model pair, workload, dominance rule, and generator are pinned | measured prefill choice, final generated packs, and clone re-proof |
| Machine-to-paper artifact chain | `docs/process/v5-artifact-flow.md` | mapped from probe through results fill | programs that generate probe configurations and close-out artifacts are in flight; later mint and rendering links have been decided and scheduled but not yet built |
| Paper result slots | `docs/paper/results-fill-registry.md` | `_v5` fill contract landed | issued campaign, floor, close-out, and claim artifacts |
| Current paper prose | `docs/paper/draft-v1.md` | frozen prior draft; not edited for `_v5` | successor skeleton is in-flight; results prose waits on data |
| Split-inference study | `docs/phase_3/` | planned optional demonstration | portable runtime pairing or the synthetic-transfer fallback |

Complete and verifiable in the repository:

- A typed configuration can drive one command to a complete run bundle with
  raw evidence, lifecycle events, outputs, and reduced energy and latency.
- Strict validation rebuilds the Apple power trace from raw property-list
  records, rebuilds summaries from trace and event bytes, checks source
  identities,
  and refuses inconsistent bundles.
- Runtime, telemetry, and transport adapters are separate, so execution and
  power sources can be composed without changing the bundle contract.
- The analysis path includes frozen prospective manifests; a *whole-window
  verdict*, which is one pass/fail check over an entire collection session
  rather than one run; floor extraction and minting; finalization; and the
  program that evaluates each registered comparison against the floor.
- An off-machine backup was restored and passed strict validation with
  byte-identical bundles.

No `_v5` result is claimed here. Earlier post-repair windows established that
the path can pass; earlier diagnostics do not substitute for the current
prospective campaign.

## Architecture

```text
typed config
  -> controller
    -> transport adapter: local | ssh
    -> runtime adapter:   mock | mlx | vllm | llama.cpp
    -> telemetry adapter: mock | powermetrics | nvidia-smi | jetson rails | wall meter
  -> run bundle (self-contained, on-disk source of truth)
    -> reducers (energy integration, idle subtraction, per-phase attribution)
    -> static report / notebooks / paper figures
```

Key elements:

- **Single controller, flexible transports.** Local execution serves a
  one-machine run; Secure Shell, or SSH, serves remote targets and split
  experiments.
- **Two adapter layers.** Runtime adapters execute a model workload. Telemetry
  adapters measure power and thermal state. The layers are independent.
- **A target is a composition** of transport, runtime, and telemetry. The
  identifiers below are literal configuration keys:

  | target key | transport | runtime | telemetry |
  |---|---|---|---|
  | `macbook_m3_max` | local | MLX | Apple `powermetrics` |
  | `nvidia_3050` | SSH | vLLM, with llama.cpp using NVIDIA CUDA as fallback | `nvidia-smi` board power |
  | `orin_nano` | SSH | to be decided after live contact | module-input rails |
  | `pi5_hailo` | SSH | unsupported workload, retained as a feasibility finding | wall meter |

- **Every run writes a self-contained bundle.** It includes the normalized
  config, device and environment metadata, timestamped lifecycle, phase and
  token events, raw power readings, backend-native telemetry, logs, model
  outputs, and reduced summary metrics. Summary numbers are derived and
  re-derivable; raw bundle bytes are the source of truth.
- **Typed schemas** use standard-library Python data classes in the core and
  export JSON Schema for external validation.
- **Unsupported is a result, not a crash.** An infeasible combination returns
  a structured reason such as model-too-large, runtime unavailable, or power
  telemetry unavailable, while preserving a complete diagnostic bundle.
- **The dashboard is read-only.** Static HTML provides a run table, per-run
  pages, and power traces with workload phases shaded. It cannot launch or
  alter an experiment.

## Measurement Methodology Highlights

Unless a figure says otherwise, the headline basis is *gross measured energy*
inside the named measurement boundary. Gross energy retains idle draw, loaded-
model residency, and runtime overhead during the interval. Idle-subtracted
energy is a secondary within-device view of activity above a measured idle
baseline; it is not used to rank devices. For the fixed-plus-marginal model,
the fixed term is estimated from the gross-energy workload sweep, not equated
with idle power.

This choice follows the advisor-reviewed physical argument: subtracting idle
penalizes energy-proportional devices and rewards high-idle devices; in a split
run, subtracting both machines' idle energy deletes part of the cost the
crossover question is meant to measure (reporting-basis decision D-067).

- **Both bases are captured.** Every eligible request records gross and idle-
  subtracted energy plus idle variance. Reporting choices never alter stored
  evidence.
- **Measurement boundaries are named.** Apple `powermetrics` covers selected
  system-on-chip subsystems: the central processor, graphics processor, and
  Apple Neural Engine. `nvidia-smi` covers the graphics board. Jetson rail
  sensors cover module input. A wall meter covers full-system alternating-
  current power. Within-target comparisons are primary; cross-target claims
  state the boundary mismatch.
- **Timing attribution is explicit.** Power readings and workload events use
  separate clocks. Calibration estimates their relationship, and the allowed
  clock and boundary-placement uncertainty is propagated into energy. The
  repaired instrument's approximately 1-joule attribution limit is a physical
  claim boundary, not a software nuisance to subtract away
  (measurement-soundness decision D-078, clause 11).
- **Uncertainty is quantified.** Registered comparisons use repeated paired or
  blocked measurements, report raw points, means and scatter, and use a 95%
  interval based on Student's t distribution when that model is admitted.
  Outliers are flagged, never silently deleted. Dependence sensitivity for the
  ten-block direction test is being prepared separately so that independence
  is not assumed without examination.
- **A result must clear the right floor.** The confidence interval of the
  predeclared paired or blocked difference—not the fact that two separately
  computed one-model intervals happen not to overlap—controls a direction
  claim. A difference below the floor is not resolvable; an above-floor but
  non-directional result remains unresolved; a claim that two models are
  practically the same requires its own threshold, declared in advance, for
  how close counts as the same.
- **The headline attribution sentence has a stronger pre-data gate.** For
  every component and cell, the timing-aware floor divided by the naive floor
  must be at least two. Comparative cells also disclose the shared-shift replay
  ratio. The authenticated close-out artifact alone licenses the corresponding
  paper sentence.
- **Multi-node timing is bounded.** Split runs record controller-mediated
  marker events. Cross-node intervals shorter than the measured offset bound
  are flagged rather than trusted.
- **Quality is data.** Requested and observed sample rate, dropped samples,
  idle variance, thermal state, telemetry identity, calibration identity, and
  refusal reasons travel with the evidence.
- **Evidence is immutable and retries are governed.** Failed or invalid runs
  remain in custody. They are never silently overwritten or rerun until they
  pass; any replacement follows the recorded procedure for replacing a
  superseded run, which keeps the original in place.

## Experiment Plan

### Current Qwen3 campaign

The live campaign sequence is:

1. **Four-rung prompt probe.** In one bracketed, non-claim evening, collect at
   least five Qwen3-1.7B runs at each of 512, 1,024, 2,048, and 4,096 prompt
   tokens. Retain Qwen3-8B observations without letting them select the rung.
   A *bracket* means calibrated reference measurements before and after the
   probes so drift and clock alignment are bounded around the work. This
   measurement window contains probe data only and cannot carry a claim.
2. **Checked selection and desk freeze.** A program chooses the shortest rung
   with at least five small-model runs and at least five overlapping power
   records in every one of those runs. A rung with fewer than five small-model
   runs is unevaluable and cannot be selected. The desk step stores and hashes
   that choice, generates the three final Qwen3 packs, verifies byte-for-byte
   regeneration, and repeats the complete admission proof in a disposable
   clone of the repository. If no
   rung qualifies, 4,096 tokens is collected with a pre-registration refusal
   attached; the rule is not weakened.
3. **Real-pack shakedown and authorization.** The next instrumented night first
   proves one small/large/large/small block on the real pack, builds its
   calibration bracket and whole-window verdict, runs the desk checker, and
   confirms that finalization refuses for exactly the expected incomplete-
   campaign reasons. Any other refusal stops. Ed then decides whether to open
   the claim-bearing transaction.
4. **Claim-bearing collection.** The Qwen3-1.7B and Qwen3-8B arms use Qwen3's
   optional reasoning mode switched off, so the model emits no hidden
   deliberation tokens and output length remains controlled. They choose the
   highest-probability token at every step, force a 512-token output, and use
   the measured prefill length. Diagnostic runs and claim-bearing runs are
   written to separate directories, so no diagnostic bundle can enter a claim.
   A desk check after every campaign night blocks the next arm on any failure.
5. **From evidence to prose.** Each bundle passes strict validation, and its
   summary is re-derived without changing the bundle. Each registered cell is
   turned into its own floor report. The mint checks those reports against
   their source evidence and issues one combined floor for the campaign. The
   frozen plan is then bound to the exact runs actually collected. The
   comparison program computes each pre-registered comparison against that
   floor; the close-out program picks one of the two permitted paper sentences,
   or neither; and the rendering program writes numbers only into the slots the
   fill contract already named.

The detailed operator-to-artifact chain is in
`docs/process/v5-artifact-flow.md`. It also names current implementation gaps:
the program that generates the prompt-probe configuration files, final Qwen3
floor-extraction and mint inputs, the dominance sidecar—an authenticated
companion file carrying replay inputs and derived ratios—and close-out path,
and the final adapter into the successor results renderer. The probe generator
and close-out core have active branches. The later mint and rendering links
have been decided and scheduled but not yet built. None is described here as
landed evidence.

### Optional split-inference demonstration

Split inference remains feasibility-first:

1. A guaranteed synthetic-transfer microbenchmark moves cache-sized payloads
   between machines while measuring both ends.
2. The primary implementation persists the prompt cache, transfers it, and
   resumes generation with the same runtime family on the second machine.
3. Live streaming of the cache is a stretch goal and may be dropped without
   weakening the capstone.

Cache payload size is predictable from layer count, attention-head geometry,
numeric precision, and prompt length. That prediction sizes the link-speed
sweep before borrowed hardware time is scheduled.

### Analysis

Analysis consumes only validated bundles, keeps an exclusion log, regenerates
figures deterministically, and maintains a claim-to-evidence index from paper
sentence to figure, script, authenticated artifact, and raw bundles. The
results-fill registry is the exact list of values and branch sentences the
paper may request.

## Phase Plan Detail

- **Phase 1 — `docs/phase_1/`:** maintain the methodology and contracts; close
  advisor scope, calendar, wall-meter, topology, and remote-device inputs.
- **Phase 2 — `docs/phase_2/`:** operate the mock-proved, Mac-validated
  instrument; complete the Qwen3 campaign chain above; promote remote targets
  only after live evidence.
- **Phase 3 — `docs/phase_3/`:** run cache-portability spikes, the synthetic
  transfer study, offline replay, and only then an optional live split.
- **Phase 4 — `docs/phase_4/`:** authenticate floors and claims, regenerate
  figures, fill results and limitations, and complete the claims audit.
- **Phase 5 — `docs/phase_5/`:** verify the quickstart and extension guide,
  freeze the dataset with a hash manifest, and produce the final report and
  colloquium presentation.

Each phase closes only when its exit checklist contains evidence or a declared
blocker.

## Evolution From The Original Architecture Sketch

| original sketch | current position | reason |
|---|---|---|
| YAML or JSON configuration | normalized, sorted-key JSON; YAML deferred | stable hashing with a zero-dependency core |
| likely Pydantic schemas | standard-library data classes with the same contract | the core runs without optional packages |
| implement Mac first | deterministic mock vertical slice first, then Mac | prove controller and arithmetic before real telemetry can confound them |
| file-backed dashboard, perhaps a database later | static HTML and analysis files; no database planned | smallest tool that supports inspection and progress reporting |
| offline cache replay before live splitting | three-stage ladder: synthetic transfer, then offline replay, then an optional live split | cache representations are not generally portable across runtime engines |
| schedule cross-device pairs directly | require feasibility evidence before borrowed-hardware scheduling | bounds the largest execution risk and preserves a synthetic fallback |
| measurement boundaries mostly implicit | boundaries, clock discipline, uncertainty, and controller effects explicit | required for defensible physical energy comparisons |

The original controller-and-adapter architecture remains coherent. The changes
above strengthen evidence and bound feasibility risk rather than changing the
capstone into a different system.

## Risks And Minimum Viable Outcome

| risk | current posture |
|---|---|
| No claim-bearing Qwen3 data yet | preserve the fixed sequence; do not write results before authenticated artifacts exist |
| The four prompt lengths provide too few overlapping power records | retain every probe and issue the registered refusal instead of lowering the count floor |
| A machine night is lost to contamination or a failed gate | fail closed, preserve the evidence, and require a governed disposition; no silent retry |
| Timing attribution does not dominate repeatability by a factor of two | the close-out selects the non-dominance wording; the capstone remains a valid instrument result |
| Relationships among blocks affect the ten-block direction test more than its confidence interval assumes | complete the sensitivity analysis and narrow wording if needed |
| The inserted timing marker cannot be run or does not transfer | keep the headline conditional and report the limitation |
| Close-out or rendering programs are not ready when data arrive | keep them as explicit desk gates; no hand-filled claim sentence bypasses them |
| Remote cache replay or device access fails | use the synthetic-transfer study or omit split inference; neither blocks the core capstone |
| Academic calendar remains uncertain | sequence dependencies without promising dates; derive targets after dates are known |

The minimum viable outcome is a trustworthy, reproducible measurement
instrument plus a governed Apple-Silicon characterization and honest positive,
negative, or refusal results under frozen rules. Optional split and remote-
hardware work can add demonstrations but cannot redefine completion.

## Timeline

This document promises sequence, not dates. Live status is in `RUN_STATE.md`.

| order | stage | start condition |
|---:|---|---|
| 1 | four-rung prompt-length evening | Ed present, with no automated agents running on the M3 Max and the machine otherwise idle, so nothing else draws measurable power |
| 2 | desk selection, final pack generation, and throwaway-clone proof | immutable probe bracket, counts, and selector input |
| 3 | real-pack one-block shakedown | desk proof passes |
| 4 | Ed's claim-bearing transaction decision | complete, reviewable shakedown record |
| 5 | approximately one week of collection with nightly desk checks | Ed authorizes; each preceding night passes its check |
| 6 | floor mint, finalization, claim and dominance close-out, results fill | complete authenticated campaign custody |
| 7 | inserted timing-marker study, then optional scored-workload follow-up | campaign closes and its own gates pass |

Calendar dates, report deadline, colloquium date, and any borrowed-device
window belong in `docs/milestones.md` when known.

## Deliverables At Completion

- The JouleWise repository: instrument, adapters, tests, continuous
  integration, verified quickstart, and extension guide.
- An immutable dataset of raw run bundles with a hash manifest and every figure
  regenerable by script.
- Authenticated floor, finalization, claim, dominance-close-out, and results-
  fill artifacts that show exactly why each paper sentence was admitted or
  refused.
- Demonstration studies showing what the instrument can and cannot resolve,
  with uncertainty, dependence sensitivity, limitations, and hardware-
  applicability findings.
- The final capstone report and colloquium presentation, with each quantitative
  claim traceable to raw evidence.

## Repository Map (for verification)

| path | purpose |
|---|---|
| `README.md` | plain-language entry point and quickstart |
| `RUN_STATE.md` | live gates and next machine or desk step |
| `TASK_QUEUE.md` | detailed generated work queue |
| `docs/process/state_kernel.json` | machine-readable source for live work selection |
| `docs/process/v5-artifact-flow.md` | current probe-to-paper artifact chain |
| `docs/paper/results-fill-registry.md` | exact `_v5` paper fill contract |
| `docs/phase_1/` through `docs/phase_5/` | phase plans and evidence-gated exit checklists |
| `docs/contracts/` | measurement, evidence, campaign, and claim contracts |
| `docs/decision_log.md` | binding decisions and their rationale |
| `docs/risk_register.md` | risks, triggers, mitigations, and descope ladder |
| `docs/milestones.md` | calendar map when dates are known |
| `docs/run_reports/` | dated work records and verification evidence |
| `joulewise/`, `scripts/`, `tests/` | instrument package, governed artifact-generating programs, and tests |

## Process Note

The project is developed by a human researcher directing a reviewed,
multi-model engineering workflow. Ed owns research direction, physical machine
operation, external access, and final authorization of claim-bearing
collection. A designated lead owns decomposition, design rulings, final diff
review, verification, and integration. Separate implementers and reviewers use
distinct perspectives so that an assumption shared by code and its first test
does not become unchallenged evidence.

Consequential changes—measurement physics, pre-registration, evidence
identity, and paper-claim rules—receive deeper independent review than routine
bookkeeping. Raw evidence is immutable, review findings receive explicit
dispositions, and no agent performs final live-hardware verification on behalf
of the human operator. The 2026-09-01 fresh-model review is an example: it
found a stale live-work selector, missing close-out ownership, a frozen draft
that names the retired campaign, and dependence wording that needed a dedicated
sensitivity analysis. The work selector and ownership question are now decided
and recorded, while the follow-up code and paper work remain visibly in flight.
The earlier review by three independent reviewers on 2026-08-28 separately
found and repaired the nearly unfalsifiable headline rule before data existed.

Each fact has one owning artifact: decisions in `docs/decision_log.md`, live
work state in `docs/process/state_kernel.json`, deliberation in
`docs/council_log.md`, session evidence in `docs/run_reports/`, and raw
scientific evidence in immutable bundles. The complete operating model is in
`docs/orchestration.md`.

**Where to look.** Start with `RUN_STATE.md` for live status, this document for
the advisor view, `docs/process/v5-artifact-flow.md` for the current mechanism,
and `docs/decision_log.md` for binding choices. Front-facing changes update
`docs/site/DRIFT.md`; Ed deploys the status site manually.

## Maintenance Of This Document

Update this page whenever an advisor-visible gate, verdict, campaign step, or
claim boundary changes. Keep dates and work selection in their owning files,
preserve the frozen first paper draft, and never convert in-flight branch work
or fixture evidence into a landed or live result.
