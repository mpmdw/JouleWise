# RC-CMP-2 report

OUTPUT_PROTOCOL: bridge-report/v1. Seat RC-CMP-2, branch `lane/2026-10-27-recompute-comparator`, base `234fbb127`.
Brief: `docs/process_traces/2026-10-28-recompute-meter-fit/BRIEF.md` (main `9e985c59c`). Authority: RUN_STATE items
83 and 84. Synthetic data only; no real block-5, block-6 or BYTES archive, export or key directory was opened.

## SUMMARY

STATUS: DONE. The recompute's meter clock fit now implements the registered parser definition in its own code. The
adversarial jitter of `7e322b767` agrees: 0 ns at sample 1150 (the old bins: 1249 ns) and 0.0 J against the 1.24e-4 J
bar (the old bins: -0.020 J). Over 240 seeded jitter streams the recompute's per-sample host times are within 1 ns of
the parser's. The old binning fails 239 of the 240. The binding bar set is now `configs/analysis/b5/recompute_bars.json`.
It is the coded set of `7e322b76`, family by family, plus four meter families under the same rule, each with its
derivation. The comparator uses it by default. The comparator now compares the whole-machine meter line on a member
fixture with a raw meter stream, and planted faults in each meter family fail, with counterfactuals. No bar was
widened, and the sealed registration and the registered arithmetic are unchanged.

## ACCEPTANCE

| Item | Status | Evidence |
|---|---|---|
| M1 meter clock fit = parser definition, own code, no pipeline import | PASS | `scripts/independent_recompute_b5.py` `meter_clock_fit` (constants `FIT_RESPONSE_CAP` 63, `FIT_MAX_RTT_MS` 3.0, `FIT_MIN_POINTS` 20, `FIT_BIN_DEVICE_MS` 10000, `FIT_MIN_BINS` 4). The function takes polls in host receive order, with one point per poll that kept a sample (its newest sample against `rx`, the RTT in ms and `n`). Eligible polls have `n < 63` and RTT `< 3.0` ms; when fewer than 20 are eligible, every poll is fitted. Then: a first-pass centred least squares; `bins = max(4, int(span / 10000))` of width `(span + 1) / bins` from the first fit point; the lowest residual per bin, first one kept on ties; an envelope refit, falling back to the first pass when the envelope cannot define a line. `r_max_s` is the largest residual above the envelope over the fitted points, as the parser's `excess_latency_ms_max`. `grep -nE 'joulewise\.(external|b5_analysis)'` over both scripts matches nothing (also `test_meter_fit.test_recompute_imports_no_pipeline_module`). |
| M2 old test replaced; property test over 200+ seeds; counterfactual | PASS | `test_auditfix.test_adversarial_clock_fit_jitter_agrees_with_parser_within_coded_bar` replaces `test_different_clock_fit_bins_disclose_energy_difference_without_slack`. On the same jitter, with the stop placed between the old and parser placements of sample 1150, it gets no `meter_request_mismatch`, `recorded_comparison.matches`, equal `meter/n` and a difference of 0.0 J against a 0.000124 J bar. `test_meter_fit.test_host_times_equal_parser_within_1ns_over_seeded_jitter` covers 240 seeds. Each stream has its own clock drift (±80 ppm), 1 to 5 samples per poll and occasional 63-sample caps. A third of the streams have every RTT below 3 ms. A third mix in 30% of RTTs above 3 ms. A third have fewer than 20 eligible polls (80 streams use the fallback). Across all 240 the largest difference is 1 ns, from rounding. Counterfactuals: `test_counterfactual_old_clock_fit_bins_fail_the_coded_bar` puts the old fit back through `mock` and gets the `7e322b767` result (flag on `meter/energy_J` and `meter/n`, -0.02 J). `test_counterfactual_old_binning_fails_the_property` fails 239 of 240 seeds, including all 80 within-cap streams. |
| M3 release bar config; comparator default; S-13 stays in tests | PASS | `configs/analysis/b5/recompute_bars.json` (`bar_set` `b5_release_recompute_coded_7e322b76`). Every family of `tests/independent_recompute/bar_sets/recompute_coded_7e322b76.json` is copied with equal bars, plus `meter_j`, `meter_w`, `machine_j` (1e-6 relative, 1e-6 absolute) and `rho` (1e-6 absolute). Every family carries a `derivation`. `compare_b5_recompute.py`: `DEFAULT_BARS` is that file, `--bars` defaults to it and `run()` defaults to it. Tests in `test_comparator_meter.ReleaseBarsTests`: the release set equals the coded set plus the meter families; the CLI without `--bars` prints `bar_set=b5_release_recompute_coded_7e322b76`; `s13_block6.json` stays in `tests/…/bar_sets`. |
| M4 comparator covers the whole-machine meter line; planted faults with counterfactual | PASS | `compare_machine`. From the step-11 disclosure's `machine_member` lines it compares rho, dE_rail and dE_machine per member. From the harvest's withheld meter record (new `--harvest-meter PACK=PATH`, digest in the restricted output) it compares gross meter energy, meter delta and baseline W, meter `n` and `n_baseline`, `battery_term_available` (exact), the battery term and `n` when available, dE_machine, dE_rail, rho and the integer-ns window edges. All of these are checked against the recompute's request phase. A disclosed meter window with no record is DISAGREE. Coverage rules map the member lines' `rho`, `rail_j` and `machine_j`. Fixture: `test_auditfix.machine_archive`, a raw 50 Hz KM003C stream whose record is written by the parser. The recompute runs on the same archive. `test_comparator_meter.MeterLineTests` (10 tests): the baseline agrees with 0 unmapped leaves. Each planted fault (meter energy, baseline W, rho in the disclosure, rho on the recompute side, dE_machine, meter `n`) fails exactly its family and passes with `bar_for` set to infinity. A missing record disagrees. The S-13 set (no meter families) refuses a meter line with `bars_family_missing:rho`. Stubbing out `compare_machine` leaves the mapped rho leaf uncompared. |
| M5 suite passes; nothing outside WRITE_SCOPE | PASS | `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`: **165 tests OK, 18 skipped** (real-archive tests skipped in synthetic-only mode; 148 before this job, +17). `git diff --name-only 234fbb127` lists only WRITE_SCOPE paths (see FILES CHANGED). |

## FILES CHANGED

- `scripts/independent_recompute_b5.py`: `meter_clock_fit` and its constants; `MeterStream` sorts polls by `rx` and passes every poll's point to the fit.
- `scripts/compare_b5_recompute.py`: `METER` families (optional in a bar set, required once used); `battery_term` categorical; `compare_machine`, `load_meter_records`, `--harvest-meter`; `DEFAULT_BARS`; machine-member coverage rules.
- `configs/analysis/b5/recompute_bars.json` (new).
- `tests/independent_recompute/test_meter_fit.py` (new), `test_comparator_meter.py` (new).
- `tests/independent_recompute/test_auditfix.py`: the old fit-difference test is replaced by an agreement test and a counterfactual.
- `tests/independent_recompute/test_meter.py`: 19 polls now fit through the fallback (one poll does not fit); the 45 s span has 4 bins of 11250.25 ms, not 5.
- `tests/independent_recompute/test_round3.py`: bin-origin label.
- `tests/independent_recompute/test_comparator.py`: the no-meter baseline also asserts no meter family is counted.
- `.codex-report/RC-CMP-2.md`.

## DECISIONS I MADE

1. **Poll order and eligibility follow the parser.** Polls are sorted by `rx` before decoding, as `parse()` does. Negative RTTs are eligible, as in the parser, where the old code required `0 <= rx - tx`. The fit falls back to every poll below 20 eligible, where the old code flagged `meter_no_fit`. These are part of the registered definition, so the recompute now matches them.
2. **One recompute-only refusal kept.** A non-finite or non-positive final slope still gives `meter_no_fit`, which the parser does not check. It can only turn a comparison into a non-comparison, never into a false agreement. It is not reached on any test stream.
3. **The fit record's fields changed** (`points_used`, `filtered`, `bins`, `envelope_fallback`, the actual bin width, and `bin_origin` "device time of the first fit point"). These are disclosure fields, not compared values.
4. **The meter families are optional in a bar set and refuse when used.** This keeps block 6's S-13 file unchanged and still prevents a meter line from being compared without a bar fixed in advance.
5. **The source of gross meter energy.** L9's disclosure publishes only rho, dE_rail and dE_machine per member. Gross meter energy appears only in the harvest's withheld meter record, so the comparator reads that record (`--harvest-meter`) and records its SHA-256.
6. **The `machine_summary` order statistics are not compared separately** (median, minimum, maximum, q25, q75, spread and central band). They are mapped as uncovered, with the reason that they are order statistics of the member rho values compared individually.

## OPEN ISSUES

1. **Only the request phase is compared.** The recompute also computes gross meter energy for decode and prefill (the 03:26 amendment), but neither L9 nor the harvest writes a per-phase meter value, so those terms have nothing to be compared against.
2. **Who passes the harvest record at release.** The release comparison must pass `--harvest-meter` for each window whose disclosure has meter lines. Without it, the comparator reports DISAGREE.
3. **Rounding.** The largest host-time difference is 1 ns, from summation order in the least squares and `round()` at a half-nanosecond. It is within the M2 tolerance. No sample moved across a window edge on any test.
4. **Reviews.** The two executing reviews over RC-CMP-1 and RC-CMP-2 are the lead's to launch (gate policy rule 3). This seat did not launch them.
5. **Environment.** This cloud seat ran `/usr/bin/python3.13`. `/opt/homebrew/bin/python3.13` was not needed and was not linked.

## NEEDS_RULING

None.
