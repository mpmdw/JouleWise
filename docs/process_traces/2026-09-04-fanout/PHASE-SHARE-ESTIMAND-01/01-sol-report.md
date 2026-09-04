```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Implemented and tested an exact shared-boundary replay; retained a10 evidence shows that joint coupling removes impossible phase-total combinations but gives no narrower scalar phase-share or normalized phase-asymmetry envelope, so claim-path promotion needs a lead ruling.",
  "workspace": {"base_requested":null,"base_mode":null,"head_start":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","head_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","upstream_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","branch":"feat/2026-09-04-fan-PHASE-SHARE-ESTIMAND-01"},
  "pathspec": ["docs/process_traces/2026-09-04-fanout/PHASE-SHARE-ESTIMAND-01/01-sol-report.md","joulewise/phase_share.py","scripts/analyze_phase_share.py","tests/test_phase_share.py"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"needs_ruling"},
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_phase_share","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["......","----------------------------------------------------------------------","Ran 6 tests in 0.003s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 6 tests .* OK"}},
    {"id":"V2","kind":"other","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/analyze_phase_share.py /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r01 | jq -c '{bundle_id,source_sha256,source_boundary_bound_s,joint_total:.envelope.joint_total_phase_energy_j,box_total:.envelope.independent_box_total_phase_energy_j,joint_share:.envelope.joint_prefill_share,box_share:.envelope.independent_box_prefill_share,joint_asymmetry:.envelope.joint_normalized_decode_minus_prefill,box_asymmetry:.envelope.independent_box_normalized_decode_minus_prefill,comparison:{joint_to_box_prefill_share_width_ratio:.comparison.joint_to_box_prefill_share_width_ratio,joint_to_box_normalized_asymmetry_width_ratio:.comparison.joint_to_box_normalized_asymmetry_width_ratio}}'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["{\"bundle_id\":\"p2015-df-ph-decode-abs-r01\",\"source_sha256\":{\"events.jsonl\":\"3ef7c7aeba5e5f2219c3fee75bb095424cfbd486c4aca5fa0cb9b231deb78b5d\",\"metadata.json\":\"5ceee193847f09acc948ea7c6e6be25cd002179aefceaefcc2eb31ee457c918f\",\"power_trace.csv\":\"a00f9f67576fb0ff067f8e6bdc66778dcb3593701792fae1f326821ec9738c6e\",\"summary_metrics.json\":\"37783c83b6826a41c71fab5b57263279a73551d994b7cd4c9837c8b2652c85c6\"},\"source_boundary_bound_s\":0.026206752495348457,\"joint_total\":{\"lower\":51.62730338107395,\"upper\":51.62730338107395},\"box_total\":{\"lower\":50.27478179508489,\"upper\":52.97982496706301},\"joint_share\":{\"lower\":0.017640500094209376,\"upper\":0.043838296558722796},\"box_share\":{\"lower\":0.017640500094209376,\"upper\":0.043838296558722796},\"joint_asymmetry\":{\"lower\":0.9123234068825544,\"upper\":0.9647189998115813},\"box_asymmetry\":{\"lower\":0.9123234068825544,\"upper\":0.9647189998115813},\"comparison\":{\"joint_to_box_prefill_share_width_ratio\":1.0,\"joint_to_box_normalized_asymmetry_width_ratio\":1.0}}"]},"expected":{"exit_code":0,"tail_regex":"joint_to_box_normalized_asymmetry_width_ratio\\\":1.0"}},
    {"id":"V3","kind":"other","cmd":"for bundle in /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r[0-9][0-9]; do PYTHONDONTWRITEBYTECODE=1 python3 scripts/analyze_phase_share.py \"$bundle\" | jq -r '[.bundle_id,.comparison.joint_to_box_prefill_share_width_ratio,.comparison.joint_to_box_normalized_asymmetry_width_ratio,(.envelope.joint_total_phase_energy_j.upper-.envelope.joint_total_phase_energy_j.lower),(.envelope.independent_box_total_phase_energy_j.upper-.envelope.independent_box_total_phase_energy_j.lower)] | @tsv'; done","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["p2015-df-ph-decode-abs-r01\t1.0\t1.0\t0\t2.7050431719781187","p2015-df-ph-decode-abs-r02\t1.0\t1.0\t3.953966617586957e-05\t2.0873878449290686","p2015-df-ph-decode-abs-r03\t1.0\t1.0\t0\t2.5062640988897584","p2015-df-ph-decode-abs-r04\t1.0\t1.0\t7.105427357601002e-15\t3.1972289470055912","p2015-df-ph-decode-abs-r05\t1.0\t1.0\t7.105427357601002e-15\t2.6364862442271075","p2015-df-ph-decode-abs-r06\t1.0\t1.0\t7.105427357601002e-15\t3.3777750717810164","p2015-df-ph-decode-abs-r07\t1.0\t1.0\t7.105427357601002e-15\t2.9931897532122633","p2015-df-ph-decode-abs-r08\t1.0\t1.0\t6.279471159587047e-05\t2.3678798715860836","p2015-df-ph-decode-abs-r09\t1.0\t1.0\t5.6812689301466435e-05\t2.1945554636763873","p2015-df-ph-decode-abs-r10\t1.0\t1.0\t5.687288045663763e-05\t2.370300094088684"]},"expected":{"exit_code":0,"tail_regex":"p2015-df-ph-decode-abs-r10\\t1.0\\t1.0"}}
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"The row's expected scalar uncertainty reduction is refuted by exact measured-curve arithmetic, and no authority defines a different publishable joint estimand.","needs":"Rule whether to close the scalar phase-share/asymmetry proposal as a null result (recommended) or open a separately pre-registered phase-allocation/closure estimand."},
    {"id":"F2","kind":"residual_risk","level":"nonblocking","text":"The retained a10 bundle is diagnostic evidence; D-078 records that its whole-window verdict artifact is absent, so this replay cannot license a claim.","needs":"Keep every output diagnostic_non_claim_bearing; use a prospective governed campaign if a new estimand is authorized."}
  ]
}
```

## Change

Added a pure measured-curve helper and a command-line diagnostic. The helper moves the prefill stop and decode start by the same displacement, preserves the measured marker gap, evaluates every measured interval-support crossing, and returns both the one-parameter curve and the rectangle obtained by combining the two marginal ranges independently. The command-line producer reads the bound from matching current-wire phase envelopes and records SHA-256 digests for the power trace, events, metadata, and stored summary. It labels its output non-claim-bearing. The reducer summary schema and every claim path are unchanged.

The counterfactual regression is physical rather than structural: the fixture transfers energy across one contiguous boundary. The joint result keeps total phase energy invariant, while deleting the coupling and combining the marginals admits impossible totals. A test also pins the less intuitive result that the scalar share and normalized asymmetry endpoints do not narrow.

### Finding and decision table

| ID | Finding or decision | Evidence | Disposition |
|---|---|---|---|
| F-1 | `_corner_composed_anchor_shift_envelope` does not represent phase adjacency. The reducer calls it separately for each phase and emits two marginal envelopes with no shared-boundary coordinate. | Code inspection of `joulewise/reduce.py`; the new counterfactual fixture. | Confirmed defect for a joint two-phase record. |
| F-2 | A joint curve removes impossible combinations for total phase-attributed energy. | V2: the retained r01 curve stays at 51.62730338107395 J, while the marginal rectangle spans 50.27478179508489--52.97982496706301 J. Source bytes are sealed in V2. | Real geometric improvement, but for total/closure, not for scalar phase share. |
| F-3 | The proposed scalar gain is zero. Define prefill share as `prefill / (prefill + decode)` and normalized phase asymmetry as `(decode - prefill) / (decode + prefill)`. Their joint and independent-box endpoints are identical. | V2 gives identical intervals and width ratios of 1.0; V3 repeats both ratios across every retained member in the absolute decode cell. | The kernel row's inflation premise is refuted for these scalar estimands. |
| D-1 | Do not alter marginal phase envelopes or the analysis claim path. | The scalar claim does not tighten, while the joint total is a different estimand. | Implemented: diagnostic only. |
| R-1 | **NEEDS_RULING:** classify the scalar proposal as a diagnostic sensitivity result, or authorize a new joint phase-allocation/closure estimand. | No cited authority defines that new estimand, its floor, or its claim ceiling. | Recommend retaining the result for diagnostics rather than treating it as an empirical null finding. |

### Scoped design

**Forcing problem.** Two marginal phase envelopes form a rectangle. Most points in that rectangle cannot occur when one boundary displacement simultaneously removes energy from one phase and adds it to the other.

**Options.** (A) Preserve the full one-parameter phase-allocation curve as a diagnostic; this is implemented. (B) Replace the scalar phase-share/asymmetry interval with the curve's projection; rejected because the endpoints and width are unchanged. (C) Register total phase-attributed energy or closure as a new estimand; this gains from the curve, but changes the scientific question and requires prospective authority.

**Recommendation.** Select A and close the expected scalar improvement as a null result. Select C only if the paper needs a closure claim; then pre-register the formula, evidence binding, floor transport, and claim ceiling before it touches claim-bearing data.

**Worked example.** In V2 the retained r01 bundle has prefill 1.5869922431521415 J and decode 50.04031113792181 J at the recorded boundary. Sweeping the issued 0.026206752495348457 s bound jointly gives prefill share 0.017640500094209376--0.043838296558722796 and normalized asymmetry 0.9123234068825544--0.9647189998115813. The independent rectangle gives exactly the same two scalar intervals, while admitting the impossible phase-total interval reported in F-2.

## Verification notes

The repository-wide suite was not run, as required by the preflight rule. An initial focused run exposed a last-bit floating association difference between two algebraically identical asymmetry formulas; the implementation now uses the single canonical formula `1 - 2 * prefill_share`. A first direct script invocation also showed that the repository root was absent from the script search path; the producer now follows the repository's script-bootstrap convention. V1 is the clean rerun after both repairs.

## Residual risk

Precise handoff checklist:

1. **NEEDS_RULING:** choose R-1. Recommendation: close the scalar uncertainty-reduction premise as a null result; do not promote a claim estimator.
2. If a closure estimand is authorized, define it in the owning analysis plan and decision record, require the same estimator in calibration and consumption, and add a provenance-bearing output schema before production integration.
3. The magistrate updates `docs/process/state_kernel.json`, `TASK_QUEUE.md`, `RUN_STATE.md`, and any decision-log disposition. Those lead-owned files were intentionally not edited.
4. No hardware work remains for this desk investigation. Any new claim-bearing estimator must be frozen prospectively and exercised on its governed campaign; the retained a10 replay remains diagnostic only.
