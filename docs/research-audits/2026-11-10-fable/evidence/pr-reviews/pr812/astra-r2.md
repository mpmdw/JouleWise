**BLOCK** PR #812 at `57ed7334e` with drafts `b3bed8d38`. All five original findings are fixed on their original scenarios. Two new timing failures remain. A correctly authorized start can also be refused.

- **[HIGH] [VERIFIED] A rollback can put the recorded start before issue and close-gap release.** On qual-01-s01, issue, watcher observation and the 1,200-second close gap all became valid at `1795111200`. The gates passed. A two-second rollback before the arm anchor let the child admit `1795111199`. All six drafts reproduced this in Bash and Zsh. Carry these lower bounds into the child. [Reproduction](/tmp/jw812-delta.aJ31pv9A/delta.py:138)
- **[HIGH] [VERIFIED] Sleep can hide elapsed time from the expiry check.** With 60 seconds of watcher validity left, simulate 60 seconds asleep, five awake and a ten-second backward wall correction. At 65 seconds elapsed, the child saw wall `+55`, recorded `+5` and admitted. A sleep-inclusive anchor refused the same case. Use a sleep-inclusive clock at both ends of the handoff. [Reproduction](/tmp/jw812-delta.aJ31pv9A/delta.py:150) · [Python clock mapping](https://docs.python.org/3.13/library/time.html#time.monotonic) · [Apple clock semantics](https://developer.apple.com/documentation/driverkit/mach_continuous_time)
- **[LOW] [VERIFIED] False refusal.** With no clock step, a two-millisecond arm sampling interval and an actual start one millisecond before cutoff, the projected interval extended one millisecond past cutoff. The child returned `3`. This is the guard’s conservative behavior. [Reproduction](/tmp/jw812-delta.aJ31pv9A/delta.py:160)

| Original finding | Result on the pinned revisions |
|---|---|
| [HIGH] [REFUTED] Batch rollback | Exact `02:35:39` release admitted. `02:35:38.750` and `01:08:39` refused on all six drafts. |
| [MED] [REFUTED] Watcher expiry | With one second left, equality at expiry refused on either clock. |
| [MED] [REFUTED] Midnight rounding | `1795161599.9999998` counted on Nov 19. Nov 20 authority refused. |
| [MED] [REFUTED] Omitted authority | Both CLIs exited `2` for all three qualification kits. |
| [LOW] [REFUTED] Receipt omission | Each admitted synthetic start persisted its authorized date, inclusive lower bound and exclusive cutoff. |

I reran the original harness unchanged. Its five finding probes stopped at obsolete shell or CLI assumptions. The current-interface probes above exercised the underlying behavior and stopped admitted runs at synthetic preflight. Every effective upper bound passed at cutoff −1 ns, equality and +1 ns. Both DST transitions passed. [Original output](/tmp/jw812-delta.aJ31pv9A/original-all.log) · [Exact probes](/tmp/jw812-delta.aJ31pv9A/delta.py) · [Results](/tmp/jw812-delta.aJ31pv9A/delta.log)