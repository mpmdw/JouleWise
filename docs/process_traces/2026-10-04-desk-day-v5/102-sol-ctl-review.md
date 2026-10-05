```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVIEW: FAIL — the G2-b exception also admits unregistered plain runs.",
  "workspace": {
    "base_requested": "b2ff2f36",
    "base_mode": "exact",
    "head_start": "9b08ecf62357cf4e0ea245ef601d5fef8377cb7e",
    "head_end": "9b08ecf62357cf4e0ea245ef601d5fef8377cb7e",
    "upstream_end": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "REVIEW: FAIL",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "joulewise/controller.py",
        "line": 452,
        "title": "Plain, unregistered runs can enter the G2-b attachment exception",
        "evidence": "With a valid root-local locator, an untagged config absent from the authenticated pack inventory succeeded with g2b_pre_slot metadata and no full launch_lineage. The same attachment was refused by b2ff2f36. The helper authenticates the root without config_paths, and the untagged writer skips member authentication.",
        "recommendation": "Require the existing launch-lineage marker and authenticate the running config as a pack member before granting this exception."
      }
    ],
    "attachment_checks": "Foreign sessions, unfinalized PRE, POST, copied custody, missing consumption, stale boot, completed launch and absent lineage were refused. Symlink aliases to the genuine PRE were accepted; replacing the reserved PRE directory itself with a symlink was refused. G2-a compatibility passed.",
    "battery_checks": "Both probes were outside sampler lifetimes. Injected 120-second delays shifted following stages but preserved measured duration; the post probe did not delay the measured-stop stamp. Probe, timeout and raw-write failures were recorded without crashing members.",
    "reader_checks": "Candidate authenticators and the archived harvest battery_attempts function accepted emitted pairs, real calibration attachments and a full archived bundle shape with explicitly synthetic battery additions."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 -m unittest discover -s tests -p 'test_controller*.py' > /tmp/dd5-ctrev/controller.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 101 tests in 323.397s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 -m unittest discover -s tests -p 'test_battery_float*.py' > /tmp/dd5-ctrev/battery.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 136 tests in 386.964s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 -m unittest discover -s tests -p 'test_revision_five*.py' > /tmp/dd5-ctrev/revision.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.015s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 /tmp/dd5-ctrev/compat.py > /tmp/dd5-ctrev/compat.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 61.554s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 /tmp/dd5-ctrev/adversarial.py > /tmp/dd5-ctrev/adversarial.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["plain_unregistered_config_in_authenticated_root ACCEPTED", "plain_member_status succeeded"]},
      "expected": {"exit_code": 0, "tail_regex": "plain_member_status succeeded"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 /tmp/dd5-ctrev/mutations.py > /tmp/dd5-ctrev/mutations.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ATTACHMENT_GUARDS_KILLED=26/26", "ALL_MUTATION_CHECKS_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)ATTACHMENT_GUARDS_KILLED=26/26.*ALL_MUTATION_CHECKS_COMPLETE"}
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 /tmp/dd5-ctrev/reader_trace.py > /tmp/dd5-ctrev/reader_trace.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["REAL_TIMEOUT: timed_out=True probe_error=True passed=False elapsed_under_1s=True", "READER_TRACE_COMPLETE"]},
      "expected": {"exit_code": 0, "tail_regex": "READER_TRACE_COMPLETE"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctrev python3 /tmp/dd5-ctrev/regressions.py > /tmp/dd5-ctrev/regressions.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: ValueError not raised : plain unregistered member must retain Revision-5 refusal", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    }
  ],
  "flags": [
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Launch fixtures stub ARM/T-0 issuance and boot boundaries. Battery timing uses labelled adapters; harvest coverage executes the archived battery_attempts function rather than a complete s1 harvest. No live hardware measurements were performed.",
      "needs": "Lead-owned cold final pass and live qualification."
    }
  ]
}
```

## Findings

REVIEW: FAIL

**F1 — should_fix:** The exception at [controller.py:452](/Users/edr/code/JouleWise-wt-dd5-ctrev/joulewise/controller.py:452) authenticates the runs root without binding the running config to its pack. An untagged, unregistered member therefore accepts Revision-5 calibration and succeeds without full launch-lineage metadata; the parent refuses it. Require member authentication before granting the exception. [Reproduction](/tmp/dd5-ctrev/regressions.py), [evidence](/tmp/dd5-ctrev/regressions.log).

All 249 existing focused and compatibility tests passed. All 35 mutation checks triggered failures. Repository unchanged.

## Residual risk

Timing evidence uses labelled adapters. Reader checks include archived capture bytes and a real bundle shape, but do not establish live hardware qualification or complete harvest success.