# DIFFICULTY pack registration, version 1

Status: committed before any DIFFICULTY energy session exists (the commit time is the registration time). Author: Opus 5.5, orchestrator. Governing texts: `docs/design/block6_collection_draft.md` sections 14 to 18; the pack code on `lane/2026-10-14-difficulty-pack` (head `346a5b246`) and its spec v1.1 (`/Users/edr/night-archive/difficulty-pack/SPEC.md`, reproduced in `docs/contracts/difficulty_tables.md` on that branch); the pilot (`/Users/edr/night-archive/pilots/difficulty/SUMMARY.md`, no power capture).

## 1. Question

For each MATH difficulty level 1 to 5, which configuration (a Qwen3 model at 4-bit and a thinking mode) produces a correct answer for the fewest joules; whether that choice changes with level; and how much of the energy per attempt is explained by tokens generated. Outputs say "at level L", never "difficulty causes".

## 2. Configurations

| Configuration | Output cap (tokens) | Status |
|---|---|---|
| Qwen3-1.7B, thinking off | 4,096 | measured |
| Qwen3-4B, thinking off | 4,096 | measured |
| Qwen3-8B, thinking off | 4,096 | measured |
| Qwen3-4B, thinking on | 16,384 | measured |
| Qwen3-8B, thinking on | 16,384 | optional: measured only if the machine schedule allows before the end date; if measured, analysed exactly like the others |

Qwen3-1.7B with thinking on is not measured (pilot: less accurate than 4B thinking off at every level, 4 to 6 times slower per correct answer). Model files: the pinned copies under `/Users/edr/jw_models` at the revisions the campaign panel pins. Greedy decoding. Prompts rendered by the pack's `rendered_prompt` with the importer's template.

## 3. Problems

The manifest `manifest-difficulty-v1.json` built by `scripts/difficulty_manifest.py` from the pack config (seed `joulewise.packs.difficulty.v1`), excluding the importer's pilot and n=128 sets and every problem the pilot used (`pilot_item_ids.txt`): 200 problems per level, subject-balanced in every prefix.

- **Bench (accuracy and tokens, no power capture):** thinking off, all 200 problems per level per configuration; thinking on, the first 64 per level.
- **Energy subset (power capture, whole-request energy):** the first m problems of each level in manifest order, m = 20 at levels 1 and 2 and 40 at levels 3 to 5 for thinking off (the pilot's runaway rate exceeded 5% there), m = 20 at every level for thinking on.
- Accuracy for the energy-per-correct interval comes from the bench problems outside the energy subset (spec 5.3); the headline accuracy table uses all bench problems.

## 4. Estimators (spec sections 5 and 6, unchanged)

Per boundary (rails, and the whole-machine meter as a labelled line) × configuration × level, confidence 0.95: accuracy with a Wilson interval; mean whole-request energy per attempt with a t interval; energy per correct answer = mean energy per attempt ÷ accuracy, with the MOVER interval on the log scale using the holdout accuracy; joules per generated token with the ratio-estimator interval; the decomposition of energy on prompt and generated tokens (intercept, slopes, R², generated-token share, per-level mean residuals). Energy is gross (idle not subtracted), the same basis as the rail cells.

## 5. Crossover rule and multiplicity

Per level, the cheapest configuration is the one with the lowest point estimate of energy per correct answer. It is **resolved** when the lower bound of ln(EPC_rival / EPC_cheapest) exceeds 0 for every rival at confidence 0.99 (0.95 divided across the five levels, Bonferroni); 0.95 intervals are printed beside it as description. **The choice changes with level** only when two resolved levels have different winners. Configurations are treated as independent though they answer the same problems; this errs toward "unresolved".

## 6. Exclusions and flags

A row is excluded when it carries `runtime_failed` (a harness failure, not an answer) or a physical flag the block-6 plan names as excluding (agent overlap, sleep, contention above its level, idle wait at the cap). A capped answer counts as wrong and is flagged `cap_hit`; repetition loops are flagged and kept. The printed results also show a line with every flagged row included.

## 7. Blinding, collection and end date

Energies are blinded by the pack's hidden factors (design section 16) until the analysis is frozen and the twin (`scripts/difficulty_twin.py`) agrees with the main code on the real tables. Accuracy from the bench is not an energy and is not blinded. Collection uses block-6 sessions and modules (design sections 14, 16, 17); the counts above are fixed; no precision-based stopping for this pack. Data collection ends 2026-11-07, or when every measured configuration has its counts. A configuration short at the end date is printed with its counts and called short.

## 8. What would change this registration

Nothing after the first DIFFICULTY energy session, except by an erratum that is dated, gives its reason, and prints the registered result beside the changed one.
