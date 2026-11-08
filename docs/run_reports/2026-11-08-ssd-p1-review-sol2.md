# SSD-P1 review — Sol 2 run report

2026-11-08 UTC (2026-11-07 PST). Branch:
`align/2026-11-08-ssd-p1-review-sol2`, already created at intake, initially
clean at `58fb53c3054994b9aa6ffd6b5444e5e3d6ad421e`.

## Outcome and scope

Delivered [the independent review](../align/v4/ssd-p1-review-sol2.md):
**SIGN_WITH_CHANGES**, with five HIGH, two MED and one LOW findings.
B-unmount and zero human actions per window are supported. Adoption as
written is held on the numerical impossibility overclaim, unqualified
replacement of stability gates, incomplete counter/log observability,
incomplete R1/operational transfer and missing amended R12 loss/series rules.
The report includes corrected arithmetic, P1–P5 dispositions, an offline
macOS fact audit and purchase-spec limits.

This is an explicitly assigned [AGENT] documentation review, selected by the
user over the generated queue. M0 intake covered the inactive stop card,
queue and do-not-do list, workspace state, playbook/orchestration, D-043 and
D-062, both SSD seats and the task-specific authority. No coordination-state
task was registered. RUN_STATE.md, TASK_QUEUE.md, state_kernel.json and
tests/test_gen_state.py were preserved under the user's binding exception.
No code, existing recommendations or evidence bundles changed.

## Evidence and checks

Authority: `origin/main` at
`c07b388e90d9f085e6428a1e0d96b0361ff417f0`, RUN_STATE items 181, 210,
212–215. Agreement reviewed at the initial head above. Original seat refs:
Sol 1 `b29aae8e0e78ee344827c04c4e7e990977a31555`; Sol 2
`994059c323677ff0faa4bba9f7e7ac190b3324be`.
R12's rationale was read from
`origin/perf/2026-11-08-latency-synthesis:docs/perf/2026-11-08-latency-synthesis.md`.
Some proposed source documents are absent from this checkout; remote-tracking
Git objects, not external worktrees, supplied the cited branch documents.

| Check | Result / number protected |
|---|---|
| `python3.13 -B -m unittest tests.align.test_ssd_qualification` | 26 tests OK in 0.353 s; existing synthetic Q1/Q5 behavior only. |
| `python3.13 -B -m unittest tests.align.test_external_volume` | 23 tests OK in 0.006 s; existing synthetic mount/census behavior only. |
| Inline Python arithmetic with `_ols`, `student_t_quantile`, `math` | df 2; CI factor 2.665569950; SD UCB factor 4.415396443; nonzero-noise five-block example passes both proposed bounds. Counters the impossibility claim, not a hardware qualification. |
| Qualification-duration sum | 7.5 automated MBP h; 8.25 h including 45 min setup, before additional work. Catches the 6.5 h undercount. |
| Authority and endpoint dependency review | Catches loss of R12/item 215 eligibility requirements and insufficient R1/DC transfer evidence. |
| Documentation QA | Local Markdown links resolve; finding inventory is 5 HIGH / 2 MED / 1 LOW; embedded reproduction executes successfully. Final staged whitespace and two-file scope are checked before commit. |

Reproduction of the decisive arithmetic (standard library plus repo code;
no data files):

```python
import math
from joulewise.align.apple.ssd_qualification import _ols
from joulewise.analysis_engine.distributions import student_t_quantile
x = [[1., float(i), float(i % 2 == 0)] for i in range(5)]
_, inv, _, df = _ols(x, [0.] * 5)
t = student_t_quantile(.95, df)
h = t * math.sqrt(inv[2][2])
u = math.sqrt(2 / (-2 * math.log(.95)))
s = .00001  # synthetic W, not measured MBP scatter
y = [15 + .001*i + r*s/math.sqrt(5)
     for i, r in enumerate((1, -2, 0, 2, -1))]
beta, inv, s2, df = _ols(x, y)
assert abs(beta[2])*1800 + t*math.sqrt(s2*inv[2][2])*1800 < .10
assert u*math.sqrt(s2)*1800 < .60
print(df, h, u, .5 + 2.5 + 2 + 2.5, .5 + .75 + 2.5 + 2 + 2.5)
```

Full suite/compileall omitted for a docs-only review and the user's active-job
load restriction. Tests ran sequentially, under one second combined reported
test time, with bytecode writes disabled. No fixture process was launched;
the normal session-end process census was omitted to avoid inspecting the
active job under this brief's machine-safety constraints.
No network, real restricted directory, out-of-clone user path, model download,
Block-5 pipeline or machine-state mutation was used. Git reads of shared
repository objects used the user-authorized alternate store only.

## Handoff

Only two new Markdown files are in scope: this run report and the review.
Commit locally with a clear docs message; do not push. Final handoff carries
the resulting commit ID and whitespace/scope-check results.

Open decisions: lead/Ed disposition of the HIGH findings and scoped R12
supersession; endpoint-specific DC qualification; precise loss/series rules;
R1 transfer matrix; actual-device macOS/log/registry qualification; borrowed
device availability and purchased configuration. No live readiness, power
precision, enclosure behavior or timeline was established. No other agent or
external consult was invoked. The next step is the lead's adjudication of
the independent seat reports, before any native qualification is scheduled.
