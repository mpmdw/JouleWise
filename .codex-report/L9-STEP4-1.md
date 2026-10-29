# L9-STEP4-1 seat report

bridge-report/v1 · brief `main:docs/process_traces/2026-10-29-l9-step4-class/BRIEF.md` (`8b4e6dd0d`) · branch
`lane/2026-10-29-l9-census-path` on BASE_HEAD `49991c73a`.

## SUMMARY

EARLY_RETURN: NEEDS_SCOPE. S1, S2, S3 and S5 are met. S4 is met for the classifier and step record but not in the
driver. `classify_step4_exit` now gives every step-4 exit-1 branch a registered name, and every name is in
`dry_run_refusal_classes.json`. But the driver that would pass the name into the step record is `dry_run.step_4` in
`joulewise/b5_analysis/dry_run.py`, and that file is not in WRITE_SCOPE. The driver only reads the classification when
it equals `p42_floor_cells_only`. In every other case it keeps the extractor's stderr token. On exit 1 that line is
`refused cells (fail-closed): ...`, which `refusal_token` turns into None, so the record still shows
`unclassified_refusal`. A two-line driver patch and its test are below. I validated both in a scratch worktree and did
not commit them. Until the patch lands, the next dry run would still record step 4 as `unclassified_refusal` for every
branch except the p42 one.

Lead: session 015ASG1T only. No other session has messaged this seat.

## SEAT

- Claude cloud session (scheduled routine), 2026-10-29. Python 3.13 at `/usr/bin/python3.13`. There is no
  `/opt/homebrew` link because no test needed one. TMPDIR is `/tmp/claude-0/jwtmp`: outside the checkout, no symlink,
  no float-like token.
- Synthetic data only. I did not open or search for any real block-5/6/BYTES data.

## S1-S5

| Item | Status | Evidence | Counterfactual |
|---|---|---|---|
| S1 subset rule | MET | `test_S1_a_nonempty_subset_of_p42_floor_cells_is_the_registered_exit`: a refusal of only `syn-p42-abs`, or only `syn-p42-cmp`, returns `p42_floor_cells_only`, and the step record is `ok` with `registered_exit` set. `test_S1_every_p42_floor_cell_refused_is_the_registered_exit` covers the full p42 set. `refused <= p42` with `refused` non-empty. | At 49991c73a the subset cases return `refused` (2 subtest failures). The full-set case passed then and still passes. |
| S2 outcome class | MET (classifier + table) | A non-p42 floor cell that is not extractable returns `floor_cell_not_extractable`, alone or mixed with p42 cells, and also in a spec with no p42 cells. The code is registered under `outcome_class`. `step_record` gives `outcome_class` / `outcome-class refusal at step 4`. | At base: `refused`, and the code was absent from the table (4 failures). |
| S3 tooling codes | MET (classifier + table) | Tooling codes, all registered: `extraction_spec_membership_refused` (checked first after report shape, whatever the refused set is), `extraction_cell_set_differs_from_spec`, `extraction_cell_ids_duplicated` (report or spec), `extraction_report_malformed` (report not a mapping; `cells` or `spec_membership_refusals` not a list; a cell not a mapping, or with an empty or non-str id), `extraction_spec_malformed`, `extraction_extractable_not_boolean`, `extraction_exit_without_refused_cell`. Exit statuses other than 0/1, and non-int statuses, still return `refused`, so the driver keeps the extractor's own token for them as before. | At base every one of these branches returns `refused` and the codes are not registered (21 subtest failures). |
| S4 driver passes class | **NOT MET: NEEDS_SCOPE** | In-scope part: `step_record('4', exit_status=1, refusal_code=<class>, classes=refusal_classes())` gives the registered `tooling_refusal`/`outcome_class` status for every branch (`test_step4_exit_classes`, 13 tests, all OK). Driver part: the patch below, applied in a scratch worktree, passes the new `test_T8b_step4_exit_names_its_class` (target refusal → step 4 `outcome_class`, run exit 3, steps 5+ `not_run`; exit 1 with nothing refused → `tooling_refusal extraction_exit_without_refused_cell`) and the amended T8. The existing p42-only T8 path still reaches step 5, and so does `test_chain_fixture` (p42 = the full set). | With the driver unpatched, T8b fails: run exit 2, `step 4 alpha unclassified_refusal`. |
| S5 nothing else changed; tests | MET (see TESTS) | `git diff --name-only 49991c73a HEAD` lists only `joulewise/b5_analysis/steps.py`, `configs/analysis/b5/dry_run_refusal_classes.json`, `tests/b5_analysis/test_step4_exit_classes.py`, `tests/b5_analysis/test_dry_run.py` (T18) and this report. No change to arithmetic, extraction, spec files or the census path. `disclosures.py` imports `classify_step4_exit` but never calls it. | - |

## TESTS

- `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_step4_exit_classes
  tests.b5_analysis.test_dry_run` gives Ran 68, OK (skipped=3). The skips are the existing full-size joined runs.
- First run: 1 failure and 1 error.
  - T18 pins the table's `outcome_class` set to `run_d165_closeout_from_custody.OUTCOME_CLASS_CODES`, so it fails once
    the step-4 class is added. I amended it in `test_dry_run.py` (in scope) to closeout codes ∪
    `{floor_cell_not_extractable}`. Step 6 keeps its own constant, so the S7 split still holds.
  - `test_only_git_seams_replay_registered_history_and_tracked_index` raised `paper_reported_energy_ordering_history_invalid`
    on the shallow clone. It passes after `git fetch --unshallow`. That is the environment, not this change.
- `git diff --name-only 49991c73a HEAD` lists only WRITE_SCOPE paths.
- I did not run the full `discover` sweep of every short module. I ran only the brief's VERIFICATION modules.

## PROPOSED DRIVER PATCH (not committed; needs `dry_run.py` added to WRITE_SCOPE)

```diff
diff --git a/joulewise/b5_analysis/dry_run.py b/joulewise/b5_analysis/dry_run.py
index 5e9331c..ef9bd34 100644
--- a/joulewise/b5_analysis/dry_run.py
+++ b/joulewise/b5_analysis/dry_run.py
@@ -796,6 +796,8 @@ def step_4(s,r):
             classification=classify_step4_exit(exit_status,s.read('extraction_'+pack),s.specs[pack])
             if classification=='p42_floor_cells_only': code,registered=None,classification
             elif classification=='refused' and exit_status==0: exit_status=2
+            # Every other exit-1 branch is a registered tooling or outcome code.
+            elif exit_status==1 and classification!='refused': code=classification
         records.append(s.record('4',window=pack,exit_status=exit_status,code=code,outputs=outputs,registered_exit=registered))
         if records[-1].status!='ok': break
     return records
diff --git a/tests/b5_analysis/test_dry_run.py b/tests/b5_analysis/test_dry_run.py
index 7233f8a..a74703c 100644
--- a/tests/b5_analysis/test_dry_run.py
+++ b/tests/b5_analysis/test_dry_run.py
@@ -387,7 +387,7 @@ class DriverDouble(d.StepRunner):
                     spec_membership_refusals=[],cells=[{'cell_id':window+'-target','extractable':not self.target_refusal},
                                                      {'cell_id':window+'-p42','extractable':not self.p42}])
                 write(option('--out'),value)
-                if self.p42 or self.target_refusal:return 1
+                if self.p42 or self.target_refusal or getattr(self,'empty_exit',False):return 1
             elif step=='5' and '--out-dir' in argv:
                 directory=Path(option('--out-dir'))
                 for relative in ('floor-mint-pinset.json','floor-mint-inputs.json','alpha/calibration_plan.json','beta/calibration_plan.json',
@@ -535,9 +535,23 @@ class DriverAcceptanceTests(unittest.TestCase):
         DriverDouble.p42=True;result=self.execute();self.assertEqual(result.code,0,result.stderr)
         self.assertTrue(any(step=='5' for step,_,_ in DriverDouble.calls))
         self.assertEqual([r['registered_exit'] for r in result.record['steps'] if r['step']=='4'],['p42_floor_cells_only']*2)
-        DriverDouble.calls=[];DriverDouble.target_refusal=True;result=self.execute();self.assertEqual(result.code,2)
+        DriverDouble.calls=[];DriverDouble.target_refusal=True;result=self.execute();self.assertEqual(result.code,3)
         self.assertFalse(any(step=='5' for step,_,_ in DriverDouble.calls))
 
+    def test_T8b_step4_exit_names_its_class(self):
+        DriverDouble.target_refusal=True;result=self.execute();self.assertEqual(result.code,3,result.stderr)
+        rows=[(r['status'],r['refusal']) for r in result.record['steps'] if r['step']=='4']
+        self.assertEqual(rows,[('outcome_class','outcome-class refusal at step 4')])
+        self.assertFalse(any(step=='5' for step,_,_ in DriverDouble.calls))
+        self.assertTrue(all(r['status']=='not_run' for r in result.record['steps'] if r['step'] in ('5','8','6','9','9b','10','11')))
+        for name in ('p42','target_refusal'):setattr(DriverDouble,name,False)
+        DriverDouble.calls=[];DriverDouble.empty_exit=True
+        try:result=self.execute()
+        finally:DriverDouble.empty_exit=False
+        self.assertEqual(result.code,2,result.stderr)
+        rows=[(r['status'],r['refusal']) for r in result.record['steps'] if r['step']=='4']
+        self.assertEqual(rows,[('tooling_refusal','extraction_exit_without_refused_cell')])
+
     def test_T9_strict_validation_stops_and_never_visits_removed_bundle(self):
         result=self.execute();self.assertEqual(result.code,0,result.stderr)
         bundles=[argv[-1] for step,_,argv in DriverDouble.calls if step=='1' and argv]
```

The T8 amendment reflects the ruling: a target-cell refusal is now a registered outcome (run exit 3), no longer an
unclassified refusal (run exit 2). The validator (`_validate_dry_run_record`) needs no change. It already accepts
`outcome_class` rows at step 4 and checks tooling codes against the same table.

## FILES CHANGED

- `joulewise/b5_analysis/steps.py`: `STEP4_*` code constants; `classify_step4_exit` returns a registered name for
  every exit-1 branch, and accepts a non-empty subset of the p42 floor cells.
- `configs/analysis/b5/dry_run_refusal_classes.json`: 7 tooling codes and 1 outcome class added, kept sorted (T18).
- `tests/b5_analysis/test_step4_exit_classes.py`: new, 13 tests.
- `tests/b5_analysis/test_dry_run.py`: T18 accepts the step-4 outcome class next to the closeout's.
- `.codex-report/L9-STEP4-1.md`: this report.

## DECISIONS I MADE

1. Branch precedence: report shape, then spec membership, then spec shape, then duplicate ids, then cell-set match,
   then `extractable` type, then an empty refused set, then the p42 subset test. A spec-membership refusal is tooling
   even when the refused cells alone would be p42-only, because the plan's exception requires that "no kept member was
   omitted".
2. Codes are prefixed `extraction_` to follow the table's existing `extraction_spec_differs_from_archive`. The outcome
   class uses the brief's name, `floor_cell_not_extractable`.
3. A spec that does not validate is its own tooling code, `extraction_spec_malformed`. Before, it fell into "refused"
   along with everything else.
4. Behaviour for exit 0 is unchanged: it returns `ok` without checking the report, as before. That is outside S1-S3.
5. I did not edit `dry_run.py`, even though S4 needs it. CLAUDE.md says WRITE_SCOPE is exhaustive and must not be
   widened for work believed necessary.

## OPEN ISSUES

1. S4's driver hand-off needs the patch above, so `dry_run.py` must be added to WRITE_SCOPE. Until then, a real dry
   run still records any step-4 exit 1 that is not p42-only as `unclassified_refusal`.
2. `test_T8_p42_only_exception_and_target_refusal` asserts run exit 2 for a target refusal. That is true today only
   because the driver is unpatched. The patch changes the assertion to 3, as the ruling says.

## NEEDS_RULING

None. NEEDS_SCOPE: add `joulewise/b5_analysis/dry_run.py` (step_4, two lines) to WRITE_SCOPE, then apply the patch above.
