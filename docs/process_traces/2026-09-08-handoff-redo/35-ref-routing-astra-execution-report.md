```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "No routing defects found: 74 tests passed; real-clone routing/refusal probes passed; retired-literal mutation was killed.",
  "workspace": {
    "base_requested": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "base_mode": "descendant",
    "head_start": "f0fedc91a5bf35189fed34962506b65d4903d8d8",
    "head_end": "f0fedc91a5bf35189fed34962506b65d4903d8d8",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 0, "nit": 0},
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_gen_g2_phase_d tests.test_preflight tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 74 tests in 9.264s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 74 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --emit-chain \"$TMPDIR/g2a-refuter-execution/chain\" --night-date 20260910 && /bin/zsh -n \"$TMPDIR/g2a-refuter-execution/chain\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n 'JouleWise-measurement-20260813|code/JouleWise/.venv|/Users/edr|20260813|\\.venv|code/JouleWise' \"$TMPDIR/g2a-refuter-execution/chain\" docs/process_traces/2026-08-28-live-smoke/preflight.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B \"$TMPDIR/g2a-refuter-execution/probe.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS all routing probes; no measurement/interpreter executed"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS all routing probes; no measurement/interpreter executed"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -B \"$TMPDIR/g2a-refuter-execution/mutation.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FAILED (failures=1)",
          "PASS historical fixed shell block byte-identical and marked SUPERSEDED"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "FAILED \\(failures=1\\).*PASS historical fixed shell block byte-identical and marked SUPERSEDED"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --check && /bin/bash -n docs/process_traces/2026-08-28-live-smoke/preflight.sh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated Phase D matches pinned runbook bytes"]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS generated Phase D matches pinned runbook bytes"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Actual packet contains nine files, not seven. HEAD is exactly one commit above the requested base; worktree remained clean.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Neither retired literal nor broader 20260813/code/JouleWise patterns remain in chain/preflight. Two absolute user paths remain: emitted chain:23 SHAKEDOWN_ROOT=/Users/edr/JouleWise-shakedown-g2/2026-08-29 and chain:70 G2A_ROOT=/Users/edr/JouleWise-shakedown-g2/g2-a-20260910. These are custody/output roots, not retired measurement routing.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "_run_chain_once exports the derived PY without checking its existence. Both emitted routing and preflight refuse early with 'FAIL measurement venv Python is missing or not executable'. Real Git head mismatch refused in both shell routes; the driver's gate returned night_plan_stale. Missing/relative roots were rejected by the parser and shell routes.",
      "needs": ""
    }
  ]
}
```

## Residual risk

No measurements or full hardware preflight were run. Positive shell checks executed routing prefixes with real Git and an executable sentinel; the driver launched only an environment-printing stub. Temporary reproduction scripts remain under `$TMPDIR/g2a-refuter-execution/`.