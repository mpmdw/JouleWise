# NIGHT_HANDBACK.md §Executed and §Next lane (at 7ca2908f)
## Executed — reconciliation dated 2026-09-09 (activation 628c2eed; harvest record 21i)

The night described above was armed by headless activation `784a764e` (not `1ef89702`, which prepared it) with the frozen triple
(`rehearsal-20260909`, `/private/tmp/joulewise-rehearsal-20260909-checkout`, `ae8f074f`) — the checkout name differs from the
`JouleWise-rehearsal-20260909-<sha>` example above; the arm record is
`docs/process_traces/2026-09-02-hands-free-week/21h-rehearsal-20260909-arm-record.md`. It fired at 02:56 PDT on 2026-09-09:
result `REHEARSAL_ONLY`, chain exit 0, results branch `night-results/20260909` at `a84e0f7f`, courier email `1a08599a4ff4d005`.
The receipt refused `night_probe_error` (the gate read `chain.zsh`, which the stub arm never writes) — a finding; the cure is committed on branch `fix/2026-09-09-night-gate-stub-chain` at `5db38b58` (PR #309) under review, not yet merged, as lane
NIGHT-GATE-STUB-CHAIN-01; the plan is not re-armed on that signature. The §Next lane harvest, `--uninstall` from the stub checkout,
and removal of the stub checkout and plan root are DONE (record 21i); nothing is armed and the frozen-checkout list is empty apart
from the canonical repo. The standing rules below are unchanged. RECORD: harvest, uninstall and removal for this night are complete; no next plan is
armed; §Purpose, §Where the results are and §Next lane describe the completed night (this file's history holds no separate
between-nights template text; whether one should exist is referred to the cold gate, not decided here).

## Where the results are

- Custody root: `/Users/edr/night-custody/rehearsal-20260909/night/` —
  `result.json` (expected verdict `REHEARSAL_ONLY`, `chain_exit_code` 0),
  `receipt.json` or `refusal.json` as `result.json` directs,
  `chain.started`, `chain.exited`, `censuses.jsonl`, `courier.sent`,
  `courier.json`.
- Driver log: `/Users/edr/night-custody/rehearsal-20260909/night.log`
  (and the dead-man stand-down line if the 2026-09-08 07:00 firing
  preceded the night).
- Results branch: `night-results/20260909` on `origin`, if the driver's
  push succeeded — verify, do not presume.

## Next lane

The relaunched magistrate (its prompt carries the frozen triple
`rehearsal-20260909` / `/private/tmp/JouleWise-rehearsal-20260909-<sha>`
/ this commit) harvests `result.json`, the receipt or refusal, the courier
message id and the results-branch evidence, records them under
`NIGHT-REHEARSAL-01`, then runs
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260909/night_plan.json --hour 2 --minute 56 --uninstall`
FROM the stub checkout, removes the stub checkout (`git worktree remove`)
and the plan root before any real plan, and then sends the stage-1 plan
email to Ed before any `DIAGNOSTIC_NO_PACK` plan is armed. Accept only
`night_refused_agent_present` as a receipt refusal; cure any other cause
before re-arming; never re-arm the same plan on the same signature twice.
For every v2 plan, run `scripts/install_night_agent.sh` FROM the checkout
named by the plan's `measurement_root`, with that checkout at the plan's
`measurement_head`; never install the two night agents from the
development checkout. Once authored, every armed plan's canonical
`(plan_id, measurement_root, measurement_head)` is included in the magistrate relaunch prompt's
frozen-checkout list until completion.

**Standing rules** <!-- F11 -->

Author every new v2 plan with
