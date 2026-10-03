# Lane G2A-NIGHT-25G83-01, continuation (round 2)

You are continuing lane G2A-NIGHT-25G83-01 as the implementing seat (Sol 6.1). The original brief
is `/Users/edr/code/JouleWise-design-block2/docs/process_traces/2026-10-02-design-block2/03-lane-g2a-integration-brief.md`;
read it in full: every ruling, fence, verification step and the WRITE_SCOPE there still bind you.
Your first round's report is
`/Users/edr/code/JouleWise-design-block2/docs/process_traces/2026-10-02-design-block2/21-sol-lane-report-round1.md`.
Its R2 and R3 work is committed on this branch as `b2393079` (by the lead).

## Lead rulings on your round-1 flags

- **F1 (Revision 6 test fixtures).** RULED: correct the fixture identity only. Where an existing
  Revision 6 start-condition test builds its plan with the D-166 registration bytes but asserts
  Revision 6 behaviour (manifest, 7680 s budget, `SESSION_ID`), change the fixture so its plan
  authenticates as the actual Revision 6 registration (`night_gate.REV6_25G83_REGISTRATION_SHA256`
  bytes, i.e. `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`), keeping every
  assertion unchanged. Then add the mirror tests: the same fixture with the D-166 registration and a
  non-Revision-6 calibration-kind chain takes the R1 generic path (no manifest read, budget from
  `NIGHT_PROGRAMMED_SPAN_S`, refusal when the literal is absent). List every fixture you changed in
  your report.
- **F2 (git).** Do NOT run `git add` or `git commit` (the sandbox cannot write the worktree's git
  metadata). Leave all changes in the working tree; the lead reviews and commits them. Do not run
  `git stash`, `checkout` or `reset`.
- **F3.** Known local-only failure class ("battery fixture in child Pythons", 46 tests); compare
  against base and report, nothing to fix.
- **F4.** Complete R1 and R4-R7 now, with the verification the original brief requires.

## `NIGHT_PROGRAMMED_SPAN_S`

Size the variable-work allowance from code (model load for each stage's campaign, warmup,
prefill and decode at the producer's output budget for both models, cooldown/admission, sampler
readiness, reductions, custody operations); where code gives no bound, use a stated conservative
per-member and per-stage figure and show the arithmetic in a comment next to the constant. The
final literal is an integer. Do not read any measured value from any archived bundle to size it;
a published or documented timing (for example the runsheet's "historical approximately
148-second cadence" per member) may be cited.

Report in your wrapper's envelope as before. Budget: finish within 100 minutes; if you cannot
finish, stop at a consistent state (tests passing for what you completed) and report exactly what
remains.

WRITE_SCOPE: ["scripts/gen_g2_phase_d.py", "scripts/generate_g2a_probe_inputs.py", "scripts/run_night.py", "joulewise/night_agent_install.py", "joulewise/night_gate.py", "scripts/harvest_g2a_window.py", "scripts/summarize_g2a_prefill_probe.py", "scripts/select_g2a_prefill_length.py", "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md", "docs/phase_2/window_runbook.md", "tests/**", "scripts/test_timings.json"]
