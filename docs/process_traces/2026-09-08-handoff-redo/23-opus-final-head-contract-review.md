# Opus contract-lens counter-review — final head (298da021), gate rows 6 & 10

Worktree `/Users/edr/code/JouleWise-wt-ref-census-opus2` @ `298da021`, read-only.
Scoped suite green: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog` → **Ran 97 tests … OK** (18.5 s).

## Findings

| id | severity | file:line | defect | demonstrating command |
|---|---|---|---|---|
| F1 | should-fix | `docs/process/MAGISTRATE_WATCHDOG.md:196` vs `scripts/magistrate_watchdog.py:518-533`, `:2286` | The Ed-hands escape hatch is gated on "`state.json` is missing or malformed", but the first tick after the corruption *repairs* `state.json`: `load_state` substitutes `initial_state()` + `state_error` and `tick` writes it back. Five minutes later the doc's own predicate is false and the doc then says the manual `rm` is "not authorized". The only documented recovery for the only remaining stall case becomes unreachable exactly when the watchdog is loaded — i.e. always, at a real handoff. | `python3 scratchpad/ref-opus2/probe_state.py` → `decision: HOLD_UNSAFE corrupt_lock_no_record / lock still present: True / state.json now parses: True / state_error: state.json unreadable…` |
| F2 | nit | `scripts/magistrate_watchdog.py:2257-2272` | The `corrupt_lock_refusal` event is appended on **every** tick with no dedupe (≈288 rows/day while stalled), and `notice_pending` dedupes on `reason` while the ack path (`:1266-1281`) keys on `id`; a churning `pids=[…]` list therefore grows `notice_pending` with repeated `id`s. | `grep -n "corrupt_lock_refusal" -A 14 scripts/magistrate_watchdog.py` |
| F3 | nit (prune, ledger row 8) | `scripts/install_magistrate_watchdog.sh:90-113` | 24 lines re-implement `handoff_process_role`'s daemon/`bg-spare`/`bg-pty-host` classifier inline (own regex, own token sets). Behaviourally equivalent today, but nothing pins the two; this is C5 unclosed and now six times larger. `"$python_bin" "$script_dir/magistrate_watchdog.py" handoff-daemons` is the same gate step 1 already uses and deletes the copy. | `diff <(sed -n '92,112p' scripts/install_magistrate_watchdog.sh) <(sed -n '867,903p' scripts/magistrate_watchdog.py)` |
| F4 | nit | `docs/process/MAGISTRATE_WATCHDOG.md:177` | `original = path.read_bytes()` precedes any existence check, so running the step-4 block with no lock file dies with a raw `FileNotFoundError` traceback instead of a named refusal. | extract block, run with the lock absent |

No blockers.

## Q1 — closure on C1–C4, C7

- **C1 cured, still cured.** `scripts/magistrate_watchdog.py:1014-1017`: `elif previous == "reused_skipped": outcomes[...] = "reused_skipped"` before the `already_gone`/`reused_skipped` fallback. Regression `test_c1_reused_pid_disappears_before_kill`.
- **C3 cured, still cured.** `docs/process/MAGISTRATE_WATCHDOG.md:214-253`: verbatim `read`-prompted PID/start block; each signal revalidates the token (`:239-240`) and the role (`:241-242`), fail-closed with `handoff_twin_token_mismatch` / `handoff_twin_still_present`; `:252` re-runs the daemon gate. Regression `test_c3_documented_twin_stop_revalidates_each_signal`.
- **C4 cured, still cured.** `:162` — "**INTERACTIVE MAGISTRATE / OPERATOR ONLY** … Headless sessions must not execute these recovery commands: [relaunch prompt, line 19](MAGISTRATE_RELAUNCH_PROMPT.md#L19)". Regression `test_c4_lock_recovery_is_interactive_operator_only` asserts all three strings. The prune and B rewrote the same paragraph and did not drop it.
- **C7 cured, still cured.** `:92` — "Before **step 1 executes any pinned file**, verify SHA-256 …", ordered before step 1's `handoff-daemons` call. Regression `test_c7_digest_gate_precedes_first_pinned_execution`.
- **C2 cured per disposition B.** `:162` binds recovery to `state.json`'s `resident_session` ("never the step-3 inventory") and names the four refusal codes; the executable block (`:180-183`) calls `corrupt_lock_refusal(load_state(storage), rows)` for `not valid_lock_pair(lock)` and only then `storage.unlink`. `{torn`, `{}`, `[]` all reach that branch.
- **Ed-hands text scoped to both-unreadable — as written, yes.** `:196` says "only when the lock is unparseable or malformed **and** `state.json` is missing or malformed", and explicitly refuses the readable-state/missing-record case. But see **F1**: the machine erases the qualifying condition within one tick.

## Q2 — safety model across HEAD~4..HEAD

Night path untouched: `git diff HEAD~4 HEAD -- scripts/magistrate_watchdog.py | grep -E "production_census|agent_census|deps\.census|real_dependencies"` returns **nothing**. `production_census()` (`:370-377`) and the in-span `deps.census()` call (`:1279`-region, `decide`) are byte-identical to `d8ad6c15`. The series only added `handoff_census`, a handoff-scoped predicate, and `:257` documents the split explicitly.

Every `unlink` of `magistrate.lock` at HEAD and its guard:

| line | guard |
|---|---|
| `:1397` (decide, corrupt lock) | `corrupt_lock_refusal(state, snapshot) is None` — refuses on missing/malformed record, live recorded pair (defunct row counts as live), any live resumed twin, any live daemon/host/spare |
| `:1407` (decide, valid pair, dead owner) | `owned_process()` is None **and** no live `resumed_twin` row |
| `:1638` (`_finish_child`) | this supervisor's own child returned an exit code |
| `:1722` (stand-down verify) | `owner_gone` from `child.poll()` or `owned_process()` |
| `:2028` (`start_session_guarded`) | spawn raised; the lock was seeded by this process microseconds earlier |
| `:2181` (`adopt_recorded_session_for_drain`) | `valid_lock_pair(current_lock)` (`:2141`), recorded pair absent (`:2153`), no live resumed twin (`:2155-2159`), **and** `current_lock == lock_record` exactly (`:2180`) |
| doc `:191` (operator) | service lock held, corrupt→`corrupt_lock_refusal` / valid→`handoff_census`+`handoff_refusals`, plus a re-read byte-equality check (`:189`) |

No new path unlinks while a possible owner is alive. The `:2141` guard is the load-bearing addition: without it a plan-conflict `HOLD_UNSAFE` reaches the drain path ahead of the corrupt-lock branch and clears `resident_session`, destroying the durable record B depends on. Mutation probe (guard deleted, `git archive` copy): **33 failures + 3 errors** — the branch is covered, not decorative.

## Q3 — spec vs test at HEAD

`test_corrupt_lock_tick_matrix_binds_durable_resident` (tests/test_magistrate_watchdog.py:1510) and `test_corrupt_lock_documented_matrix_binds_durable_resident` (`:1543`) run the same 3×20 matrix — raw bytes `{torn`/`{}`/`[]` × {live pair, absent record, gone, reused PID, twin, three daemon shapes, defunct row, eight bad-field records, three malformed records} — through **real `wd.tick`** and through the **doc block extracted by marker** (`recovery_block`, `:1481-1486`) executed with `exec(compile(...))`. `test_corrupt_lock_cli_refusal_survives_unreadable_state_and_repeated_hold` (cli:81) adds unreadable/torn `state.json` and a pre-existing `HOLD_UNSAFE`, twice, through `wd.main(["tick", …])`.

No self-declared fixture in the B mechanism: the only stubs are the process table, clock, and `os.fork`; the classifier, `corrupt_lock_refusal`, `tick`, and the operator block are production code and production text. (C6's shadow `reap_handoff` is untouched by this series and unrelated to B.) The assertions cover the promised behaviour on all four axes: state, `launch`, lock bytes preserved, `resident_session` preserved, event, and notice.

## Q4 — doc-as-executable

Extraction under the doc's contract (`scratchpad/ref-opus2/extract.py`): 11 ```zsh``` blocks, all `zsh -n` **OK**; 6 `<<'PY'` heredocs, all `compile()` **OK** — including the step-4 reconciliation block (26 lines, `from scripts.magistrate_watchdog import (`) and the reaper (28 lines, `import os`, extracted between `watchdog_checkout=` and three-space `   PY`). Install-handoff ordinals: `0,1,2,3,4,5,6` — unique and ordered (the earlier `1..5` are the separate "Fence and deadlines" list). Every operator instruction is a verbatim command: step 1 `handoff-daemons` ×2 (`:122,:125`), step 3 `handoff-inventory` (`:148-152`), step 4 install + block (`:158-159`, `:166-193`), Ed-hands `handoff-inventory`/`ps`/`rm` (`:200-201`, `:207`), twin stop (`:216-252`). WHO is present and cited: `:162` "INTERACTIVE MAGISTRATE / OPERATOR ONLY … [relaunch prompt, line 19](MAGISTRATE_RELAUNCH_PROMPT.md#L19)", and `:196` "Ed must run these verbatim commands from an observer Terminal".

## Q5 — overbuild / merge-ability

Only **F3** (installer classifier copy, `install_magistrate_watchdog.sh:90-113`). No dead code: `valid_lock_pair`, `corrupt_lock_refusal`, and the `:2141` guard are each mutation-covered. No test asserts implementation detail — the two doc-substring assertions (`test_c4_…`, `test_c7_…`) assert the operator contract, which is the doc. The 7a18fddc prune already removed the inventory mechanism the delta re-audit rejected; nothing of it survives.

## Q6 — merge / next-handoff blockers

None. Suite green, night census untouched, no unguarded unlink. **F1 must be fixed before the next real handoff** — it is a two-sentence doc edit (add "or `state.json` carries `state_error`" to the `:196` predicate, and a verbatim `python3 -m json.tool "$HOME/night-custody/magistrate/state.json"` for the operator to make the determination), not a code change, and it is the difference between a documented last-resort recovery and a stall with no authorized exit.

**Verdict: LAND-WITH-FIXES — F1 (doc predicate at `:196`) before merge; F2, F3, F4 optional.**
