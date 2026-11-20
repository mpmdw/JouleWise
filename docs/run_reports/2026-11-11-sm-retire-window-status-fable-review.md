# Fable cold review: `sm-retire-window-status` (audit Q8, second half)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 05:05 PST. Reviewed head `60827f653`
(`docs/2026-11-11-sm-retire-window-status`, base `origin/main` `a6c0e6be0`). Builder: Sol xhigh.

**Verdict: ADMIT.** Three follow-ups are the orchestrator's and are listed below.

## What the PR does, on `main` only

- Deletes `WINDOW_STATUS.md` (stale since 2026-08-24), its publisher `scripts/window_status.sh`, and
  `tests/test_window_status_guard.py` with its one line in `scripts/test_timings.json`.
- Replaces the instructions that told agents to run the publisher, in `docs/process/MAGISTRATE_WATCHDOG.md`,
  `docs/process/NIGHT_HANDBACK.md` and `docs/contracts/window_liveness.md`, with `docs/process/CURRENT.json`
  and `docs/process/POINTER_RULE.md`. The liveness helper and its contract stay.
- `docs/ARCHIVE.md` says how to get the three removed files back from the base commit.
- `tests/test_custody_isolation_guard.py` no longer lists the removed test module.

## Is the publisher installed or bound anywhere?

- `main`: no launchd template, installer, workflow or script calls it (the seat's census, which I spot-checked).
- W1 line: `scripts/window_status.sh` is not in the v4 `ARTIFACTS`, not in the registration receipt, in no
  launchd template and not in the magistrate relaunch prompt (my check). The W1 line is left alone.
- Not checked: whether an untracked copy is installed on a host. Repository evidence cannot show that.
- `configs/campaigns/v5_claim_25g83/sealed_inventory.json` still lists the publisher. It records what Block 5
  sealed and is not edited (RL-51).

## What I ran on the Air

- `python3.13 -B scripts/gen_state.py --check`: exit 0.
- `tests.test_gen_state`, `tests.test_gen_current`, `tests.test_custody_isolation_guard`,
  `tests.test_docs_freshness`: 130 tests, OK.
- `python3.13 -B scripts/repin.py --check`: `PASS 16 pin families current`. The pin registry's rows for the
  publisher are era rows against a commit and still verify.
- Read every edited line of the three process documents.

## Follow-ups for the orchestrator

- **R-1.** The state kernel still has the task `WINDOW-STATUS-GUARD-CENSUS-01` and its generated queue rows.
  The kernel is the orchestrator's file.
- **R-2.** `docs/site/readme.html` and `docs/site/run_state.html` are generated and still mention the old
  file; they refresh at the next site build.
- **R-3.** Unrelated, found while checking for leaked test processes: four orphaned `b5-fake-km003c-meter`
  fixture processes have been running on the Air since 2026-11-08 (pids 43565, 43949, 86819, 90602, parent 1).
  No process from this lane's seats is leaked. They are a likely cause of the four native process-table test
  failures seen on this machine in `tests.test_post_window_unstrand`.
