# 02 — Registration of LEAD-MARGIN-01 (2026-09-15 ~23:25 PDT, activation `08ca8197`)

## Source

At ~23:20 PDT the interactive session `b0ae8462` (Ed at the machine) relayed
over the cross-session channel Ed's remark on the 85-minute floor between the
last permitted night-agent install and t0, quoted by that session as verbatim:

> "surely a way to speed this without weakening the science"

The relay asked for a registration-only P1 lane. It is not a directive issue
(`gh issue list --label directive` was empty at 23:12 and before this slice).

## Facts re-read by this activation (read-only)

- Branch checkout `/Users/edr/code/JouleWise-wt-iw-txn` at `69d668be`
  (`feat/2026-09-15-install-windows-transactional`):
  `scripts/run_night.py:68` `INSTALL_CLOSE_MARGIN_S = 3600`;
  `:965-970` `install_close_epoch(plan) = t0 - PLAN_LEAD_S - INSTALL_CLOSE_MARGIN_S`.
  `docs/phase_2/derivation_night_runbook.md:1305` (`= t0 - 25 min - 60 min =
  t0 - 85 min`) and `:2630` (`install_close_epoch(plan) = t0 − 85 min`).
- Main at `b8719af7`: `scripts/magistrate_watchdog.py:67` `PLAN_LEAD_S = 25 * 60`.
  Neither `INSTALL_CLOSE_MARGIN_S` nor `install_close` exists on main, and the
  main runbook does not quote 85 minutes. The whole install-close mechanism
  therefore lands with INSTALL-WINDOWS-MULTI-01, which is the lane's hard
  start dependency.

## What was registered

Kernel row `LEAD-MARGIN-01`, rank 210, `p1_phase_gate`, lane `agent`, status
`queued`, hard start dependency on `INSTALL-WINDOWS-MULTI-01`. Kernel 183 → 184
rows; `TASK_QUEUE.md` regenerated; `tests/test_gen_state.py` updated. No
constant was changed. The 5-minute figure in the relay is recorded as the
proposal the seat must justify or replace from the pad's history and the
D-180/D-181 records; the 25-minute resident lead and every t0 gate are fenced
as untouched in the acceptance text.

## Amendment (2026-09-15 ~23:30 PDT)

The interactive session relayed a second remark from Ed, quoted as verbatim:

> "can't do less than 30 safely? let's do a speed pass with science quality
> the only gate to speeding things up i want quick iterations fully ran by you
> looped and running new ones"

Scope change applied to the row: the 25-minute resident lead is no longer
fenced. `PLAN_LEAD_S` / `REQUEST_LEAD_S` / `TERM_LEAD_S` / `KILL_LEAD_S`
(`scripts/magistrate_watchdog.py:67-70` on main at `d3ea0236`, re-read by this
activation: 25 / 25 / 16 / 15 minutes) are in scope with targets 5 / 5 / 3 / 2
minutes, and `INSTALL_CLOSE_MARGIN_S` targets about 2 minutes, for an
arm-to-t0 floor of about 10 minutes. The seat must justify every number by
what it physically protects (load-average decay after the agents exit, the
census needing the magistrate and its children gone, the watchdog's own tick
cadence still observing each deadline; `SUPERVISOR_POLL_S = 10` at `:71`), pin
the derived values, and leave every t0 gate untouched. The hard dependency on
INSTALL-WINDOWS-MULTI-01 stays. The doubled parenthetical in the first
status note was cleaned up in the same edit. Still registration only: no
constant changed.
