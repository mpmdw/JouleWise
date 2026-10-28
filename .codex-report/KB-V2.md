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
