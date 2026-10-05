```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented read-only G10 preflight and repaired X4 placement custody; final focused regressions pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "d77681e39ea538dc3ebfd54b91dc7aa0b60bae6a",
    "head_end": "02582c6a9510dc3ec25f921f1fec91c6f2b69c84",
    "upstream_end": null,
    "branch": "lane/2026-10-05-b4-x9"
  },
  "pathspec": [
    "scripts/ed_session/capture_t0_anchor_positive_control.py",
    "tests/test_capture_t0_anchor_positive_control.py",
    "tests/test_v5_block4_x4.py",
    "tests/test_v5_block4_x9.py"
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
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_capture_t0_anchor_positive_control.PreflightSubcommandTests tests.test_v5_block4_x4.G10CustodyTests tests.test_v5_block4_x9.PreparationIsolationTests.test_run_rechecks_offset_after_standalone_preflight_passes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_block4_x9 tests.test_v5_block4_x4 tests.test_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control_g10 tests.test_v5_block4_x1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-x9/round3_quick.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^QUICK SUMMARY .*result=PASS$"
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
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The requested suite ran 73 tests with one pre-existing X4 battery assembler error: battery_boundary_lifecycle_missing. The baseline had this error plus the now-fixed G10 placement failure. The final eight-test focused run passed.",
      "needs": "Lead: repair the separate battery lifecycle fixture and rerun the requested suite."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The supplementary touched runner was wrapped to keep temporary files under /tmp/dd5-x9 and interrupted after about 17 minutes. It reported 196 of 197 selected modules; controller_g2b_attachment remained unfinished. Eight modules failed: launch_window_realization_recheck, revision6_seal, v5_block4_x4, v5_block4_replay, axi_mock_spec, paper_rendering, axi_controller_events, authentication_io. Log: /tmp/dd5-x9/round3-quick.log.",
      "needs": "Lead: triage these failures and complete the touched-suite gate."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied ps, so the fixture-orphan census could not establish a clean result.",
      "needs": "Lead: run the fixture-orphan census where process inspection is available."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD advanced concurrently through a recipe-only commit. This session made no commits or pushes; all four authorized changes remain uncommitted.",
      "needs": ""
    }
  ]
}
```

## Change

Added canonical preflight JSON, required exit codes, and optional create-once raw output using the shared collector and agreement calculation. Tests prove no ON/OFF, no OUTSIDE prompt, and authoritative rechecking by `run`.

Updated X4 to `a2` → G10 → `s1`, preserving the support-mutation negative.

## Verification notes

Acceptance remains pending because of the pre-existing battery lifecycle error, supplementary suite failures and interruption, and unavailable orphan census. The final exception-handling adjustment was verified by the eight-test focused run.