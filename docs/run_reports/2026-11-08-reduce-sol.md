# reduce-sol handoff — 2026-11-08

Task: independent SOL primary reducer, rooted at `origin/align/2026-11-08-v4-r11` (`9891d679b95784dc3c09e1cd146de31f62ac7840`), branch `perf/2026-11-08-reduce-sol`. The branch already existed and the initial working tree was clean. The user explicitly authorized local commits and forbade pushes and coordination-state edits.

## Scope and safety

Implemented an offline reducer/API, explicit-jobs CLI, synthetic generator/profile/benchmark, equality tests and the [technical handoff](../perf/2026-11-08-reduce-sol.md). No registered instrument, analysis plan, decision rule or existing runtime module was edited. No Block 5 analysis, real measurements, model downloads, network, live collection or MLX execution occurred. Only an exact fixture allowlist was opened. Referenced absolute data paths were treated as text. The ongoing 8-worker job was not inspected or controlled. A request to lower this benchmark's own priority with `nice -n 10` was denied by the sandbox; the command continued and its observed wall/CPU times are reported without an isolation claim.

The user brief overrides the generic end-of-run checklist: `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and `tests/test_gen_state.py` remain unchanged; no kernel task was registered. M0 intake found no active stop card. The explicit reduce-sol brief governs this [AGENT] software lane. `origin/main:docs/perf/SPEED-TOOLBOX.md` was read from Git without network before profiling or optimizing.

## Implementation

- `joulewise/align/apple/reduce_sol.py`: bounded NUL-frame reads, C-backed XML tree/projection with full-plist fallback, compact typed arrays, fresh clock mapping and established attribution, raw/code-bound observation cache, ordered bounded member process pool.
- `scripts/reduce_powermetrics_sol.py`: explicit input manifest, cache/turn tables, raw/episode provenance, immutable-input alias rejection and atomic report publication.
- `scripts/bench_reduce_sol.py`: full-M3-Max-skeleton synthetic generator, cProfile baseline, throughput/member/window-equivalent benchmark and short-member 11-window end-to-end read/attribute/aggregate comparison.
- `tests/align/test_reduce_sol.py`: committed-fixture and synthetic byte equality; malformed/torn/duplicate/nested-key cases; clock and ownership arithmetic; cache invalidation/corruption/race checks; serial/parallel outputs/refusals; CLI provenance and input preservation.

The cache contains observations only. All boundary/clock/uncertainty/eligibility work stays fresh. Raw bytes are hashed on every hit; misses verify the bytes actually parsed too. Loaded executable code changes rotate the cache namespace; debug source paths are normalized for another checkout. Runtime-version changes require rebuilding. The format explicitly refuses nonfinite GPU activity/clock values, unrepresentable integer activity and timestamp/counter storage overflow; acceptance parity is not claimed outside the documented finite/int64 boundary.

## Verification

Commands were run one module at a time; no full suite or pytest was run. Total targeted test time stayed well below 20 minutes.

- `python3.13 -B -m unittest tests.align.test_reduce_sol`: final reviewed source, 18 tests OK (50.263 s).
- `python3.13 -B -m unittest tests.test_powermetrics`: 61 tests OK (20.024 s).
- `python3.13 -B -m unittest tests.align.test_attribution_holds`: 6 tests OK (0.546 s).
- `python3.13 -B -m unittest tests.align.test_thermal_desk`: 25 tests OK (2.154 s).
- Focused final CLI/date checks: 2 tests OK (2.512 s).
- `python3.13 -m compileall -q joulewise tests`: OK.
- `git diff --cached --check`: OK at source staging.

The first reducer run exposed three errors in a synthetic test helper's default foreign-domain trace; the helper now starts with no traces. The parser/equality assertions did not fail there. Subsequent focused and broad runs passed. One fixture-only check was accidentally launched before the first targeted invocation had fully returned; it passed (44.253 s). This was a scheduling mistake; subsequent unittest invocations were sequential.

## Independent review and dispositions

Two native read-only invocations are recorded in the [append-only invocation manifest](../process_traces/2026-11-08-reduce-sol/invocation_manifest.jsonl). The first invocation was not recorded at dispatch and returned no required envelope; its rows explicitly identify lead recovery and it is raw review substrate, not a compliant final-review claim. The fresh formal final review is separately dispatched from the [stored prompt](../process_traces/2026-11-08-reduce-sol/final-review-prompt.md). No reviewer repository edits or unittest runs occurred. The lead owns all fixes, tests, final diff review and this handoff.

The review found and the lead fixed:

1. `datetime.fromisoformat` accepted non-plist date separators. Exact ASCII plist date syntax now guards the fast path; both witnesses have refusal tests and use the original parser fallback.
2. Absolute code filenames prevented reuse across clones. Recursive filename normalization now preserves executable code identity; a loaded-function filename mutation test and reviewer probe passed.
3. CLI output could alias an input. Preflight now rejects raw/jobs/episode paths and hardlinks before parsing; executing probes preserved input bytes and created no cache. Final output uses atomic replacement.

Mapping review confirmed that existing attribution owns missing/ambiguous mapping behavior; the CLI emits the old desk's empty native view when no matching mapping is available. Final report provenance fields were added after the initial review and are covered by the formal final delta review.

Checks that caught number/input hazards: independent date differential probe caught an acceptance mismatch; cache identity tests caught source-location incompatibility; alias probes caught raw-evidence overwrite potential; byte equality tests protect summation, ownership, rounding and JSON number types. No deletion proposal is inferred from one session's check yield.

## Remaining integration and uncertainty

The separately built primary engine has not been modified here. Its lead should consume this API, retain custody/admission/raw-rich/trace checks, supply authenticated endpoint/mapping/evidence and compare its final serialized raw/reduced engine outputs on synthetic inputs. The benchmark's simple aggregate is an explicit stand-in, not that future engine. Full real-series throughput and cold-disk behavior remain unmeasured. Python 3.13 was exercised; Python 3.11 CI remains for the lead. No new MLX code/tests exist, so there is no reducer-specific native MLX gate; this work supplies no native hardware validation. No open science ruling was invented.

## Formal review receipt

The [final review](../process_traces/2026-11-08-reduce-sol/final-review.md) returned `DONE` with no remaining blockers. The lead validated the final-lines envelope and verified stored prompt, report and reviewed-source SHA-256 values. The four source/test files remained byte-identical to that reviewed source. The report records seven inspection/probe checks and no edits, unittest, network, real-data or measurement access by the reviewer. All initial findings are dispositioned above; no unresolved review finding remains.

## Benchmark and final closeout

The final [timing receipt](../perf/2026-11-08-reduce-sol-benchmark.json) completed with exit 0. Its producer SHA-256 was checked against the current loaded reducer. The separate [pre-implementation profile](../perf/2026-11-08-reduce-sol-baseline.json) is retained too. The full reproducible benchmark command and detailed limitations are in the technical handoff.

- Full-size synthetic member: 9,300 samples, 506,167,196 raw bytes. Streaming plistlib: 45.541 wall / 42.203 CPU s, 11.994 MB/s/core. Extractor: 27.870 wall / 25.994 CPU s, 19.473 MB/s/core. Byte-identical compact artifact: 577,168 bytes (877 times smaller).
- The cold cache build took 17.533 wall s and a verified hit including raw rehash 0.208 s. The unexpectedly lower cold-build timing than the preceding extractor timing demonstrates variability under load; it does not establish a cold-cache algorithmic saving.
- Twenty-two uncached full-size passes over one synthetic file: 787.152 wall / 583.635 CPU s (13.12 wall minutes). This is a measured 11.136 GB member-count-equivalent workload, not distinct full-size members. OS page residency was not controlled or verified; the receipt's warm-cache wording refers to repeated-file access only.
- Synthetic 11-window series: 22 distinct short members per window, 30 samples/member; 395,197,893 raw bytes plus 48,652,220 persisted-rich-JSON bytes. Serial raw path: 46.586 wall s. Cold reduced path with two workers: 20.775 s. Verified-cache path with fresh attribution: 1.890 s. The 2.24x / 24.64x improvements are for this workload and include member parallelism; child CPU is excluded from reported parent CPU fields.
- Raw/cold/warm serialized mapped rows, three-rail attribution and illustrative aggregate outputs matched byte-for-byte, SHA-256 `8f0e029fcf47c98064f1834674109ae723c0b2df3e62983d7c733a215c3a8a40`. This does not replace synthetic equality on the separately built primary engine or establish full 120 GB/real-series performance.

The final 18-test reducer module passed in 50.263 s. Final compileall covered `joulewise`, `tests` and both new scripts; whitespace checks passed. Reviewed source hashes were rechecked with no source edits after review. Implementation/tests/benchmark source are committed at `378820341` (Add offline SOL powermetrics reducer and equality checks). Documentation, both timing receipts and the two-invocation process record are committed separately with this report. No push occurred.

Next exact step: the primary-engine lead takes `378820341`, consumes `reduce_file` / `mapped_columns` / `turn_energy_table`, preserves all existing custody and fresh admission checks, and runs its raw-versus-reduced final-output comparison on a synthetic series. No science question or scope expansion is pending in this reducer build. Runtime portability, actual-engine integration, full-size distinct-series/cold-disk timing and Python 3.11 CI remain explicitly unverified. Window-side recommendations are boundary markers in already-open journals and an off-machine member index only; no such collection change was made here.
