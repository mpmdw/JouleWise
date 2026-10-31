# KB-MATCHED implementation report

Implemented on `codex/2026-10-31-kb-matched`, against
`79de7be49e34576fbd6f7e3c40ac52873b108558`. HEAD remains that commit. All changes
are uncommitted, as the resumed lead instruction requires. No push occurred.
The initial rule/report edits belong to this same task; no unrelated dirty work
was found. No additional scope is requested.

## What changed

The registration is one matched-geometry rule, assembled from RULE-REVISION.md
Part B with the admitted stack, gap, systematic-bound/native-variance, harvest
and historical-decision clauses retained. Its status remains **pending cold
review and the lead's admission**. The preceding admission is labelled history.

The probe now emits only `joulewise.bytes_stream.v3`: a 32 GiB ring in shape
`(Q,b)`, row views, repeat/rotate lists with identical indexing, whole-sweep
counts, actual view byte count/dtype, geometry pin, clock fields and logical
byte counts. The old signed-axis reasoning in `payload_shape` remains. The
residency check allocates once, reshapes through G/2^k, warms once per mode,
measures a one-sweep pilot then three calls, and stops at the first resolved
R−C timing contrast. Pilots and timing calls are durable. The knee code path
and cross-size energy fit are retired.

The stage checks residency before starting the energy capture. Refusal runs no
hour calls. A successful check plans R,C,C,R in whole sweeps at one b. Completed
receipts survive exceptions; started captures receive teardown. Allocation and
geometry reasons remain visible through harvest/read, including a failure in
the hour after a successful check.

Harvest accepts v3 measured receipts, preserves rejected evidence, and retains
one native power capture/one meter fit and the existing integrators. The reader
recomputes a successful check from receipts, checks every receipt's geometry,
uses Δ=(x_R−x_C)/b and δΔ=(δx_R+δx_C)/b, and applies κ only to the attribution
class and NOT RESOLVED upper limit. Existing native support, idle statistics,
battery, gaps, stack scope and repeatability rules remain. It prints the hour's
own timing contrast beside the check's, GPU state descriptions, four-significant-
figure ρ_L/κ, H2 intervals, and reasoned missing quantities.

Tests replace the retired knee/multi-size fixtures with matched v3 fixtures,
while retaining stack/provenance, native variance, malformed-input, integration
and archive safeguards. Fakes enforce signed 32-bit axes and shared row storage.
Repeat and rotate have different synthetic per-byte times; `--unresolved` makes
their times equal. Native prerequisite faults, check faults, durable exception
prefixes and hour-allocation refusal are exercised.

Only the approved count requirement and its diagnostic changed in
`joulewise/b5/chain.py`: eight becomes four. The isolated kit's generated plan,
plan-tree digest binding, README and planning derivations were updated.

## Decisions I made

1. Check receipts use `arm=check-C/check-R`, an integer `rung_index`, and
   `check_phase=pilot/timing`. A pilot must contain one sweep; the following
   three counts must match its registered whole-sweep planning formula. This
   prevents dropping calls, regrouping rungs or continuing past first success.
2. Saved successful timing summaries and κ are descriptive inputs: the reader
   recomputes them from receipts. Inconsistent success/status/b/W/Q or a reason
   attached to success refuses with no interval. A saved failure is never
   promoted into success by rereading its prefix. Geometry is recomputed even
   for failed-check evidence.
3. The residency allocation is released before the separately allocated hour
   calls. Only the palindrome starts the continuous powermetrics capture;
   the driver-owned meter still spans the whole chain.
4. Use §1 R5's stated **whole-ladder ~270 s plus one ~10 s fill** for worst-case
   planning. Do not introduce another multiplier from its approximate per-rung
   prose. Measured-hour planning remains 3573.6 s. Decimal planning arithmetic
   is evaluated exactly before conversion to float.
5. If an hour allocation/geometry failure follows a completed check, harvest
   carries its registered refusal reason in `check`, retaining the original
   result in `completed_check`. The raw check and call files are untouched.
6. The historical SUMMARY archive is replayed through the real R3/R4 timing
   functions using NOTES §1's explicitly supplied clock. It is **not converted
   into admitted v3 data**: its actual ring was 8 GiB, and it lacks the new
   receipt/geometry/clock fields. Both the historical timing outcome and the
   strict v3 refusal are printed. Run 2 is not counted: no receipts are archived.
7. The example transposes the archived per-dispatch times into synthetic
   production 32 GiB whole-sweep receipts, then uses the real stream and reader
   with §5's energy assumptions and native-variance fixtures. Accumulated
   synthetic time is rounded to integer nanoseconds, rather than rounding each
   dispatch separately. This does not claim a new hardware observation.
8. GPU residency descriptions average native interval time; active-frequency
   descriptions weight the decoder's `active_freq_mhz_weighted` by active time
   from `idle_ratio`. Missing support prints a reason; no class uses this
   description. Raw rows remain available.
9. Check clock prerequisites on hour receipts as well as check receipts; a
   missing clock/resolution/timebase retains the inputs, refuses all classes
   with the named clock reason and prints no interval. Preserve zero-width H2's registered `0.00` display, while rejecting negative
   or non-finite widths. DC validity requires a strictly positive lower endpoint.
10. A sandbox census failure after shell-chain exit 0 is retained as a real
    driver refusal. The synthetic fixture checks that specific failure, prints
    it, and continues to harvest the completed stage. It never writes a GO
    verdict. Child cleanup explicitly signals journaled groups and kills/waits
    tracked children, independent of ps/pgrep availability.

No threshold, noise multiplier or energy-acceptance bar was added. Exact
comparisons are used for integer contracts/hashes or identical code on identical
inputs. Independent numerical comparisons use the rule's printed-precision bar,
its κ relative bar, or 1e-6 relative where no half-width exists.

## Replay environment and commands

All Python implementation/verification commands in this resumed run used:

```sh
export JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/kb-matched-sol
PY=/opt/homebrew/bin/python3.13
```

Scratch is resolved under `/private/var`, not `/var`. Logs, helpers and synthetic
archives below are scratch artifacts. No Metal or physical measurement ran.
The report gives replay-equivalent commands using this environment; each was
executed with the variables explicitly set. Replays need fresh archive names.

### Module verification

```sh
"$PY" -B -m unittest tests.test_bytes_stream_test tests.test_bytes_stream_capture tests.test_bytes_stream_harvest tests.test_bytes_mac_kit
```

Combined run, log `$TMPDIR/all-final.log`:

```text
Ran 79 tests in 112.719s
FAILED (failures=1)
```

The sole failure was
`test_path_cli_bootstrap_without_editable_install`: it expects the ordinary-clone
cleanliness/lead-time check, but this checkout has a linked `.git` file, so
`prepare` correctly stops earlier with
`prepare must run from its own ordinary clone (no linked checkout)`.
This is the lead-described environment failure, not a matched-rule regression.
The other named test,
`test_prepare_authors_isolated_night_plan_without_default_ledger`, **passed** in
this run. Earlier combined runs had the same single failure (72 tests, then 74 before
adding the final native/clock/GPU/small-contrast regressions).

After adding the native fault grid and GPU descriptions, the final reader module:

```sh
"$PY" -B -m unittest tests.test_bytes_stream_test
```

```text
Ran 37 tests in 28.808s
OK
```

Additional focused commands and outputs:

```sh
"$PY" -B -m unittest tests.test_bytes_stream_capture.CaptureTests.test_exception_preserves_check_prefix_and_never_starts_capture tests.test_bytes_stream_capture.CaptureTests.test_hour_allocation_failure_prints_registered_reason tests.test_bytes_stream_capture.CaptureTests.test_ring_axes_and_aliasing_match_mlx tests.test_bytes_mac_kit.MacKitTests.test_stream_cli_runs_with_fake_mlx_and_writes_receipt
# Ran 4 tests in 0.402s; OK
"$PY" -B -m unittest tests.test_bytes_stream_test.ReaderTests.test_missing_and_invalid_native_leaves_preserve_boundary_scope tests.test_bytes_stream_test.ReaderTests.test_dc_zero_lower_endpoint_refuses_and_null_containers_are_reasoned
# Ran 2 tests in 10.677s; OK
"$PY" -B -m unittest tests.test_bytes_stream_test.ArithmeticTests.test_native_gpu_means_and_missing_support_are_descriptions
# Ran 1 test in 0.000s; OK
"$PY" -B -m unittest tests.test_bytes_stream_test.ReaderTests.test_small_true_contrast_uses_check_kappa_and_h2_upper_place
# Ran 1 test in 3.436s; OK
```

An initial reader test mocked `subprocess.check_output` broadly enough to catch
`platform.platform`'s subprocess; the fixture now supplies its OS observation
explicitly. The corrected reader runs pass. The initial harvest/Mac-kit run
passed 27 tests. No unrelated test modules or whole-suite discovery were run;
CI owns the full suite, per the brief.

### Production-shaped resolving chain

```sh
"$PY" -B -m tests.test_bytes_stream_capture --synthetic "$TMPDIR/resolved-archive"
"$PY" -B scripts/bytes_stream_test.py check "$TMPDIR/resolved-archive/runs_bytes_stream_test/capture/CHECK_RECEIPTS.json" > "$TMPDIR/resolved-check.json"
"$PY" -B scripts/bytes_stream_test.py read "$TMPDIR/resolved-archive/INPUT.json" > "$TMPDIR/resolved-read.json"
```

All three commands exit 0. The driver itself records the sandbox limitation:

```text
{"environment": "sandbox process-group census unavailable", "driver_exit": 6, "driver_verdict": "REFUSED", "chain_exit": 0}
```

Stage: completed; 4 records; residency resolved at b=67,108,864 B, W=34,359,738,368
B, Q=512. These sizes follow rung 0 and W/b. One rung uses 8 receipts = two modes
× (one pilot + three timing calls). κ=2.78120599577734 (printed 2.781), computed
from those synthetic timings.

```text
rails: 0.072001 ± 0.000011 J/GB — RESOLVED
GPU:   0.072001 ± 0.000011 J/GB — RESOLVED
DC:    0.1488 ± 0.0048 J/GB — RESOLVED
rest:  0.0768 ± 0.0049 J/GB — RESOLVED
share: 0.484 ± 0.016
claim_lines: {}
```

Independent raw integration prints:

```text
Independent arithmetic: 1.1e-07 J/GB * 118815.975276544 GB = 0.013069757280419841 J for this call; rails=25080.11637414316 J; meter=50159.61451522994 J; meter_edge_w=[64.84218, 22.014499999999998]; battery_edge_j=[0.0, 0.900005213394071]
```

Its bar is 1% of this run's smallest H2-printed half-width, 0.000011 J/GB;
convert to joules by the call's logical GB, and to watts by dividing by duration.
The test also checks this bar exceeds 10^6 times propagated binary64 noise.

### Production-shaped unresolved chain

```sh
"$PY" -B -m tests.test_bytes_stream_capture --synthetic --unresolved "$TMPDIR/unresolved-archive"
"$PY" -B scripts/bytes_stream_test.py check "$TMPDIR/unresolved-archive/runs_bytes_stream_test/capture/CHECK_RECEIPTS.json" > "$TMPDIR/unresolved-check.json"
"$PY" -B scripts/bytes_stream_test.py read "$TMPDIR/unresolved-archive/INPUT.json" > "$TMPDIR/unresolved-read.json"
```

All three commands exit 0. The same driver census limitation is printed and
retained. Stage: `residency not resolved`; 0 measured records; all eight rungs
retained, 64 receipts = eight × two modes × (pilot + three calls).
All four classes are UNDETERMINED; every contrast and the share print
`not defined (residency not resolved)`.

```text
Known-bytes check: rails memory-traffic attribution is undetermined (residency not resolved).
Known-bytes check: rest memory-traffic attribution is undetermined (residency not resolved).
```

The combined module run also executes the missing-fiducial chain: DC remains
RESOLVED, while rails/GPU/rest are UNDETERMINED with the missing anchor bound.

### Worked example through the real reader

```sh
"$PY" -B -m tests.test_bytes_stream_test --worked-example
```

Exit 0, output `$TMPDIR/worked.log`:

```text
Revision / real reader (J/GB):
rails: revision 0.075000000 ± 0.000306823; reader 0.074999603 ± 0.000306823; RESOLVED
dc: revision 0.344513000 ± 0.002389013; reader 0.344513072 ± 0.002389013; RESOLVED
rest: revision 0.269513000 ± 0.002695836; reader 0.269513469 ± 0.002695836; RESOLVED
Revision κ=6.213; reader κ=6.213
Revision f=0.2177 ± 0.0024; reader f=0.2177 ± 0.0024
rails x_R/x_C mJ=9.6911681, 7.1745991
rails δx_R/δx_C µJ=5.6252, 4.6701
dc x_R/x_C mJ=25.1404315, 13.5804911
dc δx_R/δx_C µJ=44.1959, 35.9660
rest x_R/x_C mJ=15.4492634, 6.4058920
rest δx_R/δx_C µJ=49.8212, 40.6361
```

Dispatch counts are exactly 2,459,648 for R and 2,962,432 for C per call, from
Q × floor(759.2/(Q*t)). The common comparison bar is 3.1e-6 J/GB = 1% of the
smallest printed half-width, 0.00031; the revision's 10^6×float-noise bound is
3.2e-10 J/GB. Independent Fraction arithmetic agrees within that bar. Meter-gap
and transient cases are tested through the reader, including the revision's
`0.098 ± 0.023` transient interval and κ-corrected class ordering. The small
true-contrast case prints `0.00030 ± 0.00031` and a claim-line upper limit
`0.00377 J/GB`, following §4's required decimal place; that upper limit rounds
to the illustrative §5 `0.0038` at two significant figures.

### Archived refusal replay

```sh
"$PY" -B -m tests.test_bytes_stream_test --replay-archive /Users/edr/night-archive/seats-c7fea69e/kb-knee-council/diag-matched/run-1
```

Exit 0, output `$TMPDIR/replay.log`:

```text
archive b=67108864: D=-41.657983 µs; δD=98.152795 µs; not resolved
archive b=33554432: D=52.410077 µs; δD=1.931119 µs; resolved
Refusal count: 0 of 1 replayable run; b=33554432; κ=6.213
Historical timing replay only: actual 8 GiB ring; clock supplied by NOTES §1; v3 geometry not attested.
Strict v3 reader gate: geometry check failed (schema_version)
```

This reproduces NOTES' historical timing refusal count while keeping the live
v3 admission gate strict. No archive file was written or altered.

### Config and scope checks

```sh
"$PY" -B configs/campaigns/bytes_stream_test/generate.py
"$PY" -B configs/campaigns/bytes_stream_test/generate.py --check
"$PY" -B "$TMPDIR/inspect_final.py"
git diff --check
```

Generator/check and whitespace check exit 0. Inspection prints:

```text
PASS: all changed paths are allowlisted; modified Python parses; chain diff is exactly the approved count/diagnostic change.
PASS: single matched rule, pending status and v3/RCCR; retained admitted clauses match verbatim.
HEAD=79de7be49e34576fbd6f7e3c40ac52873b108558
```

Generated planning is 3573.6 s for the measured session + 270+10 s for the check
= 3853.6 s stage. The existing chain allowances give
ceil(3853.6+2*1800+900+600+600+4*30+60) = **9734 s**. Disk is
**52,746,273,217 B** = 2*ceil((4502241280000000000000/1799796660838183 B/s)*9734 s)
+ 4,046,531,103 fixed bytes, using the existing sizing registration's measured
rate, two-copy factor and fixed retained bytes. Each input/source/formula is
recorded beside its generated result. No new reserve was added; resident ring
memory is not charged as extra disk.

All test-started direct children were killed/waited and journaled groups
signalled, with cleanup assertions passing. No test-created background process
is intentionally retained. The unavailable system census is not claimed as
proof of a live-machine quiet window.

## Remaining lead work

Cold-review/admit the rule and implementation, append the lead-owned executing
review record, run CI's full suite and the quiet hardware rehearsal, then commit
from the lead's writable Git environment. This sandbox supplied synthetic and
archived timing evidence only. The 32 GiB row-view allocation/build time, source
pin on the actual build, capacity premise and timing-model premise retain their
registered status; no live validation is claimed. No commit was attempted after
the resumed instruction to leave the tree uncommitted.
