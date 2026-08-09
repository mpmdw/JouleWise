```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT-CLOSED: the preservation gate accepts a post-process fingerprint when its independently recorded ordering token predates process start.",
  "workspace": {
    "base_requested": "bc01908",
    "base_mode": "exact",
    "head_start": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "head_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "upstream_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "branch": "impl/d117-ledger-recovery"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NOT-CLOSED",
    "findings": [
      {
        "id": "G3-1",
        "severity": "blocker",
        "title": "Fingerprint capture is not bound to its claimed pre-process ordering",
        "site": "tests/test_calibration_exits.py:94,98,504",
        "scenario": "In a temporary copy, PreservationGuard.begin retained only before_order while the actual before_fingerprint was deferred to finish after the public process. Combined with the mandated resume-finalize mutation that overwrote manifest.json before emitting calibration_finalization_binding_conflict, test_every_hard_stop_has_pre_handler_preservation_evidence still passed: Ran 1 test in 46.202s, OK."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_every_hard_stop_has_pre_handler_preservation_evidence",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 70.346s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_every_hard_stop_has_pre_handler_preservation_evidence",
      "cwd": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/joulewise-g3.iIQTyZ/repo",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "calibration_finalization_binding_conflict changed durable fingerprint inside refusal handler",
          "Ran 1 test in 44.298s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "calibration_finalization_binding_conflict changed durable fingerprint.*FAILED"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_every_hard_stop_has_pre_handler_preservation_evidence",
      "cwd": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/joulewise-g3-excluded.rVer0t/repo",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Items in the second set but not the first:",
          "RefusalCode.FINALIZATION_BINDING_CONFLICT",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FINALIZATION_BINDING_CONFLICT.*FAILED"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_every_hard_stop_has_pre_handler_preservation_evidence",
      "cwd": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/joulewise-g3-late.vy0Yz6/repo",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 141 not less than 139",
          "Ran 1 test in 47.886s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "not less than.*FAILED"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_every_hard_stop_has_pre_handler_preservation_evidence",
      "cwd": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/joulewise-g3-late-proof.2kemQc/repo",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 46.202s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "python3 -c 'from joulewise.calibration_exits import RefusalCode; from tests.test_calibration_exits import PublicGovernedExitWitnessTests, _PRESERVATION_EVIDENCE; codes={RefusalCode.FINALIZATION_BINDING_CONFLICT, RefusalCode.CUSTODY_UNREADABLE}; executed=PublicGovernedExitWitnessTests.execute_cases(codes); print(\"executed=\" + \",\".join(sorted(code.value for code in executed))); print(\"observed=\" + \",\".join(sorted(_PRESERVATION_EVIDENCE[code].observed_code for code in codes)))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "executed=calibration_custody_unreadable,calibration_finalization_binding_conflict",
          "observed=calibration_custody_unreadable,calibration_finalization_binding_conflict"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "observed=calibration_custody_unreadable,calibration_finalization_binding_conflict"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_low_level_finalization_binding_guard_supplements_writer_witness && git diff --check bc01908..4495609 && git status --short --branch && git rev-parse HEAD && git rev-parse @{upstream}",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.293s",
          "OK",
          "## impl/d117-ledger-recovery...origin/impl/d117-ledger-recovery",
          "4495609c7eca5efd06e886f85bd857d9f80c2f53",
          "4495609c7eca5efd06e886f85bd857d9f80c2f53"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK.*4495609c7eca5efd06e886f85bd857d9f80c2f53"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical 2,785-test suite was not rerun for this bounded G3 lens; the named corpus gate, classification probes, and mutations were executed.",
      "needs": ""
    }
  ]
}
```

## Findings

### G3-1 — Fingerprint capture is not bound to its claimed ordering

Verdict: **NOT-CLOSED**.

[`PreservationGuard.begin()`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:94>) records the fingerprint and ordering token as two independent fields. [`finish()`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:98>) and the corpus gate only compare the stored scalar ordering and fingerprint values; they do not bind when the fingerprint was actually sampled.

In the temporary-copy counterexample, `begin()` retained the prelaunch `before_order` but deferred `before_fingerprint` until `finish()`, after `resume-finalize` exited. I simultaneously applied the dictated mutation that corrupts `manifest.json` immediately before the binding-conflict refusal. Both “before” and “after” fingerprints therefore saw the already-corrupted manifest, while the stale prelaunch ordering token satisfied the ordering assertions. The mandatory gate passed.

The simpler attacks were correctly rejected:

- Excluding `FINALIZATION_BINDING_CONFLICT` from `PreservationGuard` failed exact-set equality.
- Moving both fingerprint and ordering capture after execution failed `141 not less than 139`.
- The unmodified guard killed the manifest-corruption mutation.

The two-invocation classification itself is correct: authenticated binding mismatch emitted `calibration_finalization_binding_conflict`; structurally unreadable and separately probed hash-invalid custody emitted `calibration_custody_unreadable`.

Checks performed: intact named gate; manifest-corruption, excluded-code, naïve-late-baseline, and decoupled-late-baseline mutations in `$TMPDIR`; binding-vs-custody public-process probes; low-level guard test; diff/worktree/upstream checks.

## Residual risk

The full canonical suite was not rerun; this does not affect the reproduced gate bypass.