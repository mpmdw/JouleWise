VERDICT: ADMIT_WITH_FIXES

Delta executing review of PR #692, eb6e8e493..e3b4bab55 (Erratum 4), Fable 5.1, blind.
Tree: /Users/edr/code/jw-wt/r0-smc-cov at e3b4bab55 (HEAD confirmed by `git rev-parse`). Parent
eb6e8e493 extracted with `git archive` to <scratch>/parent/. Interpreter:
/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P,
PYTHONPATH set to one tree per run; every script prints `module.__file__` (head runs show
/Users/edr/code/jw-wt/r0-smc-cov/joulewise/..., parent runs show <scratch>/parent/joulewise/...).
Journal: /Users/edr/night-align/r0-v4-20261107T0810Z/smc, 1,800 rows, SHA-256
16aa5307ffc24f55bc20d66823e8c9375d84da6ac723fa77b23d024f66244984 (matches the doc comment).
Scratch: /Users/edr/night-archive/r0-smc-cov/cold4/fable/ (harness.py = cold3 harness with SCRATCH
repointed; item1.py, item3.py, sources.py, degenerate.py, degenerate2.py, docnums.py; copies of the
cold3 Opus h.py/d3.py/f.py so their outputs land here, not in cold3). Nothing in the worktree, night-align
or night-custody was written.

Summary: every Erratum 4 item is implemented as written with its derivation beside the number; all
seven listed faults reproduce on the parent and are gone at the head; all eleven replay-table rows
re-run through the real receipt and match; D1(d) survived every D6-admitted perturbation I could
compose (single missed reads at and around the crossing, cell-late first reads 0.3-1.9 s, overruns
0.3-1.6 s, scales 0.5-1.3, and combinations); the three Erratum 2 regressions hold; 127 tests in the
five touched modules pass. The fixes asked for are about what the rule leaves unguarded (a wholesale
D1(d) exclusion passes the receipt silently) and about the slow pick, which still turns on the first
recovery read and swaps under an admitted perturbation. Neither changes the real capture's result
(Tf18 / TaLP, reference Tf18, excluded TVH3 only, receipt pass).

## 1. Erratum 4 items: faults reproduced on eb6e8e493, gone at e3b4bab55

Command (both trees): `PYTHONPATH=<tree> python -B -P item1.py real recovery_delay:1.0
overrun_load:1.3 miss1:Tf2B:recovery:0 hole2:Tf2B:load:236 overrun_load:1.6` (rank plus the real
receipt on a rehashed scratch copy, capture subprocess no-op).

| Fault | Parent eb6e8e493 | Head e3b4bab55 |
|---|---|---|
| recovery_delay 1.0 s | fast Ts0h, ref Ts0h, 20 keys excluded incl. Tf18/Tf2B/whole Tf family; receipt pass | fast Tf18, ref Tf18 (rise 45.68), excluded TVH3; receipt pass |
| overrun_load 1.3 s | fast TV0m, ref TV0m, 136 keys excluded; receipt pass with duration flags | fast Tf18, ref Tf18 (45.67), excluded TVH3; receipt pass, same flags |
| miss1 Tf2B recovery 0 | fast Tf1B, ref Tf24, excluded TVH3, Tf18, Tf2B; receipt pass | fast Tf18, ref Tf18, excluded TVH3 |
| hole2 Tf2B load 236-237 | fast Tf1B, ref Tf24, excluded TVH3, Tf18 (Tf2B D6 record-only) | fast Tf18, ref Tf18, excluded TVH3; Tf2B D6 record-only (load empty cells 2) |
| 20 stationary Gaussian keys, sigma 0.05 (`d3.py quiet:0.05 300 400`) | settle_keys 0, settled None | settle_keys 20, settled True at 300 s, settle_consecutive 241, largest in-set slope 0.032 degC/min |
| live-desk smc inconclusive (`f.py`, backend module relabelled r0_mlx) | status pass, complete_r0 True | status pass, complete_r0 False, smc_selection_missing True; smc pass gives complete_r0 True, smc fail still stops after smc |
| overrun_load 1.6 s refusing through D6 (Opus definition, `h.py overrun:load:1.6`: load end +1.6 s with no reads, recovery shifted) | receipt inconclusive, Tf18 "D6: two consecutive empty one-second cells" (load empty 2) | receipt pass, Tf18 die, load empty 0, duration flag load 901.6 s; picks Tf18/TaLP |

(My own `overrun_load` definition, which relabels recovery reads as load, never produced the D6
refusal on the parent; it produced the reference-walk fault instead. Both are in the table above.)

Derivations beside the numbers (checked in the diff): `REFERENCE_TIE_S = 1.0` (1 Hz crossing
resolution), `HEAT_ORDER_MARGIN_C = 1.0` (gate band floor; 0.46 degC measured Tf spread; three
noise floors describe one sensor), `CLAMP_DISTINCT` comment (>=10 distinct values span >=9q, ~300
reads span ~5 sigma, sigma >= 1.8q, mode fraction <= 1/(1.8 sqrt(2 pi)) = 0.22 < 0.40; arithmetic
checked), empty-set idle end reuses `SETTLE_COUNT` (G0's ten confirmations), phase flag stays 1 s.
The stable threshold is `baseline + rise/e` with `rise` the load-tail median already computed, the
crossing is interpolated over valid recovery reads, and the time is `stable - phases["load"]["end_s"]`
(actual load end), as Erratum 4 states. The tie set is `reference_cooling_s <= shortest + 1.0`, the
reference is the largest rise (lexical tie) in it, and the exclusion is `rise > reference rise + 1.0`.
Class tau is untouched. `r0_host` copies `heat_ordering_reference`, `_rise` and `_excluded` into the
receipt; `align_smc_enumerate.py` prints them and both cooling times. `r0_runner` sets
`smc_selection_missing` and requires an smc pass for `complete_r0`. Cells end at `min(deadline_s,
end_s)`; the receipt reconstructs legacy deadlines from the profile (idle: min(actual end, cap)).

## 2. Replay table (docs/align/smc_temperature.md "Erratum 4 recorded-journal replays")

All eleven rows re-run at the head through the real receipt (item1.py, item3.py --receipt, h.py):

| Case | Fast | Slow | Ref rise | Excluded | Receipt | Matches doc |
|---|---|---|---:|---|---|---|
| real | Tf18 | TaLP | 45.68 | TVH3 | pass | yes |
| recovery_delay:0.3 | Tf18 | TaLP | 45.68 | TVH3 | pass | yes |
| recovery_delay:1.0 | Tf18 | TaLP | 45.68 | TVH3 | pass | yes |
| overrun_load:1.3 | Tf18 | TMVR | 45.67 | TVH3 | pass (load/recovery flags) | yes |
| overrun_load:1.6 | Tf18 | TMVR | 45.67 | TVH3 | pass (flags) | yes |
| scale:0.6 | Tf18 | TVS2 | 27.41 | TVH3 | pass | yes |
| scale:0.85 | Tf18 | TaLP | 38.82 | TVH3 | pass | yes |
| scale:1.2 | Tf18 | TaLP | 54.81 | none (TVH3 above_junction, no rise) | pass | yes |
| miss1:Tf2B:recovery:0 | Tf18 | TaLP | 45.68 | TVH3 | pass | yes |
| hole2:Tf2B:load:236 | Tf18 | TaLP | 45.68 | TVH3 | pass | yes |
| opus_overrun_load:1.6 | Tf18 | TaLP | 45.67 | TVH3 | pass (load flag) | yes |

Comment numbers, re-derived through the real receipt path (docnums.py, module r0_host at the head):
real: reference rise 45.67562675476074, Tf2B stable 24.248078848970863 s, Tf18 24.63169390416192 s,
separation 0.38361505519105776 s (comment: 0.383615055191057, same to the printed digits);
overrun_load:1.3: 45.670000076293945; scale 0.6 / 0.85 / 1.2: 27.40537605285644 /
38.824282741546625 / 54.81075210571288. Every value in the comment matches the receipt output to
the last digit. Load `phase_seconds` is 900.0 in every case (the grid ends at the reconstructed
deadline, including under the overrun).

## 3. Trying to break D1(d)

Reference candidates at the head on the real journal (sources.py): 118 D4-qualified keys, none with
an undefined stable time; shortest Tf2B 24.25 s; within the 1 s window Tf2B, Tf24, Tf2D, Tf2E, Tf18
(rises 45.63, 45.27 x3, 45.68); next Tf1B at 25.45 s. No qualified key has a stable time below 24 s
(keys below 20 s: Ts1P 0.17 s, TH0a 1.46 s, TH0b 2.08 s all fail D1(b); TH0x 2.02 s rise 0.54 not
resolving). TVH3 stable 33.39 s, outside the window.

Admitted perturbations (item3.py; every row gave reference Tf18 unless stated, exclusions TVH3 only,
fast pick Tf18):
- miss1 Tf2B at recovery 22, 23, 24, 25, 26; miss1 Tf18 at 23, 24, 25; miss1 Tf24 at 24. A missed
  read at the crossing moves Tf2B's stable time 24.25 -> 24.06 s (chord below the convex decay, so
  earlier), Tf18's 24.63 -> 24.69; the window keeps the five keys.
- overrun_load 0.3, 0.5, 0.8, 1.0 (under the flag bar), 1.3, 1.6: all stable times shift together
  (Tf2B 23.96 ... 23.26 s), window unchanged.
- recovery_delay 0.5, 0.7, 1.5, 1.9 (1.5 and 1.9 leave one empty recovery cell, admitted): stable
  times unchanged at 24.25 / 24.63.
- scale 0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.3: stable times invariant (threshold scales with rise);
  reference rise 22.84 ... 59.38; at 1.3 TVH3 is above_junction without a rise so the list is empty
  (same as the doc's 1.2 case).
- Combinations: scale:0.85+recovery_delay:1.0; scale:1.3+overrun_load:1.3; scale:0.5+miss1:Tf2B:24;
  recovery_delay:1.0+miss1:Tf2B:0; overrun_load:0.9+miss1:Tf18:0; recovery_delay:1.0+miss1:Tf18:24;
  scale:0.6+overrun_load:1.0+miss1:Tf2B:0. All: reference Tf18, TVH3 only.
- Per-key gain changes: scale_key Tf18 x0.97 -> reference moves to Tf2B (45.63), still TVH3 only;
  scale_key Tf2B x1.03 -> reference Tf2B (47.00), TVH3 only. scale_key Tf1B x1.03 (rise 46.72, 1.2 s
  behind the window) -> Tf1B excluded; scale_key TCDX x1.1 -> TCDX excluded. So a real key is excluded
  only if its rise exceeds the in-window maximum by more than 1.0 degC while sitting more than 1 s
  behind; on this capture that needs a 2.3% gain difference on a 45 degC rise, against the measured
  1% (0.46 degC) spread. The margin is absolute while gain spread is proportional; with the 125 degC
  ceiling the rise cannot reach the 100 degC at which 1% spread meets 1.0 degC. Informational.

Degenerate stable time (degenerate.py):
- A D4-qualified key whose recovery never crosses baseline + rise/e: constructed by offsetting
  Tf18's recovery by +17, +17.5, +20 degC. Stable 376.9 s, 428.2 s, None respectively, but class tau
  also moves to 91, 96, 122 s, so the key leaves the D4 set and cannot be the reference; Tf2B becomes
  reference and fast pick, TVH3 only excluded. The code path for `reference_cooling_s is None` drops
  the key from `sources` silently (no flag); I could not construct a D4-qualified key that reaches it,
  because the class tau (first-recovery-read peak) and the stable crossing are coupled: a key that
  never reaches rise/e above baseline cannot cross peak/e above baseline within 60 s unless its first
  recovery read exceeds e x rise above baseline. Not a hazard on this design; see L2 for the flag.
- A key already below the threshold at its first recovery read returns that read's time (index 0 in
  `_crossing`). See M1.

## 4. Regressions against eb6e8e493's correct behaviour

- Two-cell holes still remove a pick and the receipt still refuses a genuine hole (item1.py, head):
  hole2 Tf18 recovery 100 -> Tf18 record-only (recovery empty 2), fast Tf2B, receipt pass;
  hole2 Tf18 load 898-899 (the last two cells before the deadline) -> Tf18 record-only (load empty 2),
  fast Tf2B; drop2 recovery 100, drop2 recovery 0, drop2 load 898, drop2 recovery 598, drop2 idle 298
  (whole samples removed, every key holed, including at each phase's last two cells) -> no picks,
  receipt inconclusive "SMC die/heatsink selection unresolved". The deadline change does not hide a
  hole inside the grid. Exit overrun with no reads (h.py overrun:recovery:1.6) now passes with the
  recovery duration flag, as Erratum 4 intends; on the parent it refused through D6.
- Adaptive idle still waits on cooling keys (flicker.py, head): a key cooling at 1 degC/min until
  330 s holds idle to 383 s (settle_consecutive 10) with and without a flicker key beside it; flicker
  SD 3, 5, 8 degC beside a settled key ends idle at 300 s with settle_keys 1; a cooling key with noise
  0.25 degC beside a settled one is not waited on (idle 300 s, settle keys [TGAT]) -- the documented
  "not changed" case.
- Empty settle set (d3.py quiet:0.5, all keys noise 0.5 degC): idle ends at 300 s, settled None,
  settle_keys 0, settle_empty_consecutive 241, deadline_s 300; with cap 305 the same.
- Tests: `python -B -P -m unittest tests.align.test_r0_host tests.align.test_r0_scheduling
  tests.align.test_smc_classifier_v4 tests.align.test_smc_quiet tests.align.test_smc_selection`:
  127 tests OK (pytest is not installed in the venv).

## 5. Number rule

- New constants carry derivations beside them (REFERENCE_TIE_S, HEAT_ORDER_MARGIN_C, CLAMP_DISTINCT
  comment); the doc repeats them. Checked: 1/(1.8 x 2.5066) = 0.222.
- Tests: `assertAlmostEqual(row['reference_cooling_s'], 30.8*(1+math.log(.82)), delta=1)` -- a 1 s
  bar on a synthetic crossing with the derivation (slow-pole crossing, 1 Hz resolution) in the
  comment; fine. `assertAlmostEqual(shifted['reference_cooling_s'], row['reference_cooling_s']-1.3)`,
  `assertAlmostEqual(deviation_seconds, 1.6)` and `assertAlmostEqual(actual_seconds, 7.6)` use the
  default 7 places (1e-7 s) on synthetic clocks and an exact 1.3 s shift of identical inputs: that is
  float noise on bit-identical arithmetic, admissible under the rule's "identical code on identical
  inputs" clause, but the bar is not written down. Nit N1.
- No new tolerance on a measured quantity was introduced without a derivation.

## Findings by severity

### Medium

**M1. A fast, small-rise key captures the D1(d) reference and the receipt passes with the whole Tf
family excluded.** The rule's premise (the fastest D4-qualified key is the heat source) has no guard
against a low-thermal-mass key that steps with the load but is not on the main path. Executed
(degenerate.py, degenerate2.py): the real journal plus one synthetic key TZZZ (baseline 30 degC,
step 8 degC, tau 2.0 s or 3.0 s, noise 0.05). TZZZ passes D1(a)-(c), D1(b) (largest one-second
jump 3.39 degC < rise/2 = 4.0), resolving, tau 2.02 s, stable 2.04 s. It is the only key in the
window [2.04, 3.04] s, so it becomes the reference with rise 8.0; 198 keys are excluded including
Tf18 ("D1(d): rise exceeds TZZZ reference rise +1.0 degC"); the fast pick is TZZZ and the slow pick
moves to TaRT. The receipt: `status pass`, picks {TZZZ, TaRT}, no flag. No key of this kind exists on
this capture (nothing qualified below 24 s), so this is a design exposure for other hardware or an
R1 step with a different heater, not a defect on the present data. Fix options for the lead, not a
rule I am choosing: (a) the receipt records a flag when D1(d) excludes more than the one firmware
channel it was built to remove, or excludes the largest-rise D4-qualified key, which is the Erratum 4
replay expectation ("TVH3 only") written as a check; (b) require the reference's rise to be within
the margin of the largest D4-qualified rise among keys whose stable time is within one class-tau
window (60 s), which would make TZZZ a diagnostic instead of the source. Either keeps the real
capture's result.

**M2. The slow pick still turns on the first recovery read and swaps under an admitted
perturbation.** Erratum 4 keeps class tau on the first-recovery-read peak and uses it for the D5
band-hold pick. Executed (degenerate2.py): real journal TaLP hold 86.2 x ln 20.54 = 260.7 s, TMVR
90.5 x ln 17.07 = 256.9 s (3.8 s apart). recovery_delay 1.5 s or 1.9 s (one empty recovery cell,
admitted) and overrun_load 1.3 s (flagged, admitted) move TaLP's class tau to 82.9 s (hold 250.7)
and TMVR's to 89.9 s (255.1): the slow pick becomes TMVR. recovery_delay 0.3 s (no flag, no empty
cell) already moves TaLP's tau 86.2 -> 85.2 and Tf18's 24.7 -> 30.8 s (a 25% change in a printed
number from one dropped first read). With the stable cooling time already computed, the holds are
TaLP 84.9 x 3.02 = 256.6 s and TMVR 89.9 x 2.84 = 255.1 s on the real journal, and TaLP 83.6 /
TMVR 88.6 under overrun 1.3 (256.6 vs 251.4 at recovery_delay: unchanged) -- TaLP in every case.
The doc's table shows the swap ("The Fable slow pick changes because the first recovery read
changes the unchanged D5 class tau") and D5 is provisional until the first settled capture, so this
is a disposition item: either D5's hold uses the stable cooling time (the number is already in the
row), or the printed slow pick is labelled as sensitive to the first recovery read until R1.

### Low

**L1. Legacy idle exit overrun of 2 s or more still refuses through D6.** h.py overrun:idle:1.6 on
the head: receipt inconclusive, Tf18 "D6: two consecutive empty one-second cells" in idle, no
duration flag (301.6 s is inside the 300-1,200 s adaptive range). Cause: for a journal without
`deadline_s` the receipt reconstructs the idle deadline as min(actual end, cap), so an idle exit
overrun stays inside the grid; the doc says so ("legacy adaptive idle from its actual end"). The next
collector records `deadline_s`, and the re-run 7 journal has no idle overrun, so this only affects
replays of old journals. Record it beside the rule, or reconstruct the legacy idle deadline as the
last second with any read, whichever the lead prefers.

**L2. A D4-qualified key with no stable crossing is dropped from the reference set silently.**
`sources` requires `reference_cooling_s is not None`; a key that fails this still competes for the
fast role and is not flagged. I could not construct a qualifying key that reaches the path (see
section 3), so this is a record-keeping gap: print the count of D4-qualified keys without a stable
time in the receipt so a future capture that hits it is visible.

**L3. `rank` on a bare legacy capture differs from the receipt's reconstruction.** Calling `rank`
directly on the overrun_load:1.3 journal (no `deadline_s`) gives reference rise 45.66 (two
relabelled recovery reads enter the load tail); the receipt path reconstructs the 1200.44 s deadline
and gives 45.67. Documented ("bare historical captures retain end_s"), and only the receipt path is
authoritative; note it where the table says every case passes through the receipt.

### Nits

**N1.** The three `assertAlmostEqual` calls with default places on synthetic clocks (tests
test_smc_classifier_v4 / test_r0_host / test_smc_quiet) should state the bar (exact arithmetic on
identical inputs; `assertEqual` or `places=9` with the reason) so the number rule is visible.

**N2.** Doc wording "Fable's `overrun_load` ... shortens recovery; the reader grid still ends at the
load deadline" is right; the parallel sentence for `opus_overrun_load` could say the recovery grid
also starts at the shifted recovery start, which is why the Opus case keeps TaLP while the Fable
case moves to TMVR (the shift reaches the first recovery read in one and not the other).

## Not findings (checked)

- D1(c)/D1(a) checks still run over every sample labelled with the phase, including exit-overrun
  reads (the `continue` for out-of-grid reads sits after them).
- `phase_read_error_fraction` now divides by in-grid attempts, not all phase rows; handshake and exit
  reads no longer add errors.
- Empty-set idle: ten consecutive empty evaluations end idle only after the 300 s minimum; a skipped
  second resets the count; `settled` stays None.
- The receipt and summary print the reference, its rise, the excluded list and both cooling times
  (test_r0_host asserts the summary strings; the receipt fields are copied by name).
- D6 per-phase hole check, the 0.99 coverage bar and the 1% read-error bar are unchanged.
