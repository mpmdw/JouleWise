# PR #309 — ledger row 9 discharged by WAIVER (cold gate 44 Q2 A1–A6 as applied by cold gate 56 W1–W8) — magistrate record, activation 2145630c, 2026-09-09 ~08:55 PDT

Head under waiver: `6d76f9647104d74b7b23cad945adaaf908eec0fd` exactly (W1; this record does not travel). Judge ruling: `56-coldgate-ruling-309-replay-door.md`; paired Opus refuter: `57-coldgate-opus-refuter-309-replay-door.md` (dissent recorded below if any). Contamination note: the cold judge disclosed that the harness injected the memory index and CLAUDE.md files into its session before it read the packet; it named the lines and ruled from the packet — recorded, not cured (the convening pattern needs a project-dir-independent launch; follow-up for the cold-gate pattern).

## Row 9 text (judge's wording, A4 tail filled)

**Row 9 — Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded: DISCHARGED BY WAIVER
(cold gate 44 Q2 A1–A6, as applied by cold gate 56 W1–W8), not by pass.**
Attempt 2, integration tree `6d76f964` (5db38b58 + main a3da3463), four shards concurrent, started 07:45:08 PDT 2026-09-09
(`54-replay-309-attempt2-6d76f964-tail.txt`): `WORKERS SUMMARY shards=4 modules=221 tests=5642 failures=5 errors=0 skipped=108
failed_shards=3,4 result=FAIL` / `rc=1`. Failures: (1–4) `test_run_campaign.IdleAdmissionCoreVerdictTests.
{test_cpu_admission_reads_final_attempt_telemetry, test_environment_refusal_does_not_hide_valid_retry_telemetry,
test_missing_final_attempt_telemetry_fails_closed, test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound}`, each at
`tests/test_run_campaign.py:9581` `AssertionError: False is not True` — the exact ruling-44 set; pre-existing on the merge base in the
same machine state (44 A3; 39b alone on 5d13d0e6: failures 4/4/3; wall-clock fixture timeout margin 3.5× vs measured slack 3.6–3.7× at
08:44; lane FIXTURE-TIMEOUT-WALLCLOCK-01; Low Power Mode attribution withdrawn, 42 addendum). (5)
`test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses`
at `tests/test_arm_readiness_lifecycle.py:891` (a consumer thread still alive after `join(timeout=30)` under four-shard concurrency;
the test's outcome assertions were not reached) — passes alone in-process on 6d76f964 4/4 (23.699, 23.499, 23.587 s magistrate;
24.408 s cold judge 56; machine census not recorded). Independence of (5) from this PR, shown structurally: the PR's only code hunk in
`joulewise/night_gate.py` is `@@ -1040,64 +1040,78 @@` inside `evaluate_night` (945–1338); `evaluate_night` is called only from
`night_gate.py` and `scripts/run_night.py`; the race test's path (`scripts/launch_window.py:121` → `arm_readiness._admit_pack_launch_go`)
reaches `night_gate` only via the function-local import of `NightPlan`/`PlanError` at `joulewise/arm_readiness.py:9933`, whose
definitions and every module-level statement are untouched by the diff. Attempt 1, integration tree `dd135364`, started 06:49:41 PDT
(`53-replay-309-attempt1-dd135364-tail.txt`): same summary line with `failures=5`, the four above plus
`test_docs_freshness.DocsFreshnessTests.test_current_sections_do_not_copy_volatile_literals`, caused by main commit 0d9881ef (README
blurb) and cured on main at a3da3463 (main CI green). Pathspec: `git diff --stat a3da3463..6d76f964 -- joulewise scripts tests` =
night_gate.py, run_night.py, test_night_gate.py, test_run_night.py only; grep for `night_gate|run_night` over the nine failing-path
files = none. No third four-shard replay was run (escalation rule); no serial replay required (56 Q2). A4 on 6d76f964:
`python3 -m unittest tests.test_night_gate tests.test_run_night` → `Ran 136 tests in 8.682s / OK`, rc 0 (58-a4-covering-tests-6d76f964.log). A5: CI at 6d76f964
run 34365694272, all build/test checks pass, gate-ledger red by design. Waiver is for PR #309 at head 6d76f964 only; no precedent
(44 C4); the general "extra failure passes alone 3/3 + registered lane" clause was REFUSED (56 Q2). Addendum obligations: see
[ADDENDUM-1..3 below, written now, filled later].

### What the later addendum(s) must record

- **ADDENDUM-1 (the four; inherited 44 C3/A6, retargeted).** Trigger: whichever comes first of (i) FIXTURE-TIMEOUT-WALLCLOCK-01 merged,
  (ii) the charge's timer probe reading ≤ 2.0× nominal (≤ 0.100 s per 50 ms sleep) on three consecutive samples, or (iii) Ed toggling
  Low Power Mode off and the probe being re-taken. Action: run `tests.test_run_campaign.IdleAdmissionCoreVerdictTests` (71 tests)
  alone in-process on then-current main; paste tail + rc + the probe readings before and after. If not green under condition (i) or
  (ii), the four are an open defect on main with their own lane; the merge stands; the record must say so.
- **ADDENDUM-2 (the race test).** On the NEXT full-suite four-shard replay on any integration tree (the next PR's row 9), record whether
  `test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses` passed under concurrency, with the shard count and the
  timer-probe reading at start. If it fails again under concurrency, ARM-INTEGRATION-LOAD-01 (P5) must be amended to name it and its
  30 s join explicitly, and no further waiver is available for it on any PR until that lane lands.
- **ADDENDUM-3 (row wording).** Ed's answer to the refuter's proposal (45, contract-lens) that row 9 be reworded to "rc=0, or a written
  waiver naming the failing set, its independence showing, and its discharge". Until answered, every non-green row 9 is a rule-11
  trigger, as it was here.

## Conditions W1–W8 status at record time

- W1 head 6d76f964: unchanged (no commit on the PR branch after the replay; PR traces 53–59 land on main, never on this branch).
- W2 waiver wording: above, verbatim into the PR body.
- W3 A4 on 6d76f964: Ran 136 tests in 8.682s / OK rc 0 (58-a4-covering-tests-6d76f964.log).
- W4 A5: CI at 6d76f964 — every build/test check SUCCESS, gate-ledger red until the ledger is filled (gh pr checks 309, 08:5x PDT).
- W5 race test alone 4/4 on 6d76f964 (23.699, 23.499, 23.587 s magistrate; 24.408 s judge); alone in-process; machine census not recorded.
- W6 no further four-shard replay; no serial replay.
- W7 addenda 1–3 written into the ledger at merge time (above).
- W8 second dated addendum to 31 citing ruling 56: in the same bookkeeping commit as this record.
