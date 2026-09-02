# Blind seat packet — DG-071/DG-075 statistic convention amendment (2026-09-02)

You are a fresh, context-free Fable seat. Read ONLY what this packet names.
Do not read README/RUN_STATE/TASK_QUEUE/docs/orchestration.md/CLAUDE*.md or
any memory. Write nothing under any git checkout; scratch goes under a
subdirectory you create in
`<scratchpad>/`.
Disclose anything you read outside the packet.

## Background (facts, each executed at the bench by the magistrate on 2026-09-02; re-verify any you rely on)

The paper's §6 has two diagnostic-era placeholders: DG-071 "sampling-record
interval width" and DG-075 "record spacing", both for the retained bundle
`/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
(SHA-256 `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`;
read-only). A magistrate ratification on 2026-08-31
(`/Users/edr/code/JouleWise-wt-paper-d/docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md`)
fixed the statistics as:

- DG-071: median with IQR of `interval_end_s − interval_start_s` "over every
  retained record" of the bundle;
- DG-075: median with IQR of differences between consecutive UNIQUE
  `timestamp_s` values over the same bundle.

A producer (`/Users/edr/code/JouleWise-wt-paper-d/scripts/issue_dg071_dg075_statistics.py`
at commit `a3dadadd`) implemented this literally and issued
`/Users/edr/code/JouleWise-wt-paper-d/docs/paper/round7/dg071-dg075-statistics.md`
(read it). Two independent refuters (Sol xhigh, Opus 5) then found the same
four defects; their reports are
`<scratchpad>/out/245-sol-paper-d-physics.md`
and `.../out/246-opus-paper-d-physics.md` (read both; the `## P1`–`## P4`
sections are the ones that matter).

Executed at the bench (script `<scratchpad>/dg071-bench.py`,
run from `/Users/edr/code/JouleWise`):

```
rows 1218 records 406
records not exactly {cpu,gpu,ane} with identical interval: 0
max decimals in timestamp_s 7
float64 rows(1218) q1/med/q3 ms [116.951942, 120.918512, 122.92695] iqr 5.975008
float64 recs(406)  q1/med/q3 ms [116.97197, 120.918512, 122.922659] iqr 5.950689
Decimal recs(406) q1/med/q3 ms ['116.971950000', '120.91860000', '122.922700000'] iqr 5.950750000
ulp(1.78e9) s = 2.384185791015625e-07 => ms 0.0002384185791015625
DG-075 float64 405 q1/med/q3 ms [117.032051, 120.922327, 122.92695]
min width ms 111.83953285217285 count<112.5ms 6 in band 111.8-112.5 6
records whose interval_start_s != previous timestamp_s: 100   (all differ by ≤ 0.24 µs = one float64 ulp)
```

So: (1) the CSV has one row per rail (cpu, gpu, ane) per sampler record;
all three rows of a record carry identical intervals, so the issued DG-071
counts each width three times ("Sample count 1218"). (2) Timestamps are
~1.78e9 s written with 7 decimals; parsing to float64 loses resolution
(ulp 2.4e-7 s = 2.4e-4 ms), yet the artifact renders milliseconds to six
decimals. (3) The quartile method (numpy `linear` = Hyndman–Fan type 7) is
not named in the ratification or the artifact. (4) DG-075 is, up to
one-ulp writer artifacts and the first record, the same sample as DG-071
shifted by one record.

These are DIAGNOSTIC-era values (an a10 resolvability example in §6), not
headline claims. The threat model (D-161) is honest drift, not forgery.

## Questions — rule each, verdict + operative text + biting counterfactual + what it does NOT decide

Q1 (population). Amend the ratification so DG-071's population is the 406
sampler records (rails collapsed; the producer REFUSES if any record's rows
are not exactly the three rails with identical intervals), or keep "every
retained row" and disclose it? Which reading does the paper sentence
"sampling-record interval width" require?

Q2 (precision). Which of: (a) parse endpoints from text with `Decimal`,
issue exact-decimal seconds as the values of record and render
milliseconds to FOUR decimals (the CSV's own 1e-7 s resolution); (b) keep
float64 and render to THREE decimals (below the ulp error 2.4e-4 ms); (c)
other. State the rendered digits a reader may trust and why.

Q3 (method disclosure). Must the ratification addendum AND the issued
artifact name the quartile definition (Hyndman–Fan type 7 / numpy
`linear`, median = mean of the two middle values for even n)? Is the
median convention for even n part of it?

Q4 (DG-075). Given (4), should DG-075 stay a separate issued row (as
ratified) with its fill sentence saying it is the same record-period
distribution apart from endpoint convention, or be retired in favour of
DG-071? The draft is byte-frozen until round 7, so only the registry row
and fill sentence are in play now.

Q5 (process). Is amending a magistrate ratification by dated addendum —
same authority, two independent seats concurring, executed evidence — the
right instrument here, or does it need a fuller cold gate? One paragraph.

Deliverable: write your sealed ruling to
`<scratchpad>/out/seat-blind-fable-dg071.md`
(header: disclosure of contamination; then Q1–Q5). Your final message to
the caller is the five verdict lines only.
