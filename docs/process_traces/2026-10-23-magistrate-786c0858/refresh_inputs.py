"""Refresh deterministic BYTES inputs, preserving all recorded runtime evidence."""
import fnmatch
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts import bytes_plan_trees as plans
from joulewise.b6 import registration
from joulewise.identity_pins import (
    canonical_json_sha256, identity_unit_config_set_sha256,
    scientific_config_identity_sha256,
)

ALLOWED = ["configs/campaigns/bytes_v1/**", "configs/campaigns/bytes-s[1-6]-p[12]/**",
           "configs/b6/packs/**", "configs/bytes/identity_pins.json",
           "configs/b6/registration/identity_pins.json"]


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def write_changed(files):
    changed = {str(path): raw for path, raw in files.items()
               if not (ROOT / path).is_file() or (ROOT / path).read_bytes() != raw}
    outside = [path for path in changed if not any(fnmatch.fnmatchcase(path, p) for p in ALLOWED)]
    if outside:
        raise RuntimeError("NEEDS_SCOPE: " + repr(outside))
    for path, raw in changed.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    print(f"Refreshed {len(changed)} changed authorized files")


write_changed(plans.configs.build_files())
write_changed(plans.build_files())
source_path = Path("configs/bytes/identity_pins.json")
source = json.loads((ROOT / source_path).read_bytes())
for row in source["packs"].values():
    row["tree_sha256"] = sha(row["tree_path"])
write_changed({source_path: plans.configs.raw_json(source)})

target_path = Path("configs/b6/registration/identity_pins.json")
document = json.loads((ROOT / target_path).read_bytes())
source_digest = sha(source_path)
document["bytes_c4"]["file_source"]["sha256"] = source_digest
for row in document["bytes_c4"]["packs"]:
    row["plan_tree"]["sha256"] = sha(row["plan_tree"]["path"])
for name, unit in document["units"].items():
    if "bytes_file_evidence" not in unit:
        continue
    evidence = unit["bytes_file_evidence"]
    evidence["source"]["sha256"] = source_digest
    configs = []
    for row in evidence["config_inventory"]:
        row["sha256"] = sha(row["path"])
        configs.append(json.loads((ROOT / row["path"]).read_bytes()))
    evidence["config_inventory_sha256"] = canonical_json_sha256(evidence["config_inventory"])
    evidence["config_set_sha256"] = identity_unit_config_set_sha256(
        scientific_config_identity_sha256(c) for c in configs)
    assert evidence["config_count"] == len(configs)
    unit["model_revision"] = source["units"][name]["model_revision"]
write_changed({target_path: plans.configs.raw_json(document)})
registration.load_identity_pins(ROOT / target_path)
print("PASS: source/consumer tree hashes, inventories and source binding refreshed; runtime evidence retained")
