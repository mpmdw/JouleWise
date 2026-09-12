# 25 — Opus counter-review (gate row 6) — PR #324 (A177), PR #325 (A184)

Diverse-model lens on the near-final heads, after reports 04/02 and refuters
10/24 and 13/14. Read-only. Refuter 10's blocking F1 (no suite could run: no
usable temp dir) is discharged — I ran the suites.

## PR #324 — A177, head c85a171d (tests only)

**1. Smallest change / duplication.** Policy: yes — the campaign
`patch.object` wrapper is gone and one override lives on the fixture class
(`tests/test_controller.py:669-678`). No second policy home:
`tests/test_idle_admission.py:503-504` appends `--no-sleep` to a directly
invoked fixture argv (paced/unpaced comparison input, not a producer policy).
**Duplication, nit:** the post-count formula now exists three times —
production `joulewise/adapters/powermetrics.py:1029-1031`, re-derived with a
hardcoded `interval_s = 0.05` at `tests/test_controller.py:1651-1657` and
`tests/test_run_campaign.py:9627-9632`. A production change needs two identical
test edits; one shared test helper would leave one home.

**2. Failure modes the prior lenses did not test.** (a) The override is
**inherited** by `CleanAdmissionPowermetricsAdapter`
(`tests/test_controller.py:733`), whose producer `:850` has **zero callers**
(grep, all `*.py`) — harmless today, silent policy for the next clean-admission
test. (b) Other instantiation sites `:1758` and `:1782` (contaminated /
exceptional teardown) previously ran bounded captures **paced** and now run
them unpaced; both pass. (c) `count` is keyword-only
(`joulewise/adapters/powermetrics.py:1472-1478`), so `kwargs.get("count")`
cannot be evaded positionally; the fixture refuses `--no-sleep` without `-n`
(`tests/fixtures/fake_powermetrics_process.py:44`) and production emits `-n`
exactly when `count is not None` (`:1479-1481`), so the flag is always legal.
(d) Continuous capture still asserted flag-free at `:1716`.

**3. Contract text.** N/A — no prose changed.

**4. Merge-ability.** Disjoint from #325 (A177: `tests/test_controller.py`,
`tests/test_run_campaign.py`). `origin/main` is `ace4cc3c` in both worktrees;
`git diff --name-only ace4cc3c..origin/main` empty — no drift, no rebase.

**5. Verdict: MERGE** (nit only: fold the triplicated count formula into one
test helper next time the file is touched).

## PR #325 — A184, head ca7346e4

**1. Smallest change / duplication.** Yes: one enum member plus the three
class-membership sets that already drive every projection
(`joulewise/calibration_exits.py:106,268,290,373`); the docs row is generated
(`:556`, freshness asserted at `tests/test_calibration_exits.py:1500-1526`), not
a second registry. **Nits, both pre-existing patterns:** the abort-reason→code
map is mirrored at `tests/test_calibration_exits.py:5590-5604` vs production
`scripts/recover_calibration_ledger.py:62-67`; and
`_state_window_exhausted_abort` (`tests/test_calibration_exits.py:4599-4617`)
re-opens a 2-slot derivation session already built by
`_state_derivation_kind_writer` (`:4472-4492`).

**2. Positional/count enumeration.** None found — every projection is keyed by
code, not index: `joulewise/calibration_exits.py:556`,
`joulewise/calibration_ledger.py:149-156` (value-prefix filter),
`scripts/recover_calibration_ledger.py:167` (`choices` from values);
`process_exit` is a field default (`:142,161`), not an ordinal, so no exit code
shifts. The only count assertion is `tests/test_calibration_exits.py:1551`
(`len(REFUSAL_INVENTORY) == len(enum_codes)`), size-agnostic. The `readiness_*`
registry (`tests/test_arm_readiness_integration.py:790`) is a separate
vocabulary. **Labelling flag (nit):** the row carries `night_loss=true` because
`_ABORT` hardwires it (`joulewise/calibration_exits.py:469-475`), while the
runbook calls `window_exhausted` the *planned* early close
(`docs/phase_2/derivation_night_runbook.md:1673-1677`,
`tests/test_epoch_equivalence_check.py:229-231`). Nothing reads `night_loss`
outside the generated table.

**3. First-use test (runbook `:1665-1672`).** `session-refusal` is glossed at
first use; `H` is built at `:274` and `:1461`; `harvest` from `:29`/§2. **One
term fails:** "the armed night's **frozen clone** at H f90cb8c0" — the doc's
built terms are "a fresh clone at H / measurement root" (`:274`) and "frozen
checkout triple" (`:97`). Replacement: *"The night's measurement clone (§0.2 —
the fresh clone cut at H and left untouched) sits at H f90cb8c0, which predates
that code, so it prints …"*. Smaller: "(main after 2026-09-12)" is false until
this merges; prefer "(main, from the commit that adds it)". The behavioural
claim **verifies**: `f90cb8c0` has no `WINDOW_EXHAUSTED` and no
`window_exhausted` key, so `scripts/recover_calibration_ledger.py:377-379`
falls through to `calibration_session_not_open`
(`joulewise/calibration_exits.py:66`).

**4. Merge-ability.** Disjoint from #324; `origin/main` = `ace4cc3c` here too.

**5. Verdict: MERGE** (optional 2-line doc polish from §3).

## What I ran (`/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -q`)

- wt-a177 `tests.test_controller` → `Ran 74 tests in 74.154s` / `OK` (clears F1)
- wt-a177 `tests.test_run_campaign.IdleAdmissionCoreVerdictTests` → `Ran 73 tests in 97.634s` / `OK`
- wt-a184 `tests.test_reason_code_partition tests.test_calibration_ledger` → `Ran 95 tests in 8.791s` / `OK (skipped=1)`
- wt-a184 `tests.test_calibration_exits` → `Ran 48 tests in 453.195s` / `OK` (its teardown census reported a stray fake sampler pid 77113 owned by `JouleWise-wt-integ-f0d28baa`, detect-only — fleet hygiene, not this PR)
- `git show f90cb8c0:{scripts/recover_calibration_ledger.py,joulewise/calibration_exits.py}` → map present, new key/member absent
- `git rev-parse origin/main` both worktrees → `ace4cc3c…`; diff vs base empty
- greps: all adapter/producer call sites; all `RefusalCode` enumerations, `len(`, `process_exit`, `window_exhausted`, `--no-sleep`
