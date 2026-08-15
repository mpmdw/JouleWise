```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "READY does not survive: the unbounded lease-held detector is launch-blocking, the 15/16 coverage claim is false, and launch-critical verification remains open.",
  "workspace": {
    "base_requested": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "base_mode": "exact",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "branch": "worktree-agent-a5188adc7904c0b63"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "NOT-READY",
    "ready_survives": false,
    "coverage": {
      "reported": "15/16",
      "verdict": "REFUTED",
      "reason": "The universe is self-selected and inconsistently atomized; E4 is explicitly partial, E15 includes two skips, E16 contains 13 rather than 16 tests, and directly scoped artifacts/tests were omitted.",
      "direct_test_universe": 251,
      "omitted_live_three_window_tests": 23
    },
    "findings": [
      {
        "id": "L2-1",
        "severity": "blocker",
        "disposition": "CONFIRMED",
        "summary": "The detector has no finite work budget and the frozen chain invokes it synchronously while holding the writer lease."
      },
      {
        "id": "L2-COV-1",
        "severity": "blocker",
        "disposition": "CONFIRMED",
        "summary": "The anti-ritual coverage packet does not establish a real denominator."
      },
      {
        "id": "L2-EDQ-1",
        "severity": "blocker",
        "disposition": "CONFIRMED",
        "summary": "Full crash/recovery and stable live writer/sudo qualification remain unclosed despite the charter forbidding deferred ED-QUALIFICATION at READY."
      },
      {
        "id": "L2-2",
        "severity": "should_fix",
        "disposition": "CONFIRMED",
        "summary": "Missing ledger parent produces an unregistered FileNotFoundError traceback."
      },
      {
        "id": "L2-3",
        "severity": "should_fix",
        "disposition": "CONFIRMED",
        "summary": "Runbook needs_pin_commit language contradicts the required PHYSICAL_AHEAD pre-slot state; nit severity is understated."
      },
      {
        "id": "L2-4",
        "severity": "nit",
        "disposition": "REFUTED",
        "summary": "The marker is absent on idempotent re-reservation, but the runbook explicitly forbids re-reserving on restart; emitting a fresh authorization marker would be misleading."
      }
    ],
    "absence_claims": [
      {
        "id": "A1",
        "claim": "No detector work budget or chain watchdog",
        "disposition": "CONFIRMED",
        "severity": "blocker"
      },
      {
        "id": "A2",
        "claim": "No idempotent-replay calibration_pre_reserve_authorized marker",
        "disposition": "CONFIRMED_ABSENCE_REFUTED_DEFECT",
        "severity": "nit"
      },
      {
        "id": "A3",
        "claim": "No writer signature on complete custody",
        "disposition": "CONFIRMED_ACCEPTED_THREAT_MODEL_LIMITATION",
        "severity": "nit"
      },
      {
        "id": "A4",
        "claim": "No copied preflight comparator scalar in the writer",
        "disposition": "CONFIRMED",
        "severity": "nit"
      },
      {
        "id": "A5",
        "claim": "No scoped code/runbook/artifact drift from ac3fe1d",
        "disposition": "CONFIRMED",
        "severity": "nit"
      },
      {
        "id": "A6",
        "claim": "No stray processes after L2's run",
        "disposition": "PARTIAL_NOT_RETROSPECTIVELY_REPRODUCIBLE",
        "severity": "nit"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --name-status ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b..HEAD && shasum -a 256 docs/phase_2/window_runbook.md configs/calibration/calibration_acceptance_d079_v2.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M README.md",
          "M RUN_STATE.md",
          "A docs/process/audit-baseline-manifest.json",
          "25a4e809... window_runbook.md",
          "316113960... calibration_acceptance_d079_v2.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "316113960c596a6f"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import unittest; names=[\"tests.test_authentication_io\",\"tests.test_calibration_bracketing\",\"tests.test_calibration_custody_store\",\"tests.test_calibration_exits\",\"tests.test_calibration_ledger\",\"tests.test_calibration_live_three_window\",\"tests.test_calibration_writer_crash_matrix\",\"tests.test_powermetrics_fiducial\"]; L=unittest.defaultTestLoader; print({n:L.loadTestsFromName(n).countTestCases() for n in names})'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "18, 42, 7, 30, 72, 23, 13, 46 tests respectively"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "test_calibration_writer_crash_matrix': 13"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_powermetrics_fiducial.ScheduleTests.test_van_der_corput_prefix tests.test_powermetrics_fiducial.ScheduleTests.test_gaps_avoid_ten_hertz_phase_lock tests.test_powermetrics_fiducial.FrozenProtocolTests.test_preflight_screen_is_derived_bit_exactly_from_real_artifact tests.test_powermetrics_fiducial.FrozenProtocolTests.test_writer_has_no_copied_preflight_scalar_and_comparison_is_derived tests.test_powermetrics_fiducial.FrozenProtocolTests.test_calibration_entrypoint_refuses_protocol_mismatch_before_live_import",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 0.002s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/recover_calibration_ledger.py audit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"head_digest\":\"08456d50...\",\"head_sequence\":76,\"status\":\"audit_clean\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "audit_clean"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/recover_calibration_ledger.py audit-observations --baseline-sequence 76 --baseline-digest 08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"status\":\"observations_classified\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "observations_classified"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/recover_calibration_ledger.py --ledger /tmp/jw-l2-refuter-missing-parent-8937dec/ledger.jsonl --head-pin configs/calibration/calibration_ledger_head.json readiness --phase pre-reserve --session-id refuter-session --plan configs/campaigns/d117_floor_qwen25_1p5b_v1/calibration_plan.json",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/jw-l2-refuter-missing-parent-8937dec'"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "\"code\":\"calibration_"
      }
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c '<one-second external alarm around _accepted_region_projection with a non-pruning finite loss limit>'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{'outcome':'external_timeout','elapsed_s':1.0,'detail':'external one-second falsifier'}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "external_timeout"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "python3 -m unittest -v <six selected crash-matrix lease/capability cases with TMPDIR set to mktemp directory>",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 97,
        "tail": [
          "mktemp: mkdtemp failed on /tmp/jw-l2-refuter-tests.*: Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests.*OK"
      }
    },
    {
      "id": "V9",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c '<mutate one valid disposition byte in production ledger and call _parse_ledger in memory>'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "source_receipts=76, accepted_prefix=1, reasons=[calibration_ledger_malformed, calibration_ledger_recovery_required]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "calibration_ledger_malformed"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The sandbox denied TMPDIR creation, so stateful crash/recovery tests are NOT-EXECUTABLE-IN-SANDBOX.",
      "needs": "Run the actual 13-test crash matrix and 23-test three-window module in a writable isolated test environment before accepting READY."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The delegated worktree was concurrently removed; subsequent read-only probes used clean main at the identical requested HEAD without any checkout or branch switch.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD is a descendant of manifest head ac3fe1d only through README.md, RUN_STATE.md, and the manifest addition; all L2-scoped bytes checked remain identical.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "GitHub network access failed, so PR #149's claimed green status was not independently verified; the workflow definition proves only that a 120-minute two-version job exists.",
      "needs": "Attach or independently inspect the PR #149 check records."
    }
  ]
}
```

## Findings

### L2-1 — CONFIRMED; severity raised from should-fix to blocker

The projection starts with a 1.5 s × 1.5 s rectangle and refines to 0.1 ms ([powermetrics_fiducial.py](/Users/edr/code/JouleWise/joulewise/powermetrics_fiducial.py:555)). Its `while stack` loop has no cell limit, deadline, cancellation, or nonconvergence exit. The writer acquires the lease at [validate_powermetrics_fiducial.py](/Users/edr/code/JouleWise/scripts/validate_powermetrics_fiducial.py:846), calls detection at line 1509 even when the anchor is unresolved, and releases only during finalization at line 1037. The frozen runbook invokes the writer directly, without a watchdog, at [window_runbook.md](/Users/edr/code/JouleWise/docs/phase_2/window_runbook.md:1017).

My independent non-pruning projection probe required an external alarm and timed out at exactly 1.0 s. This is not merely availability: while it holds the sole writer lease it reaches neither a claim-bearing output nor a governed fail-closed terminal result. READY therefore breaks here. The proposed remedy is directionally sound: add a mandatory finite evaluation/wall budget whose exhaustion produces registered invalid evidence and governed abort; skipping projection when the anchor is already unresolved is also sound.

### L2-COV-1 — CONFIRMED blocker: 15/16 is not the real universe

The denominator is neither requirements-derived nor consistently atomized. A file-atomic lower bound is 29 directly relevant artifacts before per-pack plans and fixtures. The report omitted, among others:

- `docs/contracts/powermetrics_fiducial.md`
- `docs/contracts/calibration_ledger.md`
- `scripts/calibration_ledger_bootstrap.py`
- `scripts/calibration_ledger_backfill.py`
- `tests/test_calibration_live_three_window.py`
- `tests/verify_calibration_acceptance_corpus.py`
- frozen protocol v1/v2 identities

The omitted three-window module explicitly exercises “one issuance-equivalent prefix and its three live sessions” ([test_calibration_live_three_window.py](/Users/edr/code/JouleWise/tests/test_calibration_live_three_window.py:123)) and contains 23 tests.

Even internally, 15/16 fails: E4 admits only ~1,200/5,567 lines plus behavioral coverage, while E15 calls 215 tests “executed” despite two skips. E16 has 13 tests, not 16—the unittest loader independently returned 13. The directly scoped eight-module test universe is 251 cases: 215 fast + 13 crash-matrix + 23 three-window. The reported packet accounts for 215 fast cases, including two skipped, and only six crash cases; it omits the entire 23-case lifecycle module. Remedy: rebuild the denominator from charter obligations using one stable unit of counting, then report attempted, executed, skipped, and unexecuted separately.

### L2-EDQ-1 — CONFIRMED blocker

The charter says stable capabilities such as sudo powermetrics behavior must be qualified before the sitting and “cannot be deferred” ([instrument-readiness-audit-charter.md](/Users/edr/code/JouleWise/docs/process/instrument-readiness-audit-charter.md:70)); council READY requires all ED-QUALIFICATION rows closed at lines 81–84. L2 nevertheless leaves real-scale writer/sudo behavior and its own crash-matrix qualification open. Thus even absent L2-1, this report could be UNVERIFIED, not READY.

### L2-2 — CONFIRMED should-fix

The exact missing-parent probe exited 1 with a raw `FileNotFoundError`. `resolve_ledger_lease_identity()` performs `parent.resolve(strict=True)` outside its typed-error conversion ([calibration_ledger.py](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:2881)); the recovery CLI catches only `CalibrationLedgerError` ([recover_calibration_ledger.py](/Users/edr/code/JouleWise/scripts/recover_calibration_ledger.py:484)). Severity and remedy shape are sound: translate this path into an existing registered unreadable/unsafe-ledger refusal without creating directories during diagnostic readiness.

### L2-3 — CONFIRMED, but severity is should-fix rather than nit

The runbook requires the pre-slot governed session extension while also saying any `needs_pin_commit: true` ends the attempt ([window_runbook.md](/Users/edr/code/JouleWise/docs/phase_2/window_runbook.md:407)). Code sets that field for every `PHYSICAL_AHEAD` relation ([calibration_ledger.py](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:4949)), which is the intended pre-slot relation. The ambiguity can mechanically abort every correct session, making it launch-relevant. Remedy should align semantics, preferably making `needs_pin_commit` terminal-phase-specific; merely adding prose is weaker but acceptable if it explicitly exempts an authenticated open-session pre-slot extension.

### L2-4 — REFUTED as a defect

The absence is real: the authorization event is printed only when fresh pre-reserve readiness succeeds ([reserve_calibration_window_bracket.py](/Users/edr/code/JouleWise/scripts/reserve_calibration_window_bracket.py:162)). An idempotent replay reaches the existing-session path and does not reauthorize. But the runbook explicitly says: “On restart, do not reserve again … run `session-status`” ([window_runbook.md](/Users/edr/code/JouleWise/docs/phase_2/window_runbook.md:952)). Reprinting `calibration_pre_reserve_authorized` would falsely imply a fresh authorization. Drop WO-L2-4; at most document that idempotent API replay is non-authorizing.

### Independent falsifiers

A new in-memory ledger-tamper falsifier changed one `valid` disposition byte while leaving its old digest. Parsing retained only the one-record valid prefix and returned both `calibration_ledger_malformed` and `calibration_ledger_recovery_required`; the tamper failed closed.

A second fiducial-edge falsifier injected a non-finite power sample into an otherwise pulse-shaped trace. Detection returned `all_pulses_detected=False`, `b_fiducial_s=None`, and `pulse_detection_incomplete`; this edge survived.

### Other absence claims

- No chain watchdog: CONFIRMED, blocker, folded into L2-1.
- No custody writer signature: CONFIRMED, but explicitly within the documented trusted-writer threat model ([calibration_ledger.md](/Users/edr/code/JouleWise/docs/contracts/calibration_ledger.md:3)); no new work order without a threat-model ruling.
- No copied preflight scalar: CONFIRMED by source search and five passing pure tests; the writer derives it at [validate_powermetrics_fiducial.py](/Users/edr/code/JouleWise/scripts/validate_powermetrics_fiducial.py:267).
- No scoped baseline drift: CONFIRMED.
- No stray L2 probe processes: PARTIAL; this historical postcondition cannot be reproduced after the original process lifetime.

### Unexecuted obligations

1. Full crash matrix: launch-relevant and blocking. It has 13 tests, seven of which remain outside L2’s claimed six-case local subset. The repository records three 600-second loaded-host failures and an open reliability work order ([TASK_QUEUE.md](/Users/edr/code/JouleWise/TASK_QUEUE.md:298)).
2. Real D-079 production-prefix authentication test: launch-relevant provenance evidence; current ledger audit and byte pins reduce risk, but it should run before audit closure.
3. Deterministic/write-explicit issuance test: not per-night launch-critical for unchanged issued bytes, but required before reissuance/bootstrap.
4. Historical-import internals: not on the ordinary live-night path after the fixed sequence-76 prefix, but relevant to the acceptance artifact’s provenance. Treat as audit coverage debt, not a new launch implementation.
5. Bracketing evaluation half: legitimately owned by L4; no L2 penalty.
6. Real-time writer and sudo powermetrics: launch-critical ED-QUALIFICATION and cannot remain open at READY.

### Synthesis

L2-1, L2-2, and L2-3 survive; L2-1 rises to blocker, L2-3 rises to should-fix, and L2-4 dies as a phantom defect. READY fails independently on the unbounded lease-held detector, the invalid coverage denominator, and unclosed crash/live qualification. The minimal true work-order set is: bounded fail-closed projection; phase-correct `needs_pin_commit` semantics; typed missing-parent refusal; then an audit-closure rerun covering the actual 13-test crash matrix, the omitted 23-test three-window module, the two real-fixture tests, and the required ED qualification. No idempotent-marker or writer-signature work order is presently justified.

## Residual risk

Stateful tests could not run because the sandbox denied temporary-directory creation. PR #149’s check status also could not be independently queried because GitHub access was unavailable. The original delegated worktree was concurrently deleted, though all subsequent inspection used clean `main` at the identical HEAD and no repository bytes were changed.