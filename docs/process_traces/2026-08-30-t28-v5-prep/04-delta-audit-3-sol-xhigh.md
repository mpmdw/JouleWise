```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Question zero found no one-pin ModelConfig route to model load, so no cold instance is triggered; G-1 remains blocking because the exported schema mishandles explicit null, while G-2 and G-3 are installed.",
  "workspace": {
    "base_requested": "35e65a5b",
    "base_mode": "exact",
    "head_start": "3d63ad699441e3917c76f4064cbdbf341d5b9aa7",
    "head_end": "3d63ad699441e3917c76f4064cbdbf341d5b9aa7",
    "upstream_end": "3d63ad699441e3917c76f4064cbdbf341d5b9aa7",
    "branch": "feat/v5-ladder-prep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "question_zero": {
      "answer": "NO: no ordinary direct-construction, mapping/JSON loader, deserializer, copy/replace/asdict round-trip, default argument, or repository fixture can produce a one-pin ModelConfig that reaches mlx_lm.load.",
      "cold_instance": "not_triggered",
      "residual_schema_issue": "The exported schema accepts one non-null pin with an explicit-null counterpart, but every typed runtime path subsequently rejects it at ModelConfig.__post_init__."
    },
    "gates": {
      "G-1": "PARTIAL",
      "G-2": "INSTALLED",
      "G-3": "INSTALLED",
      "rounds-1-2-protections": "INSTALLED",
      "output-schema-energy-anchor-shift-envelopes": "INSTALLED"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The exported ModelConfig schema is not semantically equivalent to the construction choke point for absent/null pin states",
        "file_line": "joulewise/schemas.py:739,750,1020,1130-1145; tests/goldens/config_schema.json:447-505; tests/test_schemas.py:386-413",
        "refutation": "dependentRequired constrains key presence while each pin property remains nullable. Consequently pin+null is schema-accepted but typed-rejected, while null+absent is schema-rejected but typed-accepted; the reverse orientations behave identically. The regression tests only pin+absent. Replace dependentRequired with a value-aware constraint matching the typed absent/null/pin matrix and regress all nine combinations through the repository helper and a draft-2020-12 validator."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "git diff --check 35e65a5b..3d63ad69",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_schemas.BenchmarkConfigTests.test_model_identity_sha256_pins_reject_incomplete_pair_on_every_construction_path tests.test_schemas.SummaryMetricsTests.test_failure_reason_tracked_vocabularies_and_d012_mapping_match_enum tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_last_ulp_caller_bound_does_not_govern",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.048s",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c $'import json\\nfrom pathlib import Path\\nfrom joulewise.schemas import BenchmarkConfig, SchemaError\\nfrom tests.test_schemas import exported_config_semantics_accept\\nd=json.loads(Path(\"configs/examples/mock_local.json\").read_text())\\nd[\"model\"].update(tokenizer_json_sha256=\"a\"*64, chat_template_sha256=None)\\nprint(f\"schema_accepts={exported_config_semantics_accept(d)}\")\\ntry: BenchmarkConfig.from_mapping(d)\\nexcept SchemaError: print(\"typed_accepts=False\")\\nelse: print(\"typed_accepts=True\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "schema_accepts=True",
          "typed_accepts=False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "typed_accepts=False"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c $'import json\\nfrom pathlib import Path\\nfrom joulewise.schemas import BenchmarkConfig, SummaryMetrics\\nfor name, live in ((\"config_schema.json\",BenchmarkConfig.json_schema()),(\"output_schema.json\",SummaryMetrics.json_schema())):\\n expected=json.loads((Path(\"tests/goldens\")/name).read_text())\\n print(name, \"semantic_equal\", live==expected)\\n rendered=json.dumps(live,indent=2,sort_keys=True)+\"\\\\n\"\\n print(name, \"byte_equal\", rendered==(Path(\"tests/goldens\")/name).read_text())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "config_schema.json semantic_equal True",
          "config_schema.json byte_equal True",
          "output_schema.json semantic_equal True",
          "output_schema.json byte_equal True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "output_schema.json byte_equal True"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_ratio_predicate_and_zero_denominator_refusal tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_detects_all_must_pass_mutation tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_golden_readback_detects_threshold_mutation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.042s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2729 tests in 100.348s",
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
      "text": "The canonical suite cannot produce a clean result in the enforced read-only environment: the reported errors overwhelmingly arise because Python has no usable temporary directory, including import-time tempfile.gettempdir failures.",
      "needs": "Replay the canonical suite in the normal writable test environment."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The optional jsonschema package is unavailable, so the regression's external-validator branch was skipped; the repository schema evaluator and direct draft-2020-12 schema inspection both expose F1.",
      "needs": "Replay the nine-state absent/null/pin matrix with jsonschema available."
    }
  ]
}
```

## Question zero

**NO — no one-pin `ModelConfig` reaches model load, and the mandatory cold instance is not triggered.**

The exhaustive repository search found:

- Direct `ModelConfig(...)` construction only in the SSH fixture and the new regression. Both traverse [`__post_init__`](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:739).
- Every mapping/JSON production loader enters [`BenchmarkConfig.from_mapping`](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:983), which calls `ModelConfig.from_mapping` and then the same constructor at line 1020.
- The production `dataclasses.replace` calls copy an already-valid `BenchmarkConfig`; replacing a `ModelConfig` directly was also probed and invoked `__post_init__`.
- `asdict` only serializes. Reloads re-enter `from_mapping`; generic shallow/deep copies preserve an already-valid value.
- No pickle loader, alternate deserializer, constructor default, subclass, or direct model-config mutation path exists in repository code.
- MLX preparation receives the typed object, checks pins at [`mlx_runtime.py:85`](/Users/edr/code/JouleWise-wt-s15/joulewise/adapters/mlx_runtime.py:85), and reaches `mlx_lm.load` only at line 275.

The schema defect below cannot create a typed one-pin object: `BenchmarkConfig.from_mapping` still refuses it before adapter preparation.

## Findings

### BLOCKER F1 — `dependentRequired` is not equivalent to typed null semantics

[`schemas.py:1130`](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:1130) combines presence-based `dependentRequired` with nullable pin properties. The typed constructor instead treats missing and explicit `null` identically as `None`.

The complete absent/null/pin matrix exposes four parity failures:

- pin + null: schema accepts, typed construction rejects;
- null + pin: schema accepts, typed construction rejects;
- null + absent: schema rejects, typed construction accepts;
- absent + null: schema rejects, typed construction accepts.

The path-enumerating regression at [`test_schemas.py:386`](/Users/edr/code/JouleWise-wt-s15/tests/test_schemas.py:386) tests only pin + absent in each orientation, so its “every construction path” claim misses the explicit-null document route.

Refutation path: express the invariant in terms of values—both non-null pins or both semantically absent/null—and regress all nine matrix cells through typed loading, the repository schema evaluator, and `jsonschema`. This is a G-1 merge blocker, but not the cold-instance trigger because no invalid typed object reaches load.

Per-G verdicts:

- **G-1 — PARTIAL.** The invariant is correctly centralized once in `ModelConfig.__post_init__`, and the loader-local duplicate was removed. The exported constraint and path-enumerating test remain incomplete.
- **G-2 — INSTALLED.** The ten-member enum, both live/golden schema enum sites, adapter contract, D-012 amendment, and `STATUS_BY_REASON` agree exactly. The regression faithfully pins ten members and proves both `cleanup_failed` and `model_identity_mismatch` map to `failed`.
- **G-3 — INSTALLED.** The bracket flows through `registered_common_mode_operative_bound` to `authenticated_bound`, and that value—not the tolerated caller copy—is passed to the imported production predicate at [`generate_configs.py:689`](/Users/edr/code/JouleWise-wt-s15/configs/campaigns/d117_contrast_v5/generate_configs.py:689). The last-ULP regression calls the real helper imported from [`floor_extraction.py:362`](/Users/edr/code/JouleWise-wt-s15/joulewise/floor_extraction.py:362) and distinguishes the two bounds before asserting replay refusal.
- **Rounds 1–2 protections — INSTALLED.** Golden byte pins pass; generator pin refusals and the privacy allowlist are unchanged; typed both-or-neither validation is stronger at the choke point. Temp-dependent generator/privacy tests could not execute in this sandbox, but their implementation and test surfaces are byte-unchanged.
- **F2 `energy_anchor_shift_envelopes` golden change — CORRECT/INSTALLED.** The live emitter already contained this D-078 field at [`schemas.py:1638,1711`](/Users/edr/code/JouleWise-wt-s15/joulewise/schemas.py:1638), predating round 3. Regeneration repaired that pre-existing golden drift; round 3 did not change the emitter, and both schema goldens now match it byte-for-byte.

## Residual risk

The full suite needs replay in a writable environment. No live MLX model was loaded; reachability was established through exhaustive source tracing and constructor probes. The optional external JSON Schema validator was unavailable, though the repository evaluator directly reproduced F1.