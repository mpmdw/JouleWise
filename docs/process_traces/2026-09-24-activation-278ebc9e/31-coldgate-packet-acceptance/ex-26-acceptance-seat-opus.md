# Opus 5.5: blind council seat, 25G83 instrument acceptance

**Auto-loaded:** `~/.claude/CLAUDE.md`, the worktree `CLAUDE.md` and `MEMORY.md` (truncated). None of them was used as authority. I read the packet 22 files, the documents under context, and the r6/r7 corpus and 25G83 night-custody traces, all read-only. I ran two scripts under `/tmp/278ebc9e/acc-opus/`: `geom.py`, which simulates missed plateaus on real 25G83 frame sequences, and `decim.py`, which merges r6 frames pairwise and refits the pulses with the repo's own `detect_pulses`. I read no other seat's work.

## Reframe: the problem is frame jitter against a 1.0 s pulse, not the 0.245 s average

**Desk result 1 (new).** I took the 17 r6 members, merged consecutive native frames in pairs (energy-weighted, which is exact for interval-average power) and ran `joulewise/powermetrics_fiducial.py:910` `detect_pulses` on them. This gives synthetic intervals of about 0.24 s, the new rate.
- The harness is sound: without merging it reproduces each stored B to within about 1 ms.
- With merging, all 34 decimated captures (2 phases × 17) detect **59/59 pulses**.
- B spans 0.0220–0.0390 s, median about 0.029 s. The stored r6 corpus spans 0.0232–0.0329 s (`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, `derivation_corpus`).
- So halving the sampling rate alone adds about 3–6 ms to B and loses **no** captures.

**Desk result 2 (new).** Real 25G83 frames are not a regular 0.25 s grid. Over the 24 captures: median 0.2485 s, p95 0.274 s, max 0.419 s.
- The detector needs a frame wholly inside the plateau interior. The pulse is `PULSE_DURATION_S = 1.0` (`powermetrics_fiducial.py:63`) and the interior is inset 0.25 s at each end (`:102`), leaving 0.5 s.
- Placing that 0.5 s interior at random on the real frame sequences misses 3.2 % of pulses. That is P(all 59) = 0.15, which overpredicts the observed 11/24 valid, so the estimate is conservative.
- At 1.25 s or 1.5 s pulses the miss rate is **0** over 72,000 placements.
- Time coverage is complete: summed frame durations ÷ span = 1.0000 on every capture. No energy is lost to gaps.

**What 25G83 changed, taken together:**
- (i) Bulk B rose modestly. Nine of 11 valid values are 0.028–0.043 s (n1: `03-diagnostic-invalid-captures-astra.md:2 valid_fields_s`; n2: `01-n2-20260919-harvest-record.md:59-68`). That matches decimated r6 plus 25G83's larger anchor bounds (1.0–4.5 ms vs r6 0.3–2.5 ms).
- (ii) Yield collapsed. Jittered frames against a 0.5 s interior make pulses miss.
- (iii) Two captures carry single-pulse onset excursions: 0.133 s (n2 d11) and 0.173 s (n1 d05). Decimated r6 reproduces **none** in 34 captures. The d05 case is a ramp over three frames (6.4, 33.9, 40.7 W). This is the real unknown: either a 25G83 GPU launch/ramp lag or the estimator mislocating the edge under jitter.

## (a) Recommended path: characterise at the native cadence with a 1.5 s pulse, plus a small targeted diagnostic

This combines options B and C with a slice of A.

**Desk work (agent), from now:**
- **D1.** Commit `decim.py` as a tracked trace. Extend it with a *jittered* replay: resample r6 frames onto 25G83's recorded frame-length sequences.
  - It must reproduce the miss rate. If it does not, stop: the mechanism is wrong.
  - Also inspect the raw frames of the two outlier pulses to classify them (launch lag vs fit artefact). Diagnostic only; nothing is admitted from it.
- **D2.** Protocol `powermetrics_pulse_fiducial_v4`: identical to v3 except a 1.5 s pulse. The 1.0 s interior is at least 2× the largest observed frame (0.419 s).
  - A capture then takes about 59 × 3.5 + 20 ≈ 227 s, inside the 480 s slot budget (prereg `:99-102`).
  - This is a full-tier PR, because `docs/contracts/run_bundle_layout.md:613-616` accepts only v2/v3 evidence for strict reduction.
- **D3.** Registration rev 3 for the epoch {25G83, Mac15,9, ac_high_power, 100 ms, estimator v2, pulse v4}, with the rule changes in (c). It must list, as disclosed design inputs, the prior data it drew on: r6 decimation, the 25G83 frame-length distribution, and the fact that n1/n2 B values have been seen.
- **D4.** Cold gate on D1–D3. Then Ed's **written** V3 acknowledgement (night count, slots, n — required by prereg `:11-13`) and his ruling on dropping the r6 screen challenge.

**Ed hardware/settings:** turn off automatic macOS updates until the end of November. Another build bump restarts all of this. No sudo is needed on the critical path, because the fiducial chain already runs powermetrics.

**Quiet windows:**
- **W1, W2, W3:** 12 slots each, derivation-only, blind (prereg `:179-186` unchanged).
- **Futility stop after W1:** if W1 has fewer than 8 of 12 valid, stop and go to the A243 probe. This uses counts only; the existing dry run already exposes them (`:183-186`) and B values stay unseen.

**Then:** derivation, cold science gate, the D-138 successor transaction, regenerated G2-a bindings with a fresh-clone bind check, and the G2-a arm. The calibration night (council R-Q1/R-Q2) comes second, as ruled (`20-coldgate-fable-council-ruling.md:54`).

**Why not keep v3:** every claim-bearing window needs valid pre **and** post brackets, or it refuses `instrument_calibration_bracket_missing` (`run_bundle_layout.md:630-636`). At 11/24 valid per capture, P(both valid) ≈ 0.21. G2-a and every later window would mostly refuse. So the yield fix is not optional; it decides whether any window is usable.

**The A243 sudo matrix** (`06-consult-instrument-cadence-astra.md:30-50`) is useful but off the critical path. Run it in a spare quiet slot, mainly to test whether a 50 ms request restores about 0.12 s frames.

## (b) Physics: does 0.245 s threaten a claimed quantity?

- **Segment energy (10–600 s).** No. Frames tile time completely (coverage 1.0000), so the integral inside a segment is unchanged. Timing only moves energy across edges, by roughly ΔP × δ per edge.
- **The ~1 J attribution limit** is 33 W × 31 ms (`docs/decision_log.md:4764`). That bound is max(Bpre, Bpost) + max(drift, S) (`calibration_bracketing.py:2572-2579`).

| Case | B (s) | S (s) | Operative bound (s) | ΔP × bound at 33 W |
|---|---|---|---|---|
| r6 reference | 0.033 | 0.0097 | 0.043 | ≈ 1.4 J |
| 25G83 bulk | ≈ 0.04 | ≈ 0.015 (decimated range 0.0170 → S ≈ 0.017) | ≈ 0.055–0.057 | ≈ 1.8–1.9 J |
| Outliers in corpus | ≈ 0.04 | ≈ 0.145 (range) | ≈ 0.19 | ≈ 6 J |
| Outlier as a bracket endpoint | 0.17 | ≈ 0.145 | ≈ 0.32 | ≈ 10 J |

- **The ~5 J claim bar** (`decision_log.md:4809`) becomes about 6–7 J in the bulk case and roughly 20–30 J if the outliers are real. That only hurts **prefill/decode phase-split** claims.
- **Headline quantities** survive either case: J/attempt across thinking budgets (hundreds to thousands of J apart) and P̄(L) over 512-token segments of about 400 J (edge terms under 3 %).
- **Soundness:** coarser sampling widens bounds; it does not bias them. A wrong number enters only if a bound *understates* the error, and the pipeline measures B for every window. The outliers widen S and C conservatively (C = max(prior C, Q99), `prereg:232-243`), so the S ≥ C refusal stays live.

## (c) Barriers: keep, change or drop

| Barrier | Verdict | Reason |
|---|---|---|
| Three distinct calendar days (`:143`) | **Change** to 3 windows, at least 4 h apart, first to last at least 24 h (so at least 2 dates) | Within-window drift, which is what S bounds, is sampled inside every window. Day-scale state (ambient temperature, daemons) mainly sets how often the level screen refuses later windows, which is covered by a 24 h span. A third date adds no physics. |
| Retained n ≥ 19 (`:173-177`) | **Keep** | With yield at 90 % or more, 36 slots give about 32, so it costs nothing. The t(0.995, df) factor and the 1/(n+1) chance a future capture exceeds the corpus maximum are real reasons. Ed's n = 17 escape stays. |
| Screen challenge: ≥ 2 members above r6's 0.0329 s (`:188-191`) | **Drop**; keep r6-plus-range only as a recorded diagnostic | It compares against a 25F84 statistic at the old cadence. In decimated r6, 7/34 captures exceed 0.0329. At that rate, with about 33 members, P(≥ 2 above) ≈ 0.99: it would fire on unchanged physics. |
| New-max level screen and S ≥ C halt (`:245-250`) | **Keep** | Instrument-state gate and budget physics. |
| 12 slots per window | **Keep** | Fits the 150 min window. |
| Equivalence rule | **Drop** for this transition | There is no same-cadence comparator. P(PASS \| no change) = 0.48 at m = 12 (`02-fresh-opus-review-verified.md:69`). Council M1's replacement applies to future same-cadence epoch shifts. |
| Per-window cadence check | **Add**, flag only (no refusal) | Median frame length in each claim window vs the corpus. Cadence is not an additive term in B. |
| Futility stop after W1 | **Add** | See (a). |

**Rules before data:**
- The n1/n2 captures stay non-members. Ed ruled neither counts (`01-ed-ruling-fail-route-c.md:9-14`), and under v4 they belong to a *different* epoch, so the "valid same-epoch capture outside this registration refuses issuance" clash (`prereg:159-161`; packet 05 item 6) goes away.
- Seen data may inform design only, disclosed: frame-length distribution → pulse length; r6 decimation → dropping the screen challenge.
- No B value is ever used to include or exclude anything.

## (d) What would show this path wrong, and how it is detected

1. **D1's jittered replay does not reproduce the misses.** Then the geometry mechanism is wrong. Detected at the desk before any window is spent → run the A243 probe first.
2. **W1 has fewer than 8/12 valid under v4.** Yield is not geometric. The futility stop halts the campaign.
3. **Outliers are frequent** (say 20 % of captures or more, so S ≥ 0.1 s). Phase-split claims lose. Issuance computes S and publishes it. If floor plus claim-side bound exceeds a third of the target effects, D-078's revisit rule (`decision_log.md:4817`) reopens instrument work: an estimator revision or restoring the old rate. The S ≥ C halt fires automatically.
4. **Frames under inference load run much longer than under pulse load.** The per-window cadence flag reports it, and the paper states it.

## (e) Calendar (floors, assuming every gate passes on the first try)

| Step | Earliest |
|---|---|
| D1–D4 desk work | end of 09-25 (the full-tier v4 PR is the long pole) |
| W1 | 09-26, about 01:00 |
| W2 | 09-26 afternoon |
| W3 | 09-27, about 01:00 |
| Derivation, science gate, D-138 transaction | 09-27 |
| **G2-a arm** | 09-27 night, realistically **09-28** |
| **Calibration night** | **09-28** (second window that day) or 09-29; registration, payload, meter import and the 32k desk smoke are built in parallel 09-25 to 09-27 |

If the futility stop fires, add 2–3 days: probe window plus redesign, putting G2-a around 10-01/02. Either way this is well inside the end-of-November horizon.

## (f) What the question misses

- **Bracket yield, not acceptance yield, is the binding constraint.** At 46 % per capture, about four in five windows would refuse (P(both brackets valid) ≈ 0.21).
- **A cadence-proportional systematic bias that is not in the anchor envelope.** `_anchor_shift_envelope` (`joulewise/reduce.py:2064-2140`) treats power as constant within a frame. For a true step at a boundary inside a frame of length Δ, splitting that frame's energy by time share misallocates ΔP · f(1−f) · Δ, with a consistent sign. The mean is ΔP·Δ/6: about 0.66 J per edge at 0.12 s and about 1.35 J at 0.245 s, for 33 W.
  - Whole segments come out under-counted by about ΔP·Δ/3 ≈ 2.7 J.
  - It cancels in matched contrasts but not in absolute phase splits.
  - Verify the reducer's point estimate uses the same allocation, and disclose it in the paper.
- **The outliers may be real GPU launch lag on 25G83.** That affects inference attribution directly and may be a small finding in its own right.
- **OS updates:** the whole campaign can be voided by the next macOS build.
- **Every rule tied to r6 numbers carries the old cadence.** Audit them all, not just the two named here.
