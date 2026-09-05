# Full-suite replay of feat/2026-09-04-fb-metadata at 9d854b4d (row 9)

Unpiped full replay by the magistrate from /Users/edr/code/JouleWise-wt-fb-metadata (origin/main e19ff60f merged) with R7F_CORPUS_ROOT=/Users/edr/code/JouleWise, concurrent with two other replays and one astra seat.

```
FAIL: test_real_client_worker_artifact_contract_over_localhost (test_node_worker_subprocess.NodeWorkerSubprocessTests.test_real_client_worker_artifact_contract_over_localhost)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-fb-metadata/tests/test_node_worker_subprocess.py", line 151, in test_real_client_worker_artifact_contract_over_localhost
    self.assertTrue(prepare.ok, prepare)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true : NodeTaskResult(ok=False, status='failed', failure_reason=<FailureReason.UNKNOWN_ERROR: 'unknown_error'>, message="missing or malformed status.json: [Errno 2] No such file or directory: '/var/folders/p3/fp

----------------------------------------------------------------------
Ran 5204 tests in 6704.248s
FAILED (failures=1, skipped=109)
```

## Disposition

- Single failure: tests/test_node_worker_subprocess.py real-client worker call with a 15.0 s budget, the same load-sensitive signature dispositioned in docs/process_traces/2026-09-04-fanout/30-32 and reproduced on canonical main in isolation under load earlier today (docs/process_traces/2026-09-04-paper-custody/18-full-replay-f13e3a44.md). This branch changes no worker code path. Environmental, pre-existing.
- All other 5203 tests pass or skip (skipped=109), including the previously red dependence sheet, both relocation tests, the mint fixture module, the closed reader census, paper custody and paper rendering.
