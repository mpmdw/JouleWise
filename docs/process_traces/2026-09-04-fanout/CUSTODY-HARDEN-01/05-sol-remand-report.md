```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "D-138 custody is restored: reduce.py matches the issued pin, terminal consumers contain label-trust risk, and both touched test modules pass.",
  "workspace": {
    "base_requested": "a2e88e02fb45093aa9e183114cce5b7fc6a4ef56",
    "base_mode": "exact",
    "head_start": "a2e88e02fb45093aa9e183114cce5b7fc6a4ef56",
    "head_end": "a2e88e02fb45093aa9e183114cce5b7fc6a4ef56",
    "upstream_end": "a2e88e02fb45093aa9e183114cce5b7fc6a4ef56",
    "branch": "feat/2026-09-04-fan-CUSTODY-HARDEN-01"
  },
  "pathspec": [
    "docs/contracts/adapter_contracts.md",
    "docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/05-sol-remand-report.md",
    "joulewise/reduce.py",
    "tests/test_reduce.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/04-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse --verify HEAD && git rev-parse --short=8 HEAD && git branch --show-current && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "a2e88e02fb45093aa9e183114cce5b7fc6a4ef56",
          "a2e88e02",
          "feat/2026-09-04-fan-CUSTODY-HARDEN-01",
          "## feat/2026-09-04-fan-CUSTODY-HARDEN-01...origin/feat/2026-09-04-fan-CUSTODY-HARDEN-01",
          "?? docs/process_traces/2026-09-04-fanout/CUSTODY-HARDEN-01/04-delta-reaudit-round-1.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "a2e88e02fb45093aa9e183114cce5b7fc6a4ef56[\\s\\S]*feat/2026-09-04-fan-CUSTODY-HARDEN-01"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "shasum -a 256 joulewise/reduce.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc  joulewise/reduce.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc  joulewise/reduce.py$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_reduce.D078R01RegressionTests.test_d138_reduce_source_bytes_remain_at_issued_pin tests.test_run_campaign.AnchorFallbackCampaignGateTests.test_coordinated_mock_labels_cannot_override_custody_config",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.007s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_reduce tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 408 tests in 559.778s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 408 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
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
      "kind": "environment",
      "level": "nonblocking",
      "text": "The literal git checkout origin/main -- joulewise/reduce.py command could not create the linked-worktree index lock outside the writable sandbox; the two-hunk inverse patch restored identical origin/main bytes and V2 plus the hard-pin regression verify them.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The issued reducer retains its historical label-sensitive private helper until an atomic D-138 successor re-freeze; reducer-local eligibility remains non-authoritative, and every claim consumer must retain the custody-config triangle and terminal mock gates.",
      "needs": ""
    }
  ]
}
```

## Change

The estimator source is restored byte-for-byte to the issued D-138 pin. The
two reducer-internal regressions from the first landing were replaced by a
hard SHA-256 regression tied both to the literal issued digest and to the
D-079 acceptance artifact.

The hardening now lives at the terminal custody boundary: campaign and
whole-window consumers reopen the authenticated config and reject even a
coordinated metadata-plus-summary `mock` relabel when the config says
`powermetrics`. The adapter contract makes the D-138 containment explicit.
The NEG-8 external-corpus authentication, unissued pre-freshness rejection,
and evidence-binding diagnostic clarification remain intact.

## Verification notes

The requested checkout command was sandbox-blocked because this linked
worktree's shared Git index is outside the writable root. The inverse of the
exact two-hunk delta was applied instead; full-file SHA-256 proves equality.
Per the preflight rule, only the two touched test modules were run.

## Residual risk

Any future claim consumer that treats reducer-local eligibility as authority
would bypass the terminal containment. The contract now forbids that use;
changing the historical helper itself still requires the atomic D-138
successor re-freeze and dependent-pin reissue.
