# Receipts delta re-review handoff — 2026-11-08

**ADMIT_WITH_FIXES.** The Opus HIGH-1/2/3 fixes pass the requested synthetic
checks against the current v4 r11 head. Two integration conflicts and one
stale test fixture need the lead's attention. Full findings, commands,
normalization limits and the test matrix are in
[the verdict](../perf/timing-receipts-rereview-sol.md).

## Scope and authority

Review branch: `perf/2026-11-08-timing-receipts-rereview`, starting at
`bcd4fd3c2723e5fd89413ff73190fafbb23ff386`. The fix code was found through
the local `origin/receipts-fix` Git ref, not through the sibling worktree
path cited in the previous handoff. Reviewed fix head: `bec6c8ae3`;
current v4 target: `03253edcac230e39a0905d24cee317069c4ae50e`.

Mission M0, the targeted restart/queue/stop-card sections, orchestration,
D-025, and `origin/main:docs/perf/SPEED-TOOLBOX.md` were read. No stop card
was active. The explicit blinded review task overrides ordinary queue work.
The user's full-suite/coordination restrictions override repository defaults:
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` were not edited; no task was registered.

## Work and evidence

- Only this report and `docs/perf/timing-receipts-rereview-sol.md` were added
  to the review branch. No production source or tests were edited there.
- A detached scratch worktree under
  `/private/tmp/jwsol/squeeze/receipts-rereview/tmp/integration` holds merge
  `4c937e0be8731fd79a7c08832139aed682728767`. Its only manual resolutions
  preserve the receipt closure entry and wrap the current installer call,
  including its `now` argument. That local merge is test evidence, not a
  landing or registration decision. Nothing was pushed.
- Independent cross-tree processes exported Python/config blobs from the
  two pinned Git objects. All 20 bundles validate with `[]` on both trees;
  all 286 normalized capture files match. Happy/refusal structure and harvest
  yield bytes match. Audit: 68 marker emissions, zero audited I/O/spawn
  effects or marker fsync/os.write calls. Actual synthetic W1 reader:
  0 ns unattributed across 18 members; fault/clock diagnostics are retained.
- Closure, registration, lint, reader, original Opus witnesses, W1,
  next-arm packet, series end-to-end and chain checks pass. The original
  21-test receipt module reports one error and one failure in a single
  fixture that omits the new series packet. A focused in-memory fixture
  adaptation passes. Production series binding was not weakened.
- Sequential Python 3.13 checks used realpath TMPDIR and `JW_WP22_FULL=1`.
  Top-level tests: 179 executions including the fixture trial, about 4.1
  minutes summed unittest durations. No full suite ran. Compileall over
  `joulewise tests scripts` and diff whitespace checks pass.

Scratch retains `rereview_checks.py`, `fixture_adaptation.py`,
`cross-tree-results.json`, `focused-results.json`, per-module logs and the
normalized synthetic captures. Audit harness SHA-256:
`1a8372d9294fd2d2ddc8ab905440b42b90245e8799fe62146ac8f71f0b8686f3`.
The cross-tree result digest is in the verdict. These are synthetic review
artifacts only; no external user/data path was followed and no network,
model download, block-5 analysis or live collection was performed.

## Handoff

Next exact step: the lead integrates the documented two conflict resolutions,
adds a valid synthetic packet/binding seam to the isolated receipt fixture,
and reruns `tests.align.test_timing_receipts`. Then complete STRICT
re-registration, the full-desk gate and native follow-ups listed in the
verdict before any capture. Native MLX, native observer cost, live turnaround
coverage and R16 integration are not established here. No unresolved policy
or naming question was found. The scratch merge is retained for inspection.
