```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured B1–B3 and N1–N3, applied the approved test-coordinate update, and passed acceptance.",
  "workspace": {
    "base_requested": "f0fedc91",
    "base_mode": "exact",
    "head_start": "f0fedc91a5bf35189fed34962506b65d4903d8d8",
    "head_end": "f0fedc91a5bf35189fed34962506b65d4903d8d8",
    "upstream_end": null,
    "branch": "feat/2026-09-08-g2a-chain-routing"
  },
  "pathspec": [
    "tests/test_check_window_provenance.py",
    "tests/test_preflight.py",
    "tests/test_gen_g2_phase_d.py",
    "scripts/gen_g2_phase_d.py",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "docs/process_traces/2026-08-28-live-smoke/RUNSHEET.md",
    "docs/process_traces/2026-08-28-live-smoke/00-verification-notes.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_window_provenance tests.test_preflight tests.test_gen_g2_phase_d tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 110 tests in 29.131s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS generated Phase D matches pinned runbook bytes"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -k test_preflight_requires_documented_measurement_checkout_argument tests.test_check_window_provenance",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

- **B1:** Updated the argument-contract test for plan-derived root/head/interpreter. Before: `FAILED (failures=1)`, rc 1. After: `OK`, rc 0.
- **B2:** Added Phase A plan loading and verbatim `/usr/bin/jq` commands before consumers. Inspection: before `FAIL`, after `PASS`.
- **B3:** Added dated supersession pointers beside historical contracts. Both inspections: before `FAIL`, after `PASS`.
- **N1:** Added full-program missing-argument and mismatched-head tests; removed vestigial `REVIEWED_HEAD`. Previously absent coverage; after: `OK`, rc 0.
- **N2:** Replaced the missing-heading traceback with `FAIL runsheet section is missing: ## Plan-derived measurement variables`, rc 1.
- **N3:** Explained the intentional `bash` fence exclusion. Inspection: before `FAIL`, after `PASS`.

Applied the approved range update to `1534–1598`. Acceptance changed from `FAILED (failures=1)` to **110 tests, `OK`, rc 0**. Logs: [acceptance](/tmp/g2a-fix-acceptance-approved.log), [generator check](/tmp/g2a-generator-check-approved.log).

## Verification notes

No repository-wide suite, live measurement, or commit was performed. Changes remain ready for lead review.