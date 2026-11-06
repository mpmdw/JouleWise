# 2026-11-06 — MISSING-11 compiled decode

Implemented a per-decoder-layer `mx.compile(..., shapeless=False)` boundary for
batch-one, one-token decode. Prefill remains eager. Mutable device cache arrays,
RoPE values, the SSM mask and PLE rows are explicit compiled inputs; cache arrays
are explicit outputs. The linear-layer graph retains a stable shape across
tokens. QSA carries an offset-shaped input because its existing cache protocol
uses the host offset for slicing and selection.

The canonical native test now compares compiled and eager logits and every cache
array over 64 decode steps, for linear, PLE and QSA layers, after a 2052-token
prefill and across a snapshot restore/QSA trim. It skips in the Linux sandbox,
which has no MLX/Metal.

The module pin is `027dc03a36cff5455a436bc609537e72643b727f04b1eff93198721f36849564` (it was `af26a5a5…` before the review fixes below).
Existing artifacts remain immutable: step 8 must clone an artifact, replace only
the module and manifest, and re-attest the gold units under the new pins.

## Verification

- `python3 -m py_compile joulewise/align/models/qwen4_exp.py tests/align/test_qwen4_exp_canonical.py` — pass.
- `python3 -m unittest -v tests.align.test_qwen4_exp_canonical` — 32 tests,
  all skipped because MLX is absent.
- `python3 -m unittest discover -s tests` — interrupted after the broad suite
  entered an unrelated long-running B5 analysis test; one pre-existing failure
  had already been reported without details by unittest's buffered progress.

Native lead gate: run the canonical module (33 tests, zero skips), then the
Saturday step-8 gold-adapter tiny and live tiny commands against the cloned
artifact on `/Volumes/JW-EXT`. No real weights were used in this session.

## Review fixes (2026-11-06, native M4 Air, tiny fixtures only)

The unreviewed head `0715fdf74` had never run natively. On mlx 0.31.2 / Metal:

- BLOCKER: the first compiled step raised `[eval] Attempting to eval an array
  without a primitive`. The trace bound its tracer placeholders (cos, sin,
  SSM mask) into the forward's shared `_Context`, so every later layer
  received placeholders as real inputs. The trace now binds them on a private
  copy.
- HIGH: with that fixed, compiled logits differed from eager by ~1e-6 (fp32)
  on every linear-attention layer. mlx 0.31.2 inlines scalar constants into
  fused kernels with 7 significant digits; `Dk ** -0.5` (l2norm) and
  `sqrt(hidden)` (PLE gate) became different fp32 values. They are now
  `EXACT_F32` compile inputs (eager arithmetic unchanged).
- MEDIUM: every QSA layer retraced at every token (offset-shaped argument):
  slower than eager, and active memory grew with every step (+4.3 MB per 300
  steps on the tiny fixture, vs +0.6 MB eager) because each trace stays in
  mlx's compile cache. QSA layers now compile only the hyper-connections and
  the MoE; attention is eager. One trace per layer piece; memory growth equals
  eager.

Tests: the identity test now also runs the gather path, asserts one trace per
layer piece, and a new test covers a left-padded single row and a prefill
shorter than one QSA block. Both fail on `0715fdf74`.
