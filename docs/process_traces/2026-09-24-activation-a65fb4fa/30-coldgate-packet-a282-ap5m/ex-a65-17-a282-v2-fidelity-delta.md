```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "V2 repairs most v1 fidelity findings, but the operative denominator, smoke gate, and floor-widening rules still need adjudication.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "029a7e730ccb9e7887e5a395c81a94c77860fe1a",
    "head_end": "029a7e730ccb9e7887e5a395c81a94c77860fe1a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","title":"The restored denominator guard still has an observed-count execution path"},
      {"id":"F2","severity":"blocker","title":"The smoke gate drops every defined pass condition"},
      {"id":"F3","severity":"blocker","title":"Floor-plus-anchor widening conflicts with the single-count discipline"},
      {"id":"F4","severity":"should_fix","title":"Window budget and planning costs are mislabeled as nights"},
      {"id":"F5","severity":"should_fix","title":"The new instrument description gives the wrong interval-energy calculation"},
      {"id":"F6","severity":"should_fix","title":"A phase-floor observation is stated as the prospective block-window floor"},
      {"id":"F7","severity":"should_fix","title":"The scorer gloss overstates exact numeric equivalence"},
      {"id":"F8","severity":"should_fix","title":"The drift-bias derivation needs an unstated common-drift assumption"},
      {"id":"F9","severity":"nit","title":"O-4 presents the point-inclusive endpoint as equally operative"}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"inspection",
      "cmd":"python3 -c 'from pathlib import Path; a=Path(\"docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md\").read_text().splitlines(); b=Path(\"docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md\").read_text().splitlines(); print(len(a[924:950]), a[924:950]==b[34:60])'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["26 True"]},
      "expected":{"exit_code":0,"tail_regex":"^26 True$"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"git status --short --branch && git rev-parse HEAD",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","029a7e730ccb9e7887e5a395c81a94c77860fe1a"]},
      "expected":{"exit_code":0,"tail_regex":"029a7e730ccb9e7887e5a395c81a94c77860fe1a$"}
    }
  ],
  "flags":[
    {"id":"R1","kind":"lead_ruling","level":"blocking","text":"The three BLOCKER findings can change admission or claim direction.","needs":"Cold judge to rule the denominator interpretation, surviving smoke checks, and AP-5M floor/anchor roles."}
  ]
}
```

## Findings

**F1 — BLOCKER.** V2 restores AP-5’s “binomial lower-bound” wording as operative, but its [merge example (§2.4)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:309) declares a group with three observed correct answers passing, and the carried [S2 pseudocode (§3)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:803) still merges on observed count `< 3`. The [operative AP-5 field](/Users/edr/code/wt-a65fb4fa-lens3/docs/contracts/analysis_plans.md:274) says *lower bound*; [packet C §3](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:130) says *observed count*. K9 identifies the conflict, but the procedure cannot produce a unique partition until O-2 specifies the bound and confidence convention or expressly adopts the observed-count change. Keep the example conditional rather than saying that group passes.

**F2 — BLOCKER.** The [K21 proposal (§2.9)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:745) retains a named smoke gate but makes none of E1–E4 a pass condition. The [current AP-5 field](/Users/edr/code/wt-a65fb4fa-lens3/docs/contracts/analysis_plans.md:270) requires a *passing* gate; [E1–E4](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/suite_implementation_research.md:565) separately test stop reasons, emitted-token mean, emitted-token distribution, and prompt tokens. [Packet C §1](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:24) identifies level-invariant emitted length and stop reasons as the incompatibility; the [v2 revision brief](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/16-a282-v2-fidelity-delta-brief.md:7) says to keep the gate minus its length condition. Strict-valid bundles and recorded distributions alone do not define a passing envelope check. The cold judge should name the surviving predicates, including how stop-reason and prompt-token behavior are judged for MATH.

**F3 — BLOCKER.** [K11 (§2.9)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:601) faithfully carries gate 21’s `k·(floor_j + anchor_j)·s` widening from [D5a](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:68). The project’s later-described [single-count discipline](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/detection_floor.md:141) assigns the floor to a separate claim gate and the anchor to the decision interval; their sum is a *planning diagnostic*, not an acceptance gate ([lines 160–168](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/detection_floor.md:160)). Both sources explicitly require both roles, but they prescribe different interval widening. O-12 correctly exposes this; it cannot be silently resolved by citing D5a alone.

**F4 — MATERIAL.** [K2’s gloss](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:502) turns the registered *window budget* into “a number of nights”; [O-18](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1177) repeats “12 nights,” “23 nights,” and “4–5 nights a day.” [Synthesis E4](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:30) says **12 versus 23 windows**, at **4–5 windows per day**; [record 18](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/18-headline-opus-integration.md:119) gives the window arithmetic. Correct the unit wherever the mechanical n rule is explained.

**F5 — MATERIAL.** The new [instrument definition (§2.1)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:81) says interval energy is the sum of per-record energy counters “falling in it.” The [artifact guide’s extraction rule](/Users/edr/code/wt-a65fb4fa-lens3/docs/paper/artifact-guide.md:336) computes interval-supported powermetrics energy from `power_w × overlap duration` for each sample interval, including edge overlaps. The boundary and 100 ms sampling description have support in the [measurement boundary table](/Users/edr/code/wt-a65fb4fa-lens3/docs/contracts/measurement_methodology.md:257) and [artifact guide pins](/Users/edr/code/wt-a65fb4fa-lens3/docs/paper/artifact-guide.md:227); the integration sentence needs correction.

**F6 — MATERIAL.** [§2.1](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:113) states that “on this stack the floor is attribution-limited: about 1 J,” then applies `floor_j` to future block windows. [D-078 clause 11](/Users/edr/code/wt-a65fb4fa-lens3/docs/decision_log.md:4747) describes roughly 0.7–1.0 J anchor-shift envelopes across **phase** boundaries; the [research bank](/Users/edr/code/wt-a65fb4fa-lens3/docs/research_question_bank.md:1603) likewise labels ≈1 J *per phase*. The [floor artifact semantics](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/detection_floor.md:64) require an exact window class, and v2 itself says no block-window artifact exists. Label 1 J as a historical phase-window planning figure, not the block-window floor.

**F7 — MATERIAL.** The new [scorer gloss (§2.1)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:72) says the scorer compares answers “as an exact rational number.” The [MATH importer ruling C2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/40-fable-ruling-math.md:49) expressly makes `44%` match `44` and discloses the hazardous `\frac12%`/`\frac12` match; its [operative scorer rule](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/40-fable-ruling-math.md:106) is parser-and-hazard based. Describe the pinned canonicalization and hazard check, since mathematical percent scaling would change correct counts.

**F8 — MATERIAL.** The new [drift explanation (§2.1)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:167) derives between-model bias ≤ `δ_upper × P × lever` merely from a per-block per-slot shift bound. Equal mean positions cancel a *shared linear* position effect; a bound on each block’s shift alone does not establish that cancellation for different slopes or nonlinear drift. [Round-1 F1](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md:8) states the balance objective, and [gate 21 D5b](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:70) requires a registered bias budget; neither supplies that physical assumption. State the assumed drift model beside the derivation, or present the formula as the registered tolerance without claiming a proved general bound.

**F9 — NIT.** [O-4](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1130) asks whether the endpoints “are” percentiles alone or point-inclusive. [Packet C §3 step 6](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:112) already supplies the operative percentile-only wording under the v2 revision ruling. Ask whether to **amend** it with point bounds.

### D1 — v1 lens disposition

| Lens 11 item | Disposition | Evidence |
|---|---|---|
| B1 | **PARTLY** | AP-5 restored in [v2 K9](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:568), but F1 remains against [AP-5](/Users/edr/code/wt-a65fb4fa-lens3/docs/contracts/analysis_plans.md:274). |
| B2 | **FIXED** | [v2 K11](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:611) uses [C §3’s percentiles](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:112); point-inclusive endpoints are O-4. |
| M1 | **FIXED** | [v2 S6](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:869) proposes pooled, bracket, outside-gap, NR and NE wording under [gate 21 Q1(a)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:27). Adoption remains O-3. |
| M2 | **FIX INTRODUCED A NEW DEFECT** | [v2 K2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:495) carries [C’s mechanical rule](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:125), but F4 changes its budget unit. |
| M3 | **FIXED** | [v2 §6](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1113) closes the old merge/order questions per [08 F1](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md:9) and [20 Q2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/20-a281-opus-consult.md:14). The new O-2/O-10 address different questions. |
| M4 | **FIXED** | [v2 row/K6/K12](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:459) distinguishes packer objective from the tolerance in [gate 21 D5b](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:70). F8 concerns the added explanation. |
| M5 | **FIXED** | [v2 Terms](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:102) points census-clean to the [runbook](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/derivation_night_runbook.md:626), and [line 134](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:134) calls worst case an assumption as [§7(N)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:48) requires. |
| M6 | **FIX INTRODUCED A NEW DEFECT** | [v2 K21](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:745) adds the gate while removing all [E1–E4](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/suite_implementation_research.md:565) pass checks; F2. |
| N1 | **FIXED** | [v2 O-1](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1117) calls the [R6](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md:12) text a faithful excerpt, no longer VERBATIM. |

Lens 11’s **F6 open-item review** is addressed item by item in D5 below. Its previously identified errors are repaired except the denominator interpretation and new budget-unit error.

### D2 — added-text source audit

The new procedure largely restates K/S clauses; the two-stage draw and RNG/quantile choice are explicitly **PROPOSED** in [K10](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:588). The problem population and keyed draw trace to the [merged importer selection functions](/Users/edr/code/wt-a65fb4fa-lens3/joulewise/benchmark_import_math.py:228) and [M1’s correction](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:50); adoption is O-15. The worked bootstrap arithmetic recomputes to 1.9221, 1.9173 and 1.9270 from the displayed sums. The 540 s capacity, 200 s worst case, 360 s timeout and drift threshold in [§2.6](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:358) are marked illustrative. B = 20,000 traces to [C §3](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:106); five parents/envelopes to [M8 and gate 45 Q4](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:71). The added claims needing correction or a ruling are F1–F8. In particular, “about 1 J” and “12/23 nights” cannot be used as unlabeled block-floor and budget facts.

### D3 — byte-exact carries

A read-only Python extraction compared every source-labelled VERBATIM blockquote after removing its `> ` prefix: **52/52 matched**. Separate byte comparisons passed for the S2 pseudocode, complete 26-row S11 table, four-row claim-language table, claim-role field, the first two multiplicity sentences, the ceiling field’s quoted prefix, D-166 forcing problem and rulings (1)–(5), and the K5/K21 fragments: **9/9 passed**. Thus all **61** entries marked VERBATIM in [§5](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1006) passed at their stated quoted extent. K15 is correctly labelled ADAPTED; reversing [§7(X)’s substitution](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:58) reproduces the [gate 45 original](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:71). The appended `K20` pointer is outside the ceiling field’s quoted source prefix.

### D4 — O-12 question for the cold judge

The [floor contract](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/detection_floor.md:141) says `floor_j + claim_side_bound_j` is for prospective sizing; acceptance checks the floor separately and excludes zero using intervals widened by the claim-side anchor bound ([lines 160–168](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/detection_floor.md:160)). [Gate 21 D5a](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:68) instead puts `floor_j + anchor_j` inside **each bootstrap replicate’s** widening, which [v2 K11](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:604) carries.

**Precise question:** For AP-5M, must each replicate widen by `k·(floor_j + anchor_j)·s` under D5a, expressly overriding the single-count interval rule, or must it widen by `k·anchor_j·s` while the issued block-window floor remains a separate gate? Name the block-window floor artifact and define `floor_j` either way. This can change whether an interval excludes 1.

### D5 — O-1 through O-20

| Item | Audit |
|---|---|
| O-1 | Properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1117); outcome agrees but reasons differ between [gate 21](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:23) and [R6](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md:12). |
| O-2 | Properly open, though F1 makes it blocking: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1123), [AP-5](/Users/edr/code/wt-a65fb4fa-lens3/docs/contracts/analysis_plans.md:274), [C](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:130). |
| O-3 | Properly open for adoption of the proposed sentence; all-gap disclosure is already answered by [gate 21 Q1(a)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:27); [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1127). |
| O-4 | Partly misphrased (F9): percentile endpoints are operative under [C §3](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:112); point-inclusive amendment and K10 mechanics remain open in [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1130). |
| O-5 | Properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1134); [§7(P)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:60) fixes precedence, not Holm membership. |
| O-6 | Properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1136); [K15’s source](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/10-coldgate-fable-ruling.md:71) defines a cell flag, not its merged-group propagation or recapture limit. |
| O-7 | Properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1139); [D5b](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:70) supplies units and budget requirement, not values or precedence. |
| O-8 | Properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1143); [08 F2(d)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/08-a281-round1-synthesis-and-rulings.md:15) leaves the 10% trigger for consideration. |
| O-9 | Properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1146); [R6](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/11-opus-contract-refuter.md:12) requires the check without its failure disposition. |
| O-10 | Properly open as the *new* cross-night question: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1148); [M12](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:22) and [§7(N)](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/45-coldgate-packet-a281a-recut/21-coldgate-fable-addendum-ruling.md:48) leave that boundary unclear. |
| O-11 | Partly answerable and understated: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1152); [AP-5](/Users/edr/code/wt-a65fb4fa-lens3/docs/contracts/analysis_plans.md:270) requires a pass, and the [revision brief](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/16-a282-v2-fidelity-delta-brief.md:7) retains the gate minus length. F2. |
| O-12 | Properly open and blocking: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1156); [floor discipline](/Users/edr/code/wt-a65fb4fa-lens3/docs/phase_2/detection_floor.md:160) versus [D5a](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-d8cc9c0a/21-coldgate-packet-a281/10-coldgate-fable-ruling.md:68). |
| O-13 | Properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1163); [M7](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:17) calls idle a covariate without an adjustment rule. |
| O-14 | Properly open for registration values, but correct its budget unit alongside F4: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1165); [C §3](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/10-headline-packet-c-ap5-amendment.md:125). |
| O-15 | Properly open for *adoption*, though the mechanics are answerable from the [importer](/Users/edr/code/wt-a65fb4fa-lens3/joulewise/benchmark_import_math.py:228); [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1168). |
| O-16 | Editorial and properly open: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1170); the [AP-5 field list](/Users/edr/code/wt-a65fb4fa-lens3/docs/contracts/analysis_plans.md:260) supplies no prohibition on extra fields. |
| O-17 | Properly reserved for Ed: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1171); [synthesis E2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:28). |
| O-18 | **Mis-stated units** under F4; budget approval remains Ed’s: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1177), [synthesis E4](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:30). |
| O-19 | Properly reserved for Ed E3; recommendation remains a recommendation: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1180), [synthesis E3](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:29). |
| O-20 | Properly reserved for Ed E1; the custody choice is labelled a recommendation: [v2](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-24-activation-a65fb4fa/07b-a282-ap5m-draft-v2.md:1184), [synthesis E1](/Users/edr/code/wt-a65fb4fa-lens3/docs/process_traces/2026-09-23-activation-1d3796d5/19-headline-integration-synthesis.md:27). |

## Residual risk

This was a read-only text and source audit. It did not execute the draft estimator or validate a live block-window floor. The worktree remained clean at the same detached HEAD.