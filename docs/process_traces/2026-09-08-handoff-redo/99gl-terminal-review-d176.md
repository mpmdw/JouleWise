# Magistrate terminal review — D-176 pack-night GO receipt, PR #307 (interactive Fable magistrate, 2026-09-08 evening PDT)

Merge candidate: branch `int/2026-09-08-d176-seats-2-3` at **58d9225b** (7d1cffb0 = seats 2–4 + census cure + replay-fix round + main merged, plus one final-head commit: contract §9 repin, S2 test name, N1 comment, and the two lifecycle-test cures). Trace-only commits after this review (replay record, this file) are content-free for the code.

## What I verified myself (rule 1; every run rc-gated, unpiped)

| Check | Head | Result |
| --- | --- | --- |
| Nine-module bench of the replay-fix round (`tests.test_magistrate_watchdog_cli tests.test_powermetrics_fiducial tests.test_run_campaign tests.test_arm_readiness tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_run_night tests.test_docs_freshness`) | bda71e60 + seat edits | 670 tests, OK, rc 0 (scratchpad `bench-d176-fix.log`) |
| `tests.test_docs_freshness tests.test_gen_state` on the repinned contract | 7d1cffb0 + repin | 75 tests, OK, rc 0 |
| Independent pin check: every `path:line` (`symbol`) pin in the contract lands on a `def`/`class`/assignment of that symbol | 7d1cffb0 + repin | 177 symbol pins, 0 stale, 0 missing files |
| `tests.test_arm_readiness_lifecycle` under `HOME=$(mktemp -d)` (no global git identity, as on CI) | 58d9225b | 69 tests, OK (1 skip), rc 0 |
| Full-suite replay ALONE | 7d1cffb0 | 1 failure: `test_arm_readiness_integration…(profile='BETA')` refused `readiness_clock_preflight_refused` during shard start-up while an Opus reviewer and an Astra seat were launching (load signature; see below); all other modules PASS |
| Full-suite replay ALONE, nothing else on the machine | 58d9225b | recorded in the replay record 99gm (row 9) |
| CI | 58d9225b | every job green except `gate-ledger`, which fails only on the NOT-RUN rows this review closes |

Diffs I read in full: the replay-fix seat's six-file diff (fixtures + §10.3), the repin seat's diff shape (pin numbers only + S2 + N1, confirmed by my checker and by `git diff --stat`), the lifecycle test cure (my own edit), and the merge of main (test_run_campaign both-sides check, corroborated by Opus 99gi).

## Findings adjudicated at this head

- **Replay regressions (99gc, 12 tests):** cured by Astra seat 99gf under rulings A–D; Opus delta 99gg found no blocker and confirmed item C was mock interference (a third branch the ruling had not listed; the seat reported it rather than forcing a ruled branch). Two Opus nits (addendum shape, missing citation) applied at the bench.
- **Final-head review (Opus 99gi):** no blocker; S1 55 stale §9 pins and S2 a nonexistent test name — both cured by the Astra repin seat 99gj (178 occurrences, 13 frozen historical pins left as records, 0 unresolved) and re-verified by me; N1 comment added; N2 (tracked `/Users/edr` inventory paths) is by design of the frozen census.
- **CI regressions the bench missed:** `test_dry_run_is_rejected_by_launcher` predated seat 4's ruled ordering (usage refusal before any receipt IO) and only passed earlier by refusal order; re-arranged behind a real GO it draws the identical `launch_consumption_invalid` "arm receipt is invalid" refusal, so the intent is preserved. `test_consume_collision_never_emits_defensive_lock_unavailable` committed without a git identity (CI runners have none). Lesson recorded: derive the bench set from the changed modules' test dependents, and run git-fixture modules once under an empty HOME.
- **Calibration-exits CI flake:** `test_forced_auto_maintenance_mutation_reproduces_cleanup_race` failed once on 3.14 at 7d1cffb0, passed locally in the same replay and on the 58d9225b CI run; not attributable to this branch (module untouched); watch, not fix.

## Standing escalation trigger — ARM-INTEGRATION-LOAD-01 (fourth occurrence)

The ARM integration/relocation tests have now refused under machine load four times today (locator attempt 2, liveness-docs attempt 2, replay-b here with reason `readiness_clock_preflight_refused`, plus the earlier NO_GO census signature). Same signature, structural cause (production readiness gates are load-sensitive by design; the suite runs them under a 4-worker shard burst). Per rule 11 the next spend is a CONSULT, not another rerun-until-green: queued as a consult on whether the integration tests should pin the preflight inputs (deterministic clock/census doubles at the integration seam) or the shard runner should serialize the ARM-gated modules. Not blocking this merge: row 9 is satisfied by a replay with nothing else running, which is the documented condition.

## What this merge does NOT claim

No night is armed by this work. No pack-bound night may run until CLONE-READINESS-01 cuts an un-inventoried rehearsal clone at an inventory-bearing head (second cold gate 99ey, plan 99co + amendment). Rehearsal-20260909 (stub, no pack) stays the headless magistrate's to arm after the interactive stand-down and Ed's no-NO. G2-a first-window magistrate inputs (PLAN_ID, NIGHT_ROOT, T0, WINDOW_MAX_S) are ruled only after rehearsal acceptance.

## Verdict

APPROVED to merge on the condition that the replay record 99gm shows PASS with rc 0 at 58d9225b and CI stays green on the final head; both are checked by the magistrate before the merge command is issued from the canonical checkout.
