"""Pin transformers reference logits for tests/align/test_qwen4_exp_upstream_shape.py.

Run with the approved reference venv (torch 2.15.0, transformers 5.22.1):

    OMP_NUM_THREADS=2 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 nice -n 10 \
        /private/tmp/jwsol/venv-ref/bin/python -I -B \
        scripts/align_qwen4_exp_upstream_pin.py [--write]

It imports the test module by path (its MLX imports are guarded), rebuilds the
closed-form official-layout checkpoint, loads it into the official
``Qwen4ExpForCausalLM`` two ways (direct strict ``load_state_dict`` after the
minimal key mapping, and ``from_pretrained`` through transformers' own
checkpoint conversion), and checks that:

* both loads give identical logits (the key mapping matches transformers');
* sdpa and eager attention agree;
* reference prefill equals reference cached stepwise decoding;
* the helper's n-gram constants equal the reference buffers (tiny) and the
  reference formula functions (real config);
* routing and QSA block selection have clear margins (no near-ties that a
  correct port could flip through float reordering).

``--write`` replaces the PINNED REFERENCE block of the test file. Without it
the block is printed. Nothing outside the test file and a temporary
directory under ``$TMPDIR`` is written.
"""

import argparse
import hashlib
import importlib.util
import inspect
import json
import math
import os
import pprint
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch
import transformers
from safetensors.numpy import save_file
from transformers import Qwen4ExpConfig, Qwen4ExpForCausalLM
from transformers.models.qwen4_exp import modeling_qwen4_exp as ref

ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / "tests" / "align" / "test_qwen4_exp_upstream_shape.py"
BEGIN = "# BEGIN PINNED REFERENCE"
END = "# END PINNED REFERENCE"


def load_test_module():
    spec = importlib.util.spec_from_file_location("qwen4_upstream_shape", TEST_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_config(t):
    cfg = Qwen4ExpConfig.from_dict(json.loads(json.dumps(t.TINY_CONFIG)))
    return cfg.text_config


def runtime_state_dict(hf):
    """Official layout -> Qwen4ExpForCausalLM state dict (minimal mapping)."""
    out, shards = {}, {}
    for k, v in hf.items():
        if k.startswith("mtp.") or k.startswith("model.visual."):
            continue
        k = k.replace("model.language_model.", "model.", 1)
        if ".ngram_embedding.shard_" in k:
            base, rest = k.split(".ngram_embedding.shard_")
            shards.setdefault(base, {})[int(rest.split(".")[0])] = v
            continue
        out[k] = torch.from_numpy(np.array(v))
    for base, parts in shards.items():
        ordered = [parts[i] for i in range(len(parts))]
        out[base + ".ngram_embedding.weight"] = torch.from_numpy(np.concatenate(ordered))
    return out


def text_layout_checkpoint(hf):
    """Official layout with the text-only prefix, as from_pretrained input."""
    out = {}
    for k, v in hf.items():
        if k.startswith("mtp.") or k.startswith("model.visual."):
            continue
        out[k.replace("model.language_model.", "model.", 1)] = np.ascontiguousarray(v)
    return out


def build_model(cfg, attn):
    cfg = type(cfg).from_dict(cfg.to_dict())
    cfg._attn_implementation = attn
    torch.manual_seed(0)
    model = Qwen4ExpForCausalLM(cfg).eval().to(torch.float32)
    return model


def router_margin(model, ids):
    gaps = []
    k = model.config.num_experts_per_tok

    def hook(_, __, output):
        # Gap between the k-th and (k+1)-th router logit: top-k flips only
        # if float reordering moves logits by this much.
        top = output[0].float().sort(dim=-1, descending=True).values
        gaps.append(float((top[:, k - 1] - top[:, k]).min()))

    handles = [l.mlp.gate.register_forward_hook(hook) for l in model.model.layers]
    with torch.no_grad():
        model(input_ids=ids)
    for h in handles:
        h.remove()
    return min(gaps)


def qsa_margin(model, ids):
    """Smallest score gap at the top-k boundary over all selecting queries."""
    gaps = []

    def pre_hook(module, args, kwargs):
        hidden, pos, mask, _ = args if len(args) == 4 else (*args, None)
        cos, sin = pos
        b, s, _ = hidden.shape
        qk = module.index_qk_proj(hidden)
        q, k = torch.split(
            qk,
            [module.index_n_heads * module.index_head_dim, module.index_head_dim],
            dim=-1,
        )
        q = module.q_layernorm(q.reshape(b, s, -1, module.index_head_dim))
        q = ref.apply_rotary_pos_emb(q, cos=cos[:, -s:], sin=sin[:, -s:], unsqueeze_dim=2)
        keys = k.reshape(b, s, module.index_head_dim)
        visible = mask if mask.dtype == torch.bool else mask == 0
        for bi in range(b):
            for qi in range(s):
                idx = torch.nonzero(visible[bi, 0, qi]).flatten()
                n = idx.shape[-1] // module.compress_ratio
                if n <= module.block_topk:
                    continue
                blocks = idx[: n * module.compress_ratio].view(n, module.compress_ratio)
                pooled = keys[bi].index_select(0, blocks.flatten()).view(n, module.compress_ratio, -1)
                pooled = module.k_layernorm(pooled.float().mean(dim=1))
                starts = blocks[:, 0]
                pooled = ref.apply_rotary_pos_emb(
                    pooled.unsqueeze(1),
                    cos=cos[bi].index_select(0, starts),
                    sin=sin[bi].index_select(0, starts),
                ).squeeze(1)
                scores = torch.relu(q[bi, qi].float() @ pooled.float().T).sum(0)
                scores = scores / math.sqrt(module.index_head_dim)
                top = scores.sort(descending=True).values
                gaps.append(float(top[module.block_topk - 1] - top[module.block_topk]))

    handles = []
    for layer in model.model.layers:
        if hasattr(layer, "self_attn"):
            handles.append(
                layer.self_attn.indexer.register_forward_pre_hook(pre_hook, with_kwargs=True)
            )
    with torch.no_grad():
        model(input_ids=ids)
    for h in handles:
        h.remove()
    return (min(gaps) if gaps else None), len(gaps)


def real_constants():
    """Real-config constants from the reference module's own functions."""
    vocab, n, hpn, base, div = 248320, 3, 8, 20_000_000, 128
    heads = (n - 1) * hpn
    mult = ref._build_layer_multipliers(vocab, n, 0, 1234).tolist()
    sizes, offsets, total = [], [], 0
    for h in range(heads):
        size = ref._find_nth_prime_after(base - 1, h + 1)
        sizes.append(size)
        offsets.append(total)
        total += size
    return {
        "layer_multipliers": mult,
        "vocab_sizes": sizes,
        "offsets": offsets,
        "padded_rows": math.ceil(total / div) * div,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(2)
    t = load_test_module()

    cfg = text_config(t)
    hf = t.hf_checkpoint(layout="official")
    ids = torch.tensor(t.REFERENCE_INPUT_IDS)

    logits = {}
    for attn in ("sdpa", "eager"):
        model = build_model(cfg, attn)
        model.load_state_dict(runtime_state_dict(hf), strict=True)
        with torch.no_grad():
            logits[attn] = model(input_ids=ids).logits.double()
    sdpa_vs_eager = float((logits["sdpa"] - logits["eager"]).abs().max())
    assert sdpa_vs_eager < 1e-5, sdpa_vs_eager
    full = logits["sdpa"]

    # Tiny constants: reference buffers vs the test helper.
    ple = model.model.layers[1].ple.ple_embedding
    tiny = t.ngram_constants(t.TINY_TEXT_CONFIG, 0)
    assert ple.layer_multipliers.tolist() == tiny["layer_multipliers"]
    assert ple.ngram_heads_vocab_sizes.tolist() == tiny["vocab_sizes"]
    assert ple.ngram_heads_offsets.tolist() == tiny["offsets"]
    assert ple.ngram_embedding.weight.shape[0] == tiny["padded_rows"]
    real = real_constants()
    assert t.ngram_constants(t.REAL_NGRAM_TEXT_CONFIG, 0) == real

    # transformers' own loader on the same values.
    tmp_root = os.environ.get("TMPDIR") or None
    with tempfile.TemporaryDirectory(dir=tmp_root) as d:
        save_file(text_layout_checkpoint(hf), os.path.join(d, "model.safetensors"))
        tcfg = type(cfg).from_dict(cfg.to_dict())
        tcfg.save_pretrained(d)
        loaded = Qwen4ExpForCausalLM.from_pretrained(
            d, dtype=torch.float32, attn_implementation="sdpa"
        ).eval()
        with torch.no_grad():
            via_loader = loaded(input_ids=ids).logits.double()
    loader_diff = float((via_loader - full).abs().max())
    assert loader_diff == 0.0, loader_diff

    # Reference self-consistency: cached stepwise equals prefill.
    model = build_model(cfg, "sdpa")
    model.load_state_dict(runtime_state_dict(hf), strict=True)
    steps = []
    with torch.no_grad():
        out = model(input_ids=ids[:, :9], use_cache=True)
        cache = out.past_key_values
        steps.append(out.logits)
        out = model(input_ids=ids[:, 9:13], past_key_values=cache, use_cache=True)
        steps.append(out.logits)
        for i in range(13, ids.shape[1]):
            out = model(input_ids=ids[:, i : i + 1], past_key_values=cache, use_cache=True)
            steps.append(out.logits)
    stepwise = torch.cat(steps, dim=1).double()
    stepwise_diff = float((stepwise - full).abs().max())
    assert stepwise_diff < 1e-5, stepwise_diff

    rmargin = router_margin(model, ids)
    qmargin, qcount = qsa_margin(model, ids)
    assert rmargin > 1e-3, rmargin
    assert qcount > 0 and qmargin > 1e-3, (qmargin, qcount)

    full_np = full.numpy()
    srt = np.sort(full_np, axis=-1)
    m = full_np.max(axis=-1, keepdims=True)
    lse = (m + np.log(np.exp(full_np - m).sum(-1, keepdims=True))).squeeze(-1)
    vocab_ids = t.REFERENCE_VOCAB_IDS

    def rounded(x, digits=7):
        if isinstance(x, list):
            return [rounded(v, digits) for v in x]
        return float(f"{x:.{digits}g}")

    generator_src = "".join(
        inspect.getsource(f)
        for f in (t._uniform, t._closed_form, t._layer_types, t.hf_checkpoint, t.ngram_constants)
    ) + json.dumps(t.TINY_CONFIG, sort_keys=True) + json.dumps(t.REFERENCE_INPUT_IDS)

    reference = {
        "provenance": {
            "transformers": transformers.__version__,
            "torch": torch.__version__,
            "modeling_qwen4_exp_sha256": sha256(ref.__file__),
            "configuration_qwen4_exp_sha256": sha256(
                Path(ref.__file__).with_name("configuration_qwen4_exp.py")
            ),
            "generator_sha256": hashlib.sha256(generator_src.encode()).hexdigest(),
            "dtype": "float32",
            "attn_implementation": "sdpa (eager max diff %.3g)" % sdpa_vs_eager,
            "reference_stepwise_vs_prefill_max_abs": stepwise_diff,
            "from_pretrained_vs_direct_load_max_abs": loader_diff,
            "min_router_topk_logit_gap": rmargin,
            "min_qsa_block_score_gap": qmargin,
            "qsa_selecting_queries": qcount,
        },
        "input_ids": t.REFERENCE_INPUT_IDS,
        "vocab_ids": vocab_ids,
        "logits": rounded(full_np[:, :, vocab_ids].tolist()),
        "logsumexp": rounded(lse.tolist()),
        "argmax": full_np.argmax(-1).tolist(),
        "top2_margin": rounded((srt[..., -1] - srt[..., -2]).tolist(), 4),
        "tiny_ngram_constants": tiny,
        "real_ngram_constants": real,
    }
    block = (
        f"{BEGIN} (generated by scripts/align_qwen4_exp_upstream_pin.py)\n"
        f"REFERENCE = {pprint.pformat(reference, width=88, compact=True, sort_dicts=False)}\n"
        f"{END}"
    )
    print(json.dumps(reference["provenance"], indent=2), file=sys.stderr)
    if not args.write:
        print(block)
        return
    text = TEST_FILE.read_text()
    start = text.index(BEGIN)
    stop = text.index(END) + len(END)
    TEST_FILE.write_text(text[:start] + block + text[stop:])
    print(f"wrote {TEST_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
