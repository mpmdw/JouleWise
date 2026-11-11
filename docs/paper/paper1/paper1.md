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

# What a Laptop's Power Counters Can Resolve: A Pre-registered, Blinded Measurement of LLM Inference Energy on Apple Silicon

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
correction, and an independent recomputation of the core arithmetic from raw power records with recorded
collection-time judgments as inputs. A registered replication in further sessions on later days was collected
and remains blinded. <!-- FACT H01: RL-5; R2P P3; LEAN-COVERAGE-AUDIT.md §§2-4; paper-audit C-11. -->
{{FILL: P1-ABS-PART1 | one or two sentences summarising Part 1, assembled from
the issued outcome fields only: the four reported cells' L1 statement with intervals (CP-X05-*), the dominance
branch (CP-X02-abstract / CP-X03-abstract), the decode and prefill contrast outcome words and, only where the
claim gate returns L2, the registered direction (CP-X08-*-abstract), and the replication word per contrast
(P1-B6-REPWORD-decode, P1-B6-REPWORD-prefill)}} In a second part, BYTES, we test whether decode energy per
token on the same laptop follows the bytes the model reads per token, its resident size in memory, or its
decode time: the registration requires three straight lines fixed on three dense models to be committed before
seven held-out models, including three mixture-of-experts models, are unblinded.
<!-- FACT H02: RL-5 item 5; paper-audit §4.2 (BYTES commitment is a requirement, not a completed step). -->
{{FILL: P1-ABS-PART2 | one sentence: the H1 verdict
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
  the measurement session (Section 4.3);
- an **attribution floor**: the largest amount by which phase-edge timing alone could move the energy assigned
  to one request's phase (Section 4.4);
- a **detection floor**: the largest energy difference the instrument produces between runs that do the same
  thing, and hence the smallest real difference it can resolve (Section 4.5);
- a **dominance ratio**: the factor by which allowing each value to move within its timing uncertainty
  enlarges the detection floor. A ratio of at least 2 means that timing attribution, not ordinary repeatability,
  limits the measurement (Section 4.6).

The registrations fixed the counting and exclusion rules, estimators and specified fixed sentences before the
data they govern. Dated errata, interpretations and analysis-code changes are disclosed in Section 5.5.
The draft's additional branch prose was written before release, at commit `a1a5029fb`, after primary collection;
the blind draft is tagged `paper1/blind-draft-2026-10-27`. Everything changed after the primary release was changed by seats that could know the primary block's result. On 10 November 2026, statements of fact about the method and several branch glosses were corrected (`CORRECTIONS-2026-11-10.md`). On 11 November 2026, the sections were reordered with their text unchanged and the contingent subtitle was removed (`OUTLINE-MAP-2026-11-11.md`), and Section 8 was rewritten from the project record. Energies stayed hidden until a recorded release;
the independent recomputation uses recorded collection-time judgments as inputs (Section 5).
<!-- FACT H03: R2P P3/P5/P7; RL-1/RL-5; LEAN-COVERAGE-AUDIT.md §4. -->

### 1.3 Contributions

1. **A phase-attribution method with explicit limits** for interval-average software power records: an overlap
   rule, timing bounds derived from in-session GPU-pulse calibration and a fitted clock mapping, a detection
   floor with timing-widened corners, an attribution floor, a dominance ratio, a drift allowance from
   reference requests with a labelled scaled sensitivity line, and a whole-machine cross-check at the laptop's
   power input (Sections 3 and 4; Appendix D).
2. **A pre-registered, blinded measurement with a collected, blinded replication**: reported phase energies for two models, two
   primary model contrasts under a multiplicity correction and a claims ladder that caps what each result may
   say, and a replication in further sessions whose agreement word was defined before replication collection (Sections 5
   and 6). The replication results remain sealed. <!-- FACT H04: paper-audit C-10/C-11; RL-5 item 5. -->
3. **BYTES, a pre-registered test of what drives decode energy per token** on the same laptop, requiring rival
   lines to be committed before held-out models are unblinded and using mixture-of-experts models to separate
   bytes read from bytes held (Section 7).
4. **An account of research run by AI agents** under human direction, with the integrity controls that
   constrained them and the failures those controls did and did not catch (Section 8).

### 1.4 What this paper does not claim

All measurements come from one laptop, one operating-system build per session, one inference framework and
one sampler. The phase split rests on the sampler's own timing; no independent instrument checked where energy
falls within a record or at a phase edge. The decode workload uses one fixed prompt, and the prefill workload
one prompt length. The whole-machine meter measures power entering the laptop after its adapter, not at the
wall. Section 9 lists these and the other limitations in full.

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
energy; whether that allowance transfers from pulses to inference is untested (Section 9).

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
and tests them on held-out models (Section 7).

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

## 3. The instrument and its two boundaries

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
Part 2 (Section 3.2).

### 3.2 The whole-machine boundary

An inline USB-C power meter (POWER-Z KM003C) sits in the cable between the 140 W adapter and the laptop and reports
bus voltage and current 50 times a second. It measures the **DC input**: what enters the laptop after the
adapter. The adapter's AC-to-DC conversion loss is not measured, so this is not wall energy. When the laptop
draws more than the adapter supplies, the battery helps; the meter cannot see that energy, so in Part 2 it is
added from the laptop's own battery current and voltage readings (Section 7.3). The meter's clock is mapped to
the laptop's monotonic clock by a fitted envelope, and its sample timing contributes its own edge term.

In Part 1 the meter is a **descriptive cross-check** that never enters a claim: for each run, the rail energy
above the run's idle baseline (ΔE_rail), the machine energy above the same baseline (ΔE_machine) and their ratio
ρ = ΔE_rail / ΔE_machine. A run is physically plausible when 0 < ρ ≤ 1 and ΔE_machine − ΔE_rail ≥ 0, since the
rails are part of the machine. Implausible runs are listed, never removed. The replication block additionally
prints whole-machine energy per phase, gross, with the rails' share per phase. In Part 2 the DC input, and the
**rest** (DC input minus rails, which includes memory, conversion losses, storage and fans), are primary
boundaries.

### 3.3 The known-bytes stream test

Whether the GPU rail includes the energy of the memory controller decides how the rails-versus-rest split of
memory energy should be read. A registered **known-bytes stream test**, a GPU workload streaming a known number of
bytes, was scheduled after pass-1 collection and before stage-1 unblinding, from its own non-claim checkout.

**[BRANCH 6.6.1 — the test ran and the rail responded as registered]** {{FILL: P1-BY-KB | outcome of the known-bytes stream test with its record}} The rail and rest boundaries are read as registered.
**[END BRANCH 6.6.1]**

**[BRANCH 6.6.2 — the test ran and a boundary did not respond as registered]** {{FILL: P1-BY-KB | outcome}} That
outcome is printed beside every claim line of the boundary concerned. **[END BRANCH 6.6.2]**

**[BRANCH 6.6.3 — the test did not run]** The test did not run in its slot; the split of memory energy between rails
and rest is reported as not measured, and every rails and rest statement carries that caveat. **[END BRANCH 6.6.3]**

### 3.4 Whole-machine cross-check

**Whole-machine cross-check.** {{FILL: P1-B5-METER | per pack and model: median, range and interquartile range of the rails' share ρ; member windows outside the hard plausibility band, each listed with its meter flags; within-model spread; the central band from the first clean session and the count of later member windows inside it; or "no clean session, no central band"}} The boundary of this
cross-check is the DC input at the laptop's USB-C port plus the battery term; the adapter's AC-to-DC loss is not
included. It is never a claim number and removed nothing.

## 4. Phase attribution with explicit limits

This section defines every quantity the results print. Numbers in it are design constants or labelled
synthetic examples; none is a measurement.

### 4.1 A run and its phases (examples in Appendix D.1)

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
subtracted: the energy is **gross**.

![Figure 1. Phase split by overlap, and the energy moved when an edge moves (schematic).](figures/fig_p1_phase_split.svg)

*Figure 1. Schematic, no measured data. Five power records (grey); record 3 straddles the prefill-to-decode edge. Each
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

### 4.2 Where the edges are: calibration, clock mapping and the timing bound (details in Appendix D.2)

Power records are stamped by the sampler; phase edges are stamped by the program that runs the model. To give
each phase its records, the two time bases must be laid on one timeline. Three bounds limit how well this is
done.

**The fiducial bound b (calibration with commanded pulses).** Before the first run of each session and after
the last, a **calibration capture** drives the GPU through 59 commanded one-second matrix-multiplication pulses
on a fixed schedule of varied gaps, chosen so that pulse edges do not repeatedly align with the sampler's
cadence.

The two captures form a **bracket**. A pre-registered
**calibration acceptance**, derived from earlier captures, refuses a session whose opening capture exceeds a
screen or whose two captures differ by more than an allowed drift
({{FILL: P1-M-ACCEPT | the registered acceptance constants for each block: pre-capture screen, bracket screen and drift limit, from the acceptance files named in the registrations}}). The session's **operative
timing bound** is

  b = max(opening, closing) + max(|closing − opening|, s_bracket),

where s_bracket is a fixed minimum allowance for movement between the two captures, taken from the acceptance.

**The clock bounds m and s.** Each run's sampler records carry whole-second wall-clock labels; the run's own
events are stamped on both the wall clock and the machine's monotonic clock (a counter that is never corrected to
civil time). A rate-aware fit retains every straight-line mapping between the clocks consistent with the
bracketed readings and the record labels. Its spread gives the run's **effective clock bound** m. The change in
wall-minus-monotonic time over the run's sampler stream is s. Automatic network time correction is disabled
during collection, and a clock step is a physical hazard that refuses the affected data (Section 5.3).

**The edge bound g and the first-kind timing bound.** Each phase edge is uncertain by up to g = b + s, and the
whole trace may shift by up to ±m. A run's **first-kind timing bound** is the largest change in its assigned
phase energy over every independent displacement of the two edges within ±g and every common shift of the trace
within ±m.

The pulse calibration measures how the sampler places the edges of long, square GPU work. Inference has a
different sequence of work at the prefill-to-decode transition. Applying the pulse-derived bound to inference
edges is an assumption that this study did not test (Section 9).

### 4.3 Reported phase energy and its interval (derivation in Appendix D.3)

A **reported cell** is one energy per model and phase, from that model's runs of one workload in one session:
10 **absolute repeats** (single runs) and 10 **null quads**. A **quad** is four consecutive runs in the order A,
B, B, A; in a null quad A and B are the same model and workload, so any difference between the sides comes only
from the instrument and the machine. A **unit** is what the statistics treat as one independent draw: one repeat
or one whole quad. The repeats and the quads are the two **strata**. Removing any run of a quad removes the whole
quad, so its drift cancellation is never broken. A cell needs at least five kept units in each stratum.

The interval covers run-to-run and quad-to-quad variation inside one session over the kept units, plus the
recorded bounds. It does not cover variation between sessions or days, nor any bias from which units were
removed. Treating consecutive units as independent is a modelling assumption, since they share slow drifts.

### 4.4 The attribution floor

The first-kind timing bound enters each interval only through its average over the cell's runs. But every run of
a session is reduced under the same operative timing bound: if the sampler's edges sit late, they sit late in
every run, so this part of the uncertainty does not shrink when runs are averaged. We therefore print beside
each cell its **attribution floor**: the largest first-kind bound over the cell's kept runs, with the run that
attains it. It is printed and not added to the interval. Each cell carries a fixed sentence: *"Phase-edge timing
alone could move the energy assigned to this phase of a single request by up to X J. The average of that bound
over the kept runs is already inside the interval; X itself is not added. The bound says how far the assigned
energy moves when power is taken as constant within each sampler record; it is not a bound on the physical
energy of the phase."*

### 4.5 The detection floor (derivation in Appendix D.4)

The **detection floor** of a model and phase is the largest difference the registered estimator allows between
runs that do the same thing; hence the smallest real difference the instrument can resolve. It has two forms.

A **model contrast** (Section 4.8) is judged against a **floor gate**. Each form first adds the floor session's
whole gross drift allowance to its guarded operative floor, giving `drift_widened_guarded_floor_j`.
For each model and phase, `floor_abs_j` and `floor_cmp_j` are those two drift-widened values, and the cell's
`floor_gate_j` is their maximum; the contrast uses the larger gate of its two sides. The allowance is added
after the guard, once per form. It does not enter the point or corner-widened diagnostics, the dominance ratios,
or the attribution floor. Each floor is disclosed with the guarded operative value, the allowance and its source,
and the resulting minted floor. The contrast's decision interval separately carries the contrast session's
allowance (Section 4.7). The blind ruling of 12 October corrected the analysis plan's contrary description
without changing the code (Section 5.5).
<!-- FACT H05: RUN_STATE item 33(b); l9-rulings/RULING.md:117-136 (J5); detection_floor.py:1534-1536,1818-1838. -->

### 4.6 The dominance ratio (replay and branch rules in Appendix D.5)

For each model, phase and floor form we print

  R = (corner-widened floor, unguarded) ÷ (point floor, unguarded).

R ≥ 2 (equality passes) means that letting each value move within its timing box at least doubles the floor:
timing attribution, not run-to-run repeatability, is what limits the measurement. A threshold merely above 1
would let any positive timing width decide the answer, so the registered threshold is a doubling.

The attribution floor of Section 4.4, the detection-floor class `attribution_limited` under D-078, and the
dominance branch are separate quantities. A floor-class label alone does not select the dominance branch.
<!-- FACT H06: paper-audit C-2/F-10; RL-4(viii); D-078 and D-165. -->

### 4.7 Drift: reference requests and the drift screen (bound and sensitivity line in Appendix D.6)

The instrument may read differently at the end of a session than at its start. Each session runs a fixed
**reference workload** (Qwen2.5-1.5B, a 1,024-token prompt, 256 output tokens) at fixed places: a **corpus** of
18 reference runs at the start, then a **start triplet** of three, one **midpoint reference** between the decode
and prefill halves, and an **end triplet** of three. The reference energies are never science measurements.

**Drift screen.** The session passes when the absolute difference between the end-triplet and start-triplet
means is at most the bound, on gross energies and again on idle-subtracted energies. A session that fails is
excluded; one that cannot compute the screen (too few survivors) cannot count.

**Drift allowance.** A = max(bound, spread), where the spread is the largest minus the smallest of the start
mean, the midpoint energy and the end mean. Each run carries ½A into its cell's B, so a contrast, which differs
two sides, carries it once. A lost midpoint reference leaves the allowance on the start and end references only,
which cannot see an excursion that reverted before the end; this is disclosed with a fixed sentence.

### 4.8 Model contrasts, outcome words and the claims ladder (descriptive checks in Appendix D.7)

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
5. **Floor gate** (Section 4.5).

The outcome is one of four registered words, decided in this order of precedence:

- **not estimable**: a required input is missing or invalid;
- **not resolvable**: there is no floor, or |d̄| does not exceed the floor gate, or the decision interval
  contains zero while the metrology interval does not;
- **unresolved**: the metrology interval contains zero, or Holm's correction does not reject;
- **direction supported**: otherwise; the direction is the sign of d̄.

**The claims ladder** caps how strong a sentence may be. **L1** (instrument result): on this exact stack and
boundary, this quantity was observed, with its interval. **L2** (comparative result): one condition differed
from another within one boundary, with intervals reported, interleaved order and the effect above the detection
floor. A contrast reaches L2 only when its outcome is *direction supported*, its direction is the registered one
(8B uses more phase energy than 1.7B), it is not verdict-influential under leave-one-quad-out, and it remained
confirmatory (no replacement or extra run was added after the fact). Otherwise it is reported in L1 wording.
Higher levels (a model checked on held-out cells, replication on other machines) are out of reach in Part 1.
The two floor packs' reported cells, collected in separate sessions in a fixed order, are printed side by side
at L1 and are never differenced into a comparison.

## 5. Registered design, blinding, release and recomputation

### 5.1 Models, workloads and stack

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

### 5.2 Packs and the shape of a session

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

### 5.3 The primary block

The primary block (registered internally as measurement block 5) collected one analysed session of each pack.
Its registration, analysis plan, flag catalog and an inventory of the SHA-256 digest of every code and
configuration file a session reads were committed together and sealed by an independent judgment before the
first session armed. There were two seals: prospective Erratum 1 required a second seal; Errata 2 and 3 later
governed only the attempts to which they applied. Every session ran from a separate checkout at its governing
sealed commit and applicable pins. The seal and erratum history is part of the change disclosure (Section 5.5).
<!-- FACT H07: SEAL_RECORD.md (docs/process_traces/2026-10-07-block5-seal/), Erratum 1 and Addenda 3-4; RL-5 item 2. -->

**What refuses, and what is only recorded.** A session is *armed*, that is allowed to start, only after direct
measurements show none of the registered physical hazards: a clock step or drift beyond budget, running on battery
or charging, thermal pressure, an outside process drawing power, too little free disk, a sampler that is not
sampling, and an AI agent process alive on the machine (an agent process draws {{FILL: P1-AUTO-AGENTPOWER | range of processor power drawn by an idle AI agent process, from the replication registration's hazard definition}} while nominally idle).
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
pack is printed with the results (Section 6.1).

### 5.4 The replication block

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
  not used. This definition was fixed before replication collection and is a description of agreement, not a new test.
- **The flagged-inclusive line.** Beside every registered result, a labelled line adds back the non-counting
  sessions that ran the registered experiment and can be computed, ignoring session-level exclusions. It never
  replaces the registered value and shows what the session-level rules cost.

Figure 3 shows the order of sessions in the collection period.

Collection closed on 21 October 2026 with three counting sessions per pack, nine in total. These are collection
facts; the replication's numerical results remain sealed, and Section 6.8 remains an unfilled template.
<!-- FACT H08: paper-audit §4.2 (replication close), C-11; RL-6(e), DLE-10. -->

![Figure 3. Order of measurement sessions (schematic ledger).](figures/fig_p1_session_ledger.svg)

*Figure 3. Schematic of the registered ordering, with no outcomes. Rows are rounds of the replication block;
cells are the attempts of each pack in the registered rotation, with BYTES sessions interleaved between rounds
(Section 7.2). Which attempts counted is filled from the harvest records
({{FILL: P1-LEDGER | per-attempt verdicts (counting or not, with cause family) for every primary, replication and BYTES attempt, from the harvest verdicts and attempt histories}}).*

### 5.5 Pre-registration and changes after registration

Each registration fixes, before its first session, which data count, the estimators, specified fixed sentences
for the outcomes, and the sizing. The primary block's files were sealed by recording their SHA-256 digests in a
seal record. At arm, the identity check refuses an OS-build or machine-model mismatch. An executed-code difference
is detected at harvest as `code.executed_differs_from_sealed` and excludes the session; changed seal documents
cause a harvest fault. The replication block's
registration passed an independent judgment and was committed before its first round began; the BYTES
registration likewise before its first session.

Errors found after registration were handled in three ways, each recorded with its date and reason. A
**prospective erratum** changes a rule before any data it governs exist. A **registered deviation** records where
the executed procedure departed from the text. A **disclosed repair** corrects analysis code found, after release,
to differ from the registered arithmetic; the repair restores the registered arithmetic and is reported with the
result. Keeping the registered estimator definitions did not mean that the analysis program or its reporting
rules stayed unchanged after collection. The primary block's history includes:

- two seals and three prospective errata, with attempt-specific applicability;
- the blind L9 rulings J1-J8, their erratum and roster ruling, and the later L9 addendum; in particular J5
  corrected the plan's statement about the floor session's drift allowance;
- D-188's result-equivalent analysis engineering, D-189's non-stopping claim-side-bound non-issuance, and
  D-190's handling of registered nulls in the disclosures;
- analysis versions r1 through r4 and DLE-0 through DLE-5: replacement of the Results cold gate by recompute
  agreement (0), verification of the pre-release dry-run outputs at release (1), the later-block production-path
  change and its coverage conditions (2), r3's disclosure-key correction and blind post-collection D5b
  reason-mapping correction plus the documented engineering and comparison changes (3), r4's campaign-log
  member-parse correction in the floor binder (4), and the comparator's floor-leaf coverage correction (5);
- the later reporting entries DLE-6 through DLE-10: the pre-print reader gate, placement, the phase-attribution
  limitation, fixed-sentence reporting, and printing the primary block while replication remains sealed.

The D5b correction followed a permitted structural read of floor-resolution status and reason words; it was not
a prospective change made before collection. These are changes to implementation, interpretation or reporting,
and cannot be hidden by saying that the estimators were unchanged.
<!-- FACT H09: R2P P6/P7/P8; RL-5 items 1-2; SEAL_RECORD.md; l9-rulings/RULING.md J5;
L9-RULING-ADDENDUM.md; decision_log.md D-188-D-190; docs/analysis/b5/DEVIATION-LOG.md DLE-0-DLE-10. -->
({{FILL: P1-DEV-LIST | dated list of every erratum, deviation, interpretation and disclosed repair with applicability and blind status: primary-block SEAL_RECORD.md (two seals, three prospective errata), L9 rulings and addenda including the 2026-10-12 J5 floor-drift correction, docs/analysis/b5/DEVIATION-LOG.md DLE-0 through DLE-10, docs/decision_log.md D-188 through D-190, replication §17 and BYTES addenda}}).

### 5.6 Blinding and release

From each block's first session until its release, no person or AI agent read a measured energy, power, phase
duration, floor, ratio, contrast, outcome word or calibration value. The collection and analysis programs wrote
these into restricted files listed in a custody map; everything released during collection was **structure**
only: verdicts, whether a session counted, flag counts by code, kept-unit counts, hazard measurements, and timing
that is not a phase duration. A unit removed by a restricted code was reported only as "removed (restricted
code)".

Before the primary release, GAMMA floor-resolution status and reason words were read under a structural ruling;
the D5b reason-mapping correction was ruled after that read. This was a disclosed exception to the restriction
on reading analysis status, not a reading of measured values (Section 5.5).
<!-- FACT H10: R2P Decision 10(i), P8; DEVIATION-LOG.md:228-236,252-278; paper-audit C-9. -->

Before the primary release, the analysis programs ran end to end over the real archives in a **blind dry run**:
numerical outputs stayed in custody and only structure (exit codes, schema checks, refusal codes) was exposed.
A **release event** tied the digests of the sealed documents and final harvest records together. Under DLE-1,
the primary numbers designated for printing are the dry run's L9 outputs, produced before the event and verified
byte for byte at release, rather than outputs of a new post-event L9 run. Any unregistered analysis is labelled
exploratory. The replication remains blinded; its release requires closure and prior primary release, because
reading replication values first would unblind the same quantities. BYTES has a stronger, two-stage blinding
with hidden multiplicative offsets (Section 7.3).
<!-- FACT H11: R2P P2; DEVIATION-LOG.md:71-128 (DLE-1); paper-audit C-5/C-11. -->

{{FILL: P1-RELEASE | dates of the primary-block release event, the replication-block release and the BYTES stage-1 commitment and stage-2 release, with the digests each record ties, from the seal-record "Release event" section and the release records}}

### 5.7 Independent recomputation

The primary block's **independent recomputation** checks core arithmetic from raw power records using separate
code written to the registered definitions. Recorded selection, clock-anchor inputs, pulse-calibration fits,
hazard flags, clean reference membership and the drift-screen decision remain inputs. Reapplying exclusions to
stored flags is not an independent detection of the hazards that produced those flags.

Seven disclosure families are not fully recomputed: monitor cost and probe census; arm/host and anchor summaries;
battery phase/subject summaries and discharged energies; stage battery temperatures; full reference/corpus
history and the complete drift screen; all-attempt history, yield and G10 derivation; and selection and full
eligibility adjudication. Other computed items, including the load-correlated sensitivity line, lack a numerical
comparison. A separate reader check against named sources is required before uncovered quantities can be
printed; recompute agreement alone does not establish them.

For Block 5 the bars were **fixed blind before release**, by the lead's ruling adopted in DLE-0, and are specified
per family in `configs/analysis/b5/recompute_bars.json`. Joule, watt and ordinary ratio families use
max(10⁻⁶ absolute, 10⁻⁶ × |L9 value|); p values and the rail/machine ratio ρ use 10⁻⁶ absolute only; the operative
timing bound uses 10⁻⁶ relative only. Counts and integer-nanosecond window edges are exact; legacy wall-placed
meter edges use 10⁻⁶ s absolute. Where a family specifies printed decimals, half a unit of that precision also
enters the maximum. Block 6's separate S-13 rule is 1 mJ for run phase energies and half a last printed digit
for printed quantities; it is not Block 5's bar set. The observed differences and comparison coverage must be
printed beside the applicable bars, never used to choose them. Part 2 uses an independent **twin** (Section 7.3).
<!-- FACT H12: R2P P1/P3; RUN_STATE item 83 ruling 1; recompute_bars.json; DEVIATION-LOG.md DLE-0/DLE-6;
LEAN-COVERAGE-AUDIT.md §§2-4. No agreement or completion verdict is asserted here. -->

{{FILL: P1-RECOMPUTE | per block and compared family: applicable bar, number compared, observed largest difference and agreement word; name uncovered quantities and their separate reader checks; Block 5 uses recompute_bars.json fixed blind under DLE-0, Block 6 uses §12.3; checked by one executing reader before printing}}

## 6. Results I, instrument validation: phase energy, floors and contrasts

<!-- TEMPLATE. Every value below is a placeholder. Fill only from the issued artifacts named in
fill_index.md, after the release event of the block concerned. Keep one branch of each group. -->

Every phase energy in this section rests on sampler timing; phase attribution was not checked by an independent
measuring instrument (Section 9). Every number is conditional on sessions that passed the registered
physical-hazard checks at arm and kept at least five of ten units per stratum after the registered exclusions;
the kept units of each cell are printed beside it.

### 6.1 What was collected

{{FILL: P1-B5-ATTEMPTS | attempt history of each primary-block pack: number of attempts, each with its verdict and cause family, and "collected X of Y planned runs"; the three superseded first-seal attempts listed separately as inputs to no number; from the harvest records and analysis-plan disclosure producer}}

The analysed sessions were {{FILL: P1-B5-ANALYSED | identifiers and dates of the analysed attempt of each pack}}.
Table 1 lists, for each target cell, the kept units and the removed units with the catalog family of the codes
that removed them and their positions in the session, so that a reader can see whether removals clustered.

| Cell | Kept repeats n_r | Kept quads n_b | Removed units (family, position) |
|---|---|---|---|
| 1.7B decode | {{FILL: P1-B5-NR-1p7B-decode \| kept repeats}} | {{FILL: P1-B5-NB-1p7B-decode \| kept null quads}} | {{FILL: P1-B5-RM-1p7B-decode \| removed units}} |
| 1.7B prefill (2,048) | {{FILL: P1-B5-NR-1p7B-prefill \| kept repeats}} | {{FILL: P1-B5-NB-1p7B-prefill \| kept null quads}} | {{FILL: P1-B5-RM-1p7B-prefill \| removed units}} |
| 8B decode | {{FILL: P1-B5-NR-8B-decode \| kept repeats}} | {{FILL: P1-B5-NB-8B-decode \| kept null quads}} | {{FILL: P1-B5-RM-8B-decode \| removed units}} |
| 8B prefill (2,048) | {{FILL: P1-B5-NR-8B-prefill \| kept repeats}} | {{FILL: P1-B5-NB-8B-prefill \| kept null quads}} | {{FILL: P1-B5-RM-8B-prefill \| removed units}} |
| Contrast, decode | — | {{FILL: P1-B5-NQ-decode \| kept contrast quads}} | {{FILL: P1-B5-RM-ctr-decode \| removed quads}} |
| Contrast, prefill (2,048) | — | {{FILL: P1-B5-NQ-prefill \| kept contrast quads}} | {{FILL: P1-B5-RM-ctr-prefill \| removed quads}} |

*Table 1. Kept and removed units per target cell in the primary block.*

**[BRANCH 5.1.a — a pack ended without a claim-usable session]** The {{FILL: P1-B5-NOPACK | name of each pack with no claim-usable session}} pack ended with no session that the registered rules allow to be analysed;
its cells and any contrast that depends on it are printed as unavailable with the reason
{{FILL: P1-B5-NOPACK-REASON | registered refusal or end-state reason}}. **[END BRANCH 5.1]**

{{FILL: P1-B5-HAZARDS | per session: hazard measurements at arm (naming any hazard whose probe returned no reading), counts of each physics-in-span code, battery-assist counts, and the battery-temperature rise per stage, from the disclosure producer}}

### 6.2 Reported phase energies

| Model | Phase | Mean energy (J) | Interval (J) | Per token (J/token) | Attribution floor (J) |
|---|---|---|---|---|---|
| Qwen3-1.7B | decode | {{FILL: E_1p7B_decode_J_per_request \| mean}} | [{{FILL: E_1p7B_decode_lower_J \| lower}}, {{FILL: E_1p7B_decode_upper_J \| upper}}] | {{FILL: E_1p7B_decode_J_per_token \| per output token}} | {{FILL: P1-B5-AF-1p7B-decode \| attribution floor}} |
| Qwen3-1.7B | prefill (2,048) | {{FILL: E_1p7B_prefill_p2048_J_per_request \| mean}} | [{{FILL: E_1p7B_prefill_p2048_lower_J \| lower}}, {{FILL: E_1p7B_prefill_p2048_upper_J \| upper}}] | {{FILL: E_1p7B_prefill_p2048_J_per_token \| per prompt token}} | {{FILL: P1-B5-AF-1p7B-prefill \| attribution floor}} |
| Qwen3-8B | decode | {{FILL: E_8B_decode_J_per_request \| mean}} | [{{FILL: E_8B_decode_lower_J \| lower}}, {{FILL: E_8B_decode_upper_J \| upper}}] | {{FILL: E_8B_decode_J_per_token \| per output token}} | {{FILL: P1-B5-AF-8B-decode \| attribution floor}} |
| Qwen3-8B | prefill (2,048) | {{FILL: E_8B_prefill_p2048_J_per_request \| mean}} | [{{FILL: E_8B_prefill_p2048_lower_J \| lower}}, {{FILL: E_8B_prefill_p2048_upper_J \| upper}}] | {{FILL: E_8B_prefill_p2048_J_per_token \| per prompt token}} | {{FILL: P1-B5-AF-8B-prefill \| attribution floor}} |

*Table 2. Reported gross phase energy per request on the processor-rail boundary (CPU + GPU + ANE as reported by
`powermetrics`), primary block. Interval = m ± (h + B) (Section 4.3). The attribution floor is printed beside the
cell and is not added to the interval. Decode per-token values divide by the 512 runtime-observed output tokens,
511 of them generated in the decode phase. The two models were measured in separate sessions in a fixed order;
their difference is not a comparison. The 42-token prefill of the decode workload is shorter than one power record
and, as registered, is not reported.*

Each row of Table 2 carries the fixed attribution-floor sentence of Section 4.4 with its own value of X, and the
interval's three components: h, and the average first-kind timing bound, interpolation bound and drift term that
make up B ({{FILL: P1-B5-INTERVAL-PARTS | per cell: h, B and its three kind averages, and the run attaining the attribution floor with the smallest first-kind bound over kept runs}}). As an **exploratory**, unregistered diagnostic, the share of each interval taken by B rather
than h is {{FILL: P1-B5-B-SHARE | per cell, B ÷ (h + B), derived from the same record}}.
<!-- FACT H13: R2P P9; RL-5 item 6; analysis_plan_block5.md:771-772. -->

Labelled lines printed beside each cell, none of which replaces it:

- *Without battery-assisted units:* {{FILL: P1-B5-BATT-LINE | per cell: mean and interval over units with no assisted run, with n_r, n_b and the count of assisted runs per stratum; "below the registered minimum of 5 units" where applicable}}
- *Load-correlated exclusions not applied:* {{FILL: P1-B5-LOAD-LINE | per cell where any unit was removed by a thermal-pressure or outside-process code: the same estimator with those units restored, with n_r and n_b; or "no such removal"}}

**[BRANCH 5.2.a — a target cell could not be computed]** The {{FILL: P1-B5-CELL-REFUSED | model and phase of each refused cell}} cell was not computed: {{FILL: P1-B5-CELL-REFUSED-REASON | registered refusal code and its plain-language reason}}. It is printed as unavailable; it is neither zero nor evidence about the phase's energy. **[END BRANCH 5.2]**

### 6.3 Detection floors

| Model | Phase | Absolute floor (J) | Comparative floor (J) | Operative floor (J) | n (abs / cmp) |
|---|---|---|---|---|---|
| Qwen3-1.7B | decode | {{FILL: F_1p7B_decode_abs_J \| absolute operative floor}} | {{FILL: F_1p7B_decode_cmp_J \| comparative operative floor}} | {{FILL: F_1p7B_decode_operative_J \| larger of the two}} | {{FILL: P1-B5-FN-1p7B-decode \| n of each form}} |
| Qwen3-1.7B | prefill (2,048) | {{FILL: F_1p7B_prefill_p2048_abs_J \| absolute}} | {{FILL: F_1p7B_prefill_p2048_cmp_J \| comparative}} | {{FILL: F_1p7B_prefill_p2048_operative_J \| operative}} | {{FILL: P1-B5-FN-1p7B-prefill \| n}} |
| Qwen3-8B | decode | {{FILL: F_8B_decode_abs_J \| absolute}} | {{FILL: F_8B_decode_cmp_J \| comparative}} | {{FILL: F_8B_decode_operative_J \| operative}} | {{FILL: P1-B5-FN-8B-decode \| n}} |
| Qwen3-8B | prefill (2,048) | {{FILL: F_8B_prefill_p2048_abs_J \| absolute}} | {{FILL: F_8B_prefill_p2048_cmp_J \| comparative}} | {{FILL: F_8B_prefill_p2048_operative_J \| operative}} | {{FILL: P1-B5-FN-8B-prefill \| n}} |

*Table 3. Detection floors, primary block (Section 4.5). Each absolute and comparative value includes its
small-sample guard where n < 10, followed by the floor session's whole gross drift allowance; the operative
column is the larger of those drift-widened values. Disclose each guarded value, added allowance and allowance
source beside the minted value. A floor is a property of this machine, stack, boundary and session; it does not rank
hardware or validate absolute scale.*
<!-- FACT H14: RL-5 item 1; l9-rulings/RULING.md J5(b),(e); detection_floor.py:1818-1838. -->

### 6.4 Is the floor limited by timing attribution?

| Model | Phase | R, absolute (corner ÷ point, J) | R, comparative (corner ÷ point, J) | R_cm, comparative |
|---|---|---|---|---|
| Qwen3-1.7B | decode | {{FILL: R_1p7B_decode_abs \| ratio}} ({{FILL: TERM_B_1p7B_decode_abs_J \| corner}} ÷ {{FILL: TERM_A_1p7B_decode_abs_J \| point}}) | {{FILL: R_1p7B_decode_cmp \| ratio}} ({{FILL: TERM_B_1p7B_decode_cmp_J \| corner}} ÷ {{FILL: TERM_A_1p7B_decode_cmp_J \| point}}) | {{FILL: R_cm_1p7B_decode_cmp \| shared-sign ratio}} |
| Qwen3-1.7B | prefill (2,048) | {{FILL: R_1p7B_prefill_p2048_abs \| ratio}} ({{FILL: TERM_B_1p7B_prefill_p2048_abs_J \| corner}} ÷ {{FILL: TERM_A_1p7B_prefill_p2048_abs_J \| point}}) | {{FILL: R_1p7B_prefill_p2048_cmp \| ratio}} ({{FILL: TERM_B_1p7B_prefill_p2048_cmp_J \| corner}} ÷ {{FILL: TERM_A_1p7B_prefill_p2048_cmp_J \| point}}) | {{FILL: R_cm_1p7B_prefill_p2048_cmp \| shared-sign ratio}} |
| Qwen3-8B | decode | {{FILL: R_8B_decode_abs \| ratio}} ({{FILL: TERM_B_8B_decode_abs_J \| corner}} ÷ {{FILL: TERM_A_8B_decode_abs_J \| point}}) | {{FILL: R_8B_decode_cmp \| ratio}} ({{FILL: TERM_B_8B_decode_cmp_J \| corner}} ÷ {{FILL: TERM_A_8B_decode_cmp_J \| point}}) | {{FILL: R_cm_8B_decode_cmp \| shared-sign ratio}} |
| Qwen3-8B | prefill (2,048) | {{FILL: R_8B_prefill_p2048_abs \| ratio}} ({{FILL: TERM_B_8B_prefill_p2048_abs_J \| corner}} ÷ {{FILL: TERM_A_8B_prefill_p2048_abs_J \| point}}) | {{FILL: R_8B_prefill_p2048_cmp \| ratio}} ({{FILL: TERM_B_8B_prefill_p2048_cmp_J \| corner}} ÷ {{FILL: TERM_A_8B_prefill_p2048_cmp_J \| point}}) | {{FILL: R_cm_8B_prefill_p2048_cmp \| shared-sign ratio}} |

*Table 4. Dominance ratios, primary block, each over the kept units (n as in Table 3). Point diagnostic; no
interval. "Independent" in the registered name refers to the independent-corner box, not to statistical
independence; the twelve values share runs and are correlated. An absolute R_cm is not defined by the registered
replay.*

**[BRANCH 5.4.A — every one of the eight R and four R_cm is at least 2]** On this stack and boundary, allowing
each value to move within its registered timing uncertainty at least doubles every detection floor, in both forms,
for both models and both phases, and the shared-sign replay does not withdraw that statement. Timing attribution,
not run-to-run repeatability, is what limits these phase-energy measurements. This is a statement about the
registered timing domain under the held-average reconstruction; it does not say that physical phase energy is
uncertain by that amount, and the shared-sign replay does not establish robustness to one common physical timing
error. **[END BRANCH 5.4.A]**

**[BRANCH 5.4.B — at least one of the twelve ratios is below 2]** Timing attribution did not at least double every
detection floor. The components where it did not are {{FILL: P1-B5-DOM-FAILED | list of each ratio below 2, with model, phase, form, value, numerator and denominator}}. For these, repeatability
contributes at least as much to the floor as the registered timing movement does; the paper therefore makes no
claim that the measurement as a whole is attribution-limited, and prints no contingent subtitle. Where a ratio is
at least 2, it is reported as that component's diagnostic only. **[END BRANCH 5.4.B]**

**[BRANCH 5.4.R — a ratio refused (zero denominator or missing input)]** The ratio for {{FILL: P1-B5-DOM-REFUSED | component and refusal code}} was refused and is not printed as a number; branch A therefore does not hold. **[END BRANCH 5.4.R]**

### 6.5 The two model contrasts

| Contrast (8B − 1.7B) | n quads | d̄ (J) | Metrology interval (J) | Decision interval (J) | Floor gate (J) | Holm-adjusted p | Outcome | Claim level |
|---|---|---|---|---|---|---|---|---|
| decode | {{FILL: P1-B5-NQ-decode \| kept contrast quads}} | {{FILL: E_decode_contrast_signed_J_per_request \| signed estimate}} | {{FILL: P1-B5-CTR-decode-METRO \| metrology interval}} | [{{FILL: E_decode_contrast_lower_J \| lower}}, {{FILL: E_decode_contrast_upper_J \| upper}}] | {{FILL: F_claim_decode_armwise_max_J \| floor gate}} | {{FILL: P1-B5-CTR-decode-PADJ \| adjusted p}} | {{FILL: P1-B5-CTR-decode-OUTCOME \| outcome word}} | {{FILL: P1-B5-CTR-decode-LEVEL \| L1 or L2}} |
| prefill (2,048) | {{FILL: P1-B5-NQ-prefill \| kept contrast quads}} | {{FILL: E_prefill_p2048_contrast_signed_J_per_request \| signed estimate}} | {{FILL: P1-B5-CTR-prefill-METRO \| metrology interval}} | [{{FILL: E_prefill_p2048_contrast_lower_J \| lower}}, {{FILL: E_prefill_p2048_contrast_upper_J \| upper}}] | {{FILL: F_claim_prefill_p2048_armwise_max_J \| floor gate}} | {{FILL: P1-B5-CTR-prefill-PADJ \| adjusted p}} | {{FILL: P1-B5-CTR-prefill-OUTCOME \| outcome word}} | {{FILL: P1-B5-CTR-prefill-LEVEL \| L1 or L2}} |

*Table 5. Primary contrasts, Qwen3-8B minus Qwen3-1.7B gross phase energy per request, processor-rail boundary,
one Holm family of two at α = 0.05. Quads ran in the fixed, unrandomized order 1.7B, 8B, 8B, 1.7B; the p-values
assume the quad differences are independent once linear drift has cancelled. The floor gate comes from the
floor packs' sessions, collected separately; its transfer to the contrast session rests on the registered
assumption, quoted in Section 9, that the shared-edge treatment calibrated on floor quads applies unchanged at the
same quad timescale.*

Each contrast is reported in exactly one of the following branches. The decode and prefill contrasts select
their branches independently; write the paragraph once per contrast, substituting its phase.

**[BRANCH 5.5.1 — outcome "direction supported", direction positive (8B uses more), claim gate at L2]** On this
stack and boundary, the 8B model's {{FILL: P1-B5-CTR-PHASE | "decode" or "2,048-token prefill"}} phase used more
gross processor-rail energy per request than the 1.7B model's, by {{FILL: P1-B5-CTR-DBAR | d̄ for this contrast}} J
(decision interval {{FILL: P1-B5-CTR-DI | decision interval for this contrast}} J). The estimate exceeds the floor
gate of {{FILL: P1-B5-CTR-GATE | floor gate for this contrast}} J, both intervals exclude zero, Holm's correction
rejects, and leaving out any one quad changes none of these. This is a comparative (L2) result for this one prompt,
this prompt length and this machine. **[END BRANCH 5.5.1]**

**[BRANCH 5.5.2 — outcome "direction supported", but the claim gate stays at L1]** The contrast's outcome is
*direction supported* with d̄ = {{FILL: P1-B5-CTR-DBAR | d̄}} J, but the claim gate does not license a comparative
statement because {{FILL: P1-B5-CTR-L1-REASON | the failing L2 condition: leave-one-quad-out verdict-influential (name the quad), direction opposite to the registered one, or demotion from confirmatory}}. We
therefore report it at L1: the interval {{FILL: P1-B5-CTR-DI | decision interval}} J was observed on this stack; we
do not state that one model uses more energy in this phase than the other. **[END BRANCH 5.5.2]**

**[BRANCH 5.5.3 — outcome "unresolved"]** The estimate d̄ = {{FILL: P1-B5-CTR-DBAR | d̄}} J exceeds the floor gate,
but {{FILL: P1-B5-CTR-UNRES-REASON | "its metrology interval contains zero" or "Holm's correction does not reject (adjusted p = …)"}}. The direction of the difference is not supported at the registered error rate. This
is not evidence that the two models use equal energy in this phase. **[END BRANCH 5.5.3]**

**[BRANCH 5.5.4 — outcome "not resolvable"]** The instrument cannot resolve this contrast:
{{FILL: P1-B5-CTR-NR-REASON | registered gloss of each issued not-resolvable reason code; use the code-to-branch distinctions below; floor_artifact_invalid belongs to branch 5.5.5}}. The reason determines whether this is a limit of resolution or of applying the registered floor;
an unavailable transport does not establish that a difference is small. The registered descriptive estimates below are
printed for completeness and support no comparison. **[END BRANCH 5.5.4]**

**[BRANCH 5.5.5 — outcome "not estimable"]** The contrast could not be estimated:
{{FILL: P1-B5-CTR-NE-REASON | registered not-estimable code and its plain-language reason}}. No estimate is printed.
The Holm family keeps its size of two. A binding refusal (`floor_artifact_invalid`) is not evidence about the
instrument's resolution and is not an empirical negative result. It must never select branch 5.5.4.
**[END BRANCH 5.5.5]**
<!-- FACT H15: R2P P11; DEVIATION-LOG.md:252-278 (D5b); decision_log.md D-178/D-189;
analysis_engine/claims.py:333-382. These are code glosses, not selected outcomes. -->

The floor-related reasons must be kept distinct when selecting these branches:

| Issued reason code | Branch | Interpretation |
|---|---|---|
| `effect_not_above_floor` | 5.5.4 | The estimate does not exceed the floor gate; this is a resolution limit on this boundary. |
| `deterministic_bound_obscures_direction` | 5.5.4 | The decision interval contains zero while the metrology interval does not; the recorded bounds obscure direction. |
| `floor_transport_inapplicable` | 5.5.4 | The registered floor-transport conditions do not apply; this is not evidence that the difference is small. |
| `floor_artifact_invalid` | 5.5.5 | The floor artifact or its binding is invalid; no empirical negative result follows. |

Other issued codes retain their registered glosses and outcome branches; a generic absence of a floor must not
be substituted for the actual reason code.

**Leave-one-quad-out.** {{FILL: P1-B5-CTR-LOO | per contrast: "no single quad changes the verdict", or the verdict-influential quad; and, if raised, the fixed sentence "Leaving out quad k moves the estimate by X J, more than a quarter of the floor; the direction, the floor status and the multiplicity decision are unchanged"}}

**Decision interval against the floor.** {{FILL: P1-B5-CTR-DIFLOOR | per contrast: whether the decision interval's near end lies beyond the floor gate; if not, the fixed sentence "The estimate exceeds the floor, but its decision interval reaches below the floor"}}

**Registered descriptive estimates** (decide nothing). The 8B-to-1.7B ratio of phase energies was
{{FILL: P1-B5-RATIO-decode | decode energy ratio with its t interval, without recorded bounds}} for decode and
{{FILL: P1-B5-RATIO-prefill | prefill energy ratio with its t interval}} for 2,048-token prefill. Per token, the
difference was {{FILL: P1-B5-PERTOK-decode | d̄ ÷ 512 with both intervals ÷ 512}} J per output token and
{{FILL: P1-B5-PERTOK-prefill | d̄ ÷ 2,048 with both intervals ÷ 2,048}} J per prompt token. Phase energy is gross:
it includes the machine's baseline power over the phase, and the 8B phase lasts longer, so part of the difference
is baseline power times the extra duration. *Without quads holding battery-assisted runs:*
{{FILL: P1-B5-CTR-BATT | per contrast: d̄ and metrology interval without such quads, with n and the count of such quads}}.

### 6.6 Consistency checks beside the claims

**Across sessions within the primary block.** For each model and phase, the mean of that model's side over the
contrast session's kept quads is compared with the model's reported cell from its floor session, within their
statistical half-widths (recorded bounds not included). {{FILL: P1-B5-XWIN | per model and phase: "agree within their within-session intervals (difference Δ J)" or "differ by Δ J, more than their within-session intervals cover; the reported intervals understate between-session variation, which includes different interleaving and thermal history"}}

**Reference drift.** {{FILL: P1-B5-NEG8 | per session: drift-screen verdict on both energy families, the corpus size the deciding bound rested on and the corpus runs left out by reason, realised reference counts against the planned (3, 1, 3), each lost reference, each spare used, any lost midpoint with its fixed sentence, and the allowance; the bound's two terms printed with the other energies}}

**Monitor cost.** The hazard monitor ran on efficiency cores at background priority during collection and the
whole-machine meter's reader at ordinary priority; their processor time is disclosed and was not subtracted
({{FILL: P1-B5-MONITOR | per session: monitor and meter-reader CPU time, and the number of monitor probes that fell inside target phases}}).

### 6.7 Agreement of the independent recomputation

{{FILL: P1-RECOMPUTE-SUMMARY | one paragraph per block: compared families and counts, largest differences against that block's applicable bars (Block 5 recompute_bars.json fixed blind under DLE-0; Block 6 §12.3), uncovered quantities and separate reader checks; any disclosed repair with its date and effect}}

### 6.8 Replication

Table 6 places the primary block's value of every Part 1 quantity beside each counting replication session's
value, under the same estimators, with each session's interval, kept units and flags.

{{FILL: P1-B6-SIDEBYSIDE | Table 6: for each pack and each quantity of Sections 6.2-6.5 (reported means, per-token values, attribution floors, operative floors, dominance ratios, d̄ and energy ratios): the primary value; each counting replication session's value with interval, kept units, flags and its floor pairing (including any "floor from the primary block"); the difference Δ = (mean over counting replication sessions) − (primary value) and each session's own difference; and the between-session summary "between-session summary (n sessions): mean, standard deviation"}}

The rules for which runs and sessions enter differ between the blocks (the replication block turned most record
conditions into flags), and each block's calibration acceptance sets its own operative timing bound; both facts
are printed with the table, and for each replication session the primary block's session-removing codes it would
have triggered are listed ({{FILL: P1-B6-CARRIED | per replication session, the primary-block session-removing codes it carries as flags}}).

**Sessions collected.** {{FILL: P1-B6-COUNT | per pack: counting sessions of the 3 targeted, attempts made, and each non-counting attempt with its cause family; the word "short" for any pack with fewer than 3, and "below the commitment of 2" for any with fewer than 2}}

**The replication word.** For each contrast:

**[BRANCH 5.7.1 — "replicated"]** The {{FILL: P1-B6-REP-PHASE | "decode" or "2,048-token prefill"}} contrast
**replicated**: every one of the {{FILL: P1-B6-REP-N | number of counting replication contrast sessions}}
counting replication sessions gave the same outcome word as the primary block,
*{{FILL: P1-B6-REPWORD-WORD | the shared outcome word}}*, and the same sign of d̄. "Replicated" describes agreement
of outcome words and signs across sessions; it is not a new test and carries no new interval. Any claim level is
still that reached in each session separately. **[END BRANCH 5.7.1]**

**[BRANCH 5.7.2 — "not replicated"]** The {{FILL: P1-B6-REP-PHASE | phase}} contrast was **not replicated**. Its
sessions gave: {{FILL: P1-B6-REP-LIST | primary word and sign, then each counting replication session's word and sign (for example "supported +, supported +, unresolved +")}}. Agreement of signs alone does not make
a contrast replicated under the registered definition. **[END BRANCH 5.7.2]**

**[BRANCH 5.7.3 — the primary contrast was not estimable]** The primary contrast was not estimable, so the word
"replicated" is not used; the replication sessions gave {{FILL: P1-B6-REP-LIST | each session's word and sign}}. **[END BRANCH 5.7.3]**

**[BRANCH 5.7.4 — the contrast pack closed short]** The sentence reads "short: {{FILL: P1-B6-REP-N | k}} counting
replication sessions of the 3 targeted", and the word, whichever it is, rests on that many sessions.
**[END BRANCH 5.7.4]**

The replication words were {{FILL: P1-B6-REPWORD-decode | replication word for decode}} for decode and
{{FILL: P1-B6-REPWORD-prefill | replication word for prefill}} for prefill. Including the sessions that did not
count, the words would have been {{FILL: P1-B6-FLAGINC-WORDS | flagged-inclusive words per contrast, with the added sessions and their flags}}; these do not enter the registered word.

**Dominance across sessions.** {{FILL: P1-B6-DOM | per floor session: the four R per model; per contrast pairing: the branch sentence (A or B) once}}

**Labelled lines in the replication block** (none changes a registered number):

- *Scaled drift allowance* (Section 4.7): {{FILL: P1-B6-SCALED | per cell and contrast: the scaling factor and the interval or decision interval with the scaled allowance term; and, for each contrast, whether its outcome word would differ under the scaled term}}.
- *Single-step reconstruction diagnostic*: where a record straddles a phase edge, power inside it is taken to step once between neighbouring plateau levels at the time that reproduces the record's average, instead of being shared by time; printed as m ± h with no B, computed by the independent recomputation: {{FILL: P1-B6-STEP | per cell: m ± h under single-step reconstruction, beside the overlap value}}.
- *Whole-machine energy per phase*: {{FILL: P1-B6-WM | per floor-pack model and phase: DC-input gross energy per phase with estimator-1 arithmetic and the rails' share; flagged phases where the battery assisted; not given for the contrast pack}}, boundary "DC input at the USB-C port; the adapter's AC-to-DC loss is not included". Its exact definition is {{FILL: P1-B6-WM-DEF | the committed definition of per-phase whole-machine energy, including how the meter's clock-fit residual and alignment bound enter, from the replication registration's open slot for it}}.
- *Contention rule as registered*: the registered exclusion for outside processor work was not applied in the first round because it would have removed a large share of quiet rehearsal runs; its result is printed beside each cell: {{FILL: P1-B6-CONTENTION | per cell: estimate with the registered contention exclusion applied}}.
- *Waited runs*: {{FILL: P1-B6-WAITED | per cell: estimate without runs whose idle admission waited}}.
- *Cross-session consistency*: {{FILL: P1-B6-XSESS | per contrast session, model and phase: "agree within the statistical half-widths; timing bounds B not included" or the printed difference}}.

## 7. Results II, BYTES: what drives decode energy per token?

### 7.1 The question

During decode, each forward pass reads the weights it uses and the KV cache of earlier tokens from memory. On the
laptop of Part 1, energy per decode pass might follow (i) the **format-derived bytes read per pass**, b: the
stored sizes, including quantization scales and offsets, of every weight used per token plus the KV cache, computed
from the model files; (ii) the **resident size**, R: the bytes of all weights the model holds in memory; or (iii)
the **decode time** per pass, τ. The question, registered before any BYTES energy existed, is: *Does decode energy
per token follow the format-derived bytes the model reads per token, the resident model size, or decode time?*

The hypotheses barely differ on dense models, which read nearly every weight they hold, so their predictions on
dense models differ by only a few per cent. Mixture-of-experts models separate them: such a model uses only k of
its E expert blocks for each token and so reads far fewer bytes per token than it holds. Dense held-out models
therefore test whether a line stays straight over the range of bytes; the MoE models test which hypothesis is
right. This is said wherever dense results are printed.

"Bytes read" here is a count from the model format, never a reading of a memory-controller counter. Whether the
memory system actually moves those bytes, and whether the GPU rail includes the memory controller's energy, are
separate questions (Section 3.3).

### 7.2 Design

**Boundaries.** Each energy is measured at three boundaries: the **processor rails** of Part 1; the **DC input**,
the energy entering the laptop through its USB-C cable after the adapter, from the inline meter, plus the energy
the battery supplies when the laptop draws more than the adapter delivers; and the **rest**, DC input minus rails,
which includes the memory chips, conversion losses, storage and fans. The sampler reports no memory (DRAM) rail,
so the energy of reading memory is split: the chip's share appears in the rails, the memory chips' share only in
the rest.

**Models.** Ten 4-bit or 8-bit MLX checkpoints, pinned by revision (Table 7). The **fit set** is three dense
models, Qwen3-1.7B, Qwen3-4B and Qwen3-8B, through which the rival lines are drawn. The seven **held-out** models
are predicted from those lines: four dense (Qwen3-14B, Qwen3-32B, Llama-3.3-70B-Instruct and Qwen3-8B at 8 bits,
which has the fit-set 8B's architecture and about twice its bytes per token) and three MoE (Qwen3-30B-A3B,
Qwen3-Next-80B-A3B-Instruct and Qwen3.5-122B-A10B). Llama-3.3-70B was chosen to set the upper end of the range of
bytes per token.

| Role | Model | Experts used per token (k of E) | b (GB) | R (GB) |
|---|---|---|---|---|
| fit | Qwen3-1.7B, 4-bit | dense | 1.232 | 0.968 |
| fit | Qwen3-4B, 4-bit | dense | 2.603 | 2.263 |
| fit | Qwen3-8B, 4-bit | dense | 4.597 | 4.608 |
| held out, dense | Qwen3-14B, 4-bit | dense | 8.248 | 8.308 |
| held out, dense | Qwen3-32B, 4-bit | dense | 18.596 | 18.430 |
| held out, dense | Llama-3.3-70B-Instruct, 4-bit | dense | 39.852 | 39.688 |
| held out, dense | Qwen3-8B, 8-bit | dense | 8.381 | 8.703 |
| held out, MoE | Qwen3-30B-A3B, 4-bit | 8 of 128 | 1.938 | 17.175 |
| held out, MoE | Qwen3-Next-80B-A3B-Instruct, 4-bit | 10 of 512, plus shared experts | 2.166 | 44.844 |
| held out, MoE | Qwen3.5-122B-A10B, 4-bit | 8 of 256, plus shared experts | 5.281 | 68.691 |

*Table 7. BYTES roster. b = W + KV, the format-derived bytes per decode pass (weights used per pass, including
one embedding row, the whole output layer, k/E of the routed expert weights and any shared experts, plus the KV
cache averaged over the positions after prefill and after the last decode pass); R = all loaded weight storage.
Both are counted, not estimated, from the model files by a manifest script frozen before the first session
({{FILL: P1-BY-MANIFEST | SHA-256 of the frozen bytes manifest, from the registration}}); 1 GB = 10⁹ bytes. Layers of recurrent or state-space type
have a constant-size state. The roster spans a 32-fold range of b and a 71-fold range of R.*

**Workload.** Every run is the same request: a prompt of exactly 2,048 token ids, then exactly 512 output tokens
chosen greedily with the end-of-sequence token suppressed, after a 4-token warm-up. The runtime dispatches 512
decode forward passes in the measured request, one of which computes a token that is never returned, so all
per-pass arithmetic divides by 512 and every per-token value is labelled "512 decode forward passes, one of which
yields no returned token". Prefill energies are recorded and not analysed.

**Collection.** Each model is measured in a **floor module** of the Part 1 kind: 10 absolute repeats and 10 null
quads (50 runs). The ten models are grouped into six **sub-packs**, one session each: 1.7B with 4B; 8B with
30B-A3B (the cleanest dense and MoE pair share a session); 14B with Next-80B; 32B with 8B-8-bit; Llama-70B; and
Qwen3.5-122B. Each session also runs the shared reference workload of Section 4.7. A **pass** is one session of
every sub-pack. The target is two passes, the minimum one; pass 2 reverses the module order within each sub-pack
and the order of sub-packs. BYTES sessions were interleaved with the replication rounds (Figure 3), never
displacing them. No session could start after {{FILL: P1-BY-END | the registered BYTES collection end (no session start after this time), from the BYTES registration as last amended}}.

**What counts.** BYTES uses the replication block's flag catalog with a few disclose-only additions; any thermal
pressure above zero excludes the run. A run that is excluded, or has no usable record, removes its whole unit, and
a stratum with fewer than five kept units makes that cell unavailable. A run whose DC-input value is unavailable
leaves its rail record eligible. Battery assist during decode is disclosed, not excluded, and each affected cell
prints a labelled line without the assisted units. Beside every primary line a flagged-inclusive line restores
every unit excluded by a catalog code whose runs have a valid energy record.

![Figure 4. BYTES design: fit set, frozen rival lines, held-out predictions, two-stage unblinding (schematic).](figures/fig_p1_bytes_design.svg)

*Figure 4. Schematic, no measured data. Left: three fit-set models give three points per hypothesis, through
which a line in b, a line in R and a line in τ are drawn and committed. Right: each held-out model's measured
interval is compared with each line's prediction interval; the word is the single hypothesis whose prediction
interval overlaps, or "unresolved" (two or more) or "neither" (none). Bottom: the stages of unblinding.*

### 7.3 Analysis

**Cell estimate.** For one model, pass and boundary, over the kept units, the Part 1 estimator of Section 4.3 is
used unchanged except that the statistical half-width uses the Student-t quantile at 1 − 0.05/(2 × 21), the
Bonferroni level of the 21 primary consistency checks (Section 7.3, "Multiplicity"). The bound B combines, by
boundary:

| Term | Rails | DC input | Rest |
|---|---|---|---|
| Phase-edge timing | the run's first-kind rail timing bound | u + v | rail bound + u + v |
| Interpolation | 0 (required) | 0 | 0 |
| Drift | ½ A_rails × scale | ½ A_DC × scale | ½ A_rest × scale |

- **u, the meter edge term:** u = (P_start + P_end) × (r_max + Δt), where P_edge is the largest meter power among
  the samples adjacent to that decode edge (and any within ±r_max of it), r_max is the largest recorded excess
  latency of the meter's clock fit, and Δt is the meter's 20 ms sample interval.
- **The battery term and v.** At each meter poll (five a second) the laptop's latest published battery current
  and voltage give the battery's power into the machine, positive while discharging. Battery energy over a span is
  the mean of the polls in it times the span's length, and DC-input energy is the meter's energy plus this term.
  The laptop publishes battery readings about once a second, each averaging the second before, and a poll sees
  them up to one poll interval later, so battery energy is reported up to τ_b = 2 s plus the largest poll interval
  late, never early. The edge term v sums, at each decode edge, the absolute battery energy in the polls received
  in the following τ_b.
- **Drift and its scale.** A_β is the session's drift allowance on boundary β (Section 4.7), computed from the
  reference requests' whole-request energies on that boundary. Because the allowance is measured on reference
  requests far smaller and shorter than many BYTES decode phases, and the registered drift-transfer test did not
  establish a pass for any regime before collection, the allowance is multiplied by
  scale = max(1, E/E_ref, T/T_ref) on every boundary.

The largest u + v over a cell's kept runs is printed as its **meter attribution floor**, alongside the rail
attribution floor. A labelled secondary basis subtracts each run's own idle power times its decode duration.

**Per model.** With two computed passes, the model's energy E is the mean of the passes' m, with half-width the
mean of the passes' (h + B); h is not pooled, because B dominates and does not shrink with passes. Each pass's
value, their mean and their difference are printed. A **one-pass fallback**, fixed before any data, uses the
surviving pass, labelled *one pass*, when one pass of a model refuses or its withheld file is missing; a model with
neither pass has no point and no word. From E and the model's mean decode duration T: e = E/512 per decode pass,
τ = T/512, mean decode power P̄ = E/T and effective bandwidth BW = b × 512/T.

**H1: frozen rival lines.** For each hypothesis x ∈ {b, R, τ}, an ordinary least-squares line e = a + s·x is drawn
through the three fit-set points. Its **prediction interval** at a held-out model is the range of the predictions
of the 2³ = 8 lines through every combination of the fit points' interval endpoints. Hypothesis x is
**consistent** for a held-out model when the model's measured interval for e and x's prediction interval overlap.
The **word** per held-out model and boundary is `bytes`, `resident` or `time` when exactly one hypothesis is
consistent, `unresolved` when two or more are, and `neither` when none is. For every model and hypothesis,
ln(e_measured/e_predicted) is printed whatever the word. Over the three MoE models, the answer is **active** if the
resident line is inconsistent on all three with its prediction interval above the measurement each time,
**resident** if the bytes line is inconsistent on all three with its prediction interval below the measurement
each time, and **mixed** otherwise, with each model's misses printed. *Synthetic example (invented energies, not
measurements):* with fit-set energies of 0.030, 0.045 and 0.066 J per pass, ±0.001 J, the bytes line is
e = 0.016966 + 0.010685·b; a held-out model with b = 1.9378 GB and an invented measured e of 0.038 ± 0.001 J gets
prediction intervals of [0.036672, 0.038672] J (bytes), [0.181187, 0.197589] J (resident) and
[0.050714, 0.052714] J (time); only bytes overlaps, so the word is `bytes`.
This synthetic example uses the registration's four-decimal pilot regressors, rather than the rounded manifest
entries printed in Table 7; recomputing from that table does not reproduce every printed digit.
<!-- FACT H32: paper-audit F-22; bytes_pack_v1.md:297 at origin/lane/2026-11-07-bytes-stage1 (912cf8c3a). -->

**H2: power against bandwidth.** Over models, on each boundary and basis, ordinary least-squares fits of
P̄ = P₀ + ε·BW (simple), and P̄ = P₀ + ε·BW + ρ·(R/τ) (resident-extended, whose ε is primary); "resident adds
nothing" when ρ's interval contains zero or ρ ≤ 0. A **tier fit** uses only the six Qwen3 4-bit models, and each
other model (Llama-70B, Next-80B, Qwen3.5-122B, 8B-8-bit) is printed as a signed deviation from the tier line with
an interval that combines the fit's uncertainty and the model's own. On the rest boundary a fit adds P̄_rails as a
regressor; its variance inflation factor is printed, and no conclusion is drawn from its intercept or from λ,
which are not identified. Because errors in P̄ scale with P̄, primary intervals use HC3 heteroscedasticity-robust
standard errors [27] with Student t at n − p degrees of freedom; the ordinary errors are printed beside them. A
fit with fewer than two residual degrees of freedom is refused. In synthetic campaigns of 400 draws per simulated
world, the HC3 intervals' plain 95% coverage was at least 0.9475 in every world and fit, above a pre-set floor of
0.93.

**Meter label-offset alternative.** The meter's clock mapping labels each sample no earlier than it was
digitized, so an unmeasured constant label offset would move every model's DC-input decode window in the same
direction, a coherent error that the per-run term u budgets inside each cell but that H2's coefficient intervals do
not carry. Beside every H2 coefficient at DC input and rest a labelled alternative interval adds a term that
propagates the edge powers and battery edge terms through the fit, and every zero or sign statement at those
boundaries is printed under both intervals.

**Multiplicity.** The family is the H1 consistency checks plus the H2 intervals printed as primary, protected
familywise at 0.05 by Bonferroni within the pack: for H1, 7 held-out models × 3 hypotheses = 21 checks per
boundary; for H2, 9 primary intervals at rails and DC input and 11 at rest. The systematic term B is never widened.

**Blinding in two stages.** At harvest every science energy and power was multiplied by a secret pack factor drawn
once, uniform on [0.8, 1.25], and each model configuration's by a secret factor uniform on [0.97, 1.03], following
the hidden-offset practice of blind analysis [22]. A common factor leaves every H1 word unchanged, but the
configuration factors hide ratios only to about ±6%, while the MoE hypotheses differ by much larger factors; so,
in addition, the registration requires **held-out models' rows to stay withheld** from analysis exports until
the stage-1 commitment, and visible rows to carry no clock times, because gaps between reference runs could
reveal a withheld module's duration. The registered stages are:

1. **Blinded:** rails only, fit set and references, used to check that the analysis and its twin agree.
2. **Stage 1 (fit):** the fit set's and the references' factors are released; the fit points, the rival lines,
   their corner lines and the family sizes are computed and written to a predictions file whose SHA-256 is
   committed to the repository *before any held-out row enters the export*.
3. **Held-out agreement:** both implementations run on the real held-out rows, still blinded. A difference above
   the agreement bar is attributed before any held-out factor is released; a defect fix may restore the registered
   arithmetic but may not change it, and the committed predictions are never edited. If such a fix was needed, a
   second commitment is written and both results are printed, the first as registered.
4. **Stage 2 (held-out):** every held-out factor is released, the predictions file's hash is checked, and the H1
   words, the active-or-resident answer and every H2 fit are computed.

The required ordering is a recorded prediction commitment before held-out energies are *unblinded*, rather than
before they are measured. The commitment record remains unfilled here; this description of the requirement
does not assert that it has been satisfied.
<!-- FACT H30: paper-audit §4.2 (commitment), F-08; RL-7(a); RL-24 seat 3. -->

**Two implementations.** The analysis and an independent twin, written from the registration alone and sharing no
code with it, compute the same tables. They agree when every word, count, degree of freedom, refusal, label and
exit code matches exactly and every number matches within 1% of its cell's half-width (energies within 1% of
h + B; durations within 1 ms).

### 7.4 Extension models

Both extension models, Qwen3.8-27B (8-bit) and NVIDIA Nemotron 3.5 Super 120B-A12B, were dropped.
Nemotron had no loadable compatible build; Qwen3.8-27B was dropped under the registered rule that extension
sessions are dropped first ({{FILL: P1-BYX-STATUS | source identifiers for the two structural drop decisions only; no model quantities or results}}).
<!-- FACT H16: RL-5 item 5; paper-audit §4.2/F-18; RUN_STATE.md:902 (Qwen drop). -->

### 7.5 Results

<!-- TEMPLATE. Fill only from the stage-2 records of the registered analysis after release.
Keep one branch of each group. Extension results removed under RL-5 item 5 (H16). -->

**Collection.** {{FILL: P1-BY-SESSIONS | per sub-pack and pass: counting or not with cause; per model: pass status (two passes, one pass, no pass) and kept units per stratum and boundary}}

**Per-model quantities.** {{FILL: P1-BY-TABLE | Table 8, per model and boundary (rails, DC input, rest), primary selection, gross basis: each pass's m with interval, the pass mean and difference, e with interval, τ, P̄ with half-width, BW, b, R, the drift scale, the rail and meter attribution floors, the battery term's stratified mean and largest value and count of nonzero runs, the largest v; with the flagged-inclusive and idle-subtracted lines and, where applicable, the without-assisted line}}

**The committed lines.** {{FILL: P1-BY-LINES | the predictions file's SHA-256 and commit, the commitment date relative to the stage-2 release, and for each boundary the three fit lines (intercept, slope) with their corner-line ranges; and, if a second commitment exists, both, labelled}}

**H1 words.** Table 9 gives, for each held-out model and boundary, the word, the three prediction intervals, the
measured interval and the three log ratios.

{{FILL: P1-BY-H1-TABLE | Table 9: per held-out model and boundary: word, measured interval for e, prediction interval for each of b, R, τ, consistency, ln(e_measured/e_predicted) for each; per-pass words as description}}

The words at the processor rails were {{FILL: P1-BY-H1-WORDS-rails | list of held-out model: word, rails}}, at the
DC input {{FILL: P1-BY-H1-WORDS-dc | list, DC input}} and for the rest {{FILL: P1-BY-H1-WORDS-rest | list, rest}}. For each held-out
model and boundary, the word is interpreted by exactly one of the following:

**[BRANCH 6.5.W1 — word `bytes`]** Only the line in bytes read per pass predicts this model's decode energy per
pass within the registered uncertainty; the lines in resident size and in decode time do not. For an MoE model this
is direct evidence, on this machine and boundary, that energy follows the weights a token uses, not those the
model holds. **[END BRANCH 6.5.W1]**

**[BRANCH 6.5.W2 — word `resident`]** Only the line in resident size predicts this model's energy per pass; the
bytes and time lines do not. For an MoE model this indicates that holding unused experts in memory costs decode
energy on this machine, or that more of the model is read per token than the format-derived count implies.
**[END BRANCH 6.5.W2]**

**[BRANCH 6.5.W3 — word `time`]** Only the line in decode time predicts this model's energy per pass. Energy per
pass then tracks how long each pass takes, consistent with a roughly constant power draw across models, more
closely than it tracks either byte count. **[END BRANCH 6.5.W3]**

**[BRANCH 6.5.W4 — word `unresolved`]** Two or more lines predict this model within the registered uncertainty,
so the test cannot tell them apart for this model. For a dense model this is the expected result: dense held-out
models test linearity over the format-derived bytes range; their small rival splits do not identify the
hypothesis. **[END BRANCH 6.5.W4]**

**[BRANCH 6.5.W5 — word `neither`]** No registered line predicts this model's energy per pass. The log ratios
({{FILL: P1-BY-LOGR | for this model and boundary, ln(measured/predicted) under each line}}) say by how much and in which
direction each line misses. A `neither` is informative: it says that something other than the three registered
quantities, for example a model-specific kernel efficiency, quantization format or architecture, moves energy per
pass for this model, and the paper does not name which. **[END BRANCH 6.5.W5]**

**[BRANCH 6.5.W6 — no word: the model has no point]** The model has no word because {{FILL: P1-BY-NOWORD | both passes refused or were missing, with the reason}}. **[END BRANCH 6.5.W6]**

**Active or resident.** {{FILL: P1-BY-AR-rails | the active-or-resident answer at the rails, with each MoE model's misses}} at the rails;
{{FILL: P1-BY-AR-dc | the answer at DC input, with misses}} at the DC input.

**[BRANCH 6.5.A1 — `active`]** On all three MoE models, the resident-size line overpredicts the measured energy
per pass beyond the registered uncertainty: decode energy on this machine follows the experts a token activates,
not the experts held. **[END BRANCH 6.5.A1]**

**[BRANCH 6.5.A2 — `resident`]** On all three MoE models, the bytes line underpredicts the measured energy per pass
beyond the registered uncertainty: holding a model's full set of experts raises decode energy beyond what the
active bytes alone predict. **[END BRANCH 6.5.A2]**

**[BRANCH 6.5.A3 — `mixed`]** The three MoE models do not agree on either pattern; each model's misses are
printed, and no general statement about active versus resident bytes is made. **[END BRANCH 6.5.A3]**

**H2.** {{FILL: P1-BY-H2-TABLE | Table 10, per boundary and basis: each fit's n, p, df, status and k; ε (simple), ε and ρ (resident-extended), tier ε and ρ, with HC3 primary intervals and OLS errors; tier deviations of each non-tier model with both parts of their intervals; the rest fit with λ, ε_rest, VIF and r; leave-one-out predictions as description; at DC input and rest the label-offset alternative interval and dβ/dδ in J/GB per ms}}

The primary energy per byte of bandwidth was ε = {{FILL: P1-BY-H2-EPS-rails | resident-extended ε at rails with HC3 interval, J/GB}} at
the rails and {{FILL: P1-BY-H2-EPS-dc | resident-extended ε at DC input with HC3 interval and the label-offset alternative}} at the DC input.

**[BRANCH 6.5.H1 — "resident adds nothing" on a boundary]** On the {{FILL: P1-BY-H2-BOUNDARY | boundary or boundaries}}
boundary, ρ's interval contains zero or ρ ≤ 0: once bandwidth is accounted for, resident bytes per second add
nothing measurable to decode power. **[END BRANCH 6.5.H1]**

**[BRANCH 6.5.H2 — ρ positive and its interval excludes zero]** On the {{FILL: P1-BY-H2-BOUNDARY | boundary}} boundary,
resident bytes per second add to decode power beyond bandwidth, by ρ = {{FILL: P1-BY-H2-RHO | ρ with interval}}. **[END BRANCH 6.5.H2]**

**[BRANCH 6.5.H3 — the two intervals disagree at DC input or rest]** Under the registered interval the statement
is {{FILL: P1-BY-H2-REG | decision under the registered interval}}; under the label-offset alternative it is
{{FILL: P1-BY-H2-ALT | decision under the alternative}}. The meter's label offset has not been measured, so we
report both and choose neither. **[END BRANCH 6.5.H3]**

**[BRANCH 6.5.H4 — a fit refused]** The {{FILL: P1-BY-H2-REFUSED | fit and boundary}} fit was refused because it had
fewer than two residual degrees of freedom; it has no primary interval, and a refused tier fit refuses its
deviations. **[END BRANCH 6.5.H4]**

**One pass.** **[BRANCH 6.5.P1 — the one-pass fallback applied to any model]** {{FILL: P1-BY-ONEPASS | models labelled one pass and why}} carry the label *one pass*; H2 is also printed over the
models with two passes as a labelled sensitivity line ({{FILL: P1-BY-H2-TWOPASS | that line}}). **[END BRANCH 6.5.P1]**

**Commitment record.** {{FILL: P1-BY-COMMIT | the stage-2 record's commitment SHA-256, committed and evaluating module digests, any module-changed or not-rebuilt flags with field names; and, if a post-agreement fix produced a second commitment, both results with every differing word reported}}

**Agreement of the two implementations.** {{FILL: P1-BY-TWIN | per stage: counts of printed fields compared and of differences under and above the bar; attribution and ruling of any difference above the bar}}

## 8. Research automation: controls, and where they failed

### 8.1 How the work was done

This study was designed, implemented, collected, reviewed and drafted by AI agents working under one human
researcher. The researcher set the research direction, the methodological requirements (raw evidence kept for
every run, gross energy as the headline basis, a named measurement boundary on every number, no claim that cannot
be audited) and the process policy. The researcher was the escalation point for changes to what is measured or
claimed (registered constants, the deciding contrast, the model, the exclusion rules, results the design does
not cover and science-design forks), and from 10 November 2026 delegated research-design and paper-bound rulings
to a research-lead session (below). Coordination was a **lead** role held by interactive agent sessions, one after another and for a time two at
once (a project lead and a primary-block lead). The lead decomposed the work, assigned it,
adjudicated design questions, chose the review gate each change passed before merge and kept the project's
record. **Worker** sessions, drawn from two model families from different vendors ({{FILL: P1-AUTO-MODELS | the model families and versions used for the lead, research-lead, supervisory, implementation, review and judgment roles over the study period}}), implemented code against written specifications, reviewed each other's work, wrote
tests and drafted text. Under the gate policy of 27 October 2026, registration text that changes what is
computed, excluded or counted is checked by one executing refuter session; where a registration required a judge, cold judge sessions with no part in the work
ruled before it bound. From 10 November 2026 a single **research-lead** session's decision log has been the one
binding record for research-design and paper-bound rulings. A ruling by any other session is a proposal until
that log enters it. This section was written by a seat that log assigned.
<!-- FACT H17: R2P P4. Roles and gates: docs/process/gate_policy.md:3-6 (Ed's policy, 2026-10-27), :37-39
(one executing refuter; a judge only where a registration requires one, or where the refuter's executed result
contradicts the lead on a counting or exclusion rule), :49-60 (amendment: the lead picks the
gate for each change; a refuter only when the text changes what is computed, excluded or counted). Two leads at once: RUN_STATE item 102 (Ed to "the second laptop session joulewise-28"),
item 108 ("joulewise-28, as block-5 lead"), item 165 ("block-5 lead, M4 Air analysis box"). Cold judges: item 42
(replication registration, "cold gate by two blind judges"), item 69 (BYTES pass 1, "registration cold gate ...
blind, executing"), item 85 (BYTES pass 2, registration section 21). Research lead: item 257 (2026-11-10 20:10
PST: the research lead's decision log is "the single binding record for research-design and paper-bound
rulings"; any other ruling "is a proposal until the research lead enters it in that log"), item 252 (Ed,
2026-11-10: "def fable 5.2 should be the final say for anything paper bound"), item 256b (Ed approved E1-E6 as
the research lead recommended); RL-24 seat 9 assigns this section. Escalation list: gate_policy.md:54-57
(science-design forks; changes to what a registration computes, excludes or counts) and RUN_STATE item 181
("Escalate to Ed ... only for": registered constants, the deciding contrast, the model, the exclusion rules; a
result the design does not cover); delegation: item 257 ("have fable lead all research design work"), item
256b ("If Fable recommends them, go ahead"). -->

On the **measurement laptop**, a **headless supervisory agent** did the desk work between sessions. A launchd
watchdog evaluates a short tick every 300 s and, when a launch is safe, starts a fresh headless session. A working
activation reads the project's state file, takes the next permitted step, writes a record and exits; a short
launch that finds nothing to do can exit without a record. An agent
census on that laptop refuses an arm while any agent process is alive. What it does to a session already running
differed between collections. In the primary block an agent sighting during the chain stopped it. In the
replication and BYTES the chain paused, resumed after 600 s with no agent, and stopped once 7,200 s in total had
been spent paused. Interactive agent sessions also ran on the measurement laptop at times, and the census caught them
(Section 8.3). On the analysis laptop, agents ran blind dry runs over real custody under the user account that
holds custody, so custody was kept by rule rather than by the file system. Development and review also ran
locally; cloud machines were used for development, review, synthetic tests and continuous integration. This is a
separation of permitted activities and reading rules, not complete separation of agents from data by machine.
<!-- FACT S9-01: docs/process/MAGISTRATE_WATCHDOG.md:3 (`com.joulewise.magistrate`, "a short Python tick at load
and every 300 seconds"; "A safe tick forks a new session"). Activation pattern: RUN_STATE items 41-76 (working
activations "Magistrate activation <id> (Opus 5.5, headless, ...)" with a RECORD.md); docs/orchestration.md:141-142
("A headless relaunch that finds nothing to do writes no record"); items 51, 52 and 59 ("No record file (short
launch)"). The pause limit is cumulative: agent_pause.py:55-88. Census stops the chain in the
primary block: joulewise/b5/driver.py:1272-1276 at the primary claim head c27485347 ("POSITIVE ... the chain
stops"); no pause class at that commit. Pause in the replication and BYTES: joulewise/b6/agent_pause.py:12-13
(`PAUSE_RESUME_S = 600`, `PAUSE_LIMIT_S = 7200`; "ten clean minutes to resume, two paused hours total") and
joulewise/b5/driver.py:2599 (`PausingCensus`) at BYTES pass-2 code 2649fad54; agent_pause.py is identical in
length and constants at the replication pin f31aca19f and BYTES pass-1 pin 6731d5249; introduced at 495569dfc
(2026-10-14, "Block 6 driver: pause on agent sighting"). Arm census: driver.py:2194 at 2649fad54 ("Agent census:
the driver's first probe"). Analysis laptop: RUN_STATE item 108; registration_block5.md:4853 ("kept by rule, not
by the file system"); RL-5 item 3. -->

![Figure 5. The research pipeline (schematic).](figures/fig_p1_pipeline.svg)

*Figure 5. Schematic of the permitted activities. Agents develop and review code in cloud and local sessions,
run on the measurement laptop between sessions, and run blind processing on the analysis laptop under custody
rules. No agent process may remain alive during collection. Primary-block L9 outputs are produced in the blind
dry run and verified at release (Section 5.6); printing additionally requires the independent comparison and
separate checks of uncovered quantities (Section 5.7).*

**What armed each collection.** The record separates two questions: what performed each arm, and who held
standing authority over when to collect.

| Collection | Sessions armed by | Agent's part |
|---|---|---|
| Primary block, 8 to 12 October 2026 | An agent. Each of the 11 recorded arms was performed by a headless supervisory agent activation. | Under the block's written brief, the activation ran the pre-arm checks, sent the arm notice and installed two launchd jobs: a night job that started the session program at a calendar t0, and a dead-man job. It armed only packs that a program-read release line, set by recorded gates, released. |
| Replication, 17 to 21 October 2026 | The scheduled loop program. | An activation loaded the loop on 17 October and reloaded it after a fix the same evening. The loop then pre-checked each session, sent the arm notice, waited at least 1,800 s for the researcher's veto, checked again and started the session, until its terminal state, reached once nine sessions counted. |
| BYTES, 25 to 30 October 2026 | The scheduled loop program, under its BYTES configuration. | An activation loaded the loop for pass 1 on 25 October; another resumed it for pass 2 on 28 October. The loop armed the BYTES sessions as above until all 12 sub-packs counted. |

The loop runs every 300 s under launchd. It could also start a headless agent session at fixed desk points, and
supervisory activations held or resumed packs through the loop's own commands. Standing authority over when and
whether to run, re-run, schedule and arm measurement windows passed to the headless supervisory agent on
6 November 2026, after all three collections had closed. It covers a later study's windows on the same laptop, not
these collections.
<!-- FACT S9-02 (R-5; RL-40). Primary block: 11 arm records, docs/process_traces/2026-10-block5/{alpha-a1,alpha-a2,
alpha-a3}-arm.md and seal2-{alpha-a1,beta-a1..a6,gamma-a1}-arm.md, each headed "Magistrate activation <id> (Opus
5.5, headless)"; first alpha-a1-arm.md:3 (2026-10-08); procedure "sections 3 and 5 of
docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md" (alpha-a1-arm.md:4); jobs
seal2-alpha-a1-arm.md:64-68 (labels `com.joulewise.night`, `com.joulewise.night.deadman`; the night job runs
`scripts/run_night.py run --plan <the plan>` on a calendar; dead-man calendar); release line `B5-ARM-RELEASED`
"read by a program" (RUN_STATE.md head block) and seal2-gamma-a1-arm.md ("Why it is armed"); collection closed
2026-10-12, RUN_STATE item 31. Replication: item 44 (first `launchctl bootstrap` refused by the agent's permission
classifier; Ed emailed the command), item 45 (activation 88c501e5, "Block-6 round 1 ARMED 18:05 PDT: the
`launchctl bootstrap` of `com.joulewise.b6loop` succeeded ... The loop sends the arm notice"), item 47
(re-bootstrapped 19:22 PDT), item 59 ("9 of 9 finished sessions counting. The loop moved to DONE at 02:54 PDT"
2026-10-21). Loop arming code at the replication pin f31aca19f: joulewise/b6/loop.py:285-310 (`_precheck`;
`arm_notice` with `t0_not_before = clock + 1800`) and :510 (transition to SESSION_RUN after the NO check).
BYTES: item 70 and its pointer (RUN_STATE "THE BYTES PASS-1 LOOP IS ARMED", written 2026-10-25 by activation
f18a96e1; configs/b6/loop_bytes.json at 6731d5249); item 85 (activation
39206674, 2026-10-28: "The loop was resumed 06:21"); item 151 (2026-10-30: "All 12 sub-packs count, and the loop is
DONE"); loop.py:301-326 and :526 at 6731d5249 and at 2649fad54. Loop interval:
configs/launchd/com.joulewise.b6loop.plist.template:7 at f31aca19f (`StartInterval 300`). Wake sessions: RUN_STATE
items 52 and 59 ("Loop wake ... headless"), item 261 (`b6_loop.py tick` "can ... bootstrap a `claude -p` wake
job"). Hold and resume: item 52 ("judged wrong and resumed"). Authority: RUN_STATE item 181 (2026-11-06 about
09:10 PST: "The magistrate decides when and whether to run, re-run, schedule and arm R0, R1, W1 and the calibration
windows"); paper-audit C-7 dates the agent's ownership of arming from item 181. -->

### 8.2 Integrity controls

An agent can change a result in ways a human might not notice: by editing an analysis after seeing its output, by
choosing which runs to keep, or by perturbing the machine it measures. The controls below were designed against
these failure modes; each is mechanical, recorded, or both.

1. **Registration before data, by hash.** Every registration, analysis plan and flag catalog was committed, and
   for the primary block every code and configuration file a session reads was listed with its SHA-256 digest in
   a sealed inventory, before the sessions they govern. The arm checks OS build and machine model; harvest
   excludes a session for an executed-code difference and faults on changed seal documents. Changes after registration go only through a dated erratum, a registered
   deviation or a disclosed repair (Section 5.5).
2. **Blinding enforced by custody.** Energies and every derived quantity were written to restricted paths listed
   in a custody map; everything released during collection was structure only, and analysis code was written and
   repaired by sessions that had read no restricted value (Section 5.6). BYTES added hidden multiplicative offsets
   and requires held-out rows to stay withheld until its predictions are committed (Section 7.3). Two departures
   are disclosed: status and reason words were read before the primary release under a structural ruling
   (Section 5.6), and one held-out BYTES model's timing was read before the stage-1 commitment (Section 8.3).
3. **Physics refuses; a short registered list of other grounds excludes; everything else is recorded.** Only a
   directly measured physical hazard stops collection, and the presence of an AI agent process on the measurement
   laptop is one of those hazards: the arm refuses while one is alive, and a running session stops (primary block)
   or pauses (replication and BYTES), as Section 8.1 describes. Data are removed only on a physical hazard or on
   the registered grounds beside it: in the primary block, that a number would be wrong or could not be attributed
   to what it claims to measure; in the replication, that the number is undefined, that the data are not of the
   registered model, runtime or code, the registered drift screen, or structural failure of the collection code.
   Every other condition is a flag with one registered effect. This constrains, rather than removes, the
   discretion through which an agent could select data.
4. **Executing review of number-bearing code.** From 27 October 2026, code that can compute, select or exclude a
   published number is reviewed by two sessions from different model families, launched together and instructed
   to probe and mutate the code rather than only read it, together with a regression test and a demonstration
   that the test fails without the change.
5. **Independent recomputation and a twin.** Separate code recomputes the primary block's core arithmetic with
   recorded collection-time judgments as inputs; uncovered quantities require separate checks (Section 5.7).
   BYTES requires agreement with its independent twin (Section 7.3), against a tolerance fixed in advance.
6. **Fail-closed refusals with reasons.** In the primary block's registered analysis, a refusal at any step stops
   the steps after it. A tooling refusal is repaired blind and the step re-runs on identical bytes; a refusal that
   is a registered scientific outcome is the result and is printed as such.
7. **Pre-written outcome text.** The registrations fix specified sentences, and the claims ladder caps claim
   strength (Section 4.8). The draft's additional branch prose was written before release, at commit `a1a5029fb`
   (tag `paper1/blind-draft-2026-10-27`), after primary collection, with results as placeholders. Corrections made after release are stated in Section 1.2.
<!-- FACT H18: R2P P3/P5/P6; RL-1/RL-5; sources as H03/H09/H12. Item 3: as FACT S9-01 for the census;
exclusion grounds registration_block5.md:4469-4473 (PHYSICS and NUMBER_INTEGRITY) and
docs/registrations/block6_replication_DRAFT.md:551-559 (§8.1: P plus N, W, D, S). Item 6:
configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:174-178 ("Refusals"), softened from the blind draft's
universal no-default/no-zero wording, which seat 9 could not source. Item 4:
docs/process/gate_policy.md:1 (binding 2026-10-27) and :28-34 (rule 3: "Two executing reviews from different model
families, launched together, each told to probe and mutate"; regression test and counterfactual). -->

### 8.3 Failures and lessons

The controls did not prevent every failure. We report those that cost data or time, or could have affected a
number, with what each taught. The record runs to 10 November 2026.

- **Agents perturbed the instrument they were studying.** An AI agent process is not idle: it draws power even
  when waiting. The census caught agent processes on the measurement laptop several times, and each catch cost a
  session or held the loop ({{FILL: P1-AUTO-LOST | estimated quiet-machine hours lost to agent presence during the three collections, and the sessions affected, counted from the census refusal, stop and pause records outside custody (arm records, RUN_STATE items, harvest verdict codes); structure only}}). In the primary block, an interactive agent
  session opened at the keyboard stopped a chain 2 h 32 min after its t0, and that attempt did not count. In BYTES,
  a software update left an agent's background daemon running; the session paused for two hours, then ended, and
  did not count. In other windows on the same laptop, agent sessions alive at t0 caused refused arms with nothing
  captured. The headless supervisory
  agent's own sessions were bound by the same rule: while the loop was pre-checking, arming or collecting, an
  activation had to exit at once.
  <!-- FACT H19: RL-5 item 3; paper-audit C-7; RL-40 (the "shell guard" clause stays out: RUN_STATE item 80
  (1) says Ed installs a `~/.zshrc` guard keyed to `collection.active`, snippet in issue #589, and pipeline-audit
  CRITIQUE.md:27-35 describes its condition, but no record shows it installed or refusing anything, and seat 9
  did not inspect the home directory; the blind draft's "none corrupted a kept number" also stays out: SYNTHESIS.md:15
  calls each census hit to 27 October "a real contaminant" in an unadopted proposal and does not address kept
  numbers).
  RUN_STATE item 16 (BETA attempt 2: "A `claude` session opened at the keyboard at 13:28 PDT stopped the chain
  2 h 32 min after t0"; not claim-usable); item 78 (r1-bytes-s6-p1: `codex update` left an app-server daemon;
  "the fence paused 2 h, then ended the session"; "not counting"); items 67 and 158 (arms refused at t0 by the
  census, zero runs / "nothing captured"); item 78's next-activation pointer (RUN_STATE "(1) BYTES ...: if the loop
  is in PRECHECK, ARM_WAIT, SMOKE_* or SESSION_RUN, exit at once, quietly (a live agent on the Mac pauses the
  pre-check ...)"). -->
- **Reviews that executed code caught the defects that mattered.** The 27 October review of the October record
  found that the defects able to change a number had been found by reviewers that ran the code on realistic
  inputs, or by running the pipeline itself. Its examples: a reference run silently dropped when a file failed to read; a reference request's energy integrated over
  the wrong span; the twin implementation diverging from the analysis on compressed input. By the same review, reviews
  of documents and bookkeeping, serial re-reviews and multi-model councils on process questions added time and
  little protection ({{FILL: P1-AUTO-CATCHES | counts of review catches by review type (executing, reading-only, council) and by severity, from the pipeline audit's segments (through 27 October 2026) and the gate-policy pruning tallies in session records after it}}). Reading reviews could also repeat an error: for a later study on the same laptop,
  several model documents and cross-reviews stated that the external meter was outside the power path, and the
  researcher corrected them. Late review rounds mostly found defects in the previous round's fixes, but some were
  real, so a hard cap on rounds would have been unsafe. The project therefore kept two parallel executing reviews
  from different model families for number-bearing code, and reduced reviews of documents, records and code that
  cannot change a number to continuous integration and, for code, the change's own regression test.
  <!-- FACT S9-03: docs/process/gate_policy.md:13-21 ("What the October record showed": the #416 NEG-8
  reference-span blocker, RUN_STATE item 69; a reference silently dropped on a read failure; the twin diverging on
  compressed input, #573; late rounds; councils) and :25-34 (rules 1-3). Meter path: RUN_STATE item 210 of
  2026-11-07 (Ed, verbatim: "the usb c power meter is between the magsafe cord and the wallbrick, so it does catch
  all power"); docs/capstone/TALK-OUTLINE-v2.md H12. -->
- **Rules must be replayed on real non-claim data before they bind.** Two registered lines, written from first
  principles, proved wrong when replayed on rehearsal sessions: the primary block's drift bar, which every session
  fails by construction, because its widened difference is always at least the mean width of its two ranges; and the
  replication's exclusion for outside processor work, which would have removed a large fraction of quiet rehearsal runs
  ({{FILL: P1-AUTO-REPLAY | the replay counts for these two rules, from the replication registration's derivations}}). Both were changed in the
  replication registration's revision of 15 October 2026, after primary collection had closed and before
  replication collection began, and only for the replication and later packs. The primary block's drift bar became
  a disclosure there, and the replication decides drift by its own registered drift screen; the policy file keeps
  the bar's bytes, so the primary block's plan digests stay identical. The outside-processor exclusion became a
  flag for the replication's first round, with the registered rule's result printed as a labelled alternative.
  <!-- FACT S9-13: docs/registrations/block6_replication_DRAFT.md:32-43 (revision of 2026-10-15; "the NEG-8
  bracket decision is disclosure only (§9.5 item 7)"; the outside-processor line, S-8), :765-774 (replay of the
  registered outside-processor rule; "flag only (governs for round 1)"), :1046-1054 (§9.5 item 7: "that widened
  difference is at least the mean width of the two ranges, so the bar fails every session by construction"; "the
  policy file keeps the bar's bytes so that block 5's plan digests stay identical, packs registered after these
  three drop the bar, and drift is decided by the D1 screen's own bound"); RUN_STATE item 31 (primary collection
  closed 2026-10-12) and item 45 (replication round 1 armed 2026-10-17); item 42 (the outside-processor rule printed
  "as a labelled alternative"). Replay values are not reproduced. -->
- **An instrument assumption can be silently false.** An early clock mapping assumed that the wall clock and the
  monotonic clock advance at the same rate; that assumption could move every fitted edge in the same direction. A
  consult in August 2026 found the rate difference larger than the anchor margins and queued a rate-aware design;
  the analysis uses the rate-aware fit of Section 4.2.
  <!-- FACT S9-04: docs/decision_log.md:6222-6230 (D-099 item 2: consult of 2026-08-01; "the unmodeled controller
  wall/monotonic rate ... exceeds every margin"; "Rate-aware anchor design is a queued desk/paper item");
  paper1.md §4.2 ("A rate-aware fit retains every straight-line mapping between the clocks"). The blind draft's
  "replaced" and "voided for claim use" clauses are removed: seat 9 found no record of either event (the Sol
  review of seat 9, fix 3). -->
- **A leaked test process changes the machine.** An orphaned monitoring process that a test had left running was
  found on the quiet machine before the replication's first round, and the replication's background-load constant
  was measured only after it was gone. The supervisory watchdog now counts orphaned test processes.
  <!-- FACT S9-05: RUN_STATE item 42 (pid 43816, "an orphaned `scripts/hazard_monitor.py` that a test in the s3-cold
  lane leaked on 10-15"; the constant "measured without Spotify and an orphaned process"); item 198 ("The
  watchdog's fixture-orphan census had counted them"). The constant's value is not printed here. -->
- **A record can say GO when nothing was measured.** On a later study's night on the same laptop, the session
  program refused before measuring, because a directory it needed had been created with the wrong owner. The
  night's top-level result still read GO and its courier sent normally, so nothing flagged the loss, and the
  supervisory watchdog was itself holding on an unparsable key. The loss sat for 2.5 days until an activation read
  the program's own result. A verdict has to be computed from what was captured, not carried from an earlier
  stage.
  <!-- FACT S9-06: RUN_STATE item 249 (activation 30693ba4, 2026-11-10: "R1 ... NEVER MEASURED"; `status: refused`,
  `host_lock_unavailable`; "`night/result.json` still says `verdict: GO` ... and the courier sent normally, so
  nothing flagged the loss"; "Why it sat 2.5 days: the watchdog held in HOLD_UNSAFE ... because it could not
  parse the installed plists' `ac_powermode` key"); items 250-251 concern a distinct later refusal and are not part of
  this cause. No measured value of that study is used. -->
- **Analysis runtime is a defect.** One run of the primary block's blind analysis died after 18.5 h when parallel
  agent test runs filled the disk with about 110 GB of fixtures. Another took 27.1 h. A rewrite ran in 1 h 46 min
  and was shown equivalent to the 27.1 h run under a fixed comparator. The two runs were on differently
  loaded machines and the faster was niced, so the gain is not attributed to the rewrite alone, and the comparison
  of the last steps was still pending at that record. Agents sharing a machine share its disk, and a slow analysis is a process failure to be profiled, not waited out.
  <!-- FACT S9-07: RUN_STATE item 165 ("Attempt D (r1, item 160) died at step 9 on ENOSPC after 18.5 h. Parallel
  agent test runs had filled the disk with about 110 GB of fixtures"; "Candidate 1 ran in 1 h 46 min (attempt E
  took 27.1 h) and is EQUIVALENT to attempt E under the fixed comparator"); D-188;
  docs/process_traces/2026-11-04-d188-retrospective/RETROSPECTIVE.md:9-15 ("Not all of that speedup is the
  rewrite. E ran on a more loaded machine than candidate 1, and candidate 1 was niced 5"; "The final comparison,
  which also covers steps 9b, 10 and 11, waits"). -->
- **A release hold can be traced blind.** A release check of the primary block held on 1,001 failing comparator
  rows in 11 families. A trace that read only leaf identifiers, verdicts, reasons and coarse difference classes
  attributed every row to one of six defects from structure alone; the last remaining defect was fixed in a later
  analysis version.
  <!-- FACT S9-08: docs/run_reports/2026-11-07-b5-release-hold-trace.md:3-8 (inputs read: identifiers, verdicts,
  reasons, types and a coarse relative-difference class only; "This report holds no value"), :14 ("1,001 failing
  rows in 11 families"), :159 ("Every failing row maps to one of six defects. No row is left unattributed");
  docs/analysis/b5/DEVIATION-LOG.md DLE-0, DLE-1, DLE-3; TALK-OUTLINE-v2.md H7 (D5 fixed in r4, PR #697). -->
- **The agents' own safety checks stopped measurement steps.** The permission check of an agent session refused
  to load the replication's loop and refused to stop a stray process; the researcher was sent the command each
  time. A check that cannot tell a measurement step from a risky one costs a human round trip, and the record has
  to show who ran the step.
  <!-- FACT S9-09: RUN_STATE item 44 ("the auto-mode classifier refused `launchctl bootstrap` of the loop ... Ed
  was emailed the one command"); item 42 (pid 43816: "The auto-mode classifier refused the ... `kill`. Ed was emailed"). -->
- **Authority has to be written in one place.** Twice the record had two sources of ruling on one question. On
  6 November, on the researcher's instruction, the lead's holds on re-running measurements were withdrawn and
  scheduling passed to the headless supervisory agent; on 10 November a design ruling convened by a supervisory activation was reclassified
  as a proposal, and the research-lead log became the single binding record.
  <!-- FACT S9-10: RUN_STATE item 181 ("Item 176 (2)'s and item 178 (1)'s 'the laptop lead decides' re-run holds
  were the lead over-reaching. They are withdrawn"); item 257 ("`docs/process_traces/2026-11-10-r1-g0/10-fable52-
  ruling.md` is therefore a proposal"; "Magistrates ... do not convene their own deciding seat"). -->
- **Review overhead held work back.** The 27 October review of the October record found that serial review rounds
  and gating had added time with little protection. The project's gate policy was rewritten then, before any primary,
  replication or BYTES result was seen, to fit the depth of review to whether a change can alter a number
  (Section 8.2, item 4). Analysis runtime was a second bottleneck (above).
  <!-- FACT S9-11: docs/process/gate_policy.md:8 ("This policy was made before any block-5, block-6 or BYTES result
  was seen") and :20-21 ("Councils on process questions, reviews of docs and bookkeeping, and serial re-reviews added
  time and little protection"); docs/process_traces/2026-10-27-pipeline-audit/SYNTHESIS.md (proposals, not adopted;
  corrected by CRITIQUE.md). -->

{{FILL: P1-AUTO-BLINDCHECK | disclosure from the recorded check and deviation BY-BLIND-1: per-request timing of one held-out model was read and published before the stage-1 commitment; per-stage timestamps of every session were in the public operational record; each model's approximate decode time was registered from the pilot; why the committed lines cannot depend on any of it; and what the check could not establish}}

The lesson we draw, an inference from this record rather than a demonstrated guarantee, is that agents can run a
measurement study with the rigour such a study needs only if the rigour is mechanical. Digests, custody maps,
physical refusals and independent recomputation of the core arithmetic are designed not to depend on what an
individual agent believes; in the record above, reviews and judgments helped most when they ran the code. Where a
mechanical check was missing, as with a verdict carried from an earlier stage, the failure stayed unseen until
someone read the record.

## 9. Limitations

**Phase attribution was not checked by an independent instrument.** Every phase energy rests on the sampler's own
records and on the held-average reconstruction. No external instrument measured where energy falls within a
record or at a phase edge. The attribution floor bounds how far the *assigned* energy moves under the registered
timing domain; it is not a bound on the physical energy of a phase.

**Pulse-to-inference transfer is untested.** The timing bound comes from long, square GPU pulses. Inference has a
different sequence of work at the prefill-to-decode transition, which could make the bound too narrow or
unnecessarily wide. A registered inserted-gap experiment, which would pause between prefill and decode and compare
independently stamped edges with the power record, was not run.

**Calibration coverage is a design rationale.** The 59-pulse maximum is a 95/95 bound only if pulse displacements
are independent and identically distributed; pulses of one capture are not, and empirical coverage was not
established.

**One machine, one stack, one boundary.** All results come from one Apple M3 Max laptop, its recorded operating
system build(s), one MLX runtime and one sampler configuration. A different chip, firmware, operating system,
runtime or sampler could change the edge response, the power scale or both, by an unquantified amount. The
replication is across sessions and days on the same machine, not across machines.

**Counter gain.** The rail energies are on the sampler's own scale, whose gain was not checked against an external
instrument at the rail boundary. The whole-machine meter checks plausibility at a wider boundary; it neither
validates the rail gain nor the phase split, and it excludes the adapter's conversion loss.

**Workload.** One fixed decode prompt, one prefill length of 2,048 tokens and greedy generation of exactly 512
tokens. No claim is made about other prompts, lengths, sampling settings, batch sizes or concurrent requests.

**Statistical model.** Repeats and quads are modelled as independent units; consecutive units share slow drifts,
so independence is an assumption. Each Part 1 interval covers variation within one session; the replication
reports between-session variation descriptively and pools nothing. Contrast quads ran in a fixed, unrandomized
order; a curved drift does not cancel within a quad.

**Floor transfer.** Contrasts are judged against floors measured in separate sessions, under the registered
assumption that "the shared onset and offset edge treatment calibrated on floor blocks transfers unchanged to the
consuming contrast at the same block timescale"; the historical evidence for it records bounds, not realized
run-level boundary errors.

**Drift transfer.** The drift allowance is measured on reference requests of a few tens of joules. The scaled
sensitivity line (Section 4.7) shows how the replication results would change if drift scaled with energy or
duration; which is right was not measured.

**Gross energy.** Phase energies include the machine's baseline power over the phase. A longer phase therefore
carries more baseline energy, and part of any model difference is duration times baseline power.

**Excluded units.** The intervals do not cover bias from which units were removed. Labelled lines show the effect
of the load-correlated and battery-assist rules; no line can show the effect of physical-hazard removals, which are
required.

**BYTES.** Bytes per token are format-derived counts, not measured memory traffic. Dense held-out models cannot
discriminate between the hypotheses. The split of memory energy between rails and rest depends on whether the GPU
rail includes the memory controller (Section 3.3). The meter's label offset was not measured; DC-input and rest
statements are printed under both the registered and the alternative interval. No drift-transfer test passed, so
the drift allowance is scaled by a registered rule rather than measured transfer. Both extension models were
dropped (Section 7.4). The KV cache size is averaged over the 512 decode passes of one prompt length.

**Automation.** The agents that ran the study also wrote much of this paper. The controls of Section 8.2 constrain
what an agent could change in the data and the analysis; they do not make the prose neutral. The registrations'
specified sentences predate the data they govern; the draft's additional branch prose was written before
release, at commit `a1a5029fb`, after primary collection. Corrections made after release are stated in Section 1.2.
<!-- FACT H20: R2P P5; RL-1/RL-5; H16 for extension status. -->

## 10. Outlook: physical auditing of agents

## 11. Conclusion

A laptop's own power sampler can divide inference energy between prefill and decode, but only within limits that
the measurement must report: an attribution floor from phase-edge timing, a detection floor from false
differences between identical runs, and the dominance ratio that compares timing widening with repeatability. We
measured these quantities for two models on one Apple M3 Max laptop under pre-registration, blinding and
independent recomputation; the registered replication was collected in further sessions and remains blinded.
<!-- FACT H21: paper-audit C-2/C-11; no replication result is asserted. -->

**[BRANCH 9.D — dominance branch]** {{FILL: CP-X02-conclusion | under branch A: "On this stack, timing attribution, not repeatability, limits phase-energy measurement: allowing each value to move within its registered timing uncertainty at least doubled every detection floor." Under branch B: "Timing attribution at least doubled the detection floor for some components and not others (the failing components named), so neither timing nor repeatability alone limits these measurements."}} **[END BRANCH 9.D]**

**[BRANCH 9.C — contrasts]** {{FILL: CP-X08-decode-a-conclusion | one sentence per contrast in the registered wording for its outcome and claim level (Section 6.5 branch), with the replication word (Section 6.8)}} **[END BRANCH 9.C]**
<!-- FACT H22: RL-5 item 5; R2P P11; paper-audit C-10. Unconditional resolution gloss removed. -->

**[BRANCH 9.B — BYTES]** {{FILL: P1-BY-CONCLUSION | one sentence: the H1 words for the MoE models and the active-or-resident answer at rails and DC input, and the primary ε, in the registered wording; with the dense-model sentence}} **[END BRANCH 9.B]**

The methods (timing bounds carried into every phase energy, floors that refuse rather than average away missing
evidence, and registered fixed sentences) transfer to any software power counter with interval-average
records. So does the lesson of the automation: agents could run this study because the rules that protected it
were mechanical.

## Evidence and code availability

{{FILL: P1-AVAIL | public release: repository revision, archive locator and SHA-256 manifest of registrations, sealed inventories, flag catalogs, analysis and recomputation code, harvest records, released energies and figure sources; primary-block custody locator, dry-run record digest, released bundle SHA256SUMS and release-event binding; which raw captures are and are not released; locators must be supplied by the authorized release record, never inferred}}
<!-- FACT H31: R2P P12 (synthesis); release locators are required at fill, not populated by this seat. -->

## References

1. A. Tschand et al. "MLPerf Power: Benchmarking the Energy Efficiency of Machine Learning Systems from μWatts to MWatts for Sustainable AI." *IEEE HPCA*, 2025, pp. 1201–1216. DOI:10.1109/HPCA61900.2025.00092.
2. Standard Performance Evaluation Corporation. *Power and Performance Benchmark Methodology*, V2.3. https://www.spec.org/power/docs/SPEC-Power_and_Performance_Methodology.pdf.
3. S. Rivoire, M. A. Shah, P. Ranganathan, and C. Kozyrakis. "JouleSort: A Balanced Energy-Efficiency Benchmark." *ACM SIGMOD*, 2007, pp. 365–376. DOI:10.1145/1247480.1247522.
4. K. N. Khan, M. Hirki, T. Niemi, J. K. Nurminen, and Z. Ou. "RAPL in Action: Experiences in Using RAPL for Power Measurements." *ACM TOMPECS* 3(2), 2018, Article 9. DOI:10.1145/3177754.
5. M. Jay, V. Ostapenco, L. Lefèvre, D. Trystram, A.-C. Orgerie, and B. Fichel. "An Experimental Comparison of Software-Based Power Meters: Focus on CPU and GPU." *IEEE/ACM CCGrid*, 2023, pp. 106–118. DOI:10.1109/CCGrid57682.2023.00020.
6. C. Niu, W. Zhang, J. Li, Y. Zhao, T. Wang, X. Wang, and Y. Chen. "TokenPowerBench: Benchmarking the Power Consumption of LLM Inference." *AAAI* 40(38), 2026, pp. 32582–32590. arXiv:2512.03024.
7. J.-W. Chung et al. "The ML.ENERGY Benchmark: Toward Automated Inference Energy Measurement and Optimization." *NeurIPS Datasets and Benchmarks Track*, 2025. arXiv:2505.06371.
8. Z. Li et al. "Prima.cpp: Fast 30-70B LLM Inference on Heterogeneous and Low-Resource Home Clusters." *ICLR*, 2026. arXiv:2504.08791.
9. O. Basit, Y. Liu, Z. J. Kong, and Y. C. Hu. "DualScale: Energy-Efficient Disaggregated LLM Serving via Phase-Aware Placement and DVFS." arXiv:2602.18755, 2026.
10. A. Benazir and F. X. Lin. "Benchmarking and Characterization of Large Language Model Inference on Apple Silicon." *POMACS* 9(3), 2025, pp. 1–26. DOI:10.1145/3771563.
11. K.-D. Lange. "Identifying Shades of Green: The SPECpower Benchmarks." *IEEE Computer* 42(3), 2009, pp. 95–97. DOI:10.1109/MC.2009.84.
12. B. Ruf and M. Detyniecki. "The Cost of Context: Profiling the Energy Footprint of Input Tokens in Large Language Models." *HotCarbon '26*, 2026.
13. B. Ma, A. Afzal, J. Eitzinger, and G. Wellein. "The Illusion of Power Capping in LLM Decode: A Phase-Aware Energy Characterisation Across Attention Architectures." arXiv:2605.11999, 2026.
14. J. Saad-Falcon, A. Narayan, et al. "Intelligence per Watt: Measuring Intelligence Efficiency of Local AI." arXiv:2511.07885, 2025.
15. M. Dauner, M. Steinberg, A. Brunnert, B. Schicker, and B. Zönnchen. "Evaluating the Influence of Measurement Frequency on Energy Readings Using Intel RAPL and NVIDIA NVML." *HotCarbon '26*, 2026.
16. Z. Zhuang, Y. Li, and Z. Fan. "Pre-Registering the Detectable Effect: A Paired-MDE Budget for 4-bit Quantization Benchmarks, with a Pilot Audit." arXiv:2605.28873, 2026.
17. J. Li, Y. Zhu, B. Chen, E. K. Lee, and K. Nahrstedt. "Revisiting Disaggregated Large Language Model Serving for Performance and Energy Implications." *EuroMLSys '26*, 2026, pp. 397–406. DOI:10.1145/3805621.3807662.
18. Y. Guo and S. Joshi. "SplitZip: Ultra Fast Lossless KV Compression for Disaggregated LLM Serving." arXiv:2605.01708, 2026.
19. M. Hähnel, B. Döbel, M. Völp, and H. Härtig. "Measuring energy consumption for short code paths using RAPL." *ACM SIGMETRICS Performance Evaluation Review* 40(3), 2012, pp. 13–17. DOI:10.1145/2425248.2425252.
20. A. Georges, D. Buytaert, and L. Eeckhout. "Statistically Rigorous Java Performance Evaluation." *OOPSLA '07*, 2007, pp. 57–76. DOI:10.1145/1297027.1297033.
21. T. Mytkowicz, A. Diwan, M. Hauswirth, and P. F. Sweeney. "Producing Wrong Data Without Doing Anything Obviously Wrong!" *ASPLOS XIV*, 2009, pp. 265–276. DOI:10.1145/1508244.1508275.
22. J. R. Klein and A. Roodman. "Blind Analysis in Nuclear and Particle Physics." *Annual Review of Nuclear and Particle Science* 55, 2005, pp. 141–163. <!-- ADDED IN THIS DRAFT: cited by the BYTES registration; full locator to be verified in the bibliography audit. -->
23. S. Williams, A. Waterman, and D. Patterson. "Roofline: An Insightful Visual Performance Model for Multicore Architectures." *Communications of the ACM* 52(4), 2009, pp. 65–76. <!-- ADDED IN THIS DRAFT; verify. -->
24. R. Pope et al. "Efficiently Scaling Transformer Inference." *Proceedings of Machine Learning and Systems (MLSys)*, 2023. <!-- ADDED IN THIS DRAFT; verify. -->
25. B. A. Nosek, C. R. Ebersole, A. C. DeHaven, and D. T. Mellor. "The Preregistration Revolution." *PNAS* 115(11), 2018, pp. 2600–2606. <!-- ADDED IN THIS DRAFT; verify. -->
26. S. Holm. "A Simple Sequentially Rejective Multiple Test Procedure." *Scandinavian Journal of Statistics* 6(2), 1979, pp. 65–70. <!-- ADDED IN THIS DRAFT; verify. -->
27. J. G. MacKinnon and H. White. "Some Heteroskedasticity-Consistent Covariance Matrix Estimators with Improved Finite Sample Properties." *Journal of Econometrics* 29(3), 1985, pp. 305–325. <!-- ADDED IN THIS DRAFT; verify. -->

## Appendix A. Terms

| Term | Meaning (section of first use) |
|---|---|
| Prefill, decode | The phase that reads the prompt and computes the first output token; the phase that writes the remaining tokens (1.1) |
| Power record; support | One sampler output: average rail power over its own time span, the support (3.1) |
| Processor rails | CPU + GPU + neural engine power as reported by `powermetrics`; the Part 1 boundary (3.1) |
| DC input; rest | Energy entering the laptop after its adapter, with the battery term; DC input minus rails (3.2, 7.2) |
| Run; measured request; sampler stream | One request in its own process; the request whose energy is reported; the continuous sampler process of one run (4.1) |
| Gross energy | Energy with no idle power subtracted (4.1) |
| Held-average reconstruction | Treating power as constant within each record when sharing it between phases (4.1) |
| Fiducial bound; bracket; operative timing bound b | Largest pulse-edge displacement in one calibration capture; the opening and closing captures of a session; the session's timing bound (4.2) |
| Effective clock bound m; s; edge bound g | Clock-mapping uncertainty of a run; change in wall-minus-monotonic time over its stream; g = b + s (4.2) |
| First-kind timing bound | Largest change in a run's assigned phase energy over the registered edge and trace movements (4.2) |
| Repeat; quad; null quad; contrast quad | Single run; four runs ordered A, B, B, A; a quad whose sides are identical; a quad whose sides are the two models (4.3, 4.8) |
| Unit; stratum; kept unit | One repeat or one quad; all units of one kind; a unit none of whose runs was excluded (4.3) |
| Reported cell; target cell | One energy per model and phase from one session; the four cells the paper reports (4.3, 5.1) |
| Attribution floor | Largest first-kind timing bound over a cell's kept runs (4.4) |
| Detection floor (absolute, comparative, operative) | Largest false difference the estimator allows between identical runs (4.5) |
| Floor gate | The larger of the two models' worse floors for a phase (4.5) |
| Dominance ratio R; R_cm; branch A, B | Corner-widened over point floor; the shared-sign replay; all twelve ratios at least 2, or not (4.6) |
| Reference workload; corpus; triplets; midpoint | Fixed drift-tracking requests and their placement in a session (4.7) |
| Drift screen; drift allowance; scaled sensitivity line | Start-versus-end reference test; the allowance added to B; the allowance scaled by energy or duration (4.7) |
| Metrology interval; decision interval | Statistical interval of d̄; the same widened by the deterministic bounds D (4.8) |
| Outcome words | Not estimable; not resolvable; unresolved; direction supported (4.8) |
| L1, L2 | Instrument result; comparative result (4.8) |
| Pack; session; attempt | Frozen plan for one session; one unattended collection; one try at a session (5.2, 5.3) |
| Flag; physical hazard | Recorded code with one registered effect; a measured machine state that refuses collection (5.3) |
| Counting session; replicated | A replication session with no stop and no session-excluding condition; same outcome word and sign in every counting session (5.4) |
| Blind dry run; release event | End-to-end run writing only structure; the recorded moment after which numbers may be read (5.6) |
| Independent recomputation; twin | Second computation of headline numbers by code sharing nothing with the analysis (5.7, 7.3) |
| Format-derived bytes b; resident size R; decode time τ | BYTES regressors (7.1) |
| Fit set; held-out; word; active or resident | Models the lines are drawn through; models predicted from them; the H1 verdict per model; the MoE answer (7.2, 7.3) |

## Appendix B. Historical timing diagnostics

The method was developed on captures from the same laptop collected before the registered blocks, under an earlier
clock mapping that voids their energies for claim use. Re-derived under the current rate-aware mapping, one retained
pulse capture places all {{FILL: DX-012 | count of fitted onsets later than their commands}} of 59 fitted onsets after
their commands and {{FILL: DX-013 | count of fitted offsets earlier than their commands}} of 59 fitted offsets before
them, with medians of {{FILL: DX-010 | median onset lag}} and {{FILL: DX-011 | median offset lag}}. The pulses of one
capture are dependent; these statistics characterise that capture only, and the one-directional pattern has no
tested explanation, so no correction is applied and the symmetric timing domain includes it.

![Figure B1. Historical capture re-derived with the current clock method.](../figures/fig4_edge_excursions.svg)

*Figure B1. Fitted edge excursions of one historical GPU pulse capture under the current clock mapping (retained
figure of the methods draft). Historical, diagnostic only; it establishes neither phase-energy dominance nor
transfer to inference nor future coverage.*

## Appendix C. Fixed disclosure sentences

These sentences are registered and printed verbatim where they apply. The replication block prints "session" for
"window". Where a registered sentence names the drift screen by its internal label, this draft writes "drift
screen"; the wording to print is an open question for the author (see the draft summary).

- *Conditionality:* "These numbers are conditional on a window that passed the registered physical-hazard checks
  at arm and kept at least 5 of 10 units per stratum after the registered exclusions; the kept units of each cell
  are printed beside it."
- *A hazard not read at arm:* "At this window's arm the [clock, battery, thermal, contention, disk] check returned
  no reading and did not refuse; the monitor measured it during the window."
- *Single window:* "The units of this cell were measured in one window; the interval covers variation within that
  window, not between days or windows. The repeats and quads are modelled as independent units; that is an
  assumption."
- *Lost midpoint:* "The midpoint reference was lost, so drift inside this window that reverted by its end was not
  measured; the drift allowance uses the start and end references only."
- *Battery temperature:* "Stage S warmed by X K without levelling off; the window's drift screen [passed/failed],
  and the reported numbers rest on that screen, not on this reading."
- *Short prefill:* "The 42-token prefill of the decode workload is shorter than one power record and could not be
  resolved; as registered, no value is reported."
- *Separate windows:* "The 1.7B and 8B reported cells were collected in separate windows in a fixed order; their
  difference is not a comparison."
- *Dominance:* "R is a point diagnostic with no interval; 'independent' names the independent-corner component."
- *Phase attribution:* "Phase attribution is reported without a measured instrument phase-accounting check."
- *Fixed prompt:* "The decode contrast uses one fixed prompt; no prompt-population generality is claimed."
- *Order:* "Every quad ran 1.7B, 8B, 8B, 1.7B in that fixed order; the order was not randomized, and the p-value
  assumes the quad differences are independent."
- *Gross energy:* "Phase energy is gross: it includes the machine's baseline power over the phase, and the 8B phase
  lasts longer, so part of the difference is baseline power times the extra duration."
- *Whole-machine boundary:* "Whole-machine DC input plus the battery term, measured at the USB-C input; the
  adapter's AC-to-DC loss is not included."
- *BYTES dense models:* "Dense held-out models test linearity over the format-derived bytes range; their small
  rival splits do not identify the hypothesis."
- *BYTES per-token label:* "512 decode forward passes, one of which yields no returned token."

## Appendix D. Estimator derivations and synthetic examples

### D.1 Overlap example and historical minimum record support

*Synthetic example:* a phase runs from 10.00 s to 10.25 s; record 1 covers
9.90–10.03 s at 20 W (overlap 0.03 s, 0.60 J); record 2 covers 10.03–10.16 s at 30 W (0.13 s, 3.90 J); record 3
covers 10.16–10.29 s at 30 W (0.09 s, 2.70 J); the phase energy is 7.20 J. Figure 1 illustrates the rule and the
effect of moving an edge.

Historical captures on the same laptop showed the cutoff biting on short phases
({{FILL: DG-067 | historical count of short prefill phases that crossed only two records}} of
{{FILL: DG-068 | historical population size}} for a 1.5-billion-parameter model; {{FILL: DG-136 | historical count of identifiable phases for a 7-billion-parameter model}} of
{{FILL: DG-135 | its population size}} passed), which is why the prefill workload uses a 2,048-token prompt.

### D.2 Calibration rationale and timing-bound examples

For each pulse, an estimator fits the power records with a baseline plus a rectangle whose onset and
offset may be displaced from the commanded times, and returns every displacement consistent with the records
within a fixed loss tolerance. A capture's **fiducial bound** is the largest absolute displacement over all
pulses, plus the uncertainty in placing that capture's trace on the wall clock.

If the displacements of the 59
pulses were independent draws from one distribution, their maximum would exceed that distribution's 95th
percentile with probability at least 0.95 (since 1 − 0.95⁵⁹ ≥ 0.95); pulses of one capture are not independent,
so this is a design rationale, not a demonstrated coverage.

*Synthetic example:* opening 40.0 ms, closing 30.0 ms, s_bracket 14.531 ms gives b = 40.0 + 14.531 =
54.531 ms.

Because power is never negative, assigned energy cannot rise as the start edge moves later or fall as
the end edge moves later, so the extremes lie at the four edge corners, each evaluated over the trace shift.

*Synthetic example:* b = 45.6 ms and s = 0.4 ms give g = 46 ms; with m = 2 ms, a start-edge record averaging 40 W
and an end-edge record averaging 10 W, moving the start 46 ms early and the end 46 ms late adds
0.046 × (40 + 10) = 2.30 J, and shifting both a further 2 ms early adds 0.002 × (40 − 10) = 0.06 J: the bound is
2.36 J. When a displaced edge crosses into a neighbouring record this closed form is only an approximation; the
registered quantity is the exact maximum.

### D.3 Reported-cell estimator and interval example

For a cell with n_r kept repeats (energies r) and n_b kept quads (quad means q):

1. **Mean.** m = 0.2 × mean(r) + 0.8 × mean(q). The weights are fixed by design, because 10 of the 50 runs are
   repeats and 40 are quad members; with all units kept this equals the plain mean of the 50 runs.
2. **Variance.** V = 0.04 × s_r² / n_r + 0.64 × s_q² / n_b, with sample standard deviations (divisor n − 1).
3. **Half-width.** h = t(0.975, min(n_r, n_b) − 1) × √V, using the smaller stratum's degrees of freedom.
4. **Recorded bounds.** B is the sum of three stratified averages (0.2 × repeat mean + 0.8 × quad-member mean) of
   per-run bounds: the first-kind timing bound (Section 4.2); an interpolation bound, which is identically zero
   for these interval-support records; and half the session's drift allowance (Section 4.7).
5. **Interval.** [m − h − B, m + h + B], not clamped at zero.
6. **Per-token value.** For decode, m divided by the 512 runtime-observed output tokens ("decode-phase energy per
   output token; 512 output tokens, 511 of them generated in the decode phase"); for prefill, m divided by the
   2,048 prompt tokens.

*Synthetic example (all units kept):* repeats with mean 10.0 J and s_r = 0.2 J, quad means with mean 10.2 J and
s_q = 0.18257 J give m = 10.16 J, √V = 0.047889 J, h = 2.262157 × 0.047889 = 0.10833 J; with B = 0.060 J the
interval is [9.9917, 10.3283] J.

### D.4 Detection-floor estimator, corner widening and small-sample guard

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
4.2. For the comparative form, each phase edge is treated as shared by the quad's four runs and moved by one
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

### D.5 Dominance example, shared-sign replay and branch rules

In the
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
attribution dominates the detection floor. Otherwise **branch B** reports each
ratio that failed. A zero denominator refuses; no infinity is ever printed. Every ratio is printed with its
numerator, denominator and n, and labelled "point diagnostic; no interval".

### D.6 Drift bound and scaled sensitivity line

**Drift bound.** From the clean corpus energies (the first twelve valid corpus runs in committed order; at least
six required), with n_s surviving start references and n_e surviving end references, U_j the mean of the
corpus's j largest values and L_j the mean of its j smallest,

  bound(n_s, n_e) = max( max(U_{n_s} − L_{n_e}, U_{n_e} − L_{n_s}), t × s × √(1/n_s + 1/n_e) ).

The first term is the widest gap two means of those sizes could show if drawn from the corpus itself; the
second is a 95% repeatability bound for a difference of two means when nothing drifts.

**The scaled sensitivity line.** The allowance is measured on reference requests of a few tens of joules and
added, unscaled, to phases that may be much larger and longer. Whether drift transfers in proportion to energy
or duration is unmeasured. Each replication cell therefore also prints a labelled line with the allowance term
multiplied by max(1, E/E_ref, T/T_ref), where E and T are the cell's mean energy and mean phase duration and
E_ref and T_ref those of the surviving references (for a contrast, the maximum of this factor over both sides).
*Synthetic example:* an allowance term of 0.49 J, E_ref = 37.0 J, T_ref = 4.0 s and a cell of 300 J over 9.0 s
give a factor of max(1, 8.108, 2.25) = 8.108 and a scaled term of 3.97 J. The line changes no registered number.
In Part 2 the same scale is part of the registered estimator (Section 7.3), because no drift-transfer test passed
before BYTES collection.

### D.7 Contrast descriptive checks

A **leave-one-quad-out** check recomputes the contrast without each kept quad in turn. If dropping some quad
changes the sign, the floor status, the Holm decision or the outcome, the contrast is *verdict-influential*. If it
moves d̄ by more than a quarter of the floor gate, that is reported.

Beside each contrast two **registered descriptive estimates** are printed and decide nothing: the 8B-to-1.7B
ratio of phase energies, exp(mean of ln(B-side mean / A-side mean)) with its t interval and without the recorded
bounds; and d̄ per token (÷ 512 output tokens for decode, ÷ 2,048 prompt tokens for prefill). Phase energy is
gross, and the 8B phase lasts longer, so part of any difference is baseline power times the extra duration.
