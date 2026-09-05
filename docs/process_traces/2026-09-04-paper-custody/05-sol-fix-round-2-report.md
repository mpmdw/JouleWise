# PAPER-CUSTODY-SEAM-01 — Sol fix round 2

Date: 2026-09-04. Base and ending commit:
`7490bf80caee37643c3e3a9bedd043f7bd6e83b0` on
`feat/2026-09-04-paper-custody-seam`. The worktree began clean. No commit was
made, and no quiet-machine or production evidence was run.

Status: **PARTIAL — F3 is cured; the authorized portions of F1 and F2 are
green, but two mandatory removals are outside the exhaustive write scope.**

## Finding → cure → evidence

| Finding | Result | Evidence |
|---|---|---|
| F1 — floor capability downgrade | Added `joulewise.inputs.load_floor_artifact`, which returns the exact `AuthenticatedFloorArtifact` produced by the authenticated loader; added its focused identity/type regression; changed the normative contract to name only this capability-preserving wire. The old exported tuple projection remains in unlisted `joulewise/analysis_engine/inputs.py`. | `joulewise/inputs.py`; `tests/test_inputs.py`; `docs/contracts/paper_supply_custody.md` |
| F2 — duplicated/non-exhaustive D-165 reason ownership | The real module now owns one immutable enumeration, derives the closed set and OR-01 map from it, and normalizes all builder source/record stops before an artifact can emit them. The producer test builds ten real refusal close-outs, checks each code against enumeration ∩ registry, mutation-checks additions to either side, and proves every refusal literal has one module home. The duplicate shim remains because its path is not allowlisted. | `joulewise/dominance_closeout.py`; `tests/test_d165_dominance_closeout.py`; `tests/test_dominance_closeout.py`; blocked: `joulewise/d165_dominance_closeout.py` |
| F3 — stale D-173 wire | Starting HEAD already contains main's `0183607a` sync: both D-173 locations say caller input is role name + runs root only. The normative contract says the same and exposes no caller path, digest, inventory, or receipt parameter. | `docs/decision_log.md:219,10914-10920`; `docs/contracts/paper_supply_custody.md:16-22,53-67,114-130` |

## Red → green record

- RED `tests.test_inputs`: import failed because `joulewise.inputs` did not
  exist.
- RED `tests.test_d165_dominance_closeout`: the real missing-sidecar-cell build
  emitted `replay_sidecar.cells: cell census does not match floor artifact`;
  refusal-literal ownership and shim-deletion assertions also failed.
- GREEN `tests.test_paper_custody`: 10 tests.
- GREEN `tests.test_authentication_io`: 21 tests.
- GREEN `tests.test_inputs`: 1 test.
- GREEN `tests.test_d165_dominance_closeout`: 50 tests.
- GREEN `tests.test_dominance_closeout`: 3 tests, including ten real refusal
  close-outs.

The repository-wide suite was not run because the task expressly forbids it.

## Required scope expansion

Requested exact paths:

1. `joulewise/analysis_engine/inputs.py`
2. `joulewise/d165_dominance_closeout.py`

Reason: its exported `load_floor_artifact` still returns
`tuple[Mapping[str, Any], str]`. The smallest completion is to return the
`AuthenticatedFloorArtifact` directly (or remove the obsolete exported
projection) and extend the already-authorized `tests/test_inputs.py` regression
to forbid the downgrade. The second path is required for the prompt-mandated
tracked deletion of the duplicate shim. No out-of-scope diff remains.

## Environment note

An initial `git rm joulewise/d165_dominance_closeout.py` attempt made no change
because the sandbox cannot create the linked-worktree Git `index.lock`. A
transient workspace deletion was restored byte-for-byte after the allowlist
audit established that the path is also absent from `WRITE_SCOPE`.
