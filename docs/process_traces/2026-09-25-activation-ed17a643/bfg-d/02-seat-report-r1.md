```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Battery-float probe, gate, writer, and replay changes are uncommitted; test-contract rulings and two out-of-scope policy mirrors block completion.",
  "workspace": {
    "base_requested": "c6814dd8",
    "base_mode": "descendant",
    "head_start": "eb847affa6e33e8499270c5da3e8049ba73144ca",
    "head_end": "eb847affa6e33e8499270c5da3e8049ba73144ca",
    "upstream_end": "c126b0f863479db4c3682a37c39d731e7bf6ba9b",
    "branch": "feat/2026-09-25-bfg-d"
  },
  "pathspec": [
    "joulewise/battery_float.py",
    "joulewise/night_gate.py",
    "joulewise/arm_retry.py",
    "joulewise/evidence_night.py",
    "joulewise/night_agent_install.py",
    "joulewise/arm_readiness_evidence_t0.py",
    "scripts/validate_powermetrics_fiducial.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "scripts/issue_epoch_continuation.py",
    "tests/test_battery_float.py",
    "tests/test_night_gate.py",
    "tests/test_arm_retry.py",
    "tests/test_evidence_night.py",
    "tests/fixtures/battery_float/README.md",
    "tests/fixtures/battery_float/float.ioreg",
    "tests/fixtures/battery_float/charging-synthetic-from-real.ioreg",
    "tests/fixtures/battery_float/stale-synthetic-from-real.ioreg",
    "tests/fixtures/battery_float/malformed-synthetic-from-real.ioreg"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_battery_float tests.test_night_gate.NightGateTests.test_first_refusal_order_advances_one_ruled_gate_at_a_time tests.test_night_gate.NightGateTests.test_reason_code_registry_is_exactly_the_ruled_set tests.test_night_gate.NightGateTests.test_battery_float_charging_refuses_at_c3",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 0.012s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_retry.ZeroCaptureSuccessorTests.test_battery_float_zero_capture_only_and_probe_error_never_successor tests.test_battery_float",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 11 tests in 0.010s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=11)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_retry tests.test_calibration_cadence_report",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=36, errors=13)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=61, errors=5)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_evidence_night.LifecycleTests.test_canonical_fast_forwards_itself_when_nothing_is_loaded",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 1.193s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py configs/calibration/powermetrics_fiducial/protocol_v3.json scripts/night_chains configs/launchd",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V10",
      "kind": "other",
      "cmd": "git add joulewise/battery_float.py joulewise/night_gate.py joulewise/arm_retry.py joulewise/evidence_night.py joulewise/night_agent_install.py joulewise/arm_readiness_evidence_t0.py scripts/validate_powermetrics_fiducial.py scripts/issue_calibration_acceptance_generation.py scripts/issue_epoch_continuation.py tests/test_night_gate.py tests/test_arm_retry.py tests/test_evidence_night.py tests/test_battery_float.py tests/fixtures/battery_float && git commit -m 'BFG-D: add battery float observations and derivation replay' -m 'Co-Authored-By: Sol 6.0 <noreply@openai.com>'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 128, "tail": ["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-ed17a643-bfgd/index.lock': Operation not permitted"]},
      "expected": {"exit_code": 0, "tail_regex": "BFG-D:"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The required battery C3 record breaks the existing exact legacy-receipt assertion; historical issuer and continuation fixtures lack battery evidence and now refuse before their existing assertions run. The brief prohibits loosening those assertions.",
      "needs": "Rule how to preserve the legacy assertion and whether pre-directive fixture sessions receive battery evidence or an explicit historical exemption."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "calibration_cadence_report.report_window receives only LABEL=PATH; it has no authenticated ledger session to pass to validate_window.",
      "needs": "Specify the ledger/session input contract for report_window and its CLI."
    },
    {
      "id": "F3",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "arm_retry's new reason changes the generated policy block checked byte-for-byte in two documents outside WRITE_SCOPE.",
      "needs": "Expand scope prospectively for the two named policy documents."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "blocking",
      "text": "Git index metadata is outside writable roots; git add/commit failed before staging.",
      "needs": "Lead commits from a writable Git worktree or changes metadata access."
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Combined evidence-night, installer, writer, and arm-readiness suites were interrupted after early failures or slow cases; no full discovery was run as instructed.",
      "needs": "Complete focused suites after the rulings and fixture updates."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/process/NIGHT_HANDBACK.md",
      "docs/phase_2/derivation_night_runbook.md"
    ],
    "reason": "Both contain byte-exact mirrors of arm_retry.render_policy(), which now includes night_refused_battery_float.",
    "blocked_work": "Passing tests.test_arm_retry and completing the mirrored refusal-code registration.",
    "minimal_change": "Regenerate only each ARM-RETRY-POLICY v1 block."
  }
}
```

## Change

The uncommitted work adds the shared probe, parser, record, and replay validator in [battery_float.py](/Users/edr/code/JouleWise-wt-ed17a643-bfgd/joulewise/battery_float.py:17). The fixture directory contains one real ioreg capture and documented synthetic byte edits. No pinned path moved. **BFG-D is not ready to arm W1.**

| §5.3 item | Implementation | Proof |
|---|---|---|
| 1 — t0 | `joulewise/night_gate.py:1515` | `tests/test_battery_float.py:98`, `tests/test_night_gate.py:1632` pass |
| 2 — arm check | `joulewise/evidence_night.py:1364` | One existing lifecycle case passes; charging case unproved |
| 3 — publication | `joulewise/evidence_night.py:1788` | Unproved |
| 4 — installer | `joulewise/night_agent_install.py:1171` | Unproved |
| 5 — t0 power row | `joulewise/arm_readiness_evidence_t0.py:1847` | Unproved |
| 6 — writer brackets | `scripts/validate_powermetrics_fiducial.py:2231,2462,2597` | Anchor and writer regressions unproved |
| 7 — consumers | `scripts/issue_calibration_acceptance_generation.py:215,1256`; `scripts/issue_epoch_continuation.py:86` | Issuer/continuation suites fail; cadence consumer unimplemented |

| §5.5 clause | Implementation | Proof |
|---|---|---|
| Window replay and verdict | `joulewise/battery_float.py:180` | Missing, tampering, precedence, ΔQ, stale, and unused-slot tests pass at `tests/test_battery_float.py:143–167` |
| Issuer 1 — computed candidate set | `scripts/issue_calibration_acceptance_generation.py:1296` | Unproved |
| Issuer 2 — exact named set | `scripts/issue_calibration_acceptance_generation.py:1256,1327,1962` | Unproved |
| Issuer 3 — exclusion before positional checks | `scripts/issue_calibration_acceptance_generation.py:1335` | Unproved |
| Issuer 4 — A-7 exemption | `scripts/issue_calibration_acceptance_generation.py:1433` | Unproved |
| Issuer 5 — derivation notes | `scripts/issue_calibration_acceptance_generation.py:1688` | Unproved |
| Issuer 6 — dry run | `scripts/issue_calibration_acceptance_generation.py:215` | Unproved |

## Verification notes

| §5.6 test | Result |
|---|---|
| 1 — charging at both night-gate paths | Pass, `tests/test_battery_float.py:98` |
| 2 — parser defects and boundaries | Pass, `tests/test_battery_float.py:30–79` |
| 3 — arm and publication charging | Missing |
| 4 — zero-capture successor | Pass, `tests/test_arm_retry.py:490` |
| 5 — writer and pin regression | Pin check passes; writer test missing |
| 6 — issuer, dry run, cadence, tampering | Tampering passes at `tests/test_battery_float.py:152`; remaining cases missing |
| 7 — diagnostic ΔQ | Pass, `tests/test_battery_float.py:143` |
| 8 — writer exit and recovery | Missing-post validator test passes at `tests/test_battery_float.py:152`; recovery path unproved |
| 9 — anchor non-overlap | Missing |
| 10 — staleness | Pass, `tests/test_battery_float.py:112,164` |
| 11 — window-exhausted unused slot | Pass, `tests/test_battery_float.py:143` |

The existing issuer suite ended with 36 failures and 13 errors, and the continuation suite with 61 failures and 5 errors. Both primarily encounter `battery_float_evidence_missing` on historical fixtures before reaching their original assertions. The full `night_gate` suite has 11 failures, principally its exact pre-battery receipt comparison.

## Residual risk

**NEEDS_RULING:** Resolve the historical test contract and specify how `report_window(label, window)` obtains an authenticated session. The current cadence CLI accepts only `LABEL=PATH`; deriving a ledger verdict from that path alone would not meet §5.5.

**NEEDS_SCOPE:** Permit the two policy-block updates named in the envelope. Git metadata also needs a writable route before the requested commit can be made.