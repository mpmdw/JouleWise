# Review — `docs/paper/draft-v2-skeleton.md`, PEDAGOGY + STRUCTURE lens (Opus)

Reviewer: Opus 5, read-only. Source read: `/Users/edr/code/JouleWise-wt-paper-n-ref`
(detached checkout of origin/main dbe6c675), `docs/paper/draft-v2-skeleton.md`,
1459 lines. Main text §1–§8 = lines 7–972; Appendix A = lines 974–1459.
Whole main text read before writing. No file in the reference checkout was modified;
no test was run.

Line numbers below are 1-based lines of `docs/paper/draft-v2-skeleton.md` at that revision.

---

## 1. First-use ledger (main text §1–§8, abstract included)

Verdict key: **PASS** = built or glossed in plain words at or before first use.
**LATE** = the meaning arrives only in later text (line cited); a definition that
lands only in Appendix A, only in a figure caption, or only later in the same
paragraph is LATE. **NEVER** = no definition anywhere in the main text.

| # | Term / criteria word | First use | Defined / built | Verdict |
|---|---|---:|---:|---|
| 1 | sampling record | 11 | 11–12 (abstract), re-built 41–43 | PASS |
| 2 | prompt processing / prefill | 13, 45 | 13–14, 44–45 | PASS |
| 3 | token generation / decode | 14, 46 | 14, 46 | PASS |
| 4 | phase boundary | 16 | 16 ("the dividing time"), 47–48 | PASS |
| 5 | phase (as a countable object) | 13 | 46–47 | PASS |
| 6 | registered timing domain | 20 | 20 ("the edge movements fixed before collection") | PASS |
| 7 | **registered** (as a standalone qualifier: registered window 71, registered comparison method 108, registered operational resolution guard 130, registered sensitivity question 134, "is registered as future diagnostic work" 102) | 71 | never glossed on its own; the reader must back-form it from the 20/57 apposition | LATE (57, by inference only) |
| 8 | held-average reconstruction | 57 | 57–58 ("holds each record at its reported average") | PASS |
| 9 | **three-record minimum** | 29 | 669–672 | **LATE (669)** |
| 10 | **record support** | 168 (prose; line 36 is an HTML comment) | 666–667 | **LATE (666)** |
| 11 | **retained** (as a custody qualifier, ~50 uses) | 33 | 721–722 ("kept on disk as preserved evidence and never overwritten") | **LATE (721)** |
| 12 | measurement window | 34 | 94 ("one uninterrupted measurement session") | LATE (94) |
| 13 | fitted onset / offset | 23–24 | 23–24 ("switch-on and switch-off times selected by matching predicted interval-average power to the recorded trace") | PASS |
| 14 | commanded graphics-processor pulse | 18 | 18–19 (abstract), 92–94 | PASS |
| 15 | **phase-energy dominance** | 35 | 380–382 (defined as R ≥ 2) | **LATE (381)** |
| 16 | interval-overlap allocation | 53 | 53–55 | PASS |
| 17 | integrated energy | 55 | 55 (∫P dt over the record span) | PASS |
| 18 | timing envelope | 56 | 56–58 | PASS |
| 19 | synthetic enclosure diagnostic | 65 | 65–70 (worked example is the definition) | PASS |
| 20 | nonnegative partial-record enclosure | 68 | 68–70 | PASS |
| 21 | MLX | 75 | 75–76 | PASS |
| 22 | monotonic clock | 81 | 81–82 ("a counter that advances but is never corrected to civil time") | PASS |
| 23 | bracketed readings | 84 | 83–85 | PASS |
| 24 | clock-anchor bound | 96 | 96–97 | PASS |
| 25 | pulse-derived limit | 97 | 95–97 | PASS |
| 26 | transfer assumption | 88 | 98–99 | PASS (gloss 10 lines later, same argument) |
| 27 | inserted-gap check | 100 | 100–102 | PASS |
| 28 | configuration cell / **cell** | 104 | 104–107 | PASS |
| 29 | power-measurement boundary | 105 | 105–107 ("which power is counted") | PASS |
| 30 | estimand | 108 | 108–109 | PASS |
| 31 | A/B/B/A block | 112 | 112 | PASS |
| 32 | false difference | 113 | 113–114 (operational gloss only) | PASS (weak) |
| 33 | absolute floor | 114 | 114–115 | PASS |
| 34 | comparative floor | 115 | 115 | PASS |
| 35 | science contrast | 116 | 116 | PASS |
| 36 | component | 128 | 127–128 | PASS |
| 37 | resolution bound | 129 | 129–132 (circular: defined against "the safeguards in protocol P.3") | LATE (never resolved; see row 39) |
| 38 | detection floor | 129 | 129 ("in the advisor's terminology" — the advisor is never identified) | LATE |
| 39 | **protocol P.3** | 131 | nowhere — cited again 558, 811 | **NEVER** |
| 40 | **cell floor** | 132 | 131–132, but its content is entirely the unspecified P.3 safeguards | **NEVER (effectively)** |
| 41 | point-only value | 137 | 136–137 | PASS |
| 42 | moved-edge limit | 140 | 138–141 | PASS |
| 43 | independent-edge corner bound | 141 | 141 ("in the artifacts" — the artifacts are never identified) | PASS (weak) |
| 44 | independent-edge ratio | 142 | 142–143 | PASS |
| 45 | energy-allowance sign | 146 | 146–147; the underlying "block-level allowance" only arrives at 421 | LATE (421) |
| 46 | shared sign / local sign | 148 | 148–149 | PASS |
| 47 | **local corner** | 154 | 341–344 ("At each corner…"), 461–462 | **LATE (341)** |
| 48 | shared-energy-sign/local-corner sensitivity diagnostic | 154–155 | 155–156 (names its parts), full build 461–479 | LATE (474) |
| 49 | phase reduction | 163 | 163 ("computing separate phase energies from the overlapping sampler records") | PASS |
| 50 | measurement refusal | 164 | 164–166 | PASS |
| 51 | **registry** (registry SYN-03, DX-001, DG-067…) | 329 | nowhere in the main text | **NEVER** |
| 52 | science window | 191 | 191 ("one uninterrupted measurement session" — the same gloss already spent on "measurement window" at 94; the two names are never reconciled) | PASS (weak) |
| 53 | declared machine state | 191 | 191 | PASS |
| 54 | instrument-validation manifest | 191 | 191 | PASS |
| 55 | mint | 191 | 191 ("the analysis run that issues the paper's fixed results") | PASS |
| 56 | **frozen** | 191 (first use, "the frozen reservation plan") | 191, ~3 sentences later ("**Frozen** means fixed and fingerprinted before collection") | LATE (same paragraph) |
| 57 | warm-up pulse | 191 | 191 ("which are discarded") | PASS |
| 58 | quiet trace / quiet record | 191 | 191, threshold at 194–195 | PASS |
| 59 | resting power *b* | 193 | 193–194 | PASS (but see Blocker 2) |
| 60 | σ (robust scale) | 194 | 194 (`1.4826 × MAD`; the constant 1.4826 is never explained) | PASS (weak) |
| 61 | **uncommanded plateau** | 196 | "plateau" at 204; "uncommanded" never | **LATE (204) / partly NEVER** |
| 62 | **amplitude** (vs "pulse height", 204) | 197 | never defined; 204 introduces the synonym "pulse height" without linking them | **NEVER** |
| 63 | **fitted loss / no-pulse loss** | 197–198 | informal at 204 ("scores the difference…"), formal only in A.3.5 | **LATE (204) — no units, no formula in main text** |
| 64 | fitted shift | 199 | 204 ("a shifted rectangular pulse") | LATE (204) |
| 65 | trace coverage | 200 | 204 | LATE (204) |
| 66 | the detector | 204 | never introduced as an object; first appears mid-sentence | NEVER (nit) |
| 67 | fixed time margin | 204 | number never given in main text (0.75 s appears at 200 under a different name) | NEVER (nit) |
| 68 | plateau | 204 | 204 ("its flat high-power portion") | PASS at 204, LATE for the 196 use |
| 69 | **rectangle / search rectangle** | 204 | never — the text never says the rectangle lives in (onset-shift × offset-shift) space | **NEVER** |
| 70 | shared search-work limits | 204 | 204 | PASS |
| 71 | accepted capture bound | 204 | 204 | PASS |
| 72 | **native power record** (vs "sampling record") | 206 | never reconciled with "sampling record" | **NEVER** |
| 73 | first-record endpoint | 206 | 206 | PASS |
| 74 | Student-*t* | 208 | 208 ("a small-sample bell curve whose 99% quantile…") | PASS |
| 75 | calibration-acceptance rule | 208 | 208 | PASS |
| 76 | two-draw rule | 208 | 208 | PASS |
| 77 | minimum allowance | 208 | 208 | PASS |
| 78 | operative timing bound *b* | 208 | 208 (worked example at 208) | PASS (but see Blocker 2) |
| 79 | B_fiducial | 208 | 208, by pointer to A.3.6 | LATE (appendix) |
| 80 | stage | 212 | 212–213 | PASS |
| 81 | admitted | 213 | 213–214 | PASS |
| 82 | **entry check** | 215 | 215–216 (the figure it annotates labels the same object "admission gate") | PASS (text) / mismatch with Figure A2 |
| 83 | reference runs | 217 | 216–217 | PASS |
| 84 | members (of a block) | 219 | 219–220 | PASS |
| 85 | block difference | 220 | 220–221 | PASS |
| 86 | whole-window allowance | 225 | 225–232 | PASS |
| 87 | energy family | 226 | 226–227 | PASS |
| 88 | reference-trajectory excursion | 228 | 228–229 | PASS |
| 89 | issued repeatability bound | 230 | 230–232 | PASS |
| 90 | clip (a record) | 236 | 236–237 | PASS |
| 91 | absolute component / comparative component | 255–256 | 255–257 | PASS |
| 92 | **small-sample multiplier** | 276 | named only; no value, no formula, no placement rule anywhere in the main text | **NEVER** |
| 93 | unguarded / point-only unguarded value | 272 | 272–274 | PASS |
| 94 | admitted energy | 274 | 274–275 | PASS |
| 95 | independent units | 278 | 277–281 | PASS |
| 96 | sample standard deviation | 284 | 286–288 (display equation) | PASS |
| 97 | t_{.975,n−1} | 290 | 290–292 | PASS |
| 98 | prediction amount | 301 | 300–302 | PASS |
| 99 | **superscripts L / U** (B_1^L, A_1^U at 338–339) | 338 | never bound to "lower"/"upper"; the concept is at 333–334, the notation never | **NEVER** |
| 100 | block index *j* | 336 | never declared (and *j* is the pulse index in A.3.1) | NEVER (nit) |
| 101 | corner (of the enumeration box) | 342 | 341–344 | PASS |
| 102 | convex / convex combination / box | 345–348 | 345–349 ("box" itself never defined) | PASS (weak) |
| 103 | dominates | 381 | 380–383 | PASS |
| 104 | authenticated | 387 | 387–390 | PASS |
| 105 | binary64 / ulp(1.0) | 425 | 425–426 | PASS |
| 106 | member-envelope integral sum | 426 | 427–433 | PASS |
| 107 | onset set O_j / offset set P_j / zero-shift value z_j | 403–406 | 403–406 | PASS |
| 108 | shared lower/upper excursion d_j± | 408 | 408–413 | PASS |
| 109 | block-level energy allowance q_j | 421 | 417–423 | PASS |
| 110 | local half-width ℓ_j | 455 | 453–459 | PASS |
| 111 | fixture | 486 | 486–487 | PASS |
| 112 | **Source map** | 521 | 638–639 | **LATE (638)** |
| 113 | fail-closed | 567 | 567–568 | PASS |
| 114 | best-fit lag | 574 | 574 (and redundantly re-defined at 608) | PASS |
| 115 | protocol pulse (vs warm-up pulse) | 574 | 574 + 191 | PASS |
| 116 | diagnostic-era | 595 | 598 (three lines later, same paragraph) | LATE (598) |
| 117 | **D-078** (repository decision id) | 596 | apposition only; the decision itself is unresolvable from the paper | LATE/NEVER (nit) |
| 118 | **allowed region** | 626 | 626–627 — defined inside a figure caption, but needed at 204 | **LATE (626, caption)** |
| 119 | fit's discrepancy limit | 627 | never in main text | NEVER (nit) |
| 120 | record width | 660 | 659–660 | PASS |
| 121 | positive overlap | 662 | 662–665 | PASS |
| 122 | overlap count | 666 | 666–667 | PASS |
| 123 | resolvability / not resolvable | 674–676 | 674–677 | PASS |
| 124 | **identifiable / identifiability** | 686 | never glossed; the reader must equate it to "resolvable" from context at 691 | **NEVER** |
| 125 | interquartile range (IQR) | 726 | 725–727 | PASS |
| 126 | custody | 906 | 906–907 | PASS |

**Ledger counts: 126 rows — PASS 91, LATE 20, NEVER 15.**
(Rows carrying a mixed verdict — 40, 61, 68, 117 — are counted once, under the more
severe verdict: 61 and 117 count as NEVER, 68 counts as LATE.)

---

## 2. Redundancy map

14 pairs. For each: the two locations, which survives, and the exact replacement wording.

**RM-1 — prefill/decode/phase-boundary definitions (§1 vs §2).**
§1 41–48: "An inference request first reads its input through production of the first
output token; this paper calls that prompt processing, or *prefill*. It then emits later
output tokens; this is token generation, or *decode*. … The runtime-recorded time between
them is the **phase boundary**."
§2 176: "Prompt processing (*prefill*) reads the prompt through the first output token;
token generation (*decode*) emits later output tokens. A phase boundary is the
runtime-recorded time separating those phases."
*Keep §1 41–48.* Replace the §2 opening with: "Section 1 defined prompt processing
(*prefill*), token generation (*decode*), and the phase boundary between them."

**RM-2 — "repetition cannot remove this" (§1 vs §2).**
§1 61–63: "Repeating the request can narrow ordinary run-to-run scatter; it does not
remove this allocation sensitivity."
§2 176: "Repetition can reduce random scatter, but it cannot remove this systematic
reassignment."
*Keep §2 176* (it is the sentence the §2 argument turns on). Delete the §1 sentence;
§1 56–61 already makes the point with the envelope.

**RM-3 — the 30 W × 0.010 s = 0.30 J example, three times.**
§2 176: "Moving a boundary 0.010 s inside a 30-W record transfers 0.30 J between assigned
phases under the held-average reconstruction."
Figure 1 caption 182–187: "The gray rectangle is one 30-W average over [1.000,1.100] s.
… The blue hatched slice has the full 30-W height and 0.010-s width, hence 0.30 J."
§3 236–243: "a 30-W record from 1.000 to 1.100 s cut at a phase boundary of 1.040 s gives
prompt processing 30×0.040=1.20 J … This 0.30-J movement is the allocation sensitivity…"
*Keep §3 236–243* (it is the arithmetic the section needs) *and the Figure 1 caption*
(a caption must stand alone). Replace the §2 176 sentence with: "Figure 1 works the
arithmetic for one 30-W record; Section 3 repeats it in symbols."

**RM-4 — A/B/B/A block mechanics (§2 vs §3). The largest duplication in the paper.**
§2 219–224: "names its four **members** … \(A_1,B_1,B_2,A_2\) in that order. Its block
difference is \((B_1+B_2-A_1-A_2)/2\); a positive value means condition B used more energy
than condition A. The order balances conditions and suppresses a linear trend only when the
sums of the A and B run midpoints match; unequal runtimes or cooldowns can break that symmetry."
§3 256–268: "If the four phase energies in one block are \(A_1,B_1,B_2,A_2\), the block
difference is \(\delta=(B_1+B_2-A_1-A_2)/2.\) A positive difference means condition B used
more assigned phase energy than A. A/B/B/A balances order and suppresses a linear trend only
under the specified timing symmetry: the A and B run-midpoint sums must match. Unequal
runtimes or cooldowns break that balance…"
*Keep §3 256–268* (it is where δ is needed and where the display equation lives).
Replace §2 219–224 with: "Each science block uses A/B/B/A order — condition A, condition B,
condition B, condition A — and names its four **members**, meaning its four individual runs,
\(A_1,B_1,B_2,A_2\) in that order. Section 3 gives their block difference and the timing
symmetry it depends on."

**RM-5 — the definition of a cell (§1 vs §3).**
§1 104–107: "A **configuration cell**, shortened below to **cell**, is the set of runs with
one phase, workload, model, hardware, software, and power-measurement boundary…"
§3 253–254: "A cell groups runs that use the same phase, workload, model, hardware,
software, and power-measurement boundary."
*Keep §1 104–107.* Delete the §3 sentence; begin that paragraph "A cell has two
false-difference components."

**RM-6 — the 37/13 counts restated inside §4.**
§4 684–687: "37 of 50 phases overlapped two sampling records and the remaining 13 of 50
overlapped three. Accordingly, in this 1.5B population, 37 failed the three-record minimum…
and 13 passed."
§4 698–702: "Record identifiability depended on the model/stack in these retained
populations. Phases with only two overlapping records failed the three-record minimum: 37 of
the 50 1.5B phases and none of the 50 7B phases, which overlapped three or four records each."
*Keep 684–687 and 689–693* (the two population paragraphs). Replace 697–702 with the single
sentence: "In these retained populations the overlap count, not phase duration alone, decided
resolvability, and it differed between the two model stacks."

**RM-7 — §4 vs §8, verbatim.**
§4 698–700 and §8 936–938 are word-for-word identical: "Phases with only two overlapping
records failed the three-record minimum: 37 of the 50 1.5B phases and none of the 50 7B
phases, which overlapped three or four records each."
*Keep the §4 instance* (it sits with its evidence). Delete the sentence from §8; the
preceding §8 sentences (932–935) already carry both counts.

**RM-8 — abstract vs conclusion, record support.**
Abstract 28–31 and §8 932–935 are near-verbatim (37/50, 13, 33, 17).
Abstract↔conclusion overlap is conventional and I do **not** recommend removing it;
the fix is to stop the conclusion from *also* re-deriving it (see RM-7).

**RM-9 — abstract vs conclusion, edge counts.**
Abstract 25–27 / §8 923–926 ("all 59 fitted onsets occur after their commands and 49 of 59
fitted offsets occur before them; transfer … untested"). Conventional; keep both.

**RM-10 — abstract vs conclusion, held-average disclaimer.**
Abstract 21–22: "The allocation holds each record at its reported average; it does not bound
physical phase energy under arbitrary within-record allocations."
§8 928–932: "…conditional on the held-average reconstruction, which holds each record at its
reported average. It does not enclose physical phase energy under arbitrary within-record
allocations."
Conventional pairing; keep both, but make the verbs agree — §8 says "enclose", the abstract
says "bound", and §1 58 says "does not locate actual energy within records". *Pick one verb.*
Recommend "bound" everywhere.

**RM-11 — "best-fit lag" defined twice in §4.**
574: "A **best-fit lag** is fitted edge time minus its matching command time."
608–609: "A best-fit lag is fitted edge time minus its command time: positive means late,
negative means early."
*Keep 608–609* (it adds the sign convention). Replace 574 with: "Each onset or offset lag
below uses its commanded edge as zero (defined at the start of 'Historical current-method
edge result'); bounds are elapsed durations rather than positions on either clock."

**RM-12 — monotonic-clock gloss, verbatim twice.**
§1 81–82 and §2 206: "a counter that advances but is never corrected to civil time".
*Keep §1 81–82.* In §2 206 write simply "readings from the monotonic clock".

**RM-13 — "one uninterrupted measurement session", verbatim twice.**
§1 94 (for "measurement window") and §2 191 (for "science window").
*Keep §1 94.* In §2 191 write "Immediately before and after each science window (a
measurement window as defined in Section 1)…" — or, better, drop "science window" and use
"measurement window" throughout (see Should-fix 7).

**RM-14 — the transfer limitation stated twice, 9 lines apart.**
§5 809: "Transfer of the pulse-derived timing allowance to inference was not tested."
§5 818: "First, the pulse-to-inference transfer was not tested."
*Keep 818* (it heads the enumerated limitations). Delete 809 and start that paragraph at
"The shared-energy-sign/local-corner ratio is a sensitivity calculation…".

Also noted, not counted as a prose pair: the HTML source comment at line 36 is byte-identical
to the one at line 943.

---

## 3. Reading-order defects

**RO-1 — §2 states the acceptance thresholds before the algorithm that produces the
quantities they threshold.** Lines 193–202 judge "fitted loss", "no-pulse loss", "fitted
shifts", "amplitude", and the "uncommanded-plateau check"; the detector that produces all of
them is described at 204. The draft admits the inversion at 201–202: "These numeric rules
define 'far enough,' 'better,' and 'accepted' in the following summary." *Cure (minimal
reorder, no rewriting):* move the paragraph at 193–202 to immediately after the paragraph at
204, and change its opening from "Before using the checks, define resting power b…" to
"The checks above use the following fixed numbers. Define resting power…".

**RO-2 — the abstract's headline result depends on a rule built in §4.** "failed the
three-record minimum" (29) and "record support" (168) are decided at 666–672. *Cure:* at
line 29, replace "failed the three-record minimum" with "fell below the three-record
minimum this paper requires for a phase split" (word-neutral; see §5).

**RO-3 — §1 builds the floor/estimand apparatus 130 lines before any mechanism, and for a
result the paper never reports.** Lines 108–132 introduce estimand, absolute floor,
comparative floor, science contrast, component, resolution bound, detection floor, cell
floor, and protocol P.3; the mechanism arrives at 270–330, and §3 558–559 then says "no new
component floor is published here." *Cure:* compress 108–132 to the three rows of the table
plus one sentence — "JouleWise bounds each floor source separately; Section 3 gives the
construction, and no floor value is published in this paper" — and move the resolution-bound
/ detection-floor / cell-floor definitions to §3 immediately before line 270, where they
are first needed.

**RO-4 — "phase-energy dominance" is used in the abstract (35) and only defined at 381.**
*Cure:* at line 35 write "no new model-energy comparison, and no finding that boundary
placement is the limiting uncertainty (Section 3's R ≥ 2 test)".

**RO-5 — "allowed region" is defined inside a figure caption in §4 (626) but is needed by
§2 204** ("it encloses every pair close enough to that fit"). *Cure:* move the bolded
definition to line 204: "…encloses every onset/offset pair close enough to that fit — the
**allowed region** — a rectangle is rejected only when…", and delete the bold from 626.

**RO-6 — §1 72 and §2 214 send the reader to Appendix figures for their own mechanisms.**
Line 72 ("Appendix Figure A1 shows the records, window, and three energy results") carries
§1's central worked example; line 214 ("Appendix Figure A2 orders the before-and-after pulse
calibrations…") carries §2's window structure. *Cure:* promote both to the main text as
Figures 2 and 3 and renumber, or — if the figure budget is fixed — state in one clause at
each site what the reader loses by not turning to the appendix.

**RO-7 — Figures "A3" and "A4" are physically in main-text §3 (362, 549).** A reader going
front to back meets Figure A3 at line 355 having seen neither A1 nor A2, which live at 1416
and 1457. *Cure:* renumber the two §3 figures to 2 and 3 and the existing Figures 2 and 3
to 4 and 5, or move A3/A4 to the appendix and cite them from §3.

**RO-8 — "Source map:" is used as a defined construct at 521 and defined at 638.**
*Cure:* at 638 delete "A source map links each displayed value or figure mark to its
supplying artifact and field." and insert it at 520, before the first use.

**RO-9 — "block-level allowance" is used in §1 146–147 to explain the energy-allowance
sign, but q_j is only constructed at 417–423.** *Cure:* at 146 replace "a nonnegative
block-level allowance" with "a nonnegative per-block joule allowance derived in Section 3".

---

## 4. Figure and equation check

### Figures

| Figure | Text ref | Verdict |
|---|---|---|
| Figure 1 (180) | 178, caption 182–187 | **FAIL** — see below |
| Figure 2 (615) | caption 617–636 | FAIL (two items) |
| Figure 3 (708) | 704–706, caption 710–719 | PASS |
| Figure A3 (362) | 355 | PASS on element naming; numbering defect RO-7 |
| Figure A4 (549) | caption 551–555 | PASS on element naming; numbering defect RO-7 |
| Figure A1 (1416) | cited from §1 72 | PASS on element naming; reading-order defect RO-6 |
| Figure A2, the A.7 schematic (1457) | cited from §2 214 | FAIL (one item) |

**F-1 (Figure 1) — the text names a visual element the figure does not contain.**
Line 178: "Figure 1 shows interval-average power around the recorded boundary … *with the
allowed boundary positions marked as a band.* The hatched area is the energy reassigned
between phases *when the boundary moves across that band*." The SVG
(`figures/fig1_boundary_attribution.svg`) contains no band: its only boundary marks are a
solid line at 1.040 s and a dashed line at 1.050 s, and its own legend reads "Solid line:
recorded boundary 1.040 s… Dashed line: moved boundary 1.050 s…". The caption at 182–187
describes the same two lines. A reader hunting for "the band" finds nothing. (Blocker 1.)

**F-2 (Figure 2) — axis name mismatch.** Caption 618–619: "the vertical axis is signed
fitted lag in milliseconds." The SVG's axis title is "excursion (milliseconds)". Neither
text says the two words name the same quantity — and "excursion" already carries two other
meanings in this paper (see Should-fix 8).

**F-3 (Figure 2) — a term defined in a caption.** "An **allowed region** contains every edge
pair surviving the fit's discrepancy limit" (626–627): a bolded first definition inside a
figure caption, for a concept the main text needed 420 lines earlier. "the fit's discrepancy
limit" is itself undefined anywhere in the main text. (RO-5.)

**F-4 (Figure A2) — the figure labels the gate differently from the text.** §2 215 defines
"the **entry check**, the pass/fail checks on recorded machine state that a stage must
satisfy before its first run is measured"; the SVG labels that box "admission gate", and its
note begins "The admission gate re-checks quiet state, power policy, thermal pressure…".
Neither name points at the other. The caption at 1459 also says "three opening references"
and "three closing references"; the text (216–217) gives no count.

Minor: the file names no longer track the labels — Figure 2 is `fig4_edge_excursions.svg`
and Figure 3 is `fig5_phase_record_overlap.svg`; `fig3_decision_gates.svg` exists in
`docs/paper/figures/` and is referenced nowhere in the draft.

### Display equations, §2–§3

§2 contains no display equations. §3 has 13. Symbols checked against first use in the text:

- δ (261) — "block difference", named 258. PASS.
- A₁,B₁,B₂,A₂ (261) — named 219–220 and 257. PASS.
- s_r, E_i, Ē, r_i, r̄, n (287) — all named 277–284. PASS.
- t_{.975,n−1} (297) — named 290–292. PASS.
- U_abs,point (295) / U_cmp,point (313) — pattern named 136–137. PASS.
- s_δ (307), δ̄ (303) — named 303. PASS.
- **δ_j^−, δ_j^+ and the superscripts L, U (338–339) — FAIL.** B₁^L, B₂^L, A₁^U, A₂^U are
  never bound to "lower" and "upper". The concept is at 333–334 ("Each admitted repeat energy
  has lower and upper values"), the notation never. *Cure:* at 337 insert "writing E^L and
  E^U for a member's lower and upper values,".
- **Block index j (336–339) — FAIL.** *j* is introduced without declaration, and in
  A.3.1 (1030) *j* is the pulse index. *Cure:* at 336 write "first form block *j*'s
  difference interval".
- 2^n / 2^{4n} (341) — *n* is the number of blocks here and the number of repeats at 335;
  the text says so at 277–279. PASS (tight but correct).
- R (374) — named 371. PASS.
- d_j^−, d_j^+ (411–412) — named 408. PASS.
- q_j (418), z_j (406), O_j, P_j (403–406) — all named. PASS.
- Member-envelope integral sum (428) — c_m and P_m(t) named at 429–430, start_m/end_m
  self-evident. PASS.
- **p (435) — FAIL (collision).** *p* is the rounding pad here, the quartile fraction at
  728 ("interpolate quartiles at zero-based positions (n−1)p for p=0.25 and 0.75"), a phase
  endpoint subscript at 661 (p_s, p_e), and combined power p_i in A.3.1. *Cure:* rename the
  pad to π or `pad`.
- ℓ_j (458) — named 455–456. PASS.
- **r_{jm} (454) — FAIL (collision).** *r* is the residual r_i at 283, the record endpoint
  subscript r_s/r_e at 661, the resolution R_s in the table at 576, and the local energy
  change here. *Cure:* rename to λ_{jm} or `loc_{jm}`.
- δ′_j (466), s, e_j (461–462) — named. PASS.
- R_cm (477) — named 474. PASS.
- M (434) — defined in place. PASS.
- min(p_e,r_e) > max(p_s,r_s) (664) — all four named 660–662. PASS.
- **b (400–402) — FAIL (collision).** See Blocker 2.

---

## 5. Abstract

**Word count: 246** (lines 11–35; the HTML comment at 36 excluded). Cap 250 — **passes**,
with 4 words of headroom.

(a) *What was measured* — yes. A non-specialist finishes the abstract able to say: on one
Apple machine, macOS `powermetrics` records were re-analysed; in one historical GPU pulse
capture all 59 fitted switch-on times fell after their commands and 49 of 59 switch-off
times fell before them; and for two model stacks the number of sampler records overlapping
the prompt-processing phase was counted (37/50 vs 0/50 below the cutoff).

(b) *What was NOT claimed* — yes, and unusually explicitly: "does not bound physical phase
energy under arbitrary within-record allocations" (21–22); "transfer of its timing allowance
to inference remains untested" (26–27); "supplies no new model-energy comparison or
phase-energy dominance result" (34–35).

**Abstract passes.** No rewrite proposed.

Two sentence-level defects inside it are carried as findings, not as a rewrite, and both
cures are word-neutral so the 250-word cap survives:
- 29, "failed the three-record minimum" → "fell below the three-record minimum this paper
  requires" (+4 words → 250, at the cap). If that is too tight, drop "Labelled" from line 32.
- 35, "phase-energy dominance result" → "finding that boundary placement dominates" (−1 word).

---

## 6. Findings

### Blockers (3)

**B-1. Figure 1's introducing sentence describes an element that is not in the figure.**
> "Figure 1 shows interval-average power around the recorded boundary between prompt
> processing and token generation, **with the allowed boundary positions marked as a band**.
> The hatched area is the energy reassigned between phases **when the boundary moves across
> that band**." (178)

`figures/fig1_boundary_attribution.svg` draws one solid boundary at 1.040 s and one dashed
boundary at 1.050 s and no band; its own note reads "Blue hatching is the energy reassigned
under held averages." The caption (182–187) agrees with the SVG, so line 178 is the only
wrong text — and it is the reader's first instruction about the paper's first figure.
*Minimal cure:* replace 178 with — "Figure 1 shows interval-average power around one record
that the phase boundary crosses. The solid line is the recorded boundary and the dashed line
is the same boundary moved 0.010 s; the hatched area between them is the energy reassigned
between phases, and the request total does not change."

**B-2. The symbol *b* names two different physical quantities in the same section, and §3's
central construction depends on which one is meant.**
> "Before using the checks, define resting power **b** as the median of quiet records and
> σ=max(1.4826 × median absolute deviation from **b**, 0.001 W)… With **b=0 W** and
> σ=0.001 W…" (193–196)

> "The window's distinct **operative timing bound** \(b\) is the larger capture bound plus
> \(\max(|B_{\mathrm{post}}-B_{\mathrm{pre}}|,9.724\ \mathrm{ms})\)… \(b=29+\max(4,9.724)=38.724\) ms." (208)

> "The shift candidates are \(-b,0,+b\), where \(b\) is the window's authenticated operative
> timing bound from Section 2" (400–401)

Fifteen lines separate a *b* in watts from a *b* in milliseconds, and §3's shared-shift
replay, the q_j allowance, the member-envelope integral (428, limits start−b … end+b) and the
fixture constant "b=0.03678263869781979 s" (505) all ride on the second one. A reader
rebuilding §3 from the text — the stated bar — has to guess. Upper-case *B* is meanwhile a
third thing (B_pre, B_post, B_fiducial), and *B* is also a block-condition label (B₁, B₂).
*Minimal cure:* rename the resting power in 193–196 to `P_rest` (four substitutions: 193,
194, 195, and "With b=0 W" at 195), leaving *b* to mean the operative timing bound only.

**B-3. The capture-acceptance criteria are stated in terms of a quantity ("loss") that the
main text never defines, with worked examples that are bare unlabelled numbers.**
> "A pulse must rise at least 10 W and have amplitude/σ≥10. Its fitted loss must be strictly
> below half the no-pulse loss: **losses 4 and 10 pass; 5 and 10 fail.**" (197–198)

"loss" has no definition, no units, and no formula in the main text; "amplitude" is never
defined either, and 204 introduces a second name for it ("pulse height") without linking
them. The example "losses 4 and 10 pass; 5 and 10 fail" cannot be parsed at first reading:
the reader cannot tell which number is the fitted loss and which the no-pulse loss, in what
unit, or why 5 vs 10 fails a strict-inequality test that 4 vs 10 passes. This is the exact
failure the writing standard names — a criteria word whose meaning arrives only later (204,
informally) or only in Appendix A.3.5.
*Minimal cure:* after RO-1's reorder, write 197–198 as — "A pulse must rise at least 10 W
above resting power and have height/σ ≥ 10. Its **fit loss** — the score of Appendix A.3.5,
which sums how far each predicted interval average sits from the observed one, in W² — must
be strictly below half the loss of the no-pulse model fitted to the same records: a fit loss
of 4 W² against a no-pulse loss of 10 W² passes; 5 W² against 10 W² fails."
(Substitute the true unit if it is not W²; the sibling methods seat owns that fact.)

### Should-fix (14)

**S-1. "record support" and the "three-record minimum" decide the paper's headline number
and are built only in §4.** First uses at 29 (abstract) and 164/168 (§1); construction at
666–672. *Cure:* RO-2's word-neutral abstract edit, and at 168 replace "record support" with
"how many sampler records overlap a phase (Section 4's record support)".

**S-2. "retained" is a custody criterion doing load-bearing work from line 33 and is glossed
only at 721.** It qualifies captures, corpora, populations, traces, fixtures and bounds ~50
times. *Cure:* gloss at first use, line 33: "across retained measurement windows — windows
whose evidence bytes are kept on disk and never overwritten —".

**S-3. "protocol P.3", the "cell floor", and the "small-sample multiplier" are named as
steps of the published pipeline and never built.**
> "a registered operational resolution guard for assigned-energy differences in that cell
> before the safeguards in protocol P.3; the artifacts call the final gate value after those
> safeguards the **cell floor**." (130–132)

> "The later factor is the **small-sample multiplier**." (276–277)

P.3 is cited three times (131, 558, 811) and never identified — not as a section of the
linked prospective-comparison protocol, not as anything. "cell floor" is defined entirely by
reference to it. The small-sample multiplier is named, said to be applied "before the
whole-window allowance" and to be excluded from the point-only value, and never given a
value, a formula, or a location. *Cure (scope-neutral):* at 131 write "before the publication
safeguards of Section P.3 of the [prospective comparison protocol](protocol/prospective-comparison-protocol.md)";
at 276 write "The later factor is the **small-sample multiplier**, specified with the
publication safeguards in that protocol; no value in this paper uses it."

**S-4. Internal project vocabulary appears in the main text with no external referent:**
"the **detection floor** in the advisor's terminology" (129), "the artifacts call the final
gate value … the **cell floor**" (131–132), "called the **independent-edge corner bound** in
the artifacts" (141), "(registry SYN-03)" (329), "registry DX-001 binds" (639), "registry
DG-135–139" (692), "the repository decision D-078" (596), "(registry DS-34)" (901). An
outside reader cannot resolve "the advisor", "the artifacts", or "the registry".
*Cure:* delete "in the advisor's terminology" and "in the artifacts" (the alternate names add
nothing to a reader outside the project); and at the first registry citation (329) write
"(results registry row SYN-03; the registry is the project's row-by-row index of every
displayed value and its supplying artifact)".

**S-5. "identifiable" / "identifiability" is never glossed** (686, 691, 697, 936), while its
negation *is* ("not resolvable", 674–677). *Cure:* at 685–686 write "and 13 passed
(`identifiable` — the artifacts' label for a phase whose record support reaches the
minimum)".

**S-6. §2's acceptance thresholds precede the algorithm they threshold.** See RO-1; the
paragraph move is the whole cure.

**S-7. Three synonym pairs are never reconciled.** "measurement window" (34) / "science
window" (191), given the identical gloss in two places; "amplitude" (197) / "pulse height"
(204); "sampling record" (11) / "native power record" (206, 565, 789). *Cure:* pick one of
each — "measurement window", "pulse height", "sampling record" — and use it throughout; where
the raw plist object genuinely needs distinguishing, write "the native (unparsed) sampling
record" once, at 206.

**S-8. "excursion" carries three unrelated meanings.** Joules, as the spread among reference
means: "the **reference-trajectory excursion**—the spread among the mean energies of the
opening, midpoint, and closing reference runs" (228). Joules, as a shared shift effect:
"Define the shared lower and upper excursions" (408). Milliseconds, as edge displacement:
"equals the retained worst edge excursion" (630), and it is Figure 2's y-axis title.
*Cure:* keep "excursion" for the millisecond quantity only (it is the one the figure and the
script name use); rename 408 to "shared lower and upper **energy swings**" and 228 to
"reference-trajectory **spread**".

**S-9. Equation 337–339 uses undeclared notation.** Superscripts L/U and the block index *j*
(which is the pulse index in A.3.1). Cures in §4 above.

**S-10. The "rectangle" of the pulse fit is never placed in a space.**
> "a rectangle is rejected only when a mathematical lower bound proves that none of it can
> pass, and every surviving rectangle is split to a fixed resolution." (204)

Nothing in the main text says the rectangle is a set of candidate (onset-shift,
offset-shift) pairs, so "split to a fixed resolution" and the later "122,859 evaluated
rectangles" (588) are unreadable. *Cure:* at 204 insert "— each rectangle being a range of
candidate onset shifts crossed with a range of candidate offset shifts —" after "close
enough to that fit:".

**S-11. Figure numbering.** Figures labelled A3 and A4 sit inside main-text §3 while A1 and
A2 sit in the appendix and are cited from §1 and §2. See RO-6 and RO-7.

**S-12. Figure A2 labels the entry check "admission gate".** See F-4. *Cure:* one word in
the SVG, or at 215 write "the **entry check** (labelled the admission gate in Figure A2)".

**S-13. Symbols *p* and *r* are each reused for unrelated quantities.** See §4. Two renames.

**S-14. §1 108–132 front-loads an apparatus the paper never uses for a result.** See RO-3.

### Nits (9)

**N-1.** "frozen reservation plan" (191) precedes "**Frozen** means fixed and fingerprinted
before collection" by three sentences in the same paragraph. Move the definition sentence to
the head of the paragraph.

**N-2.** "uncommanded-plateau check" (196) precedes "plateau" (204). Cured by RO-1's reorder.

**N-3.** The constant 1.4826 (194) is unexplained. Add four words: "1.4826 × median absolute
deviation (the factor that puts a median absolute deviation on the same scale as a standard
deviation)".

**N-4.** "diagnostic-era" is used at 595 and glossed at 598. Move the gloss into the first
sentence.

**N-5.** File names no longer match labels (`fig4_…` is Figure 2, `fig5_…` is Figure 3), and
`fig3_decision_gates.svg` is unreferenced. Cosmetic, but a reader rebuilding the figure set
from A.4's commands will trip.

**N-6.** "Source map:" is used at 521 and defined at 638 (RO-8).

**N-7.** Decision and registry identifiers (D-078 at 596/777, DS-34 at 901) are unresolvable
from the paper. One clause at 596 — "a project decision that voids these captures' energy
values for claim use" — already exists in apposition; add "(recorded in the project decision
log)" once and drop the bare ids elsewhere.

**N-8.** §5 809 and §5 818 state the transfer limitation nine lines apart (RM-14).

**N-9.** "the fixed time margin around every pulse" (204) never gives its number in the main
text; 200 gives 0.75 s under the name "trace coverage". Say "the fixed 0.75-s time margin".

---

## Summary counts

- First-use ledger: 126 rows — **PASS 91, LATE 20, NEVER 15**.
- Redundancy pairs: **14** (3 of them — RM-8, RM-9, RM-10 — are conventional
  abstract↔conclusion overlap and are recommended to stay).
- Abstract: **246 words**, cap 250 — **pass**; (a) and (b) both satisfied — **abstract passes**.
- Findings: **3 blockers, 14 should-fix, 9 nits.**

Scope: every cure above is sentence-level or a paragraph move. No new experiment, no new
section, no new figure, and no scope growth is proposed (D-174 respected).
