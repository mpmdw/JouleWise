# R1 — OPUS INDEPENDENT DESIGN SEAT
## Production capture-pipeline v3 adoption

Seat: Opus 5, independent design (co-design protocol D-144-pending).
Read-only at `integration/phase2-transaction` @ `9f7f091`, worktree
`…/scratchpad/wtTXN`. Working tree verified clean at exit (`git status --short`
empty). Every file:line below was opened and read by me; every numeric or
behavioural claim marked **[verified]** was reproduced by a command I ran.

---

## 0. Executive summary — what I found that changes the question

The brief asks a narrow question (flip four adapter call sites, decide the
label, decide what to do with stored bundles). Five verified findings widen it:

1. **The label is already minted and already ratified.** `SCHEMA_VERSION_V3 =
   "p2-038.3"` exists at `joulewise/uncertainty_evidence.py:17`, is emitted by
   `derive_powermetrics_clock_evidence_v3` at `:1237`, and the LIVE acceptance
   artifact already declares `"evidence_schema": "p2-038.3"` in its
   `derivation_notes.method_identity`
   (`configs/calibration/calibration_acceptance_d079_v2_n17_r4.json`) **[verified
   by reading the artifact]**. There is no label decision left to *make*; there
   is a label *discipline* to fix — see §1.

2. **The failing canonical test does not have the root the brief assigns it.**
   `test_d079_real_selector_to_real_reducer_embeds_allowance_once`
   (`tests/test_whole_window_selection.py:2282`) fails with
   `calibration_ledger_custody_invalid`, not a production-capture error. I
   confirmed the root by **executed experiment**: reverting *only*
   `joulewise.calibration_bracketing.ACTIVE_CAPTURE_ANCHOR_METHOD` back to
   `CLOCK_METHOD_V2` in-process turns the test green (`Ran 1 test … OK`)
   **[verified]**. The cause is bb81323's *already-landed* calibration-admission
   flip (`joulewise/calibration_bracketing.py:1039-1040`) meeting a test helper
   that still mints v2 candidates (`tests/test_reduce.py:194`, `:233-235`). It is
   evidence *for* the flip's correctness, not evidence about the un-flipped
   adapter.

3. **The site list is incomplete.** Beyond the 4 adapter sites, production
   hardcodes the v2 estimator at `joulewise/environment_admission.py:307,351`
   (a fifth capture-adjacent site the brief does not name), and
   `joulewise/powermetrics_fiducial.py:1467` carries a silent `or CLOCK_METHOD_V2`
   **default** that will mislabel evidence after the flip. Full census in §2.

4. **After the flip there is NO mechanical barrier stopping a stored v2-anchor
   bundle from being consumed as claim-bearing evidence.** The analysis engine's
   D-078 barrier is keyed to *reducer version*
   (`joulewise/analysis_engine/inputs.py:121,3671-3678`), and all 769
   window-corpus summaries on disk carry `reducer_version 0.5.2` **[verified: I
   parsed every `runs_window_*/*/summary_metrics.json` — `Counter({'0.5.2':
   769})`]**, which is *not* in the barrier set. The only thing currently
   excluding those bundles is per-window human policy (`WINDOW_STATUS.md:44-53`).
   Since the cold review ruled v2's rate=1 model **falsified**
   (`docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md:15-17,81-83`),
   the flip must install a *mechanical* anchor-era claim barrier. This is the
   single most important clause in my design.

5. **The flip cannot be done outside the parked transaction.** All four governed
   estimator pins in the live r4 artifact match the current head byte-for-byte —
   including `joulewise/adapters/powermetrics.py` at
   `9f165a513f1f60a314dfaa3fbc8c95781c13072b1e997c208dfad0acda7ed3ec` **[verified
   by `shasum -a 256` against the artifact's `prospective_rederivation.
   estimator_code_sha256`]**. Editing the adapter therefore fires r4's own
   `protocol_or_estimator_byte_change` trigger and mandates an **r5** reissue,
   exactly as the adapter-adjacent activation forced r4 at bb81323.

The **cost of the strict answer is zero**, which is why I take it. Every stored
calibration candidate is already excluded by freshness (`MAX_AGE_S = 86400`,
`joulewise/powermetrics_fiducial.py:58`, applied at
`joulewise/calibration_bracketing.py:1524,1532,1712,1717`) **[verified]**;
historical-import receipts are already excluded from the custody count
(`joulewise/calibration_bracketing.py:1939-1951`, and all 76 live ledger rows are
`historical-import-v1-*` events **[verified by parsing
`/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl`]**); and
all claim authority already comes only from the prospective alpha/beta/gamma
windows (`WINDOW_STATUS.md:14-18`, `CLAIMS_STATUS.md:29-36`). Fail-closed here
costs us nothing and closes a real hole.

---

## (a) THE DECISION — ratifiable spec

### Clause 1 — Label: mint `p2-038.3`; retain `p2-038.2`; retire nothing

**R1-1.1.** Production powermetrics capture emits `uncertainty_evidence.
schema_version = "p2-038.3"` and `clock_anchor.method =
powermetrics_native_second_rate_aware_set_membership_v1`.

**R1-1.2.** `p2-038.2` and `p2-038.1` are **retained forever as readable stored
eras**. Neither is retired. This follows the `.1 → .2` precedent verbatim:
`docs/contracts/run_bundle_layout.md:511-519` established "New captures record
… `p2-038.2` … Exact dispatch for stored `p2-038.1` evidence is retained,"
and `joulewise/uncertainty_evidence.py:1319-1330` already generalises that into a
reconstruction-only registry.

**R1-1.3 (rationale against "keep the label, version elsewhere").** The schema
label is 1:1 with the anchor-method identity by construction — `.1↔CLOCK_METHOD`
(`:15,18`), `.2↔CLOCK_METHOD_V2` (`:16,19`), `.3↔CLOCK_METHOD_V3` (`:17,20`) —
and two independent consumers already dispatch on the pair: `joulewise/cli.py:1266`
dispatches on the *schema label*, `joulewise/reduce.py:1793` dispatches on the
*method string*. Keeping `.2` while changing the method would make the stored
label non-identifying and silently mis-route `cli.py`'s re-derivation to the v2
estimator for a v3-derived bundle — a fail-open byte-match against the wrong
model. The label must move with the method.

**R1-1.4 (NEW — closes a forgery surface the brief does not name).** Introduce
one canonical mapping in `joulewise/uncertainty_evidence.py`:

```
SCHEMA_FOR_ANCHOR_METHOD = {
    CLOCK_METHOD:    SCHEMA_VERSION,      # p2-038.1 (reconstruction-only)
    CLOCK_METHOD_V2: SCHEMA_VERSION_V2,   # p2-038.2
    CLOCK_METHOD_V3: SCHEMA_VERSION_V3,   # p2-038.3
}
```

and make **method the single dispatch key everywhere**, with the schema label
required to *agree*. A bundle whose `schema_version` and
`clock_anchor.method` disagree is a **refusal** (`clock_anchor_era_inconsistent`),
never a resolution in favour of either. Rationale: today a bundle labelled
`.2` carrying `method: v3` would be re-derived as v2 by `cli.py` and as v3 by
`reduce.py` — two answers from one artifact. Same cross-check for calibration
evidence: `instrument_evidence["anchor_method_version"]` must equal
`instrument_evidence["clock_anchor"]["method"]` (today
`joulewise/powermetrics_fiducial.py:1467` sets the former from
`detection.anchor_method or CLOCK_METHOD_V2` while
`rederive_detection_from_artifacts:1128-1137` reads the latter — the same two-key
hazard, with a v2 default papering over it).

**R1-1.5 (naming hygiene, for the ruling's record).** "v2" is overloaded in this
tree and the ruling must not inherit the ambiguity: `d079_calibration_acceptance_
**v2**_n17_r4` is the *acceptance-bound schema* v2
(`joulewise.calibration_acceptance_bound.v2`); `d117_floor_qwen25_7b_**v2**` is
the *pack generation*; `PROTOCOL_V2_ID` is the *pulse protocol*. None of them is
the anchor method. Ruling text should say "anchor-v2 / anchor-v3" throughout.

### Clause 2 — Admission: era-faithful replay, active-method-only capture, v3-only claims

**R1-2.1 (custody/integrity is era-agnostic).** `joulewise verify --strict`
accepts and *verifies* all three stored eras, each re-derived under **its own
stored method**. Strict verify answers "are these bytes internally consistent
with the estimator that produced them", which is a custody question, not a
science question. This is the D-078 precedent applied without modification
(`joulewise/cli.py:1272-1283` already does exactly this for `.1`).

**R1-2.2 (fresh production capture is active-method-only).** The campaign /
shakedown gate `assert_production_uncertainty` requires
`schema_version == SCHEMA_FOR_ANCHOR_METHOD[ACTIVE_CAPTURE_ANCHOR_METHOD]` **and**
`clock_anchor.method == ACTIVE_CAPTURE_ANCHOR_METHOD` — an **equality against the
active constant, not membership in a set**. Rationale: this gate certifies a
capture the project just took on its own hardware; there is no honest reason for
it to have been taken under a superseded estimator, and a set-membership test
here is precisely how a stale-adapter regression would go unnoticed.

**R1-2.3 (NEW mechanical claim barrier — the central clause).** Add to
`joulewise/analysis_engine/inputs.py`, alongside the existing D-078 reducer
barrier:

```
CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})
```

A bundle whose `metadata.uncertainty_evidence.clock_anchor.method` is not in that
set contributes `clock_anchor_unresolved` to its metric's refusal reasons —
regardless of reducer version, regardless of bounded status, regardless of
custody. Justification, quoted from the ratified science: "v2's rate=1 pin was
the **falsified** model" (`03-cold-science-review.md:15-17`); "v2's rate=1
assumption is measurably false by several ppm; its knife-edge intersections
placed midpoints with a rate-drift bias of order drift/2 … 11/32 exclusions are
the correction working" (`:81-84`). An estimator whose model has been falsified
does not produce admissible evidence, however clean its custody. This clause is
the exact structural analogue of `PRE_ANCHOR_REDUCER_VERSIONS`
(`inputs.py:117-121`), which D-078 installed for the *previous* method
transition; not installing it now would make anchor-v3 the first method
transition in this project's history that did **not** carry a claim barrier.

**R1-2.4 (no retrofit escape hatch for measurement bundles).** Stored anchor-v2
measurement bundles are **not** admitted by re-deriving them under v3. It is
technically possible — they carry the five `clock_stamps` and native rows v3
needs — and it is therefore worth refusing *explicitly* rather than by silence.
Three reasons: (i) the captures that would most benefit are the pre-clock-
discipline ones, which are exactly the ones v3 correctly **refuses**
(`03-cold-science-review.md:53-77`); (ii) the windows are already policy-dead
(`WINDOW_STATUS.md:44-53`, D-113/D-117), so the retrofit buys zero claims;
(iii) a re-derivation lane for claim energies would need its own acceptance
generation, its own freeze, and its own review — a program, not a clause.
Register this as a named limitation so the closure is legible to the paper.

**R1-2.5 (the one place re-derivation IS the ruled route — distinguish it).**
The D-079 **acceptance corpus** already consumes stored anchor-v2 bundles by
re-deriving them under v3: r4's `derivation_corpus.members` bind each member's
stored `manifest_sha256` / `instrument_evidence_sha256` as *custody* while
carrying v3-re-derived `b_fiducial_s` values (bb81323's message: "the stored v2
lexeme is SUPERSEDED, never copied") **[verified by reading the artifact]**. That
is lawful and stays lawful because it produces *population statistics for a
threshold*, judged by an independent oracle
(`tests/verify_calibration_acceptance_corpus.py`), not per-bundle claim energies.
The ruling should state the distinction in one line so nobody later reasons "we
re-derived the corpus, so we may re-derive claims."

**R1-2.6 (calibration candidate admission — keep the landed check).** Retain
`joulewise/calibration_bracketing.py:1039-1040` unchanged (equality against
`ACTIVE_CAPTURE_ANCHOR_METHOD`). Verified cost: **zero**. Every one of the 15
stored candidates in `/Users/edr/code/JouleWise/runs/instrument_validation/`
declares `anchor_method_version = …censored_intersection_v1` **[verified: 30
occurrences, 15 members × evidence+bindings]**, and every one of them is already
older than `MAX_AGE_S = 86400 s` relative to any future window, so none could
ever bracket a live measurement. The ledger's 76 rows are all
`historical-import-v1-*` **[verified]** and historical imports are excluded from
`registered_valid` (`calibration_bracketing.py:1939-1951`), so the check cannot
produce a spurious `calibration_ledger_custody_invalid` in production. The one
place it *does* bite is synthetic test fixtures — correctly, and §(d) fixes them
honestly rather than exempting them.

### Clause 3 — Hardening carried by the same transaction

**R1-3.1.** `joulewise/powermetrics_fiducial.py:1467`: replace
`detection.anchor_method or CLOCK_METHOD_V2` with a fail-closed read — a
detection with no anchor method raises rather than being labelled v2. A silent
default that names a *falsified* estimator is a mislabelling engine.

**R1-3.2.** `joulewise/environment_admission.py:307,351`: dispatch through
`resolve_anchor_reconstructor(clock_anchor.get("method"))` exactly as
`reduce.py:1793` does, instead of hardcoding `derive_powermetrics_anchor_v2`.
This is not cosmetic: the thermal-pressure coverage walk timestamps the measured
records from this anchor, so on a v3 bundle it currently (a) uses a different
model than the bundle's own evidence, and (b) can hit the v2 knife-edge
(`native_intersection_empty`, the alternation documented at
`01-root-cause.md:126-140`) on a capture v3 resolves cleanly, refusing the bundle
as `environment_admission_missing` — a *correct-looking* refusal for a *wrong*
reason, which is the hardest class of defect to ever find again.

**R1-3.3.** `joulewise/controller.py:1357`: the synthesised seed envelope
hardcodes `"schema_version": "p2-038.1"` when the telemetry produced no evidence.
For a powermetrics bundle this stamps a pre-D-078 era label on a current-era
bundle. Set it from `SCHEMA_FOR_ANCHOR_METHOD[ACTIVE_CAPTURE_ANCHOR_METHOD]`
when the backend is powermetrics; leave other backends unchanged. *(Lowest-
confidence item in my design — see §(g) Q3.)*

**R1-3.4 (incidental, bundled because it is inside the function §R1-2.3 amends).**
`joulewise/analysis_engine/inputs.py:188` tests `anchor.get("status") ==
"unresolved"`, but the codebase never emits that value — both
`_unresolved_anchor:291` and `_unresolved_anchor_v3:701` emit `status:
"unknown"` **[verified by reading both]**. The comparison is dead. It is
currently masked by the precheck-reason test at `:175-179`, so this is a
belt-that-was-never-buckled, not a live hole — but it is a fail-open shape one
refactor away from mattering. Fix it with a defect-shaped regression.

### Clause 4 — Transaction placement (binding)

**R1-4.1.** The flip lands **inside** the parked atomic re-freeze, as its next
step, and **before** any freeze re-mint. It is not separable: the adapter is one
of r4's four pinned governed estimator sources **[verified — all four pins match
the current head exactly]**, so touching it fires
`protocol_or_estimator_byte_change` and invalidates the live acceptance artifact.
Landing it after the re-mints would invalidate the receipts that were just
minted and force a second wave.

**R1-4.2.** The flip and the resulting **r5** reissue land as **one commit**,
for the same reason bb81323 gave for bundling activation with r4: splitting them
commits a knowingly-broken intermediate head whose live acceptance pins are stale
by construction.

**R1-4.3.** r5 must be **proven** science-neutral, not asserted — replay the full
19-member corpus through `rederive_detection_from_artifacts` at the flip head and
diff every `b_fiducial`, anchor bound, refusal disposition and projection cell
count against the r4 derivation record, exactly as r4 proved neutrality against
r3. The expectation is exact reproduction (the flip changes only *which deriver
the adapter calls at capture time*; the corpus is derived from raw bytes through
the deriver registry, which the flip does not touch), but the note in the trace
record stands: the reissue **tool** compares stored scalars and cannot check v3
generations, so this is a bespoke derive/build script, not the tool.

**R1-4.4.** r4 is **retained** as an intermediate generation, byte-identical
forever, exactly as r3 and r2 are. Only the LIVE surface moves.

---

## (b) TOUCH POINTS — enumerated file:line, all opened and verified by me

### B1. Production capture — the four adapter sites (brief's count confirmed)

| # | Site | What it is |
|---|---|---|
| 1 | `joulewise/adapters/powermetrics.py:525` | empty-capture evidence envelope in `stop_sampling_with_evidence` |
| 2 | `joulewise/adapters/powermetrics.py:540` | primary measured-window evidence derivation |
| 3 | `joulewise/adapters/powermetrics.py:563` | re-derivation after the stop-bracketing prefix freeze |
| 4 | `joulewise/adapters/powermetrics.py:755` | drain-loop anchor in `_drain_until_stop_bracket` |

Supporting: import at `:45`; the `p2-038.2` identity sentence inside
`TIMESTAMP_DERIVATION` at `:77` (this string is stored provenance text, not a
comment — it must be rewritten for the v3 method or it becomes a false
description of the derivation). Leave `derive_powermetrics_clock_evidence` (v1)
at `:1677` alone — that is `trace_fallback_endpoint`'s frozen structural
fallback, deliberately era-independent.

Key-compatibility **[verified]**: `derive_powermetrics_anchor_v3`'s bounded
record (`uncertainty_evidence.py:1187-1213`) emits `admissible_lower_epoch_s`,
`admissible_upper_epoch_s`, `first_sample_end_point_epoch_s`,
`effective_clock_anchor_bound_s`, `wall_minus_monotonic_span_s` and
`clock_stamps` — every key the adapter (`:554`, `:769`), the reducer
(`reduce.py:1804-1806`) and strict verify consume. `_unresolved_anchor_v3:700-709`
carries `clock_stamps` unconditionally, matching v2's extras behaviour
(`:349-382`). **The flip is key-compatible; no consumer needs a shape change.**

### B2. Strict verify — six cli.py sites (brief cited two)

| Site | Change |
|---|---|
| `joulewise/cli.py:108` | import `SCHEMA_VERSION_V3` (+ the new mapping) |
| `:1233` | accepted-label set must include `.3` — otherwise **every new bundle fails strict verify** |
| `:1266` | dispatch: replace the `== V2` branch with method-keyed dispatch (R1-1.4) |
| `:1290` | unresolved-anchor fallback replay: must cover `.3`, not just `.2` |
| `:1547` | `_powermetrics_trace_endpoint_s`: `.2`-only test must cover `.3` |
| `:1575` | `_strict_rich_telemetry_problems`: **`!= V2 → return []`. This is the flip's worst fail-open: a v3 bundle would silently skip rich-telemetry verification entirely.** Must be era-inclusive. |

Docstrings at `:1272`, `:1541-1544`, `:1561-1565` state the D-078 precedent in
prose and must be extended to the three-era rule.

### B3. Campaign gate — **`scripts/run_campaign.py`, not `cli.py`**

| Site | Change |
|---|---|
| `scripts/run_campaign.py:1635` | `schema_version != "p2-038.2"` → equality against the active-era label |
| `scripts/run_campaign.py:1637` | refusal detail string |
| `scripts/run_campaign.py:1644` | `clock.method != "…censored_intersection_v1"` → equality against `ACTIVE_CAPTURE_ANCHOR_METHOD` |

The brief cites "the campaign gate (cli.py ~:1644 region)". `cli.py:1644` is
inside `_verify_nvidia_smi_raw_to_trace` and has nothing to do with this
**[verified by reading it]**. The `:1644` line number is right; the file is not.
See §(f).

### B4. Fifth production site the brief does not name

`joulewise/environment_admission.py:307` (import), `:351` (call) — see R1-3.2.

### B5. Calibration evidence labelling

`joulewise/powermetrics_fiducial.py:1467` — see R1-3.1.

### B6. Controller seed envelope

`joulewise/controller.py:1357` — see R1-3.3.

### B7. Analysis / claim admission

`joulewise/analysis_engine/inputs.py`: add `CLAIM_BEARING_ANCHOR_METHODS` near
the existing barriers (`:108-134`), wire into the refusal path at `:3670-3678`,
and into `:180-191`; fix the dead comparison at `:188`. The comment at `:111`
naming "p2-038.2 metadata schema" must be corrected — it describes the reducer
0.5.2/0.6.2 envelope wire, which is orthogonal to the anchor era, and leaving it
invites a future reader to conflate the two.

### B8. Contracts and specs (all verified stale or era-bound)

| File:line | Issue |
|---|---|
| `docs/contracts/run_bundle_layout.md:492` | "schema `p2-038.1`" in the base P2-038 section |
| `docs/contracts/run_bundle_layout.md:511-530` | the `### D-078 additive era` section — add the parallel anchor-v3 era section; this is the ONE home for the era rule and the precedent template to copy |
| `docs/contracts/powermetrics_fiducial.md:144` | binding vector names the v2 method as *the* value |
| `docs/contracts/powermetrics_fiducial.md:174` | **already stale at HEAD**: says the reducer requires `anchor_method_version` equals the v2 literal; `joulewise/reduce.py:1388-1393` now only requires membership in `ANCHOR_METHOD_VERSIONS` **[verified]** |
| `docs/contracts/analysis_plans.md:274` | "metadata uncertainty schema p2-038.2" attached to the reducer-0.5.2 envelope rule — decouple |
| `docs/specs/c027/p2-038_production_uncertainty_evidence.md:512,733` | **stale by two eras**: still specifies `p2-038.1` and the v1 clock method for `assert_production_uncertainty`. The `.1→.2` flip never updated this spec — a precedent *failure* to correct now, not to repeat. |

### B9. Explicitly NOT in scope

`joulewise/uncertainty_evidence.py:1327-1330` (`ANCHOR_RECONSTRUCTION_DERIVERS`) —
untouched. Stored-method replay semantics are the thing that makes era retention
possible; the flip must not perturb them.

---

## (c) PER-CONSUMER ADMISSION POLICY FOR STORED ANCHOR-v2 BUNDLES

Population, corrected **[verified]**: **771** measurement bundles under
`/Users/edr/code/JouleWise/runs_window_*/` carry `uncertainty_evidence.
schema_version = "p2-038.2"` (top roots: `a5` 107, `metrologyB` 70, `metrologyA`
68, `a8` 60, `7bfloor` 57, `contrast`/`c`/`b` 47 each, …), plus **1** test
fixture (`tests/fixtures/d117_v2_production/strict_seed_bundle/metadata.json`),
plus **15** instrument-validation candidates whose `instrument_evidence.json`
declares the v2 anchor method, plus mirrors in
`/Users/edr/JouleWise-backup/runs` (173) and `/Users/edr/JouleWise-window-custody`
(35). The brief's figure of 54 does not correspond to any population I could
find; see §(f).

| Consumer | Policy for a stored **anchor-v2** bundle | Mechanism | Evidence it demands | Precedent |
|---|---|---|---|---|
| **`verify --strict` (custody/integrity)** | **ADMIT AND VERIFY**, re-derived under its **stored** method | `cli.py:1266` method-keyed dispatch; `resolve_anchor_reconstructor` | byte-identical re-derivation of `clock_anchor` + `sample_phase` from raw plist + stored `clock_stamps`; rich telemetry byte-matches the anchor-corrected re-derivation | **Follows** D-078 (`cli.py:1272-1283`, `run_bundle_layout.md:519`) verbatim |
| **`verify --strict` (anchor-v1 `.1` bundles)** | **ADMIT, replay-only**, never re-judged as v2/v3 | unchanged `cli.py:1274-1283` | frozen spawn-bracket derivation replays | **Follows** D-078 unchanged |
| **Campaign / shakedown gate** (`assert_production_uncertainty`) | **REFUSE** — `clock_evidence_missing` / `clock_evidence_invalid` | `run_campaign.py:1635,1644` equality against the **active** method | none admits it; the gate certifies a *fresh* capture | **Distinguishes** D-078: D-078 moved this gate's literal from `.1` to `.2` wholesale rather than making it active-method-relative. I make it relative so the next transition cannot forget it. |
| **Reducer** (`reduce_bundle`) | **REDUCE, era-faithfully** — v2 bundles reduce under the v2 reconstruction; the resulting summary is *replay-readable, not claim-licensed* | `reduce.py:1793` (already method-aware) | stored-method reconstruction must succeed and be bounded | **Follows** the existing landed design (`4efea13`, `fa7917b`) |
| **Analysis admission / claim consumption** | **REFUSE — `clock_anchor_unresolved`** | **NEW** `CLAIM_BEARING_ANCHOR_METHODS = {CLOCK_METHOD_V3}` in `analysis_engine/inputs.py` | **no re-derivation admits it** (R1-2.4). Admission requires the bundle to have been *captured* under v3, not re-derived under it. | **Follows** the D-078 barrier *shape* (`inputs.py:117-121,3671-3678`) but **keys it to anchor method rather than reducer version**, because the falsified thing is the estimator, not the wire |
| **Calibration bracket candidates** (live pre/post) | **REFUSE** (candidate simply does not load) | `calibration_bracketing.py:1039-1040`, already landed | none; and `MAX_AGE_S` makes it moot in production | **Extends** the landed bb81323 decision; verified zero production cost |
| **D-079 acceptance corpus** (population statistics) | **ADMIT under v3 re-derivation from primary bytes** — stored bytes are custody, values are re-derived | `rederive_detection_from_artifacts` at the pinned head; independent oracle `tests/verify_calibration_acceptance_corpus.py` | manifest+evidence sha256 custody match; every value re-derived, never copied; predecessor self-authentication; non-pin keys carried byte-identically | **Distinguishes** — and this distinction is the clause that must be written down (R1-2.5) |
| **Frozen `.1`/`.2` fixtures in the test tree** | **RETAIN as refusal fixtures** | see §(d) | they exist to prove the gates *refuse* | new |

**The line, stated once:** *stored bytes are custody and replay forever; a
falsified estimator's output is never claim-bearing; re-derivation may produce
population statistics for a threshold, and may never produce a claim energy.*

---

## (d) MIGRATION + TEST FAN-OUT TO FULL GREEN

### Step 0 — Baseline (before any edit)

Consume the canonical totals already on disk from the bb81323 run at
`…/d6206bd4-…/scratchpad/final-full.log` (trace-notes.md:449-457) rather than
re-running (~30 min saved). Confirm the 33 mint-lane reds + the single
`embeds_allowance_once` failure; anything else is a new baseline and stops the
step.

### Step 1 — Shared helper, first (highest blast radius, do it under its own eye)

`tests/test_reduce.py:64-270` `self_consistent_calibration` is the shared
synthetic-calibration builder used by **five** test modules (`test_reduce`,
`test_whole_window_selection`, `test_calibration_exits`,
`test_p2038_production_path`, `test_powermetrics_fiducial`) **[verified by
grep]**. It hardcodes `derive_powermetrics_anchor_v2` at `:194` and the v2
binding lexeme at `:233-235`.

Change: add `anchor_method: str = ACTIVE_CAPTURE_ANCHOR_METHOD`, derive through
`resolve_anchor_deriver(anchor_method)`, and set **both**
`bindings["anchor_method_version"]` and the emitted
`clock_anchor["method"]` from it — never independently (R1-1.4). Do **not**
fix this by relabelling the binding while leaving the v2 derivation in place:
that manufactures exactly the two-key inconsistency this design outlaws.

**Quantified consequence [verified by executed probe]** — flipping the helper's
deriver moves its outputs:

```
anchor-v2 : b_fiducial_s 0.021424074867246012 , bound 0.001005815101623535
anchor-v3 : b_fiducial_s 0.021427166160575920 , bound 0.001008906394953447
```

+3.09 µs, wider — consistent with the "honest widening" finding
(`03-cold-science-review.md:79-84`). No test carries this literal as a golden
**[verified: `grep -rn "0\.02142" tests/` is empty]**, but every derived hash,
energy and bracket scalar downstream of the helper will move. Budget one
goldens wave; do not batch it with any other change.

### Step 2 — Production flip + hardening (the pin-moving edit)

Adapter sites B1, cli sites B2, campaign gate B3, plus R1-3.1/3.2/3.3. All in
one change so the head is never internally inconsistent.

### Step 3 — Claim barrier (B7)

`CLAIM_BEARING_ANCHOR_METHODS` + the dead-comparison fix.

### Step 4 — r5 issuance in the same commit (R1-4.2, R1-4.3)

### Step 5 — Contracts and specs (B8)

### New tests the design itself demands — attack-shaped

Every one of these is written to **fail on the un-fixed code** and to fail again
if the fix is later reverted:

| ID | Attack | Must produce |
|---|---|---|
| **A1** | Stored bundle labelled `p2-038.2` whose `clock_anchor.method` is the **v3** string (and the mirror: `.3` label + v2 method) | strict verify **refuses** `clock_anchor_era_inconsistent`; **not** a byte-match against either estimator. Kills R1-1.4's forgery surface. |
| **A2** | Genuine anchor-v2 bundle, reducer 0.5.2, bounded anchor, clean custody, presented to analysis admission | `clock_anchor_unresolved`. **This test fails today** and is the direct proof of finding #4. |
| **A3** | The same bundle re-derived under v3 and re-presented | still `clock_anchor_unresolved` — pins R1-2.4's closed door |
| **A4** | v3 production bundle presented to `_strict_rich_telemetry_problems` with a **corrupted** `rich_telemetry.jsonl` | returns a problem. Kills the `:1575` fail-open — a confirmation-shaped test (clean file → no problem) passes vacuously today. |
| **A5** | v3 production bundle through the campaign gate; and an anchor-v2 bundle through the same gate | accept / `clock_evidence_invalid`. Reuse the existing `d117_v2_production/strict_seed_bundle` fixture as the **refusal** case rather than regenerating it — a free adversarial fixture. |
| **A6** | Capture whose v2 anchor is `native_intersection_empty` but whose v3 anchor is bounded, run through `environment_admission` | admits (v3 path). Kills R1-3.2; the knife-edge population at `01-root-cause.md:128-129` supplies the real shape. |
| **A7** | `instrument_evidence()` called with `detection.anchor_method is None` | raises. Kills the `or CLOCK_METHOD_V2` default. |
| **A8** | Behavioural pin: monkeypatch `ACTIVE_CAPTURE_ANCHOR_METHOD` to v2 and assert the adapter's emitted label/method follow it | proves the adapter reads the constant rather than re-hardcoding a literal. Mirrors the pattern already used at `tests/test_powermetrics_fiducial.py:290,327`. |
| **A9** | Anchor-era mutation: for each of the 6 cli.py sites and 3 run_campaign sites, mutate the era test to accept the wrong era | at least one test must die per site. This is the mutation-kill check that proves the fan-out has no vacuous coverage. |

### Existing tests that must change (census **[verified by grep]**)

- `tests/test_p2038_production_path.py:396,401,163,439-440` — the direct
  production-path goldens; the `.2` assertions become `.3`. Keep one arm
  asserting a *stored* `.2` bundle still verifies (era retention).
- `tests/test_run_campaign.py:6807,6810` — gate fixture becomes v3; add the v2
  refusal arm.
- `tests/test_powermetrics.py:1141,1446,1461` — patch targets name
  `derive_powermetrics_clock_evidence_v2` in the adapter namespace; retarget.
  `:212` already asserts `ACTIVE_CAPTURE_ANCHOR_METHOD == CLOCK_METHOD_V3`.
- `tests/test_mint_floor_artifact_generalized.py:3532,3553` — re-derivation oracle.
- `tests/test_calibration_bracketing.py:2430-2431` — **keep as-is**; it is
  already the v2-refusal arm and becomes load-bearing under this design.
- `tests/test_reduce.py:2242,3980,3987` — patch targets and the reconstruction-
  registry test; `:4016-4038` already exercises v3/v1 dispatch.
- `tests/fixtures/calibration_live_three_window/scenario.json` — scenario fixture
  naming the v2 method.

### Definition of FULL GREEN

Canonical `python3 -m unittest discover -s tests` returns 0F/0E with the 33
mint-lane reds cured by R2's step-3 landing, `embeds_allowance_once` green via
Step 1, and A1–A9 present and passing. Two independent checks before the ruling
is considered executed: (i) **delta re-audit of every fix round** — the goldens
wave in Step 1 is precisely the shape that has introduced defects twice in this
project's record; (ii) the **mutation kill** A9.

---

## (e) REJECTED ALTERNATIVES

**E1 — Keep `p2-038.2` and version the pipeline identity only in
`clock_anchor.method`.** Rejected: two consumers already dispatch on two
different keys (`cli.py:1266` on the label, `reduce.py:1793` on the method), so a
label that no longer tracks the method silently routes strict verify to the wrong
estimator. Also breaks the `.1→.2` precedent for no benefit.

**E2 — Retire `p2-038.2` (treat it as invalid everywhere).** Rejected: destroys
replay/custody verification for 771 stored bundles **[verified count]** and
throws away the negative-control and knife-edge material the science review
explicitly ordered preserved (`03-cold-science-review.md:108-110`). Retention
costs nothing; the barrier belongs at *claims*, not at *bytes*.

**E3 — Admit stored anchor-v2 bundles to claims after re-deriving them under
v3.** Rejected on cost/benefit and on science: the captures it would rescue are
the ones v3 refuses; the windows are policy-dead; and it would need its own
acceptance generation and freeze. Rejected *explicitly* rather than by silence,
because it is the alternative a future reader will independently invent.

**E4 — Set-membership (`{v2, v3}`) at the campaign gate.** Rejected: this gate
certifies a capture the project just took. Membership is how a stale-adapter
regression ships unnoticed; equality against the active constant is how it gets
caught on the first bundle.

**E5 — Land the flip outside the parked transaction, "then re-freeze once."**
Rejected on verified fact: the adapter is a pinned governed estimator source
(pin `9f165a51…` matches HEAD exactly) so the edit fires r4's
`protocol_or_estimator_byte_change`. Landing it outside would leave a head whose
live acceptance pins are stale — the precise failure bb81323 refused to commit.

**E6 — Narrow the r4 pin set to exclude the adapter, so the flip does not fire
the trigger.** Rejected as self-exemption. Narrowing a governed pin to dodge a
trigger it was written to catch is the mechanism, not the exception.

**E7 — Patch `test_whole_window_selection` (or exempt its fixture) to get
canonical green now.** Rejected: the brief is right that this failure is
evidence, and it is right for a reason the brief does not give — the test is
telling us the *shared calibration helper* mints artifacts whose declared method
and derived method disagree. Exempting it would preserve the two-key
inconsistency at the exact site where it is most visible.

**E8 — Relabel the helper's binding to v3 while leaving its v2 derivation.**
Rejected: fastest green, and it manufactures A1's forgery case inside our own
test corpus.

**E9 — Defer the mechanical claim barrier (R1-2.3) as "already covered by window
policy."** Rejected: `WINDOW_STATUS.md` is a document, not a gate. Reducer 0.5.2
on all 769 window summaries clears the existing D-078 barrier **[verified]**, so
the *only* thing standing between a falsified-estimator bundle and a claim is a
human remembering. Every method transition before this one shipped a mechanical
barrier; this one must too.

---

## (f) EXPLICIT DISAGREEMENTS WITH THE BRIEF'S FRAMING

**F1 — "One currently-failing canonical test … fails from exactly this root."**
*Disagree, with an executed refutation.* The root is the **already-landed
calibration-admission flip** (`calibration_bracketing.py:1039-1040`) meeting a
v2-minting test helper (`test_reduce.py:194,233-235`), not the un-flipped
production adapter. Reverting only the admission comparator in-process turns the
test green **[verified: `Ran 1 test … OK`]**. This matters operationally: the fix
lives in `tests/test_reduce.py`, not in `joulewise/adapters/powermetrics.py`, and
it lands in Step 1 *before* the production flip — a seat that accepted the
brief's framing would sequence it after and be confused when the flip did not
cure it.

**F2 — "the campaign gate (cli.py ~:1644 region)."** *Disagree.* The campaign
gate is `scripts/run_campaign.py:1635` and `:1644`. `joulewise/cli.py:1644` is
inside `_verify_nvidia_smi_raw_to_trace` **[verified by reading it]**. The line
number is right, the file is not — a coincidence worth flagging, because it
would send an implementer to the wrong module with a plausible-looking citation.

**F3 — "54 historical bundles on disk carry the v2 label."** *Disagree — the
count is off by more than an order of magnitude.* **[verified]**: 771 in
`/Users/edr/code/JouleWise/runs_window_*/`, 173 in `/Users/edr/JouleWise-backup/
runs`, 35 in `/Users/edr/JouleWise-window-custody`, 1751 across all of
`/Users/edr` counting iCloud mirrors. Zero in `/Users/edr/code/JouleWise/runs/`
(all 236 there are `p2-038.1`). Separately, 15 instrument-validation candidates
declare the v2 anchor method in `instrument_evidence.json`. I could not find any
population of size 54. This does not change my recommendation — it strengthens
it, since the retention argument (E2) scales with the count.

**F4 — The brief scopes the flip to 4 adapter sites + cli + campaign gate +
contracts.** *Incomplete.* `environment_admission.py:307,351` is a fifth
production site with a real, fail-closed-for-the-wrong-reason hazard (R1-3.2),
and `powermetrics_fiducial.py:1467` is a silent v2 default (R1-3.1). Neither is
named. The brief's instruction to "enumerate file:line yourself, don't trust this
brief" is what surfaced them.

**F5 — The brief frames the question as "what does admission do with stored v2
bundles."** *That is the right question with the wrong presumption.* It presumes
some gate currently *does* something with them. Verified: for claim admission,
nothing does — the D-078 barrier is keyed to reducer version, and all 769 window
summaries are 0.5.2, outside the barrier set. The design's job is therefore not
to *adjust* an admission policy but to *install* one.

**F6 — Framing agreement worth recording.** The brief's "fail-closed is the
default posture" is correct and I have applied it maximally, but I want the
ruling to note *why it was cheap here*: I verified that every strict answer in
this design costs zero live science (stale candidates, historical-import
exclusion, policy-dead windows, prospective-only claim path). Fail-closed is not
always cheap, and future rulings should not cite this one as precedent for
"fail-closed is always affordable."

---

## (g) OPEN QUESTIONS ONLY ED CAN RULE ON

**Q1 (highest value — process, not code).** R1-2.3 installs a mechanical
claim barrier keyed to anchor method. That is a **new claim-admission gate**,
which under D-144's own "big design" test (schema/contract changes,
family-superseding) arguably deserves its own co-design round rather than riding
inside R1. My recommendation is to land it here — it is the flip's direct safety
consequence and separating them ships a window in which the flip is live and the
barrier is not — but the *scoping* call is a magistrate's, not a seat's.

**Q2.** Should the 771 stored anchor-v2 bundles get a **positive, written
disposition** (a registered limitation naming them as permanently non-claim-
bearing on estimator grounds, in addition to the existing per-window policy
grounds), or does the mechanical barrier alone suffice? A written limitation is
stronger for the paper — an examiner asking "what happened to the July/August
corpus" gets a mechanism-level answer rather than a policy citation. Costs one
paragraph; I recommend it, but it publishes a statement about the project's own
data and is therefore Ed's.

**Q3.** `controller.py:1357`'s hardcoded `p2-038.1` seed (R1-3.3) is my
lowest-confidence item: it fires only when telemetry produced no evidence, it is
backend-generic, and I could not establish from the code whether any stored
bundle depends on that exact literal. Options: (a) make it active-era for
powermetrics as I propose; (b) leave it and register the mislabel as a known
quirk; (c) refuse to synthesise a schema label at all. I lean (a), weakly. Good
candidate to hand to the debate rather than the ruling.

**Q4.** r5's issuance is mandatory (R1-4.1) but its **ordinal placement relative
to R2** is a sequencing call with a real cost: if R2's mint-lane fan-out also
moves a pinned estimator source, we pay two reissues instead of one. I have not
designed R2 and did not read the other seat's work, so I can only flag it: the
ruling should check R2's touch set against r4's four pins
(`powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`,
`reduce.py`) and, if they intersect, order the two rulings' implementations so
one reissue covers both.

---

## Interaction with R2 (flagged, not designed)

R2 owns the mint-lane fan-out shape and the `_v2`-vs-`_v3` pack-family question.
My design creates exactly two interactions, both sequencing rather than
substance:

1. **Shared reissue.** Per Q4 — if R2 touches any of r4's four pinned sources,
   the two implementations should share one reissue rather than producing r5 and
   r6.
2. **Barrier vocabulary.** R1-2.3 adds an anchor-era refusal reason to the
   analysis path. If R2's pack-family design introduces its own era marker, the
   two must not become a third and fourth dispatch key — R1-1.4's "one key,
   cross-checked" rule should be stated in the ruling as binding on both.

I did not read, search for, or infer the other seat's output.

---

## Verification record (commands I ran myself)

| # | What | Result |
|---|---|---|
| V1 | `python3 -m unittest tests.test_whole_window_selection -k embeds_allowance_once` | FAIL — `AssertionError: ('calibration_ledger_custody_invalid',)` |
| V2 | Same test with `calibration_bracketing.ACTIVE_CAPTURE_ANCHOR_METHOD` reverted to v2 in-process | **OK** — root cause confirmed (F1) |
| V3 | `shasum -a 256` of the four governed sources vs r4's `estimator_code_sha256` | all four match HEAD exactly (R1-4.1) |
| V4 | Probe: `self_consistent_calibration` under v2 vs v3 deriver | b_fiducial +3.09 µs, bound +3.09 µs, both wider (Step 1) |
| V5 | Recursive census of `p2-038.2` in `metadata.json` across `/Users/edr` | 1751 total; 771 in the primary window roots; 0 in `runs/` (F3) |
| V6 | Parse of all `runs_window_*/*/summary_metrics.json` | `Counter({'0.5.2': 769})` — outside the D-078 reducer barrier (finding #4) |
| V7 | Parse of `runs/calibration_observation_ledger.jsonl` | 76 rows, all `historical-import-v1-*`; 30 valid — all excluded from `registered_valid` (R1-2.6) |
| V8 | `anchor_method_version` census in `runs/instrument_validation/` | 30 occurrences, 15 members, **all v2** (R1-2.6) |
| V9 | `git status --short` in the worktree at start and end | empty both times — read-only discipline held |
