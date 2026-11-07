VERDICT: ADMIT_WITH_FIXES

# Cold3 executing delta review (Opus 5.5): PR #692, c0c460fd9..eb6e8e493

Scope: `git -C /Users/edr/code/jw-wt/r0-smc-cov diff c0c460fd9..eb6e8e493` (695574428 Erratum 2, eb6e8e493 Erratum 3),
checked against DECISION.md D1-D6 and Errata 1-3. Worktree clean at eb6e8e493. Parent tree extracted with
`git archive c0c460fd9` into `opus/parent/` (no worktree mutation).

Interpreter: `.../align-pilot2/.venv/bin/python -B -P`, PYTHONPATH = worktree (head) or `opus/parent` (parent).
Every run prints `module: .../smc_enumeration.py` (or `r0_runner.py`) as the first line. The head runs printed
`/Users/edr/code/jw-wt/r0-smc-cov/joulewise/...` and the parent runs printed `.../cold3/opus/parent/joulewise/...`.

Harnesses, all in `/Users/edr/night-archive/r0-smc-cov/cold3/opus/`:
- `h.py OUT TRANSFORM...` loads the real capture (`/Users/edr/night-align/r0-v4-20261107T0810Z/smc`) and applies the transforms:
  - `scale:F`: every degC key's excursion from its last-60 s idle median, multiplied by F;
  - `shift:S`: S seconds inserted at the idle-to-load handshake;
  - `miss:KEY:PHASE:I`: one failed read of KEY in sample I of PHASE;
  - `overrun:PHASE:S`: the phase end extended by S seconds with no reads.

  It then rewrites r0.json/samples.jsonl with a fresh SHA, and runs the real `r0_host.smc_enumeration` receipt with `subprocess.run` patched to exit 0. The receipt calls `rank`.
- `d3.py MODE idle_s idle_max` drives the real `collect()` adaptive idle with `tests.hazards.fakes.FakeClocks`.
- `f.py` runs `r0_runner.execute` with `smc_enumeration` patched.

Touched test modules at head: `python -m unittest tests.align.test_smc_classifier_v4 test_smc_quiet test_smc_selection
test_r0_host test_r0_scheduling test_r0_step test_thermal_coverage test_r0_documentation` gives `Ran 142 tests ... OK`.

## 1. Erratum 2/3 items: original fault on c0c460fd9, gone at eb6e8e493

All six faults reproduce on the parent and are gone at the head.

| Item | Command | Parent c0c460fd9 | Head eb6e8e493 |
|---|---|---|---|
| (a) 0.85 x step | `h.py scale:0.85` | `selection: {'s_fast': 'TVH3', ...}` (status pass) | `s_fast Tf18, s_slow TaLP, ref Tf2B`; `D1(d) removed: [('TVH3', 54.51)]` |
| (b) flicker key | `d3.py rand:3 300 1200`, `rand:8`, `flicker` (7 sin t, SD about 5) | `actual_seconds 1200.0, settled False` (all three) | `actual_seconds 300.0, settled True, settle_keys 1`, TGAT not in set |
| (c) +0.75 s handshake | `h.py shift:0.75` | `inconclusive ... <=2 s intervals`, `maxint=2021162167` | `pass`, empty cells `{idle 0, load 0, recovery 0}` |
| (d) one missed fast-pick read | `h.py miss:Tf18:load:236` (the widest neighbour span, 2.149 s) | `inconclusive`, `maxint=2149301375` | `pass`, Tf18 kept, `load: 1` empty cell |
| (e) +1.3 s phase overrun | `h.py overrun:load:1.3` | `inconclusive \| ... phase durations do not match configured adaptive profile` | `pass`; `phase_duration_flags: [{'phase': 'load', 'actual_seconds': 901.3, 'deviation_seconds': 1.2999...}]` |
| (f) SMC inconclusive | `f.py` | `stopped_after {'check': 'smc', 'outcome': 'inconclusive'} checks ['smc']` | all 13 checks run; `fail` still stops after smc |

Other Erratum 2/3 items, checked in code and output:
- **D1(b) reason.** It is stamped only when `rise > 0`. The D1(b) count went 19 → 18 on the real capture.
- **`design_literal` label.** It now says the band-hold cap applies.
- **`CLAMP_DISTINCT`.** It has a derivation (see N2).
- **The `>=600 s` bar.** It is removed.
- **Journal estimate.** It is now `ceil(95,467,641/1,800) = 53,038` bytes per slot, so 2,700 x 53,038 = 143,202,600 bytes. I checked the measured file: it is 95,467,641 bytes (`ls -la`).
- **Aliases.** The picks print theirs: `{'Tf18': [], 'TaLP': []}`.
- **Empty settle set.** It records `settle_keys 0, settled None` (seat test, and see M2).
- **Erratum 3 reference.** It is D4-qualified: resolving, D1(c) passed, tau ≤ 60 s, noise ≤ 1/3 degC, not clamped.

## 2. Real capture through `rank` and the r0_host receipt (head)

`h.py out/head-none none`:
```
receipt.status: pass | WP14(a) model-free classifier and readability bars met; picks PROVISIONAL
phase_duration_flags: []
selection: {'s_fast': 'Tf18', 's_slow': 'TaLP'} ref: Tf2B
alt: {"design_literal": "TaRT", "opus": "TSXR", "sol": "TVS0"}
aliases: {'Tf18': [], 'TaLP': []}
reasons: {'D1(a) <10 degC': 75, 'constant/stale idle': 65, 'not a temperature unit': 28, 'D1(b)': 18,
          'D1(c) >125 degC': 1, 'not in a resolving/releasable D4/D5 role': 78, die: 120, heatsink: 18}
D1(d) removed: [('TVH3', 64.13)]     # TVH3 is also D1(c)
Tf18 / TaLP: phase_coverage 1.0/1.0/1.0, phase_max_empty_cells 0/0/0, read errors 0, baseline_unsettled True
```
The parent gives the same picks and alternatives. Both picks carry `baseline_unsettled` (slopes -0.64 and -0.68
degC/min): this capture's idle was still cooling after the model load, as DECISION.md says.

## 3. Regressions

Tested and holding:
- **A genuine hole still removes a pick.**
  - `miss:Tf18:load:236 miss:Tf18:load:237`: Tf18 reports `D6: two consecutive empty one-second cells`, and the fast pick becomes Tf2B.
  - The same at the end of the recovery phase (indices 598, 599).
  - `miss:TaLP:recovery:100,101`: the slow pick becomes TMVR.
  - Receipt pass in all three cases.
- **The settle set on real cooling data does not end idle early.**
  - `d3.py real 300 300` and `d3.py real 60 300` (minimum idle cut to 60 s): `settled False, settle_keys 138`.
  - Tf18, TaLP, Tf2B, TSXR, TaRT and TCMb are all in the set, at slopes -0.13 to -0.76 degC/min.
- **D1(d) under uniform scaling.**
  - 0.6: removes only TVH3; picks Tf18 / TVS2.
  - 0.85: removes only TVH3; picks Tf18 / TaLP.
  - 1.2: removes nothing; TVH3 fails coverage because it reads above the 150 degC valid_value bound; picks Tf18 / TaLP.
  - Uniform scaling cannot flip D1(d) between Tf18 and Tf2B. The margin is 0.157·F degC.

Findings, by severity:

### M1 (medium): D1(d) removes real GPU thermometers when a single admitted read moves the reference
- **Margin.** On the real capture, the reference is Tf2B (tau 24.42 s) and the limit is 45.627 + 3 x 0.070 = 45.837 degC.
  Tf18 rises 45.68, so its margin is 0.157 degC.
- **Reference choice.** Eight Tf GPU keys have taus within 24.42-25.56 s, so the reference is decided by a 0.16 s difference between linearly interpolated 1 Hz crossings.
  - Sources by tau: `Tf2B 24.42 (45.63), Tf24/Tf2D/Tf2E 24.58 (45.27), Tf18 24.74 (45.68), Tf1B 25.39 (45.36)`.
- **Spread.** Rise varies by 0.46 degC across these co-located keys. That is larger than 3 noise floors (0.15-0.21 degC).
- **Perturbations that D6 admits:**
  ```
  h.py miss:Tf2B:recovery:0
  selection: {'s_fast': 'Tf1B', ...} ref: Tf24
  D1(d) removed: [('TVH3', 64.13), ('Tf18', 45.68), ('Tf2B', 45.63)]
  h.py miss:Tf2B:load:236 miss:Tf2B:load:237     # Tf2B loses D6, reference moves
  selection: {'s_fast': 'Tf1B', ...} ref: Tf24
  D1(d) removed: [('TVH3', 64.13), ('Tf18', 45.68)]
  ```
- **What fails.** Brief item 3 says D1(d) must not remove a real responding key. These runs remove Tf18 and Tf2B. The fast pick stays a real GPU key and the receipt passes, so no refusal and no wrong-class pick on this capture, but the rule is not doing what its derivation claims.
- **Number rule.** The "3 noise floors = D4's resolution margin" derivation measures the wrong quantity. The question is whether two different sensors' rises are comparable, and that is limited by gain/offset spread between sensors, not by one sensor's noise.
- **Suggested fix (needs a lead ruling, since it changes Erratum 2's rule).** Take the reference rise as the largest rise among D4-qualified keys whose tau is within one sample period (1 s, the crossing resolution) of the shortest.
  - On this capture that set is Tf2B, Tf24/2D/2E, Tf18 and Tf1B, which gives a reference rise of 45.68 and a limit of about 45.89.
  - TVH3 (64.1, or 54.5 at 0.85x) is still removed, and no Tf key is.
  - Replay the two perturbations above.
- **Related, pre-existing.** A missed first recovery read moves tau a lot because the peak reference moves (`miss:Tf18:recovery:0` gives Tf18 tau 24.7 → 30.8 s). Tau now chooses the D1(d) reference, so this sensitivity matters more than before.

### M2 (medium): the idle "D1(b) on idle so far" term empties the settle set on a quiet machine
- **The rule.** The settle-set rule excludes a key whose largest 1 s idle jump exceeds half its cumulative idle range.
- **Why it fails.** For stationary noise σ over 300 samples, the range is about 5.5σ and the largest consecutive jump is about 4.9σ, which exceeds the half-range of about 2.75σ. So every settled key is excluded.
- **Executed (20 keys, Gaussian):**
  ```
  d3.py quiet:0.05 300 1200           parent: settled True, set 20  | head: settled None, settle_keys 0
  d3.py quiet:0.1:0.00390625 (sp78)   parent: settled True, set 20  | head: settled None, settle_keys 0
  d3.py quiet:0.05:0.25 (fpe2)        parent: settled True          | head: settled True, settle_keys 14
  ```
- **Consequence.** On the state D3 is trying to reach, a settled machine (and the SMC step now runs first), the record reads "indeterminate" instead of True. That also blinds the D3 cost measurement the next R0 run is meant to make. Idle length and picks are unaffected, and rank's per-key `baseline_unsettled` stays correct.
- **Why the seat's tests miss it.** The fixtures are smooth sinusoids (`.03 sin(t/5)`). The seat's own test `test_settle_set_checks_idle_half_range_even_below_noise_limit` asserts this exclusion for a stationary SD 0.071 key, which the D5 derivation counts as decidable.
- **What D1(b) protects against.** The noise bar ≤ 0.15 degC alone already removes the 3-8 degC flicker keys: `rand:3` and `rand:8` both have noise above 0.15.
- **Suggested fix (needs a lead ruling, since this deviates from Erratum 2's literal text).** Drop the half-range term from the settle set, or apply it only when the idle range exceeds a noise-derived floor.

### L1 (low-medium): SMC `inconclusive` now also counts as a passing R0
`ACCEPTED_OUTCOMES["smc"] = {"pass","inconclusive"}` feeds both fail-fast and the final `bad` list:
```
f.py (head), backend labelled live_desk, smc inconclusive:  status pass complete_r0 True live_desk
```
Erratum 2 asks only that the other checks still run. A live R0 with no SMC picks now prints
"Complete R0: True". Fix: keep the fail-fast exemption, but leave SMC out of `complete_r0` unless it is `pass`
(or record `smc_selection_missing`). The seat's test asserts `status == 'pass'` here.

### L2 (low): an overrun of 1.5 s or more still turns into an inconclusive SMC through D6
The loop takes no reads after the deadline, so the overrun seconds become trailing empty cells in every key:
```
h.py overrun:load:1.6      -> 'D6: two consecutive empty one-second cells in a phase': 300 ; selection unresolved; inconclusive
h.py overrun:recovery:1.6  -> same
```
So the "flag, not refusal" rule holds only below about 1.5 s. The bar is set by the half-period snap of the end edge.
Reaching 1.5 s needs a post-read census of 2.4 s or more: the measured census is 70-330 ms and the real overrun was 0 s, so
this is unlikely. Fix: count cells only up to the configured deadline (for adaptive idle, the evaluation that ended it). Exit overrun is outside the reader's grid, like the handshake.

### L3 (low): the settle set ignores decidably drifting noisy keys (as Erratum 2 wrote it)
- **What is excluded.** At t = 300 s on the real idle, 47 of 138 role candidates are outside the set:
  - fast-role keys with noise 0.15-1/3 degC, such as Tp0a (slope -1.07 degC/min, noise 0.30, which is 8 SD(slope));
  - TVsa/TVss (noise 0.066, slope -0.35), excluded for the whole idle by one 7 degC firmware jump at idle sample 4. The jump maximum is cumulative and never forgets.
- **Effect.** None on this capture, because the picks are in the set, and rank flags `baseline_unsettled` per key.
- **Option.** Count a noisy key as unsettled when |slope| > 0.2 + 3 x 0.447 x noise.

### L4 (info): the per-phase hole rule admits a real gap of about 2.3 s across the handshake
`miss:Tf18:idle:-1 miss:Tf18:load:0` gives `{idle 1, load 1}` and Tf18 is kept. This is the behaviour Erratum 2 specified; I record it only.

### L5 (low, docs): one runbook line is stale against Erratum 3
`docs/align/r0_desk_runbook.md:153` says the D1(d) reference is the "fastest resolving D1(a)–(c) key". Erratum 3 makes it
D4-qualified (tau ≤ 60, noise ≤ 1/3, unclamped). The code, RULE and smc_temperature.md are correct.

## 4. Number rule

- **Derived and correct.**
  - `SETTLE_NOISE_C = .15`: 3 x 0.447 x 0.15 ≈ 0.2.
  - Deviation > 1 s: one 1 Hz period.
  - `>= 2` empty cells: U1(c)'s 2 s window.
  - 53,038 bytes per slot: measured.
  - The 240/300/120 s windows of Opus V4/V6: 4 and 5 slope windows, and 2 slope windows.
  - `rise > 0` for D1(b).
  - The idle half-range term: derived as written, but see M2.
- **N1 (flag).** The D1(d) margin of 3 noise floors is borrowed from D4 and is the wrong quantity for comparing two sensors (M1).
- **N2 (nit).** `CLAMP_DISTINCT = 10` says "quantum << noise". For stationary noise, 10 or more distinct values in about 300 samples means σ ≳ 1.8q, not σ >> q. That still puts the non-clamp mode fraction at ≤ 0.22, against the 0.40 bar, so the number holds; reword the comment.
- **N3 (flag, follows from L2).** The effective overrun bar is about 1.5 s, set by grid snapping, while the documented flag bar is 1 s. The two disagree.

No other new number lacks a derivation.

## Disposition summary

Every Erratum 2/3 fault is fixed and reproduced. The real capture gives Tf18 / TaLP, receipt pass, and D1(d) removes only TVH3.
Admit after:
- M1, a ruling on the D1(d) reference rise or margin;
- M2, a ruling on dropping the idle half-range term;
- L1 (one line).

L2, L3 and L5 can ride along or be deferred to the R1 lane.
