"""JouleWise command-line interface.

Phase 1 added the schema/config verbs (``validate-config``,
``print-config-schema``, ``print-output-schema``). Phase 2 Slice 2E adds the
headline ``run`` verb (one command -> a complete run bundle) and the
``validate-bundle`` verb (structural verification of any bundle, reused by CI
now and by Phase 5 dataset publication later). Slice 2J adds the ``report``
verb (a static HTML run browser; D-006), which needs the ``[analysis]`` extra.
Slice 2N.6 adds the ``reduce`` verb (post-hoc re-reduction of an existing
bundle - a reducer bug never re-runs hardware, D-002/D-028).
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any, Callable

from joulewise.adapters.nvidia_smi import (
    RAW_SAMPLES_NAME as NVIDIA_SMI_RAW_SAMPLES_NAME,
    samples_from_raw_nvidia_smi,
)

from joulewise.adapters.powermetrics import (
    RAW_IDLE_NAME,
    RAW_IDLE_POST_NAME,
    RAW_SAMPLES_NAME,
    RICH_TELEMETRY_NAME,
    anchor_records_from_powermetrics,
    trace_fallback_endpoint,
    decode_rich_telemetry,
    idle_window_gpu_quality,
    parse_powermetrics_records,
    rich_telemetry_jsonl,
    samples_from_raw_powermetrics,
)
from joulewise.bundle import BundleError
from joulewise.bundle_read import (
    FROZEN_LEGACY_BUNDLE_IDENTITIES,
    BundleReader,
    BundleReadError,
    axi_v2_validation_problems,
)
from joulewise.clock import Clock, FakeClock, SystemClock
from joulewise.controller import (
    record_cooldown_anchor_rejection,
    run_benchmark,
    run_experiment,
)
from joulewise.cooldown_anchor import cooldown_anchor_eligibility
from joulewise.doctor import doctor_report, exit_code as doctor_exit_code
from joulewise.doctor import render_human as render_doctor_human
from joulewise.doctor import render_json as render_doctor_json
from joulewise.kv_size import (
    KVSizeError,
    KVSizeParams,
    bytes_per_token,
    extract_kv_params,
    format_bytes,
    prompt_totals,
)
from joulewise.provenance import (
    FIXED_BUDGET_EXACT,
    FIXED_BUDGET_INCOMPLETE,
    PROMPT_TOKEN_IDS_HASH_DOMAIN,
    SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN,
    suite_prompt_plan_class,
    suite_prompt_rollup,
)
from joulewise.output_identity import (
    OutputIdentityError,
    build_output_identity_report,
    render_output_identity_report,
)
from joulewise.reduce import (
    AXI_REDUCER_VERSION,
    AXI_REDUCER_VERSIONS,
    ReducerVersionError,
    reduce_bundle,
)
from joulewise.report import ReportError, generate_report
from joulewise.schemas import (
    BenchmarkConfig,
    is_admissible_succeeded_summary,
    RunStatus,
    RuntimeBackend,
    SchemaError,
    SUMMARY_REDUCER_VERSION,
    SummaryMetrics,
    TelemetryBackend,
    summary_validation_problems,
)
from joulewise.validation import finite_float
from joulewise.uncertainty_evidence import (
    SCHEMA_VERSION as P2038_SCHEMA_VERSION,
    SCHEMA_VERSION_V2 as P2038_SCHEMA_VERSION_V2,
    derive_idle_drift_evidence,
    derive_powermetrics_clock_evidence,
    derive_powermetrics_clock_evidence_v2,
    stamp_from_mapping,
)

_PROMPT_TOKEN_IDS_HASH_DOMAIN = PROMPT_TOKEN_IDS_HASH_DOMAIN
_SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN = SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN

_STRICT_LEGACY_BUNDLE_IDENTITIES = FROZEN_LEGACY_BUNDLE_IDENTITIES


def _load_config(path: Path) -> dict[str, Any]:
    if path.suffix.lower() != ".json":
        raise SchemaError("Phase 1 CLI supports JSON configs; YAML parsing is planned for Phase 2")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise SchemaError(f"config is not valid UTF-8: {path}") from exc


def _cmd_validate_config(args: argparse.Namespace) -> int:
    path = Path(args.path)
    config = BenchmarkConfig.from_mapping(_load_config(path))
    print(
        "valid config: "
        f"{path} target={config.hardware_target.id} "
        f"runtime={config.hardware_target.runtime_backend.value} "
        f"telemetry={config.hardware_target.telemetry_backend.value}"
    )
    return 0


def _write_or_print_schema(payload: dict[str, Any], output: str | None, label: str) -> int:
    text = json.dumps(payload, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(text + "\n")
        print(f"wrote {label}: {output}")
    else:
        print(text)
    return 0


def _cmd_print_config_schema(args: argparse.Namespace) -> int:
    return _write_or_print_schema(BenchmarkConfig.json_schema(), args.output, "config schema")


def _cmd_print_output_schema(args: argparse.Namespace) -> int:
    return _write_or_print_schema(SummaryMetrics.json_schema(), args.output, "output schema")


def _cmd_doctor(args: argparse.Namespace) -> int:
    report = doctor_report(
        [Path(path) for path in args.configs],
        backup_destination=(
            Path(args.backup_destination).expanduser()
            if args.backup_destination is not None
            else None
        ),
        mode="campaign" if args.campaign else "inspection",
        acknowledge_config_warnings=args.ack_config_warnings,
    )
    rendered = render_doctor_json(report) if args.json_output else render_doctor_human(report)
    print(rendered, end="")
    return doctor_exit_code(report)


# ---------------------------------------------------------------------------
# kv-size verb (Stage 3.0.0)


def _parse_prompt_tokens(text: str) -> list[int]:
    try:
        tokens = [int(part.strip()) for part in text.split(",") if part.strip()]
    except ValueError as exc:
        raise KVSizeError("--prompt-tokens must be a comma-separated list of integers") from exc
    if not tokens:
        raise KVSizeError("--prompt-tokens must include at least one value")
    if any(token <= 0 for token in tokens):
        raise KVSizeError("--prompt-tokens values must be positive")
    return tokens


def _cmd_kv_size(args: argparse.Namespace) -> int:
    explicit = [args.layers, args.kv_heads, args.head_dim]
    if any(value is not None for value in explicit):
        if any(value is None for value in explicit):
            raise KVSizeError("explicit params require --layers, --kv-heads, and --head-dim")
        params = KVSizeParams(args.layers, args.kv_heads, args.head_dim)
    elif args.config:
        config = json.loads(Path(args.config).read_text())
        if not isinstance(config, dict):
            raise KVSizeError("config JSON must be an object")
        params = extract_kv_params(config)
    else:
        raise KVSizeError("provide a config path or --layers/--kv-heads/--head-dim")

    bytes_per_tok = bytes_per_token(
        params.n_layers, params.n_kv_heads, params.head_dim, args.dtype_bytes
    )
    prompts = _parse_prompt_tokens(args.prompt_tokens)
    print(
        "kv-size: "
        f"layers={params.n_layers} "
        f"kv_heads={params.n_kv_heads} "
        f"head_dim={params.head_dim} "
        f"dtype_bytes={args.dtype_bytes} "
        f"bytes_per_token={bytes_per_tok} "
        f"human={format_bytes(bytes_per_tok)}"
    )
    for prompt_tokens, total_bytes in prompt_totals(bytes_per_tok, prompts):
        print(
            "kv-size-total: "
            f"prompt_tokens={prompt_tokens} "
            f"bytes={total_bytes} "
            f"human={format_bytes(total_bytes)}"
        )
    return 0


# ---------------------------------------------------------------------------
# run verb (Slice 2E)


def _select_clock(config: BenchmarkConfig) -> Clock:
    """Pick the clock the ``run`` verb binds for ``config`` (D-020).

    Compose at the CLI boundary, not inside the controller: a ``FakeClock``
    iff BOTH the runtime and telemetry backends are ``mock`` (the all-mock
    vertical slice runs on simulated time so it is instant, deterministic, and
    byte-identical across reruns), a ``SystemClock`` otherwise (any real
    runtime or telemetry needs real time even when the other side is mock).
    The controller code path is identical either way - only the injected
    dependency differs.
    """
    target = config.hardware_target
    all_mock = (
        target.runtime_backend == RuntimeBackend.MOCK
        and target.telemetry_backend == TelemetryBackend.MOCK
    )
    return FakeClock() if all_mock else SystemClock()


def _bundle_line(bundle_path: Path, summary: SummaryMetrics) -> str:
    """The single machine-greppable per-bundle result line (D-011 status map)."""
    line = f"bundle: {shlex.quote(str(bundle_path))} status={summary.status.value}"
    if summary.failure_reason is not None:
        line += f" reason={summary.failure_reason.value}"
    return line


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute the benchmark and print the machine-greppable result line(s).

    ``repetitions > 1`` dispatches to the experiment runner (Slice 2F): one
    ``bundle: ...`` line per member plus a final
    ``experiment: <manifest_path> members=<N>`` line; exit 0 only when ALL
    members succeeded, else 3.

    Config load/validation errors (OSError, JSONDecodeError, SchemaError) and a
    BundleError (e.g. a run-ID collision) propagate to ``main`` and become
    ``error: ...`` on stderr with exit 2 and no bundle. After a bundle exists,
    the controller finalizes it for every outcome (D-011); this verb then maps
    the run status to the process exit code.
    """
    if (args.instrument_calibration_dir is None) != (
        args.instrument_power_policy is None
    ):
        raise SchemaError(
            "--instrument-calibration-dir and --instrument-power-policy must be supplied together"
        )
    config = BenchmarkConfig.from_mapping(_load_config(Path(args.config)))
    clock = _select_clock(config)
    post_window_sampling_dwell_s = (
        args.post_window_sampling_dwell_s
        if config.hardware_target.telemetry_backend == TelemetryBackend.POWERMETRICS
        else None
    )
    if (
        post_window_sampling_dwell_s is not None
        and post_window_sampling_dwell_s < 1.0
    ):
        raise SchemaError(
            "--post-window-sampling-dwell-s must be at least 1.0 for powermetrics"
        )
    frozen_cooldown_anchor = None
    if args.frozen_cooldown_anchor_json is not None:
        try:
            frozen_cooldown_anchor = json.loads(args.frozen_cooldown_anchor_json)
        except json.JSONDecodeError as exc:
            raise SchemaError(
                "--frozen-cooldown-anchor-json is not valid JSON: "
                f"{exc.msg} at line {exc.lineno} column {exc.colno}"
            ) from exc
        anchor_eligibility = cooldown_anchor_eligibility(frozen_cooldown_anchor)
        if not anchor_eligibility["eligible"]:
            verdict_path = None
            if config.workload_profile.repetitions > 1:
                verdict_path = record_cooldown_anchor_rejection(
                    config,
                    Path(args.runs_dir),
                    clock,
                    frozen_cooldown_anchor,
                    anchor_eligibility,
                    boundary="cli_accept",
                )
            verdict_note = (
                f"; verdict={verdict_path}" if verdict_path is not None else ""
            )
            raise SchemaError(
                "--frozen-cooldown-anchor-json rejected fail-closed: "
                + ", ".join(anchor_eligibility["reasons"])
                + verdict_note
            )
    if config.workload_profile.repetitions > 1:
        experiment_kwargs = (
            {"frozen_cooldown_anchor": frozen_cooldown_anchor}
            if frozen_cooldown_anchor is not None
            else {}
        )
        if args.instrument_calibration_dir is not None:
            experiment_kwargs.update(
                {
                    "instrument_calibration_dir": Path(
                        args.instrument_calibration_dir
                    ),
                    "instrument_power_policy": args.instrument_power_policy,
                }
            )
        experiment_kwargs["post_window_sampling_dwell_s"] = (
            post_window_sampling_dwell_s
        )
        manifest_path, members = run_experiment(
            config,
            Path(args.runs_dir),
            clock,
            **experiment_kwargs,
        )
        for bundle_path, summary in members:
            print(_bundle_line(bundle_path, summary))
        print(f"experiment: {manifest_path} members={len(members)}")
        all_succeeded = all(
            summary.status == RunStatus.SUCCEEDED for _, summary in members
        )
        return 0 if all_succeeded else 3
    if frozen_cooldown_anchor is not None:
        raise SchemaError(
            "--frozen-cooldown-anchor-json requires workload_profile.repetitions > 1"
        )
    bundle_path, summary = run_benchmark(
        config,
        Path(args.runs_dir),
        clock,
        instrument_calibration_dir=(
            Path(args.instrument_calibration_dir)
            if args.instrument_calibration_dir is not None
            else None
        ),
        instrument_power_policy=args.instrument_power_policy,
        post_window_sampling_dwell_s=post_window_sampling_dwell_s,
    )
    print(_bundle_line(bundle_path, summary))
    return 0 if summary.status == RunStatus.SUCCEEDED else 3


# ---------------------------------------------------------------------------
# validate-bundle verb (Slice 2E) - the checks live in the shared read layer
# (BundleReader.problems, D-025); this importable wrapper is kept so CI now and
# Phase 5 dataset publication later reuse it without the CLI shell.


def validate_bundle(path: Path, strict: bool = False) -> list[str]:
    """Return a list of problems with the bundle at ``path``.

    An empty list means the bundle is valid. Performs every check (no
    short-circuit) so a single invocation reports all problems. The default
    checks are structural, via
    :meth:`joulewise.bundle_read.BundleReader.problems` (D-025).

    ``strict=True`` (D-030) adds analysis-grade checks for ``succeeded``
    bundles: the measured window and summed curve must be
    reducer-consumable, and ``summary_metrics.json`` must match a fresh
    re-reduction of the raw artifacts - so a bundle whose summary no longer
    follows from its evidence cannot be blessed into a dataset. Strict mode
    lives here (not in the reader) because it composes the reader with the
    reducer, which itself consumes the reader.
    """
    reader = BundleReader(Path(path))
    problems = reader.problems()
    if strict:
        problems.extend(_strict_problems(reader))
    return problems


def _strict_problems(reader: BundleReader) -> list[str]:
    """The D-030 analysis-grade checks; applies only to succeeded bundles.

    Failed/unsupported summaries are controller-written from partial
    evidence, and incomplete bundles already fail structurally, so a fresh
    reduction is only comparable when the summary claims success.
    """
    raw_config = reader.raw_config()
    metadata = reader.raw_metadata()
    summary = reader.raw_summary()
    axi_selected = (
        isinstance(raw_config, dict)
        and raw_config.get("schema_extensions")
        == ["joulewise.axi_decode_config.v1"]
    ) or (
        isinstance(metadata, dict)
        and metadata.get("event_semantics_version") == "joulewise.events.v2"
    ) or (
        isinstance(summary, dict)
        and isinstance(summary.get("summary_provenance"), dict)
        and isinstance(summary["summary_provenance"].get("reducer_version"), str)
        and summary["summary_provenance"]["reducer_version"]
        in AXI_REDUCER_VERSIONS
    )
    if axi_selected:
        # Event-v2 evidence is validated completely before reducer
        # interpretation. Only a clean evidence gate may reach the 0.6.0
        # derivation comparison.
        axi_problems = axi_v2_validation_problems(reader)
        if axi_problems:
            return axi_problems
        if (
            not isinstance(summary, dict)
            or summary.get("status") != RunStatus.SUCCEEDED.value
        ):
            return []
        recorded_axi_version = (
            summary["summary_provenance"].get("reducer_version")
            if isinstance(summary.get("summary_provenance"), dict)
            else None
        )
        comparison_axi_version = (
            recorded_axi_version
            if recorded_axi_version in AXI_REDUCER_VERSIONS
            else AXI_REDUCER_VERSION
        )
        try:
            fresh = reduce_bundle(
                reader.path,
                reducer_version=comparison_axi_version,
            ).to_dict()
        except (ValueError, SchemaError) as exc:
            return [
                f"axi:event_semantics_invalid: strict reducer {comparison_axi_version} "
                f"dispatch failed: {exc}"
            ]
        differing = _strict_summary_differences(fresh, summary)
        if differing:
            return [
                "axi:event_semantics_invalid: summary_metrics.json does not "
                f"match a fresh {comparison_axi_version} "
                "re-reduction of event-v2 evidence (differing keys: "
                + ", ".join(differing)
                + ")"
            ]
        return []
    if not isinstance(summary, dict) or summary.get("status") != RunStatus.SUCCEEDED.value:
        return []
    problems: list[str] = []
    try:
        window = reader.measured_window()
    except BundleReadError as exc:
        return [f"strict: {exc}"]
    if window is None:
        return ["strict: succeeded bundle has no measured window in events.jsonl"]
    try:
        curve = reader.summed_curve()
    except BundleReadError as exc:
        problems.append(f"strict: {exc}")
        return problems
    if window.duration_s <= 0:
        # P2-040 FIX-1 (ARC-3): independent of the fresh-summary comparison, a
        # succeeded bundle over a nonpositive measured window is never
        # strict-valid.
        problems.append(
            "strict: succeeded bundle measured window duration must be > 0 s; "
            f"got {window.duration_s}"
        )
    else:
        in_window = sum(
            1
            for point in curve
            if (
                point.support_start_s is not None
                and point.support_end_s is not None
                and min(window.end_s, point.support_end_s)
                > max(window.start_s, point.support_start_s)
            )
            or (
                point.support_start_s is None
                and window.start_s <= point.t <= window.end_s
            )
        )
        if in_window < 2:
            problems.append(
                f"strict: only {in_window} summed power sample(s) inside the "
                "measured window; a succeeded summary needs a "
                "reducer-consumable curve"
            )
    (
        version_problems,
        absent_tolerance,
        tolerate_fresh_nulls,
        comparison_reducer_version,
    ) = (
        _strict_reducer_version_dispatch(reader, summary)
    )
    problems.extend(version_problems)
    stored_idle_problems = _strict_idle_mean_uncertainty_problems(summary)
    problems.extend(stored_idle_problems)
    problems.extend(_strict_workload_provenance_problems(reader, summary))
    problems.extend(_strict_realized_output_problems(reader))
    problems.extend(_strict_budgeted_suite_prompt_count_problems(reader))
    problems.extend(_strict_uncertainty_evidence_problems(reader))
    problems.extend(_strict_raw_to_trace_problems(reader))
    problems.extend(_strict_rich_telemetry_problems(reader))
    # A schema-invalid stored summary is already rejected structurally.  Do
    # not add a second derivation-drift diagnosis for the same malformed
    # object; semantic re-reduction remains applicable to valid summaries.
    if not version_problems and not summary_validation_problems(summary):
        fresh = (
            reduce_bundle(
                reader.path,
                reducer_version=SUMMARY_REDUCER_VERSION,
            ).to_dict()
            if comparison_reducer_version is None
            else reduce_bundle(
                reader.path,
                reducer_version=comparison_reducer_version,
            ).to_dict()
        )
        # The fresh current derivation is the raw/metadata authority. Inspect it
        # before legacy additive-absence projection can hide the governed
        # object, while retaining the stored-summary check for unsupported
        # versions and tampered current-era summaries.  Exact diagnostics are
        # de-duplicated when both views independently report the mismatch.
        for problem in _strict_idle_mean_uncertainty_problems(fresh):
            if problem not in problems:
                problems.append(problem)
        differing = _strict_summary_differences(
            fresh,
            summary,
            absent_tolerance=absent_tolerance,
            tolerate_fresh_nulls=tolerate_fresh_nulls,
        )
        if differing:
            problems.append(
                "strict: summary_metrics.json does not match a fresh re-reduction "
                f"of the raw artifacts (differing keys: {', '.join(differing)})"
            )
    return problems


_STRICT_ADDITIVE_ABSENT_TOLERANCE = {
    "window_evidence_precheck",
    # P2-040 FIX-3: joint interpolation bound is additive over pre-0.3.0
    # summaries.
    "energy_bound_terms_j.E_interpolation_joint_edge_bound_j",
    "energy_bound_terms_j",
    "energy_uncertainty_status",
    "energy_variance_terms_j2",
    "idle_baseline.gpu_idle_ratio_mean",
    "idle_baseline.gpu_idle_ratio_min",
    "idle_baseline.gpu_freq_hz_mean",
    "idle_baseline.idle_window_suspect",
    "measurement_quality.idle_window_suspect",
}

# WO-007 landed additively within the already-live reducer-0.5.0 era. Stored
# pre-repair 0.5.0 summaries remain distinguishable by this field's absence;
# when present, normal recursive strict comparison still checks its value.
ADDED_DURING_0_5_0 = frozenset({"idle_baseline.gpu_freq_mhz_mean"})

# D-078: fields minted by reducer 0.5.1 (anchor-shift envelopes). A stored
# summary labelled 0.5.0 that carries any of these relabelled itself out of
# the frozen point-anchor arm and is rejected.
ADDED_SINCE_0_5_0 = frozenset(
    {
        "energy_anchor_shift_envelopes",
        "energy_bound_terms_j.E_clock_anchor_shift_bound_j",
    }
)

ADDED_SINCE_0_3_0 = frozenset(
    {
        "measurement_quality.remote_cleanup_failed",
        "measurement_quality.runtime_cleanup_ok",
    }
)

ADDED_SINCE_0_4_1 = frozenset({"inter_token_throughput_tokens_s"})

_STRICT_LEGACY_ADDITIVE_ABSENT_TOLERANCE = (
    _STRICT_ADDITIVE_ABSENT_TOLERANCE
    | ADDED_SINCE_0_3_0
    | ADDED_SINCE_0_4_1
    | ADDED_DURING_0_5_0
    | {
        "idle_mean_uncertainty",
        "measurement_quality.token_counts_source",
        "measurement_quality.phase_identifiability",
    }
)


def _strict_idle_mean_uncertainty_problems(
    summary: dict[str, Any],
) -> list[str]:
    uncertainty = summary.get("idle_mean_uncertainty")
    if not isinstance(uncertainty, dict):
        return []
    reasons = uncertainty.get("reason_codes")
    if isinstance(reasons, list) and "idle_metadata_mismatch" in reasons:
        return [
            "strict: raw idle trace does not match metadata.idle_baseline "
            "(idle_metadata_mismatch)"
        ]
    return []


def _strict_summary_differences(
    fresh: Any,
    stored: Any,
    path: str = "",
    *,
    absent_tolerance: set[str] | None = None,
    tolerate_fresh_nulls: bool = False,
) -> list[str]:
    """Compare fresh vs stored summaries with legacy-additive null tolerance.

    A freshly emitted key that is absent from a legacy stored summary is
    tolerated only when the fresh value is ``None``. Stored keys, including
    stored extras, remain exact claims and must match the fresh reduction.
    """
    if absent_tolerance is None:
        absent_tolerance = set()
    if isinstance(fresh, dict) and isinstance(stored, dict):
        differences: list[str] = []
        for key in sorted(set(fresh) | set(stored)):
            child = f"{path}.{key}" if path else str(key)
            if key not in stored:
                if child == "summary_provenance" and tolerate_fresh_nulls:
                    continue
                if child in absent_tolerance:
                    continue
                # P2-040 FIX-3: nested joint-interpolation fields are additive
                # for pre-0.3.0 summaries at every (dynamic) precheck path.
                if (
                    tolerate_fresh_nulls
                    and child.endswith(".interpolation_joint_edge_bound_j")
                ):
                    continue
                if not tolerate_fresh_nulls or fresh[key] is not None:
                    differences.append(child)
                continue
            if key not in fresh:
                differences.append(child)
                continue
            differences.extend(
                _strict_summary_differences(
                    fresh[key],
                    stored[key],
                    child,
                    absent_tolerance=absent_tolerance,
                    tolerate_fresh_nulls=tolerate_fresh_nulls,
                )
            )
        return differences
    if fresh != stored:
        return [path or "<summary>"]
    return []


def _strict_workload_provenance_problems(
    reader: BundleReader, summary: dict[str, Any]
) -> list[str]:
    metadata = reader.raw_metadata()
    legacy = _strict_legacy_bundle_metadata(metadata)
    if not isinstance(metadata, dict):
        return ["strict: metadata.workload_provenance is missing"]
    workload = metadata.get("workload_provenance")
    if legacy and not isinstance(workload, dict):
        return []
    if not isinstance(workload, dict):
        return ["strict: metadata.workload_provenance is missing or not an object"]

    problems: list[str] = []
    prompt = workload.get("prompt")
    if not isinstance(prompt, dict):
        problems.append("strict: metadata.workload_provenance.prompt is missing or not an object")
    else:
        missing = [
            key
            for key in (
                "realized_token_count",
                "token_hash_domain",
                "token_ids_sha256",
                "text_sha256",
            )
            if key not in prompt
        ]
        if missing:
            problems.append(
                "strict: metadata.workload_provenance.prompt is missing "
                f"required key(s): {', '.join(missing)}"
            )
        realized_token_count = prompt.get("realized_token_count")
        if realized_token_count is not None and not _is_positive_int(
            realized_token_count
        ):
            problems.append(
                "strict: metadata.workload_provenance.prompt.realized_token_count "
                "is not null or a positive integer"
            )
        token_hash = prompt.get("token_ids_sha256")
        if not _is_sha256_hex(token_hash):
            problems.append(
                "strict: metadata.workload_provenance.prompt.token_ids_sha256 "
                "is missing or not a lowercase SHA-256 hex string"
            )
        domain = prompt.get("token_hash_domain")
        expected_domain = (
            _SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN
            if isinstance(metadata.get("suite"), dict)
            else _PROMPT_TOKEN_IDS_HASH_DOMAIN
        )
        if domain != expected_domain:
            problems.append(
                "strict: metadata.workload_provenance.prompt.token_hash_domain "
                f"is not {expected_domain!r}"
            )
        if isinstance(metadata.get("suite"), dict):
            expected_rollup, rollup_problems = _strict_suite_prompt_rollup(reader)
            problems.extend(rollup_problems)
            if expected_rollup is not None:
                expected_hash = expected_rollup["token_ids_sha256"]
                expected_count = expected_rollup["realized_token_count"]
                if token_hash != expected_hash:
                    problems.append(
                        "strict: metadata.workload_provenance.prompt.token_ids_sha256 "
                        "does not match outputs/suite_items.jsonl rollup: "
                        f"metadata has {token_hash!r}, recomputed has {expected_hash!r}"
                    )
                if realized_token_count != expected_count:
                    problems.append(
                        "strict: metadata.workload_provenance.prompt.realized_token_count "
                        "does not match outputs/suite_items.jsonl rollup: "
                        f"metadata has {realized_token_count!r}, "
                        f"recomputed has {expected_count!r}"
                    )
        text_hash = prompt.get("text_sha256")
        if text_hash is not None and not _is_sha256_hex(text_hash):
            problems.append(
                "strict: metadata.workload_provenance.prompt.text_sha256 "
                "is not null or a lowercase SHA-256 hex string"
            )
    problems.extend(
        _strict_required_object_keys(
            workload,
            "generator",
            ("name", "version"),
        )
    )
    problems.extend(
        _strict_required_object_keys(
            workload,
            "tokenizer",
            ("backend", "identifier", "revision", "class", "vocab_size"),
        )
    )
    tokenizer = workload.get("tokenizer")
    if isinstance(tokenizer, dict):
        vocab_size = tokenizer.get("vocab_size")
        if vocab_size is not None and not _is_positive_int(vocab_size):
            problems.append(
                "strict: metadata.workload_provenance.tokenizer.vocab_size "
                "is not null or a positive integer"
            )
    problems.extend(
        _strict_required_object_keys(
            workload,
            "model",
            ("source", "revision"),
        )
    )
    problems.extend(
        _strict_required_object_keys(
            workload,
            "output_policy",
            ("name", "requested_tokens", "emitted_tokens", "stop_condition"),
        )
    )
    return problems


def _strict_reducer_version_dispatch(
    reader: BundleReader, summary: dict[str, Any]
) -> tuple[list[str], set[str], bool, str | None]:
    """Select strict comparison semantics solely from recorded provenance."""
    provenance = summary.get("summary_provenance")
    if (
        _strict_legacy_bundle_metadata(reader.raw_metadata())
        and "summary_provenance" not in summary
    ):
        return [], _STRICT_LEGACY_ADDITIVE_ABSENT_TOLERANCE, True, None
    if not isinstance(provenance, dict):
        return [
            "strict: summary_metrics.summary_provenance is missing or not an "
            "object for current-era bundle"
        ], set(), False, None
    reducer_version = provenance.get("reducer_version")
    if reducer_version == SUMMARY_REDUCER_VERSION:
        return [], set(ADDED_DURING_0_5_0), False, None
    if reducer_version == "0.5.1":
        return [], set(ADDED_DURING_0_5_0), False, "0.5.1"
    frozen_absence: set[str]
    relabel_markers: set[str]
    if reducer_version == "0.5.0":
        # D-078 frozen point-anchor arm: replayed byte-identically. The
        # gpu_freq_mhz_mean field legitimately appears within the 0.5.0 era
        # (WO-007), so only the 0.5.1-minted fields mark a relabel.
        frozen_absence = set(ADDED_DURING_0_5_0)
        relabel_markers = set(ADDED_SINCE_0_5_0)
    elif reducer_version == "0.4.2":
        frozen_absence = set(ADDED_DURING_0_5_0)
        relabel_markers = frozen_absence | ADDED_SINCE_0_5_0
    elif reducer_version == "0.4.1":
        frozen_absence = set(ADDED_SINCE_0_4_1 | ADDED_DURING_0_5_0)
        relabel_markers = frozen_absence | ADDED_SINCE_0_5_0
    else:
        return _unsupported_reducer_version_problems(reducer_version), set(), False, None
    # A current summary cannot opt into a frozen arm by changing only its
    # version label. Authentic frozen shapes predate these additive fields.
    if any(_summary_path_present(summary, path) for path in relabel_markers):
        return _unsupported_reducer_version_problems(reducer_version), set(), False, None
    return [], frozen_absence, False, reducer_version


def _unsupported_reducer_version_problems(reducer_version: Any) -> list[str]:
    return [
        "strict: unsupported reducer version; re-reduction required",
        "strict: unsupported reducer version "
        f"{reducer_version!r} for current-era bundle; superseded versions "
        "cannot claim the current inter_token_throughput_tokens_s reduction "
        f"shape and explicit re-reduction with {SUMMARY_REDUCER_VERSION} is "
        "required",
    ]


def _summary_path_present(summary: dict[str, Any], path: str) -> bool:
    current: Any = summary
    for component in path.split("."):
        if not isinstance(current, dict) or component not in current:
            return False
        current = current[component]
    return True


def _strict_legacy_bundle_metadata(metadata: Any) -> bool:
    if not isinstance(metadata, dict):
        return False
    return (
        metadata.get("run_id"),
        metadata.get("config_sha256"),
    ) in _STRICT_LEGACY_BUNDLE_IDENTITIES


def _strict_suite_prompt_rollup(
    reader: BundleReader,
) -> tuple[dict[str, Any] | None, list[str]]:
    path = reader.path / "outputs" / "suite_items.jsonl"
    if not path.is_file():
        return None, ["strict: outputs/suite_items.jsonl is missing for suite rollup"]
    try:
        text = path.read_text()
    except OSError as exc:
        return None, [f"strict: outputs/suite_items.jsonl cannot be read: {exc}"]
    prompt_hashes: list[str] = []
    total_tokens = 0
    problems: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(
                f"strict: outputs/suite_items.jsonl line {index} is not valid JSON: {exc}"
            )
            continue
        if not isinstance(record, dict):
            problems.append(
                f"strict: outputs/suite_items.jsonl line {index} is not a JSON object"
            )
            continue
        prompt = record.get("prompt")
        token_hash = prompt.get("token_ids_sha256") if isinstance(prompt, dict) else None
        if not _is_sha256_hex(token_hash):
            problems.append(
                "strict: outputs/suite_items.jsonl line "
                f"{index} prompt.token_ids_sha256 is missing or not a lowercase "
                "SHA-256 hex string"
            )
            continue
        prompt_tokens = record.get("prompt_tokens")
        if not _is_nonnegative_int(prompt_tokens):
            problems.append(
                f"strict: outputs/suite_items.jsonl line {index} prompt_tokens "
                "is not a non-negative integer"
            )
            continue
        prompt_hashes.append(token_hash)
        total_tokens += prompt_tokens
    if problems:
        return None, problems
    return suite_prompt_rollup(prompt_hashes, total_tokens), []


def _strict_emitted_token_ids_problems(reader: BundleReader) -> list[str]:
    problems: list[str] = []
    metadata = reader.raw_metadata()
    if isinstance(metadata, dict):
        workload = metadata.get("workload_provenance")
        if isinstance(workload, dict):
            response = workload.get("response")
            output_policy = workload.get("output_policy")
            emitted_tokens = (
                output_policy.get("emitted_tokens")
                if isinstance(output_policy, dict)
                else None
            )
            if isinstance(response, dict) and "emitted_token_ids" in response:
                emitted_token_ids = response.get("emitted_token_ids")
                problems.extend(
                    _strict_emitted_token_ids_length_problems(
                        emitted_token_ids,
                        emitted_tokens,
                        "metadata.workload_provenance.response",
                    )
                )

    for line_index, record in _strict_suite_item_records(reader):
        if "emitted_token_ids" not in record:
            continue
        problems.extend(
            _strict_emitted_token_ids_length_problems(
                record.get("emitted_token_ids"),
                record.get("emitted_tokens"),
                f"outputs/suite_items.jsonl line {line_index}",
            )
        )
    return problems


def _strict_realized_output_problems(reader: BundleReader) -> list[str]:
    """Validate the designated realized-output fields against raw evidence."""

    metadata = reader.raw_metadata()
    if _strict_legacy_bundle_metadata(metadata):
        # Frozen pre-D-033 single-run bundles keep structural compatibility.
        # They have no designated output-policy record and therefore gain no
        # exact/replay/ratio eligibility from this exemption.
        return []
    if not isinstance(metadata, dict):
        return ["strict: realized output evidence: metadata.json is missing or invalid"]
    workload = metadata.get("workload_provenance")
    observed = metadata.get("workload_observed")
    policy = workload.get("output_policy") if isinstance(workload, dict) else None
    if not isinstance(policy, dict) or not isinstance(observed, dict):
        return ["strict: realized output evidence is missing"]

    problems: list[str] = []
    emitted = policy.get("emitted_tokens")
    requested = policy.get("requested_tokens")
    observed_emitted = observed.get("output_token_count")
    stop = policy.get("stop_condition")
    name = policy.get("name")
    generator = workload.get("generator") if isinstance(workload, dict) else None
    is_mlx_single = (
        not isinstance(metadata.get("suite"), dict)
        and isinstance(generator, dict)
        and generator.get("name") == "mlx_lm.stream_generate"
    )
    if not _is_nonnegative_int(emitted):
        problems.append(
            "strict: metadata.workload_provenance.output_policy.emitted_tokens "
            "is not a non-negative integer"
        )
    if not _is_positive_int(requested):
        problems.append(
            "strict: metadata.workload_provenance.output_policy.requested_tokens "
            "is not a positive integer"
        )
    if not isinstance(stop, str) or not stop:
        problems.append(
            "strict: metadata.workload_provenance.output_policy.stop_condition "
            "is not a non-empty string"
        )
    if isinstance(metadata.get("suite"), dict):
        try:
            records = reader.suite_item_records()
        except BundleReadError as exc:
            return problems + [f"strict: realized suite output evidence: {exc}"]
        if records is None:
            return problems + ["strict: realized suite output evidence is missing"]
        # The suite aggregate stop is compatibility metadata only. Realized
        # stop evidence remains on every suite item and is validated by the
        # BundleReader structural path.
        return problems + _strict_emitted_token_ids_problems(reader)

    if observed_emitted != emitted:
        problems.append(
            "strict: metadata.workload_observed.output_token_count does not match "
            "metadata.workload_provenance.output_policy.emitted_tokens"
        )

    raw_config = reader.raw_config()
    workload_config = (
        raw_config.get("workload_profile") if isinstance(raw_config, dict) else None
    )
    configured_requested = (
        workload_config.get("output_tokens")
        if isinstance(workload_config, dict)
        else None
    )
    if (
        is_mlx_single
        and configured_requested is not None
        and requested != configured_requested
    ):
        problems.append(
            "strict: metadata.workload_provenance.output_policy.requested_tokens "
            "does not match config.workload_profile.output_tokens"
        )

    if is_mlx_single and name in {FIXED_BUDGET_EXACT, FIXED_BUDGET_INCOMPLETE}:
        if emitted != requested:
            problems.append(
                "strict: single fixed-budget run emitted_tokens does not equal "
                "requested_tokens"
            )
        if name != FIXED_BUDGET_EXACT or stop != "requested_tokens_emitted":
            problems.append(
                "strict: single fixed-budget run lacks a realized exact stop"
            )
        token_rows, token_row_problems = _strict_jsonl_object_count(
            reader.path / "outputs" / "tokens.jsonl",
            "outputs/tokens.jsonl",
        )
        problems.extend(token_row_problems)
        if _is_nonnegative_int(emitted) and token_rows != emitted:
            problems.append(
                f"strict: outputs/tokens.jsonl row count {token_rows} does not "
                f"equal emitted_tokens {emitted}"
            )
        try:
            event_count = len(reader.token_timestamps())
        except BundleReadError as exc:
            problems.append(f"strict: realized output token events: {exc}")
        else:
            if _is_nonnegative_int(emitted) and event_count != emitted:
                problems.append(
                    f"strict: decode token-event count {event_count} does not equal "
                    f"emitted_tokens {emitted}"
                )
        response = workload.get("response") if isinstance(workload, dict) else None
        if not isinstance(response, dict) or "emitted_token_ids" not in response:
            problems.append(
                "strict: metadata.workload_provenance.response.emitted_token_ids "
                "is required for single fixed-budget output evidence"
            )

    return problems + _strict_emitted_token_ids_problems(reader)


def _strict_jsonl_object_count(path: Path, label: str) -> tuple[int, list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return 0, [f"strict: {label} cannot be read: {exc}"]
    count = 0
    problems: list[str] = []
    for line_index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        count += 1
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(
                f"strict: {label} line {line_index} is not valid JSON: {exc}"
            )
            continue
        if not isinstance(value, dict):
            problems.append(f"strict: {label} line {line_index} is not a JSON object")
    return count, problems


def _strict_emitted_token_ids_length_problems(
    emitted_token_ids: Any,
    emitted_tokens: Any,
    path: str,
) -> list[str]:
    if not isinstance(emitted_token_ids, list):
        return [f"strict: {path}.emitted_token_ids is present but not a list"]
    if not _is_nonnegative_int(emitted_tokens):
        return [
            f"strict: {path}.emitted_tokens is not a non-negative integer for "
            "emitted_token_ids validation"
        ]
    if len(emitted_token_ids) != emitted_tokens:
        return [
            f"strict: {path}.emitted_token_ids length {len(emitted_token_ids)} "
            f"does not equal emitted_tokens {emitted_tokens}"
        ]
    return []


def _strict_budgeted_suite_prompt_count_problems(reader: BundleReader) -> list[str]:
    try:
        manifest = reader.suite_manifest()
    except BundleReadError as exc:
        return [f"strict: {exc}"]
    if manifest is None:
        return []
    plan_class = suite_prompt_plan_class(
        manifest.suite_id,
        manifest.suite_profile,
        manifest.source_manifest.source_id,
    )
    if plan_class != "budgeted":
        return []
    problems: list[str] = []
    records = {
        record.get("item_index"): record
        for _, record in _strict_suite_item_records(reader)
        if _is_nonnegative_int(record.get("item_index"))
    }
    for item_index, item in enumerate(manifest.items):
        if item.source.prompt_text is None:
            continue
        record = records.get(item_index)
        if not isinstance(record, dict) or record.get("status") != "succeeded":
            continue
        realized = record.get("prompt_tokens")
        planned = item.shape.planned_prompt_tokens
        if realized != planned:
            problems.append(
                "strict: outputs/suite_items.jsonl item_index "
                f"{item_index} planned_prompt_tokens_mismatch: "
                f"planned_prompt_tokens {planned}, realized_prompt_tokens {realized}"
            )
    return problems


def _strict_suite_item_records(reader: BundleReader) -> list[tuple[int, dict[str, Any]]]:
    return _tolerant_jsonl_object_records(
        reader.path / "outputs" / "suite_items.jsonl"
    )


def _strict_required_object_keys(
    workload: dict[str, Any], block_name: str, required_keys: tuple[str, ...]
) -> list[str]:
    block = workload.get(block_name)
    path = f"metadata.workload_provenance.{block_name}"
    if not isinstance(block, dict):
        return [f"strict: {path} is missing or not an object"]
    missing = [key for key in required_keys if key not in block]
    if not missing:
        return []
    return [
        f"strict: {path} is missing required key(s): {', '.join(missing)}"
    ]


RawToTraceVerifier = Callable[[BundleReader], list[str]]


def _strict_uncertainty_evidence_problems(reader: BundleReader) -> list[str]:
    """Re-derive P2-038 evidence for current-era successful powermetrics runs."""

    if _validated_config_telemetry_backend(reader) != TelemetryBackend.POWERMETRICS:
        return []
    metadata = reader.raw_metadata()
    if _strict_legacy_bundle_metadata(metadata):
        return []
    if not isinstance(metadata, dict):
        return ["strict: uncertainty evidence: metadata.json is missing or invalid"]
    evidence = metadata.get("uncertainty_evidence")
    if not isinstance(evidence, dict):
        return [
            "strict: uncertainty evidence: metadata.uncertainty_evidence is "
            "missing for current-era powermetrics bundle"
        ]
    problems: list[str] = []
    schema_version = evidence.get("schema_version")
    if schema_version not in {P2038_SCHEMA_VERSION, P2038_SCHEMA_VERSION_V2}:
        problems.append(
            "strict: uncertainty evidence: unsupported or missing schema_version"
        )
    if evidence.get("telemetry_backend") != "powermetrics":
        problems.append(
            "strict: uncertainty evidence: telemetry_backend must be 'powermetrics'"
        )
    clock_anchor = evidence.get("clock_anchor")
    sample_phase = evidence.get("sample_phase")
    raw_path = reader.path / "raw" / RAW_SAMPLES_NAME
    if not isinstance(clock_anchor, dict) or not isinstance(sample_phase, dict):
        return problems + [
            "strict: uncertainty evidence: clock_anchor and sample_phase must be objects"
        ]
    stamp_rows = clock_anchor.get("clock_stamps")
    if not isinstance(stamp_rows, dict):
        return problems + [
            "strict: uncertainty evidence: clock_anchor.clock_stamps is missing"
        ]
    try:
        stamps = {
            name: stamp_from_mapping(value)
            for name, value in stamp_rows.items()
            if isinstance(value, dict)
        }
        raw_records = parse_powermetrics_records(raw_path.read_bytes())
        if schema_version == P2038_SCHEMA_VERSION_V2:
            expected, _point = derive_powermetrics_clock_evidence_v2(
                stamps=stamps,
                records=anchor_records_from_powermetrics(raw_records),
            )
        else:
            # Exact dispatch for stored p2-038.1 evidence (D-078): the frozen
            # spawn-bracket derivation is replayed, never re-derived as v2.
            expected, _point = derive_powermetrics_clock_evidence(
                stamps=stamps,
                elapsed_s=[
                    record.elapsed_ns / 1_000_000_000.0 for record in raw_records
                ],
                plist_timestamp_s=[
                    float(record.metadata["plist_timestamp_s"])
                    for record in raw_records
                ],
            )
    except (KeyError, OSError, TypeError, ValueError) as exc:
        return problems + [
            f"strict: uncertainty evidence: cannot re-derive clock evidence: {exc}"
        ]
    expected_anchor = expected["clock_anchor"]
    if (
        schema_version == P2038_SCHEMA_VERSION_V2
        and isinstance(expected_anchor, dict)
        and expected_anchor.get("status") != "bounded"
        and raw_records
    ):
        # Replay the adapter's deterministic structural fallback so stored
        # unresolved evidence remains byte-verifiable.
        endpoint_s, method = trace_fallback_endpoint(stamps, raw_records)
        expected_anchor["trace_fallback_endpoint_epoch_s"] = endpoint_s
        expected_anchor["trace_fallback_method"] = method
    if clock_anchor != expected["clock_anchor"]:
        problems.append(
            "strict: uncertainty evidence: clock_anchor does not match paired-clock/raw-plist derivation"
        )
    if sample_phase != expected["sample_phase"]:
        problems.append(
            "strict: uncertainty evidence: sample_phase does not match paired-clock/raw-plist derivation"
        )
    events = _tolerant_jsonl_object_records(reader.path / "events.jsonl")
    marker_epochs: dict[str, float] = {}
    for _line, event in events:
        event_type = event.get("event_type")
        if event_type in {"sampling_started", "sampling_stopped"}:
            try:
                marker_epochs[str(event_type)] = finite_float(
                    event.get("timestamp_s"), f"events.{event_type}.timestamp_s"
                )
            except ValueError as exc:
                problems.append(f"strict: uncertainty evidence: {exc}")
    if sample_phase.get("status") == "bounded":
        for event_type, field in (
            ("sampling_started", "sampling_started_epoch_s"),
            ("sampling_stopped", "sampling_stopped_epoch_s"),
        ):
            if marker_epochs.get(event_type) != sample_phase.get(field):
                problems.append(
                    f"strict: uncertainty evidence: {field} does not match events.jsonl"
                )

    _strict_uncertainty_scalar(
        problems,
        metadata,
        "clock_anchor_bound_s",
        clock_anchor,
        "effective_clock_anchor_bound_s",
    )
    _strict_uncertainty_scalar(
        problems,
        metadata,
        "marker_to_first_sample_phase_bound_s",
        sample_phase,
        "marker_to_first_sample_phase_bound_s",
    )
    _strict_uncertainty_scalar(
        problems,
        metadata,
        "marker_to_last_sample_phase_bound_s",
        sample_phase,
        "marker_to_last_sample_phase_bound_s",
    )

    idle = evidence.get("idle_drift")
    guard = evidence.get("idle_drift_guard")
    if not isinstance(idle, dict) or not isinstance(guard, dict):
        problems.append(
            "strict: uncertainty evidence: idle_drift and separate idle_drift_guard must be objects"
        )
        return problems
    pre_path = reader.path / "raw" / RAW_IDLE_NAME
    post_path = reader.path / "raw" / RAW_IDLE_POST_NAME
    if post_path.is_file() and pre_path.is_file():
        try:
            pre_data = pre_path.read_bytes()
            post_data = post_path.read_bytes()
            pre_records = parse_powermetrics_records(pre_data)
            post_records = parse_powermetrics_records(post_data)
            idle_baseline = metadata.get("idle_baseline")
            if not isinstance(idle_baseline, dict):
                raise ValueError("metadata.idle_baseline is missing")
            pre_mean = finite_float(
                idle_baseline.get("power_w_mean"),
                "metadata.idle_baseline.power_w_mean",
            )
            pre_quality = idle_window_gpu_quality(decode_rich_telemetry(pre_data))
            post_quality = idle_window_gpu_quality(decode_rich_telemetry(post_data))
            expected_idle, expected_guard, expected_bound = derive_idle_drift_evidence(
                pre_power_w=[record.combined_power_w for record in pre_records],
                post_power_w=[record.combined_power_w for record in post_records],
                pre_power_w_mean=pre_mean,
                pre_idle_window_suspect=pre_quality["idle_window_suspect"],
                post_idle_window_suspect=post_quality["idle_window_suspect"],
                calibration_guard=guard,
            )
        except (OSError, TypeError, ValueError) as exc:
            problems.append(
                f"strict: uncertainty evidence: cannot re-derive idle drift: {exc}"
            )
        else:
            if idle != expected_idle:
                problems.append(
                    "strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation"
                )
            if guard != expected_guard:
                problems.append(
                    "strict: uncertainty evidence: idle_drift_guard does not match recorded guard provenance"
                )
            if metadata.get("idle_drift_bound_w") != expected_bound:
                problems.append(
                    "strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation"
                )
    elif idle != {"status": "unknown", "reason": "post_idle_unavailable"}:
        problems.append(
            "strict: uncertainty evidence: missing post-idle raw artifact is not recorded as post_idle_unavailable"
        )
    elif "idle_drift_bound_w" in metadata:
        problems.append(
            "strict: uncertainty evidence: unknown idle drift must omit idle_drift_bound_w"
        )

    extra = metadata.get("extra")
    if isinstance(extra, dict):
        for key in ("clock_anchor_bound_s", "idle_drift_bound_w"):
            if key in extra and key in metadata:
                problems.append(
                    f"strict: uncertainty evidence: metadata.extra.{key} cannot override controller evidence"
                )
    return problems


def _strict_uncertainty_scalar(
    problems: list[str],
    metadata: dict[str, Any],
    top_key: str,
    component: dict[str, Any],
    derived_key: str,
) -> None:
    if component.get("status") == "bounded":
        if metadata.get(top_key) != component.get(derived_key):
            problems.append(
                f"strict: uncertainty evidence: metadata.{top_key} does not match derivation"
            )
    elif top_key in metadata:
        problems.append(
            f"strict: uncertainty evidence: unknown component must omit metadata.{top_key}"
        )


def _tolerant_jsonl_object_records(path: Path) -> list[tuple[int, dict[str, Any]]]:
    """Collect numbered JSON-object rows without hiding adjacent diagnostics."""

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    records: list[tuple[int, dict[str, Any]]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append((index, value))
    return records


def _strict_raw_to_trace_problems(reader: BundleReader) -> list[str]:
    telemetry_backend = _validated_config_telemetry_backend(reader)
    if telemetry_backend is None:
        return ["strict: raw-to-trace: telemetry backend is unavailable from config.json"]
    verifier = RAW_TO_TRACE_VERIFIERS.get(telemetry_backend)
    if verifier is not None:
        return verifier(reader)
    return [
        "strict: raw-to-trace: no verifier registered for production backend "
        f"{telemetry_backend.value}"
    ]


def _verify_powermetrics_raw_to_trace(reader: BundleReader) -> list[str]:
    raw_path = reader.path / "raw" / RAW_SAMPLES_NAME
    if not raw_path.is_file():
        return [f"strict: raw-to-trace: missing raw/{RAW_SAMPLES_NAME}"]
    metadata = reader.raw_metadata()
    if not isinstance(metadata, dict):
        return ["strict: raw-to-trace: metadata.json is missing or invalid"]
    try:
        if _strict_legacy_bundle_metadata(metadata):
            device = metadata.get("device")
            if not isinstance(device, dict):
                return [
                    "strict: raw-to-trace: metadata.device is missing or not an object"
                ]
            anchor_offset_s = finite_float(
                device.get("plist_anchor_offset_s"),
                "metadata.device.plist_anchor_offset_s",
            )
            expected = samples_from_raw_powermetrics(
                raw_path.read_bytes(),
                plist_anchor_offset_s=anchor_offset_s,
            )
            require_interval_support = False
        else:
            evidence = metadata.get("uncertainty_evidence")
            clock_anchor = (
                evidence.get("clock_anchor") if isinstance(evidence, dict) else None
            )
            if not isinstance(clock_anchor, dict):
                return [
                    "strict: raw-to-trace: current-era clock_anchor evidence is missing"
                ]
            point_s = _powermetrics_trace_endpoint_s(evidence, clock_anchor)
            expected = samples_from_raw_powermetrics(
                raw_path.read_bytes(),
                first_record_endpoint_s=point_s,
            )
            require_interval_support = True
    except (OSError, ValueError) as exc:
        return [f"strict: raw-to-trace: cannot derive raw/{RAW_SAMPLES_NAME}: {exc}"]
    return _compare_raw_derived_samples(
        reader, expected, require_interval_support=require_interval_support
    )


def _powermetrics_trace_endpoint_s(
    evidence: dict[str, Any], clock_anchor: dict[str, Any]
) -> float:
    """The record-0 window END the stored trace/rich telemetry must replay.

    Bounded evidence uses the anchor point. A p2-038.2 unresolved anchor
    (``clock_anchor_unresolved``) records the adapter's structural fallback
    endpoint instead; strict replays it exactly, and the claim barrier stays
    in the precheck, never here."""

    if (
        evidence.get("schema_version") == P2038_SCHEMA_VERSION_V2
        and clock_anchor.get("status") != "bounded"
    ):
        return finite_float(
            clock_anchor.get("trace_fallback_endpoint_epoch_s"),
            "metadata.uncertainty_evidence.clock_anchor.trace_fallback_endpoint_epoch_s",
        )
    return finite_float(
        clock_anchor.get("first_sample_end_point_epoch_s"),
        "metadata.uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s",
    )


def _strict_rich_telemetry_problems(reader: BundleReader) -> list[str]:
    """D-078: rich telemetry must move with the corrected anchor (p2-038.2).

    Stored p2-038.1 bundles keep their legacy native-date reconstruction and
    are not re-judged; p2-038.2 bundles must byte-match a re-derivation from
    the raw capture at the stored anchor endpoint."""

    if _validated_config_telemetry_backend(reader) != TelemetryBackend.POWERMETRICS:
        return []
    metadata = reader.raw_metadata()
    if not isinstance(metadata, dict) or _strict_legacy_bundle_metadata(metadata):
        return []
    evidence = metadata.get("uncertainty_evidence")
    if (
        not isinstance(evidence, dict)
        or evidence.get("schema_version") != P2038_SCHEMA_VERSION_V2
    ):
        return []
    clock_anchor = evidence.get("clock_anchor")
    if not isinstance(clock_anchor, dict):
        return []
    raw_path = reader.path / "raw" / RAW_SAMPLES_NAME
    rich_path = reader.path / RICH_TELEMETRY_NAME
    if not rich_path.is_file():
        device = metadata.get("device")
        if isinstance(device, dict) and device.get("rich_telemetry_error"):
            return []
        return [
            f"strict: rich-telemetry: missing {RICH_TELEMETRY_NAME} without a "
            "recorded rich_telemetry_error"
        ]
    try:
        point_s = _powermetrics_trace_endpoint_s(evidence, clock_anchor)
        expected = rich_telemetry_jsonl(
            raw_path.read_bytes(), first_record_endpoint_s=point_s
        )
    except (OSError, ValueError) as exc:
        return [f"strict: rich-telemetry: cannot re-derive {RICH_TELEMETRY_NAME}: {exc}"]
    try:
        stored = rich_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"strict: rich-telemetry: cannot read {RICH_TELEMETRY_NAME}: {exc}"]
    if stored != expected:
        return [
            f"strict: rich-telemetry: {RICH_TELEMETRY_NAME} does not match the "
            "anchor-corrected re-derivation from the raw capture"
        ]
    return []


def _verify_mock_raw_to_trace_exemption(reader: BundleReader) -> list[str]:
    """Explicit fixture-only exemption: mock telemetry has no native raw file."""

    del reader
    return []


def _verify_nvidia_smi_raw_to_trace(reader: BundleReader) -> list[str]:
    raw_path = reader.path / "raw" / NVIDIA_SMI_RAW_SAMPLES_NAME
    if not raw_path.is_file():
        return [
            "strict: raw-to-trace: nvidia_smi missing "
            f"raw/{NVIDIA_SMI_RAW_SAMPLES_NAME}"
        ]
    metadata = reader.raw_metadata()
    if not isinstance(metadata, dict):
        return ["strict: raw-to-trace: nvidia_smi metadata.json is missing or invalid"]
    adapters = metadata.get("adapters")
    telemetry = adapters.get("telemetry") if isinstance(adapters, dict) else None
    if not isinstance(telemetry, dict):
        return [
            "strict: raw-to-trace: nvidia_smi metadata.adapters.telemetry "
            "is missing or not an object"
        ]
    worker_metadata = telemetry.get("worker_metadata")
    if not isinstance(worker_metadata, dict):
        return [
            "strict: raw-to-trace: nvidia_smi telemetry worker_metadata "
            "is missing or not an object"
        ]
    try:
        node_utc_offset_s = finite_float(
            worker_metadata.get("node_utc_offset_s"),
            "metadata.adapters.telemetry.worker_metadata.node_utc_offset_s",
        )
    except ValueError as exc:
        return [f"strict: raw-to-trace: nvidia_smi {exc}"]
    alignments = telemetry.get("clock_alignments")
    stop_alignment = None
    if isinstance(alignments, list):
        stop_alignment = next(
            (
                item
                for item in reversed(alignments)
                if isinstance(item, dict)
                and item.get("stage") == "telemetry.stop_sampling"
            ),
            None,
        )
    if not isinstance(stop_alignment, dict):
        return [
            "strict: raw-to-trace: nvidia_smi telemetry.stop_sampling "
            "clock alignment is missing"
        ]
    try:
        offset_estimate_s = finite_float(
            stop_alignment.get("offset_estimate_s"),
            "metadata.adapters.telemetry.clock_alignments.stop_sampling.offset_estimate_s",
        )
        expected = samples_from_raw_nvidia_smi(
            raw_path.read_bytes(),
            node_utc_offset_s=node_utc_offset_s,
            offset_estimate_s=offset_estimate_s,
        )
    except (OSError, ValueError) as exc:
        return [
            "strict: raw-to-trace: nvidia_smi cannot derive "
            f"raw/{NVIDIA_SMI_RAW_SAMPLES_NAME}: {exc}"
        ]
    return _compare_raw_derived_samples(reader, expected, backend="nvidia_smi")


def _compare_raw_derived_samples(
    reader: BundleReader,
    expected: list[Any],
    *,
    backend: str | None = None,
    require_interval_support: bool = False,
) -> list[str]:
    prefix = f"{backend} " if backend else ""
    try:
        rows = reader.trace_rows()
    except BundleReadError as exc:
        return [f"strict: raw-to-trace: {prefix}{exc}"]
    if len(rows) != len(expected):
        return [
            f"strict: raw-to-trace: {prefix}power_trace.csv row count "
            f"{len(rows)} does not match raw-derived {len(expected)}"
        ]
    for index, (row, sample) in enumerate(zip(rows, expected), start=2):
        rail = row.get("rail") or ""
        try:
            timestamp_s = finite_float(
                row.get("timestamp_s"),
                f"power_trace.csv row {index} timestamp_s",
            )
            power_w = finite_float(
                row.get("power_w"),
                f"power_trace.csv row {index} power_w",
            )
        except ValueError as exc:
            return [f"strict: raw-to-trace: {exc}"]
        source = row.get("source") or ""
        expected_rail = sample.rail or ""
        if timestamp_s != sample.timestamp_s:
            return [
                f"strict: raw-to-trace: {prefix}power_trace.csv row "
                f"{index} rail {rail!r} timestamp_s {timestamp_s!r} "
                f"does not match raw-derived {sample.timestamp_s!r}"
            ]
        if power_w != sample.power_w:
            return [
                f"strict: raw-to-trace: {prefix}power_trace.csv row "
                f"{index} rail {rail!r} power_w {power_w!r} "
                f"does not match raw-derived {sample.power_w!r}"
            ]
        if source != sample.source:
            return [
                f"strict: raw-to-trace: {prefix}power_trace.csv row "
                f"{index} rail {rail!r} source {source!r} "
                f"does not match raw-derived {sample.source!r}"
            ]
        if rail != expected_rail:
            return [
                f"strict: raw-to-trace: {prefix}power_trace.csv row "
                f"{index} rail {rail!r} does not match raw-derived "
                f"{expected_rail!r}"
            ]
        if require_interval_support:
            try:
                interval_start_s = finite_float(
                    row.get("interval_start_s"),
                    f"power_trace.csv row {index} interval_start_s",
                )
                interval_end_s = finite_float(
                    row.get("interval_end_s"),
                    f"power_trace.csv row {index} interval_end_s",
                )
            except ValueError as exc:
                return [f"strict: raw-to-trace: {exc}"]
            if interval_start_s != sample.interval_start_s:
                return [
                    f"strict: raw-to-trace: {prefix}power_trace.csv row "
                    f"{index} rail {rail!r} interval_start_s "
                    f"{interval_start_s!r} does not match raw-derived "
                    f"{sample.interval_start_s!r}"
                ]
            if interval_end_s != sample.interval_end_s:
                return [
                    f"strict: raw-to-trace: {prefix}power_trace.csv row "
                    f"{index} rail {rail!r} interval_end_s "
                    f"{interval_end_s!r} does not match raw-derived "
                    f"{sample.interval_end_s!r}"
                ]
    return []


RAW_TO_TRACE_VERIFIERS: dict[TelemetryBackend, RawToTraceVerifier] = {
    TelemetryBackend.MOCK: _verify_mock_raw_to_trace_exemption,
    TelemetryBackend.POWERMETRICS: _verify_powermetrics_raw_to_trace,
    TelemetryBackend.NVIDIA_SMI: _verify_nvidia_smi_raw_to_trace,
}


def _validated_config_telemetry_backend(reader: BundleReader) -> TelemetryBackend | None:
    try:
        return reader.config().hardware_target.telemetry_backend
    except BundleReadError:
        return None


def _is_sha256_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(char in "0123456789abcdef" for char in value)


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _cmd_validate_bundle(args: argparse.Namespace) -> int:
    problems = validate_bundle(Path(args.path), strict=args.strict)
    if problems:
        for problem in problems:
            print(f"invalid: {problem}")
        return 2
    print(f"valid bundle: {args.path}")
    return 0


# ---------------------------------------------------------------------------
# reduce verb (Slice 2N.6) - post-hoc re-reduction: a reducer bug never
# re-runs hardware (D-002).  D-078 supersedes D-028's in-place-summary carveout:
# stored summaries are immutable and prospective reductions are new artifacts.


def _cmd_reduce(args: argparse.Namespace) -> int:
    """Write a prospective reduction without mutating stored summary bytes."""
    bundle_path = Path(args.path)
    if not bundle_path.is_dir() or not (bundle_path / "config.json").is_file():
        print(
            f"error: not a run bundle directory (no config.json): {bundle_path}",
            file=sys.stderr,
        )
        return 2
    stored_path = bundle_path / "summary_metrics.json"
    recorded_version: str | None = None
    if stored_path.is_file():
        try:
            stored = json.loads(stored_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            stored = None
        provenance = stored.get("summary_provenance") if isinstance(stored, dict) else None
        value = provenance.get("reducer_version") if isinstance(provenance, dict) else None
        recorded_version = value if isinstance(value, str) else None
    requested_version = args.reducer_version
    if requested_version is None and stored_path.is_file():
        requested_version = recorded_version
    summary = reduce_bundle(bundle_path, reducer_version=requested_version)
    try:
        payload = summary.to_dict()
    except SchemaError as exc:
        print(f"reduced summary is not admissible: {exc}", file=sys.stderr)
        return 3
    reducer_version = payload.get("summary_provenance", {}).get("reducer_version")
    if args.output:
        output_path = Path(args.output)
    else:
        try:
            cwd = Path.cwd().resolve()
            resolved_bundle = bundle_path.resolve()
        except OSError as exc:
            print(f"error: cannot resolve safe reduction output location: {exc}", file=sys.stderr)
            return 2
        if cwd == resolved_bundle or resolved_bundle in cwd.parents:
            print(
                "error: current directory is inside the input bundle; choose an "
                "external --output for immutable evidence",
                file=sys.stderr,
            )
            return 2
        output_path = cwd / (
            f"{bundle_path.name}.summary_metrics.rereduced.{reducer_version}.json"
        )
    try:
        resolved_output = output_path.resolve()
        resolved_bundle = bundle_path.resolve()
    except OSError as exc:
        print(f"error: cannot resolve safe reduction output path: {exc}", file=sys.stderr)
        return 2
    if resolved_output == resolved_bundle or resolved_bundle in resolved_output.parents:
        print(
            "error: reduction output must be outside the immutable input bundle",
            file=sys.stderr,
        )
        return 2
    if resolved_output == stored_path.resolve() and stored_path.is_file():
        print(
            "error: refusing to overwrite stored summary_metrics.json; choose a new --output",
            file=sys.stderr,
        )
        return 2
    try:
        with output_path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    except FileExistsError:
        print(f"error: refusing to overwrite existing reduction artifact: {output_path}", file=sys.stderr)
        return 2
    print(_bundle_line(bundle_path, summary))
    print(f"reduction artifact: {output_path}")
    return 0 if is_admissible_succeeded_summary(payload) else 3


def _cmd_output_identity_report(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_bytes())
    if not isinstance(manifest, dict):
        raise OutputIdentityError("analysis manifest top level must be an object")
    pairs = manifest.get("pairs")
    if not isinstance(pairs, list) or not any(
        isinstance(pair, dict) and pair.get("pair_id") == args.pair_id
        for pair in pairs
    ):
        raise OutputIdentityError(f"pair {args.pair_id!r} is not in the manifest")
    manifest_id = manifest.get("manifest_id")
    if not isinstance(manifest_id, str) or not manifest_id:
        raise OutputIdentityError("analysis manifest ID is unavailable")
    report = build_output_identity_report(
        manifest_id=manifest_id,
        pair_id=args.pair_id,
        spec_off_bundle=(Path(args.spec_off_bundle) if args.spec_off_bundle else None),
        spec_on_bundle=(Path(args.spec_on_bundle) if args.spec_on_bundle else None),
        strict_validator=validate_bundle,
    )
    rendered = render_output_identity_report(report)
    if args.output:
        Path(args.output).write_bytes(rendered)
        print(
            f"output-identity-report: {args.output} "
            f"state={report['overall_state']} id={report['report_id']}"
        )
    else:
        sys.stdout.buffer.write(rendered)
    return 0


# ---------------------------------------------------------------------------
# P2-037 deterministic contrast/claim derivation.


class _EvidenceRootAction(argparse.Action):
    """Collect one exact floor-evidence ``ID=PATH`` mapping."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string: str | None = None,
    ) -> None:
        del parser, option_string
        if "=" not in values:
            raise argparse.ArgumentError(self, "expected ID=PATH")
        root_id, path_text = (part.strip() for part in values.split("=", 1))
        if not root_id:
            raise argparse.ArgumentError(self, "evidence-root ID must be nonempty")
        if not path_text:
            raise argparse.ArgumentError(self, "evidence-root PATH must be nonempty")
        mapping = dict(getattr(namespace, self.dest, None) or {})
        if root_id in mapping:
            raise argparse.ArgumentError(
                self, f"duplicate evidence-root ID {root_id!r}"
            )
        mapping[root_id] = Path(path_text)
        setattr(namespace, self.dest, mapping)


def _cmd_analyze_claims(args: argparse.Namespace) -> int:
    # Lazy import avoids a cycle: the engine receives this module's shared
    # strict validator by injection rather than importing/duplicating it.
    from joulewise.analysis_engine import AnalysisInputError, analyze_claims
    from joulewise.analysis_engine.artifact import ClaimArtifactError

    try:
        artifact = analyze_claims(
            Path(args.analysis_manifest),
            Path(args.runs_root),
            Path(args.floor_artifact),
            strict_validator=validate_bundle,
            evidence_roots=args.evidence_roots,
            output_path=Path(args.output),
            legacy_l1_mechanics=args.legacy_l1_mechanics,
            legacy_allowlist=_STRICT_LEGACY_BUNDLE_IDENTITIES,
        )
    except (AnalysisInputError, ClaimArtifactError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: cannot write claim-verdict artifact: {exc}", file=sys.stderr)
        return 3
    outcomes: dict[str, int] = {}
    for contrast in artifact["contrasts"]:
        outcome = contrast["claim_evaluation"]["outcome"]
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    counts = ",".join(f"{key}={outcomes[key]}" for key in sorted(outcomes))
    print(
        f"claim-verdicts: {args.output} id={artifact['claim_verdicts_id']} "
        f"contrasts={len(artifact['contrasts'])} outcomes={counts}"
    )
    return 0


# ---------------------------------------------------------------------------
# report verb (Slice 2J) - static HTML run browser (D-006), [analysis] extra


def _cmd_report(args: argparse.Namespace) -> int:
    """Render the static run browser and print the index path + run count.

    A :class:`~joulewise.report.ReportError` (missing ``[analysis]`` extra or a
    bad runs dir) and an ``OSError`` propagate to ``main`` and become
    ``error: ...`` on stderr with exit 2. On success prints exactly
    ``report: <output>/index.html runs=<n>`` and exits 0.
    """
    runs_dir = Path(args.runs_dir)
    index_path = generate_report(runs_dir, Path(args.output))
    runs = sum(1 for child in runs_dir.iterdir() if child.is_dir() and child.name != "experiments")
    print(f"report: {index_path} runs={runs}")
    return 0


def _cmd_envelope_gate(args: argparse.Namespace) -> int:
    """Run the P2-010b affine smoke envelope gate and emit JSON."""
    from joulewise.envelope_gate import (
        VERDICT_REFUSED,
        VERDICT_VALIDATED,
        analyze_envelope_gate,
    )

    payload = analyze_envelope_gate(
        [Path(path) for path in args.bundle_dirs],
        lambda path: validate_bundle(path, strict=True),
    )
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
        print(f"envelope-gate: {args.output} verdict={payload['verdict']}")
    else:
        print(text, end="")
    if payload["verdict"] == VERDICT_VALIDATED:
        return 0
    if payload["verdict"] == VERDICT_REFUSED:
        return 2
    return 3


def _cmd_determinism_gate(args: argparse.Namespace) -> int:
    """Run the P2-028 response-hash determinism gate and emit JSON."""
    from joulewise.determinism_gate import (
        REASON_OUTPUT_INSIDE_INPUT_BUNDLE,
        VERDICT_REFUSED,
        VERDICT_SUPPORTED,
        analyze_determinism_gate,
    )

    bundle_dirs = [Path(path) for path in args.bundle_dirs]
    output_path = Path(args.output) if args.output else None
    output_inside_bundle = output_path is not None and _path_resolves_inside_any(
        output_path, bundle_dirs
    )
    payload = analyze_determinism_gate(
        bundle_dirs,
        lambda path: validate_bundle(path, strict=True),
        preflight_reason_codes=(
            [REASON_OUTPUT_INSIDE_INPUT_BUNDLE] if output_inside_bundle else None
        ),
    )
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output_inside_bundle:
        print(text, end="")
    elif output_path is not None:
        try:
            output_path.write_text(text, encoding="utf-8")
        except OSError as exc:
            print(text, end="")
            print(
                f"determinism-gate: failed to write --output {output_path}: {exc}",
                file=sys.stderr,
            )
        else:
            print(f"determinism-gate: {args.output} verdict={payload['verdict']}")
    else:
        print(text, end="")
    if payload["verdict"] == VERDICT_SUPPORTED:
        return 0
    if payload["verdict"] == VERDICT_REFUSED:
        return 2
    return 3


def _path_resolves_inside_any(path: Path, directories: list[Path]) -> bool:
    try:
        resolved_path = path.resolve()
    except (OSError, RuntimeError):
        return False
    for directory in directories:
        try:
            resolved_directory = directory.resolve()
            resolved_path.relative_to(resolved_directory)
        except ValueError:
            continue
        except (OSError, RuntimeError):
            continue
        return True
    return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="joulewise")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-config", help="validate a benchmark config")
    validate.add_argument("path", help="path to a JSON benchmark config")
    validate.set_defaults(func=_cmd_validate_config)

    schema = subparsers.add_parser("print-config-schema", help="print draft config JSON Schema")
    schema.add_argument("--output", help="optional path to write schema JSON")
    schema.set_defaults(func=_cmd_print_config_schema)

    output_schema = subparsers.add_parser("print-output-schema", help="print draft summary output JSON Schema")
    output_schema.add_argument("--output", help="optional path to write schema JSON")
    output_schema.set_defaults(func=_cmd_print_output_schema)

    doctor = subparsers.add_parser(
        "doctor", help="run a read-only configuration and machine preflight"
    )
    doctor.add_argument(
        "configs",
        nargs="*",
        help="JSON benchmark config path(s), in any order",
    )
    doctor.add_argument(
        "--campaign",
        action="store_true",
        help="apply campaign gates, including config-warning acknowledgement",
    )
    doctor.add_argument(
        "--ack-config-warnings",
        action="store_true",
        help="record acknowledgement of ignored config keys for campaign mode",
    )
    doctor.add_argument(
        "--backup-destination",
        help="existing backup destination to inspect for presence and free space",
    )
    doctor.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="emit stable machine-readable JSON instead of the human table",
    )
    doctor.set_defaults(func=_cmd_doctor)

    kv_size = subparsers.add_parser("kv-size", help="compute KV-cache size from model config")
    kv_size.add_argument("config", nargs="?", help="path to a HF config.json")
    kv_size.add_argument("--layers", type=int, help="number of hidden layers")
    kv_size.add_argument("--kv-heads", type=int, help="number of KV heads")
    kv_size.add_argument("--head-dim", type=int, help="attention head dimension")
    kv_size.add_argument(
        "--dtype-bytes",
        type=int,
        default=2,
        help="bytes per cache scalar (default: 2 for fp16)",
    )
    kv_size.add_argument(
        "--prompt-tokens",
        default="512,2048,8192",
        help="comma-separated prompt lengths (default: 512,2048,8192)",
    )
    kv_size.set_defaults(func=_cmd_kv_size)

    run = subparsers.add_parser("run", help="run one benchmark and write a complete bundle")
    run.add_argument("config", help="path to a JSON benchmark config")
    run.add_argument(
        "--runs-dir",
        default="runs",
        help="directory the run bundle is written under (default: runs/)",
    )
    run.add_argument(
        "--frozen-cooldown-anchor-json",
        help=(
            "campaign-owned immutable cooldown anchor JSON passed explicitly "
            "to a multi-repetition experiment"
        ),
    )
    run.add_argument(
        "--instrument-calibration-dir",
        help=(
            "hash-verified powermetrics fiducial validation directory copied "
            "into the new bundle"
        ),
    )
    run.add_argument(
        "--instrument-power-policy",
        help="current run power-policy id (must match calibration binding)",
    )
    run.add_argument(
        "--post-window-sampling-dwell-s",
        type=float,
        help=(
            "retain telemetry sampling for this many seconds after the measured "
            "stop marker without extending the measured window"
        ),
    )
    run.set_defaults(func=_cmd_run)

    validate_bundle_parser = subparsers.add_parser(
        "validate-bundle", help="structurally verify a run bundle directory"
    )
    validate_bundle_parser.add_argument("path", help="path to a run bundle directory")
    validate_bundle_parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "additionally require succeeded bundles to be reducer-consumable "
            "and their summary to match a fresh re-reduction (D-030; use for "
            "dataset publication gates)"
        ),
    )
    validate_bundle_parser.set_defaults(func=_cmd_validate_bundle)

    reduce_parser = subparsers.add_parser(
        "reduce",
        help="write a prospective summary artifact without rewriting stored evidence",
    )
    reduce_parser.add_argument("path", help="path to a run bundle directory")
    reduce_parser.add_argument(
        "--output",
        help="new output path (must not be an existing stored summary/artifact)",
    )
    reduce_parser.add_argument(
        "--reducer-version",
        help="explicit reducer wire (frozen historical arms remain replay-only)",
    )
    reduce_parser.set_defaults(func=_cmd_reduce)

    output_identity = subparsers.add_parser(
        "output-identity-report",
        help="derive the C-023 cross-bundle decoded-output identity report",
    )
    output_identity.add_argument("--manifest", required=True)
    output_identity.add_argument("--pair-id", required=True)
    output_identity.add_argument("--spec-off-bundle")
    output_identity.add_argument("--spec-on-bundle")
    output_identity.add_argument("--output")
    output_identity.set_defaults(func=_cmd_output_identity_report)

    analyze = subparsers.add_parser(
        "analyze-claims",
        help="derive paired contrast and claim verdicts from frozen evidence",
    )
    analyze.add_argument(
        "--analysis-manifest", required=True, help="frozen analysis_manifest.json path"
    )
    analyze.add_argument(
        "--runs-root",
        required=True,
        help="analysis-corpus root containing registered run bundles",
    )
    analyze.add_argument(
        "--evidence-root",
        dest="evidence_roots",
        action=_EvidenceRootAction,
        default=None,
        metavar="ID=PATH",
        help=(
            "floor-evidence root mapping; repeat once for each declared "
            "evidence_root_id (may be used alongside --runs-root)"
        ),
    )
    analyze.add_argument(
        "--floor-artifact", required=True, help="validated P2-039 floor artifact JSON"
    )
    analyze.add_argument(
        "--output", required=True, help="claim_verdicts.json output path"
    )
    analyze.add_argument(
        "--legacy-l1-mechanics",
        action="store_true",
        help="mechanics-only legacy mode; frozen six-bundle allowlist and L1 ceiling",
    )
    analyze.set_defaults(func=_cmd_analyze_claims)

    report = subparsers.add_parser(
        "report", help="render a static HTML run browser (needs the [analysis] extra)"
    )
    report.add_argument("runs_dir", help="directory containing run bundles")
    report.add_argument(
        "--output",
        default="report",
        help="directory the static report is written to (default: report/)",
    )
    report.set_defaults(func=_cmd_report)

    envelope_gate = subparsers.add_parser(
        "envelope-gate",
        help="compute the affine smoke envelope-validation verdict JSON",
    )
    envelope_gate.add_argument(
        "bundle_dirs",
        nargs="+",
        help="strict-valid affine smoke bundle directory/directories",
    )
    envelope_gate.add_argument(
        "--output",
        help="optional path to write the machine-readable verdict JSON",
    )
    envelope_gate.set_defaults(func=_cmd_envelope_gate)

    determinism_gate = subparsers.add_parser(
        "determinism-gate",
        help="compare per-item response hashes across repeated strict-valid bundles",
    )
    determinism_gate.add_argument(
        "bundle_dirs",
        nargs="*",
        help="bundle directories from one same-config repetition group (two or more required)",
    )
    determinism_gate.add_argument(
        "--output",
        help="optional path to write the machine-readable verdict JSON",
    )
    determinism_gate.set_defaults(func=_cmd_determinism_gate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (
        OSError,
        json.JSONDecodeError,
        KVSizeError,
        SchemaError,
        BundleError,
        OutputIdentityError,
        ReducerVersionError,
        ReportError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
