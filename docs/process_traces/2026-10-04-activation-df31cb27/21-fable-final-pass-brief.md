You are giving a cold final pass on one commit before merge. You have no prior context. Your working directory is a detached checkout of `96747ff0` (branch fix/2026-10-04-g2a-b3w1-bracket-baseline, PR #467); its parent on main is `a6c7f9cf`. Read `git diff a6c7f9cf..96747ff0` and the surrounding code. You may run read-only commands and the unit tests with `/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest <modules>` from this directory (for example `tests.test_harvest_g2a_window tests.test_calibration_bracketing tests.test_custody_mode_inventory`).

Rules:
- Scratch: /tmp/df31-fable/ only.
- Do not edit files, and do not run git commands that write.
- Never run powermetrics, sudo, launchctl or a model.
- Do not read RUN_STATE.md, CLAUDE*.md, memory or skill files, and do not read GitHub pull-request bodies.
- Never open `summary*.json`, `counts*.json`, `selection*.json` or `bracket*.json` under /Users/edr/night-g2a, /Users/edr/night-custody or /Users/edr/night-archive.
- One non-interactive session, every command in the foreground, no background task or subagent. Budget 45 minutes.

What the commit is for:
- The JouleWise energy-measurement project's G2-a prefill probe is a diagnostic window. Each window's measured members are bracketed by a pulse calibration before and after, recorded in an append-only calibration ledger. `scripts/harvest_g2a_window.py` assigns the window a verdict (SELECT, RECOVER, NULL or REFUSED). The registration says the brackets pass when the existing bracketing decision (`joulewise/calibration_bracketing.py`), judged against the acceptance in force, admits both.
- The latest window was the first whose bracket session finalized. Its harvest returned RECOVER with the single cause `calibration_ledger_baseline_missing`. `calibration_bracketing.py` (around 2208-2220) requires the ledger snapshot's baseline to equal the acceptance artifact's `ledger_cutoff` (sequence 376 for the acceptance in force). The harvest built its snapshot with the window's seed head (sequence 392) as baseline. The other callers (`joulewise/whole_window.py`, `scripts/run_campaign.py`, `scripts/generate_g2a_probe_inputs.py`) use the cutoff.
- The commit keeps the seed-head and terminal-head custody snapshots. It adds a third snapshot with the cutoff baseline for the bracket decision. It binds the acceptance to the plan's `active_acceptance` by file sha256 and id, and refuses on a mismatch.

Judge as the last reviewer before merge on code that decides the verdict over measured bundles:
1. Is the bracket now judged against exactly the acceptance the window was planned under, with no path to a different acceptance, a different ledger, or a different pin?
2. Is any custody check weakened? Could a tampered, truncated or rolled-back ledger, or a ledger whose cutoff entry differs, now reach a passed bracket?
3. Could the new view make a bracket pass that the registration would call failed, or fail one it would call passed? This includes the open-session and no-session paths and the case where the bracket-view snapshot has refusal reasons (the binding is then None).
4. Do the tests actually kill the regressions they are meant to catch (seed-head baseline, sha check, id check)?
5. Any other defect that would make a verdict wrong.

Answer with a first line of exactly `FINAL PASS: PASS` or `FINAL PASS: FAIL`. Then give your findings, each with a severity (BLOCKER, MAJOR, MINOR or NIT), the file:line, and evidence (what you ran). Keep it under 800 words.
