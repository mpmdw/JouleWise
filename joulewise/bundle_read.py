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
from typing import Any, Mapping

from joulewise.axi_decode_config import (
    AXI_CONFIG_EXTENSION,
    COMMON_REQUEST_IDENTITY_KEYS,
    EVENT_SEMANTICS_VERSION,
    AxiSchemaError,
    RequestRoster,
    canonical_json_bytes as axi_canonical_json_bytes,
    sha256_bytes as axi_sha256_bytes,
    validate_request_row,
    validate_request_token_row,
    validate_v2_event,
    validate_v2_metadata,
)
from joulewise.schemas import (
    BenchmarkConfig,
    RunStatus,
    SchemaError,
    summary_validation_problems,
)
from joulewise.provenance import normalized_sha256_hex, prompt_token_ids_sha256, sha256_hex
from joulewise.suite import (
    BLOCK_END,
    BLOCK_START,
    ITEM_END,
    ITEM_START,
    LEVEL_END,
    LEVEL_START,
    LEGACY_SUITE_SCHEMA_VERSION,
    MARKER_REQUIRED_METADATA_KEYS,
    REDUCER_ASSIGNABLE,
    RUNTIME_ASSIGNABLE,
    SUITE_END,
    SUITE_START,
    SuiteManifest,
    canonical_effective_manifest,
    order_seed,
    realized_order,
    suite_manifest_sha256,
)
from joulewise.validation import finite_float, is_finite_number

__all__ = [
    "AXI_VALIDATOR_REASON_CODES",
    "BundleReadError",
    "BundleReader",
    "ItemWindow",
    "TracePoint",
    "Window",
    "axi_v2_validation_problems",
]

AXI_VALIDATOR_REASON_CODES = frozenset(
    {
        "axi_partial_opt_in",
        "batch_observation_mismatch",
        "cancelled_proposal_evidence_lost",
        "event_global_order_invalid",
        "event_semantics_invalid",
        "event_source_identity_unresolved",
        "primary_source_identity_unresolved",
        "proposal_count_exceeds_configured_cap",
        "request_counter_rollup_mismatch",
        "request_event_ordinal_invalid",
        "request_event_outside_decode",
        "request_identity_mismatch",
        "request_lifecycle_incomplete",
        "request_output_artifact_invalid",
        "request_output_count_mismatch",
        "request_output_hash_mismatch",
        "request_phase_overlap",
        "request_phase_pairing_invalid",
        "request_roster_hash_mismatch",
        "request_roster_invalid",
        "target_tokenizer_artifact_hash_mismatch",
        "target_tokenizer_identity_unavailable",
    }
)

#: Exact ``power_trace.csv`` header (D-018).
POWER_TRACE_HEADER = "timestamp_s,power_w,source,rail"
POWER_TRACE_INTERVAL_HEADER = (
    "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s"
)

# The pre-D-033 corpus compatibility identity set; frozen forever.
FROZEN_LEGACY_BUNDLE_IDENTITIES = frozenset(
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

#: The five keys every ``events.jsonl`` record must carry, no more, no less.
EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}

_REQUIRED_ARTIFACTS = ("config.json", "metadata.json", "events.jsonl", "summary_metrics.json")
_JSON_ARTIFACTS = ("config.json", "metadata.json", "summary_metrics.json")


class BundleReadError(Exception):
    """A structured, non-crashing bundle read/interpretation failure."""


@dataclass(frozen=True)
class TracePoint:
    """One point or interval-average observation on the summed power trace."""

    t: float
    power_w: float
    support_start_s: float | None = None
    support_end_s: float | None = None


@dataclass(frozen=True)
class Window:
    start_s: float
    end_s: float

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


@dataclass(frozen=True)
class ItemWindow:
    item_id: str
    item_index: int
    status: str
    window: Window
    start_metadata: dict[str, Any]
    end_metadata: dict[str, Any]


_PhaseSourceIdentity = tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class _PairedPhaseInterval:
    phase: str
    source_identity: _PhaseSourceIdentity
    window: Window


@dataclass(frozen=True)
class _PhasePairing:
    windows_by_phase: dict[str, list[Window]]
    windows_by_key: dict[tuple[str, _PhaseSourceIdentity], list[Window]]
    problems: list[str]

    def windows_for_event(self, phase: str, event: dict[str, Any]) -> list[Window]:
        return self.windows_by_key.get(
            (phase, _phase_source_identity(event)),
            [],
        )


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

    def is_frozen_legacy_identity(self) -> bool:
        metadata = self.raw_metadata()
        return isinstance(metadata, dict) and (
            metadata.get("run_id"), metadata.get("config_sha256")
        ) in FROZEN_LEGACY_BUNDLE_IDENTITIES

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
            TracePoint(
                t=t,
                power_w=trace.totals[t],
                support_start_s=(trace.supports[t][0] if t in trace.supports else None),
                support_end_s=(trace.supports[t][1] if t in trace.supports else None),
            )
            for t in sorted(trace.totals)
        ]
        return self._cache["summed_curve"]

    def raw_artifact_bytes(self, name: str) -> bytes | None:
        """Return one immutable ``raw/`` artifact, or ``None`` when absent.

        Reducer-owned raw derivations use this strict read boundary so an I/O
        failure remains distinguishable from an artifact that was never
        captured.  Only a basename is accepted; callers cannot traverse out of
        the bundle's raw directory.
        """
        if not name or Path(name).name != name:
            raise BundleReadError("raw artifact name must be a basename")
        key = f"raw-bytes:{name}"
        if key not in self._cache:
            path = self._path / "raw" / name
            if not path.is_file():
                return None
            try:
                self._cache[key] = path.read_bytes()
            except OSError as exc:
                raise BundleReadError(f"raw/{name} cannot be read: {exc}") from exc
        return self._cache[key]

    # ------------------------------------------------------------------
    # Tolerant accessors (None on damage, used by the report)

    def raw_config(self) -> dict[str, Any] | None:
        return self._tolerant_json("config.json")

    def raw_metadata(self) -> dict[str, Any] | None:
        return self._tolerant_json("metadata.json")

    def raw_summary(self) -> dict[str, Any] | None:
        return self._tolerant_json("summary_metrics.json")

    def is_event_v2(self) -> bool:
        metadata = self.raw_metadata()
        return isinstance(metadata, dict) and metadata.get(
            "event_semantics_version"
        ) == EVENT_SEMANTICS_VERSION

    def request_roster(self) -> RequestRoster:
        """Strict normalized RequestRoster accessor for event-v2 bundles."""

        if "request_roster" not in self._cache:
            raw = self._strict_json("request_roster.json")
            try:
                roster = RequestRoster.from_mapping(raw)
            except AxiSchemaError as exc:
                raise BundleReadError(f"request_roster.json does not re-validate: {exc}") from exc
            path = self._path / "request_roster.json"
            try:
                raw_bytes = path.read_bytes()
            except OSError as exc:
                raise BundleReadError(f"request_roster.json cannot be read: {exc}") from exc
            if raw_bytes != roster.to_bytes():
                raise BundleReadError("request_roster.json is not normalized canonical bytes")
            self._cache["request_roster"] = roster
        return self._cache["request_roster"]

    def request_rows(self) -> list[dict[str, Any]]:
        return self._strict_jsonl_objects("outputs/requests.jsonl")

    def request_token_rows(self) -> list[dict[str, Any]]:
        return self._strict_jsonl_objects("outputs/request_tokens.jsonl")

    def request_phase_windows(
        self,
    ) -> dict[tuple[str, str, str, int], Window]:
        """Event-v2 windows keyed by source, request, phase, and ordinal."""

        if "request_phase_windows" not in self._cache:
            pairs, problems = _axi_phase_pairs(self.events())
            if problems:
                raise BundleReadError("; ".join(problems))
            self._cache["request_phase_windows"] = pairs
        return self._cache["request_phase_windows"]

    def source_curve(self, source_identity: str) -> list[TracePoint]:
        """Power curve for one persisted event-v2 source identity."""

        key = f"source_curve:{source_identity}"
        if key not in self._cache:
            rows = [
                row
                for row in self.trace_rows()
                if row.get("source") == source_identity
            ]
            rails = sorted(
                {
                    row["rail"]
                    for row in rows
                    if isinstance(row.get("rail"), str) and row["rail"]
                }
            )
            if not rows or not rails:
                raise BundleReadError(
                    f"source identity {source_identity!r} has no telemetry rows"
                )
            trace = _validate_trace_rows(rows, rails)
            if trace.problems:
                raise BundleReadError(trace.problems[0])
            self._cache[key] = [
                TracePoint(
                    t=t,
                    power_w=trace.totals[t],
                    support_start_s=(
                        trace.supports[t][0] if t in trace.supports else None
                    ),
                    support_end_s=(
                        trace.supports[t][1] if t in trace.supports else None
                    ),
                )
                for t in sorted(trace.totals)
            ]
        return self._cache[key]

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

    def runtime_cleanup_ok(self) -> bool | None:
        """Local runtime-cleanup result from cleanup completion events.

        A recorded ``False`` dominates because one failed cleanup is enough to
        contaminate the following repetition. Otherwise every matching value
        must be the boolean ``True``; absent or malformed evidence is unknown.
        """
        values: list[Any] = []
        for event in self.events():
            if (
                event.get("event_type") != "stage_completed"
                or event.get("phase") != "cleanup"
            ):
                continue
            metadata = event.get("metadata")
            if not isinstance(metadata, dict):
                values.append(None)
                continue
            values.append(metadata.get("cleanup_ok"))
        if any(value is False for value in values):
            return False
        if not values or any(not isinstance(value, bool) for value in values):
            return None
        return True

    def phase_windows(self) -> dict[str, list[Window]]:
        """Return validated ``phase_start``/``phase_end`` windows.

        Pairing is scoped by phase plus power-source identity. Every marker
        must pair, intervals must not reverse, and intervals attributed to one
        source must not overlap. Concurrent intervals on distinct identified
        nodes, each representing its own meter, are valid. Multiple valid
        intervals with the same phase name are integrated separately and
        summed by the reducer.
        """
        return self._validated_phase_pairing().windows_by_phase

    def token_timestamps(self) -> list[float]:
        """Output/decode token timestamps only.

        Token events on the prompt side are not a valid denominator for
        output-token metrics. The event contract's discriminator is the
        event's phase: current runtimes emit output tokens in ``decode``.
        When decode phase windows are present, the timestamp must also land
        inside one of those windows.
        """
        pairing = self._validated_phase_pairing()
        return [
            float(event["timestamp_s"])
            for event in self.events()
            if _is_decode_token_event(event, pairing)
        ]

    def suite_manifest(self) -> SuiteManifest | None:
        """Strict suite manifest accessor.

        Returns ``None`` when ``suite_manifest.json`` is absent. If the file
        exists, it must parse and validate as a :class:`SuiteManifest`.
        Legacy v1 reads synthesize the v2 cache verification marker; the exact
        synthesized field name is exposed in ``manifest.synthesized_fields``
        so consumers cannot mistake compatibility interpretation for bytes
        that were present in the historical artifact.
        """
        if "suite_manifest" not in self._cache:
            if not (self._path / "suite_manifest.json").is_file():
                self._cache["suite_manifest"] = None
            else:
                raw = self._strict_json("suite_manifest.json")
                try:
                    self._cache["suite_manifest"] = SuiteManifest.from_mapping(raw)
                except SchemaError as exc:
                    raise BundleReadError(
                        f"suite_manifest.json does not re-validate: {exc}"
                    ) from exc
        return self._cache["suite_manifest"]

    def suite_item_records(self) -> list[dict[str, Any]] | None:
        """Return suite item outcomes in realized execution order.

        These existing per-item records are the realized-output evidence of
        record for both current and sealed suite bundles.  The bundle-level
        ``output_policy.stop_condition`` is intentionally not interpreted as
        one synthetic realized stop.
        """

        records, problems = _suite_item_records(self._path)
        if problems:
            raise BundleReadError("; ".join(problems))
        return records

    def suite_window(self) -> Window | None:
        """FIFO-pair the first ``suite_start``/``suite_end`` marker."""
        starts: list[float] = []
        for event in self.events():
            event_type = event.get("event_type")
            if event_type == SUITE_START:
                starts.append(float(event["timestamp_s"]))
            elif event_type == SUITE_END and starts:
                return Window(start_s=starts.pop(0), end_s=float(event["timestamp_s"]))
        return None

    def item_windows(self) -> list[ItemWindow]:
        """Pair item markers by ``(item_id, item_index)`` and order by index.

        Unpaired starts and ends are skipped by this accessor; validation owns
        reporting malformed marker sets. Matching by index prevents repeated
        sentinel item IDs with reordered end markers from being misattributed.
        """
        open_starts: dict[str, list[dict[str, Any]]] = {}
        windows: list[ItemWindow] = []
        for event in self.events():
            metadata = event.get("metadata")
            if not isinstance(metadata, dict):
                continue
            item_id = metadata.get("item_id")
            if not isinstance(item_id, str):
                continue
            event_type = event.get("event_type")
            if event_type == ITEM_START:
                open_starts.setdefault(item_id, []).append(event)
            elif event_type == ITEM_END:
                starts = open_starts.get(item_id, [])
                if not starts:
                    continue
                end_metadata = dict(metadata)
                item_index = end_metadata.get("item_index")
                status = end_metadata.get("status")
                if isinstance(item_index, bool) or not isinstance(item_index, int):
                    continue
                if not isinstance(status, str):
                    continue
                match_index = next(
                    (
                        index
                        for index, start in enumerate(starts)
                        if isinstance(start.get("metadata"), dict)
                        and start["metadata"].get("item_index") == item_index
                    ),
                    None,
                )
                if match_index is None:
                    continue
                start = starts.pop(match_index)
                start_metadata = dict(start["metadata"])
                windows.append(
                    ItemWindow(
                        item_id=item_id,
                        item_index=item_index,
                        status=status,
                        window=Window(
                            start_s=float(start["timestamp_s"]),
                            end_s=float(event["timestamp_s"]),
                        ),
                        start_metadata=start_metadata,
                        end_metadata=end_metadata,
                    )
                )
        return sorted(windows, key=lambda item: item.item_index)

    def block_windows(self) -> dict[str, list[Window]]:
        return _paired_group_windows(self.events(), BLOCK_START, BLOCK_END, "block_id")

    def level_windows(self) -> dict[tuple[str, str], list[Window]]:
        """Pair level markers by ``(block_id, level_id)`` (SUB-2).

        Level marker metadata carries ``level_id``; the enclosing block marker
        supplies ``block_id`` while scanning, so a recurring level id in two
        blocks yields two independent keys/windows.
        """
        open_starts: dict[tuple[str, str], list[float]] = {}
        windows: dict[tuple[str, str], list[Window]] = {}
        current_block: str | None = None
        for event in self.events():
            metadata = event.get("metadata")
            if not isinstance(metadata, dict):
                continue
            event_type = event.get("event_type")
            if event_type == BLOCK_START and isinstance(metadata.get("block_id"), str):
                current_block = metadata["block_id"]
            elif event_type == BLOCK_END:
                current_block = None
            elif event_type in {LEVEL_START, LEVEL_END}:
                level_id = metadata.get("level_id")
                if current_block is None or not isinstance(level_id, str):
                    continue
                key = (current_block, level_id)
                if event_type == LEVEL_START:
                    open_starts.setdefault(key, []).append(float(event["timestamp_s"]))
                else:
                    starts = open_starts.get(key)
                    if not starts:
                        continue
                    windows.setdefault(key, []).append(
                        Window(start_s=starts.pop(0), end_s=float(event["timestamp_s"]))
                    )
        return windows

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
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
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
        if "summary_metrics.json" in parsed:
            problems.extend(_check_summary(summary))

        if "events.jsonl" not in missing:
            problems.extend(_check_events(path / "events.jsonl"))

        problems.extend(_check_power_trace(path, summary, metadata))
        if _has_suite_contract(path, parsed.get("config.json")):
            problems.extend(
                self._suite_problems(parsed.get("config.json"), metadata, summary)
            )

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
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BundleReadError(f"{name} is not valid JSON: {exc}") from exc

    def _strict_jsonl_objects(self, name: str) -> list[dict[str, Any]]:
        key = f"jsonl:{name}"
        if key in self._cache:
            return self._cache[key]
        path = self._path / name
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise BundleReadError(f"{name} cannot be read: {exc}") from exc
        rows: list[dict[str, Any]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise BundleReadError(f"{name} line {line_number} is not valid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise BundleReadError(f"{name} line {line_number} is not a JSON object")
            rows.append(row)
        self._cache[key] = rows
        return rows

    def _validated_phase_pairing(self) -> _PhasePairing:
        if "phase_pairing" not in self._cache:
            pairing = _pair_phase_windows(self.events())
            if pairing.problems:
                raise BundleReadError(
                    "invalid phase markers: " + "; ".join(pairing.problems)
                )
            self._cache["phase_pairing"] = pairing
        return self._cache["phase_pairing"]

    def _tolerant_json(self, name: str) -> dict[str, Any] | None:
        key = f"tolerant:{name}"
        if key not in self._cache:
            try:
                value = json.loads((self._path / name).read_text())
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                value = None
            self._cache[key] = value if isinstance(value, dict) else None
        return self._cache[key]

    def _suite_problems(
        self, raw_config: Any, metadata: Any, summary: Any
    ) -> list[str]:
        return _suite_problems(self, raw_config, metadata, summary)


# ---------------------------------------------------------------------------
# Structural check helpers (validate-bundle policy details)


def _axi_problem(code: str, detail: str) -> str:
    return f"axi:{code}: {detail}"


def _axi_token_sequence_sha256(token_ids: list[int]) -> str:
    return axi_sha256_bytes(
        b"joulewise.request_output_token_ids.v1\n"
        + axi_canonical_json_bytes(token_ids)
    )


def _axi_token_slice_sha256(token_ids: list[int]) -> str:
    return axi_sha256_bytes(
        b"joulewise.request_output_token_ids_slice.v1\n"
        + axi_canonical_json_bytes(token_ids)
    )


def _axi_tokenizer_artifact_sha256(files: Mapping[str, Any]) -> str:
    return axi_sha256_bytes(
        b"joulewise.tokenizer_artifact_identity.v1\0"
        + axi_canonical_json_bytes(files)
    )


def _axi_phase_pairs(
    events: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str, str, int], Window], list[str]]:
    starts: dict[tuple[str, str, str, int], tuple[float, int]] = {}
    pairs: dict[tuple[str, str, str, int], Window] = {}
    problems: list[str] = []
    for index, event in enumerate(events, start=1):
        if event.get("event_type") not in {"phase_start", "phase_end"}:
            continue
        metadata = event.get("metadata")
        if not isinstance(metadata, dict) or "request_id" not in metadata:
            continue
        key = (
            str(metadata.get("source_identity")),
            str(metadata.get("request_id")),
            str(event.get("phase")),
            metadata.get("request_phase_ordinal"),
        )
        if not isinstance(key[3], int) or isinstance(key[3], bool) or key[3] < 0:
            problems.append(_axi_problem("request_phase_pairing_invalid", f"event {index} phase ordinal invalid"))
            continue
        timestamp = float(event["timestamp_s"])
        if event["event_type"] == "phase_start":
            if key in starts or key in pairs:
                problems.append(_axi_problem("request_phase_pairing_invalid", f"duplicate phase start {key!r}"))
            else:
                starts[key] = (timestamp, index)
            continue
        if key not in starts:
            problems.append(_axi_problem("request_phase_pairing_invalid", f"unmatched phase end {key!r}"))
            continue
        start, _ = starts.pop(key)
        if timestamp < start:
            problems.append(_axi_problem("request_phase_pairing_invalid", f"reversed phase pair {key!r}"))
            continue
        pairs[key] = Window(start, timestamp)
    for key in starts:
        problems.append(_axi_problem("request_phase_pairing_invalid", f"unmatched phase start {key!r}"))

    by_request: dict[tuple[str, str], list[tuple[str, Window]]] = {}
    for (source, request_id, phase, _ordinal), window in pairs.items():
        by_request.setdefault((source, request_id), []).append((phase, window))
    for request_key, intervals in by_request.items():
        ordered = sorted(intervals, key=lambda item: (item[1].start_s, item[1].end_s, item[0]))
        for left_index, (left_phase, left) in enumerate(ordered):
            for right_phase, right in ordered[left_index + 1 :]:
                if right.start_s >= left.end_s:
                    break
                if left_phase == right_phase or {left_phase, right_phase} == {"prefill", "decode"}:
                    problems.append(
                        _axi_problem(
                            "request_phase_overlap",
                            f"{request_key!r} {left_phase!r} {left!r} overlaps {right_phase!r} {right!r}",
                        )
                    )
    return pairs, problems


def axi_v2_validation_problems(
    reader: BundleReader,
    *,
    allow_unfinalized_summary: bool = False,
) -> list[str]:
    """Validate all event-v2 request/lifecycle/output evidence.

    This path is selected explicitly by metadata version.  It never repairs or
    reinterprets historical bundles, and each refusal carries a stable code.
    """

    raw_config = reader.raw_config()
    metadata = reader.raw_metadata()
    summary = reader.raw_summary()
    config_opted = isinstance(raw_config, dict) and raw_config.get("schema_extensions") == [AXI_CONFIG_EXTENSION]
    event_opted = isinstance(metadata, dict) and metadata.get("event_semantics_version") == EVENT_SEMANTICS_VERSION
    reducer_opted = (
        isinstance(summary, dict)
        and isinstance(summary.get("summary_provenance"), dict)
        and summary["summary_provenance"].get("reducer_version") == "0.6.0"
    )
    if allow_unfinalized_summary and summary is None and config_opted and event_opted:
        reducer_opted = True
    if not any((config_opted, event_opted, reducer_opted)):
        return []
    if not all((config_opted, event_opted, reducer_opted)):
        return [_axi_problem("axi_partial_opt_in", "config extension, event v2, and reducer 0.6.0 must appear together")]

    problems: list[str] = []
    try:
        config = reader.config()
        if config.batch_policy is None or config.speculation is None:
            raise BundleReadError("typed AXI config fields are unavailable")
    except BundleReadError as exc:
        return [_axi_problem("axi_partial_opt_in", str(exc))]

    if isinstance(metadata, dict):
        for detail in _check_config_sha256(reader.path, metadata):
            problems.append(_axi_problem("event_semantics_invalid", detail))

    try:
        validate_v2_metadata(metadata, config.batch_policy, config.speculation)
    except AxiSchemaError as exc:
        code = "target_tokenizer_identity_unavailable" if "target_tokenizer" in str(exc) else "event_semantics_invalid"
        problems.append(_axi_problem(code, str(exc)))

    runtime = metadata.get("runtime") if isinstance(metadata, dict) else None
    if isinstance(runtime, dict):
        tokenizer_files = runtime.get("target_tokenizer_artifact_files")
        identity = runtime.get("target_tokenizer_identity")
        if not isinstance(tokenizer_files, dict) or not tokenizer_files:
            problems.append(_axi_problem("target_tokenizer_identity_unavailable", "runtime target tokenizer artifact map is missing"))
        else:
            valid_map = all(
                isinstance(path, str)
                and path
                and isinstance(digest, str)
                and len(digest) == 64
                and all(character in "0123456789abcdef" for character in digest)
                for path, digest in tokenizer_files.items()
            )
            if not valid_map:
                problems.append(_axi_problem("target_tokenizer_identity_unavailable", "runtime target tokenizer artifact map is malformed"))
            elif not isinstance(identity, dict) or identity.get("tokenizer_artifact_sha256") != _axi_tokenizer_artifact_sha256(tokenizer_files):
                problems.append(_axi_problem("target_tokenizer_artifact_hash_mismatch", "target tokenizer artifact map hash does not match identity"))
        if isinstance(identity, dict) and (
            identity.get("name") == "unknown"
            or identity.get("revision") == "unknown"
        ):
            problems.append(
                _axi_problem(
                    "target_tokenizer_identity_unavailable",
                    "target tokenizer name and resolved revision must be concrete",
                )
            )

    try:
        roster = reader.request_roster()
    except BundleReadError as exc:
        return problems + [_axi_problem("request_roster_invalid", str(exc))]
    try:
        roster_bytes = (reader.path / "request_roster.json").read_bytes()
    except OSError as exc:
        return problems + [_axi_problem("request_roster_invalid", str(exc))]
    roster_hash = axi_sha256_bytes(roster_bytes)
    if roster_hash != config.batch_policy.request_roster_sha256:
        problems.append(_axi_problem("request_roster_hash_mismatch", "embedded roster hash differs from config"))
    if len(roster.requests) != config.batch_policy.requested_batch_size:
        problems.append(_axi_problem("batch_observation_mismatch", "configured B differs from roster length"))
    roster_by_ordinal = {row.request_ordinal: row for row in roster.requests}

    try:
        events = reader.events()
    except BundleReadError as exc:
        return problems + [_axi_problem("event_semantics_invalid", str(exc))]
    timestamps = [float(event["timestamp_s"]) for event in events]
    if timestamps != sorted(timestamps):
        problems.append(_axi_problem("event_global_order_invalid", "events.jsonl timestamps are not nondecreasing"))
    request_events: list[dict[str, Any]] = []
    request_event_types = {
        "request_submitted", "request_admitted", "phase_start", "phase_end",
        "decode_emission", "token", "request_terminal",
    }
    for index, event in enumerate(events, start=1):
        metadata_row = event.get("metadata")
        request_scoped = event.get("event_type") in request_event_types and isinstance(metadata_row, dict) and "request_id" in metadata_row
        if not request_scoped:
            if event.get("event_type") in {"decode_emission", "token", "request_submitted", "request_admitted", "request_terminal"}:
                problems.append(_axi_problem("request_identity_mismatch", f"event {index} lacks request identity"))
            continue
        try:
            validate_v2_event(event, config.speculation)
        except AxiSchemaError as exc:
            message = str(exc)
            if message in {"proposal_count_exceeds_configured_cap", "cancelled_proposal_evidence_lost"}:
                code = message
            elif any(
                f"event.metadata.{key} is required" in message
                for key in COMMON_REQUEST_IDENTITY_KEYS
            ) or "request_id" in message:
                code = "request_identity_mismatch"
            else:
                code = "event_semantics_invalid"
            problems.append(_axi_problem(code, f"event {index}: {message}"))
        request_events.append(event)

    pairs, phase_problems = _axi_phase_pairs(request_events)
    problems.extend(phase_problems)
    decode_windows_by_request: dict[tuple[str, str], list[Window]] = {}
    for (source, request_id, phase, _ordinal), window in pairs.items():
        if phase == "decode":
            decode_windows_by_request.setdefault((source, request_id), []).append(window)

    by_request: dict[str, list[dict[str, Any]]] = {}
    for event in request_events:
        request_id = event["metadata"].get("request_id")
        if isinstance(request_id, str):
            by_request.setdefault(request_id, []).append(event)
    admitted: set[str] = set()
    terminal: dict[str, dict[str, Any]] = {}
    for request_id, rows in by_request.items():
        ordinals = [row["metadata"].get("request_event_ordinal") for row in rows]
        if ordinals != list(range(len(rows))):
            problems.append(_axi_problem("request_event_ordinal_invalid", f"{request_id} event ordinals are not contiguous in JSONL order"))
        submitted_rows = [row for row in rows if row["event_type"] == "request_submitted"]
        admitted_rows = [row for row in rows if row["event_type"] == "request_admitted"]
        terminal_rows = [row for row in rows if row["event_type"] == "request_terminal"]
        if len(submitted_rows) != 1 or len(admitted_rows) > 1 or len(terminal_rows) > 1:
            problems.append(_axi_problem("request_lifecycle_incomplete", f"{request_id} lifecycle cardinality invalid"))
        if admitted_rows:
            admitted.add(request_id)
            if len(terminal_rows) != 1:
                problems.append(_axi_problem("request_lifecycle_incomplete", f"admitted {request_id} has no unique terminal"))
        if terminal_rows:
            terminal[request_id] = terminal_rows[0]
        if rows and rows[0].get("event_type") != "request_submitted":
            problems.append(_axi_problem("request_lifecycle_incomplete", f"{request_id} does not begin with submission"))
        if terminal_rows and rows[-1].get("event_type") != "request_terminal":
            problems.append(_axi_problem("request_lifecycle_incomplete", f"{request_id} terminal is not last"))
        if submitted_rows:
            submitted_index = rows.index(submitted_rows[0])
            admitted_index = rows.index(admitted_rows[0]) if admitted_rows else None
            terminal_index = rows.index(terminal_rows[0]) if terminal_rows else None
            work_indices = [
                index
                for index, row in enumerate(rows)
                if row["event_type"] in {"phase_start", "phase_end", "decode_emission", "token"}
            ]
            if submitted_index != 0 or (
                work_indices and admitted_index is None
            ) or (
                admitted_index is not None
                and (
                    admitted_index <= submitted_index
                    or any(index <= admitted_index for index in work_indices)
                )
            ) or (
                terminal_index is not None
                and any(index >= terminal_index for index in work_indices)
            ):
                problems.append(
                    _axi_problem(
                        "request_lifecycle_incomplete",
                        f"{request_id} lifecycle event order is invalid",
                    )
                )
        identity_values = {
            (
                row["metadata"].get("request_ordinal"),
                row["metadata"].get("request_input_id"),
                row["metadata"].get("request_roster_sha256"),
                row["metadata"].get("batch_group_id"),
            )
            for row in rows
        }
        if len(identity_values) != 1:
            problems.append(_axi_problem("request_identity_mismatch", f"{request_id} identity changes across events"))
        elif identity_values:
            ordinal, input_id, event_roster_hash, batch_group_id = next(iter(identity_values))
            roster_row = roster_by_ordinal.get(ordinal)
            if roster_row is None or roster_row.request_input_id != input_id or event_roster_hash != roster_hash:
                problems.append(_axi_problem("request_identity_mismatch", f"{request_id} does not match roster"))
            expected_group = None if config.batch_policy.mode == "single_request" else metadata["batch"].get("batch_group_id")
            if batch_group_id != expected_group:
                problems.append(_axi_problem("request_identity_mismatch", f"{request_id} batch group mismatch"))
        for event in rows:
            if event["event_type"] not in {"decode_emission", "token"}:
                continue
            event_metadata = event["metadata"]
            windows = decode_windows_by_request.get((event_metadata.get("source_identity"), request_id), [])
            timestamp = float(event["timestamp_s"])
            if not any(window.start_s <= timestamp <= window.end_s for window in windows):
                problems.append(_axi_problem("request_event_outside_decode", f"{request_id} {event['event_type']} is outside paired decode window"))

    try:
        request_rows = reader.request_rows()
        token_rows = reader.request_token_rows()
    except BundleReadError as exc:
        return problems + [_axi_problem("request_output_artifact_invalid", str(exc))]
    for index, row in enumerate(request_rows, start=1):
        try:
            validate_request_row(row, config.speculation)
        except AxiSchemaError as exc:
            problems.append(_axi_problem("request_output_artifact_invalid", f"request row {index}: {exc}"))
    for index, row in enumerate(token_rows, start=1):
        try:
            validate_request_token_row(row)
        except AxiSchemaError as exc:
            problems.append(_axi_problem("request_output_artifact_invalid", f"token row {index}: {exc}"))
    request_ordinals = [row.get("request_ordinal") for row in request_rows]
    if request_ordinals != sorted(request_ordinals) or len(request_ordinals) != len(set(request_ordinals)):
        problems.append(_axi_problem("request_output_artifact_invalid", "request rows are not unique in ordinal order"))
    token_order = [(row.get("request_ordinal"), row.get("output_token_ordinal")) for row in token_rows]
    if token_order != sorted(token_order) or len(token_order) != len(set(token_order)):
        problems.append(_axi_problem("request_output_artifact_invalid", "request token rows are not unique in required order"))

    response_mirror = reader.path / "outputs" / "response.txt"
    tokens_mirror = reader.path / "outputs" / "tokens.jsonl"
    if config.batch_policy.requested_batch_size > 1 and (
        response_mirror.exists() or tokens_mirror.exists()
    ):
        problems.append(
            _axi_problem(
                "request_output_artifact_invalid",
                "B>1 bundle must not contain collapsed compatibility mirrors",
            )
        )
    elif config.batch_policy.requested_batch_size == 1:
        if response_mirror.exists():
            expected_text = (
                request_rows[0].get("response_text")
                if len(request_rows) == 1
                else None
            )
            try:
                response_bytes = response_mirror.read_bytes()
            except OSError as exc:
                problems.append(
                    _axi_problem(
                        "request_output_artifact_invalid",
                        f"outputs/response.txt cannot be read: {exc}",
                    )
                )
            else:
                if (
                    not isinstance(expected_text, str)
                    or response_bytes != expected_text.encode("utf-8")
                ):
                    problems.append(
                        _axi_problem(
                            "request_output_artifact_invalid",
                            "outputs/response.txt compatibility mirror differs from requests.jsonl",
                        )
                    )
        if tokens_mirror.exists():
            try:
                mirror_rows = reader._strict_jsonl_objects(
                    "outputs/tokens.jsonl"
                )
            except BundleReadError as exc:
                problems.append(
                    _axi_problem("request_output_artifact_invalid", str(exc))
                )
            else:
                mirror_projection = [
                    {
                        "index": row.get("index"),
                        "timestamp_s": row.get("timestamp_s"),
                        "token_id": row.get("token_id"),
                    }
                    for row in mirror_rows
                ]
                expected_projection = [
                    {
                        "index": row.get("output_token_ordinal"),
                        "timestamp_s": row.get("timestamp_s"),
                        "token_id": row.get("token_id"),
                    }
                    for row in token_rows
                ]
                if mirror_projection != expected_projection:
                    problems.append(
                        _axi_problem(
                            "request_output_artifact_invalid",
                            "outputs/tokens.jsonl compatibility mirror differs from request_tokens.jsonl",
                        )
                    )

    rows_by_id = {row.get("request_id"): row for row in request_rows if isinstance(row.get("request_id"), str)}
    if set(rows_by_id) != admitted:
        problems.append(_axi_problem("request_lifecycle_incomplete", "admitted request IDs do not equal request output rows"))
    tokens_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in token_rows:
        if isinstance(row.get("request_id"), str):
            tokens_by_id.setdefault(row["request_id"], []).append(row)
    emissions_by_id = {
        request_id: [row for row in rows if row.get("event_type") == "decode_emission"]
        for request_id, rows in by_request.items()
    }
    singleton_by_id = {
        request_id: [row for row in rows if row.get("event_type") == "token"]
        for request_id, rows in by_request.items()
    }
    for request_id in admitted:
        request_row = rows_by_id.get(request_id)
        terminal_event = terminal.get(request_id)
        if not isinstance(request_row, dict) or not isinstance(terminal_event, dict):
            continue
        request_tokens = tokens_by_id.get(request_id, [])
        ordinals = [row.get("output_token_ordinal") for row in request_tokens]
        if ordinals != list(range(len(request_tokens))):
            problems.append(_axi_problem("request_output_artifact_invalid", f"{request_id} token ordinals are not contiguous"))
        emissions = emissions_by_id.get(request_id, [])
        emission_ordinals = [event["metadata"].get("decode_step_ordinal") for event in emissions]
        if emission_ordinals != list(range(len(emissions))):
            problems.append(_axi_problem("request_counter_rollup_mismatch", f"{request_id} decode step ordinals invalid"))
        cumulative = 0
        proposed_total = 0
        accepted_total = 0
        target_total = 0
        for event in emissions:
            event_metadata = event["metadata"]
            if event_metadata.get("output_token_start_ordinal") != cumulative:
                problems.append(_axi_problem("request_counter_rollup_mismatch", f"{request_id} emission output slices are gapped"))
            count = event_metadata.get("emitted_count")
            if not isinstance(count, int) or isinstance(count, bool) or count < 1:
                continue
            slice_rows = request_tokens[cumulative : cumulative + count]
            ids = [row.get("token_id") for row in slice_rows]
            inline = event_metadata.get("emitted_token_ids")
            slice_hash = event_metadata.get("emitted_token_ids_sha256")
            if inline is not None and inline != ids:
                problems.append(_axi_problem("request_output_hash_mismatch", f"{request_id} inline emission IDs differ from token artifact"))
            if slice_hash is not None and (any(not isinstance(token_id, int) or isinstance(token_id, bool) for token_id in ids) or slice_hash != _axi_token_slice_sha256(ids)):
                problems.append(_axi_problem("request_output_hash_mismatch", f"{request_id} emission slice hash mismatch"))
            cumulative += count
            target_total += event_metadata.get("target_emitted_count", 0)
            if config.speculation.mode != "off":
                proposed_total += event_metadata.get("tokens_proposed", 0)
                accepted_total += event_metadata.get("tokens_accepted", 0)
        terminal_metadata = terminal_event["metadata"]
        cancelled = terminal_metadata.get("cancelled_proposal_counters")
        if isinstance(cancelled, dict):
            proposed_total += cancelled.get("tokens_proposed", 0)
            accepted_total += cancelled.get("tokens_accepted", 0)
            target_total += cancelled.get("target_emitted_count", 0)
        counts = {
            cumulative,
            len(request_tokens),
            request_row.get("output_token_count"),
            terminal_metadata.get("realized_output_token_count"),
        }
        if len(counts) != 1:
            problems.append(_axi_problem("request_output_count_mismatch", f"{request_id} emission/artifact/terminal counts disagree"))
        if request_row.get("target_emitted_count") != target_total:
            problems.append(_axi_problem("request_counter_rollup_mismatch", f"{request_id} target emitted rollup mismatch"))
        if config.speculation.mode != "off":
            expected_rate = accepted_total / proposed_total if proposed_total else None
            if (
                request_row.get("tokens_proposed") != proposed_total
                or request_row.get("tokens_accepted") != accepted_total
                or request_row.get("acceptance_rate") != expected_rate
            ):
                problems.append(_axi_problem("request_counter_rollup_mismatch", f"{request_id} proposal/acceptance rollup mismatch"))
        complete_ids = [row.get("token_id") for row in request_tokens]
        if all(isinstance(token_id, int) and not isinstance(token_id, bool) for token_id in complete_ids):
            if request_row.get("emitted_token_ids_sha256") != _axi_token_sequence_sha256(complete_ids):
                problems.append(_axi_problem("request_output_hash_mismatch", f"{request_id} complete token hash mismatch"))
        elif request_row.get("emitted_token_ids_sha256") is not None:
            problems.append(_axi_problem("request_output_hash_mismatch", f"{request_id} token hash present with unavailable ID"))
        singleton_events = singleton_by_id.get(request_id, [])
        singleton_ordinals = [
            event["metadata"].get("output_token_ordinal")
            for event in singleton_events
        ]
        if len(singleton_ordinals) != len(set(singleton_ordinals)):
            problems.append(
                _axi_problem(
                    "request_output_artifact_invalid",
                    f"{request_id} has duplicate singleton token callbacks",
                )
            )
        singleton_by_ordinal = {
            event["metadata"].get("output_token_ordinal"): event
            for event in singleton_events
        }
        expected_callback_ordinals = [
            token_row.get("output_token_ordinal")
            for token_row in request_tokens
            if token_row.get("timestamp_s") is not None
        ]
        if sorted(singleton_ordinals) != expected_callback_ordinals:
            problems.append(
                _axi_problem(
                    "request_output_artifact_invalid",
                    f"{request_id} singleton callback coverage differs from timestamped token rows",
                )
            )
        for token_row in request_tokens:
            callback = singleton_by_ordinal.get(token_row.get("output_token_ordinal"))
            if (
                token_row.get("request_ordinal") != request_row.get("request_ordinal")
                or token_row.get("request_input_id") != request_row.get("request_input_id")
            ):
                problems.append(
                    _axi_problem(
                        "request_identity_mismatch",
                        f"{request_id} token row identity differs from request row",
                    )
                )
            if token_row.get("timestamp_s") is None:
                if callback is not None:
                    problems.append(_axi_problem("request_output_artifact_invalid", f"{request_id} callback exists for null timestamp row"))
                continue
            if (
                callback is None
                or callback.get("timestamp_s") != token_row.get("timestamp_s")
                or callback["metadata"].get("token_id") != token_row.get("token_id")
                or callback["metadata"].get("decode_step_ordinal")
                != token_row.get("decode_step_ordinal")
            ):
                problems.append(_axi_problem("request_output_artifact_invalid", f"{request_id} singleton token callback mismatch"))
        roster_row = roster_by_ordinal.get(request_row.get("request_ordinal"))
        expected_group = (
            None
            if config.batch_policy.mode == "single_request"
            else metadata["batch"].get("batch_group_id")
        )
        if (
            roster_row is None
            or request_row.get("request_input_id") != roster_row.request_input_id
            or request_row.get("prompt_sha256") != roster_row.prompt_sha256
            or request_row.get("output_policy_name") != roster_row.output_policy_name
            or request_row.get("requested_output_tokens") != roster_row.requested_output_tokens
            or request_row.get("request_roster_sha256") != roster_hash
            or request_row.get("batch_group_id") != expected_group
        ):
            problems.append(_axi_problem("request_identity_mismatch", f"{request_id} request row differs from roster"))
        if request_row.get("terminal_status") != terminal_metadata.get("terminal_status") or request_row.get("stop_reason") != terminal_metadata.get("stop_reason") or request_row.get("failure_reason") != terminal_metadata.get("failure_reason"):
            problems.append(_axi_problem("request_lifecycle_incomplete", f"{request_id} terminal row/event mismatch"))
        if request_row.get("terminal_status") == "succeeded" and request_row.get("requested_output_tokens") is not None and (
            request_row.get("output_token_count") != request_row.get("requested_output_tokens")
            or request_row.get("stop_reason") != "requested_tokens_emitted"
        ):
            problems.append(_axi_problem("request_output_count_mismatch", f"{request_id} fixed-budget-exact success is not exact"))
        if request_row.get("terminal_status") == "cancelled_after_proposal_before_output" and (
            request_row.get("output_token_count") != 0
            or request_tokens
            or emissions
            or terminal_metadata.get("realized_output_token_count") != 0
            or request_row.get("acceptance_rate") != 0.0
        ):
            problems.append(
                _axi_problem(
                    "cancelled_proposal_evidence_lost",
                    f"{request_id} cancelled proposal terminal retains output evidence",
                )
            )

    batch = metadata.get("batch") if isinstance(metadata, dict) else None
    if isinstance(batch, dict):
        submitted_ids = {request_id for request_id, rows in by_request.items() if any(row["event_type"] == "request_submitted" for row in rows)}
        terminal_ids = set(terminal)
        expected = {
            "configured_batch_size": config.batch_policy.requested_batch_size,
            "realized_batch_size": len(admitted),
            "submitted_request_count": len(submitted_ids),
            "admitted_request_count": len(admitted),
            "terminal_request_count": len(terminal_ids),
            "request_roster_sha256": roster_hash,
        }
        if any(batch.get(key) != value for key, value in expected.items()):
            problems.append(_axi_problem("batch_observation_mismatch", "metadata batch observations disagree with lifecycle/roster"))

    try:
        trace_rows = reader.trace_rows()
    except BundleReadError as exc:
        return problems + [_axi_problem("primary_source_identity_unresolved", str(exc))]
    trace_sources = {row.get("source") for row in trace_rows if isinstance(row.get("source"), str)}
    primary_source = runtime.get("primary_source_identity") if isinstance(runtime, dict) else None
    if primary_source not in trace_sources:
        problems.append(_axi_problem("primary_source_identity_unresolved", "primary source has no telemetry binding"))
    for event in request_events:
        source = event["metadata"].get("source_identity")
        if source not in trace_sources:
            problems.append(_axi_problem("event_source_identity_unresolved", f"event source {source!r} has no telemetry binding"))
            break
    if isinstance(summary, dict) and summary.get("status") == "succeeded":
        failed = [request_id for request_id in admitted if isinstance(rows_by_id.get(request_id), dict) and rows_by_id[request_id].get("terminal_status") != "succeeded"]
        if failed:
            problems.append(_axi_problem("request_lifecycle_incomplete", f"succeeded bundle has non-succeeded admitted requests: {failed}"))
        summary_rollup = summary.get("decode_counter_rollup")
        if not allow_unfinalized_summary and isinstance(summary_rollup, dict):
            totals = {
                "emitted_count": sum(row.get("output_token_count", 0) for row in request_rows),
                "target_emitted_count": sum(row.get("target_emitted_count", 0) for row in request_rows),
            }
            if config.speculation.mode == "off":
                totals.update(tokens_proposed=None, tokens_accepted=None, acceptance_rate=None)
            else:
                proposed = sum(row.get("tokens_proposed", 0) for row in request_rows)
                accepted = sum(row.get("tokens_accepted", 0) for row in request_rows)
                totals.update(tokens_proposed=proposed, tokens_accepted=accepted, acceptance_rate=(accepted / proposed if proposed else None))
            if summary_rollup != totals:
                problems.append(_axi_problem("request_counter_rollup_mismatch", "summary decode counter rollup differs from request rows"))
    # Preserve deterministic first occurrence while suppressing a flood of
    # identical source/identity diagnostics from one malformed fixture.
    return list(dict.fromkeys(problems))


@dataclass(frozen=True)
class _TraceValidation:
    totals: dict[float, float]
    supports: dict[float, tuple[float, float]]
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


def _is_decode_token_event(event: dict[str, Any], pairing: _PhasePairing) -> bool:
    if event.get("event_type") != "token" or event.get("phase") != "decode":
        return False
    if not pairing.windows_by_phase.get("decode"):
        return True
    decode_windows = pairing.windows_for_event("decode", event)
    timestamp_s = float(event["timestamp_s"])
    return any(
        window.start_s <= timestamp_s <= window.end_s for window in decode_windows
    )


_PHASE_SOURCE_METADATA_KEYS = ("node_id", "node_identity")


def _phase_source_identity(event: dict[str, Any]) -> _PhaseSourceIdentity:
    metadata = event.get("metadata")
    if not isinstance(metadata, dict):
        return ()
    identity: list[tuple[str, str]] = []
    for key in _PHASE_SOURCE_METADATA_KEYS:
        value = metadata.get(key)
        if value is None:
            continue
        identity.append(
            (
                key,
                json.dumps(
                    value,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        )
    # WO-006: split-node streams sometimes have no stable node identifier and
    # node_role is then their only discriminator.  Prefer an explicit node
    # identity when one exists; contradictory role labels must not split one
    # identified meter/source into parallel streams.
    if not identity and metadata.get("node_role") is not None:
        identity.append(
            (
                "node_role",
                json.dumps(
                    metadata["node_role"],
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        )
    return tuple(identity)


def _phase_source_label(identity: _PhaseSourceIdentity) -> str:
    if not identity:
        return "default power source"
    return "power source " + ", ".join(
        f"{key}={value}" for key, value in identity
    )


def _pair_phase_windows(events: list[dict[str, Any]]) -> _PhasePairing:
    """Validate and pair runtime phase markers through one shared policy."""
    open_starts: dict[
        tuple[str, _PhaseSourceIdentity], list[tuple[float, int]]
    ] = {}
    intervals: list[_PairedPhaseInterval] = []
    problems: list[str] = []

    for index, event in enumerate(events, start=1):
        event_type = event.get("event_type")
        if event_type not in {"phase_start", "phase_end"}:
            continue
        phase = event.get("phase")
        if not isinstance(phase, str) or not phase:
            problems.append(
                f"{event_type} marker at event {index} has a missing or non-string phase"
            )
            continue
        if not isinstance(event.get("metadata"), dict):
            problems.append(
                f"{event_type} marker for phase {phase!r} at event {index} "
                "has metadata that is not an object"
            )
            continue
        source_identity = _phase_source_identity(event)
        key = (phase, source_identity)
        timestamp_s = float(event["timestamp_s"])
        if event_type == "phase_start":
            open_starts.setdefault(key, []).append((timestamp_s, index))
            continue

        starts = open_starts.get(key)
        if not starts:
            problems.append(
                f"phase_end marker for phase {phase!r} on "
                f"{_phase_source_label(source_identity)} has no paired phase_start"
            )
            continue
        start_s, _start_index = starts.pop(0)
        if timestamp_s < start_s:
            problems.append(
                f"phase markers are reversed for phase {phase!r} on "
                f"{_phase_source_label(source_identity)}: "
                f"start {start_s} > end {timestamp_s}"
            )
            continue
        intervals.append(
            _PairedPhaseInterval(
                phase=phase,
                source_identity=source_identity,
                window=Window(start_s=start_s, end_s=timestamp_s),
            )
        )

    for (phase, source_identity), starts in open_starts.items():
        for _start_s, _start_index in starts:
            problems.append(
                f"phase_start marker for phase {phase!r} on "
                f"{_phase_source_label(source_identity)} has no paired phase_end"
            )

    by_source: dict[_PhaseSourceIdentity, list[_PairedPhaseInterval]] = {}
    for interval in intervals:
        by_source.setdefault(interval.source_identity, []).append(interval)
    for source_identity, source_intervals in by_source.items():
        ordered = sorted(
            source_intervals,
            key=lambda interval: (
                interval.window.start_s,
                interval.window.end_s,
                interval.phase,
            ),
        )
        active: _PairedPhaseInterval | None = None
        for interval in ordered:
            if active is not None and interval.window.start_s < active.window.end_s:
                problems.append(
                    "same_source_phase_overlap: phase intervals overlap on "
                    f"{_phase_source_label(source_identity)}: "
                    f"{active.phase!r} [{active.window.start_s}, {active.window.end_s}] "
                    f"overlaps {interval.phase!r} "
                    f"[{interval.window.start_s}, {interval.window.end_s}]"
                )
            if active is None or interval.window.end_s > active.window.end_s:
                active = interval

    windows_by_phase: dict[str, list[Window]] = {}
    windows_by_key: dict[tuple[str, _PhaseSourceIdentity], list[Window]] = {}
    for interval in intervals:
        windows_by_phase.setdefault(interval.phase, []).append(interval.window)
        windows_by_key.setdefault(
            (interval.phase, interval.source_identity), []
        ).append(interval.window)
    return _PhasePairing(
        windows_by_phase=windows_by_phase,
        windows_by_key=windows_by_key,
        problems=problems,
    )


def _paired_group_windows(
    events: list[dict[str, Any]],
    start_event: str,
    end_event: str,
    id_key: str,
) -> dict[str, list[Window]]:
    open_starts: dict[str, list[float]] = {}
    windows: dict[str, list[Window]] = {}
    for event in events:
        metadata = event.get("metadata")
        if not isinstance(metadata, dict):
            continue
        group_id = metadata.get(id_key)
        if not isinstance(group_id, str):
            continue
        event_type = event.get("event_type")
        if event_type == start_event:
            open_starts.setdefault(group_id, []).append(float(event["timestamp_s"]))
        elif event_type == end_event:
            starts = open_starts.get(group_id)
            if not starts:
                continue
            windows.setdefault(group_id, []).append(
                Window(start_s=starts.pop(0), end_s=float(event["timestamp_s"]))
            )
    return windows


def _has_suite_contract(path: Path, raw_config: Any) -> bool:
    if (path / "suite_manifest.json").is_file():
        return True
    if isinstance(raw_config, dict):
        workload = raw_config.get("workload_profile")
        return isinstance(workload, dict) and workload.get("suite_manifest_ref") is not None
    return False


def _suite_problems(
    reader: BundleReader,
    raw_config: Any,
    metadata: Any,
    summary: Any,
) -> list[str]:
    problems: list[str] = []
    artifact_exists = (reader.path / "suite_manifest.json").is_file()
    raw_status = summary.get("status") if isinstance(summary, dict) else None
    status_is_success = raw_status == RunStatus.SUCCEEDED.value
    events: list[dict[str, Any]] | None = None

    config: BenchmarkConfig | None = None
    if isinstance(raw_config, dict):
        try:
            config = BenchmarkConfig.from_mapping(raw_config)
        except SchemaError:
            config = None
    config_ref = (
        config.workload_profile.suite_manifest_ref if config is not None else None
    )
    config_hash = (
        config.workload_profile.suite_manifest_sha256 if config is not None else None
    )

    if config_ref is None and artifact_exists:
        problems.append(
            "suite_manifest.json is present but config.workload_profile."
            "suite_manifest_ref is absent"
        )
    if config_ref is not None and not artifact_exists:
        try:
            events = reader.events()
        except BundleReadError as exc:
            return [str(exc)]
        # D-011/D-012: validate-stage failures occur before prepare writes the
        # manifest. Missing suite_manifest.json becomes a suite artifact
        # problem only after a successful summary, or after prepare started.
        if status_is_success or _run_reached_prepare(events):
            problems.append(
                "config.workload_profile.suite_manifest_ref is set but "
                "suite_manifest.json is missing"
            )
        return problems
    if not artifact_exists:
        return problems

    try:
        raw_manifest = json.loads((reader.path / "suite_manifest.json").read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"suite_manifest.json is not valid JSON: {exc}"]
    try:
        manifest = SuiteManifest.from_mapping(raw_manifest)
        effective = canonical_effective_manifest(raw_manifest)
        actual_hash = suite_manifest_sha256(effective)
    except SchemaError as exc:
        return [f"suite_manifest.json does not re-validate: {exc}"]

    accepted_config_hashes = {actual_hash}
    if manifest.schema_version != LEGACY_SUITE_SCHEMA_VERSION:
        # New bundles may originate from a hash-pinned v1 source. The
        # registered config remains byte-stable while the persisted artifact
        # is v2; this deterministic projection authenticates that migration.
        accepted_config_hashes.add(
            suite_manifest_sha256(
                manifest.to_dict(schema_version=LEGACY_SUITE_SCHEMA_VERSION)
            )
        )
    if config_hash is not None and config_hash not in accepted_config_hashes:
        problems.append(
            "config.workload_profile.suite_manifest_sha256 mismatch: "
            f"config has {config_hash!r}, suite_manifest.json hashes to {actual_hash!r}"
        )
    suite_metadata = metadata.get("suite") if isinstance(metadata, dict) else None
    if not isinstance(suite_metadata, dict):
        problems.append("metadata.suite is missing or not an object")
    else:
        problems.extend(_metadata_suite_problems(suite_metadata, manifest))
        metadata_hash = suite_metadata.get("manifest_sha256")
        if metadata_hash != actual_hash:
            problems.append(
                "metadata.suite.manifest_sha256 mismatch: "
                f"metadata has {metadata_hash!r}, suite_manifest.json hashes to {actual_hash!r}"
            )

    if events is None:
        try:
            events = reader.events()
        except BundleReadError as exc:
            return problems + [str(exc)]

    suite_window = reader.suite_window()
    if suite_window is None:
        problems.append("suite markers are missing a paired suite_start/suite_end window")
    else:
        measured = reader.measured_window()
        if measured is not None and not _window_contains(measured, suite_window):
            problems.append("suite window is not inside the measured window")

    problems.extend(_marker_pair_problems(events, SUITE_START, SUITE_END, "suite"))
    problems.extend(_marker_pair_problems(events, BLOCK_START, BLOCK_END, "block_id"))
    problems.extend(_marker_pair_problems(events, LEVEL_START, LEVEL_END, "level_id"))
    problems.extend(_item_marker_pair_problems(events))
    problems.extend(_suite_summary_metrics_problems(summary))

    suite_start_metadata = _first_marker_metadata(events, SUITE_START)
    order_row, order_row_problems = _suite_order_row_for_validation(
        manifest, suite_metadata, suite_start_metadata
    )
    problems.extend(order_row_problems)
    if order_row is not None and isinstance(suite_metadata, dict):
        expected_order_seed = order_seed(
            manifest.suite_seed,
            manifest.execution_policy.order_policy,
            order_row,
        )
        if suite_metadata.get("order_seed") != expected_order_seed:
            problems.append(
                "metadata.suite.order_seed does not match derived order seed: "
                f"expected {expected_order_seed!r} from suite_seed, order_policy, "
                f"and order_row {order_row!r}; got {suite_metadata.get('order_seed')!r}"
            )

    item_start_indices: list[int] = []
    item_start_positions: list[int] = []
    item_start_order: list[dict[str, Any]] = []
    start_by_index: dict[int, dict[str, Any]] = {}
    start_by_position: dict[int, dict[str, Any]] = {}
    for event in events:
        if event.get("event_type") != ITEM_START:
            continue
        metadata = event.get("metadata")
        if not isinstance(metadata, dict):
            continue
        index = metadata.get("item_index")
        if isinstance(index, bool) or not isinstance(index, int):
            problems.append(f"item_start.item_index is not an integer: {index!r}")
            continue
        item_start_indices.append(index)
        if index in start_by_index:
            problems.append(f"item_index is duplicated in item_start markers: {index}")
        start_by_index[index] = metadata
        position = metadata.get("position")
        if isinstance(position, bool) or not isinstance(position, int):
            problems.append(f"item_start.position is not an integer: {position!r}")
            continue
        item_start_positions.append(position)
        item_start_order.append(metadata)
        if position in start_by_position:
            problems.append(f"position is duplicated in item_start markers: {position}")
        start_by_position[position] = metadata
    expected_positions = list(range(len(manifest.items)))
    if item_start_positions != expected_positions:
        problems.append(
            "item_start.position values are not the realized execution order "
            f"0..{len(manifest.items) - 1}: {item_start_positions!r}"
        )
    if set(start_by_position) != set(expected_positions):
        missing_positions = sorted(set(expected_positions) - set(start_by_position))
        extra_positions = sorted(set(start_by_position) - set(expected_positions))
        if missing_positions:
            problems.append(f"item_start marker position(s) missing: {missing_positions}")
        if extra_positions:
            problems.append(f"item_start marker position(s) outside range: {extra_positions}")

    expected_item_indices_for_order: list[int] | None = None
    if order_row is not None or manifest.execution_policy.order_policy == "manifest_order":
        try:
            expected_order = realized_order(manifest, order_row=order_row)
        except SchemaError as exc:
            problems.append(f"suite realized order cannot be derived: {exc}")
            expected_order = []
        if expected_order:
            expected_item_indices = [entry.item_index for entry in expected_order]
            expected_item_indices_for_order = expected_item_indices
            actual_item_indices = [
                metadata.get("item_index") for metadata in item_start_order
            ]
            if actual_item_indices != expected_item_indices:
                problems.append(
                    "realized item_start order mismatch: expected manifest item_index "
                    f"sequence {expected_item_indices!r}, got {actual_item_indices!r}"
                )
            expected_by_position = {entry.position: entry for entry in expected_order}
            for metadata in item_start_order:
                position = metadata.get("position")
                if not isinstance(position, int) or isinstance(position, bool):
                    continue
                expected_entry = expected_by_position.get(position)
                if expected_entry is None:
                    continue
                if metadata.get("item_id") != expected_entry.item.item_id:
                    problems.append(
                        f"item_start position {position} item_id mismatch: expected "
                        f"{expected_entry.item.item_id!r}, got {metadata.get('item_id')!r}"
                    )
            for position, metadata in enumerate(item_start_order):
                expected_prev = None if position == 0 else item_start_order[position - 1].get("item_id")
                if metadata.get("prev_item") != expected_prev:
                    problems.append(
                        f"item_start position {position} prev_item mismatch: expected "
                        f"{expected_prev!r}, got {metadata.get('prev_item')!r}"
                    )

    measured_window = reader.measured_window()
    paired_items = {window.item_index: window for window in reader.item_windows()}
    expected_indices = set(range(len(manifest.items)))
    if set(paired_items) != expected_indices:
        missing = sorted(expected_indices - set(paired_items))
        extra = sorted(set(paired_items) - expected_indices)
        if missing:
            problems.append(f"manifest item(s) missing paired item markers: {missing}")
        if extra:
            problems.append(f"paired item marker(s) outside manifest item_index range: {extra}")

    block_windows = reader.block_windows()
    level_windows = reader.level_windows()
    manifest_block_ids = sorted({item.grouping.block_id for item in manifest.items})
    manifest_level_keys = sorted(
        {(item.grouping.block_id, item.grouping.level_id) for item in manifest.items}
    )
    for block_id in manifest_block_ids:
        if not block_windows.get(block_id):
            problems.append(
                f"manifest block_id {block_id!r} is missing paired block markers"
            )
    for block_id, level_id in manifest_level_keys:
        if not level_windows.get((block_id, level_id)):
            problems.append(
                "manifest level grouping "
                f"{(block_id, level_id)!r} is missing paired level markers"
            )

    suite_item_records, record_problems = _suite_item_records(reader.path)
    problems.extend(record_problems)
    if suite_item_records is not None:
        records_by_index: dict[int, dict[str, Any]] = {}
        record_positions: list[int] = []
        record_item_indices: list[int] = []
        for line_index, record in enumerate(suite_item_records, start=1):
            item_index = record.get("item_index")
            if isinstance(item_index, bool) or not isinstance(item_index, int):
                problems.append(
                    "outputs/suite_items.jsonl line "
                    f"{line_index} item_index is not an integer: {item_index!r}"
                )
                continue
            if item_index in records_by_index:
                problems.append(
                    "outputs/suite_items.jsonl duplicates item_index "
                    f"{item_index}"
                )
            records_by_index[item_index] = record
            record_item_indices.append(item_index)
            emitted_tokens = record.get("emitted_tokens")
            if (
                isinstance(emitted_tokens, bool)
                or not isinstance(emitted_tokens, int)
                or emitted_tokens < 0
            ):
                problems.append(
                    "outputs/suite_items.jsonl line "
                    f"{line_index} emitted_tokens is not a non-negative integer: "
                    f"{emitted_tokens!r}"
                )
            stop_reason = record.get("stop_reason")
            if not _nonempty_string(stop_reason):
                problems.append(
                    "outputs/suite_items.jsonl line "
                    f"{line_index} stop_reason is not a non-empty string: "
                    f"{stop_reason!r}"
                )
            tokens = record.get("tokens")
            if not isinstance(tokens, list):
                problems.append(
                    f"outputs/suite_items.jsonl line {line_index} tokens is not a list"
                )
            elif (
                record.get("emitted_token_ids") is None
                and isinstance(emitted_tokens, int)
                and not isinstance(emitted_tokens, bool)
            ):
                if len(tokens) != emitted_tokens:
                    problems.append(
                        "outputs/suite_items.jsonl line "
                        f"{line_index} tokens length {len(tokens)} does not equal "
                        f"emitted_tokens {emitted_tokens}"
                    )
            emitted_token_ids = record.get("emitted_token_ids")
            if emitted_token_ids is not None:
                if not isinstance(emitted_token_ids, list):
                    problems.append(
                        "outputs/suite_items.jsonl line "
                        f"{line_index} emitted_token_ids is not a list"
                    )
                elif isinstance(emitted_tokens, int) and not isinstance(
                    emitted_tokens, bool
                ) and len(emitted_token_ids) != emitted_tokens:
                    problems.append(
                        "outputs/suite_items.jsonl line "
                        f"{line_index} emitted_token_ids length {len(emitted_token_ids)} "
                        f"does not equal emitted_tokens {emitted_tokens}"
                    )
            position = record.get("position")
            if position is not None:
                if isinstance(position, bool) or not isinstance(position, int):
                    problems.append(
                        "outputs/suite_items.jsonl line "
                        f"{line_index} position is not an integer: {position!r}"
                    )
                else:
                    record_positions.append(position)
        if manifest.execution_policy.order_policy != "manifest_order":
            if len(record_positions) != len(suite_item_records):
                problems.append(
                    "outputs/suite_items.jsonl records must include position under "
                    f"order_policy {manifest.execution_policy.order_policy!r}"
                )
            elif record_positions != expected_positions:
                problems.append(
                    "outputs/suite_items.jsonl position values are not realized "
                    f"execution order 0..{len(manifest.items) - 1}: {record_positions!r}"
                )
            if (
                expected_item_indices_for_order is not None
                and record_item_indices != expected_item_indices_for_order
            ):
                problems.append(
                    "outputs/suite_items.jsonl realized item_index order mismatch: "
                    f"expected {expected_item_indices_for_order!r}, got {record_item_indices!r}"
                )
        for item_index, item in enumerate(manifest.items):
            if item.source.prompt_token_ids is None and item.source.prompt_text is None:
                continue
            record = records_by_index.get(item_index)
            if record is None:
                problems.append(
                    "outputs/suite_items.jsonl is missing item_index "
                    f"{item_index} for prompt source validation"
                )
                continue
            prompt = record.get("prompt")
            actual = prompt.get("token_ids_sha256") if isinstance(prompt, dict) else None
            if item.source.prompt_token_ids is not None:
                expected_hash = prompt_token_ids_sha256(item.source.prompt_token_ids)
                if actual != expected_hash:
                    problems.append(
                        "outputs/suite_items.jsonl item_index "
                        f"{item_index} prompt.token_ids_sha256 mismatch for ids-native "
                        f"manifest prompt_token_ids: expected {expected_hash!r}, "
                        f"actual {actual!r}"
                    )
            else:
                source_hash = normalized_sha256_hex(item.source.source_sha256)
                if source_hash is None:
                    continue
                text_hash = sha256_hex(item.source.prompt_text or "")
                if actual != source_hash and text_hash != source_hash:
                    problems.append(
                        "outputs/suite_items.jsonl item_index "
                        f"{item_index} prompt.token_ids_sha256 mismatch for text "
                        "manifest prompt source: source_sha256 is neither realized "
                        "prompt token-ID hash nor prompt text hash; "
                        f"source_sha256 {source_hash!r}, "
                        f"actual {actual!r}, text_sha256 {text_hash!r}"
                    )

    if isinstance(suite_metadata, dict):
        if isinstance(suite_start_metadata, dict):
            if suite_metadata.get("order_seed") != suite_start_metadata.get("order_seed"):
                problems.append(
                    "metadata.suite.order_seed mismatch: metadata has "
                    f"{suite_metadata.get('order_seed')!r}, suite_start metadata has "
                    f"{suite_start_metadata.get('order_seed')!r}"
                )
            if suite_metadata.get("order_row") != suite_start_metadata.get("order_row"):
                problems.append(
                    "metadata.suite.order_row mismatch: metadata has "
                    f"{suite_metadata.get('order_row')!r}, suite_start metadata has "
                    f"{suite_start_metadata.get('order_row')!r}"
                )
        suite_end_metadata = _first_marker_metadata(events, SUITE_END)
        if isinstance(suite_end_metadata, dict):
            expected_counts = _status_counts_from_windows(list(paired_items.values()))
            if suite_end_metadata.get("items_executed") != len(paired_items):
                problems.append(
                    "suite_end.metadata.items_executed mismatch: suite_end has "
                    f"{suite_end_metadata.get('items_executed')!r}, paired item "
                    f"windows count is {len(paired_items)}"
                )
            if suite_end_metadata.get("status_counts") != expected_counts:
                problems.append(
                    "suite_end.metadata.status_counts mismatch: suite_end has "
                    f"{suite_end_metadata.get('status_counts')!r}, paired item "
                    f"windows status counts are {expected_counts!r}"
                )

    assignable = {status.value for status in RUNTIME_ASSIGNABLE}
    for window in paired_items.values():
        if window.status not in assignable:
            problems.append(
                f"item_end.status for item_index {window.item_index} is not "
                f"runtime-assignable: {window.status!r}"
            )
        if measured_window is not None and not _window_contains(measured_window, window.window):
            problems.append(
                f"item_index {window.item_index} window is not inside the measured window"
            )
        if suite_window is not None and not _window_contains(suite_window, window.window):
            problems.append(
                f"item_index {window.item_index} window is not inside the suite window"
            )
        expected = manifest.items[window.item_index] if window.item_index < len(manifest.items) else None
        if expected is not None:
            if window.item_id != expected.item_id:
                problems.append(
                    f"item_index {window.item_index} item_id mismatch: "
                    f"manifest has {expected.item_id!r}, events have {window.item_id!r}"
                )
            start_position = window.start_metadata.get("position")
            end_position = window.end_metadata.get("position")
            if manifest.execution_policy.order_policy != "manifest_order":
                if isinstance(start_position, bool) or not isinstance(start_position, int):
                    problems.append(
                        f"item_start.position for item_index {window.item_index} "
                        f"is not an integer: {start_position!r}"
                    )
                if isinstance(end_position, bool) or not isinstance(end_position, int):
                    problems.append(
                        f"item_end.position for item_index {window.item_index} "
                        f"is not an integer: {end_position!r}"
                    )
            if start_position is not None and end_position is not None and start_position != end_position:
                problems.append(
                    f"item_index {window.item_index} position mismatch between "
                    f"item_start ({start_position!r}) and item_end ({end_position!r})"
                )
            if (
                window.start_metadata.get("output_policy") == "fixed_budget_exact"
                and window.status == "succeeded"
                and window.end_metadata.get("emitted_tokens")
                != window.start_metadata.get("planned_output_tokens")
            ):
                problems.append(
                    "fixed_budget_exact item succeeded with emitted_tokens != "
                    f"planned_output_tokens at item_index {window.item_index}"
                )

    if suite_window is not None:
        for block_id, windows in block_windows.items():
            for window in windows:
                if not _window_contains(suite_window, window):
                    problems.append(f"block {block_id!r} window is not inside the suite window")
        for (block_id, level_id), windows in level_windows.items():
            containers = block_windows.get(block_id, [])
            for window in windows:
                if not _window_contains(suite_window, window):
                    problems.append(
                        f"level {(block_id, level_id)!r} window is not inside the suite window"
                    )
                if containers and not any(_window_contains(block, window) for block in containers):
                    problems.append(
                        f"level {(block_id, level_id)!r} window is not inside its block window"
                    )

    return problems


def _run_reached_prepare(events: list[dict[str, Any]]) -> bool:
    return any(
        event.get("phase") == "prepare"
        and event.get("event_type") in {"stage_started", "stage_completed"}
        for event in events
    )


def _metadata_suite_problems(
    suite_metadata: dict[str, Any], manifest: SuiteManifest
) -> list[str]:
    problems: list[str] = []
    required = {
        "suite_id",
        "suite_profile",
        "suite_revision",
        "manifest_sha256",
        "source_file_sha256",
        "item_count",
        "order_seed",
    }
    missing = sorted(required - set(suite_metadata))
    for key in missing:
        problems.append(f"metadata.suite.{key} is missing")
    for key in ("suite_id", "suite_profile", "suite_revision", "manifest_sha256", "order_seed"):
        if key in suite_metadata and not _nonempty_string(suite_metadata.get(key)):
            problems.append(f"metadata.suite.{key} is not a non-empty string: {suite_metadata.get(key)!r}")
    source_hash = suite_metadata.get("source_file_sha256")
    if "source_file_sha256" in suite_metadata and not _sha256_hex(source_hash):
        problems.append(
            "metadata.suite.source_file_sha256 is not a 64-character hex string: "
            f"{source_hash!r}"
        )
    item_count = suite_metadata.get("item_count")
    if isinstance(item_count, bool) or not isinstance(item_count, int):
        if "item_count" in suite_metadata:
            problems.append(f"metadata.suite.item_count is not an integer: {item_count!r}")
    elif item_count != len(manifest.items):
        problems.append(
            f"metadata.suite.item_count mismatch: metadata has {item_count!r}, "
            f"suite_manifest.json has {len(manifest.items)} item(s)"
        )
    expected_strings = {
        "suite_id": manifest.suite_id,
        "suite_profile": manifest.suite_profile,
        "suite_revision": manifest.suite_revision,
    }
    for key, expected in expected_strings.items():
        actual = suite_metadata.get(key)
        if isinstance(actual, str) and actual != expected:
            problems.append(
                f"metadata.suite.{key} mismatch: metadata has {actual!r}, "
                f"suite_manifest.json has {expected!r}"
            )
    order_policy = suite_metadata.get("order_policy")
    if order_policy is not None:
        if not isinstance(order_policy, str) or not order_policy:
            problems.append(f"metadata.suite.order_policy is not a non-empty string: {order_policy!r}")
        elif order_policy != manifest.execution_policy.order_policy:
            problems.append(
                "metadata.suite.order_policy mismatch: metadata has "
                f"{order_policy!r}, suite_manifest.json has "
                f"{manifest.execution_policy.order_policy!r}"
            )
    order_row = suite_metadata.get("order_row")
    if order_row is not None and (
        isinstance(order_row, bool) or not isinstance(order_row, int) or order_row < 0
    ):
        problems.append(f"metadata.suite.order_row is not an integer >= 0: {order_row!r}")
    return problems


def _suite_order_row_for_validation(
    manifest: SuiteManifest,
    suite_metadata: Any,
    suite_start_metadata: Any,
) -> tuple[int | None, list[str]]:
    problems: list[str] = []
    metadata_row = (
        suite_metadata.get("order_row") if isinstance(suite_metadata, dict) else None
    )
    start_row = (
        suite_start_metadata.get("order_row")
        if isinstance(suite_start_metadata, dict)
        else None
    )
    row = metadata_row if metadata_row is not None else start_row
    policy = manifest.execution_policy.order_policy
    if policy != "manifest_order" and row is None:
        problems.append(f"order_row is required for order_policy {policy!r}")
        return None, problems
    if row is None:
        return None, problems
    if isinstance(row, bool) or not isinstance(row, int) or row < 0:
        problems.append(f"order_row is not an integer >= 0: {row!r}")
        return None, problems
    return row, problems


def _suite_summary_metrics_problems(summary: Any) -> list[str]:
    if not isinstance(summary, dict):
        return []
    suite_metrics = summary.get("suite_metrics")
    if suite_metrics is None:
        return []
    if not isinstance(suite_metrics, dict):
        return ["summary_metrics.json suite_metrics is not an object"]
    assignable = {status.value for status in REDUCER_ASSIGNABLE}
    problems: list[str] = []
    problems.extend(
        _status_count_key_problems(
            suite_metrics.get("status_counts"),
            "summary_metrics.json suite_metrics.status_counts",
            assignable,
        )
    )
    for surface in ("blocks", "levels"):
        groups = suite_metrics.get(surface)
        if groups is None:
            continue
        if not isinstance(groups, list):
            problems.append(f"summary_metrics.json suite_metrics.{surface} is not a list")
            continue
        for index, group in enumerate(groups):
            if not isinstance(group, dict):
                problems.append(
                    f"summary_metrics.json suite_metrics.{surface}[{index}] "
                    "is not an object"
                )
                continue
            problems.extend(
                _status_count_key_problems(
                    group.get("status_counts"),
                    "summary_metrics.json suite_metrics."
                    f"{surface}[{index}].status_counts",
                    assignable,
                )
            )
    items = suite_metrics.get("items")
    if items is None:
        return problems
    if not isinstance(items, list):
        return problems + ["summary_metrics.json suite_metrics.items is not a list"]
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            problems.append(
                f"summary_metrics.json suite_metrics.items[{index}] is not an object"
            )
            continue
        status = item.get("status")
        if status not in assignable:
            problems.append(
                "summary_metrics.json suite_metrics.items"
                f"[{index}].status is not reducer-assignable: {status!r}"
            )
    return problems


def _status_count_key_problems(
    status_counts: Any, path: str, assignable: set[str]
) -> list[str]:
    if status_counts is None:
        return []
    if not isinstance(status_counts, dict):
        return [f"{path} is not an object"]
    problems: list[str] = []
    for status in sorted(status_counts):
        if status not in assignable:
            problems.append(f"{path} contains non-reducer-assignable status: {status!r}")
    return problems


def _suite_item_records(path: Path) -> tuple[list[dict[str, Any]] | None, list[str]]:
    suite_items_path = path / "outputs" / "suite_items.jsonl"
    if not suite_items_path.is_file():
        return None, ["outputs/suite_items.jsonl is missing for suite bundle"]
    try:
        text = suite_items_path.read_text()
    except OSError as exc:
        return None, [f"outputs/suite_items.jsonl cannot be read: {exc}"]
    records: list[dict[str, Any]] = []
    problems: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(
                f"outputs/suite_items.jsonl line {index} is not valid JSON: {exc}"
            )
            continue
        if not isinstance(record, dict):
            problems.append(
                f"outputs/suite_items.jsonl line {index} is not a JSON object"
            )
            continue
        records.append(record)
    return records, problems


def _first_marker_metadata(
    events: list[dict[str, Any]], event_type: str
) -> dict[str, Any] | None:
    for event in events:
        if event.get("event_type") != event_type:
            continue
        metadata = event.get("metadata")
        return metadata if isinstance(metadata, dict) else None
    return None


def _status_counts_from_windows(windows: list[ItemWindow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for window in windows:
        counts[window.status] = counts.get(window.status, 0) + 1
    return counts


def _marker_required_metadata_problems(
    event_type: str, metadata: dict[str, Any]
) -> list[str]:
    required = MARKER_REQUIRED_METADATA_KEYS.get(event_type, frozenset())
    return [
        f"{event_type} marker metadata.{key} is missing"
        for key in sorted(required - set(metadata))
    ]


def _marker_identity(metadata: dict[str, Any], id_key: str) -> str | None:
    if id_key == "suite":
        return "__suite__"
    value = metadata.get(id_key)
    return value if isinstance(value, str) else None


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256_hex(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdefABCDEF" for char in value)
    )


def _marker_pair_problems(
    events: list[dict[str, Any]],
    start_event: str,
    end_event: str,
    id_key: str,
) -> list[str]:
    problems: list[str] = []
    stack: list[tuple[str, dict[str, Any]]] = []
    start_counts: dict[str, int] = {}
    end_counts: dict[str, int] = {}
    for event in events:
        event_type = event.get("event_type")
        if event_type not in {start_event, end_event}:
            continue
        metadata = event.get("metadata")
        if not isinstance(metadata, dict):
            problems.append(f"{event_type} marker metadata is missing or not an object")
            metadata = {}
        problems.extend(_marker_required_metadata_problems(event_type, metadata))
        marker_id = _marker_identity(metadata, id_key)
        if marker_id is None:
            marker_id = "<missing>"
            if id_key != "suite":
                problems.append(f"{event_type} marker metadata.{id_key} is missing or not a string")
        if event_type == start_event:
            stack.append((marker_id, event))
            start_counts[marker_id] = start_counts.get(marker_id, 0) + 1
            continue
        end_counts[marker_id] = end_counts.get(marker_id, 0) + 1
        if not stack:
            problems.append(f"{end_event} marker for {marker_id!r} has no paired {start_event}")
            continue
        open_id, _open_event = stack[-1]
        if open_id != marker_id:
            problems.append(
                f"{end_event} marker for {marker_id!r} closes while {start_event} "
                f"for {open_id!r} is still open"
            )
            matching_index = next(
                (
                    index
                    for index in range(len(stack) - 1, -1, -1)
                    if stack[index][0] == marker_id
                ),
                None,
            )
            if matching_index is not None:
                stack.pop(matching_index)
            else:
                problems.append(f"{end_event} marker for {marker_id!r} has no paired {start_event}")
            continue
        stack.pop()
    for marker_id in sorted(set(start_counts) | set(end_counts)):
        starts = start_counts.get(marker_id, 0)
        ends = end_counts.get(marker_id, 0)
        if starts != ends:
            problems.append(
                f"{start_event}/{end_event} marker count mismatch for "
                f"{marker_id!r}: starts={starts}, ends={ends}"
            )
    for marker_id, _event in stack:
        problems.append(f"{start_event} marker for {marker_id!r} has no paired {end_event}")
    return problems


def _item_marker_pair_problems(events: list[dict[str, Any]]) -> list[str]:
    open_starts: dict[str, list[dict[str, Any]]] = {}
    problems: list[str] = []
    for event in events:
        metadata = event.get("metadata")
        if not isinstance(metadata, dict):
            continue
        item_id = metadata.get("item_id")
        if not isinstance(item_id, str):
            continue
        event_type = event.get("event_type")
        if event_type == ITEM_START:
            open_starts.setdefault(item_id, []).append(event)
        elif event_type == ITEM_END:
            starts = open_starts.get(item_id, [])
            if not starts:
                problems.append(f"item_end marker for {item_id!r} has no paired item_start")
                continue
            start = starts.pop(0)
            start_metadata = start.get("metadata")
            start_index = start_metadata.get("item_index") if isinstance(start_metadata, dict) else None
            end_index = metadata.get("item_index")
            if start_index != end_index:
                problems.append(
                    f"item_start/item_end item_index mismatch for item_id {item_id!r}: "
                    f"start item_index {start_index!r}, end item_index {end_index!r}"
                )
    for item_id, starts in sorted(open_starts.items()):
        for _start in starts:
            problems.append(f"item_start marker for {item_id!r} has no paired item_end")
    return problems


def _window_contains(outer: Window, inner: Window) -> bool:
    return outer.start_s <= inner.start_s and inner.end_s <= outer.end_s


def _check_summary(summary: Any) -> list[str]:
    """Shared summary validity policy used by validation and completion."""
    return summary_validation_problems(summary)


def _validate_trace_rows(rows: list[dict[str, str]], manifest: list[str]) -> _TraceValidation:
    manifest_set = set(manifest)
    totals: dict[float, float] = {}
    supports: dict[float, tuple[float, float]] = {}
    rails_at: dict[float, set[str]] = {}
    support_modes_at: dict[float, set[bool]] = {}
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
            interval_start_raw = row.get("interval_start_s")
            interval_end_raw = row.get("interval_end_s")
            if interval_start_raw is None and interval_end_raw is None:
                support = None
            elif interval_start_raw is None or interval_end_raw is None:
                raise ValueError(
                    f"power_trace.csv row {index} must carry both interval support edges"
                )
            else:
                interval_start_s = finite_float(
                    interval_start_raw,
                    f"power_trace.csv row {index} interval_start_s",
                )
                interval_end_s = finite_float(
                    interval_end_raw,
                    f"power_trace.csv row {index} interval_end_s",
                )
                if interval_start_s >= interval_end_s:
                    raise ValueError(
                        f"power_trace.csv row {index} interval support must have "
                        "start < end"
                    )
                if interval_end_s != timestamp_s:
                    raise ValueError(
                        f"power_trace.csv row {index} interval_end_s must equal timestamp_s"
                    )
                support = (interval_start_s, interval_end_s)
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
        support_modes_at.setdefault(timestamp_s, set()).add(support is not None)
        if support is not None:
            existing_support = supports.get(timestamp_s)
            if existing_support is not None and existing_support != support:
                problems.append(
                    "power_trace.csv rail rows have different interval support at "
                    f"timestamp {timestamp_s}"
                )
            else:
                supports[timestamp_s] = support
        elif timestamp_s in supports:
            problems.append(
                "power_trace.csv mixes interval-supported and point rail rows at "
                f"timestamp {timestamp_s}"
            )
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
    if supports and len(supports) != len(totals):
        problems.append(
            "power_trace.csv cannot mix interval-supported and point observations"
        )
    if any(len(modes) != 1 for modes in support_modes_at.values()):
        problems.append(
            "power_trace.csv cannot mix interval-supported and point rail rows"
        )
    if supports:
        ordered = [supports[t] for t in sorted(supports)]
        for previous, current in zip(ordered, ordered[1:]):
            tolerance = 1e-6
            if current[0] < previous[1] - tolerance:
                problems.append(
                    "power_trace.csv interval supports overlap: "
                    f"{previous!r} then {current!r}"
                )
                break
    return _TraceValidation(totals=totals, supports=supports, problems=problems)


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
    request_scoped_phase_markers = any(
        record.get("event_type") in {"phase_start", "phase_end"}
        and isinstance(record.get("metadata"), dict)
        and "request_id" in record["metadata"]
        for record in records
    )
    if not request_scoped_phase_markers:
        problems.extend(_pair_phase_windows(records).problems)
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
    joined_header = ",".join(header)
    if joined_header not in {POWER_TRACE_HEADER, POWER_TRACE_INTERVAL_HEADER}:
        return [
            "power_trace.csv header is "
            f"{joined_header!r}, expected {POWER_TRACE_HEADER!r} or "
            f"{POWER_TRACE_INTERVAL_HEADER!r}"
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
