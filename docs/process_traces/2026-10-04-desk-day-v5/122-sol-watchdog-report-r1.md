```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Active-span ticks now skip network probes and maintenance; post-span probing remains intact.",
  "workspace": {
    "base_requested": "e7d13a17",
    "base_mode": "exact",
    "head_start": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "head_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": "fix/2026-10-05-watchdog-no-network-in-span"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_magistrate_watchdog_cli.py",
    "tests/test_magistrate_watchdog_span.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wd python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_magistrate_watchdog_span tests.test_install_magistrate_watchdog > /tmp/dd5-wd/watchdog-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 158 tests in 30.414s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 158 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wd PYTHONPATH=/Users/edr/code/JouleWise-wt-dd5-wd/scripts python3 /tmp/dd5-wd/quick_suite.py --tier touched --since e7d13a1706d6352e0b3d9624dcf4c897671393da --workers 2 > /tmp/dd5-wd/touched.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["QUICK SUMMARY tier=touched modules=185 excluded=101 failures=2 seconds=1502.602 result=FAIL"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "QUICK SUMMARY tier=touched modules=185 excluded=101 failures=0 seconds=[0-9.]+ result=PASS"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wd PYTHONPATH=/Users/edr/code/JouleWise-wt-dd5-wd/scripts python3 /tmp/dd5-wd/quick_suite.py --module tests.test_axi_mock_spec > /tmp/dd5-wd/axi-mock-replay.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["SHARD SUMMARY index=1/1 modules=1 tests=11 failures=2 errors=0 skipped=0 result=FAIL", "RERUN /opt/homebrew/opt/python@3.14/bin/python3.14 /private/tmp/dd5-wd/quick_suite.py --module tests.test_axi_mock_spec"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SHARD SUMMARY .* failures=0 errors=0 .* result=PASS"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-wd PYTHONPATH=/Users/edr/code/JouleWise-wt-dd5-wd/scripts python3 /tmp/dd5-wd/quick_suite.py --module tests.test_axi_controller_events > /tmp/dd5-wd/axi-events-replay.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["SHARD SUMMARY index=1/1 modules=1 tests=7 failures=2 errors=0 skipped=0 result=FAIL", "RERUN /opt/homebrew/opt/python@3.14/bin/python3.14 /private/tmp/dd5-wd/quick_suite.py --module tests.test_axi_controller_events"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SHARD SUMMARY .* failures=0 errors=0 .* result=PASS"
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
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c 'import subprocess; allowed={\"scripts/magistrate_watchdog.py\", \"tests/test_magistrate_watchdog.py\", \"tests/test_magistrate_watchdog_cli.py\", \"tests/test_magistrate_watchdog_span.py\"}; paths={row[3:] for row in subprocess.check_output([\"git\", \"status\", \"--porcelain=v1\"], text=True).splitlines()}; assert paths <= allowed, paths - allowed; print(\"WRITE_SCOPE_OK\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["WRITE_SCOPE_OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^WRITE_SCOPE_OK$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "For installed-only spans, baseline STOP/NETWORK_UNCERTAIN handling preceded the installed fence and could adopt/drain the magistrate or enqueue a notice. Those actions, including local STOP handling in that path, now defer until the span ends.",
      "needs": "Rule on this behavior change and its delayed stop/notice consequence."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The strict no-work guard also defers tick-driven supervisor recovery, unsafe-session drain, census/clock diagnostics, and pending zero-capture-refusal release. A failed supervisor can leave its magistrate alive until admission refuses the night; an unreleased refusal can remain fenced until the original span bound. Resident stand-down enforcement is unchanged.",
      "needs": "Approve these deferrals or authorize exceptions for recovery and refusal-release checks."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "blocking",
      "text": "The touched run failed in two AXI modules, two tests each, with campaign start identity unavailable. Direct execution confirmed that this sandbox rejects /bin/ps with PermissionError. Both isolated module replays reproduced the failures.",
      "needs": "Rerun the two AXI modules in a lead environment where process identity inspection is permitted."
    }
  ]
}
```

## Change

At baseline `e7d13a17`, discovered active spans ignored remote STOP (`scripts/magistrate_watchdog.py:1604–1621`); resident plan enforcement also preceded remote handling (`:2129–2141`). Installed-only spans handled STOP/network uncertainty before fencing (`:1622–1627`), creating F1.

Confirmed active-span ticks now return before probing, census, recovery, fork, or custody writes. Inclusive endpoints remain quiet; the first post-span tick probes. Changes are uncommitted.

## Verification notes

The touched runner used a scratch copy with only its temporary-directory setting changed to `/tmp/dd5-wd/`. It emitted 88 stale-weight warnings. Its two failed modules reproduced the sandbox identity-probe failure.

## Residual risk

Lead rulings F1/F2 and the permitted-environment AXI replays remain open. Full-suite and live verification remain lead-owned.