# Delta re-audit — Paper-N fix round 1, PEDAGOGY + STRUCTURE lens (Opus, read-only)

Reviewer: Opus 5, read-only. Source read: `/Users/edr/code/JouleWise-wt-paper-n-ref` at
`482a0cc49995aba94f923956af60c547fde538c6` ("Paper-N fix round 1: clarify scope and
timing-domain limitations"), confirmed not `dbe6c675`. File read whole:
`docs/paper/draft-v2-skeleton.md`, 1519 lines (was 1459). Diff read:
`git diff dbe6c675..HEAD -- docs/paper/draft-v2-skeleton.md`, 864 lines.
Inputs consulted: `04-review-pedagogy-opus.md`, `12-brief-fix-round-1.md`,
`13-fix-round-1-astra-report.md`, `06-blind-fable-advisor-read.md`.
No file in the reference checkout was modified. No test was run; the paper build script
was not run. Line numbers below are 1-based lines of the **new** draft unless marked "old".

---

## 1. Closure table

Key: **CURED** = the finding's defect is gone at every site it named.
**PARTIAL** = the named site is fixed but the finding's substance survives somewhere.
**NOT CURED** = unchanged. **REGRESSED** = worse than at `dbe6c675`.

### Blockers

| Id | Verdict | New line |
|---|---|---|
| B-1 (Figure 1 names a band the SVG lacks) | **CURED** | 122: "Figure 1 shows interval-average power around one record that the phase boundary crosses. The solid line is the recorded boundary and the dashed line is the same boundary moved 0.010 s; the hatched area between them is the energy reassigned between phases, and the request total does not change." No "band" remains anywhere. |
| B-2 (*b* names watts and milliseconds) | **CURED** | 139–141: "Define resting power \(P_{\mathrm{rest}}\) as the median of quiet records and σ=max(1.4826 × median absolute deviation from \(P_{\mathrm{rest}}\), 0.001 W)… The quiet-record threshold is \(P_{\mathrm{rest}}+\max(5\ \mathrm{W},5\sigma)\). With \(P_{\mathrm{rest}}=0\) W…". Renamed in A.3.5 (1146, 1155, 1160, 1180), A.3.7 (1234) and Table A3's preamble (1300) too; *b* now means the timing bound only (150, 294, 402). |
| B-3 (acceptance criteria stated in an undefined "loss") | **CURED** | 143: "Its fit loss — the dimensionless score of Appendix A.3.5, which sums Huber scores of the differences between predicted and observed interval averages after division by σ — must be strictly below half the loss of the no-pulse model fitted to the same records: a fit loss of 4 against a no-pulse loss of 10 passes; 5 against 10 fails." Unit named (dimensionless), examples labelled. (New nit: "Huber" is itself unglossed here — nit 1 below.) |

### Should-fix

| Id | Verdict | New line |
|---|---|---|
| S-1 (record support / three-record minimum built only in §4) | **CURED** | Abstract 25–26: "fell below the three-record minimum this paper requires for a phase split"; §1 112: "how many sampler records overlap a phase (Section 4's record support)". |
| S-2 ("retained" unglossed to 721) | **CURED** | Abstract 28–29: "across retained measurement windows—windows whose evidence bytes are kept on disk and never overwritten". (Gloss now stands twice — nit 2.) |
| S-3 (P.3, cell floor, small-sample multiplier unbuilt) | **CURED** | 511–514: "The **cell floor** is the registered operational resolution guard for assigned-energy differences after the publication safeguards of Section P.3 of the [prospective comparison protocol](protocol/prospective-comparison-protocol.md). That section gives the safeguards and their synthetic composition example."; 236–237: "the **small-sample multiplier**, specified with the publication safeguards in that protocol; no value in this paper uses it." |
| S-4 (unresolvable internal referents) | **PARTIAL** | "in the advisor's terminology", "in the artifacts" (old 141), "(registry DS-34)" and bare "D-078" are gone; registry glossed once at 150: "(results registry row S17; the registry is the project's row-by-row index of every displayed value and its supplying artifact)". But the referent returns at **641**: "(`identifiable` — **the artifacts'** label for a phase whose record support reaches the minimum)". |
| S-5 ("identifiable" never glossed) | **CURED** | 641, quoted above. |
| S-6 (thresholds before their algorithm) | **CURED** | See RO-1. |
| S-7 (three unreconciled synonym pairs) | **CURED** at the three named pairs | "science window" and "declared machine state" are gone from the main text (moved to A.4 1439); "amplitude" is gone from the main text entirely (137, 143 use "pulse height"; A.3.5 1155/1160 and Table A3 1300 follow); "native power record" is gone — 148 now reads "the native (unparsed) sampling records", 750 "the native sampling records". **A new pair replaces them** — should-fix 1 below. |
| S-8 ("excursion" carries three meanings) | **CURED** | 410: "Define the shared lower and upper energy swings"; the reference-trajectory sentence was deleted with B5; "excursion" now appears only in the millisecond sense (575, 586) and in file/registry names. |
| S-9 (undeclared L/U superscripts and block index *j*) | **CURED** | 310–311: "Writing that half-width as \(h\), the floor inputs are \(E^L=E-h\) and \(E^U=E+h\), the member's lower and upper values."; 315–316: "first form block \(j\)'s difference interval, writing \(E^L\) and \(E^U\) for a member's lower and upper values". |
| S-10 (rectangle never placed in a space) | **CURED** | 137: "Each rectangle is a range of candidate onset shifts crossed with a range of candidate offset shifts". |
| S-11 (figure numbering) | **NOT CURED** | Figures A3 (342) and A4 (503) remain inside main-text §3. Seat cites pin T19 (caption must agree with immutable SVG labels). |
| S-12 (Figure A2 labels the entry check "admission gate") | **PARTIAL** | 157: "the **entry check** (labelled the admission gate in Figure A2)". The other half of F-4 — the A2 caption's "three opening references"/"three closing references" against a text that gives no count (158–159) — is untouched. |
| S-13 (*p* and *r* collisions) | **CURED** | 436: "Let the largest absolute energy change for member \(m\) be \(\lambda_{jm}\)"; the pad is `pad` at 1373. Neither symbol now collides in the main text. |
| S-14 (§1 front-loads unused apparatus) | **CURED** as a cut | §1 108–160 (old) is now 90–116; the point-only/moved-edge/ratio/energy-sign machinery is at 188–199 and 376–389. **But the cut created blocker 1 below.** |

### Nits

| Id | Verdict | New line |
|---|---|---|
| N-1 ("frozen reservation plan" precedes *Frozen*) | **CURED** | 135 now opens the paragraph: "**Frozen** means fixed and fingerprinted before collection." |
| N-2 ("uncommanded-plateau check" precedes "plateau") | **CURED** | 137 defines it — "its flat high-power portion, called the plateau" — and 137's last sentences and 142 use it after. |
| N-3 (1.4826 unexplained) | **CURED** | 140: "the factor puts a median absolute deviation on the same scale as a standard deviation." |
| N-4 ("diagnostic-era" glossed three lines late) | **NOT CURED** | 551 "The following are diagnostic-era instrument statistics"; 554 "Here diagnostic-era means collected in the historical July 2026 period." Seat: "Not selected in the lead's ordered cures." |
| N-5 (file names no longer track labels) | **NOT CURED** (by contract F1, pinned) | 571 `fig4_edge_excursions.svg` is Figure 2; 669 `fig5_phase_record_overlap.svg` is Figure 3. |
| N-6 ("Source map:" used at 521, defined at 638) | **CURED** | 493–494: "A source map links each displayed value or figure mark to its supplying artifact and field. Source map: `tests/fixtures/…`"; the §4 instance at 594 now follows it. |
| N-7 (unresolvable decision/registry ids) | **CURED** | 552: "whose energy values a project decision (recorded in the project decision log) voids"; 738: "The earlier clock-anchor defect voids these captures' energy values for claim use"; "(registry DS-34)" deleted at 875. |
| N-8 (transfer limitation stated twice, RM-14) | **NOT CURED** (outside the brief's N-1..N-7 and outside the contract) | 770 "Transfer of the pulse-derived timing allowance to inference was not tested." and 781 "First, the pulse-to-inference transfer was not tested." |
| N-9 ("fixed time margin" number never given) | **NOT CURED** (same) | 137 "outside the fixed time margin around every pulse"; the 0.75 s appears at 145 under "Trace coverage". |

### Reading-order defects

| Id | Verdict | New line |
|---|---|---|
| RO-1 (thresholds before the detector) | **CURED** | The detector paragraph is now 137 and the numbers follow at 139: "The checks above use the following fixed numbers. Define resting power \(P_{\mathrm{rest}}\)…". Old 201–202's admission ("These numeric rules define 'far enough'…") is deleted. |
| RO-2 (abstract's headline depends on a §4 rule) | **CURED** | 25–26, quoted under S-1. |
| RO-3 (§1 front-loads the floor apparatus) | **CURED** as a move | 103: "JouleWise bounds each floor source separately; Section 3 gives the construction, and no floor value is published in this paper." The definitions now sit at 188–199 in §3. **Creates blocker 1.** |
| RO-4 ("phase-energy dominance" used at 35, defined at 381) | **CURED** | 30–31: "It supplies no new model-energy comparison, and no finding that boundary placement is the limiting uncertainty (Section 3's R ≥ 2 test)." (Bare *R* in the abstract — nit 10.) |
| RO-5 ("allowed region" defined in a caption) | **CURED**, with residue | 137: "it encloses every onset/offset pair close enough to that fit — the allowed region, which contains every edge pair surviving the fit's discrepancy limit"; 582 is unbolded. The caption still repeats the whole definition — nit 4. |
| RO-6 (§1/§2 send the reader to appendix figures) | **CURED** per contract F1 (one-clause form) | 159: "without the appendix diagram, the reader misses their ordering on one timeline"; 186: "Without it, the reader misses the visual contrast between held-average timing sensitivity and unrestricted within-record allocation." |
| RO-7 (Figures A3/A4 physically in §3) | **NOT CURED** | See S-11. |
| RO-8 ("Source map:" used before defined) | **CURED** | 493–494. |
| RO-9 ("block-level allowance" used at 146, built at 421) | **CURED** as wording | 376–377: "which says which direction a nonnegative per-block joule allowance derived in Section 3 moves assigned energy." The sentence itself moved into §3, so the pointer is now self-referential — nit 5. |

### Figure/equation findings

| Id | Verdict | New line |
|---|---|---|
| F-1 (Figure 1 band) | **CURED** | 122, quoted under B-1. |
| F-2 (Figure 2 axis-name mismatch) | **PARTIAL** | 575: "the vertical axis is fitted edge excursion in milliseconds (the axis label)". The SVG's axis title is still literally `excursion (milliseconds)`, so the caption now asserts an axis label the figure does not carry — should-fix 8. |
| F-3 (term defined in a caption; "fit's discrepancy limit" undefined) | **PARTIAL** | Bold removed at 582 and the definition promoted to 137 ✓; "in exact arithmetic" added at 137 ✓; A.3.5 1200 adds "The implemented floating-point search has no independently established directed-rounding containment guarantee." ✓. But "the fit's discrepancy limit" is still defined nowhere in the main text — and the fix moved it *into* the main text at 137. |
| F-4 (Figure A2 gate label; caption reference counts) | **PARTIAL** | See S-12. |

### Blind advisor Asks 1–12

| Ask | Verdict | New line |
|---|---|---|
| 1 (say up front no measured ratio) | **CURED** | Abstract 16 and §1 37, both: "This paper specifies the sensitivity calculation and demonstrates it on synthetic inputs; it reports no sensitivity ratio on measured inference data." |
| 2 (rewrite the abstract as an abstract) | **PARTIAL** | 238 words (Ask asked ≤200; the lead's contract set 250). The glossary sentences survive: 12–14 "Prompt processing reads input through the first output token, a piece of generated text; token generation emits later tokens"; 18–20 "Fitted onsets and offsets are switch-on and switch-off times selected by matching predicted interval-average power to the recorded trace." The conclusion still restates the held-average disclaimer (902–906) and both count phrases (906–909). |
| 3 (code ids / hash names / decision ids out of the main text) | **PARTIAL** | The hash-name block is gone from §2 and now opens A.4 at 1439 (`validation_manifest_sha256`, `instrument_calibration_invalid`, `PLAN_HASH_MISMATCH`, `ISSUED_ACCEPTANCE_REGISTRY`, `GENESIS_FIXTURE_ACCEPTANCE_SHA256`); §2 keeps one sentence (135: "Every input to a capture — the calibration artifacts, the frozen reservation plan, and the capture's own manifest — is fingerprinted, and any mismatch refuses the capture; Appendix A.4 lists the identifiers and refusal names."); D-078 is plain words (552, 738). Not done: the §4 registry source maps stay in the main text (594–598, 742–749), which Ask 3 asked to move to §7 or Appendix A. |
| 4 (σ hit its floor; what that does to the accepted region) | **CURED** | A.3.5 1190: "On the retained capture, σ sat at its 1-mW floor while plateau scatter was of order a watt around the fitted pulse height, vastly larger than σ. The accepted region is therefore a tolerance set whose width depends on the 5% and 1-mW constants, which were not varied." §5 817–819 repeats the limitation. Scatter is in words, no new digits, as the contract required. |
| 5 (interpret the systematic lag) | **CURED** | 821–826: "The 59 of 59 onsets late and 49 of 59 offsets early form a one-directional pattern. GPU start latency after the command and sampler window stamping are two candidate explanations; neither was tested. With no tested explanation to support a correction, no correction is applied. The symmetric \(\pm b\) domain therefore includes the bias and is wider on the side the bias does not occupy." |
| 6 (connect record support to the timing bound) | **CURED**, words-only as contracted | 651–656: "A per-edge allowance of a few tens of milliseconds, as in the Section 2 example, amounts across both edges to more than half of the 1.5B median and roughly a quarter of the 7B median. The three-record minimum guards only against a split supported by two straddling averages, not against a timing envelope comparable to the phase energy." |
| 7 (instrument-precision readings) | **CURED** | 150: "\(t_{0.995,16}\) is about 3 (retained as 2.92078162242509999197 for byte-exact replay)" and "records about 10 ms (retained as 10.164834757777545 ms for byte-exact replay)"; 530: "about 1 µs (retained as 0.0000010000000000000002 s for byte-exact replay)"; 788: "about 30 ms (retained as 0.030067931757111657 s for byte-exact replay)". Every literal is byte-identical; the untouchable worked-arithmetic line 544 is unchanged. |
| 8 (explain R_cm or move it) | **CURED** | 374: "R asks how much the bound grows when every run's edges move independently; R_cm asks how much it grows when one direction of energy allowance is applied to every block at once and each block's own edges then move to their worst local corner." The padding paragraph and Table 4 moved to A.3.10 (1360–1435). |
| 9 (delete/demote unused machinery) | **PARTIAL** by the lead's own contract (B5) | Deleted: whole-window allowance mechanics, energy family, reference-trajectory excursion, issued repeatability bound — replaced at 166 by "A separately measured whole-window allowance, defined in the prospective comparison protocol, is not used by any value in this paper." Kept by contract: the three-estimand table (97–103) and stage/admitted/entry check/reference runs (154–159). |
| 10 (say in §1 the measured results are not re-derivable) | **CURED** | §1 37 and §5 777, both: "The raw captures behind the historical numbers are retained under project custody and are not released; the synthetic examples are the only fully reproducible part." |
| 11 (move the synthetic enclosure example out of §1) | **CURED** | It now sits at 179–186, directly after the 1.20 J/1.80 J example, and 185 reads "it is shown for contrast and is not added to any result in this paper." |
| 12 (justify the 17-capture rule as an instrument statement) | **CURED** | 150: "A pre/post difference above the threshold would indicate a change in the sampler's fitted edge response across the window. Interpreting this threshold as an instrument screen is conditional on the retained corpus being representative, which has not been tested; empirical 99% coverage has not been established." |

### Counts

51 items tracked (B 3, S 14, N 9, RO 9, F 4, Asks 12):

- **CURED 37** — B-1, B-2, B-3; S-1, S-2, S-3, S-5, S-6, S-7, S-8, S-9, S-10, S-13, S-14;
  N-1, N-2, N-3, N-6, N-7; RO-1, RO-2, RO-3, RO-4, RO-5, RO-6, RO-8, RO-9; F-1;
  Asks 1, 4, 5, 6, 7, 8, 10, 11, 12.
- **PARTIAL 8** — S-4, S-12; F-2, F-3, F-4; Asks 2, 3, 9.
- **NOT CURED 6** — S-11, RO-7 (both pin-blocked, T19); N-4, N-5, N-8, N-9.
- **REGRESSED 0** (no finding from 04 is worse than it was at `dbe6c675`; the round's damage
  is in *new* sites, section 4 below, not in the old ones).

Restricted to the brief's literal enumeration (N-1..N-7 only, 49 items): CURED 37,
PARTIAL 8, NOT CURED 4, REGRESSED 0. N-8 and N-9 exist in record 04 and are reported above.

---

## 2. First-use test on moved and new paragraphs only

Scope as briefed: the §1 compressed block (36–116), §3 additions (179–199, 208–212,
293–316, 374–398, 425–426, 511–514), the §2 reordered numeric-rules paragraph (137–146),
A.3.9/A.3.10 and A.4 additions (1196–1204, 1242–1249, 1360–1435, 1439), §5 additions
(777, 817–826), and the new abstract (11–31).

Terms now used before they are built, with both lines:

**1. "Absolute floor", "Comparative floor", "Science contrast" — used at 99–101, built at 210–212.**
> 99–101: "| Same-model repeats | **Absolute floor** | … | Same-model null A/B/B/A blocks (four runs in the order A, B, B, A), with A = B | **Comparative floor** | … | Two-model A/B/B/A blocks | **Science contrast** |"

> 210–212: "The **absolute floor** uses centered repeat energies; the **comparative floor** uses same-model block differences. A **science contrast** is a difference between two models."

The old draft defined all three at old 114–116, four lines under the same table. B1 moved the
defining sentences to §3 and left the table behind. 111 lines of separation, across a section
boundary, on page one. *(Blocker 1.)*

**2. "floor source" — used at 103, built at 188.**
> 103: "JouleWise bounds each floor **source** separately; Section 3 gives the construction…"

> 188: "Each separately bounded **floor source** is a component."

Same move, same paragraph deletion.

**3. "the registered joint-interpolation allowance" — used at 309, never built.**
> 308–309: "its half-width is the largest of \(E-E_{\min}\), \(E_{\max}-E\), and the recorded maximum absolute energy displacement, **plus the registered joint-interpolation allowance**."

> 312: "For native interval-average records the joint-interpolation term is zero"

New text (the F1 cure). The term appears nowhere else in the paper, main text or appendix.
It is the last addend of \(h\), and \(h\) sets \(E^L\) and \(E^U\), which the whole corner
enumeration consumes — so a reader cannot compute the quantity the section is built on.
*(Blocker 2.)*

**4. "accepted regions" — used at 82, never built in the main text.**
> 82: "The largest displacement between the commanded times and every edge position in the fit's model-defined **accepted regions**, plus the **clock-anchor bound**…"

> 137: "it encloses every onset/offset pair close enough to that fit — the **allowed region**…"

Line 82 is new wording this round (old 82 read "allowed by the pulse records"). The main text
now carries two names for one object, neither reconciled; the only definition of "accepted
region" is A.3.5 1190. *(Should-fix 1; same signature as S-7.)*

**5. "that protocol" — used at 237, with no antecedent in §3.**
> 236–237: "The later factor is the **small-sample multiplier**, specified with the publication safeguards in **that protocol**; no value in this paper uses it."

The nearest protocol mention is §2 166, 71 lines back and in another section; the link is at
513, 276 lines forward. *(Should-fix 2.)*

**6. "the 5% and 1-mW constants" — used at 819, resolvable only from A.3.5 1187.**
> 818–819: "the accepted region is therefore a tolerance set whose width depends on **the 5% and 1-mW constants**, which were not varied."

> 1187 (A.3.5): "Λ = Loss\* + max(1.0, 0.05 · Loss\*)."

"5%" occurs nowhere else in §1–§8. A §5 reader meets a definite article pointing at a number
the main text never printed. *(Should-fix 4.)*

**7. "Huber" — used at 143, glossed at 1166.**
> 143: "the dimensionless score of Appendix A.3.5, which sums **Huber** scores of the differences…"

> 1166 (A.3.5): "Huber's loss is quadratic for small residuals and linear for large ones."

The preceding paragraph (137) glosses the *mechanism* — "a rule that limits the influence of
one large discrepancy" — but never attaches the name to it. *(Nit 1; four words fix it.)*

**8. "the fit's discrepancy limit" — used at 137, never built.**
> 137: "the allowed region, which contains every edge pair surviving **the fit's discrepancy limit**"

Previously confined to the Figure 2 caption (old 627); RO-5's promotion carried the undefined
phrase into the main text's algorithm paragraph. *(Should-fix 6.)*

**9. "resolution bound" — used at 866, now built nowhere.**
> 866: "A future JouleWise study would need named boundaries at both endpoints, cross-device clock alignment, and a **resolution bound** established before collection."

Old 129–131 defined it ("The cell's **resolution bound**—the **detection floor** in the
advisor's terminology—is a registered operational resolution guard…"). B2 deleted that
sentence and retired "detection floor", but the §6 use survived the sweep. *(Should-fix 3.)*

Everything else in the audited spans passes. Specifically clean: 179–186 (the moved synthetic
enclosure paragraph — "timing envelope", "nonnegative partial-record enclosure" and the
clipping arithmetic all now precede it, which is exactly what Ask 11 wanted); 293–316 apart
from item 3; 374–398 (R/R_cm contrast, strict noncollapse, `nextafter`, \(2b\) — *b* is built
at 150); 777 and 821–826; 1360–1435 (A.3.10 rebuilds binary64, `ulp(1.0)` and the
member-envelope integral sum in place); 1439 (A.4 rebuilds "declared machine state",
"instrument-validation manifest" and "mint" at their new home, and none of the three survives
in the main text).

---

## 3. Reading order of the new §1 and the new abstract

**Abstract — 238 words** (lines 11–31; the HTML comment at 32 excluded; the seat's checker
agrees: `abstract_words=238, limit=250`). Down from 246. Ask 2 asked for ≤200.

Order as written: (1) problem/scope, 11–12 → (2) glossary, 12–14 → (3) method, 14–15 →
(4) **not claimed**, 16 → (5) **not claimed**, 17–18 → (6) **glossary**, 18–20 →
(7) what was found, 20–23 → (8) what was found, 24–27 → (9) scope, 28–29 →
(10) not claimed, 30–31.

**The reading order does not hold.** The first sentence that breaks it is line 16:

> "This paper specifies the sensitivity calculation and demonstrates it on synthetic inputs; it reports no sensitivity ratio on measured inference data."

— a *what-is-not-claimed* sentence arriving before anything measured or found. I record it as
the break but do **not** recommend moving it: Ask 1 and contract item A1 demanded it "up front"
deliberately, and page-one honesty is worth the order cost.

The first *unmandated* break is line 18–20:

> "Fitted onsets and offsets are switch-on and switch-off times selected by matching predicted interval-average power to the recorded trace."

A definition sitting between two limitation sentences and the results — the exact residue Ask 2
named. *Minimal cure (word-neutral, keeps 238):* move this sentence to the head of the abstract
beside 12–14, or delete it and let §1 19–20's identical build carry it (it already does, at 76–83).

One further abstract defect, from my own RO-4 cure text: line 31 ends "(Section 3's R ≥ 2 test)"
and *R* is a bare symbol in the abstract. *Cure:* "(Section 3's doubling test)". *(Nit 10.)*

**§1 — the order holds from line 45 onward, and breaks in the first paragraph.**

Lines 45–116 run cleanly: measurand and interval-overlap allocation (45–58) → machine scope
(60–64) → clock placement (66–74) → pulse calibration and the transfer assumption (76–88) →
cell and estimands (90–103) → the short-prefill question (105–110) → what the evidence tests
(112–116). The removal of the synthetic-enclosure block and the floor apparatus measurably
improved this; a reader now reaches the paper's actual question ~44 lines earlier.

The break is paragraph 1 (36–43, 151 words), which now does four jobs in one block:

> 36–37: "This methods/diagnostic paper asks how a software power record can support an allocation to separate parts of an inference request. **This paper specifies the sensitivity calculation and demonstrates it on synthetic inputs; it reports no sensitivity ratio on measured inference data. The raw captures behind the historical numbers are retained under project custody and are not released; the synthetic examples are the only fully reproducible part. Custody means that each named input's fingerprint still matches its recorded bytes.** macOS `powermetrics` is the power sampler used here."

Problem → two honesty statements → a gloss of a term used once and never again in §1 →
glossary. *Minimal cure:* split after the first sentence; put the two honesty sentences in
their own paragraph; drop the custody gloss here (§7 880–881 already carries the bolded
definition at the point of use). *(Should-fix 7.)*

---

## 4. New defects introduced by the round

### Blockers (2)

**NB-1. The estimand table on page one now names three criteria terms built 111 lines later
in another section.** Lines 97–101 vs 210–212, quoted in full as first-use item 1. This is the
defect class RO-2/RO-3 existed to remove, recreated by RO-3's own cure: B1 moved the defining
sentences into §3 and left the table that depends on them in §1.
*Minimal cure:* restore one sentence under the table at 102 —
"The absolute floor is built from centered repeat energies, the comparative floor from
same-model block differences, and a science contrast is a difference between two models;
Section 3 gives each construction." — and delete the now-duplicate 210–212 from §3, whose
paragraph already opens with the A/B/B/A definition.

**NB-2. The new floor-input construction depends on an allowance that is never defined.**
Lines 308–312, quoted as first-use item 3. \(h\) cannot be computed from the text, and \(h\)
determines \(E^L\)/\(E^U\), which every corner enumeration in §3 consumes. Under the
replication bar this is not a gloss defect but a missing step.
*Minimal cure:* at 309 either name it in plain words — "plus the registered
joint-interpolation allowance, the extra half-width charged when a record's power must be
interpolated between reported averages rather than held flat (zero for the native
interval-average records used here)" — or, since 312 already says it is zero for every record
this paper uses, delete the addend and keep 312's sentence as the reason.

### Should-fix (8)

1. **New synonym pair "accepted region" / "allowed region"** (82, 137, 582, 818; A.3.5 1190),
   first-use item 4. *Cure:* use "accepted region" everywhere, since A.3.5 and the SVG own it,
   and move the 137 gloss onto that name.
2. **"that protocol" dangles at 237** (first-use item 5). *Cure:* "in the prospective
   comparison protocol linked in Section 3".
3. **"resolution bound" orphaned at 866** (first-use item 9). *Cure:* "and a detection
   threshold fixed before collection" — no term of art needed in a related-work sentence.
4. **"the 5% and 1-mW constants" unresolvable at 819** (first-use item 6). *Cure:* "on the 5%
   loss tolerance and the 1-mW noise floor of Appendix A.3.5".
5. **"Table 4" now lives in Appendix A.3.10 but is cited from a §3 figure caption with no
   pointer, under a main-text-style number in an appendix whose other tables are A1/A2/A3.**
   > 508 (Figure A4 caption, §3): "The lower rows apply one shared sign and one local sign per block, enumerate **the cases in Table 4**, and identify the maximum complete bound."

   > 1415 (A.3.10): "Table 4. All eight sign cases from the full-precision SYN-01 fixture."

   *Cure:* renumber to "Table A4" and cite it as "Table A4 (Appendix A.3.10)" at 508. This is
   the RO-7 numbering defect reproduced in the table series by D2's move.
6. **"the fit's discrepancy limit" promoted into the main text and still undefined** (137),
   first-use item 8. *Cure:* "…surviving the loss tolerance of Appendix A.3.5".
7. **§1 paragraph 1 does four jobs in 151 words** (36–43); cure in section 3 above.
8. **Figure 2's caption asserts an axis label the SVG does not carry.**
   > 575: "the vertical axis is fitted edge excursion in milliseconds (**the axis label**)"

   The SVG's axis title is `excursion (milliseconds)`. *Cure:* "the vertical axis, labelled
   `excursion (milliseconds)`, is the fitted edge excursion — fitted edge time minus commanded
   edge time — in milliseconds." Text-side only; the SVG stays pinned.

### Nits (10)

1. "Huber" unglossed at 143 (first-use item 7). *Cure:* "…sums Huber scores — squared for
   small differences, proportional for large ones — of…".
2. **Duplicated gloss, "retained":** abstract 28–29 "windows whose evidence bytes are kept on
   disk and never overwritten" and §4 682–683 "retained, meaning kept on disk as preserved
   evidence and never overwritten". *Cure:* drop the §4 apposition.
3. **Duplicated gloss, "custody":** §1 37 "Custody means that each named input's fingerprint
   still matches its recorded bytes." and §7 880–881, the same sentence with **Custody** bolded.
   *Cure:* drop the §1 copy (see should-fix 7).
4. **Duplicated gloss, "allowed region":** 137 "the allowed region, which contains every edge
   pair surviving the fit's discrepancy limit" and 582–583 "An allowed region contains every
   edge pair surviving the fit's discrepancy limit." RO-5 asked for the definition to *move*;
   it was copied. *Cure:* at 582 write "The allowed region defined in Section 2…".
5. **RO-9's pointer is now self-referential.** 376–377 "a nonnegative per-block joule allowance
   **derived in Section 3**" sits *inside* §3 and points forward to \(q_j\) at 420. *Cure:*
   "derived below as \(q_j\)".
6. **No blank line before the §3 heading at 200.** Line 199 ends a paragraph and 200 is
   `### Comparing the moved-edge limit and point-only value`. CommonMark lets an ATX heading
   interrupt a paragraph and `check_markdown` passes, but it is a move artifact. *Cure:* insert
   a blank line.
7. **"the artifacts" returns at 641** after S-4 removed it elsewhere. *Cure:* "(`identifiable`
   — the label a phase receives when its record support reaches the minimum)".
8. **§5's new raw-capture sentence at 777 precedes the "First,/Second,/Third," enumeration**
   without a number of its own, so the reader meets an unnumbered fourth limitation first.
   *Cure:* move it after the "Third," paragraph, or fold it into "First,".
9. **\(b\) acquires a third name at 294:** "the window's operative **calibration** allowance",
   against "operative **timing** bound" at 150 and 403. *Cure:* use "operative timing bound".
10. **Bare *R* in the abstract at 31.** Cure in section 3 above.

---

## 5. Same-signature statement

**Yes — four classes from record 04 recur in the round-1 output.**

1. **Term used before it is built (RO-2/RO-3/S-1/S-14's class).** Round 1 cured eight of the
   nine reading-order defects and then created four fresh instances of the same class, all at
   the seams of the moves it performed: the estimand-table floor names (NB-1), the
   joint-interpolation allowance (NB-2), "resolution bound" orphaned at 866, and "the 5%
   constants" at 819. This is the round's dominant signature, and both new blockers belong to it.
2. **Synonym pair never reconciled (S-7).** S-7's three named pairs were cured exactly; a new
   pair, "accepted region"/"allowed region", was introduced at 82 in the same round.
3. **Text naming a figure element the figure does not carry (F-1/F-2).** B-1's cure removed the
   phantom band; F-2's cure added a phantom axis label at 575.
4. **Unresolvable internal referent (S-4).** "in the artifacts" was deleted at two sites and
   reappeared at 641 as "the artifacts' label".

Classes 1 and 3 are literal repeats of blocker-tier defects from 04. Per the standing
escalation trigger — two consecutive rounds failing with the same signature is a structural
problem, and the next spend is a consult, not another round — I flag class 1 explicitly: the
mechanism that produced it is that paragraph moves were executed against a finding list rather
than against the first-use ledger, so every term whose *definition* moved was checked and every
term whose *use* stayed behind was not. The cheap structural cure is to re-run the first-use
ledger mechanically over the whole main text after the fix round rather than over the moved
paragraphs only, and to add one contract clause to every future move item: "name the sites that
*use* the moved text and confirm each still resolves." That is a lens change, not a third pass
of the same lens.

**Two blockers found** (NB-1, NB-2); both are sentence-level cures inside the existing scope —
no new experiment, no new numeral, no new section, no SVG change, D-174 respected.
