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

The compact record contains, for every token, the reference top 64 token ids
and logits, full-vocabulary log-sum-exp, and the teacher-forced next-token
logit.  Top-1, top-5 overlap, and NLL delta are therefore exact.  **Top-k plus
log-sum-exp cannot determine full-vocabulary KL**: it omits the allocation of
probability within the tail.  The reported `projected_kl` is the exact
`KL(bf16 || quant)` after deterministically mapping the vocabulary to the 64
retained tokens plus one `OTHER` bucket.  By data processing it lower-bounds
full-vocabulary KL.  Calling it full KL would be a false precision claim.

## Pre-registered decision table

All five conditions in a row must pass.  Classification uses the first passing
row and is embedded in every result; thresholds must not be edited after seeing
Saturday's variants.

| Label | mean projected KL | p99 projected KL | top-1 agreement | mean top-5 intersection / 5 | mean NLL delta (quant − bf16) |
|---|---:|---:|---:|---:|---:|
| acceptable | ≤ 0.020 nat | ≤ 0.100 nat | ≥ 0.90 | ≥ 0.90 | ≤ 0.05 nat/token |
| marginal | ≤ 0.050 nat | ≤ 0.250 nat | ≥ 0.80 | ≥ 0.80 | ≤ 0.15 nat/token |
| reject | otherwise | otherwise | otherwise | otherwise | otherwise |

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
and therefore are not recycled as a quality threshold.

For ALIGN use, only `acceptable` is admitted.  `marginal` means retain for
diagnosis or try a less aggressive profile; it is not an acceptance.  `reject`
must not be used.  Because projected KL is a lower bound and the prompt set is
small and synthetic, an acceptable result is necessary but not sufficient for
broad model-quality claims.

## Saturday commands (128 GB MacBook Pro)

Run from a clean checkout containing this harness after the live-kit branch has
assembled and validated the `maxfit` model.  Set the two paths to the actual
gold run and conversion output produced by that kit.  Fetching the kit is shown
for provenance; return to the harness checkout before running the commands if
the harness has not yet been merged into that lane.

```bash
cd ~/code/JouleWise
git fetch origin lane/2026-11-07-qwen4exp-mbp-live
git rev-parse FETCH_HEAD                 # retain this live-kit commit in notes
git switch work                          # branch containing this harness

export GOLD_RUN=/Volumes/ALIGN/qwen4-gold-work   # stream --work folder (holds manifest.json)
export MAXFIT=/Volumes/ALIGN/qwen4-maxfit
export QQ=/Volumes/ALIGN/qwen4-quant-quality
mkdir -p "$QQ"

# 1. Capture once from the official bf16 reference chain (bf16 is not loaded).
python3 -B scripts/run_qwen4_quant_quality.py capture \
  --gold-root "$GOLD_RUN" \
  --top-k 64 \
  --output "$QQ/reference-top64.npz"

# 2. Score maxfit. The model is loaded lazily; prompts are teacher-forced.
python3 -B scripts/run_qwen4_quant_quality.py score \
  --reference "$QQ/reference-top64.npz" \
  --adapter joulewise.align.qwen4_quant_mlx_adapter:teacher_forced_logits \
  --model "$MAXFIT" \
  --manifest-sha256 "$MAXFIT_MANIFEST_SHA256" \
  --variant-name maxfit-g64 \
  --output "$QQ/maxfit-g64.json"

# 3. Verify the immutable classification and identities.
python3 - <<'PY'
import json, os
p=os.path.join(os.environ['QQ'], 'maxfit-g64.json')
r=json.load(open(p))
print(json.dumps(r['summary'], indent=2))
print('CLASSIFICATION:', r['classification'])
raise SystemExit(r['classification'] != 'acceptable')
PY
```

To score another assembled directory, repeat step 2 with a new `--model`,
`--variant-name`, and output JSON.  Do not rerun capture.  For an explicitly
pinned prompt set, run the gold stream with `--prompts-json FILE` (for example
the hosted/NLL continuations written by
`scripts/qwen4exp_gold_logprob_compare.py prepare` + `prompts-json`); capture
then inherits those prompts from the run.  A `--prompts-json` given to capture
or score is only a cross-check and must match exactly.  The default adapter
loads the artifact once through the live kit's pinned
`align_convert_qwen4_exp.load_verified_model`, so `--manifest-sha256` is
required.  CI/tiny-oracle tests can instead pass
an NPZ containing one `[sequence,vocabulary]` float array under each prompt
name via `--logits-npz`.

### Capacity plan

Estimates use the current two gold prompts (17 positions), top-k 64, and the
live kit's documented approximately 210 GB assembled maxfit directory.  Check
actual sizes with `du -sh`; APFS/cache behavior and the final vocabulary size
can move the figures.

| Step | Additional disk | Peak unified memory | Reason / guard |
|---|---:|---:|---|
| Existing gold run | no new disk; gold head arrays about 0.1 GB | none for capture setup | Official streamed run already paid for bf16 shard staging; no bf16 model is opened here. |
| Capture | under 1 MB compact record (allow 10 MB with JSON/temp) | about 0.25 GB | One prompt's float32 head array, sorting workspace, and top-64 record; prompts are processed sequentially. Keep ≥1 GB free. |
| Existing assembled maxfit | about 210 GB on disk | lazy | Includes the approximately 102 GB PLE table documented by the conversion kit. It belongs on a volume with at least 230 GB available during assembly. |
| Score | result normally under 1 MB | budget **≤124 GB**, leaving ≥4 GB for macOS | Lazy model plus one prompt's logits/sort workspace. Stop rather than swap if Activity Monitor pressure turns red or resident use approaches 124 GB. No bf16 allocation coexists. |
| Each later variant | its model directory + under 1 MB result | same ≤124 GB, serially | Reuses the compact reference; never run variants concurrently. |

The adapter copies logits to host and clears the MLX cache after each prompt.
This bounds transient logits but cannot make an assembled model whose resident
quantized weights exceed the laptop fit; the conversion's own full-model load
validation remains the prior gate.  Run the score as an interactive ALIGN
check, not alongside a quiet energy-measurement window.

## Artifact interpretation

The reference sidecar binds the NPZ SHA-256, source pointer, prompts, shapes,
and top-k.  A changed or truncated NPZ fails closed.  Each score binds the
reference hash, variant name/path, policy, aggregate metrics, and every token's
metrics.  NLL has `sequence_length - 1` observations because the final input
token has no pinned next-token target.  A non-finite or wrong-shaped variant
fails rather than being classified.
