```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Cured B1 by making the portable T-0 launch fixture compose to one closeout graph with exactly two backups, with direct and end-to-end regressions passing.",
  "workspace": {
    "base_requested": "e14b64f0009e198718479a3176038a11cce62240",
    "base_mode": "descendant",
    "head_start": "e14b64f0009e198718479a3176038a11cce62240",
    "head_end": "a3ddde422da6fcdf77dedd728d4abceb34d9eb7f",
    "upstream_end": "a3ddde422da6fcdf77dedd728d4abceb34d9eb7f",
    "branch": "feat/2026-09-04-fan-FIXTURE-MODERNIZATION-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/FIXTURE-MODERNIZATION-01/03-sol-fix-round-1-report.md",
    "tests/test_arm_readiness_evidence_t0.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/FIXTURE-MODERNIZATION-01/02-refuter-merge-base.md (pre-existing untracked input, concurrently committed as a3ddde42)"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_portable_launch_stage_fragment_composes_to_exactly_two_backups 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 4.071s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 162.251s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_integration tests.test_arm_readiness_lifecycle tests.test_s0_blocked_enumeration tests.test_launch_window tests.test_capture_t0_step tests.test_arm_readiness tests.test_arm_readiness_evidence_author tests.test_mint_analysis_admission 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 289 tests in 1419.644s", "", "OK (skipped=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 289 tests in .*s\\n\\nOK \\(skipped=2\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_integration tests.test_arm_readiness_lifecycle tests.test_s0_blocked_enumeration tests.test_launch_window tests.test_capture_t0_step tests.test_arm_readiness tests.test_arm_readiness_evidence_author tests.test_mint_analysis_admission tests.test_receipt_histsem 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "tests/test_receipt_histsem.py:1464: test_refresh_lane_is_idempotent_and_canonical blocked in self._run_refresh subprocess",
          "KeyboardInterrupt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran .* tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "tests.test_receipt_histsem again blocked in its unchanged refresh subprocess at test_refresh_lane_is_idempotent_and_canonical and was interrupted; the exact B1 launch test and all other touched/import-dependent modules passed.",
      "needs": "Lead may diagnose or replay that independent historical-semantics subprocess outside this fix round."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "After exact e14b64f0 preflight passed, HEAD and upstream advanced to direct descendant a3ddde42 via a concurrent custody-only commit of the pre-existing refuter report; no code changed.",
      "needs": "Lead should retain a3ddde42 as the trace-custody parent when landing this fix."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The focused aggregate retained two expected skips, including the restricted-host boot-session lookup already identified in the original seat report.",
      "needs": "Optional ordinary-macOS replay of the real sysctl variant."
    }
  ]
}
```

## Change

The portable-launch T-0 fixture now removes only the synthetic `fixture-verdict` and `fixture-backup` stages after it has built its otherwise complete standalone fixture. That mode is used by the launch-window integration, which immediately composes the returned T-0 stage fragment with `make_author_fixture()` and re-authors all freeze evidence. Ordinary T-0 callers retain the complete R1 closeout graph.

| Finding | Cure | File:line |
|---|---|---|
| B1: composing T-0's two backups with the author fixture's two yielded four, violating `DOCTRINE_PIN`. | Portable integration mode contributes no duplicate closeout stages, leaving the author fixture's one verdict and exact two backups. | `tests/test_arm_readiness_evidence_t0.py:684` |
| B1 counterfactual `2 + 2 = 4` lacked a direct regression. | The new regression performs the same two-fixture composition and requires one verdict plus exactly two backup commands; the formerly failing real launch/mint test also passes. | `tests/test_arm_readiness_evidence_t0.py:892` |

No magistrate-owned state row is needed for this cure, and no protected state file was modified.

## Verification notes

`tests.test_receipt_histsem` was attempted in the import-dependent aggregate but again blocked at its unchanged refresh subprocess and was interrupted. A second bounded run excluding only that module completed all 289 tests across the five touched modules and the other direct importers. The repository-wide discovery suite was not run, per the preflight rule.

## Residual risk

The portable mode intentionally returns a stage fragment whose stale synthetic freeze artifacts are immediately discarded and re-authored by its sole launch-integration consumer. The direct composition regression locks that contract; future additional consumers should use the ordinary complete fixture unless they likewise re-author after composition.
