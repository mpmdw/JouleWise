#!/usr/bin/env python3
"""Read-only local model hashing for the non-claim ALIGN pilot 3 kit (run at the Mac).

Replaces the committed identity_pins.json and model_artifact_inventory.json,
whose initial hashes inherit the verified pilot-2 Mac receipt for the same
model directories. The kit generator preserves this fresh local receipt. It does not load models or issue a C4 stack identity.
"""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise.flags.collect import runtime_versions
from joulewise.provenance import model_artifact_identity
from scripts.align_pilot_kit import KIT, kit_identity_pins


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-python", required=True, type=Path)
    parser.add_argument("--root", default=ROOT, type=Path)
    args = parser.parse_args(argv)
    tree = json.loads((args.root / KIT / "plan_tree.json").read_bytes())
    document, artifacts = kit_identity_pins(args.root, tree, {}, identity=model_artifact_identity)
    for name, value in (("identity_pins.json", document), ("model_artifact_inventory.json", artifacts)):
        (args.root / KIT / "registration" / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    verification = {
        "non_claim": True, "scope": "Local files match BYTES; package metadata only, no C4 stack identity",
        "runtime_python_observed": str(args.runtime_python),
        "runtime_versions": runtime_versions(str(args.runtime_python)),
        "identity_pins_sha256": hashlib.sha256((args.root / KIT / "registration/identity_pins.json").read_bytes()).hexdigest(),
        "sources": {u["model_source"]: u["model_artifact_sha256"] for u in document["units"].values()},
    }
    (args.root / KIT / "registration/local_file_verification.json").write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n")
    print(f"Hashed {len({u['model_source'] for u in document['units'].values()})} local model sources "
          f"for {len(document['units'])} identity units; non-claim file identities only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
