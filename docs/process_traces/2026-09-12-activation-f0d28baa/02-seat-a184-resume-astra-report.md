```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Corrected the inherited assertion; killed cut and all 48 unittest tests passed. Requested pytest run remains unavailable.",
  "workspace": {
    "base_requested": "ace4cc3c",
    "base_mode": "exact",
    "head_start": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "head_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "fix/2026-09-12-recover-window-exhausted"
  },
  "pathspec": ["tests/test_calibration_exits.py"],
  "unowned_dirty": [
    "docs/contracts/calibration_ledger_append.md",
    "docs/phase_2/derivation_night_runbook.md",
    "joulewise/calibration_exits.py",
    "scripts/recover_calibration_ledger.py",
    "tests/test_calibration_exits.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_session_refusal_reports_window_exhausted_derivation_abort",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1 test in 0.590s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_session_refusal_reports_window_exhausted_derivation_abort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.550s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_calibration_exits.py -q -p no:cacheprovider",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["/opt/homebrew/opt/python@3.14/bin/python3.14: No module named pytest"]
      },
      "expected": {"exit_code": 0, "tail_regex": "passed"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 48 tests in 499.478s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_generated_contract_projection_and_runbook_anchors_are_fresh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.001s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/contracts/calibration_ledger_append.md",
          " M docs/phase_2/derivation_night_runbook.md",
          " M joulewise/calibration_exits.py",
          " M scripts/recover_calibration_ledger.py",
          " M tests/test_calibration_exits.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": " M tests/test_calibration_exits.py"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " docs/contracts/calibration_ledger_append.md |  1 +",
          " docs/phase_2/derivation_night_runbook.md    |  1 +",
          " joulewise/calibration_exits.py              |  4 +++",
          " scripts/recover_calibration_ledger.py       |  1 +",
          " tests/test_calibration_exits.py             | 47 ++++++++++++++++++++++++++++-",
          " 5 files changed, 53 insertions(+), 1 deletion(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "5 files changed, 53 insertions\\(\\+\\), 1 deletion\\(-\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "No python command is installed; available python3 interpreters lack pytest. The complete unittest module passed, but the explicitly requested pytest invocation remains unverified.",
      "needs": "Lead: run python -m pytest tests/test_calibration_exits.py -q in a pytest-equipped environment."
    }
  ]
}
```

## Change

The only lasting change relative to the inherited draft is **1a**: the regression now checks `REFUSAL_BY_CODE[RefusalCode.WINDOW_EXHAUSTED].process_exit`, matching the generic witness convention and making the expectation self-describing. See [assertion, line 5994](/Users/edr/code/JouleWise-wt-a184/tests/test_calibration_exits.py:5994).

**1b:** All generic witness tests passed under unittest, including exact-set coverage, registry projection, public explanations, process exits, durable abort reasons, and terminal results. The new record mirrors all routing fields of the three existing automatic-abort records; its description and witness ID were also checked explicitly. Registry entries are at [lines 106, 268, 290 and 373](/Users/edr/code/JouleWise-wt-a184/joulewise/calibration_exits.py:106). The [terminal-result branch at line 5462](/Users/edr/code/JouleWise-wt-a184/tests/test_calibration_exits.py:5462) affects only the new observer: none of the 71 pre-existing cases uses `session-refusal`. Their assertions remain unchanged. The corpus emitted `CASE PASS calibration_window_exhausted`.

**1c:** Repository search found no standalone registry generator. The projection is constructed and compared exactly in [the freshness test, line 1501](/Users/edr/code/JouleWise-wt-a184/tests/test_calibration_exits.py:1501); that check passed. The inherited [row at line 345](/Users/edr/code/JouleWise-wt-a184/docs/contracts/calibration_ledger_append.md:345) required no changes. Inventory count is dynamically derived—75 records—with no separate digest/count artifact found. No generator wrote anything. `gen_state.py` governs separate state-kernel regions; its read-only check also passed.

**1d:** Left [powermetrics prose, line 460](/Users/edr/code/JouleWise-wt-a184/docs/contracts/powermetrics_fiducial.md:460) unchanged: it describes the rollover gate specifically, not the automatic-abort set. The inherited single [runbook sentence, line 1665](/Users/edr/code/JouleWise-wt-a184/docs/phase_2/derivation_night_runbook.md:1665) satisfies the harvest guidance.

## Verification notes

V1 ran with only the `window_exhausted` map entry removed and failed with:

`AssertionError: 'calibration_session_not_open' != 'calibration_window_exhausted'`

The script was restored in `finally` before V2. Before/after SHA-256 values were identical:

`223a17c5d4f95246852b65ffe99539237c2058c95d830bd1232e5fa3f256583f`

The pytest dependency gap is the sole outstanding verification item. No NEEDS_SCOPE or NEEDS_RULING. No commits or HEAD movement; the inherited five-file dirty tree remains for lead review.