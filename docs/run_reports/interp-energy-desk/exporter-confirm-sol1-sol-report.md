**HOLD.** F1–F6 are closed, and the real-producer e2e reaches release **AGREE**. One remaining failure: a supplied watchdog digest mismatch is swallowed, allowing export without an authenticated latch.

Committed `8cdd0ea93` on `align/2026-11-08-exporter-confirm-sol1`. Tree clean; nothing pushed.

- Added the [report](/Volumes/JW-EXT/jw-wt/sol-exporter-confirm-sol1/docs/analysis/v4/EXPORTER-CONFIRM-sol1.md), synthetic witnesses, and dated handoff.
- Targeted tests: e2e **36 pass**, prior reviews **8/11 pass**, units **15 pass**. New probes: **3 pass, 1 intentional failure** reproducing the gap.
- All used Python 3.13 with faulthandler; total test time **13m 2s**. Commands and resolved fixture issues are documented in the report.
- Synthetic evidence only; no production code changed.

Next: lead fixes supplied-watchdog authentication failures, then reruns the witness and e2e.