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
from typing import Any

from joulewise.adapters.powermetrics import (
    RAW_SAMPLES_NAME,
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
    SummaryMetrics,
    TelemetryBackend,
)
from joulewise.validation import finite_float

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
    if window.duration_s > 0:
        in_window = sum(
            1 for point in curve if window.start_s <= point.t <= window.end_s
        )
        if in_window < 2:
            problems.append(
                f"strict: only {in_window} summed power sample(s) inside the "
                "measured window; a succeeded summary needs a "
                "reducer-consumable curve"
            )
    problems.extend(_strict_summary_provenance_problems(reader, summary))
    problems.extend(_strict_workload_provenance_problems(reader, summary))
    problems.extend(_strict_emitted_token_ids_problems(reader))
    problems.extend(_strict_budgeted_suite_prompt_count_problems(reader))
    problems.extend(_strict_raw_to_trace_problems(reader))
    fresh = reduce_bundle(reader.path).to_dict()
    differing = _strict_summary_differences(fresh, summary)
    if differing:
        problems.append(
            "strict: summary_metrics.json does not match a fresh re-reduction "
            f"of the raw artifacts (differing keys: {', '.join(differing)})"
        )
    return problems


_STRICT_ADDITIVE_ABSENT_TOLERANCE = {
    "idle_baseline.gpu_idle_ratio_mean",
    "idle_baseline.gpu_idle_ratio_min",
    "idle_baseline.gpu_freq_hz_mean",
    "idle_baseline.idle_window_suspect",
    "measurement_quality.idle_window_suspect",
}

_STRICT_LEGACY_ADDITIVE_ABSENT_TOLERANCE = _STRICT_ADDITIVE_ABSENT_TOLERANCE | {
    "measurement_quality.token_counts_source",
    "measurement_quality.phase_identifiability",
}


def _strict_summary_differences(
    fresh: Any,
    stored: Any,
    path: str = "",
    *,
    absent_tolerance: set[str] | None = None,
) -> list[str]:
    """Compare fresh vs stored summaries with legacy-additive null tolerance.

    A freshly emitted key that is absent from a legacy stored summary is
    tolerated only when the fresh value is ``None``. Stored keys, including
    stored extras, remain exact claims and must match the fresh reduction.
    """
    if absent_tolerance is None:
        stored_new_era = (
            isinstance(stored, dict)
            and isinstance(stored.get("summary_provenance"), dict)
        )
        absent_tolerance = (
            _STRICT_ADDITIVE_ABSENT_TOLERANCE
            if stored_new_era
            else _STRICT_LEGACY_ADDITIVE_ABSENT_TOLERANCE
        )
    if isinstance(fresh, dict) and isinstance(stored, dict):
        differences: list[str] = []
        for key in sorted(set(fresh) | set(stored)):
            child = f"{path}.{key}" if path else str(key)
            if key not in stored:
                if child == "summary_provenance":
                    continue
                if child in absent_tolerance:
                    continue
                if fresh[key] is not None:
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


def _strict_summary_provenance_problems(
    reader: BundleReader, summary: dict[str, Any]
) -> list[str]:
    if _strict_legacy_bundle_metadata(reader.raw_metadata()):
        return []
    if isinstance(summary.get("summary_provenance"), dict):
        return []
    return [
        "strict: summary_metrics.summary_provenance is missing or not an "
        "object for current-era bundle"
    ]


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


def _strict_raw_to_trace_problems(reader: BundleReader) -> list[str]:
    raw_path = reader.path / "raw" / RAW_SAMPLES_NAME
    telemetry_backend = _validated_config_telemetry_backend(reader)
    if telemetry_backend != TelemetryBackend.POWERMETRICS and not raw_path.is_file():
        return []
    if not raw_path.is_file():
        return [f"strict: raw-to-trace: missing raw/{RAW_SAMPLES_NAME}"]
    metadata = reader.raw_metadata()
    if not isinstance(metadata, dict):
        return ["strict: raw-to-trace: metadata.json is missing or invalid"]
    device = metadata.get("device")
    if not isinstance(device, dict):
        return ["strict: raw-to-trace: metadata.device is missing or not an object"]
    try:
        anchor_offset_s = finite_float(
            device.get("plist_anchor_offset_s"),
            "metadata.device.plist_anchor_offset_s",
        )
    except ValueError as exc:
        return [f"strict: raw-to-trace: {exc}"]
    try:
        expected = samples_from_raw_powermetrics(
            raw_path.read_bytes(),
            plist_anchor_offset_s=anchor_offset_s,
        )
    except (OSError, ValueError) as exc:
        return [f"strict: raw-to-trace: cannot derive raw/{RAW_SAMPLES_NAME}: {exc}"]
    try:
        rows = reader.trace_rows()
    except BundleReadError as exc:
        return [f"strict: raw-to-trace: {exc}"]
    if len(rows) != len(expected):
        return [
            "strict: raw-to-trace: power_trace.csv row count "
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
                "strict: raw-to-trace: power_trace.csv row "
                f"{index} rail {rail!r} timestamp_s {timestamp_s!r} "
                f"does not match raw-derived {sample.timestamp_s!r}"
            ]
        if power_w != sample.power_w:
            return [
                "strict: raw-to-trace: power_trace.csv row "
                f"{index} rail {rail!r} power_w {power_w!r} "
                f"does not match raw-derived {sample.power_w!r}"
            ]
        if source != sample.source:
            return [
                "strict: raw-to-trace: power_trace.csv row "
                f"{index} rail {rail!r} source {source!r} "
                f"does not match raw-derived {sample.source!r}"
            ]
        if rail != expected_rail:
            return [
                "strict: raw-to-trace: power_trace.csv row "
                f"{index} rail {rail!r} does not match raw-derived "
                f"{expected_rail!r}"
            ]
    return []


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
