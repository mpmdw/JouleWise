```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One A3 contract-fidelity blocker remains: the v2 selection expression does not encode that only small-model members gate rung selection; recommendation is DO-NOT-MERGE.",
  "workspace": {
    "base_requested": "60beae60fe9533b1d969d46e6dee012df38395fe",
    "base_mode": "exact",
    "head_start": "1388ba76df889bf49175fa12eadad5d2d5bb9190",
    "head_end": "1388ba76df889bf49175fa12eadad5d2d5bb9190",
    "upstream_end": "1388ba76df889bf49175fa12eadad5d2d5bb9190",
    "branch": "feat/v5-ladder-prep"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "DO-NOT-MERGE",
    "question_zero": "CLEAN: the complete absent/null/pin matrix agrees between typed loading and the new oneOf schema; direct ModelConfig construction refuses either one-pin state; the v2 prompt pin's tokenizer hash does not construct ModelConfig; the v5 generator requires both model-panel pins; MLX verifies the pair before mlx_lm.load.",
    "per_increment": {
      "1_fix_round_3": "PASS at final head: construction choke point, ten-member vocabulary/D-012 mapping, and authenticated R_cm bound are installed.",
      "2_bench_schema_fix": "PASS: the two-branch oneOf matches typed absent/null semantics for all nine combinations, and both schema goldens are byte-exact.",
      "3_A3_ladder": "BLOCKED by F1. The four rungs, p4096 arm, generator guard, argparse, count floor 5, reducer MIN_PHASE_SAMPLES=3 consistency, margin 2, unresolved-hash refusal, and split refusal branch are present; the selection expression is not small-model-qualified.",
      "4_controller_seam_and_adjacency": "PASS subject to the sandbox verification gap: canonical model emission restores legacy unpinned bytes, preserves both non-null pins, and the mutation test drives the real controller-to-loader path. Dynamic CI discovery includes every touched/new module."
    },
    "cross_increment": "PASS for golden byte pins, typed/schema both-or-neither, authenticated R_cm replay, and MODEL_IDENTITY_MISMATCH propagation. No active three-rung literal remains in production/v5 test surfaces; remaining occurrences are historical ruling text or explicitly superseded inherited custody excluded from test discovery.",
    "controller_metadata": "No tracked golden expects the erroneous null-pin metadata shape. The tracked d078_r01 and d117_v2_production retained model objects remain six-key and equal between config and metadata. Existing controller tests asserted only model presence/name; the new seam tests add unpinned inclusion, pinned canonical equality, and old-asdict exclusion.",
    "ci": "PASS registration: 163 test modules discovered; analysis integration, manifest v3, v5 pack, gamma-family, mint-admission, and docs-freshness modules are all discovered. New untimed modules receive the conservative unknown weight and are not skipped. docs-freshness and gen_state checks pass.",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The prefill_prompt_pin.v2 selection expression can make large-model probes gate the rung",
        "file_line": "configs/campaigns/d117_contrast_v5/generate_configs.py:81-85; tests/test_d117_contrast_v5_pack.py:34-39; docs/decision_log.md:193",
        "refutation": "Qualify the minimum explicitly over small-model G2-a members, or add a closed gating_model_role=small_model field and reference it in the expression. Add a discriminating regression where five small-model members each have count 5 while a retained large-model member has count 2: the rung must clear; changing any small-model count to 4 must make it fail."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_schemas.BenchmarkConfigTests.test_model_identity_sha256_pins_reject_incomplete_pair_on_every_construction_path tests.test_schemas.BenchmarkConfigTests.test_config_validate_and_exported_schema_semantic_parity_matrix tests.test_schemas.SummaryMetricsTests.test_failure_reason_tracked_vocabularies_and_d012_mapping_match_enum tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_common_mode_replay_last_ulp_caller_bound_does_not_govern tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 10 tests in 0.096s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from pathlib import Path; from joulewise.schemas import BenchmarkConfig,SummaryMetrics; [(print(n,\"semantic_equal\",json.loads((Path(\"tests/goldens\")/n).read_text())==v,\"byte_equal\",(Path(\"tests/goldens\")/n).read_text()==json.dumps(v,indent=2,sort_keys=True)+\"\\n\")) for n,v in ((\"config_schema.json\",BenchmarkConfig.json_schema()),(\"output_schema.json\",SummaryMetrics.json_schema()))]'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "config_schema.json semantic_equal True byte_equal True",
          "output_schema.json semantic_equal True byte_equal True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "output_schema.json semantic_equal True byte_equal True"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check \"$(git merge-base origin/main HEAD)\"..HEAD",
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
      "kind": "lint",
      "cmd": "git diff --check 60beae60..HEAD",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "docs/process_traces/2026-08-30-t28-estate11/060-diagnostic-pre-author-tests.txt:86: trailing whitespace.",
          "+test_refresh_lane_print_and_write_test_pin (tests.test_receipt_histsem.ReceiptHistsemRefreshLaneTests.test_refresh_lane_print_and_write_test_pin) ... "
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.051s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import sys; sys.path.insert(0,\"scripts\"); import shard_tests; m=shard_tests.discover_test_modules(); targets=(\"tests.test_analysis_integration\",\"tests.test_analysis_manifest_v3\",\"tests.test_d117_contrast_v5_pack\",\"tests.test_d117_gamma_d139a2_families\",\"tests.test_mint_analysis_admission\",\"tests.test_docs_freshness\"); print(\"modules\",len(m)); print(\"targets\",all(x in m for x in targets))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "modules 163",
          "targets True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "modules 163.*targets True"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2743 tests in 126.342s",
          "FAILED (errors=1757, skipped=112)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2743 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The managed read-only sandbox has no usable temporary directory; the canonical-suite errors overwhelmingly occur at tempfile.gettempdir or TemporaryDirectory before assertions run.",
      "needs": "Replay the canonical suite and mandatory adjacency modules in the normal writable bench/CI environment after fixing F1."
    },
    {
      "id": "FL2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The optional external jsonschema package is unavailable; the repository evaluator and typed loader agreed on all nine absent/null/pin states.",
      "needs": ""
    },
    {
      "id": "FL3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The exact requested two-dot range inherits one trailing-space line in an immutable diagnostic log already present on origin/main; the PR-relative merge-base diff passes git diff --check.",
      "needs": ""
    }
  ]
}
```

## Findings

### Blocker F1 — the v2 selector does not exclude large-model probes

D-166 requires every one of at least five small-model members to clear count 5, while large-model probes are recorded but non-gating. The pinned expression at `configs/campaigns/d117_contrast_v5/generate_configs.py:81-85` checks `small_model_member_count[r]`, but computes the minimum over unqualified `reducer_written_summary_metrics[r][*]`.

If that array includes the retained large-model observations, a large-model count below 5 vetoes a rung that D-166 says must clear. The test at `tests/test_d117_contrast_v5_pack.py:34-39` duplicates and locks the same ambiguous expression, so it cannot detect the semantic omission.

Refutation path: explicitly filter the minimum to small-model members and add a discriminating record with five small-model counts of 5 plus a large-model count of 2. That rung must clear; lowering one small-model count to 4 must make it fail. This is contract-bearing pre-registration semantics, so it blocks merge.

## Residual risk

The full suite and controller-to-loader mutation tests require a writable temporary directory and must be replayed after F1 is fixed. No live MLX model was loaded. Tracked retained fixtures were inspected and remain compatible; any untracked/out-of-repository unpinned bundles produced during the short pre-fix controller window were not inventoried.