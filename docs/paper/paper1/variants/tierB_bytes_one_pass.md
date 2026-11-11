# Tier B: BYTES at its registered one-pass minimum

<!-- Historical contingency template, not the current collection state: pass 2 is complete
(paper-audit F-20 and §6; RUN_STATE items 349/898 as cited there). A missing or refused usable pass is handled
per model by the registration; collection completion alone does not establish usability. RL-24's scope freeze
is 5 December. No tier or result is selected here. FACT H26: paper-audit F-20; RL-7(f); RL-24. -->

## Abstract, Part 2 sentence (replaces the full draft's)

In a second part, BYTES, we test whether decode energy per token follows the bytes a model reads per token, its
resident size, or its decode time, with the registered one-pass fallback applied per model: three straight lines
fixed on three dense models must be committed before seven held-out models are unblinded. {{FILL: P1-ABS-PART2 | the H1 words, active-or-resident answer and primary ε in registered wording, with per-model one-pass labels}}
<!-- FACT H27: RL-5 item 5; paper-audit §4.2. -->

## §7.2, "Collection" (replaces the passes sentence)

The registration targets two passes and sets a minimum of one. {{FILL: P1-BYB-PASSES | the sub-packs whose second pass was collected before the end of collection, and those whose second pass was not}}. The
analysis applies the registered pass rule per model. Both extension models were dropped (main draft §7.4);
{{FILL: P1-BYX-STATUS | source identifiers for the two structural drop decisions only; no model quantities or results}}.

## §7.3, "Per model" (replaces the paragraph)

For a model with one usable pass, its point is that pass with its own (h + B), labelled *one pass*, under the
registered fallback. A model with two usable passes follows the registration's two-pass rule, including the
pass mean and difference; H2 is also printed over models with two passes as a labelled sensitivity line.
<!-- FACT H28: paper-audit F-20; RL-7(f); the registration's per-model rule also appears in paper1.md §6.3. -->

## §7.4 (replaces the section)

Both extension models were dropped: Nemotron had no loadable compatible build; Qwen3.8-27B was dropped under
the registered extension-first rule. {{FILL: P1-BYX-STATUS | source identifiers for the two structural drop decisions only; no model quantities or results}}
<!-- FACT H29: RL-5 item 5; paper-audit §4.2/F-18; RUN_STATE.md:902. -->

## §7.5, opening (adds before "Collection")

Models with one usable pass are labelled *one pass*. The registered difference between passes is available for
{{FILL: P1-BYB-TWOPASS-MODELS | models with two usable passes, or "no model"}} and is printed as description.

## Limitations (adds one sentence to §9, BYTES paragraph)

For a model with only one usable pass, BYTES does not test day-to-day repeatability of that model's value.
