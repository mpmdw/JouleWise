# Build brief: R1 G0 operating-point reference, S6 slow band, 1,200 s model-member cap

Seat: Sol 6.1 xhigh, build. Branch `lane/2026-11-10-r1-g0-rop` from `20e9edbc4`
(the frozen R1 measurement head). Worktree `/Users/edr/code/jw-wt/r1-g0-build`.

## Authority (in this order; the first wins where they disagree)
1. `docs/process_traces/2026-11-10-r1-g0/10-fable52-ruling.md`, sections 1, 3 and 7
   (decisions 1-10). Fable 5.2 has the final say on paper-bound design (Ed, 11-10).
2. `20-lead-disposition.md` (same directory). It adopts the ruling and defers NR-1.
3. The existing contract and code (`docs/align/r1_runtime_contract.md`,
   `joulewise/align/apple/r1_runtime_contract.py`, `r1_runtime.py`). Where
   these contradict the ruling, change them to match it and list each change.

## What to build
1. **R_op.** After the accepted `step-30b` member, its WP14(b) pre-warmup capture
   (the median over the 60 s before warmup entry, coverage >= 0.9; reuse the
   existing `capture_reference` path) becomes the reference for every later R1
   gate: G0, G1, H, precools and `g0-release-soak`. A `g0-release-soak` before
   any accepted step-30b keeps the soak mean (ruling decision 2). An unobserved
   capture leaves current behaviour: the member is incomplete. Record
   `reference_source` honestly (`r1_soak_reference` or the step-30b capture), and
   print R_op minus the soak mean per key, with no gate on it.
   `step-30b` itself gates against the soak reference with the S6 band; nothing
   else exists before it.
   NOTE: by the ruling's numbers, step-30b's own G0 against the soak mean at 1.5 C
   is predicted to release at 1,328 s (model B) or never (model A). READ the
   ruling's section 1 row 1 and section 4.1 carefully. If the ruling means
   step-30b's own G0 uses its own just-captured pre-warmup median (R_op), build
   that. If the text leaves step-30b's own G0 reference undetermined, stop and
   report NEEDS_RULING on exactly that point, quoting the lines. Do not guess.
2. **δ_slow = 1.5 C as slot S6** in `configs/campaigns/align_v4/registration/r1_slots.json`,
   with a tuning receipt citing the ruling (path and commit `cc709ace2` on branch
   `ops/2026-11-10-r1-g0-diagnosis`). S5's formula and value stay; the fast band
   stays at max(1.0, 3 SD). The runtime's slow band is max(S6, 3 x soak SD).
3. **G0 cap of 1,200 s** (`G0_CAP_MAX_S`, the existing constant) for every R1 model
   member: add `step-30b`, the three A-B-A legs and `d-4bit` to the 1,200 s kinds.
   `g0-release-soak` keeps 600 s.
4. **Deadman after G0** for the A-B-A legs and `d-4bit`, using the existing
   `rearm` path that step-30b and step-d already use. The gated D runs and X-G
   keep their deadman at G0 entry.
5. **Bounds.** Recompute every bound that contains a model-member G0 cap
   (`segment_bounds`, `aba_leg_bound_s`, the night table, `window_max_s` in the
   arm route). The ruling expects step-30b = 5,763.9952 s and each A-B-A leg
   4,328.9952 -> 5,528.9952 s. Confirm these against the code, or report the
   difference with arithmetic.
6. **NR-1 is NOT built.** The gated D runs and X-G keep their current mechanism,
   with R_op substituted for the soak mean.
7. Update `docs/align/r1_runtime_contract.md` and `docs/align/thermal_gates.md`
   (if it describes R1 references or caps) to match the build.

## Evidence required (execute)
- Every touched test module passes, plus the R1 test modules under `tests/align/`.
  Run only those. CI runs the whole suite. Set `JW_B5_SYNTHETIC_ONLY=1` and use
  your own `TMPDIR`. Python is `/opt/homebrew/bin/python3.13`.
- **Production-shaped replay.** Feed the real 11-10 step-30b thermal journal
  `/Users/edr/night-align/r1-20261111T014106Z/night/align-r1/step_30b/runs/align-v4-r1-step-30b/outputs/align_thermal.jsonl`
  (READ ONLY) through the real `ThermalSession.wait` with a virtual clock.
  - The old parameters must reproduce the recorded 600 s timeout.
  - The new parameters must show no release within the 600 s of data, with
    the R_op value printed.
  - A synthetic continuation of the tail (Fable model B: level = own idle,
    tau 70/500 s, fitted to the record) must release inside 1,200 s.
  Put this replay into a test if it can run without the custody file
  (embed a decimated fixture of at most 200 KB); otherwise a script under
  `scripts/` with its output in your report.
- One synthetic end-to-end R1 chain through the real stage chain (the existing
  `tests/align/test_r1_runtime_e2e.py` style) with the new parameters. It must
  show R_op being captured at step-30b and consumed by a later gate.

## Numbers rule (binding)
Every tolerance, threshold or test assertion on a measured or derived quantity
carries its derivation beside it: the quantity's physics (sensor resolution,
measured idle spread, 1 Hz sample interval, the ~1 J attribution limit) or its
printed precision. A number with no derivation is not written. Agreement bars
between two programs: 1e-6 relative or absolute in the column's unit. Exact
equality only for integers, hashes and identical code on identical inputs.

## Decide
Decide everything the governing texts determine, and list it under "decisions I
made". NEEDS_RULING only for a choice that changes which data count or a printed
number.

## Limits
- Commit in this worktree; do not push. No network.
- Never touch `/Users/edr/night-custody/**`, `/Users/edr/night-align/**`
  (read-only), launchctl, pmset, sudo or systemsetup. Start no measurement.
- No `cd` in compound shell commands; use absolute paths.
- Report: `docs/process_traces/2026-11-10-r1-g0/31-build-report.md`.
