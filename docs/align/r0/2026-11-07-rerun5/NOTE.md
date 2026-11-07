# ALIGN v4 R0 re-run 5 (2026-11-07 UTC): refused in `smc` by a scheduled software-update scan

Record `/Users/edr/night-align/r0-v4-20261107T0631Z`, launched by magistrate
activation 08e39e3b on the measurement checkout at `e1a91226e` (PR #691: contention
measured as CPU-seconds per second over at least 30 s). Written up by activation
ac09cac6.

- Run: 06:32:18Z to 07:09:44Z (2,245.8 s). Status `fail`, `complete_r0` false,
  `stopped_after` smc. Ladder and long-decode did not run.
- host, host-identity, model-load: pass. disk and template: diagnostic.
- load: pass. NLL 11.0368 nats/token against the reference (delta -0.0274);
  bin deltas from -0.207 to +0.081.
- generated: pass, no off-spec echo turns. checkpoint: not required
  (rewind fraction 0.0 over 12 eligible transitions).
- memory: pass. Peak 37,024,627,804 bytes against a 45e9 limit; swap
  unchanged at 9,237,954 bytes.
- smc: fail, exit 3, after 1,310 s: 300 idle and 900 load samples, then 78
  recovery samples. `CpuQuietProbe` raised `NotQuiet` over a 35.9 s interval
  (wall 07:08:28Z to 07:09:04Z): softwareupdated (pid 547) at 0.0704 CPU-s/s
  and duetexpertd (pid 834) at 0.0670 CPU-s/s, both above the 0.05 limit. The
  R0 tree was at 0.054. The host aggregate (0.364) was flagged
  (`aggregate_above_0_05`), not judged, as #691 rules.
- D pins: PASS (`d-pins.txt`). Spotlight 716 and 73957 resumed (`S`).
  photoanalysisd 13374 and mediaanalysisd 21331 are still held (`T`).
- SMC journal sha256 in `smc-journal.sha256` (1,279 records).
- The SMC row has no `quiet_observations` field. The probe returns
  observations only on a pass, so a refused stage leaves only the refusal.

## Cause

softwareupdated's automatic background scan. `/var/log/install.log` shows
`AutoBackgroundScanFinished` every 6 h, at about 05:09, 11:09, 17:09 and 23:09
PST, every day from 11-02 to 11-06. This one finished at 23:09:53 PST, the
same minute as the refusal. duetexpertd's burst came at the same moment. Its
lifetime average is about 0.0007 CPU-s/s (23:43 of CPU in 23 days). 30 s
after the refusal, both daemons added no measurable CPU time.

This is real contention, measured as a rate over at least 30 s (item 190 (2)).
It was not caused by R0 and is not a code defect. The scan is predictable, so
the remedy is timing. The re-run starts just after the 23:09 scan and has
about 5.7 h before the next one at about 05:09 PST.
