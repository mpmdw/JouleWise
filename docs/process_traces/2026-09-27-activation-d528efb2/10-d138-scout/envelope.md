```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "New loader code is required: an issued-form candidate currently fails admission on 11 governed D-126 dispositions. Inventory: 18 must-change paths, including 4 direct production pin files. Publication of issued bytes is the irreversible boundary; custody offload is separate. NEEDS_RULING: successor ID/path, disclosure carrier, and claim_eligible versus the H1 arm hold.",
  "workspace": {
    "base_requested": "c772b019",
    "base_mode": "exact",
    "head_start": "c772b019c2569a638e096ceebb619837580cc44c",
    "head_end": "c772b019c2569a638e096ceebb619837580cc44c",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-27-activation-d528efb2/10-d138-scout/report.md",
    "docs/process_traces/2026-09-27-activation-d528efb2/10-d138-scout/pin_inventory.tsv"
  ],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "D-138 issuance",
        "action": "needs_ruling",
        "wait_for": "Successor identity, disclosure placement, and H1 wording"
      },
      {
        "row": "Issuance archive packet",
        "action": "wait_for",
        "wait_for": "Issued generation; complete before custody offload"
      },
      {
        "row": "Cell-cap resize",
        "action": "do_not_start",
        "wait_for": "Separate later council ruling and D-138 transaction"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B scripts/issue_calibration_acceptance_generation.py --help",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["{check,battery-verdict,prepare-candidate,verify-members}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "check,battery-verdict,prepare-candidate,verify-members"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -B scripts/issue_calibration_acceptance_generation.py verify-members --artifact docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json --corpus-root /Users/edr/night-custody",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["member \"d079-epoch-25g83-derivation-w2-20260927-d10\": PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "member .*: PASS"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_calibration_bracketing tests.test_floor_mint_pinsets_schema tests.test_epoch_equivalence_check tests.test_acc_25g83_rev5 tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 290 tests in 173.906s", "FAILED (failures=1, skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The 25G83 successor identity/path and disclosure placement need a lead ruling before issued bytes are finalized.",
      "needs": "Rule the three Q7 questions in report.md."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The current loader rejects an otherwise issued-form candidate because it counts 11 D-126-disposed prior valid rows as illicit members.",
      "needs": "Authenticate disposition exemptions in the loader and add refusal regressions within the issuing PR."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The focused baseline had one live machine-probe failure: os_build was None; 290 tests ran, one failed and one skipped.",
      "needs": "Repeat that probe in the issuing gate on a suitable machine."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| D-138 issuance | needs_ruling | Q7 decisions, then loader repair and own gate | Issued artifact, registry, active defaults |
| Issuance archive packet | wait_for | Issuance; complete before custody offload | External custody archive |
| Cell-cap resize | do_not_start | Separate council ruling and later transaction | Four pinned estimator files |

## Critical path

The [report](/Users/edr/code/JouleWise-wt-d138-scout-d528efb2/docs/process_traces/2026-09-27-activation-d528efb2/10-d138-scout/report.md) contains Q1–Q7 and replay commands; the [pin inventory](/Users/edr/code/JouleWise-wt-d138-scout-d528efb2/docs/process_traces/2026-09-27-activation-d528efb2/10-d138-scout/pin_inventory.tsv) identifies the atomic changes. Rule Q7, repair the loader’s disposition handling, then review and gate the issued bytes in one D-138 PR. No pin or custody file was changed.