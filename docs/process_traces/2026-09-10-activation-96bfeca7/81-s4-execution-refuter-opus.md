# 81 — Seat S4 EXECUTION-LENS refuter (Opus)

Worktree `/Users/edr/code/JouleWise-wt-s4-issuer-prepare`, branch
`feat/2026-09-10-epoch-s4-issuer-prepare-candidate`, HEAD `f31884d7`, base `0fe1fc5e`.
Read-only except two temporary source cuts, both restored byte-for-byte
(`sha256 a5c980ecca3d90447631ab5894252c26774adb4e1a83c819e447e8633fbe7a1f` before
and after every cut). `PYTHONDONTWRITEBYTECODE=1` on every subprocess. No git
state changed, no `[QUIET-MAC]` measurement, `configs/calibration/` never written.
Harnesses live under `/tmp/s4ref/` (`indep_t.py`, `attack.py`, `attack1..5.py`,
`cuts.py`); fixtures under `$TMPDIR/s4atk*`.

## VERDICT: **BLOCKED**

Two blockers, both executed. The statistics are **flawless** — every claim-bearing
lexeme reproduces r6 exactly and the general-df quantile is independently correct
to 40 places, which is the part of this seat I most expected to break and could
not. What is broken is the ARTIFACT SHAPE: the emitted candidate can never pass
the production exact-byte validator, because its `prospective_rederivation.triggers`
are the predecessor's verbatim and carry the predecessor's corpus-doubling trigger.

---

## 1. STATISTICS FIDELITY — no defect found

Reproduced the whole r6 derivation through S4's own functions from r6's member
table (`/tmp/s4ref` inline script; 17 members, df 16). Every lexeme identical.

| lexeme | S4 recomputed | r6 recorded | |
|---|---|---|---|
| `minimum_s` | 0.02317490442656863 | 0.02317490442656863 | OK |
| `minimum_member_id` | 20260722T215127-eeef661a | same | OK |
| `maximum_s` | 0.03289849371536248 | 0.03289849371536248 | OK |
| `maximum_member_id` | 20260722T214220-1acdbbc0 | same | OK |
| `range_s` | 0.00972358928879385 | 0.00972358928879385 | OK |
| `mean_presentation_s.value` | 0.026848579671140323 | 0.026848579671140323 | OK |
| `mean_presentation_s.label` / `.rounding_rule` | rounded_presentation / ROUND_HALF_EVEN to quantum 1e-18 s | same | OK |
| `sample_sd_presentation_s.value` | 0.002460856207694636 | 0.002460856207694636 | OK |
| `sample_sd_presentation_s.label` / `.rounding_rule` | rounded_presentation / ROUND_HALF_EVEN to quantum 1e-18 s | same | OK |
| `t_975_quantile` (20 pl.) | 2.11990529922125467446 | 2.11990529922125467446 | OK |
| `t_995_quantile` (20 pl.) | 2.92078162242509999197 | 2.92078162242509999197 | OK |
| `prediction_95_two_draw_s` | 0.007377644019421586 | 0.007377644019421586 | OK |
| `prediction_99_two_draw_s` | 0.010164834757777545 | 0.010164834757777545 | OK |
| bracket screen (range arm, 1e-6 HALF_EVEN) | 0.009724 | 0.009724 | OK |
| `preflight_level_screen_s` (1e-15 HALF_EVEN) | 0.032898493715362 | 0.032898493715362 | OK |

**Independent quantile check.** scipy and mpmath are both absent on this machine,
so I built a reference by a deliberately DIFFERENT route (`/tmp/s4ref/indep_t.py`):
the exact finite Abramowitz & Stegun 26.7.3/26.7.4 closed forms, parametrised by
`theta` so the bisection runs on `theta in (0, pi/2)` and no `arctan` is ever
needed; `sin`/`cos` by Decimal Taylor series; `pi` by Machin's formula. It shares
no code path with S4's Lentz continued fraction. Reference accuracy ~40 places.

| df | p | S4 (80-digit context) | independent reference | abs diff |
|---|---|---|---|---|
| 16 | 0.975 | 2.119905299221254674455701449766333420202871 | 2.119905299221254674455701449766333420203 | 1.29E-40 |
| 16 | 0.995 | 2.920781622425099991967283211370732567766696 | 2.920781622425099991967283211370732567766 | 6.97E-40 |
| 18 | 0.975 | 2.100922040241038488060871643730117477540439 | 2.100922040241038488060871643730117477540 | 4.40E-40 |
| 18 | 0.995 | 2.878440472738608117805878726564631607903032 | 2.878440472738608117805878726564631607903 | 3.24E-41 |
| 19 | 0.975 | 2.093024054408309769177315282189993480410920 | 2.093024054408309769177315282189993480411 | 7.94E-41 |
| 19 | 0.995 | 2.860934606464979192084820735250293994868784 | 2.860934606464979192084820735250293994868 | 7.85E-40 |

Every difference is at MY reference's own precision limit, i.e. agreement to
~40 significant places — four times the ≥10 places asked. Third-party
corroboration: r6's own `predecessor_note` records the exact t(0.995,18) as
`2.87844047273860811780`; both implementations reproduce it independently.

Repro: `cd /Users/edr/code/JouleWise-wt-s4-issuer-prepare && PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4ref/indep_t.py`

---

## 2. FINDINGS

### BLOCKER B1 — the emitted candidate can NEVER authenticate: `prospective_rederivation.triggers` are the predecessor's

`scripts/issue_calibration_acceptance_generation.py:794` copies the predecessor's
triggers verbatim:

```python
"triggers": list(predecessor["prospective_rederivation"]["triggers"]),
```

r6's list contains `corpus_doubles_from_17_to_34` (r6's n is 17). The emitted row
at `:679` correctly says `corpus_doubling_trigger: corpus_doubles_from_20_to_40`
for a 20-member corpus. The production exact-byte validator
`joulewise/calibration_bracketing.py:753-760` demands SET EQUALITY against the
registered generation's own trigger:

```python
or set(prospective["triggers"]) != {
    "identity_field_change", "protocol_or_estimator_byte_change",
    "new_valid_same_identity_capture_expands_observed_range",
    generation["corpus_doubling_trigger"],
    "new_systematic_failure_challenges_preflight_screen",
}
```

and `generation` is `_D102_GENERATION_DERIVATIONS[acceptance_id]`
(`calibration_bracketing.py:701`) — i.e. exactly the row S3 will register FROM
S4's own emission. So the mismatch is structural, not a registry-state artefact:
whatever S3 registers, the artifact's triggers name the wrong corpus.

Observed (`python3 /tmp/s4ref/attack3.py`):

```
row corpus_n                : 20
row corpus_doubling_trigger : corpus_doubles_from_20_to_40
emitted triggers            : [... 'corpus_doubles_from_17_to_34' ...]
SET EQUAL (what the validator tests at :754): False
symmetric difference: ['corpus_doubles_from_17_to_34', 'corpus_doubles_from_20_to_40']
protocol_sha256 matches production: True
```

Expected: `triggers` must be rebuilt around the candidate's OWN
`corpus_doubling_trigger`, not copied. Everything else in the copied block
(`protocol_sha256`, the recomputed `estimator_code_sha256`) is right — this one
element is corpus-indexed and the copy does not re-index it. The artifact is also
self-contradictory as a scientific record: its row says the corpus doubles at 40,
its rederivation triggers say 34.

Reproducing command:
`cd /Users/edr/code/JouleWise-wt-s4-issuer-prepare && PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4ref/attack3.py`

Note this is invisible to S4's own suite: `_registered_generation_row_is_complete`
only inspects the ROW, and `test_emitted_candidate_is_refused_by_the_production_loader`
asserts the candidate is refused — which it is, for the `artifact_role` reason,
so the trigger defect is fully masked by the refusal the test wants.

### BLOCKER B2 — conditional screen-rule naming breaks under the ruled convention

`:594-597` names the rule by branch:

```python
screen_rule = (SCREEN_RULE_FLOORED_RANGE_ENVELOPE if floor_bound
               else SCREEN_RULE_RANGE_EQUALS_SCREEN)
```

Per the lead's design call (not re-litigated here) the name is
`floored_range_envelope_screen` for EVERY envelope generation regardless of which
arm of the `max` won, and S3 registers that one name. Executed today
(`/tmp/s4ref/attack2.py`):

```
wide  (n=20, range 0.0114 > floor)  -> screen_rule 'range_equals_screen',            _registered_generation_row_is_complete = True
floored (bimodal, range 0.0100)     -> screen_rule 'floored_range_envelope_screen',  _registered_generation_row_is_complete = False
wide row with screen_rule renamed to 'floored_range_envelope_screen' -> False
```

Under the convention the polarity inverts and three sites in S4 break:

1. `:594-597` — must emit `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` unconditionally.
2. `:757` — `"screen_rule_registered_in_validator": (screen_rule == SCREEN_RULE_RANGE_EQUALS_SCREEN)` hardcodes the inverse of the new truth; it will report `false` for a rule S3 has registered, and `prepare_candidate:526-530` will print the `SEAM:` warning on every successful run.
3. Two tests invert: `test_emitted_row_satisfies_the_registered_row_validator:930` (asserts True for a `range_equals_screen` row S3 will no longer admit) and `test_floor_bound_screen_names_an_unregistered_rule:952` (asserts `assertFalse(_registered_generation_row_is_complete(row))`, which becomes False-positive once S3 registers the name).

Also material for the real corpus: **the pre-registered n=19 floor lands in the
floored branch**. A 19-member grid at 0.0006 spacing has range 0.0108 < 0.010818,
so the minimum admissible corpus takes the floor arm — the branch is the norm,
not the exotic case the seat's `wide` happy-path fixture exercises.

```
E1 n exactly 19  -> rc 0, screen_rule: floored_range_envelope_screen, SEAM printed
E2 n exactly 20  -> rc 0, screen_rule: range_equals_screen
```

### BLOCKER B3 — the pre-registered "no corpus issues on an unproven df" gate is not implemented

`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:~131-134`:

> "…the degrees of freedom n-1 run from 18 to 35 … the quantile implementation's
> proof for the REALIZED df is computed and recorded before issuance, and **no
> corpus issues on a df whose quantile is not proven in that record**."

S4 proves df 16, 18 and 19 in tests. The realized df may be anything in 18–35.
There is no gate and no proof record in the payload. Executed
(`/tmp/s4ref/attack4.py`, 22-slot fixture):

```
rc 0  n 22  df 21
t_975: 2.07961384472768039512
payload keys mentioning proof: []
```

Observed: a df-21 corpus emits a clean candidate. Expected: refuse (or record a
computed proof for the realized df) whenever the realized df is outside the
proven set. This is a ruled clause with no code, in the same family as the "ruled
but not installed" pattern.

### should_fix S1 — the custody-hash clause is load-bearing AND unkilled by the suite

The seat self-flagged this (`_read_member_evidence:344-352`, "no counterfactual
test"). I verified both halves.

**It fires.** Building the wide fixture, mutating one member bundle after
finalization, re-committing, and running the CLI (`/tmp/s4ref/attack2.py`):

```
manifest.json byte change  -> rc 3, out not written
  REFUSED: member derivation-night-1-d06: manifest.json does not match the ledger row
instrument_evidence.json value change -> rc 3
  REFUSED: member derivation-night-1-d06: instrument_evidence.json does not match the ledger row
restore -> rc 0
```

**Nothing kills it.** Cut `:345` `for name in ("manifest.json", "instrument_evidence.json"):`
→ `for name in ():` and the seat's nearest test passes:

```
X1 custody-hash clause :345  test=test_primary_value_disagreeing_with_the_ledger_row_refuses
   Ran 1 test in 8.063s | OK -> *** SURVIVED ***
```

(The seat's C10 cut a different term — the `b_fiducial_s` comparison at `:463` —
which that test does kill. The custody loop itself is unguarded.)

**And the hole is real, not cosmetic.** With the loop cut, the tampered-manifest
counterfactual runs straight through (`/tmp/s4ref/attack5.py`):

```
TAMPERED-MANIFEST run: rc 0 | out written: True
candidate written (NOT ISSUED): .../c.json
restored sha256: a5c980... == baseline: True
```

A post-finalization manifest edit is caught by NO other clause. The counterfactual
above is the missing test, verbatim — mutate a bundle after `build_derivation_ledger`
returns, re-commit, assert `REFUSED: … manifest.json does not match the ledger row`.

### should_fix S2 — addendum A-7's "valid same-epoch row outside the registration REFUSES" is not implemented (code-read, not executed)

A-7: "The completeness check ranges over prior-set rows that are valid, carry the
target epoch, AND belong to a session of this registration; **a valid same-epoch
row outside the registration refuses issuance rather than being absorbed.**"

`_registration_observations:405-428` filters `snapshot.observations` down to the
registration's sessions and `_select_members:430` never sees the rest. A valid,
target-epoch row belonging to a session outside `--registration-session-id` is
therefore silently ignored — it lands in `prior_observation_set.observations`
(which takes every row) but triggers no refusal. I did not build the two-session
fixture within the time box, so this is a code reading, not an execution; it needs
either an implementation or an explicit ruling that the refusal is S3's, not S4's.

### should_fix S3 — `derivation_sha256` omits load-bearing derivation inputs

`derivation_sha256:828-851` seals member lexemes, `source_statistics`, `rounding`,
`two_draw_prediction_derivation`, `ratified_operatives`, `screen_rule`,
`predecessor_ceiling_s`, `d125_ruling`. The docstring says prose, paths and the
candidate label are "deliberately OUT" — true and right. But so are four things
that are neither prose nor path. Executed (`/tmp/s4ref/attack2.py`):

```
digest moves on range_s edit:                                  True
digest moves on rounding-rule edit:                            True
digest moves on member lexeme edit:                            True
digest UNCHANGED when candidate label flipped to issued:       True   (intended)
digest UNCHANGED when ledger_cutoff head_digest rewritten:     True   <-- 
digest UNCHANGED when prior observation set emptied:           True   <-- 
digest UNCHANGED when identity_epoch rewritten:                True   <-- 
```

`predecessor_acceptance_id` is also outside the seal (only the ceiling VALUE is
in). Two preparations from different identity epochs, different ledger cutoffs,
or different predecessors digest identically. Expected: `identity_epoch`, the
cutoff `head_digest`/`sequence`, and `predecessor_acceptance_id` belong in the
sealed set — they are inputs the derivation depends on, and the whole point of the
digest is that a replay from different inputs cannot present as the same derivation.
Determinism is otherwise clean: two runs on the same fixture produce a
byte-identical payload (`rerun digest equal: True | full payload equal: True`).

### nit N1 — `student_t_quantile` accuracy silently follows the ambient Decimal context

`:293-311` sets no context of its own. Production always wraps it at prec 80
(`:581-584`), but the tests call it bare at the default prec 28 and assert 20
places, and any other caller gets silent degradation rather than a refusal:

```
prec  15 -> 2.86093460646498
prec  20 -> 2.8609346064649791920
prec  28 -> 2.860934606464979192084820734   (last digit wrong; true ...73525)
prec  80 -> 2.8609346064649791920848207352502939948687849675217747263134860074706012553049536
```

No context leakage: ambient prec/rounding unchanged across a call. Suggest a
`localcontext` inside the function, or an explicit precision argument.

### nit N2 — the default `acceptance_id` hardcodes the epoch

`:774`: `f"d079_calibration_acceptance_v2_n{n}_25g83_r1"` — the corpus size is
interpolated but `25g83` is a literal, so a run under any other epoch mislabels
itself. The epoch is available as `identity_epoch["os_build"]`.

### nit N3 — the two-draw rule STRING differs from r6's, inside the sealed set

`TWO_DRAW_PREDICTION_RULE:194` ends "…recorded as its shortest **repr**"; r6's
recorded rule ends "…recorded as its shortest **round-tripping decimal**". Same
mechanism, different words — but the string sits inside
`two_draw_prediction_derivation`, which `derivation_sha256` seals, so the wording
is digest-bearing. Match r6's wording.

---

## 3. Ruled-sequence counterfactuals (all through the CLI on synthetic fixtures)

`PYTHONDONTWRITEBYTECODE=1 python3 /tmp/s4ref/attack1.py` and `attack3.py`.
Every refusal returns rc 3, prints its reason, and writes nothing.

| # | counterfactual | rc | printed reason | `--out` written |
|---|---|---|---|---|
| R1 | omit `--d125-ruling` | 3 | `d125_ruling reference absent; refusing to emit (ruling 46 V7)` | no |
| R2 | n=18 corpus, no `--ed-ruling` | 3 | `retained corpus n = 18 is below the required floor 19; not issued` | no |
| R2b | `--minimum-corpus-size 17`, no `--ed-ruling` | 3 | `corpus-size floor departure to 17 requires --ed-ruling (D-126 cl.2 SUCCESSOR_MINIMUM_CORPUS_SIZE = 19)` | no |
| R2c | `--minimum-corpus-size 20 --ed-ruling x` | 3 | `--minimum-corpus-size may not exceed the ratified floor` | no |
| R3 | head pin from a foreign tree | 3 | `ledger: calibration_ledger_head_mismatch, calibration_ledger_head_uncommitted` | no |
| R4 | tight corpus (Q99 below the floor) | 3 | `successor_screen_exceeds_budget_ceiling: screen 0.010818 is not strictly below the budget ceiling 0.010164834757777545; not issued, Ed rules in writing` | no |
| R5 | two members above 0.032898493715362 | 3 | `screen challenge: 2 retained members exceed 0.032898493715362; not issued, Ed rules in writing` | no |
| R6 | omit `--out` | 2 | argparse `the following arguments are required: --out` | no |
| R7 | no `--registration-session-id` | 3 | `registration: no --registration-session-id given` | no |
| R8 | unknown session id | 3 | `registration: session no-such-session is not in the ledger` | no |
| R9 | predecessor not an issued acceptance | 3 | `predecessor: …/notissued.json is not an authenticated issued acceptance` | no |
| R10 | unreadable `--preregistration` | 3 | `pre-registration unreadable: [Errno 2] …` | no |
| R11 | `--epoch-catalog-id d079_epoch` (predecessor's key) | 3 | `epoch catalog: the target id collides with the predecessor's` | no |
| M1 | bracket-kind session as registration | 3 | `registration: session derivation-night-1 is kind 'bracket', not a derivation session` | no |
| M2 | bundle manifest tampered post-finalization | 3 | `member …-d06: manifest.json does not match the ledger row` | no |
| M3 | bundle evidence tampered post-finalization | 3 | `member …-d06: instrument_evidence.json does not match the ledger row` | no |
| M4 | every row `ordinary-invalid` | 3 | `retained corpus n = 0 is below the required floor 19; not issued` | no |

Admits, for contrast: 19 valid + 1 `ordinary-invalid` + 1 `affine_clock_fit_empty`
→ rc 0, `corpus n: 19`, the excluded row named under
`derivation_notes.excluded_members`, the invalid rows simply not members.
`ledger_cutoff` is the authenticated physical head (`sequence 82` for a 20-slot
fixture, i.e. after the last bootstrap row), the epoch catalog has exactly the two
entries (`d079_epoch` = r6's, `d079_epoch_25g83` = target), and
`prior_observation_count == len(observations) == 20`.

**Ceiling relation (packet 69).** Verified on the wide fixture:
`predecessor_ceiling 0.010164834757777545`, own `Q99 0.014361777742543469`,
emitted `maximum_budgetable_drift_s 0.014361777742543469`;
`ceiling == max(predecessor, Q99)` **True**; `screen + excess == ceiling` **True**;
strict `screen < ceiling` enforced (R4 above). No defect.

## 4. Cut table (mine, independent of the seat's eleven)

Harness `/tmp/s4ref/cuts.py`. One term per cut, one named test, source restored
and sha256-asserted after each.

Baseline / restored `sha256(scripts/issue_calibration_acceptance_generation.py)` =
`a5c980ecca3d90447631ab5894252c26774adb4e1a83c819e447e8633fbe7a1f` (identical
before and after all cuts, verified per-cut in a `finally`).

| cut | term | test | runner | result |
|---|---|---|---|---|
| X1 | `:345` `for name in ("manifest.json", "instrument_evidence.json"):` → `for name in ():` | `test_primary_value_disagreeing_with_the_ledger_row_refuses` | `Ran 1 test in 8.063s` `OK` | **SURVIVED** (finding S1) |
| X2 | `:603` `if not screen < ceiling:` → `if False:` | `test_screen_at_or_above_the_ceiling_refuses` | `Ran 1 test in 7.187s` `FAILED (failures=1)` | KILLED |
| X3 | `:567` `if n < minimum:` → `if False:` | `test_seventeen_member_corpus_refuses_without_the_ed_ruling` | `Ran 1 test in 7.138s` `FAILED (failures=1)` | KILLED |
| X4 | `:592` `screen = max(quantized_range, D125_SCREEN_FLOOR_S)` → `screen = quantized_range` | `test_floor_bound_screen_names_an_unregistered_rule` | `Ran 1 test in 7.194s` `FAILED (failures=1)` | KILLED |
| X5 | `:305` `target = Decimal(1) - Decimal(probability)` → `target = Decimal(probability)` | `test_quantiles_reproduce_known_values_for_even_and_odd_df` | `Ran 1 test in 6.899s` `FAILED (failures=6)` | KILLED |

Suite as landed, unmutated:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation`
→ `Ran 54 tests in 42.972s` `OK` (rc 0). The seat's own 11-cut table is
consistent with what I re-ran; my X1 finds the gap the seat itself named.

## 5. Hashes

```
scripts/issue_calibration_acceptance_generation.py
  a5c980ecca3d90447631ab5894252c26774adb4e1a83c819e447e8633fbe7a1f  (before and after every cut)
emitted candidate (wide n=20 fixture) derivation_sha256
  676285785747374f07c0059cef7d943f98fa6f6ed3b2173ba7028acc7a897623  (stable across reruns)
```

## 6. What I could NOT break

- The Decimal statistics and both two-draw predictions: byte-exact against r6.
- The general-df Student-t quantile: independently correct to ~40 places on df 16, 18, 19 (and the values S4's tests pin are correctly rounded, including the df-18 `…811781` half-even case).
- The D-125 envelope arithmetic: `C = max(predecessor, Q99)`, strict `S < C`, `S + excess == C`, no clamp.
- Fail-closed refusal transport: seventeen counterfactuals, every one rc 3 with a distinct printed reason and no file written.
- Issuance safety: `candidate_not_issued: true`, `artifact_role: "candidate"`, `load_calibration_acceptance_bound` returns `None`, `--out` argparse-required with no default so `configs/calibration/` can never be a default destination.
- Determinism: two runs on one fixture give a byte-identical payload.
