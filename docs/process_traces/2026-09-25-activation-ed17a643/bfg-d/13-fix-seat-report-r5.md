```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented FX-1 through FX-11 within scope; two acceptance verification questions remain for the lead.",
  "workspace": {
    "base_requested": "df33888f",
    "base_mode": "descendant",
    "head_start": "32456d400a3e44e64dae7773887bac46653dc6e0",
    "head_end": "32456d400a3e44e64dae7773887bac46653dc6e0",
    "upstream_end": "32456d400a3e44e64dae7773887bac46653dc6e0",
    "branch": "feat/2026-09-25-bfg-d"
  },
  "pathspec": [
    "docs/phase_2/derivation_night_runbook.md",
    "joulewise/battery_float.py",
    "scripts/calibration_cadence_report.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "scripts/issue_epoch_continuation.py",
    "scripts/run_night.py",
    "tests/fixtures/battery_float/.gitattributes",
    "tests/fixtures/epoch_bootstrap/build.py",
    "tests/fixtures/epoch_continuation/build.py",
    "tests/test_acc_25g83_rev5.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_battery_float.py",
    "tests/test_calibration_cadence_report.py",
    "tests/test_epoch_continuation.py",
    "tests/test_issue_calibration_acceptance_generation.py",
    "tests/test_run_night.py",
    "tests/test_validate_powermetrics_fiducial_derivation_only.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {"id":"V1","kind":"suite","cmd":"python3 -m unittest tests.test_battery_float","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 35 tests in 1.328s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"suite","cmd":"PYTHONPATH=\"$PWD\" python3 /tmp/bfgd_issuer_skip.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 137 tests in 116.702s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK \\(skipped=1\\)"}},
    {"id":"V3","kind":"suite","cmd":"python3 -m unittest tests.test_calibration_cadence_report","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 9 tests in 2.031s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"suite","cmd":"python3 -m unittest tests.test_epoch_continuation","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 67 tests in 57.035s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V5","kind":"suite","cmd":"python3 -m unittest tests.test_acc_25g83_rev5","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 15.497s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V6","kind":"suite","cmd":"python3 -m unittest tests.test_night_gate","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 104 tests in 1.090s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V7","kind":"suite","cmd":"python3 -m unittest tests.test_run_night","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 236 tests in 91.445s","OK (skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V8","kind":"suite","cmd":"python3 -m unittest tests.test_evidence_night","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 159 tests in 254.526s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V9","kind":"suite","cmd":"python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 26 tests in 200.409s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V10","kind":"suite","cmd":"python3 -m unittest tests.test_custody_mode_inventory","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 7 tests in 39.297s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V11","kind":"suite","cmd":"python3 -m unittest tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 31 tests in 0.543s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V12","kind":"suite","cmd":"python3 -m unittest tests.test_gen_state","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 44 tests in 1.915s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V13","kind":"inspection","cmd":"git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V14","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The plain issuer suite failed only at its live machine identity test: os_build was None. The passing rerun skipped that test at runtime without changing its assertion; this seat prohibits model inference.",
      "needs": "Lead-controlled rerun of the plain issuer module in an environment where the live identity probe is permitted."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "FX-2's synthetic prepare-candidate process used a fixture-only empty disposition-registry override. The unpatched CLI refuses because the synthetic ledger lacks the production registry's eleven historical content IDs.",
      "needs": "Rule whether that fixture seam satisfies the real-CLI requirement, or supply an authentic prior-row fixture for an unpatched CLI run."
    }
  ]
}
```

## Change

Implemented the parser structure checks, pin-and-verdict commit binding, full Git-history check, ledger-derived cadence inventory and digest authentication, dry-run B-evidence gate and omitted non-pass blocker, registration-digest checks, CLI bootstrap, and 10-second production battery probe timeout. Updated the runbook and FX-10/FX-11 test documentation. Changes remain uncommitted and within `WRITE_SCOPE`.

One existing expected-message assertion changed from `missing or uncommitted for W1: absent or uncommitted` to `ledger: calibration_ledger_head_uncommitted`: the pin now remains uncommitted until the verdict is committed with it. The liveness docstring arithmetic changed from 600 to 610 seconds and from 715 to 725 seconds; its assertion was unchanged.

## Verification notes

Each RED check ran against `df33888f` in a temporary archive with the new tests overlaid. Where an old API lacked a new digest argument, the temporary harness removed only that argument to reach the old behavior. GREEN results are from the changed worktree.

| FX | RED at `df33888f` | GREEN |
|---|---|---|
| 1 | `Ran 3 tests ... FAILED (failures=16)`; malformed objects passed parser, gate, and window checks | `Ran 35 tests ... OK` |
| 2 | `Ran 1 test ... FAILED (failures=1)`; verdict refused the uncommitted pin. Separate or wrong pin commits were also accepted by the old loader | End-to-end fixture test `Ran 1 test ... OK`; battery module `Ran 35 tests ... OK` |
| 3 | `Ran 2 tests ... FAILED (failures=2)`; merge modification and separate pin commit raised no `NoRecord` | `Ran 35 tests ... OK` |
| 4 | `Ran 1 test ... FAILED (failures=1)`; swapped capture raised no `ValueError` | `Ran 9 tests ... OK` |
| 5–6 | `Ran 2 tests ... FAILED (failures=2)`; B-bearing member evidence was opened, and omitted W1 returned `0` instead of `5` | `Ran 2 tests ... OK` |
| 7 | `Ran 2 tests ... FAILED (failures=5)` for check and continuation; cadence’s missing-digest test also failed | Issuer `Ran 137 tests ... OK (skipped=1)`; cadence `Ran 9 tests ... OK`; continuation `Ran 67 tests ... OK` |
| 8 | `Ran 1 test ... FAILED (failures=1)` with `ModuleNotFoundError: No module named 'joulewise'` | `Ran 9 tests ... OK` |
| 9 | `Ran 1 test ... FAILED (failures=1)`; ioreg received 30 seconds instead of 10 | `Ran 1 test ... OK`; full driver `Ran 236 tests ... OK (skipped=9)` |

The required `c6814dd8` pin-diff command produced **no output**. `git diff --check` passed, and the battery capture fixture reports `whitespace: unset`.

## Residual risk

**NEEDS_RULING:** Is the fixture-only disposition-registry override acceptable evidence for FX-2’s prepare CLI step? Accepting it preserves the focused transaction test; requiring a wholly unpatched CLI needs a fixture containing the eleven authentic historical prior rows. I recommend the latter for strict acceptance. The plain issuer suite also awaits the lead-controlled live identity test described in F1.