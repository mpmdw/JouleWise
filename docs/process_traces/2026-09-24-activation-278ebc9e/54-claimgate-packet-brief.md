ROLE: SCOUT / PACKET ASSEMBLER (Sol 6.0) for a JouleWise D-184 four-model council: "redesign the claim-admission gate and the equivalence rule so that real effects are detectable and false claims are not admitted". Facts only, no positions. Do not call Claude or any other agent.

WRITE_SCOPE: ["docs/process_traces/2026-09-24-activation-278ebc9e/55-claimgate-council-packet/**"]

Worktree: /Users/edr/code/wt-278ebc9e-claimgate (branch docs/2026-09-24-278ebc9e-claimgate). Fences: never launchctl, sudo, networksetup, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise; no model loads; scratch /tmp/278ebc9e/claimgate/. Sandbox cannot write .git: leave files uncommitted.
Why: the desk simulations (docs/process_traces/2026-09-24-activation-278ebc9e/19-desk-simulations/README.md and results; report 18b) replayed the PRODUCTION claims.py admission path. They found:
 - it misses a 2σ effect in 100 % of trials and a 5σ effect in 84 %;
 - its nominal 95 % interval covers only ~56 % under shared-plus-local shocks, while the expanded decision interval covers ~95 %;
 - `tost_v1` at a 4σ margin fails to admit equivalence at δ = 0 in 94.8 % of trials;
 - the equivalence-night rule false-alarms in 58 % of no-change trials;
 - a PROPOSED TOST replacement is nearly blind to a ×4 variance increase.
 The fresh review (docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md) says claims.py:344 compares a mean of n blocks against a one-block prediction bound (≈√n too conservative) and tests the point estimate, not a confidence bound. The AP-5M v5 draft (docs/process_traces/2026-09-24-activation-278ebc9e/52-ap5m-v5-draft/) depends on this gate, and O-21 (Ed: YES) adds an instrument-floor condition to J/correct claims.
BUILD (each file < 250 lines, plain language, every internal id defined at first use, every fact with file:line):
 00-question.md; 01-current-gate.md (exactly what claims.py decides, step by step with file:line; every constant and where it came from — D-numbers; which claims in the paper plan route through it); 02-simulation-facts.md (the numbers above with their cells, generating models, and what each rate means); 03-constraints.md (the ratified attribution limit ~1 J / ≈5 J bar, D-078 cl.11, the D-078/D-083 addendum estimand statement, D-165, O-21's floor clause, pre-registration and rules-before-data constraints, what data exist already); 04-options.md (neutral: minimum-effect tests on confidence bounds, TOST with a physically sized margin, a block-bootstrap interval with dependence, hierarchical/shared-shock models, keeping the floor as a separate physical condition; for each: what it guarantees, its operating characteristic if the simulations give it, cost to implement); 05-open-facts.md with ten spot-checked citations.
OUTPUT: file list and a five-line fact summary per file.
