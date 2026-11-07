VERDICT: ADMIT_WITH_FIXES

Cold executing review (Fable 5.1, blind) of `git -C /Users/edr/code/jw-wt/r0-smc-cov diff e1a91226e..c0c460fd9`
(PR #692 head c0c460fd9, branch fix/2026-11-07-r0-smc-coverage-cell) against
/Users/edr/night-archive/r0-smc-cov/build2/DECISION.md D1-D6 plus Erratum 1.
Scratch: /Users/edr/night-archive/r0-smc-cov/cold2/fable/ (scripts `replay.py`, `collect_fakes.py`, `order_check.py`,
`receipt_variants.py`, `e2e.py`, `followups.py`, `settle_sim.py`, `settle_restricted.py`; outputs `*.out`, `rank-real.json`).
Every run used
`PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P`
and printed `module.__file__` = `/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/smc_enumeration.py` (and r0_host.py,
thermal.py, r0_runner.py, scripts/align_smc_enumerate.py from the same worktree). Worktree untouched; nothing pushed.

Why ADMIT_WITH_FIXES and not REFUSE: on the real capture and on production-shaped synthetic data the code selects what
DECISION.md and Erratum 1 say it should (Tf18 / TaLP; TaRT / TSXR / TVS0), the receipt passes the real capture and
refuses a 2.5 s hole, SMC runs first in all 42 orderings tried, and the adaptive idle cannot hang (cap holds). The
findings below are (1) a text-soundness hole that gives a wrong selection on a concrete, production-plausible input
(a lighter step than the 900 s matmul), which must be closed before R1 uses `rank` for selection; (2) a D3 settle
condition that is statistically unreachable on this Mac, so every R0 pays the full +900 s; (3) two receipt refusals
that fire on loop latency rather than on a sampling hole. None changes the next R0's picks; (1) changes R1's.

## Findings, ranked

### F1 (high; text D1/Erratum 1; fix before R1 selection). A derived channel wins the fast pick whenever the step leaves it under 125 degC

D1(c) removes TVH3 on this capture only because the 900 s matmul drove it to 137 degC. TVH3 is a linear function of
TCMb (the Erratum's own finding), so a lighter step leaves it below the ceiling, and nothing else in D1 touches it:
its one-second jump is 2.07 degC against a 64 degC rise (D1(b) needs > 32), and it never reads below 10 degC.

Command: `followups.py` (real capture; every degC key's excursion from its own last-60 s idle baseline scaled by f, all phases).
```
TVH3 = 1.721*TCMb + -38.2, R2 0.980; TVH3 max 137.0 at TCMb 103.9; TCMb max 104.2
TVH3 crosses 125 at TCMb = 94.8 degC
TVH3 max one-second change 2.07; TVH3 rise (load tail median - last-60 s idle median) = 64.1
scale 0.95: picks {'s_fast': 'Tf18', 's_slow': 'TaLP'}; TVH3 above_junction=True  max=132.5
scale 0.9:  picks {'s_fast': 'Tf18', 's_slow': 'TaLP'}; TVH3 above_junction=True  max=128.0
scale 0.85: picks {'s_fast': 'TVH3', 's_slow': 'TaLP'}; TVH3 class=die above_junction=False rise=54.5 tau=33.3 jump=1.76 max=123.6; Tf18 rise=38.8
scale 0.8:  picks {'s_fast': 'TVH3', 's_slow': 'TVS0'}; TVH3 class=die rise=51.3 max=119.1; Tf18 rise=36.5
scale 0.7:  picks {'s_fast': 'TVH3', 's_slow': 'TVS1'}; TVH3 class=die rise=44.9 max=110.1; Tf18 rise=32.0
```
A step 15 % lighter than the matmul selects the key the Erratum calls "a firmware-derived value, not a thermometer".
R1 re-selects on the actual planning-turn step (docs/align/smc_temperature.md: "R1 re-selects using the actual
planning-turn step"), which is lighter than a continuous 2048x2048 matmul; TCMb must exceed 94.8 degC for the ceiling
to catch TVH3. The same production-shaped synthetic run (`e2e.py`, a TVH3-like channel 1.72*TCMb-38 peaking at 120)
went script -> payload -> receipt and the receipt PASSED with `{'s_fast': 'TVH3', 's_slow': 'TaLP'}`.

Also note the slow pick moves with it (TaLP -> TVS0 at 0.8) because `select_keys` ranks by band hold, which scales with
rise; that part is by design (D5 is provisional), but it shows the slow pick is rise-sensitive.

What the text needs: D1 has no test for a derived or aliased channel as such; the 125 degC ceiling is a coincidence
of this load's magnitude. DECISION.md already records the mechanism ("Aliased keys must never count as independent
thermometers"; TVH3 = 1.72 x TCMb - 38, R^2 0.98). Make that measurement the exclusion (a key whose readings are a
linear function of another key to within the noise floor is an alias/derived channel: flagged, excluded from picks),
or at minimum pin TVH3 (and the exact duplicates TCMb/TVD0, Tf24/Tf2D/Tf2E) on Mac15,9 as a recorded exclusion before
R1 selection. I am not setting the bar; the noise floor already exists in `rank`. The code change is small once the
rule is written.

### F2 (medium; text D3, code `collect`). The settle condition is unreachable on this Mac: every R0 idles the full 1,200 s

D3 says idle continues "until every key that passes D1(a) and the stale rule" has |slope| <= 0.2 degC/min for 10
consecutive evaluations. The code does exactly that. On Mac15,9 that set includes the flicker channels (TCMz, Tp06,
Tp0E, Tp0W, Tp0c, Tp0i, Tp0o, Tp1K, Tp1S, Tp3P, Tp3X: last-60 s residual SD 3-8 degC) which D1(b) later removes, and
~30 keys with residual SD 0.2-0.8 degC. The 0.2 degC/min bar is 3 sigma for ONE key at the D5 noise limit
(0.447 x 0.15 x 3 = 0.2); demanded of 235 keys at once, 10 evaluations running, it cannot be met.

Command: `collect_fakes.py` (iv) - `collect` with FakeClocks, a flat Tf18 plus the real TCMz idle series (linearly
detrended, SD 7.34 degC) as the only other key:
```
(iv) flat Tf18 + detrended real TCMz flicker: actual_seconds=1200.000 settled=False consecutive=1 slopes={'Tf18': -0.004, 'TCMz': -0.089}
   rank TCMz reason: D1(b): one-second change exceeds half the step rise; recorded only | below_ambient False noise 7.16
```
Command: `settle_restricted.py` - the settle test on white noise at each real key's measured last-60 s residual SD
(a settled-Mac proxy; white noise is optimistic for slope variance):
```
all D1(a)+stale keys: 235 keys; settled_at=None; evaluations with 0 failing keys: 0 of 1140; longest all-pass run 0; failing-key count (top): [(21, 194), (20, 169), (22, 163), ...]
residual SD <= 1/3 (D4 bound): 207 keys; settled_at=None; evaluations with 0 failing keys: 49 of 1140; longest all-pass run 4
residual SD <= 0.15 (D5 bound): 140 keys; settled_at=69; evaluations with 0 failing keys: 1140 of 1140
```
Real-data check (`settle_sim.py`, `followups.py`): over the real 300 s idle TCMz failed 225 of 240 evaluations, Tp3X
231, Tp0W 232, TVFh 240 (it was also still cooling: every physical key failed all 240, as expected for an unsettled
capture).

Consequence: no hang (cap holds; `(ii)` below), the per-key `baseline_unsettled` flags still work, and at 1,200 s the
physical keys are settled (median 930 s, max 1,038 s). But D3's "Cost: 0 to +900 s" is always +900 s, and the phase
record's `settled` will always be False, which makes it useless as a diagnostic. Fix shape for the lead (bar is theirs):
restrict the settle set to keys the roles could ever pick, i.e. keys whose trailing-60 s residual SD is within the
noise bar the 0.2 degC/min test was derived from (0.15 degC, D5), or settle on the current fast/slow candidates only.
With the 0.15 restriction the proxy settles at the first possible evaluation; with 1/3 it still does not.

Executed cases that behave correctly (`collect_fakes.py`):
```
(i) cooling then flat at 330: actual_seconds=383.000 settled=True consecutive=10
(i-b) cooling -0.5 C/min until 700: actual_seconds=744.000 settled=True
(i-c) exponential tau 400 s, 5 C: actual_seconds=569.000 settled=True   (expected ~569 from 400*ln(0.75/0.2)+30+10)
(ii) never settles (-0.5 C/min throughout), cap 1200: actual_seconds=1200.000 settled=False; phases idle 0-1200, load 1200-2100, recovery 2100-2700; rank baseline_unsettled True slope -0.5; max quiet gap 5.0 s
(iii) key turns noisy (SD 0.5 C) at t=400: actual_seconds=300.000 settled=True   (already settled; correct)
(iii-b) key noisy (SD 0.5 C) from the start: actual_seconds=312.000 settled=True
(v) erroring key cooling -1 C/min (all reads fail): 300 s settled   (excluded from the set; rank fails it on coverage)
(vi) below-ambient cooling key: 300 s settled; (vii) all keys constant: 300 s settled, slopes={}
(ix) heavy clock read cost (every sample > 1 s): cap 1200.75, consecutive resets each evaluation; no hang
```
Can it end idle early on a key it should wait for? Only via (viii): a 1 degC-quantum staircase cooling at 0.3 degC/min
passes once its 60 s window sits on one step (slope 0.0). No degC key in this inventory has that quantum (366 flt,
9 ioft), so not a live case. Budget arithmetic: `step_budget` -> capture 2,700 s, timeout 3,300 s (1,200+900+600+600),
runner per-check deadline 7,200 s; the tracked config validates (`validate_config` -> idle_max_seconds 1200).

### F3 (medium; code `rank` max_interval_ns / receipt D6). The 2 s interval bar spans the idle->load handshake and refuses a fully covered capture

`rank` sorts valid-read midpoints from all three phases together and bounds every consecutive interval, so the gap
between the last idle sample and the first load sample (quiet census + `GpuLoad.start()`, whose readiness handshake
the code itself allows 30 s) counts against U1(c). On 11-07 that gap was 0.33 s and the capture's max interval 1.271 s
is exactly that transition. The receipt refuses once the handshake runs ~0.7 s longer than it did on 11-07.

Command: `receipt_variants.py` (real capture; load and recovery phases and their samples shifted later by X s; every
phase still 100 % covered, 0 errors):
```
[real]                status=pass  Tf18/TaLP max_interval 1.271 s; coverage idle 1.0 load 1.0 recovery 1.0
[load-start-late-0.5s]  status=pass          max_interval 1.771 s
[load-start-late-0.75s] status=inconclusive  max_interval 2.021 s  reason=... <=2 s intervals
[load-start-late-1.0s]  status=inconclusive  max_interval 2.271 s
```
A phase transition is not a hole in a thermometer stream: the baseline window ends at the idle's actual end, the step
clock starts after the handshake, and no fit crosses the boundary. Fix: bound intervals within each phase (edges per
phase, the way `Coverage.report` treats one span), or exclude the two transitions. `import mlx.core` took 0.05 s warm
here; a cold start is what this margin would meet.

### F4 (low-medium; code r0_host receipt). Phase-duration "+/-1 s" refuses the whole capture on loop latency, and its derivation names the wrong quantity

```
[load-overshoot-1.3s]       status=inconclusive reason=SMC r0.json selection unavailable: SMC observed phase durations do not match configured adaptive profile
[idle-1201.5s-no-samples]   status=inconclusive (same)
```
The new `collect` records the actual end, which is the planned end plus whatever the loop does after the last sample:
up to 0.25 s sleep granularity plus one quiet census (70-330 ms measured; each of its three probes has a 5 s subprocess
timeout). The comment derives the tolerance as "one sampling period is the capture's maximum read bracket", but the
overshoot is loop latency after the last sample, not a read bracket; a slow census at a phase end would void a 45-min
capture on a bookkeeping check. Under the project's own rule this is a flag, not a refusal (the durations are already
authenticated by sample stamps). Make it a recorded flag, or size the tolerance to the loop's latency budget.

### F5 (low; text D5 vs code). The "design-literal" alternative is "longest tau among keys with band hold <= 300 s", not "longest tau in the D5 role"

D5's role text is "60 s < tau <= 300 s, noise <= 0.15" with the <= 300 s band hold only in the pick; the code makes
`t_band_s <= 300` an eligibility condition for both roles, so TVS0 (tau 148.3 s, rise 9.21, noise 0.009, band hold
329 s) is record-only and the design-literal alternative prints TaRT (tau 129 s). The Erratum expected TaRT, so the
code matches the lead's intent; the D5 text should say the band-hold cap is part of the role. No pick changes.

### F6 (low; code `rank`). D1(b) is stamped on non-responders

`jump > rise/2` is trivially true when rise <= ~0, so four keys with no step response (TVA0 rise -0.97, TH0a 0.38,
TH0b 0.56, Ts1P 0.19; jumps 0.01-0.34) are reported as "D1(b): one-second change exceeds half the step rise". The
"D1(b) removes 19" count therefore overstates the placeholder catch by 4. Apply D1(b) only when rise > 0 (or label
these "no resolvable rise").

### F7 (low; number rule). Numbers without a derivation beside them, and one vacuous bar

- `CLAMP_DISTINCT = 10`: the comment says it "excludes coarse-quantum channels" but nothing derives 10.
- Receipt `+1 s` duration tolerance: derivation is the wrong quantity (F4).
- Receipt `sum(phase_seconds) >= 600`: always >= 1,800 under the profile refusals (load >= 900), so it never
  decides anything; section 2.6's ten minutes is a per-key readable interval, which the coverage bars now carry.
- Observation, not a new number: one skipped tick passes with 89 ms to spare (`[one-skipped-tick] status=pass
  max_interval 1.911 s, load coverage 0.9989`); with adverse jitter (prior sample early, next sample 150 ms late) a
  single skipped tick reaches 2.0 s and refuses. The 99 % cell bar tolerates nine skipped ticks per 900 s; the 2 s bar
  tolerates about one. That is U1(c)'s number, so it is the lead's call whether a lone skipped tick should refuse.
- Every other threshold in the diff carries its derivation: 10 degC (Apple minimum ambient), 125 degC (junction
  rating, with TCMb 85.5 / TCMz 112 / TVH3 137 beside it), half-rise (tau < 1/ln 2), 3.0 degC (3 bands), 1/3 and 0.15
  (3 SD in band; SD(slope) = 0.447 noise), 300 s (G1/H cap), 1,200 s (measured settle median 930 / max 1,038),
  NS // 2 (one reading per cell), 0.2 degC/min, 60 s, 10 (G0's bar, inherited), 0.4 clamp fraction
  (q/(sigma sqrt(2 pi)) <= 0.40), 99 % / 1 % / 2 s (D6, U1(c)), test deltas in test_smc_classifier_v4 (each with its
  noise/slope arithmetic; the `delta=10` on tau 100 in test_smc_selection is loose but explained).

## Executed checks that passed

1. Test modules, each in its own process (all OK): test_smc_classifier_v4 (13), test_smc_quiet (21), test_smc_selection
   (9), test_thermal_coverage (5), test_r0_host (45), test_r0_step (12), test_r0_scheduling (12), test_r0_documentation
   (4), test_thermal_gate (31), test_thermal_desk (21), test_r0_checks (30).
2. Real capture replay (`replay.py`, /Users/edr/night-align/r0-v4-20261107T0810Z/smc/r0.json + samples.jsonl: 403 keys,
   1,800 samples, phases idle 300.000 / load 900.000 / recovery 600.000 s, 0 read errors):
   - picks `{'s_fast': 'Tf18', 's_slow': 'TaLP'}`, status pass, both stages (r0 and r1) identical;
   - alternatives design_literal TaRT, opus TSXR (t_late 123.7 s), sol TVS0 with `s_fast_tracking` TCMb; as Erratum 1 expects;
   - Tf18: rise 45.68, rise60 44.03, tau 24.7 s, noise 0.062, band hold 94.5 s, slope -0.64 degC/min (unsettled flag True);
     TaLP: rise 20.54, tau 86.2 s, noise 0.020, band hold 260.7 s; TCMb printed as die (rise 36.15, tau 28.9);
   - counts: 118 die + 2 die-but-clamped (TV1m, TVm0: 63 % of idle on one value, noise 0.0; excluded from picks),
     18 heatsink, 265 record-only; reasons: 77 not resolving/releasable, 75 D1(a), 65 stale, 28 non-temperature,
     19 D1(b), 1 D1(c), 257 of 403 `baseline_unsettled` (the capture was still cooling);
   - D1(a) removes 75: all 32 Tg* (idle/recovery 0.0 / -0.5 / -2.75 / -8.75 / -9.0; 95 % placeholder), the constant
     Ta0x / Tf?0 / Tf?2 / Tf?C / TH1a / TH1b / Tz1x / TVMD channels (0, 1.0, -2.7, -10.5 to -12), and the virtual
     TV2S/TV3S/TVH2/TVM2/TVM3/TVMO/TVSO/TVHO (negative or 1-9 degC). None has an idle median above 10 degC;
   - D1(c) removes 1: TVH3 (idle 48.9, load 111.6 median, max 137);
   - D1(b) removes 19: TCMz (jump 26.9 vs rise 40.8), ten Tp* flickers (jumps 17-30 vs rises 31-40), TV0h/TV1h/TVh0/
     TVFh (clamp jumpers, jumps 19.9-22.7), and the four non-responders of F6. Verified the flicker character:
     TCMz's largest jump is at recovery 1,480 s (45.9 -> 72.8 -> 46.9), Tp06's at recovery 1,780 s (40.5 -> 57.9 ->
     40.5), only 20-25 % of their idle/recovery readings lie within 1 degC of their median; TVh0 jumps 82.8 -> 60.0 at
     load 602 s (a clamp). No key with a real positive response is removed: every die/heatsink key has jump <= 7.7
     against rises >= 3.75, and tau is consistent with the jump (Tf18: 6.12 of 45.7 at tau 24.7).
   - No placeholder, derived or virtual key reaches a pick: picks are Tf18/TaLP; the clamped TV1m/TVm0 are excluded;
     aliases TCMb=TVD0 and Tf24/2D/2E are present as die rows but neither is the pick (R1 lane item in DECISION.md).
3. Receipt on the real capture (`r0_host.smc_enumeration`, subprocess patched to exit 0): status pass, reason "WP14(a)
   model-free classifier and readability bars met; picks PROVISIONAL"; `selected_key_readability` for Tf18 and TaLP:
   coverage 1.0/1.0/1.0, errors 0/0/0, phase_seconds 300/900/600, max_interval 1,271,162,167 ns, baseline_unsettled
   true with slopes -0.641 / -0.679. Genuine 2.5 s hole (drop load t=700, shift t=701 by +0.5 s): status inconclusive,
   max_interval 2.411 s, load coverage 0.9978 (test_r0_host's hole case also exercised: 2,500,000,000 ns).
4. R0 order (`order_check.py`, fake backend/SMC/disk/host, real `r0_runner.execute`): 42 orderings including the full
   list, its reverse, all 24 permutations of [smc, disk, load, ladder] and 12 random subsets: event order was always
   SMC first, then HOST/DISK, then MODEL-LOAD; `checks[0] == 'smc'` every time; 0 violations; with smc unselected no
   SMC event.
5. End to end (`e2e.py`): `scripts/align_smc_enumerate.main` with a 403-key fake reader (measured-shape jitter 0-150 ms
   late / 50-400 ms reads, 32 Tg placeholders, a TCMz-like flicker, a TVH3-like derived channel, 28 non-degC keys,
   physical keys cooling tau 250 s), fake quiet census (0.1 s) and load (0.3 s handshake) -> r0.json / samples.jsonl /
   summary.md -> receipt pass. The idle ran to the 1,200 s cap (settled False; F2). summary.md rows print the same
   per-phase coverage, read errors, max interval (1.4811 s), slope and unsettled flag the receipt reads, plus actual
   phase lengths ("idle: 1200.000 s; settled: False") and the capture-wide fraction labelled diagnostic only.
   (The TVH3 pick in this run is F1.)
6. `profile_config` refuses idle_max_seconds < idle_seconds, non-int caps and unknown fields; budget 2,700 / 3,300 s;
   `--idle-max-seconds` reaches the script argv (test_r0_host) and `collect`.
7. Coverage at NS // 2: duplicates and the half-period tie count once; a read over one period fills no tick; one
   skipped tick gives 899/900 = 0.9989 (passes), 18 of 900 gives 0.98 (refuses), as the tests assert.
