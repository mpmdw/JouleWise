```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Prospective clock policy replacement implemented; suite migration needs six additional authorized paths.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "784d12f1b996865c8cf4053bb70101804346ceae",
    "head_end": "784d12f1b996865c8cf4053bb70101804346ceae",
    "upstream_end": "1f49625f205e410be6925a019ebf56c99e1d333f",
    "branch": "fix/2026-10-04-doctrine-pin-network-time-off"
  },
  "pathspec": [
    "configs/arm_readiness/d117_row_registry_v2.json",
    "docs/contracts/arm_readiness_network_time_policy.md",
    "docs/phase_2/window_runbook.md",
    "joulewise/arm_readiness.py",
    "joulewise/arm_readiness_evidence.py",
    "tests/test_arm_readiness_evidence.py",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_receipt_histsem.py"
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
      "cmd": "TMPDIR=/tmp/dd5-docpin PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-docpin/pc tests/test_arm_readiness*.py tests/test_receipt_histsem.py > /tmp/dd5-docpin/changed-pytest.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["133 failed, 364 passed, 7 skipped, 32 warnings, 1061 subtests passed in 4921.57s (1:22:01)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "[0-9]+ passed.*subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-docpin PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-docpin/pc tests/test_arm_readiness*.py tests/test_receipt_histsem.py > /tmp/dd5-docpin/main-baseline-pytest.log 2>&1",
      "cwd": "/tmp/dd5-docpin/main-baseline",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["437 passed, 7 skipped, 54 warnings, 1259 subtests passed in 5929.58s (1:38:49)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "437 passed, 7 skipped"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-docpin PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-docpin/pc tests/test_arm_readiness_evidence.py tests/test_arm_readiness_schemas.py > /tmp/dd5-docpin/evidence-schema-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["66 passed, 1 warning, 417 subtests passed in 15.89s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "66 passed.*417 subtests passed"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-docpin PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-docpin/pc tests/test_arm_readiness_evidence.py::NetworkTimePolicyDoctrineTests tests/test_arm_readiness_schemas.py::ArmReadinessSchemaTests::test_live_policy_replaces_restore_in_all_35_row_profiles tests/test_receipt_histsem.py::ReceiptHistoricalSemanticsTests::test_archival_restore_fact_keeps_its_predicate_after_live_replacement > /tmp/dd5-docpin/focused-policy.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["5 passed, 1 warning, 8 subtests passed in 24.41s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5 passed.*8 subtests passed"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-docpin/verify-preservation.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Historical registry, pinset, all existing predicates and clock.network_time_off unchanged; live registry validates with 35 rows.",
          "live_registry_sha256=55973f12098312c484ba3664a4ddef22131b26a92ac08920de54191e4edaecda"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "unchanged; live registry validates with 35 rows"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-docpin PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/dd5-docpin/changed-unittest.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V7",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: prospective fixtures still inject the historical restore section; the registry expectation and three checked live views still select the retired row. No out-of-scope paths were modified.",
      "needs": "Authorize the six requested paths, migrate prospective fixtures and live views, and rerun the required suites."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "git add exited 128: worktree index.lock is outside the writable sandbox (Operation not permitted). Changes remain uncommitted; no push attempted.",
      "needs": "Lead commits the authorized diff; live registry admission requires committed HEAD bytes."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main and origin/main advanced during verification. Baseline comparison uses the exact starting main commit 784d12f1b996865c8cf4053bb70101804346ceae.",
      "needs": "Review integration against current main before landing."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The additional canonical unittest run used system Python 3.14.7 and was interrupted after the required pytest comparison completed and the scope block was established. It did not complete.",
      "needs": "Lead runs the canonical suite after prospective-fixture and live-view migration."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_arm_readiness_evidence_author.py",
      "tests/test_arm_readiness_dry_run.py",
      "tests/test_arm_readiness_registry.py",
      "docs/phase_2/alpha_arm_readiness.md",
      "docs/phase_2/beta_arm_readiness.md",
      "docs/phase_2/gamma_arm_readiness.md"
    ],
    "reason": "Required prospective-fixture and checked-live-view migration is outside the exhaustive write allowlist.",
    "blocked_work": "Resolve the remaining required-suite failures and synchronize all three 35-row live readiness views.",
    "minimal_change": "Remove historical §5A overrides from prospective author/dry-run fixtures, update the obsolete negative test and expected row ID, and replace the three live-view entries without rewriting archival evidence."
  }
}
```

## Change

Replaced the live row with `clock.network_time_policy` and its new predicate. Registry rules permit the new ID; all profiles retain exactly 35 rows. The deriver enforces current §5A doctrine and rejects reinstated restore instructions. Freeze/ARM select the new row.

Archival registry v1, historical predicates and pins remain unchanged. `clock.network_time_off` retains its expected missing-live-evidence refusal.

## Verification notes

The requested full pytest runs completed. The changed run recorded 89 distinct failing nodes, including failed subtests in its raw count. Two authorized test repairs subsequently passed in the complete evidence/schema rerun. Remaining failures require the six requested paths; details are in [comparison.json](/tmp/dd5-docpin/comparison.json).

The additional canonical run was interrupted and remains incomplete. Git staging was denied, leaving changes uncommitted. Resume with the requested scope expansion to migrate prospective fixtures and live views, rerun verification, and commit.