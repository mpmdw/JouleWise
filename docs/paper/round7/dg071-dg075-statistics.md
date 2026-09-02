# DG-071 / DG-075 issued statistics

- Input: `/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
- Input SHA-256: `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`
- Retained record count: 1218
- Distinct timestamp count: 406
- Duplicate timestamps dropped: 812
- Producer: `scripts/issue_dg071_dg075_statistics.py`
- Producer SHA-256: `048d8bb20fcdea9ecd61d4c1bce8c76882c540dc5c7e80391a4f075f5e231ce2`
- Git commit: `3fca7d6ba7c377b9b2c8e87b160552330fb1ddae`

Milliseconds are renderings rounded to six decimals. The unrounded 
seconds below are the issued values of record.

| Registry row | Sample count | Median (ms) | IQR (ms) |
|---|---:|---:|---:|
| DG-071 | 1218 | 120.918512 | 5.975008 |
| DG-075 | 405 | 120.922327 | 5.894899 |

| Registry row | Q1 (s) | Median (s) | Q3 (s) | IQR (s) |
|---|---:|---:|---:|---:|
| DG-071 | 0.11695194244384766 | 0.12091851234436035 | 0.12292695045471191 | 0.005975008010864258 |
| DG-075 | 0.11703205108642578 | 0.12092232704162598 | 0.12292695045471191 | 0.005894899368286133 |
