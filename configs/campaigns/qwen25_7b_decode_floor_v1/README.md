# Qwen2.5-7B decode floor v1

**DRAFT contingency — pending magistrate selection and ratification.**

This production quiet-window floor calibration uses only
`Qwen2.5-7B-Instruct-4bit` at revision
`c26a38f6a37d0a51b4e9a1eb3026530fa35d9fed`. It contains 10 absolute
decode repeats and 10 fixed same-condition A/B/B/A null blocks.

This contingency exists because the current minted decode floor is bound to
the realized 1.5B stack identity, including its model artifact. The 7B stack
has no transportable floor and therefore needs its own calibration before a
7B contrast arm can be floor-gated. The magistrate chooses whether tonight's
quiet window runs this floor or the cross-model contrast.

All members use condition family `df-ph-decode-qwen25-7b`. Its
`A_equals_B` literal records that the A and B labels in its floor-calibration
ABBA blocks are aliases of the same condition.

The window chain supplies the governed 3+1+3 references and the 12-member
NEG-8 in-window bound corpus from `configs/campaigns/window_references/` and
`configs/campaigns/neg8_reference_corpus/`. Those reference directories are
not science stages in this campaign.

Execute each selected stage through the window chain in frozen order. The
per-stage command shape is:

```sh
.venv/bin/python scripts/run_campaign.py <stage_dir> \
  --runs-dir runs/qwen25_7b_decode_floor_v1 \
  --log runs/qwen25_7b_decode_floor_v1/campaign_log.jsonl \
  --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json
```

Measured-duration note only: the 7B member estimate is about 97 s from the
2026-07-29 timing probe; the 1.5B window-C decode mean was 92.7 s (n=40).
