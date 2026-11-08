# SOL primary powermetrics reducer — 2026-11-08

This is the independent SOL reduce-once build for the primary analysis engine
`align/2026-11-08-v4-analysis-engine-sol`. It adds offline derived data and changes
no registered instrument, collection code, estimand, or admission rule. All
executed inputs were synthetic or an explicit allowlist of committed fixtures.
Block 5 measurements and outcomes were not opened. No network or model weights
were used. Coordination state remains lead-owned and unchanged.

## What the profile establishes

The generator in `scripts/bench_reduce_sol.py` mirrors the full committed M3 Max
fixture tree (`tests/fixtures/powermetrics_sample.plist`, `Mac15,9`), including
cluster/core DVFM arrays. It replaces numeric observations, powers, dates and
thermal states with prescribed synthetic values. It does not substitute a large
padding string for the real XML structure. Synthetic frames average about
54.4 kB, close to the brief's 52.8 kB/sample; cadence is 10 Hz with small
prescribed interval jitter. This is a shape benchmark, not hardware validation.

The [pre-implementation profile receipt](2026-11-08-reduce-sol-baseline.json)
used 300 samples and 16.33 MB of synthetic XML.
`parse_powermetrics_records` took 0.948 CPU s (17.23 MB/s/core); a separate
`decode_rich_telemetry` pass took 1.090 CPU s. Mapping took 0.000041 CPU s and
simple three-rail integration 0.000095 CPU s. Under cProfile, the two full
plistlib parses accounted for 5.817 of 5.969 wall s. The profile separates XML
parser work, Python element/data callbacks, and numeric callbacks; integer/real
conversion is a smaller part of the callback/object-construction cost.

Those two parses describe the adapter APIs, not two mandatory passes in the
current desk. The series benchmark below models the desk faithfully: one raw
plist parse plus its already-persisted rich JSON sidecar. The standalone full
member comparison uses streaming frame-by-frame plistlib as a conservative
reference, avoiding the old full-stream document list's large memory footprint.

## Format and parsing

`joulewise.align.apple.reduce_sol` reads NUL-framed XML in bounded chunks, builds
one XML tree at a time using C-backed ElementTree, validates ignored values too,
and materializes only the selected fields. Unexpected grammar takes the full
plistlib path. Nested fields with colliding key names cannot impersonate root
or processor fields. Duplicate keys retain the last value. Invalid middle
frames refuse; one invalid final frame after complete documents retains the
original dropped-frame diagnostic and raw-byte digest.

`SampleColumns.columns` contains little-endian-compatible typed arrays:

| Column | Storage / units |
| --- | --- |
| `elapsed_ns`, `native_timestamp_ns` | signed 64-bit ns; native date is wall time |
| `cpu_power`, `gpu_power`, `ane_power` | float64 W, divided from mW once |
| `thermal_code` | uint32 index into `thermal_labels`, including null |
| `active_ns` | float64 GPU DVFM active duration; integer type byte preserves JSON types |
| `clock_mhz` | float64 activity-weighted GPU clock, with separate validity byte |

`mapped_columns(endpoint, offset_ns)` returns fresh integer `t_ns`,
`power_start_ns` and `thermal_start_ns` arrays on the supplied episode clock,
normally monotonic. Raw-cache identity deliberately excludes the anchor and
clock mapping: changing either must change the fresh mapped result. The float
elapsed accumulation and epoch-to-ns rounding order match the adapter exactly.
Power starts use its float support conversion; thermal starts use the desk's
integer `end - elapsed_ns`. Neither is substituted for the other. GPU clock
weighting retains DVFM state order and MHz units.

The v1 compact format supports signed-int64 elapsed/date/mapped timestamps and
finite GPU activity/clock values. Integer activity must be losslessly
representable as float64. It explicitly refuses values outside those storage
limits. Equality evidence is for the committed fixtures and synthetic cases,
not a claim of universal acceptance equivalence for every possible plist.

## Cache and consumption contract

The cache path is `<cache>/<loaded-producer-sha256>/<raw-sha256>.jwsr`.
One deterministic file holds a canonical JSON header, fixed-order little-endian
arrays and a trailing SHA-256 checksum. The header binds raw size/hash, schema,
producer, field layout, thermal labels and any dropped-tail observation.
Corrupt or stale cache contents are rebuilt. Refusals create no cache file.

Every cache hit hashes the raw file again. Cold misses also hash the bytes
actually parsed and reject a change between lookup and parsing. This deliberate
second cold read avoids trusting a stat tuple or misbinding a concurrently
modified raw file. No stat-based digest cache or negative cache exists.

The producer key hashes loaded Python code objects, including parsing helpers,
ElementTree's Python entry points, plistlib fallback and numeric validation,
plus format constants and runtime versions. Absolute debug filenames are
normalized recursively, so identical code loaded from another clone is
compatible. A different Python/runtime version rebuilds the cache; v1 does not
claim cross-runtime cache compatibility. Changes to executable loaded code
rotate the namespace even if files on disk are unchanged.

Only observations are cached. Anchor resolution, custody checks, turn boundaries,
thermal exclusions, uncertainty, eligibility, fitting, thresholds, decisions
and refusals remain fresh caller work. Raw custody validation is not replaced
by the cache checksum. Consumers must supply an independently authenticated
first-record endpoint, episode, mapping and uncertainty evidence; they must
retain existing raw/rich-count, trace and admission checks. `reduce_file` expects
the original uncompressed NUL-framed plist. Archives need explicit,
custody-verified decompression first; compressed suffixes are not discovered or
followed automatically. The compressed committed fixture is tested after
explicit decompression.

```python
from joulewise.align.apple.reduce_sol import reduce_file, turn_energy_table

samples = reduce_file(raw_path, cache_dir=derived_cache)
columns = samples.mapped_columns(first_record_endpoint_s, mapping.offset_ns)
table = turn_energy_table(
    samples, episode,
    first_record_endpoint_s=first_record_endpoint_s,
    nominal_interval_ns=100_000_000,
    evidence=uncertainty_evidence,
)
```

`power_traces` calls existing `sampler.power_records`; `turn_energy_table` calls
existing `attribute_episode` separately for each rail. The returned table
includes every segment, per-turn owned energy/half-width, total, methods and
flags. Existing turn/tool ownership, holds/gates, gap handling, edge snapping,
summation order and uncertainty arithmetic are reused. The table is recomputed
and is never put in the observation cache.

`reduce_members(paths, cache_dir=..., workers=1)` supports a bounded process pool
(1–8, default 1) across independent members and returns input order. It does not
batch measured inference or alter batch-1 episodes. Serial/parallel column
bytes, successful CLI reports and first-in-input-order refusal messages are
tested for equality. Parallel failures can leave observations for other valid
members in the cache, but publish no partial report or decision.

For an explicit jobs manifest, run:

```sh
python3.13 -B scripts/reduce_powermetrics_sol.py \
  --jobs synthetic-jobs.json --cache derived-cache --output reduced.json --workers 2
```

The manifest is `{"members": [{"id": "m1", "raw": "raw.plist", "episode":
"episode.json", "first_record_endpoint_s": 1767225600.0,
"nominal_interval_ns": 100000000, "uncertainty_evidence": {}}]}`.
Paths are explicit and relative to the jobs file. Without `episode`, only
column references are returned. No config/model/data path is discovered or
followed. Reports bind raw and episode bytes, the endpoint, interval and
supplied uncertainty evidence. Output aliases to any explicit input (including
hardlinks) refuse before parsing. Cache files and final reports are replaced
atomically. No bundle file is written.

## Benchmark receipt

The [final JSON receipt](2026-11-08-reduce-sol-benchmark.json) records Python
3.13.18, arm64, on the user-identified Air with the unrelated long-running
8-worker job left untouched. These are single phase timings under load. CPU
seconds measure the current process; wall time includes contention. No quiet
machine or OS-cache control is claimed. The attempted `nice -n 10` prefix was
denied by the sandbox; the benchmark continued.

| Full-size synthetic member: 9,300 samples, 506,167,196 bytes | Wall s | CPU s | MB/s/core |
| --- | ---: | ---: | ---: |
| Streaming full plistlib reference | 45.541 | 42.203 | 11.994 |
| Validating targeted extractor | 27.870 | 25.994 | 19.473 |
| Cold content-addressed cache build | 17.533 | 15.106 | — |
| Verified cache hit, including raw rehash | 0.208 | 0.206 | — |
| 22 uncached full-size extraction passes | 787.152 | 583.635 | 19.080 aggregate |

The column artifact is **577,168 bytes (877× smaller)**; full-reference and
extractor artifact bytes matched exactly. Per-sample array payload is 62 bytes,
with a small header/checksum. Cold-build time being lower than the separate
extractor timing demonstrates phase-to-phase variability; it is not evidence
that hashing/caching speeds up the cold parser. Repeat isolated runs before
using these figures as capacity guarantees.

The 22-pass workload reads 11.136 GB by repeating uncached extraction over one
synthetic file. It measures the member-count-equivalent byte workload, not 22
distinct full-size members. The receipt's `warm OS page cache` note denotes
repeated-file access; actual page residency was not verified under the active
job. Cold-disk performance remains unmeasured.

The end-to-end comparison uses **11 windows × 22 distinct members × 30 samples**:
395,197,893 raw bytes plus 48,652,220 bytes of persisted rich JSON. All mapped
native rows, three-rail segment/turn energies, uncertainty/flags and illustrative
mean/SD outputs were byte-identical across the three paths:

| Synthetic 11-window read/map/attribute/aggregate path | Wall s |
| --- | ---: |
| Serial raw parser + persisted rich JSON | 46.586 |
| Cold reduction + fresh analysis, 2 workers | 20.775 |
| Verified observation-cache hits + fresh analysis, 2 workers | 1.890 |

This is a measured **2.24× cold / 24.64× warm** improvement for this workload.
The cold comparison combines the extractor and two-member software parallelism;
it does not isolate their separate contributions. Parent-process CPU times for
the process-pool paths exclude child CPU and are not used for throughput claims.
The serialized output SHA-256 is
`8f0e029fcf47c98064f1834674109ae723c0b2df3e62983d7c733a215c3a8a40`.

Members in this series contain approximately three seconds of synthetic
telemetry. Its illustrative mean/SD aggregation is not the separately built
primary engine or a registered analysis. No full 120 GB series, real window,
or sealed-outcome performance is claimed.

```sh
python3.13 -B scripts/bench_reduce_sol.py --samples 300 \
  --member-samples 9300 --window-passes 22 \
  --series-samples 30 --windows 11 --members-per-window 22 --workers 2 \
  --output /private/tmp/reduce-sol-benchmark.json
```

Fixture/synthetic equality and refusal checks are in
`python3.13 -B -m unittest tests.align.test_reduce_sol`. The run report records
targeted legacy checks, final review, limitations and the integration handoff.

## Window-side improvements: proposals only

Follow `origin/main:docs/perf/SPEED-TOOLBOX.md` (read before implementation).
Existing within-member prefill/decode/tool/gate stamps are sufficient for
reduction; do not add sample-rate markers or another telemetry format during
measured members.

1. For reader-reported gaps only, append phase name, monotonic ns and wall time
   at existing turnaround boundaries to already-open `chain-stages.jsonl` or
   `events.jsonl`. Keep counts to tens per window. Buffer any in-member marker
   until the existing sync; no extra fsync, file, thread, process or computation.
2. Off the measurement machine, emit a deterministic member index joining
   relative raw path/hash, episode/hash, existing endpoint/mapping evidence,
   rich count and boundary-stamp references. This would remove directory/config
   discovery from analysis and make missing inputs visible before a long parse.
3. Run this reduction on the Air after offload and preserve raw custody. An
   analysis-ready manifest can reference compact observations and explicit
   fresh-analysis inputs; it must not carry a cached admission/selection result.

These proposals change no registered instrument in this branch. Any future
collection change needs its owning authority; batching measured members stays
forbidden.
