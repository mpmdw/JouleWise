VERDICT: ACCEPT_WITH_FIXES

# L9-STEP4-3 delta review, second family (Fable), seat L9-STEP4-3-FABLE-REV

Reviewed `8222d0e47..901956944` on `lane/2026-10-30-l9-step4-reasons` without the `origin/main` merge `ed577960d`
(lane commits `64b7674d3`, `b898fbbc2` code, `901956944` report, read as claims) from branch
`review/2026-10-30-l9-step4-3-fable-rev`. Synthetic data only; I did not open or search any real block-5, block-6 or
BYTES data. Evidence files: `.codex-report/l9-step4-3-fable-rev/`.

The code implements the recorded ruling exactly and fails closed: no step-4 exit-1 report with a refused non-p42 cell
can reach `ok`, the p42 exit or an outcome class any more. The one fix is to the ruling's `r3` list, not the
classifier: three member-level codes that plan section 2.2 names literally and routes to R3 are reachable at step 4 and
are classed tooling, which is the cure-route error the R3 split exists to prevent.

## Findings (ranked)

**F1 (fix). The `r3` list omits three plan-named member-level codes that reach a step-4 cell.**
Plan 2.2, third bullet, names `window_evidence_precheck_missing`, `campaign_cooldown_evidence_missing` and
`idle_window_suspect` literally (with `paired_block_incomplete`, `fixed_n_plan_incomplete` and the same-slot cooldown-cap
exclusion) and says: "If one fires on a kept unit, the registration's member rules and the code disagree: the analysis
stops and the step goes to R3." That is the same sentence the lane pins as `MEMBER_RULE` for its six forwarded reducer
codes (`tests/b5_analysis/test_step4_reason_table.py:57`). The three codes are emitted by the window-evidence precheck
(`joulewise/analysis_engine/inputs.py:4062-4079`, `:4101`, `:4105`) and the extractor extends every member's reasons with
the precheck's reasons, filtering only `cooldown_cap_hit` (`joulewise/floor_extraction.py:2237-2245`). Executed
(`classifier_counterfactuals.txt`): each on a refused target gives `extraction_cell_tooling_refusal`, recorded
`(tooling_refusal, extraction_cell_tooling_refusal)`; all three are in the blind `tooling` list and none is in `r3`.
r14's second subcase pins the tooling answer for `window_evidence_precheck_missing`
(`tests/b5_analysis/test_floor_kept_units.py:968`). Both classes are stops, so nothing passes; but under RUN_STATE item
132's condition a tooling code licenses a code fix and rerun, where plan 2.2 requires Ed's ruling. The lane reports this
as NEEDS_RULING 1 and implemented the eight-code ruling as written (RUN_STATE item 138), so the amendment is the lead's
to make. Fix: add the three codes to `RULING['r3']` and the JSON (the regeneration test forces both), pin them in
`R3_PINS` to `inputs.py` and `MEMBER_RULE`, relax `test_R3_list…drawn_from_the_blind_mask` (they are blind-tooling
codes, so `r3 <= mask` no longer holds) and the `FORWARDED_PRECHECK == 6` count, and flip r14's second expectation to
`extraction_cell_r3_refusal`. `paired_block_incomplete` and `fixed_n_plan_incomplete` are claim-gate codes
(`joulewise/analysis_engine/__init__.py:562,778`) that never enter an extractor cell, so listing them is optional.

**F2 (note, outside the delta). The cooldown-cap case of the same plan sentence stops by another route.** On a kept
member, `_stop_kept_member_exclusion` (`joulewise/floor_extraction.py:2399-2404`) calls the extractor's `stop`
(`:3210-3211`), which raises `AnalysisRefusal("member_code_on_kept_unit")` (`joulewise/b5_analysis/kept_units.py:184`).
The extractor exits 2 and the driver records the registered tooling code `member_code_on_kept_unit`. It is a plan-2.2
R3 case recorded under the code-defect class. Not changed by this delta; worth a line in the ruling.

**F3 (note, pre-existing). The classifier trusts exit 0.** `classify_step4_exit(0, report, spec)` returns `ok` without
reading the cells (`joulewise/b5_analysis/steps.py:57-58`); executed with a refused target: `ok`. No path today: the
extractor returns 1 whenever any cell is refused or any member omitted (`scripts/extract_detection_floors.py:268-287`),
and the driver only turns exit 0 into 2 when the report or spec is not a mapping (`dry_run.py:798`). Same at `8222d0e47`.

**F4 (note). The report's S-VERIFY tails are "(pending)" at `901956944`.** Answer 5 below supplies the tail from this
container at the same head.

## Answers

**1. Faithful to the recorded ruling; the ruling's R3 list is not exactly plan 2.2's.** The code matches items
133/138 line for line (`steps.py:95-110`): p42-only is the registered exit whatever the reasons (F6 of my L9-STEP4-2
review, pinned by `test_R2_p42_cell_reasons_are_irrelevant…`); a refused non-p42 cell with no reasons is
`extraction_report_malformed`; any `r3` code on any refused non-p42 cell is `extraction_cell_r3_refusal`; everything
else, including blind-mask codes outside `r3`, is `extraction_cell_tooling_refusal`. The eight `r3` codes are each
pinned to an emission statement that exists in the named producer module and to a plan 2.2 sentence
(`test_R3_each_code_is_pinned…`, passes). Each is a code the plan routes to R3 on a kept unit: the two minimum-rule
codes and the six reducer codes the precheck forwards (my F1/F2). `anchor_energy_envelope_exceeds_quarter_metric` is
R3 as ruled (F5 was a note, stop-side either way). Nothing in `r3` is a tooling case. The reverse holds for the three
F1 codes: plan-R3 cases classed tooling. No R3 code is read on a p42 cell (executed: target tooling + p42 R3 ->
tooling).

**2. No path from a refused non-p42 cell to `ok`, the p42 exit or an outcome code.** `ok` needs exit 0 (F3) and the
extractor exits 1 on any refused cell. The p42 exit needs `targets` empty (`steps.py:98-100`). The outcome registry is
now `['dominance_ratio_zero_denominator']` only (`dry_run_refusal_classes.json`), the classifier returns neither it nor
the removed `floor_cell_not_extractable` (no reference left in `joulewise/` or `scripts/`), and `step_record` maps all
three stop codes to `tooling_refusal`, so `completed_without_tooling_refusal` is false and the run exits 2
(`dry_run.py:1342`); an unregistered code would be `unclassified_refusal`, also a stop. Executed table in
`classifier_counterfactuals.txt`; T8/T8b/T8c pass.

**3. Generator byte-identical; the test guards generator and ruling.** `tests/b5_analysis/step4_reasons/make_table.py`
sha256 `051c13b2…a549d2` equals `docs/process_traces/2026-10-30-step4-reasons/make_table.py` at `08ea5c958`; the
range has no diff under `step4_reasons/`. `test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file`
compares the table to generator output plus `RULING` and the raw bytes to `json.dumps(..., indent=1)+'\n'`. In a
scratch copy (`regen_mutation_probe.txt`): two literals appended to `floor_extraction.py` (one mask-shaped, one tooling)
-> that test FAILS; a ninth `r3` code added to the JSON only -> that test and `test_R3_list…` FAIL; clean copy 7 OK.
Classifier mutants against the step-4 tests (`classifier_mutants.txt`, 58 tests): R3 branch removed, 15 failures;
`r3` read on p42 cells too, 1; empty reasons not malformed, 4; one `r3` code dropped at runtime, 1. Limit as before:
a literal in a module outside the generator's eleven is unseen, which the classifier treats as tooling (fail-closed).

**4. The record prints only the class code.** `step_4` passes the classification as `code` (`dry_run.py:796-800`) and
`step_record` writes it as `refusal` (`steps.py:146-147`); the classifier returns only module constants, never a reason
string. T8c asserts the reasons are absent from the record, stdout and stderr for six reason sets including the R3 ones,
and T4's `Q7331Z` sentinel cannot occur inside a digest (`test_dry_run.py:18`, `:519-523`). Executed records in
`classifier_counterfactuals.txt` show `(tooling_refusal, extraction_cell_r3_refusal)` etc. with no reason text.

**5. Full run.** `TMPDIR=/tmp/jwrev_tmp_d JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .`
at `901956944` from `/home/user/JouleWise` after `git fetch --unshallow` (TMPDIR outside the checkout, no float-like
token). Exact tail (`full_suite_tail.txt`):

```
        '--output-dir',str(f['root'])], out)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/JouleWise/tests/b5_analysis/test_sensitivity_guard.py", line 62, in invoke
    self.assertFalse(output.exists())
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1027 tests in 3565.259s

FAILED (failures=1, skipped=13)
EXIT=1
```

The one failure is G6, the order-dependent fixture leak of RUN_STATE items 134-135 (PR #603, not on the lane's merged
`origin/main`); standalone at the same head it is `Ran 1 test in 26.492s`, `OK` (`g6_standalone_tail.txt`). Every lane test
passes in the whole run: r14, T4, T8/T8b/T8c, the step-4 modules and the archive step-4 test. Two earlier whole-directory
attempts in this container gave no tail: one was stopped by my own 10-minute background limit, and its 12 GB of leftover
TMPDIR then exhausted the disk allowance so the next attempt errored in `tempfile` and `copytree` (fixture copies); the
run above started on an emptied TMPDIR. That is the same ENOSPC mechanism the lane records for Opus's `mint_kept_units`
ERROR (S6): environment-dependent, not a code or fixture defect.

Targeted run (T4, T8, T8b, T8c, `DriverPrimitiveTests`, the two step-4 modules, `test_archive`): `Ran 72 tests`, `OK`
(`targeted_tests_tail.txt`).

## Fix list

1. F1: amend the ruling's `r3` list with the three plan-named precheck codes and update the pins, r14 and the two
   table assertions as described; or record Ed's ruling that they are tooling at step 4, which is the other legitimate
   closure of NEEDS_RULING 1.
2. F2: state in the ruling that `member_code_on_kept_unit` (exit 2) is the extractor's existing stop for the plan's
   cooldown-cap case, so its cure route is also a ruling.
