VERDICT: ADMIT_WITH_FIXES

# Opus 5.5 delta executing review: Erratum 4 on PR #692 (eb6e8e493..e3b4bab55)

Scope: `git -C /Users/edr/code/jw-wt/r0-smc-cov diff eb6e8e493..e3b4bab55`, governed by DECISION.md Erratum 4
(with D1-D6 and Errata 1-3). The worktree HEAD is e3b4bab55, and its tracked code matches the head (`git diff --quiet` clean).
The parent tree is a `git archive eb6e8e493` export in `opus/parent/`. Python:
`/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python -B -P`, TMPDIR = scratch.
Every output prints `module.__file__`: head runs resolve to `/Users/edr/code/jw-wt/r0-smc-cov/joulewise/...` and parent runs to
`/Users/edr/night-archive/r0-smc-cov/cold4/opus/parent/joulewise/...`. Tools are copies of the cold3 harnesses in `opus/tools/`,
with the scratch path redirected, plus `probe.py`, `sweep.py`, `rcpt.py`, `holes.py`, `recheck.py`, `cooling.py` and `derived.py`.
All outputs are in `opus/out-*.txt`. Journal sha256 16aa5307…44984, 1,800 rows (checked). The worktree was not modified.

Every Erratum 4 item is implemented as written. All seven original faults reproduce on the parent and are gone at the head.
Eleven replay-table rows were re-run, and all match the doc. D6-admitted perturbations do not move the D1(d) reference off the Tf
family. The regressions checked are clean. Two findings need a small fix or a recorded decision: M1, an unbounded and unflagged
recovery-onset gap, and L1, an amplified alias inside the tie window. Neither occurs on the real capture, so neither blocks the R0 run.

## 1. Original faults: parent vs head (executed)

Files: `out-faults.txt`, `out-faults-head2.txt`, `out-opus-overrun16.txt`, `out-d3-f.txt`, `out-f-parent.txt`.

| Case | eb6e8e493 | e3b4bab55 |
|---|---|---|
| `recovery_delay:1.0` | fast Ts0h, reference Ts0h; D1(d) excludes the whole Tf family plus TCDX, TCMz and others (20 keys); receipt **pass** | Tf18 / TaLP, reference Tf18 (45.676), excluded [TVH3]; receipt pass |
| `overrun_load:1.3` (Fable) | fast TV0m; 130 keys excluded; receipt **pass** | Tf18 / TMVR, reference Tf18, excluded [TVH3]; receipt pass with load +1.3 and recovery -1.3 flags |
| `miss1:Tf2B:recovery:0` | fast Tf1B, reference Tf24; excludes Tf18 and Tf2B; receipt **pass** | Tf18 / TaLP, excluded [TVH3]; receipt pass |
| `hole2:Tf2B:load:236` | fast Tf1B, reference Tf24; excludes Tf18 (Tf2B lost to D6); receipt **pass** | Tf18 / TaLP; Tf2B loses its role to D6; excluded [TVH3]; receipt pass |
| d3 `quiet:0.05` (20 Gaussian keys, sigma 0.05) | `settle_keys: 0`, `settled: None` | `settle_keys: 20`, `settled: True`, idle 300 s |
| live-desk smc `inconclusive` (f.py) | `complete_r0 True` | `complete_r0 False`; checks still run; `smc_selection_missing` recorded |
| h.py `overrun:load:1.6` (Opus) | receipt **inconclusive**: 300 keys fail D6 with `load: 2` empty cells | receipt pass, Tf18 / TaLP, load empty cells 0, `phase_seconds.load` 900, flag +1.6 |

For each item, the code matches Erratum 4:
- **Stable crossing.** The threshold is `baseline + rise/e`, using the load-tail rise, timed from `phases["load"]["end_s"]` (the actual end).
- **Reference.** The largest rise among Erratum 3 qualifiers whose stable time is within `REFERENCE_TIE_S = 1.0` of the shortest. The `HEAT_ORDER_MARGIN_C = 1.0` margin is used.
- **Class tau.** Unchanged, and printed beside the stable time.
- **Receipt and summary.** Both print the reference, its rise and the excluded keys.
- **Settle set.** The half-range term is gone. An empty set needs 10 consecutive evaluations.
- **complete_r0.** Requires smc `pass`.
- **Cell grid.** Ends at `min(deadline_s, end_s)`. Adaptive idle records its deciding evaluation. Legacy receipts reconstruct fixed deadlines from the profile.
- **Docs.** The runbook D1(d) text and the CLAMP comment are updated.

Touched test modules at head: 127 tests OK (`out-tests-head.txt`).

## 2. Replay table (docs/align/smc_temperature.md): re-run, all match

Files: `out-table-receipts.txt`, `out-sweep1.txt`, `out-faults*.txt`. These rows went through the real receipt:

| Case | Mine | Doc |
|---|---|---|
| real | Tf18 / TaLP, 45.6756 → 45.68, [TVH3], pass | same |
| recovery_delay:0.3 | Tf18 / TaLP, 45.68, [TVH3], pass | same |
| recovery_delay:1.0 | Tf18 / TaLP, 45.68, [TVH3], pass | same |
| overrun_load:1.3 | Tf18 / TMVR, 45.670000076 → 45.67, [TVH3], pass | same |
| overrun_load:1.6 | Tf18 / TMVR, 45.67, [TVH3], pass | same |
| scale:0.6 | Tf18 / TVS2, 27.405 → 27.41, [TVH3], pass | same |
| scale:1.2 | Tf18 / TaLP, 54.81, [] (TVH3 `above_junction`, stable None), pass | same |
| miss1:Tf2B:recovery:0 | Tf18 / TaLP, 45.68, [TVH3], pass | same |
| hole2:Tf2B:load:236 | Tf18 / TaLP, 45.68, [TVH3], pass | same |
| opus overrun_load:1.6 | Tf18 / TaLP, pass | same |

scale:0.85 was checked through rank only: Tf18 / TaLP, 38.824, [TVH3], which matches.

Note on the rank-only path: without `deadline_s`, the overrun rows give 45.6647, which rounds to 45.66. The receipt gives 45.67,
because post-deadline relabelled reads leave the tail. The doc's numbers are the receipt's, as the doc says.

The comment's stable times also reproduce: Tf2B 24.2481 s and Tf18 24.6317 s, a separation of 0.384 s.

## 3. Attacks on the new D1(d)

### Admitted perturbations: robust (`out-sweep1.txt`)

Reference Tf18 holds and D1(d) excludes only TVH3 in every one of these cases:
- scale 0.5, 0.6, 0.7, 0.85, 1.2 and 1.3 (at 1.2 and 1.3 TVH3 is already record-only by D1(c) and coverage);
- recovery_delay 0.3, 0.5, 2, 5 and 10 s;
- overrun_load 0.5, 1.0, 1.3, 1.6 and 3 s;
- single missed reads of Tf18 at recovery 0, 23 and 24 (the reads around its crossing) and at load 899, and of Tf2B at recovery 23;
- combinations: scale 0.85 + Tf18 miss at recovery 0 + delay 1.0; scale 0.5 + overrun 1.3; scale 1.3 + delay 1.0.

The stable time moves exactly with the overrun: 24.63 → 24.14 → 23.64 → 21.65 for +0.5, +1.0 and +3 s. That is correct, because
the origin is the actual load end.

TVH3 has no route back through admitted perturbations. Its stable time is 33.4 s, 8.8 s outside the tie window. Its rise exceeds
reference + 1.0 degC at every scale tested; for example, at 0.5 it is 32.07 against a limit of 23.84.

Real capture (`out-allrows-real.txt`): none of the 118 D4 sources lacks a stable crossing. The only stable times under 15 s belong
to Ts1P, TH0a, TH0x and TH0b. Their rises are 0.19-0.56 degC, so they are not resolving and none of them is a source.

### M1 (medium): an unbounded, unflagged recovery-onset gap degrades D1(d) silently, and the receipt still passes

Erratum 4 says neither the threshold nor the origin depends on when the first recovery read lands. That holds only while the
first recovery read lands before the fast keys cross, about 23-25 s after load end. Beyond that, two things happen:
- the class tau (still timed from the first read) of every Tf key exceeds 60 s, so the Tf family drops out of the Erratum 3 source set;
- a key whose stable crossing precedes the first read gets a censored "crossing" equal to the first read's time. `_crossing` returns `t` at index 0.

Executed (`out-sweep1.txt`, `out-gap-receipt.txt`):

| Recovery-onset delay | Result |
|---|---|
| 20 s | fast Tf2B (a sibling; acceptable) |
| 23-27 s | reference TCDX or TVV0 (43.04-43.08 degC); D1(d) excludes the whole Tf family (12 keys); fast **TVV0**, a virtual key that DECISION.md defers as non-independent; receipt **pass** |
| 30-35 s | reference TV0s or TVHC; 38-57 keys excluded |
| scale 0.85 or 0.7, delay 34 or 40 s | **TVH3 is the reference and the fast pick** (class die, stable 34.25 s = the censored first-read time); nothing excluded; receipt **pass** |

Nothing bounds or records this gap:
- The receipt checks only `begin >= previous`.
- In a real `collect`, recovery runs its full 600 s from its own start, so no duration flag fires. The harness's shortened recovery is the only reason a flag appears above.

Plausibility: the gap is 0.17 s on the real capture. The code permits up to about 10 s from `GpuLoad.stop()` (a 5 s SIGTERM wait,
then a 5 s SIGKILL wait), plus a successful quiet census whose subprocess probes each have 5 s timeouts. The head is robust to 10 s
and breaks at about 23 s. The margin is about 2x over a pathological stop, and the failure is silent.

Fix (cheap, a flag rather than a refusal):
1. Record `recovery_onset_gap_s`: the first in-grid recovery read minus `load.end_s`.
2. Mark each row whose stable crossing is at recovery index 0 as `reference_crossing_censored`.
3. If any Erratum 3 qualifier is censored, or the gap exceeds the fastest qualifier's stable time, set `heat_ordering_indeterminate: true` and print it in the receipt and summary. Whether that makes the receipt inconclusive is the lead's call: the sampler missed the cooling onset, which is an "instrument not sampling" physical loss. The derivation needs no new number, because "crossing bracketed by two valid reads" is the 1 Hz resolution already used for `REFERENCE_TIE_S`.

### L1 (low, design-level, implemented as written): an amplified alias of any key in the 1 s tie window wins the reference

The tie rule takes the largest rise among keys within 1 s of the shortest stable time. A firmware-derived amplified copy has the
same form as TVH3 = 1.72 x TCMb - 38. Such a copy, built from any tied key, shares that key's crossing time and has the larger rise,
so it becomes the reference and D1(d) cannot exclude it.

Executed on the real journal with a synthetic key TDRV inserted (`derived.py`, `out-derived*.txt`):

| TDRV | Head | Parent |
|---|---|---|
| 1.3 x Tf18 - 12 (max 111.8 degC, under D1(c)) | fast pick TDRV, reference TDRV (59.38) | reference Tf2B (argmin tau); TDRV excluded by D1(d) |
| 1.72 x Tf18 - 38 at scale 0.85 | TDRV picked | not run |
| 1.1 x Tf2B - 4 | TDRV picked | not run |

So the widening from argmin tau to the 1 s window grows the set of keys whose amplified alias defeats D1(d), from one key to the
five tied Tf keys. The parent was equally blind to an alias of the single argmin key, because it broke ties lexically.

No such key exists on this capture: TVH3 derives from TCMb, which is 4.1 s outside the window. This belongs with the deferred R1
alias and virtual-key work. One cheap R0 diagnostic would be to print, for the pick, any key that is a linear function of it with
R^2 near 1 and gain above 1.

### Degenerate or undefined stable time

- **A qualifier that never crosses** is removed from the sources (`reference_cooling_s is not None`). If no source crosses, `heat_ordering_reference` is None and D1(d) is silently off; only the printed None shows it. For a D4 key (class tau ≤ 60 s, peak ≤ rise) this cannot happen in a 600 s recovery: the class threshold baseline + peak/e lies at or below the stable threshold whenever the first recovery read is at or below the load-tail median, so the class crossing implies the stable one. No real source lacked a crossing.
- **The censored index-0 case** is M1.

### L2 (low, informational): the slow pick is sensitive to sub-2 s onset timing

The D5 class tau is still timed from the first recovery read, as Erratum 4 says. As a result the slow pick flips TaLP → TMVR at
recovery_delay 2, 5 and 10 s, and at overrun 1.3, 1.6 and 3 s. The doc's table shows only the overrun cases. The lead should know
this when D5 is chosen on the first settled capture.

## 4. Regressions against eb6e8e493: none found

**Holes still remove a pick** (`out-holes.txt`, through the receipt).
- `hole2:Tf18` at load 0, load 450, load 898 (the last two cells before the deadline), recovery 598 and idle 298 each move the fast pick to Tf2B, and the receipt passes on clean rows.
- The deadline grid does not hide end-of-phase holes.
- `overrun_load:1.3` + `hole2:Tf18:load:898` still removes Tf18.
- A single miss (`miss1:Tf18:load:899`) is admitted, with empty cells = 1.

**The receipt still refuses genuine holes.**
- `drop2` at load 450, load 898 and recovery 598 (every key holed) gives `inconclusive`, "selection unresolved".
- The receipt's own re-check (`recheck.py`), forced onto the selected row, refuses each of: `phase_max_empty_cells` 2, coverage 0.985 and read errors 0.01. Each gives `inconclusive` with the coverage reason.

**Adaptive idle still waits on cooling keys** (`cooling.py`, `out-cooling.txt`). The cooling key is 48 + A·exp(-t/300); analytically its slope falls below 0.2 degC/min at t = 300·ln(A/5).

| Case | Parent | Head | Analytic |
|---|---|---|---|
| A = 10, noiseless | 731 s | 731 s | 690.8 s, plus the 30 s lag of the trailing-window centre and 10 confirmations |
| A = 10, sigma 0.05 | 714 s | 714 s | |
| A = 40, sigma 0.05 | 1,161 s | 1,161 s | 1,106.7 s |

At the head the stationary TFLAT key now joins the set (the M2 fix), and a 6 degC flicker key stays out.

**Real idle replay** (d3 `real`): settles at 364 s, with 235 keys at the head against 218 at the parent.

**Tests**
- Every `tests/align/test_smc*` and `test_r0*` module at head: 239 run, 1 error. The error is `test_r0_mlx` `test_constructor_builds_valid_config…` (`object.__new__()`).
- It is an order dependence on `test_r0_checks`: the pair fails, each passes alone, and `test_r0_scheduling` + `test_r0_mlx` passes.
- Neither file, nor `r0_mlx.py`, is in this delta. It predates the delta, is out of scope, and goes to CI.

## 5. Number rule

| Number | Derivation | Check |
|---|---|---|
| `REFERENCE_TIE_S = 1.0` | the 1 Hz crossing resolution | Measured separation of the two closest leaders: 0.384 s |
| `HEAT_ORDER_MARGIN_C = 1.0` | the 1 degC band floor | Covers the measured inter-sensor spread: Tf18 45.676, Tf2B 45.627, Tf1B 45.365, Tf24 45.271, Tf14 45.222, a spread of 0.454 degC. Headroom to TVH3 is 17.4 degC at scale 1 and 8.2 degC at scale 0.5 |
| Phase-length flag of 1 s | one period | — |
| Settle bars | G0's 0.2 degC/min and count of 10; noise bar 0.15 = the D5 3-sigma derivation | — |

The replay-table cells carry their derivation in the HTML comment. In tests:
- the `delta=1` on `reference_cooling_s` is one sampling period;
- the `-1.3` equality is arithmetic identity on shifted input.

No silly numbers found.

Two doc and comment derivations are slightly off; the conclusions stand. Simulated with 400 draws each:

| Claim | Simulated |
|---|---|
| "largest jump about 4.9 sigma, exceeding half its approximately 5.5 sigma range" (smc_temperature.md) | n = 300: jump 4.36 sigma, range 5.77 sigma. n = 1,200: jump 4.88 sigma, range 6.57 sigma |
| CLAMP comment: "about 300 reads span ~5 sigma, so sigma ≥ about 1.8q, mode fraction ≤ 0.22" | 300 reads span about 5.8 sigma; adaptive idle reaches 1,200 reads, about 6.6 sigma. That gives sigma ≥ 1.55q or 1.38q, and mode fraction ≤ 0.26 or 0.29, still under the 0.40 bar |

The first claim mixes two sample sizes, but P(jump ≤ half range) = 0.000 at n ≥ 300, so the conclusion holds. The second only
needs the stated numbers corrected (nit).

## Fixes requested

1. **M1.** Record `recovery_onset_gap_s`, mark censored (index-0) stable crossings, and set and print `heat_ordering_indeterminate` when an Erratum 3 qualifier's crossing is censored. The lead decides flag or inconclusive.
2. **L1.** Record in the R1 hand-forward that the 1 s tie window lets an amplified alias of any tied key become the reference. Optionally print a linear-alias diagnostic for the picks in R0.
3. **Nits.** Correct the sigma figures in the settle-set and CLAMP derivations, and add a recovery_delay ≥ 2 s row, or a sentence, for the slow-pick flip.
