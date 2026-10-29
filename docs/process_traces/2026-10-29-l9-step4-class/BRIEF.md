BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "L9-STEP4-1: make the step-4 exit classifier total and faithful to the analysis plan's registered p42 exception",
 "OBJECTIVE": "Every way step 4 can exit maps to a named, registered class (registered p42 outcome, outcome-class refusal, or tooling refusal), so the blind dry run's own record says what happened and no step-4 exit is unclassified.",
 "AUTHORITY": [
   "configs/campaigns/v5_claim_25g83/analysis_plan_block5.md section 3.1 Refusals: 'if step 4 exits 1 and its refused cells are only the p42 floor cells and no kept member was omitted from the spec, the report it wrote is the input to step 5 and the exit is recorded as the registered p42 outcome. A tooling refusal goes to R3 ...; a refusal that is a registered scientific outcome ... is the result and is printed as such.'",
   "RUN_STATE.md item recording this ruling (lead, 2026-10-29, made blind)",
   "docs/process/gate_policy.md (binding)",
   "this brief"],
 "WRITE_SCOPE": [
   "joulewise/b5_analysis/steps.py",
   "configs/analysis/b5/dry_run_refusal_classes.json",
   "tests/b5_analysis/test_step4_exit_classes.py",
   "tests/b5_analysis/test_dry_run.py",
   ".codex-report/L9-STEP4-1.md"],
 "BASE_HEAD": "lane/2026-10-29-l9-census-path at 49991c73a (L9-PATHTOKEN-1, on b13a510dc)",
 "ACCEPTANCE": [
   "S1 classify_step4_exit (joulewise/b5_analysis/steps.py) maps exit 1 with no spec-membership refusals, a well-formed report whose cell set equals the spec's, and a NON-EMPTY refused set that is a SUBSET of the spec's p42 floor cells, to p42_floor_cells_only (the plan's 'only the p42 floor cells'); today it requires equality",
   "S2 exit 1 where any non-p42 floor cell is not extractable maps to a new outcome-class code (name it floor_cell_not_extractable or follow the existing naming in dry_run_refusal_classes.json), registered in that table as an outcome class, so later steps stop and the record prints the registered outcome",
   "S3 spec_membership_refusals non-empty, a cell-set mismatch, duplicate ids, malformed cells or report, a non-boolean extractable, and exit 1 with an empty refused set each map to a named tooling-refusal code registered in the table; an exit status other than 0 or 1 keeps its existing handling",
   "S4 the driver passes the class through so the step record shows the code (tooling_refusal with its code, or outcome_class), never unclassified_refusal, for every branch; one synthetic regression test per branch, each failing (unclassified) at 49991c73a and passing after; the real p42-only case still returns p42_floor_cells_only and continues to step 5",
   "S5 no change to analysis arithmetic, extraction, the spec files, the census-path change, or any file outside WRITE_SCOPE; tests.b5_analysis short modules pass (JW_B5_SYNTHETIC_ONLY=1)"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_step4_exit_classes tests.b5_analysis.test_dry_run",
   "git diff --name-only 49991c73a HEAD lists only WRITE_SCOPE paths"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# L9-STEP4-1 brief

**What happened (structure only).** A probe of the real block-5 dry run (custody dry-b, at a census-path variant of
`b13a510dc`) passed steps 0, 1, 2, 3 and 3b, then stopped at step 4 ALPHA with `unclassified_refusal`, exit status 1.
`classify_step4_exit` returns "refused" unless the refused cells EXACTLY equal the p42 floor cells, and it has no
name for any other branch. Nobody has looked at which branch fired, and nobody will: the per-cell extractable flags
are outcome-bearing. This repair is blind: it makes every branch name itself through the registered table, and the
next dry run's own record reports the code.

**The lead's ruling (blind, before any branch is known).** The plan's "its refused cells are only the p42 floor
cells" means every refused cell is a p42 floor cell (a non-empty subset), not necessarily all of them. A non-p42
floor cell that is not extractable is a registered scientific outcome: it stops the later steps and is printed as
such. Malformed or inconsistent reports and spec-membership refusals are tooling.

**Rules.** Synthetic data only; never open real block-5/6/BYTES data (none is in the cloud). Commit on
lane/2026-10-29-l9-census-path on top of 49991c73a; push only that branch; no force push, no merge, no PR.

**Report.** .codex-report/L9-STEP4-1.md: SUMMARY, the S1-S5 table with evidence and counterfactuals, FILES CHANGED,
DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.
