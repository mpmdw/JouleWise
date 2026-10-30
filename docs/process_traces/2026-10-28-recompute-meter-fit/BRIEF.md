BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "RC-CMP-2: the recompute's meter clock fit follows the registered parser definition; the binding bar set moves to a release config; the meter line is exercised",
 "OBJECTIVE": "Remove the one known definition difference between the independent recompute and the pipeline (the meter clock-fit bins, 0.020 J on synthetic jitter against a 1.24e-4 J bar, commit 7e322b767), so the block-5 release comparison can agree on the whole-machine line, and fix the bar set that binds block 5's release in a config.",
 "AUTHORITY": [
   "RUN_STATE.md item 83 (lead rulings on RC-CMP-1 NEEDS_RULING: the recompute's coded bars 7e322b76 bind block 5's release)",
   "RUN_STATE.md item 84 (this brief's ruling: the meter clock fit is defined by the registered parser, registration_block5.md 'the parser fits the meter's sample clock to the host's clock from the poll times'; the recompute re-implements that definition in its own code)",
   "configs/campaigns/v5_claim_25g83/registration_block5.md (sealed; not amended)",
   "docs/process/gate_policy.md (binding)",
   "this brief"],
 "WRITE_SCOPE": [
   "scripts/independent_recompute_b5.py",
   "scripts/compare_b5_recompute.py",
   "tests/independent_recompute/**",
   "configs/analysis/b5/recompute_bars.json",
   ".codex-report/RC-CMP-2.md"],
 "BASE_HEAD": "tip of lane/2026-10-27-recompute-comparator (234fbb127 at writing)",
 "ACCEPTANCE": [
   "M1 the recompute's meter clock fit implements the definition of joulewise/external/km003c_parse.py clock_fit (batch selection by RESPONSE_CAP and FIT_MAX_RTT_MS with the FIT_MIN_POINTS fallback, first-pass least squares, bins = max(4, int(span / FIT_BIN_MS)) of width (span + 1) / bins, lowest residual per bin, envelope refit with fallback) in the recompute's own code; the recompute still imports nothing from joulewise.external or joulewise.b5_analysis at run time (tests may import the parser as the reference)",
   "M2 test_different_clock_fit_bins_disclose_energy_difference_without_slack is replaced by a test that the same adversarial jitter now gives agreement within the coded bar, plus a property test over at least 200 seeded jitter patterns (within the 3 ms eligible RTT cap, and some above it to hit the fallback) that the recompute's per-sample host times equal the parser's within 1 ns; counterfactual: the old binning fails the new tests",
   "M3 configs/analysis/b5/recompute_bars.json is the release copy of the coded bar set (content equal to tests/independent_recompute/bar_sets/recompute_coded_7e322b76.json plus whatever family the meter line needs, each bar with its derivation); the comparator's default --bars is that file; the S-13 set stays in tests as block 6's",
   "M4 the comparator covers the whole-machine meter line (gross meter energy per phase and rho) with a synthetic window or member fixture that has a meter stream; planted-fault test for the meter family with counterfactual",
   "M5 tests/independent_recompute passes; no file outside WRITE_SCOPE changed"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .",
   "grep -nE 'joulewise\\.(external|b5_analysis)' scripts/independent_recompute_b5.py scripts/compare_b5_recompute.py matches nothing"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# RC-CMP-2 brief

**Why.** RC-CMP-1 (`.codex-report/RC-CMP-1.md`, OPEN ISSUES 2) found 0 disagreements on a full-size synthetic window,
but that window has no meter stream. The one known definition difference is the meter clock fit: the recompute bins
the fit's residuals differently from the parser, which on adversarial synthetic jitter moves one sample by 1,249 ns
and the gross meter energy by 0.020 J against a 1.24e-4 J bar (commit `7e322b767`). On real data that would be a
release disagreement found with numbers in view. Independence means separate code, not a separate definition; the
same rule was applied to the meter request window in `7e322b767`.

**Rules.**
- Synthetic data only. Never open a real block-5 or block-6 archive, export or key directory.
- No change to registered arithmetic or to the sealed registration. The bars are not widened.
- Push only to `lane/2026-10-27-recompute-comparator`. No force push, no merge to main, no PR.
- One heavy run at a time; long runs detached with durable logs; push the report after each milestone.
- No full-size L9 dry run is needed for this job.
- After this job the lead launches two executing reviews together (gate policy rule 3) over RC-CMP-1 and RC-CMP-2.

**Report.** `.codex-report/RC-CMP-2.md`: SUMMARY, the M1-M5 table with evidence, FILES CHANGED, DECISIONS I MADE,
OPEN ISSUES, NEEDS_RULING.
