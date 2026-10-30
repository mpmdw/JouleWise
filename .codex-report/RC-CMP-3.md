# RC-CMP-3 seat report

bridge-report/v1 · brief `main:docs/process_traces/2026-10-28-recompute-meter-fit/FIX-BRIEF.md` (685b48a68) ·
branch `lane/2026-10-27-recompute-comparator`, base 3bf93b25e, fix commit 048085b3e. Synthetic data only. No real
block-5, block-6 or BYTES data was opened. Interpreter `/usr/bin/python3.13` (3.13.17).

## SUMMARY

**DONE: X1-X9 are met.** Every probe in both reviews now fails at the fixed head, by refusal or by DISAGREE. Each
one is a regression test that fails at 3bf93b25e. Two items are for the lead (OPEN ISSUES 1-2): on real-shape data
the comparator now fails closed, and only a rerun of the full-size A6 comparison can show it does not over-refuse.

- **Coverage (X1, X6).** A mapped step-11 leaf names the row it copies, as (family, key). The key is built from the
  leaf's path and the ids around it: contrast_id, pack, cell_id, run_id, the line, the LOO block and the floor source
  cell. The leaf is covered only if that row exists, its L9 value equals the leaf in type and value, and the row is
  AGREE. An `uncovered:` rule never takes a number. A numeric leaf is left uncovered only by an `uncovered-by-name:`
  rule, and every such leaf is listed in `coverage.uncovered_numeric`; stdout gives their count.
- **Machine summary (X2).** The median, minimum, maximum, q25, q75 and spread, and the central band's bounds, are
  re-derived from the recompute's member rho. They use the parser's percentile and PLAN 8.2's plausible-member
  rule, and are compared under the rho bar.
- **Union (X3).** Every family compares the union of L9's items and the recompute's: runs, floor cells, aggregate
  cells, ratios, contrasts, reported cells, sensitivity rows, disclosure lines, the NEG-8 lines and meter members.
  An item on one side only is DISAGREE `missing_or_null`.
- **Meter fit (X4).** The fit now works in the parser's coordinates and with its sums. Over 1,041 streams it gives
  **0 ns** difference from the parser, with identical envelope points. The streams: seeded jitter at origins 1e12,
  1e15, 4e15 and 1e16 ns, the Opus probe's 800 planted near-ties, and Sol's stream. The old fit fails 240 of them.
- **X5, X7, X8.** Per-key overrides are validated like family bars. NaN and Infinity become null with a structure
  flag, and the restricted output is always written. `exact()` compares type and value. Window edges follow the
  7e322b76 rule. MeterStream follows the parser on header status and batch decoding.
- **Suite:** `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s
  tests/independent_recompute -t .` gives `Ran 205 tests in 165.008s OK (skipped=18)`. Before this job: 165 tests.

## X1-X9

Probe outputs at the fixed head come from a detached worktree of 048085b3e with the reviewers'
`.codex-report/rc-cmp-*-rev/` directories copied in, untracked. Commands as in the reviews:
`TMPDIR=… PYTHONPATH=.:tests python3.13 .codex-report/<dir>/<probe>.py`. The counterfactual is the new test files
run against the 3bf93b25e scripts and config, in a worktree with only `tests/independent_recompute/` replaced:
`Ran 43 tests … FAILED (failures=31, errors=12)`. 36 of the 43 test methods fail there. The 7 that pass are
guards, not probes: a valid override loads, the shipped-map baseline is clean, words stay uncovered under
catch-alls, controller-stamp edges are exact, a zero-count batch is skipped, unselected members are not keys, and
there is no pipeline import.

| # | Criterion | Status | Evidence (fixed head) | Counterfactual (3bf93b25e) |
|---|---|---|---|---|
| X1 | key-bound step-11 coverage | PASS | Opus: `P1b … exit0=False … unmapped=['fill:gamma/contrasts/*/estimate']`, the same for P2, and `P3 … unmapped=['fill:gamma/contrasts/*/claim_evaluation/outcome']`. Sol: `wrong_fill_estimate {} ['fill:gamma/contrasts/*/estimate']`, `wrong_fill_cli 2 stderr= refused=step11_unmapped_fill`. Tests `KeyBoundCoverageTests` (8): swap, cross-field, CI-bound copy, L1/null, raw direction, int vs float, a DISAGREE row, no row. Each gives its reason in `coverage.unbound` (`value_differs`, `row_disagrees`, `no_row`, `key_unresolved`). | Probes: `P1b/P2/P3 exit0=True`, `wrong_fill_cli 0`. Tests fail. In-test counterfactual: with `same` made always true, the swap is coverage. |
| X2 | machine order statistics and band compared | PASS | Sol: `wrong_machine_median {'rho': 1} ['disclosure:window_lines/alpha/machine_summary/median']`, `wrong_machine_median_cli 2`. `MachineSummaryTests`: every statistic and the band bound give `{rho: 1}` at +1e-5. The percentile equals `km003c_parse.percentile`. | `wrong_machine_median {} [] uncovered:…`, `_cli 0`. Tests fail. In-test: with `compare_machine_summary` removed and the old uncovered rule, the moved median passes. |
| X3 | union of keys; meter members equal sets | PASS | Opus P4 (`contrast_j: 8`, …), P5 `{'run_phase_energy_j': 3}`, P6 `{'floor_j': 24, 'count': 4}`, P7 `REFUSED bars_family_missing:rho` (the coded test bar set has no meter bars; under the release bars `test_meter_line_absent_from_l9_disclosure_p7` gives rho and machine_j DISAGREE). Sol: `missing_l9_run_output {'run_phase_energy_j': 3}`, `missing_l9_run_cli 1`, `extra_recompute_run {'run_phase_energy_j': 3}`, `missing_harvest_member {…'meter_j': 2…}`, `missing_harvest_member_cli 2`, `missing_harvest_machine {…'meter_j': 2…'battery_term': 1}`. | Probes all exit0/`{}`. Tests fail. In-test: with the union reduced to L9's keys, P5 passes. |
| X4 | meter fit in parser coordinates; ≤1 ns; same envelope | PASS | Sol `probe_meter_stream`: `differences_ns= [0, 0, 0]`. Sol `probe_meter_fit`: `largest 0`. `probe_meter_short`: `base_max … 0` at 1e15, 1e16 and 1e17. Opus `probe_meter_fit`: `A … max|host diff|=0 ns` at 0, 1e15 and 4e15; `B planted near-ties: 0 streams`. Test `test_host_times_and_envelope_equal_parser_at_long_host_origins`: 1,041 streams, envelope offsets equal the parser's second `_linear_fit` call. `meter_fit_property` max difference 0 ns. | `test_counterfactual_absolute_coordinates_fail_at_long_origins`: `{"failing": 240, "failing_near_ties": 211, "streams": 1041}`, including Sol's stream and no 1e12 near-tie. At base the new test errors. |
| X5 | per-key overrides validated | PASS | Opus P8 and P8b `REFUSED bars_invalid:contrast_j`. Sol `infinite_override`: `load_bars` raises `Refusal: bars_invalid:contrast_j`, so the probe stops at that line with that traceback. A copy with only that call guarded prints `infinite_override REFUSED bars_invalid:contrast_j` and the rest of the probe. `BarOverrideTests` covers inf, −9, a negative relative, 2.0 decimals, no bar, a bad regex and no match. | `P8/P8b exit0=True`, `infinite_override {} AGREE inf`. 6 of 7 subtests fail (all but the override without `match`, which base already refused). |
| X6 | catch-alls non-numeric; named numerics listed | PASS | Opus P12: `unmapped=['disclosure:window_lines/alpha/machine_member/meter_energy_j', '…/values/rho', 'fill:campaigns/gamma/gross_energy_j', 'fill:characterization/delta_j']`. `CatchAllTests` (3), including `uncovered_numeric` listing `…/magnitude_per_token/denominator`. | P12 reported the four as uncovered. Tests fail. In-test: letting `uncovered:` take numbers swallows them. |
| X7 | non-finite → null + flag; output always written | PASS | Opus `probe_streams`: `restricted written for NaN case: True`. `NonFiniteTests`: `structure_flags=[{"code": "nonfinite_value_read_as_null", "count": 1, "source": "l9:outputs/…-claim-verdicts.json"}]`; that row is `l9: null, DISAGREE, missing_or_null`. A refusal writes `{"refused": "l9_record_unreadable"}`. | `error=internal ValueError`, no output written. Tests error. |
| X8 | window edges, `exact()` type, MeterStream | PASS | P9 `fails={'outcome_word': 2}`. `EdgeTests`: controller edges are exact (+1 ns gives `{count: 1}`). A legacy `wall_anchor` edge agrees at 900 ns and gives `{window_edge_s: 1}` at 1,100 ns. `MeterStreamParserTests`: status `stopped` gives no stream (`meter_stream_not_streaming`); a header without status streams; count mismatches decode as the parser does (90 samples, equal times); an undecodable payload gives no samples on either side. | P9 `exit0=True`. The legacy-edge, status, count-mismatch and undecodable tests fail. |
| X9 | probes are regression tests; suite; scope; independence | PASS | `tests/independent_recompute/test_review_fixes.py` (46 tests) and the new `test_meter_fit.py` tests. The suite passes (205). `git diff --name-only 3bf93b25e HEAD` lists only WRITE_SCOPE files. `grep -nE "joulewise\.(b5_analysis\|external)"` over both scripts finds nothing. | See the counterfactual run above. |

## FILES CHANGED

- `scripts/compare_b5_recompute.py`: X1-X3 and X5-X8, as above. New `loads`, `items`, `union`, `same`,
  `bar_spec_valid`, `compare_machine_summary`, `percentile`, `machine_summary` and `binding`/`key_for`, plus a
  rewritten `coverage`, `leaves` and `COVERAGE`. Rows added where a printed leaf copies a value nothing compared
  yet:
  - each contrast's `floor_abs_j` and `floor_cmp_j`, primary and sensitivity;
  - the sensitivity record's T, attained sequence, per-window b_op and b_sens, and floor-cell allowance;
  - the battery-assist "without" n_r/n_b, and the contrast assist members;
  - the LOO-magnitude movement.
- `scripts/independent_recompute_b5.py`: `parser_line` and `meter_clock_fit` in parser coordinates (X4), with the
  fit's `envelope_offsets_ms`. MeterStream follows the parser on header status and decoding (X8, new structure-free
  flag `meter_stream_not_streaming`). Member detail gains `selected`: a kept run, the runs L9 re-reduces.
- `configs/analysis/b5/recompute_bars.json`: new meter-only family `window_edge_s` (1e-6 s absolute, 7e322b76's
  legacy edge rule). No existing bar changed.
- `tests/independent_recompute/test_review_fixes.py` (new), `test_meter_fit.py` (X4 tests and counterfactual) and
  `meter_streams/sol-long-origin-three-polls.jsonl` (Sol's stream, verbatim).
- `test_comparator.py` and `test_comparator_meter.py`: the fixtures gain what the union now requires (both models'
  aggregate cells, the sensitivity windows, `loo_counts` lines, `selected`, one-member meter sets, a central band),
  key-bound test rules, and line-named paths. The planted counts follow from the new rows: a moved b_op now fails 2
  rows, a moved recompute rho fails 9.
- `.codex-report/RC-CMP-3.md`: this report.

## DECISIONS I MADE

1. **Paths name the line.** A disclosure line item's path segment is its `line` word, for example
   `window_lines/alpha/machine_member/rho`. Other list items stay `*`. Rules then name a line's fields directly.
2. **Every `uncovered:` rule is non-numeric, not just the catch-alls.** This is stricter than X6. Numeric leaves
   that stay uncovered are named field by field, or by named subtree, under `uncovered-by-name:`. Examples: hazard
   `measurements/…`, NEG-8 `values_j/…` internals, the load-correlated line's `values/…`, and attempt numbers.
3. **Recompute item keys.** A recompute item counts as a key when it is a dict whose status is absent or
   `computed`; p42 cells are excluded (registered exit). A member is a run key when `selected` is true. A member
   detail without the field counts as selected, so an older output fails closed.
4. **Printed direction.** The direction row keeps L9's raw word (`l9_raw`, null for unsupported). Coverage checks
   the printed null against it, not against the compared word `none`.
5. **Central band.** The band's window is taken from L9's `central_band.pack`, as identity. Its bounds are
   re-derived from that window's plausible members. A band on the recompute's side only is DISAGREE. Which window is
   "clean" is not re-derived.
6. **Window edges.** The edge rule follows the recompute's `window_basis`, as 7e322b76 did. A legacy edge is
   compared in seconds under the new config family `window_edge_s`, so no bar is coded in the comparator.
7. **Undecodable meter payload.** A payload that is bad hex or not whole samples makes the parser raise. The
   recompute now drops the whole stream (no samples) rather than the one batch.
8. **Exit code.** A leaf bound to a DISAGREE row refuses (exit 2), not exit 1. The brief's covered-only-if-AGREE
   puts it under coverage.

## OPEN ISSUES

1. **Real-shape coverage is not proven here.** The A6 full-size L9 dry run (about 9.5 h, L9 worktree harness)
   could not be rerun in this seat. The new map was checked against a scratch census: synthetic records with every
   line type and field the L9-2 producers (6af08b780 `disclosures.py`, `results_fill_adapter.py`) write. 200 leaves
   bound, 66 named numerics, and no unmapped leaf or unresolved key. A field the producers write that I did not
   read refuses the run (fail-closed). Ask: rerun A6 against 048085b3e before release.
2. **The equal-member-set rule can over-refuse.** The recompute's `whole_machine` members are every collected roster
   member with metadata. L9's are `withheld/meter.json`'s. If a real harvest record omits collected members, X3's
   equal-set rule gives DISAGREE. The test fixture had to restrict the recompute side to the record's one member.
   The full-size run will show which case holds.
3. **Some numeric leaves are named, not compared.** These are named on purpose, not compared:
   - the load-correlated sensitivity lines (the recompute has `load_sensitivity`, but its minimum-5 handling differs);
   - SE_repeat, SE_metrology, the repeat-point interval and variance contributions;
   - battery discharged energy;
   - floor-cell kept counts;
   - planned_n and observed_complete_n.

   All are listed per run in `coverage.uncovered_numeric`, for the post-release reader (RC-CMP-1 NEEDS_RULING 3).
4. **Bindings that rest on reading the producers.** Some leaves are bound on the reading that L9 prints the same
   float its source compared. If not, they refuse visibly:
   - `contrast_interval/rounded_t` → `t_critical`;
   - `estimator/raw_p` → multiplicity `raw_p`;
   - `sampling/kept_n` → n;
   - the arm-gate floor → the aggregate cell by model substring.
5. **Probe notes.** Opus `probe_streams` exits 2 on the comparator because its fixture's `note` leaf is not in the
   shipped map; the probe pops it only in `probe_comparator`. The decimal tokens it reports (`7e6`, `7e322`) are
   inside a sha256 and the bar-set name. Sol `probe_comparator` stops at its `infinite_override` line (X5).

## NEEDS_RULING

None.
