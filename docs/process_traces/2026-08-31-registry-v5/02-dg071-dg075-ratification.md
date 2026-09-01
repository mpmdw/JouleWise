# DG-071 / DG-075 statistic ratification (magistrate, 2026-08-31)

Reviewer-panel item C7 asked for the two diagnostic-era §6 `[PENDING]` values
to be fillable by DECLARING their statistic. RATIFIED as the registry
proposes:

- **DG-071 (record interval width):** median with IQR of
  `interval_end_s − interval_start_s` over every retained record of the cited
  `p2015-df-ph-decode-abs-r03` bundle, with the exact file path and SHA-256
  recorded by the fill's ratification artifact. The former "111.8–112.5 ms"
  band is the bottom of the width distribution, not its range (projection
  evidence, PR #245), and the fill must not resurrect it.
- **DG-075 (record spacing):** median with IQR of differences between
  consecutive unique `timestamp_s` values over the same bundle. Records tile
  with no sampler pause (328k-record evidence, PR #245); the draft's
  "sampler pauses" mechanism sentence is corrected in round 7.

Both rows remain STOP_FILL / VALUE_UNISSUED: ratification fixes the
statistic and its supplier route before any value is computed; the values
are issued only through the declared route at round-7 fill time, each with
its ratification artifact. The cited-bundle multiplicity hazard (the capture
resolves five ways across corpora — projection anomaly 3) is closed by the
path+SHA-256 requirement.
