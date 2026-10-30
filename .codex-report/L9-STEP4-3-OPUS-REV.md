VERDICT: ACCEPT

# L9-STEP4-3-OPUS-REV: delta review of 8222d0e47..901956944 (merge ed577960d excluded)

Seat: Opus reviewer, one of two parallel blocking delta reviews (gate rule 3). Lead: joulewise-28. Branch
`review/2026-10-30-l9-step4-3-opus-rev` from 901956944, full (unshallowed) clone. Synthetic data only. I did not open
or search any real block-5, block-6 or BYTES data. Code under review: `b898fbbc2` and `64b7674d3` (the only commits in
the range touching `joulewise/`, `configs/` or `tests/`). Evidence is in `.codex-report/l9-step4-3-opus-rev/`:
`probe.py`/`probe.txt`, `mut.sh`/`mutants.txt`, `t4-leak-mutant.txt` and `full-run-tail.txt`.

The classifier implements the blind ruling exactly. No exit-1 report reaches `ok`, `p42_floor_cells_only` with a
refused non-p42 cell, or any `outcome_class` code. All 12 mutants are killed. The findings below concern the cure
route only, never a pass. Every affected code stops the run either way.

## Findings (most severe first)

**F1 (needs ruling, not blocking): the R3 list is narrower than plan §2.2 bullet 3, and the test's pin cannot tell the
difference.** The pin is `tests/b5_analysis/test_step4_reason_table.py:57-79`.
- Six codes are pinned to `MEMBER_RULE`, the plan sentence "If one fires on a kept unit … goes to R3"
  (`analysis_plan_block5.md:87-91`). The basis is that the window-evidence precheck forwards them onto kept units
  (`analysis_engine/inputs.py:4064-4070`).
- That precheck forwards all 31 `REDUCER_REASON_CODES` (`analysis_engine/claims.py:40-73`), not just these six. The
  other 25 stay tooling, for example `cooldown_cap_hit`, `thermal_pressure_elevated_in_window` and
  `negative_power_sample`. Five of them, which the bullet names literally, are also tooling:
  - `window_evidence_precheck_missing`
  - `paired_block_incomplete`
  - `campaign_cooldown_evidence_missing`
  - `idle_window_suspect`
  - the cooldown-cap same-slot exclusion, `cooldown_cap_hit` (`floor_extraction.py`, 3 sites)

  `fixed_n_plan_incomplete` is in neither list, so it classes as unlisted, which means tooling.
- The real selector is "blind MASK ∩ reducer codes" (`test_step4_reason_table.py:141-147`). That is the lead's ruling
  as written, and the implementer flagged the same point (report NEEDS_RULING 1).
- Ed should decide whether §2.2's member rule covers every forwarded member-level code. If it does, it is a two-place
  edit: `RULING` and the JSON. M10 shows the test forces the two to change together.

**F2 (low, R3 in the over-inclusive direction): three R3 codes also have producers that are not §2.2 disagreements.**
A defect at any of these sites would route to an Ed ruling instead of a code fix. It still stops the run.
- `instrument_calibration_stale` at `reduce.py:1505-1506`: returned on
  `BundleReadError/KeyError/TypeError/ValueError`, which are read or integrity failures.
- `calibration_acceptance_bound_stale` at `whole_window.py:347`: a session-level code unioned into every cell, not a
  member rule.
- `kept_units_below_minimum` at `floor_extraction.py:2515` and `:2974`: emitted whenever fewer than 2 members are
  admitted, so member-level tooling refusals upstream can surface as R3.

The R3 label is coarse, but nothing is lost: the lead reads the restricted report before ruling.

**F3 (informational, unchanged from L9-STEP4-2-OPUS-REV F4):** on exit 0, `classify_step4_exit` returns `ok` whatever
the cells contain (`steps.py:58-59`; probe column `exit0`). This is safe only because
`scripts/extract_detection_floors.py:269-288` returns 1 whenever any cell is refused or any member is omitted.

**F4 (nit):** `joulewise/b5_analysis/disclosures.py:25` imports `classify_step4_exit` and never uses it. This predates
the range.

## Answers

**(1) Is there any path from a refused non-p42 cell to `ok`, `p42_floor_cells_only` or an outcome code?** No, on
exit 1. `probe.py` runs 34 adversarial reports (`probe.txt`). The exit-1 codes seen are
`extraction_cell_r3_refusal`, `extraction_cell_tooling_refusal`, `extraction_report_malformed` and
`p42_floor_cells_only`. Their intersection with `outcome_class` (now only `dominance_ratio_zero_denominator`) is `[]`.

`p42_floor_cells_only` appears only when every refused cell is p42, whatever reasons those cells carry, R3 or empty
included. An empty-reason non-p42 cell is malformed even beside an R3 cell or a p42 cell. Upper-case or
whitespace-suffixed R3 codes are tooling. Malformed reason containers give malformed.

In the driver (`dry_run.py:796-800`), every non-p42 classification on exit 1 becomes the record code, and the run is
recorded as `tooling_refusal`. T8/T8b/T8c pass.

Mutants (`mutants.txt`) run against the classifier tests, the table tests and `DriverAcceptanceTests`. The baseline
is OK and every mutant is killed:

| Mutant | Failures |
|---|---|
| M1 empty reasons not malformed | 4 |
| M2 R3 needs every reason | 6 |
| M3 tooling wins | 6 |
| M4 R3 read on p42 cells | 1 |
| M5 R3 returns the old outcome code | 16 |
| M6 p42 counted as target | 12 |
| M7 empty R3 set | 17 |
| M8 first target only | 1 |
| M9 JSON R3 drops `instrument_calibration_stale` | 4 |
| M10 JSON R3 gains `window_evidence_precheck_missing` | 3 |
| M11 `extraction_cell_r3_refusal` registered as `outcome_class` | 1 |
| M12 driver records R3 as the p42 exit | 2 |

**(2) R3 precedence and the R3 list.** Precedence is correct (M2, M3, M8): any R3 code on any refused non-p42 cell
wins. R3 codes on p42 cells are ignored (M4).

Each of the eight codes is present at the producer site the test pins:
- `floor_extraction.py:2461,2512,2515`
- `reduce.py:981,988,998,1505/1524,2358/2361`
- `calibration_bracketing.py:2204…`

`test_R3_each_code…` passes. The plan sentences are at `analysis_plan_block5.md:84-85` (the minimum rule) and
`:87-91` (the member rule). All eight are in the blind MASK.

On whether any code is wrongly in or out of R3, see F1 (out of R3 under a literal reading of §2.2) and F2 (in R3 with
non-§2.2 producers). Both errors are stop-side.

**(3) Is the generator still byte-identical, and does the regeneration test cover generator + ruling?** Yes.
- `make_table.py` sha256 is `051c13b2…a549d2`, equal to `08ea5c958:docs/process_traces/2026-10-30-step4-reasons/make_table.py`.
  The range has no diff under `tests/b5_analysis/step4_reasons`.
- A fresh generator run gives `mask` and `tooling` equal to the registered file and to the blind `CLASS_TABLE.json`.
- `test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file` compares
  `HEADER + generator output + RULING` with the file bytes. M9 and M10 (JSON edited, test `RULING` not) are killed.

**(4) r14, T4 and the S6 disposition.**
- r14 (`test_floor_kept_units.py:961-992`) now runs three real-composition subcases: p42-only, the tooling seam and an
  R3 seam. It addresses my prior F1.
- T4 (`test_dry_run.py:518-529`) asserts that the sentinel `Q7331Z` is absent and that `7331` is absent once 64-hex
  digests are stripped, as T3 does. `Q7331Z` cannot occur in hex, so stripping digests cannot hide a real leak. My
  leak mutant copies the escaped traceback's last line to stderr in `StepRunner.run` and is killed:
  `AssertionError: 'Q7331Z' unexpectedly found` (`t4-leak-mutant.txt`).
- S6 (`test_mint_kept_units` ERROR): the implementer's disposition, ENOSPC in my earlier container caused by the
  parallel mutant worktrees, matches my L9-STEP4-2 answer 4. This time I ran the mutants in one worktree on an ample
  disk, and the full run below shows the result.

**(5) Full run.** The command was
`TMPDIR=/tmp/jwrevtmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .`
from the checkout at 901956944, with a full clone. TMPDIR is outside the checkout and has no float-like token. Exact
tail (`full-run-tail.txt`):

```
TAIL_PLACEHOLDER
```
