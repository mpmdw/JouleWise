BLOCK

[HIGH] [VERIFIED] PR #821 at `6ffcb3c3d` registers three superseded kit hashes. For `qual-01`, `qual-02`, and `qual-03`, the manifest pins `fe5b692a…`, `a1b964fa…`, and `f977eff8…`. The audit branch’s replacement kits hash to `35ded7c8…`, `69ba7cfe…`, and `d7e6fda1…`. A synthetic final with only the 32 pending hashes filled exited `0`. Substituting **any one** current kit hash exited `1` with `final manifest differs outside the registered hash slots`. Update all three kit pins and the ledger digest before the first qualification receipt. [PR manifest](https://github.com/mpmdw/JouleWise/blob/6ffcb3c3d2b4ed6f4e925faa4cc41ce6669ef52c/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-qual-01.manifest.json#L34-L70) · [Current kit table](https://github.com/mpmdw/JouleWise/blob/d7c436930ec1a3a29b262990837e6154058b5add/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118/STATUS.md#L23-L29)

```sh
d=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign
git show "6ffcb3c3d:$d/looks/lm-qual-01.manifest.json" | jq -r '.reads.blocks[].kit_sha256'
for n in 01 02 03; do
  git show "d7c436930:$d/item-drafts-1118/kits/cl-qual-$n.v1.1.json" | shasum -a 256
done
```

[MED] [VERIFIED] The §4(a) hand-read summary omits the capture G0 check, each consumer’s release and wait, and each leg’s decode count against its cap. It also omits the requirement for a prior qualifying run’s **hand-read** to discharge the gate. [Manifest](https://github.com/mpmdw/JouleWise/blob/6ffcb3c3d2b4ed6f4e925faa4cc41ce6669ef52c/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-qual-01.manifest.json#L101-L106) · [RL-181 §4(a)](https://github.com/mpmdw/JouleWise/blob/d7c436930ec1a3a29b262990837e6154058b5add/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19512-L19516)

The GPU 1.10 own-prefix series, length-specific sample SDs, equal-day 90% t interval, support gates and inclusive unrounded ±0.10 bounds match RL-181. Both tails, all eleven public fields, both energy-dependent words, the no-twin rule and all three custody names match. All 32 placeholders are code, scorer or schema hashes. The validator rejected scientific and whitespace changes, all five focused tests passed, and the PR leaves v1 untouched.