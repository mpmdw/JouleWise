# Headline path — integration synthesis (magistrate, Opus 5.5)

Inputs: three blind design packets, A (08, MATH importer), B (09, scored-campaign night kind) and C (10, D-166/AP-5 amendment draft). Two blind integration consults followed: Sol 6.0 high (17) and Opus 5.5 (18). This record makes the integration decision the throughput synthesis asks for (item 2: "one integration adjudication"). It does not ratify any claim policy. AP-5M and the D-166 addendum remain drafts for the cold gate and for Ed.

## 1. Settled here (both integration seats agree; magistrate authority, cold gate at registration)

**Terms used below.** The *population* is the set of MATH test problems eligible to be drawn. A *cell* is one (model, thinking arm, level) combination. A *block* is a fixed slice of problems whose energy is measured as one unit. An *envelope* is one fixed-length power capture. *Holm* is Holm's step-down correction for testing several levels at once. *Cap* is the maximum number of generated tokens per attempt.

| # | Question | Decision | Why |
|---|---|---|---|
| M1 | Population | The full MATH test split, 5,000 rows = `test.jsonl` plus the `test/`-tagged rows of `train.jsonl` at `openai/prm800k` `7ecc7947`. Those rows hold 5,001 lines and 4,999 unique ids. **Both** rows of the duplicated id are excluded. Rational-valued answers only. Balanced by subject. Retention per level is disclosed (0.872 at Level 1 falling to 0.782 at Level 5). | MATH-500 has only 43 Level-1 items, so it cannot supply 64 per level (A; verified by Opus). Packet A's sentence "4,040" is an arithmetic slip against its own table. The implementation recomputes the count and every reference hash. |
| M2 | Capped attempts | Every attempt that hits the cap counts as incorrect, even when a boxed answer parses. The parsed text is kept for a sensitivity analysis. | Thinking traces contain intermediate boxed answers. This deliberately differs from the GSM8K scorer (`benchmark_import.py:950-953`). |
| M3 | Cap-bound label | A cell with more than 20 % capped attempts is labelled cap-bound. The cap per arm is the smaller of two values: the cap-ladder rung that covers the pilot's Level-5 1.7B 95th-percentile length, and B's physical ceiling (cap × s/token + prefill ≤ 450 s). | All three packets use 20 %; only B has a physical ceiling. |
| M4 | Sizing pilot | 16 problems per level (80), disjoint from the test items. It runs as a **bench token pilot** between windows (token counts, cap hits, loop rate, scorer audit, rough s/token), followed by one short shakedown night for envelope timing. | Three problems per level cannot set a 95th percentile. Under a fixed decoding rule, token counts do not depend on the power capture, so the pilot costs no measurement windows (Opus 18). |
| M5 | What the pilot may set | Caps, block size, envelope pitch, n per level (64 or 128, by a registered rule), and scorer additions (additions only, with a scorer-id bump). **Never** which levels are reported (D-062). | |
| M6 | Registrations | One headline registration with a sizing formula, plus a mechanical sizing receipt from the pilot (synthesis item 3). | One cold gate instead of several. |
| M7 | Energy numerator | Gross energy between the outer item edges of each block. Net-of-idle is never a peer number; the idle reference is a covariate. | D-045.7 (`decision_log.md:2618-2619`): block and level energies are gross only. |
| M8 | Claims-ladder L2 (n ≥ 5 per condition) | Each cell is spread over at least 5 blocks in at least 5 distinct envelopes. The packer carries a no-two-blocks-of-a-cell-in-one-envelope constraint. Block membership is identical across the two models, and block size is set per arm, not per model. | This meets `claims_ladder.md:63` without amending the ladder. Planning cost: about 14 envelopes (≈ 1.2 windows) for thinking-off at n = 64. |
| M9 | Inference | Bootstrap over paired problems **and** over capture blocks (block-aware), widened by the instrument's floor and anchor bounds. Holm is applied in two families of m = 5 (thinking-on primary; thinking-off secondary and unable to carry the headline). The crossover level L\* is defined only on Holm-significant directions. | Sol F4 (C's problem-only bootstrap treats item energies as fixed); Opus Q1.8 (C defines L\* from raw intervals). |
| M10 | J/token | Descriptive only. | D-045.7 bans token-normalized claim metrics. |
| M11 | Where scoring runs | At the desk, in a pure reducer over immutable per-item rows written during the night. Any courier count is labelled provisional. | |
| M12 | Overruns | A block that overruns is re-queued once within the night. It is then re-queued as single-problem envelopes, never dropped. | B's "void after two overruns" would drop exactly the long items. |
| M13 | Other operational points from B | Idle collector plus a separate model worker; one thinking arm per night; the energy rail and floor identity must match Paper B's pins or the floors are re-measured. | |

## 2. Decisions for Ed (decision brief emailed; see §4)

- **E1 — publishing the problem text.** Recommendation: commit hashes and ids only; the problem text stays in an untracked custody path bound by sha256. PRM800K's MIT licence covers OpenAI's data, and it is doubtful that it licenses the Art of Problem Solving problem text (Hugging Face took down its copy after an AoPS copyright notice in January 2025).
- **E2 — adopting AP-5M and the D-166 addendum** (packet C, amended by M7-M10). This is claim policy, so it goes to the cold gate and then to Ed.
- **E3 — decoding and the primary arm.** Qwen3's model card advises against greedy decoding in thinking mode (repetition loops). A loop runs to the cap, counts as incorrect, and is the most expensive attempt. That can manufacture a crossover in the direction the headline looks for. Options: (a) greedy, labelled "under greedy decoding"; (b) the card's sampling settings (temperature 0.6, top-p 0.95, top-k 20), one pinned seed per (problem, model), one attempt, the same attempt count as greedy; (c) thinking-off as primary, which avoids the problem but most likely yields a null headline. Both integration seats recommend (b), with (a) as the registered fallback if a bench probe shows seeded MLX sampling does not reproduce the same tokens. The magistrate concurs.
- **E4 — n per level (budget).** Planning figures (accuracy 0.25 for the 1.7B and 0.625 for the 8B at the hardest level): the 95 % interval on the energy-per-correct ratio is about ×/÷ 1.59 at n = 64 and ×/÷ 1.39 at n = 128, before token variance. That is about 12 windows (≈ 3 days at 4–5 windows/day) against about 23 windows (≈ 5–6 days). The deadline is end of November. Recommendation: 128 if the pilot confirms the rates. The registered rule decides mechanically from the pilot; Ed rules only on whether the budget ceiling is acceptable.

## 3. Order of work

**Starts now (no Ed ruling needed):**
1. MATH importer core: source receipts, eligibility, selection (pilot 16/level + test n ∈ {64, 128}), stdlib scorer and golden pairs. Manifests are written to an untracked path. Seat brief 20. Full claim-bearing gate.
2. Thinking-on rendering pinset for the model panel.
3. A bench determinism probe for greedy and for seeded sampling on both local models (after 1, or in parallel once a sampler exists).
4. After A277 merges (it owns `evidence_night.py` today): B's PR A, the kind-table refactor with no behaviour change.
5. Pure modules: packer with the M8 constraint, the scored reducer, the M9 estimator, and figure code on synthetic fixtures.
6. The AP-5M redraft folding in M7-M10, for the cold gate.

**Sequential:** B's PR B (the scored kind) → bench dry run → bench token pilot (needs E3) → registration packet → cold gate → shakedown night → sizing receipt → headline nights.

**Not covered by any packet, now lanes to register:** the affine-ladder leg (synthesis item 3 says "both ladders"; include it or defer it by ruling), audit tooling for the scorer audit, and figure/table code.

## 4. Scorecard (same packets)

Sol 6.0 (17): found the 5-bundle vs 2-sub-block conflict, the problem-only bootstrap gap, and packet A's arithmetic slip. Opus 5.5 (18): the same conflicts plus the bench-token-pilot restructure, the greedy-only adapter (`mlx_runtime.py:984-1009`), D-045.7 against net joules, block membership across models, the overrun-drop bias, and the n arithmetic. Both PASS. Opus was deeper on this packet; Sol's F4 inference point was the only one Opus missed.

## Addendum (15:50 PDT, same activation) — correction to M1

M1 and §1's reason column call packet A's 4,040 "an arithmetic slip". **That is wrong.** The importer seat (record 21) authenticated the pinned files and computed the population from them: 5,001 rows, 5,000 distinct ids before exclusion (one id appears twice), 4,999 singleton ids. Exclusions are both rows of the duplicated id (2), 954 non-rational references and 5 plain-comma references. That leaves **5,001 − 2 − 954 − 5 = 4,040 eligible**, with the reference self-check passing 4,040/4,040. Packet A misstated only its base (5,000 instead of 5,001 rows); its total and table were right. Both integration seats (17, 18) and this synthesis repeated the base error. The rule "exclude both rows of the duplicated id" stands.
