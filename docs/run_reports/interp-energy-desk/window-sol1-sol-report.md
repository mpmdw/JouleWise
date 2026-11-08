Committed **`2d684a718`** on `perf/2026-11-08-window-efficiency-sol1`. Working tree clean; not pushed.

- [Analysis](/Users/edr/code/CapstoneProject/jw-wt/sol-window-sol1/docs/perf/WINDOW-EFFICIENCY-sol1.md): phase budgets, confound/evidence matrix, two costed redesigns, and unchanged-R1 analysis requests.
- [Handoff and verification](/Users/edr/code/CapstoneProject/jw-wt/sol-window-sol1/docs/run_reports/2026-11-08-window-efficiency-sol1.md).

Main finding: the recurring D frame budgets **11.258 programmed hours versus a 16.533-hour cap**. Unused reservation is not physical runtime saved. I recommend v4-lean; v4-max requires fresh calibration and native qualification.

**Checks passed:** `python3 -B` arithmetic and isolated source-function audits; `git diff --cached --check`; documentation and protected-path checks. No full suite, native measurements, network access, or coordination-state edits.

Open uncertainties remain R1 phase timings/tails, eligibility yield, score exchangeability, and the proposed ungated envelope. Next step: export the timing-only worksheet after R1 closes, then reconcile R10/R11 before W1 registration.