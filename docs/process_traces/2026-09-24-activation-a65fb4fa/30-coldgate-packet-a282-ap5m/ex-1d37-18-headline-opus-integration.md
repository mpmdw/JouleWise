# Integration consult: headline packets A, B and C (Opus 5.5, read-only at 313efcca)

## Answers first

- **The three packets mostly fit together.** There are six real conflicts:
  1. B's packing puts the 1.7B's whole cell in one envelope, which fails claims-ladder L2's "n >= 5 per condition" under C's own reading.
  2. Pilot size: A pilots 16 items in total, B wants 16 per level.
  3. B keeps the GSM8K truncation rule.
  4. B's "net" joules conflict with D-045.7, which says block and level energies are gross only.
  5. A's "commit hashes only" option (R1(b)) conflicts with B's binding of tracked files.
  6. C defines the crossover from raw 95% intervals, but its decision rule uses Holm.
- **The biggest gap nobody names:** the MLX adapter always decodes greedily (`joulewise/adapters/mlx_runtime.py:984-1009`, temperature 0). B's plan to reuse it "unchanged" therefore holds only if we stay greedy. Also missing: a registration packet, code for C's estimator, the affine-ladder leg, and figure code.
- **Q3:** in the thinking-on arm, use the model card's sampling settings with one pinned seed per (item, model) and one attempt per item. This depends on a bench test showing that seeded MLX sampling reproduces the same tokens. If it does not, fall back to greedy decoding, label repetition loops, and put "under greedy decoding" in the claim.
- **A structural improvement:** under a fixed decoding rule, token counts do not depend on the power capture. Split the pilot into (i) a **bench token pilot**, run between windows, which measures tokens per item, cap hits, loop rate, the scorer audit and a rough seconds per token; and (ii) one short shakedown night for envelope timing. The pilot then costs almost no window time, which settles the pilot-size conflict.

## Q1. Conflicts and resolutions

1. **Population.** A uses the full test split, rational answers only, subject-balanced (A §2). C ruling 7 asks "full split vs MATH-500" and leaves MATH-500's Level-1 count open.
   - I verified MATH-500's Level-1 count at 43, so MATH-500 cannot supply n = 64. Adopt A's population.
   - Add the eligibility filter and the subject balancing to C's AP-5M `selection_scope`, and put the falling retention (0.872 to 0.782) into its claim ceiling. Right now the population is described only as a "frozen hashed problem set".
2. **n per level.** A and C both use n ∈ {64, 128}. C picks 128 "if it fits the registered window budget", but neither packet gives the budget number. The registration must state it as a number (arithmetic in Q5).
3. **Pilot composition.** A takes 16 items in total (4 at Level 5, 3 at each other level). B R4 wants 16 per level. A 3-item sample cannot give B's p95 token count or a cap.
   - Adopt 16 per level (80 items). A's `pilot_key` rule carries over, but its pilot reference hash changes.
   - Run it on the bench (see above).
4. **Truncation.** A §3 and C §3 treat a capped attempt as truncated even when a boxed answer parses. B §2 says "a capped item *without a parseable answer*", which is the GSM8K rule (`benchmark_import.py:951-953`, confirmed). Adopt A/C. Thinking traces contain intermediate answers.
5. **Cap and cap-bound threshold.** B and C both use 20%. Only B has a physical ceiling: cap × s/token + prefill ≤ 450 s. Unify into one rule per arm: cap = min(the rung of C's cap ladder that covers the Level-5 1.7B pilot p95, B's ceiling).
6. **Numerator.** B's level window is contiguous same-level items within an envelope. C's block requires "membership identical across models". Because B packs more of the 1.7B's sub-blocks into each envelope, level windows differ between the two models.
   - Make the energy block the **sub-block**. Its edges are item edges, so the extra error is about 2 J per edge (B §2).
   - B also contradicts itself: sub-block size is "per (model, arm)", yet the slices must be "the same … for both models". Make the sub-block size per arm only.
7. **Blocks vs L2's n >= 5.** C requires at least 5 blocks spread over at least 5 envelopes per cell. B's packer is first-fit with no spreading rule.
   - Add a constraint that no two blocks of the same cell share an envelope. Envelope j gets block j of each level if it fits.
   - This is cheap. At n = 64 in thinking-off, blocks are about 13 items; the 1.7B needs 5 envelopes and the 8B about 9, roughly 14 in total, or 1.2 windows.
   - C also says "strict-valid bundles". Replace that with "strict-valid scored envelope" under B's exclusion list, as B §6.2 already asks.
8. **Holm family.** C has two families (thinking-on and thinking-off, m = 5 each); B names one "Holm family". Adopt C.
   - The affine ladder keeps its own AP-5 family.
   - C's Terms define L\* from raw 95% intervals, while §3 decides with Holm. Define the crossover only on Holm-significant directions.
9. **Where scoring runs.** A §6 names "B's night kind" as the scorer's call site. B §1.1 and §4 score at harvest.
   - Score at the desk in `scored_reduce`. The night writes raw rows only.
   - If the courier shows provisional accuracy, it calls the same pure function after the last recorder stop.
10. **Thinking-mode decoding.** A R4 and B R3 lean greedy. C writes "greedy" into its Terms and estimand. If Q3 is adopted, C's definition of an attempt must change.
11. **Publication vs binding.** Under A R1(b), full manifests live in an untracked custody path. B's scored manifest pins suite-manifest digests as tracked files.
    - Bind the untracked full manifests the way weights are bound: the registration pins their sha256, and the chain re-verifies them before the settle (B §3 already does this for weights).
12. **Gross vs net.** D-045.7 says "Per-item/block/level energies are GROSS-only" (`decision_log.md:2618-2619`). B R2 reports net joules as a peer number.
    - Keep gross as the only energy number.
    - Report the idle reference as a covariate, not as a net energy.

## Q2. Gaps before a sizing pilot can be armed

- **Decoding path.** A seeded sampler in the adapter, plus a bench determinism probe for greedy and for seeded sampling on both models. B's overrun re-run (§2) assumes "greedy reproduces the same tokens"; nobody has tested that.
- **Thinking-on pinset and panel entry.** The panel pins only thinking-off (`configs/model_panels/qwen3_4bit.json:24-26, 57-59, 73-81`).
  - Weights for both models are already on disk (`/Users/edr/jw_models/mlx-community/Qwen3-{1.7B,8B}-4bit`) and pinned by revision, so nothing needs downloading.
- **The registration packet itself (synthesis item 3).** No packet drafts it: the n formula with the window-budget number, the cap ladder values, bootstrap B and seed, the energy rail, and the floor class for sub-block windows (C's floor gate cites `floor_abs_j`/`floor_cmp_j`, which exist only as P2-015-pending for level windows, `analysis_plans.md:273`).
- **Estimator code.** B's `scored_reduce` computes J/correct and the three factors. Nothing implements C's paired bootstrap, instrument widening, Holm step or merge order.
- **The affine-ladder leg.** Synthesis item 3 says "both ladders". No packet covers it, and AP-5 still requires its envelope smoke gate (`analysis_plans.md:270`). Either add it or explicitly defer it by ruling.
- **Audit tooling and protocol** for A's blind audit (sampling code, labelling seat, Wilson rates).
- **Figure and table code** on `paper_rendering.py` (synthesis item 8).
- **Overrun tail.** B voids a sub-block after two overruns (`not_estimable`), which drops long items: the bias B itself warns about. Instead, re-queue the sub-block as single-item envelopes. With the cap under B's ceiling, one item always fits in an envelope alone.

## Q3. Greedy decoding in thinking mode

**How serious it is.** A greedy repetition loop runs to the cap. That makes the attempt truncated, and so incorrect, and it is the most expensive attempt possible. The smaller 1.7B is the more likely to loop. So greedy can manufacture exactly the crossover the headline looks for: the 1.7B's J/correct inflates at high levels for a reason that comes from the decoding rule, not from the model as it is meant to run. The model card explicitly says not to decode this way, so a reviewer will attack it first.

The options:

| Option | Claim | Budget and work |
|---|---|---|
| (a) Greedy, with a cap and loop labels | Valid only "under greedy decoding". A crossover driven by loops is labelled but not removed. | No adapter change. Deterministic, so overrun re-runs are identical. |
| (b) Card sampling (T 0.6, top-p 0.95, top-k 20), seed per (item, model), one attempt | Matches deployed practice. The bootstrap over problems absorbs sampling noise; no repeats are needed for a population estimand. | Same attempt count. Probably fewer cap hits. Needs a claim-bearing adapter change under the full gate, plus a determinism proof (identical token ids on a re-run). |
| (c) Thinking-off primary | Avoids the warning, but by the synthesis prior it is probably a null headline. | Cheapest, about 1–2 windows at n = 64. |

**Recommend (b)**, with (a) as the registered fallback if the determinism probe fails. Keep thinking-off greedy: it is the existing pinned stack and comparable to Paper B. The bench pilot measures the greedy loop rate as a disclosed sensitivity. It costs no window time.

## Q4. Order of work

**Parallel now, no Ed ruling needed:**
1. B's PR A, the kind-table refactor (full gate).
2. A's importer core: receipts, eligibility, selection, scorer, golden pairs. It writes manifests to an untracked path; committing them waits on Ed's publication ruling (E1).
3. Thinking-on pinset.
4. The bench determinism probe, plus building the seeded sampler (merging it waits on E3).
5. Pure modules: the packer with the spread constraint, `scored_reduce`, C's estimator, and figure code on synthetic fixtures.
6. The AP-5M redraft folding in the Q1 fixes.

**Sequential after that:**
1. PR B, the scored kind.
2. B's bench dry run.
3. The bench token pilot. This needs the importer, the pilot-size ruling (M4) and the decoding decision (E3).
4. The registration packet.
5. Cold gate.
6. Shakedown night.
7. Mechanical sizing receipt.
8. Headline nights.

**Blocked on Ed:** committing manifests (E1), merging AP-5M (E2), and the registration and any arm (E2, E3).

## Q5. Consolidated rulings

**Genuinely Ed's:**
- **E1. Publishing the problem text (A R1).** Recommend (b): commit hashes only. PRM800K's MIT licence covers OpenAI's data, and I doubt it can license AoPS's problem text (my inference).
- **E2. Adopting AP-5M and the D-166 addendum (C 1).** This is claim policy. Recommend a sibling row.
- **E3. Headline scope: thinking-on primary with the Q3 decoding.** Recommend Q3 (b) with the (a) fallback.

**Magistrate or cold gate:**
- **M1. Population (A R2, C 7):** full split, rational answers only, subject-balanced, retention disclosed.
- **M2. Capped counts as truncated (A, C 5).**
- **M3. Caps (A R6, C 6):** the unified cap rule from Q1.5; 20% cap-bound threshold.
- **M4. Pilot size (B R4):** 16 per level, bench token pilot plus a shakedown night. Arithmetic: 80 thinking-on items at about 146 s each (8B plus 1.7B, planning) is about 11,700 s, or 2.5 windows if run at night; on the bench it costs zero windows.
- **M5. What the pilot may set:** the union of caps, sub-block size, pitch, n, and A R3's scorer additions (additions only, with a scorer-id bump).
- **M6. One registration with a sizing formula and a mechanical receipt (B R5, option 2),** as synthesis item 3 asks.
- **M7. Holm (C 2):** two families of m = 5, crossover defined on Holm decisions.
- **M8. L2's n >= 5 (C 3):** sub-block blocks, at least 5 per cell, in at least 5 distinct envelopes. No change to the claims ladder.
- **M9. J/token stays descriptive (C 4).**
- **M10. Gross energy only (B R2),** per D-045.7.
- **M11–M16 (B R1, R6–R10):** idle collector plus a model worker as the route; re-queue within the same night if budget allows, then single-item envelopes; the rail must match Paper B's floors; floors carry over only on matching identity pins; D-182 successor rules as B asks; never mix arms in one night.
- **M17. Auditor (A R5):** two blind seats from different model families. Ed's 20 hand-labelled rows are optional, since they cost Ed's time.
- **M18. C 8 and 9:** the residual fit stays exploratory; claims say "MATH level".

**n arithmetic (for the magistrate).**
- *Interval width.* Take accuracy 0.25 for the 1.7B and 0.625 for the 8B (C's worked example). The log-scale standard error of R_L is about 0.237 at n = 64 (95% interval ×/÷ 1.59) and 0.168 at n = 128 (×/÷ 1.39), before token variance, which widens it further. C's example R_5 = 1.02 would stay unresolved at either n.
- *Window cost.* At 12 × 480 s per window and 0.8 utilisation, n = 64 needs about 10 thinking-on windows plus 1–2 thinking-off windows. This assumes 8 h of 8B decode (synthesis) and my assumed 5 h for the 1.7B. n = 128 needs about 20 + 3.
- *Days.* At 4–5 windows per day, that is about 3 days vs about 5–6 days. The deadline is end of November, so recommend 128 if the pilot confirms the rates.

## Q6. Fact checks

1. **A, answers-first §2, is off by one.** The data has **5,001** rows tagged `test/`: one id appears twice, so there are 4,999 unique problems (I checked the per-level counts too). "5,000 − 2 − 954 − 5" gives 4,039, not 4,040. The counts table and the hashes use the correct 4,999 base; only the sentence is wrong.
2. **A's sha256 pins match both downloaded files.** MATH-500's per-level counts are 43/90/105/128/134, which closes C's ruling 7.
3. **B's "reuse the adapter unchanged" holds only for greedy decoding** (`mlx_runtime.py:984-1009`).
4. **B's truncation sentence restates the GSM8K code** (`benchmark_import.py:951-953`), and so conflicts with A and C.
5. **B's net joules conflict with D-045.7** (`decision_log.md:2618-2619`).
6. **`<think>` and `</think>` are `special: false` in both local tokenizers.** A checked only the 8B.
7. **The greedy warning cannot be checked locally.** The local mlx-community READMEs have no sampling text, so A R4 and B R3 rest on the upstream Qwen card. The registration should cite that card's revision.
8. **These citations check out:**
   - B: `night_gate.py:149-161`, `run_night.py:581-596`, `analysis_plans.md:268`, and the palindrome arithmetic.
   - C: `analysis_plans.md:265/270/276`, `claims_ladder.md:63`, and the worked-example rates (`research_question_bank.md:1615-1616`: 47/512 and 192/512 J/token, which are Qwen2.5 stand-ins).

Files read: the three packets and the brief under `/Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/`. Background, synthesis and contract files are under `/Users/edr/code/wt-1d3796d5-consult/`.