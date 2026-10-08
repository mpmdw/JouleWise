#!/usr/bin/env python3
"""Write the two desk identity files of a block-5 window from the live machine.

Desk helper for the post-seal runbook; it is not part of the repository and never arms anything.
It calls the two functions the calibration writer's own desk tool uses
(scripts/write_derivation_night_inputs.py: _derive_planned_vectors, _json_bytes), run under the
measurement interpreter, so the MLX version and the powermetrics digest are the ones a capture
would record. It writes identity-epoch.json and t1-bindings.json into --stage-dir only when both
serializations hash to the bytes block 3 used; any other result means the machine's identity has
moved since the acceptance was derived, and nothing is written.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

EXPECTED = {
    "identity-epoch.json": "b8a1094c24d1795e39fc527ce96ba9e1a4ba2bda66d4250f35a462e28a90b607",
    "t1-bindings.json": "8dcdfb009d9cf6c7d218bf19667ad1b88f6a9747c6822c02fd2997ef9a1e9d98",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--measurement-root", required=True, type=Path)
    parser.add_argument("--stage-dir", required=True, type=Path)
    parser.add_argument("--power-policy", default="ac_high_power")
    args = parser.parse_args()
    source = args.measurement_root.resolve() / "scripts/write_derivation_night_inputs.py"
    spec = importlib.util.spec_from_file_location("write_derivation_night_inputs", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    epoch, t1 = module._derive_planned_vectors(args.power_policy)
    payloads = {"identity-epoch.json": module._json_bytes(epoch), "t1-bindings.json": module._json_bytes(t1)}
    digests = {name: hashlib.sha256(raw).hexdigest() for name, raw in payloads.items()}
    different = {name: {"live": digests[name], "block_3": EXPECTED[name]}
                 for name in payloads if digests[name] != EXPECTED[name]}
    if different:
        print(json.dumps({"status": "REFUSED", "different": different, "identity_epoch": epoch, "t1_bindings": t1},
                         indent=2, sort_keys=True))
        return 2
    for name, raw in payloads.items():
        with open(args.stage_dir / name, "xb") as stream:
            stream.write(raw)
    print(json.dumps({"status": "WRITTEN", "stage_dir": str(args.stage_dir), "sha256": digests}, indent=2,
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
