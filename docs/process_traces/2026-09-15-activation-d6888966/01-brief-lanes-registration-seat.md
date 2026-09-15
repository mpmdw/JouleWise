# Seat brief — register two kernel lanes (WATCHDOG-STALE-EXIT-CLASS-01, FIXTURE-FAKE-VLLM-LEAK-01)

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json","tests/test_gen_state.py","TASK_QUEUE.md","RUN_STATE.md"]

Worktree `/Users/edr/code/JouleWise-wt-lanes-d6888966`, branch `chore/2026-09-15-lanes-d6888966` at `17c80571` (origin/main). Do NOT commit (the lead commits by pathspec). Never touch `/Users/edr/code/JouleWise` (frozen canonical root), any other worktree, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, or `/Users/edr/night-custody`. No network. `RUN_STATE.md` and `TASK_QUEUE.md` may be changed ONLY inside their generator-owned marker fences (`<!-- BEGIN GENERATED: state-kernel ... -->` … `<!-- END GENERATED ... -->`) and only by running `python3 scripts/gen_state.py`; hand-edit nothing else in those two files.

## Task
Register two new tasks in `docs/process/state_kernel.json` in the exact shape of the most recent registration (`git show 03f324b2 -- docs/process/state_kernel.json tests/test_gen_state.py`, task `PACK-ROOT-SUCCESSOR-V5-01`), regenerate the fenced regions with `python3 scripts/gen_state.py`, prove `python3 scripts/gen_state.py --check` exits 0, and update the row-count assertion in `tests/test_gen_state.py` (currently 170; the comment convention records date, activation, and the arithmetic: 170 + 2 = 172). Run `python3 -m unittest tests.test_gen_state` and paste the result. Ranks: next free ranks after 196 (197, 198). Lane `agent`. Status `queued`. Both are registrations by the magistrate, not rulings (say so in `authority.label`, as the PACK-ROOT row does).

### Lane 1 — WATCHDOG-STALE-EXIT-CLASS-01 (priority `p3_hardening_candidates`)
Goal: `scripts/magistrate_watchdog.py`'s clean-exit path (the `exit_class == "clean"` branch in the child-finish handler, ~line 1655) resets the backoff indices and sets a fixed 300 s cooldown but never resets `state["last_exit_class"]`; the launch-predicate path (~line 1447) then labels that cooldown `BACKOFF_USAGE` whenever the stale field still reads `usage_exhausted`, and `state.json` shows `last_exit_class: usage_exhausted` after every clean exit. Two magistrate activations on 2026-09-15 (decae362, d6888966) read that field as "the previous activation exited on usage" when both prior exits were exit 0 with `stop_reason end_turn` (events.jsonl sequences 132/136 `clean activation exit`; the last real usage exit is sequence 37, 2026-09-09).
Acceptance summary: the clean-exit branch sets `last_exit_class` to `"clean"` (or the launch predicate keys the waiting-state label on the exit that set the deadline, not on a stale field); a regression drives one real usage exit followed by one clean exit through the handler and asserts `state.json` reads `last_exit_class == "clean"` and the waiting transition is `BACKOFF`, not `BACKOFF_USAGE`; the existing `classify_exit` tests unchanged; lands under the twelve-row gate; not night-critical; no change to the 300 s cooldown or to the usage ladder.
Evidence entries: `docs/process_traces/2026-09-15-activation-d6888966/00-launch-record.md` (section "Correction 06:50 PDT"); `scripts/magistrate_watchdog.py` clean-exit branch and launch predicate (cite the line numbers you read); `/Users/edr/night-custody/magistrate/events.jsonl` sequences 132–137 (cite by sequence; do not copy the file).
Authority: 2026-09-15 activation d6888966 record 00 correction (registration by the magistrate, not a ruling).

### Lane 2 — FIXTURE-FAKE-VLLM-LEAK-01 (priority `p3_hardening_candidates`)
Goal: `tests/test_node_worker_subprocess.py` writes a fake `vllm` server into a temp venv (`_write_fake_vllm`, ~line 375) and starts it as a subprocess; on some exit path the server is not reaped, and 35 orphaned `python … /var/folders/…/T/tmp*/bin/vllm serve /fake/model … --served-model-name nv5-fake-model` processes (parent pid 1, 0 % CPU, launched 2026-09-03 … 09-05 per `ps -o lstart`) have accumulated on Ed's machine. They are not in the agent census (python, not claude/codex/t3) but hold memory and ports. Sibling of REPLAY-FIXTURE-LEAK-01 (which covers the replay runner's fixtures); do not merge the two rows — this one names a different fixture and file.
Acceptance summary: the fixture's teardown terminates the fake server on every exit path (addCleanup/finally, SIGKILL fallback after a bounded wait); an interrupted-test regression starts the fixture, aborts mid-test, and proves no survivor by pid; the module's tests pass; the orphan cull itself is Ed's call (recorded as a separate `ed_external` note in `status_note`, not an acceptance clause); not night-critical.
Evidence entries: `docs/process_traces/2026-09-15-activation-decae362/00-launch-record.md` ("35 orphaned test-fixture processes" and "Follow-up"); `tests/test_node_worker_subprocess.py` `_write_fake_vllm` and the kill path (~line 316) — cite what you read; `docs/process_traces/2026-09-15-activation-d6888966/00-launch-record.md` (State found).
Authority: 2026-09-15 activation decae362 record 00 Follow-up + d6888966 registration (magistrate registration, not a ruling).

## Verification you must run and paste
1. `python3 scripts/gen_state.py` then `python3 scripts/gen_state.py --check; echo rc=$?` (must be 0).
2. `python3 -m unittest tests.test_gen_state 2>&1 | tail -3`.
3. `git status --short` (only the four in-scope paths may appear) and `git diff --stat`.

## Report
Final message in the claude-codex-report/v1 envelope: changed files, the two new ranks, the test tail, and any conflict with the registration shape you found (do not guess field values; if the schema rejects a field, report the validator message and stop).
