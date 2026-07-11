# CI-002 Packaging And Strictness Hardening

Date: 2026-07-11  
Branch/worktree: `impl/ci002` / `/Users/edr/code/JouleWise-wt/ci002`  
Base: `f4fd36e`  
Lane: `[AGENT]`; no quiet-machine or hardware measurement was performed.  
Commit authority: none; changes remain uncommitted.

## Outcome

CI-002 is implemented within the adjudicated footprint. The workflow now
builds distributions, installs and smokes the wheel independently of the
checkout, compiles Python sources, preserves the canonical test matrix, and
runs the complete strict mock chain. Core runtime dependencies remain empty.

The row is not closed yet. Its acceptance criterion is a green lead-side CI
run, and this offline sandbox lacks the packaging frontend/backend needed to
build a conforming local distribution.

## Workflow Diff Summary

- The existing Ubuntu Python 3.11/3.14 test matrix now runs
  `python -m compileall -q joulewise tests` before the canonical suite.
- The former non-strict mock smoke is now the exact chain:
  `run -> validate-bundle --strict -> reduce -> validate-bundle --strict`.
- A separate `build` job installs the CI-only `build` frontend, runs
  `python -m build` (wheel plus sdist), and uploads `dist/` as a required
  artifact.
- A dependent `installed-wheel` job deliberately performs no checkout. It
  downloads the distributions, creates a disposable venv, installs the wheel
  with `--no-deps`, changes to `$RUNNER_TEMP`, and runs
  `python -m joulewise --help` outside the repository.
- `pyproject.toml` now declares `setuptools.build_meta` with
  `setuptools>=61`. `[project].dependencies` remains `[]`; no console script,
  optional extra, macOS job, Ruff, coverage gate, retry, or rerun was added.

## Local Verification

Baseline M0 suite before edits:

```text
Ran 1041 tests in 70.055s
OK (skipped=13)
```

Static configuration and syntax checks:

```text
pyproject static contract: OK
workflow YAML syntax: OK
workflow static contract: OK
```

The TOML check asserted the exact build-system table, empty runtime
dependencies, and absence of `[project].scripts`. Ruby's standard YAML parser
accepted the workflow. A separate workflow contract check asserted every
required command, both strict validations, and absence of the prohibited
macOS/Ruff/coverage/retry surfaces. `git diff --check` passed.

`python3 -m compileall -q joulewise tests` passed with no output.

Exact strict mock chain:

```text
bundle: /tmp/jw-ci002-strict.29NPeo/example-mock-local status=succeeded
valid bundle: /tmp/jw-ci002-strict.29NPeo/example-mock-local
bundle: /tmp/jw-ci002-strict.29NPeo/example-mock-local status=succeeded
valid bundle: /tmp/jw-ci002-strict.29NPeo/example-mock-local
```

The four lines are respectively `run`, first strict validation, `reduce`, and
second strict validation. All commands exited zero.

Final canonical suite, written unpiped to `/tmp/ci002-canonical.txt`:

```text
Ran 1041 tests in 69.067s
OK (skipped=13)
```

The expected retained-corpus and sandbox-localhost acceptance gates skipped
loudly; neither is part of this workflow-only diff.

## Offline Packaging Constraint

The required local command was attempted first and failed before any build:

```text
$ python3 -m build
/opt/homebrew/opt/python@3.13/bin/python3.13: No module named build
```

An offline pip-wheel fallback was preflighted with both build isolation and
index access disabled. The preflight stopped because Python 3.13 has no
setuptools installation. The only other local setuptools is version 58.0.4
under unsupported Python 3.9, below the declared PEP 621-capable
`setuptools>=61` requirement. It was not used to manufacture a misleading
artifact. Consequently, local wheel/sdist creation and disposable-venv wheel
installation are deferred rather than reported as passes.

## Lead-Side CI Validation

Before closing CI-002, the lead must require one green workflow run proving:

1. `python -m build` emits both `*.whl` and `*.tar.gz` into the uploaded
   `python-distributions` artifact.
2. The no-checkout `installed-wheel` job installs the wheel with `--no-deps`
   in its fresh venv and passes `python -m joulewise --help` from
   `$RUNNER_TEMP`.
3. Compileall, canonical tests, config smokes, and the complete strict mock
   chain pass on both Python 3.11 and 3.14.

No phase-exit checklist row exists for CI-002, so no checklist status was
changed. The queue row must remain implemented/pending until the CI evidence
exists.

During final review, `origin/main` advanced from the requested base to
`4eac0f6` through two advisor/site-refresh commits. They do not touch the
CI-002 production or bookkeeping files. This branch remains intentionally
based on `f4fd36e`; no unauthorized merge or rebase was performed.
