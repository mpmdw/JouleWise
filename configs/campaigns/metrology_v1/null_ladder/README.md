# Metrology v1: null ladder

This campaign feeds paper claim C2 by measuring null bias and scatter versus
effect magnitude against the error-model envelope.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; this member set uses the frozen 1.5B stack.

Each output size has five same-condition blocks in fixed A/B/B/A order. A and B
are aliases of the same condition family.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/null_ladder`; the exact log is
`runs/metrology_v1/null_ladder/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/null_ladder/01_null_o0128 \
  --runs-dir runs/metrology_v1/null_ladder \
  --log runs/metrology_v1/null_ladder/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/null_ladder/02_null_o0512 \
  --runs-dir runs/metrology_v1/null_ladder \
  --log runs/metrology_v1/null_ladder/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/null_ladder/03_null_o2048 \
  --runs-dir runs/metrology_v1/null_ladder \
  --log runs/metrology_v1/null_ladder/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p0128-o0128` | 128/128 | `phase_energy_j.decode` | `eec17ac336e270e556158638d8c720b669412f9bbffa453ebbe5d5d4a1110d62` |
| `mt-q15-decode-p0128-o0512` | 128/512 | `phase_energy_j.decode` | `6974fbf58bcce32b757631fb8536750788a13d371731354d8873abbfc23fd54d` |
| `mt-q15-decode-p0128-o2048` | 128/2048 | `phase_energy_j.decode` | `a5b3b5682e21aa71052cd7e5d899f4d7635c36531a2912822532f1c4fffd65ad` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s. o128:
20×90.5=1810 s; o512: 20×92.1=1842 s; o2048: 20×98.2=1964 s;
total 5616 s = 93.6 min, 60 members. Basis: the 2026-07-29 timing probe; the
four-token warmup is absorbed in overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status:
  draft_pending_magistrate_ratification`, and `kind: comparative_abba` are the
  selected plan literals; the plan vocabulary is not runner-validated.
- Family IDs use the ratified modular template and the three definitions are
  byte-identical to the matching linearity definitions.
