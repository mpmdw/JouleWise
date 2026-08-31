```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "DO-NOT-MERGE: annotation validation still accepts forged line_index provenance, and one Q5 subset-order assertion was not ported before deletion.",
  "workspace": {
    "base_requested": "a829215e236b8400ac8cd62c479a3392e4455e5d",
    "base_mode": "exact",
    "head_start": "04bc2296e266adfd67c83db72ef93804478393c1",
    "head_end": "04bc2296e266adfd67c83db72ef93804478393c1",
    "upstream_end": "bb7b29254fe1ba458b0d4009f36cc47d836692dd",
    "branch": "feat/workload-scored-v6"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "DO-NOT-MERGE",
    "coverage_port": "fail: most Q5 assertions are substantively ported, but full-record and canonical-subset-hash input-order invariance disappeared",
    "deletion": "pass: both files are absent; no executable imports, shard registrations, or live invocation pointers remain",
    "bypass_closures": {
      "forged_record_list_builder": "refused with gsm8k_source_authentication_required",
      "foreign_public_scoring": "refused with gsm8k_pinned_set_foreign",
      "public_per_item_scorer": "absent",
      "forged_line_index_validator": "accepted: blocker",
      "other_public_provenance_surface": "reviewed prompt/token hashes can still accompany foreign per-item token IDs"
    },
    "pinned_bytes": {
      "configs_diff": "unchanged",
      "canonical_subset_json_sha256": "fcfc8ab8e8ce5ba2550d156d7a3242132b5216a89c7404053dae50105249231c",
      "manifest_file_sha256": "1ad902f8ec64c737ee80f76b9b2dc6989b9e2d49ca267d5cb685b6f4c645c7f5",
      "annotations_file_sha256": "9123780834539c9bf9bf3c1a7581034018fea5a9f5e4a26a65ed30c9ed36c7e2",
      "panel_file_sha256": "78875a0e8b2c6d9f573cd42b0d27de6498cdfc8de57af4b4a502e1f93a02513a"
    },
    "cross_damage": {
      "condition_family_v2": "intact",
      "shape_dispatched_identity": "5 tests pass",
      "offline_hash_verification": "intact",
      "docs_freshness": "6 tests pass",
      "shard_discovery": "165 unique modules; tests.test_benchmark_import assigned exactly once to shard 4"
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The canonical public annotation validator accepts forged line_index provenance",
        "location": "joulewise/benchmark_import.py:837",
        "refutation": "Changing only annotations[0].line_index to 999999 on the committed sidecar still passes validate_gsm8k_annotations."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The Q5 coverage port dropped subset-content input-order invariance",
        "location": "tests/test_benchmark_import.py:181",
        "refutation": "The deleted test compared complete selected records and canonical_subset_json_sha256 across forward/reversed inputs; the surviving test compares only item IDs and their ID-only hash."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The prior reviewed prompt/token provenance gap remains",
        "location": "joulewise/benchmark_import.py:790",
        "refutation": "Replacing a committed item's prompt_token_ids with [999999], updating planned_prompt_tokens and the sidecar manifest hash, is accepted while the reviewed tokenizer/chat hashes remain unchanged."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD^ HEAD -- configs/",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_benchmark_import.BenchmarkImportTests.test_selection_refuses_duplicate_key_and_invalid_k tests.test_benchmark_import.BenchmarkImportTests.test_scorer_pins_all_four_outcomes_and_cap_semantics tests.test_benchmark_import.BenchmarkImportTests.test_scorer_refuses_hash_scorer_and_status_drift tests.test_benchmark_import.BenchmarkImportTests.test_public_scoring_surface_refuses_a_foreign_item",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 4 tests in 0.012s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 4 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs tests.test_suite.SuiteManifestTests.test_all_retained_v1_manifests_migrate_with_pinned_hashes tests.test_suite.SuiteManifestTests.test_v2_scoring_and_benchmark_import_are_exact_and_hash_validated tests.test_suite.SuiteManifestTests.test_v1_still_defers_v2_scoring_and_benchmark_import",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 8 tests in 0.016s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 8 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 0.053s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 6 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from scripts import shard_tests as s; m=s.discover_test_modules(); assert \"tests.test_benchmark_import\" in m and \"tests.test_gsm8k_import\" not in m; p=s.partition_modules(m,s.load_timing_map(),4); assert sorted(x for q in p for x in q)==sorted(m); print(\"shard_partition_complete\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["shard_partition_complete"]},
      "expected": {"exit_code": 0, "tail_regex": "shard_partition_complete"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from pathlib import Path; from joulewise.benchmark_import import validate_gsm8k_annotations; m=json.loads(Path(\"configs/suite_manifests/gsm8k_scored_v6_qwen3.json\").read_text()); s=json.loads(Path(\"configs/suite_manifests/gsm8k_scored_v6_qwen3_annotations.json\").read_text()); s[\"annotations\"][0][\"line_index\"]=999999; validate_gsm8k_annotations(m,s); print(\"FORGED_LINE_INDEX_ACCEPTED\")'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["FORGED_LINE_INDEX_ACCEPTED"]},
      "expected": {"exit_code": 1, "tail_regex": "line_index.*mismatch"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "test ! -e scripts/gsm8k_import.py && test ! -e tests/test_gsm8k_import.py && ! rg -n --glob '*.py' --glob '*.json' --glob '*.toml' --glob '*.yaml' --glob '*.yml' 'scripts\\.gsm8k_import|gsm8k_import\\.py|test_gsm8k_import|gsm8k_import' joulewise scripts tests .github configs pyproject.toml",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests 2>&1 | tail -60",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FileNotFoundError: [Errno 2] No usable temporary directory found", "Ran 2776 tests in 91.770s", "FAILED (errors=1765, skipped=114)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran .* tests.*OK"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox has no writable temporary directory; the full suite, full benchmark module, and shard test module fail on tempfile allocation.",
      "needs": "Rerun the canonical suite and shard tests in the lead's writable workspace."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Both Qwen3 mirrors are present, but Transformers is absent, so the exhaustive 16-prompt live re-tokenization test skipped.",
      "needs": "Run the mirror regression in the pinned Transformers environment."
    },
    {
      "id": "R3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Current GitHub PR checks could not be queried because network access to api.github.com is unavailable.",
      "needs": "Confirm PR #246 CI status at the lead merge gate."
    }
  ]
}
```

## Findings

**DO-NOT-MERGE.**

- **F1 — `line_index` provenance still fails open.** The builder now rejects the audit-1 forged plain-record list, but the public validator at [benchmark_import.py:837](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:837) never checks `line_index`. A committed sidecar changed only to `999999` validates successfully. The fix needs a direct validator check and a regression that mutates the sidecar itself.

- **F2 — Q5’s coverage-transfer condition is incomplete.** The deleted test asserted complete selected-record equality and equality of `canonical_subset_json_sha256` under reversed input. The surviving test at [test_benchmark_import.py:181](/Users/edr/code/JouleWise-wt-scored/tests/test_benchmark_import.py:181) checks only IDs and an ID-only hash. A mutation that preserves IDs while changing selected content would pass the new test. Because audit-1’s verdict was KEEP until unique assertions moved, deletion remains gated.

- **F4 — Prior should-fix remains.** [validate_gsm8k_annotations](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:790) accepts foreign prompt token IDs after the manifest hash is recomputed, while retaining the reviewed chat/tokenizer hashes. This reproduces audit-1’s incomplete prompt-byte/model-pin binding.

The remaining requested checks passed: the foreign public scoring path refuses, the public per-item scorer is absent, deletion/import/shard cleanup is complete, pinned config bytes are unchanged, condition-family v2 and shape-dispatched identity remain intact, and docs freshness is green.

## Residual risk

The writable full-suite/shard replay, live mirror re-tokenization, and current GitHub CI rollup remain lead-side verification gaps because of this sandbox’s tempfile, dependency, and network restrictions.
---

## Magistrate disposition (Fable, 2026-08-31, appended at custody)

F1 CURED at the bench: `validate_gsm8k_annotations` now binds `line_index` by
derivation from the manifest's `source_item_id` (`gsm8k_test_NNNN`), with the
forged-line_index regression on the committed fixtures. F2 CURED at the
bench: the input-order invariance test restored to full-record and
`canonical_subset_json_sha256` comparison. F4 (prompt_token_ids not
independently bound to the reviewed tokenizer bytes) is REGISTERED as a
PRE-COLLECTION BLOCKER for the `_v6` leg: it must close before any `_v6`
collection (weeks out, post-campaign), with the admit-tool mirror
verification as the natural closure site; tracked in WAVE-ROWS. Merge
proceeds on green CI with F4 open-and-tracked, per the D-166 sequencing
(the `_v6` leg has its own council + estate before any claim).
