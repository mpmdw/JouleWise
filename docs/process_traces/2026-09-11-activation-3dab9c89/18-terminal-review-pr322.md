# 18 — Magistrate terminal review of PR #322 (NIGHT-C1-REGISTRATION-DOCS-01) at the exact merge candidate 2c25eccbe102a57ad40c3f91c38d977465462788 — 2026-09-11 09:0x PDT, activation 3dab9c89

**What the candidate is.** Seat landing 503a271e (Astra, brief 15 of activation 58a3bcfc, spec = cold-gate ruling 12 §5, decision (i) in synthesis 14), then five lead commits from dictated cures: 1f8c1174 (refuter 01 F1: gloss "receipt class"), dc93749c (Opus 07 B1: `${H}` braces in the two new git revision:path commands, with a runbook-wide regression; S1/S2 rewordings), 7fc058b9 (delta 09: the S1 description re-derived from the registration's own fields), 66963ace + d8cf309a + 53310262 (consult 15 after the escalation trigger: the §0.5 paragraph states only the replicable C1 check; one T3-tripping line reworded; one line wrapped), and the conflict-free merge of main baf7b900 (PR #320) as 2c25eccb. Five files; the unit diff over main is byte-identical to 53310262's over 1dddcfea (verified by sorted +/- lines).

**What I read myself (rule 1).** The generator's two-line change (import `D166_REGISTRATION_PATH`; the example plan's `registration_path` uses it) and its regenerated runsheet line; all four seam tests plus the `$H:` regression in `tests/test_night_gate.py` and the T1 change in `tests/test_gen_derivation_night.py` (above, in full); every runbook sentence I wrote or pasted (rounds 1–4c) and the §0.5/§1.1/§1.4/arm-block/§2.5/§5 lines the refuters cited. What I ran: the two test modules at every round (97 → 98 OK), `gen_derivation_night.py --check` PASS at every round, the zsh `$H:` reproduction at the bench (`1f8c1174abconfigs/x`), the T3 counterfactual (offenders at 1f8c1174 = lines 1428 and 1755).

**Design questions answered (row 7).** (1) *Why bind the plan to the D-166 file rather than the pre-registration (Astra's (ii))?* Row C1 for `DIAGNOSTIC_NO_PACK`/`REHEARSAL_STUB` hashes one file against one compiled constant; changing that is gate code, moves the measurement head after the 09-09 rehearsal exercised it, and converts a desk-time stop into an unattended t0 refusal (ruling 12; synthesis 14). The pre-registration is already fixed by H, the commit the plan pins and the chain verifies (Opus 07 §B: a committed change refuses `night_plan_stale`; an uncommitted edit is not detected but is also never read by the night). (2) *Is C1 then "a ceremony" (Astra's dissent)?* For this class the night has no consumer of the pre-registration's bytes; C1 authenticates the file it is coded to authenticate, and the runbook now says exactly that instead of dressing it as science. The PASS-route guard is the §2.5 desk re-hash; the FAIL route has `prepare-candidate`'s mechanical refusal. Registered as follow-up thinking, not a blocker: a mechanised desk re-hash. (3) *Why was the §0.5 paragraph so expensive (four rounds)?* Because it tried to explain another campaign's rule; the consult ruled the science out of the paragraph — the correct application of the writing standard's "delete" option, and the escalation trigger worked as designed (round three did not happen unconsulted).

**Overbuild / merge-ability prune (row 8).** Not taken: Opus 07 N1–N4 (changelog forward references; arm-assert vs gate hashing pipelines; the launchd WorkingDirectory assumption; the night plan's own digest in the arm record) — each is a defensible improvement to a runbook that will be revised again for the equivalence night; none changes tonight's or the equivalence night's behaviour. Nothing in the unit is speculative.

**Gate ledger evidence.** Row 1: refuter 01 (Astra xhigh, contract + execution + pedagogy; contract table all PASS). Row 2/6: Opus counter-review 07 (contract + physics-of-the-gate; executed the gate on both classes). Rows 3–5: lead notes 05, the dictated cures applied at the bench, deltas 09 (round 2), 12 (round 3), 16 (round 4/4b/4c); same-signature statements: S3 survived rounds 2→3 → consult 15 (record), cured in round 4 (delta 16 line one). Row 10: delta 16's fresh read of the final paragraph and Opus 07 at 1f8c1174. Row 11: CI at 2c25eccb. Row 9: full-suite replay at 2c25eccb, tail appended below.

**VERDICT: MERGE on replay PASS at 2c25eccb and CI green at 2c25eccb**, under D-072. Post-merge: cross-unit review of main; then record 13 of 58a3bcfc's `registration_path` placeholder is filled with `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` (this ruling's (i)) for tonight's stub — the first live C1 pass.

## Replay tail (row 9) — appended when the run lands

Replay 23 at 2c25eccb (the integration tree: 53310262 + merge of main baf7b900), worktree `JouleWise-wt-c1-seam`, `python3 scripts/shard_tests.py --workers 4 --split`, detached pid 93705, started 09:0x PDT 2026-09-11 (activation b23f3cb7), finished 10:20 PDT (harvested by activation 36d3a823 from `/tmp/magistrate-b23f3cb7/replay-23-pr322-2c25eccb.log`, 1,196,410 bytes). Exact tail:

```
SHARD SUMMARY index=1/4 modules=52 tests=1390 failures=0 errors=0 skipped=50 result=PASS
SHARD SUMMARY index=2/4 modules=59 tests=1202 failures=0 errors=0 skipped=7 result=PASS
SHARD SUMMARY index=3/4 modules=59 tests=1923 failures=0 errors=0 skipped=47 result=PASS
SHARD SUMMARY index=4/4 modules=62 tests=1506 failures=0 errors=0 skipped=5 result=PASS
WORKERS SUMMARY shards=4 modules=232 tests=6021 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
REPLAY_RC=0
```

PASS: 6021 tests, 0 failures, 0 errors, 109 skipped, failed_shards=none.
