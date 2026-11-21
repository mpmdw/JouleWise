"""Patch draft for finding D1 (mlx-vlm 0.7.12, mlx_vlm/models/qwen4_exp/language.py):
with a left-padded batch cache, QSA decode (L=1, mask "left_padded_decode") and
batched multi-token verify discard the indexer's selection and attend densely.

The fix keeps the selection: build the indexer's left-padding-aware boolean
mask (Qwen4ExpQSAIndexer.build_mask, which already offsets blocks by each
row's left padding and excludes pad columns) and run masked SDPA over the
padded KV, instead of the Qwen3.5 ragged dense helper that ignores masks.
Dense prefixes (selection is None) keep the original exact ragged path.

apply() installs the fix by monkeypatching, for testing; the same change as a
source diff is in d1_qsa_left_padding.patch.
"""
import mlx.core as mx


def _padded(cache, mask):
    from mlx_vlm.models.qwen3_5.language import _qwen3_5_left_padding_info
    if isinstance(mask, str) and mask == "left_padded_decode":
        return True
    info = _qwen3_5_left_padding_info(cache) if cache is not None else None
    return info is not None and info[1] > 0


def _masked_qsa(attention, linears, linear, hidden, cache, position_ids, position_embeddings,
                selection, mask):
    from mlx_vlm.models.base import scaled_dot_product_attention
    qsa_mask = attention.indexer.build_mask(selection)
    if isinstance(mask, mx.array):
        qsa_mask = qsa_mask & mask if mask.dtype == mx.bool_ else qsa_mask & (mask == 0)
    batch, length, _ = hidden.shape
    q, k, v = linears((attention.q_proj, attention.k_proj, attention.v_proj), hidden)
    queries, keys, values, gate, _ = attention._prepare_projected_qkv(
        q, k, v, cache, position_ids, position_embeddings, None)
    out = scaled_dot_product_attention(queries, keys, values, cache=cache,
                                       scale=attention.scale, mask=qsa_mask)
    out = out.transpose(0, 2, 1, 3).reshape(batch, length, -1)
    return linear(attention.o_proj, out * mx.sigmoid(gate))


def apply():
    from mlx_vlm.models.qwen4_exp import language as L4
    from mlx_vlm.models.qwen3_5.language import Qwen3_5Attention

    original_call = L4.Qwen4ExpAttention.__call__
    original_qsa = L4.Qwen4ExpBatchInvariantForward._qsa_attention

    def attention_call(self, x, mask=None, cache=None, position_ids=None, position_embeddings=None):
        if not (isinstance(mask, str) and mask == "left_padded_decode"):
            return original_call(self, x, mask=mask, cache=cache, position_ids=position_ids,
                                 position_embeddings=position_embeddings)
        selection = self.indexer.select(x, cache, position_ids)  # appends index keys once
        if selection is None:
            return Qwen3_5Attention.__call__(self, x, mask=mask, cache=cache, position_ids=position_ids,
                                             position_embeddings=position_embeddings)
        return _masked_qsa(self, lambda ls, h: tuple(l(h) for l in ls), lambda l, h: l(h), x, cache,
                           position_ids, position_embeddings, selection, None)

    def qsa_attention(self, attention, hidden_states, cache, position_ids, mask):
        if not _padded(cache, mask):
            return original_qsa(self, attention, hidden_states, cache, position_ids, mask)
        projected = self._linear(attention.indexer.index_qk_proj, hidden_states)
        selection = attention.indexer.select_from_projected(projected, cache, position_ids)
        if selection is None:
            return self._attention(attention, hidden_states, mask, cache, position_ids, None)
        return _masked_qsa(attention, self._linears, self._linear, hidden_states, cache, position_ids,
                           None, selection, mask if isinstance(mask, mx.array) else None)

    L4.Qwen4ExpAttention.__call__ = attention_call
    L4.Qwen4ExpBatchInvariantForward._qsa_attention = qsa_attention
