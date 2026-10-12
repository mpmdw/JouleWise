"""Structural window index and first-claim-usable selection (L9 stage S0)."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import json
import math
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Mapping, Sequence, TYPE_CHECKING

from joulewise.flags.exclusions import first_claim_usable

if TYPE_CHECKING:
    from .archive import AttemptRecord

ROOT = Path(__file__).resolve().parents[2]
INDEX_SCHEMA = "joulewise.b5_window_index.v1"
PACKS = frozenset(("alpha", "beta", "gamma"))
VERDICTS = frozenset(("COLLECTED", "NULL", "HARVEST_FAULT", "NO_COLLECTION"))
PackTable = Mapping[str, Mapping[str, str]]
_SELECTION_TOKEN = object()


class AnalysisRefusal(ValueError):
    """A tooling refusal, with a stable code and no restricted input in its text."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class SealPins:
    pins: Mapping[str, Any]
    sealed: Mapping[str, str]
    erratum_2_epoch_s: int
    erratum_3_epoch_s: int

    @classmethod
    def load(cls, path: Path = ROOT / "configs/analysis/b5/seal_pins.json") -> SealPins:
        value = json.loads(Path(path).read_bytes())
        if value.get("schema") != "joulewise.b5_seal_pins.v1":
            raise AnalysisRefusal("seal_pins_invalid")
        return cls(freeze(value["pins"]), freeze(value["sealed"]),
                   value["erratum_2_epoch_s"], value["erratum_3_epoch_s"])

    def shape(self, head: str) -> str:
        for shape, pin in self.pins.items():
            if pin["head"] == head:
                return shape
        raise AnalysisRefusal("window_index_pin_mismatch")


def governing_pin(t0_epoch_s: float, seal: str, *, seal_pins: SealPins | None = None) -> str:
    pins = seal_pins or SealPins.load()
    if (isinstance(t0_epoch_s, bool) or not isinstance(t0_epoch_s, (int, float))
            or t0_epoch_s <= 0 or (isinstance(t0_epoch_s, float) and not math.isfinite(t0_epoch_s))):
        raise AnalysisRefusal("window_index_invalid")
    if seal not in ("first", "second"):
        raise AnalysisRefusal("window_index_invalid")
    shape = ("pin1" if seal == "first" else "pin2" if t0_epoch_s <= pins.erratum_2_epoch_s
             else "pin3" if t0_epoch_s <= pins.erratum_3_epoch_s else "pin4")
    return pins.pins[shape]["head"]


def sealed_pack_table() -> PackTable:
    """Derive ids as the frozen harvest does: the sealed pack directory's name.

    The sizing record maps the pack labels to their sealed plan trees. No pack
    id is duplicated here. An explicit pack_table argument is a test-only seam
    for synthetic ids and plan prefixes (with optional {attempt} expansion).
    """
    import hashlib
    try:
        sizing = json.loads((ROOT / "configs/campaigns/v5_claim_25g83/sizing_b5.json").read_bytes())
        table = {}
        for pack in PACKS:
            row = sizing["packs"][pack.upper()]["plan_tree"]
            tree = ROOT / row["path"]
            if (tree.parent.parent != ROOT / "configs/campaigns"
                    or hashlib.sha256(tree.read_bytes()).hexdigest() != row["sha256"]):
                raise ValueError()
            table[pack] = {tree.parent.name: f"v5-b5-{pack}-a{{attempt}}-"}
        return freeze(table)
    except (OSError, ValueError, TypeError, KeyError):
        raise AnalysisRefusal("window_index_pack_mismatch") from None


@dataclass(frozen=True)
class IndexEntry:
    pack: str
    pack_id: str
    attempt: int
    plan_id: str
    t0_epoch_s: float
    seal: str
    entry_kind: str
    archive_root: Path | None
    harvest_record_sha256: str | None
    superseded_archive_roots: tuple[Path, ...]
    claim_runs_root: Path
    bound_runs_root: Path
    custody_root: Path
    measurement_root: Path
    harvest_pin: str
    verdict: str
    claim_usable: bool
    cause_key: str | None = None
    g10_requested: bool = False
    g10_redraw_cycles: int | None = None
    record_citation: str | Mapping[str, Any] | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], *, seal_pins: SealPins | None = None,
                     pack_table: PackTable | None = None) -> IndexEntry:
        pins = seal_pins or SealPins.load()
        try:
            if not isinstance(value, Mapping):
                raise ValueError()
            data = dict(value)
            for key in ("archive_root", "claim_runs_root", "bound_runs_root", "custody_root", "measurement_root"):
                if key == "archive_root" and data.get(key) is None:
                    data[key] = None
                else:
                    raw = data[key]
                    if not isinstance(raw, str) or not raw or "\x00" in raw or not Path(raw).is_absolute():
                        raise ValueError()
                    data[key] = Path(raw)
            superseded = data.get("superseded_archive_roots", ())
            if (not isinstance(superseded, (list, tuple)) or any(
                    not isinstance(item, str) or not item or "\x00" in item or not Path(item).is_absolute()
                    for item in superseded)):
                raise ValueError()
            data["superseded_archive_roots"] = tuple(Path(item) for item in superseded)
            entry = cls(**data)
        except (KeyError, TypeError, ValueError):
            raise AnalysisRefusal("window_index_invalid") from None
        validate_entry(entry, seal_pins=pins, pack_table=pack_table)
        return entry


def validate_entry(entry: IndexEntry, *, seal_pins: SealPins, pack_table: PackTable | None = None) -> None:
    if (type(entry.pack) is not str or entry.pack not in PACKS
            or type(entry.pack_id) is not str or not entry.pack_id or type(entry.plan_id) is not str or not entry.plan_id
            or type(entry.attempt) is not int or entry.attempt < 1
            or type(entry.claim_usable) is not bool or type(entry.verdict) is not str or entry.verdict not in VERDICTS
            or type(entry.entry_kind) is not str or entry.entry_kind not in ("harvested", "no_archive")
            or type(entry.seal) is not str or type(entry.harvest_pin) is not str
            or type(entry.g10_requested) is not bool
            or (entry.g10_redraw_cycles is not None and
                (type(entry.g10_redraw_cycles) is not int or entry.g10_redraw_cycles < 0))
            or (entry.cause_key is not None and type(entry.cause_key) is not str)):
        raise AnalysisRefusal("window_index_invalid")
    if entry.record_citation is not None and not isinstance(entry.record_citation, (str, Mapping)):
        raise AnalysisRefusal("window_index_invalid")
    roots = (entry.claim_runs_root, entry.bound_runs_root, entry.custody_root, entry.measurement_root)
    if (not isinstance(entry.superseded_archive_roots, tuple)
            or any(not isinstance(path, Path) or not path.is_absolute() or "\x00" in str(path)
                   for path in roots + entry.superseded_archive_roots)
            or (entry.archive_root is not None and (not isinstance(entry.archive_root, Path)
                or not entry.archive_root.is_absolute() or "\x00" in str(entry.archive_root)))):
        raise AnalysisRefusal("window_index_invalid")
    if entry.harvest_pin != governing_pin(entry.t0_epoch_s, entry.seal, seal_pins=seal_pins):
        raise AnalysisRefusal("window_index_pin_mismatch")
    table = sealed_pack_table() if pack_table is None else pack_table
    prefix = table.get(entry.pack, {}).get(entry.pack_id)
    if not isinstance(prefix, str) or not entry.plan_id.startswith(prefix.format(attempt=entry.attempt)):
        raise AnalysisRefusal("window_index_pack_mismatch")
    if entry.entry_kind == "no_archive":
        if not entry.record_citation:
            raise AnalysisRefusal("window_index_record_citation_required")
        if (entry.archive_root is not None or entry.harvest_record_sha256 is not None or entry.claim_usable
                or entry.verdict == "COLLECTED"):
            raise AnalysisRefusal("window_index_invalid")
    elif entry.archive_root is None or not isinstance(entry.harvest_record_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", entry.harvest_record_sha256):
        raise AnalysisRefusal("window_index_invalid")


@dataclass(frozen=True)
class WindowIndex:
    entries: tuple[IndexEntry, ...]
    sha256: str | None = None


def load_window_index(path: Path, *, seal_pins: SealPins | None = None,
                      pack_table: PackTable | None = None) -> WindowIndex:
    import hashlib
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw)
        if value.get("schema") != INDEX_SCHEMA or not isinstance(value.get("attempts"), list):
            raise ValueError()
        table = sealed_pack_table() if pack_table is None else pack_table
        entries = tuple(IndexEntry.from_mapping(item, seal_pins=seal_pins, pack_table=table) for item in value["attempts"])
    except AnalysisRefusal:
        raise
    except (OSError, ValueError, TypeError, AttributeError):
        raise AnalysisRefusal("window_index_invalid") from None
    _unique(entries)
    _complete_history(entries)
    return WindowIndex(entries, hashlib.sha256(raw).hexdigest())


def _unique(entries: Sequence[IndexEntry]) -> None:
    keys = [(item.pack, item.seal, item.attempt) for item in entries]
    if len(keys) != len(set(keys)):
        raise AnalysisRefusal("window_index_duplicate_attempt")


def _complete_history(entries: Sequence[IndexEntry]) -> None:
    for pack, seal in {(entry.pack, entry.seal) for entry in entries}:
        history = sorted((entry for entry in entries if (entry.pack, entry.seal) == (pack, seal)),
                         key=lambda entry: entry.attempt)
        if ([entry.attempt for entry in history] != list(range(1, len(history) + 1))
                or any(earlier.t0_epoch_s > later.t0_epoch_s for earlier, later in zip(history, history[1:]))):
            raise AnalysisRefusal("window_index_attempts_incomplete")


@dataclass(frozen=True)
class AnalysedWindow:
    pack: str
    pack_id: str
    plan_id: str
    attempt: int
    archive_root: Path
    harvest_record_sha256: str
    claim_runs_root: Path
    bound_runs_root: Path
    custody_root: Path
    measurement_root: Path
    harvest_pin: str
    governed_e2: bool
    governed_e3: bool
    record: AttemptRecord
    _selection_token: object = field(default=None, repr=False, compare=False)

    @classmethod
    def from_record(cls, record: AttemptRecord, *, seal_pins: SealPins | None = None) -> AnalysedWindow:
        entry = record.entry
        pins = seal_pins or SealPins.load()
        if entry.archive_root is None or entry.harvest_record_sha256 is None:
            raise AnalysisRefusal("attempt_not_claim_usable")
        fields = {key: getattr(entry, key) for key in (
            "pack", "pack_id", "plan_id", "attempt", "archive_root", "harvest_record_sha256", "claim_runs_root",
            "bound_runs_root", "custody_root", "measurement_root", "harvest_pin")}
        return cls(**fields, governed_e2=entry.seal == "second" and entry.t0_epoch_s > pins.erratum_2_epoch_s,
                   governed_e3=entry.seal == "second" and entry.t0_epoch_s > pins.erratum_3_epoch_s, record=record)


def select_analysed_attempts(index: WindowIndex | Sequence[IndexEntry], records: Sequence[AttemptRecord],
                             *, seal_pins: SealPins | None = None) -> dict[str, AnalysedWindow]:
    entries = index.entries if isinstance(index, WindowIndex) else tuple(index)
    _unique(entries)
    _complete_history(entries)
    if len(records) != len(entries) or any(record.entry != entry for entry, record in zip(entries, records)):
        raise AnalysisRefusal("window_index_disagrees_with_archive")
    result = {}
    for pack in sorted(PACKS):
        history = sorted((record for record in records if record.entry.pack == pack and record.entry.seal == "second"),
                         key=lambda record: record.entry.attempt)
        if not history or not any(record.claim_usable for record in history):
            raise AnalysisRefusal("block_incomplete")
        candidates = []
        for record in history:
            row = {"attempt": record.entry.attempt, "claim_usable": record.claim_usable}
            if record.release_blocked is not None:
                row["release_blocked"] = record.release_blocked
            candidates.append(row)
        selected = first_claim_usable(candidates)
        if selected is None:
            raise AnalysisRefusal("analysed_attempt_undecided")
        record = next(record for record in history if record.entry.attempt == selected)
        result[pack] = replace(AnalysedWindow.from_record(record, seal_pins=seal_pins),
                               _selection_token=(_SELECTION_TOKEN, record.entry))
    return result


def open_attempt_record(entry: IndexEntry, *, seal_pins: SealPins, pack_table: PackTable | None = None) -> AttemptRecord:
    """Public reader seam; implementation lives with the archive I/O."""
    from .archive import open_attempt_record as read
    return read(entry, seal_pins=seal_pins, pack_table=pack_table)
