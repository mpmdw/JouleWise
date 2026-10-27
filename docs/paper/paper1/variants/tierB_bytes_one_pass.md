# Tier B: BYTES at its registered one-pass minimum

<!-- Use when BYTES pass 2 is incomplete at the 15 November scope freeze. Decided by completion, not by any
result. Replaces the named parts of ../paper1.md §6 and the abstract's Part 2 sentence. -->

## Abstract, Part 2 sentence (replaces the full draft's)

In a second part, BYTES, we test whether decode energy per token follows the bytes a model reads per token, its
resident size, or its decode time, using one registered pass of every model: three straight lines fixed on three
dense models are committed before ten held-out models are unblinded. {{FILL: P1-ABS-PART2 | the H1 words, active-or-resident answer and primary ε in registered wording, with "one pass"}}

## §6.2, "Collection" (replaces the passes sentence)

The registration targets two passes and sets a minimum of one. {{FILL: P1-BYB-PASSES | the sub-packs whose second pass was collected before the end of collection, and those whose second pass was not}}. The
analysis uses the registered minimum: one pass for every model. The extension models, scheduled after the
registered pass-1 sub-packs and dropped first when time ran short, are
{{FILL: P1-BYX-STATUS | extension models' status: reported in their own section, or dropped for time}}.

## §6.3, "Per model" (replaces the paragraph)

Each model's point is its single computed pass, with that pass's own (h + B), labelled *one pass*; this is the
registered fallback, fixed before any data so that it is not a choice made after seeing them. Where a model also
has a second pass, that pass is printed as a labelled description beside the registered one-pass value, never
averaged into it; and H2 is also printed over the models with two passes as a labelled sensitivity line. Because B
dominates the interval and does not shrink with passes, one pass loses little precision; what it loses is the
check that a model's value repeats on a second day.

<!-- Open question for Ed: the registration's one-pass fallback (a) covers a model whose *other* pass refuses or
is missing. When pass 2 was never collected for any model, should a second pass that does exist for some models
be (i) averaged in as the registration's two-pass rule says, or (ii) printed as description only as written
above? This file assumes (ii) for uniformity across models; (i) is what the registration's per-model rule would
do model by model. Ruling needed before fill. -->

## §6.4 (replaces the section)

Two models released after the roster was registered were added on 27 October 2026 as a separately labelled
extension. {{FILL: P1-BYX-STATUS | for each: collected with one pass and reported in its own table with its own Bonferroni family, or dropped for time before the registered end, recorded with no substitute}}

## §6.5, opening (adds before "Collection")

Every per-model value in this section is a one-pass value. The difference between passes, which the full
registration prints as a check of day-to-day repeatability, is available only for
{{FILL: P1-BYB-TWOPASS-MODELS | models with two collected passes, or "no model"}} and is printed as description.

## Limitations (adds one sentence to §8, BYTES paragraph)

Each model was measured in one registered pass, so day-to-day repeatability of BYTES values is not tested by
BYTES itself; the replication block's between-session summaries on the two shared Qwen3 models are the closest
evidence.
