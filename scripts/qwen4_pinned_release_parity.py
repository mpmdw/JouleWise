#!/usr/bin/env python3
"""Replay the released-structure B/C gold fixtures through pinned mlx-lm."""
import argparse
from contextlib import ExitStack, contextmanager
import json
from pathlib import Path
from unittest.mock import patch

from qwen4_ple_cache_probe import RELEASE_CONFIG, load_python


@contextmanager
def dense_traces(harness):
    # A short prompt leaves the released 2048-token budget unfilled. MLX
    # uses an implicit causal mask and returns no materialized indexer mask.
    components = harness.components
    with patch.object(harness, "components", lambda m: ((k, v) for k, v in components(m)
                                                       if not k.endswith(".indexer"))):
        yield


def prepare_reference(fixtures, harness, gold):
    import torch

    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    release = json.loads(RELEASE_CONFIG.read_text())
    original_loader = harness.load_python

    def resized_loader(path, name):
        module = original_loader(path, name)
        if name == "parity_prior":
            for field in ("config_b", "config_c"):
                original = getattr(module, field)()
                sizes = {key: original[key] for key in (
                    "hidden_size", "hc_lowrank", "moe_intermediate_size", "shared_expert_intermediate_size",
                    "num_attention_heads", "num_key_value_heads", "head_dim", "linear_num_key_heads",
                    "linear_num_value_heads", "linear_key_head_dim", "linear_value_head_dim",
                    "indexer_n_heads", "indexer_head_dim", "num_hidden_layers", "num_experts",
                    "num_experts_per_tok", "vocab_size", "ple_embed_dim", "heads_per_ngram", "ngram_vocab_size_base",
                )}
                sizes["ngram_vocab_size_base"] = 37
                resized = dict(release["text_config"], **sizes)
                resized["layer_types"] = resized["layer_types"][:resized["num_hidden_layers"]]
                setattr(module, field, lambda config=resized: dict(config))
        return module

    with patch.object(harness, "load_python", resized_loader), dense_traces(harness):
        for case in ("B", "C"):
            for dtype in ("fp32", "bf16"):
                root = fixtures / f"{case}-{dtype}"
                root.mkdir(parents=True, exist_ok=True)
                harness.reference(root, gold, case, dtype)
                path = root / "config.json"
                config = json.loads(path.read_text())
                config["text_config"].pop("norm_topk_prob")  # Transformers defaults to true.
                runtime = dict(release, **config)
                harness.write_json(path, runtime)


def capture_comparators(fixtures, harness, gold):
    with dense_traces(harness):
        for case in ("B", "C"):
            for dtype in ("fp32", "bf16"):
                for which in ("upstream", "port"):
                    harness.mlx(fixtures / f"{case}-{dtype}", gold, dtype, which)


def replay(fixtures, harness, scratch):
    import mlx.core as mx
    from mlx_lm.utils import load_model
    import numpy as np

    from qwen4_pinned_quantization_probe import released_fixture_config, vendored_checkpoint

    sources = ("hf", "upstream", "port")
    pairs = (*harness.PAIRS, ("hf", "pinned"), ("upstream", "pinned"), ("port", "pinned"))
    result = {}
    for case in ("B", "C"):
        with np.load(fixtures / f"{case}-fp32" / "hf.npz") as hf32:
            for dtype in ("fp32", "bf16"):
                directory = fixtures / f"{case}-{dtype}"
                config = json.loads((directory / "config.json").read_text())
                checkpoint_config = released_fixture_config(config, "zero_centered")
                with vendored_checkpoint(scratch, checkpoint_config, directory / "hf.safetensors") as checkpoint:
                    model, _ = load_model(checkpoint)
                with dense_traces(harness):
                    observed = harness.capture_mlx(model, model.model, mx.array([config["ids"]]), port=False)
                with ExitStack() as stack:
                    traces = {name: stack.enter_context(np.load(directory / f"{name}.npz")) for name in sources}
                    if any(observed.keys() != set(trace.files) for trace in traces.values()):
                        raise AssertionError(f"{directory.name}: component inventory differs")
                    traces["pinned"] = observed
                    rows = {}
                    for key in observed:
                        exact = key.endswith((".indexer", ".router")) or key == "greedy"
                        noise = np.max(np.abs(traces["hf"][key] - hf32[key])) if not exact and dtype == "bf16" else 0
                        atol = 0.0 if exact else float(max(1e-4, 1.5 * noise))
                        rows[key] = {f"{a}/{b}": harness.metrics(traces[a][key], traces[b][key], atol) for a, b in pairs}
                    for key, row in rows.items():
                        if dtype == "fp32" and any(not row[pair]["pass"] for pair in
                                                    ("hf/pinned", "upstream/pinned", "hf/upstream")):
                            raise AssertionError(f"{directory.name}/{key}: FP32 parity regression")
                        if (not row["upstream/pinned"]["pass"]
                            or (row["hf/upstream"]["pass"] and not row["hf/pinned"]["pass"])
                            or (row["upstream/port"]["pass"] and not row["port/pinned"]["pass"])):
                            raise AssertionError(f"{directory.name}/{key}: pinned adapter parity regression")
                    result[directory.name] = rows
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixtures", type=Path)
    parser.add_argument("--harness", type=Path, required=True, help="Path to the merged parity harness script")
    parser.add_argument("--stage", choices=("reference", "comparators", "pinned"), default="pinned")
    parser.add_argument("--gold-checkout", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    harness = load_python(args.harness, "qwen4_parity")
    if args.stage == "pinned":
        if args.output is None:
            parser.error("pinned replay requires --output")
        harness.write_json(args.output, replay(args.fixtures, harness, args.output.parent))
    else:
        if args.gold_checkout is None:
            parser.error("reference and comparator stages require --gold-checkout")
        if args.stage == "reference":
            prepare_reference(args.fixtures, harness, args.gold_checkout)
        else:
            capture_comparators(args.fixtures, harness, args.gold_checkout)
