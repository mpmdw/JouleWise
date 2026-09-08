# 47 — ICLOUD-BACKUP-PROBE-01, Opus contract-lens refuter

Worktree `/Users/edr/code/JouleWise-wt-ref-icloud-opus`, HEAD `c3488fb8`
(two commits on `a969e526`). Read-only; no tracked file edited. The iCloud path
was never touched by this review.

Mandated run: `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise
python3 -m unittest tests.test_paper_excursion_decomposition
tests.test_paper_replay_fence tests.test_paper_round7_artifacts` →
**Ran 88 tests in 643.068s, OK, zero skips** (all-dot progress line), so the
corpus-gated `test_both_producers_are_byte_identical`
(`tests/test_paper_round7_artifacts.py:1466`) and
`test_registry_pinned_files_match` (`:268`) actually executed under the new
pins. The seat's byte-identical XD/AQ/F4 claim is corroborated on my bench.

## Findings

| id | severity | file:line | defect | demonstrating command |
|---|---|---|---|---|
| C1 | should-fix | `docs/paper/results-fill-registry.md:778,781` | Provenance chain broken by the re-pin. XS now reads "supersedes 8733ff03… from 49b258d2, #240" but the digest actually superseded is `12d0293b…`, which now appears nowhere in the registry. AS reads `3f4f4f12… (b36d1e85, #272; …)` — that commit/PR landed `e3e4355c…`, so the parenthetical attributes the *new* bytes to a commit that does not contain them. Both prior re-pins recorded the superseded digest explicitly; this one does not. | `git -C …-wt-ref-icloud-opus show HEAD~2:docs/paper/results-fill-registry.md \| sed -n '778,781p'` vs `sed -n '778,781p' docs/paper/results-fill-registry.md` |
| C2 | should-fix | `scripts/paper_excursion_decomposition.py:125`, `…anchor_correction_quantified.py:212`, `check_paper_replay_fence.py:321` | `JOULEWISE_BACKUP_ROOTS` and the 2 s budget are documented **only in code**: absent from all three USAGE docstrings, from `docs/paper/round7/fill-checklist.md:171`, from `docs/paper/fill-rehearsal-2026-08-27.md:190`, from `docs/guides/tutorial-replicate-the-calibration-bound.md:125`, and from the registry note. A replaying operator cannot learn the knob or the new failure mode. | `grep -rn "JOULEWISE_BACKUP_ROOTS" --exclude-dir=.git . \| grep -v "^./scripts\|^./tests"` → no hits |
| C3 | should-fix (fold into C2) | `scripts/paper_excursion_decomposition.py:134-172` | The budget is per *(root, call)* and covers `is_dir` + **both** globs cumulatively, not per glob. A responsive-but-slow root (>2 s total) therefore now yields **zero** candidates where it previously yielded matches. Behaviour change is real; it is nowhere recorded. | scratch `probe.py` (below): two blocked roots at 0.4 s → 0.82 s elapsed, i.e. budget per root per call |
| C4 | nit | `scripts/paper_excursion_decomposition.py:172` (and `:259`, `:368`) | `return result[0]` raises `IndexError` if the worker raises anything other than `OSError`, contradicting the docstring's "a timeout/error contributes no candidates". Fail-loud, not silent, so it cannot corrupt an artifact. | scratch `probe.py` → `non-OSError worker failure -> IndexError('list index out of range')` |
| C5 | nit | three copies, `…excursion:121-172`, `…anchor:208-259`, `…fence:317-368` | No test asserts the three copies are byte-identical. They are identical today (block sha256 `e4d4c10b8791…` in all three). Behavioural drift *is* caught, because `tests/test_check_paper_replay_fence.py:6` and `tests/test_paper_anchor_correction_quantified.py:6` re-run the whole suite against each script's own copy; only cosmetic drift is unguarded. | `for f in scripts/paper_excursion_decomposition.py scripts/paper_anchor_correction_quantified.py scripts/check_paper_replay_fence.py; do awk '/^# Kept verbatim in all three/,/^    return result\[0\]$/' $f \| shasum -a 256; done` |
| C6 | nit | `…excursion:165-168` | The `reason=os_error` branch is near-unreachable in production: CPython `Path.is_dir()` swallows `OSError`/`ValueError` and returns `False`, and `pathlib` glob suppresses walk errors. It is exercised only by mocks. Harmless overbuild; the timeout branch is the one that cures the hang. | `python3 -c "import pathlib,inspect;print(inspect.getsource(pathlib.Path.is_dir))"` |
| C7 | nit | `scripts/paper_excursion_decomposition.py:66-67` | `import math` precedes `import logging` (block otherwise alphabetical). No ruff/flake8 config in `pyproject.toml` and no lint job in `.github/workflows/`, so no CI impact. | `sed -n '64,70p' scripts/paper_excursion_decomposition.py` |
| C8 | should-fix, **out of packet** | `joulewise/calibration_ledger.py:4650-4658` + `tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl:1` | The same unbounded-iCloud hang class survives outside the three scripts: tracked fixture rows carry `custody_locator` values under `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/…`, and `_custody_state()` does `path.exists()` / `path.is_dir()` on them with no budget. Static evidence only — **not bench-verified**, I did not execute any path that would touch iCloud. Recommend a queue row, not a merge block. | `grep -rn "custody_locator" joulewise/*.py \| grep "Path("` |

## Per-question evidence

**1. Custody contract.** D-173 (`docs/contracts/paper_supply_custody.md:1-56`) governs the
`open_paper_input` seam and `configs/paper_supply/supply_map.json`; none of the three
scripts appears in that map (`grep -o … configs/paper_supply/supply_map.json` → no
matches), and none is an `ESTIMATOR_CODE_PATHS`-pinned file. So the only authority
over these bytes is the round-7 registry pin, whose rule is stated at
`docs/paper/results-fill-registry.md:769-773`: `R7_FENCED` means digest- and
field-checked by R7F with byte-identical replay — it authenticates *bytes*, and
contains no clause freezing behaviour. Precedent settles the rest: AS was re-pinned in
#272 for an exit-code change and XS in R7F-EXIT3-SEMANTICS-01, both with a dated
supersession note and both with issued values unchanged
(`results-fill-registry.md:783-785`). A discovery-only producer change with a dated
note is therefore sanctioned — but the note's established *form* records the superseded
digest, which this one drops (C1). Old digests `12d0293b…` / `e3e4355c…` appear
**only** in `docs/process_traces/…` (historical narration); no test, fixture, script, or
other doc pins them, so nothing was missed. New digests verified on the bench:
`shasum -a 256` gives `d6c683fd…` and `3f4f4f12…`, matching lines 778 and 781. The
third script (RF) is not digest-pinned anywhere.

**2. Equivalence.** Absent root: `root.is_dir()` false → `result.append(())` → `()`.
Unavailable root: timeout/OSError → `()`. Both extend the caller's list with nothing, at
the same position, so candidate order is preserved exactly. Ordering is also preserved
*within* the rewrite: the fence and excursion scripts kept unsorted glob order over
`("*", "*/*")` in that sequence; the anchor script kept `sorted()` per prefix via
`sort_matches=True` (`…anchor:283`). Side effects: the timeout/error paths emit a
`logging.warning` on a module logger with no handler, so it reaches stderr via
`lastResort` and carries no timestamp — verified in the scratch run, whose output was
the bare line `backup_root_unavailable reason=timeout root=… budget_s=0.4`. No
consumer captures that stream into a retained artifact (`fill-checklist.md` preserves
stdout/stderr only for the §7 renderer). Artifact surfaces: XD contains no
discovery-derived field (only `replay_command`, which is invocation-derived); the fence's
`--json` writes no path; **AQ does** carry `raw_powermetrics_path`
(`…anchor:513`, 15 occurrences in `docs/paper/round7/anchor-correction-quantified.json`)
and `not_rederivable_reason` (`…anchor:506`). Both are discovery-derived — but the
backup candidates are appended *after* every local corpus candidate (`…anchor:274-284`)
and the loop returns on first digest match, so with the retained corpus present a backup
can never supply bytes or a path. All 15 AQ rows are `rederivable` with local
`/Users/edr/code/JouleWise/runs_window_a*` paths, and zero `not_rederivable_reason`
strings exist. Equivalence holds for every retained artifact today.

**3. The 2 s budget.** Per root, per call, covering `is_dir` plus both globs cumulatively
(C3). A 3 s-responsive iCloud now returns `()` where it previously returned real
matches — a real backup silently skipped. It can change a retained artifact **only** on a
machine whose local corpus lacks the matching bytes, in which case AQ's
`raw_powermetrics_path`/`not_rederivable_reason` would differ. That is acceptable under
the contract, because AQ is byte-pinned (`registry:780`) and R7F/`test_registry_pinned_files_match`
fails closed on any divergence rather than letting it land silently — and the prior
behaviour on such a machine was an unbounded hang, not a better artifact. It is **not
documented** anywhere, which is the fixable half.

**4. Duplication.** No byte-identity test (C5); behavioural equivalence is covered by the
two subclass modules, which re-run all ten cases against each copy.

**5. Test isolation.** Modules touching any of the three scripts:
`tests/test_paper_excursion_decomposition.py` (override in `setUp`, `:32`),
`tests/test_paper_replay_fence.py` (import-time + `setUpModule`, `:38,:46`),
`tests/test_paper_round7_artifacts.py` (both imports + `setUpModule`, `:61,:72,:80`),
`tests/test_check_paper_replay_fence.py` and
`tests/test_paper_anchor_correction_quantified.py` (inherit the `setUp` override).
`tests/fixtures/paper_first_use_pre_cure.md` is prose, not a runner. **None is
unisolated.** No workflow, Makefile, or `release_check` step runs the producers.

**6. Overbuild / merge-ability.** Lean overall. The only prunable pieces are the
unreachable `os_error` branch (C6) and the two three-line subclass modules, which earn
their keep by covering the copies. `scripts/test_timings.json` needs no entry (unmeasured
modules take the median). No blockers.

## Verdict

**LAND-WITH-FIXES** — C1 (restore the superseded digest and correct the AS commit/PR
attribution in the two pin lines) and C2/C3 (document `JOULEWISE_BACKUP_ROOTS`, the 2 s
per-root budget, and the slow-root skip in the producers' USAGE blocks and the round-7
fill checklist). C4–C7 are nits; C8 is a follow-up queue row, not a gate on this diff.
