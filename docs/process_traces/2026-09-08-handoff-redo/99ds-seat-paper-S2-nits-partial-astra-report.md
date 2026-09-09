```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "N1, N2 and N5 implemented; N4 pin removed, but fence wiring and fixture repinning require expanded scope.",
  "workspace": {
    "base_requested": "e5eb5b8d",
    "base_mode": "exact",
    "head_start": "e5eb5b8d5c8b9217c1f895b659661375fd2dfe63",
    "head_end": "e5eb5b8d5c8b9217c1f895b659661375fd2dfe63",
    "upstream_end": null,
    "branch": "feat/2026-09-08-paper-S2"
  },
  "pathspec": [
    "docs/contracts/paper_supply_custody.md",
    "joulewise/paper_rendering.py",
    "joulewise/paper_reported_energy.py",
    "docs/contracts/paper_reported_energy.md",
    "tests/test_paper_rendering.py",
    "tests/test_paper_reported_energy.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_paper_reported_energy tests.test_paper_rendering tests.test_paper_custody tests.test_docs_freshness > /private/tmp/paper-S2-nits-acceptance.log 2>&1\nsuite_rc=$?\ncat /private/tmp/paper-S2-nits-acceptance.log\nprintf '\\nEXIT_CODE=%s\\n' \"$suite_rc\" >> /private/tmp/paper-S2-nits-acceptance.log\nexit \"$suite_rc\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=13)", "EXIT_CODE=1"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_paper_reported_energy.ReportedEnergyTests.test_nonpositive_prefill_denominator_precedes_surface_disagreement > /private/tmp/paper-S2-nits-denominator.log 2>&1\ncheck_rc=$?\nprintf '\\nEXIT_CODE=%s\\n' \"$check_rc\" >> /private/tmp/paper-S2-nits-denominator.log\ncat /private/tmp/paper-S2-nits-denominator.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK", "EXIT_CODE=0"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check > /private/tmp/paper-S2-nits-diff-check.log 2>&1\ncheck_rc=$?\nprintf 'EXIT_CODE=%s\\n' \"$check_rc\" >> /private/tmp/paper-S2-nits-diff-check.log\ncat /private/tmp/paper-S2-nits-diff-check.log\nexit \"$check_rc\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["EXIT_CODE=0"]},
      "expected": {"exit_code": 0, "tail_regex": "EXIT_CODE=0"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: actual gate registration is in paper_custody.py; changed owner-source bytes also invalidate fixture receipt and inventory pins in supply_map.json. Neither path was modified.",
      "needs": "Expand scope for the two requested paths, or provide a ruling identifying an in-scope registration hook."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Acceptance ran 91 tests with 13 failures, all reporting stale supply-map receipt digest: reported_energy_parents. The N2 regression cannot reach rendering until fixture pins are updated. Canonical full discovery was not run before this scope-blocked return.",
      "needs": "After authorized fixture repinning and N4 wiring, rerun acceptance and canonical discovery."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/paper_custody.py",
      "configs/paper_supply/supply_map.json"
    ],
    "reason": "The actual issuance registry is outside paper_reported_energy.py, and fixture custody pins bind the changed owner source.",
    "blocked_work": "N4 registration-fence enforcement and its regression; green fixture-dependent acceptance.",
    "minimal_change": "Connect the ordering-fence enforcement to the custody registration boundary without enabling production issuance, and update affected synthetic fixture receipt/inventory pins."
  }
}
```

## Change

- **N1:** Exhaustive public-entry wording → requested custody-seam/renderer-guard distinction and D-179 exception. Surrounding paragraph remains consistent.
- **N2:** Missing `cells` escaped as `StopIteration` → sentinel lookup and closed projection-mismatch refusal. Added missing/non-array regressions; the code already existed in the vocabulary, and its contract-table condition now includes rendering.
- **N4:** Removed the lane-local commit pin. Fence wiring and registration regression remain blocked on scope.
- **N5:** Agreement ran before positivity → nonpositive denominators now refuse `_denominator_invalid` first. Added zero/negative regressions.

N3 untouched. No commit made.

## Verification notes

The [acceptance log](/private/tmp/paper-S2-nits-acceptance.log) records 13 stale-fixture-pin failures. N5 passes independently; N2 execution remains blocked during fixture setup.

Next step: expand the two-path scope so registration enforcement and fixture repinning can be completed and verified.