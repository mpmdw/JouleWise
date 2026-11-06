# Qwen3.8-Flash-Next quantization-quality harness

## Purpose and non-claim

This harness compares teacher-forced final-layer logits from the Saturday
`maxfit` MLX build with the pinned bf16 official-reference chain.  It does not
keep the bf16 model resident: `capture` reads the already-produced gold `head`
arrays one prompt at a time and emits a small, reusable reference.  `score`
then loads only a quantized model.  `capture --gold-root` takes the prompts
from the gold run's own `parity/provenance.json` and every head output from
the stream `manifest.json` (`units.head` must be `done`; each
`chain.head["bf16:<prompt>"]` file must match its recorded SHA-256), so the
two harnesses cannot silently drift.  `score` always scores the prompts pinned
in the reference sidecar.

Chain paths are resolved against the manifest's own folder, so a gold work
folder that was moved or copied (or reached as /tmp rather than /private/tmp)
still opens; a recorded path that is not a pinned artifact is refused.  Head
outputs are hash-checked and memory-mapped when their prompt is read, and
`capture`/`score` work on at most 64 rows of a `[positions, 248320]` array at
a time.  Quantized logits from the adapter are likewise computed per prompt
on demand, so one prompt's logits are alive at a time.

The compact record contains, for every token, the reference top 64 token ids
and logits, full-vocabulary log-sum-exp, and the teacher-forced next-token
logit.  Top-1, top-5 overlap, and NLL delta are therefore exact.  **Top-k plus
log-sum-exp cannot determine full-vocabulary KL**: it omits the allocation of
probability within the tail.  The reported `projected_kl` is the exact
`KL(bf16 || quant)` after deterministically mapping the vocabulary to the 64
retained tokens plus one `OTHER` bucket.  By data processing it lower-bounds
full-vocabulary KL.  Calling it full KL would be a false precision claim.

## Pass rules

Lead ruling L3 (docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-1.md on
`lane/2026-11-06-align-v4-design-council`) merges the two quantization pass
rules into this one table.  The quant-quality `POLICY`
(`joulewise.align.qwen4_quant_quality.POLICY`) is **primary**: scored
teacher-forced against the bf16 quality reference, it alone admits a
quantized variant.  The e2e profile thresholds
(`scripts/qwen4exp_e2e_eval.py` `THRESHOLDS["profiles"]`) are **secondary
screens**: they are still computed and reported, never decisive.  Every
quality report records the primary rule: quant-quality scores (`pass_rule`),
the full-vocabulary cross-check `scripts/qwen4exp_gold_logprob_compare.py
compare` (`classification`, `pass_rule`, `e2e_screen`) and e2e results files
(`quality_policy`).

| Metric (vs the bf16 gold reference unless noted) | POLICY `acceptable` (primary; admits) | POLICY `marginal` (diagnosis only) | e2e screen `maxfit` / `maxfit5` (secondary) | e2e screen `bf16` (secondary) |
|---|---:|---:|---:|---:|
| mean KL(bf16 ‖ quant), nat | ≤ 0.020 (projected) | ≤ 0.050 | ≤ 0.05 (hosted, bucketed) | ≤ 0.03 |
| p99 KL, nat | ≤ 0.100 | ≤ 0.250 | — | — |
| top-1 agreement | ≥ 0.90 | ≥ 0.80 | ≥ 0.95 (hosted greedy) | ≥ 0.97 |
| mean top-5 intersection / 5 | ≥ 0.90 | ≥ 0.80 | top-k overlap ≥ 0.85 | ≥ 0.90 |
| hosted token in local top 5 | — | — | ≥ 0.99 | ≥ 0.995 |
| mean NLL delta (quant − bf16), nat/token | ≤ 0.05 | ≤ 0.15 | NLL ≤ ref × 1.02 + 0.02 | ≤ ref × 1.01 + 0.02 |
| benchmark slack (binomial floor) | — | — | 0.01 | 0.00 |

Reading the table:

- All five POLICY conditions in a row must pass; classification uses the first
  passing row, otherwise `reject`.  Thresholds must not be edited after seeing
  Saturday's variants.
- Only `acceptable` is admitted.  `marginal` means retain for diagnosis or try
  a less aggressive profile; it is not an acceptance.  `reject` must not be
  used.  `compare` exits 0 only for `acceptable`.
- `compare` measures exact full-vocabulary KL, which is ≥ the projected KL
  POLICY bounds, so applying the POLICY bars to it is the conservative reading.
- A variant that passes a secondary screen but not POLICY fails; a variant
  that passes POLICY but fails a secondary screen is flagged for the lead
  (the screens compare against an FP8 hosted model or model-card numbers, not
  against the bf16 reference).

These are conservative **ALIGN engineering allowances**, not literature-wide
accuracy standards.  The NLL bars correspond to perplexity multipliers of
`exp(.05)=1.051` and `exp(.15)=1.162`.  The strict row is deliberately close
to the “negligible degradation” regime targeted by post-training methods:
[GPTQ](https://arxiv.org/abs/2210.17323) reports accurate 3–4 bit weight-only
compression, [SmoothQuant](https://arxiv.org/abs/2211.10438) targets
accuracy-preserving W8A8 inference, and [AWQ](https://arxiv.org/abs/2306.00978)
protects salient weights to reduce quantization loss.  None supplies universal
KL or agreement cutoffs, so those papers motivate measuring task output rather
than pretending to justify these exact numbers.  The p99 bound prevents a good
mean from hiding a few badly changed positions.  Gold's bf16 numerical
allowances validate implementation parity, not quantized semantic quality,
and therefore are not recycled as a quality threshold.  Because projected KL
is a lower bound and the prompt set is small, an acceptable result is
necessary but not sufficient for broad model-quality claims.

## The bf16 quality reference (second gold pass, lead ruling L3)

The parity gold stream (`/private/tmp/jwgold-run-a2`, pid 3097) runs the two
DEFAULT_PROMPTS (17 positions of arbitrary token ids).  It stays the
layer-parity validation; its head unit is no quality reference.  A second
streamed pass on the laptop captures the reference on real text:

- prompts: the 12 hosted-reference prompts
  (`configs/qwen4_exp_port/hosted_reference_prompts.json`), rendered by the
  pinned official chat template with thinking off, each followed by a fixed
  natural-text continuation cut from the sha256-pinned public-domain excerpts
  in `configs/qwen4_exp_port/e2e_items.json` (table `CONTINUATIONS` in
  `scripts/qwen4exp_quality_ref_prompts.py`), **never** from maxfit's own
  greedy output;
- each prompt ≤ 512 tokens (continuations 128 tokens; the long-context prompt
  keeps whole paragraphs of its passage up to the budget; the tool prompt's
  continuation shrinks to fit), tokenized by the official tokenizer at
  revision `de4b8e4d43b917e7706784d8bb445c9af86a3540`;
- `scripts/run_qwen4_gold_stream.py --reference-chain-only --prompts-json`:
  the official reference forward only, real inputs, both dtypes (bf16 is the
  reference; fp32 is the precision floor for `compare`), no MLX worker and no
  random-input cases.  Each case's traces are pruned to its `output.npy`, and
  a unit's chain is deleted once its successor commits.  Only the head unit
  (the logits) and the live chain stay on disk.  The pass is resumable like
  the parity pass (pruned cases are re-pinned, so `--resume` reuses them).

### Laptop command (run after pid 3097's parity pass finishes)

```bash
# 0. Wait for the parity pass; never overlap the two (CPU, disk, HF staging).
while kill -0 3097 2>/dev/null; do sleep 300; done
test -f /private/tmp/jwgold-run-a2/work/summary.json && df -g /private/tmp   # need >= 45 GB available

# 1. A checkout of this branch (worktree under jw-wt, removed afterwards).
git -C /Users/edr/code/CapstoneProject/jw-wt/handoff fetch origin lane/2026-11-06-qwen4exp-quality-ref
git -C /Users/edr/code/CapstoneProject/jw-wt/handoff worktree add --detach \
  /Users/edr/code/CapstoneProject/jw-wt/qwen4exp-qref-run FETCH_HEAD
cd /Users/edr/code/CapstoneProject/jw-wt/qwen4exp-qref-run
export QREF=/private/tmp/jwgold-qref && mkdir -p "$QREF"
PY=/private/tmp/jwsol/venv-ref/bin/python        # transformers 5.22.1 + huggingface_hub

# 2. Tokenizer at the pinned revision, then the prompts (CPU only, < 1 min, ~15 MB).
$PY -B scripts/qwen4exp_quality_ref_prompts.py fetch-tokenizer --dest "$QREF/tokenizer"
$PY -B scripts/qwen4exp_quality_ref_prompts.py build --tokenizer-dir "$QREF/tokenizer" \
  --out "$QREF/prompts.json"                     # prints total_tokens; also writes prompts.json.provenance.json

# 3. Same pins and budgets as the parity pass, plus the L3 mode.
STREAM=($PY -B scripts/run_qwen4_gold_stream.py --work "$QREF/work" --reference-chain-only
  --prompts-json "$QREF/prompts.json"
  --ref-python /private/tmp/jwsol/venv-ref/bin/python --mlx-python /private/tmp/jwsol/venv-both/bin/python
  --mlx-module "$PWD/joulewise/align/qwen4_gold/canonical_adapter.py"
  --adapter-dependency /private/tmp/jw-gold-canonical-65763077/qwen4_exp.py
  --adapter-dependency /private/tmp/jw-gold-canonical-65763077/canonical_converter.py
  --shared-shards restage --min-free-gb 25 --max-staging-gb 12 --max-gb 12 --timeout 3600)
"${STREAM[@]}" --plan-only                       # config/index pins + storage plan; no shard download

# 4. The pass. Resumable: after any stop, rerun this same line.
nohup nice -n 10 "${STREAM[@]}" --resume > "$QREF/run.log" 2>&1 &
```

Done when `run.log` ends with `{"status": "REFERENCE_CHAIN_ONLY", ...}` and
`$QREF/work/summary.json` exists.  Then remove the run worktree
(`git -C .../handoff worktree remove .../qwen4exp-qref-run`); `$QREF/work`
holds the reference.  The MLX module and adapter dependencies are only
fingerprinted in this mode; no MLX worker starts.

**Disk** (T = `total_tokens` printed by `build`; about 2,300–2,600 for the
12 prompts):

| Item | Size |
|---|---:|
| HF staging (restaged unit subsets, cap) | ≤ 12 GiB |
| Head unit outputs, kept (fp32 + bf16, `[T, 248320]` float32) | T × 1.99 MB ≈ 5 GB |
| Live chain (2 units × 2 dtypes × `[T, 10240]` float32) | T × 164 kB ≈ 0.4 GB |
| One case's traces before pruning (≤ 512 tokens) | ≤ 0.5 GB |
| Sparse PLE rows, JSON, logs | < 0.5 GB |
| **Peak work folder** | **≈ 19 GB**, plus the 25 GiB free-disk reserve: start with ≥ 45 GB free |
| Downloaded over the pass (restage policy, same as the parity pass) | 462 GB (none retained) |

Without pruning the same pass would keep about 1 MB per token per unit
(≈ 130 GB for T = 2,500), which does not fit the laptop; that is why the mode
exists.

**Time.** The parity pass ran its first 23 units in 3.9 h: about 5–7 min per
layer unit (16 worker calls on 17 tokens plus about 1–3 min of downloads),
and 57 min for the unit that stages the PLE table.  The quality pass makes
24 reference calls per unit (12 prompts × 2 dtypes) on ~150–510 tokens each,
estimated at 15–35 s per call (process start and expert slicing dominate at
17 tokens; the fp32/bf16 CPU forward grows with tokens).  Estimate: downloads
≈ 2 h + PLE staging ≈ 1 h + compute 5–12 h, so **≈ 10 h (8–15 h)**.
Calibrate from the log once unit 2 has finished: (minutes for unit 2) × 47 +
the time already spent.

**Capture afterwards** (laptop, CPU, ~1 min, ~1 GB peak, < 15 MB output):

```bash
python3 -B scripts/run_qwen4_quant_quality.py capture --gold-root "$QREF/work" \
  --top-k 64 --output "$QREF/reference-top64.npz"
```

Copy `reference-top64.npz` and its `.json` sidecar to
`/Volumes/JW-EXT/flashnext/quant-quality/` on the MacBook Pro; `score` needs
only those two files.  For the exact full-vocabulary cross-check
(`qwen4exp_gold_logprob_compare.py compare`) also keep `$QREF/work` (its head
outputs, ≈ 5 GB) and pass `--prepared "$QREF/prompts.json"` to add the
continuation-only group.  `qwen4exp_gold_logprob_compare.py prepare`
(maxfit greedy continuations) must not feed the gold pass.

## Saturday commands (128 GB MacBook Pro)

Run from a checkout containing this harness after the live kit has assembled
and validated the `maxfit` model on `/Volumes/JW-EXT`.  The MLX adapter
applies the kit's guards itself: it refuses while launchd measurement agents
are loaded, requires the artifact and every PLE table it pages to be on
`/Volumes/JW-EXT`, sets the Metal memory limit to min(115.4 GB, the device's
recommended working set) and a 256 MiB cache limit before loading, and
checks the Metal peak and the 21.5 GB PLE resident-page cap after load and
after every prompt.

```bash
export QQ=/Volumes/JW-EXT/flashnext/quant-quality      # holds reference-top64.npz(.json)
export MAXFIT=/Volumes/JW-EXT/flashnext/maxfit          # the kit's verified conversion
export MAXFIT_MANIFEST_SHA256=...                       # from the kit's convert.json

# Score maxfit. The model is loaded once; prompts are teacher-forced one at a time.
python3 -B scripts/run_qwen4_quant_quality.py score \
  --reference "$QQ/reference-top64.npz" \
  --adapter joulewise.align.qwen4_quant_mlx_adapter:teacher_forced_logits \
  --model "$MAXFIT" \
  --manifest-sha256 "$MAXFIT_MANIFEST_SHA256" \
  --variant-name maxfit-g64 \
  --output "$QQ/maxfit-g64.json"

# Verify the immutable classification and identities.
python3 - <<'PY'
import json, os
r = json.load(open(os.path.join(os.environ['QQ'], 'maxfit-g64.json')))
print(json.dumps(r['summary'], indent=2))
print('CLASSIFICATION:', r['classification'])
raise SystemExit(r['classification'] != 'acceptable')
PY
```

Use the live kit's Python (`mlx`, `mlx-lm`, `transformers` 5.22.1).  To score
another assembled directory, repeat with a new `--model`, `--variant-name`,
and output JSON.  Do not rerun capture.  A `--prompts-json` given to capture
or score is only a cross-check and must match exactly.  The default adapter
loads the artifact through the kit's pinned
`align_convert_qwen4_exp.load_verified_model`, so `--manifest-sha256` is
required.  CI/tiny-oracle tests can instead pass an NPZ containing one
`[sequence,vocabulary]` float array under each prompt name via
`--logits-npz`.

### Capacity plan

| Step | Additional disk | Peak unified memory | Reason / guard |
|---|---:|---:|---|
| Quality-reference gold pass (laptop) | ≈ 19 GB peak, ≈ 5 GB kept | reference worker ≤ 12 GiB cap (parity pass peaked < 1 GB RSS) | See above; runs after the parity pass. |
| Capture (laptop) | < 15 MB compact record | ≈ 1 GB | One prompt's head output memory-mapped, 64 rows at a time in float32. |
| Existing assembled maxfit | about 210 GB on JW-EXT | lazy | Includes the approximately 102 GB PLE table documented by the conversion kit. |
| Score (MacBook Pro) | result under 5 MB | Metal cap min(115.4 GB, recommended set) | Lazy model plus one prompt's logits (≤ 512 × 248320 float32 ≈ 0.5 GB) and a 64-row sort workspace. Stops on the Metal peak or the PLE resident cap. |
| Each later variant | its model directory + result | same, serially | Reuses the compact reference; never run variants concurrently. |

The adapter copies logits to host and clears the MLX cache after each prompt.
This bounds transient logits but cannot make an assembled model whose resident
quantized weights exceed the laptop fit; the conversion's own full-model load
validation remains the prior gate.  Run the score as an interactive ALIGN
check, never alongside an energy-measurement window.

## Artifact interpretation

The reference sidecar binds the NPZ SHA-256, source pointer, prompts, shapes,
and top-k.  A changed or truncated NPZ fails closed.  Each score binds the
reference hash, variant name/path, policy, aggregate metrics, and every token's
metrics.  NLL has `sequence_length - 1` observations because the final input
token has no pinned next-token target.  A non-finite or wrong-shaped variant
fails rather than being classified.
