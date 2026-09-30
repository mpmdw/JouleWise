```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Converted 26 IDs with assertions preserved; 10 distinct switch grants remain.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "8b6d64d4b382c0723ed85fc06717de862807c731",
    "head_end": "8b6d64d4b382c0723ed85fc06717de862807c731",
    "upstream_end": "8b6d64d4b382c0723ed85fc06717de862807c731",
    "branch": "test/2026-09-29-s1-battery-fixture"
  },
  "pathspec": [
    "tests/bfgs_fixtures.py",
    "tests/genuine_evidence.py",
    "tests/test_genuine_evidence.py",
    "tests/test_analysis_integration.py",
    "tests/test_bfgs_fixtures.py",
    "tests/test_floor_extraction.py",
    "tests/fixtures/d117_postcollection_trust/extraction_report.json",
    "tests/s1_evidence_probe.py",
    "tests/s1_evidence_comparison.md",
    "tests/s1_evidence_results.json",
    "tests/s1_evidence_ids.json"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B -m unittest tests.test_floor_extraction tests.test_bfgs_fixtures tests.test_genuine_evidence > /tmp/s1fix-artifacts/whole-floor-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 210 tests in 251.195s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B -c 'import runpy,sys; sys.argv=[\"/tmp/s1fix-artifacts/s1_evidence_probe.py\",\"today\",\"tests.test_analysis_integration\"]; runpy.run_path(sys.argv[0],run_name=\"__main__\")' > /tmp/s1fix-artifacts/whole-analysis-confirmed-results.jsonl 2> /tmp/s1fix-artifacts/whole-analysis-confirmed.log",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=8, errors=6)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B -c 'import json,runpy,sys; sys.argv=[\"/tmp/s1fix-artifacts/s1_evidence_probe.py\",\"charging\",*json.load(open(\"/tmp/s1fix-artifacts/converted.json\"))]; runpy.run_path(sys.argv[0],run_name=\"__main__\")' > /tmp/s1fix-artifacts/charging-final-results.jsonl 2> /tmp/s1fix-artifacts/charging-final.log",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=29)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=29\\)"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard python3 -B /tmp/s1fix-artifacts/final_inspection.py > /tmp/s1fix-artifacts/final-inspection.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Final inspection: PASS"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Final inspection: PASS"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Ten distinct IDs remain in both switch lists: 10 first-form entries and 10 second-form entries. Switch machinery cannot yet be deleted entirely.",
      "needs": "Lead review of the recorded refusing checks and remaining fixture work."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The complete analysis module retains 14 baseline nonpassing methods, with zero new nonpassing IDs. The repository-wide suite was not run; complete touched modules and per-ID trials were used for this fixture-only change.",
      "needs": "Lead-owned final verification."
    }
  ]
}
```

## Change

Converted all 23 ruled passers, the golden case, and two of the 16 baseline analysis failures. Existing assertions are unchanged.

The [50-ID table](/tmp/s1fix-artifacts/conversion-report.md) records every disposition and refusing check.

Removed and archived the [probe](/tmp/s1fix-artifacts/s1_evidence_probe.py), [comparison](/tmp/s1fix-artifacts/s1_evidence_comparison.md), and [results](/tmp/s1fix-artifacts/s1_evidence_results.json).

Changes remain uncommitted. Intended commits:

1. Add genuine evidence builders and refusal regressions.
2. Convert passing IDs, prune grants, repair missing fixture members, and re-pin fixture digests.

## Verification notes

All 26 converted IDs went RED under charging in the [final control run](/tmp/s1fix-artifacts/charging-final-results.jsonl).

The golden pin changed exactly five summary SHA-256 leaves, with zero numeric or other changes: [leaf diff](/tmp/s1fix-artifacts/golden-leaf-diff.json).

The analysis module retains 14 pre-existing nonpassing methods; all seven converted analysis IDs pass.

## Residual risk

Ten distinct switched IDs remain—20 entries across both lists. The machinery cannot yet be deleted entirely. Next step: lead review of the table’s remaining refusals and final verification.