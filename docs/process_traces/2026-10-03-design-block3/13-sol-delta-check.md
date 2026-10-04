```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "DELTA: FAIL — harvest guard passes; 683 s is still not a conservative worst-case budget.",
  "workspace": {
    "base_requested": "68bf2301",
    "base_mode": "exact",
    "head_start": "68bf2301e5aaa7d0a3f5bdbd71c04e50d58c7d2a",
    "head_end": "68bf2301e5aaa7d0a3f5bdbd71c04e50d58c7d2a",
    "upstream_end": "871a43f620a64f95152f3e50467225d52d7faa9e",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "delta": "FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "tests/test_controller_retry_backoff.py:237",
        "claim": "The claimed worst-case budget underprices idle captures and omits startup and stop-side work.",
        "evidence": "Idle-slice deadline is 122.65 s; the clock span extends from pre_spawn through post_parse after drain, teardown and parsing."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/db3-delta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_controller_retry_backoff tests.test_gen_g2a_window tests.test_harvest_g2a_window tests.test_schemas",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 118 tests in 36.505s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/db3-delta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_harvest_g2a_window",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 52 tests in 26.159s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/db3-delta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/db3-delta/delete_guard.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/db3-delta PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/db3-delta/policy_matrix.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS 16 policy combinations {'SELECT': 1, 'campaign_policy_not_claim_grade': 9, 'schema_refusal': 6}"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS 16 policy combinations"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — should_fix — `tests/test_controller_retry_backoff.py:237`: incomplete conservative budget.**

The token counts are correct: one warmup emits up to four tokens, followed by 512 measured tokens; both use the 4096-token prompt. Three in-stream guards each execute five commands with three-second timeouts, correctly totaling 45 seconds. Settling and dwell contribute 5+1 seconds. Model load precedes sampler startup; thermal observations use cached records.

However, 104 seconds is empirical. The idle-slice deadline permits `(751 × 0.1 × 1.5)+10 = 122.65` seconds per attempt, before subsequent processing. Startup readiness/rollover, drain (up to 5.45 seconds), teardown/census, and parsing before `post_parse` lack explicit allowances (`powermetrics.py:532,623,1256`; `sampler_teardown.py:29`). Prefill ≤10 seconds and decode ≥5 tokens/s are assumptions, not enforced runtime bounds.

Under the stated assumptions, longest-rung budgets are 630.6 seconds for the small model at 10 tokens/s and 682.2 seconds for the large model at 5 tokens/s. Both share the omissions. Revise the budget or label it empirical.

At 683 seconds, the adjusted synthetic bound is **4.49949 ms** at 3.2 ppm; it reaches 5 ms at approximately **3.933 ppm**, including stamp-envelope, resolution, and padding terms. At 983 seconds it is **5.45960 ms**. These calculations do not establish that 300 seconds is unsafe.

Harvest checks pass: both block policies SELECT. All 16 policy combinations behave correctly; nine schema-valid non-claim-grade combinations receive the named refusal, and six fail schema validation. Deleting only the guard in memory produces two test failures.

## Residual risk

Fixture and synthetic verification only; supplied block-2 drift/half-width observations were not independently reread. Worktree unchanged.