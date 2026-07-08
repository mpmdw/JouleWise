"""Shared bundle read layer: one home for bundle-interpretation policy.

Implements D-025 (Slice 2N.8): ``reduce.py`` (metrics), ``report.py``
(presentation), and the ``validate-bundle`` verb (structural checks) all read
bundles through :class:`BundleReader`, so policy questions - which rails sum to
``power_w`` (D-018), what the measured window is (D-026), when per-rail rows
are misaligned (D-027), what makes a bundle complete (D-011) - are answered in
exactly one place. Phase 4's ``aggregate`` verb becomes the fourth consumer.

The reader owns parsing and interpretation policy for one standard node
bundle; it does no metrics math (``_integrate`` and idle subtraction stay in
``joulewise.reduce``) and no rendering. Future composite/split bundles should
get a separate ``CompositeBundleReader`` that owns merged events, per-node
sub-bundle coordination, and cross-node summary semantics while reusing this
reader for each node bundle. Accessors come in two strictness levels:

- strict (``config()``, ``metadata()``, ``events()``, ``summed_curve()``):
  raise :class:`BundleReadError` with a structured problem message on
  missing/corrupt artifacts - the reducer converts these into structured
  ``FAILED`` summaries (Slice 2N.6), never tracebacks.
- tolerant (``raw_config()``, ``raw_metadata()``, ``raw_summary()``): return
  ``None`` on missing/corrupt artifacts - the report uses these so a damaged
  bundle is surfaced rather than hidden (D-011).

Rail summation policy (D-018 + D-027): ``power(t)`` sums ``power_w`` over
exactly the manifest rails, grouped by identical ``timestamp_s``. Per-rail
rows for one sample instant must share one timestamp (row fan-out per rail);
with a multi-rail manifest, a timestamp carrying only a subset of the manifest
rails is a misalignment and raises a structured failure - a silently
interleaved (undersummed) curve is never produced. An empty manifest yields an
empty curve: consumers must not invent a fallback summation policy (2N.7).
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    SchemaError,
)
from joulewise.validation import finite_float, is_finite_number

__all__ = [
    "BundleReadError",
    "BundleReader",
    "TracePoint",
    "Window",
]

#: Exact ``power_trace.csv`` header (D-018).
POWER_TRACE_HEADER = "timestamp_s,power_w,source,rail"

#: The five keys every ``events.jsonl`` record must carry, no more, no less.
EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}

_REQUIRED_ARTIFACTS = ("config.json", "metadata.json", "events.jsonl", "summary_metrics.json")
_JSON_ARTIFACTS = ("config.json", "metadata.json", "summary_metrics.json")
_SUMMARY_WRITER_KEYS_V0_1 = {
    "status",
    "energy_request_j",
    "energy_token_j",
    "energy_output_token_j",
    "gross_energy_j",
    "idle_subtracted_energy_j",
    "ttft_s",
    "decode_latency_s",
    "throughput_tokens_s",
    "idle_baseline",
    "uncertainty",
    "measurement_quality",
    "phase_energy_j",
    "failure_reason",
    "failure_message",
}
_SUCCEEDED_FINITE_FIELDS = {"energy_request_j", "gross_energy_j"}
_SUCCEEDED_NULLABLE_NUMBER_FIELDS = {
    "energy_token_j",
    "energy_output_token_j",
    "idle_subtracted_energy_j",
    "ttft_s",
    "decode_latency_s",
    "throughput_tokens_s",
}


class BundleReadError(Exception):
    """A structured, non-crashing bundle read/interpretation failure."""


@dataclass(frozen=True)
class TracePoint:
    """One point on the summed power curve: ``power_w`` at ``t``."""

    t: float
    power_w: float


@dataclass(frozen=True)
class Window:
    start_s: float
    end_s: float

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


class BundleReader:
    """Read one bundle directory; parsing and policy live here (D-025).

    Accessors memoize, so repeated reads of the same artifact cost one parse.
    The reader works on not-yet-finalized bundles exactly as the controller's
    reduce stage does (``summary_metrics.json`` may be absent).
    """

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        self._cache: dict[str, Any] = {}

    @property
    def path(self) -> Path:
        return self._path

    # ------------------------------------------------------------------
    # Strict accessors (structured failures, used by the reducer)

    def config(self) -> BenchmarkConfig:
        """The re-validated typed config; raises :class:`BundleReadError`."""
        if "config" not in self._cache:
            raw = self._strict_json("config.json")
            try:
                self._cache["config"] = BenchmarkConfig.from_mapping(raw)
            except SchemaError as exc:
                raise BundleReadError(f"config.json does not re-validate: {exc}") from exc
        return self._cache["config"]

    def metadata(self) -> dict[str, Any]:
        """Parsed ``metadata.json``; raises :class:`BundleReadError`."""
        if "metadata" not in self._cache:
            raw = self._strict_json("metadata.json")
            if not isinstance(raw, dict):
                raise BundleReadError("metadata.json is not a JSON object")
            self._cache["metadata"] = raw
        return self._cache["metadata"]

    def events(self) -> list[dict[str, Any]]:
        """Parsed ``events.jsonl`` records (a missing file is an empty list;
        a malformed line raises :class:`BundleReadError`).

        Field types are validated centrally here (2N follow-up, 2026-07-06
        status review P1): every record's ``timestamp_s`` must be a finite
        real number, so the window/token/phase accessors below can cast
        without consumers ever seeing a raw ``ValueError``/``TypeError`` from
        a corrupt event line.
        """
        if "events" not in self._cache:
            path = self._path / "events.jsonl"
            if not path.is_file():
                self._cache["events"] = []
                return self._cache["events"]
            events: list[dict[str, Any]] = []
            try:
                text = path.read_text()
            except OSError as exc:
                raise BundleReadError(f"events.jsonl cannot be read: {exc}") from exc
            for index, line in enumerate(text.splitlines()):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise BundleReadError(
                        f"events.jsonl line {index + 1} is not valid JSON: {exc}"
                    ) from exc
                if not isinstance(record, dict):
                    raise BundleReadError(
                        f"events.jsonl line {index + 1} is not a JSON object"
                    )
                if set(record) != EVENT_KEYS:
                    raise BundleReadError(
                        f"events.jsonl line {index + 1} keys are "
                        f"{sorted(record)}, expected {sorted(EVENT_KEYS)}"
                    )
                if not is_finite_number(record.get("timestamp_s")):
                    raise BundleReadError(
                        f"events.jsonl line {index + 1} timestamp_s is not a "
                        f"finite number: {record.get('timestamp_s')!r}"
                    )
                events.append(record)
            self._cache["events"] = events
        return self._cache["events"]

    def trace_rows(self) -> list[dict[str, str]]:
        """Raw ``power_trace.csv`` rows (a missing file is an empty list)."""
        if "trace_rows" not in self._cache:
            path = self._path / "power_trace.csv"
            if not path.is_file():
                self._cache["trace_rows"] = []
                return self._cache["trace_rows"]
            try:
                with path.open(newline="") as handle:
                    self._cache["trace_rows"] = list(csv.DictReader(handle))
            except OSError as exc:
                raise BundleReadError(f"power_trace.csv cannot be read: {exc}") from exc
        return self._cache["trace_rows"]

    def summed_curve(self) -> list[TracePoint]:
        """The D-018 summed power curve over exactly the manifest rails.

        Rows on rails outside the manifest are ignored; rows are grouped by
        identical ``timestamp_s`` and the result is time-sorted. With a
        multi-rail manifest, a timestamp carrying only a subset of the
        manifest rails is a D-027 misalignment: a structured failure naming
        the timestamp and missing rail(s) is raised instead of silently
        producing an interleaved, undersummed curve. An empty manifest yields
        an empty curve (no fallback summation policy exists - 2N.7).
        """
        if "summed_curve" in self._cache:
            return self._cache["summed_curve"]
        trace = _validate_trace_rows(self.trace_rows(), self.rail_manifest())
        if trace.problems:
            raise BundleReadError(trace.problems[0])
        self._cache["summed_curve"] = [
            TracePoint(t=t, power_w=trace.totals[t]) for t in sorted(trace.totals)
        ]
        return self._cache["summed_curve"]

    # ------------------------------------------------------------------
    # Tolerant accessors (None on damage, used by the report)

    def raw_config(self) -> dict[str, Any] | None:
        return self._tolerant_json("config.json")

    def raw_metadata(self) -> dict[str, Any] | None:
        return self._tolerant_json("metadata.json")

    def raw_summary(self) -> dict[str, Any] | None:
        return self._tolerant_json("summary_metrics.json")

    def is_complete(self) -> bool:
        """D-011: complete iff ``summary_metrics.json`` validates by status."""
        summary = self.raw_summary()
        return summary is not None and not _check_summary(summary)

    # ------------------------------------------------------------------
    # Interpretation policy

    def rail_manifest(self) -> list[str]:
        """The telemetry adapter's rail manifest (D-018); ``[]`` when absent."""
        metadata = self.raw_metadata()
        if isinstance(metadata, dict):
            try:
                return _rail_manifest_from_metadata(metadata)
            except ValueError as exc:
                raise BundleReadError(str(exc)) from exc
        return []

    def measured_window(self) -> Window | None:
        """The window the reducer integrates over (D-026).

        Preferred bounds are the ``sampling_started``/``sampling_stopped``
        marker events (sampling confirmed active, so sampler spawn latency and
        stop-side parsing stay outside the window). Bundles written before the
        markers existed (pre-2N.2) fall back to the ``measured_run`` stage
        boundaries.
        """
        marker_start: float | None = None
        marker_end: float | None = None
        stage_start: float | None = None
        stage_end: float | None = None
        for event in self.events():
            if event.get("phase") != "measured_run":
                continue
            event_type = event.get("event_type")
            if event_type == "sampling_started":
                marker_start = float(event["timestamp_s"])
            elif event_type == "sampling_stopped":
                marker_end = float(event["timestamp_s"])
            elif event_type == "stage_started":
                stage_start = float(event["timestamp_s"])
            elif event_type == "stage_completed":
                stage_end = float(event["timestamp_s"])
        if marker_start is not None and marker_end is not None:
            return Window(start_s=marker_start, end_s=marker_end)
        if stage_start is None or stage_end is None:
            return None
        return Window(start_s=stage_start, end_s=stage_end)

    def phase_windows(self) -> dict[str, list[Window]]:
        """Pair ``phase_start``/``phase_end`` events by phase name in order.

        Multiple intervals with the same phase name are all returned (the
        reducer sums their energies; the report shades each span).
        """
        open_starts: dict[str, list[float]] = {}
        windows: dict[str, list[Window]] = {}
        for event in self.events():
            event_type = event.get("event_type")
            phase = event.get("phase")
            if not isinstance(phase, str):
                continue
            if event_type == "phase_start":
                open_starts.setdefault(phase, []).append(float(event["timestamp_s"]))
            elif event_type == "phase_end":
                starts = open_starts.get(phase)
                if not starts:
                    continue
                start_s = starts.pop(0)
                windows.setdefault(phase, []).append(
                    Window(start_s=start_s, end_s=float(event["timestamp_s"]))
                )
        return windows

    def token_timestamps(self) -> list[float]:
        return [
            float(event["timestamp_s"])
            for event in self.events()
            if event.get("event_type") == "token"
        ]

    # ------------------------------------------------------------------
    # Structural validation (the validate-bundle policy)

    def problems(self) -> list[str]:
        """Return every structural problem with the bundle (no short-circuit).

        An empty list means the bundle is structurally valid. This is the
        policy behind the ``validate-bundle`` CLI verb, CI, and Phase 5
        dataset publication.
        """
        path = self._path
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

        metadata = parsed.get("metadata.json")
        if "metadata.json" in parsed and not isinstance(metadata, dict):
            problems.append("metadata.json is not a JSON object")
        if isinstance(metadata, dict):
            problems.extend(_check_config_sha256(path, metadata))

        summary = parsed.get("summary_metrics.json")
        if summary is not None:
            problems.extend(_check_summary(summary))

        if "events.jsonl" not in missing:
            problems.extend(_check_events(path / "events.jsonl"))

        problems.extend(_check_power_trace(path, summary, metadata))

        return problems

    # ------------------------------------------------------------------
    # Internals

    def _strict_json(self, name: str) -> Any:
        path = self._path / name
        try:
            return json.loads(path.read_text())
        except FileNotFoundError as exc:
            raise BundleReadError(f"missing required artifact: {name}") from exc
        except OSError as exc:
            raise BundleReadError(f"{name} cannot be read: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise BundleReadError(f"{name} is not valid JSON: {exc}") from exc

    def _tolerant_json(self, name: str) -> dict[str, Any] | None:
        key = f"tolerant:{name}"
        if key not in self._cache:
            try:
                value = json.loads((self._path / name).read_text())
            except (OSError, json.JSONDecodeError):
                value = None
            self._cache[key] = value if isinstance(value, dict) else None
        return self._cache[key]


# ---------------------------------------------------------------------------
# Structural check helpers (validate-bundle policy details)


@dataclass(frozen=True)
class _TraceValidation:
    totals: dict[float, float]
    problems: list[str]


def _check_config_sha256(path: Path, metadata: dict[str, Any]) -> list[str]:
    expected = metadata.get("config_sha256")
    if expected is None:
        return ["metadata.config_sha256 is missing"]
    if not isinstance(expected, str):
        return [f"metadata.config_sha256 is not a string: {expected!r}"]
    try:
        actual = hashlib.sha256((path / "config.json").read_bytes()).hexdigest()
    except FileNotFoundError:
        return []
    except OSError as exc:
        return [f"config.json cannot be read for config_sha256 validation: {exc}"]
    if actual != expected:
        return [
            "metadata.config_sha256 mismatch: "
            f"metadata has {expected!r}, config.json bytes hash to {actual!r}"
        ]
    return []


def _rail_manifest_from_metadata(metadata: dict[str, Any]) -> list[str]:
    device = metadata.get("device")
    if not isinstance(device, dict):
        return []
    manifest = device.get("rail_manifest")
    if manifest is None:
        return []
    if not isinstance(manifest, list):
        raise ValueError("metadata.device.rail_manifest is not a list")
    for index, rail in enumerate(manifest):
        if not isinstance(rail, str):
            raise ValueError(
                "metadata.device.rail_manifest entry "
                f"{index} is not a string: {rail!r}"
            )
    return manifest


def _check_summary(summary: Any) -> list[str]:
    """Shared summary validity policy used by validation and completion."""
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
    if status == RunStatus.SUCCEEDED:
        missing = sorted(_SUMMARY_WRITER_KEYS_V0_1 - set(summary))
        for key in missing:
            problems.append(f"summary status is succeeded but {key} is missing")
        for key in sorted(_SUCCEEDED_FINITE_FIELDS):
            value = summary.get(key)
            if not is_finite_number(value):
                problems.append(
                    f"summary status is succeeded but {key} is not a finite "
                    f"number: {value!r}"
                )
        for key in sorted(_SUCCEEDED_NULLABLE_NUMBER_FIELDS):
            value = summary.get(key)
            if value is not None and not is_finite_number(value):
                problems.append(
                    f"summary status is succeeded but nullable numeric field "
                    f"{key} is not null or finite: {value!r}"
                )
    return problems


def _validate_trace_rows(rows: list[dict[str, str]], manifest: list[str]) -> _TraceValidation:
    manifest_set = set(manifest)
    totals: dict[float, float] = {}
    rails_at: dict[float, set[str]] = {}
    seen: set[tuple[float, str]] = set()
    problems: list[str] = []
    for index, row in enumerate(rows, start=2):
        rail = row.get("rail") or ""
        if rail not in manifest_set:
            continue
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
            problems.append(str(exc))
            continue
        key = (timestamp_s, rail)
        if key in seen:
            problems.append(
                "power_trace.csv has duplicate rail row at timestamp "
                f"{timestamp_s}: rail {rail!r} appears more than once"
            )
            continue
        seen.add(key)
        totals[timestamp_s] = totals.get(timestamp_s, 0.0) + power_w
        rails_at.setdefault(timestamp_s, set()).add(rail)
    if len(manifest_set) > 1:
        misaligned = sorted(t for t, rails in rails_at.items() if rails != manifest_set)
        if misaligned:
            first = misaligned[0]
            missing = sorted(manifest_set - rails_at[first])
            problems.append(
                "power_trace.csv rail rows are misaligned (D-027): at "
                f"timestamp {first} rails {sorted(rails_at[first])} do not "
                f"match the manifest {sorted(manifest_set)} (missing "
                f"{missing}); per-rail rows for one sample instant must "
                f"share one timestamp ({len(misaligned)} misaligned "
                "timestamp(s) total)"
            )
    return _TraceValidation(totals=totals, problems=problems)


def _check_events(events_path: Path) -> list[str]:
    """Every line a JSON object with exactly the five keys and a finite
    numeric ``timestamp_s``; non-decreasing timestamps; the last event is
    ``run_finalized``."""
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
        if set(record) != EVENT_KEYS:
            problems.append(
                f"events.jsonl line {index + 1} keys are "
                f"{sorted(record)}, expected {sorted(EVENT_KEYS)}"
            )
            continue
        if not is_finite_number(record["timestamp_s"]):
            problems.append(
                f"events.jsonl line {index + 1} timestamp_s is not a finite "
                f"number: {record['timestamp_s']!r}"
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


def _check_power_trace(path: Path, summary: Any, metadata: Any) -> list[str]:
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
    if ",".join(header) != POWER_TRACE_HEADER:
        return [
            "power_trace.csv header is "
            f"{','.join(header)!r}, expected {POWER_TRACE_HEADER!r}"
        ]
    problems: list[str] = []
    manifest: list[str] = []
    if isinstance(metadata, dict):
        try:
            manifest = _rail_manifest_from_metadata(metadata)
        except ValueError as exc:
            problems.append(str(exc))
    try:
        with trace_path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
    except OSError as exc:
        return [f"power_trace.csv cannot be read: {exc}"]
    if manifest:
        problems.extend(_validate_trace_rows(rows, manifest).problems)
    else:
        for index, row in enumerate(rows, start=2):
            for field in ("timestamp_s", "power_w"):
                try:
                    finite_float(row.get(field), f"power_trace.csv row {index} {field}")
                except ValueError as exc:
                    problems.append(str(exc))
    return problems
