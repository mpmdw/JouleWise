You are giving a cold final pass on one change before merge. You have no prior context. Your working directory is a detached checkout of `a1133594` (branch feat/2026-10-04-v5-floor-prefill-from-pin, PR #472); its parent on main is `8fa002f7`. Read `git diff 8fa002f7..a1133594` and the surrounding code. You may run read-only commands, the generators into scratch, and unit tests with `/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider <files>` from this directory.

Rules:
- Scratch: /tmp/dd5-fable-fl/ only (set TMPDIR there). Do not edit files in the checkout, and do not run git commands that write.
- Never run powermetrics, sudo, launchctl or a model. Never write under /Users/edr/night-archive, /Users/edr/night-g2a or /Users/edr/night-custody.
- Do not read RUN_STATE.md, CLAUDE*.md, memory or skill files, and do not read GitHub pull-request bodies.
- One non-interactive session, every command in the foreground, no background task or subagent. Budget 50 minutes. Ending before your ruling file exists is a protocol failure.
- Write your ruling to /Users/edr/night-archive/desk-day-v5/fable-floors.md; first line `FINAL PASS: PASS` or `FINAL PASS: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and evidence. Do not print the selected prefill length.

What the change is for:
- JouleWise measures LLM inference energy on a Mac. The `_v5` campaign has two "floor" packs (`configs/campaigns/d117_floor_qwen3-1p7b_v5/`, `..._qwen3-8b_v5/`, one per model) and one contrast pack. Decision D-166 fixes the campaign's prefill prompt length from a diagnostic probe through an issued "prompt pin" (`joulewise.prefill_prompt_pin.v2`); decision D-117 puts the prefill floor cells on the floor windows, so the floors must measure the same prefill length as the contrast. The floors hardcoded 512 and refused any other pin; the probe selected another rung of the ladder 512/1024/2048/4096.
- The change: the floors read the length from the authenticated pin only (and accept the probe's end-state 4096 record); bind the calibration acceptance in force (`d079_calibration_acceptance_v2_n24_25g83_r2`, registry in `joulewise/calibration_bracketing.py`) instead of one from the previous OS epoch, with the acceptance's ledger cutoff (not the live head) as the ledger literal; the paper's reported-energy registry (`joulewise/paper_reported_energy.py`, contract `docs/contracts/paper_reported_energy.md`) gains prospective `prefill-p<L>` reported cells for each ladder rung, one length per family, with historical p512 registrations byte-identical; span planning constants become a component estimate (only the prefill phase scales with length). A non-author executing review passed it.

Judge as the last reviewer before merge on code that defines what the claim windows measure and how the paper names it:
1. Can a floor pack be generated whose prefill members do not carry exactly the pin's token ids and length, or whose length differs from the contrast pack's pin? Is there any path back to a hardcoded 512?
2. Is the acceptance binding exactly the registry's live default, and is the ledger literal the acceptance cutoff? What would break at arm/freeze/whole-window time if it were wrong?
3. Do historical p512 registrations, digests and replays stay byte-identical? Can a family mix lengths or alias a longer prompt to `p512`?
4. Are the span planning constants only planning (no consumer turns them into a limit)?
5. Do the tests kill the regressions they claim?
