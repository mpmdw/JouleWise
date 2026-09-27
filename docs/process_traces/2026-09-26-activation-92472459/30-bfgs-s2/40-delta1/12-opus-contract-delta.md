# BFG-S S2 fix round 1: Opus contract-lens delta re-audit, `4ea4b26b..6c73caf4`

Reviewer: Claude Opus 5.5, contract lens. I worked in one foreground session with no subagents. One long test run was moved to the background by the harness's 600 s limit, and I waited for it to finish. I edited no repository file. Scratch lives under `/tmp/s2delta/`:
- `cand/` is `git archive 6c73caf4`;
- `base/` is `git archive 4ea4b26b`;
- `redbase/` is the base code with the candidate's two test files;
- `diffcand/` is the candidate code with the base's two test files;
- `mut/<name>/` holds one mutant each, made by `mutate.py`;
- the probes are `diffprobe.py`, `f7probe.py`, `f7probe_journal.py` and `f7auth.py`.

I read the delta charge, the fix contract, the seat report, both round-1 lens reports, the seat brief, and amendment 32 (ERR §3) and amendment 35 item 2 (Q35) for the ordering clause. I did not read RUN_STATE, TASK_QUEUE, CLAUDE*, AGENTS, the decision log, or any memory or skill file.

## Verdict

- **BLOCKER:** 0
- **SHOULD-FIX:** 1
- **NIT:** 2

Each of F1 to F8, and the NO CHANGE item, implements its dictated closure. None goes beyond it. Every dictated counterfactual mutant is killed, apart from the one operand in D-1.

The fix round changed no behaviour that the ruled texts fix. I compared the candidate with the base on eleven envelope classes through the real `pilot_summary`. Only the two intended differences appear:
- F2's carve-out row;
- F1's replay keys under a battery status.

The base suite also runs green against the candidate code.

The standing constraints hold:
- only the four fix-round paths changed;
- `battery_float.py` and the excluded paths are untouched;
- the registration digest is `69321c69…` (re-hashed);
- no exclusion literal was added;
- custody is only ever raised, never turned into a status.

## 1. Executed evidence

```
$ git -C …/JouleWise-wt-s2lens-92472459 rev-parse HEAD            -> 6c73caf42b4df2bf882c0fef84d56d27ffd325b3
$ git diff --name-only 4ea4b26b 6c73caf4
joulewise/quiet_predicate_campaign.py
scripts/sample_quiet_predicate_evidence.py
tests/test_quiet_predicate_campaign.py
tests/test_sample_quiet_predicate_evidence.py
$ git diff --stat 1417c0c4 6c73caf4 -- joulewise/battery_float.py joulewise/evidence_night.py joulewise/night_gate.py configs/campaigns/quiet_predicate_evidence_01 scripts/night_chains
(empty; night_kinds.py shows only S2's own text-15 flip)
$ shasum -a 256 configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json
69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
```

### V1, V2 and V3 on the candidate

`/bin/ps` is permitted here. The real-collector subprocess row that the seat could not run passed.

```
cand overlay: python3 -m unittest tests.test_quiet_predicate_campaign
Ran 194 tests in 28.297s
OK

cand overlay: python3 -m unittest tests.test_sample_quiet_predicate_evidence tests.test_battery_float_sweep tests.test_evidence_night
Ran 248 tests in 122.428s
FAILED (failures=1, errors=2)
```

All three failures are in `test_evidence_night` and need a git repository: `git clone --bare` of a `git archive` overlay, and `unable to read tree`. So I re-ran those modules in the read-only worktree, with `PYTHONDONTWRITEBYTECODE=1`. `git status` stayed clean.

```
worktree: python3 -m unittest tests.test_evidence_night tests.test_night_kinds
Ran 181 tests in 344.732s
OK

worktree: python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers      (V2)
Ran 131 tests in 94.262s
OK

worktree: python3 -m unittest tests.test_gen_evidence_night tests.test_night_agent_install tests.test_run_night   (V3)
Ran 329 tests in 763.210s
OK
```

### New tests against the base code (`redbase`)

The fix round's 31 tests (the three new `BenchReplayFailClosedTests` rows, plus `BatteryFloatSummaryTests`, `BatteryFloatExecuteTests` and the three new collector rows) were run against the base code:

```
ERROR: test_replay_with_battery_nonpass_refuses_at_harvest                    (F1)
ERROR: test_refusal_journal_precedes_session_even_if_session_write_fails     (F7)
FAIL:  test_amendment32_empty_crash_has_collect_error_without_custody (pre=False), (pre=True)   (F2)
FAIL:  test_authenticated_session_swap_raises_before_pilot_routing           (F4, pilot_summary)
FAIL:  test_missing_historical_journal_is_custody_with_accurate_message      (F8)
FAIL:  test_replay_markdown_names_excused_and_refused_envelopes              (F6 N-3)
FAIL:  test_summarize_detects_session_changed_during_authentication          (F4, summarize)
Ran 31 tests in 4.372s
FAILED (failures=6, errors=2)
```

### Base tests against the candidate code (`diffcand`)

```
Ran 282 tests in 64.070s
FAILED (failures=1)   -> LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child (exit_delay=60)
re-run of LoadTests alone, both diffcand and cand:  Ran 11 tests … OK
```

This is a timing flake under machine load. The delta does not touch the load-join ladder.

### Mutation matrix

Each mutant replaces exactly one production text in a copy of the candidate (`/tmp/s2delta/mutate.py`).

| Mutant | Scope run | Result | Killer |
|---|---|---|---|
| M1a: `execute` refuses on status only | `BenchReplayFailClosedTests` | KILLED | `test_replay_with_battery_nonpass_refuses_at_harvest` (outcome/rc) |
| M1b: replay keys gated on `not battery_statuses` | same | KILLED | same (KeyError) |
| M2a: carve-out row hard-codes `[collect_error, incomplete_interior_support]` and skips the helper | `BatteryFloatSummaryTests` | KILLED | `test_amendment32_empty_crash…` ×2 |
| M2b: carve-out drops `cleanup_unproven` | same | KILLED | same |
| M3a: carve-out ignores `rounds.jsonl` | same | KILLED | `test_carveout_requires_absent_journal_and_round_directories` |
| M3b: carve-out ignores `raw/round-*` | same | KILLED | same |
| M3c: `lstat` replaced by `exists()` | same | KILLED | same (dangling symlink) |
| M3d: `route_1248_1`, dropping `not completed` from `refusal` | same | KILLED | `test_completed_record_with_refusal_marker_uses_observer_floor` |
| M4a: `pilot_summary` session comparison removed | + Execute, Interrupted | KILLED | `test_authenticated_session_swap_raises_before_pilot_routing` |
| **M4b: `pilot_summary` journal comparison removed** | **all of `tests.test_quiet_predicate_campaign` (194)** | **SURVIVED** (`OK`) | none |
| M4c: `summarize` session comparison removed | all of `tests.test_sample_quiet_predicate_evidence` (101) | KILLED | `test_summarize_detects_session_changed_during_authentication` |
| **M4d: `summarize` journal comparison removed** | **all of `tests.test_sample_quiet_predicate_evidence` (101)** | **SURVIVED** (`OK`) | none |
| M4e: routing re-reads `session.json` fresh instead of using `b0` | `BatteryFloatSummaryTests` | survived: equivalent mutant (see §3, no finding) | — |
| M5a: `os.fsync` deleted in `atomic_write_text` | `BatteryCollectorTests` | KILLED | `test_atomic_session_and_final_journal_fsync_before_replace` |
| M5c: `fsync` moved after `os.replace` | same | KILLED | same |
| M5b: `flush=True` deleted on the custody line | `BatteryFloatExecuteTests` | KILLED | `test_x1_flushes_custody_line` |
| M6: replay `summary.md` without notes | `BatteryFloatSummaryTests` | KILLED | `test_replay_markdown_names_excused_and_refused_envelopes` |
| M7: refusal path writes session first again | `BatteryCollectorTests` | KILLED | `test_refusal_journal_precedes_session…` |
| M8: old "after authentication" wording | `BatteryFloatSummaryTests` | KILLED | `test_missing_historical_journal_is_custody_with_accurate_message` |
| N4-q: `first_write` dropped from the excuse branch | same | KILLED | T6-j/k, T6-q/s, T6-r |
| N4-d: a lone pre raw blocks the carve-out | same | KILLED | `test_amendment32_empty_crash…` |
| N4-p: the refusal route adds a battery status | same | KILLED | T6-p; replay-markdown row |

Exact tails of the two survivors:

```
M4b_pilot_no_journal_compare: SURVIVED | Ran 194 tests in 28.194s | OK | killers=[]
M4d_summarize_no_journal_compare: SURVIVED | Ran 101 tests in 31.549s | OK | killers=[]
```

### Differential probe (`/tmp/s2delta/diffprobe.py`)

The probe runs the real `pilot_summary` on the same scenarios, with the base code (`redbase`) and with the candidate code, and compares `summary.json` and `summary.md`:

```
scen_carveout_unproven
    .report.envelopes[4].busy_cores: ADDED {...}
    .report.envelopes[4].busy_cores_samples: ADDED 0
    .report.envelopes[4].excluded: ["collect_error", "incomplete_interior_support"] -> ["cleanup_unproven", "collect_error", "incomplete_interior_support"]
    .report.envelopes[4].non_observer_process_busy: ADDED []
    .report.envelopes[4].recorder_observer_cpu_s: ADDED 0
scen_clean IDENTICAL
scen_completed_124_unproven IDENTICAL
scen_completed_error_class IDENTICAL
scen_executor_nonobserver_verdict IDENTICAL
scen_first_write_excused_unproven IDENTICAL
scen_legacy IDENTICAL
scen_refusal_exit3 IDENTICAL
scen_replay_only IDENTICAL
scen_replay_plus_battery
    .report.replay_recorder_envelopes: ADDED [{"index": 1, "recorder_kind": "replay"}, …]
    .report.replay_recorder_reason: ADDED "one or more session.json records do not carry power.recorder_kind == 'powermetrics'"
scen_unfinished_exit0 IDENTICAL
```

### Real refusal record after F7 (`f7auth.py`, real `collect`)

```
refusal error_class: network_time_provenance | files: ['raw', 'rounds.jsonl', 'session.json']
authenticate: pass []
pilot_summary: SPREAD_RECORDED | env5: collector refused before capture: network_time_provenance, collector_exit 3 ['collect_error', 'incomplete_interior_support']
```

### A kill between the refusal path's two writes, real `collect`, then `pilot_summary` with exit 124

`f7probe.py` stops the collector at the `session.json` write. `f7probe_journal.py` stops it at the `rounds.jsonl` write.

```
kill at session.json write
  base: left ['raw', raw/…post.ioreg, raw/…pre.ioreg]                 -> SPREAD_RECORDED, env5 ['collect_error','incomplete_interior_support'] "collector left no record"
  cand: left ['raw', raw/…post.ioreg, raw/…pre.ioreg, 'rounds.jsonl'] -> CustodyUnreadable session.json unreadable: missing | summary.json exists: False
kill at rounds.jsonl write
  base: left ['raw', …, 'session.json']                               -> CustodyUnreadable round journal missing | summary.json exists: False
  cand: left ['raw', …]                                               -> SPREAD_RECORDED, env5 ['collect_error','incomplete_interior_support'] "collector left no record"
```

## 2. Item table (contract lens)

| Item | Dictated closure | Implementation | Pinned, and the mutant that kills it | Verdict |
|---|---|---|---|---|
| F1 | Replay keys whenever `replay_recorders` is non-empty; battery status precedence kept; `execute` refuses on the keys; the row through `execute` | QPC:1452-1456 (keys written unconditionally); the status block is still gated `and not battery_statuses`; the battery block still overrides; QPC:1780 | `test_replay_with_battery_nonpass_refuses_at_harvest` (environment unset: `exercise(recorder_kind='replay')` sets no environment); M1a and M1b KILLED | exact |
| F1: can a non-replay night be refused? | — | `replay_recorders` fills only when `power` is non-null and `recorder_kind != 'powermetrics'`. The collector sets `power` only from `recorder.metadata`, which always carries `recorder_kind` (SQ:752, :1185). First-write and refusal records have `power: null`. A live production night therefore cannot enter the new refusal. A pre-key historical session can, but that is exactly the pre-S2 `REPLAY_NEVER_EVIDENCE` refusal. No other consumer reads the keys (grep). `scen_*` on production nights: IDENTICAL | — | no defect |
| F2 | One booking helper for `collect_error`, `cleanup_unproven`, the non-observer rule with `require_observer_marked`, and busy cores, called on both paths; the carve-out adds `incomplete_interior_support`; authentication stays first | `book_envelope` QPC:1149-1174; carve-out :1200-1204; main path :1226, in the same position as before (after the non-pass `battery_float_envelopes` append, before the session parse) | extended `test_amendment32_empty_crash…` (`cleanup_proven: False`, busy keys); M2a and M2b KILLED. Differential: only the carve-out row changes; the authenticated classes (completed exit 124 with cleanup unproven, executor non-observer verdict, excused, refused, unfinished, legacy, completed carrying `error_class`, clean) are IDENTICAL; the base suite is green on the candidate | exact. The carve-out's `excluded` is `sorted(set(…))`, the same form the main path emits |
| F3 | Rows (i) to (iv) through `pilot_summary`; (i), (ii) and (iv) RED under the named mutants | `test_carveout_requires_absent_journal_and_round_directories` (i, ii, iii); `test_completed_record_with_refusal_marker_uses_observer_floor` (iv) | M3a, M3b, M3c and M3d KILLED | exact |
| F4 | Snapshot `b0`/`j0` before and `b1`/`j1` after authentication; any difference, including presence, raises `CustodyFailure` naming the file; all routing and summary reads use `b0`/`j0`; a session-swap row in `pilot_summary` and a parallel row in `summarize` | QPC:1205-1217, 1228-1231, 1281-1283; SQ:1507-1529, 1598 (provenance now reads the authenticated sessions) | both swap rows RED on base; M4a and M4c KILLED; **M4b and M4d SURVIVE (D-1)** | implemented exactly; one dictated operand unpinned |
| F4 honest-night check | — | `record_attestation` (QPC:1695) rewrites `session.json` inside the envelope loop, before `pilot_summary`. `authenticate_quiet_session` only opens files `O_RDONLY` (battery_float.py:850). The covariate recorder writes the night journal, not envelope files. `cleanup_record` runs before `pilot_summary`. The full executor rows (V1, V3) and the real-collector rows are green | — | no defect (residual in §3) |
| F5 | `fsync` before `os.replace` for the session write and the finalization journal; temp name asserted; custody line flushed | `test_atomic_session_and_final_journal_fsync_before_replace`; `test_x1_flushes_custody_line` | M5a, M5c and M5b KILLED | exact |
| F6 | N-3 notes on the replay branch; the N-4 assertions and inputs; the synthetic 12-envelope legacy night in CI; the N-5 rename and the original scenario through `execute` | QPC:1501-1507 and :1534 | M6 KILLED. The N-4 pins are baseline-green by nature (the seat's RED-PINS flag); their teeth are shown by N4-q, N4-d and N4-p KILLED. `test_L2_replay_collectors_crash_before_any_record_still_refuses` sets the environment and every exit to 124: refused, rc 2, `recorder_kind` replay | exact |
| F7 | Empty `rounds.jsonl` written before the refusal `session.json`; the row through `collect` | SQ:1109-1110 | M7 KILLED; a real refusal record still authenticates `pass` and routes as refused (`f7auth.py`) | implemented exactly; **the purpose is not met (D-2)** |
| F8 | Keep the raise, worded `rounds.jsonl unreadable: <reason>`; add a row | QPC:1283 | M8 KILLED; `^rounds.jsonl unreadable:` | exact |
| NO CHANGE (Sol B1) | No discriminator added | none added; `first_write` at QPC:1250-1252 unchanged | — | exact |

## 3. Findings

### D-1 (SHOULD-FIX). F4's `rounds.jsonl` comparison is unpinned in both `pilot_summary` and `summarize`

**What the contract dictated.** F4's closure is "if b1 != b0 **or j1 != j0** … raise … ('… rounds.jsonl changed …')". The contract named a row only for the session swap. The seat implemented the journal comparison correctly at QPC:1216-1217 and SQ:1526-1528.

**Evidence.** Deleting either journal comparison leaves every test in its module green:
- M4b: `Ran 194 tests … OK`;
- M4d: `Ran 101 tests … OK`.

**What depends on it.** Routing and the observer floor use `j0`, the bytes read before authentication. Only `j0 == j1` shows that those bytes are the ones the authenticator saw. A future edit that drops the comparison would go unnoticed.

**Closure (bench-sized: two test rows, no production change).** Mirror the two existing session-swap rows:
1. Wrap the real `authenticate_quiet_session` so that, right after it returns `pass` for envelope 5, it appends a line to that envelope's `rounds.jsonl`. Run this through `pilot_summary` and through `summarize`.
2. Expect `CustodyFailure` matching `rounds.jsonl changed during authentication`, and no `summary.json`.
3. Show the rows RED under M4b and M4d.

### D-2 (NIT). F7 moves the honest-kill custody window instead of closing it, and makes it slightly wider

**This was my own mistake in round 1.** Round-1 N-2 (my lens) proposed writing the journal first as the closure, and the contract dictated it. The executed probe (§1, last block) shows why it does not work. Under either order there is exactly one kill point between the two writes that reads as custody:
- **Base:** `session.json` exists without `rounds.jsonl`, and authentication raises `round journal missing`.
- **Candidate:** `rounds.jsonl` exists without `session.json`, the carve-out is blocked by the journal, and the envelope raises `session.json unreadable: missing`.

**The window is wider now.** In the base it was the empty `write_text("")`. In the candidate it is the whole atomic session write: temp file, `fsync`, then `os.replace`.

**No write order can close this window.** The leftover state from either kill is byte-identical to a tamper that deletes one file of a complete refusal record. F3 row (i) rules that kind of tamper as custody. So carving out either state would turn custody into an exclusion.

**Harm.** Nothing is harmed:
- the outcome is fail-closed custody, never an exclusion;
- the refusal path finishes in seconds, while the executor kills at `envelope_s + 30`;
- the completed refusal record still authenticates.

**Closure (magistrate's choice, no ruling needed).** Either:
- restore the base order, which has the narrower window, and invert the F7 row to pin it; or
- keep F7 as it is.

In both cases, record the residual: "a kill between the refusal path's two writes reads as custody".

### D-3 (NIT). F4 reads before authenticating; amendment 32(2) says authentication runs "before the summary's own read"

**The literal conflict.** The dictated sandwich reads `b0`/`j0` before `authenticate_quiet_session` and routes from them. Taken literally, that puts the summary's read first.

**Why the purpose holds.**
- The routed bytes are proved equal to a read taken after authentication returned (`b1`, `j1`).
- Amendment 35 item 2's operative sentence is also met. It says "no decision to exclude, excuse, route or skip … before this call has returned", and the pre-read makes no decision.
- `battery_float.py` is frozen and does not return the bytes it authenticated, so the sandwich is the only way to close B2 within scope.

**Closure.** No code change. The magistrate records that the before/after snapshot satisfies 32(2) because the routed bytes equal the post-authentication read. That way a later reviewer does not "fix" the order back and reopen B2.

### Observations (no finding)

- **M4e, fresh re-read, is an equivalent mutant.** With both comparisons in place, a fresh read can differ from `b0` only through a change after the comparison. No test can kill that deterministically. The code routes from `b0`, as dictated.
- **Straggler writes during authentication.** A collector whose cleanup is unproven could in principle rewrite its files while authentication runs. The night then raises custody (X-1: printed, re-raised, no outcome document) instead of ending `refused`. Before F4, the same straggler could already make authentication itself raise on a mismatched pair, or produce B2's unauthenticated routing. F4 therefore does not widen what can happen; it replaces a silent wrong route with a raise.
- **`summarize` load-join reads are outside F4's scope.** `summarize` still reads `raw/round-*/ps_before.txt` and `ps_after.txt` fresh, but only when `load_logs` is supplied. These feed the diagnostic load joins, not routing, and F4 dictated `b0`/`j0` only.
- **The replay-plus-battery `summary.md` names only the battery status.** Nothing ruled requires a replay line there. `summary.json` now carries the replay keys (F1).

## 4. Same-signature statement, one line per round-1 defect class

1. **Custody converted to exclusion: NO.**
   - The carve-out mutants M3a, M3b and M3c are killed.
   - F2 changes only what the carve-out row books, not when it applies.
   - F4 turns a change after authentication into custody.
   - The one new honest-kill state (D-2) reads as custody, not as an exclusion.
2. **An unpinned routing operand: NO for routing operands; YES, adjacent, in the same family, at a new site.**
   - Every routing operand the delta touched is killed: M1a, M1b, M3d, N4-q, N4-d, N4-p.
   - But F4's new custody guard has an unpinned operand, the `rounds.jsonl` comparison (D-1), in both entry points.
   - It came from a contract that named a row for only one of the two dictated operands. The seat implemented the operand correctly.
   - The magistrate should judge whether this counts as the same signature for the escalation trigger. My reading: it is the same family (a dictated condition without a dying test), not a repeat of a round-1 defect, and it is closable at the bench.
3. **A record field dropped under a battery status: NO.**
   - F1 restores `replay_recorder_envelopes` and `replay_recorder_reason` whatever the battery status. M1b is killed.
   - The differential shows no other field added or dropped on any of the eleven classes.
