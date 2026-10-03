```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "No branch defects found; 140 requested tests and adversarial replay probes passed, with one sandbox-limited direct CLI check.",
  "workspace": {
    "base_requested": "3260e280",
    "base_mode": "exact",
    "head_start": "7f3953e37319636bcb658b67af60a73d62edcfc0",
    "head_end": "7f3953e37319636bcb658b67af60a73d62edcfc0",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "PASS",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/adae-sol /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_g2a_calibration_attachment tests.test_harvest_g2a_window tests.test_gen_g2a_window tests.test_controller",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 140 tests in 113.982s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "(?s)Ran 140 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/adae-sol /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/adae-sol/probes.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["trial derived terminal authenticated 384 aborted", "PROBES OK"]},
      "expected": {"exit_code": 0, "tail_regex": "PROBES OK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/adae-sol /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/adae-sol/additional_probes.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ADDITIONAL PROBES OK"]},
      "expected": {"exit_code": 0, "tail_regex": "ADDITIONAL PROBES OK"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/adae-sol /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/adae-sol/cross_session_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["actual prior-session pre REFUSE G2-a pre attachment does not match the finalized pre slot", "CROSS SESSION PROBE OK"]},
      "expected": {"exit_code": 0, "tail_regex": "CROSS SESSION PROBE OK"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/adae-sol /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/adae-sol/harvest_real.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["AssertionError: {'detail': 'harvest_frozen_input_authentication_failed', 'type': 'G2AProbeError'}"]},
      "expected": {"exit_code": 0, "tail_regex": "REAL HARVEST OK"}
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/adae-sol /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/adae-sol/harvest_replay.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["derived terminal authenticated 384 aborted", "REAL HARVEST REPLAY OK"]},
      "expected": {"exit_code": 0, "tail_regex": "REAL HARVEST REPLAY OK"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/adae-sol/audit_assertions.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Existing harvest test assertion ASTs unchanged: 46 methods; 132 assertion calls", "Added harvest tests: 2", "Estimator, captured power adapter, physics and protocol unchanged", "ASSERTION AUDIT OK"]},
      "expected": {"exit_code": 0, "tail_regex": "ASSERTION AUDIT OK"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check 3260e280 7f3953e3",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The direct real harvest's frozen-input subprocess failed because the sandbox denied sysctl kern.osversion. The successful replay retained input authentication but substituted frozen identity/T1 vectors for live observation.",
      "needs": "Repeat the unmodified real CLI in the lead's environment if a fresh direct-CLI result is required."
    }
  ]
}
```

## Findings

No BLOCKER, MAJOR, MINOR, or NIT findings. Repository HEAD and clean workspace remained unchanged; all writes stayed under `/tmp/adae-sol`.

The controller probes exercised the guards at `joulewise/controller.py:538–576`:

| Probe | Executed outcome |
|---|---|
| Governed ordinary pre slot, exact registered config | Admitted |
| Legacy controller attachment; legacy backfill | Refused Revision-5 evidence |
| Derivation session | Refused |
| Non-diagnostic or claim-eligible plan | Refused |
| Edited plan; forged session reference | Refused |
| Unregistered member; changed config with the same run ID | Refused |
| Uncommitted pin | Refused |
| Manually set environment on a different runs root | Refused |
| Actual previous session’s pre capture | Refused |
| Historical-import pre guard, via snapshot mutation | Refused |

`paper_anchor_correction_quantified.py:458` **does read the stored bound** from the real Revision-5 capture. This predates this branch: BFG-D round 7b explicitly reverted C-2(b), preserving the pinned historical-corpus producer. It has no connection to the new controller admission path.

The real attachment replay used copied capture, plan and config bytes, retaining their original custody coordinates and routing repository lookup to the measurement clone. It admitted the exact frozen real plan. Appending one byte independently to evidence, plan or config refused. Every returned attachment artifact remained byte-identical to its copied source.

Harvest checks at `scripts/harvest_g2a_window.py:143` and `scripts/recover_calibration_ledger.py:73` established:

- Every real mid-session receipt at sequences 377–382 refused generic head-pin creation; terminal-pin selection also refused the open session.
- Read-only replay returned `RECOVER`, with `bracket_incomplete`, `chain_nonzero_or_missing_exit`, and `rung_valid_small_members_shortfall`; `capture_made=true`.
- Source ledger and pin remained byte-identical. Both the existing trial and my derived terminal ledger authenticated at sequence 384, state `aborted`.
- The default complete-window fixture returned `SELECT` with 24 valid members, used `terminal-pin` → `advance-head-pin`, preserved ledger bytes and advanced the source pin.
- The empty `derived/terminal-ledger.jsonl.lock` is harmless. Permanent lock sidecars are intentional; kernel `flock` ownership determines liveness (`joulewise/calibration_ledger.py:3623`). Its existence is neither a terminal receipt nor evidence of an active writer.

No existing harvest assertion was weakened: AST comparison found all **132 assertion calls across 46 existing test methods unchanged**. Each modification serves the new execution path:

- Imports expose real ledger/recovery APIs and the shared Git fixture helper.
- The snapshot gains the governed-open-extension flag.
- The mock switches from generic receipt pinning to session terminal pinning.
- `crash_after_pre` constructs a committed seed and actual open-session receipt tail.
- Two added tests assert copied-source preservation/authenticated closure and the default source abort/pin procedure.

The provenance field at `joulewise/controller.py:515` changes bundle metadata bytes only. It does not alter copied calibration artifacts, captured telemetry, measured values, or numerical estimator inputs. The reducer, power adapter, fiducial physics and protocol are unchanged.

I found no disagreement with sealed registration §4 or §7: stage order and timing remain intact; incomplete governed sessions produce `RECOVER`, capture detection remains archival, and no selection or pooling occurs for w1.

## Residual risk

The direct real CLI check was limited by the sandbox’s `sysctl` denial. The successful real-data harvest replay substituted frozen identity/T1 observations; it is read-only replay evidence, not live hardware validation. Complete-window verification used real ledger replay with fixture member/bracket validation.

VERDICT: PASS