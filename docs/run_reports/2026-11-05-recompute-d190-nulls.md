# Independent recompute: blind D-190 null ruling — 2026-11-05

Branch: `lane/2026-11-05-recompute-d190-nulls`, from local `origin/main`
`92026c1849c0f053e56bdac6110c079211db2c31`. Local only; no push.
**Both continuation items complete: fresh full S10 before/after passes; n<2 null fix and synthetic probes pass.**

## Authority and intake

Read repository AGENTS/CLAUDE instructions, Mission M0, orchestration,
targeted restart/status/workspace/queue sections, and D-190. No active stop
card. The explicit brief selects this bounded agent task and forbids
coordination-state edits and the full suite. Read these branch-only documents
with `git show`, without checking out their changes:

- `origin/lane/2026-11-05-b5-release-readiness:docs/run_reports/2026-11-05-b5-release-readiness.md`
- `origin/lane/2026-11-05-b5-results-renderer:docs/process/b5_results_renderer.md`

Initial tree was clean and detached. No agents were delegated. No network,
real measurement input, or path under a `restricted/` directory was accessed.
Git's shared object store was used only for repository objects, as authorized.
No production analysis driver or quiet-machine measurement was run.

## Changed files and ruling map

| File | Change |
|---|---|
| `scripts/compare_b5_recompute.py` | Registered reason/code checking; distinct null status and counts; contrast, arm/resolution and sensitivity bindings; null-interval coverage. |
| `scripts/independent_recompute_b5.py` | Independent reason metadata for n<2 estimator values and below-minimum floor cells; aggregate floor reason propagation. No numeric arithmetic or comparison bar changed. |
| `tests/independent_recompute/test_d190_nulls.py` | Four ruling clauses, lookalikes, complete code sets, source-code vocabulary parity, nonfinite handling, counts/CLI, native-shaped contrast/floor probes and coverage. |
| `docs/process/recompute_d190_null_ruling.md` | Short DRAFT citing D-190 and the supplied blind 2026-11-05 lead ruling. |
| This report | Verification, limits and the exact remaining gate. |

1. Both values null, same registered reason and complete code set:
   `verdict=AGREE`, **`status=agree_null:<outcome>:<codes>`**. The existing
   verdict remains compatible with the renderer's gate; numeric `pass` does
   not include these rows. Each family gets an `agree_null` count when used;
   `null_agreements` records the total and counts by reason. Public stdout
   prints the total only.
2. Different codes/reasons, unknown or lookalike codes, absent codes and
   malformed code lists disagree. Source-health code vocabulary is checked
   against the registered producer vocabulary by a test. Resolution provenance
   and structural checks retain their independent role.
3. Null opposite a number disagrees even with matching metadata. Missing
   values and NaN/Infinity cannot acquire a null waiver.
4. Finite numeric pairs retain their existing bars, differences and verdicts.

The recompute carries `null_reason={"outcome": ..., "codes": [...]}` only
for independently established states. The release-side estimator mapping
requires integer n<2, `not_estimable`, and the registered causal code
`insufficient_complete_blocks`; floor mappings require refused resolutions
and their exact registered codes. A missing floor does not invent a code.
Whole null intervals bind to the already compared null endpoint row, with
the existing identity, expected-item and routing checks still required.

The draft does not enter or amend the decision log. RUN_STATE, TASK_QUEUE,
the state kernel, `tests/test_gen_state.py`, sealed analysis code/configs,
and the renderer were not edited.

## Focused verification

CPython 3.13; modules run sequentially, synthetic inputs only. No full suite.
Successful final module runs total **144 tests**; execution time is well below
the 20-minute test budget. Python 3.11 was not run here.

| Command/module | Result |
|---|---|
| `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.independent_recompute.test_d190_nulls` | 14 tests, OK |
| `tests.independent_recompute.test_comparator`, wrapper below | 28 tests, OK |
| `tests.independent_recompute.test_rc_cmp11`, wrapper below | 13 tests, OK |
| `tests.independent_recompute.test_input_gate`, wrapper below | 45 tests, OK |
| `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.independent_recompute.test_examples` | 30 tests, OK |
| `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.independent_recompute.test_archives` | 14 tests, OK |

The three existing comparator modules normally create a directory named
`restricted/`. To preserve the standing restriction, only their fresh
synthetic storage constant was redirected. The exact wrapper is below;
substitute the other module names for their separate invocations:

```sh
JW_B5_SYNTHETIC_ONLY=1 python3.13 -B - <<'PY'
import unittest
from tests.independent_recompute.test_comparator import cmp
cmp.RESTRICTED = 'dry-run/synthetic-artifacts'
module = 'tests.independent_recompute.test_comparator'
result = unittest.TextTestRunner(verbosity=1).run(
    unittest.defaultTestLoader.loadTestsFromName(module))
raise SystemExit(not result.wasSuccessful())
PY
```

Compilation: `python3.13 -B -m compileall -q -x '(^|/)restricted(/|$)'
joulewise tests scripts/compare_b5_recompute.py
scripts/independent_recompute_b5.py` — exit 0. The exclusion preserves the
directory restriction. `git diff --check` — clean.

An initial comparator check exposed an existing counterfactual monkeypatch
whose positional signature rejected the new optional keyword. The ordinary
numeric call now stays positional through a small nullable-call adapter;
the existing test source is unchanged and passes. The new interval-coverage
probe initially omitted unrelated copied block lists; it now isolates the
three leaves under test and their routing rows. Final checks above pass.

## Initial a43d84b27 probes and limits (historical)

The in-memory n=1 estimator probe records **8 null agreements**; a refused
floor probe records **7 null agreements**. These are separate assertions over
selected comparator rows, not complete zero-disagreement synthetic windows.
Changing the independent reason to a different registered code or a
lookalike produces disagreements. Null intervals lose coverage when their
comparison row disagrees.

The independent program's existing n<2 D and p placeholders remain numeric.
They still disagree with release nulls under clause 3; the test explicitly
checks the D case. Its derived df and other conditional-shape checks also
remain independent gates. This patch does **not** claim that every D-190
release will now achieve end-to-end recompute agreement. A representation
change for these placeholders is a separate follow-up, not silently included
in null equality. No study outcome or actual release readiness is inferred.

## Initial NEEDS_RULING — resolved by the continuation brief

Question: may the full S10 run access only its own freshly generated
synthetic `restricted/` directories inside this clone? The standing user rule
says **"never under any `restricted/` directory"**. The real r2 driver and
comparator use that directory layout, so the requested standard full harness
cannot run under the literal prohibition. The question was submitted through
the user-input tool and remains unanswered at this handoff.

Options considered: retain the absolute restriction and stop full-chain
execution; or allow only new, clone-local synthetic directories for this
acceptance run. Recommendation: the narrow synthetic exception. No existing
restricted material would be used. Test-only storage redirection above does
not establish the real driver's standard full-chain behavior.

Blocked work: full S10 driver at r2 → current independent recompute → current
comparator; fresh comparison/coverage totals; any additional full-chain null
window supported by the fixtures. **No fresh full-S10 totals exist for this
lane.** The readiness lane's historical 2,514/0 result is not a verification
result of this patch.

Prepared detached worktree: `.scratch-d190/r2`, tag `b5/analysis-r2`, commit
`929fc65c9ce3ff82f0311d28acf76a682edd466f`. No fixture restore or driver launch
was started. A clone-local `.git/info/exclude` entry ignores `/.scratch-d190/`.
The worktree is source preparation only; it contains no newly generated S10
custody. After an explicit exception, use the readiness lane's saved
`docs/process_traces/2026-11-05-b5-release-readiness/synthetic_run.py`, with
`JOULEWISE_B5_VDL=on`, one driver worker and clone-local scratch/cache paths,
then record fresh exits and totals here before claiming full acceptance.

Commit identity is reported by this lane's `git log` and the task reply.
The next exact step is the user's directory ruling, followed by that synthetic
acceptance sequence if allowed. All other work is ready for lead review.

## Continuation item 1 — full S10 baseline

The lead ruled blind on 2026-11-05 that fresh synthetic `restricted/`
directories under TMPDIR or this clone are allowed. This resolves the
directory early-return above. Real study custody remains prohibited. The
second supplied ruling selects the n<2 representation follow-up; it is
implemented and reported separately below. No coordination task was
registered and no lead-owned state file was edited. Mission M0 and targeted
D-190 / plan / registration authority were re-read; no active stop card.
The existing named lane was clean at `a43d84b27`. No agents were delegated.

Ran the full S10 restore → r2 real driver → unchanged `a43d84b27` recompute
→ unchanged comparator. Every final driver row is `ok`, through step 11;
`completed_without_tooling_refusal=true`. Driver, recompute and comparator
exits are **0 / 0 / 0**. The no-template renderer flag remains expected.

| Case | Comparisons | Numeric agreements | Categorical agreements | agree_null | Disagreements | Uncovered | Unmapped |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fresh baseline | 2,514 | 1,490 | 1,024 | 0 | 0 | 1,056 | 0 |

Null agreements by reason: **{}**. Coverage has 1,384 normalized paths,
328 compared, 340 named numeric/null exemption paths (a subset of the
1,056 uncovered paths), 0 unbound, 0 nonfinite and no absent sources. This
reproduces the readiness lane's **2,514 comparisons / 0 disagreements**;
its counts are not substituted for this fresh evidence. The ordinary S10
fixture does not exercise an n<2 estimator. Its lack of null agreements
is not evidence for or against that branch. Full-size meter streams remain
unexercised.

Exact invocation, from `.scratch-d190/r2`:

```sh
TMPDIR="$PWD/.scratch-s10f/tmp/baseline" JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1 JW_B5_S10_CHAIN_CACHE="$PWD/.scratch-s10f/tmp/baseline/fixtures" JOULEWISE_B5_VDL=on python3.13 -B ../../docs/process_traces/2026-11-05-recompute-d190-nulls/synthetic_run.py
```

The saved runner is byte-identical to the readiness lane's runner. The
existing joined harness supplies only its documented synthetic Git seams;
no arithmetic or program callable is replaced. One driver worker. Actual
executing r2 source is `929fc65c9ce3ff82f0311d28acf76a682edd466f`;
the record's Git anchor belongs to the synthetic harness, as before.
All restored inputs and new custody are inside the clone-local scratch
TMPDIR and are retained. The r2 tracked tree is unchanged. Local Git
exclude `/.scratch-s10f/` keeps that worktree's generated storage ignored.

Driver/setup/restore wall time: **2551.72 s**; this is synthetic acceptance
execution, separate from the bounded unittest budget, with no hardware
performance claim. The [baseline summary](../process_traces/2026-11-05-recompute-d190-nulls/baseline-summary.json)
records exact command vectors, exits, source/bar/artifact hashes, step
statuses and counts. Recompute flags are the existing intentional fixture
features: 19 archive-file-missing, 3 trace-plist-missing, 3 missing pre-bound
and 3 absent-meter flags. Comparator structure flags are empty.

Targeted baseline check: `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest
tests.independent_recompute.test_d190_nulls` — **14 tests, OK, 0.053 s**.
An initial runner setup used the wrong working directory and its launch
failed before fixture restore; the task-created misplaced files were
removed and the corrected invocation above supplied all evidence.
No network, real data, production pipeline, quiet-machine measurement,
full suite, push or merge was used.

## Continuation item 2 — registered n<2 recompute nulls

The supplied second blind lead ruling resolves the former numeric D/p
placeholder boundary: when the registered estimator does not exist,
recompute emits its registered not-estimable null, never a number.

- `scripts/independent_recompute_b5.py`: n=0/1 has null D, raw p, adjusted p
  and df; null estimator/interval values carry the independently established
  `insufficient_complete_blocks` reason. Deterministic terms are empty.
  Primary, timing-bound sensitivity, scaled allowance and LOO partner tests
  preserve nulls. Holm retains the frozen m=2 denominator and never rejects
  a null test. Numeric pairs retain the same arithmetic.
- `scripts/compare_b5_recompute.py`: the n<2 df comparison reads the emitted
  null instead of fabricating n−1. Missing df and numeric df still disagree;
  all registered reason checks and rule (3) remain. No bar was changed.
- `tests/independent_recompute/test_d190_nulls.py`: n=0/1 raw/finalized rows,
  full synthetic recompute CLI across all three bound variants, real engine
  n=1 null-shape parity, frozen-m Holm, partner n=0/1, explicit df presence,
  and injected numeric placeholders. The native contrast-field test now
  has 13 null agreements instead of the former 8.
- `tests/independent_recompute/test_examples.py`: its old Holm missing-test
  expectation was p=1; updated to null under the supplied ruling.
- Ruling draft, this report and value-free trace metadata document both
  items. No registered engine or sealed configuration was edited.

The saved [n=1 probe](../process_traces/2026-11-05-recompute-d190-nulls/null_probe.py)
runs the real independent CLI entrypoint on fresh synthetic ALPHA/BETA (n=5) and GAMMA
(n=1) archives, then compares 13 estimator fields for each of the two
contrasts to the real engine's synthetic n=1 output. Result: **26 comparisons,
0 numeric agreements, 26 agree_null, 0 disagreements**; the complete reason
count is **not_estimable:insufficient_complete_blocks = 26**.
[Probe metadata](../process_traces/2026-11-05-recompute-d190-nulls/n1-summary.json).
This is explicitly a field probe: uncovered/unmapped are **not assessed**,
not zero. It is not a full-window routing/coverage certification. The valid
full S10 chain requires at least five kept units (analysis plan §2.2), so
its ordinary issued-output fixture and this n<2 probe are reported separately.

### Final focused verification

Modules ran one at a time with this command prefix:

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$PWD/.scratch-d190/tests-tmp" python3.13 -B -m unittest <module>
```

| Module | Tests | Final result |
|---|---:|---|
| `tests.independent_recompute.test_d190_nulls` | 20 | OK |
| `tests.independent_recompute.test_examples` | 30 | OK |
| `tests.independent_recompute.test_comparator` | 28 | OK |
| `tests.independent_recompute.test_rc_cmp11` | 13 | OK |
| `tests.independent_recompute.test_hygiene` | 6 | OK |
| `tests.independent_recompute.test_input_gate` | 45 | OK |
| `tests.independent_recompute.test_archives` | 14 | OK |
| `tests.b5_analysis.test_step11_null_outcomes` | 9 | OK |

**165 tests in the eight final passing runs**, 111.090 s wall time. The
initial worked-example run failed its outdated p=1 expectation; only that
expectation was corrected before its successful rerun. Exact vectors,
individual times and the failed attempt are retained in
[tests-summary.json](../process_traces/2026-11-05-recompute-d190-nulls/tests-summary.json).
Before installing the patch, three scratch previews loaded the pending
sources into the existing test modules with `exec(compile(source,
module.__file__, 'exec'), module.__dict__)`, then used unittest's module
loader: 18/19/19 tests, all OK, 1.216/1.984/3.195 s. Those are development
checks, not the full S10 acceptance result. Including the earlier baseline
module and failed attempt, targeted test time remains far below 20 minutes.
Python 3.11 was not run.

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR="$PWD/.scratch-d190/tests-tmp" python3.13 -B docs/process_traces/2026-11-05-recompute-d190-nulls/null_probe.py docs/process_traces/2026-11-05-recompute-d190-nulls/n1-summary.json
python3.13 -B -m compileall -q -x '(^|/)restricted(/|$)' joulewise tests scripts/compare_b5_recompute.py scripts/independent_recompute_b5.py docs/process_traces/2026-11-05-recompute-d190-nulls
git diff --check
```

All exit 0. The full suite was not run, per the standing load/blinding
instruction. The full S10 driver runs are separate synthetic acceptance
executions and their wall times are recorded separately.

### Patched full S10 rerun

**PASS.** A second full restore → r2 real driver → patched recompute →
patched comparator completed in fresh
`.scratch-d190/r2/.scratch-s10f/tmp/patched/`. Every final driver step is
`ok`, through 11; `completed_without_tooling_refusal=true`. The expected
no-template renderer flag is unchanged. All three exits are **0 / 0 / 0**.
Recompute `comparison_stopped=false`; comparator structure flags are empty.

| Case | Comparisons | Numeric agreements | Categorical agreements | agree_null | Disagreements | Uncovered | Unmapped |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fresh baseline, item 1 | 2,514 | 1,490 | 1,024 | 0 | 0 | 1,056 | 0 |
| Patched full S10, item 2 | 2,514 | 1,490 | 1,024 | 0 | 0 | 1,056 | 0 |

Null agreements by reason for **each full S10 run: {}**. The n=1 probe's
separate count is **26**, all `not_estimable:insufficient_complete_blocks`;
its uncovered/unmapped totals are not assessed. No probe count is added
to either full S10 run. Both full runs match the readiness lane's 2,514
comparisons / 0 disagreements.

Both full runs have 1,384 normalized paths, 328 compared, 1,056 uncovered
(including 340 named numeric/null exemption paths), 0 unmapped, 0 unbound,
0 nonfinite and no absent sources. The entire coverage summary, every
comparison-family count and the coded bar digest match the fresh baseline.
The same intentional recompute fixture flags remain (19/3/3/3 as above).
No numerical comparison bar or D-190 engine behavior was changed.

Exact patched invocation from `.scratch-d190/r2`:

```sh
TMPDIR="$PWD/.scratch-s10f/tmp/patched" JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1 JW_B5_S10_CHAIN_CACHE="$PWD/.scratch-s10f/tmp/patched/fixtures" JOULEWISE_B5_VDL=on python3.13 -B ../../docs/process_traces/2026-11-05-recompute-d190-nulls/synthetic_run.py
```

One driver worker. Actual r2 source remains
`929fc65c9ce3ff82f0311d28acf76a682edd466f`; its tracked tree is unchanged.
Driver/setup/restore wall time is **9670.73 s**. This is not a hardware
performance comparison, and no cause is assigned to the longer runtime.
Only this task's session was polled; the existing analysis job was not
signalled or inspected. An optional process lookup was unavailable
(`pgrep`: sysmon service not found); no permission override was attempted.
The first metadata-summary attempt preceded the comparator file and failed
with FileNotFoundError; rerunning it after the runner's terminal exit 0
succeeded. No acceptance artifact was overwritten by that failed read.

[Patched metadata](../process_traces/2026-11-05-recompute-d190-nulls/patched-summary.json)
records exact child command vectors, source/bar/artifact hashes, driver
statuses and totals. The summarizer verified the recompute output's source
hash against the actual executing script. Both synthetic fixture caches,
custody roots and comparison outputs remain in ignored scratch.

### Final handoff and limits

Changed code: the independent recompute and comparator's df binding.
Changed tests: `test_d190_nulls.py` and the one superseded expectation in
`test_examples.py`. Documentation: ruling draft, this report, and the trace
runner/summarizer, n=1 probe and value-free verification summaries.

No RUN_STATE, TASK_QUEUE, state kernel, test_gen_state, registered engine,
sealed configuration or advisor-visible status file was changed. No full
suite, production pipeline, quiet-machine measurement, real data access,
network, push or merge was used. Final diff and protected-path checks pass.

Item 1 is local commit **427f0c1d7**. Item 2 is the subsequent local commit
`Emit registered n<2 nulls in independent recompute`; its hash is supplied
by the final Git log/task reply (avoiding a self-referential report commit).
No implementation question remains. Limits: Python 3.11 was not run; the
full S10 fixture has no meter stream or n<2 estimator; the n=1 probe proves
estimator-field equality, not full-window routing/coverage certification.
These are synthetic results, not study release or hardware validation.

Next exact step: the lead reviews the two continuation commits and the
updated ruling draft. Decision-log adoption, any real release, and its
live evidence/pin gates remain lead-owned.
