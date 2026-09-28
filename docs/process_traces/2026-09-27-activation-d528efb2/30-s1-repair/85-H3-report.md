```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented both test-only parity switches, closed-list sweeps, gate regressions, and bound fixture repairs.",
  "workspace": {
    "base_requested": "601a06c5",
    "base_mode": "exact",
    "head_start": "601a06c5c2712fa2ea1d8aada078c05ccd12b38e",
    "head_end": "601a06c5c2712fa2ea1d8aada078c05ccd12b38e",
    "upstream_end": null,
    "branch": "fix/2026-09-28-s1-r3-H3"
  },
  "pathspec": [
    "tests/bfgs_fixtures.py",
    "tests/test_bfgs_fixtures.py",
    "tests/test_bfgs_consumer_sweep.py",
    "tests/test_bfgs_window_consumers.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -u -m unittest tests.test_bfgs_fixtures tests.test_bfgs_consumer_sweep tests.test_bfgs_window_consumers tests.test_bundle_read tests.test_battery_float > /private/tmp/h3_final_modules.log 2>&1; result=$?; tail -n 14 /private/tmp/h3_final_modules.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 331 tests in 1857.032s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 331 tests in .*s"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -c 'import sys; sys.path.insert(0, \".\"); exec(compile(open(\"/private/tmp/h3_parity_mutants.py\").read(), \"/private/tmp/h3_parity_mutants.py\", \"exec\"))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["G7 RED failures=3 errors=0", "sweep1 RED failures=1 errors=0", "sweep2 RED failures=1 errors=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "sweep2 RED failures=1 errors=0"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The lead-owned Rule 5 switched-on coverage census was not supplied to this seat; no additional direct test was identified as owed from that record.",
      "needs": "Lead checks the census before admitting test IDs and returns any uncovered check for a scoped direct test."
    }
  ]
}
```

## Change

`exemption_parity(test_id)` applies the first switch for a granted ID and the second switch only for an ID on its second list. **Both ID lists remain empty** for the lead to fill. The closed lists are:

```python
PARITY_SWITCHED_OFF = (
    ("joulewise/analysis_engine/inputs.py", "anchor_fallback_member_unusable"),
    ("joulewise/floor_extraction.py", "_cpu_admission_bundle_reasons"),
    ("scripts/run_campaign.py", "_current_member_environment_refusals"),
    ("scripts/run_campaign.py", "_member_readiness_reasons"),
)

PARITY_SECOND_FORM_SWITCHED_OFF = (
    "AuthenticatedConsumptionSession._prepare",
    "_manifest_members",
    "_reference_energy_evidence",
    "mint_neg8_drift_bound_artifact",
    "_derived_neg8_decision",
    "_manifest_bundle_paths",
    "_current_core_rederivation_reasons",
    "_validate_row_uncached",
    "_row_references_current_strict_member",
    "whole_window_refusal_reasons",
    "whole_window_drift_allowances",
)
```

Added H-15–H-22, G-1–G-7, and AST sweeps for both lists. H-19 also checks the full registered corpus: all 30 bundles are `included` with no base reasons. The three §4.3 passing fixture calls now use `real=True`; their assertions are unchanged. No replay keyword or test ID was added.

## Verification notes

Every row below was GREEN in the final 331-test run and RED under its in-memory plant. The plants were restored when the mutation process exited.

| Test | Planted defect that turned it RED |
|---|---|
| H-15 | Remove the first property switch |
| H-16 | Remove the ID guard |
| H-17 | Substitute a passing pair for the charging pair |
| H-18 | Bypass the bound-config gate |
| H-19 | Remove the second switch |
| H-20 | Apply the second switch to a first-list-only ID |
| H-21 | Substitute a passing pair for the charging pair |
| H-22 | Bypass the bound-config gate |
| G-1 | Make the new gate method always refuse |
| G-2 | Bypass its bound-config check |
| G-3 | Remove its mock-config refusal |
| G-4 | Remove its config-detail refusal |
| G-5 | Check config before preserving a non-pass pair verdict |
| G-6 | Check config before authenticating raw battery bytes |
| G-7 | Bypass the reader’s bound-config check |
| Sweep 1 | Add a sixth production exemption use |
| Sweep 2 | Add a twelfth second-form caller |

## Residual risk

The lead must complete the Rule 5 coverage census before granting parity IDs. No NEEDS_RULING arose in this seat.