# Sol cross-review of Claude reviewer2 — run report

Date: 2026-11-07. Desk documentation only; draft advice for the lead.
Branch: `align/2026-11-07-sol-review-claude-reviewer2`.
Base/reviewed product: `f01e47f295f36b5f77c06dd2d788bcaf88ff7f21`.

## Delivered

Created [the independent cross-review](../align/squeeze/sol/review-of-claude-reviewer2.md)
of `docs/align/squeeze/reviewer2.md`, including both verbatim seat appendices.
It gives AGREE / DISAGREE / UNVERIFIABLE dispositions for all 23 synthesized
actions, all 20 Fable actions, all 18 Opus actions, distinct substantive claims,
the reconciliation/correction tables, external-source claims and venue forecasts.
Citations expand through 32 source-key entries to exact commit/path/line
coordinates. The lead retains scientific and final admission authority.

Verdict: the direction makes v4 sounder, but literal adoption is insufficient.
The principal corrections are score-rank validity and window dependence;
direct paired physical joint-evasion evidence instead of a proxy-rate product;
detector failure versus operational abort accounting; the .05-margin P2 sizing
error; CHAIR's repeated residual-SD/MDE substitution; a complete DC/battery/
baseline/clock contract; capability-gate sizing; and monitor views that omit
system prompts and tool-call arguments even when called “full.”

## Intake, constraints and workspace

- Read repository instructions, Mission M0, orchestration, source-of-truth map,
  targeted restart/status/workspace sections, Current Queue and Do-Not-Do-Yet.
  The active stop card and global work-selection gate both said NONE.
- Classified this explicit owner request as an `[AGENT]` desk cross-review of
  the main-goal ALIGN product. Did not select a quiet-machine task or change
  the lead's queue/state. The user's explicit no-coordination-write rule
  supersedes the normal state/kernel close-out instructions.
- The exact requested branch was already provisioned and checked out at the
  reviewed product; the initial tree was clean. Preserved it and made no branch
  switch, reset, merge, worktree operation or unrelated edit.
- No fetch/network: all requested protocol/audit objects were locally available.
  No remote freshness claim. Read Git objects through normal Git operations;
  no direct traversal of the shared alternate repository.
- No path under `/Users/edr` outside this clone was opened, listed, searched or
  followed. No real `restricted/`, sealed measurement storage, night-custody,
  night-archive, analysis pipeline, model download, model execution, live
  telemetry or measurement process was used. Absolute data pointers in prose
  were never followed. Pilot numbers were checked only against unblinded
  repository narrative records explicitly named in the review.
- No agents/consults, integrations, external posting, registrations or task
  creation. RUN_STATE, TASK_QUEUE, state_kernel and test_gen_state are unchanged.

Git-source extracts were placed only in
`/private/tmp/jw-sol-review-claude-reviewer2-sources/`; they contain the selected
repository code/docs and a manifest, no measurement streams. They are not part
of the commit. No persistent verification script or generated repository file
was added.

## Verification

1. `TMPDIR=/private/tmp python3.13 -B -m unittest tests.external.test_km003c_parse.EnergyTests`
   — **PASS**, 6 tests in 0.024 s. Inspected the class first: every input is
   synthetic. The recorded-fixture test classes were not run. This checks
   integration, discharge/charge sign, missing-SMC behavior and ratios, not
   native meter accuracy or claim calibration.
2. `python3.13 -B - <<'PY' ... PY` standard-library arithmetic — **PASS**:
   verified exact conformal ranks; sample-max and iid-binomial reference bounds;
   19-of-21 yield probabilities; six-window calibration allocation; dependence
   counterexamples; the .05-margin sizing correction; 40-episode/28-cell budget.
   The key reproducible expressions are below. They require no repo imports,
   measurements, weights or network.
3. `python3.13 -B - <<'PY' ... PY` source/citation/coverage validator — **PASS**:
   32 source entries resolve with `git show`; all 585 citation anchors/ranges lie
   within their named source blob; synthesized actions 1–23, A1–A20 and B1–B18
   are each covered exactly once. Whitespace and final-newline checks pass.
   This is a structural citation check; semantic source comparison was manual.
4. Final staged `git diff --cached --check`, exact changed-path review and
   documentation diff review — **PASS** before commit. Only the two files in
   this report are included.

No full/sharded suite or compileall: this changes documentation only, and the
owner forbids the full suite while the blinded job runs. No Metal/native tests
were attempted. No additional native test is required by these documentation
edits. Future DC endpoint/clock/battery qualification, enforced reasoning-budget
behavior and synchronized physical injector tests remain lead-owned work
outside this sandbox, not validation completed by this session.

```python
from math import ceil, comb, sqrt
from statistics import NormalDist

rank = lambda m: (39 * (m + 1) + 39) // 40  # exact ceil(.975*(m+1))
assert (rank(21), rank(39), rank(78), rank(79)) == (22, 39, 78, 78)
print(1 - .05**(1/20))                 # 0/20 iid upper95: .13910834
print(.1**(1/3), .1**(1/6))           # 3/3,6/6 iid lower90: .46416,.68129
print(1 - .1**(1/39))                  # iid max-tail upper90: .05733154
print([sum(comb(21, k)*(1-p)**k*p**(21-k) for k in range(19, 22))
       for p in (.05, .10, .14)])      # .91508,.64841,.42050
print(6*7, 3*7)                       # 42 total; 21 after a 3+3 split
print(1/7, 1/43)                      # six window-shared scores vs 42 iid
print(.05/sqrt(2*.1*.9/150))           # .05-margin z: 1.44338, not 2.89
z = NormalDist().inv_cdf(.95) + NormalDist().inv_cdf(.8)
print(ceil(2*.1*.9*(z/.05)**2))         # illustrative independent-arm N: 446
print(40*1800/3600, 40/(2*2*7))        # 20 hours; 1.43 episodes/grid cell
```

## Files and commit handoff

- `docs/align/squeeze/sol/review-of-claude-reviewer2.md` — source-pinned review.
- `docs/run_reports/2026-11-07-sol-review-claude-reviewer2.md` — this handoff.

Local commit message: `docs(align): independently cross-review Claude reviewer2`.
The final response records the resulting commit ID; a report cannot contain
the hash of its own commit. No push or publication was requested/performed.

## Open questions and next exact step

The lead must disposition the scientific corrections before applying the
reviewer2 action list, particularly actions 2, 3, 5, 7, 8, 13 and 23. Resolve
threat authority/D-139, measurement baseline, fit/calibration/test allocation
and exchangeability unit, primary monitor/view, primary joint-escape hypothesis,
unknown-outcome accounting and capability sample/switching rules. Keep the
existing W1 registration blockers and R1 scope intact.

Primary literature versions/quotations, current IOReport privileges, CFP dates,
Mac-time estimates and prior-seat workflow provenance remain unverified under
the offline/path constraints. The review confirms the literature audit's
internal contradiction about Token Inflation; it does not independently settle
which external version is correct. It makes no claim that a positive squeeze
result, detector performance target or venue acceptance has been achieved.
