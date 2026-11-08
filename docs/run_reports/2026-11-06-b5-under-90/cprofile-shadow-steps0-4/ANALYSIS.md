# Block-5 joined-driver function profile (synthetic S10, HEAD)

## Scope and run conditions

This is **synthetic-data-only** attribution from the committed S10 fixtures. It
is not hardware or real-data evidence. HEAD was `e717e8b4`; the driver-recorded
analysis-code digest was `276a80bf47c08c7eecb83a819446bceb26a2757c2962b64286db17b691e06913`.
The host exposed `nproc=3`, so `W=min(7,max(2,nproc-1))=2`. Python was
`/root/.pyenv/versions/3.13.13/bin/python3.13` (3.13.13). At launch the host had
17 GiB RAM (16 GiB available), no swap, and 30 GiB free of 32 GiB on the
overlay containing both `/tmp` and `/workspace`. `TMPDIR=/tmp/jwprof/tmp`.

The run failed at step 4 with `tooling_refusal`; see `FAILURE.md`. Therefore the
requested full-driver attribution is incomplete. Steps 5, 8, 6, 9, 10, and 11
have no profile and no defensible total or hot-spot ranking. This report does
not interpolate them.

## Method

“Profiled seconds” are cProfile aggregate process-seconds, not wall seconds.
Driver and worker totals are reported separately because adding two worker
profiles intentionally exceeds elapsed wall time. Percentages below partition
**self time** by filename/function-name classification: (a) validation/parsing
(`json`, `plistlib`, XML/pyexpat, strict/schema/parse); (b) Decimal and
acceptance-bound arithmetic (`decimal`, quantile/acceptance and
`calibration_bracketing`); (c) hashing/file I/O; (d) pickle/process transport;
(e) numerical fitting (including Fraction arithmetic used by the fitting
path); (f) waiting/locks/polling. “Other” is shown so percentages are honest.
These are name-based attribution estimates; `report.txt` is the authoritative
function table.

## Per-step results

| Step/group | Profiled s | a parse/validate | b Decimal/accept. | c hash/I/O | d transport | e fitting | f waiting | other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 driver | 24.861 | 1.470 (5.9%) | 0 | 16.730 (67.3%) | 0 | 0 | 2.215 (8.9%) | 4.447 (17.9%) |
| 1 driver | 1091.417 | 0.132 (0.0%) | 0 | 1.306 (0.1%) | 0.357 (0.0%) | 0 | 1076.365 (98.6%) | 13.257 (1.2%) |
| 1 workers | 2054.843 | 496.329 (24.2%) | 0.000 | 15.994 (0.8%) | 0.081 (0.0%) | 1054.447 (51.3%) | 45.197 (2.2%) | 442.794 (21.5%) |
| 2 driver | 23.689 | 1.634 (6.9%) | 0 | 7.410 (31.3%) | 1.575 (6.6%) | 0 | 8.568 (36.2%) | 4.503 (19.0%) |
| 2 workers | 14.250 | 1.866 (13.1%) | 0 | 3.744 (26.3%) | 0.159 (1.1%) | 0 | 1.298 (9.1%) | 7.183 (50.4%) |
| 3 driver | 1.076 | 0.117 (10.9%) | 0 | 0.608 (56.5%) | 0 | 0 | 0.023 (2.1%) | 0.328 (30.5%) |
| 3b driver | 1533.904 | 0.659 (0.0%) | 0.976 (0.1%) | 1.005 (0.1%) | 0.577 (0.0%) | 0 | 1473.518 (96.1%) | 57.169 (3.7%) |
| 3b workers | 2463.406 | 428.542 (17.4%) | 12.402 (0.5%) | 35.359 (1.4%) | 0.672 (0.0%) | 1297.803 (52.7%) | 94.461 (3.8%) | 594.166 (24.1%) |
| 4 driver | 477.904 | 0.021 (0.0%) | 0 | 0.105 (0.0%) | 0.094 (0.0%) | 0 | 470.716 (98.5%) | 6.967 (1.5%) |
| 4 workers | 946.391 | 252.703 (26.7%) | 7.336 (0.8%) | 22.114 (2.3%) | 0.046 (0.0%) | 408.689 (43.2%) | 24.503 (2.6%) | 231.001 (24.4%) |
| 5, 8, 6, 9, 10, 11 | unavailable | — | — | — | — | — | — | not run |

Step 0 is an I/O census: `posix.lstat` led self time (6.820 s, 332,239
calls), followed by `_io.open` (1.281 s, 18,575 calls) and buffered `read`
(0.882 s, 18,565 calls). Step 2 is short but repeats path construction,
hashing and transport; its driver spends 5.034 s polling and 1.233 s in
`_pickle.Pickler.dump`, while workers spend 1.644 s in `posix.read`. Step 3 is
also brief and I/O-led.

Step 1’s driver is almost entirely waiting: lock `acquire` is 1047.239 s self
and `select.poll` 25.184 s. Worker hot spots are XML/plist parsing
(`pyexpat.ParseFile`, 182.232 s self; plist `handle_data`, 73.025 s) and the
fitting/uncertainty path: `fractions.forward` 117.931 s,
`fractions._from_coprime_ints` 112.253 s, `fractions._mul` 112.185 s,
`powermetrics_fiducial._overlap_fraction` 103.332 s, and
`uncertainty_evidence._lp2_line_optimum` 71.097 s. The strict validator’s
cumulative scope is 2010.150 s across 262 member calls, demonstrating that it
re-enters parsing and refitting rather than merely checking a small result.

Step 3b’s driver waits in lock `acquire` for 1461.161 s. Workers are dominated
by `powermetrics_fiducial._overlap_fraction` (318.828 s self), its generator
(214.302 s), XML `ParseFile` (150.502 s), `_huber` (98.281 s), and `math.fsum`
(68.244 s). Acceptance arithmetic is smaller but explicit: worker
acceptance-bound derivation is 4.198 s cumulative in one worker (three calls),
and the driver repeats the derivation once for 1.135 s; student-t quantile
work accounts for most of that path. Ledger parsing occurs four times in the
driver (6.734 s cumulative) and twice in one worker (4.507 s cumulative).

Step 4’s driver again waits (468.544 s in lock `acquire`). Worker hot spots are
`pyexpat.ParseFile` (91.491 s), `_overlap_fraction` (74.125 s), its generator
(50.428 s), plist `handle_data` (36.140 s), and Fraction operations (31–32 s
each). The two extraction workers consume 946.391 profile-seconds for a
477.9-second wall step. The step then refuses, so its profile describes the
work performed before refusal, not a successful step.

## Repeated-work candidates

Savings are estimated profile-process seconds if the named result were
computed once per run and safely reused with the **existing** identity and
validation semantics. They are opportunity estimates, not prescriptions: no
estimator, cache key, or refusal order is changed or proposed. cProfile shows
call multiplicity but cannot prove argument equality, so same-input claims
below are based on the synthetic driver repeatedly visiting the same committed
S10 files/bundles; implementation must verify exact identity before reuse.

1. **Repeated strict bundle validation — `joulewise/cli.py:_strict_problems`.**
   262 step-1 member calls cover about 2010.150 s cumulatively; step 3b adds
   roughly 421 s per profiled worker tranche and step 4 repeats it again.
   Compute the strict result once for each unchanged bundle: **~1,500 s saved**.
2. **Repeated fiducial physics verification/refits —
   `joulewise/powermetrics_fiducial.py:verify_stored_evidence_physics` and
   `rederive_detection_from_artifacts`.** Step 3b includes four verifications
   at 478.563 s cumulative and repeated rederivations; the same fitting path
   already ran in step 1 and runs again in step 4. Once per unchanged evidence
   bundle: **~650 s saved**.
3. **Repeated plist/XML parsing — `plistlib.load/loads/parse` and
   `pyexpat.xmlparser.ParseFile`.** `ParseFile` alone costs 424.225 s self over
   steps 1/3b/4 and is called 607,737 times; plist parsing cumulative time is
   larger. Reuse the parsed representation of each identical powermetrics
   plist: **~400 s saved**.
4. **Repeated pulse-overlap evaluation —
   `joulewise/powermetrics_fiducial.py:_overlap_fraction`.** 60.7 million calls
   in step 1, 242.9 million in step 3b, and 32.6 million in step 4 cost 496.285
   s self. Once per identical fit candidate/input pair: **~300 s saved**.
5. **Repeated uncertainty anchor derivation —
   `joulewise/uncertainty_evidence.py:derive_powermetrics_anchor_v3` / `_lp2`.**
   Step 1 invokes `_lp2` 28,116 times (852.038 s cumulative), and later strict
   passes rederive the same sealed evidence. Reuse each bundle’s authenticated
   derived anchor: **~250 s saved**.
6. **Repeated pulse-loss fitting —
   `joulewise/powermetrics_fiducial.py:_fit_pulse`, `loss`, and `_pulse_loss`.**
   Step 1 alone evaluates loss about 2.3 million times across the workers and
   later steps refit the same stored evidence. Once per unchanged artifacts
   and fit inputs: **~200 s saved**.
7. **Repeated strict uncertainty validation —
   `joulewise/cli.py:_strict_uncertainty_evidence_problems`.** Step 1 spends
   about 456 s cumulative over 262 calls, with another ~53 s in a step-3b
   worker and more in step 4. Reuse the strict result for the identical sealed
   uncertainty object: **~180 s saved**.
8. **Repeated hashing/read-ahead of unchanged files —
   `joulewise/b5_analysis/archive.py:_read_ahead_digest`,
   `analysis_run_cache.py:sha256`, and `_hashlib.openssl_sha256`.** Step 0
   performs 18,415 read-ahead digests (9.747 s cumulative) and 18,562 SHA-256
   calls; later steps hash tens of thousands more unchanged fixture files.
   Once per path plus the existing identity inputs: **~30 s saved**.
9. **Repeated calibration ledger loading —
   `joulewise/calibration_ledger.py:load_calibration_ledger_snapshot`,
   `_scan_physical_ledger`, and `_attempts_and_observations`.** Step 3b loads
   three snapshots in the driver (5.103 s cumulative), parses the ledger four
   times (6.734 s), and a worker parses it twice (4.507 s), with 1,348 driver
   calls to `_attempts_and_observations`. One immutable snapshot for this step:
   **~10 s saved**.
10. **Repeated acceptance-bound derivation —
    `joulewise/calibration_bracketing.py:_acceptance_bound_from_authenticated_bytes`
    plus `issue_calibration_acceptance_generation.py:student_t_quantile`.** The
    driver derives it once (1.135 s), and a worker repeats it three times
    (4.198 s cumulative), including 2,706 survival evaluations and nine
    quantiles in that worker. Once per authenticated acceptance input:
    **~4 s saved**.

JSON reparsing and process transport are measurable but smaller than the ten
items above: step-2 workers call `json.raw_decode` 1,310 times (~0.415 s self),
while step-2 driver pickle dump costs 1.233 s. `analysis_member_pool` export and
merge calls are numerous but contribute well under a second of self time in
these profiles; their large cumulative scopes are child work, not serialization
self time.
