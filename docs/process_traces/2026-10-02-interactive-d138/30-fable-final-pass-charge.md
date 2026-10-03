# Cold Fable 5.1 final pass: the D-138 issuance transaction, epoch 25G83 Revision 6 block 1

You are a COLD final-pass judge (Fable 5.1): fresh session, no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.** One non-interactive session, every command in the foreground, no background task, no subagent; ending your turn before your output file exists is a protocol failure. Read-only except your output file and scratch `/tmp/d138-rev6-fable/`. No sudo, launchctl, powermetrics, systemsetup; no git write, fetch or checkout. Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python -B`. Budget 60 minutes.

Working directory: a fresh detached worktree at the PR head HEAD_SHA; base origin/main BASE_SHA. Read the diff with `git diff BASE_SHA HEAD_SHA -- . ':!docs'` and the records under `docs/process_traces/2026-10-02-interactive/` (items 40–42) and `docs/process_traces/2026-10-02-interactive-d138/`.

## The question

This merge makes `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` the live calibration that judges 25G83 measurements. Can any defect in the merge code make a number, a member, an admission decision, or the live default wrong, or make a claim-bearing result rest on bytes other than those the cold science gate admitted?

Check, by execution where you can:
1. The issued file is the admitted candidate (sha256 aa59ebb2…9884, ruled ADMIT in `docs/process_traces/rev6-derivation-block1/packet/RULING-judge.md`) changed only in issuance fields: every member, statistic, operative, the cutoff, the prior set and `derivation_input_sha256` byte-identical; `derivation_sha256` recomputes.
2. The promotion tool's Revision 6 entry refuses wrong candidates, wrong or incomplete issuance text and drifted seals, and leaves the retired r1 entry's behaviour unchanged.
3. Registration and the default move: the registry digest, the generation row (equal to the file's `registered_generation_row`), the admission set and the pinset schema; earlier generations still authenticate; the default loads and validates; a 25G83 identity is fresh and a 25F84 identity stale against it.
4. Every pin that named P8 as the live default moved, and every pin that names P8 as P8 (Revision 6's sealed predecessor, its fixtures, P8's own authentication) stayed: `docs/process_traces/2026-10-02-interactive-d138/06-pin-classification.md`.
5. Erratum E-NT1 (`42-erratum-nt1.md`) and the issuance text (`10-issuance-text.json`, disclosures D1–D10) state the facts the rulings and the code support. D10 defers the explicit 25F84 re-evaluation route to lane A335: say whether that deferral leaves any path that silently judges a recorded 25F84 result against the 25G83 file.
6. The four pinned estimator files, `scripts/validate_powermetrics_fiducial.py`, the night chains, the sealed registration and the disposition registry are untouched.

## Output

Write `docs/process_traces/2026-10-02-interactive-d138/31-fable-final-pass.md` in this worktree. Its **first line** is exactly `FINAL PASS: MERGE` or `FINAL PASS: BLOCK`. Then the contamination disclosure, a table of executed checks (command, result), findings each as {severity blocker|major|minor|nit, file:line, claim, evidence}, and a 3-line plain summary. BLOCK only for a defect of the kind the question names.
