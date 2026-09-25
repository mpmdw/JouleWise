# OSCTX-MVP-01: blind pre-decision review (Fable 5.1 seat, read-only, main 7dd24d7b)

Filed by the lead from the seat's hand-back message, verbatim apart from formatting.

**Verdict: RUN WITH CHANGES.** The measurement plan is basically the right shape. As drafted, though:
- it cannot reach its own "within the bar" verdict;
- its census would miss the processes most likely to contaminate a cell;
- its story of *why* the night cadence is 248 ms is not what the archived captures show.

## Executed evidence (this seat, read-only)

1. **Archived captures.** Re-parsed qpe01 09-23 envelopes 1–3 and d079 n1 d01/d06:

| Capture | Local time | Mean package power | Median gap | Gaps >220 ms | Gaps <160 ms | Power in short / long gaps |
|---|---|---|---|---|---|---|
| qpe01 envelope 1–3 | 07:10–07:31 PDT | 0.38 W (no workload) | 248 ms | 72 % | 7 % | 1.5 W / 0.2 W |
| d079 d01 | 00:10 PDT | 13.2 W (loaded) | 244 ms | 67 % | 12 % | 18.1 W / 12.1 W |

The 248 ms appears at 0.38 W with nothing running. Gap length is capped at ≈275 ms, and the rare short gaps coincide with moments of higher power. That is the signature of **timer coalescing**: the kernel may delay a low-priority thread's wake-up by a "leeway" so that cores stay asleep. On a quiet machine the leeway is used in full; it is cut short whenever anything else wakes a core. `sysctl kern` shows `kern.timer.coalescing_enabled=1`, with per-priority caps up to 75 ms (tier 3) and 100 ms (background). So daytime 175 ms (agents active) against 248 ms (quiet machine) needs no new "unattended state tightens the throttle" mechanism. This predicts that the Interactive context stays ≈126 ms in every state and the default context drifts with how quiet the machine is.

2. **Pilot noise.** Same-context cell-to-cell median ratios: CPU loop D 1.050, I 1.030, shell 1.026; LM I 1.034. The between-cell noise of the CPU loop (3–5 %) is larger than the ±3 % bar.

3. **Production integration.** `joulewise/reduce.py:_integrate` sums power_w × overlap(sample support, window). `uncertainty_evidence.py:108` confirms that power_w × elapsed_s equals the plist energy counters to ~1e-4 J. idle_subtracted = gross − idle_mean_w × duration. No `ProcessType` appears in any template. The night chain execs Python directly, with no caffeinate, nice or taskpolicy, so every child inherits the launchd job's role.

4. **Live state.**
   - fseventsd runs at 10 % CPU and mds at 3 %.
   - The magistrate job fires every 300 s.
   - An agent-owned caffeinate assertion is live.
   - DAS logged 588 STARTING events in 2 h, but every activity name is `<private>`.
   - Brightness is not readable through ioreg; corebrightnessdiag exists.

## Findings

| # | Mechanism | Matters? | Detection | Change |
|---|---|---|---|---|
| 1a | Timer coalescing | explains the cadence; does not bias energy (each sample carries its own counter) | idle-segment vs LM-segment cadence | SHOULD_FIX: rewrite §1 to the leeway mechanism; drop Q3 |
| 1b | E-core placement of utility threads on a quiet machine | the real threat; it is what state U tests | per-cluster residency in the LM segment plus `launchctl procinfo` | SHOULD_FIX: add procinfo; state that the pilot's D≈I does not transfer to U |
| 1c | I/O throttling of the default role | affects model load, not per-token energy; contaminates first cells via a cold page cache | a model-load segment | SHOULD_FIX: pre-read the model; a discarded warm-up cell; alternate the starting context |
| 1d | Maintenance daemons and the 5-min magistrate tick | fseventsd is at 10 % now | the draft's one-shot ps misses these | **BLOCKER** (see 5) |
| 1e | Brightness 0 vs display asleep | owner's question | GPU idle power and residency U vs S; pmset -g log; corebrightnessdiag | SHOULD_FIX: promote Q4 |
| 1f | sudo and powermetrics' own cost | sudo does not reset task policy | ps cputime of powermetrics | NIT |
| 1g | App Nap, Metal priority, thermal, Power Nap | App Nap n/a to a non-app child; GPU unaffected even under B | thermal_pressure per segment | NIT |

- **Statistics, BLOCKER.** Three cells per context cannot reach "within the bar": at n = 3 the 95 % interval is ±5 % or wider. The minimum change:
  - 6 interleaved D–I pairs per state, and B ×2;
  - primary metric: 7B decode J/token and tokens/s;
  - the CPU loop becomes a mechanism probe only;
  - per pair, a paired-t 95 % interval on the mean log(D/I). COMPROMISED if the interval excludes 1 and the point estimate is outside ±3 %; CLEAR if the whole interval is inside [0.97, 1.03]; otherwise INCONCLUSIVE, then 4 more pairs;
  - "all three pairs point the same way" has a 25 % false-alarm rate.
- **Integration, SHOULD_FIX.** Use Σ power × overlap. Add 2 s idle guard bands on both sides of every timed segment. Also sum the plist millijoule counters over the same overlap, and flag any disagreement > 0.1 J.
- **Census, BLOCKER.**
  - Run `ps` every 5 s for the whole cell and `pmset -g assertions` every 30 s.
  - Flag any process other than the workload and powermetrics that averages ≥ 5 % over a segment, OS processes included.
  - Its owner parks the magistrate job for U and S.
  - Record any foreign caffeinate.
- **Safety.**
  - Trap every exit path so each dummy label gets booted out.
  - Keep the labels outside the `com.joulewise.night*` patterns.
  - S is last, because `caffeinate -u` creates a UserIsActive assertion.

---

# Delta check of design v2 (same seat, main eec7acaa)

| v1 finding | Status |
|---|---|
| BLOCKER stats | cured in shape; α numbers inconsistent (2a) |
| BLOCKER census | half cured: no flag threshold, and the watchdog-overlap flag is degenerate (2c, 2d) |
| 1a, 1b, 1c, guard bands + dual integrals, B→MDE, 1f | cured |
| 1e promote Q4 | not adopted; the ruling is acceptable |

- **2a SHOULD_FIX.** Pocock spends 0.0294 per look, so DIFFERENT needs a 97.06 % interval and TOST 94.1 %. As written, the family-wise error exceeds 5 %.
- **2b SHOULD_FIX.** δ = min(3 %, 5 J / E) depends on an arbitrary request length. A 256-token 7B request is ≈200–300 J, so δ ≈ 1.7–2.5 %, and EQUIVALENT becomes essentially unreachable at n = 6. Use δ = 3 % on relative endpoints and report the absolute J/token interval.
- **2c SHOULD_FIX.** Every ≈4-min cell overlaps the 300 s tick. Park the magistrate job for U, or rely on the CPU rule.
- **2d SHOULD_FIX.** State the census rule: ≥ 5 % CPU averaged over a segment, OS processes included.
- **2e SHOULD_FIX.** July's path was `caffeinate -is /bin/zsh window-chain.zsh` from Terminal (`scripts/quiet_window_clock.sh:141`). SH should wrap the same way and launch detached. Record ancestry and QoS, and put the lead's session on the census allowlist.
- **2f NIT.** For 3 arms, the carry-over-balanced design is Williams: all 6 orders once per stage.
- **2g NIT.** The U–S–U sandwich yields an interval, not a verdict.
- **§7 rulings.** Right, including S being secondary. The trigger and the crossed sampler×workload design should be pre-registered now.
- **Verdict:** RUN AFTER LISTED FIXES (2a–2e).
