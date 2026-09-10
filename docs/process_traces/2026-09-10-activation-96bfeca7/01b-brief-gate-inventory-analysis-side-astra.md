SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# GATE-SENSIBILITY-SWEEP-01 scout, seat B (whole-window → analysis engine → reported number): inventory every numeric gate on the claim path and judge it against the instrument (gpt-6-astra, high, genre scout, read-only)

## Why this exists (Ed, 2026-09-10 ~04:20 PDT, verbatim, record 121 of docs/process_traces/2026-09-09-rehearsal-harvest/)

> also make sure there are no silly gates on accepting numbers, like make sure all barriers are sensible, recall that time where you wanted a tolerance of like 1e-15 sensitivity or something ridiculously microscopic comapred to the measurement, be sensible about insturment rigor requirements

Kernel lane GATE-SENSIBILITY-SWEEP-01 (docs/process/state_kernel.json, p1_phase_gate) must land before the first real G2-a number is consumed. Its acceptance: a table of every numeric gate, tolerance, threshold and refusal between capture and a reported number, each with its current value, the physical quantity it protects, and its ratio to the ~1 J attribution limit and the ~5 J claim bar; every gate is either justified by physics or evidence (kept, D-161 fail-closed classes) or re-set to a physically motivated tolerance with a defect-shaped test; no microscopic tolerance survives without a written physical reason.

## Reference scales (do not re-derive; cite)

- Attribution limit ≈ 1 J per window (D-078 clause 11: the instrument is attribution-limited, not noise-limited ~0.3 J).
- Effective claim bar ≈ floor + claim-side ≈ 5 J (D-078/D-083).
- powermetrics sample cadence and its timestamp resolution: read them from joulewise/adapters/powermetrics.py and docs/contracts/powermetrics_fiducial.md and state them.
- D-161 (docs/decision_log.md index row D-161 and the §D-161 body): fail-closed STAYS where the failure is PHYSICS/EVIDENCE or PRE-REGISTRATION (missing calibration, unresolved anchor, absent floor, stale drift evidence, unfrozen plan, post-hoc analysis choice) or an OPERATOR MISTAKE; deliberate-only guards retire. The operative test is MISTAKE vs DELIBERATE.

## Your footprint (seat B; seat A covers the capture adapter, bundle_read, reduce, calibration_bracketing, floor_extraction, floor_mint_estimator, detection_floor, powermetrics_fiducial, load_transition_alignment, window_duration_margins, controller, environment_admission, night_gate, envelope_gate and the G2-a chain scripts — do not duplicate)

joulewise/whole_window.py, joulewise/analysis_engine/*.py (artifact.py, estimators.py, claim_side_bound.py, inputs.py, distributions.py and every sibling), joulewise/uncertainty_evidence.py, joulewise/dominance_closeout.py, joulewise/idle_dependence.py, joulewise/aggregate.py, joulewise/salvage_dangler.py, joulewise/cli.py (acceptance gates only), joulewise/paper_* modules if present (reported-energy rendering). Contracts to read for intent: docs/contracts/analysis_plans.md, paper_claim_side_bound.md, paper_reported_energy.md, d165_dominance_closeout.md, d117_step6_confirmation_table.md, claims_ladder.md, measurement_methodology.md (the floors doctrine paragraphs).

Starting grep (not exhaustive; you must widen it): `grep -n -E '(TOL|TOLERANCE|THRESHOLD|_EPS|EPSILON|1e-[0-9]+|MIN_SAMPLES|MAX_AGE|isclose|abs\(.*\) *[<>])'` over the footprint. Known hits to classify include whole_window.py:810/823/903-907/3463/3531/3540/4386/4389/4540-4552 (1e-9 / 1e-12 against authenticated bounds, minted records, stored-vs-fresh gross and idle values), idle_dependence.py:29-30 (METADATA_REL_TOL 1e-9, METADATA_ABS_TOL 1e-12), dominance_closeout.py:902/963, and every named constant in analysis_engine/artifact.py (22 hits), uncertainty_evidence.py, estimators.py, claim_side_bound.py, aggregate.py.

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
