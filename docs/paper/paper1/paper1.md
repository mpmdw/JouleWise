<!--
PAPER 1 — FULL DRAFT WITH PLACEHOLDERS (written 2026-10-27, before any block-5, block-6 or BYTES
result was released or seen by the author).

How to read this file:
- Every measured energy, floor, ratio, outcome word, count derived from collected data, and BYTES
  result is a placeholder {{FILL: <id> | <what it is>}}. Ids are listed in fill_index.md with the
  artifact and field that supply each one.
- Where the text must depend on an outcome, it is written in labelled branches:
  **[BRANCH <id>.<n> — <condition>]** ... **[END BRANCH <id>]**. On fill, keep exactly one branch of
  each group (the one the issued artifact selects) and delete the others. Never choose a branch by
  reading a number; the branch is selected by the artifact's outcome field named in fill_index.md.
- Synthetic worked examples are labelled "synthetic" and are not results.
- Shorter alternative sections for the contingency tiers B-E are in variants/.
- This text changes no registered analysis. If wording here and a registration differ, the
  registration governs and this text is corrected.
-->

# Dividing a Laptop's Inference Energy Between Phases with On-Chip Power Sensors: Detection Floors, Attribution Limits, a Replication, and a Pre-registered Test of Energy per Byte

{{FILL: CP-X02-headline | contingent subtitle, printed only under dominance branch A (every required dominance ratio at least 2): "An attribution-limited measurement"; under branch B no subtitle is printed}}

## Abstract

Language-model inference has two phases: *prefill*, in which the model reads the prompt and computes the first
output token, and *decode*, in which it writes the remaining tokens. We ask how finely a laptop's own power
sensors can divide inference energy between these phases, and we answer with a method whose limits are part of
its output. On one Apple M3 Max laptop running the MLX framework, the operating system's power sampler reports
the average power of the processor package (CPU, GPU and neural engine) over records of roughly a tenth of a
second. We assign each record's energy to a phase in proportion to its time overlap with the phase, and we carry
every source of timing uncertainty into the result: a calibration with commanded GPU pulses before and after
each measurement session, a fitted clock mapping, and a drift screen built from repeated reference requests.
From these we derive four quantities: the reported phase energy with an interval, the *attribution floor* (how
far timing alone can move one request's assigned energy), the *detection floor* (the largest difference the
instrument produces when nothing differs), and the *dominance ratio* (how much timing uncertainty enlarges the
detection floor). We then report a pre-registered, blinded experiment on Qwen3-1.7B and Qwen3-8B (4-bit), with
a 512-token decode workload and a 2,048-token prefill workload, two primary model contrasts with Holm
correction, an independent recomputation of every headline number from the raw records, and a replication in
further sessions on later days. {{FILL: P1-ABS-PART1 | one or two sentences summarising Part 1, assembled from
the issued outcome fields only: the four reported cells' L1 statement with intervals (CP-X05-*), the dominance
branch (CP-X02-abstract / CP-X03-abstract), the decode and prefill contrast outcome words and, only where the
claim gate returns L2, the registered direction (CP-X08-*-abstract), and the replication word per contrast
(P1-B6-REPWORD-decode, P1-B6-REPWORD-prefill)}} In a second part, BYTES, we test whether decode energy per
token on the same laptop follows the bytes the model reads per token, its resident size in memory, or its
decode time: three straight lines are fixed on three dense models and committed before ten held-out models,
including three mixture-of-experts models, are unblinded. {{FILL: P1-ABS-PART2 | one sentence: the H1 verdict
words for the held-out models at the processor-rail and DC-input boundaries (P1-BY-H1-WORDS-*), the
active-or-resident answer (P1-BY-AR-*), and the primary energy-per-bandwidth coefficient with its interval
(P1-BY-H2-*), in the registered wording only}} Every phase energy reported here rests on sampler timing that no
independent instrument checked at phase resolution. The study was run by a pipeline of AI agents under human
direction; we describe the controls that kept the agents from changing what was measured or how, and where
those controls failed.

## 1. Introduction

### 1.1 The question

A large language model (LLM) generates text one *token* at a time; a token is a short piece of text such as a
word, part of a word or a digit. Serving one request has two phases. In **prefill** the model processes the whole
prompt and computes the first output token. In **decode** it produces each later token with one *forward pass*
through the network, reading its weights and the stored keys and values of earlier tokens (the *KV cache*) from
memory. The two phases load the hardware differently: prefill is dominated by arithmetic over many prompt
tokens at once, decode by memory traffic for one token at a time. Their energies therefore answer different
questions, from the cost of long prompts to the cost of long answers.

Measuring phase energy on a laptop is attractive because the sensors are already there. macOS exposes the
processor's power through its `powermetrics` sampler, with no external meter and no special hardware. But a
software sampler reports *averages over records*, not instantaneous power, and its records do not line up with
the phase boundary. A record that begins in prefill and ends in decode reports one average for both. Any split
of that record between the phases is an allocation, and the allocation moves when the boundary moves. The
question this paper asks is therefore not only "how much energy does each phase use?" but first "how finely can
these sensors divide energy between phases at all, and what limits that?"

### 1.2 Approach

We treat the instrument's limits as results. Every reported phase energy carries:

- an interval that combines run-to-run scatter with three recorded bounds: how far the phase edges could sit
  from where they were placed, a (zero, for these traces) interpolation bound, and an allowance for drift over
  the measurement session (Section 3.4);
- an **attribution floor**: the largest amount by which phase-edge timing alone could move the energy assigned
  to one request's phase (Section 3.5);
- a **detection floor**: the largest energy difference the instrument produces between runs that do the same
  thing, and hence the smallest real difference it can resolve (Section 3.6);
- a **dominance ratio**: the factor by which allowing each value to move within its timing uncertainty
  enlarges the detection floor. A ratio of at least 2 means that timing attribution, not ordinary repeatability,
  limits the measurement (Section 3.7).

We fixed every rule (which runs count, which are excluded, every estimator and every sentence that may be
printed under each outcome) in registrations written and sealed before the data existed, kept every energy
hidden from people and agents until a recorded release, and recomputed the headline numbers with independent
code before release (Section 4).

### 1.3 Contributions

1. **A phase-attribution method with explicit limits** for interval-average software power records: an overlap
   rule, timing bounds derived from in-session GPU-pulse calibration and a fitted clock mapping, a detection
   floor with timing-widened corners, an attribution floor, a dominance ratio, a drift allowance from
   reference requests with a labelled scaled sensitivity line, and a whole-machine cross-check at the laptop's
   power input (Section 3).
2. **A pre-registered, blinded measurement and its replication**: reported phase energies for two models, two
   primary model contrasts under a multiplicity correction and a claims ladder that caps what each result may
   say, and a replication in further sessions whose agreement word was defined before any data (Sections 4
   and 5). The outcome is publishable whichever way it falls: a contrast that is not resolvable is a statement
   about the instrument's resolution, and pre-registration is what makes it one.
3. **BYTES, a pre-registered test of what drives decode energy per token** on the same laptop, with rival
   lines committed before held-out models were unblinded and mixture-of-experts models used to separate
   bytes read from bytes held (Section 6).
4. **An account of research run by AI agents** under human direction, with the integrity controls that
   constrained them and the failures those controls did and did not catch (Section 7).

### 1.4 What this paper does not claim

All measurements come from one laptop, one operating-system build per session, one inference framework and
one sampler. The phase split rests on the sampler's own timing; no independent instrument checked where energy
falls within a record or at a phase edge. The decode workload uses one fixed prompt, and the prefill workload
one prompt length. The whole-machine meter measures power entering the laptop after its adapter, not at the
wall. Section 8 lists these and the other limitations in full.

## 2. Background and related work

### 2.1 Software power counters: gain and time

Running Average Power Limit (RAPL) is an energy counter exposed by Intel and AMD processors. Khan et al. and Jay
et al. study the *gain* of such counters: how accurately a software counter reports the magnitude of energy
use against an external wall meter [4] [5]. Khan et al. align lag, model the relationship between RAPL and wall
power, account for temporal correlation and inspect update granularity, sampler overhead, jitter, overflow and
timestamps [4]. Jay et al. find that the disagreement between software meters and wall power changes with load,
and they decline component-level claims that their reference meter cannot test [5]. Agreement of whole-request
totals with a wall meter does not by itself validate how a software trace divides those totals between phases.

The *time* axis is closer to our problem. Hähnel et al. show that RAPL's update interval limits how short a code
path can receive a defensible energy attribution, and they align the start and end of the measured path to the
counter's own update boundaries [19]. Dauner et al. show, across RAPL and the NVIDIA Management Library
counter, that update behaviour and requested sampling frequency can materially change an energy reading [15].
Our method fits GPU pulse edges in the power record and carries the resulting timing allowance into every phase
energy; whether that allowance transfers from pulses to inference is untested (Section 8).

### 2.2 Energy of LLM inference

TokenPowerBench reports prefill and decode energy and groups measurements by context length [6]; its
published method does not specify the boundary events, alignment rule, repetition protocol or validation needed
to reconstruct a phase-attribution error budget. Ruf and Detyniecki isolate prefill by generating one token and
infer decode by subtraction [12]. *The Illusion of Power Capping in LLM Decode* is phase-aware, repeats
configurations and cross-checks sampled-power integrals against the GPU's hardware energy counter [13]; our
setting has no such counter, and our narrower contribution is to carry registered phase-edge perturbations into
the calculation that decides whether a phase contrast may be reported. ML.ENERGY and Intelligence per Watt map
energy across deployed configurations [7] [14], and Benazir and Lin characterise inference on Apple silicon
without energy measurement [10]. These works answer system-selection questions; we ask whether one named
software-counter boundary can support a phase claim at all, and then how decode energy scales across models on
that boundary.

### 2.3 Memory traffic and decode

Decode on a single request is commonly described as memory-bandwidth-bound: each forward pass must read every
weight it uses, while the arithmetic per byte read is small [23] [24]. That picture predicts that decode energy
per token should follow the bytes read per token. A mixture-of-experts (MoE) model, which uses only a few of its
expert weight blocks for each token, reads far fewer bytes per token than it holds in memory, so MoE models can
separate "bytes read" from "bytes resident". Part 2 turns this picture into three rival, pre-registered lines
and tests them on held-out models (Section 6).

### 2.4 Benchmark discipline, metrology and pre-registration

JouleSort established that an energy benchmark needs a fixed workload, a comparison metric and explicit rules
for running the workload and measuring energy, and it named synchronization between meter readings and the run
as a source of error [3]. SPECpower and MLPerf Power require load-specific analyzer uncertainty, fixed ranges,
minimum measurement intervals, invalid-sample accounting, clock synchronization and controlled battery
behaviour [1] [2] [11]. We carry their reject-on-missing-evidence discipline to a consumer software counter:
missing timing evidence refuses a phase claim instead of disappearing into an average.

Georges, Buytaert and Eeckhout make repetition, warm-up, independence and uncertainty part of performance
evaluation [20]; Mytkowicz et al. show that harmless-looking experimental choices can create systematic bias
[21]. Paired minimum-detectable-effect methods let observed variability raise, but not lower, a threshold fixed
before results are seen [16]; we borrow that prospective discipline but treat timing movement over the
registered edge domain as a deterministic allocation sensitivity, never combined with random noise as if
independent. Pre-registration, the public fixing of hypotheses and analyses before data, separates confirmatory
from exploratory results [25]. Blind analysis, in which the analysts cannot see the quantity of interest until
the analysis is fixed, protects against tuning toward an expected answer [22]; Part 2 uses hidden multiplicative
offsets in the manner of that literature, and both parts withhold energies until a recorded release.

### 2.5 Split inference

Split, or disaggregated, inference runs prefill and decode on different devices. Prior work reports whole-run
or GPU-only energy for such deployments [17] [9] [8], and SplitZip makes no energy claim [18]. A phase-resolved
energy measurement with named boundaries is a prerequisite for evaluating such designs, which are outside this
paper's scope.

## 3. Method

This section defines every quantity the results print. Numbers in it are design constants or labelled
synthetic examples; none is a measurement.

### 3.1 The machine, the sampler and the measurement boundary

All measurements use one Apple M3 Max laptop (model identifier Mac15,9, 128 GB of unified memory) on its 140 W
mains adapter, dedicated to this work, with displays asleep and no other user workload. Models run in Apple's
MLX framework on the GPU. The operating-system build is recorded with every session
({{FILL: P1-ID-OS | operating-system build(s) of the primary-block sessions and of each replication session, from the identity pins and per-session records}}).

The power sampler is macOS `powermetrics`, asked for one record every 100 ms. Each **power record** states the
average power of three on-chip rails, the CPU cores, the GPU and the neural engine (ANE), over the record's own
time span, its **support**. The sampler never samples faster than requested, and in practice records arrive
somewhat more slowly ({{FILL: P1-M-RECORD-WIDTH | median record width and its range in the pre-collection probe sessions, from the registration's instrument description}}). Within a record the power is known
only as that average.

The **measurement boundary** of Part 1 is therefore the *processor package rails*: CPU plus GPU plus ANE as the
sampler reports them. It excludes memory chips, storage, fans, power conversion and the display. We never call
this quantity "wall power" or "system energy". A second, wider boundary, the power entering the laptop at its
USB-C input, is measured by an independent meter and used as a cross-check in Part 1 and as a primary boundary in
Part 2 (Section 3.9).

### 3.2 A run and its phases

A **run** is one inference request executed in its own process. Its steps are: an idle baseline, in which the
sampler records the quiet machine for a fixed number of records (576, about 75 s); **idle admission**, a set of
tests that the baseline was quiet; one untimed warm-up generation of the same request, so that the measured
request does not pay first-call costs; the **measured request**; and clean-up. One continuous sampler process,
the **sampler stream**, runs from the start of the baseline to the end of the measured request. Between runs a
**cooldown** waits until a short power reading is at most twice the previous run's baseline power with the
operating system's thermal state nominal, or until 300 s have passed.

The runtime stamps each phase edge. Prefill ends, and decode begins, at the first streamed output token. Decode
ends with the last output token.

**Phase energy by overlap.** Each power record contributes its average power multiplied by the length of the
overlap between its support and the phase. Records wholly inside the phase count in full, a record that
straddles an edge counts in proportion to its overlap, and records outside count zero. No idle power is
subtracted: the energy is **gross**. *Synthetic example:* a phase runs from 10.00 s to 10.25 s; record 1 covers
9.90–10.03 s at 20 W (overlap 0.03 s, 0.60 J); record 2 covers 10.03–10.16 s at 30 W (0.13 s, 3.90 J); record 3
covers 10.16–10.29 s at 30 W (0.09 s, 2.70 J); the phase energy is 7.20 J. Figure 1 illustrates the rule and the
effect of moving an edge.

![Figure 1. Phase split by overlap, and the energy moved when an edge moves (schematic).](figures/fig_p1_phase_split.svg)

*Figure 1. Schematic, no measured data. Three power records (grey) straddle a prefill-to-decode edge. Each
record's energy is shared between the phases in proportion to its time overlap with each. Moving the edge by a
timing bound g reassigns a slice of one record's energy (hatched) from one phase to the other; the request total
does not change. Values and widths are illustrative and not to scale.*

This rule, which we call the **held-average reconstruction**, assumes power is constant within each record. It
yields an *assigned* phase energy. It does not bound the physical energy of the phase under arbitrary power
variation inside a record; a record that straddles an edge could, physically, have spent all or none of its
energy on either side.

**Minimum record support.** A phase needs at least three records with positive overlap or the reduction refuses
it. Three allows a phase to cross two boundary records and contain one whole middle record. This is a fixed
cutoff, not a proof of adequate precision. The 42-token prefill of the decode workload lasts a few tens of
milliseconds, shorter than one record, and is registered in advance as not resolvable; it is never reported.
Historical captures on the same laptop showed the cutoff biting on short phases
({{FILL: DG-067 | historical count of short prefill phases that crossed only two records}} of
{{FILL: DG-068 | historical population size}} for a 1.5-billion-parameter model; {{FILL: DG-136 | historical count of identifiable phases for a 7-billion-parameter model}} of
{{FILL: DG-135 | its population size}} passed), which is why the prefill workload uses a 2,048-token prompt.

### 3.3 Where the edges are: calibration, clock mapping and the timing bound

Power records are stamped by the sampler; phase edges are stamped by the program that runs the model. To give
each phase its records, the two time bases must be laid on one timeline. Three bounds limit how well this is
done.

**The fiducial bound b (calibration with commanded pulses).** Before the first run of each session and after
the last, a **calibration capture** drives the GPU through 59 commanded one-second matrix-multiplication pulses
on a fixed schedule of varied gaps, chosen so that pulse edges do not repeatedly align with the sampler's
cadence. For each pulse, an estimator fits the power records with a baseline plus a rectangle whose onset and
offset may be displaced from the commanded times, and returns every displacement consistent with the records
within a fixed loss tolerance. A capture's **fiducial bound** is the largest absolute displacement over all
pulses, plus the uncertainty in placing that capture's trace on the wall clock. If the displacements of the 59
pulses were independent draws from one distribution, their maximum would exceed that distribution's 95th
percentile with probability at least 0.95 (since 1 − 0.95⁵⁹ ≥ 0.95); pulses of one capture are not independent,
so this is a design rationale, not a demonstrated coverage. The two captures form a **bracket**. A pre-registered
**calibration acceptance**, derived from earlier captures, refuses a session whose opening capture exceeds a
screen or whose two captures differ by more than an allowed drift
({{FILL: P1-M-ACCEPT | the registered acceptance constants for each block: pre-capture screen, bracket screen and drift limit, from the acceptance files named in the registrations}}). The session's **operative
timing bound** is

  b = max(opening, closing) + max(|closing − opening|, s_bracket),

where s_bracket is a fixed minimum allowance for movement between the two captures, taken from the acceptance.
*Synthetic example:* opening 40.0 ms, closing 30.0 ms, s_bracket 14.531 ms gives b = 40.0 + 14.531 =
54.531 ms.

**The clock bounds m and s.** Each run's sampler records carry whole-second wall-clock labels; the run's own
events are stamped on both the wall clock and the machine's monotonic clock (a counter that is never corrected to
civil time). A rate-aware fit retains every straight-line mapping between the clocks consistent with the
bracketed readings and the record labels. Its spread gives the run's **effective clock bound** m. The change in
wall-minus-monotonic time over the run's sampler stream is s. Automatic network time correction is disabled
during collection, and a clock step is a physical hazard that refuses the affected data (Section 4.3).

**The edge bound g and the first-kind timing bound.** Each phase edge is uncertain by up to g = b + s, and the
whole trace may shift by up to ±m. A run's **first-kind timing bound** is the largest change in its assigned
phase energy over every independent displacement of the two edges within ±g and every common shift of the trace
within ±m. Because power is never negative, assigned energy cannot rise as the start edge moves later or fall as
the end edge moves later, so the extremes lie at the four edge corners, each evaluated over the trace shift.
*Synthetic example:* b = 45.6 ms and s = 0.4 ms give g = 46 ms; with m = 2 ms, a start-edge record averaging 40 W
and an end-edge record averaging 10 W, moving the start 46 ms early and the end 46 ms late adds
0.046 × (40 + 10) = 2.30 J, and shifting both a further 2 ms early adds 0.002 × (40 − 10) = 0.06 J: the bound is
2.36 J. When a displaced edge crosses into a neighbouring record this closed form is only an approximation; the
registered quantity is the exact maximum.

The pulse calibration measures how the sampler places the edges of long, square GPU work. Inference has a
different sequence of work at the prefill-to-decode transition. Applying the pulse-derived bound to inference
edges is an assumption that this study did not test (Section 8).

### 3.4 Reported phase energy and its interval

A **reported cell** is one energy per model and phase, from that model's runs of one workload in one session:
10 **absolute repeats** (single runs) and 10 **null quads**. A **quad** is four consecutive runs in the order A,
B, B, A; in a null quad A and B are the same model and workload, so any difference between the sides comes only
from the instrument and the machine. A **unit** is what the statistics treat as one independent draw: one repeat
or one whole quad. The repeats and the quads are the two **strata**. Removing any run of a quad removes the whole
quad, so its drift cancellation is never broken. A cell needs at least five kept units in each stratum.

For a cell with n_r kept repeats (energies r) and n_b kept quads (quad means q):

1. **Mean.** m = 0.2 × mean(r) + 0.8 × mean(q). The weights are fixed by design, because 10 of the 50 runs are
   repeats and 40 are quad members; with all units kept this equals the plain mean of the 50 runs.
2. **Variance.** V = 0.04 × s_r² / n_r + 0.64 × s_q² / n_b, with sample standard deviations (divisor n − 1).
3. **Half-width.** h = t(0.975, min(n_r, n_b) − 1) × √V, using the smaller stratum's degrees of freedom.
4. **Recorded bounds.** B is the sum of three stratified averages (0.2 × repeat mean + 0.8 × quad-member mean) of
   per-run bounds: the first-kind timing bound (Section 3.3); an interpolation bound, which is identically zero
   for these interval-support records; and half the session's drift allowance (Section 3.8).
5. **Interval.** [m − h − B, m + h + B], not clamped at zero.
6. **Per-token value.** For decode, m divided by the 512 runtime-observed output tokens ("decode-phase energy per
   output token; 512 output tokens, 511 of them generated in the decode phase"); for prefill, m divided by the
   2,048 prompt tokens.

The interval covers run-to-run and quad-to-quad variation inside one session over the kept units, plus the
recorded bounds. It does not cover variation between sessions or days, nor any bias from which units were
removed. Treating consecutive units as independent is a modelling assumption, since they share slow drifts.
*Synthetic example (all units kept):* repeats with mean 10.0 J and s_r = 0.2 J, quad means with mean 10.2 J and
s_q = 0.18257 J give m = 10.16 J, √V = 0.047889 J, h = 2.262157 × 0.047889 = 0.10833 J; with B = 0.060 J the
interval is [9.9917, 10.3283] J.

### 3.5 The attribution floor

The first-kind timing bound enters each interval only through its average over the cell's runs. But every run of
a session is reduced under the same operative timing bound: if the sampler's edges sit late, they sit late in
every run, so this part of the uncertainty does not shrink when runs are averaged. We therefore print beside
each cell its **attribution floor**: the largest first-kind bound over the cell's kept runs, with the run that
attains it. It is printed and not added to the interval. Each cell carries a fixed sentence: *"Phase-edge timing
alone could move the energy assigned to this phase of a single request by up to X J. The average of that bound
over the kept runs is already inside the interval; X itself is not added. The bound says how far the assigned
energy moves when power is taken as constant within each sampler record; it is not a bound on the physical
energy of the phase."*

### 3.6 The detection floor

The **detection floor** of a model and phase is the largest difference the registered estimator allows between
runs that do the same thing; hence the smallest real difference the instrument can resolve. It has two forms.

- **Absolute form**, from the kept repeats v₁ … v_n: deviations are vᵢ − mean(v); the prediction term is
  t × s × √(1 + 1/n), with s the sample standard deviation of the deviations and t the two-sided 95% Student-t
  value at n − 1 degrees of freedom.
- **Comparative form**, from the kept null-quad differences d = (B₁ + B₂ − A₁ − A₂)/2: deviations are the d
  themselves, not re-centred; the prediction term is |mean(d)| + t × s × √(1 + 1/n).

In both, the **point floor** is max(largest |deviation|, prediction): the first term keeps the largest
displacement already observed, the second is, under an independent-normal model, a two-sided 95% prediction
amount for one further value. It is not a deterministic bound on future errors.

**Corner widening.** Each value may lie anywhere within ± its timing half-width wᵢ. For the absolute form, wᵢ is
the largest distance of the run's phase energy from its unshifted value over the timing movements of Section
3.3. For the comparative form, each phase edge is treated as shared by the quad's four runs and moved by one
common amount within ±b, and each run's remaining local clock uncertainty is added. The **corner-widened floor**
is the largest point floor over every corner of the box of values (2ⁿ corners, enumerated exactly; the program
refuses above 16 units rather than approximate). The point floor is a convex function of the values, so its
maximum over the box lies at a corner. The **operative floor** is max(point floor, corner-widened floor).

**Small-sample guard.** For fewer than ten kept units the operative floor is multiplied by
g(n) = √(9/(n − 1)) (for example 1.0607 at n = 9 and 1.5 at n = 5); the factor is undefined below five, which is
why each stratum needs five kept units.

*Synthetic example:* ten repeats with s = 0.2 J and largest deviation 0.4 J give a prediction of
2.262 × 0.2 × √1.1 = 0.4745 J, the point floor; with wᵢ = 0.05 J on every run the operative floor is 0.5730 J.
Ten null-quad differences with mean 0.04 J and s = 0.0966 J give a point floor of 0.2692 J; with a shared-edge
width of 0.30 J on every quad the operative floor is 1.0349 J.

A **model contrast** (Section 3.10) is judged against a **floor gate**: for each side, the worse of that model's
absolute and comparative operative floors for the phase, and then the larger of the two sides.

### 3.7 The dominance ratio

For each model, phase and floor form we print

  R = (corner-widened floor, unguarded) ÷ (point floor, unguarded).

R ≥ 2 (equality passes) means that letting each value move within its timing box at least doubles the floor:
timing attribution, not run-to-run repeatability, is what limits the measurement. A threshold merely above 1
would let any positive timing width decide the answer, so the registered threshold is a doubling. In the
synthetic examples above, the absolute R is 0.5730 / 0.4745 = 1.21 (fails) and the comparative R is
1.0349 / 0.2692 = 3.84 (passes).

For the comparative form we also print R_cm, a sensitivity replay in which a block-level energy allowance
derived from shared edge movements is applied with *one* sign across all quads, and each quad's own local
uncertainty with its own sign, over every sign combination. R_cm retains one shared sign for scalar energy
allowances; it does not replay one physical time shift in every quad, and passing it licenses no claim of
robustness to a common physical timing error.

Two models, two phases and two forms give eight R values and four R_cm values. They share runs and are
correlated; "independent" in the registered name of R refers to the independent-corner box, not to statistical
independence. **Branch A** holds when every one of the twelve is at least 2, and licenses the sentence that timing
attribution dominates the detection floor and the paper's contingent subtitle. Otherwise **branch B** reports each
ratio that failed. A zero denominator refuses; no infinity is ever printed. Every ratio is printed with its
numerator, denominator and n, and labelled "point diagnostic; no interval".

### 3.8 Drift: reference requests, the drift screen and the scaled sensitivity line

The instrument may read differently at the end of a session than at its start. Each session runs a fixed
**reference workload** (Qwen2.5-1.5B, a 1,024-token prompt, 256 output tokens) at fixed places: a **corpus** of
18 reference runs at the start, then a **start triplet** of three, one **midpoint reference** between the decode
and prefill halves, and an **end triplet** of three. The reference energies are never science measurements.

**Drift bound.** From the clean corpus energies (the first twelve valid corpus runs in committed order; at least
six required), with n_s surviving start references and n_e surviving end references, U_j the mean of the
corpus's j largest values and L_j the mean of its j smallest,

  bound(n_s, n_e) = max( max(U_{n_s} − L_{n_e}, U_{n_e} − L_{n_s}), t × s × √(1/n_s + 1/n_e) ).

The first term is the widest gap two means of those sizes could show if drawn from the corpus itself; the
second is a 95% repeatability bound for a difference of two means when nothing drifts.

**Drift screen.** The session passes when the absolute difference between the end-triplet and start-triplet
means is at most the bound, on gross energies and again on idle-subtracted energies. A session that fails is
excluded; one that cannot compute the screen (too few survivors) cannot count.

**Drift allowance.** A = max(bound, spread), where the spread is the largest minus the smallest of the start
mean, the midpoint energy and the end mean. Each run carries ½A into its cell's B, so a contrast, which differs
two sides, carries it once. A lost midpoint reference leaves the allowance on the start and end references only,
which cannot see an excursion that reverted before the end; this is disclosed with a fixed sentence.

**The scaled sensitivity line.** The allowance is measured on reference requests of a few tens of joules and
added, unscaled, to phases that may be much larger and longer. Whether drift transfers in proportion to energy
or duration is unmeasured. Each replication cell therefore also prints a labelled line with the allowance term
multiplied by max(1, E/E_ref, T/T_ref), where E and T are the cell's mean energy and mean phase duration and
E_ref and T_ref those of the surviving references (for a contrast, the maximum of this factor over both sides).
*Synthetic example:* an allowance term of 0.49 J, E_ref = 37.0 J, T_ref = 4.0 s and a cell of 300 J over 9.0 s
give a factor of max(1, 8.108, 2.25) = 8.108 and a scaled term of 3.97 J. The line changes no registered number.
In Part 2 the same scale is part of the registered estimator (Section 6.3), because no drift-transfer test passed
before BYTES collection.

### 3.9 The whole-machine boundary

An inline USB-C power meter (POWER-Z KM003C) sits in the cable between the 140 W adapter and the laptop and reports
bus voltage and current 50 times a second. It measures the **DC input**: what enters the laptop after the
adapter. The adapter's AC-to-DC conversion loss is not measured, so this is not wall energy. When the laptop
draws more than the adapter supplies, the battery helps; the meter cannot see that energy, so in Part 2 it is
added from the laptop's own battery current and voltage readings (Section 6.3). The meter's clock is mapped to
the laptop's monotonic clock by a fitted envelope, and its sample timing contributes its own edge term.

In Part 1 the meter is a **descriptive cross-check** that never enters a claim: for each run, the rail energy
above the run's idle baseline (ΔE_rail), the machine energy above the same baseline (ΔE_machine) and their ratio
ρ = ΔE_rail / ΔE_machine. A run is physically plausible when 0 < ρ ≤ 1 and ΔE_machine − ΔE_rail ≥ 0, since the
rails are part of the machine. Implausible runs are listed, never removed. The replication block additionally
prints whole-machine energy per phase, gross, with the rails' share per phase. In Part 2 the DC input, and the
**rest** (DC input minus rails, which includes memory, conversion losses, storage and fans), are primary
boundaries.

### 3.10 Model contrasts, outcome words and the claims ladder

A **contrast** compares two models on the same workload in **contrast quads** ordered 1.7B, 8B, 8B, 1.7B. Each
kept quad k gives d_k = (B₁ + B₂)/2 − (A₁ + A₂)/2, with B the 8B side. Over n kept quads (at least five of ten):

1. d̄ = mean(d_k); se = s_d / √n.
2. **Metrology interval**: d̄ ± t* × se, with t* the 0.975 Student-t value at n − 1 degrees of freedom rounded to
   three places. No extra error term is added for phase energies, because each run's random error is already in
   s_d.
3. **Deterministic bound D**: for each recorded bound kind, a quad's bound is the A-side mean of its two runs'
   bounds plus the B-side mean; D sums, over kinds, the mean over kept quads. The **decision interval** is the
   metrology interval widened by D on both sides. Errors common to every run (a timing bias, a drift) are carried
   by D and the attribution floor, never by the statistical interval.
4. **Test**: t = d̄ / se, two-sided. The two primary contrasts (decode and prefill) form one family corrected by
   Holm's method at α = 0.05 [26]; a contrast that cannot be estimated keeps the family size at two.
5. **Floor gate** (Section 3.6).

The outcome is one of four registered words, decided in this order of precedence:

- **not estimable**: a required input is missing or invalid;
- **not resolvable**: there is no floor, or |d̄| does not exceed the floor gate, or the decision interval
  contains zero while the metrology interval does not;
- **unresolved**: the metrology interval contains zero, or Holm's correction does not reject;
- **direction supported**: otherwise; the direction is the sign of d̄.

A **leave-one-quad-out** check recomputes the contrast without each kept quad in turn. If dropping some quad
changes the sign, the floor status, the Holm decision or the outcome, the contrast is *verdict-influential*. If it
moves d̄ by more than a quarter of the floor gate, that is reported.

Beside each contrast two **registered descriptive estimates** are printed and decide nothing: the 8B-to-1.7B
ratio of phase energies, exp(mean of ln(B-side mean / A-side mean)) with its t interval and without the recorded
bounds; and d̄ per token (÷ 512 output tokens for decode, ÷ 2,048 prompt tokens for prefill). Phase energy is
gross, and the 8B phase lasts longer, so part of any difference is baseline power times the extra duration.

**The claims ladder** caps how strong a sentence may be. **L1** (instrument result): on this exact stack and
boundary, this quantity was observed, with its interval. **L2** (comparative result): one condition differed
from another within one boundary, with intervals reported, interleaved order and the effect above the detection
floor. A contrast reaches L2 only when its outcome is *direction supported*, its direction is the registered one
(8B uses more phase energy than 1.7B), it is not verdict-influential under leave-one-quad-out, and it remained
confirmatory (no replacement or extra run was added after the fact). Otherwise it is reported in L1 wording.
Higher levels (a model checked on held-out cells, replication on other machines) are out of reach in Part 1.
The two floor packs' reported cells, collected in separate sessions in a fixed order, are printed side by side
at L1 and are never differenced into a comparison.

## 4. Experimental design

### 4.1 Models, workloads and stack

Part 1 uses two models from the same family, Qwen3-1.7B and Qwen3-8B, both quantized to 4 bits (each weight
stored in 4 bits with a scale and offset per group of weights) and published as MLX checkpoints. Model files,
tokenizer, runtime packages, kernel library, sampler and output policy are pinned by hash for every run
({{FILL: CP-X01-identity | model identities and revisions, runtime and library versions, tokenizer and chat-template digests, from the identity pins and prompt pin}}). Two workloads are registered:

- **Decode workload.** One fixed prompt of 42 tokens, rendered through the model family's chat template with
  its "thinking" mode off. Generation is greedy (the most probable token each time) and forced to exactly 512
  output tokens by suppressing the end-of-sequence token. Its decode phase is reported. Its 42-token prefill is
  registered as not resolvable and never printed.
- **Prefill workload.** One fixed prompt of exactly 2,048 tokens, with 512 output tokens. Its prefill phase is
  reported. The length was chosen in a pre-collection probe as the shortest of 512, 1,024, 2,048 and 4,096 tokens
  at which every probe run of the smaller model overlapped at least five sampler records
  ({{FILL: CP-X01-length | the selection record that fixed the 2,048-token length, with its digest}}).

The four **target cells** are decode and 2,048-token prefill for each model. The results support no statement
about other prompts, other prompt lengths, other models, other machines or another measurement boundary.

### 4.2 Packs and the shape of a session

A **pack** is a frozen, hash-pinned plan for one measurement session. Three packs are registered:

- the **1.7B floor pack** measures Qwen3-1.7B's reported cells and detection floors;
- the **8B floor pack** does the same for Qwen3-8B;
- the **contrast pack** measures the two contrasts, decode and prefill, in contrast quads.

A **session** is one unattended collection of a whole pack on the laptop, of roughly six hours, with no other
workload and no AI agent process on the machine. Its shape is fixed (Figure 2): a 60 s settle; the opening
calibration capture; the 18-run reference corpus; the start triplet; the decode half; the midpoint reference;
the prefill half; the end triplet; and the closing calibration capture. In each floor pack each half holds 10
absolute repeats followed by 10 null quads (50 runs); in the contrast pack each half holds 10 contrast quads (40
runs), with one diagnostic reference run in the middle that enters neither the drift screen nor the allowance.
Quad order in the contrast pack is fixed, 1.7B, 8B, 8B, 1.7B, and not randomized: a linear drift cancels inside
each quad, a curved drift does not.

![Figure 2. Shape of one measurement session (schematic).](figures/fig_p1_session_shape.svg)

*Figure 2. Schematic, no measured data. One session, left to right: settle, opening calibration capture,
reference corpus, start triplet, decode half, midpoint reference, prefill half, end triplet, closing capture.
The floor packs fill each half with 10 repeats and 10 null quads; the contrast pack with 10 contrast quads around
one diagnostic reference. Widths are not to scale.*

### 4.3 The primary block

The primary block (registered internally as measurement block 5) collected one analysed session of each pack.
Its registration, analysis plan, flag catalog and an inventory of the SHA-256 digest of every code and
configuration file a session reads were committed together and sealed by an independent judgment before the
first session armed. Every session ran from a separate checkout of the repository at the sealed commit.

**What refuses, and what is only recorded.** A session is *armed*, that is allowed to start, only after direct
measurements show none of the registered physical hazards: a clock step or drift beyond budget, running on battery
or charging, thermal pressure, an outside process drawing power, too little free disk, a sampler that is not
sampling, and an AI agent process alive on the machine (agent processes draw 8 to 47 W while nominally idle).
During the session a monitor measures the same hazards. Only a directly measured physical hazard refuses
collection or removes data. Every other condition is written as a **flag**, a recorded code beside the data, and
a registered catalog gives each code exactly one effect: exclude the run, exclude the session, or disclose only.
Battery assist (the battery helping the adapter at peak load) is disclosed, not excluded, because excluding it
would select runs by load; each affected cell also prints a labelled line without the assisted units. Removals
by three load-correlated codes (two thermal-pressure codes and outside-process overlap with a request) are
likewise accompanied by a labelled line computed as if those codes had not applied.

**Attempts.** An *attempt* is one try at a session. An attempt that a physical hazard stopped, or that the drift
screen or another session-level rule excluded, is kept, listed and never analysed; the pack is re-armed. Re-arming
may depend only on structure (verdicts, flag counts, unit counts), never on an energy. The attempt history of every
pack is printed with the results (Section 5.1).

### 4.4 The replication block

A single session says how much a number moves from run to run on one afternoon, and nothing about whether it
holds on another day. The replication block (registered internally as block 6) was designed before any
primary-block number was seen, so that it would be collected whatever the primary block showed. Its rules are:

- **Same experiment.** The same three packs and session shape, with no change inside a run: same models,
  workloads, prompts, token counts, idle baseline, cooldown rule and stage order. The four estimator source files
  are byte-identical to the primary block's.
- **What counts.** A session **counts** when no physical hazard stopped it and it carries no session-excluding
  condition. Those conditions are physical (a power-path change or clock step during calibration, an operative
  timing bound above a pre-set stop line, a stop for sampler loss, disk, heat, deadline or agent pauses); a
  number that would be undefined (missing calibration, too few clean references, fewer than five kept units in a
  target stratum, no science runs); wrong data (model files, runtime stack or number-bearing code differing from
  the registered ones); the drift screen; and structural failure of the collection code. Twenty-five of the
  primary block's 32 session-removing codes became flags only.
- **How many, and when it closes.** The target is 3 counting sessions per pack and the minimum 2. Sessions run in
  rotating rounds (floor packs and contrast pack in the orders 1.7B, 8B, contrast; then 8B, contrast, 1.7B; then
  contrast, 1.7B, 8B), so that slow changes of the machine spread over all packs and each pack's start time moves
  through the day. The block **closes** when every pack has 3 counting sessions or at the end of 1 November 2026,
  Pacific time, whichever is first; a pack with fewer than 3 is printed as **short**.
- **Floor pairing.** Each contrast session is judged against floors from a 1.7B and an 8B floor session: the same
  round's counting session if it exists, otherwise the next counting one, otherwise the previous one, and failing
  all of these the primary block's, labelled "floor from the primary block". Pairing depends only on which sessions
  count, never on an energy.
- **Estimators.** The primary block's four estimators, applied to each counting session separately; nothing is
  pooled across sessions.
- **The one new estimator**, a **between-session summary**: for each printed quantity, each session's value
  (the primary block's analysed session and every counting replication session), their mean and their sample
  standard deviation. No pooled interval, no test, and no claim rests on it.
- **The replication word.** A contrast is **replicated** when every counting replication session gives the same
  outcome word as the primary block's analysed session *and* the same sign of d̄; otherwise it is **not
  replicated**, and each session's word and sign are printed. If the primary contrast is not estimable, the word is
  not used. This definition was fixed before any data and is a description of agreement, not a new test.
- **The flagged-inclusive line.** Beside every registered result, a labelled line adds back the non-counting
  sessions that ran the registered experiment and can be computed, ignoring session-level exclusions. It never
  replaces the registered value and shows what the session-level rules cost.

Figure 3 shows the order of sessions in the collection period.

![Figure 3. Order of measurement sessions (schematic ledger).](figures/fig_p1_session_ledger.svg)

*Figure 3. Schematic of the registered ordering, with no outcomes. Rows are rounds of the replication block;
cells are the attempts of each pack in the registered rotation, with BYTES sessions interleaved between rounds
(Section 6.2). Which attempts counted is filled from the harvest records
({{FILL: P1-LEDGER | per-attempt verdicts (counting or not, with cause family) for every primary, replication and BYTES attempt, from the harvest verdicts and attempt histories}}).*

### 4.5 Pre-registration and changes after registration

Each registration fixes, before its first session, which data count, every estimator, every printed sentence for
each outcome, and the sizing. The primary block's files were sealed by recording their SHA-256 digests in a seal
record; a session refuses to start if any file it reads differs from the sealed bytes. The replication block's
registration passed an independent judgment and was committed before its first round began; the BYTES
registration likewise before its first session.

Errors found after registration were handled in three ways, each recorded with its date and reason. A
**prospective erratum** changes a rule before any data it governs exist. A **registered deviation** records where
the executed procedure departed from the text. A **disclosed repair** corrects analysis code found, after release,
to differ from the registered arithmetic; the repair restores the registered arithmetic and is reported with the
result. No registered arithmetic was changed after data existed
({{FILL: P1-DEV-LIST | list of every erratum, deviation and disclosed repair with its date and whether it preceded or followed the data it governs, from the seal record, the replication registration's change log and the BYTES addenda}}).

### 4.6 Blinding and release

From each block's first session until its release, no person or AI agent read a measured energy, power, phase
duration, floor, ratio, contrast, outcome word or calibration value. The collection and analysis programs wrote
these into restricted files listed in a custody map; everything released during collection was **structure**
only: verdicts, whether a session counted, flag counts by code, kept-unit counts, hazard measurements, and timing
that is not a phase duration. A unit removed by a restricted code was reported only as "removed (restricted
code)".

Before release, the analysis programs ran end to end over the real archives in a **blind dry run** that wrote out
only structure (exit codes, schema checks, refusal codes). A **release event** then tied the digests of the sealed
documents and the final harvest records together; the registered analysis ran after it, and any analysis not
registered is labelled exploratory. The replication block's numbers were released only after the replication
block had closed *and* the primary block had been released, because replication values estimate the same
quantities and reading them first would have unblinded the primary analysis in all but name. BYTES used a
stronger, two-stage blinding with hidden multiplicative offsets (Section 6.3).

{{FILL: P1-RELEASE | dates of the primary-block release event, the replication-block release and the BYTES stage-1 commitment and stage-2 release, with the digests each record ties, from the seal-record "Release event" section and the release records}}

### 4.7 Independent recomputation

Before a result was printed, the headline numbers were computed a second time from the raw power records by an
**independent recomputation**: code written to the registered definitions that shares no code with the analysis
programs. The registered agreement tolerance is that each run's phase energy agrees within 1 mJ and every printed
quantity, compared unrounded, agrees within half a unit of its last printed digit. The tolerance was set from a
non-claim rehearsal in which an independent overlap sum reproduced every phase energy far inside it, while the
defects it must catch are far larger (a 1 ms edge shift at the powers involved is tens of millijoules; a dropped
record is joules). The observed agreement is printed beside the tolerance and is never used as one. Part 2 uses
an independent **twin** implementation in the same way (Section 6.3).

{{FILL: P1-RECOMPUTE | the comparison table of the independent recomputation against the analysis for every printed Part 1 quantity: tolerance, observed largest difference, and agreement word, per block; checked by one executing reader before printing}}
