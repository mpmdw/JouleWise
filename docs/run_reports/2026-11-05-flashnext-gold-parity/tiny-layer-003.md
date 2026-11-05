# Qwen4 gold: 3

Status: **INCOMPLETE_OR_FAILED**. Scope: prefill, no cache.

Completed cases: 8/8.

| Case | Status | Max abs | Min cosine | Peak worker GiB |
|---|---|---:|---:|---:|
| tokens-a-fp32-real | STUB_NOT_VALIDATED | 0.0134472 | 0.99047411 | 0.317 |
| tokens-a-fp32-random | STUB_NOT_VALIDATED | 0.00463744 | 0.997171624 | 0.320 |
| tokens-b-fp32-real | STUB_NOT_VALIDATED | 0.00740908 | 0.993970819 | 0.315 |
| tokens-b-fp32-random | STUB_NOT_VALIDATED | 0.00607341 | 0.996714214 | 0.317 |
| tokens-a-bf16-real | STUB_NOT_VALIDATED | 0.0134277 | 0.990481299 | 0.314 |
| tokens-a-bf16-random | STUB_NOT_VALIDATED | 0.00462286 | 0.997181654 | 0.319 |
| tokens-b-bf16-real | STUB_NOT_VALIDATED | 0.00738525 | 0.993974698 | 0.324 |
| tokens-b-bf16-random | STUB_NOT_VALIDATED | 0.00605943 | 0.996704059 | 0.321 |

Tolerances (all required traces must pass elementwise and cosine gates):

{"fp32": {"atol": 0.0001, "rtol": 0.0001, "cosine_min": 0.999999}, "bf16": {"atol": 0.03125, "rtol": 0.03125, "cosine_min": 0.999}}

fp32: 1e-4 absolute/relative permits differing reduction order. bf16: 0.03125 absolute/relative
allows eight bf16 representable steps at |reference|=1 (atol+rtol); cosine >= 0.999 constrains aggregate drift.
These provisional engineering bounds are fixed before comparison and are never fitted to results.
Router expert sets, PLE hash ids and QSA masks must agree exactly. See case JSON for metrics, missing traces and failures.
