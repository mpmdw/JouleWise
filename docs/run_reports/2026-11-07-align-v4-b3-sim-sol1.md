# ALIGN v4 B3 simulation — Sol1 handoff

Branch `align/2026-11-08-b3-sim-sol1`, base
`50c99e4f83b9e4d1442745fbe4492e0a1cc6446c`. Task authority: the explicit
synthetic-only B3 brief and R12 amended in `origin/main:RUN_STATE.md` items
214–215 (`c07b388e90d9f085e6428a1e0d96b0361ff417f0`).

Full report, assumptions, file:line roster sources, all 36 scenario tables,
Monte Carlo intervals, prospective alternatives and open questions:
[`B3-SIM-sol1.md`](../align/v4/b3-sim/B3-SIM-sol1.md).

Count6 can exceed R14's nominal mean FPR under moderate window dependence:
hot 5% exclusion, .5 s_r window effect, no trend gives maximum FPR
2.841% [2.826, 2.856] versus fixed8 2.141% [2.130, 2.152]. Rank05 gives
5.382% versus 4.125%. Fixed8 also fails the nominal targets under the
modeled forward trend. Minimum seven alone is insufficient; minimum seven
plus a frozen .5 s_r margin passes the mean targets on this model grid,
with worst pair-specific maximum FPR 1.767% [1.754, 1.779]. This is a
candidate sensitivity result, not an adopted estimator or a live guarantee.

Changed files: the standalone NumPy simulator, study report, two CSV result
tables, metadata, completed-run stdout/checks and the aborted preflight log
under `docs/align/v4/b3-sim/`, plus this pointer. No product/runtime code,
coordination state or registration was changed. No network, measurements,
model downloads, real data, external checkout, full suite or other-job
inspection/control. No delegation or consult. The already-created task
branch was retained; only local commits are authorized, no push.

Verification:

* Simulator `--check`: six unittest checks passed. One completed
  100,000-study-per-scenario Monte Carlo run, 153.2 seconds, all count and
  iid-risk assertions passed. An initial first-scenario reference failure
  and diagnostic probes exposed large-array operand mutation on this local
  Python 3.14.6/NumPy 2.2.6 combination; explicit allocating operations and
  an immutability regression check were added before the completed run.
  The report discloses the aborted attempt; there was no seed/result selection.
* `python3.13 -B -m unittest tests.align.test_v4_estimands`: 15 passed,
  .004 seconds. Python 3.13 simulator AST parsing passed. The installed
  Python 3.13 lacks NumPy, so the simulation used Python 3.14.6.
* Stdlib output audit: 144 count rows, 1,296 score rows; source digest,
  probability bounds, pair means, paired deltas and quoted stdout verified.
  The complete report tables were generated from the saved CSVs.
* Full suite omitted per the user load restriction; this is docs/simulation
  only. No MLX/native tests are required by these files. `git diff --check`
  is the final whitespace gate; final commit identifiers are in the handoff.

Next exact step: lead compares both independent B3 reports, reproduces the
simulator with supported Python 3.11/3.13 + NumPy off the busy machine, then
rules the final fit/calibration/test bill, scorer/rank, final eligibility,
attempt accounting and drift treatment before W1 registration. Uncertainty
remains about the actual residual scale/drift, test unit/schedule and the
margin's detection cost. Coordination files were deliberately left to the
lead under the brief's explicit prohibition.
