# ALIGN v4 R0 re-run 6 (2026-11-07 UTC): refused in `smc` by the daily /tmp cleaner at 00:00 PST

Record `/Users/edr/night-align/r0-v4-20261107T0720Z`, launched by magistrate
activation ac09cac6 on the measurement checkout at `e1a91226e`. Written up by
activation 62c121f8.

- Run: 07:18:54Z to 08:00:04Z (2,469.8 s). Status `fail`, `complete_r0` false,
  `stopped_after` smc. Ladder and long-decode did not run.
- host, host-identity, model-load: pass. disk and template: diagnostic.
- load: pass. NLL 11.0368 nats/token against the reference 11.0642 (delta
  -0.0274); 256-target bin deltas from -0.207 to +0.081. Same as run 5.
- generated: pass, 0 off-spec echo turns. checkpoint: not required (rewind
  fraction 0.0 over 12 eligible transitions).
- memory: pass. Peak 37,025,283,164 bytes against a 45e9 limit; swap unchanged
  at 9,237,954 bytes.
- smc: fail, exit 3, after 1,520 s: 300 idle and 900 load samples, then about
  288 of 600 recovery samples (1,488 records). `CpuQuietProbe` raised
  `NotQuiet` over a 35.9 s interval (wall 07:59:28Z to 08:00:04Z, i.e.
  23:59:28 to 00:00:04 PST): `find` (pid 59251, started 00:00:00) at 0.0786
  CPU-s/s and fseventsd (pid 23753) at 0.0697, both above the 0.05 limit. The
  R0 tree was at 0.051. The host aggregate (0.357) was flagged
  (`aggregate_above_0_05`), not judged.
- D pins: PASS (`d-pins.txt`). Spotlight 716 and 73957 resumed (`S`).
  photoanalysisd 13374 and mediaanalysisd 21331 are still held (`T`).
- SMC journal sha256 in `smc-journal.sha256`.

## Cause

macOS's `com.apple.tmp_cleaner` system daemon
(`/System/Library/LaunchDaemons/com.apple.tmp_cleaner.plist`,
`StartCalendarInterval` Hour 0, so every day at 00:00 local). The unified log
shows launchd spawning it at 00:00:00.006 PST because of its calendar interval
(`UserEventAgent ... Running StartCalendarInterval: com.apple.tmp_cleaner`).
`/usr/libexec/tmp_cleaner` runs two `find -dx . -fstype local ...` walks over
`/tmp`, deleting files untouched for 3 days. `/private/tmp` holds about 73,100
entries (2.3 GB), mostly agent-seat scratch, so the walk is not trivial:
`find` charged about 2.8 CPU-s inside the judged interval, all of it in the
4 s after 00:00:00. fseventsd's rate is the file-system event load of that
walk and its deletions.

This is real contention, measured as a rate over at least 30 s. It was not
caused by R0 and is not a code defect. The refusal is correct.

## Count

Third consecutive `smc` failure: run 4 (the #691 snapshot artefact, fixed),
run 5 (softwareupdated's 6-hourly scan at 23:09), run 6 (this). Each has a
different, identified cause outside R0. Under item 181 a third consecutive
failure of the same check goes to Ed, and the magistrate waits for his answer
before re-launching.

## Known scheduled contention (PST, measured on this Mac)

| Time | Source | Evidence |
|---|---|---|
| 00:00 daily | com.apple.tmp_cleaner (`find` over /tmp) | this run; plist |
| about 05:09, 11:09, 17:09, 23:09 | softwareupdated background scan | install.log `AutoBackgroundScanFinished`, run 5 |
| about 05:40, not fixed | XProtectRemediator scan | RUN_STATE item 14 |
| about 12:53 daily | background maintenance batch | RUN_STATE item 17 |

A re-launch that starts after one of these and ends before the next avoids all
four: the gaps are about 00:05-05:05, 06:15-11:05, 11:15-12:45, 13:15-17:05
and 17:15-23:05.
