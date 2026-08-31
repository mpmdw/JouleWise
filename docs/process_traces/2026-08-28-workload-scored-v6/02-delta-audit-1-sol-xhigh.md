```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "DO-NOT-MERGE: canonical aggregate enforcement improved, but provenance, scoring, and reviewed-panel bypasses remain.",
  "workspace": {
    "base_requested": "8e0609970345078987fdb530e10982a7400539ff",
    "base_mode": "exact",
    "head_start": "dafb653af5257f1e12cddc330d8f6e3cb1c405ea",
    "head_end": "dafb653af5257f1e12cddc330d8f6e3cb1c405ea",
    "upstream_end": "bb7b29254fe1ba458b0d4009f36cc47d836692dd",
    "branch": "feat/workload-scored-v6"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "DO-NOT-MERGE",
    "q5_deletion_verdict": "KEEP",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Official provenance remains reachable through unauthenticated builder paths",
        "location": "joulewise/benchmark_import.py:737; scripts/gsm8k_import.py:423",
        "refutation": "The annotation builder accepts a plain record list and stamped the official manifest SHA while preserving a forged line_index; the still-executable deprecated builder accepted forged records and stamped the official GSM8K file SHA."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Pinned-set scoring remains bypassable through two callable scorer paths",
        "location": "joulewise/benchmark_import.py:911; scripts/gsm8k_import.py:796",
        "refutation": "The canonical public per-item helper returned correct=true for a foreign caller-defined item, while the deprecated aggregate accepted an empty sidecar and emitted pinned-set-labelled output with accuracy=null."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The panel file is genuinely loaded, but prompt bytes and model revisions are not bound",
        "location": "joulewise/benchmark_import.py:397",
        "refutation": "Pinset hash drift is refused through load_model_panel, but copied top-level hashes plus arbitrary prompt text/token IDs are accepted, and a valid 40-hex model revision drift passes _reviewed_qwen3_pins."
      }
    ],
    "pinned_bytes": {
      "configs_diff": "unchanged",
      "canonical_subset_json_sha256": "fcfc8ab8e8ce5ba2550d156d7a3242132b5216a89c7404053dae50105249231c",
      "manifest_file_sha256": "1ad902f8ec64c737ee80f76b9b2dc6989b9e2d49ca267d5cb685b6f4c645c7f5",
      "annotations_file_sha256": "9123780834539c9bf9bf3c1a7581034018fea5a9f5e4a26a65ed30c9ed36c7e2",
      "panel_file_sha256": "78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a"
    },
    "cross_damage": "No last-commit changes to condition_family.v2, shape-dispatched identity, the canonical CLI, or configs; focused identity regressions pass.",
    "merge_readiness": {
      "upstream_fresh": true,
      "shard_discovery": "tests.test_benchmark_import assigned shard 3; tests.test_gsm8k_import assigned shard 4 using the conservative unknown-module fallback",
      "pytest_style_modules": [],
      "docs_freshness": "pass"
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD^ HEAD -- configs/",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_benchmark_import.BenchmarkImportTests.test_committed_manifest_validates_and_round_trips tests.test_benchmark_import.BenchmarkImportTests.test_committed_subset_hashes_recompute_from_manifest_and_annotations tests.test_benchmark_import.BenchmarkImportTests.test_four_way_outcome_table_requires_the_exact_pinned_set tests.test_benchmark_import.BenchmarkImportTests.test_manifest_builder_refuses_unauthenticated_records",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 0.009s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 0.008s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 6 tests in 0.053s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_suite.SuiteManifestTests.test_all_retained_v1_manifests_migrate_with_pinned_hashes tests.test_suite.SuiteManifestTests.test_v2_scoring_and_benchmark_import_are_exact_and_hash_validated tests.test_suite.SuiteManifestTests.test_v1_still_defers_v2_scoring_and_benchmark_import",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.013s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check HEAD^ HEAD",
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
      "id": "V7",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests 2>&1 | tail -60",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "Ran 2783 tests in 91.115s",
          "FAILED (errors=1764, skipped=114)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran .* tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox exposes no writable temporary directory; the canonical suite's 1764 errors are temp-allocation failures.",
      "needs": "Rerun the canonical suite in the lead's writable workspace."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Both local Qwen3 mirrors exist, but Transformers is unavailable, so exhaustive live re-tokenization was not rerun.",
      "needs": "Run the mirror regression with the pinned Transformers environment."
    }
  ]
}
```

## Findings

**DO-NOT-MERGE.**

- **F1 — Provenance is not fail-closed on every builder path.** The canonical manifest builder now calls `_require_authenticated_source`, and its named `gsm8k_source_authentication_required` refusal is exercised through the real builder at [benchmark_import.py:577](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:577). But the annotation builder at [benchmark_import.py:737](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:737) still accepts an ordinary list. Supplying reconstructed selected records with forged `line_index` values produced a valid sidecar stamped with the official manifest SHA; validation never checks that line index against the authenticated source.

  Worse, the executable deprecated builder at [gsm8k_import.py:423](/Users/edr/code/JouleWise-wt-scored/scripts/gsm8k_import.py:423) still accepts fabricated records and stamps the fixed official source hash at [line 553](/Users/edr/code/JouleWise-wt-scored/scripts/gsm8k_import.py:553). Its former test module was redirected to the canonical implementation at [test_gsm8k_import.py:12](/Users/edr/code/JouleWise-wt-scored/tests/test_gsm8k_import.py:12), leaving this path untested.

- **F2 — The canonical aggregate is fixed, but scoring bypasses remain.** [score_gsm8k_outcome_table](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:957) correctly enforces k=8, the canonical subset hash, manifest/sidecar validation, exact IDs, and order. Its empty/subset/superset/foreign regressions are discriminating.

  However, the public per-item helper at [benchmark_import.py:911](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:911) accepts a caller-invented foreign item and returns `correct=true`, permitting external aggregation without the set gate. The deprecated aggregate at [gsm8k_import.py:796](/Users/edr/code/JouleWise-wt-scored/scripts/gsm8k_import.py:796) is worse: an empty response/annotation pair returns `accuracy=null` while claiming the result belongs to “this pinned set.”

- **F4 — Real loader, incomplete binding.** `_reviewed_qwen3_pins` does load `configs/model_panels/qwen3_4bit.json` through `joulewise.model_panel` at [benchmark_import.py:397](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:397). Coherent pinset drift produces the named `gsm8k_reviewed_panel_pin_drift` refusal, so the regression at [test_benchmark_import.py:366](/Users/edr/code/JouleWise-wt-scored/tests/test_benchmark_import.py:366) exercises the real loader.

  The builder nevertheless validates only caller-supplied top-level hashes at [lines 428–446](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:428), then trusts each rendered prompt and token sequence at [line 613](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:613). Copied correct hashes plus arbitrary prompt text and `[999999]` token IDs were accepted and stamped with the reviewed chat hash. Valid 40-hex model revision drift is also ignored because `_reviewed_qwen3_pins` returns only the two rendering hashes.

Q5 deletion verdict: **KEEP** for deleting the script/test pair. The script alone is **DELETE-SAFE**—there are no consumers, and deleting it closes major F1/F2 bypasses. But [test_gsm8k_import.py](/Users/edr/code/JouleWise-wt-scored/tests/test_gsm8k_import.py:163) still contains unique canonical regressions not present in `test_benchmark_import`: positive source authentication, duplicate/invalid-k selection, capped-wrong scoring, scorer/status tamper refusal, deterministic production, rendered-order refusal, sidecar tampering, and exhaustive committed-mirror token-ID checks. Migrate or retain those tests.

Pinned bytes are unchanged. F3 remains cured: HEAD descends from `origin/main`, with no upstream commits missing. The condition-family v2 either-or validator and shape-dispatched identity code were untouched; the five identity tests, including the retained-bundle before/after comparison, passed. Both new modules are `unittest`-style and shard-discovered; docs-freshness passed.

## Residual risk

The full suite needs a writable lead-controlled rerun. The failure was environmental, but it prevents a green final-suite attestation. Exact local Qwen3 re-tokenization also remains unverified because Transformers is absent.