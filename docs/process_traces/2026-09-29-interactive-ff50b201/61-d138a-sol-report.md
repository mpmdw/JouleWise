```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Loader repair and promotion tool implemented; requested checks pass, but sandbox permissions prevent staging and committing.",
  "workspace": {
    "base_requested": "9eab16f8",
    "base_mode": "exact",
    "head_start": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "head_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": "feat/2026-09-29-d138-loader-promotion"
  },
  "pathspec": [
    "joulewise/calibration_dispositions.py",
    "joulewise/calibration_bracketing.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "scripts/promote_calibration_candidate.py",
    "tests/test_calibration_dispositions.py",
    "tests/test_promote_calibration_candidate.py",
    "tests/test_calibration_bracketing.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_calibration_dispositions tests.test_promote_calibration_candidate tests.test_calibration_bracketing tests.test_acc_25g83_rev5",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 123 tests in 17.643s", "FAILED (errors=7, skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_calibration_dispositions tests.test_promote_calibration_candidate tests.test_calibration_bracketing tests.test_acc_25g83_rev5 > /private/tmp/d138-option-a-focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 125 tests in 19.565s", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git grep -n -i 'claim_hold\\|held_build\\|n12_25g83_r1' -- joulewise scripts tests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git grep --untracked -n -i 'claim_hold\\|held_build\\|n12_25g83_r1' -- joulewise scripts tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["scripts/promote_calibration_candidate.py:25:ACCEPTANCE_ID = \"d079_calibration_acceptance_v2_n12_25g83_r1\""]
      },
      "expected": {"exit_code": 0, "tail_regex": "scripts/promote_calibration_candidate.py:25:ACCEPTANCE_ID"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -B /private/tmp/d138-option-a-counterfactual.py > /private/tmp/d138-option-a-counterfactual.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["All 9 scratch counterfactuals RED; all 9 restorations GREEN; repository files untouched."]
      },
      "expected": {"exit_code": 0, "tail_regex": "All 9 scratch counterfactuals RED; all 9 restorations GREEN"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -B /private/tmp/d138-option-a-inspect.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ISSUED_ACCEPTANCE_REGISTRY: unchanged from base",
          "_D102_GENERATION_DERIVATIONS: unchanged from base",
          "ACTIVE_ACCEPTANCE_ID: unchanged from base",
          "DEFAULT_ACCEPTANCE_BOUND_PATH: unchanged from base",
          "Exactly seven allowed repository paths modified; no other dirty paths."
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Exactly seven allowed repository paths modified"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "other",
      "cmd": "git add -- joulewise/calibration_dispositions.py joulewise/calibration_bracketing.py scripts/issue_calibration_acceptance_generation.py scripts/promote_calibration_candidate.py tests/test_calibration_dispositions.py tests/test_promote_calibration_candidate.py tests/test_calibration_bracketing.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-d138a-ff50b201/index.lock': Operation not permitted"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /private/tmp/d138-option-a-canonical.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The shared worktree Git metadata directory is outside writable sandbox roots. Staging failed; no commit was created and nothing was pushed.",
      "needs": "Lead stages the seven allowed paths and commits with message prefix 'D-138 option (a):'."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The additional canonical suite was interrupted after the staging blocker; it did not finish. The final requested focused suite passed.",
      "needs": "Lead reruns the canonical suite before final acceptance."
    }
  ]
}
```

## Change

The seven-file implementation is ready for lead review. R7 remains the default; registration, generation tables, pins, hold routing, and docs remain unchanged.

Source-hunk ledger, relative to `9eab16f8` → `b953f4b0`:

| File | Ported / adapted | Dropped and reason |
|---|---|---|
| `joulewise/calibration_dispositions.py` | Entire source module: pinned parser and disposition table/helpers. | Nothing; module contains the loader repair. |
| `joulewise/calibration_bracketing.py` | Disposition import and hunks at base lines 975, 982, 1021, 2396: declaration checks, diagnostic exclusion, completeness, doubling count. | All registration, OS-build map, operative-wrapper, inspection-seam, hold-routing and export changes. |
| `scripts/issue_calibration_acceptance_generation.py` | Shared-loader import, constants relocation and `_registered_dispositions` parser delegation. | R7-specific import/predecessor/default changes; these belong to registration. |
| `scripts/promote_calibration_candidate.py` | Source promotion logic, seals, citation and metadata validation. Made `--issuance-text` required. | Removed default reference to the dropped issuance document. No runtime hold enforcement is introduced. |
| `tests/test_calibration_dispositions.py` | Disposition fences adapted to an existing synthetic generation; added duplicate-key issuer regression. | Withdrawn-file loading and hold inspection dependencies. |
| `tests/test_promote_calibration_candidate.py` | Protection, seal and citation tests use temporary output/evidence; CLI input requirement tested. | Registered-file pin checks and P5 registry-row comparison. |
| `tests/test_calibration_bracketing.py` | DT4 counting regression adapted to the existing synthetic doubling fixture. | Withdrawn-generation imports, hold fixtures/comments and registration exceptions. |

No `NEEDS_SCOPE` or `NEEDS_RULING` item arose.

## Verification notes

The initial seven test errors came from a temporary-root symlink mismatch in the adapted promotion fixture. Resolving that root fixed them.

The exact requested `git grep` excludes untracked files, so I additionally ran it with `--untracked`. Its sole hit is:

```text
scripts/promote_calibration_candidate.py:25:ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n12_25g83_r1"
```

This constant identifies the candidate the tool promotes; it adds no registration or load authority.

Counterfactuals ran in scratch copies using `python3 -B -m unittest <test>`. Every mutation exited 1; every restoration exited 0.

| Mutation | Named regression |
|---|---|
| Remove duplicate-key parser hook | `DispositionTests.test_issuer_rejects_duplicate_json_keys` |
| Restore pre-repair issuer call site | `DispositionTests.test_issuer_rejects_duplicate_json_keys` |
| Restore pre-repair bracketing loader | `DispositionTests.test_l1_synthetic_disposed_diagnostics_validate` |
| Remove decision-declaration equality | `DispositionTests.test_l10_undeclared_decision_touching_prior_set_refuses` |
| Remove disposed-prefix completeness guard | `DispositionTests.test_l5_missing_disposed_row_refuses` — RED through `KeyError` |
| Remove registration/member fence | `DispositionTests.test_l6_disposed_inside_registration_refuses` |
| Count disposed diagnostics toward doubling | `CalibrationBracketingTests.test_corpus_doubling_excludes_disposed_diagnostics` |
| Remove promotion input-seal guard | `PromotionTests.test_p7_issued_input_seal_drift_stops` |
| Restore implicit issuance-text default | `PromotionTests.test_cli_requires_explicit_issuance_text` |

[Full counterfactual commands and outputs](/private/tmp/d138-option-a-counterfactual.log), [replay script](/private/tmp/d138-option-a-counterfactual.py), [focused suite output](/private/tmp/d138-option-a-focused.log).

The canonical suite was explicitly interrupted; no completed result is claimed. [Canonical output](/private/tmp/d138-option-a-canonical.log).

**No commit was created.** Staging failed because the shared Git metadata directory is outside the sandbox’s writable roots. Next exact step: lead stages the seven allowed paths, reruns the canonical suite, and commits with `D-138 option (a): port loader repair and promotion tool`.