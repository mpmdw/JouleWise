# Magistrate terminal review — PR #308 (rehearsal-20260909 arm + harvest record, T38d checkpoint), merge candidate = the custody commit that carries this file (sha named in the ledger rows 11/12)

Reviewer: headless magistrate, activation 2145630c (Fable), full session context, not delegated. Read in the linked worktree
`/Users/edr/code/JouleWise-wt-magistrate-1ef89702` (branch `bookkeeping/2026-09-09-rehearsal-arm-record`).

## What the PR is

Docs plus one checkpoint: (1) arm record 21h and harvest record 21i for rehearsal-20260909 with the byte-copied night artifacts under
`21b-rehearsal-20260909-bench/`; (2) the 2026-09-09 sections of the durable pointer (activations 784a764e, 8844a3d0, b1e2fd2f,
628c2eed, 2145630c); (3) NIGHT_HANDBACK §Executed reconciliation; (4) the T38d checkpoint (RUN_STATE, kernel fold registering
NIGHT-GATE-STUB-CHAIN-01, satisfying the POST-WATCHDOG-REHEARSAL-20260909 event and re-blocking NIGHT-REHEARSAL-01 on the cure
merge, one EXPECTED_IDS line in tests/test_gen_state.py); (5) the 2026-09-09-rehearsal-harvest process traces. No code path changes.

## Design-level questions (row 7)

1. **Does the record say only what the artifacts show?** After five fix rounds, yes. Rounds 1–4 removed over-statements (ordering,
   digest scope, pid attribution, process type); round 5 removed the last cross-document value drift (cure sha) and the one
   prospective clause. Verification chain: fidelity refuter 05, Opus contract 06, deltas 12/15/21/29/36, Opus final-head 30
   (23/24 claims re-derived match; the 24th was S-A, cured), consult 33 (exhaustive repeated-fact table, ~90 facts, one mismatch,
   cured), fact guard 34b PASS (11 scopes, 0 mismatches) at 5d13d0e6.
2. **Does it rule anything?** No. The handback clause that read as assigning the next plan's author was replaced with a RECORD
   sentence; the between-nights template question, D-175 condition 8 scope, the second stub night, the plan-aware launch fence and
   the stub class's absent chain-identity check are all referred to the cold gate or Ed, not decided.
3. **Is the kernel state truthful?** Event satisfied with evidence = 21i; NIGHT-REHEARSAL-01 BLOCKED on a pending hard start
   dependency on NIGHT-GATE-STUB-CHAIN-01 (cure merged before any further stub or real night); the second-stub-night question is
   `needs_ruling` in the status note; CLONE-READINESS-01 carries the cure-merge prerequisite as a note. gen_state --check rc 0.
4. **Does anything here arm, move, or delete?** No. It records that 628c2eed uninstalled both night agents and removed the stub
   checkout and plan root under the documented post-completion uninstall; nothing is armed; the frozen list is the canonical repo.
5. **Escalation discipline.** The standing trigger fired (same drift class in rounds 3 and 5) and was honoured with a consult (33)
   before the fix, not a third whack-a-mole round; the consult's mechanical guard now stands as the PR's own verification.

## Overbuild / merge-ability prune (row 8)

Nothing to prune. The guard scripts (34, 34b) are one-off verification artifacts kept as traces, not tooling; no process rule is
introduced. The kernel-fold branch is folded here so the harvest record and the kernel state that cites it land together.

## Replay (row 9)

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4` in this worktree at 5d13d0e6 (contains origin/main 83ab38ed, so it is the integration tree), started 04:36 PDT with no seat, reviewer agent or other test process launched by this session (four shards ran concurrently; the rest of the machine's state was not recorded). Verbatim summary lines (38-replay-308-5d13d0e6-tail.txt):

```
SHARD SUMMARY index=1/4 modules=34 tests=542 failures=0 errors=0 skipped=30 result=PASS
SHARD SUMMARY index=2/4 modules=54 tests=1201 failures=0 errors=0 skipped=53 result=PASS
SHARD SUMMARY index=3/4 modules=66 tests=1985 failures=0 errors=0 skipped=9 result=PASS
SHARD SUMMARY index=4/4 modules=67 tests=1908 failures=4 errors=0 skipped=16 result=FAIL
WORKERS SUMMARY shards=4 modules=221 tests=5636 failures=4 errors=0 skipped=108 failed_shards=4 result=FAIL
rc=1
```

The four failures, all `tests.test_run_campaign.IdleAdmissionCoreVerdictTests` at `tests/test_run_campaign.py:9581` (`AssertionError: False is not True`): test_cpu_admission_reads_final_attempt_telemetry, test_environment_refusal_does_not_hide_valid_retry_telemetry, test_missing_final_attempt_telemetry_fails_closed, test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound. `failed_shards=4` is the list of failing shard indices (shard 4 only; shards 1–3 PASS).

Pre-existing on merge base 83ab38ed in the same machine state (see 42-bench-rootcause-low-power-mode.md with its addendum, 44-coldgate-ruling-replay-verdict.md and 45-coldgate-opus-refuter-replay-verdict.md): the class alone in-process fails identically on 5d13d0e6 and on main+#309 5db38b58 (39-*.log), one of the four reproduced on main itself by the judge; CI passes every test shard at 5d13d0e6 on Linux 3.11/3.14. Independence: `git diff --stat 83ab38ed..5d13d0e6 -- joulewise scripts tests` = tests/test_gen_state.py only (two lines: the ID and the count). Cause: flaky wall-clock coupling of a sleeping fixture against a 17.5 s timeout with a 3.5× margin (the Low Power Mode attribution was refuted by the refuter and withdrawn). Three post-refutation class re-runs stayed red (4/4/3 failures, 39b-*.log), so the refuter's green-before-merge condition was not met; disposition per cold gate 44 Q1 (a) with C1–C5, refuter dissent recorded. Addendum obligation (C3, synthesized): re-run the class on then-current main after the fixture cure (FIXTURE-TIMEOUT-WALLCLOCK-01) merges or the slack state changes, and record the tail as a dated addendum to this row. No precedent (C4).

## Post-review commits (row 10)

After the reviewed content head 5d13d0e6 (delta 36 clean; fact guard 34b PASS), one custody commit carries: the 2026-09-09 harvest traces 23b–47 (reviews, consult, cold gate 44/45, root-cause seat, bench records, retry logs), this file, the two kernel lanes ruled by cold gate 44 (seat 47 + bench rewording per the refuter; gen_state --check rc 0; test_gen_state + test_docs_freshness 75 tests rc 0), the A6 addendum to 31, the 42 addendum, and this activation's durable-pointer section. The fact guard 34b is re-run at that head with the durable scope sliced before the new section; its tail is recorded in the ledger summary. Rows 11/12 name that custody commit.

## Verdict

CLEAN for merge at the custody commit once CI is green there (the `gate-ledger` check turns green when this ledger is in the PR body).
