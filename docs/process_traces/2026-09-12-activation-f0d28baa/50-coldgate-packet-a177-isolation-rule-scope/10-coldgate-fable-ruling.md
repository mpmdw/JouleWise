# 10 — Cold-gate Fable ruling on packet 50: scope of the isolation rule over a test's own terminal oracles and mirrored formulas

Convened 2026-09-12 (rule 11, fresh session) in the detached worktree `/Users/edr/code/JouleWise-wt-coldgate-a177` at `74a547cd` (PR #324 head).
Packet digest of `00-PACKET.md` + exhibits A, B, D: `3b72345562c0d8f53f3d369f4dd703289a436bf587a96f76044e0b7471e1b422` (matches the convening digest `3b72345562c0d8f5`).

## Contamination disclosure

This session was launched with the user-level and project-level `CLAUDE.md` files and the memory index `MEMORY.md` injected by the harness, as every session is. From those I knew before opening the packet: that an "A177" desk seat exists in a worktree `wt-a177` and is one of three seats running today; the four commit subjects of the FIXTURE-SENTINEL-CONTROLLER-01 series visible in the worktree's `git log` (including the phrase "33 in-memory cuts each killed by a named assertion" and "rule-11 consult 39"); and a one-line memory pointer that mutation sweeps must collapse every `max`/`min` to each operand because an isolation rule stated over terms is insufficient (the lesson of Exhibit C, record 88). I did not read `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/`, `docs/decision_log.md`, any other process trace, `.claude/`, any memory file beyond the index, or the delta/consult drivers under `/private/tmp`. I had no knowledge of the content of audits 33, 37, or 46, of consult 39, or of ruling 69 beyond what the exhibits show, and no prior position on Q1–Q3. The user-level `CLAUDE.md` writing standard (plain words, define at first use) applies to this document and I have followed it.

## Q1 — does the isolation rule's "clause" include a test's own terminal oracles?

**Reading: no. The texts already decide it, and no amendment is needed.**

Terms, defined once. A *terminal oracle* is an assertion at the end of a test that reports whether what the test observed matches what it expected (`assertEqual`, `assertGreater`, `assertIn`, and the `expected` list a parametrised case is compared against). The *mechanism* of a test is everything that decides what the oracle gets to see: fixtures, subclass wiring, environment patches, recorded witnesses, and the arithmetic that turns a raw observation into the number the oracle compares. A *cut* is one deliberate edit made to a copy of the source so a test can be run against it; a cut is *killed* when the test fails on the edited source and *survives* when it still passes.

Ruling 69 Q2 (Exhibit A) opens with the definition that settles this: "A *clause* is one boolean term of a refusal condition." A refusal condition is a check that decides whether an input is admitted or refused. Clause (1) then says every added clause "is named by a test whose counterfactual is refused by that clause ALONE: with that single term deleted and every other line intact, the test fails." In that sentence the test is the *killer* and the clause is the *thing cut*; the two roles are distinct. A5 (Exhibit B) keeps the same shape: the re-audit "re-cuts, one term at a time, every clause the round's diff adds or changes … running the single test selected for each cut." Nothing in either text asks a test to be killed by a second test, and the definition of clause does not reach an assertion, because an assertion refuses nothing; it reports.

Audits 33 and 37 extended the rule from production clauses to the test's own mechanism (deletable stress wiring; a validator mock replaceable by a canned `[]`). That extension is sound under the definition: wiring that decides which capture is stressed, and a mock that decides what the validator returns, are fence-like terms in the sense of Exhibit A ("any check that refuses an input before a later check sees it"); they decide what the oracle observes. A surviving cut on them means the test does not exercise what it claims. Extending one step further, to the oracle itself, breaks the rule's own structure: the only "single test selected for each cut" that could kill "delete assertion X" is a test asserting that X asserts, which is the regress consult 39 (Exhibit E) refused and audit 46 (Exhibit D) itself warns would "repeat the overbuild problem."

The oracle is not unprotected under this reading. It is protected transitively by the mechanism cuts: a mechanism cut is killed only if some assertion fails on it, so deleting or weakening an assertion turns every cut it was the named killer for into a *surviving mechanism cut*, which clause (3) already scores as `should_fix`. Exhibit E's table is exactly that record: each of the twelve added expectations is the first-failing assertion for at least one atomic cut of mechanism or falsified input (for example `Scale >= 12` kills `stress_patch`, `stress_scope`, `record_scale`, and `floor`; `First strict result []` kills `command_forward`, `no_sleep`, and `strict_before`). The right experiment for "is this assertion load-bearing" is therefore not "delete it and see if the test passes" (it always will) but "delete it and see whether any recorded cut now survives." An assertion for which no cut can be named is dead and is deleted, which is the oracle-side analogue of Exhibit A's "a term nothing can isolate is either dead or unruled."

Boundary between the two classes, for the record: an edit to how the *observed* side of a comparison is produced (the recorded count, the parsed argv, the `nominal_s * scale` product) is a mechanism cut and needs a named killer; an edit to the *comparison itself* or its *reference* side (delete the assertion, `strict=True → False`, canned `[]`, `expected == expected`, the inequality's right operand replaced by `0`, a parametrised case removed) is an oracle edit and is discharged by the killer record. Audit 46's `stress_timeout_zero` and all of R2 fall on the oracle side; `record_timeout` (the wiring records zero) falls on the mechanism side and does have a killer today.

**The one sentence to record as the reading of ruling 69 Q2 / A5 for this case:** Under ruling 69 Q2 and A5, a *clause* is a term that decides what is admitted or observed, which covers production refusal terms and, as audits 33 and 37 applied it, a test's own wiring, fixtures, mocks, and observation arithmetic, but not the test's terminal oracles; an added oracle is discharged not by a second test that watches it but by the fix-round record naming at least one atomic cut of mechanism or falsified input on which that oracle is the first assertion to fail, and an oracle for which no such cut exists is dead and is deleted.

## Q2 — the mirrored formula and the inequality (Exhibit D R1)

**Ruled shape: (ii), in its smallest form. Delete the mirrored formula; read the timeout through production's own function; keep the inequality.** No second regime is added, and the inequality is not deleted.

Facts verified in the repository at `74a547cd`:

- Production has one home for the deadline: `joulewise/adapters/powermetrics.py:1468-1470`, `_capture_timeout_s(config, count)` returning `max(15.0, nominal_s * 1.5 + 10.0)`. `_run_bounded_capture` (`:1190-1201`) builds the argv with `_command(config, capture_path, count=count)` and takes its subprocess timeout from `_capture_timeout_s(config, count)` with the same `config` and `count`.
- The formula is already protected by a production test that covers **both operands of the `max`**: `tests/test_run_campaign.py:9636-9646`, `test_real_powermetrics_capture_timeout_is_unchanged`, asserts `_capture_timeout_s(config, 100) == 17.5` (the affine operand wins: 100 × 0.05 s = 5 s, 5 × 1.5 + 10 = 17.5) and `_capture_timeout_s(config, 3) == 15.0` (the floor wins: 3 × 0.05 s = 0.15 s, 0.15 × 1.5 + 10 = 10.225, so `max` returns 15.0). Record 88's operand-collapse cuts are killed there: collapsing `max` to `15.0` fails the count-100 case; collapsing it to the affine operand fails the count-3 case. In addition, `tests/test_idle_admission.py:546-562` asserts that the real `subprocess.run` receives `timeout == 17.5` for a count-100 capture, so the formula's consumption by production is also tested. (I read these tests; I did not run them.)
- The regression's mirror at `tests/test_controller.py:1688-1689` is therefore a second home for a formula that already has one home and full operand coverage. In the regression's own regime the count is host-derived (89 to 94 at 20 Hz, so nominal 4.45 to 4.7 s and a deadline of about 16.7 to 17.05 s), the floor is inactive, and the `15.0` term is dead in this test. Audit 46's `formula_floor` survivor is correct and its cure is deletion of the duplicate, not a conditioned second regime (option (i)), because that regime already exists at `test_run_campaign.py:9646`.
- The witness value `capture["timeout_s"]` at `:1651` is already computed by calling production's own `_capture_timeout_s`. So the only thing the mirror line adds today is a killer for the wiring cut "record the timeout as zero" (`record_timeout`, killed by "Timeout formula equality" in Exhibit E). The smallest shape removes the recorded operand instead of adding a watcher for it: read the deadline once, in the test body, from production, for the same config and count production used.

**Exact code change** (the seat applies it; this ruling makes no edit):

```diff
@@ StressedSentinelAdapter._command (tests/test_controller.py ~:1646-1652)
                     bounded_captures.append({
                         "count": count,
                         "interval_s": self._interval_ms(config) / 1000.0,
                         "scale": float(os.environ["FAKE_POWERMETRICS_SLEEP_SCALE"]),
-                        "timeout_s": self._capture_timeout_s(config, count),
+                        "config": config,
                         "argv": argv,
                     })
@@ regression body (tests/test_controller.py ~:1687-1693)
         nominal_s = capture["count"] * capture["interval_s"]
-        # Production _capture_timeout_s: max(15.0, nominal_s * 1.5 + 10.0).
-        self.assertEqual(capture["timeout_s"], max(15.0, nominal_s * 1.5 + 10.0))
+        # Production's own deadline for this capture. One home:
+        # powermetrics.py _capture_timeout_s; both max operands are pinned by
+        # test_run_campaign.test_real_powermetrics_capture_timeout_is_unchanged.
+        timeout_s = registry.adapter._capture_timeout_s(capture["config"], capture["count"])
         self.assertGreater(
-            nominal_s * capture["scale"], capture["timeout_s"],
+            nominal_s * capture["scale"], timeout_s,
             "this bounded capture must time out if --no-sleep is removed",
         )
```

After this change no `15.0`, `1.5`, or `10.0` exists in the test, so there is no formula term to cut in the test; `capture["count"]` is still cross-checked against the argv `-n` value (`:1681-1683`) and against `drift["post_sample_count"]` (`:1694`), and `capture["interval_s"]` against the argv `-i` value (`:1684-1687`), so the two inputs to the production call are witnessed, not asserted by fiat. `registry.adapter` is the `StressedSentinelAdapter` instance that ran (asserted at `:1714-1715`), and `config` is `args[0]` of the same `_command` call production made at `:1200`, so the body's call is production's call at `:1201` repeated with identical inputs.

**Why keep the inequality (not option (iii)).** The inequality is the regression's only guard on its own detection power. It says: with `--no-sleep` removed, this capture would run past production's deadline. If a future change raised production's deadline, or lowered the fixture stress, the cure would silently stop being load-bearing and the test would keep passing while no longer detecting report 19. The inequality turns that silent decay into a failure. It costs three lines and has a real production counterfactual, given next.

**Isolating counterfactual for what the regression keeps.**

- For the inequality, a *production* counterfactual: raise the floor in `_capture_timeout_s` from `15.0` to `60.0` (or the offset from `10.0` to `50.0`). Arithmetic for the observed run: count 94 × 0.05 s = 4.7 s nominal, × 12 = 56.4 s stressed, against a deadline that becomes 60.0 s, so `56.4 > 60.0` is false and the inequality fails while every other assertion still passes (the cure holds, so the capture succeeds, drift is `bounded`, strict validation is `[]`). With count 89 the stressed duration is 53.4 s; same outcome. NOT EXECUTED here (read-only session); it is an in-memory cut of `powermetrics.py:1470` for the seat's sweep.
- For the `--no-sleep` cure, the ground-truth counterfactual already observed by both Exhibit D (V3) and Exhibit E (V3): remove the bounded `--no-sleep`; the stressed capture (about 56 s) exceeds the 17 s deadline, `subprocess.TimeoutExpired` is raised, drift becomes `{'status': 'unknown', 'reason': 'post_idle_unavailable'}`, and strict validation returns two reason strings, so `First strict result []` fails. The inequality is the prediction; this cut is the proof.
- For the two witnessed inputs of the production call: `record_count` (count + 1) is killed by the argv `-n` equality, and `record_interval` (conversion doubled) by the argv `-i` equality (Exhibit E rows 10 and 11). Both survive this change unchanged.

## Q3 — classification (for the record)

Audit 46's "same-signature: YES" is half right and should be split. R1's mirrored-formula finding (`formula_floor` survives) **is** the same class as audits 33 and 37: a term of the test's own mechanism that nothing in this test can isolate, and whose cure is the same as theirs, delete the term rather than add a watcher; here the term is a duplicate home for a production formula whose only home and both operands are already tested elsewhere. R1's `stress_timeout_zero` and all of R2 (deleting any of the twelve expectations, `strict=True → False`, canned `[]`, `expected == expected`, deleting a policy case) are a **different** class: edits to the oracle itself, which ruling 69 Q2 / A5 does not cover and which the fix-round record already discharges through the killer column of Exhibit E. Under the Q1 reading these are not findings, not `should_fix`, and not nits; they are the expected result of cutting the killer instead of the clause. Record 88's operand-collapse lesson is not weakened by this: its cuts apply to `max`/`min` in production and in test mechanism, and for this formula they are already killed at `test_run_campaign.py:9645-9646`.

## Executed probes (all foreground, read-only, this session)

1. `git rev-parse HEAD` → `74a547cd9037f7c43fc7470bab81d133509ab3c0`. `cat 00-PACKET.md exhibit-A… exhibit-B… exhibit-D… | shasum -a 256` → `3b72345562c0d8f5…` (matches the convening digest). Read `00-PACKET.md` and exhibits A through F in full.
2. `git show 74a547cd:tests/test_controller.py | sed -n '655,705p'` → `RetryAdmissionPowermetricsAdapter._command` appends `--no-sleep` only when `count is not None` (`:673-681`). `sed -n '1605,1770p'` → policy test `:1610-1623`; regression `:1625-1767`; witness record `:1641-1652` (`timeout_s` from `self._capture_timeout_s(config, count)` at `:1651`); mirror `:1688-1689`; inequality `:1690-1693`; count/argv and post-count agreement `:1681-1687`, `:1694`; strict validation before `:1673` and after `:1767`. `sed -n '765,810p'` → `_produce_admission_powermetrics_bundle` builds its own config (20 Hz, idle 1.5 s) and does not return it, which is why the ruled change records `config` in the witness. `sed -n '105,135p'` → `make_config`.
3. `git show 74a547cd:joulewise/adapters/powermetrics.py` → `_capture_timeout_s` `:1468-1470` (`max(15.0, nominal_s * 1.5 + 10.0)`); `_run_bounded_capture` `:1190-1201` (argv at `:1200`, timeout at `:1201`, same `config`/`count`); `measure_post_run_idle` `:1021-1033` (`count = max(3, ceil(min(5.0, baseline.duration_s) / interval_s))`, so the count is host-derived and must not be pinned); `_interval_ms` `:1461-1462`. `grep -n` for `_capture_timeout_s|15.0|1.5 + 10` in that file → lines 59, 66, 1133 (unrelated 15.0 constants), 1201, 1256, 1468-1470 only.
4. `grep -n 'capture_timeout\|15\.0\|1\.5 + 10' tests/*.py` → the only production-formula tests are `tests/test_run_campaign.py:9636-9646` (`_capture_timeout_s(config, 100) == 17.5`; `_capture_timeout_s(config, 3) == 15.0`) and `tests/test_idle_admission.py:546-562` (`kwargs["timeout"] == 17.5` at the real `subprocess.run`). Every other hit is an unrelated 15.0 constant. In `tests/test_controller.py` the formula appears only at `:1651`, `:1688`, `:1689`.
5. Ran the regression once: `/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` → `Ran 1 test in 23.205s`, `OK`, rc 0. `git status --short` empty before and after.
6. Hand arithmetic only (no interpreter): 100 × 0.05 = 5 s → 17.5 s; 3 × 0.05 = 0.15 s → 10.225 s → floor 15.0 s; 94 × 0.05 = 4.7 s → 17.05 s deadline, 56.4 s stressed; 89 × 0.05 = 4.45 s → 16.675 s deadline, 53.4 s stressed.
7. NOT EXECUTED: any cut (in-memory or on disk); the conditioned 1.5 s regime; the floor-to-60 production counterfactual; `test_run_campaign.py:9636` and `test_idle_admission.py:546` themselves; the audit and consult drivers under `/private/tmp` (not read); the full controller suite; hosted CI.

No tracked file was edited; no git write was made; `/Users/edr/code/JouleWise` was touched only for its interpreter; the measurement clone and `/Users/edr/night-custody` were not touched.
