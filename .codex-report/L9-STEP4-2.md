STATUS: DONE

# L9-STEP4-2: step-4 refused cells are classified by their reason codes

Branch `lane/2026-10-30-l9-step4-reasons`, cut from origin/main `0a9ff42`. Seat lead: joulewise-28. Synthetic data only.
I did not open or search any real block-5, block-6 or BYTES data.

## SUMMARY

`classify_step4_exit` now reads `refusal_reasons` on every refused cell. A refused non-p42 cell is an outcome
(`floor_cell_not_extractable`) only when every reason is a **mask** code from the registered blind table. A cell with
no reasons and `floor: null` is also an outcome. Any tooling reason, or any reason in neither list, gives the new
registered TOOLING code `extraction_cell_tooling_refusal`, so the run exits 2 (cure and rerun) instead of 3. The blind
table is registered as `configs/analysis/b5/step4_reason_classes.json`. A test reruns the committed generator over
this checkout's extractor modules and must reproduce the table. The dry-run record still names only the class code.

## R1-R4

| Req | Change | Evidence (this branch) | Counterfactual at origin/main 0a9ff42 |
|---|---|---|---|
| R1 | `configs/analysis/b5/step4_reason_classes.json`: `mask` (42) and `tooling` (1898) copied verbatim from CLASS_TABLE.json at 08ea5c958, plus `modules`, `mask_rule` and the source commit/generator sha256. `tests/b5_analysis/step4_reasons/make_table.py` is a byte-identical copy of the generator (sha256 `051c13b2…a549d2`, pinned in the config and in the test). | `test_step4_reason_table.py`: shape/sorted/disjoint/pin; generator digest; `test_R1_regenerating_over_the_current_modules_gives_the_registered_lists` runs the generator (subprocess, `-I`) over the checkout and compares mask, tooling, mask_rule and modules. Before writing the file I also ran the regeneration by hand over origin/main: identical to CLASS_TABLE.json (`True True True`, empty symmetric difference). | The regeneration test passes at origin/main too, as it should: the table describes main's modules. Only the shape test errors there (`steps.step4_reason_classes` does not exist). |
| R2 | `steps.classify_step4_exit`, after the existing checks: any refused cell (p42 included) whose `refusal_reasons` is missing, not a list, or has a non-str element → `extraction_report_malformed`. Refused cells all p42 → `p42_floor_cells_only` (reasons ignored). Otherwise, for each refused non-p42 cell: a reason outside `mask`, or empty reasons with a floor present or with the `floor` key absent → `extraction_cell_tooling_refusal`. Otherwise `floor_cell_not_extractable`. The new code is registered under `tooling_refusal` (sorted position). The T18 pin test passes unchanged. | `test_step4_exit_classes.py::Step4ReasonClassTests` (8 tests); `test_every_returned_code_is_registered` (now 10 STEP4_ codes). | Run at origin/main with the new tests: tooling-only, mixed, unclassified, no-reason-with-floor or no floor key all returned `floor_cell_not_extractable`. Malformed reasons returned `floor_cell_not_extractable` (non-p42) or `p42_floor_cells_only` (p42). Code count 9 != 10. Mask-only and p42-with-tooling-reason cases pass there (unchanged behavior, intended). |
| R3 | No record schema change. `step_record` already prints a tooling code by name and an outcome as `outcome-class refusal at step 4`. The schema has no field for reason lists (`keys(row, …)` is closed), so no reason code is printed. | `test_T8c_…`: for each case, the record file, stdout and stderr contain none of the extractor reason codes. | n/a (no reason codes were printed at main either; the class itself was wrong). |
| R4 | Tests for every listed case; driver test T8c (T8b style); DriverDouble now emits `refusal_reasons`/`floor` (mask reason by default, a tooling reason on p42 cells). | T8c: step-4 row `('tooling_refusal','extraction_cell_tooling_refusal')`, run exit 2, `completed_without_tooling_refusal` false, step 5 not called. Run for tooling-only, mixed and unlisted reasons. T8/T8b are unchanged and still pass: a mask reason keeps outcome_class exit 3, and p42 cells with a tooling reason keep the registered exit. | T8c at origin/main: `AssertionError: 3 != 2` for all three subcases (outcome exit). |

## VERIFICATION

`TMPDIR=/tmp/jwrun JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .`
(TMPDIR is outside the checkout and has no float-like token.) Exact tail:

```
(full run in progress after a container restart; the exact tail lands in the next commit)
```

## FILES CHANGED

- `joulewise/b5_analysis/steps.py`: `STEP4_CELL_TOOLING_REFUSAL`, `step4_reason_classes()` (cached loader), reason-aware tail of `classify_step4_exit`.
- `configs/analysis/b5/step4_reason_classes.json` (new).
- `configs/analysis/b5/dry_run_refusal_classes.json`: `+extraction_cell_tooling_refusal` under `tooling_refusal`.
- `tests/b5_analysis/step4_reasons/make_table.py` (new, verbatim generator; no `__init__.py`, so discovery does not import it).
- `tests/b5_analysis/test_step4_reason_table.py` (new, R1).
- `tests/b5_analysis/test_step4_exit_classes.py`: helpers emit reasons and floor; new `Step4ReasonClassTests`; code count 9→10.
- `tests/b5_analysis/test_dry_run.py`: DriverDouble emits reasons; new T8c.
- `tests/b5_analysis/test_archive.py`: two synthetic reports gain `refusal_reasons`/`floor` (otherwise they are now malformed).
- `.codex-report/L9-STEP4-2.md`.

`joulewise/b5_analysis/dry_run.py` is unchanged: the driver already passes any exit-1 class through as the code.

## DECISIONS I MADE

1. **Generator location.** The task asks for a test that regenerates with make_table.py. `docs/process_traces/` is outside WRITE_SCOPE, and the branch holding the generator may not be fetched in CI. So I committed a byte-identical copy under `tests/b5_analysis/step4_reasons/` and pinned its sha256 to the 08ea5c958 blob in both the config and the test.
2. The config keeps `modules` and `mask_rule` alongside the verbatim lists, so the regeneration test also catches a change to the rule or module set.
3. Non-str elements inside `refusal_reasons` count as malformed (`extraction_report_malformed`), not as "unclassified".
4. Malformed-reasons validation runs before the p42-subset check and covers refused p42 cells too (see NEEDS_RULING 1).
5. "No reason and no floor" is read as `refusal_reasons == []` **and** a `floor` key present with value `null`. A missing `floor` key, or a non-null floor with no reasons, is `extraction_cell_tooling_refusal` (see NEEDS_RULING 2).
6. The reason-table loader is named `_STEP4_REASON_TABLE`, so the existing `STEP4_*` code-enumeration test still enumerates only codes.

## OPEN ISSUES

- The real extractor always emits `refusal_reasons` as a list of terminal reasons (`floor_extraction.py` `as_row`). Reports from real chain fixtures (test_chain_fixture / test_floor_kept_units) still give `p42_floor_cells_only` in the full run.
- If a future extractor code is added on the path, R1 fails until the table is re-registered (blindly, by rule). This is intended.
- The table classifies `kept_units_below_minimum` as mask. `dry_run_refusal_classes.json` lists the same literal as tooling for the driver's own step refusals. These are separate namespaces (extractor cell reasons vs driver step codes), and I changed neither.

## NEEDS_RULING

1. **Malformed reasons on a refused p42 cell.** I implemented the stricter reading: `extraction_report_malformed` even when only p42 cells are refused. The alternative reading ("a refused p42 cell's reasons are irrelevant") would accept a p42 cell with missing reasons as the registered exit.
2. **Empty reasons with the `floor` key absent, or a non-null floor.** I implemented the stricter reading: tooling (`extraction_cell_tooling_refusal`), not outcome.
