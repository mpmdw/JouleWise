```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Completed plan-derived chain, preflight, and driver routing; all 74 tests across the three touched modules pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "head_end": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "upstream_end": null,
    "branch": "feat/2026-09-08-g2a-chain-routing"
  },
  "pathspec": [
    "scripts/gen_g2_phase_d.py",
    "scripts/run_night.py",
    "docs/process_traces/2026-08-28-live-smoke/preflight.sh",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "docs/process_traces/2026-08-28-live-smoke/2026-09-08-g2a-chain-routing-report.md",
    "tests/test_gen_g2_phase_d.py",
    "tests/test_preflight.py",
    "tests/test_run_night.py",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest discover -s tests -p test_gen_g2_phase_d.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 8 tests in 0.292s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest discover -s tests -p test_preflight.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 8 tests in 1.008s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest discover -s tests -p test_run_night.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 58 tests in 7.593s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS generated Phase D matches pinned runbook bytes"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --emit-chain /private/tmp/g2a-routing-chain.zsh --night-date 20260908",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["emitted /private/tmp/g2a-routing-chain.zsh"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "emitted /private/tmp/g2a-routing-chain.zsh"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "/bin/zsh -n /private/tmp/g2a-routing-chain.zsh && /bin/bash -n docs/process_traces/2026-08-28-live-smoke/preflight.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

Completed `_run_chain_once`’s approved handoff: child root, head, and interpreter now come from the parsed plan and override inherited values. Historical source bytes and sidecar verification remain intact.

The [report](/Users/edr/code/JouleWise-wt-g2a-routing/docs/process_traces/2026-08-28-live-smoke/2026-09-08-g2a-chain-routing-report.md) records literal locations, consumed fields, refusal texts, and fail-before/pass-after evidence. No scope or ruling requests remain.

## Verification notes

Acceptance covers only the three named modules. Tests establish routing behavior, not live hardware readiness. No repository-wide suite, measurement run, production checkout creation, or commit occurred.