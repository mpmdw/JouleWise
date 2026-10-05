```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented D2, D4, D5 and C2 coverage; all 194 requested tests pass. Broader verification remains pending.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "d671e95c69edfc63dc4ffa00fbfd0983aebcb57d",
    "head_end": "d671e95c69edfc63dc4ffa00fbfd0983aebcb57d",
    "upstream_end": null,
    "branch": "lane/2026-10-05-b4-x12a"
  },
  "pathspec": [
    "joulewise/v5_qualification.py",
    "scripts/harvest_v5_g2b_window.py",
    "scripts/harvest_v5_qualification.py",
    "scripts/write_v5_qualification_plan.py",
    "tests/test_harvest_v5_g2b_window.py",
    "tests/test_v5_block4_x12a.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x12a PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/dd5-x12a/round2_baseline.py > /tmp/dd5-x12a/round2-replay-baseline-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=4)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=4\\)"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x12a PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_v5_block4_x7 tests.test_v5_block4_x2 tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_s1_desk_closeout tests.test_v5_s1_qualification tests.test_v5_qualification_plan tests.test_v5_block4_x12a > /tmp/dd5-x12a/round2-modules-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x12a PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/dd5-x12a/round2_digest_mutation.py > /tmp/dd5-x12a/round2-digest-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SINGLE_ROW_DIGEST_BASELINE=PASS",
          "SINGLE_ROW_DIGEST_GUARD_DELETION=KILLED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SINGLE_ROW_DIGEST_GUARD_DELETION=KILLED"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-x12a PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/dd5-x12a/round2_scope.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "WRITE_SCOPE=PASS; PINNED_ESTIMATORS=UNCHANGED; HEAD=UNCHANGED; STAGED=EMPTY; WHITESPACE=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "WRITE_SCOPE=PASS; PINNED_ESTIMATORS=UNCHANGED; HEAD=UNCHANGED; STAGED=EMPTY; WHITESPACE=PASS"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x12a PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests > /tmp/dd5-x12a/round2-canonical.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK.*$"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x12a PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/dd5-x12a/round2_canonical_baseline_probe.py > /tmp/dd5-x12a/round2-canonical-baseline-probe.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (errors=1)",
          "ROUND1_CANONICAL_PROBE=ARM_CONTEXT_SHA256_MISMATCH"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "ROUND1_CANONICAL_PROBE=ARM_CONTEXT_SHA256_MISMATCH"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-x12a PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/fixture_orphan_census.py --fail-on-orphans > /tmp/dd5-x12a/round2-fixture-census.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^\\[\\]$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery reported failures and was interrupted. Its first arm_context SHA-256 mismatch in tests/test_arm_readiness.py also reproduces on round 1. Other discovery failures were not individually attributed; out-of-scope files were preserved.",
      "needs": "Lead triage of baseline failures and completion of integration discovery."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denies ps. Fixture census exited 2, so orphan status is unverified.",
      "needs": "Lead rerun of scripts/fixture_orphan_census.py --fail-on-orphans in a permitted session."
    }
  ]
}
```

## Change

Reused the member assessment for admission aborts, separated observer faults from structural recovery, blocked third attempts after matching consecutive NULL refusals, and added the single-row digest test. Changes remain uncommitted; pinned estimators are unchanged.

## Verification notes

D2/D4/D5 reproduce four failures on round 1 and pass after the fixes. C2 passes against the existing guard and kills its deletion mutant.

All 194 requested tests pass. Lead next step: rerun the fixture census, triage the baseline arm-context failure, and complete integration discovery.