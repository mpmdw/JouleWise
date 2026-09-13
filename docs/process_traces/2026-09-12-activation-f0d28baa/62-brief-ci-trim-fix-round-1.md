# Fix-round brief — CI-TRIM-01 round 1 (Fable review 61: GAP-2 blocker, GAP-1 should-fix, nit 5)

WRITE_SCOPE: [".github/workflows/ci.yml"]

Fix-round seat in the linked worktree you were started in (branch
`chore/2026-09-10-ci-trim`, HEAD = main merged in; the workflow diff under
review is `git diff origin/main..HEAD -- .github/workflows/ci.yml`). Only the
workflow file is in scope. Never move HEAD, never push, never touch
`/Users/edr/code/JouleWise`, `/Users/edr/JouleWise-measurement-20260913-derivation`,
or `/Users/edr/night-custody`. Read first:
`../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/61-fable-review-ci-trim-01.md`
(GAP-1, GAP-2, verdict) and the branch's own resume note
`docs/process_traces/2026-09-10-side-threads/ci-trim-01-RESUME.md` (the six
fences that must survive; contracts T1–T5). PyYAML may be absent; validate
the YAML with `python3 -c "import yaml"` if available, else with a careful
re-read and `git diff --check`.

## GAP-2 (blocker) — cancel-in-progress × path gate on main
`concurrency.cancel-in-progress: true` with group `ci-${{ github.ref }}`
means a docs-only push B to main cancels code push A's matrix, then B's
detector diffs A..B → docs-only → the matrix is SKIPPED, so commit A never
gets its main-branch full run. Fix exactly: cancel only on pull_request
events (`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`),
and update the comment above it so it states the reason in plain words
(docs pushes to main now cost ~1.6 min, so queuing them is cheap; a code
push's full run must never be cancelled by a later docs push).

## GAP-1 (should-fix) — docs-resident code classified as docs
`docs/` holds 48 `.py`, 181 `.json`, 20 `.sh`, 12 `.zsh`, 12 `.plist`, and 60
test modules read `docs/` paths (e.g. `tests/test_paper_build.py` loads
`docs/paper/build/build_paper.py`). The detector must classify a changed
path as docs ONLY if it is `docs/**` or top-level `*.md` AND its file kind
is prose/data-for-humans: extensions `.md`, `.txt`, `.rst`, `.png`, `.svg`,
`.pdf`, `.jpg`/`.jpeg`, `.gif`, `.csv`? — NO: keep it fail-closed-to-code:
treat as code every `docs/**` path whose extension is one of
`.py .sh .zsh .bash .json .jsonl .plist .toml .yaml .yml .cfg .ini` (and any
path with no extension); everything else under `docs/**` and top-level
`*.md` is docs. Keep the existing fail-OPEN behaviour for zero/missing
before-sha, unavailable object, empty diff, unsupported event, and detector
error. Keep `--no-renames`. Write the rule as ONE shell function with a
comment listing the code extensions, so a reviewer can read it in one
place.

## Nit 5 (optional, only if trivially safe)
`tests.test_docs_freshness` now runs in `fences` AND inside a shard on code
PRs; if the shard run is incidental discovery, leave it (D-061: no test
deletions; a duplicated run is not a deletion). Do NOT remove it from the
shard.

## Verify
`git diff --check`; if PyYAML is importable, `python3 -c "import yaml,sys;
yaml.safe_load(open('.github/workflows/ci.yml'))"`; run the detector's shell
logic locally against three synthetic path lists (a docs-only list; a list
with `docs/paper/build/build_paper.py`; a list with `README.md` +
`docs/x.json`) by extracting the function into a scratch script under /tmp
and paste the three classifications. Do NOT commit; report `git status
--short` and `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
Exact hunks (quote), the three synthetic classifications, YAML validation
status, anything unsure. Under 6000 bytes.
