```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented deterministic module-atomic LPT sharding, invariant tests, bundled timing data, and the blocking Python-by-shard CI matrix.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "13745c47fe5ca5f3acc3d19b6bc8df0b9e6aab4b",
    "head_end": "13745c47fe5ca5f3acc3d19b6bc8df0b9e6aab4b",
    "upstream_end": null,
    "branch": "impl/test-speed"
  },
  "pathspec": [
    ".github/workflows/ci.yml",
    "scripts/shard_tests.py",
    "scripts/test_timings.json",
    "tests/test_shard_tests.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V0",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "KeyError: 'clock_anchor_bound_s'",
          "Ran 2436 tests in 558.484s",
          "FAILED (errors=1, skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2436 tests.*OK"
      }
    },
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 scripts/shard_tests.py --shards 4 --index 1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SHARD SUMMARY index=1/4 modules=1 tests=203 failures=0 errors=0 skipped=0 result=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SHARD SUMMARY index=1/4 .* result=PASS"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 scripts/shard_tests.py --shards 4 --index 2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SHARD SUMMARY index=2/4 modules=28 tests=552 failures=0 errors=0 skipped=45 result=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SHARD SUMMARY index=2/4 .* result=PASS"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 scripts/shard_tests.py --shards 4 --index 3",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SHARD SUMMARY index=3/4 modules=33 tests=985 failures=0 errors=0 skipped=14 result=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SHARD SUMMARY index=3/4 .* result=PASS"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 scripts/shard_tests.py --shards 4 --index 4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SHARD SUMMARY index=4/4 modules=32 tests=700 failures=0 errors=0 skipped=26 result=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SHARD SUMMARY index=4/4 .* result=PASS"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_shard_tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 0.159s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c \"from scripts import shard_tests as s; from tests.test_shard_tests import _unittest_discover_module_set as d; m=s.discover_test_modules(); p=s.partition_modules(m,s.load_timing_map(),4); f=sum((list(x) for x in p),[]); u=set(f); e=d(); print(f'discover={len(e)} partitioned={len(f)} unique={len(u)}'); print('missing=',sorted(e-u)); print('extra=',sorted(u-e)); print('duplicates=',sorted(x for x in u if f.count(x)>1))\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "discover=94 partitioned=94 unique=94",
          "missing= []",
          "extra= []",
          "duplicates= []"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "missing= \\[\\].*extra= \\[\\].*duplicates= \\[\\]"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 scripts/shard_tests.py --workers 4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "WORKERS SUMMARY shards=4 modules=94 tests=2440 failures=0 errors=0 skipped=85 failed_shards=none result=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "WORKERS SUMMARY shards=4 modules=94 tests=2440 .* result=PASS"
      }
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2440 tests in 563.822s",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2440 tests.*OK \\(skipped=85\\)"
      }
    },
    {
      "id": "V9",
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py --check",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The pre-change 2436-test serial baseline transiently failed in test_p2038_production_path with missing clock_anchor_bound_s; the exact test passed alone, every shard passed, and the final 2440-test serial rerun passed.",
      "needs": "Watch supported-version CI for recurrence; investigate cross-module state only if it repeats."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Local verification used Python 3.13.1; the CI matrix targets Python 3.11 and 3.14, neither installed locally.",
      "needs": "Confirm all eight GitHub Actions matrix cells and any branch-protection check-name impact."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The source design calls the advisory PR-fast/full tier Lever 2, while the named Phase 1 deliverable specifies only the blocking full-suite shard matrix. The named deliverable was followed; no test-fast job was added.",
      "needs": "Confirm the advisory fast tier remains deferred."
    }
  ]
}
```

## Change

The runner discovers current unittest modules, applies deterministic LPT packing, gives unknown modules the timing-map median, and executes each shard module-atomically in one process. `--workers N` launches all N shard processes concurrently and aggregates their counts and exit status.

The timing map contains all 93 measurements from 2026-08-03, rounded to milliseconds. The new invariant-test module is intentionally unknown and receives the 0.623s median fallback.

N=4 assignment (`tests.` prefix omitted):

- Shard 1 — 181.757s: `test_run_campaign`
- Shard 2 — 171.365s: `test_2k_amplification`, `test_aggregate`, `test_audit_bundle_validation`, `test_audit_cli_examples`, `test_audit_powermetrics_parser`, `test_audit_report`, `test_axi_burst_reduce`, `test_axi_mock_spec`, `test_axi_output_identity`, `test_axi_schemas`, `test_bundle_read`, `test_claims_index_lint`, `test_doctor`, `test_env_locks`, `test_gen_state`, `test_generate_matrix`, `test_idle_dependence`, `test_interfaces`, `test_microdelta_generate_configs`, `test_mint_floor_artifact`, `test_mlx_runtime`, `test_mock_adapters`, `test_p2038_production_path`, `test_pack_capsule`, `test_package_bundle_pack`, `test_rpt002_related_work`, `test_shard_tests`, `test_uncertainty_evidence`
- Shard 3 — 171.235s: `test_analysis_integration`, `test_analysis_ratio_integration`, `test_audit_clock`, `test_audit_reduce_degenerate`, `test_axi_analysis_manifest`, `test_axi_controller_events`, `test_axi_request_validation`, `test_axi_sb_spike`, `test_axi_sc_spike`, `test_bundle`, `test_claims_lint`, `test_claude_bridge_mcp`, `test_codex_bridge_observer`, `test_controller`, `test_d078_reason_registry`, `test_environment`, `test_floor_extraction`, `test_gensuite`, `test_idle_admission`, `test_kv_size`, `test_node_client`, `test_node_worker_subprocess`, `test_powermetrics`, `test_reduce`, `test_report`, `test_rpt001_report_slice`, `test_salvage_dangler`, `test_schemas`, `test_suite`, `test_uncertainty_p2029`, `test_vllm_runtime`, `test_whole_window_selection`, `test_workloads`
- Shard 4 — 171.231s: `test_adapters_powermetrics`, `test_analysis_claims`, `test_analysis_engine`, `test_analysis_manifest`, `test_analysis_manifest_v3`, `test_analysis_multiplicity`, `test_audit_amplification`, `test_audit_schema_edges`, `test_bridge`, `test_build_site_parsers`, `test_calibration_bracketing`, `test_cli`, `test_cli_run`, `test_clock`, `test_codex_app_bridge`, `test_corpus_strict_validation`, `test_detection_floor`, `test_determinism_gate`, `test_docs_freshness`, `test_envelope_gate`, `test_experiment`, `test_load_transition_alignment`, `test_mint_floor_artifact_generalized`, `test_node_worker`, `test_nvidia_node_integration`, `test_nvidia_smi`, `test_powermetrics_fiducial`, `test_publication_privacy`, `test_sealed_bundle_compatibility`, `test_ssh_transport`, `test_suite_control_parity`, `test_whole_window`

The existing test job is now Python `[3.11, 3.14]` × shard `[1,2,3,4]`. Fetch depth, state checking, compilation, CLI smoke, strict mock flow, and all other jobs remain unchanged.

## Verification notes

The explicit invariant proof is complete: 94 discovered modules, 94 partitioned entries, 94 unique entries, with empty missing, extra, and duplicate sets. The four shard counts sum to 2,440, exactly matching the final plain-discovery count, and both execution modes passed with 85 skips.

No existing test module was edited or deleted. No class-level splitting was introduced.

## Residual risk

Module-atomic sharding remains capped by `test_run_campaign` at an estimated 181.757s. Class splitting is correctly deferred to Phase 2.

The lead should verify the eight-cell Actions matrix and confirm branch protection recognizes the resulting matrix check names.