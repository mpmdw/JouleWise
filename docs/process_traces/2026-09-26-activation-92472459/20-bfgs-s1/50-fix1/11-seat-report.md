```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented fix-round amendments 36, 37, and 39–43; V1 and V2 are green, and V3 has no class C failures.",
  "workspace": {
    "base_requested": "24b79db349706c9945ce42789b1be862a4400edc",
    "base_mode": "exact",
    "head_start": "24b79db349706c9945ce42789b1be862a4400edc",
    "head_end": "24b79db349706c9945ce42789b1be862a4400edc",
    "upstream_end": "24b79db349706c9945ce42789b1be862a4400edc",
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [
    "joulewise/bundle_read.py",
    "scripts/build_battery_float_historical_bundles.py",
    "configs/battery_float/historical_bundles.json",
    "tests/test_controller.py",
    "tests/test_bundle_read.py",
    "tests/test_bfgs_window_consumers.py",
    "tests/test_battery_float_consumers.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_controller tests.test_bundle_read tests.test_reduce tests.test_revision_five_b_readers tests.test_bfgs_publication_privacy tests.test_bfgs_window_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".............................................................................................................................................................................................................................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 333 tests in 434.908s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...........................................................................................................................................................................................................................................................................................................................",
          "----------------------------------------------------------------------",
          "Ran 315 tests in 534.259s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_integration tests.test_audit_amplification tests.test_audit_bundle_validation tests.test_authentication_io tests.test_axi_controller_events tests.test_axi_mock_spec tests.test_axi_request_validation tests.test_cli tests.test_cli_run tests.test_corpus_strict_validation tests.test_determinism_gate tests.test_envelope_gate tests.test_experiment tests.test_floor_extraction tests.test_gate_sensibility_rounding tests.test_idle_dependence tests.test_mint_floor_artifact_generalized tests.test_nvidia_node_integration tests.test_p2038_production_path tests.test_package_bundle_pack tests.test_paper_reported_energy tests.test_partial_record_enclosure tests.test_phase_share tests.test_powermetrics tests.test_report tests.test_rpt001_report_slice tests.test_schemas tests.test_whole_window_selection tests.test_window_duration_margins",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 1052 tests in 437.842s",
          "",
          "FAILED (failures=49, errors=37, skipped=16)",
          "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "Ran [0-9]+ tests in .*s"
      }
    },
    {
      "id": "B1",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["forward check: byte-identical entries=69"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
    },
    {
      "id": "B2",
      "kind": "build",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["forward check: byte-identical entries=69"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "forward check: byte-identical entries=69"
      }
    },
    {
      "id": "W1",
      "kind": "inspection",
      "cmd": "python3 scripts/build_battery_float_historical_bundles.py --check --witness /Users/edr/code/JouleWise/runs*",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "witness_count included complete df-ph-decode-floor-mint1.json 50",
          "witness_count listed complete docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md 12",
          "witness_count listed complete docs/process_traces/2026-08-07-plan-factory/DRAFT-NEVERZERO.md 51",
          "witness_count listed complete docs/process_traces/2026-08-08-attribution-debate/COMMONMODE-REPLAY.md 40",
          "witness_count listed tree analysis/rpt001-v2/artifact_manifest.json 6",
          "witness_count included tree analysis/rpt001-v2/input_manifest.json 6",
          "witness_count listed tree docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md 3",
          "witness_count listed tree docs/legacy/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md 3",
          "witness_count listed tree docs/process_traces/2026-08-07-plan-factory/DRAFT-QUANT_GATES.md 6"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "witness_count included tree analysis/rpt001-v2/input_manifest.json 6"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The fifty 7B runs pinned only by six file hashes remain prospective under the erratum.",
      "needs": "Historical-battery lane ruling."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "V3 has 13 class A, 68 class B, zero class C, and five class D cases reserved for later ruled work or base/environment follow-up.",
      "needs": "Run round 2 and round F in the ruled order."
    }
  ]
}
```

## Change

| Amendment | Files and functions | Test rows; RED counterfactual → GREEN |
|---|---|---|
| 36 | Exact controller replace-call rows in [the guard](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_battery_float_consumers.py) | At `24b79db3`, both guard tests failed on four controller sites. A path-wide exemption made the new forged-verdict self-test RED. The exact rows, type test, provenance test, and forgery self-test are GREEN; V2 is GREEN. |
| 37 | [BundleReader](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/bundle_read.py) config binding and refusal labels | Head returned bare config errors or `invalid record` for the ruled cases. New missing-config and changed-digest rows, the rewritten SF-6 expectation, and the tightened prefix row are GREEN. |
| 39 | `HistoricalBundleSet`, tree digest, and reader admission | Head refused a retained RPT001 run as `prospective bundle`. Tree admission, mutation refusal, digest equivalence, invalid identity, and duplicate-entry tests are GREEN. The unedited RPT001 full-route test passes. |
| 40 | [Builder](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/build_battery_float_historical_bundles.py), [historical set](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/configs/battery_float/historical_bundles.json), reader pin | Head held 13 entries and lacked `c2851728…86bf`. Source-count, unnamed-source, forward-byte, and reverse-witness checks are GREEN. |
| 41 | Builder classification of `PINNED_BUNDLE_SHA256` | Head treated the pin as an unresolved candidate. The builder now lists it as `file_digest`; hashing the named `power_trace.csv` gives `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`. |
| 42 | Typed reader refusal and window gate | At head, two prospective members produced `CustodyUnreadable` naming only the first; deleted raw evidence had no member label. Both status rows and the custody label, note, traceback, and original-failure-list rows are GREEN. |
| 43 | Existing controller span stage; new [controller tests](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_controller.py) | Base `1417c0c4` wrote zero sentinel events for the non-provider wall-meter run; the ruled test requires two. Current wall-meter span, removed-marker refusal, and MOCK no-marker rows are GREEN. |

The rebuilt set has **69 entries**: 13 complete digests from tracked fixture bundles, 50 complete digests from `df-ph-decode-floor-mint1.json`, and 6 tree digests sourced from `analysis/rpt001-v2/input_manifest.json`. Its new `HISTORICAL_BUNDLE_SET_SHA256` is `207a3d40730500e5f83b5885720be1c7e5f42beb4a5245f99614d491c871c18a`.

## Verification notes

The two forward checks printed, verbatim:

```text
forward check: byte-identical entries=69
forward check: byte-identical entries=69
```

Their complete stdout files were byte-identical, as were their complete stderr files. The reverse witness printed `witness bundles=1402`; its source-by-source counts are in W1 above. **Both checks’ full stdout and stderr, every reverse-witness hit, and the RED/GREEN logs are pasted verbatim** in the [verification transcript](/private/tmp/bfgs-s1-fix-verbatim-report.md). The [fresh V3 failure index](/private/tmp/bfgs-v3-failure-index-fresh.txt) classifies every case: **A 13, B 68, C 0, D 5**. There is no class C text to report.

The builder lists these excluded populations by name or source:

- `PINNED_BUNDLE_SHA256` (`69451609…d3e06e9`): a file digest; its containing bundle enters through the floor artifact’s `c2851728…86bf` citation.
- The twelve retired tree citations in `analysis/rpt001-v1/input_manifest.json` and `analysis/rpt001-v1/artifact_manifest.json`; the duplicate six v2 artifact-manifest citations are listed, with `input_manifest.json` retained as their source.
- The 100 runs in `docs/process_traces/2026-08-09-prefill-phase-proof/results.json`, identified there by six file hashes each. Fifty enter through the floor artifact. The other fifty 7B runs remain prospective:

```text
sw7bfloor-df-cmp-abba-ph-decode-b01-a1, sw7bfloor-df-cmp-abba-ph-decode-b01-a2, sw7bfloor-df-cmp-abba-ph-decode-b01-b1, sw7bfloor-df-cmp-abba-ph-decode-b01-b2
sw7bfloor-df-cmp-abba-ph-decode-b02-a1, sw7bfloor-df-cmp-abba-ph-decode-b02-a2, sw7bfloor-df-cmp-abba-ph-decode-b02-b1, sw7bfloor-df-cmp-abba-ph-decode-b02-b2
sw7bfloor-df-cmp-abba-ph-decode-b03-a1, sw7bfloor-df-cmp-abba-ph-decode-b03-a2, sw7bfloor-df-cmp-abba-ph-decode-b03-b1, sw7bfloor-df-cmp-abba-ph-decode-b03-b2
sw7bfloor-df-cmp-abba-ph-decode-b04-a1, sw7bfloor-df-cmp-abba-ph-decode-b04-a2, sw7bfloor-df-cmp-abba-ph-decode-b04-b1, sw7bfloor-df-cmp-abba-ph-decode-b04-b2
sw7bfloor-df-cmp-abba-ph-decode-b05-a1, sw7bfloor-df-cmp-abba-ph-decode-b05-a2, sw7bfloor-df-cmp-abba-ph-decode-b05-b1, sw7bfloor-df-cmp-abba-ph-decode-b05-b2
sw7bfloor-df-cmp-abba-ph-decode-b06-a1, sw7bfloor-df-cmp-abba-ph-decode-b06-a2, sw7bfloor-df-cmp-abba-ph-decode-b06-b1, sw7bfloor-df-cmp-abba-ph-decode-b06-b2
sw7bfloor-df-cmp-abba-ph-decode-b07-a1, sw7bfloor-df-cmp-abba-ph-decode-b07-a2, sw7bfloor-df-cmp-abba-ph-decode-b07-b1, sw7bfloor-df-cmp-abba-ph-decode-b07-b2
sw7bfloor-df-cmp-abba-ph-decode-b08-a1, sw7bfloor-df-cmp-abba-ph-decode-b08-a2, sw7bfloor-df-cmp-abba-ph-decode-b08-b1, sw7bfloor-df-cmp-abba-ph-decode-b08-b2
sw7bfloor-df-cmp-abba-ph-decode-b09-a1, sw7bfloor-df-cmp-abba-ph-decode-b09-a2, sw7bfloor-df-cmp-abba-ph-decode-b09-b1, sw7bfloor-df-cmp-abba-ph-decode-b09-b2
sw7bfloor-df-cmp-abba-ph-decode-b10-a1, sw7bfloor-df-cmp-abba-ph-decode-b10-a2, sw7bfloor-df-cmp-abba-ph-decode-b10-b1, sw7bfloor-df-cmp-abba-ph-decode-b10-b2
sw7bfloor-df-ph-decode-abs-r01, sw7bfloor-df-ph-decode-abs-r02, sw7bfloor-df-ph-decode-abs-r03, sw7bfloor-df-ph-decode-abs-r04
sw7bfloor-df-ph-decode-abs-r05, sw7bfloor-df-ph-decode-abs-r06, sw7bfloor-df-ph-decode-abs-r07, sw7bfloor-df-ph-decode-abs-r08
sw7bfloor-df-ph-decode-abs-r09, sw7bfloor-df-ph-decode-abs-r10
```

## Residual risk

V3’s A and B cases remain for the later ruled fixture work. Its four base-failing AXI cases and one stale paper supply-map receipt are class D. The fifty named 7B runs remain refused pending a historical-battery cold gate. No commit, push, full-suite run, or out-of-scope repository edit was made.