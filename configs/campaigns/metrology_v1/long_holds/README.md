# Metrology v1: long holds

This campaign feeds paper claim C5 by measuring drift curvature during
sustained decode and thermal settle relative to the 180 s convention.

These campaigns measure the INSTRUMENT, not a gated scientific claim. They
therefore need no new model stacks and no new detection floors. They reuse the
two already-characterized stacks; this member set uses the frozen 1.5B stack.

Part A contains three 4096-output-token sustained decode members. Part B
contains one 128-output-token member at each of 120, 300, and 600 idle seconds.

## HARNESS GAP

HARNESS FACT (lead-verified, do not re-litigate):
`workload_profile.output_tokens` is validated by `_positive_int`
(`joulewise/schemas.py:816`) so a ZERO-token / pure-idle member is IMPOSSIBLE;
and the NEG-8 reference configs
(`configs/campaigns/neg8_reference_corpus/`) are NOT idle members — they run
the `df_rq_mid` 1024/256 workload. The only supported extended-idle knob is
`sampling.idle_seconds` (schema: number, minimum 0, no maximum,
`joulewise/schemas.py:1170`). Therefore Part B = 3 members with output_tokens
128, prompt_tokens 128, and `sampling.idle_seconds` ∈ {120.0, 300.0, 600.0}.
This limitation is flagged for magistrate ratification. DO NOT MODIFY HARNESS
CODE.

## Evidence root and execution

The exact evidence root is `runs/metrology_v1/long_holds`; the exact log is
`runs/metrology_v1/long_holds/campaign_log.jsonl`.

```sh
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/long_holds/01_holds \
  --runs-dir runs/metrology_v1/long_holds \
  --log runs/metrology_v1/long_holds/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
.venv/bin/python scripts/run_campaign.py configs/campaigns/metrology_v1/long_holds/02_idle_extended \
  --runs-dir runs/metrology_v1/long_holds \
  --log runs/metrology_v1/long_holds/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Extraction invocations must pass an ABSOLUTE `--runs-dir` and
`--evaluation-basis-sha256`.

## Condition families

| ID | Prompt/output | Metric | Canonical SHA-256 |
| --- | --- | --- | --- |
| `mt-q15-decode-p0128-o4096` | 128/4096 | `phase_energy_j.decode` | `b3ded631d0be157a5ff8d7d53f71bb7f06ebe35ebef345787dfbefe7fbba5154` |
| `mt-q15-decode-p0128-o0128-idle0120` | 128/128, idle 120 s | `phase_energy_j.decode` | `e2e3670670547c0f6ddf7857ab612cd897bd10e0214ed6d79f1d185250795a17` |
| `mt-q15-decode-p0128-o0128-idle0300` | 128/128, idle 300 s | `phase_energy_j.decode` | `5f05f3b5d0060dc9f054e5219e47eec1b9a6c9f36a65b9a44420365a2c5890b8` |
| `mt-q15-decode-p0128-o0128-idle0600` | 128/128, idle 600 s | `phase_energy_j.decode` | `5a22f0e9a356eb0a84d3e5debb0c2659a0f3cccf47c75b41d06e37ab4d42f431` |

## Duration arithmetic

Per-member wall = 90 s fixed overhead + output_tokens × 0.004004 s. Part A:
3 × 106.4 = 319 s = 5.3 min. Part B: 90.5 + (120−30) = 180.5 s,
90.5 + (300−30) = 360.5 s, and 90.5 + (600−30) = 660.5 s;
1201.5 s = 20.0 min. Total 1520 s = 25.3 min, 6 members. Basis: the
2026-07-29 timing probe; the four-token warmup is absorbed in overhead.

## OPEN QUESTIONS FOR RATIFICATION

- `use_role: staleness_sentinel`, `freeze_status:
  draft_pending_magistrate_ratification`, and four `kind: absolute` cells are
  the selected plan literals; the plan vocabulary is not runner-validated.
- The extended-idle workload name is `mt_idle_extended`, the supplied exception
  had no literal. Each sampling variant has the mandated
  `mt-q15-decode-p0128-o0128-idleSSSS` family ID. The plan describes variable
  sampling through `idle_seconds_by_condition_family`; both field choices need
  ratification before a plan validator consumes them.
- The three one-member idle cells use `minimum_claim_n: 1` because each
  idle-duration family has exactly one planned observation; these are
  characterization cells and do not gate a claim.
