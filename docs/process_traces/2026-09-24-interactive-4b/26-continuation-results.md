# OSCTX-MVP-01 continuation (session C): results

Run 2026-09-25 00:24–01:16 PDT under registration v2.5 (24), harness `fix/2026-09-24-osctx-mvp-r3` at 845b1cc5 (fix round 8 plus the F14 bench fix; audit 6 in 25). Data: `/Users/edr/osctx-mvp-01/sessionC1/`, with copies of the summary, the session record and both ledgers in `sessionC1/` here.

Conditions:
- Ed away: HIDIdleTime > 13,000 s at admission. The display was on at Ed's brightness (powerd assertion).
- Network time was paused. The magistrate was drained (≥ 300 s loops).
- signpost_reporter (36 % CPU) was watched until it left the top of the CPU list before launch. It still consumed 24.7 CPU-s during the discarded warm-up cell.
- Chronology: the session started at 00:17:58, the first accepted cell at 00:21:39, and the session ended at 01:15:48.

Every cell was **diagnostic-valid** (the v2.3 C1 predicate), the analyzer reported zero errors, and the only discard was the preregistered warm-up. Every bundle's claim precheck remains **ineligible**, because environment admission and instrument calibration are missing. That is why no number here is claim-bearing.

## Primary result (C1: I vs SH, 6 Williams blocks, 1 production run per cell, a single look)

| Contrast | Ratio SH/I, 99.375 % interval | Verdict | Absolute E contrast (J/token) |
|---|---|---|---|
| E, J per output token (idle-subtracted, whole request) | **0.99991** [0.99548, 1.00435] | **EQUIVALENT (nominal, under amended v2.5 C3; attribution unresolved; widened interval crosses δ: yes)** | −0.00004 [−0.00176, +0.00169] |
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

**In two probe-only D cells on the quiet machine, the CPU probe showed no slowdown.** This is descriptive: the D and B probes ran cold, with no preceding 200 J production run, while the I and SH probes ran hot after one, so the 2 % D advantage may be thermal. The probes pool 18 repeats per I/SH arm and 6 per D/B arm. The D probes were not run at the same time as the session-2 timeouts. The observed QoS classes fit this mechanism: D's processes run at 0x11 UTILITY, the class whose wake-ups macOS may coalesce, so powermetrics wakes late and 300 samples overrun production's 55 s bound. Timer coalescing as the sole cause is an inference, not proven here. B shows that the probe does see throttling when present. This supports the council's scoping: D's energy bias is unmeasured, but its compute is not throttled.

## Census: the "lagging OS processes" question

7 of 12 C1 cells carry `census_cpu`: some process other than the workload, its powermetrics and the census used ≥ 5 % of a core in a segment. CPU time consumed over the whole of C1 (all cells, from the 5 s `ps` census):

Totals below span **13 cells including the discarded warm-up** (12 inferential cells).

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

These processes are associated with the flags; the census does not show that any of them caused an energy effect. The primary result holds with every cell retained, and the flags are disclosed. Wispr Flow is the largest non-agent, non-OS consumer, averaging 5.3–5.8 % of a core per cell. That is an average at the census's 5 s resolution, not a continuous level.

The largest single flags: corespotlightd at 30 % of a core in C1-04 SH's idle segment, and PerfPowerServices at 16 % in C1-03 I. Run-segment flags (≤ 9 %) occur in C1-05 I and C1-06 SH. Other flag contributors: runningboardd, ControlCenter and mds_stores. A flag means a census interval overlapping a sampling window, with allowlisted processes excluded. It is not necessarily interference during the request.

## What this establishes, and what it does not

1. **(F-A, session 2)** In the tested configuration, the default-launchd production run failed closed on all three attempts, at production's 55 s idle-baseline bound, with delivered cadence 237–248 ms. The later D probe showed no CPU slowdown. The mechanism is attributed to utility-QoS timer coalescing of the sampler, as an inference.
2. **ProcessType=Interactive** gives production measurements **nominally** statistically equivalent, within 3 %, to a contemporary shell launch on E (attribution unresolved: the widened interval crosses δ) and on R. This holds **for the tested workload only**: one fixed prompt, Qwen2.5-7B-Instruct-4bit, 512 output tokens, an ≈ 6.4 s measurement window, and one evening. The SH arm is a detached `caffeinate -is zsh` descendant of the Claude Code session in Terminal.app, at QoS 0x21 USER_INTERACTIVE. I ran at 0x15 and B at 0x09. Every I run completed with margin. It is a supported candidate for the night job's launch context. **Installation is gated:** a PR and the council under D-184.
3. **Not established:**
   - equivalence to the July shell path (SH is contemporary: a different OS build and harness);
   - transport to other nights (one evening);
   - display-asleep behaviour (Ed's habit is brightness 0 with the display on, which is what was tested);
   - any bias of D when it can complete.
4. **No number here is claim-bearing.**

## Corrections and additions from the results reviews (Astra 27, Fable seat; both "STAND WITH LISTED CORRECTIONS")

Both reviewers independently recomputed the paired intervals from the raw ledger-selected bundles (t = 4.5257, df = 5), and both match the numbers above exactly. The lead's own recomputation matches too. The corrections above were applied in response to their reports. Further disclosures:

- **Formula of the widened interval** (so it can be replicated).
  - For each cell, B = the per-run attribution bound (anchor-shift + drift + edge energy bounds, in J), and net = the idle-subtracted request energy.
  - Each side of the nominal log interval is widened by the mean over the 6 pairs of [−ln(1 − B_SH/net_SH) − ln(1 − B_I/net_I)], with no √n shrinkage (`analyze.py`, the `log_bound` helper inside `decision_table`).
  - The result is [0.861, 1.161]. The Fable seat's reading of the 22 spec gives [0.866, 1.154]. Every variant crosses δ, so the disclosure stands either way.
- **Amendments after data.** C3 v2.5 and the R5 purpose-based cure test were both adopted **after observing stage0U** (registration 24 labels them so).
- **Astra's dissent.** Repeatability, a small SD of E, cannot exclude a **stable, arm-correlated** bias. Only an attribution bound can, and the worst-case one fails to exclude one.
- **Network time.** Both `systemsetup` calls returned rc 0, but each printed a `### Error:-99` log line, so "paused" rests on the return code. Every anchor bound was ≤ 4 ms, so a clock step would have shown, and none did.
- **Brightness.** The powerd assertion proves only that the display was on. Brightness 0 is Ed's stated habit and was not measured.
