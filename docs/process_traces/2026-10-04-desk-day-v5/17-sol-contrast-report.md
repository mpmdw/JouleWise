```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Replay and live-default acceptance implemented; changes uncommitted and canonical verification incomplete.",
  "workspace": {
    "base_requested": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "base_mode": "exact",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": "feat/2026-10-04-v5-contrast-replay-acceptance"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "tests/test_d117_contrast_v5_pack.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "/opt/homebrew/opt/python@3.14/bin/python3.14 -I -B /tmp/dd5-contrast/repro/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --check",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["generate_configs.py: error: the following arguments are required: --panel, --model-a, --model-b"]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "the following arguments are required: --panel, --model-a, --model-b"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-contrast python3 -B -m unittest tests.test_d117_contrast_v5_pack > /tmp/dd5-contrast/contrast-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 48 tests in 137.289s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-contrast python3 -B -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_emitted_generator_passes_generic_pack_authentication tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generic_replay_refuses_one_byte_output_and_input_drift tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_successor_acceptance_is_registry_live_default_with_issued_cutoff > /tmp/dd5-contrast/final-regressions.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 57.525s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-contrast python3 -B -m unittest tests.test_arm_readiness_evidence tests.test_arm_readiness_evidence_author tests.test_arm_readiness_evidence_packauth tests.test_arm_readiness_evidence_t0 tests.test_analysis_inputs tests.test_gamma_unit_roster_guard tests.test_issue_g2a_prefill_prompt_pin tests.test_d117_floor_qwen3_v5_generate tests.test_d165_dominance_closeout tests.test_night_gate tests.test_campaign_generator_core > /tmp/dd5-contrast/focused-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 358 tests in 2543.530s", "FAILED (failures=1, skipped=5)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-contrast python3 -B -m unittest discover -s tests > /tmp/dd5-contrast/canonical-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt", "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-contrast python3 -B configs/campaigns/d117_contrast_v5/generate_configs.py --check --no-preserve-current-frozen-bytes --panel configs/model_panels/qwen3_4bit.json --model-a qwen3-1p7b --model-b qwen3-8b --decode-workload configs/workloads/real_prompts_v1.json --prefill-length 512 --prefill-prompt-pin /tmp/dd5-contrast/repro/prefill-pin.json > /tmp/dd5-contrast/committed-check.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": []},
      "expected": {
        "exit_code": 0,
        "tail_regex": "checked D-117 gamma .*plan_sha256=.*tree_sha256="
      }
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "other",
      "cmd": "python3 -B scripts/bridge scope-check --baseline /tmp/dd5-contrast/baseline.json --expect-digest sha256:90b77c0698618bb59d93e003069111341df6812f40896e987620e9e104531e36 --scope configs/campaigns/d117_contrast_v5/generate_configs.py joulewise/arm_readiness_evidence.py tests/test_d117_contrast_v5_pack.py tests/test_arm_readiness_evidence.py 'tests/fixtures/**' tests/fixtures/custody_read_replay_allowlist.json",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 4, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ""}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Focused suite has one night-gate 100 ms timeout failure (tests/test_night_gate.py:1086), reproduced using exact base source blobs. Those sources are unchanged.",
      "needs": "Lead verify timeout behavior in its environment."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical suite interrupted after over 90 minutes at tests/test_battery_float.py:1882: 1070 progress markers (1055 passes, 4 failures, 11 skips), no final unittest summary. Four failures followed campaign identity refusals; this sandbox returns UNKNOWN for its own process identity (joulewise/measurement_liveness.py:110).",
      "needs": "Lead complete canonical suite with process identity access."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git staging rejected external worktree index.lock creation (Operation not permitted). Changes are uncommitted; no push.",
      "needs": "Lead review and commit the two-file diff."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Scope checker reported ATTRIBUTION_INDETERMINATE/no_governing_lease; both modified paths were in_scope, baseline was clean, and HEAD stayed unchanged.",
      "needs": "Lead perform lease-backed attribution audit."
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Committed generated contrast target is absent at this base; --check reports missing inventory. No committed pack root was generated or modified.",
      "needs": "Lead generate and authenticate the prospective pack with its issued pin before freeze."
    }
  ]
}
```

## Change

Fixed generator emission, keeping **one generic authentication path**. The emitted generator bakes model IDs, prefill length, pack-relative input paths, and SHA-256 pins; it carries byte-exact panel, workload, and prefill bundle copies. It exposes the same preservation boolean used by the floors. Authentication regenerates outputs and refuses one-byte output or input drift. `arm_readiness_evidence.py` and its historical allowlist remain unchanged.

The acceptance binding matches the registry entry at `joulewise/calibration_bracketing.py:219`, selected as live default at line 231:

- ID: `d079_calibration_acceptance_v2_n24_25g83_r2`
- Artifact SHA-256: `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`
- Derivation SHA-256: `10965d36527c73217154efdbd75ab923412685f3e79526bd31f33e6f9142e5c0`

The issued cutoff remains **376**, never live ledger head 402.

Prospective pack inventory, generator/pack hashes, and acceptance fields change. Freeze schemas/rules, receipt schemas/cadence, and histsem pinsets are unchanged. Future freezes and receipts must bind the new pack bytes; historical artifacts were preserved.

**Uncommitted**: staging failed because the sandbox cannot create the external worktree Git index lock. Nothing was pushed.

## Verification notes

Before edits, generic authentication refused with code `evidence_author_pack_authentication_underivable`: the flagless generator digest was outside the closed historical allowlist. Direct isolated replay also reproduced the missing-arguments refusal shown in V1.

The focused run’s sole failure expects child output within 100 ms; it reproduced against exact base sources. Canonical verification remains incomplete after interruption.

No committed generated contrast target exists at this base, so `--check` reported missing inventory. Scratch comparison against the original generated pack found:

- Changed: `README.md`, `decode_workload_candidate.json`, `generate_configs.py`, `plan_tree.json`, `plan_tree.sha256`.
- Added: two `generator_inputs` JSON files and three `prefill_pin` bundle files.
- **110 existing files byte-identical**, no removals.

## Residual risk

Both floor generators still bind n17_r6 at `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:202` and `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py:202`; both retain fixed prefill length 512 at line 78. They were left untouched for the other seat.

Next: lead reviews and commits the two-file diff, completes canonical verification, then generates and authenticates the prospective contrast pack using its issued pin before freeze.