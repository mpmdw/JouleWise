# 11 — Final fresh joint pedagogy adjudication (Opus, fresh seat, 2026-08-31)

Seat: fresh pedagogy adjudication of the round-7 editing apparatus, blind to the
drafting process. Judged: `docs/paper/draft-v1.md` read in full, every structural
row S01–S21 mentally applied to it, then every retensing block substituted into
that post-structural draft. Consulted after forming findings:
`07-readjudication-opus.md`, `09-COLD-RULING.md`, `10-perimeter-round-record.md`.
Read-only; this file is the only write.

Counts: **3 blockers, 13 should-fixes, 4 notes. 59 of 81 blocks PASS.**

Verdict: **NOT USABLE FOR SUBSTITUTION.**

---

## Blockers

### BL-1 — *attribution-limited* is left naming two incompatible things, one of which the paper says does not select its result

S12 hands the italicised term to the demoted legacy predicate, inside Table 1,
which is its **first use anywhere in the paper** (draft line 96 precedes 185,
210, and 298):

> The artifact calls that label *attribution-limited* when its legacy
> `admissible_set_uncertainty_dominates_point_floor` predicate is true; the label
> records whether its older corner term exceeded its guarded point term and **does
> not select the paper's result**.

S04 (and H48, verbatim) then gives the same italicised term the opposite,
result-selecting meaning, and S14's Replacement 2 uses it that way in §7:

> The subtitle uses *attribution-limited* only when every independent-edge
> component ratio in every cell is at least 2 and no required comparative
> shared-error ratio is below 2 …

> … their one-line ratio consequence is *attribution-limited*: every
> independent-edge ratio was at least 2 and no required comparative shared-error
> ratio was below 2.

H22 then puts the legacy sense into the results table for every row — "Each
published floor cell reported its magnitude, independent-edge ratio, and
code-generated diagnostic label" — so a reader meets cells stamped with the
§3 sense while §7 and the subtitle assert the ≥2 sense.

This is the ruled meaning half-installed. `09-COLD-RULING.md` §3.3 requires
that "S04's ≥2 rule governs the label and the line-96/103 predicate is
diagnostic-only." The perimeter round demoted the predicate (correct) but left
the **name** on it, and `10-perimeter-round-record.md` records the intent that
the round did not deliver: "*Attribution-limited* now means every
independent-edge ratio is at least 2 and no required comparative shared-error
ratio is below 2." After substitution it means both, and the retired `>1`
criterion survives — not as a stated criterion, but attached to the word that
now carries the ≥2 verdict. That is the survivor class the census is binding
about, wearing the new vocabulary.

Cure (small, no new evidence, no new ruling): in S12 and H22 name the legacy
flag by its artifact field only (or "the artifact's legacy corner-exceeds-point
flag") and reserve the italicised term for the ≥2 verdict, as S04/H48 already do.

### BL-2 — The rebuilt research question is stated in four terms that are not built or glossed at that point, two of them not until §4

S21 replaces the paper's primary question with:

> The primary research question is therefore plain: under the corrected clock
> model, did every component's complete unguarded corner-re-evaluation bound
> reach at least twice its complete unguarded point-only bound, with no required
> comparative shared-error ratio below 2, for prompt processing and token
> generation on the named M3 Max / MLX / *powermetrics* configuration?

At its site nothing has been built:

- **"component"** — built two sentences later, by S01 ("The two components are
  the absolute component … and the comparative component …").
- **"complete unguarded"** — built one sentence later, by S01 ("before the later
  small-sample multiplier \(g(n)\) and whole-window drift allowance").
- **"corner-re-evaluation"** — "corner" is built only in §4 step 3, draft line
  148: "Enumerate all \(2^n\) joint *corners*, where a corner is one simultaneous
  lower-or-upper choice for every interval." The compound "corner-re-evaluation"
  appears nowhere else in either sheet in this form.
- **"comparative shared-error ratio"** — its construction is S03, in §4. Its
  concept appears in plain words in the Abstract (H06: "timing error shared
  within each four-run comparison moved together") and in the *next* sentence
  (H07), but the term itself is never glossed at any use before §4.

The standard is explicit that a term whose meaning arrives only in later text
fails the draft, and this is the sentence the whole apparatus exists to rebuild.
S01 immediately afterwards does the building well; the question simply precedes
its own vocabulary.

Supporting evidence that this class was structurally unguarded: the first-use
lint the cold ruling credits as the round-1/2 cure (`0 finding(s) across 94
sentence(s)`) was run only against `retensing-plan.md`. Run against the
structural sheet it does not lint at all:

```text
$ python3 scripts/paper_terms_lint.py lint --draft docs/paper/draft-v1.md \
    --plan docs/paper/round7/structural-edits.md \
    --lexicon docs/paper/round7/built-terms-lexicon.md
error: plan contains no recognized A/B/C/D variant sentences
```

`scripts/paper_terms_lint.py` accepts exactly one `--plan`. Every structural
replacement — S01's falsifier, S02's \(R\), S03's \(R_{cm}\), S12–S15, S21 — has
therefore never passed the mechanical first-use check.

Cure: either restate the question in physical words (the movement the session's
own calibration admits; the false-difference bound with and without it), or
specify at substitution that S01's construction is placed ahead of S21's
question inside draft line 21.

### BL-3 — Both result tables keep "Prospective" in their titles, contradicting the retensed captions they now head

Unreplaced by any row in either sheet, and missed by both censuses (the plan's
census is keyed on `will `, the structural census on the exceedance / `256` /
`_v4` / model-naming families):

> Table 2. **Prospective** phase-result schema. (draft line 276)

> Table 3. **Prospective** contrast decisions. (draft line 285)

After substitution H01 says "the tables below report each issued cell, each
registered comparison decision, and every independent-edge and shared-error
ratio", and the caption bodies are retensed to reported fact — H23: "The
token-generation mean was `[E_decode_contrast_signed_J_per_request]` J per
request"; H22: "Each published floor cell reported its magnitude …". A table
titled *Prospective contrast decisions* whose caption reports the decisions
taken denies its own contents, in the two captions a PC reviewer reads first.
SF-7 removed exactly this framing from the Conclusion; it survives here because
neither census keyed on the word.

Cure: two words. This is the cheapest of the three blockers and the only one
whose omission is purely a sweep escape — the third of its kind (BL-9, then
BL-1/BL-2, now this), which is itself the finding.

---

## Should-fixes

**SF-1 — The G2-a prompt-length rule is stated three times in ten draft lines.**
H15's A=B branch gives the full four-rung rule at line 260; S07 restates it at
the same line ("its prompt-processing arm used `[PREFILL_LENGTH]` prompt tokens
selected by the four-rung G2-a rule"); H46 then gives it again as the whole
subsection whose job it is. Item 13's de-duplication discipline is applied
elsewhere (H16: "The Abstract owns the one physical … glossary"; H17, H36, H37)
but no owner is assigned here. Assign the rule to H46's subsection; reduce H15
and S07 to a pointer.

**SF-2 — S01 and H07 define "the two components" in consecutive sentences, in
clashing tenses.** H07: "The two components—the spread among repeated runs within
one model arm and the between-model difference formed by subtracting the two A
energies from the two B energies and dividing by two—**were** produced
independently …"; S01, next: "The two components **are** the absolute component,
which measures spread among repeated runs within one model arm, and the
comparative component …". Same definition twice, past then present. Merge.

**SF-3 — S01 uses "A/B/B/A" at draft line 21, before its first construction.**
The order is built at lines 55/57 (S05/H39, §2), 117 (§4), and 229 (§5). Either
drop the token at line 21 ("block differences between model arms") or add "in
the A,B,B,A run order defined in §2".

**SF-4 — S03's sweeps do not say what is enumerated.** "moving all four phase
starts together through **every registered start-edge candidate**" leaves the
candidate set undefined; a hostile reviewer cannot tell whether that is two
interval endpoints, a grid, or the accepted-region enclosure of §A.3.5. This is
the one non-replicable step in an otherwise replicable \(R_{cm}\). One clause
fixes it ("every start time the capture's calibration bound admits").

**SF-5 — S03's worked fixture omits \(\delta_2\), so its two headline numbers
cannot be re-derived from the text.** \(q_1\), \(d_1^\pm\) and \(\ell_1\) all
recompute exactly from the printed figures. The point floor 2.4305766103 J and
the maximum 8.8304376431 J cannot: the second block's difference is never
printed. (I reconstructed \(\delta_2 \approx 0.4074\) J and both floors then
reproduce to four decimals under \(t_{.975,1}=12.706\), including the maximising
corner \(s=+1\), \(e_1=-1\), \(e_2=+1\) — so the arithmetic is sound; only the
input is missing.) Print \(\delta_2\) and \(z_2\).

**SF-6 — H09 states the null test against this cell's own bound, dropping the
disjoint comparator.** "so the block passes only when its largest absolute
difference stays inside the corner-widened resolution bound" reads as testing a
bound against itself. Table 1 (draft line 95, unreplaced) requires "a disjoint,
earlier-issued same-cell \(F_{\mathrm{op}}\)", and U02/H11/Item 10 all say
"comparator". Add "independently issued".

**SF-7 — H48's lines 2–7 span is not byte-anchored.** This is the defect class
the cold ruling fenced for H46 (BL-6): the span holds an HTML comment block with
the retired two-title device and two `_v4` mentions, a blank line, and the h1,
and H48 supplies no verbatim quote of any of it. Lower severity than BL-6 (the
at-risk content is a comment), but the same cure applies — quote lines 2–7
verbatim, as H46 now does.

**SF-8 — Tense clashes inside replacement prose that will sit adjacent.** S17's
Replacement 2 is present tense ("The result **reports** each usable component's
ratio … it **does not** collapse …") inside a Conclusion retensed to past by
S17-R1, S08, H28, H29, H47. S15 (present) sits beside H07 (past) at line 21.
H05's C branch mixes both in one sentence ("the analysis **constructs** … no such
bound **was** constructed").

**SF-9 — Draft line 247's "50 Qwen2.5 1.5B prompt-processing phases" is the only
model-naming hit the binding census neither cures nor fences.** The census's own
recorded command (`rg -n 'Qwen2\.5|1\.5B|7B'`) hits it; its disposition row lists
lines 260, 272, 278–290, 356 only. It is defensible content — retained
diagnostic-era evidence, self-labelled — but it now sits thirteen lines above a
demonstration section reading Qwen3-8B / Qwen3-1.7B, with nothing telling the
reader why a different model family appears. One clause, and a census row.

**SF-10 — S14's Replacement 2 asserts an unsupported conjunct about the pilot
cells.** "no required comparative shared-error ratio was below 2" — no comparative
shared-error replay exists for the three retained cells (the replay's only
numbers are the `fcm_r4_real_blocks` fixture in S03). The clause is vacuously
true and reads as evidence. Say "no comparative shared-error replay was required
for them".

**SF-11 — H06's Abstract gloss renames instead of explaining.** "every registered
boundary movement—that is, every movement allowed by the rule fixed before
collection" substitutes one label for another; what the reader needs is the
physical fact (the boundary positions the session's own pulse calibration
admits), which the Abstract has already built two sentences earlier.

**SF-12 — Four near-verbatim restatements of the \(R\) construction.** S02
(binding), Item 10-A, H01-A and H28-A each re-derive "the complete unguarded
bound after full interval-edge corner re-evaluation … divided by … before
\(g(n)\) and the whole-window allowance". The cold ruling required the unguarded
qualifier in all four; it permits "restatements subordinated to it", which a
short back-reference satisfies. As written, Results and Conclusion each redefine
the headline instead of reporting it.

**SF-13 — Table 2's retained header "Cell floor (labeled)" now names the demoted
legacy label** and reads, beside two ratio columns, as if it carried the headline
verdict. Rename to make its diagnostic status visible.

---

## PASS blocks (59 of 81)

S05, S06, S08, S09, S10, S11, S13, S16, S18, S20; H02, H03, H04, H08, H10, H11, H12, H13, H14, H16, H17, H18, H19, H20, H21, H23, H24, H25, H26, H27, H29; U01, U02, U03, U04, U05, U06, U07, U08; H30, H31, H32, H33, H34, H35, H36, H37, H38, H39, H40, H41, H42, H43, H44, H45, H47, H49, H50; Item 60.

Verified as correct while judging these: H31's `2^40 = 1,099,511,627,776` and its
analytic-corner argument; H42's 2.4984/2.6484 → 2.8984/3.0484 → max 3.0484 J
against §4's fixture; H41's 0.917/0.009/0.000 W in one 0.111 s record and H44's
0.103 J against §A.3.1; H30's withdrawal of the 95/95 label; S02's retained pairs
(3.153/0.2888 = 10.92, 2.922/0.4934 = 5.92, 2.184/0.3113 = 7.02); the sixteen
Table 2 ratio tokens matching the plan's table; S05 and H39 carrying identical
replacement text; S04 and H48 carrying the identical Methods sentence; all four
mandated unguarded restatements present; the item-13 glossary reduced to exactly
one home (Abstract), with H33, H36, H40 and H16 clearing lines 19, 298, 204 and
262; the three-record resolvability rule and the new five-record design floor
consistent across §1, §6, H15 and H46 with no contradiction.

---

## Notes

1. **The structural sheet has never been linted.** See BL-2. Whatever happens to
   this verdict, the fill session should either extend
   `scripts/paper_terms_lint.py` to accept both sheets or run the structural
   sheet through an equivalent check; the mechanical layer the cold ruling
   credits covers roughly half the substituted prose.
2. **Draft line 256 cites a bundle name that resolves five ways.**
   `p2015-df-ph-decode-abs-r03` exists in five retained corpora with prefill
   durations from 0.1210 s to 0.1374 s; the paper's number is the
   `runs_window_a10_20260725` copy (`prefill-resolvability-projection.md` §481,
   which already says "Citations of it should carry the corpus root"). Neither
   sheet touches line 256. Not a round-7 defect; worth carrying to the fill
   session, since the passage is the worked example of the paper's named
   negative result.
3. The two `[PENDING]` diagnostic-era values at draft line 256 are owned by
   registry rows DG-071 and DG-075. Checked and clear — no round-7 row is needed.
4. Draft line 262's "No floor will transport across model, phase, or prompt
   length." is the one surviving future-tense sentence on a hazard line, ruled a
   standing rule by the plan. It reads acceptably as a rule; noted only so the
   fill session does not treat it as an escape.

---

## Disposition

Three blockers, all locally curable from what exists, none needing data or a new
ruling. BL-1 is the serious one: it leaves the paper's headline label meaning two
incompatible things, one of which the paper explicitly says does not select its
result, and it is the ruled cure only half-installed. BL-2 puts the paper's
primary question ahead of its own vocabulary. BL-3 is two words that both
censuses were structurally unable to see.

**NOT USABLE FOR SUBSTITUTION.**
