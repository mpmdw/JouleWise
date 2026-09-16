# 08f — Cold-gate 06 Q3 STOP CONDITION fired; blind three-seat redesign consult convened (magistrate b0ae8462, 2026-09-15 22:58 PDT)

The Q5 execution lens (08e) drove real SIGINT/SIGTERM/SIGHUP at every seam under Python 3.14.7 and 3.9.6 on
`efdaed87`: seams a, b, c, d, f, g and the F1 shell cells pass; seam e fails 60/222 per interpreter — a signal queued
after its original disposition is re-installed is delivered at the final `SIG_SETMASK` with that original disposition
and terminates the process (or raises KeyboardInterrupt) AFTER the result was completed. Per ruling 10 Q3 there is no
round 7. Consult packet: 13-consult-signal-redesign/00-CONSULT.md (exhibits = 08e + AUDIT, ruling 10, synthesis 13,
pairing 12, adjudication 34, the current code). Seats: Astra xhigh (read-only seat in wt-row10), a blind Fable
subagent, an Opus subagent (evidence-backed on signal seams tonight). The magistrate synthesises, then one
implementation round under the new design, delta re-audit, the execution lens again, replay, PR.
