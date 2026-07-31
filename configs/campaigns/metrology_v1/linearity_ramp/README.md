# Metrology v1: linearity ramp

This campaign feeds paper claim C1 by measuring instrument-response linearity
and fitting the per-token decode slope that becomes C3's energy standard.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; this member set uses the frozen 1.5B stack.

Eight fixed, auditable, counterbalanced replicate-blocks cover five output
levels for 40 members. The generator asserts one occurrence of every level per
block and a mean level position within ±0.5 of 3.0.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/linearity_ramp`; the exact log is
`runs/metrology_v1/linearity_ramp/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/linearity_ramp/01_ramp \
  --runs-dir runs/metrology_v1/linearity_ramp \
  --log runs/metrology_v1/linearity_ramp/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p0128-o0128` | 128/128 | `phase_energy_j.decode` | `eec17ac336e270e556158638d8c720b669412f9bbffa453ebbe5d5d4a1110d62` |
| `mt-q15-decode-p0128-o0256` | 128/256 | `phase_energy_j.decode` | `f1590ef7099780219aba4578dbf56cb963269c87f5ebc2bde28b5b05452d8ae3` |
| `mt-q15-decode-p0128-o0512` | 128/512 | `phase_energy_j.decode` | `6974fbf58bcce32b757631fb8536750788a13d371731354d8873abbfc23fd54d` |
| `mt-q15-decode-p0128-o1024` | 128/1024 | `phase_energy_j.decode` | `d57bfcd616d61e7a30f1fc9c08d9006c6f9457df45671952d4f53d2313f42abb` |
| `mt-q15-decode-p0128-o2048` | 128/2048 | `phase_energy_j.decode` | `a5b3b5682e21aa71052cd7e5d899f4d7635c36531a2912822532f1c4fffd65ad` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s. The supplied
values are o128 90.5 s, o256 91.0 s, o512 92.1 s, o1024 94.1 s, and o2048
98.2 s. Total: 8 × (90.5+91.0+92.1+94.1+98.2) = 8 × 465.9 = 3727 s =
62.1 min, 40 members. Basis: the 2026-07-29 timing probe; the four-token warmup
is absorbed in overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status:
  draft_pending_magistrate_ratification`, and `kind: absolute` are the selected
  plan literals; the plan vocabulary is not runner-validated.
- Family IDs use the ratified `mt-q15-decode-p0128-oOOOO` template. The
  `mt-q15-decode-p0128-o2048` definition is byte-identical to additivity's
  shared decode-heavy family.
