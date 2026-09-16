# 09 — Registration of INSTALLER-FOLLOWUPS-REBASE-01 and RUNBOOK-SOURCE-MAP-01 (2026-09-16 ~01:15 PDT, activation `08ca8197`)

Requested by the interactive session `b0ae8462` from the installer's
post-merge cross-unit review (its record 25, landing with its next batch;
seat report `scratchpad/seats/postmerge-astra.md`). Registration only.

## Facts re-read by this activation (main at `d2cc8b5e`)

- `docs/process/state_kernel.json`: `INSTALLER-BACKUP-WINDOW-01` (`:3019`,
  queued, rank 203) and `NIGHT-STREAM-PATHS-01` (`:3957`, queued, rank 176)
  both still reference `scripts/install_night_agent.sh` in their text;
  `INSTALL-WINDOWS-MULTI-01` (`:2977`) is still `queued` at rank 0 although
  PR #341 merged at `2944a45d`.
- `docs/phase_2/derivation_night_runbook.md:2555` cites `check_schedule`;
  `grep check_schedule scripts/install_night_agent.sh` is empty on main (the
  wrapper shrank to the engine call). The engine's admission is
  `Prepared.admit` at `joulewise/night_agent_install.py:583` (`class
  Prepared` at `:556`).
- `tests/test_run_night.py:1020` keeps the comment "so its 07:00 local
  dead-man is in the past" (the fixed-07:00 assumption).

## Also relayed, not acted on here

The review's R1: with the merged engine, `--render-only` on a plan at the
staging path refuses `plan_outside_custody_root` before rendering, so the
D-175 stub procedure fails at the render step. A fix is in flight on
`fix/2026-09-16-render-only-staged-plan`. This activation will not attempt
the arm until the interactive session's handoff says that fix is on main.

## What was registered

`INSTALLER-FOLLOWUPS-REBASE-01` (rank 215) and `RUNBOOK-SOURCE-MAP-01`
(rank 216), both `p3_hardening_candidates`, lane `agent`, `queued`. Kernel
188 → 190 rows; `TASK_QUEUE.md` regenerated; `tests/test_gen_state.py`
updated. The `INSTALL-WINDOWS-MULTI-01` status flip to done is left to the
interactive session's post-merge batch (its lane; the dependent rows'
blocked states recompute with it).
