# Splitwise decode v1

**DRAFT — pending magistrate ratification.**

This production quiet-window campaign is a 10-block fixed ABBA decode-phase
energy contrast. Arm A is `Qwen2.5-1.5B-Instruct-4bit` at revision
`8b403126fc14f14cfc99bb4cfa72ecbc129ea677`; arm B is
`Qwen2.5-7B-Instruct-4bit` at revision
`c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`.

The arms deliberately use distinct condition families,
`sw-decode-a-qwen25-1p5b` and `sw-decode-b-qwen25-7b`, so floor selection and
analysis partition evidence by arm before deriving stack identity. In each
family definition, `A_equals_B` describes that family's own floor-calibration
null alias; it does not describe this campaign's cross-model ABBA contrast.

The window chain supplies the governed 3+1+3 references and the 12-member
NEG-8 in-window bound corpus from `configs/campaigns/window_references/` and
`configs/campaigns/neg8_reference_corpus/`. Those reference directories are
not science stages in this campaign.

Execute each selected stage through the window chain in frozen order. The
per-stage command shape is:

```sh
.venv/bin/python scripts/run_campaign.py <stage_dir> \
  --runs-dir runs/splitwise_decode_v1 \
  --log runs/splitwise_decode_v1/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Measured-duration note only: the 1.5B decode member mean was 92.7 s in
window C (n=40); the 7B member estimate is about 97 s from the 2026-07-29
timing probe.
