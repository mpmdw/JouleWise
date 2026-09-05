```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: R1 fixture modernization passes its claimed modules but breaks the importing launch-window module by composing four backup commands where doctrine requires exactly two.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "e14b64f0009e198718479a3176038a11cce62240",
    "head_end": "e14b64f0009e198718479a3176038a11cce62240",
    "upstream_end": "04cd6e52e9d6ed2da369398bb448c5454f1917b3",
    "branch": "feat/2026-09-04-fan-FIXTURE-MODERNIZATION-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/FIXTURE-MODERNIZATION-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "location": "tests/test_arm_readiness_dry_run.py:70",
        "text": "install_passing_freeze appends its verdict/backup stages to every pre-existing stage graph. make_t0_fixture therefore returns a graph with two backup commands; tests.test_launch_window later composes that graph with make_author_fixture's independently complete two-backup graph. The production DOCTRINE_PIN derivation counts four backups, requires exactly two, and the importing test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change errors before minting. The helper must remain composable/idempotent, or the dependent composition must be repaired and covered.",
        "counterfactual": "At the merge base, the exact launch test passes (1 test, 153.648s). At HEAD it errors; direct fixture inspection reports t0_backup_commands=2, author_backup_commands=2, composed_backup_commands=4."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_dry_run 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 116.121s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_integration 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 146.458s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_lifecycle 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 66 tests in 208.979s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 66 tests in .*s\\n\\nOK \\(skipped=1\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 66 tests in 581.725s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 66 tests in .*s\\n\\nOK \\(skipped=1\\)"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_s0_blocked_enumeration 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 1.468s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*s\\n\\nOK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 47 tests in 5.198s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 47 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_author 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 24 tests in 169.307s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 24 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_capture_t0_step 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 37.801s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 31 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_launch_window 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 25 tests in 10.794s", "FAILED (errors=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 25 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_analysis_admission 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 8 tests in 11.349s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 8 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V12",
      "kind": "test",
      "cmd": "tmp_root=$(mktemp -d /private/tmp/jw-fixture-base.XXXXXX); git archive b0ed6991c11f3a515ad293760c6dfc031adda8e1 | tar -x -C \"$tmp_root\"; (cd \"$tmp_root\" && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change 2>&1)",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 153.648s", "OK", "base_test_exit=0"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*s\\n\\nOK"}
    },
    {
      "id": "V14",
      "kind": "inspection",
      "cmd": "git diff --quiet $(git merge-base origin/main HEAD)..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md && git diff --quiet $(git merge-base origin/main HEAD)..HEAD -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["state_docs_unchanged=true", "frozen_estimators_unchanged=true"]},
      "expected": {"exit_code": 0, "tail_regex": "state_docs_unchanged=true\\nfrozen_estimators_unchanged=true"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The Darwin real-boot test remains skipped because kern.bootsessionuuid is unavailable in the restricted environment; the synthetic stale-boot verification-and-consumption regression ran and passed.",
      "needs": "Optional ordinary-macOS replay after the blocker is fixed."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The additional import-dependent tests.test_receipt_histsem run was interrupted after prolonged blocking in an internal subprocess; all five claimed modules completed, and the independent launch-module blocker already makes the landing non-landable.",
      "needs": "Re-run tests.test_receipt_histsem after B1 is fixed."
    }
  ]
}
```

## Findings

- B1 (blocker): The new shared fixture is not composable. `make_t0_fixture()` now receives two backup commands from `install_passing_freeze()`, while `make_author_fixture()` independently supplies two; `tests/test_launch_window.py:488` concatenates both graphs. The resulting four commands violate the production doctrine's exact-two invariant and break an importing module. V9 is the HEAD failure; V12 proves the exact test passed at the merge base; a direct count produced `2 + 2 = 4`.

The mission delta is exactly the six paths declared by `01-sol-report.md`; `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no delta, and the four frozen estimator sources remain unchanged. The directory contained no previous refuter verdict, so there was no prior non-staleness blocker to retest. Current counterfactuals are sound where applicable: a one-line mock mutation forcing legacy generic schemas made the new R1 test fail with `readiness_unknown_key`; the stale-boot input is a changed boot-session UUID and V3 proves both verification and consumption refuse; restoring the former static-map assertion fails because the governed `_v5` predecessor is `_v3` and is absent from `_PROFILE_BY_PACK`.

## Residual risk

The real boot-session lookup remains environment-skipped, and the extra `tests.test_receipt_histsem` import-dependent run did not complete before interruption. Neither limitation changes B1's causal result or the `NOT LANDABLE` verdict.
