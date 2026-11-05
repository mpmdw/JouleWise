# Qwen4 gold: 0

Status: **INCOMPLETE_OR_FAILED**. Scope: prefill, no cache.

Completed cases: 8/8.

| Case | Status | Max abs | Min cosine | Peak worker GiB |
|---|---|---:|---:|---:|
| tokens-a-fp32-real | STUB_NOT_VALIDATED | 0.00127189 | 0.99992793 | 0.312 |
| tokens-a-fp32-random | STUB_NOT_VALIDATED | 0.000438619 | 0.999983165 | 0.324 |
| tokens-b-fp32-real | STUB_NOT_VALIDATED | 0.000934612 | 0.999932164 | 0.324 |
| tokens-b-fp32-random | STUB_NOT_VALIDATED | 0.000292573 | 0.999990755 | 0.321 |
| tokens-a-bf16-real | STUB_NOT_VALIDATED | 0.0012207 | 0.999926564 | 0.319 |
| tokens-a-bf16-random | STUB_NOT_VALIDATED | 0.000469649 | 0.999980676 | 0.315 |
| tokens-b-bf16-real | STUB_NOT_VALIDATED | 0.000976562 | 0.999930881 | 0.323 |
| tokens-b-bf16-random | STUB_NOT_VALIDATED | 0.000360593 | 0.999989469 | 0.325 |

Tolerances (all required traces must pass elementwise and cosine gates):

{"fp32": {"atol": 0.0001, "rtol": 0.0001, "cosine_min": 0.999999}, "bf16": {"atol": 0.03125, "rtol": 0.03125, "cosine_min": 0.999}}

fp32: 1e-4 absolute/relative permits differing reduction order. bf16: 0.03125 absolute/relative
allows eight bf16 representable steps at |reference|=1 (atol+rtol); cosine >= 0.999 constrains aggregate drift.
These provisional engineering bounds are fixed before comparison and are never fitted to results.
Router expert sets, PLE hash ids and QSA masks must agree exactly. See case JSON for metrics, missing traces and failures.
