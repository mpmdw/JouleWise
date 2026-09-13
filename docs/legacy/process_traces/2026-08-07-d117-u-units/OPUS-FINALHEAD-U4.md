# OPUS POST-MERGE FINAL-HEAD REVIEW — U4 (PR #113, merge cdb7896)

**Reviewer:** Opus 5, read-only, fresh eyes on the skipped final-head pass.
**Target:** `35ba641` (the post-delta narrow fix) and the whole merged U4 diff
`cdb7896^..cdb7896`.
**Repo:** `.../scratchpad/desk`, pulled. Note: `main` advanced to `47b9008`
during this review by a concurrent session; `35ba641` remains an ancestor and
**no U4 file has changed since `cdb7896`** (`git log cdb7896..HEAD --
tests/test_calibration_live_three_window.py tests/fixtures/calibration_live_three_window/
joulewise/calibration_bracketing.py` is empty). The review is current.
The desk repo was not modified. All mutation work was done in `/tmp` copies
produced by `git archive`.

**Bottom line:** the fix does what its commit message claims — verified by my
own mutation, reproducing the exact claimed signature. The final-head gap
**landed no defect**. But the gap did conceal three things worth recording, one
of which is a residual of the very FIX-D the commit purported to close.

---

## 1. Charge 1 — mutation verification of `35ba641`

### 1.1 What the fix does

`35ba641` adds a `bracket_runs_root` override (sentinel
`_USE_WINDOW_RUNS_ROOT`) to the `_evaluate` helper and inserts one new arm into
`test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding`: beta's
*correct* binding is evaluated against beta's window identifiers but with
**alpha's `runs_root`** as the caller's intended-window root, asserting
`("calibration_bracket_binding_invalid",)`.

### 1.2 The three redundant validation sites

`runs_root` is enforced in three independent places in
`joulewise/calibration_bracketing.py`:

| Site | Location | Property enforced |
|---|---|---|
| **S1** | `validate_calibration_bracket_binding`, intended-window loop (~L648) | `binding.runs_root == caller's expected runs_root` |
| **S2** | `evaluate_calibration_bracket`, candidate-agreement loop (~L1318/1324) | every candidate in the bound session has `bracket_runs_root == expected` |
| **S3** | `validate_calibration_bracket_binding`, session-agreement block (~L660) | `binding.runs_root == session.runs_root` |

### 1.3 Mutation matrix (measured, not asserted)

Scratch tree from `git archive cdb7896`; runner
`/Users/edr/code/JouleWise/.venv/bin/python -m unittest`. Baseline U4 module:
`Ran 23 tests ... OK (skipped=3)`.

| Mutation | U4 module | + `test_calibration_bracketing` + `test_calibration_ledger` (110 tests) |
|---|---|---|
| S1 only | OK | OK |
| S2 only | OK | OK |
| S3 only | OK | OK |
| **S1 + S2** | **FAILED (1)** | **FAILED (2)** |
| S1 + S3 | — | OK |
| S2 + S3 | — | OK |
| **S1 + S2 + S3** | — | **FAILED (2)** |

**The S1+S2 kill reproduces the commit message's claimed signature exactly:**

```
FAIL: test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding
  File .../tests/test_calibration_live_three_window.py, line 770, in ...
    self.assertEqual(reasons, ("calibration_bracket_binding_invalid",))
AssertionError: Tuples differ: () != ('calibration_bracket_binding_invalid',)
```

`()` instead of `calibration_bracket_binding_invalid` — verbatim what
`35ba641`'s message asserts. **Claim verified.** Mutation reverted; the
unmutated copy is `OK (skipped=3)`.

### 1.4 The fix is genuinely necessary at the module level

I applied the identical S1+S2 mutation to the **pre-fix** tree (`4b82180`):
`Ran 23 tests ... OK (skipped=3)`. The pre-fix L5 test was fully
non-discriminating for `runs_root`, exactly as the delta re-audit reported.
`35ba641` closed that.

### 1.5 Whole-repo mutation delta

Full suite (2733 tests), baseline vs S1+S2, same scratch method:

- Baseline: `FAILED (failures=1, errors=2, skipped=86)`
- S1+S2: `FAILED (failures=3, errors=2, skipped=86)`

The three baseline failures are artifacts of my scratch copy having no git
history (`git archive` of a commit is not a repo) — `project_commit == "unknown"`,
`tracked-files-only`, and `git archive <BASE_HEAD>` exit 128. Confirmed by
re-running them in a `git init`'d copy; two clear immediately and the third is
literally `git archive 9ee8710 -> 128`. None are real defects and all are
identical across both runs.

**The mutation delta is exactly two tests:**

```
FAIL: test_l5_later_same_t1_calibration_from_another_runs_root_cannot_be_borrowed
      (test_calibration_bracketing.CalibrationBracketingTests)
FAIL: test_l5_foreign_runs_root_cannot_bracket_with_or_without_binding
      (test_calibration_live_three_window.CalibrationLiveThreeWindowTests)
```

---

## 2. Charge 2 — findings on the merged U4 diff

### F1 — SHOULD-FIX (residual): FIX-D is closed as *implemented*, not as *specified*

The delta re-audit's FIX-D finding reads: *"It never supplies a binding naming
foreign-root endpoints."* `35ba641` did **not** supply such a binding. It
supplied the *correct* binding with a foreign **caller-side** `runs_root`. Those
are different vectors:

- **Landed vector** (caller-side mismatch): `binding.runs_root = beta`,
  `expected = alpha` → S1 catches; S2 backstops.
- **Requested vector** (forged binding naming a foreign root): a hand-rehashed
  binding with `runs_root = alpha` for beta's session, evaluated with
  `expected = alpha` → S1 *passes*, and only **S3** stands between that and
  acceptance (S2 also backstops).

`build_calibration_bracket_binding` refuses to construct such a binding
(L550–568), so it must be forged + rehashed — which the U4 file already knows
how to do (`_rehash_binding`, used in two other tests).

**Measured consequence: S3 has zero coverage anywhere in the calibration
modules.** Removing it alone leaves 110 tests green. The delta auditor asked for
the vector that would have covered it; the fix landed a neighbouring one; and
because the final-head pass was skipped, nobody compared the fix against the
finding it was answering. Suggested closure: add a fourth arm using
`_rehash_binding` to set `runs_root` to alpha's root, asserting
`calibration_bracket_binding_invalid`.

### F2 — OBSERVATION: `35ba641` bought no *net repo-level* coverage

`tests/test_calibration_bracketing.py:1069-1088` already contained the same
assertion (correct binding, `bracket_runs_root="/synthetic/root-beta"` →
`calibration_bracket_binding_invalid`) and **already killed S1+S2 before the
fix**. I confirmed this directly: pre-fix U4 file + S1+S2 across the three
calibration modules gives `FAILED (failures=1)` — the pre-existing unit test.

This does not make the fix wrong. U4 is the *integration* regression over the
live three-window fixture and should carry its own L5 discrimination rather than
lean on a unit-level fixture. But the honest characterisation is
"module self-sufficiency," not "closed a hole in the repo's coverage," and the
commit message's framing overstates slightly.

### F3 — SHOULD-FIX: the three U2-staged tests are correctly gated but vacuous

They are **not** silently disabled — each carries
`@unittest.skip("U2 successor engine pending")`, the reason names the blocker,
and the runner reports `skipped=3` on every run. Gating is honest.

The problem is the bodies. All three assert a fixture value against a string or
int literal (`vector["expected_trigger"] == "new_valid_..."`;
`vector["expected_total_valid_same_epoch"] == 38`; `vector["mutations"] == [...]`).
They exercise **zero production code**. Whoever lands U2 and deletes the three
decorators gets three instantly-green tests that assert nothing — a
false-assurance trap precisely at the moment the successor engine most needs
coverage. The delta auditor noted the bodies are placeholders; it did not flag
the un-skip trap. Suggested closure: make each body `self.fail("staged for U2 —
implement against the successor engine")` beneath the skip, so removing the
decorator fails loudly.

### F4 — OBSERVATION (pre-existing, not introduced by U4): discovery authentication is stubbed everywhere

Every U4 test that discovers candidates patches
`joulewise.calibration_bracketing._candidate_from_observation` with the
test-local `self._candidate`, which copies observation fields with **no
cross-checks**. The real function (L871–923) performs the substantive
authentication: manifest/evidence SHA-256 vs the receipt's `artifact_sha256`,
`content_id` re-derivation, decimal bound equality, capture-time equality, and
`V2_BINDING_FIELDS` / `ACCEPTANCE_IDENTITY_FIELDS` agreement. All of it is
bypassed.

I checked the whole test tree: **no test in the repo calls
`discover_calibration_candidates` without stubbing
`_candidate_from_observation`** (`test_calibration_bracketing.py:767, 1201,
1222, 1582` all patch it). `load_calibration_candidate` is tested directly
(L1979) but the cross-authentication block appears to have no coverage anywhere.

This is forced by U4's fixture design — `_write_synthetic_custody` writes
`f"{label}:{relative}"` bytes, not parseable JSON bundles, so the real function
could not run. It is a legitimate boundary. But it is *undeclared*: the file
carries an explicit comment for the smaller `verify_custody=False` boundary
(L226-229) and none for this larger one, while
`test_bundle_path_uses_ledger_discovery_as_candidate_authority` is named for
authority the stub removes. Worth a comment at `_candidate` and a queue item for
the underlying gap.

### F5 — VERIFIED GOOD: `76 + 3*5 = 91` is derived, not curve-fitted

I traced the chain and it holds:

- **76** — `self.base_sequence = len(base_receipts)`, *computed* by
  `_build_issuance_equivalent_base` (2 receipts per member × 38 members: 19
  authentic derivation-corpus members + 19 synthetic additions). Asserted equal
  to the module constant `_ISSUANCE_BASE_SEQUENCE` **and** to the fixture's
  independent `receipt_count: 76`
  (`test_issuance_equivalent_base_has_76_receipts_and_30_2_6_dispositions`).
- **5** — an oracle checked against the *actual* production writer. `setUpClass`
  drives the real `scripts/validate_powermetrics_fiducial._CaptureLedgerLifecycle`,
  whose `begin()` calls `_validate_reserved_bracket_slot` +
  `claim_bracket_session_slot` and whose `finalize()` calls
  `finalize_bracket_session_slot` + `terminal_head_pin_for_session`, hashing
  *real on-disk custody files* via `ledger_artifact_hashes`.
  `test_production_writer_receipts_end_at_derived_terminal_sequence` then
  asserts the literal five-event ordering
  `[open, claim, finalization, claim, finalization]` per session and the per-slot
  ordering `["pre","pre","post","post"]`. If the writer emitted a different
  number of receipts, the 5-wide slicing misaligns and this fails.
- **3** — `len(self.windows)`, asserted via
  `test_each_night_issues_its_verdict_at_a_committed_closeout` (`len(set(pin_commits)) == _LIVE_SESSION_COUNT`).

So the terminal sequence is genuinely the production writer's, cross-checked
from two directions. **Not curve-fitted.** The superseded three-receipt/85
model survives in the fixture only under an explicit
`receipt_model_supersession.superseded` key, which is the right way to keep it.

### F6 — NIT: duplicated literals where named constants exist

`test_final_closeout_replays_all_verdicts_with_complete_universe` uses
`[snapshots[0]] * 3` instead of `_LIVE_SESSION_COUNT`;
`test_all_six_are_same_epoch_...` uses `self.assertEqual(len(observations), 6)`
instead of the fixture's `live_observation_count: 6`. Both are the exact class
of stale-literal drift that produced the original FIX-A defect.

### F7 — NIT: dead fixture data

`scenario.json` gives each window a `runs_root` (`/synthetic/d117/alpha` etc.),
and `setUpClass` overwrites all three with tmpdir paths (L120). The JSON values
are never read. In a fixture whose whole subject is `runs_root` binding, leaving
three unreachable `runs_root` strings in the fixture is actively misleading.

### F8 — OBSERVATION: the writer's committed-pin path is not exercised

Every `_CaptureLedgerLifecycle` in `setUpClass` is constructed with
`require_committed_pin=False`; production defaults to `True`. The
committed-pin branch inside `_validate_reserved_bracket_slot` is therefore never
driven through the writer. It *is* covered from the snapshot side
(`append_bracket_session_receipt(..., require_committed_pin=True)`, the closeout
loads, and the dedicated `calibration_ledger_head_uncommitted` vector), so this
is a seam-level gap rather than an uncovered property.

### F9 — PROCESS (not code): the delta verdict's PARTIALs were never adjudicated

`U4-DELTA-VERDICT.md` returned **NOT CLEAN**: FIX-D `NOT CLOSED`, and FIX-C,
FIX-E, FIX-F all `PARTIAL`. `35ba641` addressed **only** FIX-D. FIX-C (parent
artifact hand-reconstructed rather than emitted through the D-116 emitter),
FIX-E (issued verdict bytes never compared against terminal replay; the
open-beta/alpha-verdict vector absent), and FIX-F (no NEEDS_SCOPE clause) were
carried into the merge with no recorded ruling accepting them. `U1` and `U3` each
have a `FABLE-GATE-*.md`; **there is no `FABLE-GATE-U4.md`.** Whether those
PARTIALs are acceptable is a magistrate call, not mine — but the record should
say someone made it.

---

## 3. Charge 3 — did the gap land a defect?

**Process violation with no landed defect — but not with no consequence.**

Precisely:

- **No defect landed.** `35ba641` is a test-only change (18 lines, one file). It
  cannot regress production behaviour. It does what it claims — verified by my
  own mutation reproducing the claimed signature byte-for-byte. It does not break
  any other test: the merged tree is `OK (skipped=3)` on the module and clean on
  the full 2733-test suite modulo three scratch-environment artifacts. The
  merged U4 diff touches only `tests/`. **No production code path is worse off
  than before the PR.**

- **The gap nonetheless hid a real miss.** The one job a final-head pass does is
  ask *"does this last commit actually answer the finding that prompted it?"*
  Here the answer is **partially** (F1): the fix closed a neighbouring vector, not
  the one the delta auditor specified, and left validation site S3 with zero
  coverage in the entire calibration suite. A fresh reader holding the delta
  verdict next to the diff would have caught that in minutes — it is a
  three-line comparison of the finding's wording against the fix's arm. Instead
  FIX-D is now recorded as closed.

- **Two further items would plausibly have surfaced** at the same pass: the
  un-skip trap in the three staged tests (F3) and the un-adjudicated
  FIX-C/E/F PARTIALs (F9).

So: the historical precedent (final-head catching a real crash path) did not
repeat. This time the cost was a **mis-recorded closure** plus two unraised
items — cheap, but exactly the failure mode the rule exists to prevent, and the
kind that compounds because "FIX-D closed" is now the record future sessions
will trust.

Nothing here rises to a revert. Recommended follow-ups, in order: **F1**
(add the forged-binding arm and correct the FIX-D closure record), **F3**
(make the staged bodies fail loudly), **F9** (adjudicate or record the PARTIALs),
then **F4/F6/F7** as queue items.

---

## Checks performed

- `git show 35ba641`; `git diff cdb7896^ cdb7896 --stat` (2 files, +1580, tests only).
- Read in full: `tests/test_calibration_live_three_window.py` (1412 L),
  `tests/fixtures/calibration_live_three_window/scenario.json`,
  `joulewise/calibration_bracketing.py` L519-700 / L1160-1345 / L840-960,
  `scripts/validate_powermetrics_fiducial.py` L352-500.
- Baseline U4 module: `Ran 23 tests in 0.641s / OK (skipped=3)`.
- Mutation matrix S1/S2/S3 and all pairs + triple across 110 calibration tests
  (table §1.3); pre-fix tree + S1+S2 `OK (skipped=3)`; pre-fix tree + S1+S2
  across 110 tests `FAILED (failures=1)`.
- Full suite ×2 (2733 tests, ~550 s each): baseline `FAILED (1 failure, 2 errors)`
  vs S1+S2 `FAILED (3 failures, 2 errors)`; the three common items confirmed as
  git-absent scratch artifacts.
- Grep sweep: production callers of `validate_calibration_bracket_binding`
  (exactly one, `evaluate_calibration_bracket` L1288; also in `__all__`);
  every repo call site of `discover_calibration_candidates` /
  `_candidate_from_observation`; trigger-string existence in the implementation.
- Read `docs/process_traces/2026-08-07-d117-u-units/U4-DELTA-VERDICT.md` to
  establish what the earlier layers had already reported.
- Desk repo unmodified throughout (`git status --short` unchanged by me; all
  mutation work under `/tmp`).
