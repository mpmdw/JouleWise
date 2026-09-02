# DG-071 / DG-075 issued statistics

- Input: `runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
- Input SHA-256: `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`
- Retained record count: 1218
- Distinct timestamp count: 406
- Duplicate timestamps dropped: 812
- Producer: `scripts/issue_dg071_dg075_statistics.py`
- Producer SHA-256: `6efc3ec75ca6f59a86b8a68ff1049abbb5fba4cdf4500cb585ee3b13ead62f51`
- Git commit: `681f30ce6c4f2afd5325cc944150643f63739185`

Milliseconds are renderings rounded to six decimals. The unrounded 
seconds below are the issued values of record.

| Registry row | Sample count | Q1 (ms) | Median (ms) | Q3 (ms) | IQR (ms) |
|---|---:|---:|---:|---:|---:|
| DG-071 | 1218 | 116.951942 | 120.918512 | 122.926950 | 5.975008 |
| DG-075 | 405 | 117.032051 | 120.922327 | 122.926950 | 5.894899 |

| Registry row | Q1 (s) | Median (s) | Q3 (s) | IQR (s) |
|---|---:|---:|---:|---:|
| DG-071 | 0.11695194244384766 | 0.12091851234436035 | 0.12292695045471191 | 0.005975008010864258 |
| DG-075 | 0.11703205108642578 | 0.12092232704162598 | 0.12292695045471191 | 0.005894899368286133 |
