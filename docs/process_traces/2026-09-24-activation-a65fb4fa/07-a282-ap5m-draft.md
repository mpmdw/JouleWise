# 07 — A282 AP-5M draft: the proposed MATH energy-per-correct analysis plan and D-166 addendum (PROPOSAL)

Drafting seat: Opus 5.5 subagent, activation a65fb4fa, lane A282 (HEADLINE-AP5M-AMENDMENT-01), read-only against
worktree `wt-a65fb4fa-bk` at `c90bc392`. Written 2026-09-24.

## 1. Status

**This is a proposal, not adopted claim policy.** AP-5M is a proposed row of the project's analysis-plan contract
(`docs/contracts/analysis_plans.md`): a filled table of rules that any published claim about MATH energy per correct
answer would have to cite and obey, written before any data exist. The accompanying D-166 addendum is a dated
amendment to decision-log entry D-166 (the project's workload decision), which today licenses scored benchmarks only
for the GSM8K leg. The magistrate (the agent that runs the project loop)
cannot adopt claim policy. An independent cold gate (a fresh Claude Fable instance with no loop context, paired
with an Opus refuter who checks the text against the project's contracts) reviews this draft. Ed alone decides
adoption, through his answer to question E2 ("adopt AP-5M and the D-166 addendum?") of the decision brief emailed on 2026-09-23 (Gmail `1a0d069e15a52ba9`); that answer is still pending. Until Ed
answers, no sentence here binds any measurement, estimator or claim, and the magistrate only records the gate's
ruling.

**What it supersedes.** It replaces packet C (the 2026-09-23 design draft,
`docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md`) as the AP-5M
candidate: packet C's draft decision-log addendum (its §2a), its draft plan row (§2b) and its decision rule (§3) are
replaced by §2–§4 below. Packet C's statement of the problem, its prohibitions, its claim-language table and its
list of files needing matching edits (§6) are carried forward. §2.7 itemises every change, after the terms it
needs. The sources include two earlier cold-gate rulings on the
estimator and packer code, convened as records 21 and 45 of activation d8cc9c0a ("gate 21", "gate 45"). When
sources conflict, the later ruling prevails, in this order: the gate-45 addendum (record 45/21 §7), the
gate-45 ruling (45/10), the gate-21 ruling with its paired refuter (21/10, 21/11), the round-1 rulings (record 08),
then packet C and the integration synthesis (record 19).

## 2. The proposed AP-5M row

### 2.1 Terms (read before the row; each term uses only terms defined above it)

**The physical setup.**

- **Problem, level.** A MATH problem is one competition-mathematics question with one reference answer, from the
  MATH dataset (Hendrycks et al., 2021). Its *level* is the integer 1–5 the dataset's authors attached when they
  published it. It is fixed before any model sees the problem and is never computed from a model's success rate or
  answer length. In this plan "difficulty" means only this label.
- **Model, arm.** The two models are Qwen3 1.7B and Qwen3 8B (pinned 4-bit MLX weights, run on one M3 Max
  laptop). An *arm* is a thinking mode: *thinking on* (the model writes a reasoning trace before its answer) or
  *thinking off*.
- **Attempt, cap, capped.** An *attempt* is one generation by one model for one problem. The *cap* is the fixed
  maximum number of tokens an attempt may generate in an arm. An attempt that reaches the cap is *capped*.
- **Scorer, correct, malformed.** The *scorer* is a pinned program that extracts the final answer from an
  attempt's text and compares it with the reference answer. An attempt is *correct* only when the scorer finds a
  match and the attempt is not capped. A *malformed* attempt has no extractable answer and counts as incorrect.
- **Cell.** One (model, arm, level) combination. Both models see the same problems in each (arm, level).
- **Envelope, envelope index, capacity.** An *envelope* is one continuous, fixed-length recording of the machine's
  power (600 s in the current design) during which exactly one model is loaded. Envelopes follow one another on a
  fixed schedule. The *envelope index* 0, 1, 2, … is an envelope's position in that schedule. *Capacity* is the
  number of seconds inside an envelope available for running problems; the registration's timing fields fix it.
- **Idle slot.** An envelope recorded with its model loaded and doing nothing, labelled `kind: "idle_slot"`. It
  keeps the schedule grid evenly spaced. Its joules never enter a numerator.
- **Block, block window, gross block energy.** A *block* is a fixed list of problems from one cell, run back to
  back inside one envelope. A marker is written when its first problem starts and when its last problem ends (the
  block's *outer item edges*). The *block window* is the interval between those markers. *Gross block energy* is
  the joules the power meter records inside the block window, with nothing subtracted for idle power.
- **Measurement window (night), census-clean.** A *measurement window*, usually called a *night*, is one scheduled,
  unattended capture session holding a sequence of envelopes (not to be confused with a block window). It counts
  only if the machine's process census (an inventory of running processes taken for that session) finds nothing
  outside the measurement's own processes. "Census-clean" means that check passed.
- **Registration.** The frozen, hashed record of every rule, constant and input fixed before any test problem runs
  (problem ids, caps, block size, timing, bounds, seeds). Nothing in it changes once data exist.

**Scheduling and retries.**

- **Packer, roster, parent block, piece.** The *packer* is the program that assigns blocks to envelopes before the
  night; its output list is the *roster*. A *parent block* is a block placed by this initial packing. A retry can
  cut a parent into one-problem blocks; each of these is a *single*, also called a *piece* of its parent.
- **Predicted, worst-case and reserved seconds.** `predicted_s` is the packer's forecast of a block's duration,
  taken from the sizing pilot. The *derived worst case* of one problem is `cap_tokens × s_per_token_upper +
  prefill_s`: the cap times the registered upper bound on seconds per generated token, plus the time to read the
  prompt. No legitimate attempt can take longer. `reserved_s` is the time the packer sets aside for a block in an
  envelope.
- **Overrun, observation, culprit, innocent.** An *overrun* is an envelope ending before all its blocks finish.
  Each block in that envelope then receives an *observation*: `completed`, `cut_off` (started, not finished) or
  `not_started`, with its elapsed seconds where it ran. A *culprit* is a block whose elapsed time exceeded its
  `predicted_s` (at the single stages, its derived worst case): the block that used up the time. An *innocent*
  block was cut off or never started because a culprit used up the time.
- **Retry stages, terminal states.** A culprit moves through fixed stages: `initial` → `whole_block` (the whole
  block re-run alone in a fresh envelope) → `single_problem` (each problem as its own single) → `single_retry` →
  `ceiling_violation`. A *ceiling violation* is a single that exceeds its derived worst case twice. It proves the
  registered upper bound false, so it is a terminal state, not a retry path. `unattributed_overrun` is the terminal
  state for blocks left unfinished in an envelope that holds no culprit; under correct instrumentation it cannot
  occur, so it signals a fault. Terminal states are listed in `terminal_refusals`; nothing is silently dropped.
- **Voided window.** The window of an attempt that a retry superseded. It stays on record and is never counted.
- **Spread, M8.** A cell's *spread* is the number of its parent blocks and the number of distinct envelopes that
  hold their counted windows. The claims ladder's comparative level (L2) needs "n ≥ 5 per condition"; M8 (the
  integration synthesis's eighth settled item) meets it by requiring at least five of each.
- **Position, drift lever.** Forcing problem: the machine's power drifts slowly across a night (temperature,
  background load). If one model's blocks sit systematically later in the night, drift biases the ratio between
  models. A parent's *position* is the item-weighted mean envelope index of its counted windows. The *drift lever*
  of a level is the absolute difference between the mean position of its 8B parents and that of its 1.7B parents,
  in envelope slots. Equal mean positions cancel a drift that is linear in time.
- **Recapture.** A registered re-measurement on a later census-clean window, allowed only where a rule below names
  it.

**Estimation.**

- **J/correct, R_L, factors.** A cell's *J/correct* is its summed gross block energy divided by its number of
  correct attempts. It factors exactly as J/correct = J/token × tokens/attempt ÷ accuracy (J/token = cell energy ÷
  cell generated tokens; tokens/attempt = generated tokens ÷ n; accuracy = correct ÷ n). *R_L* = J/correct(8B) ÷
  J/correct(1.7B) at level L in one arm. R_L < 1 means the 8B spent fewer joules per correct answer on that level's
  problems.
- **Floor and anchor bounds.** `floor_j` is the smallest energy the instrument can attribute to one window (about
  1 J on this stack). `anchor_j` (`E_clock_anchor_shift_bound_j`) is the most energy that can be assigned to the
  wrong window because the marker clock and the power sampler's clock may be offset. Each measured window can be
  wrong by at most `floor_j + anchor_j`. This error is a fixed bound, not random scatter, so it widens the interval
  rather than entering the resampling.
- **Bootstrap, replicate.** The *bootstrap* estimates sampling uncertainty by redrawing, with replacement, from the
  observed blocks and problems many times; each redraw is a *replicate*, and the spread of the recomputed ratios
  across replicates stands in for the spread a repeated experiment would show. Each replicate yields a *low-side*
  ratio (energies shifted by the instrument bound in the direction that makes the 8B look cheapest) and a
  *high-side* ratio (shifted the other way). The *interval* runs from the 2.5th percentile of low-side ratios to the
  97.5th percentile of high-side ratios (endpoint detail in K11); `lo` and `hi` are its ends.
- **p_below, p_above, p_L.** `p_below` is (1 + the number of replicates whose high-side ratio is ≥ 1 or undefined)
  ÷ (B + 1), with B the number of replicates: small when nearly every replicate says the 8B is cheaper. `p_above` is
  the mirror. `p_L = min(1, 2·min(p_below, p_above))` is the two-sided p-value for level L.
- **Holm, family, primary, secondary.** A *family* is the fixed set of hypotheses tested together; here one family
  per arm, each holding five hypotheses "R_L = 1", one per level. *Holm's procedure* keeps the chance of any
  false rejection in a family at or below α (0.05 here). With m hypotheses (m = 5) and p_L as each one's p-value:
  sort the family's p-values ascending as p(1) ≤ … ≤ p(m); reject the k-th while p(k) ≤ α/(m − k + 1); stop at
  the first failure. The thinking-on family is *primary* (it alone can carry the headline); the
  thinking-off family is *secondary*.
- **Sparse, merge, group, pooled.** A level is *sparse* in an arm when either model has fewer than 3 correct
  attempts there. A sparse level is *merged* with a neighbour in a fixed order, decided on correct counts only. The
  result is a set of *groups*: single levels or merged runs such as "4–5". A merged group is tested as one
  hypothesis; its constituent levels are *pooled* and each carries `pooled_in` (the group's levels).
- **Group status.** Each tested group gets one of four statuses: *8B cheaper* (E8, letter `8`), *1.7B cheaper*
  (E1, letter `1`), *not resolved* (NR, letter `n`: the evidence does not settle the direction, which is
  inconclusive, not a null), or *not estimable* (NE, letter `e`: no ratio can be computed, with a reason such as
  `sparse_after_merges` or `ceiling_violation`). A pooled constituent of an estimable group carries letter `p`.
  `interval_disagrees` flags a group whose Holm test rejected but whose interval still contains 1; such a group is NR.
- **Pattern, licensing group, boundary group, L\*, region statement.** Reading the resolved groups (E8 or E1) in
  level order gives a *pattern* such as `crossover` (1.7B-cheaper groups, then 8B-cheaper groups, one switch). The
  *boundary group* is the first 8B-cheaper group; the *licensing group* is the last 1.7B-cheaper group before it.
  The *crossover level L\** is the boundary group's level, reported only when the boundary group is a single level.
  When the licensing group is pooled, the claim may only be a *region statement*: it names the pooled range, never
  a constituent level.
- **Gap levels, bracket gap levels.** *Gap levels* are every NR or NE level in the family. *Bracket gap levels*
  are the gap levels lying strictly between the licensing group and the boundary level.
- **Cap-bound.** A cell with more than 20 % capped attempts.
- **Selection-confounded sensitivity.** A secondary re-analysis that removes some attempts (for example the
  retried ones). Because it removes exactly the longest problems, it is labelled as confounded by that selection and
  never replaces the primary estimate.
- **spread_exceeded, drift_exceeded.** Flags that a cell lost its minimum spread after capture, or that a level's
  executed drift lever exceeded the registered maximum; each makes the level NR until a registered recapture.

### 2.2 Worked example (planning figures, unmeasured)

These numbers come from packet C and the integration synthesis. They are planning stand-ins (the 1.5B/7B
decode-energy levels at `docs/research_question_bank.md:1615-1616`, about 47 J and 192 J per 512 tokens), not
measurements.

*One level.* Thinking on, Level 5, n = 64 problems. The 1.7B spends 0.092 J/token × 4,000 tokens/attempt = 368 J
per attempt, so its cell energy is 64 × 368 = 23,552 J. It gets 16 correct (25 %): 23,552 ÷ 16 = 1,472 J/correct.
The 8B spends 0.375 J/token × 2,500 tokens = 937.5 J per attempt, 60,000 J per cell, and gets 40 correct (62.5 %):
1,500 J/correct. R_5 = 1,500 ÷ 1,472 = 1.019. The 8B needed an accuracy ratio of (0.375 ÷ 0.092) × (2,500 ÷
4,000) = 2.55 to break even and achieved 0.625 ÷ 0.25 = 2.50.

*Spread.* The 64 problems split into five parent blocks of 13, 13, 13, 13 and 12, the same membership for both
models, each parent in a different envelope: five parents, five envelopes, so M8 holds.

*Instrument bound.* Take `floor_j` = 1 J (packet C) and, for illustration only, `anchor_j` = 1 J. Each parent is one
window, so each model's bound is U = 5 × 2 J = 10 J. The point bounds are (60,000 − 10) ÷ 40 over (23,552 + 10) ÷
16 = 1.0184 and (60,000 + 10) ÷ 40 over (23,552 − 10) ÷ 16 = 1.0196, around the point value 1.0190. The integration
synthesis's planning interval from sampling alone (E4, Ed's pending decision on problems per level) is about ×/÷ 1.59 at n = 64, i.e. [0.64, 1.62]. Sampling
dominates the instrument by more than two orders of magnitude; this level would be NR.

*Holm (illustrative p-values, invented for the arithmetic).* Thinking-on p-values L1 0.004, L2 0.030, L3 0.011,
L4 0.20, L5 0.009; α = 0.05, m = 5. Sorted: L1 0.004 ≤ 0.05/5 = 0.010, reject; L5 0.009 ≤ 0.05/4 = 0.0125, reject;
L3 0.011 ≤ 0.05/3 = 0.0167, reject; L2 0.030 > 0.05/2 = 0.025, stop. L2 and L4 are not rejected. If L1's interval
lies wholly above 1 and L3's and L5's wholly below, the statuses are `1n8n8`; the §3 rules classify this as a
crossover with L\* = 3, licensing group Level 1, gap levels 2 and 4, bracket gap level 2.

### 2.3 Diagram: one parent block's retry path (illustrative timings, not measured)

Assumed for the drawing only: capacity 540 s; derived worst case ≈ 200 s per problem (8,192-token cap × 0.02 s/token
upper bound + 36 s prefill); parent P3 holds four Level-5 problems (P3.a–P3.d) with `predicted_s` 250 s.

```
envelope index ->  4                        ...  20                          21                        22
model loaded       1.7B                          1.7B                        1.7B                      1.7B
                 +------------------------+    +---------------------------+ +-----------------------+ +-----------------------+
stage            | initial                |    | whole_block (P3 alone)    | | single_problem        | | single_problem        |
blocks           | P7 (L2): completed,    |    | P3 retry, 4 problems      | | P3.a   P3.b           | | P3.c   P3.d           |
                 |   180 s <= 200 s pred. |    |   reserved_s = 540 s      | |   200 s reserved each | |   200 s reserved each |
                 | P3 (L5): cut_off,      |    |   (min of 4 x 200, 540)   | |   both completed      | |   both completed      |
                 |   360 s > 250 s pred.  |    |   not completed -> split  | |                       | |                       |
                 |   => culprit           |    |                           | |                       | |                       |
                 +------------------------+    +---------------------------+ +-----------------------+ +-----------------------+
P3 windows         voided                        voided (envelope keeps       counted: 2 problems       counted: 2 problems
                                                 voided_block_ids = [P3])
time ------------------------------------------------------------------------------------------------------------------>
```

Every element: the top row is the **envelope index**, the envelope's slot in the night's schedule; "…" stands for
envelopes 5–19 of the initial roster. **Model loaded** is the one model in that envelope. Each box is one
**envelope**. **Stage** is the retry stage of the P3 work placed there. **Blocks** lists what ran: P7 is an
unrelated Level-2 parent that completed inside its `predicted_s` (so it keeps its window and is not a culprit); P3
is the culprit, cut off after 360 s against a 250 s prediction, so it advances to `whole_block`. Envelope 20 holds
the whole-block retry alone, reserved at the smaller of its four problems' worst cases (800 s) and capacity (540 s);
it does not complete, so it splits. Envelopes 21 and 22 hold the four **singles**, each reserved at its 200 s worst
case, two per envelope because three would need 600 s. Pieces of one parent may share an envelope; two parents of
one cell may not. **P3 windows** says which recordings count: the two failed attempts are voided and contribute
nothing; the singles' windows are counted. The arrow is **time**; every retry sits at a higher index than the
envelope where its overrun was observed.

*Drift lever from the drawing.* Suppose Level-5 thinking-on parents sit, at pack time, in envelopes 1, 5, 9, 13, 17
for the 8B (mean 9) and 0, 4, 8, 12, 16 for the 1.7B (mean 8): lever 1.0 slot. After the retry, P3's position is
(21 × 2 + 22 × 2) ÷ 4 = 21.5, the 1.7B mean becomes (0 + 21.5 + 8 + 12 + 16) ÷ 5 = 11.5, and the lever grows to 2.5
slots. That is why the lever is recomputed after every retry and checked against its registered maximum.

### 2.4 Placement

A new subsection `### AP-5M: MATH author-level energy per correct answer, two model sizes` inserted after AP-5 in
`docs/contracts/analysis_plans.md`. AP-5 gains one line: "Amendment (D-166 addendum, proposed 2026-09-24): MATH
author-level strata are AP-5M, which inherits this row's forbidden upgrade and quarantine." The registry paragraph
listing separate families adds "MATH level energy per correct answer" (packet C §2b, unchanged).

### 2.5 The row

Fields follow the AP-5 row in order. Five fields marked *(added)* are required by the lane and have no AP-5 slot;
the cold gate may fold them into the standard fields. Clause references (K-n) point to §2.6.

| Field | Value |
|---|---|
| Plan ID / RQ consumer | AP-5M / RQ-NEXT-EPCA-LEVELS headline: MATH author-level energy per correct answer, Qwen3 1.7B vs 8B (D-166 dated addendum, §4, proposed). |
| family_id | FAM-MATHLVL-EPC-THINKON (primary); FAM-MATHLVL-EPC-THINKOFF (secondary). The registration field `arm_to_family` derives the family from the arm; the family is never passed separately. |
| claim_role | Thinking-on R_L: primary. Thinking-off R_L: secondary; it cannot carry the crossover headline. |
| Estimand *(added)* | For each arm and level L, R_L = J/correct(8B) ÷ J/correct(1.7B) on the frozen problem set, this machine (M3 Max), pinned MLX 4-bit weights, pinned prompt template, scorer and extractor, the arm's cap, and the decoding rule fixed under E3 (open item O-14). The headline quantity is the thinking-on crossover level L\*, which exists only where §3 licenses it. |
| selection_scope | Population K1; Qwen3 1.7B and 8B; two arms; levels 1–5; the same problems for both models; pinned template, scorer, extractor and caps (K3). Nothing else is searched. |
| multiplicity_rule | Holm within each family, α = 0.05 two-sided, m = 5 fixed (one hypothesis R_L = 1 per level; a merged cell tests one hypothesis and m stays 5). Holm: sort p ascending; reject the k-th while p(k) ≤ α/(m−k+1); stop at the first failure. A not-estimable group is not tested and m stays 5. Clause K9. |
| Metric + exact window class | Gross block energy (K4) summed per cell; J/correct; the three factors, descriptive only (K5); capped, truncated and malformed counts; the cap-bound label (K3). Never envelope energy including idle padding. |
| Capture unit *(added)* | The envelope, one model loaded, one thinking arm per night; the block window inside it; the parent block as the energy replicate; idle slots captured, never a numerator (K6). |
| Unit of analysis + dependence structure | Problem for correctness and tokens (distinct problems, D-047.3); parent block for energy. Spread K7; retry tails K8. No problem window is an energy replicate. |
| Estimator/formula | R_L with the paired, block-aware bootstrap and share-scaled instrument bound (K10, K11); status by the three-way test (§3). |
| Inclusion/exclusion + quality-flag waiver rules | Strict-valid bundles only (bundles passing the claims ladder's applicable strict validation); a bundle contaminated by outside machine activity is re-run under the replacement rule, not waived. Capped = incorrect (K3); malformed = incorrect (D-047.6). Terminal-attempt windows K17. Pilot rosters K18. |
| Order/blocking/covariates | Equal mean envelope position per cell across models (K6); parent-unit drift lever and its refusal (K12). The idle reference is a covariate, never a numerator. |
| Floor gate | Every block window above `max(floor_abs_j, floor_cmp_j)` for its class (the larger of the instrument's calibrated absolute floor and comparison floor, from the P2-015 calibration artifact); the estimator refuses a block window at or below the floor. |
| MDE/n sizing + predeclared top-up rule | n per level ∈ {64, 128}, equal across levels, models and arms, set by a registered rule from the sizing pilot (K2) and frozen before any test problem runs (D-062). No top-up. Planning intervals ×/÷ 1.59 at n = 64 and ×/÷ 1.39 at n = 128 (E4, pending). |
| Denominator provenance requirement | Runtime-observed generated tokens including thinking tokens; exact scorer output with `scorer_id` on every row; `stop_reason` required on every row (K3); ≥ 3 correct per model per group, else the merge order (K9), else `not estimable`. |
| Sparse-level merge order *(added)* | K9. |
| Holdout cells (L3 only) | not applicable. |
| Retry and overrun rules *(added)* | K13 (M12 as amended), K14–K16 (ceiling violation, spread, precedence), K8 (M8 on retry tails). |
| Status vocabulary *(added)* | §3 in full. Ruled constants K19. |
| Claim ceiling + exact forbidden upgrade | Ceiling L2 on this frozen set, stack and caps. Forbidden: intelligence-per-joule; "difficulty causes energy"; any capability, ranking or routing claim; extrapolation beyond levels 1–5, these two models, or these caps. K20. |
| Disqualifiers + not-resolvable conditions | Below-floor blocks (refused); a packing shortfall of the five-parent or five-envelope minimum (packing refusal); `not estimable` after all merges; any R_L interval spanning 1, any `interval_disagrees`, `spread_exceeded` or `drift_exceeded` prints `not resolved`; a ceiling violation withholds L\* (S7, S8); an unattributed overrun leaves its cell unresolved until a registered recapture (K13); a non-claim-ready roster is refused (K18). |
| Linked manifests/bundle hashes | pending post-execution. |

### 2.6 Clauses referenced by the row

Blockquotes are carried from a ruling or settled source; the line under each names it. Unquoted text is this
seat's drafting and has no authority beyond the proposal.

**K1 — population (ADAPTED; see §5 A1).** The full MATH test split: `test.jsonl` plus the `test/`-tagged rows of
`train.jsonl` at `openai/prm800k` `7ecc7947`, 5,001 rows. Both rows of the one duplicated id are excluded, as are
954 references that are not rational-valued and 5 plain-comma references, leaving 5,001 − 2 − 954 − 5 = 4,040
eligible problems. Balanced by subject. Retention per level is disclosed (0.872 at Level 1 falling to 0.782 at
Level 5). Publication of problem text follows Ed's E1 ruling.

**K2 — sizing pilot and what it may set.**

> Caps, block size, envelope pitch, n per level (64 or 128, by a registered rule), and scorer additions (additions only, with a scorer-id bump). **Never** which levels are reported (D-062).

*Source: integration synthesis 19 §1 M5. VERBATIM.* The pilot is 16 problems per level (80), disjoint from the test
items, run as a bench token pilot (the problems run on the bench without power capture, to count tokens, cap hits
and rough seconds per token) plus one short measured shakedown night for envelope timing (M4), and is never
reported as a result.

**K3 — caps, capped attempts, cap-bound.**

> Every attempt that hits the cap counts as incorrect, even when a boxed answer parses. The parsed text is kept for a sensitivity analysis.

*Source: synthesis 19 §1 M2. VERBATIM.*

> capped := generated_tokens ≥ Registration.cap_tokens[arm]; stop_reason required on every row; disagreement refuses.

*Source: gate-21 refuter 11 R9. VERBATIM.*

> A cell with more than 20 % capped attempts is labelled cap-bound. The cap per arm is the smaller of two values: the cap-ladder rung that covers the pilot's Level-5 1.7B 95th-percentile length, and B's physical ceiling (cap × s/token + prefill ≤ 450 s).

*Source: synthesis 19 §1 M3. VERBATIM.* ("B" is packet B, the scored-night design.)

> **Cap-bound label.** A cell with > 20 % truncated attempts is *cap-bound*. The label prints beside every number
> from that cell. If L\* rests on a cap-bound cell, the crossover sentence must state the cap ("at an N-token cap").

*Source: packet C §3. VERBATIM.*

**K4 — energy numerator.**

> Gross energy between the outer item edges of each block. Net-of-idle is never a peer number; the idle reference is a covariate.

*Source: synthesis 19 §1 M7. VERBATIM.*

**K5 — J/token.** Descriptive only (synthesis 19 §1 M10, VERBATIM "Descriptive only."). J/token and tokens/attempt
are reported beside J/correct and never carry a claim-bearing contrast (D-045.7 unchanged).

**K6 — capture unit, idle slots, ordering invariant.**

> An empty slot is captured as a full-length envelope with its model worker loaded and idle, and is labelled `kind: "idle_slot"` in the roster. It never enters any numerator (M7). It may be used as a covariate.

*Source: round-1 rulings 08 F1. VERBATIM.*

> Drift cancels in a per-level ratio only when each model's measured blocks share the mean envelope index; `idle_slot` captured, never a numerator.

*Source: gate 21 ruling 10 §Q4 F1. VERBATIM.*

> Idle collector plus a separate model worker; one thinking arm per night; the energy rail and floor identity must match Paper B's pins or the floors are re-measured.

*Source: synthesis 19 §1 M13. VERBATIM.* (An idle collector is the process that records power; the model worker is a
separate process that runs the model. Paper B is the project's earlier measurement paper, whose power-rail and floor
settings are pinned.)

**K7 — spread (M8).**

> Each cell is spread over at least 5 blocks in at least 5 distinct envelopes. The packer carries a no-two-blocks-of-a-cell-in-one-envelope constraint. Block membership is identical across the two models, and block size is set per arm, not per model.

*Source: synthesis 19 §1 M8. VERBATIM.* K8 fixes what "block" means once retries exist.

**K8 — M8 on retry tails.**

> M8 applies to parent blocks. A parent block is a block scheduled by the initial packing; single-problem blocks made from it under M12 are pieces of that parent, not new replicates. No two parent blocks of one cell share an envelope at any stage, initial or retry. Pieces of one parent may share an envelope with each other and with blocks of other cells of the same model, within capacity. The five-block and five-envelope minima count parent blocks and the distinct envelopes holding their executed windows; a split never adds to either count.

*Source: gate 45 ruling 10 §Q4, "M8 on retry tails". VERBATIM.*

**K9 — minimum correct, sparse-level merge order, multiplicity.**

> **Minimum correct and merge order.** Each cell needs ≥ 3 correct (AP-5 guard; an observed count, a deterministic
> property of the set). If either model fails at a level in an arm, that level merges for both models, in that arm only,
> in this fixed order: 5 into 4 ("4–5"), then into 3; 1 into 2 ("1–2"), then into 3. Merges depend only on correct
> counts, never on energy or R. If no valid merge remains, the result is `not estimable`.

*Source: packet C §3. VERBATIM.* The isolated sparse Level 3 case, and the status of constituents, are fixed in §3
(S5, S9). Whether a sparse Level 4 alone (or Level 2 alone) merges is not stated by any ruling; see O-2.

**K10 — bootstrap (ADAPTED; see §5 A2 and O-4).** For each arm and each tested group: draw B replicates (B =
20,000, seed pinned in the registration). In each replicate, within each level of the group, draw as many parent
blocks as the level has, with replacement, and use the same draw for both models (membership is identical). Within
each drawn parent, draw as many problems as it holds, with replacement, and apply the same problem draws to both
models. A drawn problem contributes its model's correct flag and tokens; a drawn parent contributes its measured
gross energy g times the drawn-token share s (drawn problems' generated tokens ÷ the parent's generated tokens;
equal shares when the parent generated zero tokens). Compute each model's Σ energy ÷ Σ correct and their ratio. A
replicate with zero correct for one model gives 0 or +∞; zero for both is undefined and counts against both
directions. The point estimate uses untouched cell gross energy and correct counts.

> Bootstrap over paired problems **and** over capture blocks (block-aware), widened by the instrument's floor and anchor bounds. Holm is applied in two families of m = 5 (thinking-on primary; thinking-off secondary and unable to carry the headline). The crossover level L\* is defined only on Holm-significant directions.

*Source: synthesis 19 §1 M9. VERBATIM.*

**K11 — instrument bound.**

> per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`, with `k` the block's measured windows for that model and `s` the drawn-token share used at `:60-65`; point bounds keep `s = 1`.

*Source: gate 21 ruling 10 §Q2 D5a. VERBATIM.* (`:60-65` names the share computation in the draft estimator; K10
gives the share in words.)

> U_m = Σ u. Low bound R(E₈ − U₈, E₁.₇ + U₁.₇), high R(E₈ + U₈, E₁.₇ − U₁.₇); point bounds use s = 1.

*Source: Opus consult 20 §Q5(a), adopted by gate 21 D5a ("AFFIRM Opus's share-scaled bound"). VERBATIM.* The
reported interval runs from the lower of the point low bound and the 2.5th percentile of replicate low bounds to
the higher of the point high bound and the 97.5th percentile of replicate high bounds (ADAPTED, O-4).

**K12 — drift lever and refusal.**

> The drift lever of a level is the absolute difference, in envelope slots, between the mean position of its 8B parents and the mean position of its 1.7B parents. A parent's position is the item-weighted mean of the envelope indices of its executed windows: each item contributes the index of the envelope in which its counted attempt was captured. Voided attempts and idle slots contribute nothing. At pack time every item of a parent sits in one envelope, so its position is that envelope's index.

*Source: gate 45 ruling 10 §Q4, "Parent-unit drift lever". VERBATIM.*

> register `δ_upper` in joules per block per slot and `budget_j` as the per-cell absolute bias budget with its derivation; `max_gap` follows. `requeue_overrun` recomputes `drift_lever_slots`.

*Source: gate 21 ruling 10 §Q2 D5b. VERBATIM.* (δ_upper is the registered upper bound on how far a block's energy
can drift per envelope slot of separation; budget_j is the largest drift bias per cell the plan tolerates;
`requeue_overrun` is the packer function that applies K13 after an overrun.) The formula is `max_gap = budget_j / (δ_upper · blocks_per_cell)`
(gate-21 charge D5(b)); the packer refuses a roster above it.

> If the executed roster's gap exceeds max for a level, that level's status is NR(`drift_exceeded`) pending a balanced recapture.

*Source: gate-21 refuter 11 R11. VERBATIM.* The source of δ_upper is open (O-6).

**K13 — overruns and retries (M12 as amended).** M12 as settled in the synthesis:

> A block that overruns is re-queued once within the night. It is then re-queued as single-problem envelopes, never dropped.

*Source: synthesis 19 §1 M12. VERBATIM; amended by 08, gate 21 Q4 and gate 45 addendum §7 below.*

> After a second overrun, the items become single-problem BLOCKS, packed several per envelope, each with its own item edges. They are packed by the item's cap-bounded worst case (cap tokens × upper s/token + prefill; the pure module takes that worst-case seconds as an input), never by the prediction that already failed.

*Source: round-1 rulings 08, "M12 amendment". VERBATIM.*

> the worst-case seconds input is derived in Registration (`cap × s_per_token_upper + prefill`) and asserted ≥ the failed prediction, and the AP-5M text carries the amended M12 wording so registration and code do not diverge.

*Source: gate 21 ruling 10 §Q4, M12 amendment condition. VERBATIM.*

> "`requeue_overrun` at the initial and whole-block stages takes, for every block in the reporting envelope, an observation: `completed` with elapsed seconds, `cut_off` with elapsed seconds, or `not_started`; the envelope records every observation. A completed block keeps its window; if its elapsed exceeds its `predicted_s` it is marked `late: true` and is a culprit. An uncompleted block whose elapsed exceeds its `predicted_s` is a culprit and advances one stage. An uncompleted or not-started non-culprit is rescheduled at its current stage without advancing, provided the envelope holds a culprit. If it holds none, every uncompleted or not-started block becomes the typed terminal state `unattributed_overrun` (a `terminal_refusals` entry; its cell is unresolved until a registered recapture); the call never raises for innocence. The whole-block retry is scheduled alone in a fresh envelope with `reserved_s = min(Σ item derived worst cases, capacity)`; `predicted_s` is unchanged."

*Source: gate 45 addendum 21 §7 (W). VERBATIM.*

> "A whole-block retry advances to the split stage when its attempt did not complete within its envelope; its observed elapsed is recorded. Each single is packed at `reserved_s = predicted_s = the item's derived worst case`."

*Source: gate 45 addendum 21 §7 (T). VERBATIM.*

> "At the single stages the observation per single is `completed`, `cut_off` or `not_started`, with elapsed where applicable. A single whose elapsed exceeds its derived worst case advances (`single_problem` → `single_retry` → `ceiling_violation`). Any other uncompleted or not-started single is rescheduled without advancing, into the first later envelope satisfying M8-by-parent and capacity, else a fresh one. Each innocent reschedule is caused by one culprit event in its envelope and each item has at most two culprit events, so the total is at most 2 × (number of singles); the seal refuses a roster exceeding it."

*Source: gate 45 addendum 21 §7 (N). VERBATIM.*

> "An envelope with no active block is legal iff its `kind` is `idle_slot` or its `voided_block_ids` is non-empty; `_seal` refuses any other empty envelope. An envelope is fixed once an observation is recorded on it; a retry or reschedule is placed only at an index above the reporting envelope's. The split stage never reuses the whole-block retry's envelope."

*Source: gate 45 addendum 21 §7 (E). VERBATIM.* (Carried because it fixes where retries sit, which the drift lever
depends on; `_seal` is the packer's single validating exit.)

> `unattributed_overrun` is unreachable under correct instrumentation (Σ elapsed ≤ Σ predicted ≤ capacity); it is a fault signal the runner lane must surface, not a retry path.

*Source: gate 45 addendum 21 §8 NIT N1. VERBATIM.*

> runner lane, as the per-attempt kill timeout; registration keeps the inequality derived worst case ≤ `ceiling_s` ≤ capacity

*Source: gate 45 ruling 10 §Q2, CARRIED row for `ceiling_s`. VERBATIM.* (`ceiling_s` is the registered per-attempt
kill timeout that the night runner enforces; the inequality stops a runner killing a legitimate long attempt.)

Round-1 conditions on retry tails that still stand:

> (a) Pairing survives a split: singles carry `parent_block_id`, and the estimator pairs on the parent (Opus B2).
> (b) `retry_stage` is on every item row and flows into cells (Opus S6).
> (c) The single-problem stage is terminal: one single-problem retry, then the item is flagged `ceiling_violation`, a typed refusal for that item, recorded and never silently dropped (Opus S5).
> (d) The paired drop-retried sensitivity analysis is pre-registered, and it is labelled selection-confounded because it removes exactly the long items (Opus). If including versus pairwise excluding retried blocks changes any Holm direction or L\*, that claim is reported unresolved until a balanced recapture (Sol).

*Source: round-1 rulings 08 F2 (a)–(d), affirmed by gate 21 ruling 10 §Q4. VERBATIM.* The suggested
10 %-retried trigger in 08 F2(d) is not adopted here; see O-7.

**K14 — ceiling violation.** The status consequence (the gate-21 cure) and its recapture bound (the gate-21 refuter)
are carried in §3 as S7 and S8.

**K15 — spread_exceeded (ADAPTED by ruled substitution; see §5 A3).**

> A cell is spread-exceeded when its executed roster holds fewer than five parent blocks whose every item has a counted window, or fewer than five distinct envelopes holding them, for any reason after capture (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place). The cell carries `spread_exceeded: true`, its numbers are reported, and its level is not resolved (`spread_exceeded`) until a registered recapture. Before capture the same shortfall is a packing refusal.

*Source: gate 45 ruling 10 §Q4 "spread_exceeded", with the clause replaced by gate 45 addendum 21 §7 (X). Each
part VERBATIM; the join is the substitution (X) orders.*

**K16 — precedence.**

> "When a level carries both NE(`ceiling_violation`) for a group and `spread_exceeded`, NE(`ceiling_violation`) takes precedence in the A281b total table and `spread_exceeded: true` is recorded alongside; a level with `spread_exceeded` and no NE is NR(`spread_exceeded`)."

*Source: gate 45 addendum 21 §7 (P). VERBATIM.* (A281b is the estimator lane, now A293.)

**K17 — terminal-attempt windows.**

> A window for a terminal ceiling_violation attempt is accepted, recorded on the terminal refusal as `gross_j`, and never enters a cell sum.

*Source: gate 45 ruling 10 §Q5 F3. VERBATIM.*

**K18 — pilot rosters.**

> `mode = pilot` objects may emit only rosters flagged `claim_ready: false`; every consumer refuses a non-claim-ready roster outside pilot mode.

*Source: gate 21 ruling 10 §Q2 D4. VERBATIM.* (`mode = pilot` marks a registration used only for the sizing pilot;
a consumer is any program that reads the roster: reducer, estimator or night runner.)

**K19 — ruled constants.** Levels [1, 2, 3, 4, 5]; merge order 5→4→3 and 1→2→3 (K9); minimum correct 3 per model per
group; Holm m = 5 per family; α = 0.05 two-sided; minimum parent blocks per cell 5; minimum envelopes per cell 5;
cap-bound fraction 0.20; retry stages `initial`, `whole_block`, `single_problem`, `single_retry`,
`ceiling_violation`; B = 20,000.

> Module constants pinned by `schema`; one test asserts equality to the AP-5M text.

*Source: gate 45 ruling 10 §Q3, constants row. VERBATIM.* (`schema` is the registration's version identifier.) This clause is therefore the text such a test compares
against.

**K20 — forbidden upgrades, exclusions and claim language.** The AP-5 prohibitions carry over through §4 ruling (2).
The claims ladder's L2 row forbids "extrapolated crossover" in any case. What the plan does not license:

> Capability or leaderboard claims; rankings beyond this pair and set; routing policies; other caps, quantizations,
> devices or benchmarks; per-problem energy; confirmatory J/token or tokens/attempt contrasts; mechanism claims from the
> residual fit E = fixed + a·p + b·d (exploratory unless registered); thinking-off results as headline; pilot outcomes;
> any change to AP-5's affine-ladder rules.

*Source: packet C §5. VERBATIM.* Example sentences:

| Allowed | Banned |
|---|---|
| Per-level R_L with interval, cap and set named. *"On our frozen MATH Level 5 problems (thinking on, 8,192-token cap), Qwen3-8B used 0.6× [0.4, 0.9] the joules per correct answer of Qwen3-1.7B."* | Causal difficulty. *"Harder problems make the model draw more energy."* |
| Decomposition. *"Of the Level-5 gap, the token ratio contributes X and the accuracy ratio Y."* | Intelligence per joule or capability. *"The 8B delivers more intelligence per joule"*; *"the 8B solves 62 % of Level-5 MATH."* |
| Crossover within tested levels. *"The cheaper model per correct answer changed from 1.7B to 8B at MATH Level 4 on this set."* | Routing or general advice. *"Route hard prompts to bigger models to save energy."* |
| Null. *"No crossover within levels 1–5."* | Extrapolated crossover. *"Beyond Level 5 the 8B wins by more."* |

*Source: packet C §4. VERBATIM.* The allowed crossover and null examples are shapes only; the exact sentence for
any pattern is fixed by §3 (S3, S6, S10), which prevails.

### 2.7 Changes from packet C

- Packet C's problem-only bootstrap and fractional instrument widening (its §3 steps 1–6) give way to the paired,
  block-aware bootstrap (K10) and the share-scaled bound (K11).
- "≥ 5 bundles per cell" gives way to five parent blocks in five envelopes (K7, K8).
- Level-order rotation and A-B-B-A model order give way to equal mean envelope position per cell and the drift
  lever (K6, K12; O-10).
- The crossover definition (lowest level wholly below 1, with a lower level wholly above 1) gives way to the
  gate-21 decision table and status rules (§3).
- Population, cap and pilot text give way to the integration synthesis M1–M5 (K1–K3).
- The implicit "re-queue, never drop" overrun rule gives way to the gate-45 retry texts (K13–K16).
- Packet C's "n = 64 or 128" rule, prohibitions, cap-bound label, truncation rule, null wording and forbidden
  upgrades are kept (K3, K9, S10, K20).

## 3. Decision-pattern table and status rules

This section decides, for each arm, which groups are 8B cheaper, 1.7B cheaper, not resolved or not estimable,
which pattern the family shows, and whether a crossover level L\* may be claimed. The adopted vocabulary and
procedure are Opus consult 20's (gate 21 ruling 10 §Q1: "AMEND D2 (adopt, with rulings below)"), amended by the
gate-21 cures and the gate-21 refuter's wording. Every rule below is carried; this seat adds only the ordering and short reading notes.

**S1 — vocabulary.**

> Group status: `8B cheaper` (E8), `1.7B cheaper` (E1), `not resolved` (NR), `not estimable` (NE, reason `sparse_after_merges` or `ceiling_violation`). Level status: the group status if alone, else `pooled` with `pooled_in`. Pattern: `crossover`, `reverse_order`, `non_monotone`, `all_1.7B`, `all_8B`, `one_signed_1.7B`, `one_signed_8B`, `none_resolved`, `none_estimable`. L\* absent reasons: `boundary_group_pooled`, `reverse_order_not_registered`, `non_monotone`, `no_8B_cheaper_group`, `no_1.7B_cheaper_group`, `none_resolved`, `none_estimable`.

*Source: Opus consult 20 §Q2, adopted by gate 21 ruling 10 §Q1. VERBATIM.* S9 amends "else `pooled`" for
constituents of a not-estimable group; S7 adds `ceiling_violation_unresolved`; K12 and K15 add
`drift_exceeded` and `spread_exceeded` as NR reasons.

**S2 — the three-way direction test (status rule).**

> The status rule is: Holm rejects, the direction by p, and the interval lies wholly on that side; otherwise NR with an `interval_disagrees` flag.

*Source: gate-21 charge 00, lead disposition D2. VERBATIM; affirmed by the next quote.*

> Packet C's terms paragraph ("interval wholly below 1") and §3 ("Holm rejects and p_below < p_above") plus M9 ("only on Holm-significant directions") are satisfied together only by the conjunction; a Holm rejection whose widened interval straddles 1 is NR with `interval_disagrees`.

*Source: gate 21 ruling 10 §Q1, "Status rule (three-way conjunction): AFFIRM". VERBATIM.*

Operational form (Opus consult 20 §Q2 pseudocode, adopted with D2; VERBATIM):

```
merge(c8, c17):                        # correct counts per level; nothing else
  groups = {1},{2},{3},{4},{5}; sparse(g) = min(Σc8[g], Σc17[g]) < 3
  if sparse{4} or sparse{5}: join(5,4); if sparse(group(5)): join(group(5),3)
  if sparse{1} or sparse{2}: join(1,2); if sparse(group(1)): join(group(1), group(3))
  NE = {g : sparse(g)}                 # e.g. {3} alone, 345, 123, 12345
holm(p over tested groups, m=5 fixed): sort ascending; reject while p ≤ α/(5−rank); stop at first failure
status(g): NE if g∈NE; else if not rejected or p_below==p_above: NR
           else E8 if p_below<p_above and hi<1; E1 if p_above<p_below and lo>1
           else NR + flag interval_disagrees
classify(groups in level order):
  seq = statuses of E8/E1 groups in level order; changes = #adjacent differences
  seq empty          → none_estimable if all NE else none_resolved
  changes == 0       → all_X if every group resolved else one_signed_X
  changes ≥ 2        → non_monotone
  seq[0] == E8       → reverse_order
  else (E1…E1 E8…E8) → crossover: boundary = first E8 group, licensing = last E1 group,
                       gap_levels = levels strictly between (NR/NE)
                       L* = boundary's level if single, else None, reason boundary_group_pooled
                       (crossover_group still reported)
```

In `holm`, `rank` counts from 0, so the first comparison is against α/5. The `gap_levels` line is amended by S6;
the merge lines' handling of a sparse Level 4 or Level 2 alone goes beyond packet C's K9 text (O-2).

**S3 — pooled licensing, boundary rule.**

> A merged group may license L\* only as a region statement. When the licensing group is pooled, the crossover sentence reads: 'The cheaper model per correct answer changed from 1.7B on pooled Levels 1–2 to 8B at Level 3 on this set.' The output carries `licensing_group` (list of levels) and `licensing_pooled: true|false`. The boundary group must always be a single level.

*Source: gate 21 ruling 10 §Q1, Split 1 cure text. VERBATIM.*

**S4 — reverse order and non-monotone patterns.**

> Pattern `reverse_order`, reason `reverse_order_not_registered`, no L\*, per-level results printed.

*Source: gate 21 ruling 10 §Q1, Split 2. VERBATIM.*

> (b) `reverse_order` is any resolved sequence matching `8+1+` with zero further changes; `88111` qualifies, `8n111` too.

*Source: gate 21 ruling 10 §Q1, amendment (b). VERBATIM.*

> NIT: non_monotone rows need the reason code `non_monotone`.

*Source: gate-21 refuter 11 R5. VERBATIM.*

**S5 — sparse Level 3.**

> **Isolated sparse Level 3: AFFIRM** NE(`sparse_after_merges`); registration text for A282.

*Source: gate 21 ruling 10 §Q1. VERBATIM.* An isolated sparse Level 3 has no merge target in K9 and stays not
estimable.

**S6 — gap levels and the gap sentence.**

> (a) `gap_levels` must list every NR/NE level in the family, not only those strictly between licensing and boundary; the claim sentence names them.

*Source: gate 21 ruling 10 §Q1, amendment (a). VERBATIM.*

> If any level lies strictly between the licensing group and the boundary level, the sentence reads 'changed from 1.7B (Level a) to 8B between Levels a and L\*; Levels … not resolved'; L\* is reported as the first level with a resolved 8B-cheaper result.

*Source: gate-21 refuter 11 R4 cure. VERBATIM.*

> NIT: keep `bracket_gap_levels` separate.

*Source: gate-21 refuter 11 R4. VERBATIM.* How S3's pooled form, S6's bracket form and S6(a)'s all-gaps naming
combine in one sentence, and what word an NE gap level takes, are open (O-3).

**S7 — ceiling-violation null.**

> When any item in the family carries a terminal `ceiling_violation`, its group is NE(`ceiling_violation`), every other group is classified and printed, and `crossover_level` is null with reason `ceiling_violation_unresolved` until a registered recapture resolves the item. Pairwise exclusion of the item appears only in the labelled selection-confounded sensitivity.

*Source: gate 21 ruling 10 §Q1, Split 3 cure text. VERBATIM.* The gate's stated reason ("the violating item is by
construction the longest; a gap there is the selection M12 forbids") is disputed by the refuter (O-1).

**S8 — ceiling-violation recapture bound.**

> At most one recapture, on a later census-clean window, both models' copies adjacent as singles; the night's other blocks for that arm are checked against s_per_token_upper; a second violation makes `ceiling_violation_unresolved` terminal for the family under this registration.

*Source: gate-21 refuter 11 R6 cure. VERBATIM.* Precedence with `spread_exceeded` is K16.

**S9 — constituents of merged groups.**

> Constituents of an estimable merged group get `pooled` + `pooled_in`. Constituents of an NE merged group get `not estimable` + `pooled_in` + the NE reason.

*Source: gate-21 refuter 11 R7. VERBATIM.*

**S10 — null sentences.**

> **Null wording.** All levels above 1: "On this frozen MATH subset and stack, Qwen3-1.7B spent fewer joules per correct
> answer than Qwen3-8B at every level 1–5; no crossover within the tested levels." All below 1: the mirror. Non-monotone:
> per-level results, no crossover claimed.

*Source: packet C §3. VERBATIM.*

> When any group is pooled, the null sentence reads 'at every level or pooled level group (Levels 4–5 pooled)'; the mirror for 8B.

*Source: gate-21 refuter 11 R3 cure. VERBATIM.*

**S11 — authoritative worked-pattern table.** How to read it: in the first column, `|` separates groups and digits
written together form one merged group (`45` = Levels 4 and 5 merged); the letters after the partition are group
statuses in level order, and the second column gives level statuses 1→5. "(Sol)" marks rows contributed by the Sol
consult seat; "code" notes record what the ungated draft did. A row with no partition written is the
all-singleton partition 1|2|3|4|5.

Statuses per level 1→5: `8` 8B cheaper, `1` 1.7B cheaper, `n` not resolved, `e` not estimable, `p` pooled (with `pooled_in`). Brackets = merged group. "code" = probe at d2f9a273 where it differs.

| Partition / group statuses | Level statuses | Pattern | L\* or reason |
|---|---|---|---|
| 1\|2\|3\|4\|5 `1n888` | `1n888` | crossover | **3**, gap 2 |
| `88111` | `88111` | reverse_order | none, `reverse_order_not_registered` |
| `81888` | `81888` | non_monotone | none (code: 3) |
| `18188` | `18188` | non_monotone | none (code: 2) |
| `1n8n1` | `1n8n1` | non_monotone | none (code: 3) |
| `1nn8n` | `1nn8n` | crossover | **4**, gaps 2,3,5 |
| `n1n8n` | `n1n8n` | crossover | **4**, licensing 2, gaps 1,3,5 |
| `11188` | `11188` | crossover | **4** |
| `11n88` | `11n88` | crossover | **4**, gap 3 |
| `11111` | `11111` | all_1.7B | none, `no_8B_cheaper_group` |
| `88888` | `88888` | all_8B | none, `no_1.7B_cheaper_group` |
| `111n1` | `111n1` | one_signed_1.7B | none, `no_8B_cheaper_group` |
| `n8888` | `n8888` | one_signed_8B | none, `no_1.7B_cheaper_group` |
| `nnnnn` | `nnnnn` | none_resolved | none, `none_resolved` |
| 1\|2\|3\|4\|5, L3 sparse `11e88` | `11e88` | crossover | **4**, licensing 2, gap 3 (NE) |
| 1\|2\|3\|45 `1118` | `111pp` | crossover | none, `boundary_group_pooled`; crossover_group 4–5 |
| 1\|2\|3\|45 `1111` | `111pp` | all_1.7B | none, `no_8B_cheaper_group` (code: false `boundary_in_merged_group`) |
| 1\|2\|3\|45 `n1n8` | `n1npp` | crossover | none, `boundary_group_pooled` |
| 12\|3\|4\|5 `1888` | `pp888` | crossover | **3**, licensing 1–2 pooled (code: none; 08: undefined) |
| 12\|3\|45 `1n8` | `ppnpp` | crossover | none, `boundary_group_pooled` |
| 1\|2\|345 `11e` | `11eee` | one_signed_1.7B | none, `no_8B_cheaper_group` (code: false `boundary_in_merged_group`) |
| 123\|4\|5 `e18` (Sol) | `eee18` | crossover | **5**, licensing 4, gaps 1–3 (NE) |
| 1\|2\|345 `1n8` (Sol `1:1\|2:n\|[3–5]8`) | `1nppp` | crossover | none, `boundary_group_pooled` |
| 1\|2\|3\|45 `1n88` (Sol `1:1\|2:n\|3:8\|[4–5]8`) | `1n8pp` | crossover | **3**, gap 2 |
| 12345 `e` | `eeeee` | none_estimable | none, `none_estimable` |
| any partition, one group NE(`ceiling_violation`) | as above | as classified | none, `ceiling_violation_unresolved` |

*Source: gate 21 ruling 10 §Q1, "Authoritative worked-pattern table", legend and all 26 table rows (25 worked patterns plus the generic ceiling-violation row). VERBATIM. The "code"
annotations record what the ungated draft at `d2f9a273` did and are not rules. Under S6 the sentence for `1nn8n`
reads "between Levels 1 and 4"; under S9, rows with an NE merged group print `e` for its constituents.*

## 4. D-166 dated addendum (draft)

Index row pointer, appended to the D-166 row at `docs/decision_log.md:212`: "(MATH levels: see dated addendum,
proposed 2026-09-24; adoption by Ed under E2)."

> ## D-166 dated addendum (PROPOSED 2026-09-24, not adopted; Ed decides under E2): MATH author levels as a stratum for energy per correct answer
>
> **Forcing problem.** The headline question is how the energy spent per correct answer changes with problem
> difficulty and model size. AP-5 was written for a synthetic ladder built to keep answer length fixed, so it cannot
> host a benchmark whose answers lengthen on harder problems.
>
> **Terms.** As built in AP-5M §Terms (analysis_plans.md): level (the MATH authors' published label 1–5, never
> computed from model behaviour), attempt, cap, correct (a capped or malformed attempt is incorrect), cell, envelope,
> block, parent block, gross block energy, J/correct and R_L = J/correct(8B) ÷ J/correct(1.7B).
>
> **Worked example (planning figures, unmeasured).** Level 5, thinking on, n = 64: the 1.7B spends 0.092 J/token ×
> 4,000 tokens and gets 16 correct, 1,472 J/correct; the 8B spends 0.375 J/token × 2,500 tokens and gets 40 correct,
> 1,500 J/correct; R_5 = 1.02. The 8B needed an accuracy ratio of 2.55 to break even and achieved 2.50.
>
> **Ruling.** (1) MATH levels may stratify energy-per-correct comparisons under analysis plan AP-5M. (2) Every AP-5
> prohibition carries over unchanged: no intelligence-per-joule claim, no "difficulty causes energy" claim; accuracy is a
> property of the pinned frozen problem set, never a capability claim, because Qwen3's pre-training contamination by
> MATH is unmitigable; correctness remains a quarantined annotation (C-004) used only as the J/correct denominator.
> (3) The three factors are always reported beside J/correct and gross block energy is co-displayed
> (`token_normalization.md`). (4) J/token and tokens/attempt are descriptive factors, never claim-bearing contrasts
> (D-045.7 unchanged). (5) The GSM8K constants and manifest keep their text; the MATH importer carries its own.
> (6) The energy numerator is gross energy between the outer item edges of each block; net-of-idle is never a peer
> number. (7) A crossover is claimed only where the AP-5M decision table licenses it: a crossover is the first
> supported switch in which model uses less gross energy per correct answer, and a pooled difficulty group can
> license only a region statement. (8) No problem is dropped for running long: overruns are retried under AP-5M's
> retry rules, and a problem that exceeds its registered worst case withholds the crossover until one bounded
> recapture resolves it.
>
> **Status.** Proposed. A cold gate reviews this text; Ed adopts or rejects it under E2 (Gmail
> `1a0d069e15a52ba9`). Until then it binds nothing.
>
> Gate records:
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md`;
> `docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md`;
> draft `docs/process_traces/2026-09-24-activation-a65fb4fa/07-a282-ap5m-draft.md`; the AP-5M cold-gate ruling
> (pending).

Forcing problem, ruling (1)–(5): packet C §2a VERBATIM. Terms and worked example: packet C §2a ADAPTED (shortened,
pointing to the AP-5M Terms). Ruling (6): synthesis M7 ADAPTED. Ruling (7): lane A282 row ADAPTED. Ruling (8):
this seat's summary of K13 and S7–S8. Matching edits elsewhere follow packet C §6 unchanged, except that its
"≥ 5-bundle rule" entry for `claims_ladder.md:63` now reads "five parent blocks in five envelopes (M8)" and its
`research_question_bank.md:1728-1738` entry uses n ∈ {64, 128} from K2.

## 5. Provenance

Paths abbreviated: **C** = `docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md`;
**19** = `…/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md`; **08** =
`…/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md`; **20** = `…/d8cc9c0a/20-a281-opus-consult.md`;
**21/00, 21/10, 21/11** = `…/d8cc9c0a/21-coldgate-packet-a281/{00-charge, 10-coldgate-fable-ruling, 11-opus-contract-refuter}.md`;
**45/10, 45/21** = `…/d8cc9c0a/45-coldgate-packet-a281a-recut/{10-coldgate-fable-ruling, 21-coldgate-fable-addendum-ruling}.md`.

| # | Carried text (opening words) | Where here | Source § | Carry |
|---|---|---|---|---|
| 1 | "Caps, block size, envelope pitch, n per level…" | K2 | 19 §1 M5 | VERBATIM |
| 2 | "Every attempt that hits the cap counts as incorrect…" | K3 | 19 §1 M2 | VERBATIM |
| 3 | "capped := generated_tokens ≥ Registration.cap_tokens[arm]…" | K3 | 21/11 R9 | VERBATIM |
| 4 | "A cell with more than 20 % capped attempts is labelled cap-bound…" | K3 | 19 §1 M3 | VERBATIM |
| 5 | "**Cap-bound label.** A cell with > 20 % truncated attempts…" | K3 | C §3 | VERBATIM |
| 6 | "Gross energy between the outer item edges of each block…" | K4 | 19 §1 M7 | VERBATIM |
| 7 | "Descriptive only." | K5 | 19 §1 M10 | VERBATIM |
| 8 | "An empty slot is captured as a full-length envelope…" | K6 | 08 F1 | VERBATIM |
| 9 | "Drift cancels in a per-level ratio only when…" | K6 | 21/10 §Q4 F1 | VERBATIM |
| 10 | "Idle collector plus a separate model worker…" | K6 | 19 §1 M13 | VERBATIM |
| 11 | "Each cell is spread over at least 5 blocks…" | K7 | 19 §1 M8 | VERBATIM |
| 12 | "M8 applies to parent blocks…" | K8 | 45/10 §Q4 | VERBATIM |
| 13 | "**Minimum correct and merge order.** Each cell needs ≥ 3 correct…" | K9 | C §3 | VERBATIM |
| 14 | "Bootstrap over paired problems **and** over capture blocks…" | K10 | 19 §1 M9 | VERBATIM |
| 15 | "per replicate, per drawn block and model, `u = k·(floor_j + anchor_j)·s`…" | K11 | 21/10 §Q2 D5a | VERBATIM |
| 16 | "U_m = Σ u. Low bound R(E₈ − U₈, …)…" | K11 | 20 §Q5(a) | VERBATIM |
| 17 | "The drift lever of a level is the absolute difference…" | K12 | 45/10 §Q4 | VERBATIM |
| 18 | "register `δ_upper` in joules per block per slot…" | K12 | 21/10 §Q2 D5b | VERBATIM |
| 19 | "If the executed roster's gap exceeds max for a level…" | K12 | 21/11 R11 | VERBATIM |
| 20 | "A block that overruns is re-queued once within the night…" | K13 | 19 §1 M12 | VERBATIM |
| 21 | "After a second overrun, the items become single-problem BLOCKS…" | K13 | 08 M12 amendment | VERBATIM |
| 22 | "the worst-case seconds input is derived in Registration…" | K13 | 21/10 §Q4 | VERBATIM |
| 23 | (W) "`requeue_overrun` at the initial and whole-block stages…" | K13 | 45/21 §7 (W) | VERBATIM |
| 24 | (T) "A whole-block retry advances to the split stage…" | K13 | 45/21 §7 (T) | VERBATIM |
| 25 | (N) "At the single stages the observation per single…" | K13 | 45/21 §7 (N) | VERBATIM |
| 26 | (E) "An envelope with no active block is legal iff…" | K13 | 45/21 §7 (E) | VERBATIM |
| 27 | "`unattributed_overrun` is unreachable under correct instrumentation…" | K13 | 45/21 §8 N1 | VERBATIM |
| 28 | "runner lane, as the per-attempt kill timeout…" | K13 | 45/10 §Q2 CARRIED table | VERBATIM |
| 29 | F2 (a)–(d) "Pairing survives a split…" | K13 | 08 F2 | VERBATIM |
| 30 | spread_exceeded with (X) substituted | K15 | 45/10 §Q4 + 45/21 §7 (X) | ADAPTED (A3) |
| 31 | (P) "When a level carries both NE(`ceiling_violation`)…" | K16 | 45/21 §7 (P) | VERBATIM |
| 32 | "A window for a terminal ceiling_violation attempt is accepted…" | K17 | 45/10 §Q5 F3 | VERBATIM |
| 33 | "`mode = pilot` objects may emit only rosters…" | K18 | 21/10 §Q2 D4 | VERBATIM |
| 34 | "Module constants pinned by `schema`…" | K19 | 45/10 §Q3 | VERBATIM |
| 35 | "Group status: `8B cheaper` (E8)…" | S1 | 20 §Q2 | VERBATIM |
| 36 | "The status rule is: Holm rejects, the direction by p…" | S2 | 21/00 D2 | VERBATIM |
| 37 | "Packet C's terms paragraph… a Holm rejection whose widened interval straddles 1…" | S2 | 21/10 §Q1 | VERBATIM |
| 38 | merge/holm/status/classify pseudocode | S2 | 20 §Q2 | VERBATIM |
| 39 | "A merged group may license L\* only as a region statement…" | S3 | 21/10 §Q1 Split 1 | VERBATIM |
| 40 | "Pattern `reverse_order`, reason `reverse_order_not_registered`…" | S4 | 21/10 §Q1 Split 2 | VERBATIM |
| 41 | "(b) `reverse_order` is any resolved sequence matching `8+1+`…" | S4 | 21/10 §Q1 (b) | VERBATIM |
| 42 | "NIT: non_monotone rows need the reason code `non_monotone`." | S4 | 21/11 R5 | VERBATIM |
| 43 | "**Isolated sparse Level 3: AFFIRM** NE(`sparse_after_merges`)…" | S5 | 21/10 §Q1 | VERBATIM |
| 44 | "(a) `gap_levels` must list every NR/NE level…" | S6 | 21/10 §Q1 (a) | VERBATIM |
| 45 | "If any level lies strictly between the licensing group and the boundary level…" | S6 | 21/11 R4 | VERBATIM |
| 46 | "NIT: keep `bracket_gap_levels` separate." | S6 | 21/11 R4 | VERBATIM |
| 47 | "When any item in the family carries a terminal `ceiling_violation`…" | S7 | 21/10 §Q1 Split 3 | VERBATIM |
| 48 | "At most one recapture, on a later census-clean window…" | S8 | 21/11 R6 | VERBATIM |
| 49 | "Constituents of an estimable merged group get `pooled`…" | S9 | 21/11 R7 | VERBATIM |
| 50 | "**Null wording.** All levels above 1…" | S10 | C §3 | VERBATIM |
| 51 | "When any group is pooled, the null sentence reads…" | S10 | 21/11 R3 | VERBATIM |
| 52 | Table legend + 26 table rows (25 patterns + generic ceiling-violation row) | S11 | 21/10 §Q1 | VERBATIM |
| 53 | "Thinking-on R_L: primary. Thinking-off R_L: secondary…" | row claim_role | C §2b | VERBATIM |
| 54 | "Holm within each family, α = 0.05 two-sided, m = 5 fixed…" | row multiplicity | C §2b | VERBATIM (first two sentences; last two sentences are this seat's) |
| 55 | "Ceiling L2 on this frozen set, stack and caps. Forbidden: …" | row ceiling | C §2b | VERBATIM |
| 56 | D-166 forcing problem and ruling (1)–(5) | §4 | C §2a | VERBATIM |
| 57 | D-166 worked example | §4 | C §2a | ADAPTED (A4) |
| 58 | D-166 ruling (6) | §4 | 19 §1 M7 | ADAPTED (A5) |
| 59 | D-166 ruling (7) | §4 | TASK_QUEUE A282 row | ADAPTED (A6) |
| 60 | K1 population | K1 | 19 §1 M1 + §Addendum | ADAPTED (A1) |
| 61 | K10 bootstrap scheme and K11 interval rule | K10, K11 | C §3 steps 3, 5, 6; code `d2f9a273:joulewise/energy_per_correct.py` `ratio_interval` | ADAPTED (A2) |
| 62 | "Capability or leaderboard claims; rankings beyond this pair and set…" | K20 | C §5 | VERBATIM |
| 63 | Claim-language table (Allowed / Banned, 4 rows) | K20 | C §4 | VERBATIM |
| 64 | R6 dissent "Group-level NE is not pairwise exclusion…" | O-1 | 21/11 R6 | VERBATIM |

Counts: 58 VERBATIM carries (rows 1–29, 31–56 and 62–64; the 26-row table in row 52 counts once; row 54 is verbatim
for its first two sentences), 6 ADAPTED (rows 30 and 57–61; notes A1–A6 below).

**Adaptations, with originals.**

- **A1 (K1).** Original, 19 §1 M1: "The full MATH test split, 5,000 rows = `test.jsonl` plus the `test/`-tagged rows
  of `train.jsonl` at `openai/prm800k` `7ecc7947`. Those rows hold 5,001 lines and 4,999 unique ids. **Both** rows of
  the duplicated id are excluded. Rational-valued answers only. Balanced by subject. Retention per level is disclosed
  (0.872 at Level 1 falling to 0.782 at Level 5)." Corrected by 19 §Addendum: "5,001 rows, 5,000 distinct ids before
  exclusion (one id appears twice), 4,999 singleton ids. Exclusions are both rows of the duplicated id (2), 954
  non-rational references and 5 plain-comma references. That leaves **5,001 − 2 − 954 − 5 = 4,040 eligible**". The
  addendum prevails; K1 states its counts.
- **A2 (K10, K11).** Original, C §3 step 3: "Draw B = 20,000 resamples (seed pinned in the registration). Each draws n
  problem indices with replacement within the level and applies the same indices to both models". M9 requires the
  block level as well; no ruling states the two-stage scheme in words. K10 describes the scheme the draft estimator
  implements (`ratio_interval` docstring: "Bootstrap common blocks, then paired problems within each drawn block"),
  and K11's interval sentence describes its `interval = (min(point_low, _quantile(lows, 0.025)), max(point_high,
  _quantile(highs, 0.975)))`. C §3 step 6 original: "The reported interval runs from the 2.5th percentile of the
  low-side values to the 97.5th percentile of the high-side values." Code is not ruling; O-4 asks the gate to rule it.
- **A3 (K15).** Original, 45/10 §Q4: "…or fewer than five distinct envelopes holding them, because a parent lost an
  item to a terminal ceiling_violation after capture. The cell carries…". Substitution, 45/21 §7 (X): "Replace
  'because a parent lost an item to a terminal ceiling_violation after capture' with 'for any reason after capture
  (terminal `ceiling_violation`, `unattributed_overrun`, or a rescheduled parent the seal cannot place)'."
- **A4 (§4 example).** Original, C §2a: "**Worked example (1.5B/7B planning figures as stand-ins,
  research_question_bank.md:1615-1616).** Level 5, n = 64: the 1.7B spends 0.092 J/token × 4,000 tokens/attempt and
  gets 16 correct (25%): 0.092 × 4,000 ÷ 0.25 = 1,472 J/correct. The 8B spends 0.375 J/token × 2,500 tokens and gets
  40 correct (62.5%): 1,500 J/correct. R_5 = 1.02. The 8B needed an accuracy ratio of (0.375/0.092) × (2,500/4,000) =
  2.55 to break even and achieved 2.50." Shortened; numbers unchanged.
- **A5 (§4 ruling 6).** Original, 19 §1 M7: "Gross energy between the outer item edges of each block. Net-of-idle is
  never a peer number; the idle reference is a covariate." Rephrased as a ruling clause.
- **A6 (§4 ruling 7).** Original, TASK_QUEUE A282: "a crossover is the first supported switch in which model uses
  less gross energy per correct answer, and a pooled difficulty group can license only a region statement."
  Carried word for word inside a new lead-in sentence.

## 6. Open items

For the cold gate unless marked **Ed**. Each states the question that would close it.

- **O-1 (cold gate; refuter dissent, not resolved here).** The gate-21 refuter agrees with S7's outcome but disputes
  its reason. Dissent, VERBATIM from 21/11 R6: "Group-level NE is not pairwise exclusion, and the table lets
  count-based NE gaps license L\* (`11e88`, `eee18`), so "a gap there is selection" contradicts it. The operative
  reasons: (i) the censored outcome leaves the count-only merge partition undetermined; (ii) the violation falsifies
  a registered physical bound, a physics/evidence refusal." *Question:* which reason does AP-5M record for withholding
  L\* on a ceiling violation: the ruling's "a gap there is the selection M12 forbids", the refuter's (i) and (ii), or
  both? (The reason governs how the null is explained, not which statuses are printed.)
- **O-2 (cold gate).** K9 (packet C) moves only Level 5 and Level 1; it does not say where a sparse Level 4 or a sparse
  Level 2 goes when its outer neighbour is not sparse. S2's `merge` joins 5 with 4 when either is sparse, and 1 with 2
  when either is sparse. *Question:* is S2's `merge` the registered merge order, so that a sparse Level 4 alone yields
  group "4–5"?
- **O-3 (cold gate).** Three sentence rules meet without a combined form: S3 (pooled licensing), S6 R4 (bracket gap,
  "Levels … not resolved") and S6 (a) (the sentence names every gap level). Example `12|3|4|5` with statuses `1n88`
  (levels `ppn88`): licensing pooled 1–2, bracket gap 3, L\* = 4. Also, R4 says "not resolved" for gap levels, but
  table rows `11e88` and `eee18` have not-estimable gaps. *Question:* give the exact sentence for (i) a pooled
  licensing group with a bracket gap, (ii) gaps outside the bracket (`1nn8n`: is Level 5 named, and where), and (iii)
  an NE gap level ("not estimable" or "not resolved").
- **O-4 (cold gate).** No ruling states the resampling scheme or the interval's endpoint rule in words; K10–K11
  describe the draft code (two-stage: parent blocks within level, then paired problems within each drawn parent; the
  interval includes the point bounds). *Question:* adopt K10–K11 as registration text, with B = 20,000?
- **O-5 (cold gate).** K15 makes a spread-exceeded cell's level NR, but merged groups are not addressed. *Question:*
  when one constituent of a merged group is spread-exceeded, is the whole group NR(`spread_exceeded`)? And does
  "until a registered recapture" in K15 and in (W) share S8's one-recapture bound?
- **O-6 (cold gate).** K12 needs δ_upper and budget_j values; 21/11 R11 notes no source is named (the bench token
  pilot measures no energy). *Question:* is δ_upper taken from the shakedown night or from a pinned earlier corpus, and
  what budget_j derivation is registered? Also: where does NR(`drift_exceeded`) sit in K16's precedence?
- **O-7 (cold gate).** 08 F2(d) left to this lane a trigger: "retried attempts > 10 % of a headline cell ⇒ the next
  night re-measures the other model's copies adjacently". This draft does not adopt it; K13 (d) already reports a
  claim unresolved when the drop-retried sensitivity changes a direction or L\*. *Question:* add the 10 % trigger, or
  confirm its omission?
- **O-8 (cold gate).** S8 says "the night's other blocks for that arm are checked against s_per_token_upper" but not
  what follows if one fails. *Question:* is a failure a second violation (terminal under S8), or a separate refusal?
- **O-9 (cold gate).** M12 (K13, first quote) says "re-queued once within the night"; (N) places rescheduled singles
  "into the first later envelope … else a fresh one", with no same-night limit, and M13 allows one thinking arm per
  night. *Question:* may retry tails spill into a later night of the same arm, and if so, do their positions count in
  K12 across nights?
- **O-10 (cold gate).** Packet C's order rule (level order rotated across bundles, A-B-B-A model order) is dropped in
  favour of K6/K12, following 08 F1 ("The palindrome is kept only if the balance search wants it"). *Question:*
  confirm the drop.
- **O-11 (cold gate).** The row adds five fields (Estimand, Capture unit, Sparse-level merge order, Retry and overrun
  rules, Status vocabulary) beyond the AP-5 structure. *Question:* keep them, or fold them into the
  standard fields?
- **O-12 (Ed, E2).** Adopt AP-5M and the §4 D-166 addendum as drafted (after the cold gate's amendments), amend, or
  reject. Packet C's open rulings stand for Ed where not settled since: (1) sibling row vs rewriting AP-5; (2) two Holm
  families of m = 5 vs one of m = 10; (3) the L2 "n ≥ 5" met by five parent blocks in five envelopes, not by amending
  the claims ladder; (4) J/token descriptive only (M10); (5) capped = incorrect even when an answer parses (M2); (6) the
  20 % cap-bound threshold and the per-arm cap rule (M3); (8) the residual mechanism fit E = fixed + a·p + b·d
  exploratory; (9) claims say "MATH level", and "difficulty" appears only where defined. Packet C's (7) source set is
  settled by M1 (full test split).
- **O-13 (Ed, E4).** n per level: 128 if the pilot confirms the planning rates (about 23 windows) vs 64 (about 12).
  The registered rule decides mechanically; Ed rules on whether the budget ceiling is acceptable.
- **O-14 (Ed, E3).** Decoding: greedy (labelled "under greedy decoding") vs the model card's seeded sampling
  (temperature 0.6, top-p 0.95, top-k 20, one pinned seed per problem and model) vs thinking-off as primary. The
  estimand in §2.5 is incomplete until this is ruled; option (c) would swap the families' roles.
- **O-15 (Ed, E1).** Problem text stays in an untracked custody path bound by sha256; only hashes and ids are
  committed.

**First-use test.** Run over §1–§4. Every term of art is built in §2.1 before the row, or glossed where first used
(cold gate, magistrate and E2 in §1; "B" as packet B in K3; `_seal` in K13; A281b in K16). Terms not fully built:
(i) *strict-valid bundle* is glossed only as "passing the claims ladder's applicable strict validation"; the list of
strict checks is not restated. (ii) *capacity* is defined in words, but its formula from the registration's timing
fields (`envelope_s`, `offset_s`, `interior_s`, `guard_s`, `pitch_s`) is not stated in any ruling seen here and is
left to the packer registration (lane A291). (iii) Decision identifiers (D-045.7, D-047.3, D-047.6, D-062, C-004)
are cited, not explained; each is a pointer to a binding rule that the row does not restate.
