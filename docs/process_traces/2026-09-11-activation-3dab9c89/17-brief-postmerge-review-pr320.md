SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

POST-MERGE CROSS-UNIT INTEGRATION REVIEW of main at baf7b900 (merge of PR #320 EPOCH-CONTINUATION-01, branch head a6ddb2ab, twelve rounds; gate ledger row 11's second half). Read-only in this detached worktree; temp files only under /tmp. Read the PR body (gh pr view 320 --repo mpmdw/JouleWise --json body --jq .body) and the terminal review /Users/edr/code/JouleWise-wt-bk-3dab9c89/docs/process_traces/2026-09-10-activation-96bfeca7/204-terminal-review-pr320.md, then 'git diff 1dddcfea..baf7b900 --stat' and the full diff.

The question is INTEGRATION, not re-review of the unit: does the merged unit interact badly with anything else on main that the branch-scoped reviews could not see?
1. Every call site of the judged-epochs loader helper and of the continuation artifact reader on main (grep the module names the diff introduces): any consumer on main that still reads the pre-#320 shape, or any path where the loader's refusal semantics differ from what the contract paragraphs (docs/contracts/*.md changed by the PR) promise?
2. The capture writer routing through judged epochs: does any OTHER writer or desk tool on main (scripts/issue_calibration_acceptance_generation.py, the S1 --derivation-only writer, night chains under scripts/night_chains/, gen_derivation_night.py) construct the same envelope/ledger objects with assumptions the routing changed?
3. state_kernel / generated views: python3 scripts/check_state_kernel.py (or whatever the repo's kernel-drift check is — find it in .github/workflows) passes at baf7b900?
4. Run the focused modules the PR touched plus every test module that imports the changed modules (grep -l): paste counts. Do NOT run the full suite (a replay is running on this host).
5. Docs: any process doc on main (RUN_STATE.md, docs/process/*.md, TASK_QUEUE.md, docs/phase_2/derivation_night_runbook.md) that still describes the PASS route of issue 316 as "not implemented" or names scripts/issue_epoch_continuation.py wrongly? List file:line.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: INTEGRATION CLEAN | FOLLOW-UP NEEDED (list lanes) | REVERT-CLASS DEFECT and the claude-codex-report/v1 envelope.
