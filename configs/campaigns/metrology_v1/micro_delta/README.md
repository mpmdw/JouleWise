# Metrology v1: micro delta

**DRAFT-PENDING-SLOPE: `k0064` is a placeholder only. Do not measure it until
the linearity slope fixes and the magistrate ratifies all k slots.**

This campaign feeds paper claim C3 by walking a known decode-energy effect
across the detection floor in both directions.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; both A and B here use the identical frozen
1.5B stack and differ only in output length.

The generator accepts repeatable `--k` arguments. With no arguments it emits
only the 20-member `k0064` placeholder: five fixed A/B/B/A blocks with A=512
and B=576 output tokens.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/micro_delta`; the exact log is
`runs/metrology_v1/micro_delta/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/micro_delta/k0064 \
  --runs-dir runs/metrology_v1/micro_delta \
  --log runs/metrology_v1/micro_delta/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p0128-o0512` | 128/512 (A) | `phase_energy_j.decode` | `6974fbf58bcce32b757631fb8536750788a13d371731354d8873abbfc23fd54d` |
| `mt-q15-decode-p0128-o0576` | 128/576 (B, k=64) | `phase_energy_j.decode` | `cdcf30d0c40a64638aa4d18eb9fca72b96fdeb1a41fbd50008966d90129ebc91` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s. For k=64:
5 × (2×92.1 + 2×92.35) = 5 × 368.9 = 1845 s = 30.7 min,
20 members. Three k slots ≈ 92 min, 60 members; only k=64 is generated now.
Basis: the 2026-07-29 timing probe; the four-token warmup is absorbed in
overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status: draft_pending_slope`,
  `kind: comparative_contrast`, `null_alias: false`, and
  `difference_orientation: condition_b_minus_condition_a` are the selected
  plan literals; the plan vocabulary is not runner-validated.
- The condition-family validator accepts only
  `comparison_policy: same_condition_repeat_and_null_abba_alias` with
  `abba_alias_relation: A_equals_B`. Those literals are therefore used for the
  A≠B contrast families as the spec-directed fallback, even though the plan
  correctly declares a non-null contrast.
- The plan's two arms use per-k `condition_families` and `output_tokens_by_k`
  fields so repeatable `--k` generation stays descriptive. Ratification should
  confirm those plan-only field names before a plan validator is introduced.
- Family IDs follow `mt-q15-decode-p0128-oOOOO`; the k-derived B family changes
  with each final slot. The placeholder remains DRAFT-PENDING-SLOPE until the
  fitted slope targets 0.5× / 1× / 1.5× / 3× the published floor.
