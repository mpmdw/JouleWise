# 12 — A282 pedagogy lens (Opus 5.5, read-only) on record 07, the AP-5M draft

Lens: pedagogy only. The question is whether a technical reader with no project grounding (a metrology expert and
JouleSort co-author who has never seen this repository) could REPLICATE the mechanism from the text of record 07
alone. Factual fidelity to sources is another lens's job and is not re-checked here. Line numbers refer to
`07-a282-ap5m-draft.md` as read at 898 lines. Where a failing term sits inside a VERBATIM carry, the fix builds the
term before the carry (in §2.1 Terms or in a lead-in sentence) and never edits the carry.

Severity key: **BLOCKER** means the reader cannot replicate a step. **MATERIAL** means the reader can replicate only
by guessing, or reads one meaning and later finds another. **NIT** means internal shorthand that costs trust but does
not change what the reader would compute.

## 1. First-use table

Verdicts: BUILT-BEFORE (constructed before first use), GLOSSED-AT (plain gloss at first use), FAILS (meaning arrives
later at the line given, or never). Severity is given for FAILS only.

| # | Term (first use) | Line | Verdict | Sev. | Note |
|---|---|---|---|---|---|
| 1 | "A282", "lane", "HEADLINE-AP5M-AMENDMENT-01" | 1, 3 | FAILS (never) | NIT | "lane" (a queued work item) is never glossed; it recurs at 224, 417, 446 |
| 2 | AP-5M | 1 | GLOSSED-AT 8 | — | title precedes gloss by 7 lines; acceptable |
| 3 | D-166 | 1 | GLOSSED-AT 10–11 | — | |
| 4 | "drafting seat", "Opus 5.5 subagent", "activation a65fb4fa", worktree/commit | 3–4 | FAILS (never) | NIT | provenance metadata; "seat" and "activation" never glossed |
| 5 | analysis-plan contract, claim policy | 8 | GLOSSED-AT | — | |
| 6 | "GSM8K leg" | 12 | FAILS (never) | NIT | benchmark not named as such; "leg" is shorthand |
| 7 | magistrate | 12 | GLOSSED-AT | — | |
| 8 | cold gate, Fable, Opus refuter | 13–14 | GLOSSED-AT | — | roles glossed; model names left bare (fine) |
| 9 | "Ed" | 14 | FAILS (never) | NIT | the project owner; one word fixes it |
| 10 | E2, decision brief | 15 | GLOSSED-AT | — | |
| 11 | packet C | 19 | GLOSSED-AT | — | weak gloss ("design draft"), adequate |
| 12 | "records 21 and 45 of activation d8cc9c0a" | 25 | FAILS (never; path key at 723–727) | MATERIAL | "record" and "activation" never glossed |
| 13 | "45/21 §7", "45/10", "21/10, 21/11" | 26–27 | FAILS (key at 726–727) | MATERIAL | the slash notation is decoded 700 lines later |
| 14 | "round-1 rulings (record 08)" | 27 | FAILS (never) | NIT | "round 1" of what is not said |
| 15 | "integration synthesis (record 19)" | 28 | FAILS (never) | MATERIAL | used as the source of every M-number (M1–M13) |
| 16 | problem, level, MATH, "difficulty" | 36–39 | BUILT-BEFORE | — | model paragraph |
| 17 | "pinned", "4-bit MLX weights" | 40 | FAILS (never) | NIT | "pinned" (fixed by version hash) recurs about 20 times |
| 18 | arm, thinking on/off | 41 | BUILT-BEFORE | — | |
| 19 | attempt, cap, capped | 43 | BUILT-BEFORE | — | |
| 20 | scorer, correct, malformed | 45 | BUILT-BEFORE | — | |
| 21 | cell | 48 | BUILT-BEFORE | — | |
| 22 | envelope, envelope index | 49–51 | BUILT-BEFORE | — | |
| 23 | capacity | 51 | FAILS (formula never; self-admitted at 894) | MATERIAL | "the registration's timing fields fix it", but the fields and formula never appear |
| 24 | "registration" (used) | 52 | FAILS (defined at 63) | MATERIAL | move the Registration bullet above Envelope |
| 25 | idle slot | 53 | BUILT-BEFORE | — | |
| 26 | "numerator" | 54 | FAILS (J/correct built at 101) | NIT | |
| 27 | block, block window, marker, outer item edges | 55–57 | BUILT-BEFORE | — | "marker" is loose but adequate |
| 28 | "item" (bare, = one problem inside a block) | 56 | FAILS (never glossed) | MATERIAL | carries weight at 93, 324, 367, 388, 404 ("item-weighted", "items become single-problem BLOCKS") |
| 29 | "the power meter", later "energy rail" | 57, 310 | FAILS (never identified) | BLOCKER (see F3) | for a metrology reader, what records the joules (instrument, rail, sampling rate) is the mechanism itself |
| 30 | measurement window (night), census-clean | 59–62 | BUILT-BEFORE | — | |
| 31 | registration | 63 | BUILT-BEFORE (for uses after 63) | — | |
| 32 | packer, roster, parent block, piece, single | 68–70 | BUILT-BEFORE | — | |
| 33 | "sizing pilot" | 72 | FAILS (built at K2, 267–270) | MATERIAL | `predicted_s` is defined through it |
| 34 | derived worst case, `s_per_token_upper`, `prefill_s`, `reserved_s` | 72–75 | BUILT-BEFORE | — | |
| 35 | overrun, observation, culprit, innocent | 76–80 | BUILT-BEFORE | — | "single stages" points forward 5 lines; acceptable |
| 36 | retry stages, terminal state, `terminal_refusals` | 81–86 | GLOSSED-AT | — | `single_retry` never described (one more attempt of the single); NIT |
| 37 | voided window, counted window | 87–88 | BUILT-BEFORE | — | |
| 38 | "claims ladder", "L2" | 89 | FAILS (never) | MATERIAL | also collides with MATH "Level 2" (see F6) |
| 39 | M8 | 89 | GLOSSED-AT | — | points into row 15's unglossed synthesis |
| 40 | position, drift lever | 91–95 | BUILT-BEFORE | — | forcing problem present; good |
| 41 | recapture | 96 | BUILT-BEFORE | — | |
| 42 | "census-clean window" (here = a night) | 96 | FAILS (collision) | MATERIAL | "window" means block window (57), night (59), attempt window (87), "problem window" (237), night again (608), and "about 23 windows" (883) |
| 43 | J/correct, R_L, factors | 101–105 | BUILT-BEFORE | — | "n" is implicit (problems per cell); NIT |
| 44 | `floor_j`, "attribute", "this stack" | 106 | GLOSSED-AT | — | but see row 63: a second floor family appears later |
| 45 | `anchor_j` | 107 | BUILT-BEFORE | — | |
| 46 | bootstrap, replicate, low/high side | 111–115 | GLOSSED-AT | — | |
| 47 | "interval" endpoints | 115–116 | FAILS (meaning changed at 361–363) | BLOCKER (see F2) | Terms: "2.5th pct of low-side to 97.5th pct of high-side"; K11: "the lower of the point low bound and the 2.5th pct…". The reader learns one rule and later meets a different one |
| 48 | "undefined" ratio | 117 | FAILS (built at 344–345) | MATERIAL | |
| 49 | `p_above` "is the mirror" | 118 | FAILS (never written out) | MATERIAL | "mirror" does unpaid work; the count condition (low-side ≤ 1? < 1?) must be guessed |
| 50 | Holm, family, α, primary, secondary | 120–125 | BUILT-BEFORE | — | good |
| 51 | sparse, merge, group, pooled, `pooled_in` | 126–129 | GLOSSED-AT | — | "fixed order" points to K9; acceptable as a pointer |
| 52 | E8/E1/NR/NE, letters, `interval_disagrees` | 130–134 | BUILT-BEFORE | — | |
| 53 | pattern, `crossover`, boundary, licensing, L\*, region statement | 135–140 | BUILT-BEFORE | — | |
| 54 | gap levels, bracket gap levels | 141–142 | BUILT-BEFORE | — | |
| 55 | cap-bound, selection-confounded sensitivity | 143–146 | BUILT-BEFORE | — | |
| 56 | `spread_exceeded`, `drift_exceeded`, "registered maximum" | 147–148 | GLOSSED-AT | — | |
| 57 | "1.5B/7B decode-energy levels … 47 J and 192 J per 512 tokens" | 153 | FAILS (never) | NIT | the link to 0.092 and 0.375 J/token (÷ 512) is left for the reader to compute |
| 58 | "×/÷ 1.59" | 168 | FAILS (never) | MATERIAL | multiplicative-interval notation unglossed; the 1.59 cannot be derived from the text |
| 59 | `voided_block_ids` | 194 | FAILS (indirectly at 408) | MATERIAL | the diagram legend skips it |
| 60 | AP-5 | 217 | FAILS (partly at 679–680) | MATERIAL | the parent row is never described; "synthetic ladder" at 679 is itself unglossed |
| 61 | "forbidden upgrade", "quarantine" | 219 | FAILS (never; "quarantined annotation" at 693 unglossed) | MATERIAL | |
| 62 | "RQ consumer", `RQ-NEXT-EPCA-LEVELS` | 229 | FAILS (never) | NIT | |
| 63 | `floor_abs_j`, `floor_cmp_j`, "for its class", "P2-015 calibration artifact" | 241 | FAILS (never) | BLOCKER (see F3) | how these relate to row 44's `floor_j` (the number K11 needs) is never stated |
| 64 | E3 / O-14 | 232 | FAILS (at 885) | NIT | pointer; acceptable if "E3 = Ed's pending decoding decision" is added |
| 65 | "window class" | 235 | FAILS (never) | MATERIAL | |
| 66 | "truncated" | 235 (also 286) | FAILS (never) | MATERIAL | the row lists "capped, truncated and malformed counts" as three things; K3 (packet C) defines cap-bound by "truncated", M3 by "capped". Same thing or not? |
| 67 | D-047.3, D-047.6, D-062, D-045.7, C-004 | 237, 239, 242, 297, 693 | FAILS (self-admitted at 896) | MATERIAL | each carries a rule the row relies on (distinct-problem unit, malformed = incorrect, pilot freeze, J/token descriptive, correctness quarantine); a one-clause gloss each |
| 68 | "energy replicate", "problem window" | 237 | FAILS (never) | MATERIAL | singles have per-problem windows that ARE counted; the sentence reads as a contradiction without a gloss |
| 69 | "bundle", "strict-valid", "replacement rule" | 239 | FAILS (never; "strict-valid" self-admitted at 893) | MATERIAL | |
| 70 | "top-up" | 242 | FAILS (never) | NIT | adding problems after seeing data |
| 71 | `stop_reason` | 243 | FAILS (never) | NIT | why generation stopped (end token vs cap) |
| 72 | "Holdout cells (L3 only)" | 245 | FAILS (never) | MATERIAL | L3 is a claims-ladder rung here, not MATH Level 3 |
| 73 | M12 (and M2–M13 generally) | 246 | FAILS | NIT | glossed only by analogy to M8 at 89 |
| 74 | "rational-valued", "plain-comma" references | 259 | FAILS (never) | BLOCKER (see F4) | the eligibility predicate that yields 4,040 cannot be rebuilt |
| 75 | "Balanced by subject" | 260 | FAILS (never) | BLOCKER (see F4) | how n problems per level are drawn is never stated |
| 76 | E1 | 261 | FAILS (at 888) | NIT | |
| 77 | "envelope pitch" | 265 | FAILS (never; field named at 895) | MATERIAL | |
| 78 | M4 | 269 | FAILS (never) | NIT | |
| 79 | "boxed answer" | 274 | FAILS (never) | NIT | MATH answers are wrapped in `\boxed{…}` |
| 80 | "disagreement refuses" | 278 | FAILS (never) | MATERIAL | disagreement between `stop_reason` and the token count? Must be guessed |
| 81 | "cap-ladder rung" | 282 | FAILS (never) | MATERIAL | the candidate cap values are never listed; the diagram's 8,192 is the only hint |
| 82 | packet B | 284 | GLOSSED-AT | — | |
| 83 | "peer number" | 293 | FAILS (never) | NIT | |
| 84 | "energy rail" | 310 | FAILS (never) | BLOCKER (with row 29) | |
| 85 | "AP-5 guard" | 330 | FAILS (never) | NIT | |
| 86 | share `s`, `g` | 342–344 | BUILT-BEFORE | — | |
| 87 | `k` = "the block's measured windows" | 354 | GLOSSED-AT | MATERIAL | for a split parent (four singles) the count of k is ambiguous; see F2 |
| 88 | `E₈`, `E₁.₇`, `U_m`, `R(a, b)` | 359 | FAILS (never) | MATERIAL | `E8` is already the status "8B cheaper" (131); `R(·,·)` as a two-argument function is unglossed |
| 89 | `δ_upper`, `budget_j` | 371 | GLOSSED-AT 373–375 | — | |
| 90 | `blocks_per_cell` | 375 | FAILS (never) | BLOCKER (see F5) | parents per cell? all blocks including singles? |
| 91 | "balanced recapture" | 378 | FAILS (never) | NIT | |
| 92 | "the pure module" | 388 | FAILS (never) | NIT | code jargon inside a carry |
| 93 | "reporting envelope", `late: true` | 396 | GLOSSED-AT | — | |
| 94 | "the seal" | 404 | FAILS (at 411) | NIT | |
| 95 | "runner lane", "night runner" | 417–420 | FAILS (never) | NIT | |
| 96 | "Opus B2 / S6 / S5", "(Sol)" | 424–427 | FAILS (never) | NIT | reviewer attributions |
| 97 | A281b / A293 | 444–446 | FAILS | NIT | lane ids |
| 98 | "residual fit E = fixed + a·p + b·d" | 476 | FAILS (never) | MATERIAL | p and d never defined |
| 99 | "affine-ladder rules" | 477 | FAILS (never) | MATERIAL | |
| 100 | "Opus consult 20", "D2", "cures" | 509–510 | FAILS | NIT | |
| 101 | pattern names `reverse_order`, `non_monotone`, `all_X`, `one_signed_X`, `none_resolved`, `none_estimable`, and the L\* absent reasons | 514 | FAILS (defined by pseudocode at 542–547) | MATERIAL | `all_1.7B` vs `one_signed_1.7B` is resolvable only from line 545 |
| 102 | `c8`, `c17`, `join`, `rank` | 533–554 | GLOSSED-AT | — | |
| 103 | regex `8+1+` | 569 | FAILS | NIT | that `n` letters are skipped is only implied by "`8n111` too" |
| 104 | "both models' copies adjacent as singles" | 608 | FAILS (never) | MATERIAL | "copies" (the same problem run by each model) and "adjacent" (consecutive envelopes?) |
| 105 | "code", "probe at d2f9a273" | 636 | GLOSSED-AT (weak) | — | |
| 106 | Sol notation `1:1\|2:n\|[3–5]8` | 662 | FAILS | NIT | |
| 107 | "GSM8K constants and manifest", "MATH importer" | 695 | FAILS | NIT | |
| 108 | "first supported switch" | 699 | FAILS | MATERIAL | inside the adapted ruling (7); build "supported" in the addendum's Terms paragraph |
| 109 | "about 23 windows" vs "about 12" | 883 | FAILS | NIT | windows = nights? envelopes? |
| 110 | "custody path" | 888 | FAILS (never) | MATERIAL | Ed's own example of a failing word |
| 111 | "idle reference is a covariate" | 240, 293, 302 | FAILS (never operationalised) | MATERIAL | K10 has no covariate step; the reader cannot tell whether to adjust R_L by it or merely report it |

Counts: 111 rows; **67 FAILS** (7 BLOCKER, 32 MATERIAL, 28 NIT); 44 BUILT-BEFORE or GLOSSED-AT. The draft's
self-check at 891–897 ("Every term of art is built … or glossed") is therefore not accurate as written; it names
three residual gaps where the table finds 67.

The Terms block (36–148) is strong: rows 16–56 mostly pass, and the forcing problem written into the drift-lever
bullet is exactly the pattern the standard asks for. The failures cluster in three places: §1 provenance
shorthand, the §2.5 row and the K-clauses (where carried text brings in vocabulary the Terms never built), and the
estimator's formal symbols.

## 2. Why-chain audit per mechanism

| Mechanism | Forcing problem? | Worked example with real numbers? | Diagram, every element named? | Verdict |
|---|---|---|---|---|
| Retry ladder | Partial. "Nothing is silently dropped" (86) and §4 ruling (8) state the rule, not the physics. Never stated in one place: envelopes have a fixed length, the longest attempts cost the most joules, so dropping them biases hard-level J/correct downward. | Yes, the diagram's timings (540 s capacity, 200 s worst case, 360 s vs 250 s). | Yes, with gaps: `voided_block_ids` (194) unnamed in the legend; only the success path is drawn, with no innocent reschedule, no `single_retry`, no `ceiling_violation`; line 203 says "the smaller of its four problems' worst cases (800 s)", which reads as min(200, …) = 200 when the sum 4 × 200 = 800 is meant. | MATERIAL |
| Spread minima (M8) | No physics. Justified only as a ladder rule ("n ≥ 5", 89). Missing: blocks sharing an envelope share its thermal and background state, so they are not independent energy measurements; hence "five distinct envelopes" and "no two parents of a cell in one envelope". | Yes (162–163). | Not needed. | MATERIAL |
| Drift lever | Yes (91–95). | Yes for the lever (210–213: 1.0 → 2.5 slots). No for the refusal threshold: `max_gap = budget_j / (δ_upper · blocks_per_cell)` has no illustrative numbers and one undefined variable. The algebra behind "equal mean positions cancel a linear drift" (bias ≈ δ × Δposition × blocks) is never shown. | Partial (the retry diagram shows how a retry moves position). | BLOCKER (threshold not computable) |
| Bootstrap interval | Partial ("sampling uncertainty", 111). Missing: why two stages (energy is measured per parent block, correctness per problem) and why share-scaling (a replicate that draws half a parent's tokens should carry about half its energy). | No. The only interval number, [0.64, 1.62], is imported ("×/÷ 1.59") and cannot be reproduced. No single replicate is worked through. | None, though this is the most algorithmic mechanism in the document. | BLOCKER |
| Holm correction | Implicit (five levels give five chances of a false finding); one sentence would make it explicit. | Yes (171–175), clean. | A sort table would suffice; the inline example serves. | PASS, with one gap: whether a level forced NR by `spread_exceeded` or `drift_exceeded` still contributes its p-value to the Holm sort (which changes the other levels' thresholds) is unstated. See F1. |
| Merge order | No. Why ≥ 3 correct (J/correct divides by the correct count, so 1 or 2 makes the ratio swing by factors of 2–3 on one problem) and why merge toward the middle are never said. | No numeric example of correct counts triggering a merge; merges appear only as partitions in S11. | A five-node level line with arrows 5→4→3 and 1→2→3 would be cheap and decisive. K9 and S2 disagree on a sparse Level 4 or Level 2 alone (O-2); the reader meets two rules. | MATERIAL |
| Decision table | Yes in S2's second quote (Holm and the widened interval can disagree). | Yes: 26 rows plus the Holm example. | The table serves as the diagram; its legend is good. Pattern names reach the reader late (row 101), and sentence templates are open (O-3). | MATERIAL (ordering only) |
| Ceiling-violation recapture | Yes (84: it falsifies a registered bound). The reason for withholding L\* is disputed (O-1). | No numbers. | None; the retry diagram stops before this branch. "Copies" and "adjacent" unglossed; the failure path is open (O-8). | MATERIAL |

## 3. Replication test: from raw per-block energies and per-problem correctness to a per-level verdict

This is the procedure written from record 07 alone, run once per arm. A `GUESS` tag marks each step where the text
forced a guess.

1. **Label each attempt.** capped := `generated_tokens ≥ cap_tokens[arm]`; correct := scorer match ∧ ¬capped;
   malformed ⇒ incorrect. `GUESS 1`: what "disagreement refuses" (278) compares. `GUESS 2`: whether "truncated"
   (235, 286) is a separate count from "capped".
2. **Select counted windows.** Drop voided windows. Keep terminal `ceiling_violation` windows out of cell sums (K17).
   Refuse any block window at or below the floor. `GUESS 3`: the floor value. Is it `floor_j`, or
   `max(floor_abs_j, floor_cmp_j)`, and for which "class" (241)?
3. **Form per-parent energy per model.** `GUESS 4`: for a split parent, is g the sum of its counted singles'
   windows? And is k (354) the number of those windows, or 1?
4. **Spread check per cell.** At least five parents with every item counted, in at least five distinct envelopes,
   else `spread_exceeded` ⇒ level NR (K15). Replicable.
5. **Drift check per level.** Positions and lever are replicable (K12). `GUESS 5`: `blocks_per_cell`. `GUESS 6`:
   δ_upper and budget_j have no values (O-6), so `max_gap` cannot be computed and the check cannot be run.
6. **Merge.** Take correct counts per level per model and apply S2 `merge`. `GUESS 7`: K9 or S2 when Level 4 alone is
   sparse (O-2).
7. **Point estimate per group.** R = (Σ E_8B ÷ Σ c_8B) ÷ (Σ E_1.7B ÷ Σ c_1.7B) over the group's levels. Point bounds
   with U = Σ k·(floor_j + anchor_j). Replicable, given steps 2 and 3.
8. **Bootstrap, B = 20,000.** Draw parents within each level of the group, then problems within each drawn parent,
   paired across models. Scale energy by the token share s. Compute low-side and high-side ratios per replicate.
   `GUESS 8`: the random-number generator and how the seed maps to draws (bit-exact p-values need it; statistical
   replication does not). `GUESS 9`: whether s uses each model's own tokens (implied) or a shared denominator.
9. **p-values.** `p_below` = (1 + #{high ≥ 1 or undefined}) ÷ (B + 1). `GUESS 10`: `p_above` = (1 + #{low ≤ 1 or
   undefined}) ÷ (B + 1), taking "mirror" literally; is it ≤ or <? p = min(1, 2·min(p_below, p_above)).
10. **Holm**, m = 5, over tested (non-NE) groups. `GUESS 11`: whether levels already forced NR by
    `spread_exceeded` or `drift_exceeded` enter the sort. Including or excluding them changes the other levels'
    thresholds, so this guess can flip verdicts.
11. **Interval.** `GUESS 12`: the Terms rule (115–116) or the K11 rule (361–363). `GUESS 13`: the quantile
    interpolation method.
12. **Status per group** (S2 `status`), then flag overrides: NE(`ceiling_violation`) > `spread_exceeded` (K16).
    `GUESS 14`: where `drift_exceeded` ranks (O-6 admits this).
13. **Level statuses** (S9), **pattern and L\*** (S2 `classify`, checked against S11). Replicable.
14. **Sensitivity pass.** Re-run steps 7–13 with retried items removed pairwise; if any Holm direction or L\*
    changes, report the claim unresolved (K13 d). `GUESS 15`: "pairwise" means removing the item for both models
    (implied, not stated).
15. **Cap-bound label** per cell at > 20 % capped. **Claim sentence** from S3, S6 and S10. `GUESS 16`: sentence
    forms for pooled licensing with a bracket gap, for gaps outside the bracket, and for NE gaps (O-3 admits this).
16. **Idle covariate.** `GUESS 17`: is it used in any computation, or only reported?

Result: 17 guesses. Guesses 3, 4, 6, 11 and 12 can change a printed verdict. The rest change wording or bit-exact
reproducibility only. Guesses 6, 7, 14 and 16 are already flagged as open items (O-6, O-2, O-3). The lens asks only
that the text say at the point of use that the step cannot be run until the item is ruled.

The larger structural finding: **no end-to-end procedure appears anywhere in record 07.** Steps 1–16 had to be
assembled from Terms, twenty K-clauses, eleven S-rules and the pseudocode. The clause-by-provenance layout serves
fidelity review, not replication.

## 4. Ranked fix list

**BLOCKER**

- **F1. Insert an "Analysis procedure" subsection between §2.1 Terms and §2.2 (before line 150),** following §3
  above: numbered steps from raw rows to the per-level verdict and sentence, each step citing its clause (K-n, S-n).
  Each step still waiting on an open item says so in place ("cannot run until O-6 is ruled"). This step list must
  state whether flag-forced NR levels enter the Holm sort (guess 11). If no ruling fixes that, add it as a new open
  item.
- **F2. Bootstrap: one rule, fully written, with a worked replicate and a diagram.**
  1. Rewrite Terms lines 115–116 to state the K11 endpoint rule, or mark it there as "provisional, the rule is fixed
     in K11 pending O-4". Never leave two different definitions.
  2. At line 118, write `p_above` out in full, with the comparison operator.
  3. Before K10 (line 338), add a worked replicate for one level with three parents × three problems: draws shown,
     s computed, g·s and u = k·(floor_j + anchor_j)·s computed, then the low-side and high-side ratios. Add a
     two-tier draw diagram (parents drawn with replacement, then problems within each drawn parent) with every box
     and arrow named.
  4. At line 343 and line 354, state g and k for a split parent.
  5. Name the quantile method and the RNG.
- **F3. Identify the instrument and reconcile the floors.** At line 57, name what "the power meter" is (instrument,
  rail, sampling interval) or point to Paper B's pinned setup by name with a one-line description. Gloss "energy
  rail" before K6 (310). At line 106, state how `floor_j` relates to `floor_abs_j` / `floor_cmp_j` (241). Is
  `floor_j` equal to max(floor_abs_j, floor_cmp_j) for the block's class? Gloss "class" and "P2-015 calibration
  artifact".
- **F4. Make the frozen set rebuildable.** Before K1 (257), state the eligibility predicates: what makes a reference
  "rational-valued", with two examples in and two out, and what a "plain-comma" reference is. Gloss "balanced by
  subject" and state how the n problems per level and the 16 pilot problems per level are drawn (seeded draw?
  stratified by subject within level? the same ids in both arms?). The draw is not ruled anywhere cited, so add it
  as an open item.
- **F5. Drift threshold (a verdict cannot be computed without it).** At line 375, define
  `blocks_per_cell`. Add an illustrative computation after the drift example (after 213), for example δ_upper = 2
  J/block/slot, budget_j = 50 J, 5 parents ⇒ max_gap = 5 slots, so the 2.5-slot lever passes. Also add the one
  line of algebra showing why the lever in slots × δ × blocks bounds the bias in joules.

**MATERIAL**

- **F6. Disambiguate colliding names.**
  - Claims-ladder rungs: at 89, gloss the claims ladder (the project's table of claim strengths, from descriptive
    L1 up) and write rungs as "ladder rung L2" at 89, 245 and 248, so "L2"/"L3" never collide with MATH Levels 2/3.
  - Energy vs status: rename energy `E₈` to `E_8B` in the lead-in to K11 (359 is a carry; add "here E₈ and E₁.₇
    denote each model's cell energy, not the status letters E8/E1").
  - "Window": add to Terms a sentence fixing "window" = block window unless qualified. Gloss "census-clean window"
    at 96 and 608 as "census-clean night". Gloss "problem window" (237) and "windows" at 883.
  - Capped vs truncated: add "truncated = capped" to the cap bullet (43) if that is the meaning; otherwise define
    truncated.
- **F7. Build the missing Terms before the row (insert in §2.1):**
  - "item" (= one problem inside a block) at line 56.
  - Registration, moved above Envelope (52).
  - Sizing pilot (72).
  - AP-5: one sentence on what the existing row governs and what its "synthetic ladder", "forbidden upgrade",
    "quarantine" and "affine-ladder rules" are (217, 219, 477, 693).
  - Bundle, strict-valid and the replacement rule (239).
  - Envelope pitch (265) and cap-ladder rung with its values (282).
  - Energy replicate (237).
  - Window class (235).
  - The residual-fit symbols p and d (476).
  - What "the idle reference is a covariate" does in computation, or "reported only" (240).
- **F8. §1 provenance key up front.** Move the §5 path key (723–727) into §1 after line 28. Gloss "record NN" (file
  NN in an activation's trace folder), "activation", "NN/MM" (record NN, sub-file MM), "integration synthesis"
  (the 2026-09-23 merged design record whose settled items are numbered M1–M13) and "round-1 rulings".
- **F9. Gloss pattern names before S1 (before 514).** One line each for `reverse_order`, `non_monotone`, `all_X`
  vs `one_signed_X`, `none_resolved` and `none_estimable`, taken from the pseudocode at 542–547.
- **F10. Merge order why-chain.** Before K9 (328), state why three correct and why merge toward Level 3. Add a
  numeric example (for instance 8B correct 30/25/14/6/2 and 1.7B 20/12/5/2/1 per level ⇒ Level 5 sparse ⇒ group
  4–5 has 1.7B total 3 ⇒ stop) and a five-node level-line diagram. At 336, say plainly which of K9 or S2 the reader
  should apply until O-2 is ruled.
- **F11. Retry diagram.** Line 203: replace "the smaller of its four problems' worst cases (800 s)" with "the
  smaller of the sum of its four problems' worst cases (4 × 200 = 800 s) and capacity (540 s)". Name
  `voided_block_ids` in the legend. Add a second small panel showing one innocent reschedule and the
  `single_problem` → `single_retry` → `ceiling_violation` branch.
- **F12. Spread why-chain.** At 88–90, add the physical reason for five distinct envelopes (blocks in one envelope
  share its thermal and background state, so they are not independent energy measurements).
- **F13. Ceiling-violation recapture.** Before S8 (608), gloss "copies" (the same problem run by each model) and
  "adjacent" (consecutive envelopes?). Add a numeric example (a single exceeds 200 s twice → group NE → one
  recapture night → outcome).
- **F14. Decision identifiers.** Gloss each cited D-/C-number in one clause at first use (237, 239, 242, 297, 693).
  The self-check at 896 already admits this.
- **F15. Planning interval.** At 168, gloss "×/÷ 1.59" (point ÷ 1.59 to point × 1.59) and say it is imported, not
  derivable here. Better, replace it with the F2 worked replicate.
- **F16.** Gloss "disagreement refuses" before the carry at 278. Gloss "custody path" at 888. Build "supported
  switch" in the addendum's Terms paragraph (682) before ruling (7).
- **F17.** Correct the self-check at 891–897 so it does not claim a pass the table above does not support.

**NIT**

- **F18.** Gloss or remove internal ids. Provenance header (3–4, or move to a footer); "lane" (first use); "Ed" (14,
  "the project owner"); "GSM8K leg" (12); "pinned" (40, "fixed by version and hash"); MLX (40); M4 (269) and M12
  (246); "top-up" (242); `stop_reason` (243); "boxed answer" (274); "peer number" (293); "AP-5 guard" (330); "pure
  module" (388); "the seal" (404, lead-in before the carry); "runner lane" (417); "Opus B2/S5/S6", "(Sol)" (424,
  632); A281b/A293 (446); "balanced recapture" (378); `8+1+` (569, "n letters are ignored"); Sol partition notation
  (662); "GSM8K constants and manifest" (695); E1 (261) and E3 (232), each with "Ed's pending decision on …".
- **F19.** At 153, show 47 ÷ 512 ≈ 0.092 and 192 ÷ 512 = 0.375 so the worked example's J/token figures trace to
  their source.
- **F20.** At 81, add one clause saying `single_retry` is one more attempt of a single that exceeded its worst
  case.
