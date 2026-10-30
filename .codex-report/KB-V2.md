# KB-V2 — activation 39206674, 2026-10-28

Status: Steps 1 and 2 implemented and locally verified; reconciled rule awaiting the lead's admission. No hardware measurements. CI read: completed checks pass; ordinary shards still in progress. Stopped at the scope boundary for v1 compatibility-test updates.

## Authority and inputs

User brief: base `ci/2026-10-27-bytes-enddate` at `e624d67c7ca154c67df77f105b6aa8adcad047a4`; branch `codex/2026-10-28-kb-v2`.
Write scope is exactly the registration draft, probe, new probe test module and this report.
The brief overrides local broad-suite and bookkeeping defaults: run only the touched test module; preserve every other file.
Environment: `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, `/workspace/.joulewise-env/bin/python3.13` (3.13.5).

Inputs fetched successfully from mpmdw/JouleWise-data:
- Fable `39398e572ea0943edc77f0981d82e3be32311a32`, `kb-cold/REPORT.md`.
- Opus `ecd46c1124000dbfbc51b475068661ceefb62a1f`, `kb-cold/REPORT.md`.
- Reconciler `0609bcc0caf941fd68c36fccea323f34c3951730`, `kb-revise/`.
- Current draft: JouleWise main `8b39d4846de168ab3fb83b21084238e3491ade21`.

## Decisions I made

- Adopt the lead's Fable 1 ruling (a): retain the disclosed remainder, ε_flip and per-arm GPU frequency/residency. No new kernel or leverage model.
- This is bounded [AGENT] implementation/documentation work; no quiet-Mac collection, unblinding, admission or merge.

## NEEDS_RULING

None at intake. The access exception does not apply: all inputs are reachable.

## Step 1 — correction audit

Locations below refer to sections of the installed reconciled draft (the wording is unchanged except Status and the worked-script locator listed below).

| Id | Asked | Where applied | Verdict |
|---|---|---|---|
| Fable 1 | Charge cache fixed-cost non-constancy; qualify one-sided-error claim | §1 C3 and eight-call order; §3 arithmetic 5, propagation, uncovered remainder and Bias; §4 descriptions; §5 false-positive case | applied: residual charged in both δγ_c and δα. It does not fully bound the example; lead option (a) expressly adopts that disclosure. |
| Fable 2 | Marginal-throughput knee and plateau-pair band | §1 knee steps 1–6; §5 Knee | applied differently: marginal throughput retained; measured-range band replaced by derived one-sided m_th, reconciling Opus 6. The straddling pair is slower than DRAM, so a two-sided band would move K. |
| Fable 3 | Precedence prevents RESOLVED/BELOW overlap | §4 ordered class table; §5 overlap case | applied: first matching row wins. |
| Fable 4 | Sum available calls; UNDETERMINED if DC unavailable | §3 Meter gap; §4 row 1 and reason list | applied differently: any affected stamped span removes DC/rest for the whole test, every class UNDETERMINED; rails/GPU Δ retained. Opus 8's choice preserves symmetry and repeatability; no partial-call estimator is invented. |
| Fable 5 | Consistent cache sizes and recomputed uncertainty | §1 Sizes; §4 about 12 ε₀; §5 4/8/16 MiB and table | applied: Bc1=K/16, C3=K/8, Bc2=K/4; numerical execution agrees. |
| Fable 6 | Rest mechanism caveat, corrected upper limit, signed wording | §0; §4 response paragraph, slot sentence and printed lines | applied: conversion/fans disclosed; limit divided by 1−φ; “differed” with DRAM-minus-cache sign. |
| Opus 1 | Repeatability term or agreement check | §3 Repeatability and Propagation; §5 transient | applied: additive max(N)/ΣN term generalizes half-difference to unequal counts; 5 W transient becomes NOT RESOLVED. |
| Opus 2 | Restrict “never toward resolved”; describe GPU frequency/residency and thermal level | §3 Bias/uncovered remainder; §4 Description only | applied: only cache leakage has the one-sided statement; diagnostics explicitly required. |
| Opus 3 | State class precedence | §4 Classes | applied. |
| Opus 4 | Wholly negative UNDETERMINED; bound both interval ends for BELOW | §4 rows 1 and 3; §5 negative/small cases | applied: negative reason and max absolute endpoint. |
| Opus 5 | Bias-correct NOT RESOLVED upper limit | §4 printed line; §5 0.00089 | applied. |
| Opus 6 | Fix rising-side knee, derive tolerance, refuse infeasible knee | §1 knee steps 2–6 | applied differently: marginal throughput removes fixed-time rising side; all subsequent pairs must meet derived threshold, rather than explicit whole-throughput peak search. Refusal is explicit. |
| Opus 7 | Compared stack projections/reference | §2 item 2 table and reference paragraph | applied: machine/device and runtime name/version only; seven package keys; kernel unavailable equals unavailable. Independently checked all 19 registered units agree on projections at 6731d5249. |
| Opus 8 | Meter gap, b_i definition, receipt-span variance, warm-up order | §2 item 1 and Capture/harvest; §3 Meter gap, per-call bound, baseline | applied: whole-test gap rule; b_i sum; named Bartlett/IID-floor estimator; warm-up before pre-idle. |
| Opus 9 | Correct se_idle and all dependent printed numbers | §3 baseline/agreement; §4 ε₀ ratio; §5 | applied: √(v_pre+v_post)/2; table/bar/ratio execute as quoted. |
| Opus 10 (nonblocking) | Amend registration §1 wording, rest caveat, agreement rule, glosses, tree paths | §4 proposed wording and slot; §3 Agreement bar; Status, §§0–3, §5 | applied differently: registration amendment is proposed here, not written outside scope. One common bar replaces per-boundary bars to satisfy this brief. Glosses and source tree supplied. |

No missing correction ids. Nonblocking Fable notes are also incorporated: explicit inputs, scale wording, count/φ agreement, size rationale, scan flags/allocation fallback, warm-up placement, GPU series and harvest plumbing.

### Independent arithmetic check

A second recomputation used Python 3.13 decimal.Decimal with 50-digit precision, directly from the printed source/assumed inputs and §3 formulas (not the reconciler's arithmetic functions). Publication strings, not a new numerical tolerance, were compared. All table digits and counts agree:

```text
rails: alpha=1.4000 mJ, gamma_c=0.02800, gamma_d=0.09472, delta=0.066716626, halfwidth=0.000571796, N=[38457, 4613030, 3743791]
dc: alpha=2.6500 mJ, gamma_c=0.05300, gamma_d=0.24594, delta=0.192943505, halfwidth=0.002345131, N=[38457, 4613030, 3743791]
rest: alpha=1.2500 mJ, gamma_c=0.02500, gamma_d=0.15123, delta=0.126226879, halfwidth=0.002265001, N=[38457, 4613030, 3743791]
epsilon0 0.000049009052306508565348800952662555789157502220838697
threshold_GBps 335.12493427470529063389713447750248541739917022974
se_idle 0.0077578992001701079075615640442830854506491747057725 0.035355339059327376220042218105242451964241796884424
f=0.3458 +/- 0.0072
rails: epsilon_flip=7.20 microJ, share=0.51%
dc: epsilon_flip=29.54 microJ, share=1.11%
rest: epsilon_flip=28.53 microJ, share=2.28%
Decimal audit: all table publication digits and counts agree; no added tolerance
```

Read-only final audit also confirmed that current-main's draft is byte-identical to the cold-reviewed draft at 948cc31b9, and that the installed reconciler body differs only in the relocated worked-script citation (besides the required Status block).

### Fixes made to the reconciler's artifact

1. Required Status change: name both cold reports and the reconciler, record the lead's option (a), and state awaiting admission.
2. Correct the §5 “beside this text” script locator to its pinned JouleWise-data path: execution confirms the script lives in kb-revise/, not the destination registration directory. No numerical or rule change.

### Worked-example execution

Executed the exact fetched script in memory (no out-of-scope checkout/output files):

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.joulewise-env/bin/python3.13 - <<'PY'
import subprocess
source = subprocess.check_output(['git', '-C', '/workspace/JouleWise-data', 'show',
    '0609bcc0c:kb-revise/kb_worked_example.py'], text=True)
exec(compile(source, 'kb-revise/kb_worked_example.py', 'exec'))
PY
```

Exit 0. Entire output matches the reconciler's committed .out byte-for-byte. All §5 values reproduce: source/assumed powers, idle errors, knee (including old-rule 512 MiB/1 GiB), sizes, repeats, hour/midpoints, α/γ/r/Δ/δΔ, ε_flip/shares, f, agreement bar and three counterexamples. Other quoted arithmetic: 1/331.6 GB/s ≈ 3 ps, 1/TB/s = 1 ps; ε₀=1/(512×39,852,331,520/1e9)=4.90091e−5; 20,404.394 GB; δΔ_rails/ε₀=11.7≈12; 0.1×Δ_rails=0.0066717≈0.0067 (2.95 rest half-widths≈3); 341≈340 leverage; 16×57.6=921.6, 16×3=48, 8×10=80, total 3549.6 s; τ=2×1+0.302=2.302 and next whole second=3; r_max+20 ms≈38 ms; 1/(1−1/64)−1≈1.6%; 32 GiB/64=512 MiB. These are quoted/planned quantities, not new tolerances. Source record numbers are inputs, not measurements re-created on this seat.

Worked-example output tail:

```text

rest : alpha = 1.2500 mJ  gamma_c = 0.02500  gamma_d = 0.15123  r = -0.000 uJ  Delta = 0.1262 ± 0.0023 J/GB  (full 0.126227 +/- 2.265e-03)  -> RESOLVED
description: f = Delta_rails / Delta_DC = 0.3458 ± 0.0072; phi = 0.015625
  eps_flip rails = 7.20 uJ per dispatch = 0.51% of alpha
  eps_flip dc    = 29.54 uJ per dispatch = 1.11% of alpha
  eps_flip rest  = 28.53 uJ per dispatch = 2.28% of alpha
agreement bar = 1% of smallest printed half-width = 5.7e-06 J/GB; 1e6 x float noise (largest boundary) = 2.5e-10 J/GB; between: True
1% of each half-width: rails 5.7e-06, dc 2.3e-05, rest 2.3e-05
delta_rails / eps0 = 11.7

== Classes on hand-set intervals (J/GB) ==
Fable 3a overlap        : +0.00003 ± 0.00001 -> RESOLVED
Opus 3b negative rest   : -0.01000 ± 0.00200 -> UNDETERMINED (contrast negative)
small, spanning zero    : +0.00001 ± 0.00002 -> BELOW ATTRIBUTION LEVEL
draft §5 contrast       : +0.00030 ± 0.00054 -> NOT RESOLVED (upper limit 0.00085 J/GB, cache-bias corrected)

== True Delta_rails = 0.00030, no transient ==
rails: alpha = 1.4000 mJ  gamma_c = 0.02800  gamma_d = 0.02830  r = -0.000 uJ  Delta = 0.00030 ± 0.00057 J/GB  (full 0.000300 +/- 5.718e-04)  -> NOT RESOLVED (upper limit 0.00089 J/GB, cache-bias corrected)
dc   : alpha = 2.6500 mJ  gamma_c = 0.05300  gamma_d = 0.17953  r = +0.000 uJ  Delta = 0.1265 ± 0.0023 J/GB  (full 0.126527 +/- 2.335e-03)  -> valid
rest : alpha = 1.2500 mJ  gamma_c = 0.02500  gamma_d = 0.15123  r = -0.000 uJ  Delta = 0.1262 ± 0.0023 J/GB  (full 0.126227 +/- 2.255e-03)  -> RESOLVED
-- with a 5 W transient through the first S call (Opus 1b): Delta_rails = 0.00787 ± 0.00814 -> NOT RESOLVED (upper limit 0.01626 J/GB, cache-bias corrected); without the repeatability term the half-width would be 0.00057
-- true Delta_rails = 0, C2 fixed cost 1% below C1 (Fable 1c), C3 at half the step: r = -2.33 uJ, Delta_rails = 0.00111 ± 0.00076 -> RESOLVED
-- true Delta_rails = 0, C2 fixed cost 1% below C1 (Fable 1c), C3 linear in GPU duty cycle: r = -0.67 uJ, Delta_rails = 0.00111 ± 0.00063 -> RESOLVED
```

## Step 2 — receipt and tests

### Receipt diff summary (file:line)

- `scripts/bytes_stream_test.py:44`: read registered reference projections from the two §2 pin files; verify unit projections agree.
- `scripts/bytes_stream_test.py:60`: collect platform/machine, passed-in device, mx.__version__, pass-1 kernel-library fallback, Python/all packages through runtime_versions(sys.executable), checkout git HEAD, and all five not_applicable fields. Collection is outside all stamped spans.
- `scripts/bytes_stream_test.py:77`: compare exactly the §2 projections, every package key and Python; omit adapter/config_id/model fields/git from comparison. Capture fields come only through harvest's capture_stack argument. Missing capture identity remains pending_capture; it is never called a match. Differences do not suppress the receipt.
- `scripts/bytes_stream_test.py:114`: injected array module, clock and sleep; defaults 57.6 s idle and 3 s settle (from §2, not invented bars). Allocate/fill/evaluate/sync; one warm sum/eval/sync; pre-idle; settle; measured fresh reductions/sync; settle; post-idle, retaining payload. All six stamps are integer CLOCK_MONOTONIC_RAW ns. Zero idle/settle supports the knee scan.
- `scripts/bytes_stream_test.py:166`: v2 receipt preserves logical byte counts/duration/boundary/non_claim and adds idle stamps, requested idle/settle lengths, stack and comparison result. Warm-up is excluded from counts and duration; gaps enter no span.
- `scripts/bytes_stream_test.py:177`: CLI adds --device (required, passed from hardware_target.id), --idle-s and --settle-s; strict JSON output retained.
- `tests/test_bytes_stream_test.py:81`: fake-array/event-clock tests for ordering, payload residency, exact counts/stamps, zero-span scan mode, bad clocks/arguments, all compared fields/packages, capture deferral/mismatch, ignored projections, reference consistency, CLI/help and end-to-end fake MLX with real runtime metadata and git sources.

### Decisions I made (implementation)

- Device must be explicitly supplied from the checkout's run config (--device), rather than guessed from platform.machine or copied from the pin being checked.
- Identity equality is the registered string/key projection equality in §2; no numerical tolerance enters the identity comparison. Synthetic timing assertions use integer ns and the exactly representable 1/2 s conversion, not a new timing bar.
- Record stack differences and retain the receipt; a mismatch is an interpretation failure under §4, not an exclusion of collected numbers.
- Compare local fields immediately; expose compare_stack(..., capture_stack=...) for harvest to complete comparison with concurrent telemetry identity. Missing capture fields are explicitly pending, not fabricated from reference values. The full check can only match after harvest.
- Keep the kernel unchanged (sum/eval per dispatch); add precisely one warm reduction before pre-idle. Do not implement the rejected alternative kernel or leverage model.
- §2's continuous powermetrics/meter capture, one clock fit, arbitrary-span integration with existing pass-1 integrators and τ-dependent post-idle trimming are capture/harvest operations, not performed by this probe. The receipt supplies raw spans and the comparison helper; no new energy reducer or capture launcher was added. No measured τ can be invented on this non-Metal seat.

### §2/code disagreements and scope boundary

- Compared with v1, the old probe had no idle spans/settle gaps/stack and compiled its first reduction in the measured span. Those disagreements are fixed in v2.
- No identified disagreement remains in the receipt-producing operations of §2. The capture/harvest paragraph remains an external operational requirement; this change does not claim to implement or validate that chain extension. In particular, telemetry_backend/rails identity and τ-based trimming require the actual capture at harvest, not a locally guessed value.
- The existing v1 tests in `tests/test_bytes_mac_kit.py:85` and `:110` omit the now-required device, provide a fake module with no __version__, assume only two stamps and no warm reduction. They require a v2 update outside WRITE_SCOPE. **Preserved unchanged; no broader test module was run locally.** The existing README invocation also needs the device/idle/settle arguments when the lead updates operational instructions; `configs/campaigns/bytes_mac_check/README.md` is outside scope and preserved. No attempt was made to repair these other files.

### Test command and output tail

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.joulewise-env/bin/python3.13 -m unittest -v tests.test_bytes_stream_test
```

```text
test_scan_zero_idle_and_settle_still_stamps_and_warms ... ok
test_stamps_use_one_clock_and_exclude_idle_settle_and_warmup ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.291s

OK
```

Earlier run: 16 tests passed; then added the end-to-end fake-MLX CLI test and reran this same touched module. `git diff --check`: exit 0. No hardware validation, full suite, quiet capture, blinded data, new tolerance or out-of-scope repository file writes.


## CI

Draft PR **#593**, [CI only: KB-V2](https://github.com/mpmdw/JouleWise/pull/593), targets `ci/2026-10-27-bytes-enddate` at exactly `e624d67c7`. Still draft; no merge or admission.

Code/test head: `5e2833d1e923bcbb0e8d69e1f27b9972b83f38e0`.
[CI run 40681260779](https://github.com/mpmdw/JouleWise/actions/runs/40681260779) (ci #3844): **IN_PROGRESS, not established green** at the final observation. Read via the GitHub connector (the CLI's api.github.com route is forbidden; Git operations and connector reads work).

| Job | Observed result |
|---|---|
| changes | success |
| fences | success |
| build | success |
| installed-wheel | success |
| quick | success |
| calibration-exits-exclusive (3.13) | success |
| calibration-writer-crash-matrix-exclusive (3.13, 1 and 2) | both success |
| ordinary test (3.13, shards 1–12) | all in progress; no completed result yet |
| gate-ledger (run 40681260764) | skipped (draft) |

Read the completed quick job's log (job 122792993711); relevant tail:

```text
2026-10-28T11:38:37.7814951Z EXCLUDE tests.test_bytes_mac_kit: unknown weight
2026-10-28T11:38:37.7816289Z EXCLUDE tests.test_bytes_stream_test: unknown weight
2026-10-28T11:42:12.6954316Z QUICK SUMMARY tier=quick modules=213 excluded=246 failures=0 seconds=214.936 result=PASS
```

Thus quick green does not cover either probe module. The new module's direct local 17-test pass is the evidence for it. No CI failure is asserted before a completed job log establishes it. This final report-only checkpoint will trigger another CI run; it does not change the verified code or tests.

## Scope stop and handoff

The four allowed files are the entire branch diff. The old v1 compatibility tests in **tests/test_bytes_mac_kit.py** need a v2 update outside that allowlist; stop here rather than editing them or adding a v1 behavior path that contradicts §2. The operational invocation in **configs/campaigns/bytes_mac_check/README.md** is likewise unchanged. These are scope boundaries, not unresolved choices changing which data count or a printed number; NEEDS_RULING remains none.

Next exact step: lead review/admission of the reconciled rule; observe the ordinary/final-head CI result and authorize any compatibility-test or operational-instruction update separately. Capture/harvest integration and actual Metal validation remain external to this synthetic receipt change.

Final checks: `git diff --check e624d67c7` exit 0; `git diff e624d67c7 --name-only` contains exactly the four WRITE_SCOPE paths; reconciler-body preservation and main/cold-reviewed draft equivalence PASS. One optional static CI-layout introspection attempt stopped while importing a split-declaration module because the read-only shell could not probe a temporary directory; it executed no test methods and changed no repository file. Only tests.test_bytes_stream_test was executed locally.

Commit checkpoints: `3c1776298` early authority/access; `c644a5b3c` Step 1; `5e2833d1e` Step 2; final report-only evidence checkpoint follows. Each checkpoint committed and pushed.


## Round 2 — authorized v2 compatibility and operations follow-up

Authority: magistrate activation 39206674, 2026-10-28 follow-up. Continued
`codex/2026-10-28-kb-v2` at exactly `9add41e36a21acd8247ca4f475dd9c8fc17761fe`.
The exhaustive write scope for this round is `tests/test_bytes_mac_kit.py`,
`configs/campaigns/bytes_mac_check/README.md` and this report. The previous
round's scope stop is resolved for those two named files only.

### Changes and decisions

- Updated both legacy probe compatibility tests to v2: explicit device,
  fake MLX `__version__`, six ordered integer RAW stamps, one warm reduction
  and synchronization before pre-idle, and five distinct evaluations (payload,
  warm result, three measured results). Retained logical byte count, positive
  measured span, duration tolerance, clock, non-claim and bad-count assertions.
  CLI smoke uses zero idle/settle for a fast synthetic invocation; the direct
  test injects sleep and six stamps to check nonzero idle/settle behavior without
  wall-clock waiting. No v1 code path and no production-code changes.
- Updated the operational command with `--device DEVICE --idle-s 57.6
  --settle-s 3`. DEVICE comes from the checkout config's `hardware_target.id`.
  Linked the governing draft; documented warm-up and payload residency,
  logical count/span boundaries, the eight-call continuous captures and one
  clock fit, unchanged pass-1 span integrators, measured-τ post-idle trimming,
  and local versus harvest stack comparison sources. Capture/harvest work
  remains external to the probe; these instructions do not claim it is done.
- NEEDS_RULING: none. All changes follow the branch's §2 and the explicit
  follow-up; no choice changes which data count or a printed number.

### Verification

Python: `/workspace/.joulewise-env/bin/python3.13` (3.13.5).

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /workspace/.joulewise-env/bin/python3.13 -m unittest -v tests.test_bytes_mac_kit tests.test_bytes_stream_test
```

Baseline: 21 tests, one failure and one error, both existing compatibility
calls missing the required device. Final: **21 tests in 0.761s, OK** (four kit
tests and 17 receipt tests). `git diff --check`: exit 0. Fixture orphan census:
`[]`, exit 0. Only the two requested test modules ran; no full suite or hardware
capture. Synthetic evidence is not hardware validation.

### Push and CI handoff

PR #593 remains draft, targeting `ci/2026-10-27-bytes-enddate`; no admission or
merge. Before this round's push, the connector reports the prior head's
[ci run 40683266757](https://github.com/mpmdw/JouleWise/actions/runs/40683266757)
as **queued**, with gate-ledger skipped (draft). This is not green evidence.
This Round 2 checkpoint is committed and pushed with the two compatibility
updates. The final response records the remote-confirmed SHA and its CI
observation after push, avoiding another report-only commit that would replace
the observed head. The full-suite/live/merge gates remain lead-owned.


## Round 3 (fix round)

Authority: magistrate activation 39206674, 2026-10-28; continued
`codex/2026-10-28-kb-v2` at `94af71056` (draft PR #593). Both executing
reviews were reachable and read: Sol `.codex-report/KB-V2-REV-SOL.md` on
`codex/2026-10-28-kb-v2-rev-sol`, and Opus `kb-v2-rev-opus/REPORT.md` on
JouleWise-data `claude/kb-v2-rev-opus-t9vl2k`. R1–R9 govern this round.

### Step 1 — reading rule and arithmetic

- R1: derive per-dispatch uncertainty from two half-nanosecond stamp endpoints
  plus the three-call spread; propagate through the reciprocal marginal
  throughput and harmonic threshold. Undefined differences never count above
  threshold. Before: Sol's unquantized/quantized DRAM-only scans falsely found
  8/4 MiB knees. After: both give `knee not found`; the worked example retains
  64 MiB in both cases. Zero, negative and uncertainty-overlapping differences
  are explicitly undefined.
- R2/R4/R9: print every stack difference, scope the interpretation consequence
  to OS/hardware/MLX/MLX-Metal with physical reasons, use the nonsingular δf,
  and print `not defined (<reason>)` for unavailable descriptions without a
  refusal. Name `hazards/monitor/thermal.jsonl` and correct the device source.
- R3/R5: estimate meter and battery idle means separately at native cadence and
  sample support; add their SEs using the correlation +1 bound. Bound counter
  gaps by missing time times adapter rating plus measured battery maximum,
  propagating idle gaps through their half-weight. No alignment, covariance
  estimate or partial-call selection. Revised §5: DC 0.1929 ± 0.0025, rest
  0.1262 ± 0.0024 J/GB; f = 0.3458 ± 0.0075. One 20 ms gap in call 4 adds
  2.8 J and yields DC/rest half-widths 0.0026/0.0025, still resolved.
- R6: the hour is 3573.6 s with 24 settle gaps; paired stream midpoints share
  1788.3 s, 1.5 s past the session midpoint. Linear drift cancellation holds.

Decisions I made: use the maximum observed deviation around the three-call
mean plus mean stamp-resolution bound; bound threshold uncertainty too; retain
arithmetic sample weights for meter/battery as their integrator requires;
illustrate separate SEs with assumed 0.05 W meter and 0.01 W battery per span.
The latter is an explicit example assumption, not a measurement. Preserve the
existing missing-battery prerequisite. NEEDS_RULING: none.

Verification: the baseline 21 focused tests passed. Re-ran Sol's five repros:
false knees, metadata-only mismatch, hold/linear variance discrepancy and both
zero divisions reproduced; the duration tolerance was present. The revised
independent arithmetic fixtures (5 tests) pass, including the bounded gap and
all revised publication digits. The original worked script at `0609bcc0c` was
executed in memory before and after substituting the stated R3/R6 inputs;
its original output and revised arithmetic reproduce. Agreement bar remains
5.7e-6 J/GB, above 1e6 × float noise (2.5e-10). No hardware evidence.

### Step 2 onward

Continuation authority: magistrate activation caa9ff66, 2026-10-28, starting at
`86b73a26b`. Step 1 was read first and retained. Both reviews were reachable.

Step 2 — R1 in the program: `knee_scan` consumes the real three-call receipts,
prints every pair, undefined reason, margin and propagated bar; `scan` exposes
it through the CLI. The tests now call this implementation instead of their
own transcription. Before: Sol's exact DRAM-only repro found 8/4 MiB knees;
Opus's exact noise script reproduced its reported refusal rates. After: both
DRAM-only cases give `knee not found`; the §5 model gives 64 MiB, with and
without quantization. Zero/negative/uncertain differences never count.
Decision: retain Step 1's endpoint propagation, without an added epsilon.

Step 3 — R2/R7: receipts contain full actual/expected comparisons, all
physical/disclosure differences and pending capture fields. Embedded projections
come from `6731d5249`; both source SHA256 values match the registered git blobs
and are printed in every receipt. Every running-checkout unit and the versions
file are compared; missing/unreadable/divergent references are recorded, never
raised. Before: Sol 2 reproduced the metadata-only veto; Opus 4's checkout
reference could raise. After: transformers-only changes have no physical veto;
all governed physical fields do, and divergent/unreadable checkout files still
produce comparisons/receipts. Both focused modules pass (27 tests).
Decision: capture metadata and kernel_library remain full disclosures, per R2;
only OS/hardware and the MLX/Metal versions affect physical transfer.

Step 4 — R6/R9 code: sleep one existing settle gap after warm-up synchronize
and before the pre-idle stamp. All three gaps are outside the stamped spans.
Before: Opus's exact production-shaped eight-call fake run confirmed immediate
pre-idle; Sol 5 found the 1e-6 duration tolerance. After: the same review script
writes eight receipts with the added gap (its old-order boolean now correctly
prints False); event-order tests assert the new first sleep. Duration is exact
1.0 for 10^9 ns. Both focused modules pass (26 tests). Step 1's 3573.6 s hour
and common midpoint offset remain correct; no arithmetic correction required.

Step 5 — R3/R4/R5 and the §3/§4 reader: native rails/GPU intervals and
meter/battery polls feed the named estimator with their own cadence and sample
support. DC adds separate SEs; no alignment/covariance choice exists. The reader
uses actual receipt spans and integrator products, adds source-labelled gap
bounds (including half-weighted idle gaps), computes repeatability/contrasts,
prints the full stack comparison, ordered classes, H2 intervals and claim lines.
The nonsingular share and reasoned undefined descriptions never veto a class.
The CLI now exposes `read`; its harvest-input contract is documented in §4.
Thermal descriptions name `hazards/monitor/thermal.jsonl`; no journal is invented.

Before: exact Sol 3/4 repros showed hold/linear SEs 0.0131781/0.0122875 W and
two zero divisions. Opus's exact replay voided DC/rest on a single gap. After:
the native-cadence program has one SE construction; zero rails yields f=0,
δf=0.01 on Sol's inputs. The real `stream()` ran all eight §5 production-sized
calls through constant-memory fake arrays with the full repeat counts, then
native synthetic harvest samples through the real reader and JSON CLI.
It reproduces the revised §5 numbers within the existing 5.7e-6 J/GB bar:
DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024, f 0.3458 ± 0.0075. A single C2 gap
adds 2.8 J, leaving DC/rest RESOLVED at ±0.0026/±0.0025. Tests cover baseline
gap weighting, native support failures, missing battery, zero α, invalid DC,
missing knee, disclosure-only versus physical mismatches and ordered classes.

Opus's seeded 2000-trial-per-level noise experiment was also rerun through the
new program, retaining all three individual call durations and stamp rounding.
Noiseless: 100% 64 MiB. At 0.05/0.10/0.20/0.30/0.50% per-call noise, the
not-found fractions are 31.45/29.70/29.95/29.10/30.65%. This is a limitation of
the admitted reference/uncertainty rule (unresolved references must not count),
not evidence warranting a new percentage band. Decisions I made: retain that
rule exactly; expose raw recomputation values alongside governed printed values;
keep capture/integration outside this probe reader and require their products.
All evidence is synthetic. Step 1's arithmetic needs no correction.
Verification for Step 5: both touched modules pass, 32 tests. Only these
modules were run, as requested; no full-suite or live-hardware claim is made.

Step 6 — R8: edited the generator's README string, then regenerated the kit;
no generated file was hand-edited. All documented Mac invocations use
`/opt/homebrew/bin/python3.13`. The Linux seat has `/usr/bin/python3.13`
(3.13.5), so synthetic execution/checks used that available interpreter.
Before: Opus 1's exact README comparison was False and `--check` drifted first
on the 8B-8bit config. After: README bytes equal the generator, and
`python3.13 -B scripts/bytes_mac_kit.py --check` passes. The generator alone
updated `configs/campaigns/bytes_mac_check/plan_tree.json`'s generator SHA256,
its source manifest locators/digests, and the five 8B-8bit configs plus their
order-manifest digests (the source revision is now explicit). Those are the
existing moved-input drifts exposed by regeneration; no source inputs changed.
The generator skips identical files, so the already-identical out-of-scope
`configs/b6/smoke_keep.json` was not rewritten. Tests now require byte equality
with every generated output instead of accepting historical drift.
Verification: both touched modules pass, 33 tests; `--check` and
`git diff --check` pass. Decisions I made: regenerate from the current supplied
inputs as R8 requires, retaining their exact source locators and hashes.
NEEDS_RULING: none. No hardware capture, unblinding, admission or merge.

Step 7 — final verification and CI snapshot. Implementation steps were committed
and pushed separately: Step 2 `3bffbf220`, Step 3 `1d00f80d1`, Step 4
`6cbbcd517`, Step 5 `46c5777be`, Step 6 `c748238eb`. The final implementation
has 33 passing focused tests and a passing generator `--check`; the complete
round diff passes `git diff --check`. The changed-file list is wholly inside
WRITE_SCOPE. No changes to RUN_STATE, TASK_QUEUE, smoke_keep or data-repository
content were made. The final report is a separate commit.

PR #593 remains open and draft. CI was read through GitHub: the starting
`86b73a26b` CI run [40696166708](https://github.com/mpmdw/JouleWise/actions/runs/40696166708)
completed successfully (all returned jobs, including fences, quick, build,
installed-wheel, calibration exclusives and all 12 unit shards, passed);
gate-ledger was skipped. At the final code/kit head `c748238eb`, CI run
[40759703837](https://github.com/mpmdw/JouleWise/actions/runs/40759703837)
is pending, and gate-ledger run 40759703675 is skipped. This is a status
snapshot, not a claim that the new head is CI-green. No approval rejection or
scope blocker occurred. NEEDS_RULING: none.

## Round 4 (fix round)

2026-10-28, magistrate activation caa9ff66. Continued `a7a20c197` on
`codex/2026-10-28-kb-v2` (draft PR #593). Read Sol delta review, Opus delta
review and all its scripts, and knee consult at `47bead35d`.

Step 1 — K1–K2. Installed the consult's replacement §1 scan steps, Sizes
bullet and complete §3, plus its revised §5 knee numbers. Exact reciprocal
endpoints, largest-lower-endpoint cache reference (smaller-size tie), monotone
threshold endpoints and both actual cache-arm increment checks now govern the
program. Every call/pair, candidate K and arm check remains visible; no retry,
late-pair filtering or shrinking K. Receipts collect RAW getres, macOS
mach_timebase_info, clock identity and unknown conversion/source. The bound is
2(r+1 ns)/N: two endpoints, each within max(getres,tick) plus integer conversion.
The lead's 2026-10-28 Mac measurement gives r=42 ns and 86 ns/N.

Before: reproduced 123/400 noisy worked refusals and 72/200 noiseless tick
DRAM false knees; the original focused baseline passed 33 tests. After:
the same metadata-completed seeded scenarios give 0/400 refusals at 0.05%
noise and 0/200 noiseless DRAM false knees, with 200/200 worked K=64 MiB.
The three original DRAM-noise cells give 0/200 accepted each; these observed
rates are not guarantees. Original pre-metadata inputs now print missing-clock
reasons; adapted replays explicitly add synthetic clock provenance. The old
single-line candidate patch is superseded by the ruled production rule.
The ported rational check reproduces margin 664.900336137 GB/s, bar
0.000429892228 GB/s and threshold uncertainty 0.000044586060 GB/s.
Agreement bar 4.5e-7 GB/s = 1% of 0.000045; 1e6 times exact-rational/binary64
discrepancy is 2.879319e-7 GB/s, below that bar. Energy-example numbers do not
change. Both touched modules pass 38 tests, including the reduced fixed-seed
noise sweep (no rate assertions), both integer conversions, and real stream
receipts written/reloaded through the scan CLI for worked and DRAM-only models.

Step 2 — F4–F6, F8–F9. Missing prerequisites print complete inputs, all retained
calls, available per-call/complete-arm arithmetic, central contrasts and reasoned
undefined bounds. Replayed Opus's five exception cases before and after: unnamed
gap source, absent adapter rating, lost call, absent r_max and missing meter
integral now print UNDETERMINED instead of raising. Additional CLI cases cover
battery source, edge bounds, anchor bound, tau, each stream integral, empty input
and a missing receipt. Missing redundant φ is recomputed from its definition K/B.
Native cadence uses positive intervals; duplicates are counted without removing
polls or voiding variance. Different rail sets now have an explicit physical
reason on rails/rest only; DC/GPU are unaffected. No-knee sizes, φ, contrasts,
coefficients, residuals, sensitivities, share and GPU arm-power contrast use
`not defined (knee not found)`. Upper limits share the H2 interval's decimal
place; zero-width intervals use fixed two-decimal formatting.

Before: a duplicate vetoed DC validity, a rail-set mismatch remained RESOLVED,
no-knee descriptions had unrelated reasons, and 0.000996 printed an extra
upper-limit digit; zero width exposed float repr. After: the corresponding
production-shaped CLI regressions pass. Actual stream scan receipts are written,
reloaded and processed by the real scan CLI; its worked/no-knee outputs feed
the eight real production-sized fake-array stream calls and fresh read CLI
processes for the requested variants. The isolated-late-pair regression retains
all 21 pairs and candidate 256 MiB, then refuses the cache-arm checks rather
than shrinking K. Focused suite: 43 tests passed; the subsequent K/B missing-φ
regression also passed. No new numeric acceptance bar was introduced.

Step 3 — S1. Fixed scan/read invocations in `scripts/bytes_mac_kit.py`'s README
string and the rule to start with `/opt/homebrew/bin/python3.13`; expanded the
kit verification invocation likewise. Regenerated exclusively through the kit
generator. Generated files changed: `configs/campaigns/bytes_mac_check/README.md`
and `configs/campaigns/bytes_mac_check/plan_tree.json`. The latter's generator
SHA256 is `7a11cd67331bfcfb928524833eedbf0b560938d21b3e9b89fc38e90820efb69e`,
matching the generator bytes. An explicit pre-write check confirmed every
out-of-scope generated product was already identical, including smoke_keep.
F7's five 8B-8bit model revisions remain as regeneration writes them; none
changed this round. Before: Sol's bare scan/read commands exit 126. After:
instructions have the absolute interpreter, generator/README bytes agree,
`--check` passes, and both touched modules pass all 44 tests. This Linux seat
uses `/usr/bin/python3.13` (3.13.5); the Mac path is verified as instruction text,
with the same scan/read entrypoints executed under the available Python 3.13.

Step 4 — final verification. Implementation steps were committed and pushed
separately: `476a3aaf4`, `c99f11ef5`, `9cfaddf05`. Final focused command:
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3.13 -B -m unittest tests.test_bytes_stream_test tests.test_bytes_mac_kit`
— 44 tests, OK (86.777 s). Generator `--check`, README byte equality and the
whole-round `git diff --check` pass; all eight changed files are in WRITE_SCOPE.
The full repository suite was not run: this bounded standalone non-claim tooling
round uses the two requested modules and independent reviewer replays.
The supplied full e2e script was rerun after the fixes, with explicit synthetic
clock metadata added to its legacy scan inputs. Its real stream receipts and
read CLI retain DC 0.1929 ± 0.0025 J/GB and share 0.3458 ± 0.0075; all independent
energy differences remain inside the existing 5.7e-6 J/GB bar. The candidate-check
script also reran: its obsolete source substitution is a no-op on the final
rule, and its original seeded cases now exercise that rule. Scratch evidence is
under `/tmp/kb-round4`, outside both repositories.

PR #593 is open and draft. Read starting-head CI run
[40759901627](https://github.com/mpmdw/JouleWise/actions/runs/40759901627):
fences and quick/shard 1 fail on four stale external-manifest pins in the kit
plan; shard 8 reports 21 `bytes_h_session` errors for a missing external-input
lookup key. These are CI merge-tree findings; no out-of-scope repair was made
(`scripts/bytes_h_session.py` is outside WRITE_SCOPE). Build, installed-wheel
and calibration jobs passed in that snapshot. At final implementation head
`9cfaddf05`, CI run
[40769688587](https://github.com/mpmdw/JouleWise/actions/runs/40769688587)
is pending; gate-ledger 40769688468 is skipped. No claim of final-head CI green.

Decisions I made: apply the consult exactly; use recorded getres alone on
non-macOS where mach timebase is explicitly not applicable; retain unknown
integer conversion unless sourced; preserve all duplicate polls and partial
results; recompute φ from K/B; use two fixed decimals for zero-width intervals;
keep the existing generated F7 revisions. None changes a rule-defined data
choice or adds an acceptance tolerance. No scope expansion, approval rejection,
hardware measurement, unblinding, admission or merge occurred. All execution
evidence is synthetic. NEEDS_RULING: none.


## Round 5 (fix round)

### Initial G3 stop (historical; resolved by R-G3 below)

Activation bde918c1; synthetic-only Python 3.13, no bytecode. Read both Sol-3 and
Opus-2 reports and their scripts at the requested refs. Status: **BLOCKED by G3**.

G3 census: `python3.13 -B scripts/repin.py --write registry` changed only the
registry. Kind-P literals: **32,556 → 33,297**. `repin.py --check` prints
`PASS 16 pin families current`; kit `--check` also passes without regeneration.
Registry-only commit `2153f1333` was pushed prematurely: I incorrectly checked
row ownership against the merge base with main. The corrected comparison with
PR #593's base `e624d67c7` identifies the 27 exception files below. G3 requires
stopping on these exceptions. No further implementation commits were made.
The individual added/removed registry rows are enumerated in the next section.
Besides 741 new rows, six existing sizing rows (`bytes-s1-p1` through
`bytes-s6-p1`, `/source/code_sha256/joulewise~1b6~1precheck.py`) lose their
`file:joulewise/b6/precheck.py` target and instead have a null target.

| Exception file | Changed row locations |
|---|---|
| `configs/b6/packs/bytes-s1-p1/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s1-p2/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s2-p1/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s2-p2/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s3-p1/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s3-p2/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s4-p1/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s4-p2/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s5-p1/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s5-p2/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s6-p1/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/packs/bytes-s6-p2/registration.json` | `/flag_catalog_sha256` |
| `configs/b6/registration/identity_pins.json` | `358 pointers; exact inventory below` |
| `configs/b6/registration/sizing_b5.json` | `6 pointers; exact inventory below` |
| `configs/bytes/identity_pins.json` | `359 pointers; exact inventory below` |
| `configs/campaigns/bytes-s1-p1/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s1-p2/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s2-p1/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s2-p2/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s3-p1/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s3-p2/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s4-p1/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s4-p2/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s5-p1/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s5-p2/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s6-p1/plan_tree.sha256` | `#L1` |
| `configs/campaigns/bytes-s6-p2/plan_tree.sha256` | `#L1` |

Uncommitted authorized fixes are preserved in the worktree: G1's single
schema-driven input accessor, reasoned prerequisite failures and finite/exact
edge validation; G2's independent arm reductions; G4's exact manifest-ID lookup;
and G5's reference snapshots, negative-place upper-limit rounding and missing
GPU-source rule in §§2/4. The generated real-stream/disk/CLI test walks one full
call's consumed leaves with five mutations each, checks complete output and
leaf-naming UNDETERMINED reasons, and forbids smaller surviving aggregate,
per-call or gap bounds. Separate tests cover every lost-call position, null
containers, scan inputs and both sides of the rail-set comparison.

Before/after repros: Sol's null/edge cases originally raised or narrowed bounds;
they now exit 0 and retain records and complete-arm summaries. Opus's complete
matrix reproduced the original five tracebacks, negative gap charge, stale
reference snapshot and 157 upper limit; its replay reports zero reader
tracebacks, reasoned undefined bounds, matching snapshots and upper limit 160.
Only its display inspector was adapted to tolerate correctly absent bound keys;
its scenarios and arithmetic were unchanged. The final malformed-gap replay
prints `bound_j: null`, never zero. Valid worked values remain rails
0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024 J/GB.
The baseline session/repin run had 21 errors and one failure.

Verification at handoff: `tests.test_bytes_stream_test`, `tests.test_bytes_mac_kit`
and `tests.test_repin`: **86 tests, OK** (1292.761 s), including **945 real read CLI
leaf faults**. Whole `tests.test_bytes_h_session`: **36 tests, OK** (1799.185 s).
Supplemental no-knee, container/scan and production-shaped tests also pass.
Kit `--check`, final `repin.py --check` and `git diff --check` pass. The whole
repository suite was not run; this bounded round ran the requested modules.
All test results describe the worktree. Final-head CI is reported separately
after the report push; no green claim is made. The uncommitted fixes are not
present in that pushed head.

Decisions I made: reject an invalid native collection as a prerequisite, rather
than drop a row; retain signed measured powers/integrals while requiring physical
counts, durations, systematic bounds and adapter ratings to have their governed
sign; preserve ordinary no-knee and absent-description wording; check GPU source
on the registered-versus-harvested comparison; use compact native support only
in the exhaustive synthetic fault test. No new agreement bar: 4.5e-7 GB/s and
5.7e-6 J/GB remain unchanged. No hardware collection, admission or merge.

Required next decision: authorize retaining the census's exception rows, or
authorize reverting `2153f1333` in a new commit. The G3 instruction is the reason
for this stop; elapsed time is not authorization. Implementation commits and
pushes remain blocked pending that answer.


### Outcome after lead ruling R-G3

R-G3 resolves the stop. **Completed and pushed** the preserved G1, G2, G4 and
G5 fixes and the narrow G3 repair. No ruling remains pending.

Commit sequence (each pushed separately):

- `013a8e99d`: `git revert --no-edit 2153f1333`, restoring the pre-census registry
  in a new history-preserving commit.
- `0c513a7c3`: rebuild only the four authorized registry rows.
- `d2ead5f2b`: G1/G2/G5 reader, rule and regression tests.
- `70e085230`: G4 template roles keyed and looked up by existing `manifest_id`.

The one-off repair calls `scripts.repin.census`'s `literals_in`, `build_index`,
`_best_target`, `classify` and `render`, using the same literal-to-target-to-family
indexed row construction as the census writer. It reads current targets from
the kit plan and reuses their existing target indices; no JSON was hand-edited
and no full census was retained. The four target bindings are:

| Pointer in `configs/campaigns/bytes_mac_check/plan_tree.json` | Current target |
|---|---|
| `/stage_graph/2/input/sha256` | `configs/campaigns/bytes-s1-p1/members/bytes-s1-p1-bound-collection/order_manifest.json` |
| `/stage_graph/4/input/sha256` | `configs/campaigns/bytes-s1-p1/members/bytes-s1-p1-reference-start/order_manifest.json` |
| `/stage_graph/18/input/sha256` | `configs/campaigns/bytes-s1-p1/members/bytes-s1-p1-reference-midpoint/order_manifest.json` |
| `/stage_graph/24/input/sha256` | `configs/campaigns/bytes-s1-p1/members/bytes-s1-p1-reference-end/order_manifest.json` |

Proof: both against the reverted registry and against `977a5d2df`, the registry
diff contains **exactly four removed and four added row lines**. Assertions
verified the four pointers, unchanged row families, zero stale rows, and equality
of every other row, target, metadata field and summary. Kind-P remains
**32,556 → 32,556** for this narrow repair. The six sizing `precheck.py` target
bindings are preserved, and the 741 other-lane literals remain unregistered.
The exception inventory below records the rejected census only; none of its
exception-row changes remains in the final registry.

After the narrow repair, `python3.13 -B scripts/repin.py --check` prints
**PASS 16 pin families current** and `python3.13 -B -m unittest tests.test_repin`
passes **37 tests in 13.723 s**. The unchanged preserved implementation already
passed all **122 requested local tests**: reader/kit/repin 86 (including 945
real-CLI leaf mutations), plus the whole session module's 36 tests. No source
edits were made between those passing checks and the implementation commits.
Kit verification required no regeneration. Final diff and scope checks pass.
All execution remains synthetic-only under Python 3.13 with bytecode disabled;
no acceptance bars changed and no out-of-scope file was edited.

PR #593 remains draft. Its exact final head and every available CI job state
are read after this report is pushed and reported in the final handoff. A pending
run or missing jobs is not a green result.

## Round 5 registry exception row inventory

Exact semantic census delta versus `977a5d2df`, restricted to files unchanged
since PR base `e624d67c7`. Target indices are resolved to target identities.

### `configs/b6/packs/bytes-s1-p1/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s1-p2/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s2-p1/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s2-p2/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s3-p1/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s3-p2/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s4-p1/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s4-p2/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s5-p1/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s5-p2/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s6-p1/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/packs/bytes-s6-p2/registration.json`

Added:

- `/flag_catalog_sha256` — `sealed_registration` — `file:configs/b6/flag_catalog_b6.json`

### `configs/b6/registration/identity_pins.json`

Added:

- `/bytes_c4/issuer/sha256` — `issued_config` — `file:scripts/write_b5_identity_pins.py`
- `/bytes_c4/runtime_observation_source/sha256` — `issued_config` — `file:docs/process_traces/2026-10-23-magistrate-786c0858/RUNTIME-OBSERVE.txt`
- `/bytes_c4/stack_evidence/llama-70b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/10/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/10/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/11/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/11/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/12/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/12/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/13/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/13/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/14/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/14/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/15/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/15/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/16/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/16/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/17/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/17/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/18/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/18/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/19/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/19/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/20/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/20/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/21/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/21/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/22/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/22/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/23/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/23/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/24/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/24/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/25/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/25/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/26/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/26/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/27/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/27/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/28/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/28/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/29/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/29/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/30/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/30/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/31/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/31/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/32/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/32/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/33/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/33/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/5/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/5/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/6/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/6/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/7/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/7/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/8/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/8/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/9/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/llama-70b/9/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/10/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/10/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/11/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/11/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/12/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/12/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/13/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/13/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/14/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/14/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/15/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/15/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/16/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/16/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/17/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/17/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/18/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/18/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/19/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/19/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/20/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/20/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/21/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/21/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/22/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/22/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/23/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/23/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/24/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/24/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/25/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/25/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/26/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/26/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/27/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/27/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/28/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/28/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/29/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/29/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/30/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/30/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/31/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/31/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/32/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/32/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/33/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/33/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/34/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/34/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/35/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/35/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/36/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/36/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/37/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/37/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/38/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/38/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/39/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/39/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/40/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/40/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/41/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/41/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/42/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/42/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/43/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/43/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/44/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/44/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/45/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/45/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/46/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/46/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/47/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/47/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/48/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/48/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/49/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/49/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/5/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/5/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/50/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/50/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/51/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/51/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/52/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/52/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/53/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/53/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/54/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/54/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/55/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/55/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/56/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/56/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/57/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/57/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/58/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/58/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/59/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/59/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/6/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/6/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/60/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/60/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/61/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/61/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/62/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/62/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/63/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/63/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/64/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/64/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/7/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/7/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/8/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/8/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/9/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/neg8_reference/9/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-14b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-1p7b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-30b-a3b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-32b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-4b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b-8bit/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-8b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/10/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/10/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/5/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/5/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/6/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/6/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/7/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/7/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/8/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/8/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/9/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen3-next-80b/9/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/0/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/1/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/10/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/10/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/11/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/11/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/12/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/12/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/13/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/13/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/14/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/14/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/15/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/15/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/16/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/16/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/17/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/17/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/18/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/18/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/19/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/19/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/2/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/20/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/20/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/21/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/21/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/22/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/22/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/3/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/4/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/5/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/5/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/6/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/6/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/7/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/7/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/8/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/8/runtime_identity_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/9/metadata_sha256` — `issued_config` — `None`
- `/bytes_c4/stack_evidence/qwen35-122b/9/runtime_identity_sha256` — `issued_config` — `None`
- `/units/llama-70b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/llama-70b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-14b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-14b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-1p7b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-1p7b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-30b-a3b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-30b-a3b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-32b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-32b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-4b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-4b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-8b-8bit/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-8b-8bit/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-8b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-8b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-next-80b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-next-80b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen35-122b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen35-122b/stack_identity/model_artifact_sha256` — `issued_config` — `None`

### `configs/b6/registration/sizing_b5.json`

Removed:

- `/packs/bytes-s1-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `file:joulewise/b6/precheck.py`
- `/packs/bytes-s2-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `file:joulewise/b6/precheck.py`
- `/packs/bytes-s3-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `file:joulewise/b6/precheck.py`
- `/packs/bytes-s4-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `file:joulewise/b6/precheck.py`
- `/packs/bytes-s5-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `file:joulewise/b6/precheck.py`
- `/packs/bytes-s6-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `file:joulewise/b6/precheck.py`

Added:

- `/packs/bytes-s1-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `None`
- `/packs/bytes-s2-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `None`
- `/packs/bytes-s3-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `None`
- `/packs/bytes-s4-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `None`
- `/packs/bytes-s5-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `None`
- `/packs/bytes-s6-p1/source/code_sha256/joulewise~1b6~1precheck.py` — `issued_config` — `None`

### `configs/bytes/identity_pins.json`

Added:

- `/derivation/stack_issuer/sha256` — `issued_config` — `file:scripts/write_b5_identity_pins.py`
- `/stack_evidence/llama-70b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/10/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/10/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/11/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/11/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/12/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/12/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/13/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/13/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/14/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/14/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/15/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/15/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/16/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/16/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/17/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/17/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/18/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/18/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/19/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/19/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/20/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/20/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/21/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/21/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/22/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/22/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/23/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/23/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/24/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/24/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/25/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/25/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/26/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/26/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/27/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/27/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/28/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/28/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/29/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/29/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/30/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/30/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/31/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/31/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/32/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/32/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/33/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/33/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/5/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/5/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/6/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/6/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/7/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/7/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/8/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/8/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/9/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/llama-70b/9/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/10/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/10/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/11/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/11/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/12/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/12/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/13/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/13/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/14/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/14/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/15/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/15/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/16/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/16/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/17/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/17/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/18/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/18/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/19/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/19/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/20/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/20/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/21/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/21/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/22/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/22/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/23/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/23/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/24/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/24/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/25/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/25/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/26/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/26/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/27/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/27/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/28/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/28/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/29/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/29/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/30/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/30/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/31/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/31/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/32/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/32/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/33/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/33/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/34/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/34/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/35/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/35/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/36/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/36/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/37/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/37/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/38/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/38/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/39/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/39/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/40/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/40/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/41/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/41/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/42/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/42/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/43/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/43/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/44/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/44/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/45/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/45/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/46/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/46/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/47/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/47/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/48/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/48/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/49/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/49/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/5/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/5/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/50/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/50/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/51/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/51/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/52/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/52/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/53/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/53/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/54/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/54/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/55/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/55/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/56/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/56/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/57/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/57/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/58/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/58/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/59/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/59/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/6/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/6/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/60/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/60/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/61/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/61/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/62/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/62/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/63/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/63/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/64/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/64/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/7/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/7/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/8/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/8/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/9/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/neg8_reference/9/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-14b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-1p7b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-30b-a3b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-32b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-4b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b-8bit/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-8b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/10/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/10/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/5/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/5/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/6/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/6/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/7/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/7/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/8/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/8/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/9/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen3-next-80b/9/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/0/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/0/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/1/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/1/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/10/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/10/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/11/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/11/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/12/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/12/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/13/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/13/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/14/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/14/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/15/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/15/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/16/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/16/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/17/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/17/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/18/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/18/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/19/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/19/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/2/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/2/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/20/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/20/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/21/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/21/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/22/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/22/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/3/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/3/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/4/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/4/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/5/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/5/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/6/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/6/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/7/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/7/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/8/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/8/runtime_identity_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/9/metadata_sha256` — `issued_config` — `None`
- `/stack_evidence/qwen35-122b/9/runtime_identity_sha256` — `issued_config` — `None`
- `/units/llama-70b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/llama-70b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/neg8_reference/runtime_identity_sha256` — `issued_config` — `None`
- `/units/neg8_reference/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-14b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-14b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-1p7b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-1p7b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-30b-a3b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-30b-a3b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-32b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-32b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-4b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-4b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-8b-8bit/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-8b-8bit/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-8b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-8b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen3-next-80b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen3-next-80b/stack_identity/model_artifact_sha256` — `issued_config` — `None`
- `/units/qwen35-122b/runtime_identity_sha256` — `issued_config` — `None`
- `/units/qwen35-122b/stack_identity/model_artifact_sha256` — `issued_config` — `None`

### `configs/campaigns/bytes-s1-p1/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s1-p1/plan_tree.json`

### `configs/campaigns/bytes-s1-p2/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s1-p2/plan_tree.json`

### `configs/campaigns/bytes-s2-p1/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s2-p1/plan_tree.json`

### `configs/campaigns/bytes-s2-p2/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s2-p2/plan_tree.json`

### `configs/campaigns/bytes-s3-p1/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s3-p1/plan_tree.json`

### `configs/campaigns/bytes-s3-p2/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s3-p2/plan_tree.json`

### `configs/campaigns/bytes-s4-p1/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s4-p1/plan_tree.json`

### `configs/campaigns/bytes-s4-p2/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s4-p2/plan_tree.json`

### `configs/campaigns/bytes-s5-p1/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s5-p1/plan_tree.json`

### `configs/campaigns/bytes-s5-p2/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s5-p2/plan_tree.json`

### `configs/campaigns/bytes-s6-p1/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s6-p1/plan_tree.json`

### `configs/campaigns/bytes-s6-p2/plan_tree.sha256`

Added:

- `#L1` — `pack_config_bytes` — `file:configs/campaigns/bytes-s6-p2/plan_tree.json`

## Round 6 (fix round)

Activation `1cc172c8`, 2026-10-29. Continued `codex/2026-10-28-kb-v2` from `6847502b8`; read the Sol review at `fb477524d` and Opus review at `7d5065f`. Implementation commits, each pushed: `93de6cdab`, `78daeb3ad`, `dfbba204d`.

H1–H8 are implemented. G1 rejects numbers outside finite binary64, validates receipt/native time order and fixed signs, validates scan status, and handles stack leaves separately. Invalid rows remain in `input_records`; their collections do not supply a recomputed smaller bound. Idle overflow, including a non-finite power-duration product, produces a reasoned UNDETERMINED result. Complete prerequisite arms retain their central coefficients when another arm is lost; residuals and uncertainties remain reasoned `not defined`. Disclosure-only failures print `not recorded` without charging a class or discarding a valid rail set. The identity-source test injects only the stream sleep and leaves subprocess sleep alone.

Verification used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, and `PYTHONDONTWRITEBYTECODE=1`:

- `tests.test_bytes_stream_test` plus `tests.test_bytes_mac_kit`: **50 tests, OK**, 1,979.938 s; 892 generated CLI faults in that run. This is 1.37× the review's Round 5 combined-module time of 1,450.139 s, under the requested approximate 1.5× budget despite concurrent verification.
- `tests.test_bytes_h_session` plus `tests.test_repin`: **73 tests, OK**, 2,139.197 s.
- Final generated test: **900 real CLI faults, OK**, 1,279.431 s, including huge integers, interval/native-row order, scan status, fixed signs and disclosure-only class retention. Final arithmetic module: **6 tests, OK**.
- Sol `extra.py` and `partial.py` were replayed before and after: the two tracebacks disappear, bad scan status is reasoned, and lost C3 retains `gamma_c`, `alpha`, `gamma_d` and Delta. The four named Opus disclosure leaves were independently replayed before/after; final classes remain RESOLVED with leaf-naming disclosures. Opus `probes.py` cases finish without reader tracebacks on the valid nonnegative fixture; only its obsolete numeric-bound display lookup was adapted.
- Independent Opus walk: **44,816 cases before and after**. Before: 980 crashes; after: **0 crashes, 0 lost calls**, with 450/463 sampled CLI reads respectively exiting 0. The walk process predated the final battery-list follow-up: all **36** affected zero-stamp cases were replayed on the final source, with matching CLI classes, DC UNDETERMINED and no smaller bound; this reconciles its three old-process/new-CLI mismatches. No huge-integer, invalid native-zero-stamp or fixed-sign-negative case shrank a surviving bound. The raw 176 remaining shrink flags are valid zero/signed-measurement changes, changed row/gap collections or record-deletion index comparisons, not these malformed prerequisites.
- `repin.py --check`: **PASS 16 pin families current**. Kit freshness: **verified non-claim Mac kit**. No regeneration or pinned-digest changes were required. `git diff --check` passes.

Worked output from the final committed reader is unchanged: **rails 0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024 J/GB; share 0.3458 ± 0.0075**. The **4.5e-7 GB/s** rational-check and **5.7e-6 J/GB** energy bars are unchanged; no new agreement bar was added.

Decisions I made:

- Keep duplicate poll stamps valid, reject reversed order and zero stamps that break the receipt/native order, and preserve valid flanking support rows. Apply the accessor to the separate native battery poll list as well as idle collections.
- Keep battery power and battery edge energy signed, while enforcing the signs H6 fixes. Preserve unconsumed stack metadata alongside the validated leaves.
- Thin generated idle support from six 9.6 s rows to four 14.4 s rows, still covering 57.6 s and at least three bandwidths; walk every retained leaf. Final fault count is 900 versus Round 5's 945.
- Repair negative-power synthetic fixtures with sparse positive pulses, retaining their means and governed standard errors. The original Opus fixture is still replayed literally and correctly refuses under H6; its nonnegative equivalent supplies the worked-value and physical-order checks. This changes no valid-input estimator or publication number.

No NEEDS_RULING or scope expansion. All repository writes stay within the supplied allowlist. No hardware measurement, admission or merge. Final-head CI is read after pushing this report, and every job's observed state is included in the handoff; this section makes no advance green claim.
## Round 7 (fix round)

Activation `1cc172c8`, 2026-10-29. Continued `codex/2026-10-28-kb-v2` from `840137268`; used Sol review `471bbc79b` on `codex/2026-10-29-kb-v2-rev-sol-5`. Implementation/test commits pushed: `5252e4e91`, `1cbf35c30`, `ad0ec9340`, `4dad3f7df`, `2e3b1ed31`, `32e91f9bd`. Did not wait for the parallel Opus review.

J1–J3 are implemented. One executable dependency table governs every arm's x/dx, coefficients, residual, propagated half-width and upper-limit prerequisites. Failed native support makes that arm's x/dx, the residual and dependent widths reasoned `not defined`; complete-arm coefficients remain available. The rule now states the all-arm native-support dependency explicitly. Round 6's classification of all 176 shrink flags as benign was incorrect: the four deficient C3-support cases are fixed here.

Arithmetic guards cover trim rounding, native aggregation, gaps, per-call calculations, reducer quantities, class/upper-limit ratios and print conversions. Failures retain all calls/evidence and name input leaves. Reducer arithmetic reasons survive common DC classification. A regression also checks an overflowing intermediate attribution ratio whose later upper limit would otherwise be finite.

Verification used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`:

- Reader/kit: **50 tests, OK, 1,113.923 s; 1,048 generated real-CLI faults**. This is **0.56×** Round 6's reported 1,979.938 s, within the approximate 1.5× budget.
- Session/repin: **73 tests, OK, 1,409.429 s**. All **123 requested tests pass**. The final class/epsilon follow-up additionally passed **7 focused tests, 18.349 s**.
- Both supplied scripts ran before and after the fixes, with a final-source replay. Before: short C3 support retained/shrank numeric widths; finite float/int tau overflow exited 1. After: all six short-support scenarios retain eight calls and remove dependent numeric widths; both extreme tau variants exit 0. Thinned, full-cadence and jittered fixtures were exercised.
- The generated test adds **128** deficient native-support collections across all eight calls, both spans, all four native families and lengths one/zero; **16** extreme tau/settle cases; and **4** aggregate-overflow cases. It checks class reasons, absent dependent widths, unchanged complete-arm coefficients, retained evidence and no smaller surviving width. Another **13** finite-arithmetic probes passed across integrals, idle powers, edge bounds and gaps.
- `repin.py --check`: **PASS 16 pin families current**. `git diff --check` passes. The four requested modules plus focused checks cover this bounded standalone tooling change; the whole repository suite was not run.

Worked output is unchanged: **rails 0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024 J/GB; share 0.3458 ± 0.0075**. The **4.5e-7 GB/s** and **5.7e-6 J/GB** agreement bars are unchanged; no new acceptance bar was added.

Decisions I made:

- Apply J1's residual support gate to all four arms, including S; preserve coefficients whose own arms remain complete.
- Test the consumed `receipt.settle_s` leaf. At `1e308`, its subtraction safely yields zero trim and unchanged output; do not invent an arithmetic failure.
- Keep all existing generated repetitions and four-row native support. Discover the unchanged registered stack once per read instead of eight times; no further thinning was needed.
- Run review scripts in a temporary mirror because they write evidence; preserve the review branch's evidence and the repository allowlist.

No NEEDS_RULING or scope expansion. Only the four authorized files changed. No hardware measurement, admission or merge. Final-head CI is read after pushing this section; every observed job state is reported separately in the final handoff, without an advance green claim.

## Round 8 replay transcripts

Complete output of the supplied scripts (trailing whitespace trimmed); before is an immutable archive of `156f03110`, after uses the final reader. Fixtures were generated with the review's unchanged `run_with_clock.py` compatibility shim and `e2e_nonneg.py`.

### baseline-probes

```text
baseline {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)}
[tau_s_1e300_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
    gpu: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
    dc: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
    rest: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
[settle_s_1e300_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[gap_fsum_overflow_rec3] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
    gpu: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
    dc: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
    rest: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
[anchor_shift_1e308_all] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.idle.pre.rails.power_w, records[0].harvest.idle.post.rails.power_w, records[0].harvest.anch
    gpu: S bound/N from records[0].harvest.energy_j.gpu, records[0].harvest.idle.pre.gpu.power_w, records[0].harvest.idle.post.gpu.power_w, records[0].harvest.anchor_shi
    rest: S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.energy_j.meter, records[0].harvest.energy_j.battery, records[0].harvest.idle.pre.rails.powe
[meter_edge_1e308_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    gpu: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    dc: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    rest: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
[r_max_1e308_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    gpu: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    dc: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    rest: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
[energy_rails_1e308_rec0] rc=0 calls=8 {'rails': ('NOT RESOLVED', 5.146164472158233e+302), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('NOT RESOLVED', 5.146164472158233e+302)} shrunk=[]
    rails:
    rest:
[rails_row_overlap_prev_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732413065690482), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.0024454463165376823)} shrunk=['rails']
[gpu_row_overlap_prev_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.0002858005853337753), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[rails_row0_covers_span_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.004869316027778751), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.006747554463523138)} shrunk=[]
[idle_pre_start_ns_0_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[idle_post_end_far_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[meter_row0_stamp_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
    gpu: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
    dc: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
    rest: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
[rails_row0_start_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.rails[0].start_ns invalid time order
    rest: records[1].harvest.idle.pre.rails[0].start_ns invalid time order
[battery_samples_row0_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.battery_samples[0].stamp_ns invalid time order
    gpu: records[1].harvest.battery_samples[0].stamp_ns invalid time order
    dc: records[1].harvest.battery_samples[0].stamp_ns invalid time order
    rest: records[1].harvest.battery_samples[0].stamp_ns invalid time order
[battery_idle_row0_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
    gpu: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
    dc: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
    rest: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
[meter_post_row0_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
    gpu: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
    dc: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
    rest: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
[battery_edge_neg_small_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002523995578128949), 'rest': ('RESOLVED', 0.002442377826125168)} shrunk=['dc', 'rest']
[battery_edge_neg_all_calls] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    dc: dc delta/halfwidth print arithmetic unavailable: math domain error
    rest: rest delta/halfwidth print arithmetic unavailable: math domain error
    dc halfwidth not defined (dc delta/halfwidth print arithmetic unavailable: math domain error) baseline 0.002527022733700807 printed not defined (dc delta/halfwidth print arithmetic unavailable: math domain error)
[battery_idle_power_neg_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.0038892153761101323), 'rest': ('RESOLVED', 0.003807597624106364)} shrunk=[]
[energy_battery_neg_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.017290156402910678), 'rest': ('RESOLVED', 0.0172085386509069)} shrunk=[]
[energy_gpu_neg_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('NOT RESOLVED', 0.02404943315698854), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    gpu:
[energy_meter_neg_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 0.14455694011577663), 'rest': ('UNDETERMINED', 0.14447532236377283)} shrunk=[]
    rails: contrast not resolved
    gpu: contrast not resolved
    dc: contrast not resolved
    rest: contrast not resolved
[meter_edge_neg_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
    gpu: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
    dc: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
    rest: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
[gpu_power_zero_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.0003125907889370728), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[disclosure_python=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['python']
[disclosure_python=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['python']
[disclosure_python=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['python']
[disclosure_numpy=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['packages.numpy']
[disclosure_numpy=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['packages.numpy']
[disclosure_numpy=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['packages.numpy']
[disclosure_kernel_library=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['kernel_library']
[disclosure_kernel_library=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['kernel_library']
[disclosure_kernel_library=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['kernel_library']
[disclosure_telemetry_backend=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['telemetry_backend']
[disclosure_telemetry_backend=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['telemetry_backend']
[disclosure_telemetry_backend=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['telemetry_backend']
[stack_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.os_version missing or invalid
    gpu: records[2].receipt.stack.os_version missing or invalid
    dc: records[2].receipt.stack.os_version missing or invalid
    rest: records[2].receipt.stack.os_version missing or invalid
[hardware_unit_str_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.hardware_unit.machine missing or invalid
    gpu: records[2].receipt.stack.hardware_unit.machine missing or invalid
    dc: records[2].receipt.stack.hardware_unit.machine missing or invalid
    rest: records[2].receipt.stack.hardware_unit.machine missing or invalid
[packages_mlx_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.packages.mlx missing or invalid
    gpu: records[2].receipt.stack.packages.mlx missing or invalid
    dc: records[2].receipt.stack.packages.mlx missing or invalid
    rest: records[2].receipt.stack.packages.mlx missing or invalid
[runtime_version_name_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.runtime_version.name missing or invalid
    gpu: records[2].receipt.stack.runtime_version.name missing or invalid
    dc: records[2].receipt.stack.runtime_version.name missing or invalid
    rest: records[2].receipt.stack.runtime_version.name missing or invalid
[capture_stack_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: measured rails boundary missing (measurement_boundary_label.rails)
    gpu: records[2].harvest.capture_stack.measurement_boundary_label.rails missing or invalid
    rest: measured rails boundary missing (measurement_boundary_label.rails)
[mbl_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: measured rails boundary missing (measurement_boundary_label.rails)
    gpu: records[2].harvest.capture_stack.measurement_boundary_label.rails missing or invalid
    rest: measured rails boundary missing (measurement_boundary_label.rails)
[rails_label_elem_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: measured rails boundary missing (measurement_boundary_label.rails)
    gpu: records[2].harvest.capture_stack.measurement_boundary_label.rails[1] missing or invalid
    rest: measured rails boundary missing (measurement_boundary_label.rails)
[scan_status_null] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_7] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_list] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_absent] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_knee_not_found_with_K] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[scan_refused_K_null] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: knee not found
    gpu: knee not found
    dc: knee not found
    rest: knee not found
[scan_status_null_K_null] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_B_equals_K] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records must be the complete stamped palindrome
    gpu: records must be the complete stamped palindrome
    dc: records must be the complete stamped palindrome
    rest: records must be the complete stamped palindrome
[scan_Bc1_equals_Bc2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records must be the complete stamped palindrome
    gpu: records must be the complete stamped palindrome
    dc: records must be the complete stamped palindrome
    rest: records must be the complete stamped palindrome
```

### baseline-overflow

```text
tau_s_1e300 OK {'rails': ('UNDETERMINED', 'not defined (two complete arm calls missing)'), 'gpu': ('UNDETERMINED', 'not defined (two complete arm calls missing)'), 'dc': ('UNDETERMINED', 'not defined (two complete arm calls missing)'), 'rest': ('UNDETERMINED', 'not defined (two complete arm calls missing)')}
gap_fsum OK {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum)'), 'rest': ('UNDETERMINED', 'not defined (records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum)')}
anchor_1e308_all OK {'rails': ('UNDETERMINED', 'not defined (S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.idle.pre.rails.power_w, records[0].harvest.idle.post.rails.power_w, records[0].harvest.anchor_shift_j, records[0].harvest.r_max_s, records[0].harvest.meter_edge_w, records[0].harvest.battery_edge_j, records[0].harvest.meter_gaps, records[7].harvest.energy_j.rails, records[7].harvest.idle.pre.rails.power_w, records[7].harvest.idle.post.rails.power_w, records[7].harvest.anchor_shift_j, records[7].harvest.r_max_s, records[7].harvest.meter_edge_w, records[7].harvest.battery_edge_j, records[7].harvest.meter_gaps, records[0].receipt.repeats, records[7].receipt.repeats arithmetic unavailable: non-finite arithmetic)'), 'gpu': ('UNDETERMINED', 'not defined (S bound/N from records[0].harvest.energy_j.gpu, records[0].harvest.idle.pre.gpu.power_w, records[0].harvest.idle.post.gpu.power_w, records[0].harvest.anchor_shift_j, records[0].harvest.r_max_s, records[0].harvest.meter_edge_w, records[0].harvest.battery_edge_j, records[0].harvest.meter_gaps, records[7].harvest.energy_j.gpu, records[7].harvest.idle.pre.gpu.power_w, records[7].harvest.idle.post.gpu.power_w, records[7].harvest.anchor_shift_j, records[7].harvest.r_max_s, records[7].harvest.meter_edge_w, records[7].harvest.battery_edge_j, records[7].harvest.meter_gaps, records[0].receipt.repeats, records[7].receipt.repeats arithmetic unavailable: non-finite arithmetic)'), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', 'not defined (S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.energy_j.meter, records[0].harvest.energy_j.battery, records[0].harvest.idle.pre.rails.power_w, records[0].harvest.idle.pre.meter.power_w, records[0].harvest.idle.pre.battery.power_w, records[0].harvest.idle.post.rails.power_w, records[0].harvest.idle.post.meter.power_w, records[0].harvest.idle.post.battery.power_w, records[0].harvest.anchor_shift_j, records[0].harvest.r_max_s, records[0].harvest.meter_edge_w, records[0].harvest.battery_edge_j, records[0].harvest.meter_gaps, records[7].harvest.energy_j.rails, records[7].harvest.energy_j.meter, records[7].harvest.energy_j.battery, records[7].harvest.idle.pre.rails.power_w, records[7].harvest.idle.pre.meter.power_w, records[7].harvest.idle.pre.battery.power_w, records[7].harvest.idle.post.rails.power_w, records[7].harvest.idle.post.meter.power_w, records[7].harvest.idle.post.battery.power_w, records[7].harvest.anchor_shift_j, records[7].harvest.r_max_s, records[7].harvest.meter_edge_w, records[7].harvest.battery_edge_j, records[7].harvest.meter_gaps, records[0].receipt.repeats, records[7].receipt.repeats arithmetic unavailable: non-finite arithmetic)')}
anchor_1e308_one OK {'rails': ('NOT RESOLVED', 3.0271555718577845e+302), 'gpu': ('NOT RESOLVED', 3.0271555718577845e+302), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('NOT RESOLVED', 3.0271555718577845e+302)}
battery_edge_all_-1.0 OK {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.0024378264195100137), 'rest': ('RESOLVED', 0.002356208667506232)}
battery_edge_all_-10.0 OK {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.0016350595917928672), 'rest': ('RESOLVED', 0.001553441839789086)}
battery_edge_all_-20.0 OK {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.0007430964498849271), 'rest': ('RESOLVED', 0.0006614786978811458)}
battery_edge_all_-40.0 OK {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (dc delta/halfwidth print arithmetic unavailable: math domain error)'), 'rest': ('UNDETERMINED', 'not defined (rest delta/halfwidth print arithmetic unavailable: math domain error)')}
battery_edge_rec0_-1e6 OK {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (dc delta/halfwidth print arithmetic unavailable: math domain error)'), 'rest': ('UNDETERMINED', 'not defined (rest delta/halfwidth print arithmetic unavailable: math domain error)')}
```

### after-probes

```text
baseline {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)}
[tau_s_1e300_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
    gpu: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
    dc: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
    rest: call prerequisite missing in call 1: records[0].harvest.tau_s / records[0].receipt.settle_s arithmetic unavailable: cannot convert float infinity to integer
[settle_s_1e300_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[gap_fsum_overflow_rec3] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
    gpu: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
    dc: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
    rest: records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum
[anchor_shift_1e308_all] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.idle.pre.rails.power_w, records[0].harvest.idle.post.rails.power_w, records[0].harvest.anch
    gpu: S bound/N from records[0].harvest.energy_j.gpu, records[0].harvest.idle.pre.gpu.power_w, records[0].harvest.idle.post.gpu.power_w, records[0].harvest.anchor_shi
    rest: S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.energy_j.meter, records[0].harvest.energy_j.battery, records[0].harvest.idle.pre.rails.powe
[meter_edge_1e308_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    gpu: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    dc: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    rest: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
[r_max_1e308_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    gpu: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    dc: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
    rest: records[0].harvest energy_j/idle/meter_edge_w/r_max_s/battery_edge_j/anchor_shift_j.dc arithmetic unavailable: records[0].harvest energy_j/idle/edges.dc arithme
[energy_rails_1e308_rec0] rc=0 calls=8 {'rails': ('NOT RESOLVED', 5.146164472158233e+302), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('NOT RESOLVED', 5.146164472158233e+302)} shrunk=[]
    rails:
    rest:
[rails_row_overlap_prev_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.rails[300].start_ns invalid time order
    rest: records[1].harvest.idle.pre.rails[300].start_ns invalid time order
[gpu_row_overlap_prev_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    gpu: records[1].harvest.idle.pre.gpu[300].start_ns invalid time order
[rails_row0_covers_span_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.rails[1].start_ns invalid time order
    rest: records[1].harvest.idle.pre.rails[1].start_ns invalid time order
[idle_pre_start_ns_0_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[idle_post_end_far_rec1] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[meter_row0_stamp_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
    gpu: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
    dc: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
    rest: records[1].harvest.idle.pre.meter[0].stamp_ns invalid time order
[rails_row0_start_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.rails[0].start_ns invalid time order
    rest: records[1].harvest.idle.pre.rails[0].start_ns invalid time order
[battery_samples_row0_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.battery_samples[0].stamp_ns invalid time order
    gpu: records[1].harvest.battery_samples[0].stamp_ns invalid time order
    dc: records[1].harvest.battery_samples[0].stamp_ns invalid time order
    rest: records[1].harvest.battery_samples[0].stamp_ns invalid time order
[battery_idle_row0_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
    gpu: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
    dc: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
    rest: records[1].harvest.idle.pre.battery[0].stamp_ns invalid time order
[meter_post_row0_0_rec1] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
    gpu: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
    dc: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
    rest: records[1].harvest.idle.post.meter[0].stamp_ns invalid time order
[battery_edge_neg_small_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
    gpu: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
    dc: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
    rest: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
[battery_edge_neg_all_calls] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
    gpu: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
    dc: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
    rest: records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)
    dc halfwidth not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid)) baseline 0.002527022733700807 printed 0.19294313677240393 J/GB; not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))
[battery_idle_power_neg_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.0038892153761101323), 'rest': ('RESOLVED', 0.003807597624106364)} shrunk=[]
[energy_battery_neg_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.017290156402910678), 'rest': ('RESOLVED', 0.0172085386509069)} shrunk=[]
[energy_gpu_neg_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    gpu: records[0].harvest.energy_j.gpu missing or invalid
[energy_meter_neg_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest.energy_j.meter missing or invalid
    gpu: records[0].harvest.energy_j.meter missing or invalid
    dc: records[0].harvest.energy_j.meter missing or invalid
    rest: records[0].harvest.energy_j.meter missing or invalid
[meter_edge_neg_rec0] rc=0 calls=8 {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
    gpu: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
    dc: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
    rest: records[0].harvest.meter_edge_w[0] missing or invalid (meter edge powers missing)
[gpu_power_zero_rec0] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.0003125907889370728), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
[disclosure_python=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['python']
[disclosure_python=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['python']
[disclosure_python=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['python']
[disclosure_numpy=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['packages.numpy']
[disclosure_numpy=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['packages.numpy']
[disclosure_numpy=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['packages.numpy']
[disclosure_kernel_library=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['kernel_library']
[disclosure_kernel_library=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['kernel_library']
[disclosure_kernel_library=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['kernel_library']
[disclosure_telemetry_backend=None_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['telemetry_backend']
[disclosure_telemetry_backend=7_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['telemetry_backend']
[disclosure_telemetry_backend=''_rec2] rc=0 calls=8 {'rails': ('RESOLVED', 0.0005732822806092617), 'gpu': ('RESOLVED', 0.00028575897827642216), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('RESOLVED', 0.002445404981697026)} shrunk=[]
    stack_comparison disclosure ['telemetry_backend']
[stack_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.os_version missing or invalid
    gpu: records[2].receipt.stack.os_version missing or invalid
    dc: records[2].receipt.stack.os_version missing or invalid
    rest: records[2].receipt.stack.os_version missing or invalid
[hardware_unit_str_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.hardware_unit.machine missing or invalid
    gpu: records[2].receipt.stack.hardware_unit.machine missing or invalid
    dc: records[2].receipt.stack.hardware_unit.machine missing or invalid
    rest: records[2].receipt.stack.hardware_unit.machine missing or invalid
[packages_mlx_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.packages.mlx missing or invalid
    gpu: records[2].receipt.stack.packages.mlx missing or invalid
    dc: records[2].receipt.stack.packages.mlx missing or invalid
    rest: records[2].receipt.stack.packages.mlx missing or invalid
[runtime_version_name_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records[2].receipt.stack.runtime_version.name missing or invalid
    gpu: records[2].receipt.stack.runtime_version.name missing or invalid
    dc: records[2].receipt.stack.runtime_version.name missing or invalid
    rest: records[2].receipt.stack.runtime_version.name missing or invalid
[capture_stack_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: measured rails boundary missing (measurement_boundary_label.rails)
    gpu: records[2].harvest.capture_stack.measurement_boundary_label.rails missing or invalid
    rest: measured rails boundary missing (measurement_boundary_label.rails)
[mbl_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: measured rails boundary missing (measurement_boundary_label.rails)
    gpu: records[2].harvest.capture_stack.measurement_boundary_label.rails missing or invalid
    rest: measured rails boundary missing (measurement_boundary_label.rails)
[rails_label_elem_null_rec2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: measured rails boundary missing (measurement_boundary_label.rails)
    gpu: records[2].harvest.capture_stack.measurement_boundary_label.rails[1] missing or invalid
    rest: measured rails boundary missing (measurement_boundary_label.rails)
[scan_status_null] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_7] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_list] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_absent] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_status_knee_not_found_with_K] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid (inconsistent or unknown scan status)
    gpu: scan.status missing or invalid (inconsistent or unknown scan status)
    dc: scan.status missing or invalid (inconsistent or unknown scan status)
    rest: scan.status missing or invalid (inconsistent or unknown scan status)
[scan_refused_K_null] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: knee not found
    gpu: knee not found
    dc: knee not found
    rest: knee not found
[scan_status_null_K_null] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: scan.status missing or invalid
    gpu: scan.status missing or invalid
    dc: scan.status missing or invalid
    rest: scan.status missing or invalid
[scan_B_equals_K] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records must be the complete stamped palindrome
    gpu: records must be the complete stamped palindrome
    dc: records must be the complete stamped palindrome
    rest: records must be the complete stamped palindrome
[scan_Bc1_equals_Bc2] rc=0 calls=8 {'rails': ('UNDETERMINED', None), 'gpu': ('UNDETERMINED', None), 'dc': ('UNDETERMINED', None), 'rest': ('UNDETERMINED', None)} shrunk=[]
    rails: records must be the complete stamped palindrome
    gpu: records must be the complete stamped palindrome
    dc: records must be the complete stamped palindrome
    rest: records must be the complete stamped palindrome
```

### after-overflow

```text
tau_s_1e300 OK {'rails': ('UNDETERMINED', 'not defined (two complete arm calls missing)'), 'gpu': ('UNDETERMINED', 'not defined (two complete arm calls missing)'), 'dc': ('UNDETERMINED', 'not defined (two complete arm calls missing)'), 'rest': ('UNDETERMINED', 'not defined (two complete arm calls missing)')}
gap_fsum OK {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum)'), 'rest': ('UNDETERMINED', 'not defined (records[3].harvest.meter_gaps/adapter_max_w/battery_samples.power_w arithmetic unavailable: intermediate overflow in fsum)')}
anchor_1e308_all OK {'rails': ('UNDETERMINED', 'not defined (S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.idle.pre.rails.power_w, records[0].harvest.idle.post.rails.power_w, records[0].harvest.anchor_shift_j, records[0].harvest.r_max_s, records[0].harvest.meter_edge_w, records[0].harvest.battery_edge_j, records[0].harvest.meter_gaps, records[7].harvest.energy_j.rails, records[7].harvest.idle.pre.rails.power_w, records[7].harvest.idle.post.rails.power_w, records[7].harvest.anchor_shift_j, records[7].harvest.r_max_s, records[7].harvest.meter_edge_w, records[7].harvest.battery_edge_j, records[7].harvest.meter_gaps, records[0].receipt.repeats, records[7].receipt.repeats arithmetic unavailable: non-finite arithmetic)'), 'gpu': ('UNDETERMINED', 'not defined (S bound/N from records[0].harvest.energy_j.gpu, records[0].harvest.idle.pre.gpu.power_w, records[0].harvest.idle.post.gpu.power_w, records[0].harvest.anchor_shift_j, records[0].harvest.r_max_s, records[0].harvest.meter_edge_w, records[0].harvest.battery_edge_j, records[0].harvest.meter_gaps, records[7].harvest.energy_j.gpu, records[7].harvest.idle.pre.gpu.power_w, records[7].harvest.idle.post.gpu.power_w, records[7].harvest.anchor_shift_j, records[7].harvest.r_max_s, records[7].harvest.meter_edge_w, records[7].harvest.battery_edge_j, records[7].harvest.meter_gaps, records[0].receipt.repeats, records[7].receipt.repeats arithmetic unavailable: non-finite arithmetic)'), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('UNDETERMINED', 'not defined (S bound/N from records[0].harvest.energy_j.rails, records[0].harvest.energy_j.meter, records[0].harvest.energy_j.battery, records[0].harvest.idle.pre.rails.power_w, records[0].harvest.idle.pre.meter.power_w, records[0].harvest.idle.pre.battery.power_w, records[0].harvest.idle.post.rails.power_w, records[0].harvest.idle.post.meter.power_w, records[0].harvest.idle.post.battery.power_w, records[0].harvest.anchor_shift_j, records[0].harvest.r_max_s, records[0].harvest.meter_edge_w, records[0].harvest.battery_edge_j, records[0].harvest.meter_gaps, records[7].harvest.energy_j.rails, records[7].harvest.energy_j.meter, records[7].harvest.energy_j.battery, records[7].harvest.idle.pre.rails.power_w, records[7].harvest.idle.pre.meter.power_w, records[7].harvest.idle.pre.battery.power_w, records[7].harvest.idle.post.rails.power_w, records[7].harvest.idle.post.meter.power_w, records[7].harvest.idle.post.battery.power_w, records[7].harvest.anchor_shift_j, records[7].harvest.r_max_s, records[7].harvest.meter_edge_w, records[7].harvest.battery_edge_j, records[7].harvest.meter_gaps, records[0].receipt.repeats, records[7].receipt.repeats arithmetic unavailable: non-finite arithmetic)')}
anchor_1e308_one OK {'rails': ('NOT RESOLVED', 3.0271555718577845e+302), 'gpu': ('NOT RESOLVED', 3.0271555718577845e+302), 'dc': ('RESOLVED', 0.002527022733700807), 'rest': ('NOT RESOLVED', 3.0271555718577845e+302)}
battery_edge_all_-1.0 OK {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))'), 'rest': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))')}
battery_edge_all_-10.0 OK {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))'), 'rest': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))')}
battery_edge_all_-20.0 OK {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))'), 'rest': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))')}
battery_edge_all_-40.0 OK {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))'), 'rest': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))')}
battery_edge_rec0_-1e6 OK {'rails': ('UNDETERMINED', 0.0005732822806092617), 'gpu': ('UNDETERMINED', 0.00028575897827642216), 'dc': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))'), 'rest': ('UNDETERMINED', 'not defined (records[0].harvest.battery_edge_j[0] missing or invalid (battery edge energy missing or invalid))')}
```

## Round 8 (fix round)

Activation `431c49d8`, 2026-10-29. Continued `codex/2026-10-28-kb-v2` from `156f03110`; read Opus delta review and scripts at JouleWise-data `8970e3b4e414b908ef0be60f1c2d30a94c66c7a1`. Implementation/test steps committed and pushed as `390ac6b81` and `6c75a95a1`; this report is the final committed/pushed step.

K1–K4 are complete. Battery edge energy is again a non-negative bound; invalid values retain all evidence/calls and give `battery edge energy missing or invalid`, with no dependent printed interval. Nonpositive or non-finite computed half-widths become UNDETERMINED with quantity-naming reasons before interval formatting. Native rails/GPU intervals must be disjoint and ordered, including duplicate-row rejection. GPU and meter integrals must be non-negative. Scan statuses come from the producer's two values (`knee found`, `knee not found`); unknown values and a refusal with numeric K are reasoned scan-status faults.

Verification: Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`.

- Reader/kit: **51 tests, OK, 2060.172 s**, including **1134 generated real-CLI faults**. Added negative battery edge terms in all eight calls and both edge positions, overlap/duplicate rows in both native families and idle spans, GPU/meter signs, unknown/inconsistent scan statuses, and a formatter spy for invalid widths. Evidence/call retention, named reasons and no shrink are checked.
- Session/repin: **73 tests, OK, 2021.338 s**. All **124 requested tests pass**. Seven focused tests and two formatter compatibility follow-up tests also pass. The environment interrupted the first full-suite attempt before completion; these totals are from completed reruns. These four modules cover the standalone tooling change; the full repository suite was not run locally.
- Both Opus scripts replayed at the immutable `156f03110` snapshot and final reader: **53 named CLI cases plus 9 in-process cases** per side. Every transcript line is preserved in this report’s preceding replay-transcript appendix. Final CLI cases all exit 0 with eight calls, **0 tracebacks and 0 shrink flags**. All five negative-edge scenarios in the in-process script are reasoned unavailable after the fix. The review's stated 58 CLI cases differs from the observed 53; no cases were removed.
- K2's `tau_s_1e300_rec0`, `gap_fsum_overflow_rec3`, and `anchor_shift_1e308_all` already pass at `156f03110`, retaining eight calls and reasoned undefined affected quantities. Round 7's J3 guards need no further change.
- Round 7's `short_support.py` and `extreme.py` replay unchanged in a temporary mirror: six short-support cases retain eight calls and remove dependent widths; float/int extreme tau both exit 0. Opus `h4_arms.py`: **1,248 checks, 0 failures**. Standalone `repin.py --check`: **PASS 16 pin families current**; kit freshness: **verified non-claim Mac kit**. No regeneration or digest changes. `git diff --check` passes.

Worked output is unchanged: **rails 0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024 J/GB; share 0.3458 ± 0.0075**. The **4.5e-7 GB/s** and **5.7e-6 J/GB** bars are unchanged; no acceptance bar was added.

Decisions I made:

- K1 supersedes Round 6's mistaken signed-edge decision: battery power and its stream integral stay signed, but the registered absolute-power edge bound does not.
- Reject nonpositive computed uncertainty before formatting; retain valid zero-valued underlying measurements and bounds. CI caught the existing direct zero-width helper compatibility test; restore that helper behavior while keeping invalid computed widths out of the formatter. No epsilon or replacement width is introduced.
- Enforce disjointness only for interval rows; preserve the existing duplicate-poll-stamp policy for meter/battery polls.
- Read status values directly from `knee_scan`'s initializer/update, and reject an inconsistent refusal with numeric K. Preserve the ordinary refusal with K null.
- Replay scripts and write their scratch evidence in temporary mirrors, preserving both review branches and the exhaustive repository write scope.

No NEEDS_RULING or scope expansion. Only the four authorized files changed. No hardware measurement, admission or merge. Final-head CI is read after pushing this report; every observed job state is reported separately in the final handoff, without an advance green claim.
