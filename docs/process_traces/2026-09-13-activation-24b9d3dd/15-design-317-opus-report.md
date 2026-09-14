# 15 — Design consult, PR #317 T2 (blind seat: Opus 5, contract+execution lens)

```json
{"schema":"claude-codex-report/v1","genre":"scout","status":"findings","completion":"complete",
 "summary":"Recommend A. Runtime open()-tracing cannot see subprocess, git-object, or not-yet-existing-file reads; the fail-closed repair pulls in 120/230 modules (66% of suite seconds) and the saving collapses to ~36%.",
 "workspace":{"head":"8819cb5f","branch":null},"pathspec":[],"unowned_dirty":[]}
```

## Recommendation: **A** (drop T2's matrix gate; keep the rest of #317)

Keep the `fences` hoist, the `pr-fast` deletion, the zsh guard and the per-run
concurrency group (FIX-1). Delete the `changes` and `docs-readers` jobs and the
`if:` guards on `test` and the two exclusive jobs.

**Deciding reason.** B and C rest on one claim — *"the traced map lists every
repository file a test module depends on."* It is false here for three
independent reasons, two of which I executed, and the fail-closed repair costs
more than the saving it protects.

## The trace works — and then does not

Prototype hook (`sys.addaudithook`, `open` events, paths resolved under the
worktree root; `/tmp/opus317-trace.py`), run with the canonical `.venv` python
`-B`, cwd `JouleWise-wt-ref-317`:

```
RESULT tests.test_workload_sizing tests= 8 ok= True
REPO FILES OPENED: 15
   docs/phase_2/floor_workload_sizing.md
   joulewise/__pycache__/*.pyc, tests/__pycache__/*.pyc  (13 more)
```

B's hook *does* catch delta-07 R1's flagship miss
(`tests/test_workload_sizing.py:17` joins its path, so the committed regex
cannot see it). That is the whole of B's case.

**Counterexample 1 — subprocess reads are invisible (executed).**
`tests/test_paper_build.py:95` runs `subprocess.run([sys.executable,
CHECK_SCRIPT], cwd=ROOT)` where `CHECK_SCRIPT` is
`docs/paper/build/check_markdown.py`, which at `:499` does
`draft_path.read_text(...)` on `docs/paper/draft-v1.md` (`:17`). Same hook, that
one test:

```
RESULT tests.test_paper_build.PaperBuildTests.test_check_markdown_accepts_current_draft tests= 1 ok= True
DOCS-ISH FILES RECORDED: 0
```

A passing test whose whole assertion is about the paper draft records **zero**
documentation reads, so a docs-only push editing `docs/paper/draft-v1.md` would
skip it — the exact defect class the PR is fixing, silently reintroduced by the
fix. Census: 120 of 230 test modules match
`subprocess|Popen|sys.executable|os.system`; 62 spawn `zsh`/`sh`/`git`.

**Counterexample 2 — git-object reads open no working-tree path.**
`tests/test_axi_burst_reduce.py:126-136` runs `git archive BASE_HEAD` and
`git show BASE_HEAD:joulewise/reduce.py` with `cwd=ROOT`. Content comes from
`.git/objects`; no tracked path is `open()`ed, so no path-open trace in any
process can attribute the dependency.

**Counterexample 3 — the map can be fresh and still wrong (the staleness proof
fails).** B argues "any change to a test or to code it imports is code-touching,
so the map is regenerated before it is relied on." But the map is a function of
code **and of repository contents at trace time**. `scripts/claims_lint.py:861`
`rglob`s `*.md`/`*.tex`/`*.typ` under `docs/report_src`, `docs/slides`,
`docs/captions`, `docs/tables` (and `:770` globs `pack_dir/*.md`); it is driven
from `tests/test_claims_index_lint.py:551` by subprocess with `cwd=ROOT`. A
docs-only push that **adds** `docs/report_src/foo.md` changes no code, so the
map is provably fresh — and the new file is in nobody's recorded reads because
it did not exist at trace time. Intersection selects nothing; the
forbidden-language fence never sees it. Fresh map, lost fence.
(`tests/test_docs_freshness.py:286` globs `docs/**/*.md` but is hoisted into
`fences`; `claims_lint` is not.)

## Why the repair is not worth buying

The honest repair is fail-closed: any module that spawns a subprocess, invokes
git plumbing, or scans a directory joins every docs-only run unconditionally.
Using the committed weights in `scripts/test_timings.json`:

```
modules=230  total_suite_seconds=10829 (180 min serial)
subprocess-spawning modules=120  cost=7142 s (119 min) = 66.0% of suite
  exclusive: tests.test_calibration_exits              2036.0 s
  exclusive: tests.test_calibration_writer_crash_matrix 1990.65 s
```

Both exclusive modules spawn subprocesses, so both return to every docs-only run
(delta-07 R2 independently requires `test_calibration_exits` back anyway). A
*sound* docs-only run is ≈ 119 min single-version + 1.5 min fences ≈ **121
runner-min against the matrix's 190** — a 36% cut, not the 87% the current shape
advertises (1.5 + 23 = 24.5).

Build estimate for what B actually needs — audit hook in
`shard_tests.py:run_units`; a `sitecustomize.py` on `PYTHONPATH` to reach python
children (nothing reaches zsh/git children); `scripts/docs_readers.json`
(module → read paths + scanned directory prefixes + `always_run`); a
regeneration entrypoint; a drift check failing code-touching runs closed; a CI
selection step; the fail-closed subprocess/git/glob classifier — **12–20
seat-hours**, plus another refuter + delta-re-audit cycle (this PR has spent
two), plus a standing tax: the map changes on most code pushes, so a stale map
costs a failed run (190 runner-min) and a regenerate-and-repush, and every new
subprocess in a test is a new silent hole.

Payback: ~69 runner-min per docs-only push in the sound shape. Measured rate on
`main`, last 8 weeks, using `ci.yml`'s own `classify_path` and 10-minute commit
grouping as a push proxy: **294 of 581 pushes (50.6%) docs-only ≈ 37/week** →
~2,550 runner-min/week. That repays 16 seat-hours quickly **if runner minutes
are the binding constraint** — they are not. The binding constraints on a
paper-priority project are fence soundness and magistrate attention, and B
spends both to buy a resource that is free on public repositories and has never
blocked a night or a paper gate.

## Better option than B/C, if cost must come down (sound by construction)

1. **Coalesce bursts instead of skipping fences.** Of 581 pushes in 8 weeks,
   164 (28%) are superseded by a newer push within a 25-minute run window. A
   shared push group with `cancel-in-progress: true` reclaims ~28% of
   runner-minutes with no path classification and no read-map. Cost: per-commit
   coverage becomes per-tested-tree coverage (an evicted commit's content is a
   subset of the next tested tree; a commit later reverted is never tested
   alone). This reverses FIX-1, so it is a cold-gate ruling, not a seat's call —
   but it is the only lever that cannot lose a fence's *content* coverage.
2. **Attack the suite, not the gate.** Two modules are 4,026 s = 37% of 10,829
   suite-seconds; `WO-CRASHMATRIX-RELIABILITY` is already registered against the
   ~23-min indivisible test. Sound by construction.
3. **Push less often.** The 37/week is an artifact of per-activation bookkeeping
   commits (`docs/process_traces/**` alone is 107 of the 294); batching to one
   push per activation cuts the count with zero CI change.

C is B's complement and inherits its incompleteness: the complement of an
incomplete read set is an over-broad "inert" set, so the same three
counterexamples apply. The narrower "declare `docs/process_traces/**` inert"
idea also fails: `scripts/gen_derivation_night.py:50` pins
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` and
`tests/test_gen_g2_phase_d.py:52` asserts on it.

## What the lead should double-check

- **Whether runner minutes are billed at all.** No network here; if the repo is
  public they are free and B's whole case is latency — ~10-20 min of wall clock
  on pushes nobody waits on. Confirm before spending seat-hours on B.
- **My push-grouping proxy.** 10-minute commit gaps stand in for push events;
  the true counts are in the Actions run list (`gh api`), which I could not
  query. The 50.6% share is more robust than the absolute 37/week.
- **The 120-module subprocess census is textual** (`subprocess|Popen|
  sys.executable|os.system` over `tests/test_*.py`) — an upper bound on spawners,
  a lower bound on modules whose reads escape the hook.
- **Dangling required checks.** Removing `docs-readers`/`changes` changes the
  job set; branch-protection rules naming them would block merges.
- **`fences` alone carries docs under A** — unchanged from today, but confirm
  `gen_state.py --check`, `tests.test_docs_freshness` and
  `verify_receipt_histsem.py` are the once-per-run set the hoist intended.
