# CI-TRIM-01 — resume note (durable pause, 2026-09-10 ~21:45 PDT)

Side thread run by an Opus 5 lieutenant directing one Astra seat (gpt-6-astra,
effort high). Paused before tonight's measurement window. Everything needed to
finish is in this file.

## State reached

- Branch `chore/2026-09-10-ci-trim`, based on origin/main `1d4045b4`.
- Workflow commit `b4a4cf7a` implements T1–T4 (T5 investigated, deliberately
  not applied). Only `.github/workflows/ci.yml` changed: +109 / −128.
- **DRAFT PR #317 is open** (https://github.com/mpmdw/JouleWise/pull/317).
  Its body is a placeholder and still needs the real content — see "Next step".
- **CI HAS RUN ON THE BRANCH AND IS GREEN**: run `34561804133`, conclusion
  success, 18 jobs, 22.2 min wall clock. The `changes` and `fences` jobs both
  passed and the full matrix ran (correct: the diff touches `.github/`, which
  classifies as code).
- The Astra seat COMPLETED normally (status OK, `completion=complete`, scope
  passed, only ci.yml modified). Its full report is beside this file at
  `ci-trim-01-seat-astra.md`. Nothing was killed; no partial state.

## Before-state (medians, five green runs: 34556323562, 34552826178, 34548485351, 34542312494, 34538936958)

| Job | min |
|---|---|
| build | 0.3 |
| installed-wheel | 0.2 |
| test (3.11, 1..4) | 13.7 / 18.2 / 14.4 / 20.9 |
| test (3.14, 1..4) | 11.7 / 18.3 / 12.0 / 21.0 |
| calibration-exits-exclusive (3.11 / 3.14) | 17.0 / 12.5 |
| calibration-writer-crash-matrix (3.11 1,2) | 11.6 / 5.5 |
| calibration-writer-crash-matrix (3.14 1,2) | 8.0 / 4.1 |
| pr-fast (1 / 2), PRs only | 12.8 / 19.9 |

Totals: **222.1 runner-min per code PR**, ~189.4 per push to main, 17 jobs,
~21–33 min wall clock.

**The dominant waste:** 19 of the last 20 pushes to main were docs-only
bookkeeping commits, and each ran the entire ~189-minute matrix.

## After-state (branch run 34561804133, green)

changes 0.3 · fences 0.8 · build 0.3 · installed-wheel 0.2 · test 3.11
14.3/21.0/15.2/17.9 · test 3.14 15.5/21.2/17.9/13.5 · cal-exits 18.8/11.5 ·
crash-matrix 11.0/6.0/8.0/4.0 = **197.4 runner-min, 22.2 min wall**.

- Code PR: 222.1 → 197.4 runner-min (−11%). Wall clock unchanged (~22 min); it
  is set by the longest shard, which this trim does not touch. Hosted shard
  variance is ±3 min, so treat the per-shard deltas as noise, not signal.
- **Docs-only push: ~189 → ~1.6 runner-min** (changes + fences + build +
  installed-wheel only). This is the real win and it is where 19/20 of main's
  traffic lives.
- NOT YET PROVEN LIVE: the docs-only skip path. The commit carrying this note
  is itself docs-only, so **the CI run triggered by it is the live proof** —
  whoever resumes should open that run and confirm the eight `test` shards and
  both exclusive calibration jobs show as skipped while `fences` still runs.

## The five contracts

- **T1 IMPLEMENTED** — new ungated `fences` job takes the four steps that
  previously ran identically in all eight matrix jobs (gen_state --check,
  verify_receipt_histsem, CLI config smokes, strict mock
  run/validate/reduce/revalidate) plus `tests.test_docs_freshness`, now pinned
  EXPLICITLY instead of running incidentally inside whichever shard discovery
  happened to place it. `compileall` deliberately stays per-interpreter in the
  shards. Measured cost of the whole fences job: 0.8 min.
- **T2 IMPLEMENTED** — new `changes` detector job (pure git, no third-party
  action); `test` and both exclusive jobs get `needs: changes` +
  `if: needs.changes.outputs.code == 'true'`. Docs = `docs/**` and top-level
  `*.md`; everything else is code. Fails OPEN on zero/missing before-sha,
  unavailable object, empty diff, unsupported event, and checkout or detector
  error. `--no-renames` so moving code into `docs/` still counts the deleted
  code path.
- **T3 IMPLEMENTED** — `pr-fast` deleted. Its own header defines it as a
  ~4-minute additive signal that is explicitly NOT a gate and must never become
  a required check, so no fence is lost. It had drifted to 12.8 and 19.9 min
  against a full matrix finishing in ~22 — it was no longer early signal, just
  two more 20-minute jobs per PR. `scripts/test_timings.json` still carries the
  now-unreferenced `pr_fast_tier` block (left alone: out of the seat's scope).
- **T4 IMPLEMENTED** — zsh apt install guarded on `/bin/zsh`. The guard tests
  the absolute path rather than `command -v zsh` because the tests invoke
  `/bin/zsh` directly, so a `/usr/bin/zsh` with no symlink must still install.
- **T5 INVESTIGATED, NOT APPLIED** — dropping `fetch-depth: 0` from the two
  exclusive calibration jobs. The seat found both modules build independent
  fixture repos, but their imported validator reaches `arm_readiness`, which
  does historical git replay. Transitive history-independence was not
  established, so the conservative option was taken. Correctness beat the
  saving. Re-open only with real evidence.

## Fences that must survive (verified present)

1. Full suite runs once, in full, on every code-touching PR and push to main —
   `test` matrix (both interpreters, 4 shards) + both exclusive jobs. Nothing
   deleted from the suite, no shard dropped.
2. `scripts/gen_state.py --check` on EVERY push and PR incl. docs-only —
   `fences`.
3. `tests/test_docs_freshness.py` on EVERY push and PR incl. docs-only —
   `fences` (now explicit).
4. `verify_receipt_histsem.py --require-published` — `fences`.
5. CLI smoke + strict mock chain — `fences`.
6. build + installed-wheel behavioral smokes — unchanged, ungated.

## The 3.14 proposal — NOT IMPLEMENTED, owner's call

D-017 ("CI scope", 2026-06-09) chose Python 3.11 + 3.14 and justified it as
catching "the realistic compat risks (3.11 floor vs 3.14 local) **at trivial
cost**". That cost is no longer trivial. Measured on branch run 34561804133,
the 3.14 half of the matrix is **91.6 runner-min** — test 3.14 68.1 +
cal-exits 3.14 11.5 + crash-matrix 3.14 12.0. Dropping the 3.14 duplicate to a
compile/import smoke would take a code PR from 197.4 to **~106 runner-min**,
roughly halving it.

This was deliberately NOT delegated to the seat and NOT implemented, because
amending a ruling is the owner's call, not a lieutenant's (doctrine rule 11).
The clause to amend is D-017's "at trivial cost" justification. A middle option
if the owner wants to keep compat signal: 3.11 full on PRs, 3.14 full retained
on push-to-main, so a compat break is still caught on every merge, just
post-merge.

## Known gaps / what a reviewer should check

- The detector's live behavior on event shapes that could not be tested
  offline: fork PRs, reopened PRs, force pushes with unavailable old objects,
  first push of a new branch. All are designed to fail open; only the first two
  are untested in anger.
- `ci.yml` has no `merge_group` trigger; the detector's unsupported-event
  fallback does not make the workflow run for merge-queue events.
- Branch protection on `main` is OFF and there are no required status checks
  (verified via the GitHub API 2026-09-10), so a skipped job cannot wedge a
  merge on a pending required check. If protection is ever enabled, re-examine
  T2: required checks + conditional jobs need the skip-gate pattern.
- If the `changes` job itself dies at the infrastructure level, dependent jobs
  SKIP rather than run. The run still goes red (so it is visible, not silently
  green), but `if: always() && needs.changes.outputs.code != 'false'` would
  make it fail open at the job level too. Judged a non-blocker; worth a look.
- PyYAML was unavailable in the seat's sandbox, so the YAML parse was never run
  locally — the hosted green run is what validates it.

## Next step for whoever resumes, in order

1. Open the CI run for the docs-only commit that carries this note and confirm
   the heavy jobs skipped while `fences` ran. Record the runner-minutes.
2. Spawn ONE Fable 5.1 read-only review seat (Agent tool, model `fable`) over
   the diff `origin/main...HEAD` with this note's fence list and duration
   tables. Ask it for: (a) every removed/narrowed job mapped to a surviving
   fence by name, (b) whether any path filter can skip a test job on a change
   the fence exists for, (c) any ruled CI shape (TEST-SPEED-01, the sharding
   and exclusive-module decisions) undone without being named, (d) every
   third-party action version-pinned, (e) whether the trim went far enough,
   with jobs named either way. It reviews; it does not edit the branch.
3. Fix every blocker it raises; re-run CI if the workflow changed.
4. Rewrite PR #317's placeholder body: before/after tables above, each
   removed/changed job with its covering fence, the 3.14 proposal, the known
   gaps, and a "Fable 5.1 review seat" heading carrying the verdict and the
   fixes made. Keep it a DRAFT; do not merge.
5. gate-ledger is red on #317 by construction (a fresh PR body has no filled
   twelve-row ledger). It is advisory, not a required check. Fill the ledger
   when the PR is taken out of draft.
