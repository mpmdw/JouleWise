# Seat: `_v5` throwaway-clone re-proof (freeze, arm-admission, receipt) on the generated packs — DESK EVIDENCE ONLY

You are a headless Claude Opus 5.5 seat. One non-interactive session; every command in the foreground (anything longer than 9 minutes: split it, or run it with `python3 -c 'import subprocess…Popen(…, start_new_session=True)'` and poll in loops of at most 9 minutes). No subagents, no background tasks left running at the end. Ending before `/Users/edr/night-archive/desk-day-v5/clone-proof/REPORT.md` exists is a protocol failure. Wall budget: 5 hours; if not finished, write REPORT.md with status IN_PROGRESS and the exact next step.

## Hard rules
- No sudo, launchctl or powermetrics. Never arm or launch a real window; never consume a launch capability; never run a window chain. Never write under /Users/edr/night-g2a, /Users/edr/night-custody, /Users/edr/night-archive (except /Users/edr/night-archive/desk-day-v5/clone-proof/), or in /Users/edr/code/JouleWise or any existing worktree. Do not push anything; do not `git fetch` in /Users/edr/code/JouleWise.
- Do not read RUN_STATE.md, CLAUDE.local.md or memory files. Do not print or record measured energy values.
- Work only in fresh clones under /tmp/dd5-clone/ (`git clone --no-local /Users/edr/code/JouleWise /tmp/dd5-clone/<name>` then `git -C … checkout --detach 24741cab…` — use the full sha of branch `desk/2026-10-04-v5-pin-and-packs` head: `git -C /Users/edr/code/JouleWise rev-parse 24741cab`). Custody for all outputs: /tmp/dd5-clone/custody/ and copies of every receipt/report into /Users/edr/night-archive/desk-day-v5/clone-proof/.
- Python: /Users/edr/code/JouleWise/.venv/bin/python.

## What exists
Branch `desk/2026-10-04-v5-pin-and-packs` (head 24741cab) = main b3ef116d + the two reviewed producer fixes (PRs #472, #473, not yet merged to main) + the issued prefill prompt pin (`configs/campaigns/d117_contrast_v5/prefill_pin/`, pin sha256 d1209f6d…) + the three generated `_v5` packs: `configs/campaigns/d117_floor_qwen3-1p7b_v5`, `configs/campaigns/d117_floor_qwen3-8b_v5`, `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` (unfrozen drafts; all generators' `--check` pass).

## Procedure (from the read-only scout, /Users/edr/night-archive/desk-day-v5/sol-scout.md §3 — READ IT FIRST, and the templates it cites: `docs/process_traces/2026-08-30-t28-estate11/estate-12-delta-template.md`, `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md`, `docs/phase_2/window_runbook.md` ~284-392)
1. Clone; derive estate anchors (`scripts/derive_estate_anchors.py`).
2. Identity projection: `scripts/project_identity_pins.py freeze <pack>` for each of the three packs (real runtime/model/tokenizer identity; models are local under /Users/edr/jw_models). Commit in the clone.
3. Pre-author tests (`tests.test_arm_readiness_schemas tests.test_receipt_histsem tests.test_mint_analysis_admission tests.test_d117_contrast_v5_pack tests.test_d117_floor_qwen3_v5_generate`), then evidence authoring for each pack at one derivation head (`scripts/author_arm_readiness_evidence.py --pack-root … --measurement-checkout <clone>`); one evidence commit.
4. Sacrificial freeze in a second clone first; then the primary freeze for each pack with its ruled predecessor (`scripts/generate_arm_readiness.py freeze --pack-root … --measurement-checkout … --predecessor-pack-root …`; mappings: floor 1.7B ← `d117_floor_qwen25_1p5b_v3`, floor 8B ← `d117_floor_qwen25_7b_v3`, contrast ← `d117_contrast_qwen25_1p5b_vs_7b_v3`; expected receipt `freeze-0004`). A refused freeze poisons that clone: start a fresh clone rather than rewriting.
5. Histsem pinset + verify, family marker build + verify, as the scout lists (find the reviewed base pinset and candidate manifest inputs; do not guess file names — if an input does not exist, stop that step and report it).
6. Arm/verify only as far as possible WITHOUT live prerequisites: a governed refusal receipt is the expected outcome where a live T-0 fact is required (S0 runsheet ~2477-2480); record exact return codes and reason codes. Then `scripts/author_arm_evidence_t0.py --pack-root … --custody-root …` for the A196 dry gate, expecting `evidence_author_t0_clock_attestation_missing`.

At every step record: command, rc, refusal/reason codes, receipt paths and sha256s. Any refusal that is NOT the expected governed refusal is a FINDING: diagnose it to file:line (read-only), say whether it is a pack/generator defect, a procedure/doc defect, or an environment limit, and continue with the next pack/step where possible.

## Report
`/Users/edr/night-archive/desk-day-v5/clone-proof/REPORT.md`: first line `CLONE PROOF: PASS` (every step reached its expected outcome), `CLONE PROOF: FINDINGS` or `CLONE PROOF: IN_PROGRESS`; then a step table (step, pack, command, rc, outcome, expected?), findings with file:line, the clone heads/commits you created (local only), and the exact commands a lead would rerun at the final claim head.
