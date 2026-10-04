# Executing review: PR #467 (G2-a harvest judges the bracket against the acceptance cutoff)

Worktree: `/Users/edr/code/JouleWise-wt-df31-review`, detached at `96747ff0` (branch `fix/2026-10-04-g2a-b3w1-bracket-baseline`; parent main `a6c7f9cf`). This is a read-only review: do not edit tracked files and do not commit. Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python -B`, run from the worktree root so the worktree's code is imported. Scratch: `/tmp/df31-review/` only. Never run powermetrics, sudo, launchctl or a model. Never read `summary*.json`, `counts*.json`, `selection*.json` or `bracket*.json` under `/Users/edr/night-g2a`, `/Users/edr/night-custody` or `/Users/edr/night-archive`. Do not read GitHub PR bodies.

## What the change is for

`scripts/harvest_g2a_window.py` decides the verdict of a G2-a diagnostic window. Block-3 window b3w1 was the first G2-a window whose calibration bracket session (a pulse calibration before and after the measured members) finalized. Its harvest returned RECOVER with the single cause `calibration_ledger_baseline_missing`. `joulewise/calibration_bracketing.py` (around 2208-2220) requires the ledger snapshot's baseline to equal the acceptance artifact's `ledger_cutoff`. The harvest passed the window's seed head (the frozen `calibration_plan.json` `calibration_ledger.head_*`) instead. Every other caller (`joulewise/whole_window.py:507-522`, `scripts/run_campaign.py:~4819`, `scripts/generate_g2a_probe_inputs.py:~677`) passes the cutoff.

Requirements:
1. The seed-head authentication (committed pin) and the terminal-head scratch-pin authentication are unchanged in strength and in refusal behaviour.
2. The bracket session lookup, `build_calibration_bracket_binding` and `calibration_bracket_for_bundles` receive a snapshot of the same physical ledger and the same selected pin, with baseline = the cutoff of the acceptance the bracket decision itself uses (`load_calibration_acceptance_bound()`, the default).
3. That acceptance must be the plan's `active_acceptance`: file-byte sha256, the same function the generator used to write the field, and the same id. Otherwise `HarvestRefusal('bracket_acceptance_plan_mismatch')`.
4. A refusal of the bracket-view snapshot remains a RECOVER cause and is never filtered or turned into SELECT.
5. Open-session (governed open extension), no-session, block-2-style and NULL archives still harvest exactly as before.

## Execute (an executing lens: run the code, do not only read it)

- Read `git diff a6c7f9cf..96747ff0`. Run `tests.test_harvest_g2a_window tests.test_calibration_bracketing tests.test_generate_g2a_probe_inputs tests.test_custody_mode_inventory`, plus any other module that imports `scripts.harvest_g2a_window` (grep for it).
- Mutation probes on a scratch copy (`cp -R` the worktree to `/tmp/df31-review/mut-N`; never edit the review worktree):
  (a) revert the bracket view's baseline to the seed head;
  (b) drop the acceptance sha check;
  (c) drop the acceptance id check;
  (d) filter the bracket-view snapshot's refusal reasons to empty;
  (e) build the bracket view on the committed pin even when the session is finalized;
  (f) compute the acceptance sha with a JSON re-serialization instead of file bytes.
  For each probe, say whether some test fails. A surviving mutation is a finding.
- Trace the open-session path: with `bracket_pin = pin` and the cutoff baseline, what are the snapshot's refusal reasons and `bracket_session_by_id`? Does the captures list for the network-time report change compared with `a6c7f9cf`? Show this with a test or a scratch run on fixtures.
- Check whether `binding = None` (now possible when the snapshot has refusal reasons) can make `calibration_bracket_for_bundles` return anything other than a failed status with reasons.
- Real-data smoke (blinded): on a scratch copy of `~/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z/` (`cp -R` to `/tmp/df31-review/arch`), run `scripts/harvest_g2a_window.py --help`. If the script can re-harvest from an archive copy with `--read-only-sources`, do so into `/tmp/df31-review/rh` and report ONLY the verdict string, the cause codes and the process exit code. Never print selection, counts, summary or bracket numbers. If it cannot run from a copy, say so and skip this step.

## Output

A `claude-codex-report/v1` review whose first line is `REVIEW: PASS` or `REVIEW: FAIL`. Give findings, each as {severity BLOCKER|MAJOR|MINOR|NIT, file:line, claim, evidence (command and result)}, then the mutation table. At most 1000 words.

## Write scope (exhaustive)

WRITE_SCOPE: []
