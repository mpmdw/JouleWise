# A309 BFGD-VERDICT-MERGE-LIVENESS-01: Opus CONTRACT lens

- **Candidate:** `87aad39c7c8d543afc252395797a948e3b4373da` (parent `64e39bb9`), in the worktree `JouleWise-wt-a309-opuslens-6bec2aa6`.
- **Authority:** `10-liveness/ex-01-dictated-closure-M1.md` and `10-liveness/00-seat-brief.txt`.
- **Lens:** CONTRACT (Opus 5.5). Read-only; scratch files are in `/tmp/a309lens/`.

## Verdict

**PASS. No BLOCKER and no SHOULD-FIX; there are two NITs.** The candidate implements the dictated closure exactly. Consumers see the same contract as before. The comment's claim holds wherever it matters: a merge-borne rewrite that is still present at HEAD is refused. The flag combination `--no-renames` + `--full-history` + `--no-merges` cannot hide a non-merge commit that touches the path.

## 1. Line-by-line check against the dictated closure

| Dictated item | Candidate (`joulewise/battery_float.py`) | Match |
|---|---|---|
| (1) `touching = (_git(root, "log", "--full-history", "--no-merges", "--no-renames", "--format=%H", "--", rel) or b"").decode().split()` | line 580, character-identical | yes |
| (1) `adding = (... "--no-merges", "--no-renames", "--diff-filter=A", "--format=%H", "--", rel) ...)` | line 581, character-identical | yes |
| (1) the `len(touching) != 1 or adding != touching` test is unchanged | lines 582–584 unchanged, including the `_COMMIT.fullmatch` conjunct | yes |
| (2) `if _git(root, "show", f"{touching[0]}:{rel}") != committed: raise NoRecord("path history is not a single adding commit (the adding commit's bytes differ from HEAD)")` | lines 586–587, character-identical, placed immediately after the count test | yes |
| (3) the comment is verbatim and sits above step (2) | line 585, verbatim | yes |
| Tests (a) and (b) use the dictated names, sit beside `:504`, and use the shared fixture (`self.write`/`self.commit`/`self.git`/`assert_no_record`) | `tests/test_battery_float.py` +518…+564 | yes |
| (c) `:504` is unmodified and the add/add `--theirs` test exists | `test_merge_branch_modify_then_restore_is_no_record` is untouched; `test_add_add_theirs_conflict_still_refuses` is added (no such test existed before) | yes |
| Scope is exactly the two WRITE_SCOPE files; `_structure` (l.97) and `_recorded_values` (l.214) are untouched | `git diff --stat 64e39bb9 87aad39c`: 2 files, +53/−3; the hunk covers only `load_committed_verdict` | yes |

`committed` is the value returned by `ingest_git_authentication_input`. That function returns `raw` unchanged, both with no active session (`authentication_io.py:635`) and with one (`:513`). The new check therefore compares raw blob bytes with raw blob bytes, so it adds no false-refusal risk from normalisation.

**RED proof for (a), re-executed by me.** I used a `/tmp` tree built by `git archive 87aad39c`, with `joulewise/battery_float.py` replaced by `git show 64e39bb9:joulewise/battery_float.py`. `git diff b2c31e5b 64e39bb9 -- joulewise/battery_float.py` is empty, so this file is identical to the dictation's `b2c31e5b` baseline.
```
ERROR: test_honest_harvest_merged_no_ff_into_moved_main_loads
joulewise.battery_float.NoRecord: path history is not a single adding commit (2 commits, 1 adding)
FAIL: test_evil_merge_rewriting_record_is_no_record
AssertionError: "adding commit's bytes differ" not found in 'path history is not a single adding commit (2 commits, 1 adding)'
FAILED (failures=1, errors=1)        # (c) passes at base, as it should
```

**Green on the candidate (executed):**
```
python3 -m unittest tests.test_battery_float                          -> Ran 59 tests in 65.367s  OK
python3 -m unittest tests.test_battery_float_consumers                -> Ran 10 tests in 10.993s  OK
python3 -m unittest tests.test_issue_calibration_acceptance_generation -> Ran 156 tests in 187.715s OK
python3 -m unittest tests.test_calibration_cadence_report tests.test_battery_float_sweep -> Ran 12 tests OK
```
I also started the full set of other `tests/test_*.py` modules that mention `battery_float` (18 modules). That run exceeded the 600 s foreground limit and was moved to the background, so **no result is recorded here**. Of those modules, only `test_issue_calibration_acceptance_generation`, `test_battery_float_consumers` and `test_battery_float` reach `load_committed_verdict` or `authenticate_committed_verdict` (grep below), and all three ran green above.

## 2. Callers and the consumer contract

`grep -rn 'load_committed_verdict\|authenticate_committed_verdict' --include='*.py' .` finds these production call sites:
- `joulewise/battery_float.py:715`: `authenticate_committed_verdict` is the only caller of `load_committed_verdict`. The consumer AST guard `tests/test_battery_float_consumers.py:25-30` still passes.
- `scripts/issue_calibration_acceptance_generation.py:1398` and `scripts/calibration_cadence_report.py:83`: both call `authenticate_committed_verdict`. The issuer persists `verdict.commit` as `verdict_commit` (`:2097`, `:2104`).

**Contract preserved.** The returned `commit` is still `touching[0]`, a non-merge commit that added the path.

The old code accepted a history only when exactly one commit touched the path, and that commit was a non-merge add. Old `--full-history` without parent rewriting also lists any merge that differs from any of its parents (the RED output shows this: "2 commits"). Under the old test, then, no merge changed the path. It follows that HEAD's bytes equal the adding commit's bytes, and the new code returns the same commit for every history the old code accepted.

The new code accepts a strict superset: histories in which merges touch the path but HEAD's bytes still equal the adding commit's bytes. For every newly accepted history, the bytes consumed are the ones committed at the adding commit, and step 5 still binds the ledger-head pin at that commit. All refusals remain `NoRecord`, which maps to `record_unauthenticated`. Every refusal message keeps the prefix `path history is not a single adding commit`, so existing `assertIn` checks that use that prefix still hold.

## 3. The claim "a merge that rewrites the record is caught by the adding-blob check"

I ran adversarial histories through the real fixture: `/tmp/a309lens/probe.py`, which subclasses `CommittedVerdictTests`. Output on the candidate:
```
P01 evil-merge rewrite then evil-merge restore (HEAD bytes == C): LOADS commit=C status=pass
P02 side-branch modify merged -s ours (HEAD keeps honest): NoRecord: ... (2 commits, 1 adding)
P03 add/add, merge -s ours keeps main's: NoRecord: ... (2 commits, 2 adding)
P04 honest harvest via octopus merge: LOADS commit=C (harvest commit)
P05 evil octopus rewriting record: NoRecord: ... (the adding commit's bytes differ from HEAD)
P06 merge deletes, merge re-adds FORGED bytes: NoRecord: ... (the adding commit's bytes differ from HEAD)
P07 rename from other path into rel (with pin): LOADS (equivalent to a plain add + pin)
P08 side renames rel away, merge keeps rel: NoRecord: ... (2 commits, 1 adding)
P09 cherry-pick of adding commit + merge of original: NoRecord: ... (2 commits, 2 adding)
P10 harvest on unrelated root merged in: LOADS commit=C (orphan harvest commit)
P11 typechange rel -> symlink: NoRecord: working tree differs from HEAD
```
- The claim is **true for every rewrite that survives to HEAD**, including two-parent merges (test (b)), octopus merges (P05) and delete-then-re-add across merges (P06).
- **P01 is the one newly accepted "tampered history".** Two merges rewrite the record and then restore it byte-for-byte. The loader returns the honest bytes and the honest adding commit, and the pin binding is still checked at that commit. Only HEAD's bytes are consumed, and they are exactly the adding commit's bytes, so this cannot produce a false number. The literal claim in the comment ("caught") therefore needs no correction. The step-2 header comment is slightly stale, though; see NIT-1.

## 4. Can `--no-renames` with `--full-history --no-merges` hide a touching commit?

**No.** `git log --full-history -- <path>` without parent rewriting walks every parent of every merge. It shows each commit whose tree differs from a parent's tree at the path. Commit selection uses that tree comparison, which is independent of rename detection. `--no-merges` then removes only merge commits. Every non-merge commit in HEAD's ancestry that changes the path is therefore listed.

- P02 is the evidence: the side-branch edit is still counted even though the `-s ours` merge leaves main's copy unchanged.
- `--no-renames` changes only the status label: a rename into `rel` is labelled `A`, as P07 shows. It cannot remove a commit from `touching`.
- A symlink type change is status `T` and appears in `touching` but not in `adding`. P11 is refused earlier, at the working-tree check.

**Configuration sensitivity (executed).** I reran the fixture class and P01–P11 with `GIT_CONFIG_GLOBAL` set in turn to `log.follow=true`, `diff.renames=copies`, `log.showSignature=true` and `core.ignoreCase=true`. `CommittedVerdictTests` stayed OK every time, and no probe changed from refusing to loading. The only change was `log.follow=true`, which makes P07 refuse (`2 commits, 1 adding`). That is stricter, not weaker.

## Findings

**BLOCKER:** none.

**SHOULD-FIX:** none.

**NIT-1: the step-2 header comment is stale.** `battery_float.py:579` still reads `# 2. Exactly one commit in HEAD's history touches the path, and it added it.` After this change the invariant is "exactly one *non-merge* commit touches the path and added it, and HEAD's bytes equal that commit's bytes". Merges may touch the path (P01). The dictated comment at l.585 carries the full meaning, so this is cosmetic.
- Fix, if wanted in a later touch outside the verbatim closure: `# 2. Exactly one non-merge commit in HEAD's history touches the path, it added it, and HEAD holds its bytes.`

**NIT-2: test (c) does not pin the refusal route.** `test_add_add_theirs_conflict_still_refuses` asserts only the shared prefix `path history is not a single adding commit`. That prefix also appears in the new blob-check message, so the test would stay green if the count test were accidentally weakened and the blob check fired instead. `:504` has the same property, but it is dictated as unmodified.
- Fix: assert `"path history is not a single adding commit (2 commits, 2 adding)"` in (c). This is the route I observed; P03 and the fixture use the same shape.
- (Optional) Test (b) rewrites toward the more conservative status (`battery_float_evidence_missing`). The check compares bytes, so the direction does not matter, but a rewrite toward `pass` would document the threat the check exists for.

**Out of scope (pre-existing, not introduced by this diff; for awareness only).** In a shallow clone, the grafted boundary commit looks like it adds every file. The loader could then name the boundary commit as the adding commit, and step 5 would refuse unless the pin has not changed since. The history flags in this diff do not affect this.
