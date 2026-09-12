# 179 — S10 round 3 DELTA re-audit (Opus, read-only)

Target `6d838a102fa867338e91c398b8adf44cbfb09603` ("S10 round 3"), parent/round 2
`e187723701df35553fb0dbb1a694743613f95916`, branch `feat/2026-09-10-epoch-continuation`.
Everything executed from a read-only export at `/tmp/s10-r3-export`
(`git archive $R3 | tar -x`), `PYTHONDONTWRITEBYTECODE=1`, no `timeout` wrapper.
Nothing written in any repo; no git write commands; canonical, night-custody and the
other worktrees untouched. Only this file was written.

**Verdict: NOT CLEAN — 0 blockers, 1 should-fix (the known S1 residue, now
demonstrated as an executed acceptance, not a theory), 2 nits.**
B1 is CLOSED. S1/S2/S3 landed as briefed. No regression.

---

## (5) Regression run — first, because everything below depends on it

```
cd /tmp/s10-r3-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_epoch_continuation tests.test_calibration_bracketing \
  tests.test_validate_powermetrics_fiducial_derivation_only \
  tests.test_validate_powermetrics_fiducial tests.test_d078_reason_registry 2>&1 | tail -3
```
```
Ran 170 tests in 103.096s

OK (skipped=1)
```
rc 0. Independent mutation replay, same export:
`python3 tests/fixtures/epoch_continuation/mutation_cuts.py` →
`cuts=24 killed=24 survivors=0 source_sha256_restored=true`, rc 0. The seat's
24/24 claim reproduces; the six new cuts (C19–C24) are honest — C19 deletes the
three converse lines as a block, C23/C24 isolate lines 242 and 243–245, C20
removes the non-empty-detail requirement, C21 *restores* the acknowledgment
exemption in the systematic branch, C22 disables the prepare refusal. **No
regression.**

---

## (1) B1 — CLOSED, plus the two neighbours

Executed: `/tmp/s10_r3_delta_demo.py` (refuter 170's fixture shape rebuilt
against the r3 export: 12 declared slots, 9 filled, session aborted
`window_exhausted`, six captures at `0.025` and three at `level + 0.001`).

```
honest prepare rc = 4 (4 == FAIL)  m = 9  max = 0.033898493715362  level = 0.032898493715362  wrote file = False
ledger finalized rows = 9

[B1-hide-three-rows] verdict-in-file=pass m=6 loaded=0
  refusals=[{'reason': 'calibration_epoch_continuation_invalid',
             'continuation_id': 'epoch-continuation-b99aa921…',
             'detail': 'hidden_finalized_row'}]

[a-unresolved-with-madeup-detail] verdict-in-file=pass m=6 loaded=1 refusals=[]
[a-unresolved-with-madeup-detail] *** ACCEPTED *** m=6 verdict=pass
  cross_check=verified_terminal_derivation_session acknowledged=9

[b-relabel-ordinary-invalid] verdict-in-file=pass m=6 loaded=0
  refusals=[… 'detail': 'acknowledged_row_disagrees'}]
```

**Original B1: REFUSED**, detail `hidden_finalized_row`, zero continuations
loaded. Refuter 170's blocker does not reproduce. The refusal comes from
`joulewise/calibration_epoch_continuation.py:240-241` (a file slot carrying
`content_id: null` whose slot name IS in `session.finalized_slots`); had the
forger also renamed slots, `:242` (`file_finalized == ledger_finalized`) and
`:243-245` (every ledger observation of the session must appear in the file)
close the remaining directions. `cross_check` is set to
`verified_terminal_derivation_session` only at `:256`, after all three.

**(b) re-label the three rows `ordinary-invalid`: REFUSED**, detail
`acknowledged_row_disagrees`, from `:252-253` —
`row.classification_disposition == slot["disposition"]`. The ledger row says
`valid`; the file says `ordinary-invalid`; the loop at `:246` iterates **every**
finalized slot, not just retained ones, so excluded rows are cross-checked too.
Yes, `exact_bound_lexeme_s` is compared for those rows as well, in the same
`_require` at `:253`.

**(a) disclose all nine, mark the three over-screen rows `valid` with
`anchor_v3_resolved: false` and a made-up detail: ACCEPTED**, m=6, verdict
`pass`, `ledger_cross_check: verified_terminal_derivation_session`, nine
acknowledged attempt ids, zero refusals. See SF-1 below.

Precisely what the file must assert for (a) to work, and what is checked:
- It must disclose all nine rows with the ledger's own `attempt_id`,
  `content_id`, `disposition` (`valid`), and `b_fiducial_s` — including
  `0.033898493715362` on each of the three over-screen rows. All four are
  compared against the ledger row (`:248-253`), so the file **cannot lie about
  the magnitude**: the failing bound sits in the file in plain text.
- It must set `anchor_v3_resolved: false` and a non-empty string
  `anchor_v3_detail` on those three. **Neither field exists on
  `LedgerObservation`** (`joulewise/calibration_ledger.py:329-349` — fields are
  `sequence, receipt_digest, attempt_id, content_id, artifact_sha256,
  identity_epoch, t1_bindings, capture_wall_time_s, exact_bound_lexeme_s,
  disposition, custody_locator, observation_kind, bracket_*`). The loader
  cannot replay bytes and has no ledger counterpart to compare, so the
  assertion is accepted as written. The S1 check at `:204-205` requires only
  that the detail be a non-empty string; its *content* is unconstrained.
- `identity_epoch` is compared only for retained rows (`:254-255`), so the
  three excluded rows escape that check too — harmless here (they are
  excluded), noted for completeness.

---

## SHOULD-FIX

### SF-1 — anchor-v3 exclusion is still an unverifiable, verdict-flipping assertion (the accepted S1 residue, now executed)

`joulewise/calibration_epoch_continuation.py:201-205, 218-220`.

Refuter 170 called this S1 and said it "cannot be fully closed"; triage 171
accepted the *auditability* mitigation only. I am re-raising it at should-fix
rather than closing it because the executed case (a) above shows the residue is
not merely "an exclusion that is invisible" — it **turns a night the tool scores
FAIL rc 4 into an authenticated PASS**, with the record stamping
`verified_terminal_derivation_session` over it. That is the same outcome B1 had;
only the mechanism moved from *hiding rows* to *hiding their eligibility*.
Round 3 did buy something real: the bad bound is now disclosed, cross-checked
byte-for-byte against the ledger lexeme, and accompanied by a named reason — a
human reading the continuation sees three `valid` rows at `0.0339` excluded for
a stated cause, so the defect is *detectable by inspection*. It is still
undetectable by machine, and the acceptance is what the arm consumes.

The contract already states the property that is unenforced
(`docs/contracts/epoch_continuation.md:56-58`: exclusion "is never based on the
magnitude of a bound").

**A machine-checkable close exists and does not require replaying bytes:**
require the screens to hold over **every disclosed `valid` row**, resolved or
not, while `m` continues to count only resolved ones. Anchor-resolution then
can only reduce `m` (already floored by `MINIMUM_RETAINED`); it can never
convert a FAIL into a PASS, because the level/bracket comparison ranges over the
full valid set whose lexemes are all ledger-pinned. One added statistic over
`[slot["b_fiducial_s"] for slot in slots if slot["disposition"] == "valid"]`,
refusing when its verdict is not `pass`.

This is **a design question for the magistrate, not a seat defect** — the seat
implemented triage 171 exactly. The trade is: a genuinely unresolved
high-bound capture would then block the night rather than being droppable. That
is the conservative direction, and it matches the precedent round 3 itself set
for systematic failures (`prepare-candidate` refuses the whole night rather than
issuing something that should be adjudicated).

Note the bound on severity, which is why this is not a blocker: every forgery
above presupposes the forged bytes being **registered** in
`EPOCH_CONTINUATION_REGISTRY` with their SHA-256 (`:154-157`), i.e. surviving
the owner's registration review — at which point the three `0.0339` rows are on
the page. The realistic failure it guards is an issuer bug or a partial
anchor-replay outage, not an adversary.

---

## (2) S3 — implemented as decided

- `acknowledged_attempt_ids` is **gone from the systematic branch**. It now
  appears at exactly three places in `joulewise/calibration_bracketing.py` —
  `:2363`, `:2365` (construction) and `:2374`, the range-expansion filter.
  The systematic branch (`:2380-2385`) filters on
  `observation.disposition == "systematic-invalid" and
  dict(observation.identity_epoch) in judged_epochs` only. Corpus doubling
  still counts acknowledged valid rows (`test_doubling_is_per_epoch_and_acknowledged_values_count`, passing).
- **`prepare-candidate` refuses, executed independently** (`/tmp/s10_r3_prepare_demo.py`,
  a 12-slot night with one `systematic-invalid` row, plus an all-clean control):
```
[one-systematic-row] rc=3  stdout_len=0  out_file_written=False
[one-systematic-row] stderr="REFUSED: night_contains_systematic_failure: slots.d12;
  continuation would be stale on arrival; the desk reports the failure to Ed
  under D-102's systematic-failure trigger"
[all-clean-control]  rc=0  stdout_len=8441  out_file_written=True
```
  rc 3, empty stdout, no file. The refusal sits at
  `scripts/issue_epoch_continuation.py:78-81`, before any evidence is read, and
  the control proves it is not refusing everything.
- **Does the inverted test really assert an ACKNOWLEDGED systematic row fires?
  Yes.** `tests/test_epoch_continuation.py:406-424`
  (`test_systematic_row_in_the_equivalence_night_still_fires`) flips the FIRST
  finalized row of the equivalence night to `systematic-invalid` in both the
  file and the ledger, loads it with **zero refusals**, then asserts
  `assertIn(row.attempt_id, loaded[0].acknowledged_attempt_ids)` — i.e. the row
  really is acknowledged — before asserting the evaluation returns
  `calibration_acceptance_bound_stale` with `observed_triggers ==
  ["new_systematic_failure_challenges_preflight_screen"]`. The second half
  (`:425-443`) independently fires the trigger from an *ordinary* 25G83
  systematic row against a healthy equivalence night, so a broken trigger cannot
  be masked by the first case. C21 (restore the exemption) is killed by this test.

## (3) S1 — both null and empty refuse

`joulewise/calibration_epoch_continuation.py:204-205`
(`… or bool(slot["anchor_v3_detail"])`, detail `slots.anchor_v3_detail_required`).
`tests/test_epoch_continuation.py:510-524` sub-tests `None` and `""` and asserts
`details[0]["detail"] == "slots.anchor_v3_detail_required"` for both, with a
positive control (a genuinely unresolved row with a real detail loads, one
continuation, zero refusals). Confirmed in the passing run above.

## (4) S2 — contract now says "only when non-empty"

`docs/contracts/epoch_continuation.md:152-156`: "Bracket evaluation records these
as `acceptance.continuation_refusals` **only when non-empty** … The field is
absent otherwise, preserving stable receipt hashes and the pre-continuation
evaluation record when no continuation is registered." Matches
`joulewise/calibration_bracketing.py:2128-2129`. The doc was fixed, not the code
— as triaged. The contract's added sentence "Thus `m` cannot exceed the ledger
session's valid-row count" is now **true**: `m` counts rows that are `valid` and
resolved, and `valid` is ledger-compared at `:252`.

---

## (6) SAME-SIGNATURE STATEMENT — the B1 class is NOT closed by construction

The B1 class is "a field of `evidence.slots[*]` that decides the verdict and
that the loader accepts on the file's word." Round 3 closes **row existence**
by construction (three set-level converse checks, both directions, plus a
direct sweep of `ledger_snapshot.observations`). It does **not** close the class:
exactly one field pair is still file-asserted-only, and it is outcome-bearing.

Walking every field of `evidence.slots[*]` (loader lines in
`joulewise/calibration_epoch_continuation.py`):

| field | status | where |
|---|---|---|
| `slot` | **checked** — slot list must equal `evidence.declared_slots` (`:193`), which must equal `session.declared_slots` (`:233`); membership both directions at `:240-245` | `:193, :233, :240-245` |
| `attempt_id` (finalized) | **checked** — `(slot, attempt_id)` set equality with `session.finalized_slots` (`:236-237, :242`), re-checked per row (`:248`), and the row must be the same object in `observation_by_attempt` and belong to this session (`:249-250`) | `:236-250` |
| `attempt_id` (unfinalized) | **checked** — must be `null` (`:208`) and the slot must be absent from `session.finalized_slots` (`:240-241`) | `:208, :240-241` |
| `content_id` | **recomputed AND checked** — recomputed from the file's two hashes via `content_id_from_artifact_hashes` (`:213-214`) and compared to `row.content_id` (`:251`) | `:213-214, :251` |
| `manifest_sha256` | **effectively checked** — not compared field-to-field against `row.artifact_sha256["manifest.json"]`, but it is a hash preimage of `content_id`, which is; forging it requires a SHA-256 collision | `:213-214, :251` |
| `instrument_evidence_sha256` | **effectively checked** — same argument | `:213-214, :251` |
| `disposition` (finalized) | **checked** — `row.classification_disposition == slot["disposition"]`, for every finalized row including excluded ones | `:252` |
| `disposition` (unfinalized) | **checked** — must be `window_exhausted`/`no_row`, only when `session_state == "aborted"`, and the slot must be ledger-unfinalized | `:207, :240-241` |
| `b_fiducial_s` (finalized) | **checked** — `row.exact_bound_lexeme_s == slot["b_fiducial_s"]`, exact lexeme, for every finalized row including excluded ones; also re-parsed as Decimal (`:216-217`) | `:216-217, :253` |
| `b_fiducial_s` (unfinalized) | **checked** — must be `null` | `:210` |
| **`anchor_v3_resolved`** | **FILE-ASSERTED ONLY** — no counterpart on `LedgerObservation`; type-checked (`:201`) and forced `false` on unfinalized slots (`:210`); **gates retention and therefore the verdict** (`:218-220`) | `:201, :218` |
| **`anchor_v3_detail`** | **FILE-ASSERTED ONLY** — must be `null` when resolved (`:203`) and a non-empty string when a `valid` row is unresolved (`:204-205`); **content never verified** | `:202-205` |

Derived quantities are all recomputed, not trusted: `m`, `retained_min_s`,
`retained_max_s`, `retained_range_s` and `verdict` are re-derived by
`equivalence_statistics` from the disclosed lexemes and compared with type
(`:221-224`); `acknowledged_attempt_ids` must equal the file's finalized
attempt-id list (`:196-198`), which round 3 now pins to the ledger's — so
acknowledgment is no longer independently forgeable either.

So: **one unchecked outcome-bearing pair remains (`anchor_v3_resolved` /
`anchor_v3_detail`), and SF-1 above is the executed demonstration that it
reproduces B1's outcome.** Everything else in `evidence.slots[*]` is either
recomputed or ledger-compared.

---

## NITS

**N1 — line `:240-241` is not independently cut.** C19 deletes the three
converse lines as a block; C23 isolates `:242`, C24 isolates `:243-245`; nothing
isolates the unfinalized-absence check. It is de facto covered — removing it
alone routes the forgery to `:242` with detail `ledger_finalized_slots_mismatch`,
and `test_failed_nine_row_night_cannot_hide_three_finalized_rows_to_pass` asserts
`details[0]["detail"] == "hidden_finalized_row"` exactly, so it would still fail
— but the cut table's own convention is one isolated cut per branch.

**N2 — no strict key-set check on `evidence.slots[*]`.** Unknown keys in a slot
object are ignored (unlike the tool's S9 witness, which refuses unknown keys at
`scripts/issue_epoch_continuation.py:219-220`). No semantic effect — the loader
reads named keys and `derivation_sha256` covers the whole object — but a
registered file could carry misleading annotations that no check contradicts.

Refuter 170's N1 (`check` picks the acceptance from the untrusted candidate),
N2 (`no_row` candidate the reader will refuse) and N3 (hand-typed operative
digits in contract prose) were out of brief 172's scope and remain open as
filed; I confirmed round 3 did not touch them.

## Footprint

Read-only. Export at `/tmp/s10-r3-export`; scratch scripts
`/tmp/s10_r3_delta_demo.py`, `/tmp/s10_r3_prepare_demo.py`; log
`/tmp/s10-r3-tests.log`. The S10 worktree, `/Users/edr/code/JouleWise`,
`/Users/edr/night-custody` and every other worktree were not written to and no
git write command was run.
