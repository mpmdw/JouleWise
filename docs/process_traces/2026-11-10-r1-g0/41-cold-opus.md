# Cold pass (Opus 5.5, blind): R1 G0 operating-point reference / S6 band / 1,200 s cap

Branch `lane/2026-11-10-r1-g0-rop`, worktree `/Users/edr/code/jw-wt/r1-g0-cold-opus`
at `ad9c0667f`, diffed against `20e9edbc4`. I formed this view before reading
`31-build-report.md`. Read-only: no edits, no git writes, no measurement. The
scratch scripts are in `/tmp/mag-5515/cold-opus/` (`replay_opus.py`, `tails.py`,
`hotstart.py`, `chain.py`, `chain2.py`, `worst.py`).

## Verdict: ADMIT

No defect changes a number on the R1 path. Every item in the brief was
executed and behaves as the ruling (sections 1, 3, 7) and the lead fix
specify. Four flags follow. None of them refuses the branch. Flag 1 is a
one-line doc fix that should land with the merge.

## What I executed

**1. Replay of the real 11-10 step-30b journal** (read only). I wrote my own
harness rather than reuse `scripts/replay_r1_g0.py`. It drives the production
`thermal.Sidecar.tick`, `ThermalSession.capture_reference` and
`ThermalSession.wait` on a `FakeClock`. Ticks stay on the session's own 1 Hz
grid. At each tick the reader returns the latest recorded reading and its
recorded status.
- Old parameters (soak R 25.489 / 34.011 °C, δ_slow 1.0, cap 600 s):
  **timeout at 600.0 s**. The exit Tf08 is 28.406876 °C, identical to the
  recorded release value. This reproduces the recorded outcome.
- New parameters: the capture at warmup entry gives **R_op Tf08
  26.571250 °C, TV0h 34.106462 °C**. The ruling says about 26.571 °C. There is
  **no release** through the 651 s of record after G0 entry. After the record
  ends, the gate goes unobserved, as it should when data are missing.

**2. Synthetic continuation** (from G0 + 600 s; R_op, 1.5 °C, 1,200 s). Fits
cover 60–600 s after warmup end. Own idle is Tf08 26.5486 °C (median of the
60 s ending 10 s before warmup).

| Model | Fit (slow) | Release after G0 entry | Excess over own idle at release |
|---|---|---|---|
| B: level = own idle, τ 70/500 s | rmse 0.0765 °C | 706 s (no noise); 725–746 s (σ 0.078 °C noise, 5 seeds) | +1.49 (no noise); +1.26 to +1.50 (noise) |
| D: level free, τ 70/956 s | rmse 0.0822 °C, level 23.96 °C | 940 s (no noise); 734–868 s (noise) | +0.46 (no noise); +0.75 to +1.22 (noise) |

Every release falls inside 1,200 s. Model B's excess is the predicted
+1.5 °C. Model D's is lower, as the ruling's own table says (+0.56). My D time
without noise is 940 s against the ruling's 911 s. The difference comes from
τ1 being held at 70 s instead of searched, and both values are inside the cap.

As cross-checks, R_op at 2.0 °C releases at 592 s, matching the ruling's 592 s.
R_op at 1.0 °C releases at 905–940 s. The soak reference at 1.5 °C times out
under model B.

**3. Hot-start test** (R0 `r0-v4-20261108T0550Z`, `smc/samples.jsonl`). G0 is
entered at load end with reference = own idle (Tf08 26.369 °C, matching the
ruling), fast band 1.0 °C, slow band 1.5 °C and cap 1,200 s. Status is
synthetic Nominal, which is the most permissive setting. The first 600 s are
the record. After that, the continuation is fitted to 300–600 s with τ = 743,
824 or 956 s. **Timeout at 1,200 s in all three cases**, with exit excess
+2.50, +2.77 and +3.14 °C. The slope bar is nearly met at the cap
(−0.204 to −0.210 °C/min), so the band is what refuses. The result is the same
at 2.0 °C.

**4. Synthetic R1 chain** through the real runtime (`rt.main`, synthetic
backend, separate kinds in run order):
- A `g0-release-soak` before step-30b uses `r1_soak_reference` with cap 600 s.
- step-30b captures R_op. Its own G0 reference equals R_op exactly, with
  `source_member r1_step_30b_pre_warmup`. Its policy cap is 1,200 s, and
  `deadline_origin` is `R1_after_G0_release_and_quiet`.
- A `g0-release-soak` after step-30b uses R_op and keeps cap 600 s.
- The three A-B-A legs and d-4bit have G0 reference R_op, cap 1,200 s,
  `deadline_origin R1_after_G0_release`, and deadline − G0 end = 1,580.0 s.
  Their deadman is therefore armed after G0.
- The gated D runs and X-G have `deadline_origin G0_entry`, meaning the
  deadman is armed at G0 entry. Their reference is R_op, their cap is
  1,200 s, and the driver's `_check_soak_reference_consumed` passes.
- Step-d slots: S5 = 1.0, S6 = 1.5, bands {fast 1.0, slow 1.5}.
- The precool uses R_op with δ 1.5. The designed state R+0 targets R_op.

In the synthetic world R_op equals the soak mean (38.0 = 38.0), so value
checks there cannot tell the two apart. I therefore re-ran with a copied
step-30b result whose R_op was shifted by +1.06 / +0.10 °C, with custody
re-hashed.
- The later release and gated D run gated on **39.06 °C**, the R_op value.
- The driver check passes against R_op and refuses when compared with the
  soak mean.

Unobserved capture: I forced capture coverage to 0.5. The window-reference
record says `unobserved`. Step-30b exits 3 with "not one complete turn:
['turns:0', 'episode.g0_unreleased:0', 'thermal.state_unobserved']", and a
later gate refuses ("needs the accepted step-30b result and custody"). The
member is incomplete and the night refuses, as decision 2 requires.

**5. Refusal and incomplete clauses added or changed**, replayed on
production-shaped data:
- `Segment.reference()` refuses when a canonical `step_30b/` exists without
  complete custody or `operating_reference`. In the driver, a rejected
  attempt is renamed before the next release (`_segment`). A failed
  step-30b already refuses the night. So a night that should run never
  reaches this clause. The chain and the rejected-directory test confirm it.
- `_check_soak_reference_consumed` with R_op passes on the real chain and on
  the shifted-R_op chain.
- step-30b's three new contract fields are always present when a soak is
  given, and the driver always gives one.
- A-B-A leg G0 timeout on the re-armed path stays inconclusive (exit 0)
  (`test_aba_leg_without_its_own_g0_release_is_inconclusive_not_a_failure`
  passes with the 1,200 s cap).
- step-30b G0 timeout refuses the night, as intended by decision 5.
- Unchanged clauses whose inputs changed: the planning check "release within
  R ± δ" (now R_op, 1.5) and the kit's "S6 ≠ S5 needs a tuning record". The
  driver's `s6_tuning` carries `authority`, `from_c = S5` and `to_c = S6`, so
  the kit check passes.

I found **no clause that would refuse a night that should run.**

**6. Bound arithmetic** (computed from the code at base and head):

| Quantity | Value |
|---|---|
| Re-armed member | 1,750 + 1.13544 × 1,580 + 120 = 3,663.9952 s |
| step-30b | 3,663.9952 + 1,200 + 300 + 600 = **5,763.9952 s** (base 5,163.9952) ✓ |
| A-B-A leg | 65 + 600 + 1,200 + 3,663.9952 = **5,528.9952 s** (base 4,328.9952) ✓ |
| d-4bit | 4,863.9952 s (base: 1,800 s quiet bound) |
| `night_worst_case_s` without 4-bit | 90,662.9424 → **94,862.9424 s**, Δ exactly 4,200 s = 600 + 3 × 1,200 ✓ |
| `R1_RETRY_FLOOR_S` | 96,427 → 100,627 s; margin over the worst case preserved at 5,764 s ✓ |
| `BASE_WINDOW_S` | 109,327 s |
| `window_max_s` with display dwell | **109,627 s** at one batch crossing; +11,164 s per extra crossing (builder: 120,791 s at 08:00 PT) |
| Sampler span `t_stream_max_s` | ceil(5,763.9952) = 5,764 s, unchanged |

**7. R1 tests.** Command:
`/opt/homebrew/bin/python3.13 -m unittest discover -s tests/align -t <wt> -p 'test_r1_*.py'`,
with `JW_B5_SYNTHETIC_ONLY=1` and TMPDIR `/tmp/mag-5515/cold-opus/t`.
Result: **296 tests, OK, skipped=1**. The skip is the subprocess-helper case in
`test_r1_round7_close_deferral`, which is skipped by design.

## Numbers dimension

Every new tolerance carries a derivation:
- 1e-6 agreement bars in °C and s, citing the brief.
- `< 1 s` = one 1 Hz poll.
- rmse ±0.0005 °C = half of the printed 0.001 °C.
- 200,000 bytes = the brief's fixture cap.
- 1.5 °C = the ruling's §3.2 ladder.
- `600 + 3 × 1,200` = the caps.

The driver's reference-match bar changed from `abs_tol 1e-9` (a silly number)
to `rel_tol 1e-6, abs_tol 1e-6`. That effective 2.7e-5 °C bar at 27 °C sits at
the agreement-bar level. The quantity is bit-identical through JSON, so exact
equality would also be correct. **No number lacks a derivation.**

## Flags (none refuses)

1. **Stale doc line (fix with the merge, docs tier).**
   `docs/align/thermal_gates.md:237` says "Every later R1 G0, G1, H, precool
   and sensors-only release uses the fixed accepted R_op". The lead fix
   `ad9c0667f` reverted G1/H to the episode (G0-release) reference and
   corrected `r1_runtime_contract.md`, but not this file. Delete "G1, H" here,
   and add that G1/H keep the G0-release temperatures. A reader replicating
   from this page would compute the wrong G1/H waits.
2. **S7 now derives from R_op + S6 (record a one-line decision; no code
   change).** Step-d's `recovery_time` uses `self.reference()` and
   `self.bands()`, so G_turn = min(300, 3 × recovery) is now measured to
   R_op + 1.5 °C instead of soak + 1.0 °C. That is consistent with ruling
   decision 3 ("one reference for everything after step-30b"), but the
   ruling does not name S7, and S7 binds W1's `turn_cap_s`. On the
   production-shaped tail (R0 0550Z: +5.8 °C at 600 s after load) recovery is
   censored at 600 s either way, giving S7 = 300 s, so I expect no change in
   value. The disposition should still record it.
3. **Synthetic world cannot separate R_op from the soak mean (tests tier,
   follow-up).** In `r1_synthetic` the member's pre-warmup idle equals the
   soak mean (38.0 °C). The e2e and conformance value assertions
   (`reference_c == op["slow_c"]`) would therefore pass even if a consumer read
   soak values under an R_op label. Only the `source_member` label
   discriminates. I closed this by execution (the shifted-R_op chain
   above). Under the doctrine, the synthetic world should give the
   model-loaded idle an offset above the soak (for example +1 °C), so the
   suite exercises this rule above its bar.
4. **d-4bit not in the arm floor (latent).** `R1_G0_BOUND_INCREASE_S`
   hard-codes `600 + 3 × 1,200` and excludes d-4bit, whose bound grew from
   1,800 s to 4,863.9952 s. R1 does not run d-4bit
   (`configs/align/v4/r1_runtime.json` has `d_4bit_source: null`), so this
   has no effect today. If R0.10 ever sets it, the floor is 3,064 s short. The
   base floor also left out d-4bit, so this is not a regression. The constant
   is also not derived from `g0_timeout_s`. The driver's t0 check pins the
   runtime value to the committed config, but a config change would leave
   the floor stale.

## Agreement with the builder

Reading `31-build-report.md` after the above, I found no disagreement. Its
R_op (26.571250 / 34.106462 °C), model-B release (706.67 s after G0 entry,
Tf08 28.044 °C), bound table, 4,200 s delta, 100,627 s floor and 109,627 s
window all match my independent numbers. Its decision 3 (fixed R_op for
G1/H) was correctly reverted by the lead, and the code at `ad9c0667f` uses
the episode reference for G1/H. Its "8 failures" were sandbox
process-enumeration limits. On this Mac the full R1 selection passes.
