# 2026-11-21 Custody deadline test stability

The shard-4 control on `main` reproduced the reservation subprocess
timeouts from PR #930. Running the two original failures in isolation
on the same checkout passed. The tests mixed child startup and host
scheduling with the custody allowance they were meant to exercise.

The reservation tests now use an explicit test clock. A FIFO reader,
metadata probe, or append boundary advances it when the relevant work
has started. The CLI, worker, ledger writes, and refusal documents remain
real. The subprocess watchdog uses wall time to catch a hang. The three
50 ms probe tests wait for worker entry and simulate the bounded join.
The test assertions and production deadline code are unchanged.

The load replay uses the CI timing map to allocate shard 4 of 6 to four
workers. The custody worker replays its regular predecessors and runs
the complete 62-test module 20 times. The other three workers run their
normal assignments and repeat them as needed to sustain the load. The
first loaded repetition passed all 62 tests in a stdlib-only Python
3.13.18 environment.
