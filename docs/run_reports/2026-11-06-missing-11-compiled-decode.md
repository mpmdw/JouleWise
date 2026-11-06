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

The module pin is `af26a5a5bf15a6c475f21637989c5f03c6f8bd3a3e0b8824ac99765a99f7f95f`.
Existing artifacts remain immutable: step 8 must clone an artifact, replace only
the module and manifest, and re-attest the gold units under the new pins.

## Verification

- `python3 -m py_compile joulewise/align/models/qwen4_exp.py tests/align/test_qwen4_exp_canonical.py` — pass.
- `python3 -m unittest -v tests.align.test_qwen4_exp_canonical` — 32 tests,
  all skipped because MLX is absent.
- `python3 -m unittest discover -s tests` — interrupted after the broad suite
  entered an unrelated long-running B5 analysis test; one pre-existing failure
  had already been reported without details by unittest's buffered progress.

Native lead gate: run the canonical module (32 tests, zero skips), then the
Saturday step-8 gold-adapter tiny and live tiny commands against the cloned
artifact on `/Volumes/JW-EXT`. No real weights were used in this session.
