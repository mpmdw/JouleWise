# Executable v4 series candidate (Sol)

`series_manifest.json` freezes **a proposal**, not native collection authority.
It enumerates every member, seed, pair, condition and pool. The checked-in
choice is W1 → D1–D3 (separate fit) → C1–C8 → T1–T3. D1=C1, D2=C2,
D3=C3 and six-test alternatives are supported explicitly by the builder.
The lead must settle the mapping/fit/scorer and test shape with the independent
Opus build. No old seven-plus-reserve or interleaved-v5 sheet is consumed.

```sh
python3.13 -B scripts/align_v4_series.py materialize --window-id C1
python3.13 -B scripts/align_v4_series.py materialize --window-id C1 --check
```

This writes the real `configs/campaigns/align_v4_c1` kit: member configs,
order manifests, collection plan, calibrated stage graph, identity inventories,
seed allocation and sizing. It reads repository configs/Git objects only.
Materialize all selected windows and commit them at the final measuring head;
generation is possible before R1, while **native prepare still refuses pending
R1/U3/W1 registration**. W1 itself retains its existing kit and generator.

Native selection is `scripts/align_v4_session.py prepare --window-id C1` with
the existing measurement/session-root arguments. Install/desk use the stored
selection; changing the series or admission after prepare refuses install.
There is no second launcher. See [the Sol build and ruling list](../../../../docs/align/v4/DCT-SERIES-sol.md)
for admission, R12 packet sources, synthetic replay and native gates.
