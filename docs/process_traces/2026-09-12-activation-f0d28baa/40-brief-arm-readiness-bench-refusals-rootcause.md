# Root-cause brief — seven arm-readiness tests REFUSE (`readiness_record_expired`) at the bench on pristine main code; CI green; does it touch tonight's armed night?

SESSION_MODE: delegated
WRITE_SCOPE: []

READ-ONLY root-cause seat in the linked worktree you were started in
(`bookkeeping/2026-09-12-activation-f0d28baa`; its `joulewise/`, `scripts/`,
`tests/` are byte-identical to origin/main `ace4cc3c`). You may run tests
(temp dirs allowed) and read-only probes; never edit tracked files; never
touch `/Users/edr/code/JouleWise`, `/Users/edr/JouleWise-measurement-20260913-derivation`
(an ARMED measurement night lives there — do not even `ls` inside it) or
`/Users/edr/night-custody`. Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python3`
(read-only use). No sudo, no powermetrics.

## Facts (bench-verified by the magistrate this hour)
- Integration replay `scripts/shard_tests.py --workers 4 --split` at 04:57–05:42 PDT: 7 failures, all arm-readiness, every one
  `'REFUSE' != 'PASS'` with `reason_codes: ['readiness_record_expired']` (one is `returncode 2 != 0` from the real arm generator):
  `tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.{test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change,test_dry_run_rehearsal_root_and_id_are_single_use,test_real_under_lease_rehearsal_uses_reservation_and_both_writer_slots}`,
  `tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.{test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses,test_boot_session_change_voids_verification_and_consumption}`,
  `tests.test_arm_readiness_lifecycle.PostSupersessionLayeringTests.test_historical_predecessor_resolves_and_still_anchors_the_chain`,
  `tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go`.
- All seven reproduce on pristine main code in THIS worktree (single-test runs, ~1.7 s each; 5 tests: `Ran 5 tests in 13.122s FAILED (failures=5)`).
- The same suite was CLEAN in yesterday's replay 25 (2026-09-11 ~11:00 PDT, main 97da620e) on this same machine, and CI on main ace4cc3c is green today.
- Machine: `kern.boottime` Wed Sep 2 20:35:16 2026 (≈9.4 days ago); `time.monotonic_ns()` ≈ 6.42e14 ns ≈ 7.43 days (macOS monotonic excludes sleep).
- Production constants seen: `joulewise/arm_readiness.py:6674 _T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS = 600_000_000_000`, `:8537 validity_ns: int = 300_000_000_000`, `:8746` min over `[evaluated_at_monotonic_ns + arm_horizon_ns, *evidence_expirations]`; the refusal branches at `:6285-6301` (prior boot session vs `valid_until_monotonic_ns < now`).
- Two Astra seats and a Claude session are alive on the host (agent load); the display is awake (desk day).

## Questions (answer each with executed evidence, file:line)
1. Which branch fires — "belongs to a prior boot session" or "evidence item expired" — and what are the actual `boot_session_id`/`valid_until_monotonic_ns`/now values in one failing case (instrument via a scratch copy under /tmp or by reading the dry-run receipt the test writes; never edit the tree)?
2. Why now and not yesterday: find the term that crossed a threshold (monotonic ≥ some constant? a fixture deadline computed from wall clock vs monotonic? a receipt written at test-fixture time with a validity that the loaded host exceeds? a boot-session id derived from something that changed at 03:46 today, e.g. the watchdog relaunch)? Prove it with numbers, and say whether the failures are load-dependent (run one failing test 3× and report).
3. THE QUESTION THAT MATTERS: does the same code path run in PRODUCTION at t0 tonight (02:56 PDT 09-13) for the armed night — the driver's arm-time readiness/consumption check reading receipts written at arm time (03:00 today) with `valid_until_monotonic_ns`? Trace the production call chain (`scripts/run_night.py` / `scripts/night_chains/...` / the arm-readiness consume path) and state, with the numbers, whether a receipt written ~03:00 today can read as expired at ~02:56 tomorrow on THIS machine, or whether the production path pins a different validity (arm_horizon) / re-authors at t0. If there is any risk, say exactly what evidence the magistrate should read from the night root (paths only; the magistrate will read them) — do not read the night root yourself.
4. Classification: bench-only fixture-class (which prior kernel row / failure family, if any: grep docs/process/state_kernel.json and docs/process_traces for `readiness_record_expired`) vs a production defect. Propose the kernel-row text if new.

Report (claude-codex-report/v1, genre root_cause): causal chain with numbers; Q3 answered first in the summary line; disproved alternatives; under 8000 bytes.
