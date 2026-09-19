SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Diagnostic read — why 8 of 12 derivation captures were non-valid on night n1-20260919, and why 3 of 4 valid values exceed the r6 level screen

Read-only. Cwd is a detached worktree at `d595aa9f` (the night's measurement head H). The night's evidence lives OUTSIDE this worktree and is read-only for you: night root `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/` (chain log `operator_logs/derivation-chain.log`, `night/chain.stdout.log`, `night/chain.stderr.log`, `night/censuses.jsonl`, and the twelve capture bundles `runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-dNN/` with `events.jsonl`, `instrument_evidence.json`, `manifest.json`, `power_trace.csv`, `raw/powermetrics.plist`), and the measurement clone `/Users/edr/JouleWise-measurement-20260919-derivation/` (its `runs/calibration_observation_ledger.jsonl`, 126 rows). Never write anywhere, never run git anywhere, never touch any other worktree or the canonical root `/Users/edr/code/JouleWise`. Report only in the envelope (under 8000 bytes; table first). Do not run powermetrics or any capture; do not launch anything that samples the machine.

## Facts already established (do not re-derive; verify only if you find them wrong)

- Session finalized 12/12, chain exit 0; ledger dispositions: d01, d03, d05, d12 `valid`; the other eight `ordinary-invalid`.
- `instrument_evidence.json` `reasons`: d02, d04, d06, d08, d09, d11 = `not_all_pulses_detected` + `pulse_detection_incomplete` (59 pulses listed, e.g. d02 detected 57/59); d07, d10 = `clock_anchor_unresolved` + `pulse_count_below_protocol:0!=59` (0 pulses, `clock_anchor_resolved` false, `baseline_w` null).
- Valid `b_fiducial_s`: d01 0.041133514338919874, d03 0.04200278099548145, d05 0.172710636067422, d12 0.03255031906139217. The r6 level screen is 0.032898493715362 s; d01, d03, d05 carry `exceeds_prior_level_screen: true` as a diagnostic.
- The desk verdict is INCONCLUSIVE (m = 4 < 6) under directive issue 316; that verdict is fixed and not your question.
- Every capture's `baseline_w` is 0.0 with `robust_sigma_w` 0.001 for the pulse-bearing captures; say whether that is the normal shape for a fiducial capture (compare one accepted r6 member under `/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/` named in `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` `derivation_corpus.members[].source_directory`; read-only).

## Questions (answer each with file paths, field names, and the exact commands you ran)

1. For each of the six `not_all_pulses_detected` captures: which pulse indices were not detected, what the detector saw at those indices (amplitude, residuals, any `reason` per pulse in `pulses[]`), and whether the misses cluster in time (first/last pulses, a contiguous run, or scattered). Cite the detector code in `joulewise/` that sets `detected` and the threshold it applies.
2. For d07 and d10 (0 pulses): what is in `power_trace.csv` and `raw/powermetrics.plist` (row counts, time span, sample cadence, any gap, any all-zero or constant segment), and what in `events.jsonl` marks the pulse train start/end. Was the fiducial pulse train emitted at all (is there evidence the load generator ran)? Cite the code path that reports `pulse_count_below_protocol`.
3. For the three over-screen valid captures (d01, d03, d05, especially d05 at 0.1727 s, five times the screen): which component of the bound dominates (`anchor_only_bound_s`, onset/offset residual widths, `residual_p95_s_diagnostic_only`, sample cadence); show the decomposition fields from `instrument_evidence.json` and `clock_anchor` for each of the four valid captures side by side. Cite the estimator code (`anchor_method_version` `powermetrics_native_second_rate_aware_set_membership_v1`).
4. Time correlation: list the twelve slot start times (chain log) beside each capture's outcome; note whether the failure pattern alternates or trends with time-of-night (00:10 → 02:03 PDT) and whether the two 0-pulse slots share anything (e.g. both immediately after a particular event in `night/chain.stderr.log`).
5. `night/chain.stderr.log` (244 lines): classify its lines (which are the two `clock_anchor_unresolved` lines, what the rest are), and quote any line that indicates powermetrics sampler restarts, permission prompts, or stalls.
6. Compare against the accepted r6 members: powermetrics sample cadence, `pulse_count`, `pulses[].delta_on_s` typical magnitudes, and `anchor_only_bound_s` typical magnitudes, so the reader sees whether the 09-19 captures differ in kind (instrument changed on macOS 25G83 with the new `/usr/bin/powermetrics` binary, sha256 b762e5bf…) or only in degree.
7. One paragraph of candidate causes ranked by the evidence you found, each with the single observation that would confirm or refute it. Do NOT propose changes to thresholds, screens, or the pre-registered rule; this is instrument diagnosis for the owner, not a proposal.
