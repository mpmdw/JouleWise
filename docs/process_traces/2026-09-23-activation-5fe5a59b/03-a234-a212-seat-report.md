```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented early watchdog release after a delivered terminal zero-capture machine-state refusal; focused tests pass.",
  "workspace": {
    "base_requested": "af879efb",
    "base_mode": "exact",
    "head_start": "af879efb7f52f3abc57d4d2597bd2cda9b1a0198",
    "head_end": "af879efb7f52f3abc57d4d2597bd2cda9b1a0198",
    "upstream_end": "af879efb7f52f3abc57d4d2597bd2cda9b1a0198",
    "branch": "feat/2026-09-23-refusal-early-release"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "joulewise/arm_retry.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_arm_retry.py",
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
      "cmd": "python3 -B -m unittest tests.test_magistrate_watchdog.FenceTests.test_delivered_zero_capture_refusal_releases_both_holds_early tests.test_magistrate_watchdog.FenceTests.test_refusal_without_courier_holds_until_delivery tests.test_magistrate_watchdog.FenceTests.test_started_chain_refusal_keeps_full_span tests.test_magistrate_watchdog.FenceTests.test_registration_refusal_and_receipt_capture_keep_hold tests.test_magistrate_watchdog.FenceTests.test_early_release_reaches_standdown_and_launch_filter",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 5 tests in 0.012s", "FAILED (failures=5)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=5\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_magistrate_watchdog.FenceTests.test_delivered_zero_capture_refusal_releases_both_holds_early tests.test_magistrate_watchdog.FenceTests.test_refusal_without_courier_holds_until_delivery tests.test_magistrate_watchdog.FenceTests.test_started_chain_refusal_keeps_full_span tests.test_magistrate_watchdog.FenceTests.test_registration_refusal_and_receipt_capture_keep_hold tests.test_magistrate_watchdog.FenceTests.test_early_release_reaches_standdown_and_launch_filter",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 5 tests in 0.012s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 5 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_arm_retry tests.test_install_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 149 tests in 18.483s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 149 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 0.457s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 31 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -B -m pytest tests/test_magistrate_watchdog.py tests/test_magistrate_watchdog_cli.py tests/test_arm_retry.py tests/test_install_magistrate_watchdog.py",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": ["/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest"]
      },
      "expected": {"exit_code": 0, "tail_regex": "passed"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -B -m pytest -q -x tests -k 'watchdog or retry or night'",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": ["/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest"]
      },
      "expected": {"exit_code": 0, "tail_regex": "passed"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": ["Interrupted during tests/test_arm_readiness_evidence_t0.py; no final test count."]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "pytest is absent, so neither requested CI-equivalent command collected tests or produced counts.",
      "needs": "Magistrate reruns both exact pytest commands in an environment with pytest."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide unittest discovery run was interrupted during an unrelated slow readiness fixture; focused modules and docs freshness passed.",
      "needs": "Magistrate completes the repository-wide gate."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "courier.sent proves delivery but may precede courier and driver process exit.",
      "needs": "Magistrate checks live-process behavior before accepting the early arm release."
    }
  ]
}
```

## Change

At `af879efb`, A212(b) was already implemented by `zero_capture_successor_allowed` and `successor_arm_allowed` ([arm_retry.py](/Users/edr/code/wt-5fe5a59b-a234/joulewise/arm_retry.py:246)); its spacing, fresh-plan, notice, cutoff, and NO tests already existed ([test_arm_retry.py](/Users/edr/code/wt-5fe5a59b-a234/tests/test_arm_retry.py:453)). D-182 already recorded the ruling ([decision_log.md](/Users/edr/code/wt-5fe5a59b-a234/docs/decision_log.md:11958)). A212(a), the watchdog part of A212(c), and A234 remained: the original `plan_span_active` held through nominal completion despite a delivered refusal.

The watchdog now releases `plan_span_active` and `plan_is_armed` only when `result.json` and `receipt.json` agree on an eligible terminal refusal, `courier.sent` exists, and no chain start or receipt capture claim exists ([magistrate_watchdog.py](/Users/edr/code/wt-5fe5a59b-a234/scripts/magistrate_watchdog.py:785)). Its eligibility and result/receipt checks share one predicate with the successor route ([arm_retry.py](/Users/edr/code/wt-5fe5a59b-a234/joulewise/arm_retry.py:202)). Registration and class refusals, and refusals after a chain start, retain the full span. No t0 gate changed. The handbook and runbook explain the recovery cost and successor; the runbook’s adjacent stale 25-minute plan lead was corrected to eight minutes.

The duplicate A212 and A234 queue rows differ only in status: the instructed rows say `READY [AGENT]`; later copies say `READY`. Their description and acceptance cells match. No queue or other fenced file was edited.

**Proposed decision-log addendum text for the magistrate’s cold gate:**

> ### Addendum (2026-09-23) — A212/A234 implementation
>
> Ed’s 2026-09-16 00:35 PDT ruling, relayed verbatim by session b0ae8462 and recorded in the A212 lane registration, was: “unless there's a scientific reason that's an unsound decision absolutely reduce the hours to 20 min”.
>
> D-182 already licenses one new-plan successor after a terminal zero-capture machine-state refusal and completed courier delivery. A212/A234 installs the watchdog half: after the driver’s terminal result and receipt agree, `courier.sent` exists, and no chain start or capture claim exists, the watchdog ends the refused plan’s census hold before nominal completion. A refusal file alone grants no release. Registration and class refusals and every refusal after a chain start retain the full span. The successor still requires a new plan and notice, at least 60 seconds after terminal write, installation before its own cutoff, every observed NO honored, and all checks at its own t0. The current next-start planner’s 40-minute lead means the 20-minute recovery target is not a promise of a new measurement within 20 minutes.

## Verification notes

All five defect-shaped watchdog tests failed before the production edit and pass afterward, including the standdown, installed-plan, and launch decision call sites. The final focused run passed **149 tests**; docs freshness passed **31**. The two requested pytest commands produced **no test counts** because `pytest` is unavailable. The broader unittest run was interrupted before a result.

## Residual risk

The magistrate should verify the resident watchdog’s state freshness after early release, the unchanged dead-man bound when delivery is absent, and whether a courier or driver still alive after `courier.sent` can overlap a new arm. The driver may finish logs and durable recording after delivery; the successor’s cleanup, arm checks, and t0 gate remain the safeguards.