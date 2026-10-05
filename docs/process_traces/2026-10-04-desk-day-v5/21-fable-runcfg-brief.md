You are giving a cold final pass on one change before merge. You have no prior context. Your working directory is a detached checkout of `2a682b2e` (branch fix/2026-10-04-run-config-normalized-pin, PR #470); its parent on main is `8fa002f7`. Read `git diff 8fa002f7..2a682b2e` and the surrounding code. You may run read-only commands and unit tests with `/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider <files>` from this directory (e.g. `tests/test_window_duration_margins.py tests/test_custody_mode_inventory.py`).

Rules:
- Scratch: /tmp/dd5-fable-rc/ only. Do not edit files in the checkout, and do not run git commands that write.
- Never run powermetrics, sudo, launchctl or a model.
- Do not read RUN_STATE.md, CLAUDE*.md, memory or skill files, and do not read GitHub pull-request bodies.
- One non-interactive session, every command in the foreground, no background task or subagent. Budget 45 minutes. Ending before your ruling file exists is a protocol failure.
- Write your ruling to /Users/edr/night-archive/desk-day-v5/fable-runcfg.md; its first line is `FINAL PASS: PASS` or `FINAL PASS: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and evidence (code read, or a command you ran and its output).

What the change is for:
- JouleWise measures LLM inference energy on a Mac. A "pack" is a frozen set of run configs; each run writes a bundle whose `config.json` the runner produces by parsing the input config (`BenchmarkConfig.from_mapping`) and re-serializing it (`config.to_dict()`, `joulewise/bundle.py` ~950), with the hash in the bundle's `metadata.json` `config_sha256`. The pack pins sha256 of the SOURCE config bytes.
- `joulewise/window_duration_margins.py` (used by `scripts/record_window_duration_margins.py` after a pack window) authenticated each member by comparing sha256(<run>/config.json) with the pack pin, so every real member was refused `member_config_mismatch`. The change locates each member's source config through the authenticated plan tree's science rows, requires its bytes to match the pin, requires the run's config.json hash to equal the runner-normalized hash of the parsed source (`joulewise/controller.py` `_config_sha256`), and requires metadata to bind the run config hash. A reviewer found that the second plan-tree read was not bound to the first's digest; the second commit binds it.

Judge as the last reviewer before merge on code that admits or refuses measured bundles:
1. Is any member that would be refused under a sound reading now admitted? (Two source configs that normalize to the same run bytes; a source path resolved outside the pack or repository; symlinks; a plan tree changed between reads; GAMMA versus floor source roots; metadata mismatch.)
2. Is `_config_sha256` exactly the serialization the bundle writer used? Any version/default-filling drift that would make a valid member refuse?
3. Do the tests kill the regressions they claim (the old byte comparison; a one-field source edit; a post-run config edit; the tree-binding)?
