# 12 — Lead triage of delta re-audit 07 on PR #317 fix round 1: SAME SIGNATURE → consult, not round two

Activation `24b9d3dd`, 06:40 PDT 2026-09-13. Input: Astra execution-lens delta 07 at `8819cb5f` (Opus contract-lens delta 08 pending at this write; folded in below when it lands).

| Finding | Severity | Disposition |
|---|---|---|
| R1: the run-time regex over test sources (`["'](docs/|README.md|…)`) misses 15 ordinary modules that assert documentation content through joined paths or imported path constants (e.g. `tests/test_workload_sizing.py`, `tests/test_schemas.py`, `tests/test_claims_index_lint.py` via `scripts/claims_lint.py:37`); proven by mutation (`docs-mutation=AssertionError` with the module unselected) | blocker | ESCALATED (below) |
| R2: `tests.test_calibration_exits` is an exclusive module that reads `calibration_ledger_append.md` and `window_runbook.md` and asserts on them; the docs-readers step excludes exclusive modules and the exclusive job is skipped on docs-only runs | blocker | ESCALATED (below) |
| R3: a failed detector runs both docs-readers and the full matrix | nit | accepted (fail-open by contract FIX-3; cost only) |
| FIX-1 concurrency: repaired (per-run group for pushes; modelled) | — | closed |
| FIX-3 wiring table: no completed-workflow case where neither job runs | — | closed |
| Environment parity: 48/48 imports pass on 3.11 and 3.14 in fresh venvs; steps identical to `test` except the version matrix | — | closed |

## Same-signature determination

Round 0 (refuter 07 §3 + lead D1): "a test that asserts on documentation content does not run on a docs-only push". Round 1 cure: derive the module set at run time from a regex over test sources. Delta 07: the same statement is still true for 16 modules, and the refuter's structural point stands on its own: static text over test sources cannot enumerate what tests READ, because reads go through joins, constants and helper modules. Delta's own line: "Same signature: YES".

Two consecutive rounds, same signature (rule 11 standing escalation trigger). A second fix round on the same defect is also a cold-gate mandatory trigger. The magistrate does not run round two; the next spend is a bounded design consult, then a cold gate rules the mechanism.

## The question for the consult (blind seats; license to disagree)

Can a docs-only push to main ever skip the test matrix SOUNDLY, and if so by what mechanism? Options on the table:
- (A) No skipping: drop T2's matrix gate (keep the `fences` hoist, `pr-fast` deletion, zsh guard, the per-run concurrency group). The PR's headline saving disappears; every push runs the full matrix as the kernel fence (TEST-SPEED-01: "merges keep the full suite") says today.
- (B) Skip, with a RUNTIME-TRACED reader map: the full-suite run records, per test module, every repository file it opens (an `open()`/`sys.addaudithook` trace inside `scripts/shard_tests.py`), writes `scripts/docs_readers.json`, and a code-touching run FAILS if the committed map differs from the traced one; a docs-only run runs exactly the modules whose recorded reads intersect the changed paths (plus `fences`). Staleness argument: any change to a test or to code it imports is code-touching, so the map is regenerated and checked before it is ever relied on.
- (C) Skip, with the docs class narrowed to paths that the traced map proves NO test reads (the complement of B's map) — converges with B.

Deliver from each seat: the option it recommends and why; for B/C the exact design (trace hook placement, map format, how the diff-check and the selection step work, how exclusive modules are handled, cost in runner-minutes, failure modes: conditional reads, subprocess reads, reads via `git show`, file globs); a proof sketch or counterexample for "the map cannot be stale when relied upon"; and whether the cost of B is worth it against A for a project whose priority is the paper (state the runner-minute arithmetic: full matrix ≈ 190 runner-min, docs-only ≈ 1.5 + docs-readers ≈ 23).
