SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

POST-MERGE CROSS-UNIT INTEGRATION REVIEW of main at 18ab2cc4 (merge of PR #322 NIGHT-C1-REGISTRATION-DOCS-01, branch head 2c25eccb; gate ledger row 11's second half). Read-only in this detached worktree (/Users/edr/code/JouleWise-wt-postmerge-322); temp files only under /tmp. Read the PR body (gh pr view 322 --repo mpmdw/JouleWise --json body --jq .body) and the terminal review /Users/edr/code/JouleWise-wt-bk-36d3a823/docs/process_traces/2026-09-11-activation-3dab9c89/18-terminal-review-pr322.md, then 'git diff 4c06b3b4..18ab2cc4 --stat' and the full diff.

The question is INTEGRATION, not re-review of the unit: does the merged unit interact badly with anything else on main that the branch-scoped reviews could not see? PR #321 (night interpreter pin: installer --python flag, plist template, driver MIN_PYTHON guard, runbook interpreter paragraphs) merged to main as 4c06b3b4 BEFORE this PR; both PRs edited docs/phase_2/derivation_night_runbook.md and the branch merged main at baf7b900 (before #321), so the runbook on main is the first place the two units meet.
1. Runbook coherence after both merges: read docs/phase_2/derivation_night_runbook.md on main end to end for §0.5, §1.1, §1.4, the arm block, §2.5, §5 and the interpreter/--python paragraphs from #321. Any duplicated, contradictory, or orphaned paragraph (e.g. an arm block that names the plist interpreter one way and the C1 registration_path another; a step numbering that no longer follows)? List file:line.
2. Gate constant vs plan writer vs runbook: does joulewise.night_gate's D166_REGISTRATION_PATH (find it) equal the literal the runbook's arm block tells the operator to put in the plan, and does joulewise.night_plan_writer.write_night_plan accept/emit registration_path in the field the gate reads? Does scripts/gen_derivation_night.py's example plan agree? Run `python3 scripts/gen_derivation_night.py --check` at 18ab2cc4 and paste the outcome.
3. NIGHT_HANDBACK procedure (docs/phase_2/NIGHT_HANDBACK.md) on main: does its plan-authoring step name registration_path at all, and if so does it agree with the gate constant for REHEARSAL_STUB / DIAGNOSTIC_NO_PACK? If the procedure and the runbook disagree, that is a SHOULD_FIX with exact lines.
4. Kernel drift: run the CI-defined kernel check (find it in .github/workflows/ci.yml) at 18ab2cc4; paste the outcome.
5. Run the focused modules the PR touched (tests/test_gen_derivation_night.py, tests/test_night_gate.py) plus every test module that imports the changed modules (grep -l); paste counts. Do NOT run the full suite.
6. Docs: any process doc on main (RUN_STATE.md, docs/process/*.md, TASK_QUEUE.md, docs/phase_2/*.md, docs/contracts/*.md) that still binds the equivalence-night plan's registration_path to the calibration pre-registration markdown, or says the C1 seam is unresolved? List file:line.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: INTEGRATION CLEAN | FOLLOW-UP NEEDED (list lanes) | REVERT-CLASS DEFECT and the claude-codex-report/v1 envelope.
