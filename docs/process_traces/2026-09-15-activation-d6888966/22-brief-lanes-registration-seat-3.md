# Seat brief — register WATCHDOG-CLI-TEST-TMP-DISCOVERY-01 and note the GAMMA merge on PACK-ROOT-SUCCESSOR-V5-01

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json","tests/test_gen_state.py","TASK_QUEUE.md","RUN_STATE.md"]

Worktree `/Users/edr/code/JouleWise-wt-lanes-d6888966`, branch `chore/2026-09-15-lanes-d6888966` at origin/main (cite `git rev-parse --short HEAD`). Do NOT commit. Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. `RUN_STATE.md`/`TASK_QUEUE.md` change ONLY inside the generator-owned fences via `python3 scripts/gen_state.py`.

## Task 1 — register WATCHDOG-CLI-TEST-TMP-DISCOVERY-01 (rank 201, lane `agent`, status `queued`, priority `p3_hardening_candidates`)
Shape: same as this morning's rows (`git show ee6065f8 -- docs/process/state_kernel.json tests/test_gen_state.py`). Row count 174 + 1 = 175 with the dated comment convention.
Goal: `scripts/magistrate_watchdog.py:259` discovers night plans with `self.root.parent.glob("*/night_plan.json")` — the PARENT of the custody root. `tests/test_magistrate_watchdog_cli.py` (`HandoffCliDefectTests.test_corrupt_lock_cli_refusal_survives_unreadable_state_and_repeated_hold`, ~line 82) passes `--custody-root <TemporaryDirectory>`, whose parent is `/private/tmp`, so any stale `/tmp/*/night_plan.json` fixture left by another session makes the tick go `HOLD_UNSAFE` (`night_plan_malformed … authored_epoch_s is in the future` against the harness's fixed 2026-09-04 clock) before the corrupt-lock notice is appended; twelve subtests fail at the bench while CI's clean runner passes. Seen 2026-09-15 on the PR #339 replay (record 19); the same module fails identically on clean main at that bench.
Acceptance summary: every watchdog CLI/harness test nests its custody root at least one level below its temporary directory (e.g. `<tmp>/custody/magistrate`) so discovery sees only fixtures the test authored; a regression plants a foreign `<tmp-parent>/*/night_plan.json` sibling and proves the test's tick ignores it; `tests.test_magistrate_watchdog_cli` and `tests.test_magistrate_watchdog` pass at the bench with a deliberately planted stale plan under `/tmp`; no change to production discovery semantics (the parent-directory glob is the production contract for `~/night-custody/<plan>/`).
Evidence: `docs/process_traces/2026-09-15-activation-d6888966/19-gamma-replay-804eb394.md` (section "The one red module, diagnosed at the bench"); `scripts/magistrate_watchdog.py:259`; `tests/test_magistrate_watchdog_cli.py` (cite the line of `--custody-root`).
Authority: 2026-09-15 activation d6888966 record 19 (magistrate registration from a bench replay finding; not a ruling). Sibling lanes: REPLAY-FIXTURE-LEAK-01, FIXTURE-FAKE-VLLM-LEAK-01 (stale fixture residue); do not merge rows.

## Task 2 — PACK-ROOT-SUCCESSOR-V5-01 status_note
Append (do not rewrite) to that row's `status_note`: " 2026-09-15 (activation d6888966): the GAMMA root-key repair MERGED as PR #339 (merge commit on main; records 11–20 under docs/process_traces/2026-09-15-activation-d6888966/); the scout's Q2/Q5 replays remain to run in a writable checkout; production pack generation still waits for the issued G2-a pin."

## Verification to paste
`python3 scripts/gen_state.py && python3 scripts/gen_state.py --check; echo rc=$?`; `python3 -m unittest tests.test_gen_state 2>&1 | tail -3`; `git status --short`; `git diff --stat`.

## Report
claude-codex-report/v1 envelope: changed files, the rank, tails; NEEDS_RULING on any schema conflict.
