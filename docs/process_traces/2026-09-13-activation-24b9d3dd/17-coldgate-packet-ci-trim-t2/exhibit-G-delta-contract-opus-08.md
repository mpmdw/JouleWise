# 08 — Delta re-audit, PR #317 fix round 1, CONTRACT lens (Opus 5, read-only)

Worktree `/Users/edr/code/JouleWise-wt-ref-317` @ `8819cb5f`; delta
`f5f2403e..8819cb5f` (ci.yml +77/−8 plus the R2 whitespace nit; `git diff
--check a4bb8838..8819cb5f` rc=0; `git status --short` empty). YAML parsed with
PyYAML (canonical venv interpreter, read-only); `bash -n` on all `run:` blocks →
0 failures. `gh` reads available.

Job wiring: `docs-readers` `!cancelled() && …code != 'true'` (`ci.yml:130`);
`test` + both exclusive jobs `!cancelled() && …code != 'false'` (`:197`, `:287`,
`:323`); `changes`, `fences`, `build` ungated.

## Q1 — FIX-2 cures the blocker IN PART. BLOCKER residual.

Both named cases are cured. Running the shipped selection verbatim in-worktree:
`DOCS READERS selected=48 of 230`, and all 23 modules from 07 §3 are in it,
including `tests.test_magistrate_watchdog` (the `MAGISTRATE_WATCHDOG.md` reaper
`exec`) and `tests.test_quiet_guard` (the D-115 marker). No exclusive module
reads docs, so that subtraction drops nothing today.

The deciding line is the regex, `ci.yml:171`:

```python
doc_path = re.compile(r"[\"'](docs/|README\.md|RUN_STATE\.md|TASK_QUEUE\.md|AGENTS\.md|AGENT_PLAN\.md)")
```

It requires the literal `docs/` **inside one quoted string**, so it cannot see
the `Path` **join spelling** `ROOT / "docs" / …`. Fifteen modules are missed;
eleven read a real `docs/**.md` that `classify_path` labels `docs`, so on a
docs-only run neither the matrix nor `docs-readers` runs them:

| module:line | documentation file read |
|---|---|
| `test_build_capstone.py:51` | `docs/report_src/generated/rpt001_vertical_slice.md` (generated == committed, voided-results fence) |
| `test_schemas.py:630,637` | `docs/contracts/adapter_contracts.md`, `docs/decision_log.md` |
| `test_modularity.py:27` | `docs/contracts/analysis_plans.md` |
| `test_paper_build.py:25`, `test_paper_renumber_refs.py:14`, `test_paper_replay_fence.py:32,137`, `test_paper_round7_artifacts.py:38-41`, `test_dependence_sensitivity.py:34,35,510` | `docs/paper/draft-v1.md`, `draft-v2-skeleton.md`, `round7/*.md`, `results-fill-registry.md` |
| `test_workload_sizing.py:15-19` | `docs/phase_2/floor_workload_sizing.md` (pins the D-166 retirement sentences) |
| `test_midcampaign_cure_generation_docs.py:15-20` | `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` |
| `test_gen_g2_phase_d.py:18` | `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` |

(The other four — `test_env_locks`, `test_render_results_fills`,
`test_results_prose_template`, `test_run_night` — reach only `.json`/`.py` under
`docs/`, which classify `code`.) `fences` does not help: `DOC_PATHS` in
`tests/test_docs_freshness.py:22` is only `README.md`, `PROJECT_STATUS.md`,
`docs/orchestration.md`.

**Exact replacement (one line, bench-sized):**

```python
doc_path = re.compile(r"[\"'](docs/|docs[\"']|README\.md|RUN_STATE\.md|TASK_QUEUE\.md|AGENTS\.md|AGENT_PLAN\.md|PROJECT_STATUS\.md|CLAUDE\.md)")
```

Measured in-worktree: selection goes 48 → **63**, adding exactly the fifteen
missed modules. Related latent defect: the root-doc names are a **checked-in
list** while `classify_path` (`ci.yml:54`) treats *every* top-level `*.md` as
docs, so `ci.yml:127` ("derived at run time … can never go stale") is only half
true — a new root `.md` with a new test is a silent miss. Deriving root docs from
`git ls-files -- '*.md' ':!*/*'` would close the class.

## Q2 — FIX-1 CURES 07 §4. No residual on the reported defect.

`ci.yml:11`: `group: ci-${{ github.event_name == 'pull_request' && github.ref || github.run_id }}`.
GitHub's `A && B || C` yields `B` when `A` is truthy and `B` non-empty, else `C`;
`github.ref` is never empty. So `pull_request` → `ci-refs/pull/N/merge` with
`cancel-in-progress: true` (intended); `push` → `ci-<run_id>`, unique per run, so
the pending-replacement path that evicted queued code push B cannot exist. The
A→B→C scenario of 07 §4 / 04 R1 is closed.

Residual (nit, cost): pushes now share no group, so N rapid pushes run N full
matrices **concurrently** instead of queueing. `ci.yml:8` states GitHub's
replacement semantics but not what the config does; suggest "Pushes get a
per-run group so nothing can evict a queued run; PRs share a ref group and
cancel superseded runs."

## Q3 — The claim is NOT consistent with the fence as written; the RULING must precede the merge, the addendum prose need not.

Fence, `docs/process/state_kernel.json:6513-6516`: *"No test deletions, and the
fast tier never substitutes for a required full-suite gate: merges, whole-window
verdicts, and audited heads keep the full suite."* A docs-only merge now runs
`fences` + `docs-readers` and no matrix: it does not "keep the full suite", and
`docs-readers` is the only test execution on it — i.e. it *does* substitute, in
the only case in which it runs, so `ci.yml:126` ("never substitutes for the full
suite") is false exactly there. Operational bite on "audited heads": under
operation-loop §5 a bookkeeping docs commit pushed after review yields a green
head with no matrix behind it.

Disposition: deferring the **addendum prose** to Ed / the cold gate is right —
rule 11 forbids the magistrate amending a process rule, and this narrowing
("merges" → "code-touching merges") is one. But the **ruling must precede the
merge**: merging is itself the act that makes the ratified fence false on main,
so a post-hoc addendum is the amendment performed first and authorised after.
Ed's "accepted as proposed" does not reach it — decision 2 authorises amending
the kernel text *as a consequence of retiring `pr-fast`*, while "Fences that
survive" #1 told him the full suite still runs on everything code-touching,
without disclosing that 63 test modules assert on Markdown. Correct order: a
one-line cold-gate/owner ruling on the narrowing (~15 min), then merge, then the
addendum plus the dead `pr_fast_tier` block (`scripts/test_timings.json:6-13`).

## Q4 — PR body is still the pre-fix-round-1 text. Seven repairs.

1. Title *"(DRAFT: two decisions are Ed's)"* and *"this PR stays a draft until
   both are answered"* → "Both decisions answered by Ed 2026-09-12 (Gmail
   `1a0969ba0b31c2b2`) as proposed: keep the 3.11 + 3.14 matrix; delete
   `pr-fast`."
2. T2: *"60 test modules read `docs/` paths"* → "63 test modules read
   documentation paths (48 selected by the shipped regex; see `docs-readers`)".
3. Concurrency bullet: *"superseded runs are cancelled only on `pull_request`
   events … queuing them is cheap"* → "Every push to main gets a per-run group
   (`github.run_id`) so a newer push cannot evict a queued one; PRs keep the ref
   group with `cancel-in-progress`."
4. **"Fences that survive" #1** — *"The full suite runs once, in full, on every
   code-touching PR and push to main"* → "The full suite runs whenever the
   detector sees code. On a docs-only run the new `docs-readers` fence runs the
   documentation-asserting modules instead; it is not the full suite, and
   narrowing the TEST-SPEED-01 fence clause to code-touching merges is an
   owner/cold-gate ruling this PR does not make." Add a fence 7 for
   `docs-readers`.
5. **Measured table** — *"Docs-only PR, after … **1.4**"* is stale by ~17×.
   Bench measurement of the shipped selection: two shards at **692.1 s each**,
   i.e. **≈23.1 runner-min added**; docs-only total **≈24.5 runner-min, ~12 min
   wall** (vs ~189 / ~22 min before). Restate the row and the "19 of the last 20
   pushes were docs-only" economics off the new number.
6. Fable-seat section: *"BLOCKER GAP-2 … fixed"* → the `558a9054` fix was
   incomplete (pending-run replacement) and is superseded by the per-run group.
7. Known gaps: *"if the `changes` job itself dies, dependents skip and the run
   goes red"* → "if `changes` dies its outputs are empty and the `!cancelled() &&
   != 'false'` guards run the full matrix (fail open)." Add commit `8819cb5f` and
   this review round to Evidence.

## Q5 — New defects in the delta

- **should-fix** — `ci.yml:126` asserts `docs-readers` "never substitutes for
  the full suite"; on a docs-only merge it is the only suite execution. Reword
  to "a partial fence, not the full suite" and tie it to the Q3 ruling.
- **should-fix** — cost claim: the delta multiplies docs-only run cost by ~17
  (1.4 → ≈24.5 runner-min). Correct in fact, undisclosed in the body (Q4 #5).
- **nit** — `!cancelled()` fail-open is correct for `test`/exclusives (a failed
  `changes` yields `''`, which `!= 'false'`), but `''` is also `!= 'true'`, so a
  detector-job failure runs the matrix **and** `docs-readers` (+23 runner-min,
  duplicated). The triage's "runs only when the matrix does not" holds on every
  path but this one.
- **nit (latent)** — `docs-readers` subtracts `exclusive_modules`; neither
  current exclusive module reads docs (verified), but a future one drops
  silently. Assert that no excluded module matches `doc_path`.
- **clean** — `run_units(partitions[index-1], 2, index)` on whole-module units is
  the supported shape (`shard_tests.py:701`); the zero-selection refusal exits 1;
  every `shard_tests` call matches its signature; the step's checkout/zsh/
  compileall preamble matches `test`.

## VERDICT

**BLOCK** — deciding line `.github/workflows/ci.yml:171`: the selection regex
requires `docs/` inside a single quoted string and misses the `ROOT / "docs" / …`
join spelling, leaving 11 modules that assert on `docs/**.md` — including
`test_build_capstone.py:51` (voided results page) and the four paper-draft
fences — unrun on docs-only pushes and merges. One-line cure above (48 → 63
selected, bench-verified). Secondary merge gate: the Q3 ruling on narrowing the
TEST-SPEED-01 fence must exist before the merge. Q4's seven body repairs and
Q5's two should-fixes are AMEND-level.

**Same signature as a round-0 finding: YES** — this is 07 §3 again (a
documentation-asserting test module the gate cannot reach on a docs-only run),
now via the `Path`-join spelling instead of the extension list. Under rule 11's
standing trigger a *second* failed round on this defect would force a consult,
so the cure belongs at the lead's bench (one regex line + rerun the selection),
not in a third delegated seat.
