# Lane G2A-NIGHT-25G83-01: make the G2-a probe window armable and harvestable at today's main

You are the implementing seat (Sol 6.1) for one lane of the JouleWise measurement project. Working
directory: the worktree you were started in, on branch `feat/2026-10-02-g2a-night-integration`
(base: origin/main `b317866d`). Single non-interactive session; foreground only; no subagents.
No sudo, launchctl, powermetrics, systemsetup, no model loading, no live capture; no git fetch,
pull, checkout, push or branch operations. Commit your work on this branch in small, described
commits (`git add` only paths in WRITE_SCOPE; commit messages end with
`Co-Authored-By: Codex (gpt-6.1-sol) <noreply@openai.com>`). Interpreter:
`/Users/edr/code/JouleWise/.venv/bin/python -B`; run tests with `-m unittest`. Sandboxed runs cannot
use pgrep/sysctl; a test that fails only for that reason is an environment flag; compare it
against the base.

## Why

The G2-a window (queue row `V5-G2A-PREFILL-PROBE-01`; rule D-166 in `docs/decision_log.md` as
amended 2026-08-30) measures, for four prompt lengths 512/1024/2048/4096, how many 100 ms power
records overlap each Qwen3-1.7B member's prefill phase (≥5 small members per length, one 8B
member per length non-gating), between a governed pre and post pulse calibration. It was prepared
on 2026-09-10 (runbook 68,
`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`) and
superseded only by the macOS 25F84→25G83 acceptance mismatch, which PR #457 cured. Since then the
night machinery was rebuilt around the Revision 6 derivation windows, and a read-only scout at
`b317866d` found the G2-a path no longer traverses it. The scout report is
`/Users/edr/code/JouleWise-design-block2/docs/process_traces/2026-10-02-design-block2/12-sol-g2a-readiness-scout.md` (absolute path; read it there) (read it first; its
item ids B1-B8, N1-N5 are used below). The orchestrator's rulings on its open questions are below;
implement them.

## Rulings (the orchestrator decided these; do not reopen them)

R1. **Admission scope (scout B6, B7, B8).** Revision 6 bookkeeping (the
`start_conditions_manifest.json` with a prior Revision 6 session, the literal `SESSION_ID` pattern,
`DERIVATION_PROGRAMMED_SPAN_S` = 7680) applies only to Revision 6 derivation windows, identified by
the plan's `registration_path` file hashing to `night_gate.REV6_25G83_REGISTRATION_SHA256` (or an
equally exact discriminant you find already in code; say which). Every other `DIAGNOSTIC_NO_PACK`
calibration-kind chain, G2-a included, keeps the PHYSICAL start conditions unchanged: network-time
OFF receipt through the existing setter path and its 600 s settle on both clocks, the clean dwell
(`scripts/prewindow_check.sh`) overlapping that settle, the night gate's checks (census, AC,
battery float, display, load, thermal). Its start budget is
`latest chain start = t0 + window_max_s − NIGHT_PROGRAMMED_SPAN_S`, where `NIGHT_PROGRAMMED_SPAN_S`
is ONE literal integer export in the pinned chain, written by the chain generator from the code
constants (scout item 12's arithmetic: settles, countdowns, members × (idle 75 + 5 + 1),
two calibration captures, display pauses) plus a declared allowance for model load and inference
work that you size from code and state in the generator with its arithmetic. A non-Revision-6
calibration-kind chain without that literal refuses at admission (typed refusal, before OFF).
Write a start-conditions record for G2-a too (same physical evidence fields as the derivation
record where they apply; no Revision 6 manifest). Do NOT change any Revision 6 behaviour: every
existing Revision 6 test must pass unchanged.

R2. **Producer ledger authentication (B2).** `generate_g2a_probe_inputs.py` refuses when the ledger
snapshot carries any refusal reason. Defect-shaped test: the 76-row stale ledger case refuses.

R3. **Pre-calibration screen (B3).** The G2-a chain's frozen `PRE_CAL_FIDUCIAL_MAX_S` literal(s) are
re-derived from the authenticated live acceptance through the writer's existing derivation
(`_derive_preflight_systematic_screen_s()` or its current name), never typed by hand. The
generator writes them, and `gen_g2_phase_d.py --check` FAILS when any rendered or source literal
differs from the value derived from the live acceptance (two-way check, as the window runbook §5B
requires). Update every source the G2-a chain renders from (find where the literal lives: the G2
runsheet and/or `docs/phase_2/window_runbook.md`); the G2-b region may be updated by the same
mechanism if it shares the source; do not hand-edit generated regions. Fix the stale comment text
naming `r3` next to the literal. Tests: stale literal → `--check` fails; regenerated → passes.

R4. **Installer render and launchd probe (B4, B5).** The G2-a chain gains, before any mutation
(mkdir, input check, reservation), the `NIGHT_VERIFY_ONLY=1` and `NIGHT_RESERVATION_ARGV_ONLY=1`
branches the installer and driver expect (`scripts/run_night.py` ~661,
`joulewise/night_agent_install.py` ~750-801, ~1295-1307): argv-only prints the reservation argv in
the same NUL-delimited form the derivation chain prints and exits 0 without mutation;
verify-only runs the reservation in its verify-only mode. The chain exports literal absolute
`CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN` (and any other coordinate the installer's probe needs)
for the specific clone, written by the generator from arguments (the generator gains the flags it
needs: measurement root, G2-a root, night root, plan id, t0 date). The installer's probe bindings
accept the G2-a chain's inspection surface (do not require `calibration_derivation_only.zsh` for
it), with the same strictness for the derivation chain as today. Tests prove: argv-only mutates
nothing (temp tree before/after identical) and prints the expected argv; installer render-only on
a G2-a fixture succeeds without executing the reservation; the derivation chain path is unchanged.

R5. **Typed calibration refusal (N4).** The G2-a chain exports `JOULEWISE_CALIBRATION_REFUSAL_PATH`
to the night directory's `calibration-refusal.json`, as the derivation chain does.

R6. **Plan authoring.** One recorded command authors a G2-a window end to end at the desk, so the
magistrate never edits a plan by hand: `scripts/gen_g2_phase_d.py --new-g2a-window` (or a small
new script; your choice, state it) taking t0 epoch, window_max_s, plan id, measurement root,
measurement head, night root, G2-a root, and writing the v2 `DIAGNOSTIC_NO_PACK` plan
(`joulewise.night_plan.v2`, schema_version 2, `registration_path` = the D-166 registration
`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`), the chain and its
sha256 sidecar, through the existing plan writer (`write_night_plan` or its current name). It
refuses: plan id/paths containing `codex`, `claude` or `t3` in any case; measurement root outside
`/Users/edr/night-custody/measurement/`; `window_max_s < NIGHT_PROGRAMMED_SPAN_S + 900`; t0 not
minute-aligned or less than 2400 s ahead. Print the schedule (install close, stand-down, t0,
latest chain start, window end, harvest open) as `run_night.py schedule` computes it.

R7. **Harvest (N5).** New `scripts/harvest_g2a_window.py` (100-250 lines plus tests), reusing
existing seams, never `harvest_window.py`'s derivation-only paths. It refuses before
`t0 + window_max_s + 300`, without the courier's delivery marker, or while any process of the
chain's process group is alive. Then: (1) archive night custody, the complete G2-a root, the
clone's physical ledger and head pin to `--archive-root` with a `SHA256SUMS` (byte copy, verify
after copy); (2) authenticate the frozen inputs (`generate_g2a_probe_inputs.py check` path) and the
roster (4 rungs × 5 small + 4 × 1 large, exact config ids); (3) authenticate the pre and post
bracket custody and the bracket verdict through the existing bracketing code
(`joulewise/calibration_bracketing.py`), including drift against the live acceptance;
(4) strictly validate every member bundle from raw evidence (existing strict validator,
`joulewise/cli.py` ~392); (5) regenerate the counts receipt and four-row summary in scratch with
`summarize_g2a_prefill_probe.py` and require byte equality with the chain's outputs (or produce them
if the chain stopped before writing them); (6) network-time report: the OFF receipt's admitted
statement and both clocks; for every capture, its within-capture clock-movement outcome (the
estimator's existing anchor admission) and, where the receipt and the capture record comparable
wall and monotonic readings from the same monotonic source, the difference between the receipt's
wall-minus-monotonic offset and the capture's, flagged when above 0.015 s (report only; say
"not comparable" rather than inventing a comparison when the sources differ); (7) a mechanical
verdict, written as JSON: `SELECT` (both brackets pass and every rung has ≥5 valid small-model
members: run `select_g2a_prefill_length.py` on the authenticated summary and record its output
path and sha256), `RECOVER` (anything else that leaves the window incomplete: a pre-screen stop, a
post-bracket failure, any rung with <5 valid small members, a chain nonzero exit; name the cause
code), or `REFUSED` (archive/authentication failure: a tooling fault, never a science outcome);
(8) the ledger head-pin advance through the governed terminal-pin procedure
(`recover_calibration_ledger.py`), as a file change the operator commits, exactly as the Revision 6
harvest does. The harvest's stdout prints paths, shas, counts of members and the verdict, NEVER an
energy, a fiducial bound, a drift value or a per-member sample count (those stay in the files).
A prefill phase with fewer than 3 overlapping records is a reducer outcome
(`not_resolvable_sample_count`), not a member failure: prove with a test that such a member is a
VALID member with its count recorded, that the campaign does not stop on it (`--max-failures 1`),
and that the summary and selector treat it per D-166. If the code instead fails the member or stops
the chain on it, STOP and report that as `NEEDS_RULING` with file:line; do not change capture or
reducer code.

R8. **Ledger seed (B1)** is an arm-recipe setting (the retained C2 ledger, 376 rows), not code. Make
no code change for it; do make sure the producer/reservation refuse the stale 76-row ledger (R2).

## Fences

- Never edit the four pinned estimator files (`joulewise/powermetrics_fiducial.py`,
  `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`),
  `scripts/validate_powermetrics_fiducial.py`, `scripts/night_chains/**`, any file under
  `configs/calibration/`, `configs/campaigns/**`, the Revision 6 registration, or `run_campaign.py`
  capture behaviour. If a fix seems to need one of them, stop and report `NEEDS_SCOPE`.
- No new enforcement beyond what the rulings name. Prefer one literal or one flag over machinery.
- Every existing test must pass; add defect-shaped tests for each ruling (a test that fails when the
  fix is removed).

## Verify before you report

Run: `tests.test_gen_g2_phase_d` (or the module that tests the generator), `tests.test_run_night*`,
`tests.test_night_agent_install*`, `tests.test_night_gate*`, `tests.test_generate_g2a_probe_inputs*`,
`tests.test_summarize_g2a_prefill_probe*`, `tests.test_select_g2a_prefill_length*`,
`tests.test_harvest_window`, `tests.test_gen_derivation_night`, `tests.test_check_window_provenance`,
every new module, and `python -B scripts/gen_g2_phase_d.py --check`. Emit a G2-a chain and plan
into `/tmp/g2a-lane/` with the new command and show `zsh -n` passes, `run_night.py preflight --plan`
passes, and `NIGHT_RESERVATION_ARGV_ONLY=1 NIGHT_VERIFY_ONLY=1` argv-only run of the chain mutates
nothing. Report exact test tails.

## Output

Your wrapper's report envelope: what changed (file, purpose, lines), each ruling R1-R8 with its test
names, verification tails, any `NEEDS_RULING`/`NEEDS_SCOPE`, and the final `NIGHT_PROGRAMMED_SPAN_S`
arithmetic.

WRITE_SCOPE: ["scripts/gen_g2_phase_d.py", "scripts/generate_g2a_probe_inputs.py", "scripts/run_night.py", "joulewise/night_agent_install.py", "joulewise/night_gate.py", "scripts/harvest_g2a_window.py", "scripts/summarize_g2a_prefill_probe.py", "scripts/select_g2a_prefill_length.py", "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md", "docs/phase_2/window_runbook.md", "tests/**", "scripts/test_timings.json"]
