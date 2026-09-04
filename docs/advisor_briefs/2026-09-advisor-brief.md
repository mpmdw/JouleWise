# JouleWise — advisor brief for Suzanne Rivoire, September 2026

JouleWise measures the energy an Apple-silicon laptop assigns to **prompt
processing**, when a model reads a prompt, and **token generation**, when it
produces later output tokens. The metrology problem is timing: the power sampler
reports average power over intervals about a tenth of a second wide, so moving a
phase boundary can move energy from one phase to the other while leaving the
whole-request energy unchanged.

## The current campaign

The **claim-bearing campaign**, meaning the campaign eligible to support the
paper's conclusions, compares four-bit models—weights stored with four bits per
value—named Qwen3-1.7B and Qwen3-8B. This fifth frozen campaign configuration
has rules fixed and sealed against later change before collection. It replaces
the earlier Qwen2.5 comparison and fixed 256-token prompt. Token generation uses
real prompts, the Qwen3 **conversation template**, the format that turns a
conversation into model input, with extended reasoning off; **greedy decoding**,
which selects the most likely next token; and a forced 512-token output. A
**shakedown**, an instrument-readiness trial, selects the shortest prompt for
which every small-model trial overlaps at least five **power-sampling records**,
each an average-power report for a recorded interval.

The two comparisons are prompt processing and token generation. Each uses ten
complete **A/B/B/A blocks**: one smaller-model run, two larger-model runs, then
one smaller-model run. This order counters simple linear drift. No campaign
result is claimed here; these are its fixed judging rules. [Issued campaign
design](../decision_log.md#d-164-newer-models-in-the-campaign-ed-2026-08-28)

The main falsification test asks whether timing attribution dominates
repeat-to-repeat variation. For each model and phase, the **dominance ratio**,
R, divides the worst allowed false difference—an apparent condition difference
that timing uncertainty could create—by the corresponding bound with recorded
phase edges treated as exact. Its components are same-model repeatability and
the between-model comparison. Timing is dominant only if R ≥ 2 for every
component and condition: boundary motion must at least double each bound. A
**shared-error ratio** instead moves the session-wide timing error in one shared
direction across blocks. If it is below two, the paper withdraws the dominance
sentence. This separates timing error that repeats cannot average away from
independent edge movements that could overstate the problem. [Issued dominance
criterion](../decision_log.md#d-165-the-falsifier-magistrate--cold-gate-2026-08-28)

## Two checks on the metrology argument

The **dependence sensitivity sheet** asks whether adjacent blocks move together.
It recomputes each comparison with independent blocks, estimated neighbour
correlation, and a pessimistic **effective sample** of five blocks—the smaller
number of independent blocks giving the same repeat uncertainty. Only repeat
uncertainty changes; issued measurement uncertainty remains fixed. Agreement
does not prove independence. Disagreement prints all three intervals and
withholds the direction. The **direction screen** requires the complete
uncertainty interval to remain on the expected side of zero. [Pre-registered
dependence analysis](../paper/round7/dependence-sensitivity.md)

The **timing-excursion decomposition** explains the retained 30.07-millisecond
**calibration bound**, the maximum timing displacement carried into the energy
calculation. Its terms are 13.0 milliseconds of median, repeatable start-delay;
14.0 milliseconds from the worst pulse beyond that median; 1.93 milliseconds
for the remaining allowed interval; and 1.13 milliseconds for placing the trace
on the wall clock. The repeatable onset bias is the largest single term, but
pulse-to-pulse scatter is slightly larger. Removing the bias would greatly
improve a typical edge while shrinking the worst-case bound by less than half.
A plausible but untested explanation is that starting graphics work requires
dispatch, scheduling, and a power ramp, whereas stopping follows a different
drain-and-decay path. [Issued decomposition and source
artifact](../paper/round7/excursion-decomposition.md)

## The negative result already in the manuscript

A sampling record counts only when its interval overlaps prompt processing for
positive duration; the calculation requires at least three overlapping records.
In the retained earlier diagnostic population, 37 of 50 phases overlapped only
two records, while 13 overlapped three. Most were therefore too brief for this
phase-energy calculation. That does not mean their energy was zero, compare
models, or limit the forthcoming campaign. It explains the current five-record
prompt-selection requirement. The source is the [issued result
records](../paper/results-fill-registry.md#diagnostic-era-value-custody-addendum-3-item-38),
also printed in manuscript Section 6 on the paper branch dated September 2.

## Three questions for your judgment

1. Does an independently time-stamped no-work gap inside real inference adequately test whether the square-pulse timing bound transfers to inference, or would you require another physical transfer fiducial—a known event used to test that transfer?
2. Do prompt processing and token generation belong in one two-comparison Holm family—a step-down correction controlling the chance of any false directional claim—or are their physical mechanisms distinct enough for separate families?
3. Given sampling intervals near a tenth of a second and the three-record minimum, is selecting a longer prompt for five-record support sufficient treatment of cadence, or should the paper include a cadence sweep or higher-rate reference measurement?
