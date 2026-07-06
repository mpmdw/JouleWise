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
import sys
from pathlib import Path
from typing import Any

from joulewise.bundle import BundleError
from joulewise.bundle_read import BundleReader, BundleReadError
from joulewise.clock import Clock, FakeClock, SystemClock
from joulewise.controller import run_benchmark, run_experiment
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
    fresh = reduce_bundle(reader.path).to_dict()
    if fresh != summary:
        differing = sorted(
            key
            for key in set(fresh) | set(summary)
            if fresh.get(key) != summary.get(key)
        )
        problems.append(
            "strict: summary_metrics.json does not match a fresh re-reduction "
            f"of the raw artifacts (differing keys: {', '.join(differing)})"
        )
    return problems


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
    except (OSError, json.JSONDecodeError, SchemaError, BundleError, ReportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
