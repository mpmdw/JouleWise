# FIX contract — PR #317 CI-TRIM-01, fix round 1 (Astra high, enforced scope)

SESSION_MODE: delegated
WRITE_SCOPE: [".github/workflows/ci.yml"]

You are in the linked worktree of branch `chore/2026-09-10-ci-trim` (HEAD
`f5f2403e`). Do NOT commit (the lead commits by pathspec). Do not touch
`/Users/edr/code/JouleWise`, any `/Users/edr/JouleWise-measurement-*` directory,
or `/Users/edr/night-custody`. No network. The only file you may write is
`.github/workflows/ci.yml`. Precedence: if this contract, the PR body and any
repository doc conflict, this contract wins; flag the conflict in your report.

Findings being fixed (refuter record 04, lead diff gate, Opus lens 07):

FIX-1 (blocker R1, concurrency). GitHub keeps at most ONE pending run per
concurrency group: a newer run in the group REPLACES a queued one even when
`cancel-in-progress` is false. Scenario: run A active on main; code push B
queued; docs push C arrives → B is cancelled, C's `B..C` diff is docs-only,
the matrix is skipped, and B's code never gets a full run. Required behavior:
every push to main gets its own run that nothing can evict; PR runs keep
ref-based cancellation. Exact shape:
```yaml
concurrency:
  group: ci-${{ github.event_name == 'pull_request' && github.ref || github.run_id }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```
Update the comment above it to state the replacement semantics in one
sentence (a queued run is replaced by a newer one in the same group).

FIX-2 (lead diff gate D1, blocker-class fence gap). 48 test modules assert on
Markdown under `docs/` and on the top-level `README.md` / `RUN_STATE.md` /
`TASK_QUEUE.md` / `AGENTS.md` / `AGENT_PLAN.md` (paper term lint, first-use
ledger, claims lint, identity pins, D-165 census, …). Under the current YAML a
docs-only change skips ALL of them; only `tests.test_docs_freshness` runs in
`fences`. Required behavior: on every run where the matrix is skipped, a job
`docs-readers` runs exactly the test modules that read documentation paths,
DERIVED AT RUN TIME (never a checked-in list), so a new docs-reading test can
never fall out of it. Exact shape:
- job `docs-readers`, `needs: changes`, `if: ${{ !cancelled() &&
  needs.changes.outputs.code != 'true' }}` (runs only when the matrix does
  not), `runs-on: ubuntu-latest`, Python 3.11, checkout with `fetch-depth: 0`,
  the same zsh guard as `test`, `compileall` as in `test`, then one `python -
  <<'PY'` step that: scans `tests/test_*.py` with the regex
  `["'](docs/|README\.md|RUN_STATE\.md|TASK_QUEUE\.md|AGENTS\.md|AGENT_PLAN\.md)`
  (a literal path prefix inside a string), excludes
  `scripts/test_timings.json`'s `exclusive_modules`, prints
  `DOCS READERS selected=<n> of <total>` plus the sorted module list, refuses
  with exit 1 if zero modules are selected, partitions the selected modules
  into 2 shards with `shard_tests.partition_modules(...)` using the timing map
  exactly as the deleted `pr-fast` step did, and runs the shard with
  `shard_tests.run_units(partition, 2, index)` (the same runner `test` uses,
  so the unit-selection semantics match the full suite; if `run_units`'s
  signature differs from what `test` calls, mirror `test`'s call exactly).
  `strategy: fail-fast: false, matrix: shard: [1, 2]`, env `SHARD_INDEX`.
- A header comment (8 lines max) stating: this job is a FENCE for
  documentation-asserting tests on docs-only runs, it never substitutes for
  the full suite, and the module list is derived at run time.
At the lead's bench the derived set is 48 modules ≈ 23 hosted minutes on one
runner (one module, `tests.test_whole_window_selection`, is ≈ 500 s); two
shards is the intended shape.

FIX-3 (residual risk from record 04). If the `changes` JOB fails outright
(runner loss), `needs` skips every dependent job silently. Required: the
three gated jobs (`test`, both exclusive jobs) use
`if: ${{ !cancelled() && needs.changes.outputs.code != 'false' }}` so a
missing output (failed/skipped detector) runs the full matrix; `docs-readers`
uses the complementary `!= 'true'` form above. Keep `changes`'s own
`continue-on-error` steps and the `|| 'true'` output default as they are.

FIX-4 (nit R2). Not in your scope: the trailing whitespace at
`docs/process_traces/2026-09-10-side-threads/ci-trim-01-seat-astra.md:194` is
fixed by the lead. Do not touch it.

Do NOT change: the `classify_path` rule, the detector's diff commands, the
`fences` job, the matrix definitions, the exclusive jobs' steps, `build`,
`installed-wheel`, `gate-ledger`.

Verification you must run and paste (no network):
1. `bash -n` on every extracted `run:` block; a Python YAML parse with the
   venv interpreter `/Users/edr/code/JouleWise/.venv/bin/python3` (PyYAML is
   installed there; read-only use) listing every job id, `needs` and `if`.
2. Execute the `docs-readers` selection step's Python locally (not the tests):
   paste the `DOCS READERS selected=…` line, the two shard estimates, and the
   full sorted module list.
3. `git diff --stat` and `git status --short` (only `.github/workflows/ci.yml`
   modified).
Report (claude-codex-report/v1, genre implementation) as your FINAL MESSAGE:
what changed per FIX id, the pasted evidence, deviations, and "what the lead
should double-check". Under 8000 bytes.

## Addendum from the Opus contract lens (record 07), folded into this round

- FIX-2 rationale, sharpest case: `tests/test_magistrate_watchdog.py:1398-1418`
  reads `docs/process/MAGISTRATE_WATCHDOG.md`, extracts a fenced Python block
  and `exec`s it; `tests/test_quiet_guard.py:190-197` pins a marker in
  `docs/contracts/quiet_guard.md`. Both `.md` files classify `docs` today. The
  derived `docs-readers` job must therefore select modules by the literal
  presence of `docs/` etc. in the TEST SOURCE (as specified), which catches
  both. Do not attempt a directory allowlist instead.
- FIX-5 (nit): the comment at `.github/workflows/ci.yml:8` says "~1.6
  minutes"; the PR body's measured docs-only cost is 1.4 runner-min. Make the
  comment say "about 1.5 minutes" so neither number is asserted precisely.
- NOT yours: the decision-log addendum retiring TEST-SPEED-01 lever 2 and the
  dead `pr_fast_tier` block in `scripts/test_timings.json` are lead/owner
  items; leave both untouched.
