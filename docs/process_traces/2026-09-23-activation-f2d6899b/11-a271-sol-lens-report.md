```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Two blockers: a slow t0 log read can miss a qualifying spawn, and arm commands can wait indefinitely before Wi-Fi restoration.",
  "workspace": {
    "base_requested": "971e60d8",
    "base_mode": "exact",
    "head_start": "f81e34ec079bfda56c0b0132fe98135355006193",
    "head_end": "f81e34ec079bfda56c0b0132fe98135355006193",
    "upstream_end": "f81e34ec079bfda56c0b0132fe98135355006193",
    "branch": "feat/2026-09-23-a271-corecaptured"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "path": "joulewise/night_gate.py",
        "line": 1515,
        "summary": "The ten-minute cutoff uses the clock after the log read, so probe duration can erase a spawn from the read window.",
        "evidence": "V2"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "path": "joulewise/evidence_night.py",
        "line": 849,
        "summary": "Arm commands have no timeout; a hung Wi-Fi-off command prevents the finally block from attempting Wi-Fi-on.",
        "evidence": "V3"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "path": "joulewise/corecaptured_loop.py",
        "line": 40,
        "summary": "A harmless trailing blank or continuation line makes the entire arm observation fail.",
        "evidence": "V4"
      },
      {
        "id": "F4",
        "severity": "nit",
        "path": "tests/test_night_gate.py",
        "line": 340,
        "summary": "The focused tests do not protect either exactly-two precheck threshold.",
        "evidence": "V5"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["200 passed, 265 subtests passed in 735.75s (0:12:15)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "200 passed"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/window_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["delay 0 count 3 refusal night_refused_not_quiet", "delay 30 count 2 refusal None"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "delay 30 count 2 refusal None"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/hang_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["after_hung_off alive True off 1 on 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "alive True off 1 on 0"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["header_only count 0", "empty ValueError corecaptured log has no syslog header", "trailing_blank ValueError corecaptured log has an unparseable line", "continuation ValueError corecaptured log has an unparseable line"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "trailing_blank ValueError"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/mutate.py t0_gt_to_ge",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["2 passed, 81 deselected, 2 subtests passed in 0.11s", "MUTANT_RESULT t0_gt_to_ge 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTANT_RESULT t0_gt_to_ge 0"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/mutate.py arm_before_le_to_lt",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["4 passed, 110 deselected in 13.31s", "MUTANT_RESULT arm_before_le_to_lt 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTANT_RESULT arm_before_le_to_lt 0"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/mutate.py arm_after_ge_to_gt",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["1 failed, 3 passed, 110 deselected in 13.38s", "MUTANT_RESULT arm_after_ge_to_gt 1"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "MUTANT_RESULT arm_after_ge_to_gt 1"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/mutate.py window_600_to_60",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["2 failed, 1 passed, 2 subtests passed in 0.05s", "MUTANT_RESULT window_600_to_60 1"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "MUTANT_RESULT window_600_to_60 1"
      }
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-execution/mutate.py wait_180_to_0",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["2 failed, 2 passed, 110 deselected in 13.57s", "MUTANT_RESULT wait_180_to_0 1"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "MUTANT_RESULT wait_180_to_0 1"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Log variants and hangs were simulated; no live machine commands were run.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — BLOCKER — [night_gate.py](/Users/edr/code/wt-f2d6899b-a271/joulewise/night_gate.py:1515).** Three spawns at 590, 300, and 1 seconds before a log read trigger `night_refused_not_quiet` when the read is immediate. When the fake read takes 30 seconds, the same returned rows count as two and `_check_machine` does not refuse. The production t0 runner has a 30-second timeout, but that duration is enough to change this verdict. Evidence: V2.

- **F2 — BLOCKER — [evidence_night.py](/Users/edr/code/wt-f2d6899b-a271/joulewise/evidence_night.py:849).** The production arm actuator calls `probe_command` without a timeout. With three initial spawns and a fake Wi-Fi-off command that waits, the check remains active and Wi-Fi-on has not been attempted (`alive True off 1 on 0`). Exceptions from off or the eight-second wait *do* reach the restore attempt; a command that never returns does not. Evidence: V3 and the executed `probe_command` inspection (`production_timeout None`).

- **F3 — SHOULD-FIX — [corecaptured_loop.py](/Users/edr/code/wt-f2d6899b-a271/joulewise/corecaptured_loop.py:40).** A header followed by a trailing blank line or a message continuation raises `ValueError`; at arm time the trailing-blank input becomes `Refused corecaptured log not measured: corecaptured log has an unparseable line`. At t0, the caller records `not_measured`, which is the required fail-safe outcome. Header-only output measures zero; empty output raises the missing-header error. Evidence: V4 and the direct arm probe.

- **F4 — NIT — [test_night_gate.py](/Users/edr/code/wt-f2d6899b-a271/tests/test_night_gate.py:340), [test_evidence_night.py](/Users/edr/code/wt-f2d6899b-a271/tests/test_evidence_night.py:891).** Exactly two initial spawns correctly pass without a toggle in an executed boundary probe, but mutations of t0 `> 2` to `>= 2` and arm precheck `<= 2` to `< 2` survive the focused tests (V5–V6). The post-toggle `>= 2`, 600-second window, and 180-second wait mutations are killed (V7–V9).

## Residual risk

The parser counted the supplied full capture and ignored `service inactive` and `gui/` rows; timezone offsets were parsed as instants. A spawn timestamp equal to toggle completion was excluded, while a later timestamp was included. Source inspection shows the arm census runs before the corecaptured check and `machine_quiet` runs after it; whether remediation should proceed when an earlier census check failed is **NOT EXECUTED**. The repository worktree remained clean.