# env/ — environment lock artifacts (REPRO-1)

Spec: `docs/specs/c027/doc-009_repro-001_authority_and_repro.md` Part B, REPRO-1.
Created 2026-07-09 (C-027).

## What each lock covers

| Lockfile | Environment | Covers |
| --- | --- | --- |
| `mac-measurement-lock.txt` | The repo Mac measurement venv `.venv` (Python 3.13.1, macOS Apple Silicon) | The environment that produced the six strict-valid real-energy corpus bundles under `runs/` — mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1 and their transitive closure (37 pins). |
| `analysis-lock.txt` | The system `python3` (`/opt/homebrew/bin/python3`, Python 3.13.1) invoked from the repo root | The environment used for reduction/analysis runs from the repo root. It is nearly empty (JouleWise's core is stdlib-only); the `analysis` extra (matplotlib) is **not** installed in it — recorded as found. |

Note on the spec's open question 1 (analysis env identity): analysis does
NOT run inside the Mac `.venv` here — the reduction path is stdlib-only and
runs under the system python3, so the two-lockfile case holds, with the
analysis lock being (correctly) minimal.

## Regeneration commands

```sh
# Mac measurement env (from the repo root, main checkout with .venv):
.venv/bin/python -m pip freeze --exclude-editable > env/mac-measurement-lock.txt

# Analysis env (system python3, from the repo root):
python3 -m pip freeze --exclude-editable > env/analysis-lock.txt
```

After regenerating, restore each file's header comment block (freeze date,
Python/macOS versions, this rule). `--exclude-editable` keeps the editable
`joulewise` install out of the lock — the project itself is pinned by the
git commit/tag, not by pip.

## The lock-what-IS rule

Locks capture the environments **as they are** — the environments that
produced the corpus. Never upgrade, install, or "clean up" packages as part
of locking; if `pip freeze` surfaces something surprising (e.g. the
Homebrew-vendored `wheel @ file://...` line in the analysis lock), record it
verbatim. Regeneration is only legal after a deliberate, decision-logged
dependency change — which by design also invalidates the CI cross-check
against the corpus bundles until re-measured.

## Relationship to pyproject.toml

`pyproject.toml` remains the single *intent* spec: loose, installer-facing
pins (core stdlib-only; extras `analysis = ["matplotlib"]`,
`mac = ["mlx-lm>=0.31.3", "transformers<5.13"]`). The lockfiles are
*reconstruction* specs, used as pip **constraints**, never as a parallel
dependency list:

```sh
python3 -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
python3 -m pip install -c env/analysis-lock.txt -e .
```

This keeps one dependency-declaration surface (pyproject) and makes the
locks purely additive. There is no install-everything `requirements-lock`
file — constraints only.

## CI check

`tests/test_env_locks.py` asserts both lockfiles exist, are non-empty, and
that every non-comment line is `==`-pinned (or a verbatim PEP 508 direct
reference, per lock-what-IS); when the `runs/` corpus is present it also
cross-checks the mac lock's mlx and mlx-lm pins against
`runs/example-mac-mlx-local__r1/metadata.json`
(`.adapters.runtime.prepare_metadata`). The bundle does not record a
transformers version, so that leg of the spec's cross-check is not
enforceable from bundle metadata (deviation recorded).
