"""Rebuild ``battery/publications-20260925-20261005.json`` (provenance tool, not a test).

Scans archived ``ioreg -r -c AppleSmartBattery`` captures (raw ``.ioreg``
files and the ``raw_stdout`` strings embedded in night receipts), keeps one
record per distinct gauge publication (UpdateTime), and stores the fields the
hazard battery module reads, with the source path and the SHA-256 of the
exact bytes read.  Synthetic fixtures (names containing ``synthetic``) are
skipped.  Run from the repository root:

    python3 tests/fixtures/hazards/tools/build_battery_publications.py \
        /Users/edr/night-archive tests/fixtures tests/fixtures/hazards/battery/float-20261005-desk.ioreg
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from joulewise.hazards import battery  # noqa: E402

OUT = ROOT / "tests/fixtures/hazards/battery/publications-20260925-20261005.json"


def blobs(path: Path):
    if path.suffix in (".ioreg", ".txt"):
        data = path.read_bytes()
        if b"+-o AppleSmartBattery" in data and data.startswith(b"+-o AppleSmartBattery"):
            yield "file", data
        return
    if path.suffix == ".json":
        try:
            document = json.loads(path.read_text())
        except ValueError:
            return
        stack = [("", document)]
        while stack:
            where, item = stack.pop()
            if isinstance(item, dict):
                stack.extend((f"{where}/{k}", v) for k, v in item.items())
            elif isinstance(item, list):
                stack.extend((f"{where}[{i}]", v) for i, v in enumerate(item))
            elif isinstance(item, str) and item.startswith("+-o AppleSmartBattery"):
                yield where, item.encode()


def main(roots):
    seen = {}
    for root in roots:
        root = Path(root)
        paths = [root] if root.is_file() else sorted(p for p in root.rglob("*")
                                                     if p.is_file() and p.suffix in (".ioreg", ".txt", ".json")
                                                     and p.stat().st_size < 2_000_000)
        for path in paths:
            if "synthetic" in path.name or "results-clone" in str(path):
                continue
            for where, data in blobs(path):
                update = battery.update_time(data)
                if update is None or update in seen:
                    continue
                try:
                    values = battery.parse_reading(data, float(update))
                except Exception:
                    continue
                seen[update] = {"source": str(path), "embedded_at": where,
                                "sha256": hashlib.sha256(data).hexdigest(),
                                "update_time_s": update,
                                "instant_amperage_ma": values["instant_amperage_ma"],
                                "amperage_ma": values["amperage_ma"],
                                "voltage_mv": values["voltage_mv"],
                                "is_charging": values["is_charging"],
                                "external_connected": values["external_connected"],
                                "adapter_watts": values["adapter_watts"],
                                "power_telemetry": values["power_telemetry"]}
    rows = [seen[key] for key in sorted(seen)]
    OUT.write_text(json.dumps({"schema": "joulewise.hazard_battery_publications.v1",
                               "note": "one record per distinct gauge publication; see the battery module docstring",
                               "publications": rows}, indent=1, sort_keys=True) + "\n")
    print(f"{len(rows)} publications -> {OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
