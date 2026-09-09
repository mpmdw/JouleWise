```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One blocker: pack refusals fail main's frozen validator; all other requested mutation checks passed.",
  "workspace": {
    "base_requested": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "base_mode": "exact",
    "head_start": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "head_end": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "upstream_end": "4d72e5248953c178cbaa2fa2125bcbc034685e66",
    "branch": "int/2026-09-08-d176-seats-2-3"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "path": "joulewise/night_gate.py",
        "line": 71,
        "summary": "Expanded gate-reason registry masks refused-pack incompatibility with the frozen main validator."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest -v tests.test_launch_window.PackNightLaunchBoundaryTests.test_integrated_driver_arm_go_launcher_consumption_and_replay > /tmp/d176_exact_fixture.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.975s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/d176_delta_audit.py > /tmp/d176_delta_audit.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["AUDIT_COMPLETED; GIT_STATUS_EMPTY"]},
      "expected": {"exit_code": 0, "tail_regex": "AUDIT_COMPLETED; GIT_STATUS_EMPTY"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/d176_frozen_check.py > /tmp/d176_frozen_check.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FROZEN_RECEIPT_ACCEPTANCE_FAIL"]},
      "expected": {"exit_code": 0, "tail_regex": "FROZEN_RECEIPT_ACCEPTANCE_PASS"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest -v tests.test_arm_readiness.PackNightConsumerTests tests.test_launch_window.PackNightLaunchBoundaryTests tests.test_run_night.PackNightProducerTests > /tmp/d176_focused.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 16.186s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import subprocess; assert subprocess.check_output([\"git\", \"status\", \"--short\"]) == b\"\"; assert subprocess.check_output([\"git\", \"rev-parse\", \"HEAD\"]).decode().strip() == \"4d72e5248953c178cbaa2fa2125bcbc034685e66\"; print(\"HEAD_UNCHANGED; GIT_STATUS_EMPTY\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["HEAD_UNCHANGED; GIT_STATUS_EMPTY"]},
      "expected": {"exit_code": 0, "tail_regex": "HEAD_UNCHANGED; GIT_STATUS_EMPTY"}
    }
  ],
  "flags": []
}
```

## Findings

**F1 — blocker.** [night_gate.py:71](/Users/edr/code/JouleWise-wt-int-d176/joulewise/night_gate.py:71) adds both GO codes to `NIGHT_GATE_REASON_CODES`. [_pack_refused_receipt](/Users/edr/code/JouleWise-wt-int-d176/scripts/run_night.py:1265) consequently emits `launch_go_receipt_invalid` directly into standard pack refusals.

Executed pack-tree and higher-ARM mutations both produced `REFUSED` receipts accepted by the integrated validator but rejected by the **complete validator module loaded from main `99a42edb`**:

- `refusal.reason: is not registered`
- `refusal.reason: REFUSED verdict requires a registered gate code`

Neither produced GO. The unchanged validator function hides changed validation behavior through its expanded global registry. Restore frozen receipt compatibility, preserving the actual cause separately as required by §10.3. Re-run V3 after repair.

Independent TemporaryDirectory mutations, layered onto the integrated fixture:

| Case | Executed result |
|---|---|
| a: plan bytes after GO | **Killed:** `launch_go_receipt_invalid`, detail `plan_sha256`; reached real consumer. |
| b: pack after preparation | **Killed at GO:** `launch_go_receipt_invalid`, disk/committed bytes differ. |
| b: pack after GO | **Killed at consumption:** `launch_go_receipt_invalid`, `pack_night.pack_root.pack_sha256`. |
| c: valid higher-numbered unconsumed ARM | **Killed:** `launch_go_receipt_invalid`, `higher-numbered unconsumed receipt or re-arm this boot`. |
| d: issuance ahead / expiry behind clock | **Both killed:** `launch_go_receipt_invalid`, `monotonic_ns`. |
| e: nested production-window custody | **Killed at both predicates:** `launch_go_receipt_invalid`, `rehearsal_roots_not_disjoint`. |
| e: correctly named sibling child | **Accepted** by producer and consumer purpose/root predicates. |
| e: measurement under synthetic `~/night-custody` | **Killed at both predicates:** `launch_go_receipt_invalid`, `rehearsal_roots_not_disjoint`. |
| e: relative custody | **Killed:** `launch_go_receipt_invalid`, `custody_root`; preparation additionally names `non-absolute or symlinked`. |
| f: altered GO bytes on consumed replay | **Killed:** `launch_go_receipt_invalid`, `sha256`. |
| g: v2 replay | **Live killed:** `launch_go_receipt_missing`; historical `require_current_boot=False`: **PASS**. |
| h: second driver / repeated consumer | **Killed:** `night_record_exists` / `readiness_record_consumed`; exactly one unchanged consumption. |
| i: frozen receipt / GO absence | **Acceptance failed: F1.** GO absence passed. |

Byte comparison against main confirmed identical receipt validator/key sets, condition order/status vocabulary, driver registry, readiness registries, legacy consumption schema/key set, T-0 author, watchdog, and rehearsal G5/G7 schemas/evaluators. The gate-reason registry changed.

[Mutation evidence](/tmp/d176_delta_audit.log) · [Frozen comparison](/tmp/d176_frozen_check.log). No repository writes; final Git status asserted empty.

## Residual risk

Synthetic ARM issuance, semantic checks, and machine probes remain fixture substitutions. Rehearsal cases exercised the real root predicates. No live hardware validation or full canonical suite was performed.