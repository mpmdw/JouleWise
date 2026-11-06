# ALIGN v4 R0 re-run, 2026-11-06: FAIL at the `load` check

Magistrate activation 7a50d0de (Opus 5.5, headless), writing up the run that
activation a90d8f8a launched under RUN_STATE item 179 (1). Not re-run (item 179 (2)).

## Run

- Record `/Users/edr/night-align/r0-v4-20261106T1705Z`, launch id
  `5eb457807c404f3da497bd799f91d92a` (09:03-09:04 PST, 75.5 s wall).
- `report.json` sha256 `857ed2859ee0ef7a82c00e3a3bb425c8325eecf9262a717db86b5577ab91c780`;
  `report.md` sha256 `4adc8d2f1e7135d87aa2781412dcb417ec83eaad94f698f63518c0c083485276`.
- The #684 fix held: `runner.json` runs `$M/.venv/bin/python` unresolved, and model-load passed
  (mlx 0.31.2, mlx_lm 0.31.3, transformers 5.12.1; D artifact folded sha256
  `a8d1c5c9…6b30`, revision `815b83c0…ef9`; active Metal memory 28.58 GB after load).
- Checks: host pass, disk diagnostic, host-identity pass, model-load pass, **load FAIL**:
  teacher-forced NLL on the 2,048 pinned SHADE targets = 11.04 nats/token against the 3.0 limit
  (perplexity 62,119). The short arithmetic prompt answered `42` (coherent = true). Nothing after
  `load` ran, so there is no SMC journal, SMC key classification, rung selection, B7 verdict or
  peak-memory figure.
- D pins (`align_v4_verify_d_pins.py`): prints FAIL; every failing line is one of 41 unpinned files
  under `.cache/huggingface/` (the same 5,782 bytes as before). Revision, sizes and LFS sha256 all
  match. Under the item 179 ruling this counts as a pass. Output: `d-pin-verifier-output.txt`.
- Spotlight: corespotlightd 716 and spotlightknowledged 73957 both in state `S` after the run.
  R0 LaunchAgent gone. Measurement checkout clean at `f3af22b9`.

## Diagnostic (after the run, same model, same venv; scripts in `diagnostics/`)

Each script loads the D weights with `mlx_lm.load` and scores the `nll_prompt_ids` that
`report.json` recorded. About 1 minute each. Nothing in the record or the checkout was changed.

1. **The NLL code is not the cause.** One forward pass over all 2,049 IDs gives 11.07; the
   128-token chunked-cache path R0 uses gives 11.04. Targets are shifted correctly
   (`ids[s+1:e+1]` against logits of `ids[s:e]`).
2. **The token IDs are canonical.** `tok.encode(tok.decode(ids))` returns the identical 2,049 IDs.
3. **The model is fine on other long text.** The first 2,049 tokens of the checkout's README score
   1.9-3.0 nats/token in every 256-token bin. A 217-token plain sentence scores 0.52.
4. **On the pinned prompt the loss grows with position.** 256-token bins:
   4.56, 10.30, 10.36, 8.07, 13.33, 15.26, 15.72, 10.98. That is worse than a uniform guess over
   the 248,077-token vocabulary (ln 248,077 = 12.4). The worst targets are obvious JSON keys
   (`required`, `parameters`, `description`) at 34-39 nats. The top-5 predictions there are
   plausible but wrong nearby tokens (`_user`, ` rule`, `_type`), so the model reads the
   context wrongly.
5. **A prefix causes it, not the text being scored.** Tokens 900-2048 scored after different
   starting points: start 0 → 13.33, start 1 → 13.09, start 40 → 10.33, start 100 → 0.67,
   start 300 → 2.80, start 600 → 0.08, start 900 (no prefix) → 0.32. The response is not
   monotone in prefix length, and the README is fine at the full 2,048 length, so this is not a
   plain context-length limit. Including tokens 40-100 (the end of the system line
   "Reasoning effort is set to xhigh …" and the `# Tools` header) is enough to break it.

**Reading:** the forward pass of this D build (Qwen3.8-27B-8bit, `qwen3_5`, bfloat16 norms,
under mlx 0.31.2 / mlx_lm 0.31.3) gives corrupted next-token distributions on the SHADE system
and tool prompt. The pilots' agents run on exactly this kind of prompt, so the fault would reach
generation too. The `load` check caught what it exists to catch. The likely places to look are
the runtime's handling of this architecture (attention or linear-attention state over this
prefix) and the 8-bit quantization. The controls below test both; nothing in the record, checkout or
pinned venv was changed.

## Controls run after RUN_STATE item 181 (magistrate owns R0 decisions)

Each control used the same pinned text. The other models scored the text after it was
re-encoded with their own tokenizer.

| Control | Script | Mean nats/token | 256-token bins |
|---|---|---|---|
| D, one token per call (recurrent decode path) | `step_diag.py` | 11.06 | 4.55 10.29 10.33 8.07 13.23 15.30 15.75 10.98 |
| D, 16- and 64-token chunks | `step_diag.py` | 11.04, 11.03 | same shape |
| D under mlx 0.32.4 / mlx_lm 0.32.2 (throwaway venv, deleted) | `pos_diag.py` | ≈11 | 4.54 10.30 10.32 7.92 13.09 15.30 15.77 10.99 |
| Qwen3-30B-A3B-4bit anchor (`qwen3_moe`, pinned venv) | `anchor_control.py` | 0.37 | 1.32 0.21 0.60 0.34 0.08 0.01 0.04 0.31 |
| Qwen3.5-122B-A10B-4bit (`qwen3_5_moe`, same hybrid linear-attention family as D) | `anchor_control.py` | 2.35 | 0.97 1.08 1.59 1.22 2.99 4.31 4.45 2.22 |

- The prefill and decode paths agree. A kernel fault in only one of them is ruled out.
- The latest mlx and mlx_lm reproduce the numbers to 0.1 nat per bin, so upgrading the runtime
  does not cure it.
- The mlx stack itself is sound: on the same text, the older-architecture anchor is near-perfect.
- The 122B sibling passes the 3.0 limit, but its loss rises in the same token region where D
  peaks (bins 5-7), on JSON that the anchor predicts at 0.01-0.08. The fault therefore looks
  family-wide (either the `qwen3_5` family on this prompt, or mlx_lm's shared implementation of
  it in both versions), with D's 8-bit build much the worst.
- What is left to tell apart: (a) the D artifact, (b) mlx_lm's `qwen3_5` code in every version,
  (c) the model itself. Doing that needs a reference implementation that is not mlx (HF
  transformers on the upstream bf16 weights, about 54 GB) scoring these same 2,049 IDs. That is
  off this Mac's pinned stack.

**Classification under item 181:** not an infrastructure defect in our code. Every way to cure
it changes the pinned model artifact or the pinned runtime, which is a model change. This
escalates to Ed.
