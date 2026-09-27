```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Classified all 533 S1 suite outcomes; synthetic evidence gaps dominate, while mock-window behavior and stale paper receipts need lead decisions.",
  "workspace": {
    "base_requested": "97082508..204424e6",
    "base_mode": "informational",
    "head_start": "42e2af3e460af1aef021ec2b5004a1121cdd4b52",
    "head_end": "42e2af3e460af1aef021ec2b5004a1121cdd4b52",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "synthetic bundle and capture fixtures", "action": "start_now"},
      {"row": "mock-window contract", "action": "needs_ruling"},
      {"row": "paper supply-map receipts", "action": "needs_ruling"},
      {"row": "S1 merge gate", "action": "wait_for"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -c '^(FAIL|ERROR): ' /tmp/s1-regress-scout-77b1bee2/row9.log",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["533"]},
      "expected": {"exit_code": 0, "tail_regex": "^533$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/s1-regress-scout-77b1bee2/run_reps.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["s1 assert:'bundle_read_failed' != 'bundle_strict_validation rc=1 secs=0.84", "main assert:'bundle_read_failed' != 'bundle_strict_validation rc=0 secs=2.46"]},
      "expected": {"exit_code": 0, "tail_regex": "main assert:.* rc=0 secs="}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/s1-regress-scout-77b1bee2/run_reps2.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["s1 pin:supply_map:whole_window_verdict rc=1 secs=10.24", "main pin:supply_map:whole_window_verdict rc=0 secs=23.84"]},
      "expected": {"exit_code": 0, "tail_regex": "main pin:supply_map:whole_window_verdict rc=0 secs="}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "S1 correctly refuses not_applicable mock members under Final texts v1.1 §12, but existing mock campaign and analysis workflows expect successful output. Preserving those workflows needs an explicit non-claim path or a revised contract; admitting not_applicable to claim-bearing windows would weaken the gate.",
      "needs": "Rule the mock non-claim workflow before a production change."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "S1 changed sources included in three paper-custody validator digests. Their receipt pins are outside the S1 write scope.",
      "needs": "Authorize and review a separate supply-map and receipt repin after the source diff is final."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "One window-duration test hard-links a repository fixture into TMPDIR; the required /tmp scratch location is on a different filesystem. A read-only runner substitution of copy for link reproduced the S1 gate failure and main pass.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Thirty-six outcomes are downstream assertions or nested-suite failures. Their deeper expectations require a full-suite rerun after the primary fixture and contract closures.",
      "needs": "Rerun row 9 after the primary repairs."
    }
  ]
}
```

## Failure groups

The complete inventory is [inventory.jsonl](/tmp/s1-regress-scout-77b1bee2/inventory.jsonl): **all 533 outcomes**, each with test ID, module, first exception line, group, and log line. It contains 478 distinct test IDs; subtests account for repeated IDs. Counts below are failures/errors. Line references are S1 changes in `git diff 97082508 204424e6`.

| Group | Count | First exception signature and S1 cause | Classification and closure |
|---|---:|---|---|
| G1 | 0/135 | `WindowBatteryRefusal: ... prospective bundle`; [bundle_read.py:326](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/bundle_read.py:326), [inputs.py:2824](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/analysis_engine/inputs.py:2824), and [whole_window.py:4078](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/whole_window.py:4078) now gate fabricated members. | **(a)** Give synthetic claim fixtures authenticated battery pairs and bound bytes, or assert the new refusal in negative tests. Test/fixture scope. Do not add their run IDs to the historical set. |
| G2 | 42/56 | `WindowBatteryRefusal: ... not_applicable`; [bundle_read.py:345](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/bundle_read.py:345) rejects mock members at window scope; [run_campaign.py:9032](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/scripts/run_campaign.py:9032) exposes this in campaign completion. | **Contract tension.** Claim-bearing refusal is ruled. Tests of claims should expect refusal or use battery-passing non-mock fixtures. Preserving successful *non-claim* mock workflows requires a separately ruled production path; treating `not_applicable` as a pass would weaken the gate. |
| G3 | 0/62 | `CustodyUnreadable: ... missing required artifact: metadata.json`; [bundle_read.py:311](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/bundle_read.py:311) authenticates members before consumers such as [aggregate.py:104](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/aggregate.py:104). | **(a)** Build complete synthetic members for claim tests; for malformed-member tests, assert custody refusal. Test/fixture scope. |
| G4 | 0/40 | `prospective bundle (config.json cannot be read)` in window or reader paths; [bundle_read.py:491](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/bundle_read.py:491) requires a digest-bound mock config when no pair or historical digest applies. | **(a)** Supply config and its metadata digest, then battery evidence where the member is claim-bearing. Test/fixture scope. |
| G5 | 20/61 | `config.json digest does not match metadata.config_sha256`, including strict-validation assertions; [bundle_read.py:491](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/bundle_read.py:491) and gated [bundle_read.py:616](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/bundle_read.py:616). | **(a)** Rebuild synthetic metadata/config bindings after fixture mutation. A copied or modified historical bundle loses its exact digest exemption; exempting it by run ID would weaken the gate. Test/fixture scope. |
| G6 | 0/20 | `CustodyUnreadable: ... instrument_evidence.json unreadable`; [calibration_bracketing.py:1841](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/calibration_bracketing.py:1841) now parses ledger-bound capture bytes. The three-window fixture hashes non-JSON placeholder bytes. | **(a)** Generate valid capture evidence, raw battery pair where required, and recompute fixture hashes and receipts. Test/fixture scope. |
| G7 | 0/17 | `CustodyFailure: ... instrument_evidence.json ... observed absent`; [calibration_bracketing.py:1821](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/calibration_bracketing.py:1821) reads the ledger locator before classification. | **(a)** Make synthetic custody locators resolve to bytes matching the ledger digest. Historical sequence alone does not excuse a missing recorded artifact. Test/fixture scope. |
| G8 | 1/9 | `instrument calibration battery_float_evidence_missing: pre ... post ...`; [controller.py:448](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/controller.py:448) authenticates attachment before its physics fields. | **(a)** Add a passing capture pair to synthetic attachments and update their manifest hashes. Test/fixture scope. |
| G9 | 23/0 | `stale supply-map receipt digest` for `d165_closeout` (12), `reported_energy_parents` (10), and `whole_window_verdict` (1). S1 changed pinned owners including [inputs.py:3195](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/analysis_engine/inputs.py:3195) and [whole_window.py:3791](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/whole_window.py:3791). | **(c)** Regenerate and review the validator-source digests, receipts, and dependent supply-map pins. This reaches production configuration outside S1’s ruled write scope; it needs separate authority. |
| G10 | 11/0 | `<RunStatus.FAILED> != <RunStatus.SUCCEEDED>` in powermetrics-backed synthetic runs. [controller.py:879](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/controller.py:879) and [controller.py:884](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/controller.py:884) now perform real pre/post probes unless a runner is injected. | **(a)** Inject a deterministic passing battery runner in these tests and retain probe failure behavior for real non-mock runs. Test/fixture scope. |
| G11 | 18/18 | Secondary first lines include `EvidenceAuthoringError: focused suite refused` (9), `KeyError: 'collection'` (5), `AssertionError: Lists differ` (6), `UnboundLocalError` (3), and changed refusal/output assertions. They follow G1–G8; the nested arm-readiness suite specifically reruns G6’s 20 failing tests. | Inherits the parent fixture closure, then rerun. Preserve the earlier gate and revise expectations where it intentionally changes refusal precedence. One campaign output-shape expectation may need a production contract ruling if the old record shape must survive refusal. |

**No failing group qualified for (b).** The ruled historical set is closed over exact committed bundle digests and tree identities. Several failing synthetic copies reuse historical-looking names, but their bytes differ or their recorded artifacts are absent. `order_manifest.json` appears as a warning in the log; it is not a distinct failure cause.

## Counts by module

Each cell is **failures/errors**; totals are **115/418**.

| Module | F/E | Module | F/E |
|---|---:|---|---:|
| test_run_campaign | 42/29 | test_calibration_bracketing | 0/6 |
| test_d165_dominance_closeout | 0/48 | test_epoch_continuation | 0/6 |
| test_analysis_integration | 0/47 | test_paper_rendering | 6/0 |
| test_floor_extraction | 4/28 | test_uncertainty_p2029 | 0/6 |
| test_aggregate | 0/27 | test_analysis_claims | 0/6 |
| test_check_window_provenance | 0/25 | test_audit_amplification | 4/0 |
| test_cli_run | 25/0 | test_pipeline_smoke_tail | 0/4 |
| test_window_duration_margins | 0/24 | test_phase_share | 0/3 |
| test_calibration_live_three_window | 0/20 | test_custody_mode_inventory | 0/3 |
| test_bracket_binding_cli | 0/19 | test_corpus_strict_validation | 0/3 |
| test_whole_window_selection | 3/15 | test_arm_readiness_evidence_author | 2/0 |
| test_paper_custody | 16/0 | test_d117_floor_qwen25_7b_plan | 0/1 |
| test_analysis_finalizer | 0/15 | test_powermetrics | 1/0 |
| test_mint_floor_artifact | 0/14 | test_cli | 1/0 |
| test_whole_window | 0/14 | test_d117_floor_qwen25_1p5b_plan | 0/1 |
| test_floor_mint_estimator | 0/12 | test_detection_floor | 0/1 |
| test_experiment | 0/12 | test_package_bundle_pack | 1/0 |
| test_launch_window | 0/11 | test_paper_reported_energy | 1/0 |
| test_p2038_production_path | 1/8 | test_partial_record_enclosure | 1/0 |
| test_collector_analysis_manifest_id | 7/1 | test_arm_readiness_dry_run | 0/1 |
| test_mint_floor_artifact_generalized | 0/7 | test_dominance_closeout | 0/1 |

## Paired confirmation and coverage gap

[reps.json](/tmp/s1-regress-scout-77b1bee2/reps.json) and [reps2.json](/tmp/s1-regress-scout-77b1bee2/reps2.json) record the exact test IDs, commands, return codes, and output files. Representatives of G1–G10 and secondary G11 failed on S1 and passed on main. The window-duration representative initially hit a `/tmp` hard-link permission error on **both** trees; substituting a copy for that fixture hard link in the runner exposed the expected S1 `config_sha256` refusal and a main pass. The nested arm-readiness representative also failed on S1 with 20 focused-suite errors and passed on main.

V1 covered S1’s selected reader, controller, sweep, and new consumer tests (477); V2 covered helper and envelope tests (343). Neither selected the 42 failing legacy modules. Their fixtures exercised exact historical entries, explicit mock reader admission, and injected controller runners. The builder’s 69-entry check verifies the frozen historical list, not temporary fixtures or paper receipt digests. Thus all targeted checks could pass while row 9 failed.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Fixture and expectation repairs (G1, G3–G8, G10) | start_now | — | Legacy tests and fixture builders; keep exact historical set closed |
| Mock workflow disposition (G2) | needs_ruling | — | Window and campaign production behavior |
| Paper receipt repin (G9) | needs_ruling | Final S1 source bytes | `configs/paper_supply/supply_map.json` and dependent receipts |
| Full-suite merge gate | wait_for | Fixture repairs, mock ruling, receipt repin | Integration tree and row 9 |

## Critical path

Settle the mock workflow contract and paper repin authority, land the fixture repairs, then rerun the full suite. The 36 secondary outcomes need that rerun to reveal any remaining independent failures. All three inspected repository trees remained clean; this scout wrote only under `/tmp/s1-regress-scout-77b1bee2/`.

SCOUT: COMPLETE