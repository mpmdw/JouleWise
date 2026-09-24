# 18 — A282 v2 pedagogy delta re-audit (Opus 5.5, read-only) on record 07b

Lens: pedagogy only, to the same standard as record 12. The question is whether a technical reader with no project
grounding could REPLICATE the mechanism from `07b-a282-ap5m-draft-v2.md` alone. Line numbers refer to 07b at 1,208
lines. Source fidelity is not re-checked. I recomputed the new worked examples (§2.3 sampling spread, §2.4 merge,
§2.5 replicate, §2.6 drift threshold and panel 2), and every figure matches its stated inputs.

Verdict key: FIXED; PARTLY; NOT FIXED; FIX INTRODUCED A NEW DEFECT. Severity key as in record 12: BLOCKER / MATERIAL /
NIT.

## 1. Record 12's fixes, one by one

### BLOCKERs

| Fix | Verdict | Evidence |
|---|---|---|
| **F1** end-to-end procedure; Holm membership of flag-forced levels | **FIXED** | §2.2 (226–266) gives 15 steps, each citing its clause. Step 10 (252–256) states the O-5 question and says why it can flip a verdict. Residual (NIT-plus): three open items that bear on verdicts are listed in §6 but not flagged at the step that needs them. O-6 (spread in merged groups) belongs at step 4 (239). O-10 (retry tails across nights, which changes positions) belongs at step 5 (241). O-9 (recapture-check failure) belongs at step 13 (261). |
| **F2** bootstrap: one interval rule, `p_above`, g and k for split parents, worked replicate, diagram, RNG and quantile | **FIXED** | One interval rule appears at 191–192, 257 and 614–617, with point-bound widening moved to O-4. `p_above` is written in full at 194–195. g and k for split parents are at 236–238 and 602. The worked replicate and two-tier diagram are at 313–356, with every element named at 342–344; the arithmetic checks (R\* 1.9221, low 1.9173, high 1.9270). RNG and interpolation are at 594. NIT: the Terms statement at 191–192 does not flag O-4, though step 11 does. |
| **F3** instrument identity; floor constants reconciled | **PARTLY** | Instrument: fixed. powermetrics at 100 ms, SoC-package boundary, rail manifest (81–86); "energy rail" tied to M13 (85). Floors: `floor_abs_j`, `floor_cmp_j`, window class and P2-015 are all glossed (108–117). But `floor_j` is only "the per-window floor value" (119). Whether it equals max(floor_abs_j, floor_cmp_j), and whether the floor belongs in the widening at all, is left to O-12 (1156–1162). That is honest, and step 2 flags it (234–235), but step 7 (245–246) uses `floor_j` without the flag. This is now a ruling gap, not a writing gap. |
| **F4** eligibility predicates; how problems are drawn | **FIX INTRODUCED A NEW DEFECT** | Predicates, examples, per-level counts and the keyed round-robin draw by subject are at 474–489: fixed. New defect (MATERIAL): 478 lists "grouped integer" among forms that qualify, and 479 then excludes `1,000` as a "plain-comma" reference. `1,000` is the ordinary example of a grouped integer, so the predicate reads as self-contradictory. It needs "grouped integer (thousands grouped by a TeX `{,}` or thin space, not a plain comma)" or the importer's exact forms. NIT: the "fixed domain string" and the content-hash fields (483) are given only by pointer to code. |
| **F5** drift threshold: define `blocks_per_cell`, give illustrative numbers and the algebra | **FIX INTRODUCED A NEW DEFECT** | Now defined: `blocks_per_cell` as parent blocks per cell per model (629, O-7), P in §2.1 (171–173), and a worked threshold at 396–399. New defect (MATERIAL): the derivation at 171–173 starts from "a block's energy shifts by at most δ_upper joules per slot of position" (a bound on the drift's slope) and concludes "the between-model bias is at most δ_upper × P × lever". That holds only if the drift is **linear** in envelope index with a slope common to both models. Counterexample: 8B parents at positions 0 and 10 (mean 5), 1.7B parents at 5 and 5 (mean 5), lever 0, drift f(x) = δ·\|x − 5\| (slope never above δ). The 8B sum shifts by 10δ and the 1.7B sum by 0, so the bias is 10δ against a stated bound of 0. Version 1 said "cancel a drift that is linear in time"; version 2 dropped the word. Fix: state the linearity assumption in §2.1 before the bound. The K6 carry at 542 already implies it. δ_upper and budget_j values remain O-7, and step 5 flags this (242). |

### MATERIAL

| Fix | Verdict | Evidence |
|---|---|---|
| **F6** name collisions | **FIXED** (the four named) | Claims-ladder rungs: 154–158, 464. E₈ vs E8: 183–185, 606–607. "Window": 100, 102–103, 503, 889. Capped = truncated: 70. The new text adds new collisions (§2, rows N5, N7, N9, N18, N22, N23, N24). NIT: 157 says "this file always writes 'rung L2'", but the verbatim row carry at 467 reads "Ceiling L2"; add "outside carries". |
| **F7** missing Terms | **FIXED**, one partial | Built before use: item (64), registration moved first (55), sizing pilot (124), AP-5 and its forbidden upgrade and quarantine (433–438; AP-5's first use is 432, so the gloss arrives in time), bundle, strict-valid and replacement rule (159–162), pitch (88), energy replicate (455), window class (114), residual-fit symbols (725–726), idle covariate report-only (459, 530). Capacity is PARTLY fixed: `interior_s − guard_s` at 92, but "working interior" is not built (self-admitted at 1202). |
| **F8** provenance key up front | **FIXED** | 24–42. |
| **F9** pattern names before S1 | **FIXED** | S0 at 777–782; §2.1 points to it (212). |
| **F10** merge why-chain, numbers, diagram, K9 vs S2 | **FIXED** | The why is at 292–294. The diagram at 296–307 names every element. Numbers at 309–311 check (group 4–5: 8B 8, 1.7B 3). S2 governs, and O-2 is flagged at 309. The regression from this change is logged as N12. |
| **F11** retry diagram wording, `voided_block_ids`, second panel | **FIXED** | Wording at 386–387, `voided_block_ids` named at 387–389, panel 2 at 401–428. NIT: the legend does not say why the rescheduled single goes to envelope 23 rather than 22 (22 is full: 400 s + 200 s > 540 s), or what 22 holds in the alternative history. |
| **F12** spread forcing problem | **FIXED** | 164–165. |
| **F13** ceiling-violation recapture | **FIXED** | "Copies" at 889–890; worked at 421–428. "Adjacent" = consecutive is the seat's own reading, flagged as such at 426. |
| **F14** decision codes | **FIXED** | D-062 (58), D-047.6 (75), D-045.7 (99), D-078 (116), C-004 (437), D-047.3 (456). |
| **F15** "×/÷ 1.59" | **FIXED** | 284–288, with a delta-method derivation that checks (SE 0.237 gives 1.59; SE 0.168 gives 1.39). |
| **F16** "disagreement refuses", "custody path", "supported switch" | **FIXED** | 510–511, 1185–1186, 213 and 969–970. |
| **F17** correct the self-check | **PARTLY** | See §4. |

## 2. Fresh first-use pass over v2's new text only

New or rewritten text covered: the §1 key, §2.1 additions, §2.2 procedure, §2.3–§2.6 worked examples, §2.7 AP-5
gloss, the K1 draw, the K2/K3/K6/K9–K13/K20 lead-ins, K21, S0, the S6 proposed template, the §4 lead-in, the O-items
and §7.

| # | Term | Line | Verdict | Sev. | Note / fix |
|---|---|---|---|---|---|
| N1 | seat, activation, record, work item | 3–4, 24–25 | GLOSSED-AT | — | |
| N2 | "council entries" | 42 | FAILS (never) | NIT | |
| N3 | PRM800K, MLX, pinned, top-up, stop_reason, boxed answer | 56–73 | GLOSSED-AT | — | |
| N4 | "adapter's rail manifest" | 83 | FAILS (never) | NIT | "adapter" = the project's per-instrument reader |
| N5 | "per-record energy counters … falling in it" | 86 | FAILS | NIT | "record" collides with project records (24); how a 100 ms sample straddling a window edge is handled is unstated (≤ one sample of energy; within the ~1 J floor) |
| N6 | `interior_s`, `guard_s`, "working interior" | 92 | FAILS (parts never built; self-admitted) | NIT | |
| N7 | "arm time" | 105 | FAILS (collision) | NIT | "arm" is built at 66 as a thinking mode; here it means scheduling the night |
| N8 | `codex\|claude\|t3` | 105 | FAILS | NIT | the project's AI-agent processes |
| N9 | "spread" (statistical) in the floor definitions | 110–111 | FAILS (collision and unquantified) | MATERIAL | "spread" is built at 163 as a count of parents and envelopes. Here it means measurement dispersion of unstated form (SD? 2σ? range?), and it defines the floor value |
| N10 | A-B-B-A, window class, attribution-limited, D-078 | 111–117 | GLOSSED-AT | — | |
| N11 | drift bound derivation | 171–173 | FIX INTRODUCED A NEW DEFECT | MATERIAL | linearity unstated; see F5 |
| N12 | "denominator guard" (defines *sparse*) | 202 | FAILS (meaning at 292 and 571) | MATERIAL | Regression: v1's Terms said "fewer than 3 correct". Fix: "(at least 3 correct per model per level; exact reading O-2)" at 202 |
| N13 | "reducer" | 232 | FAILS (glossed at 511) | NIT | |
| N14 | "balanced recapture" | 264 | FAILS (glossed at 630) | NIT | |
| N15 | "three-way test" | 259, 457 | FAILS (defined at S2, 791) | NIT | pointer; add "(Holm rejects, p gives the direction, and the interval lies wholly on that side)" |
| N16 | planning SE, "binomial spread … on a log scale" | 285–287 | GLOSSED-AT | — | |
| N17 | merge diagram elements | 296–307 | BUILT-BEFORE | — | |
| N18 | "drawn slots", "slot" | 334, 342 | GLOSSED-AT | NIT | collides with envelope slot and idle slot; "draw #1, #2, #3" would avoid it |
| N19 | K1 "grouped integer" vs `1,000` | 478–479 | FIX INTRODUCED A NEW DEFECT | MATERIAL | see F4 |
| N20 | "problems per bundle" (inside a carry) | 498 | FAILS | NIT | build before the carry: here it means block size |
| N21 | "balance search" (inside a carry) | 548 | FAILS | NIT | |
| N22 | "magistrate ruling B1/B2" | 569, 612 | FAILS (collision) | NIT | collides with B = replicate count and with packet B |
| N23 | K21 "checks E1–E4", "E5 (early-stop bias)" | 747, 751, 1152 | FAILS (collision) | MATERIAL | E1–E4 are Ed's four decision questions at 20–21 and in O-17…O-20; here they are smoke-gate checks. Rename them "smoke checks SG1–SG4" in the lead-in; "early-stop bias" is unglossed |
| N24 | "Record 11 M6 and the magistrate's ruling M6" | 752 | FAILS (collision) | NIT | M-numbers are built at 31 as record 19's settled items |
| N25 | S0 pattern names | 777–782 | BUILT-BEFORE (S1, 786) | — | |
| N26 | S4 `8+1+` | 834–835 | GLOSSED-AT | — | |
| N27 | S6 proposed template and rules | 869–881 | BUILT-BEFORE | — | the three examples apply the rules consistently |
| N28 | §4 lead-in (MATH importer, GSM8K constants) | 958–959 | GLOSSED-AT | — | |
| N29 | "4–5 nights a day" | 1179 | FAILS (jarring) | NIT | "night" is built as a capture session; say so here |
| N30 | "custody path" | 1185 | GLOSSED-AT | — | |
| N31 | step 7's `floor_j` | 245–246 | FAILS (value open, not flagged here) | NIT | add "(value: O-12)" |

New findings: **20**. That is 18 FAILS (N2, N4–N9, N12–N15, N20–N24, N29, N31) plus 2 defects introduced by fixes
(N11, N19). **5 are MATERIAL** (N9, N11, N12, N19, N23) and 15 NIT; N18 is glossed and counted as a NIT naming note
only. **No new BLOCKER.**

## 3. Replication rerun from v2 alone

This is record 12 §3's procedure, now from §2.2. Of record 12's 17 guesses, these are resolved: capped vs truncated
(1), "disagreement refuses" (2), g and k for split parents (4), `blocks_per_cell` (5), RNG and quantiles (8, as
proposed text), s per model (9), `p_above` (10), pairwise removal (15), idle covariate (17), and the K9-vs-S2 merge
rule (7).

Remaining guesses:

| # | Guess | Flagged as open item? | Flagged at the procedure step? | Can change a verdict? |
|---|---|---|---|---|
| G1 | Value of `floor_j`; whether the floor belongs in the widening; the block-window floor gate | O-12 | step 2 yes, step 7 no | Yes, at the knife edge (the bound is ~0.1 % of sampling spread); step 2 cannot run at all |
| G2 | δ_upper, budget_j; rank of `drift_exceeded` against NE | O-7 | steps 5, 12 yes | Yes |
| G3 | Denominator guard: observed count vs statistical lower bound | O-2 | step 6 yes | Yes (changes the partition) |
| G4 | Whether flag-forced NR levels stay in the Holm sort | O-5 | step 10 yes | Yes |
| G5 | Whether point bounds widen the interval ends | O-4 | step 11 yes | Yes, at the knife edge |
| G6 | Spread-exceeded constituent of a merged group | O-6 | **no** (step 4) | Yes |
| G7 | Positions of retry tails that spill into another night | O-10 | **no** (step 5) | Yes (via the drift lever) |
| G8 | Consequence of a failed `s_per_token_upper` check on the recapture night | O-9 | **no** (step 13) | Yes (L\* withheld or not) |
| G9 | **Which attempt supplies correctness and tokens for a retried item.** The text voids superseded *windows* (152–153) but never says the superseded *attempt's* answer and tokens are dropped too. An item completed inside a cut-off block and then re-run as a single has two answers | **no** | **no** | Yes under seeded sampling (E3 option b), where the two attempts can differ; no under greedy decoding |
| G10 | Sampler-record handling at window edges (N5) | no | no | No (within the floor) |
| G11 | "Adjacent" = consecutive envelope indices in S8 | the seat's own reading (426) | — | No (scheduling only) |
| G12 | Claim sentence form | O-3 (template proposed) | step 15 yes | No (wording only) |
| G13 | Exact "grouped integer" forms (N19) | no | — | No for the data-to-verdict path; affects rebuilding the frozen set |
| G14 | Linearity behind the drift bound (N11) | no | — | No for the computation (the formula is given); yes for whether the threshold means what it says |

Result: 14 guesses remain. **Nine can change a verdict** (G1–G9): G1–G5 are flagged at their step, G6–G8 are
flagged only in §6, and **G9 is flagged nowhere**. All steps other than those depending on O-2, O-4, O-5, O-7 and O-12
are now replicable from the text alone. The remaining obstacles to replication are ruling gaps, not writing gaps, with
the exception of G9.

## 4. Is v2's own self-check (§7, 1189–1208) accurate?

**Partly accurate.**

- **Accurate:** its claim that record 12's BLOCKER and MATERIAL rows are now built or glossed holds for every row
  checked in §1 above. Its "pointer only" list (census-clean, capacity, cap-ladder rung, binomial lower-bound, strict
  checks) and its "identifiers left bare" list are true.
- **Overclaims:** "window collisions" as fixed is true for "window" but not for collisions in general. The new text
  introduces seven: arm (N7), spread (N9), slot (N18), B1/B2 (N22), E1–E4 (N23), M6 (N24) and record (N5). The
  §2.1 "always writes rung L2" claim is also contradicted by the 467 carry. `floor_j` is listed as built, but its
  value and role are open (O-12).
- **Omits:** all 20 new findings in §2, including the five MATERIAL ones: the drift-bound linearity, the
  denominator-guard forward reference (a regression from v1), the floor "spread", "grouped integer" vs `1,000`, and
  the E1–E4 collision. It also omits the three open items not flagged at their procedure step (G6–G8) and the unflagged
  G9.

## 5. Ranked fixes for v3

**MATERIAL**

1. **Add a new open item for G9** and a sentence at step 1 or step 3 stating which attempt's correctness and tokens
   count for a retried item (presumably the attempt whose window is counted).
2. **State the linearity assumption** in the §2.1 drift bullet (171–173) before the bound: drift linear in envelope
   index, with a slope common to both models and at most δ_upper.
3. **Build the guard in Terms at 202:** "at least 3 correct per model per level (exact reading O-2)".
4. **Fix the K1 predicate** at 478–479 so that "grouped integer" cannot include `1,000`.
5. **Rename the K21 smoke checks** away from E1–E4 (747, 751, 1152), and gloss "early-stop bias".
6. **Replace "spread" in the floor definitions** (110–111) with the actual statistic, for example "the standard
   deviation (or the calibration artifact's stated dispersion) of …".
7. **Flag O-6, O-10 and O-9 at procedure steps 4, 5 and 13**, and O-12 at step 7.

**NIT**

N2, N4–N8, N13–N15, N18, N20–N22, N24 and N29 (one-clause glosses or renames); the panel-2 envelope-23 note; "outside
carries" at 157; O-4 flagged at 191–192.

Bottom line: **0 pedagogy BLOCKERs remain.** Two BLOCKER fixes introduced MATERIAL defects (F4's "grouped
integer" and F5's linearity), and F3 is now a ruling gap rather than a writing gap. Nine verdict-changing guesses
remain; eight are open items awaiting rulings, and one (G9) is new and unflagged.
