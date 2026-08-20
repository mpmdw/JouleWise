# S1 — CONTRACT LENS (C-028 gauntlet, D-146 stage S1)

Range audited: `8018a4b..1ec5dc4` on `impl/r2-s0-mint-resolver`
(commits `b7e5730` implementation + `1ec5dc4` fix round), worktree
`…/scratchpad/wtS0`. Read-only throughout; no repo writes, no test execution
(execution lens owns that). Every file:line below was opened by me at head
`1ec5dc4` unless marked as a diff-hunk citation.

Spec chain read in full: `13-r1-ruling.md` (S1–S10), `04-r1-design-opus.md`
(§(a)–§(e), B1–B9, A1–A9), `09-r1-debate-opus.md` (R1-2.3′/2.3″, R1-2.6′,
R1-3.3′, E1–E6), `08-r1-debate-terra.md` (F1–F5), `14-r2-ruling.md` S7,
plus the S1 work order (`S1-impl-prompt.md`) for WRITE_SCOPE.

**Verdict: CONFORMANT ON 8 OF 10 CLAUSES, WITH 2 BLOCKERS.** The
capture-side flip, the `:1575` fail-open fix, the r5 issuance and its
neutrality proof are the strongest parts of this diff — I re-derived the r5
neutrality claim myself and it holds exactly. The two blockers are both in
the S3 claim barrier: its per-lane mutation-kill property is unmet for two
of the three lanes, and the shared predicate fails open on the
absent-evidence bundle shape that S8 creates in this very diff.

---

## Clause-by-clause conformance

### S1 — Identity, single mapping, era-inconsistent refusal — **PASS**

- `SCHEMA_FOR_ANCHOR_METHOD` exists once, in `joulewise/uncertainty_evidence.py:25-30`,
  mapping all three methods to their labels. No competing map anywhere.
- Method is the dispatch key at every rewritten site:
  `joulewise/cli.py:1253` (era cross-check), `:1273-1290` (re-derivation
  dispatch on `anchor_method`, not label), `:1585` (rich-telemetry gate keyed
  through the map from the method), `joulewise/environment_admission.py:351`
  (`resolve_anchor_reconstructor(clock_anchor.get("method"))`).
- Label/method disagreement refuses:
  `joulewise/cli.py:1253-1254` appends
  `"strict: uncertainty evidence: clock_anchor_era_inconsistent"`.
  It does not resolve in favour of either — the problem list is non-empty and
  the bundle fails closed regardless of what the subsequent re-derivation does.
- **Grep-clean on inlined method literals**: `grep -rn "powermetrics_native_second" joulewise/ scripts/`
  returns hits only inside `joulewise/uncertainty_evidence.py`. No production
  module re-spells a method string.
- `.1`/`.2` retained: `ANCHOR_RECONSTRUCTION_DERIVERS` (`uncertainty_evidence.py:1351-1355`)
  is untouched by the diff; `resolve_anchor_reconstructor` (`:1357-1362`) untouched.
- Population enumerated to a manifest as ordered: `r5-issuance/p2038-v2-population-manifest.json`
  carries `count: 748`, `len(members) == 748` under root `/Users/edr/code/JouleWise`
  — matches the ruling's "~748 primary". The brief's 54 was correctly not ratified.

### S2 — Strict verify, all six cli.py sites — **PASS**

| Ruling site | Head | Status |
|---|---|---|
| `:108` import | `cli.py:107-115` | `CLOCK_METHOD`, `_V2`, `_V3`, `SCHEMA_VERSION_V3`, `SCHEMA_FOR_ANCHOR_METHOD`, `resolve_clock_evidence_deriver` imported; `derive_powermetrics_clock_evidence_v2` dropped | ✔ |
| `:1233` label set | `cli.py:1237` | `set(SCHEMA_FOR_ANCHOR_METHOD.values())` — derived, not enumerated | ✔ |
| `:1266` dispatch | `cli.py:1273-1290` | `if anchor_method == CLOCK_METHOD` → frozen `.1` replay; `else` → `resolve_clock_evidence_deriver(anchor_method)` | ✔ era-faithful |
| `:1290` fallback replay | `cli.py:1293-1296` | `anchor_method in {CLOCK_METHOD_V2, CLOCK_METHOD_V3}` | ✔ |
| `:1547` trace endpoint | `cli.py:1553-1556` | keyed on `clock_anchor.get("method")` | ✔ |
| `:1575` rich telemetry | `cli.py:1580-1590` | schema gate removed; era set derived from the stored **method** via the map; `.2` and `.3` both replay | ✔ **the blocker is fixed in the flip commit as ruled** |

The A4 corruption case is written as a corruption test, not a confirmation
test: `tests/test_capture_pipeline_era.py:97-118` corrupts `rich_telemetry.jsonl`
on a `.3` bundle and asserts exactly one "does not match" problem. Custody
transcript at `r5-issuance/a4-corruption-probe-transcript.txt`.

Era-faithful stored-method re-derivation preserved: `reduce.py` is not in
the diff file list at all; `ANCHOR_RECONSTRUCTION_DERIVERS` untouched.

### S3 — ONE shared predicate, three consumers CALL it — **PARTIAL: BLOCKER-1, BLOCKER-2**

Structurally correct:
- One predicate: `CLAIM_BEARING_ANCHOR_METHODS` (`uncertainty_evidence.py:1295`)
  + `capture_pipeline_refusal()` (`:1298-1313`).
- All three lanes **call** it, none re-implements it:
  `analysis_engine/inputs.py:3468-3470` (window_evidence_precheck),
  `floor_extraction.py:1927-1929` (`_evaluate_member`),
  `whole_window.py:715-719` (member admission).
- No inlined method literal in any of the three (grep above).

But the two properties the clause was written to guarantee are not delivered
— see BLOCKER-1 (mutation-kill) and BLOCKER-2 (fail-open) below.

### S4 — Refusal vocabulary, exactly four additive sites — **PASS**

`grep -rn "capture_pipeline_superseded" joulewise/ scripts/` gives exactly the
four ruled registry entries plus the S5 calibration lane:

- `analysis_engine/claims.py:134` (`ENGINE_REASON_CODES`) ✔
- `analysis_engine/claims.py:171` (`_NOT_RESOLVABLE`) ✔ — explicitly bucketed,
  not left to the trailing `remaining` extend, exactly as E2 required
- `whole_window.py:199` (`_REDERIVATION_LEAF_REASONS`) ✔
- `floor_extraction.py:190` (`CELL_REFUSAL_CODES`) ✔

All four are pure additions; nothing was removed or reordered.

`clock_anchor_unresolved` is **not** emitted by the new barrier for a bounded
v2 bundle — the new code paths emit only `capture_pipeline_superseded`. The
pre-existing emissions at `analysis_engine/inputs.py:3684` (pre-anchor/
superseded reducer wires) and `:3698` (anchor-shift-**envelope** method
eligibility) are independently derived and untouched, which the debate's
R1-2.3′ explicitly permits ("A bundle may of course carry both, independently
derived"). Conformant.

### S5 — Calibration-lane diagnostics — **PASS (with SF-7)**

- `_capture_pipeline_refusal_for_observation` (`calibration_bracketing.py:1253-1263`)
  classifies before reconciliation.
- Excluded from `registered_valid`: `calibration_bracketing.py:2059`
  adds `and _capture_pipeline_refusal_for_observation(observation) is None`
  to the count, and `:1293-1294` skips the candidate — so counts stay balanced
  and the era rejection can no longer masquerade as
  `calibration_ledger_custody_invalid`. ✔ Exactly R1-2.6′.
- The mixed-era regression asserts the **era** reason, not the custody code:
  `tests/test_calibration_bracketing.py:2137-2179` —
  `assertNotIn("calibration_ledger_custody_invalid", reasons)` plus
  `assertIn({"attempt_id": …, "reason": "capture_pipeline_superseded"}, result["candidate_discovery"]["rejections"])`. ✔

Two sub-findings on the mechanism: SF-6 (unratified artifact key) and SF-7
(predicate polarity) below.

### S6 — Per-consumer admission table — **PASS EXCEPT ONE ROW**

| Table row | Implemented | Evidence |
|---|---|---|
| strict verify: admit v2 historically, byte-exact v2 re-derivation | code ✔, **regression missing** | `cli.py:1273-1290` dispatches era-faithfully, but no test asserts a stored `.2` bundle still passes strict verify — see SF-10 |
| strict verify `.1`: replay-only | ✔ | `cli.py:1274-1290`, the `CLOCK_METHOD` branch is unchanged in substance |
| campaign gate: refuse, **equality against the ACTIVE constant** | ✔ | `scripts/run_campaign.py:1639-1652` — `evidence.get("schema_version") != active_schema` and `clock.get("method") != ACTIVE_CAPTURE_ANCHOR_METHOD`. Equality, never set-membership (E4 upheld). v2 refusal arm at `tests/test_run_campaign.py:6889-6896` |
| reducer: era-faithful, replay-readable not claim-licensed | ✔ | `reduce.py` untouched |
| claims / floors / whole-window: refuse via S3/S4 | ✔ wired, ✖ under-tested | see BLOCKER-1 |
| corpus re-derivation lane untouched | ✔ | `tests/verify_calibration_acceptance_corpus.py` gains only an r5 alias row (`:58-60`); the oracle logic is unchanged. No claim-energy retrofit lane exists anywhere in the diff — E3/R1-2.4 held |

### S7 — Union census — **PASS EXCEPT ONE CONTRACT SITE (SF-1)**

Every code site in the ratified union appears:

- adapter `:525,:540,:563,:755` → `adapters/powermetrics.py` hunks at
  `@@ -522`, `@@ -537`, `@@ -560`, `@@ -752`; import at `@@ -39`;
  `TIMESTAMP_DERIVATION` provenance text rewritten to the p2-038.3 sentence
  (`@@ -71`); `:1832` docstring rewritten (`@@ -1829`). ✔
- six cli.py sites ✔ (table above)
- campaign gate `run_campaign.py:1635,:1637,:1644` ✔
- `environment_admission.py:307,351` ✔
- `powermetrics_fiducial.py:1467` → `:1461-1470`, `or CLOCK_METHOD_V2` killed,
  absent method now `raise ValueError("detection anchor method is missing")`
  (`:1463`) ✔ (R1-3.1)
- `controller.py:1355-1362` ✔ (S8)
- `analysis_engine/inputs.py:188` → head `:190`, `"unresolved"` → `"unknown"`,
  and the `:111` comment corrected to name the stored clock method rather than
  the p2-038.2 schema ✔ (R1-3.4)
- `arm_readiness.py:4143-4149` `_issued_d079` gains `…_r5` (`:4149`) ✔ — terra's
  best catch, landed in the same commit as the flip as required

Contracts, checked as **text vs implemented semantics**, not mere presence:

- `run_bundle_layout.md:645-670` — new `### D-079 additive era` section placed
  parallel to the D-078 section, correctly the ONE home. Content matches the
  code: method is the sole dispatch key; closed method→schema map; retained
  `.1`/`.2` replayable and never relabelled; only v3 is claim-bearing;
  consumers report `capture_pipeline_superseded`; campaign admission is exact
  equality; missing controller evidence carries `capture_pipeline_absent`.
  One inaccuracy — NIT-2.
- `powermetrics_fiducial.md:174` → head `:170-186`: rewritten from the stale
  "equals the v2 literal" to "is a registered stored anchor method and equals
  the measuring bundle's recorded anchor method", and the reducer sentence
  from "re-derives its v2 trace anchor" to "stored-method". Matches
  `reduce.py:1388-1393`'s membership rule and the new dispatch. ✔
- `powermetrics_fiducial.md:144` — **NOT UPDATED. See SF-1.**
- `analysis_plans.md:274` → head `:270-276`: the p2-038.2 label is decoupled
  from the reducer-0.5.2 envelope rule and replaced by "the stored clock
  method owns metadata-era dispatch". Matches
  `analysis_engine/inputs.py:110-114`. ✔
- `docs/specs/c027/p2-038_production_uncertainty_evidence.md:512,733` →
  head `@@ -509` and `@@ -730`: both brought to `.3`, and the worked example's
  `clock_anchor` block was replaced field-by-field with the v3 bounded record's
  key set (`rate_lower/rate_upper/rate_limit_ppm/rate_fit_baseline_s/
  model_departure_allowance_s/admissible_*_epoch_s/arithmetic`), which matches
  `derive_powermetrics_anchor_v3`'s emitted keys. The two-era-stale precedent
  failure is corrected, not repeated. ✔

### S8 — Controller seed envelope — **PASS**

`joulewise/controller.py:1355-1359`: `"schema_version": "p2-038.1"` removed;
envelope is now `{"telemetry_backend": …, "capture_pipeline_absent": True}`.
No era label is synthesized, exactly R1-3.3′. The bundle fails closed at
`cli.py:1237` (`schema_version` absent → "unsupported or missing
schema_version").

No stored-bundle dependency was created: the change *removes* a field rather
than adding one, and the debate's E3 census established zero stored bundles
carry the seed shape. I confirmed no reader requires
`uncertainty_evidence["capture_pipeline_absent"]` — `grep -rn "capture_pipeline_absent" joulewise/ scripts/`
returns only the writer at `controller.py:1358`. It is a pure marker, so
nothing downstream can break on its absence in older bundles.

(This clause is nonetheless the *source* of BLOCKER-2 — it creates a new
evidence shape with no `clock_anchor` that the S3 predicate silently admits.)

### S9 — r5 science-neutral by construction — **PASS, independently verified by me**

I diffed `configs/calibration/calibration_acceptance_d079_v2_n17_r4.json`
against `…_r5.json` leaf-by-leaf with my own recursive walker. **16 differing
leaves, all of them identity/provenance/pins:**

| Category | Leaves |
|---|---|
| identity | `acceptance_id`, `derivation_sha256` |
| provenance | `derivation_notes.generation`, `.predecessor.{acceptance_id,relative_path,file_sha256,derivation_sha256,relationship}`, `.reissue_delta.{changed_estimator_pins×3, science_neutrality_evidence}` |
| governed pins | `prospective_rederivation.estimator_code_sha256` for `adapters/powermetrics.py`, `powermetrics_fiducial.py`, `uncertainty_evidence.py` |

**Zero** differences in `derivation_corpus` (members, n, member table),
`decimal_derivation`, screens, quantiles, bounds, or any scientific scalar.
`reduce.py`'s pin is present and **unchanged** (`1da45a47…`) — correct, since
`reduce.py` was not edited.

Pins verified against head bytes by `shasum -a 256` — all four match exactly:

```
70f47086…  joulewise/adapters/powermetrics.py     == r5 pin
386e8254…  joulewise/powermetrics_fiducial.py     == r5 pin
67e34a1a…  joulewise/uncertainty_evidence.py      == r5 pin
1da45a47…  joulewise/reduce.py                    == r5 pin
```

This survives the fix round: `git diff --name-only b7e5730..1ec5dc4` is
**tests and fixtures only**, so no pinned estimator byte moved after issuance.
No stale-pin hazard.

`r5` file sha256 `92b9c060…` matches `ANCHOR_V3_R5_ACCEPTANCE_BOUND_SHA256`
(`calibration_bracketing.py:187`) and the test pin
(`tests/test_powermetrics_fiducial.py:1560`). `r5.predecessor.file_sha256`
= `dcb3d3ed…` = `ANCHOR_V3_R4_ACCEPTANCE_BOUND_SHA256`, and
`r5.predecessor.derivation_sha256` = `4a0ce072…` = r4's own
`derivation_sha256` — the generation chain self-authenticates.

r4/r3 byte-identical: `git diff --name-status 8018a4b..1ec5dc4 -- configs/`
shows only `A configs/calibration/calibration_acceptance_d079_v2_n17_r5.json`.
No modification to any predecessor artifact. ✔ (R1-4.4)

**Methodology review of `build_r5.py` against the D-079 issuance precedent
— this is the strongest artifact in the stage.** Neutrality is enforced
*mechanically*, not asserted:

- authenticates the predecessor's own `derivation_sha256` before reading it
  (`build_r5.py:45-49`) — predecessor self-authentication, as r4 required;
- copies r4 wholesale and mutates only four keys (`:65-98`);
- then **re-verifies** that every other top-level key (`:100-110`), every
  non-pin key inside `prospective_rederivation` (`:111-117`), and every
  non-provenance key inside `derivation_notes` (`:118-125`) is byte-equal to
  r4, refusing otherwise. This is what makes S9's "science-neutral **by
  construction**" literally true of the artifact;
- refuses when no pin moved (`:61-63`), so r5 cannot duplicate r4;
- recomputes `derivation_sha256` with the same `_canonical_sha256` rule used
  to authenticate the predecessor (`:98`).

`prove_r5_neutrality.py` implements R1-4.3 as ruled: a **bespoke** replay,
not the reissue tool. It re-derives each member's anchor via
`derive_powermetrics_anchor_v3` from the raw plist located by
`artifact_sha256` custody match (`:43-54` — custody-bound, not path-trusted),
then `rederive_detection_from_artifacts` at the flip head, and compares
disposition, `effective_clock_anchor_bound_s`, anchor detail, `b_fiducial_s`
and `projection_evaluated_cell_count` (`:121-131`) — exactly the four
quantities the ruling named. Result: `r5-neutrality-proof.json` = 19 members,
`mismatches: []`, 17 `bounded` + 2 `refused`, matching r4's own "n=17 corpus
plus the two anchor-v3 exclusions". I spot-checked member 0 against the r4
record: `anchor_bound_s 0.0011349971959968978` identical.

One custody gap: SF-8 below.

### S10 + fix rounds — **PASS ON THE NAMED ITEMS, with SF-2**

- **`test_052` pin move carries the era rationale**: `tests/test_reduce.py:3662-3691`,
  `test_052_relabelled_capture_time_disagrees_with_hashed_events` now asserts
  `instrument_calibration_invalid` and carries a five-line "Era rationale"
  comment explaining that the retained D-078 measurement fixture cannot
  authenticate regenerated current-v3 calibration physics. Rationale present
  as required — but the pin lost its discriminating power, SF-2.
- **The v3 staleness lane keeps a pin**: new
  `test_052_v3_measurement_stale_calibration_still_refuses_stale`
  (`tests/test_reduce.py:3692-3733`) drives a real `p2-038.3` production
  fixture with a calibration aged `MAX_AGE_S + 100 s` and asserts
  `_verify_instrument_calibration` returns `("instrument_calibration_stale")`
  plus the reducer-level reason. ✔
- **v2 production fixture byte-identical**:
  `git diff --stat 8018a4b..1ec5dc4 -- tests/fixtures/d117_v2_production`
  is **empty**. ✔ Preserved and reused as a refusal arm
  (`tests/test_p2038_production_path.py:572-583`).
- **New v3 fixture provenance documented and independent**:
  `tests/fixtures/p2038_v3_production/paired_clock_native_records.json:2-3`
  declares `schema_version: joulewise.p2038_v3_production_fixture.v1` and
  states explicitly *"Native endpoint labels and paired clock offsets are
  fixture facts, not values produced by the anchor implementation."* The test
  then asserts the derived anchor against independently-declared `expected`
  values (`tests/test_p2038_production_path.py:445-459`). This is the correct
  independence discipline — the fixture is not a recording of the estimator's
  own output. ✔
- **Goldens moved by the predicted physics**:
  `tests/test_whole_window_selection.py:1296-1297`,
  `EXPECTED_MINTED_ANCHOR_BOUND_S 0.07799298220062004 → 0.07799607349394995`
  = **+3.0913 µs**, matching opus's executed V4 probe prediction of +3.09 µs
  for the v2→v3 helper flip. Independent corroboration that this is the
  ruled physics delta and not an arbitrary refit. ✔
- **The canonical red is cured at its executed root**:
  `test_d079_real_selector_to_real_reducer_embeds_allowance_once` now builds
  through `v3_measurement=True` (`tests/test_whole_window_selection.py:2365-2372`)
  and `self_consistent_calibration` is parameterized with derive-and-declare
  from one method (`tests/test_reduce.py:70,196-203,237`), including an
  internal `AssertionError` if the derived method disagrees with the declared
  one (`:202-203`) — E8's forgery case is closed inside our own corpus. ✔

---

## SCOPE-CREEP SWEEP — **CLEAN AT FILE LEVEL**

All 32 changed paths are inside WRITE_SCOPE or the explicitly approved
fixture expansion. Cross-checked one by one:

- 30 of 32 are literal WRITE_SCOPE entries.
- `tests/fixtures/p2038_v3_production/fake_powermetrics_process.py` and
  `…/paired_clock_native_records.json` are licensed by the work order's hard
  constraint *"add v3 fixtures, never relabel"* (`S1-impl-prompt.md:108`).
- **Zero** writes to `configs/campaigns/`, `arm_readiness_evidence.py`,
  the S0 golden block, `tests/test_floor_mint_estimator.py`, `reduce.py`,
  or any frozen `_v2` pack — all forbidden by the work order and all absent
  from `git diff --name-status`.
- The fix round `b7e5730..1ec5dc4` touched **tests and fixtures only** —
  no source hunk was added after the implementation commit, which is the
  cleanest possible fix-round shape and is why the r5 pins survived.
- One WRITE_SCOPE entry is **unused**: `tests/test_analysis_engine.py`. Its
  absence is exactly the missing lane in BLOCKER-1.

At hunk level I found no unlicensed *source* change. Five *test* hunks are
either unlicensed or under-justified — SF-2 through SF-5 and NIT-6.

---

## FINDINGS

### BLOCKER-1 — S3's per-lane mutation-kill property is unmet for 2 of the 3 claim lanes

**The clause.** Ruling S3, from the debate's off-agenda blocker R1-2.3″:
*"The attack test is a mutation check: flipping the helper's return must kill
at least one test in each of the three lanes independently."* A9 exists
specifically to prove "no vacuous era coverage".

**What is there.** `grep -rn "capture_pipeline_superseded\|capture_pipeline_refusal" tests/`
returns exactly five assertion sites:

| Site | What it covers |
|---|---|
| `tests/test_capture_pipeline_era.py:70-86` | the **helper**, called directly |
| `tests/test_p2038_production_path.py:572-583` | the **helper**, called directly on the retained v2 fixture |
| `tests/test_whole_window_selection.py:2536-2569` | the **whole_window lane** — real `AuthenticatedConsumptionSession`, asserts `capture_pipeline_superseded` in `session.refusal_reasons` ✔ |
| `tests/test_calibration_bracketing.py:2178` | the **S5 calibration lane** (not one of the three) |

**What is missing.** No test asserts `capture_pipeline_superseded` arriving
from `floor_extraction.py:1927-1929` or from
`analysis_engine/inputs.py:3468-3470`. `tests/test_floor_extraction.py`
contains **zero** references to any anchor method
(`grep -rn "CLOCK_METHOD\|anchor.*method" tests/test_floor_extraction.py` is
empty). `tests/test_analysis_engine.py` is in WRITE_SCOPE and was never
touched.

**Consequence.** Delete either three-line barrier hunk — the fail-open
mutation, which is the dangerous direction — and the suite stays green. Two
of the three lanes have the barrier *wired* but *unpinned*. The floor lane is
precisely the one terra caught and opus conceded as "a real gap in my design"
(`09-r1-debate-opus.md:187`), and it carries its **own** independent
reducer-version barrier, so nothing else in that lane covers anchor era.

The implementation report's A9 table lists a single entry for this predicate
("Claim-barrier v3 method predicate → `test_claim_barrier_rejects_every_non_v3_stored_method`"),
which is the helper unit test — i.e. the report itself shows the per-lane
property was not established.

**Fix.** Two lane-level regressions: a floor-extraction member with a stored
v2 anchor asserting `capture_pipeline_superseded` in the cell refusals, and a
`window_evidence_precheck` case asserting it in `result["reasons"]`. Then
re-run the A9 sweep against those two hunks specifically.

### BLOCKER-2 — the shared claim predicate fails OPEN on the absent-evidence shape that S8 creates in this same diff

**The code** (`joulewise/uncertainty_evidence.py:1298-1313`):

```python
def capture_pipeline_refusal(metadata: Mapping[str, Any]) -> str | None:
    if not isinstance(metadata, Mapping):
        return None
    uncertainty = metadata.get("uncertainty_evidence")
    clock_anchor = (
        uncertainty.get("clock_anchor") if isinstance(uncertainty, Mapping) else None
    )
    if not isinstance(clock_anchor, Mapping):
        return None          # <-- fail-OPEN
    return (
        None
        if clock_anchor.get("method") in CLAIM_BEARING_ANCHOR_METHODS
        else "capture_pipeline_superseded"
    )
```

Three early returns admit a bundle: non-mapping metadata, missing/non-mapping
`uncertainty_evidence`, missing/non-mapping `clock_anchor`. In every one of
those cases the bundle's capture method is *not* in
`CLAIM_BEARING_ANCHOR_METHODS`, yet the barrier returns `None`.

**Why it matters now rather than hypothetically.** S8, implemented in this
same diff at `joulewise/controller.py:1355-1359`, **creates** an evidence
envelope with no `clock_anchor` at all:

```python
self._uncertainty_evidence = {
    "telemetry_backend": self._telemetry.name,
    "capture_pipeline_absent": True,
}
```

So the stage simultaneously introduces a new bundle shape and a claim barrier
that silently admits it. The clause this violates is R1-2.3's own wording —
the barrier applies *"regardless of reducer version, regardless of bounded
status, regardless of custody"* — and the project's stated fail-closed
posture, which R1-3.1 applied to the exactly-parallel case one file away
(`powermetrics_fiducial.py:1463` now **raises** on an absent anchor method
rather than defaulting).

**Mitigation that keeps this from being a live claim hole today:** all three
lanes have independent downstream gates (`_current_strict_summary` in
whole_window, the STRICT-VALID requirement in floor extraction, other precheck
reasons in inputs), and `cli.py:1237` fails the seed shape closed at strict
verify. So this is a defence-in-depth failure in the designated single
predicate, not a demonstrated admitted claim. I still rate it blocker because
the whole point of S3 was to make **one** mechanical predicate authoritative
rather than relying on a human remembering which other gate happens to cover
the case (E9's reasoning applied to the barrier itself).

**Fix + one design question for the magistrate.** Invert the guards so any
metadata that does not positively present a claim-bearing method refuses. The
open question is *which* reason: `capture_pipeline_superseded` is semantically
wrong for absent evidence (the same objection that produced S4 in the first
place), so this may want `capture_pipeline_absent` as a second registered
engine reason — which is a vocabulary addition and therefore a magistrate
call, not a lieutenant one.

### SHOULD-FIX

**SF-1 — `docs/contracts/powermetrics_fiducial.md:144`: ratified S7 census
site absent from the diff, and the text is now affirmatively false.**
Ruling S7 names "`powermetrics_fiducial.md` :144/:174"; B8 describes :144 as
"binding vector names the v2 method as *the* value". Only :174 was fixed.
Head `:143-144` still reads:

> `powermetrics_sha256`, `sampling_interval_ms`, `anchor_method_version`
> (`powermetrics_native_second_censored_intersection_v1`), `mlx_version`,

That value is now **refused** by live code: `instrument_evidence` emits
`detection.anchor_method` (`powermetrics_fiducial.py:1470`) and
`load_calibration_candidate` requires equality with
`ACTIVE_CAPTURE_ANCHOR_METHOD` (`calibration_bracketing.py:1128-1129`). This
is the only S7 census site missing from the diff, no justification was
offered, and the contract is the ONE home read by the advisor. One-line fix,
mirroring the wording already used at `:174`.

**SF-2 — the F1 relabelled-capture-time attack is no longer pinned.**
`tests/test_reduce.py:3662-3691`. The test still documents the F1 defect shape
("an attacker moved only the declared capture time far into the future and
re-hashed both evidence and custody manifest … immutable calibration event
bytes still prove the lie") but now asserts `instrument_calibration_invalid`,
which the era mismatch between the retained `d078_r01` measurement fixture and
the regenerated v3 calibration produces **independently of the attack**.
Removing the `evidence["capture_wall_time_s"] += 10_000_000.0` line — or
removing the defence itself — leaves the assertion satisfied. The test can no
longer fail for the reason it documents. Note the sibling
`test_052_shifted_event_clock_cannot_relabel_calibration_fresh`
(`tests/test_reduce.py:3819-3820`) retains discriminating power because it
also asserts `assertNotIn("instrument_calibration_stale", reasons)`. Fix:
rebuild the F1 arm on the v3 fixture — the new
`_v3_measurement_bundle_with_calibration` helper (`tests/test_reduce.py:3053-3105`)
makes it cheap — or add the control arm that proves the assertion still
discriminates.

**SF-3 — a fix-round blocker regression's setup assertion was relaxed in the
permissive direction on an unproven rationale.**
`tests/test_run_campaign.py:8635-8641`, inside
`test_missing_final_attempt_telemetry_fails_closed` (docstring: *"Fix round 1
(blocker): absent retried telemetry fails closed"*):
`expected_strict_valid=False` → `True`. That parameter is a real assertion —
`self.assertIs(evaluation.strict_valid, expected_strict_valid)` at
`tests/test_run_campaign.py:8570`. So the diff now asserts that a bundle whose
`rich_telemetry_idle_attempt_2.jsonl` has been **deleted** is strict-VALID,
where previously it was strict-INVALID. The inline justification ("the
final-attempt pairing is a whole-window admission concern, not a generic
bundle-layout requirement") is plausible — `joulewise/cli.py` indeed never
references `rich_telemetry_idle_attempt_*`
(`grep -rn "rich_telemetry_idle" joulewise/*.py` hits only
`environment_admission.py:78-80`, `salvage_dangler.py:539-541`,
`whole_window.py:3836-3838`, `publication_privacy.py:273`) — but it is
asserted, not demonstrated. No S-clause licenses this change. Required: state
which strict problem previously fired and which hunk removed it. If the
removal is legitimate, keep an arm proving the missing attempt-2 file is still
caught somewhere. The test's own blocker assertions (`decision == "failed"`,
`cpu_baseline_telemetry_missing`) are unchanged, so the blocker property
itself is intact.

**SF-4 — an unremarked capture-yield regression: a real production shape moves
from `bounded` to `unknown` under v3.**
`tests/test_powermetrics.py:2111-2114`,
`clock_anchor["status"]` expectation `"bounded"` → `"unknown"` in the
dropped-final-unparseable-frame / truncated-tail run. Unlike every other era
expectation flip in this diff, this one carries **no comment**. It is very
likely legitimate (the cold science review ruled v3's refusals "the correction
working"), but it is a fact the magistrate should be told explicitly: the flip
converts at least one previously-bounded capture shape into an unresolved
anchor. It also **compounds** with the `inputs.py:190` fix in the same diff —
now that `anchor.get("status") == "unknown"` is live rather than dead, that
same shape is additionally `anchor_fallback_member_unusable`. Two
independently-licensed changes intersecting on one bundle shape, with no
combined note anywhere. Fix: a one-sentence rationale at the assertion and a
line in the S1 report.

**SF-5 — an unlicensed bound relaxation.** `tests/test_powermetrics.py:1072`,
`self.assertLess(...)` → `self.assertLessEqual(...)` on
`operational_now[0] <= anchor_lag_s + 2.0/power_hz + 0.25`. A strict
inequality became non-strict, i.e. the exact-boundary case that previously
failed now passes. No clause licenses it and no comment explains it. Either
re-derive the bound under v3 physics or restore the strict comparison.

**SF-6 — `candidate_discovery` is an unratified additive key in a governed
artifact, and it changes the verdict-conflict surface.**
`joulewise/calibration_bracketing.py:2096-2107` adds
`result["candidate_discovery"] = {"rejections": [...]}` to the
`joulewise.instrument_calibration_bracket.v1` dict. S5 requires the rejection
to be *reported*; it does not authorize a new artifact field. The bracket dict
is compared by exact equality at `joulewise/whole_window.py:4094-4098`
(`dict(stored_calibration_bracket) != calibration_bracket` →
`whole_window_verdict_conflict`), and the re-derivation lane at `:4084-4092`
calls `calibration_bracket_for_bundles` **without** `ledger_snapshot`, so the
key can never appear on that side. Any stored verdict minted with superseded
observations present would therefore conflict on re-verification. Live impact
is currently nil — all 76 ledger rows are `historical-import-v1-*` and are
excluded — but this is a governed-artifact schema surface and should either be
ratified or moved to the reasons tuple / a non-artifact diagnostic.

**SF-7 — the calibration lane installs a SECOND era predicate with inverted
polarity.** `joulewise/calibration_bracketing.py:1258-1263` classifies via
`if method == CLOCK_METHOD_V2` — a **denylist** — while the shared helper uses
`method in CLAIM_BEARING_ANCHOR_METHODS` — an **allowlist**. The comment
("Ledger validation owns malformed/unregistered binding failures") is a
reasonable defence, but the divergence is real: a ledger-valid observation
whose `anchor_method_version` is `CLOCK_METHOD` (v1) or any future v4 passes
the era pre-filter, then fails inside `_candidate_from_observation`, which
`return ()`s the whole discovery (`:1300-1302`) and reproduces the exact
`calibration_ledger_custody_invalid` masquerade S5 was written to abolish —
just for a different era. Given that the debate's off-agenda blocker was
specifically *"three era gates with no shared predicate — the exact defect
class that created this ruling"*, a second predicate of opposite polarity in
the same stage deserves either a shared observation-shaped helper or an
explicit ruling that the v2-only denylist is intended.

**SF-8 — the S9 neutrality proof's reference basis is not in the preserved
custody copy.** `prove_r5_neutrality.py` compares against an
`R4_DERIVATION_RECORD` supplied as `argv[2]`. The path appears only inside the
implementation report's verification block
(`S1-impl-report.md:104`:
`/private/tmp/claude-501/…/d6206bd4-…/scratchpad/r4-derivation.json`), i.e. a
**previous session's ephemeral `/private/tmp` scratchpad**. The file does
still exist today (38 875 bytes, 19 rows, sha256 `ad923506…`, and I confirmed
member 0's `effective_clock_anchor_bound_s` matches the proof), so the claim
is currently auditable — but neither the file, its path, nor its sha256 is
recorded in `…/scratchpad/r5-issuance/` alongside the proof it authorizes.
The reference side of a mandatory neutrality proof should not live only in a
volatile temp directory. One `cp` plus a sha256 line in the transcript.

**SF-9 — A6 is implemented as a mock-based dispatch assertion, not as the
ruled attack.** A6 (`04-r1-design-opus.md:468`) specifies: *"Capture whose v2
anchor is `native_intersection_empty` but whose v3 anchor is bounded, run
through `environment_admission` → admits (v3 path)."*
`tests/test_environment_admission.py:16-67` instead patches
`joulewise.uncertainty_evidence.resolve_anchor_reconstructor` to a stub and
asserts `resolver.assert_called_once_with(CLOCK_METHOD_V3)`. That is a valid
mutation-kill for the dispatch site (a hardcoded v2 would fail it), and the
test's own comment describes the knife-edge shape it is standing in for — but
the knife-edge behaviour itself is mocked away, so the "correct-looking refusal
for a wrong reason" hazard that motivated R1-3.2 is never exercised. Worth one
real-shape arm.

**SF-10 — S6's first row has no regression.** No test asserts that a stored
`p2-038.2` bundle still **passes** `verify --strict`. Opus's fan-out asked for
exactly this ("Keep one arm asserting a stored `.2` bundle still verifies (era
retention)", `04-r1-design-opus.md:476`) and E2 rests the entire retention
argument on it (748 bundles' replay/custody value). The flip rewrote the
dispatch that delivers it (`cli.py:1273-1290`), so this is the property most
able to break silently. The retained `d117_v2_production/strict_seed_bundle`
fixture is right there and is currently used only as a refusal arm.

### NITS

- **NIT-1 — `docs/contracts/run_bundle_layout.md:492`** still says
  "`uncertainty_evidence` with schema `p2-038.1`" in the base P2-038 section.
  B8 listed it, so it is inside the ratified contract list — but I judge it
  **justifiably absent**: the D-078 era section at `:511` established the
  precedent that the base section describes the original era and additive
  sections layer on top, and D-078 did not touch `:492` either. Flagging only
  so the omission is a recorded decision rather than an oversight.
- **NIT-2 — the new contract section overstates one refusal.**
  `run_bundle_layout.md:653-655` says "a crossed, **missing**, or unknown pair
  refuses with `clock_anchor_era_inconsistent`". For the both-missing case
  (`schema_version` absent and `clock_anchor.method` absent),
  `cli.py:1253` evaluates `SCHEMA_FOR_ANCHOR_METHOD.get(None) != None` →
  `False`, so no era-inconsistent problem is raised; the bundle refuses under
  "unsupported or missing schema_version" instead. Crossed pairs and
  single-sided absences do behave as documented. Reword or extend the check.
- **NIT-3 — a third era set is spelled inline, twice.**
  `cli.py:1293` and `cli.py:1554` both enumerate
  `{CLOCK_METHOD_V2, CLOCK_METHOD_V3}` ("current-era native anchors"). These
  are constants, not literals, so the grep-clean claim holds — but S1's "one
  canonical mapping" discipline argues for a named
  `NATIVE_ANCHOR_METHODS` constant beside `SCHEMA_FOR_ANCHOR_METHOD`,
  especially since a v4 would have to find both sites by hand.
- **NIT-4 — dead parameter.** `_powermetrics_trace_endpoint_s(evidence, clock_anchor)`
  (`cli.py:1543-1544`) no longer reads `evidence` after the method-keying
  change; both call sites (`:1526`, `:1601`) still pass it.
- **NIT-5 — fragile binding.** `superseded_observations`
  (`calibration_bracketing.py:2042`) is bound only inside the `else` branch;
  the guard at `:2096` is safe purely by `and` short-circuit on
  `ledger_snapshot is not None`. Initialize it to `[]` before the branch.
- **NIT-6 — the evidence-authoring fixtures retreated wholesale to v2.**
  `tests/test_powermetrics_fiducial.py:922-930` now stamps
  `anchor_method=CLOCK_METHOD_V2` on every synthetic `EvidenceTests` detection
  (plus `:683`, `:736`, `:1749`, `:1791`, `:2404`, `:2447`). Era-faithful and
  minimal, but it leaves the *new-evidence authoring* lane exercising the
  superseded era by default with a single v3 assertion at `:2500`. Prefer v3
  as the default and keep v2 arms explicit.
- **NIT-7 — `analysis_plans.md:272` line overruns** the file's wrap width after
  the edit ("...contrasts as the deterministic..." now trails a long line).
- **NIT-8 — refusal-code semantics at the campaign gate.** A retained v2
  bundle is refused as `clock_evidence_missing`
  (`scripts/run_campaign.py:1640-1643`, asserted at
  `tests/test_run_campaign.py:6896`) although the evidence is present and
  merely of the wrong era. Pre-existing code shape, unchanged by the ruling,
  but the same semantic objection that produced S4 applies.

### Carried verification gap (execution lens owns it)

`S1-fix1b-report.md` flag F1 records
`tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_default_only_v2_output_remains_byte_identical_to_golden_oracle`
still erroring with `MintError`. The work order permits only the stale-golden
chain to remain red at S1 (goldens move at S2), so this appears in-bounds —
but the classification is the implementer's own and has not been independently
confirmed. Noting for the execution lens rather than raising it as a contract
finding.

---

## What I checked and found clean (recorded so it is not re-checked)

- r5 vs r4 leaf-by-leaf diff — 16 leaves, all identity/provenance/pins, zero
  scientific deltas (my own walker, not the implementer's script).
- r5 pins vs head bytes — all four match; fix round moved no pinned source.
- r3/r4 untouched; r5 is the only new config.
- Generation chain self-authenticates (file sha, derivation sha, predecessor
  derivation sha all cross-check).
- `build_r5.py` refuses any non-provenance delta by construction — reviewed
  against the r3/r4 issuance precedent it cites.
- 19/19 neutrality members, 0 mismatches, 17 bounded + 2 refused.
- Population manifest = 748, matching the ruling.
- `tests/fixtures/d117_v2_production` byte-identical.
- No inlined anchor-method literal anywhere in `joulewise/` or `scripts/`.
- Exactly four additive reason-code registrations.
- `reduce.py` and `ANCHOR_RECONSTRUCTION_DERIVERS` untouched.
- Zero out-of-scope file writes; fix round is tests-and-fixtures only.
- Goldens moved by exactly the predicted +3.09 µs.
- A8 **is** satisfied — `tests/test_powermetrics.py:1168-1199`
  (`test_adapter_dispatches_the_active_capture_method_constant`) patches
  `ACTIVE_CAPTURE_ANCHOR_METHOD` to v2 and asserts the resolver follows,
  proving the adapter reads the constant rather than a re-hardcoded literal.
