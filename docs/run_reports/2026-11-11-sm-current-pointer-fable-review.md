# Fable cold review: `sm-current-pointer` (audit section 8.2 item 4, Q7, part of Q8)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 03:56 PST. Reviewed head `0bf70db8a` (round 2) plus my
own hook commit `d5ec72ecf` on `feat/2026-11-11-sm-current-pointer`, base `origin/main`. Builder: Sol xhigh, two
rounds. Round 1 built a hand-bumped pointer; the orchestrator asked for a generated one, and round 2 replaced it.

**Verdict: ADMIT.** Two items are left to the orchestrator and listed below; none blocks the merge.

## What the PR does

- A RUN_STATE item may carry a fenced `pointer` block directly under its heading: owner, the armed plan with its
  host, t0 and latest end, a wait from a closed list, a deadline, a refusal branch and the next observable.
- `scripts/gen_current.py` renders `docs/process/CURRENT.json` from the highest-numbered item that carries a
  block, and records that item as `source_item` with the date in its heading. Items without a block are ignored,
  so an ordinary RUN_STATE commit needs no generator run.
- `scripts/gen_state.py` now generates and checks the file on the live RUN_STATE (my commit). CI already runs
  `gen_state.py --check`.
- No item carries a block today, so the committed file is the "no pointer" document and the check passes.

## What I did

- Read all of `scripts/gen_current.py` (302 lines), the test list, `POINTER_RULE.md` and the doc edits.
- Ran `tests.test_gen_current` (49 tests with my three hook tests) and `tests.test_gen_state` (44): OK, with the
  default temp directory.
- End to end on a scratch copy: added a block under item 261, `gen_state.py --check` returned 1 with the drift
  message, `gen_state.py` regenerated, `--check` returned 0, `gen_current.py --show` printed the one-line form
  with `t0=1794372780`. Restored the files afterwards.
- Mutation-tested ten points of the generator and two of the hook: twelve killed.

| Mutant | Killed |
|---|---|
| first block wins, not the highest item | yes |
| any `wait` word accepted | yes |
| deadline before latest end accepted | yes |
| time without an offset accepted | yes |
| drift not reported | yes |
| a block not directly under a heading accepted | yes |
| duplicate key accepted | yes |
| implausible epoch accepted | yes |
| second block in one item accepted | yes |
| other code fences not skipped | yes |
| hook: pointer drift dropped from the exit code | yes |
| hook: fixture runs touch the live pointer | yes |

## Findings

- **P-1 (for the orchestrator).** `WINDOW_STATUS.md` is not retired. Round 1 deleted it; round 2 restored it
  unchanged because `scripts/window_status.sh` rewrites it and three process documents still tell agents to run
  that script (`docs/process/MAGISTRATE_WATCHDOG.md:10`, `docs/process/NIGHT_HANDBACK.md:29`,
  `docs/contracts/window_liveness.md:739`). Deleting only the file would be undone by the next run. Retiring it
  means removing the publisher, its test and those three instructions together. That is Q8's remaining half and
  a separate small PR.
- **P-2 (informational).** The heading pattern also matches a numbered sub-list line that starts with bold text
  (`1. **Yes: ...`). A block placed under such a line would be attributed to item "1" and lose to any real
  item. The rule document says the block goes under the item heading; nothing else is needed now.
- **P-3 (for the orchestrator).** Nothing reads `deadline` yet. The Air watcher that alarms when it passes is
  the wave-2 seat `sm-air-watch`. Until it lands, a stale pointer is visible only through `source_item`.

## Not covered

- Python 3.11 was not run locally; CI runs it.
- The kernel's `authority` string is unchanged; that edit is the orchestrator's.
