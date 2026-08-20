```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented scheduler-gate stages 1-2: strict vocabulary/schema, G4 reviewed-main enforcement, and G5 create-only campaign boot pin.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "088c20da8984484805aae8fb82a13330ec1b8af2",
    "head_end": "088c20da8984484805aae8fb82a13330ec1b8af2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "joulewise/scheduler_gates.py",
    "tests/test_scheduler_gates.py"
  ],
  "unowned_dirty": [
    "schedgate-opus-design.md",
    "schedgate-ruling.md",
    "schedgate-terra-design.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "set -o pipefail\nPYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_scheduler_gates -v 2>&1 | tee /tmp/joulewise-scheduler-gates-stage12.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 23 tests in 0.933s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 23 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "set -o pipefail\nPYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests 2>&1 | tee /tmp/joulewise-full-suite-stage12.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3783 tests in 2904.312s",
          "OK (skipped=100)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3783 tests in .*s[\\s\\S]*OK \\(skipped=100\\)"
      }
    }
  ],
  "flags": []
}
```

## Change

File manifest:

- [scheduler_gates.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtIMPL/joulewise/scheduler_gates.py) adds the separate closed vocabulary, exact v1 receipt validation, G4, G5, and fail-closed staged composition.
- [test_scheduler_gates.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtIMPL/tests/test_scheduler_gates.py) adds 23 schema, vocabulary, G4, G5, ordering, reboot, race, and no-pack-write regressions.
- `scripts/evaluate_window_gates.py` remains absent because CLI/wiring is ruled Stage 6.

| Gate | Stage behavior | Refusal-code vocabulary |
|---|---|---|
| G1 | `NOT_IMPLEMENTED`, or `NOT_EVALUATED` after G5 refusal | `scheduler_fuse_insufficient`, `scheduler_fuse_underivable`, `scheduler_span_undeclared`, `scheduler_budget_unresolved` |
| G2 | `NOT_IMPLEMENTED`, or `NOT_EVALUATED` after G5 refusal | `scheduler_halt_bound_violated`, `scheduler_campaign_halted`, `scheduler_bounds_unmeasured`, `scheduler_timing_underivable`, `scheduler_timing_cross_boot` |
| G3 | `NOT_IMPLEMENTED` | `scheduler_b22_cure_absent`, `scheduler_b22_binding_absent`, `scheduler_b22_cure_ineffective`, `scheduler_shakedown_record_claim_use` |
| G4 | Implemented | `readiness_git_tree_dirty`, `readiness_reviewed_main_mismatch`; both carry `mirrored_from: arm_readiness` |
| G5 | Implemented first | `scheduler_boot_pin_mismatch`, `scheduler_boot_pin_underivable`, `scheduler_boot_pin_conflict` |
| G6 | `NOT_IMPLEMENTED` | All ruled C1–C5 scheduler codes are reserved in the closed vocabulary |

The composed receipt cannot become `GO` while any gate is `NOT_IMPLEMENTED` or `NOT_EVALUATED`. G4 requires `exact_match is True`; G5 uses `O_EXCL` creation and treats the campaign-span pin as authoritative. Only the campaign custody root is written.

## Verification notes

The mandatory full focused log is `/tmp/joulewise-scheduler-gates-stage12.log`. It includes the reboot and moved-main falsifiers. The supplemental canonical-suite log is `/tmp/joulewise-full-suite-stage12.log`; its 100 skips are existing corpus/environment skips. No ruling constraint in Stages 1–2 was left unsatisfied.