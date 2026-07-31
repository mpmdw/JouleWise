# Metrology v1: additivity shapes

This campaign feeds paper claim C4 by testing phase-to-whole conservation and
the causal invariance of prefill energy with respect to output length.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; this member set uses the frozen 1.5B stack.

There are 24 members, not 72. Each shape member records prefill-phase energy,
decode-phase energy, and whole-request energy; the plan has three cells per
shape pointing to the same ordered bundle IDs.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/additivity_shapes`; the exact log
is `runs/metrology_v1/additivity_shapes/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/additivity_shapes/01_shapes \
  --runs-dir runs/metrology_v1/additivity_shapes \
  --log runs/metrology_v1/additivity_shapes/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p2048-o0128` | 2048/128 | `phase_energy_j.decode` | `61e5b2244686edcb67808fb4b67ebb664374d6c6c093ab5bbde3c078c52c6f6a` |
| `mt-q15-prefill-p2048-o0128` | 2048/128 | `phase_energy_j.prefill` | `0617f1072282ce443fd8ad7cd151b5644a214ed514728dd4428af88d5e1bd4fe` |
| `mt-q15-request-p2048-o0128` | 2048/128 | `energy_request_j` | `90c8d4c0ac2e84ec46a253e3b5896262c18a0a2b649eaef0f418123ecf459e44` |
| `mt-q15-decode-p0512-o0512` | 512/512 | `phase_energy_j.decode` | `c6818da04094e6ffe87c8c5462c3300bc0bae58050df02d834385ed047e0e9cf` |
| `mt-q15-prefill-p0512-o0512` | 512/512 | `phase_energy_j.prefill` | `9a77ea91d9eb2ac02a2f388d720df03036b0446824b362a30aa36ea59102c45e` |
| `mt-q15-request-p0512-o0512` | 512/512 | `energy_request_j` | `6aed2b73c4d3a8dbb5d96a42e6f446a090d69eca2b83ae8a5405f353b3ee2fe6` |
| `mt-q15-decode-p0128-o2048` | 128/2048 | `phase_energy_j.decode` | `a5b3b5682e21aa71052cd7e5d899f4d7635c36531a2912822532f1c4fffd65ad` |
| `mt-q15-prefill-p0128-o2048` | 128/2048 | `phase_energy_j.prefill` | `b7fb463adf73f972923bd65fccde1d17d0ec1d53560ae389914fe74698d58468` |
| `mt-q15-request-p0128-o2048` | 128/2048 | `energy_request_j` | `c8c0ed2de6e078078e4584b2e5223459745cd9a808580e4796b7f663d75cc5dc` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s.
8 × (91.5 + 92.4 + 98.2) = 8 × 282.1 = 2257 s = 37.6 min,
24 members. The 91.5 and 92.4 figures include a ≤1 s prefill allowance for
the 2048- and 512-token prompts. Prefill time is not in the 2026-07-29 timing
probe and remains unmeasured; the four-token warmup is absorbed in overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status:
  draft_pending_magistrate_ratification`, and nine `kind: absolute` cells are
  the selected plan literals; the plan vocabulary is not runner-validated.
- The spec says the workload name is an exception for additivity but supplies
  no replacement literal. `df_ph_decode` is retained because the shared
  `mt-q15-decode-p0128-o2048` family must be byte-identical to linearity's
  definition. Ratification should confirm that modularity-directed fallback.
- Each member carries all three metric-specific `df-condition=` tags, and each
  manifest entry names the request family as its primary `workload` while also
  listing all three `condition_family_ids`; a future manifest consumer should
  ratify that descriptive vocabulary.
