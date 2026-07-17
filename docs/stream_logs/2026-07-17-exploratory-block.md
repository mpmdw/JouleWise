# Stream ledger — exploratory measurement blocks (2026-07-17)

Scope: Ed-directed configuration preparation only. No measurement was started.

## EXP-1 — Label and claim boundary

These three blocks follow the FLAGSHIP-001 precedent for production-shaped,
strict-validation-eligible bundles, but their evidence posture is explicitly
`EXPLORATORY` / `L1-legacy`. They are observation-only and carry no claim
framing. Strict bundle validity is an evidence-integrity property, not a claim
upgrade. The D-070 axis-name tags are agenda/indexing tags; they do not assert
that static batching, speculation/MTP, MoE-vs-dense, quantization, or reasoning
length was independently manipulated or identified in these runs.

## EXP-2 — Frozen sequential block order

The directory prefixes and per-block order manifests freeze this sequence:

1. `olmoe-1b-7b`, three contiguous repetitions;
2. `qwen3-4b`, three contiguous repetitions;
3. `qwen35-122b`, three contiguous repetitions.

Each config uses the experiment runner's `repetitions: 3`, yielding three
member bundles with the existing inter-repetition cooldown gate. Do not
interleave the blocks. The operator remains responsible for the quiet-machine
gate and for strict validation of every produced member bundle.

## EXP-3 — Workload parity and tokenizer binding

All blocks preserve the template's five-item `jw_mixed_v1_sentinel` workload,
generator seed/semantics, manifest order, 512-token prompt shape, 256-token
fixed-budget output shape, one warmup run, 10 Hz sampling, 30-second idle
baseline, and 5-second post-warmup settling period.

The template manifest itself is Qwen2.5-tokenizer-bound and contains token IDs
above OLMoE's 50,304-token vocabulary. Reusing it verbatim would pass config
schema validation but fail during OLMoE execution. Therefore the existing
`scripts/gen_jw_mixed.py` generator emitted model-specific manifests and
annotation sidecars from each local tokenizer, inside the authorized campaign
tree. This preserves workload semantics and shape while making the ids-native
prompt path executable and provenance-bound for each model.

Schema 0.1 has no supported chat-template or thinking-mode field. Qwen3-4B
therefore uses the ids-native raw-token prompt path, which bypasses its chat
template and avoids thinking mode; no unknown config key is introduced.

## EXP-4 — Model identity notes

- OLMoE uses upstream revision
  `6d84c48581ece794365f2b8e9cfb043c68ade9c5`. Its local `config.json` is
  intentionally patched with the verified Transformers default
  `rms_norm_eps=1e-05`; the patched file SHA-256 is
  `a57cfd3b1e587296e4e61e68acd467c3acdf7d70f34f51744c2bf826325b649c`.
- Qwen3-4B uses the local D-074 candidate mirror at revision
  `4dcb3d101c2a062e5c1d4bb173588c54ea6c4d25`.
- Qwen3.5-122B-A10B uses the existing FLAGSHIP-001 mirror at revision
  `e9c67b08899964be5fdd069bb1b4bc8907fe68f5`.

## EXP-5 — Planning wall-clock estimates

Each measured bundle includes 30 seconds idle, 5 seconds post-warmup settling,
a four-token adapter warmup, five 512-token prefills, and 1,280 measured output
tokens. A three-bundle block also has two cooldown gates; nominal recovery is
about 30 seconds per gate, while the fail-closed cap is 300 seconds per gate.

| Sequential block | Nominal planning estimate | Basis |
|---|---:|---|
| OLMoE-1B-7B | 3.5–4.5 min | No harness throughput receipt yet; allows roughly 80–160 tok/s plus BF16 load/prefill overhead. |
| Qwen3-4B | 3.3–4.2 min | Anchored to the dated 113 tok/s local greedy feasibility observation, with suite prefill/load margin. |
| Qwen3.5-122B-A10B | 4.5–5.5 min | Anchored to FLAGSHIP-001's 46 tok/s and 12.8 s warm-cache load receipt. |

If both cooldowns hit their 300-second caps, add up to about 9 minutes to a
nominal block estimate. These are scheduling estimates, not measured campaign
results.

## EXP-6 — Execution handoff

Run the three subdirectories in numeric order with the production campaign
runner. Do not execute while any agent session is active. Afterward, validate
every member bundle with `validate-bundle --strict`; retain EXPLORATORY/L1-legacy
labels regardless of strict validity.
