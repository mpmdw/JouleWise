"""Production-shaped synthetic custody; never reads any study file."""
import hashlib
import json
from pathlib import Path
import subprocess
import plistlib

from .support import dump
from .support_b6 import b6, build_session, nine_sessions, write_attempts, NINE
from .test_meter import stream_file


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(archive, compress=False):
    """Only a fixture author may mint these synthetic custody pins."""
    if not (archive / b6.SYNTHETIC_MARKER).is_file():
        raise ValueError("fixture_seal_requires_synthetic_marker")
    roster = json.loads((archive / "derived/roster.json").read_bytes())
    flags = [json.loads(line) for line in (archive / "derived/flags.jsonl").read_text().splitlines()]
    waited = {f["scope"]["run_id"] for f in flags if f["code"] == "idle.waited"}
    for root in (archive / "sources/claim-runs", archive / "sources/bound-runs"):
        for metadata in root.glob("*/metadata.json"):
            doc = json.loads(metadata.read_bytes())
            doc["clock_anchor"] = {"wall_minus_monotonic_lower_s": -1000., "wall_minus_monotonic_upper_s": -1000.}
            if metadata.parent.name in waited:
                doc["environment_admission"] = {"attempts": [{"attempt": 1}, {"attempt": 2}]}
                old = metadata.parent / "rich_telemetry_idle.jsonl"
                (metadata.parent / "rich_telemetry_idle_attempt_2.jsonl").write_bytes(old.read_bytes())
                old.write_text(json.dumps({"elapsed_ns": 1000000000, "rail_sum_power_w": 99.}) + "\n")
            dump(metadata, doc)
            idle = plistlib.dumps({"elapsed_ns": 1000000000, "processor": {"gpu_power": 0., "ane_power": 0.}})
            (metadata.parent / "raw/powermetrics_idle.plist").write_bytes(idle)
            events = metadata.parent / "events.jsonl"
            with events.open("a") as out:
                for kind, stamp in (("stage_started", 0.), ("stage_completed", 1.)):
                    out.write(json.dumps({"event_type": kind, "phase": "idle_baseline", "timestamp_s": stamp}) + "\n")
    stream = archive / "sources/night-custody/hazards/meter/stream-synthetic.jsonl"
    stream_file(stream, lambda t: 10. if t < 1. else 50., count=251)
    journal = archive / "sources/night-custody/hazards/monitor/contention.jsonl"
    journal.parent.mkdir(parents=True)
    journal.write_text(json.dumps({"schema": "joulewise.hazard_journal.v1", "module": "contention", "kind": "interval",
        "values": {"interval": {"monotonic_ns": [1000000000000, 1010000000000]}, "outside_total_cpu_s_per_s": .054},
        "error": None}) + "\n")
    dump(archive / "withheld/spans.json", {"spans": {m["run_id"]: {"member": [1000000000000, 1004000000000],
         "request": [1001000000000, 1003000000000]} for m in roster["members"]}})
    # Genuine separate synthetic request-level truth: the finite sample sum
    # and rail trace are closed form; no B5 or B6 meter function is called.
    recorded = {}
    for member in roster["members"]:
        rid = member["run_id"]
        root = "bound-runs" if rid.startswith("neg8-refcorpus") else "claim-runs"
        summary = json.loads((archive / "sources" / root / rid / "summary_metrics.json").read_bytes())
        delta = summary["gross_energy_j"] - .5 * 2
        recorded[rid] = {"machine": {"delta_J": 80., "meter": {"energy_J": 100., "baseline_W": 10., "n": 100},
                                     "battery": {"n": 100}, "window_ns": [1001000000000., 1003000000000.]},
                         "rail_delta_J": delta, "rho": delta / 80.}
    dump(archive / "withheld/meter.json", {"members": recorded})
    sums = archive / "sources/SHA256SUMS"
    sources = [p for p in sorted((archive / "sources").rglob("*")) if p.is_file() and p != sums]
    sums.write_text("".join(f"{sha(p)}  {p.relative_to(archive / 'sources')}\n" for p in sources))
    harvest = json.loads((archive / "harvest.json").read_bytes())
    harvest["outputs"] = {str(p.relative_to(archive)): sha(p) for folder in ("derived", "withheld")
                          for p in sorted((archive / folder).rglob("*")) if p.is_file()}
    dump(archive / "harvest.json", harvest)
    pin = {"harvest_sha256": sha(archive / "harvest.json"),
           "acceptance_sha256": sha(archive / "derived/b6-acceptance.json"), "sha256sums_sha256": sha(sums),
           "meter_streams": [str(stream.relative_to(archive))]}
    pin["contention_journal"] = str(journal.relative_to(archive))
    pin["copied_records"] = {family: ["derived/b6-acceptance.json", "derived/flags.jsonl"] for family in (
        "monitor_cost", "arm_host", "battery_phase", "subject_temperature", "reference_history",
        "attempt_history", "g10_history", "block5_codes_carried")}
    if compress:
        rows = []
        targets = [stream, next((archive / "sources/claim-runs").glob("*/raw/powermetrics.plist"))]
        for path in targets:
            rows.append({"event": "compress", "root": "archive", "path": str(path.relative_to(archive)),
                         "size": path.stat().st_size, "sha256": sha(path)})
            subprocess.run(["zstd", "-q", "-1", "-T1", "-f", str(path), "-o", str(path) + ".zst"], check=True)
            path.unlink()
        record = archive / "compression.jsonl"
        record.write_text("".join(json.dumps(row) + "\n" for row in rows))
        pin["compression"] = {"path": record.name, "sha256": sha(record)}
    return pin


def production_block(parent, compress=True):
    archives, attempts, _ = nine_sessions(parent)
    # Three COUNTING sessions in each pack, plus the non-counting ALPHA r2.
    extra, _ = build_session(parent, "ALPHA", 4, 9)
    archives.append(extra)
    specs = [(pack, rnd, (pack, rnd) != ("ALPHA", 2)) for pack, rnd in NINE] + [("ALPHA", 4, True)]
    write_attempts(attempts, specs)
    pins = {a.name: seal(a, compress=compress and i == 0) for i, a in enumerate(archives)}
    document = parent / "run-inputs.json"
    dump(document, {"host": "Air", "l9_audit": "not_run", "sessions": pins,
                    "external": {"loop_attempts": sha(attempts)}})
    return archives, attempts, document
