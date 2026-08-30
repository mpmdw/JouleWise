```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 2 leaves one blocker and two should-fix defects: direct typed configs and exported JSON Schema still admit one-pin identity, the new failure vocabulary is absent from tracked contract/golden surfaces, and replay applies the production predicate to a near-equal caller bound rather than the authenticated bound.",
  "workspace": {
    "base_requested": "7749f493",
    "base_mode": "exact",
    "head_start": "60beae60fe9533b1d969d46e6dee012df38395fe",
    "head_end": "60beae60fe9533b1d969d46e6dee012df38395fe",
    "upstream_end": "60beae60fe9533b1d969d46e6dee012df38395fe",
    "branch": "feat/v5-ladder-prep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "dispositions": {
      "E-1": "PARTIAL",
      "E-2": "PARTIAL",
      "E-3": "PARTIAL",
      "E-4": "INSTALLED",
      "E-5": "PARTIAL",
      "E-6": "INSTALLED",
      "D-1-golden-byte-pins": "INSTALLED",
      "round-1-generator-refusals": "INSTALLED",
      "round-1-admit-tool": "INSTALLED"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The public typed-config and exported-schema paths still admit a one-pin identity and can reach model load",
        "file_line": "joulewise/schemas.py:728,753,1031,1057,1126; joulewise/controller.py:269; joulewise/adapters/mlx_runtime.py:90,94,117",
        "refutation": "from_mapping raises the named SchemaError for both one-pin mappings, but a directly constructed ModelConfig with only chat_template_sha256 passes BenchmarkConfig.validate(), serializes one pin, passes the exported JSON Schema, skips tokenizer hashing, and reaches mlx_lm.load. Re-entry through BenchmarkConfig.from_mapping refuses, so loaders are closed but the public typed API and schema are not."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "MODEL_IDENTITY_MISMATCH was not propagated to the tracked output-schema and contract vocabularies",
        "file_line": "tests/goldens/output_schema.json:605,683; joulewise/schemas.py:263,1708,1803; docs/decision_log.md:683,693; docs/contracts/adapter_contracts.md:684",
        "refutation": "Fresh output-schema generation adds model_identity_mismatch in two enum sites, while the checked-in golden rejects a failed summary carrying that value. The binding D-012 mapping and Structured Failure Reasons contract also omit it. Dynamic summary validation, NodeWorkerClient, publication privacy, reporting surfaces, and the controller accept/map it correctly; no frozen runtime evidence validator was found that rejects it."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Replay invokes the production window predicate with the caller's near-equal bound instead of the authenticated bound",
        "file_line": "configs/campaigns/d117_contrast_v5/generate_configs.py:671,689; joulewise/floor_extraction.py:362",
        "refutation": "With authenticated b=0.036782638697819788 and supplied b'=b-5.000028e-13, the existing 1e-12 authentication tolerance accepts b'. A window ending at 2*b'+2e-13 passes the production predicate under b' but fails it under authenticated b; replay accepts it with ratio 3.6330628731577335. Thus importing the predicate did not make the accepted-input set identical to production."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "git diff --check 7749f493..60beae60",
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
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_schemas.BenchmarkConfigTests.test_model_identity_sha256_pins_validate_export_and_schema tests.test_schemas.BenchmarkConfigTests.test_model_identity_sha256_pins_reject_noncanonical_values tests.test_schemas.BenchmarkConfigTests.test_model_identity_sha256_pins_reject_incomplete_pair tests.test_schemas.SummaryMetricsTests.test_summary_metrics_schema_has_failure_contract tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_matches_independent_retained_fixture_calculation tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_refuses_unauthenticated_or_invalid_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.030s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c $'import io,tempfile\\nfrom contextlib import redirect_stdout\\nfrom pathlib import Path\\ntempfile.tempdir=\".\"\\nfrom joulewise.cli import main\\ns=io.StringIO()\\nwith redirect_stdout(s): code=main([\"print-config-schema\"])\\nequal=s.getvalue()==Path(\"tests/goldens/config_schema.json\").read_text()\\nprint(f\"cli_exit={code} equal={equal}\")\\nraise SystemExit(0 if code==0 and equal else 1)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "cli_exit=0 equal=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "equal=True"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c $'import io,tempfile\\nfrom contextlib import redirect_stdout\\nfrom pathlib import Path\\ntempfile.tempdir=\".\"\\nfrom joulewise.cli import main\\ns=io.StringIO()\\nwith redirect_stdout(s): code=main([\"print-output-schema\"])\\nequal=s.getvalue()==Path(\"tests/goldens/output_schema.json\").read_text()\\nprint(f\"cli_exit={code} equal={equal}\")\\nraise SystemExit(0 if code==0 and equal else 1)'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "cli_exit=0 equal=False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "equal=True"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2727 tests in 100.316s",
          "FAILED (errors=1733, skipped=112)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical suite cannot establish a clean result under the enforced read-only filesystem: sampled and import-time errors uniformly report that Python has no usable temporary directory; the summary reports errors, not assertion failures.",
      "needs": "Replay the canonical suite in the normal writable test environment."
    },
    {
      "id": "FL2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Fresh output-schema comparison also exposes a pre-existing missing energy_anchor_shift_envelopes property. A base-vs-head fresh-schema comparison isolates the round-2 change to the two model_identity_mismatch enum insertions.",
      "needs": "Keep the pre-existing schema-golden drift separately attributed when repairing the round-2 E-5 omission."
    }
  ]
}
```

## Findings

### BLOCKER F1 — Both-or-neither is not enforced by all validation boundaries

[ModelConfig.from_mapping](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:739) now raises `model_identity_sha256_pins_incomplete` for either one-pin mapping, and the regression covers both fields. The paired-pins test is also sound: patching `_sha256_file` proves the tokenizer check is reached; independently patching `sha256_hex` can only raise after the tokenizer check succeeds.

But [BenchmarkConfig.validate](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:1031) does not validate the model invariant, and the exported model schema at [schemas.py:1126](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:1126) has no paired-field `allOf`. A direct `ModelConfig`/`dataclasses.replace` construction therefore:

- passes `config.validate()`;
- serializes exactly one pin through `to_dict()`;
- passes the exported schema;
- passes the controller’s validation call at [controller.py:269](/Users/edr/code/JouleWise-wt-s15/joulewise/controller.py:269);
- executes only the present pin’s conditional branch and reaches `mlx_lm.load`.

The read-only probe used a template-only config, made tokenizer hashing raise if called, supplied a matching template hash, and observed `adapter_ok=True` with one load call. `BenchmarkConfig.from_mapping(config.to_dict())` does refuse, so mapping/JSON loaders are protected; the typed production entry point and exported validator are not.

Refutation path: make `BenchmarkConfig.validate()` or `ModelConfig` itself enforce the invariant, add the equivalent exported-schema constraint, and add a direct-construction regression proving refusal before adapter preparation.

### SHOULD-FIX F2 — E-5’s closed vocabulary propagation is incomplete

The production pieces are correct:

- `FailureReason.MODEL_IDENTITY_MISMATCH.value == "model_identity_mismatch"`.
- All four missing/mismatched pin branches at [mlx_runtime.py:99](/Users/edr/code/JouleWise-wt-s15/joulewise/adapters/mlx_runtime.py:99) use it.
- [STATUS_BY_REASON](/Users/edr/code/JouleWise-wt-s15/joulewise/controller.py:171) maps it to `FAILED`.
- The exhaustive controller regression compares the mapping keys with all `FailureReason` members.
- Dynamic summary validation, dynamic JSON Schema, `NodeWorkerClient`, publication transformation, report access, and salvage’s open-string comparison accept it.

However, fresh `print-output-schema` bytes differ from [tests/goldens/output_schema.json:605](/Users/edr/code/JouleWise-wt-s15/tests/goldens/output_schema.json:605) and `:683`: both enum sites lack the new wire string. A failed summary with `model_identity_mismatch` passes the live validator but is refused by the tracked golden. Base-vs-head fresh regeneration proves those two enum additions are specifically caused by round 2.

The binding D-012 entry at [decision_log.md:683](/Users/edr/code/JouleWise-wt-s15/docs/decision_log.md:683) and the public Structured Failure Reasons list at [adapter_contracts.md:684](/Users/edr/code/JouleWise-wt-s15/docs/contracts/adapter_contracts.md:684) also remain closed over the old vocabulary.

No frozen runtime evidence-side validator was found that would reject retained artifacts. The problem is the stale independently reviewed schema/contract surface, not a need to rewrite historical evidence.

Refutation path: regenerate and independently review the output-schema golden, amend D-012 and the adapter contract, then validate a failed summary containing the exact new string against every tracked/live schema surface.

### SHOULD-FIX F3 — E-3 calls the correct predicate with the wrong authority value

The helper imports and calls the actual production `_common_mode_window_is_strictly_noncollapsed`, performs strict numeric checks before arithmetic, and the required `nextafter(2*b, +inf)` regression genuinely refuses through `replay_common_mode_dominance`. The retained valid fixture still produces its previous result.

The remaining divergence is [generate_configs.py:671-690](/Users/edr/code/JouleWise-wt-s15/configs/campaigns/d117_contrast_v5/generate_configs.py:671): the supplied bound may differ from the authenticated bound by `1e-12`, and the supplied value is passed to the predicate.

A refuter used:

- authenticated `b = 0.036782638697819788`;
- supplied `b' = b - 5.0000281692774706e-13`;
- window end `2*b' + 2e-13`.

The predicate returns `True` with `b'` and `False` with authenticated `b`; replay nevertheless accepts and emits ratio `3.6330628731577335`.

Refutation path: after authenticating the caller value, invoke every production-domain check with `authenticated_bound`—or require exact equality—and pin this near-equal-bound counterexample.

Per-disposition verdicts:

- E-1 — **PARTIAL**
- E-2 — **PARTIAL**: all 80 generated full `_v5` configs pass privacy classification and preserve both pins, and the config-schema golden exactly matches fresh generation; the “no other golden changes” condition fails because E-5 changes the output schema.
- E-3 — **PARTIAL**
- E-4 — **INSTALLED** at the inherited `7294cb8f` ancestor; D-165’s binding text is non-contradictory.
- E-5 — **PARTIAL**
- E-6 — **INSTALLED** as the named TOCTOU limitation.
- D-1 and round-1 safeguards — **INSTALLED**. The dominance literal’s bytes are unchanged, retain all ruled component dispositions, and correctly exclude unrelated model-pin/failure-reason semantics. Generator pin refusals and the admission tool were not weakened; the admit tool is byte-unchanged.

## Residual risk

The full suite requires replay in a writable environment. No live MLX model was loaded; load ordering and the one-pin bypass were exercised with a mocked backend. The E-6 check-to-load TOCTOU remains the explicitly accepted single-operator residual.