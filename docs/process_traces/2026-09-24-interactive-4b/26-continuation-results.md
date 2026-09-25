# OSCTX-MVP-01 continuation (session C): results

Run 2026-09-25 00:24–01:16 PDT under registration v2.5 (24), harness `fix/2026-09-24-osctx-mvp-r3` at 845b1cc5 (fix round 8 plus the F14 bench fix; audit 6 in 25). Data: `/Users/edr/osctx-mvp-01/sessionC1/`, with copies of the summary, the session record and both ledgers in `sessionC1/` here.

Conditions:
- Ed away: HIDIdleTime > 13,000 s at admission. The display was on at Ed's brightness (powerd assertion).
- Network time was paused. The magistrate was drained (≥ 300 s loops).
- signpost_reporter (36 % CPU) was allowed to settle before t0.

Every cell was valid, the analyzer reported zero errors, and the only discard was the preregistered warm-up.

## Primary result (C1: I vs SH, 6 Williams blocks, 1 production run per cell, a single look)

| Contrast | Ratio SH/I, 99.375 % interval | Verdict | Absolute E contrast (J/token) |
|---|---|---|---|
| E, J per output token (idle-subtracted, whole request) | **0.99991** [0.99548, 1.00435] | **EQUIVALENT** | −0.00004 [−0.00176, +0.00169] |
| R, inter-token tokens/s | **0.99471** [0.99192, 0.99751] | **EQUIVALENT** | |

- Per-cell E: I 0.3883–0.3914, SH 0.3884–0.3906 J/token. R: I 84.07–84.35, SH 83.73–83.86 tok/s.
- SH is 0.53 % slower in R, and the interval excludes 1. The difference is real but far inside δ = 3 %. It is consistent with the stage0U and attended observations (SH ≈ 0.5–1 % slower).
- **The C3 v2.5 stability gates pass.** The per-arm SD of log E is well under 1 %, and every idle baseline is ≤ 1 W (I mean 0.11 W, SH 0.16 W).
- **Disclosures:**
  - The widened interval (worst-case anchor + drift + edge bounds) is [0.861, 1.161]: **it crosses δ**.
  - The **v2.3 C3 outcome would have been INCONCLUSIVE-by-attribution**, because the drift bound ÷ net was 5.4–12.0 % per cell.
  - Astra's dissent (22) stands.

## The cure test (R5)

| Test | Result |
|---|---|
| Original v2 criterion: I median idle cadence ≤ 130 ms | **not met** (131.8 ms) |
| Purpose-based test: all I production runs valid (C1 I invalid attempts = 0) and median ≤ 150 ms | **met** |
| Production margin: 300 × cadence | 39.6 s against the 55 s bound |

## Mechanism probe (descriptive, outside inference)

| Context | Median CPU-probe seconds | Ratio to I |
|---|---|---|
| I (launchd Interactive, after production runs) | 7.694 | 1.00 |
| SH (shell, after production runs) | 7.614 | 0.99 |
| D (launchd default, probe-only) | 7.556 | **0.98** |
| B (launchd Background, probe-only) | 57.27 | **7.44** |

**On the quiet machine, the default context does NOT throttle a CPU-bound workload.** Its failure in session 2 is the sampler's timer coalescing: powermetrics wakes late, so 300 samples overrun production's 55 s bound. It is not slowed compute. B shows that the probe does see throttling when present. This supports the council's scoping: D's energy bias is unmeasured, but its compute is not throttled.

## Census: the "lagging OS processes" question

7 of 12 C1 cells carry `census_cpu`: some process other than the workload, its powermetrics and the census used ≥ 5 % of a core in a segment. CPU time consumed over the whole of C1 (all cells, from the 5 s `ps` census):

| Process | CPU-s | Cells present |
|---|---|---|
| claude (the two resting agent sessions) | 129 | 13 |
| Wispr Flow + Wispr Flow Helper (Renderer) (Ed's dictation app) | 153 | 13 |
| WindowServer | 33 | 13 |
| launchd | 29 | 13 |
| mediaanalysisd | 18 | 13 |
| coreaudiod | 16 | 13 |
| com.apple.DriverKit-AppleBCMWLAN / airportd (Wi-Fi) | 21 | 13 |
| corespotlightd | 12 | 4 |

These processes are associated with the flags; the census does not show that any of them caused an energy effect. The primary result holds with every cell retained, and the flags are disclosed. Wispr Flow is the largest non-agent, non-OS consumer, at ≈ 5 % of a core throughout.

## What this establishes, and what it does not

1. **(F-A, session 2)** An unchanged default-launchd night job cannot run production measurement on a quiet machine: it fails closed. Its compute is not throttled; its sampler is.
2. **ProcessType=Interactive** gives production measurements statistically equivalent, within 3 %, to a contemporary shell launch on both E and R. Every I run completed with margin. It is a supported candidate for the night job's launch context. **Installation is gated:** a PR and the council under D-184.
3. **Not established:**
   - equivalence to the July shell path (SH is contemporary: a different OS build and harness);
   - transport to other nights (one evening);
   - display-asleep behaviour (Ed's habit is brightness 0 with the display on, which is what was tested);
   - any bias of D when it can complete.
4. **No number here is claim-bearing.**
