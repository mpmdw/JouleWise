# Qwen4 gold: 2

Status: **INCOMPLETE_OR_FAILED**. Scope: prefill, no cache.

Completed cases: 8/8.

| Case | Status | Max abs | Min cosine | Peak worker GiB |
|---|---|---:|---:|---:|
| tokens-a-fp32-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-a-fp32-random | STUB_NOT_VALIDATED | 0.476076 | 0.998310205 | 0.913 |
| tokens-b-fp32-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-b-fp32-random | STUB_NOT_VALIDATED | 0.580986 | 0.997703527 | 0.896 |
| tokens-a-bf16-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-a-bf16-random | STUB_NOT_VALIDATED | 0.476222 | 0.998308706 | 0.583 |
| tokens-b-bf16-real | BLOCKED_REAL_INPUT | — | — | 0.000 |
| tokens-b-bf16-random | STUB_NOT_VALIDATED | 0.578757 | 0.99770728 | 0.572 |

Blocked case reasons: missing or failed reference predecessor; no synthetic substitute


Tolerances (all required traces must pass elementwise and cosine gates):

{"fp32": {"atol": 0.0001, "rtol": 0.0001, "cosine_min": 0.999999}, "bf16": {"atol": 0.03125, "rtol": 0.03125, "cosine_min": 0.999}}

fp32: 1e-4 absolute/relative permits differing reduction order. bf16: 0.03125 absolute/relative
allows eight bf16 representable steps at |reference|=1 (atol+rtol); cosine >= 0.999 constrains aggregate drift.
These provisional engineering bounds are fixed before comparison and are never fitted to results.
Router expert sets, PLE hash ids and QSA masks must agree exactly. See case JSON for metrics, missing traces and failures.
