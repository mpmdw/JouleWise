# Fable 5 seat (fresh)

Model: claude-fable-5, no prior context. Every fact re-read at file:line on `main` = `340f8bfc` and the two worktrees; other seat files not opened.

## 1

**The algebra checks, with one correction of scope and one sharpening.**

Confirmed at file:line:

- Point gate `g(n)·max(max|r_i|, P)` (`detection_floor.py:788-803`), `P = t·s_r·√(1+1/n) + prediction_extra` (`:697`; extra = 0 / `|mean Δ|` at `:883, :907`); `g(10) = 1` (`:670-672`); `t(9) = 2.262` (`aggregate.py:50`) × `√1.1 = 1.04881` ⇒ `P = 2.3724 s_r`. Confirmed.
- Absolute TERM B (`:822-831`): equal widths give `2h·9/10 = 1.8h`. Comparative TERM B (`:832-835`): `max_i(|d_i| + w_i)`. `not any(widths) → False` (`:816-817`); strict `>` (`:841`). Confirmed.
- Never-zero width: allowance `max(observed, 0.009724)` (`calibration_bracketing.py:211`, applied `:794`; the n=17 row is the operative one). Confirmed.
- `Σr_i² = (n−1)s_r²` ⇒ `max|r| ≥ s_r√(9/10) = 0.9487 s_r`; also `max|r| ≤ 9 s_r/√10 = 2.846 s_r`, so Regime 1 is reachable only by a single-outlier sample. Regime-2 threshold `(2.372 s_r − max|r|)/1.8 ∈ (0, 0.791 s_r]`, `0.262 s_r` at `max|r| = 1.9 s_r`. Confirmed.
- Generalisations: with unequal widths TERM B `> max|r|` whenever any width is positive, so Regime 1 holds for ANY positive width vector. Comparative: false iff `max|d| < P` and `h ≤ P − max|d|`, threshold range `(0, 2.372 s_d]`.

**Correction of scope.** "Vacuous" is too strong mathematically; "near-vacuous at this instrument's scale" is exact. The boolean is false only when `s_r > 1.26 h` (best case for falsification) to `s_r > 3.8 h` (typical `max|r| ≈ 1.9 s_r`). On the diagnostic cells the widening (2.4–2.9 J) against point floors 0.29–0.49 J (`s_r ≈ 0.12–0.21 J`) puts the falsification threshold at `≤ 0.79 s_r ≈ 0.1–0.16 J`, an order of magnitude below the width the 9.724 ms never-zero allowance alone produces at tens of watts. A hotter model pair would have to raise `s_r` ~10× before the boolean could turn.

**The sharpening.** `draft-v1.md:103` ("forcing all timing-envelope widths to zero flipped the registered dominance predicate … showing that phase-edge placement … produced the widening") is a tautology: the predicate is monotone in every `w_i` and returns `False` by construction at zero widths (`:816-817`). Delete it.

**What the boolean CAN falsify:** the claim "timing width is not negligible compared with scatter" — specifically, it fails when `h ≤ (P − max|r|)/1.8` (absolute) or `h ≤ P − max|d|` (comparative). That is a real, if weak, test: a cell with large scatter and a tight bracket could fail it.

**What it CANNOT falsify:** (i) "attribution DOMINATES scatter" — a quarter of one scatter-sd passes; (ii) any magnitude (1.1× vs 11×); (iii) the common-mode question (C3) — re-independised widths only make it MORE true; (iv) the label: `_add_attribution_limit_metadata` (`:846-857`) attaches `attribution_limited` on exactly this boolean, so nearly every production cell will carry it.

**Recommendation:** Confirm the director's algebra (with the unequal-width generalisation and the comparative range corrected as above). Treat the coded boolean as a LABEL predicate, not a falsifier of the headline. Delete the zero-width sentence at `draft-v1.md:103`.
**Strongest counter:** The boolean is not literally vacuous — it has a falsifying region (`s_r ≳ 1.3–3.8 h`) — and a reviewer may say "weak test ≠ no test." True, but a test whose falsifying region lies an order of magnitude from the instrument's operating point is a test of the wrong hypothesis.

## 2

**Which ratio.** Register `R_j = corner_widened_unguarded_floor_j / point_unguarded_j` per component — the published complete corner-maximised floor (`_corner_maximized_unguarded_floor`, `:859ff`) over the point-only floor (`:789-792`). It is the quantity the paper already prints (10.92/5.92/7.02; registry DG-050/DG-099), so no second "dominance number" appears; the guard cancels at n=10; TERM B/TERM A is strictly ≤ R (no Student-t widening at corners) and is an intermediate, not a published quantity. Report TERM B/TERM A as a column, not as the gate.

**Which threshold: R ≥ 2 per component, derived, not tuned.** `R − 1 = widening / point floor`, so `R ≥ 2` is exactly "the timing widening is at least as large as the entire scatter-only floor" — the plain-English sentence the paper already uses at `draft-v1.md:298` ("edge placement contributed more than scatter"). `≥ 3` has no such reading. Against "you picked it knowing 5.9–10.9": (i) the threshold comes from the label's own sentence; (ii) under D-164 the production pair is a different model at different power, so July-25 ratios no longer forecast `_v5`; (iii) the old 3× margin is disclosed as pilot evidence, as any pre-registration does.

**Headline rule.** "The instrument is attribution-limited" is falsified iff ANY claim-bearing component (4 cells × {absolute, comparative} = 8 components, the sixteen TERM rows at `results-fill-registry.md:197-261` already enumerate them) has `R_j < 2`. Mixed outcomes are reported per component and the null title applies. Keep the coded boolean as the label predicate for the artifact, named as such.

**Common-mode (C3).** Two ratios must exist: `R_indep` (present code, independent corners; conservative for Gate 1, kept as THE Gate-1 floor) and `R_cm` (shared fiducial term held common across the ten blocks — and, for the absolute component, across the members of one window, where a common shift cancels from residuals entirely). `R_cm` is the one that can actually be small: a shared timing shift does not manufacture a false effect between members that all shift together. GATE the headline on `R_cm ≥ 2`; REPORT `R_indep` beside it. If `R_cm` cannot be derived at the desk from the emitted shared/local split (`floor_extraction.py:486-494` composes `shared_width + local_width` per block; the absolute-member analogue must be checked), then register `R_indep ≥ 2` and print the C3 caveat verbatim — but say so before mint, not after.

**Where it lives, and what counts as "pre-registered."** The pack's identity closure (`arm_readiness.py:320-327`, `PACK_IDENTITY_KEYS`) is `plan_path/plan_sha256` plus the pack tree digests (`PACK_KEYS`, `:328ff`); there is no code-commit pin. So "minted into the pack" means bytes inside the plan tree. Options, cheapest first:

1. **Registry + RQ row only (`results-fill-registry.md`, decision log).** Declared in a document, timestamped by git before the mint. Cost ≈ 0.25 Sol-day. Not pack-bound.
2. **A registered function in `detection_floor.py`** (`attribution_dominance_ratio(estimate) → float` and a frozen `DOMINANCE_RATIO_THRESHOLD = 2.0`, exact-golden tests) plus registry rows. The paper's falsifier is then "the code, verbatim" under the same item-34 doctrine. Cost ≈ 0.5–1 Sol-day plus the review gauntlet. Git-timestamped, still not pack-bound.
3. **A registration file inside the pack tree** (e.g. a `registered_predicates.json` next to `analysis_manifest_v3.json` naming the formula, threshold, component list, and the code function's file/sha). The generator is "committed into the frozen successor pack" (`generate_configs.py:1655-1659`), and `pack_sha256` covers the tree, so this rides the `_v5` mint at ~0.5 Sol-day IF the pack digest admits an additional validated-by-hash file without a validator change. That must be verified by whoever implements it; I could not confirm it read-only.
4. **A new top-level key in `analysis_manifest_v3.json`.** `analysis_manifest_v3.py:175-186` (`TOP_KEYS`) is validated as an exact set (`:386-396`, `:691`), and the semantics digest (`analysis_semantics_sha256_v1`, `:1658`) is what D-157 byte-binds. (Brief note: the brief cites `analysis_manifest.py:37-47`, which is the older slice_2m validator; the generator writes the v3 prospective schema at `:1663`, and that validator's DESIGN_KEYS already carry `analysis_type`/`null_alias`.) This is a contract change ⇒ generator + validator + tests + D-157 "mint-path change ⇒ S-0 re-runs as a new estate." It fits inside the `_v5` re-generation ONLY if it lands before estate 12's clone proof; realistically +1–2 Sol-days on the transaction's critical path and one more thing that can refuse on the night.

**Recommendation:** Do 2 + 3 (code function with frozen threshold; hash-bound registration file in the pack tree), with 1 as the paper-side trace. Do NOT do 4. Gate on `R_cm ≥ 2` if derivable, else `R_indep ≥ 2` with the C3 caveat printed. Budget 1 Sol-day, inside the D-164 `_v5` window, no extra estate.
**Strongest counter:** Option 3 may be refused by the pack digest/plan-tree validator, collapsing to option 2 — a git-timestamped registration that a hostile reviewer can call "declared, not minted." Answer: git history before the mint commit is the standard the field accepts (OSF-style timestamped registration); the pack-internal digest is a stronger bar the project set for itself, not a bar the paper needs.

## 3

The steelman for leaving item 34 as ruled:

1. **Verbatim-code discipline is the defence against post-hoc aggregation.** Item 34 exists because an invented aggregate was caught; the boolean is what the artifact computes, replay-fenced, with sixteen registry rows already written to it. A thresholded ratio is a NEW number with a NEW threshold argument — the class of desk invention item 34 forbade.
2. **Not vacuous, and conservative in the right direction.** A falsifying region exists (`s_r ≳ 1.3–3.8 h`), and a cell where timing width is even a quarter-sd is already one where more repetitions will not help — the paper's practical message at `draft-v1.md:298`.
3. **A threshold of 2 has no more standing than 1.** Both are conventions; registering one invites attack on the threshold instead of the phenomenon.
4. **The ratio reported descriptively already carries the weight.** Readers judge 10.9 vs 1.2 themselves; a metrology paper's contribution is the bound, not a hypothesis test.
5. **Schedule.** D-164 spent the budget on the model swap; a falsifier change touches code, registry, RQ row, possibly the manifest, on the path to 09-01/02.

**Recommendation:** Reject the steelman on points 1–4 (a threshold derived from the label's own sentence is not an invention; a falsifier that cannot fail at the operating point is not conservative, it is decorative), but honour point 5 by keeping the registration off the manifest contract.
**Strongest counter:** Point 4 is genuinely strong — if the paper drops "dominance" from the headline and reports R descriptively, item 34 stands and no falsifier is needed. That is a different paper (bound-only, no phenomenon claim); it is the S8 null-outcome paper written in advance.

## 4

The two-title device answers the objection rather than violating it. Naming the outcome-conditional framing BEFORE collection is the opposite of steering; a single title chosen now either commits to the phenomenon before its falsifier runs or commits to the null and quietly rewrites if dominance reproduces — exactly the steering the reviewer feared. The device only signals steering if the branch rule is hidden. Make it explicit: the registry title row states the falsifier (`R_cm ≥ 2` on all eight components) and which title each outcome selects; both titles in git before mint. That is a registered outcome-contingent title, a recognised pre-registration form.

**Recommendation:** Keep item 28, amended: the title row names the falsifier and the branch rule, both titles are committed pre-mint, and the paper's methods section discloses the branch in one sentence. Replace "if `_v4` reproduces dominance" with "if the registered dominance ratio passes."
**Strongest counter:** Reviewers reading only the paper will not see the registry; a title that changes with the result still reads as spin unless the disclosure sentence is present. If Ed will not print the disclosure, drop to the single protocol-first title.

## Arithmetic

- `t(9) = 2.262` (`aggregate.py:50`); `√1.1 = 1.048809`; `P = 2.3724 s_r` (`detection_floor.py:697`); `g(10) = 1` (`:670-672`, `:108`).
- `1.8h` (`:822-831`); `max|d_i| + w_i` (`:832-835`); `not any → False` (`:816-817`); strict `>` (`:841`); label (`:846-857`); `prediction_extra` (`:883, :907`).
- `0.9487 s_r ≤ max|r| ≤ 2.846 s_r` from `Σr_i² = (n−1)s_r²` (`:695`); Regime-2 threshold `(0, 0.791 s_r]`, `0.262 s_r` at `1.9 s_r`; comparative `(0, 2.372 s_d]`.
- `0.009724`, `max(observed, screen)` — `calibration_bracketing.py:211, :794`.
- 0.2888/0.4934/0.3113 J; 3.153/2.922/2.184 J; 10.92/5.92/7.02 — `draft-v1.md:103, :298`; DG-050 (`results-fill-registry.md:606`), DG-099 (`:655`). Recomputed: 10.918, 5.922, 7.016. Implied `s_r ≈ 0.12–0.21 J`, widening 2.4–2.9 J.
- v3 `TOP_KEYS` exact set — `analysis_manifest_v3.py:175-186, :386-396, :691`; semantics digest `:1658`; older `analysis_manifest.py:36-55` is the slice_2m validator, not the `_v5` schema.
- `PACK_IDENTITY_KEYS` — `arm_readiness.py:320-327`; `PACK_KEYS` `:328ff`.
- Generator — `…wt-s8-d139-families/…/generate_configs.py:1655-1659, :1663, :1681-1735`.
- D-164 — `decision_log.md:191`; ruling items 28/34 — `03-MAGISTRATE-RULING.md:229-233, :265-268`; synthesis — `04-SYNTHESIS.md:27-47, :163-165, :189-199, :244`.
- Common-mode `shared_width + local_width` — `floor_extraction.py:447-494`; ten independent widths → `comparative_false_effect_floor` `:620-633`.

## Confidence

High on 1 (every step re-derived at file:line); medium-high on 2 (threshold defence and cost tiers are solid; whether the pack digest admits an extra hash-bound file is unverified); medium on 3–4 (judgment calls, argued not measured).
