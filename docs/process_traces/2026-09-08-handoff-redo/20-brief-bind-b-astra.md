WRITE_SCOPE: ["scripts/magistrate_watchdog.py","docs/process/MAGISTRATE_WATCHDOG.md","tests/test_magistrate_watchdog.py","tests/test_magistrate_watchdog_cli.py"]

# Seat brief — disposition B: bind corrupt-lock recovery to the durable `resident_session` record (gpt-6-astra, high)

HEAD = 7a18fddc on branch feat/2026-09-08-watchdog-census-daemon (landing 898e5305 → fix round b3eeee9a → prune
7a18fddc which restored the fail-closed doc-block refusal for corrupt locks). A rule-11 cold gate ruled on the
corrupt-lock question; its ruling is binding and is quoted here in full for the mechanism (read it twice):

> Third disposition, call it B (bind): revert the exhibit-B inventory mechanism [done in 7a18fddc]; in both the
> tick's dead-lock branch and the step-4 block, treat `read_lock() == {}` as "consult `state["resident_session"]`",
> refuse if that pair is live, if any resumed twin is live, if any daemon is live, or if the record is absent or
> malformed; unlink only when the pair is provably absent. Regression: the tick matrix (headless resident live,
> corrupt lock, populated `resident_session` → HOLD, lock kept; record absent → HOLD, lock kept; pair gone →
> unlink). Document Ed-hands recovery only for the both-unreadable case.
> Finding 2: "The watchdog's own tick already refuses to launch on an invalid lock" is FALSE at 898e5305,
> b3eeee9a and main. `read_lock` maps corrupt bytes to `{}`; `owned_process({} …)` returns None; the tick treats
> that as a dead owner and unlinks unless a `--resume --reply-on-resume` interactive twin is visible
> (898e5305:1359-1367). The watchdog spawns exactly a headless `claude -p` session (`session_argv`), so corrupt
> lock plus a resident whose supervisor died equals: next tick unlinks, launches a second resident. Fix the tick's
> own corrupt-lock unlink FIRST.
> Finding 4: `state.json` carries `resident_session` in the lock schema with PID, start token and activation
> (b3eeee9a:2099-2107 already uses it for drain adoption). Recovery bound to that record needs no classifier:
> pair live → refuse; pair absent, no twin, no daemon → owner proven gone, unlink; `resident_session` missing or
> malformed → fail closed. The doc block takes the same record, never a step-3 inventory.

## Deliverables
1. `scripts/magistrate_watchdog.py`: in the tick's dead-lock branch (`decide`, the `HOLD_UNSAFE
   dead_lock_resumed_twin` region) and wherever else a `{}`/unparseable lock is currently treated as a dead owner:
   consult `state["resident_session"]`; if the (pid, start_time) pair is live → HOLD (named refusal, e.g.
   `HOLD_UNSAFE corrupt_lock_resident_live`), lock kept; if any resumed twin or daemon shape is live → HOLD, lock
   kept; if the record is absent/malformed → HOLD (`corrupt_lock_no_record`), lock kept; only when the pair is
   provably absent (pid absent, or present with a different start token) and no twin/daemon → unlink and proceed.
   Keep a VALID lock's existing semantics untouched. Emit a transition/event so the refusal is visible in
   events.jsonl and the next launch notice.
2. `docs/process/MAGISTRATE_WATCHDOG.md` step-4 reconciliation block: same rule, same record, verbatim commands;
   Ed-hands recovery text ONLY for the both-unreadable case (lock unparseable AND state.json missing/malformed).
   Keep the extraction contract (`watchdog_checkout=` … `   PY`, three-space indent), `zsh -n` + `compile()`.
3. Regressions (write first; each must FAIL on 7a18fddc and pass after; name the counterfactual in the docstring):
   the cold gate's tick matrix — (a) corrupt lock + populated resident_session whose pair is live (a `claude -p`
   resident shape) → HOLD, lock kept; (b) corrupt lock + record absent → HOLD, lock kept; (c) corrupt lock + pair
   gone (pid absent) → unlink; (d) corrupt lock + pair gone but a resumed twin live → HOLD; (e) same for the
   documented step-4 block via its extraction. Try all three corrupt forms `{torn`, `{}`, `[]`.
4. Report body: exact counterfactuals, fail-before/pass-after tails, acceptance = the FOUR scoped modules
   `python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog`
   to a log with rc (never the repository-wide suite). Explicit design disagreement with the ruling is welcome in
   a section of its own, but implement the ruling as written unless it is impossible (then NEEDS_RULING).
No `git commit`. Header < 8192 bytes; genre implementation verdict keys.
