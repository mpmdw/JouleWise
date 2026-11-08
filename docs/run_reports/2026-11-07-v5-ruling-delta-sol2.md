# v5-ruling-delta — Sol2 handoff

Date: 2026-11-07 (session environment date; source design/branch labels use
2026-11-08). Seat sol2. Branch:
`align/2026-11-08-v5design-ruling-delta-sol2`, already provisioned clean at
`7d2e434648303c715f1ad07c183ebccea28d57dd` when this session began.

## Assignment and authority

Review `18f35ae06..7d2e43464` and every finding in both prior Sol reviews; write
the Sol2 delta review, recompute the arithmetic in a temporary stdlib script,
and commit locally without pushing. This is the explicitly selected docs-only
[AGENT] task, not permission to select a measurement task from the older queue.
The user's blind/no-network/no-full-suite and coordination-state exclusions
override the ordinary end-of-run state-update checklist.

Mission M0 intake: read AGENTS.md, CLAUDE.md, the relevant RUN_STATE intake,
project/workspace/next-work pointers, TASK_QUEUE current/do-not-do regions,
agent_playbook M0, AGENT_PLAN source map/report protocol, orchestration review
rules, targeted decision-log policy and analysis-plan authority. No active stop
card was present. The direct assignment controls work selection. Preserve all
sealed outcomes, immutable evidence and the running blinded job; no process
inspection, hardware activity or real-data access was needed or performed.

## Deliverable and findings

Added [ruling-delta-review-sol2.md](../align/squeeze/v5-design/ruling-delta-review-sol2.md).
Verdict **SIGN_WITH_CHANGES**, four HIGH, three MED and one LOW findings.

- HIGH: unknown side-success imputation can favor the tested rule's paired gain.
- HIGH: exchangeable dates do not establish the pooled episode-rank FPR bound;
  an exact synthetic shared-date example yields 12.5% instead of 4% at m=49.
- HIGH: actual efficacy-date count/weighted variance remain unspecified; a
  mean-zero, 28-date synthetic example fits 336 attempts and gives a t-test
  rejection lower bound of 6.89% even at Holm's strictest nominal threshold.
- HIGH: actual runtime-token allowances can explain away concealed work in E;
  S's receipt components and actual-rerun/public-projection comparison still
  require an explicit deployable contract.
- MED: main ledger is correct, but the calibration cap increases reserved hours
  to 892.875 at 900 s; the all-twin cut is 208.5 h from the listed roster, not
  214.5; development S/twin billing remains ambiguous.
- MED: CAP-1's v4 throughput needs a v5 transfer/qualification rule and a dated
  resource schedule including the cap, actual clusters, all audits and scoring.
- MED: after-T3 quarantine is a good repair; bind local F/C separation, access
  history and all score ledgers before release.
- LOW: cited R12/item 214 was not available in the local RUN_STATE. No outside
  checkout or network lookup was attempted. §9 should distinguish intention,
  completed textual repair and gated work.

The review maps all 18 ranked findings (eight S1, ten S2) and the unnumbered
requirements, with quotations from the revised text. It preserves the native
hybrid and identifies what must change before signature. It does not amend
the ruling, register an estimator, adjudicate peer findings for the lead or
predict an empirical squeeze result.

## Arithmetic and verification

Executed:

```text
python3.13 -B /private/tmp/jw-v5-ruling-delta-sol2-check_arithmetic.py
PASS — ASSERTIONS PASS: literal arithmetic and synthetic counterexamples only
```

Temporary script SHA-256:
`1bec5687ccbe8de959b3c801df55bec4a40c207863f027ca4d5102f45b329315`.
No project imports or file reads; only literal counts, Decimal/Fraction,
datetime and math. Selected output is quoted verbatim in the review. Main
reserved totals recompute to **866.875 / 1,123.708333 / 1,637.375 h** at
900/1,200/1,800 s. With both additional calibration sessions they become
**892.875 / 1,157.541667 / 1,686.875 h**. Seven sessions offer 49/pair; one
whole-date loss leaves 42 for both pairs, then session 8 restores the target.

The t counterexample uses an exact discrete probability calculation, with
deterministic stdlib quadrature only for nominal Student-t critical values.
It is not measured FPR or a completed G12 simulation. Counts, dose resolution,
native replay, deployment permissions and performance projections are not
certified by the arithmetic.

Final checks are the stdlib arithmetic run, quoted-output consistency and
`git diff --cached --check` over the two added Markdown files. No source code
changed, so no unittest, compileall, full/sharded suite or MLX execution was
appropriate; the user explicitly forbade the full suite. No network, download,
analysis pipeline or real measurement read occurred. No new native test was
claimed passed. Later integrated tiny-synthetic MLX unittest modules and all
clean-machine qualification remain the lead's responsibility outside this
sandbox; confirm module paths before running them one at a time.

## Scope and next exact step

Only the requested review and this run report are repository changes.
RUN_STATE.md, TASK_QUEUE.md, docs/process/state_kernel.json,
tests/test_gen_state.py, PROJECT_STATUS.md, decision_log and RULING-DRAFT.md
were preserved. No kernel task or external integration was created. No
sub-agent or reverse consult was launched; this is the single independent
Sol2 seat. Source refs were read as local code objects only, with remote
freshness unverified. Paths printed inside source documents were text only.

The lead should disposition D1–D8, repair the four HIGH semantics, reconcile
the ledger/gates and obtain the companion independent delta judgment over
the exact revised text. If calibration/inference assumptions cannot be made
defensible within the resulting budget, redesign then. R12 authority, exact
test dates/weights and deployment receipt coverage remain explicit unknowns.

Commit: the local commit titled
`docs(align v5): review ruling revision 2 from Sol2` contains both files.
No push, merge, measurements or coordination-state writes are authorized by
this report. The final handoff supplies the resulting commit ID.
