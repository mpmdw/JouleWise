# 26 — Merge wave 2026-09-16 (A172 → A173 → A210 → CI → A208 → render fix → histsem)

Interactive session b0ae8462, 01:26–02:05 PDT 2026-09-16. Gate per Ed's ruling (memory `ci-postmerge-ruling`): merge on a
green LOCAL full replay at the integration tree plus the quick tier on every lane head after merging main; hosted CI is
post-merge confirmation.

## Integration replay (the shared gate)

Integration tree `int/2026-09-16-merge-wave` @ `881a8d6b` = main `2944a45d` (installer, PR #341) + all lanes below.
`PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp nice -n 5 python3 scripts/shard_tests.py --workers 12 --split` in
`/Users/edr/code/JouleWise-wt-int`, working tree clean (0 lines of `git status --short`). Result (full log:
[26a](26a-integration-replay-881a8d6b.txt)):

```
WORKERS SUMMARY shards=12 modules=239 tests=6240 failures=0 errors=0 skipped=109 failed_shards=none result=PASS
Wed Sep 16 01:26:19 PDT 2026
```

## Per-lane merges (in D-181 order)

Each lane was brought up to main by `scratchpad/seats/staged/merge-wave.sh <lane>` (merge `origin/main`; on conflict take
the integration tree's already-resolved file version), then `scripts/quick_suite.py --tier quick` on the lane head, then a
bare `gh pr merge <n> --merge`.

| lane | PR | lane head after merge-up | quick tier | merge commit |
|---|---|---|---|---|
| A172 ARM-RETRY-CLASS-01 | #342 | `3cd050a3` (no conflicts) | (covered by the int replay; quick not rerun — first lane, identical tree) | `cb70e97f` |
| A173 ARM-CENSUS-IDLE-INTERACTIVE-01 | #343 | `c093373e` (runbook + NIGHT_HANDBACK from the int tree) | PASS 100 modules, 0 failures, 491.6 s | `b8b4406d` |
| A210 LEAD-MARGIN-01 | #344 | `3477455b` (runbook from the int tree) | PASS 100 modules, 0 failures, 484.2 s | `e79eac14` |
| CI-TRIM-02 + quick suite | #340 | `1a505a18` (no conflicts) | PASS 153 modules, 0 failures, 58.8 s | `bf870fed` |
| A208 FIXTURE-ORPHAN-SENTINEL-01 | #345 | `353720d2` (no conflicts) | PASS 153 modules, 0 failures, 59.1 s | `e41cb4c2` |
| render-only staged-plan fix (post-merge review R1) | #346 | `6a000fb3` (runbook §1.4: kept both the render-only block and A173's census block) | docs_freshness OK; PASS 153 modules, 0 failures, 59.4 s | `a77067cc` |
| TEST-SPEED-01 HISTSEM H1 | #347 | `b6c143cc` (no conflicts) | PASS 153 modules, 0 failures, 60.7 s | `68e5dce6` |

The 100-module quick tiers ran the integration tree's `quick_suite.py` copied into the lane worktree (the script lands
with #340); the 153-module tiers ran the lane's own copy once #340 was in main.

## Render-only fix (#346)

Seat `render-astra` (Astra high, bridge §7 baseline `mag-render-20260916` + lease) on
`fix/2026-09-16-render-only-staged-plan` from `d2cc8b5e`: `Prepared.admit`/`render` take `require_published`
(real installs = `LaunchdTarget` / no `--render-only` keep the `plan_outside_custody_root` refusal; render-only accepts
a staged plan and substitutes `<custody_root>/night_plan.json` into `@@PLAN@@`). Seat verification: both modules pass
(53 + 53), six mutation cells RED, scope-check SCOPE_OK. Lead read of the four-file diff at the bench: three call sites
consistent with the existing `isinstance(self.target, LaunchdTarget)` gating at `:427/:473`; accepted. Commit `ed5fa307`.

## Defects found in the wave itself

1. **Gate ledgers missing on seven PR bodies (#340, #342–#347).** The bodies were written with `gh pr create --body`,
   which replaces `.github/pull_request_template.md`; the `gate-ledger` workflow failed on each PR and nothing blocked
   the bare merge because main has no branch protection. Backfilled post-merge by a Fable bookkeeping agent using
   `scripts/check_gate_ledger.py`; Ed asked that it never recur — memory `pr-body-gate-ledger-required`; branch
   protection requiring the `gate-ledger` context requested from Ed (the auto-mode classifier denied the magistrate).
2. **CI queue flooded by the wave's pushes.** Eight `push`/`pull_request` runs queued behind each other; runs for
   already-merged PRs (#345, #346, #347 heads) and superseded main heads (`a77067cc`, `4f46482a`, `e41cb4c2`) were
   cancelled, keeping `68e5dce6` and the later `cf249594`.
3. **A failed `cd` in a chained command** (missing `JouleWise-wt-speed-histsem`) let a `git diff --stat` and a
   `quick_suite.py` invocation run in canonical; no state changed (verified `git status` clean, no merge commit). The
   histsem worktree was recreated as `JouleWise-wt-histsem`. Memory `bash-chain-cd-guard` applies.

## Handoff

Main `68e5dce6` + bookkeeping `4f46482a`. Handoff message sent to the headless magistrate 08ca8197 at ~02:02 PDT with an
added step (0): wait for a GREEN CI run on main before re-cloning; it re-cut `rehearsal-20260916` at `cf249594`
(t0 03:00:00 PDT, install close 02:50) and holds on CI + the bookkeeping seat's census entry. Ed's session b0ae8462
stays open for the research prospectus (idle-exempt under A173); no further detached seats until the stub is published.

## Bookkeeping (this branch)

Seat `bk-astra` (Astra high, baseline `mag-bk-20260916` + lease) closed the five lane rows (190 → 185), satisfied
REFUSAL-FAST-RETRY-01's two edges (now queued), added the DONE rows outside the generated fence, refreshed the
`test_gen_state` pins; flags F1–F7 in its report are recorded in the scratchpad (F4: the replay result was
magistrate-reported at the time — this record and 26a now carry it in the checkout).

## Addendum 02:12 PDT — stub arm ruling

CI run 35076281462 on main `68e5dce6` was still queued (hosted-runner backlog, all three jobs queued) at 02:11 with
t0 03:00 and install close 02:50. The headless magistrate asked for a ruling: (A) re-plan t0 by +60 min and keep
waiting, or (B) arm the REHEARSAL_STUB now with CI recorded as pending. Ruled **B**: the stub acquires nothing, so a
red main costs a failed rehearsal, which is what a rehearsal exists to surface; the merge gate that applied to this code
was the integration-tree replay (26a) plus the per-lane quick tiers, and Ed's ruling makes hosted CI post-merge
confirmation. Surviving condition: the first science night (the equivalence night, #316) still waits for a green CI run
on the main it is cloned from.
