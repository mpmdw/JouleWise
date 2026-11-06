# Flash-Next (`qwen4_exp`) decode: static performance pass

Date: 2026-11-06. Scope: synthetic/static analysis only; no checkpoint or
experiment custody was read. The checkout has no MLX/Metal runtime, so this
report deliberately makes no tokens/s or wall-time claim.

## Static profile

The decode hot path is `TextModel.__call__` → 48 `DecoderLayer` calls. The
released layout has 36 linear layers and 12 QSA layers (the configured
full-attention interval is four). The implementation already has the important
fusion boundary:

* each linear layer, including optional PLE, DeltaNet, both hyper-connections,
  and MoE, is one `mx.compile(..., shapeless=False)` call;
* each QSA layer compiles its pre-attention hyper-connection and its
  post-attention hyper-connection + MoE separately, while selection/attention
  remains eager; compiling QSA attention would key the graph on its growing
  host offset and retrace every token;
* parameters and exact-fp32 constants are explicit captured inputs, avoiding
  stale weights and compiled-tape weight retention; mutable recurrent arrays
  enter and leave the compiled linear boundary explicitly.

This gives **60 stable compiled calls/token** (36 linear + 2 × 12 QSA) and 12
eager QSA attention calls/token. Static inspection found no safe cross-layer
fusion: every boundary carries a distinct mutable cache object, and QSA needs
host-side selection between the two compiled pieces. Compiling the Python
layer loop would hide cache mutations after tracing.

The remaining repeated graph construction was the absent-optional-input
sentinel. Every compiled linear layer executed `mx.zeros((0,), dtype=h.dtype)`
before selecting its SSM-mask and PLE arguments. On the released 36-linear-
layer layout that was **36 zero-length MLX graph leaves/token**. The change
creates one sentinel in `TextModel` and shares it through `_Context`, reducing
that count to **1/token (−35, 97.2%)**. Eager, prefill, batch, first-token, QSA,
and value-producing graphs are unchanged. A defensive direct-layer fallback
preserves the old standalone-layer behavior.

## Exact-output contract

The sentinel has shape `(0,)`, the same dtype as the hidden state, and is read
only when an optional argument is absent. `_decode_arrays` continues to map
`size == 0` back to `None`; therefore it cannot enter a numerical operation.
The existing native identity test compares eager and compiled logits plus every
cache array bit-for-bit for 64 steps, after a 2,052-token prefill, on both QSA
mask and gather paths, including snapshot/restore trim. The padded/short-
prefill case covers a real SSM mask and PLE arguments. A new Linux-safe static
regression proves there is exactly one forward allocation site and that layers
consume the context sentinel.

## Reproduction and limits

Static counts were obtained from the checked-in 48-layer schedule and the
control flow above; `python3 -m unittest -v tests.align.test_qwen4_exp_canonical`
runs the structural regression here and skips native cases when MLX is absent.
A native Apple-Silicon closure should rerun the 64-step bitwise tests and record
latency separately; the 97.2% figure is an allocation-site count reduction,
**not** a predicted latency improvement.

The module hash is
`e702b2da3ef23f17a25ce5cd2b608d0ad0c50d644fcb11ed746b69089d4a1d95`;
the converter pin and canonical record were updated together. Existing
artifacts remain immutable and require re-signing a cloned artifact before use.
