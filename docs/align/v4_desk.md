# ALIGN v4 desk analysis

This is an additive desk path. It does not modify the v3 anchor configuration
or the pinned measurement core. Its rules follow council `FINAL-DESIGN.md`
§§2.4–2.6, as summarized in the reviewed thermal handoff
[`thermal_gates.md`](thermal_gates.md): U4 combines sentinel equivalence with
the four-anchor, K≥3 balanced crossed-anchor moment; U5 bounds state
sensitivity; U6 checks frozen-fit residual stability. Missing evidence is
**inconclusive**, never a pass.

Run the member desk with any number of prior session reports:

```sh
python3 scripts/align_v4_thermal_desk.py \
  --manifest SESSION/manifest.json --output SESSION/v4-desk \
  --compare-session S1/PILOT.json \
  --compare-session S2/PILOT.json \
  --compare-session S3/PILOT.json
```

Each synthetic/portable PILOT may contain `v4_desk_evidence` with
`session_id`, the same four `anchors`, per-model `sentinel_energies_j`, a
`sentinel_reference_j`, and per-model `u5_inputs` / `u6_inputs` records. The
reader computes U5 and U6 from these journal-derived values. Precomputed `u5`
and `u6` objects remain an adapter compatibility form, not the preferred CLI
fixture interface.
The K-session reader compares anchor energies across files and passes U4 only
when both council conditions pass. `PILOT.json.K_session_read` records the
reader outcome and adapter identity.

The real `k_sessions.py` is outside this repository. Its adapter point is
`session_desk_evidence(..., adapter=callable)`: the callable receives decoded
PILOT objects and returns `anchors`, `sentinels`, `sentinel_reference_j`,
`u5`, and `u6`. The CLI intentionally uses only the portable object until the
off-repository owner connects that callable. It never follows paths embedded
in a PILOT file.

## Decision rules

* **U4:** at least three windows; sentinel mean has a ±0.25% point bar and its
  two-sided 90% Student interval must lie within ±0.5%. The crossed four-anchor
  window standard deviation must be ≤6 J. Either failure fails; absent or
  insufficient evidence is inconclusive.
* **U5:** light cells scale the W1 contrast's maximum absolute 90% endpoint by
  the cell/30B energy ratio. Heavy cells use eligible token-identical paired
  energy/temperature differences fit through zero and multiply the 90% bound
  by the observed G0 range. The bound must be within 0.1× the smaller paired
  residual scale; a point outside fails and an overlapping interval is
  inconclusive.
* **U6:** frozen-fit benign residuals use per-turn OLS and chronological
  within-pair early/late halves with equal-pair Welch uncertainty. Both the
  energy-scaled ±1 J/turn rule and ±0.37% episode-energy rule must pass.
  Temperature and clock correlations are diagnostics only.

## Open questions

1. The off-repository adapter's custody/identity handshake and exact invocation
   remain to be pinned when `k_sessions.py` is available.
2. Protocol v4 must freeze the estimator conventions noted in
   `thermal_gates.md` (balanced moments, heavy fit through zero, and the U6
   split/weighting convention); this implementation does not create that
   scientific ruling.
3. A W1 report remains intentionally unable to claim U4–U6 control. At least
   K=3 completed session reports are required for the cross-session read.
