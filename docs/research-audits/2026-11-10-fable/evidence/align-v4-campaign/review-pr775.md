# Review of PR #775 (cadence-legs-v1), head 79031dcd8, gate-ledger row 1

VERDICT: ADMIT WITH FIXES (no blocker; two small fixes and one process note before it arms a real span)

## Findings
1. MEDIUM. verify_frozen_production (scripts/cadence_legs_runner.py) is untested and mutant (b) survived. grep finds no test that calls it. The only related test, test_frozen_paths_hash_at_the_frozen_commit, hashes the kit against git, not the runner's check. Skipping the per-path hash comparison (`if bad:` -> `if False:`) passes every test. This is the preflight guard for "the bytes that run are the frozen bytes". Fix: add a test that builds a temp repo or monkeypatches ROOT, then (i) flips one frozen file and expects SpanRefusal, (ii) uses a HEAD that differs from the kit and expects SpanRefusal.
2. MEDIUM (process). The runner refuses unless HEAD == kit.frozen.commit. The kits pin efbd0b020, but the PR head is 79031dcd8 (the re-pin commit changes only the two kits and BLOCK-QUEUE.json; `git diff --stat efbd0b020 HEAD` is 3 files). A merge or squash gives yet another SHA. A real span therefore only passes preflight from a checkout at exactly efbd0b020 with --kit supplied from outside that tree (the tree's kit copy there carries the older pin), or after a re-pin that chases itself. It fails closed, so it is safe, but the magistrate will hit it. Say in the runbook which commit the MBP checks out and where the kit comes from, or make the pin the merge base of the frozen paths. I verified that all 36 frozen-path hashes in both kits match the working tree at HEAD (bad = []).
3. LOW. Mutant (h2), work_remaining without WORK_RESERVE_S, survives. No test references WORK_RESERVE. The reserve is what keeps the close inside the launcher's grace. Add a test that a leg whose cap exceeds (deadline - reserve - now) is refused.
4. LOW. Real-runtime G0-timeout path is only exercised by a fake backend (test_unreleased_g0_is_a_recorded_leg_not_a_failure) and the mock. Logic reads right: leg_status g0_unreleased, rc 0, not admitted, span continues, wall 1200 s plus fixed work fits the 2700 s cap (about 2240 s). But the real run_member behavior on G0 timeout (exit code, custody completeness, which the runner's accepted_result requires) is not checked by me. Make the first pilot span the real test.
5. INFO. Plan inside the runner re-evaluates the blackout refusal at the actual start (t0 = run start, later than the launcher's arm-time plan by preflight + dwell). A borderline arm can pass the launcher and refuse in the runner. Fail-closed and before any measurement; no action needed beyond awareness.
6. INFO. The word "power" appears in non-desk files only as the key `ac_powermode` (runtime_result.json, leg_record.json, receipt steps). That is the host power-mode setting, not a power measurement. The desk bundle and desk output are clean.

## Time model and deadline math (checked by hand)
- Budget per leg = 500 + 19458*.005 (97.3) + 6 + 209 + 97.3 + 4096/12.03 (340.5) = 1250.1, ceil 1251. It is within kit leg_budget_s 1260 and matches the 1,251 s anchor. G0-timeout leg worst case about 2240 s is under leg_worst_case_s 2700.
- worst = 1950 + 1200 + (n + 2) * 2700. Pilot (3 legs) is 16,650 s. Full roster is 40,950 s. This is under the launcher ceiling (43,200 - 560). deadline = t0 + worst. Launcher deadline = plan deadline + 370 + 190 reserve. Work deadline = deadline - 370.
- Full roster at 13:20 local plans and runs. At 03:00 it is REFUSED (worst case meets 11:45-13:15 blackout). Both are designed behavior.
- Batch admission (leg_start_delay, interval_delay for the soak with the driver window added) reads correct, DST-safe (boundaries built from local calendar dates).
- Redo: contaminated attempt is renamed runtime.rejected<N>, quota is per span (2), and the last contaminated attempt is kept as not admitted. The blackout wait is re-evaluated per attempt. Plan reserves (n + quota) * cap.
- Close: restore_power runs only if read_power succeeded (same as the R1 smoke), feeds stopped in reverse order and hashed, signals ignored during close, receipt written with "x" (create-once). Restoring means Automatic powermode only; display sleep is not undone by the runner (as in the smoke; launcher owns it). A restore failure sets rc 2, giving INCOMPLETE/REFUSED.
- Leg-runtime swap (`rt.Segment = bound`) is restored in a finally in cadence_leg.main, and the process is a one-shot child, so double protection.

## Condition-13 check
- `git diff origin/align/2026-11-13-rl145-build...HEAD --stat` lists 23 files. None is among the ten R1_EXECUTED_SOURCES (align_r1_rehearsal.py, align_r1_runtime.py, r1_runtime.py, r1_runtime_contract.py, smc_enumeration.py, thermal_gates.py, r1_runtime.json, r1_phase_table.py, workload.py, align/apple/thermal.py). Name-grep of the diff for those plus v4_registration returned 0. The only touched existing file is scripts/launch_align_r0.py (not in the ten; it is in the kit's frozen list and the kit is hashed after the edit). I did not enumerate the 24 Block 6 files by name from a list (see "not checked"); none of the diff paths is under their obvious names, and test_rl145_gate_hashes passes.
- `git diff --quiet base HEAD -- thermal_gates.py thermal.py` (align/apple versions): identical. (A separate joulewise/hazards/thermal.py exists and is untouched.)

## Mock span, own scanner (/private/tmp/claude-501/scan.py, not the PR's)
Pilot roster L001-L003 at t0 13:20 and full roster (12 legs) at 13:20, run through `mock` on cl-dev-01. 27 and 72 files. Scanner walks every JSON/JSONL key and string value for energy, power, joule, watt, slot, transcript, condition, label and greps the text files. Hits: schema names only (".v1" strings), the step name `condition13` (a preflight check name, not a condition label), `ac_powermode` (item 6), and the desk table's boilerplate sentence. desk-bundle (5 and 14 files) and desk/ have zero denied keys or values. The meter stream holds only a mock header and trailer. No sample, energy, slot or transcript content in any output file.

## Mutants (worktree /Volumes/JW-EXT/jw-wt/rev-pr775-mut, removed afterwards; tests: test_legs_runner + test_kit)
| mutant | result | killed by |
|---|---|---|
| (a) leg summary carries an energy key | KILLED | 10 tests (assert on LEG_SUMMARY_KEYS), e.g. full-span, g0-timeout, redo |
| (b) preflight skips frozen-path hash check | SURVIVED | none (finding 1) |
| (c) leg starts inside blackout | KILLED | test_no_leg_starts_inside_a_blackout |
| (d) redo quota not enforced | KILLED | test_load_redo_keeps_the_rejected_attempt_and_quota_is_per_span |
| (e) condition-13 Segment swap outlives the call | KILLED | 3 LegRuntimeTests |
| (f) failed leg runtime does not stop span | KILLED | test_a_leg_runtime_failure_stops_the_span_and_still_closes |
| (g) plan worst case ignores redo quota | KILLED | 10 tests |
| (h1) admission ignores g0_released | KILLED | test_summary_is_the_desk_allowlist_and_admission |
| (h2) work_remaining ignores WORK_RESERVE_S | SURVIVED | none (finding 3) |
| (h3) close skips Automatic restore | KILLED | 3 tests |
| (h4) rejected attempt not kept | KILLED | redo test |
| (h5) plan skips blackout refusal | KILLED | plan blackout test |

## Test tails (taskpolicy -b python3.13 -B, PYTHONPATH=.:tests, in the PR worktree)
- tests.cadence.test_kit: Ran 18 in 1.163s, OK
- tests.cadence.test_queue: Ran 12 in 0.012s, OK
- tests.cadence.test_stops_desk: Ran 14 in 0.065s, OK
- tests.cadence.test_legs_runner: Ran 39 in 30.207s, OK
- tests.align.test_r1_smoke_launcher: Ran 58 in 30.960s, OK
- tests.align.test_rl145_part_c: Ran 22 in 0.569s, OK
- tests.align.test_rl145_gate_hashes: Ran 1 in 0.002s, OK
- tests.align.test_v4_registration: Ran 24 in 325.808s, OK (first run exceeded 120 s; reran to completion)

## Not checked
- Anything on the MBP; no real run, so the real leg runtime, real G0 timeout behavior, real feeds, real powermode restore and the launcher LaunchAgent path are unexercised by me.
- The explicit list of 24 Block 6 files (I had no such list file; I used the condition-13 ten, name greps, and the passing gate-hash test).
- That kit seeds/band recipe match the ruling text beyond what test_kit asserts; I did not re-derive the seed law.
- Full suite was not run (per limits). The temp mock output dir was deleted; the scanner is at /private/tmp/claude-501/scan.py.
