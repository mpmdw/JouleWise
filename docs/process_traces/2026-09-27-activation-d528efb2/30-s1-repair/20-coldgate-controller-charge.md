# Cold gate S1-REGRESSION-01-A2: a test file outside every grant contradicts text 12a

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Rulings:** S1-REGRESSION-01 `docs/process_traces/2026-09-27-activation-77b1bee2/36-s1-regression-consult/21-coldgate-fable-ruling.md` (text 12a §3.3; scope §6: "a seat that needs a refused or unnamed path stops and returns the exact path and the test that needs it; the lead brings it to a cold gate") and its addendum A1 `docs/process_traces/2026-09-27-activation-77b1bee2/36-s1-regression-consult/31-addendum-ruling.md` (its §6 item 2 names `tests/test_controller.py` among S1's §E files that no repair seat may write).
**The return:** seat P implemented 12a and 10a on branch `fix/2026-09-27-s1-regress-P` at `db4eadf6` (worktree `/Users/edr/code/JouleWise-wt-s1-P-d528efb2`, read-only for you; base S1 head `c7593edb`). Report: `docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/11-seat-P-report.md`. Its blocking flag F1: `tests.test_controller.SuiteControllerTests.test_mock_experiment_refuses_at_aggregation` still expects `WindowBatteryRefusal`, "contrary to ruled operational mock admission"; `tests/test_controller.py` is in no seat's scope. (Its F2, the 10a issuing sub-case, was the lead's by ruling §4 and is decided: `CustodyFailure`, with the old assertion kept in a split test.)

**Rule on:**
1. Read the test and the production path it exercises at `db4eadf6` (`joulewise/controller.py`, `joulewise/aggregate.py`, `joulewise/bundle_read.py`). Is this test's flow one of 12a's two admitted non-claim flows (campaign completion; the experiment manifest aggregate), as ruled? Or did seat P admit more than 12a allows, so production must still refuse here? Execute the test at `db4eadf6` and cite file:line.
2. If the assertion is stale: grant `tests/test_controller.py` for exactly this test, with the exact replacement assertion (and, per "split, never delete", where the refusal coverage moves — e.g. a mixed window still refusing), and name which seat carries it.
3. If P over-admitted: give the exact correction to P's production diff, and name the seat.
4. Does the answer change any other clause of the ruling or addendum?

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. `/opt/homebrew/bin/python3 -B`; macOS has no `timeout` (`perl -e 'alarm N; exec @ARGV' …`); kill any process you start by PID. Never read the laptop battery.
- Modify NO file in any repository except the ruling file below. Scratch under `/tmp/cg-s1ctl-d528efb2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/21-coldgate-controller-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 30 minutes. First line `RULING: S1-REGRESSION-01-A2 ISSUED`. Plain language. End with a 3-line plain summary.
