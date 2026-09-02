```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All requested pins, generated-pack checks, and six emission mutants passed; the committed retired v3 pack refuses the current prospective validator.",
  "workspace": {
    "base_requested": "4a41d791",
    "base_mode": "exact",
    "head_start": "6296ce93",
    "head_end": "6296ce93",
    "upstream_end": "8db1ab7db4528d574c625a340a8fa8a6214ba450",
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "joulewise/analysis_manifest_v3.py",
        "line": 2932,
        "summary": "The committed frozen Qwen2.5 v3 pack refuses prospective validation, contrary to ruling 70c clause 7's legacy-validation promise."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=<scratch>/tmpdir-a /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 82 tests in 29.852s", "OK (skipped=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 82 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=<scratch>/tmpdir-b /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 82 tests in 29.632s", "OK (skipped=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 82 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-closeout-s1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_phase0_base_floor_bytes_are_pinned",
      "cwd": "/",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 3.766s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "git archive 4a41d791 | tar -x -C <scratch>/base-r4; git archive a4c88f4c tests/test_mint_floor_artifact_generalized.py | tar -x -C <scratch>/base-r4; python -m unittest ...test_phase0_base_floor_bytes_are_pinned",
      "cwd": "<scratch>/base-r4",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["phase0_floor_sha256=9127a51d5f3cb53263c90afd5c63c94d29442a3f9127f11aa25d0498e3c72400"]
      },
      "expected": {"exit_code": 0, "tail_regex": "phase0_floor_sha256=9127a51d"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d165_dominance_closeout tests.test_floor_mint_estimator tests.test_mint_floor_artifact_generalized tests.test_analysis_manifest_v3 tests.test_analysis_finalizer tests.test_d117_contrast_v5_pack tests.test_detection_floor",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 387 tests in 58.901s", "OK (skipped=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 387 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "find /tmp -maxdepth 1 -name 'joulewise-test-*' -print | wc -l",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["0"]},
      "expected": {"exit_code": 0, "tail_regex": "^0$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The archived v3 manifest has no finalization_contract and returns schema_invalid, unknown_key, unresolved_slot, and not_frozen under the current validator.",
      "needs": "Clarify or restore the clause-7 legacy-validation promise; D-167 retires this pack operationally."
    }
  ]
}
```

## Findings

- F1 — SHOULD-FIX — `joulewise/analysis_manifest_v3.py:2932`: the committed `d117_contrast_qwen25_1p5b_vs_7b_v3` manifest refuses validation. It is a nine-key, `as_generated_pre_d134_freeze` legacy form with no `finalization_contract`, yielding `schema_invalid`, `unknown_key`, `unresolved_slot`, and `not_frozen`. This conflicts with 70c clause 7’s “Legacy four-row packs … still validate” promise. D-167 retires Q2–Q4, so it is moot for the active `_v5` transaction, not for the stated compatibility guarantee.

Byte pin: both fresh-TMPDIR module runs passed; the `/` cwd pin passed. A pristine `4a41d791` archive with only `a4c88f4c`’s test file transplanted emitted:

`9127a51d5f3cb53263c90afd5c63c94d29442a3f9127f11aa25d0498e3c72400`

All mutations ran from separate `git archive 6296ce93` scratch copies and were killed.

| Mutant | Killing named test | Tail |
|---|---|---|
| (a) no gate/bind census | `V2PinsetAndMintTests.test_d165_recomputation_census_checks_a_late_cell` | `MintError not raised` |
| (b) no rollback after third write | `...test_d165_output_writer_rolls_back_floor_and_statement_on_third_failure` | `AssertionError: True is not false`; `floor.json` is left behind |
| (c) bypass sole builder | `...test_common_mode_full_cli_path_writes_bound_exact_artifact` | `AssertionError: 0 != 1` |
| (d) hash parsed sidecar JSON | `D165DominanceCloseoutTests.test_minted_mixed_floor_finalizes_and_refuses_default_contrast_cell` | `replay_sidecar_digest_mismatch != cell_not_common_mode` |
| (e) hard-code schema accessor | `...test_stage2_sidecar_ownership_ast_census` | second owner: `analysis_manifest_v3.py` |
| (f) accept four-row dominance contract | `AnalysisManifestV3Tests.test_dominance_criterion_without_attachment_is_named_refusal` | `AssertionError: 0 != 1` |

The integrated (a) mutant additionally completed the common-mode CLI scenario and wrote its sidecar despite a deliberately altered gate recomputation; the direct census test kills that unsafe condition.

Generated `_v5` pack: five required attachments, validator refusals `()`. Reducing it to four rows produced `analysis_prospective_dominance_replay_attachment_missing` (also expected schema and plan-tree mismatch refusals).

Full requested module set: 387 passed, 2 skipped. `/tmp/joulewise-test-*` is empty.

## Residual risk

- No independent behavioral test simulates an owner schema-version change; the AST ownership census is the sole guard against re-hardcoding the accessor. No real models or hardware were exercised, as required.