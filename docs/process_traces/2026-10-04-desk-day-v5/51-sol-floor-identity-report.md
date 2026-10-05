```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Fixed both floor decode declarations and added regression coverage; focused suite passed, but clone freezes refused without Metal access.",
  "workspace": {
    "base_requested": "784d12f1b996865c8cf4053bb70101804346ceae",
    "base_mode": "exact",
    "head_start": "784d12f1b996865c8cf4053bb70101804346ceae",
    "head_end": "784d12f1b996865c8cf4053bb70101804346ceae",
    "upstream_end": "784d12f1b996865c8cf4053bb70101804346ceae",
    "branch": "fix/2026-10-04-v5-floor-decode-identity"
  },
  "pathspec": [
    "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
    "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
    "tests/test_d117_floor_qwen3_v5_generate.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-flid /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-flid/pc tests/test_d117_floor_qwen3_v5_generate.py tests/test_identity_pins.py tests/test_d117_contrast_v5_pack.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["112 passed, 1 warning, 204 subtests passed in 154.00s (0:02:34)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "112 passed, 1 warning, 204 subtests passed"
      }
    },
    {
      "id": "V2",
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
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-flid /Users/edr/code/JouleWise/.venv/bin/python scripts/project_identity_pins.py freeze /tmp/dd5-flid/clone/configs/campaigns/d117_floor_qwen3-1p7b_v5",
      "cwd": "/tmp/dd5-flid/clone",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "  \"reason_codes\": [",
          "    \"readiness_identity_artifact_unreadable\"",
          "  ],",
          "  \"status\": \"REFUSE\"",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"status\": \"PASS\""
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-flid /Users/edr/code/JouleWise/.venv/bin/python scripts/project_identity_pins.py freeze /tmp/dd5-flid/clone/configs/campaigns/d117_floor_qwen3-8b_v5",
      "cwd": "/tmp/dd5-flid/clone",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "  \"reason_codes\": [",
          "    \"readiness_identity_artifact_unreadable\"",
          "  ],",
          "  \"status\": \"REFUSE\"",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"status\": \"PASS\""
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-flid /Users/edr/code/JouleWise/.venv/bin/python scripts/project_identity_pins.py freeze /tmp/dd5-flid/clone/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
      "cwd": "/tmp/dd5-flid/clone",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "  \"reason_codes\": [",
          "    \"readiness_identity_artifact_unreadable\"",
          "  ],",
          "  \"status\": \"REFUSE\"",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"status\": \"PASS\""
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Worktree commit failed with exit 128: sandbox denied index.lock creation in the canonical repository's shared Git metadata. Changes remain uncommitted as authorized; the patch was committed only in the scratch clone.",
      "needs": "Lead commits the three authorized changes."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "All three clone freezes returned rc 2 with readiness_identity_artifact_unreadable because MLX reported No Metal device available. No projection receipts were written. Clone-only empty checkpoint commits followed each refusal.",
      "needs": "Lead reruns clean-tree projections in a Metal-accessible session."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The requested focused suite ran; canonical unittest discovery did not run in this seat.",
      "needs": "Lead includes the canonical suite in final verification."
    }
  ]
}
```

## Change

Both decode declarations now include `prompt_tokens: None`, matching contrast. The regression generates both floors at a synthetic ladder pin, checks every config against its typed projection, and confirms that removing the field triggers `readiness_identity_environment_dirty`.

## Verification notes

The `--no-local` clone received the committed scratch patch and desk-branch pin custody. Both floors generated and passed generator checks; contrast generated as a control. Every freeze reached the Metal-access refusal recorded above.

Worktree changes remain uncommitted. Nothing was pushed; pinned estimator files were untouched. Evidence is in [proof-summary.json](/tmp/dd5-flid/proof-summary.json), and the scratch clone is clean at `2fcf6eef3b4e115f0e2e60aecfeaaf3c4a5cd15e`.

Next: commit the worktree changes and rerun the projections with Metal access.