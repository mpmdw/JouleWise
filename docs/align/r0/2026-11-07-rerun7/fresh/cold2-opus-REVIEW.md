VERDICT: ADMIT_WITH_FIXES

# Cold executing review (Opus 5.5, blind): PR #692 head c0c460fd9 against DECISION.md D1-D6 + Erratum 1

Scope: `git -C /Users/edr/code/jw-wt/r0-smc-cov diff e1a91226e..c0c460fd9` (16 files). Worktree clean at
c0c460fd9. All runs used the pilot2 venv python with `-B -P`, `PYTHONPATH=<worktree>`, TMPDIR = my scratch;
`__file__` printed as `/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/...` on every run. Scripts are in
`/Users/edr/night-archive/r0-smc-cov/cold2/opus/scripts/`.

No input I built gives a wrong pick, a hang, or a crash. On the real capture the code does what D1-D6 and
Erratum 1 say. Three findings come from the decision text itself, and the code makes them visible. The
first wastes up to 900 s of quiet machine time on every R0, the second turns pass/fail into a coin flip on
one missed read, and the third lets an SMC inconclusive throw away the whole R0. None of the three changes
a printed number, so they are fixes rather than a refusal.

## Findings, by severity

### F1 (medium-high, a fault in the D3 text): the settle test can never pass on this Mac, so every R0 idle runs to the 1,200 s cap

How settling works: collect waits until every degC key that passes D1(a) and the stale rule on idle data
has |60 s OLS slope| <= 0.2 degC/min for 10 evaluations in a row. That is literally what D3 says. On
Mac15,9 this set has 235 keys. It includes 15 flickering keys (TCMz plus Tp1K, Tp0c, Tp0W, Tp1S, Tp0i,
Tp3X, Tp0o, Tp3P, Tp06, Tp0E, Tp0M, Tp18, Tp1G and Tp0T). Their idle residual SD is 3-7.7 degC, D1(b)
removes them later, and none of them can ever be a pick. With noise that large, the 60 s slope swings by
2-4 degC/min from one window to the next, even when the underlying temperature is flat.

- Command: `scripts/settle_noise.py`. It takes the real recovery data, subtracts a centred 121-sample
  running mean, and so keeps only each key's own high-frequency noise. It then runs collect's exact test.
  ```
  A: D3 as built | evaluations 300 all-key passes 0 longest run 0
     keys failing >50%: [('Tp0W', 295), ('Tp1S', 293), ('Tp1K', 292), ... ('TCMz', 273), ...]
  ```
- Same test with a linear detrend instead (`settle_joint.py`): 0 passes out of 240.
- Synthetic run through the real chain (`e2e.py`), same keys, the only difference being one Tp-like
  flicker key at SD 5:
  ```
  noflicker  phases [('idle', 470.0, True), ...]
  flicker    phases [('idle', 1200.0, False), ...]   picks unchanged: Tf18 / TaLP
  ```
- Fakes (`d3_fakes.py`), flat key plus one key at SD 6: `idle 1200.0 settled False slopes {'TDIE': -0.005, 'Tp1K': 3.911}`.

Consequences:
- D3 behaves as a fixed 1,200 s idle. The capture records `settled: False` every time.
- D3's stated cost ("0 to +900 s") is really +900 s on every R0. The waste is largest exactly when SMC now
  runs first, on an already cool machine.
- Selection is not harmed: rank flags each key by its own slope, and a longer idle only settles baselines
  further.

Fix for the lead to rule on (it changes the text of D3): wait only on keys whose trailing-window residual
SD is <= 0.15 degC. This is D5's own derivation: for 60 one-Hz samples, SD(slope) = 0.447 x noise, so
noise <= 0.15 puts 3 sigma of the slope at <= 0.2 degC/min. A key noisier than that cannot pass the slope
test even while it is truly flat. Its unsettled status is still reported per key by rank.
- Replay of the same noise data, `settle_noise_c.py`: `C: skip keys with window SD>0.15 | all-key passes 78 longest run 30`.
- Using D4's 1/3 degC bar instead still fails (variant B: 0 passes; Tp0R/S, Tp1E/F, Te0M/T, Tp0K/L fail
  more than half the evaluations). The real noise is autocorrelated, so the white-noise 0.447 factor
  understates the slope spread above about 0.15.

### F2 (medium, a fault in the D6 text that the code exposes): the <= 2 s interval bar passes or fails one missed read by jitter, and the receipt discards the step instead of taking the next key

D6 admits up to 1% read errors and 99% cell coverage, which allows up to 8 missed reads in a 900 s load.
But one missed read leaves a gap between valid midpoints of 1.85-2.38 s on the real stamps (normal
intervals run 0.85-1.27 s). The 2 s bar sits in the middle of that range.

- Command: real journal midpoints, gap across one dropped reading:
  `single-miss interval: n 1798 >2.0 s: 1025 0.57 max 2.379 min 1.850`
- Command `scripts/holes.py`. It edits the real journal, recomputes the SHA, and runs the real
  `r0_host.smc_enumeration`:
  ```
  A_hole_2p5s       | inconclusive | ... | picks Tf18/TaLP | max_interval {'Tf18': 2.5, 'TaLP': 2.5}
  B_one_miss_wide   | inconclusive | ... | picks Tf18/TaLP | max_interval {'Tf18': 2.149, ...} | err Tf18 0.0011
  C_one_miss_narrow | pass         | ... | picks Tf18/TaLP | max_interval {'Tf18': 1.85, ...}  | err Tf18 0.0011
  ```
- B and C are the same defect, one missed Tf18 read, at two positions. One passes and the other refuses.

The interval bar is checked only in the receipt. It is not part of rank's eligibility test, so the pick
stays Tf18 and the whole roughly 45-minute step is lost. Tf2B (rise 45.63 against Tf18's 45.68, tau 24.4,
noise 0.07) would have passed.

Brief item 5 is satisfied: the genuine 2.5 s hole refuses (A), and the real capture passes.

Fix for the lead to rule on, either or both:
- (a) State U1(c) in grid cells, "no two consecutive empty 1 s cells", using the Coverage grid that
  already exists. If it stays in seconds, derive it as 2 periods plus the measured lateness (about 0.4 s).
- (b) Make the readability bar a condition of rank eligibility, so the next key is picked instead of the
  step refusing.

### F3 (medium): with SMC first and fail-fast, an SMC inconclusive now stops the whole R0

Because `inconclusive` is not in `ACCEPTED_OUTCOMES["smc"]`, any non-pass SMC result raises `_StopChecks`
before host, disk, host-identity and every model check. Before this change SMC ran after memory, so
load/template/generated/memory had already finished.

- Command `scripts/order.py`, with fake SMC returning inconclusive and the full CHECKS list:
  `events ['smc'] report checks ['smc'] stopped_after {'check': 'smc', 'model': None, 'outcome': 'inconclusive'}`
- The runbook documents this ("inconclusive checks do" stop). D3 does not decide it.

Under the "physics refuses, everything else is a flag" doctrine, an inconclusive sensor pick is not a
hazard to the model checks. Suggest accepting `inconclusive` for smc as a flag, or running R0 with
`--keep-going`. This is the lead's call.

Brief item 4 is verified. Over 107 orderings (canonical, reversed, 60 random permutations, every 1-, 2- and
3-subset containing smc, all 8-subsets), SMC ran first and exactly once, before `disk` and before any
`backend-init`: `orderings checked 107 violations 0`.

### F4 (low): the "design_literal" diagnostic is computed under the band-hold cap, which D5 places only on the default pick

The code requires tau*ln(rise) <= 300 for both roles (`releasable`). D5 states that cap only for the
default pick. So `design_literal` (longest tau) is chosen from an already capped bank and returns TaRT
(tau 129.0). Without the cap, the D5 role (60 < tau <= 300, noise <= 0.15, resolving) also admits TVS0
(148.3), TVS2 (147.7), TVS1 (145.1) and TVFm (130.5); their band holds run 329-406 s.

- Command: filter of the replay rows → `TVFm 130.5 406.0 / TVS2 147.7 364.7 / TVS1 145.1 349.1 / TVS0 148.3 329.3`.

Erratum 1 names TaRT as expected, so the lead may already accept this. But the diagnostic exists so the
slow rule can be chosen on the next settled capture, and its label should say "longest tau with band hold
<= 300 s". The default and fast picks are unaffected.

### F5 (low, number rule plus doctrine): r0_host refuses on a phase lasting more than ±1 s off its configured length, with an incomplete derivation

The comment says one period is "the capture's maximum read bracket". At a phase end, though, the overrun
is read time plus quiet-check time minus 1 s.
- Measured on the real journal: max read 0.392 s; max finished-to-next-start 1.067 s (a quiet check). The
  worst overrun is therefore about 0.46 s, which fits today.
- A slow quiet probe of 1.6 s or more at the last tick would raise "observed phase durations do not match"
  and void the step's selection.
- This is a non-physical record check. Suggest a recorded flag, or a bound derived from the measured
  read and quiet-check maxima.

### F6 (low): settled is reported True when nothing is being waited on

If the settle set is empty, `all()` over no slopes is True and idle ends at 300 s marked settled. That
happens when every key is below 10 degC, stale, or every read takes more than 1 s.
- Fakes: `5b 1.2 s reads: idle 300.0 settled True`.
- Selection is harmless (rank refuses on coverage), but the record is misleading. Suggest recording
  `settled: null` or `settle_keys: 0`.

### F7 (low, for the R1 lane as DECISION says): D1 has no rule for virtual or aliased keys

Virtual keys are still die candidates: TVV0 (rise 43.08, 14th by rise) and TVD0 (identical to TCMb). TVS0
is the Sol alternative. The picks on this capture (Tf18, TaLP) are not virtual. TVV0 trails Tf18 by
2.6 degC, so a later capture could promote it. DECISION already sends aliasing to R1.

## Brief item 2: real-capture replay (`scripts/replay.py`, `scripts/removals.py`)

`r0_host.smc_enumeration` on `/Users/edr/night-align/r0-v4-20261107T0810Z/smc` (subprocess replaced; SHA
verified by the code):
```
status pass | selection {'s_fast': 'Tf18', 's_slow': 'TaLP'} readable True
Tf18/TaLP: phase_coverage 1.0/1.0/1.0, read errors 0, phase_seconds 300/900/600, max_interval 1.271 s,
           baseline_unsettled True (slopes -0.641 / -0.679 degC/min)
alternatives: design_literal TaRT; opus TSXR (t_late 123.7 s); sol TVS0 (s_fast_tracking TCMb)
```
This matches DECISION/Erratum 1 (Tf18 / TaLP; TaRT / TSXR / TVS0).

Counts by reason over 403 keys:

| Count | Reason |
|---:|---|
| 118 | die (fast-role candidates) |
| 2 | die but clamped: TV1m, TVm0, excluded from picks |
| 18 | heatsink (slow-role candidates) |
| 77 | not resolving or releasable |
| 75 | D1(a) |
| 65 | stale |
| 28 | not degC |
| 19 | D1(b) |
| 1 | D1(c) |

Flags: 35 clamped (32 Tg, TV1m, TVm0, TVh0); 136 of 136 eligible keys are baseline_unsettled, which is
expected on this unsettled idle.

What each D1 rule removes, and whether it should:
- **D1(a), 75 keys:** the 32 Tg* keys, which are below 10 on 870-871 of 900 idle/recovery reads with
  placeholders 0, -0.5, -2.75, -8.75 and -9.0. The other 43 read below 10 on 900 of 900: TH1a/b, Ta08/09,
  Ta0G/H/K/L/O/P, Tf00/02/0C/10/11/12/1C/20/22/30/32/3C/40/42/4C, Tz11-18/1j, and the negative or
  near-zero TV keys TV2S, TV3S, TVH2, TVHO, TVM2, TVM3, TVMD, TVMO, TVSO. No key with any reading of
  10 degC or more is removed except the Tg placeholders. Correct.
- **D1(b), 19 keys:**
  - TCMz and 10 Tp*: jumps of 17-30 degC against rises of 31-41, idle SD 3-7.7.
  - TV0h, TV1h, TVFh: one 19.9 degC firmware step at t = 360.6 s, 60 s into load, from 59.4 to 79.3 degC.
    This is not the load onset.
  - TVh0: clamp jumper.
  - TH0a, TH0b, Ts1P: rises of 0.19-0.56 degC, which would fail the 3 degC floor anyway.
  - TVA0: negative rise.
  No real positive responder is removed. Correct.
- **D1(c), 1 key:** TVH3, max 137.01 degC. Correct.
- **Pick check:** neither pick is a placeholder, derived or virtual key. The hottest surviving fast
  candidates (Tf18 at 95.2, TCDX at 95.8) are below 125.

## Brief item 3: D3 with fakes (`scripts/d3_fakes.py`)

| Case | Result |
|---|---|
| Still cooling, settles (8 degC excess, tau 400 s) | idle 745 s, settled, 10 in a row. Analytic: the trailing-window slope reaches 0.2 at about 747 s |
| Never settles (-0.5 degC/min) | stops at the cap: idle 1200.0, settled False; rank flags baseline_unsettled with slope -0.477 |
| Flat key plus SD-6 flicker key | 1200 s (F1) |
| Key becomes noisy at 310 s | ends at 300 s, correctly, because the earlier data was settled |
| Key becomes noisy at 295 s | runs to the cap |
| Reads taking 0.9 s / 1.2 s | no hang; phases 300 / 900 / 600 (1.2 s: F6) |
| 375 keys | 7.5 CPU-seconds for the whole collect; each evaluation well under 1 s |

- **Early stop:** no case ended idle early on a key it should have waited for. Excluded keys are only
  those below 10 degC or stale, and both are unpickable under rank.
- **Budget:** maximum 1,200 + 900 + 600 = 2,700 s; timeout 3,300 s. Overhead on the real run is
  1,845.6 s total minus 1,800.7 s of capture = 44.9 s, and the new rank costs 2.8 s on 1,800 rows, so
  there is ample margin. The receipt accepts an idle of 300-1,201 s.

## Brief item 6: end to end (`scripts/e2e.py`)

Chain: the real `scripts/align_smc_enumerate.main`, with fake reader, clock and load, writes the journal,
r0.json and summary.md; the real `r0_host.smc_enumeration` then reads them.
- Keys: a fast key, a slow key, a Tg-like placeholder, TVH3-like derived values reaching 141, a constant
  9.969 key, an rpm key, plus an optional flicker key.
- Both scenarios pass with picks Tf18 / TaLP. The script's ranking and the receipt's ranking are identical
  (True). D1(a), (b) and (c) each remove their planted key.
- summary.md's row for each pick prints exactly the receipt's coverage, errors and max interval
  (e.g. `1.1318` against `1131769535 ns`). Phase durations print per phase.

## Brief item 1: tests

Each module run in its own process. All OK:

| Module | Tests |
|---|---:|
| test_r0_documentation | 4 |
| test_r0_host | 45 |
| test_r0_scheduling | 12 |
| test_r0_step | 12 |
| test_smc_classifier_v4 | 13 |
| test_smc_quiet | 21 |
| test_smc_selection | 9 |
| test_thermal_coverage | 5 |
| test_thermal_gate | 31 |
| test_thermal_desk | 21 |
| test_r0_checks | 30 |

Gap: no test covers a single missed reading against the 2 s bar (F2), or a noisy key in the settle set (F1).

## Brief item 7: number rule (a separate dimension)

**Derived:**
- 10 degC (Apple's minimum operating ambient)
- 125 degC (junction absolute maximum)
- 0.2 / 10 / 60 / 1,200 (D3)
- 3.0, 1/3 and 0.15 (D4/D5)
- NS // 2 (one cell)
- CLAMP_FRACTION 0.4: 1/sqrt(2 pi) for sigma >= q
- the Opus 0.149: 3 x 0.447 x sigma
- test tolerances: <=400 s, delta .01, the 3 s / 6 s tau windows, all with derivations beside them

**Without adequate derivation:**
1. The D6 <= 2 s bar ignores the measured lateness of up to 0.27 s per tick, and so splits single misses
   57/43 (F2).
2. The r0_host ±1 s phase tolerance omits the quiet-check term (F5).
3. `CLAMP_DISTINCT = 10`: "excludes coarse-quantum channels", with no derivation of 10.
4. Diagnostic-only Opus alternative windows, 240 s idle, 300 s recovery and 120 s slope: cited to
   "Opus V4/V6" without the derivation in place.
5. The `journal_bytes_per_slot_estimate` of 16,384 B, re-asserted in new test comments, against the
   measured 95,467,641 B / 1,800 slots = 53 KB per slot. This predates the PR and is a planning figure,
   not a gate, but it is 3.2x low. The 2,700 s maximum journal is about 143 MB.
