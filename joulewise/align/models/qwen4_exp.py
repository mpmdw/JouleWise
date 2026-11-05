"""JouleWise text-only Qwen3.8-Flash-Next for mlx 0.31.2 / mlx-lm 0.31.3.

Authority: official transformers modeling_qwen4_exp.py. Vision and speculative
MTP are intentionally absent. Norm weights retain the official zero-centered
representation; there is no heuristic or irreversible `1 +` conversion.
"""
from dataclasses import dataclass, field, fields
import importlib.util
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn
from mlx_lm.models.base import BaseModelArgs
from mlx_lm.models import cache as cache_api
from mlx_lm.models.cache import ArraysCache, KVCache
from mlx_lm.models.gated_delta import gated_delta_update
from mlx_lm.models.switch_layers import SwitchGLU

# A sibling file, shipped and hashed with this module, also works with the
# pinned loader's spec_from_file_location("custom_model", ...) entry point.
_spec = importlib.util.spec_from_file_location(
    "jw_qwen4_tables", Path(__file__).with_name("qwen4_exp_tables.py"))
tables = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tables)


@dataclass
class ModelArgs(BaseModelArgs):
    model_type: str = "qwen4_exp"
    vocab_size: int = 248320
    hidden_size: int = 2560
    num_hidden_layers: int = 48
    num_attention_heads: int = 24
    num_key_value_heads: int = 2
    head_dim: int = 256
    hc_count: int = 4
    hc_lowrank: int = 320
    linear_conv_kernel_dim: int = 4
    linear_key_head_dim: int = 128
    linear_value_head_dim: int = 128
    linear_num_key_heads: int = 16
    linear_num_value_heads: int = 48
    num_experts: int = 512
    num_experts_per_tok: int = 10
    moe_intermediate_size: int = 640
    shared_expert_intermediate_size: int = 640
    norm_topk_prob: bool = True
    hidden_act: str = "silu"
    output_gate_type: str = "sigmoid"
    rms_norm_eps: float = 1e-6
    attention_bias: bool = False
    tie_word_embeddings: bool = False
    full_attention_interval: int = 4
    layer_types: list = field(default_factory=list)
    rope_parameters: dict = field(default_factory=lambda: dict(
        rope_type="default", rope_theta=10000000, partial_rotary_factor=0.25))
    indexer_n_heads: int = 4
    indexer_kv_heads: int = 1
    indexer_head_dim: int = 128
    indexer_budget: int = 2048
    indexer_compress_ratio: int = 4
    ple_layer_ids: list = field(default_factory=lambda: [2])
    ple_embed_dim: int = 2560
    ple_conv_kernel_size: int = 4
    ngram_size: int = 3
    heads_per_ngram: int = 8
    ngram_vocab_size_base: int = 20000000
    make_ngram_vocab_size_divisible_by: int = 128
    split_ngram_parts: int = 128
    seed: int = 1234
    eos_token_id: object = 248044
    ple_tables: dict = field(default_factory=dict)
    jw_format: str = "hf-zero-centered-v1"

    @classmethod
    def from_dict(cls, config):
        c = tables.text_config(config)
        for k in ("ple_tables", "jw_format"):
            if k in config:
                c[k] = config[k]
        return cls(**{f.name: c[f.name] for f in fields(cls) if f.name in c})

    def __post_init__(self):
        if not self.layer_types:
            self.layer_types = ["indexed_attention" if (i + 1) % self.full_attention_interval == 0
                                else "linear_attention" for i in range(self.num_hidden_layers)]
        self.layer_types = ["indexed_attention" if t == "full_attention" else t for t in self.layer_types]
        if len(self.layer_types) != self.num_hidden_layers or set(self.layer_types) - {
                "linear_attention", "indexed_attention"}:
            raise ValueError("Invalid layer_types")
        if self.hidden_act != "silu" or self.output_gate_type not in (None, "silu", "sigmoid"):
            raise ValueError("Only official silu MLP / silu or sigmoid output gates supported")
        if self.rope_parameters.get("rope_type", "default") != "default":
            raise ValueError("Only official default text RoPE supported")
        rd = int(self.head_dim * self.rope_parameters.get("partial_rotary_factor", 1))
        if rd <= 0 or rd % 2 or rd > self.indexer_head_dim:
            raise ValueError("Invalid partial rotary dimension")
        if self.indexer_kv_heads != 1 or self.indexer_budget < self.indexer_compress_ratio or (
                self.indexer_budget % self.indexer_compress_ratio):
            raise ValueError("QSA requires one key head and a whole-block budget")
        if not 0 < self.num_experts_per_tok <= self.num_experts or self.hc_count <= 1:
            raise ValueError("Invalid router / hyper-connection configuration")
        if self.num_attention_heads % self.num_key_value_heads or (
                self.linear_num_value_heads % self.linear_num_key_heads):
            raise ValueError("Head counts must be divisible")
        for layer in self.ple_layer_ids:
            if not 1 <= layer <= self.num_hidden_layers or self.layer_types[layer - 1] != "linear_attention":
                raise ValueError("PLE requires a one-indexed linear-attention layer")
        if self.ple_layer_ids and (self.ngram_size <= 1 or self.ple_embed_dim % (
                (self.ngram_size - 1) * self.heads_per_ngram) or self.eos_token_id is None):
            raise ValueError("Invalid PLE configuration")
        if self.jw_format != "hf-zero-centered-v1":
            raise ValueError("Unsupported norm representation")


class Qwen4ExpRecurrentCache(ArraysCache):
    """conv, fp32 DeltaNet state [B,Hv,Dv,Dk], PLE conv, token history.

    Recurrent state cannot be cropped. Prefix rewrites rebuild or restore a
    snapshot; claiming trimmability here corrupts hybrid prompt-cache reuse.
    """
    def __init__(self):
        super().__init__(4)
        self.offset = 0

    @property
    def meta_state(self):
        return (str(self.offset),)

    @meta_state.setter
    def meta_state(self, value):
        self.offset = int(value[0])

    def size(self):
        return self.offset

    def advance(self, n):
        self.offset += n

    @classmethod
    def merge(cls, caches):
        raise ValueError("Use explicit left-padded batches; BatchGenerator merge is not supported")


class Qwen4ExpAttentionCache(KVCache):
    """Native KVCache plus raw QSA keys and token validity, trimmed together."""
    def __init__(self):
        super().__init__()
        self.raw_keys = self.valid = None

    @property
    def state(self):
        return (*super().state, self.raw_keys, self.valid)

    @state.setter
    def state(self, value):
        KVCache.state.fset(self, value[:2])
        self.raw_keys, self.valid = value[2:]

    def trim(self, n):
        n = super().trim(n)
        if self.raw_keys is not None:
            self.raw_keys = self.raw_keys[:, :self.offset]
            self.valid = self.valid[:, :self.offset]
        return n

    def to_quantized(self, *args, **kwargs):
        raise ValueError("QSA cache quantization is unsupported: refusing to lose indexer state")

    @classmethod
    def merge(cls, caches):
        raise ValueError("Use explicit left-padded batches; BatchGenerator merge is not supported")

    @property
    def nbytes(self):
        return super().nbytes + (0 if self.raw_keys is None else self.raw_keys.nbytes + self.valid.nbytes)


# mlx-lm 0.31.3's native deserializer resolves cache classes in its own globals.
cache_api.Qwen4ExpRecurrentCache = Qwen4ExpRecurrentCache
cache_api.Qwen4ExpAttentionCache = Qwen4ExpAttentionCache


class RMSNorm(nn.Module):
    def __init__(self, dim, eps, group_size=None):
        super().__init__()
        self.weight = mx.zeros((dim,))
        self.eps, self.group_size = eps, group_size

    def __call__(self, x):
        y = x.astype(mx.float32)
        if self.group_size:
            y = y.reshape(*x.shape[:-1], -1, self.group_size)
        y = y * mx.rsqrt(mx.mean(y * y, axis=-1, keepdims=True) + self.eps)
        y = y.reshape(x.shape) * (1 + self.weight.astype(mx.float32))
        return y.astype(x.dtype)


def rope(x, positions, args):
    dim = int(args.head_dim * args.rope_parameters.get("partial_rotary_factor", 1))
    inv = args.rope_parameters.get("rope_theta", 10000000) ** (-mx.arange(0, dim, 2) / dim)
    angles = positions[..., None].astype(mx.float32) * inv
    cos = mx.concatenate([mx.cos(angles)] * 2, axis=-1).astype(x.dtype)
    sin = mx.concatenate([mx.sin(angles)] * 2, axis=-1).astype(x.dtype)
    while cos.ndim < x.ndim:
        cos, sin = mx.expand_dims(cos, -2), mx.expand_dims(sin, -2)
    a, b = x[..., :dim // 2], x[..., dim // 2:dim]
    rotated = x[..., :dim] * cos + mx.concatenate([-b, a], axis=-1) * sin
    return mx.concatenate([rotated, x[..., dim:]], axis=-1)


class HyperConnection(nn.Module):
    def __init__(self, a, combine=True):
        super().__init__()
        self.h, self.d = a.hc_count, a.hidden_size
        self.hc_norm = RMSNorm(self.h * self.d, a.rms_norm_eps, self.d)
        self.input_mix_weight_down = nn.Linear(self.h * self.d, a.hc_lowrank, bias=False)
        self.input_mix_weight_up = nn.Linear(a.hc_lowrank, self.h * self.d, bias=False)
        self.block_inject_weight = nn.Linear(self.h * self.d, self.h, bias=False) if combine else None

    def __call__(self, x):
        n = self.hc_norm(x)
        weights = mx.sigmoid(self.input_mix_weight_up(nn.silu(self.input_mix_weight_down(n) / self.h)))
        mixed = (weights * n).reshape(*x.shape[:-1], self.h, self.d).mean(axis=-2)
        return mixed if self.block_inject_weight is None else (
            mixed, 2 * mx.sigmoid(self.block_inject_weight(n) / self.h))


def short_conv(conv, x, previous, dilation=1):
    history = (conv.weight.shape[1] - 1) * dilation
    if previous is None:
        previous = mx.zeros((x.shape[0], history, x.shape[-1]), dtype=x.dtype)
    full = mx.concatenate([previous, x], axis=1)
    return nn.silu(conv(full)), mx.contiguous(full[:, -history:]) if history else full[:, :0]


class GatedNorm(nn.Module):
    def __init__(self, a):
        super().__init__()
        self.weight = mx.ones((a.linear_value_head_dim,))
        self.eps = a.rms_norm_eps
        self.activation = a.output_gate_type or a.hidden_act

    def __call__(self, x, gate):
        y = x.astype(mx.float32)
        y = (y * mx.rsqrt(mx.mean(y * y, axis=-1, keepdims=True) + self.eps)).astype(x.dtype)
        y = self.weight * y
        g = gate.astype(mx.float32)
        return (y * (mx.sigmoid(g) if self.activation == "sigmoid" else nn.silu(g))).astype(x.dtype)


class GatedDeltaNet(nn.Module):
    def __init__(self, a):
        super().__init__()
        self._args = a
        kd, vd = a.linear_num_key_heads * a.linear_key_head_dim, a.linear_num_value_heads * a.linear_value_head_dim
        self.in_proj_qkv = nn.Linear(a.hidden_size, kd * 2 + vd, bias=False)
        self.in_proj_z = nn.Linear(a.hidden_size, vd, bias=False)
        self.in_proj_a = nn.Linear(a.hidden_size, a.linear_num_value_heads, bias=False)
        self.in_proj_b = nn.Linear(a.hidden_size, a.linear_num_value_heads, bias=False)
        self.conv1d = nn.Conv1d(kd * 2 + vd, kd * 2 + vd, a.linear_conv_kernel_dim, groups=kd * 2 + vd, bias=False)
        self.A_log = mx.zeros((a.linear_num_value_heads,))
        self.dt_bias = mx.ones((a.linear_num_value_heads,))
        self.norm = GatedNorm(a)
        self.out_proj = nn.Linear(vd, a.hidden_size, bias=False)

    def __call__(self, x, mask, cache):
        a = self._args
        b, s, _ = x.shape
        x = mx.where(mask[..., None], x, 0)
        mixed, conv_state = short_conv(self.conv1d, self.in_proj_qkv(x), cache[0] if cache else None)
        if cache is not None:
            cache[0] = conv_state
        kd = a.linear_num_key_heads * a.linear_key_head_dim
        q, k, v = mx.split(mixed, [kd, 2 * kd], axis=-1)
        q = q.reshape(b, s, a.linear_num_key_heads, a.linear_key_head_dim).astype(mx.float32)
        k = k.reshape(q.shape).astype(mx.float32)
        # Reference l2norm uses sum + eps, not RMS mean + eps.
        q *= mx.rsqrt(mx.sum(q * q, axis=-1, keepdims=True) + 1e-6) / a.linear_key_head_dim ** 0.5
        k *= mx.rsqrt(mx.sum(k * k, axis=-1, keepdims=True) + 1e-6)
        v = v.reshape(b, s, a.linear_num_value_heads, a.linear_value_head_dim)
        out, state = gated_delta_update(q, k, v.astype(mx.float32), self.in_proj_a(x).astype(mx.float32), self.in_proj_b(x),
                                        self.A_log, self.dt_bias.astype(mx.float32), cache[1] if cache else None, mask,
                                        use_kernel=not self.training and a.linear_key_head_dim % 32 == 0)
        if cache is not None:
            cache[1] = state
        out = self.norm(out.astype(x.dtype), self.in_proj_z(x).reshape(v.shape))
        return self.out_proj(out.reshape(b, s, -1))


class QSAIndexer(nn.Module):
    def __init__(self, a):
        super().__init__()
        self._args = a
        self.index_qk_proj = nn.Linear(a.hidden_size, (a.indexer_n_heads + 1) * a.indexer_head_dim, bias=False)
        self.q_layernorm = RMSNorm(a.indexer_head_dim, a.rms_norm_eps)
        self.k_layernorm = RMSNorm(a.indexer_head_dim, a.rms_norm_eps)

    def __call__(self, x, positions, valid, cache):
        a = self._args
        b, s, _ = x.shape
        qk = self.index_qk_proj(x)
        split = a.indexer_n_heads * a.indexer_head_dim
        q = rope(self.q_layernorm(qk[..., :split].reshape(b, s, a.indexer_n_heads, a.indexer_head_dim)), positions, a)
        raw = qk[..., split:]
        if cache is not None:
            if cache.raw_keys is not None:
                raw = mx.concatenate([cache.raw_keys, raw], axis=1)
            cache.raw_keys = raw
        t = raw.shape[1]
        # This shortcut is exact: all complete blocks and each query's tail fit.
        if t <= a.indexer_budget:
            return None
        r = a.indexer_compress_ratio
        blocks = t // r
        left = t - valid.sum(axis=1)
        cols = left[:, None, None] + mx.arange(blocks)[None, :, None] * r + mx.arange(r)[None, None, :]
        cols = mx.minimum(cols.reshape(b, -1), t - 1)
        pooled = raw[mx.arange(b)[:, None], cols].reshape(b, blocks, r, a.indexer_head_dim)
        pooled = pooled.astype(mx.float32).mean(axis=2).astype(raw.dtype)
        pooled = rope(self.k_layernorm(pooled), mx.broadcast_to(mx.arange(blocks)[None] * r, (b, blocks)), a)
        scores = mx.maximum(mx.einsum("bshd,bnd->bsnh", q.astype(mx.float32), pooled.astype(mx.float32)), 0).sum(axis=-1)
        complete = mx.maximum(positions + 1, 0) // r
        visible = mx.arange(blocks)[None, None] < complete[..., None]
        scores = mx.where(visible, scores, -mx.inf)
        topk = min(a.indexer_budget // r, blocks)
        top = mx.argpartition(-scores, topk - 1, axis=-1)[..., :topk]
        picked = mx.take_along_axis(visible, top, axis=-1)
        tok = left[:, None, None, None] + top[..., None] * r + mx.arange(r)[None, None, None]
        good = mx.broadcast_to(picked[..., None], tok.shape)
        # The incomplete block is query-local, never the buffer's final block.
        tail = left[:, None, None] + complete[..., None] * r + mx.arange(r - 1)[None, None]
        tail_good = tail <= (left[:, None] + positions)[..., None]
        return (mx.concatenate([tok.reshape(b, s, -1), tail], axis=-1),
                mx.concatenate([good.reshape(b, s, -1), tail_good], axis=-1))


class Attention(nn.Module):
    def __init__(self, a):
        super().__init__()
        self._args = a
        self.indexer = QSAIndexer(a)
        self.q_proj = nn.Linear(a.hidden_size, a.num_attention_heads * a.head_dim * 2, bias=a.attention_bias)
        self.k_proj = nn.Linear(a.hidden_size, a.num_key_value_heads * a.head_dim, bias=a.attention_bias)
        self.v_proj = nn.Linear(a.hidden_size, a.num_key_value_heads * a.head_dim, bias=a.attention_bias)
        self.o_proj = nn.Linear(a.num_attention_heads * a.head_dim, a.hidden_size, bias=a.attention_bias)
        self.q_norm = RMSNorm(a.head_dim, a.rms_norm_eps)
        self.k_norm = RMSNorm(a.head_dim, a.rms_norm_eps)

    def __call__(self, x, mask, cache):
        a = self._args
        b, s, _ = x.shape
        valid = mask if cache is None or cache.valid is None else mx.concatenate([cache.valid, mask], axis=1)
        positions = mx.cumsum(valid.astype(mx.int32), axis=1)[:, -s:] - 1
        selected = self.indexer(x, positions, valid, cache)
        q, gate = mx.split(self.q_proj(x).reshape(b, s, a.num_attention_heads, 2 * a.head_dim), 2, axis=-1)
        q = rope(self.q_norm(q), positions, a).transpose(0, 2, 1, 3)
        k = rope(self.k_norm(self.k_proj(x).reshape(b, s, a.num_key_value_heads, a.head_dim)), positions, a).transpose(0, 2, 1, 3)
        v = self.v_proj(x).reshape(b, s, a.num_key_value_heads, a.head_dim).transpose(0, 2, 1, 3)
        if cache is not None:
            k, v = cache.update_and_fetch(k, v)
            cache.valid = valid
        if selected is None:
            causal = mx.arange(k.shape[2])[None, None, :] <= mx.arange(k.shape[2] - s, k.shape[2])[None, :, None]
            keep = causal & valid[:, None, :]
            # Fully padded queries get a harmless self entry, then are zeroed.
            keep = keep | (~mask[..., None] & (mx.arange(k.shape[2])[None, None] ==
                                               mx.arange(k.shape[2] - s, k.shape[2])[None, :, None]))
            out = mx.fast.scaled_dot_product_attention(q, k, v, scale=a.head_dim ** -0.5, mask=keep[:, None])
            out = out.transpose(0, 2, 1, 3)
        else:
            indices, keep = selected
            indices = mx.clip(indices, 0, k.shape[2] - 1)
            # Per-query sparse KV gather keeps workspace proportional to budget,
            # rather than materializing [heads, chunk, entire context] scores.
            kk = k.transpose(0, 2, 1, 3)[mx.arange(b)[:, None, None], indices]
            vv = v.transpose(0, 2, 1, 3)[mx.arange(b)[:, None, None], indices]
            kk = kk.transpose(0, 1, 3, 2, 4).reshape(b * s, a.num_key_value_heads, -1, a.head_dim)
            vv = vv.transpose(0, 1, 3, 2, 4).reshape(kk.shape)
            # Avoid NaNs on padding-only rows. Their outputs are discarded.
            keep = keep | ~mask[..., None]
            out = mx.fast.scaled_dot_product_attention(q.transpose(0, 2, 1, 3).reshape(b * s, a.num_attention_heads, 1, a.head_dim),
                                                       kk, vv, scale=a.head_dim ** -0.5,
                                                       mask=keep.reshape(b * s, 1, 1, -1))
            out = out.reshape(b, s, a.num_attention_heads, a.head_dim)
        out = out * mx.sigmoid(gate)
        return mx.where(mask[..., None], self.o_proj(out.reshape(b, s, -1)), 0)


class MLP(nn.Module):
    def __init__(self, d, m):
        super().__init__()
        self.gate_proj = nn.Linear(d, m, bias=False)
        self.up_proj = nn.Linear(d, m, bias=False)
        self.down_proj = nn.Linear(m, d, bias=False)

    def __call__(self, x):
        return self.down_proj(nn.silu(self.gate_proj(x)) * self.up_proj(x))


class SparseMoE(nn.Module):
    def __init__(self, a):
        super().__init__()
        self._args = a
        self.gate = nn.Linear(a.hidden_size, a.num_experts, bias=False)
        self.switch_mlp = SwitchGLU(a.hidden_size, a.moe_intermediate_size, a.num_experts)
        self.shared_expert = MLP(a.hidden_size, a.shared_expert_intermediate_size)
        self.shared_expert_gate = nn.Linear(a.hidden_size, 1, bias=False)

    def __call__(self, x):
        probs = mx.softmax(self.gate(x).astype(mx.float32), axis=-1)
        indices = mx.argpartition(-probs, self._args.num_experts_per_tok - 1, axis=-1)[..., :self._args.num_experts_per_tok]
        weights = mx.take_along_axis(probs, indices, axis=-1)
        if self._args.norm_topk_prob:
            weights /= weights.sum(axis=-1, keepdims=True)
        routed = (self.switch_mlp(x, indices) * weights.astype(x.dtype)[..., None]).sum(axis=-2)
        return routed + mx.sigmoid(self.shared_expert_gate(x)) * self.shared_expert(x)


class NGramEmbedding(nn.Module):
    def __init__(self, a, ple_index):
        super().__init__()
        self._args, self._index = a, ple_index
        self._layout = tables.ngram_layout(vars(a), ple_index)
        descriptor = a.ple_tables.get(str(a.ple_layer_ids[ple_index]))
        self._table = None
        if descriptor:
            descriptor = dict(descriptor)
            descriptor["path"] = Path(__file__).parent / descriptor["path"]
            self._table = tables.MMapTable(**descriptor)
            if self._table.rows != self._layout["rows"] or self._table.dim != self._layout["dim"]:
                raise ValueError("Offloaded PLE layout disagrees with configuration")
        else:
            # Tiny/reference-only route. Production conversion always offloads.
            if self._layout["rows"] * self._layout["dim"] > 16_000_000:
                raise ValueError("Large PLE table requires an on-disk descriptor; refusing GPU allocation")
            self.ngram_embedding = nn.Embedding(self._layout["rows"], self._layout["dim"])

    def __call__(self, ids, cache):
        a = self._args
        eos = a.eos_token_id[0] if isinstance(a.eos_token_id, list) else a.eos_token_id
        previous = cache[3] if cache is not None else None
        previous = np.full((ids.shape[0], a.ngram_size - 1), eos, dtype=np.int64) if previous is None else np.array(previous)
        host_ids = np.array(ids)
        indices = tables.ngram_ids(host_ids, previous, vars(a), self._index)
        if cache is not None:
            cache[3] = mx.array(np.concatenate([previous, host_ids], axis=1)[:, -(a.ngram_size - 1):].astype(np.int32))
        if self._table is not None:
            return mx.array(self._table.lookup(indices)).reshape(*ids.shape, -1)
        return self.ngram_embedding(mx.array(indices.astype(np.int32))).reshape(*ids.shape, -1)


class PLE(nn.Module):
    def __init__(self, a, ple_index):
        super().__init__()
        self._args = a
        self.ple_embedding = NGramEmbedding(a, ple_index)
        self.key_proj = nn.Linear(a.ple_embed_dim, a.hc_count * a.hidden_size, bias=False)
        self.value_proj = nn.Linear(a.ple_embed_dim, a.hidden_size, bias=False)
        for name in ("norm_key", "norm_query", "norm_conv"):
            setattr(self, name, RMSNorm(a.hc_count * a.hidden_size, a.rms_norm_eps, a.hidden_size))
        d = a.hc_count * a.hidden_size
        self.conv1d = nn.Conv1d(d, d, a.ple_conv_kernel_size, groups=d, dilation=a.ngram_size, bias=False)

    def __call__(self, x, ids, mask, cache):
        a = self._args
        emb = self.ple_embedding(ids, cache).astype(x.dtype)
        shape = (*ids.shape, a.hc_count, a.hidden_size)
        key = self.norm_key(self.key_proj(emb)).reshape(shape)
        query = self.norm_query(x).reshape(shape)
        gate = (key * query).sum(axis=-1, keepdims=True) / a.hidden_size ** 0.5
        gate = mx.sqrt(mx.maximum(mx.abs(gate), 1e-6)) * mx.sign(gate)
        value = (mx.sigmoid(gate) * self.value_proj(emb)[..., None, :]).reshape(x.shape)
        normed = mx.where(mask[..., None], self.norm_conv(value), 0)
        conv, state = short_conv(self.conv1d, normed, cache[2] if cache else None, a.ngram_size)
        if cache is not None:
            cache[2] = state
        return mx.where(mask[..., None], value, 0) + conv


class DecoderLayer(nn.Module):
    def __init__(self, a, index):
        super().__init__()
        self._args = a
        self._linear = a.layer_types[index] == "linear_attention"
        if self._linear:
            self.linear_attn = GatedDeltaNet(a)
        else:
            self.self_attn = Attention(a)
        self.attn_hyper_connection = HyperConnection(a)
        self.mlp_hyper_connection = HyperConnection(a)
        self.mlp = SparseMoE(a)
        self.ple = PLE(a, a.ple_layer_ids.index(index + 1)) if index + 1 in a.ple_layer_ids else None

    def __call__(self, x, ids, mask, cache):
        a = self._args
        if self.ple is not None:
            x = x + self.ple(x, ids, mask, cache)
        mixed, weights = self.attn_hyper_connection(x)
        attn = self.linear_attn(mixed, mask, cache) if self._linear else self.self_attn(mixed, mask, cache)
        x = x + (attn[..., None, :] * weights[..., None]).reshape(x.shape)
        mixed, weights = self.mlp_hyper_connection(x)
        x = x + (self.mlp(mixed)[..., None, :] * weights[..., None]).reshape(x.shape)
        if self._linear and cache is not None:
            cache.advance(ids.shape[1])
        return x


class TextModel(nn.Module):
    def __init__(self, a):
        super().__init__()
        self.embed_tokens = nn.Embedding(a.vocab_size, a.hidden_size)
        self.layers = [DecoderLayer(a, i) for i in range(a.num_hidden_layers)]
        self.hyper_connection_mixer = HyperConnection(a, combine=False)


class Model(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.model_type = args.model_type
        self.model = TextModel(args)
        if not args.tie_word_embeddings:
            self.lm_head = nn.Linear(args.hidden_size, args.vocab_size, bias=False)

    @property
    def layers(self):
        return self.model.layers

    def make_cache(self):
        return [Qwen4ExpRecurrentCache() if t == "linear_attention" else Qwen4ExpAttentionCache()
                for t in self.args.layer_types]

    def __call__(self, inputs, cache=None, attention_mask=None):
        if inputs.ndim != 2 or inputs.shape[1] == 0:
            raise ValueError("Nonempty [batch, tokens] input required")
        if cache is not None and len(cache) != len(self.layers):
            raise ValueError("Wrong cache layer count")
        if cache is not None and len({c.offset for c in cache}) != 1:
            raise ValueError("Hybrid cache offsets disagree")
        mask = mx.ones(inputs.shape, dtype=mx.bool_) if attention_mask is None else attention_mask[:, -inputs.shape[1]:].astype(mx.bool_)
        # Only initial left padding is supported. Holes or right padding need
        # sequence compaction, not the contiguous compressed-block algorithm.
        if attention_mask is not None:
            host = np.array(mask)
            if host.shape != inputs.shape or np.any(host[:, 1:] < host[:, :-1]) or (
                    cache is not None and cache[0].offset and not host.all()):
                raise ValueError("Only initial left padding is supported")
        eos = self.args.eos_token_id
        eos = eos[0] if isinstance(eos, list) else eos
        ids = mx.where(mask, inputs, eos) if self.args.ple_layer_ids else inputs
        x = mx.tile(self.model.embed_tokens(inputs), (1, 1, self.args.hc_count))
        for i, layer in enumerate(self.layers):
            x = layer(x, ids, mask, cache[i] if cache is not None else None)
        x = self.model.hyper_connection_mixer(x)
        return self.model.embed_tokens.as_linear(x) if self.args.tie_word_embeddings else self.lm_head(x)

    def sanitize(self, weights):
        out, shards = {}, {}
        for original, value in weights.items():
            key = tables.canonical_name(original)
            if key is None:
                continue
            if key.rsplit(".", 1)[-1] in tables.CONSTANTS:
                layer = int(key.split("layers.", 1)[1].split(".", 1)[0]) + 1
                layout = tables.ngram_layout(vars(self.args), self.args.ple_layer_ids.index(layer))
                expected = layout[dict(zip(tables.CONSTANTS, ("multipliers", "sizes", "offsets")))[key.rsplit(".", 1)[-1]]]
                if not np.array_equal(np.array(value), expected):
                    raise ValueError(f"N-gram hash constant mismatch: {original}")
                continue
            match = tables.SHARD_RE.search(key)
            if match:
                base = tables.SHARD_RE.sub(".ngram_embedding.weight", key)
                shards.setdefault(base, {})[int(match[1])] = value
                continue
            if key.endswith("mlp.experts.gate_up_proj"):
                gate, up = mx.split(value, 2, axis=-2)
                base = key[:-len("experts.gate_up_proj")]
                out[base + "switch_mlp.gate_proj.weight"] = gate
                out[base + "switch_mlp.up_proj.weight"] = up
            elif key.endswith("mlp.experts.down_proj"):
                out[key[:-len("experts.down_proj")] + "switch_mlp.down_proj.weight"] = value
            elif key.endswith("conv1d.weight") and value.shape[1] == 1:
                out[key] = value.transpose(0, 2, 1)
            else:
                out[key] = value
        for key, parts in shards.items():
            if sorted(parts) != list(range(len(parts))):
                raise ValueError(f"Non-contiguous PLE shards: {key}")
            out[key] = mx.concatenate([parts[i] for i in range(len(parts))], axis=0)
        if self.args.tie_word_embeddings:
            out.pop("lm_head.weight", None)
        return out

    @property
    def quant_predicate(self):
        # Keeping the whole Attention module unmodified preserves the indexer.
        # Only its leaf projections may be replaced by quantized linears.
        def predicate(path, module):
            return hasattr(module, "to_quantized") and not path.endswith(("mlp.gate", "shared_expert_gate"))
        return predicate
