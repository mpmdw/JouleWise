"""Official transformers 5.22.1 worker. CPU only; never loads the whole model."""
from __future__ import annotations

import inspect
from pathlib import Path

from .core import REFERENCE_VERSION, sha256


def run_reference(request, checkpoint):
    import numpy as np
    import torch
    import transformers
    from transformers.models.qwen4_exp import modeling_qwen4_exp as ref
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig

    if transformers.__version__ != REFERENCE_VERSION:
        raise RuntimeError(f"reference requires transformers {REFERENCE_VERSION}, got {transformers.__version__}")
    torch.set_num_threads(2)
    torch.set_num_interop_threads(2)
    dtype = torch.float32 if request["dtype"] == "fp32" else torch.bfloat16
    config = Qwen4ExpTextConfig(**checkpoint.text)
    config._attn_implementation = "eager"
    traces = {}
    ids = torch.tensor(request["input_ids"], dtype=torch.long)
    unit = request["unit"]
    hidden = None if request.get("hidden") is None else torch.from_numpy(
        np.load(request["hidden"], allow_pickle=False)).to(dtype)

    def capture(name, value):
        traces[name] = value.detach().float().cpu().numpy().copy() if value.is_floating_point() else value.detach().cpu().numpy().copy()

    class ExpertSlice:
        # Only the storage changes: Qwen4ExpTextExperts.forward remains official.
        def __init__(self, name):
            self.name = name
        def __getitem__(self, index):
            index = int(index)
            return checkpoint.read(self.name, (index, slice(None), slice(None)), "torch", request["dtype"])

    class RowEmbedding(torch.nn.Module):
        def __init__(self, base):
            super().__init__()
            self.base = base
            # Official ngram forward queries only weight.device, never its data.
            self.register_buffer("weight", torch.empty(0, dtype=dtype), persistent=False)
        def forward(self, indices):
            capture("ple.ngram_ids", indices)
            return checkpoint.ngram_rows(self.base, indices.numpy(), "torch", request["dtype"])

    def load(module, prefix):
        for name, parameter in list(module.named_parameters()):
            owner_path, _, leaf = name.rpartition(".")
            owner = module.get_submodule(owner_path) if owner_path else module
            full = prefix + name
            if "ngram_embedding.weight" in name:
                continue
            shape, _ = checkpoint.info(full)
            if tuple(parameter.shape) != shape:
                raise ValueError(f"shape mismatch {full}: {parameter.shape} vs {shape}")
            if ".experts." in full:
                del owner._parameters[leaf]
                setattr(owner, leaf, ExpertSlice(full))
            else:
                setattr(owner, leaf, torch.nn.Parameter(checkpoint.read(full, framework="torch", dtype=request["dtype"]), requires_grad=False))
        # These persistent I64 buffers are checkpoint state, not interchangeable
        # with config-derived defaults. Missing buffers fail closed.
        for name, buffer in list(module.named_buffers()):
            full = prefix + name
            shape, storage = checkpoint.info(full)
            if tuple(buffer.shape) != shape or storage != "I64":
                raise ValueError(f"persistent buffer shape/dtype mismatch: {full}")
            owner_path, _, leaf = name.rpartition(".")
            owner = module.get_submodule(owner_path) if owner_path else module
            setattr(owner, leaf, checkpoint.read(full, framework="torch", dtype="native"))
        for name, child in module.named_modules():
            if isinstance(child, ref.Qwen4ExpTextNGramEmbedding):
                child.ngram_embedding = RowEmbedding(prefix + name + ".ngram_embedding")
        # Every remaining tensor must be real, never an uninitialized meta value.
        if any(p.is_meta for p in module.parameters()) or any(b.is_meta for b in module.buffers()):
            raise RuntimeError("unmaterialized reference tensor")
        return module.eval()

    with torch.inference_mode():
        if unit == "embed":
            out = checkpoint.rows(checkpoint.prefix + "embed_tokens.weight", ids.numpy(), "torch", request["dtype"])
            capture("embedding", out)
            out = out.repeat(1, 1, config.hc_count)
        elif unit == "head":
            name = "lm_head.weight"
            if name not in checkpoint.weight_map and config.tie_word_embeddings:
                name = checkpoint.prefix + "embed_tokens.weight"
            rows, width = checkpoint.info(name)[0]
            if width != hidden.shape[-1]:
                raise ValueError("head hidden width mismatch")
            chunks = []
            for start in range(0, rows, 1024):
                weights = checkpoint.read(name, (slice(start, min(rows, start+1024)), slice(None)), "torch", request["dtype"])
                chunks.append(torch.nn.functional.linear(hidden, weights))
            out = torch.cat(chunks, dim=-1)
        elif unit == "final":
            with torch.device("meta"):
                module = ref.Qwen4ExpTextGatedResidual(config, use_combine=False)
            module = load(module, checkpoint.prefix + "hyper_connection_mixer.")
            module.hc_norm.register_forward_hook(lambda m, a, o: capture("final.norm", o))
            out = module(hidden)
        else:
            layer_idx = int(unit)
            with torch.device("meta"):
                module = ref.Qwen4ExpTextDecoderLayer(config, layer_idx)
            module = load(module, checkpoint.prefix + f"layers.{layer_idx}.")
            for stem, hc in [("attn", module.attn_hyper_connection), ("mlp", module.mlp_hyper_connection)]:
                hc.hc_norm.register_forward_hook(lambda m, a, o, s=stem: capture(s + ".norm", o))
                def hyper_hook(m, a, o, s=stem):
                    capture(s+".mix", o[0]); capture(s+".residual", o[1]); capture(s+".inject", o[2])
                hc.register_forward_hook(hyper_hook)
            module.mlp_hyper_connection.register_forward_pre_hook(lambda m, a: capture("attn.streams", a[0]))
            attention = module.linear_attn if module.layer_type == "linear_attention" else module.self_attn
            attention.register_forward_hook(lambda m, a, o: capture("attention", o[0] if isinstance(o, tuple) else o))
            if module.layer_type == "linear_attention":
                attention.norm.register_forward_hook(lambda m, a, o: capture("attention.gated_norm", o))
            else:
                attention.q_norm.register_forward_hook(lambda m, a, o: capture("attention.q_norm", o))
                attention.k_norm.register_forward_hook(lambda m, a, o: capture("attention.k_norm", o))
                attention.indexer.register_forward_hook(lambda m, a, o: capture("qsa.mask", o == 0 if o.is_floating_point() else o))
            def router_hook(m, a, o):
                capture("router.logits", o[0]); capture("router.weights", o[1]); capture("router.experts", o[2])
            module.mlp.gate.register_forward_hook(router_hook)
            module.mlp.register_forward_hook(lambda m, a, o: capture("moe", o))
            if module.ple is not None:
                module.ple.register_forward_hook(lambda m, a, o: capture("ple", o))
                module.ple.ple_embedding.register_forward_hook(lambda m, a, o: capture("ple.embedding", o))
                for stem in ["norm_key", "norm_query", "norm_conv"]:
                    getattr(module.ple, stem).register_forward_hook(lambda m, a, o, s=stem: capture("ple."+s, o))
            positions = torch.arange(ids.shape[1]).view(1, 1, -1).expand(3, ids.shape[0], -1)
            rotary = ref.Qwen4ExpTextRotaryEmbedding(config)
            position_embeddings = rotary(hidden, positions)
            # Same no-padding eager additive causal mask as TextModel.forward.
            length = ids.shape[1]
            causal = torch.full((length, length), torch.finfo(dtype).min, dtype=dtype).triu(1)
            causal = causal[None, None].expand(ids.shape[0], 1, -1, -1)
            out = module(hidden, position_embeddings=position_embeddings, attention_mask=causal,
                         conv_mask=None, past_key_values=None, ple_input_ids=ids)
            capture("mlp.streams", out)
        capture("output", out)
    return traces, {"transformers": transformers.__version__, "torch": torch.__version__,
                    "reference_source_sha256": sha256(inspect.getfile(ref)),
                    "device": "cpu", "experts": "official forward with sliced storage",
                    "reads": checkpoint.reads}


def make_tiny(root):
    """Real HF save_pretrained checkpoint, including both layer types and PLE."""
    import torch
    from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig
    from transformers.models.qwen4_exp.modeling_qwen4_exp import Qwen4ExpForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(20261105)
    config = Qwen4ExpTextConfig(
        vocab_size=128, hidden_size=32, num_hidden_layers=4,
        layer_types=["linear_attention", "linear_attention", "linear_attention", "full_attention"],
        num_attention_heads=4, num_key_value_heads=2, head_dim=8,
        linear_key_head_dim=8, linear_value_head_dim=8, linear_num_key_heads=2, linear_num_value_heads=4,
        hc_count=2, hc_lowrank=8, num_experts=4, num_experts_per_tok=2,
        moe_intermediate_size=16, shared_expert_intermediate_size=16,
        ple_layer_ids=[2], ple_embed_dim=32, ngram_vocab_size_base=31,
        heads_per_ngram=2, split_ngram_parts=4, make_ngram_vocab_size_divisible_by=4,
        indexer_n_heads=2, indexer_kv_heads=1, indexer_head_dim=8,
        indexer_budget=4, indexer_compress_ratio=2, eos_token_id=0,
        rope_parameters={"rope_type": "default", "rope_theta": 10000.0,
                         "partial_rotary_factor": 1.0, "mrope_section": [1, 1, 2]},
    )
    model = Qwen4ExpForCausalLM(config).eval().to(torch.bfloat16)
    model.save_pretrained(root, max_shard_size="32KB")
    return {"checkpoint": str(root), "parameters": sum(p.numel() for p in model.parameters())}
