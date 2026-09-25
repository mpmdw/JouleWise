```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Updated the W1 arm scripts for the round-3 battery, registration, frozen-plan, notice, and harvest rulings; changes remain uncommitted.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "89e4872a141542184902541eac551b6a0c5b13bf",
    "head_end": "89e4872a141542184902541eac551b6a0c5b13bf",
    "upstream_end": "7c8d1164b5b60b4fae063dcaefacdb7f4a88ebf8",
    "branch": "docs/2026-09-25-817355d2-w1arm"
  },
  "pathspec": [
    "docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/README-sequence.md",
    "docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/arm-env.zsh",
    "docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/step0-discover.zsh",
    "docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/step2-desk.zsh",
    "docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/step3-notice.zsh",
    "docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/step4-publish-install.zsh"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "for script in docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/*.zsh; do zsh -n \"$script\" || exit; done; printf 'zsh -n PASS: %s scripts\\n' \"$(find docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts -name '*.zsh' | wc -l | tr -d ' ')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["zsh -n PASS: 7 scripts"]},
      "expected": {"exit_code": 0, "tail_regex": "zsh -n PASS: 7 scripts"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -n -i 'automatic|auto-update|autoupdate|joulewise-4b' docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts; test $? -eq 1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "zsh -c 'source <(sed -e \"s/__H__/0123456789abcdef0123456789abcdef01234567/\" -e \"s/__T0__/1790467200/\" -e \"s/__PREREG__/abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789/\" docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/arm-env.zsh); for key in H T0_EPOCH_S PREREG_SHA256 WINDOW_ID NIGHT_DATE PLAN_ID SESSION_ID EVIDENCE_ROOT_ID MEASUREMENT_ROOT PY NIGHT_ROOT STAGE STAGED_PLAN PLAN CALIBRATION_PLAN FROZEN_PLAN_REL FROZEN_PLAN_SHA256 CALIBRATION_LEDGER LEDGER_HEAD_PIN ATTEMPT_DIR; do print -r -- \"$key=${(P)key}\"; done'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "H=0123456789abcdef0123456789abcdef01234567",
          "T0_EPOCH_S=1790467200",
          "PREREG_SHA256=abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
          "WINDOW_ID=w1",
          "NIGHT_DATE=20260926",
          "PLAN_ID=d079-epoch-25g83-derivation-w1-20260926",
          "SESSION_ID=d079-epoch-25g83-derivation-w1-20260926",
          "EVIDENCE_ROOT_ID=evidence-d079-epoch-25g83-derivation-w1-20260926",
          "MEASUREMENT_ROOT=/Users/edr/night-custody/measurement/JouleWise-measurement-20260926-derivation-w1",
          "PY=/Users/edr/night-custody/measurement/JouleWise-measurement-20260926-derivation-w1/.venv/bin/python",
          "NIGHT_ROOT=/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260926",
          "STAGE=/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w1-20260926",
          "STAGED_PLAN=/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w1-20260926/night_plan.json",
          "PLAN=/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260926/night_plan.json",
          "CALIBRATION_PLAN=/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260926/calibration_plan.json",
          "FROZEN_PLAN_REL=configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json",
          "FROZEN_PLAN_SHA256=9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072",
          "CALIBRATION_LEDGER=/Users/edr/night-custody/measurement/JouleWise-measurement-20260926-derivation-w1/runs/calibration_observation_ledger.jsonl",
          "LEDGER_HEAD_PIN=/Users/edr/night-custody/measurement/JouleWise-measurement-20260926-derivation-w1/configs/calibration/calibration_ledger_head.json",
          "ATTEMPT_DIR=/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w1-20260926/arm-attempts/000001"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "ATTEMPT_DIR=.*/arm-attempts/000001"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "zsh -c 'source <(sed -e \"s/__H__/0123456789abcdef0123456789abcdef01234567/\" -e \"s/__T0__/1790467200/\" -e \"s/__PREREG__/abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789/\" docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/arm-env.zsh); battery_gate'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CHECK: exactly one AppleSmartBattery object; count=1",
          "CHECK: exactly one complete top-level object; close_count=1",
          "CHECK: exactly one top-level quoted ExternalConnected; raw=['Yes']",
          "CHECK: exactly one top-level quoted IsCharging; raw=['No']",
          "CHECK: exactly one top-level quoted InstantAmperage; raw=['0']",
          "CHECK: exactly one top-level quoted UpdateTime; raw=['1790375745']",
          "CHECK: exactly one top-level quoted AppleRawCurrentCapacity; raw=['7591']",
          "CHECK: exactly one top-level quoted AppleRawMaxCapacity; raw=['7591']",
          "CHECK: exactly one top-level quoted Amperage; raw=['0']",
          "CHECK: exactly one top-level quoted Voltage; raw=['12905']",
          "CHECK: exactly one top-level quoted Temperature; raw=['3033']",
          "CHECK: exactly one top-level quoted FullyCharged; raw=['Yes']",
          "CHECK: exactly one top-level quoted CurrentCapacity; raw=['100']",
          "CHECK: InstantAmperage raw=0 signed=0 mA; unsigned64_conversion=False",
          "CHECK: UpdateTime raw=1790375745 wall_epoch_s=1790375789 age_s=44; 0 <= age <= 180",
          "BATTERY GATE PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "BATTERY GATE PASS"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check -- docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The merged BFG-D cadence CLI and amended registration are prerequisites not present in this checkout; no arm, installer, or harvest step was run.",
      "needs": "Lead verifies the cadence command and fills H, T0, and PREREG after those prerequisites land."
    }
  ]
}
```

## Change

The battery gate now checks one complete battery object, exact top-level keys, signed current and gauge freshness; it logs the additional gauge values. Desk and notice steps use the A-R5b digest placeholder and pin the frozen plan. The README now gives the ruled prerequisites, fresh-supervisor sequence and battery-float harvest route. Seat-4b instructions are removed.

## Verification notes

All seven zsh scripts passed syntax checks. The dry environment evaluation and read-only live battery gate passed. There are no standalone `.py` files in this script set to compile. The arm steps were not executed.

## Residual risk

The lead must verify the harvest command against merged BFG-D, fill the three placeholders, and perform the live arm gates.