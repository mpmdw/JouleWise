NIGHT-STALL-WALLCLOCK-ABORT-01 (kernel A221, P1): a stalled night chain now ends by itself.

**Defect:** nothing terminated a stalled chain before a person entered the agent census (the 2026-09-16 night held the machine 11 h 07 m); the chain's own window guard sits after the reservation, the dead-man correctly refuses while the chain is alive, and the driver had no wall-clock abort. The cured custody reads (PR #350, #352) bound one stall class; this is the driver-side backstop the design consult called not redundant.

**Cure (cold-gate ruling 61 as amended by the Opus pairing refuter, synthesis record 13):**
- The driver terminates the chain at the exclusive window end plus a separate shutdown constant WINDOW_SHUTDOWN_GRACE_S = 300 s (not derived from the courier deadline), tracked on the monotonic clock, checked before and after every census probe and census append, and enforced by a daemon watchdog thread that fires even when the main loop is blocked in a probe wait or a custody-root write; the thread writes the refusal document, chain.deadline and chain.unkilled itself and never runs the courier.
- Termination is proven for the whole process group on both the deadline and the census-abort paths: SIGTERM, wait, re-signalled group census, SIGKILL, wait, census (70 s bound); proven only when the direct child is reaped and the census is empty (pgrep rc 1 with empty output); unproven keeps night_chain_alive with the trigger in evidence and suppresses the courier.
- The chain's end-of-window abort inspects only the slot it consumes (next_slot) under one 120 s custody budget passed by the chain, in explicit read-replay mode, so a slow-but-admitted root completes instead of refusing; a lawful abort that starts at the window end and uses its full budget is not interrupted (120 ≤ 300 − 70).
- night_window_exceeded registered COLD (never auto-retry) at all five sites; runbook, handback timeline (window end → +300 s → ≤70 s → ≤300 s courier → dead-man +3900 s, ≥3230 s spare) and courier prompt updated; chain digest re-pinned.

No plan schema, dead-man, census or gate semantics change. Flagged for Ed (lane PREREG-CHAIN-DIGEST-ADDENDUM-01, rank 227): the sealed pre-registration still pins the chain digest as sealed; the chain moved twice today for operational reasons only; a dated addendum is required before the next arm and is not the magistrate's to write. All seats and refuters on this PR are Opus 5 (Codex quota exhausted); the cold judge is Fable.

## Gate ledger (D-118 / D-121)

| # | Gate item | Evidence |
| --- | --- | --- |
| 1 | Independent audit by a fresh non-author reviewer | RUN docs/process_traces/2026-09-16-activation-9853dd2b/66-wallclock-abort-refuter-report.md |
| 2 | Paired distinct lenses: contract + execution (physics if measurement-adjacent) | RUN docs/process_traces/2026-09-16-activation-9853dd2b/66-wallclock-abort-refuter-report.md |
| 3 | Lead-written FIX contract with dictated closure shapes; findings triaged and dispositioned, never silently applied | RUN docs/process_traces/2026-09-16-activation-9853dd2b/62-brief-wallclock-abort-seat.md |
| 4 | Delta re-audit of every fix round | RUN ROW4 |
| 5 | Same-signature statement from every delta; a surviving class escalates to a consult, not round three | RUN ROW5 |
| 6 | Opus counter-review on the near-final head | RUN docs/process_traces/2026-09-16-activation-9853dd2b/61-coldgate-packet-wallclock-abort/12-opus-pairing-refuter-on-ruling-10.md |
| 7 | Apex Fable code-reading diff gate answering design-level questions; never skipped or downgraded | RUN docs/process_traces/2026-09-16-activation-9853dd2b/61-coldgate-packet-wallclock-abort/10-coldgate-fable-ruling.md |
| 8 | Overbuild / merge-ability prune | RUN docs/process_traces/2026-09-16-activation-9853dd2b/61-coldgate-packet-wallclock-abort/13-magistrate-synthesis-ruling-10-with-opus-amendments.md |
| 9 | Lead unpiped full-suite replay on the integration tree (not the stale branch), exact tail recorded | RUN ROW9 |
| 10 | Final-head fresh-eyes review after every post-review commit | RUN ROW10 |
| 11 | CI green on final head + post-merge cross-unit integration review | RUN docs/process_traces/2026-09-16-activation-9853dd2b/00-launch-record.md |
| 12 | Magistrate terminal review, full session context, of the exact merge candidate (final head sha); not delegable | RUN FINALSHA |

### Ledger notes
- Rows 1–2: one Opus refuter carried both lenses with nine mutation probes and real-process adversarial probes (record 66).
- Row 6: the Opus counter-review of the DESIGN is the pairing refutation of the cold ruling (record 12), which found the blocker-grade gap the ruling's shape had; the code counter-review is record 66.
- Row 7: the cold Fable judge's ruling (a fresh Fable instance, executed probe) stands as the design-level code-reading gate; the magistrate's own read is in record 00 addendum "terminal review".
- Row 8: the synthesis narrowed the abort to the one read it consumes and kept the courier call site out of the strengthening (record 13, record 64 §4).
- Row 11: hosted CI does not run on pull requests here and is post-merge confirmation under Ed's 2026-09-16 ruling; the linked record documents the local substitute (full replay + quick tier) on this head; the post-merge review of this merge is the successor's next item.
- Row 12: FINALSHA is the exact merge candidate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
