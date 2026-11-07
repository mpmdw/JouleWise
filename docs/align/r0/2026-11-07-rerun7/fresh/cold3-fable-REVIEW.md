VERDICT: ADMIT_WITH_FIXES

Cold executing review (Fable 5.1, blind) of `git -C /Users/edr/code/jw-wt/r0-smc-cov diff c0c460fd9..eb6e8e493`
(695574428 Erratum 2 fixes; eb6e8e493 Erratum 3) against DECISION.md D1-D6 and Errata 1-3.

Setup: every run used `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P`
with `PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov` (head) or `PYTHONPATH=<scratch>/parent` (a `git archive c0c460fd9`
extraction of joulewise/, scripts/, tests/, configs/). Each run printed `module.__file__`; head runs resolved to
`/Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/smc_enumeration.py` and `.../r0_host.py`, parent runs to
`<scratch>/parent/joulewise/...`. The worktree was not edited (`git status --short` empty). TMPDIR = scratch.
Harness and raw outputs are in `/Users/edr/night-archive/r0-smc-cov/cold3/fable/` (`harness.py`, `sources.py`,
`alt_ref.py`, `tau_alt.py`, `settle_real.py`, `flicker.py`, `runner_inconclusive.py`, `out-*.txt`).

Real capture: `/Users/edr/night-align/r0-v4-20261107T0810Z/smc/{r0.json,samples.jsonl}` (1,800 samples, 403 keys,
phases idle 300.0 / load 900.0 / recovery 600.0 s, idle-to-load handshake 0.33 s, load-to-recovery 0.17 s).
The receipt was exercised by calling `r0_host.smc_enumeration(repo, <scratch copy>, None)` with `subprocess.run`
replaced by a returncode-0 no-op, so the receipt read a scratch copy of the real r0.json + journal (SHA re-computed
when a scenario edits the journal).

Summary: all six Erratum 2/3 items (a)-(f) reproduce on c0c460fd9 and are gone at eb6e8e493; the real capture gives
Tf18 / TaLP with receipt `pass`; the touched test modules pass (142 tests). One High finding: D1(d) as built is
anchored on the argmin cooling tau over about 120 near-identical die keys, and that tau is measured from the first
recovery read, so a one-cell (1 s) later first recovery read, or a +1.3 s load overrun, moves the reference and
excludes Tf18 and the whole Tf family; the receipt still prints `pass`. The fix set treats such overruns as flags, so
this is a production-shaped condition. A stable-threshold tau (same crossing, threshold from the load-tail rise, time
from the load phase end) keeps Tf2B as the reference and excludes only TVH3 in every scenario tried.

## Findings by severity

### HIGH

**H1. D1(d) removes the real fast pick when the first recovery read lands one cell later; receipt still `pass`.**

Mechanism (code, `rank`): `peak = cooling[0][1] - baseline`, `tau = crossing(cooling, baseline + peak/e) - cooling[0][0]`.
The Tf keys drop about 6 degC in the first second after the load stops (Tf18: 78.92 at t=0.0, 72.99 at t=1.0,
66.87 at t=2.1 s; `out-tv0m-series.txt`). If the first recovery read lands one cell later, the "peak" is 6 degC lower,
the 1/e threshold falls, the crossing is later, and the Tf family's tau grows from 24.7 to 30.8 s. The argmin then
moves to a key whose first-second drop is small (Ts0h, tau 27.6 s, rise 38.5), and D1(d)'s limit falls from 45.84 to
38.72, excluding 20 keys including Tf18, Tf2B, Tf48, TCMb's family and TVV0.

Executed (head; scenario `recovery_delay:S` moves `recovery.start_s` by +S and drops reads in the handshake gap, which is
what a slower quiet census between `load.stop()` and the recovery `phase_start` stamp does; the real handshake was 0.17 s):

```
PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov python -B -P alt_ref.py real
  D4 qualifiers: 118; tau min 24.42 (Tf2B) ... Tf18: tau 24.74 rise 45.68 class die
  A as built: reference Tf2B limit 45.84; excludes 1: ['TVH3']            picks: Tf18 TaLP
PYTHONPATH=... python -B -P alt_ref.py recovery_delay:0.3      (same result at 0.5 and 1.0)
  D4 qualifiers: 119; tau min 27.63 (Ts0h) ... Tf18: tau 30.82 rise 45.68 class record-only
  A as built: reference Ts0h limit 38.72; excludes 20: ['TVH3','Tf18','Tf2B','Tf1B','Tf24','Tf2D',...]
  picks as built: Ts0h TaLP
PYTHONPATH=... python -B -P harness.py overrun_load:1.3 --rank --receipt
  rank: s_fast TV0m, s_slow TMVR, heat_ordering_reference TV0m; D1(d) excluded 131 keys (Tf18 record-only:
  "model-free die step response; D1(d): rise exceeds TV0m rise +3 source noise floors")
  receipt: status pass, selection {TV0m, TMVR}, phase_duration_flags [load +1.3, recovery -1.3]
```

The same overrun on the parent gives Tf18 / TMVR (`out-parent-overrun_load:1.3.txt`), so the pick change is the new
rule's doing. D4 alone (largest rise among die class) still picks Tf18 in all of these; D1(d) is the only cause.

Why this is production-shaped: the collector's own comment says the 5 s census takes 70-330 ms, Erratum 2 says quiet
probes can overrun a phase deadline, and the GPU child has its own hard duration bound, so the interval between the
real GPU stop and the first recovery read is a scheduling accident of up to about one cell. The receipt has no flag
for "D1(d) excluded N keys"; `summary.md` only shows it in per-key reasons.

Secondary fragility, same rule: on the real capture Tf18 survives by 0.16 degC (rise 45.68 against the limit 45.84 =
Tf2B 45.63 + 3 x 0.070). The Tf family's rises spread over 0.5 degC (45.22-45.68), so a 3-floor margin (0.21 degC) is
inside same-family scatter.

Evidence for a fix direction (not a ruling), `tau_alt.py`: threshold = baseline + rise/e with `rise` the load-tail
median already computed, crossing time measured from the load phase end:

```
real:               as built argmin Tf2B 24.42 | stable-threshold Tf2B 24.25, Tf18 24.63; excludes only TVH3
recovery_delay:1.0: as built argmin Ts0h 27.63 | stable-threshold Tf2B 24.25, Tf18 24.63; excludes only TVH3
overrun_load:1.3:   as built argmin TV0m 29.15 | stable-threshold Tf2B 22.97, Tf18 23.34; excludes only TVH3
scale:0.85:         as built argmin Tf2B 24.42 | stable-threshold Tf2B 24.25, Tf18 24.63; excludes only TVH3
```

Options for the lead: (1) anchor D1(d)'s reference (and arguably `tau_s` itself) on the stable-threshold crossing;
(2) widen the margin to the 1 degC band floor (a derived number in FINAL-DESIGN) or 3 floors, whichever is larger;
(3) make D1(d) a recorded flag and rely on D1(c) (which misses TVH3 under a 15% lighter step, so (3) alone fails
item (a)). Whatever is chosen, replay it over this capture with `recovery_delay:0.3/1.0` and `overrun_load:1.3` and
write the exclusion counts beside it (doctrine, acceptance-rule requirements). A tau-window reference ("max rise among
qualifiers within 1 s of the minimum tau", `alt_ref.py` rule B) does not help, because the Tf taus themselves move.

### MEDIUM

**M1. Settle set (Erratum 2 D3) excludes 47 of the 138 role-eligible keys on the real idle; idle can end while they drift.**
Implemented as written (noise <= 0.15 degC), but D4 admits fast-role keys up to 1/3 degC, so keys in (0.15, 0.333] are
never waited on. On the real idle at T=300 s (`settle_real.py`): head settle set 138 keys (parent rule 235); every
pick and alternative is in the set (Tf18 noise 0.062, TaLP 0.020, TaRT 0.042, TSXR 0.019, TVS0 0.009, TCMb 0.084,
Tf48 0.067, Tf2B 0.070); the 47 eligible keys outside it (Ts0E, Te0M/T, Tf04/0D/0E/0B, Tp16/17/1I/1J/1E/1F/0a/0b,
Th06, Tp0g/h, Ts0W, Tp0U/V/C/D/K/L/04/05/R/S/m/n, TVsa/ss, TRD*) have noise 0.16-0.33 and are all still drifting at
-0.3 to -1.1 degC/min. On the fake seams (`flicker.py`): a key with noise 0.25 cooling at -1 degC/min until t=330 s
beside a settled key gives `idle 300 s, settled True, settle_keys 1` at head; the parent waited to 384 s. Consequence:
those keys carry `baseline_unsettled` in `rank` (slope computed for every key), which at noise 0.25 is a 1.8-sigma
test (SD(slope) = 0.447 x 0.25 = 0.11 degC/min). None of them is a pick on this capture. Disposition suggestion: flag,
with the doc stating that fast-role keys above 0.15 degC are not waited on and why (slope undecidable at 3 sigma).

### LOW

**L1. Empty settle set ends idle at the 300 s minimum on a single evaluation.** `collect`: `if now >= origin+idle_s and
not slopes: break`. One evaluation second at which no key clears the 0.15 bar (a fan transient lifting all residuals)
ends idle immediately with `settled: null`, where the parent kept waiting. On the real idle the head set never drops
below 36 keys over T=60..300 (`settle_real.py`: min 36), so it does not trigger here; Opus F6 asked for `settled: null`,
not for an early end. Either break only at the cap when the set is empty, or document the single-evaluation end.

**L2. D1(d) exclusions are invisible at the receipt level.** `heat_ordering_reference` and per-key
`heat_ordering_excluded` exist in `rank`, but the receipt prints no count and `summary.md` prints no line. Given H1,
print "D1(d) reference <key>, excluded N keys: ..." in both.

**L3. `CLAMP_DISTINCT = 10` derivation wording.** The comment says ">=10 distinct values makes quantum << noise". The
chain that holds is: 10 or more distinct values over 300 idle reads means the spread covers at least 9 quanta, so
sigma is at least about q, which is the condition under which the 0.40 mode-fraction bound (q/(sigma sqrt(2 pi)) <= 0.40
for sigma >= q) applies. "At least comparable", not "<<". Wording only.

### Verified as written (no finding)

- (a) Lighter step. Parent `scale:0.85` (every key's excursion from its last-60 s idle median scaled by 0.85, all
  phases): `s_fast TVH3` (rise 54.51, max reading below 125). Head: `s_fast Tf18`, TVH3 `record-only ... D1(d): rise
  exceeds Tf2B rise +3 source noise floors`. `out-parent-scale:0.85.txt`, `out-head-sources-scale:0.85.txt`.
- (b) Flicker key. `flicker.py` on the test seams, flicker SD 3 / 5 / 8 degC beside a settled key: parent idle
  1200 s, settled False (all three); head idle 300 s, settled True, settle_keys 1, TGAT absent from
  `baseline_slopes_c_min`. A real cooling key still holds idle to 383 s on both trees.
- (c) +0.75 s load handshake (`shift_load:0.75`: load start_s +0.75, the one read in the gap dropped). Parent:
  `max_interval_ns 2379437417`, receipt `inconclusive ... <=2 s intervals`. Head: cells 0/0/0, receipt `pass`,
  `phase_duration_flags []` (load 899.25 s is within 1 s).
- (d) Single missed read of Tf18. 555 of 898 interior load positions on the real journal have neighbouring midpoints
  more than 2 s apart (`out-tv0m-series.txt`), so on the parent a single miss refused in most positions: at load index 4
  (2.008 s span) parent receipt `inconclusive`; head `phase_max_empty_cells load 1`, coverage 0.99889, receipt `pass`,
  Tf18 kept. At index 450 (1.88 s span) both trees pass.
- (e) +1.3 s load overrun. Parent: `ValueError` -> receipt `inconclusive: SMC r0.json selection unavailable: SMC
  observed phase durations do not match configured adaptive profile`. Head: receipt `pass`,
  `phase_duration_flags [{load, 901.3, +1.3}, {recovery, 598.7, -1.3}]` (but see H1 for the picks).
- (f) SMC inconclusive. Head `runner_inconclusive.py`: `smc inconclusive` -> checks run [smc, host, disk, ...] (disk
  failed only because the scratch path is not a materialized unrestricted directory in this environment; the head
  unittest `test_opus_f3_smc_inconclusive_still_runs_host_disk_and_models` passes with status pass and all checks);
  `smc fail` -> `stopped_after smc`. Parent: the same call stops before any check row (ACCEPTED_OUTCOMES lacked smc).
  `complete_r0` requires `not bad`, and `inconclusive` is accepted for smc, so a live R0 with no picks can be
  `complete_r0 True` with `selection {None, None}`; that is what Erratum 2 asked for (R1 re-selects) and is noted only.
- Real capture through `rank` at head: picks Tf18 (rise 45.68, tau 24.74, noise 0.062) / TaLP (rise 20.54, tau 86.24,
  noise 0.020); reference Tf2B; alternatives design_literal TaRT, opus TSXR, sol TVS0; aliases of picks [] / [];
  readability true; status pass. Rule removals among the 375 degC keys: D1(a) 75, stale 65, D1(b) 18, D1(c) 1 (TVH3),
  D1(d) 1 (TVH3), not resolving/releasable 78, clamp flags 35 (flag only), die 120, heatsink 18. Receipt: `pass`,
  coverage 1.0 / 1.0 / 1.0, errors 0, empty cells 0, `phase_duration_flags []`. Baselines of both picks carry
  `baseline_unsettled True` (slopes -0.64 and -0.68 degC/min), as the decision expects for this unsettled capture.
  Parent on the same capture: identical picks; only per-key differences are TVH3 (adds the D1(d) stamp) and TVA0
  (rise -0.97, loses the D1(b) stamp, Erratum 2 "positive rise only").
- Regressions. Two consecutive empty cells on Tf18 in load (`hole2:Tf18:load:450`): head drops Tf18 (`D6: two
  consecutive empty one-second cells`), picks Tf2B / TaLP, receipt `pass` on Tf2B; parent kept Tf18 and refused at the
  receipt. Two whole samples removed (`drop2:load:450`): head removes all 300 degC keys with data, picks null, receipt
  `inconclusive: selection unresolved`. D1(d) on scaled steps: 0.6, 0.85, 1.2 exclude TVH3 only (at 1.2 TVH3 is
  already invalid above 150 degC, and the exclusion list is empty); Tf18 is kept at all three. At 0.6 the slow pick is
  TVS2 on both parent and head (D5 band-hold property, not a regression).
- Coverage: `Coverage.observe` is now called for failed reads inside the bracket, so the phase grid is fixed by the
  first read and a key's first success cannot move its empty cells; `max_consecutive_empty_cells` counts leading and
  trailing cells within the phase only (head test `test_empty_cell_runs_include_edges_duplicates_and_half_period_ties`).
- Tests: `tests.align.test_smc_classifier_v4 test_thermal_coverage test_r0_host test_smc_selection
  test_r0_documentation test_smc_quiet test_r0_step test_r0_scheduling` at head: 142 tests OK (JW_B5_SYNTHETIC_ONLY=1).

### Number rule (own dimension)

Derived beside the number: `SETTLE_NOISE_C = .15` (3 x 0.447 x 0.15 <= 0.2 degC/min); `< 2` empty cells (U1(c) 2 s
reader window, 99% bar admits one cell); `abs(deviation) > 1` s (one sampling period); `ceil(95,467,641/1800) =
53,038` bytes/slot (measured journal); docs `2,700 x 53,038 = 143,202,600` (checked); D1(d) reference gates `tau <= 60`,
`noise <= 1/3`, `3 x noise_floor` (D4's own numbers); 240 / 300 / 120 s in the Opus alternative (four, five, two slope
windows). Test inputs 0.75 s, 150 ms, 1.3 s, SD 5 (7 sin t) and 0.071 (0.1 sin 1.7t) are scenario shapes with their
derivations in comments. Without a sound derivation: none found; `CLAMP_DISTINCT = 10` has one but the wording
overstates it (L3). Pre-existing numbers not in the diff (`SETTLE_COUNT = 10`, `IDLE_MAX_S = 1200`, the five-sample
minimum) were not re-audited.
