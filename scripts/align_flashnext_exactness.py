#!/usr/bin/env python3
"""Deferred MLX checks. Importing this script is safe; MLX imports require desk approval.

Run with python -m scripts.align_flashnext_exactness. Known broken paths produce
FAIL records and a nonzero exit, never xfail/green qualification.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import tempfile

from scripts.align_flashnext_common import approved_runtime, verify_inventory


def tiny_config():
    return dict(hidden_size=64, num_hidden_layers=4, num_attention_heads=4,
                num_key_value_heads=2, head_dim=32, vocab_size=128,
                full_attention_interval=4, num_experts=8, num_experts_per_tok=2,
                moe_intermediate_size=32, shared_expert_intermediate_size=32,
                linear_num_key_heads=2, linear_num_value_heads=4,
                linear_key_head_dim=16, linear_value_head_dim=16,
                linear_conv_kernel_dim=4, hc_count=4, hc_lowrank=16,
                indexer_n_heads=2, indexer_kv_heads=1, indexer_head_dim=16,
                indexer_budget=8, indexer_compress_ratio=4, ngram_size=3,
                heads_per_ngram=2, ngram_vocab_size_base=101,
                split_ngram_parts=4, ple_embed_dim=64, ple_layer_ids=[2],
                ple_conv_kernel_size=4, eos_token_id=1, seed=1234,
                rope_parameters={"rope_theta": 10000000, "partial_rotary_factor": 0.25})


def walk_copy(value, clone_array):
    if isinstance(value, list):
        return [walk_copy(v, clone_array) for v in value]
    if isinstance(value, tuple):
        return tuple(walk_copy(v, clone_array) for v in value)
    if isinstance(value, dict):
        return {k: walk_copy(v, clone_array) for k, v in value.items()}
    return copy.deepcopy(value) if value is None or isinstance(value, (str, int, float, bool)) else clone_array(value)


def exercise(model, *, lengths, atol, rtol):
    # This function is called only after approved_runtime has verified the venv.
    import mlx.core as mx
    import numpy as np
    from mlx_lm.models import cache as api, qwen4_exp as q

    rows = []

    def check(name, fn):
        try:
            detail = fn()
            rows.append({"check": name, "status": "PASS", "detail": detail})
        except Exception as exc:
            rows.append({"check": name, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})

    def compare(a, b):
        mx.eval(a, b)
        if a.shape != b.shape:
            raise AssertionError(f"shape mismatch: {a.shape}, {b.shape}")
        maximum = squares = kl_sum = agreements = positions = elements = 0
        close = True
        # Bound host temporaries even for the 248,320-wide real LM head.
        for start in range(0, a.shape[1], 16):
            aa = np.asarray(a[:, start:start+16].astype(mx.float32))
            bb = np.asarray(b[:, start:start+16].astype(mx.float32))
            if not np.isfinite(aa).all() or not np.isfinite(bb).all():
                raise AssertionError("nonfinite logits")
            delta = np.abs(aa - bb)
            maximum = max(maximum, float(delta.max()))
            squares += float(np.sum(delta.astype(np.float64) ** 2))
            elements += delta.size
            agreements += int(np.sum(aa.argmax(-1) == bb.argmax(-1)))
            positions += aa.shape[0] * aa.shape[1]
            la, lb = aa - aa.max(-1, keepdims=True), bb - bb.max(-1, keepdims=True)
            la -= np.log(np.exp(la).sum(-1, keepdims=True))
            lb -= np.log(np.exp(lb).sum(-1, keepdims=True))
            kl_sum += float((np.exp(la) * (la - lb)).sum(dtype=np.float64))
            close = close and bool(np.allclose(aa, bb, atol=atol, rtol=rtol))
        detail = {"max_abs": maximum, "rms": (squares / elements) ** 0.5,
                  "argmax_agreement": agreements / positions, "mean_kl_nats": kl_sum / positions}
        if not close:
            raise AssertionError(json.dumps(detail))
        return detail

    def clone_array(a):
        # NumPy need not support BF16. Float32 represents every BF16 value
        # exactly; integer caches must keep their integer bits unchanged.
        host_source = a.astype(mx.float32) if a.dtype == mx.bfloat16 else a
        return mx.array(np.array(host_source, copy=True)).astype(a.dtype)

    def clone_cache(caches):
        # Host copies intentionally sever all array aliases, including KV's
        # in-place writes. Fresh model caches supply private-class constructors.
        result = model.make_cache()
        for dest, src in zip(result, caches):
            dest.state = walk_copy(src.state, clone_array)
            dest.meta_state = copy.deepcopy(src.meta_state)
        return result

    def feed(ids, caches=None):
        logits = model(mx.array([ids]), cache=caches)
        mx.eval(logits)
        return logits

    vocab = model.args.text.vocab_size
    eos = model.args.text.eos_token_id
    eos = eos[0] if isinstance(eos, list) else eos
    for length in lengths:
        ids = [3 + (i * 17) % (min(vocab, 4096) - 3) for i in range(length)]
        if length > 6:
            ids[5] = eos  # exercise n-gram EOS reset inside the sequence
        label = f"L{length}"

        def prefill_step():
            reference = feed(ids)
            caches = model.make_cache()
            worst, agreements = 0.0, []
            for i, token in enumerate(ids):
                detail = compare(reference[:, i:i+1], feed([token], caches))
                worst = max(worst, detail["max_abs"])
                agreements.append(detail["argmax_agreement"])
            return {"max_abs": worst, "mean_argmax_agreement": sum(agreements) / len(agreements)}
        check(label + "/prefill_vs_step", prefill_step)

        def chunks():
            reference = feed(ids)
            details = {}
            for chunk in (3, 4, 7, 512):
                caches = model.make_cache()
                for start in range(0, length, chunk):
                    detail = compare(reference[:, start:start+chunk], feed(ids[start:start+chunk], caches))
                    details[str(chunk)] = max(details.get(str(chunk), 0), detail["max_abs"])
            return details
        check(label + "/chunk_boundaries", chunks)
        check(label + "/causality", lambda: compare(feed(ids)[:, :-1], feed(ids[:-1] + [(ids[-1] + 1) % vocab])[:, :-1]))

        def padded(left):
            pad = 3
            longer = ids + [7] * pad
            if left:
                caches = [q._BatchAttnCache([pad, 0]) if layer.layer_type == "full_attention"
                          else q._LayerCache(4, left_padding=[pad, 0]) for layer in model.layers]
            else:
                first, second = model.make_cache(), model.make_cache()
                caches = [type(a).merge([a, b]) for a, b in zip(first, second)]
            if not left:
                for c in caches:
                    c.prepare(lengths=[length, length + pad], right_padding=[pad, 0])
            padded_ids = [0] * pad + ids if left else ids + [0] * pad
            out = model(mx.array([padded_ids, longer]), cache=caches)
            mx.eval(out)
            detail = compare(feed(ids), out[0:1, pad:] if left else out[0:1, :length])
            for c in caches:
                c.finalize()
            extracted = [c.extract(0) for c in caches]
            solo = model.make_cache()
            feed(ids, solo)
            expected = feed([9], solo)
            compare(expected, feed([9], extracted))
            compare(expected, model(mx.array([[9], [9]]), cache=caches)[0:1])
            return detail
        check(label + "/raw_left_padding", lambda: padded(True))
        check(label + "/right_padding_finalize_decode", lambda: padded(False))

        def cache_restore():
            split = max(2, length // 2)
            prefix, suffix = ids[:split], ids[split:]
            caches = model.make_cache()
            feed(prefix, caches)
            saved = clone_cache(caches)
            original = feed(suffix, caches)
            # saved includes Delta conv/FP32 matrix, PLE conv/history and indexer.
            restored = clone_cache(saved)
            detail = compare(original, feed(suffix, restored))
            compare(feed(ids), mx.concatenate([feed(prefix), feed(suffix, clone_cache(saved))], axis=1))
            # Generic hybrid trim MUST refuse atomically, without touching KV.
            before = clone_cache(caches)
            if api.can_trim_prompt_cache(caches) or api.trim_prompt_cache(caches, len(suffix)) != 0:
                raise AssertionError("hybrid trim unexpectedly allowed")
            for a, b in zip(before, caches):
                def assert_same(x, y):
                    if isinstance(x, (tuple, list)):
                        if len(x) != len(y):
                            raise AssertionError("cache state length changed on refused trim")
                        for xx, yy in zip(x, y):
                            assert_same(xx, yy)
                    elif x is None:
                        if y is not None:
                            raise AssertionError("unused cache slot changed on refused trim")
                    else:
                        if x.dtype != y.dtype or x.shape != y.shape or not mx.array_equal(x, y):
                            raise AssertionError("cache array changed on refused trim")
                assert_same(a.state, b.state)
            # Checkpoint lane recipe: trim attention at current position, restore
            # recurrent layers at prefix boundary, then re-feed the suffix.
            for i, c in enumerate(caches):
                if hasattr(c, "indexer"):
                    if c.trim(len(suffix)) != len(suffix) or c.indexer.keys.shape[1] != split:
                        raise AssertionError("KV/indexer rewind offset mismatch")
                else:
                    caches[i].state = walk_copy(saved[i].state, clone_array)
                    caches[i].meta_state = copy.deepcopy(saved[i].meta_state)
            compare(original, feed(suffix, caches))
            # Branch the suffix to detect stale state surviving a rewind.
            alternate = suffix[:-1] + [(suffix[-1] + 3) % vocab]
            compare(feed(prefix + alternate)[:, split:], feed(alternate, clone_cache(saved)))
            return detail
        check(label + "/hybrid_snapshot_trim_restore", cache_restore)

    def native_disk():
        caches = model.make_cache()
        feed(ids, caches)
        with tempfile.TemporaryDirectory(prefix="flashnext-cache-") as temp:
            path = str(Path(temp) / "cache.safetensors")
            api.save_prompt_cache(path, caches)
            loaded = api.load_prompt_cache(path)
            return compare(feed([9], caches), feed([9], loaded))
    check("native_disk_cache_roundtrip", native_disk)

    def kv_quant():
        caches = model.make_cache()
        feed(ids, caches)
        for c in caches:
            if hasattr(c, "indexer"):
                converted = c.to_quantized(group_size=32, bits=4)
                if not hasattr(converted, "indexer"):
                    raise AssertionError("to_quantized lost QSA indexer; --kv-bits forbidden")
        return "indexer retained"
    check("kv_quantization_retains_indexer", kv_quant)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--approved-desk", action="store_true")
    p.add_argument("--pins", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--model", type=Path)
    p.add_argument("--artifact-manifest", type=Path)
    p.add_argument("--seeds", default="0,1,7")
    p.add_argument("--lengths", default="7,8,9,20,23,70")
    p.add_argument("--atol", type=float, default=1e-4)
    p.add_argument("--rtol", type=float, default=1e-4)
    args = p.parse_args()
    if args.output.exists():
        p.error("output exists; preserve prior evidence")
    lengths = [int(n) for n in args.lengths.split(",")]
    if min(lengths) < 7 or args.atol < 0 or args.rtol < 0:
        p.error("lengths >= 7 and nonnegative tolerances required")
    pins = approved_runtime(args.approved_desk, args.pins)
    if args.model:
        if not args.artifact_manifest:
            p.error("real model requires artifact manifest")
        verify_inventory(args.model, json.loads(args.artifact_manifest.read_text())["files"])
    import mlx.core as mx
    from mlx_lm.models import qwen4_exp as q
    from mlx_lm.utils import load
    report = {"status": "DESK_DIAGNOSTIC_NOT_WINDOW_ADMISSION", "pins": pins,
              "atol": args.atol, "rtol": args.rtol, "runs": []}
    for seed in ([0] if args.model else [int(n) for n in args.seeds.split(",")]):
        mx.random.seed(seed)
        model = load(str(args.model), tokenizer_config={"trust_remote_code": False})[0] if args.model else q.Model(q.ModelArgs(text_config=tiny_config()))
        model.eval()
        rows = exercise(model, lengths=lengths, atol=args.atol, rtol=args.rtol)
        report["runs"].append({"seed": seed, "checks": rows})
        del model
        mx.clear_cache()
    report["all_checks_pass"] = all(row["status"] == "PASS" for run in report["runs"] for row in run["checks"])
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
