VERDICT: BLOCKER 1 / SHOULD-FIX 4 / NIT 1

Refuter: Opus 5, EXECUTION + PHYSICS lens.
Checkout `/Users/edr/code/JouleWise-wt-paper-d`, HEAD `a3dadaddda58dc0548a47cb4c333a3249c1ca41e`, branch `feat/2026-09-02-paper-d`.
Bundle SHA-256 verified before use:

```text
$ shasum -a 256 /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv
6945160964bc8667f4bfcc1ba7b500f81045fce8301ef7aadce45a188d3e06e9  .../power_trace.csv
```

Nothing was written under any git checkout; `git status --short` in the worktree was empty after all work (shown in P6).

## Findings

| id | severity | title | file:line |
|---|---|---|---|
| B-1 | blocker | DG-071 is issued over 1218 CSV rows = 406 sampler records counted three times (once per rail); the counted record support sums to 146.41 s inside a 48.80 s trace, and Q1/Q3/IQR differ from the record-level values at the issued precision | `docs/paper/round7/dg071-dg075-statistics.json:21,37` and `docs/paper/round7/dg071-dg075-statistics.md:5` (producer convention stated at `scripts/issue_dg071_dg075_statistics.py:18`) |
| S-1 | should_fix | Six-decimal-millisecond renderings and 17-digit "unrounded seconds of record" assert ~200x more precision than the arithmetic carries; exact-decimal arithmetic on the same CSV gives different digits from the 4th ms decimal on | `scripts/issue_dg071_dg075_statistics.py:75,131-134,195` |
| S-2 | should_fix | Neither artifact discloses the quantile definition, the median convention, or the sample population, so the issued numbers cannot be replicated from the artifact | `docs/paper/round7/dg071-dg075-statistics.md:12-13` |
| S-3 | should_fix | 4 of 17 refusal sites have a test asserting their reason; a mutant deleting the `record_interval_not_positive` raise survives all 8 tests. luna SF-3 was recorded "cured" by terra 185 on the strength of one guard | `scripts/issue_dg071_dg075_statistics.py:196-200`; `tests/test_issue_dg071_dg075_statistics.py:29-233` |
| S-4 | should_fix | DG-075's median exceeds DG-071's by 0.003815 ms, which reads as the "sampler pauses" mechanism the frozen draft still asserts; the gap is entirely the dropped first record plus the B-1 rail tripling | `docs/paper/draft-v1.md:256`; `docs/paper/round7/dg071-dg075-statistics.md:17-18` |
| N-1 | nit | Ruling `R-167-1`, which the producer says fixes the population and quantile conventions, has no artifact anywhere in the checkout — it appears only inside the producer's own docstring | `scripts/issue_dg071_dg075_statistics.py:14,98` |

---

## P1 — Record multiplicity

### Census

```text
$ awk -F, 'NR>1{print $4}' /Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv | sort | uniq -c
 406 ane_power
 406 cpu_power
 406 gpu_power
```

Grouping the 1218 data rows by the triple `(timestamp_s, interval_start_s, interval_end_s)` (script `opus-paper-d/p1_p4.py`):

```text
rows: 1218
distinct (ts,start,end) triples: 406
group size histogram: Counter({3: 406})
rail-set histogram: Counter({('ane_power', 'cpu_power', 'gpu_power'): 406})
```

Every one of the 406 sampler records appears exactly three times, once per rail, carrying the identical interval. The file is a long-format rendering of a wide record; the rail is a *column* of a record, not a record.

### (a) Do the tripled statistics differ from the record-level ones?

Yes — in Q1, Q3 and IQR, at the issued six decimals. Median is unaffected.

```text
DG-071 over 1218 rows:            n=1218 q1_ms=116.951942 med_ms=120.918512 q3_ms=122.926950 iqr_ms=5.975008
DG-071 over 406 distinct records: n=406  q1_ms=116.971970 med_ms=120.918512 q3_ms=122.922659 iqr_ms=5.950689
identical to repr? q1: False med: True q3: False iqr: False
ms deltas: q1 -0.020028  med 0.0  q3 +0.004291  iqr +0.024319
```

The IQR delta, 0.024319 ms, is 24 319 times the last issued digit and 0.41 % of the issued IQR. The 1218-row Q1 is exactly the 406-record `lower`/`nearest` order statistic, not its type-7 interpolant: tripling every value collapses the quartile onto a run of three identical entries, so the interpolation weight vanishes (see P2).

### (b) What does "every retained record" mean, physically?

The physical answer is settled by wall time. Summing the exact decimal widths:

```text
trace span (first interval_start -> last timestamp), s: 48.8018784
sum of the 406 exact widths, s:                         48.8018768
sum of all 1218 row widths, s:                         146.4056304
mean record rate over span, Hz:                          8.3193519
```

The 406 record widths tile the trace to within 1.6 us over 48.8 s. The 1218-row population claims 146.41 s of record support inside a 48.80 s trace — exactly 3x the elapsed time. A population of "records" whose supports triple-cover wall time is not a population of records, and it contradicts the same ratification's own "records tile with no sampler pause" (`docs/process_traces/2026-08-31-registry-v5/02-dg071-dg075-ratification.md:14-15`).

The paper sentence names the quantity unambiguously (`docs/paper/draft-v1.md:256`, read this session):

> The **sampling-record interval width** is how long one power record covers — the width of its support in time — and for this bundle it is [PENDING] …

and the registry row repeats it (`docs/paper/results-fill-registry.md:643`): "DG-071 — Section 6 sampling-record interval width, line 256 … over every retained record in the cited R03P". There are 406 sampling records. The artifact reports `Retained record count: 1218` (`docs/paper/round7/dg071-dg075-statistics.md:5`) and `Duplicate timestamps dropped: 812` (`:7`) — but 812 is not duplicated sampling, it is two further rails per record. A reader is told the sampler emitted 1218 records of median width 121 ms; the arithmetic 1218 x 0.1209 s = 147 s against a 48.8 s trace is checkable in one line by any reviewer, and metrology is this paper's subject.

Compounding it, the two issued rows sit in one table with `Sample count` 1218 and 405 for two descriptions of the same physical period distribution.

The producer is faithful to its stated convention — `scripts/issue_dg071_dg075_statistics.py:18` "every CSV row included without filtering" — so the defect is in the convention, not the code. That convention is attributed to Ruling `R-167-1`, which has no artifact in the tree (N-1).

**What the artifact/registry must say if the ruling stands as-is:** the row label must stop calling this the sampling-record interval width. If the intended quantity is the sampling-record interval width (as the frozen draft and the registry row both say), the fill must be re-issued over the 406 distinct records — median unchanged at 120.918512 ms, but Q1 116.971970, Q3 122.922659, IQR 5.950689 ms — and the artifact must report `Sampler records: 406` with the rail multiplicity stated. Severity is blocker because it is a wrong-population defect in an issued value of record, it is internally inconsistent with the tiling physics in the same ratification, and no prose edit cures it.

## P2 — Quartile method

`_quantile` (`scripts/issue_dg071_dg075_statistics.py:99-113`) computes `position = fraction * (n - 1)` and interpolates linearly between the bracketing order statistics. That is **Hyndman & Fan type 7** — numpy's default `method="linear"`, R's default `type = 7`, and the `"linear"`/`"inclusive"` convention of `numpy.percentile`. Executed confirmation against numpy 2.5.1 on the 406-width record-level sample, all eleven numpy methods:

```text
numpy 2.5.1
n=406 method=linear                   q1_ms=116.971970 q3_ms=122.922659 iqr_ms=5.950689   <-- matches _quantile
n=406 method=lower                    q1_ms=116.951942 q3_ms=122.909784 iqr_ms=5.957842
n=406 method=higher                   q1_ms=117.032051 q3_ms=122.926950 iqr_ms=5.894899
n=406 method=midpoint                 q1_ms=116.991997 q3_ms=122.918367 iqr_ms=5.926371
n=406 method=nearest                  q1_ms=116.951942 q3_ms=122.926950 iqr_ms=5.975008
n=406 method=inverted_cdf             q1_ms=116.951942 q3_ms=122.926950 iqr_ms=5.975008
n=406 method=averaged_inverted_cdf    q1_ms=116.951942 q3_ms=122.926950 iqr_ms=5.975008
n=406 method=hazen                    q1_ms=116.951942 q3_ms=122.926950 iqr_ms=5.975008
n=406 method=weibull                  q1_ms=116.936982 q3_ms=122.927964 iqr_ms=5.990982
n=406 method=median_unbiased          q1_ms=116.946956 q3_ms=122.927288 iqr_ms=5.980333
n=406 method=normal_unbiased          q1_ms=116.948202 q3_ms=122.927204 iqr_ms=5.979002
n=406 numpy median_ms=120.918512  statistics.median_ms=120.918512
```

`_quantile` reproduces `method="linear"` exactly at the issued six decimals and differs from ten of the eleven alternatives, so the identification is unambiguous.

On the issued 1218-row sample the method is unidentifiable, because the tripling makes every definition agree:

```text
n=1218 method=linear/lower/higher/midpoint/nearest/inverted_cdf/averaged_inverted_cdf/
              hazen/weibull/median_unbiased/normal_unbiased
              -> q1_ms=116.951942 q3_ms=122.926950 iqr_ms=5.975008  (all eleven identical)
```

On the 405-spacing DG-075 sample the method **is** identifying again (`hazen` 117.011964 / `weibull` 116.991878 / `median_unbiased` 117.005269 vs the issued 117.032051).

**Does the ratification pin a method?** No. `02-dg071-dg075-ratification.md` says only "median with IQR"; the pinning is asserted by the producer's docstring citation to `R-167-1`, which is not in the tree (N-1).

**Does the artifact disclose it?** No — and this is S-2. The Markdown discloses only "Milliseconds are renderings rounded to six decimals. The unrounded seconds below are the issued values of record" (`docs/paper/round7/dg071-dg075-statistics.md:12-13`); the JSON adds only `"statistic": "interval_end_s - interval_start_s"`. Absent from both: the quantile definition (type 7), the median convention (`statistics.median`, i.e. mean of the two middle values at even n, not the low median), that IQR is the plain Q3 - Q1 of those, and — most consequentially — that the sample is CSV rows rather than sampler records. A reader who does the natural thing (406 records, R/numpy defaults) gets 116.971970, not the issued 116.951942; a reader who uses 406 records with `nearest`, `hazen` or `inverted_cdf` reproduces the issued digits by coincidence and concludes wrongly that they replicated. That fails Ed's replication bar in both directions.

## P3 — DG-075 vs DG-071 physics

They are the same sample, shifted by one record, to within one float ulp.

```text
unique timestamps: 406
ts already ascending in file order: True
records where interval_end_s != timestamp_s:                                    0   (of 406)
records (after first) where interval_start_s != previous distinct timestamp_s: 100   (of 405)
first 5 mismatches (prev_ts, start, delta_s):
  (1784978889.5679703, 1784978889.5679705,  2.384185791015625e-07)
  (1784978889.6909783, 1784978889.690978,  -2.384185791015625e-07)
  (1784978890.0619888, 1784978890.061989,   2.384185791015625e-07)
  (1784978890.1861742, 1784978890.186174,  -2.384185791015625e-07)
  (1784978890.4331727, 1784978890.433173,   2.384185791015625e-07)
```

`interval_end_s == timestamp_s` for all 406 records. `interval_start_s` equals the previous record's timestamp for 305 of 405 boundaries exactly (as CSV strings) and for the other 100 differs by one float64 ulp at 1.785e9 s. Checking the raw decimal strings rather than the parsed floats:

```text
boundaries with nonzero exact-decimal gap: 100 of 405
distinct nonzero gap values (s): -4E-7, -3E-7, -2E-7, -1E-7, 1E-7, 2E-7, 3E-7
max |gap| s: 4E-7
boundaries where the interval_start_s STRING == previous timestamp_s STRING: 305 of 405
```

So the tiling is real to within 0.4 us (3 parts per million of a record) and the residual is last-digit noise in the writer, not a sampler pause. **"Records tile with no sampler pause" is confirmed.**

Consequence: DG-075's 405 spacings are element-wise the 405 widths of records 2..406, up to that ulp.

```text
element-wise float differences between DG-075 spacings and widths[2..406]: 100 of 405
max |elementwise diff| s: 2.384185791015625e-07
sorted multisets identical? False
```

The multisets are not bitwise identical, yet the perturbations are far too small to move the order statistics at the quartile positions, so the four issued statistics come out **bitwise identical**:

```text
DG-075 spacings (405):           q1_s=0.11703205108642578 med_s=0.12092232704162598 q3_s=0.12292695045471191 iqr_s=0.005894899368286133
widths of records 2..406 (405):  q1_s=0.11703205108642578 med_s=0.12092232704162598 q3_s=0.12292695045471191 iqr_s=0.005894899368286133
DG-075 stats == widths[1:] stats? True
```

**DG-075 carries no information independent of DG-071.** It is DG-071's sample with its first record removed.

### Is the Q1 difference entirely the one dropped record?

No — 75 % of it is, and 25 % is the P1 rail tripling.

```text
Q1 ms: 1218-row =116.951942 | 406-record =116.971970 | 405 drop-first =117.032051 | DG-075 spacings =117.032051
gap issued DG-075 - issued DG-071 Q1 (ms): 0.080109
  attributable to dropped record: 0.060081
  attributable to rail tripling : 0.020027
dropped record 1 width_s: 0.11188864707946777  (111.888647 ms — the 2nd smallest of the 406 widths)
```

The dropped record is the second-smallest width in the bundle, which is why removing it lifts Q1 disproportionately.

### S-4 — the residual reads as the mechanism the draft asserts

`docs/paper/draft-v1.md:256` (frozen) says record spacing "is longer than the width because the sampler pauses between records". The issued fill would put 120.922327 ms (DG-075) beside 120.918512 ms (DG-071) — spacing larger than width by 0.003815 ms — which numerically *corroborates* the very mechanism the ratification says is false and is to be corrected in round 7. Nothing in either artifact tells the reader that the two rows are one sample minus one record plus a 3x weighting difference. The round-7 correction must therefore also state that DG-075 is DG-071's sample shifted by one record, or the two numbers will be read as independent confirmation of a pause that does not exist.

## P4 — Float and rounding

### The plumbing is clean

Executed against the committed artifacts:

```text
DG-071 all four *_s reprs present verbatim in the Markdown: True
DG-071 every *_ms == round(*_s*1000, 6): True
DG-071 iqr_s == q3_s - q1_s exactly: True | iqr_ms == q3_ms-q1_ms? True
DG-075 all four *_s reprs present verbatim in the Markdown: True
DG-075 every *_ms == round(*_s*1000, 6): True
DG-075 iqr_s == q3_s - q1_s exactly: True | iqr_ms == q3_ms-q1_ms? True
all JSON *_s literals round-trip exactly through float/repr: True
```

The JSON carries exactly the values the Markdown prints as `repr`; `round(x*1000.0, 6)` at `scripts/issue_dg071_dg075_statistics.py:131-134` is the only rounding; `:.6f` in `render_markdown` only pads an already-rounded value; IQR is computed in seconds before any rounding. **Confirmed as claimed.**

### S-1 — but the digits being carried are not real

The subtraction itself is exact (Sterbenz: `end` and `start` are within a factor of 2, so `end - start` is representable and computed exactly in float64). The loss is upstream, in `float(value)` on the two large absolute timestamps.

```text
ulp of timestamp ~1.785e9 s: 2.384185791015625e-07 s  -> 0.000238 ms
ulp of a width    ~0.12   s: 1.3877787807814457e-17 s -> 1.4e-14 ms
max |float width - exact decimal width| over the 406 records: 1.851043701171875e-07 s = 0.000185 ms
```

Each parsed endpoint is a rounding of its decimal string to within half an ulp of 1.785e9 s, so each width inherits up to ~2.4e-7 s of representation error — measured maximum 1.85e-7 s. The input's own resolution is coarser still than six ms decimals:

```text
sample exact widths (s): 0.1118886, 0.1158752, 0.1178830, 0.1235535, 0.1230078, 0.1232598
decimal exponent (places) set: [5, 6, 7]
```

The CSV records widths to at most 7 decimal places of seconds, i.e. **1e-4 ms**. `MS_DECIMALS = 6` (`scripts/issue_dg071_dg075_statistics.py:75`) renders 1e-6 ms — a 100x precision overclaim against the input and a ~200x overclaim against the arithmetic's own 2.4e-4 ms error floor.

Recomputing the identical ruled statistic with `decimal.Decimal` on the same CSV strings (same population of 1218 rows, same type-7 quantiles, same `statistics.median`):

| quantity | issued (float64) | exact decimal | delta (ms) | multiples of the last issued digit |
|---|---:|---:|---:|---:|
| Q1 (ms) | 116.951942 | 116.9519 | 4.2e-5 | 42 |
| Median (ms) | 120.918512 | 120.9186 | 8.8e-5 | 88 |
| Q3 (ms) | 122.926950 | 122.9270 | 5.0e-5 | 50 |
| IQR (ms) | 5.975008 | 5.9751 | 9.2e-5 | 92 |

```text
EXACT-decimal over the 1218 rows: q1_ms=116.951900000 med_ms=120.9186000 q3_ms=122.92700000 iqr_ms=5.975100000
ISSUED (float)                   : q1_ms=116.951942    med_ms=120.918512 q3_ms=122.926950   iqr_ms=5.975008
```

Every issued millisecond value is wrong from its fourth decimal onward relative to the exactly-recorded input. The recorded median width is 120.9186 ms exactly; the artifact issues 120.918512 ms and declares `0.12091851234436035` "the issued value of record", where the recorded truth is `0.1209186`. Ten of those seventeen significant digits are an artifact of representing a 1.785e9 s absolute in binary.

Physically the error is ~1 ppm and immaterial to any use of these rows (the registry marks them NON_CLAIM_BEARING), which is why this is should_fix and not blocker. But a metrology paper that issues digits it cannot support, and calls them values of record, invites exactly the reviewer question it should be pre-empting. The cure is small and local: parse the three timestamp fields with `decimal.Decimal(value)` (the finiteness and float checks can stay), subtract in Decimal, and set `MS_DECIMALS = 4` — the input's real resolution.

## P5 — Refusals at the production site

The module's own suite passes as expected:

```text
$ TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics -v
test_cli_refusal_is_nonzero_and_names_reason ... ok
test_five_records_have_hand_computable_statistics ... ok
test_missing_required_field_is_refused_without_output ... ok
test_non_monotone_timestamps_are_refused_without_output ... ok
test_two_checkout_roots_produce_byte_identical_json ... ok
test_two_runs_are_byte_identical ... ok
test_wrong_bundle_path_is_refused_without_output ... ok
test_wrong_sha_is_refused_without_output ... ok
Ran 8 tests in 0.108s
OK
```

### Guard census

17 `raise IssuanceRefused` sites (`grep -n 'IssuanceRefused(' scripts/issue_dg071_dg075_statistics.py`, lines 120, 144, 150, 161, 170, 176, 181, 188, 197, 205, 219, 224, 243, 248, 255, 263, 359). Reasons asserted anywhere in the test file (`grep -n 'reason,\|REFUSED '`): `bundle_sha256_mismatch`, `record_field_missing`, `timestamps_non_monotone`, `bundle_path_mismatch`.

| reason | site | test through `main`/`issue_artifacts` | mutant killed? |
|---|---|---|---|
| `bundle_sha256_mismatch` | :255 | `test_wrong_sha_is_refused_without_output` (`issue_artifacts`) | yes |
| `bundle_path_mismatch` | :243 | `test_wrong_bundle_path…`, `test_cli_refusal…` (via `main`) | yes |
| `record_field_missing` | :170 | `test_missing_required_field…` (via `main`, blank `interval_end_s`) | yes |
| `timestamps_non_monotone` | :188 | `test_non_monotone_timestamps…` (`issue_artifacts`) | **yes — demonstrated below** |
| `record_interval_not_positive` | :197 | none | **no — demonstrated below** |
| `record_schema_mismatch` (non-UTF-8) | :144 | none | no |
| `record_schema_mismatch` (bad header) | :150 | none | no |
| `record_schema_mismatch` (extra fields) | :161 | none | no |
| `record_field_invalid` (not a float) | :176 | none | no |
| `record_field_invalid` (not finite) | :181 | none | no |
| `record_set_empty` | :205 | none | no |
| `insufficient_unique_timestamps` | :263 | none | no |
| `statistic_sample_empty` | :120 | none | no |
| `git_commit_unavailable` | :219 | none | no |
| `git_commit_invalid` | :224 | none | no |
| `bundle_path_unavailable` | :248 | none | no |
| `output_path_invalid` | :359 | none | no |

4 of 17. luna 178's SF-3 named "invalid-value, extra-field, non-positive interval, empty-set, insufficient-unique-timestamp, output-extension, and commit-error guards" as untested; terra 185 recorded SF-3 "cured" citing only the new `record_field_missing` test. Every other guard luna named is still untested. That is S-3, and it is a delta-audit gap as much as a code gap.

### Mutant A — `record_interval_not_positive` (survives)

Sandbox is a standalone git repo under TMPDIR holding copies of the two files; nothing in a checkout was touched.

```text
MUTANT A applied: record_interval_not_positive raise deleted
 scripts/issue_dg071_dg075_statistics.py | 5 -----
 1 file changed, 5 deletions(-)
===== tests against MUTANT A =====
........
----------------------------------------------------------------------
Ran 8 tests in 0.108s

OK
```

The mutant survives the entire suite. It is not a harmless guard — feeding a fixture whose third record has `interval_start_s == interval_end_s`:

```text
PRODUCTION: REFUSED record_interval_not_positive: row 4 has interval width 0.0
MUTANT A:   ISSUED n=5 median_ms=2000.0 q1_ms=1000.0  <-- zero-width record admitted
```

This is the guard that stands between the issued median and a merged or zero-width *powermetrics* record silently entering the sample. It has no regression behind it.

### Mutant B — `timestamps_non_monotone` (control, killed)

```text
MUTANT B applied: timestamps_non_monotone raise deleted
FAIL: test_non_monotone_timestamps_are_refused_without_output
AssertionError: IssuanceRefused not raised
Ran 8 tests in 0.115s
FAILED (failures=1)
```

The harness does bite where a test exists; the problem is coverage, not the harness. Both mutants were reverted (`git checkout --`) after each run.

## P6 — Other execution / physics checks

### Replay determinism at HEAD, output outside the repo

`main` (`scripts/issue_dg071_dg075_statistics.py:379-418`) takes an arbitrary `--out` and only `mkdir`s that path's parent, so writing to TMPDIR touches no checkout. Two runs at `a3dadadd`:

```text
wrote <TMPDIR>/replay/a/dg071-dg075-statistics.json   (and .md)
DG-071 median_ms=120.918512 iqr_ms=5.975008
DG-075 median_ms=120.922327 iqr_ms=5.894899
wrote <TMPDIR>/replay/b/dg071-dg075-statistics.json   (and .md)
DG-071 median_ms=120.918512 iqr_ms=5.975008
DG-075 median_ms=120.922327 iqr_ms=5.894899
--- byte compare of the two replays ---
json identical
md identical
--- diff replay@a3dadadd vs committed artifact ---
17c17
<     "git_commit": "a3dadaddda58dc0548a47cb4c333a3249c1ca41e",
---
>     "git_commit": "681f30ce6c4f2afd5325cc944150643f63739185",
json diff rc=1
--- worktree clean? ---
(empty)
```

Every statistic, count, hash and path is bit-identical to the committed artifact; only `git_commit` moves, which is the known and correct behaviour terra 185 recorded. `script_sha256` is unchanged from `681f30ce`, so the producer has not been touched since issuance. The worktree stayed clean.

### The "111.8–112.5 ms band is the bottom of the distribution" claim — CONFIRMED

Computed over the 406 record-level widths:

```text
min width ms: 111.839533   max width ms: 128.748655
5th pct ms (linear):       112.679183
count widths < 112.5 ms:   6
count widths in [111.8,112.5] ms: 6
count widths < 111.8 ms:   0
smallest 10 widths ms: 111.839533, 111.888647, 112.398386, 112.457275, 112.468004,
                       112.476110, 112.523794, 112.528324, 112.555504, 112.557173
largest 5 widths ms:   127.118587, 127.137184, 127.172232, 127.697468, 128.748655
```

Only 6 of 406 widths (1.5 %) fall in the old 111.8–112.5 ms band, none below it, and the distribution extends to 128.75 ms. The band sits below the 2nd percentile. The ratification's "the former 111.8–112.5 ms band is the bottom of the width distribution, not its range" is correct, and the "must not resurrect it" instruction is well founded. (Note the interaction with P1: the same 6 low widths are each counted three times in the issued sample, which is the direct cause of the Q1 shift.)

### Ordering assumptions

`_read_records` enforces non-decreasing `timestamp_s` across CSV rows, which the file satisfies (`ts already ascending in file order: True`), and equal timestamps are permitted — necessary, since the three rails of a record share one timestamp. `unique_timestamps = sorted(set(timestamps))` is therefore redundant after the monotonicity check but harmless, and it is the belt-and-braces the ratification asks for. No defect.

### N-1 — the cited ruling has no artifact

```text
$ git grep -n "R-167-1" -- .
scripts/issue_dg071_dg075_statistics.py:14:Ruling R-167-1 fixes the previously open conventions: ``statistics.median``;
scripts/issue_dg071_dg075_statistics.py:98:# Ruling R-167-1; paper producers remain standalone rather than importing it.
$ ls docs/process_traces/2026-08-31-registry-v5/
00-change-record.md 01-verify-registry-v5.py 02-dg071-dg075-ratification.md
03-retensing-rewrite-record.md 04-pedagogy-adjudication-opus.md 05-ADJUDICATION-DISPOSITION.md
06-structural-round-record.md 07-readjudication-opus.md 08-COLD-PACKET.md 09-COLD-RULING.md
10-perimeter-round-record.md 11-final-adjudication-opus.md 12-PARK-DISPOSITION.md
```

`R-167-1` appears only inside the producer's own docstring and one comment. The three conventions it is said to fix — `statistics.median`, type-7 interpolation, and "every CSV row included without filtering" — are exactly the conventions this review found undisclosed (S-2) and physically wrong (B-1). The single decision that produces the 1218-row population is currently traceable to nothing but the code that implements it. Filed as nit because the contract lens owns citation custody; flagged here because B-1's remedy depends on which body actually ruled the population.

### Checked and found sound (no finding)

- `_quantile` degenerate branches (`n == 1`, `lower_index == upper_index`) are correct and unreachable for these samples.
- `if None in row` correctly detects `csv.DictReader`'s `restkey`; short rows fall through to `record_field_missing`. Both are fail-closed.
- `csv.DictReader(text.splitlines())` splits on Unicode line separators (`\x85`, ` `, …) that a file iterator would not split on. A crafted `source`/`rail` value could therefore change row boundaries — but every resulting row is short and refuses with `record_field_missing`. Fail-closed; not reported as a finding.
- `_absolute_without_symlink_resolution` deliberately does not resolve symlinks, so a symlinked path cannot masquerade as the pin. Correct for the stated custody intent.
- Refusal ordering: path pin, then file existence, then SHA-256, then schema — the SHA is verified before any parsing, so no partially-parsed input can influence the refusal.

## What this review did NOT check

- **The contract lens.** Ratification text vs implementation vs artifact wording, custody-chain and registry-row bookkeeping, and artifact SHA registration were luna 178's and terra 185's lens; I read their reports only to avoid duplicating them and did not re-verify their findings except where P5 forced the SF-3 recheck.
- **The canonical full suite.** Per the brief I ran only `tests.test_issue_dg071_dg075_statistics`; I did not run `python3 -m unittest discover`, so I cannot say whether any other test in the repository binds this producer or its artifacts.
- **Upstream provenance of the bundle itself.** I verified the pinned SHA-256 and analysed the file's internal consistency, but I did not check how `power_trace.csv` was produced, whether its `interval_start_s`/`interval_end_s` faithfully reflect *powermetrics*' own sampling boundaries, or whether the ±1e-7 s boundary noise originates in the sampler or in the writer's float formatting. The tiling and rate conclusions are conclusions about the recorded file.
- **Whether 8.32 Hz / ~121 ms is the right sampler period** for the a10 window, or how these rows interact with the resolvability threshold arithmetic elsewhere in §6 beyond draft line 256.
- **Other registry rows and other round-7 fills.** Only DG-071 and DG-075 were in scope.
- **Cross-platform float behaviour.** All float results are from this machine's CPython on arm64 macOS; I did not check whether the 17-digit `repr` values reproduce on another platform (they should, IEEE-754 double and CPython's shortest-repr being deterministic, but I did not execute it).
- **Any `runs*` directory was read only**; nothing under `/Users/edr/code/JouleWise/runs_window_a10_20260725/` was modified, and no codex or claude process was launched.
