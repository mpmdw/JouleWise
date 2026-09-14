# Exhibit K — governing text at 27957b60

## docs/process/state_kernel.json TEST-SPEED-01 (fence + goal)
```json
{
 "acceptance": {
  "evidence": [
   "Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test",
   "Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions",
   "Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners"
  ],
  "pointer": {
   "json_pointer": "/tasks/TEST-SPEED-01/acceptance",
   "label": "TEST-SPEED-01 acceptance",
   "path": "docs/process/state_kernel.json"
  },
  "summary": "The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence."
 },
 "authority": {
  "label": "Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report",
  "path": "docs/run_reports/2026-07-28-floor-mint-implementation.md"
 },
 "fences": [
  {
   "authority": {
    "label": "D-061 zero-deletion clearance; the full suite as the authoritative gate",
    "path": "docs/decision_log.md"
   },
   "rule": "No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite"
  }
 ],
 "goal": "Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners.",
 "id": "TEST-SPEED-01",
 "status": "queued"
}
```

## Ed's acceptance (Gmail 1a0969ba0b31c2b2, 2026-09-12, quoted in c5048879 triage 13): "both pr's accepted as proposed" — the two decisions the PR body posed were: keep the 3.14 half of the matrix; delete pr-fast.

## PR #317 body at this write (gh pr view 317)
```
## CI-TRIM-01 — trim the hosted CI matrix without losing a fence (DRAFT: two decisions are Ed's)

### What this changes (only `.github/workflows/ci.yml`)
- **T1 `fences` job (new, ungated, ~0.7 min):** the four steps that previously ran identically inside all eight matrix jobs (`gen_state --check`, `verify_receipt_histsem --require-published`, the CLI config smokes, the strict mock run/validate/reduce/revalidate chain) plus `tests.test_docs_freshness`, now pinned explicitly. Runs on every push to main and every PR, docs-only included.
- **T2 `changes` detector (new, pure git):** `test` and both exclusive calibration jobs run only when the diff touches code. Docs = `docs/**` and top-level `*.md`, EXCEPT that under `docs/` any `.py .sh .zsh .bash .json .jsonl .plist .toml .yaml .yml .cfg .ini` or extensionless file is code (60 test modules read `docs/` paths — Fable review 61 GAP-1). Fails OPEN (full matrix) on a zero/missing before-sha, unavailable object, empty diff, unsupported event, or detector error; `--no-renames` so a code→docs move keeps the old code path.
- **Concurrency (Fable review 61 GAP-2, blocker, fixed at 558a9054):** superseded runs are cancelled only on `pull_request` events. On main, a later docs-only push no longer cancels a code push's full matrix and then skips it; docs pushes to main now cost ~1.4 runner-min, so queuing them is cheap.
- **T3 `pr-fast` deleted** (its own header: an additive ~4-minute signal, "NOT a gate", never a required check; it had drifted to 12.8 / 19.9 min). See decision 2.
- **T4** the zsh apt install is guarded on `/bin/zsh`. **T5** (dropping `fetch-depth: 0` from the exclusive jobs) investigated and NOT applied: the imported validator reaches `arm_readiness`, which replays git history.

### Fences that survive (verified by the Fable 5.1 review seat, record 61)
1. The full suite runs once, in full, on every code-touching PR and push to main (four shards × 3.11/3.14 + both exclusive jobs); nothing deleted from the suite (D-061). 2. `gen_state --check` on every push/PR — `fences`. 3. `test_docs_freshness` on every push/PR — `fences`. 4. `verify_receipt_histsem --require-published` — `fences`. 5. CLI smoke + strict mock chain — `fences`. 6. build + installed-wheel — unchanged, ungated.

### Measured
| | runner-min | wall |
|---|---|---|
| Code PR, before (median of 5 green runs) | 222.1 | ~22 min |
| Code PR, after (run 34561804133) | 197.4 | 22.2 min |
| Docs-only push/PR, before | ~189 | ~22 min |
| Docs-only PR, after — PROVEN LIVE, run 34701979541 (throwaway PR #328: `changes` 0.2 + `build` 0.2 + `fences` 0.7 + `installed-wheel` 0.2; test matrix and exclusive jobs SKIPPED) | **1.4** | ~1 min |

19 of the last 20 pushes to main were docs-only bookkeeping.

### Fable 5.1 review seat (record 61, 2026-09-12): FIX-FIRST → fixed
- BLOCKER GAP-2 (cancel-in-progress × path gate on main) — fixed, see Concurrency above.
- SHOULD-FIX GAP-1 (docs-resident code classified as docs) — fixed, see `classify_path`.
- SHOULD-FIX: the `pr-fast` deletion amends the Ed-ratified TEST-SPEED-01 PR-fast/full tier — now stated here as decision 2; `scripts/test_timings.json` `pr_fast_tier` and the kernel row text go stale if accepted.
- SHOULD-FIX: docs-only skip unproven — now proven (run 34701979541).
- NITS: `test_docs_freshness` runs twice on code PRs (kept: not a deletion); actions pinned by major tag.

### Decisions for Ed (this PR stays a draft until both are answered)
1. **3.14 (NOT implemented):** D-017 chose 3.11 + 3.14 "at trivial cost"; the 3.14 half now costs 91.6 of ~197 runner-min per code PR. Keep as is, or drop 3.14 to a compile/import smoke on PRs with the full 3.14 matrix kept on push-to-main (a compat break still caught on every merge, post-merge)?
2. **`pr-fast` deletion:** accept (and retire `pr_fast_tier` in `scripts/test_timings.json`, amend the TEST-SPEED-01 kernel text) or restore the job?

### Known gaps (from the resume note and review 61)
Detector behaviour on fork PRs / reopened PRs / force pushes with unavailable old objects is designed to fail open but untested in anger; no `merge_group` trigger; branch protection on main is off (no required checks), so a skipped job cannot wedge a merge — re-examine T2 if protection is enabled; if the `changes` job itself dies, dependents skip and the run goes red (visible).

### Evidence
Resume note and seat report on this branch under `docs/process_traces/2026-09-10-side-threads/`; review 61, fix report 63, proof record 64 on `bookkeeping/2026-09-12-activation-f0d28baa`. Branch CI: 34561804133 (T1–T4, green), 34563307192 (docs-only pause commit; full matrix ran because a PR event diffs the whole PR range), 558a9054's run (fix round 1, code change → full matrix).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

```
