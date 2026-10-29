# L9-PATHTOKEN-1 seat report

bridge-report/v1 · brief `main:docs/process_traces/2026-10-29-l9-census-path/BRIEF.md` (`82486bfc7`) · branch
`lane/2026-10-29-l9-census-path` cut at BASE_HEAD `b13a510dc`.

## SUMMARY

IN PROGRESS (milestone 1: fix and regression tests committed; wider short-module run pending).
Attempt A's step-0 refusal is reproduced on synthetic archives and repaired in the narrow form the brief asks for.
A census path that carries a number-like token is admitted only when it is an exact entry of its own analysed
window's authenticated archive inventory. That inventory is recomputed from disk by one helper,
`dry_run.archive_inventory`, at write time (step 0) and again in the run-record validator. Every other field and
every other path keeps the full `_FLOAT_TOKEN` guard.

Lead: session 015ASG1T only. No other session has messaged this seat.

## SEAT

- Claude cloud session (scheduled routine), 2026-10-29. Python 3.13 at `/usr/bin/python3.13`; no
  `/opt/homebrew` link (no test needed one). TMPDIR outside the checkout, no symlink, no float-like token.
- Clone unshallowed (`git fetch --unshallow`) so `b13a510dc` resolves.
- Synthetic data only. No real block-5/6/BYTES data was opened or searched for.

## P1-P4

| Item | Status | Evidence | Counterfactual |
|---|---|---|---|
| P1 diagnosis reproduced | MET | `test_census_path_token`: each synthetic archive's listing gets `sources/night-custody/results-clone/docs/process_traces/x/{replay-branch-82622e70-summary.txt, 21e2-delta2-final-head-opus.md, claude-help-2.1.260.txt}` (gamma also gets `gamma-only-4158e658.md`). | At `b13a510dc`: real `step_0` returns `tooling_refusal reader_record_not_structure_only`. The attempt-A-shaped run record (step 0 refused, later steps `not_run`) then fails `validate_dry_run_record` with `dry_run_record_invalid`. Dropping only the number-like inventory rows from that record makes the base validator pass, which locates the refusal at the `input_census` path check. |
| P2 narrow admission | MET | Writer: for `census_<pack>` only, a row's `path` is withheld from the scan only when it is in the inventory; `sha256`, `check`, any extra key, a dict-shaped value, a caller-supplied `raw`, and the `attempt_`/`kept_`/`tripwire_` roles are all scanned in full (7 refused subcases). Validator: refuses an unlisted name, another window's inventory name, a `sources/attempts/<plan>/` history-prefixed name, a record whose `sources/SHA256SUMS` row digest is not the bytes on disk, a non-index-pinned `harvest.json`, and an inventory name used as `release_difference.path`. The existing `ReaderRecordGuardTests` case `census_gamma {'path':'sources/1e-100.json'}` is unchanged and still refuses. | The same tests at base fail or error (no exemption, no `inventory` argument, no `archive_inventory`). |
| P3 no other change | MET | `git diff --name-only b13a510dc HEAD` lists only `joulewise/b5_analysis/dry_run.py`, `tests/b5_analysis/test_census_path_token.py` and this report. No arithmetic, step order or refusal class changed. Governed estimator files are untouched, so they are byte-identical. | - |
| P4 tests | PARTLY MET | `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_census_path_token tests.b5_analysis.test_dry_run`: Ran 61, OK (skipped=3; the full-size joined run is skipped and is the lead's laptop check). The wider short-module run is pending. | New tests at base: 3 failures and 10 errors (listed under P1/P2). |

## FILES CHANGED

- `joulewise/b5_analysis/dry_run.py`: new `archive_inventory()`; `RunState.write(..., inventory=)`; step 0 passes
  each window's inventory to its census write; validator `path()` takes the window inventory for `input_census` rows only.
- `tests/b5_analysis/test_census_path_token.py`: new (6 tests).
- `.codex-report/L9-PATHTOKEN-1.md`: this report.

## DECISIONS I MADE

1. **What the inventory is.** The index-pinned `harvest.json` `outputs` keys, every name in `sources/SHA256SUMS`
   as `sources/<name>`, and that listing's claim-runs mirror as `original/claim-runs/<name>`. The mirror uses the
   same prefix rule as `ArchiveHandle.compare_runs_root`. It is included because step 0 censuses those rows from the
   same listing, and on the real layout the claim-runs root may sit under `night-custody/`.
2. **How the listing is authenticated.** `harvest.json` does not pin `sources/SHA256SUMS` (it is read with no
   expected digest; source bytes are then checked against it). The helper takes the listing only if its digest equals
   the census's own `sources/SHA256SUMS` row. That row is the reader's digest at write time, and the record's row in
   the validator. The harvest record must match the index digest. Any mismatch, parse failure or unreadable file
   gives an empty inventory, and the full guard applies.
3. **Per window, analysed attempt only.** The validator builds an inventory only for an index entry that a
   `windows` row names by pack, plan id and harvest digest. A path is admitted only under its own `window`.
   History-only attempt rows (`sources/attempts/...`) get no exemption.
4. **Validator inputs.** As before, the validator reads the archive from disk through the index. Without an index
   (or with the tracked one), no inventory is built and no exemption applies.

## OPEN ISSUES

1. **Release mode, out of scope.** `release_difference` reports a changed census row by its path. If that path is a
   number-like inventory name, the release record's `release_difference.path` fails validation, and `run()` stops
   with `dry_run_record_invalid` instead of writing the step-11 `release_digest_differs_from_dry_run` record. That
   still fails closed, but without the closed record. A test pins the guard on that field, per P2. A ruling is needed
   if release should admit it.
2. **Other path-bearing fields.** Step output names (for example finalization's `gamma-pack/` copies of pack config
   files) keep the full guard. The synthetic packs have no number-like names there. If a real pack config file name
   had one, a later step would refuse in the same way. The lead's full-size laptop run and attempt B will show this.
3. `role_census_<pack>` custody documents have no float guard at the base and are unchanged.

## NEEDS_RULING

None blocking. Open issue 1 is offered for a ruling.
