# DG-071 / DG-075 issued statistics

- Input: `runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
- Input SHA-256: `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`
- Sampler records: 406
- Rail rows: 1218
- Rails: ane_power, cpu_power, gpu_power
- Maximum absolute tiling gap (s): 0.0000004
- Nonzero tiling-gap boundaries: 100
- Producer: `scripts/issue_dg071_dg075_statistics.py`
- Producer SHA-256: `d769f05b050d56e49e55b1aac3d30a21e1a1ad7ddd181f7d15ad62988edf4899`
- Git commit: `29181d6cdf7bcea89540c52eba39965363f5446f`

## Method

A sampler record is one contiguous group sharing an exact `timestamp_s` literal. Every group must contain exactly one row for each of `ane_power`, `cpu_power`, and `gpu_power`, with byte-identical `interval_start_s` and `interval_end_s` literals. DG-071 uses one exact interval width per sampler record.

The timestamp and endpoint literals are parsed directly as exact decimals. Widths, spacings, quantiles, and IQR never pass through binary floating point.

For the n values sorted ascending, the quantile at probability p uses the exact 0-based position h = (n−1)·p and exact linear interpolation between the two neighbouring order statistics (Hyndman–Fan type 7; numpy `linear` and R type 7 are cross-references). Median is the p = 0.5 quantile, which is the mean of the two middle values for even n. IQR is Q3 − Q1, computed exactly before rendering.

Exact seconds below are JSON-string values of record. Milliseconds are renderings: value × 1000 rounded to four decimal places with round-half-even. A separately rendered IQR can differ from the difference of rendered quartiles by one unit in the last place.

A float64 replication (numpy `linear`, R type 7) is guaranteed to agree only to three decimals because a float64 at 1.78e9 s has spacing 2.4e-7 s, coarser than the file's 1e-7 s literals; the digits characterise the retained bytes, not the sampler's physical timing resolution.

Worked example: median 120.9186 ms exact vs 120.9185 ms float64.

DG-075 is the DG-071 distribution minus the first record: every record's `interval_end_s` literal equals its `timestamp_s` literal, and every later `interval_start_s` is within 0.000001 s of the previous timestamp; its consecutive timestamp differences are the widths of records 2–n up to the retained writer's endpoint convention.

| Registry row | Sample count | Q1 (ms) | Median (ms) | Q3 (ms) | IQR (ms) |
|---|---:|---:|---:|---:|---:|
| DG-071 | 406 | 116.9720 | 120.9186 | 122.9227 | 5.9508 |
| DG-075 | 405 | 117.0321 | 120.9224 | 122.9270 | 5.8949 |

| Registry row | Q1 (s) | Median (s) | Q3 (s) | IQR (s) |
|---|---:|---:|---:|---:|
| DG-071 | 0.116971950 | 0.12091860 | 0.122922700 | 0.005950750 |
| DG-075 | 0.1170321 | 0.1209224 | 0.122927 | 0.0058949 |
