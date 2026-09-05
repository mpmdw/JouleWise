# PAPER-CUSTODY-SEAM-01 — Sol fix round 3

Date: 2026-09-04. Base and ending commit:
`3c27234e24b3de67cb1cbb03b779156cf9bec3b5` on
`feat/2026-09-04-paper-custody-seam`. The worktree began clean. No commit was
made, and no quiet-machine or production evidence was run.

Status: **COMPLETE — delta 04 F1 is cured and all permitted preflight tests are
green.**

## Finding → cure → evidence

`joulewise.analysis_engine.inputs.load_floor_artifact` now returns the frozen
`AuthenticatedFloorArtifact` produced by byte authentication, preserving its
verified digest, raw authenticated bytes, parsed value, and derived root IDs.
The authority-erasing `(Mapping, digest)` return is gone. The former private
filesystem loader was removed, and every filesystem floor read in the module
now consumes the one public capability-preserving loader. The normative
contract names that real module path.

The regression writes a valid floor artifact, loads it through the public API,
requires the authenticated capability type and verified byte digest, rejects
both Mapping/tuple identity, and proves tuple unpacking cannot recover the old
public `(Mapping, digest)` wire.

## Red → green record

- RED `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs`:
  `Ran 19 tests in 59.941s`; one expected failure because the loader returned
  `tuple[dict, str]`, not `AuthenticatedFloorArtifact`.
- GREEN `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs`:
  `Ran 19 tests in 59.381s`; `OK`.
- GREEN `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_custody tests.test_authentication_io`:
  `Ran 31 tests in 17.841s`; `OK`.
- FINAL GREEN `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs tests.test_paper_custody tests.test_authentication_io`:
  `Ran 50 tests in 76.089s`; `OK`.

The repository-wide suite was not run because the prompt expressly forbids it.

## Census and hygiene proof

`rg` finds the loader definition, its three production filesystem callers, its
export, and the focused test import/call only. It finds no private
`_load_authenticated_floor_artifact` survivor. A separate import grep finds no
module importing the deleted `joulewise/inputs.py` or
`joulewise/d165_dominance_closeout.py`. `git diff --check` passes.
