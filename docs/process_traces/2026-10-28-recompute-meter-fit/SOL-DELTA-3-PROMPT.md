BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "review",
 "ROLE": "execution-lens delta reviewer (Sol half of gate-policy rule 3) of the comparator's structural fix round",
 "OBJECTIVE": "Return ACCEPT / ACCEPT_WITH_FIXES / REJECT on scripts/compare_b5_recompute.py at lane/2026-10-27-recompute-comparator 7fede8c7 (RC-CMP-5, e5ccf720b..7fede8c7), backed by executed evidence.",
 "AUTHORITY": ["docs/process/gate_policy.md (binding)", "RUN_STATE.md items 86, 87, 91, 94", "docs/process_traces/2026-10-28-recompute-meter-fit/FIX-BRIEF-2.md", "docs/contracts/bridge_protocol.md"],
 "WRITE_SCOPE": [".codex-report/RC-CMP-SOL-REV-3.md", ".codex-report/rc-cmp-sol-rev-3/"],
 "ACCEPTANCE": ["Report on a new branch review/2026-10-29-rc-cmp-sol-rev-3 cut from 7fede8c7, with a verdict line and ranked findings backed by executed commands", "Answers 1-3"],
 "VERIFICATION": ["JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t ."],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

Origin: Claude Code lead (laptop), launched in Codex Cloud by the measurement Mac's orchestrator at a desk. Hop depth 1: do not call Claude by MCP, claude -p, or any launcher.

Context. Your two earlier reviews (review/2026-10-28-rc-cmp-sol-rev REJECT, review/2026-10-28-rc-cmp-sol-rev-2 REJECT) and Opus's (review/2026-10-28-rc-cmp-opus-rev, -rev-2) found false-agreement paths twice. RC-CMP-5 replaced case-by-case logic with structural rules (report .codex-report/RC-CMP-5.md): S1 numbers denied by default; S2 bindings built only from structural position, with every routing id compared; S3 one union helper (Comparison.pairs) and one key space. Lead rulings kept as designed: public per-family pass/fail counts; BETA extra sessions not compared. An Opus delta reviews the same head in parallel; you do not see its result. Synthetic data only; never open or search for real block-5/6/BYTES data.

1. Rerun every probe from all four earlier reviews against 7fede8c7 (git archive origin/<branch> .codex-report/<dir> | tar x): does each fail (refusal or DISAGREE)?
2. Attack the structural rules: numeric content reaching an uncovered rule (numbers in strings, booleans, nested lists, empty containers); a key still routed by a leaf's own value; any collection compared outside Comparison.pairs (check the AST test); duplicate keys across families; uncovered-by-name or uncovered-null-by-name rules broad enough to hide a printed number.
3. Over-refusal on a real full-size window with no defect (a legitimately null registered value, list order, a routing id spelled differently on the two sides): what evidence settles it? RC-CMP-4 (report/2026-10-28-rc-cmp-4) is the full-size synthetic rerun.

Push the report to review/2026-10-29-rc-cmp-sol-rev-3 only; never main, no force push, no PR. TMPDIR outside the checkout with no float-like token in the path. Do not run L9's full-size test_dry_run.
