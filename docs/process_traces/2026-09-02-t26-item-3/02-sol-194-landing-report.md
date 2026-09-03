```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed the T-0 600 s liveness predicate and defect-shaped regressions; one out-of-scope schema fixture prevents the mandated suite from being green.",
  "workspace": {
    "base_requested": "6075389a (main)",
    "base_mode": "exact",
    "head_start": "6075389a13df206205651175a7a9d52135df6fde",
    "head_end": "6075389a13df206205651175a7a9d52135df6fde",
    "upstream_end": "3e6243df8943f6a4ec152cab7ea791a8a161efea",
    "branch": "feat/2026-09-02-t26-liveness"
  },
  "pathspec": [
    "docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md",
    "joulewise/arm_readiness.py",
    "tests/test_arm_readiness.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_t0_rehearsal.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness.ClockProbePredicateLivenessTests tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_issuance_passes_t0_when_r1_batch_is_600s_minus_1ns_old tests.test_t0_rehearsal.T0RehearsalTests.test_rehearsal_t0_liveness_bound_refuses_at_600s_plus_1ns tests.test_t0_rehearsal.T0RehearsalTests.test_rehearsal_t0_liveness_bound_passes_at_600s_minus_1ns",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 7 tests in 4.609s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_evidence_author tests.test_capture_t0_step",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: False is not true",
          "Ran 221 tests in 345.998s",
          "FAILED (failures=1, skipped=7)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_integration",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 9 tests in 3.217s",
          "OK (skipped=5)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=5\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "With the new <= 600_000_000_000 conjunct temporarily deleted: python3 -m unittest tests.test_arm_readiness.ClockProbePredicateLivenessTests.test_t0_liveness_bound_refuses_at_600s_plus_1ns tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "AssertionError: True is not false",
          "AssertionError: T0EvidenceAuthoringError not raised",
          "Ran 2 tests in 3.053s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "After restoring the conjunct: python3 -m unittest tests.test_arm_readiness.ClockProbePredicateLivenessTests.test_t0_liveness_bound_refuses_at_600s_plus_1ns tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 2.337s",
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
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "5 files changed, 149 insertions(+), 5 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5 files changed, 149 insertions\\(\\+\\), 5 deletions\\(-\\)"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md",
          " M joulewise/arm_readiness.py",
          " M tests/test_arm_readiness.py",
          " M tests/test_arm_readiness_evidence_t0.py",
          " M tests/test_t0_rehearsal.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_t0_rehearsal.py"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The mandated suite's sole failure is the generic genuine-clock fixture in tests/test_arm_readiness_schemas.py: it retains valid_until_monotonic_ns=10**30, which the new upper bound correctly refuses.",
      "needs": "Resume with tests/test_arm_readiness_schemas.py added to WRITE_SCOPE."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "D-170 is absent from the requested base and current origin/main; the implementation cites it as explicitly directed.",
      "needs": "Land the authoritative D-170 entry before or with this branch."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_arm_readiness_schemas.py"
    ],
    "reason": "Its generic clock-predicate fixture must construct a deadline satisfying the newly ruled liveness relation.",
    "blocked_work": "A green replay of the mandated six-module suite.",
    "minimal_change": "For a PROBE-sourced clock.correct_and_prior_state.v1 receipt, set valid_until_monotonic_ns to r1_batch_finished_monotonic_ns + 21_600_000_000_000 before predicate evaluation."
  }
}
```

## Change

- CONFIRMED — exact `0 ≤ validity_origin − r1_finished ≤ 600 s` predicate and liveness constant: [arm_readiness.py:6349](/Users/edr/code/JouleWise-wt-t26-b/joulewise/arm_readiness.py:6349), predicate at `:6478–6485`.
- CONFIRMED — ordinary-clock identity: production binds to `time.monotonic_ns`; R1 samples it at `:1115` and publishes it at `:1199`; validity origin uses the same context clock at `:2325`, forming `valid_until` at `:2338`: [arm_readiness_evidence_t0.py:301](/Users/edr/code/JouleWise-wt-t26-b/joulewise/arm_readiness_evidence_t0.py:301). RAW remains separate.
- CONFIRMED — AST census: 12 static `_fresh_probe` call sites total, one inside the R1 batch and eleven after R1. The relevant interval therefore has eleven sites: `11 × 45 s = 495 s`; `495 + 105 = 600 s = _MIN_IDLE_NS`.
- CONFIRMED — code labels the bound a liveness/hang detector, explicitly not metrology.
- CONFIRMED — ARM controls for 600 s + 1 ns, 600 s − 1 ns, and negative age: [test_arm_readiness.py:59](/Users/edr/code/JouleWise-wt-t26-b/tests/test_arm_readiness.py:59). The negative half was already enforced by the former `valid_until − r1_finished ≥ 6 h` check.
- CONFIRMED — issuance refuses with `evidence_author_t0_predicate_refused` and passes below the boundary: [test_arm_readiness_evidence_t0.py:831](/Users/edr/code/JouleWise-wt-t26-b/tests/test_arm_readiness_evidence_t0.py:831).
- CONFIRMED — rehearsal’s real ARM predicate path mirrors both boundaries: [test_t0_rehearsal.py:562](/Users/edr/code/JouleWise-wt-t26-b/tests/test_t0_rehearsal.py:562).
- CONFIRMED — dated §6.3 disposition strikes 5 s/35 s, records D-170/ruling provenance, and states no reason-code delta: [reason-code-coverage-delta.md:1150](/Users/edr/code/JouleWise-wt-t26-b/docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:1150).
- NOT DONE — `docs/contracts/arm_readiness.md` does not exist at this base, so it was left untouched as instructed.
- NOT DONE — full green mandated suite, pending the narrowly requested fixture scope expansion.

## Verification notes

The mutation killed both required refusal tests. After restoration, both passed. The only broad-suite failure is the out-of-scope stale generic fixture described in F1.