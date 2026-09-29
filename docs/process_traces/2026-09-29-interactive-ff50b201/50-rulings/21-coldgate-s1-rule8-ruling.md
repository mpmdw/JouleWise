ADDENDUM: S1-REPAIR-ROUTE-01-A2 ISSUED

# Cold gate S1-REPAIR-ROUTE-01-A2 — the second switch for tests whose subject is the window-level recomputation (rule 8)

Judge: Claude Fable 5.1 (`claude-fable-5-1`), cold, one non-interactive session, foreground only, no subagents, no background tasks. Session 2026-09-29, about 12:15 to 12:58 PDT by the host clock (about 43 minutes of the 60-minute budget). Python was `/opt/homebrew/bin/python3 -B` (3.14.7), always with the guard directory on `PYTHONPATH`. Scratch checkouts: `/tmp/cg-s1r8-ff50b201/B` (seat B, `d4345946`), `/tmp/cg-s1r8-ff50b201/A` (seat A, `c3137f46`), `/tmp/cg-s1r8-ff50b201/M` (main, `9eab16f8`). Every production edit below was made in a scratch copy and reverted (`git status` clean on B and A at the end). This file is the only repository file I wrote. No battery was read; no `systemsetup`, `sntp` or `powermetrics` was run.

**Verdict in one paragraph.** Seat B's three floor tests get the second switch, as an exception to rule 8 that I now write into rule 8 itself: the rule's name-based clause catches them by the letter, but the thing they test lives on the branch the switch leaves on, and I proved it by execution — with the switch on, the three production checks they guard each turn a test red when removed, and one of those checks (the two-row conflict at `whole_window.py:6072`) has no other test anywhere in the floor or selection modules. Seat A's F1 is not forbidden by rule 8 at all: the one closed-list function it is accused of touching runs before the switch is entered, its subject is the missing-bundle listing, and A1 itself classed it green under both switches. The second list goes to 11, which is A1's cap and not over it; I amend condition 9 to name the 11 so the list cannot grow by counting alone. No measured or published number moves. If an outcome is still red after R3-6, it goes to a per-ID cold gate with the refusing check named, not to the owner and not to a stop.

## 0. Contamination disclosure

Written before reading any gate material.

- Session: fresh non-interactive Claude Fable 5.1 session, worktree `/Users/edr/code/JouleWise-wt-cg-s1r8-ff50b201`, 2026-09-29.
- I did NOT open RUN_STATE.md, TASK_QUEUE.md, AGENTS.md, any memory file, or any skill file by my own action.
- Involuntary exposure: the harness injected into my system prompt (a) the full text of the user's global `~/.claude/CLAUDE.md` (multi-model orchestration rules, a writing standard), (b) the full text of this worktree's `CLAUDE.md` (Codex bridge routes), and (c) the index lines of the auto-memory `MEMORY.md` (one line per memory, about 100 lines, including titles such as "Verity-germane = mandatory (#421)", "Light gates for docs/tests (#415)", "Stop conditions are anti-spiral", "Sensible gates directive", "No artificial owner stops (D-183)"). I did not open any of the memory files those lines point to. The index lines give me one-line gists of owner directives that a truly blank judge would not have; where a gist could bias a call below, I say so at that point and rest the call on the documents the brief names instead.
- Bias I can name in advance: the memory index primes me toward "gates are anti-spiral, not round-counting", which is also what the brief's owner quote says, so the priming and the brief point the same way. I checked A1's own text for what rule 8 and condition 9 say before ruling (§1, §3).
- After the fact: no call below rests on a memory gist. The #421 reading in §6 rests on A1 §4.6, which the brief told me to read.

## 1. Terms used in this addendum

Terms of A1 (its §1) keep their meaning. The ones this text leans on, restated in plain words, and the new ones:

- **Bundle.** One run's directory (`config.json`, `metadata.json`, the summary, raw telemetry).
- **The gate.** The battery check `authenticate_window_members` in `joulewise/bundle_read.py`. It refuses a bundle whose battery pair says the laptop was charging or whose config is not bound.
- **Verdict row.** One line in `campaign_log.jsonl` that the campaign runner writes after a window, recording for the whole set of bundles whether the machine was idle (CPU admission), whether the power adapter stayed the same (adapter continuity), and whether the two reference runs at the ends of the window agree (the NEG-8 bracket). A reader never trusts the row; it recomputes and refuses on any difference.
- **The verdict check.** The function `whole_window_refusal_reasons` in `joulewise/whole_window.py`. It is the one public entry for reading a verdict row. Inside it, per row, `_validate_row_uncached` compares the row with what the member files say, and `_current_core_rederivation_reasons` does the deeper recomputation.
- **Current member.** A bundle for which `_current_strict_summary` answers true: reducer version `0.5.2` or `0.6.2` and a bound, non-mock config. This is A1's "second form".
- **The two branches.** Inside the verdict check there is a fork (A1 §3.1). **Short branch** (no member is current): the reader still compares the row's adapter-continuity decision with `stable`, still counts and de-duplicates the row's members, still recomputes the NEG-8 decision from the member summaries and compares it with the row, and still refuses two rows for one window that disagree. **Deep branch** (at least one member is current): on top of that it recomputes environment admission, CPU admission from idle records, adapter continuity from wattage, the calibration bracket and NEG-8 point drift, and demands the row carry the current four-field point-drift shape. "The window-level recomputation" in rule 8's title means the deep branch.
- **The second switch.** The test-only patch in `exemption_parity` that makes `_current_strict_summary` answer false for one named test ID (the ID must be on `PARITY_SECOND_FORM_TEST_IDS`, "the second list"). It forces the short branch. It does not touch the gate, the bundle's config binding, the mock barrier or strict validation.
- **Rule 8** (A1 §4.4): the second switch is refused to a test whose own source, or a fixture method of its class that it calls, names a function of A1 §4.2 (the eleven functions that ask the second form), or asserts a reason only the deep branch can raise, or whose subject is the verdict row under current evidence.
- **Mutant.** A deliberate one-place removal of a production check, made in a scratch copy, to see whether a test turns red. A test that turns red "kills" the mutant.
- **Charging pair.** A planted battery reading that says the laptop was charging. A repaired test must go red under it; that proves the gate is really exercised.

## 2. Executed evidence (this session, all in the foreground)

| Id | What I ran | Where | Observed |
|---|---|---|---|
| Z1 | The three floor IDs, unmodified | B | 3 FAIL. #1 `all_cells_extractable` is `False` (the clean half; the failed half passes). #2 gets `('adapter_continuity_failed', 'environment_admission_missing', 'whole_window_neg8_verdict_failed', 'whole_window_verdict_provenance_invalid')` instead of `('whole_window_verdict_conflict',)`. #3 gets `('environment_admission_missing', 'whole_window_verdict_provenance_invalid')`, no conflict. Matches seat B's F1 to F3 and packet A4. |
| Z2 | The same three with their IDs added to the second list in memory | B | 3 OK. |
| Z3 | The same three on main, with `_current_strict_summary` wrapped to log every answer and its caller (rule 7's recorder) | M | 3 OK on main. Calls: 26, 18, 10. **Every answer false.** Callers: `_current_core_rederivation_reasons`, `_reference_energy_evidence`. Rule 7 is met for all three: main ran them on the short branch. |
| Z4 | Five mutants, each against the three tests with the switch on | B | M1 `whole_window.py:6072` (`len(valid) != len(overlapping)` conflict return → `if False`): **#2 RED** `() != ('whole_window_verdict_conflict',)`. M2 the four `whole_window_verdict_conflict` adds in `:5791–5803` (NEG-8 stored-versus-derived) → `pass`: **#3 RED**. M3 `:5807` `adapter_continuity_failed` add removed: **#1 RED** (its failed half). M4 `:5748` (`derived_problem == "conflict"`) removed: none of the three red. M5 `:6077` (semantic-set conflict) removed: none of the three red. M4 and M5 are not claimed by these tests. |
| Z5 | The charging pair planted on every bound bundle, three IDs, switch on (seat B's own harness) | B | 3 RED, all `WindowBatteryRefusal: battery_float_confounded`. The switch does not reach the gate. |
| Z6 | Census: `_current_strict_summary` wrapped; every call whose enclosing function is `_current_core_rederivation_reasons` recorded with its answer; run over `tests.test_floor_extraction`, `test_whole_window`, `test_whole_window_selection`, `test_idle_admission` (327 tests, 7 min) | B | 19 tests reach the deep branch (at least one true answer inside `_current_core_rederivation_reasons`). 16 are green; the 3 red ones are exactly seat B's three (they reach the deep branch on the candidate only because round 3 bound their bundles; on main, Z3, they never did). Green list in §3.4. Also observed: 3 ERRORs in `test_whole_window.LaunchLineageWholeWindowTests` (`test_neg8_bound_authenticates_every_member_and_seals_full_lineage`, `…_refuses_marker_without_direct_receipts`, `…_refuses_mixed_full_lineages`), cause `WindowBatteryRefusal: battery_float_evidence_missing (pair not bound (config.json does not re-validate: schema_version must be a non-empty string))` on ten members. Not in this gate's charge; recorded for the lead in §8. |
| Z7 | Mutant M1 against the 17 green tests that reach the deep branch (Z6) | B | run 17, **0 killed**. No deep-branch test guards the two-row conflict return at `:6072`. |
| Z8 | Mutant M1 against the whole of `test_floor_extraction` + `test_whole_window_selection` (235 tests) with the three IDs switched | B | **Killed by exactly one test:** `test_later_passed_row_cannot_supersede_failed_whole_window_row`. Without the switch that test is red for another reason (Z1), so on the candidate as it stands `:6072` has no living guard in those two modules. |
| Z9 | Seat A's F1, unmodified, then with its ID on the second list in memory | A | Unmodified: 12 sub-test outcomes RED, each `0 != 4` (estimator `n`). Switched: OK. 4 min 06 s wall for the pair. Matches seat A's F1 and packet A5. |
| Z10 | Reading, not execution: F1's source (`tests/test_analysis_integration.py:4944–5013`) and the helper it calls (`:175–207`) | A | `prepared_session` is built by `prepared_minted_consumption_session` at `:4957`, **before** the `with exemption_parity(...)` block opens at `:4963`. That helper is the place `_prepare` is named. So the closed-list function `_prepare` runs with the switch **off**, on the real second form, for the full 30-bundle set; the test then removes one bundle and hands the already-prepared session to `analyze_claims` through the class patch. The switch never reaches `_prepare` in this test. Of the 8 integration IDs that are on or proposed for the second list, F1 is the only one that patches the class or calls the helper (checked by source split), so the lead's withholding was not inconsistent with the other grants; it was a letter-reading of "names a function of §4.2". |
| Z11 | List counts on both seat trees | A, B | First list 35, second list 6, identical on both. All five IDs in this gate are on the first list; none is on the second. |

NOT EXECUTED: rule 7's recorder for F1 on main (packet A5 cites item 121 #8 for it; I did not re-run it, cost about 90 s, and nothing in my ruling on F1 turns on it because A1 §5.1 already classed F1 under both switches). Mutants M2 to M5 against the deep-branch census (only M1 was run there, because M1 is the one check whose only guard is a switched test). The full suite. Any bench step.

## 3. Ruling 1 — seat B's three IDs

### 3.1 What rule 8 says, clause by clause, against each test

| Clause of rule 8 | #1 `test_failed_adapter_continuity_refuses_but_clean_core_passes` | #2 `test_later_passed_row_cannot_supersede_failed_whole_window_row` | #3 `test_whole_window_rederives_neg8_verdict_from_member_summaries` |
|---|---|---|---|
| (a) own source or class fixture method names a §4.2 function | **No.** It calls `extract_cells`; its class fixtures `_whole_window_row` and `_extract_cells_corpus` name no §4.2 function. (The module helper `prepared_minted_consumption_session` names `_prepare`, but it is not a method of the class, and `_extract_cells_corpus` passes it as a `side_effect`.) | **Yes, by the letter.** Calls `whole_window_refusal_reasons` and the helper that names `_prepare`. | **Yes, by the letter.** Calls `whole_window_refusal_reasons`. |
| (b) asserts a reason only the deep branch can raise | **No.** `adapter_continuity_failed` is raised on the short branch at `:5807` (Z4 M3 proves it with the switch on). | **No.** `whole_window_verdict_conflict` is raised on the short branch at `:6072` (Z4 M1). | **No.** `whole_window_verdict_conflict` is raised on the short branch at `:5803` (Z4 M2). |
| (c) subject is the verdict row under current evidence | **No.** On main no member was current (Z3); the rows are hand-written in the old shape. | No, same. | No, same. |

So clause (a) catches #2 and #3, and only by naming. Clause (a) is over-broad for one reason: `whole_window_refusal_reasons` is the single public entry to the verdict check, both branches. Any test of the short branch must name it. Read literally, clause (a) would refuse the switch to every test of the short branch, which is the branch the switch keeps on. That cannot be the rule's purpose. Its purpose, stated in A1 §6 item 8 and by the one example A1 refused (`test_authenticated_v2_whole_window_source_reaches_claim_consumption`, whose subject is a *current* window source reaching claim consumption), is: the switch must not delete what a test tests.

### 3.2 The route: second switch, granted, with rule 8 amended

**Granted** to all three IDs. Reasons, in order of weight:

1. **The switch does not delete what they test; it is the only thing keeping one of the checks tested.** With the switch on, each test's guarded production check still bites when removed (Z4, M1 to M3). And for the two-row conflict at `:6072`, the switched #2 is the **only** test in 235 across the floor and selection modules that kills the mutant (Z7, Z8). Refusing the switch to #2 does not preserve coverage of the deep branch; it leaves `:6072` with no test at all.
2. **Rule 7 is met** (Z3): main ran all three on the short branch. The switch restores main's branch for main's tests. Nothing is lost relative to main.
3. **The battery gate is real under the switch** (Z5): three of three red under the charging pair.
4. **The other routes are worse.** Evidence-forward fixture repair (members carrying environment admission, idle records, adapter wattage, a clock anchor and a current-shape row) is the "extend the builder" route A1 §4.1 rated high-risk and sent to lane CLAIM-CHAIN-CANARY-01; it would also change what these tests are about, from the short-branch checks to the deep ones, for which green tests already exist (§3.4). Re-classing into refusal assertions would delete the clean half of #1 and the specific single-reason assertion of #2. Gating them (leaving them red or skipped) leaves `:6072` unguarded, item 1.

**Rule 8, amended text.** Replace A1's rule 8 with:

> 8. **Never the test's own subject.** The second switch is refused to a test whose subject is the deep branch: the recomputation of environment admission, CPU admission, adapter continuity, the calibration bracket or NEG-8 point drift, or the verdict row under current evidence. A test's own source or a class fixture method naming a function of §4.2, or asserting a reason the deep branch raises, **triggers the check below; it is not the verdict.** The verdict is by execution, recorded in the pull request: (i) on main the recorder of rule 7 answered false for every bundle the test read; (ii) with the switch on, the test is green; (iii) with the switch on, for each reason or acceptance the test asserts, a one-place mutant of the short-branch check that produces it turns the test red. A test that fails (i), or whose asserted outcome no short-branch mutant can turn red, is refused. `test_authenticated_v2_whole_window_source_reaches_claim_consumption` remains refused (its subject is a current source).

For this gate, (i) is Z3, (ii) is Z2, (iii) is Z4 M1 to M3. The lead records those three rows in the pull-request ledger; the seat may re-run them but need not.

### 3.3 Coverage lost for these three while switched

With the switch, the three tests run the short branch, as on main. What they no longer exercise on the candidate (and never exercised on main): the deep branch's recomputation of environment admission, CPU admission from idle records, adapter continuity from wattage, the calibration bracket, NEG-8 point drift, and the current-shape row requirement. For their own subjects, nothing is lost: adapter decision compared with `stable` (#1, `:5807`), two-row conflict (#2, `:6072`), NEG-8 decision recomputed from member summaries and compared with the row (#3, `:5803`) all stay tested, by execution.

### 3.4 Where deep-branch coverage lives (rule 9, executed)

Sixteen green tests on the candidate reach `_current_core_rederivation_reasons` past its early return (Z6). At least one asserts acceptance and at least one asserts refusal, as rule 9 requires:

- **Accepting:** `test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_current_whole_window_rederives_cpu_and_adapter_labels` (asserts the clean core yields `set()`, then `cpu_admission_core_failed` and `adapter_continuity_failed` on forged cores — the deep-branch twin of #1); `test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r1_explicit_minted_fresh_valid_session_is_prepared_and_accepted` (asserts `reasons == ()` and `session.ready`).
- **Refusing:** in the same floor class, `test_current_campaign_log_malformed_row_refuses_join`, `test_current_claim_refuses_registered_exploratory_policy_row`, `test_current_neg8_summary_disagreement_maps_to_whole_window_conflict` (the deep-branch twin of #3), `test_current_whole_window_rejects_nonempty_core_conditions`, `test_bracket_max_exceeding_minted_member_bound_refuses`, `test_inflated_metadata_effective_bound_is_provenance_invalid`, `test_whole_window_core_rejects_duplicate_member_occurrences`; in `test_whole_window_selection`: `MaxBracketConsumptionTests.test_b1_r3_implicit_minted_without_session_is_refused`, `test_b1_r4_implicit_minted_fresh_valid_session_matches_explicit`, `test_minted_secondary_verifier_refuses_missing_session`, `test_minted_semantics_loads_and_refuses_pending_ledger_snapshot`; `SalvageSemanticsDispatchTests.test_b5_real_row_rejects_same_policy_binding_substitution`, `test_explicit_salvage_dispatch_selects_only_salvage`; `WholeWindowSelectionTests.test_custody_triangle_disagreement_survives_mixed_current_path`.

**One gap, named and assigned.** No deep-branch test kills M1 (`:6072`, two valid rows for one window) (Z7). #2 has no current-evidence twin. That is a pre-existing gap on main (Z3 shows #2 was always short-branch), not one the switch opens. It goes to lane CLAIM-CHAIN-CANARY-01 as a one-line item: "a deep-branch twin of `test_later_passed_row_cannot_supersede_failed_whole_window_row`". Not inside S1.

## 4. Ruling 2 — seat A's F1

**Rule 8 does not forbid it. The second switch is granted** to `tests.test_analysis_integration.AnalysisIntegrationTests.test_incomplete_pair_is_listed_and_never_converted_to_unpaired_samples_with_production_telemetry_identity`.

1. **The accused function runs unswitched.** `_prepare` is called by the helper at `:175–207`, invoked at `:4957`, before `exemption_parity` opens at `:4963` (Z10). The switch never reaches the only §4.2 function this test comes near. The class patch at `:4969` substitutes an already-prepared session for the one `inputs.py` would build; it names the class, not `_prepare`.
2. **Its subject is the incomplete-pair listing**, not the verdict row: it asserts `n == 4`, `df == 3`, the missing block not included with `bundle_missing`, `fixed_n_plan_incomplete`, outcome `not_resolvable`, over 12 contrasts. None of these is a deep-branch reason. What the deep branch does to it is attach `cpu_admission_core_failed`, `environment_admission_failed`, `environment_admission_missing`, `whole_window_verdict_provenance_invalid` to all 29 remaining bundles (seat A's diagnosis), which zeroes `n`. That is the pilot mechanism of A1 §3.1, not this test's subject.
3. **A1 already classed it under both switches.** A1 §5.1 lists `incomplete_pair_is_listed…` (12) in sub-class T5a, "GREEN … both switches by ID under rules 7 and 8", and refused only `test_authenticated_v2…` under rule 8. The lead's item-9 withholding was more conservative than A1; this addendum aligns the list with A1.
4. **Executed:** 12 red unmodified, green with the switch (Z9), no assertion changed.

The amended rule 8 (§3.2) covers this case directly: the class name is a trigger, and the executed check clears it. Rule-7 evidence for F1 rests on the lead's item 121 #8 (NOT re-executed by me, §2).

## 5. Ruling 3 — condition 9

Condition 9 (A1 §5.4) says: the second list "holds more than **11** IDs (the 7 of T5a and the 4 of F): return to a cold gate. The second switch is for the integration corpus and is not to spread."

- **The number.** 6 today (Z11) + 2 (A5: F1 and F2) + 3 (this ruling) = **11**. "More than 11" is not reached. Within the cap.
- **The intent.** The 11 was sized as 7 T5a + 4 F, all in `tests/test_analysis_integration.py`. After A5 the list holds 7 T5a + 1 F = 8; three of the four F IDs went green without the second switch (rule 10), so three slots are numerically free. The three floor IDs fill those slots but are **outside** the integration corpus, which is exactly the spread the sentence warns against. That is why this question belongs to a cold gate, and it is now decided here, once: the three floor IDs are admitted by name, for the reasons of §3.2, and no floor ID beyond them is.
- **Condition 9, amended text:**

> 9. `PARITY_SECOND_FORM_TEST_IDS` is a closed list of at most **11** IDs: the 7 T5a IDs and the 4 F IDs of `tests/test_analysis_integration.py` (A1 §5.1) plus the 3 IDs of `tests/test_floor_extraction.py` named in S1-REPAIR-ROUTE-01-A2 §3, with the 3 unused F slots retired. Any other ID, from any module, returns to a cold gate before it is added, whatever the count. A count of 11 is not itself a trigger.

## 6. #421 — whether any measured or published number is at stake

**No number moves.** The five tests are refusal-path tests on hand-written fixtures: energies 40.0, 40.04 and 45.0 J in the floor tests, and the analysis corpus's fixed-n plan in F1. No paper literal, pin, registry digest or calibration value is read or written by any of them. Both seat branches change only `tests/` and one fixture golden report (seat B's leaf diff: five `battery_float_members` pass rows and `summary_sha256`, per its commit message; not re-checked by me).

What is verity-germane is the **coverage of the claim path**, and the check that covers it is stated per item:

| Concern | Check | Status |
|---|---|---|
| The battery gate on claim paths stays real under the switch | Z5: charging pair → `battery_float_confounded` on all three floor IDs; seat A reports the same for F1 (`battery_float_confounded` ×30) | Executed by me for B; by seat A for F1 |
| The short-branch checks these tests guard stay guarded | Z4: M1, M2, M3 each killed with the switch on | Executed |
| The deep branch keeps green tests that run it switched on | Z6: 16 green tests, accepting and refusing | Executed |
| The one short-branch check with no other guard (`:6072`) | Z8: guarded only by the switched #2; deep-branch twin owed to CLAIM-CHAIN-CANARY-01 | Executed; item assigned |
| A1 §4.6, "no test may pass on evidence a real window could not produce" | By the letter, still not met, for the same tests and the same reason as on main and as A1 already disclosed: the deep-branch checks are off for these five while switched. The owner's reading (production acceptance, not fixtures) stands until the owner overturns it. This addendum widens A1's table by 3 IDs outside the integration corpus; the pull-request sentence of A1 §6 item 7 must state M = 11 and name the floor module. | Policy unchanged; disclosure widened |

## 7. If a grant still leaves a failing outcome after R3-6

Not "stop". The route by kind of residue:

1. **A refusal on one of these five IDs that survives both switches** (a third form, A1 rule 11): the seat returns it by test ID with the refusing check's function and line; the lead convenes a **per-ID cold gate** (the same shape as this one, 60 minutes, a scratch checkout). If more than 3 IDs share one refusing check, condition 8 fires and it is **one cold gate for the class**, not three.
2. **A failure whose cause is not the verdict check** (a gate refusal like Z6's three `LaunchLineageWholeWindowTests` errors, a fixture-shape error, a pin): it is not this ruling's class; the lead sorts it by the A3 rules for its own class, and only if that class has no rule does it go to a cold gate.
3. **The condition-2 count.** Counted as the orchestrator's A0 ruling says, outcomes still failing after R3-6. If after the grants of A2 to A5 that number exceeds 10, the question is not "how many rounds" but "is there a fourth kind of leniency nobody has found" — a **consult** (one fresh reader with A1 §3.1's drawing and a recorder over every `whole_window.py` branch on bundle identity, A1 §6 item 1's last row) before any cold gate, because a gate cannot rule on a mechanism nobody has described.
4. **The owner** is asked only one thing, and only if it arises: whether to keep A1 §4.6's reading of #421 as the list grows past the integration corpus. That is a policy question, not a test question. Nothing else in this class needs the owner.

Round counting is not a route. Condition 2 and rule 11 exist to catch a mechanism nobody has explained; once the mechanism is explained and the fix is executed, the count resets to the surprises that remain.

## 8. Corrections and notes for the lead

1. Packet A4 §2 says `adapter_continuity_failed` is asserted at `test_floor_extraction.py:1417`. That line is inside the `_whole_window_row` fixture; the assertion sites are `:1523` (#1) and `:1726` (the deep-branch twin), plus `test_run_campaign.py:10001` on seat B's tree (not `:9817`).
2. Packet A4 §2 reports the mutants' effect only with the switch on, as I did. Add: M1 is killed by nothing else in the floor and selection modules (Z8). This is the strongest fact for the grant and the packet did not have it.
3. Three ERRORs in `tests.test_whole_window.LaunchLineageWholeWindowTests` on seat B's tree (Z6) are gate refusals (`battery_float_evidence_missing`, config `schema_version` missing) on ten members. Outside this gate. Bench L's later commit `478f5709` ("fence real sudo/powermetrics starts in three whole-window test modules") may or may not cover them; the lead checks before R3-6.
4. Seat B's report lists the pilot residue as "3 failures, no errors in 178 tests" for the floor module; my census over four modules reproduces the 3 failures and adds the 3 errors above, which live in a different module.
5. Clause (a) of the original rule 8 also catches, by the letter, every test in `test_floor_extraction.py` that calls `whole_window_refusal_reasons` — including all the deep-branch tests of §3.4 that need no switch. The amended rule removes that trap.

## 9. Plain summary

Seat B's three floor tests and seat A's F1 all get the second switch: I ran them, they pass with it, the battery gate still refuses a charging pair under it, and each production check they guard still turns a test red when removed — one of those checks has no other test anywhere.
Rule 8 is rewritten so that naming the verdict function only triggers an executed check instead of deciding the answer, and condition 9 becomes a closed list of 11 named IDs rather than a count.
No measured or published number changes; a residue after R3-6 goes to a per-ID cold gate with the refusing check named, or to a consult if it is a new mechanism, never to a stop or to the owner.
