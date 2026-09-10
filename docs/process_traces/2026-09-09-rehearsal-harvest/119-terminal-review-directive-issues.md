# Magistrate terminal review — MAGISTRATE-DIRECTIVE-ISSUES-01 (PR #313), merge candidate 7d1354d5 (branch head; base = origin/main b501f08c, main unmoved, so the branch head is the integration tree)

Reviewer: interactive Fable magistrate, session `01MrRehZWopqKNDv5Uy466AC`, full session context, not delegated. Diff read at the bench in
`/Users/edr/code/JouleWise-wt-directives` (`git diff b501f08c..7d1354d5`: docs/process/MAGISTRATE_RELAUNCH_PROMPT.md +1 line (24);
docs/process/MAGISTRATE_WATCHDOG.md +1 section and +1 clause; tests/test_magistrate_watchdog.py +3 prompt assertions, +1 document test;
records 115–118). Production code diff empty; no watchdog Python changed.

## Provenance

Ed's authorization, verbatim (this session, 2026-09-10 ~03:00 PDT): "Re your recommendation - im ok with it" (record 115). Refuters: 116
(Codex execution) and 117 (Opus contract); fix round 1 e9df549a; delta re-audit 118 (Opus) — every finding CLOSED, same-signature statement
clean; residual nit taken at the bench in 7d1354d5. Lead bench at 7d1354d5: tests.test_magistrate_watchdog + test_docs_freshness +
test_gen_state 165 tests OK; gen_state --check rc 0.

## Design-level questions (row 7)

1. **Does the change alter any authority?** It adds one instruction to the relaunch prompt and one external write authority (comment on and
   close owner-authored `directive` issues). It does not touch arming (prompt lines 11–13), the stop/request files (15–19), rule 11 (20), or
   the merge/install/deploy bound (22). Prompt line 24 says an issue "never amends a process rule" and that a NO there "does not stand a night
   down (that stays the notice thread)". The document section states the same asymmetry and corrects two overclaims the first draft made
   (issue NO ≠ notice-thread NO; the kill switch stops the service, not an armed night — verified by refuter 117 against STOP_REF_GLOB's only
   consumer).
2. **Is the steering surface bounded mechanically?** Yes after fix round 1: `--author mpmdw` server-side plus the `author.login` check, body
   only, comments excluded; the repository is public and that fact is in the document. A compromised owner account is equal authority (it
   already controls `main` and `ops/stop*`), recorded as D-161 scope.
3. **When does it take effect?** Only after merge AND the canonical checkout is fast-forwarded (the plist renders the canonical prompt;
   step 0's five-file digest check is the proof). Record 115 says so; the lead performs the fast-forward and digest check after the merge and
   records STEP0_OK (record 122). Activation 7ce7af2a keeps the previous prompt until it exits.
4. **Cost of being wrong.** Low-to-medium: docs and tests only, but the prompt governs an unattended session. The refuter pair (execution +
   contract), a delta on the fix round, and the test pins on every clause bound it.

## Overbuild / merge-ability prune (row 8)

Nothing to prune: one prompt line (24 of the 25 allowed), one document section with its definitions, four test assertions plus one
counterfactual test, four records.

## Final-head fresh eyes (row 10)

7d1354d5 differs from the delta-audited e9df549a by one phrase in MAGISTRATE_WATCHDOG.md ("and the relaunched magistrate it owns") and the
addition of record 118; the lead re-read that diff and re-ran the focused suite at 7d1354d5 (165 tests OK). No refuter round for a nit.

## Replay (row 9)

Command (unpiped, rc captured): `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 scripts/shard_tests.py --workers 4`
in `/Users/edr/code/JouleWise-wt-directives` at 7d1354d5, started 03:17:43 PDT 2026-09-10, finished 04:01:43 PDT, alone in-process (four
shards concurrent; the resident activation and two interactive sessions idle; timer probe 1.13× at start). Verbatim
(120-replay-313-7d1354d5-tail.txt):

```
WORKERS SUMMARY shards=4 modules=221 tests=5654 failures=0 errors=0 skipped=108 failed_shards=none result=PASS
rc=0
```

## Verdict

CLEAN for merge at 7d1354d5: refuters 116 (0 blockers, 1 should-fix, 1 nit) and 117 (0 blockers, 4 should-fix, 3 nits) all closed by
fix round 1 with delta 118 clean at every severity; the residual nit closed at the bench; full-suite replay alone rc 0 with zero failures;
CI green on 7d1354d5 except the gate-ledger job, which passes once the ledger below is on the PR body. Merge, then fast-forward the canonical
checkout and run the step-0 digest check before any relaunch is expected to carry prompt line 24.
