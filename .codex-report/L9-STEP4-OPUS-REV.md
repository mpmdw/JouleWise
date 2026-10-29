VERDICT: ACCEPT_WITH_FIXES

# L9-STEP4-OPUS-REV: blocking delta review of `49991c73a..a2a0c1419`

Seat: Claude cloud routine, 2026-10-29, on `review/2026-10-29-l9-step4-opus-rev` (= `a2a0c1419` plus this report).
Python 3.13 (`/usr/bin/python3.13`), TMPDIR `/tmp/jwrevtmp`. Synthetic data only. I did not open or search for real
block-5, block-6 or BYTES data. The evidence scripts and their outputs are in `.codex-report/l9-step4-opus-rev/`.

The classifier is total and follows the ruling. The driver change does what it claims. There is one fix: the commit
moved the Mapping guards below the exit-0 return, so a malformed exit-0 report now passes step 4. One line restores
the old behaviour.

## Findings (ranked)

**F1 (LOW-MEDIUM; fix before merge): exit 0 lost its fail-closed shape guard.** `joulewise/b5_analysis/steps.py:45-46`.
At `49991c73a`, a report or spec that is not a Mapping returned `refused` before the exit-0 check, so the driver set
exit 2 and stopped at step 4. Now `exit_status == 0` returns `ok` before any Mapping check. As a result, the driver
branch `dry_run.py:798` (`classification=='refused' and exit_status==0`) can no longer fire. Seat report DECISION 4
("behaviour for exit 0 is unchanged") is therefore wrong for this case. The real extractor always writes a dict, and
step 3 parses the spec, so I see no real path that triggers it. Still, it is a fail-closed guard the diff removed
without saying so.
```
exit 0 None       | base: refused | head: ok
exit 0 []         | base: refused | head: ok
exit 0 spec=None  | base: refused | head: ok
driver, head: exit0_report_list  run=2 step4-alpha=(ok, None) step5_called=True later=['not_run','ok','unclassified_refusal']
driver, base: exit0_report_list  run=2 step4-alpha=(unclassified_refusal, ...) step5_called=False
```
Fix (`l9-step4-opus-rev/proposed_fix_F1.diff`, validated: probe gives step 4 `unclassified_refusal` and does not run
step 5; `test_step4_exit_classes` + `DriverAcceptanceTests` OK):
`return "ok" if isinstance(report, Mapping) and isinstance(spec, Mapping) else "refused"`. Add a test for exit 0 with
`None`/`[]` (`test_S3_other_exit_statuses_keep_their_handling` checks only a well-formed exit-0 report).

**F2 (LOW, test gap, logic predates this diff): two p42-identification mutants survive.** At `steps.py:67-68`,
C4 (drop the `kind in ("absolute","comparative")` filter) and C5 (match `"p42"` as a substring instead of a `-` token)
pass every test. Synthetic `SPEC` has only absolute/comparative cells and no family such as `p420`. Suggested fix: add
one spec cell of another kind with a p42 family and one `p420` family, both refused, and expect
`floor_cell_not_extractable`. This is not blocking.

**F3 (INFO, predates this diff, unchanged): exit 0 never inspects cells.** A report that exits 0 with
`extractable: false` on a target cell runs to completion (`exit0_target_refused run=0`, the same at base). The real
extractor returns 1 whenever any cell is falsy (`scripts/extract_detection_floors.py:269-287`), so only an inconsistent
extractor reaches this. I mention it only because question 3 asks about it.

Surviving mutants that I judge equivalent: D3 (`code=classification` also on `refused`) cannot change anything,
because the classifier never returns `refused` for an int exit 1. D5 (the p42 branch keeps the stderr token) is a
pre-existing line. The real extractor writes no `error:` line and no stdout on exit 1, so the token is None.

## Answers

**1. Total? Yes.** In 200,000 random synthetic inputs (`probe_totality.py`, seed 1), the classifier never raised.
Every result was in {ok, p42_floor_cells_only, refused} ∪ table codes. `refused` came back only for non-int statuses
or statuses other than 0 and 1. All 7 tooling codes and the outcome code were hit. An independent oracle for the
ruling agreed on all 22,316 well-formed, consistent cases (`failures: 0`). In the table, the 7 `extraction_*` codes are
under `tooling_refusal` and `floor_cell_not_extractable` is under `outcome_class`. Mutant T1, which moves the outcome
code out, is killed (9 failures). Precedence: a malformed report, then a membership refusal, then a malformed spec,
then duplicate ids, then a cell-set mismatch, then a non-bool extractable, then an empty refused set, then the subset
test. Every one of those checks reads structure only. The exception is the empty-set check, which the ruling
explicitly names as tooling. Exit 0 is total but not shape-checked (F1).

**2. Faithful to the ruling? Yes.** A non-empty refused set that is a subset of the p42 cells gives
`p42_floor_cells_only`. That covers a single p42 cell and the full p42 set. Mutants C1 (`==`) and C9 (`>=`) are
killed, and so is C2 (an empty set counted as a subset). A non-p42 refusal gives `floor_cell_not_extractable`, also
when it is mixed with p42 cells: unit test S2, and the driver case `target_and_p42` gives run 3 / `outcome_class`. The
p42 set is built from `spec["cells"]` only. That is `s.specs[pack]`, which `prepare_kept` (`dry_run.py:630-633`)
byte-checks against the archived sealed spec. Mutant C6 (p42 taken from the report) is killed.

**3. Driver: yes on every point.** In `probe_driver.py` (the real `d.run` with the synthetic `DriverDouble`; ALPHA's
report and exit are overridden), every exit-1 branch reaches the step record with its code:
`membership / report_list / report_null / cell_missing / dup_id / nonbool / nothing_refused` →
`tooling_refusal <code>`, run 2, only alpha recorded, steps 5-11 `not_run`. `target_only` and `target_and_p42` give
`outcome_class`, run 3, step 5 never invoked, steps 5-11 `not_run`. `p42_only` gives `ok` with
`registered_exit=p42_floor_cells_only`, beta runs, step 5 is invoked, run 0. No exit-1 branch can give `ok` with a
refused target cell. The only way to `ok` at exit 1 is a refused subset of the p42 cells. The validator
(`dry_run.py:408-410`) also refuses an `ok` exit-1 row without that registered exit. On exit 0, see F1 and F3.
Driver mutants D1 (pass-through removed), D2 (exit status ignored), D4 (no break) and D6 (outcome treated as p42) are
killed.

**4. Leakage: none beyond what the ruling allows.** An outcome row prints only `outcome-class refusal at step 4`. The
code `floor_cell_not_extractable` and the cell ids (`-target`, `-p42`) are absent from every probe record
(`assertNotIn` over all 12 cases). Tooling rows print only their structural code. The new information is the class
itself, which the ruling allows, plus the break after alpha, which was already there. `extraction_exit_without_refused_cell`
implies "nothing refused", but the ruling names that branch as tooling, and the real extractor cannot produce it (it
exits 1 only when something is refused or omitted). As before, the record lists the report's sha256 as an output.
That is unchanged and not invertible.

## Executed evidence

- `TMPDIR=/tmp/jwrevtmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_step4_exit_classes tests.b5_analysis.test_dry_run`
  → `Ran 69 tests in 365.178s  OK (skipped=3)`.
- `l9-step4-opus-rev/mutants.py` (18 mutants; step-4 class tests + `DriverAcceptanceTests` + T18) → 14 killed;
  survivors C4 and C5 (F2), D3 and D5 (equivalent). Output: `mutants.out`.
- `probe_totality.py` → `probe_totality.out`; `probe_driver.py` → `probe_driver_head.out`.
- Seat claims in `.codex-report/L9-STEP4-1.md`: S1-S4 confirmed. DECISION 4 is wrong for non-Mapping input (F1).
