"""T1 (finding D1): ragged left-padded batch vs single requests vs reference.

Config C (budget 8, ratio 4: sparse from 12 visible tokens; tie-free indexer).
Prompts of 20 and 17 tokens, left padding [0, 3], 4 teacher-forced greedy
decode steps (the reference's greedy tokens), then a 3-token speculative
verify through LanguageModel.speculative_verify_logits (the MTP verifier).
Control: an equal-length batch [A, A]. Decode is run through the default
batch-invariant path and through the main path. --patched applies d1_patch.

Usage: python t1_ragged.py CASE_DIR [--patched]
"""
import json
import sys
from pathlib import Path

import numpy as np

G, V = 4, 3


def f(v):
    import mlx.core as mx
    v = getattr(v, "logits", v)
    mx.eval(v)
    return np.array(v.astype(mx.float32))


def run(lm, seqs, prompts, batched):
    """Returns per-row logits [n_positions, V] for: prompt last, G decode steps, V verify."""
    import mlx.core as mx
    from mlx_vlm.generate.ar import _make_cache
    lm._position_ids = lm._rope_deltas = None
    B = len(seqs)
    width = max(prompts)
    pads = [width - p for p in prompts]
    if batched:
        cache = _make_cache(lm, pads)
    else:
        cache = lm.make_cache()
    batch = np.zeros((B, width), dtype=np.int32)
    for b, (s, p) in enumerate(zip(seqs, prompts)):
        batch[b, pads[b]:] = s[:p]
    # Prompt metadata exactly as batch_generate/BatchGenerator forward it for
    # text-only rows: get_input_embeddings -> per-row positions 0..n-1, left
    # padded with zeros (_pad_sequence_aligned_prompt_kwarg), rope_deltas 0,
    # and rope_deltas re-sent on every decode step (BatchGenerator._step).
    kw = {}
    if batched:
        pos = np.zeros((B, width), dtype=np.int32)
        for b, p in enumerate(prompts):
            pos[b, pads[b]:] = np.arange(p)
        kw = dict(position_ids=mx.array(pos), rope_deltas=mx.zeros((B, 1), dtype=mx.int32))
    prefill = f(lm(mx.array(batch), cache=cache, **kw))
    rows = [[prefill[b, -1]] for b in range(B)]
    kw.pop("position_ids", None)
    for t in range(G):
        step = np.array([[s[p + t]] for s, p in zip(seqs, prompts)], dtype=np.int32)
        out = f(lm(mx.array(step), cache=cache, **kw))
        for b in range(B):
            rows[b].append(out[b, -1])
    block = np.array([s[p + G:p + G + V] for s, p in zip(seqs, prompts)], dtype=np.int32)
    _, _, tx, logits = lm.speculative_verify_logits(mx.array(block), cache, lambda x: x)
    logits = f(logits)
    tx.abort()
    for b in range(B):
        rows[b].extend(list(logits[b]))
    return [np.stack(r) for r in rows]


def main(case, patched):
    from mlx_vlm.utils import load_model
    if patched:
        import d1_patch
        d1_patch.apply()
    case = Path(case)
    ref = np.load(case / "ref.npz")
    seqs = [ref["t1_seq0"].tolist(), ref["t1_seq1"].tolist()]
    prompts = [20, 17]
    truth = [ref[f"t1_logits{b}"][0][p - 1:p + G + V] for b, p in enumerate(prompts)]
    lm = load_model(case / "vlm_hf_fused").language_model
    report = {}
    for path in ("batch_invariant_decode", "main_path_decode"):
        if path == "main_path_decode":
            lm._supports_batch_invariant_decode = lambda: False
        single = [run(lm, [s], [p], False)[0] for s, p in zip(seqs, prompts)]
        ragged = run(lm, seqs, prompts, True)
        control = run(lm, [seqs[0], seqs[0]], [20, 20], True)

        def steps(x, t):
            d = np.abs(x - t).max(-1)
            return dict(prompt=float(d[0]), decode=[float(v) for v in d[1:1 + G]],
                        verify=[float(v) for v in d[1 + G:]])
        report[path] = {
            "single_row0_vs_ref": steps(single[0], truth[0]),
            "single_row1_vs_ref": steps(single[1], truth[1]),
            "ragged_row0(pad0)_vs_ref": steps(ragged[0], truth[0]),
            "ragged_row1(pad3)_vs_ref": steps(ragged[1], truth[1]),
            "control_equal_len_row0_vs_ref": steps(control[0], truth[0]),
            "control_equal_len_row1_vs_ref": steps(control[1], truth[0]),
        }
    print(json.dumps(dict(case=case.name, patched=patched, **report), indent=1))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    main(sys.argv[1], "--patched" in sys.argv)
