#!/usr/bin/env python3
"""Replay the audit 5 FP32 mlx-vlm export with PLE disabled."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType
from zipfile import ZipFile

from qwen4_ple_cache_probe import expect_pinned_refusal, measure, prepare

WHEEL_SHA = "0412a883ed5f0ee2fe65e6c050819ae586ac76f1811f94a373b6293e92568e37"


def export(root, wheel):
    import mlx.core as mx
    from mlx.utils import tree_flatten
    import numpy as np

    if sha256(wheel.read_bytes()).hexdigest() != WHEEL_SHA:
        raise ValueError("expected the released mlx-vlm 0.7.12 wheel")
    package = root / "wheel"
    with ZipFile(wheel) as archive:
        archive.extractall(package)
    # Load the wheel's model code without its optional processors and server.
    for name in ("mlx_vlm", "mlx_vlm.models", "mlx_vlm.speculative",
                 "mlx_vlm.models.qwen4_exp", "mlx_vlm.models.qwen3_5",
                 "mlx_vlm.models.qwen3_5_moe", "mlx_vlm.models.qwen3_vl",
                 "mlx_vlm.models.qwen3_vl_moe"):
        namespace = ModuleType(name)
        namespace.__path__ = [str(package.joinpath(*name.split(".")))]
        sys.modules[name] = namespace
        if "." in name:
            parent, attr = name.rsplit(".", 1)
            setattr(sys.modules[parent], attr, namespace)

    from mlx_vlm.models.qwen3_vl.vision import VisionModel
    sys.modules["mlx_vlm.models.qwen3_vl"].VisionModel = VisionModel
    from mlx_vlm.models.qwen3_vl.qwen3_vl import Model as Qwen3VLModel
    sys.modules["mlx_vlm.models.qwen3_vl"].Model = Qwen3VLModel
    from mlx_vlm.models.qwen3_5.qwen3_5 import Model as Qwen35Model
    sys.modules["mlx_vlm.models.qwen3_5"].Model = Qwen35Model
    from mlx_vlm.models.qwen4_exp.config import ModelConfig
    from mlx_vlm.models.qwen4_exp.qwen4_exp import Model

    hf = root / "hf"
    config = json.loads((hf / "config.json").read_text())
    config["text_config"].update(model_type="qwen4_exp_text", max_position_embeddings=32768)
    config["vision_config"] = dict(depth=1, hidden_size=32, intermediate_size=64, num_heads=2,
                                   patch_size=4, spatial_merge_size=2, temporal_patch_size=2,
                                   out_hidden_size=64, num_position_embeddings=16, deepstack_visual_indexes=[])
    config.update(image_token_id=60, video_token_id=61, vision_start_token_id=58, vision_end_token_id=59)
    full = Model(ModelConfig.from_dict(config))
    weights = full.sanitize(mx.load(str(hf / "model.safetensors")))
    lm = full.language_model
    lm.load_weights([(k.removeprefix("language_model."), v) for k, v in weights.items()], strict=True)
    lm.eval()
    logits = np.asarray(lm(mx.array([config["ids"]]), cache=lm.make_cache()).logits)
    gold = np.load(hf / "hf.npy")
    error = float(np.abs(gold - logits).max())
    if not error < 1e-4:
        raise AssertionError(f"mlx-vlm full prefill differs from Transformers: {error}")
    vlm = root / "vlm"
    vlm.mkdir()
    weights = {f"language_model.{k}": v for k, v in tree_flatten(lm.parameters())}
    payload = vlm / "model.safetensors"
    mx.save_safetensors(str(payload), weights)
    (vlm / "config.json").write_text(json.dumps(config))
    print(json.dumps({"mlx_vlm_full_max_abs": error, "mlx_vlm_token": int(logits[0, -1].argmax()),
                      "weights_sha256": sha256(payload.read_bytes()).hexdigest()}))


def replay(root, stage):
    from mlx_lm.utils import load_model
    import numpy as np

    vlm = root / "vlm"
    config = json.loads((vlm / "config.json").read_text())
    if stage == "pinned":
        expect_pinned_refusal(root, config, vlm / "model.safetensors", "ple_layer_ids")
        return
    override = {} if stage == "upstream" else {"qwen4_norm_layout": "zero_centered"}
    model, _ = load_model(vlm, model_config=override)
    result = measure(model, config["ids"], np.load(root / "hf" / "hf.npy"))
    print(json.dumps({"implementation": stage, **result}))
    matched = (result["cached_last_max_abs"] < 1e-4 and result["full_max_abs"] < 1e-4
               and result["stream_token"] == result["hf_token"])
    if matched != (stage == "upstream-fixed"):
        raise AssertionError(f"unexpected logits or stream token for {stage}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="stage", required=True)
    for stage in ("prepare", "export", "upstream", "upstream-fixed", "pinned"):
        cmd = commands.add_parser(stage)
        cmd.add_argument("root", type=Path)
        if stage == "prepare":
            cmd.add_argument("--gold-checkout", required=True, type=Path)
        if stage == "export":
            cmd.add_argument("--wheel", required=True, type=Path)
    args = parser.parse_args()
    if args.stage == "prepare":
        hf = args.root / "hf"
        hf.mkdir()
        prepare(hf, args.gold_checkout, ple_layer_ids=[], ple_conv_kernel_size=2)
    elif args.stage == "export":
        export(args.root, args.wheel)
    else:
        replay(args.root, args.stage)
