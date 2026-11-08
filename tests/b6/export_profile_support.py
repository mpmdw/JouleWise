"""Synthetic archives for export profiling; no external paths or model loads."""
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path
import random
import shutil
import subprocess
import sys
import types

from joulewise import desk_compress
from tests.b6.support import write_json
from tests.b6.test_export_runs import archive_fixture, seal_reference_inputs

SERIAL_EXPORT_COMMIT = "912cf8c3a998b5d9d82c6b96e215871cf21288f4"


@contextmanager
def serial_exporter():
    source = subprocess.run(["git", "show", SERIAL_EXPORT_COMMIT + ":joulewise/b6/export_runs.py"],
                            capture_output=True, text=True, check=True).stdout
    module = types.ModuleType("_bytes_export_serial_oracle")
    sys.modules[module.__name__] = module
    try:
        exec(compile(source, "<serial-export-oracle>", "exec"), module.__dict__)
        yield module
    finally:
        sys.modules.pop(module.__name__, None)


def fixture(root, *, references=16, science=7, blob_bytes=2 * 1024**2, samples=2048,
            compressed=False, interval_trace=False):
    archive, registration, plan, record = archive_fixture(root)
    roster_path = archive / "derived/roster.json"
    roster = json.loads(roster_path.read_bytes())
    template = next(m for m in roster["members"] if m["run_id"] == "ref")
    for index in range(2, references):
        run = f"ref-{index:04d}"
        shutil.copytree(archive / "sources/claim-runs/ref", archive / "sources/claim-runs" / run)
        shutil.copyfile(archive / "withheld/reductions/ref.summary_metrics.rereduced.json",
                        archive / "withheld/reductions" / (run + ".summary_metrics.rereduced.json"))
        roster["members"].append({**template, "run_id": run})
    template = next(m for m in roster["members"] if m["run_id"] == "q0")
    for index in range(7, science):
        run = f"science-{index:04d}"
        shutil.copytree(archive / "sources/claim-runs/q0", archive / "sources/claim-runs" / run)
        shutil.copyfile(archive / "withheld/reductions/q0.summary_metrics.rereduced.json",
                        archive / "withheld/reductions" / (run + ".summary_metrics.rereduced.json"))
        roster["members"].append({**template, "run_id": run})
    write_json(roster_path, roster)
    tree_path = archive / "sources/pack/plan_tree.json"
    tree = json.loads(tree_path.read_bytes())
    tree["stage_graph"][0]["expected_count"] = references
    tree["stage_graph"][1]["expected_count"] = science
    tree["science"].extend(member for member in roster["members"]
                           if member["run_id"].startswith("science-"))
    write_json(tree_path, tree)
    registration_record = {"blinding_group": "bytes", "bytes_pass": 1}
    write_json(archive / "sources/pack/registration.json", registration_record)
    payload = random.Random(701).randbytes(min(blob_bytes, 65536))
    payload = (payload * ((blob_bytes + len(payload) - 1) // len(payload)))[:blob_bytes] if payload else b""
    for member in roster["members"]:
        bundle = archive / "sources/claim-runs" / member["run_id"]
        if member["role"] in ("start", "corpus"):
            if interval_trace:
                (bundle / "power_trace.csv").write_text(
                    "timestamp_s,power_w,rail,source,interval_start_s,interval_end_s\n" + "".join(
                        f"{(i + 1) * 20 / samples},10,mock,mock,{i * 20 / samples},{(i + 1) * 20 / samples}\n"
                        for i in range(samples)))
            else:
                (bundle / "power_trace.csv").write_text("timestamp_s,power_w,rail,source\n" + "".join(
                    f"{i * 20 / (samples - 1)},10,mock,mock\n" for i in range(samples)))
            (bundle / "raw").mkdir()
            (bundle / "raw/synthetic.bin").write_bytes(payload)
        elif member["run_id"].startswith(("q", "science-")):
            config_path = bundle / "config.json"
            config = json.loads(config_path.read_bytes())
            config["model"]["name"] = "Qwen3-4B-4bit"
            write_json(config_path, config)
    seal_reference_inputs(archive)
    if compressed:
        journal = Path(str(archive) + ".desk") / "compression.jsonl"
        journal.parent.mkdir()
        rows = []
        for path in sorted((archive / "sources/claim-runs").rglob("*")):
            if not path.is_file():
                continue
            raw = path.read_bytes()
            info = path.stat()
            subprocess.run([desk_compress.zstd_path(), "-1", "-T1", "-q", str(path), "-o", str(path) + ".zst"],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            rows.append({"event": "compress", "path": str(path), "root": "archive", "size": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest(), "mode": info.st_mode & 0o777,
                         "mtime_ns": info.st_mtime_ns})
            path.unlink()
        journal.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))
    return archive, registration, plan, registration_record
