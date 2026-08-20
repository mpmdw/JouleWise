# Review lens — `docs/guides/instrument-guide.md` rewrite (working tree, `wtS0`, branch `impl/r2-s0-mint-resolver`)

Read-only. Nothing edited anywhere. Diff: +1078 / −480, final file 1435 lines.
Two dimensions reported separately, each run independently of the writer's own
verification table.

**Verdict in one line:** the rewrite is a large pedagogical improvement and did
not drift a single inherited number — but it introduced **two new factual
errors**, both in §7, both created by the act of glossing something the old
draft left unglossed.

---

## DIMENSION 1 — PEDAGOGY (first-use test)

Method: swept the body (lines 32–1323; front matter and glossary excluded) for
every term of art, criteria word, and verb doing technical work — ~100 terms —
and located each term's first body occurrence mechanically, then checked
whether a gloss or physical construction stands at or before that line. Also
re-derived every worked example's arithmetic from scratch and traced each
mechanism for rebuildability.

**Overall: the discipline holds.** Of ~100 terms swept, all but the items below
are built or glossed at first use, in the body, in order. The overloaded-word
handling is genuinely good — `floor` (§3 line 222), `bracket` (§3 line 226) and
`quantization` (§8 line 976, explicitly cross-referencing §3's different sense)
are each flagged as overloaded *before* they start working. Forward references
are signposted where they occur (line 188 "as section 8 will show", line 643
"sections 5 and 7 explain", line 808 "built properly in section 6", line 903
"described in section 12 step 5", line 995 "section 10 shows how"). I found no
unsignposted forward reference on a load-bearing term other than the one below.

### Blocker

**P-B1 — line 945: `cells` is a load-bearing term used for the first time in
the document, unglossed, in a sense the guide elsewhere calls something else.**

> §7: "…the record that the full 19-member replay reproduced, exactly, every
> capture's anchor bound, its **disposition** …, the number of cells its
> surviving-candidate map came out as, and its b_fiducial value."

`cells`/`cell` appears exactly three times in the whole document (945, 1023 is a
false hit, 1028). Line 945 is the first. §4.4 built the same object at length and
named it a **block** ("A block — a rectangle of the plane — is nothing
mysterious…", line 436). A reader arriving at 945 has never met "cell", and the
one place they *will* next meet it (line 1028, "a 10-member absolute cell") is an
unrelated experiment-design sense. This is also factually wrong — see F-B1 —
so the two findings should be fixed by one edit. Suggested: *"the number of
blocks its search had to evaluate — the §4.4 evaluation count."*

### Should-fix

**P-S1 — §8 lines 1026–1031: the floor-pack arithmetic does not close, and the
guide tells the reader not to check it.**

> "Each successor floor pack carries three condition families — token
> generation, 128-token prompt processing, and 256-token prompt processing —
> and every family gets both arms: a 10-member absolute cell and a 10-block
> ABBA cell. The pack totals 100 science configurations, and the exact member
> inventory is not something to reconstruct from this paragraph…"

Three families × (10 absolute + 10 ABBA blocks × 4 members) = 150, not 100. Both
halves are individually true (see F-OK below — I verified them against the plan),
but the reconciliation is withheld: the p128 family is a **zero-member rider**
whose `ordered_bundle_ids` are byte-identical to the decode absolute cell's, so
only two families cost physical bundles. The hedge sentence reads as a
pre-emptive deflection of an arithmetic contradiction the reader hits in one
step, in a document whose stated standard is "the reader could rebuild each
mechanism from the text alone." One clause fixes it: *"…the 128-token family
rides on the decode members' own prompts rather than costing its own bundles,
so the pack totals 100 science configurations."*

**P-S2 — §4.3 line 368: the score is not rebuildable, because its noise scale
has no source.**

> "For each sample: take the **miss** … and divide it by that sample's noise…"

"That sample's noise" implies a per-sample quantity. There is no such quantity.
The scale is a single robust scatter estimate computed once per capture from the
samples lying outside every pulse margin (`sigma_w = max(1.4826 × MAD, 1e-3)`,
`_baseline_stats`, `joulewise/powermetrics_fiducial.py:704–726`). Since §4.3 is
the section that makes "ruled out" and "survives" mean something, and the
waterline's `max(1.0, …)` floor is stated in units of *noise-widths*, the reader
cannot rebuild the mechanism as written. One clause ("…the machine's ordinary
sample-to-sample scatter, measured once per capture from the quiet stretches
between pulses") closes it.

**P-S3 — §3 lines 184–186: a load-bearing number arrives before anything
justifies it.**

> "Each sample covers roughly 0.112 s, so one sample carries about 1.3 J."

This is the number that motivates the entire project (one misplaced sample >
the whole claimable quantity). At line 185 the reader knows only that samples are
"an *average* over its own sampling interval" (§2 line 133). The 100-ms-requested
/ ~112-ms-observed reconciliation does not arrive until §4.1 line 292. The
parenthetical at 190 ("the sample width and the floor are real") asserts it
rather than sourcing it. Either move a one-clause version of the reconciliation
into §2 or signpost forward explicitly.

**P-S4 — §7 lines 913–918: subject and verb five lines apart, with a colon
nested inside the em-dashes.**

> "…the acceptance is **reissued**: all 19 members of the *replay set* — the
> predecessor generation's complete corpus, kept whole on purpose: it includes
> the two captures the corrected anchor refuses, so every reissue must reproduce
> not only the 17 surviving values but the two refusals *as refusals* — are
> re-authenticated from their raw artifacts under the new code…"

The interpolation is excellent content and belongs; it should be its own
sentence. As written this is the hardest sentence in the document to parse, and
it is a regression against the rest of the rewrite's prose standard.

### Nits

- **P-N1 — line 589 vs 890.** "hash-linked" is the first use of *hash*; the
  document-wide definition ("A hash, throughout this document, is…") lands 300
  lines later at §7. §1.2 line 104's "cryptographic fingerprints" partly covers
  it. Cheapest fix: move the parenthetical gloss to line 104.
- **P-N2 — line 1028.** "cell" in the experiment-design sense (a group of
  members constituting one arm) is never glossed. Given the guide's own
  overloaded-word discipline, and P-B1's *different* sense of the same word,
  `cell` earns the same treatment `floor` and `bracket` get.
- **P-N3 — line 1277.** "pre-flight screen" appears once, in the §12 checklist,
  and is never explained. The reader has "screen" (a threshold a value must
  clear, line 638) but not what this one screens. It is the registered
  `preflight_level_screen_s` = 0.032898 s, which §5 line 800 already quotes as
  "the maximum falls to 0.032898 s" without connecting the two.
- **P-N4 — line 336.** "miss" is used in §4.2 before §4.3 line 367 defines it.
  The immediately preceding numbers (predicted 2 W, recorded 12.18 W) make it
  self-evident. Low priority.
- **P-N5 — lines 307–309.** "they carry it as a height: the fraction of the
  interval the pulse covered" conflates the height (a power reading) with the
  fraction it encodes. The worked example two lines later resolves it.
- **P-N6 — glossary line 1333.** "Acceptance artifact (D-079)" is the only
  internal decision ID in the document; the body never uses it. Against the
  plain-language standard for outward-facing surfaces.

### Worked examples — arithmetic re-derived independently, all correct

| Where | Check | Result |
|---|---|---|
| §3 184–190 | 3 s × 12 W = 36 J; 12 W × 0.112 s = 1.344 J → "about 1.3 J" | ✓, labeled illustrative ("Those wattages are illustrative; the sample width and the floor are real") |
| §4.1 311–315 | 2 + (30/112) × 38 = 12.179 → 12.18 W | ✓, labeled "illustrative power levels" |
| §4.2 333–338 | (+40, +40): overlap vanishes → predicted 2 W vs recorded 12.18 W = 10.18 W miss → "A 10 W miss" | ✓ |
| §4.2 340–344 | (+0.3 ms): 2 + (29.7/112) × 38 = 12.076 → 12.08 W; Δ = 0.102 W = 0.84% → "about 0.1 W, well under one percent" | ✓ |
| §4.3 409–415 | best 38.0 → 5% = 1.9 > 1.0 → limit 39.9 ✓; best 4.0 → 5% = 0.2 < 1.0 → floor wins → limit 5.0 ✓ | ✓, both branches worked, both correct |
| §4.6 512–513 | 115,449/59 = 1,957; 137,535/59 = 2,331 → "about 2,000–2,300 per pulse"; median 122,097/59 = 2,069 → "roughly two thousand" | ✓ |
| §8 1001–1014 | ABAB: A (100.0, 100.4) = 100.2, B (100.2, 100.6) = 100.4 → −0.2 J ✓; ABBA: A (100.0, 100.6) = 100.3, B (100.2, 100.4) = 100.3 → 0.0 J ✓ | ✓, labeled illustrative; "a fifth of the working floor" ✓ (0.2 vs ~1 J) |
| §5 690–693 | 7 ppm × 197 s = 1.379 ms → "roughly 1.4 ms" ✓, against logged 1.442–1.447 ms | ✓ |

Every invented number is labeled illustrative at or adjacent to its use.

### Forcing problems — every mechanism has one

Verified present for: phase-resolved measurement (§1.1), rail enumeration (§2),
the commanded pulse (§4 "Why a commanded pulse"), the low-discrepancy schedule
(§4 — the concrete 1.000 s / 0.100 s aliasing walk-through is the best single
addition in the rewrite), blocks over grids (§4.4 opening), the two-part penalty
(§4.3 "The reason is a specific failure mode"), the waterline's absolute floor
(§4.3), the detection budget (§4.6 "Two reasons, and neither is 'to save
time'"), total-not-partial refusal (§4.6), clock discipline (§4.7), bracketing
(§4.8), the bracket screen (§4.8 "two brackets can agree closely by luck"), the
rate-aware replacement (§5 falsification), frozen constants (§5 "A model with
more free parameters can explain more"), the claim barrier (§6 "A policy
document is not a gate"), two refusal reasons not one (§6), the pin rule (§7),
resolved-not-copied constants (§7 "A trap lives in that table"), ABBA (§8),
freezing (§10 "Why freeze"), identity-pin projection (§10 "naming is not
enough"), path-bound receipts (§10 "A subtlety that cost a night's receipts"),
freshness horizons (§11), the single-use capability (§11).

I found no mechanism asserted without its forcing problem.

---

## DIMENSION 2 — FIDELITY

### Mechanical numeral diff, HEAD → working tree

Extracted every numeral token from both versions and set-differenced them.

**Numerals present in HEAD but absent from the rewrite: NONE.** Not one
inherited project number was dropped, altered, or rounded away.

Every added numeral is accounted for: section cross-references (4.1–4.8),
worked-example values (0.0–0.6, 100.0–100.6, 12.08, 12.18, 29.7, 30, 36, 38,
38.0, 39.9, 4.0, 5.0, 1.9, 1.0, 1.000, 0.100), the block example (250, 500), the
pulse index (23), and four real project values newly *stated* rather than
newly *invented*: 112 / 0.112 (observed cadence), 128 (prompt length),
2,000–2,300 (per-pulse evaluations, derived from the already-present
115,449/137,535), and 1.2 (§ numbering + the ×1.2 headroom). I verified each of
the four.

I also compared the surrounding sentence for every high-risk inherited number
(780 µs, 1.039 ms, −313 µs, 7.243–7.285 ppm, 0.311 ms, 3.09 µs, 5.612 µs,
1.873 µs, 11 of 32, 6 of 17, 25–35 ms, 1.442–1.447 ms, 0.033559, 0.032898,
0.010818, 0.009724, 10.165, 137,189, 1,282,827, 9.2×): **no context drift** —
each number sits in a sentence saying the same thing about the same population,
in the same era framing, as HEAD did.

### Blockers — both introduced by the rewrite

**F-B1 — §7 line 945: the "projection cell count" gloss states the wrong
quantity.**

> "…the number of cells its surviving-candidate map came out as…"

The recorded quantity is `projection_evaluated_cell_count`, incremented in
`_ProjectionWorkBudget.consume_cell()`
(`joulewise/powermetrics_fiducial.py:550`), which is called **at the top of every
stack pop, before the reject / split / accept branch**
(`_accepted_region_projection`, lines 666–667). It therefore counts *every block
the branch-and-bound evaluated, including the ones it rejected* — which is
exactly the §4.4 "**evaluation**" the guide defines at line 449 and exactly what
§4.6's 165,000 budget caps. The *surviving* map is the separate `retained` list
(line 665), which is never serialized. Serialization at
`powermetrics_fiducial.py:1540` and the r6 artifact's own wording
(`derivation_notes.reissue_delta.science_neutrality_evidence`: "every
b_fiducial, anchor bound, refusal disposition and **projection cell count**
reproduced the r4 derivation record exactly") both confirm it.

Consequences: (a) the fact is wrong; (b) it makes §7's recorded quantity look
like a *different* thing from §4.6's budgeted quantity, when they are the same
number, severing the guide's own best cross-section link; (c) it fails the
first-use test (P-B1). HEAD said only "projection cell count" — unglossed but not
wrong. The rewrite's attempt to help introduced the error.

Fix: *"…the number of blocks its search had to evaluate (the §4.4 evaluation
count)…"*

**F-B2 — §7 lines 953–958: the literal-ban regression test's scope is
overstated, in the flattering direction.**

> "So no such literal exists anywhere in **the code that issues acceptance
> artifacts**: an automated **regression test** … forbids both digit strings from
> appearing there, exempting only the acceptance registry itself…"

The guard is `tests/test_mint_policy_resolver_guard.py` (the only such guard in
the tree — I searched for any other `assertNotIn` on these literals; there is
none). It scans exactly three files, enumerated inline:

```
"joulewise/floor_mint_estimator.py",
"joulewise/detection_floor.py",
"scripts/mint_floor_artifact_generalized.py",
```

These are the **floor-mint lane**, not the acceptance-issuing code. Two errors:

1. **Scope.** HEAD said "no such literal exists anywhere in the **mint lane**" —
   correct. The rewrite widened a checkable claim to code the guard does not
   cover.
2. **Mechanism.** "exempting only the acceptance registry itself" describes an
   exemption list. The test is an *inclusion* list of three paths; the registry
   (`_D102_N19_DERIVATION` / `_D102_N17_DERIVATION` in
   `joulewise/calibration_bracketing.py:193–215`) is simply not scanned, not
   deliberately exempted. `tests/test_d117_v3_family.py:26` and
   `tests/test_floor_extraction.py:2583` both carry `0.010818` literals today
   and pass, which is the direct demonstration that the ban is not repo-wide.

Fix: restore "anywhere in the mint lane", and say the guard names the three
files it covers rather than exempting one.

### Should-fix

**F-S1 — §5 line 790: the "43" gloss asserts a provenance the artifacts do not
establish, and collides with a second population in the same artifact.**

> "…of the 43 replayed corpus-lineage captures — **the wider family of captures
> the corpus was drawn from** — 41 need exactly zero slack."

The number 43 is correct and sourced
(`03-cold-science-review.md:68`, "41 of 43 bundles need exactly zero slack";
r6 `derivation_notes.exclusion_accounting.surviving_pre_discipline_members`,
"41 of 43 replayed bundles need exactly zero model slack"). The **gloss** is the
new material and it is not supported:

- The corpus's actual selection pool is the prior observation set —
  `prior_observation_set.observations` n = **38** at ledger cutoff 76
  (`backfill_candidate.candidate_inventory`: 30 valid + 6 ordinary-invalid + 2
  systematic-invalid), under the rule "valid protocol-v3 captures before the
  excluded window-B judged pair, exact identity epoch." 43 is not that pool.
- The same r6 artifact reports a *different* replayed population:
  `residual_margin_distribution.all_bounded_replayed_members` n = **45**, plus
  `members_that_do_bind` listing **3**. A reader who follows the guide's gloss to
  the artifact finds 45 and 45+3, not 43, and has been told 43 is "the family the
  corpus was drawn from."

The three populations are genuinely distinct (43 = slack-analysis replay set;
45 = bounded replayed members for the residual-margin distribution; 38 =
selection pool), and slack ≠ residual-margin binding, so nothing is
*internally* contradictory — but the gloss invites exactly the conflation the
magistrate flagged. Recommend the paper's neutral wording, which makes no
provenance claim: *"of the 43 captures in this lineage that were replayed"*
(`docs/paper/draft-v1.md:80`).

**F-S2 — §4.6 line 512: the exact survivor range is stated with no population or
era label, 72 lines before the sentence that defines it.**

> line 512: "…a whole healthy capture lands between 115,449 and 137,535…"
> line 583: "…the 17 corpus survivors demand between 115,449 and 137,535
> evaluations, median 122,097…"

HEAD said "roughly 115,000 to 138,000" — rounded, and therefore making no
population claim. The rewrite promoted the figures to exact and attached them to
"a whole healthy capture," i.e. a universal property. They are the anchor-v3
17-survivor range specifically (`corpus_survivor_cell_demand`
min 115449 / median 122097 / max 137535). The reader then meets, 54 lines later,
a **40-capture old-anchor** sweep with max 137,189 and will try to reconcile two
ranges they were told were generic. Fix: label at first use, e.g. "…and a whole
healthy capture in the current corpus lands between…", or restore the rounded
form at 512 and keep the exact figures only at 583.

### Named verify items — dispositions

**(i) "projection cell count" gloss — FAILS. See F-B1.** Checked against
`_accepted_region_projection` and `evaluated_cell_count` as instructed; the
gloss names `retained`, the artifact records the evaluated count. Writer's
self-flag was correct.

**(ii) the "43 replayed corpus-lineage captures" gloss — PARTIALLY FAILS. See
F-S1.** Number correct; gloss conflates the replay set with the selection pool
and collides with the artifact's 45 / 45+3 populations.

**(iii) §4.6's three evaluation-demand populations — PASSES with one labeling
gap (F-S2).**

| Population | Guide | Era/population label | Verified against |
|---|---|---|---|
| 40-capture old-anchor sweep, max 137,189 | 566–568 | "(under the anchor estimator then in force)" — present, though it attaches grammatically to the maximum rather than to the 40/34/6 counts | `powermetrics_fiducial.py:74–87`: "n=34 full 59-pulse convergences, min 112,205, median 122,044, p95 135,513, max 137,189"; 165,000 "clears the observed maximum by 27,811 cells (20.3%) — more than the entire observed 24,984-cell spread" ✓ (guide: "about 20% above that maximum, with the margin exceeding the entire observed spread" ✓) |
| 17 new-anchor survivors, 115,449–137,535, median 122,097 | 583–584 | "the claim-bearing population's own numbers: the 17 corpus survivors" — correct and explicit | r6 `corpus_survivor_cell_demand` {n 17, min 115449, median 122097, p95 137535, max 137535} ✓; 137,535 × 1.2 = 165,042 → "that maximum plus about 20%" ✓, matching `budget_ruling` "plus 20% headroom" |
| the v3-resolvable set the 1,282,827 outlier is compared against | 590–594 | "9.2× the next highest demand of any capture **the current anchor method can resolve at all** (a set wider than the 17 survivors)" — correct and explicitly distinguished | r6 `budget_probe_status`: "demands 1,282,827 cells (9.21x the next highest)" ✓. Internal consistency check: 1,282,827 / 9.21 ≈ 139,300 > 137,535, which independently confirms the comparator set *is* wider than the 17 survivors ✓ |

No sentence invites conflating the three; the parenthetical at 594 does the
distinguishing work explicitly. The one gap is F-S2 (line 512's unlabeled
pre-statement of the second population's figures). Also correct: "A ninefold
increase would make a wall-clock deadline the real limit" — rejected Option A was
1,550,000 = 9.4× (`budget_ruling`), and the deadline is real
(`DETECTION_PROJECTION_WALL_BUDGET_S = 120.0`).

**(iv) 100-ms-requested / ~112-ms-observed — PASSES.** The guide states it as
request-vs-observed in both places it matters:
- line 263: "with the sampler **asked for** a 100 ms cadence"
- line 292: "in practice each interval covers about 112 ms (**the 100 ms cadence
  is a request, not a guarantee**)"

Sources: `configs/calibration/powermetrics_fiducial/protocol_v2.json`
`sampling_interval_ms: 100` and `protocol_v3.json` likewise;
`SAMPLING_INTERVAL_MS = 100` in the estimator; `docs/paper/draft-v1.md:274` "The
power sampler's approximately 112 ms cadence". No claim anywhere that 112 ms is
configured or that 100 ms is achieved.

**(v) three-family floor-pack structure — PASSES on fidelity, see P-S1 on
pedagogy.** Verified against `configs/campaigns/d117_floor_qwen25_1p5b_v3/`:
- `calibration_plan.json` `floor_cells` = 6 cells over **3** `condition_family_id`s
  (`df-ph-decode`, `df-ph-prefill-p128-qwen25-1p5b`,
  `df-ph-prefill-p256-qwen25-1p5b`) ✓ "three condition families — token
  generation, 128-token prompt processing, and 256-token prompt processing" ✓
- every family has one `kind: absolute` cell with `ordered_bundle_ids` of
  length **10** and one `kind: comparative_abba` cell with `ordered_blocks` of
  length **10** ✓ "a 10-member absolute cell and a 10-block ABBA cell" ✓
- `order_manifest.json` `planned_n_bundles` = **100**, `executed_order` length
  **100**, 6 subcampaigns ✓ "The pack totals 100 science configurations" ✓
- the reconciliation the guide omits: the p128 absolute cell's
  `ordered_bundle_ids` are **byte-identical** to the decode absolute cell's
  (verified by equality test), and `PLAN_ID` is
  `plan-d117-floor-qwen25-1p5b-decode-p128-**prefill-rider**-v3` — the p128
  family rides the decode bundles. This is why 3 × 50 ≠ 100.
- "the pack's own generator re-derives and attests it on every check" ✓
  (`generate_configs.py --check`).

### Era labels — all superseded-era values carry them

| Line | Value | Label |
|---|---|---|
| 503 | b_fiducial 0.0232–0.0329 s | "the 17-member corpus that grounds **the current** acceptance artifact" ✓ |
| 567 | max demand 137,189 | "(under the anchor estimator **then in force**)" ✓ |
| 571 | b_fiducial 0.0309 s | "under the anchor estimator **then in force**. (That number moved when the estimator was replaced the next day — section 5.)" ✓ |
| 642–644 | 9.724 ms provenance | "derived under **the same calibration generation** — sections 5 and 7 explain … why it changed" ✓ |
| 697–701 | six-capture diagnostic | framed throughout as the old censored-intersection method ✓ |
| 799 | b_fiducial 0.033559 s | "the *corpus maximum* **under the old model**" ✓ |
| 800–802 | 0.032898 s / 0.010818 → 0.009724 s | stated as an explicit old→new tightening ✓ |
| 951–952 | 0.010818 vs 0.009724 | "**under the 19-member generations** … **under the 17-member ones**" ✓ |
| 808–818 | the whole "replay is not validity" passage | era/claim-eligibility distinction is the passage's subject ✓ |

Only gap: F-S2 (line 512, current-era value, no label at all).

### Process-machinery leakage — clean

Scanned the full document for council / seat / ruling / magistrate / lieutenant /
cold / classifier / adjudicat* / Codex / Sol / Opus / Fable / `D-\d{2,3}` /
lead / refuter / consult. **One hit**: glossary line 1333, "Acceptance artifact
(D-079)" — an internal decision ID the body never uses (P-N6). Line 723's "the
disciplined capture the science review examined" is the only other trace of
process and it carried over unchanged from HEAD; it reads as ordinary scientific
review rather than project machinery, so I would leave it. §13 discusses
verification culture in fully generic terms (independent reviewers, re-audits,
fresh-eyes reversals) with no seat names or mechanisms — correct handling.

### Verified correct (no action) — the substantive fidelity checks that passed

- r6 file hash begins `0227bca3` ✓ (`shasum -a 256` on the artifact).
- Corpus n = 17; b_fiducial min 0.02317490442656863 → "0.0232 s", max
  0.03289849371536248 → "0.0329 s" ✓.
- Screens: `bracket_screen_s` 0.009724, `preflight_level_screen_s` 0.032898…,
  `maximum_budgetable_drift_s` 0.010164834757777545 → "10.165 ms" ✓; predecessor
  `bracket_screen_s` 0.010818 ✓ (`calibration_bracketing.py:193–215`,
  per-generation tables — which is itself the "resolved, never copied" mechanism
  §7 describes).
- "The 9.724 ms comes from the historical range of 17 bounds" ✓
  (`range_s` = 0.00972358928879385).
- Allowance = full bracket disagreement, floored at the screen ✓
  (`allowance_rule`: `max(observed_drift_s, bracket_screen_s)`).
- Anchor ceiling 5 ms ✓ (`MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S = 0.005`).
- Frozen anchor constants: 250 µs departure ✓ (`MAX_AFFINE_CLOCK_RESIDUAL_S =
  0.000250`), ±50 ppm **refuses rather than clips** ✓
  (`MAX_CLOCK_RATE_DEVIATION_PPM = 50.0`, docstring at line 835), padding raised
  1 ns → 1 µs ✓ (`NUMERIC_PADDING_S = 1e-6`; r6 `numeric_pricing`).
- Waterline formula `best + max(1.0, 5% of best)` ✓ exactly
  (`tolerance = max(1.0, 0.05 * best_loss)`; `loss_limit = best_loss + tolerance`).
- Significance gate "below **half** the flat explanation's score" ✓ exactly
  (`if not best_loss < 0.5 * flat_loss`).
- Accept-at-0.1 ms ✓ (`REGION_COVERAGE_RESOLUTION_S = 0.0001`, applied as
  `max(onset_width, offset_width) <=` — i.e. both sides, as the guide says);
  reject-if-lower-bound-above-limit ✓; bisect-the-longer-side ✓; "every point …
  either provably ruled out or counted in" ✓ (matches the function docstring).
- b_fiducial composition — widen by command-stamp uncertainty, collapse to
  worst-edge scalar, add the anchor ✓ (`b_fiducial_s = max(worst_per_edge) +
  trace_anchor_bound_s`, line 1043; stamp widening at 872–875).
- Protocol v3: 59 pulses, 3 warmup, 4096 half-precision, 100 ms requested ✓.
- §5 diagnostic numbers verbatim from `03-cold-science-review.md` Q2/Q3:
  5.612 µs, 1.873 µs, [−1.1, +5.2] vs [−16.04, −15.99] ppm ("disjoint by more
  than 15 ppm" ✓ "disjoint by ≥15 ppm"), −3.18 ms, −9.2 / −2.27 ppm, 11 of 32,
  +0.311 ms against 25–35 ms bounds, custody pin postdating both ✓.
- 748 stored `.2` bundles / 745 recording a resolved anchor ✓
  (`09-r1-debate-opus.md:195, 297` full-tree `os.walk`).
- §6 claim barrier, verified structurally: one shared test
  `capture_pipeline_refusal` (`uncertainty_evidence.py:1301`) imported by exactly
  three claim-side consumers — `analysis_engine/inputs.py:82`,
  `floor_extraction.py:120`, `whole_window.py:68` ✓ ("the analysis, the floor
  extraction, and the whole-window check"); positive presentation from
  `CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})` ✓ ("a closed
  set — an explicitly enumerated list, **one member long today**" — exact);
  absent vs superseded kept distinct ✓.
- §6 label/method binding: one canonical table `SCHEMA_FOR_ANCHOR_METHOD`
  (`uncertainty_evidence.py:29–33`) ✓; disagreement refuses outright
  (`cli.py:1255`) ✓; method is the dispatch key, not the label ✓
  (`resolve_anchor_deriver` gates `resolve_clock_evidence_deriver`).
- §7 generation table — every row verified: acceptance_ids are
  `d079_calibration_acceptance_v2_n19` and `…_v2_n19_r2` ✓ (matching the guide's
  `…_v2_n19` / `…_v2_n19_r2` labels, which do not match the *filenames* — the
  guide is right and the filenames are the odd ones); pin counts r4 = 1
  (`uncertainty_evidence.py`), r5 = 3 (`powermetrics_fiducial.py`,
  `uncertainty_evidence.py`, `adapters/powermetrics.py`), r6 = 2
  (`uncertainty_evidence.py`, `reduce.py`) ✓ exactly as tabulated. Table is
  byte-identical to HEAD.
- §11 freshness horizons: 20 minutes volatile / 6 hours procedural ✓
  (`arm_readiness_evidence_t0.py:49–50`), monotonic-clock-based ✓.
- §10 "eleven evidence documents per pack, thirty-three in all" ✓ — each v3 pack's
  `arm_readiness.evidence/` holds 22 files = 11 JSON + 11 `.sha256`; 3 v3 packs
  (1.5B floor, 7B floor, contrast) × 11 = 33 ✓.
- §8 attribution-limited framing: noise-limited ~0.3 J, working floor ~1 J,
  effective bar ~5 J with pre-registered margins ✓ (unchanged from HEAD, matches
  the ratified attribution-limit position).

---

## Recommended disposition

Two edits are required before this ships: **F-B1** (§7 line 945 — replace the
cell gloss with the §4.4 evaluation count, which also clears P-B1) and **F-B2**
(§7 lines 954–956 — restore "the mint lane" and describe the guard as naming
three files). Both are single-clause fixes in the same paragraph pair.

Four should-fixes are worth taking in the same pass because each is one clause:
P-S1 (the p128 rider clause), P-S2 (where the noise scale comes from), F-S1
(drop the "43" provenance gloss for the paper's neutral wording), F-S2 (label
line 512's population). P-S3 and P-S4 are prose moves.

Everything else in the rewrite is an improvement I would keep verbatim — in
particular the §4.1→4.5 single-pulse walkthrough, the aliasing walk-through that
justifies the low-discrepancy schedule, the §4.4 "converged means the map is
finished" reframing (which does exactly what it was rebuilt to do), the two
worked waterline branches, and the ABBA-vs-ABAB numerical demonstration. The
rewrite's one systematic risk is visible in both blockers: **the errors are in
the glosses the rewrite added to previously-unglossed terms of art**, i.e. in
exactly the places where prose had to assert something the old draft left
implicit. If any further glossing passes are planned, that is the class to
re-check.
