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
    decode_rich_telemetry,
    idle_window_gpu_quality,
    parse_powermetrics_records,
    samples_from_raw_powermetrics,
)
from joulewise.bundle import BundleError
from joulewise.bundle_read import BundleReader, BundleReadError
from joulewise.clock import Clock, FakeClock, SystemClock
from joulewise.controller import run_benchmark, run_experiment
from joulewise.kv_size import (
    KVSizeError,
    KVSizeParams,
    bytes_per_token,
    extract_kv_params,
    format_bytes,
    prompt_totals,
)
from joulewise.provenance import (
    PROMPT_TOKEN_IDS_HASH_DOMAIN,
    SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN,
    suite_prompt_plan_class,
    suite_prompt_rollup,
)
from joulewise.reduce import reduce_bundle
from joulewise.report import ReportError, generate_report
from joulewise.schemas import (
    BenchmarkConfig,
    RunStatus,
    RuntimeBackend,
    SchemaError,
    SUMMARY_REDUCER_VERSION,
    SummaryMetrics,
    TelemetryBackend,
)
from joulewise.validation import finite_float
from joulewise.uncertainty_evidence import (
    SCHEMA_VERSION as P2038_SCHEMA_VERSION,
    derive_idle_drift_evidence,
    derive_powermetrics_clock_evidence,
    stamp_from_mapping,
)

_PROMPT_TOKEN_IDS_HASH_DOMAIN = PROMPT_TOKEN_IDS_HASH_DOMAIN
_SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN = SUITE_PROMPT_TOKEN_IDS_HASH_DOMAIN

# The pre-D-033 corpus; frozen forever, never extended.
_STRICT_LEGACY_BUNDLE_IDENTITIES = frozenset(
    {
        (
            "example-mac-mlx-local__r1",
            "ee80585a2f6cee6aa7e12eb83c318fd88a934be02d5fa2fb2eb7509630640fd5",
        ),
        (
            "example-mac-mlx-local__r2",
            "08144a7be4a10d887babbd5fcd1a93f391c1db2d11c63d3131afad80b59cb373",
        ),
        (
            "example-mac-mlx-local__r3",
            "fe75fc3bafe0af7485fdf98b70ac3d07ccc1db502230bf1b180b94689ab54652",
        ),
        (
            "example-mac-mlx-qwen35-122b-512t__r1",
            "74761e420520e0d6d979be7d3d08aa6ff7e0f5f8ac8e48109d3dedc08d8d0b7a",
        ),
        (
            "example-mac-mlx-qwen35-122b-512t__r2",
            "8808632f0235b412d30563747283c397ad534edb711e4cec784712182cbe3b60",
        ),
        (
            "example-mac-mlx-qwen35-122b-512t__r3",
            "8be8dd955219a8631c8e37a1b3467f368f37624d07acebd2d52924137dff69f4",
        ),
    }
)


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
    config = BenchmarkConfig.from_mapping(_load_config(Path(args.config)))
    clock = _select_clock(config)
    if config.workload_profile.repetitions > 1:
        manifest_path, members = run_experiment(config, Path(args.runs_dir), clock)
        for bundle_path, summary in members:
            print(_bundle_line(bundle_path, summary))
        print(f"experiment: {manifest_path} members={len(members)}")
        all_succeeded = all(
            summary.status == RunStatus.SUCCEEDED for _, summary in members
        )
        return 0 if all_succeeded else 3
    bundle_path, summary = run_benchmark(config, Path(args.runs_dir), clock)
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
    summary = reader.raw_summary()
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
            1 for point in curve if window.start_s <= point.t <= window.end_s
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
    problems.extend(_strict_emitted_token_ids_problems(reader))
    problems.extend(_strict_budgeted_suite_prompt_count_problems(reader))
    problems.extend(_strict_uncertainty_evidence_problems(reader))
    problems.extend(_strict_raw_to_trace_problems(reader))
    if not version_problems:
        fresh = reduce_bundle(reader.path).to_dict()
        # The fresh 0.4.2 derivation is the raw/metadata authority.  Inspect it
        # before legacy additive-absence projection can hide the governed
        # object, while retaining the stored-summary check for unsupported
        # versions and tampered current-era summaries.  Exact diagnostics are
        # de-duplicated when both views independently report the mismatch.
        for problem in _strict_idle_mean_uncertainty_problems(fresh):
            if problem not in problems:
                problems.append(problem)
        if comparison_reducer_version is not None:
            fresh["summary_provenance"]["reducer_version"] = (
                comparison_reducer_version
            )
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
        return [], set(), False, None
    if reducer_version == "0.4.1":
        return [], ADDED_SINCE_0_4_1, False, "0.4.1"
    return [
        "strict: unsupported reducer version; re-reduction required"
    ], set(), False, None


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
    path = reader.path / "outputs" / "suite_items.jsonl"
    if not path.is_file():
        return []
    try:
        text = path.read_text()
    except OSError:
        return []
    records: list[tuple[int, dict[str, Any]]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append((index, record))
    return records


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
    if evidence.get("schema_version") != P2038_SCHEMA_VERSION:
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
        expected, _point = derive_powermetrics_clock_evidence(
            stamps=stamps,
            elapsed_s=[record.elapsed_ns / 1_000_000_000.0 for record in raw_records],
            plist_timestamp_s=[
                float(record.metadata["plist_timestamp_s"]) for record in raw_records
            ],
        )
    except (KeyError, OSError, TypeError, ValueError) as exc:
        return problems + [
            f"strict: uncertainty evidence: cannot re-derive clock evidence: {exc}"
        ]
    if clock_anchor != expected["clock_anchor"]:
        problems.append(
            "strict: uncertainty evidence: clock_anchor does not match paired-clock/raw-plist derivation"
        )
    if sample_phase != expected["sample_phase"]:
        problems.append(
            "strict: uncertainty evidence: sample_phase does not match paired-clock/raw-plist derivation"
        )
    events = _strict_suite_item_records_from_path(reader.path / "events.jsonl")
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


def _strict_suite_item_records_from_path(path: Path) -> list[tuple[int, dict[str, Any]]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    records: list[tuple[int, dict[str, Any]]] = []
    for index, line in enumerate(text.splitlines(), start=1):
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
        else:
            evidence = metadata.get("uncertainty_evidence")
            clock_anchor = (
                evidence.get("clock_anchor") if isinstance(evidence, dict) else None
            )
            if not isinstance(clock_anchor, dict):
                return [
                    "strict: raw-to-trace: current-era clock_anchor evidence is missing"
                ]
            point_s = finite_float(
                clock_anchor.get("first_sample_end_point_epoch_s"),
                "metadata.uncertainty_evidence.clock_anchor.first_sample_end_point_epoch_s",
            )
            expected = samples_from_raw_powermetrics(
                raw_path.read_bytes(),
                first_record_endpoint_s=point_s,
            )
    except (OSError, ValueError) as exc:
        return [f"strict: raw-to-trace: cannot derive raw/{RAW_SAMPLES_NAME}: {exc}"]
    return _compare_raw_derived_samples(reader, expected)


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
# re-runs hardware (D-002); the bundle is re-reduced in place.


def _cmd_reduce(args: argparse.Namespace) -> int:
    """Re-derive and rewrite ``summary_metrics.json`` for an existing bundle.

    Rewriting the summary is the one sanctioned post-finalize bundle mutation
    (D-028): the raw artifacts stay immutable evidence, and the summary is by
    definition derived from them. A path that is not a bundle directory (no
    ``config.json``) is refused with exit 2 and no write, so evidence is never
    invented inside an arbitrary directory. Degenerate bundle contents reduce
    to a structured FAILED summary (exit 3), matching ``run``'s exit scheme:
    0 succeeded, 2 usage/not-a-bundle, 3 reduced-to-failure.
    """
    bundle_path = Path(args.path)
    if not bundle_path.is_dir() or not (bundle_path / "config.json").is_file():
        print(
            f"error: not a run bundle directory (no config.json): {bundle_path}",
            file=sys.stderr,
        )
        return 2
    summary = reduce_bundle(bundle_path)
    (bundle_path / "summary_metrics.json").write_text(
        json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n"
    )
    print(_bundle_line(bundle_path, summary))
    return 0 if summary.status == RunStatus.SUCCEEDED else 3


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
        help="re-derive summary_metrics.json for an existing bundle (post-hoc reduction)",
    )
    reduce_parser.add_argument("path", help="path to a run bundle directory")
    reduce_parser.set_defaults(func=_cmd_reduce)

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
        ReportError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
