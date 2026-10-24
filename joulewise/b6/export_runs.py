"""Per-run harvest table; offsets are applied only at this export boundary."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from joulewise.b6 import blinding
from joulewise.b6.acceptance import evidence_from_archive
from joulewise.b6.archive import (CLOCK_ANCHOR_STATUS, bundle_of, ordered_roster, read_json,
                                unresolved_clock_anchor)
from joulewise.desk_compress import read_bytes

PHASES = ("tokenize", "generation_setup", "prefill", "decode")
BOUND_TERMS = ("E_clock_anchor_shift_bound", "E_drift_bound",
               "E_interpolation_edge_bound", "E_interpolation_joint_edge_bound")
ENERGIES = tuple("phase_" + phase + "_j" for phase in PHASES) + (
    "gross_energy_j", "idle_subtracted_energy_j", "energy_request_j",
) + tuple("bound_" + term + "_j" for term in BOUND_TERMS) + (
    "idle_power_w", "idle_variance_of_mean_w2",
)
REFERENCE_KEY = "neg8_reference"
REFERENCE_REQUEST_COLUMNS = ("reference_request_gross_j", "reference_request_idle_subtracted_j",
                             "reference_request_duration_s")
COLUMNS = (
    "pack_id", "session_id", "attempt", "run_id", "stage_id", "role", "order_index",
    "cell_ids", "strata", "unit_ids", "abba_block_id", "abba_label", "config_key",
    "model_name", "workload_name", "status", "excluded", "exclusion_codes", "flag_codes", "non_claim",
) + ENERGIES + ("prompt_tokens", "emitted_tokens", "requested_output_tokens") + tuple(
    "dur_" + phase + "_s" for phase in PHASES
) + ("idle_baseline_s", "ttft_s", "decode_latency_s", "run_start_utc")


@dataclass(frozen=True)
class ExportResult:
    csv_path: Path
    sidecar_path: Path
    row_count: int

    def structure(self) -> dict:
        return {"csv": str(self.csv_path), "session": str(self.sidecar_path), "rows": self.row_count}


def atomic_write(path: Path, writer) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _events(bundle: Path | None) -> list[dict]:
    if bundle is None:
        return []
    try:
        lines = read_bytes(bundle / "events.jsonl").decode("utf-8").splitlines()
    except FileNotFoundError:
        return []
    return [json.loads(line) for line in lines if line.strip()]


def _event_fields(events: list[dict]) -> dict:
    result, starts = {}, {}
    for event in events:
        phase, kind = event.get("phase"), event.get("event_type")
        meta = event.get("metadata") or {}
        if kind == "phase_start":
            starts[phase] = event["timestamp_s"]
        elif kind == "phase_end":
            if phase in starts and phase in PHASES:
                result["dur_" + phase + "_s"] = event["timestamp_s"] - starts[phase]
            for key in ("prompt_tokens", "emitted_tokens", "requested_output_tokens"):
                if key in meta:
                    result[key] = meta[key]
            if phase == "decode" and "output_tokens" in meta:
                result["emitted_tokens"] = meta["output_tokens"]
        elif kind == "run_started":
            result["run_start_utc"] = event.get("timestamp_utc") or (
                datetime.fromtimestamp(event["timestamp_s"], timezone.utc).isoformat()
                if event.get("timestamp_s") is not None else None)
    return result


def _reference_request_fields(bundle, events, summary, record, archive_root, *, physics_cache=None):
    """Clock-free reference integrals on tokenize start through decode end.

    Use the reducer's native reconstructed curve, rather than a sum of phase
    energies: gaps between phases are part of the request too.
    """
    from joulewise.bundle_read import BundleReader, BundleReadError
    from joulewise.desk_restore import readable_run
    from joulewise.reduce import (REDUCER_VERSION, _derive_anchor_context,
                                  _assert_trace_matches_raw, _integrate)
    starts = [e["timestamp_s"] for e in events
              if e.get("phase") == "tokenize" and e.get("event_type") == "phase_start"]
    ends = [e["timestamp_s"] for e in events
            if e.get("phase") == "decode" and e.get("event_type") == "phase_end"]
    if bundle is None or len(starts) != 1 or len(ends) != 1:
        return {}
    start, end = starts[0], ends[0]
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in (start, end)) or end <= start:
        return {}
    try:
        journal = Path(str(archive_root) + ".desk") / "compression.jsonl"
        with readable_run(bundle, compression_records=journal) as plain:
            reader = BundleReader(plain)
            curve = reader.summed_curve()
            bound = (record.get("calibration") or {}).get("operative_bound_s")
            version = (summary.get("summary_provenance") or {}).get("reducer_version", REDUCER_VERSION)
            context = _derive_anchor_context(reader, reader.metadata(), reducer_version=version,
                authenticated_fiducial_bound_override_s=float(bound) if bound is not None else None,
                instrument_calibration_physics_cache=physics_cache)
            if context.telemetry_is_powermetrics:
                if context.unresolved or context.curve is None:
                    return {}
                _assert_trace_matches_raw(curve, context.curve)
                curve = context.curve
            if not curve:
                return {}
            gross = _integrate(curve, start, end)
        idle = (summary.get("idle_baseline") or {}).get("power_w_mean")
        if type(idle) not in (int, float) or not math.isfinite(idle):
            return {}
        return dict(zip(REFERENCE_REQUEST_COLUMNS, (gross, gross - idle * (end - start), end - start)))
    except (OSError, ValueError, KeyError, TypeError, ArithmeticError, BundleReadError):
        # A reference without a usable request record cannot supply NEG-8.
        # Keep the row and its existing status; the BYTES reader records the
        # missing reference input rather than manufacturing an energy value.
        return {}


def export(archive_root: Path | str, plan: Mapping, registration_dir: Path | str,
           pack_records_root: Path | str, export_dir: Path | str, *, non_claim: bool = False,
           evidence=None, acceptance_record: Mapping | None = None,
           pack_registration: Mapping | None = None) -> ExportResult:
    root = Path(archive_root)
    evidence = evidence or evidence_from_archive(root, plan, registration_dir)
    record = acceptance_record or read_json(root / "derived/b6-acceptance.json")
    roster = ordered_roster(read_json(root / "derived/roster.json", {}), evidence)
    pack_id = record["pack_id"]
    session_id = record.get("session_id") or evidence.session_id or str(roster.get("plan_id") or root.name)
    if pack_registration is None:
        # Prefer the harvested registration to the desk checkout. The explicit
        # argument is for synthetic/seam callers; normal harvest needs no flag.
        candidates = (root / "sources/pack/registration.json",
                      root / "sources/repo/configs/b6/packs" / pack_id / "registration.json",
                      Path(registration_dir) / "registration.json",
                      Path(__file__).resolve().parents[2] / "configs/b6/packs" / pack_id / "registration.json")
        # Closed replication archives name their campaign (d117_...), while
        # their registrations are alpha/beta/gamma. Resolve the registered
        # plan reference rather than treating that known alias as unregistered.
        plan_ref = f"configs/campaigns/{pack_id}/plan_tree.json"
        for packs in (root / "sources/repo/configs/b6/packs",
                      Path(__file__).resolve().parents[2] / "configs/b6/packs"):
            candidates += tuple(path for path in sorted(packs.glob("*/registration.json"))
                                if isinstance(doc := read_json(path), Mapping)
                                and doc.get("plan_tree_ref") == plan_ref)
        pack_registration = next((doc for path in candidates
                                  if isinstance(doc := read_json(path), Mapping) and doc
                                  and (doc.get("pack_id", pack_id) == pack_id
                                       or doc.get("plan_tree_ref") == plan_ref)), None)
        if not isinstance(pack_registration, Mapping) or not pack_registration:
            raise ValueError(f"pack registration unresolved for {pack_id}: "
                             + ", ".join(str(path) for path in candidates))
    elif not isinstance(pack_registration, Mapping) or not pack_registration:
        raise ValueError(f"explicit pack registration empty or malformed for {pack_id}")
    key_dir = blinding.key_directory(pack_records_root, pack_id, pack_registration)
    excluded, codes = defaultdict(set), defaultdict(set)
    for item in record.get("excluding", []):
        if item.get("scope") == "member":
            excluded[item["run_id"]].add(item["code"])
    flags = [*evidence.runtime.get("_b6", {}).get("flags", []), *record.get("emitted_flags", [])]
    for flag in flags:
        run_id = flag["scope"].get("run_id")
        if run_id:
            codes[run_id].add(flag["code"])
    rows, withheld, key_names = [], [], set()
    group = pack_registration.get("blinding_group")
    grouped_blind = bool(group)
    # Every grouped table is offset, including non-claim smoke sessions. The
    # legacy row-level non_claim bit means "offsets not applied" to the existing
    # release reader, so grouped tables keep session provenance in the sidecar
    # and omit that bit. This lets _released_rows remain unchanged.
    columns = (tuple(c for c in COLUMNS if c not in ("run_start_utc", "non_claim")) + ("pass_id",)
               if grouped_blind else COLUMNS)
    bytes_request = group == "bytes" or pack_id == "bytes" or pack_id.startswith("bytes-")
    if bytes_request:
        columns += REFERENCE_REQUEST_COLUMNS
    reference_physics_cache = {}
    for index, member in enumerate(roster.get("members", [])):
        run_id = member["run_id"]
        bundle = bundle_of(root, plan, run_id)
        config = read_json(bundle / "config.json", {}) if bundle else {}
        model, workload = config.get("model") or {}, config.get("workload_profile") or {}
        key = blinding.configuration_key(config)
        if member["role"] in ("corpus", "start", "midpoint", "end"):
            key = REFERENCE_KEY
        tags = dict(tag.split("=", 1) for tag in (config.get("run_metadata") or {}).get("tags", [])
                    if isinstance(tag, str) and "=" in tag)
        units = member.get("units", [])
        row = {"pack_id": pack_id, "session_id": session_id, "attempt": roster.get("attempt"),
               "run_id": run_id, "stage_id": member["stage_id"], "role": member["role"], "order_index": index,
               "cell_ids": ";".join(u["cell_id"] for u in units),
               "strata": ";".join(u["stratum"] for u in units),
               "unit_ids": ";".join(str(u["unit_id"]) for u in units),
               "abba_block_id": tags.get("calibration-abba-block-id"),
               "abba_label": tags.get("calibration-abba-label"), "config_key": key,
               "model_name": model.get("name"), "workload_name": workload.get("name"),
               "status": member["status"], "excluded": bool(excluded[run_id]),
               "exclusion_codes": ";".join(sorted(excluded[run_id])),
               "flag_codes": ";".join(sorted(codes[run_id])), "non_claim": non_claim}
        summary = read_json(root / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json"), {})
        events = _events(bundle)
        row.update(_event_fields(events))
        row["run_start_utc"] = row.get("run_start_utc") or summary.get("started_at")
        row.update({key: summary.get(key) for key in ("ttft_s", "decode_latency_s")})
        idle = summary.get("idle_baseline") or {}
        row["idle_baseline_s"] = idle.get("duration_s")
        row.update(dict.fromkeys(ENERGIES))
        unresolved = (summary.get("energy_status") == CLOCK_ANCHOR_STATUS
                      or unresolved_clock_anchor(read_json(bundle / "metadata.json", {}) if bundle else {},
                                                 summary, codes[run_id]))
        if unresolved:
            row["status"] = CLOCK_ANCHOR_STATUS
        if member["status"] == "succeeded" and not unresolved:
            row.update({"phase_" + phase + "_j": (summary.get("phase_energy_j") or {}).get(phase) for phase in PHASES})
            row.update({key: summary.get(key) for key in ("gross_energy_j", "idle_subtracted_energy_j", "energy_request_j")})
            row.update({"bound_" + term + "_j": (summary.get("energy_bound_terms_j") or {}).get(term + "_j")
                        for term in BOUND_TERMS})
            row["idle_power_w"] = idle.get("power_w_mean")
            row["idle_variance_of_mean_w2"] = (summary.get("idle_mean_uncertainty") or {}).get("governed_variance_of_mean_w2")
            if bytes_request and key == REFERENCE_KEY:
                row.update(_reference_request_fields(bundle, events, summary, record, root,
                                                     physics_cache=reference_physics_cache))
        if not non_claim or grouped_blind:
            row = blinding.apply(row, blinding.factor(key_dir, key, session_id=session_id))
            key_names.update(("pack.json", blinding._config_filename(key)))
        if grouped_blind:
            # The registered stage walk supplies order_index; no wall/monotonic
            # clock enters the pre-commit table. Durations remain observables.
            row.pop("run_start_utc", None)
            row.pop("non_claim", None)
            row["pass_id"] = pack_registration.get("bytes_pass")
            (rows if key == REFERENCE_KEY or blinding.configuration_stage(config) == "fit"
             else withheld).append(row)
        else:
            rows.append(row)
    destination = Path(export_dir) / pack_id
    csv_path = destination / (session_id + ".runs.csv")
    sidecar = destination / (session_id + ".session.json")

    def write_csv(stream):
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    withheld_record = None
    if grouped_blind:
        key_sha256 = blinding.bind_session_keys(key_dir, session_id, key_names)
        store = blinding.withheld_path(key_dir, pack_id, session_id)
        def write_withheld(stream):
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(withheld)
        # Persist already offset rows before publishing their count-only locator.
        atomic_write(store, write_withheld)
        counts = defaultdict(int)
        for row in withheld:
            counts[hashlib.sha256(row["config_key"].encode("utf-8")).hexdigest()] += 1
        withheld_record = {"path": os.path.relpath(store, destination), "row_count": len(withheld),
                           "config_key_sha256": dict(sorted(counts.items()))}
    atomic_write(csv_path, write_csv)
    session = {"schema": "joulewise.b6_export_session.v1", "pack_id": pack_id, "session_id": session_id,
               **{key: record.get(key) for key in ("verdict", "counting", "flag_counts")},
               "operative_bound_s": record.get("calibration", {}).get("operative_bound_s"),
               "neg8": record.get("neg8"), "non_claim": non_claim,
               "blinding": {"applied": not non_claim or grouped_blind, "key_dir": os.path.relpath(key_dir, destination)}}
    if grouped_blind:
        session["blinding"]["key_sha256"] = key_sha256
        session["blinding"].update(group=group, pass_id=pack_registration.get("bytes_pass"),
                                    withheld=withheld_record)
    atomic_write(sidecar, lambda stream: stream.write(json.dumps(session, sort_keys=True, indent=2) + "\n"))
    return ExportResult(csv_path, sidecar, len(rows))
