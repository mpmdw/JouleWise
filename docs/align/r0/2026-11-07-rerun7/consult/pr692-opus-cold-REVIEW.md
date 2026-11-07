VERDICT: ADMIT_WITH_FIXES

Seat: opus (cold, executing). Branch `fix/2026-11-07-r0-smc-coverage-cell`, one commit `3c0b71b24` on `e1a91226e`.
Worktree untouched (`git status --short` empty). All scratch, scripts and outputs are in /Users/edr/night-archive/r0-smc-cov/opus/.

## Summary

The coverage change does what it says, and I could not break it. With `tolerance_ns = NS // 2`, `nearest()` puts every midpoint stamp in exactly one 1 s cell. The tolerance check then always passes, so the 99% bar becomes "at least 99% of cells hold at least one valid reading". That is the property the bar was meant to protect. I found no capture with genuinely missing readings that the change newly lets through. Other callers are bit-identical. The new tests fail on the base code and pass on the branch.

The blocking concern is outside the diff, but this diff exposes it. On the real capture the change turns "inconclusive" into `status: pass`, with s_fast = `Tg2I` and s_slow = `TaRT`. Both picks rest on artifacts that the unchanged classifier does not catch (finding 1). Merging is safe because R0 picks are marked provisional. Using that "pass" as the R0 readability bar, or carrying Tg2I/TaRT into R1 or the thermal gates, is not safe until finding 1 is ruled.

## Findings, ranked

### 1. HIGH (outside the diff, now reachable): the real capture "passes" with die picks driven by power-gating placeholder values and heatsink picks measured against an unsettled idle

Command:
`PYTHONPATH=<wt> <venv python> -B -P opus/real.py` (full output in opus/real.txt), then `opus/series.py` and `opus/picks.py`.

Output (branch `rank`, real capture r0-v4-20261107T0810Z; samples sha256 matches r0.json):
```
OLD(100ms) status inconclusive  die 0 heatsink 0 record-only 403   (identical to the stored r0.json response)
NEW(500ms) status pass selection {'s_fast': 'Tg2I', 's_slow': 'TaRT'} select_keys {'s_fast': 'Tg2I', 's_slow': 'TaRT'}
   die 16 heatsink 141 record-only 246
   reasons: heatsink 141, record-only 131, constant/stale idle 115, die 16
   min-phase coverage min/med/max 1.0 1.0 1.0
r1 status pass {'s_fast': 'Tg2I', 's_slow': 'TaRT'}
```
What the picks rest on:
```
Tg2I idle first10 [-2.75, -2.75, -2.75, 53.41, 53.38, -2.75, ...]  idle median -2.75, pstdev 10.241
DIE candidates (all 16 are Tg*): idle mode is a fixed sub-zero value (-0.5, -2.75, -8.75, -9.0) in 95% of idle reads;
  recovery returns to that same value within seconds (tau 1.68-1.69 s for all 16)
TaRT: idle drifts 34.35 -> 30.61 degC over the 300 s idle (30 s means 33.97 ... 30.65); noise_floor 1.137;
  delta_t60 0.064 degC, so the t63 threshold sits 0.04 degC above the idle median; t63 = 50.9 s; tau 123 s
heatsink n 141; idle drift (first 30 s mean minus last 30 s mean) min/med/max 2.75 / 11.5 / 33.77 degC; all 141 drift > 1 degC
```
What this means:
- The 16 "die" keys read a fixed below-zero placeholder whenever the GPU is power-gated. `valid_value` accepts any value in -40..150 degC, so the placeholder counts as a temperature. Their "rise" (about 88 degC) is measured from that placeholder. Their t63 (about 2.9 s) and cooling tau (1.68 s) time the GPU switching on and off, not heat flow. Tg2I may well be the GPU die sensor, but its classification numbers are not thermal time constants. A downstream gate reading s_fast at idle would see -2.75 degC.
- Every heatsink candidate's idle baseline was still cooling by a median of 11.5 degC, so the machine entered the step warm. TaRT, the slow pick, has a 50-60 s rise of 0.064 degC against a 1.14 degC noise floor, so its t63 is a crossing inside the noise. The heatsink rule asks only for t63 > 5 s, so it passes.
- None of this comes from the coverage change. The rules that admit these keys are unchanged, and the old 100 ms refusal had been masking them for the wrong reason. Refusing this diff would keep a wrong-reason refusal, so I do not refuse it.
- Fix required before the result is used, not before merge: route to a classifier lane (a) sub-zero constant placeholder series on GPU keys and (b) an idle-settledness condition, or a baseline taken at load onset. Until then, record the branch's R0 "pass" on this capture as a flag, not as "readability bar met". The R0 report already says PROVISIONAL / PENDING_R1_CLASSIFICATION, and R1 runs the same `rank`.

### 2. MEDIUM (inside the diff's effect; representation, flag not refuse): the same R0 report now shows 2% coverage next to a 100%-coverage "pass"

Command: `opus/report_cov.py`. Output: `branch script-level coverage identical to stored: True frac 0.02`.
`scripts/align_smc_enumerate.py` line 130 still calls `temperature.coverage(...)` at the default 100 ms, and `summary.md` prints "Complete-sensor sample fraction: 0.02". On the branch the same `r0.json` would carry `coverage.all_keys.sample_fraction = 0.02` while `response` reports 100% per-phase coverage and `status: pass`. Keeping the default for other callers was intentional. The report should still say which tolerance each number uses, or use the cell tolerance for the classifier capture, so that a reader does not see a contradiction.

### 3. LOW: `Coverage` docstring and the `edge_policy` string are false at 500 ms

At `tolerance_ns = NS // 2`, `boundary()` snaps every span edge, because every instant is within half a period of a grid point. "Partial cells excluded; near-grid edges snapped" (docstring and `report()["edge_policy"]`) is therefore wrong for this counter: an edge half-cell is counted as a whole expected cell. The same applies to `gaps_ns`, whose threshold becomes NS + tolerance = 1.5 s (`rank` does not use it). The practical effect is bounded: at most one unfillable cell per edge, and only when the first reading arrives more than 500 ms late (case 10 below). The sampler's first read is at `due = origin`, so this does not happen in practice.

### 4. LOW (number rule): new test asserts a 4 degC floor that matches no rule

`tests/align/test_smc_classifier_v4.py`: "The synthetic 8 degC rise exceeds the brief's 4 degC floor" and `assertGreaterEqual(sensors["THEA"]["observed_rise"], 4)`. The classifier's registered heatsink floor is ΔT >= 3.0 degC (`RULE`, `heatsink = ... rise >= 3.0`). The 4 has no derivation in the code. Use the rule's 3.0, or cite where 4 comes from.

The other numbers in the new tests carry derivations, and I checked them:
- t63 3 ± 1 s: one sample period.
- THEA t63_end 50 ± 3 s: 1 s plus 0.1 / (8 / (50e)) = 1.70 s noise over slope, total 2.7 s.
- tau 120 ± 6 s: 1 s plus 0.1 / (8 / (120e)) = 4.08 s, total 5.1 s.
- 882/900 is exact count arithmetic.
- 0.99 is the registered bar.
- 0-150 ms start lateness and 50-400 ms read time are labelled measured-shape. The real capture shows 0-150 ms lateness and 79-392 ms reads, so they match.

### 5. LOW: the code comment's rationale is slightly off and cites a path that does not resolve

The `rank` comment says the old 100 ms "refused measured jitter up to ~150 ms". On the real capture the start lateness is 0-150 ms, but the counter measures midpoint offsets from the first reading's start (`grid_ns = min(started)`, stamp = midpoint). Those offsets are 40.9-222.5 ms, with a median of 141-173 ms per phase (real.txt). Lateness plus half the read time is what broke the 100 ms window. The margin to 500 ms is about 278 ms at the worst observed offset. The comment also cites `r0/2026-11-07-rerun7/NOTE.md`. That path is not tracked in the repo and does not exist under /Users/edr/night-align/r0/ or /Users/edr/night-archive/r0/.

### 6. INFO (existed before the diff, unchanged by it): the count-only bar passes a contiguous 9 s hole at load onset, which misclassifies a 3 s die

Command: `opus/attack2.py` case 11 (on-grid reads; reads at load seconds 1-9 removed).
```
11 on-grid reads, 9 s stall at load onset (new 500 ms): status=inconclusive sel={'s_fast': None, 's_slow': 'THEA'} load_cov=0.99 t63(TDIE)=6.555
11 same capture under old 100 ms:                      status=inconclusive sel={'s_fast': None, 's_slow': 'THEA'} load_cov=0.99 t63(TDIE)=6.555
   TDIE class record-only
```
The result is the same under both tolerances, so the diff does not cause it. The 99% bar allows 9 missing cells anywhere. If they sit at the step onset, a 3 s die reads t63 = 6.6 s and drops to record-only. That is a wrong selection which passes coverage. `Coverage.report` already computes `gaps_ns`, and `rank` ignores it. This belongs in the same classifier lane as finding 1.

## Test runs (step 1)

One process per module, `PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov <venv python> -B -P -m unittest tests.align.<m>`:
```
test_smc_classifier_v4  Ran 6   OK
test_thermal_coverage   Ran 5   OK
test_smc_selection      Ran 9   OK
test_smc_quiet          Ran 19  OK
test_r0_host            Ran 44  OK
test_thermal_gate       Ran 31  OK
test_thermal_desk       Ran 21  OK
tests.hazards.test_temperature      Ran 13 OK   (other Coverage caller)
tests.hazards.test_smc_enumeration  OK          (script caller)
```
Counterfactual: base code (`git archive e1a91226e joulewise scripts`) with the branch tests, in opus/base. `test_smc_classifier_v4` gives 2 errors (no `tolerance_ns` kwarg) and 1 failure (`0.2356 != 0.98`). `test_thermal_coverage` gives 11 errors. The new tests do test the change.

Environment trap, for the lead: without `-P`, `python -m unittest` puts the current directory first on `sys.path`. My agent shell's directory resets to /Users/edr/code/JouleWise between calls, so the brief's standalone `cd` does not carry over for an agent. My first run therefore imported `/Users/edr/night-custody/.../joulewise` and failed (4 to 11 errors per module). I confirmed the import path, then reran with `-P`. Agent seats should use `-P`, or check `module.__file__`, rather than rely on a standalone `cd`.

## Break attempts (step 3)

Command: `opus/attack.py` and `opus/attack2.py` (outputs in attack.txt and attack2.txt). These use the synthetic die/heatsink world from the branch test (TDIE tau 3 s, THEA 50/120 s) with altered timing. "Holes" means missing 1 s cells in the 900-cell load phase; the 99% bar allows at most 9.

| case | load coverage | result | right? |
|---|---|---|---|
| 0 production-shaped jitter | 1.0 | pass TDIE/THEA | yes |
| 1 1.5 s period, whole load | 0.667 | refuse | yes |
| 2a 1.5 s period for 20 s (7 holes) | 0.9933 | pass | yes: 893/900 meets the bar |
| 2b 1.5 s period for 30 s (10 holes) | 0.9889 | refuse | yes |
| 2c 2.0 s period for 20 s (10 holes) | 0.9889 | refuse | yes |
| 3a stalled reader 9 s | 0.99 | pass | count-correct; see finding 6 |
| 3b stalled reader 10 s | 0.9889 | refuse | yes |
| 4 duplicate bursts in one cell, then a hole, every 50 s | 0.98 | refuse | yes: each duplicate counts once |
| 5a nine 1.2 s reads | err 0.01 | refuse | yes: >1 s reads are read errors and never fill a cell |
| 5b eight 1.2 s reads | 0.9911, err 0.0089 | pass | yes, within both bars |
| 6 every read 0.95 s long | 0.9989 | inconclusive | not a false pass |
| 7' pairs 100 ms apart with 1.9 s gaps (the sampler cannot produce this) | 0.9989 | pass, t63 3.13 vs 3.01 | count-correct; the fit barely moves |
| 8 first read on time, rest 480 ms late | 0.9989 | pass | yes: the cell shifts by one and each reading counts once |
| 9 first read on time, rest 0-600 ms late | 0.837 | refuse | false refusal, not a false pass; real offsets are 40-222 ms |
| 10 first read of each phase 600 ms late | 0.904 | refuse | false refusal: the grid is anchored on the first start; the sampler makes the first read punctual |

No capture with genuinely missing readings passes the 99% bar under 500 ms when it should fail. Every pass corresponds to at least 99% of cells holding a distinct valid reading. The two new failure modes (cases 9 and 10) err toward refusing. Both need offsets above 500 ms from the first-reading grid. The real capture's worst offset is 222 ms.

Other callers, checked by code and by run:
- `thermal.py:128` (Sidecar), `thermal_gates.py:206`, `thermal_desk.py:130` and `thermal.coverage()` (used by the script report) all construct `Coverage` without the keyword, so they keep 100 ms.
- No code reads or overrides the `Coverage.tolerance_ns` class attribute.
- On the real capture, the script-level `coverage` block computed by the branch is byte-identical (as sorted JSON) to the stored base-code block.

Boundary and tie behaviour at 500 ms:
- An exactly-half stamp rounds forward (`(t - grid + NS//2) // NS`) and counts once. The new test covers this.
- Edge snapping always applies at 500 ms (finding 3).

## Number rule (step 4)

- `NS // 2` is derived from the 1 s period: half a period gives each stamp exactly one cell.
- The validator range (0, NS//2] is derived the same way: above half a period the check is vacuous.
- 0.99 and the 1% read-error bar are the registered bars and the diff does not change them.
- The test tolerances are derived (finding 4 lists them), except the unexplained 4 degC assertion.
- The comment's "~150 ms" understates the quantity that matters (finding 5).
- I propose no new bar.
