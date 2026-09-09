```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Completed seat-4 implementation; all 302 named acceptance tests and git diff --check passed. No commit.",
  "workspace": {
    "base_requested": "07681e95",
    "base_mode": "descendant",
    "head_start": "e73e5439e0c10a13577ff51d0e5a3f39ec070f8a",
    "head_end": "e73e5439e0c10a13577ff51d0e5a3f39ec070f8a",
    "upstream_end": null,
    "branch": "feat/2026-09-08-d176-seat4-rehearsal"
  },
  "pathspec": [
    "scripts/run_night.py",
    "joulewise/t0_rehearsal.py",
    "scripts/launch_window.py",
    "joulewise/arm_readiness.py",
    "scripts/rehearse_t0_unattended.py",
    "tests/test_run_night.py",
    "tests/test_t0_rehearsal.py",
    "tests/test_launch_window.py",
    "tests/test_rehearse_t0_unattended.py",
    "tests/test_arm_readiness.py",
    "docs/contracts/pack_night_go_receipt.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_arm_readiness tests.test_rehearse_t0_unattended tests.test_docs_freshness > /tmp/d176-seat4-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check > /tmp/d176-seat4-diff-check.log 2>&1",
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
  "flags": []
}
```

## Change

| Clause | Implementation and regression |
|---|---|
| B4; §10.5 items 1–6 | Consumer-owned admission precedes ARM access. G7 producer exercises both real launcher presentations, writes create-once 0600 evidence, and preserves completed-night bytes. Pinned by `test_g7_control_refuses_both_presentations_before_missing_arm`. |
| S1/S4 | Authenticated ARM window checks preserved; producer 2×2 and four consumer purpose/root cases pinned by `test_go_producer_enforces_two_by_two_purpose_window_table` and `test_four_case_purpose_root_table_through_consumer`. |
| G5/F6 | Current GO schema replays ARM semantics and consumption evidence to recompute C1–C5. `PackGoReplayTests` covers authorization, ARM/T0, census, expiry, consumption and re-arm refusals. D-149 is refused. |
| N1 | Numeric types, condition order, duplicates, vocabulary and basis mutations are refused by `test_g5_numeric_types_condition_order_and_vocabulary_are_exact`. |
| §10.5 items 7–8 | Exact G7 schema and authenticated bundle locator implemented; acceptance rechecks bytes, PASS conditions and presented-source digests. |
| §7.1/§9 | Ownership and clause-to-test pins updated. Census-cure implementation bytes and §10.4 preserved exactly. |

Exact G7 JSON produced by the acceptance regression, retained in the [acceptance log](/tmp/d176-seat4-acceptance.log):

    {"absence": {"chain_started_absent": true, "checked_monotonic_ns": 341235146249958, "consumption_absent": true}, "control_custody_root": "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpmddhwwhd/home/night-custody/rehearsal-t0-unattended-g7-fixture-g7-control", "control_plan_sha256": "38afe4b16a229070be780cf1aa3be809ad315150a929a869eb60a85ee527c80f", "presented": [{"first_refusal": true, "kind": "rehearsal_receipt", "path": "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpmddhwwhd/home/night-custody/rehearsal-t0-unattended-g7-fixture-g7-control/night/presented_rehearsal_receipt.json", "presented_monotonic_ns": 341235144251041, "refusal": {"detail": "receipt_class", "reason": "launch_go_receipt_invalid"}, "sha256": "fc8957322e014b57f1ba56517d7c8cf3f06827cc68885c69bdf1be83057fd8bb"}, {"first_refusal": true, "kind": "rehearsal_go", "path": "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpmddhwwhd/home/night-custody/rehearsal-t0-unattended-g7-fixture-g7-control/night/presented_go_receipt.json", "presented_monotonic_ns": 341235145247583, "refusal": {"detail": "rehearsal_purpose_on_production_id", "reason": "launch_go_receipt_invalid"}, "sha256": "8c1617894d33c694a4571011069b9b05fa0a7e2dc0623e781fb63a9769a58444"}], "rehearsal_window_id": "rehearsal-t0-unattended-g7-fixture", "schema_version": "joulewise.pack_night_g7_control.v1", "verdict": "PASS"}

## Verification notes

Historical D-149-only fixtures now intentionally fail G5; current GO acceptance has separate replay tests. G5 uses recorded consumption time while explicitly replaying ARM semantics.

## Residual risk

Live qualification remains unverified. Next: lead final diff review, then the clean-session live rehearsal.