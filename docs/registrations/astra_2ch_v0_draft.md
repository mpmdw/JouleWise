# ASTRA-2CH v0: two channels of weight-edit energy (DRAFT)

**Status: DRAFT, NOT REGISTERED.** Written 2026-11-07 for desk review.
Committing this file does **not** register an experiment, authorize a model
download, reserve a Mac window, or permit collection. No measurements were
made for this draft. All proposed choices below require lead review; an
`OPEN[A-n]` slot prevents registration until its evidence or ruling is pinned.
The companion [analysis plan](../analysis/astra_2ch/ANALYSIS-PLAN-v0-draft.md)
owns the arithmetic; this file owns the design, admission, and stopping rules.
They must be reviewed and sealed together before ASTRA-2CH collection.

**Authority and sources.** The task brief authorizes this draft only. The
[design study](../research-audits/2026-11-07/interp-weight-edit-energy.md)
§§1–4 and its [checks](../research-audits/2026-11-07/interp-weight-edit-energy-checks.md)
§§3, 10, 12 supply the rationale and planning numbers. The study's lead
synthesis governs over superseded seat proposals in its appendix and checks.
The [measurement contract](../contracts/measurement_methodology.md),
[analysis-plan contract](../contracts/analysis_plans.md), and
[decision log](../decision_log.md) govern measurement soundness, frozen sample
sizes, and claims. The block registrations supply format, not permission to
reuse their data, acceptance thresholds, or floors on a different workload.
Block 5 remains sealed and independent of this experiment. No sealed outcomes
or real measurement files were consulted; absolute paths in source documents
are text, not input locations for this work.

## 1. Question, estimands, and claim ceiling

Does the published Astra loop-removal edit change energy mainly by changing
the answers the model generates, and how tightly can a separate experiment
bound energy differences when both weight sets process identical tokens?
The candidate is dense Qwen3.5-0.8B in **bf16**, with the released 50-pass edit
applied once to a pinned base. The study describes changes to 64 output
columns in each of layers 15 and 19's MLP output projections, 131,072 weights
(about 0.016%). This is a source description to verify against the actual
artifact, not a checked implementation claim. No quantization, pruning,
runtime steering, or new direction discovery belongs to this experiment.

Two primary **estimands**, with different units and uncertainties:

| ID | Primary quantity | Scope |
|---|---|---|
| F-EPC | Energy per correct answer, `sum(request J) / sum(correct)`, separately for base/thinking-on and edited/thinking-on; edited/base ratio when estimable | Gross whole-machine energy at KM003C DC input plus signed battery assist; the frozen problem set, sampler and cap only. Includes energy of wrong and capped attempts. Estimation pilot, without a confirmatory superiority test. |
| T-DC | Mean paired edited-minus-base gross replay energy in J, its relative difference, and an upper confidence bound on its absolute magnitude | Identical prompt/completion tokens, single-token forced decode, the selected reference-sequence distribution; DC plus battery is authoritative. Equivalence at ±0.1% is a target that may be unattainable. |

Secondary quantities are F tokens per answer, accuracy, cap-hit rate, gross
request J per output token, gross decode J per decode step, J per problem,
and the two comparisons against base/thinking-off and base/thinking-on/8k.
T reports GPU rail, summed CPU+GPU+ANE rails, available IOReport channels,
DC minus rails ("rest"), decode time, frequency, and the A/A′ null. P reports
synthetic fill contrasts at each boundary. These are descriptive; no search
over secondary quantities can replace a primary result.

This is a single-machine pilot, consistent with Stage 1 of the study. Even
after registration it supports conditional estimates and instrument bounds,
not general claims about all edits or hardware, added model capability,
per-weight joules, an exactly zero switching term, or a novel literature
first. A rail-only bound must name that boundary. A whole-machine bound
requires the DC result. The formal test proposed here is T-DC equivalence;
F-EPC's small correctness counts limit inference regardless of meter quality.

## 2. Machine, boundaries, and time

Proposed measurement target: the actively cooled M3 Max MBP, with the KM003C
inline on DC input. Machine identity, OS, MLX/mlx-lm/Python, model/tokenizer
bytes, sampler, kernel policy, code commit, and meter configuration must be
pinned at `OPEN[A-1]`. The Air may validate software later; it supplies no
transferable energy or noise result. Batch size and concurrency are one.

The primary boundary is `E_DC = E_cable + E_battery`, where battery discharge
is positive and charging is negative. Report cable and battery terms
separately. Missing battery-assist evidence is not silently zero. KM003C is
the independent authority for small effects; a software rail can be insensitive
to operand values. IOReport and powermetrics are not independent corroboration
of physical power. Rest is computed on aligned spans before aggregation; it
is not a dedicated DRAM meter and includes other unreported system loads.

The request span starts immediately before prompt prefill and ends after the
last committed output and device synchronization. It excludes model loading,
fills, compilation, warm-up, weight swaps, scoring, and file serialization.
F includes its sampling work; T computes logits but discards them. Record
prefill/decode edges separately, but gross request energy is the headline.
Phase values with inadequate time support are `not_resolvable`.
Warm-up uses a separate fixed synthetic prompt and separate RNG state;
it does not generate an unreported second answer to a scored problem.

Use native sampler interval support and the approved common clock mapping;
do not invent sub-record power structure. Requested powermetrics cadence is
100 ms (the study reports about 130 ms delivered); KM003C's planning cadence
is 50 Hz. Actual cadence, alignment, gaps, battery interpolation, edge
envelopes, and non-averaging systematic bounds need local validation at
`OPEN[A-2]`. Gross energy is primary; request idle-subtracted results, when
available, are labelled sensitivities. Phase results remain gross-only.

## 3. Arms, blocks, and experimental units

### P: synthetic data-dependence and instrument check

Two separately analysed geometries: a fixed-shape bf16 GEMM (prefill-like)
and a weight-ring GEMV (decode-like), with **at least 1 GB of distinct,
explicitly written resident weight buffers**. Fix shapes, inputs, layout,
dtype, operations, synchronization, dispatch counts, and kernel path across
fills within a geometry. Do not optimize away outputs. Fills are seeded
random, all-zero, constant non-zero, row-sorted random (same histogram),
50% unstructured zeros, and A/A′ (two byte-identical random buffers).
The grade is a set of contrasts, not a predicted monotone ordering.

Each fill is contrasted with random using balanced randomized ABBA/BAAB
quads; A/A′ uses the same placement/swap procedure. A quad is four measured
spans and **one** contrast unit, not four independent replicates. Proposed
budget is 60–90 minutes across both geometries. Exact dimensions, constants,
zero masks, dispatch counts, durations, quads per contrast, order seed, and
matched-time/frequency tolerances are `OPEN[A-3]`, set from independent null
and timing work before P's fill-energy contrasts are read. Equal dispatch
counts are primary; do not force timing equality by changing work counts.

Report J/dispatch and mean W alongside duration. A time/frequency/kernel
mismatch makes the result a combined execution-path contrast, not pure
operand-power evidence. Check explicit stores, residency, and allocation;
zero-page, compression, or shortcut explanations remain possible. P cannot
prove the absence of data dependence when both instruments are flat.

### F: free-running behaviour channel

| Arm | Weights | Thinking | Output cap |
|---|---|---|---|
| F0 | base | on | 32,768 tokens |
| F1 | edited | on | 32,768 tokens |
| F2 | base | off | 32,768 tokens |
| F3 | base | on | 8,192 tokens |

Proposed n is **40 distinct MATH-500 problems**, one sampled answer per arm
per problem. Select a seeded subset without inspecting model responses or
energy; exclude any software-smoke or coefficient-calibration problems.
Freeze dataset revision, IDs, prompt templates, and the selection algorithm
at `OPEN[A-4]`. A problem with all compared arms is the paired analysis unit.
An answer is one attempt, not an independent replicate of its problem.

Use the study's reported Astra settings: temperature 0.6, top-p 0.95, top-k
20, presence penalty 1.5. Freeze their actual runtime semantics, chat
templates, stop IDs, answer parser, correctness checker, and seed mapping.
Seeds are paired per problem across arms; this does not guarantee identical
random choices after paths diverge. Randomize arm order within each problem
block, balanced across the 24 permutations over the manifest as nearly as
possible. No batching, adaptive sampling, retry-until-correct, or best-of-k.
Score the first answer only. A cap hit is scored wrong under the proposed
rule, even if a partial answer looks promising; report stop reasons.

The study's optional smaller design (30 problems, dropping F3 if throughput
is below 100 tok/s) is **not an in-window switch**. If independent software
sizing requires it, amend and freeze this design before collecting F. Neither
the 32k cap nor sampler may be changed in response to F results.

### T: forced-token weight-only channel

Select 12 F1 completion sequences by a frozen hash order: six cap-hit and
six uncapped, filling any stratum deficit from the other in that same order.
This intentionally samples the edited reference distribution, not both arms'
natural output distributions. Selection uses token validity and cap status,
never correctness, energy, residual, or apparent loops. Valid token streams
may be selected even if F energy was unavailable. Freeze the rule before F;
seal the selected token manifest before T. Fewer than 12 valid sequences
leaves the planned T design incomplete; do not invent replacements.

Each reference is run through base and edited weights in one randomly
oriented ABBA/BAAB quad. Reset **both KV and hybrid recurrent/DeltaNet state**
for every member. Prefill the identical prompt, compute its next-token logits,
then feed the reference completion one token at a time, computing and
discarding each next-token logit vector. For D committed output tokens,
prefill predicts the first and **D−1 single-token decode calls** predict the
rest; do not append an extra terminal call. Ignore model-predicted EOS during
replay. The reference IDs, count, prompt, cache policy, and tensor shapes
are identical across weights. This is not a batched teacher-forced prefill.

An A/A′ quad for every selected reference compares base against a
byte-identical copy with the same swap/placement machinery. One reference
and its quads form one cluster. Proposed n = 12 unique references; repeated
quads cannot inflate it. Weight loading, packing, buffer allocation, and
compilation finish before measurement; cache growth uses the identical pinned
policy in both arms. Swap only between spans after synchronization, without
reload or recompile; a compiled closure must not retain the previous weights.
Balance buffer placement; log swap latency outside the energy span.
Require bit-identical evaluated outputs for A/A′ under the pinned deterministic
path. Logits across **different** weights need not match; forced input tokens do.

A separate sensitivity control replays a hash-first subset through a bf16
copy with 50% of weights zeroed across **all MLPs**, with an otherwise
identical path. Subset size and mask are `OPEN[A-3]`. Its sign is not assumed
on Apple silicon; a bound is allowed. No int4 zero surrogate is used: affine
quantization can turn intended zeros into nonzero operands.

## 4. Floors and sizing: planning evidence, not ASTRA calibration

These are transcribed from design-study §2, not recomputed from any campaign.
They do not reveal new Block 5 information or license opening its artifacts.

| Study anchor | Planning value and limitation |
|---|---|
| Free-running token-model residual | SD 19–58 J on 2–4 kJ episodes (about 1–2%); cannot isolate a tiny fixed-token effect. |
| Token-identical whole-episode replay | About 2 J per measurement; pair-difference SD 2.97 J on about 2.7 kJ (0.11%); seven-session within-session scale 4.67 J. Different model/workload. |
| Session step | 8–9 J (about −0.41%), unattributed; no between-session pooling to manufacture precision. |
| Historical 50 J decode members | SD 0.21 J; absolute floors 2.94–3.59 J; comparative 6.80–7.38 J; attribution about 1 J; practical phase contrast about 5 J. These are phase anchors, not whole-replay/DC floors. |
| Known-bytes, hour interleave | GPU half-width about 1.05e−4 J/GB (about ±11 mW); rails ±0.22 W, DC ±0.77 W, rest ±0.89 W at that geometry. DC's J/GB half-width about 0.0072, roughly 70× the GPU value. These are summed conservative bounds, **not standard errors**. |

The study's paired planning law is `MDE80 ≈ 2.80 × SD(pair difference) / sqrt(n)`:
at 2.97 J and 2.7 kJ, n=16 gives 2.08 J (0.077%), n=64 gives 1.04 J
(0.038%). Thus 0.04–0.1% is an optimistic replay planning range, not a
promised DC bound. The study's ≈11 pairs for ±0.1% equivalence is likewise
an approximate variance-only calculation, not native small-n power analysis.
An ABBA contrast's local SD must be measured on its own definition.

Before registration, independent A/A′ work at the actual model, sequence
lengths, boundaries, and clocks must fill `OPEN[A-2]`: absolute/comparative
floors, systematic envelopes, null SD, joules per unit, and finite-sample
power/MDE for the proposed n. Keep calibration separate from scored F/T.
Floors and edge/battery bounds do not shrink as `1/sqrt(n)`. If 12 references
cannot resolve ±0.1% at DC, retain an explicitly wider upper-bound deliverable
or prospectively redesign before collection; do not substitute a finer rail
interval for DC. The equivalence margin is never widened after outcomes.

## 5. Admission, exclusions, and missingness

All live work requires an Ed-authorized, lead-controlled quiet window with
no active agents, displays asleep, AC/battery state recorded, and nominal
thermal level 0. This session cannot start or continue such work and must
not interfere with the existing blinded analysis job. Local quiet/admission,
contention, cooldown, and matched-frequency rules are `OPEN[A-5]`; the study's
0.05 CPU-s/s per-process monitor is a planning pointer, not an installed
ASTRA exclusion threshold. Existing campaign thresholds do not transfer by
copying their numbers. A deadline, not repeated waiting for a favorable
instrument value, bounds admission.

Freeze a reason catalog before collection. Proposed effects:

- Wrong identities, corrupted/missing tokens, replay count/path mismatch,
  nonfinite runtime output, or unresolved clock alignment invalidate the
  affected member's energy. A wrong/empty **finite** answer or cap hit is a
  behavioural outcome and remains in F with its spent energy.
- A meter gap or unknown battery term removes DC and rest for that member;
  independently valid rails remain descriptive. No rail-to-DC imputation.
- Thermal, timing, or frequency failures under the frozen local rules remove
  eligibility for the matched-state T/P interpretation. Keep and disclose
  the measured execution-path contrast separately.
- A paired F contrast requires both arms' valid energy and scores; an
  incomplete T/P quad removes that quad, not an arbitrary favorable subset.
  Keep all raw members and list missing/excluded IDs and reasons. An F
  all-arm complete-set sensitivity accompanies pair-specific sets.
- Energy magnitude, correctness, loop appearance, model-fit residual, and
  modified-z/MAD outlier status are never exclusion causes. Flag outliers;
  perform influence checks without deleting them.

F reports paired coverage against all planned problems, with correctness
and energy denominators from the **same** eligible set. Below five complete
problem blocks or five independent T quads, show raw/descriptive results
only, with no inferential decision. This minimum follows the measurement
contract and is not evidence of adequate power. Missing-score/runtime-abort
attempts and energy spent are disclosed separately, not silently scored as
ordinary wrong answers or used to inflate accuracy. No post-outcome top-ups
or replacements are planned.

## 6. Blinding and release

Before collection, pin a manifest containing coded weight identities,
problem IDs, sampler seeds, orders, scripts, floors, analysis code, and all
completed slots. An independent custodian holds the code-to-weight map.
The analyst receives coded energy bundles and technical validity metadata;
the scorer receives answer text and checker inputs without energy or weight
labels. Text and lengths can reveal loops: scorer/length blinding is imperfect
and must be disclosed, not claimed as effective arm concealment.

Freeze scripts, eligibility decisions, checker results, and a synthetic
analysis dry run before joining outcomes or releasing the weight map. Custody
implementation, permitted structural disclosures, identities, hashes, and
release-record location are `OPEN[A-6]`. The release event binds the final
inventory and exclusions. This release applies to ASTRA only; nothing here
changes Block 5's blinding or authorizes its analysis pipeline.

## 7. Decision rules and stopping

The analysis plan defines intervals widened by systematic bounds. Always
print point, interval, floor, n, denominator, and boundary together.

| Outcome | Required reading |
|---|---|
| T equivalent within ±0.1% | DC local floor below the margin, valid null/path/instrument evidence, and TOST passes including systematic uncertainty. Say only "equivalent within ±0.1% on this boundary and reference set". |
| T upper bound | Valid DC analysis yields an absolute-magnitude confidence bound, even if equivalence fails. Print J and %; if wider than 0.1%, say that target was not established. |
| T not resolved / unresolved | An estimate below the local floor is `not_resolvable`; above-floor evidence whose interval spans zero is `unresolved`. Neither means zero. A resolved unexpected effect requires diagnosis before any switching attribution. |
| T not estimable | Missing clock/battery/null evidence or too few complete units prevents a defensible bound; print the reason. Rails alone cannot repair a missing DC conclusion. |
| F frontier | Report EPC and correctness uncertainty including unbounded/undefined ratios. No universal Pareto or superiority claim from a few correct answers. The base-off and budget comparator remain visible even if unfavorable to the edit. |

For P predeclare: both DC and rail resolve a matched-state contrast; DC
resolves while rail is equivalent within its own locally justified margin;
or neither resolves and both bounds print. A DC-only outcome is consistent
with rail insensitivity **or** an off-rail effect, not proof of Apple's
implementation. Rail-only detection, rail non-detection without equivalence,
opposite signs, invalid timing, and missing meters receive explicit
inconclusive/discordant labels. Do not force them into "both flat". P failure
does not erase F; it limits the interpretation of T to the supported boundary
and sensitivity. Positive controls can themselves yield upper bounds.

Proposed collection stops at the frozen roster or the authorized window
deadline, whichever comes first; allow a quad to start only if its pre-sized
worst-case duration fits. Safety/identity/thermal failures trigger the frozen
abort rule. No stop for accuracy, effect sign, p-value, equivalence success,
or a nicer bound. Preserve incomplete rosters; no new night or extra pairs
without a prospective amendment. Study estimates are about 2.6M F tokens
and 1M T tokens, with ≤12.4 h as the proposed total window ceiling. These
are **estimates**: size the actual F, ABBA, A/A′, controls, baselines, and
cooldowns at `OPEN[A-7]`; no window is yet promised.

Study predictions (not success criteria) are F1/F0 tokens about 0.40–0.55,
cap hits falling toward the source's 32–33%, about 12–15× EPC improvement
against the poor base-on setting, and a tiny fixed-token residual. The
generous surgical bound ≈3e−5 of energy and more plausible ≲1e−6 are physics
estimates, not measured floors or guaranteed upper limits. Accuracy against
base-off may be similar. Fresh token-plus-context modelling tests explanation;
"90% explained" is descriptive and never a stopping or exclusion rule.

## 8. Deviations and decisions needed before registration

Before seal, record substantive design changes with date, reason, and which
data were visible. After seal, preserve originals and make a prospective
versioned amendment for later collection only. No repair changes an already
collected arm, cap, score rule, floor, exclusion, estimand, or sample size.
An outcome-driven extension is exploratory permanently; report the original
fixed roster as well. Lead review and any required independent review must
precede registration; this author does not adopt new project policy.

| Slot | Lead / Ed decision and evidence needed |
|---|---|
| OPEN[A-1] | **Ed: download permission** for the ≈1.6 GB bf16 base and small edit artifact; **lead: edit source**, license, revision, hashes, apply script, realized bf16 tensor diff, tokenizer, runtime support. Prefer authors' diff on the pinned base; choosing a third-party checkpoint requires provenance verification. Nothing is downloaded here. |
| OPEN[A-2] | Lead: native clock/battery/meter validation, local A/A′ floors and uncertainty at each boundary, rail margin for P, MDE/power and whether DC can support ±0.1%. No existing study floor is installed as ASTRA truth. |
| OPEN[A-3] | Lead: exact synthetic P manifests, repeats and duration budget, matched-path tolerances, and whole-MLP control subset/mask. |
| OPEN[A-4] | Lead: MATH-500 revision and disjoint smoke/calibration/scored IDs, checker/cap semantics, templates, seeds, order and reference-selection implementation; approve 40/four-arm design or a prospective smaller version. |
| OPEN[A-5] | Lead: measured quiet, thermal, frequency, contention and cooldown admission/exclusion catalog and bounded abort rules. No changes to the currently running job. |
| OPEN[A-6] | Lead / Ed: custodian, blinded coding, release inventory and deviation-record implementation, final reviewer and seal commit. |
| OPEN[A-7] | **Ed: Mac windows and priority** after already ranked work (including BYTES, ALIGN, and Paper 1 obligations); lead: native throughput and full wall-time sizing. The study banks this direction; this draft schedules nothing. |

Native checks the lead must arrange **outside this sandbox**, after separate
authorization: dense hybrid MLX load; edit hashes and nonzero bf16 changes;
A/A′ deterministic logits and reference token identity; KV/recurrent reset;
one-token decode counts; no swap reload/recompile; kernel/residency checks;
clock/battery/meter gap cases; and a disjoint 20-problem software smoke. The
study proposes edited cap hits within ±10 percentage points of its published
32–33% before proceeding; the lead must freeze the source target and exact
smoke rule before running it. A failed smoke stops for diagnosis, not editing
against scored prompts. No MLX implementation or native test was executed
for this documentation task.
