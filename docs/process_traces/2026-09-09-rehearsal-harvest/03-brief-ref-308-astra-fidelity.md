SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Refuter brief — PR #308 (bookkeeping/2026-09-09-rehearsal-arm-record @ 20f95848d5975947dbc5bb1c295e56cb58bb534f), FIDELITY / EXECUTION lens (gpt-6-astra, medium, genre review, read-only)

You are a fresh, non-author reviewer. The branch under review adds ONLY process-trace documents and byte-copied artifacts
(`git diff --stat main...HEAD`): the arm record 21h, the harvest record 21i, the durable-state sections for activations 784a764e,
8844a3d0, b1e2fd2f and 628c2eed in docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md, and the artifacts under
docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-bench/ (arm-* and night-harvest/*).

Lens: EXECUTION FIDELITY. Every factual claim in 21h, 21i and the four durable-state sections must be traceable to a byte artifact
in the branch or to live state you can observe read-only. Check specifically:
1. Every epoch/timestamp, sha, pid, Gmail id, branch name, rc and count quoted in 21i against night-harvest/* (result.json,
   receipt.json, night.log, courier.sent, courier.json, night_plan.json, pre-uninstall-observations.txt, uninstall-output.txt,
   removal-output.txt, SHA256SUMS). Recompute SHA256SUMS with `shasum -a 256` and compare.
2. The results branch: `git ls-remote origin refs/heads/night-results/20260909` must equal the sha 21i names; `git log` of
   `origin/night-results/20260909` (fetch it read-only if absent) must match the parent chain 21i states.
3. Live state (read-only): `launchctl list | grep -i joulewise`; `ls ~/Library/LaunchAgents | grep -i joulewise`;
   `ls /Users/edr/night-custody`; absence of /private/tmp/joulewise-rehearsal-20260909-checkout and of the plan root; compare
   with what 21i §Documented post-completion uninstall claims.
4. The root-cause paragraph in 21i: confirm the cited line numbers in joulewise/night_gate.py, scripts/run_night.py and
   tests/test_night_gate.py on THIS head are accurate (within ±3 lines) and that the described mechanism is real.
5. The NIGHT-REHEARSAL-01 acceptance item-by-item table in 21i against docs/process/state_kernel.json /tasks/NIGHT-REHEARSAL-01/acceptance:
   every kernel item is addressed exactly once and the MET/NOT status is supported by evidence in the branch.
6. Internal contradictions between 21h, 21i, the durable-state sections and docs/process/NIGHT_HANDBACK.md (e.g. an armed/not-armed
   statement, a frozen triple, a next-action list that disagrees).

Do NOT edit anything. Report as claude-codex-report/v1, genre review, header < 8192 bytes; body = findings ranked by severity
(blocker / should-fix / nit) each with the exact quote, the artifact or command that refutes or confirms it, and a one-line
proposed correction. State explicitly the checks that passed. No design proposals; fidelity only.
