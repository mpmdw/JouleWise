# 91 — Seat S4 fix round 1, DELTA RE-AUDIT (execution lens, Opus)

Worktree `/Users/edr/code/JouleWise-wt-s4-issuer-prepare`, branch
`feat/2026-09-10-epoch-s4-issuer-prepare-candidate`, HEAD `a3ae7bf8`
(= `501bde4f` + the merge of S3's final). Round under audit `f31884d7 → 501bde4f`,
diff scope `a18cb812..501bde4f`. Read-only except temporary source cuts, every
one restored byte-for-byte and sha256-asserted in a `finally`.
`PYTHONDONTWRITEBYTECODE=1` on every subprocess. No git state changed, nothing
written to `configs/calibration/`, no capture, no `[QUIET-MAC]` measurement.
Harnesses under `/tmp/s4delta/`; fixtures in per-run `TemporaryDirectory`.

## VERDICT: **should_fix** — no blocker.

Every prior-round finding (B1, B2, B3, SF1, SF2, SF3, N1–N3) is cured, and each
cure is killed by at least one named cut. **28 of 29 cuts KILLED; one survivor**,
and the survivor is a clause the seat itself disclosed as open (the inert
predecessor arm of the ceiling `max`) — it is structurally unreachable for the r7
generation and therefore cannot mis-emit today, but the cold-gate-69 ratchet it
implements has no counterfactual and will become reachable at r8.

Prior-round B1 is verified cured **at the strongest available bar**: the emitted
candidate, with only its three label fields flipped and its row + id registered
in-test, is ADMITTED by the production `_valid_acceptance_bound`. That converts
the whole artifact shape into a live fence, and all five ordered cuts against it
die.

---

## 1. Cut table

Baseline = restored `sha256(scripts/issue_calibration_acceptance_generation.py)`
= `da8deb1189fbd88bcf03697251952017ab9372f3709f3f9ed3677e0784be8aa8`, asserted
identical before and after **every** cut (harness aborts otherwise).
Test path prefix `tests.test_issue_calibration_acceptance_generation.PrepareCandidateTest`.

### 1a. B1 cure — the ordered cuts (all against the authentication test)

| cut | clause | mutation | test | runner | result |
|---|---|---|---|---|---|
| D1 | `:1088` triggers | `rederivation_triggers(row[...])` → `sorted(predecessor["prospective_rederivation"]["triggers"])` | `test_only_the_candidate_label_stops_the_candidate_authenticating` | Ran 1 test in 7.525s, FAILED (failures=1) | KILLED |
| D1b | same | same | `test_emitted_triggers_are_derived_from_the_emitted_row` | Ran 1 in 7.415s, FAILED | KILLED |
| D2 | `:1143` digest recipe | production `_canonical_sha256(artifact − key)` → the old curated subset (`derivation_input_sha256`) | `test_only_the_candidate_label_…` | Ran 1 in 7.404s, FAILED | KILLED |
| D2b | same | same | `test_the_artifact_digest_uses_the_production_recipe` | Ran 1 in 7.600s, FAILED | KILLED |
| D3 | `:937` inventory | add `if any(...)` → zero-count dispositions dropped | `test_only_the_candidate_label_…` | Ran 1 in 7.609s, FAILED | KILLED |
| D4 | `:1062` `decision_ids` | `["D-102","D-109"]` → `["D-079","D-102","D-125","D-126"]` | `test_only_the_candidate_label_…` | Ran 1 in 7.669s, FAILED | KILLED |
| D5 | `:998` quantum lexeme | `_plain(PREFLIGHT_LEVEL_SCREEN_QUANTUM_S)` → `str(...)` (`"1E-15"`) | `test_only_the_candidate_label_…` | Ran 1 in 7.604s, FAILED | KILLED |
| D22 | `:958` member sort | `sorted(..., key=member_id)` → `reverse=True` | `test_only_the_candidate_label_…` | Ran 1 in 8.765s, FAILED | KILLED |

D22 is notable: the seat listed "the member sort has no isolating test" as an
open item, but the new B1 authentication test **does** kill a sort reversal
(the validator's `member_ids == sorted(member_ids)` clause fires through it).
The seat under-claimed; the item is closed.

### 1b. B3 — the quantile proof

| cut | clause | mutation | test | runner | result |
|---|---|---|---|---|---|
| D6 | `:471` forward-residual bound | `if residual > BOUND:` → `if False:` | `test_a_failing_forward_check_refuses` | Ran 1 in 7.590s, FAILED | KILLED |
| D7 | `:477` closed-form agreement bound | `if digits < BOUND:` → `if False:` | `test_a_disagreeing_independent_route_refuses` | Ran 1 in 7.592s, FAILED | KILLED |
| D21 | `:442` `_agreement_digits` equal-shortcut | `if left == right:` → `if True:` (always claims full agreement) | `test_a_disagreeing_independent_route_refuses` | Ran 1 in 8.870s, FAILED | KILLED |
| D18 | `:352` arctan reflection | `if x > 1:` → `if False:` | `test_the_closed_form_route_reproduces_r6_and_both_parities` | Ran 1 in 8.013s, FAILED (errors=1) | KILLED |
| D19 | `:397` A&S parity branch → even only | `if df % 2 == 0:` → `if True:` | same | Ran 1 in 8.051s, FAILED | KILLED |
| D20 | same → odd only | `if df % 2 == 0:` → `if False:` | same | Ran 1 in 8.254s, FAILED (failures=2) | KILLED |

### 1c. SF1 / SF2 / B2 / F2

| cut | clause | mutation | test | runner | result |
|---|---|---|---|---|---|
| D8 | `:345` custody-hash loop (SF1) | `for name in ("manifest.json","instrument_evidence.json"):` → `for name in ():` | `test_a_manifest_edited_after_finalization_refuses` | Ran 1 in 8.625s, FAILED | KILLED |
| D9 | `:831` A-7 refusal (SF2) | `if foreign:` → `if False:` | `test_a_valid_same_epoch_row_outside_the_registration_refuses` | Ran 1 in 8.765s, FAILED | KILLED |
| D10 | `:871` rule name (B2) | `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` → `"range_equals_screen"` | `test_floor_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 in 7.875s, FAILED | KILLED |
| D10b | same | same | `test_range_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 in 8.878s, FAILED | KILLED |
| D17 | `:562` tuple conversion (F2) | `tuple(converted[field])` → `list(...)` | `test_range_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 in 8.722s, FAILED | KILLED |

The prior round's X1 (the surviving custody cut) now dies — SF1 closed.

### 1d. Operand-collapse cuts (isolation rule)

| cut | expression | collapsed to | test | runner | result |
|---|---|---|---|---|---|
| D11 | `:868` `screen = max(quantized_range, D125_SCREEN_FLOOR_S)` | `quantized_range` | `test_floor_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 in 8.730s, FAILED | KILLED |
| D12 | same | `D125_SCREEN_FLOOR_S` | `test_range_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 in 8.408s, FAILED | KILLED |
| D13 | `:874` `ceiling = max(predecessor_ceiling, Decimal(prediction_99))` | `predecessor_ceiling` | `test_the_ceiling_is_the_max_of_predecessor_and_own_q99` | Ran 1 in 8.887s, FAILED (errors=1) | KILLED |
| **D14** | same | `Decimal(prediction_99)` | `test_the_ceiling_is_the_max_of_predecessor_and_own_q99` | Ran 1 in 8.827s, **OK** | ***SURVIVED*** |
| D14b | same | same | `test_screen_at_or_above_the_ceiling_refuses` | Ran 1 in 7.437s, OK | SURVIVED |
| D14c | same | same | `test_emitted_row_refuses_when_its_predecessor_ceiling_is_rebased` | Ran 1 in 7.452s, OK | SURVIVED |
| D14d | same | same | `test_only_the_candidate_label_stops_the_candidate_authenticating` | Ran 1 in 7.192s, OK | SURVIVED |
| D15 | `:869` `floor_bound = screen != quantized_range` | `False` | `test_floor_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 in 8.675s, FAILED | KILLED |
| D16 | same | `True` | `test_range_bound_corpus_row_is_admitted_alongside_r6` | Ran 1 in 8.697s, FAILED | KILLED |

---

## 2. The one finding

### should_fix DF-1 — the predecessor arm of the ceiling `max` is untested and, with r6 as predecessor, untestable

`ceiling = max(predecessor_ceiling, Decimal(prediction_99))` (`:874`) collapses to
its Q99 operand with **no test anywhere in the suite noticing** — four separate
tests chosen as its most plausible killers all pass under the collapse (D14,
D14b, D14c, D14d above).

Why it is not a blocker: the collapse is unreachable for THIS generation, by
arithmetic rather than by luck. `S = max(quantized range, 0.010818) ≥ 0.010818`
always, and r6's ceiling is `0.010164834757777545 < 0.010818`. The strict
`S < C` gate therefore admits only when `C > 0.010818 > predecessor_ceiling`,
i.e. only when Q99 already won the `max`. No admissible r7 corpus exists on which
`max(predecessor, Q99) ≠ Q99`. The emitted number is correct today under either
form.

Why it still matters: `max(predecessor, Q99)` is the cold-gate-69 **ratchet** —
"the successor ceiling … can never fall" — and the ratchet is exactly the clause
that becomes load-bearing at r8, when the predecessor ceiling (r7's, ≈ 0.0144)
will be well ABOVE the floor and can win. The seat's own prose (`:1029-1031`)
states the ratchet; the code carries a term for it that nothing verifies. The
cheap cure is a unit-level test on the arithmetic (not the CLI): feed the ceiling
computation a synthetic predecessor ceiling above the corpus Q99 and assert the
predecessor value is returned. That is a bench-sized fix, smaller than a
delegation contract.

Status against the seat's disclosure: the seat listed this as open item 3
("the envelope's predecessor arm remains inert"). This audit confirms the
inertness by execution and pins its severity: **should_fix, not blocker, and not
a defect in any number the D-138 transaction will consume.**

---

## 3. B3 — the proof record, its sealing, and the code the two routes share

**The proof is inside the sealed input set.** `derivation_input_sha256`
(`:1147-1185`) lists `"quantile_proof": derivation["quantile_proof"]` explicitly;
`derivation_sha256` is the production recipe over the whole artifact minus itself,
so the proof is inside that digest too. Both directions verified by cut (D2/D2b
and the seat's F7-class test `test_the_input_seal_covers_every_derivation_input`,
which the suite runs green).

**What the two routes share — read from the code, precisely.**

- The **quantile route** (`student_t_quantile` → `student_t_survival` →
  `regularized_incomplete_beta` → `_beta_continued_fraction`, `_half_integer_beta`,
  `_half_integer_gamma`) takes π from the **transcribed `_PI` constant** (`:186`),
  and only through `_half_integer_beta`'s `sqrt(pi)` powers.
- The **proof route** (`student_t_quantile_closed_form` →
  `student_t_absolute_cdf_closed_form` → `_decimal_arctan`, `_machin_pi`) takes π
  from **`_machin_pi()`, computed** by Machin's formula from Euler-series arctans.
- **Nothing is shared but the Decimal machinery**: `Decimal`, `localcontext`,
  `DECIMAL_WORK_PRECISION = 80`, and the *shape* of a 300-step bisection on
  `[0, 100]` — separately written in each function, no common helper. No
  incomplete-beta code, no continued fraction, and no π constant crosses over.
- A parity detail worth recording: for **even** df the quantile route's
  `sqrt(pi)` powers cancel to zero (`_half_integer_gamma` returns power 0/1 such
  that `power_a + power_b − power_ab == 0`), and A&S 26.7.4 uses no
  transcendental at all — so on even df **neither** route reads any π. The
  π-cross-check therefore has force only on odd df (which df 19 and df 21, the
  realized and the proof-fixture cases, both are).

**π-corruption counterfactual, executed** (`/tmp/s4delta/pi2.py`, wide fixture,
df 19, odd):

```
--- _PI corrupted at significant digit 12 (inside prec 80) ---
rc 3
REFUSED: quantile_proof_failed: df 19 p 0.975 closed-form agreement 13 digits is below 30
out written: False

--- _PI corrupted at significant digit ~82 and ~101 (BEYOND prec 80) ---
rc 0   (candidate emitted)
```

The seat's claim — "a mistyped digit in `_PI` shows up as a proof failure rather
than as a wrong number" — **holds**, with the exact and correct qualification
that `_PI` carries 101 significant digits while the working context is 80, so
digits past the 80th are never read by anything and their corruption is a no-op
rather than an escaped defect. (nit N-b below.)

**df-21 proof record** (`test_realized_df_carries_a_two_route_quantile_proof`'s
22-slot fixture, run through the CLI; df 21 is pinned by no other test):

```json
{
  "degrees_of_freedom": 21,
  "probabilities": ["0.975", "0.995"],
  "quantiles": {"0.975": "2.07961384472768039512",
                "0.995": "2.83135955802305001688"},
  "forward_residuals": {"0.975": "1.800E-80", "0.995": "2.500E-81"},
  "forward_residual_bound": "1E-30",
  "closed_form_agreement_digits": {"0.975": 56, "0.995": 56},
  "closed_form_agreement_bound": 30,
  "closed_form_method": "Abramowitz & Stegun 26.7.3 (odd df) / 26.7.4 (even df) finite closed form, inverted by bisection; pi by Machin's formula",
  "precision": 80
}
```

Realized margins: forward residual ~1e-80 against a 1e-30 bound; agreement 56
digits against a 30-digit bound. The pre-registration clause
(`~:131-134`, "no corpus issues on a df whose quantile is not proven in that
record") is now implemented, computed for the REALIZED df, recorded, and sealed.
B3 closed.

---

## 4. Ruled refusals — still refusing (through the CLI)

`PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/cli.py`. Every refusal returns
rc 3, prints its reason, and writes nothing.

| # | counterfactual | rc | printed reason |
|---|---|---|---|
| R1 | omit `--d125-ruling` | 3 | `d125_ruling reference absent; refusing to emit (ruling 46 V7)` |
| R2 | n = 18 without `--ed-ruling` | 3 | `retained corpus n = 18 is below the required floor 19; not issued` |
| R3 | screen challenge (2 members over the prior level screen) | 3 | `screen challenge: 2 retained members exceed 0.032898493715362; not issued, Ed rules in writing` |
| R4 | S ≥ C (tight corpus) | 3 | `successor_screen_exceeds_budget_ceiling: screen 0.010818 is not strictly below the budget ceiling 0.010164834757777545; not issued, Ed rules in writing` |
| R5 | omit `--out` | 2 | argparse `the following arguments are required: --out` |
| — | ADMIT (wide, n = 20) | 0 | `corpus n: 20`, `screen_rule: floored_range_envelope_screen`, no `SEAM:` line |

R4's reason still quotes the predecessor ceiling because the tight corpus's own
Q99 is below it — the one place the predecessor arm is visible, and it is on a
refusal path, which is why DF-1 is inert rather than dangerous.

---

## 5. Suite and key-set diff

```
$ cd /Users/edr/code/JouleWise-wt-s4-issuer-prepare && PYTHONDONTWRITEBYTECODE=1 \
    python3 -m unittest tests.test_issue_calibration_acceptance_generation \
                        tests.test_calibration_bracketing
Ran 156 tests in 54.312s
OK (skipped=1)
rc 0
```

(One informational line precedes it: `custody_locator_unreachable reason=timeout
locator=/private/var/folders/…/tmp… budget_s=0.05` — an expected probe timeout in
a temp-dir fixture, not a failure.) Nothing the fix round touched is broken.

**Key-set diff, emitted candidate vs r6's issued artifact** (recursive over
object keys).

Top level, only in the candidate — all three expected:
`candidate_not_issued`, `derivation_input_sha256`, `registered_generation_row`.
Top level, only in r6: **none**.

Nested, only in the candidate — every one accounted for:
`decimal_derivation.quantile_proof.*` (B3, new and sealed),
`derivation_input_sha256` (SF3), `registered_generation_row.*` (the S3 row),
`derivation_notes.rule_outcomes.*` and `derivation_notes.preregistration.*`
(the ruled sequence's own record), `derivation_notes.excluded_members`,
`derivation_notes.prior_screen_comparison`,
`decimal_derivation.rounding.operative_bracket_screen.{floor_bound,floor_s}`
(D-125 floor), `prior_observation_set.epoch_catalog.d079_epoch_25g83.*`
(the target epoch). **No unexplained additions.**

Nested, only in r6 — the substantive ones are prose/provenance blocks the
candidate does not yet carry: `derivation_notes.method_identity.*`,
`derivation_notes.derivation_method.*`, `derivation_notes.exclusion_accounting.*`,
`derivation_notes.residual_margin_distribution.*`,
`derivation_notes.network_time_provenance.*`,
`derivation_notes.methodology_review_adjudication.*`,
`derivation_notes.reissue_delta.*`, `derivation_notes.permanently_refusing_records`,
`decimal_derivation.presentation_values.*`,
`decimal_derivation.two_draw_prediction_derivation.predecessor_note`,
`backfill_candidate.superseded_id_only_blind_exclusions`,
`derivation_notes.predecessor.{file_sha256,derivation_sha256}`.

None of these is validator-required — the B1 authentication test proves the
candidate authenticates without them. They are a **scientific-record gap against
the predecessor**, not a code defect, and they belong to the D-138 transaction
brief (see §7 nit N-c).

Digests (wide n = 20 fixture; the absolute paths inside make them fixture-local,
not repo-stable):

```
scripts/issue_calibration_acceptance_generation.py
  da8deb1189fbd88bcf03697251952017ab9372f3709f3f9ed3677e0784be8aa8  (before and after every cut)
tests/test_issue_calibration_acceptance_generation.py
  80a5838e975a6bf60be2a314d991686bee1d9363a73c2cea178d3d900a35aa4c
tests/fixtures/epoch_bootstrap/build.py
  8ad586d78afc9c506fa394640f8ae354126cc2197d13f344557b82874555a195
emitted candidate derivation_sha256        2d3fe646e474b44a7494cb3528214a6aea98bf31cdad7e6366db91c77ff51ec5
emitted candidate derivation_input_sha256  78db0bd62855dd3ebbbac056332e748c2c1c25dac6bc7acdacab17f2ee3c9f01
```

---

## 6. The seat's three open items — severity for the D-138 transaction

1. **Absolute `source_directory`** — CONFIRMED by execution; the emitted member
   carries e.g.
   `/var/folders/p3/…/T/tmp6fgpsekr/wide/runs/instrument_validation/derivation-night-1-d01`.
   **should_fix, and it must be fixed BEFORE the transaction, not after**: r6
   stores a repo-relative locator, and committing a machine-local absolute path
   into `configs/calibration/` would make the issued artifact unreproducible on
   any other checkout while the validator (which only type-checks the field)
   would never say so. It is a one-line `Path.relative_to(REPO_ROOT)` at the
   emission site with a refusal if the member lies outside the repo — bench-sized.
   Not a blocker for the CANDIDATE (a desk artifact), a blocker for the ISSUED
   one.

2. **Member sort untested** — **CLOSED, not open.** Cut D22 (sort reversed) is
   killed by `test_only_the_candidate_label_stops_the_candidate_authenticating`,
   because the production validator's `member_ids == sorted(member_ids)` clause
   runs inside that test. The seat under-claimed its own coverage; no action.

3. **Inert predecessor arm** — the audit's single finding, DF-1 above.
   **should_fix**, zero risk to the r7 numbers, real risk deferred to r8. Fix by
   a unit test on the ceiling arithmetic with a synthetic predecessor ceiling
   above Q99; do not build a CLI fixture for it (no admissible one exists).

---

## 7. Nits

- **N-a — `TWO_DRAW_PREDICTION_RULE` and its function docstring disagree.** The
  constant (`:198-201`) now correctly reads "recorded as its shortest
  round-tripping decimal" (r6's wording, digest-bearing, asserted by test), but
  `two_draw_prediction_lexeme`'s docstring (`:508`) still says "recorded as its
  shortest **repr**". Cosmetic — the docstring is not sealed — but it is the
  exact wording the prior round flagged, left behind in one place.
- **N-b — `_PI` carries 101 significant digits against a working precision of
  80.** Digits 81+ are unreachable: corrupting them changes nothing (executed,
  §3). Harmless, but the constant advertises a precision the code cannot use;
  either trim it to 80 or note the margin.
- **N-c — the candidate does not restate the predecessor's digests.**
  `derivation_notes.predecessor` carries `acceptance_id`, `relative_path` and
  `maximum_budgetable_drift_s`; r6's equivalent block also carries
  `file_sha256` and `derivation_sha256`. Custody is nonetheless enforced at read
  time — `_authenticated_predecessor` (`:639-651`) goes through the production
  exact-byte loader, which pins the registry digest, and the sealed set covers
  `predecessor_acceptance_id` — so this is a record-completeness nit, not a
  custody hole.

---

## 8. Reproducing commands

```bash
cd /Users/edr/code/JouleWise-wt-s4-issuer-prepare
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_issue_calibration_acceptance_generation tests.test_calibration_bracketing

# cut batches (each restores the source and asserts the sha256 in a finally)
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/cuts.py /tmp/s4delta/cuts1.json   # D1..D5
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/cuts.py /tmp/s4delta/cuts2.json   # D6..D22
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/pi_and_extra.py                   # D14b..D14d
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/pi2.py                            # _PI corruptions
PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4delta/cli.py                            # R1..R5, proof, key-set diff
```
