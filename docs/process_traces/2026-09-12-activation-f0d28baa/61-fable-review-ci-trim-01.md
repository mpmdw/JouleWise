# 61 — Fable 5.1 read-only review of CI-TRIM-01 (draft PR #317)

Diff: `origin/main...origin/chore/2026-09-10-ci-trim` (1d4045b4 → b4552590):
`.github/workflows/ci.yml` (+109/−128) plus the two trace files. `new:` =
branch ci.yml line, `base:` = main ci.yml line. "Fence" = a check that must run
on every push and PR so a class of breakage cannot land unseen. "Fail open" =
when the detector cannot decide, everything runs.

## (a) Removed / narrowed → surviving fence, by name

| Removed or narrowed | Base | Survives as | Runs on |
|---|---|---|---|
| `gen_state.py --check` ×8 shards | base:34 | `fences` new:92 | push main + every PR; no `needs`/`if` (new:84–86) |
| `verify_receipt_histsem --require-published` ×8 | base:36 | `fences` new:96 | same |
| CLI `validate-config` ×2 configs ×8 | base:106–107 | `fences` new:97–100 | same |
| Strict mock run/validate/reduce/revalidate ×8 | base:108 | `fences` new:101–112 | same |
| `tests.test_docs_freshness` (incidental in a shard) | discovered | `fences` new:94, explicit; still also discovered in shards | same |
| `pr-fast` (2 shards, PRs only) | base:254–362 | Fence 1: `test` 2×4 matrix new:114–122 + both exclusive jobs new:204, 240, unchanged | code PR / code push |
| `test` + both exclusive jobs | ungated | `needs: changes` + `if: code == 'true'` new:115–116, 205–206, 241–242 | skipped on docs-only by design |
| unconditional `apt-get install zsh` | base | guard `! -x /bin/zsh`; postcondition `test -x /bin/zsh` kept new:137–142 | every shard |
| build, installed-wheel | — | unchanged, ungated new:343, 361 | every event |

All six listed fences exist and run on docs-only pushes (F2–F5 via `fences`,
F6 ungated, F1 on code). Triggers unchanged: `push: main`, `pull_request`
(new:3–6).

## (b) Path filter gaps

Classifier (new:65–70): `docs/*` → docs; any other path containing `/` →
code; top-level `*.md` → docs. So `pyproject.toml`, `configs/**`,
`tests/fixtures/**`, `scripts/test_timings.json`, `.github/**` → code. No
tracked symlinks. `--no-renames` (new:38, 44) lists old+new paths, so a
code→docs move keeps the old code path. Deletions list the deleted path.

GAP-1 (should-fix): classification is by DIRECTORY, not file kind. `docs/`
holds 48 `.py`, 181 `.json`, 20 `.sh`, 12 `.zsh`, 12 `.plist`; 60 test modules
read `docs/` paths. Worked example: edit `docs/paper/build/build_paper.py` →
docs → `tests/test_paper_build.py` (loads it, line 23) is SKIPPED and no
`fences` step covers it. Same for `docs/paper/fill-rehearsal/
select_outcome_branches.py` (test_select_outcome_branches.py:11–13, imported),
`docs/paper/figures/*.py` + `worked-examples.json` (test_paper_terms_lint),
`docs/paper/round7/*.json` (5 modules), `docs/**/*.sh` (test_preflight,
test_check_window_provenance). Deleting or moving these within `docs/` is
also docs-only. Fix: treat `docs/**/*.{py,sh,zsh,json,jsonl,plist}` as code.

GAP-2 (BLOCKER): cancel-in-progress × path gate. Group `ci-${{ github.ref }}`,
`cancel-in-progress: true` (new:12–14, pre-existing): every push to main shares
one group. Before this PR the superseding run re-ran the full matrix at the
newer head, so nothing was lost. After it: code push A starts the matrix; docs
push B lands minutes later (19/20 main pushes are docs), cancels A's run; B's
detector diffs A..B → docs-only → matrix SKIPPED. Commit A never gets its
main-branch full run, and the run is green. Fence 1 ("push to main") lost
silently. One-line fix: `cancel-in-progress: ${{ github.event_name ==
'pull_request' }}` (docs pushes now cost 1.6 min; queuing them is cheap).

Top-level `*.md`: `RUN_STATE.md`/`TASK_QUEUE.md` generated regions are
covered by `gen_state --check` (gen_state.py:812–813, 837);
`test_docs_freshness` reads README/RUN_STATE/TASK_QUEUE/PROJECT_STATUS/
AGENT_PLAN + `state_kernel.json`. No gap found.

## (c) Ruled CI shapes

Four-shard split kept (new:122); two exclusive jobs kept (new:204, 240);
3.11+3.14 in all three families (new:121, 215, crash-matrix). No
`python-version` line in the diff → the 3.14 halving is NOT implemented,
proposal only. NOT fully named (should-fix): kernel row
`/tasks/TEST-SPEED-01/acceptance` calls the PR-fast/full split "ratified", one
of Ed's three 2026-08-03 levers; deleting `pr-fast` undoes lever 2. The note
names the deletion, not that it amends a ratified lever. PR body must say so;
`scripts/test_timings.json:6–13` `pr_fast_tier` and the kernel text go stale.
D-061 zero test deletions: satisfied.

## (d) `uses:` lines

new:27, 87, 124, 217, 284, 346 `actions/checkout@v5`; new:90, 129, 220, 287,
347, 365 `actions/setup-python@v6`; new:355 `actions/upload-artifact@v5`;
new:369 `actions/download-artifact@v5`. Major tags (mutable), unchanged from
base; no new action. Nit.

## (e) Far enough / too far

`pr-fast` deletion loses no gate; its header (base:256–257): "ADDITIVE EARLY
SIGNAL. THIS JOB IS NOT A GATE AND NEVER SUBSTITUTES FOR THE FULL SUITE." At
12.8/19.9 min vs a 22-min matrix it was dead weight. Too far: GAP-1. Not far
enough: nothing material — `build`+`installed-wheel` (0.5 min) not worth
gating; T5 caution is right. The only big lever left is the 3.14 half
(91.6 of ~197 runner-min per code PR), Ed's call.

## (f) Docs-only skip proof — NOT PROVEN

`gh run list`: 34563307192 (b4552590, pull_request, success), 34561804133
(b4a4cf7a, pull_request, success). Run 34563307192: ALL 18 jobs ran, none
skipped. `changes` log: `code: .github/workflows/ci.yml`, `docs: …RESUME.md`,
`docs: …seat-astra.md`, `code=true`. On a PR the detector diffs
`origin/main...HEAD` — the whole PR, which contains the ci.yml commit. Correct
behaviour, but the note's "this run is the live proof" is wrong.
Runner-minutes 200.3 (changes 0.3, fences 0.7, build 0.4, wheel 0.2, test
137.4, cal-exits 32.8, crash 28.6); the four light jobs = 1.6 min as claimed.
Proof route: a throwaway one-docs-file branch PR'd AGAINST
`chore/2026-09-10-ci-trim` as base exercises the skip before merge.

## Verdict

BLOCKER: (1) GAP-2 cancel-in-progress × path gate on main.
SHOULD-FIX: (2) GAP-1 docs-resident code classified as docs; (3) PR body names
`pr-fast` removal as amending TEST-SPEED-01 lever 2 + queue `pr_fast_tier`/
kernel cleanup; (4) docs-only skip unproven — run the throwaway-PR proof.
NITS: (5) `test_docs_freshness` runs twice on code PRs; (6) major-tag pins.

FIX-FIRST. The 3.14 question for Ed (unimplemented): does D-017's "at trivial
cost" still hold when the 3.14 half is 91.6 of ~197 runner-min per code PR, or
should 3.14 drop to a compile/import smoke on PRs with full 3.14 kept on
push-to-main?
