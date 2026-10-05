# Seat: the block-4 joined producer-to-harvest replay on a frozen throwaway clone (addendum C item 6)

You are a headless Claude Opus 5.5 seat. This is one non-interactive session, and every command runs in the foreground. Anything longer than 9 minutes is split, or launched with `python3 -c 'import subprocess,sys; subprocess.Popen(sys.argv[1:], stdout=open(LOG,"w"), stderr=subprocess.STDOUT, start_new_session=True)'` and polled in loops of at most 9 minutes. No subagents, and no background work left running at the end. Ending before `/Users/edr/night-archive/desk-day-v5/joined-replay/REPORT.md` exists is a protocol failure. Wall budget: 3 hours. If you are not finished by then, write REPORT.md with status IN_PROGRESS and the exact next step.

## Hard rules

- No sudo, launchctl, powermetrics or systemsetup.
- Never arm or launch a real window, never consume a real launch capability, never run a window chain against the real machine state.
- Never write:
  - under /Users/edr/night-g2a, /Users/edr/night-custody or /Users/edr/night-archive (except /Users/edr/night-archive/desk-day-v5/joined-replay/);
  - in /Users/edr/code/JouleWise or in any existing worktree.
- Push nothing. No `git fetch` in /Users/edr/code/JouleWise.
- Do not read RUN_STATE.md, CLAUDE.local.md or memory files.
- Never print or record a measured energy or power value.
- Work only in fresh clones under /tmp/dd5-joined/: `git clone --no-local /Users/edr/code/JouleWise /tmp/dd5-joined/<name>`, then `git -C /tmp/dd5-joined/<name> checkout --detach <HEAD>`, where HEAD is given below.
- Python: /Users/edr/code/JouleWise/.venv/bin/python.

## Head

HEAD = `__HEAD__`, the PR #483 integration head (block-4 qualification code, lanes X1-X10, with main merged).

## Step 1: freeze the three `_v5` packs in the clone

Follow `/Users/edr/night-archive/desk-day-v5/clone-proof2/REPORT.md`, section "Exact commands to rerun at the final claim head", steps 1-4:
- anchors and generator `--check`s;
- the U11 projection, one pack per commit;
- the pre-author tests;
- evidence authoring and its commit;
- the sacrificial screen, then the primary `freeze-0004` for all three packs and its commit.

Set `refs/remotes/origin/main` locally as that REPORT does. Steps 5-6 (the successor pinset, the family marker, arm) follow only if the joined replay needs them; say which.

## Step 2: implement and run the joined replay on the frozen GAMMA pack

`tests/test_v5_block4_replay.py::CommittedGammaJoinedReplayTests` holds four skipped tests:
- `test_joined_success_qualification_and_structural_pass`;
- `test_joined_observation_exception_preserves_chain_rc_and_structural_verdict`;
- the `recover_no_science` variant;
- the agent-present variant.

Each stops at `joined_stop()` because GAMMA had no freeze authority. With the frozen clone, implement them in the clone, as specified in brief 86 (`/Users/edr/code/JouleWise-wt-dd5-records/docs/process_traces/2026-10-04-desk-day-v5/86-sol-b4-replay-brief.md`). Each is ONE complete desk occurrence chain: a1, a2, the G10 control, then s1. Mock only the physical seams, each labelled with the seam it replaces:
- sudo and systemsetup;
- the powermetrics sampler;
- model inference;
- ioreg battery reads;
- the HID idle read;
- the sntp collector;
- wall and monotonic clocks;
- launchctl.

Everything else runs the real code:
- `scripts/write_v5_qualification_plan.py` (a1, a2, s1, with the `previous_attempt: none` history field);
- the ARM-only path and `scripts/check_v5_arm_abort.py`;
- the G10 helper's `run` with its preflight;
- the s1 driver under the observation producer, as the installed job invokes it, including the native T-0 stage with the T-0 dwell;
- `scripts/v5_s1_desk_closeout.py`;
- the qualification assembly and `scripts/harvest_v5_qualification.py`;
- `scripts/harvest_v5_g2b_window.py`.

**G1, G3, G5, G8 and G9 must PASS on native output**, and both verdicts must PASS on the success chain. Add two more variants:
- a NULL `s1` (refused before `chain.started`), then the NULL restore (`scripts/restore_v5_null_reservation.py`), then a fresh `s1` whose history chain and census pass;
- one admission abort, then a fresh `s1`, then the allowance spent; a second abort refuses as the same refusal twice.

Where the real code cannot run on desk inputs without a physical seam you have not listed, stop that step. FLAG it with file:line rather than stubbing non-physical semantics: no ARM, plan-loader, evaluator or harvester shortcuts. If you find a real defect, do not fix production code. Record it with a minimal reproducer.

## Report

`/Users/edr/night-archive/desk-day-v5/joined-replay/REPORT.md`. The first line is `JOINED REPLAY: PASS`, `JOINED REPLAY: FINDINGS` or `JOINED REPLAY: IN_PROGRESS`. Then:
- a step table (step, command, rc, outcome, expected?);
- per variant, the gates and verdicts reached;
- the findings with file:line and a reproducer;
- the final test file. Copy it to `/Users/edr/night-archive/desk-day-v5/joined-replay/test_v5_block4_replay.py`, so the lead can land it on the integration branch.
