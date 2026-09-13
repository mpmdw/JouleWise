# 09-refuter-329-contract-opus — Opus 5 contract-lens refuter (read-only; final message verbatim; 2026-09-13)

Baseline note by the lead: the brief stated origin/main `27957b60` as merged; the PR heads actually merged `a4bb8838` (H landed two minutes later). Both lenses corrected it.

## CONTRACT-LENS VERDICT: no blocker found (2 should-fix, 2 nits, 1 scoping correction)

### SCOPING CORRECTION — read this first (affects the parallel refuter too)
**The briefed baseline is wrong.** `27957b60` is *not* an ancestor of `ae5b09e7`; the merge parent is `a4bb8838`, and `main` is one commit ahead (`27957b60`, the 09-15 handback H). Diffing `27957b60..HEAD` therefore renders main's newest commit as a *deletion* and shows a phantom blocker: a custody deployment row `JouleWise-measurement-20260915-derivation` vanishing from `configs/production_custody_inventory.json`, plus a matching `assertEqual(6→5)` in `tests/test_arm_readiness_schemas.py:1704`. **The branch does not touch either file.** Correct base is `a4bb8838`; against it the diff is 309 R100 / 11 M / 7 A, with `tests/test_docs_freshness.py` as the *only* non-doc file. If the execution-lens refuter reports a custody-inventory regression, it is this artifact.

### 1. Runtime readers — CLEAN
Zero of the 309 moved paths appear as a literal anywhere in `joulewise/`, `scripts/`, `tests/`, `.github/`, `configs/` (658 `docs/` literals extracted and intersected against the full rename list; empty intersection). Every path code actually reads is still live, verified by `test -e`:
- `scripts/gen_state.py:30,31` → `docs/process/state_kernel.json`, `.schema.json` — LIVE; `gen_state.py --check` rc **0**.
- `joulewise/arm_readiness_evidence.py:813`, `scripts/build_site.py:32` → `docs/decision_log.md` — LIVE.
- `joulewise/detection_floor.py:140` → `2026-08-08-attribution-debate/COMMONMODE-REPLAY.md`; `scripts/render_results_fills.py:49-59` → `2026-08-07-plan-factory/lint_results_prose_template.py` + `docs/paper/results-fill-registry.md`; `scripts/build_site.py:26` → `2026-07-17-floor-extraction/extraction-verified.json`; `scripts/derive_estate_anchors.py:56`; `scripts/gen_derivation_night.py:50` — all LIVE despite pre-08-15 dates (the kernel-pin restore worked).
- Only wholesale `docs/**` enumerators in the tree are `tests/test_docs_freshness.py:48,130,286,293`. No `.github/` workflow references any moved path.

### 2. Magistrate / courier / contract docs — CLEAN
`MAGISTRATE_WATCHDOG.md`, `MAGISTRATE_RELAUNCH_PROMPT.md`, `NIGHT_COURIER_PROMPT.md`, `NIGHT_HANDBACK.md`, `docs/phase_2/derivation_night_runbook.md`, all 32 `docs/contracts/*.md` — present, none in the rename list. Cross-grepping all 309 moved paths against those files plus `state_kernel.json` yields **zero** hits (the three `STATUS.md` hits are substring false positives inside `PROJECT_STATUS.md` / `WINDOW_STATUS.md`). `docs/report_src/**` (paper source, `source_map.json`, `references.csl.json`) references zero archived paths.

### 3. Owner's ask vs delivery — faithful, with one live-pointer miss
The rule is a defensible minimal execution of "thin to necessary data, maybe a separate legacy folder": nothing deleted, one mechanical predicate, kernel-pinned exceptions restored, front door added. Nothing archived is treated as *current* by a live process — the paper, its bibliography, the kernel, and all configs are clean. Two defects:

- **SHOULD-FIX** — `RUN_STATE.md:6-9`, the intake doc's opening orientation paragraph, still cites the old paths: "The three dated restart docs `docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, and `RESUME-2026-07-28.md`…". Two of those three moved to `docs/legacy/process_traces/` and **the PR does not modify `RUN_STATE.md` at all**. Failing scenario: a relaunched magistrate follows RUN_STATE (the mandated first read) and hits two dead paths in its first paragraph. Mitigating: the same sentence labels them "point-in-time session records only", so nothing is mis-signalled as current — hence should-fix, not blocker.
- **NIT** — rule applied inconsistently to a sibling set: `RESUME-2026-07-26.md` stayed live while `-27`/`-28` were archived. It is not in `state_kernel.json` and not in the branch's own pinned-paths list, so the asymmetry looks unintended rather than pinned.

### 4. Reversibility — CLEAN, zero exceptions
All 309 renames are `R100` (pure, 100% similarity) against `a4bb8838`; `grep -E '^R[0-9]{1,2}\b'` returns nothing. The 11 modified files are 10 docs (link repairs) + the two-line test. History is intact; `git mv` back is exact.

### 5. `tests/test_docs_freshness.py` exclusion — no silent narrowing
The module docstring (lines 1-6) already scopes the guarantee: *"Bounded freshness checks for reader-facing current documentation. Dated history is intentionally out of scope."* The new `docs/legacy/` exclusion (line 290-291) sits immediately beside the pre-existing `docs/process_traces/` exclusion and is the same class of carve-out; the guard is `_dangling_decision_references`, so the only thing lost is D-ID validity inside archived history — which the docstring already disowns. **No addendum required.** I found no decision-log ID cited by this specific function (the module's D-IDs at lines 217/244/399/417 belong to unrelated assertions), so "the decision-log entry it cites" — could not verify a citation exists; the docstring is the governing statement.

- **SHOULD-FIX (undisclosed)** — `docs/specs/axi/sb_static_batch_verdict.md:200` cites `docs/process_traces/2026-07-16-axi-sb-live-probes/axi-sb-b2.jsonl`, now archived. The PR body discloses the eight `docs/paper/**` dangling lines but not this one; a spec doc's evidence pointer is contract-adjacent. (Confirmed live-area dangling refs are exactly these: 4 in `docs/paper/**`, 1 in `docs/specs/`.)
- **NIT** — PR body claims the diff base is `29dbc537`; the actual merge parent is `a4bb8838`. Update before merge.

### Checks performed
`git status --short` **empty**; `git diff -M a4bb8838..HEAD --name-status` (309 R100 / 11 M / 7 A, no sub-100 renames); 309-path × 658-literal intersection over `joulewise|scripts|tests|.github|configs`; 309-path cross-grep of the 5 process contracts + 32 `docs/contracts/*.md` + `state_kernel.json` + 7 root docs + `docs/report_src/**`; existence probe of 9 runtime-read paths; `scripts/gen_state.py --check` rc 0; `tests.test_docs_freshness` 31 OK, `tests.test_gen_state` 44 OK, `tests.test_arm_readiness_schemas` 50 OK.