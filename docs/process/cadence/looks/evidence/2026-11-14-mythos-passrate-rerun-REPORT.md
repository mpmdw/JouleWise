# Seat: Mythos 5.2, pass-rate re-run

Sat Nov 14 22:19:48 PST 2026 (from `date`).

**A correct model passes the 2 % line 0.42 of the time under RL-166b, which is inside 0.25 to 0.60, so nothing goes to the research lead on that test.** The new δ column barely moves the pass rate. The no-heat figure is about 1 in 10.5, not 1 in 12.

Everything is synthetic; no measurement was opened. "±" is one standard error.

## Pass rate at the 2 % line, default world

40,000 campaigns (two seeds of 20,000), layout real4.

| Fit | Yes | Each seed |
|---|---|---|
| Correct model, RL-166b | 0.421 ± 0.0025 | 0.4225, 0.4189 |
| Correct model, RL-166 as written, same campaigns | 0.414 ± 0.0025 | 0.4157, 0.4118 |
| Change from the new column, paired | +0.0070 ± 0.0006 | |
| No heat term | 0.0946 ± 0.0015 | 0.0949, 0.0943 |

- **The old code path is reproduced:** the first 300 campaigns of each world give the old table exactly (0.42 and 0.08 in the default world).
- **The no-heat change is Monte Carlo error, not the column:** the old 0.08 was 23 of 300 (± 0.015), and the base fit has no δ column.
- **No B-2 to B-6 rule bit in the default world:** no inactive reading, no fold dropped δ, and the main onset fit was estimable in all 40,000.

Other worlds, 20,000 campaigns each (± 0.0035 or less):

| World | RL-166b | RL-166 as written | No heat |
|---|---|---|---|
| Day sd 0 | 0.693 | 0.688 | 0.205 |
| Day sd 1.5 points | 0.187 | 0.183 | 0.034 |
| Day sd 3 points | 0.041 | 0.041 | 0.007 |
| Day sd 5 points | 0.010 | 0.010 | 0.002 |
| Leg sd 1 point | 0.622 | 0.613 | 0.149 |
| Leg sd 4 points | 0.239 | 0.235 | 0.054 |
| Onset scatter 30 s | 0.313 | 0.291 | 0.070 |
| Onsets about 150 s later | 0.280 | 0.229 | 0.000 |
| About 14 % of onsets censored | 0.159 | 0.104 | 0.000 |
| About 30 % censored | 0.042 | 0.022 | 0.000 |
| About 45 % censored | 0.001 | 0.002 | 0.000 |

The manifest's "0.03 to 0.66" becomes 0.04 to 0.69 over the same five worlds.

## Attenuation of δ

4,000 campaigns per world, both columns on the same campaigns.

- **Default world:** the exported offset carries 0.880 ± 0.001 of the true heat effect, against 0.788 ± 0.001 as written. One campaign's ratio spreads by 0.04 around that (5th to 95th percentile 0.81 to 0.95).
- **Over twelve worlds:** 0.84 (onset scatter 30 s, was 0.65) to 0.96 (no start effect, no drift). RL-166b's "0.85 to 0.95" is slightly narrow at both ends.
- **Planted linear truth:** δ̂ over truth is 0.996 ± 0.0002, against 0.879 ± 0.0004; at 30 s scatter it is 0.992 against 0.740.

## The estimability rule at the minimum

320,000 onset-only campaigns, with onsets pushed late so that few legs leave the state.

- **At the old minimum** (12 to 15 uncensored on 3 days; 16,671 campaigns) the new rule says `estimable` in none. Only 2.6 % ± 0.1 % of them have a maximum at all.
- **At the new minimum** (second cell at exactly 4; 24,017 campaigns, about 38 of 60 uncensored) the fit passed B-5 in every one, so the failure rate is under 0.00012 at 95 %.
- **Fit quality there:** the reported error is 18.8 s against a true 19.8 s, and 3.6 % of onsets fall before the count-only cut against a nominal 2.3 %.
- **Above the minimum:** of all 98,757 campaigns that met counts and cells, none failed B-5.
- **B-5 alone is not enough:** it passed 1 of 107,279 single-cell campaigns, a drifting fit that happened to stop at the 100-step cap. The cell clause caught it.

## For the research lead

- **A fold that drops δ under B-4 always gave `no`:** 0 `yes` in 4,230 such campaigns. At the new minimum only 0.48 ± 0.003 of campaigns keep an onset model in all four folds.
- **Late onsets cut a correct model's pass rate well before the 0.30 censored-share tripwire:** 0.16 at 14 % censored.
- **The no-heat "1 in 10" holds only when most blocks are hot.** With late onsets it is zero.

## Basis

- **Implementation:** B-1 to B-6 are mine, written from RL-166b §3. I did not see the analyst's or the twin's code.
- **One reading I had to make:** when the main onset fit is not estimable, every fold drops δ. RL-167 was not given to me. It never arises in the default world.
- **"Correct model"** means what it meant in the first report: the fit form on the default physical world.
- **Checks:** the new column matches a 2,000,000-draw simulation, and with σ̂ set to zero the new code reproduces the old predictions to 5e-13.
- **Not done:** no commit, no repository file touched. The originals in `mythos-rl166-form/` are unchanged (hashes checked).

Files are in `/Volumes/JW-EXT/scratch/mythos-passrate/`:
- `q4b_gates_b.out`
- `q1e_attenuation_b.out`
- `q3c_estimable_b.out`
- `rl166b.py`