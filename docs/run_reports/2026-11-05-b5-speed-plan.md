# Block-5 speed plan, 2026-11-05

Branch `lane/2026-11-05-b5-speed-plan`, created from `origin/main`
`92026c184`. User-authorized post-release engineering; local commits only.
The brief targets a complete r2 pipeline below two hours on a 10-core M4 Air,
with a seven-worker alternative, and permits one or two measured, low-risk
changes. **The whole-pipeline target remains PROVISIONAL / unverified.**

## Result and changes

- [Speed plan](../process/b5_speed_plan.md): all 13 steps, cost classification,
  dependencies versus construction-only serialization, proposed changes/tests,
  ranked gains/risks, hash-independence/cache constraints and D-188 gates.
  Conditional schedules total 114 minutes at seven workers and 98.5 at ten.
- `joulewise/b5_analysis/dry_run.py`: step 0 now calls the existing ordered
  bulk source census instead of serially reading/discarding every source.
  Authentication, first-refusal ordering, census application and all outputs
  remain governed by the existing archive reader.
- `scripts/benchmark_b5_speed_plan.py`: bounded synthetic full-size copy/census
  profiles and joined step-0 comparisons. Baseline code comes from Git, not
  study paths. Three alternating-order pairs and separate cProfile runs.
- `tests/b5_analysis/test_speed_plan.py`: byte/digest equality, first-corrupt
  source and partial-census equality, prefix-range edge cases, and actual
  joined step-0 output/record equality against the serial reader.
- A second candidate, bracket inventory prefix indexing, was tested and then
  removed from production because its wall-time gain was not reliable. Its
  reproducible experiment remains in the benchmark. `bracket.py` is unchanged.
- Queue/kernel and run-state records retain post-release integration and the
  end-to-end runtime/equivalence gate as unfinished work. There is no phase
  exit-checklist row for this new engineering task; none is marked complete.

Runtime/test/benchmark commit: `856c5f21a` (`perf(b5): use ordered bulk source
census after release`). The following documentation commit contains this
report, plan, timing ledger and generated queue state.

## Safety and intake

M0: no active stop card/global gate; clean detached checkout at `origin/main`;
read current queue/do-not-do list, targeted RUN_STATE sections, playbook,
orchestration, D-188 through D-190 and the store/pool design comments.
The direct user request selects this bounded [AGENT] task ahead of legacy
queue work in this clone. It neither clears a machine-state gate nor grants
promotion to a study analysis. No advisor-visible claim changed, so
`PROJECT_STATUS.md` is unchanged.

The annotated tag object initially looked different from the brief's commit;
peeling it confirmed `b5/analysis-r2^{}` is exactly
`929fc65c9ce3ff82f0311d28acf76a682edd466f`. The tag and release checkout were
not changed. No study analysis, real measurement, network, quiet-Mac collection,
external integration or push was performed. External design/data locators in
repository text were not followed. Git object access through the clone's
alternate is the exception explicitly allowed in the brief.

The complete joined driver normally creates a literal `restricted/` directory.
A clarification was requested about synthetic exceptions, but no exception was
needed or assumed: only real joined **step 0** was exercised, with `RunState`
and `StepRunner` using a fresh temporary `artifacts/` directory. All fixture
and profiler work stayed under `/private/tmp/jwsol/speed-plan/tmp`.
The full analysis CLI/driver was not run. There were **zero worker processes**
in these profiles; the existing census uses four reader threads. The user's
ongoing seven-worker job was not inspected or modified.

## Measurements and equality

The definitive three-pair ledger is
[2026-11-05-b5-speed-plan-timings.json](2026-11-05-b5-speed-plan-timings.json).
Its inputs are synthetic. Expanded S2 copy/selection has 125 selected bundles,
2,375 copied files and 2,547 source files. Joined step 0 uses the established
S3/S3b three-window harness (3,766 source files), with Git-only synthetic seams.
The expanded timing-stub window is never sent to a claim consumer.

Final wall-time medians (three alternating-order pairs, seconds):

| Work | Before | After | Interpretation |
|---|---:|---:|---|
| 125-bundle source census | 1.372 | 1.085 | 20.9% faster; implemented |
| Three-window joined step 0 | 4.642 | 3.870 | 16.6% faster; implemented |
| 125-bundle copy/selection prefix candidate | 2.072 | 2.150 | No wall gain; deferred |

The paired step-0 output-map digest is
`e89797cc7ebefa70465d87a90426b284e6d2e6db2d8c953d35f3c9a5582f0d10`,
and its step-record digest is
`9a35d1698e874cc48f641f9bb68191eea696a9e1446b1b15d4d86f8c51786472`.
Both are identical before/after. The copied-file digest of the full-size
candidate is `12abeaee125a1a597bca9e3afa2238d77b386279ad5655e88f3b607ca39129bf`
on both sides. These commitments describe this synthetic run; relocated fixture
paths may change some commitments between independent runs. The ledger keeps
all pairs, CPU times, counts and remaining digest commitments.

The earlier full-size pair set found source census 2.064 → 1.262 seconds and joined
step 0 5.543 → 4.539 seconds (medians); prefix indexing 3.124 → 3.189 seconds,
with a small CPU decrease. All paired census, copied-file, selection, step
output and record digest comparisons matched exactly. Those earlier medians
explain the candidate selection; use the final ledger for the reproducible
committed benchmark's timings.

An initial whole-bracket cProfile on the unexpanded S2 window passed in about
5 seconds: ~2 seconds in acceptance arithmetic (Decimal quantiles/proofs),
~1.6 in ledger loading and ~1.4 in copy/selection. Separate final cProfiles are
under TMPDIR, with their top function tables in the committed ledger.
`py-spy` was not on PATH. No arithmetic/cache eligibility was changed.

Limitations: these are loaded-machine synthetic timings, with timing-only
strict-validation/capture seams. They do not measure production refits,
sustained fanless performance, memory pressure, or a complete pipeline. The
seven-worker study job is user-reported, not a measured covariate. An attempted
`nice -n 10` test launch printed `setpriority: Operation not permitted` but ran
its tests; subsequent commands used plain inherited scheduling. Do not compare
these seconds directly with nice-5 dry-j minutes or claim a two-hour result.

## Verification

Commands ran one at a time, with `TMPDIR=/private/tmp/jwsol/speed-plan/tmp`,
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, and Python 3.13 `-B`:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.b5_analysis.test_speed_plan` | 6 tests, OK, 35.537 s (earlier five-test version also passed) |
| `python3.13 -B -m unittest tests.b5_analysis.test_small_fixes` | 33 tests, OK, 7.352 s; existing ConfigKeyWarning |
| `python3.13 -B -m unittest tests.b5_analysis.test_release_equality.ReleaseComparisonPrimitiveTests` | 5 tests, OK |
| `python3.13 -B -m unittest tests.test_gen_state` | 44 tests, OK, 3.112 s; new task id/count registered |
| Syntax compilation of Git-listed `joulewise` / `tests` Python sources and the two new files | 733 tracked files + two new files passed; no bytecode writes; restricted paths excluded |
| Benchmark command in the plan, baseline `92026c184`, 125 bundles, three pairs, joined step 0 | Paired digest equality required by the command; final ledger linked above |

`python3.13 -B scripts/gen_state.py --check` and `git diff --check` passed.
The latest focused modules total 88 passing tests, with combined test time
under one minute; including the earlier five-test run stayed well below the
user's 20-minute limit. Final lead diff/documentation review confirmed one
runtime call-site change, no bracket/estimator/cache/pin/comparator change,
matching generated queue views, and no unrelated files staged. The expected
task id/count in `tests/test_gen_state.py` changes with the new kernel row.
The full suite was deliberately not run, per the user's load/blinding rule.
Python 3.11 and ten-worker execution were not exercised. No test's fixture
result is represented as live validation.

## Remaining work and exact next step

After the frozen release completes, integrate with sibling lane
`lane/2026-11-05-b5-post-release-fixes` item (a), then implement and measure the
three-pack bracket scheduler first. Preserve serial consumption/refusal order,
store/physics/session effects and global process/memory budgets. Follow with
issuer, sensitivity and producer preparation scheduling if measured budgets
justify them. Only the authorized post-release operator may perform the
blinded full-result comparator and full 7/10-worker timing run.

There is no science ruling requested by this lane. Open uncertainties are the
actual fraction of each real step spent in Python versus I/O/serialization,
ten-worker sustained scaling/RSS, and whether each proposed step budget is
achievable. The external D-188 design was outside the allowed read boundary;
the decision log, retrospective and in-repository implementation design were
used instead. No independent model review or network consult was performed;
the lead owns the final diff and documentation review.
