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
    qsa_ties = {"topk_calls": 0, "straddling_ties": 0}
    router_ties = {"topk_calls": 0, "rows": 0, "straddling_ties": 0}
    ids = torch.tensor(request["input_ids"], dtype=torch.long)
    unit = request["unit"]
    hidden = None if request.get("hidden") is None else torch.from_numpy(
        np.load(request["hidden"], allow_pickle=False)).to(dtype)

    def capture(name, value):
        traces[name] = value.detach().float().cpu().numpy().copy() if value.is_floating_point() else value.detach().cpu().numpy().copy()

    def observe_norm(norm, name, transform=lambda x: x):
        # Gate amendment A1: the exact tensor(s) the official norm consumed.
        def inputs(m, a):
            capture(name + ".input", transform(a[0]))
            if len(a) > 1:
                capture(name + ".gate", transform(a[1]))
        norm.register_forward_pre_hook(inputs)
        norm.register_forward_hook(lambda m, a, o: capture(name, transform(o)))

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
            observe_norm(module.hc_norm, "final.norm")
            out = module(hidden)
        else:
            layer_idx = int(unit)
            with torch.device("meta"):
                module = ref.Qwen4ExpTextDecoderLayer(config, layer_idx)
            module = load(module, checkpoint.prefix + f"layers.{layer_idx}.")
            for stem, hc in [("attn", module.attn_hyper_connection), ("mlp", module.mlp_hyper_connection)]:
                observe_norm(hc.hc_norm, stem + ".norm")
                def hyper_hook(m, a, o, s=stem):
                    capture(s+".mix", o[0]); capture(s+".residual", o[1]); capture(s+".inject", o[2])
                hc.register_forward_hook(hyper_hook)
            module.mlp_hyper_connection.register_forward_pre_hook(lambda m, a: capture("attn.streams", a[0]))
            attention = module.linear_attn if module.layer_type == "linear_attention" else module.self_attn
            attention.register_forward_hook(lambda m, a, o: capture("attention", o[0] if isinstance(o, tuple) else o))
            if module.layer_type == "linear_attention":
                observe_norm(attention.norm, "attention.gated_norm")
            else:
                observe_norm(attention.q_norm, "attention.q_norm")
                observe_norm(attention.k_norm, "attention.k_norm")
                deterministic_qsa_ties(attention.indexer, torch, qsa_ties)
                attention.indexer.register_forward_hook(lambda m, a, o: capture("qsa.mask", o == 0 if o.is_floating_point() else o))
            def router_hook(m, a, o):
                capture("router.logits", o[0]); capture("router.weights", o[1]); capture("router.experts", o[2])
            deterministic_router_ties(module.mlp.gate, torch, router_ties)
            module.mlp.gate.register_forward_hook(router_hook)
            module.mlp.register_forward_hook(lambda m, a, o: capture("moe", o))
            if module.ple is not None:
                module.ple.register_forward_hook(lambda m, a, o: capture("ple", o))
                module.ple.ple_embedding.register_forward_hook(lambda m, a, o: capture("ple.embedding", o))
                for stem in ["norm_key", "norm_query", "norm_conv"]:
                    observe_norm(getattr(module.ple, stem), "ple." + stem)
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
                    "qsa_topk": dict(qsa_ties, tie_rule="score descending, block ascending"),
                    "router_topk": dict(router_ties, tie_rule="fp32 probability descending, expert ascending"),
                    "reads": checkpoint.reads}


def deterministic_qsa_ties(indexer, torch, counts):
    """Fix the official QSA indexer's unspecified top-k tie order.

    Qwen4ExpTextQSAIndexer.forward selects blocks with ``scores.topk(k, dim=0)``.
    relu makes a block score exactly 0.0 whenever every indexer head's dot
    product is <= 0, so exact ties at the k-th score occur in practice, and
    torch.topk leaves the order of equal values unspecified. The official
    selected set is then not a function of the inputs, and an exact
    ``qsa.mask`` gate against it would compare with an arbitrary draw.
    Inside this indexer's forward only, topk returns the stable
    (score descending, block ascending) order: one of torch.topk's permitted
    outputs. It selects a different set than torch's own call only on an exact
    tie straddling the k-th score; scores are untouched, and the indexer's
    scatter makes the index order irrelevant. Same rule as the canonical port
    (D0, ``topk_mask_lowest_index``) and its validation reference ("REF").
    The MoE router has its own, identically scoped patch
    (``deterministic_router_ties``).
    """
    from unittest.mock import patch

    def topk(values, k, dim=-1, largest=True, sorted=True):
        if not largest or values.dim() != 1:
            raise RuntimeError("unexpected QSA indexer topk call")
        counts["topk_calls"] += 1
        order = torch.sort(-values, dim=0, stable=True).indices
        if k < values.shape[0] and bool(values[order[k - 1]] == values[order[k]]):
            counts["straddling_ties"] += 1
        index = order[:k]
        return torch.return_types.topk((values.gather(0, index), index))

    forward = indexer.forward

    def tie_ordered_forward(*args, **kwargs):
        with patch.object(torch.Tensor, "topk", topk):
            return forward(*args, **kwargs)
    # Instance attribute: nn.Module.__call__ still runs the registered hooks.
    indexer.forward = tie_ordered_forward


def deterministic_router_ties(router, torch, counts):
    """Fix the official MoE router's unspecified top-k tie order.

    Qwen4ExpTextTopKRouter.forward ranks fp32 softmax probabilities with
    ``torch.topk(router_probs, top_k, dim=-1)``. Equal bf16 logits give equal
    fp32 probabilities, and at the released scale (512 experts, top-10) exact
    ties straddling the k-th probability are common in bf16 (canonical.md
    deviation 7: 8 of 54 rows at layer 2). torch.topk leaves their order
    unspecified (on CPU it is not even reproducible), so the official expert
    set is not a function of the inputs there. Inside this router's forward
    only, topk returns the stable (probability descending, expert ascending)
    order: one of torch.topk's permitted outputs, differing from torch's own
    call only on an exact tie straddling the k-th value. Probabilities and the
    renormalised weights are untouched. This is the rule canonical.md
    (follow-up P4/P11) prescribes for the reference; the canonical port's
    ``argpartition`` on fp32 probabilities is unspecified on ties as well, and
    its GPU order is lowest-index in every straddling tie observed (gold run
    layers 1-2, and 14,531 synthetic 512-expert top-10 rows). router.experts
    stays an exact gate in fp32; in bf16 any other port choice must pass gate
    amendment A2 (admissible boundary swap plus a teacher-forced layer).
    """
    from unittest.mock import patch

    def topk(values, k, dim=-1, largest=True, sorted=True):
        if not largest or values.dim() != 2 or dim not in (-1, 1):
            raise RuntimeError("unexpected MoE router topk call")
        counts["topk_calls"] += 1
        counts["rows"] += values.shape[0]
        order = torch.sort(values, dim=-1, descending=True, stable=True).indices
        if k < values.shape[-1]:
            ranked = values.gather(-1, order[:, k - 1:k + 1])
            counts["straddling_ties"] += int((ranked[:, 0] == ranked[:, 1]).sum())
        index = order[:, :k]
        return torch.return_types.topk((values.gather(-1, index), index))

    forward = router.forward

    def tie_ordered_forward(*args, **kwargs):
        with patch.object(torch, "topk", topk):
            return forward(*args, **kwargs)
    # Instance attribute: nn.Module.__call__ still runs the registered hooks.
    router.forward = tie_ordered_forward


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
