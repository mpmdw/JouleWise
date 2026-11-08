# BYTES stage-1 export engineering — 2026-11-08

Branch: `perf/2026-11-08-eng-bytesexport`, based on
`912cf8c3a998b5d9d82c6b96e215871cf21288f4`
(`origin/lane/2026-11-07-bytes-stage1`, PR #701).
Authority: Ed's eng-bytesexport brief; latency synthesis §4 rank 7 and §5 D9
at `origin/perf/2026-11-08-latency-synthesis`.

Final synthetic export medians fell 37–38% for compressed inputs and 59% for
plain inputs, with exact CSV/sidecar/withheld equality against the original
exporter. Verification commands and handoff: [run report](../run_reports/2026-11-08-eng-bytesexport.md).

All experiments used newly generated synthetic archives. No real archive,
sealed outcome, model weight, external user directory, or network was accessed.
The running analysis job was left alone. No coordination state or registration
was edited. This is engineering evidence, not live hardware validation.

## What changed

- Index the source inventory once by lexical ancestor directory. Reference
  membership and bundle lookup no longer scan the entire inventory repeatedly.
  Symlink names, archive-only selection, vanished listed inputs, unlisted
  present inputs, and duplicate/conflicting inventory rules remain enforced.
- Stream inventory-only verification through `desk_compress.open_bytes` in
  1 MiB chunks, including `.zst` decompression and its EOF/exit-status check.
  Large raw artifacts are no longer materialized solely to hash them.
- Remember successful verification within one export, keyed by logical absolute
  path, expected digest, and physical file identity/size/mtime/ctime. Retain at
  most 4 MiB of control bytes, at most 64 KiB per file. A changed/deleted input
  or a new plain sibling invalidates the entry; failed authentication is never
  cached. A change during a read is a storage refusal.
- Reuse the parsed compression journal across reference restores in one export.
  The restore reader's private caller-owned cache checks journal identity,
  size/mtime/ctime on reuse; corruption, deletion and parse failures still
  refuse. Every bundle's bytes are still independently copied, hashed and
  checked against its restore records. Other restore callers retain the
  original uncached behavior.
- Add `export(..., read_workers=N)` and CLI `--read-workers N`, integers 1–8,
  default **1**. Workers verify reference input files only. At most N futures
  are outstanding; results are consumed in serial filename order. On refusal,
  pending work is cancelled and running workers are joined before returning.
- All row arithmetic, reference integration, key reads/draws, session bindings,
  withheld-store writes and public publication remain on the calling thread.
  Do not pool whole archive exports against the shared group key store.

The existing scratch restore byte checks, compression journal, scratch lock,
40 GiB reserve, reducer, estimator digest, registration, thresholds, held-out
split and stage-1 commitment/release order are unchanged.

## Profile first

Before implementation, the original exporter took 7.462 s median for a
compressed point-trace fixture: 16 references, seven science members, 2 MiB of
synthetic raw payload per reference, and 2,048 trace samples per reference.
The uncompressed version took 4.216 s median. Three unprofiled repeats each;
fixture creation and initial key creation excluded.

The compressed cProfile run took 8.409 s (instrumentation overhead applies):
`_reference_request_fields` 4.475 s cumulative, `_integrate` 2.873 s,
`_ReferenceInputs.read` 1.672 s, bundle lookup 1.417 s, bundle verification
1.261 s, and scratch restore about 1.174 s. These are **overlapping cumulative
times**, not an additive stage ledger. Repeated inventory scans and repeated
logical decompression were actionable. Key binding scans were not a leading
cost in this small fixture, so no key cache or key-store parallelism was added.

The point-trace integration cost is the reducer's existing repeated linear
interpolation. Native interval integration follows another branch. The reducer
was left intact; interval-supported mock traces were added to isolate the
export I/O work without claiming native powermetrics validation.

## Before/after on identical synthetic inputs

Python 3.13.18; Zstandard CLI 1.5.7. The host had the user's concurrent
eight-worker analysis load. These are noisy shared-host measurements, not
quiet-machine throughput or a production runtime forecast.

The harness loads the **unchanged original exporter** from the base commit
above using local Git objects. For each repeat it runs original then optimized
against the same archive, stored factors, output paths and withheld locator.
It checks exact CSV, sidecar and withheld-store bytes. Timings exclude fixture
construction, key creation, comparison and profiling. Three repeats per row.

Final code `8066b1783`, including the journal cache:

| Fixture | Read workers | Original median (s) | Optimized median (s) | Reduction |
|---|---:|---:|---:|---:|
| Compressed, interval, 16 references / 7 science | 1 | 4.598 | 2.909 | 36.7% |
| Same geometry | 4 | 3.055 | 1.892 | 38.1% |
| Compressed, interval, 16 references / 128 science | 4 | 10.016 | 6.289 | 37.2% |
| Plain, interval, 16 references / 7 science | 4 | 0.677 | 0.278 | 58.9% |

The final one-worker samples were original `[4.378066, 7.783816, 4.597822]`,
optimized `[2.909159, 5.836152, 2.752957]`. The slow middle pair illustrates
the shared-host variance; no cause was inferred from the running analysis.
Four-worker samples were original `[2.861693, 3.241025, 3.054558]`, optimized
`[1.891503, 1.419166, 2.099893]`. Compare each optimized series with its own
interleaved reference, not across separate worker runs.
The wider fixture's final samples were original
`[11.983157, 10.016116, 9.943245]`, optimized
`[6.082164, 6.289346, 7.349421]`; decompressions fell **672 → 576**. The
journal is parsed once per export; per-bundle restore byte verification remains.
Final plain samples were original `[0.703212, 0.677399, 0.562717]`, optimized
`[0.278363, 0.311564, 0.211055]`; neither path launches a decompressor.

Initial worker sizing, before the follow-up journal parse cache:

| Fixture | Read workers | Original median (s) | Optimized median (s) | Reduction |
|---|---:|---:|---:|---:|
| Compressed, interval, 16 references / 7 science | 1 | 4.104 | 2.830 | 31.0% |
| Same geometry | 2 | 4.262 | 2.545 | 40.3% |
| Same geometry | 4 | 4.336 | 2.567 | 40.8% |
| Compressed, interval, 16 references / 128 science | 4 | 12.126 | 8.452 | 30.3% |
| Plain, interval, 16 references / 7 science | 4 | 0.994 | 0.419 | 57.9% |

The wider fixture's profile exposed 1.675 s in `_records`: each of 16
reference restores parsed and resolved the same large compression journal.
The failing-first test reproduced three parses for three references; the
final implementation parses once and invalidates on journal changes.

For the 16-reference/seven-science compressed geometry, decompressor launches
fell **309 → 213**, counted
outside the timing samples across all threads. One scratch restore per
collected reference is still required; it was not replaced with an unchecked
compressed reader. There is no evidence here for extrapolating 1–4 production
hours to a particular new runtime. Initial sizing found two and four workers similar;
leave the default at one and select concurrency only on the non-measuring host.

Reproduce without accepting any real archive path:

```sh
PYTHONNOUSERSITE=1 python3.13 -B scripts/profile_bytes_export.py --compressed --interval-trace --compare-serial --workers 1
PYTHONNOUSERSITE=1 python3.13 -B scripts/profile_bytes_export.py --compressed --interval-trace --compare-serial --workers 2
PYTHONNOUSERSITE=1 python3.13 -B scripts/profile_bytes_export.py --compressed --interval-trace --compare-serial --workers 4
PYTHONNOUSERSITE=1 python3.13 -B scripts/profile_bytes_export.py --compressed --interval-trace --science 128 --compare-serial --workers 4
PYTHONNOUSERSITE=1 python3.13 -B scripts/profile_bytes_export.py --interval-trace --compare-serial --workers 4
```

The shared host initially refused even the tiny restore at the standing 40 GiB
reserve. The synthetic-only harness therefore uses the restore tests' disk-space
seam and caps its generated raw payload at 256 MiB. It never changes the
production reserve. cProfile covers the calling thread only; the explicit
decompressor census includes workers. The serial commit must exist locally;
the harness never fetches it.

## D9: can stage 1 run on the Air?

**Technically yes, after a complete, custody-approved closed-input copy. It is
not a CSV-only handoff.** There is no MLX, Metal, live telemetry or model-weight
requirement in export/census/thermal-line preparation/fit analysis/twin/commitment.
The existing stage-1 plan already reports its synthetic driver tests on the Air.
“One-time archive read” can mean one MBP transfer of closed inputs: subsequent
archive reads and refits occur on the Air's copy. It cannot mean the entire
pipeline reads archive contents only once.

Code evidence and required handoff:

1. `bytes_stage1.py census` and pre-commit blinded analysis use exported identity
   and rails tables. But `build_manifest` reads archive acceptance identity;
   `bytes_analysis.load_records` takes `archive_records` at stage `fit`, which
   reads raw bundles and re-derives summaries under the recorded operative
   timing bound. Twin stage 1 uses `load_archive`/`dc_join` and raw meter/battery
   streams. Copy the complete closed archives and their source inventories,
   reductions, acceptance, calibration evidence, meter/battery/thermal journals,
   session plans and registrations, not just the public export.
2. Both `desk_restore._records` and the independent twin's `_readable_bundle`
   key compression records by **absolute logical path**. A compressed archive
   copied to a different root with an unchanged journal is not automatically
   portable. Preserve the original logical path layout on the Air, or have the
   lead establish an authenticated relocation/plain-copy procedure first.
   Do not rewrite custody journals ad hoc or fall back to external originals.
3. Thermal-line views use symlinks to source archives. Keep their sources
   reachable on the Air; copying only a view leaves dangling/original-host
   dependencies. Construct views after the input handoff.
4. Export needs the authorized group key store with its **existing key bytes,
   session digest bindings and withheld stores**, and the stage-1 driver needs
   the fit-only release route. The lead must select a single writer/owner and
   authorize custody on the Air; copying just factors, drawing new ones or
   sharing the writable store between hosts is not the proposed optimization.
   Keep held-out keys unreleased and held-out rows withheld through commitment.
5. Use the lead-selected stage-1 checkout and registered estimator digest from
   the owning plan, ample scratch plus the unchanged reserve, and the same
   Python/zstd dependencies. Export with e.g. `--read-workers 2` inside the
   existing **serial session loop**, then run the existing census/agreement/
   release/fit/commit sequence. Do not install this candidate into a measurement
   checkout or overlap work on that host with a window from this session.

This answers feasibility, not authorization to transfer keys or a claim of an
executed Air handoff. No Air filesystem, archive location, free space or key
custody was inspected. The outstanding placement decision is who owns the
approved Air copy and whether its absolute paths are preserved.

## Equality and verification scope

The new targeted module uses the pre-change exporter as an executable oracle,
not a second implementation of expected arithmetic. It checks point/interval
and plain/compressed outputs at 1/2/4 workers, complete stored-key and archive
immutability, calling-thread-only key/publication operations, bounded streaming,
cache invalidation, worker overlap and first-refusal order. Missing inputs,
digest mismatch, malformed events, unlisted files, corrupt compressed frames
and corrupt restore journals are compared by exact exception text; failed
exports publish no new public files. Initial tests failed before the worker
API existed. The new refusal comparisons also caught and corrected a
missing-file message difference during implementation.

The lead still owes native powermetrics-backed synthetic archive parity at
1/2/4 workers outside this sandbox's time budget, on a non-measuring host,
before operational adoption. No native measurement, real archive, weights or
MLX execution is claimed. No MLX code changed and no MLX test is required by
this patch. Full-suite/CI execution is deferred per Ed's explicit instruction.
