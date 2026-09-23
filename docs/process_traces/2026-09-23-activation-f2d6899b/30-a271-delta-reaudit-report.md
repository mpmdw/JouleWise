```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One clock-rollback blocker, one contract-recording defect, and one test gap found in the A271 delta.",
  "workspace": {
    "base_requested": "f81e34ec",
    "base_mode": "exact",
    "head_start": "1b8c64105c8d985b8e06bb68e086bb9e87d113f7",
    "head_end": "1b8c64105c8d985b8e06bb68e086bb9e87d113f7",
    "upstream_end": "1b8c64105c8d985b8e06bb68e086bb9e87d113f7",
    "branch": "feat/2026-09-23-a271-corecaptured"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "path": "joulewise/corecaptured_loop.py",
        "line": 51,
        "summary": "A backward wall-clock step can turn three recent spawns into a measured zero at both arm and t0.",
        "counterexample": "The log has spawns 20, 10, and 1 seconds before the read; the clock after the read is 30 seconds earlier than before it. check() passes with count 0 and no remediation; t0 records measured count 0 and no refusal.",
        "evidence": "V3"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "docs/contracts/evidence_night_entry.md",
        "line": 175,
        "summary": "The claim that every machine move and its exit code appear in check.json is false on command exceptions.",
        "counterexample": "An OFF timeout attempts OFF and ON, then refuses; check.json has wifi_on_exit_code but no OFF outcome field. An ON timeout likewise has no ON outcome field. A failed canonical pull also raises before its observation is returned.",
        "evidence": "V4"
      },
      {
        "id": "F3",
        "severity": "nit",
        "path": "tests/test_night_gate.py",
        "line": 368,
        "summary": "The arm and t0 integration tests do not protect inclusion of spawns logged during the read.",
        "counterexample": "Replacing either call-site upper bound with the pre-read clock leaves its targeted test green; a row at pre-read plus 15 seconds should be included.",
        "evidence": "V5"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_evidence_night.py tests/test_arm_retry.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["246 passed, 290 subtests passed in 306.58s (0:05:06)"]},
      "expected": {"exit_code": 0, "tail_regex": "246 passed, 290 subtests passed"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-a271delta/check_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["item0: count 5, not_licensed, no actuators", "census_exception: count 5, not_licensed, no actuators", "retry_skipped: count 5, not_licensed, no actuators", "fake_rehearsal_failed: count 5, not_licensed, no actuators"]},
      "expected": {"exit_code": 0, "tail_regex": "not_licensed actuators \\[\\]"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-a271delta/backwards_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["backwards_check 0 pass none []", "backwards_t0 {'status': 'measured', 'last_10m_spawns': 0, 'first_spawn': None, 'last_spawn': None} None"]},
      "expected": {"exit_code": 0, "tail_regex": "backwards_t0 .*last_10m_spawns.*0"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-a271delta/exception_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OFF timeout/runtime, 8 s wait timeout/runtime, and ON timeout/runtime: each refused with moves ['off', 'on'], timeouts [30, 30, 30], and no restart", "OFF timeout recorded only wifi_on_exit_code; ON timeout recorded only wifi_off_exit_code"]},
      "expected": {"exit_code": 0, "tail_regex": "on_runtime refused fail \\['off', 'on'\\]"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-a271delta/mutate.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Survived: license_right, anchor_arm_upper, anchor_t0_upper", "Killed: license_left, timeout_off, timeout_on, timeout_restart, threshold, anchor_arm_lower, anchor_t0_lower"]},
      "expected": {"exit_code": 0, "tail_regex": "anchor_t0_upper 0 1 passed"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/f2d6899b-scratch-a271delta/sanity_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["equal 1; dst_offsets 2", "blank_then_malformed corecaptured log has an unparseable line", "Both rendered policy blocks byte-equal render_policy(): True"]},
      "expected": {"exit_code": 0, "tail_regex": "policy_equal docs/phase_2/derivation_night_runbook.md True"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A clean fake_launchctl rehearsal still permits the simulated OFF/ON path; ruling 16 Q3 licenses it when item 0 and all earlier rows pass. No live actuator command was run.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — BLOCKER.** [corecaptured_loop.py](/Users/edr/code/wt-f2d6899b-a271/joulewise/corecaptured_loop.py:51) uses the post-read wall clock as the inclusive upper bound without checking whether that clock moved backward. V3 exercised the resulting false zero through both `check()` and the t0 gate. Refuse or mark the observation unmeasured when the post-read clock precedes the pre-read clock.

- **F2 — SHOULD-FIX.** [evidence_night_entry.md](/Users/edr/code/wt-f2d6899b-a271/docs/contracts/evidence_night_entry.md:175) promises an exit-code record for every move. V4 shows that timed-out or exception-raising commands leave no outcome field for the attempted move. Record the attempted command and its exception when no exit code exists, then state that distinction in the contract.

- **F3 — NIT.** The slow-read tests in [test_night_gate.py](/Users/edr/code/wt-f2d6899b-a271/tests/test_night_gate.py:368) and `test_evidence_night.py` exercise only pre-read timestamps. Both upper-bound call-site mutations survived. Add a spawn stamped during the read to each test.

The licensing probes found no actuator command after item 0 failed, an earlier row raised, or an earlier row was skipped, including the failed fake-launchctl rehearsal. Read-only count five failed with `not_licensed`. Six OFF, wait, and ON exception probes each refused after exactly one ON attempt, with no second OFF or restart. An exact toggle-completion timestamp was excluded; one microsecond later triggered one restart and refusal. Equal timestamps, DST offsets, and malformed nonblank lines behaved as intended. Both policy blocks are byte-identical to `arm_retry.render_policy()`.

## Residual risk

All actuator calls were simulated. A passing fake-launchctl rehearsal does enter the actuation path, which the stated Q3 licensing condition permits.