# RC-CMP-5 seat report

bridge-report/v1 · brief `main:docs/process_traces/2026-10-28-recompute-meter-fit/FIX-BRIEF-2.md` (d22bda7d2) ·
branch `lane/2026-10-27-recompute-comparator`, base `e5ccf720b`, fix commit `7955f57d8`. Synthetic data only. No real
block-5, block-6 or BYTES data was opened. Interpreter `/usr/bin/python3.13`. Cloud seat; the lead is session 015ASG1T.

## SUMMARY

**DONE: S1-S4 are met.** The fix removes the false-agreement class as a whole, not only the five round-2 instances.
All five instances now fail closed at `7955f57d8`. Every round-2 comparator probe is now a regression test that
fails at `e5ccf720b`. The round-1 probes were already tests (RC-CMP-3) and still pass.

- **S1, default deny for numbers.** A step-11 leaf is numeric-class if it is a number or a null, or if it was read
  from a NaN or Infinity token. The loader now records the leaf path of each such token in the
  `nonfinite_value_read_as_null` flag (`paths`).
  - An `uncovered:` rule matches only strings and booleans.
  - A numeric-class leaf has two ways to pass. It can bind to an agreeing compared row. Or it can be named by an
    `uncovered-by-name:` rule, which lists it. A registered null can also be named by the new
    `uncovered-null-by-name:` rule, which is also listed.
  - Any nonfinite value in a step-11 output refuses the run: exit 2, `refused=step11_nonfinite_value`.
  - The public line gains `step11_nonfinite=<count>`.
- **S2, independent binding.** A key is built only from three things: path groups, the identity fields of the
  enclosing containers, and list positions.
  - The identity fields are contrast, cell, pack, run, model, ratio component and label, and the leave-one-out
    block.
  - Attributes never route a key. These are a gate's `condition_family_id`, a resolution's `source_cell_ids` and a
    band's `pack`.
  - Arm gates and resolutions bind by their registered position (A, then B) to the recompute's arm: A is ALPHA's
    model and B is BETA's. Their printed `arm_id`, `condition_family_id` and source cell ids are compared exactly, as
    `routing_id` rows.
  - Every key that routes a binding has a `routing_id` row, which compares the key on L9's side with the key on the
    recompute's side. Coverage requires each such row to be AGREE (reason `route_disagrees` otherwise). An identity
    leaf that routed a binding that agrees is reported as `routing_id`.
  - The central band's window is now the one the recompute chose. Its pack is compared exactly, and a band on one
    side only is DISAGREE.
- **S3, one union and one key space.** `Comparison.pairs` is the only union. It takes the union of the keys and
  writes one `routing_id` row per key, so a key on one side only is DISAGREE `missing_or_null`.
  - Each L9 list is keyed through `keyed()`. Two L9 items under one key refuse the run with
    `item_key_duplicated:<collection>`.
  - A second row under one (family, key) refuses the run with `row_key_duplicated:<family>`.
  - Ratio rows have their own prefix, `ratio/`.
  - Two step-11 leaves at the same path that bind one row are reported as `duplicate_binding`.
  - An AST test checks every `compare_*` function. Each one may iterate only `pairs` or a constant expression, and only
    `compare_*` functions may build rows.
- **Suite:** `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s
  tests/independent_recompute -t .` gives `Ran 235 tests in 168.491s OK (skipped=18)`. Before this job it gave 205
  tests, OK (skipped=18).

## S1-S4

Probe commands are the reviews' own:
`PYTHONPATH=.:tests JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/<dir>/<probe>.py`.
The four review directories were extracted with `git archive origin/review/<branch> .codex-report/<dir> | tar x`.
They are untracked and not committed. At `e5ccf720b` both round-2 probes reproduce their reviews' `.out` files
byte for byte.

For the counterfactual, a detached worktree of `e5ccf720b` got this head's `tests/independent_recompute/`, and the
two new test modules were run there. Result: `Ran 30 tests … FAILED (failures=23, errors=3)`. 26 of the 27
comparator tests fail. The one that passes is `test_the_checker_catches_a_one_sided_loop`, which tests the AST
checker itself. The three meter-probe tests pass at both heads: those probes found no defect, and they are kept as
guards.

| # | Criterion | Status | Evidence (`7955f57d8`) | Counterfactual (`e5ccf720b`) |
|---|---|---|---|---|
| S1 | numbers denied by default; nonfinite step-11 values refuse | PASS | **Sol 1:** `new_nonfinite_leaf {} ['fill:campaigns/gamma/gross_energy_j'] None [{…'paths': ['campaigns/gamma/gross_energy_j']}] cli 2`. **Opus N1b:** `exit=2 stderr='refused=step11_nonfinite_value'`. N1c (Infinity as `j_per_token`) and N1d (NaN under an uncovered-by-name rule) also give `exit=2`. N1d shows `uncovered_numeric lists it: True`. Tests in `NumbersDeniedByDefaultTests` (5): NaN under the identity catch-all, Infinity `j_per_token`, NaN listed by name, a null that no `uncovered:` rule takes, and a registered null that is named and listed. | Probes gave `cli 0` and N1b/c/d `exit=0`. All 5 tests fail (4 F, 1 E). |
| S2 | structural keys; routing ids compared; arm gate binds to the recompute's arm; band window is the recompute's | PASS | **Sol 2:** `arm_wrong_id {} ['…/arm_gates/*/condition_family_id', '…/arm_gates/*/floor_gate_j'] cli 2`. **Opus N3a:** `{'rho': 2, 'routing_id': 1} [… central_band/lower, …/pack, …/upper]`, and N3b the same. Tests in `IndependentBindingTests` (8) and `CentralBandTests` (4). In a full v3 floor, a B gate printed with A's condition and value gives `{floor_gate_j: 1, routing_id: 1}` and exit 2. A wrong condition id on its own gives `{routing_id: 1}`. A resolution that copies the other arm gives `{floor_gate_j: 2, routing_id: 1}`. Reversed gates give `{floor_gate_j: 2, routing_id: 4}`. A contrast on L9's side only gives `route_disagrees`, although its `floor_abs_j` row is AGREE. `contrast_id` and band `pack` leaves report `routing_id`. | Probes gave `arm_wrong_id {} [] cli 0` and N3a/N3b `{} []`. All 12 tests fail. |
| S3 | one union helper; one-sided keys DISAGREE; unique keys; ratio prefix; AST test | PASS | **Sol 3:** `assist_recompute_only ({'count': 1, 'routing_id': 1}, […'l9': None, 'recompute': 3 … 'missing_or_null'…])`. **Opus N2:** `N2 duplicated row keys: []`. `N2a … n=9 … exit=2 … ('disclosure:block_lines/dominance_ratio/n', 'value_differs')`. `N2b … correct ratio n=7: exit=0`. Tests in `OneKeySpaceTests` (7) and `StructureTests` (3): contrast and cell strata unions; a second row under one key refuses; two verdict contrasts with one id refuse (`item_key_duplicated:contrast`); a duplicated fill contrast gives `duplicate_binding`; the loo_magnitude union; and the AST checks. | Probes gave `assist_recompute_only ({}, [])`, N2 `[('count', 'Qwen3-1.7B-4bit/decode/absolute/n')]`, N2a `exit=0` and N2b `exit=2`. 9 of 10 tests fail (7 F, 2 E); the checker's own guard passes. The AST test lists the old one-sided loops. |
| S4 | every probe is a regression test; suite; scope; independence | PASS | Round 2: `probe_new_paths` and `probe_delta` are ported in `test_structural_rules.py`. Opus `probe_meter_adversarial` is `test_review_probes_meter.py` (12 families, 580 streams, 0 ns, same envelope). Sol's `probe_meter_fit` (6,000 point sets) and `probe_meter_short` (150,000) are in the same file, with largest difference 0 at every origin. Round 1: the RC-CMP-3 tests (`test_review_fixes.py`, `test_meter_fit.py`, `test_auditfix.py` for the compressed plist) still pass. At the fixed head all ten probe scripts run and fail closed (`.codex-report/rc-cmp-*` outputs in the seat's scratch). `git diff --name-only e5ccf720b HEAD` lists only WRITE_SCOPE files. `grep -nE "joulewise\.(b5_analysis\|external)"` finds nothing in either script. | Round-2 comparator tests: above. Round-1 probes found their defects at `3bf93b25e` and were closed by RC-CMP-3, whose report records their counterfactual. At `e5ccf720b` they pass, as both round-2 reviews also found. |

## FILES CHANGED

- `scripts/compare_b5_recompute.py`:
  - `Comparison.add` checks the key space, and `Comparison.pairs` is the union helper with its routing rows.
  - `loads`/`scrub` record nonfinite paths, and `Custody.nonfinite` keeps them per file.
  - New helpers: `keyed` and `positions`, plus `sides`, which pairs two intervals' bounds.
  - Every `compare_*` function is rewritten onto `pairs`. The new `compare_arms` handles arm gates and resolutions.
  - Ratio rows move to `ratio/…`.
  - The loo_magnitude, assist-strata, sensitivity-window and NEG-8 window-line loops become unions.
  - `compare_machine_summary` takes the band's window from the recompute.
  - `leaves`/`binding`/`key_for` follow the S2 field rule. `coverage` applies S1 numeric-class (`admits`), the
    route check, `duplicate_binding` and `nonfinite`.
  - `main` refuses a nonfinite step-11 value.
  - `COVERAGE` changes:
    - arm and resolution rules by position, with id rules;
    - the `j_per_token` null rule becomes `uncovered-null-by-name:`;
    - ratio templates use `ratio/`;
    - a rule for `central_band/pack`.
- `tests/independent_recompute/test_structural_rules.py` (new, 27 tests) and `test_review_probes_meter.py` (new, 3
  tests).
- `test_comparator.py`: the fixture gains two shapes from L9's producer (`6af08b780`), which the S3 unions now
  require. These are the sensitivity record's refused p42 cells (`sensitivity.py:288-293`) and one `loo_magnitude` line per
  contrast (`disclosures.py:556-567`). A moved p42 status now fails 2 rows (extraction and sensitivity).
- `test_comparator_meter.py`: the member's window is made clean (no battery activity). The recompute then sets the
  band that L9's line prints. Before, the fixture printed a band from a window that both the recompute and L9's own
  rule (`disclosures.py:677`) call unclean. That is the N3a shape.
- `test_review_fixes.py`: expected counts now include the one-sided key's `routing_id` row. The NaN flag now carries
  `paths`. The L9-keys-only counterfactual now patches `Comparison.pairs`.
- `.codex-report/RC-CMP-5.md`: this report.

## DECISIONS I MADE

1. **What "compared exact against the recompute's value" means for an identity id.** Some ids are a line's own
   identity: `contrast_id`, `cell_id`, `pack`, `run_id`, `model`. For these, the `routing_id` row that `pairs` writes
   for the key is the comparison: L9's key against the recompute's. The contrast case shows why the check is not
   redundant. A contrast's `floor_abs_j` row is computed from the recompute's floor cells, so it agrees even for a
   contrast the recompute does not have. The route check now stops that leaf.
2. **The recompute's arms.** Arm A is the a1/a2 runs on ALPHA's model and arm B is BETA's. The condition id is
   `sw-<decode|prefill-p2048>-<a|b>-<model tag>`, the kept-unit tag rule at `independent_recompute_b5.py:1016-1018`.
   Gates and resolutions are compared from the claim verdict's floor, which the fill copies. They are compared only
   when the verdict prints `arm_gates`/`resolutions` (v3 floors). A fill gate with no verdict gate refuses
   (`no_row`), and this is how Sol's literal probe now refuses. A source cell id is compared through its derived
   (model, phase); the printed id is kept as `l9_raw`.
3. **The dominance-ratio label still comes from the line's text.** L9's line names R or R_cm only in its text
   (`disclosures.py:1146-1157`). I treat that word as the line's identity, not as an attribute. The new ratio prefix
   and `duplicate_binding` stop it from aliasing a floor row or a second line.
4. **Null is numeric-class, as the brief says.** The one null registered in the map (`j_per_token` for a J contrast)
   gets the new `uncovered-null-by-name:` rule, which is listed. That rule does not take a null read from a
   nonfinite token.
5. **The recompute's own side for four former one-sided loops:**
   - loo_magnitude: the PLAN 7.3 trigger, movement > ¼ × the contrast's `floor_gate_j`.
   - Sensitivity p42 cells: the recompute's `p42` entries.
   - Extraction p42: one row per pack from all of L9's p42 cells. Before, there was one row per cell, and none when
     L9 listed no p42 cell.
   - Projection refused p42: unchanged. It is compared only when L9 lists such a cell, through a helper.
6. **Where the refusals happen.** A nonfinite step-11 value refuses in `main`, as `step11_unmapped` does, so the
   restricted output keeps the full coverage report. Duplicate rows and duplicate L9 items raise `Refusal`, a
   structure fault.
7. **What the AST rule covers.** It applies to functions named `compare_*`. Helpers outside them may iterate, for
   example to key a list or derive a statistic. But they may not build rows, and a second test checks that.

## OPEN ISSUES

1. **More real shapes may now refuse.** Every new check fails closed, but each could refuse a sound real window.
   RC-CMP-4 runs at `e5ccf720b`, not at this head. The candidates:
   - a null under a former `uncovered:` rule;
   - a fill arm gate when the verdict has none;
   - a missing sensitivity p42 cell or `loo_magnitude` line;
   - a different trigger definition;
   - an extraction report with no p42 cell;
   - a repeated step-11 line.

   The full-size A6 comparison at `7955f57d8` would settle this from structure alone. Run it with the
   `coverage.unbound` reasons, `coverage.unmapped` and the `routing_id` failures from its restricted output.
2. **The ratio label is routed from the line's text** (decision 3). Removing that needs a field in L9's line, which is
   outside this repository's comparator.
3. **Over-refusal from RC-CMP-3 is unchanged here, by the brief:** equal member sets, and multi-source floor cells.
   A resolution with two source ids now gives a `routing_id` DISAGREE at position 1, where before it gave
   `key_unresolved`. It still fails closed.

## NEEDS_RULING

None.

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| CI-equivalent suite (`tests/independent_recompute`) | yes | no | no | 235 OK at `7955f57d8` |
| regression test with counterfactual | yes | no | no | 26/27 new comparator tests fail at `e5ccf720b` |
