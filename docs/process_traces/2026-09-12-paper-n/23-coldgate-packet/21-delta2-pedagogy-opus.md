# Delta re-audit 2 — Paper-N fix round 2, PEDAGOGY + STRUCTURE lens (Opus, read-only)

Reviewer: Opus 5, read-only. Source read: `/Users/edr/code/JouleWise-wt-paper-n-ref` at
`e3285e67d6b616b020b95eaf1caf2e8089f240ff` ("Paper-N fix round 2: cure the term-before-definition
residue…"), confirmed by `git log --oneline -1` before any file was opened (not `482a0cc4`).
Files read whole: `docs/paper/draft-v2-skeleton.md` (1524 lines, was 1519),
`docs/paper/protocol/first-use-audit-ledger.md`, `docs/paper/round7/built-terms-lexicon.md`.
Diff read: `git diff 482a0cc4..HEAD -- docs/paper/draft-v2-skeleton.md` (317 lines) plus the
supporting-file diff. Inputs consulted: `04-review-pedagogy-opus.md`, `16-delta-pedagogy-opus.md`
(the baseline), `18-brief-fix-round-2.md`, `19-fix-round-2-astra-report.md`,
`06-blind-fable-advisor-read.md`.
No file in the reference checkout was modified. No test and no build script was run; the two
mechanical passes below are my own read-only Python over the draft, run with `python3 -B`.
Line numbers are 1-based lines of the **new** draft unless marked "old".

---

## 1. Closure table — record 16's items

Key: **CURED** = the finding's defect is gone at every site it named. **PARTIAL** = the named site
is fixed but the finding's substance survives somewhere. **NOT CURED** = unchanged.
**REGRESSED** = worse than at `482a0cc4`.

Record 16 raised 21 distinct items: NB-1, NB-2; SF-1..8; N-1..10; and one first-use item
(§2 item 2, "floor source") that was not separately ticketed. Its §2 items 1, 3–9 and its §3
reading-order cures map onto those ids (noted in the rows) and are not double-counted.

### Blockers

| Id | Verdict | New line |
|---|---|---|
| NB-1 (estimand table names three criteria terms built 111 lines later) — §2 item 1 | **CURED** | 108, immediately under the table: "The absolute floor is built from centered repeat energies, the comparative floor from same-model block differences, and a science contrast is a difference between two models; Section 3 gives each construction. For each block, the difference is mean B energy minus mean A energy." The duplicate §3 block is deleted and §3 keeps its A/B/B/A opener at 216. Separation is now 2–4 lines inside one section. **The deletion overreached — new blocker 1 below.** |
| NB-2 (half-width depends on an allowance defined nowhere) — §2 item 3 | **CURED** | 313–315: "plus the registered joint-interpolation allowance, the extra half-width charged when a record's power must be interpolated between reported averages rather than held flat; it is zero for the native interval-average records used here." 318–319 is made consistent: "For these native interval-average records, timing sensitivity remains in the recomputed envelope despite the zero joint-interpolation allowance." \(h\) is now computable from the text. |

### Should-fix

| Id | Verdict | New line |
|---|---|---|
| SF-1 (synonym pair accepted/allowed region) — §2 item 4 | **CURED** | One name everywhere: 86, 144, 589, 823, A.3.5 1195. `grep -n "allowed region"` over the draft returns nothing. |
| SF-2 ("that protocol" dangles) — §2 item 5 | **CURED** | 241: "specified with the publication safeguards in the prospective comparison protocol linked in Section 3". (Pointer is self-referential — nit 4.) |
| SF-3 ("resolution bound" orphaned at 866) — §2 item 9 | **CURED** | 871: "and a detection threshold fixed before collection." "resolution bound" no longer occurs in the draft. |
| SF-4 ("the 5% and 1-mW constants") — §2 item 6 | **CURED** | 824: "on the 5% loss tolerance and the 1-mW noise floor of Appendix A.3.5, which were not varied." |
| SF-5 (Table 4 in an appendix of A1/A2/A3 tables) | **CURED** in the text | 514: "the cases in Table A4 (Appendix A.3.10)"; 1420: "Table A4. All eight sign cases…". No "Table 4" remains in the draft. **The pinned Figure A4 SVG still says "Table 4" — new should-fix 1.** |
| SF-6 ("the fit's discrepancy limit" undefined) — §2 item 8 | **CURED** | 144: "the accepted region, which contains every edge pair surviving the loss tolerance of Appendix A.3.5"; the same gloss now carries the §1 first use at 86. |
| SF-7 (§1 paragraph 1 does four jobs in 151 words) — §3 cure | **CURED** | 36–37 is the question alone; 39 is the two honesty sentences alone; 41 opens the instrument/glossary paragraph. The custody gloss is gone from §1. |
| SF-8 (caption asserts an axis label the SVG lacks) | **CURED** | 580–582: "the vertical axis, labelled `excursion (milliseconds)`, is the fitted edge excursion — fitted edge time minus commanded edge time — in milliseconds." Verified against `docs/paper/figures/fig4_edge_excursions.svg`, whose axis title is literally `excursion (milliseconds)`. |
| §2 item 2 ("floor source" used at 103, built at 188) | **CURED** | The §1 use is gone (110 now reads "JouleWise bounds each of these floors separately"); the first use of "floor source" is now its own defining sentence at 195. (110's wording folds the science contrast into "these floors" — nit 5.) |

### Nits

| Id | Verdict | New line |
|---|---|---|
| N-1 ("Huber" unglossed) — §2 item 7 | **CURED** | 150: "which sums Huber scores — squared for small differences, proportional for large ones — of the differences between predicted and observed interval averages after division by σ". (Nested inside another dash pair — new should-fix 4.) |
| N-2 (duplicated "retained" gloss) | **CURED** | 688: "The forcing problem appears in one run whose power trace was retained." The §4 apposition is gone; the abstract gloss stands alone at 29. |
| N-3 (duplicated "custody" gloss) | **CURED** | "custody" now occurs at 885 (bolded definition) and 963 only; §1 39 and §5 820 read "retained by the project". |
| N-4 (duplicated "allowed region" gloss) | **CURED** | 589–590: "The accepted region defined in Section 2 is distinct from the allowance: …". No second definition. |
| N-5 (self-referential "derived in Section 3") | **CURED** | 386: "a nonnegative per-block joule allowance derived below as \(q_j\)". |
| N-6 (no blank line before the §3 heading) | **CURED** | 207 is blank; 208 is `### Comparing the moved-edge limit and point-only value`. |
| N-7 ("the artifacts" returns at 641) | **CURED** | 647: "(`identifiable` — the label a phase receives when its record support reaches the minimum)". |
| N-8 (§5 raw-capture sentence precedes First/Second/Third) | **CURED** | The sentence is now at 820, after the "Third," paragraph (784, 788, 798). |
| N-9 (*b* acquires a third name) | **CURED** | 298: "\(b\) the window's operative timing bound". The three sites (157, 298, 409) agree. |
| N-10 (bare *R* in the abstract) | **CURED** | 31: "(Section 3's doubling test)". |

### Counts — record 16

**21 tracked: CURED 21, PARTIAL 0, NOT CURED 0, REGRESSED 0.**
Every item record 16 raised is closed at every site it named. As in round 1, the round's damage is
at *new* sites (section 4), not in the old ones.

### Contract ids not raised by record 16

| Id | Verdict | Evidence |
|---|---|---|
| D (abstract) | **DONE** | The fitted-onset/offset sentence now sits with the method block at 16–17; "macOS `powermetrics` is the power sampler used here." added at 12; **245 words** (my count of lines 11–31 excluding the HTML comment agrees with the seat's checker: `abstract_words=245, limit=250`). Both headline strings and the three count phrases are intact. |
| E / H2 (lexicon + ledger homes) | **DONE** | Seven successor rows re-homed; the "allowed region" ledger row merged into "accepted region"; footer 263 → 262, which matches the table's 262 data rows (verified by count). **But one ledger row is now false — should-fix 5.** |
| F (F7 provenance wording) | **DONE, with a misdirection** | 550: "Subtracting the two printed bounds gives \(…\) s; the separately retained largest pulse residual is recorded in the source artifact (Appendix A.3.6)." The fallback wording was correct: A.3.6 (1225) explicitly does **not** print a distinct retained residual. **New should-fix 2.** |
| G1 (cell floor conflation) | **CURED** | 517: "The **cell floor** is the final gate value for assigned-energy differences in a cell after the publication safeguards of Section P.3…". |
| G2 (keep the A/B/B/A table row) | **DONE** | 105 verbatim. |
| G3 (synthetic origin of the Section 2 allowance) | **DONE, tautological** | 658: "as in the Section 2 example (Section 2's worked example, not a measured window bound)". **Nit 1.** |
| H1 (pre/post difference interpretation) | **DONE** | 157: "A pre/post difference above the threshold indicates a change in the compound calibration allowance; it does not distinguish a change in fitted edge response from a change in clock-placement uncertainty." Representativeness and coverage sentences retained. |
| H3 (`math.fsum`) | **DONE** | 1405 and 1414. The A.3 conventions block at 978 still defines "Exact floating summation" as `math.fsum`, and 993/1171 still use that phrase, so the two names remain explicitly equated — no defect. |

### Carried forward from record 04 / the blind advisor read (out of this contract, unchanged)

| Id | Verdict | Note |
|---|---|---|
| S-4 (unresolvable internal referents) | **now CURED** | Closed by N-7 at 647. |
| S-11 / RO-7 (Figures A3/A4 numbered as appendix figures inside §3) | **NOT CURED** | 348 and 509 are still in §3 (175–522). Pin-blocked (T19). |
| N-4 of 04 (diagnostic-era glossed late) | **NOT CURED** | 557 uses it; 560 defines it. |
| N-5 of 04 (SVG file names do not track labels) | **NOT CURED** | 577 `fig4_edge_excursions.svg` is Figure 2; 675 `fig5_phase_record_overlap.svg` is Figure 3. Pin-blocked (F1). |
| N-8 of 04 (transfer limitation stated twice) | **NOT CURED** | 775 and 784. |
| N-9 of 04 ("fixed time margin" number never given) | **NOT CURED** | 144 uses it; 152 prints 0.75 s. |
| F-2, F-3 of 04 | **now CURED** | Closed by SF-8 and SF-6. |
| F-4 of 04 (Figure A2 caption reference counts) | **PARTIAL** | Untouched this round. |
| Ask 2 (abstract ≤ 200 words) | **PARTIAL** | 245 words; the lead's contract set 250 and the round met it. |
| Ask 3 (code ids / registry source maps out of the main text) | **PARTIAL** | The §4 registry source maps remain in the main text. |
| Ask 9 (delete/demote unused machinery) | **PARTIAL** by the lead's own B5 contract. |

---

## 2. First-use test over the WHOLE main text (abstract → §8, lines 9–921)

Two independent mechanical passes, both my own (not the seat's anchor file, and not the ledger
test's implementation):

**Pass A — every bold term.** 42 bold terms extracted from lines 9–921; for each, the earliest
line in 9–921 containing the term (case- and punctuation-normalised, HTML comments excluded) was
compared with the line carrying the bold definition.

- **LATE: 0.** One row surfaced and is not a defect: "record support" occurs at 119 before its
  bold build at 627, but 119 carries the gloss at first use *and* the forward pointer —
  "how many sampler records overlap a phase (Section 4's record support)".

**Pass B — every ledger term.** All 262 rows of `first-use-audit-ledger.md`; for each row, the
earliest main-text use of any alias was located and the section containing it compared against the
row's declared first-use home.

- **LATE: 0.** Two rows flagged and both are substring artifacts of the matcher, verified by hand:
  "command time" matching inside "command timestamps" (81), and the alias split of "model/stack"
  matching the bare word "model" (30).
- 145 rows have no main-text use (appendix- or protocol-homed), consistent with the seat's 139
  OUTSIDE rows.

**LATE = 0, confirmed independently of the seat.** The seat's zero is upheld.

**NEVER — 2 rows, and they are what the passes above cannot see.** A mechanical first-use pass
compares a use against a *declared* definition site; it cannot tell that a declared definition was
deleted. Both of this round's NEVER rows are of that kind:

**1. "false difference" / "false-difference" — used at 197 and 218, built nowhere.** *(Blocker 1.)*
> 197: "at least doubles each **component's source of false difference**."

> 218: "A cell has two **false-difference** components."

Its only build was the sentence A1 deleted with the duplicate block:
> old 210–211: "Repeat the same model to measure false differences; enlarge their spread into a threshold a model comparison must exceed."

The replacement sentence at 108 carries the three floor *constructions* but not that build. The
ledger still certifies it (row 95: "false-difference components / false-difference | 3. How the
method quantifies assigned-energy sensitivity | **glossed-at-first-use**"), and the seat's census
recorded "false-difference components / false-difference | 197 | 105 | OK" — anchoring the
definition to line 105, the table row "Same-model null A/B/B/A blocks …| Comparative floor", which
contains neither the words nor the idea.

**2. "centered" — used at 108 and 335, built nowhere.** *(Should-fix 3.)*
> 108: "The absolute floor is built from **centered** repeat energies"

> 335: "the comparative formula has the same property after **centering** the repeat energies"

`grep -n "center"` returns only 108, 332, 335 in the main text; none defines it. The word enters
the paper on page one inside the sentence NB-1 prescribed — i.e. inside my own record-16 cure text.

---

## 3. Reading order of the new §1 and the new abstract

**Abstract — 245 words** (lines 11–31; the HTML comment at 32 excluded; agrees with the seat's
`abstract_words=245, limit=250`). Up from 238, by the two sentences the contract required
(the `powermetrics` naming under D). Ask 2's ≤ 200 is still not met; the lead's 250 is.

Order as written: (1) problem 11–12 → (2) instrument 12 → (3) glossary 12–14 → (4) method 14–15 →
(5) glossary 16–17 → (6) **not claimed** 18 → (7) **not claimed** 19–20 → (8) what was found 20–23 →
(9) what was found 24–27 → (10) scope 28–29 → (11) not claimed 30–31.

**The reading order now holds, apart from the one break the contract mandates.** The first
sentence that breaks it is line 18:

> "This paper specifies the sensitivity calculation and demonstrates it on synthetic inputs; it reports no sensitivity ratio on measured inference data."

— a *what-is-not-claimed* sentence arriving before anything found. This is the same break record 16
recorded and, as there, I do **not** recommend moving it: Ask 1 and contract item A1 demanded it up
front deliberately, and 19–20 sits directly beside it as a matched limitation pair rather than as a
second interruption. The unmandated break record 16 named — the fitted-onset/offset definition
stranded between the limitation sentences and the results — is gone: that sentence now sits at
16–17, immediately after the method sentence it defines terms for. Nothing else in the abstract
breaks the order.

**§1 — the order holds throughout.**

36–37 the question → 39 the two honesty sentences, their own paragraph → 41–47 instrument and
phase glossary → 49–62 the measurand and interval-overlap allocation → 64–68 machine scope →
70–78 clock placement → 80–93 pulse calibration and the transfer assumption → 95–110 cell and
estimands → 112–117 the short-prefill question → 119–123 what the evidence tests. The SF-7 split
removed the four-jobs-in-one-block defect without displacing anything: the honesty paragraph is a
deliberate page-one placement, and the reader still reaches the paper's actual question at 112.

---

## 4. New defects introduced by the round

### Blocker (1)

**NB2-1. A1's deletion removed the build of "false difference" and the forcing problem for the
whole floor apparatus.** First-use NEVER row 1 above. Two separate losses in one deleted sentence:

- *The term.* "False difference" is a term of art — the criteria word on which both components and
  both floors rest — and nothing in the main text now says what makes a difference false. The
  reader can infer it from "same-model null blocks" at 204–206, but inference is exactly what the
  replication bar forbids for a criteria word.
- *The why.* "…enlarge their spread into a threshold a model comparison must exceed" was the only
  statement in the main text of what a floor is *for*. `grep` over lines 9–921 for "exceed" and
  "threshold" now returns nothing that supplies it: 211 gives the forcing problem for the
  *doubling test*, not for the floors, and 218–221 says what each component measures, not why it
  is built. A reader cannot reconstruct why the paper bounds floors at all.

This is a **REGRESSION**: the text existed at `482a0cc4` and the round deleted it. It is also
certified as present by a ledger row (§5 below), so the mechanical gate will not catch it.

*Minimal cure (one clause + one sentence, both at the sites of use, no new numeral, no move):*
at 197 write "at least doubles each component's source of false difference — the apparent energy
difference produced by runs that differ in no condition"; and restore the purpose clause at 218,
e.g. "A cell has two false-difference components, and their spread is enlarged into a threshold a
model comparison must exceed."

### Should-fix (5)

**1. The pinned Figure A4 SVG still calls the table "Table 4"; the text now calls it "Table A4".**
> `docs/paper/figures/figA4_shared_signs.svg` line 15: "One shared sign s; independent signs e1,e2 → δ′j = δj + s qj + ej ℓj → **eight rows in Table 4**."

> 514 (Figure A4 caption): "enumerate the cases in **Table A4 (Appendix A.3.10)**"

The SVG is pinned and cannot be edited, so the cure is text-side and the same shape already used
for the Figure A2 gate label: at 514 write "the cases in Table A4 (Appendix A.3.10; the figure's
note calls it Table 4)". Note also `docs/paper/figures/README.md` line 16 and
`docs/paper/figures/build_mechanism_figures.py` line 77 still say "Table 4"; neither was in
WRITE_SCOPE, and the README line should be swept when the figure sources next move.

**2. The new F7 sentence sends the reader to A.3.6 for a value the same paragraph prints.**
> 550: "Subtracting the two printed bounds gives \(0.030067931757111657-0.0011349971959968978=0.0289329345611147592\) s; **the separately retained largest pulse residual is recorded in the source artifact (Appendix A.3.6)**."

> 550, five sentences later: "The retained residual bound for the pulse is the largest absolute value those four endpoints allow — \(0.02893293456111476\) s, the upper end of the onset interval"

> 1225 (A.3.6): "…it is **not itself** the value the code retains for the worst edge excursion, which is computed and stored separately."

The fallback wording was chosen correctly on the facts — A.3.6 prints no distinct retained residual
— but the result tells the reader the number is elsewhere and then prints it, and leaves the two
similar-looking literals (…47592 and …476) related only implicitly. *Cure, text-side, literals
untouched:* "…; the separately retained largest pulse residual is a different quantity, computed
and stored separately (Appendix A.3.6) and given below."

**3. "centered repeat energies" is unbuilt at 108 and 335.** First-use NEVER row 2. *Cure at 108:*
"built from repeat energies after each is expressed as its difference from their mean". The defect
originates in record 16's own prescribed sentence, which the contract copied verbatim.

**4. The Huber gloss is nested inside another em-dash pair, giving one sentence four dashes.**
> 150: "Its fit loss — the dimensionless score of Appendix A.3.5, which sums Huber scores — squared for small differences, proportional for large ones — of the differences between predicted and observed interval averages after division by σ — must be strictly below half the loss of the no-pulse model…"

Dash 1 opens the "dimensionless score" apposition, dash 2 opens the Huber gloss, dash 3 closes it,
dash 4 closes the first — and nothing on the page tells the reader which closes which. The sentence
carries a blocker-tier acceptance criterion (B-3). *Cure:* parenthesise the inner gloss —
"sums Huber scores (squared for small differences, proportional for large ones) of the
differences…".

**5. The first-use ledger now certifies a gloss the round deleted.**
> `docs/paper/protocol/first-use-audit-ledger.md` row 95: "| false-difference components / false-difference | 3. How the method quantifies assigned-energy sensitivity | **glossed-at-first-use** | The same-model null A/B/B/A block produces this diagnostic, distinct from the two-model science contrast. |"

The named gloss no longer exists in §3. `built-terms-lexicon.md` rows 65 and 130 likewise quote a
build sentence — "The construction has two sources of false difference. The *absolute component*
m…" — that the draft no longer contains (218 now reads "A cell has two false-difference
components."). The ledger is the acceptance instrument for exactly this defect class, so a stale
row is worse than a stale doc. *Cure:* with blocker NB2-1's cure, rewrite row 95's gloss column to
quote the restored text; refresh the two lexicon build quotations to the draft's wording.

### Nits (6)

1. **G3's parenthesis is a tautology.** 658: "as in the Section 2 example (Section 2's worked
   example, not a measured window bound)". The parenthesis re-names its own antecedent; only
   "not a measured window bound" does work. *Cure:* "(a worked example, not a measured window
   bound)".
2. **Duplicated "median" gloss.** 146 "the median (the middle sorted value, or the mean of the two
   middle values for an even count)" and 572 "Their medians—the middle sorted values—are +13.0 ms
   and −5.5 ms". The 146 gloss is new this round; 572's predates it. *Cure:* at 572 write "Their
   medians are +13.0 ms and −5.5 ms".
3. **The sampler sentence is now verbatim in two places.** 12 and 41: "macOS `powermetrics` is the
   power sampler used here." Abstract-to-intro repetition is conventional, but this round cured two
   other duplicated glosses (N-2, N-3) and this one is word-identical. *Cure (optional):* at 41,
   "That sampler emits one record reporting average power between recorded start and end times."
4. **A self-referential section pointer, the class N-5 just cured.** 241: "in the prospective
   comparison protocol **linked in Section 3**" — the sentence is itself in §3 (175–522), pointing
   forward 275 lines to the link at 516. *Cure:* "linked at the end of this section".
5. **"these floors" folds in the science contrast.** 110: "JouleWise bounds each of these floors
   separately" follows 108, which names two floors *and* a science contrast; a contrast is not a
   floor. *Cure:* "JouleWise bounds each floor separately".
6. **"the allowance" has no antecedent in the Figure 2 caption.** 589–590: "The accepted region
   defined in Section 2 is distinct from **the allowance**: …". The N-4 cure made the accepted
   region the subject and left "the allowance" as a bare definite noun. Carried, not new — the old
   wording had the same referent gap. *Cure:* "…is distinct from the edge allowance — the largest
   endpoint displacement in an accepted region, …".

---

## 5. Same-signature statement, over both rounds

**Yes. One class has now produced defects in three consecutive states of the draft, and it is the
same class in each.**

**The class: a fix is applied against the finding list, not against the set of sites that *use*
the text being changed.**

- **Round 0 → round 1** (record 16 §5): eight reading-order cures were performed by moving
  definitions; four terms whose *uses* stayed behind were left unbuilt (NB-1, NB-2, "resolution
  bound", "the 5% constants"). Both round-1 blockers were of this class.
- **Round 1 → round 2** (this round): the mechanism was explicitly named in contract §Structural
  rule, and the seat did run a whole-text mechanical pass — which is why **LATE is genuinely 0**,
  the first time in the series. The class nevertheless produced one blocker and two should-fix,
  through the one door a first-use pass cannot see:
  - **NB2-1** — A1's *deletion* removed a build; a first-use pass that compares uses against
    declared definitions cannot detect that the declaration is now false, and the ledger row that
    declared it (should-fix 5) was not re-read against the text.
  - **New should-fix 1** — SF-5's *renumbering* was applied to the draft but not to the pinned SVG
    and the figures README that name the renumbered table. This is also a literal third occurrence
    of record 04's F-1/F-2 class (text and figure disagree about what the figure carries), after
    B-1's cure removed a phantom band and F-2's cure added a phantom axis label.
  - **New should-fix 3** — "centered" entered the draft inside record 16's own prescribed cure
    sentence and was never built; the reviewer's prescription was itself not run through the
    first-use test.

Two further round-1 classes recurred at nit tier: duplicated gloss (N-2/N-3/N-4 cured; "median"
and the sampler sentence introduced) and self-referential section pointer (N-5 cured; SF-2's cure
introduced one).

**The standing escalation trigger is met on its face** — two consecutive rounds failing with the
same signature — and I record it as met. What changed this round is the *mechanism*, not just the
count: the blind spot has moved from "uses left behind by a move" (now mechanically covered, LATE
= 0) to "declarations left behind by a deletion, and uses that live outside the draft file" (SVGs,
figure READMEs, the ledger's own gloss column). The structural cure is one clause, not a third
lens or a third delegated round: **every delete/rename item must name the sites that USE the
deleted build or the renamed object — including pinned figure text, figure READMEs, and the
ledger/lexicon gloss columns — and the report must quote each of them after the edit.** A first-use
pass over the draft alone cannot close this; a "who uses this?" sweep over the repository can, and
it is cheap.

**One blocker found (NB2-1), five should-fix, six nits.** Every cure above is one sentence or one
clause at a site already open, with no new experiment, no new numeral, no new section and no SVG
edit — each is smaller than the contract needed to delegate it. My recommendation is therefore
**one more lead bench edit**, not a third delegated fix round: apply NB2-1 plus should-fix 1–5,
re-read only the eight edited sentences plus ledger row 95, and land. If instead a third
*delegated* round is contemplated, the escalation trigger governs and the next spend should be a
consult on the sweep clause above before any further edits are commissioned.
