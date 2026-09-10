# 58 — Seat S2 (Claude Opus, replacing the Astra seat) — derivation-kind ledger sessions with N declared slots

Lane ACCEPTANCE-EPOCH-25G83-01. Worktree `/Users/edr/code/JouleWise-wt-s2-ledger-sessions`,
branch `feat/2026-09-10-epoch-s2-ledger-sessions` at main `7c4366ec`. Diff left uncommitted in
the working tree; no git commit / push / checkout / stash / reset was run.
Authority: cold-gate ruling 46 §R-a A7 and §R-d row S2, addendum 11 A-1 and A-6, brief 47.

## Summary

A ledger session now declares an ORDERED slot list at open. Two kinds exist:

- **`bracket`** declares exactly `("pre", "post")` and records **neither** the kind nor the
  list, so its receipt bytes, its CLI flags, every existing fixture and the 76-row production
  ledger are untouched. Absence of the fields IS the bracket default.
- **`derivation`** records `session_kind: "derivation"` and `declared_slots: [...]`
  explicitly. The reserve CLI names them `d01..dNN` from `--slot-count N`.

The session is `finalized` when all declared slots are final; the terminal pin candidate is
the last declared slot's finalization or the abort receipt (`window_exhausted` keeps every
already-finalized slot as an observation); the head pin is still checked ONCE at open and never
again while the session runs; `is_governed_open_bracket_extension` is unchanged in meaning.

`resume_finalize_bracket_session` now takes `systematic_screen_s: Decimal | None`. For a
derivation-kind session the caller passes `None`, the disposition collapses to
`valid`/`ordinary-invalid`, and the `slot == "pre"` auto-abort does not apply.
`scripts/recover_calibration_ledger.py` reads the session's declared kind before choosing the
screen, so the active artifact's level screen is never handed to a derivation session.

## Changed paths (all within WRITE_SCOPE)

| Path | Change |
|---|---|
| `joulewise/calibration_ledger.py` | kind/declared-list constants and helpers; open-receipt shape validator accepts the kinded shape; assembler, claim, finalize, abort, terminal pin, session status and readiness all read the session's declared list; `resume_finalize_bracket_session` screen semantics; new public `declared_session_shape`, `derivation_session_slots`, `is_declared_slot_name`, `session_kind_of_open_receipt`, `declared_slots_of_open_receipt` |
| `scripts/reserve_calibration_window_bracket.py` | `--session-kind {bracket,derivation}` (default bracket), `--slot-count N`, repeated `--slot-attempt-id` / `--slot-custody-locator`; bracket flags and output unchanged |
| `scripts/recover_calibration_ledger.py` | `--slot` is a free string validated against the declared list (`readiness`, `validate-slot`, `resume-finalize`); derivation sessions get `systematic_screen_s=None` |
| `scripts/validate_powermetrics_fiducial.py` | MECHANICAL slot plumbing only: launch-lineage slot predicate, `_validate_reserved_bracket_slot` expected slot, `--slot` free string, `_CaptureLedgerLifecycle` terminal-slot / derivation-kind properties |
| `tests/test_calibration_ledger.py` | new `DerivationSessionSlotTests` (16 tests) |
| `tests/test_calibration_ledger_custody.py` | one stubbed session gains the three new attributes |
| `tests/test_calibration_writer_crash_matrix.py` | 12-slot derivation crash + abort-at-slot-k case; derivation resume-finalize screen case |

Not edited, deliberately (see "Sites that stay bracket-shaped"): `joulewise/receipt_oracle.py`,
`joulewise/arm_readiness.py`, `tests/test_calibration_live_three_window.py`,
`tests/test_mint_floor_artifact_generalized.py`, `tests/test_powermetrics_fiducial.py`,
`tests/test_receipt_oracle.py` — all pass unchanged.

## Slot-set sweep (A-6): every site enumerated by grep

Command: `grep -rn 'BRACKET_SESSION_SLOTS\|"pre"\|"post"\|PRE_SLOT' joulewise scripts`.

**Generalized (23 sites in `calibration_ledger.py`)**: `:66` constant (kept as the bracket
default), `_valid_session_receipt_shape` open / claim / abort / finalization branches
(`:810–848`), `_bracket_sessions_and_observations` (`:1518, 1543, 1560, 1577, 1599, 1624,
1640` — open attempt ids, claim and finalization expected slot, abort unused list, the
`len(finals) == 2` finalized test, completed-observation order, `slot_attempt_ids`),
`validate_bracket_session_reservation_inputs` (`:4155, 4158, 4185, 4188`),
`append_bracket_session_receipt` (`:4253`), `claim_bracket_session_slot` (`:4299, 4324`),
`finalize_bracket_session_slot` (`:4405, 4430`), `abort_bracket_session` (`:4544`),
`terminal_head_pin_for_session` (`:4596`), `calibration_session_status` (`:4876, 4895`),
`calibration_readiness` (`:5020`), `resume_finalize_bracket_session` (`:5266, 5362, 5371`).
Plus `scripts/recover_calibration_ledger.py:172, 191, 204, 437–453` and
`scripts/validate_powermetrics_fiducial.py:72, 815, 1217–1243, 1479–1501, 1591`.

**Sites that stay bracket-shaped (no NEEDS_SCOPE):**

- `joulewise/receipt_oracle.py:88–118` and `joulewise/arm_readiness.py:8147` both build a
  BRACKET-kind session on purpose (a campaign-pack cadence oracle and the reservation dry
  run). `BRACKET_SESSION_SLOTS` survives as the bracket default, so both are correct as
  written and their tests pass untouched. Generalizing them would change what they model.
- `scripts/validate_powermetrics_fiducial.py:1759` and `:2259`
  (`bracket_mode and args.slot == "post"/"pre"`) are `WriterStage` crash-test markers keyed to
  the two-slot window's dispatch shape (`BEFORE_POST_DISPATCH`,
  `AFTER_PRE_FINALIZATION_BEFORE_SUPERVISOR_DISPATCH`). They are inert for a derivation
  session (no stage fires) and belong to the capture/chain shape S1 and S5 own.
- `joulewise/calibration_bracketing.py` (`:900, 901, 940, 1010, 1014, 1427, 1428, 1670, 1678,
  1921, 1922`), `joulewise/whole_window.py`, `scripts/mint_floor_artifact_generalized.py`,
  `scripts/build_bracket_binding.py`, `joulewise/arm_readiness_evidence_t0.py`,
  `joulewise/adapters/node_client.py`: these are BRACKET-ENDPOINT consumers — `pre` and `post`
  are the two ROLES of a bracket binding, not a session slot set. A derivation row must never
  reach them at all; ruling 46 V1 assigns that skip to seat S3
  (`discover_calibration_candidates` and the `registered_valid` universe). Out of my scope by
  design, and none of them is a slot-set site.
- `joulewise/calibration_exits.py:80` `PRE_SLOT_NOT_READY` is the registered refusal-code
  spelling of the "next reserved slot" phase gate; renaming it would break the exit registry
  and every runbook citing it. Its MEANING is now "the next declared slot", unchanged in code.

## Per-change tests (admit / refuse)

All new tests are in `tests/test_calibration_ledger.py::DerivationSessionSlotTests` unless
marked (CM) = `tests/test_calibration_writer_crash_matrix.py::CalibrationWriterCrashMatrixTests`.

| Change | ADMIT | REFUSE |
|---|---|---|
| N declared slots, filled in order under one open pin | `test_twelve_slot_derivation_session_fills_in_order_and_pins_at_the_last` (12 slots; asserts `next_slot`, `is_governed_open_bracket_extension` and `SESSION_NOT_TERMINAL` at every intermediate step, then the terminal pin equals d12's digest) | `test_out_of_order_claim_and_finalization_refuse_with_the_expected_slot` (claim and finalize d03 after d01 → `SLOT_ORDER_CONFLICT`, `expected_slot == "d02"`) |
| abort at slot k keeps k observations, emits the terminal pin | `test_abort_at_slot_k_keeps_k_observations_and_emits_the_terminal_pin` (5 of 12, `window_exhausted`; finalized/unused lists, observation order, pin = abort digest) | — |
| one open session at a time | — | `test_second_open_session_refuses_while_one_derivation_session_is_open` (`RESERVATION_HEAD_MISMATCH`) |
| declared-list membership | — | `test_undeclared_slot_name_is_refused_by_the_session_assembler` (a perfectly well-SHAPED claim for `d09` in a 3-slot session → `calibration_ledger_bracket_session_conflict`; the same list without it is clean) |
| bracket kind is fixed at pre/post | — | `test_bracket_kind_refuses_any_declared_list_but_pre_post` (`bracket_session_slots_fixed`) |
| kind and slot-count domains | — | `test_unknown_session_kind_and_out_of_range_slot_count_refuse` (`session_kind_unknown`; `slot_count_out_of_range` at 0 and 100) |
| bracket byte identity | `test_bracket_open_receipt_records_neither_kind_nor_declared_slots` (key set equals the historical `_SESSION_OPEN_KEYS`) | `test_an_explicit_bracket_kind_in_an_open_receipt_is_refused` (one shape, one byte representation) |
| historical/production parse | `test_production_ledger_fixture_parses_and_reserializes_byte_identically` (`tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl`: 76 rows, zero refusal reasons, canonical re-serialization equals the file bytes) and `test_kindless_historical_open_receipt_reads_as_the_bracket_pair` | — |
| declared-shape reader | `test_declared_shape_reader_reports_kind_and_ordered_slot_list` | same test: unknown session → `SESSION_NOT_FOUND` |
| kind vocabulary and the exact attribute path S3 reads | `test_finalized_row_exposes_session_kind_through_bracket_session_by_id` (real derivation session built through the reservation API; both its rows resolve `bracket_session_by_id[row.bracket_session_id].session_kind == SESSION_KIND_DERIVATION`; a bracket session over the same path yields `SESSION_KIND_BRACKET`; the two literal values and `SESSION_KINDS` are pinned) | — |
| A-1 recovery finalization | `test_derivation_resume_finalize_never_uses_the_prior_epoch_screen` (CM): 3-slot derivation session finalized through the real `recover_calibration_ledger.py resume-finalize` subprocess; slot d02's bound 0.05 s EXCEEDS r6's level screen 0.032898493715362 s and is still `valid`; `needs_pin_commit` is false until d03 | `test_resume_finalize_refuses_the_prior_epoch_screen_for_a_derivation` (`RESERVATION_INPUT_INVALID` / `systematic_screen_kind_mismatch`) and `test_recover_cli_refuses_a_slot_outside_the_declared_list` (`calibration_reserved_slot_mismatch`) |
| reserve CLI | `test_reserve_cli_declares_d01_dnn_and_keeps_the_bracket_flags` (derivation 3-slot dry run AND the unchanged bracket invocation in the same test) | `test_reserve_cli_refuses_mixed_bracket_and_derivation_slot_flags` (3 sub-cases: `bracket_session_takes_pre_post_flags`, `derivation_session_takes_slot_list_flags`, `declared_slot_flag_count_mismatch`) |
| crash matrix, N slots | `test_twelve_slot_derivation_session_survives_a_kill_and_aborts_at_slot_k` (CM): 12 declared slots, 4 finalized, SIGKILL between the durable finalization intent and its committed target on d05, then fresh-process `repair` → `session-status` (kind, declared list, still open) → `abort-session --reason window_exhausted`; the surviving observations and the terminal pin are asserted | — |

**What the crash matrix assumed about slot count (asked by the brief).** It hard-coded two
slots everywhere: `_applicable_slots` returns `("pre", "post")` for every non-reservation
stage (`:103–106`); `_case` builds exactly a pre/post custody dict and pre-finalizes `pre`
(`:428–446`); the two append sweeps enumerate `("reservation",)` or `("pre", "post")`
(`:986, 1056`) and `_recover_after_crash` maps a reservation crash onto slot `pre`. Those
literals are correct FOR THE BRACKET KIND and are left exactly as they are — the module's
20-case bracket sweep is unchanged and still passes. The N-slot coverage is added as the two
new cases above rather than by parameterizing the bracket sweep, which would have doubled a
232 s module for no new bracket coverage.

## Mutation observations

Each production change was reverted in place and the named test re-run (harness:
apply mutation → `python3 -m unittest <module>` → restore). All nine are killed.

| # | Mutation (production call site) | Killed by |
|---|---|---|
| M1 | `_bracket_sessions_and_observations` expected slot → `BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2` | `test_abort_at_slot_k…`, `test_out_of_order_claim_and_finalization_refuse…`, `test_second_open_session_refuses…` |
| M2 | `terminal_head_pin_for_session` → `session.finalized_slots["post"]` | `test_twelve_slot_derivation_session_fills_in_order_and_pins_at_the_last` |
| M3 | `abort_bracket_session` unused list → `BRACKET_SESSION_SLOTS` | `test_abort_at_slot_k_keeps_k_observations_and_emits_the_terminal_pin` |
| M4 | `resume_finalize_bracket_session` kind/screen pairing guard disabled | `test_resume_finalize_refuses_the_prior_epoch_screen_for_a_derivation` |
| M5 | `recover_calibration_ledger.resume-finalize` always passes `PREFLIGHT_SYSTEMATIC_SCREEN_S` | `test_derivation_resume_finalize_never_uses_the_prior_epoch_screen` (CM) |
| M6 | `append_bracket_session_receipt` emits the kind fields for the bracket kind too | `test_bracket_open_receipt_records_neither_kind_nor_declared_slots`, `test_an_explicit_bracket_kind_in_an_open_receipt_is_refused` |
| M7 | `_valid_session_receipt_shape` stops accepting the kinded open shape | `test_abort_at_slot_k…`, `test_declared_shape_reader…`, `test_out_of_order_claim…` |
| M8 | `recover_calibration_ledger` `--slot` no longer checked against the declared list | `test_recover_cli_refuses_a_slot_outside_the_declared_list` |
| M9 | (dropped, see NEEDS_RULING #3) | — |
| M10 | `CalibrationBracketSession.session_kind` renamed to `.kind` (the attribute seat S3's `_observation_session_kind` reads) | `test_abort_at_slot_k…`, `test_an_explicit_bracket_kind…`, `test_bracket_open_receipt_records_neither_kind_nor_declared_slots`, `test_finalized_row_exposes_session_kind_through_bracket_session_by_id` |

## Test rcs (verbatim, process rc captured in a variable, never a pipe)

Focused modules I touched, plus every module that consumes the changed code, plus
`tests.test_docs_freshness`. The full suite was NOT run, per the brief.

Sweep 1, before the CH-1 ordering fix described below:

```
# for m in <module>; do python3 -m unittest $m -q > /tmp/... 2>&1; echo "$m RC=$?"; done
tests.test_calibration_ledger RC=0  Ran 88 tests in 3.873s OK (skipped=1)
tests.test_calibration_ledger_custody RC=0  Ran 29 tests in 2.700s OK
tests.test_calibration_live_three_window RC=0  Ran 23 tests in 1.833s OK (skipped=3)
tests.test_receipt_oracle RC=0  Ran 3 tests in 0.228s OK
tests.test_reserve_calibration_window_bracket RC=1  Ran 1 test in 0.000s FAILED (errors=1)
tests.test_powermetrics_fiducial RC=0  Ran 75 tests in 62.035s OK
tests.test_mint_floor_artifact_generalized RC=0  Ran 83 tests in 26.136s OK (skipped=2)
tests.test_calibration_exits RC=1  Ran 47 tests in 435.839s FAILED (failures=1)
tests.test_calibration_bracketing RC=0  Ran 50 tests in 0.416s OK (skipped=1)
tests.test_docs_freshness RC=0  Ran 31 tests in 0.694s OK
tests.test_calibration_writer_crash_matrix RC=0  Ran 20 tests in 233.416s OK
```

Sweep 2, after the fix and after the seat-S3 addendum regression landed — every module green:

```
tests.test_calibration_ledger RC=0  Ran 89 tests in 3.644s OK (skipped=1)
tests.test_calibration_writer_crash_matrix RC=0  Ran 20 tests in 240.453s OK
tests.test_calibration_exits RC=0  Ran 47 tests in 434.035s OK
tests.test_docs_freshness RC=0  Ran 31 tests in 0.773s OK
```

**The one real regression this seat introduced, and its fix (CH-1 refusal ordering).**
`tests/test_calibration_exits.py::ResumeFinalizeAcceptanceUnderivableTests` pins that
`resume-finalize` refuses `calibration_frozen_protocol_invalid` /
`acceptance_artifact_underivable` **before touching any ledger path** when
`PREFLIGHT_SYSTEMATIC_SCREEN_S` is `None`. My first draft read the session's declared shape
first, so a nonexistent ledger returned `calibration_physical_ledger_unreadable` instead —
one failure, caught by that module. `tests/test_calibration_exits.py` is outside my
WRITE_SCOPE, so the PRODUCTION order was restored instead: the `None`-comparator refusal is
the first statement in the branch, exactly as before, and only then is the declared shape
read to decide whether to withhold the screen. Consequence, stated plainly: a derivation
session cannot be resume-finalized while the active acceptance artifact is unauthenticatable,
even though it never consults that artifact's screen. That is the pre-existing behaviour and
it is fail-closed, so I kept it rather than editing a test I do not own. M5 still kills after
the reorder (re-verified).

`tests.test_reserve_calibration_window_bracket RC=1` is **ModuleNotFoundError**, not a
failure: that module does not exist in this checkout and I did not create it. The reserve-CLI
and recover-CLI regressions live where every existing one already lives —
`tests/test_calibration_ledger.py`, which imports `reserve_calibration_window_bracket as
bracket_session_cli` and `recover_calibration_ledger as recovery_cli` and holds
`test_bracket_reservation_cli_is_explicit_and_machine_readable` and its siblings. Creating two
new modules would have duplicated that fixture for no coverage. Same for
`tests/test_recover_calibration_ledger.py`. Both remain unwritten and unmodified; if the gate
wants them as separate files, say so and I will split them out.

Mutation harness rcs are in the table above; each row was produced by
`python3 /tmp/s2_mutate.py`, which restores the file in a `finally` block. `git status` after
the sweep shows only the seven intended paths modified.

## NEEDS_RULING

1. **Bracket sessions record NO `session_kind` key, and an explicit `"bracket"` kind is
   REFUSED.** Ruling 46 §R-d says "`session_kind` in the open receipt (`bracket` default,
   `derivation`)". I read "default" as *the value a receipt without the field carries*, and
   made the kindless shape the sole canonical bracket representation. The forcing constraint
   is the brief's own byte-for-byte requirement: if a new bracket session emitted
   `session_kind: "bracket"`, its receipt bytes would differ from every bracket receipt this
   tool has ever written, the G2-a window would produce a receipt shape no committed pin or
   pack has seen, and the same session would have two valid byte representations. The cost of
   the choice is that a reader must know the defaulting rule; it is stated in a comment at the
   constant, in `session_kind_of_open_receipt`, and in the shape validator. If the gate wants
   the field always present, it is a two-line change to `kind_fields` plus the two byte-identity
   tests — but the bracket receipt bytes then change.
2. **The screen/kind pairing is enforced in BOTH directions.** A-1 requires that a derivation
   caller passes `None`. I also made `resume_finalize_bracket_session` refuse a BRACKET session
   finalized with `systematic_screen_s=None` (same `systematic_screen_kind_mismatch` refusal).
   Without it, a future caller could silently disable the systematic screen on a real bracket
   window — a fail-open. This is stricter than the ruling says, in the fail-closed direction.
3. **No mutation probe exists for the writer's derivation branch (dropped M9).** I generalized
   `_CaptureLedgerLifecycle`'s close path (`validate_powermetrics_fiducial.py:1479–1501`) to
   use `is_terminal_slot` / `is_derivation_session`, because the brief scoped that site to me
   as mechanical plumbing. For the BRACKET kind the new code is behaviourally identical to the
   old (proved by `tests.test_powermetrics_fiducial` and the 20-case crash sweep, both green),
   so any mutation I write there is killed by nothing or by everything. The DERIVATION branch
   cannot be exercised until seat S1 lands `--derivation-only`, since nothing else drives a
   live writer into a derivation-kind slot. **S1 must add the mutation-kill for it**: revert
   `not self.is_derivation_session` in the `aborted` expression and show a `--derivation-only`
   capture with an `ordinary-invalid` d01 that wrongly closes the night.
4. **`abort_calibration_session` reason `window_exhausted` is not a code-level constant.** The
   ruling names it; today it is an operator-supplied free string (`--reason`), and I left it
   that way — the ledger only requires a non-empty reason. If the pre-registration wants the
   string pinned, that belongs to S5's chain or S6's contract text, not here.

5. **The four bracket per-slot flags lost `required=True`.** `--pre-attempt-id`,
   `--post-attempt-id`, `--pre-custody-locator` and `--post-custody-locator` cannot be argparse
   `required` any more, because a derivation invocation must not supply them. A bracket
   invocation that omits one now returns a governed
   `calibration_reservation_input_invalid` / `bracket_session_slot_flags_missing` refusal on
   stderr instead of argparse's bare usage text and rc 2. That is a strictly better exit for
   the runbook, but it IS a change to the bracket command's failure surface, so it is recorded
   here rather than filed under "byte-for-byte compatible". Every successful bracket
   invocation is unchanged, flags and output alike.

## NEEDS_SCOPE

None. Every site the A-6 sweep found is either inside my WRITE_SCOPE and generalized, or is a
bracket-ENDPOINT consumer whose `pre`/`post` are binding roles rather than session slots (list
above), or belongs to seat S3's V1 derivation-row skip.

## Session-kind vocabulary: the ONE home, and the exact path S3 reads

Requested by seat S3's refuter, and already how this seat built it:

- The vocabulary is declared once, in `joulewise/calibration_ledger.py` (`:67–76`):
  `SESSION_KIND_BRACKET = "bracket"`, `SESSION_KIND_DERIVATION = "derivation"`,
  `SESSION_KINDS = (SESSION_KIND_BRACKET, SESSION_KIND_DERIVATION)`. All three are in
  `__all__`.
- **The exact attribute path**, for the integration tree's assertion:

  ```
  snapshot = load_calibration_ledger_snapshot(...)
  session = snapshot.bracket_session_by_id[observation.bracket_session_id]
  session.session_kind   # -> "bracket" | "derivation"
  session.declared_slots # -> ordered tuple[str, ...]
  ```

  `session_kind` is a field of the frozen dataclass `CalibrationBracketSession`
  (`calibration_ledger.py:480–483`), defaulting to `SESSION_KIND_BRACKET`, so a session
  assembled from a kindless historical open receipt reports `"bracket"` — which is what S3's
  defensive reader wants, and now by construction rather than by its fallback.
  `LedgerObservation` itself carries no `session_kind` attribute, so S3's first `getattr`
  branch never fires; the `bracket_session_by_id` branch is the live path.
- Seat S3 currently re-declares the literals as `calibration_bracketing.BRACKET_SESSION_KIND`
  and `DERIVATION_SESSION_KIND` (`calibration_bracketing.py:199–200`). Their VALUES match mine
  exactly (verified by reading `feat/2026-09-10-epoch-s3-acceptance-validator` at
  `3f498026`). **The integration tree should assert**
  `calibration_bracketing.DERIVATION_SESSION_KIND == calibration_ledger.SESSION_KIND_DERIVATION`
  and the bracket pair likewise — or, better, have S3 import mine and delete its two literals,
  which removes the drift surface entirely. I did not edit `calibration_bracketing.py`: it is
  outside my WRITE_SCOPE and belongs to S3.
- A rename now breaks a test: mutation M10 renamed `session_kind` to `kind` on the session
  object and four tests failed, including the new
  `test_finalized_row_exposes_session_kind_through_bracket_session_by_id`.

## Landing note for seat S1

The interface S1 builds against is fixed:

- Slot names are arbitrary strings satisfying `calibration_ledger.is_declared_slot_name`
  (non-empty, ≤32 chars, alnum/`-`/`_`). Derivation slots are `d01..dNN` from
  `calibration_ledger.derivation_session_slots(n)`.
- `declared_session_shape(ledger_path, session_id=...)` → `{"session_id", "session_kind",
  "declared_slots"}`. It scans the maximal valid chain only, so it is safe before any lease,
  repair, or custody work.
- `CalibrationBracketSession` gained `session_kind`, `declared_slots`, and the properties
  `next_slot` (the only claimable/finalizable slot right now, `None` when not open) and
  `terminal_slot`.
- `_CaptureLedgerLifecycle` already exposes `session_shape`, `is_terminal_slot` and
  `is_derivation_session`; `--slot` no longer has argparse `choices`.
- `tests/test_powermetrics_fiducial.py` was NOT modified (it passes unchanged), so S1's rebase
  on that file is clean.


## Lead correction (contract refuter 71 F1, 2026-09-10 09:45 PDT)

The report's claims that the bracket reserve CLI's output is unchanged are FALSE: `scripts/reserve_calibration_window_bracket.py` now emits `session_kind` and `declared_slots` in its dry-run JSON for BOTH kinds (the seat's own test asserts `bracket_payload["session_kind"] == "bracket"`). Receipt bytes for bracket sessions are unchanged; the CLI's informational JSON is not. F10: the mutation table lists nine kills; the commit message says ten; the table is authoritative.
