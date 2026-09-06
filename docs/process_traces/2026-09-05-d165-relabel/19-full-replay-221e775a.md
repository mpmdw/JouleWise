# Full-suite replay of feat/2026-09-05-d165-relabel at 221e775a (row 9)

Unpiped full replay by the magistrate from /Users/edr/code/JouleWise-wt-d165-relabel (origin/main df657492 merged: paper-K/L/M, seam, F+B included) with R7F_CORPUS_ROOT=/Users/edr/code/JouleWise; machine uptime crossed three days during the run.

```
ERROR: test_acid_real_boot_session_then_real_arm_generator_reaches_go (test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go)
Darwin's real boot-session identifier reaches the arm generator.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-d165-relabel/tests/test_arm_readiness_evidence_t0.py", line 3035, in test_acid_real_boot_session_then_real_arm_generator_reaches_go
    self._assert_acid_authored_fifteen_then_arm_generator_reaches_go(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
FAIL: test_real_client_worker_artifact_contract_over_localhost (test_node_worker_subprocess.NodeWorkerSubprocessTests.test_real_client_worker_artifact_contract_over_localhost)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-d165-relabel/tests/test_node_worker_subprocess.py", line 151, in test_real_client_worker_artifact_contract_over_localhost
    self.assertTrue(prepare.ok, prepare)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : NodeTaskResult(ok=False, status='failed', failure_reason=<FailureReason.UNKNOWN_ERROR: 'unknown_error'>, message="missing or malformed status.json: [Errno 2] No such file or directory: '/var/folders/p3/fp
Ran 5269 tests in 7148.894s
FAILED (failures=1, errors=1, skipped=108)
```

## Disposition

- FAIL test_node_worker_subprocess … real_client_worker: the load-sensitive 15.0 s budget signature dispositioned in docs/process_traces/2026-09-04-fanout/30-32 and reproduced on canonical main in isolation (2026-09-04-paper-custody/18). Environmental, pre-existing.
- ERROR test_arm_readiness_evidence_t0 … test_acid_real_boot_session_then_real_arm_generator_reaches_go: 'T-0 RAW anchor span exceeds 3600000000000 ns'. Reproduced in isolation on THIS branch and on canonical main (9bcc9559 lineage) at uptime 3 d 3 h; the same test passed in the paper-M replay at uptime 2 d 22 h. The acid fixture anchors R0 with time.monotonic_ns() when the clock is real (tests/test_arm_readiness_evidence_t0.py, helper at ~2870-2880) while the author anchor is monotonic_raw_ns; on Darwin the two clocks drift apart across sleep/uptime, so the span check fails once the drift exceeds the fixture's margin. Test-fixture defect, pre-existing on main, unrelated to this branch (which touches neither file); registered as T0-ACID-CLOCK-01 in TASK_QUEUE.md. Production arming samples one clock family inside the T-0 sequence and is not affected by this fixture.
- All other 5267 tests pass or skip (skipped=108): census 10, closeout 59, custody 29, round-7 checker 67, paper tests, refresh lanes.
