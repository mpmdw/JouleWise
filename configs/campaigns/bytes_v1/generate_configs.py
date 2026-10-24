#!/usr/bin/env python3
"""Deterministic BYTES drafts: ten repeats and ten null ABBA quads per model.

The D-117 generator supplies the floor assembly convention and its run config
supplies hardware/sampling defaults. R2 replaces its chat/suite workload with
exact synthetic ids. No downloads, inference, identity issuance, or measurement.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = Path("configs/campaigns/bytes_v1")
TEMPLATE = Path("configs/campaigns/d117_floor_qwen3-8b_v5/01_phase_decode_absolute/d117fq38-df-ph-decode-abs-r01.json")
ROSTER = (
    ("qwen3-1p7b", "Qwen3-1.7B-4bit", "qwen3", "r_qwen3-1.7b.json"),
    ("qwen3-4b", "Qwen3-4B-4bit", "qwen3", "r_Qwen3-4B-4bit.json"),
    ("qwen3-8b", "Qwen3-8B-4bit", "qwen3", "r_Qwen3-8B-4bit.json"),
    ("qwen3-30b-a3b", "Qwen3-30B-A3B-4bit", "qwen3_moe", "r_Qwen3-30B-A3B-4bit.json"),
    ("qwen3-14b", "Qwen3-14B-4bit", "qwen3", "r_Qwen3-14B-4bit.json"),
    ("qwen3-next-80b", "Qwen3-Next-80B-A3B-Instruct-4bit", "qwen3_next", "r_Qwen3-Next-80B-A3B-Instruct-4bit.json"),
    ("qwen3-32b", "Qwen3-32B-4bit", "qwen3", "r_Qwen3-32B-4bit.json"),
    ("qwen3-8b-8bit", "Qwen3-8B-8bit", "qwen3", None),
    ("llama-70b", "Llama-3.3-70B-Instruct-4bit", "llama", "r_Llama-3.3-70B-Instruct-4bit.json"),
    ("qwen35-122b", "Qwen3.5-122B-A10B-4bit", "qwen3.5", "r_Qwen3.5-122B-A10B-4bit_pinned.json"),
)
STAGES = ("01_decode_absolute", "02_decode_abba_01_05", "03_decode_abba_06_10")


def raw_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def config_dirs(model_id):
    return [(PACK / model_id / stage).as_posix() for stage in STAGES]


def assembly(model_id):
    stages = [[], [], []]
    for rep in range(1, 11):
        stages[0].append({"run_id": f"bytes-{model_id}-abs-r{rep:02}", "rep": rep,
                          "role": "absolute_repeat", "block_id": None, "block_index": rep,
                          "position": None, "position_in_block": 1, "arm": None})
    for block in range(1, 11):
        for index, position in enumerate(("A1", "B1", "B2", "A2"), 1):
            stages[1 if block <= 5 else 2].append({
                "run_id": f"bytes-{model_id}-null-b{block:02}-{position.lower()}",
                "rep": block, "role": "comparative_abba_member", "block_id": f"bytes-{model_id}-null-b{block:02}",
                "block_index": block, "position": position, "position_in_block": index, "arm": position[0]})
    return stages


def model_config(spec):
    model_id, name, family, pilot = spec
    revision = None
    source = f"/Users/edr/jw_models/mlx-community/{name}"
    if pilot:
        p = json.loads((ROOT / "docs/design/bytes_pilot" / pilot).read_bytes())
        source = p["snapshot"]
        snapshot = Path(source)
        if snapshot.parent.name == "snapshots":
            revision = snapshot.name
    if model_id == "qwen35-122b":
        revision = json.loads((ROOT / "configs/examples/mac_mlx_qwen35_122b.json").read_bytes())["model"]["revision"]
    if model_id == "qwen3-8b-8bit":
        # Download receipt: configs/bytes/records/RUN.md, addendum 16:17 PDT.
        revision = "48a0b75b1ae72503e21e1558d040bc227510ff06"
    return {"name": name, "family": family, "source": source,
            "revision": revision, "weight_format": "mlx"}


def build_files():
    template = json.loads((ROOT / TEMPLATE).read_bytes())
    files, roster = {}, []
    for spec in ROSTER:
        model_id, name, family, pilot = spec
        model = model_config(spec)
        bits = 8 if model_id == "qwen3-8b-8bit" else 4
        roster.append({"model_id": model_id, "model": model, "pilot": pilot,
                       "role": "fit" if model_id in ("qwen3-1p7b", "qwen3-4b", "qwen3-8b") else "held_out",
                       "identity_status": "draft_pending_C4", "revision_status": "pinned_source" if model["revision"] else "pending_download_R8_5"})
        for directory, runs in zip(config_dirs(model_id), assembly(model_id)):
            entries = []
            for index, run in enumerate(runs, 1):
                cfg = deepcopy(template)
                cfg.update(run_id=run["run_id"], model=model,
                           quantization={"name": f"int{bits}", "bits": bits, "group_size": 64},
                           workload_profile={"name": "bytes_synthetic_2048_decode_512", "prompt_tokens": 2048,
                                             "output_tokens": 512, "repetitions": 1, "warmup_runs": 1})
                cfg["hardware_target"]["notes"] = "BYTES draft; requires C4 identity pins and R8 Mac checks before registration."
                cfg["run_metadata"] = {"project": "capstone-joulewise", "operator": "lead", "tags": [
                    "bytes-v1", "floor-calibration", "launch_lineage_required", "draft",
                    f"bytes-model={model_id}", "bytes-phase=decode", "bytes-null-contrast", f"rep{run['rep']}"]}
                raw = raw_json(cfg)
                filename = run["run_id"] + ".json"
                files[Path(directory) / filename] = raw
                entries.append({**run, "index": index, "config": filename, "config_sha256": sha(raw),
                                "model_tag": model_id + "-mlx", "workload": "bytes_synthetic_2048_decode_512"})
            files[Path(directory) / "order_manifest.json"] = raw_json({
                "schema_version": "joulewise.order_manifest.v1", "manifest_id": "bytes-" + model_id + "-" + Path(directory).name,
                "planned_n_bundles": len(entries), "executed_order": entries})
    files[PACK / "roster.json"] = raw_json({"status": "draft", "models": roster,
        "workload": {"prompt_tokens": 2048, "output_tokens": 512, "decode_forward_passes": 512,
                     "temperature": 0, "eos_suppressed": True, "warmup_tokens": 4, "settle_seconds": template["sampling"]["warmup_seconds"],
                     "phase_boundary_method": "first_token"},
        "source_run_config": TEMPLATE.as_posix(), "minimum_kept_units_per_stratum": 5})
    return files


def generate(output_root=ROOT, check=False):
    files = build_files()
    for relative, raw in files.items():
        target = Path(output_root) / relative
        if check:
            if target.read_bytes() != raw:
                raise ValueError(f"generated bytes drifted: {relative}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    generate(args.output_root, args.check)
    print(("verified" if args.check else "generated") + " 500 BYTES science configs (10 models x 50)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
