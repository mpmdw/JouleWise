```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Fixes applied within scope; named acceptance ran 309 tests with one failure and one error; diff check passed.",
  "workspace": {
    "base_requested": "3032dd93",
    "base_mode": "exact",
    "head_start": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "head_end": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "upstream_end": "3032dd9371d262450ede4418f784c8ea4a9055c7",
    "branch": "feat/2026-09-08-d176-seat4-rehearsal"
  },
  "pathspec": [
    "docs/contracts/pack_night_go_receipt.md",
    "docs/process/NIGHT_HANDBACK.md",
    "joulewise/arm_readiness.py",
    "joulewise/t0_rehearsal.py",
    "scripts/launch_window.py",
    "scripts/rehearse_t0_unattended.py",
    "scripts/run_night.py",
    "tests/test_arm_readiness.py",
    "tests/test_launch_window.py",
    "tests/test_rehearse_t0_unattended.py",
    "tests/test_t0_rehearsal.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_arm_readiness tests.test_rehearse_t0_unattended tests.test_docs_freshness > /private/tmp/d176-seat4-fix-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 309 tests in 455.699s",
          "FAILED (failures=1, errors=1)",
          "SUITE_EXIT_CODE=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check >> /private/tmp/d176-seat4-fix-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["DIFF_EXIT_CODE=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DIFF_EXIT_CODE=0$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The non-pack regression errors at tests/test_launch_window.py:2368: its DIAGNOSTIC_NO_PACK fixture omits required registration_path, so it never reaches admission.",
      "needs": "Repair the non-pack fixture and rerun named acceptance."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The existing refusal regression fails at tests/test_launch_window.py:2459 because it expects zero rehearsal consumptions; the new completed-rehearsal fixture correctly retains one.",
      "needs": "Assert preservation of pre-existing rehearsal consumption and absence of new control consumption, then rerun named acceptance."
    }
  ]
}
```

## Change

| Finding | Implementation and counterfactual |
|---|---|
| 1 | `scripts/rehearse_t0_unattended.py:144` admits absent G7; `joulewise/t0_rehearsal.py:875` reports `g7_control_pending`. Regression `tests/test_t0_rehearsal.py:750` removes the locator and artifact: nine gates pass without a load error. Sequencing added to §6/§10.5 and `NIGHT_HANDBACK.md:118`. |
| 2 | `tests/test_t0_rehearsal.py:432` builds current GO/consumption evidence; `:743` asserts ten-gate PASS through the loader. D-149 refusal remains covered. One older consumption-absence assertion needs repair. |
| 3 | `joulewise/arm_readiness.py:9944/:9951` distinguishes GO-shape and plan-class details; `joulewise/t0_rehearsal.py:856` accepts only the GO detail. Validator mutations reject aliased details; the new non-pack execution regression remains blocked by its malformed fixture. |
| 4 | Contract §7.1 row 4 (`:639`) and §9 B4/S1/S4/N1 carry verified symbol-line pins. Inspection rejects a pin naming the wrong source line. |
| 5 | Contract S4 (`:855`) restores root/census citations; N1 (`:858`) restores confirmation validation. Counterfactuals cover wrong-name custody, stale census, and string confirmation epochs. |
| 6 | `tests/test_t0_rehearsal.py:762` changes, omits, and substitutes real T-0 capture files from a G5 PASS fixture. Each produces G5 FAIL while GO/C2 bytes remain unchanged. |
| 7 | Removed debug output and restored the original explanatory comment at `scripts/launch_window.py:109`. |
| Astra F1 | `scripts/run_night.py:1318` checks destination resolution and confines writes through directory descriptors. Regressions at `tests/test_launch_window.py:2275/:2278` reject symlinked destinations without changing completed rehearsal files. |

`night_gate.py` is unchanged; `arm_readiness.py` changes only the two admission details. No commit.

## Verification notes

Stopped after named acceptance as instructed. Two test repairs remain before this is ready; exact causes and next steps are in the flags above.

[Acceptance log](/private/tmp/d176-seat4-fix-acceptance.log)

## Residual risk

Evidence is synthetic; ARM semantics and pack metadata remain fixture-controlled. No live hardware qualification was performed.