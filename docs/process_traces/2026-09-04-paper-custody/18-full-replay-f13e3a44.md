# Full-suite replay of the seam branch at f13e3a44 (row 9)

Unpiped full replay, run by the magistrate from /Users/edr/code/JouleWise-wt-paper-custody at f13e3a44 with R7F_CORPUS_ROOT=/Users/edr/code/JouleWise while two astra seats were running (load average 3.2–4.1).

```
FAIL: test_real_client_worker_artifact_contract_over_localhost (test_node_worker_subprocess.NodeWorkerSubprocessTests.test_real_client_worker_artifact_contract_over_localhost)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-paper-custody/tests/test_node_worker_subprocess.py", line 151, in test_real_client_worker_artifact_contract_over_localhost
    self.assertTrue(prepare.ok, prepare)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : NodeTaskResult(ok=False, status='failed', failure_reason=<FailureReason.UNKNOWN_ERROR: 'unknown_error'>, message="missing or malformed status.json: [Errno 2] No such file or directory: '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk

----------------------------------------------------------------------
Ran 5164 tests in 6781.434s
FAILED (failures=1, skipped=110)
```

## Disposition of the single failure

- The failing test is tests/test_node_worker_subprocess.py::test_real_client_worker_artifact_contract_over_localhost, whose real-client worker call carries a 15.0 s timeout (timeout_s=15.0 at lines 149 and 175).
- Rerun in isolation on this branch under the same load: FAILED after 15.175 s (the budget).
- Rerun in isolation on canonical main (3db44a6f) under the same load: FAILED identically.
- The seam branch changes no worker code path (git diff origin/main...f13e3a44 touches no joulewise worker module).
- Same signature as the load-sensitive diagnosis in docs/process_traces/2026-09-04-fanout/30-32 (node-worker budget under load; T0 real-boot cure tracked there). Environmental, pre-existing on main, not introduced by this PR.
- All other 5163 tests: pass or skip (skipped=110).
