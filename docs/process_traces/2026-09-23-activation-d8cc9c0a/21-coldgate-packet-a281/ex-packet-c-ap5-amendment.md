# 10 — Headline packet C: D-166/AP-5 amendment for MATH author levels (DRAFT)

Opus 5.5 design seat, read-only at `main 313efcca`. DRAFT for the cold Fable gate and Ed; the magistrate cannot
ratify it. Planning figures are unmeasured.

## Answers first

- **Blocked today:** AP-5 covers only the synthetic affine ladder and requires level-invariant answer lengths; MATH
  has neither. Two question-bank rows say MATH needs "a prospective policy ruling"; this drafts it.
- **Shape:** a sibling row **AP-5M** plus a dated D-166 addendum. AP-5M inherits both bans, the contamination caveat,
  correctness quarantine, the ≥3-correct guard and malformed-as-incorrect. It replaces AP-5's level-invariant-length
  gate with a mandatory three-factor decomposition: for MATH, length change is measured, not a contaminant.
- **Decision rule:** per level, R_L with a paired problem bootstrap (energy measured per block, never per problem),
  widened by the instrument bound; Holm over 5 levels; thinking-on primary, thinking-off a secondary family.
- **Two conflicts need rulings:** claims-ladder L2 "n ≥ 5 per condition" (met by ≥ 5 bundles per cell) and D-045.7's
  ban on token-normalized claim metrics (met by keeping J/token descriptive).

## 1. Current text and why it forbids the comparison

| Where | Current text (verbatim) | Effect on the headline |
|---|---|---|
| `docs/contracts/analysis_plans.md:262` | "AP-5 / C5-1.9 controlled-envelope ladder (C-014/C-004)." | Consumer is the affine ladder only. |
| `analysis_plans.md:265` | "Frozen affine-ladder levels, item set, scorer version, and merge policy named for the C5-1.9 campaign before execution." | MATH levels are in no row's selection scope; `:11-12` "A comparison that cannot fill the fields below is not eligible for L2/L3 wording." |
| `analysis_plans.md:270` + `docs/research_question_bank.md:104-106` | "envelope-validation smoke gate must pass before any scored campaign"; the gate "must show level-invariant emitted-token and stop-reason distributions" | MATH answers lengthen with level by nature; the gate fails by design. |
| `analysis_plans.md:276` | "Forbidden upgrade: no intelligence-per-joule or "difficulty causes energy" claim." | Kept unchanged. |
| `joulewise/benchmark_import.py:87-89` | "D-166/C5-1.9/AP-5: source difficulty is unlabelled; correctness remains quarantined and licenses no difficulty or capability claim" | True for GSM8K; reused for MATH it forbids any per-level statement. |
| `docs/decision_log.md:212` (D-166) | "accuracy a set property under AP-5/C5-1.9 quarantine — contamination unmitigable" | Licenses scoring for the GSM8K `_v6` leg only. |
| `research_question_bank.md:1452-1453` | "Extending AP-5 to this source requires a prospective policy ruling; D-041 alone licenses only energy beside external scores, not this ratio." | Explicit block (repeated at `:1737-1738`). |
| `research_question_bank.md:453-455` (C5-I.2) | "Ceiling L1 association unless preplanned repeated-bundle L2; never "difficulty causes energy."" | L2 needs a preplanned design; AP-5M is that design. |

## 2. Proposed amendment text (paste-ready)

### 2a. Decision-log addendum (append after the D-166 dated addendum of 2026-09-04; add "(MATH levels: see 2026-09-23 addendum)" to the index row at `decision_log.md:212`)

> ## D-166 dated addendum (2026-09-23, DRAFT pending cold gate + Ed): MATH author levels as a stratum for energy per correct answer
>
> **Forcing problem.** The headline question is how the energy spent per correct answer changes with problem
> difficulty and model size. AP-5 was written for a synthetic ladder built to keep answer length fixed, so it cannot
> host a benchmark whose answers lengthen on harder problems.
>
> **Terms.** A *level* is the label 1–5 that the MATH dataset's authors (Hendrycks et al., 2021) attached to each
> problem when they published it; it is fixed before any model sees the problem and is never computed from a model's
> success rate or answer length. An *attempt* is one greedy generation for one problem by one model, stopped by the
> model's end token or by the *output cap* (a fixed maximum of generated tokens); an attempt that reaches the cap is
> *truncated*. An attempt is *correct* only when the pinned scorer finds a final answer equal to the reference;
> truncated and malformed attempts are incorrect. A *cell* is one (thinking arm, model, level); both models see the same
> problems. A *block* is a run of consecutive attempts inside one capture bundle, bracketed by markers; its *gross block
> energy* is the joules recorded between those markers, with no idle subtraction and no envelope padding.
> *J/correct* of a cell is its summed gross block energy divided by its number of correct attempts. It factors exactly
> as J/correct = J/token × tokens/attempt ÷ accuracy (J/token = cell energy ÷ cell generated tokens, same Qwen3
> tokenizer for both models; tokens/attempt = generated tokens ÷ n; accuracy = correct ÷ n). *R_L* = J/correct(8B) ÷
> J/correct(1.7B) at level L in one arm; R_L < 1 means the 8B spent fewer joules per correct answer on that level's
> problems. The *crossover level L\** is the lowest level whose R_L interval lies wholly below 1, provided some lower
> level's interval lies wholly above 1.
>
> **Worked example (1.5B/7B planning figures as stand-ins, research_question_bank.md:1615-1616).** Level 5, n = 64: the 1.7B spends
> 0.092 J/token × 4,000 tokens/attempt and gets 16 correct (25%): 0.092 × 4,000 ÷ 0.25 = 1,472 J/correct. The 8B
> spends 0.375 J/token × 2,500 tokens and gets 40 correct (62.5%): 1,500 J/correct. R_5 = 1.02. The 8B needed an
> accuracy ratio of (0.375/0.092) × (2,500/4,000) = 2.55 to break even and achieved 2.50.
>
> **Ruling.** (1) MATH levels may stratify energy-per-correct comparisons under analysis plan AP-5M. (2) Every AP-5
> prohibition carries over unchanged: no intelligence-per-joule claim, no "difficulty causes energy" claim; accuracy is a
> property of the pinned frozen problem set, never a capability claim, because Qwen3's pre-training contamination by
> MATH is unmitigable; correctness remains a quarantined annotation (C-004) used only as the J/correct denominator.
> (3) The three factors are always reported beside J/correct and gross block energy is co-displayed
> (`token_normalization.md`). (4) J/token and tokens/attempt are descriptive factors, never claim-bearing contrasts
> (D-045.7 unchanged). (5) The GSM8K constants and manifest keep their text; the MATH importer carries its own.

### 2b. `analysis_plans.md` edits

AP-5 `:262` append: "Amendment 2026-09-23 (D-166 addendum): MATH author-level strata are AP-5M, which inherits this
row's forbidden upgrade and quarantine." Registry `:63-67` append "MATH level energy-per-correct" to the list of
separate families.

New row, inserted after AP-5:

> ### AP-5M: MATH author-level energy per correct answer, two model sizes
>
> | Field | Value |
> |---|---|
> | Plan ID / RQ consumer | AP-5M / RQ-NEXT-EPCA-LEVELS headline (D-166 addendum 2026-09-23). |
> | family_id | FAM-MATHLVL-EPC-THINKON (primary); FAM-MATHLVL-EPC-THINKOFF (secondary). |
> | claim_role | Thinking-on R_L: primary. Thinking-off R_L: secondary; it cannot carry the crossover headline. |
> | selection_scope | Qwen3 1.7B and 8B (pinned 4-bit MLX weights), two thinking arms, MATH levels 1–5, frozen hashed problem set (same problems for both models), pinned prompt template, scorer, extractor and caps. Nothing else is searched. |
> | multiplicity_rule | Holm within each family, α = 0.05 two-sided, m = 5 fixed (one hypothesis R_L = 1 per level; a merged cell tests one hypothesis and m stays 5). Holm: sort p ascending; reject the k-th while p(k) ≤ α/(m−k+1); stop at the first failure. |
> | Metric + exact window class | Gross block energy summed per cell; J/correct; the three factors; truncated/malformed counts. Never envelope energy including idle padding. |
> | Unit of analysis + dependence structure | Problem for correctness and tokens (distinct problems, D-047.3); block for energy. Each cell's n problems are split by SHA order into K ≥ 5 blocks spread over ≥ 5 distinct strict-valid bundles; block membership identical across models. No problem window is an energy replicate. |
> | Estimator/formula | R_L with the paired bootstrap interval of packet §3. |
> | Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only; a contaminated bundle is re-run under the replacement rule, not waived. Truncated = incorrect; malformed = incorrect (D-047.6). |
> | Order/blocking/covariates | Level order rotated across bundles by a pre-declared order; model order alternated A-B-B-A across bundles. |
> | Floor gate | Every block window above `max(floor_abs_j, floor_cmp_j)` for its class. |
> | MDE/n sizing + predeclared top-up rule | n per level ∈ {64, 128}, equal across levels, models and arms, set by the pilot rule of §3 and frozen before any test problem runs (D-062). No top-up. |
> | Denominator provenance requirement | Runtime-observed generated tokens including thinking tokens; exact scorer output; ≥ 3 correct per cell else the fixed merge order, else `not estimable`. |
> | Holdout cells (L3 only) | not applicable. |
> | Claim ceiling + exact forbidden upgrade | Ceiling L2 on this frozen set, stack and caps. Forbidden: intelligence-per-joule; "difficulty causes energy"; any capability, ranking or routing claim; extrapolation beyond levels 1–5, these two models, or these caps. |
> | Disqualifiers + not-resolvable conditions | Below-floor blocks, fewer than 5 bundles per cell, a failed guard after all merges (`not estimable`); any R_L interval spanning 1 prints `not resolved`. |
> | Linked manifests/bundle hashes | pending post-execution. |

## 3. Pre-registered decision rule

**Estimand.** R_L per level per arm on the frozen set (M3 Max, pinned MLX 4-bit weights, greedy decoding, pinned
caps).

**Interval: paired, level-stratified bootstrap over problems, block-level energy.** (1) For each block b, J/token_b =
gross block energy ÷ block generated tokens. (2) Each attempt i is assigned ê_i = J/token of its block × its tokens.
Energy remains a block measurement; problem windows are never read as energy. (3) Draw B = 20,000 resamples (seed pinned
in the registration). Each draws n problem indices with replacement within the level and applies the same indices to
both models, so the shared problems stay paired. Compute Σê ÷ Σcorrect per model and their ratio R*. (4) Instrument
widening: w = Σ_b (operative floor + `E_clock_anchor_shift_bound_j`) ÷ cell energy, per model. The low-side value is
R*·(1−w₈)/(1+w₁.₇) and the high-side value is R*·(1+w₈)/(1−w₁.₇). (5) p_below = (1 + #{high-side R* ≥ 1 or
undefined}) ÷ (B+1); p_above likewise with low-side R* ≤ 1; p_L = min(1, 2·min). A resample with zero correct for one
model gives R* = 0 or +∞; zero for both is undefined and counts against both directions. (6) The reported interval runs
from the 2.5th percentile of the low-side values to the 97.5th percentile of the high-side values.

**Why this method.** R_L is a ratio of two ratios whose parts are correlated within a model (same problems) and
across models (paired problems). The delta method gives a symmetric interval on a skewed, zero-bounded quantity and
fails at small correct counts (the guard admits 3). Fieller covers one ratio of two jointly normal quantities, not this
paired four-quantity ratio. The bootstrap needs neither assumption, keeps the pairing, and is rebuildable from this
text. Instrument error is a deterministic widening: ≈ 1 J floor per window against hundreds of joules per block
(`research_question_bank.md:1603-1604`), while binomial spread (±12 % at n = 64) dominates.

**Interval above/below 1.** Level L is *below 1* when Holm rejects H_L and p_below < p_above, and *above 1* in the
mirror case. Otherwise it is *not resolved*: inconclusive, not a null (synthesis item 9).

**Fixed n and pilot.** A 16-problem sizing pilot, disjoint from test problems, never reported as a result, may set only
(a) problems per bundle, (b) each arm's cap from a declared ladder, (c) n = 128 if the pilot-projected capture for
the arm at 128 fits the registered window budget, else 64. It never sets which levels, models, arms, families or
estimands are reported (D-062). All five levels are always reported.

**Minimum correct and merge order.** Each cell needs ≥ 3 correct (AP-5 guard; an observed count, a deterministic
property of the set). If either model fails at a level in an arm, that level merges for both models, in that arm only,
in this fixed order: 5 into 4 ("4–5"), then into 3; 1 into 2 ("1–2"), then into 3. Merges depend only on correct
counts, never on energy or R. If no valid merge remains, the result is `not estimable`.

**Truncation.** An attempt that reaches the cap is incorrect even if a boxed answer parses, because thinking traces
hold intermediate answers. This deliberately differs from GSM8K (`benchmark_import.py:950-953`).

**Cap-bound label.** A cell with > 20 % truncated attempts is *cap-bound*. The label prints beside every number
from that cell. If L\* rests on a cap-bound cell, the crossover sentence must state the cap ("at an N-token cap").

**Null wording.** All levels above 1: "On this frozen MATH subset and stack, Qwen3-1.7B spent fewer joules per correct
answer than Qwen3-8B at every level 1–5; no crossover within the tested levels." All below 1: the mirror. Non-monotone:
per-level results, no crossover claimed.

**Arm ordering: agree with synthesis item 9.** A crossover, if any, is expected where the 1.7B's long thinking traces
cost tokens and cap hits; thinking-off is expected not to cross (8B ≈ 3–4× per token against ≤ 2× accuracy,
planning). Choosing the plausible arm as primary before data is legitimate; thinking-off is the decomposition baseline. Per level, report the accuracy ratio the 8B needs to break even:
(J/token₈/J/token₁.₇) × (tokens₈/tokens₁.₇).

## 4. Claim language

| Allowed | Banned |
|---|---|
| Per-level R_L with interval, cap and set named. *"On our frozen MATH Level 5 problems (thinking on, 8,192-token cap), Qwen3-8B used 0.6× [0.4, 0.9] the joules per correct answer of Qwen3-1.7B."* | Causal difficulty. *"Harder problems make the model draw more energy."* |
| Decomposition. *"Of the Level-5 gap, the token ratio contributes X and the accuracy ratio Y."* | Intelligence per joule or capability. *"The 8B delivers more intelligence per joule"*; *"the 8B solves 62 % of Level-5 MATH."* |
| Crossover within tested levels. *"The cheaper model per correct answer changed from 1.7B to 8B at MATH Level 4 on this set."* | Routing or general advice. *"Route hard prompts to bigger models to save energy."* |
| Null. *"No crossover within levels 1–5."* | Extrapolated crossover. *"Beyond Level 5 the 8B wins by more."* |

## 5. What this does NOT license

Capability or leaderboard claims; rankings beyond this pair and set; routing policies; other caps, quantizations,
devices or benchmarks; per-problem energy; confirmatory J/token or tokens/attempt contrasts; mechanism claims from the
residual fit E = fixed + a·p + b·d (exploratory unless registered); thinking-off results as headline; pilot outcomes;
any change to AP-5's affine-ladder rules.

## 6. Consistency check (strings that become false or need a matching change)

| File:line | Needed change |
|---|---|
| `docs/contracts/analysis_plans.md:262`, `:63-67` | Pointer and family list (§2b). |
| `analysis_plans.md:276` | None; AP-5M inherits it. |
| `docs/decision_log.md:212` | Index pointer to the addendum. |
| `docs/decision_log.md:2619` (D-045.7) | None if J/token stays descriptive; otherwise needs an amendment (open ruling 4). |
| `docs/contracts/claims_ladder.md:63` (L2 n ≥ 5 per condition) | Met by the ≥ 5-bundle rule; no text change. |
| `docs/contracts/token_normalization.md:30-40` | None; its co-display rule binds AP-5M. |
| `docs/research_question_bank.md:1728-1738` | "needs a prospective policy ruling" → "ruled: AP-5M"; design (8B/32B/30B-A3B, 32/level) → 1.7B/8B, n ∈ {64,128}. |
| `research_question_bank.md:1449-1453`, `:1802` | RQ-D-A10's policy prerequisite satisfied by AP-5M; its large-model design is unchanged. |
| `research_question_bank.md:452-455` (C5-I.2) | Name AP-5M as the preplanned L2 design. |
| `research_question_bank.md:96-109`, `:723-730` | Note: controlled-envelope shape stays the ladder's; MATH uses AP-5M. |
| `research_question_bank.md:114-118`, `:314-319`, `:436`, `:443` | None. |
| `docs/process/research_plan_2026-09-16.md:150` | "32 items/level", "AP-5 policy ruling extended" → AP-5M (slot move is separate). |
| `docs/phase_2/suite_implementation_research.md:623` | Per-bundle energy_per_correct; AP-5M pools per cell. Pointer. |
| `joulewise/benchmark_import.py:79-89`, `:622-629` | Unchanged for GSM8K. The MATH importer needs its own constants: difficulty `{axis:"math_author_level", value:1–5, scale:"ordinal", label:"Level L", source:"hendrycks_math_2021", quarantine_note:"D-166 add. 2026-09-23/AP-5M: author label; stratifies, never causes; accuracy is a set property"}`. `joulewise/suite.py:693-720` accepts this without a schema change. |
| `benchmark_import.py:950-953` | The MATH scorer must implement capped = incorrect (differs by design). |
| `joulewise/workloads.py:192-202`, `joulewise/gensuite/__init__.py:1340-1348`, `configs/suite_manifests/gsm8k_scored_v6_qwen3.json`, `docs/axi-handoff.md:232` | None. |

## 7. Open rulings for Ed

1. A sibling AP-5M row (recommended; AP-5's length-invariance design stays intact) vs rewriting AP-5 in place.
2. Two Holm families with m = 5 each (recommended) vs one family with m = 10 across arms (stricter, less power).
3. ≥ 5 bundles per cell (meets L2 without repeats; fixes a bundle floor) vs amending the claims ladder for
   problem-dominated estimands (a process change).
4. J/token as descriptive only (recommended) vs amending D-045.7 to make the factors claim-bearing.
5. Capped = incorrect even when an answer parses (recommended) vs following the GSM8K precedent.
6. Cap-bound threshold of 20 % and the cap ladder values per arm.
7. Source set: the full MATH test split vs MATH-500. MATH-500's Level-1 count is unverified; if it is below 64, it
   cannot supply n = 64. Subject balancing is left to the importer packet.
8. The residual mechanism fit: exploratory (recommended) vs registered as secondary.
9. Wording: claims say "MATH level"; "difficulty" appears only in the sentence that defines it (recommended).
