BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "L9-PATHTOKEN-1: blind repair of the block-5 dry run's step-0 tooling refusal on real archive file names",
 "OBJECTIVE": "Let the census of real harvest archives pass the structure-only guards when a recorded path is an authenticated archive inventory name that happens to look like a number (a git short hash such as 82622e70, a version such as 2.1.260), without weakening the guard for any value L9 itself produces or for any path not authenticated by the index-pinned harvest.",
 "AUTHORITY": [
   "RUN_STATE.md items 83, 93, 94, 95 (L9 accepted at 2ea99f51f; dry run attempt A refused at step 0)",
   "report/2026-10-22-blind-dry-run-scout BLIND-DRY-RUN-SCOUT.md section 3 (cure tooling refusals blind and restart in a fresh custody root)",
   "docs/process/gate_policy.md (binding: two cross-family executing reviews for blinding code)",
   "this brief"],
 "WRITE_SCOPE": [
   "joulewise/b5_analysis/dry_run.py",
   "tests/b5_analysis/test_dry_run.py",
   "tests/b5_analysis/test_census_path_token.py",
   "tests/b5_analysis/fixtures_s10.py",
   ".codex-report/L9-PATHTOKEN-1.md"],
 "BASE_HEAD": "b13a510dc15b5e280309f7dd6b280426bf44afc6 (the accepted analysis commit; contained in origin/main)",
 "ACCEPTANCE": [
   "P1 diagnosis reproduced on synthetic data: a synthetic window whose harvest archive inventory contains source files named like the real ones (for example sources/night-custody/results-clone/docs/process_traces/x/replay-branch-82622e70-summary.txt, .../21e2-delta2-final-head-opus.md, .../claude-help-2.1.260.txt) makes step 0 refuse reader_record_not_structure_only at the base, and makes validate_dry_run_record refuse dry_run_record_invalid on the input_census path; record both as counterfactuals",
   "P2 the census record (role census_<pack>) and the run record's input_census rows admit a float-like token in a path only when that exact path is an entry of the archive's authenticated inventory (the names the index-pinned harvest record and the archive's authenticated source listing vouch for, checked at write time and again in the validator); every other field of every structure-only record, and every path not in that inventory, keeps the full _FLOAT_TOKEN guard; the existing ReaderRecordGuardTests case census_gamma {'path':'sources/1e-100.json'} with no such inventory entry still refuses",
   "P3 no change to any analysis arithmetic, step order, refusal class table, or any file outside WRITE_SCOPE; the governed estimator files are byte-identical",
   "P4 tests: the new regression tests fail at the base and pass after; tests.b5_analysis short modules pass (JW_B5_SYNTHETIC_ONLY=1); the full-size test_dry_run with JW_B5_S10_REAL_PROGRAMS=1 is NOT required here (the lead runs it on the laptop)"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_census_path_token tests.b5_analysis.test_dry_run",
   "git diff --name-only b13a510dc HEAD lists only WRITE_SCOPE paths"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# L9-PATHTOKEN-1 brief

**What happened (structure only).** The real block-5 blind dry run, attempt A (laptop, 2026-10-29 04:42 UTC, custody
root /Users/edr/jw-b5-custody/dry-a), stopped at step 0 with tooling_refusal reader_record_not_structure_only, and then
the run record failed validate_dry_run_record (dry_run_record_invalid at the input_census path check,
dry_run.py:291). Cause, from the transfer manifests committed on main (paths only): each analysed harvest archive
holds about 68 inventory files under sources/night-custody/results-clone/docs/process_traces/ whose names contain git
short hashes or version numbers that _FLOAT_TOKEN (dry_run.py:207) reads as numbers, for example 82622e70, 4158e658,
21e2, 2.1.260. The synthetic fixtures have no such names, so no test covered them. No measured value is involved.

**Why the narrow form.** The guard exists so that no analysis number reaches a structure-only record. An archive
inventory name is fixed at collection, authenticated by the index-pinned harvest digest, and cannot carry an
analysis result. A path that is not such an authenticated inventory entry gets no exemption, which keeps the
existing test's intent.

**Rules.** Synthetic data only; never open real block-5/6/BYTES data (none is in the cloud). Branch
lane/2026-10-29-l9-census-path from b13a510dc; push only that branch; no force push, no merge, no PR. The lead
opens the PR after two executing reviews.

**Report.** .codex-report/L9-PATHTOKEN-1.md: SUMMARY, the P1-P4 table with evidence and counterfactuals, FILES
CHANGED, DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.
