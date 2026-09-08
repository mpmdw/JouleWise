# Night handback

This file is what the night courier reads first (`NIGHT_COURIER_PROMPT.md`).
The magistrate rewrites the three sections below before every armed night
(ruling R-9, `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`)
and commits the rewrite with the night's plan. Between nights the sections
hold the standing template text, so a courier that reads this file on a
night nobody armed reports exactly that.

The courier does not decide anything from this file. The verdict, the chain
exit code, and every refusal reason come from the result record under the
night's custody root: `night/result.json`, then `night/receipt.json` or
`night/refusal.json` as `result.json` directs. If this file and the result
record disagree, the result record is right and the courier says so.

The night driver independently reads the plan-configured sibling path
`<custody-parent>/magistrate/state.json` when it constructs every courier
message; for the production plan layout this is
`~/night-custody/magistrate/state.json`. The email body reports that file's age
and its last `state` decision without importing the watchdog. Operational
liveness is 15 minutes: an age greater than 900 seconds, a missing file, or an
unreadable decision means the watchdog is dead and must be reported as such.

## Purpose of this night

Plan `rehearsal-20260909`, class `REHEARSAL_STUB`, armed by the headless
magistrate (activation 1ef89702, spawned by the relaunch watchdog on
2026-09-08 00:51:55 PDT) for 02:56 local on 2026-09-09 with a 900 s
window, inside the 02:45–03:30 belt. It is the fresh post-watchdog
rehearsal the state kernel requires before any real plan
(`NIGHT-REHEARSAL-01`, last acceptance item). The chain is the driver's
built-in stub (`sleep 2; echo REHEARSAL`); no pack, no model, no
measurement, no sudo. The plan is v2: `repo_head` and `measurement_head`
both pin THIS commit (the one that rewrote this file), and
`measurement_root` is a disposable detached checkout of this commit at
`/private/tmp/joulewise-rehearsal-20260909-checkout`, used only by this
stub and removed with the plan root before any real plan; the measurement
checkout of record (`/Users/edr/JouleWise-measurement-20260813`) is
untouched. Both night agents are installed FROM that checkout. Ed was
emailed the arming notice before the arm (thread `1a0800cdb282c3f1`, with
the exact pins in its follow-up); a NO on that thread stands the night
down. Expected: `result.json` verdict `REHEARSAL_ONLY`, chain exit 0,
courier deadline `t0 + 900 + 300` = 03:16 PDT. A receipt refusing
`night_refused_agent_present` is acceptable for a stub (it can never
carry GO); any other refusal is a finding. If the agents were installed
before 07:00 on 2026-09-08, that morning's dead-man firing stands down
with one `night.log` line (the R-7 observable); otherwise this night does
not repeat that case. The design ruling and bench pass are in
`docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-arm-plan.md`.

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
`rehearsal-20260909` / `/private/tmp/joulewise-rehearsal-20260909-checkout`
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
development checkout. Author every new v2 plan with
`joulewise.night_plan_writer.write_night_plan`; the writer emits both
`schema: joulewise.night_plan.v2` and integer `schema_version: 2`. Once
authored, every armed plan's canonical `(plan_id, measurement_root,
measurement_head)` is included in the magistrate relaunch prompt's
frozen-checkout list until completion.

**Standing rules** <!-- F11 -->

Author every new v2 plan with
`joulewise.night_plan_writer.write_night_plan`; invalid-plan tests begin with
that writer's bytes and apply a named mutation. The writer emits both
`schema: joulewise.night_plan.v2` and integer `schema_version: 2`; either field
missing or inconsistent makes the plan malformed.
Installer note: on install the installer checks `repo_head` against the
driver checkout HEAD and `measurement_head` against the HEAD of the plan's
`measurement_root`, while `--uninstall` checks neither pin and no longer
needs `claude` on PATH.
Ordinary
daytime work in the dev checkout no longer invalidates an armed night; only
moving the pinned measurement checkout does.
