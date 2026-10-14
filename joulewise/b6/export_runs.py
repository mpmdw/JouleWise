"""Per-run harvest table; offsets are applied only at this export boundary."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from joulewise.b6 import blinding
from joulewise.b6.acceptance import evidence_from_archive
from joulewise.b6.archive import bundle_of, ordered_roster, read_json

PHASES = ("tokenize", "generation_setup", "prefill", "decode")
BOUND_TERMS = ("E_clock_anchor_shift_bound", "E_drift_bound",
               "E_interpolation_edge_bound", "E_interpolation_joint_edge_bound")
ENERGIES = tuple("phase_" + phase + "_j" for phase in PHASES) + (
    "gross_energy_j", "idle_subtracted_energy_j", "energy_request_j",
) + tuple("bound_" + term + "_j" for term in BOUND_TERMS) + (
    "idle_power_w", "idle_variance_of_mean_w2",
)
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
        lines = (bundle / "events.jsonl").read_text(encoding="utf-8").splitlines()
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


def export(archive_root: Path | str, plan: Mapping, registration_dir: Path | str,
           pack_records_root: Path | str, export_dir: Path | str, *, non_claim: bool = False,
           evidence=None, acceptance_record: Mapping | None = None) -> ExportResult:
    root = Path(archive_root)
    evidence = evidence or evidence_from_archive(root, plan, registration_dir)
    record = acceptance_record or read_json(root / "derived/b6-acceptance.json")
    roster = ordered_roster(read_json(root / "derived/roster.json", {}), evidence)
    pack_id = record["pack_id"]
    session_id = record.get("session_id") or evidence.session_id or str(roster.get("plan_id") or root.name)
    key_dir = Path(pack_records_root) / pack_id / "blinding"
    excluded, codes = defaultdict(set), defaultdict(set)
    for item in record.get("excluding", []):
        if item.get("scope") == "member":
            excluded[item["run_id"]].add(item["code"])
    flags = [*evidence.runtime.get("_b6", {}).get("flags", []), *record.get("emitted_flags", [])]
    for flag in flags:
        run_id = flag["scope"].get("run_id")
        if run_id:
            codes[run_id].add(flag["code"])
    rows, reference_key = [], None
    for index, member in enumerate(roster.get("members", [])):
        run_id = member["run_id"]
        bundle = bundle_of(root, plan, run_id)
        config = read_json(bundle / "config.json", {}) if bundle else {}
        model, workload = config.get("model") or {}, config.get("workload_profile") or {}
        key = blinding.configuration_key(config)
        if member["role"] in ("corpus", "start", "midpoint", "end"):
            reference_key = reference_key or key
            key = reference_key
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
        row.update(_event_fields(_events(bundle)))
        row["run_start_utc"] = row.get("run_start_utc") or summary.get("started_at")
        row.update({key: summary.get(key) for key in ("ttft_s", "decode_latency_s")})
        idle = summary.get("idle_baseline") or {}
        row["idle_baseline_s"] = idle.get("duration_s")
        row.update(dict.fromkeys(ENERGIES))
        if member["status"] == "succeeded":
            row.update({"phase_" + phase + "_j": (summary.get("phase_energy_j") or {}).get(phase) for phase in PHASES})
            row.update({key: summary.get(key) for key in ("gross_energy_j", "idle_subtracted_energy_j", "energy_request_j")})
            row.update({"bound_" + term + "_j": (summary.get("energy_bound_terms_j") or {}).get(term + "_j")
                        for term in BOUND_TERMS})
            row["idle_power_w"] = idle.get("power_w_mean")
            row["idle_variance_of_mean_w2"] = (summary.get("idle_mean_uncertainty") or {}).get("governed_variance_of_mean_w2")
        if not non_claim:
            row = blinding.apply(row, blinding.factor(key_dir, key, session_id=session_id))
        rows.append(row)
    destination = Path(export_dir) / pack_id
    csv_path = destination / (session_id + ".runs.csv")
    sidecar = destination / (session_id + ".session.json")

    def write_csv(stream):
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    atomic_write(csv_path, write_csv)
    session = {"schema": "joulewise.b6_export_session.v1", "pack_id": pack_id, "session_id": session_id,
               **{key: record.get(key) for key in ("verdict", "counting", "flag_counts")},
               "operative_bound_s": record.get("calibration", {}).get("operative_bound_s"),
               "neg8": record.get("neg8"), "non_claim": non_claim,
               "blinding": {"applied": not non_claim, "key_dir": os.path.relpath(key_dir, destination)}}
    atomic_write(sidecar, lambda stream: stream.write(json.dumps(session, sort_keys=True, indent=2) + "\n"))
    return ExportResult(csv_path, sidecar, len(rows))
