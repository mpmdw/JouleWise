PR #314 head beb808bcc4d7d65f4648980c0c356f6dda6b5cb6

## Why

Ed, 2026-09-10 ~04:20 PDT: "make sure there are no silly gates on accepting numbers … recall that time where you wanted a tolerance of like 1e-15 … be sensible about instrument rigor requirements" (record 121). Kernel lane GATE-SENSIBILITY-SWEEP-01 (p1, before any G2-a number is consumed).

## What the sweep found

Two Astra scouts inventoried every numeric gate between capture and a reported number (trace `docs/process_traces/2026-09-10-activation-96bfeca7/`, reports 02a and 02b): 299 rows, 284 keep. The 1e-15 of Ed's example is a decimal presentation quantum inside a calibration identity check, not a measurement tolerance, and stays. Four real defects share one mechanism: a 1e-9 s slack compared against epoch-scale binary64 timestamps whose representable step is 0.238 μs at epoch 1.789e9, so valid data is refused by rounding luck.

## What lands here

- R1 `environment_admission.py`: `ADMISSION_TIME_ROUNDING_S = 1e-6` (four contemporary epoch roundings; precedent `uncertainty_evidence.py:45–59`) replaces three 1e-9 literals. A 10 μs excess or a capture endpoint one sample outside the attempt still refuses.
- R3 `controller.py` cooldown completion: span slack 1e-6; coverage slack = max(1e-6, summed endpoint ULPs of positive overlap contributions + ulp(coverage)). 30 s / 80 % / power / thermal / 300 s `cap_hit` semantics unchanged.
- R4 `load_transition_alignment.py`: producer midpoint from the endpoint offsets, the validator's arithmetic path (demonstrated 0.119 μs divergence); validator tolerance unchanged.
- G2-a probe producer `idle_seconds` 30 → 75 (report 09): a fast 512-token member supplied ~48 s of raw sampler intervals against the 60 s anchor-v3 rate-fit gate, and 300 idle records sit 3 short of 3(L+1) at an exact 100 ms cadence. Pin test added. Adds ~21 min to the chain (budget 13,500 s).
- Contract sentences (measurement_methodology.md, load_transition_alignment.md) written to the replication bar.
- 13 defect-shaped regressions in `tests/test_gate_sensibility_rounding.py` (admit + refuse counterfactual per repair).

## What deliberately does NOT land

- R2 (`reduce.py` coverage endpoint ULP): `reduce.py` is a D-138 governed estimator input pinned by the issued D-079 acceptance; staged as a patch for the atomic re-freeze (record 15). `reduce.py` is byte-identical to main here.
- B1 (D-165 zero-point provenance band): needs a decision-log correction → cold gate; not G2-a-blocking at G2-a energies.

## Gates

- Seat 08 (Astra high) implementation with per-repair mutation reverts; execution refuter 18 (Astra xhigh): one should_fix → fix round 1 `558f9368` (bench delta re-audit pasted in record 20); Opus contract/physics refuter: no blockers, three should_fix wording items → fix round 2 `58d4696b`; delta re-audit of both rounds (Astra) in flight; full replay at the final head in flight (one known LOCAL-ONLY pre-existing failure `test_controller::test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`, sleeping-sentinel fixture class, CI green at 078a13a4 — record 19).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
