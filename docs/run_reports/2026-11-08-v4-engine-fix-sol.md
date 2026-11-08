# V4 engine-fix handoff — 2026-11-08

Branch: `engine-fix`, from `align/2026-11-08-v4-analysis-engine-sol`.
Implementation commit: `184c37b2562eda3f870eb0fa1c80dbc44ecaf486`.
The subsequent documentation commit contains this report and benchmark receipts.

## Result and authority

Applied the ENGINE-side R21 interpretations, including the user/lead amendment
that U5 INCONCLUSIVE does **not** trigger R20. The complete A0–A36 clause-to-code
map and exporter interface are in `docs/analysis/v4/ENGINE-sol.md`.

Scoring now uses the turn-owned GPU sum and h=0; attribution bounds and gross
energy are diagnostic. Known-H unreachable doses are null, carrier denominators
are per dose, prefix crossings and the fixed bootstrap recipe are implemented.
Exclusion classes are the union of recorded and re-derived evidence. U1–U6,
FAIL-only pool bars, calibration holds, W1 arithmetic, supplemental sentinels,
CP bounds and the descriptive B stop/release record follow R21. Benign DC is
integrated from observations and receives its own h=0 LOTO sequence model.

Rebuilt the Sol reducer from `origin/perf/2026-11-08-reduce-sol`: conservative
native byte scanner, plistlib fallback, shared column builder, one cold raw read
for hash/parse, atomic content-addressed column cache and verified warm hits.
Energy tables and decisions are recomputed. The optional C accelerator builds
locally with system cc; without it, plistlib remains functional at reference
speed. No package was installed.

Added raw-export ingestion and `--through-window` prefix execution. Full CLI
runs reuse already verified C material within the invocation, avoiding a second
raw C read before opening T. Output directories remain separate from inputs.

Authority read: repository instructions/M0, relevant restart/queue/stop-card
sections (no active stop card), orchestration, D-009/D-078, R21 item 230, every
ruling row and §7, the speed toolbox, the existing primary engine and the Sol
reducer. Explicit assignment overrides prohibit coordination writes/full-suite
execution. No coordination task was registered. No peer was delegated and no
Opus recompute code was read; independent comparison remains lead-owned.

## Failing-first evidence

- The initial 12 R21 witnesses failed against the old engine (3 failures,
  9 errors), exposing scoring, doses, classes, calibration and U-check changes.
- A cold-cache witness first observed two raw opens; the new path observes one.
- Raw/DC/prefix witnesses first failed for missing implementation. A W1 record
  witness then exposed lost ordinal metadata, corrected in the adapter.
- Streaming witnesses exposed XML-error priority changes after an earlier
  semantic fault, including a GPU schema fault. Both now match the reference.
- Explicit raw capture presence is validated as a bool before reading evidence;
  missing/truthy values are refused rather than inferred.
- Old C6, INCONCLUSIVE-pool, predeclaration and complete-dose expectations were
  updated to the adopted R21 behavior, with dedicated replacement witnesses.

## Verification

Each module ran separately with unittest, using Python 3.13.18:

| Command suffix after `python3.13 -B -m unittest` | Result |
|---|---|
| `tests.align.test_reduce_sol` | 23 passed |
| `tests.align.test_v4_analysis_engine` | 24 passed |
| `tests.align.test_v4_r21_engine` | 16 passed |
| `tests.align.test_v4_raw_engine` | 6 passed |
| `tests.align.test_thermal_desk` | 25 passed |
| `tests.align.test_v4_estimands` | 15 passed |
| `tests.align.test_v4_r11` | 27 passed |
| `tests.external.test_km003c_parse` | 43 passed |

**179 passed.** Focused testing, including iteration, remained below the
assignment's approximately twenty-minute test budget. The full suite was not
run. `python3.13 -B -m compileall -q joulewise tests scripts/analyze_align_v4.py
scripts/reduce_powermetrics_sol.py scripts/benchmark_v4_r21.py
scripts/bench_reduce_sol.py` and `git diff --check` passed. The frozen fitter's
SHA-256 remains `d187698d5cc8a0856ffe730079e16a164a5ac338b9dd0a4b10be8cac6206acef`.

Tests use synthetic records plus exact allowlisted, committed small parser
fixtures. No real measurement root was discovered or followed. No network,
model weights, B5 pipeline, quiet-Mac capture, real restricted directory or
external user path was read. The separate eight-worker analysis was not
inspected or changed. No MLX code changed; no new Metal test is required by
this diff. Python 3.11 and a no-compiler host were not run natively here; the
fallback route is exercised in the focused tests.

## Measured synthetic rehearsal

Command:

```sh
python3.13 -B scripts/benchmark_v4_r21.py --samples 64 --workers 2 --output docs/analysis/v4/ENGINE-sol-r21-benchmark.json
```

Eleven windows, 242 members, 64 raw samples/member, **845,239,703 source bytes**.
The benchmark requires 56 calibrators per pair and actual T3 fits, preventing
an all-barred/no-fit result from masquerading as an equality rehearsal.

| Mode | End-to-end seconds |
|---|---:|
| Serial, empty derived cache | 3.060 |
| Two workers, empty derived cache | 3.408 |
| Serial, verified column cache | 1.934 |
| Two workers, verified column cache | 2.855 |

All four complete fill/verdict byte streams are identical. Fill SHA-256:
`a5c147a7c7aadd339efcf305a5f8c8a09b0b21cfdf619cb60b73f1328504ca08`.
Verdict SHA-256:
`7b5b057e7b7477efe557be7f977ecce916a9513aa92976e656db92c4740ba601`.

Same-input parser comparison over 54,426,584 bytes: old ElementTree extractor
**40.70 MB/s/core**, new scanner **548.51 MB/s/core**, plistlib **25.56 MB/s/core**.
Columns match byte-for-byte, and the ≥300 MB/s/core target was reached in this
local run. The receipt's CPU time includes the hash helper thread. Serial is
faster than two workers on these short members; no parallel speedup is claimed.

The first whole-series fixture had a sub-second G0 with undefined collector-grid
coverage, causing every window to be barred. It was corrected to have an
observed G0 interval; only the exercising rehearsal above is the final receipt.
The earlier before/after JSON files are development snapshots, not final claims.

## Changed files

- Reducer: `joulewise/align/apple/{reduce_sol.py,_reduce_native.py,_reduce_scan.c}`.
- Acceptance/estimands: `joulewise/align/apple/{thermal_desk.py,v4_estimands.py}`.
- Engine/adapters: `joulewise/align/v4_analysis/{engine.py,acceptance.py,io.py,
  synthetic.py,exclusions.py,raw.py,dc.py}`.
- Byte-fed production DC parser seam: `joulewise/external/km003c_parse.py`.
- Tools: `scripts/{analyze_align_v4.py,reduce_powermetrics_sol.py,
  bench_reduce_sol.py,benchmark_v4_r21.py}`.
- Tests: `tests/align/{test_reduce_sol.py,test_v4_r21_engine.py,
  test_v4_raw_engine.py,test_v4_analysis_engine.py,test_v4_estimands.py,
  test_v4_r11.py}`.
- Documentation/receipts: `docs/analysis/v4/ENGINE-sol.md`,
  `ENGINE-sol-reducer-before.json`, `ENGINE-sol-reducer-after.json`,
  `ENGINE-sol-r21-benchmark.json`, and this report.

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`,
`tests/test_gen_state.py` and `PROJECT_STATUS.md` are untouched. Nothing pushed.

## Limits and exact next step

No interpretation ruling remains requested by this lane. The primary code is
synthetic-qualified; it is not a cross-build agreement or live release result.
The rehearsal uses short traces and absent DC, while separate synthetic tests
exercise DC integration, holds and independent DC LOTO coefficients. Full-size
507 MB/member performance, real DC throughput and the common export's actual
native shape remain unverified. One short parser timing on a contended machine
does not establish sustained throughput on the Air. Source authentication and
R1/W1 evidence qualification remain the exporter's/lead's responsibility.

Next: the lead maps the committed common export into the documented raw_source
interface, exercises a landed W1/C1 prefix on the Air, freezes C8 thresholds,
then adds T prefixes with that freeze. Run the independent comparator and
release rehearsal against the final primary tree, and remeasure full-size
throughput on a quiet Air. Keep scientific claim gates and PROVISIONAL labels
until their owning evidence passes. These gates do not require reading B5 data.
