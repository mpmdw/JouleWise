# 12 — Opus 5 pairing refuter (contract lens) on cold-gate ruling 10

Read-only in `/Users/edr/code/JouleWise-wt-coldgate-census` (f015ac05); every
fact below executed this session. I authored Exhibits B, G and J; where the
ruling contradicts Exhibit G I checked the file, not my earlier report.

## VERDICT: AMEND

Q1, Q2(a), Q2(c), Q3 **AFFIRMED** — I reproduced every load-bearing number.
Q2(b)'s conclusion (addendum may follow the merge) stands, but the **addendum
text as drafted must not be committed**: it mislabels what is retired, asserts
one thing the row it amends contradicts, and its row-2 replacement is
destructive. Replacement text in §3. Two further repairs: §6, §7.

## 1. Q1 — YAML deletions: AFFIRM, mechanically verified

I extracted `8819cb5f:.github/workflows/ci.yml` (499 lines), applied the ruled
edits verbatim in `/tmp` (delete 15–91, 125–194, 196–197, 286–287, 322–323;
replace 8–9) and parsed with PyYAML: **346 lines, parses clean**, six jobs
(`fences`, `test`, both exclusive calibration jobs, `build`, `installed-wheel`),
only `installed-wheel` carrying a `needs` (`build`) and none an `if`. No dangling `needs`, no orphan `if`, no double blank line; no `changes` /
`docs-readers` / `cancelled` token survives. Every boundary is right on the file
(15–18 detector comment, 19–90 `changes`, 91 blank; 125–127 fence comment,
128–193 `docs-readers`, 194 blank; `fences` 92–123; `build` 424;
`installed-wheel` 442): **no mis-numbered deletion.** FIX-3's `!cancelled()` is
moot and its removal is strictly safer: with `needs: changes` gone, `test` and
both exclusive jobs can no longer be skipped by a dead upstream at all.

Nothing parses the workflow: `git grep -E 'ci\.yml|workflows/' 8819cb5f` over
`tests`, `scripts` and `joulewise` returns nothing.

**I discharged the item the ruling deferred to the lead.** `gh api
repos/:owner/:repo/branches/main/protection` → 404 `Branch not protected`;
`…/rulesets` → `[]`. No required check exists, so no deleted job id can wedge a
merge. Strike the "the lead confirms" clause.

## 2. Q2(a) — fence literally true under A: AFFIRM

Fence verbatim, `27957b60:docs/process/state_kernel.json:6516` (line verified):

> "No test deletions, and the fast tier never substitutes for a required
> full-suite gate: merges, whole-window verdicts, and audited heads keep the
> full suite"

Under A no test is deleted; there is no fast tier, so clause 2 is vacuously
satisfied; every push and PR runs four shards × two Pythons plus both
exclusive jobs. True on all three clauses; no narrowing needed.

## 3. Q2(b) — conclusion AFFIRMED, drafted text REFUSED

The decisive reason is sound and I adopt it: rule 11 forbids the magistrate
*amending a process rule*, but Ed already ratified this amendment ("as
proposed", the proposal being decision 2 — delete `pr-fast`, retire
`pr_fast_tier`, **amend the TEST-SPEED-01 kernel text**). Writing the addendum
executes a ratified decision rather than making one, so ordering is bookkeeping.
The paragraph nonetheless fails on facts:

**(i) "lever 2, the PR-fast tier" is wrong on this repo's own usage.** The
authority label orders levers so #2 is the tier split, but the kernel
`status_note` says *"lever 2 (crash-matrix parallelization … ) LANDED via PR
#172"*, and the shipping commit is titled **"TEST-SPEED-01 lever 2: unit-atomic
sharding, crash-matrix split, PR-fast tier"** (349e06f4, 2026-08-23). A reader
of "lever 2 is retired" cannot tell whether unit-atomic sharding and the
crash-matrix split — live and load-bearing — went too. First-use test failing
on a term doing technical work.

**(ii) "never a gate and never a required check" is contradicted by the row
being amended.** Acceptance row 2 reads *"the fast tier **gates PRs**…"*, while
the shipped job is additive (`_what_this_is`: "It is NOT a gate"; no branch
protection, §1). Both are true of different objects — ratified intent vs shipped
job — and the addendum must say so, not assert only the convenient half.

**(iii) the row-2 instruction is destructive.** Row 2 conjoins the shard-runner
*and* the tier split; replacing the whole row with "implemented 2026-08-23,
retired 2026-09-13 by owner acceptance" deletes the shard-runner acceptance
criterion, which nobody retired.

Dates/ids check out: 2026-08-03 ratification (authority label); 2026-08-23
implementation (349e06f4 touches both files); Gmail `1a0969ba0b31c2b2`
(`…activation-c5048879/00-launch-record.md:34`, Exhibit K). Charter recomputed
`099de884…c95d81` = pin.

**Exact replacement paragraph (use verbatim):**

```
**TEST-SPEED-01 addendum (2026-09-13): the PR-fast/full tier split is
retired.** Ed ratified three levers on 2026-08-03 (suite-speed priority, a
PR-fast/full tier split, a Blacksmith runner evaluation). The tier split
shipped 2026-08-23 in commit 349e06f4 as the additive `pr-fast` job in
`.github/workflows/ci.yml` and the `pr_fast_tier` block in
`scripts/test_timings.json`. Naming note: this row's status_note and that
commit subject both use "lever 2" for the unit-atomic sharding and crash-matrix
split that landed the same day; those stay, and only the tier split is retired.
The shipped tier was never a required check (main carries no branch protection
and no rulesets, verified 2026-09-13), although acceptance-evidence row 2 as
ratified says "the fast tier gates PRs"; that gating clause was never
implemented and is withdrawn with the tier. On 2026-09-12 Ed accepted PR #317
"as proposed" (Gmail 1a0969ba0b31c2b2), whose decision 2 proposed deleting
`pr-fast`, retiring `pr_fast_tier`, and amending this task's kernel text. The
retirement deletes zero tests. Row 2 becomes "Shard-runner implemented from the data;
the ratified PR-fast/full tier split implemented 2026-08-23 and retired
2026-09-13 by owner acceptance; the FULL suite remains the gate for merges,
verdicts, and audited heads; zero test deletions", and the goal sentence drops
"and the PR-fast/full tier split". The fence is unchanged and remains literally
true. Cold gate 17 (2026-09-13) ruled option A on PR #317 T2, so no path-based
skipping narrows it. Levers 1 and 3 are unaffected.
```

Add one operational condition: the kernel edit and `scripts/gen_state.py
--check` regeneration must land in the **same commit** — that check runs in
`fences` and fails closed on drift.

## 4. Q2(c) — nothing reads `pr_fast_tier`: AFFIRM, two corrections

`git grep -n pr_fast_tier 8819cb5f` → `scripts/test_timings.json:6` plus six
hits in **four** trace files (ruling says "three"). The only other `pr-fast`
outside traces is the comment at `tests/test_check_gate_ledger.py:36`. Only
`scripts/shard_tests.py` and `tests/test_shard_split.py` load the JSON, and
neither asserts on the top-level key set (`test_shard_split.py:152` reads only
`unknown_module_weight_seconds`). Deletion is safe. Corrections: the block is
**lines 6–13, an 8-line deletion**, not "two-line"; and PR #317 touches only
`ci.yml` plus two trace files today, so this adds a second code file to the
diff — state that as scope.

## 5. Q3 — escalation classification: AFFIRM, reproduced

Over a `git archive 8819cb5f tests scripts/test_timings.json` extract:
**shipped selects 48 of 230; Exhibit G's widened selects 63.** The 15 added are
exactly Exhibit G's fifteen but only **13 of Exhibit F's fifteen**: widened
still misses `tests.test_claims_index_lint` (path arrives via
`claims_lint.DEFAULT_AP_PATH = Path("docs/contracts/analysis_plans.md")`, used
at `:382`) and `tests.test_gen_derivation_night` (`GEN.RUNSHEET_PATH.read_text()`
at `:1003`), while adding `test_env_locks` and `test_run_night`, which Exhibit F
never named. A third widening is round three of the same class. Charter §9
quoted accurately (`coldgate_charter.md:136`).

**The ruling is right and my Exhibit G was wrong.**
`8819cb5f:tests/test_calibration_exits.py:1501–1533` reads
`REPO_ROOT/"docs"/…/calibration_ledger_append.md` and asserts generated-registry
equality (1527), then reads `REPO_ROOT/"docs"/"phase_2"/"window_runbook.md"` and
asserts three D-117 anchors (1531–1533). It matches the *widened* regex (not the shipped one) yet is
subtracted as an exclusive module either way. Exhibit G's "No exclusive module
reads docs" is false; strike it. Exhibit F R2 is correct.

## 6. Writing standard — one defect the ruling creates

The line-8 replacement is accurate against lines 10–12 and plain. But the
ruling keeps "the `fences` job and its comment (92–123)", which reads
*"deliberately **ungated** on every push and pull request, **including
docs-only changes**"*. Under A nothing is gated and docs-only is not a
category, so it asserts a contrast the operator's checkout lacks — true on
8819cb5f, false on main after the merge. AMEND to:

```
  # F2 state generation, F3 explicit docs freshness, F4 historical receipt
  # semantics, and F5 CLI/strict mock smokes ran identically inside every
  # matrix job; they run once here instead. Every job below runs on every
  # push to main and every pull request.
```

## 7. Incomplete PR-body repair list

Beyond T2, the 1.4-runner-min row and "60 test modules" — also stale under A,
MATERIAL because the body is the merge record:

1. **Title** "trim the hosted CI matrix without losing a fence": A trims no
   matrix. Use "CI-TRIM-01 — hoist once-per-run fences, delete `pr-fast`, guard
   the zsh install".
2. **Concurrency bullet** justifies FIX-1 by "a later docs-only push no longer
   cancels a code push's full matrix and then skips it". FIX-1 stays; its stated
   reason must become the generic one (no push may evict a queued push).
3. **Measured table**: "Code PR, after (run 34561804133) 197.4" was measured on
   a tree containing `changes`; mark superseded or re-measure.
4. **"docs-only skip … now proven (run 34701979541)"** — moot; mark withdrawn.
5. **"Known gaps"** is entirely detector behaviour; delete it whole.
6. NIT: `test_docs_freshness` now runs twice on **every** run. Cost only.

## Executed probes

PyYAML parse of the post-deletion copy; both regexes over a `git archive`
extract; `git show` of `ci.yml`, `test_calibration_exits.py`,
`test_claims_index_lint.py`, `test_gen_derivation_night.py`, `claims_lint.py`,
`test_timings.json`, `state_kernel.json@27957b60`, `test_shard_split.py`;
`git grep` for `pr_fast_tier`, `pr-fast`, workflow readers; `git log -S` for the
`pr-fast` origin commit; `gh api` protection + rulesets; charter `shasum`. No
test run, no tracked file edited.
