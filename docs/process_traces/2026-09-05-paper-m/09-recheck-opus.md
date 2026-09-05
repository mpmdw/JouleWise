# 09 — Counter-review RE-CHECK (Opus) after fix rounds 2 and 2b

Target: `docs/paper/draft-v2-skeleton.md`, `docs/paper/protocol/prospective-comparison-protocol.md`,
`docs/paper/results-fill-registry.md` at `4be34bc4`. Read-only. Checked against the
FILES, not against reports 06/07.

## Executed evidence (this session)

- `python3 scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise`
  → `COMPARED 43 / MISMATCHES 0`, rc=0.
- `shasum -a 256 docs/process_traces/2026-08-09-prefill-phase-proof/results.json`
  → `e93c1d9c9ccff764cb6c64379cc3551c710e63b38b5314569d89662d2b88d8b1`, byte-identical
  to the digest every DG-135–142 row pins.
- Recomputed from that artifact: 100 bundles / 2 stacks. **1.5B** =
  `Qwen2.5-1.5B-Instruct-4bit`, 50 bundles (10 distinct in `runs_window_a10_20260725`,
  40 distinct in `runs_window_c_20260726`, zero name overlap), `prefill_overlap_sample_count`
  = {2: 37, 3: 13}, `resolvability` = {identifiable 13, not_resolvable 37}.
  **7B** = `Qwen2.5-7B-Instruct-4bit`, 50 distinct bundles all in
  `runs_window_7bfloor_20260729`, `prefill_overlap_sample_count` = {3: 33, 4: 17},
  `resolvability` = {identifiable 50}, `anomalies` = []. Both stacks split
  decode_absolute 10 / decode_abba 40.
- Abstract body (`:11-35`, excluding the trailing HTML comment) = **246 words**, under
  the 250 limit with 4 words of headroom.
- Body (`:7-959`) ≈ 10,501 words; appendix (`:960-1440`) ≈ 8,243 words.

## 1. Status of the 22 prior findings

| # | Status | Evidence |
|---|---|---|
| **B1** abstract opening | **CLOSED** | `:11-14` — "macOS powermetrics is the power sampler used here… A record can span two phases: prompt processing…; token generation…". Grammatical, no premature definite article, both phases enumerated before "each phase" at `:15`. Residue → NF8. |
| **B2** two-arm artifact | **CLOSED (verified)** | See §2. |
| **B3** Figure 3 gap | **CLOSED** | Article figures 1/2/3 at `:179`, `:610`, `:696`; protocol renumbered to Figure P1 at `:406`, `:417`, `:419`. No gap in either document. |
| **B4** undefined "P1" | **PARTIAL** | Conclusion `:924` now "synthetic partial-record enclosure"; caption `:1406` now "Figure A1. Synthetic; no hardware observation." But the SVG's own title text still reads `Figure A1 · SYNTHETIC P1`, and `:1401` glosses it circularly: "The artwork's P1 label identifies this partial-record example" — that says a label exists, not what it means. First-use test still FAILs on the figure surface. Downgraded to should-fix (off the Conclusion). |
| **S1** A.5→A.7 gap | **CLOSED** | Article A.1–A.7 contiguous (`:970`–`:1436`); protocol heading is now plain `## P.10 Historical release-status note` (`:623`), no A-number. No `A.8` reference survives anywhere. |
| **S2** P.8 starts at "3." | **CLOSED** | `protocol:608-614` — lead-in "In addition to the run bundle and `instrument_calibration/` subtree of article Appendix A.2…", items renumbered 1/2. |
| **S3** stale xref | **CLOSED** | `protocol:583` now "described in P.5 above". |
| **S4** close-out artifact | **CLOSED** | `:384-387` defines **authenticated** by expected-SHA-256 agreement only. "close-out artifact" and "required ratio" are gone from the article. |
| **S5** orphan definitions | **CLOSED** | "Gross energy", "Idle-subtracted energy", "A same-cell floor" all absent (grep, 0 hits). |
| **S6** "admissible" cold | **CLOSED** | "admissible half-width" gone; the only survivors are the code identifiers `admissible_interval_empty` (`:1105`) and "exact admissible interval" (`:1121`) inside A.3.3, where the term is local to the estimator. |
| **S7** missing captions | **CLOSED** | Italic element-naming captions now at `:361` (A3), `:546` (A4), `:1300` (A5), `:1351` (A6). All nine figures captioned. |
| **S8** §3/§5 stubs | **CLOSED** | Stubs eliminated. Order is now method (§2 `:173`, §3 `:233`) → results (§4 `:556`, with "Evidence validity" folded in at `:558`) → discussion (§5 `:784`). No method/result alternation remains. Residue → NF1. |
| **S9** un-exercised §4 apparatus | **CLOSED** | Safeguards/`g(n)`/`A_k`/`F_cell` moved out; `:552-554` signposts protocol P.3. |
| **S10** D-078 in record support | **CLOSED** | `:764-766`, verbatim in substance. |
| **S11** length | **REPORT-ONLY, worsened** | Body grew ~510 words (9,990 → 10,501) *despite* the S9 excision, so roughly 1,100 words were added. Still report-only. |
| **N1** "excursion" two dimensions | **CLOSED at the flagged site** | `:623-624` now "the largest **endpoint displacement** in an allowed region, 28.93293456111476 ms". A.3.6 `:1226-1232` keeps "worst excursion" for the same quantity, but there it is the code's retained field name. |
| **N2** A4/A5 out of order | **CLOSED** | First-citation order is A1 `:71`, A2 `:213`, A3 `:352`, A4 `:544`, A5 `:1298`, A6 `:1349`. Introduced NF5. |
| **N3** worst-excursion framing | **CLOSED** | `:624` "equals the retained worst edge excursion". |
| **N4** M₂ asserted before derived | **CLOSED** | `:505-506` derives then asserts. |
| **N5** GPU gloss orphaned | **CLOSED** | Gloss now at first use of the abbreviation, `:25`. |
| **N6** "one configuration" | **CLOSED** | `:33-34` "one Apple computer across retained measurement windows" — and the dropped count is the *right* call, since the 7B arm makes it four windows, not three. |
| **N7** verbatim paste | **CLOSED** | Abstract close `:33-35` and Conclusion close `:926-928` now differ; no duplicated >80-char line remains anywhere in the draft. |

**Tally: 20 CLOSED, 1 PARTIAL (B4), 1 report-only (S11).**

## 2. B2 verified in detail

Every place the record-support failure is stated now carries the model qualifier and
both arms: Abstract `:28-31`, §4 `:675-690`, §4 alignment argument `:739`, §5 `:788-789`,
§7 availability `:896-898`, Conclusion `:918-921`. Counts are exact against the artifact
everywhere: 1.5B 37/13 of 50, 7B 50 of 50 split 33 three-overlap / 17 four-overlap.
Membership is right in both §4 (`:676-677`, `:683-684`) and §7. Nothing claims a causal
model-size effect: `:689-690` and `:791` both disclaim it explicitly.

Note the author did **not** copy my proposed cure sentence, which was wrong — I wrote
"all 50 of its prefill phases reached three overlaps"; the artifact says 33 reached
three and 17 reached four. The draft has the correct split. Good catch by the author.

Registry: DG-135–142 (`results-fill-registry.md:1011-1018`) all resolve. I ran each
locator against the pinned digest — `stack_summaries[stack="7B"].bundle_count`=50,
`.resolvability.identifiable`=50, `.prefill_overlap_sample_count["3"]`=33 / `["4"]`=17,
`.model_names`, and the a10/window-C membership rows (10 and 40, disjoint, summing to
DG-068's 50). Every value matches its row.

Diagnostic conclusion is honest: `:686-687` and `:789` scope identifiability to the
stack rather than asserting a blanket failure, and `:780-782` closes with the correct
caution that duration ÷ typical record width cannot replace the overlap calculation.

## 3. New findings this round

### SHOULD-FIX

**NF1 — self-referential cross-reference introduced by the S8 restructure.**
`:563`: "The retained historical sources **in Section 4** have separate diagnostic
authority." This sentence is itself inside §4 (`:556`). It was correct when "Evidence
validity" was §5. **Cure:** "The retained historical sources **below**…".

**NF2 — the stack-comparison sentence is garbled, and duplicated.**
`:687-689` and, verbatim in substance, `:922-924`: "two records per bundle failed the
count discipline for the 1.5B stack; three passed for its remaining bundles, and three
or four passed for 7B." Records do not fail a discipline; *phases* fail a *minimum*.
"count discipline" is also a fourth synonym for the three-record minimum, undefined,
occurring only in these two sentences (grep: 2 hits) — first-use FAIL in the paper's
most-read closing paragraph. **Cure (both sites):** "Phases with only two overlapping
records failed the three-record minimum; that was 37 of the 50 1.5B phases and none of
the 50 7B phases, which overlapped three or four records each."

**NF3 — the 7B arm is asserted without the number that explains it (why-chain).**
§4 spends `:729-742` building a careful alignment argument for 1.5B, anchored on a real
number ("the 0.121-s phase is only barely longer than the median-width sampling record",
against the 120.9186-ms median width at `:712-713`). The 7B paragraph `:683-690` then
asserts the opposite outcome with no comparable number, so a reader cannot rebuild why
7B always contained a whole middle record. The artifact supplies it:
`stack_summaries[stack="7B"].prefill_duration_s.median` = 0.28151941299438477 s versus
1.5B's 0.13650262355804443 s — 2.3 versus 1.1 median record widths. **Cure:** one
sentence in §4 after `:686` giving the two medians against the 120.9186-ms width, with
a new registry row binding them. (Keep it out of the Abstract — see NF7.)

### NIT

- **NF4** `:897-898` mixes number styles inside one sentence: "**ten** named members …
  and **forty** …" then "**50** members". Make all three numerals or all three words.
- **NF5** The N2 label swap moved labels but not filenames: Figure A4 (`:544`) loads
  `figures/figA5_shared_signs.svg` and Figure A5 (`:1298`) loads
  `figures/figA4_clock_polygon.svg`. Harmless when rendered, confusing in source and in
  any figure-manifest check. Rename the two files (and the two `![…]` targets).
- **NF6** `:828` HTML comment: "fixed by the **Section 2** record definition." The
  sampling-record definition is in §1 — `:652` says so ("Section 1 introduced a sampling
  record"). Stale after the renumber. → "Section 1".
- **NF7** The Abstract is 246 of 250 words. Any further addition breaks the limit; flag
  it so a later editor does not spend the headroom unknowingly.
- **NF8** B1 residue: `:41`, `:46`, `:50` call prefill and decode "parts", and `:52`
  switches to "phases", without one sentence saying the two parts *are* the two phases.
  One clause at `:47` ("…prompt processing and token generation are this paper's two
  **phases**") closes it.
- **NF9** §3 runs `:233-555` (322 lines) under a single subheading (`:244`). Two or three
  more `###` breaks would help a reviewer navigate the paper's longest section.

No regression of any round-1 cure was found: the replay fence still passes 43/43, all
21 DG/DX identifiers cited in the two source maps exist in the registry, and every
`Section N` and `Appendix A.N` reference in both documents resolves to a real heading
(article refs to §§1, 2, 3, 4, 7 all check out; `:1058`'s "Section 9" is explicitly
the *artifact guide's* section, not the article's References).

## Verdict

**LANDABLE at `4be34bc4`.**

All four blockers are discharged. B2 — the only one that changed what the paper says —
is closed to primary evidence, not to a report: both arms of the prefill-phase-proof
artifact are now named with their models, counts, and membership at all six places the
result appears, the counts reproduce exactly from the pinned `results.json` digest, the
eight new registry rows resolve, and the diagnostic conclusion has been rewritten to say
that identifiability depended on the stack rather than that short requests fail in
general — which is what the artifact actually supports. B1 and B3 are clean surface
cures; B4 survives only as a "P1" string baked into one SVG's title with a circular
gloss beside it, which is a should-fix, not a gate. Eleven of eleven should-fixes and
seven of seven nits from round 1 are closed, the restructure did what S8 asked without
breaking a single cross-reference I could test, and the replay fence and all registry
locators still hold. What remains is one dangling self-reference, one garbled sentence
duplicated into the Conclusion, one missing worked number in the 7B paragraph, and six
cosmetic items — none of which changes a claim, and all of which are bench edits of a
few minutes each. My recommendation is to fix NF1–NF3 before submission because NF2 sits
in the Conclusion where the advisor will read it, but none of them should hold the merge.
