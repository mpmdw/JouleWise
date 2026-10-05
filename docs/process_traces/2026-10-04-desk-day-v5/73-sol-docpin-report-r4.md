```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "F1–F5 implemented; requested suite passed; sandbox blocked staging and fixture census.",
  "workspace": {
    "base_requested": "3180dafb",
    "base_mode": "exact",
    "head_start": "3180dafb81eb1b73a9265cb533746eb825fa7df5",
    "head_end": "3180dafb81eb1b73a9265cb533746eb825fa7df5",
    "upstream_end": "3180dafb81eb1b73a9265cb533746eb825fa7df5",
    "branch": "fix/2026-10-04-doctrine-pin-network-time-off"
  },
  "pathspec": [
    "joulewise/arm_readiness_evidence.py",
    "docs/contracts/arm_readiness_network_time_policy.md",
    "docs/process/rehearsal-operator-card.md",
    "tests/test_arm_readiness_evidence.py"
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
      "cmd": "TMPDIR=/tmp/dd5-docpin4 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-docpin4/pc tests/test_arm_readiness_evidence.py tests/test_arm_readiness_schemas.py tests/test_receipt_histsem.py tests/test_arm_readiness_registry.py tests/test_docs_freshness.py tests/test_arm_readiness_evidence_author.py tests/test_arm_readiness_dry_run.py tests/test_arm_readiness_evidence_packauth.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["243 passed, 1 skipped, 54 warnings, 1181 subtests passed in 3346.09s (0:55:46)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^243 passed, 1 skipped, .*1181 subtests passed in "
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --quiet 85d67b12 HEAD -- configs/arm_readiness/d117_row_registry_v1.json configs/campaigns 'tests/fixtures/histsem*'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --quiet 85d67b12 -- configs/arm_readiness/d117_row_registry_v1.json configs/campaigns 'tests/fixtures/histsem*'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-docpin4 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "git add -- joulewise/arm_readiness_evidence.py docs/contracts/arm_readiness_network_time_policy.md docs/process/rehearsal-operator-card.md tests/test_arm_readiness_evidence.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-docpin/index.lock': Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox denied ps, so the fixture-orphan census could not complete.",
      "needs": "Lead should rerun the census outside this sandbox before quiet-machine work."
    },
    {
      "id": "ENV2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Sandbox denied Git index.lock creation. Changes remain uncommitted; nothing was pushed.",
      "needs": "Lead can review and commit the four-file diff."
    }
  ]
}
```

## Change

Implemented structural sentence checks across governed runbook sections and §11/§12, restored the two-backup check, and rejected clock-control tokens in frozen recipes. Superseded the operator card’s restore instruction while retaining history, and reused the retired-doctrine fixture.

Regression coverage includes all 16 Fable lines, the three weakening edits, every scanned section, current doctrine, and pure re-wrapping.

## Verification notes

Initial fixture-helper failures were corrected before the full green run. The expected skip concerns an unminted successor pinset. Archival bytes remain identical.

Staging and process census were blocked by sandbox permissions. Changes are uncommitted; no push or background job was started.