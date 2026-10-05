# Seat: `_v5` throwaway-clone re-proof, round 2, at main b2ff2f36 (desk evidence only)

You are a headless Claude Opus 5.5 seat. One non-interactive session; every command in the foreground. Anything longer than 9 minutes is split, or launched with `python3 -c 'import subprocess,sys; subprocess.Popen(sys.argv[1:], stdout=open(LOG,"w"), stderr=subprocess.STDOUT, start_new_session=True)'` and polled in loops of at most 9 minutes. No subagents and no background work left running at the end. Ending before `/Users/edr/night-archive/desk-day-v5/clone-proof2/REPORT.md` exists is a protocol failure. Wall budget: 4 hours; if not finished, write REPORT.md with status IN_PROGRESS and the exact next step.

## Hard rules
- No sudo, launchctl or powermetrics. Never arm or launch a real window, never consume a launch capability, never run a window chain. Never write under /Users/edr/night-g2a, /Users/edr/night-custody, /Users/edr/night-archive (except /Users/edr/night-archive/desk-day-v5/clone-proof2/), in /Users/edr/code/JouleWise or in any existing worktree. Push nothing. No `git fetch` in /Users/edr/code/JouleWise.
- Do not read RUN_STATE.md, CLAUDE.local.md or memory files. Never print or record a measured energy or power value.
- Work only in fresh clones under /tmp/dd5-clone2/: `git clone --no-local /Users/edr/code/JouleWise /tmp/dd5-clone2/<name>` then `git -C /tmp/dd5-clone2/<name> checkout --detach b2ff2f3632e916bc4b7d3cccd037b52e19c34c01`. Custody: /tmp/dd5-clone2/custody/, with copies of every receipt and report in /Users/edr/night-archive/desk-day-v5/clone-proof2/.
- Python: /Users/edr/code/JouleWise/.venv/bin/python.

## Why this is being rerun
Round 1 (`/Users/edr/night-archive/desk-day-v5/clone-proof/REPORT.md`; read it first, it lists every command) stopped at evidence authoring on two blockers. Both are now fixed on main: F1 (floor decode identity unit missing `prompt_tokens`) by PR #476, and F2 (freeze evidence still required the retired network-time restore step) by PR #479, which replaced the live row with `clock.network_time_policy`. Main b2ff2f36 also carries PR #477: the issued prefill prompt pin (`configs/campaigns/d117_contrast_v5/prefill_pin/`) and the three generated `_v5` packs (`configs/campaigns/d117_floor_qwen3-1p7b_v5`, `configs/campaigns/d117_floor_qwen3-8b_v5`, `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`). Nine evidence kinds were never exercised in round 1, including PACK_AUTHENTICATION for the contrast pack (PR #473's repair).

## Procedure
Repeat round 1's steps 1 to 6 exactly as its REPORT lists them (anchors; generator `--check`s; identity projection per pack, committed in the clone; the five pre-author test modules; evidence authoring per pack at one derivation head and one evidence commit; sacrificial freeze in a second clone, then the primary freeze per pack with its ruled predecessor and expected `freeze-0004`; histsem pinset and verify; family marker build and verify; arm as far as possible without live prerequisites, expecting a governed refusal receipt; the A196 dry gate expecting `evidence_author_t0_clock_attestation_missing`). This time no blocker is expected before freeze.

At every step record the command, rc, refusal and reason codes, receipt paths and SHA-256s. Any outcome other than the expected one is a FINDING: diagnose it to file:line (read-only), classify it (pack or generator defect, procedure or doc defect, environment limit), and continue with the next pack or step where possible. A refused freeze poisons its clone: start a fresh clone rather than rewriting history.

## Report
`/Users/edr/night-archive/desk-day-v5/clone-proof2/REPORT.md`. First line `CLONE PROOF: PASS` (every step reached its expected outcome), `CLONE PROOF: FINDINGS` or `CLONE PROOF: IN_PROGRESS`. Then a step table (step, pack, command, rc, outcome, expected?), the findings with file:line, the clone commits you created (local only), and the exact commands a lead would rerun at the final claim head.
