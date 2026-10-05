```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "REVIEW: PASS - real-pin replay, drift refusals, acceptance binding and all active importer tests passed.",
  "workspace": {
    "base_requested": "a42a26fd",
    "base_mode": "exact",
    "head_start": "a42a26fde1745d73c41675ef33949824a2a9d0f6",
    "head_end": "a42a26fde1745d73c41675ef33949824a2a9d0f6",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "REVIEW: PASS",
    "findings": [],
    "diff_base": "8fa002f77db7af1e261a30e3787e38af2ab5e946"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-dd5-isfable PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B scripts/issue_g2a_prefill_prompt_pin.py --harvest /Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/harvest.json --registration configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md --output /tmp/dd5-ctreview/pin/prefill-prompt-pin.json > /tmp/dd5-ctreview/issuer.log 2>&1; result=$?; if [ $result -eq 0 ]; then echo ISSUER_PASS; else sed -E 's/[0-9]{3,}/[redacted]/g' /tmp/dd5-ctreview/issuer.log; fi; exit $result",
      "cwd": "/Users/edr/code/JouleWise-wt-dd5-isfable",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ISSUER_PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "ISSUER_PASS"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-ctreview/replay_review.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "GENERATE_HEAD exit=0",
          "GENERATE_MAIN exit=0",
          "GENERIC_AUTH PASS regenerated immutable",
          "DRIFT_OUTPUT REFUSED production bytes differ from regeneration",
          "DRIFT_BAKED_INPUT REFUSED pinned replay input drifted",
          "DRIFT_PIN_BUNDLE REFUSED pinned replay input drifted",
          "TAMPER_AND_REGENERATE REFUSED baked input SHA pin",
          "SCRATCH_PACK_RESTORED PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "SCRATCH_PACK_RESTORED PASS"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-ctreview/input_drift_all.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ALL_FIVE_BAKED_INPUT_DRIFTS REFUSED; scratch pack restored"]
      },
      "expected": {"exit_code": 0, "tail_regex": "ALL_FIVE_BAKED_INPUT_DRIFTS REFUSED"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-ctreview/rebind_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "REBIND_OLD_PLAN REFUSED generator digest differs",
          "REBIND_NEW_PLAN PASS as a different pack identity",
          "ORIGINAL_FREEZE_IDENTITY REFUSED committed pack bytes differ"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "ORIGINAL_FREEZE_IDENTITY REFUSED"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-ctreview/compare_packs.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["  \"acceptance_cutoff\": 376", "}"]
      },
      "expected": {"exit_code": 0, "tail_regex": "\"acceptance_cutoff\": 376"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/dd5-ctreview/pytest-primary tests/test_d117_contrast_v5_pack.py tests/test_arm_readiness_evidence.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["60 passed, 112 subtests passed in 248.17s (0:04:08)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "60 passed, 112 subtests passed"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/dd5-ctreview/pytest-main-primary tests/test_d117_contrast_v5_pack.py tests/test_arm_readiness_evidence.py",
      "cwd": "/tmp/dd5-ctreview/main",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["57 passed, 109 subtests passed in 177.13s (0:02:57)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "57 passed, 109 subtests passed"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/dd5-ctreview/pytest-importers tests/test_d117_floor_qwen3_v5_generate.py tests/test_issue_g2a_prefill_prompt_pin.py tests/test_d165_dominance_closeout.py tests/test_campaign_generator_core.py tests/test_arm_readiness_evidence_t0.py tests/test_analysis_inputs.py tests/test_gamma_unit_roster_guard.py tests/test_night_gate.py tests/test_dependence_sensitivity.py tests/test_generate_g2a_probe_inputs.py tests/test_summarize_g2a_prefill_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["369 passed, 5 skipped, 777 subtests passed in 1938.33s (0:32:18)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "369 passed, 5 skipped, 777 subtests passed"}
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-ctreview/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/dd5-ctreview/pytest-evidence tests/test_arm_readiness_evidence_packauth.py tests/test_arm_readiness_evidence_author.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["51 passed, 43 warnings, 28 subtests passed in 1009.57s (0:16:49)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "51 passed, 43 warnings, 28 subtests passed"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Importer tests all passed and pytest exited 0; MLX then emitted an ignored at-exit RuntimeError reporting No Metal device available. Live GPU validation was not performed.",
      "needs": ""
    }
  ]
}
```

## Findings

REVIEW: PASS — no findings.

Real-pin GAMMA passes generic authentication through regeneration. One-byte output drift and drift in each of the five carried inputs refuse. The base generator reproduces `evidence_author_pack_authentication_underivable`.

Baking does not bypass existing pins. Input hashes are enforced at `generate_configs.py:3624`; the plan tree pins the generator, checked at `arm_readiness_evidence.py:293`. Updating the input, generator hashes, and regenerated plan can authenticate **a new pack identity**. The original plan pin and freeze identity both refuse it; the complete pack digest is bound at `arm_readiness.py:5636`.

Acceptance matches `d079_calibration_acceptance_v2_n24_25g83_r2`, including artifact and derivation hashes. Cutoff remains **376**.

Both revisions generated successfully with the real pin. **110 existing files are byte-identical**, including all 80 science configs and four condition-family files. No files were removed.

- Changed: `README.md`, `decode_workload_candidate.json`, `generate_configs.py`, `plan_tree.json`, `plan_tree.sha256`.
- Added: `generator_inputs/decode_workload.json`, `generator_inputs/model_panel.json`, `prefill_pin/prefill-prompt-ladder.json`, `prefill_pin/prefill_prompt_pin.json`, `prefill_pin/selection.json`.

JSON differences are limited to the workload source path, resulting metadata hashes, generator hash, and three acceptance pins. Repository files remain untouched and the worktree is clean.

## Residual risk

Verification exercised pre-projection GAMMA authentication and fixture-based readiness tests. Production identity projection, freeze/re-attestation, and estate-12 receipt proof remain the lead’s next gate.