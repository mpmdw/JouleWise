# R1 thermal replay: D members against their own pre-warmup reference

2026-11-11 05:10 PST. Research-lead ruling RL-59, item 4, step 1. Custody `/Users/edr/night-align/r1-20261111T043229Z`
(MBP), build `da3187e6e`. Script `scripts/align_r1_thermal_replay.py`, tests `tests/test_align_r1_thermal_replay.py`,
inputs `docs/run_reports/2026-11-11-r1-thermal-replay.manifest.json`.

## Answer

All nine D-type G0 gates would have released inside the 1,200 s cap if each member had been gated against its own
pre-warmup 60 s median. That covers the seven that timed out at R1 (A-B-A legs A1, B and A2, step-D twice, planning +0 °C
twice) and the two that released (planning +2 °C and +4 °C). Release times run from 728 to 889 s for the members that timed
out, and planning +4 °C and +2 °C are unchanged at 462 and 694 s. Each D member's own idle sits 1.18 to 1.92 °C above
R_op on the slow sensor and 0.11 to 0.16 °C above it on the fast sensor. Against R_op the slow sensor sat between 0.05 °C below and 0.64 °C
above the band edge at the cap. Leg B's slow sensor touched the R_op band on only three isolated samples, at 1,148, 1,152 and 1,172 s, so it never held 10 consecutive samples. Against its own reference it sat 0.88 to 1.45 °C below the edge, so the slope bar decides
the release, as RL-32 expects of W1's gate.

## Self-check

The rule was replayed against the reference each gate actually used at R1, on all 13 recorded G0 intervals: the nine D
members, step-30b, and the three release-against-soak sessions before the legs (600 s cap). The replay reproduces every
recorded outcome. Each replayed release lands within 1.0 s of the recorded wait, and the replay is always slightly
early (step-30b 714.95 s against 715.86 s recorded; release before B 580.03 s against 580.63 s). That is the expected
effect of polling at the moment each sample arrives instead of on the live 1 s loop. Read the own-reference release
times as about 1 s early. The recomputed step-30b pre-warmup median equals R_op bit for bit (fast 34.1641960144043 °C, slow
27.0440616607666 °C), which validates the warmup anchor. Replaying with the os_level and pm_state conditions disabled
(`--ignore-status`) leaves every outcome and time unchanged.

## Printed output

```
R_op (step-30b pre-warmup 60 s median, recomputed): fast 34.164 C, slow 27.044 C; band d_fast 1.0 C, d_slow 1.5 C; cap 1200 s; status conditions applied

Self-check: the rule replayed against the reference each gate actually used
| member | recorded ref slow C | recorded | replay | recorded wait s | replay wait s |
|---|---|---|---|---|---|
| step_30b | 27.044 | released | released | 715.86 | 714.95 |
| high_power_A1 | 27.044 | timeout | timeout | 1200.05 | 1200.43 |
| high_power_B | 27.044 | timeout | timeout | 1200.05 | 1200.65 |
| high_power_A2 | 27.044 | timeout | timeout | 1200.06 | 1200.55 |
| step_D (first try) | 27.044 | timeout | timeout | 1200.04 | 1200.15 |
| step_D (retry) | 27.044 | timeout | timeout | 1200.03 | 1200.21 |
| planning +4C | 31.044 | released | released | 463.11 | 462.11 |
| planning +2C | 29.044 | released | released | 694.56 | 694.37 |
| planning +0C (first try) | 27.044 | timeout | timeout | 1200.05 | 1200.53 |
| planning +0C (retry) | 27.044 | timeout | timeout | 1200.06 | 1200.25 |
| release vs soak before A1 | 27.044 | timeout | timeout | 600.02 | 600.01 |
| release vs soak before B | 27.044 | released | released | 580.63 | 580.03 |
| release vs soak before A2 | 27.044 | timeout | timeout | 600.03 | 600.02 |

SELF-CHECK PASSED: every recorded G0 outcome is reproduced (released waits within 2.0 s), and the recomputed step-30b pre-warmup median equals R_op exactly.

Own pre-warmup reference (planning: own slow median + designed offset; fast ceiling 150 C)
| member | own-R_op fast C | own-R_op slow C | at cap: slow - R_op edge C | at cap: slow - own edge C | at cap: slope C/min | own-ref G0 | own-ref release s |
|---|---|---|---|---|---|---|---|
| step_30b | +0.000 | +0.000 | released | released | released | released | 714.95 |
| high_power_A1 | +0.146 | +1.502 | +0.051 | -1.452 | -0.036 | released | 728.41 |
| high_power_B | +0.124 | +1.225 | -0.046 | -1.270 | +0.031 | released | 877.65 |
| high_power_A2 | +0.114 | +1.176 | +0.056 | -1.119 | -0.177 | released | 862.54 |
| step_D (first try) | +0.159 | +1.547 | +0.622 | -0.925 | -0.135 | released | 753.16 |
| step_D (retry) | +0.143 | +1.542 | +0.644 | -0.897 | -0.130 | released | 815.21 |
| planning +4C | +0.138 | +1.414 | released | released | released | released | 462.11 |
| planning +2C | +0.163 | +1.924 | released | released | released | released | 694.37 |
| planning +0C (first try) | +0.129 | +1.397 | +0.313 | -1.084 | -0.093 | released | 888.53 |
| planning +0C (retry) | +0.118 | +1.295 | +0.416 | -0.879 | +0.049 | released | 869.25 |
```

The "at cap" columns use the last sample the gate saw before its 1,200 s timeout. The "R_op edge" is the recorded G0
reference plus 1.5 °C, which for the planning turns is R_op + offset + 1.5 °C. The "own edge" is the member's own reference plus
1.5 °C. The slope is the OLS slope of S_slow over the preceding 60 s.

## Rule and parameters (cited at `da3187e6e`)

- Reference capture (`thermal_gates.py:396-414`, `:220-234`): the median of S_fast and S_slow over [warmup entry − 60 s,
  warmup entry). It needs a 1 s read bracket, valid values, and grid coverage of at least 0.9 (`thermal.py:195-267`).
- G0 release (`thermal_gates.py:459-593`): 10 consecutive good samples (`:487`). A sample is good when all of these hold:
  the gate is observed (coverage ≥ 0.9, `:506-509`); the sample is continuous (≤ 2 s, `:516`) and fresh (≤ 2 s, `:518`);
  S_fast ≤ R_fast + δ_fast and S_slow ≤ R_slow + δ_slow (`:520-521`); |slope| ≤ 0.2 °C/min (`:525-526`); and os_level is 0,
  pm_state is Nominal, and the pm observation is ≤ 2 s old (`:527-528`). An unobserved gate stops at 300 s (`:537`).
- δ_fast = 1.0 °C (`r1_runtime.py:87`, `:409-425`; the soak's 3 SD falls below the floor). δ_slow = 1.5 °C (S6,
  `r1_slots.json:21`, RL-32). Cap = 1,200 s (`thermal_gates.py:24`, `r1_runtime.py:441`), and 600 s for the
  release-against-soak sessions (`:23`). All ten member configs carry exactly these values, with TV0h fast and Tf08 slow. The
  script refuses a manifest whose policy differs.
- Planning turns (`r1_runtime.py:1532-1545`) gate on (150 °C, R_op_slow + offset). For "own", they gate on (150 °C, own
  slow median + offset).
- Warmup anchor: `capture_reference` runs at the top of the runtime warmup (`workload.py:394-396`), right after the
  controller's `stage_started warmup` event (`controller.py:2445-2446`). On step-30b that event comes 1.6 ms before its
  recorded capture end, and the nearest sample lies 18 ms inside the window edge. For the D members the margin is
  42 to 419 ms. Every capture has 60 samples and coverage 1.0.

## Caveats

1. **Planning turns are not a true counterfactual.** A heater ran during their G0 and drove S_slow toward R_op + offset. With
   their own reference it would have aimed 1.3 to 1.9 °C higher, so the recorded trace is not the one an own-reference
   night would produce. The planning rows show only that the recorded trace meets the own-reference rule. The five
   gated members (the three legs and step-D twice) have no heater. Their G0 is an idle wait whose trace does not depend on the reference, so
   their rows are exact replays, about 1 s early.
2. RL-59 makes planning and the gated block consume **step-D's** reference, not their own. Step-D's own medians (slow
   28.59 °C) lie above the planning +0 °C members' own medians (28.34 and 28.44 °C), so step-D's band is the looser one.
   This replay does not compute that consume case.
3. Each A-B-A leg here is gated against its own reference after the night's release-against-soak session. RL-59 drops that
   session, so a follow-up leg would start warmer.

## Files read

Hashes were taken on the MBP before copying. The Air copies match, and those copies are in the session scratchpad, not the repo.

| path under `night/align-r1/` | sha256 |
|---|---|
| `high_power_A1/runs/align-v4-r1-high-power-aba-a1/outputs/align_thermal.jsonl` | `4cdf5ac31841530b3bf54e9f9fac305f56bfa507182f9a96e680dad27cad49ce` |
| `high_power_A2/runs/align-v4-r1-high-power-aba-a2/outputs/align_thermal.jsonl` | `bd6f0866c759990f853152cde183136e0ad616fabd3669b53277d2830ab9a141` |
| `high_power_B/runs/align-v4-r1-high-power-aba-b/outputs/align_thermal.jsonl` | `8e0a223776bff5b73079dfe117c3ee0192e487a689a56595a426d7715474e7d9` |
| `planning_turn_R_plus_0C.g0_timeout1/runs/align-v4-r1-d-planning-turn-r-plus-0c/outputs/align_thermal.jsonl` | `681587ba8f6ca013df5d8e3cd32c0272e7d8c7d2892d2351075da7267cfd5453` |
| `planning_turn_R_plus_0C/runs/align-v4-r1-d-planning-turn-r-plus-0c/outputs/align_thermal.jsonl` | `9feb77c3bc91b1237094158bba28605302e10c0a936e93ff09047f582ab7ed3e` |
| `planning_turn_R_plus_2C/runs/align-v4-r1-d-planning-turn-r-plus-2c/outputs/align_thermal.jsonl` | `3b3a9c0d68d8ef770f225c3c452d5e1336dea092d6d5b920d338f8581f7e5964` |
| `planning_turn_R_plus_4C/runs/align-v4-r1-d-planning-turn-r-plus-4c/outputs/align_thermal.jsonl` | `186fcc7f55454f83969ee79c21186b3ce823c0baa2f8e43f820901b09cb4550f` |
| `step_30b/runs/align-v4-r1-step-30b/outputs/align_thermal.jsonl` | `879bb4de8be9a0409cf1b8ead4ff766ff095eecd2ec1195b1a664847263bc810` |
| `step_D_prefill_10k_decode_4096.g0_timeout1/runs/align-v4-r1-step-d/outputs/align_thermal.jsonl` | `a941ef7ed5c611816a5b2625e11db21c7a87ca17256e6c84f481f61ab340105d` |
| `step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d/outputs/align_thermal.jsonl` | `f163771c6cbe15b8cc92a5d44abb3096d85ba859fecfc1f53e64a985708ca73e` |
| `high_power_A1.g0_release0/g0/align_thermal.jsonl` | `09ab7a0f66fdd5aa4e3d2a36d1c2ee79ede1ab96e4058fc01c2f34a0410673ab` |
| `high_power_A2.g0_release0/g0/align_thermal.jsonl` | `8ade03ad8efce7abeb99ca83d1c28e9a097e902e50fde6f829d500d881de45aa` |
| `high_power_B.g0_release0/g0/align_thermal.jsonl` | `3ada1485df30eec0e8e9318395ec4121702884dea304b42784bc36e713f7a18d` |
| `high_power_A1/runs/align-v4-r1-high-power-aba-a1/events.jsonl` | `ba2879e140bffd7fa8f3e93ae9a9fd2684b8f121ca8181f2ae46eb8ea5be477c` |
| `high_power_A2/runs/align-v4-r1-high-power-aba-a2/events.jsonl` | `044d2d2034f691bee06a3c66c8111940829ad3aa0a88863b77bbd55e0a79249f` |
| `high_power_B/runs/align-v4-r1-high-power-aba-b/events.jsonl` | `3e90f41722bc2d4afb3a55730d869a16c2e64e94c9911f70e627fcc582bafa0f` |
| `planning_turn_R_plus_0C.g0_timeout1/runs/align-v4-r1-d-planning-turn-r-plus-0c/events.jsonl` | `c9fdd72000902878035db77b040870dca9606857cbc86679d6646fd04bfb7d6a` |
| `planning_turn_R_plus_0C/runs/align-v4-r1-d-planning-turn-r-plus-0c/events.jsonl` | `40ac93b8041bc2835f98b29ff8a58d33424848a842bc067ced23769d5b3ddb69` |
| `planning_turn_R_plus_2C/runs/align-v4-r1-d-planning-turn-r-plus-2c/events.jsonl` | `f0c6764f8af9f7c47f58a458b5c1faa8cd79dc58fa9e57c44e702090771d9e46` |
| `planning_turn_R_plus_4C/runs/align-v4-r1-d-planning-turn-r-plus-4c/events.jsonl` | `8c3be9290929eac3e37edf76521d0dc93d6ea3aa6b86700ef658c59c0692c1d7` |
| `step_30b/runs/align-v4-r1-step-30b/events.jsonl` | `460adb91779d50dd188a5b462c51e2dfca0fc39d79a574f07ce9b5eac3153fb6` |
| `step_D_prefill_10k_decode_4096.g0_timeout1/runs/align-v4-r1-step-d/events.jsonl` | `bebe5fe90f0145905bc704494c7a7b0605963342566724e3eee547308f4299ef` |
| `step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d/events.jsonl` | `5b7adb3f40a5ae659a0c06dab62a4ae05726581ad35c38f6218a9520275ed3d5` |
| `high_power_A1/runs/align-v4-r1-high-power-aba-a1/config.json` | `598601d927e71dff5eae20500ad398eb20faca681ffae7213d3b9c8810d6f40e` |
| `high_power_A2/runs/align-v4-r1-high-power-aba-a2/config.json` | `437befe533d285e56159c74e0c12601a883cbf89921347d21895d840a13878f6` |
| `high_power_B/runs/align-v4-r1-high-power-aba-b/config.json` | `24e43c854f9d9ea7dcc24a0c465edcaaecf6ba1bca11153c3c7ac8a51d45dea5` |
| `planning_turn_R_plus_0C.g0_timeout1/runs/align-v4-r1-d-planning-turn-r-plus-0c/config.json` | `cbff16bc5b3ada4dc6a3d525ad9b3054200923f0678f535d862604f41bac9e3e` |
| `planning_turn_R_plus_0C/runs/align-v4-r1-d-planning-turn-r-plus-0c/config.json` | `cbff16bc5b3ada4dc6a3d525ad9b3054200923f0678f535d862604f41bac9e3e` |
| `planning_turn_R_plus_2C/runs/align-v4-r1-d-planning-turn-r-plus-2c/config.json` | `2d11e9c2f60256762935aecc0a4b73c873dc69afecb491a7bcdff87ad8c09875` |
| `planning_turn_R_plus_4C/runs/align-v4-r1-d-planning-turn-r-plus-4c/config.json` | `a6041c65c391fc6418a757a7c308d9f849c22989b82e9f3a4ddb2d18c6a3cc68` |
| `step_30b/runs/align-v4-r1-step-30b/config.json` | `bc5c5cca1ff3caedbe14a2ac15577a51c193c7f843bde0a4c5a5ba81c1e73898` |
| `step_D_prefill_10k_decode_4096.g0_timeout1/runs/align-v4-r1-step-d/config.json` | `bd528baafca8d77d2a44e7264a8fe5774ec017d5e1da5c6290e65bd1499f3d6d` |
| `step_D_prefill_10k_decode_4096/runs/align-v4-r1-step-d/config.json` | `bd528baafca8d77d2a44e7264a8fe5774ec017d5e1da5c6290e65bd1499f3d6d` |
| `step_30b/runs/align-v4-r1-step-30b/outputs/align_window_reference.json` | `7855d406675f4fdd11556fa5a187b30ec65c432a492090faca0cf72b4df96e66` |

What each file contributed:
- `align_thermal.jsonl`: every line was parsed and projected at once onto stamps, TV0h, Tf08, their read errors,
  status (os_level, pm_state, pm_observed_ns) and the recorded G0 interval.
- `events.jsonl`: only the `stage_started` and `stage_completed` timestamps of idle_baseline, warmup and measured_run
  were extracted, by a read-only command on the MBP. The file was not copied.
- `config.json`: only the thermal gate policy (sensors, δ_fast, δ_slow, g0_cap_s, window_reference) was extracted,
  read-only on the MBP. The file was not copied.
- `align_window_reference.json`: copied. Its R_op values and span were used.

## Commands

Every MBP command was `ssh -o ConnectTimeout=8 -o BatchMode=yes mbp-ts '<cmd>'`, starting 2026-11-11 12:56 UTC:

1. `launchctl list | grep joulewise; date -u` returned only `com.joulewise.magistrate`, both at the start and again just before the copy.
2. `ls` and `find . -name 'align_thermal*.jsonl'` and `ls -la` of the journals in `night/align-r1`.
3. `shasum -a 256` of the 13 journals, the 10 `events.jsonl`, the 10 `config.json` and `align_window_reference.json`.
4. `tar cf - <13 journals> <align_window_reference.json>` piped to `tar xf -` into the scratchpad on the Air, followed by re-hashing on the Air (all match).
5. `/usr/bin/python3 -I -c` that read the stage timestamps from each `events.jsonl`, and one that read the thermal policy from each
   `config.json` (`workload_profile.prompt_text`, parsed as the member spec).
6. On the Air: `python3 -I scripts/align_r1_thermal_replay.py --manifest docs/run_reports/2026-11-11-r1-thermal-replay.manifest.json
   --root <scratchpad>/r1-journals`, which exits 0, and the same command with `--ignore-status`, which gives identical verdicts. CPU time is about 10 s.

Nothing was written on the MBP.

## Blinding

The report holds temperatures, deltas, slopes and times only. There is one disclosed slip. Before the stage filter was written, an
exploratory listing of step-30b's `events.jsonl` printed event types and timestamps for its first 60 events, about 40 of them
decode token timestamps. Those are the 30B positive control's, not a v4 or D outcome. No energy, power or token value was
printed, and no D member's events were listed unfiltered.
