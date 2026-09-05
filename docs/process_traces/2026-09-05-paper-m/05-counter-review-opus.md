# 05 — Counter-review (Opus, contract + pedagogy lens)

Target: `docs/paper/draft-v2-skeleton.md` and `docs/paper/protocol/prospective-comparison-protocol.md`
at `d243c776` in `/Users/edr/code/JouleWise-wt-paper-m`. Read-only. Lens is
deliberately *not* closure of the 30 refuter findings (another reviewer owns that);
it is the binding writing standard, evidence contract, and post-cut structure.

## Executed evidence (this session)

- `python3 scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise`
  → `COMPARED 43 / MISMATCHES 0`, rc=0.
- `docs/paper/round7/excursion-decomposition.json`: onset `count=59, count_positive=59`;
  offset `count=59, count_negative=49, count_positive=8, count_zero=2`;
  `median_ms` +13.0 / −5.5; `b_fiducial_s=0.030067931757111657`,
  `b_anchor_s=0.0011349971959968978`, `max_worst_edge_excursion_ms=28.932935`,
  `projection_evaluated_cell_count=122859`. All match the draft.
- `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`: 1.5B
  `bundle_count=50`, `resolvability={identifiable:13, not_resolvable_sample_count:37}`,
  `prefill_overlap_sample_count={"2":37,"3":13}`; members = 10 × `runs_window_a10_20260725`
  + 40 × `runs_window_c_20260726`. **Also present: a 7B stack, 50 bundles from
  `runs_window_7bfloor_20260729`, `identifiable=50`.**
- `docs/paper/round7/dg071-dg075-statistics.md`: 100 of 405 nonzero tiling gaps, largest
  0.0000004 s — matches draft line 750–752.
- Live code: `absolute_false_effect_floor([0.]*5, half_widths=[0.5]*5)` → 1.6656,
  guarded 2.4984; comparative → 1.7656 / 2.6484; `[8..12]` → 4.808173041811203;
  `[0..4]` → 6.808173041811203. All SYN-02/SYN-03 figures reproduce.
- Recomputed by hand and confirmed: Fig. 1 (1.20/1.80/1.50/0.30 J, 3.00 J total);
  §1 enclosure (9 J, [8.8, 9.2], [8, 10]); §4 five-energy example; SYN-05 four corners
  (22.007438 / 45.014875 / 1.000000 / 24.007438); SYN-02 composition (2.8984 / 3.0484);
  the full SYN-01 block fixture (d₁±, q₁, ℓ₁, d₂±, q₂, ℓ₂, M₁=103.06152807459057,
  M₂=102.95961680584864, p=7.322962010973595e-13); all eight Table 4 rows spot-checked
  (rows 1 and 6 to full displayed precision); R_cm = 8.8304376431/2.4305766103 = 3.6330628732;
  §2 bracket constants (t·s_b·√2 = 10.164834757777545 ms; b = 29 + max(4, 9.724) = 38.724 ms);
  §2 residual subtraction (0.0289329345611147592 s) and Fig. 2 sum (30.067931757111657 ms);
  A.3.9 Huber example (ρ=1.7854875), Λ = 1.05 × 13724.280240837228 = 14410.494252879089,
  half-flat-loss 239169.235309275; §6 r03/r08 overlap durations, all nine table rows.

**No arithmetic error found.** Every worked example in the article recomputes.
The findings below are pedagogy, scope, and structure.

---

## BLOCKER

### B1 — The Abstract's first sentence is not parseable, and uses two undefined terms

`docs/paper/draft-v2-skeleton.md:11-13`

> "The sampler averages power while input reading changes to emitting tokens,
> pieces of generated text. JouleWise assigns energy to each part as average
> power times overlap duration"

Three defects in the paper's most-read sentence. (a) "while input reading changes to
emitting tokens" is ungrammatical and the reader cannot recover the intended
mechanism — that *one* sampler record straddles the moment prefill becomes decode.
(b) "**The** sampler" takes a definite article before any sampler exists; `powermetrics`
is not introduced until line 35. (c) "each part" has no antecedent — the two parts
were never enumerated. Compounding: line 19 then says "physical **phase** energy",
so the Abstract uses *part* and *phase* for the same object, and *phase* is never
built. First-use test: FAIL on "sampler", "part/phase".

**Cure.** Rewrite as, e.g.: "macOS's `powermetrics` sampler reports one average power
per fixed interval. A single such interval can span the moment a request stops reading
its prompt and starts emitting output tokens, so it reports one number for two
different kinds of work. JouleWise splits that record's energy between the two —
prompt processing and token generation — as average power times the duration each
gets." Then use "phase" consistently for the rest of the Abstract.

### B2 — The 37/50 headline is one arm of a two-arm artifact; the other arm passed 50/50 and is never disclosed

`docs/paper/draft-v2-skeleton.md:23-24` (Abstract), `:791-797` (§6), `:943-944` (Conclusion)

> Abstract: "Earlier short requests had 37 of 50 measured parts crossed by two power
> readings and 13 by three"

The supplying artifact `2026-08-09-prefill-phase-proof/results.json` contains **100**
bundles in two stacks. The 1.5B stack gives 37/13 (verified). The 7B stack — 50 bundles
from `runs_window_7bfloor_20260729`, same July-2026 era — has `identifiable: 50`,
i.e. **zero** record-support failures. The article never mentions it.

Two consequences. (i) The Abstract states the result for "earlier short requests" with
no model qualifier, so an abstract-only reader takes it as a property of short requests
in general; §6 line 791 does scope it to the 1.5B configuration, but the Abstract and
Conclusion do not. (ii) Reporting the failing half of a two-arm artifact without naming
the passing half is exactly the selective-reporting pattern a JouleSort-lineage advisor
is trained to catch, and the omission is discoverable in one `jq` call on a cited file.

**Cure.** (1) Add the qualifier to the Abstract and Conclusion: "Earlier short requests
from a 1.5-billion-parameter configuration had 37 of 50…". (2) Add one sentence to §6
after line 797 disclosing the 7B arm: all 50 of its prefill phases reached three
overlaps, because a larger model's prefill spans several record widths — which is the
same alignment/width argument the section already makes, now with its positive control
present. This *strengthens* §6; it costs two sentences.

### B3 — The article's figure numbering skips Figure 3

`docs/paper/draft-v2-skeleton.md:167` (Fig. 1), `:266` (Fig. 2), `:723` (Fig. 4).
There is no Figure 3 anywhere in the article; `fig3_decision_gates.svg` is now cited
only from `protocol/prospective-comparison-protocol.md:346`. A submitted paper that
jumps 1 → 2 → 4 reads as a document cut in a hurry, and it is the first thing a
reviewer notices.

**Cure.** Renumber the phase–record overlap diagram to Figure 3 in the article
(caption at `:719`, `:723`, `:725`); let the protocol number its own figure
independently (e.g. "Figure P1"), since it is a standalone companion.

### B4 — "P1" is undefined internal shorthand, and it appears in the Conclusion

`docs/paper/draft-v2-skeleton.md:944`, `:1387`

> "The synthetic P1 enclosure and two-block fixture make the distinct calculations
> explicit and reproducible."
> "Figure A1. SYNTHETIC P1; no hardware observation."

"P1" occurs exactly twice in the whole draft and is defined nowhere. It is a registry-era
label (`[FILL:PE-01]`). The Conclusion is one of the three places the advisor is
guaranteed to read, and the standing plain-language instruction is explicit that
internal shorthand does not appear on advisor-facing surfaces.

**Cure.** Delete both occurrences. Line 944 → "The synthetic partial-record enclosure
and the two-block fixture…"; line 1387 → "Figure A1. Synthetic; no hardware observation."

---

## SHOULD-FIX

### S1 — Appendix numbering gap: A.5 → A.7, with A.6 orphaned inside the protocol

Article headings run A.1, A.2, A.3, A.4, A.5, **A.7**, A.8. The missing A.6 now lives at
`protocol/prospective-comparison-protocol.md:547` as `### A.6 Release status`, nested
under `## P.10 Historical release-status note` — an article-numbered heading inside a
P-numbered document. Nothing in the article references A.6, so the gap is silent but
visible. **Cure:** renumber article A.7→A.6, A.8→A.7; retitle the protocol heading
"Release status" with no A-number (P.10 already names it).

### S2 — Protocol §P.8 is a numbered list that starts at "3."

`protocol/prospective-comparison-protocol.md:538-539`. Items 1 and 2 stayed behind in
article A.2 (`draft-v2-skeleton.md:998-999`). As it stands P.8 opens mid-enumeration.
**Cure:** renumber 3/4 → 1/2 and open with "In addition to the run bundle and
`instrument_calibration/` subtree of article Appendix A.2, a complete comparison archive
would need:".

### S3 — Stale cross-reference in the protocol

`protocol/prospective-comparison-protocol.md:481-482`: "It does not close the generic
floor consumer's uncertainty-width gap **described in Section 7**." Per the protocol's own
convention (line 8), "Section N" means the article; article §7 is "Discussion and
limitations" and describes transfer, single-host, and gain limits — not a width gap. The
width gap is described in this same document at P.5 (lines 455–461).
**Cure:** "described in P.5 above".

### S4 — "close-out artifact … every required ratio": campaign machinery left in the article

`draft-v2-skeleton.md:457-461`. "authenticated" — a term §4 needs at line 470 — is defined
via "the evidence, plan, and post-campaign **close-out artifact**, which checks every
**required ratio**". Neither exists for this paper: the twelve-ratio census moved to
protocol P.1, and no campaign ran, so no close-out artifact will issue. "required ratio"
is undefined in the article (first-use FAIL) and "close-out artifact" is used once and
never again. **Cure:** define authentication without the campaign object — "**authenticated**
means each named input carries its expected SHA-256 fingerprint and the inputs its record
names agree with the files on disk" — and move the close-out/ratio-census sentence to
protocol P.1, which already owns the twelve ratios.

### S5 — Orphan definitions that no later sentence uses

Three bolded terms are defined and never used again anywhere in the draft:
`:211` "**Gross energy**", `:212` "**Idle-subtracted energy**", `:624` "**A same-cell
floor**". They are dead weight in a paper that has no campaign to apply energy families
or same-cell matching to. **Cure:** delete all three from the article; the energy-family
machinery belongs with the campaign in the protocol. (Checked: "energy family",
"reference-trajectory excursion", "issued repeatability bound" and "entry check" *are*
re-used at `:641-651` / `:353`; leave those.)

### S6 — "admissible" enters cold at its first use

`:673`: "five zero-valued block differences, each with a 0.5-J **admissible half-width**."
This is the first occurrence of "admissible" in the article; everywhere else the paper
says "allowed", "permitted", or "registered". A reader meets a fourth synonym in the
one place it carries the load. **Cure:** either gloss at first use ("admissible half-width
— half the width of that energy's allowed movement interval") or use "allowed half-width"
for consistency with §4's own vocabulary.

### S7 — Four figures carry no caption, while five do

Figures 1, 2, 4, A1, A2 have full element-naming captions. Figures A3 (`:439`), A5
(`:617`) have **only** markdown alt text; A4 (`:1317`) and A6 (`:1364`) have three-sentence
commentary but no formal caption. I inspected the SVGs: both A3 and A5 are dense
self-labelling flow diagrams whose in-figure text names every element (A3 even prints
the corner→bound mapping that line 433's "in the displayed order" relies on), so this is
a presentation defect, not a substance one — but a reviewer reading captions first gets
nothing from four of nine figures, and the inconsistency reads as unfinished.
**Cure:** add a caption to each of A3, A4, A5, A6 in the style already used for A1/A2.

### S8 — §3 and §5 are stubs; method and results interleave

`:305-311` (§3 "Scope of the reported evidence") is 7 lines: one signpost paragraph
pointing at the protocol. `:683-691` (§5 "Evidence validity") is 9 lines. They sit
between §2 (2,824 words) and §4 (2,624 words) and §6 (1,125 words). The reading order is
also method+result (§2) → scope (§3) → method (§4) → validity (§5) → result (§6).
**Cure:** fold §3 into the end of §1 (it is a scope statement) and §5 into §2 or §6 as a
subsection; promote §2's "Historical current-method edge result" (`:244`) and §6 into a
single Results section so methods and results do not alternate.

### S9 — §4 is 2,600 words of apparatus the paper never applies to real data

The cut removed campaign-presuming *sections* but left the whole floor construction —
A/B/B/A blocks, `g(n)`, the whole-window allowance `A_k`, `F_abs`/`F_cmp`/`F_cell`,
and the `R_cm` shared/local replay — in the article. It is exercised only on synthetic
fixtures. That is defensible for a methods paper, and I am not calling it a defect; but
a metrology-rigorous reader will ask why the un-exercised half of the method sits in the
article while the un-exercised campaign sits in the protocol. **Cure (optional but
recommended):** move "Adding publication safeguards after the ratio" (`:619-681`,
`g(n)`, `A_k`, `F_cell`) into the protocol next to P.3's claim gates, keeping in the
article only the clip/timing-envelope/`R`/`R_cm` machinery the synthetic diagnostics
actually use. This shortens the body by ~600 words and makes §4 exactly "what this paper
computes".

### S10 — D-078 is invoked for §2 but never for §6

`:246-248` correctly discloses that D-078 "voids [these captures'] energy values for
energy-claim use". §6 uses corpora from the same era (`runs_window_a10_20260725`,
`runs_window_c_20260726`) and never mentions D-078. A reader who has met D-078 in §2
will ask whether §6 is voided too. It is not — record support is a count over record
timestamps, not an energy value — but the article should say so.
**Cure:** one sentence in §6: "D-078 voids these captures' *energy* values for claim use;
record support is a count of overlapping record intervals, uses no energy value, and is
reported here as a descriptive property of the retained population."

### S11 — Length

Body (title through references) 950 lines / ~9,990 words, of which references 648;
appendix 442 lines / ~7,995 words. ~18,000 words total, ~9,340 of running body prose.
That is long for an undergraduate capstone submission even allowing that A.3
(7,096 words) is a deliberately replicable algorithm specification. Report only —
combined with S8/S9 the body would land near 8,500.

---

## NIT

- **N1** `:217` vs `:279` — "excursion" is a joule quantity at 217
  ("reference-trajectory excursion") and a millisecond quantity at 279 ("the largest
  excursion of an allowed-region endpoint"). One word, two physical dimensions.
  Rename the timing one "endpoint displacement".
- **N2** Appendix figures are first cited out of order: A1 (`:65`), A2 (`:201`),
  A3 (`:432`), **A5** (`:617`), **A4** (`:1317`), A6 (`:1364`). Swap A4/A5 labels.
- **N3** `:280` presents 28.93293456111476 ms as "the largest excursion of an
  allowed-region endpoint", while A.3.6 `:1251` warns that this subtracted difference
  "is not itself the value the code retains for the worst edge excursion". The two agree
  numerically (`max_worst_edge_excursion_ms=28.932935`), so this is framing only —
  but the caption should say "equal to the retained worst edge excursion".
- **N4** `:573-574` states M₂ = 102.95961680584864 J before `:577-579` derives it.
  Move the assertion after the derivation.
- **N5** `:18-19` "A GPU is a graphics processor; fitted onsets and offsets are…"
  bundles an orphan abbreviation gloss with an unrelated definition; the abbreviation
  is not used until line 22. Fold the gloss into line 22's first use.
- **N6** `:27` "confined to one Apple computer, software configuration, and macOS
  processor-power records" compresses three distinct measurement windows
  (`a_20260722`, `a10_20260725`, `c_20260726`). One machine, yes; one configuration
  is a stretch. Say "one Apple computer and three retained measurement windows".
- **N7** `:22` and `:937` are the same sentence pasted verbatim, both as single
  unwrapped ~50-word lines in a file otherwise wrapped at ~72 columns. Cosmetic, but
  it advertises the paste.

---

## Verdict

**NOT LANDABLE at `d243c776`; LANDABLE after B1–B4.**

The evidence contract is in good shape and I could not break it: every load-bearing
number I re-derived — the 59/59 and 49/59 edge counts, the two medians, `b_fiducial`,
the 122,859 cell count, the 37/50/13 record-support counts, DG-071/075's record-width
and spacing statistics, both floor-composition examples, the four SYN-05 corners, all
eight SYN-01 sign rows and `R_cm` — reproduces from the named primary artifacts or from
live code, and the replay fence passes 43/43 clean. No sentence in the article claims the
comparison campaign ran, and the protocol is honestly and prominently labelled
PROSPECTIVE / UNPERFORMED; it does not stand alone but correctly declares its dependence
on the article rather than pretending otherwise. What blocks the draft is not soundness
but three cheap surface defects that a metrology-rigorous advisor will hit in the first
ninety seconds — an ungrammatical opening sentence, a figure-number gap, and undefined
shorthand in the Conclusion — plus one substantive scope defect: the article reports the
failing arm of a two-arm artifact whose other arm resolved 50 of 50 and is never
mentioned, and the Abstract states that failure without the model qualifier the body
supplies. B2 is the only finding that changes what the paper says; the other three are
sub-hour edits. Fix those four and this lands.
