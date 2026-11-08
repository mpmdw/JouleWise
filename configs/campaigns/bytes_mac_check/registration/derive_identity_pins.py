#!/usr/bin/env python3
"""Read-only local model hashing for the non-claim BYTES Mac check.

This does not load models, measure their runtime, or issue a C4 stack identity.
The runtime interpreter is explicit because a worktree need not have a venv.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from joulewise.b5.plan import resolve_stage_dispatches
from joulewise.flags.collect import runtime_versions
from joulewise.provenance import model_artifact_identity

KIT = Path("configs/campaigns/bytes_mac_check")


def derive(root, runtime_python, *, identity=model_artifact_identity, versions=runtime_versions):
    root = Path(root)
    tree_raw = (root / KIT / "plan_tree.json").read_bytes()
    tree = json.loads(tree_raw)
    roster = json.loads((root / "configs/campaigns/bytes_v1/roster.json").read_bytes())
    names = {m["model"]["source"]: m["model_id"] for m in roster["models"]}
    counts = {s["stage_id"]: s["expected_count"] for s in tree["stage_graph"]
              if s["kind"] == "campaign_collection"}
    units = {}
    for dispatch in resolve_stage_dispatches(tree, root):
        if dispatch.error:
            raise ValueError(dispatch.error)
        directory = root / dispatch.config_dir
        manifest = json.loads((directory / "order_manifest.json").read_bytes())
        for row in manifest["executed_order"][:counts[dispatch.stage_id]]:
            config_path = directory / row["config"]
            config = json.loads(config_path.read_bytes())
            model = config["model"]
            source = model["source"]
            name = names.get(source, "neg8_reference")
            unit = units.setdefault(name, {
                "model_source": source,
                "model_name": model["name"],
                "model_revision": model.get("revision"),
                "stack_identity": {},
                "flags": ["runtime_stack_unobserved"],
                "config_paths": [],
            })
            if unit["model_source"] != source:
                raise ValueError("multiple reference model sources")
            unit["config_paths"].append(config_path.relative_to(root).as_posix())
    artifacts = {}
    for name, unit in sorted(units.items()):
        artifact = identity(unit["model_source"])
        digest = artifact.get("folded_sha256") or artifact.get("sha256")
        if artifact.get("status") != "ok" or not digest:
            raise ValueError("model files unavailable: " + unit["model_source"])
        unit["model_artifact_sha256"] = digest
        unit["config_count"] = len(unit["config_paths"])
        artifacts[name] = artifact
    document = {
        "schema": "joulewise.b5_identity_pins.v1",
        "non_claim": True,
        "status": "NON_CLAIM_FILE_IDENTITIES_ONLY",
        "runtime_python_observed": str(runtime_python),
        "runtime_versions": versions(str(runtime_python)),
        "units": units,
        "derivation": {
            "model_artifact_sha256": "joulewise.provenance.model_artifact_identity, read-only local weight hashing",
            "runtime_versions": "joulewise.flags.collect.runtime_versions of the explicitly named interpreter",
            "stack_identity": "empty: no model was executed; runtime stack is unobserved, never inferred",
            "config_count": "number of dispatched planned members for this source, including reference members",
            "tree_path": (KIT / "plan_tree.json").as_posix(),
            "tree_sha256": hashlib.sha256(tree_raw).hexdigest(),
        },
    }
    return document, {"non_claim": True, "artifacts": artifacts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-python", required=True, type=Path)
    parser.add_argument("--root", default=ROOT, type=Path)
    args = parser.parse_args(argv)
    document, artifacts = derive(args.root, args.runtime_python)
    for name, value in (("identity_pins.json", document), ("model_artifact_inventory.json", artifacts)):
        target = args.root / KIT / "registration" / name
        target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(f"Hashed {len(document['units'])} local model sources; non-claim file identities only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
