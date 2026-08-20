```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No S1 replay-integrity blocker; v2 mint failure is unchanged S2-owned golden staleness, with r5 schema and campaign-fixture gaps remaining.",
  "workspace": {
    "base_requested": "8018a4b..1ec5dc4",
    "base_mode": "exact",
    "head_start": "8018a4b",
    "head_end": "1ec5dc4",
    "upstream_end": "1ec5dc4",
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "priority_adjudication": "No resolver or S0/S1 schema regression: the priority test produces the same closed-pinset refusal at 8018a4b and 1ec5dc4. The current generalized-v2 reds are S2-owned stale producer aggregate/component hashes.",
    "findings": [
      {
        "id": "F-S1-001",
        "severity": "should_fix",
        "title": "r5 is absent from the closed v2 pinset schema",
        "text": "schema_v2.json n17AcceptanceIds contains only r3 and r4, while runtime r5 registration and allowance resolution succeed. Any schema validation of an r5 final pinset will reject its acceptance_id."
      },
      {
        "id": "F-S1-002",
        "severity": "should_fix",
        "title": "No campaign-positive v3 production fixture",
        "text": "The generated v3 fixture strict-verifies cleanly but the actual campaign gate refuses request_ineligible with anchor_energy_envelope_exceeds_quarter_metric and environment_admission_missing. A5 positive campaign admission is therefore unproven."
      },
      {
        "id": "F-S2-001",
        "severity": "should_fix",
        "title": "13 generalized mint reds remain",
        "text": "test_mint_floor_artifact_generalized has 7 failures and 6 errors. All preempt at stale producer_set_sha256/producer_pin_sha256 checks; no S1-era admission or replay defect was observed."
      },
      {
        "id": "F-S1-003",
        "severity": "nit",
        "title": "Campaign refusal vocabulary differs",
        "text": "The retained v2 campaign fixture refuses as clock_evidence_missing, whereas claims, floors, and whole-window return capture_pipeline_superseded. S6 mandates refusal but does not explicitly mandate the shared reason at campaign gate."
      },
      {
        "id": "F-R5-001",
        "severity": "nit",
        "title": "r4-to-r5 raw diff includes issuance metadata",
        "text": "Raw JSON diff is 16 paths; after excluding acceptance identity, predecessor/reissue provenance, and derivation metadata, science-bearing diff is zero. All four estimator pin entries were recomputed; three changed and reduce.py remained identical."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_default_only_v2_output_remains_byte_identical_to_golden_oracle",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.065s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(errors=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git archive 8018a4b to a temporary checkout; run the same priority unittest",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "same MintError: artifact.pinset: explicit pinset: pinset does not match a closed final pinset schema",
          "Ran 1 test in 0.065s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "pinset does not match a closed final pinset schema"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 47 tests in 0.093s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 61 tests in 11.343s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics_fiducial",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 75 tests in 52.576s",
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
      "cmd": "python3 -m unittest tests.test_calibration_exits",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 31 tests in 344.086s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 57 tests in 141.627s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_p2038_production_path",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 225.130s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_capture_pipeline_era",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 2.343s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V10",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 131 tests in 416.633s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V11",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_mint_estimator",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 37 tests in 2.275s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests.*OK"
      }
    },
    {
      "id": "V12",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 76 tests in 16.460s",
          "FAILED (failures=7, errors=6, skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "failures=7, errors=6"
      }
    },
    {
      "id": "V13",
      "kind": "inspection",
      "cmd": "python3 - <<'PY' r5 registry, digest, pin-recompute, and normalized r4 diff harness PY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "registry_digest_match=True",
          "science_field_diff_count=0",
          "science_neutral=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "science_neutral=True"
      }
    },
    {
      "id": "V14",
      "kind": "inspection",
      "cmd": "python3 tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2_n17_r5.json",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: runs_window_a_20260722",
          "source corpus is absent from this checkout"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
      }
    },
    {
      "id": "V15",
      "kind": "smoke",
      "cmd": "python3 - <<'PY' independent A1/A4/A5/A7/S8 era probe harness PY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "crossed_strict=pass",
          "rich_telemetry_corruption=pass",
          "claims=pass",
          "floors=pass",
          "whole_window=pass",
          "fiducial_absent_anchor=refused",
          "controller_no_evidence=pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "controller_no_evidence=pass"
      }
    },
    {
      "id": "V16",
      "kind": "other",
      "cmd": "python3 - <<'PY' temporary git-archive mutation harness covering 3 CLI and 3 campaign sites PY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "cli-schema-method-pair killed=True",
          "cli-rich-telemetry-era-filter killed=True",
          "cli-v3-fallback-endpoint killed=True",
          "campaign-active-schema-gate killed=True",
          "campaign-active-method-gate killed=True",
          "campaign-active-schema-selector killed=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "killed=True"
      }
    },
    {
      "id": "V17",
      "kind": "inspection",
      "cmd": "python3 - <<'PY' compare schema_v2 n17 ids with runtime r5 registration PY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "schema_n17_ids=['d079_calibration_acceptance_v2_n17_r3', 'd079_calibration_acceptance_v2_n17_r4']",
          "r5_runtime_registered=True",
          "r5_schema_admitted=False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "r5_schema_admitted=False"
      }
    },
    {
      "id": "V18",
      "kind": "inspection",
      "cmd": "git status --short --branch; git diff --check 8018a4b..1ec5dc4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The 13 generalized mint reds are the pre-existing S2 golden/hash chain, reproduced unchanged against 8018a4b.",
      "needs": "S2 golden regeneration and delta re-audit."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The r5 corpus verifier cannot reach primary members because runs_window_a_20260722 is absent from this checkout.",
      "needs": "Run the verifier where the authenticated corpus is mounted."
    }
  ]
}
```

## Findings

- F-S1-001 — [schema_v2.json](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS1-lensEXE/scripts/floor_mint_pinsets/schema_v2.json:186) omits r5 from the closed n17 acceptance enum. Runtime r5 authentication is correct, but the declarative schema is stale.

- F-S1-002 — The v3 fixture strict-verifies but is not campaign-positive; it fails closed on fixture environment/admission evidence.

- F-S2-001 — The generalized mint suite’s 13 reds are S2-owned stale producer hashes, not an S1 resolver or replay regression. Refresh only through the independent S2 golden process.

- F-S1-003 — Campaign v2 refusal uses `clock_evidence_missing`; the shared `capture_pipeline_superseded` vocabulary is present in claims, floors, and whole-window lanes.

- F-R5-001 — r5 is science-neutral after normalizing issuance metadata: zero science-field differences and all four estimator pins match recomputed source hashes.

## Residual risk

Full r5 primary-corpus replay remains unverified because the referenced corpus directories are absent from this checkout.