"""T1 through mlx-vlm's REAL batched generation entry point.

Replicates mlx_vlm.generate.ar.batch_generate's text-only body verbatim
(get_input_embeddings on the left-padded batch + attention mask, per-row
prompt kwargs, BatchGenerator.insert(attention_mask=...), gen.next() loop)
with a stub processor (no tokenizer exists for the tiny model). Greedy, fp32,
config C. Compares generated tokens and their logprobs (plus top-5) with the
transformers reference single-row greedy run, for a ragged batch (prompts 20
and 17, left padding [0, 3]) and an equal-length control.

Usage: python t1_batchgen.py CASE_DIR [--patched]
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

MAX_NEW = 7


def log_softmax(x):
    x = x - x.max(-1, keepdims=True)
    return x - np.log(np.exp(x).sum(-1, keepdims=True))


def generate(model, rows):
    import mlx.core as mx
    from mlx_vlm.generate.ar import BatchGenerator, _split_prompt_kwargs_per_row
    from mlx_vlm.utils import StoppingCriteria
    width = max(len(r) for r in rows)
    ids = np.zeros((len(rows), width), dtype=np.int32)
    mask = np.zeros_like(ids)
    for b, r in enumerate(rows):
        ids[b, width - len(r):] = r
        mask[b, width - len(r):] = 1
    input_ids, mask = mx.array(ids), mx.array(mask)
    # --- batch_generate body (generate/ar.py:3987-4052), text-only ---
    data_kwargs = {}
    embedding_output = model.get_input_embeddings(input_ids, None, mask=mask, **data_kwargs)
    gen_kwargs = {**data_kwargs, **{k: v for k, v in embedding_output.to_dict().items() if v is not None}}
    tok = SimpleNamespace(stopping_criteria=StoppingCriteria([10_000], None))
    gen = BatchGenerator(model.language_model, SimpleNamespace(tokenizer=tok),
                         prefill_batch_size=len(rows), completion_batch_size=len(rows),
                         compute_logprobs=True, top_logprobs_k=5, max_tokens=MAX_NEW,
                         manage_wired_limit=False)
    prompt_kwargs = _split_prompt_kwargs_per_row(gen_kwargs, len(rows))
    uids = gen.insert(input_ids, MAX_NEW, prompt_kwargs=prompt_kwargs, attention_mask=mask)
    out = {u: [] for u in uids}
    while gen.has_work:
        _, responses = gen.next()
        for r in responses:
            out[r.uid].append((int(r.token), float(r.token_logprob), r.top_logprobs))
    return [out[u] for u in uids]


def score(result, prompt_len, seq, ref_logits):
    """Tokens vs reference greedy; logprob error on the first token where
    both agree and on every token while the sequences agree."""
    lp = log_softmax(ref_logits[0].astype(np.float64))
    toks = [t for t, _, _ in result]
    ref_toks = list(seq[prompt_len:prompt_len + len(toks)])
    agree = 0
    while agree < len(toks) and toks[agree] == ref_toks[agree]:
        agree += 1
    errs = [abs(result[i][1] - lp[prompt_len - 1 + i, toks[i]]) for i in range(agree)]
    top5 = []
    for i in range(agree):
        for t, l in (result[i][2] or []):
            top5.append(abs(l - lp[prompt_len - 1 + i, t]))
    return dict(tokens=toks, ref_tokens=ref_toks, tokens_agree_prefix=agree,
                max_logprob_err=max(errs) if errs else None,
                max_top5_logprob_err=max(top5) if top5 else None)


def main(case, patched):
    from mlx_vlm.utils import load_model
    if patched:
        import d1_patch
        d1_patch.apply()
    case = Path(case)
    ref = np.load(case / "ref.npz")
    seqs = [ref["t1_seq0"].tolist(), ref["t1_seq1"].tolist()]
    prompts = [20, 17]
    model = load_model(case / "vlm_hf_fused")
    rep = {}
    single = [generate(model, [s[:p]])[0] for s, p in zip(seqs, prompts)]
    ragged = generate(model, [seqs[0][:20], seqs[1][:17]])
    control = generate(model, [seqs[0][:20], seqs[0][:20]])
    for name, res, which in (("single_A", single[0], 0), ("single_B", single[1], 1),
                             ("ragged_row0_A_pad0", ragged[0], 0), ("ragged_row1_B_pad3", ragged[1], 1),
                             ("control_row0_A", control[0], 0), ("control_row1_A", control[1], 0)):
        rep[name] = score(res, prompts[which], seqs[which], ref[f"t1_logits{which}"])
    print(json.dumps(dict(case=case.name, patched=patched, **rep), indent=1))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    main(sys.argv[1], "--patched" in sys.argv)
