```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Stages 1–2 mostly conform, but receipt validation permits forged GO/stage states and the required falsifiers could not run in this read-only sandbox.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "088c20da8984484805aae8fb82a13330ec1b8af2",
    "head_end": "088c20da8984484805aae8fb82a13330ec1b8af2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [
    "joulewise/scheduler_gates.py",
    "tests/test_scheduler_gates.py",
    "schedgate-ruling.md",
    "schedgate-terra-design.md",
    "schedgate-opus-design.md"
  ],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Receipt validation does not enforce stage-1/2 gate semantics or gate-scoped mirrored codes.",
        "evidence": "validate_scheduler_gate_receipt accepted an all-PASS, claim-admissible GO receipt despite G1/G2/G3/G6 being stubs, and accepted readiness_reviewed_main_mismatch on G5. The evaluator does not mint either state, but the validator admits both."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B -c '<in-memory forged receipt validation probe>'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "all-pass= GO",
          "wrong-gate= readiness_reviewed_main_mismatch"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "validator rejects forged staged GO and wrong-gate mirrored code"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest discover -s tests -p test_scheduler_gates.py -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 23 tests in 0.009s",
          "FAILED (errors=20)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2281 tests in 47.552s",
          "FAILED (errors=1408, skipped=88)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=100\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The reboot and moved-main falsifiers both error in setUp before their bodies because no usable temporary directory exists. R12's writable-worktree test-run requirement remains unmet.",
      "needs": "Rerun the focused scheduler suite and canonical suite in a writable worktree."
    },
    {
      "id": "FL2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The delivered test file has 23 ordinary test methods and zero skip mechanisms. The claimed 100-vs-95 five-skip delta cannot arise from this artifact; the repository's prior report already classifies that delta as unresolved environment-conditional behavior.",
      "needs": "Capture the writable canonical run's per-test skip list before attributing a five-skip delta."
    }
  ]
}
```

## Findings

### F1 — should_fix

`validate_scheduler_gate_receipt()` exact-validates keys, but not the ruled stage/gate semantics. It accepts:

- `GO` with every gate `PASS`, including currently stubbed G1/G2/G3/G6.
- A G4-only mirrored code on G5, with `mirrored_from: "arm_readiness"`.

Bind permitted codes to their gate, and require G1/G2/G3/G6 to remain `NOT_IMPLEMENTED` in this stage (except G1/G2 `NOT_EVALUATED` after G5 refusal). Add both falsifiers.

Clause results:

1. **FAIL** — separate vocabulary and causal ground are correct in emitted receipts, but validation admits a mirrored G4 code on G5.
2. **PASS** — `joulewise.window_scheduler_gate_receipt.v1` and root/gate/refusal exact-key checks are implemented.
3. **PASS** — source evaluates G5 first, records all six gates, and makes G1/G2 `NOT_EVALUATED`, never `PASS`, on boot mismatch.
4. **PASS** — G4 requires `exact_match is True`; unavailable origin yields `REFUSE` with `failed_conjunct: unavailable`.
5. **PASS** — G5 uses `O_EXCL`, preserves the initial campaign pin, and checks live/pin/every receipt against the authoritative pin.
6. **FAIL** — evaluator output is correctly `NO-GO`, but the validator accepts a forged staged `GO` receipt.
7. **PASS** — no bypass/waiver/force flag is present; the only implementation write is the campaign-root boot pin. `_pack_record()` is read-only.
8. **PASS** — none of the four cold-pass corrections changes a stages-1/2 obligation: warning re-homing is documentary; G1 byte recomputation is stage 3; causal-ground wording preserves the stage-1 vocabulary invariant; R-7’s B-δ driver clause is later topology work.
9. **FAIL** — no five new skips can be identified from this artifact: it contains zero skip mechanics. The focused run has 3 passes and 20 temp-directory setup errors; both required falsifiers error before execution. The full suite likewise cannot establish `skipped=100`.

## Residual risk

A writable rerun must prove the reboot and moved-main falsifiers execute, then record the canonical suite’s actual skip list and total.