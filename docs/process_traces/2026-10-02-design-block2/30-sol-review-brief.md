You are an independent executing reviewer (Sol 6.1) of a JouleWise pull request: lane G2A-NIGHT-25G83-01, which makes the G2-a prefill probe window armable and harvestable at today's main. You did not write it. Working directory: a detached worktree at the PR head 8a8635a7b (base: origin/main b317866d0). Single non-interactive session; foreground only; no subagents. WRITE_SCOPE is empty: change no tracked file. Scratch: /tmp/g2a-lane-review/ (copy files there for mutations; never mutate the worktree). No sudo, launchctl, powermetrics, systemsetup, no model loading, no live capture; no git write, fetch or checkout. Interpreter: /Users/edr/code/JouleWise/.venv/bin/python -B (sandboxed runs cannot use pgrep/sysctl; a test failing only for that reason is an environment flag, compare against base; the 46-test "battery fixture in child Pythons" class is a known local-only failure).

## What the PR claims (verify each; do not trust it)

The lane brief is `/Users/edr/code/JouleWise-design-block2/docs/process_traces/2026-10-02-design-block2/03-lane-g2a-integration-brief.md` with continuation `04-lane-continuation-brief.md` in the same directory; the readiness scout that motivated it is `12-sol-g2a-readiness-scout.md` there. Rulings R1-R8:

- R1: Revision 6 start bookkeeping (manifest, `SESSION_ID`, 7680 s span) applies only to plans whose registration is the Revision 6 registration; other `DIAGNOSTIC_NO_PACK` calibration-kind chains keep OFF receipt + 600 s settle + clean dwell + gate, budgeted by one literal `NIGHT_PROGRAMMED_SPAN_S` in the chain (refuse when absent). Revision 6 behaviour unchanged.
- R2: the G2-a producer refuses any ledger snapshot refusal.
- R3: the pre-calibration screen literal is derived from the live acceptance; `gen_g2_phase_d.py --check` fails on drift.
- R4: the G2-a chain has argv-only and verify-only branches before any mutation; literal ledger/pin exports; installer probe accepts the G2-a inspection surface.
- R5: typed calibration refusal export.
- R6: one command authors a G2-a window (plan v2, chain, sidecar) with the listed refusals.
- R7: `scripts/harvest_g2a_window.py` (archive, authenticate, bracket verdict, strict member validation, summary regeneration, network-time report, SELECT/RECOVER/REFUSED verdict, pin advance); a prefill count < 3 is a valid member.

## What you must execute

- **Revision 6 non-regression.** Show that a Revision 6 derivation plan takes exactly the old admission path (manifest, `SESSION_ID`, 7680 s), with the tests that prove it; diff `scripts/run_night.py` and explain every changed line on that path. Any change in what a Revision 6 window admits is a blocker.
- **Admission discriminant.** Plant mutants in scratch copies: (a) a G2-a plan whose chain lacks `NIGHT_PROGRAMMED_SPAN_S` (must refuse before the OFF setter would run); (b) a Revision 6 plan whose registration bytes are D-166's (must NOT take the Revision 6 path); (c) the discriminant inverted; (d) the span literal removed from the generator. Report which test goes red for each; a surviving mutant is a finding.
- **Span arithmetic.** Recompute `NIGHT_PROGRAMMED_SPAN_S` from the code constants the generator cites; check the allowance is stated and that `window_max_s = span + 2700` rounded up leaves the clean dwell its full cap.
- **Screen.** Confirm the rendered literal equals `_derive_preflight_systematic_screen_s()` against the live acceptance (boolean comparison only; do not print the value) and that a stale literal fails `--check`.
- **Argv-only safety.** Run the emitted chain with `NIGHT_RESERVATION_ARGV_ONLY=1` (and with `NIGHT_VERIFY_ONLY=1` where safe) against a scratch tree; prove by before/after listing that nothing is created or changed and that the printed argv matches what the installer parses.
- **Installer.** Render-only on a G2-a fixture plan; the derivation chain path unchanged (tests).
- **Harvest.** Run `harvest_g2a_window.py` against synthetic fixtures the tests build (complete sweep → SELECT; one invalid small member → RECOVER; pre-screen stop → RECOVER; archive mismatch → REFUSED); confirm it refuses before the completion boundary and prints no energy, fiducial bound, drift or per-member count. Check the low-count proof: a member with prefill overlap count < 3 is valid, does not stop the campaign, and the selector applies D-166.
- **Fences.** `git diff --stat b317866d0 8a8635a7b` touches none of `joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`, `scripts/validate_powermetrics_fiducial.py`, `scripts/night_chains/**`, `configs/calibration/**`, `configs/campaigns/**` (except a new registration directory if present), `scripts/run_campaign.py`.
- **Tests.** Run `tests.test_run_night tests.test_night_agent_install tests.test_night_gate tests.test_gen_g2_phase_d tests.test_generate_g2a_probe_inputs tests.test_summarize_g2a_prefill_probe tests.test_select_g2a_prefill_length tests.test_harvest_window tests.test_gen_derivation_night tests.test_check_window_provenance` and every new test module the PR adds; report exact tails (module names that do not exist: say so).

## Output

The report envelope your wrapper requires, with `verdict.decision` MERGE or BLOCK and each finding as {id, severity (blocker|major|minor|nit), file:line, claim, evidence you executed}. BLOCK only for a defect that can make a window admit what it should refuse (or refuse a clean window), change a Revision 6 admission, mutate state during inspection, or let the harvest return SELECT on an incomplete or unauthenticated sweep. Do not claim anything you did not execute.

WRITE_SCOPE: []
