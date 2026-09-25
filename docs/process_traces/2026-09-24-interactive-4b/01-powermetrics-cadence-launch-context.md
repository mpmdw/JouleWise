# Powermetrics cadence: the 248 ms is launch context, not the 25G83 binary

Interactive Fable seat, Ed present, 2026-09-24 ≈17:50–18:05 PDT, macOS 26.6.2 build 25G83, Mac15,9, AC power, `pmset powermode 0`.
Nothing was armed (`launchctl list` showed only `com.joulewise.magistrate`). Agent sessions were active, so this is a diagnostic, not a quiet-machine measurement.

## Why this was run

Ed challenged the premise of ACCEPTANCE-25G83-01 (activation 278ebc9e record 74): "be very sure powermetrics changed". The magistrate's answer (record 69, Gmail `1a0d4d7081f2e57d`) rested on the binary SHA changing (`d1dccad0…` to `b762e5bf…`). Every OS update changes that hash, so it is not evidence of a behaviour change. It then asked Ed to run a sudo probe. **That was an artificial owner stop (D-183).** `sudo -n /usr/bin/powermetrics` works passwordless for the agent, exactly as it does for the night harness.

## Executed evidence

The parser reads every NUL-separated plist record and takes `elapsed_ns`, dropping the first sample. The argv is the production one: `-b 0 -i 100 --format plist`, 60 samples per run.

### 1. Interactive shell, sampler subsets, two interleaved repeats

| Samplers | r1 median | r2 median | p95 |
|---|---|---|---|
| cpu,gpu,ane,thermal (production) | 117.8 ms | 117.5 ms | 120.1 ms |
| cpu,gpu,ane | 119.0 | 119.1 | 120.5 |
| cpu | 115.1 | 115.2 | 116.0 |
| gpu | 107.5 | 107.5 | 108.2 |
| ane | 101.2 | 101.2 | 101.2 |
| thermal | 101.3 | 101.3 | 101.4 |
| cpu,gpu | 118.9 | 119.4 | 120.7 |

**The 25G83 binary delivers ≈118 ms with the production argv, matching July's 120.3 ms on 25F84.** The `thermal` sampler is not the cause.

### 2. Same parser on archived 25G83 captures

| Capture | median | p05 | p95 |
|---|---|---|---|
| 09-19 n1 d01 | 244.3 ms | 133.5 | 274.0 |
| 09-19 n1 d06 | 245.8 | 135.4 | 273.1 |
| 09-19 n1 d12 | 248.6 | 140.8 | 273.9 |
| qpe01 09-23 envelope-01 | 247.9 | 147.7 | 277.6 |

The parser reproduces the scout's 248 ms, so the difference is in the conditions, not the measurement.

### 3. Identical argv under throwaway launchd jobs (gui domain, dummy labels, booted out after)

| launchd job | r1 median | r2 median | p95 |
|---|---|---|---|
| no `ProcessType` (what `night_agent_install.py` renders) | 171.0 ms | 177.9 ms | ≈200 ms |
| `ProcessType = Interactive` | 126.7 | 126.3 | 128.5 |

launchd.plist(5): an unspecified ProcessType gets "light resource limits … throttling its CPU usage". The 09-19 derivation captures and the qpe01 pilots ran under the launchd night agent (`launchd.night.err` in the harvests; the installer landed 2026-09-15). The July r6 corpus predates it.

## Conclusion and what remains open

- **Cause (strongly supported):** the slowdown follows the launch context. A default-ProcessType launchd job throttles powermetrics. The gap between the daytime default job (≈175 ms) and the night captures (≈248 ms) is not reproduced yet. The likely extra factor is display-sleep timer coalescing at night. That is untested.
- **Consequence for ACCEPTANCE-25G83-01:** its premise, that the 25G83 powermetrics binary samples at ≈245 ms, is false. Option A (restore the cadence) is back on the table. The likely cure is `ProcessType Interactive` in the night-agent plist, not a 2 s pulse.
- **Science concern, wider than the instrument:** if the launchd night agent throttles CPU, the inference workloads it launches may be throttled too. Any energy or latency number from a launchd night needs this checked before claim use.
- **Next evidence the council needs, all agent-runnable:**
  1. One Interactive-ProcessType capture during a real display-asleep window.
  2. A check of whether the workload children inherit the throttling. Compare `taskpolicy` or QoS for a child under each ProcessType.

Raw plists and the parser are in the interactive seat's scratchpad and are not tracked. The tables above are the record.
