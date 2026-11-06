# ALIGN v4 WP2 + WP3 handoff

Branch: `lane/2026-11-05-align-v4-wp2-657`, based on `c8ef6b2f6`. Local commits only; no push.

Code commits:

- `4c8616da8` — default checkpoint limits to `None`, omit unset identity fields, retain trial fix-up items 4/5.
- `54b8a624d` — move checkpoint prefill into ALIGN's stream observer using an explicit runtime view; restore the complete MLX adapter to `83e2dac59` bytes.

The v3 plan, identity pins, verification receipt, and generator are byte-identical to `83e2dac59`. None of the 42 tracked `align_pilot_v3` files contains `hybrid_checkpoint_limit`. Trial fix-up items 1–3 were unnecessary.

Final selected tests: **201 selected, 191 passed, 10 skipped, zero failures/errors**. Final module runs were sequential. No full suite, network, analysis pipeline, or live measurement was run.

Each module below used `python3.13 -B -m unittest <module>` with the offline Jinja2/MarkupSafe overlay and native opt-ins disabled. Exact environment, the blinded KitTests wrapper, preliminary failures, and logs are documented in the [dated report](docs/run_reports/2026-11-05-align-v4-wp2-wp3.md).

| Module / class | Passed | Skipped |
|---|---:|---:|
| `tests.align.test_cache_checkpoint` | 16 | 0 |
| `tests.align.test_cache_checkpoint_native` | 0 | 5 |
| `tests.align.test_pilot3.KitTests` (blinded wrapper) | 3 | 1 |
| `tests.align.test_pilot3_cache` | 12 | 0 |
| `tests.align.test_pilot4` (includes its KitTests) | 17 | 1 |
| `tests.align.test_decode_budget` | 20 | 1 |
| `tests.align.test_history_rendering` | 7 | 2 |
| `tests.align.test_xml_tool_calls` | 21 | 0 |
| `tests.align.test_measurement_core_boundary` | 4 | 0 |
| `tests.align.test_apple_endpoint` | 9 | 0 |
| `tests.align.test_thermal_gate` | 31 | 0 |
| `tests.test_mlx_runtime` | 43 | 0 |
| `tests.test_mlx_runtime_detokenizer` | 8 | 0 |

`compileall`, `git diff --check`, and `align_pilot_kit.py --check` pass. The four lead-owned coordination files are unchanged.

Files touched: `workload.py`, `endpoint.py`, new `generation.py` under `joulewise/align/apple/`; restored `joulewise/adapters/mlx_runtime.py`; three ALIGN test files; `docs/align/hybrid_cache_checkpoints.md`; this handoff and the dated report.

Lead next steps: run the native checkpoint, MLX deadman, and pinned-tokenizer history gates; obtain the independent Opus executing-review paper and cite it in WP5's `0ba413d40` row. The two external-source kit gates were not exercised here. Native correctness/overhead and production readiness remain PROVISIONAL. No new Ed ruling is requested. Full standalone survey papers outside the allowed tree were not independently inspected; the supplied synthesis, patch, local trial bundle, and in-repo implementation records were used.
