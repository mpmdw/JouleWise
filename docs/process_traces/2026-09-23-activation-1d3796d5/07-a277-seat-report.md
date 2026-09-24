```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented disk-backed zero-capture successor admission and a create-once claim; 306 named acceptance tests pass.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "exact",
    "head_start": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "head_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "upstream_end": null,
    "branch": "feat/2026-09-23-a277-successor-facts"
  },
  "pathspec": [
    "joulewise/zero_capture_facts.py",
    "joulewise/arm_retry.py",
    "scripts/magistrate_watchdog.py",
    "joulewise/evidence_night.py",
    "tests/test_zero_capture_facts.py",
    "tests/test_arm_retry.py",
    "tests/test_evidence_night.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/contracts/night_quiet_admission.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_zero_capture_facts tests.test_arm_retry tests.test_magistrate_watchdog tests.test_evidence_night > /private/tmp/a277-acceptance-latest.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 306 tests in 422.297s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 306 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -c 'import sys, unittest; from tests.test_evidence_night import LifecycleTests; names = sorted(n for n in dir(LifecycleTests) if n.startswith(\"test_a277_\")); suite = unittest.defaultTestLoader.loadTestsFromNames([\"tests.test_evidence_night.LifecycleTests.\" + n for n in names]); result = unittest.TextTestRunner().run(suite); sys.exit(not result.wasSuccessful())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 17 tests in 15.243s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 17 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_fixture_orphan_census tests.test_install_night_agent tests.test_magistrate_watchdog_cli > /private/tmp/a277-importers-clean.txt 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 83 tests in 206.979s", "", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 83 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_plan_writer tests.test_run_night.NightDriverTests.test_install_close_precedes_the_plan_span_by_the_margin",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 11 tests in 0.052s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V5",
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
      "kind": "environment",
      "level": "nonblocking",
      "text": "One night_agent_install importer test fails identically on the base revision: sandbox pgrep cannot obtain the sysmond process list.",
      "needs": "Magistrate full-suite replay in its normal verification environment."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The broad night_agent_install importer run was not completed after its baseline failure; its long timing test was interrupted. The named acceptance and other importer checks completed.",
      "needs": "Magistrate full-suite replay."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Direct install_night_agent.sh installation does not execute evidence_night.check, as the A277 design decision records.",
      "needs": "Track the decided direct-installer follow-up lane."
    }
  ]
}
```

## Change

Changed files: `joulewise/zero_capture_facts.py`, `joulewise/arm_retry.py`, `scripts/magistrate_watchdog.py`, `joulewise/evidence_night.py`, `tests/test_zero_capture_facts.py`, `tests/test_arm_retry.py`, `tests/test_evidence_night.py`, `docs/process/NIGHT_HANDBACK.md`, `docs/phase_2/derivation_night_runbook.md`, and `docs/contracts/night_quiet_admission.md`. No commit was made.

| Clause | Implementation |
|---|---|
| C1 | [zero_capture_facts.py](/Users/edr/code/wt-1d3796d5-a277/joulewise/zero_capture_facts.py:17) returns a frozen record with the requested counts and index state. Its composed entry point checks a real custody directory, courier marker, and readable result and receipt before absence can license anything ([line 99](/Users/edr/code/wt-1d3796d5-a277/joulewise/zero_capture_facts.py:99)). Scan-root and descendant symlinks count as present. |
| C2 | The watchdog imports that entry point and uses its `clean` decision for early release ([magistrate_watchdog.py](/Users/edr/code/wt-1d3796d5-a277/scripts/magistrate_watchdog.py:48), [line 817](/Users/edr/code/wt-1d3796d5-a277/scripts/magistrate_watchdog.py:817)). Its existing tests were left unchanged. |
| C3 | [arm_retry.py](/Users/edr/code/wt-1d3796d5-a277/joulewise/arm_retry.py:247) has the pure zero-capture door and shared delivery, claim, identity, and 60-second tail. It no longer requires a C5 evidence block. Door 2 remains for A270. The old desk entry points remain as thin adapters that cannot license without facts ([line 292](/Users/edr/code/wt-1d3796d5-a277/joulewise/arm_retry.py:292)). |
| C4 | [evidence_night.py](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:810) finds released predecessors still within their normal completion span and rereads their facts. `check` records `successor` immediately after `retained_roots` ([line 1227](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:1227)). |
| C5 | Claim reading and validation are at [line 765](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:765); exclusive claim creation is at [line 879](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:879). `publish_install` rereads eligibility and creates the claim just before plan publication ([line 1637](/Users/edr/code/wt-1d3796d5-a277/joulewise/evidence_night.py:1637)). |
| C6 | The calibration finding and added ledger fact are below; the plan-bound ledger scan is at [zero_capture_facts.py:80](/Users/edr/code/wt-1d3796d5-a277/joulewise/zero_capture_facts.py:80). |
| C7 | The policy blocks in [NIGHT_HANDBACK.md](/Users/edr/code/wt-1d3796d5-a277/docs/process/NIGHT_HANDBACK.md:141) and [derivation_night_runbook.md](/Users/edr/code/wt-1d3796d5-a277/docs/phase_2/derivation_night_runbook.md:1939) remain byte-identical. [night_quiet_admission.md](/Users/edr/code/wt-1d3796d5-a277/docs/contracts/night_quiet_admission.md:305) defines the disk-fact route, check row, claim, and direct-installer limitation. |

**C6 finding.** The driver exclusively creates `chain.started` before calling the chain ([run_night.py:536](/Users/edr/code/wt-1d3796d5-a277/scripts/run_night.py:536), [line 3170](/Users/edr/code/wt-1d3796d5-a277/scripts/run_night.py:3170)); the chain process starts at [line 849](/Users/edr/code/wt-1d3796d5-a277/scripts/run_night.py:849). Inside that process, the calibration chain invokes reservation ([calibration_derivation_only.zsh:187](/Users/edr/code/wt-1d3796d5-a277/scripts/night_chains/calibration_derivation_only.zsh:187)), which appends the ledger session ([reserve_calibration_window_bracket.py:362](/Users/edr/code/wt-1d3796d5-a277/scripts/reserve_calibration_window_bracket.py:362)). The verify-only path returns before that append ([line 359](/Users/edr/code/wt-1d3796d5-a277/scripts/reserve_calibration_window_bracket.py:359)). **Inference from this ordering:** `chain.started` precedes a production ledger session; a `*.consumed.json` marker is not guaranteed to precede the ledger append. The scanner therefore also checks ledger rows for the predecessor plan id.

## Verification notes

The exact A277 replay command in V2 was run against a `git archive` of `313efcca` at `/private/tmp/a277-base.Z14PJ3`, with the current test file copied into that temporary tree. The command was identical to V2 except for `cwd` and output redirection to `/private/tmp/a277-base-results-final.txt`. Its tail was `Ran 17 tests in 13.545s` and `FAILED (failures=12, errors=5)`. The same 17 tests passed here. Each row below is one base-failing, changed-tree-passing regression:

| Regression | Counterfactual input | Base → changed |
|---|---|---|
| Delivered successor | Latched, delivered refusal; bare C5; publish attempt | FAIL: no row or claim → PASS: row and one claim |
| Delivery and latch | Remove `courier.sent`, then remove latch | FAIL: no successor decision → PASS: refusal |
| Chain start | Add `chain.started` after latch | FAIL: no successor row → PASS: refusal |
| Reservation | Add nested `*.consumed.json` | FAIL: no successor row → PASS: refusal |
| Evidence link | Symlink `night/evidence` | FAIL: no successor row → PASS: refusal |
| Envelope index | Write a nonempty index | FAIL: no successor row → PASS: refusal |
| Index link | Symlink the index | FAIL: no successor row → PASS: refusal |
| Spacing and door | Check at 59.99 seconds; use `non_observer_process_busy` | FAIL: no spacing row → PASS: both refused |
| Claim and removal | Claim another candidate, then remove predecessor custody | FAIL: no durable count → PASS: refusal |
| Third plan | Release the successor’s own refusal, then present a distinct third id | FAIL: no lineage check → PASS: refusal |
| Multiple predecessors | Two released predecessors remain in span | FAIL: no count check → PASS: refusal |
| Calibration capture | Add an `instrument_validation` entry | FAIL: no successor row → PASS: refusal |
| Ledger session | Add a plan-bound ledger-open row | FAIL: no successor row → PASS: refusal |
| Missing custody | Remove released predecessor custody | FAIL: candidate can appear ordinary → PASS: refusal |
| Symlinked custody | Replace released custody with a symlink | FAIL: no composed root check → PASS: refusal |
| Parity | Compare watchdog and check before and after a late marker | FAIL: no shared check row → PASS: matching facts |
| Publication reread | Add a marker after passing `check`, before `publish_install` | FAIL: no publication reread → PASS: refusal before claim |

The initial scanner counted a macOS `/var` ancestor symlink outside the scanned tree and broke watchdog fixtures. That was narrowed to the scan root and descendants; the final named run passed. The only design extension was the C6 ledger fact. `successor_arm_allowed` remains a compatibility adapter because it has no production caller.

The broader importer fail-fast command was `python3 -B -m unittest -f tests.test_fixture_orphan_census tests.test_install_night_agent tests.test_magistrate_watchdog_cli tests.test_night_agent_install tests.test_night_plan_writer tests.test_run_night`. It stopped at `test_cleanup_refusal_reports_the_failure_it_interrupted` after 122 tests: `pgrep: Cannot get process list`. Running that exact test on the base archive produced the same failure.

## Residual risk

The magistrate should double-check the claim’s behavior around a failed publication and same-id, same-digest retry; replay the full suite in its normal environment; and register the decided direct-installer follow-up.