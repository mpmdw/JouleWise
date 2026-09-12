```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No blocker found; both fix cuts are killed, fresh/old host probes pass, and existing expiry semantics remain effective. One optional test-precondition nit.",
  "workspace": {
    "base_requested": "100dfb2d",
    "base_mode": "exact",
    "head_start": "100dfb2d7192e2c8bb43d9bd08bf51d1e492928f",
    "head_end": "100dfb2d7192e2c8bb43d9bd08bf51d1e492928f",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "fix/2026-09-12-arm-readiness-fixture-clock-origin"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "N1",
        "severity": "nit",
        "citation": "tests/test_arm_readiness_dry_run.py:279",
        "summary": "The long-uptime scenario has no explicit precondition guard: replacing self.origin with 0 survives.",
        "recommendation": "Optionally assert that the synthetic origin exceeds the selected evidence horizon, preventing future fixture edits from silently dropping long-uptime coverage.",
        "impact": "Current regression still kills both origin-1 cuts; this does not block landing."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat ace4cc3c..HEAD -- joulewise scripts configs",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "ARMFIX_MODE=a PYTHONPATH=/tmp:$PWD PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v armfix_refuter_probe",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["joulewise.arm_readiness.ArmReadinessError: evidence item expired", "Ran 1 test in 0.893s", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=1\\)"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "ARMFIX_MODE=b PYTHONPATH=/tmp:$PWD PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v armfix_refuter_probe",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["joulewise.arm_readiness.ArmReadinessError: evidence item expired", "Ran 1 test in 0.910s", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=1\\)"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "ARMFIX_MODE=c_fresh PYTHONPATH=/tmp:$PWD PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v armfix_refuter_probe",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.934s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "ARMFIX_MODE=c_expired PYTHONPATH=/tmp:$PWD PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v armfix_refuter_probe",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["AssertionError: ArmReadinessError not raised", "Ran 1 test in 1.033s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "ARMFIX_MODE=fresh_host PYTHONPATH=/tmp:$PWD PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v armfix_refuter_probe",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 4.660s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "ARMFIX_MODE=old_host PYTHONPATH=/tmp:$PWD PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v armfix_refuter_probe",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 4.494s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_dry_run_rehearsal_root_and_id_are_single_use tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_real_under_lease_rehearsal_uses_reservation_and_both_writer_slots tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_boot_session_change_voids_verification_and_consumption tests.test_arm_readiness_lifecycle.PostSupersessionLayeringTests.test_historical_predecessor_resolves_and_still_anchors_the_chain tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 7 tests in 53.844s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v tests.test_arm_readiness_dry_run.FreezeFixtureClockOriginTests tests.test_arm_readiness_lifecycle.FreezeReplayExpiryTests tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_arm_consumes_volatile_receipts_within_short_horizon tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_mocked_forbidden_process_evidence_expires_before_arm",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 9 tests in 22.358s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git status --short",
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
      "text": "The real-boot ACID test skipped because kern.bootsessionuuid returned Operation not permitted. Six other named tests passed.",
      "needs": "Lead performs the real-boot ACID verification where sysctl is available."
    }
  ]
}
```

## Findings

**No blocker found; no should-fix found. N1 is an optional nit.**

The production fence and final cleanliness check both returned empty stdout:

```text
$ git diff --stat ace4cc3c..HEAD -- joulewise scripts configs
$ git status --short
```

No pre-existing assertion changed. The sole replaced existing line was `now_monotonic_ns=1,`, now `now_monotonic_ns=authored_at_monotonic_ns,` at `tests/test_arm_readiness_dry_run.py:180`.

Cuts were compiled and executed **in memory** through `/tmp/armfix_refuter_probe.py`; repository bytes remained unchanged:

- **V2 / a:** line 145 sampling replaced with `authored_at_monotonic_ns = 1`.
- **V3 / b:** line 180 pass-through replaced with `now_monotonic_ns=1`, retaining live sampling.
- **V4 / c_fresh:** line 279 replaced with `self.origin = 0`. Survivor; N1.
- **V5 / c_expired:** line 313 changed from origin + eight days to origin + one second.

V2–V4 each selected `FreezeFixtureClockOriginTests.test_fresh_evidence_authenticates_after_seven_days_host_uptime`; V5 selected `test_evidence_still_expires_eight_days_after_authoring`. Both fix cuts reached the actual expiry refusal at `joulewise/arm_readiness.py:6299`.

V6/V7 selected `ArmReadinessDryRunTests.test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change`, patching `time.monotonic_ns` to **1000000000000** and **800000000000000**, respectively. Both passed.

The requested `rg -n '604800000000001|valid_until|now_monotonic_ns'` across all three modules found **no `604800000000001` expectation**. Relevant existing expectations remain independent:

- `tests/test_arm_readiness_lifecycle.py:2769`: `self.deadline = 1_000`; line 2774 assigns that deadline directly. Expiry tests authenticate at `self.deadline + 1` and assert `"readiness_record_expired"`; acceptance uses `self.deadline - 1` (lines 2869–2885).
- `tests/test_arm_readiness_evidence_t0.py:2221`: `receipt["valid_until_monotonic_ns"]` must equal `1_000_000_000_000 + horizon`. This checks separately authored T0 receipts.
- T0 expiry additionally requires the refusal’s `evidence_id` to equal `"arm-t0-t0-no-stray-keepawake-v1"` (line 2368), so unrelated freeze expiry cannot satisfy it.
- Boot-change verification explicitly asserts `"prior boot session"` (lifecycle line 1020).
- Freeze digests are calculated from authored bytes, rather than a fixed golden digest (`dry_run.py:253`). T0 byte-idempotence compares before/after bytes within the same fixture (`evidence_t0.py:2274`).

V9 passed these focused expiry, deadline, and idempotence checks plus both new regressions. **No now-vacuous expiry test found.**

## Residual risk

Host-age probes patch the parent Python clock; they do not simulate a physical reboot or change subprocess clocks. The complete three-module suite was not rerun in this bounded refuter pass.