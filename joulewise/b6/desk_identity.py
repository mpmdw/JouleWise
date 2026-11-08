"""Record desk identities with the measurement interpreter; mismatches are notes."""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
from pathlib import Path

EXPECTED = {
    "identity-epoch.json": "b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607",
    "t1-bindings.json": "8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98",
}

IDENTITY_SOURCE = '''import base64, importlib.util, json, sys
from pathlib import Path
source = Path(sys.argv[1])
sys.path.insert(0, str(source.parent.parent))
spec = importlib.util.spec_from_file_location("write_derivation_night_inputs", source)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
epoch, t1 = module._derive_planned_vectors("ac_high_power")
print(json.dumps({name: base64.b64encode(module._json_bytes(value)).decode("ascii")
    for name, value in (("identity-epoch.json", epoch), ("t1-bindings.json", t1))}))
'''

def collect(measurement_root, stage_dir, *, run=subprocess.run):
    measurement, stage = Path(measurement_root), Path(stage_dir)
    stage.mkdir(parents=True, exist_ok=True)
    result = run([str(measurement / ".venv/bin/python"), "-B", "-c", IDENTITY_SOURCE,
                  str(measurement / "scripts/write_derivation_night_inputs.py")],
                 check=True, capture_output=True, text=True, timeout=120)
    payloads = json.loads(result.stdout)
    identities, notes = {}, []
    for name, expected in EXPECTED.items():
        raw = base64.b64decode(payloads[name], validate=True)
        if not isinstance(json.loads(raw), dict):
            raise ValueError("identity producer must write JSON objects")
        target = stage / name
        if target.exists():
            if target.read_bytes() != raw:
                raise ValueError("prepared identity changed: " + name)
        else:
            target.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        identities[name] = {"path": str(target), "sha256": digest, "block3_sha256": expected,
                            "matches_block3": digest == expected}
        if digest != expected:
            notes.append({"kind": "identity_differs_from_block3", "file": name,
                          "sha256": digest, "block3_sha256": expected})
    return identities, notes
