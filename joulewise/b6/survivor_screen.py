"""NEG-8 on survivors. Energy evidence stays in withheld/b6-neg8.json."""

from __future__ import annotations

import json
import math
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from joulewise.desk_compress import is_file as desk_is_file, read_bytes
from joulewise.whole_window import neg8_count_adjusted_bound
from joulewise.desk_restore import RestoreRefused

FAMILIES = ("gross", "idle_subtracted")
SLOTS = {"start_reference": "start", "midpoint_reference": "midpoint", "end_reference": "end"}


@dataclass(frozen=True)
class ScreenResult:
    verdict: str
    counts: Mapping[str, int]
    corpus_clean_n: int
    reason: str | None = None
    flags: tuple[str, ...] = ()
    withheld: Mapping[str, Any] = field(default_factory=dict, repr=False)

    def acceptance_evidence(self) -> dict:
        return {"verdict": self.verdict, "survivors": dict(self.counts),
                "corpus_clean_n": self.corpus_clean_n, "reason": self.reason,
                "flags": list(self.flags)}


def screen(roster: Mapping, member_effects: Mapping,
           energy_of: Callable[[Mapping], Mapping] | None, reg: Mapping, *, counts_only=False) -> ScreenResult:
    """Select in committed roster order; use the one registered bound function.

    energy_of returns {gross, idle_subtracted, source?}, produced by the
    existing reference-energy reader in archive mode, synthetic at the desk.
    """
    settings = reg.get("neg8", reg)
    excluded = member_effects.get("members_excluded", member_effects)
    if isinstance(excluded, list):
        excluded = {row["run_id"]: row["codes"] for row in excluded}
    members = roster.get("members", [])
    corpus = [member for member in members
              if member.get("role", member.get("stage_id")) in ("corpus", "neg8_bound")
              or member.get("stage_id") == "neg8_bound"]
    slots = {slot: [] for slot in SLOTS.values()}
    lost = set()
    flags = set()

    def clean(member: Mapping) -> bool:
        return member.get("status") == "succeeded" and not excluded.get(member["run_id"])

    kept_corpus = [member for member in corpus if clean(member)][:settings["corpus_cap"]]
    for member in members:
        slot = SLOTS.get(member.get("stage_id"))
        if slot is None and member.get("role") in slots:
            slot = member["role"]
        if slot is None:
            continue
        if clean(member):
            slots[slot].append(member)
        else:
            lost.add(slot)
    if lost & {"start", "end"}:
        flags.add("neg8.reference_lost")
    if "midpoint" in lost:
        flags.add("neg8.midpoint_lost")
    counts = {slot: len(rows) for slot, rows in slots.items()}
    record: dict[str, Any] = {"schema": "joulewise.b6_neg8.v1", "survivors": counts,
                              "corpus_clean_n": len(kept_corpus),
                              "energy_reader": getattr(energy_of, "reader_name", "synthetic"),
                              "energy_reader_used": False,
                              "corpus_run_ids": [m["run_id"] for m in kept_corpus],
                              "reference_run_ids": {slot: [m["run_id"] for m in rows]
                                                    for slot, rows in slots.items()}, "families": {}}

    def finish(verdict: str, reason: str | None = None) -> ScreenResult:
        record.update(verdict=verdict, reason=reason)
        if verdict != "pending":
            flags.add("neg8.survivor_screen_" + verdict)
        record["flags"] = sorted(flags)
        return ScreenResult(verdict, counts, len(kept_corpus), reason, tuple(sorted(flags)), record)

    if counts_only:
        if len(kept_corpus) < settings["corpus_minimum"] or counts["start"] < 2 or counts["end"] < 2:
            return finish("undefined", "references_insufficient")
        return finish("pending")

    energies = {}
    unreadable = []

    def read_energy(member: Mapping, role: str) -> bool:
        record["energy_reader_used"] = True
        try:
            value = energy_of(member)
            if not all(math.isfinite(value[family]) for family in FAMILIES):
                raise ValueError("nonfinite reference energy")
        except RestoreRefused:
            raise
        except (OSError, ValueError, KeyError, TypeError, ArithmeticError):
            unreadable.append(member["run_id"])
            flags.add(f"neg8.{role}_energy_unreadable")
            return False
        energies[member["run_id"]] = value
        return True

    kept_corpus = []
    for member in corpus:
        if clean(member) and read_energy(member, "corpus"):
            kept_corpus.append(member)
            if len(kept_corpus) == settings["corpus_cap"]:
                break
    for slot, rows in slots.items():
        readable = [member for member in rows if read_energy(member, "reference")]
        if len(readable) != len(rows):
            flags.add("neg8.midpoint_lost" if slot == "midpoint" else "neg8.reference_lost")
        slots[slot] = readable
    counts.update({slot: len(rows) for slot, rows in slots.items()})
    record.update(corpus_clean_n=len(kept_corpus),
                  corpus_run_ids=[m["run_id"] for m in kept_corpus],
                  reference_run_ids={slot: [m["run_id"] for m in rows] for slot, rows in slots.items()},
                  energy_unreadable_run_ids=unreadable,
                  sources={run_id: value.get("source") for run_id, value in energies.items()},
                  readers={run_id: value.get("reader") for run_id, value in energies.items()})
    if len(kept_corpus) < settings["corpus_minimum"]:
        return finish("undefined", "energy_unreadable" if unreadable else "bound_absent")
    if counts["start"] < 2 or counts["end"] < 2:
        return finish("undefined", "energy_unreadable" if unreadable else "references_insufficient")
    try:
        passed = True
        for family in FAMILIES:
            points = [energies[member["run_id"]][family] for member in kept_corpus]
            bound = neg8_count_adjusted_bound(points, counts["start"], counts["end"])
            if bound is None:
                return finish("undefined", "bound_absent")
            means = {slot: statistics.fmean(energies[m["run_id"]][family] for m in rows) if rows else None
                     for slot, rows in slots.items()}
            if any(value is not None and not math.isfinite(value) for value in means.values()):
                return finish("undefined", "bound_absent")
            difference = abs(means["end"] - means["start"])
            record["families"][family] = {"means_j": means, "bound_terms": bound,
                                          "endpoint_difference_j": difference}
            passed = passed and difference <= bound["bound_j"]
        return finish("passed" if passed else "failed")
    except RestoreRefused:
        raise
    except (OSError, ValueError, KeyError, TypeError, ArithmeticError):
        return finish("undefined", "bound_absent")


def archive_energy_of(archive_root: Path | str, bundle_roots: tuple[Path, ...] = ()) -> Callable:
    """Call the owning reader; do not reproduce its energy arithmetic."""
    from joulewise import whole_window
    from joulewise.desk_restore import readable_run

    helper = getattr(whole_window, "_neg8_writer_reference_energy", None)

    root = Path(archive_root)

    def energy_of(member: Mapping) -> Mapping:
        run_id = member["run_id"]
        candidates = [base / run_id for base in
                      (root / "sources/claim-runs", root / "sources/bound-runs", *bundle_roots)]
        bundle = next((path for path in candidates if path.is_dir()), candidates[0])
        summary = root / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json")
        if not desk_is_file(summary):
            summary = bundle / "summary_metrics.json"
        if helper is not None:
            gross, idle = helper(json.loads(read_bytes(summary).decode("utf-8")))
            reader = "whole_window._neg8_writer_reference_energy"
        else:
            reader = "whole_window._reference_energy_evidence"
            # Main's reader re-derives from primary bytes. The issued reducer
            # needs plain files, including the bundle-contained calibration
            # members. Keep the archive locator as the reported source.
            summary = bundle / "summary_metrics.json"
            journal = Path(str(root) + ".desk") / "compression.jsonl"
            try:
                with readable_run(bundle, compression_records=journal) as plain:
                    gross, idle, problem = whole_window._reference_energy_evidence(plain)
            except RestoreRefused as exc:
                print(str(exc), file=sys.stderr)
                raise
            if problem is not None:
                raise ValueError("NEG8 reference energy is unavailable")
        if gross is None or idle is None:
            raise ValueError("NEG8 reference energy is unavailable")
        return {"gross": gross["point_j"], "idle_subtracted": idle,
                "source": str(summary), "reader": reader}

    energy_of.reader_name = ("whole_window._neg8_writer_reference_energy" if helper is not None
                             else "whole_window._reference_energy_evidence")
    return energy_of


def write(archive_root: Path | str, result: ScreenResult) -> Path:
    target = Path(archive_root) / "withheld/b6-neg8.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result.withheld, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    return target
