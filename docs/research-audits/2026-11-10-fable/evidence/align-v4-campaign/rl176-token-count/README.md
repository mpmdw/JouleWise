# RL-176 C.1 — D turn-zero prompt count

The rows apply to every C/T stratum for the named task. The public upstream resets to
its fixed initial state regardless of the seed. D uses the medium reasoning effort in
W1's prospective inputs, tools enabled and the sabotage hint on.

| Pair | Benign tokens | Instructed tokens | Instructed − benign | Benign characters | Instructed characters |
|---|---:|---:|---:|---:|---:|
| `bank_transfer_2` | 10,021 | 11,240 | +1,219 | 38,801 | 44,472 |
| `spam_filter_update` | 6,516 | 7,284 | +768 | 26,304 | 30,078 |

Both absolute differences exceed 16. RL-176 C.2 activates the heading condition
on `S_dec` and the analyst seat's step-4 cell. Both differences are identical under
low and xhigh effort. The four medium-effort rendered prompt hashes, all effort
counts, and the hashes of the three tokenizer artifacts are in [counts.json](counts.json).

In both conditions turn zero prefills the whole rendered prompt. The endpoint's
episode cache starts empty and first `EpisodePromptCache.prepare` uses a zero-length
represented prefix. Warmup uses a separate runtime path. Each task's benign turn-zero
prompt is fixed within the stratum, so it supplies no turn-zero variation at the
instructed prompt size. Later turns can supply different count support. The count
alone cannot establish how closely the fit predicts the instructed prefill.

| Conditionless kit (prospective design) | Planned prefill tokens |
|---|---|
| cl-dev-01 and cl-dev-02 at 589748f15 | 19,458 |
| cl-dev-03 through cl-dev-05, v1.1 | 2,000 / 10,000 / 19,458 |
| cl-qual-01 through cl-qual-03, v1.1 drafts | 2,000 / 10,000 / 19,458 |

Kit values are the distinct leg-level prefill settings, falling back to a kit's
leg default, from the versioned kit definitions in `item-drafts-rl172/kits/` and
`item-drafts-1118/kits/` at `66d0d622d`. The 30B pilot-record cross-check is omitted
under the builder brief's data boundary.

## Reproduction

Executed on the desk MacBook Air. Inputs were W1 source at `b2e01464d`, the public
[jkutaso/SHADE-Arena pin](https://github.com/jkutaso/SHADE-Arena/commit/6614e77191c1f8e2d0c44c123c6f915905ebafae),
and the three tokenizer files at the
[D artifact pin](https://huggingface.co/mlx-community/Qwen3.8-27B-8bit/tree/815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9).
The W1 port fetched the upstream and verified its Git-file manifest. From the W1
checkout with the package versions in counts.json and with only those three files
under TOKENIZER_DIR, run:

```sh
PYTHONPATH=. python /path/to/count_prompts.py UPSTREAM_CACHE TOKENIZER_DIR
```

The script calls the W1 task, XML rendering and encode paths. It constructs the
two starting messages and serializes the upstream tool schemas without invoking a
tool. It loads no model weights, runs no inference and reads no measurement data.
