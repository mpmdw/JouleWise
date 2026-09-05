# 05 — Opus counter-review of paper-K (fact + pedagogy lens)

Independent Opus counter-review, JouleSort-literate advisor lens. Tree `JouleWise-wt-paper-k`, branch
`feat/2026-09-04-paper-k`, HEAD `850ea169`; diff `4ea033ec...HEAD -- docs/paper docs/paper/fill-rehearsal
tests`. Governing texts read: ruling 17 §A/§B and `43-magistrate-synthesis-gate-17.md` (the latter from the
sibling ratification worktree — **it is not present in this worktree**, so paper-K carries no copy of the
text it implements).

Tests run here, one at a time, `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1
python3 -m unittest`: `tests.test_paper_first_use_ledger` 10 OK, `tests.test_paper_terms_lint` 4 OK,
`tests.test_select_outcome_branches` 3 OK. Selector run for all three outcomes: A 241 words, B 240,
REFUSAL 250.

Verdict: **NOT LANDABLE** — 3 blockers, 4 should-fix, 4 nits.

## Executed code verification (this session, at this HEAD)

| Paper sentence | Code | Result |
|---|---|---|
| interpolation term zero for interval records | `joulewise/reduce.py:515-518`, `:553-554` (`if curve[0].support_start_s is not None: return 0.0`), comment `:2482` | CONFIRMED |
| no stochastic metrology term on the phase path | `joulewise/analysis_engine/inputs.py:3668-3676` — `governed_stochastic_variance` returns `(), ()` for every metric whose `name != "energy_request_j"` | CONFIRMED |
| `t_{.975,4}=2.776` three-decimal table | `joulewise/aggregate.py:41-45`, `:78-89`; used by `detection_floor.py:32,698` | CONFIRMED; recomputed 2.776·√2.5·√1.2 = **4.808173041811203**, max(4, 2+that) = **6.808173** |
| two-gate rule `\|estimate\|>max(F,h+B)`, strict both ends | `joulewise/analysis_engine/claims.py:335` (`abs(est) <= floor` → `effect_not_above_floor`), `:362-370` (either interval containing 0 fails) | CONFIRMED, strict at both boundaries |
| D-165 shared-sign / local-corner replay | `joulewise/dominance_closeout.py:687-702` (one shared sign × 2^n local mask), `:328-333` (`q_j` = zero-centred width + `\|z_j−δ_j\|`) | CONFIRMED; two-block fixture recomputed: 8.8304376431/2.4305766103 = **3.6330628731** |

## Blockers

**BL-1 (fact) — orphaned p-value; the diff moved *t* and left its old *p*.**
Line 830 now reads `\(t=5.0/0.442719=11.2938\) on 9 degrees of freedom`. Lines 838-840 still reuse
`\(2.8\times10^{-6}\)`, the two-sided *p* of the **deleted** t=10.2923 path (recomputed here:
p(10.2923, ν=9)=2.8138e-6; p(11.293849, ν=9)=**1.2885e-6**). A referee who recomputes finds the Holm
worked example resting on a number the draft no longer derives.
- Old (830): `…\(t=5.0/0.442719=11.2938\) on 9 degrees of freedom. The separate…`
- New: `…\(t=5.0/0.442719=11.2938\) on 9 degrees of freedom, with two-sided \(p=1.3\times10^{-6}\). The separate…`
- Old (838-841): `Pairing an illustrative \(2.8\times10^{-6}\) with a second illustrative raw probability of \(0.041\) … orders them as \(2.8\times10^{-6}<0.041\)`
- New: `Pairing that \(1.3\times10^{-6}\) with a second illustrative raw probability of \(0.041\) … orders them as \(1.3\times10^{-6}<0.041\)`

**BL-2 (pedagogy + fact) — "total standard error" now has no definition, and the ledger says it does.**
The diff deleted the `se_total = sqrt(se_repeat² + se_metrology²)` construction, but line 852 still reads
"the measurement interval, formed from the total standard error" — a term of art whose only build in the
draft is now Section 7 (1250-1252), 400 lines *after* first use. Glossary row 1887 asserts it is
`glossed-at-first-use` in "Adding publication safeguards after the ratio"; it is not, so line 2022
(`Terms inventoried: 261; FAILS: 0`) is false as printed.
- Old (851-853): `The direction check requires two named complete uncertainty intervals: the measurement interval, formed from the total standard error, and the decision interval, …`
- New: `The direction check requires two named complete uncertainty intervals: the measurement interval, formed from the repeat standard error just defined — which is the **total standard error** on this path, because the builder supplies no additional stochastic metrology variance — and the decision interval, …`

**BL-3 (pedagogy) — the estimand relabel puts an unglossed term of art in every Abstract branch.**
`interval-overlap-assigned phase energy` / `interval-overlap allocation` appears at 29, 35, 41 (Abstract
A/B/Refusal), 61 (Section 1) and 1410, 1416, 1422 (Conclusion). Its mechanism — split each record's energy
in proportion to the share of its interval on each side of the boundary — is first stated only at line 205,
in Section 2. `held-average reconstruction` (1410/1416/1422) is never glossed in that compressed form.
Neither term, nor `timing envelope` (63, 74), has a first-use-ledger row, so the inventory is incomplete as
well as the gloss missing. This is the paper's central measurand phrase.
- Old (60-61): `The measurand is energy assigned to each phase by interval-overlap allocation of the sampler's interval-average records.`
- New: `The measurand is energy assigned to each phase by **interval-overlap allocation**: each sampling record's energy is divided between the two phases in proportion to the share of its interval falling on each side of the phase boundary.`
- Abstract (29/35/41): replace `the largest change in interval-overlap-assigned phase energy` with plain words that carry the mechanism, e.g. `the largest change in the phase energies obtained by splitting each record in proportion to the interval on each side of the dividing time`, and add ledger rows for the three terms.
- **Budget constraint that must be solved with this fix:** the Refusal Abstract renders at **250/250** words
  (selector cap). Any Abstract-side gloss must be paid for by a trim in that branch, or the selector fails.

## Should-fix

**SF-1 (fact) — Section 7's "every dependence model" sentence contradicts the sheet it cites.**
Lines 1265-1267: "Every dependence model therefore sets the total stochastic standard error to its modeled
repeat standard error." The cited `docs/paper/round7/dependence-sensitivity.md` requires `se_metrology` and
computes `SE_total = hypot(SE_repeat,model, SE_metrology)` (sheet 14, 33, 36; CLI 102 passes
`--se-metrology 0.2`); its published ν=9 row (sheet 82) uses SE_total 0.485798, t 10.292337. Draft line 845
still cites "the sheet's \(\nu=9\) row".
- New (1265-1267): `For these gross phase-energy contrasts the current builder supplies no additional stochastic metrology variance, so \(SE_{\mathrm{metrology}}=0\) on this path and each model's total stochastic standard error reduces to its modeled repeat standard error. The dependence-sensitivity sheet's worked example stipulates a nonzero \(se_{\mathrm{metrology}}\) and is an arithmetic check of the composition, not a campaign input.`

**SF-2 (consistency) — the Introduction still presents the inserted-gap check as work this paper does.**
Lines 102-105: "Because pulses are not inference, a later **inserted-gap check** creates about 500 ms of no
work … and compares …" — present tense, no hedge, while §7 (1202) and §8 (1320-1321) now say it was not run
and is not a submission predicate (ruling Q5).
- New: `Because pulses are not inference, an **inserted-gap check**—commanding about 500 ms of no work between prefill and decode and comparing the gap's independently time-stamped edges with the power record—is registered as future diagnostic work; this paper did not run it.`

**SF-3 (fact) — the registry names a `.v2` supplier that no producer emits.**
`results-fill-registry.md` now names `d165_shared_sign_local_corner_replay.v2` in the four `_cmp` R_cm rows
and the D165 note, at freeze status `DERIVATION_FROZEN`. In this tree `joulewise/dominance_closeout.py:50`
still emits `...replay.v1` and `:51-55` still carry the superseded `ABSOLUTE_COMMON_MODE_REASON`
("a uniform shared fiducial shift cancels exactly"). Ruling 17 assigns the relabel to a separate seat, so
this is a dependency, not a paper defect — but as written the rows are unfulfillable.
- Add to each of those four rows' freeze column: `; SUPPLIER_PENDING: producer emits .v1 until the D-165 relabel lands`.

**SF-4 (pedagogy) — the synthetic enclosure diagnostic is not replicable from the text.**
Lines 72-76 give `[8, 10] J` with no derivation; the reader cannot rebuild it.
- New (73-75): `Its \(\pm10\)-ms two-edge timing envelope is [8.8, 9.2] J, while allowing each record's energy to sit anywhere inside its own interval gives the nonnegative partial-record enclosure [8, 10] J: the eight records lying wholly inside contribute 8 J, and the two records the window only partly covers contribute between 0 and 1 J each.`

## Nits

- **N-1** Refusal Abstract at exactly 250/250 words: zero headroom for any later edit (see BL-3).
- **N-2** Glossary row 1885 calls floor packs collectors of "null-calibration data"; first use (294) says "calibration data used to build a comparator floor". Align.
- **N-3** `test_paper_terms_lint.py` pins `draft.count("[FILL:") == 131` exactly; any legitimate fill edit breaks an unrelated lint. Use `assertGreaterEqual` or drop.
- **N-4** Registry rows DS-28 / PG-04 dropped the template column anchor ("under `Sizing sum F+B; signed clearance`") while relabelling the title; keep the anchor so the cell binding survives.

## Checks that passed

- Branches are complete alternatives: A = all twelve ≥ 2; B = all authenticated and evaluable, one < 2; Refusal covers the before-comparison stop and the close-out stop (missing value, unmatched source, zero denominator). No gap; zero-denominator lives only in Refusal, correctly.
- No surviving sentence claims physical phase-energy containment, common-time robustness, a transfer result, or F+B as a gate. The surviving "containment" uses (329-361, 441) are the null-ladder / phase-accounting sense, already caveated to measured-block containment.
- Component census consistent: 8 independent-edge (2 models × 2 phases × {repeat, null}) + 4 comparative \(R_{cm}\) (null only) = 12; matches the registry's four `_cmp` and four `not_applicable` `_abs` rows.
- Overbuild: none material; the new test lines are string ratchets, not logic (subject to N-3).
