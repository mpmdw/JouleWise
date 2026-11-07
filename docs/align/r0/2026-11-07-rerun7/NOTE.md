# ALIGN v4 R0 re-run 7 (2026-11-07 UTC): first complete SMC capture; selection inconclusive because of a coverage-accounting defect

Record `/Users/edr/night-align/r0-v4-20261107T0810Z`, launched by magistrate
activation 62c121f8 on the measurement checkout at `e1a91226e`. Written up by
activation a9031916.

- Run: 08:11:31Z to 08:57:59Z (2,788.8 s). Status `fail`, `complete_r0` false,
  `stopped_after` smc with outcome `inconclusive`. Ladder and long-decode did not run.
- host, host-identity, model-load: pass. disk and template: diagnostic.
- load: pass, NLL 11.0368 nats/token (same as runs 5 and 6).
- generated: pass. checkpoint: not required (rewind fraction 0.0 over 12 transitions).
- memory: pass, peak 37,025,053,788 bytes against 45e9.
- smc: exit 0 after 1,845.6 s. **No contention refusal**: 305 quiet observations,
  all clean. The full 300/900/600 s profile ran: 1,800 readings of 403 keys,
  zero read errors (three keys of type `hex_` are unreadable at enumeration and
  are not in the 403). Status `inconclusive`, reason "SMC die/heatsink selection
  unresolved": every one of the 403 keys was rejected with "insufficient phase
  coverage or >=1% read errors" (phase coverage 0.12 idle, 0.29 load, 0.22 recovery).
- D pins: PASS (`d-pins.txt`). Spotlight 716 and 73957 resumed (`S`).
  photoanalysisd 13374 and mediaanalysisd 21331 still held (`T`).
- SMC journal sha256 in `smc-journal.sha256`.

## Cause: the 100 ms grid tolerance, not the sensors

`thermal.Coverage` counts a 1 s tick as covered only if a reading's midpoint,
`(started + finished) / 2`, lies within 100 ms (`NS // 10`) of the grid point.
The grid point is anchored at the phase's first reading. In this capture:

- Reading all 403 keys takes 86 ms median and 392 ms at most, so the midpoint sits
  about 43 ms after the start on average.
- Readings start late against the phase origin by 106 ms (idle), 113 ms (load)
  and 80 ms (recovery) median, and by 150 ms at the 90th percentile. Most of this
  lateness comes from the quiet census that #691 runs every 5 s inside the
  sampling loop.
- So 153 of 300 idle, 498 of 900 load and 241 of 600 recovery readings miss the
  100 ms window. The readings themselves are complete: the start-to-start
  interval is 1,002 ms median (850 ms min, 1,298 ms max) and the longest interval
  is 1.27 s.

The 100 ms value carries no derivation beyond "scheduler/read jitter", and this
capture's measured jitter is larger. What the bar is meant to protect is one
valid reading in each 1 s cell. The fits use each reading's actual stamps; no
value is placed on the grid. A cell 1 s wide owns every stamp within half a
period of its centre, so the tolerance that matches that cell is 500 ms
(`NS // 2`), with duplicates counted once as now.

## Diagnostic re-rank (not a result; R0 is selection data and stays inconclusive)

`diag-rerank.py` loads this journal and runs the pinned `smc_enumeration.rank`
from `e1a91226e`, with only `thermal.Coverage.tolerance_ns` changed:

- 100 ms (as run): 403 keys "insufficient phase coverage"; no die, no heatsink;
  `select_keys` gives `s_fast` None, `s_slow` None. This reproduces the recorded result.
- 500 ms: phase coverage 1.0 in all three phases for the temperature keys; 16
  die-class keys (all `Tg*`; e.g. `Tg2I`: t63 2.9 s, cooling tau 1.7 s, rise
  88.6 degC), 141 heatsink-class keys (e.g. `TaRT`: t63 50.9 s, tau 123 s, rise
  4.1 degC), 246 record-only. `select_keys` gives `s_fast` `Tg2I`, `s_slow` `TaRT`.

## Next

The fix goes on its own lane (coverage cell tolerance for the classifier), with the
normal gates, then R0 re-launches in a clean gap. See RUN_STATE item 195.
