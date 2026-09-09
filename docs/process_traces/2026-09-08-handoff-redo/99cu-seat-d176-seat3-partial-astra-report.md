```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_SCOPE: implemented schema, GO-reading, registry and refusal foundations; live consumer/replay migration remains pending.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "7b9d4a7b2ecc39c60c6e61b583c8e0ab434a7bd5",
    "head_end": "7b9d4a7b2ecc39c60c6e61b583c8e0ab434a7bd5",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-d176-seat3-consumer"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "scripts/launch_window.py",
    "docs/contracts/d078_reason_registry_amendment.md",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_launch_window.py",
    "docs/contracts/pack_night_go_receipt.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas tests.test_arm_readiness_lifecycle tests.test_launch_window tests.test_d078_reason_registry tests.test_docs_freshness > /private/tmp/d176-seat3-acceptance.log 2>&1; rc=$?; tail -n 8 /private/tmp/d176-seat3-acceptance.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 180 tests in 506.401s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.PackNightGoSchemaTests tests.test_launch_window.PackNightGoRefusalHandlerTests > /private/tmp/d176-seat3-focused.log 2>&1; rc=$?; tail -n 5 /private/tmp/d176-seat3-focused.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 8 tests in 0.014s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check > /private/tmp/d176-seat3-diff-check.log 2>&1; rc=$?; cat /private/tmp/d176-seat3-diff-check.log; exit $rc",
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
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests > /private/tmp/d176-seat3-canonical.log 2>&1; rc=$?; tail -n 12 /private/tmp/d176-seat3-canonical.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Prospective expansion requested; no out-of-scope edits made. tests/test_arm_readiness.py owns LaunchConsumptionV2Tests._consumer_inputs and live-v2 expectations used by the scoped acceptance tests and other suites. Its fixture omits all six newly required inputs.",
      "needs": "Add tests/test_arm_readiness.py to WRITE_SCOPE and resume the consumer/replay migration."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical suite was deliberately interrupted with exit 130 for this scope handoff; no canonical pass is claimed. The final basis-type correction and eighth new test were verified by V2 after V1 had started.",
      "needs": "Complete canonical verification after the resumed implementation."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced during this run; the worktree HEAD remained unchanged.",
      "needs": "Lead reconciles the implementation with the integrated head."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_arm_readiness.py"],
    "reason": "The shared launch fixture and existing live-v2 assertions must migrate alongside the mandatory six-input consumer and historical-only v2 replay.",
    "blocked_work": "Complete consumer enforcement, v3 emission, replay and child integration, reader-mode migration, and their integrated regressions.",
    "minimal_change": "Upgrade LaunchConsumptionV2Tests shared launch inputs with authenticated plan, GO and confirmation fixtures; separate historical-v2 expectations from live-v3 tests while preserving existing adversarial coverage."
  }
}
```

## Change

Installed R1–R3 in §10.2, registered both GO codes outside seat 2’s constants area, added exact GO/v3 schema validation and a GO byte-reading helper, and unified launcher refusal handling.

The [per-clause map](/Users/edr/code/JouleWise-wt-d176-seat3/docs/contracts/pack_night_go_receipt.md:808) identifies implemented checks, regressions, counterfactuals, and pending clauses. No commit was made.

## Verification notes

The exhaustive `WRITE_SCOPE` excludes the shared fixture migration described above. Expand that exact path and resume. Canonical verification remains incomplete because the run was interrupted for this handoff.

## Residual risk

The live consumer and reader still use v2. The new helpers are not yet wired into consumption, replay, or child execution; this partial diff does **not** enforce the D-176 GO gate.