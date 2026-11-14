# Cold audit: Block 6 release record, PR #769

Auditor: Claude Mythos 5.2, read-only, blind. Audited 2026-11-13 17:59 to 18:10 PST (`date`).
Record under audit: `docs/registrations/block6_release_record.md` / `.json` at head `2d8a8ee7b` (md SHA-256 `c0c021d0…a5fd`, json `5139d68e…100d`).

## Verdict: ADMIT WITH FIXES

**Do not merge the PR as it stands. Merge after findings 1 and 2 are closed.**

Everything the record states is true except one commit pointer (finding 4). Every digest I could recompute matches. The r2 gate run, dry run, probe, term 7 and release check pass by RL-134's own definitions. The registration hash is valid at the named commit and at current `origin/main`.

Two things block the merge today:

- The record is incomplete against two later rulings that add to what it must carry (RL-144 addendum §2 and RL-142 §2 item 6). The evidence exists and passes; it is just not in the record.
- CI is red on the head, so the repository's own merge rule is not met.

Neither fix needs a program run on custody. Both are docs and CI work.

## Findings

### 1. BLOCKING. The record omits what the RL-144 addendum says the release record must list

The RL-144 addendum §2 binds "today's release" and names the release record four times (`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`, lines 10274-10296, commit `bc1d78b72`):

- §2 item 1: "The lead lists the modules run and their counts in the release record."
- §2 item 2: "Each failing id is listed in the release record with one of: base-inherent and reproduced (name the base), platform (passes on macOS at r2), or unexplained."
- §2 item 4: "The two guards of §3 are listed as base-inherent, with §3's text."
- §3 M2: a frozen Block 5 file (`joulewise/flags/exclusions.py`) was edited without a cited rebind; "The release record carries one line saying so."

Its gate line reads: "Release on §2 item 2 and RL-134's conditions on r2."

The record has none of this. A grep of the record for `RL-144`, `base-inherent` and `test_block6` finds nothing.

The substance is satisfied elsewhere, on the audit branch (`evidence/pr762/README.md`, commits `650cb80f5`, `852fd1605`, `301b63273`):

| Item | Evidence found |
|---|---|
| Named set green at r2 on macOS before the gate run | `test_block6` + `test_b6_production`: 62 OK; `test_b6_release_record` + `test_b6_structure_probe`: 40 OK (`rl144-premerge-b.log`, done 15:55:45; gate r2 started 15:58:11). Kit end-to-end "8 OK" is asserted in the README with no kept log |
| Failing ids classified | hosted run 43521257617: 75 log lines, 41 distinct ids, all equal to the Linux baseline on `3551e1a7d` (run 43525694693). Unexplained: none. Named set: none |
| M2 closure check | `exclusions.py` `ebe1678c…0ad6` is a row of the 24 (verified) |
| M1 check | registration §3.3 states 10.818 ms (lines 386-393; I checked it myself) |

**Fix.** Add a section to the record before the merge: the modules and counts, the classification table (or the evidence file by path, commit and SHA-256), M1 and M2 as base-inherent with §3's text, and M2's follow-up line. Alternatively the research lead rules that the evidence file meets "listed in the release record". The renderer has no field for this, so it is a hand-written section or a renderer change.

### 2. BLOCKING (state at 18:08 PST). CI is not green on the head, and the PR cannot merge under TIER-01

`gh pr checks 769` at 18:08:31 PST:

```
gate-ledger     fail    (run 43542262280)
test (3.13, 1)  fail    20m35s (job 132285504996)
test (3.13, 3)  pending
```

`gh pr view 769`: `isDraft: true`, `mergeStateStatus: BLOCKED`. The PR body's ledger row 3 reads `NOT-RUN`, which is why `gate-ledger` fails (`scripts/check_gate_ledger.py:219`). A light-tier PR needs CI green on the final head (`docs/orchestration.md:266`).

I could not read the failing shard's log (the command was denied in this session). PR #764's ledger records a "watchdog clock flake" on the same shard, with PR #767 open to fix it, so a flake is plausible. That is not confirmed for this run.

**Fix.** Read the shard 1 failure and classify it. Re-run to green. Fill row 3 with the head SHA. Any edit for findings 1, 3, 4 or 5 moves the head, so the green run must be on the new head.

### 3. SHOULD-FIX. Comparisons (a) and (b) are release conditions under RL-142 and are not in the record

RL-142 §2 item 6: "Release conditions are RL-134's, on r2, with 48 in place of 44 and comparisons (a) and (b) added." The record's table has eleven rows. The 48 is there (condition 4). The two comparisons are not.

Both pass. I read only the top-level verdict and count fields of the result files:

| | Result file SHA-256 | Mode, dirs | Verdict | Differing / unowned |
|---|---|---|---|---|
| (a) | `b3717ec3…5f9b` | a, `gate-2` vs `gate-r2` | PASS | 27 / 0 (per records §G) |
| (b) | `8b805e8e…e6eb` | b, `dry` vs `dry-r2` | PASS | 176 / 0 |

Both name comparer `eb82b6e2…02c1`, which is the file on disk at `rl142-cmp-v2/compare_rl142.py`.

**Fix.** Add the two rows with these digests, in the same edit as finding 1.

### 4. SHOULD-FIX. Condition 9 cites a commit that is not on `main`

The record's condition 9 evidence: "S-16 line 236c8f708 (RL-134 item 17)".

- `git merge-base --is-ancestor 236c8f708 76a6eba99` exits 1.
- `git branch -r --contains 236c8f708` gives only `origin/docs/2026-11-13-b6-s17-fill-staged`.
- The line reached `main` as `255ab96cc`, inside PR #748's merge `35b94bca5`.

The fact holds. The §17-S16 line is byte-identical at `236c8f708`, `255ab96cc` and `76a6eba99` (`grep "§17-S16 (RL-134" | shasum` gives `5e5cf37e…a9a5` for all three), and §14's S-16 row reads "filled 2026-11-13 (§17-S16)". Only the pointer is wrong.

**Fix.** Cite `255ab96cc`. The cite is baked into the draft through `--cite`, so either re-run `check` with a new `--receipt-out` (RL-139 reading 10 allows it; about two minutes) or add a dated correction line.

### 5. SHOULD-FIX. The record's release time is the render time, and three things are tied to today's date

The record opens "Released under its registration on 2026-11-13 17:38 PST" and then says the commit on `main` is the release event. At 18:08 PST that commit does not exist. 17:38 is when the record was rendered (commit `2d8a8ee7b`, 17:38:52).

Three statements depend on the merge landing on 2026-11-13 PST:

- the record's date;
- the RL-6 (d) line: "Block 6 is released under its registration on 2026-11-13" (RUN_STATE item 309);
- Ed's renewed OK: "release today ... any further stop moves it to tomorrow and to the research lead" (same item).

**Fix.** When the record is re-rendered, word the first line as signed-at, not released-at, or re-date it from `date`. If the merge slips past midnight PST, re-date the record and the RL-6 (d) line and get Ed's OK again (RL-142 §3 already says a next-day release uses the same r2 outputs with no further run).

Also owed at the merge and not in this PR: the `RUN_STATE.md` item with the time from `date` (runbook step 12).

### 6. SHOULD-FIX. Ed's OK rests on the lead's paraphrase

Conditions 1, 2, 9, 10 and 11 are "cited, not checked" by the tool (`checked: false`). I checked 1, 2, 9 and 10 against `RUN_STATE.md` and git and they hold (9 with finding 4's pointer). Condition 11 I cannot check.

RUN_STATE item 309 reports Ed's OK of 08:45 and its renewal at 14:30 in the lead's words. It quotes nothing. Item 231, the Block 5 precedent, quoted Ed verbatim. RL-142 §3 says this release "needs Ed again".

**Fix.** Ed confirms on the PR, or performs the merge himself.

### 7. NOTE. The r2 predeclaration amendment was committed 46 s after the r2 gate run started

Runbook step 6 says the predeclaration is committed before any program run. Commit `0dbfd105f` is stamped 15:58:57; gate r2 started 15:58:11 and ended 16:03:31; dry r2 started 16:03:52.

No value the gate depends on changed in that amendment. The count of 48 was predeclared by RL-142 (committed 14:30, `1f54727cb`), fixed in the tools at 14:50 (`f19f36081`), and produced by `b5-probe` at 15:57:52, before the gate. Records §G discloses the order. I could not verify when the branch was pushed.

The predeclaration lives only on `docs/2026-11-13-b6-s17-fill-staged`, not on `main`, and the record does not cite it.

### 8. NOTE. The registration's S-14 row still names the first pin

§14 row S-14 gives commit `3551e1a7d`, tag `b6/analysis` and RC-B6-1 `90e22603…` as the fill. §17-R3 cites the R3 table at that commit. Revision 2 is recorded only by §17-R13 (tag and digest, no commit SHA) and the addendum row (which has the commit). The record's "S-14 commit `6e6d1b18a`" therefore differs from §14 on its face. Records open points 1 and 2 put this to the research lead; I found no answer.

Suggested: the identity row says "revision 2 (§17-R13; supersedes `3551e1a7d`)".

### 9. NOTE. The S-14 line is not on `main`

`git branch -r --contains 6e6d1b18a` gives only `origin/analysis/2026-11-13-b6-s14-merge`. RL-134 item 18 said a PR is "opened at the cut"; none of today's open PRs is from that branch. This gates nothing (item 18, runbook step 17). It is owed after the release, with RL-144 addendum M1 and M2. Until then the 24 pinned files are reachable from the tag and that branch only.

### 10. NOTE. "No person or agent opened the restricted outputs" leaves out one program

Programs opened them, by ruling: the pinned program, the launcher and release check (hash only), the structure probe (RL-134 item 4), and the RL-142 comparer on `gate-2`, `gate-r2`, `dry` and `dry-r2` (RL-142 §2 item 5). The comparer is not in RL-134 item 10's list and the record does not mention it. One clause would cover it.

### 11. NOTE. Smaller points

- The conditions table is ordered 1, 10, 11, 2, …; the ledger prints `None` for empty class and code.
- The Markdown ledger omits each attempt's time and output digests. The JSON has both.
- The record does not say which mode ran (serial, `--workers 1`; RL-134 item 13 asks for it) or name the tool commits (`f19f36081`, kit `e1f4f8052`).
- The tier is light. That is defensible, since the PR changes no registration byte. It is also the unblinding event, and TIER-01 resolves any disagreement to full. This audit can stand as row 1 evidence if wanted.

## Answers to the five questions

**1. Does the record tie every item step 12 requires?** Yes for step 12's own list; every one is present and correct (table below). No for the additions of RL-142 and the RL-144 addendum (findings 1 and 3).

**2. Is the registration hash still valid?** Yes. `7243a2bc…4ead` at `76a6eba99`, at `HEAD`, in the working tree, and at `origin/main` `783381fac` (re-fetched 18:08). One commit landed after `76a6eba99`; it touches `RUN_STATE.md` and `docs/process/CURRENT.json` only. Merging now leaves the record true. The commit the record names is the PR's base, not the merge's first parent, so re-hash the file at `origin/main` immediately before merging.

**3. Are the r2 gate, dry run, probe, term 7 and release check PASS by RL-134's definitions?** Yes.

| Check | Evidence |
|---|---|
| Gate r2 | exit 0, `complete`, `time_wrapper_exit` 0, 319.3 s against an 1,800 s limit. One-session `block` on `r1-alpha`, no `--closed`, no `--block5` (item 1). Probe `ok`: `option_c.pass` true, 0 failures, every compared class failed 0 and unmatched 0, no `__block__` entry, 122 = 4 + 118 |
| Dry r2 | exit 0, `complete`, 2,805.1 s against W_pred 3,200, alarm 4,800, stop 6,400. Nine sessions in the registered order, `--closed`, `--block5`, `--workers 1`. Peak RSS 1.76 GB. stderr empty |
| stdout | the recorded stdout digests equal the SHA-256 of the one relayed line plus a newline, for both runs, so each stdout holds exactly that line with `comparison_stopped=false` |
| Probe, dry | every check `ok` or `reported`; no `departs`, no `not_checked`; 20 flags, none with `stops_comparison`; pairing as §17-R7; counting 3/3/3; P* removals 0 of 840; `block5_included` 48 = 48 (22/22/4) |
| Term 7 | `pass`, no stop class; compared 3,296, both-null 0, first-program-only 945 |
| Release check | exit 0, `release-check: pass`, 16:52:44 to 16:54:46; second receipt did not pre-exist, kit exit 0 |
| Ledger | five rows, equal to `attempts.jsonl` and to the five `*/record.json` directories; the three r1 attempts are in it. One class A attempt (limit three). The exit 3 went to the research lead (RL-142). No stop on r2 |
| Budgets | total wall of all five attempts 6,268 s (1.74 h) against RL-127's 8 machine-hours |

Conditions asserted without independent evidence: condition 11 (finding 6).

**4. Anything in RL-134 items 1-18 that should have happened before release and did not?** Nothing that gates the release.

- Items 1, 2, 4 to 8, 11, 12 and 17 are evidenced.
- Item 3 (kit): rebased, 117 tests pass, 96 mutants with 0 surviving; the end-to-end run at r2 is asserted without a log.
- Item 9: #748 merged at 13:23:27, before the first gate launch at 13:24:02. A fill-checker script exists on the staging branch; I did not see its output.
- Item 10: §17-R13 reached `main` at 17:38:14, before this record's commit; the RL-6 (d) line is on `main` since 16:52:19; Ed's OK is finding 6.
- Items 13 to 15 did not arise. Item 16 is post-release. Item 18's PR was not opened (finding 9).

**5. Anything else that would make me refuse the merge?** Findings 1 and 2 as things stand.

## What I verified, and how

| Item | Method | Result |
|---|---|---|
| Registration SHA-256 at `76a6eba99`, `HEAD`, `origin/main` | `git show <c>:<path> \| shasum -a 256` | `7243a2bc…4ead`, all equal to the record |
| 24 pinned files at `6e6d1b18a` | `git show` + `shasum`, each file | 24 of 24 equal to the record |
| 24 pinned files in the run checkout now | `shasum` on `/Volumes/JW-EXT/jw-wt/b6-s14-run/…` | 24 of 24; worktree HEAD `6e6d1b18a` |
| Catalog | row of the 24 | `b5bce6c6…a42b`, equal to §14 S-3 |
| S-14 r2 commit and tag | `git log`, `git rev-parse`, `git cat-file -p` | merge of `3551e1a7d` and `aaa2f3086`; tree `726501c9…` equals the fix commit's; tag object `e11a6003…` resolves to the commit; diff from S-14 is two files |
| Nine `harvest_sha256` | `shasum` of `<root>/<id>/archive/harvest.json` (the kit's definition, `b6_custody_kit.py:42,234`) | 9 of 9 equal |
| Manifest | `shasum` | `b2901d51…9d6b` |
| Both receipts | `shasum`; read the release receipt | both `57df8a76…0c91`. The receipt has no timestamp, so equal bytes are expected. Verdict `verified`, 169,070 files, 8,067,003,236 bytes, equal to RUN_STATE item 303 |
| `D_block`, `D_gate` | `shasum` | `0a1a149c…6a8e`, `ace8bfb4…7b9a` |
| Block 5 output, loop files | `shasum`, against the documents' `external` block | `c06ee7c8…cacc`; `attempts.jsonl` `1203f37b…6c32`; `state.json` `1e243f0d…ac90`; all equal |
| Output digests, all five attempts | `shasum` on `public.json`, `restricted.json`, `stdout`, `stderr` | 18 of 18 equal to the record and ledger; `public.restricted_sha256` equals the restricted file's for both r2 runs |
| Python, zstd, L9 | `record.json`, receipt, `structure.json` | 3.13.18; v1.5.7; `not_run` |
| Record against draft | read both | the record is the draft plus the six render fields; draft `result: pass`, no failed condition |
| Tools | `shasum` of the working files against `git show f19f36081:…` and `e1f4f8052:…` | equal; I read `b6_release_record.py` in full |
| RUN_STATE items 59, 231, 309, 310 | `git show origin/main:RUN_STATE.md` | as cited; item 309 is commit `a5c698e51`, 16:52:19, an ancestor of `76a6eba99` |
| Registration | read §1.10, §12, §13, §14, §17 | §12.3's "dated record tying the digests of this file, the catalog and every block-6 harvest record" is met; §17-R13 equals RL-142 §4 with the digest filled |
| Timeline | commit, tag and ledger timestamps | consistent with every events file |
| PR #769 | `gh pr view`, `gh pr checks` | two files added, nothing else; draft; state as in finding 2 |

## What I could not verify

- Ed's OK and its renewal (finding 6).
- Why CI shard 1 failed, and the `gate-ledger` log (commands denied).
- That the run checkout's porcelain is empty now (`git -C` denied). The release check logged `porcelain=0` at 16:52:44, and the 24 files re-hash.
- That the tag is on the remote (`git ls-remote` denied). The local tag object equals records §G, and the commit is on `origin/analysis/2026-11-13-b6-s14-merge`.
- A full custody census since 16:54:46. I re-hashed the manifest, nine harvest records, two loop files, the Block 5 file, both input documents and all outputs; I did not and may not run the kit's `verify`.
- That nobody read a restricted file. Nothing on disk can show it. In this session the file listing did not return `restricted.json`, `stdout` or `stderr` at all.
- File modes and the removal of `analysis-tmp` (`ls` and `stat` denied outside the worktree). Comparison (b) reports no extra files in either run directory.
- `samples.jsonl` (priority, other heavy jobs): not on my read list, not opened. CPU time of 2,583 s over 2,805 s wall is consistent with normal priority.
- The kit end-to-end run at r2, and the comparer's 18 of 18 (no kept log for either; the one logged comparer test run errored on a module path).
- Whether the per-count predictions of the J-item rulings hold in comparison (b). I confirmed verdict, comparer digest, 176 differing and 0 unowned; the research lead's cold check of PR #764 read the path names.
- Whether an open PR could change the registration before the merge. #765 to #767 are CI changes by title; I did not read their file lists.

## Files I read beyond the brief's list

- Rulings: `fable-rl142-dry-hold.md`, `fable-rl142-j-rulings.md`, `fable-rl144-release-ci.md`, and the decisions log on the audit branch.
- Logs and scripts: `rl142-postmerge.log`, `rl144-premerge*.zsh`, `rl144-premerge-b.log`, two lines of `b6-kit-r3-mutants.log`, and the first-attempt events files.
- Run directory: five lines of each `run-inputs-*-2.json` (`external`, `host`, `l9_audit`) and `mapping-report.json`.
- Comparer results: from `rl142-cmp-a.json` and `rl142-cmp-b.json`, the top-level verdict, mode, directory and count fields only, not the path lists.

I opened no blinded content: no `restricted.json`, no `stdout` or `stderr` file, nothing under `/Volumes/JW-EXT/b6-custody/` and no `analysis-tmp` was read; those files were touched by `shasum -a 256` only.