```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "H1 remains open; an epoch hold must govern both claim authority and permission to arm, with a separate non-claim inspection path.",
  "workspace": {
    "base_requested": "8458f797",
    "base_mode": "exact",
    "head_start": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "head_end": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "summary": "The file-keyed loader hold does not cover arm evidence, mixed pack declarations, or future authority for the held epoch."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "summary": "Promotion accepts deleted required citations and a hold list containing only a bare H1 identifier."
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "summary": "Four R7-freeze mutants need tests with a distinct simulated live default."
      },
      {
        "id": "S3",
        "severity": "should_fix",
        "summary": "Replay item (vi) asks production evaluation for freshness that the hold intentionally refuses."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["8458f797d0a7d9854d3799863ff3b9d1fd06285a"]},
      "expected": {"exit_code": 0, "tail_regex": "^8458f797d0a7d9854d3799863ff3b9d1fd06285a$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "This was a read-only design review. No proposed change or counterfactual test was executed.",
      "needs": "Lead to implement, run RED-then-GREEN tests, and commission a fresh route refutation."
    }
  ]
}
```

SEAT: GPT-6 — HOLD-BY-CONSTRUCTION-01

## Findings

**B1 — Hold the epoch at the point authority is created, and at arm.** H1 forbids *arming a claim-bearing window at 25G83*; it is broader than a ban on one file ID ([science addendum:158–164](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:158)). Today the loader checks an ID **after** `_acceptance_bound_from_authenticated_bytes` returns the artifact. Arm evidence calls that primitive directly, while admission and evidence read different pack fields ([calibration_bracketing.py:1197](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/calibration_bracketing.py:1197), [arm_readiness.py:6205](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/arm_readiness.py:6205), [arm_readiness_evidence.py:895](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/arm_readiness_evidence.py:895)). The mixed R7/held pack reached certified arm evidence in the refuter’s probe; that probe did not reach a number ([hold refuter 2:38–66](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/refuters/hold-refuter-2-opus.md:38)).

**Recommendation (inference):** Keep one immutable `HELD_CLAIM_EPOCHS` policy, matching macOS build `25G83` wherever it appears in an acceptance identity, a continued identity, or the authenticated window identity. Make the byte authenticator the sole producer of a *claim-authorized acceptance*: it authenticates the pin first, then refuses authority when either the artifact’s epoch or the proposed judged epoch is held. The loader, arm evidence, and operative-number lookup must use that result. Remove the public `allow_claim_held` boolean from claim-facing APIs. A separate, named governance inspection API may return authenticated **non-claim data**, but no claim-authorized object or `claim_eligible` result. This matters because the operatives table currently returns the held screen by ID alone, and bracket evaluation can mark an issued artifact claim-eligible after matching a continuation ([calibration_bracketing.py:590](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/calibration_bracketing.py:590), [calibration_bracketing.py:2199](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/calibration_bracketing.py:2199)).

The authenticator alone cannot satisfy H1’s **arming** clause. Give every claim-bearing arm path the same epoch-policy check against authenticated current identity, and refuse if that identity is unavailable; check it again when an arm receipt is consumed. Normalize `issued`, nested `issued_acceptance`, and `issued_artifact_id` into one declaration and refuse disagreement. A manual, marker-free campaign also needs a held-epoch refusal before claim collection or result publication: its preflight presently returns without pack admission ([run_campaign.py:1866](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/scripts/run_campaign.py:1866), [run_campaign.py:8091](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/scripts/run_campaign.py:8091)). These are applications of one policy, rather than separate file-ID hold lists. *(Recommendation/inference.)*

A **non-claim purpose** is a declared derivation session or reviewed governance replay/re-issue that can inspect calibration data but cannot issue an arm receipt, a passed claim bracket, or a floor. Authorize it through its authenticated session kind or a narrow governance API, never a CLI flag, environment variable, or arbitrary boolean. Route R requires two non-claim windows and an interim re-issue while H1 remains open ([cap addendum:191–208](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/20-cap-council/31-addendum-ruling.md:191)). The derivation-only capture path already requires a declared derivation-kind session, and derivation observations are excluded from claim bracket candidates ([validate_powermetrics_fiducial.py:2100](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/scripts/validate_powermetrics_fiducial.py:2100), [calibration_bracketing.py:1917](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/calibration_bracketing.py:1917)).

**Smallest coherent change (inference):** Change the policy, byte authenticator, loader, explicit re-authentication, operatives and bracket gate in `joulewise/calibration_bracketing.py`; normalize declarations and gate receipt creation/consumption in `joulewise/arm_readiness.py`; make `ACCEPTANCE_OWNER` use claim authority in `joulewise/arm_readiness_evidence.py`; gate ordinary capture preflight in `scripts/validate_powermetrics_fiducial.py` and manual claim entry in `scripts/run_campaign.py`. Give re-issue and replay tools the narrow non-claim inspection API. Retain R7 as default; its current setting is explicit ([calibration_bracketing.py:211–223](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/calibration_bracketing.py:211)).

**Counterfactual tests (recommendation):**

| Route | RED mutation or current defect → required GREEN result |
|---|---|
| Round 1, R7 pack/default | Move the default to held 25G83; an R7-declaring claim window at 25G83 must still fail the epoch arm gate and claim bracket. The earlier refuter showed why admission alone misses it ([contract refuter:19–36](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/refuters/contract-refuter-opus.md:19)). |
| Round 1, manual no-pack | Use the marker-free config and `claim_bearing=true`; fail before claim work, including with a held file named explicitly ([hold refuter:66–75](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/refuters/hold-refuter-astra.md:66)). |
| Round 2, B-1 | Both `issued=R7` plus nested held and `issued=R7` plus flat held must refuse admission **and** `ACCEPTANCE_OWNER`; ordinary committed single-ID shapes must remain accepted ([hold refuter 2:48–82](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/refuters/hold-refuter-2-opus.md:48)). |
| S-1 to S-4 | Direct authenticated held bytes must yield no claim authority; nonliteral `allow_claim_held=flag` and `**kwargs` must fail the census; held ID must yield no claim operative; a synthetic interim 25G83 issue and R7→25G83 continuation must both refuse. Each currently exposed surface is identified in the refuter ([hold refuter 2:84–99](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/refuters/hold-refuter-2-opus.md:84)). |

For an **unknown route**, add a failing-on-change AST census over production modules: every read of `configs/calibration/*.json`, call of the raw byte authenticator, construction of claim authority, and call using non-claim access must be in a reviewed allowlist with its purpose. Plant one new direct reader and one new authority constructor to show the census turns RED. An AST census bounds ordinary code drift; dynamic Python calls still need review. *(Recommendation/inference.)*

**S1 — Promotion completeness.** Require the specified citation objects and path/digest pairs *before* recursive hash verification; require H1 and H5–H7 with nonempty text. Deletion and empty-text tests should refuse. The present verifier runs only when both citation keys exist, and its hold check asks only whether an `H1` ID appears ([promote_calibration_candidate.py:75–108](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/scripts/promote_calibration_candidate.py:75), [contract refuter 2:119–145](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/refuters/contract-refuter-2-astra.md:119)).

**S2 — R7-freeze mutants.** They are equivalent **at this head** because the live default is R7; they are not equivalent to the intended freeze when the default later moves. Perturb the live default to a distinct sentinel in each test and assert the tool still names explicit R7. The four GREEN observations and their mutations are recorded in the mutation report ([mutation2/report.md:90–114](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/mutation2/report.md:90)).

**S3 — Replay item (vi).** Rule it as two checks: production evaluation refuses the held file; a specifically authorized non-claim replay reports authenticated *freshness data* without producing a passed, claim-eligible bracket. The current replay loads with the keyword, then explicit evaluation re-authenticates without it and refuses ([calibration_bracketing.py:1320–1340](/Users/edr/code/JouleWise-wt-holdc-sol-d528efb2/joulewise/calibration_bracketing.py:1320), [replay2/report.md:133–149](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/50-d138-issuance-seat/replay2/report.md:133)).

## Residual risk

A third refuter could still find a claim sink that treats plain authenticated data as authority, or an arm path without authenticated epoch identity. The split result types, arm refusal, and planted census failures make those additions visible in review; they do not prove arbitrary future Python code cannot bypass the policy. Keep H1 open until the implemented diff, counterfactuals, whole suite, and fresh refutation pass. *(Inference.)*