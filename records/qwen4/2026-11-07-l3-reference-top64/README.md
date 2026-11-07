# Flash-Next (qwen4_exp) bf16 quality reference, top-64 (lead ruling L3)

Closes Saturday operator card B12 / MISSING-6 (F13): the gold-stream reference stands in for a bf16 vLLM host.

- Gold pass: `scripts/run_qwen4_gold_stream.py --reference-chain-only` from `lane/2026-11-06-qwen4exp-quality-ref` @ `92042869a`, finished 2026-11-06 23:4x PST on the M4 Air. Status `REFERENCE_CHAIN_ONLY`: 48 layers, fp32 and bf16, real inputs, no failures (`gold-summary.json`, fingerprint `3d1c04eb…218b`).
- Prompts: `/private/tmp/jwgold-run-l3/prompts.json` sha256 `a3645cd6f11113e0070907966db2bca8ae1b3c6797931dbd5d1001f762a6cd05` (provenance file alongside).
- Capture (same commit): `python3 -B scripts/run_qwen4_quant_quality.py capture --gold-root <gold work> --top-k 64 --output reference-top64.npz`.
- `reference-top64.npz` sha256 `6c9dcb7c2d95974ebffc667cbe9830a9be146cac5e15a15462437c9bc08245f8`; `reference-top64.npz.json` sha256 `2d8b30c0f429b7a7d10a7f8d4c6bd3a0aacdd5990a6d467e080390fad9b203b6`; arrays_sha256 (in the json) `6c9dcb7c2d95974ebffc667cbe9830a9be146cac5e15a15462437c9bc08245f8`.

Use on the 128 GB Mac: `python3 -B scripts/run_qwen4_quant_quality.py score --reference reference-top64.npz --variant-name <name> --model <assembled artifact> --manifest-sha256 <its manifest.json sha256> --output <out.json>` (from a checkout of `92042869a` or later on that lane). `projected_kl` is a lower bound on full-vocabulary KL (top-64 + OTHER).
