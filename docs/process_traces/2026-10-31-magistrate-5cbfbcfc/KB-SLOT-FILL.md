# Known-bytes stream test: outcome (the BYTES reg. §1 slot)

**Status.** This file fills the slot `⟦MAC: known-bytes stream test outcome⟧` in §1 of `docs/registrations/bytes_pack_v1.md`. That registration lives on the BYTES lineage (`lane/2026-10-28-bytes-pass2-open`), and the slot text below is copied into it, through a PR (the registrations rule runs the whole suite), when that lineage lands. The reading rule is `docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md` (matched-geometry revision, code `53bcceeac`). The test is non-claim and changes no registered number, exclusion or estimator. Its only effects are this slot and the printed lines beside the rails and rest claim lines, and with all classes RESOLVED no such line prints.

Written 2026-10-31 by magistrate activation 5cbfbcfc (Opus 5.5), after the cold science gate: a raw re-derivation by Fable 5.1 and Opus 5.5, blind to each other and both executing, each with its own program written from the rule text. Both returned **ADMIT-WITH-CORRECTIONS** with no BLOCKER. Reports: `~/night-archive/seats-5cbfbcfc/kb3-science-gate/{fable,opus}-report.md`.

## The session
- Window `attempt-3`, measurement Mac (Apple M3 Max, macOS 25G83), checkout `/Users/edr/code/bytes-stream-test` at `53bcceeac`. The window ran from 23:21:05 PDT 2026-10-30 to 00:38:13 PDT 2026-10-31, with driver verdict GO, chain exit 0, and no hits in 147 agent censuses. The capture stage ran 23:29:36 to 00:34:12. Night record branch `night-results/attempt-3` (`30c2a34f5`).
- Archive (read-only): `/Users/edr/night-archive/bytes-stream-test/attempt-3`. Harvest `attempt-3-INPUT.json` sha256 `4e0863e00239dd41dac4e994d13a4ba1e6188f926fdb9f6534248a78b3b50c60`. Reader output sha256 `f33c58cce4753f787fc0dab574108ebc33ba053599ed930da593fdaac4a2942f`. Both seats re-ran the reader byte-identically, and `check` on the archived receipts reproduces `CHECK.json` byte-identically.
- Hour as run: 3,558.8 s. Four calls in the order R, C, C, R. Each R call ran N_R = 2,394,112 dispatches (2,338 whole sweeps of the ring), and each C call ran N_C = 2,672,640.

## Slot fill

**Classes.** Rails **RESOLVED**; GPU rail **RESOLVED**; rest **RESOLVED**. DC input is valid (Δ − δΔ = 0.0317 J/GB > 0). Nothing prints beside the rails or rest claim lines.

**Contrasts** (rotate minus repeat, J per GB of logical bytes, 32 MiB matched dispatches):

| boundary | Δ ± δΔ | full precision | class |
|---|---|---|---|
| rails | 0.0092 ± 0.0021 | 0.0092430977 ± 0.0020742222 | RESOLVED |
| GPU rail | 0.00879 ± 0.00010 | 0.0087900978 ± 0.0001046952 | RESOLVED |
| DC input | 0.0389 ± 0.0072 | 0.0388927024 ± 0.0072375402 | valid |
| rest | 0.0296 ± 0.0084 | 0.0296496048 ± 0.0084425395 | RESOLVED |

Both seats' independent programs agree with every value above to within 6e-10 J/GB. The agreement bar was 1% of each boundary's half-width, so the smallest bar was 1.05e-6 J/GB for the GPU rail.

**Geometry and the residency check.**
- b = 33,554,432 B (32 MiB), the first resolved rung (k = 1). Rung k = 0 (64 MiB) was not resolved: D = 19.2 µs, δD = 34.6 µs.
- At the chosen rung, D ± δD = 33.1 ± 10.1 µs, with t_R = 317.08 ± 0.41 µs and t_C = 283.98 ± 9.66 µs.
- W = 34,359,738,368 B (32 GiB ring), Q = 1,024, G = 67,108,864 B. G's source pin: `mlx v0.31.2 mlx/backend/metal/reduce.cpp all_reduce_dispatch: in.nbytes() <= (1 << 26)`.
- φ_U = 1/64; ρ_L = 0.07140; κ = 14.01.

**Stack check.** All four hour receipts match on every field:
- OS: macOS-26.6.2-arm64-arm-64bit-Mach-O; machine: macbook_m3_max.
- Python 3.13.1; mlx and mlx-metal 0.31.2. The pinned packages equal `configs/bytes/identity_pins.json` at `6731d5249`.
- Telemetry: powermetrics; rails = cpu_power + gpu_power + ane_power.

**Geometry check.** Passed on all 16 check receipts and all 4 hour receipts.

**Receipt digests.** The reader prints sha256 of each receipt serialized as sorted-key JSON (`json.dumps(receipt, sort_keys=True)`):
- 01-R `7ce4b17fca15ca6f2446092641d50f9c8c4ba6a14ef1396b6aab648a3d3b5377`
- 02-C `cd1024bc63a354b06bbaecd6205ca7f616bb66a1faec2bf4df0081a8fd0b5c02`
- 03-C `0eb93b9819d46cd92057ec6bb11eb546e822eb6d15d89e9f845451fc5e80a4de`
- 04-R `a1d8a676ab03d534d1c8f06be352580f0c421c13973562f2a8e33a1db104d66c`

The archived files, by file sha256 (`runs_bytes_stream_test/capture/`):
- `calls/01-R.json` `c205eab7f89071b7df424e67c70a4974b72697f6d2c725b6f356f3eac2d4e4b6`
- `calls/02-C.json` `bdd94ea15038e5ffedc01ff6fb1a4e4a0c4cdc249ce5529614dfe8c46b8eada5`
- `calls/03-C.json` `6b082ab1f02375752d48e74ef15e7a3957d89670f8ae5c92da20cd726108dde0`
- `calls/04-R.json` `603ae5ce2e7b6e7ce121e410ce88d2e76bcc5f7bcf7b9902b9c7a9dca7a3aa77`
- `CHECK_RECEIPTS.json` `268114ea7def40a9eb7bd82e61a03d987860ddcfd0e4bc3bc1b33397133e3889`
- `CHECK.json` `dc66a3d24fcfce28953b362cceeb6d269805c7ce5cbf67318b6b3407dee3d453`
- `raw/powermetrics.plist` `def4512146c46de34b253b3cfa6b4d7b3e8f94dae9f66f17c934e13c7b0f34be`

**Sentence.** "The test identifies memory-traffic energy on a boundary, not whether it is the memory controller, the fabric or the GPU waiting on memory; on rest it does not separate the memory chips from power conversion and fans."

**Reg. §1 wording on admission** (rule §4; changes no number). "Whether the GPU rail includes the memory controller is measured by the known-bytes stream test" becomes "Whether memory traffic costs energy on the GPU rail, on rails and on rest is measured by the known-bytes stream test".

## Description (no class reads these)
- Rails share f = Δ_rails / Δ_DC = 0.238 ± 0.098.
- GPU-rail excess-power contrast, R − C: 0.144 W.
- Hour per-dispatch times: t_R = 314.94 µs and t_C = 289.98 µs, so D_hour = 24.96 µs, against the check's 33.10 µs. κ is fixed by the check (rule §4), and the hour contrast is printed so that a change during the hour is visible. In the hour, C ran 6.0 µs slower than in the check while R ran 2.1 µs faster. GPU frequency did not differ between the arms (next item). Had ρ_L been computed from the hour's timing, κ would be about 21.5. No class reads κ when RESOLVED.
- GPU state per arm: active frequency 1379.6 MHz (R) and 1379.6 MHz (C), within 0.08 MHz of each other; active residency 0.99992 (R) and 0.99995 (C).
- OS thermal level 0 on every journal reading in every span (611 readings inside the four streams). The reader prints `not defined (thermal journal missing)` here because of a parsing defect (correction 3 below). This line is taken from the journal directly, as both seats read it.
- Battery: on adapter, full, not charging. The battery term is 0 J with v = 0 in every call: B0AC = 0 on every in-session read.
- Meter: no gaps, no restarts. Clock: kernel frequency word 0 ppm throughout, and wall minus RAW spread 8.4 µs over the hour.
- Timing: r_max = 16.08 ms, τ = 2.210 s, operative timing bound 0.03961 s.
- **What the contrast is made of** (seat decomposition, Δ = [P_C(t_R − t_C) + (P_R − P_C) t_R] / b, where P is an arm's excess power over its streams):

  | boundary | longer-dispatch part | power-rise part | time share |
  |---|---|---|---|
  | rails | 0.00815 | 0.00110 | 0.88 |
  | GPU rail | 0.00744 | 0.00135 | 0.85 |
  | rest | 0.01435 | 0.01530 | 0.48 |

  On the GPU rail, 85% of the contrast is the same ~10 W drawn for 25 µs longer per R dispatch, the stall-time outcome rule §0 expected. GPU RESOLVED therefore shows that the GPU stays powered while it waits on memory, not that the memory controller is on the GPU rail. Rest carries the only sizeable power rise (1.63 W), and three quarters of the DC contrast is in rest. That is far more than conversion loss on the rails' own rise could supply.
- Regime: the matched dispatch reads at 106.5 GB/s (R) and 115.7 GB/s (C), below the SoC's DRAM bandwidth. The 32 MiB launch is latency-bound, so transfer to bandwidth-bound decode traffic is a stated limit of this test.

## Disclosures (bounded; none changes a class)
1. **Call 3's pre-idle span** carries a photoanalysisd episode (CPU rail up to 5.05 W). Its rails pre-idle mean is 0.259 W, against 0.035-0.106 W for the other spans. This raises the C arm's idle baseline and moves central Δ_rails by about +3.2e-4 J/GB toward RESOLVED (Fable) or +4.5e-4 J/GB (Opus). Both seats find that the baseline row already charges it: call 3's baseline bound is 217 J, about 0.0012 J/GB of δΔ_rails. Δ_rails − δΔ_rails = 0.0072 J/GB even with the shift removed.
2. **Background daemons inside the hour.** The contention monitor records 29 to 37 ten-second intervals (counts differ by span selection) in which one daemon was above the 0.05 CPU-s/s per-process limit: corespotlightd, softwareupdated, signpost_reporter, fseventsd and photoanalysisd, each at most 0.56 CPU-s/s. The aggregate never exceeded its limit, and the hazard verdict was PASS. Inside the streams the activity falls in both arms. Its asymmetry is about 4.5e-6 J/GB on Δ_rails, 0.2% of δΔ_rails.

## Corrections from the cold gate (lead's dispositions)
1. **The lag count (both seats' MAJOR).** Rule §3 names the estimator as "a Newey–West estimate with a 10 s Bartlett bandwidth" (method `duration_weighted_newey_west_bartlett_10s_iid_floor_v2`, the pass-1 method). Its next clause glosses that bandwidth as "(10 Hz, 100 lags)". powermetrics was asked for 100 ms but delivered about 130 ms in the idle spans. So the reader's lag count of floor(10 s / per-span median interval) = 75-77 follows the named 10 s estimator, while a literal 100 lags would span about 13 s. The two readings move δΔ_rails by 3.26e-5 J/GB, 1.6 times the rails bar. **Disposition:** the result above uses the named estimator, as run. The rule text (on the KB lineage, `codex/2026-10-30-kb-capture`) is to read "lag count floor(10 s / median native interval) per span; 100 at the nominal 100 ms cadence". This choice moves no class, and the rule's own battery formula already uses it. Because the choice was settled after the data existed, the literal reading is printed beside the result as a labelled alternative:
   *Labelled alternative (100 lags, rule §3's literal gloss): rails 0.0092 ± 0.0020 J/GB, rest 0.0296 ± 0.0084 J/GB, f = 0.238 ± 0.097. Every class is unchanged (rails RESOLVED, Δ − δΔ = 0.0072).*
2. **GPU edge row (both seats' minor).** Rule §3 says the GPU rail uses the rails anchor-shift bound, "which is never smaller because GPU power never exceeds rails power". That is false for the two-edge envelope: at call 2 the GPU envelope is 0.18661 J and the rails envelope 0.18134 J. The harvest already uses the larger of the two for both rows (`scripts/bytes_stream_harvest.py:286`), which is conservative, and the effect is 3e-8 J/GB. The text is to read "the larger of the rails and GPU-rail envelopes"; applied with item 1 at the KB lineage's next change.
3. **Thermal description (Opus minor).** The reader treats a JSON null leaf as missing (`scripts/bytes_stream_test.py:168, 1073-1075`), and every journal row carries `"error": null`. So the reader prints "thermal journal missing" although 712 valid in-session readings exist. Description only; the line above is taken from the journal. Code fix deferred to the KB lineage's next change.
4. **ρ_L printed precision.** The reader prints 0.0714. Rule §3 requires 4 significant figures, so the slot prints 0.07140. Code fix deferred with item 3.
5. **Receipt digests.** Both forms are given above.
6. **Inherited constants without a derivation in this rule** (clock-fit filters: 3 ms RTT, response cap 63, 10 s bins, 20 points; T_chk and the three-call planning; the 140 W adapter rating, which enters only the gap charge, 0 here). All are inert for this result. Recorded as a flag for the rule's next revision.
7. **Not executed by either seat:** an independent re-derivation of the operative timing bound (0.03961 s, taken from the pass-1 b6 calibration at harvest). Both seats bound its effect directly instead: shifting the whole trace by ±39.6 ms moves Δ_rails by at most 3.0e-6 J/GB, and the anchor is pinned to ±0.06 ms.
