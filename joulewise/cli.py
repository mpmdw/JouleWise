"""JouleWise command-line interface.

Phase 1 added the schema/config verbs (``validate-config``,
``print-config-schema``, ``print-output-schema``). Phase 2 Slice 2E adds the
headline ``run`` verb (one command -> a complete run bundle) and the
``validate-bundle`` verb (structural verification of any bundle, reused by CI
now and by Phase 5 dataset publication later). Slice 2J adds the ``report``
verb (a static HTML run browser; D-006), which needs the ``[analysis]`` extra.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from joulewise.bundle import BundleError
from joulewise.clock import Clock, FakeClock, SystemClock
from joulewise.controller import run_benchmark, run_experiment
from joulewise.report import ReportError, generate_report
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    RuntimeBackend,
    SchemaError,
    SummaryMetrics,
    TelemetryBackend,
)

#: Exact ``power_trace.csv`` header (D-018); ``validate-bundle`` pins it.
_POWER_TRACE_HEADER = "timestamp_s,power_w,source,rail"

#: The five keys every ``events.jsonl`` record must carry, no more, no less.
_EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}


def _load_config(path: Path) -> dict[str, Any]:
    if path.suffix.lower() != ".json":
        raise SchemaError("Phase 1 CLI supports JSON configs; YAML parsing is planned for Phase 2")
    return json.loads(path.read_text())


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
    line = f"bundle: {bundle_path} status={summary.status.value}"
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
# validate-bundle verb (Slice 2E) - check functions kept importable so CI now
# and Phase 5 dataset publication later reuse them without the CLI shell.

_REQUIRED_ARTIFACTS = ("config.json", "metadata.json", "events.jsonl", "summary_metrics.json")
_JSON_ARTIFACTS = ("config.json", "metadata.json", "summary_metrics.json")


def validate_bundle(path: Path) -> list[str]:
    """Return a list of structural problems with the bundle at ``path``.

    An empty list means the bundle is valid. Performs every check (no
    short-circuit) so a single invocation reports all problems. Reused by the
    ``validate-bundle`` CLI verb, by CI, and by Phase 5 dataset publication.
    """
    path = Path(path)
    if not path.exists():
        return [f"path does not exist: {path}"]
    if not path.is_dir():
        return [f"path is not a directory: {path}"]

    problems: list[str] = []

    missing = [name for name in _REQUIRED_ARTIFACTS if not (path / name).is_file()]
    for name in missing:
        problems.append(f"missing required artifact: {name}")

    parsed: dict[str, Any] = {}
    for name in _JSON_ARTIFACTS:
        if name in missing:
            continue
        try:
            parsed[name] = json.loads((path / name).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{name} is not valid JSON: {exc}")

    if "config.json" in parsed:
        try:
            BenchmarkConfig.from_mapping(parsed["config.json"])
        except SchemaError as exc:
            problems.append(f"config.json does not re-validate: {exc}")

    summary = parsed.get("summary_metrics.json")
    if summary is not None:
        problems.extend(_check_summary(summary))

    if "events.jsonl" not in missing:
        problems.extend(_check_events(path / "events.jsonl"))

    problems.extend(_check_power_trace(path, summary))

    return problems


def _check_summary(summary: Any) -> list[str]:
    """Status is a valid RunStatus; failure_reason consistency (D-012 shape)."""
    if not isinstance(summary, dict):
        return ["summary_metrics.json is not a JSON object"]
    problems: list[str] = []
    raw_status = summary.get("status")
    try:
        status = RunStatus(raw_status)
    except ValueError:
        return [f"summary status is not a valid RunStatus: {raw_status!r}"]
    raw_reason = summary.get("failure_reason")
    if status in {RunStatus.FAILED, RunStatus.UNSUPPORTED}:
        if raw_reason is None:
            problems.append(f"summary status is {status.value} but failure_reason is missing")
        else:
            try:
                FailureReason(raw_reason)
            except ValueError:
                problems.append(
                    f"summary failure_reason is not a valid FailureReason: {raw_reason!r}"
                )
    elif raw_reason is not None:
        problems.append(
            f"summary status is succeeded but carries failure_reason {raw_reason!r}"
        )
    return problems


def _check_events(events_path: Path) -> list[str]:
    """Every line a JSON object with exactly the five keys; non-decreasing
    timestamps; the last event is ``run_finalized``."""
    try:
        text = events_path.read_text()
    except OSError as exc:
        return [f"events.jsonl cannot be read: {exc}"]
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return ["events.jsonl has no event records"]
    problems: list[str] = []
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(f"events.jsonl line {index + 1} is not valid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            problems.append(f"events.jsonl line {index + 1} is not a JSON object")
            continue
        if set(record) != _EVENT_KEYS:
            problems.append(
                f"events.jsonl line {index + 1} keys are "
                f"{sorted(record)}, expected {sorted(_EVENT_KEYS)}"
            )
            continue
        records.append(record)
    if len(records) != len(lines):
        # A malformed line already produced a problem; remaining checks need a
        # clean record set, so stop here.
        return problems
    timestamps = [record["timestamp_s"] for record in records]
    if any(later < earlier for earlier, later in zip(timestamps, timestamps[1:])):
        problems.append("events.jsonl timestamps are not non-decreasing")
    if records[-1]["event_type"] != "run_finalized":
        problems.append(
            "events.jsonl last event is "
            f"{records[-1]['event_type']!r}, expected 'run_finalized'"
        )
    return problems


def _check_power_trace(path: Path, summary: Any) -> list[str]:
    """power_trace.csv is required for succeeded runs, optional otherwise;
    whenever present, its header must be exactly the D-018 header."""
    trace_path = path / "power_trace.csv"
    status_value = summary.get("status") if isinstance(summary, dict) else None
    succeeded = status_value == RunStatus.SUCCEEDED.value
    if not trace_path.is_file():
        if succeeded:
            return ["power_trace.csv is required when status is succeeded but is missing"]
        return []
    try:
        with trace_path.open(newline="") as handle:
            header = next(csv.reader(handle), None)
    except OSError as exc:
        return [f"power_trace.csv cannot be read: {exc}"]
    if header is None:
        return ["power_trace.csv is empty (no header line)"]
    if ",".join(header) != _POWER_TRACE_HEADER:
        return [
            "power_trace.csv header is "
            f"{','.join(header)!r}, expected {_POWER_TRACE_HEADER!r}"
        ]
    return []


def _cmd_validate_bundle(args: argparse.Namespace) -> int:
    problems = validate_bundle(Path(args.path))
    if problems:
        for problem in problems:
            print(f"invalid: {problem}")
        return 2
    print(f"valid bundle: {args.path}")
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
    validate_bundle_parser.set_defaults(func=_cmd_validate_bundle)

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
    except (OSError, json.JSONDecodeError, SchemaError, BundleError, ReportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
