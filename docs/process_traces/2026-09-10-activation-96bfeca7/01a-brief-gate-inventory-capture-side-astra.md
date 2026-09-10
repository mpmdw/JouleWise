SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# GATE-SENSIBILITY-SWEEP-01 scout, seat A (capture → reduction → floors): inventory every numeric gate on the claim path and judge it against the instrument (gpt-6-astra, high, genre scout, read-only)

## Why this exists (Ed, 2026-09-10 ~04:20 PDT, verbatim, record 121 of docs/process_traces/2026-09-09-rehearsal-harvest/)

> also make sure there are no silly gates on accepting numbers, like make sure all barriers are sensible, recall that time where you wanted a tolerance of like 1e-15 sensitivity or something ridiculously microscopic comapred to the measurement, be sensible about insturment rigor requirements

Kernel lane GATE-SENSIBILITY-SWEEP-01 (docs/process/state_kernel.json, p1_phase_gate) must land before the first real G2-a number is consumed. Its acceptance: a table of every numeric gate, tolerance, threshold and refusal between capture and a reported number, each with its current value, the physical quantity it protects, and its ratio to the ~1 J attribution limit and the ~5 J claim bar; every gate is either justified by physics or evidence (kept, D-161 fail-closed classes) or re-set to a physically motivated tolerance with a defect-shaped test; no microscopic tolerance survives without a written physical reason.

## Reference scales (do not re-derive; cite)

- Attribution limit ≈ 1 J per window (D-078 clause 11: the instrument is attribution-limited, not noise-limited ~0.3 J).
- Effective claim bar ≈ floor + claim-side ≈ 5 J (D-078/D-083).
- powermetrics sample cadence and its timestamp resolution: read them from joulewise/adapters/powermetrics.py and docs/contracts/powermetrics_fiducial.md and state them.
- D-161 (docs/decision_log.md index row D-161 and the §D-161 body): fail-closed STAYS where the failure is PHYSICS/EVIDENCE or PRE-REGISTRATION (missing calibration, unresolved anchor, absent floor, stale drift evidence, unfrozen plan, post-hoc analysis choice) or an OPERATOR MISTAKE; deliberate-only guards retire. The operative test is MISTAKE vs DELIBERATE.

## Your footprint (seat A; seat B covers whole_window, analysis_engine, uncertainty, dominance, idle_dependence, aggregate — do not duplicate)

joulewise/adapters/powermetrics.py, joulewise/bundle_read.py, joulewise/reduce.py, joulewise/calibration_bracketing.py, joulewise/floor_extraction.py, joulewise/floor_mint_estimator.py, joulewise/detection_floor.py, joulewise/powermetrics_fiducial.py, joulewise/load_transition_alignment.py, joulewise/window_duration_margins.py, joulewise/controller.py (window completion/coverage gates only), joulewise/environment_admission.py, joulewise/night_gate.py, joulewise/envelope_gate.py, scripts/gen_g2_phase_d.py and the G2-a preflight it renders (follow the chain: what runs between launchd firing and a bundle on disk). Contracts to read for intent: docs/contracts/measurement_methodology.md, calibration_ledger.md, powermetrics_fiducial.md, load_transition_alignment.md, quiet_guard.md, window_liveness.md, run_bundle_layout.md.

Starting grep (not exhaustive; you must widen it): `grep -n -E '(TOL|TOLERANCE|THRESHOLD|_EPS|EPSILON|1e-[0-9]+|MAX_SKEW|MAX_DRIFT|FRESH_S|MIN_SAMPLES|MAX_AGE|isclose|abs\(.*\) *[<>])'` over the footprint. Known hits to classify include reduce.py:1400/1472/1584/1586/1847 (1e-12 against fiducial bounds), reduce.py:1928 (1e-9 relative on power_w), reduce.py:1948/1955 (1e-6 on widths), controller.py:2555-2556 (1e-9 s completion slack), envelope_gate.py:514 (1e-12 in a permutation chi-square comparison), floor_mint_estimator.py:524, bundle_read.py:2885 (1e-6), and every named constant in detection_floor.py, calibration_bracketing.py, floor_extraction.py, load_transition_alignment.py, environment_admission.py, night_gate.py, powermetrics_fiducial.py.

## The distinction you must make on every row (this is the whole job)

1. IDENTITY CHECK: the compared values are supposed to be the SAME NUMBER re-derived (same bytes, same arithmetic, stored vs recomputed). A 1e-9 relative or 1e-12 absolute fuzz here is float-equality hygiene, not a measurement tolerance. Classification: `identity` — KEEP, but say so in one line; recommend no change unless the two sides are computed by different arithmetic paths (then propose the honest bound and say why).
2. MEASUREMENT TOLERANCE: the compared values are two physical readings or a reading vs a bound, where real instrument noise, timestamp jitter, sample cadence or calibration uncertainty legitimately separates them. Here a tolerance far below the instrument's resolution is the "1e-15" defect. Classification: `measurement` with a `sensible` / `microscopic` verdict; for `microscopic`, propose the physically motivated value (derive it: cadence × power, timestamp resolution, calibration width, D-078 1 J) and a defect-shaped test (the counterfactual input that the current gate wrongly refuses and the new gate admits, plus the input the new gate still refuses).
3. EVIDENCE/PRE-REGISTRATION REFUSAL: missing calibration, unresolved anchor, absent floor, stale drift evidence, unfrozen plan, post-hoc choice, agent present during capture. Classification: `evidence` — KEEP (D-161). List it so the table is complete; one line each.
4. OPERATOR-MISTAKE GUARD vs DELIBERATE-ONLY GUARD (D-161 test): name which; deliberate-only guards are out of this sweep's remit (THREAT-MODEL-PRUNE-01) — list, do not judge.

## Deliverable (return the whole report as your FINAL MESSAGE; the lead files it — write nothing in the repository)

Report envelope claude-codex-report/v1, genre scout, header < 8192 bytes. Body:

A. Table, one row per gate: `# | file:line | constant / expression | value | what physical quantity it protects | class (identity / measurement / evidence / mistake-guard / deliberate-guard) | ratio to 1 J and to 5 J (or "n/a: not an energy") | verdict (keep / re-set / needs_ruling) | one-line reason`.
B. RE-SET list, ranked by how likely the gate is to refuse a real G2-a number: for each, the proposed value with its derivation from instrument facts, the exact code change (diff-shaped, not applied), the defect-shaped regression test (both counterfactuals), and which contract doc sentence must change with it.
C. KEEP list summary: count per class; any `identity` row whose two sides are NOT the same arithmetic path gets called out explicitly.
D. Anomalies: any gate whose value you could not trace to a physical reason or a decision-log entry, and any gate on the chain you could not reach by reading (say what you could not open).
E. NEEDS_RULING items (question, options, recommendation, blocked work) for anything that is a design choice, not a reading.

Read-only: no edits anywhere in the repository, no test runs beyond `python3 -c` sanity arithmetic, no full suite, no git operations. If a hit is in seat B's footprint, list the file:line under D and move on.
