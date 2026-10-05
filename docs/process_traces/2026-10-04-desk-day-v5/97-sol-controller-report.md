```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented G2-b pre-slot attachment and bundle battery pairs; all 101 controller and 136 battery tests pass.",
  "workspace": {
    "base_requested": "b2ff2f36",
    "base_mode": "exact",
    "head_start": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
    "head_end": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
    "upstream_end": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
    "branch": "feat/2026-10-05-controller-g2b-attach-battery"
  },
  "pathspec": [
    "joulewise/controller.py",
    "tests/fixtures/controller_g2b/README.md",
    "tests/fixtures/controller_g2b/block3-pre/events.jsonl.gz",
    "tests/fixtures/controller_g2b/block3-pre/instrument_evidence.json.gz",
    "tests/fixtures/controller_g2b/block3-pre/manifest.json.gz",
    "tests/fixtures/controller_g2b/block3-pre/power_trace.csv.gz",
    "tests/fixtures/controller_g2b/block3-pre/provenance.json",
    "tests/fixtures/controller_g2b/block3-pre/raw/battery_float.post.ioreg.gz",
    "tests/fixtures/controller_g2b/block3-pre/raw/battery_float.pre.ioreg.gz",
    "tests/fixtures/controller_g2b/block3-pre/raw/powermetrics.plist.gz",
    "tests/test_battery_float_consumers.py",
    "tests/test_battery_float_sweep.py",
    "tests/test_controller_battery_float.py",
    "tests/test_controller_g2b_attachment.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 -m unittest discover -s tests -p 'test_controller*.py' > /tmp/dd5-ctl/controller-approved.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: .*)?$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 -m unittest discover -s tests -p 'test_battery_float*.py' > /tmp/dd5-ctl/battery-approved.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: .*)?$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 -m unittest tests.test_battery_float_sweep tests.test_battery_float_consumers > /tmp/dd5-ctl/guards-approved.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: .*)?$"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "cd /tmp/dd5-ctl/origin-main && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 -m unittest discover -s tests -p 'test_battery_float*.py' > /tmp/dd5-ctl/battery-origin-main.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: .*)?$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "cd /tmp/dd5-ctl/origin-main && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 -m unittest tests.test_battery_float_consumers.ConsumerGuardTests.test_the_guard_reports_every_primitive_call_of_the_pre_seam_tree > /tmp/dd5-ctl/origin-history-guard.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: .*)?$"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 -m unittest tests.test_revision_five_b_readers tests.test_g2a_calibration_attachment > /tmp/dd5-ctl/compatibility-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: .*)?$"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 /tmp/dd5-ctl/verify_scope.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SCOPE_OK",
          "PINNED_ESTIMATORS_UNCHANGED",
          "PYTHON_SYNTAX_OK",
          "REAL_CAPTURE_SHA256_OK (7 files)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)SCOPE_OK.*PINNED_ESTIMATORS_UNCHANGED.*REAL_CAPTURE_SHA256_OK"
      }
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctl python3 -m unittest discover -s tests > /tmp/dd5-ctl/canonical.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: .*)?$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Earlier canonical discovery was interrupted (exit 130); no complete canonical result. Requested controller and battery suites and compatibility checks pass. Executing review and cold Fable final pass remain lead-owned.",
      "needs": "Complete canonical discovery and the planned review gates."
    }
  ]
}
```

## Change

G2-b attachments now authenticate launch lineage and the session’s finalized pre slot. Controller battery pairs use the shared reader outside sampling and clock anchors; observation failures are recorded without aborting the member. Approved guard inventories were updated without loosening checks.

Changes remain uncommitted. No out-of-scope writes; pinned estimator files are unchanged.

## Verification notes

Canonical discovery was interrupted. The origin/main history-test skip passed separately after restoring read-only history access in scratch.

## Residual risk

Verification uses real archived capture bytes with synthetic launch context and a labelled ioreg stub. Executing review and the cold Fable final pass remain pending.