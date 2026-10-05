You are giving a cold final pass on one change before merge. You have no prior context. Your working directory is a detached checkout of `0636046c` (branch feat/2026-10-04-g2b-one-block-stop, PR #474); its parent on main is `8fa002f7`. Read `git diff 8fa002f7..0636046c` and the surrounding code. You may run read-only commands and unit tests with `/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider <files>` from this directory (e.g. `tests/test_run_campaign_max_blocks.py tests/test_gen_g2_phase_d.py`).

Rules:
- Scratch: /tmp/dd5-fable-gs/ only (set TMPDIR there). Do not edit files in the checkout, and do not run git commands that write.
- Never run powermetrics, sudo, launchctl or a model.
- Do not read RUN_STATE.md, CLAUDE*.md, memory or skill files, and do not read GitHub pull-request bodies.
- One non-interactive session, every command in the foreground, no background task or subagent. Budget 45 minutes. Ending before your ruling file exists is a protocol failure.
- Write your ruling to /Users/edr/night-archive/desk-day-v5/fable-g2bstop.md; first line `FINAL PASS: PASS` or `FINAL PASS: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and evidence.

What the change is for:
- JouleWise measures LLM inference energy on a Mac in unattended "windows". `scripts/run_campaign.py` runs a pack's members in A/B/B/A blocks (A = small model, B = large model) and is the chain every claim window runs. The real-pack shakedown "G2-b" must collect exactly ONE complete A/B/B/A block, non-claim, unattended, then take the post-bracket calibration path. Before this change its chain (rendered by `scripts/gen_g2_phase_d.py` into the runsheet/runbook) waited for an operator's SIGINT (rc 130) and nothing enforced `permitted_blocks` at run time.
- Now `run_campaign.py --max-blocks N` (bound to the authenticated authorization's `permitted_blocks`; the CLI cannot widen it) stops between members after N complete, strict-valid blocks, writes a terminal `max_blocks_reached` row and exits rc 3; a bounded run refuses a failure budget other than 1 (no top-up after a failed member, decision D-078). The G2-b chain uses it; the shared `run_stage` shell helper propagates rc explicitly. A non-author executing review found the unbounded path byte-identical to main and no false rc 3 in 28 adversarial cases.

Judge as the last reviewer before merge on code in the claim-window chain:
1. Without the flag/bound, is behaviour (log, rc, artifacts) identical to main?
2. Can rc 3 or the stop row appear without N complete strict-valid blocks? Can a member be cut mid-run?
3. Is the bound read from authenticated bytes, and can it be widened?
4. Does the re-rendered G2-b chain still run the post-bracket path after rc 3, and is the G2-a chain's behaviour unchanged by the `run_stage` edit?
5. Do the tests kill the regressions they claim?
