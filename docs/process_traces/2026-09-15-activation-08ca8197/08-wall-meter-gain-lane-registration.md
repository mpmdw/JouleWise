# 08 — Registration of WALL-METER-GAIN-01 (2026-09-16 ~01:10 PDT, activation `08ca8197`)

## Source

The interactive session `b0ae8462` (Ed at the machine) relayed at ~01:05 PDT
that Ed is buying a ChargerLAB POWER-Z KM003C USB-C inline power meter,
quoting Ed's condition as verbatim: "if that buys us meaningful science
quality". Not a directive issue. Registered as relayed.

## Facts re-read by this activation (main at `1884922b`)

- `docs/process_traces/2026-09-15-interactive-b0ae8462/21-rq-literature-and-best-practices-fable.md`
  §2 row 1: the analyzer practice (≤1 % uncertainty, calibrated yearly, fixed
  ranges; SPEC Power methodology, MLPerf checker) is scored **Not done** for
  JouleWise, whose energy scale rests on the software counter alone; row 5 of
  the same record cites Jay et al. (CCGrid 2023) on the load-dependent gap
  between software meters and the wall.
- `docs/process/research_plan_2026-09-16.md` exists on main (the plan whose
  Phase 0 desk day the lane rides).

## What was registered

Kernel row `WALL-METER-GAIN-01`, rank 214, `p1_phase_gate`, lane
`ed_external` (the meter is plugged, and the battery held full, by Ed's
hands; the logger design, alignment method and tests are agent work under
it), status `queued` with the hardware-arrival condition in the status note.
Kernel 187 → 188 rows; `TASK_QUEUE.md` regenerated; `tests/test_gen_state.py`
updated. Registration only; nothing measured, no plan doc edited (the
Phase 0 row is the lane's own first edit).
