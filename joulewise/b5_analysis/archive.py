"""Authenticated archive access and bounded, structural attempt histories."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping

from .windows import (AnalysisRefusal, AnalysedWindow, IndexEntry, SealPins, VERDICTS,
                      freeze, validate_entry)

BASE_KEYS = frozenset(("schema", "verdict", "plan_id", "pack_id", "attempt", "archive_root", "claim_usable",
                       "flags", "members_assessed", "faults", "yield", "exclude_window_reasons",
                       "runs_root_overrides", "harvest_checkout", "outputs"))


@dataclass(frozen=True, order=True)
class CensusRow:
    path: str
    sha256: str
    check: str


def _read(root: Path, relative: str, expected: str | None, code: str, check: str,
          census: dict[str, CensusRow]) -> bytes:
    # A digest never authorizes traversal or a symlink out of the archive.
    path = PurePosixPath(relative)
    if not relative or path.is_absolute() or ".." in path.parts or str(path) != relative or "\\" in relative:
        raise AnalysisRefusal("archive_path_invalid")
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()):
        raise AnalysisRefusal("archive_path_invalid")
    try:
        raw = target.read_bytes()
    except OSError:
        raise AnalysisRefusal(code) from None
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None and digest != expected:
        raise AnalysisRefusal(code)
    row = CensusRow(relative, digest, check)
    if relative in census and census[relative] != row:
        raise AnalysisRefusal("archive_input_changed")
    census[relative] = row
    return raw


def _json(raw: bytes, code: str) -> dict:
    try:
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, UnicodeError):
        raise AnalysisRefusal(code) from None


def _output(record: Mapping[str, Any], root: Path, relative: str, census: dict[str, CensusRow]) -> bytes:
    code = ("roster_record_unauthenticated" if relative == "derived/roster.json" else
            "exclusions_record_unauthenticated" if relative == "derived/exclusions.json" else
            "window_flags_record_unauthenticated" if relative == "derived/window_flags.json" else
            "archive_output_unauthenticated")
    digest = record.get("outputs", {}).get(relative)
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise AnalysisRefusal(code)
    return _read(root, relative, digest, code, "harvest_outputs", census)


@dataclass(frozen=True)
class AttemptRecord:
    entry: IndexEntry
    kind: str
    record_shape: str | None
    verdict: str
    claim_usable: bool
    release_blocked: bool | None
    exclusions_form: str
    window_reasons: tuple[str, ...]
    flag_total: int
    flags_by_family: Mapping[str, int]
    g10_codes: Mapping[str, int]
    yield_counts: Mapping[str, Any] | None
    calibration_bracket: Mapping[str, Any] | None
    reference_source: str | None
    checkout_flags: tuple[str, ...]
    census: tuple[CensusRow, ...]
    catalog_sha256: str | None = None


def open_attempt_record(entry: IndexEntry, *, seal_pins: SealPins) -> AttemptRecord:
    validate_entry(entry, seal_pins=seal_pins)
    if entry.entry_kind == "no_archive":
        return AttemptRecord(entry, "no_archive", None, entry.verdict, False, None, "none", (), 0,
                             freeze({}), freeze({}), None, None, None, (), ())
    root = entry.archive_root
    census: dict[str, CensusRow] = {}
    # Check 1: the index, not the archive, authenticates harvest.json.
    record = _json(_read(root, "harvest.json", entry.harvest_record_sha256,
                         "harvest_record_not_the_indexed_one", "window_index", census),
                   "harvest_record_shape_mismatch")
    # Check 2: shape comes from the governing pin, never from observed keys.
    shape = seal_pins.shape(entry.harvest_pin)
    keys = BASE_KEYS | ({"calibration_bracket"} if shape == "pin4" else set())
    if (record.keys() != keys or record.get("schema") != "joulewise.harvest_b5_window.v1"
            or any(record.get(key) != getattr(entry, key) for key in ("pack_id", "plan_id", "attempt"))
            or type(record.get("verdict")) is not str or record.get("verdict") not in VERDICTS or type(record.get("attempt")) is not int
            or not isinstance(record.get("outputs"), dict)):
        raise AnalysisRefusal("harvest_record_shape_mismatch")
    if record["verdict"] != entry.verdict:
        raise AnalysisRefusal("window_index_disagrees_with_archive")
    # Check 3: the recorded program head AND each pinned program byte digest.
    checkout = record.get("harvest_checkout")
    pin = seal_pins.pins[shape]
    if (not isinstance(checkout, dict) or checkout.get("head") != pin["head"]
            or checkout.get("files") != dict(pin["files"])):
        raise AnalysisRefusal("harvest_commit_not_the_pinned_one")
    checkout_flags = ("harvest_checkout_status_not_clean",) if (
        checkout.get("status_clean") is not True or checkout.get("status_lines") != 0
        or checkout.get("errors") != []) else ()
    # Check 4: full document or one of the two actual writer stubs.
    exclusions = _json(_output(record, root, "derived/exclusions.json", census),
                       "exclusions_record_shape_mismatch")
    if exclusions.get("schema_version") == "joulewise.exclusions.v1":
        form = "document"
    elif exclusions.get("schema") == "joulewise.exclusions.v1":
        form = "document"
    elif exclusions.get("status") in ("NULL", "UNAVAILABLE") and "schema" not in exclusions and "schema_version" not in exclusions:
        form = "stub_null" if exclusions["status"] == "NULL" else "stub_unavailable"
        required_reason = "window.null" if form == "stub_null" else "exclusions.function_unavailable"
        if exclusions.get("reasons") != [required_reason] or any(
                key in exclusions for key in ("catalog_sha256", "release_blocked")):
            raise AnalysisRefusal("exclusions_record_shape_mismatch")
    else:
        raise AnalysisRefusal("exclusions_record_shape_mismatch")
    if exclusions.get("harvest_checkout") != checkout:
        raise AnalysisRefusal("exclusions_harvest_checkout_differs")
    catalog = exclusions.get("catalog_sha256")
    if form == "document" and entry.seal == "second" and catalog != seal_pins.sealed["catalog_sha256"]:
        raise AnalysisRefusal("exclusions_catalog_mismatch")
    # Check 5: bools must be actual bools; stubs are never claim-usable.
    usable = record.get("claim_usable")
    doc_usable = exclusions.get("claim_usable")
    release = exclusions.get("release_blocked")
    if (type(usable) is not bool or type(doc_usable) is not bool
            or ("release_blocked" in exclusions and type(release) is not bool)
            or usable != (doc_usable and record["verdict"] == "COLLECTED")
            or (form != "document" and doc_usable)):
        raise AnalysisRefusal("attempt_record_inconsistent")
    if entry.claim_usable != usable:
        raise AnalysisRefusal("window_index_disagrees_with_archive")
    # Check 6: the structural flags record is independently authenticated.
    flags = _json(_output(record, root, "derived/window_flags.json", census), "window_flags_record_inconsistent")
    if (flags.get("schema") != "joulewise.window_flags.v1"
            or flags.get("exclusions", {}).get("claim_usable") is not usable):
        raise AnalysisRefusal("window_flags_record_inconsistent")
    counts = flags.get("flags", {})
    if (type(counts.get("total")) is not int or counts["total"] < 0
            or any(not isinstance(counts.get(key), dict) for key in ("by_family", "by_code"))
            or any(type(code) is not str or type(n) is not int or n < 0
                   for key in ("by_family", "by_code") for code, n in counts[key].items())):
        raise AnalysisRefusal("window_flags_record_inconsistent")
    source = None
    if shape in ("pin3", "pin4") and "derived/neg8-screen.json" in record["outputs"]:
        screen = _json(_output(record, root, "derived/neg8-screen.json", census), "archive_output_unauthenticated")
        source = (screen.get("rescreen") or {}).get("reference_source", {}).get("source")
    return AttemptRecord(entry, "harvested", shape, record["verdict"], usable, release, form,
                         tuple(record["exclude_window_reasons"]), counts["total"], freeze(counts["by_family"]),
                         freeze({code: n for code, n in counts["by_code"].items() if code.startswith("g10.")}),
                         freeze(record["yield"]), freeze(record.get("calibration_bracket")), source, checkout_flags,
                         tuple(sorted(census.values())), catalog)


class ArchiveHandle:
    def __init__(self, window: AnalysedWindow, record: Mapping[str, Any], census: dict[str, CensusRow]):
        self.window = window
        self.record = freeze(record)
        self.shape = window.record.record_shape
        self._census = census
        self._source_manifest: dict[str, str] | None = None

    def census(self) -> tuple[CensusRow, ...]:
        return tuple(sorted(self._census.values()))

    def output_bytes(self, relative: str) -> bytes:
        return _output(self.record, self.window.archive_root, relative, self._census)

    def _sources(self) -> dict[str, str]:
        # Re-read on every call: a changed manifest cannot silently use a cached list.
        raw = _read(self.window.archive_root, "sources/SHA256SUMS", None, "archive_source_unauthenticated",
                    "input_census", self._census)
        if self._source_manifest is None:
            manifest = {}
            try:
                for line in raw.decode("utf-8").splitlines():
                    match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
                    if match is None or match[2] in manifest:
                        raise ValueError()
                    name = match[2]
                    if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts or "\\" in name:
                        raise ValueError()
                    manifest[name] = match[1]
            except (ValueError, UnicodeError):
                raise AnalysisRefusal("archive_source_manifest_invalid") from None
            self._source_manifest = manifest
        return self._source_manifest

    def source_bytes(self, relative: str) -> bytes:
        if not relative.startswith("sources/") or relative == "sources/SHA256SUMS":
            raise AnalysisRefusal("archive_path_invalid")
        name = relative.removeprefix("sources/")
        digest = self._sources().get(name)
        if digest is None:
            raise AnalysisRefusal("archive_source_unauthenticated")
        return _read(self.window.archive_root, relative, digest, "archive_source_unauthenticated",
                     "sources_sha256sums", self._census)

    def withheld_bytes(self, relative: str) -> bytes:
        if not relative.startswith("withheld/"):
            raise AnalysisRefusal("archive_path_invalid")
        if relative in self.record["outputs"]:
            return self.output_bytes(relative)
        return _read(self.window.archive_root, relative, None, "archive_withheld_unreadable", "input_census",
                     self._census)

    def compare_runs_root(self) -> tuple[Mapping[str, Any], ...]:
        """Step-0 seam: compare original claim bytes with the harvested inventory."""
        root = self.window.claim_runs_root
        prefix = "claim-runs/"
        if root.is_relative_to(self.window.custody_root):
            prefix = "night-custody/" + root.relative_to(self.window.custody_root).as_posix() + "/"
        manifest = {name.removeprefix(prefix): digest for name, digest in self._sources().items()
                    if name.startswith(prefix)}
        if not manifest:
            raise AnalysisRefusal("runs_root_differs_from_archive")
        for name, digest in manifest.items():
            try:
                path = root / name
                if not path.resolve().is_relative_to(root.resolve()):
                    raise OSError()
                raw = path.read_bytes()
            except OSError:
                raise AnalysisRefusal("runs_root_differs_from_archive") from None
            if hashlib.sha256(raw).hexdigest() != digest:
                raise AnalysisRefusal("runs_root_differs_from_archive")
            key = "original/claim-runs/" + name
            row = CensusRow(key, digest, "sources_sha256sums")
            if key in self._census and self._census[key] != row:
                raise AnalysisRefusal("archive_input_changed")
            self._census[key] = row
        extra = sum(path.relative_to(root).as_posix() not in manifest for path in root.rglob("*") if path.is_file())
        return (freeze({"code": "runs_root_has_unlisted_file", "count": extra}),) if extra else ()


def open_archive(window: AnalysedWindow, *, seal_pins: SealPins) -> ArchiveHandle:
    if window.record.verdict != "COLLECTED" or window.record.claim_usable is not True:
        raise AnalysisRefusal("attempt_not_claim_usable")
    shape = seal_pins.shape(window.harvest_pin)
    if shape not in ("pin2", "pin4"):
        raise AnalysisRefusal("analysed_window_shape_unsupported")
    # Reauthenticate after selection, including the indexed harvest bytes.
    record = open_attempt_record(window.record.entry, seal_pins=seal_pins)
    if record != window.record or AnalysedWindow.from_record(record, seal_pins=seal_pins) != window:
        raise AnalysisRefusal("window_index_disagrees_with_archive")
    census = {row.path: row for row in record.census}
    parsed = _json(_read(window.archive_root, "harvest.json", window.harvest_record_sha256,
                         "harvest_record_not_the_indexed_one", "window_index", census), "harvest_record_shape_mismatch")
    # RULING.md Z1 supersedes design T6 for analysed windows. A pinned file
    # digest cannot establish the bytes of every imported module in a dirty
    # checkout. History-only attempts retain the structural flag above.
    checkout = parsed["harvest_checkout"]
    if (checkout.get("status_clean") is not True or checkout.get("status_lines") != 0
            or checkout.get("errors") != []):
        raise AnalysisRefusal("harvest_checkout_not_clean")
    return ArchiveHandle(window, parsed, census)
