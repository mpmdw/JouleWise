```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented A–D fixture and contract repairs; all nine named acceptance modules and git diff --check passed.",
  "workspace": {
    "base_requested": "bda71e60",
    "base_mode": "exact",
    "head_start": "bda71e604e93dafb59fd1362aaed0116fb3efbe1",
    "head_end": "bda71e604e93dafb59fd1362aaed0116fb3efbe1",
    "upstream_end": "bda71e604e93dafb59fd1362aaed0116fb3efbe1",
    "branch": "int/2026-09-08-d176-seats-2-3"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "tests/test_arm_readiness.py",
    "tests/test_magistrate_watchdog_cli.py",
    "tests/test_powermetrics_fiducial.py",
    "tests/test_run_campaign.py",
    "tests/test_t0_rehearsal.py"
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
      "cmd": "python3 -m unittest tests.test_magistrate_watchdog_cli tests.test_powermetrics_fiducial tests.test_run_campaign tests.test_arm_readiness tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_run_night tests.test_docs_freshness > /private/tmp/d176-integrated-acceptance.log 2>&1\nsuite_rc=$?\ntail -n 32 /private/tmp/d176-integrated-acceptance.log\nprintf '\\nSUITE_RC=%s\\n' \"$suite_rc\"\ngit diff --check > /private/tmp/d176-integrated-diff-check.log 2>&1\ndiff_rc=$?\ncat /private/tmp/d176-integrated-diff-check.log\nprintf 'DIFF_CHECK_RC=%s\\n' \"$diff_rc\"\ngit status --short --branch\ngit rev-parse HEAD\ngit rev-parse '@{upstream}'\nif [ \"$suite_rc\" -ne 0 ]; then\n  exit \"$suite_rc\"\nfi\nexit \"$diff_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SUITE_RC=0",
          "DIFF_CHECK_RC=0",
          "## int/2026-09-08-d176-seats-2-3...origin/int/2026-09-08-d176-seats-2-3",
          " M docs/contracts/pack_night_go_receipt.md",
          " M tests/test_arm_readiness.py",
          " M tests/test_magistrate_watchdog_cli.py",
          " M tests/test_powermetrics_fiducial.py",
          " M tests/test_run_campaign.py",
          " M tests/test_t0_rehearsal.py",
          "bda71e604e93dafb59fd1362aaed0116fb3efbe1",
          "bda71e604e93dafb59fd1362aaed0116fb3efbe1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SUITE_RC=0\\nDIFF_CHECK_RC=0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "A read-only ps diagnostic was sandbox-denied while waiting; acceptance subsequently completed successfully.",
      "needs": ""
    }
  ]
}
```

## Change

- **A:** Current watchdog helper lacked the entire binding. Added all six exact keys, including absolute `pack_root` with matching basename. Parser unchanged; no external fixture files needed edits.
- **B:** **TRANSACTION_PACK branch.** Committed the calibration config in temporary fixture Git, refreshed digest bindings, and documented the no-untracked-entry invariant in §10.3.
- **C:** **Pack launch with GO present.** The broad child-process mock intercepted Git during GO replay. Restricted it to the synthetic child; retained `launch_lineage_conflict`.
- **D:** Pinned F6 to lines **703 / 980 / 787**, corrected “items 6–9,” and separated reusable fixture setup from strict test-case isolation.

## Verification notes

C matched neither proposed failure scenario: the defect was mock interference, not missing GO or a production class leak.

[Acceptance log](/private/tmp/d176-integrated-acceptance.log). No commit made. Next step: lead diff review.