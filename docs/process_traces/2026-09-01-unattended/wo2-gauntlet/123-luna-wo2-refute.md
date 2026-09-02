```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FIX-ROUND: execution review found five blockers and one over-restrictive overrun guard.",
  "workspace": {
    "base_requested": "89d58e80",
    "base_mode": "descendant",
    "head_start": "89d58e80",
    "head_end": "8f3d4adfcebfa03f3e6020a47ff61af1160829c4",
    "upstream_end": "8f3d4adfcebfa03f3e6020a47ff61af1160829c4",
    "branch": "feat/2026-09-01-night-driver"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "value": "FIX-ROUND",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "file": "configs/launchd/com.joulewise.night.plist.template:9-14",
        "input": "Clean launchd-style environment invoking the absolute script path.",
        "observed": "ModuleNotFoundError: No module named 'joulewise' before argument parsing.",
        "expected": "The installed LaunchAgent reaches the driver."
      },
      {
        "id": "B2",
        "severity": "blocker",
        "file": "scripts/run_night.py:431-436; docs/process/NIGHT_COURIER_PROMPT.md:7",
        "input": "Courier Popen recording from an arbitrary working directory.",
        "observed": "Popen supplies only start_new_session; the prompt uses relative docs/process/NIGHT_HANDBACK.md, and claude depends on inherited PATH.",
        "expected": "Courier has deterministic cwd/PATH or absolute paths."
      },
      {
        "id": "B3",
        "severity": "blocker",
        "file": "scripts/run_night.py:252-263",
        "input": "Chain wait raises TimeoutExpired after both SIGTERM and SIGKILL.",
        "observed": "Abort returns with no chain.exited; run_night proceeds to result/durable record/courier while the child may still exist.",
        "expected": "No courier or completion path until chain termination is proven."
      },
      {
        "id": "B4",
        "severity": "blocker",
        "file": "scripts/run_night.py:495-496,542-543",
        "input": "Malformed plan file containing {}.",
        "observed": "PlanError escapes uncaught; no refusal, result, durable record, or courier.",
        "expected": "Registered night_plan_malformed refusal and reporting path."
      },
      {
        "id": "B5",
        "severity": "blocker",
        "file": "scripts/run_night.py:615,676-708",
        "input": "Valid green REHEARSAL_STUB plan via rehearse.",
        "observed": "Popen runs /bin/zsh -c 'sleep 2; echo REHEARSAL' and creates chain.started.",
        "expected": "REHEARSAL_STUB never runs a chain under the supplied contract."
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "file": "scripts/run_night.py:552-556",
        "input": "Local t0=06:30 and window_max_s=600.",
        "observed": "Driver adds 840 seconds of backoffs and refuses; maximum accepted window becomes 360 seconds.",
        "expected": "R-7 guard adds only the 600-second deadline, permitting up to 1200 seconds before 07:00."
      },
      {
        "id": "N1",
        "severity": "nit",
        "file": "tests/test_run_night.py:189-331",
        "input": "Mutation-shaped suite audit.",
        "observed": "Dropping start_new_session and moving chain.exited after durable push survive; O_EXCL, wrong census constant, and skipped killpg are caught.",
        "expected": "Tests assert process-session isolation and chain.exited ordering."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 58 tests in 0.044s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 58 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "env -i PATH=\"$PATH\" /usr/bin/env python3 \"$PWD/scripts/run_night.py\" --help",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["ModuleNotFoundError: No module named 'joulewise'"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "usage:.*"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "zsh -n scripts/install_night_agent.sh",
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
      "id": "V4",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The checkout advanced from requested 89d58e80 to descendant 8f3d4ad during review; the descendant was reviewed and is now upstream-aligned.",
      "needs": "Lead confirmation that descendant review is acceptable."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The supplied contract says REHEARSAL_STUB never runs a chain, while D-169 R-4 describes a dry-run stub chain.",
      "needs": "Resolve which rehearsal semantics controls before merge."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No real chain, claude, launchctl, or push was executed, per review restrictions.",
      "needs": "Stage-2 live LaunchAgent acceptance."
    }
  ]
}
```

## Findings

B1–B5 are blockers. S1 is a should-fix. N1 records surviving test mutants.

## Residual risk

The normal, failure, census-abort, 95-second cadence, clone argv, deadline-kill, emitter, dead-man, DST, and sidecar probes passed in isolated scratchpad shims. No repository files were changed.