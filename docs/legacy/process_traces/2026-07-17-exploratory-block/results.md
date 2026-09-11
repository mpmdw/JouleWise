# EXPLORATORY block — verified bundle extraction (2026-07-17)

Status: **EXPLORATORY / L1-legacy observation only; not claim evidence.** The
nine retained bundles are strict-valid and collection-usable, but every bundle
is claim-evidence-flagged. The three model/configuration points are unmatched,
the repetition count is below the headline protocol, and none of the
comparisons below is a promoted model, architecture, quantization, or
efficiency claim.

Measurement boundary for every energy value: **Apple M3 Max / powermetrics SoC
rails (CPU + GPU + ANE)**. Following D-067, gross energy is listed first.
Idle-subtracted energy and the stored idle-subtracted per-output-token metric
are labeled within-device secondary views.

## Extraction method and denominator

Each bundle executed the same five-item `jw_mixed_v1_sentinel` shape. Every
item carried 512 model-tokenizer-specific prompt tokens and emitted the exact
fixed budget of 256 generated tokens. The realized denominator is therefore
2,560 prompt tokens plus 1,280 generated output tokens, or 3,840 total tokens
per bundle. The bundle `summary_metrics.json` files record
`token_count_source=runtime_observed` and five item-level
`emitted_tokens=256` rows; the bundle manifests and `suite_items.jsonl` files
record the 512/256 shape and realized counts. Denominator evidence:
[O1 summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/summary_metrics.json),
[O1 manifest](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/suite_manifest.json),
[Q1 summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/summary_metrics.json),
[Q1 manifest](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/suite_manifest.json),
[F1 summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r1/summary_metrics.json), and
[F1 manifest](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r1/suite_manifest.json).

Two similarly named reducer fields have different denominators:

- `energy_output_token_j` is idle-subtracted request energy divided by the
  1,280 generated output tokens. It is the stored per-generated-token metric
  reported below as a within-device secondary view.
- `energy_token_j` is idle-subtracted request energy divided by all 3,840
  prompt-plus-output tokens. It is not the requested per-generated-token
  metric and is not used below.
- Gross mJ/generated output token is derived here as
  `1000 * gross_energy_j / 1280`, preserving D-067's gross-first posture.

## Per-model extraction

“Spread” is the sample standard deviation `s`; the parenthetical range is the
minimum–maximum across r1–r3. Means and sample standard deviations independently
reproduce the retained experiment aggregates. Every row is backed by the three
named bundle summaries in its evidence cell.

| model/configuration | gross suite energy, J — M3 Max / SoC rails, mean ± s (range) | gross mJ/generated output token — same boundary, mean ± s (range) | idle-subtracted suite energy, J — same boundary, secondary, mean ± s (range) | idle-subtracted mJ/generated output token — same boundary, secondary, mean ± s (range) | runtime-observed output tok/s, mean ± s (range) | bundle evidence |
|---|---:|---:|---:|---:|---:|---|
| OLMoE-1B-7B-0924, BF16 | 229.028 ± 2.445 (227.141–231.790) | 178.928 ± 1.910 (177.454–181.086) | 227.712 ± 1.877 (226.184–229.808) | 177.900 ± 1.467 (176.706–179.537) | 122.361 ± 0.111 (122.261–122.481) | [O1](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/summary_metrics.json), [O2](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r2/summary_metrics.json), [O3](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r3/summary_metrics.json) |
| Qwen3-4B-4bit, INT4 group 64 | 362.772 ± 0.131 (362.642–362.903) | 283.416 ± 0.102 (283.314–283.518) | 361.354 ± 0.517 (360.800–361.825) | 282.308 ± 0.404 (281.875–282.675) | 106.519 ± 0.042 (106.470–106.545) | [Q1](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/summary_metrics.json), [Q2](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r2/summary_metrics.json), [Q3](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r3/summary_metrics.json) |
| Qwen3.5-122B-A10B-4bit, INT4 group 64 | 1072.273 ± 11.882 (1061.722–1085.144) | 837.713 ± 9.283 (829.471–847.769) | 1064.688 ± 16.667 (1048.728–1081.982) | 831.787 ± 13.021 (819.319–845.298) | 39.473 ± 0.113 (39.349–39.569) | [F1](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r1/summary_metrics.json), [F2](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r2/summary_metrics.json), [F3](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r3/summary_metrics.json) |

The raw repetition values used in those aggregates are preserved here so each
reported value has a direct bundle pointer:

| bundle | gross suite J — M3 Max / SoC rails | gross mJ/generated output token — same boundary | idle-subtracted suite J — same boundary, secondary | stored idle-subtracted mJ/generated output token — same boundary, secondary | output tok/s | generated tokens | evidence |
|---|---:|---:|---:|---:|---:|---:|---|
| OLMoE r1 | 231.790 | 181.086 | 229.808 | 179.537 | 122.261 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/summary_metrics.json) |
| OLMoE r2 | 227.141 | 177.454 | 226.184 | 176.706 | 122.481 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r2/summary_metrics.json) |
| OLMoE r3 | 228.151 | 178.243 | 227.144 | 177.456 | 122.339 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r3/summary_metrics.json) |
| Qwen3-4B r1 | 362.772 | 283.416 | 360.800 | 281.875 | 106.470 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/summary_metrics.json) |
| Qwen3-4B r2 | 362.642 | 283.314 | 361.438 | 282.373 | 106.542 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r2/summary_metrics.json) |
| Qwen3-4B r3 | 362.903 | 283.518 | 361.825 | 282.675 | 106.545 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r3/summary_metrics.json) |
| Qwen3.5-122B r1 | 1085.144 | 847.769 | 1081.982 | 845.298 | 39.349 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r1/summary_metrics.json) |
| Qwen3.5-122B r2 | 1061.722 | 829.471 | 1048.728 | 819.319 | 39.569 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r2/summary_metrics.json) |
| Qwen3.5-122B r3 | 1069.952 | 835.900 | 1063.354 | 830.745 | 39.502 | 1,280 | [summary](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r3/summary_metrics.json) |

## Published-floor context

The like-for-like published guard is the **suite-level gross**
`floor_gate_j=24.618735 J` on the Apple M3 Max / powermetrics SoC-rail
boundary. It is itself marked “drift review required.” It applies to the
single five-item suite-level window, so the following diagnostic uses
`suite_metrics.levels[0].energy_gross_j`, not the slightly wider top-level
request window. Floor evidence:
[verified Window-A extraction](../2026-07-17-floor-extraction/extraction-verified.json).

| unmatched exploratory contrast | absolute difference between mean suite-level gross windows — M3 Max / SoC rails | comparison with published suite-level gross `floor_gate_j` | bundle evidence |
|---|---:|---:|---|
| OLMoE BF16 vs Qwen3-4B INT4 | 133.720 J | clears 24.619 J (5.43× the guard) | [O1](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/summary_metrics.json), [O2](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r2/summary_metrics.json), [O3](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r3/summary_metrics.json), [Q1](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/summary_metrics.json), [Q2](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r2/summary_metrics.json), [Q3](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r3/summary_metrics.json) |
| Qwen3-4B INT4 vs Qwen3.5-122B-A10B INT4 | 709.569 J | clears 24.619 J (28.82× the guard) | [Q1](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/summary_metrics.json), [Q2](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r2/summary_metrics.json), [Q3](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r3/summary_metrics.json), [F1](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r1/summary_metrics.json), [F2](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r2/summary_metrics.json), [F3](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r3/summary_metrics.json) |
| OLMoE BF16 vs Qwen3.5-122B-A10B INT4 | 843.289 J | clears 24.619 J (34.25× the guard) | [O1](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/summary_metrics.json), [O2](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r2/summary_metrics.json), [O3](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r3/summary_metrics.json), [F1](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r1/summary_metrics.json), [F2](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r2/summary_metrics.json), [F3](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r3/summary_metrics.json) |

Clearing a false-effect guard is necessary but not sufficient for a claim.
These are unregistered, unmatched exploratory contrasts with claim-evidence
flags, no prospective multiplicity family, no matched model/quantization
design, and no output-equivalence gate. The floor comparison says only that
the observed descriptive gaps are larger than this published measurement
guard; it does not support a directional efficiency, architecture, MoE, model
size, or quantization conclusion.

## Configuration and interpretation caveats

- **Unmatched models/configurations.** OLMoE is the local
  `OLMoE-1B-7B-0924` BF16 artifact; Qwen3-4B and Qwen3.5-122B-A10B use INT4,
  group-size-64 MLX artifacts. Size, active/total parameter structure,
  architecture, tokenizer, artifact, and quantization are not controlled.
  Sources: [OLMoE config](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/config.json),
  [Qwen3 config](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/config.json), and
  [Qwen3.5 config](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen35-122b__r1/config.json).
- **Token IDs are model-specific.** The suite shape is matched, but each
  manifest contains model-tokenizer-specific prompt IDs. Fixed token counts do
  not prove fixed semantic input or output work across tokenizers.
- **Thinking/chat-template policy.** Qwen3-4B's config explicitly uses the
  ids-native raw-token path, bypasses the chat template, and says thinking mode
  is avoided. This is not interchangeable with the separate DSpark/DFlash
  feasibility smoke, where thinking mode was engaged and outputs were
  unmatched. The schema has no general chat-template/thinking-mode knob, so
  this behavior is a config-specific caveat, not a cross-runtime guarantee.
  Source: [Qwen3 config](../../../runs/exploratory_2026_07_17/exploratory-20260717-qwen3-4b__r1/config.json); smoke context:
  [DSpark/DFlash trace](../2026-07-17-dspark-dflash-smoke/README.md).
- **OLMoE patch.** The OLMoE target records a local verified
  `rms_norm_eps=1e-05` default patch with its SHA-256 in the hardware notes;
  this local configuration is part of the observation's identity. Source:
  [OLMoE config](../../../runs/exploratory_2026_07_17/exploratory-20260717-olmoe-1b-7b__r1/config.json).
- **Evidence ceiling.** All nine bundles are strict-valid and
  `collection=usable`, but all nine are `claim_evidence_classification=flagged`.
  Universal families include clock/cadence/short-window flags; OLMoE r2 and
  Qwen3.5 r2 also hit a cooldown cap, and OLMoE r3 carries additional
  interpolation/nonpositive-short-window flags. The three retained campaign
  verdicts say claim readiness was not assessed. Source:
  [campaign log](../../../runs/exploratory_2026_07_17/campaign_log.jsonl).
- **Throughput is descriptive.** Tok/s is runtime-observed output throughput
  for these exact artifacts, prompts, fixed output budget, and warm-cache
  sequence. It is not a hardware, architecture, or serving benchmark ranking.

## Verification

The extraction read only retained artifacts. The nine-bundle strict replay was:

```bash
for bundle in runs/exploratory_2026_07_17/exploratory-*__r?; do
  .venv/bin/python -m joulewise validate-bundle --strict "$bundle"
done
```

Result: all nine reported `valid bundle`. Direct arithmetic over the nine
`summary_metrics.json` files reproduced the three retained experiment
aggregates for means, sample standard deviations, and ranges. No bundle,
summary, campaign log, or raw evidence file was modified.
