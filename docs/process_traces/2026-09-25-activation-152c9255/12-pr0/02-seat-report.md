```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented and blob-pinned the canonical v1 claim replay golden within the three authorized paths.",
  "workspace": {
    "base_requested": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "base_mode": "exact",
    "head_start": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "head_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "upstream_end": "c034a56ff6684a28fc3c5af32c7da3e01c7e0e95",
    "branch": "test/2026-09-25-claimgate-pr0-golden"
  },
  "pathspec": [
    "scripts/capture_claim_replay_golden.py",
    "tests/golden/claimgate_v1_replay.json",
    "tests/test_claim_replay_golden.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 scripts/capture_claim_replay_golden.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["wrote tests/golden/claimgate_v1_replay.json"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "wrote tests/golden/claimgate_v1_replay\\.json"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_claim_replay_golden -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.297s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git hash-object tests/golden/claimgate_v1_replay.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["72148bfea157d4207bbbb85670dda411a12944cd"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "72148bfea157d4207bbbb85670dda411a12944cd"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## test/2026-09-25-claimgate-pr0-golden...origin/main",
          "?? scripts/capture_claim_replay_golden.py",
          "?? tests/golden/",
          "?? tests/test_claim_replay_golden.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "only the three WRITE_SCOPE paths"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide suite was stopped during a slow run; it produced no completion summary.",
      "needs": "Magistrate runs the canonical suite before acceptance."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The 09-19 replay uses checked-in recorded slot outcomes because the underlying measurement bundles are outside this repository.",
      "needs": ""
    }
  ]
}
```

## Change

The capture script writes a canonical golden covering five fixture families, two checked-in claim-verdict artifacts, seven analysis manifests, three analysis registries, and the 09-19 INCONCLUSIVE m=4 and FAIL m=7 decisions. The tests pin its git blob SHA and check that changing one numeric replay field breaks comparison. No `joulewise/` file changed; nothing was committed.

## Verification notes

The requested capture, focused tests, blob check, and scope check passed. The canonical suite remains incomplete after interruption; no suite verdict is claimed.