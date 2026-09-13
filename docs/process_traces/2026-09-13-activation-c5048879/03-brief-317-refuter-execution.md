# Refuter brief — PR #317 CI-TRIM-01, EXECUTION lens (Astra high, read-only on tracked files)

SESSION_MODE: delegated
WRITE_SCOPE: []

You are in a detached review worktree at HEAD `f5f2403e` (PR #317's branch
`chore/2026-09-10-ci-trim` with origin/main `27957b60` merged in). The PR's
diff against main is `git diff 27957b60..HEAD`; the ONLY code file it changes
is `.github/workflows/ci.yml` (two docs records accompany it). You may run
commands and tests (temp dirs allowed) but must not edit tracked files; the
tree must end clean (`git status --short` empty). Never touch
`/Users/edr/code/JouleWise` (read-only use of its `.venv/bin/python3` is
allowed), any `/Users/edr/JouleWise-measurement-*` directory, or
`/Users/edr/night-custody`. `python3 -m unittest` only; no sudo; no network
(GitHub API calls are NOT available to you; say so where you would have used one).

Context: the PR body (read `gh`-less: it is quoted in
`docs/process_traces/2026-09-10-side-threads/ci-trim-01-RESUME.md` and the
seat report `ci-trim-01-seat-astra.md` beside it) claims: T1 a `fences` job
(gen_state --check, verify_receipt_histsem --require-published, CLI config
smokes, strict mock chain, tests.test_docs_freshness) on EVERY push to main and
EVERY PR, docs-only included; T2 a pure-git `changes` detector gating the
matrix `test` jobs and both exclusive calibration jobs to code-touching diffs,
where docs = `docs/**` and top-level `*.md` EXCEPT files under `docs/` with
extensions .py .sh .zsh .bash .json .jsonl .plist .toml .yaml .yml .cfg .ini or
no extension (those are code), failing OPEN (full matrix) on a zero/missing
before-sha, unavailable object, empty diff, unsupported event or detector
error, with `--no-renames`; concurrency cancel-in-progress only on
`pull_request`; T3 the `pr-fast` job deleted; T4 the zsh apt install guarded on
`/bin/zsh`; the full suite (four shards × 3.11/3.14 + both exclusive jobs) still
runs on every code-touching PR and push. The owner accepted the two open
decisions (keep the 3.14 half of the matrix; delete pr-fast) as proposed.

Try to BREAK it, in this order:
1. Parse: load the YAML with Python (`import yaml` if importable, else
   `python3 -c` with a minimal check) and list every job id, its `needs`, and
   its `if:` expression verbatim. If `actionlint` is on PATH run it and paste
   the output; if not, say so.
2. Detector adversarial cases — construct each as a concrete diff (file list)
   and trace the detector's shell logic by hand, quoting the exact lines:
   (a) a PR touching only `docs/foo/bar.py`; (b) only `docs/foo/data.json`;
   (c) a code→docs RENAME of a `.py` file into `docs/legacy/` (with
   `--no-renames`, does the deletion side count as code?); (d) top-level
   `README.md` only; (e) `tests/test_x.py` + `README.md`; (f) a push to main
   whose `before` sha is all zeros (branch creation) or unreachable (force
   push); (g) a `workflow_dispatch` or `schedule` event; (h) a diff that is
   empty; (i) a file with NO extension under `docs/` (e.g. `docs/process/foo`);
   (j) a Makefile or `pyproject.toml` at the repo root (is root code beyond
   `*.md` classified code?). For each: expected classification per the
   PR's rule vs what the YAML actually does. A mismatch that SKIPS the matrix
   for a code change is a BLOCKER; one that runs it unnecessarily is a nit.
3. Concurrency: quote the `concurrency` block; confirm cancel-in-progress is
   false/absent for `push` events and true only for `pull_request`. Explain
   with the expression, not a paraphrase.
4. Fences: confirm the `fences` job has NO `needs`/`if` that could skip it,
   and that each of the five listed steps is present with the same arguments
   the old matrix jobs used (diff the step commands old vs new; paste).
5. Suite completeness: diff the old and new matrix definitions; confirm no
   shard, Python version, or exclusive job was dropped for code-touching
   runs, and that no `unittest` selection narrowed. D-061 (no suite
   deletion) is the invariant.
6. Required-checks hazard: list the job/check NAMES that exist after this
   change vs before (old names that disappear: `pr-fast (1)`, `pr-fast (2)`,
   any renamed matrix names). The lead checks branch protection; you list the
   name delta exactly.
7. Run `python3 -m unittest tests.test_docs_freshness` (the fences job's test)
   and `python3 scripts/gen_state.py --check` in this worktree; paste result
   lines; `git status --short` must be empty.

Report (claude-codex-report/v1, genre review) as your FINAL MESSAGE: findings
tiered blocker / should-fix / nit, each with `file:line` and a concrete
failing scenario; an explicit "no blocker found" plus a one-line "checks
performed" list if none. Under 8000 bytes.
