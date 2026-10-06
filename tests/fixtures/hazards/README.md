# Hazard-module fixtures (lane L1)

Positive controls for `joulewise/hazards`, built from archived real bytes.
Edits to real bytes are listed exactly; nothing else in a file was changed.

## battery/

| File | Source | Edit |
|---|---|---|
| `float-20261005-desk.ioreg` | Live read-only `/usr/sbin/ioreg -r -c AppleSmartBattery` on 2026-10-05 (UpdateTime 1791249441), 17345 bytes | none |
| `charging-1716ma-synthetic-from-real.ioreg` | `float-20261005-desk.ioreg` | top-level `IsCharging` No to Yes, `InstantAmperage` and `Amperage` 0 to 1716, `Voltage` 12180 to 12952: the 09-25 charging episode of `docs/process_traces/2026-09-24-interactive-4b/31-battery-float-log.jsonl` (amp_mA 1716, charging Yes, mV 12952), whose raw ioreg bytes were not kept |
| `discharge-minus447ma-synthetic-from-real.ioreg` | `float-20261005-desk.ioreg` | top-level `InstantAmperage` and `Amperage` 0 to 18446744073709551169 (-447 mA): the 2026-10-01T04:24:54Z gauge reading of the 0555Z attempt (`docs/process_traces/2026-09-30-activation-e4df3b93/c1-rearm/battery-refused-0555Z-attempt.txt`), which recorded values only, not raw bytes; ExternalConnected Yes and Voltage 12180 as recorded |
| `on-battery-synthetic-from-real.ioreg` | `float-20261005-desk.ioreg` | top-level `ExternalConnected` Yes to No |
| `malformed-synthetic-from-real.ioreg` | `float-20261005-desk.ioreg` | top-level `InstantAmperage` 0 to `broken` |
| `c2-d06-pre-20261001.ioreg`, `c2-d06-post-20261001.ioreg` | `night-archive/harvest-d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/custody-root/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d06/raw/battery_float.{pre,post}.ioreg` | none; the post read is the only archived publication with a nonzero instant `BatteryPower` (-134 mW) |
| `c1-d01-pre-20261001.ioreg` | `night-archive/harvest-d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/custody-root/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d01/raw/battery_float.pre.ioreg` | none; with `tests/fixtures/battery_float/float-2026-09-25-2047.ioreg` it brackets the -447 mA episode |
| `publications-20260925-20261005.json` | every distinct archived gauge publication with `PowerTelemetryData` (66) plus the live desk read; built by `tools/build_battery_publications.py`, each record with its source path and the SHA-256 of the exact bytes read | values only |

## instrument/

| File | Source |
|---|---|
| `cadence-20260919-n1-d01-launchd.json` | The first 300 frames' `elapsed_ns` of `runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d01/raw/powermetrics.plist` (iCloud archive `d079-epoch-25g83-derivation-n1-20260919-harvest-20260919.tar`, SHA-256 in the file): the default-ProcessType launchd night agent, median 249.7 ms |
| `cadence-20261004-block3-idle.json` | The first 300 frames of `night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z/g2a-root/runs/g2a-large-p0512-r01/raw/powermetrics_idle.plist`: block 3 under the Interactive launchd job, median 129.9 ms (block 3's own probe receipt: 131.4 ms) |
| `fake_powermetrics.py` | Stand-in for `/usr/bin/powermetrics` at the hardware seam: accepts the production argv and re-serialises a cadence fixture's frames |

Built by `tools/build_cadence_fixtures.py`.

## tools/

Provenance scripts, not tests: `build_battery_publications.py`,
`build_cadence_fixtures.py`, `build_physics_rows.py` (writes
`configs/gates/physics_rows.json` from the gate-prune inventory) and
`write_protects.py` (writes each module's `PROTECTS` and `SUPERSEDES` from
that file).
