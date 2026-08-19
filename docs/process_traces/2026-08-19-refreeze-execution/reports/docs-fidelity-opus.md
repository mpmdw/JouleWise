# FIDELITY LENS — uncommitted docs enrichment (wtDOCS)

Scope: `git diff` in
`/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtDOCS`
— `docs/guides/instrument-guide.md` (+345/−40 region) and
`docs/paper/draft-v1.md` (+28). Read-only; no edits made anywhere.
Every number below was re-derived from primary artifacts in the same tree.

**Headline.** The diff is unusually accurate. I checked ~70 distinct
quantitative claims; the overwhelming majority match the artifacts to the
digit, including every hard number the writer self-flagged. Two blockers,
both in the guide, both in the same paragraph-pair of §5. The paper's
numbers are clean; its issues are framing and one scope overclaim.

---

## BLOCKERS

### B1 — The guide names the wrong pair of clocks for the anchor (mechanism the code contradicts, and the paper gets it right)

Guide §5, three places:

> "The sampler prints rows **labelled in its own timebase**; the workload
> stamps its pulse commands in the system's wall-clock time."

> "The sampler prints a whole-second label **in its own timebase** each time
> its clock rolls over…"

> Glossary: "**Clock anchor** — the measured relationship between the
> sampler's timebase and the workload's wall clock…"

The label is a **wall-clock** reading, not a sampler-timebase reading.
`joulewise/uncertainty_evidence.py:77-85` (`NativeAnchorRecord`):

> "`native_timestamp_s` is the record's whole-second-quantized **naive-UTC
> plist `<date>`** mapped to epoch seconds; it labels the END of the record's
> `elapsed_s` averaging interval."

And the method identity fits **wall vs monotonic**, not sampler vs wall —
`joulewise/uncertainty_evidence.py:826-829` (v3 docstring, model condition):

> "the **wall clock is affine in monotonic time** across the capture — one
> rate, no mid-capture step — and every **native whole-second label** may
> depart from **that** affine relation by at most 250 µs"

So the two quantities being related are (i) the wall-clock whole-second
labels and (ii) the accumulated `elapsed_ns` / monotonic timeline. The
draft-v1 diff states this correctly — "The sampler labels each record with a
whole second of **wall time** and reports how long that record's averaging
interval lasted" — so guide and paper currently disagree on the core
mechanism of the section that is the guide's centrepiece.

Knock-on inside the same paragraph:

> "On this machine **the two timebases** differ by about **7 parts per
> million**"

The +7.24 ppm is wall-vs-monotonic (`03-cold-science-review.md:16-18`:
"the disciplined shakedown capture itself runs at +7.24 ppm — v2's rate=1
pin was the falsified model"; and the paper says it correctly: "the wall
clock running about +7.24 parts per million fast against **it**" [the
monotonic clock]). As written the guide attributes the 7 ppm to a
sampler-vs-wall difference that the estimator does not model.

**Correct form:** the sampler prints a whole-second **wall-clock** label per
rollover plus a per-record elapsed duration in its own monotonic-style
timebase; the anchor solves for the rate between wall time and that elapsed
timeline. Source: `joulewise/uncertainty_evidence.py:77-85, 814-865`.

Aggravating: the guide then uses "wall-versus-monotonic" twice (lines 251,
302) without ever having introduced a monotonic clock — see S8.

---

### B2 — Guide §5 "Every bound moved outward; nothing tightened; no capture changed status" is false, and "a second widening" double-counts the padding

Guide §5, verbatim:

> "**The bounds got wider. That is the honest direction.** On the calibration
> fixture shared by the whole test suite, both b_fiducial and the anchor
> bound moved outward by 3.09 microseconds, **and a second widening came from
> pricing a numerical detail instead of deferring it** (the padding constant
> was raised from 1 nanosecond to 1 microsecond, covering the representation
> error of double-precision epoch timestamps). **Every bound moved outward;
> nothing tightened; no capture changed status.**"

**(a) "nothing tightened" — falsified by the issued corpus.** I recomputed
every member's v2→v3 delta from
`docs/process_traces/2026-08-18-shakedown-first-light/04-d079-reissue-r2-proceed.log`
(`MEMBER_DELTA_REPORT.member_values`, the v2 issued b_fiducial) against
`calibration_acceptance_d079_v2_n17_r6.json → derivation_corpus.members`:

| member | v2 b_fiducial | v3 b_fiducial | Δ |
|---|---|---|---|
| 20260722T145535-e941c821 | 0.030189804 | 0.030067932 | **−0.122 ms** |
| 20260722T214220-1acdbbc0 | 0.033120146 | 0.032898494 | **−0.222 ms** |
| 20260723T221449-e9ae755e | 0.027702588 | 0.027201280 | **−0.501 ms** |
| 20260723T223406-314f6d9e | 0.026173652 | 0.025993442 | **−0.180 ms** |
| 20260725T022712-0a9534f5 | 0.029197265 | 0.028733194 | **−0.464 ms** |
| 20260725T060617-97c5cba6 | 0.025045995 | 0.025016956 | **−0.029 ms** |

**6 of the 17 issued members tightened**, including the one that becomes the
new corpus maximum. The guide contradicts itself three paragraphs later, and
correctly so: "Taking the maximum would look conservative while smuggling the
falsified model's numbers back in **wherever they happened to be bigger**" —
a sentence that only makes sense because old values sometimes *were* bigger
(corroborated by r6 `derivation_notes.derivation_method.value_semantics`:
"b_fiducial_s is the anchor-v3 re-derived value itself, NOT
max(stored_v2, anchor_v3)").

**(b) "no capture changed status" — falsified** by the next paragraph of the
same section: two captures moved accepted→refused.

**(c) "a second widening" double-counts.** `NUMERIC_PADDING_S` is used **only
in the v3 deriver** (`joulewise/uncertainty_evidence.py:1017, :1189, :1219`,
all inside `derive_powermetrics_anchor_v3` which begins at :814); the v2
composition is `half_width + offset_span + stamp_resolution` with no padding
term (`joulewise/uncertainty_evidence.py:459` region,
`bundle_bound_s = half_width_s + offset_span_s + stamp_resolution_s`). The
padding raise to 1e-6 landed at `afab1a2` (2026-08-18), which is an ancestor
of the r3 issuance `2de24b0` and therefore of the r4 head the +3.09 µs probe
was run against (`04-r1-design-opus.md` V3: "shasum of the four governed
sources vs r4's `estimator_code_sha256` — all four match HEAD exactly").
So the 3.09 µs v2→v3 delta **already contains** the ~1.0 µs padding term; the
remaining ~2.09 µs is the rate-fit widening. There is no second, additive
widening on that fixture.

Where the three clauses *are* true: they are true of the **padding raise in
isolation**. r6 `derivation_notes.method_identity.numeric_pricing`:

> "Every anchor-v3 bound moves outward by 1e-6 - 1e-9 s; **no number tightens
> and no member changed status**."

The draft is safe here — it says only "the identical inputs yield a
timing-attribution bound 3.09 µs wider under the current estimator" and
elsewhere restricts the widening claim to "the **mean anchor term** rose by
0.311 ms", which is exactly what `03-cold-science-review.md:84-85` supports.

**Minimal fix:** scope the three clauses to the padding constant, and change
the paragraph's thesis from "every bound widened" to the true and equally
strong claim: the *anchor term* rose in the mean (+0.311 ms against 25–35 ms
member bounds), while individual b_fiducial values moved both ways because
the detector re-fits under a shifted anchor — which is the same mechanism the
paper already uses to explain the +4.72 ms outlier.

---

## SHOULD-FIX

**S1 — "no such literal exists in the measurement kernel" overstates the guard.**
Guide §7: *"So no such literal exists in the measurement kernel — a regression
test forbids both digits."* The test is
`tests/test_mint_policy_resolver_guard.py:10-21` and covers exactly three
files: `joulewise/floor_mint_estimator.py`, `joulewise/detection_floor.py`,
`scripts/mint_floor_artifact_generalized.py`. Both literals *do* live in
`joulewise/calibration_bracketing.py:199, :211` — necessarily, that is the
registry. Say "mint lane" (the ruling's own scope, `14-r2-ruling.md` S4:
"forbids `0.010818`/`0.009724` literals in kernel sources") rather than
"measurement kernel", or the sentence is checkably false.

**S2 — "An external reviewer" (paper §2).**
> "An external reviewer re-implemented the estimator from its specification in
> exact rational arithmetic, sharing no code with the implementation, and
> reproduced the published intervals."

The source is `03-cold-science-review.md:3-8` — "Cold Fable instance, no loop
context… the estimator independently re-implemented… no shared code with the
production LP… reproduce the published intervals at 1-ulp tightness". That is
an internal cold-context review, not an external reviewer. The *method* claim
is fully supported; the *actor* claim is not. Recommend the actor-free form:
"An independent re-implementation of the estimator from its specification, in
exact rational arithmetic and sharing no code with the production solver,
reproduced the published intervals to one unit in the last place." (This also
removes the only place in the diff where process identity leaks into
reader-facing prose.)

**S3 — "Every generation is retained rather than overwritten" (paper §4) has one documented exception.**
`calibration_acceptance_d079_v2_r2.json` was issued at `3e780a1`
(sha256 `1c51e2d4…`) and **re-issued in place** at `54f990d`
("D-138 detection-budget ruling: … D-079 r2 **re-issued in place**",
sha256 `3c92dd66…`) under the same `acceptance_id`
`d079_calibration_acceptance_v2_n19_r2`. Six generation *files* are retained
(verified: all six present), but one generation's bytes were replaced. The
guide's parallel sentence survives because it is more precise ("Predecessor
generations are kept byte-identical forever; a superseded generation is
retired as the *live* artifact, never edited" — r2 was edited while live).
Recommend the paper adopt the guide's precision.

**S4 — "748 … on this machine" / "roughly 748" (guide §6, paper §4).**
`09-r1-debate-opus.md:195-202` executed census: **748** `p2-038.2` envelopes
in `/Users/edr/code/JouleWise` (745 bounded, 3 unknown) and 622 `p2-038.1`;
plus 173 in `/Users/edr/JouleWise-backup/runs`, 35 in
`/Users/edr/JouleWise-window-custody`, **1751 across `/Users/edr`**. "On this
machine" is the 1751 figure; 748 is the repository tree. Also `13-r1-ruling.md`
S1 says "~748 primary" because the population is enumerated at implementation
time. Paper's "**roughly** 748" hedges a figure the census made exact for the
repo tree while under-stating the machine total — pick one frame. The derived
745/748 in the guide is exact and correct.

**S5 — Guide §4 still says "under the current estimator" where the paper now says "under the current pulse detector".**
Guide line 156 (unchanged by the diff): *"the very first live capture **under
the current estimator** hit that budget and was refused."* The diff changed
the paper's matching sentence to "under the current **pulse detector**"
precisely because that capture predates the anchor replacement — and the
guide's own new step-4 addendum says "under the anchor estimator **then in
force**". As it stands the guide contradicts itself two paragraphs apart and
contradicts the paper. One-word fix; the status note ("Every calibration
number quoted below has been re-checked") invites the reader to trust it.

**S6 — "same minute" is false.**
Guide §5: *"Same machine, same protocol, **same minute** — a coin flip."*
Each probe is a ~197-second capture (`01-root-cause.md`: 197 native
rollovers; sampling duration 196.789–196.805 s), so six back-to-back probes
cannot occupy one minute; the named probe bundles alone span
`20260818T163440` → `20260818T182149`. "Same hour" or "same sitting" is both
true and rhetorically sufficient.

**S7 — One quantity, two names, never linked.**
Guide §4 (unchanged): "a **genesis lower bound** of 9.724 ms". Guide §5/§7 and
the whole paper diff: "**bracket screen**". Same number, same field
(`decimal_derivation.ratified_operatives.bracket_screen_s = "0.009724"`).
The paper's diff deliberately retired "genesis lower bound" and italicised
*bracket screen* as a defined term; the guide now uses both names without a
bridge, and its glossary defines neither.

**S8 — "monotonic" is undefined in the guide.**
It appears only at guide lines 251 and 302, both new, both inside §5
("wall-versus-monotonic spans", "wall-versus-monotonic offset moving
−3.18 ms"). The paper defines it at first use ("a monotonic clock — a counter
that only ever advances and is never adjusted by network synchronization").
The guide is the *newcomer-facing* document; it needs the gloss more, not
less. Compounds B1.

**S9 — The 43 and 32 denominators are quoted without their populations.** See
the four verdicts below for the adjudication. Both documents quote
"41 of 43" verbatim from r6 / cold review, which is defensible, but neither
says what the 43 is, and r6's own residual-margin block publishes a
different, larger replayed population (n=45 bounded + 3 binding). One
qualifying phrase in each document removes a real reviewer trip-hazard.

**S10 — "the shakedown capture" is an ambiguous referent (guide §5).**
> "the fitted rate falls out as a by-product — on **the shakedown capture**, a
> window from +7.243 to +7.285 ppm, 0.04 ppm wide"

The ppm window is from bundle **20260818T173136-bc9bff8e**
(`03-cold-science-review.md:12-14`), an afternoon diagnostic probe. The
guide's §4 story is about **20260818T045736-4d9e9db9**, the first-light
capture (`03-budget-calibration-sweep.md:56`; r6
`outlier_mechanism_note`). The cold review does loosely call bc9bff8e "the
disciplined shakedown capture", so the guide inherited the ambiguity, but a
reader who has just read §4 will bind it to the wrong bundle. The numbers
themselves are exact (7.2854172553 − 7.2430695284 = 0.0423 ppm → "0.04 ppm
wide" ✓).

**S11 — "9.2× the next highest" invites a wrong division.**
Guide §4 places it one sentence after "the 17 corpus survivors demand between
115,449 and 137,535". 1,282,827 / 137,535 = **9.33**, not 9.2. The artifact's
"9.21x the next highest" (r6 `budget_probe_status`) is against the next
highest demand among **all v3-resolvable captures** (≈139,286), which is
outside the 17. Say "next highest **of any v3-resolvable capture**". The
paper's "more than nine times the next highest" is safe as written.

**S12 — "even as individual bounds widened" (paper §7) is unqualified.**
> "since the refused pair included the contaminated corpus maximum, the
> screens derived from that corpus tightened **even as individual bounds
> widened**"

Six of seventeen member b_fiducial values fell (table in B2). Earlier in the
same paragraph the paper is careful — "3.09 µs on the shared fixture,
0.311 ms **in the mean anchor term**" — and this clause should inherit that
qualification.

---

## NITS

- **N1 — paper HTML comment mislabels two line citations.** `<!-- … consumers
  joulewise/floor_extraction.py:190, joulewise/whole_window.py:199 -->`.
  Those lines are refusal-**reason registry** rows
  (`"capture_pipeline_absent"` / `"capture_pipeline_superseded"`); the actual
  consumer call sites are `floor_extraction.py:1928`, `whole_window.py:717`,
  and `analysis_engine/inputs.py:3468`. (All three consumers *do* call the
  shared helper — the guide's claim is correct, only the citation is off.)
  Every other code citation in the diff checked out: `uncertainty_evidence.py`
  :29-33, :37-38, :42-60, :1014-1022, :1189, :1299-1324; `cli.py:1257` (exact),
  `cli.py:1568`; `calibration_bracketing.py:172` (`ACTIVE_ACCEPTANCE_ID =
  ANCHOR_V3_R6_ACCEPTANCE_ID`), :193-228, :231-291.
- **N2 — glossary alphabetical order broken by three new entries.**
  "Clock anchor" is placed after "Detection budget"; "Generation (of the
  acceptance artifact)" before "Fiducial pulse train"; "ppm" after "Rail".
  "Capture era", "Claim barrier" and "Reissue (science-neutral)" are correctly
  placed.
- **N3 — "censored-intersection" used once, unglossed** (guide §6, strict-verify
  bullet). It is the real name (`CLOCK_METHOD_V2 =
  "powermetrics_native_second_censored_intersection_v1"`,
  `uncertainty_evidence.py:19`), but it is the guide's only appearance and the
  §5 narrative never calls the old method that.
- **N4 — "in the same direction every time"** strengthens the source. Cold
  review Q3 says "a rate-drift bias of order drift/2"; the paper's "a
  systematic bias of order half the accumulated rate drift rather than random
  scatter" is the safe form.
- **N5 — band rounding convention changed.** Old text used outward rounding
  (0.022741→0.0227, 0.033559→0.0336); the new 17-member band uses nearest
  (0.023175→0.0232, 0.032898→0.0329), which narrows the low end by 0.4 µs.
  Immaterial, but the two bands now appear in the same corpus of documents
  under different conventions.
- **N6 — guide §4 item 3 (pre-existing): "Every retained raw trace on the
  machine — 34 of them — was swept."** The sweep enumerated **40** unique v3
  bundles; **34** produced full 59-pulse convergences and 6 refused before
  fitting (`03-budget-calibration-sweep.md:2, :11`). Not in the diff, but
  adjacent to new text and now the only unqualified "34" left.
- **N7 — for the record, the docs beat one of their sources.** Cold review
  Q2 says "the max drops to **32.897 ms**"; r6 `source_statistics.maximum_s`
  is `0.03289849371536248` = 32.898 ms. Guide ("0.032898 s") and paper
  (HTML comment quoting the full lexeme) both follow the artifact. Correct.
- **N8 — paper §4 present tense on an unminted receipt.** "…a new member of
  the pack family **whose freeze receipt is chained to its predecessor's**."
  `freeze-0003` is not minted (verified: no
  `arm_readiness.freeze.receipts/` under any `d117_*_v3`). The HTML comment
  acknowledges it; the prose describes the rule, so this is acceptable, but a
  reader could read it as an accomplished fact.

---

## VERDICTS ON THE FOUR SELF-FLAGGED ITEMS

### 1. "41 of 43" vs the residual-margin block's n=45 — **NOT an error. Keep the number; add the population.**

Both documents quote it faithfully:
- r6 `derivation_notes.exclusion_accounting.surviving_pre_discipline_members`:
  "**41 of 43 replayed bundles need exactly zero model slack**"
- `03-cold-science-review.md:68`: "**41 of 43 bundles need exactly zero
  slack** — the model fits normal captures at sub-µs consistency"

The n=45 is a **different population**. r6
`derivation_notes.residual_margin_distribution` reports
`all_bounded_replayed_members.n = 45` — members whose fit came back
*bounded* — with `members_that_do_bind` listing **three** ids
(`563b9849`, `901c5c13`, `4ce692b4`). 45 bounded + 3 binding = 48 replayed,
against the 43 of the exclusion-accounting sentence. The two are reconcilable
only as different replay sets: the 43 excludes the third binding member,
`20260722T213749-563b9849`, which is the permanently quarantined archive
bundle with no retained canonical raw
(`permanently_refusing_records[0]`: "runs/instrument_validation/
20260722T213749-563b9849/raw is empty… never a member of any issued D-079
corpus… PERMANENTLY QUARANTINED"), and 45/48 is a later, wider replay. **No
published number is wrong.**

Two residual cautions:
- The artifact itself never defines either population. If Ed wants that
  closed, it is a one-line addition to r6's exclusion_accounting, not a docs
  fix.
- The paper's clause "**the two that need slack are the two that are
  refused**" is true *within the 43* but false against the artifact's full
  binding list of three. Recommend "of the 43 replayed corpus-lineage
  bundles, 41 need exactly zero model slack, and the two that need slack are
  the two refused from the corpus."

### 2. The 11-of-32 denominator — **CORRECT AS QUOTED; one word of precision recommended.**

`03-cold-science-review.md:83-86`:
> "Removing a bias SHOULD produce new intervals excluding the old biased
> points — **11/32 exclusions** are the correction working. … the corpus
> **survives 32/34** with the max DECREASING."

So 34 members were re-derived, **32 survived**, and 11 of those 32 have
intervals that no longer contain the old accepted point. The guide's "11 of
the **32 re-derived captures**" therefore uses the right denominator but the
wrong participle — 34 were re-derived; 32 survived. Recommend "11 of the 32
captures that survived re-derivation". Note also that 34 is the same 34 that
converged in the budget sweep, and 32/34 = 34 minus the two steering
refusals, which is internally consistent with the n=19→17 accounting. **No
number changes.**

### 3. The 0.0232–0.0329 band — **CORRECT. Verified to the digit.**

`calibration_acceptance_d079_v2_n17_r6.json → decimal_derivation.source_statistics`:
- `minimum_s = "0.02317490442656863"` (member `20260722T215127-eeef661a`) → **0.0232**
- `maximum_s = "0.03289849371536248"` (member `20260722T214220-1acdbbc0`) → **0.0329**
- `range_s = "0.00972358928879385"` = max − min exactly → screen `0.009724` ✓

The superseded n=19 band is `[0.022741007370546462, 0.03355875667989999]` →
[0.0227, 0.0336], which the paper still quotes and **correctly labels** as
"the **then-issued** corpus band" followed by "Both that bound and that band
were derived under the superseded anchor estimator." Era labelling on this
pair is exemplary. Only N5 (rounding convention) applies.

### 4. The r2 generation-table row — **SUBSTANTIVELY CORRECT; one word wrong.**

| guide cell | verdict |
|---|---|
| id `…_v2_n19_r2` | ✓ `calibration_acceptance_d079_v2_r2.json → acceptance_id = "d079_calibration_acceptance_v2_n19_r2"`. The filename lacks `n19`; the **identity** has it, and the table is a table of identities. Correct. |
| "audited detection work, **then the budget correction**" | ✓ Two commits, one identity: `3e780a1` "D-079 successor ISSUED (d079_calibration_acceptance_v2_n19_r2) + dual-generation live-pin migration", then `54f990d` "D-138 detection-budget ruling: DETECTION_PROJECTION_CELL_BUDGET 100k → 165k, **D-079 r2 re-issued in place**". |
| "corpus still 19" | ✓ `derivation_corpus.n = 19`; screen `0.010818`, drift ceiling `0.012093166090593858` unchanged from the genesis generation. |
| "estimator **pins**" (plural) | ✗ **One pin.** Against the genesis `…_v2_n19` artifact, exactly one of the four `estimator_code_sha256` entries differs: `joulewise/powermetrics_fiducial.py`. The budget re-issue's own delta report confirms it independently: `04-d079-reissue-r2-proceed.log` `"changed_pin_count":1`, with only the `powermetrics_fiducial.py` row `"changed":true`. Both r2 issuances rotated the same single file. Recommend "one estimator pin, rotated twice". |

Two further notes the writer should have: r2 is the **only** generation with
no `derivation_notes` at all (no `predecessor`, no `reissue_delta`,
no science-neutrality record) — so the guide's "each carries its proof rather
than an assertion… a named predecessor with its file hash, the
before-and-after hash of every estimator source that changed" is true of
r4/r5/r6 and **not** of r2. As written the sentence is scoped to "r4, r5 and
r6", so it holds — but it is worth knowing that the table's second row is the
one link in the chain that cannot show its own proof. And r2 is the
in-place-rewrite exception behind S3.

---

## CROSS-CUTTING CHECKS (all clean unless noted)

| Check | Result |
|---|---|
| Same numbers for the same facts, guide vs paper | ✓ 9.724 ms / 10.164835 ms (guide 10.165 ms), 10.818→9.724, 19→17, 3.09 µs, 41 of 43, +7.24 ppm window, 748/745, 165,000 & 137,535, 0.033559→0.032898. **Two divergences**, both listed: S5 ("current estimator" vs "current pulse detector") and S7 ("genesis lower bound" vs "bracket screen"). Plus B1 (mechanism). |
| No energy claim value filled in the paper | ✓ `[PENDING]` count is **15 at HEAD and 15 in the worktree**; the diff touches no Section-6 table cell and introduces no measured energy value. |
| No internal process machinery leaked | ✓ Guide diff: zero hits for council / magistrate / seat / cold gate / classifier / lieutenant / Sol / Codex / subagent / ruling / Fable / Opus. Paper diff: "ruling" appears 4× and **only inside HTML comments** (the `13-r1-ruling.md` / `14-r2-ruling.md` filenames and r6's own `.budget_ruling` field name). One judgement call flagged separately as S2 ("external reviewer"). |
| Every new term defined at first use | ✓ *capture-pipeline era*, *bracket screen*, *generation*, *pin set*, *monotonic clock*, *admissible set* — all defined at first use in the paper. Guide defines *clock anchor*, *capture era*, *claim barrier*, *generation*, *ppm*, *rate-aware set membership*. **Misses:** monotonic (S8), bracket screen vs genesis lower bound (S7), censored-intersection (N3). |
| Every historical/superseded value labeled with its era | ✓ Strong. `[0.0227, 0.0336]` → "the **then-issued** corpus band… derived under the superseded anchor estimator"; 0.0309 s → "under the anchor estimator **then in force**"; 0.033559 s → "under the old model"; 10.818 ms → "the **previous generation's**"; 137,189 → framed by the new "re-earned, not inherited" paragraph. No unlabeled superseded value found. |
| S4 state (33 receipts, 11 kinds, freeze-0003 outstanding) | ✓ **Exactly right.** 11 `evidence-*.json` per pack × 3 packs = 33, each with a `.sha256` sidecar; parsed all 33 → `Counter({'PASS': 33})`. No `arm_readiness.freeze.receipts/` under any `d117_*_v3` (present under every `_v1`/`_v2`). |
| `_v3` packs bound at birth to the live generation | ✓ `d117_floor_qwen25_1p5b_v3/generate_configs.py:155` `SUCCESSOR_ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n17_r6"`; test `test_v3_specs_and_plan_trees_bind_r6_via_generation_resolver` and `test_committed_v2_pack_tree_digests_are_unchanged_at_head` both exist in `tests/test_d117_v3_family.py`, backing the guide's "a regression re-hashes the committed `_v2` trees to prove it". Note `14-r2-ruling.md` S7 says r5; the packs bind r6, which is the later, correct state. |
| Shakedown deltas +4.72 / 0.32 ms | ✓ r6 `outlier_mechanism_note`: "+4.72 ms b_fiducial delta on **20260818T045736-4d9e9db9**… anchor point moves only +0.27 ms and its B_anchor only +0.32 ms. The remainder is detector-refit sensitivity… accepted regions jumping sample quanta". Bundle identity confirmed as the first-light capture via `03-budget-calibration-sweep.md:56` and `02-root-cause-diagnosis.md:101`. Paper's rendering is exact. |
| Budget block | ✓ `corpus_survivor_cell_demand {n:17, min:115449, median:122097, p95:137535, max:137535}`; `governed_projection_cell_budget 165000`; 165000/137535 = 1.1997 → "about 20%"; `budget_probe_status` probe `20260818T182149-a7e8b412`, 1,282,827 cells, "9.21x the next highest", `detection_nonconvergent`. Guide's "ninefold increase" matches r3's rejected Option A (165,000→1,550,000 = 9.4×). |
| Screens / drift ceilings / quantile method | ✓ `bracket_screen_s "0.009724"` from `range_s "0.00972358928879385"` (ROUND_HALF_EVEN, quantum 1e-6); `maximum_budgetable_drift_s "0.010164834757777545"` = `prediction_99_two_draw_s`, df 16, t(0.995,16) = 2.92078162242509999197 by "exact even-degree-of-freedom closed form (Abramowitz & Stegun 26.7.4) solved by bisection in 60-digit decimal". n=19 counterparts 0.010818 / 0.012093166090593858 ✓. Both live in `calibration_bracketing.py:193-228` keyed by acceptance id ✓. |
| Exclusions + mechanism | ✓ `901c5c13` (issued 0.03355875667989999, corpus max) and `4ce692b4`, both `anchor_v3_status: unresolved`, `anchor_v3_detail: affine_clock_fit_empty`, mechanism "ACTIVE TIME STEERING during the capture, pre-clock-discipline"; custody corroboration `pin-20260727T051946Z` postdates both. Slacks 5.612 µs / 1.873 µs, rate windows [−1.1,+5.2] vs [−16.04,−15.99] ppm and −9.2 vs −2.27 ppm, offset move −3.18 ms — all verbatim from `03-cold-science-review.md:59-66`. |
| Probe widths / spans / rollovers | ✓ `01-root-cause.md:128-140`: valid +780.344 µs, +1.038790 ms; invalid −4.292, −312.567, −209.570, −158.787 µs; 197 native rollovers; wall-minus-monotonic spans 1.442–1.447 ms; "no measurable startup discriminator", readiness 1.136–1.192 s, sampling 196.789–196.805 s. Guide and paper both faithful. |
| Era system, barrier vocabulary, resolver, crosswire guard | ✓ `13-r1-ruling.md` S1/S2/S3/S4/S8 and `14-r2-ruling.md` S1/S2/S3/S4/S7 all match the prose; code verified at `uncertainty_evidence.py:29-33, :1298-1324` and `calibration_bracketing.py:231-291` (registered-generation lookup, unregistered → refusal, `bracket_screen_s` disagreement → refusal). |
| r6 file hash prefix `0227bca3` | ✓ `shasum -a 256` = `0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d`. |
| Section renumbering | ✓ "Sections 4–8 are that self-measurement", "calibration (sections 4 and 5)", "floors (section 8)", and all ten `##` headings renumbered consistently; every internal "section 5"/"section 6" cross-reference resolves. |

---

## SUMMARY

- **2 blockers**, both guide §5, both fixable in one paragraph-pair: B1 (wrong
  clock pair; contradicts `NativeAnchorRecord` and the paper) and B2 (six of
  seventeen members tightened, two changed status, and the padding is already
  inside the 3.09 µs).
- **12 should-fix**, of which the load-bearing ones are S1 (checkably false
  scope claim), S2 ("external reviewer"), S3 ("never overwritten" vs the r2
  in-place re-issue) and S5 (guide/paper split on "current estimator").
- **8 nits.**
- **All four self-flagged items survive:** 41/43 correct (population needs
  naming), 11/32 correct (participle needs fixing), 0.0232–0.0329 exact, r2
  row correct except "pins" → "pin".
- No energy value entered the paper; all 15 `[PENDING]` markers intact; no
  process machinery in reader-facing prose; era labelling on superseded
  values is the strongest part of the diff.
