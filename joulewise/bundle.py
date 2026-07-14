"""Run-bundle writer: layout, run-ID scheme, and write-order invariants.

Implements the bundle contract in ``docs/contracts/run_bundle_layout.md``:

- D-001: the bundle stores the normalized config as sorted-key
  ``config.json``; its SHA-256 (over the exact bytes written) is recorded in
  ``metadata.json`` and exposed as ``RunBundleWriter.config_sha256``.
- D-005: experiment manifests live at ``runs/experiments/<id>.json`` and are
  extended incrementally, so manifest overwrite is explicitly allowed.
- D-010: run IDs are ``<UTC ts>__<target>__<workload>__<4 hex>`` sanitized to
  ``[a-z0-9_-]``; a config-supplied ``run_id`` is used verbatim after
  sanitization; an existing bundle directory is a hard error (bundles are
  immutable evidence, never overwritten).
- D-011: ``summary_metrics.json`` is the completion marker, written last by
  ``finalize()`` after the ``run_finalized`` event; metadata must be written
  before a summary can be staged.
- D-018: ``power_trace.csv`` carries one row per rail per sample with the
  header ``timestamp_s,power_w,source,rail`` (row fan-out per rail is the
  caller's responsibility).

All timestamps come from the injected :class:`joulewise.clock.Clock`
(D-003/D-019); this module never reads the wall clock directly.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import tempfile
import time
from enum import Enum
from pathlib import Path
from typing import Any

import joulewise
from joulewise.clock import Clock
from joulewise.interfaces import PowerSample, RunContext, RuntimeEvent
from joulewise.schemas import BenchmarkConfig, SummaryMetrics

_ID_ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789_-")
_POWER_TRACE_HEADER = ["timestamp_s", "power_w", "source", "rail"]
_RESERVED_TOP_LEVEL_ARTIFACTS = {
    "config.json",
    "metadata.json",
    "events.jsonl",
    "power_trace.csv",
    "summary_metrics.json",
}
_METADATA_QUARANTINE_KEY = "serialization_quarantine"


class BundleError(Exception):
    """Raised when a bundle invariant (layout, ordering, immutability) breaks."""


def _json_pointer_child(path: str, key: str) -> str:
    """Append one string key to an RFC 6901 JSON pointer."""
    escaped = key.replace("~", "~0").replace("/", "~1")
    return f"{path}/{escaped}"


def _stable_type_name(value: Any) -> str:
    """Return type provenance without consulting ``value``'s str/repr hooks."""
    value_type = type(value)
    try:
        module = type.__getattribute__(value_type, "__module__")
        qualname = type.__getattribute__(value_type, "__qualname__")
    except (AttributeError, TypeError):
        return "unknown"
    if not isinstance(module, str) or not isinstance(qualname, str):
        return "unknown"
    return f"{module}.{qualname}"


def _quarantine_json_value(
    value: Any,
    path: str,
    active_containers: set[int],
    diagnostics: list[dict[str, Any]],
) -> Any:
    """Return deterministic JSON data, quarantining malformed metadata leaves.

    Unsupported values and cycles become ``null`` at their original JSON
    pointer. Non-string-keyed entries are omitted while valid siblings remain.
    Every replacement or omission is described in the top-level
    ``serialization_quarantine`` list; no value's ``str`` or ``repr`` is ever
    captured in either the sanitized metadata or its diagnostics.
    """
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        diagnostics.append(
            {
                "path": path,
                "reason": "non_finite_number",
                "value_type": _stable_type_name(value),
            }
        )
        return None
    if isinstance(value, Enum):
        return _quarantine_json_value(
            value.value, path, active_containers, diagnostics
        )
    if isinstance(value, (dict, list, tuple)):
        container_id = id(value)
        if container_id in active_containers:
            diagnostics.append(
                {
                    "path": path,
                    "reason": "cycle",
                    "value_type": _stable_type_name(value),
                }
            )
            return None
        active_containers.add(container_id)
        try:
            if isinstance(value, dict):
                result: dict[str, Any] = {}
                valid_keys: list[str] = []
                invalid_key_types: dict[str, int] = {}
                for key in dict.keys(value):
                    if isinstance(key, str):
                        valid_keys.append(key)
                    else:
                        key_type = _stable_type_name(key)
                        invalid_key_types[key_type] = (
                            invalid_key_types.get(key_type, 0) + 1
                        )
                for key_type in sorted(invalid_key_types):
                    diagnostics.append(
                        {
                            "count": invalid_key_types[key_type],
                            "key_type": key_type,
                            "path": path,
                            "reason": "non_string_key",
                        }
                    )
                for key in sorted(valid_keys):
                    result[key] = _quarantine_json_value(
                        dict.__getitem__(value, key),
                        _json_pointer_child(path, key),
                        active_containers,
                        diagnostics,
                    )
                return result
            result_list: list[Any] = []
            for index, inner in enumerate(value):
                result_list.append(
                    _quarantine_json_value(
                        inner,
                        f"{path}/{index}",
                        active_containers,
                        diagnostics,
                    )
                )
            return result_list
        finally:
            active_containers.remove(container_id)
    diagnostics.append(
        {
            "path": path,
            "reason": "unsupported_type",
            "value_type": _stable_type_name(value),
        }
    )
    return None


def _quarantine_metadata(
    value: dict[Any, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Sanitize one metadata object and return path-sorted diagnostics."""
    diagnostics: list[dict[str, Any]] = []
    sanitized = _quarantine_json_value(value, "", set(), diagnostics)
    assert isinstance(sanitized, dict)
    diagnostics.sort(
        key=lambda item: (
            item["path"],
            item["reason"],
            item.get("key_type", ""),
            item.get("value_type", ""),
        )
    )
    return sanitized, diagnostics


def sanitize_id_component(s: str) -> str:
    """Lowercase ``s`` and map every char outside ``[a-z0-9_-]`` to ``-``.

    Raises :class:`BundleError` when the result is empty (D-010 components
    must be non-empty).
    """
    sanitized = "".join(ch if ch in _ID_ALLOWED else "-" for ch in s.lower())
    if not sanitized:
        raise BundleError("run-ID component is empty after sanitization")
    return sanitized


def generate_run_id(config: BenchmarkConfig, clock: Clock) -> str:
    """Return the bundle directory name for ``config`` per D-010.

    A config-supplied ``run_id`` is used verbatim after sanitization (no
    timestamp or random suffix). Otherwise the generated form is
    ``<UTC ts>__<target_id>__<workload_name>__<4 hex>``.
    """
    if config.run_id is not None:
        return sanitize_id_component(config.run_id)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(clock.now()))
    target = sanitize_id_component(config.hardware_target.id)
    workload = sanitize_id_component(config.workload_profile.name)
    # D-022: the 4-hex suffix is derived from the config content hash, not a
    # random token, so identical config+clock yields a byte-identical run_id
    # (and thus byte-identical run_started events and metadata.run_id). The
    # canonical config bytes match create()'s D-001 hash input exactly.
    config_bytes = (
        json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    suffix = hashlib.sha256(config_bytes).hexdigest()[:4]
    return f"{ts}__{target}__{workload}__{suffix}"


def write_experiment_manifest(runs_root: Path, manifest: dict) -> Path:
    """Write ``runs_root/experiments/<experiment_id>.json`` (D-005).

    The manifest must contain an ``experiment_id`` key; the ID is sanitized
    for the filename only. Unlike bundles, manifests are extended
    incrementally, so overwriting an existing manifest file is allowed.

    The replacement is atomic (P2-040 FIX-6/ARC-5): the serialized bytes are
    written to a unique temporary file in the same ``experiments/`` directory,
    fsynced, and moved over the destination with ``os.replace``. A failure
    before the replace leaves any existing destination untouched; the
    temporary file is unlinked best-effort and the original error propagates.
    """
    experiment_id = manifest.get("experiment_id")
    if not isinstance(experiment_id, str) or not experiment_id:
        raise BundleError("experiment manifest requires a non-empty 'experiment_id' key")
    experiments_dir = Path(runs_root) / "experiments"
    experiments_dir.mkdir(parents=True, exist_ok=True)
    path = experiments_dir / f"{sanitize_id_component(experiment_id)}.json"
    payload = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(experiments_dir)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    # Best-effort directory fsync so the rename itself is durable; platforms
    # that refuse O_RDONLY directory fds (e.g. Windows) simply skip it.
    try:
        dir_fd = os.open(str(experiments_dir), os.O_RDONLY)
    except OSError:
        pass
    else:
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
        finally:
            os.close(dir_fd)
    return path


def _validated_raw_path(raw_dir: Path, name: str) -> Path:
    """Validate ``name`` as a plain file name and return ``raw_dir/name``.

    Path separators and ``..`` are rejected so a raw artifact can never
    escape the bundle (D-002). Ensures ``raw_dir`` exists; writes nothing.
    """
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        raise BundleError(f"raw artifact name must be a plain file name: {name!r}")
    raw_dir.mkdir(exist_ok=True)
    return raw_dir / name


def _write_raw_file(raw_dir: Path, name: str, data: bytes | str) -> Path:
    """Write ``raw_dir/name`` verbatim; an existing file is an error."""
    path = _validated_raw_path(raw_dir, name)
    if path.exists():
        raise BundleError(
            f"raw artifact already exists: {path} (raw evidence is immutable)"
        )
    handle = tempfile.NamedTemporaryFile(
        dir=raw_dir,
        prefix=f".{name}.",
        suffix=".tmp",
        delete=False,
    )
    tmp_path = Path(handle.name)
    handle.close()
    try:
        if isinstance(data, bytes):
            tmp_path.write_bytes(data)
        else:
            tmp_path.write_text(data)
        tmp_path.replace(path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
    return path


def write_raw_artifact(context: RunContext, name: str, data: bytes | str) -> Path:
    """Adapter-side raw-evidence write: ``context.raw_dir/name``, verbatim.

    The one sanctioned way for an adapter to preserve its native sampler
    output under ``raw/`` (D-002 via the D-024 context seam; 2026-07-06
    status review P3): the name must be a plain file name and an existing
    file is a :class:`BundleError` - the same validation and no-overwrite
    rule as :meth:`RunBundleWriter.write_raw`, without handing the adapter
    the writer's bundle-lifecycle authority. Raw writes after ``finalize()``
    are not reachable through the controller (adapters are only invoked
    while the run is open), so no open-check is needed here.
    """
    return _write_raw_file(context.raw_dir, name, data)


def write_derived_artifact(context: RunContext, name: str, data: bytes | str) -> Path:
    """Adapter-side write for additive top-level derived artifacts.

    This mirrors :func:`write_raw_artifact` for artifacts derived from native
    evidence but not themselves raw evidence. The name must be a plain file
    name, core bundle artifacts are reserved, and overwriting is an error.
    Adapters still receive only :class:`RunContext` paths, not writer authority
    (D-024).
    """
    if name in _RESERVED_TOP_LEVEL_ARTIFACTS:
        raise BundleError(f"derived artifact name is reserved: {name!r}")
    path = _validated_raw_path(context.bundle_path, name)
    if path.exists():
        raise BundleError(
            f"derived artifact already exists: {path} (bundle evidence is immutable)"
        )
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data)
    return path


def _git_commit() -> str:
    """Return the harness git commit, or ``"unknown"`` outside a checkout."""
    package_dir = Path(__file__).resolve().parent
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=package_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    commit = result.stdout.strip()
    return commit if commit else "unknown"


class RunBundleWriter:
    """Writes one run bundle, enforcing immutability and write order.

    Construct via :meth:`create`; the writer immediately persists
    ``config.json`` and an empty ``events.jsonl`` so even an early crash
    leaves an inspectable (incomplete) bundle per D-011.
    """

    def __init__(
        self,
        path: Path,
        run_id: str,
        config: BenchmarkConfig,
        config_sha256: str,
        clock: Clock,
    ) -> None:
        self._path = path
        self._run_id = run_id
        self._config = config
        self._config_sha256 = config_sha256
        self._clock = clock
        self._metadata_written = False
        self._power_trace_written = False
        self._suite_manifest_written = False
        self._staged_summary: dict[str, Any] | None = None
        self._closed = False

    @classmethod
    def create(cls, runs_root: Path, config: BenchmarkConfig, clock: Clock) -> "RunBundleWriter":
        """Create ``runs_root/<run_id>/`` and seed the mandatory artifacts.

        Raises :class:`BundleError` if the bundle directory already exists
        (bundles are immutable evidence; never overwrite, D-010).
        """
        run_id = generate_run_id(config, clock)
        path = Path(runs_root) / run_id
        if path.exists():
            raise BundleError(
                f"bundle directory already exists: {path} (bundles are immutable evidence)"
            )
        path.mkdir(parents=True)
        for subdir in ("raw", "logs", "outputs"):
            (path / subdir).mkdir()
        config_bytes = (
            json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        (path / "config.json").write_bytes(config_bytes)
        config_sha256 = hashlib.sha256(config_bytes).hexdigest()
        (path / "events.jsonl").write_text("")
        return cls(
            path=path,
            run_id=run_id,
            config=config,
            config_sha256=config_sha256,
            clock=clock,
        )

    @property
    def path(self) -> Path:
        return self._path

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def config_sha256(self) -> str:
        return self._config_sha256

    def _require_open(self, operation: str) -> None:
        if self._closed:
            raise BundleError(f"cannot {operation}: bundle is finalized")

    def append_event(self, event: RuntimeEvent) -> None:
        """Append one event line with exactly the contract's five keys."""
        self._require_open("append event")
        self._append_event_record(event)

    def _append_event_record(self, event: RuntimeEvent) -> None:
        record = {
            "timestamp_s": event.timestamp_s,
            "event_type": event.event_type,
            "phase": event.phase,
            "message": event.message,
            "metadata": event.metadata,
        }
        with (self._path / "events.jsonl").open("a") as handle:
            handle.write(json.dumps(record) + "\n")

    def write_power_trace(self, samples: list[PowerSample]) -> None:
        """Write ``power_trace.csv`` (D-018). A second call is an error."""
        self._require_open("write power trace")
        if self._power_trace_written:
            raise BundleError("power_trace.csv already written")
        with (self._path / "power_trace.csv").open("w", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(_POWER_TRACE_HEADER)
            for sample in samples:
                writer.writerow(
                    [
                        sample.timestamp_s,
                        sample.power_w,
                        sample.source,
                        sample.rail if sample.rail is not None else "",
                    ]
                )
        self._power_trace_written = True

    def write_metadata(self, extra: dict) -> None:
        """Write ``metadata.json`` from base fields merged with ``extra``.

        A key collision between ``extra`` and the base fields is an error,
        as is a second call. Malformed values are recursively replaced with
        ``null`` and described by RFC 6901 path in the additive top-level
        ``serialization_quarantine`` list. Invalid mapping keys are omitted;
        valid siblings are retained. The diagnostic list is absent when all
        metadata is JSON-safe, preserving valid metadata bytes unchanged.
        """
        self._require_open("write metadata")
        if self._metadata_written:
            raise BundleError("metadata.json already written")
        base: dict[str, Any] = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "joulewise_version": joulewise.__version__,
            "schema_version": self._config.schema_version,
            "config_sha256": self._config_sha256,
            "run_id": self._run_id,
            "git_commit": _git_commit(),
            "clock": self._clock.info(),
        }
        collisions = sorted(set(extra) & (set(base) | {_METADATA_QUARANTINE_KEY}))
        if collisions:
            raise BundleError(
                f"metadata extra keys collide with base fields: {', '.join(collisions)}"
            )
        merged = {**base, **extra}
        sanitized, diagnostics = _quarantine_metadata(merged)
        if diagnostics:
            sanitized[_METADATA_QUARANTINE_KEY] = diagnostics
        (self._path / "metadata.json").write_text(
            json.dumps(sanitized, indent=2, sort_keys=True) + "\n"
        )
        self._metadata_written = True

    def write_suite_manifest(self, mapping: dict[str, Any]) -> Path:
        """Write the canonical effective suite manifest artifact.

        The controller supplies the already materialized mapping. The writer
        owns only bundle-layout invariants: sorted-key D-001 JSON, open-bundle
        ordering, and one immutable ``suite_manifest.json`` per bundle.
        """
        self._require_open("write suite manifest")
        if self._suite_manifest_written:
            raise BundleError("suite_manifest.json already written")
        path = self._path / "suite_manifest.json"
        if path.exists():
            raise BundleError("suite_manifest.json already exists")
        path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n")
        self._suite_manifest_written = True
        return path

    def write_output(self, name: str, text: str) -> Path:
        """Write ``outputs/<name>`` and return its path."""
        self._require_open(f"write output {name!r}")
        path = _validated_raw_path(self._path / "outputs", name)
        path.write_text(text)
        return path

    def raw_path(self, name: str) -> Path:
        """Return ``raw/<name>`` (ensuring ``raw/`` exists); writes nothing.

        ``name`` must be a plain file name: path separators and ``..`` are
        rejected so a raw artifact can never escape the bundle (D-002).
        """
        return _validated_raw_path(self._path / "raw", name)

    def write_raw(self, name: str, data: bytes | str) -> Path:
        """Write ``raw/<name>`` verbatim and return its path (D-002).

        Raw artifacts are immutable evidence: writing over an existing raw
        file - or writing after ``finalize()`` - is an error. Adapters do not
        get this method (D-024: context is data, not capability); they use
        the module-level :func:`write_raw_artifact` against their
        ``RunContext``, and this is the controller-side counterpart for raw
        evidence the controller itself collects.
        """
        self._require_open(f"write raw {name!r}")
        return _write_raw_file(self._path / "raw", name, data)

    def log_path(self, name: str) -> Path:
        """Return ``logs/<name>`` (ensuring ``logs/`` exists); writes nothing."""
        return _validated_raw_path(self._path / "logs", name)

    def write_summary(self, summary: SummaryMetrics) -> None:
        """Stage the summary for :meth:`finalize` (write-order invariant D-011).

        ``metadata.json`` must already be written; the summary itself is
        validated here (via ``to_dict``) but persisted only by ``finalize``,
        keeping ``summary_metrics.json`` the very last artifact.
        """
        self._require_open("write summary")
        if not self._metadata_written:
            raise BundleError("metadata.json must be written before the summary (D-011 ordering)")
        self._staged_summary = summary.to_dict()

    def finalize(self) -> Path:
        """Append ``run_finalized``, write the summary last, close the writer."""
        self._require_open("finalize")
        if self._staged_summary is None:
            raise BundleError("cannot finalize: no summary staged (call write_summary first)")
        self._append_event_record(
            RuntimeEvent(
                timestamp_s=self._clock.now(),
                event_type="run_finalized",
                phase="run",
                message="bundle finalized",
            )
        )
        (self._path / "summary_metrics.json").write_text(
            json.dumps(self._staged_summary, indent=2, sort_keys=True) + "\n"
        )
        self._closed = True
        return self._path
