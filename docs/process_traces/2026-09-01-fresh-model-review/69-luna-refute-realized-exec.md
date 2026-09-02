```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "M2 full-hash mutation survives; remaining clauses are bound or directly rejected, with filesystem-dependent verification sandbox-blocked.",
  "workspace": {
    "base_requested": "0d14893e",
    "base_mode": "exact",
    "head_start": "0d14893e738bb7c509f16faa8315ce612b03f3e6",
    "head_end": "0d14893e738bb7c509f16faa8315ce612b03f3e6",
    "upstream_end": "0d14893e738bb7c509f16faa8315ce612b03f3e6",
    "branch": "feat/2026-09-01-realized-prefill"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "M2 hash comparison is not mutation-bound",
        "text": "Case-insensitive comparison is observationally equivalent under the current lowercase validator, and first-8 comparison survives all existing tests. An in-memory probe returned [] for registered a×64 versus realized a×8+b×56. No reader test uses same-prefix/different-suffix hashes.",
        "needs": "Add a full-length hash regression using equal prefixes and differing suffixes; preserve lowercase/full-64-character enforcement."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_schemas tests.test_bundle_read tests.test_run_campaign tests.test_publication_privacy tests.test_d117_contrast_v5_pack tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "tests could not import node_client because the sandbox denied temporary-directory creation"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2801 tests in 107.994s",
          "FAILED (errors=1791, skipped=114)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "python3 -c \"import hashlib,json,sys; sys.path.insert(0,'configs/campaigns/d117_contrast_v5'); from generate_configs import dominance_criterion_registration as r; print(hashlib.sha256(json.dumps(r(),sort_keys=True,separators=(',',':')).encode()).hexdigest()[:8])\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a11"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a11$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check $(git merge-base main HEAD) HEAD",
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
      "id": "R1",
      "kind": "inspection",
      "cmd": "BundleReader.problems() on specified and second retained bundles from branch and main checkouts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "specified: branch=[] main=[]",
          "second: branch=[] main=[]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "specified: branch=\\[\\] main=\\[\\].*second: branch=\\[\\] main=\\[\\]"
      }
    },
    {
      "id": "R2",
      "kind": "inspection",
      "cmd": "Read-only retained prefill surface probe",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"all_three_present\":true,\"observed_token_count_minus_output_token_count\":4096,\"prefill_start_metadata_prompt_tokens\":[4096],\"status\":\"succeeded\",\"tokenize_end_metadata_prompt_tokens\":[4096]}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"all_three_present\":true"
      }
    },
    {
      "id": "R3",
      "kind": "inspection",
      "cmd": "BenchmarkConfig.from_mapping(config).to_dict() canonical round-trip",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "equal=true",
          "config_sha256_canonical=86bc204e9f8781289c1f0c1198af57db6de7c283cccee1bebc0e24058e2620a7",
          "roundtrip_sha256_canonical=86bc204e9f8781289c1f0c1198af57db6de7c283cccee1bebc0e24058e2620a7"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "equal=true"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "M2 full-hash integrity mutation survives the current test portfolio.",
      "needs": "Add same-prefix/different-suffix hash coverage."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "The specified scratch copy does not exist and the read-only sandbox denies creating it or temporary test directories.",
      "needs": "Rerun physical mutations and the focused suite in a writable review environment."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The literal R3 expression fails because WorkloadProfile has no to_dict method; the canonical full-config BenchmarkConfig round-trip passes byte-identically.",
      "needs": ""
    }
  ]
}
```

## Findings

F1 (blocker) is the M2 survivor.

| Mutation | Result |
|---|---|
| M1 | Fails `test_equal_counts_different_hash_names_hash_mismatch` (`<=`); dropping count fails `test_coherent_count_mutation_is_one_mismatch`. |
| M2 | **SURVIVED**. First-8 comparison accepts equal-prefix/different-suffix hashes; no current test binds this. |
| M3 | Fails `test_domain_mutation_is_mismatch`. |
| M4 | Fails `test_missing_provenance_and_marker_are_never_a_pass`. |
| M5 | Fails `test_changed_prompt_text_without_updated_hash_is_inconsistent`. |
| M6 | Fails `test_prompt_realization_reader_codes_are_unwaivable_including_any`. |
| M7 | Fails the same unwaivable-reader test; flags become empty. |
| M8 | Fails the `unknown-key` subcase of `test_prompt_token_expectation_rejects_malformed_registration`. |
| M9 | Fails `test_legacy_config_to_dict_bytes_remain_golden_identical`. |
| M10 | Fails pack candidate/family equality and raises `prompt_realization_registration_inconsistent`. |
| M11 | Fails `test_closed_pack_prompt_registration_refusals_are_defect_shaped`. |
| M12 | Covered by `test_prompt_realization_mismatch_stops_before_second_child`: `max_failures=1`, `order.log` contains only member 1, and member 2 is asserted absent. |

## Residual risk

The focused suite and physical scratch-copy mutations require a writable temporary filesystem and must be rerun by the lead. No files were modified and no commits were created.