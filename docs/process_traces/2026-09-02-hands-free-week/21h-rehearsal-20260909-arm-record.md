# 21h — ARM RECORD: rehearsal-20260909 armed by headless activation 784a764e

Written 1788944302 2026-09-09 01:58:22 PDT. Every fact below is a pointer to a captured artifact under `21b-rehearsal-20260909-bench/`; nothing is
restated from memory.

- Block A (steps 0–3) output: `arm-blockA-output.txt` (rc 0; disposable checkout at H; staged plan + validation twin; render-only
  pins validated; both plists lint; differing fields exactly the three custody paths).
- Step 3b: `arm-step3b-output.txt` (own background tasks stopped; no daemon shapes; leaked test pid 58633 retired with its argv in
  `pass3-pid58633-argv.txt`; production census afterwards = this session's own codex mcp-server only).
- Step 5: NO check on thread `1a0800cdb282c3f1` immediately before block B — six messages, all sent by the magistrate (Gmail ids in 21b).
- Block B (steps 4, 6, 7) output: `arm-blockB-output.txt` (foreign agent sessions []; informational []; atomic move; both agents
  installed FROM the stub checkout with validated pins; rc 0).
- The armed plan, byte copy: `arm-night_plan.json`. launchctl list and the watchdog state.json at arm time: `arm-launchctl-and-state.txt`.
- Frozen triple for the next relaunch prompt: (`rehearsal-20260909`, `/private/tmp/joulewise-rehearsal-20260909-checkout`, `ae8f074f`).

## Morning after (the relaunched magistrate; 21b §Morning after)
Harvest `/Users/edr/night-custody/rehearsal-20260909/night/{result.json,receipt.json,refusal.json,courier.sent,courier.json}` and
`night.log`; verify branch `night-results/20260909` on origin; record under NIGHT-REHEARSAL-01; then from the stub checkout run
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260909/night_plan.json --hour 2 --minute 56 --uninstall`;
remove the stub checkout (`git -C /Users/edr/code/JouleWise-wt-magistrate-1ef89702 worktree remove --force
/private/tmp/joulewise-rehearsal-20260909-checkout`) and the plan root before any real plan. Accept only
`night_refused_agent_present` as a receipt refusal; any other refusal is a finding. Then the relayed daytime lanes in
`00-DURABLE-STATE.md` (CLONE-READINESS-01 → G2-a at the earliest census-clean time; the remote-control test between windows).

## This activation's exit
Arming obligates exit by 1788946260 (02:31 PDT). All own background tasks were stopped at step 3b; this record is committed and
pushed on `bookkeeping/2026-09-09-rehearsal-arm-record` (PR opened, ledger to be completed by the successor after the harvest);
Ed is emailed the arm record on thread `1a0800cdb282c3f1`; the session then ends its turn with no live background work.
