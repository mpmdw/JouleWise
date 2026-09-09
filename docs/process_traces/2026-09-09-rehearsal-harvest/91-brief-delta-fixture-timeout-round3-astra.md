SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Delta re-audit — FIXTURE-TIMEOUT-WALLCLOCK-01 fix round 3 (consult-authored), bdbc9e75 → 016ac5f0 (gpt-6-astra, medium, genre review, read-only)

Closing: consult 87 F1 (/Users/edr/code/JouleWise-wt-magistrate-1ef89702/docs/process_traces/2026-09-09-rehearsal-harvest/87-consult-fixture-regression-portability-astra-report.md): the regression's in-controller cadence probe asserted a non-null cadence ratio that a sparse ~112 ms measured window cannot guarantee on a fast host. Round 3 replaced the whole test method with the consult's minimal replacement (stress floor, real deadline, strict_valid True, idle_drift bounded, 100 post samples) and removed the two diagnostic-only additions (3ca9a58c, bdbc9e75).
Audit ONLY `git diff bdbc9e75..016ac5f0` (tests/test_run_campaign.py):
1. The new method is byte-equivalent in behaviour to the consult's replacement (compare against 87 §Minimal replacement; note any deviation and whether it matters).
2. No wrapper/patch of `_Execution._stage_idle_drift_sentinel` remains; no `checked_sentinel`, `stages_checked`, `_window_gap_stats`, `TracePoint` references remain in the test; the shared helper's round-2 form is unchanged.
3. Portability: list every assertion in the replaced method and say whether it holds on Linux 1×, on the Mac at 3.4× slack, and at an inherited 7× scale (per 87's assumption table).
4. Defect discrimination retained: explain (from code) why the sleeping fixture at ≥3.5× would still produce post_idle_unavailable and fail this test (the counterfactual), and confirm `test_real_capture_timeout_leaves_post_idle_unavailable` and the timeout-formula test are untouched.
5. Same-signature statement for "Mac-calibrated test assumption": closed or surviving, with the line.
Read-only; no edits. Report claude-codex-report/v1, genre review, header < 8192 bytes (verdict = {counts, findings} only); body = disposition per item with command tails (execution may be blocked by the sandbox's missing temp dir; say so; do not fabricate).
