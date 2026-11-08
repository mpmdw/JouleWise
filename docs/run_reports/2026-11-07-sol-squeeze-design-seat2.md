# Independent Sol squeeze-design seat 2 — run report

Date: 2026-11-07. Branch: `align/2026-11-07-sol-squeeze-design-seat2`.
Starting HEAD: `be3cc8b680cde290299aeb8d198de73993fe38b2`.

## Delivered

Wrote [the requested independent design](../align/squeeze/sol/squeeze-design-seat2.md).
It contains an executive summary, prioritized proposed owners/lanes/costs and
R1/W1/D gates, eight findings with confidence and commit/path/line citations,
attack/control definitions, joint estimands, fixed-FPR OR/AND calibration,
monitor identity/visibility/blinding, power calculations, costs, decision rules
and the cheapest risk-reduction experiment.

Main recommendations and limits:

- Use real local hidden-work/sham controls and an adaptive combined attack;
  edited logs alone establish neither physical detection nor semantic security.
- Primary monitoring uses the upstream SHADE `no_scratchpad` view and a proposed
  frozen local Qwen3-30B-A3B-4bit monitor. A full-reasoning view is secondary.
  Logged reasoning counts can explain energy while their contents remain hidden
  from the primary monitor. This is the largest risk to the squeeze rationale.
- Fit, calibration and test cohorts are disjoint. The concrete option has 20
  fitting and 39 calibration episodes per pair, 100 held-out benign tests per
  pair, and 80 held-out attack attempts per pair. Its primary estimand is the
  balanced mixture, not a worst-task guarantee.
- Exact iid paired-test power is calculated; clustered power, calibration
  exchangeability and useful sabotage capability remain assumptions to validate
  before a registration. The text explicitly distinguishes marginal FPR from
  realized-threshold FPR and flags the existing quantile-path discrepancy.
- The conservative full D option reserves 37 long D-sized windows plus R1/W1
  and two 30B development nights: 666.046 hours / 53.71 conventional nights.
  This is a deliberately explicit full option, not a forecast of actual runtime
  or a claim that it fits the remaining November calendar. First spend 0 nights
  on visibility/count closure, then 1–2 approved 30B development nights.

## Files and authority

Only these files are added:

- `docs/align/squeeze/sol/squeeze-design-seat2.md`
- `docs/run_reports/2026-11-07-sol-squeeze-design-seat2.md`

No changes to code, tests, registration, decision log, `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py` or
advisor-facing state. No kernel task registered. The user explicitly reserved
coordination state to the lead, overriding ordinary end-of-run state updates.
Nothing in this report installs a scientific ruling or grants an arm.

Mission M0 intake read the applicable repository conventions, stop-card/status
and queue sections, playbook/orchestration, authority map and targeted decision
entries. There was no active stop card; the worktree was initially clean and
already on the requested branch. No delegated agent or cross-model consult was
started; this remains an independent seat.

Read the required agenda/HTML and the four specified protocol/audit ref sources
using local Git objects. No fetch: the binding no-network rule took precedence
over the conflicting fetch request. No other squeeze-seat branch was read.
No external filesystem pointer, real restricted directory, measurement data,
model weight or sealed outcome was opened. No B5 pipeline, hardware collection,
process inspection, model download, integration authorization or network action
was run. The ongoing blinded analysis job was not inspected or touched.

Some initial source discovery found that ALIGN code is absent from this pruned
main checkout, and two guessed Git paths were absent at V4. All source reading
then used explicitly located V4 Git blobs or the MAIN amendment. The citations
in the deliverable resolve to existing pinned blobs; no guessed path remains
as evidence.

## Verification

Documentation only; no unittest module, full suite, sharded suite, pytest,
compileall or native MLX test was needed or run. The user specifically prohibited
the full suite while the 8-worker job runs. All Python work below was isolated,
stdlib-only arithmetic or repository-text validation, taking seconds.

Executed `python3.13 -I -B -` with the following independent planning calculations:

1. Binomial CDF inversion for one-sided exact FPR bounds: at n=100, alpha=.025,
   k=0/1/5 gives .036217/.054459/.112835.
2. Exact McNemar power, summing over the binomial discordant-count distribution
   and its conditional binomial direction test. At cutoff .025, n=80/100/160,
   the three scenarios printed in the design give respectively
   (.9083,.7368,.4368), (.9614,.8367,.5444), (.9982,.9708,.7772).
3. Sample-max marginal/conditional tails, all-caught lower bounds, conformal
   ranks and window reservations. The conservative reservation sum is
   `(37*59520 + 61607 + 44640 + 2*44640)/3600 = 666.0463889 h`.
4. A source-citation checker loaded each named `commit:path` with `git show` and
   checked 33 cited line/ranges across 17 source blobs. Also checked code fences,
   ranks, tail bounds, power approximation and budget assertions. Final result:
   PASS. All nine exact-power cells and three exact-FPR bounds reproduced.
5. `git diff --check`: PASS after staging both new files; final staged paths
   reviewed against the two-file scope.

The first budget assertion caught a 0.001-hour rounding mistake in the table;
it was corrected before the final check. No measured or scientific outcome
changed. No test gate here established a hardware number.

Reproducible exact-power core (no third-party dependencies):

```python
import math

def mass(n, k, p):
    return math.comb(n, k) * p**k * (1-p)**(n-k)

def paired_power(n, b, c, alpha=.025):
    out = 0.0
    for d in range(1, n+1):
        cutoff = next((k for k in range(d+1)
                       if sum(mass(d, j, .5) for j in range(k, d+1)) <= alpha),
                      d+1)
        out += mass(n, d, b+c) * sum(
            mass(d, j, b/(b+c)) for j in range(cutoff, d+1))
    return out
```

## Commit and handoff

This report and the design are committed together locally with message
`docs(align): draft independent Sol seat 2 squeeze experiment design`.
No push or merge. The final response supplies the resulting commit ID.

No blocker remains to delivering this desk assignment. Adoption remains the
lead's decision. The next exact step is to choose the trust/visibility boundary,
balanced-mixture versus per-task claim, monitor, fixed sample sizes and budget,
then issue the synthetic visibility/quantile/pairing packet and 30B development
kit brief. Complete clustered-power simulation before registration, not after
test outcomes. No pending question requires this seat to open study data.

Native work the lead must run outside this sandbox, after implementation and
with the measurement machine free of agents: existing R0/R1 and W1 native gates;
DC synchronization/battery-storage/boundary validation; actual injector execution,
RNG/cache isolation and matched-work checks; monitor request/renderer/parser
fidelity and context-cap checks; then the preregistered development and held-out
cohorts. No MLX implementation or native test was added in this documentation
task, and no native validation is claimed.

Remaining uncertainty: local monitor adequacy, D's useful sabotage rate,
independent DC capture readiness, battery energy buffering, DC-model residual
spread, window dependence, calibration tail stability and actual adaptive gain.
The design supports a measured limits result if the hypothesized squeeze fails;
it does not promise a favorable result or venue acceptance.
