# Delta re-audit of fix round 2: branch feat/2026-09-23-qpe01-v3-round2, 0e5578fb..c496f244

Reviewer: Opus 5.5, read-only delta lens covering both contract and execution. Worktree `/Users/edr/code/JouleWise-wt-v3r2-7a0f14bd`. `git status --short` was empty before and after this review. Nothing was written inside the worktree.

A documentation-only commit, 92ee76f5, landed on top of c496f244 while I worked. `git diff --name-only c496f244..92ee76f5` lists only `docs/` paths, so I ignored it. The one test run below happened at 92ee76f5, and its code is identical to c496f244.

Mutation probes ran in throwaway clones `/tmp/delta-r2-mut*` at c496f244, and those clones have since been deleted. The driver script is kept at `/tmp/delta-r2-mutate.sh`.

**Terms used below** (the same as the round-1 re-audit):
- **Round 1** is F1–F16. **Round 2** is R1–R4.
- **In-chain verdict** is the executor's per-envelope decision, taken while the night runs.
- **Summary** is `pilot_summary`, re-derived from disk after the night.
- **Floor** is Σ whole-envelope observer CPU ÷ Σ envelope span, in cores.
- **Companion** is the floor with the sibling load recorder's CPU added back. It is reported, never a stop input.
- **Mutation**: a deliberate re-break of the code in a scratch copy. A test **kills** it if the test fails. The mutation **survives** if every test still passes.
- **Same signature**: an earlier round's defect class reappearing in the same shape.

---

## BLOCKER

None.

## SHOULD-FIX

None.

## NIT

**N2-a. After an in-chain marking failure, the outcome under-reports what was captured.**
- Mechanism: the R1 guard (`quiet_predicate_campaign.py:1614`) raises after envelope 01's collector has run, been reaped and been clock-attested, but before that envelope's row is appended (`:1616-1632`).
- What is on disk afterwards (executed probe, section 3 below):
  - `evidence/envelope-01/{session.json, rounds.jsonl, timed-log.txt}` exist.
  - `evidence_envelopes.jsonl` does not exist at all. Seat deviation 2 says it is "empty"; it is actually absent.
  - `evidence_outcome.json` says `"envelopes_attempted": 0`.
  - `summary.json` is written as `INCONCLUSIVE`, `retained 0`, zero envelopes.
- The executor's own facts about envelope 01 are lost: its collector exit code, its per-envelope cleanup verdict, and its cleanup and attestation wall costs. The attestation state itself survives in the envelope directory.
- The start-drift abort takes the other path: it appends a row marked `"abort"` before raising (`:1542`).
- Nothing is admitted, and the refusal document and the outcome both carry the true cause (see the D1 row). `night_probe_error` is a cold-gate code (`arm_retry.COLD_GATE_CODES`). It is not in `zero_capture_successor_allowed`'s eligible set, so this refusal licenses no retry and no successor.
- Optional cure: append the row with an `"abort": "unmarked_journal"` marker before raising, as start-drift does. Or leave it, and correct the seat's word "empty" to "absent, with `envelopes_attempted: 0`".

**N2-b. The harness change (`summary` may now be `None`) removes an implicit guard, but hides nothing today.**
- `FrozenExecutorTests.exercise` (`tests/test_quiet_predicate_campaign.py:621-624`) used to die with `FileNotFoundError` on any night that wrote no `summary.json`. That was an unstated assertion that the summary was written.
- What executes today:
  - Probe (e), strict loading restored: 155/155 OK. No test at HEAD reaches the `None` branch, not even the new R1 test, whose night writes `summary.json` with zero envelopes.
  - Probe (f), `pilot_summary` always raising: under the lenient harness, 11 test cases (6 distinct tests) now pass that the strict harness would fail. The mutation itself is still killed by 86 others.
  - Probe (h), a realistic narrow break where the summary raises on any `cleanup_unproven` envelope: the lenient harness loses two kills, the truth-table cases "refused (two cleanup_unproven), restored / restore failed". It keeps 36 errors, led by `test_isolated_cleanup_unproven_continues_but_two_consecutive_refuse`, so the mutation is still killed.
- Optional cure: make the `None` branch opt-in with an `allow_missing_summary=False` keyword. Its only user was the R1 test's failing-before run at 0e5578fb.

**N2-c. One R2 assertion claims more than it proves.**
- The assertion: `self.assertFalse(set(hits) & basenames)`, "The measurement's own processes are never named" (`:3757`).
- Mutation (c2): mark only `powermetrics` instead of the seven basenames. It **survives** (155/155 OK).
- Why: unmarked, the other six stay far under the 30 core-s bar. Executed with the bar set to 1e-9: the largest per-envelope integrals are `Python` 0.40 and `top` 0.11 on 21:00, and `Python` 0.77 and `top` 0.11 on 02:17.
- So the assertion guards `powermetrics` only. The seat's own probe, "observer mark ignored → {'powermetrics'}", kills that case. The ruled property itself (12/12 `fseventsd` on 21:00, 0/12 on 02:17) does not depend on the six.
- Optional cure: reword the comment to "powermetrics, the one observer over the bar, is never named".

**N2-d. The R3 test would silently pass if the stop were ever absent.**
- `stop = report["block_two_stop"] or {}` (`:3567`) makes `assertNotIn` pass if `block_two_stop` is ever `None`. The summary's other return path at `:1412` sets it to `None`.
- Today the stop is live: mutation (b) is killed.
- Optional cure: add one line, `self.assertIsNotNone(report["block_two_stop"])`.

**N2-e. One loop in the R1 test checks an empty list.** The loop that asserts no row names `fseventsd` (`:3339`) runs over zero rows in the passing case, because the journal is absent and the summary has no envelopes. The property is carried by the reason assertion and the `envelope_directories == ["envelope-01"]` assertion, which mutation (a) trips. No action needed; recorded so no one treats the loop as the guard.

Round-1 NITs N-a and N-c through N-g were out of this round's scope. None of them was touched, and none got worse.

---

## Per-finding disposition

| Item | Disposition | Commit, file:line | New defect from the cure? |
|---|---|---|---|
| **D1**: marking failure aborts as `non_observer_process_busy` | **CURED** | 0fd965fe; `joulewise/quiet_predicate_campaign.py:1605-1615` (the guard runs on the envelope's joined rows before `non_observer_busy`); test `tests/test_quiet_predicate_campaign.py:3296` | Only N2-a (the outcome says 0 attempted while envelope 01 is on disk). See the notes after the table |
| **D2**: ruling 10 regression 1 on archive bytes untested | **CURED** | 1226e8d9; `archive_summary` gains `observer_basenames` (`:3005-3031`), which marks consumers in the /tmp copy only; test `:3722` | Only N2-c (one comment overclaims). See the notes after the table |
| **D3**: "companion never a stop input" was vacuous | **CURED** | fac33045; test `:3542`. The fixture's split is asserted inside the test (`:3564-3565`: floor 0.04983 < 0.05 < companion 0.05067) | Only N2-d |
| **N-b**: generic refusal names a skipped check | **CURED** | 308f24ac; `joulewise/evidence_night.py:997-1003` (`failed` is built with the same test as `passed`, and `passed = not failed`) and `:1021`; test `tests/test_evidence_night.py:1165` | No. `passed` is logically identical to the old `all(...)`, and `armable` and `rehearsal_ready` are unchanged. When `passed` is false, `failed` is never empty, so the text can never read "failed: ;" |

**D1 notes.**
- Executed on-disk probe: `refusal.json` has reason `night_probe_error` and detail "evidence chain refused: ValueError: recorder journal carries no observer-marked consumer; ancestry marking failed". The outcome error carries the same text, and rc is 2.
- Nothing is admitted: the summary is `INCONCLUSIVE` with `retained 0`, and the orphaned envelope-01 capture is not in it.
- `night_probe_error` is cold-gate only, so neither A270's successor route nor D-182's zero-capture route can fire on it.
- The guard now also runs per envelope in the chain. That adds no new false-positive exposure. Executed on both archives: every envelope has 18–19 rows naming consumers, and 18–19 of them contain `powermetrics`, so an envelope with no marked consumer does not occur on real bytes.

**D2 notes.**
- The marking is done on parsed rows re-serialised into `tempfile` under /tmp. The archive is only read (`read_bytes`), and `copytree` goes from the archive to /tmp. Nothing writes back.
- The test asserts each night's guard status (21:00 `INCONCLUSIVE`, 02:17 `REPLAY_NEVER_EVIDENCE`), so neither half can pass vacuously.
- Executed: it ran rather than skipped (the suite's `OK` line carries no skips).

**D3 note.** The old sibling assertion is still vacuous on its own, but the property it names is now guarded.

---

## Executed evidence

**1. The two named modules, run once** (in the worktree, HEAD 92ee76f5, code = c496f244):
```
$ cd /Users/edr/code/JouleWise-wt-v3r2-7a0f14bd && time python3 -B -m unittest tests.test_quiet_predicate_campaign tests.test_evidence_night
...
envelope_start index=12 collector_pgid=8000012 recorder_pgid=8000000
envelope_end index=12 rc=0 cleanup_proven=True clock_attestation=authenticated
evidence_end outcome=complete cleanup_proven=True network_time_restored=True
...............................................................................................................
----------------------------------------------------------------------
Ran 265 tests in 301.016s

OK
python3 -B -m unittest tests.test_quiet_predicate_campaign   145.54s user 137.72s system 94% cpu 5:01.26 total
rc=0
```
This is 265 tests, matching the seat's count, with no skips.

**2. Required mutations** (each in its own scratch clone at c496f244; the whole module run once per mutation):
```
(a) quiet_predicate_campaign.py:1614  require_observer_marked(support) -> pass
    tests.test_quiet_predicate_campaign: Ran 155, FAILED (failures=1)
    KILLED by NonObserverAbortTests.test_a_marking_failure_in_chain_is_a_probe_error_never_a_busy_daemon
      AssertionError: 'non_observer_process_busy' != 'night_probe_error'
(b) :1343  stop_branch(..., observer_floor=observer_floor_including_load_recorder, ...)
    Ran 155, FAILED (failures=1)
    KILLED by ObserverFloorTests.test_the_companion_above_the_smallest_share_is_never_a_stop_cause
      AssertionError: 'observer_floor_above_smallest_holdable_share' unexpectedly found in ['observer_floor_above_smallest_holdable_share']
(c) tests:3029  consumer["observer"] = True -> pass   (the archive helper marks nothing)
    Ran 155, FAILED (errors=1)
    KILLED by ObserverFloorTests.test_ruling_10_regression_1_on_marked_copies_of_both_archived_journals
      ValueError: recorder journal carries no observer-marked consumer; ancestry marking failed
(d) evidence_night.py:1021  ", ".join(failed) -> ", ".join(k for k, v in checks.items() if v["verdict"] != "pass")
    tests.test_evidence_night: Ran 110 in 277.372s, FAILED (failures=1)
    KILLED by LifecycleTests.test_the_generic_refusal_names_only_failed_checks_never_a_skipped_one
      AssertionError: False is not true : pre-arm checks failed: courier, machine_quiet; see /private/tmp/lifecycle-.../lifecycle/check.json
```
Each mutation is killed by exactly the new test for its item and by no other test. That is expected: the new tests exist because nothing else guarded these properties.

Mutation (c) is killed by an error from the fail-closed guard, not by an assertion failing, and that is still a kill. A helper that marks everything would fail the `fseventsd`/`pid 341` assertions instead, because the summary could then name no one.

**3. Additional probes:**
```
(c2) archive helper marks only powermetrics                 SURVIVES  Ran 155, OK            -> N2-c
     unmarked six basenames, max per-envelope core-s (bar 30):
       2100 {'Python': 0.4, 'top': 0.11}   0217 {'Python': 0.77, 'top': 0.11}
(e)  harness back to strict summary loading                  Ran 155, OK  (no test at HEAD reaches summary=None)
(f)  pilot_summary always raises, lenient harness            FAILED (failures=61, errors=82): 86 names
(g)  same, strict harness                                    FAILED (failures=5, errors=160): 97 names
     killed only under strict: test_dead_covariate_recorder_refuses_with_document,
       test_regression_0_the_executor_launches_the_recorder_with_its_own_pid,
       test_regression_5_a_stepped_wall_clock_keeps_the_window_over_the_capture (step=±30),
       test_regression_8_the_teardown_budget_is_the_gap_not_a_literal,
       6 truth-table cases (final cleanup unproven x2, dead recorder x2, two cleanup_unproven x2)   -> N2-b
(h)  summary raises on any cleanup_unproven envelope, lenient   FAILED (errors=36)
(hs) same, strict                                               FAILED (errors=38)
     difference: truth-table 'refused (two cleanup_unproven), restored' / '..., restore failed'  -> N2-b
```

**4. D1 on-disk probe** (the R1 test's unmarked scenario, with a spy wrapping `campaign.execute` that lists the night directory after it returns):
```
PROBE rc 2
PROBE files { evidence/envelope-01/rounds.jsonl: 398, evidence/envelope-01/session.json: 2061,
  evidence/envelope-01/timed-log.txt: 47, evidence/summary.json: 4185, evidence/summary.md: 770,
  evidence_busy_cores.jsonl: 529, evidence_cleanup.json: 134, evidence_cleanup.lock: 0,
  evidence_outcome.json: 253, evidence_processes.jsonl: 227, network_time_control.json: 561, refusal.json: 343 }
PROBE evidence_envelopes.jsonl bytes: '<absent>'
PROBE outcome {"cleanup_proven": true, "envelopes_attempted": 0,
  "error": "ValueError: recorder journal carries no observer-marked consumer; ancestry marking failed",
  "network_time_restored": true, "outcome": "refused", "recorder_kind": "powermetrics"}
PROBE refusal.json {"refusal": {"detail": "evidence chain refused: ValueError: recorder journal carries no
  observer-marked consumer; ancestry marking failed", "evidence": null, "reason": "night_probe_error"},
  "verdict": "REFUSED", "receipt_class": "DIAGNOSTIC_NO_PACK", ...}
PROBE summary status INCONCLUSIVE retained 0 envelopes 0
```

**5. How the refusal code is routed** (`joulewise/arm_retry.py`): `night_probe_error` is in `COLD_GATE_CODES`, so `classify_abort` gives `cold_gate`. `zero_capture_successor_allowed` has this eligible set: `{night_refused_not_quiet, night_refused_bind_expired, night_refused_agent_present, night_refused_hid_idle, night_refused_boot_clock}`. `night_probe_error` is not in it.

**6. False-positive margin of the in-chain guard on real bytes** (production `envelope_support` over each archived night's own executor rows; each tuple is index, rows, rows naming consumers, rows with `powermetrics`):
```
2100 [(1,19,19,19),(2,19,19,19),(3,19,19,19),(4,18,18,18),(5,19,19,19),(6,18,18,18),(7,19,19,19),(8,19,18,18),(9,18,18,18),(10,19,19,19),(11,18,18,18),(12,19,19,19)]
0217 [(1,19,19,19),(2,19,19,18),(3,19,19,19),(4,18,18,18),(5,19,19,19),(6,19,19,19),(7,19,19,19),(8,18,18,18),(9,19,19,19),(10,19,19,19),(11,19,18,18),(12,18,18,18)]
```

**7. Tree state:** `git status --short` in the worktree is empty. The scratch clones are deleted.

---

## Same-signature statement

1. **"A test that passes without its property"** (round-0 Opus S2, round-1 D3): **it does not recur at SHOULD-FIX or above.**
   - All four required mutations are killed, each by the new test for its item. D3's instance is cured, and the new test asserts its own fixture split, so it cannot drift back into vacuity by editing the fixture.
   - Three residual instances exist at NIT level. None carries a load-bearing property alone, and each property is killed by some test:
     - N2-c: one comment overclaims for six of seven basenames.
     - N2-d: the `or {}` fallback would make the R3 test vacuous if the stop were ever absent, which it is not today.
     - N2-e: one loop runs over an empty list.
   - Judgement: the same family, but at a severity that does not trip the standing two-rounds trigger. I recommend no consult. Whether to record it as the class's third appearance is the magistrate's call.
2. **"The record contradicts itself"** (round-0 S2's latent row defect, round-1 D1): **D1 is cured.** The typed reason and the text now agree.
   - A mild neighbour remains (N2-a): the outcome says `envelopes_attempted: 0` while envelope 01's capture is on disk, and the seat calls an absent file "empty".
   - It is not the same shape: the reason and the text agree, nothing contradicts the cause, and it licenses nothing.
3. **Accounting boundary**, **exception escape** and **scope** (round-0 classes 1, 2 and 5): not touched this round. The seat lists exactly four code and test files plus the seat report. `git diff --stat 0e5578fb..c496f244` shows exactly those five files.
4. **New in round 2:** loosening the shared test harness (N2-b). It is a new kind of risk, not a repeat of an earlier class. Today it hides nothing (probe (e)). Under a targeted break it hides two cases while the mutation is still killed elsewhere (probe (h)).

---

## Verdict

**MERGEABLE.** D1, D2, D3 and N-b are all cured. Each cure is shown by a test that fails on the round-1 code and is killed by the targeted mutation. The executed on-disk state after an in-chain marking failure is refused, cold-gate-only and admits nothing, and the true cause is in both the refusal and the outcome. The two named modules pass: 265 tests, no skips.

N2-a to N2-e are optional bench-sized clean-ups, none required before merge:
- the `abort` row, or a one-word correction to the seat report (N2-a);
- the opt-in `None` in the harness (N2-b);
- the `assertIsNotNone` line (N2-d);
- a comment reword (N2-c).
