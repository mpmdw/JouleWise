```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Completed A234/A212 fix round 2, including disk-backed F3 release checks and counterfactual tests; no commit made.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "head_end": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "upstream_end": "4c76ab6979a16e80e15d2174eafe4e1857aabac3",
    "branch": "feat/2026-09-23-refusal-early-release-f3"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "joulewise/arm_retry.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_arm_retry.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [
    "scripts/magistrate_watchdog.py",
    "joulewise/arm_retry.py",
    "tests/test_magistrate_watchdog.py",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_magistrate_watchdog.py tests/test_magistrate_watchdog_cli.py tests/test_arm_retry.py tests/test_install_magistrate_watchdog.py tests/test_evidence_night.py tests/test_docs_freshness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["315 passed, 756 subtests passed in 330.09s (0:05:30)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "315 passed, 756 subtests passed"
      }
    },
    {
      "id": "V2",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The unchanged zero_capture_successor_allowed predicate still requires harvested C5 evidence absent from live receipts; early watchdog release alone does not enable the new-plan successor.",
      "needs": "Lead to track the separate successor evidence path identified in ruling 16."
    }
  ]
}
```

## Change

| Item | Before → after | Biting test |
|---|---|---|
| F1 | The agent census could miss a live driver → a separate `run_night.py` probe must also be empty on the release tick ([watchdog:413](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:413), [watchdog:1606](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:1606)). | `test_live_driver_without_agent_census_match_holds_then_releases` ([test:379](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:379)) |
| F2 | The latch survived a replacement refusal at the same plan and root → its key includes the SHA-256 of `result.json` ([watchdog:881](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:881)). | `test_replaced_result_same_plan_and_root_requires_new_census` ([test:401](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:401)) |
| F3 | A delivered refusal could release despite a consumed marker or capture file → release now reads the pinned chain with the imported `probe_payload_kind` and `chain_literal`, checks the ruled custody locations, and fails closed on unreadable or ambiguous chain data ([watchdog:801](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:801), [watchdog:839](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:839)). The receipt retains its veto role; a bare C5 row supplies no disk evidence ([arm_retry:202](/Users/edr/code/wt-f2d6899b-f3/joulewise/arm_retry.py:202)). `zero_capture_successor_allowed` remains unchanged. | `test_f3_nested_consumed_marker_vetoes_release`, `test_f3_runs_root_consumed_marker_vetoes_release`, both capture-file tests, `test_f3_chain_started_vetoes_release`, `test_f3_clean_bare_c5_releases_and_latches`, and the unreadable, ambiguous, relative-root, and index tests ([tests:228](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:228)); the no-C5 successor assertion ([test_arm_retry:466](/Users/edr/code/wt-f2d6899b-f3/tests/test_arm_retry.py:466)). |
| S1 | An undelivered, started refusal lost its dead-man tail → that tail remains armed ([watchdog:929](/Users/edr/code/wt-f2d6899b-f3/scripts/magistrate_watchdog.py:929)). | `test_undelivered_chain_refusal_keeps_deadman_tail` ([test:433](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:433)) |
| S3 | The two explanations lacked the ruled terms and disk facts → both now state them in plain language ([handback:57](/Users/edr/code/wt-f2d6899b-f3/docs/process/NIGHT_HANDBACK.md:57), [runbook:1856](/Users/edr/code/wt-f2d6899b-f3/docs/phase_2/derivation_night_runbook.md:1856)). | First-use documentation read |
| N1 | The result chain-field veto lacked a counterfactual test → it is exercised through `decide()` ([test:446](/Users/edr/code/wt-f2d6899b-f3/tests/test_magistrate_watchdog.py:446)). | `test_result_chain_fields_veto_zero_capture_release` |

## Verification notes

Each injected single-fact mutant failed its named test: consumed check → `test_f3_nested_consumed_marker_vetoes_release`; calibration capture check → `test_f3_calibration_capture_file_vetoes_release`; evidence capture check and payload-kind branch → `test_f3_evidence_capture_file_vetoes_release`. Treating `chain.started` as absent also failed `test_f3_chain_started_vetoes_release`. There were no scope or test deviations.

## Residual risk

Ruling 16’s separate successor limitation remains: live receipts lack the harvested C5 block required by `zero_capture_successor_allowed`. The lead’s next step is final diff review and its full-suite gate.