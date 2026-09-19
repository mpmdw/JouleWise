SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Delta re-audit (read-only, fix round 1) — lane TEST-LARGE-FRAME-ARGV-PORTABILITY-01, head `3855ad25` vs round-0 head `e32ea56c` vs base `6ec5b460`

Cwd is a detached read-only worktree at `3855ad25`. Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch (use `/tmp/ref-delta-28ff4b28/`). No network, no `sudo`, no `powermetrics`. Never run the canonical `python3 -m unittest discover`; run at most `tests.test_run_night.BindSupervisionProcessTests`. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and pass `-B`. A full-suite replay may be running on this machine concurrently: if a test fails only on its external 8 s watchdog, rerun it once alone and report both outcomes with the load average.

## The fix round you are auditing

`git diff e32ea56c 3855ad25 -- tests/` (3 insertions, 1 deletion) answers two round-1 should-fix findings:

- F-A (contract lens, record `/Users/edr/code/JouleWise-wt-mag-28ff4b28/docs/process_traces/2026-09-18-activation-28ff4b28/04-refuter-contract-astra.md`, finding C3-01): at `e32ea56c` the bench's one-second ACK allowance `ack_until = time.monotonic()+1` was evaluated BEFORE `_BindTask(...)` construction and submission, shortening it by construction time relative to base `6ec5b460` (where it was evaluated after). The refuter's probe `/tmp/ref-contract-28ff4b28/ack_probe.py` (read-only, may still exist) showed base waits at mocked 11.1 with deadline 11.25 while head raised `fault ACK missing`. The fix sets `row['ack_until'] = time.monotonic() + 1` after `row['task'] = task`.
- F-B (execution lens, record `.../05-refuter-execution-opus.md`, finding 1): `max_arg_bytes` defaults to 0 and is only set inside the launcher closure, so the regression could pass blind if the recording stopped running. The fix adds `self.assertGreater(task['max_arg_bytes'], 0)` to `test_large_frame_keeps_each_worker_argument_below_linux_limit`.

## Questions — answer each with executed evidence (commands and output)

D1. Ordering restored: show from the code (cite lines at `3855ad25` and at `6ec5b460`) that the ACK deadline is now evaluated after task construction exactly as at base, and that no other use of `row['ack_until']` (e.g. `Bench.sleep`, the enforcement near the old line 239) sees `None` before it is set. Re-run the C3-01 probe idea against `3855ad25` (adapt the refuter's probe or write your own: mock time so construction consumes 250 ms and confirm the deadline is base-equivalent).
D2. Positive floor bites: with the recording line `row['max_arg_bytes'] = max(...)` deleted in a `/tmp` copy of the fixture (never the worktree), the new test must FAIL with `0 not greater than 0`; with the fixture intact it passes.
D3. Nothing else moved: `git diff e32ea56c 3855ad25` touches only the two test paths and only those lines; the four existing assertions of `test_large_frame_is_incremental_and_still_bounded` remain byte-identical to base.
D4. Whole class green at `3855ad25`: `python3 -B -m unittest tests.test_run_night.BindSupervisionProcessTests 2>&1 | tail -4`.
D5. Same-signature check: did fix round 1 introduce any defect of the same class as round 0's findings (an evaluation-order change in the bench, or an assertion that can pass vacuously)? Look specifically at every field initialised in the `row` dict before the task exists.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre review`; `verdict` = `{counts, findings}` only; JSON header under 8000 bytes; all evidence in the markdown body. Severity vocabulary: blocker / should_fix / nit. End the body with exactly one of "same-signature: none found" or "same-signature: <named signature>".
