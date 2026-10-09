# NEG-8 settled-reference corpus

This campaign collects 18 sequential, same-condition copies of the canonical
Window-A NEG-8 reference cell. Its fixed membership supplies the governed
`n >= 10` settled-reference corpus used to derive the Ed-ratified 2026-07-24
gross and idle-subtracted point-drift bounds. The artifact includes both the
legacy single-member endpoint guard and the prospective three-member
endpoint-mean guard; this corpus is not itself a start/end whole-window
bracket.

After the campaign has completed under `RUNS_ROOT`, mint the immutable bound:

```sh
python3 scripts/run_campaign.py \
  --derive-neg8-drift-bound configs/campaigns/neg8_reference_corpus_v5/derivation/settled_corpus.json \
  --neg8-drift-bound-output RUNS_ROOT/neg8-drift-bound.json \
  --runs-dir RUNS_ROOT
```

These v5 inputs set `idle_seconds` 57.6: 576 records at the sampler's ~130.5 ms
cadence, about 75 s of idle capture (block-5 timing ruling, 2026-10-06). Run ids are retained because each
prospective window has fresh bound and claim runs roots; never reuse a
historical 30-second bundle root for this campaign.

The block-5 corpus18 erratum, admitted by the cold ruling on 2026-10-09, adds six unconditional members; the desk uses the first 12 clean members in committed order, or all clean members if only 10 or 11 remain.
