# Prefill-arm resolvability at 512, 1024 and 2048 prompt tokens

**Desk pre-registration for the G2 shakedown (D-166 R-2).**
Supporting material for reviewer-panel item D1.

Every number in this document comes from
`docs/paper/round7/prefill-resolvability-projection.json`, which is written by
the script named below and carries the SHA-256 of every retained file it read.

## Replay

```
/Users/edr/code/JouleWise/.venv/bin/python \
  scripts/paper_prefill_resolvability_projection.py \
  --corpus-root /Users/edr/code/JouleWise \
  --out docs/paper/round7/prefill-resolvability-projection.json
```

The script only reads. It opens no network connection, writes nothing into any
`runs*/` directory, and runs in about three seconds.

## What this document is, and what it is not

It is a statement, written before the measurement, of what the retained
evidence implies about three candidate prompt lengths — and of what the
measurement will decide. It is **not** a prediction that the campaign will
succeed. Where the retained evidence already says a length fails, this document
says so; where the evidence runs out, it says that instead of guessing.

Three things are settled here in advance so that they cannot be chosen after
the result is seen: the arithmetic that turns a phase duration into a record
count, the transfer assumption that carries a Qwen2.5 measurement onto a Qwen3
model, and the contingency for each way the shakedown can come out.

## 1. The words this document uses

A **bundle** is one measured run stored on disk as a directory: the runtime's
event log (`events.jsonl`), the power samples (`power_trace.csv`), the run
configuration, and a reduced summary (`summary_metrics.json`). A **corpus** is
one night's directory of bundles, named `runs…` at the repository root. Bundles
are never edited after collection, so every number below is read from bytes that
were written when the measurement happened.

**Prefill** (also called prompt processing) is the part of a generation request
that runs before the first output token appears: the model reads the whole
prompt and builds its internal state. In a bundle it is
delimited by two runtime events in `events.jsonl` — a record with
`event_type: "phase_start"` and `phase: "prefill"`, and the matching
`phase_end`. The **phase duration** is the difference of their `timestamp_s`
fields. No bundle stores this duration as a field; it exists only as that
subtraction.

**Powermetrics** is the macOS sampler that supplies the power readings. It does
not report an instantaneous wattage at a point in time. It reports one **record**
per sampling interval, and each record covers a stretch of time called its
**support interval**, written into `power_trace.csv` as the pair
`interval_start_s` / `interval_end_s`. A record is a rectangle: an average power
over that stretch.

A record **overlaps** a phase when the record's support and the phase window
share strictly positive time. The production reducer writes this exactly
(`joulewise/reduce.py:196-206`):

```
min(phase_end, support_end) > max(phase_start, support_start)
```

**Resolvable** means the phase has at least `MIN_PHASE_SAMPLES = 3` overlapping
records (`joulewise/reduce.py:116`). A phase with fewer is refused, and the
refusal is written into the bundle under the name
`not_resolvable_sample_count`. Energy is not estimated for a refused phase;
the refusal is the result.

**Margin** already has a definition in this repository, and it is a machine-
checked one. `joulewise/window_duration_margins.py:801-803` writes a field
literally named `sample_count_margin`, and the schema check at
`joulewise/window_duration_margins.py:1091-1093` rejects any receipt where it
is not exactly:

```
sample_count_margin = overlapping_power_interval_count - MIN_PHASE_SAMPLES
```

So a phase with three overlapping records has margin 0; six records is margin 3.

A **cell** is one fixed measurement condition — one model at one prompt length
and one output length — and a **member** is one bundle collected under that
condition. A cell is what gets repeated; a member is one repetition of it.

The **G2 shakedown** is the pre-campaign rehearsal night at which the prefill
length is to be fixed. The **mint** is the step that freezes the campaign's
configuration into an unchangeable pack; after the mint the prompt length cannot
be revised, which is why it has to be chosen from the shakedown record.

## 2. The rule being pre-registered, and an ambiguity in it

D-166 R-2 (`docs/process_traces/2026-08-28-workload-consult/04-MAGISTRATE-RULING.md`,
ruling R-2) fixes the `_v5` prefill length as:

> the shortest of {512, 1024, 2048} tokens whose small-model members show ≥ 3
> overlapping records with margin (≥ 5) in every shakedown member

The phrase **"margin (≥ 5)"** carries two readings, and they select different
lengths. This document evaluates both and prefers neither.

| Reading | What "margin ≥ 5" means | Required record count per member |
|---|---|---|
| **A — repository field** | `margin` is the existing `sample_count_margin` field, which is count minus 3. Margin ≥ 5 therefore means count ≥ 3 + 5. | **≥ 8** |
| **B — plain English** | "≥ 3 overlapping records with margin" is the rule; the parenthetical spells out "with margin" as an absolute floor of 5 records. | **≥ 5** |

Reading A has the stronger textual support: the repository already has a
quantity named exactly "margin", it is schema-enforced, and the consult's Sol
seat used the same convention in writing ("four or more gives one-record
margin" — `01-sol-seat.md:53`, margin counted against three). Reading B is the
more natural parse of the sentence as written, and is the weaker requirement.

**This is flagged for the magistrate as a NEEDS-RULING.** Section 8 shows the
two readings select different outcomes, so it must be settled before the
shakedown, not after.

## 3. What was read

The script walked every retained corpus under `/Users/edr/code/JouleWise`
(37 `runs*` directories) and kept every bundle whose model is one of the two
Qwen2.5 models and whose `events.jsonl` contains at least one complete prefill
phase pair. It found **1,127 bundles** holding **1,647 prefill phases** and
**328,522 power records**.

A bundle can hold more than one prefill phase. A dedicated cell holds exactly
one — the shape the `_v5` prefill members will have. A `jw_mixed_v1` suite
bundle holds one per item, five in total. The two shapes are kept apart
throughout, because their durations differ (Section 5) and only the single-item
shape matches the campaign design.

| Prompt tokens | Model | Cell shape | Bundles | Phases | Corpora | Example bundle |
|---|---|---|---|---|---|---|
| 128 | Qwen2.5-1.5B-4bit | single-item | 458 | 458 | 13 | `runs_recal2_20260719/p2015-df-cmp-abba-ph-short-prefill-b01-a1` |
| 512 | Qwen2.5-1.5B-4bit | suite item | 130 | 650 | 6 | `runs_recal3_20260719/p2015-df-cmp-abba-su-b06-a1` |
| 512 | Qwen2.5-1.5B-4bit | single-item | 15 | 15 | 2 | `runs_window_metrologyA_20260731/mtadd-p0512o0512-r01` |
| 1024 | Qwen2.5-1.5B-4bit | single-item | 276 | 276 | 29 | `runs_recal2_20260719/p2015-neg8-reference-end` |
| 2048 | Qwen2.5-1.5B-4bit | single-item | 14 | 14 | 2 | `runs_window_metrologyA_20260731/mtadd-p2048o0128-r01` |
| 4096 | Qwen2.5-1.5B-4bit | single-item | 164 | 164 | 9 | `runs_recal2_20260719/p2015-df-rq-long-prompt-abs-r01` |
| 128 | Qwen2.5-7B-4bit | single-item | 70 | 70 | 2 | `runs_window_7bfloor_20260729/sw7bfloor-df-cmp-abba-ph-decode-b01-a1` |

Per-bundle SHA-256 values for `events.jsonl` and `power_trace.csv` are in the
JSON under `phase_observations` and `bundle_rows`.

**Two gaps matter and are stated here rather than worked around.** There is no
retained bundle at 256 prompt tokens for any model — every 256-token figure in
the earlier consult seats is extrapolation. And **the large model was never run
at any prompt length except 128**: all 70 of its retained bundles use a
128-token prompt. Section 7 says what follows from that.

## 4. How records behave, measured rather than assumed

The draft's Section 6 states that record spacing exceeds record width "because
the sampler pauses between records." **The retained bytes do not support that
mechanism.** Across all 328,522 records, the largest gap between one record's
`interval_end_s` and the next record's `interval_start_s` is
**2.4 × 10⁻⁷ s** — floating-point noise. The records **tile**: each one begins
exactly where the previous one ended, and no stretch of the timeline is left
uncovered.

Width and spacing are therefore the same quantity, measured once per record.
What varies is the width itself:

| Statistic over 328,522 record periods | Value |
|---|---|
| minimum | 110.04 ms |
| 1st percentile | 112.38 ms |
| **median** | **120.80 ms** |
| 95th percentile | 125.04 ms |
| **99th percentile** | **127.59 ms** |
| 99.9th percentile | 130.63 ms |
| maximum | 460.70 ms |

This resolves an inconsistency in the registry. Row DG-071 records record width
as "measured 111.8–112.5 ms" and row DG-075 records spacing as 120.922 ms, with
the difference attributed to a sampler pause. In the bundle both rows cite,
`runs_window_a10_20260725/p2015-df-ph-decode-abs-r03`, only 6 of 406 records are
at or below 112.5 ms. **111.8–112.5 ms is the bottom of the width distribution,
not its range**, and the 120.9 ms figure is the median of the same distribution
rather than a different quantity. Both rows are `[PENDING]` in the draft, so
nothing published is wrong yet; the supplier notes need correcting before those
sites are filled.

The 460.70 ms maximum is not a normal record. A few traces drop samples, which
merges intervals. The bound below uses the **99th percentile, 127.59 ms**, and
reports the maximum beside it so the choice is visible rather than buried.

## 5. Turning a duration into a record count

Because records tile with no gaps, a phase window overlaps one record, plus one
more for every **tile boundary** — the instant where one record ends and the
next begins — that falls strictly inside the window. If no record is longer than
a period `S`, then a window of duration `D` contains at least `floor(D / S)`
boundaries. So:

> **guaranteed count = floor(D / S) + 1**

Using the *longest* plausible period makes this a floor rather than an estimate:
longer records mean fewer boundaries, hence fewer records. With lucky alignment
and the *shortest* observed period the count can reach `floor(D / S) + 2`.

**Worked example, the bundle the paper already cites.** In
`runs_window_a10_20260725/p2015-df-ph-decode-abs-r03`, the prefill phase runs
from 1784978933.267684 s to 1784978933.388718 s, so
`D = 0.121034 s`. With `S = 0.12759 s`:

```
floor(0.121034 / 0.12759) + 1 = floor(0.9486) + 1 = 0 + 1 = 1
```

so at least 1 record, and with the shortest observed period 0.11004 s,
`floor(0.121034 / 0.11004) + 2 = 1 + 2 = 3` at best. The recorded count for that
bundle is **2** — inside the band, and short of the threshold of 3. That is the
paper's printed negative result, reproduced from the formula.

**The formula was checked against every group, not just that one.** For all
seven groups in Section 3, the guaranteed count never exceeded the smallest
count actually observed, and the best case never fell below the largest:

| Prompt tokens | Cell shape | Observed counts | Bound (guaranteed – best case) |
|---|---|---|---|
| 128 (1.5B) | single-item | 2 – 3 | 1 – 3 |
| 512 | suite item | 2 – 3 | 2 – 4 |
| 512 | single-item | 3 – 3 | 2 – 4 |
| 1024 | single-item | 3 – 5 | 3 – 5 |
| 2048 | single-item | 6 – 7 | 5 – 7 |
| 4096 | single-item | 10 – 11 | 9 – 12 |
| 128 (7B) | single-item | 3 – 4 | 3 – 4 |

The bound is tight at 1024 and at the 7B 128-token cell, and loose at short
durations, which is the expected behaviour: alignment matters most when the
window spans barely one record.

**An independent check of the whole pipeline.** The script recomputed each
bundle's resolvability label from raw bytes and compared it with the label the
production reducer had already written into `summary_metrics.json`. Across all
1,127 bundles there were **zero disagreements**.

## 6. What the retained measurements say, per length

All Qwen2.5-1.5B, one row per prompt length and cell shape. "Fails" counts
phases with fewer than 3 overlapping records.

| Prompt tokens | Cell shape | Phases | Duration median | Duration IQR | Duration range | Prefill tokens/s | Overlap counts | Smallest margin | Fails |
|---|---|---|---|---|---|---|---|---|---|
| 128 | single-item | 458 | 0.1308 s | 0.0093 s | 0.1125 – 0.1522 s | 979 | 2 × 410, 3 × 48 | −1 | 410 / 458 |
| 512 | suite item | 650 | 0.1902 s | 0.0058 s | 0.1801 – 0.2451 s | 2 692 | 2 × 211, 3 × 439 | −1 | 211 / 650 |
| 512 | single-item | 15 | 0.2295 s | 0.0019 s | 0.2132 – 0.2462 s | 2 231 | 3 × 15 | 0 | 0 / 15 |
| 1024 | single-item | 276 | 0.3422 s | 0.0132 s | 0.3218 – 0.3636 s | 2 993 | 3 × 14, 4 × 252, 5 × 10 | 0 | 0 / 276 |
| 2048 | single-item | 14 | 0.5883 s | 0.0144 s | 0.5587 – 0.5964 s | 3 481 | 6 × 12, 7 × 2 | +3 | 0 / 14 |
| 4096 | single-item | 164 | 1.1199 s | 0.0121 s | 1.1049 – 1.1393 s | 3 658 | 10 × 14, 11 × 150 | +7 | 0 / 164 |

Large model, for comparison: at 128 prompt tokens, 70 phases, median 0.2810 s,
range 0.2587 – 0.2920 s, 456 tokens/s, counts 3 × 46 and 4 × 24, smallest margin 0,
0 failures.

Two features of this table carry the argument.

**The tokens-per-second figure rises with prompt length, so it is not a rate.**
979 tokens/s at 128 tokens against 3 658 tokens/s at 4096 is not the model
speeding up; it is a fixed startup cost being spread over more tokens. Any
projection that multiplies a short-prompt rate by a longer prompt is wrong, and
wrong in the unsafe direction — it over-predicts duration and so over-predicts
resolvability. Section 7 fits the fixed cost explicitly instead.

**512 tokens does not have one duration.** The same 512-token prompt length
gives 0.2295 s in a dedicated single-item cell and 0.1902 s as an item inside a
suite bundle — a 21 % difference at identical prompt length. The single-item
figure is the one that matches the campaign's design, but the suite figure is
retained evidence that a 512-token prefill on this machine can run short enough
to yield only 2 records: it did so in **211 of 650** suite phases. Within one
suite bundle the counts run `[3, 2, 3, 2, 3]` across five identical-length
items. That is the reviewer's D1 concern made visible — at 512 tokens, not only
at 256 — and it is why the single-item cell's clean 15-for-15 result is not on
its own sufficient reassurance.

## 7. The transfer assumption, stated as an assumption

**No Qwen3 prefill duration has ever been measured on this machine.** Every
Qwen3 figure below is a Qwen2.5 measurement multiplied by an assumed slowdown.
That is an assumption, and the G2 shakedown exists to replace it with a
measurement.

What is shared, and therefore not assumed: the same M3 Max machine, the same
MLX runtime, the same 4-bit quantization, the same powermetrics configuration,
and — from D-164 — a byte-identical tokenizer between the two Qwen3 models. The
sampler behaviour in Section 4 is a property of powermetrics and the machine, so
it transfers without a model assumption.

What is assumed: that prefill wall time scales with model size in roughly the
way parameter count suggests. Both campaign models are slightly larger than the
models they replace:

| Role | Retained (`_v4`) | Campaign (`_v5`, D-164) | Parameter ratio | 4-bit weight ratio |
|---|---|---|---|---|
| small | Qwen2.5-1.5B-4bit, 1.5 B, 0.87 GB | `Qwen3-1.7B-4bit`, 1.7 B, 0.97 GB | **1.133** | 1.115 |
| large | Qwen2.5-7B-4bit, 7 B, 4.30 GB † | `Qwen3-8B-4bit`, 8 B, 4.61 GB | 1.143 | 1.072 |

Weight sizes for the campaign models are the model-panel survey's table
(`docs/process_traces/2026-08-28-model-panel/00-SURVEY.md`, section 1), which
covers candidate models only. † is the measured on-disk size of the pinned local
artifact `/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit`
(4.0 GiB), not a survey figure. Nothing in Sections 8–10 depends on it.

Prefill is compute-bound rather than memory-bound, so parameter count is the
better of the two handles, and **1.133×** is the assumed slowdown for the small
arm — the arm the rule constrains. It is a planning number
with no measurement behind it, which is why Section 9 does not rest on it:
the projection table sweeps slowdowns from 1.0× to 3.0×, and the sensitivity
paragraph asks what slowdown each length would need rather than asserting one.

**The large arm is informational only.** With the large model measured at a
single prompt length, its 128-token duration ratio against the small model
(0.2810 / 0.1308 = **2.15×**) mixes a fixed startup term with a per-token term
and cannot be separated into the two. Its rows below are the small model's
fitted curve multiplied by that ratio, and they should not be read as a
projection of comparable standing. This matters less than it sounds: the D-166
rule constrains the **small** model's members, which is the arm that has real
evidence at all three candidate lengths, and every retained large-model phase is
already resolvable with margin 0 or better.

**The duration model.** A least-squares fit of
`duration = fixed_overhead + tokens / marginal_rate` over the five single-item
1.5B lengths gives a fixed overhead of **0.0939 s** and a marginal rate of
**4 023 tokens/s** (0.2486 ms per token). The largest residual is 14.8 ms, on
durations up to 1.12 s. The fit is used only where a length has no direct
measurement — that is, only for the large arm.

## 8. Projection

Small model. Durations are the measured Qwen2.5 single-item durations at that
length multiplied by the assumed slowdown; counts are computed by the Section 5
formula. "Guaranteed" uses the shortest measured duration with the 99th-
percentile record period; "typical" uses the median duration with the median
period; "best case" uses the longest duration with the shortest period.

| Prompt tokens | Slowdown | Duration (min – median – max) | Guaranteed | Typical | Best case | Reading A (≥ 8) | Reading B (≥ 5) |
|---|---|---|---|---|---|---|---|
| 512 | 1.000× | 0.2132 – 0.2295 – 0.2462 s | 2 | 2 | 4 | no | no |
| 512 | **1.133×** | 0.2416 – 0.2600 – 0.2789 s | 2 | 3 | 4 | no | no |
| 512 | 1.250× | 0.2665 – 0.2868 – 0.3078 s | 3 | 3 | 4 | no | no |
| 512 | 1.500× | 0.3198 – 0.3442 – 0.3693 s | 3 | 3 | 5 | no | no |
| 512 | 2.000× | 0.4265 – 0.4589 – 0.4924 s | 4 | 4 | 6 | no | no |
| 512 | 3.000× | 0.6397 – 0.6884 – 0.7386 s | 6 | 6 | 8 | no | yes |
| 1024 | 1.000× | 0.3218 – 0.3422 – 0.3636 s | 3 | 3 | 5 | no | no |
| 1024 | **1.133×** | 0.3645 – 0.3877 – 0.4119 s | 3 | 4 | 5 | no | no |
| 1024 | 1.250× | 0.4022 – 0.4277 – 0.4544 s | 4 | 4 | 6 | no | no |
| 1024 | 1.500× | 0.4826 – 0.5133 – 0.5453 s | 4 | 5 | 6 | no | no |
| 1024 | 2.000× | 0.6435 – 0.6844 – 0.7271 s | 6 | 6 | 8 | no | yes |
| 1024 | 3.000× | 0.9653 – 1.0266 – 1.0907 s | 8 | 9 | 11 | yes | yes |
| 2048 | 1.000× | 0.5587 – 0.5883 – 0.5964 s | 5 | 5 | 7 | no | **yes** |
| 2048 | **1.133×** | 0.6330 – 0.6665 – 0.6758 s | 5 | 6 | 8 | no | **yes** |
| 2048 | 1.250× | 0.6983 – 0.7353 – 0.7455 s | 6 | 7 | 8 | no | **yes** |
| 2048 | 1.500× | 0.8380 – 0.8824 – 0.8947 s | 7 | 8 | 10 | no | **yes** |
| 2048 | 2.000× | 1.1174 – 1.1765 – 1.1929 s | 9 | 10 | 12 | yes | yes |
| 2048 | 3.000× | 1.6760 – 1.7648 – 1.7893 s | 14 | 15 | 18 | yes | yes |

Large model, informational, at the assumed 1.133× slowdown: 512 tokens gives a
guaranteed 5 records, 1024 gives 7, 2048 gives 12. No candidate length puts the
large arm anywhere near the threshold.

The verdict columns use the guaranteed count, which is the reading the rule's
phrase "in every shakedown member" calls for.

## 9. Contingency

The rule is a selection procedure, and the shakedown supplies the input. The
table below says what each outcome selects, so the decision does not have to be
made with the result in hand.

| Prompt tokens | Smallest count measured on Qwen2.5 (single-item) | Smallest count measured (suite items) | Under reading A (≥ 8) | Under reading B (≥ 5) |
|---|---|---|---|---|
| 512 | 3 | 2 | fails | fails |
| 1024 | 3 | — | fails | fails |
| 2048 | 6 | — | fails | **clears** |
| *(4096, outside the ruled ladder)* | 10 | — | clears | clears |

**Under reading B, the shortest length that clears on retained evidence is
2048, and the ladder has a survivor.** Under reading A, **no length in
{512, 1024, 2048} clears on retained evidence**, and the contingency below is
live rather than hypothetical.

What happens at each outcome:

1. **If the small arm at 512 returns `not_resolvable_sample_count` in any
   member**, 512 is out and 1024 and 2048 remain. This is the outcome the
   retained evidence points at under both readings.
2. **If 1024 also fails**, 2048 remains. Under reading B, 2048 is expected to
   clear; under reading A it is not.
3. **If none of the three clears**, the ladder is exhausted, and there are three
   exits, in order of preference:
   - **Extend the ladder to 4096.** This is the only length with measured
     margin: 164 retained phases, smallest count 10, margin +7 under either
     reading. The cost is night time, and it is small — a 4096-token prefill
     runs about 1.12 s against 0.59 s at 2048, so 40 members add roughly 21
     seconds of generation to a window budgeted in hours. This exit requires a
     magistrate ruling, because 4096 is outside the D-166 ladder.
   - **Relax the margin, not the rule.** The rule proper is `≥ 3`, which is what
     the reducer enforces; the margin is a pre-registration safety factor
     chosen at the desk. Lowering it is a decision about how much alignment risk
     the campaign accepts, and it is reversible only before the mint.
   - **Print the refusal.** The demonstration reports two **contrasts** — one
     for the decode arm, one for the prefill arm — where a contrast is the
     small-model-versus-large-model energy difference for that arm. The two are
     tested together as one **Holm family**: a multiple-comparison correction
     that divides the error budget across a fixed, pre-declared number of tests
     (here m = 2) so that testing two things does not inflate the chance of a
     false positive. If the prefill arm is collected and refuses, the
     paper prints `not_resolvable_sample_count` for that arm, the family stays
     frozen at m = 2 with the failed contrast contributing a refusal
     rather than a p-value — the denominator does not shrink to reward the
     failure — and the decode arm carries the demonstration. This
     is a sound outcome and an honest one — the paper already has a printed
     negative result of exactly this kind — but it costs half the demonstration
     for a reason that was knowable in advance, which is precisely the failure
     reviewer item D1 named.

The refusal outcome must not be reached by accident. That is the whole purpose
of fixing the length from the shakedown record rather than from a guess.

## 10. Sensitivity

The question the projection cannot answer is how far the Qwen3 rate can differ
from the assumed 1.133× before the answer changes. That is settled by asking, in
reverse, what duration each length would need.

To reach a guaranteed count of `N`, a phase needs `N − 1` tile boundaries inside
it, so it needs a duration of at least `(N − 1) × 127.59 ms`. Under reading B
(`N = 5`) that is **0.5104 s**; under reading A (`N = 8`) it is **0.8931 s**.
Against the shortest duration each length actually produced on Qwen2.5:

| Prompt tokens | Shortest measured duration | Slowdown needed for reading B (≥ 5) | Slowdown needed for reading A (≥ 8) |
|---|---|---|---|
| 512 | 0.2132 s | **2.39×** | 4.19× |
| 1024 | 0.3218 s | **1.59×** | 2.78× |
| 2048 | 0.5587 s | 0.91× — already clears | 1.60× |

Read plainly: **512 tokens would need Qwen3-1.7B to be 2.4 times slower at
prefill than Qwen2.5-1.5B before it clears reading B, and 4.2 times slower for
reading A.** A 1.13× parameter-count ratio does not get near either. Nor does the
model-panel survey's own uncertainty: it attaches an "off by up to ~1.5×" band
to its planning estimates, and even taking that band at face value — and it is
stated there for *decode* rates, not prefill — 1.5 × 1.133 = 1.70× still leaves
512 short of reading B by a wide margin. **1024 tokens needs 1.59× for reading B.** That is a large gap but
not an absurd one, and it is the one number in this document where the
shakedown could plausibly overturn the desk expectation — which is a reason to
run the shakedown, not a reason to pre-judge it. **2048 tokens already clears
reading B at the measured Qwen2.5 rate**, with the shortest of its 14 retained
phases producing 6 records against a threshold of 5; it would have to be 1.60×
*slower* to clear reading A.

The sensitivity runs one way only. A Qwen3 model that is *faster* at prefill
than Qwen2.5 moves every length toward failure, and nothing in this document
rules that out.

## 11. Anomalies and corrections for the record

1. **The "sampler pauses between records" mechanism is contradicted by the
   bytes.** Records tile with a maximum gap of 2.4 × 10⁻⁷ s over 328,522
   records. Registry rows DG-071 and DG-075 attribute the width/spacing
   difference to a pause; the real cause is variation in record width. Both
   sites are `[PENDING]`, so nothing published is wrong, but the supplier notes
   need correcting before they are filled (Section 4).
2. **DG-071's "111.8–112.5 ms" is the bottom of the width distribution, not its
   range.** In the cited bundle, 6 of 406 records fall in that band; the median
   is 120.9 ms and the maximum 128.7 ms.
3. **The bundle name `p2015-df-ph-decode-abs-r03` resolves five ways.** Five
   retained corpora contain a bundle with that name, with prefill durations from
   0.1210 s to 0.1374 s. The paper's number is the
   `runs_window_a10_20260725` copy. Citations of it should carry the corpus root.
4. **512 prompt tokens has two retained durations that differ by 21 %**
   (0.2295 s single-item, 0.1902 s suite item), and the shorter one fails the
   ≥ 3 rule in 211 of 650 phases. Section 6.
5. **No retained bundle exists at 256 prompt tokens, for any model.** Every
   256-token figure in the D-166 consult seats is extrapolation, including the
   ones that motivated retiring `prefill_p256`. The conclusion to retire it is
   independently supported by the 128-token evidence (410 of 458 phases fail),
   but the specific 256-token numbers have no primary artifact behind them.
6. **The large model has no retained bundle at any prompt length except 128.**
   Its rows in Section 8 are constructed, not measured (Section 7).
7. **A 4.39× "prefill ratio" cited in the consult's Opus seat is an energy
   ratio, not a duration ratio.** The measured duration ratio between the two
   models at 128 prompt tokens is 2.15×. Using the energy ratio to scale
   durations would overstate large-model prefill duration by about a factor of
   two — in the direction that flatters resolvability.
8. **"margin (≥ 5)" in D-166 R-2 is ambiguous** and the two readings select
   different lengths. NEEDS-RULING; Section 2.

## 12. What the shakedown must record

For the pre-registration to bind, the G2 record needs, for every small-model
member at each candidate length: the prefill phase start and end timestamps, the
overlapping record count, the `sample_count_margin` field, and the per-record
support intervals from which both were derived. All four already exist in the
bundle format — nothing new has to be built. The selection is then mechanical:
apply the ruled reading of the margin to the smallest count observed across
members, and take the shortest length that clears.
