# 43 — Explore sweep: is a `_v5` prefill run's realized prompt length ever checked against the registered length?

Seat: Claude Explore agent (read-only sweep, 2026-09-01), commissioned by the magistrate under ruling 39b clause 6.

## Conclusion (verbatim)

No. Nothing in `joulewise/` or `scripts/` refuses, flags, or even *observes* a mismatch for a `_v5` PREFILL run whose realized token count ≠ `PREFILL_LENGTH` or whose realized `token_ids_sha256` ≠ the registered `prompt_candidate.token_count_basis.per_model[].token_ids_sha256`. The three candidate gates are all structurally out of reach: `cli.py`'s hash/count cross-check is fenced by `if isinstance(metadata.get("suite"), dict)`, `cli.py`'s `planned_prompt_tokens_mismatch` and `bundle_read.py`'s per-item hash check both short-circuit on `suite_manifest() is None` / `manifest.items`, and `envelope_gate`'s E4 "realized prompt_tokens invariance" is (a) suite-only and (b) a within-run cross-item dispersion metric, not a plan-conformance check. The prefill config never carries a `prompt_tokens` key at all (`workload_for()` emits `prompt_text` only); the only planned number lives in `prefill_family_definition()["workload_profile"]["prompt_tokens"]`, which `floor_extraction._validate_condition_family_definition` only asserts is a positive integer. `analysis_manifest_v3` binds `prefill_prompt_candidate.json` by path+sha256 bytes only and never parses `token_count_basis`; the string `token_count_basis` does not appear in production code. `joulewise/analysis_engine/inputs.py:2478-2482` states the exclusion outright ("Collection-varying values (run ID, prompt hash, emitted tokens, stop reason, environment load) are deliberately excluded").

## Sites inspected

| file:line | compares | applies to prefill `prompt_text` runs? |
|---|---|---|
| joulewise/cli.py:765-783 | realized prompt hash/count vs suite_items rollup | suite-only |
| joulewise/cli.py:707-764, 784-826 | shape only (keys, 64-hex, domain) | yes — no value check |
| joulewise/cli.py:1158-1192 | per-item realized vs planned_prompt_tokens | suite-only (budgeted) |
| joulewise/bundle_read.py:2095-2129 | realized hash vs manifest item source | suite-only |
| joulewise/envelope_gate.py:564-585 | E4 cross-item dispersion | suite-only; not plan conformance |
| joulewise/floor_extraction.py:813-852 | family prompt_tokens is a positive int | schema only |
| joulewise/adapters/mlx_runtime.py:1135-1170 | suite closure (hash, planned count) | suite-only |
| joulewise/adapters/mlx_runtime.py:931-952 | `_prompt_for_workload` prompt_text branch | prefill path — no comparison |
| scripts/run_campaign.py:2586-2710 | realized hash vs generator sidecar | `not_applicable` without sidecar/suite |
| joulewise/analysis_manifest_v3.py:2399-2425 | candidate file path+sha | bytes only |
| joulewise/analysis_engine/inputs.py:2552-2617 | config↔realized identity; non-suite checks output_tokens only | no prompt check |
| scripts/check_window_provenance.py, scripts/gen_state.py, joulewise/campaign_provenance.py | no matches | — |

## Why it matters

The prefill arm's claim is "prefill energy at L tokens". Without this check an honest tokenizer or `mlx_lm` drift between the desk day and collection would silently measure a different length than registered — a physics/evidence fence in D-161's sense, not an operator-only adversary. Disposition: design consult (three seats), then a kernel row.
