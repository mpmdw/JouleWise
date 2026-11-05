# Qwen4 gold: 1

Status: **INCOMPLETE_OR_FAILED**. Scope: prefill, no cache.

Completed cases: 8/8.

| Case | Status | Max abs | Min cosine | Peak worker GiB |
|---|---|---:|---:|---:|
| tokens-a-fp32-real | STUB_NOT_VALIDATED | 0.00580163 | 0.99814663 | 0.315 |
| tokens-a-fp32-random | STUB_NOT_VALIDATED | 0.00565533 | 0.997975333 | 0.318 |
| tokens-b-fp32-real | STUB_NOT_VALIDATED | 0.00474855 | 0.998587362 | 0.320 |
| tokens-b-fp32-random | STUB_NOT_VALIDATED | 0.00416922 | 0.998107826 | 0.327 |
| tokens-a-bf16-real | STUB_NOT_VALIDATED | 0.00579834 | 0.99814241 | 0.320 |
| tokens-a-bf16-random | STUB_NOT_VALIDATED | 0.00563796 | 0.997963199 | 0.318 |
| tokens-b-bf16-real | STUB_NOT_VALIDATED | 0.00476074 | 0.998587297 | 0.325 |
| tokens-b-bf16-random | STUB_NOT_VALIDATED | 0.00426773 | 0.998097839 | 0.324 |

Tolerances (all required traces must pass elementwise and cosine gates):

{"fp32": {"atol": 0.0001, "rtol": 0.0001, "cosine_min": 0.999999}, "bf16": {"atol": 0.03125, "rtol": 0.03125, "cosine_min": 0.999}}

fp32: 1e-4 absolute/relative permits differing reduction order. bf16: 0.03125 absolute/relative
allows eight bf16 representable steps at |reference|=1 (atol+rtol); cosine >= 0.999 constrains aggregate drift.
These provisional engineering bounds are fixed before comparison and are never fitted to results.
Router expert sets, PLE hash ids and QSA masks must agree exactly. See case JSON for metrics, missing traces and failures.
