```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Retired two landed lanes, registered A280–A290, regenerated state, and passed the named checks.",
  "workspace": {
    "base_requested": "8175a7ad",
    "base_mode": "descendant",
    "head_start": "78025bee4ea6c01369f0744e3ebfdc353488cae5",
    "head_end": "78025bee4ea6c01369f0744e3ebfdc353488cae5",
    "upstream_end": "8175a7adefacd6c8bd5a0992da8cdba935083bc9",
    "branch": "docs/2026-09-23-1d3796d5"
  },
  "pathspec": [
    "docs/process/state_kernel.json",
    "TASK_QUEUE.md",
    "RUN_STATE.md",
    "tests/test_gen_state.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "python3 scripts/gen_state.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 44 tests in 1.735s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 44 tests in .*s\\n\\nOK"}
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
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The requested heading says five PRs merged, while the activation record documents four merges during 1d3796d5. The pointer explicitly counts prior PR #394 as the fifth.",
      "needs": "Magistrate review of the heading’s count."
    }
  ]
}
```

## Change

Removed kernel keys `NOTICE-SUMMARY-V3-TEXT-01` (A276; PR #397, `1c59cc6b`) and `ZERO-CAPTURE-EVIDENCE-WRITER-01` (A277; PR #399, `8175a7ad`). Updated A270, A272 and A278, added the restart pointer, and regenerated the queue. The kernel now has **242 tasks**.

| Lane | Registered kernel key |
|---|---|
| A280 | `HEADLINE-SCORED-NIGHT-KIND-01` |
| A281 | `HEADLINE-PURE-MODULES-GATE-01` |
| A282 | `HEADLINE-AP5M-AMENDMENT-01` |
| A283 | `HEADLINE-DECODING-AND-RUNTIME-01` |
| A284 | `HEADLINE-AFFINE-LADDER-LEG-01` |
| A285 | `HEADLINE-SCORER-AUDIT-01` |
| A286 | `DIRECT-INSTALLER-SUCCESSOR-CHECK-01` |
| A287 | `LINUX-CI-TERM-DELAY-01` |
| A288 | `ARM-READINESS-ANCHOR-DELTA-LOAD-FLAKE-01` |
| A289 | `BRIEF-MANDATED-WORDING-RULE-01` |
| A290 | `D182-SUCCESSOR-CANNOT-RELICENSE-RULING-01` |

## Verification notes

`gen_state.py --check` exited 0; the named module passed **44 tests**. No workflow deviations. The five-PR heading interpretation is flagged above.