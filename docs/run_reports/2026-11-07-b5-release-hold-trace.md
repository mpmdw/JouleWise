# B5 release hold on dry-j: blind trace (structure only)

**Date:** 2026-11-07 (Air). **Seat:** blind trace under DLE-2 (`docs/analysis/b5/DEVIATION-LOG.md`;
`docs/analysis/b5/RELEASE-RUNBOOK-lean.md` §2). **Inputs read:** the release output's `comparison.json` only,
through `docs/process_traces/2026-11-07-b5-release-trace/extract_blind.py` (`python3 -I`). That script emits only
leaf identifiers, verdicts, reasons, types (number, string, bool, null), string or bool match, and a coarse
relative-difference class (`identical`, `<1e-6`, `<1e-3`, `<1e-1`, `>=1e-1`, `one_side_zero`). This report holds no
value, difference, sign, ratio, estimate, interval, p-value or outcome word. Code was read at `d271fb476` (main)
and `929fc65c9` (`b5/analysis-r2`). Their `joulewise/b5_analysis`, `joulewise/b5` and `joulewise/analysis_engine`
trees are identical.

**Run under trace.** `scripts/release_b5.py` on dry-j custody, pinned analysis commit `929fc65c9`, checkout
`d271fb476`, and bars sha `2f65bba2…`. Stage (a) verified. The recompute was clean. The comparator disagreed:
1,001 failing rows in 11 families.

## 1. Verdict on the lead hypothesis: refuted

The hypothesis was that the recompute reuses collection-time clock anchors and window edges while L9 re-derives
them, so that `window_edge_s` differs everywhere and cascades. The structure refutes it:

- **Every member with values on both sides has bit-identical request edges.** For all 346 such members, the
  comparator compares the edges as exact integer nanoseconds under the `count` family (`meter/<w>/<rid>/request/window_ns/{start,end}`):
  692 rows, all `identical`, all AGREE. The `meter_j`, `meter_w` and `meter/n` rows of those members also all
  agree.
- **The 22 `window_edge_s` rows are an artifact of which branch the comparator takes.** The comparator routes a
  member's edges to `window_edge_s` only when the recompute's own row lacks
  `window_basis == "controller_stamps"` (`scripts/compare_b5_recompute.py:3403-3409`). That happens only for the
  11 members whose recompute request row is the unavailable stub (defects D3 and D4 below). In 18 of the 22 rows
  both sides are null; in 4, L9 has a number and the recompute has null. No edge is compared there.
- **The value disagreements sit in members whose edges agree.** The rail and ρ differences occur in 33 members,
  and all 33 have identical `window_ns` rows. The 357 `battery_term` failures on `machine/` rows occur in every
  member. Neither pattern follows the window edges.

## 2. Per-family structure (fail counts)

Window `-` means a block-level row. The class gives the type pair `L9/recompute`, or, when both sides are finite
numbers, the relative-difference bucket. `nomatch` is a string or bool mismatch.

| Family | Fail | By window | By class | By defect |
|---|---|---|---|---|
| battery_term | 368 | alpha 127, beta 129, gamma 112 | bool/null 2, null/bool 346, null/null 20 | D1 346, D1+D3 2, D3 2, D4 18 |
| count | 24 | alpha 4, beta 9, gamma 11 | null/null 18, number/null 6 | D3 6, D4 18 |
| floor_gate_j | 34 | - 34 | null/number 34 | D5 34 |
| floor_j | 2 | beta 2 | null/number 2 | D6 2 |
| machine_j | 112 | alpha 44, beta 41, gamma 27 | <1e-1 40, <1e-3 26, null/null 36, number/null 10 | D2 66, D3 10, D4 36 |
| meter_j | 22 | alpha 4, beta 8, gamma 10 | null/null 18, number/null 4 | D3 4, D4 18 |
| meter_w | 11 | alpha 2, beta 4, gamma 5 | null/null 9, number/null 2 | D3 2, D4 9 |
| outcome_word | 45 | - 34, alpha 2, beta 4, gamma 5 | nomatch 36, null/bool 9 | D3 2, D4 9, D5 34 |
| rho | 108 | alpha 45, beta 41, gamma 22 | <1e-1 48, <1e-3 36, >=1e-1 2, null/null 18, number/null 4 | D2 66, D2/D3 cascade 20, D3 4, D4 18 |
| routing_id | 50 | - 40, alpha 2, beta 4, gamma 4 | null/string 50 | D4 9, D5 40, D6 1 |
| window_edge_s | 22 | alpha 4, beta 8, gamma 10 | null/null 18, number/null 4 | D3 4, D4 18 |

Every failing row maps to one of six defects. No row is left unattributed.

Leaf-path patterns, with `<w>` the window and `<rid>` the member:

- D1: `machine/<w>/<rid>/request/battery_term_available` (all 357 `machine/` rows). The same field under
  `meter/<w>/<rid>/request/` agrees for all 346 members that have values.
- D2: `{machine,meter}/<w>/<rid>/request/{rail_delta_J,rho}` in 33 members (alpha 18, beta 12, gamma 3). Each of
  these members is `<1e-3` or `<1e-1` on all four rows. In the same members, `meter/.../{delta_J,meter/*,battery/*}`
  and `window_ns` agree. The cascade reaches `machine_summary/<w>/<model>/{median,minimum,maximum,q25,q75,spread}`.
- D3: every `machine/` and `meter/` field of two members,
  `beta/d117fq38-df-cmp-abba-ph-decode-b04-a2` and `gamma/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b06-b2`.
  L9 has numbers or bools; the recompute has null; `routing_id` agrees. Neither member is in a kept unit: neither
  has a `run_phase_energy_j` row.
- D4: nine members on the recompute side only (`routing_id machine/<w>/<rid>` is null/string). Every field is
  null on both sides; `plausible` is null/bool. The members:
  - alpha: `d117fq31p7-df-cmp-abba-ph-decode-b05-b2`, `-b08-a2`;
  - beta: `d117fq38-df-cmp-abba-ph-decode-b01-a2`, `d117fq38-df-ph-prefill-p2048-abs-r01`, `neg8-refcorpus-r14`;
  - gamma: `d117c-…-decode-contrast-b09-b2`, `d117c-…-prefill-p2048-contrast-b01-a2`, `-b01-b1`, `-b09-a2`.
- D5: for both GAMMA contrasts, these rows are null on L9's side and present on the recompute's:
  `{cid}/{active_floor_j,floor_abs_j,floor_cmp_j}`, `{cid}/arm/{0,1}/floor_gate_j`,
  `{cid}/resolution/{0,1}/{floor_abs_j,floor_cmp_j,floor_gate_j}`, the sensitivity and primary floor rows, and
  `routing_id` for `{floor_row_ids,resolution/*/source,source_cell_ids,transport_group_id,transport_rule_id}`,
  `expected/contrast/{cid}[/resolutions/*]` and `expected/sensitivity/contrasts/{cid}`. The words that read the
  floor all mismatch: `{cid}/{outcome,direction,ceiling,claim_ready}`, `loo/*/{floor_status,outcome}` and
  `sensitivity[/primary]/{cid}/outcome`. Everything else about the contrasts agrees: the estimates and interval
  ends, D, raw and adjusted p, t*, n, df, kept quads, the leave-one-out estimates, `holm_reject`, and the
  per-model aggregate floor cells.
- D6: `disclosure/beta/neg8_allowance/{bound_envelope_j,bound_prediction_j}` (null/number) and
  `expected/disclosure/window_lines/beta/neg8_allowance`. The other five terms of the line, alpha and gamma
  included, agree.

## 3. Defects, with code on each side, and which side the plan supports

### D1: L9 reads a key the meter record does not have (L9 bug)

- **L9:** `joulewise/b5_analysis/disclosures.py:696` (`929fc65c9`, same on main) prints
  `battery_term_available=(row.get("machine") or {}).get("battery_available")`. The record's machine object comes
  from `km003c_parse.delta_machine_energy`, which names the field `battery_term_available`
  (`joulewise/external/km003c_parse.py:441`). So every `machine_member` line prints null.
- **The L9 test hid it.** The fixture at `tests/b5_analysis/test_disclosures.py:380` builds the record with the
  same wrong key.
- **Comparator:** `scripts/compare_b5_recompute.py:3381-3382` compares the printed line against the recompute.
  `:3393-3394` compares the record itself, which agrees.
- **Plan:** analysis plan §8.2 (`analysis_plan_block5.md:658-659`) says "The row also says whether the battery
  term was available." **L9 is wrong.** No outcome-bearing number is involved.
- **Fix (L9 bug report, patch on this branch):** read `battery_term_available`, and correct the fixture. The test
  now asserts that the line carries the flag. It fails without the fix. Making it count needs a cited rebind of the
  analysis pin and a re-run of step 11. That is the lead's decision.

### D2: the recompute's rail idle term reads the wrong idle attempt (recompute bug)

- **Registered quantity.** Registration §5.8 (`registration_block5.md:3522`) defines ΔE_rail as "the bundle's
  `idle_subtracted_energy_j` as the harvest re-derives it". The reducer computes
  gross − `metadata.idle_baseline.power_w_mean` × T (`joulewise/reduce.py:2958-2962` and `:3536-3540`). The harvest
  copies it (`joulewise/b5/harvest.py:6929`, `:6963-6971`), and L9 prints it (`disclosures.py:679`).
- **Recompute:** rail = overlap gross − `rail_idle_power(member)` × T
  (`scripts/independent_recompute_b5.py:2026` and `:2043` at `d271fb476`). `rail_idle_power` (`:1941-1952`)
  always reads `rich_telemetry_idle.jsonl`.
- **Collection.** When the first idle admission attempt is not admitted, the controller measures a second idle
  baseline and keeps it as the baseline (`joulewise/controller.py:1945` and `:1972`). That baseline is the
  `metadata.idle_baseline` the reducer uses. The adapter writes attempt N's rich rows to
  `rich_telemetry_idle_attempt_N.jsonl` (`joulewise/adapters/powermetrics.py:278-282`). Promotion replaces only
  the canonical raw plist (`:188-255`); `rich_telemetry_idle.jsonl` stays attempt 1. So for every member whose
  idle baseline was re-measured, the recompute subtracts attempt 1's idle power and the bundle subtracts the kept
  attempt's.
- **Structure fits.** Gross request energy agrees within the bar for every kept member among the 33: 16 have
  `run_phase_energy_j .../request` rows, all AGREE. `delta_J` and the meter terms agree. Only rail, and ρ through
  it, differ, and only in a minority of members, which is the expected shape of an occasional idle retry.
- **Which side the plan supports.** **The recompute is wrong**: its idle term is not the bundle's baseline.
  Combined power and `rail_sum_power_w` are the same rail sum, weighted the same way. The 115 rail rows that are
  `identical` and the 198 that are `<1e-6` show that the formula itself is not the difference.
- **Fix (recompute, on this branch).** `idle_attempt_telemetry_name` picks the rich file of the metadata's last
  `environment_admission.attempts[*].attempt`. If that file is missing, the term is unavailable and flagged; it
  never falls back silently to attempt 1. Tests: `IdleAttemptTests` in
  `tests/independent_recompute/test_release_trace_20261107.py`. They cover the kept attempt with 0, 1 and 2
  attempts and with both attempts not admitted, a missing attempt file, and the rail delta end to end against the
  reducer-style term. All fail on the unfixed recompute.
- **Falsification probe** (section 6). Expected, if this is the cause: every one of the 33 has an attempt-N file
  and a 2-attempt record, and no agreeing member has either.

### D3: two removed members that L9 describes and the recompute does not (unresolved; probe first)

- **L9 or harvest:** the harvest computes the meter terms whenever the request window lies inside a stream
  (`harvest.py:6909` and `:6921`). It takes ΔE_rail from the re-reduction whatever the member's validity, and L9
  prints the row (`disclosures.py:676-697`).
- **Recompute:** `machine_member` returns the unavailable stub, with every field null, in two cases:
  - **(a)** the member is `not_compared` (`independent_recompute_b5.py:1988`): its status is not succeeded, its
    anchor is not bounded, or its trace is missing;
  - **(b)** the stream does not cover the idle baseline (`:2017`). The harvest checks only the request window.
- **Precedent.** The R18 rehearsal test asserts that an anchor-unbounded member has null rail and ρ while the
  record holds them (`tests/independent_recompute/test_round3.py:429-439`), so (a) is a designed behaviour of the
  recompute.
- **Plan.** §8.2 (`analysis_plan_block5.md:653`, `:690`): "For each kept or removed member … (the meter describes
  every collected member)", and it "never excludes a member". Under (a), the recompute leaves out members the
  plan describes, a coverage gap on its side. The meter term ΔE_machine needs no rail anchor when controller
  stamps exist, so at least the meter terms are recomputable. Under (b), L9's baseline is the mean over only part
  of the idle stage, which is not registration §5.8's "mean over the member's idle-baseline stage". L9 would then
  be the side that is wrong.
- **No fix applied.** The probe (section 6) reads the members' summary status and anchor status words to decide
  between (a) and (b).

### D4: collected members that never measured a request (recompute membership)

- **L9 or harvest:** a meter row exists only for a member with a request span, that is, the `sampling_started` and
  `sampling_stopped` controller stamps (`harvest.py:6909`, `member_spans`). The nine members have no row on L9's
  side.
- **Recompute:** it listed every roster member with a `metadata.json` (`independent_recompute_b5.py:2358-2369`),
  so these nine became members whose every field is null. The comparator then failed each field, as null/null,
  and the `plausible` word as null/bool, and routed their edges to `window_edge_s` (section 1).
- **Plan:** §8.2 describes each member "over its measured request (the harvest's request span)"
  (`analysis_plan_block5.md:653-654`). A member without one has nothing to describe. **The recompute is wrong to
  emit a null member.** No value is involved.
- **Fix (recompute, on this branch).** A member that is absent from the harvest record and has neither a request
  edge nor controller sampling stamps goes to `no_measured_request`, not `members`. A member with a measured
  request that the record lacks still gets its row, so a dropped harvest row stays visible to the comparator.
- **Test.** `UnmeasuredMemberTests`: a full synthetic pack plus one failed member with no sampling events. It
  fails on the unfixed recompute.
- **Probe:** expected `stamps_missing` 9/9. A plausible common cause is a run aborted at idle admission, which
  stops before sampling; the probe also prints the admission decision word.

### D5: GAMMA contrast floor resolution refused on L9's side (unresolved; it decides the outcome words, so probe before any fix)

- **L9:** for both contrasts, both arms' `floor.resolutions` are present and `refused`, with empty
  `source_cell_ids` and null transport ids. So `active_floor_j` is null, and under §7.2 step 2 the outcome is
  `not_resolvable` ("if there is no floor").
- **Code paths that print exactly this signature**, read with an independent Sol 6.1 seat, its events audited:
  - `_floor_request_or_refusal`'s explicit refusals `consumer_identity_undeclared` and
    `consumer_identity_set_unauthenticated` (`joulewise/analysis_engine/inputs.py:4796`);
  - its empty returns, which become `artifact_schema_invalid` plus binding codes when the claim-side floor binding
    has problems, or `consumer_term_unknown` otherwise (`analysis_engine/__init__.py:413-454`;
    `inputs.py:4774`, `:4851`, `:4889`, `:4933`);
  - more than one exact cell, `transport_group_incomplete` (`inputs.py:5188`);
  - zero or several matching transport groups, `cell_missing` or `transport_group_incomplete` (`inputs.py:5202-5237`).
- **Ranked candidates:**
  1. the claim-side evidence binding (`inputs.py:2211`, `:2448`; joins of producer plans, orders and logs at
     `:1346` and `:1952`) refuses cells the mint accepted;
  2. consumer-identity multiplicity blocks exact-stack selection (`inputs.py:4874`);
  3. a mint/request key mismatch. This one is the least likely, because finalization checks those keys
     (`analysis_manifest_v3.py:3480`).
- **Recompute:** takes the armwise maximum of the per-model cells directly
  (`independent_recompute_b5.py:1679`, `:2848`), with no transport or binding admission. The aggregate cells agree
  with L9's.
- **Which side the plan supports** depends on the refusal's cause. Plan §5 ("How GAMMA uses them") and §7.2 make
  a genuine absence or inapplicability of the floor a registered outcome, `not_resolvable`, and then the recompute
  is the side that is wrong. A tooling refusal is R3, a repair (§3.1, "Refusals"), and then L9 is the side that is
  wrong.
- **Not decidable from `comparison.json`.** The resolution `reason_codes` are not compared leaves. The opt-in probe
  (section 6) prints only `status:reason_codes` words, each checked against the engine's code list. No fix is
  applied, and none should be until the codes are known.

### D6: BETA's NEG-8 bracket has no envelope or prediction term (definitional; comparator mapping)

- **L9:** `disclosures.py:1047-1061` prints every finite `*_j` field of the allowance's source bracket. The
  allowance is the record the harvest names (plan `analysis_plan_block5.md:237-243`).
- **The bracket writer** sets `bound_envelope_j` and `bound_prediction_j` only under the survivor protocol, and
  only when its survivor terms exist (`joulewise/whole_window.py:3435-3453`). The planned and legacy records
  "keep their historical bytes", without those terms.
- **Recompute:** always re-derives both terms with the count-adjusted survivor formula
  (`independent_recompute_b5.py:836-848`, `:1171`).
- **Comparator:** compares all seven terms unconditionally (`compare_b5_recompute.py:3274-3279`).
- **Verdict:** BETA's allowance itself (`drift_allowance_j`) and its other four terms agree. The two terms the
  record does not carry are not printed values, so **neither producer is wrong**. The comparator should compare
  them only when the recorded bracket carries them. That needs the recompute to expose the recorded protocol and
  term presence, and the expected-check table to treat the two terms as conditional.
- **Not implemented here, pending the lead.** The probe prints BETA's protocol word and whether each term is
  finite.

## 4. The 60 "unmapped" step-11 leaves: no mapping gap

`coverage()` returns `unmapped = unmapped_no_rule ∪ uncompared` (`compare_b5_recompute.py:3982`). Here the 60
equal the `uncompared` list exactly, so no leaf lacks a rule. All 536 `unbound` entries have the reason
`row_disagrees`: the leaf is mapped, but the row it copies disagrees. They are the printed copies of the defects
above:

- `disclosure:window_lines/{alpha,beta,gamma}/machine_member/{battery_term_available,rail_j,rho,machine_j,plausible}`
  (D1, D2, D3);
- `.../machine_summary/{median,minimum,maximum,q25,q75,spread}` (the D2 and D3 cascade);
- `disclosure:contrasts/decision_floor/floor_j`,
  `disclosure:{sensitivity/contrasts/*,block_lines/sensitivity_contrast/record}/{primary,sensitivity}/{floor_*,outcome}`
  and `fill:gamma/contrasts/*/{floor/*,claim_evaluation/{outcome,direction,claim_level_ceiling,claim_ready_for_l2_l3},loo/rows/*/{floor_status,outcome}}`
  (D5).

They clear when their rows agree. A reporting nit, not a defect: the verdict's `step11_unmapped` would be clearer
split into `no_rule` and `uncompared`.

## 5. What is on this branch (`lane/2026-11-07-b5-release-trace`)

| Change | Defect | Side | Tests |
|---|---|---|---|
| `scripts/independent_recompute_b5.py`: `idle_attempt_telemetry_name`; `rail_idle_power` reads the kept attempt | D2 | recompute | `test_release_trace_20261107.IdleAttemptTests` (3) |
| `scripts/independent_recompute_b5.py` `add_machine`: no null member without a measured request (`no_measured_request`) | D4 | recompute | `test_release_trace_20261107.UnmeasuredMemberTests` |
| `joulewise/b5_analysis/disclosures.py:696`: `battery_term_available`; fixture key in `tests/b5_analysis/test_disclosures.py` | D1 | L9 (bug report and patch; needs a cited rebind) | `test_T8_T20_B8_meter_all_members` |
| `docs/process_traces/2026-11-07-b5-release-trace/` | the blind extractor and the structure-only probe | | |

- Every new test fails on the unfixed code.
- Passing:
  - `tests.independent_recompute.{test_meter,test_round3,test_comparator_meter,test_review_fixes,test_review_probes_meter,test_auditfix}`:
    107 run, 9 skipped (`JW_B5_SYNTHETIC_ONLY=1`);
  - `tests.b5_analysis.test_disclosures`: 62;
  - `scripts/repin.py --check`.

**Expected effect of a re-run (the lead decides; nothing was re-run on real data).**

- With the D2 and D4 fixes, the recompute-side rows clear: the 132 D2 rail and ρ rows and their summary rows, and
  the 171 D4 rows.
- With the L9 D1 patch, after its rebind and a step-11 re-run, the 346 D1 rows clear.
- D3, D5 and D6 stay until the probe has answered.

## 6. Probe for the lead (structure only)

`docs/process_traces/2026-11-07-b5-release-trace/probe_release_hold.py`:

```bash
python3 -I probe_release_hold.py "$OUT/comparison.json" configs/analysis/b5/analysed_windows.json [<dry-j custody root>]
```

- It prints only counts, file presence and enum words checked against fixed vocabularies, and refuses output that
  contains a decimal.
- It reads member `metadata.json` and `summary_metrics.json` for enum fields only, the names of
  `rich_telemetry_idle_attempt_*` files, and BETA's rescreen bracket for the protocol word and term finiteness.
- With the third argument it also reads `floor.resolutions[*].{status,reason_codes}` from L9's claim verdicts.
  That reads an outcome-bearing file for structure words only, so whether to pass it is the lead's call.

Expected results:

- **D2:** `rail_differs` all `attempt_file_present` and `metadata_attempts_2`; `rail_agrees` none.
- **D4:** `stamps_missing` 9.
- **D3:** the status and anchor words decide between (a) and (b).
- **D5:** the reason codes rank its candidates.
- **D6:** the protocol word, and both terms not finite.
