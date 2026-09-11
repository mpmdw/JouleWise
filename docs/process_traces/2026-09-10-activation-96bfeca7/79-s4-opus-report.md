# 79 — Seat S4 (issuer `prepare-candidate`) report

Worktree `/Users/edr/code/JouleWise-wt-s4-issuer-prepare`, branch
`feat/2026-09-10-epoch-s4-issuer-prepare-candidate`, base HEAD `0fe1fc5e`.
No git state changed (no commit, checkout, stash, reset, push). No capture, no
powermetrics, no `[QUIET-MAC]` window. Nothing outside WRITE SCOPE was written;
`configs/calibration/` is untouched and the real ledger was never read.

## 1. What landed

`scripts/issue_calibration_acceptance_generation.py` — S5's `check` is unchanged;
the `prepare-candidate` stub is replaced.

| Piece | file:line | What it does |
|---|---|---|
| Pre-registration constants | `:128-176` | `D125_SCREEN_FLOOR_S 0.010818`, `R6_PREFLIGHT_LEVEL_SCREEN_S 0.032898493715362`, `R6_MAXIMUM_PLUS_RANGE_S 0.04262208300415633` (addendum A-4 spelling), `SUCCESSOR_MINIMUM_CORPUS_SIZE 19` (addendum A-2), the two quanta, `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` |
| Half-integer Gamma / Beta | `:190-224` | `Gamma(k/2)` split as (rational, power of `sqrt(pi)`) so the `sqrt(pi)` cancels for even df and exactly one `pi` survives for odd df |
| Incomplete beta (Lentz CF) | `:227-282` | `I_x(a,b)` at 80 digits, both convergence branches |
| `student_t_survival` / `student_t_quantile` | `:285-311` | `P(T>t) = I_{df/(df+t^2)}(df/2, 1/2)/2`, inverted by 300-step bisection. Works for **both parities** — r6's A&S 26.7.4 path was even-df only |
| `two_draw_prediction_lexeme` | `:314` | r6's rule verbatim: `t * sd_presentation * sqrt(2)` in binary64, recorded as its shortest `repr` |
| `_read_member_evidence` | `:328` | custody bytes authenticated against the ledger row's `artifact_sha256` before anything is read from them |
| `anchor_v3_replay_outcome` | `:369` | the replay outcome read from the hashed evidence: method must be `CLOCK_METHOD_V3`, `clock_anchor_resolved is True`, and an unresolved record yields its `detail` |
| `_authenticated_predecessor` | `:391` | r6 through the production exact-byte loader, `artifact_role == "issued"` |
| `_registration_observations` | `:405` | every observation of the named sessions; a missing session or a non-`derivation` kind refuses |
| `_select_members` | `:430` | valid + replay-resolved → member; valid + `affine_clock_fit_empty` → `derivation_notes.excluded_members` (`member_id`, `manifest_sha256`, `instrument_evidence_sha256`, `reason`); any other refusal detail refuses issuance |
| `_corpus_statistics` | `:482` | Decimal min/max/range/mean/sample-SD at explicit precision 80, presentation quantum `1e-18`, exactly r6's shape |
| `prepare_candidate` / `_prepare_candidate` | `:513` / `:532` | the whole ruled sequence; refusals print `REFUSED: <reason>` and return rc 3, nothing is written |
| `derivation_sha256` | `:828` | sha256 over the member lexemes, `source_statistics`, `rounding`, `two_draw_prediction_derivation`, `ratified_operatives`, `screen_rule`, `predecessor_ceiling_s`, `d125_ruling` — prose and paths deliberately out |
| CLI | `:863-899` | `--ledger --head-pin --repo-root --preregistration --predecessor-acceptance --registration-session-id(×N) --d125-ruling --ed-ruling --minimum-corpus-size --epoch-catalog-id --acceptance-id --out` |

Ruled behaviours, in order (`_prepare_candidate`):

1. `--d125-ruling` absent → refuse (`:535`); the reference is recorded on the row under `d125_ruling`.
2. `--minimum-corpus-size != 19` without `--ed-ruling` → refuse (`:539`); a value above 19 refuses outright.
3. head pin + complete history authenticated by `load_calibration_ledger_snapshot(require_committed_pin=True, mode="read_replay")`; any refusal reason refuses.
4. members selected by the registration; retained `n < minimum` → refuse (`:567`).
5. screen challenge: ≥ 2 retained members above `0.032898493715362` → refuse, "Ed rules in writing" (`:574`). One is recorded as a diagnostic and admits.
6. `S = max(range quantized 1e-6 ROUND_HALF_EVEN, 0.010818)` (`:592`); `C = max(predecessor ceiling, Q99)` (`:600`); strict `S < C` else `successor_screen_exceeds_budget_ceiling` (`:603`).
7. level screen = maximum quantized `1e-15`; excess = `C - S`, no clamp.
8. emits `--out` only: `candidate_not_issued: true`, `artifact_role: "candidate"`, `issuance.status: "candidate_not_issued"`, `claim_eligible: false`, two-entry `epoch_catalog` (predecessor's id + `--epoch-catalog-id`), `prior_observation_set.observations` = the complete history through the authenticated head with `session_id` per row, `ledger_cutoff` = that head, `prospective_rederivation.triggers` copied from the authenticated predecessor with the estimator-code digests recomputed, `derivation_notes` (predecessor, exclusions, `rule_outcomes`, per-member `prior_screen_comparison`), `registered_generation_row`, `derivation_sha256`.

`tests/fixtures/epoch_bootstrap/build.py` — builds a disposable **Git-committed**
ledger through the real writer (open a derivation-kind session at head-equals-pin,
claim+finalize each declared slot, write and commit the terminal pin), with
per-slot control of the value lexeme, the disposition, the recorded replay
outcome, the anchor method, and a deliberate primary-vs-row lexeme skew.

## 2. Per-clause test + mutation table

One term per cut, the single named test, `Ran 1 test` parsed from the runner,
source bytes restored and sha256-asserted after every cut
(`a5c980ecca3d90447631ab5894252c26774adb4e1a83c819e447e8633fbe7a1f`),
`PYTHONDONTWRITEBYTECODE=1` on every subprocess. Harness: `/tmp/s4_mutate.py`.

| Cut | Term deleted (production call site) | Test | Result |
|---|---|---|---|
| C1 | `if n < minimum:` `:567` | `test_seventeen_member_corpus_refuses_without_the_ed_ruling` | Ran 1 — KILLED |
| C2 | `and not args.ed_ruling` `:539` | `test_lowering_the_floor_without_a_ruling_refuses_before_reading_the_ledger` | Ran 1 — KILLED |
| C3 | `if not args.d125_ruling:` `:535` | `test_missing_d125_ruling_refuses` | Ran 1 — KILLED |
| C4 | `if not screen < ceiling:` `:603` | `test_screen_at_or_above_the_ceiling_refuses` | Ran 1 — KILLED |
| C5 | `if len(challenged) >= SCREEN_CHALLENGE_MEMBER_LIMIT:` `:574` | `test_two_members_over_the_prior_level_screen_refuse` | Ran 1 — KILLED |
| C6 | `if detail not in REGISTERED_CORPUS_EXCLUSION_REASONS:` `_select_members:455` | `test_unregistered_exclusion_mechanism_refuses` | Ran 1 — KILLED |
| C7 | `if session.session_kind != SESSION_KIND_DERIVATION:` `_registration_observations:417` | `test_bracket_kind_session_is_not_a_derivation_registration` | Ran 1 — KILLED |
| C8 | `max(quantized_range, D125_SCREEN_FLOOR_S)` `:592` | `test_floor_bound_screen_names_an_unregistered_rule` | Ran 1 — KILLED |
| C9 | `"predecessor_ceiling_s": str(predecessor_ceiling)` `:689` | `test_emitted_row_satisfies_the_registered_row_validator` | Ran 1 — KILLED |
| C10 | `observation.exact_bound_lexeme_s != lexeme` `_select_members:463` | `test_primary_value_disagreeing_with_the_ledger_row_refuses` | Ran 1 — KILLED |
| C11 | `anchor.get("method") != CLOCK_METHOD_V3` `anchor_v3_replay_outcome:380` | `test_a_non_v3_anchor_is_not_an_anchor_v3_replay` | Ran 1 — KILLED |

**First round: C7, C10 and C11 SURVIVED, all three masked** — the cure is
recorded because the masking pattern is the one packet 69 ruled on.
C7: the two-slot bracket fixture refused at the corpus-size floor instead of at
the kind check. C10: the skewed lexeme `0.0999` moved the range so far that the
ceiling clause refused first. C11: the test's counterfactual was an
already-unresolved anchor, which the `reason` term refuses without ever reaching
the method term. Cure: every refusal test now asserts the printed REASON through
`assert_refused` (a refusal is its reason, not a non-zero code), C10's skew was
reduced to a last-place perturbation that changes nothing downstream, and C11 got
a new counterfactual — a `valid` row whose anchor says RESOLVED under the
superseded v2 method. All eleven then kill.

Non-mutation coverage: `test_quantiles_reproduce_known_values_for_even_and_odd_df`
(df 16 = r6's two recorded pins to 20 places; df 18 and df 19 against published
values), `test_r6_predictions_are_reproduced_from_its_own_sd` (the whole
prediction rule reproduces r6's `0.007377644019421586` and
`0.010164834757777545` from r6's own SD), `test_emitted_candidate_is_refused_by_the_production_loader`,
`test_emitted_row_refuses_when_its_predecessor_ceiling_is_rebased`,
`test_derivation_digest_moves_with_an_operative_lexeme`,
`test_one_member_over_the_prior_level_screen_is_recorded_and_admits`.

## 3. Exact runner tails

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation \
    tests.test_calibration_bracketing tests.test_docs_freshness
----------------------------------------------------------------------
Ran 168 tests in 43.830s

OK (skipped=1)
SUITE_RC=0

$ python3 -m compileall -q scripts joulewise
COMPILEALL_RC=0
```

(`tests.test_issue_calibration_acceptance_generation` alone: `Ran 54 tests` OK —
S5's 31 desk-watch/chain tests plus S4's 23.) No full suite was run. No commit.

## 4. Footprint

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/test_issue_calibration_acceptance_generation.py
?? tests/fixtures/epoch_bootstrap/

$ git diff --stat
 scripts/issue_calibration_acceptance_generation.py | 763 ++++++++++++++++++++-
 ...test_issue_calibration_acceptance_generation.py | 421 +++++++++++-
 2 files changed, 1173 insertions(+), 11 deletions(-)
```

New untracked files: `tests/fixtures/epoch_bootstrap/__init__.py`,
`tests/fixtures/epoch_bootstrap/build.py`. All in scope.

**One deletion the lead must see.** The 11 deleted test lines are S5's
`test_production_defaults_and_stub`, which asserted `prepare-candidate` returns
rc 64 with the text "not implemented". It cannot hold now. It is replaced in
place by `test_production_defaults_and_required_destination`, which keeps every
one of S5's `check`-default assertions and adds the fence that matters: a bare
`prepare-candidate` exits 2 naming `--out` and `--preregistration` as required,
so the tool can never default to writing into `configs/calibration`. Nothing else
of S5's was touched (I overwrote the file mid-session and restored S5's content
from `HEAD` before finishing; the final diff is additive apart from those 11
lines).

## 5. Ambiguities decided, and why

1. **"Anchor-v3 replay from primary bytes resolves" is read, not recomputed.**
   Ruling 46 R-d records that a fresh v3 capture stores its own value
   (`stored_lexeme_is_member_value: True`), so the derivation-only writer's
   hashed `instrument_evidence.json` already carries both the anchor-v3 record
   and the member value. `anchor_v3_replay_outcome` therefore requires
   `clock_anchor.method == CLOCK_METHOD_V3`, `clock_anchor_resolved is True`, and
   no `clock_anchor_unresolved` reason; the value is the bundle's `b_fiducial_s`
   lexeme, cross-checked against the row's `exact_bound_lexeme_s`, and the bundle
   bytes are first authenticated against the row's `artifact_sha256`. Re-running
   the estimator over the raw trace inside the issuer would be a second
   estimator implementation; if the lead wants the replay recomputed rather than
   read, that is a distinct (larger) seat.
2. **Refusal transport.** Refusals print `REFUSED: <reason>` and return rc 3
   (S5's `check` already uses 3). Nothing is written on any refusal — every
   refusal test asserts the output file does not exist.
3. **`--d125-ruling` is not `argparse`-required.** Making it required would emit
   an argparse usage error, not the ruled refusal. It is optional at the parser
   and refused in the body, so the refusal is observable and testable.
4. **`--out` and `--preregistration` ARE argparse-required, with no defaults.**
   Writing into `configs/calibration` is the D-138 transaction's act.
5. **Prior set = the complete authenticated history**, every observation with a
   content id through the authenticated head, each tagged with the target epoch
   id when its epoch equals the artifact's and the predecessor's catalog id
   otherwise; `prior_prefix_mode` is `import_plus_live`; `cutoff_sequence` is the
   physical head (the `2N` relation is not imposed on a live prefix).
6. **The successor epoch must differ from the predecessor's**, else the run is a
   re-derivation, not an epoch bootstrap; refused.
7. **`epoch_catalog_ids` / `registration_session_ids` travel as JSON lists.**
   S3's registry wants tuples; the tests convert at the boundary and say so.
8. **`derivation_sha256` covers lexemes and rounding rules only** — not prose,
   paths, or the candidate label — so two preparations of the same corpus under
   the same rules digest equal and any operative edit moves it.

## 6. Seam items

**For S3 (`joulewise/calibration_bracketing.py`) — the screen-rule conflict.**
This is the one item that blocks issuance and is NOT mine to decide.

- The pre-registration's screen rule is `S = max(range quantized 1e-6
  ROUND_HALF_EVEN, 0.010818)`. `_REGISTERED_SCREEN_RULES` admits exactly one
  name, `range_equals_screen`, and `_valid_acceptance_bound` (`:1017-1021`)
  enforces `quantized range == screen` under it.
- When the quantized range wins the max, the realized derivation IS
  `range_equals_screen` byte for byte and the row registers that name — the
  ordinary case, and what the happy-path fixture exercises.
- When the **floor** wins, the realized rule is a different rule. The issuer
  names it honestly, `floored_range_envelope_screen` (`:176`), records
  `rule_outcomes.screen_rule_registered_in_validator: false`, and prints a
  `SEAM:` line. That row is currently REFUSED by
  `_registered_generation_row_is_complete` — proven by
  `test_floor_bound_screen_names_an_unregistered_rule`. **S3 must register the
  name and implement its check** (`screen == max(quantized range, 0.010818)`),
  or this branch cannot issue. It is reachable and it is not exotic: a corpus
  tighter than 0.010818 with enough spread to keep Q99 above the floor lands
  there (that is exactly the `floored` fixture).
- **`d125_ruling` (packet 69 addendum A-2) is emitted on the row but is not yet
  in `_GENERATION_ROW_REQUIRED_KEYS`.** The completeness check uses `issubset`,
  so the extra key passes today; A-2 says the key joins the required set when
  the envelope row lands. That edit is S3's.
- **The predecessor arm of the envelope is inert for THIS generation.** With r6
  as predecessor, `C = max(0.010164834757777545, Q99)` can only resolve to Q99:
  `S >= 0.010818 > 0.010164834757777545`, so any corpus in which the predecessor
  ceiling won would fail strict `S < C` and refuse. The term is kept because the
  row/validator relation requires it and because the NEXT generation's
  predecessor will have a ceiling above the floor — but no test can isolate the
  `max`'s predecessor arm through this predecessor, and C9 cuts the row field
  instead. Worth a refuter's eye.

**For S5 (`check`).** No interface of S5's changed. Only S5's stub test was
rewritten (§4). If S5's chain or watchdog text anywhere still says
`prepare-candidate` is "reserved" or "not implemented", it is now stale.

**Ed's open ruling, recorded and not encoded.** The consult's alternative
successor screen rule `S = max(S_{g-1}, Q95_g)` is NOT implemented anywhere in
this seat. Ruling 46 addendum A-3 withdrew the ruling's own `S_g = max(S_{g-1},
Q95_g)` note as guidance and states that a ruling on which rule binds is
required BEFORE any successor issuance; the pre-registration's
`max(range quantized, 0.010818)` is what the issuer implements, per the brief.
If Ed rules for the consult's alternative, `:592` and the `screen_rule` naming
are the two sites that change.

**Known gap (should_fix, no isolating test).** `_read_member_evidence`'s
`artifact_sha256` authentication (`:344-352`) has no counterfactual test: the
fixture would have to mutate a bundle after finalization. The clause is small and
fail-closed, but by the isolation rule an untested atomic term is `should_fix`,
not a nit, and I am naming it rather than leaving it for a refuter to find.

---

# Fix round 1 (seat S4, on top of `a18cb812` = S4 `f31884d7` + S3's seam round)

Every item of refuter report 81 addressed. No git state changed; write scope
unchanged (`scripts/issue_calibration_acceptance_generation.py`,
`tests/test_issue_calibration_acceptance_generation.py`,
`tests/fixtures/epoch_bootstrap/**`). The statistics and the quantile the refuter
verified byte-exact are untouched except for one strictly-additive change (the
quantile now pins its own Decimal context); its outputs are unchanged, and the
new independent route re-derives r6's df-16 pins as a regression.

## B1 — triggers derived from the emitted row, never copied. FIXED.

`prospective_rederivation.triggers` is now built by `rederivation_triggers(...)`
(`:517`) around the emitted row's own `corpus_doubling_trigger`, which is the
same five-name rule `_valid_acceptance_bound` (`:779-787`) demands; the
protocol digest is recomputed by `protocol_sha256(PROTOCOL_ID)` rather than
copied too. `rederivation_triggers` is the one home for the rule.

Chasing B1 to the end found **four more shape defects that would each have
blocked authentication on their own**, none of them reported, all now fixed and
each killed by a cut:

| # | defect | fix |
|---|---|---|
| B1a | `derivation_sha256` was a curated subset digest; the production definition is `_canonical_sha256(artifact minus derivation_sha256)` (`calibration_bracketing.py:660,764`), so no candidate could ever match | `derivation_sha256` now IS the production recipe; the curated seal moved to a second key, `derivation_input_sha256` (which is what SF3 asked for) |
| B1b | no `backfill_candidate` block; the issued role requires one, and the validator recomputes `candidate_inventory` over the WHOLE prior set with one entry per admissible disposition **including the zeros** (`:869-884`) | emitted, truthfully labelled `candidate_not_issued`, inventory computed over `prior_observations` across `PRIOR_SET_DISPOSITIONS` |
| B1c | `decision_ids` was `["D-079","D-102","D-125","D-126"]`; the validator demands exactly `["D-102","D-109"]` (`:762`) | emitted as the demanded pair; the D-079/D-125/D-126 provenance travels in `derivation_notes` and in the row's machine-checked `d125_ruling` |
| B1d | `"quantum_s": str(PREFLIGHT_LEVEL_SCREEN_QUANTUM_S)` renders `"1E-15"`; the validator compares against the literal `"0.000000000000001"` | `_plain()` (`format(d, "f")`) on all three quanta/floor lexemes |

Members are also emitted in `member_id` order now (`:958`), which the validator
requires (`:832`).

**The test that makes this class of defect visible**:
`test_only_the_candidate_label_stops_the_candidate_authenticating`. It flips the
three label fields (and registers the row and the id, as the D-138 transaction
will) and asserts the production `_valid_acceptance_bound` **ADMITS** the result.
So the refusal reason really is `candidate_not_issued` and nothing else — any
future shape defect, copied trigger or wrong digest recipe surfaces here as a
still-refusing artifact, which is exactly what the old "assert it is refused"
test could not do.

## B2 — one screen-rule name, unconditionally. FIXED.

`D125_SCREEN_FLOOR_S`, `BRACKET_SCREEN_QUANTUM_S`,
`PREFLIGHT_LEVEL_SCREEN_QUANTUM_S`, `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` and
`protocol_sha256`/`PROTOCOL_ID` are now imported from
`joulewise.calibration_bracketing`; my restatements are deleted. The rule is named
`floored_range_envelope_screen` unconditionally (`:871`) — the name is the
pre-registered RULE, not which arm of the `max` won; naming it by the realized
branch would make the registered rule a function of the data. The stale
`screen_rule_registered_in_validator` flag and the `SEAM:` warning are removed.
`test_range_bound_corpus_row_is_admitted_alongside_r6` and
`test_floor_bound_corpus_row_is_admitted_alongside_r6` both assert the emitted
row — with `d125_ruling`, `predecessor_ceiling_s` = r6's registered ceiling and
`predecessor_acceptance_id` = r6's id — is ADMITTED by
`_registered_generation_row_is_complete` alongside r6.

**Where the list→tuple conversion lives (S3 delta 83 F2).** On the EMITTING side,
in `generation_row_for_registry` (`:559`), with `GENERATION_ROW_TUPLE_FIELDS`
naming the two fields. The JSON artifact serialises them as arrays either way;
anything handing the row to S3's `isinstance(..., tuple)` fences — the future
`_D102_GENERATION_DERIVATIONS` entry the D-138 transaction writes, and both B2
tests — calls that function rather than re-deriving the conversion. The tests
assert the converted fields ARE tuples, so a regression in the helper is caught.
**Transaction seat: call `generation_row_for_registry(payload["registered_generation_row"])`;
do not hand the JSON row to the registry directly.**

## B3 — the realized df is proven, two independent ways, before issuance. FIXED.

`build_quantile_proof(df)` (`:450`) runs before any prediction and refuses
`quantile_proof_failed` on either bound:

- **forward check** — `student_t_survival` evaluated AT the returned quantile
  reproduces `1 − p`; residual bound `1e-30` (realized: ~1e-80).
- **independent route** — `student_t_quantile_closed_form` (`:423`) inverts the
  exact Abramowitz & Stegun **26.7.3 (odd df) / 26.7.4 (even df)** finite forms,
  with `arctan` by Euler's series (reflected into `|x| ≤ 1`, or it crawls — that
  cost me one debugging round) and **π by Machin's formula, computed**, not the
  transcribed `_PI` the continued-fraction route uses. Bound ≥ 30 significant
  digits; realized **56–57**. The two routes share no code, and because one
  computes π and the other transcribes it, a mistyped digit in `_PI` now shows up
  as a proof failure rather than as a wrong number.

Recorded as `decimal_derivation.quantile_proof` (df, both probabilities, both
quantiles, forward residuals and their bound, agreement digits and their bound,
the closed-form method, the precision) and sealed. `test_realized_df_carries_a_two_route_quantile_proof`
uses a 22-slot fixture (**df 21 — pinned by no test**) and asserts the record;
`test_the_closed_form_route_reproduces_r6_and_both_parities` shows the
independent route is independently right, not merely agreeing.

## SF1 / SF2 / SF3 — all implemented and killed

- **SF1**: `tamper_member_bundle()` rewrites one member's `manifest.json` after
  finalization and re-commits; `test_a_manifest_edited_after_finalization_refuses`
  asserts the printed reason. Cut F5 (the refuter's surviving X1) now dies.
- **SF2** (addendum A-7): a `valid` row carrying the target epoch that belongs to
  no registered session **refuses issuance** (`:831`), naming the offending
  attempt ids. Fixture support: `build_derivation_ledger(second_session=...)`
  writes a second, unregistered derivation session into the same ledger.
  Note S3 independently enforces the same rule inside the validator
  (`calibration_bracketing.py:917-927`); the issuer-side refusal fires earlier
  and says which rows.
- **SF3**: `derivation_input_sha256` now seals `identity_epoch`, the ledger
  cutoff, `predecessor_acceptance_id` and `quantile_proof` alongside the member
  lexemes, statistics, rounding rules, operatives, screen rule and `d125_ruling`.
  `test_the_input_seal_covers_every_derivation_input` rewrites each of six inputs
  and asserts the digest moves, and asserts prose does NOT move it.

## Nits

N1 — `student_t_quantile` pins `prec = DECIMAL_WORK_PRECISION` in its own
`localcontext` (`:320`); `test_the_quantile_pins_its_own_precision` calls it at
ambient prec 15 and still gets 20 correct places. N2 — `default_acceptance_id`
(`:535`) derives the epoch segment from `identity_epoch["os_build"]` and refuses
if absent. N3 — `TWO_DRAW_PREDICTION_RULE` copied verbatim from the r6 artifact
("shortest round-tripping decimal"), asserted equal to r6's string by test
because it is digest-bearing.

## Cut table (fix round 1)

One term per cut, one named test, `Ran 1 test` parsed, bytes restored and
sha256-asserted after every cut, `PYTHONDONTWRITEBYTECODE=1` throughout.
Harness `/tmp/s4_mutate2.py`; baseline = restored =
`da8deb1189fbd88bcf03697251952017ab9372f3709f3f9ed3677e0784be8aa8`.

| cut | term | test | runner | result |
|---|---|---|---|---|
| F1 | `rederivation_triggers(row["corpus_doubling_trigger"])` → the predecessor's copy | `test_emitted_triggers_are_derived_from_the_emitted_row` | Ran 1 | KILLED |
| F2 | `screen_rule = SCREEN_RULE_FLOORED_RANGE_ENVELOPE` → `"range_equals_screen"` | `test_floor_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 | KILLED |
| F3 | `if residual > QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL:` → `if False:` | `test_a_failing_forward_check_refuses` | Ran 1 | KILLED |
| F4 | `if digits < QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS:` → `if False:` | `test_a_disagreeing_independent_route_refuses` | Ran 1 | KILLED |
| F5 | `for name in ("manifest.json", "instrument_evidence.json"):` → `for name in ():` | `test_a_manifest_edited_after_finalization_refuses` | Ran 1 | KILLED |
| F6 | `if foreign:` → `if False:` | `test_a_valid_same_epoch_row_outside_the_registration_refuses` | Ran 1 | KILLED |
| F7 | delete `"identity_epoch": payload["identity_epoch"],` from the seal | `test_the_input_seal_covers_every_derivation_input` | Ran 1 | KILLED |
| F8 | `{os_build.lower()}` → literal `25g83` | `test_the_default_acceptance_id_names_the_realized_epoch` | Ran 1 | KILLED |
| F9 | delete `context.prec = DECIMAL_WORK_PRECISION` in `student_t_quantile` | `test_the_quantile_pins_its_own_precision` | Ran 1 | KILLED |
| F10 | inventory `sorted(PRIOR_SET_DISPOSITIONS)` → `("valid",)` | `test_only_the_candidate_label_stops_the_candidate_authenticating` | Ran 1 | KILLED |
| F11 | `_plain(PREFLIGHT_LEVEL_SCREEN_QUANTUM_S)` → `str(...)` | same | Ran 1 | KILLED |
| F12 | `decision_ids ["D-102","D-109"]` → the old four | same | Ran 1 | KILLED |
| F13 | "shortest round-tripping decimal" → "shortest repr" | `test_the_two_draw_rule_string_matches_r6` | Ran 1 | KILLED |
| F14 | production digest recipe → the curated seal | `test_the_artifact_digest_uses_the_production_recipe` | Ran 1 | KILLED |

The seat's original eleven cuts are unchanged in intent; C8 (`screen = max(...)`)
and C9 (`predecessor_ceiling_s` on the row) still hold, and the two tests they
named were rewritten under B2 (F2 and the rebase test now carry them).

## Runner tails

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation \
    tests.test_calibration_bracketing tests.test_docs_freshness
----------------------------------------------------------------------
Ran 185 tests in 56.711s

OK (skipped=1)
SUITE_RC=0

$ python3 -m compileall -q scripts joulewise
COMPILEALL_RC=0
```

`tests.test_issue_calibration_acceptance_generation` alone: `Ran 66 tests` OK.
No full suite, no commit.

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/fixtures/epoch_bootstrap/build.py
 M tests/test_issue_calibration_acceptance_generation.py

$ git diff --stat
 scripts/issue_calibration_acceptance_generation.py | 452 ++++++++++++++++++---
 tests/fixtures/epoch_bootstrap/build.py            |  93 ++++-
 ...test_issue_calibration_acceptance_generation.py | 329 +++++++++++++--
 3 files changed, 751 insertions(+), 123 deletions(-)
```

## Decisions made this round

1. **Two digests, not one.** `derivation_sha256` must be the production recipe or
   the artifact cannot authenticate; the curated input seal SF3 asked for is real
   and useful but is a different invariant, so it is a second key,
   `derivation_input_sha256`, sealed inside the first.
2. **`decision_ids` follows the validator.** Losing the D-079/D-125/D-126
   provenance from that field is acceptable because `d125_ruling` on the row is
   machine-checked (S3 requires it on envelope rows) and `derivation_notes`
   carries the rest — whereas a decision-id list the validator rejects would make
   the artifact unusable.
3. **`backfill_candidate` is emitted, labelled `candidate_not_issued`** with
   `production_issuance_blocked: true`, so the candidate differs from an issued
   artifact ONLY in its label fields. That is what makes the B1 test a real fence
   rather than a tautology.
4. **A-7 refused at the issuer, not merely relied on in the validator.** S3
   enforces it too; issuance stops earlier and names the rows, and the two
   enforcement points are independent.
5. **Machin π for the proof route, transcribed `_PI` for the quantile route.**
   Deliberate asymmetry: it turns the proof into a check on the constant.
6. **Registration epoch resolved up front.** The target epoch is read from the
   registration's rows (unanimity enforced) before the A-7 scan, so an empty
   registration now refuses with `registration: its sessions hold no observations`
   rather than reporting a corpus-size shortfall.

## Still open for the next lens

- **`source_directory` is the absolute custody locator.** The validator only
  checks it is a string, and r6 stores a repo-relative path. For the real
  transaction it should be relativised against the repo root; the candidate is
  a desk artifact so it is not wrong today, but the D-138 transaction should not
  inherit an absolute path into a committed config. Not fixed this round —
  flagging rather than changing an emitted field under time pressure.
- **The member sort (`:958`) has no isolating test**: the fixtures' slot names
  (`d01…d20`) are already in order, so a cut to the sort survives. Building a
  fixture with out-of-order attempt ids is the missing counterfactual.
- **The envelope's predecessor arm remains inert for this generation** (noted in
  the first round and unchanged): with r6 as predecessor, `S ≥ 0.010818 >
  0.010164834757777545`, so `C = max(predecessor, Q99)` can only resolve to Q99.

---

# Fix round 2 (seat S4, on top of `a3ae7bf8` = S4 round 1 + S3 final)

Every item of delta 91 and contract refuter 93 addressed. No git state changed;
scope unchanged. **16 cuts, one term each, all KILLED**; suite `Ran 202 tests …
OK (skipped=1)`, rc 0; `compileall` rc 0.

## 1. SF-1 BLINDNESS — the pre-registered fence now has code

`refuse_open_registration` (`:857`) refuses while ANY named registration session
has a `state` outside `TERMINAL_SESSION_STATES = {"finalized", "aborted"}`
(`:854`). It is called at `_prepare_candidate`'s **third** statement — after the
argument checks and the snapshot load, and **before the generic ledger-refusal
check, before member selection, before any bundle is read and before any
statistic is formed**. Nothing is printed but the refusal reason.

It deliberately precedes the ledger check: an open derivation session is the
physical/pin gap every snapshot consumer tolerates by design (CG46 A7), so the
ledger reports the opaque `calibration_ledger_bracket_session_open`; the seat
must say *which session is open and why that stops the run*.

Two tests, because one alone would be masked:

- `test_the_blindness_gate_is_isolated_from_the_ledger_refusal` drives
  `refuse_open_registration` against a synthetic snapshot with **no refusal
  reason at all** — the state the desk is in once the pin has been advanced
  between nights — and also asserts both terminal states pass. This is the
  isolating counterfactual (cut G1).
- `test_an_open_registration_session_refuses_before_anything_is_computed` runs
  the CLI on a 20-slot fixture with only 6 slots filled (new fixture parameter
  `fill_slots`), asserts rc 3, the reason names the open session and
  "Blindness", and — the point — that stdout contains **no member value, no
  screen, no ceiling and no count** (`assert_no_measured_value_leaked` over the
  lexeme fragments `0.02`, `0.03`, `0.011`, `0.010818`, `corpus n`). Cut G1b
  deletes the call site and this test dies.

## 2. SF-2 — the only ruled floor departure is exactly 17

`:775-790`: a `--minimum-corpus-size` other than 19 must be exactly
`RULED_ALTERNATIVE_CORPUS_SIZE = 17` (`:304`) **and** carry `--ed-ruling`.
`--minimum-corpus-size 3 --ed-ruling <anything>` no longer emits an n = 3 corpus.
The old "may not exceed the ratified floor" refusal is subsumed: 20 is not a
ruled floor either. `test_only_seventeen_is_a_ruled_alternative_floor` exercises
3, 18 and 20, each with a ruling present.

## 3. SF-4 — pending or unresolved prefix rows refuse

`:1170`: any snapshot observation with no content id, or whose classification is
outside `PRIOR_SET_DISPOSITIONS`, refuses issuance naming the attempt ids,
instead of being filtered out of the prior set. Counterfactual fixture: one slot
finalized with disposition `abandoned` (classification `unresolved`), which
leaves the session terminal so the blindness gate cannot mask it.

## 4. SF-3 / 91 — `source_directory` is repo-relative

`_repo_relative_custody` (`:664`) relativises against **the run's `--repo-root`**
(not the issuer's own `REPO_ROOT`, which would be wrong for any checkout but this
one) and refuses a member whose custody lies outside it.
`test_member_source_directory_is_repo_relative_and_re_resolves` asserts every
emitted path is relative, that `root / path` re-resolves to a real directory
named for the member, and that r6 stores its members the same way.

## 5. DF-1 — the envelope arithmetic as pure functions, both operands exercised

`envelope_screen(quantized_range, floor)` (`:689`) and
`envelope_ceiling(predecessor_ceiling, own_q99)` (`:700`) replace the two inline
`max(...)` calls. `test_the_ceiling_takes_whichever_operand_is_larger` covers
predecessor-wins, Q99-wins and the tie, plus both screen arms — so **all four
operand-collapse cuts (G5a–G5d) die**. This is the only way to exercise the
ceiling's predecessor arm at all: r6's ceiling `0.010164834757777545` sits below
the `0.010818` screen floor, so through the CLI the predecessor can never win the
max without failing strict `S < C` first. The finding from rounds 1 and 2 that
the arm is "inert this generation" is now covered by test rather than by prose.

## 6. SF-6 ruled-not-installed — `check`'s registration dry run (CG46 V5)

`registration_dry_run` (`:129`), wired into `check` behind `--session-ids`
(repeatable, `:1463`). Per session it prints kind, state, `terminal=yes|NO`,
declared-slot count, row count, `valid` count, and excluded counts **by
mechanism**; then the prefix's pending/unresolved rows; then whether the
registration would be admissible for `prepare-candidate`, with one line per
blocker. Exit 0 when admissible, 3 otherwise.

**Blindness binds the dry run too** — it is the tool one runs *between* nights,
which is exactly when a leaked value would be fatal. So it reports no bound, no
screen, no statistic and no member value; the bundle reads that classify
exclusions sit **inside** the `if terminal:` branch, so no path touches primary
bytes before the gate opens; and the one count that could carry information (the
retained-valid count) is printed only when the registration is already
admissible. `test_the_dry_run_reports_no_measured_value` asserts the same
no-leak predicate as the CLI test.

`check`'s existing epoch-watch output is **byte-identical** when no registration
is named: `test_check_output_is_unchanged_when_no_registration_is_named` compares
the no-argument output against `--session-ids ""` (empty ids are ignored, `:272`)
and asserts the registration run merely **prefixes**-matches, i.e. the dry run
only ever appends. Cut G6c makes empty ids trigger a dry run and dies.

## 7. SF-7 — the tool describes itself truthfully

The module docstring (surfaced verbatim by `--help`) is rewritten: both
subcommands named; `check` stated READ-ONLY; `prepare-candidate` stated to WRITE
EXACTLY ONE FILE to a caller-named `--out` with **no default destination**, so it
cannot write into `configs/calibration/` by omission; the file stated to be a
candidate the production loader refuses, with issuing named as the D-138
transaction's act; and every refusal enumerated. `"reserved for S4"` is gone.
`test_the_module_docstring_describes_both_subcommands_truthfully` is the
first-use test: it checks each claim and each named refusal term, and that
`--help` carries the text.

## 8. Wording — `derivation_corpus.selection`

Now says what the code does: the member's ledger disposition is `valid` and its
**stored** anchor-v3 record, read from primary evidence bytes **authenticated
against its ledger row**, reports a resolved clock anchor; the value is the
bundle's own `b_fiducial_s` lexeme cross-checked against the row's exact bound
lexeme; and **"no value is re-derived here"**. The pre-registration glossary edit
is S6's and was not touched.

## 9. Nits

`two_draw_prediction_lexeme`'s docstring now states the sealed property
("shortest round-tripping decimal") and notes that Python's float `repr` IS that
decimal. `_PI`'s comment states why the digits past precision 80 are **inert**
(Decimal rounds the literal into the working context on first use; they are guard
digits for a future precision raise) and that the proof route computes π by
Machin instead of reading it, so a typo surfaces as a proof failure.
`derivation_notes.predecessor` now restates the predecessor's `file_sha256`
(computed from the bytes actually loaded) and its `derivation_sha256`, so the note
identifies the predecessor by bytes rather than by a path.

## 10. SF-5 — the proof bounds say whose they are

`quantile_proof.bounds_origin` (`:641`) records, inside the artifact and inside
`derivation_input_sha256`, that 1e-30 and 30 digits are the **issuer's declared
bounds**, that the pre-registration requires a proof and states no numeric bound,
why each was chosen (tighter than the 20 published digits, looser than the
realized 56–57), and that ratifying them in the pre-registration or the D-138
record is the magistrate's edit, not this tool's. The bounds themselves are
unchanged.

## Cut table (fix round 2)

One term per cut, one named test, `Ran 1 test` parsed, bytes restored and
sha256-asserted after every cut, `PYTHONDONTWRITEBYTECODE=1` throughout.
Harness `/tmp/s4_mutate3.py`; baseline = restored =
`156b6fd2f09ff1b1358a7d138e1878f958f3037d93346254c0441759a94a9ff3`.

| cut | term | test | runner | result |
|---|---|---|---|---|
| G1 | `if session is not None and session.state not in TERMINAL_SESSION_STATES:` → `if False:` | `test_the_blindness_gate_is_isolated_from_the_ledger_refusal` | Ran 1 | KILLED |
| G1b | delete the `refuse_open_registration(...)` call site | `test_an_open_registration_session_refuses_before_anything_is_computed` | Ran 1 | KILLED |
| G2 | `if minimum != RULED_ALTERNATIVE_CORPUS_SIZE:` → `if False:` | `test_only_seventeen_is_a_ruled_alternative_floor` | Ran 1 | KILLED |
| G3 | `if unresolved: raise PrepareRefusal(` → `if False:` | `test_an_unresolved_prefix_row_refuses` | Ran 1 | KILLED |
| G4 | `_repo_relative_custody(...)` → `observation.custody_locator` | `test_member_source_directory_is_repo_relative_and_re_resolves` | Ran 1 | KILLED |
| G5a | `max(predecessor_ceiling, own_q99)` → `own_q99` | `test_the_ceiling_takes_whichever_operand_is_larger` | Ran 1 | KILLED |
| G5b | `max(predecessor_ceiling, own_q99)` → `predecessor_ceiling` | same | Ran 1 | KILLED |
| G5c | `max(quantized_range, floor)` → `quantized_range` | same | Ran 1 | KILLED |
| G5d | `max(quantized_range, floor)` → `floor` | same | Ran 1 | KILLED |
| G6 | `terminal = session.state in TERMINAL_SESSION_STATES` → `terminal = True` | `test_the_dry_run_reports_no_measured_value` | Ran 1 | KILLED |
| G6b | dry-run `if unresolved:` → `if False:` | `test_the_dry_run_names_exclusion_mechanisms_and_unresolved_rows` | Ran 1 | KILLED |
| G6c | `[s for s in args.session_ids if s]` → `list(args.session_ids)` | `test_check_output_is_unchanged_when_no_registration_is_named` | Ran 1 | KILLED |
| G7 | docstring "WRITES EXACTLY ONE FILE" → "writes something" | `test_the_module_docstring_describes_both_subcommands_truthfully` | Ran 1 | KILLED |
| G8 | selection "stored … record, read from" → "replay re-derived from" | `test_the_selection_string_describes_a_read_not_a_re_derivation` | Ran 1 | KILLED |
| G9 | predecessor `file_sha256` computed → `"0"*64` | `test_the_predecessor_note_identifies_it_by_bytes` | Ran 1 | KILLED |
| G10 | `bounds_origin` "issuer-declared bounds" → "ratified bounds" | `test_the_quantile_proof_records_where_its_bounds_came_from` | Ran 1 | KILLED |

## Runner tails

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation \
    tests.test_calibration_bracketing tests.test_docs_freshness
----------------------------------------------------------------------
Ran 202 tests in 77.317s

OK (skipped=1)
SUITE_RC=0

$ python3 -m compileall -q scripts joulewise
COMPILEALL_RC=0
```

`tests.test_issue_calibration_acceptance_generation` alone: `Ran 81 tests` OK.
No full suite, no commit.

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/fixtures/epoch_bootstrap/build.py
 M tests/test_issue_calibration_acceptance_generation.py

$ git diff --stat
 scripts/issue_calibration_acceptance_generation.py | 324 +++++++++++++++++++--
 tests/fixtures/epoch_bootstrap/build.py            |  10 +-
 ...test_issue_calibration_acceptance_generation.py | 258 +++++++++++++++-
 3 files changed, 565 insertions(+), 27 deletions(-)
```

## Decisions made this round

1. **The blindness gate precedes the ledger-refusal check.** An open derivation
   session makes the snapshot report `calibration_ledger_bracket_session_open`,
   which would mask the ruled reason. Ordering the gate first makes the tool say
   which session is open and why, and makes the clause isolable.
2. **One home for the gate, two tests.** The check lives only in
   `refuse_open_registration`, not also inside `_registration_observations`. The
   synthetic-snapshot test isolates the clause; the CLI test proves the
   end-to-end no-leak property. I say plainly that the CLI test alone would be
   masked by the ledger reason.
3. **The dry run's exclusion classification sits inside the terminal branch.**
   Reading a bundle to name a mechanism leaks nothing by itself, but keeping the
   whole branch behind the gate means no code path can reach a member value
   before the registration is terminal — a structural guarantee rather than a
   reviewed one.
4. **`--minimum-corpus-size 20` now refuses too.** The previous "may not exceed
   the floor" refusal is gone as a separate clause; a stricter floor is simply
   not one of the two ruled values. This changes an existing refusal message and
   is noted here rather than left for a refuter to notice.
5. **Relativise against `--repo-root`, not `REPO_ROOT`.** The issuer's own repo
   root is wrong for any run whose ledger lives elsewhere (every test fixture,
   and any clone-based rehearsal). Refusing a custody path outside that root is
   the fail-closed half.
6. **`envelope_screen` / `envelope_ceiling` extracted as pure functions.** Not
   cosmetic: it is the only way to exercise the ceiling's predecessor arm, which
   the current predecessor makes unreachable through the CLI, and it makes all
   four operand-collapse cuts killable.
7. **Empty `--session-ids` values are ignored** so the epoch-watch output stays
   byte-identical, which is the property the round asked to be tested.
8. **Not touched, deliberately:** the pre-registration (S6's, per rule 11 — SF-5
   and the glossary wording both need a magistrate/S6 edit, and this report names
   both), and SF-8's licence sentence in `issuance.reason`, which was not in this
   round's list; it is a one-string change that moves `derivation_sha256` and not
   `derivation_input_sha256`, and is the next obvious bench-sized item.

## Still open

- **SF-8** (the candidate saying in words what it licenses) — not in this round's
  brief; one string in `issuance.reason`.
- **The member sort** still has no isolating test (fixture slot names are already
  ordered).
- **Pre-registration edits are S6's**: the SF-5 bounds sentence and the
  "Anchor-v3 replay" glossary definition. The artifact side of both is done.

---

# Fix round 3 (seat S4, on top of `6e9d2a63`)

One item: contract refuter 93 **SF-8**. Nothing else touched.

## What landed

`CANDIDATE_LICENCE` (`:306`) carries the sentence verbatim, and the `issuance`
block emits it under `licence` (`:1351`):

> These bytes license nothing: no measurement window, no claim, no threshold.
> No tool may load them as authority; the production loader refuses them by
> artifact_role.

It sits **inside the sealed artifact**, so `derivation_sha256` (the production
recipe, the canonical digest of everything but itself) covers it and it cannot be
edited away without moving the artifact's own digest.

## Where it sits in the transaction, and why

`licence` is a **candidate-LABEL field**, in the same class as
`issuance.status`, `issuance.claim_eligible`, `candidate_not_issued` and the two
`backfill_candidate` label fields. The D-138 transaction **rewrites the whole
`issuance` block** when it issues rather than editing fields inside it, so the
sentence cannot survive into an issued artifact and quietly contradict it — an
issued acceptance saying "these bytes license nothing" would be worse than no
sentence at all.

`test_only_the_candidate_label_stops_the_candidate_authenticating` now states
that explicitly: it asserts `licence` IS present on the candidate, replaces the
whole block, asserts `licence` is NOT present afterwards, and still finds the
production `_valid_acceptance_bound` **admits** the result. So the key is proven
to be a label field rather than assumed to be one, and the round-1 property (only
the candidate label stops the artifact authenticating) still holds with the key
present.

## Test

`test_the_candidate_states_its_licence_in_words` asserts the sentence verbatim;
asserts that rewriting it **moves** `derivation_sha256` (it is sealed) and does
**not** move `derivation_input_sha256` (prose is deliberately outside the input
seal, which is exactly what that seal was built for); and asserts the loader does
what the sentence says it does — `load_calibration_acceptance_bound` returns
`None` on the emitted file.

## Cut table (fix round 3)

Baseline = restored = `e4e0260d30ac459efe5f2d72c3dbbe56431cdd724d82671040a0497bb2acd602`;
`PYTHONDONTWRITEBYTECODE=1`; harness `/tmp/s4_mutate4.py`.

| cut | term | test | runner | result |
|---|---|---|---|---|
| H1 | delete `"licence": CANDIDATE_LICENCE,` | `test_the_candidate_states_its_licence_in_words` | Ran 1 test | KILLED |
| H1b | same deletion | `test_only_the_candidate_label_stops_the_candidate_authenticating` | Ran 1 test | KILLED |

H1b is the label-class assertion: with the key gone, the "is it present, then is
it stripped" pair in the authentication test fails, so the claim that `licence`
belongs to the stripped label set is itself under test.

## Runner tail

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation
----------------------------------------------------------------------
Ran 82 tests in 64.834s

OK
SUITE_RC=0

$ python3 -m compileall -q scripts
COMPILEALL_RC=0
```

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/test_issue_calibration_acceptance_generation.py
```

No git state changed, no commit, nothing outside the two files touched.

---

# Fix round 4 (seat S4, on top of `410229f1`)

All seven delta-96 items. **10 cuts, one term each, all KILLED**; suite
`Ran 211 tests … OK (skipped=1)`, rc 0; `compileall` rc 0. No git state changed.

## E-1 — the dry run's `filled` count comes from the session record

`registration_dry_run` reports `declared={len(session.declared_slots)}` and
`filled={len(session.finalized_slots)}` — the LENGTH of each mapping, never the
slot objects. Published observations were the wrong source: an open session
publishes none, so a 6-of-20 registration reported no progress at all.
`test_the_dry_run_counts_filled_slots_on_an_open_session` parses the line with
the template regex and asserts `declared=20 filled=6 terminal=no`, plus the
no-leak predicate. Cut E1 swaps the count back to published rows and dies.

## E-2 — the `"aborted"` arm is witnessed, not assumed

`test_an_aborted_session_is_terminal` builds a 24-slot session, fills 20 and
closes it with `abort_bracket_session(reason="window_exhausted")` — the
pre-registration's planned early close. It asserts against the **literal** state
name rather than iterating `TERMINAL_SESSION_STATES`, so removing `"aborted"`
from the set fails here instead of quietly agreeing with itself (which is what
round 2's `for state in TERMINAL_SESSION_STATES` subtest did). It also runs
`prepare-candidate` on that fixture and gets a 20-member corpus, so the blindness
gate is shown to PASS an aborted registration rather than merely to exist. New
fixture parameter `abort_reason`. Cut E2 removes the arm and dies.

## E-3 — `bounds_origin` is now true against S6's pre-registration

S6's round-5 text states both bounds (`:174`, `:179`, `:185`: "residual at most
1e-30", "at least 30 significant decimal digits", "the ISSUER'S DECLARED
bounds"). The old sentence claimed the pre-registration "states no numeric
bound" — false, and pinned by `assertIn`, so it would have travelled. It now
reads "issuer-declared bounds, stated in the pre-registration's quantile-proof
clause and recorded here in the candidate", names both numbers, and the test pins
the new wording plus `1e-30` and `30 significant digits`.

## E-4 — `check`'s exit code answers the question asked

With `--session-ids`, the exit code is the dry-run verdict alone: **0**
admissible, **`DRY_RUN_INADMISSIBLE_EXIT = 5`** otherwise, distinct from the
epoch watch's 3 so a caller can tell "the machine has drifted" from "the
registration is not ready". The epoch-watch table still prints in full above it.
The reasoning is in the code: a drifted epoch is *why* a new corpus is being
captured, so it must not mask the registration question. Without `--session-ids`
the old rc semantics and bytes are unchanged (round 2's test still passes). Two
CLI-boundary tests: admissible registration on a mismatched epoch → rc 0 with
`MISMATCH` still on stdout; open registration → rc 5, asserted `!= 3`.

## E-5 — the `if terminal:` gate is now load-bearing and pinned

With E-1 the exclusion loop iterates `session.finalized_slots.values()`, which is
**non-empty for an open session too** — so removing the gate really does open
bundles mid-campaign, and the gate stopped being decorative.
`test_no_bundle_is_opened_for_an_open_session` replaces `_read_member_evidence`
with one that raises, so any path reaching a member's primary bytes for an open
session fails. Cut E5 (`if terminal:` → `if True:`) dies. This is the item round 2
could only argue for in prose; it is now a test.

## E-6 — every flag documents itself; the docstring passes the first-use test

Help strings on all eleven flags across both subcommands (`--ledger`,
`--head-pin`, `--repo-root`, `--acceptance`, `--session-ids`,
`--preregistration`, `--predecessor-acceptance`, `--registration-session-id`,
`--d125-ruling`, `--ed-ruling`, `--minimum-corpus-size`, `--epoch-catalog-id`,
`--acceptance-id`, `--out`), and on the `check` subcommand itself.
`test_every_flag_carries_a_help_string` walks the parser tree and asserts each
non-`-h` action has one, so a new flag cannot land undocumented.

The docstring now builds each term of art before it does any work: OPERATIVES
("the three numbers the acceptance actually governs measurement with"), BRACKET
SCREEN ("the drift below which a measurement window passes without spending any
of its error budget"), BUDGET CEILING ("the largest drift the generation will
ever budget for"), LEVEL SCREEN ("the absolute bound above which a single capture
is refused before a window opens"), PRIOR-SET PREFIX ("the run of ledger rows at
or below the cutoff"), QUANTILE PROOF ("checked two independent ways, before any
threshold derived from it was written down"), TRIGGER OBSERVATION ("a later
capture whose result would oblige the generation to be re-derived"), COLD SCIENCE
GATE ("the fresh-eyes review of the exclusions and the per-night diagnostics that
no one involved in the capture may sit on"), D-138 transaction ("the single
reviewed commit that swaps the live acceptance and every pin that names it"), and
one clause each for D-102, D-109, D-125, D-126.
`test_the_docstring_glosses_every_term_of_art_at_first_use` checks the term, the
gloss, and that the gloss arrives at or before the term's first use — it collapses
line wrapping first, since wrapping is not meaning.

## E-7 — the dry run trimmed to a fixed template

```
                                              <- blank
Registration dry run (counts and states only; no measured value)
<id>: kind=<kind> state=<state> terminal=<yes|no> declared=<int> filled=<int> excluded=<none|mech:count,...>
<id>: absent
prefix pending or unresolved rows: <int>
registration admissible for prepare-candidate: <yes|no>
  blocker: <reason>
```

`rows=`, `valid=` and the retained-count line are gone (not in the
pre-registration's list), and the prefix pending/unresolved rows are a **COUNT**
— naming attempt ids invites reading them, and the count is all a desk decision
needs. `test_every_dry_run_line_matches_the_fixed_template` matches line 2
against a regex in which only integers and enum words vary, and pins lines 0, 1,
3, 4, 5 and the blocker shape exactly.

## Cut table (fix round 4)

Baseline = restored = `a5af6f15f18b50565331e664ff87c939f756ae01afeeddca59a65385e4d0e9b4`;
one term per cut, `Ran 1 test` parsed, sha256-asserted after each,
`PYTHONDONTWRITEBYTECODE=1`. Harness `/tmp/s4_mutate5.py`.

| cut | term | test | runner | result |
|---|---|---|---|---|
| E1 | `filled={len(session.finalized_slots)}` → count of published rows | `test_the_dry_run_counts_filled_slots_on_an_open_session` | Ran 1 | KILLED |
| E2 | `TERMINAL_SESSION_STATES` drops `"aborted"` | `test_an_aborted_session_is_terminal` | Ran 1 | KILLED |
| E3 | `bounds_origin` drops "stated in the pre-registration's quantile-proof clause" | `test_the_quantile_proof_records_where_its_bounds_came_from` | Ran 1 | KILLED |
| E4 | `return dry_run_code` → `3 if errors or mismatches else dry_run_code` | `test_check_returns_the_registration_verdict_when_one_is_named` | Ran 1 | KILLED |
| E4b | `DRY_RUN_INADMISSIBLE_EXIT = 5` → `3` | `test_check_returns_a_distinct_code_for_an_inadmissible_registration` | Ran 1 | KILLED |
| E5 | `if terminal:` → `if True:` around the bundle reads | `test_no_bundle_is_opened_for_an_open_session` | Ran 1 | KILLED |
| E6 | `--out`'s `help=` → an unused kwarg | `test_every_flag_carries_a_help_string` | Ran 1 | KILLED |
| E6b | delete the LEVEL SCREEN gloss | `test_the_docstring_glosses_every_term_of_art_at_first_use` | Ran 1 | KILLED |
| E7 | prefix line gains free-form text after the count | `test_every_dry_run_line_matches_the_fixed_template` | Ran 1 | KILLED |
| E7b | `_excluded_summary` → `str(dict)` | same | Ran 1 | KILLED |

## Runner tails

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation \
    tests.test_calibration_bracketing tests.test_docs_freshness
----------------------------------------------------------------------
Ran 211 tests in 68.208s

OK (skipped=1)
SUITE_RC=0

$ python3 -m compileall -q scripts joulewise
COMPILEALL_RC=0
```

`tests.test_issue_calibration_acceptance_generation` alone: `Ran 90 tests` OK.

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/fixtures/epoch_bootstrap/build.py
 M tests/test_issue_calibration_acceptance_generation.py

$ git diff --stat
 scripts/issue_calibration_acceptance_generation.py | 278 ++++++++++++++-------
 tests/fixtures/epoch_bootstrap/build.py            |  13 +-
 ...test_issue_calibration_acceptance_generation.py | 222 ++++++++++++++--
 3 files changed, 411 insertions(+), 102 deletions(-)
```

## Decisions

1. **Exit 5, not 3, for an inadmissible registration.** A distinct code lets the
   caller separate epoch drift from registration readiness; the test asserts
   `!= 3` so a future collapse is caught.
2. **Dry-run output is now lower-case `yes`/`no` and `absent`** for uniformity
   with the template regex; round 2's `YES`/`NO`/`terminal=NO` assertions were
   updated accordingly.
3. **`valid=` and the retained-count line were dropped**, not merely renamed:
   E-7's list is exhaustive, and every count that is not needed for a desk
   decision is one more thing to be tempted by mid-campaign.
4. **Whitespace is normalised before prose matching** in both docstring tests —
   argparse rewraps the help text, and a term split across two lines is still the
   term.
5. **E-5 became a real fence only because of E-1.** Iterating
   `session.finalized_slots` rather than published observations is what makes the
   gate load-bearing; the two items are one change, and I would not claim the
   gate is pinned without E-1 in place.

---

# Fix round 5 (seat S4, on top of `4832dc75`)

One item: the lead's diff-gate finding (record 110). Nothing else touched.

## The defect

`prior_observations` labelled every prior-set row with

```python
target_catalog_id if dict(observation.identity_epoch) == identity_epoch
else predecessor_catalog_id
```

The catalog has exactly two entries, so labelling is a two-way choice — and a
two-way choice made with `else` silently LABELS anything it does not recognise.
A row captured under a **third** identity epoch (a further OS update mid-campaign,
or a corrupted row) would enter the prior set wearing the predecessor's catalog
id, and every downstream check would then agree with the lie: the catalog would
hold two honest entries, the row would name one of them, and the epoch it was
actually captured under would have vanished from the record.

## The fix

A guard immediately before the labelling (`:1221`): any snapshot observation
with a content id whose identity epoch matches **neither** the target's nor the
predecessor's refuses, naming the attempt ids:

```
prior set: attempt <id> carries an identity epoch that is neither the target's
nor the predecessor's; not issued
```

The two-entry catalog is unchanged — the guard is what lets it stay exactly two
entries and stay honest, rather than growing an entry to accommodate whatever
turns up.

## Tests

`test_a_third_identity_epoch_in_the_prefix_refuses` builds a second, unregistered
derivation session under epoch `25H01` (new fixture parameter
`second_session_epoch`) and asserts the exact reason. The counterfactual is
**isolating by construction**: that row is `valid` and has a content id, so the
addendum A-7 scan cannot see it (A-7 only ranges over TARGET-epoch rows) and the
pending/unresolved scan cannot see it either — only the epoch guard can refuse it.

`test_the_epoch_catalog_stays_exactly_two_entries` asserts the catalog holds
exactly the target's and the predecessor's epochs and that every prior-set row's
`epoch_id` is one of the catalog's keys, so no row is labelled by default.

## Cut table (fix round 5)

Baseline = restored = `65ffe7e239b26e4108fbadf2ec8d3361a5576398b809c03d93107ef0f18178c3`;
`Ran 1 test` parsed per cut, sha256-asserted after each,
`PYTHONDONTWRITEBYTECODE=1`. Harness `/tmp/s4_mutate6.py`.

| cut | term | test | runner | result |
|---|---|---|---|---|
| J1 | `if foreign_epoch:` → `if False:` | `test_a_third_identity_epoch_in_the_prefix_refuses` | Ran 1 test | KILLED |
| J1b | the epoch comparison `not in (identity_epoch, predecessor_epoch)` → `False` | same | Ran 1 test | KILLED |

J1b is the operand cut: with the comparison gone the list is empty and the
refusal never forms, so the guard's condition is under test and not only its
`if`.

## Runner tail

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation
----------------------------------------------------------------------
Ran 92 tests in 110.600s

OK
SUITE_RC=0

$ python3 -m compileall -q scripts joulewise
COMPILEALL_RC=0
```

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/fixtures/epoch_bootstrap/build.py
 M tests/test_issue_calibration_acceptance_generation.py
```

No git state changed, no commit, nothing outside scope touched.

---

# Fix round 6 (seat S4, on top of `9c998a9d`)

Terminal review 109's B-1, B-2, B-3 and the "two homes" / binary64 / line-pin
items. **10 cuts, one term each, all KILLED**; suite `Ran 227 tests … OK
(skipped=1)`, rc 0; `compileall` rc 0. No git state changed.

## B-1 — the machine facts that VOID the registration now have an enforcer

The pre-registration names two: the `os_build` in its Epoch clause and the
`/usr/bin/powermetrics` sha256 "in force", and says a change to either voids the
registration. Nothing read them.

`preregistration_epoch_pins(text)` parses both out of the **file the caller
names**, by strict patterns, so the campaign's own text is the authority rather
than a constant restated in the issuer. Exactly one match each: **absent and
ambiguous both refuse** — a document that names two `os_build` values cannot be
guessed past. `prepare-candidate` then refuses when the registration's target
epoch `os_build` differs, or when the registration's rows do not unanimously
carry the pre-registered `powermetrics_sha256` (read from their T1 bindings).

`check` gained an optional `--preregistration`: given one, it appends a single
line comparing the machine's **observed** binary digest against the
pre-registered one and marks the watch failed on a mismatch. Without the flag the
watch output is byte-identical, asserted by prefix comparison.

The fixture's `T1_BINDINGS` now carries the real pre-registered digest — with a
placeholder it would have exercised the void-registration path on every test.

## B-2 — the corpus is bound to the pre-registered SHAPE

Exactly **three** `--registration-session-id` values unless `--nights-ruling`
names a written ruling; every registration session must declare exactly **12**
slots (read from the session record's `declared_slots`) unless
`--slot-count-ruling`. A corpus assembled from a different schedule is a
different experiment, whatever its statistics say.

The shared test runner supplies both departure flags, because every earlier
fixture is one session of N slots; the two shape tests omit them. One test builds
the genuine shape — two sessions of exactly 12 declared slots — and shows the
NIGHT fence firing while the SLOT fence stays silent, so the two are not one
fence wearing two names.

## B-3 — the pre-registration text is pinned

`--preregistration-sha256` is now **required**, and a file whose digest differs
refuses. Without it the tool would derive against whatever the document says
today, which is the one edit a pre-registration exists to forbid. The arm
materials will carry the digest.

## Two homes closed, and a literal that now checks itself

`R6_PREFLIGHT_LEVEL_SCREEN_S` is **deleted**. The screen-challenge threshold is
read from the authenticated predecessor's
`ratified_operatives.preflight_level_screen_s` and threaded into `_select_members`
and the refusal message. A test asserts the emitted
`screen_challenge_threshold_s` equals r6's own value **and that the module no
longer has the attribute at all**, so the second home cannot quietly return.

`R6_MAXIMUM_PLUS_RANGE_S` stays as the CG46 A-4 ruled literal — it is a ruling,
not a derivation — but the run now recomputes the predecessor's `maximum_s +
range_s` in Decimal and **refuses** if the literal no longer describes that
corpus. A ruled constant that has outlived the artifact it describes is worse
than a derived one.

## Prose

`derivation_sha256`'s docstring cites `_canonical_sha256` and the `core` mapping
by name instead of `(:660, :764)`; a test asserts no `` `:NNN` `` line pin remains
in it. The module docstring now states that the quantiles are computed in
80-digit decimal but the two-draw **predictions** are evaluated in **binary64**
and recorded as the shortest decimal that reads back as the same double — r6's
sealed rule string, kept verbatim so this generation's arithmetic is the
predecessor's arithmetic. (The pre-registration edit is S6's.)

## Cut table (fix round 6)

Baseline = restored = `ebf0e919d70e6761899b4730dfad29e6c94971d837c9851fc412882c2f3c6cba`;
one term per cut, `Ran 1 test` parsed, sha256-asserted after each,
`PYTHONDONTWRITEBYTECODE=1`. Harness `/tmp/s4_mutate7.py`.

| cut | term | test | runner | result |
|---|---|---|---|---|
| K1 | `if target_epoch.get("os_build") != registered_os_build:` → `if False:` | `test_a_registration_under_another_os_build_is_void` | Ran 1 | KILLED |
| K2 | `if observed_powermetrics != {registered_powermetrics}:` → `if False:` | `test_a_registration_under_another_powermetrics_binary_is_void` | Ran 1 | KILLED |
| K3 | `if len(found) != 1:` → `if False:` | `test_an_absent_or_ambiguous_epoch_pin_refuses` | Ran 1 | KILLED |
| K4 | `if args.preregistration is not None:` → `if True:` | `test_check_compares_the_preregistered_binary_only_when_asked` | Ran 1 | KILLED |
| K5 | the night-count fence → `if False:` | `test_a_registration_of_other_than_three_nights_refuses` | Ran 1 | KILLED |
| K6 | `if declared != PREREGISTERED_SLOTS_PER_NIGHT:` → `if False:` | `test_a_night_declaring_other_than_twelve_slots_refuses` | Ran 1 | KILLED |
| K7 | `if preregistration_sha256 != args.preregistration_sha256:` → `if False:` | `test_a_changed_preregistration_refuses` | Ran 1 | KILLED |
| K8 | level screen read from the predecessor → a restated literal | `test_the_level_screen_threshold_comes_from_the_predecessor` | Ran 1 | KILLED |
| K9 | `if recomputed != R6_MAXIMUM_PLUS_RANGE_S:` → `if False:` | `test_the_a4_diagnostic_is_checked_against_the_predecessor` | Ran 1 | KILLED |
| K10 | docstring drops "evaluated in BINARY64" | `test_the_docstring_states_the_binary64_prediction_step` | Ran 1 | KILLED |

K4 is the inverse-direction cut: forcing the comparison ON breaks the
byte-identical-without-the-flag property, which is the half a "does it fire"
test would miss.

## Runner tails

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation \
    tests.test_calibration_bracketing tests.test_docs_freshness
----------------------------------------------------------------------
Ran 227 tests in 199.357s

OK (skipped=1)
SUITE_RC=0

$ python3 -m compileall -q scripts joulewise
COMPILEALL_RC=0
```

`tests.test_issue_calibration_acceptance_generation` alone: `Ran 106 tests` OK.

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/fixtures/epoch_bootstrap/build.py
 M tests/test_issue_calibration_acceptance_generation.py

$ git diff --stat
 scripts/issue_calibration_acceptance_generation.py | 189 ++++++++++++++++++--
 tests/fixtures/epoch_bootstrap/build.py            |  17 +-
 ...test_issue_calibration_acceptance_generation.py | 198 ++++++++++++++++++++-
 3 files changed, 384 insertions(+), 20 deletions(-)
```

## Decisions

1. **The pins are PARSED, not restated.** Copying the two values into the issuer
   would have created the third home this round exists to close, and would let
   the code and the campaign document disagree silently. The cost is a regex
   contract with S6's text — so absent and ambiguous both refuse loudly rather
   than defaulting.
2. **`--preregistration-sha256` is required, `--preregistration` was already.**
   Together they mean the tool cannot run against an unpinned document at all.
3. **The shape rulings are separate flags**, not one `--shape-ruling`: a ruling
   to run two nights is not a ruling to run nights of a different length, and
   collapsing them would let one written ruling license both departures.
4. **The fixture carries the real pre-registered powermetrics digest.** A
   placeholder would have made every existing test travel the void-registration
   path, and the round's own fences would have looked like they were passing.
5. **`R6_MAXIMUM_PLUS_RANGE_S` kept as a literal but checked.** It is a ruled
   number (A-4 corrected its last digits), so deriving it would discard the
   ruling; recomputing and comparing keeps the ruling authoritative while making
   it impossible for it to describe the wrong corpus.
6. **The `check` comparison marks the watch failed on mismatch** rather than
   only printing: the binary having rotated is exactly the condition that voids
   an armed campaign, and a desk watch that reports it as informational would be
   the wrong shape.

---

# Fix round 7 (seat S4, on top of `4bf2ce9f`)

One item: row-10 review 117's nit. Nothing else touched.

## The defect

The three-nights fence counted flag REPETITIONS. `--registration-session-id A`
given three times satisfied `len(session_ids) != 3` while the ledger held a
single session, so a one-night corpus could present itself as the pre-registered
three-night shape.

## The fix, in two independent places

`refuse_repeated_sessions` (`:953`) refuses a repeated id **on its own terms**,
naming it: a registration that names the same night twice is malformed whatever
the count fence would have said, because the caller who typed it meant something
the ledger cannot supply. It runs before the blindness gate — a malformed
registration is malformed regardless of session state, and the refusal reveals
nothing about any value.

The fence itself now counts `distinct_nights = len(set(session_ids))` (`:1218`).
Deduplicating alone would have been enough to close the hole, but then one check
would rest on the other having run, and deleting either would silently restore
the other's defect.

## Tests

`test_a_repeated_registration_session_refuses` gives the same id twice with no
nights ruling and asserts the printed reason
`registration names a session more than once: derivation-night-1`.

`test_the_night_count_fence_counts_distinct_sessions` disables
`refuse_repeated_sessions` — the only way to reach the count fence with
duplicates at all — and asserts the fence then refuses with
`registration names 1 sessions, not the pre-registered 3`. Extracting the
repetition check into a named function was done for exactly this reason: inline,
the second term had no isolating counterfactual, and a term nothing can isolate
is either dead or unruled.

## Cut table (fix round 7)

Baseline = restored = `46eacce5c4ce8422f93ac2c661427d9d03199bc816db364f2e190ad9e3c8ad85`;
one term per cut, `Ran 1 test` parsed, sha256-asserted after each,
`PYTHONDONTWRITEBYTECODE=1`. Harness `/tmp/s4_mutate8.py`.

| cut | term | test | runner | result |
|---|---|---|---|---|
| L1 | `if repeated:` → `if False:` | `test_a_repeated_registration_session_refuses` | Ran 1 test | KILLED |
| L1b | `if list(session_ids).count(session_id) > 1` → `if False` | same | Ran 1 test | KILLED |
| L2 | `len(set(session_ids))` → `len(session_ids)` | `test_the_night_count_fence_counts_distinct_sessions` | Ran 1 test | KILLED |

L1b is the operand cut: with the detector gone the set is empty and the refusal
never forms, so the condition is under test and not only its `if`. L2 is the
original defect, restored and caught.

## Runner tail

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_issue_calibration_acceptance_generation
----------------------------------------------------------------------
Ran 108 tests in 203.303s

OK
SUITE_RC=0

$ python3 -m compileall -q scripts joulewise
COMPILEALL_RC=0
```

```
$ git status --short
 M scripts/issue_calibration_acceptance_generation.py
 M tests/test_issue_calibration_acceptance_generation.py
```

No git state changed, no commit, nothing outside the two files touched.
