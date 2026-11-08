# 2026-11-08 — v5 ruling delta7, independent Sol1 review

## Outcome and authority

Seat verdict: **SIGN** on draft revision 7 at `4078c0850`.
Primary deliverable:
[ruling-delta7-review-sol1.md](../align/squeeze/v5-design/ruling-delta7-review-sol1.md).
Branch: `align/2026-11-08-v5design-ruling-delta7-sol1`, already created and
clean at intake. This review neither signs for the other independent seat
nor authorizes registration, measurement or the lead's final signoff.

The user's task supersedes ordinary queue selection and authorizes local
commits only. Mission M0 targeted intake found no active stop card or global
work-selection hold. AGENTS.md, CLAUDE.md, the source map, orchestration,
D-050/D-062 and the analysis-plan contract were consulted. The origin/main
speed toolbox was read through Git; no speed optimization was attempted.
The user's prohibition on coordination-state edits overrides the normal
end-of-run bookkeeping instructions. RUN_STATE.md, TASK_QUEUE.md,
docs/process/state_kernel.json and tests/test_gen_state.py are unchanged.

## Findings

1. **Worker fix verified.** The author passes r/missingness/replications
   explicitly; the three targeted tests pass under explicit spawn. A full
   stress row has identical sequential/spawned results, and differs from
   baseline at the same seed. The author's published source digest matches.
2. **Corrected author table reproduced.** All published rows were re-run at
   2,000 replications with the published seeds. Stress H1/H123/H4 at 28
   windows = .6835/.5155/.5575; at 44 = .8860/.7830/.7740; at 52 =
   .9285/.8615/.8250. Thus +24 is the first author-law rung meeting the
   two primary targets. Intermediate inputs select +8. Added stress reserve
   independently sums to 470.410 h, agreeing with the 470.4 h ledger line.
3. **Existing independent law checked.** Restored the prior Sol1 simulator,
   retaining its shared scores, disjoint rescues, beta shock and literal
   subset. Twelve unchanged-default rows give exactly the old results.
   The dense .01 grid reproduces baseline MDEs and gives stress MDEs
   .12/.12/.12/.14/.13. The final .13 differs from the prior coarser
   .14 result because .13 was previously untested. The independent stress
   ladder meets primary targets at +16; +24 also clears H4. Law dependence
   in conjunction power is real and must not be attributed only to MC error.
4. **Sizing is prospective.** Development inputs and a pre-calibration/test
   freeze respect D-062. The coarse ICC tiers are planning stresses, not
   confidence bounds. G12 must specify the rate UCB and ICC estimators,
   accommodate development clustering, check the rescue/net-difference ICC
   distinction and cover dependence outside .30 rather than assume it away.
   Finite-sample UCBs can select more capacity than the .05/.05 example.
   The existing development-calibrated power gate, CAP gates and prospective
   claim narrowing are essential, not satisfied by this review.
5. **Honest gate is a gross-inflation screen.** Exact iid nominal false-fail
   rate is 1.432719% per rule; six independent rules pass with probability
   91.705769%. Across-rule union bound on false failure is 8.596314% when
   each rule's member sequence is iid nominal. These are not guarantees
   under arbitrary within-date dependence. At the accepted maximum count,
   point FPR=.07857143 and Hoeffding U=.15171185. No ≤.05 certification or
   simultaneous six-rule 95% coverage follows. The 20,000-replication
   shared-maxima nominal toy passes all six at .9281 [.9244,.9316],
   versus .1068 [.1026,.1112] for the old gate.
6. **Calibration remains material.** Under the old coupled iid-calibration
   toy, the new gate passes .7595, but nominal-.10 H1/H123 power remains
   .4805/.2765 and strong-label yield is only .1870. The date-constant toy
   yields .0050 strong labels. These are sensitivities, not measured v5
   rates or a failed G12 certificate. Revision 7 explicitly requires G12
   to include this stage and narrow/enlarge calibration prospectively.
7. **Nonblocking wording repairs.** Align §4b's stale “requires honest FPR
   ≤0.05 per rule” bullet with the revised gross-inflation conjunction;
   qualify the old “identical” MDE reconciliation with the denser-grid
   result. H4 demotion correctly means exploratory outside Holm, m=3.

## Files

All paths below are new on this branch; production code and ruling text
are unchanged.

- `docs/align/squeeze/v5-design/ruling-delta7-review-sol1.md`: verdict,
  judgments, quoted evidence and limitations.
- `docs/align/squeeze/v5-design/power_sim_sol1.py`: restored prior simulator
  with optional roster sizing, derived denominators and revised honest gate;
  no author-code imports. The new roster test checks 28/36/44/52/60 windows,
  H4 counts 8/10, and six-cell support.
- `docs/align/squeeze/v5-design/delta7_checks_sol1.py`: bounded single-worker
  author replay and separate independent grid/ladder/honest-gate calculations.
- `docs/align/squeeze/v5-design/delta7-{author,coupled,ladder,gates}-sol1.txt`:
  complete command output, including design labels, pointwise 95% Wilson
  MC intervals where applicable, and elapsed times; seeds are explicit
  in the runner and the author job generator.
- This dated report.

The prior simulator was restored with:

```sh
git show origin/align/2026-11-08-v5design-ruling-delta5-sol1:docs/align/squeeze/v5-design/power_sim_sol1.py > docs/align/squeeze/v5-design/power_sim_sol1.py
```

Its original SHA-256 was
`23f0e40e3bbedc61d3633845bab0c23eb0b87f3680836f00ed7eb0ea72691335`.
The 12-row identity check loaded that exact Git object in a separate Python
module and compared both versions' `power_row(12345,10,effect,scenario)`
for effects .07/.10/.14 and the first four scenarios. Entire `(hits,means)`
return values agree, and neither version imports the author's sampler.

## Verification

Run from the clone root, one command at a time. No full/quick/sharded suite,
real-data analysis pipeline or data-reading test module was run.

```sh
python3.13 -I -B -m unittest discover -s docs/align/squeeze/v5-design -p test_ruling_power_sim.py -v
python3.13 -I -B docs/align/squeeze/v5-design/power_sim_sol1.py --self-test
python3.13 -I -B docs/align/squeeze/v5-design/delta7_checks_sol1.py author --reps 2000
python3.13 -I -B docs/align/squeeze/v5-design/delta7_checks_sol1.py coupled --reps 2000
python3.13 -I -B docs/align/squeeze/v5-design/delta7_checks_sol1.py ladder --reps 2000
python3.13 -I -B docs/align/squeeze/v5-design/delta7_checks_sol1.py gates --reps 20000
git diff --check
```

Author tests: **3 passed**, approximately .08 s. Independent checks:
**7 passed**, approximately .14 s. Identity replay: **12 exact matches**.
Author/grid/ladder/gates replays: exit 0, 41.67/174.97/57.48/13.81 s respectively.
The author's unbounded default Pool was never launched; author replay used
one explicit spawn worker. An initial `nice -n 10` prefix could not change
priority in the sandbox and warned; the bounded command continued normally.
No priority/state operation targeted the existing analysis job.

Total simulation time is approximately 4.8 minutes; targeted unittest time
is under one second per pass. Outputs are stored in the four named text
files. The fixed-nominal shared-rule gate replay gives per-rule false-fail
estimates .0135/.0146/.0142/.0147/.0149/.0152 and all-six false failure
.0719, consistent with the exact marginal calculation and union bound.
Final repeated targeted runs: 3/3 author tests and 7/7 independent checks
passed. AST parsing passed for the four sampler/runner/test files. Staged
`git diff --check` passed; final scope review contains exactly the eight
new review/evidence paths listed above, with no production or coordination
file changes. No broader suite is needed for this synthetic review artifact.

## Safety, uncertainty and exact next step

No access to real measurement directories, sealed outcomes or external
/Users/edr paths; no network, weights, pipeline, live hardware collection,
job inspection, process signaling, coordination-state change, push or merge.
No subagent, consult, plugin or external skill invocation was needed.

This review adds no MLX/native implementation or tests, so there is no new
native-test command to hand off. Live G0-G12 capability, replay, energy,
calibration and CAP evidence must still be obtained by the lead outside
this sandbox and under their authorized machine-state lanes. The toy
laws do not model actual outages, score-missingness, unknown helper mix,
unequal effects or finite development-estimator uncertainty. No ≥80%
power or actual schedule feasibility has been established for v5 data.
The next exact step is lead consumption of both independent delta7 reports,
wording reconciliation and the lead's own ruling; preserve the existing
G12/CAP holds before any registration or measurement.

Mechanism yield: spawn transport and result comparison verified the numeric
bug repair; independent score coupling changed the conjunction/MDE forecast;
exact honest tails and clustered sensitivities bounded the gate's honest
interpretation; final diff review protects the coordination/data boundaries.
No delegation-calibration row is self-assigned; the lead adjudicates this seat.
