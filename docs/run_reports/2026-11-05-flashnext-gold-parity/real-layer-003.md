# Qwen4 gold: 3

Status: **INCOMPLETE_OR_FAILED**. Scope: prefill, no cache.

Completed cases: 8/8.

| Case | Status | Max abs | Min cosine | Peak worker GiB |
|---|---|---:|---:|---:|
| tokens-a-fp32-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-a-fp32-random | STUB_NOT_VALIDATED | 1.31946 | 0.990208362 | 0.934 |
| tokens-b-fp32-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-b-fp32-random | STUB_NOT_VALIDATED | 1.62776 | 0.987688981 | 0.931 |
| tokens-a-bf16-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-a-bf16-random | STUB_NOT_VALIDATED | 1.3118 | 0.990216292 | 0.552 |
| tokens-b-bf16-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-b-bf16-random | STUB_NOT_VALIDATED | 1.64243 | 0.987711256 | 0.550 |

Blocked case reasons: missing or failed reference predecessor; no synthetic substitute


Tolerances (all required traces must pass elementwise and cosine gates):

{"fp32": {"atol": 0.0001, "rtol": 0.0001, "cosine_min": 0.999999}, "bf16": {"atol": 0.03125, "rtol": 0.03125, "cosine_min": 0.999}}

fp32: 1e-4 absolute/relative permits differing reduction order. bf16: 0.03125 absolute/relative
allows eight bf16 representable steps at |reference|=1 (atol+rtol); cosine >= 0.999 constrains aggregate drift.
These provisional engineering bounds are fixed before comparison and are never fitted to results.
Router expert sets, PLE hash ids and QSA masks must agree exactly. See case JSON for metrics, missing traces and failures.
