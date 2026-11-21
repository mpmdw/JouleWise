#!/usr/bin/env python3
"""Generate and replay the audit 4 width-one PLE fixture offline."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


def load_python(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def prepare(root, checkout, **text_overrides):
    import numpy as np
    from safetensors.torch import save_file
    import torch
    import transformers

    if transformers.__version__ != "5.22.1":
        raise ValueError("expected transformers 5.22.1")
    prior = load_python(checkout / "scripts/audit_mlxvlm/ref_gen.py", "ple_prior")
    gold = load_python(checkout / "tests/align/test_qwen4_exp_canonical.py", "ple_gold")
    torch.set_num_threads(2)
    config = prior.config_a()
    config.update(ple_conv_kernel_size=1, rms_norm_eps=1e-6, tie_word_embeddings=False,
                  norm_topk_prob=True, layer_types=["linear_attention", "full_attention"])
    config.update(text_overrides)
    ids = prior.ids_for("A")
    model = prior.build_model(config, 1105)
    gold.randomize(model, torch, 1105)
    with torch.inference_mode():
        logits = model(torch.tensor([ids]), use_cache=False).logits.numpy()
    np.save(root / "hf.npy", logits)

    weights = {}
    for key, value in model.state_dict().items():
        if key.startswith("model."):
            key = "model.language_model." + key.removeprefix("model.")
        if key.endswith(".ngram_embedding.weight"):
            for i, shard in enumerate(value.chunk(config["split_ngram_parts"], dim=0)):
                weights[f"{key.removesuffix('.weight')}.shard_{i}.weight"] = shard.contiguous()
        else:
            weights[key] = value.contiguous()
    payload = root / "model.safetensors"
    save_file(weights, str(payload))
    (root / "config.json").write_text(json.dumps({"model_type": "qwen4_exp",
                                                "text_config": config, "ids": ids}))
    print(json.dumps({"hf_token": int(logits[0, -1].argmax()),
                      "weights_sha256": sha256(payload.read_bytes()).hexdigest()}))


def measure(model, tokens, gold):
    import mlx.core as mx
    from mlx_lm import stream_generate
    import numpy as np
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from transformers import PreTrainedTokenizerFast

    ids = mx.array([tokens])
    cache = model.make_cache()
    mx.eval(model(ids[:, :-1], cache=cache))
    cached = np.asarray(model(ids[:, -1:], cache=cache))
    vocab = {"<unk>": 0, "<bos>": 1, "<eos>": 2}
    vocab.update({str(i): i for i in range(3, gold.shape[-1])})
    tokenizer = PreTrainedTokenizerFast(tokenizer_object=Tokenizer(WordLevel(vocab, unk_token="<unk>")),
                                        bos_token="<bos>", eos_token="<eos>", unk_token="<unk>")
    [response] = list(stream_generate(model, tokenizer, tokens, max_tokens=1))
    full_error = float(np.abs(np.asarray(model(ids)) - gold).max())
    cached_error = float(np.abs(cached[0, -1] - gold[0, -1]).max())
    gold_token = int(gold[0, -1].argmax())
    return {"full_max_abs": full_error, "cached_shape": cached.shape,
            "cached_last_max_abs": cached_error, "stream_token": response.token, "hf_token": gold_token}


def expect_pinned_refusal(root, config, weights, field):
    from mlx_lm.utils import load_model
    from qwen4_pinned_quantization_probe import vendored_checkpoint

    with vendored_checkpoint(root, config, weights) as checkpoint:
        try:
            load_model(checkpoint)
        except ValueError as error:
            if type(error).__name__ != "UnsupportedByPinnedRuntime" or field not in str(error):
                raise
            print(json.dumps({"implementation": "pinned", "refusal": str(error)}))
            return
    raise AssertionError(f"pinned loader accepted unsupported {field}")


def replay(root, pinned):
    from mlx_lm.utils import load_model
    import numpy as np

    config = json.loads((root / "config.json").read_text())
    if pinned:
        expect_pinned_refusal(root, config, root / "model.safetensors", "ple_layer_ids")
        return
    model, _ = load_model(root)
    result = measure(model, config["ids"], np.load(root / "hf.npy"))
    print(json.dumps({"implementation": "upstream", **result}))
    if not result["full_max_abs"] < 1e-4:
        raise AssertionError("FP32 full prefill exceeds tolerance")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="step", required=True)
    for step in ("prepare", "upstream", "pinned"):
        command = sub.add_parser(step)
        command.add_argument("fixture", type=Path)
        if step == "prepare":
            command.add_argument("--gold-checkout", type=Path, required=True)
    args = parser.parse_args()
    if args.step == "prepare":
        prepare(args.fixture, args.gold_checkout)
    else:
        replay(args.fixture, pinned=args.step == "pinned")


if __name__ == "__main__":
    main()
