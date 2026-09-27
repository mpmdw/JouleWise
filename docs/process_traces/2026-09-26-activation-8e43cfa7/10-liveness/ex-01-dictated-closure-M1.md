## 6. Dictated closure texts

**M-1 (FIX-FIRST).** In `joulewise/battery_float.py` `load_committed_verdict`:

1. Both history calls become:
   ```python
   touching = (_git(root, "log", "--full-history", "--no-merges", "--no-renames", "--format=%H", "--", rel) or b"").decode().split()
   adding = (_git(root, "log", "--full-history", "--no-merges", "--no-renames", "--diff-filter=A", "--format=%H", "--", rel) or b"").decode().split()
   ```
   The existing `len(touching) != 1 or adding != touching` test is unchanged.
2. Immediately after that test, add:
   ```python
   if _git(root, "show", f"{touching[0]}:{rel}") != committed:
       raise NoRecord("path history is not a single adding commit (the adding commit's bytes differ from HEAD)")
   ```
   This catches a merge commit that rewrites the record, which `--no-merges` no longer lists.
3. Comment above step 2: `# --no-merges: an honest harvest commit reaching main through a --no-ff merge is one adding commit; a merge that rewrites the record is caught by the adding-blob check below (BFG-D row-6 M-1).`

Tests in `tests/test_battery_float.py`, beside `:504`, through the shared git-fixture helper:
- (a) `test_honest_harvest_merged_no_ff_into_moved_main_loads`: the harvest commit on a branch; main gains an unrelated commit; `merge --no-ff`. The record loads with `commit` equal to the harvest commit. It must be RED at `b2c31e5b`.
- (b) `test_evil_merge_rewriting_record_is_no_record`: the record on main; an unrelated branch; a `merge --no-ff --no-commit` that rewrites the record, then commit. Expect `NoRecord` containing "adding commit's bytes differ".
- (c) `:504` and the add/add `--theirs` shape still refuse.

Run `tests.test_battery_float`, `tests.test_battery_float_consumers` and `tests.test_issue_calibration_acceptance_generation`, and paste the tails. The pin proof of E2 must stay empty. `_structure` and `_recorded_values` are untouched, so the R2-9 freeze pin stays green.

