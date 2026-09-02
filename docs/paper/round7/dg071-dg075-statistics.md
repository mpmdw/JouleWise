# DG-071 / DG-075 issued statistics

- Input: `runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv`
- Input SHA-256: `6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9`
- Sampler records: 406
- Rail rows: 1218
- Rails: ane_power, cpu_power, gpu_power
- Largest tiling gap (s; defined under Method): 0.0000004
- Boundaries with a nonzero tiling gap (see Method): 100
- Producer: `scripts/issue_dg071_dg075_statistics.py`
- Producer SHA-256: `404e6a5614619dbb03916016b0284addfff3ce2458a5ea31ce60be834a16b859`
- Producer commit (last commit that changed the producer; defined under Method): `701471732488b56952beb47393e08c68285a5ea2`

## Method

A sampler record is one contiguous group of CSV rows — consecutive rows in file order — that share one `timestamp_s` literal. A literal is the character string exactly as written in the file, before any numeric conversion; two literals are equal only when their characters are identical. Every group must contain exactly one row for each of `ane_power`, `cpu_power` and `gpu_power`, and the three rows' `interval_start_s` and `interval_end_s` literals must be identical; a timestamp literal that reappears after another group has begun is refused. DG-071 uses one interval width, `interval_end_s − interval_start_s`, per sampler record.

The timestamp and endpoint literals are parsed directly as exact decimals. Widths, spacings, quantiles and IQR never pass through binary floating point.

For the n values sorted ascending, the quantile at probability p uses the exact 0-based position h = (n−1)·p and exact linear interpolation between the two neighbouring order statistics — the sorted values at positions ⌊h⌋ and ⌊h⌋+1 (Hyndman–Fan type 7; numpy `linear` and R type 7 are cross-references). The median is the p = 0.5 quantile, which is the mean of the two middle values for even n. IQR is Q3 − Q1, computed exactly before rendering.

The exact seconds in the second table are the values of record: the authoritative numbers, which nothing downstream re-derives. The millisecond columns are renderings of them — value × 1000, rounded to four decimal places with round-half-even, meaning a value exactly halfway between two four-decimal neighbours goes to the one whose last digit is even — and are never re-used as inputs. Because rounding is applied after subtraction, a rendered IQR can differ from the difference of the rendered quartiles by one unit in the last place.

A float64 replication (numpy `linear`, R type 7) is guaranteed to agree only to three decimals because a float64 at 1.78e9 s has spacing 2.4e-7 s, coarser than the file's 1e-7 s literals; the digits characterise the retained bytes, not the sampler's physical timing resolution. Worked example: median 120.9186 ms exact vs 120.9185 ms float64.

Tiling. The records tile when each record's interval ends exactly at its own timestamp (`interval_end_s` literal identical to `timestamp_s` literal) and begins where the previous record ended (`interval_start_s` of record k within 0.000001 s of `timestamp_s` of record k−1); the producer refuses otherwise. The tiling gap at a boundary is |interval_start_s(k) − timestamp_s(k−1)| in exact decimal seconds; the header reports the largest gap and the number of boundaries whose gap is not zero. In this bundle 100 of 405 boundaries have a nonzero gap, the largest 0.0000004 s: the writer formatted the interval endpoints and the timestamp from two separately rounded binary floats, so the seventh decimal can differ. This is the endpoint convention referred to next.

DG-075 is the DG-071 distribution minus the first record: its consecutive timestamp differences equal the widths of records 2–n up to the endpoint convention above, i.e. to within the largest tiling gap.

Provenance. The producer commit is the last commit in the repository's history that changed the producer script (`git log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py`), not the commit the issuer happened to have checked out. A committed artifact cannot name the commit that contains it, so recording the checkout would make byte-exact replay impossible at exactly the commit a reader checks out; recording the script's last commit means re-running the producer from any checkout in which the script is unchanged since that commit reproduces both files byte for byte. The producer SHA-256 is recorded beside it: an uncommitted edit to the producer shows as a mismatch between the two.

| Registry row | Sample count | Q1 (ms) | Median (ms) | Q3 (ms) | IQR (ms) |
|---|---:|---:|---:|---:|---:|
| DG-071 | 406 | 116.9720 | 120.9186 | 122.9227 | 5.9508 |
| DG-075 | 405 | 117.0321 | 120.9224 | 122.9270 | 5.8949 |

| Registry row | Q1 (s) | Median (s) | Q3 (s) | IQR (s) |
|---|---:|---:|---:|---:|
| DG-071 | 0.116971950 | 0.12091860 | 0.122922700 | 0.005950750 |
| DG-075 | 0.1170321 | 0.1209224 | 0.122927 | 0.0058949 |
