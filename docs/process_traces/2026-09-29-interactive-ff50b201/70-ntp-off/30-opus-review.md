REVIEW: MERGE
Head 7b4deba0 (feat/2026-09-29-ntp-off-thin, base 32ff9013). Opus 5.5, executing, non-author. Worktree /Users/edr/code/JouleWise-wt-ntpthinrev-ff50b201 (clean). Probes in scratchpad/ntpthinrev/probe_*.py.
Safety: every run used a Python audit hook plus a PATH shim that refuses sudo, systemsetup, sntp and powermetrics (guard/). `pgrep -x powermetrics` returned nothing before, between and after runs. The only blocked calls were test_run_night NightProbeTests trying real `sudo -n /usr/bin/powermetrics` (the same at base; see N2).

Verdict basis: I found no path where a capture starts with network time ON or without an admitted, same-boot OFF receipt at least 600 s old. Every defect below fails closed: it refuses or blocks, and none can make a number false.

1. Capture admission, driven with bad receipts (probe_admission.py, probe_derivation.py, probe_arm.py, probe_e2e_sampler.py; all 35 cases gave the expected result):
 - Module (network_time_off.py:37-105): each of these is refused: stdout `off`, no newline, or `On`; exit 1, False or None; ON argv; another boot; a null boot; 599 s on either clock alone; NaN or inf; wall clock stepped back. A settled receipt is admitted.
 - Derivation night (run_night.py:2986-2997, called at :3208, before the pack GO and before the chain is claimed): a wrong-stdout OFF, exit 1, 599 s, or an existing receipt (FileExistsError) is refused. The receipt is saved in every case.
 - Pack night (:2988-2991): a missing receipt, one 300 s old, another boot, wrong stdout, or a symlink is refused.
 - Evidence night: campaign execute runs OFF, then sleeps settle_s (600 in v1-v3), then re-admits (quiet_predicate_campaign.py:1488-1496). The sampler admits again at its start stamp, before powermetrics (sample_quiet_predicate_evidence.py:1087-1108). It refuses 599 s, another boot, wrong stdout, another plan, and a legacy control record.
 - Claim arm: at ledger-readiness and ledger-reservation (capture_t0_step.py:804-808), a 300 s receipt is refused before the command runs and a 700 s receipt is admitted. The T-0 author (arm_readiness_evidence_t0.py:1231-1245) requires a settled, plan- and window-bound receipt that matches the clock-disable capture.
2. ON after a capture: `git grep -i usingnetworktime` over code finds exactly one ON call site, capture_t0_step.py:757, inside _arm_reference. Nothing else in code turns network time ON:
 - quiet_window_clock.sh `enable` is deleted.
 - campaign restore_network_time is deleted.
 - The bench stub only prints.
 - The sudoers fragment still grants `on`, which the arm resync needs.
 - The runbook (window_runbook.md:598-632) keeps manual ON as a desk action between windows only, followed by a fresh OFF and a 600 s dwell.
3. Arm resync: all six cases passed.
 - Reference never valid: toggles are [on, off], a receipt is written, and the step refuses.
 - ON fails: toggles are [on, off], a receipt is written, and the step refuses.
 - A file in any one of RUNS, BOUND_RUNS, CUSTODY or QUARANTINE: the step refuses with zero toggles.
 - An existing receipt or clock-reference.json: the step refuses with no command.
 - The OFF sits in `finally` (:762), before the dwell that the ledger steps check.
 - SIGKILL between ON and OFF leaves ON with no receipt, so the pack, author and ledger steps all refuse. Derivation and evidence nights set their own OFF.
4. Tests: the 21 deleted IDs match exactly the withdrawn restore and H6 machinery. The two refusal-shaped deletions are covered again by test_network_time_off, PermanentOffExecutorTests.test_missing_off_receipt_prevents_recorder_and_capture, and the campaign refusal block around test_quiet_predicate_campaign.py:2023-2035. Kept-test diffs re-shape fixtures and do not weaken anything that bears on a number. One liveness pin was relaxed (N1).
5. I ran all nine modules whole under the guard, as one command: `python3 -B -m unittest tests.test_network_time_off … tests.test_t0_rehearsal`.
 - Head: 707 tests, 6 failures and 1 error.
 - Base 32ff9013, same guard, 8 modules: 721 tests, 23 failures and 5 errors.
 - Every head failure also fails at base under the same guard, so none is new. Causes:
   - the guard blocked `sudo powermetrics` and a fake `/bin/sleep /usr/bin/powermetrics` process;
   - `sys.executable` is /opt/homebrew/opt/python@3.14/bin/python3.14 while the record says /opt/homebrew/bin/python3.
 - The failing tests: test_run_night ×6 (probe receipt, supervised probe, worker receipt, preflight, installer, calibration worker) and test_g4_real_ruled_census_pgrep_dialect.
6. Paths to a false number: none found. pilot_summary exempts an envelope from H6 only when the sampler wrote policy = network_time_off.v1 after admission (quiet_predicate_campaign.py:1165-1168). Legacy envelopes keep their H6 replay. An envelope with no policy stays excluded as unattested.

Findings (none holds the merge):
F1 HIGH, must land before the next evidence night: the evidence sampler refuses every real envelope because of letter case.
 - The receipt stores the boot ID lowercased (network_time_off.py:28 `.lower()`).
 - The sampler compares it with the raw sysctl value from metadata (sample_quiet_predicate_evidence.py:1047,1057 → :1089). On this Mac that value is uppercase: CD5B815A-….
 - End to end, a settled, same-boot, correct receipt gives error_class=network_time_provenance, provenance=None and zero rounds. Command: probe_e2e_sampler.py.
 - Nothing is captured, but evidence nights would yield 0 envelopes.
 - Tests hide it because both sides are faked as "fixture" (test_sample_quiet_predicate_evidence.py:895-898).
 - Fix: lowercase the sampler's boot ID, or compare case-insensitively in seconds_since_receipt. Add a test that uses a real uppercase sysctl string.
F2 MEDIUM, known and deferred: `clock.restore_recipe.v1` is the only restore doctrine still required.
 - Where it is required: registry configs/arm_readiness/d117_row_registry_v2.json:385,545,586,627,687, with its content predicate at arm_readiness.py:971-975,1147.
 - How it is derived: arm_readiness_evidence.py:833-863 requires the §5A phrases "whole-window verdict, and the backup, re-enable it" and "The restore comes last". The runbook at head no longer contains them (0 hits at head, 2 at base).
 - What it blocks today: the DOCTRINE_PIN derivation cannot be derived, so freeze/ARM evidence cannot be authored for any d117 claim window, and pack nights cannot follow. Derivation and evidence nights are not affected.
 - Tests pass only because they splice in tests/fixtures/historical_clock_restore_5a.md.
 - The other hits are sealed historical doctrine-pin and freeze receipts, plus v1. v1 is not the active registry, and those hits are not requirements.
F3 LOW: the bench replay is broken. scripts/bench_replay_start_drift.py:814-825,857,864 still uses campaign.SUDO, campaign.SYSTEMSETUP, attestation_timeout_s and network_time_restored, so it raises AttributeError before running anything. When migrating it, inject the OFF runner; never let it reach the real OFF_ARGV.
F4 LOW: the pack admission does not bind the receipt to the pack's plan or window. run_night.py:2988-2997 reads the receipt, then re-reads it with its own IDs, which proves nothing. The path is per pack_id, so the risk is small.
F5 LOW: the sampler binds plan and window only through NIGHT_PLAN_ID (sample_quiet_predicate_evidence.py:282-283). If that variable is unset, the binding is silently skipped.
F6 LOW: the derivation branch's 600 s sleep (run_night.py:2994) comes after GO and counts against window_max_s and the shutdown deadline. This affects liveness only; check the budgets.
N1 NIT: test_arm_readiness_evidence_t0 changes the liveness-budget pin from assertEqual to assertGreaterEqual. It no longer detects budget drift.
N2 NOTE, not from this change: test_run_night NightProbeTests launch real `sudo -n /usr/bin/powermetrics` when no guard is present.
