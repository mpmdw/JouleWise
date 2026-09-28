# N1 fix round 2b — report

Seat: an Opus 5.5 agent that ran outside the codex sandbox, 2026-09-28. Worktree `/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2`, branch `feat/2026-09-28-ntp-n1`, head `c8995f4b` (it did not move). **No git writes.** The lead commits.

Authority: addendum A1 (record 38) §4.2, §4.6, §4.7, §5 and §7; the lead's ruling in item 118 of the activation record.

**Result.** All three defects are fixed. Every module in scope passes with zero failures. Every regression that A1 §4.7 requires to fail on `3ad82b43` fails there by assertion. Every red-by-deletion case turns its named test red by assertion. One caveat: deleting P1 **inside the proof alone** does not turn the driver-side same-group case red, because an earlier check covers that case (details in table (b)). No stop condition was met.

## Words used

- **Proof**: the check that no capture process is still running, `_prove_capture_absent` in `scripts/run_night.py`. It has three checks. **P1**: the chain's own process group is empty. **P2**: every group listed in the night's registry file (`evidence_processes.jsonl`) is empty. **P3**: one listing of every process on the machine (a "sweep"), in which no command line may name the sampler or a path of the night.
- **Pass**: one run of P1, then P2, then P3. A pass stops at the first check that fails.
- **Census**: one `pgrep -g` listing of a process group, with a timeout. A census that times out counts as "not proved".
- **Marker**: the file that says network-time ON is still owed. The driver's OFF step creates it, and the proof reads the night's paths from it.
- **The two records**: `night/result.json` (the night's verdict and `aborted_reason`) and `night/refusal.json` (the driver's refusal document, with `reason` and `evidence`).
- **Stop**: the driver ending the chain itself, either at the wall-clock deadline (a watchdog thread does this) or when the agent census finds an agent session running.

## E1 — the last pass ran its checks with a starved timeout

**Cause.** The retry loop gave each check `min(1 s, time left in the 5 s window)`, and never less than 0.01 s. The loop ran until the window ended, so its last pass started with almost no time left. That pass's P1 census timed out after about 0.01 s ("census_failed: TimeoutExpired"), and its P1 evidence replaced the evidence of the check that had really failed. Executed on `c8995f4b` with this round's regression: expected P3 evidence, got `'P1' != 'P3'`. The seven live tests failed the same way.

**Fix.** `scripts/run_night.py`:

- `:3899` `CAPTURE_CHECK_TIMEOUT_S = 1.0`. Every timed listing in a pass gets this whole timeout, never whatever is left of the window.
- `:3902` `_capture_pass_calls(groups)`. It counts the worst-case number of timed listings in one pass: one for P1, one for P3, and for P2 either none (no registered groups), one (one group), or two per batch of 256 groups (one census and one `ps` call to attribute pids).
- `:3913` `_capture_proof_pass`. One complete pass, factored out of the loop.
- `:3939` `_prove_capture_absent`. The first pass always runs. After a failed pass, another pass starts only if the pause plus that pass's worst case still ends inside `GROUP_CENSUS_WINDOW_S`. Otherwise the proof returns the evidence of the last complete pass, now with a `passes` count. A census that really times out inside a pass is that pass's "not proved". An exception in a check still ends the proof at once, as before.

**Bound.** The proof takes at most max(`GROUP_CENSUS_WINDOW_S`, the worst case of the first pass), plus the time to reap a listing that timed out. With production constants and up to 256 registered groups, that is **5 s**: the worst pass is 4 × 1 s. The proof runs twice per night (before the query and again before ON), so the total is at most 10 s.

**Trade-off for the lead to weigh.** Because a pass may not start unless it can finish, retries in a night **with** a registry can start only in the first ≈0.8 s of the window (5 − 0.2 − 4). In a night **without** one they can start in the first ≈2.8 s. Before this fix, retries ran for the whole 5 s, but with starved timeouts. A shorter retry span can only make the driver refuse more often. It cannot let the query or ON run beside a capture.

**Regressions** (`tests/test_run_night.py`):

- `:1452` `test_capture_proof_never_starves_a_check_and_keeps_the_failing_check`: real 5 s window; P1 proves, P3 keeps matching. It asserts that every census and sweep got exactly 1.0 s, that the evidence is P3 with the matching pid, and that the proof took no more than 5.5 s. On `c8995f4b` it fails by assertion (`'P1' != 'P3'`).
- `:1486` `test_capture_proof_that_times_out_is_not_proved_and_stays_bounded`: a census that spends its whole timeout is "not proved" (P1, "TimeoutExpired after 0.2 seconds"), and the proof ends within its 1 s window.
- The seven live tests that expect P2 or P3 now get the right label.

## E2 — result.json and refusal.json named different causes

**Cause.** At the deadline, the watchdog writes `refusal.json` itself, as `night_window_exceeded`. It does this so that a main loop blocked for ever still leaves a record. Refusal documents are created exclusively, so when the proof later failed, the result step could not write `refusal.json` again: it wrote `refusal-01.json` (`night_chain_alive`) and `result.json` (REFUSED / `night_chain_alive`). Executed on `c8995f4b`: `refusal.json` said `night_window_exceeded`, `refusal-01.json` said `night_chain_alive` with `{"check": "P3", "error": "restore marker unreadable"}`, and `result.json` said REFUSED / `night_chain_alive`.

**Fix** (lead's ruling under A1 §4.2). `scripts/run_night.py`:

- `:3511` `_capture_unproved_abort`. When the proof fails, before the query or before ON, the night's cause becomes `night_chain_alive`. Its evidence is the proof's evidence plus `prior_abort`, which holds the earlier stop's `reason`, `detail`, `evidence` and `document` name. If the earlier cause is already on disk (the watchdog's document), that document is **superseded in place**. The new mapping carries `document`, so the result step writes no second copy.
- `:296` and `:334` `_write_driver_refusal(..., supersede=True)`. It writes the new document exclusively to a temporary name, then `os.replace`s it over the existing one. That is atomic, and it is the only exception to "refusal documents are immutable". It is used only here.
- Call sites: `:3359` (before the query) and `:3374` (before ON).
- If the supersede itself fails, a log line is written and the result step writes a fresh `night_chain_alive` document, so `result.json` still names the right cause.
- The agent-census stop had no document on disk, so it now writes `refusal.json` as `night_chain_alive` with `prior_abort` = `night_aborted_agent_present`.

The query does not run, ON does not run, and the marker stays, exactly as before. The exit status is `EXIT_REFUSED` (3), as before.

**Regression.** `:1186` `_assert_one_chain_alive_cause`. It reads **both** records and asserts: `result.json` says REFUSED / `night_chain_alive`; `refusal.json` says REFUSED / `night_chain_alive`, with `prior_abort.reason` equal to the stop's reason and `prior_abort.evidence` present; `refusal.json` is the only refusal document; and `result.json`'s `refusal_documents` lists only it. T4 uses it for both stops: `:1245` deadline (prior `night_window_exceeded`) and `:1242` agent census (prior `night_aborted_agent_present`). T4's essential assertions stay: events exactly `["off"]` (no query, no ON), marker kept, the child alive with parent 1. On `c8995f4b`, T4-deadline fails by assertion (`'night_window_exceeded' != 'night_chain_alive'`).

## E3 — four deadline tests failed after a proven kill

**Cause: the test fixture only; no code defect.** The module-level stand-in for network-time OFF returned a receipt but did not create the marker, and `RESTORE_PENDING_PATH` still pointed at the real path in the home directory, where no marker exists. After a proven kill, the proof read no marker and refused with `{"check": "P3", "error": "restore marker unreadable"}`. Executed on `c8995f4b` with its own test file: `result.json` said REFUSED / `night_chain_alive`, and `refusal-01.json` carried exactly that evidence. With only the fixture fixed, all four tests **pass on the unchanged `c8995f4b` code**. That confirms the cause.

**Fix** (`tests/test_run_night.py`):

- `:54` `_fixture_network_time_off`. It creates the marker with production's `network_time_window.create_restore_marker`, passing along whatever night paths the driver gives (on `3ad82b43` the driver passes none, and the stand-in still works). The module's recovery stand-in answers "nothing_pending", which models a clean machine, so a marker left by an earlier test is removed first.
- `:72` `_fixture_network_time_on`. A successful ON removes the marker, as production does.
- `:79` `setUpModule`. It points `RESTORE_PENDING_PATH` at a temporary directory for the whole module, so no stand-in can read or write the machine's real marker.

No assertion was changed. A clean chain, and a chain whose group was killed and proved empty with no capture process alive, again reach GO or ABORTED exactly as on `3ad82b43`. All four tests also pass on `3ad82b43` with the new fixture.

## Added: tests that pin P1 on a live path

The red-by-deletion check showed that deleting P1 **inside the proof** leaves the driver-side same-group case green (table (b)). The census of the chain's group that fix round 1 added after the chain exits, and the one inside the stop path, run first and catch the survivor. P1 in the proof carries the load in recovery, where nothing runs before it. Two live tests were added:

- `:1215` `test_same_group_live_child_without_signature_blocks_query_and_on`: a survivor in the chain's group that names no sampler and no path of the night, so P3 cannot see it.
- `:1222` `test_recovery_withholds_on_while_same_group_child_without_signature_lives`: recovery through `recover_network_time` with the driver's proof, while that survivor lives. Expected: `chain_unproved`, no ON command, marker kept.

## Module results (per-ID runner, outside any sandbox, one module at a time)

| Module | Tests | ok | fail | error | skip | Baseline on `3ad82b43` |
|---|---|---|---|---|---|---|
| tests.test_run_night | 281 | 281 | 0 | 0 | 0 | 255, all ok |
| tests.test_network_time_window | 48 | 48 | 0 | 0 | 0 | 41, all ok |
| tests.test_night_gate | 104 | 104 | 0 | 0 | 0 | 104, all ok |
| tests.test_arm_retry | 37 | 37 | 0 | 0 | 0 | 37, all ok |
| tests.test_launch_window | 39 | 39 | 0 | 0 | 0 | 39, all ok |

`test_run_night`: all 254 baseline IDs that still exist pass. The one missing ID, `test_direct_child_exit_with_live_descendant_never_queries_or_restores`, is the saved F1 test that round 2 replaced with T1, as A1 §6 (D4) directs. There are 27 new IDs. The outputs are `/tmp/ntp-n1fix2b-d528efb2/<module>.json` and `.log`. The `test_run_night` numbers are from the final test file. The other four modules ran after the last code change; later edits touched only `tests/test_run_night.py`.

## Table (a) — the regressions on `3ad82b43`

Run in `/Users/edr/code/JouleWise-wt-ntp-n1old-d528efb2` (head `3ad82b43`) after copying in this round's final `tests/test_run_night.py` and `tests/test_network_time_window.py`. Output: `/tmp/ntp-n1fix2b-d528efb2/a_old_final.txt`.

| Row | Test | On `3ad82b43` |
|---|---|---|
| T1 | test_journaled_detached_capture_blocks_query_and_on | **fail (assertion)**: events `['off','query','on'] != ['off']` |
| T2 | test_unjournaled_detached_capture_blocks_query_and_on | **fail (assertion)**: same |
| T3 | test_sampler_named_detached_capture_outside_night_blocks_query_and_on | **fail (assertion)**: same |
| P2 case | test_journaled_detached_capture_without_path_signature_blocks_by_registry | **fail (assertion)**: same |
| T4 census, with E2 | test_census_stop_with_detached_child_blocks_query_and_on | **fail (assertion)**: same |
| T4 deadline, with E2 | test_deadline_stop_with_detached_child_blocks_query_and_on | **fail (assertion)**: same |
| T5 | test_recovery_from_run_night_waits_for_detached_child_then_restores | **fail (assertion)**: `['restored'] != ['chain_unproved']` |
| T6 | test_dead_man_both_recovery_calls_withhold_on_while_child_lives | **fail (assertion)**: outcome set differs |
| T7 timeout | test_sweep_timeout_refuses_before_query_and_on | **fail (assertion)**: `0 != 3` |
| T7 exit | test_sweep_nonzero_exit_refuses_before_query_and_on | **fail (assertion)**: `0 != 3` |
| T7 row | test_sweep_unparsed_row_refuses_before_query_and_on | **fail (assertion)**: `0 != 3` |
| T8 | test_sweep_excludes_its_own_matching_command_row | **fail (assertion)**: `False is not true` (no sweep on this head) |
| T9 (control) | test_clean_chain_runs_off_query_on | ok, as required on both heads |
| T10 | test_production_sampler_builder_matches_closed_name_list | **fail (assertion)** |
| D2 (i) | test_wrong_off_and_failed_immediate_on_recover_from_never_launched_claim | **fail (assertion)**: `'marker_invalid' != 'restored'` |
| D2 (ii) | test_unsavable_off_and_failed_immediate_on_recover_from_never_launched_claim | **fail (assertion)**: same |
| E1 | test_capture_proof_never_starves_a_check_and_keeps_the_failing_check | **fail (assertion)**: no proof on this head |
| E1 | test_capture_proof_that_times_out_is_not_proved_and_stays_bounded | **fail (assertion)**: no proof on this head |
| P1 recovery | test_recovery_withholds_on_while_same_group_child_without_signature_lives | **fail (assertion)**: `capture_proof` parameter absent |
| same group | test_same_group_live_child_blocks_query_and_on | ok (expected: this is the fix-round-1 case, cured on this head) |
| same group, no signature | test_same_group_live_child_without_signature_blocks_query_and_on | ok (expected: same reason) |

The E2 regression's own counterfactual is `c8995f4b`. Run there in a `git archive` copy with this round's test file (`/tmp/ntp-n1fix2b-d528efb2/c899_regress.*`):

- T4 deadline: fail (assertion) `'night_window_exceeded' != 'night_chain_alive'`.
- The E1 regression, and the seven live tests: fail (assertion) with P1 in place of P2 or P3.
- The four E3 tests: **ok**, which is the fixture-only proof.

## Table (b) — red by deletion on the final code

Done in the `/tmp` copy `/tmp/ntp-n1fix2b-d528efb2/final` (never in the worktree). Script: `/tmp/ntp-n1fix2b-d528efb2/deletions.py`. Output: `deletions.out` and `deletions_e2.out`. The files were restored and compared byte for byte after every case.

| Deleted | Named test | Result |
|---|---|---|
| P3 (sweep answers "clear") | T2 unjournaled | **red (assertion)**: `['off','query','on'] != ['off']` |
| P3 | T3 sampler-named, outside the night | **red (assertion)**: same |
| P2 (every registered group read as empty) | journaled child with no signature | **red (assertion)**: same |
| P1 inside the proof only | unit P1 regression `test_live_chain_group_cannot_prove_p1` | **red (assertion)** |
| P1 inside the proof only | new recovery same-group, no-signature test | **red (assertion)**: `'restored' != 'chain_unproved'` |
| P1 inside the proof only | driver same-group case (with or without signature) | **stays green**: the post-exit census of the chain's group (fix round 1, C7, unchanged) catches it first |
| P1 in the proof **and** the post-exit census | same-group case, no signature | **red (assertion)**: `['off','query','on'] != ['off']` |
| P1 in the proof **and** the post-exit census | same-group case, child under the night's root | **red (assertion)** on the exit status (`3 != 6`). P3 still withheld the query and ON. |
| C5 (the recovery proof gate) | T5 | **red (assertion)**: `['restored'] != ['chain_unproved']` |
| never-launched start claim | D2 (i) and (ii) | **red (assertion)**: `'chain_unproved' != 'restored'` |
| E2 supersede | T4 deadline | **red (assertion)**: `'night_window_exceeded' != 'night_chain_alive'` |

## Files changed (`git status --short`)

```
 M scripts/run_night.py
 M tests/test_run_night.py
```

`git diff --check` is clean. The scratch worktree `JouleWise-wt-ntp-n1old-d528efb2` now holds this round's two test files in place of the earlier ones, as the brief allowed.

## Stop conditions

None met.

- The cure needed no file outside scope.
- No existing assertion was weakened or deleted. T4 only gained assertions; the E3 cure changed the fixture, not any assertion.
- No case was found in which a process with a capture signature is alive while the query or ON runs. Every live case refused with events `["off"]`, and every deletion that let the query and ON through was a deletion of a check.
- Safety: no sudo, systemsetup, sntp, system-log query, capture, battery read, or process named after the sampler. Every test child was a harmless Python sleeper, killed in cleanup. A `pgrep` after each run found none left.
