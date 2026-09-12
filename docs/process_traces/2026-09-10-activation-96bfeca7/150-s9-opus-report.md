# S9 — epoch-equivalence check (directive issue 316) — COMPLETE

Worktree `/Users/edr/code/JouleWise-wt-s9-eq-check`, branch
`feat/2026-09-10-epoch-equivalence-check`, HEAD `bc1d7ef9` unchanged (no git
state changes; the lead commits).

## What landed

| path | lines | role |
| --- | --- | --- |
| `scripts/epoch_equivalence_check.py` | 676 (new) | the desk tool |
| `tests/test_epoch_equivalence_check.py` | 520 (new) | 19 defect-shaped tests |
| `tests/fixtures/custody_read_replay_allowlist.json` | +7 | census row for the one `read_replay` snapshot load |

Key anchors in `scripts/epoch_equivalence_check.py`:

- `_refuse_out_path:149` — refuses any `--out` whose resolved parts contain
  `configs/calibration` in sequence (holds for any checkout, not just this
  one), and refuses an existing destination without `--force`. Runs FIRST,
  before anything is read.
- `reference_envelope:166` — loads r6 through the production loader
  `joulewise.calibration_bracketing.load_calibration_acceptance_bound`, reads
  the operatives through the public accessor
  `acceptance_generation_operatives(acceptance_id, acceptance=acceptance)`
  (which itself refuses a bracket-screen crosswire), then compares
  `preflight_level_screen_s`, `bracket_screen_s` and
  `maximum_budgetable_drift_s` field-by-field between the artifact's
  `ratified_operatives` and the registry, and `derivation_corpus.n` against the
  registry's `corpus_n`. Any disagreement = refusal, rc 3, nothing written.
- `envelope_lines:258` — the constants table; every number carries its source,
  and a NOTE fires when operative ≠ raw statistic.
- `_slot_outcomes:298` — one line per DECLARED slot; retention reuses the
  issuer's `_read_member_evidence` and `anchor_v3_replay_outcome` (imported,
  not re-implemented), so bytes are authenticated against the row before any
  value is read, and the row's `exact_bound_lexeme_s` must equal the primary
  `b_fiducial_s`.
- `resolve_session:379` — absent / not-derivation / not-terminal refusals. It
  runs BEFORE `snapshot.refusal_reasons`, because an open derivation session is
  itself one of those reasons and would otherwise mask the actionable message.
- `evaluate_session:405` — `m < 6` → INCONCLUSIVE with no comparison computed
  at all; otherwise Decimal max/min/spread under
  `localcontext(prec=DECIMAL_WORK_PRECISION)` and the two `<=` comparisons.
- `record_lines:488`, `run:553`, `build_parser:588` (help with the six glosses
  and the "never issues / never continues / never writes an addendum" epilog),
  `main_args:661` / `main:671`.

Exit codes: 0 PASS, 4 FAIL, 5 INCONCLUSIVE, 3 refusal (distinct from the
issuer's use of 3 for the same "would not judge" meaning).

## The constants, as the tool prints them for the REAL r6 artifact

`python3 scripts/epoch_equivalence_check.py --print-envelope-only`, rc 0
(a flag that needs no session, reads no ledger and writes nothing):

```
Reference envelope (the acceptance in force; issue 316)
  acceptance_id: d079_calibration_acceptance_v2_n17_r6
  artifact: /Users/edr/code/JouleWise-wt-s9-eq-check/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json
    loaded by joulewise.calibration_bracketing.load_calibration_acceptance_bound
  corpus n = 17 (artifact derivation_corpus.n; registry corpus_n; they agree)
  raw corpus maximum_s = 0.03289849371536248  [artifact decimal_derivation.source_statistics]
  raw corpus range_s   = 0.00972358928879385  [artifact decimal_derivation.source_statistics]
  OPERATIVE level screen   preflight_level_screen_s   = 0.032898493715362  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  OPERATIVE bracket screen bracket_screen_s           = 0.009724  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  budget ceiling           maximum_budgetable_drift_s = 0.010164834757777545  [validator registry _D102_GENERATION_DERIVATIONS operatives]
    artifact decimal_derivation.ratified_operatives agrees with the registry on all three, or this tool refuses
    NOTE: the operative comparators differ from the raw statistics (quantization / never-zero floor); issue 316 rules the OPERATIVE value is the one compared against.
```

Both operatives differ from the raw statistics (level screen truncated to 15
decimal places from a 17-place maximum; bracket screen quantized upward from
the raw range), so issue 316's "the operative value is the one used" clause is
live for BOTH screens on this artifact, not only the bracket screen.

## Mutation cut table (each cut: single test, `Ran 1 test`, sha256-restored `ee55b898…`, `PYTHONDONTWRITEBYTECODE=1`)

| cut | test that killed it | rc |
| --- | --- | --- |
| C1 level comparison → `True` | `test_one_value_above_the_level_screen_fails` | 1 |
| C2 bracket comparison → `True` | `test_range_above_the_bracket_screen_fails_with_every_value_inside` | 1 |
| C3 `max(values)` → `min(values)` | `test_one_value_above_the_level_screen_fails` | 1 |
| C4 `min(values)` → `max(values)` | `test_range_above_the_bracket_screen_fails_with_every_value_inside` | 1 |
| C5 `<=` → `<` on the level screen | `test_a_value_exactly_on_the_level_screen_passes_and_one_ulp_above_fails` | 1 |
| C6 spread `max - min` → `max + min` | `test_twelve_retained_values_inside_the_envelope_pass` | 1 |
| C7 `m < MINIMUM_RETAINED_M` gate dropped | `test_five_retained_values_are_inconclusive_even_though_all_pass` | 1 |
| C8 `disposition != "valid"` gate dropped | `test_m_counts_only_valid_and_resolved_rows_and_lists_the_rest` | 1 |
| C9 `not resolved` (anchor-v3 replay) gate dropped | same | 1 |
| C10 terminal-state gate dropped | `test_an_open_session_refuses_and_writes_nothing` | 1 |
| C11 derivation-kind gate dropped | `test_a_bracket_kind_session_refuses` | 1 |
| C12 `configs/calibration` out-path guard dropped | `test_an_out_path_under_configs_calibration_refuses` | 1 |
| C13 overwrite guard dropped | `test_an_existing_out_is_not_overwritten_without_force` | 1 |
| C14 artifact/registry operative cross-check dropped | `test_an_operative_the_loader_does_not_police_still_refuses` | 1 |
| C15 corpus-n cross-check dropped | `test_a_disagreeing_corpus_size_refuses` | 1 |
| C16 level screen sourced from raw `maximum_s` | `test_the_json_record_equals_the_printed_values` | 1 |
| C17 bracket screen sourced from raw `range_s` | same | 1 |
| C18 retained values through a float round trip | `test_full_precision_lexemes_survive_the_check_unrounded` | 1 |
| C18b stored maximum re-rendered at reduced precision | same | 1 |
| C19 unused/no-row distinction collapsed | `test_an_aborted_window_exhausted_night_is_evaluated` | 1 |

**20 cuts, 20 killed, 0 survivors.** Two survivors on the first pass, both
fixed rather than argued away:

- C14 first survived because my cut (`False and A or B or C`) was defeated by
  `and`/`or` precedence — an INEFFECTIVE cut, not a test gap. Re-cut as the
  whole `if (...)` → `if False:`; killed.
- C18 first survived for real: a float round trip of a 15-significant-digit
  value is the identity, so r6's own operatives cannot witness the
  "never float" clause. Added
  `test_full_precision_lexemes_survive_the_check_unrounded` (462), which builds
  a grid at the ~18-digit width a real `b_fiducial_s` actually has, asserts the
  fixture really is wider than binary64, and pins max/min/range to exact
  Decimal arithmetic on the stored strings. Both float cuts now die.

## Runs

```
python3 -m unittest tests.test_epoch_equivalence_check tests.test_custody_mode_inventory \
  tests.test_issue_calibration_acceptance_generation tests.test_docs_freshness \
  tests.test_mint_policy_resolver_guard
Ran 172 tests in 99.845s
OK
SUITE rc=0

python3 -m compileall -q scripts    → rc=0
scripts/epoch_equivalence_check.py --print-envelope-only → rc=0
```

`tests.test_epoch_equivalence_check` alone: `Ran 19 tests in 6.783s / OK`.
The mint-policy guard passes: neither new file contains the forbidden literals
(`grep -c` = 0 in both); the script reads them from the registry and the tests
read them via `acceptance_generation_operatives(ACTIVE_ACCEPTANCE_ID)`,
including the boundary ulp, which is derived from the stored lexeme's exponent.

## Footprint

`git status --short` shows exactly:

```
 M tests/fixtures/custody_read_replay_allowlist.json
?? scripts/epoch_equivalence_check.py
?? tests/test_epoch_equivalence_check.py
```

Nothing else touched; no other worktree, no captures, no sudo, no git state
change. The allowlist row demanded by `tests.test_custody_mode_inventory` was
`("scripts/epoch_equivalence_check.py", "run", 1)`; added with `line: 568` and
a one-line replay reason, and the file re-sorted by (file, function, ordinal),
which produced a pure 7-line insertion.

## Decisions and wording questions resolved

1. **"corpus maximum (level screen)" vs the operative.** Issue 316 states the
   raw corpus maximum `0.03289849371536248` as "the level screen", but the
   registered operative `preflight_level_screen_s` is the 15-place
   `0.032898493715362` — the operative is SMALLER, i.e. stricter. The issue's
   own tie-breaker clause names only the bracket screen ("if the validator's
   operative screen differs from the raw range"). I applied the clause's
   PRINCIPLE to both screens, as the brief directs: compare against the
   operative in each case. The tool prints both numbers with their sources and
   emits an explicit NOTE that they differ, so the magistrate's record quotes
   the difference rather than hiding it. **This is the stricter reading** — a
   night's maximum falling between `0.032898493715362` and
   `0.03289849371536248` would FAIL here and PASS under the raw reading. Flagged
   for the magistrate, since it is the one place where the two readings diverge.
2. **Unregistered exclusion mechanisms are listed, not refused.** The issuer
   refuses a `valid` row whose replay refused with a mechanism outside
   `REGISTERED_CORPUS_EXCLUSION_REASONS`, because such a row would silently
   shrink a corpus that sets a screen. This tool only reads an envelope, so
   refusing the whole night over one unrecognised refusal detail would discard
   a usable equivalence answer. It prints `valid+unresolved <detail>` verbatim
   and excludes the row. A custody-hash or lexeme mismatch still refuses the
   whole run (rc 3) — that is an integrity failure, not a classification.
3. **`slot_refused` vs `unused (window_exhausted)`.** Neither is a ledger
   disposition; both are "no finalized row". The tool distinguishes them from
   the session record: unfilled declared slots of a session aborted with reason
   `window_exhausted` print `unused (window_exhausted)`, all other unfilled
   slots print `no row`. Cut C19 proves the distinction is load-bearing.
4. **Refusal order.** `resolve_session` runs before `snapshot.refusal_reasons`,
   mirroring the issuer's `refuse_open_registration`; otherwise every
   mid-campaign run reports `calibration_ledger_bracket_session_open` instead
   of "session … is 'open', not terminal".
5. **Registry access.** Operatives go through the public accessor
   `acceptance_generation_operatives`. `_D102_GENERATION_DERIVATIONS` is
   imported only for `corpus_n`, for which no public accessor exists.
6. **`--print-envelope-only`** was added exactly as the brief asked, and is
   also how the artifact/registry disagreement is exercised end-to-end (it
   needs no ledger). Note that the production loader authenticates the artifact
   AGAINST the registry, so a rewritten registry row is already refused one
   layer out; this tool's own field comparison is the inner guard, tested
   directly at `test_an_operative_the_loader_does_not_police_still_refuses`
   (321) with the loader stubbed — the only mock in the file, and it mocks a
   byte loader, nothing about the machine.
7. **Test `--out` lives outside the fixture checkout**, since an untracked
   file inside a tree whose head pin is being authenticated is a different
   experiment.
