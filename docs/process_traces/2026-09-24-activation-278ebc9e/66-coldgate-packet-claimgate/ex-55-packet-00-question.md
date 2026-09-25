# D-184 council packet: claim admission and equivalence

This is a facts-only reading packet. D-184 calls for Fable 5.1, Opus 5.5, Sol 6.0, and Astra 6 on major science decisions when usage permits; their agreement is not itself progress (`docs/decision_log.md:12168-12174`). No option in this packet is adopted.

## Question to be decided elsewhere

How should a registered effect clear a physically applicable instrument floor and a calibrated uncertainty test, while retaining useful power for real effects? The current evaluator compares a point estimate with the floor, then checks interval signs and an adjusted test decision (`joulewise/analysis_engine/claims.py:343-382`). The floor's prediction term is for a new block, while the paired estimator tests a mean of blocks (`joulewise/detection_floor.py:871-881`; `joulewise/analysis_engine/estimators.py:450-489`).

How should an equivalence night be judged when old and new nights may have separate common shocks, and when both a mean shift and a spread change matter? The current numerical rule checks a new maximum and range against old screens after six retained captures (`scripts/epoch_equivalence_check.py:480-536`). The desk replacement remains proposed and is weak against a fourfold variance increase (`docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/equivalence_replacement.md:1-3,19-30`).

The proposed AP-5M v5 analysis plan for the MATH problem set's joules per correct answer (J/correct) requires a redesigned and validated gate before a headline claim; its contrast-scale to J/correct floor mapping is open (`docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/01-ap5m-draft-v5.md:15,55-69`).

Read `01-current-gate.md` for operative code, `02-simulation-facts.md` for synthetic rates, `03-constraints.md` for ratified boundaries, `04-options.md` for unranked mechanisms, and `05-open-facts.md` for ten spot checks.
