# A309 BFGD-VERDICT-MERGE-LIVENESS-01 — cold Fable final pass (gate row 7)

- **Judge:** Fable 5.1, cold session, worktree `JouleWise-wt-a309-fp-6bec2aa6` at `58bfd3b0` (branch `fix/2026-09-26-bfgd-verdict-merge-liveness`, main `6a463e87` merged in). Working tree clean.
- **Not read:** RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, the decision log.
- **Read:** the diff `6a463e87..58bfd3b0`; `load_committed_verdict` in full; the dictated closure `10-liveness/ex-01-dictated-closure-M1.md`; `70-a309-gate/10-sol-execution-lens.md`; `70-a309-gate/11-opus-contract-lens.md`; the cold-gate ruling `50-coldgate/10-coldgate-fable-ruling.md` (E20, F-C, D2) and the addendum `30-addendum/21-coldgate-fable-addendum-ruling.md` §4 text 3.
- **Protocol:** single foreground session; no subagents, no background tasks. Scratch under `/tmp/a309fp/`.

## Verdict: MERGE

The candidate implements the dictated closure verbatim, every dictated test module is green here, no probed history authenticates bytes that differ from the honest adding commit, the Sol F1 disposition is accepted, and the merge-before-S0 ordering satisfies both rulings' purpose. One ordering obligation is placed on S0 (§Q3), not on this PR.

## 1. Executed evidence

| # | Command (cwd = candidate worktree unless noted) | Observed |
|---|---|---|
| E1 | `git diff --stat 6a463e87 58bfd3b0` | 2 files: `joulewise/battery_float.py` +6/−4, `tests/test_battery_float.py` +48. The hunk is inside `load_committed_verdict` only. |
| E2 | `grep -c` of the four dictated lines (both `_git(... "log" ...)` calls, the new `raise NoRecord(...)`, the `# --no-merges:` comment) | 1, 1, 1, 1: character-identical to the closure text. The `len(touching) != 1 or adding != touching or not _COMMIT.fullmatch(...)` test is unchanged; the blob check sits immediately after it. |
| E3 | `python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers` | `Ran 69 tests in 118.087s  OK` (includes `GrammarFreezeTests`, so the R2-9 `_structure`/`_recorded_values` pin is green). |
| E4 | `python3 -m unittest tests.test_issue_calibration_acceptance_generation` | `Ran 156 tests in 401.016s  OK` |
| E5 | `grep -c "PairVerdict\|authenticate_pair" joulewise/battery_float.py` on the candidate and on `origin/main` (`6a463e87`) | 0 and 0: **S0 has not merged**; `origin/main` equals the merged-in main. |
| E6 | `git ls-files configs/calibration/battery_float_verdicts` | empty: **no committed harvest verdict exists on main**; no existing record changes disposition under the new loader. |
| E7 | `/tmp/a309fp/probe.py`: eleven adversarial histories through the real `CommittedVerdictTests` fixture, each run against the candidate loader AND the pre-change loader (`git show 6a463e87:joulewise/battery_float.py` loaded as a separate module) | Table below. |
| E8 | `scripts/issue_calibration_acceptance_generation.py:1396-1400, 1614-1631` | The issuer's only entry is `authenticate_committed_verdict(repo_root, ...)` at HEAD; `battery_float_module_sha256` is the whole-file digest, recorded at harvest and never compared by `compare_verdict` (`:632-640`). |

**E7 probe table** (`H` = the honest harvest commit; "loaded bytes == H" is a byte comparison of the working-tree record against `git show H:<rel>`):

| Probe | History | Candidate | Pre-change loader |
|---|---|---|---|
| P1 (Sol F1) | evil merge rewrites, second evil merge restores; HEAD bytes == H | LOAD, commit = H, loaded bytes == H: True | NoRecord (3 commits, 1 adding) |
| P2 | evil merge rewrite survives to HEAD | NoRecord (adding commit's bytes differ from HEAD) | NoRecord (2 commits, 1 adding) |
| P3 | forged non-merge on main + honest on branch, conflict resolved to the honest bytes | NoRecord (2 commits, 2 adding) | NoRecord (3 commits, 2 adding) |
| P4 | non-merge remove, non-merge re-add of identical bytes | NoRecord (3 commits, 2 adding) | same |
| P5 | merge deletes the record | NoRecord (absent or uncommitted) | same |
| P6 | merge flips only the file mode, bytes identical | LOAD, loaded bytes == H: True | NoRecord (2 commits, 1 adding) |
| P7 | merge rewrite, then non-merge restore | NoRecord (2 commits, 1 adding) | NoRecord (3 commits, 1 adding) |
| P8 | sole forged adding commit with its own pin | LOAD (status evidence_missing) | LOAD, identical: pre-existing surface, untouched by A309 |
| P9 | forged bytes copied over the record by a non-merge commit, H in history | NoRecord (2 commits, 1 adding) | same |
| P10 | honest record first committed inside a merge commit | NoRecord (0 commits, 0 adding) | NoRecord (1 commits, 0 adding) |
| P11 | honest `--no-ff` merge into moved main, then a second unrelated `--no-ff` merge | LOAD, commit = H, loaded bytes == H: True | NoRecord (2 commits, 1 adding) |

Every LOAD in the table returns bytes equal to the unique non-merge adding commit's bytes. Every history the old loader accepted (P8) is accepted unchanged; the newly accepted set (P1, P6, P11) is exactly "merges touched the path, HEAD still holds the adding commit's bytes".

## 2. Q1: faithful and complete; no history authenticates different bytes

**Faithful.** E2: all three dictated items are character-identical and in the dictated position. Tests (a), (b), (c) exist under the dictated names beside `:504`, on the shared fixture; (c) pins the count route (`2 commits, 2 adding`) after the bench NIT; `:504` is untouched. The Opus lens's RED proof at the `b2c31e5b` baseline for (a) and (b) is consistent with my old-loader column (P11 and P2 refuse with the count message on the old code).

**Complete against the closure's run obligations.** E3 and E4 are the three dictated modules, all OK. `_structure` and `_recorded_values` are untouched (E1) and the R2-9 pin passes (E3). The E2 pin proof (cold-gate v1 E2) concerns pack registrations and this diff touches none.

**No history authenticates bytes that differ from the honest adding commit.** The argument is structural, and E7 exercises its edges:

1. `touching` is every non-merge commit in HEAD's ancestry whose tree differs from its parent at the path. `--full-history` follows all parents of every merge, so no non-merge commit is simplified away (P3, P7, P9: side-branch and post-merge edits are always counted). `--no-renames` changes only the status letter and cannot drop a commit from `touching`. `--no-merges` removes merge commits only.
2. The loader requires `touching == adding == [C]` for one commit C, then requires `HEAD:<rel>` bytes == `C:<rel>` bytes, then binds the ledger-head pin at C (step 5).
3. Therefore the consumed bytes are always the bytes committed by the sole non-merge commit that added the path. If the honest harvest commit H is in HEAD's ancestry, C == H (any second non-merge toucher refuses: P3, P4, P7, P9). If H is not in the ancestry, C is a different sole adding commit, which the old loader accepted identically (P8) and which the identity, slot-binding and pin checks govern as before. A309 opens no new path of that kind.
4. Merge commits can change the path transiently (P1) or in mode only (P6) without refusal, and can delete it (P5, refused at step 1). None of these can put bytes other than C's at HEAD and load (P2).

**Liveness residue noted, not a defect.** P10: a record first committed inside a merge commit still refuses (0 commits). The harvest procedure commits the record and its pin in one ordinary commit, so this shape is operator error and the refusal is correct.

**Pre-existing, out of scope (for awareness).** Shallow clones (Opus noted) and `refs/replace` objects are honoured by `git log`/`git show` in both the old and new loader; both are operator-only surfaces and unchanged by this diff.

## 3. Q2: the F1 disposition is accepted

Sol's F1 (rewrite-then-restore across two merges loads) reproduces here as P1: the loaded commit is H and the loaded bytes equal H's bytes byte-for-byte. Truth impact is nil: the issuer consumes HEAD's bytes (E8), those bytes are H's, the pin is bound at H, and the transient rewrite remains visible in git history for any auditor. Sol's proposed remedy (walk every reachable merge and compare its record entry with each parent's) would restore precisely the class of refusal M-1 was ruled to remove, with new shapes (criss-cross merges, conflict resolutions in unrelated paths that re-touch the entry) able to trap an honest record, while catching nothing that can change a number. The inline comment's claim ("a merge that rewrites the record is caught") is exact for any rewrite present at HEAD, which is the only rewrite the loader can ever hand to a consumer; the step-2 header now states the full invariant (fixed in `67231358`). Keep the dictated text.

## 4. Q3 (ordering): merging A309 before S0 is consistent with both rulings

**Text 3's purpose** is that the issuer recomputes with main's code and cannot disagree with itself mid-epoch, enforced by a source-digest pin that S0 installs. **The M-1 ruling's purpose** is that an honest harvest verdict reaching main by `--no-ff` merge must load.

**Facts that resolve it.** S0 has not merged (E5). No harvest verdict exists on main (E6). The Revision 5 epoch has not issued and W1 has not run (given in the charge; consistent with E6). So there is no committed verdict, no issuance and no harvest that has ever been evaluated by any version of `load_committed_verdict` inside the epoch. If A309 merges first, S0's pin is computed over the post-M-1 source and every harvest and issuance in the epoch runs one version. Text 3's rationale is satisfied exactly, not by exception.

**The struck exception.** The v1 cold-gate ruling struck the synthesis's M-1 carve-out on packet grounds (E20: the ruling was not in the packet), and its D2 text says what to do if the ruling exists: "the S1 brief quotes its text and the pin test names it, otherwise the freeze is absolute". v1.1 text 3's "No exception is granted by this ruling" is that ruling declining to grant one itself; it does not, and could not, forbid a separately ruled edit landing before the pin exists. Merging A309 before S0 needs no exception at all: the freeze binds from the pin's installation, and the pinned bytes are the post-M-1 bytes.

**What must happen for the ordering to hold (obligations on S0, not on A309):**

1. A309 merges before S0's PR is opened against main, or S0 rebases onto the A309 merge head before computing its pin digests. A pin computed over pre-A309 bytes would fail on merge or, worse, freeze the liveness trap back in.
2. S0's pin test names the M-1 ruling (`10-liveness/ex-01-dictated-closure-M1.md`) as the baseline for `load_committed_verdict`, per the v1 D2 condition, so the pinned digest is traceable to its ruling.
3. No harvest verdict is committed to main between the A309 merge and the S0 merge under any loader other than the post-M-1 one. E6 shows none exists today and W1 has not run, so this holds by default; S0's PR body states it.

If S0 were already merged with a pre-A309 pin, the correct action would be a FIX-FIRST on S0 (recompute the pin, citing M-1), not a refusal of A309. That is not the case now (E5).

## 5. Findings

- **BLOCKER:** none.
- **SHOULD-FIX:** none.
- **NIT (no change required):** the comment at `battery_float.py:585` says a rewriting merge "is caught by the adding-blob check"; that is true for the only rewrite a consumer can see (one present at HEAD). The header at `:579` already carries the precise invariant. Leave the dictated text.

## 6. Disposition

**MERGE** `58bfd3b0`. Then S0 under the three obligations in §4.
