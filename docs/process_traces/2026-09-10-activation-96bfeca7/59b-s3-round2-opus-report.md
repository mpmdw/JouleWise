# 59 — Seat S3 (Claude Opus, replacing the Astra seat) — generation-keyed issuance validation

Lane ACCEPTANCE-EPOCH-25G83-01. Worktree `/Users/edr/code/JouleWise-wt-s3-acceptance-validator`,
branch `feat/2026-09-10-epoch-s3-acceptance-validator` at main `7c4366ec`. No git write of any kind:
the diff is left in the working tree (`git diff --name-only` = the two files below).
Authority: cold-gate ruling 46 §R-a A2/A5/A6, §R-b V1/V6/V7, §R-d row S3; addendum 11 A-3, A-5, A-7.

## Summary

`_valid_acceptance_bound` no longer carries the single-epoch, 38-row, sequence-76, import-only,
range-equals-screen literals. Each is now a field of the artifact's OWN registered generation row in
`_D102_GENERATION_DERIVATIONS`, so r3–r6 keep validating against exactly the fence they were derived
under while a successor derived from a live corpus on a changed identity epoch can register its own.
Two new corpus-membership fences were added (purity, completeness) and the derivation-kind endpoint
barrier was installed at every site of the anti-withholding universe — three sites, not the two the
ruling named (see "Beyond the named footprint").

Nothing about the successor generation is registered: `_D102_GENERATION_DERIVATIONS` still holds six
rows, all `import_only`, all with an empty `registration_session_ids`. The `import_plus_live` machinery
is exercised only by a generation registered inside a test's `with` block. That data rides the D-138
transaction, per the ruling's landing order.

## Changed paths

- `joulewise/calibration_bracketing.py` (+368 / −16)
- `tests/test_calibration_bracketing.py` (+783)

No other file in the WRITE_SCOPE needed a change; nothing outside it was touched. See "NEEDS_SCOPE".

## What changed, mechanism by mechanism

**Generation-row schema (§R-d row S3; A-3).** Every row gains `epoch_catalog_ids`,
`prior_prefix_mode`, `prior_observation_count`, `cutoff_sequence`, `screen_rule`,
`inherited_ceiling_s`, `registration_session_ids`. Both existing derivations register their current
literals: `("d079_epoch",)`, `import_only`, `38`, `76`, `range_equals_screen`, `()`.
`inherited_ceiling_s` is A-3's schema slot: each row carries its own 99 % two-draw prediction (n19
`0.012093166090593858`, n17 `0.010164834757777545`), which is the ceiling a D-125 successor lineage
inherits as a lower bound. Nothing in this module compares it — seat S4 owns
`successor_screen_exceeds_budget_ceiling`. A new `_registered_generation_row_is_complete` refuses any
row that omits or malforms one of the fields, so a forgotten field refuses rather than letting the
corresponding check evaporate.

**Target epoch is DERIVED, not registered.** The old code asserted
`epoch_catalog == {"d079_epoch"}` and `epoch_catalog["d079_epoch"] == identity`. The new code asserts
`set(epoch_catalog) == set(generation["epoch_catalog_ids"])` and that EXACTLY ONE catalog entry equals
the artifact's `identity_epoch`; that entry is the target epoch. This is why no `target_epoch_id`
registry field was needed: registering it would have created a second place for the catalog and the
identity to disagree. Per-row `epoch_id` is now checked for membership in the registered catalog
rather than against the literal.

**Purity (§R-a A6).** Every corpus member's own prior-set row (matched by the content id derived from
the member's two artifact hashes) must carry the TARGET epoch. A non-member row of another registered
epoch is admitted — that is precisely what a two-epoch catalog exists to carry.

**Completeness (§R-a A6, A-7).** For `import_plus_live` generations only. Ranges over prior-set rows
that are `valid` AND carry the target epoch AND belong to a session in `registration_session_ids`;
a valid target-epoch row whose `session_id` is outside the registration REFUSES issuance rather than
being absorbed. Each remaining row is a corpus member or an entry in
`derivation_notes.excluded_members` with keys exactly
`{member_id, manifest_sha256, instrument_evidence_sha256, reason}` and a reason in
`REGISTERED_CORPUS_EXCLUSION_REASONS` (today: `affine_clock_fit_empty` alone). Entries carry no content
id, so they are matched into the prior set by the id derived from the two hashes, per A-7. The final
fence is a set identity, not a subset test: `members | excluded == registration_valid`, members and
excluded disjoint, exclusions distinct. That kills both directions — a withheld valid row and a
phantom exclusion naming no prior row.

**Prior-set row schema for live generations.** A-7's completeness check needs to know which session a
prior-set row came from, and the artifact's prior-set rows carried only
`{content_id, epoch_id, disposition, attempt_id}`. For `import_plus_live` generations the row schema
therefore requires a fifth key, `session_id` (a non-empty string, or `null` for an imported row), and
`_prior_set_matches_import_cutoff_prefix` compares it against the ledger row's `bracket_session_id`.
Without that comparison `registration_session_ids` would be an assertion the artifact makes about
itself; with it, the registration is ledger-bound. Import-only artifacts keep the exact four-key
schema and the exact four-tuple comparison they have today. **This is the row-schema decision seat S4
depends on** (ruling: "S4 once S3 fixes the row schema").

**Prefix mode (§R-b V6).** `_prior_set_matches_import_cutoff_prefix` resolves the generation from the
artifact's own id and keys on `prior_prefix_mode`. Import-only: a single live row in the prefix refuses,
unchanged. Import-plus-live: a live row is admitted when it has a content id and a terminal disposition
in `{valid, systematic-invalid, ordinary-invalid}` — which admits the finalized slots of an abort-closed
session, since those are ordinary finalized observations — while a pending row (no content id) and an
`abandoned` row (classification `unresolved`) still refuse. An unregistered acceptance id never matches
any prefix.

**Screen rule (§R-b V7).** The range-equals-screen comparison is now gated on
`screen_rule == range_equals_screen`. Only that rule is implemented; the D-125 envelope rule is Ed's
open item and its refusal is S4's, so a generation registering any other name refuses at the comparison
site instead of silently degrading to this one. The registry vocabulary
(`_REGISTERED_SCREEN_RULES`) is a second, independent fence.

**Derivation-kind endpoint barrier (§R-b V1).** `_observation_session_kind` resolves a row's kind
defensively: the observation's own `session_kind` attribute if seat S2 puts it there, else the
`session_kind` of the session named by `bracket_session_id`, else `bracket`. A missing field is read as
`bracket`, so a ledger written before S2's field existed is unaffected. `_is_derivation_kind_observation`
is consulted with `continue` / `and not ...` — never `return None`, which would empty discovery
entirely — at both named sites and at one further site described below.

## Beyond the named footprint (flagged for the refuters)

The ruling names two sites of the anti-withholding universe: `discover_calibration_candidates`
(orig. `:1330-1336`) and the `registered_valid` set in `evaluate_calibration_bracket`
(orig. `:1597-1610`). There is a THIRD, inside `calibration_bracket_for_bundles` (orig. `:2105-2119`,
now `:2461-2481`): a `registered_valid` COUNT compared against `len(candidates)` from the same
discovery call, refusing `calibration_ledger_custody_invalid` on inequality. Left unchanged it would
have refused every claim window on the machine for as long as a derivation row is on the ledger — that
is, forever. I added the same skip there and a test that names it. This is inside my WRITE_SCOPE
(same file) and is the same mechanism, not a new one; recording it because it is a site the ruling did
not enumerate.

## Tests — admit / refuse pairs

New class `GenerationKeyedIssuanceValidationTests` (18 tests) and three methods added to
`CalibrationBracketingTests`.

Regression that fences the whole seat:
- `test_every_issued_generation_and_genesis_fixture_load_byte_identically` — sweeps EVERY
  `configs/calibration/calibration_acceptance_*.json` (6 artifacts: v2, v2_r2, r3, r4, r5, r6), asserts
  the file sha256 equals its registry pin, that the loaded object equals the raw JSON, and that
  `_valid_acceptance_bound` admits it; then the genesis fixture bytes and their sha256 pin.

| Check | Admit | Refuse |
|---|---|---|
| epoch catalog | `test_two_epoch_catalog_admits_and_an_unregistered_catalog_refuses` (two-epoch import-only generation admits) | same test (catalog narrowed; catalog widened with an unregistered id); `test_catalog_that_names_no_entry_equal_to_the_bound_identity_refuses` |
| purity | `test_corpus_purity_refuses_a_member_row_from_another_epoch` (a NON-member row of the other epoch still admits) | same test (a MEMBER's prior row flipped to the other epoch) |
| completeness | `test_live_prefix_generation_admits_with_its_named_exclusion`; `test_completeness_does_not_range_over_the_predecessor_epoch` (30 valid old-epoch rows, none a member, no exclusion demanded) | `test_completeness_refuses_an_unaccounted_valid_registration_row`; `test_completeness_refuses_an_unregistered_exclusion_reason`; `test_completeness_refuses_an_exclusion_that_names_no_prior_row`; `test_valid_same_epoch_row_outside_the_registration_refuses_issuance` |
| prefix mode | `test_import_only_prefix_still_refuses_a_single_live_row` (all-import admits); `test_live_prefix_admits_finalized_rows_and_refuses_unresolved_ones` (admits) | same tests (one live row under import-only; an `abandoned`/`unresolved` row; a pending row with no content id); `test_live_prefix_binds_every_row_to_the_session_it_declares`; `test_unregistered_generation_never_matches_a_prefix` |
| registered counts | `test_registered_cutoff_sequence_is_read_from_the_row_not_a_literal` (r6 admits under its own row) | same test (`cutoff_sequence` 80, `prior_observation_count` 39) |
| row schema | `test_every_registered_generation_row_carries_the_full_schema` | `test_generation_row_missing_a_fence_refuses_rather_than_defaulting` (each of the 7 new fields dropped in turn) |
| screen rule | — | `test_unimplemented_screen_rule_refuses_instead_of_falling_back` (vocabulary widened so ONLY the comparison site can refuse; then the vocabulary fence alone) |
| endpoint barrier | `test_derivation_night_row_never_becomes_a_claim_endpoint` (window still passes, no off-ledger refusal); `test_derivation_night_row_is_skipped_by_the_bundles_universe_count` | same tests (the row is absent from discovery; A-5's one-sided-skip counterfactual) |

The synthetic `import_plus_live` generation (`_live_prefix_generation`) is registered ONLY inside the
test's `with` block, via `patch.dict` over `_D102_GENERATION_DERIVATIONS` and
`ISSUED_ACCEPTANCE_REGISTRY`. Its shape mirrors the real successor: 38 imported genesis rows under the
OLD epoch, a 3-member corpus captured live under `25G83` inside one registered derivation session, one
valid same-session row excluded by `affine_clock_fit_empty`, one `ordinary-invalid` row.

The derivation session object in the barrier tests is a duck-typed `SimpleNamespace` carrying
`session_kind` — deliberately, because that is also the shape tolerance the defensive reader must have
against seat S2's not-yet-landed field.

## Mutation observations

Each new or generalized check was reverted at its production call site in
`joulewise/calibration_bracketing.py`, the naming test run alone, and the file restored (script kept at
`/tmp/s3_mutations.py`; it asserts byte-identical restoration at exit and printed `restored: True`).
16/16 KILLED.

| Mutation (production call site) | Naming test | rc |
|---|---|---|
| catalog ids ← literal `{"d079_epoch"}` (`_valid_acceptance_bound`) | `test_two_epoch_catalog_admits_and_an_unregistered_catalog_refuses` | 1 |
| `len(target_epoch_ids) != 1` deleted | `test_catalog_that_names_no_entry_equal_to_the_bound_identity_refuses` | 1 |
| per-row `epoch_id` ← literal | `test_live_prefix_generation_admits_with_its_named_exclusion` | 1 |
| prior-set size / cutoff sequence ← literals `38` / `2*len` | `test_registered_cutoff_sequence_is_read_from_the_row_not_a_literal` | 1 |
| `_registered_generation_row_is_complete` guard deleted | `test_generation_row_missing_a_fence_refuses_rather_than_defaulting` | 1 |
| purity loop deleted | `test_corpus_purity_refuses_a_member_row_from_another_epoch` | 1 |
| completeness block disabled | `test_completeness_refuses_an_unaccounted_valid_registration_row` | 1 |
| registered exclusion reasons ← any string | `test_completeness_refuses_an_unregistered_exclusion_reason` | 1 |
| outside-the-registration refusal deleted | `test_valid_same_epoch_row_outside_the_registration_refuses_issuance` | 1 |
| screen-rule dispatch deleted | `test_unimplemented_screen_rule_refuses_instead_of_falling_back` | 1 |
| prefix fence ← `live_prefix_allowed = True` (`_prior_set_matches_import_cutoff_prefix`) | `test_import_only_prefix_still_refuses_a_single_live_row` | 1 |
| live-prefix terminal-disposition clause deleted | `test_live_prefix_admits_finalized_rows_and_refuses_unresolved_ones` | 1 |
| per-row session-id tuple element dropped | `test_live_prefix_binds_every_row_to_the_session_it_declares` | 1 |
| derivation skip removed at `discover_calibration_candidates` ONLY | `test_derivation_night_row_never_becomes_a_claim_endpoint` | 1 |
| derivation skip removed at the `registered_valid` universe ONLY (A-5's counterfactual) | `test_derivation_night_row_never_becomes_a_claim_endpoint` | 1 |
| derivation skip removed at the `calibration_bracket_for_bundles` count ONLY | `test_derivation_night_row_is_skipped_by_the_bundles_universe_count` | 1 |

The screen-rule dispatch SURVIVED on the first sweep: `_registered_generation_row_is_complete` already
refused the unknown rule name upstream, so the dispatch was unreachable in that counterfactual. The
test was rewritten to widen `_REGISTERED_SCREEN_RULES` for the duration of the assertion, which leaves
the comparison site as the only thing that can refuse; it then killed. The original vocabulary fence is
still asserted in the same test's second half. Recording this because it is exactly the "the cure did
not name the counterfactual input" failure mode.

## Test rcs (verbatim, captured in shell variables)

```
test_calibration_bracketing         rc=0 :: Ran 70 tests in 0.416s  OK (skipped=1)
test_calibration_live_three_window  rc=0 :: Ran 23 tests in 1.951s  OK (skipped=3)
test_paper_first_use_ledger         rc=0 :: Ran 11 tests in 1.885s  OK
test_floor_mint_pinsets_schema      rc=0 :: Ran  1 test  in 0.000s  OK
test_docs_freshness                 rc=0 :: Ran 31 tests in 0.761s  OK
python3 -m compileall -q joulewise tests            rc=0
python3 scripts/gen_state.py --check                rc=0
```

`tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact <r6>` exits rc=1 in this
worktree with `FileNotFoundError: .../runs_window_a_20260722` — the corpus verifier resolves the
member run bundles under the repo root, and the custody bundles are not in a linked worktree. That is
environmental, not a regression: I did not modify that file (`git diff --name-only` lists two files),
and the check it performs is over member hashes and the prior set, neither of which this diff moves.
It needs a canonical-checkout run to be exercised.

Not required by the brief, run as insurance because the changed functions are consumed outside the
focused modules (`grep -l` over `tests/` for `_valid_acceptance_bound`,
`discover_calibration_candidates`, `calibration_bracket_for_bundles`,
`_prior_set_matches_import_cutoff_prefix`):

```
tests.test_calibration_ledger tests.test_mint_floor_artifact_generalized
tests.test_whole_window tests.test_whole_window_selection
tests.test_check_window_provenance tests.test_custody_mode_inventory
                                    rc=0 :: Ran 313 tests in 209.985s  OK (skipped=3)
```

The four remaining consumers (`test_analysis_finalizer`, `test_analysis_integration`,
`test_floor_extraction`, `test_run_campaign`) were NOT run — the brief forbids the full suite and
these are the long ones. They are the residual coverage gap in this seat's own verification.

## NEEDS_SCOPE

None. The census flagged four files as possible literal pins; all four were inspected and none needed
a change:

- `tests/test_calibration_live_three_window.py:331-333, :435` pin the epoch catalog as
  `{"d079_epoch": <epoch>}` and the per-row `epoch_id` as `"d079_epoch"`. Those literals remain CORRECT
  under the generalization, because the fixtures build predecessor-generation artifacts whose registered
  `epoch_catalog_ids` is exactly `("d079_epoch",)` and whose identity equals that catalog entry. The
  module passes unmodified (rc 0, 23 tests), so the scope ruling's licence was not needed, and seat S2's
  slot-name lines are untouched.
- `tests/test_paper_first_use_ledger.py` and `tests/test_floor_mint_pinsets_schema.py` contain no epoch
  catalog or registry literal at all; both pass unmodified.
- `tests/verify_calibration_acceptance_corpus.py` reads the prior set by content id and pins only the
  banked per-generation statistics; it has no epoch-catalog or prior-size literal. Its
  `stored_lexeme_is_member_value` row for the successor rides the D-138 transaction, per the ruling.

## NEEDS_RULING

Three items where I made a call the ruling did not spell out. None contradicts it; all are recorded so
the refuters can overturn them cheaply.

1. **The prior-set row gains a `session_id` key for `import_plus_live` generations.** A-7's
   completeness check ranges over rows "of a session of this registration", but the artifact's
   prior-set rows carry no session at all, and `_valid_acceptance_bound` has no ledger access. The
   alternatives were to move the check to a ledger-bearing site (contradicting the §R-d footprint,
   which names `:605-607`) or to trust `registration_session_ids` as an unverified assertion. I chose
   the fifth key plus a ledger comparison in the prefix matcher. Import-only artifacts are unaffected.
   **Seat S4 must emit this key**; it is the row-schema dependency the landing order names.
2. **The third universe site.** Added beyond the two the ruling enumerates; see above.
3. **`screen_rule` has exactly one implemented value.** I did NOT implement V7's
   `max(quantized range, 0.010818)` rule, because V7 is proposed-not-ratified and awaits Ed. The slot
   is keyed and fail-closed; whoever registers a successor under the D-125 envelope must implement the
   branch, which is the handoff A-3 describes to S4.

Also recorded, not blocking: the ruling's line numbers are from `origin/main` before this diff; the
`:562` per-row epoch check is at `:566` on `7c4366ec` (the other cited offsets match).

---

# Fix round 1 (contract refuter: MERGEABLE AFTER FIXES)

Applied on top of `3f498026` in the same worktree; the diff is again left uncommitted
(`git status --short` = the same two files). F2 (integration test with a real derivation session) and
F4 (the contract's fifth binding) were routed elsewhere and are not touched here.

## F1 — `registration_session_ids` must name DERIVATION-kind sessions

`_prior_set_matches_import_cutoff_prefix` now resolves every id in
`generation["registration_session_ids"]` through `ledger_snapshot.bracket_session_by_id` and refuses
unless the ledger holds that session AND its kind is `derivation`. A session the ledger does not hold
refuses; a session whose kind field is missing reads as `bracket` through the same defensive reader
and refuses.

The kind reader was split so both callers share it: `_session_record_kind(session)` (the defensive
`getattr` with the `bracket` default) is now the one home, and `_observation_session_kind` delegates to
it after resolving the row's session.

Scope note for the refuters: the check is on the REGISTRATION, not on every live prefix row. Requiring
`derivation` kind of *every* live row in an `import_plus_live` prefix would also refuse the ordinary
claim-window captures that sit on the ledger between sequence 76 and the derivation nights, which would
make the successor unissuable. The named defect — "`registration_session_ids` must name derivation-kind
sessions" — is closed exactly, and the per-row `session_id` binding added in the first round already
forces a registration row to be one of those sessions.

New: `test_registration_must_name_derivation_kind_sessions` (admit: derivation kind; refuse: `bracket`
kind, missing kind, session absent from the ledger). `_prefix_snapshot` gained a `session_kind`
parameter and now builds the session records the prior set names.

## F3 — `inherited_ceiling_s` is checked, not trusted

`_registered_generation_row_is_complete` now requires, by Decimal equality,
`inherited_ceiling_s == operatives["maximum_budgetable_drift_s"] == prediction_99_two_draw_s`, and
requires the operative screen to sit STRICTLY below that ceiling
(`bracket_screen_s < maximum_budgetable_drift_s`).

**The refuter was right that the field was unvalidated, and it was carrying a real defect**: my own
`_live_prefix_generation` fixture registered `inherited_ceiling_s` `0.010164834757777545` (r6's number,
copied) against its own `maximum_budgetable_drift_s` `0.009000`, and the code accepted it. The fixture
now registers `0.009000` and the guard would refuse the old value.

Reading recorded for overturn: I applied the strict `screen < ceiling` inequality to EVERY registered
row, not only to rows registering an envelope screen rule. All three current rows satisfy it
(n19 `0.010818 < 0.012093166090593858`; n17 `0.009724 < 0.010164834757777545`; the test fixture
`0.006000 < 0.009000`), it is fail-closed, and it is the same relation `screen + excess == maximum` at
the bottom of `_valid_acceptance_bound` already implies for a non-negative excess. Narrow it to
envelope-rule rows if that was the intent.

New: `test_generation_row_refuses_a_desynchronised_inherited_ceiling` (each of the three copies moved
in turn) and `test_generation_row_refuses_a_screen_at_or_above_its_ceiling` (admit at a ceiling one
millisecond above the screen, refuse at a ceiling equal to it).

## F5 — the `cutoff_sequence == 2 x prior_observation_count` relation

Restored inside `_registered_generation_row_is_complete`, for `import_only` generations only: one
reservation row plus one finalization row per imported observation. It is deliberately NOT imposed on a
live prefix, whose sessions add open and abort control rows the observation count does not predict —
`test_import_only_cutoff_sequence_is_two_rows_per_observation` asserts both halves (an import-only row
at 77/38 refuses; a live row three control rows past twice its count admits).

## F6 / F9 — comments

- The stale citation `(:1339-1341)` is replaced by a description of the actual site ("the `return ()`
  on a `None` candidate at the bottom of this loop"), which cannot drift with line numbers.
- `affine_clock_fit_empty` is now glossed at its first use: the anchor-v3 replay found NO feasible
  affine wall-versus-monotonic clock fit for that capture, so no bound can be derived from it at all,
  and the exclusion turns on that replay outcome rather than on the value produced.
- The ephemeral seat-role names are gone: "seat S2 stamps" became "stamped on the session's open
  receipt by the ledger writer", and the two "seat S4's issuer" references became the mechanism
  ("the issuer that derives the successor reads it from here", "not implemented in this module").

## Mutation sweep, re-run in full

20 mutations, **20/20 KILLED** (`/tmp/s3_mutations.py`, byte-identical restoration asserted at exit:
`restored: True`). The four new entries:

| Mutation (production call site) | Naming test | rc |
|---|---|---|
| registration derivation-kind check deleted (`_prior_set_matches_import_cutoff_prefix`) | `test_registration_must_name_derivation_kind_sessions` | 1 |
| `ceiling != drift or drift != prediction` deleted (`_registered_generation_row_is_complete`) | `test_generation_row_refuses_a_desynchronised_inherited_ceiling` | 1 |
| `not screen < drift` deleted | `test_generation_row_refuses_a_screen_at_or_above_its_ceiling` | 1 |
| the 2-rows-per-observation relation deleted | `test_import_only_cutoff_sequence_is_two_rows_per_observation` | 1 |

**Three first-round counterfactuals were masked by the new upstream checks and had to be re-cut** —
the same failure mode the first round's screen-rule survivor showed, and worth recording as a pattern:
adding a fence upstream silently blunts every counterfactual that reached the old fence through it.

1. `test_registered_cutoff_sequence_is_read_from_the_row_not_a_literal` moved `cutoff_sequence` alone,
   which the new F5 relation now refuses before the artifact comparison is reached. It now moves
   `cutoff_sequence` and `prior_observation_count` together (80/40), keeping the row internally
   consistent so only the comparison against the ARTIFACT can refuse.
2. The `screen < ceiling` counterfactual first changed the screen in the ROW only; the artifact's own
   `ratified_operatives` then disagreed and refused downstream. It now retunes the row and the artifact
   to the same ceiling together, so the strict inequality is the only clause left.
3. The F5 counterfactual first used the r6 artifact, whose 38 rows and sequence 76 cannot violate the
   relation without also violating the row-versus-artifact comparison. It now uses the synthetic
   import-only artifact with both sides moved to 77.

## Test rcs (verbatim, rc captured in `RC`)

```
python3 -m unittest tests.test_calibration_bracketing tests.test_calibration_live_three_window \
    tests.test_paper_first_use_ledger tests.test_floor_mint_pinsets_schema tests.test_docs_freshness
FIXROUND1_RC=0 :: Ran 140 tests in 4.837s  OK (skipped=4)

python3 -m compileall -q joulewise tests   rc=0
python3 scripts/gen_state.py --check       rc=0
```

`tests.test_calibration_bracketing` is now 74 tests (22 in
`GenerationKeyedIssuanceValidationTests`). The byte-identical sweep over every artifact under
`configs/calibration/` and the genesis fixture still passes unchanged, which is the fence that matters:
none of these four fixes moved an issued byte.

---

# Fix round 2 (cold-gate ruling 69 §Q1 "Ruled relation (option iii)"; S2 contract refuter 71 F4/F5)

Applied on top of `93799321` in the same worktree; the diff is again left uncommitted (same two files).

**Addendum not found.** `69-coldgate-packet-s3-envelope-clause/11-ruling-addendum-opus-amendments.md`
does not exist in the bookkeeping worktree (that directory holds `00-PACKET.md`, the ruling, exhibits
A–D, and the convene log; the only file of that name in the activation trace belongs to packet 46).
I implemented from ruling 69 §Q1 plus the coordinator's message, which restates A4's substance —
the `predecessor_acceptance_id` back-reference, the `is None`-before-`_decimal` ordering, and the
unresolvable-predecessor refusal. **If A4 says anything more, this round has not seen it.**

## 1. `inherited_ceiling_s` retired; the ruled relation installed

The field is gone. The row now carries `predecessor_ceiling_s` — the ceiling in force of the
generation this one was derived FROM under D-125's envelope rule, as a Decimal string, or `None` for a
generation not derived under that rule — and, when it is not `None`, `predecessor_acceptance_id` naming
the predecessor's registered row. `predecessor_ceiling_s` stays in `_GENERATION_ROW_REQUIRED_KEYS`;
`predecessor_acceptance_id` is required only when a predecessor is declared.

The clause is now the ruling's one line:

```python
or drift != (prediction if predecessor is None else max(predecessor, prediction))
```

with `screen is None or not screen < drift` retained unchanged and universal. The invented
`drift == prediction` equality is gone — that was the term whose only isolating refusal was a
legitimate envelope successor, which is the defect ruling 69 found.

**Both registered rows set `predecessor_ceiling_s = None`, and the code says why.** The n=19 corpus is
the genesis: no predecessor at all. The anchor-v3 r-series is a re-derivation of the same captures
under changed estimator bytes (D-145), not a D-125 envelope successor of n=19 — its ceiling is its own
Q99 and sits BELOW n=19's, so registering n=19 as its predecessor would refuse it, correctly. `None`
is the truthful registration in both cases, and for both the relation collapses to
`ceiling == own Q99`, which all six issued artifacts satisfy.

Absent and malformed stay different facts: `predecessor_ceiling_s is None` is tested BEFORE `_decimal`
is called, so a present non-string (`0`, a `Decimal`) or an unparseable string never reaches the
"absent" branch. A declared predecessor whose registered row cannot be resolved, or whose row's
`operatives.maximum_budgetable_drift_s` differs, refuses.

**One redundancy removed after the sweep found it** (see below): the standalone
`if predecessor is None: return False` immediately after `_decimal` was dead — a malformed value parses
to `None`, and no registered Decimal equals `None`, so the read-back comparison already refused every
input that term could refuse. It is gone; the comment at the read-back states the reasoning. The ruled
BEHAVIOUR is unchanged and still asserted by test.

## 2. Tests — the four counterfactuals from §Q1, plus two

Each moves the ARTIFACT with the ROW (a row-only move is refused upstream by the row-versus-artifact
comparisons of the 99 % prediction and the operatives, and proves nothing about this clause — the D2
defect), retunes `max_budgetable_excess_s` so `screen + excess == maximum` still holds, and leaves the
screen at `0.006000` so `screen < ceiling` still holds. A `_predecessor_row` context manager registers
the predecessor generation the lineage is read back from.

| Case (predecessor / own Q99 / ceiling) | Test | Verdict |
|---|---|---|
| `0.009` / `0.008` / `0.009` — inherited ceiling won the max | `test_envelope_ceiling_equals_max_of_predecessor_and_own_q99` | ADMIT (the HEAD clause wrongly refused this) |
| `0.0095` / `0.008` / `0.009` — ceiling fell below its predecessor's | `test_envelope_ceiling_that_fell_below_its_predecessor_refuses` | REFUSE |
| `0.0085` / `0.008` / `0.009` — headroom invented above both inputs | `test_envelope_ceiling_invented_above_both_inputs_refuses` | REFUSE |
| `None` / `0.008` / `0.009` — genesis ceiling that is not its corpus Q99 | `test_genesis_ceiling_that_is_not_its_own_q99_refuses` | REFUSE |
| `None` admits; present `0`, `""`, `"not-a-decimal"`, `Decimal("0.009")` refuse | `test_absent_predecessor_ceiling_is_none_and_never_a_present_zero` | ADMIT + 4 REFUSE |
| predecessor row disagrees / is unregistered / is unnamed | `test_predecessor_ceiling_must_match_the_predecessor_row` | ADMIT + 3 REFUSE |
| screen strictly below the ceiling, with no predecessor | `test_generation_row_refuses_a_screen_at_or_above_its_ceiling` | ADMIT + REFUSE |

`test_every_registered_generation_row_carries_the_full_schema` now asserts
`predecessor_ceiling_s is None` and `maximum_budgetable_drift_s == prediction_99_two_draw_s` on both
registered rows.

## 3. Seam with S2 (refuter 71 F4/F5)

**F5 — one home for the vocabulary.** `calibration_bracketing.py` no longer declares
`BRACKET_SESSION_KIND` / `DERIVATION_SESSION_KIND`. It imports `SESSION_KIND_BRACKET` and
`SESSION_KIND_DERIVATION` from `joulewise.calibration_ledger`, which owns them. The names and values
were verified against S2's branch (`origin/feat/2026-09-10-epoch-s2-ledger-sessions`,
`calibration_ledger.py:72-73`, with `CalibrationBracketSession.session_kind: str = SESSION_KIND_BRACKET`
at `:493`).

**They are not importable at this seat's base** (`93799321` predates S2's landing), so the import is
wrapped in `try/except ImportError` with a fallback that restates the two values, commented
`TEMPORARY SEAM SHIM ... delete this fallback there`. **The integration tree must delete the fallback**
— two sources for one vocabulary is exactly the drift the import exists to prevent, and a fallback that
survives the merge silently reinstates it. Flagging this as the one thing in the diff that is
deliberately not final.

**F4 — the kind reader fails closed.** `_observation_session_kind` returns a third value,
`SESSION_KIND_UNRESOLVED`, when a row names a session id that `bracket_session_by_id` does not hold, and
`_is_derivation_kind_observation` bars it from the endpoint universe alongside true derivation rows.
`LedgerObservation` carries no kind of its own (S2's deliberate choice), so the lookup is the only path,
and a row whose session cannot be resolved MAY be a derivation row — admitting it on that doubt was the
fail-open reading. The historical case is untouched: a row belonging to no session, or to a resolvable
session with no kind field, is still `bracket`, which is every capture written before derivation kinds
existed. `test_unresolvable_session_is_barred_not_read_as_bracket` asserts both halves.

Scope note: at the two universe sites this is defence in depth, because an unresolvable session id is
already outside `finalized_session_ids` and skipped there. It bites on the predicate itself and on any
future caller — which is what F4 asked for.

## 4. Noted, no code written

- **`d125_ruling` becomes a required generation-row key when the envelope row lands** (S4; packet 46
  addendum A2). It is deliberately NOT in `_GENERATION_ROW_REQUIRED_KEYS` today, because adding it
  would refuse both currently registered rows.
- **The successor screen rule is unruled and is Ed's.** The pre-registration text says
  `max(quantized range, 0.010818)`; the D-125 consult says `S_g = max(S_{g-1}, Q95_g)`. They are
  different rules. **Neither is encoded.** `screen_rule` still admits exactly one value,
  `range_equals_screen`, and any other registered name refuses at the comparison site. Ruling 69 also
  notes that when the envelope screen rule lands it takes the same shape as the ceiling
  (`predecessor_screen_s`, `S_g = max(S_{g-1}, Q95_g)`) — also not written.

## Mutation sweep, whole, one term per cut

25 cuts, **25/25 KILLED**, no survivors, no anchor misses; source bytes restored and compared
(`restored: True`). Every cut deletes or negates exactly ONE boolean term, per ruling 69 §Q2's
isolation rule. The seven cuts touching this round:

| Atomic cut (one term) | Naming test | rc |
|---|---|---|
| `drift != (prediction if predecessor is None else max(...))` | `test_envelope_ceiling_that_fell_below_its_predecessor_refuses` | 1 |
| same term | `test_envelope_ceiling_invented_above_both_inputs_refuses` | 1 |
| same term | `test_genesis_ceiling_that_is_not_its_own_q99_refuses` | 1 |
| `if predecessor_lexeme is not None:` → `if True:` (the absence gate) | `test_absent_predecessor_ceiling_is_none_and_never_a_present_zero` | 1 |
| `registered is None or registered != predecessor` | `test_predecessor_ceiling_must_match_the_predecessor_row` | 1 |
| `not screen < drift` | `test_generation_row_refuses_a_screen_at_or_above_its_ceiling` | 1 |
| `return SESSION_KIND_UNRESOLVED` → `return SESSION_KIND_BRACKET` | `test_unresolvable_session_is_barred_not_read_as_bracket` | 1 |

**The sweep did its job twice this round, and both are worth recording.**

1. One cut came back **ANCHOR-MISS** rather than KILLED, because the F5 rename moved the anchor text
   out from under an existing entry. An anchor miss is a silently unexercised clause, so the harness
   prints it as its own verdict rather than counting it as a kill — without that, F1's clause would
   have gone unswept this round with no signal.
2. One cut **SURVIVED**: the standalone `if predecessor is None: return False`. The diagnosis is the
   one ruling 69 §Q2 clause (3) names — a term nothing can isolate is either dead or unruled — and here
   it was dead: the read-back comparison refuses every input that term could refuse. I removed the term
   rather than weaken the test, and re-cut the absence GATE instead, which is isolable (making the
   branch unconditional refuses both genesis rows). The ruled behaviour is unchanged.

## Test rcs (verbatim, rc captured in `RC`)

```
python3 -m unittest tests.test_calibration_bracketing tests.test_calibration_live_three_window \
    tests.test_paper_first_use_ledger tests.test_floor_mint_pinsets_schema tests.test_docs_freshness
FIXROUND2_RC=0 :: Ran 146 tests in 4.843s  OK (skipped=4)

python3 -m compileall -q joulewise tests   rc=0
python3 scripts/gen_state.py --check       rc=0
```

`tests.test_calibration_bracketing` is now 80 tests (28 in `GenerationKeyedIssuanceValidationTests`).
The byte-identical sweep over all six artifacts under `configs/calibration/` and the genesis fixture
passes unchanged — the field rename and the two `None` values moved no issued byte.

---

# Fix round 3 (delta re-audit 73, execution lens: S1, S2, S3 — all should_fix, no blockers)

Applied on top of `f40e748b`; diff uncommitted, same two files. The seam shim is untouched, as
instructed — the integration tree deletes it.

The delta upheld the behaviour (16 cuts, 14 killed, no blockers) and **confirmed the round-2 dead-term
claim by re-insertion** — putting `if predecessor is None: return False` back at HEAD changed nothing.
Its sting is in the tail: that deadness was load-bearing on `registered is None`, a term nothing pinned
(S2). The refuter's own summary of the situation is the right one, and S2 closes both at once.

## S1 — the `max` was pinned in one direction only

Every envelope test in round 2 used own Q99 `0.008` against a predecessor at or above `0.0085`, so the
predecessor always won the max and `max(predecessor, prediction)` → `predecessor` survived the whole
module. Ruling 69 probe 3's fourth row — "own Q99 dominates" — had no test.

Added `test_envelope_ceiling_equals_own_q99_when_own_q99_dominates`, both halves, artifact and row
moved together with the excess retuned and the screen at `0.006000`:

- predecessor `0.0085`, own Q99 `0.009000`, ceiling `0.009000` → **ADMIT** (own Q99 won the max)
- predecessor `0.0085`, own Q99 `0.009000`, ceiling `0.0085` → **REFUSE** (a budget ceiling below this
  corpus's own 99 % two-draw prediction, which the cut would have licensed whenever a predecessor is
  present)

No production change: the relation was already correct, only unpinned.

## S2 — the `registered is None` disjunct is now pinned

It is reached only when BOTH sides are `None`: an unparseable or non-string `predecessor_ceiling_s`
AND an unresolvable `predecessor_acceptance_id`. `None != None` is False, so without the disjunct the
row is admitted **as a genesis** — the lineage fence switched off by two independent defects at once.

Added `test_malformed_ceiling_with_an_unresolvable_predecessor_refuses`: `predecessor_ceiling_s = 0`
with `predecessor_acceptance_id = "no-such-generation"`, ceiling == own Q99 == `0.009000`. No
production change.

## S3 — the lineage fields are now jointly present or jointly absent

The one real hole of the three. `predecessor_acceptance_id` was consulted ONLY inside the
`predecessor_lexeme is not None` branch, so a row that NAMED a predecessor and NULLED its ceiling took
the genesis arm and was admitted — laundering the exact violation
`test_envelope_ceiling_that_fell_below_its_predecessor_refuses` catches when the row is honest. No live
exposure (both registered rows name no predecessor and set `None`), so this is a future-issuance hole.

Production change, in `_registered_generation_row_is_complete`:

```python
if predecessor_lexeme is None and (
    generation.get("predecessor_acceptance_id") is not None
):
    return False
```

The docstring now states the pairing in one sentence. The converse direction — a non-None ceiling with
no resolvable predecessor row — already refused and is kept.

`test_lineage_fields_are_jointly_present_or_jointly_absent` covers four inputs: the nulled-ceiling
launder REFUSES; the same lineage stated honestly (ceiling `0.0095` = max(0.0095, 0.009)) ADMITS; a
ceiling with no id named REFUSES; a genesis row naming nothing ADMITS.

**The guard also caught a defect in my own round-2 test fixture.** `_envelope_case` set
`predecessor_acceptance_id` unconditionally, including on genesis cases — so two round-2 tests were
constructing exactly the mismatched pair S3 forbids and passing anyway. The helper now pops the id when
there is no predecessor, which is what the two registered rows look like. Worth noting because it is
the same failure mode as S3 itself: an unpaired field nobody was reading.

## Atomic sweep — all round-2 clauses plus the three new terms

28 cuts, **28/28 KILLED**. No survivors, no anchor misses, no `NO-TESTS-RAN`. Every cut deletes or
negates exactly ONE boolean term. The harness now parses `Ran N` from the runner and treats `N < 1` as
its own verdict (a test that never ran is not a kill), and asserts restoration by SHA-256 rather than by
string compare:

```
restored_sha256: 51ae8ad43ae3c61aca6326029c9af7afa79040c9a5a3d8b1a86ee83a3a7c38cf
restored_matches: True
```

The three new cuts:

| Atomic cut (one term) | Naming test | rc | Ran |
|---|---|---|---|
| `max(predecessor, prediction)` → `predecessor` (S1) | `test_envelope_ceiling_equals_own_q99_when_own_q99_dominates` | 1 | 1 |
| `registered is None or` dropped from the read-back (S2) | `test_malformed_ceiling_with_an_unresolvable_predecessor_refuses` | 1 | 1 |
| joint-presence guard deleted (S3) | `test_lineage_fields_are_jointly_present_or_jointly_absent` | 1 | 1 |

The 25 round-2 cuts all still kill, each `Ran 1`, unchanged.

## Test rcs (verbatim, rc captured in `RC`)

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing tests.test_calibration_ledger
FIXROUND3_RC=0 :: Ran 155 tests in 3.381s  OK (skipped=2)

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_live_three_window \
    tests.test_paper_first_use_ledger tests.test_floor_mint_pinsets_schema tests.test_docs_freshness
focused_rest_rc=0 :: Ran 66 tests in 4.282s  OK (skipped=3)
```

`tests.test_calibration_bracketing` is now 83 tests (31 in `GenerationKeyedIssuanceValidationTests`).
The byte-identical sweep over all six artifacts under `configs/calibration/` and the genesis fixture
passes unchanged; the only production change this round is one refusal on a field pairing that no
registered row uses.

---

# Fix round 4 (seam) — the D-125 envelope screen rule and `d125_ruling`

Applied on top of `57d0044d` (round 3's delta, record 77, was CLEAN); diff uncommitted, same two files.
Authority: cold gate 46 addendum A-2 and the pre-registration
(`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` on
`origin/feat/2026-09-10-epoch-s6-docs-prereg`, the "full D-125 envelope governs both operatives"
clause). Seat S4 read at `f31884d7`.

## What S4 must import (exact names, from `joulewise.calibration_bracketing`)

```python
from joulewise.calibration_bracketing import (
    D125_SCREEN_FLOOR_S,                    # Decimal("0.010818")
    SCREEN_RULE_FLOORED_RANGE_ENVELOPE,     # "floored_range_envelope_screen"
    SCREEN_RULE_RANGE_EQUALS_SCREEN,        # "range_equals_screen" (already exported)
    BRACKET_SCREEN_QUANTUM_S,               # Decimal("0.000001")
    PREFLIGHT_LEVEL_SCREEN_QUANTUM_S,       # Decimal("0.000000000000001")
)
```

S4 currently restates `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` at its `:176` and defines
`BRACKET_SCREEN_QUANTUM_S` / `PREFLIGHT_LEVEL_SCREEN_QUANTUM_S` at `:164-165`; it already references
`D125_SCREEN_FLOOR_S` at `:591`. All five now have one home here. The floor digits `0.010818` appear
exactly once in this module.

## 1. The envelope rule is registered and checked

`_REGISTERED_SCREEN_RULES` now holds two names. At the `_valid_acceptance_bound` site the dispatch is
explicit, and an unregistered name still falls through to `return False` rather than defaulting to
either branch:

```python
quantized_range = (max(values) - min(values)).quantize(
    BRACKET_SCREEN_QUANTUM_S, rounding=ROUND_HALF_EVEN
)
if screen_rule == SCREEN_RULE_RANGE_EQUALS_SCREEN:
    screen_matches_rule = quantized_range == screen
elif screen_rule == SCREEN_RULE_FLOORED_RANGE_ENVELOPE:
    screen_matches_rule = max(quantized_range, D125_SCREEN_FLOOR_S) == screen
else:
    return False
```

The level-screen term and `screen + excess == maximum` stay universal and untouched, as does
`range_equals_screen` for the six issued rows.

**One thing S4 must change, and it is a real disagreement, not a naming preference.** S4's `:593-596`
selects the rule name from which side of the max won:

```python
floor_bound = screen != quantized_range
screen_rule = (SCREEN_RULE_FLOORED_RANGE_ENVELOPE if floor_bound
               else SCREEN_RULE_RANGE_EQUALS_SCREEN)
```

`screen_rule` names the DERIVATION RULE the generation was pre-registered under, not the branch the
data happened to take. A corpus derived under the envelope registers
`floored_range_envelope_screen` whether or not the floor bound it — the rule was fixed before the
captures, and the outcome was not. Selecting the name from the outcome makes the row's own account of
its derivation a function of the data, which is the same class of defect as choosing corpus membership
after seeing the values. The validator accepts both branches under the envelope name
(`max(range, floor) == screen` is satisfied when the range wins too), so S4 can register the envelope
name unconditionally with no other change. S4's `rule_outcomes.screen_rule_registered_in_validator`
flag and the seam note in its report are now stale: both names are registered.

## 2. `d125_ruling` — conditionally required

A non-empty string on every row whose `screen_rule` is `floored_range_envelope_screen`; absent or
`None` on `range_equals_screen` rows stays valid. Implemented as a conditional clause inside
`_registered_generation_row_is_complete`, deliberately NOT added to
`_GENERATION_ROW_REQUIRED_KEYS` — the six issued rows carry no such key and adding it unconditionally
would refuse all of them.

## Tests

`_floored_envelope_case` builds the route the pre-registration names: corpus range `0.006000`, BELOW
the floor, so the floor binds and the screen is `0.010818`; a real lineage (r6's registered ceiling
`0.010164834757777545`, named by r6's own id); own Q99 `0.012000` wins the ceiling max, keeping the
screen strictly below the ceiling with `excess = 0.001182` so `screen + excess == maximum` holds; the
level screen is unchanged and consistent. Artifact and row move together throughout.

| Case | Test | Verdict |
|---|---|---|
| envelope row, floor-bound screen `0.010818` | `test_floored_envelope_screen_rule_admits_a_floor_bound_generation` | ADMIT |
| same row with screen = quantized range `0.006000` (floor ignored) | `test_envelope_generation_that_ignored_the_floor_refuses` | REFUSE |
| same floored screen registered under `range_equals_screen` | `test_floor_bound_screen_refuses_under_the_range_equals_screen_rule` | REFUSE |
| envelope row with `d125_ruling` missing, `""`, `0`, or a list | `test_envelope_generation_requires_a_non_empty_d125_ruling` | 4 × REFUSE |
| every registered row carries no `d125_ruling` and still validates | `test_range_equals_screen_rows_need_no_d125_ruling` | ADMIT |

## Atomic sweep — whole, one term per cut

32 cuts, **32/32 KILLED**, no survivors, no anchor misses, no `NO-TESTS-RAN`; every cut `Ran 1`.
Restoration hash-verified: `restored_sha256: f30e62ed0e9df76be2ff1aee46dc14929c0d1a44107fa2bf21c3bdb375983946`,
`restored_matches: True`. `PYTHONDONTWRITEBYTECODE=1` throughout.

| Atomic cut (one term) | Naming test | rc | Ran |
|---|---|---|---|
| `D125_SCREEN_FLOOR_S` `0.010818` → `0.009000` | `test_floored_envelope_screen_rule_admits_a_floor_bound_generation` | 1 | 1 |
| envelope branch `max(...)` → `min(...)` | `test_envelope_generation_that_ignored_the_floor_refuses` | 1 | 1 |
| range branch `quantized_range == screen` → `max(quantized_range, D125_SCREEN_FLOOR_S) == screen` | `test_floor_bound_screen_refuses_under_the_range_equals_screen_rule` | 1 | 1 |
| conditional `d125_ruling` clause deleted | `test_envelope_generation_requires_a_non_empty_d125_ruling` | 1 | 1 |
| dispatch `else: return False` → falls back to the range comparison | `test_unimplemented_screen_rule_refuses_instead_of_falling_back` | 1 | 1 |

The 28 round-3 cuts all still kill. Two harness repairs were needed and are worth recording, because
both are the isolation rule biting on my own work:

1. The old "screen-rule dispatch" cut came back **ANCHOR-MISS** — restructuring the site into an
   if/elif/else moved its anchor text. Re-cut against the new `else: return False`, which is the term
   that actually carries "an unregistered name refuses rather than defaulting".
2. My first attempt at a rule-name cut (`== SCREEN_RULE_RANGE_EQUALS_SCREEN` →
   `in _REGISTERED_SCREEN_RULES`) **SURVIVED**: it sends the envelope name down the range branch,
   which the floor-bound test does not exercise. The cut that isolates "the two rules are not the same
   semantics" is the one above — making the RANGE branch floor its comparison — and it kills.

## Test rcs (verbatim, rc captured in `RC`)

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing \
    tests.test_calibration_ledger tests.test_docs_freshness
FIXROUND4_RC=0 :: Ran 191 tests in 4.192s  OK (skipped=2)

byte-identical artifact sweep, alone      :: Ran 1 test  OK
tests.test_calibration_live_three_window tests.test_paper_first_use_ledger \
    tests.test_floor_mint_pinsets_schema  :: rest_rc=0 :: Ran 35 tests  OK (skipped=3)
```

`tests.test_calibration_bracketing` is now 88 tests (36 in `GenerationKeyedIssuanceValidationTests`).
The byte-identical sweep over all six artifacts under `configs/calibration/` and the genesis fixture
passes unchanged: no issued row's `screen_rule`, screen, or level screen moved, and the new rule is
registered for no registered generation.
