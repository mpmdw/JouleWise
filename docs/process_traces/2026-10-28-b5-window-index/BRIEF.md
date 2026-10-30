BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "S11-INDEX-1: write block 5's window index (configs/analysis/b5/analysed_windows.json) for the laptop dry run, and list every other input L9 needs before a real blind run",
 "OBJECTIVE": "Produce the S11 window index that lane L9 (accepted at 2ea99f51f) loads at step 0, built only from tracked records and the committed transfer manifests, so the block-5 blind dry run can start on the analysis laptop as soon as N3 confirms.",
 "AUTHORITY": [
   "docs/process_traces/2026-10-27-l9-restart/BLOCK5-TRANSFER.md (analysis laptop step 2) and ED-RULING.md item 10",
   "RUN_STATE.md items 28, 31, 83 (analysed attempts ALPHA a1, BETA a6, GAMMA a1; L9 acceptance head 2ea99f51f)",
   "report/2026-10-22-blind-dry-run-scout .codex-report/BLIND-DRY-RUN-SCOUT.md section 2 (index requirements, governing harvest pins)",
   "configs/campaigns/v5_claim_25g83/registration_block5.md, analysis_plan_block5.md, docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md and its addenda, docs/process_traces/2026-10-block5/",
   "this brief"],
 "WRITE_SCOPE": [
   "configs/analysis/b5/analysed_windows.json",
   "tests/b5_analysis/test_analysed_windows_index.py",
   ".codex-report/S11-INDEX-1.md"],
 "BASE_HEAD": "lane/2026-10-27-l9-2 at 2b3047d5b (code identical to 2ea99f51f outside .codex-report/)",
 "ACCEPTANCE": [
   "I1 every block-5 attempt of every pack (ALPHA, BETA, GAMMA) under the current seal is an entry, attempts numbered from 1 with no gap and t0 non-decreasing, each with verdict, claim_usable, entry_kind, cause_key and record_citation taken from the tracked attempt records (cite file:line for each); the analysed attempts are exactly ALPHA a1 v5-b5-alpha-a1-20261009T2312Z, BETA a6 v5-b5-beta-a6-20261011T2011Z, GAMMA a1 v5-b5-gamma-a1-20261012T0420Z; earlier-seal history is represented as L9's schema requires",
   "I2 roots are absolute paths under /Users/edr exactly as on the measurement Mac (the laptop unpacked to the same paths): archive_root, claim_runs_root, bound_runs_root, custody_root, measurement_root, superseded_archive_roots; each analysed entry's paths are shown to exist as directories in the committed manifests docs/process_traces/2026-10-27-l9-restart/b5-transfer/*.manifest.json (cite the manifest and a file path under each root)",
   "I3 harvest_record_sha256 of each analysed entry equals the sha256 of <archive_root>/harvest.json in its harvest manifest; harvest_pin is the governing harvest program per the scout report (ALPHA a1 224a264c5, BETA a6 and GAMMA a1 b039c0257) in the form L9 expects",
   "I4 tests/b5_analysis/test_analysed_windows_index.py loads the file with joulewise.b5_analysis.windows.load_window_index (real seal pins and pack table) and select_analysed_attempts, and asserts the three analysed attempts; it skips with a reason, not fails, when the roots are absent (cloud)",
   "I5 the report lists every other input L9 steps 0-11 read before or during a real blind run that is not in the transfer manifests (for example custody_root contents such as the excluded results-clone, seal-record FILLs, sidecars, pins), each with the code line that reads it and whether it is present, absent or needs a Mac-side action; nothing is guessed"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_analysed_windows_index tests.b5_analysis.test_windows",
   "git diff --name-only 2b3047d5b lists only WRITE_SCOPE paths"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# S11-INDEX-1 brief

**Why.** The block-5 bytes are now on the analysis laptop, verified file by file against the manifests the measurement
Mac committed (`b5-transfer/`), unpacked to the same absolute paths as on the Mac. L9 is accepted at `2ea99f51f`.
The only missing input the scout report names is the tracked window index, which exists on no branch.

**Rules.**
- Structure only. Never open, parse or print an energy, power, duration or other measured value. The manifests give
  paths, sizes and digests; attempt records give verdicts and reasons. Those are all you need.
- Never select or reorder attempts by any value. The analysed attempts are fixed by RUN_STATE items 28 and 31.
- No change to any code, registration, plan, seal record or L9 file. If L9's schema cannot represent a record as it
  stands, return NEEDS_RULING with the exact conflict.
- Push only to a new branch `lane/2026-10-28-b5-window-index` cut from `lane/2026-10-27-l9-2` at `2b3047d5b`. No
  force push, no merge to main, no PR.

**Report.** `.codex-report/S11-INDEX-1.md`: SUMMARY, the I1-I5 table with evidence, the entry table (pack, attempt,
plan id, verdict, claim_usable, citation), FILES CHANGED, DECISIONS I MADE, OPEN ISSUES, NEEDS_RULING.
