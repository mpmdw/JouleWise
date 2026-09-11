# Test Audit - 2026-07-07

- Branch: `stream/test-audit`
- Baseline suite on current main-equivalent tree: `python3 -m unittest discover -s tests` -> `Ran 369 tests ... OK (skipped=10)`
- Final suite after this audit: `Ran 415 tests ... OK (skipped=10, expected failures=31)`
- Scope: stable core around `bundle_read`, bundle evidence layout, schemas, reducer, report, powermetrics parser, CLI, and clock behavior.

## Confirmed Bugs

| ID | Severity | file:symbol | One-line impact | Pinning test |
|---|---|---|---|---|
| B1 / rank 7 | blocker | `joulewise/bundle_read.py:_check_summary` | A status-only succeeded summary is treated as complete and valid, hiding truncated metrics. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_status_only_succeeded_summary_is_not_complete_or_valid` (`expectedFailure`) |
| B2 / S5 | blocker | `joulewise/bundle_read.py:BundleReader.problems` | Tampered `config.json` with stale `metadata.config_sha256` passes provenance validation. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_validate_bundle_rejects_config_sha256_mismatch` (`expectedFailure`) |
| A1 | blocker | `joulewise/adapters/powermetrics.py:parse_powermetrics_records` | A trailing truncated plist tail rejects otherwise complete powermetrics frames. | `tests/test_audit_powermetrics_parser.py::PowermetricsParserBugPins.test_parser_ignores_trailing_truncated_document_after_valid_frames` (`expectedFailure`) |
| rank 1 | high | `joulewise/bundle.py:RunBundleWriter.write_output/log_path` | Traversal names can escape `outputs/` or `logs/` subdirectories. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_write_output_rejects_path_traversal_name`; `...test_log_path_rejects_path_traversal_name` (`expectedFailure`) |
| rank 2 / rank 3 / B4 | high | `joulewise/bundle_read.py:BundleReader.summed_curve`, `_check_power_trace` | Non-finite trace values parse and validate, allowing NaN/Infinity to enter energy math. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_summed_curve_rejects_non_finite_trace_numbers`; `...test_validate_bundle_rejects_non_finite_trace_rows` (`expectedFailure`) |
| S1 | should-fix | `joulewise/schemas.py:BenchmarkConfig.from_mapping` | Unsupported `schema_version` values are accepted by the v0.1 parser. | `tests/test_audit_schema_edges.py::SchemaBugPins.test_rejects_unsupported_schema_version` (`expectedFailure`) |
| S3 | should-fix | `joulewise/schemas.py:WorkloadProfile.validate` | Multiple prompt sources are accepted, making runtime/reducer token accounting ambiguous. | `tests/test_audit_schema_edges.py::SchemaBugPins.test_workload_rejects_multiple_prompt_sources` (`expectedFailure`) |
| S4 | should-fix | `joulewise/schemas.py:_optional_float` | `NaN`/`Infinity` numeric config values validate. | `tests/test_audit_schema_edges.py::SchemaBugPins.test_sampling_rejects_non_finite_numbers` (`expectedFailure`) |
| B3 | should-fix | `joulewise/bundle_read.py:BundleReader.problems` | `metadata.json` can be valid JSON but not an object and still pass default validation. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_validate_bundle_rejects_metadata_non_object` (`expectedFailure`) |
| B5 | should-fix | `joulewise/bundle_read.py:BundleReader.summed_curve` | Duplicate rail rows at one timestamp are summed, double-counting energy. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_summed_curve_rejects_duplicate_rail_at_timestamp` (`expectedFailure`) |
| B8 | should-fix | `joulewise/bundle.py:RunBundleWriter.write_raw` | A partial raw artifact can poison retry because immutable-file checks see it as existing evidence. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_write_raw_partial_failure_does_not_poison_retry` (`expectedFailure`) |
| R2 | should-fix | `joulewise/reduce.py:_idle_baseline` | Malformed idle baseline metadata raises before structured-failure handling. | `tests/test_audit_reduce_degenerate.py::ReduceDegenerateBugPins.test_malformed_idle_baseline_is_structured_failure` (`expectedFailure`) |
| R3 | should-fix | `joulewise/reduce.py:_idle_baseline/_reduce` | NaN idle baseline produces succeeded summaries with NaN metrics. | `tests/test_audit_reduce_degenerate.py::ReduceDegenerateBugPins.test_nan_idle_baseline_fails_instead_of_nan_success` (`expectedFailure`) |
| R4 | should-fix | `joulewise/reduce.py:_reduce` | In-window NaN trace power produces succeeded summaries with NaN gross energy. | `tests/test_audit_reduce_degenerate.py::ReduceDegenerateBugPins.test_nan_power_trace_fails_instead_of_nan_success` (`expectedFailure`) |
| R5 | should-fix | `joulewise/reduce.py:_thermal_drift_c` | Bad thermal metadata raises raw `ValueError` instead of a structured failed summary. | `tests/test_audit_reduce_degenerate.py::ReduceDegenerateBugPins.test_bad_thermal_metadata_is_structured_failure` (`expectedFailure`) |
| A5 | should-fix | `joulewise/adapters/powermetrics.py:_required_float` | Powermetrics rail power can parse as NaN and contaminate downstream samples. | `tests/test_audit_powermetrics_parser.py::PowermetricsParserBugPins.test_parser_rejects_non_finite_power_values` (`expectedFailure`) |
| K1 | should-fix | `joulewise/cli.py:_load_config/main` | Invalid UTF-8 config bytes raise `UnicodeDecodeError` instead of clean exit 2. | `tests/test_audit_cli_examples.py::CliAndKVSizeBugPins.test_invalid_utf8_config_exits_2_without_traceback` (`expectedFailure`) |
| K2 | should-fix | `joulewise/kv_size.py:extract_kv_params` | `num_kv_heads` alias is ignored, overreporting Falcon-style KV size. | `tests/test_audit_cli_examples.py::CliAndKVSizeBugPins.test_extracts_num_kv_heads_alias` (`expectedFailure`) |
| K3 | should-fix | `joulewise/kv_size.py:extract_kv_params` | `multi_query: true` without KV-head count falls back to full attention heads. | `tests/test_audit_cli_examples.py::CliAndKVSizeBugPins.test_multi_query_true_uses_one_kv_head` (`expectedFailure`) |
| K4 | should-fix | `joulewise/kv_size.py:extract_kv_params` | Non-divisible attention-head/KV-head grouping is accepted. | `tests/test_audit_cli_examples.py::CliAndKVSizeBugPins.test_attention_heads_must_be_divisible_by_kv_heads` (`expectedFailure`) |
| K5 | should-fix | `joulewise/cli.py:_bundle_line` | Unquoted bundle path field is not round-trip parseable for paths containing spaces. | `tests/test_audit_cli_examples.py::CliAndKVSizeBugPins.test_bundle_line_with_space_path_is_parseable` (`expectedFailure`) |
| rank 11 | med | `joulewise/bundle_read.py:BundleReader.rail_manifest` | Non-string rails are coerced with `str()` instead of rejected. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_rail_manifest_rejects_non_string_entries` (`expectedFailure`) |
| rank 12 | med | `joulewise/bundle_read.py:BundleReader.events` | Strict event reads accept missing/extra keys that `validate-bundle` rejects. | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_strict_events_rejects_non_contract_key_set` (`expectedFailure`) |
| rank 14 | med | `joulewise/report.py:_flatten` | Flattened report rows preserve insertion order despite a sorted-output docstring. | `tests/test_audit_report.py::ReportBugPins.test_flatten_returns_sorted_key_rows` (`expectedFailure`) |
| rank 21 | med | `joulewise/clock.py:FakeClock.sleep` | Bool and non-finite sleep durations are accepted. | `tests/test_audit_clock.py::ClockBugPins.test_fake_clock_rejects_bool_sleep_duration`; `...test_fake_clock_rejects_nan_sleep_duration`; `...test_fake_clock_rejects_inf_sleep_duration` (`expectedFailure`) |
| S6 | nit | `joulewise/schemas.py:BenchmarkConfig.json_schema` | Exported schema allows lower `sampling.power_hz` than the loader. | `tests/test_audit_schema_edges.py::SchemaBugPins.test_config_schema_power_hz_minimum_matches_loader` (`expectedFailure`) |
| S7 | nit | `joulewise/schemas.py:BenchmarkConfig.json_schema` | Exported schema allows empty strings that the loader rejects. | `tests/test_audit_schema_edges.py::SchemaBugPins.test_config_schema_required_strings_are_non_empty` (`expectedFailure`) |

## Coverage Gaps Closed

| Finding ID(s) | Area | Test |
|---|---|---|
| rank 5 | Required schema sections | `tests/test_audit_schema_edges.py::SchemaCoverageGapTests.test_required_sections_must_be_objects` |
| rank 6 | Schema primitive invariants | `tests/test_audit_schema_edges.py::SchemaCoverageGapTests.test_bool_and_negative_numeric_optionals_are_rejected` |
| rank 8 | Clock selection | `tests/test_audit_cli_examples.py::CliCoverageGapTests.test_select_clock_uses_fake_only_for_all_mock` |
| rank 9 | Report HTML escaping | `tests/test_audit_report.py::ReportCoverageGapTests.test_key_value_table_escapes_html_from_values` |
| rank 10 | Example backend resolvability | `tests/test_audit_cli_examples.py::CliCoverageGapTests.test_example_backend_resolution_is_structured` |
| rank 16 | CLI schema `--output` paths | `tests/test_audit_cli_examples.py::CliCoverageGapTests.test_schema_output_options_write_json_and_stdout_message` |
| rank 17 | Non-`.json` config rejection | `tests/test_audit_cli_examples.py::CliCoverageGapTests.test_validate_config_rejects_non_json_path_without_traceback` |
| rank 18 | `kv-size --prompt-tokens` invalid lists | `tests/test_audit_cli_examples.py::CliCoverageGapTests.test_kv_size_rejects_empty_zero_and_negative_prompt_lists` |
| rank 19 | `kv-size` config JSON type | `tests/test_audit_cli_examples.py::CliCoverageGapTests.test_kv_size_config_json_must_be_object` |
| rank 20 | `dtype_bytes` direct validation | `tests/test_audit_cli_examples.py::CliCoverageGapTests.test_dtype_bytes_zero_and_negative_raise` |
| rank 23 | `run_metadata.tags` invalid lists | `tests/test_audit_schema_edges.py::SchemaCoverageGapTests.test_run_metadata_tags_invalid_lists_are_rejected` |
| S2 | Unknown workload keys ignored; no contract or exported schema forbids extras | `tests/test_audit_schema_edges.py::SchemaCoverageGapTests.test_unknown_workload_keys_are_ignored` |
| rank 24 | Run ID sanitization; `...` -> `---` satisfies D-010 charset/non-empty rules | `tests/test_audit_bundle_validation.py::BundleValidationBugPins.test_punctuation_only_run_id_sanitizes_to_allowed_nonempty_value` |
| R6 | Report non-finite number formatting; literal `nan`/`inf` tokens are defensible | `tests/test_audit_report.py::ReportBugPins.test_index_formats_nonfinite_numbers_as_literal_tokens` |
| K6 | `kv-size` human output shape; `human=<n> <unit>` is the documented format | `tests/test_audit_cli_examples.py::CliAndKVSizeBugPins.test_cli_kv_size_output_human_value_includes_unit_token` |

## Stale, Dropped, Duplicates

| ID | Classification | Reason |
|---|---|---|
| rank 4 | dropped/covered | Reversed marker timestamps either violate existing non-decreasing event validation or reduce to a structured failure; no unstructured crash was confirmed. |
| rank 13 | dropped | `phase_windows()` documents pairing starts/ends and ignoring unmatched events; no contract-required invalidation found. |
| rank 15 | dropped | Report currently omits corrupt-event shading while still rendering the page; no explicit chart-note contract was found in this stable-core audit. |
| C1, C2, C3, C5 | dropped from Stream F stable-core pins | Controller execution-path bugs are outside the stable-core scope for this final audit artifact; C3 remains important for a controller-focused pass. |
| A2, A3, A4, A6, A7 | dropped from Stream F stable-core pins | Operational adapter/runtime process handling is outside this stable-core pass; only powermetrics parser bugs A1/A5 were pinned. |
| K7 | dropped from Stream F stable-core pins | `scripts/backup_runs.sh` is outside CLI/core Python scope. |
| rank 32 | stale | `scripts/generate_matrix.py` and `tests/test_generate_matrix.py` exist in this tree; stale per brief, landed via PR #3. |
| rank 33 | stale | `scripts/run_campaign.py` and `tests/test_run_campaign.py` exist in this tree; stale per brief, landed via PR #3. |
| B6 | dropped | D-011 completion is a schema-valid `summary_metrics.json`; a torn/partial write is not a JSON object, so `BundleReader.is_complete()` already returns `False`. |
| B7 | dropped | The writer contract allows inspectable incomplete bundle directories after an early crash; cleanup is not required. |
| C4 | dropped | Known design tradeoff per D-003: `SystemClock.now()` is epoch wall time, while monotonic-vs-wall offset is recorded separately; backward wall-clock steps remain a residual risk. |

## Deferred

- rank 25 - Reducer aggregation: No aggregate implementation/tests present; future aggregate consumer of reader policy. Reason: add aggregate fixture with mixed succeeded/failed/incomplete bundles and expected rollups later.
- rank 26 - Controller experiment: Cooldown skip when telemetry resolver returns `None`. Reason: non-mock telemetry registry returns unavailable; assert manifest cooldown skip reason later.
- rank 27 - Controller experiment: Cooldown `AdapterFailure` branch untested. Reason: stub `measure_idle` raising `AdapterFailure`; assert manifest records failure reason later.
- rank 28 - Mock telemetry timing: Zero-duration sampling produces one boundary sample. Reason: start/stop without clock advance; assert expected sample count and reducer behavior later.
- rank 29 - Powermetrics parser: Non-dict plist document branch untested. Reason: parse a plist list/scalar document and assert normalized `ValueError` later.
- rank 30 - Powermetrics adapter: `_stop_process()` kill-after-timeout path untested. Reason: fake process whose `communicate()` times out; assert `kill()` is called later.
- rank 31 - Powermetrics adapter: `start_sampling()` active-process guard untested. Reason: call `start_sampling()` twice; expect structured `UNKNOWN_ERROR` later.
- R1 - Reducer bracket-only interpolation. Reason: enhancement gated by D-030; D-030 defines a reducer-consumable nonzero window as `>= 2` in-window samples.

## Suggested Fix Queue

- B1/rank 7: make summary completeness require schema-level metric fields for succeeded summaries, and have `is_complete()` reject status-only success.
- B2/S5: recompute SHA-256 over the on-disk `config.json` bytes and compare it to `metadata.config_sha256` in `BundleReader.problems()`.
- A1: parse NUL-framed powermetrics streams leniently for trailing truncated tails after at least one complete frame.
- rank 1: route `write_output()` and `log_path()` through the same plain-file-name validation used for raw artifacts.
- rank 2/rank 3/B4/R4/A5: centralize finite-number checks for trace and powermetrics numeric fields before values enter curves or summaries.
- S1/S3: add explicit schema-version and mutually-exclusive prompt-source validation in schema loaders.
- S4/S6/S7: align loader and exported JSON Schema for finite numbers, `sampling.power_hz >= 0.001`, and non-empty strings.
- B3/B5/rank 11/rank 12: tighten reader validation for metadata object shape, manifest element types, duplicate rails, and event key sets.
- B8: write raw artifacts with temp-file/rename cleanup semantics so failed writes do not leave retry-blocking partial state.
- R2/R3/R5: move all metadata reconstruction into structured failure handling and validate finite numeric metadata.
- rank 14/rank 15: make report formatting deterministic and explicit about omitted/degenerate data.
- rank 21: reject non-real sleep durations.
- K1-K5: normalize CLI parse/error handling and add KV-size aliases, MQA semantics, divisibility validation, and quoted/path-safe output.
