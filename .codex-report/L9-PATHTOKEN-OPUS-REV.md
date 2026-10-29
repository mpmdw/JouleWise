# L9-PATHTOKEN-OPUS-REV: executing review of b13a510dc..49991c73a

**Verdict: ACCEPT** (one residual-risk finding for the lead to acknowledge; no code change required).

Seat: Claude cloud session (scheduled routine), 2026-10-29. Python 3.13. TMPDIR=/home/user/rvtmp (outside the
checkout, no float-like token, no symlink). Synthetic archives only; no real block-5/6/BYTES data opened or searched.
Probes: `.codex-report/l9-pathtoken-opus-rev/probes.py` (reuses the seat's fixtures), output in `probes.out`.

## Findings (ranked)

1. **Residual, low: the source listing is self-pinned, not pinned by the index.** `archive_inventory`
   (`joulewise/b5_analysis/dry_run.py:210-234`) authenticates `harvest.json` against the index digest, but
   `sources/SHA256SUMS` only against the census's own digest of the same on-disk file
   (writer `dry_run.py:605-607`, validator `dry_run.py:363-367`). `harvest.json` `outputs` never contain the listing
   (`joulewise/b5/harvest.py:8141`; outputs are `derived/`/`withheld/` only), and `ArchiveHandle._sources` reads it
   with no expected digest (`archive.py:272`). Probe B: a listing edited consistently on disk before step 0 admits
   `sources/planted/value-0.7310.txt` end to end (step 0 ok, `validate_dry_run_record` passes). This is the
   pre-existing trust model for source names (at base such a name already entered the census if it had no
   number-like token); the change widens it to number-like names. It cannot carry an L9 result: step 0 writes the
   census before any analysis step of the run, and L9 never writes archive roots. The seat report states this
   honestly (DECISIONS 2). If an independent pin for the listing exists later (e.g. the transfer manifest),
   binding it would close the gap.
2. **Note: release mode fails closed without the step-11 record** when a changed row is a number-like inventory
   name (seat OPEN ISSUE 1). Confirmed by the seat's `release difference path` subtest. Needs a ruling before a
   release run, not before this merge.
3. **Note:** `archive_inventory` reads with plain `read_bytes` (follows symlinks), unlike `archive._read`. Harmless:
   step 0 already refuses a symlinked listing (`archive_path_invalid`, probe D), and the validator digest-checks bytes.

## Answers

**(1) Can an analysis number reach a structure-only record or the run record via the exemption? No.** Admission
needs exact set membership of the path string (`dry_run.py:318`, `dry_run.py:495-499`). Executed:
- Path L9 constructs / not in inventory / appended value: probe A refuses, at both writer and validator,
  `<inv>/0.731`, `<inv>.0.731`, `<inv>-0.731`, a sibling `0.731`, and a renamed `-0.731.txt` variant; the seat's
  `unlisted source name` subtest also refuses.
- Wrong window: seat subtest `another window's inventory name` refuses; inventories are keyed by pack and built
  only for an index entry that a `windows` row names by pack, plan id and harvest digest (`dry_run.py:358-367`).
  History-only rows (`sources/attempts/...`) refuse.
- Unauthenticated listing: harvest digest mismatch gives an empty inventory (seat tests); listing changed after
  write refuses (probe C); a listing that is consistently wrong on disk is admitted (finding 1).
- Symlink: symlinked `sources/SHA256SUMS` refused at step 0 with `archive_path_invalid` before any census write (probe D).
- No index: no exemption, record refused (probe E).

**(2) Authenticated by the index-pinned harvest digest, identical at write and validation?** Harvest outputs: yes,
both times. Listing: no, only self-consistency (finding 1). Identical: yes; probe F recomputes both inventories
on the same run (alpha 2368, beta 2370, gamma 2370 entries; number-like entries are exactly the injected names,
e.g. `21e2-delta2-final-head-opus.md`, `claude-help-2.1.260.txt`, `replay-branch-82622e70-summary.txt`,
gamma also `gamma-only-4158e658.md`) and asserts equality.

**(3) Other fields and roles keep the full guard? Yes.** `tests/b5_analysis/test_dry_run.py` is unchanged from
b13a510dc; `ReaderRecordGuardTests` (T19, includes `census_gamma {'path':'sources/1e-100.json'}`) passes:
`Ran 1 test ... OK`. The writer only blanks `path` of list rows in `census_*`; `sha256`, `check`, extra keys,
dict-shaped values, caller `raw`, and `attempt_`/`kept_` roles all refuse (seat test, 7 subcases, re-run OK).
Validator `path()` takes an inventory only for `input_census` rows (`dry_run.py:371`).

**(4) Regression tests fail at base and pass at head? Yes.**
```
# 49991c73a
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_census_path_token tests.b5_analysis.test_dry_run
Ran 61 tests in 308.412s
OK (skipped=3)
# b13a510dc worktree + new test module
Ran 6 tests in 34.516s
FAILED (failures=3, errors=10)
  FAIL test_P1_step0_admits_authenticated_inventory_names_with_number_like_tokens
  FAIL test_P2_validator_keeps_the_guard_outside_the_exact_window_inventory
  FAIL test_P2_validator_requires_the_index_pinned_harvest
  ERROR test_P1_run_record_validates_inventory_census_paths, test_P2_inventory_is_empty_unless_..., 8x writer subcases (API absent at base)
# probes at 49991c73a
Ran 6 tests in 66.736s
OK
```
The P1 failures are true counterfactuals (step 0 refuses at base); the writer/inventory errors are API absence.
