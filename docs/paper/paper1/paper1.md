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
