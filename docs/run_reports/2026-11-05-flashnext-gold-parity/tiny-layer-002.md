# Qwen4 gold: 2

Status: **INCOMPLETE_OR_FAILED**. Scope: prefill, no cache.

Completed cases: 8/8.

| Case | Status | Max abs | Min cosine | Peak worker GiB |
|---|---|---:|---:|---:|
| tokens-a-fp32-real | STUB_NOT_VALIDATED | 0.000482772 | 0.999968375 | 0.317 |
| tokens-a-fp32-random | STUB_NOT_VALIDATED | 0.000440792 | 0.999987468 | 0.320 |
| tokens-b-fp32-real | STUB_NOT_VALIDATED | 0.000565298 | 0.999969398 | 0.319 |
| tokens-b-fp32-random | STUB_NOT_VALIDATED | 0.000527629 | 0.999989906 | 0.322 |
| tokens-a-bf16-real | STUB_NOT_VALIDATED | 0.000488281 | 0.999964112 | 0.324 |
| tokens-a-bf16-random | STUB_NOT_VALIDATED | 0.000442499 | 0.999985958 | 0.323 |
| tokens-b-bf16-real | STUB_NOT_VALIDATED | 0.000610352 | 0.999966949 | 0.322 |
| tokens-b-bf16-random | STUB_NOT_VALIDATED | 0.000531815 | 0.999987787 | 0.325 |

Tolerances (all required traces must pass elementwise and cosine gates):

{"fp32": {"atol": 0.0001, "rtol": 0.0001, "cosine_min": 0.999999}, "bf16": {"atol": 0.03125, "rtol": 0.03125, "cosine_min": 0.999}}

fp32: 1e-4 absolute/relative permits differing reduction order. bf16: 0.03125 absolute/relative
allows eight bf16 representable steps at |reference|=1 (atol+rtol); cosine >= 0.999 constrains aggregate drift.
These provisional engineering bounds are fixed before comparison and are never fitted to results.
Router expert sets, PLE hash ids and QSA masks must agree exactly. See case JSON for metrics, missing traces and failures.
