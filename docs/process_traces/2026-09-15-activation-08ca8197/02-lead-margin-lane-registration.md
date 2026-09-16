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
