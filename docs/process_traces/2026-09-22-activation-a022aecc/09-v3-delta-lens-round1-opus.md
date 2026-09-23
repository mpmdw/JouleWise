# Delta re-audit of fix round 1: branch feat/2026-09-23-qpe01-registration-v3-nonobserver, 16900e3d..0e5578fb

Reviewer: Opus 5.5, read-only delta lens covering both contract and execution. Worktree `/Users/edr/code/JouleWise-wt-v3-a022aecc` at 0e5578fb. `git status` was clean before and after this review. Nothing was written inside any worktree. Mutation probes ran in a throwaway clone at `/tmp/delta-r1-mut`, which is clean after its `git checkout --` resets. Archive re-derivations ran in `tempfile` copies under /tmp.

**Terms used below.**
- **Round 0** is the original landing at 16900e3d. **Round 1** is F1–F16 plus the seat report (F11).
- **Whole** is `whole_envelope_observer_cpu_s`: the collector's own CPU plus the CPU of every child it reaped (`RUSAGE_SELF + RUSAGE_CHILDREN`).
- **Span** is the collector's own clock window for one envelope.
- **Floor** is Σ whole ÷ Σ span, in cores.
- **Companion** is `observer_floor_including_load_recorder_cores` = (Σ whole + Σ load recorder CPU) ÷ Σ span. It is reported only.
- **In-chain verdict** is the executor's per-envelope decision, taken while the night runs. **Summary** is `pilot_summary`, re-derived from disk after the night.
- **Mutation probe**: deliberately re-break the code, run the new tests, and see which test fails. A test "kills" the mutation if it fails. A mutation "survives" if every test still passes, which means no test guards that property.
- **Same signature**: a round-0 defect class that reappears in the same shape. Doctrine sends that to a consult, not to round two.

---

## BLOCKER

None.

## SHOULD-FIX

**D1. If observer marking fails in production, the chain aborts under the typed reason `non_observer_process_busy`, while the refusal text says marking failed. The typed reason is the code the D-182 addendum's successor lane (A270) will key on.** This defect comes from F16 interacting with the in-chain verdict. The seat saw the interaction (§7, "F16 in the chain") but left it open; it was not tested.
- Mechanism:
  - The in-chain verdict (`joulewise/quiet_predicate_campaign.py:1605`) calls `non_observer_busy` without `require_observer_marked`.
  - With an unmarked journal it therefore excludes envelopes 1 and 2 and raises `NonObserverAbort`, which sets `refusal_reason = NON_OBSERVER_EXCLUSION` (`:1647`).
  - The summary's new guard (`:1173`) then raises, and `:1672` overwrites `error` with "pilot summary failed: …". That discards the abort's own text naming the process, pid and core-seconds, but keeps the typed reason.
- Executed probe: the scratch clone, with the regression-3 fixture's marks all cleared. Output:
  ```
  PROBE envelopes in journal: [(1, ['fseventsd']), (2, ['fseventsd'])]
  PROBE write_refusal calls: [('pilot summary failed: recorder journal carries no observer-marked consumer; ancestry marking failed', {'reason': 'non_observer_process_busy'})]
  ```
- Consequences:
  - The refusal document contradicts itself: its reason says a daemon held the machine, and its text says the measurement's own marking broke.
  - The cause row now promises "a typed refusal naming the process, its pid and its core-seconds", but in this case that text is lost.
  - Once A270 lands, a marking failure (2 < 8 captured) would license the one new-plan successor. The successor would repeat the same failure.
- Nothing is admitted, so this does not block merge today, because no successor exists yet.
- Cure: run `require_observer_marked` in the in-chain verdict before `non_observer_busy`, raising a plain `ValueError` (not `NonObserverAbort`). Add the probe above as a test that asserts the reason is not `non_observer_process_busy`. Alternatively, the magistrate records this as a written precondition on A270.

**D2. Ruling 10's regression 1, run through production `pilot_summary` on the 21:00 night's own bytes, has lost its test.**
- Ruling 10 §5 item 1 reads: "archived journal … through v3 `pilot_summary` → twelve `non_observer_process_busy` naming `fseventsd`; prior night's rows (with regression 0's marking, or the explicit observer set) → zero."
- F16 turned the only test of that (`test_the_contaminated_night_loses_every_envelope_under_v3`) into `test_the_unmarked_archives_refuse_under_v3_rather_than_blame_the_sampler` (`tests/test_quiet_predicate_campaign.py:3599`), which only expects the refusal.
- What is left:
  - the synthetic regression 1 (`:3106`-area);
  - the diagnostic script, which uses its own join and its own observer rule, not production `pilot_summary`, and is not a unit test.
- Executed probe: I marked the ruling's seven observer basenames in a /tmp copy of each journal and re-derived under v3. The production rule then gives 21:00 → 12/12 exclusions naming `{fseventsd, mediaanalysisd}`, with `fseventsd` at 544.7–575.6 core-s; 02:17 → 0/12.
- So the property holds today, but no test pins it. Cure: add that marked-copy archive test, which is about 15 lines.

**D3. A new "passes for the wrong reason" assertion. The test claims the companion never feeds the stop, but it cannot tell.**
- The assertion: `test_the_residue_no_longer_subtracts_the_sibling_load_recorder` (`:3463-3467`) asserts `block_two_stop.causes == ["observer_floor_above_smallest_holdable_share"]` "never the companion".
- Why it cannot tell: on that fixture the floor (0.175) and the companion (0.175 + 0.0003) are both far above the 0.05 bar.
- Mutation M9 (below) wires the companion into `stop_branch` in place of the ruled floor. It survives the whole `tests.test_quiet_predicate_campaign` module: 152 tests, OK.
- The code is right today: `:1343` passes `observer_floor`. The ruling ("REPORTED only") is simply unguarded, despite a comment saying it is.
- Cure: a fixture where the floor is below 0.05 and the companion is above it, for example whole 29.9 s and load recorder 0.5 s per 600 s. Then the cause must be absent.
- This is the same defect class as Opus round-0 S2 (see the same-signature statement).

## NIT

- **N-a. The arm check still catches fewer exception types than t0.** `machine_quiet_check` (`joulewise/evidence_night.py:821`) catches `ProbeError, RuntimeError, SubprocessError, OSError, ValueError, TypeError, KeyError`; t0 (`night_gate.py` predicate block) catches `Exception`. An `AttributeError`, `IndexError` or `ArithmeticError` from the sampler would still escape `check()` without a `check.json`. The sampler's parsers raise `ValueError` deliberately, so this is hard to reach, and the result is fail-closed. `AssertionError` is left out on purpose so the test guard (F12a) can fire. A `except Exception` that re-raises `AssertionError` would match t0.
- **N-b. The generic refusal text names a skipped check as failed.** `evidence_night.py:1016` lists every check whose verdict is not `"pass"`, so when some other check fails, a `machine_quiet: skipped` row is listed as failing ("pre-arm checks failed: courier, machine_quiet"). The `passed` computation itself treats skipped correctly. This came in with F12(b).
- **N-c. The summary's `observer_definition` now reads as a self-contradiction.** `quiet_predicate_campaign.py:927` gives "…including collector, power recorder, load recorder and census; never subtracted, with the 30 s load recorder a sibling process reported beside it…". That is what the brief asked for: the ruled sentence verbatim plus the sibling fact. It is a string for the block-two consult the magistrate is holding, not a code defect.
- **N-d. Fable N7 is left as it was.** `test_regression_0_the_recorder_refuses_to_run_without_a_chain_root` (`:3074`) still has no guard against the production sampler. On the counterfactual (the pid guard removed), it would start the real recording loop and hang rather than fail. At HEAD it does not reach the sampler. `tests/test_quiet_predicate_campaign.py` has no module-level guard like F12(a)'s.
- **N-e. Fable N2 is left as it was.** The registration file's `ruling` string still differs from the `RULED_REGISTRATIONS` v3 entry's `ruling` (executed: `False`), and nothing compares them.
- **N-f. The fix brief is not quoted verbatim in the seat report.** §2 summarises it, and the round's WRITE_SCOPE (the exhaustive list of files the seat may edit) is asserted only in one sentence (§6.1: "This round's WRITE_SCOPE includes all three"). Every file round 1 touched is inside brief 04's scope plus the three files named in S5. `tests/test_arm_retry.py` was not touched this round. I could not check that against the brief the seat actually received.
- **N-g. The rewritten main regression-5 test still passes on its own under mutation M2** (the executor list passed through again), because on a clean night the executor and the summary agree. M2 is killed only by the new tampered-verdict twin (`:3311`). That is acceptable, because the property is guarded by that twin. Recorded so no one deletes the twin as redundant.

---

## Per-finding disposition

"Cured" means the defect is gone and a test or the executed evidence shows it. "Recorded" means the round's only obligation was to write the deviation down for ratification, and it did; the ratification itself is the magistrate's.

### Opus lens (round 0)

| Finding | Disposition | Commit, file:line | New defect from the cure? |
|---|---|---|---|
| S1 load recorder inside whole | CURED as ruled. Residue = whole − round_block (`quiet_predicate_campaign.py:1329`); `inside_whole` flags; companion (`:1335`); `components` text rewritten, and the four ruled strings are byte-identical (test `:3480`). Executed: residue share 0.12326 / 0.10701 = old 0.11601 / 0.09986 + load recorder 0.00725 / 0.00715; `load_recorder` never inside whole; round + residue − whole = 0.0. The (d) tautology is relabelled as "definitional", and a real counterfactual test (`:3434`) kills M1 | 38d5052c | Yes, D3 (the companion-not-a-stop assertion is vacuous) |
| S2 regression 5 circular | CURED. The summary always writes its own list; the executor's list is kept under `executor_non_observer_process_busy`, plus a disagreement flag (`:1179`). The tampered twin (`:3311`) kills M2 and M2b | 18029a86 | No (see N-g) |
| S3 arm-check exceptions escape | CURED for the families named (`evidence_night.py:821-823`); the test (`:332`) kills M3 | 15ef8f2b | Residual, narrower than t0 (N-a) |
| S4 refusal drops the observation | CURED. `Refused.evidence` is merged into the failing row (`:830`), and `verdict`/`reason` cannot be overwritten; M3b is killed | d41a64bb | No |
| S5 out-of-scope files | RECORDED (seat report §6.1); needs a written grant from the magistrate | 0e5578fb | No new out-of-scope file seen (N-f) |
| S6 regression 4, limb 3 | CURED as a labelled guard (`test_evidence_night.py:1088`), stated to be not defect-shaped | ff65cae9 | No |
| S7 no seat report | CURED. The report exists with a ledger, failing-before lines and deviations | 0e5578fb | It omits D1 as a defect (listed only as an open question) and D2 |
| N1 0.176 / 0.159 | RECORDED §6.2 | 0e5578fb | No |
| N2 `bar_basis` | RECORDED §6.3 | 0e5578fb | No |
| N3 v3 `records` | CURED (`night_gate.py` table + test `:1386`) | d156609b | No |
| N4 byte-equality on one night only | CURED as far as possible. Each night's guard status is asserted, and the docstring says 02:17's energies cannot be verified by this route | 3a4844c8 | No |
| N5 stale strings / README | CURED: README v3 plus the rules paragraph; summary `observer_definition` = ruled sentence + suffix (test `:3470`) | e53fefa9 | N-c (reads as self-contradictory, by brief) |
| N6 gate constant vs registration | CURED (`test_night_gate.py:1376`), labelled a drift guard | f6cdeef5 | No |
| N7 "four fields" comment | CURED | 28b84b98 | No |
| N8 floor test fails for the wrong reason on main | CURED: round clock support added; the seat reports main now fails on the number (0.0016667 ≠ 0.175) | 28b84b98 | No |
| N9 no end-to-end regression 0 | LEFT (seat §7, open) | — | — |
| N10 bind-loop cost / verdict race | PARTIAL. The race is now visible (disagreement flag) but nothing acts on it; the bind-loop cost is not examined | 18029a86 | No |

### Fable lens (round 0)

| Finding | Disposition | Commit, file:line | New defect from the cure? |
|---|---|---|---|
| S1 arm-check crash | CURED (same as Opus S3) | 15ef8f2b | N-a |
| S2 out-of-scope files | RECORDED §6.1 | 0e5578fb | — |
| S3 `supersedes` numbers | RECORDED §6.2 | 0e5578fb | — |
| S4 `bar_basis` wording | RECORDED §6.3 | 0e5578fb | — |
| S5 02:17 silently vacuous | CURED (status asserted per night, `:3537`) | 3a4844c8 | No |
| S6 README stale | CURED | e53fefa9 | No |
| S7 two scopes for the predicate | CURED. The arm check now reads the sealed `chain.zsh` with the gate's own `probe_payload_kind` (`evidence_night.py:786`); an ambiguous kind fails closed (`:990`); M5 and M6 are killed. Executed: both real archived `chain.zsh` files read `quiet_predicate_evidence`, and the generator always writes that declaration (`scripts/gen_evidence_night.py:53`), so real evidence nights are NOT skipped | dc6c4bb9 | N-b |
| N1 v3 not canonical | CURED (executed: v3 canonical True; the test asserts it for v2 and v3) | 2f31898b | No |
| N2 file `ruling` vs table `ruling` | LEFT (N-e) | — | — |
| N3 t0 share not bound | CURED | f6cdeef5 | No |
| N4 C3 PASS detail | CURED (`night_gate.py:1550`); M8 is killed by the calibration-text assertion | d0dc4a1a | No |
| N5 two shapes for one meaning | CURED (the key is always present; clean = `[]`) | 18029a86 | No |
| N6 regression-0 mechanism passes before | LEFT (documented in the ledger as not defect-shaped) | — | — |
| N7 hangs on the counterfactual | LEFT (N-d) | — | — |
| N8 no guard for "no observer marked" | CURED in the summary (`quiet_predicate_campaign.py:955`, `:1173`); M4 is killed by both new tests. Executed false-positive margin on the archives: `powermetrics` appears at rank ≤ 3 of 10 in every row where it runs, and 10th place is ≤ 0.0135 cores, so crowding the observers out of the top 10 for a whole envelope is remote | 2ff07212 | **Yes: D1** (the in-chain verdict has no matching guard) and **D2** (regression 1 on archive bytes lost) |
| N9 `observer_definition` strings | PARTIAL. The summary string changed (N-c). The collector strings (`scripts/sample_quiet_predicate_evidence.py:1064,1165`) are unchanged and not in scope; `:1165` is accurate | e53fefa9 | N-c |
| N10 `write_refusal` validation | No action needed | — | — |

### Magistrate items

| Item | Disposition |
|---|---|
| F10 abort cause text | CURED. Executed: the `arm_retry.COLD_GATE_CODES` cell equals the table cell in `docs/phase_2/derivation_night_runbook.md:1906` and in `docs/process/NIGHT_HANDBACK.md:108`, byte for byte. It names "ONE new-plan successor when fewer than minimum_retained envelopes were captured (installed by lane QPE01-ABORT-SUCCESSOR-01; until that lane lands the chain ends with no successor)". That matches main's D-182 addendum (worked example: 2 < 8 licenses one; 10 ≥ 8 licenses none) and TASK_QUEUE A270. `classify_abort` gives `cold_gate` |
| F12(a) production sampler | CURED for `tests/test_evidence_night.py`. The module-level guard raises an `AssertionError` subclass, and `LifecycleTests` inject the fake observation. Executed: no `top -l` process appeared during a 60 s poll of my four-module run, nor during the 30 s PrepareTests run (its time is `git clone` fixtures). No other test module calls `evidence_night.check`; `tests/test_quiet_admission.py:144` mocks `subprocess.run` |

---

## Same-signature statement

Round 0's defect classes and how each looks now:

1. **Accounting boundary misplaced** (Opus S1): not repeated. The code, the components text and the tests agree with the ruling. The one surviving false sentence (the ruled `definition`) is held by explicit ruling, not left by oversight.
2. **Exception escapes the arm check** (Opus S3 / Fable S1): cured for every family the sampler is written to raise. The residue (N-a) is the same site with a narrower-than-t0 catch. It is fail-closed and practically unreachable. Not escalation-grade.
3. **A test that passes without the property it claims** (Opus S2): this class **recurs in a new instance, D3.** The mandated regression-5 test is now real (the tampered twin kills M2 and M2b). But round 1 added a new assertion, "the companion is never a stop input", that survives the mutation it names (M9, 152/152 OK).
   - My judgement: this is the same defect class, but a different and lower-stakes instance. The round-0 instance was a brief-mandated regression proving nothing. This one is an auxiliary assertion on a reported-only field, whose code path is one visible line (`:1343`).
   - Every other new test killed its targeted mutation: 8 of 9 probes killed, the ninth being M9.
   - I recommend a bench fix (one fixture), not a consult. Whether it trips the standing two-rounds-same-signature trigger is the magistrate's call to record.
4. **Record contradicts itself** (Opus S2's latent row defect): the round-0 instance is cured. A new, unrelated instance comes from F16 (D1: the typed reason disagrees with the error text). Its mechanism is a different call site (executor versus summary), not a repeat of the round-0 shape.
5. **Scope beyond WRITE_SCOPE** (Opus S5 / Fable S2): no new file outside brief 04's scope plus the three recorded files. It cannot be verified against a verbatim fix brief (N-f).

Net: no round-0 defect survives in the same shape at SHOULD-FIX or higher. One class (the vacuous assertion) recurs in a new, minor instance.

---

## Executed evidence

**1. Four named modules, run once** (concurrently with the magistrate's full suite, hence the time):
```
$ cd /Users/edr/code/JouleWise-wt-v3-a022aecc && time python3 -B -m unittest tests.test_quiet_predicate_campaign tests.test_night_gate tests.test_evidence_night tests.test_arm_retry
...
evidence_end outcome=complete cleanup_proven=True network_time_restored=True
.......................................WARNING: runway below the 40-minute planning default
...................................................
----------------------------------------------------------------------
Ran 374 tests in 629.448s

OK
python3 -B -m unittest tests.test_quiet_predicate_campaign     186.37s user 200.37s system 61% cpu 10:29.94 total
```

**2. Registration canonical form and pins:**
```
v2 canonical True sha256 2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1
v3 canonical True sha256 69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
gate constant 69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
v2 superseded_by 69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
table sha 9ad277ce180bc5289e2e29391c20312a95a0847f72ba09bfeb32ade841e851a6
top-level diff vs 16900e3d ['observer_floor']
observer_floor subkeys differing ['components']
keys held back present? []
$ git grep -n -e 69321c69 -e b6cb513f -e 9491bc37 -- . ':!docs/process_traces'
configs/campaigns/quiet_predicate_evidence_01/README.md:9
joulewise/night_gate.py:67
tests/test_quiet_predicate_campaign.py:3355   (V3_REGISTRATION_SHA256)
```
There is no stale b6cb513f or 9491bc37 pin anywhere outside the trace. The table-digest test literal (`9ad277ce…51a6`) equals the executed value.

**3. Archive re-derivation** (`tests.test_quiet_predicate_campaign.archive_summary`, read-only archives, /tmp copies):
```
0217 v2 rules: status=REPLAY_NEVER_EVIDENCE observer_floor_cores=0.17572 observer_floor_including_load_recorder_cores=0.18297 observer_variation_cores=0.00214 block_two_stop=None
   stop_branch(observer_floor=0.17572, v2) -> {'outcome': 'no cutoff qualifies', 'causes': ['observer_floor_above_smallest_holdable_share'], 'pairs': None}
   max |round+residue-whole| = 0.0  load_recorder inside_whole any: False  mean residue share 0.12326
   v3 (unmarked, as archived): ValueError recorder journal carries no observer-marked consumer; ancestry marking failed
   v3 with observer basenames marked in a /tmp copy: non_observer exclusions 0/12, named []
2100 v2 rules: status=SPREAD_RECORDED observer_floor_cores=0.15909 observer_floor_including_load_recorder_cores=0.16624 observer_variation_cores=0.00267 block_two_stop={'outcome': 'no cutoff qualifies', 'causes': ['sized_pairs_above_24', 'observer_floor_above_smallest_holdable_share'], 'pairs': 517081}
   energies byte-equal: True True True
   max |round+residue-whole| = 0.0  load_recorder inside_whole any: False  mean residue share 0.10701
   v3 (unmarked, as archived): ValueError recorder journal carries no observer-marked consumer; ancestry marking failed
   v3 with observer basenames marked in a /tmp copy: non_observer exclusions 12/12, named ['fseventsd', 'mediaanalysisd'], fseventsd core-s 544.7..575.6
```
F16's guard fires on both unmarked archives, as the fix brief intended.

**4. Diagnostic script:**
```
$ python3 -B docs/process_traces/.../05-nonobserver-predicate-seat/diagnostic_reanalysis.py > /tmp/delta-r1-diag.json; echo rc=$?; diff /tmp/delta-r1-diag.json .../diagnostic_reanalysis.json && echo IDENTICAL
rc=0
IDENTICAL
```

**5. F16 false-positive margin** (archived journals, top_consumers are the top 10 of all processes):
```
0217 rows 238 with observation 236  top_consumers lengths {10: 236}  powermetrics rank max 1  absent rows 7  10th-place busy max 0.0135
2100 rows 245 with observation 243  top_consumers lengths {10: 243}  powermetrics rank max 3  absent rows 9  10th-place busy max 0.0102
```

**6. Mutation probes** (`/tmp/delta-r1-mutate.py` in the clone `/tmp/delta-r1-mut`; each mutation reset by `git checkout --`):
```
M1 residue subtracts load recorder again        KILLED by test_the_residue_no_longer_subtracts_the_sibling_load_recorder, test_the_floor_is_the_whole_envelope_over_the_collectors_own_span, test_both_archived_nights_re_derive_to_the_corrected_floor (both nights)
M2 summary passes executor list through         KILLED by test_regression_5_a_tampered_executor_verdict_is_caught_not_passed_through (only)
M2b summary never flags disagreement            KILLED by test_regression_5_a_tampered_executor_verdict_is_caught_not_passed_through
M3 arm check swallows unreadable observation    KILLED by test_the_arm_check_records_an_unreadable_observation_as_not_armable (all 3 subcases)
M3b refusal drops the observation               KILLED by test_the_arm_check_refuses_a_busy_non_observer_with_the_gates_own_text
M4 unmarked-journal guard disabled              KILLED by test_a_marked_journal_is_summarised_and_an_unmarked_one_refuses, test_the_unmarked_archives_refuse_under_v3_rather_than_blame_the_sampler (both nights)
M5 arm check ignores payload kind               KILLED by test_the_arm_check_spends_the_predicate_only_on_an_evidence_chain
M6 unreadable payload kind fails open           KILLED by test_an_unreadable_payload_kind_fails_the_arm_check_closed
M7 companion omits the load recorder            KILLED by test_the_residue_no_longer_subtracts_the_sibling_load_recorder, test_both_archived_nights_re_derive_to_the_corrected_floor
M8 C3 detail always claims the predicate        KILLED by test_the_non_observer_predicate_is_spent_only_on_an_evidence_night
M9 companion fed to stop_branch (:1343)         SURVIVES: tests.test_quiet_predicate_campaign, Ran 152 tests in 41.149s, OK   -> D3
```

**7. Marking failure in-chain probe** (D1): quoted under D1. A scratch test file in the clone, deleted afterwards.

**8. The three abort cause-text copies:**
```
docs/phase_2/derivation_night_runbook.md rows 1 identical True
docs/process/NIGHT_HANDBACK.md rows 1 identical True
names lane True | licenses ONE new-plan successor True
classify cold_gate
```

**9. F12(b) end to end:** `night_gate.probe_payload_kind` on the archived `chain.zsh` of 0217 and 2100 both give `quiet_predicate_evidence`.

**10. Tree state after review:** `git status --short` in the worktree is empty, HEAD is 0e5578fb, and the clone is clean.

---

## Verdict

**MERGEABLE AFTER FIXES.** Every round-0 SHOULD-FIX is cured or recorded for ratification, and every targeted mutation but one is killed. The v3 bytes are canonical, and the new digest is pinned consistently in the gate, the test literal and the README. The archive numbers match the ruling. The abort text matches the D-182 addendum in all three copies.

Before merge:
- **D2**: add the marked-copy archive test for ruling 10 regression 1.
- **D3**: add a floor-below, companion-above fixture so the "never a stop input" claim is real.

Both are bench-sized test additions.

**D1** needs either the one-line in-chain guard plus its probe test, or a written A270 precondition from the magistrate. Without one of those, the first marking failure after A270 lands would license a successor under the wrong reason.

The remaining ratifications (S5 scope, N1 and N2 wording) are the magistrate's and are recorded in the seat report.
