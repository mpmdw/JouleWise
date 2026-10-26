# BYTES test 7: BY-H2 desk comparison (2026-10-23)

All three regimes retain `scale = max(1, E/E_ref, T/T_ref)` on every boundary. No numerical pass criterion is specified by the registration §7, the BYTES design R3/R8 item 6, or block-6 design §14. Completion of the stages does not establish a pass (P0 ruling 3).

## Inputs and arithmetic

Read-only non-claim session `bytes-h2-20261023T144711843389Z-calibration`. Source identities:

- `/Users/edr/night-bytes/h2-20261023T144711Z/MEASUREMENTS.json`: SHA-256 `c7d9c4f17f5758f82a8263b3a24a71c215fb02885e27d416eabac820b10f76a8`.
- `/Users/edr/night-bytes/h2-20261023T144711Z/export/bytes-mac-check/bytes-h2-20261023T144711843389Z-calibration.runs.csv`: SHA-256 `88633cced4259d0d39791a0ac9a4b3d18385fa5b9b9d7b66c11e1969a1f11bfc`.
- `/Users/edr/code/jw-wt/by-fill/configs/b6/flag_catalog_b6.json`: SHA-256 `33e1c6110d98474465109062cfcdff480679ba8b2c9854fc754fa26fa07bccb6`.

Replay: `TMPDIR=/private/tmp/by-fill/20261023-desk JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B .scratch-fill/compute_test7.py --check`.

The six stage IDs are `bytes-mac-check-test7-<regime>-<start|end>` in MEASUREMENTS.json `/stage_timestamps`; all have rc 0. Each export stage alternates workload/reference/workload/reference. Use the workload's **gross rails decode** `phase_decode_j` and the reference's **gross rails whole-request** `gross_energy_j`, matching registration §7's energy definitions (and `joulewise/bytes_analysis.py:779-817`). For each role, average the start observations and the end observations separately. Change = end mean − start mean. Change difference = workload change − reference change. There are two reference observations at each end in every row below.

Primary selection applies §6's existing member exclusions. The 70B end r01 is excluded for `thermal.os_level_nonzero`; all other test-7 rows are succeeded and unexcluded. The labelled flagged-inclusive table restores that one valid energy record under §6. These are descriptive stage means, not floor-module cells. No new minimum, tolerance or pass threshold is imposed. Every source decimal lexeme, selected run ID, flag and measurement receipt is retained in TEST7.json. Arithmetic uses exact rational values and rounds only the printed energies to §14's 3 decimals; JSON stores the exact numerator and denominator plus a 50-digit decimal rendering.

## Primary comparison (rails)

| Regime | n workload start/end | Workload start (J) | end (J) | change (J) | Reference start (J) | end (J) | change (J) | change difference (J) | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| llama-70b | 2/1 | 2079.130 | 1991.531 | -87.598 | 36.973 | 37.031 | +0.058 | -87.656 | pass not established |
| qwen35-122b | 2/2 | 306.417 | 306.765 | +0.348 | 37.620 | 37.124 | -0.496 | +0.844 | pass not established |
| qwen3-next-80b | 2/2 | 144.712 | 142.993 | -1.719 | 37.244 | 37.613 | +0.370 | -2.088 | pass not established |

## Flagged-inclusive description (rails)

| Regime | n workload start/end | Workload start (J) | end (J) | change (J) | Reference start (J) | end (J) | change (J) | change difference (J) | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| llama-70b | 2/2 | 2079.130 | 1970.000 | -109.129 | 36.973 | 37.031 | +0.058 | -109.187 | pass not established |
| qwen35-122b | 2/2 | 306.417 | 306.765 | +0.348 | 37.620 | 37.124 | -0.496 | +0.844 | pass not established |
| qwen3-next-80b | 2/2 | 144.712 | 142.993 | -1.719 | 37.244 | 37.613 | +0.370 | -2.088 | pass not established |

## Outcome and limits

For llama-70b, qwen35-122b and qwen3-next-80b: **pass not established**; the registered fallback remains `scale = max(1, E/E_ref, T/T_ref)` (§7; P0 ruling 3). E and T are the eventual cell's gross decode estimate and stratified mean decode duration; E_ref and T_ref are that session's kept start/midpoint/end references' mean gross whole-request energy and duration. This desk table does not substitute its small stage means for those future claim-cell quantities.

The supplied export contains rails energies only. DC-input and rest drifts are unavailable from these two inputs; no pass on those boundaries is asserted. The same fallback remains there. No model, meter stream, key, measurement or session output was opened or changed by this computation beyond the explicitly authorized MEASUREMENTS.json and export reads.
