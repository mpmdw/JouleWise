# AP-5M v4 → proposed v5: final-text change ledger

This ledger identifies every v4 gate-final text T-1–T-28 and the operative K/S/row/addendum provisions affected by R-Q3. “V4 text” is the identifying operative phrase, copied exactly where quoted; the v4 file remains the archive of each full paragraph. “V5 text” names the replacement in `01-ap5m-draft-v5.md`, or says carried. An amended rule is proposed, not adopted. R-Q3 item numbers refer to the verbatim paragraph in v5 §0. E1 and O-21 are Ed's answers recorded in the interactive record §6. **HOLD** means the prior clause cannot govern the new cell until A291 contract v5 or the claim-gate redesign is ruled; it is not silently inherited.

| ID | V4 text / final effect | V5 text / disposition | Ruling item |
|---|---|---|---|
| T-1 | “Denominator guard, sparse, merge, group, pooled”; observed correct count ≥ 3 and merge sparse neighbouring levels. | HOLD merge as confirmatory: §6 preserves five level hypotheses; zero accuracy makes C undefined, reported not estimable. A council must rule any pooling sensitivity. | (6), (7) |
| T-2 | “Observed count of correct attempts ≥ 3 per model per level”; merge if fewer. | Accuracy n ≥ 128; display correct counts and uncertainty. Whether ≥ 3 remains a claim guard is OPEN; it cannot trigger v4's level merge. | (4), (6), (7) |
| T-3 | “one shakedown night per arm”; old `capped := generated_tokens ≥ cap_tokens[arm]`, stop reason and elapsed checks. | §2 requires a quiet-shape shakedown; §3 separates thinking-cap from answer-allowance hit; exact smoke predicates await A291 v5. | (1)–(5), (9) |
| T-4 | Block-window floor and anchor are separate; old floor tied to each v4 block. | §4 carries separate window floor and anchor roles; new split-sample estimate floor is added in §6, with 25G83 row prerequisite. | (5), (6); O-21 |
| T-5 | `u = s · Σ_w anchor_{j,w}` and point `s = 1` under a two-stage all-attempts bootstrap. | §5 retains per-window anchor widening, but split-sample propagation is OPEN for validated estimator. No `floor_j` is put into u. | (5), (6) |
| T-6 | “Every counted block window must exceed `floor_gate_j = max(floor_abs_j, floor_cmp_j)`”; estimate-level O-21 held for Ed. | §4 retains block-window refusal; §6 adds mandatory `|estimate| > F` at estimate level. | (5), (6); O-21 |
| T-7 | Percentile interval over v4 low/high R draws and point bounds. | §5 requires paired-bootstrap, anchor-widened bands for split accuracy/energy samples; exact draws and interval procedure OPEN to claim-gate redesign. | (5)–(7) |
| T-8 | “Holm”, m = 5 over tested merged groups in each thinking arm. | §6: one fixed five-level family at the pre-registered pair; no separate thinking-on/off families or confirmatory merged groups. | (1), (7) |
| T-9 | Flagged merged groups become NR and have one `(arm, level)` recapture. | §4 carries typed flags and bounded recapture principle; new cell key `(model, level, budget)` and exact recapture mapping HOLD for A291 v5. | (1), (5), (9) |
| T-10 | `max_gap = budget_j / (δ_upper · P)` per `(arm, level)`; shakedown drift estimate. | §4 retains balanced-position requirement; derived threshold and cell mapping HOLD for A291 v5 pilot/shakedown. | (1), (5), (9) |
| T-11 | “NE(`ceiling_violation`) first; otherwise NR” ordered v4 merged-group flags. | §6 keeps typed refusal before any direction; v4 group precedence HOLD because no confirmatory pooling is licensed. | (6), (7), (9) |
| T-12 | Linear within-night gross-block drift model over v4 per-arm parent blocks. | §4 carries need to balance captured model positions; budget-specific drift model and bound HOLD for A291 v5. | (1), (5), (9) |
| T-13 | “Retries and reschedules extend the same night”; `night_exhausted` typed terminal. | §4 carries this safety requirement for energy subsample; exact budget-cell roster and recapture HOLD for A291 v5. | (5), (9) |
| T-14 | “For every problem and model at most one attempt is counted”; problems with no counted attempt dropped from both models. | §3 has one counted accuracy outcome per `(problem, model, budget)` and explicit paired missingness; §4 requires matched energy replay. No silent deletion. | (1), (4)–(6) |
| T-15 | One recapture after a ceiling violation, then family crossover withheld. | §4 retains terminal evidence and a bounded recapture concept; `crossover_level` outcome removed; exact v5 status HOLD. | (1), (5), (7), (9) |
| T-16 | “The 10 %-retried trigger is not adopted.” | Carried unchanged: no 10% retry trigger is introduced by v5. | — |
| T-17 | A terminal ceiling violation makes group NE and withholds `crossover_level`. | §6 withholds affected level direction; cross-level crossover endpoint removed. | (7) |
| T-18 | Combined crossover sentence and gap-level disclosure. | §6 instead requires sentence naming registered budget pair, contrast direction, components, limits and flags. | (7) |
| T-19 | Idle reference reported, not used to adjust R; gross energy. | Carried unchanged in §4 for the measured subsample. | — |
| T-20 | Pilot chooses `n = 128` if capture fits budget, else `64`; old cap/number list. | §2: n ≥ 128 accuracy problems outside quiet windows, pilot may raise to 200; energy subsample size set by precision target; at most five budget rungs. | (1), (4), (5), (9) |
| T-21 | K1 deterministic eligible MATH population and draw; E1 publication pending. | §1 retains population/draw, now fixes public IDs and hashes only; test draw ≥ 128 per level, pilot disjoint. | (1), (4); E1 |
| T-22 | “An attempt is correct only when the scorer finds a match and the attempt is not capped.” | §3: correct iff a parseable final answer **inside A** matches the pinned scorer; a thinking-cap hit does not alone make it wrong. | (1), (3) |
| T-23 | 100 ms powermetrics CPU+GPU+ANE rail boundary and gross energy. | Carried in §4, subject to accepted 25G83 instrument identity and new window class. | (5); 25G83 gate |
| T-24 | Pilot/shakedown may set old `(arm, level)` timeout, δ and gap quantities and `n ∈ {64,128}`. | §2 allows feasibility and precision parameters only; n ≥ 128, budget ladder and pair frozen, no outcome selection. A291 v5 owns exact resource fields. | (1), (4), (5), (7), (9) |
| T-25 | Fixed sparse merge order and `merge_order`, `min_correct`, `holm_m` constants. | `holm_m = 5` carried; sparse-merge confirmatory machinery HOLD. V5 schema must pin its own constants and test them. | (6), (7), (9) |
| T-26 | K25 adds `night_exhausted` and recapture edges to A291 contract v4. | §4 requires A291 **contract v5** to install new budget-cell transitions and seal/reducer invariants before execution. | (1), (5), (9) |
| T-27 | K10 parent-first, problem-second bootstrap over all captured attempts. | §5 requires paired bootstrap over full accuracy cohort and measured subsample with parent/envelope clustering; implementation and power validation OPEN. | (4)–(7) |
| T-28 | Flagged constituents of merged groups carry `pooled_in`. | Confirmatory pooling removed; flags attach to budget-level cells and level contrast, mapping HOLD for redesigned estimator. | (1), (7), (9) |

## Other changed operative v4 texts

| ID | V4 text / final effect | V5 text / disposition | Ruling item |
|---|---|---|---|
| Row: estimand/selection | “thinking-on crossover level L*”; cells `(model, arm, level)`. | §§1,5–6: budget b crossed with model and level; `C_mLb`, `R_L(b)` and one registered-pair contrast per level. | (1), (6), (7) |
| Row: claim role | “Thinking-on R_L: primary. Thinking-off R_L: secondary”. | b = 0 is one candidate ladder rung; thinking budget is the variable; no primary/secondary arm families. | (1), (7) |
| Row: multiplicity | “Holm within each family, α = 0.05 two-sided, m = 5 fixed” with one family per arm. | §6: one five-level family on the registered budget pair. | (7) |
| Row: metric/capture/unit | “Gross block energy (K4) summed per cell; J/correct”; parent blocks are energy replicates, problems supply accuracy. | §§4–5: quiet directly measured energy subsample supplies mean gross J/attempt; ≥128 outside-quiet problems supply accuracy. | (4)–(6) |
| Row: MDE/n | “n per level ∈ {64, 128}” by budget. | §2: accuracy n ≥ 128, pilot may raise to 200; energy n chosen separately by pilot precision target. | (4), (5) |
| Row: floor | O-21 was open, so claim acceptance used Holm and interval only. | §6 adds estimate-level `|estimate| > F` beside Holm and anchor-widened interval; conversion to budget contrast OPEN. | (6), (7); O-21 |
| Row: disqualifiers/ceiling | `capped = incorrect`; ceiling violations withhold L*; cap-bound label >20%. | §3 scores answers inside A after forced close; §6 withholds affected contrast; cap-hit counts reported per cell. Old L* and cap-bound threshold are not adopted for new cells without ruling. | (1), (3), (7) |
| K1 | Pilot/test draw shared across both arms; publication E1 undecided. | §1: shared across models and budgets; IDs and SHA-256 hashes public, text in local custody. | (1), (4); E1 |
| K2 | Cap ladder and a fit-based 64/128 rule. | §2: thinking-budget ladder, at most five feasible rungs, n ≥ 128 or 200, separate subsample. | (1), (4), (5) |
| K3 | “Every attempt that hits the cap counts as incorrect, even when a boxed answer parses.” | §3: thinking-cap hit is an intervention; only accepted final answer inside A can score correct, with cap counts displayed. | (1), (3) |
| K4/K5/K6 | Gross block numerator, J/token descriptive, idle never numerator, balance positions. | Carried in §§4–5 for **direct measured subsample**; full-cell quotient and old drift grouping replaced. | (5), (6) |
| K7/K8/K12/K15/K22/K23/K25 | Five-parent/five-envelope spread and v4 arm/level scheduling, retries, drift and recapture. | §4 preserves safety invariants but exact `(model, level, budget)` implementation HOLD for A291 contract v5. | (1), (5), (9) |
| K9/K10/K11/K19 | Observed ≥3 guard, merged groups, parent/problem bootstrap, anchor bounds and constants. | §§5–6 retain Holm m=5 and separate anchor; estimator/draw/floor on split sample and any sparse handling OPEN. | (5)–(7) |
| K13/K14/K16/K17/K18/K21/K24 | Typed retry and terminal paths; pilot roster non-claim-ready; one counted attempt per problem/model; smoke by arm. | §§2–4 retain custody and refusal principles, pilot isolation and typed evidence; counted key includes budget and smoke uses new energy shape. Exact mechanics HOLD A291 v5. | (1), (3)–(5), (9) |
| K20 | Prohibits wider capability/routing claims; example allowed a crossover sentence. | §6 retains prohibitions and forbids `optimal budget`; removes crossover example as confirmatory output. | (7) |
| S0–S11 | Group patterns, sparse merges, statuses and exact 25-pattern crossover table yield L*. | §6 replaces confirmatory outcome with a registered budget-pair sign at each level; no cross-level L* decision table. Typed refusals remain required. | (7) |
| D-166 addendum (1)–(9) | MATH stratification with thinking-on headline, fixed cap, v4 measured-all energy and supported crossover. | §8 proposes MATH stratification under budget experiment and split direct energy; old addendum cannot be installed unchanged. | (1)–(9) |
| Open items O-17–O-21 | E2 adoption, E3 decoding, E4 capture budget, E1 text, O-21 floor were open. | E3 fixed by (2), E4 rule by (4)–(5), E1 IDs/hashes only, O-21 YES; E2 awaits unanimous council. | (2), (4), (5), (9); E1/O-21 |

The unchanged v4 source-population eligibility, gross rail boundary, strict-valid custody, idle-reference status, pilot/test segregation and no-top-up principle are stated in the self-contained v5 §§1–5. The old worked examples and first-use checklist are historical, not final design text; their disposition is listed in v5 §9.
