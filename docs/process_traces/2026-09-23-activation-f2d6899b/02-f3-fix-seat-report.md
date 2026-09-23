```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Fixed early refusal release so the watchdog requires an empty production census before launching.",
  "workspace": {
    "base_requested": "31124f68",
    "base_mode": "exact",
    "head_start": "31124f68950cf0b729ed3a5698c5e5dbeb1206ea",
    "head_end": "31124f68950cf0b729ed3a5698c5e5dbeb1206ea",
    "upstream_end": "af879efb7f52f3abc57d4d2597bd2cda9b1a0198",
    "branch": "feat/2026-09-23-refusal-early-release-f3"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "tests/test_magistrate_watchdog.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
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
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q tests/test_magistrate_watchdog.py -k 'delivered_refusal_live_census_holds_decide or delivered_refusal_empty_census_releases_decide or delivered_refusal_armed_until_empty_census_observed or noneligible_delivered_refusal_preserves_base_disarm'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["4 failed, 101 deselected in 0.42s"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "4 failed, 101 deselected"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q tests/test_magistrate_watchdog.py -k 'delivered_refusal or delivered_zero_capture_refusal or refusal_without_courier or started_chain_refusal or registration_refusal_and_receipt_capture or early_release_reaches'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["11 passed, 96 deselected in 0.16s"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "11 passed, 96 deselected"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q tests/test_magistrate_watchdog.py tests/test_magistrate_watchdog_cli.py tests/test_arm_retry.py tests/test_install_magistrate_watchdog.py tests/test_evidence_night*.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["296 passed, 754 subtests passed in 284.50s (0:04:44)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "296 passed, 754 subtests passed"
      }
    },
    {
      "id": "V4",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Driver coverage by the production census depends on the resolved courier path containing 'claude', as it does in the inspected pilot.",
      "needs": "Magistrate checks the rendered driver argv before acceptance; a future nonmatching path needs a separate driver-exit proof."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live watchdog, launchctl, or hardware run was performed under this seat's fences.",
      "needs": "Magistrate owns live verification and canonical watchdog restart."
    }
  ]
}
```

## Change

**F3 confirmed on `31124f68`.** In that revision, `plan_span_active` returned false at delivery (`scripts/magistrate_watchdog.py:816–817`), while `decide()` called the census only under `if active_plans` (`:1519–1521`). The new production-call-site test returned `LAUNCHING` with a non-empty census; all four requested defect tests failed before the fix.

[The watchdog](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:1500) now checks the production census on every tick for an eligible delivered refusal within its nominal span. A non-empty result keeps `HOLD_CENSUS`; an empty result records release in the watchdog-owned `state.json`, removes the plan from the active and armed filters, and permits `LAUNCHING` when other predicates clear. A later non-empty census restores the hold. `plan_is_armed` stays true until that observed release or nominal completion. The plan-directory caller can read the same state from its sibling magistrate directory. A recorded live magistrate retains adoption during `HOLD_CENSUS`.

The census covers the pilot driver: [its pattern](/Users/edr/code/wt-f2d6899b-f3/joulewise/night_gate.py:162) matches `claude`, and [the installer template](/Users/edr/code/wt-f2d6899b-f3/configs/launchd/com.joulewise.night.plist.template:7) places `--courier-bin` in the driver’s argv. The [pilot census](/Users/edr/night-custody/magistrate/events.jsonl:1055) listed both driver PID 18001 and courier PID 29161 at 09:20:21. [Delivery](/Users/edr/night-archive/qpe01-pilot-n1-20260923-0700-harvest-20260923/night.log:6) followed at 09:20:59; the driver logged activity at [09:22:20](/Users/edr/night-archive/qpe01-pilot-n1-20260923-0700-harvest-20260923/night.log:7). The first empty census was 09:25:22. The inspected production driver therefore needs no separate exit file for this fix.

The seat’s new armed behavior for **non-eligible** delivered refusals was not required by the brief: the base disarmed them on `courier.sent`, while the seat kept them in `armed_plans` through nominal completion, extending the checkout fence and potentially delaying a canonical fast-forward. I restored the base behavior for registration and class refusals; their plan-span hold remains. A refusal after `chain.started` remains armed through nominal completion. The runbook’s eight-minute span start matches `PLAN_LEAD_S = 480` in the code.

Changed files: [watchdog](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:810), [watchdog tests](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:208), [handback](/Users/edr/code/wt-f2d6899b-f3/docs/process/NIGHT_HANDBACK.md:57), and [runbook](/Users/edr/code/wt-f2d6899b-f3/docs/phase_2/derivation_night_runbook.md:1856). The existing shared eligibility predicate in `arm_retry.py` needed no change. The persistent release record and sibling-state read are the implementation additions beyond the suggested shape; no write-scope deviation occurred.

## Verification notes

The five prior seat tests were adjusted explicitly: delivered refusal now asserts a hold before census; delivery-without-courier keeps holding at marker creation; the chain-start test waits for census after its test-only removal of `chain.started`; the registration test expects the base disarmed state and waits for census when changed to an eligible refusal; and the launch-filter test checks standdown and plist fencing before the empty-census decision. The baseline and final command tails are in V1–V3. No whole-suite run was performed.

## Residual risk

The magistrate should double-check the canonical rendered `--courier-bin` path against the census pattern, the resident watchdog’s staleness and restart path, the dead-man boundary, and the sibling-state lookup used by the successor entry check. The live watchdog and custody state were left untouched; changes remain uncommitted in this worktree.