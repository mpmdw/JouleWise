"""A three-poll, synthetic KM003C stream at a long host clock origin."""
import json
from pathlib import Path
import struct

from independent_recompute.support import recompute as own
from joulewise.external import km003c_parse as parser

path = Path(__file__).with_name("synthetic-meter-stream.jsonl")
points = [(0, 10000000000546129), (10000, 10000010002542062), (20000, 10000020000271267)]
rows = [{"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": 2,
         "status": "streaming", "start_raw_ns": points[0][1], "start_mono_ns": points[0][1]}]
for device, rx in points:
    payload = struct.pack("<HHiiHHHH", device, 0, 10000000, 1000000, 0, 0, 0, 0)
    rows.append({"k": "b", "tx": rx - 1000000, "rx": rx, "n": 1, "p": payload.hex()})
rows.append({"k": "t", "end_raw_ns": points[-1][1] + 1, "end_mono_ns": points[-1][1] + 1})
path.write_text("".join(json.dumps(row) + "\n" for row in rows))
a = own.MeterStream(path, own.Reader("synthetic", []))
b = parser.parse(path)
print("own=", a.times)
print("parser=", b.host_ns)
print("differences_ns=", [x - y for x, y in zip(a.times, b.host_ns)])
print("max_abs_ns=", max(abs(x - y) for x, y in zip(a.times, b.host_ns)))
