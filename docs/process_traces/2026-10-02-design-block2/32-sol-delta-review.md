```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "MERGE: no blocking delta defect found; 51 tests passed, three mutants were caught, and the plan-name mutant exposed a nonblocking test gap.",
  "workspace": {
    "base_requested": "d5b28bb859a5d9227b470c19029f7c1cfb8f1652",
    "base_mode": "exact",
    "head_start": "d5b28bb859a5d9227b470c19029f7c1cfb8f1652",
    "head_end": "d5b28bb859a5d9227b470c19029f7c1cfb8f1652",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGE",
    "findings": [
      {
        "id": "G2AD-01",
        "severity": "should_fix",
        "file:line": "tests/test_gen_g2a_window.py:219",
        "claim": "The wrong-plan-name assertion is masked by existing chain outputs. Removing the production filename guard leaves the test green.",
        "evidence executed": "The drop-plan-name scratch mutant passed all 21 authoring/generator tests. A separate fresh-output check showed head refusing other.json with 'plan output must be named night_plan.json', while the mutant successfully wrote it. The existing negative test reuses the chain produced earlier and therefore still raises ValueError from the existing-output fence."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/g2a-delta-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_harvest_g2a_window tests.test_gen_g2a_window tests.test_gen_g2_phase_d > /tmp/g2a-delta-review/baseline.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 51 tests in 33.990s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 51 tests.*\\n\\s*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-delta-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-delta-review/run_mutant.py drop-bounded > /tmp/g2a-delta-review/drop-bounded.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 30 tests in 14.118s", "FAILED (failures=5)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=5\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-delta-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-delta-review/run_mutant.py unconditional-copy > /tmp/g2a-delta-review/unconditional-copy.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 30 tests in 14.078s", "FAILED (failures=2)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-delta-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-delta-review/run_mutant.py never-refuse-copy > /tmp/g2a-delta-review/never-refuse-copy.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 30 tests in 13.980s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-delta-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-delta-review/run_mutant.py drop-plan-name > /tmp/g2a-delta-review/drop-plan-name.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 21 tests in 19.889s", "OK"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/g2a-delta-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/g2a-delta-review/extra_checks.py > /tmp/g2a-delta-review/extra-checks.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "span=17248 registered_window=19980",
          "head fresh-wrong-name: plan output must be named night_plan.json",
          "drop-plan-name fresh-wrong-name: accepted",
          "low-count: SELECT stdout=custody-only capture_made=False",
          "recover-no-capture: RECOVER stdout=custody-only capture_made=False",
          "recover-capture: RECOVER stdout=custody-only capture_made=True",
          "refused-copy: REFUSED stdout=custody-only capture_made=None"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "refused-copy: REFUSED stdout=custody-only"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/g2a-delta-review PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS generated Phase D matches pinned runbook bytes$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check 8a8635a7b d5b28bb85",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git rev-parse 8a8635a7b",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "d5b28bb859a5d9227b470c19029f7c1cfb8f1652",
          "8a8635a7ba40b41574fc4e7af898b5ad74cb73dd"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "V5's mutant survived; G2AD-01 identifies the masked negative assertion. The production filename guard passed the fresh-output check.",
      "needs": "Use fresh output coordinates and assert the filename-specific refusal in the negative test."
    }
  ]
}
```

## Findings

**G2AD-01 — should_fix, nonblocking:** The filename-negative test at `tests/test_gen_g2a_window.py:219` needs fresh output coordinates and a filename-specific error assertion.

All four mutants were executed:

| Mutant | Test that went red |
|---|---|
| Drop bounded check | `test_c1_clock_refused_small_members_are_invalid_and_window_recovers`, plus four others |
| Compare chain copies unconditionally | Both `test_c2_chain_copy_with_invalid_small_member_recovers_not_refused` and `test_c2_chain_copy_with_invalid_large_member_selects` |
| Never refuse chain-copy differences | `test_summary_byte_tamper_refuses_with_original_bytes_archived` |
| Drop plan-name check | None; all 21 tests passed |

Code-path inspection confirmed that **prefill overlap count does not determine member validity**. The harvest applies strict validity, succeeded status and bounded anchor before passing the valid-member set to the summarizer. Strict validation checks raw consistency and whole-request consumability without imposing a prefill-count threshold. Count 2 with phase eligibility false remained valid in the scratch check.

Staged-plan custody and chain paths remain in the night root. Documentation agrees with span **17248** and window **19980**. SELECT, RECOVER and REFUSED stdout contained custody information only, with no measured values. The worktree remained unchanged.

## Residual risk

Harvest fixtures mock raw validation, ledger authentication and bracket assessment. No live capture or full repository suite was run; this review covered the requested delta modules and scratch scenarios.