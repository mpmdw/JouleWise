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

## Purpose of this night

Plan `rehearsal-20260902`, class `REHEARSAL_STUB`, armed by the magistrate
(Fable, standing loop) for 02:56 local on 2026-09-02 with a 900 s window.
The chain is the driver's built-in stub (`sleep 2; echo REHEARSAL`); no
pack, no model, no measurement, no sudo. This night exists to prove the
stage-1 machinery end to end from launchd: the driver fires from the
installed LaunchAgent (not from a shell), records the gate receipt (expected
NOT GO — agent sessions were deliberately left running, so the census
refuses `night_refused_agent_present`, and a `REHEARSAL_STUB` may never
carry GO), runs the stub chain, pushes the results branch, and delivers this
courier email. It serves kernel row `NIGHT-REHEARSAL-01` (stage 2 of the
unattended lane; acceptance items 2 and 3). The e-mail's message id becomes
the row's evidence.

## Where the results are

- Results branch: `night-results/20260902` on `origin` (pushed by the
  driver from a fresh shallow clone; readable from a phone).
- Custody root: `/Users/edr/night-custody/rehearsal-20260902/night/` on the
  measurement machine — `result.json` (expected verdict `REHEARSAL_ONLY`,
  `chain_exit_code` 0), `receipt.json`, `chain.started`, `chain.exited`,
  `censuses.jsonl`, `courier.json`, `night.log`.

## Next lane

Resume the standing loop (`/loop` mandate; memory `unattended-loop-first`):
the magistrate harvests the custody root, records the courier message id
and the first `censuses.jsonl` record (does the driver see its own
`--courier-bin …/claude` argv? bench prediction: no — BSD `pgrep` excludes
its ancestors) under `NIGHT-REHEARSAL-01`, then runs
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260902/night_plan.json --hour 2 --minute 56 --uninstall`
at the SAME commit the plan was armed on (the installer checks `repo_head`
before the uninstall branch), so the dead-man job stops firing at 07:00.
Then: the "installed the morning before" stand-down rehearsal (cold gate D1
R-7 amendment) and the stage-1 plan email to Ed before any
`DIAGNOSTIC_NO_PACK` plan is armed. A refusal other than
`night_refused_agent_present` on this night is a finding: cure the cause
before re-arming; never re-arm the same plan on the same signature twice.
