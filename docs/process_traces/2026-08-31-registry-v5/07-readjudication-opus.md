# 07 — Fresh pedagogy re-adjudication (Opus seat, 2026-08-31)

Seat: fresh, blind to the drafting process. Materials judged: `docs/paper/draft-v1.md`
(673 lines, read in full), `docs/paper/round7/structural-edits.md` (S01–S11),
`docs/paper/round7/retensing-plan.md` (H01–H48, U01–U08, Item 10, Item 60).
Method: every structural edit applied mentally to the frozen draft, then every
retensing A/B/C/D sentence substituted at its named line into that post-structural
draft; findings are about the resulting page, not about the sheets' bookkeeping.

**Counts: 6 BL / 8 SF / 3 N.**
**Verdict: NOT USABLE FOR SUBSTITUTION.**

Every blocker below is cheap to cure (a quoted span, a clause, one added column,
one built definition). None requires new evidence or a new ruling except BL-2's
choice of which criterion the word *attribution-limited* names.

---

## Blockers

### BL-1 — The Discussion still glosses *attribution-limited* with the retired >1 criterion, contradicting the new ≥2 rule

Draft line 298 survives the sheets except for the one sentence H36 deletes and the one
H27 replaces. Two retired-criterion clauses remain:

> When phase-boundary attribution **exceeds** run-to-run scatter, collecting more repetitions attacks the smaller uncertainty while leaving the dominant one in place.

> Subject to the load-transfer assumption above and only for those cells, their one-line label consequence is *attribution-limited*: **edge placement contributed more than scatter**.

S04/H48 rule the opposite criterion for the same word:

> The subtitle uses *attribution-limited* only when every independent-edge component ratio in every cell is **at least 2** and no required comparative shared-error ratio is below 2.

and S01 explicitly forbids the >1 reading:

> …rather than merely make the quotient greater than 1, which any positive interval width can do.

After substitution the paper defines one term of art two incompatible ways, with the
plain-language gloss a reader will actually remember ("contributed more than scatter")
attached to the retired one. No sheet touches either clause.

### BL-2 — First use of *attribution-limited* and of *dominance* is Table 1, unbuilt, and there the demoted predicate is still an accept/refuse criterion

The word's first appearance anywhere in the body is draft line 96 (§3, Table 1), before
§4 builds anything:

> …evaluate the attribution-limited predicate (the artifact's field name is `admissible_set_uncertainty_dominates_point_floor`) for each floor cell.

> …the dominance predicate must be true for every floor cell.

> …an evaluated closure, invariance, bracket, flag, or dominance failure contradicts the row; a false dominance predicate **withholds the attribution-limited label**.

Two defects at once. (a) First-use test: the term is never built or glossed at line 96 —
the parenthetical field name renames it and encodes the retired criterion; S01 at line 21
builds \(R\) and the threshold but never names the label. (b) Contradiction: S01 rules

> The older coded exceedance predicate remains only as the cell's diagnostic label and does not select the paper's result.

yet line 96 makes that predicate a pass/fail criterion of a frozen characterization row
("Accept iff every listed predicate holds"), i.e. it does select a published outcome.
Line 103 compounds it: "Forcing all timing-envelope widths to zero flipped **the registered
dominance predicate** from true to false" — *registered* is exactly the status S01/S02 take
away from it. No sheet touches lines 96 or 103.

### BL-3 — \(R_{cm}\) is decision-bearing but not rebuildable from the words: \(q_j\) and \(\ell_j\) rest on four unbuilt terms and no worked numbers

S03's construction:

> For block \(j\), it reconstructs a shared excursion \(q_j\) from the **registered onset and offset sweeps around their zero point**, including the **recorded zero-point-to-block-difference discrepancy**, and a local half-width \(\ell_j\) equal to half the sum of that block's four **member-residual half-widths**.

None of "registered onset and offset sweeps", "their zero point", "the recorded
zero-point-to-block-difference discrepancy", or "member-residual half-widths" is built
anywhere in the draft or either sheet. §2 builds onset/offset *lags* and widened *edge
regions*; §4 builds member interval half-widths \(h_i\). A hostile PC reviewer can execute
everything after \(\delta'_j\) — the two shared signs, the \(2^n\) local signs, the recomputed
comparative floor, the division — and cannot compute the one input that makes the
replay differ from the independent-edge corner sweep. Since "A comparative \(R_{cm}<2\)
withdraws the boundary-dominance sentence even when independent-edge \(R\ge2\)", this is
the paper's second gate on its headline claim.

Two aggravating specifics: \(\ell_j\) as defined ("half the sum of that block's four
member-residual half-widths") is arithmetically the same quantity §4 already builds as
the block-difference half-width via \(\delta^-,\delta^+\) — a rename, not an explanation;
and unlike \(R\), \(R_{cm}\) gets no worked example with real numbers anywhere in the
sheets (the plan's "1.8" at line 23 is a threshold illustration, not a computation).

### BL-4 — \(R\)'s numerator and denominator are described three different ways, and the difference changes the number

S02 is explicit that the ratio uses pre-guard quantities:

> …first calculate the complete point-only formula from steps 1 or 2 **without the later multiplier \(g(n)\) or window allowance**.

> \(R=\dfrac{\text{largest complete unguarded floor after full corner re-evaluation}}{\text{complete unguarded floor from the observed point values}}\)

Then S02's own example gloss says the opposite:

> These examples also show that the numerator is **the whole floor** recalculated at a corner, not a timing term divided by a scatter term.

And the retensing sheet's paper-facing restatements drop the qualifier entirely —
Outcome A: "divide **the complete bound** made after allowing every registered interval edge
to move by the bound made from the observed point values alone"; Item 10 A: "**the complete
bound** after full interval-edge corner re-evaluation was divided by the same complete bound
calculated from the observed point values alone"; H28 A: "the complete interval-edge bound
was divided by the point-only bound".

This is not a wording preference. \(g(n)\) cancels, but \(A_k\) does not: on §4's own fixture,
\(F=g\cdot U+A\) with \(A=0.4\) J against \(U\approx1.67\) J, so including the allowance in both
terms moves the quotient materially against a threshold of exactly 2. A reader who takes
"the complete bound" to mean the published cell floor computes a different, wrong \(R\).
Compounding it: S02's only worked example, \(3.153/0.2888=10.92\), draws on draft line 103,
which names those numbers "point floors from run-to-run scatter alone" and "the
corresponding **corner-widened floors**" — the page never says they are the unguarded
quantities the definition requires, so the sole numeric instance of the central falsifier
cannot be checked against the definition.

### BL-5 — The headline ratios have no reporting slot: H22 and H01 describe Table 2 columns that no sheet creates

H22's replacement is the schema sentence for Table 2:

> Each published floor cell reported its magnitude, **independent-edge ratio**, and code-generated diagnostic label, and n counted independent run bundles… comparative rows reported the **replayed shared-error ratio**.

H01 A likewise: "the tables below report each issued cell, each registered comparison
decision, and **every independent-edge and shared-error ratio**".

The retained table header at draft line 278 is unchanged, and H45 — the only sheet row
that edits Tables 2 and 3 — changes model labels only:

> | Phase | Model | Gross J/request (lower, upper) | J per prompt token | J per output token | Cell floor (labeled) | n |

After substitution the prose asserts columns the adjacent table does not contain, for the
quantity the whole round exists to report.

### BL-6 — H46's replacement span is not byte-anchored over the retired 256-token arithmetic

H46 is headed "draft lines 266–272" but quotes verbatim only the heading
("### Why 256 prompt tokens were selected") and then supplies a single "**Replacement
paragraph:**" for a region containing two paragraphs *and* a display equation:

> \(\widehat\Delta_{256}=\frac{256}{128}(5.809930)=11.619860\ \mathrm{J}\)

plus draft line 272's `[[NEEDS-VALUE: … the D-122 p256 sizing decision …]]` and
"That arithmetic selected 256." Every other row in both sheets quotes its replaced bytes
exactly (the structural sheet asserts this as its own discipline: "Every quoted passage
below is byte-exact"). Here the discipline lapses at precisely the highest-risk survivor:
if any of 268–272 is left standing, the retired proportional-scaling selection of 256
sits beside H15/H46's four-rung 512/1024/2048/4096 ladder, which is the BL-9 defect the
prior round was ordered to remove.

---

## Should-fixes

- **SF-1 — "component" is unbuilt at first use, because H07 removes its antecedent.** The
  frozen line 21 said "The two components will be produced independently…"; H07's A branch
  replaces it with "The spread among repeated runs and the energy that calibrated boundary
  uncertainty could move across the edge were produced independently… allowing that movement
  at least doubled **each component bound**", and S01 then quantifies over "each registered
  **component** in each cell". §4 first names the absolute and comparative components ~90
  lines later. Cure: keep the naming in H07 ("these two components — …") or gloss in S01.
- **SF-2 — S05 and H39 disagree on the replaced span.** S05 quotes the whole of draft lines
  55 and 57 and replaces both; H39 quotes only their first sentences ("Figure 2 maps that
  bracket onto one complete measurement window." / "The pale lower inset expands one A/B/B/A
  block.") and offers the identical replacement text "for both quoted draft passages". Applied
  literally, H39 leaves the two full figure walks in place beside their own replacement.
- **SF-3 — H40 miscounts its span.** It replaces "the **three** prose paragraphs before the
  Figure 3 image"; the draft has two (lines 202 and 204).
- **SF-4 — H46 leaves a dangling definition.** Its replacement paragraph ends "In the later
  sizing notation, F means the applicable cell floor and B means the separately registered
  claim-side bound", but that paragraph no longer uses F or B anywhere (the `C = F + B`
  disclosure it once introduced is deleted), and H26 re-defines both at their actual use site.
- **SF-5 — §4 line 189 contradicts H20/H21.** "The four prospective phase-cell values and their
  decompositions **remain unavailable until their authenticated artifacts issue**: **[RESULT
  PENDING ISSUED ARTIFACTS]**" survives, while H20/H21 report that the artifacts issued and
  merely "defined neither that mean-energy field nor its endpoints".
- **SF-6 — §1 ends in three tenses; the census does not cover lines 23 and 25.** After
  substitution line 21 is present-tense (S01), lines 21/30/31 past (H07/H03/H08), and these
  survive future: "The planned model-size comparison **will** demonstrate how this measurement
  result governs a claim" (23) and "The result **will** characterize one physical machine…
  It **will** not establish whole-system energy" (25). The plan's "Census of `will ` on the
  hazard lines" lists neither line.
- **SF-7 — The Conclusion keeps pre-collection framing around the retensed sentences.**
  Untouched at line 356: "The capstone's central outcome is the registered attribution-dominance
  test." and "Failure in both phases yields a calibration that corrected its own clock-model
  error followed by a **prospective null**."; at line 358: "neither retroactively changes a
  **prospective null** into attribution dominance." H28/S08/H29/H47 land past-tense results
  between them.
- **SF-8 — Line 21's surviving failure semantics are per-phase where the rule is per-component.**
  "Failure in one phase narrows the finding to the other; failure in both **rejects attribution
  dominance**" survives beside S02's "mixed outcomes are **reported by component** and do not
  support the all-components sentence", and beside S08's B branch, which identifies failed
  components.

---

## Notes

- **N-1** — draft line 80's evidence comment still reads "fresh `_v4` captures byte-retain v3";
  non-reader-facing, but it is the last `_v4` token the sheets do not reach (H48 covers 2–7,
  H35 covers 164, S09/S10/S11 and H28 cover 294/314/356/358).
- **N-2** — H31 and H43 share one anchor ("immediately after Table 1 and before the paragraph
  at draft line 99") with no stated order between them.
- **N-3** — S04/H48's Methods placement is disclosed as PROPOSED and needs the lead's ruling
  before mechanical substitution; that disclosure is correct behaviour, not a defect, but the
  round cannot be executed mechanically until it is answered.

---

## PASS

Judged clean as written: S01, S05 (text), S06, S07, S08, S09, S10, S11; H02–H06, H08–H21,
H23–H27, H29–H38, H41–H45, H47, H48; U01–U08; Item 10; Item 60. In particular the threshold
justification in S01 ("must add at least one entire point-only bound, rather than merely make
the quotient greater than 1"), the \(2^{40}\)-versus-\(n=16\) explanation in H31, the withdrawn
"95/95" label in H30, the split refusal semantics shared by H15 and H46, the `not_applicable`
cancellation argument shared by S03 and H22, and the A/B/B/A sign convention in S05/H39 all
meet the replication bar.
