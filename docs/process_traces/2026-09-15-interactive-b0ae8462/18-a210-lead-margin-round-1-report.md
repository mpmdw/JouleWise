```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Reduced the install pad to 120 seconds, yielding a 27-minute cutoff; shortening the resident ladder requires two additional documentation paths.",
  "workspace": {
    "base_requested": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "base_mode": "exact",
    "head_start": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "head_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "upstream_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "branch": "feat/2026-09-15-lead-margin"
  },
  "pathspec": [
    "scripts/run_night.py",
    "scripts/magistrate_watchdog.py",
    "tests/test_run_night.py",
    "tests/test_magistrate_watchdog.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1-RED",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_run_night.NightDriverTests.test_install_close_precedes_the_plan_span_by_the_margin tests.test_run_night.NightDriverTests.test_fixed_epoch_install_close_is_1799998380",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 3600 != 120",
          "AssertionError: 1799998380 != 1799994900",
          "Ran 2 tests in 0.202s",
          "FAILED (failures=2)",
          "real 0.54"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V2-GREEN",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 101 tests in 19.037s",
          "OK",
          "real 19.37",
          "user 15.83",
          "sys 2.02"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 101 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 94 tests in 2.399s",
          "OK",
          "real 2.90",
          "user 1.89",
          "sys 0.57"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 94 tests[\\s\\S]*OK"
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --exit-code -- joulewise/night_gate.py",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_RULING + scope_expansion; no scope violation occurred. MAGISTRATE_RELAUNCH_PROMPT.md:17 instructs exit within nine minutes, incompatible with the proposed two-minute REQUEST-to-TERM interval. MAGISTRATE_WATCHDOG.md also owns the operational deadline table and boundary examples.",
      "needs": "Expand the lease and WRITE_SCOPE to the two requested paths, then resume this worker."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The approximately ten-minute objective is not implemented. PLAN/REQUEST/TERM/KILL remain 25/25/16/15 minutes. Two-minute KILL lead alone does not provide two minutes of settling after delayed signalling and supervisor exit.",
      "needs": "Complete the teardown-budget derivation and aligned ladder change after scope expansion."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md",
      "docs/process/MAGISTRATE_WATCHDOG.md"
    ],
    "reason": "The live cooperative-exit instruction and owning deadline documentation must agree with the shortened enforcement chain.",
    "blocked_work": "Shortened resident constants, aligned request payload, final timing regressions, and replacement of remaining 25-minute deadline references.",
    "minimal_change": "Make the relaunch prompt honor the plan-specific exit deadline; update the watchdog deadline table and affected examples alongside the already-authorized code, tests, runbook and handback changes."
  }
}
```

## Change

Hunks implement the independent pad reduction, document history and physical mechanisms, pin the fixed-epoch cutoff, and test ordering plus cadence slack. All 85-minute cutoff references in the two authorized documents now read 27 minutes. No commit was made.

The original chain came from `2b4476cb`: nine minutes for cooperative handback, one minute after TERM, then the historical idle allowance. `391a194b` added the flat installation hour. The new two-minute pad separates installation from REQUEST by twelve nominal resident polls; it is not a settling allowance.

## Verification notes

RED was captured before changing production; both assertions pass within V2. Only the requested modules ran, sequentially and timed. Baseline digest matched. Structural inspection confirmed six authorized changed files, unchanged `night_gate.py`, and an empty gate-threshold diff grep.

The resident’s 10-second cadence fits proposed 120/60-second gaps with 110/50 seconds of nominal slack. Launchd’s 300-second recovery cadence cannot guarantee those phases after supervisor failure.

## Residual risk

The shorter ladder remains unfinished. Expand scope to the two named documents and resume; keeping the nine-minute live instruction while shortening TERM would leave contradictory operational instructions.