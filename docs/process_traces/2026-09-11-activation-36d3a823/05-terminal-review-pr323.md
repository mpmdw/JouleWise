# 05 — Magistrate terminal review of PR #323 (H′: NIGHT_HANDBACK rewrite for rehearsal-20260912) at the exact merge candidate 97da620e — 2026-09-11 10:5x PDT, activation 36d3a823

**What the candidate is.** One docs-only commit 944963b9 (activation 39e3f9e1: the three replacement sections of 58a3bcfc record 13 §Step 0b applied by `/tmp/magistrate-3dab9c89/handback_rewrite.py`, heading kept as the bare `## Next lane`, one reflow of the interpreter paragraph, the driver-interpreter pin dated) plus the merge of main 18ab2cc4 (PRs #321 and #322) as 97da620e. One file, `docs/process/NIGHT_HANDBACK.md`, +97/−32. The unit diff over main is byte-identical (sorted +/− lines) to 944963b9's over its parent — verified by me at 10:33 and independently by Opus (record 04 §1), who also showed why: PR #321's file state was already the rewrite's parent, so the main merge contributed zero bytes to this file.

**Why a PR and not a direct commit.** D-170's decision entry (decision log ~10880) says docs-only pull requests fill all twelve rows or use the direct-commit practice; H′ is the head an unattended night pins as `repo_head = measurement_head`, so it takes the full ledger, as PR #319 (docs-only, Ed's ruling) did.

**What I read myself (rule 1).** The full 129-line diff at 97da620e (10:33). The three rewritten sections against record 13 §Step 0b as quoted in that record (§Purpose, §Where the results are, §Next lane). The pins: recomputed at the bench with `zoneinfo` (t0 1789198200 = 00:30 PDT; close 1789199100; courier 1789199400 = 00:50; stand-down 1789196700 = 00:05; TERM 1789197240; KILL 1789197300; dead-man 1789221600 = 07:00 09-12) — every number in the sections matches. The uninstall command in §Next lane against the installer on main (`--hour 0 --minute 30 --uninstall`, no `--python`; addendum 11 of 3dab9c89). The interpreter paragraph's dating parenthetical against PR #321's actual change (absolute argv[0]; `/usr/bin/env python3` before it).

**Design questions answered (row 7).** (1) *Is the rewrite still the right text after #322 merged?* Yes: #322 did not touch this file (Opus §2, `git diff 4c06b3b4 18ab2cc4 -- docs/process/NIGHT_HANDBACK.md` empty) and the `registration_path` the plan will carry is the D-166 literal the rewrite does not need to name (record 13 §0c reads the compiled constant). (2) *Opus NIT-1 — the four links into `docs/process_traces/2026-09-11-activation-58a3bcfc/` do not resolve on main; should the bookkeeping chain land on main before H′?* Decided NO, with the reason: the night reads no documentation (driver, gate, installer and plan only); the links are inherited (main already carries five such dangling refs; H′ carries four); landing five activations' bookkeeping under H′ would force another CI and replay round on a new head for no night-relevant change, and the bookkeeping chain lands on main immediately after H′ anyway. Recorded here so a reader of the stub checkout knows where the ruling and records live (the bookkeeping branches, then main). (3) *Daytime install?* Ruling 06 C-5 bounds the install to "on 2026-09-11 local, at a wall-clock time after 07:00 PDT and after the chosen hour:minute has passed"; the handback's word "evening" is descriptive. Today's activations have been exhausting usage in 10–25 minutes each; arming as soon as H′ exists is the choice that maximises the chance the arm happens at all. The notice says so in one sentence.

**Overbuild / merge-ability prune (row 8).** Nothing to prune: the commit is the prescribed text. Opus NIT-2 (unguarded "nothing is armed" in the dated 09-11 history entry), NIT-3 (the C1 clause of the "since PR #309" sentence is supported by the post-#309 scope, not by the colon clause), NIT-4 (one 122-column line) and NIT-5 (a pre-existing duplicated sentence) are DECLINED for H′ — verbatim-prescribed or pre-existing — and NIT-2/NIT-3 are folded into lane NIGHT-HANDBACK-GLOSS-01 with 39e3f9e1 record 02's F1–F3. No fix round was run; there is no delta to re-audit; the unit diff has not changed since the first review.

**Gate ledger evidence.** Row 1: 39e3f9e1 record 02 (Astra, contract lens, verbatim/pins/nothing-else-changed/first-use test) — MERGEABLE. Row 2/6/10: record 04 (Opus, contract + execution lens, at the FINAL head 97da620e: verbatim diffs, pins recomputed against code constants, every named path/flag/field checked to exist, `test_docs_freshness` 31 OK) — MERGEABLE. Rows 3–5: no fix rounds; findings dispositioned in 39e3f9e1 record 02's lead disposition and above; same-signature statement in record 04 (no repeated class; trigger not met). Rows 7–8: this record. Row 9: replay 24 at 97da620e (`JouleWise-wt-hprime`, `python3 scripts/shard_tests.py --workers 4 --split`, started 10:32 PDT), tail appended below. Row 11: CI at 97da620e. Row 12: this record.

**Standing escalation check.** Two reviews, zero fix rounds, no shared defect class; the cold gate is not owed.

**VERDICT: MERGE on replay PASS at 97da620e and CI green at 97da620e**, under D-072. The merge commit on main is H′ for tonight's plan; `git merge-base --is-ancestor` of it against `origin/main` is the A2 check in Block A.

## Replay tail (row 9) — appended when the run lands

Replay 24 died with activation 36d3a823; replay 25 (activation 4824d78c, nohup pid 99611, `JouleWise-wt-hprime` at 97da620e, `python3 scripts/shard_tests.py --workers 4 --split`, log `/tmp/magistrate-4824d78c/replay-25-hprime-97da620e.log`, 1,161,341 bytes) started 10:53 PDT and finished 11:40:56 PDT; harvested from disk by activation 1944317a at 11:50 PDT. Exact summary lines and tail:

```
replay-25 start 2026-09-11T10:53:20-0700 head=97da620ef3467cfb980632ef890209b52fe59134
===== SHARD 1/4 OUTPUT =====
MODULE START tests.test_2k_amplification
test_bound_formula_handles_extreme_skew_and_negative_offsets (test_2k_amplification.ClockMathAmplificationTests.test_bound_formula_handles_extreme_skew_and_negative_offsets) ... ok
test_client_alignment_record_rederives_controller_timestamp_from_raw_node_time (test_2k_amplification.ClockMathAmplificationTests.test_client_alignment_record_rederives_controller_timestamp_from_raw_node_time) ... ok
...
----------------------------------------------------------------------
Ran 8 tests in 0.001s

OK
MODULE PASS tests.test_workload_sizing tests=8 failures=0 errors=0 skipped=0 seconds=0.002
SHARD SUMMARY index=4/4 modules=62 tests=1509 failures=0 errors=0 skipped=5 result=PASS
WORKERS SUMMARY shards=4 modules=232 tests=6036 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
replay-25 rc=0 end 2026-09-11T11:40:56-0700
```

Summary lines:

```
replay-25 start 2026-09-11T10:53:20-0700 head=97da620ef3467cfb980632ef890209b52fe59134
SHARD SUMMARY index=1/4 modules=52 tests=1390 failures=0 errors=0 skipped=50 result=PASS
SHARD SUMMARY index=2/4 modules=59 tests=1214 failures=0 errors=0 skipped=7 result=PASS
SHARD SUMMARY index=3/4 modules=59 tests=1923 failures=0 errors=0 skipped=47 result=PASS
SHARD SUMMARY index=4/4 modules=62 tests=1509 failures=0 errors=0 skipped=5 result=PASS
WORKERS SUMMARY shards=4 modules=232 tests=6036 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
replay-25 rc=0 end 2026-09-11T11:40:56-0700
```

**Row 9 result: PASS** — 4 shards, 232 modules, 6036 tests, 0 failures, 0 errors, 109 skipped, rc 0.
