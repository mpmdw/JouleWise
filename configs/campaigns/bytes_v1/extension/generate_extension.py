#!/usr/bin/env python3
"""BYTES extension packs: extra held-out models outside the registered roster.

Authority: docs/registrations/bytes_extension_models_2026-10-27.md (Ed). Each
extension model gets one pass (one 50-run floor module, the registered workload)
in its own sub-pack. The registered generator, roster, packs bytes-s1..s6 and
the registered analysis are untouched: this file only reads them.

Every value that needs the measurement Mac lives in ``slots.json`` beside this
file as an explicit MAC-PENDING slot. Until the slots are filled the pack stays
draft and no plan tree is written. ``--tree`` (desk only) refuses while any
slot it needs is pending. No download, inference or measurement happens here.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path("configs/campaigns/bytes_v1/extension")
SLOTS = HERE / "slots.json"
AUTHORITY = "docs/registrations/bytes_extension_models_2026-10-27.md"
END_T0_BEFORE = "2026-11-05T00:00:00-08:00"  # docs/registrations/bytes_end_date_amendment_2026-10-27.md
MAC_PENDING = "MAC-PENDING"


def _load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


configs = _load("bytes_configs", "configs/campaigns/bytes_v1/generate_configs.py")

# One row per extension model. Only a "prepared" model gets configs and a pack.
EXTENSION = (
    {"model_id": "qwen38-27b-8bit", "name": "Qwen3.8-27B-8bit", "family": "qwen3.8", "bits": 8,
     "hf_repo": "mlx-community/Qwen3.8-27B-8bit", "kind": "dense", "pack_id": "bytes-s7-p1",
     "status": "prepared"},
    {"model_id": "nemotron35-super-120b-a12b", "name": "Nemotron-3.5-Super-120B-A12B-4bit",
     "family": "nemotron_h", "bits": 4, "hf_repo": None, "kind": "moe_hybrid_mamba",
     "pack_id": "bytes-s8-p1", "status": "dropped_not_feasible",
     "evidence": ".codex-report/BY-EXT-1.md section 1"},
)
PREPARED = tuple(row for row in EXTENSION if row["status"] == "prepared")


def pending(value):
    return value == MAC_PENDING or value is None


def read_slots(repo_root=ROOT):
    return json.loads((Path(repo_root) / SLOTS).read_bytes())


def config_dirs(model_id):
    return [(HERE / model_id / stage).as_posix() for stage in configs.STAGES]


def model_block(spec, slots):
    """Plain local-dir source, like Qwen3-8B-8bit and Qwen3.5-122B: one download
    destination, the revision pinned separately and never inferred."""
    revision = slots["models"][spec["model_id"]]["revision"]
    return {"name": spec["name"], "family": spec["family"],
            "source": f"/Users/edr/jw_models/{spec['hf_repo']}",
            "revision": None if pending(revision) else revision, "weight_format": "mlx"}


def run_config(template, run, model, bits, group_size, model_id, *, extension=True):
    """The registered generator's run-config body (generate_configs.build_files).

    With extension=False this reproduces a registered config byte for byte;
    the tests hold it to that, so the workload cannot drift from §3.
    """
    cfg = deepcopy(template)
    cfg.update(run_id=run["run_id"], model=model,
               quantization={"name": f"int{bits}", "bits": bits, "group_size": group_size},
               workload_profile={"name": "bytes_synthetic_2048_decode_512", "prompt_tokens": 2048,
                                 "output_tokens": 512, "repetitions": 1, "warmup_runs": 1})
    cfg["hardware_target"]["notes"] = ("BYTES extension draft (" + AUTHORITY + "); never part of the registered roster; "
                                       "requires its MAC-PENDING slots, C4 identity pins and a refuter gate before registration."
                                       if extension else
                                       "BYTES draft; requires C4 identity pins and R8 Mac checks before registration.")
    tags = ["bytes-v1", "floor-calibration", "launch_lineage_required", "draft",
            f"bytes-model={model_id}", "bytes-phase=decode", "bytes-null-contrast", f"rep{run['rep']}"]
    if extension:
        tags.insert(1, "bytes-extension")
    cfg["run_metadata"] = {"project": "capstone-joulewise", "operator": "lead", "tags": tags}
    return cfg


def model_files(spec, slots, template):
    files = {}
    model = model_block(spec, slots)
    group_size = slots["models"][spec["model_id"]]["group_size"]["value"]
    for directory, runs in zip(config_dirs(spec["model_id"]), configs.assembly(spec["model_id"])):
        entries = []
        for index, run in enumerate(runs, 1):
            raw = configs.raw_json(run_config(template, run, model, spec["bits"], group_size, spec["model_id"]))
            filename = run["run_id"] + ".json"
            files[Path(directory) / filename] = raw
            entries.append({**run, "index": index, "config": filename, "config_sha256": configs.sha(raw),
                            "model_tag": spec["model_id"] + "-mlx", "workload": "bytes_synthetic_2048_decode_512"})
        files[Path(directory) / "order_manifest.json"] = configs.raw_json({
            "schema_version": "joulewise.order_manifest.v1",
            "manifest_id": "bytes-" + spec["model_id"] + "-" + Path(directory).name,
            "planned_n_bundles": len(entries), "executed_order": entries})
    return files


def roster(slots, template):
    rows, dropped = [], []
    for spec in EXTENSION:
        row = {"model_id": spec["model_id"], "kind": spec["kind"], "hf_repo": spec["hf_repo"],
               "pack_id": spec["pack_id"], "status": spec["status"], "role": "extension_held_out",
               "registered_roster_member": False}
        if spec["status"] == "prepared":
            model = model_block(spec, slots)
            row.update(model=model, identity_status="draft_pending_C4",
                       revision_status="pinned_source" if model["revision"] else MAC_PENDING)
            rows.append(row)
        else:
            # Kept out of "models": no configs, no source, no identity unit.
            row.update(model={"name": spec["name"], "family": spec["family"]}, evidence=spec["evidence"])
            dropped.append(row)
    return {"status": "draft", "authority": AUTHORITY, "registered_roster": "configs/campaigns/bytes_v1/roster.json",
            "note": "Extension models only. Never merged into the registered roster, fit set, H1 family or H2 fits.",
            "models": rows, "dropped": dropped, "workload": json.loads((ROOT / configs.PACK / "roster.json").read_bytes())["workload"],
            "minimum_kept_units_per_stratum": 5}


def pending_slots(slots, model_id):
    """Every MAC-PENDING slot for one model, as JSON pointers (sorted).

    A slot is an object whose status is MAC-PENDING (reported once, whatever
    its fields hold) or a bare MAC-PENDING value outside such an object.
    """
    found = []

    def walk(value, pointer):
        if isinstance(value, dict):
            if value.get("status") == MAC_PENDING:
                found.append(pointer)
                return
            for key, item in value.items():
                walk(item, f"{pointer}/{key}")
        elif value == MAC_PENDING:
            found.append(pointer)

    walk(slots["models"][model_id], f"/models/{model_id}")
    walk(slots["packs"][next(s["pack_id"] for s in EXTENSION if s["model_id"] == model_id)],
         "/packs/" + next(s["pack_id"] for s in EXTENSION if s["model_id"] == model_id))
    return sorted(set(found))


def registration(spec, slots, repo_root=ROOT):
    bpt = _load("bytes_plan_trees", "scripts/bytes_plan_trees.py")
    pack_slots = slots["packs"][spec["pack_id"]]
    value = json.loads((ROOT / "configs/b6/registration_template.json").read_bytes())
    est = pack_slots["est_minutes"]
    status = pack_slots["registration_status"]
    value.update(pack_id=spec["pack_id"], title=f"BYTES extension {spec['pack_id']}: {spec['name']}, pass 1 only",
                 question="Does decode energy follow format-derived bytes per token, resident size, or decode time?",
                 status=status, kind="new", session_shape="fixed",
                 plan_tree_ref=f"configs/campaigns/{spec['pack_id']}/plan_tree.json",
                 target_sessions=1, minimum_sessions=1, estimators=deepcopy(bpt.ESTIMATORS),
                 flag_catalog="configs/b6/flag_catalog_b6.json",
                 stopping={"count": 1, "end_t0_before": END_T0_BEFORE, "precision": None},
                 blinding_group="bytes", interleave="none", reference_cadence="session_half")
    # The same registered analysis module evaluates extension rows (rule 4);
    # its file is unchanged, so its digest is the pass-1 one.
    for estimator in value["estimators"]:
        estimator["version"] = bpt.AGREED_ESTIMATOR_VERSION
    value["modules"] = [{"module_id": "bytes-" + spec["model_id"], "kind": "floor", "phase": "decode",
                         "config_dirs": config_dirs(spec["model_id"]), "run_count": 50,
                         "est_minutes": None if pending(est["value"]) else est["value"],
                         "est_minutes_source": est["source"]}]
    value["pack_unit"] = [m["module_id"] for m in value["modules"]]
    value["bytes_pass"] = 1
    value["bytes_extension"] = {
        "authority": AUTHORITY, "registered_roster_member": False, "model_id": spec["model_id"],
        "passes": [1], "schedule": "after every registered pass-1 sub-pack and the fit set; dropped first if time runs short",
        "h1_family": "extension checks only (3 per boundary per extension model); never added to the registered 21",
        "h2": "not in any registered fit; printed only as a labelled deviation from the tier line",
        "predictions": "committed registered lines, unchanged; no extension result before predictions.sha256 is recorded",
        "export": "never inside the registered analysis's --export tree",
        "pending_slots": pending_slots(slots, spec["model_id"])}
    catalog = bpt.load_catalog(ROOT / value["flag_catalog"])
    value["flag_effects"] = {code: catalog.entry(code)["effect"] for code in sorted(catalog.codes)}
    value["flag_effects"]["cell.below_minimum"] = "DISCLOSE"
    value["flag_catalog_sha256"] = catalog.sha256
    if status == "draft":
        value["draft_notes"] = [
            "BYTES extension pack (" + AUTHORITY + "): one pass, own sub-pack, never part of the registered roster, "
            "fit set, H1 family or H2 fits. Rows go to the bytes withheld store like any held-out model.",
            "Open MAC-PENDING slots are listed in bytes_extension.pending_slots and in "
            + SLOTS.as_posix() + "; nothing in them is guessed. The plan tree is written at the desk by "
            "generate_extension.py --tree once they are filled.",
            "Gate policy rule 5: one blind executing refuter before any session of this model.",
        ]
    return value


def validation_errors(value, repo_root=ROOT):
    """Validator errors, less the one a pending module estimate must raise."""
    bpt = _load("bytes_plan_trees", "scripts/bytes_plan_trees.py")
    catalog = bpt.load_catalog(ROOT / value["flag_catalog"])
    errors = bpt.validate(bpt.Registration(value), catalog, root=repo_root)
    if value["modules"][0]["est_minutes"] is None and value["status"] == "draft":
        errors = [e for e in errors if e != "modules[0].est_minutes"]
    return errors


def build_files(repo_root=ROOT, slots=None):
    slots = slots if slots is not None else read_slots(repo_root)
    template = json.loads((ROOT / configs.TEMPLATE).read_bytes())
    files = {HERE / "roster.json": configs.raw_json(roster(slots, template))}
    for spec in PREPARED:
        files.update(model_files(spec, slots, template))
    return files, slots


def registrations(repo_root=ROOT, slots=None):
    slots = slots if slots is not None else read_slots(repo_root)
    out = {}
    for spec in PREPARED:
        value = registration(spec, slots, repo_root)
        errors = validation_errors(value, repo_root)
        if errors:
            raise ValueError(f"{spec['pack_id']}: {errors}")
        out[Path("configs/b6/packs") / spec["pack_id"] / "registration.json"] = configs.raw_json(value)
    return out


@contextmanager
def _extension_tree_context(bpt, registered):
    """bytes_plan_trees reads the registered roster for identity units and marks
    pass 1 registered. For an extension tree, name units from the extension
    roster and keep the tree draft until this pack itself is registered."""
    pack, passes = bpt.configs.PACK, bpt.REGISTERED_PASSES
    bpt.configs.PACK = HERE
    bpt.REGISTERED_PASSES = frozenset({1}) if registered else frozenset()
    try:
        yield
    finally:
        bpt.configs.PACK, bpt.REGISTERED_PASSES = pack, passes


def tree(spec, repo_root=ROOT, slots=None):
    """Desk only: refuses while a slot the tree depends on is pending."""
    slots = slots if slots is not None else read_slots(repo_root)
    missing = pending_slots(slots, spec["model_id"])
    if missing:
        raise ValueError(f"{spec['pack_id']}: MAC-PENDING slots open: {missing}")
    bpt = _load("bytes_plan_trees", "scripts/bytes_plan_trees.py")
    value = registration(spec, slots, repo_root)
    with _extension_tree_context(bpt, value["status"] == "registered"):
        files, keep = bpt.tree_files(value, repo_root)
    return files, keep


def _emit(files, output_root, check):
    for relative, raw in files.items():
        target = Path(output_root) / relative
        if check:
            if target.read_bytes() != raw:
                raise ValueError(f"generated bytes drifted: {relative}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)


def generate(output_root=ROOT, check=False, repo_root=ROOT):
    files, _ = build_files(repo_root)
    _emit(files, output_root, check)
    # The validator counts the order manifests just written under output_root.
    packs = registrations(output_root)
    _emit(packs, output_root, check)
    return {**files, **packs}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--tree", action="store_true",
                        help="desk only: also write each extension plan tree (refuses on pending slots)")
    args = parser.parse_args(argv)
    files = generate(args.output_root, args.check)
    if args.tree:
        for spec in PREPARED:
            trees, keep = tree(spec, args.output_root)
            _emit(trees, args.output_root, args.check)
            print(f"{spec['pack_id']} smoke_keep entry for configs/b6/smoke_keep.json: "
                  + json.dumps({spec["pack_id"]: keep}, sort_keys=True))
    print(("verified" if args.check else "generated") + f" {len(files)} BYTES extension files "
          f"({len(PREPARED)} prepared extension model(s) x 50 configs); registered packs untouched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
