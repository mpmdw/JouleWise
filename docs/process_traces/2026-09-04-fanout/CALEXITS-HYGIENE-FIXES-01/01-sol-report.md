```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Confirmed the complete seven-item calibration-exit hygiene implementation already at this head, closed its H1 counterfactual-test gap, and pinned the E-4 errno fence.",
  "workspace": {"base_requested":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","base_mode":"exact","head_start":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","head_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","upstream_end":"849915bc1393a6c1cb962a4dc12b25c33dad1f74","branch":"feat/2026-09-04-fan-CALEXITS-HYGIENE-FIXES-01"},
  "pathspec": ["tests/test_calibration_exits.py","docs/process_traces/2026-09-04-fanout/CALEXITS-HYGIENE-FIXES-01/01-sol-report.md"],
  "unowned_dirty": [],
  "verdict": {"implementation":"implemented","acceptance":"ready"},
  "verification": [
    {"id":"V1","kind":"suite","cmd":"python3 -m unittest -v tests.test_calibration_exits","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["test_success_capture_is_byte_identical_to_legacy_termination (tests.test_calibration_exits.SamplerLifecycleHardeningTests.test_success_capture_is_byte_identical_to_legacy_termination) ... F4_SUCCESS_CAPTURE_BYTES=214524 SHA256=6aa3b1ea3b07ac9230d7c920eccf5d467edc194efceb7d1d1ae3e97041ec315f BYTE_IDENTICAL=1","ok","","----------------------------------------------------------------------","Ran 47 tests in 683.864s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 47 tests in [0-9.]+s\\n\\nOK"}},
    {"id":"V2","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V3","kind":"inspection","cmd":"git diff --name-only e6f500ca^..0202ce9a","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["tests/test_calibration_exits.py"]},"expected":{"exit_code":0,"tail_regex":"^tests/test_calibration_exits.py$"}}
  ],
  "flags": [
    {"id":"F1","kind":"baseline_drift","level":"nonblocking","text":"The state kernel still labels CALEXITS-HYGIENE-FIXES-01 queued although all seven implementation commits are ancestors of the requested base and the focused module is green.","needs":"Magistrate should retire the kernel row and regenerate TASK_QUEUE.md and RUN_STATE.md; this worker was expressly forbidden to edit those files."}
  ]
}
```

## Change

The current head already contained the row's seven prioritized repairs in commits `e6f500ca`, `7c08b985`, `bc27c96b`, `1d913a94`, `c55e806b`, `6f62f67b`, and `0202ce9a`. They implement the bounded shapes required by the audit: fixed logical time, one immutable witness-corpus owner, semantic readiness, stable detached-process identity, complete Git Trace2 topology, progress-acknowledged resume, and backoff assertions that do not grade host speed. Git Trace2 is Git's structured event stream; a process identifier is the operating system's numeric process label.

This session added a direct counterfactual for the logical writer's default origin. The test makes any call to the ambient wall clock raise immediately, so restoring `str(time.time())` to `_writer_env` makes the regression fail. It also gave the E-4 cleanup-race errno allowlist one named constant and asserted exact equality with `ENOTEMPTY` and `ENOENT`, preserving the upheld fence without changing the real maintenance witness.

| Finding | Decision | Evidence |
|---|---|---|
| H1's existing byte-equality test supplied its own fixed origin, so it did not directly guard the default | Add a poisoned-wall-clock unit regression against `_writer_env` | With the old expression temporarily restored, `python3 -m unittest -v tests.test_calibration_exits.RefusalInventoryTests.test_default_writer_origin_never_reads_the_ambient_wall_clock` exited 1 with `AssertionError: logical writer read ambient wall time`; after restoration it exited 0 with `OK` |
| The E-4 errno pair was repeated as tuple literals | Name the exact set once and assert its membership and equality | `test_absent_pack_child_never_masks_a_raised_cleanup_errno` passes inside V1; the real forced-maintenance test still reports a detached maintenance path and no incomplete trace |
| The implementation predates this fan-out branch but the kernel row remains queued | Treat code acceptance as ready and leave source-of-truth retirement to the magistrate | The seven named commits are ancestors of the requested base; V1 passes; V3 shows their implementation range touched only the calibration-exit test module |

Design record: the forcing problem was that elapsed host time, file existence, fixed sleeps, and bare process identifiers could substitute scheduler luck for semantic evidence. Keeping those mechanisms with wider delays would only move the failure threshold. The landed recommendation instead waits for meaning: parseable or exact records, durable sequence acknowledgements, retained process handles, stable detached identities, and terminal events in one Trace2 clock domain. For example, after resume the parent appends the `sampling_stopped` event with its sequence, the sampler durably acknowledges that sequence after capture progress, and only then does the parent terminate it. Removing the acknowledgement wait permits termination before the intended progress and is exercised by the module's suspension-invariance test.

## Verification notes

The repository-wide suite was not run, exactly as required by the mission preflight. A preliminary selected-test command used `CalibrationExitReliabilityTests` for two methods actually owned by `SamplerLifecycleHardeningTests`; it exited 1 with two loader `AttributeError` results. The corrected command passed both methods, and V1 then passed the complete touched module.

No hardware, privileged access, pending dependency, or unresolved design ruling is needed. The deterministic tests exercise the relevant event and process semantics without presenting fixture evidence as live hardware validation.

## Residual risk

The state kernel and its generated queue and run-state projections remain stale until the magistrate performs the prohibited bookkeeping edits described by flag F1. No production implementation, historical mechanism record, or r6-pinned estimator source changed in this session.
