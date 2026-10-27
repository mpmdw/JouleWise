#!/usr/bin/env python3
"""Read-only local model hashing for the non-claim align pilot v0 kit (run at the Mac).

Replaces the committed identity_pins.json and model_artifact_inventory.json,
whose hashes were copied from the BYTES Mac check kit for the same model
directories. It does not load models or issue a C4 stack identity.
"""
from __future__ import annotations

import argparse
import json
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
    document, artifacts = kit_identity_pins(args.root, tree, {}, identity=model_artifact_identity,
                                            versions=runtime_versions, runtime_python=args.runtime_python)
    for name, value in (("identity_pins.json", document), ("model_artifact_inventory.json", artifacts)):
        (args.root / KIT / "registration" / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(f"Hashed {len({u['model_source'] for u in document['units'].values()})} local model sources "
          f"for {len(document['units'])} identity units; non-claim file identities only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
