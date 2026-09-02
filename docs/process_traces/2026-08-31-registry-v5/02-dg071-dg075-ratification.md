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

## Addendum 2026-09-02 (magistrate) — population, arithmetic, method disclosure, DG-075 dependence

Forcing finding: two independent physics/execution refuters (Sol 245, Opus
246) and a blind Fable seat, all in
`../2026-09-02-paper-d-dg071/` (files 12, 13, 15), found that the producer
implementing this ratification counted every width three times. The cause is
the magistrate's own seat ruling R-167-1 (file 03 there), which glossed
"every retained record" as every CSV row without inspecting the bundle: the
retained `power_trace.csv` holds one row per rail (`cpu_power`,
`gpu_power`, `ane_power`) per sampler record, all three rows carrying the
same `interval_start_s`/`interval_end_s`. R-167-1 is WITHDRAWN where it
conflicts with this addendum; the addendum is the ONE home for these
conventions and the producer cites it, not R-167-1.

1. **Population (DG-071).** "Every retained record" means every SAMPLER
   RECORD: the rows sharing one `timestamp_s`, collapsed to one width. The
   producer REFUSES (`record_rail_set_mismatch`) unless every record has
   exactly the three rails above with byte-identical
   `interval_start_s`/`interval_end_s`; it never averages or picks a rail.
   The 1218-row artifact issued at `a3dadadd` is withdrawn. The artifact
   reports "sampler records: 406; rail rows: 1218" and never calls a rail
   row a record.
2. **Arithmetic and digits.** Endpoints are parsed from the CSV literals
   with exact decimal arithmetic (`decimal.Decimal(<string>)`, never
   through `float`); widths, spacings, quantiles and IQR are computed
   exactly. The VALUES OF RECORD are the exact decimal seconds, written in
   the JSON as strings. Milliseconds are renderings: value × 1000 rounded
   to FOUR decimals, round-half-to-even, the rule stated in the artifact,
   which also states that a float64 replication (numpy, R defaults) is
   guaranteed to agree only to three decimals because a float64 at 1.78e9 s
   has spacing 2.4e-7 s, coarser than the file's 1e-7 s literals (worked
   example in the artifact: median 120.9186 ms exact vs 120.9185 ms float).
   The digits characterise the retained bytes, not the sampler's physical
   timing resolution, and the artifact says so.
3. **Method disclosure.** The ratification statistic is: order the n
   values ascending; quantile at fraction p = the value at position
   h = (n−1)·p (0-based), linearly interpolated between the two
   neighbouring order statistics (Hyndman–Fan type 7; numpy `linear`;
   R type 7 — library names are cross-references, the formula is the
   definition); median = the p = 0.5 quantile (for even n, the mean of the
   two middle values); IQR = Q3 − Q1 computed exactly before rendering (so
   the rendered IQR may differ from the difference of the rendered
   quartiles by one unit in the last place). The artifact states this
   definition in full.
4. **DG-075 stays a separate row** with a dependence sentence: it is the
   DG-071 distribution minus the first record, because every record's
   `interval_end_s` equals its `timestamp_s` and its `interval_start_s`
   equals the previous record's `timestamp_s` to within one float64 ulp
   (≤ 2.4e-7 s, 100 of 405 boundaries differ by exactly that; the writer
   formatted two floats). The producer verifies tiling on the pinned bytes
   (`interval_end_s == timestamp_s` for every record and
   max |`interval_start_s`(k) − `timestamp_s`(k−1)| ≤ 1e-6 s) and REFUSES
   (`records_do_not_tile`) otherwise; the round-7 draft's "sampler pauses"
   mechanism sentence is already scheduled for correction (parked structural
   edits) and is not touched here. Retiring or merging DG-075 is a round-7
   draft decision, not a registry decision.

Instrument: dated addendum by the same authority that issued the
ratification, three seats concurring on executed evidence, diagnostic-era
rows only (D-161 honest-drift threat model). A cold gate becomes mandatory
on a same-signature re-audit failure, on any change to the draft's
definitions, or if either row is promoted to claim-bearing. One
execution-lens delta re-audit of the re-issued artifact is still owed.

### Executed evidence (magistrate, 2026-09-02, from `/Users/edr/code/JouleWise`)

```
$ python3 docs/process_traces/2026-09-02-paper-d-dg071/14a-dg071-bench.py
rows 1218 records 406
records not exactly {cpu,gpu,ane} with identical interval: 0
max decimals in timestamp_s 7
float64 rows(1218) q1/med/q3 ms [116.951942, 120.918512, 122.92695] iqr 5.975008
float64 recs(406)  q1/med/q3 ms [116.97197, 120.918512, 122.922659] iqr 5.950689
Decimal recs(406) q1/med/q3 ms ['116.971950000', '120.91860000', '122.922700000'] iqr 5.950750000
ulp(1.78e9) s = 2.384185791015625e-07 => ms 0.0002384185791015625
DG-075 float64 405 q1/med/q3 ms [117.032051, 120.922327, 122.92695]
widths[1:] == diffs? False n 405
min width ms 111.83953285217285 count<112.5ms 6 in band 111.8-112.5 6
records whose interval_start_s != previous timestamp_s: 100 max gap us 0.2384185791015625
interval_end_s == timestamp_s for all records: True
```

(File 14a reads the bundle by its repo-relative path, so it runs only from
a checkout that holds the retained corpus — the main checkout, not a linked
worktree.)
