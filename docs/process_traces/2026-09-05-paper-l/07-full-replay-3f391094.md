# Full-suite replay of feat/2026-09-05-paper-l at 3f391094 (row 9)

Unpiped full replay by the magistrate from /Users/edr/code/JouleWise-wt-paper-l (origin/main e19ff60f merged; D-166 identity-set fixture fix and singleton coverage test included) with R7F_CORPUS_ROOT=/Users/edr/code/JouleWise, concurrent with two other replays.

```
FAIL: test_real_client_worker_artifact_contract_over_localhost (test_node_worker_subprocess.NodeWorkerSubprocessTests.test_real_client_worker_artifact_contract_over_localhost)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-paper-l/tests/test_node_worker_subprocess.py", line 151, in test_real_client_worker_artifact_contract_over_localhost
    self.assertTrue(prepare.ok, prepare)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : NodeTaskResult(ok=False, status='failed', failure_reason=<FailureReason.UNKNOWN_ERROR: 'unknown_error'>, message="missing or malformed status.json: [Errno 2] No such file or directory: '/var/folders/p3/fp

----------------------------------------------------------------------
Ran 5202 tests in 6684.045s
FAILED (failures=1, skipped=109)
```

## Disposition

- Single failure: the node-worker real-client test with a 15.0 s budget, the load-sensitive signature dispositioned in docs/process_traces/2026-09-04-fanout/30-32 and reproduced on canonical main in isolation under load (docs/process_traces/2026-09-04-paper-custody/18-full-replay-f13e3a44.md). This branch changes no worker code path. Environmental, pre-existing.
- The six FrozenConsumerIdentitySetTests that failed at a3bbd9b3 now pass (D-166 fixture fix, reports 06–08 in docs/process_traces/2026-09-05-d166-prompt0/); all other 5201 tests pass or skip (skipped=109).
