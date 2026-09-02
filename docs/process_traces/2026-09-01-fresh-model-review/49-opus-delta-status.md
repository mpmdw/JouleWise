<!-- Opus 5 delta re-audit of PROJECT_STATUS fix round 1 (Sol, report 47) on PR #253 @ a915a9c7. Harvested 2026-09-01. -->

**Magistrate note (2026-09-01):** VERDICT SHOULD-FIX — all 32 round-1 items cured, substantive
claims verified against primary sources (max-not-sum at `detection_floor.py:764`; four-corner scan
`reduce.py:2225-2244`; D-078 cl.11 range and ~5 J disclosure). Residual = 9 first-use items + 5
uncited numbers. Round 2 (Sol high) applies the dictated glosses verbatim. Cold-gate trigger
assessed: NOT fired — no round-1 defect is being re-fixed (P1 is new, introduced by the A2 cure;
P2 is a distinct term the italic-only checker could not see); the CLASS recurs, the defect does
not. Recorded here so the reading is visible to Ed.

## Delta re-audit — PROJECT_STATUS.md @ `a915a9c7` (PR #253, worktree `/Users/edr/code/JouleWise-wt-status`)

Read-only. No file edited, no git write run. All line numbers below are `PROJECT_STATUS.md` at HEAD unless another file is named.

---

### 1. Item-by-item verdicts

| item | verdict | line | note (source verified against) |
|---|---|---:|---|
| A1 registered semantics | **PASS** | 81–88 | Rule-text → SHA-256 → "edit after data arrive would be visible" all present; golden readback correctly described as pinning threshold + refusal. Verified: `configs/campaigns/d117_contrast_v5/generate_configs.py:2597-2603` (`frozen_semantics_sha256 = analysis_semantics_sha256_v1(manifest)`), `tests/test_d117_contrast_v5_pack.py:518,536,544` (readback detects threshold and all-must-pass mutations). See P8 for a naming nit. |
| A2 "worst admitted energy change" | **PARTIAL** | 104–113 | **Substance is exactly right**, verified line by line: four boundary corners = `for eps_on_s in (-e,e): for eps_off_s in (-e,e)` at `joulewise/reduce.py:2225-2244`; "scans the remaining shared clock shift across the exact power-trace breakpoints" matches that function's own docstring (`reduce.py:2158-2161`, "the remaining `delta_common` dimension is evaluated by the existing breakpoint-exact scanner"); "chooses the low or high end of every interval … keeps the largest" = `_corner_maximized_unguarded_floor`, `joulewise/detection_floor.py:894-913` (`for mask in range(1 << n)`); **"the larger of that corner result and the naive floor; the two are not added"** = `_apply_admissible_set_guard`, `detection_floor.py:764` (`unguarded = max(estimate.unguarded_floor_j, uncertainty_floor_j)`). PARTIAL only because the cure violates the brief's "do not add a new term of art": "timing-**bracket** corners" introduces *bracket* 338 lines before its gloss and in a second sense (P1). |
| A3 *rung* | **PASS** | 136 | "Each candidate length is called a *rung*." First occurrence in the file is 136 (verified by scan). |
| A4 *block* | **PASS** | 99–100 | "one paired *block* is four consecutive runs in small, large, large, small order, placing each model on both sides of the pair so slow drift tends to cancel." First occurrence is 99. |
| A5 *frozen* before *pack* | **PASS** | 10–11 vs 23 | Glossary order corrected. |
| A6 ratio order | **PASS** | 115 | "timing-aware floor divided by the naive floor" = `dominance_ratio(corner_widened_unguarded_floor_j / point_unguarded_floor_j)`, `feat/d165-dominance-closeout-core:joulewise/dominance_closeout.py:191-212`; independently confirmed at `docs/process/v5-artifact-flow.md:24` ("R is the corner-widened floor divided by the point floor"). |
| A7 "three model families" | **PASS** | 159–162 | Phrase gone; sole surviving "model family" is line 235, where it correctly means the *models under test* (Qwen2.5→Qwen3). |
| A8 *shakedown* | **PASS** | 152–154 | Glossed at first use. |
| A9 *desk day* | **PASS** | 149–151 | Glossed at first use, with the contamination reason. |
| A10 "ruled follow-ups" | **PASS** | 310, 486 | "have been decided and scheduled but not yet built"; `grep -c "ruled"` = 0. |
| A11 step-5 jargon chain | **PASS** | 469–477 | Nine-noun chain replaced by six named program actions. |
| A12 Window A | **PASS** | 193 | "the July 2026 calibration campaign—222 run bundles, internally labelled Window A". |
| A13 six category labels | **PASS** | 194–196 | Rewritten as granularity prose. |
| A14 environment guard | **PASS** | 204–206 | "refuses a run if anything else on the machine, such as a screensaver or background process, could add power draw." |
| A15 *members* | **PASS** | 136, 442, 449 | `grep -c -i "member"` = 0; "runs" throughout. |
| A16 thinking disabled | **PASS** | 462–464 | "Qwen3's optional reasoning mode switched off, so the model emits no hidden deliberation tokens." |
| A17 three-rung ladder | **PASS** | 538 | "three-stage ladder"; *rung* now carries one meaning only. |
| A18 "roots" | **PASS** | 466–467 | "separate directories, so no diagnostic bundle can enter a claim." |
| A19 whole-window verdict / claim engine | **PASS** | 325–328 | Verdict glossed in situ; "claim engine" → "the program that evaluates each registered comparison against the floor". First use of "whole-window" is 325. |
| A20 *prospective* | **PASS** | 12–13 | Glossary. |
| A21 admitted/admissible | **PASS** | 14–15 | `grep -c -i "admissible"` = 0; *Admitted* glossed at 14, first non-glossary use at 26. |
| A22 *gate* | **PASS** | 16–17 | Glossary, before first use at 20. |
| A23 *governed* | **PASS** | 18–19 | Glossary. |
| A24 *producer* | **PASS** | 168–169, 481 | `grep -c -i "producer"` = 0. |
| A25 "three-seat" | **PASS** | 634 | `grep -c -i "seat"` = 0. |
| A26 agent-free window | **PASS** | 571 | Physical reason stated ("nothing else draws measurable power"). |
| A27 *unmatched* | **PASS** | 218 | "never collected as matched pairs". |
| A28 time anchor | **PASS** | 174–178 | Two-clock mechanism now arrives in the same sentence as the term, before the void claim. |
| **B1** repeatability range | **PASS** | 179–181 | Exact: "0.7-1.0 J per run" / "0.29-0.49 J repeatability noise on ~50 J points" — matches D-078 cl.11 verbatim at `docs/decision_log.md:4726-4733`. `grep -n "0\.3"` = no hits; the optimistic-edge figure is gone. |
| **B2** single-count disclosure | **PASS** | 181–185 | "the effective clearable effect is floor plus claim-side bound (~5 J for phase contrasts), not the floor alone. The registered rules require this disclosure wherever an attribution-limited floor is published." — matches `docs/decision_log.md:4768-4779` ("effective clearable effect is FLOOR + CLAIM-SIDE BOUND (~5 J for phase contrasts) … Every artifact publishing an attribution-limited floor must state this explicitly"). See N1: the bullet carries no D-078 pointer. |
| B3 "fifth" | **PASS** | 75–77 | "a regeneration of the same frozen design under the new model pair … the superseded `_v4` family will not be collected (newer-model decision D-164)" — matches D-164 (`docs/decision_log.md:192` index row, `:10365-10373`). `grep -c "fifth"` = 0. |
| B4 reviewer provenance | **PASS** | 161–162 | "blind to each other and ran as separate sessions across more than one vendor's large-language model." |

**Brief-mandated verification controls, checked substantively:**

| control | verdict | evidence |
|---|---|---|
| Ratio count ("every component in every cell" quantifier) | **PASS** | 116–118 "exactly eight ordinary cases—an absolute and a comparative component in each of four registered cells"; 119–120 "Four additional comparative ratios"; 128 "All eight ordinary ratios and all four required shared-shift ratios must pass." Matches D-168 at `docs/decision_log.md:195` ("exactly eight ordinary ratios and four comparative R_cm values") and D-165 R-5 (`:10385-10396`), where *absolute* R_cm is registered `not_applicable` — the word "required" at line 128 correctly carries that scoping. |
| Neither-branch rule | **PASS** | 130–132, verbatim against `docs/decision_log.md:195` ("any missing, unauthenticated, or zero-denominator result selects NEITHER branch and stops filling"). |
| *replay* glossed as recomputation | **PASS** | 121–122 "a recomputation from stored, authenticated inputs, not another experiment." Matches `v5-artifact-flow.md:24`. |
| Worked example, labelled | **PASS** | 124–128, opens "Illustrative, not campaign data", and correctly shows a case passing the ordinary ratio while failing the shared-shift ratio — the exact asymmetry D-165 rules on. |
| ≥5-runs as a **selection precondition** | **PASS** | 137–138 and 449–450: "a rung with fewer than five small-model runs is unevaluable and cannot be selected." Matches the code, not the stale index prose: `scripts/select_g2a_prefill_length.py:103-107` gates on `row["small_members"] >= MIN_SMALL_MEMBERS` **and** `row["all_small_count_ge_5"]`, with `MIN_SMALL_MEMBERS = 5` (`:18`). D-166's index row still says "a rung with **no** small-model members is unevaluable", but its own bracketed amendment ("G2-a sweep (≥5 members/rung) made the selection's precondition") and the code both say five — the document follows the code. Correct call. |
| "power record" physical meaning | **PASS (substance)** | 141–143 "one sampling interval of the Apple power meter—requested every 100 milliseconds, with its actual interval stored in the run." Verified: `configs/campaigns/d117_contrast_v5/generate_configs.py:494` `SAMPLING = {"power_hz": 10.0, …}` and `joulewise/adapters/powermetrics.py:1461-1462` `interval_ms = max(1, round(1000/power_hz))` → 100 ms; the "actual interval stored" claim is consistent with line 428 ("Requested and observed sample rate … travel with the evidence"). See N2 — no citation on the page. |
| why five = 3 + 2 | **PASS** | 143–144 "the reducer's physical minimum of three records plus a declared pre-registration safety factor of two." Matches `select_g2a_prefill_length.py:19,23` (`MIN_OVERLAPPING_POWER_INTERVAL_COUNT = 5`, `PREREGISTERED_MIN_PHASE_SAMPLES = 3`) and D-166 (`docs/decision_log.md:193`, "the floor is the physical rule, the +2 a declared pre-registration safety factor"). |
| Glossary first-use table | **PASS with one residual** | I re-ran the check independently rather than trusting the report. All 23 glossary terms are defined at 10–48 and used later; no term is used before its definition. **One miss:** Sol's checker scans only italicised terms, so it did not catch *estimator*, used inside the *cell* definition at line 33 and defined nowhere (P2). |
| Naive-floor definition ("residual from what") | **PASS** | 94–103. Absolute: "one run's energy minus the mean energy for that cell … the larger of the largest residual magnitude and the 95% prediction from their scatter" = `_floor_estimate`, `detection_floor.py:689-699` (`unguarded = max(max_abs, prediction)`). Comparative: "each block's small-versus-large energy difference … the larger of the largest magnitude of such a difference and the 95% prediction from the differences' mean and scatter" — correctly captures `prediction_extra = abs(mean)` (`detection_floor.py:958`, "deltas are never re-centered"). |
| Ancillary state claim spot-check | **PASS** | "three final Qwen3 packs" (452) = one contrast pack (`v5-artifact-flow.md:9`, `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/`) + two per-arm floor packs (`generate_configs.py:1122-1125`, `FLOOR_PACKS` for arms A and B). All five in-flight branches at 165–170 exist (`feat/2026-09-01-skeleton`, `-dependence`, `feat/transfer-fiducial-01`, `feat/d165-dominance-closeout-core`, `feat/2026-09-01-g2a-probe`) and none is claimed as landed. `joulewise/dominance_closeout.py` is absent from this worktree and the document correctly does **not** claim it as landed. |

---

### 2. Pedagogy pass — residual and newly-introduced first-use failures

| id | sev | line | term | reader will misread it as | gloss I would dictate |
|---|---|---:|---|---|---|
| **P1** | **should-fix** (new, introduced by the A2 cure) | 106 | "the four calibrated **timing-bracket corners**" | *bracket* first appears here, 338 lines before its gloss at 444 ("calibrated reference measurements before and after the probes") **and in a different sense** — here it means the ± limits of a timing-uncertainty interval. "Corner" is also unbuilt: there is no geometry on the page for it to be a corner *of*. | Delete the coinage: "…displaces the start boundary and the end boundary independently to the low and high limits of the calibrated timing uncertainty — two boundaries at two limits each, so four combinations — and at each combination scans the remaining shared clock shift…" |
| **P2** | **should-fix** (residual A5-class) | 33 | "a combination of model, workload phase, and **estimator**" | an unglossed term inside a glossary definition — the exact defect A5 was raised for; used once, defined never | "…of model, workload phase, and which of the two formulas below produces the number." (The *component* sentence immediately after already carries the real distinction.) |
| **P3** | **should-fix** | 143 | "Five is the **reducer's** physical minimum of three records" | *reducer* is first explained 202 lines later, inside a code block at 345 — and this sentence is precisely where a metrology reader decides whether 5 is conservative or arbitrary | "Five is three plus two: three is the fewest power samples the energy-integration program can compute a phase's energy from at all, and two is a safety factor declared in advance." |
| **P4** | **should-fix** | 116 | "timing attribution dominates **repeatability**" | *repeatability* is one side of the headline test and is never glossed; the nearest gloss is at 181, and *timing attribution* is built at 404–408, ~290 lines later | "For the paper to say that error in placing the measurement boundaries in time matters more than the spread seen when the same run is repeated with nothing changed, this ratio must be…" |
| **P5** | should-fix | 167, 414, 554 | "the ten-block **direction test**" / "the ten-block **direction screen**" / "Ten paired blocks" | two names for one object, and neither says what a direction test *is* | Pick one name and build it once: "the ten-block test of *which* model uses more energy — its direction, not its size". |
| **P6** | nit | 417 vs 287 | **marginal** | at 287 it means the per-token slope of the fixed-plus-marginal energy model; at 417 it means a per-arm confidence interval. One word, two meanings — the A17 defect class | 417: "…not the fact that two separately computed one-model intervals happen not to overlap". |
| **P7** | nit | 419 | "**practical equivalence** requires its own predeclared gate" | one use, unglossed term of art | "a claim that two models are practically the same requires its own threshold, declared in advance, for how close counts as the same." |
| **P8** | nit (traceability) | 83 | coinage "*registered semantics*" | the pack, D-165, and the generator all call this `frozen_semantics_sha256` / "analysis semantics"; an advisor grepping the repository for "registered semantics" finds nothing | "…as a body of text called the *frozen analysis semantics*" (`generate_configs.py:2597-2603`). |
| **P9** | nit | 433 | "the registered **supersession** procedure" | single unglossed use | "…follows the recorded procedure for replacing a superseded run, which keeps the original in place." |

**Numbers stated with no source the advisor could open:**

- **N1 (should-fix), 179–187.** The attribution bullet carries four load-bearing numbers — 0.7–1.0 J, 0.29–0.49 J, ~50 J, ~5 J — and **no citation**; the D-078 pointer sits at the end of the *previous* bullet (178). D-078 clause 11 itself makes the ~5 J statement mandatory wherever an attribution-limited floor is published (`docs/decision_log.md:4768-4779`), so the pointer belongs on this bullet: append "(measurement-soundness decision D-078, clause 11)" after "…not the floor alone."
- **N2, 142.** "requested every 100 milliseconds" — correct but unopenable from the page (`configs/campaigns/d117_contrast_v5/generate_configs.py:494`; `joulewise/adapters/powermetrics.py:1461-1462`).
- **N3, 193.** "222 run bundles" — the "Technical record" pointer at 201 is a different document and does not carry the count; it lives at `docs/council_log.md:1536` and `docs/stream_logs/2026-07-17-topdocs.md:11,34`.
- **N4, 128.** "eight ordinary ratios and … four required shared-shift ratios" — D-168 is cited four lines later at 132; attaching the ID to the counts would close it.
- **N5, 408.** "approximately 1-joule attribution limit" restated 230 lines from its only citation.

Passes worth recording: `thesis` 0, `admissible` 0, `member` 0, `producer` 0, `seat` 0, `ruled` 0, `Holm` 0, `0.3` 0. Decision IDs follow the plain-description-then-ID pattern at 77, 113, 132, 146, 178, 393. No volatile counts.

---

### 3. Bench

```
$ cd /Users/edr/code/JouleWise-wt-status
$ python3 -m unittest tests.test_paper_terms_lint tests.test_gen_state
unittest exit=0
...........................................
----------------------------------------------------------------------
Ran 43 tests in 2.094s

OK

$ git -C /Users/edr/code/JouleWise-wt-status diff --check
(no output)
diff --check exit=0

$ git status --porcelain
(clean)
```

---

### 4. Assessment

Every one of A1–A28 and B1–B4 is cured; 31 of 32 are clean PASSes and A2 is PARTIAL on pedagogy only. I verified the substantive claims against primary sources rather than checking that sentences changed, and the two hardest ones came back exactly right: the timing-aware floor really is a **max** against the naive floor and not a sum (`detection_floor.py:764`), and the four-corner + breakpoint-exact-scan description matches `reduce.py:2225-2244` clause for clause. B1/B2 reproduce D-078 clause 11's range and its mandatory ~5 J single-count disclosure faithfully. The ≥5 selection precondition follows the **code** where D-166's index prose is stale — the right call, and one a less careful fix would have gotten wrong. No factual error about project state and no wrong physical claim survives.

What remains is nine first-use failures, two of them in load-bearing places (P1 at the numerator of the headline test, P3 in the justification of the count floor), plus five numbers the advisor cannot trace from the page — of which N1 is the one that matters, because D-078 clause 11 makes that disclosure mandatory and the bullet carrying it has no pointer to the decision that requires it. P1 and P2 are worth naming as a pattern: the A2 cure imported a new term of art (the brief forbade this), and the glossary self-check missed *estimator* because it only scans italicised terms — the checker cannot see an unglossed term hiding inside a glossary definition.

VERDICT: SHOULD-FIX
