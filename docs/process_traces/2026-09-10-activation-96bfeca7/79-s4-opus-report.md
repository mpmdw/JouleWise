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
