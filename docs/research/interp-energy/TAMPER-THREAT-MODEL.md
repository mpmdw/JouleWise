# Tamper detection by energy and timing

**DESK DESIGN — NOT REGISTERED — all new results are synthetic.** No capture,
model download, Block 5 analysis or Mac window is authorized here. This develops
ranked ideas **10, 11 and 13** in the
[design study](../../research-audits/2026-11-07/interp-weight-edit-energy.md#3-ranked-idea-table).
The companion [checks](../../research-audits/2026-11-07/interp-weight-edit-energy-checks.md)
number those ideas **16, 5 and 15**, respectively. They are the evidence source
for historical rig figures and literature pointers below; sources were not
independently reopened or checked over the network in this task.

## The claim and the observer

ALIGN's proposed claim that “sabotage leaves an energy signature” must be
conditional: **unaccounted physical work on an observed boundary can leave a
residual above that boundary's noise and attribution floor**. It cannot mean
that malicious intent, changed weights, or every successful sabotage is
observable. Logged malicious outputs can cost exactly what the token/context
model predicts. A harmless background task can produce the same residual as
hidden training. A smaller substitute can create a **negative** residual.

The study places unlogged editing under ALIGN E2's hidden-work dose response.
The addition is a joules-per-edit map and explicit evasion controls, rather
than a new interpretation of ALIGN's frozen score or thresholds. The simulator
here is a separate, exploratory two-sided GPU/DC detector. It does **not** alter
the existing positive-tail GPU-only ALIGN implementation or reproduce its
registered inference. See the [wave-1 integration limits](../../run_reports/interp-energy-desk/INTEGRATION.md).

Assume a local observer controls token/event counting, reference runtime,
telemetry clocks and an independently trusted DC meter, while an actor can
change resident parameters or runtime precision after load. Where the observer
can inspect the actual resident weights, hashing or attestation is more direct.
A file hash at load does not attest later memory mutations. Remote APIs usually
offer neither trusted power nor trusted local timing: this design does not
solve their substitution-audit problem. A compromised host can forge software
rails/logs; physical energy alone does not repair forged token accounting.

| Actor | Allowed action | Required comparisons | Detection ceiling |
|---|---|---|---|
| Non-adaptive | Changes values, precision, structure or performs hidden editing, without observing the score | Frozen energy residual; count-conditioned timing baseline; their joint decision | Large work/precision changes may flag. A flag identifies an anomaly, not intent or edit identity. |
| Timing-masked | Pads a cheaper substitute with sleep/idle or overlaps editing with a pre-existing tool-wait gap | Same token IDs and equal observed elapsed time, with GPU and DC residuals | Idle padding may leave a negative energy signal. Work in a wait gap may leave a positive one. Neither has a guaranteed size. |
| Adaptive | Knows the detector, allocates dummy CPU/GPU work, precision and latency budget, possibly queries an audit endpoint | Frozen held-out challenges and boundary-specific scores; record attacker budget and access | Matching the joint observed energy/timing distribution defeats these features. Busy-work matching is an explicit counterexample, not a verified real attack. |

All three can use a precomputed delta, harvested logged activations, a CPU
closed-form update, or a tiny merged edit. These negative controls prevent a
training-heavy experiment from implying universal self-modification coverage.
The study's “Astra” example edits another model; it is not evidence that the
serving model autonomously changed itself.

## Channels and rig limits

Gross task energy changes through **behaviour** (token count and growing context),
**structure** (bytes, shapes, kernels, top-k), and **switching** (operand values
at identical work). A dense zero mask preserves dense bytes and operations;
it is a switching hypothesis, not structural pruning. Fixed-k expert identity
changes retain the active-byte count at batch one. Unmerged LoRA adds kernels
and repeated adapter reads; merged LoRA is a value-only arm. Quantized outliers
can collapse their neighbours' codes; define that separately from bf16 outliers.

| Observation | What it can reveal | What it cannot establish |
|---|---|---|
| GPU-rail gross energy minus frozen count/context prediction | Sufficient hidden GPU work; persistent extra kernels; negative precision/structure anomalies | CPU-only work; malicious intent; whether excess joules were training, inference or contention |
| CPU/total rails or DC-input energy | Part of the CPU gap; whole-device changes missed by the GPU rail | Per-component causal attribution; DC minus rails is a residual boundary, not a measured DRAM rail |
| Count-conditioned latency | Large plain precision/structure swaps and serial hidden work | A swap with padded timing; hidden work entirely within a tool-wait gap |
| Fixed-token replay/lock-in contrast | A bound on weight-dependent residual cost at matched work | Semantic integrity or absence of a tiny edit; a general gain from faster chopping |
| Free-running task energy | Behaviour-mediated cost changes, alongside quality/cap-hit outcomes | A switching effect without a separate fixed-token comparison |

The study quotes GPU paired replay SD **2.97 J on about 2.7 kJ**, cross-session
variation about **4.7 J**, and fresh-episode residual SD **19–58 J**. Those are
different units and contexts. An episode monitor cannot borrow the replay SD.
Absolute uncertainty does not scale down just because a smaller model is used.
The simulator uses 2.97 J white paired noise or an illustrative 35 J episode
noise, then adds colored noise, bursts and session shifts. DC SD 12/80 J,
timing SD 0.12/1.5 s and the DC/GPU factor 1.8 are **assumptions**, not measured
rig calibrations. The 0.5 J systematic bound used in planning is also a
sensitivity input, not an earned instrument bound.

Software rails may be activity models blind to operand values. A surgical null
there can be an instrument limit. Require the existing S1/ASTRA block-P gate
with GPU rail and KM003C before a physical weight-fingerprint claim. Rail+DC,
DC-only and neither-moving outcomes must all survive the reading rule. Coarse
rail cadence (about 130 ms in the study) and DC aggregation cannot inherit
the cited H200 study's roughly 10 MHz probe results. No frequency resolution,
causal attribution or sensitivity transfer is assumed. The latency-bound KB
J/GB coefficient is not used to size bandwidth-bound precision effects.

## Synthetic implementation and predictions

[tamper_detection.py](../../../joulewise/interp_energy/tamper_detection.py)
reuses `behaviour_channel.Answer`, `EnergyModel` and `answer_energy` for the
token/context prediction. It uses `lockin.make_schedule`, `simulate_trace` and
`abba_differences` for a correlated noise surrogate, and `power.plan_power` for
the independent-pair normal approximation. It neither executes model edits nor
loads artifacts. Existing `weight_edits`, `forced_decode` and S1 tools remain
the future execution path; no second replay or edit engine is introduced.

For logged counts p,d, the reused model charges
`fixed + a*p + b*d + c*(p*d + d*(d-1)/2)` in gross joules. Fit and freeze its
coefficients on benign training data in a later study. Keep separate benign
calibration units, blinded challenge units and unused holdouts; never refit
energy coefficients on substituted models. This desk simulation supplies
coefficients rather than estimating them. Its timing prediction is conditioned
on logged work; elapsed time is not fitted into the energy model, where it
could absorb hidden compute.

The synthetic baseline is 2698.37 J over an assumed 100 s. Examples are
deliberately explicit scenario assumptions:

| Scenario | Assumed GPU residual | Timing residual | Interpretation |
|---|---|---|---|
| Astra-scale merged edit | +0.027 J (10^-5 relative) | 0 | Below the replay floor; a weak result must remain a bound |
| Rank-one edit | +0.094 J | 0 | Statistics-preserving scenario, not a ROME measurement |
| Dense zero/outlier ladder | Sweep negative, zero and positive fractional effects | 0 | Unknown Apple switching response; no guaranteed positive label |
| Structured pruning | −10% | −10 s | Bytes/shapes actually shrink; not dense zeroing |
| Plain 8-to-4-bit substitution | −35% | −35 s | Hypothetical memory-bound time-at-flat-power saving; also trivial on a stopwatch |
| Same substitute + idle padding | about −874 J | 0 | 35 s at assumed 2 W GPU / 12 W DC idle power leaves a large energy deficit |
| Same substitute + adaptive dummy work | 0 on GPU and DC | 0 | Joint feature matching stipulated by construction; coverage cannot be claimed |
| Hidden GPU edit / identical logged edit | +200 J / 0 residual, same +200 J gross | +8 s / 0 residual | Accounting sensitivity; physical dose must match in a real control |
| GPU edit inside tool wait | +200 J | 0 | Requires at least enough pre-existing slack; tests value beyond timing |
| CPU edit / precomputed delta apply | 0 GPU, +40 / +0.1 J DC | 0 | GPU blind spot; a small DC effect may also be unresolved |
| Unmerged LoRA | +3% | +3 s | Hypothetical persistent kernel overhead |
| Behaviour shortening | Large negative gross change, zero residual | 0 after count adjustment | Legitimate work savings accounted for by the behaviour model |

Dose should be varied in joules (e.g. 0,25,50,100,200,400 J), alongside actual
training tokens × epochs, forward-probe tokens × batches, model and boundary.
Do not translate “50 forward passes” into 50 token-level forwards. Training
can amortize weight reads and cost less per token than memory-bound decode.
Meter dose independently with paired replay; do not infer it from the flag.
Use an identical logged burst, model residency and thermal schedule for the
accounted/unaccounted control. Thermal carry-over is not modelled here.

Calibration freezes a two-sided absolute threshold per GPU/DC/time channel at
an `(m+1)`-corrected empirical quantile using alpha/3. The maximum normalized
score gives a joint anomaly decision; signed residuals remain available.
Under exchangeability the Bonferroni union bound limits benign error. Drift
and session dependence can violate exchangeability: report held-out sham FPR
and channel errors; do not present that guarantee for this stress population.
Matched tamper/sham observations share the same simulated session offset;
the calibration realization has its own offset. Forced-choice comparison asks
which of a tamper/sham pair has the greater
anomaly score, with fair ties. It is **binary detection**, not edit-class
identification. Timing-only and energy-only results accompany the joint result.

Lock-in noise is an 8 Hz ABBA surrogate, scaled so its white component has the
chosen absolute paired SD. Its eight-second blocks do **not** assert that
short chips achieve long-replay sensitivity. Pink noise, thermal relaxation,
a step, positive bursts, GPU/DC covariance and a shared session shift stress
the estimator. Noise is generated in bounded 256-block segments: each has its
own finite pink spectrum, relaxation and step; only the session shift spans
the whole realization. No long-range spectral law is claimed between segments.
The simulation is one chronological realization with randomized
class interleaving; it reports descriptive rates, no independent-trial CI.
Independent-pair power columns omit those extra noise terms and say so.

## Blinded challenge: replace three copies with an actual power target

[tamper_challenge.py](../../../joulewise/interp_energy/tamper_challenge.py)
provides exact binomial power and a synthetic analyst roster/curator key.
At three independent copies, even 3/3 forced-choice successes has one-sided
null p = **0.125**. It cannot reject chance at 0.05. Replaying those three
copies repeatedly improves a copy's measurement, not the count of independent
edit instances.

Freeze a one-sided forced-choice null p0=0.5 and a weak alternative p1=0.60,
power ≥0.80, family alpha=0.05. Count **all searched class contrasts** before
collection, including nulls/controls. The default broad 17-class sensitivity
plan needs **325 independent tamper copies per class**, each with a separate
matched sham, and rejects at ≥188 successes. Exact per-class size is
0.0027322 (≤0.05/17); power at 0.60 is 0.802397. Bonferroni works across
dependent class tests, but the binomial calculation still requires independent
copy decisions *within* each class. Repeated copies of the same edit, prompts
or correlated sessions do not satisfy it. A class is an independent seed /
target / direction realization from a declared edit-generating distribution;
duplicate byte-identical edits count as measurement repeats.

With eight paired replay observations per artifact, separate matched shams,
and an assumed 200 s per base-versus-copy pair, that broad plan costs **4911
acquisition hours before overhead** (11,050 artifacts). This deliberately
exposes why the proposed half-night six-class challenge is untenable. It is
**banked, not a proposed booking**. A future owner can prospectively narrow
the family and effect target or choose a dose/equivalence study; they cannot
claim 60%-versus-chance power from three copies or select classes after seeing
their separability. A 70% target answers a different, easier question.

Use this later protocol, conditional on S1 and new authorization:

1. Freeze the artifact-generating distribution, class/dose roster, prompt/token
   bank, model/runtime/dtype/quantization identity, channels, metrics, comparator,
   thresholds, families, fixed n, missing-data disposition and holdouts. Keep
   calibration, tuning and test artifacts disjoint. This memo is not an
   analysis registry or a new policy ruling (D-037/D-053/D-062/D-067 apply).
2. A curator generates opaque IDs and an independently stored assignment key.
   `make_challenge` randomizes the order independently in each replay round
   and binds the public roster with the existing canonical digest. Its public
   rows contain only copy ID and repeat index. The seed and curator key stay
   private; reproducible PRNG IDs are not cryptographic blinding if the seed
   leaks. Native custody and key commitments are future lead-owned work.
3. For **value-only** classes attest identical shapes, dtypes, tensor names,
   quantization groups/config and byte counts. Hashes differ; check outside
   timed work. Dequantize/edit/requantize through the same path for all arms,
   including sham, and verify a nonzero stored delta survives rounding.
   Precision and structure controls intentionally differ internally. Present
   every artifact in the same outer packaging; hide filenames, sizes,
   metadata, preparation cost and class key from the analyst. The desk roster
   tests field separation; it does not validate real artifact formatting.
4. Load/warm outside the owned window. Use the existing forced-token replay
   with fresh caches and matching token/policy hashes, logits policy and model
   identities. Resolve the wave-1 ASTRA counting-boundary discrepancy first.
   Balance ABBA/BAAB and interleave classes, session positions and sequence
   assignments; cross copies with prompts/sessions. Thermal/frequency gates,
   content-swap and A/A′ nulls, 0.5/1/2/4 s chip sweep and instrument guards
   remain mandatory native design items. Log routing agreement where relevant.
5. Aggregate repeats into **one frozen decision per independent copy**. Balance
   pairing within sessions, assess residual session/copy dependence, and use
   session/copy cluster resampling or a predeclared blocked randomization test
   if independence fails. In that case recompute power under that design
   before collection; 325 is no longer a sufficient guaranteed n. The roster
   generator supplies randomized slots, not a native session allocator or
   analysis implementation for the clustered case.
6. Lock predictions and quality exclusions before unblinding. Report TPR,
   sham FPR/specificity, channel results, timing-only comparator, paired
   forced-choice rate, class-wise uncertainty, dose curves and gross changes.
   Failure to beat chance is **inconclusive** without a powered interval;
   it is not equivalence or proof of no side channel. Report exclusions and
   the original fixed-n analysis; no outcome-driven top-ups.

For energy equivalence use a prespecified ±0.1% margin (2.7 J at the study
unit), justified independently of the observed result, and widen intervals
by the instrument's fixed systematic bound. The supplied normal planning
function keeps
`Var(mean) = pair_sd²/(copies*replays) + copy_sd²/copies + session_sd²/sessions`.
It assumes ideal balanced session weights in a connected crossed design;
individual copies may visit subsets of sessions. For unequal session weights
use their squared-weight sum in place of `1/sessions`. The examples below
are ideal-balance sensitivity calculations, not a constructed session roster.
At 325 copies × 8 replays, copy SD .3 J,
session SD 4.7 J and bound .5 J, zero-effect TOST power after alpha/17 is
0 with 16 sessions, about .668 with 64, and .987 with 128. Those are **known-SD
planning calculations**, not achieved live coverage. Unknown variances need
small-sample/cluster inference and their own sizing. Under pure independent
2.97 J paired noise, centered known-SD TOST at ±2.7 J needs 13 pairs for
80% power at alpha .05; the study's 11-pair shortcut understates that centered
two-tail requirement. Systematic and session terms can dominate either count.

## Desk commands and remaining gates

```sh
python3.13 -B scripts/interp_energy/tamper_detection.py --design-only
# Use an already installed NumPy interpreter; no package installation needed.
python3 -B scripts/interp_energy/tamper_detection.py --mode replay --seed 17
python3 -B scripts/interp_energy/tamper_detection.py --mode episode --seed 17
python3.13 -B -m unittest tests.interp_energy.test_tamper_challenge
python3 -B -m unittest tests.interp_energy.test_tamper_detection
```

The numerical demo uses one observation per independent synthetic copy; the
eight-replay, multi-session challenge above is a design, not an implemented
native collection or clustered reducer. No new MLX path is needed for this
simulation. Module discovery and stdlib planning import no MLX or NumPy.
Numerical tests skip when NumPy is absent. Python 3.13 numerical validation
and Python 3.11 compatibility remain lead/CI checks in this environment.

Outside this sandbox, the lead must run the reused native tests individually
on an authorized Metal-capable **non-measurement** machine, without downloads:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

Native tiny-model tests validate software only. A later lead-controlled quiet
window must establish the S1 rail/DC gate, noise spectrum, paired and session
variance, padding powers, artifact blinding, timing match and true dose. All
physics, rig feasibility and detector coverage remain **PROVISIONAL**.
