# NEG-8 settled-reference corpus

This campaign collects 12 sequential, same-condition copies of the canonical
Window-A NEG-8 reference cell. Its fixed membership supplies the governed
`n >= 10` settled-reference corpus used to derive the Ed-ratified 2026-07-24
gross and idle-subtracted point-drift bounds. The artifact includes both the
legacy single-member endpoint guard and the prospective three-member
endpoint-mean guard; this corpus is not itself a start/end whole-window
bracket.

After the campaign has completed under `RUNS_ROOT`, mint the immutable bound:

```sh
python3 scripts/run_campaign.py \
  --derive-neg8-drift-bound configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json \
  --neg8-drift-bound-output RUNS_ROOT/neg8-drift-bound.json \
  --runs-dir RUNS_ROOT
```
