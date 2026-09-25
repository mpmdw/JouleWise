ROLE: DELTA re-audit (read-only review) for JouleWise combined PR A294+A295, fix round 1. Independent reviewer; you did not write this code. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT. Linked worktree /Users/edr/code/wt-a65fb4fa-a294rev2, detached at the fix-round head (`git log -1`). The fix round is `git diff 5ef72338 HEAD`, and the whole PR is `git diff bd80d169 HEAD`. Read-only in the repository; scratch work only under /tmp. Fences: never launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*; never import or execute from /Users/edr/code/JouleWise.
Fix contract: /Users/edr/code/wt-a65fb4fa-bk/docs/process_traces/2026-09-24-activation-a65fb4fa/23-a294-fix1-seat-brief.md (P1-P9). Lens reports that produced it: 20-a294-a295-sol-execution-lens.md and 21-a294-a295-opus-contract-lens.md in the same directory.

1. TASKS (execute; do not just read):
   D1. Each of P1-P9: FIXED / PARTLY / NOT FIXED / FIX INTRODUCED A NEW DEFECT, with executed evidence. For P2, re-run the fsmonitor hook probe against the production probe runner. For P3, re-run a partial-output timeout through scripts/run_night.py's runner and the gate.
   D2. New defects introduced by the fix round anywhere in its diff: behaviour changes outside the contract, refusal texts, receipts, the render_policy doc blocks, runbook accuracy (does the rewritten passage describe the code exactly?), and test strength (mutate each new guard in a /tmp copy; which tests kill it).
   D3. Same-signature statement: does any finding repeat a defect class from lenses 20 or 21 (for example another missed consumer, another probe path without evidence)? Say YES or NO per class.
   Named test modules only (never discover): tests.test_night_gate tests.test_run_night tests.test_night_kinds tests.test_evidence_night tests.test_arm_retry tests.test_magistrate_watchdog tests.test_git_fixture_maintenance.

2. ACCEPTANCE. Review genre. Severity BLOCKER / SHOULD-FIX / NIT with file:line and executed evidence. Body under about 300 lines; JSON header under 8 KB. End your turn only when D1-D3 are answered.
