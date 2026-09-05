# Opus refuter (CONTRACT lens) — exhibit 17 final ruling, packet 17

Worktree `JouleWise-wt-packet-ruling-17` @ `fffd9333`. Independent of the cold judge's
file. Every file:line and count below was opened or executed this session.

**Packet validation:** `scripts/validate_gate_packet.py` → `"result":"PASS"`
(`coldgate-validator-receipt/v2`; packet `73d2a52a…6419`, charter `099de884…5d81`; all 37
exhibit digests observed == expected).

| Q | Verdict |
|---|---|
| Q-17-1 | AMEND |
| Q-17-2 | NOT REFUTED |
| Q-17-3 | AMEND (arithmetic exact; census wrong) |
| Q-17-4 | AMEND |
| Q-17-5 | AMEND |
| Q-17-6 | AMEND |
| Q-17-7 | AMEND |

---

## Q-17-1 — D-078 estimand / clause 11 / enclosure — **AMEND**

A and B not refuted: no contract asserts a physical within-record estimand, and the
withdrawal preserves the two roles fixed by clause 11's SINGLE-COUNT DISCIPLINE.

**Defect 1 — the five conditions omit stored current-era summaries.** The seat emits
`phase_partial_record_enclosure_j` non-null on the **current** `0.5.2`/`0.6.2` wires
(`30-…seat-report.md:163-188`) with no version bump. Strict validation compares a
fresh re-reduction to the stored summary (`joulewise/cli.py:573-583`); tolerance is
chosen by provenance in `_strict_reducer_version_dispatch` (`cli.py:829-870`), and a
summary at `SUMMARY_REDUCER_VERSION` gets `absent_tolerance = set(ADDED_DURING_0_5_0)`,
`tolerate_fresh_nulls=False` (`cli.py:845-846`). A post-0.5.2 field is not in that set.
Executed:

```
_strict_summary_differences({'a':1.0,'phase_partial_record_enclosure_j':{'decode':2.0},
  'phase_partial_record_enclosure_reason_code':None}, {'a':1.0})
-> ['phase_partial_record_enclosure_j','phase_partial_record_enclosure_reason_code']
```

Every already-stored 0.5.2/0.6.2 summary therefore fails `strict: … does not match a
fresh re-reduction`. The only escapes are an added absent-tolerance entry — forbidden by
condition (iii) — or re-reduction, which changes bytes and breaks custody pins. The
seat's `existing_fields_changed=0` proof (`30-…:113-128`) pops the added keys from a
fixture re-reduction and is silent on stored bundles. Add condition (vi):

> (vi) the enclosure field is minted on a NEW reducer version (`0.5.3`/`0.6.3`, added
> to the recognized list at `docs/contracts/run_bundle_layout.md:781-784`); or, if added
> to `0.5.2`/`0.6.2`, an executed inventory shows no stored 0.5.2/0.6.2 summary outside
> `tests/goldens` is subject to strict re-reduction and no custody-pinned bundle is
> re-reduced to acquire it. No entry may be added to `ADDED_DURING_0_5_0` or any
> absent-tolerance set.

**Defect 2 — condition (iv) misnames the artifact; the withdrawal is ambiguous.** There
is no "per-version roster": the additive-field table in `run_bundle_layout.md` has columns
Field/Location/Contract and no version column; version scoping lives in each row's
Contract prose (e.g. "Reducer 0.4.0 writes no generic `request` alias"). And
"permanent-dominance assertions" does not resolve against clause 11's two distinct
permanence sentences, nor touch its B-45/L11-SF3 and B-47/L11-N2 caveats. Replace:

> (iv) the field's row in the additive governed-summary table of
> `docs/contracts/run_bundle_layout.md` states in its Contract cell that it is emitted
> only by reducers `0.5.2`/`0.6.2` and later and is absent from every earlier arm;

> Withdraw clause 11's sentence "the corner-widened maximum is exactly the largest false
> effect this instrument can produce" and its sentence "Because repeatability will always
> beat attribution here, the refusal is STRUCTURALLY PERMANENT: no future phase corpus
> can pass it and there is nothing to re-collect around", retaining both as conditional
> on the registered timing domain. The 2026-08-24 B-45 and B-47 caveats stand unmodified.

---

## Q-17-2 — D-165 physics and versioned relabel — **NOT REFUTED**

The `.v1 → .v2` relabel renames a rationale, not a frozen number: ratios, thresholds,
census, arithmetic and branch restrictions are preserved verbatim, v1 bytes/meanings are
preserved, and absolute `R_cm` keeps value `not_applicable` with a changed reason. Head
still emits `.v1` (`joulewise/dominance_closeout.py:50-66`), so the mint is prospective
and correctly scoped. No frozen result moves. Nit: name D-165 in `docs/decision_log.md`
as the home for "later changes require prospective registration".

---

## Q-17-3 — D-083 arithmetic and migration — **AMEND**

**B is exact; I hunted a counter-example and there is none.**
`joulewise/analysis_engine/artifact.py:665-675` enforces `decision = [metrology_lo −
total, metrology_hi + total]` with `total ≥ 0`, so decision ⊇ metrology.
`claims.py:336-368` requires for `direction_supported`: `abs(estimate) > floor`
(line 337: `<= floor` sets `effect_not_above_floor`) **and** zero strictly outside both
intervals (lines 362-365). With metrology `estimate ± h` and widening `B ≥ 0`, zero
outside metrology ⟺ `|est| > h`; zero outside decision ⟺ `|est| > h+B`, which subsumes
it. Conjunction = `|est| > max(F, h+B)`, strict, as written. The only reachable
asymmetric case (decision contains 0, metrology does not) is correctly failed as
`deterministic_bound_obscures_direction` / `not_resolvable` (`claims.py:366-368`). The
addendum's carve-outs (`adjusted_rejected`; the `_NOT_ESTIMABLE`/`_NOT_RESOLVABLE`/
`_UNRESOLVED` sets) are present.

**The migration census in ruling Q3 is wrong on three counts:**

1. Not "seven exact-equality sites" but **nine** in `joulewise/`:
   `detection_floor.py:3345,3834,4104`; `analysis_engine/__init__.py:258,295`;
   `analysis_engine/artifact.py:490`; `analysis_engine/inputs.py:4336,4468`;
   `analysis_engine/claims.py:304` — plus a tenth producer-side expectation at
   `scripts/mint_floor_artifact.py:1914`. All compare the whole `single_count_discipline`
   OBJECT, not the id string, so a `.v2` object breaks ten sites, not seven.
2. "14 rehearsal JSONs regenerated" matches nothing at this head:
   `docs/paper/fill-rehearsal/` holds **17** JSONs, of which **4** carry the key.
3. Two carriers are unnamed: root `df-ph-decode-floor-mint1.json` and the generated
   `docs/site/adapter_contracts.html` (mirror of `adapter_contracts.md:623`, correctly
   inside the cited 618-637).

Replacement for the Q3 parenthetical:

> (the ten exact-equality consumers — `joulewise/detection_floor.py:3345,3834,4104`;
> `joulewise/analysis_engine/__init__.py:258,295`; `…/artifact.py:490`;
> `…/inputs.py:4336,4468`; `…/claims.py:304`; `scripts/mint_floor_artifact.py:1914` —
> which compare the whole object, not the id; `docs/contracts/adapter_contracts.md:618-637`
> and its generated `docs/site/adapter_contracts.html`; and the four
> `docs/paper/fill-rehearsal/dominance-reproduced-*.json` plus root
> `df-ph-decode-floor-mint1.json` regenerated)

---

## Q-17-4 — D-166 prompt-0 amendment and supersession — **AMEND**

A not refuted: the pinset guard at
`configs/campaigns/d117_contrast_v5/generate_configs.py:942-951` compares the profile's
full prompt projection against the rendering pinset's, so per-block selection of prompt 0
leaves `prompt_set_sha256`, tokenizer, chat-template and thinking-off pins (`:952-957`)
intact. B correctly retains 16-F2.

C is **incomplete**. `expected_pack_paths()` (same file) enumerates what the pack writes;
the addendum's list ("configs, identities, projections and custody pins") omits
`order_manifest.json` (root and per-stage), `plan_tree.json(.sha256)`,
`calibration_plan.json(.sha256)`, `analysis_manifest_v3.json`,
`consumer_family_declaration.json`, and every per-stage ABBA run JSON. It is also silent
on the D-138 question the generator itself raises:
regeneration must either replay frozen bytes in preserve mode or mint a SUCCESSOR family
(`GenerationIdentity`; `acceptance_pin()` at `:399-430`; `PREDECESSOR_ACCEPTANCE` vs
`SUCCESSOR_ACCEPTANCE`, which "never share a pin"). Append:

> Regeneration runs under a successor generation identity (target ordinal ≥ 2,
> `SUCCESSOR_ACCEPTANCE` pin); the frozen `_v5` ordinal-1 bytes are never rewritten. The
> superseded set is exactly `expected_pack_paths()` for the pack — including
> `order_manifest.json`, `plan_tree.json(.sha256)`, `calibration_plan.json(.sha256)`,
> `analysis_manifest_v3.json`, `consumer_family_declaration.json` and every per-stage run
> JSON — together with the identity pins, the analysis-semantics projection, the custody
> pins over the above, and the clone proof. A generated inventory of that set is attached
> to the supersession record before collection.

---

## Q-17-5 — scope freeze and dated cuts — **AMEND**

Individual TASKS are bounded ("bounded acceptance and a stop time"), but the RULE is not:
"Until submission" names no date, and there is no un-park path if a parked item becomes
necessary for a selected figure. The dated cuts also overlap: "last useful acquisition
night 8 September" leaves no interval for reduction, extraction, verdicts and fill before
"content freezes 9 September". Replace the last three sentences:

> Establish desk readiness and feasible acquisition scheduling by 6 September; the final
> useful acquisition is the night of 8 September, whose reduction, extraction and verdicts
> must complete before content freeze at 23:59 on 9 September, with fallback selected at
> 12:00 on 9 September if they have not; 48 hours after the freeze are reserved for
> verification and reading. This rule expires at submission or on 11 September, whichever
> is earlier. A parked item is un-parked only by a written finding that it is necessary
> for a named selected figure, table or refusal sentence, recorded in the decision log.
> Authoritative earlier deadlines advance these cuts. Missing evidence selects fallback,
> never empirical refusal.

---

## Q-17-6 — refusal branch without a receipt family — **AMEND**

A–C are contract-sound. D is not ratifiable verbatim: the mechanism it binds to — "the
seam's `whole_window_verdict` ref" — rests on D-173, whose index row reads "**proposed**
(magistrate, **provisional**, 2026-09-04 … **pending the paper-supply cold gate before any
supplier merges**; Ed may veto)", and whose normative module is absent at this head: `ls
joulewise/paper_custody.py` → *No such file or directory*. Ratifying Q6 as written
pre-ratifies an ungated contract. The record itself is real and frozen elsewhere:
`joulewise/analysis_manifest_v3.py:1109,1142`, schema
`joulewise.idle_admission_whole_window_verdict.v1` at `:1206,1229`. Replace:

> …rendered only from verified failed production evidence bound to model, window, basis,
> membership and governing row through the `whole_window_verdict` record of
> `joulewise/analysis_manifest_v3.py` (schema
> `joulewise.idle_admission_whole_window_verdict.v1`). Routing that read through the D-173
> custody seam is required only once D-173 passes its own paper-supply cold gate; until
> then the sentence renders through the manifest ref directly, and no supplier merges
> under D-173.

The absence of a receipt family is not itself a contract defect: D-161 retires guards
whose only defended actor is the trusted operator.

---

## Q-17-7 — legacy-L1 route census and the D-161 fence — **AMEND**

A–B are consistent with the live D-161 row, but only via a clause the one-liner does not
name, and as written the addendum reads against D-161's direction: D-161's subject is the
threat-model PRUNE (retiring operator-only fail-closed guards), while this addendum ADDS
a permanent fence. It is admissible under D-161's preserved carve-out — "fail-closed
STAYS where the failure is PHYSICS/EVIDENCE or PRE-REGISTRATION"
(`decision-log-D-161-index-L207.txt`). Cite it:

> D-161 (addendum, 2026-09-04): under the preserved physics/evidence carve-out, the rpt001
> capstone profile is a closed publication route for legacy energy values; every producer
> under it emits void placeholders, and regeneration cannot reopen it. This fence is
> evidence-side, not operator-adversary, and is out of scope for the THREAT-MODEL-PRUNE-01
> downgrade sweep.

C is otherwise sufficient as a fence statement; the census evidence is absent from the
manifest (§13.6), conditioning this AMEND but not forcing REFUSE on the contract lens.
