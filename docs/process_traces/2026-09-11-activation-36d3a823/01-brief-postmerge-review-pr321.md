# Re-run by activation 36d3a823 (the 2dae3835 run 20260911T171546Z-84660 was cut at its exit, 10:17 PDT).
SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

POST-MERGE CROSS-UNIT INTEGRATION REVIEW of main at 4c06b3b4 (merge of PR #321 NIGHT-INTERPRETER-PIN-01, branch head a6e0eb31, five fix rounds; gate ledger row 11's second half). Read-only in this detached worktree; temp files only under /tmp. Read the PR body (gh pr view 321 --repo mpmdw/JouleWise --json body --jq .body) and the terminal review /Users/edr/code/JouleWise-wt-bk-36d3a823/docs/process_traces/2026-09-11-activation-3dab9c89/13-terminal-review-pr321.md, then 'git diff baf7b900..4c06b3b4 --stat' and the full diff.

The question is INTEGRATION, not re-review of the unit: does the merged unit interact badly with anything else on main that the branch-scoped reviews could not see?
1. Every caller of the night-agent installer (scripts/install_night_agent.py or whatever the diff names) and of the plist template on main: the NIGHT_HANDBACK procedure (docs/phase_2/NIGHT_HANDBACK.md), the derivation-night runbook (docs/phase_2/derivation_night_runbook.md), any arm/rehearsal scripts, and any test fixture that renders the template. Does any caller still pass no --python, expect `/usr/bin/env python3` in the rendered plist, or parse the plist with plutil? List path:line.
2. The driver's MIN_PYTHON import-time guard and hoisted module-scope imports: is there any consumer on main that imports the night driver module (joulewise/run_night.py or scripts/run_night.py — find it) under an interpreter or context where the hoisted imports now fail earlier than before (CI jobs on 3.11 and 3.14, the watchdog scripts/magistrate_watchdog.py, the night chains under scripts/night_chains/, gen_derivation_night.py)? Does the `preflight` subcommand's plan loading agree with the plan schema written by joulewise.night_plan_writer.write_night_plan on main?
3. The installer's default interpreter `<measurement_root>/.venv/bin/python` derived from the plan: does the plan schema on main carry measurement_root in the field the installer reads, and does the NIGHT_HANDBACK procedure on main create that venv before install (or say where it comes from)? If the procedure and the installer disagree, that is a SHOULD_FIX with the exact lines.
4. Kernel drift: run the CI-defined kernel check (find it in .github/workflows/ci.yml) at 4c06b3b4; paste the outcome.
5. Run the focused modules the PR touched (tests/test_install_night_agent.py, tests/test_run_night.py) plus every test module that imports the changed modules (grep -l): paste counts. Do NOT run the full suite (a replay is running on this host).
6. Docs: any process doc on main (RUN_STATE.md, docs/process/*.md, TASK_QUEUE.md, docs/phase_2/*.md, docs/contracts/*.md) that still describes the plist as running `/usr/bin/env python3`, names the installer flags wrongly, or says the interpreter pin is not yet landed? List file:line.

Severity-tier findings (BLOCKER / SHOULD_FIX / NIT) with path:line, command and output. End with VERDICT: INTEGRATION CLEAN | FOLLOW-UP NEEDED (list lanes) | REVERT-CLASS DEFECT and the claude-codex-report/v1 envelope.
