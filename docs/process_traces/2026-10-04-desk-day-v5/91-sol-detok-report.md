```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Built the BPE detokenizer during prepare, added reset shallow copies and fallback provenance, and passed all requested tests.",
  "workspace": {
    "base_requested": "b2ff2f36",
    "base_mode": "exact",
    "head_start": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
    "head_end": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
    "upstream_end": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
    "branch": "fix/2026-10-05-detokenizer-outside-prefill"
  },
  "pathspec": [
    "joulewise/adapters/mlx_runtime.py",
    "tests/test_mlx_runtime_detokenizer.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-detok python3 -m unittest discover -s tests -p 'test_mlx_runtime_detokenizer.py'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 0.006s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 6 tests in [0-9.]+s\\s+OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-detok python3 -m unittest discover -s tests -p 'test_mlx_runtime*.py'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 49 tests in 0.020s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 49 tests in [0-9.]+s\\s+OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-detok python3 -m unittest discover -s tests -p 'test_adapter*.py'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 2.076s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in [0-9.]+s\\s+OK"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-detok python3 /tmp/dd5-detok/check_installed_detokenizer.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: installed mlx-lm 0.31.3 BPE class, 16 identical token/text comparisons, isolated reset, no Metal imports"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS: installed mlx-lm 0\\.31\\.3 BPE class"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-detok/verify_scope.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: only two authorized files changed; HEAD unchanged; four pinned estimator files unchanged; diff whitespace clean"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^PASS: only two authorized files changed"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-detok python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The additional canonical suite was intentionally interrupted during unrelated arm_readiness tests after roughly 600 completed cases, with no failures reported before interruption. All requested focused suites passed.",
      "needs": "Lead completes the canonical suite before final acceptance."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Verification is fixture-only, including installed Python detokenizer classes; no live Metal or measurement validation was performed.",
      "needs": "Lead owns hardware qualification and the prospective registration note before _v5 collection."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Scope verification used a scratch Git snapshot; scripts/bridge baseline writes outside the exhaustive allowlist and no runner baseline manifest was supplied.",
      "needs": ""
    }
  ]
}
```

## Change

Preparation builds one exact-class BPE detokenizer. Generation receives reset shallow copies sharing its vocabulary map. Unsupported classes retain existing behavior, recorded in preparation metadata and generator provenance.

Six labeled fixture regressions cover timing, reset, fallback, suites, interrupted streams, and cleanup. Changes remain uncommitted; nothing was pushed.

## Verification notes

All requested tests passed. The additional canonical suite remains incomplete; its interrupted log is `/tmp/dd5-detok/full-suite.log`.

## Residual risk

Live hardware validation remains provisional. Lead review, canonical-suite completion, and the prospective registration note are the next steps.