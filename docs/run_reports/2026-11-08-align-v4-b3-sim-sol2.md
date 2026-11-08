# ALIGN v4 B3 simulation — Sol2 handoff

2026-11-08 UTC / 2026-11-07 PST. User-assigned [AGENT] work on
`align/2026-11-08-b3-sim-sol2`, from R11 `50c99e4f8`.
The authoritative detailed report is
[B3-SIM-sol2](../align/v4/b3-sim/B3-SIM-sol2.md), including source file/line
citations, assumptions, every main scenario, Monte Carlo intervals, quoted
output, proposed prospective fixes and unresolved questions. It is a synthetic
sensitivity analysis; no live gate or ruling is closed.

Changed files:

- `docs/align/v4/b3-sim/simulate_sol2.py`: stdlib synthetic simulator, one process.
- `docs/align/v4/b3-sim/test_simulate_sol2.py`: 11 analytical unittest checks.
- `docs/align/v4/b3-sim/results-sol2.json`: complete results, per-pair MC intervals,
  paired deltas, exact controls and source/script pins.
- `docs/align/v4/b3-sim/output-sol2.txt`: compact simulation output.
- `docs/align/v4/b3-sim/B3-SIM-sol2.md`: requested analysis and recommendations.
- This dated pointer/handoff.

The single simulation run used 60,000 tapes/scenario, seven scenarios and three
window-effect scales, seed 20261108, Python 3.13.18; elapsed 210.56 s. Its script
SHA-256 is `dcc9f7425c5abd472f2883397db08b4155099604abef7d11b0551d387e68e93c`.
The JSON records the runtime version and creation time; the generated results
were not changed after the run.

Findings that affect a number: count6 exceeds both nominal FPR bars in all six
main stationary tau=.5 scenarios; hotter-future drift defeats fixed eight too.
Hot-correlated 20% exclusions reduce both-pair cap success to 86.767%
[86.493, 87.035] versus 95.780% [95.616, 95.938] for independent exclusions.
A minimum of seven helps partly; fixed eight removes the adaptive horizon;
a conservative threshold allowance is valid only under the stated bounded
drift/eligibility/common-noise assumptions. Fit-slot deductions can make the
eight-window capacity inadequate. No empirical parameter estimates are claimed.

Verification:

```sh
python3.13 -B -m unittest discover -s docs/align/v4/b3-sim -p test_simulate_sol2.py
# 11 tests, OK, 0.001 s (before the simulation).
python3.13 -B docs/align/v4/b3-sim/simulate_sol2.py --replicates 60000 --seed 20261108 --output docs/align/v4/b3-sim
# One run; PASS: exact count / iid rank / review-counterexample audits; 210.56 s.
```

AST parsing of both new Python files passed. `git diff --check` and the final
staged whitespace check passed. No full suite was run: the user prohibits it
while the eight-worker blinded job runs, and this work changes no product or
existing test code. The new tests guard numerical/stopping mechanics and the
analytical comparison laws. No study-data reader, Block-5 pipeline, network,
model download, native runtime, hardware capture or external integration ran.
No native MLX test is needed for this stdlib-only change. No delegated agent or
external consult was invoked; this independent seat owns its final review.

Coordination state is lead-owned and untouched by explicit instruction:
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`tests/test_gen_state.py`. No new kernel task or protocol constant was installed.
All source refs were read locally; cited external paths were treated as text.
The branch is for a local commit only; no push or merge is authorized.

Open questions: final F/C/T roles and fit cost, U3/B final eligibility and late
adjudication, actual common scorer/LOTO asymmetry, live state/score/eligibility
dependence, defensible drift bounds and resulting detection cost. Simulation
parameters are plausible sensitivity cases, not learned from sealed outcomes;
unbounded/serial drift and residual-dependent missingness remain outside the
model. The comparison includes both sample-size and state-selection effects;
it is not an equal-m identification of optional stopping alone.

Next exact step: lead compares both B3 seats, rules the prospective ordered
manifest/stop/cap policy and scorer/drift treatment before W1 registration,
then runs any resulting owning native gates later in a controlled session.
