# 07-refuter-317-contract-opus — Opus 5 contract-lens refuter (read-only; final message verbatim; 2026-09-13)

Baseline note by the lead: the brief stated origin/main `27957b60` as merged; the PR heads actually merged `a4bb8838` (H landed two minutes later). Both lenses corrected it.

## Contract-lens refuter report — PR #317 (CI-TRIM-01)

**Base-fact correction:** `27957b60` is *not* merged into HEAD. `git merge-base 27957b60 HEAD` = `a4bb8838`; main is one commit ahead (`27957b60` handback H). True PR base is `a4bb8838`; GitHub's file list is 3 files (`ci.yml` +126/−133, two trace `.md`). I used that base.

### 1. What CI promises as a gate
`docs/process/state_kernel.json:6510-6516` — the only fence on TEST-SPEED-01:
> `"rule": "No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite"`, authority `"D-061 zero-deletion clearance; the full suite as the authoritative gate"`.

Goal/acceptance (`:6498-6505`, `:6521`, status `"queued"`): `"the ratified PR-fast/full tier split implemented from the data"`; authority `"Ed ratification 2026-08-03 (three levers…)"`.

- **No test deletions:** upheld — the diff touches zero files under `tests/`.
- **`pr-fast` deletion:** does *not* contradict the fence (it removes the substitute, not the full suite). It *does* strand acceptance-evidence row 2 of a still-`queued` Ed-ratified task. `gen_state.py --check` passes (rc=0, run here) — it does not catch prose staleness.
- **Path-gating:** contradicts the fence's second half as written. Under the new YAML a **docs-only merge to main runs no full suite at all**. Owner email accepting "as proposed" covers what was proposed; the PR body asserts the opposite of the residue (see §3), so acceptance does not reach it.
- Note: `D-061` in `docs/decision_log.md:3334` is "Review-layer evaluation rule v2" — nothing about test deletion. The "zero deletions (D-061-clean)" phrase is in **D-101 addendum II** (`:7242`). The kernel's fence citation is a mis-pin (pre-existing, not this PR).
- **Addendum owed** (do not write): a `docs/decision_log.md` addendum to TEST-SPEED-01 retiring lever 2 (`pr-fast`) and narrowing the fence clause from "merges keep the full suite" to "code-touching merges", plus retiring `scripts/test_timings.json:6-13` `pr_fast_tier` (now dead config).

### 2. PR claims vs YAML
Supported: T1 (`ci.yml:96-124`), T2 (`:20-91`, `--no-renames` at `:65,:72`, fail-open default at `:61-76,:87-89`), T3, T4 (`:147-154`), T5 not applied (`fetch-depth: 0` retained `:231,:298`), concurrency (`:11-13`), Measured table (run 34701979541: `test` + both exclusive jobs `skipped`, wall 43 s; run 34561804133: 04:20:03→04:42:09 = 22.1 min).

**Not supported — "Fences that survive" #1**, "the full suite runs once, in full, on every code-touching PR and push to main". True only under the PR's own definition of "code". 23 test modules assert on real `docs/**.md` content (§3), so a docs-only push is code-touching in substance and gets no suite.

Nit: comment `ci.yml:8` says "~1.6 minutes"; body says 1.4.

### 3. BLOCKER — the docs/code classification premise is false for `.md`
Premise check: **51** `test_*.py` modules contain a `docs/` literal (64 counting `"docs"` joins), not 60. The extension list does cover docs-resident `.py/.json/.sh` (verified: `docs/paper/figures/build_mechanism_figures.py`, `docs/process/state_kernel.json`, `docs/process_traces/2026-08-28-live-smoke/preflight.sh` all → `code`).

But **23 modules read a real repo `docs/**.md`** and every one classifies **docs** (verified by running `classify_path` verbatim): `test_quiet_guard`, `test_magistrate_watchdog`, `test_paper_custody`, `test_paper_comparison_placements`, `test_paper_first_use_ledger`, `test_paper_terms_lint`, `test_paper_reported_energy`, `test_coldgate_charter_v3`, `test_night_gate`, `test_launcher_argv_regression`, `test_window_env_allowlist`, `test_validate_powermetrics_fiducial`, `test_receipt_histsem`, `test_d165_dominance_closeout`, `test_arm_readiness_registry`, `test_arm_readiness_schemas`, `test_partial_record_enclosure`, `test_select_outcome_branches`, `test_s0_line_audit_guard`, `test_capture_t0_step`, `test_check_window_provenance`, `test_d117_floor_qwen25_1p5b_plan`, `test_build_site_parsers`. `fences` runs only `test_docs_freshness`, whose scope is `DOC_PATHS = ("README.md", "PROJECT_STATUS.md", "docs/orchestration.md")` (`tests/test_docs_freshness.py:22`) + decision-log/bridge clause maps — none of these.

**Failing scenario (markdown-resident executable code):** `tests/test_magistrate_watchdog.py:1398-1418` reads `docs/process/MAGISTRATE_WATCHDOG.md`, splits out the reaper block, and runs `exec(compile(block, "<documented-reaper>", "exec"), {})`, asserting `receipt["verdict"] == "pass"`. Edit that fenced Python in the `.md` → classified `docs` → whole matrix skips → a broken documented reaper merges to main green, and the watchdog is the night-custody mechanism. Same shape at `tests/test_quiet_guard.py:190-197` (D-115 marker in `docs/contracts/quiet_guard.md`).

GAP-1 was closed by *extension*; the actual docs-resident code lives *inside* `.md`. Minimum cure: classify `docs/**` `.md` files that any test reads as code (allowlist from the 23 modules, or invert — treat `docs/contracts/**`, `docs/process/**`, `docs/phase_2/**`, `docs/paper/protocol/**` as code).

### 4. Concurrency on main
`ci.yml:11-13`: `group: ci-${{ github.ref }}`, `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`.

To a maintainer: **for exactly two rapid pushes, no** — the later push queues and then runs, so it gets its own full matrix. **SHOULD-FIX at three or more.** GitHub cancels a *previously pending* run in the group. Push A (docs, in progress) → push B (code, pending) → push C (docs) arrives: B is cancelled, and C's detector diffs `github.event.before` = B's sha → C sees docs-only and skips. B's code range gets **no** full matrix on any run. The `ci.yml:8-10` comment ("a later docs push must never cancel a code push's full run") is true only for in-progress runs; the pending lane still has it. Strictly better than base (base cancelled in-progress too), so not a regression — but the stated fix is incomplete.

### 5. Removed named/required checks
No branch protection on main (`gh api .../branches/main/protection` → 404 "Branch not protected"; `rulesets` → `[]`), so nothing wedges. `pr-fast` appears in no requirement doc: 0 hits in `docs/process/MAGISTRATE_WATCHDOG.md` and `docs/process/NIGHT_HANDBACK.md`; all other hits are historical process traces plus `scripts/test_timings.json:6` `pr_fast_tier` (now dead) and a comment in `tests/test_check_gate_ledger.py`.

### Verdict
- **BLOCKER** — §3, docs-resident `.md` code/pins skip the suite; concrete: `MAGISTRATE_WATCHDOG.md` reaper block.
- **SHOULD-FIX** — §1, decision-log addendum owed for lever 2 + the "merges keep the full suite" clause; `pr_fast_tier` left dead.
- **SHOULD-FIX** — §4, pending-run cancellation on main leaves an untested push range at ≥3 pushes.
- **NIT** — §2, 1.4 vs ~1.6 min; kernel fence mis-cites D-061 (pre-existing).

Checks run in-worktree: `gen_state.py --check` rc=0; `tests.test_docs_freshness` 31 tests OK; `classify_path` executed verbatim on 9 paths; `gh` reads only. **`git status --short` is empty (clean).**