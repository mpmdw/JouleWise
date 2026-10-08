"""Rebuild the instrument cadence fixtures (provenance tool, not a test).

Each fixture keeps, from one archived real powermetrics capture, the
``elapsed_ns`` of its first 300 frames (the production idle count) and the
values of its first frame that the production parser requires, with the
source path and the SHA-256 of the whole capture.  The fake powermetrics
(``instrument/fake_powermetrics.py``) re-serialises those values as a
NUL-framed plist stream; the cadence physics (the frame intervals) are the
archived ones.
"""
from __future__ import annotations

import hashlib
import json
import plistlib
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "instrument"


def build(source: str, name: str, note: str) -> None:
    data = Path(source).read_bytes()
    frames = [part for part in data.split(b"\0") if part.strip()][:300]
    documents = [plistlib.loads(part) for part in frames]
    first = documents[0]
    processor = {key: first["processor"][key] for key in
                 ("cpu_power", "gpu_power", "ane_power", "cpu_energy", "gpu_energy", "ane_energy")}
    record = {"schema": "joulewise.hazard_cadence_fixture.v1", "note": note,
              "source": source, "source_sha256": hashlib.sha256(data).hexdigest(),
              "frames": len(documents),
              "elapsed_ns": [int(item["elapsed_ns"]) for item in documents],
              "first_timestamp": first["timestamp"].isoformat(),
              "processor": processor, "thermal_pressure": first.get("thermal_pressure"),
              "kern_osversion": first.get("kern_osversion"), "hw_model": first.get("hw_model")}
    (OUT / name).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(name, len(documents))


if __name__ == "__main__":
    build(sys.argv[1], "cadence-20260919-n1-d01-launchd.json",
          "09-19 n1 d01: default-ProcessType launchd night agent; the slow-cadence defect")
    build(sys.argv[2], "cadence-20261004-block3-idle.json",
          "10-04 block 3 (1305Z) g2a-large-p0512-r01 idle capture under the Interactive launchd job")
