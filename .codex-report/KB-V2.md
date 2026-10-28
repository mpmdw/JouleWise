# KB-V2 — activation 39206674, 2026-10-28

Status: in progress; reconciled rule awaiting the lead's admission. No hardware measurements.

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

Pending implementation.

## CI

Draft PR #593: https://github.com/mpmdw/JouleWise/pull/593 . Pending final-head CI.
