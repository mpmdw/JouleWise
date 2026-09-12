# 162 — Counter-review (Opus, fresh non-author), gate row 6

Checkout: `/Users/edr/code/JouleWise-wt-eq-ruling` at `08ccdb4a`
(branch `feat/2026-09-10-equivalence-ruling-316`), read-only. Base `bc1d7ef9`.
Authority read: directive issue 316 (`gh issue view 316`). Prior reports 157/158/160
and trace 161 read for context only; findings below are independently derived.

**Verdict: MERGE-ABLE with three should-fix items and two nits. No blocker.**
Every number, comparator, exit code and verdict branch in the diff is correct and
agrees across the four units. The should-fix items are a false attribution in the
tool's own prose, an operator instruction that cannot succeed as written, and a
§2.5 invocation block that departs from its section's conventions.

---

## Executed evidence (this session, this checkout)

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_equivalence_check 2>&1 | tail -3
Ran 25 tests in 33.117s

OK

$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_policy_resolver_guard tests.test_docs_freshness tests.test_custody_mode_inventory 2>&1 | tail -3
Ran 39 tests in 94.530s

OK

$ PYTHONDONTWRITEBYTECODE=1 python3 scripts/epoch_equivalence_check.py --print-envelope-only; echo rc=$?
Reference envelope (the acceptance in force; issue 316)
  acceptance_id: d079_calibration_acceptance_v2_n17_r6
  artifact: /Users/edr/code/JouleWise-wt-eq-ruling/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json
    loaded by joulewise.calibration_bracketing.load_calibration_acceptance_bound
  corpus n = 17 (artifact derivation_corpus.n; registry corpus_n; they agree)
  raw corpus maximum_s = 0.03289849371536248  [artifact decimal_derivation.source_statistics]
  raw corpus range_s   = 0.00972358928879385  [artifact decimal_derivation.source_statistics]
  OPERATIVE level screen   preflight_level_screen_s   = 0.032898493715362  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  OPERATIVE bracket screen bracket_screen_s           = 0.009724  [validator registry _D102_GENERATION_DERIVATIONS operatives]
  budget ceiling           maximum_budgetable_drift_s = 0.010164834757777545  [validator registry _D102_GENERATION_DERIVATIONS operatives]
    artifact decimal_derivation.ratified_operatives agrees with the registry on all three, or this tool refuses
    NOTE: the operative comparators differ from the raw statistics (quantization / never-zero floor); issue 316 rules the OPERATIVE value is the one compared against.
rc=0
```

---

## Findings

### SHOULD-FIX 1 — the tool's prose asserts the never-zero floor is what quantized the bracket screen; all three documents say the opposite, deliberately

`scripts/epoch_equivalence_check.py:47-50` (module docstring):

> "The OPERATIVES are the numbers the validator actually measures with, and they
> are not always the raw statistics: **the bracket screen is quantized upward from
> the raw range under the never-zero floor rule**, and the level screen is
> quantized from the raw maximum."

`scripts/epoch_equivalence_check.py:313-316` (printed, on every real run and on
`--print-envelope-only`):

> `NOTE: the operative comparators differ from the raw statistics (quantization / never-zero floor); …`

Against the three documents in the same diff, each of which spends a numbered
paragraph refuting exactly this reading:

- `docs/phase_2/derivation_night_runbook.md:1655-1663` — "**No floor is in force here.**
  The never-zero floor issue 316 parenthesises — `0.010818` s, `D125_SCREEN_FLOOR_S` —
  belongs to the screen rule `floored_range_envelope_screen` … The acceptance in force
  registers the other rule, `range_equals_screen` … The gap between the operative
  bracket screen and the raw range here is **quantization alone**."
- `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:411-420` — same fact,
  same wording ("quantization alone, not a floor").
- `docs/decision_log.md:6740-6745` — "Here the difference is quantization, not a floor:
  this generation registers `range_equals_screen` (no floor)."

Confirmed against the contract: `docs/contracts/calibration_ledger.md:268-276` defines
`range_equals_screen` as "the bracket screen IS the corpus range quantized to 0.000001 s
under ROUND_HALF_EVEN", and `floored_range_envelope_screen` as the D-125 floor rule; the
registered row for r6 is the former. Arithmetically: `0.00972358928879385` → 6 decimals
ROUND_HALF_EVEN → `0.009724`. Pure quantization; the `0.010818` floor never enters.

Why this is not cosmetic: the printed NOTE is the text the magistrate will quote into
the D-102 continuation addendum's record of "the validator's own code path", and the
docstring is the tool's own account of its rule. A reader of the record would conclude a
floor widened the comparator — the single misattribution the three docs were written to
prevent. It is also a first-use-test failure under the writing standard: "never-zero
floor rule" is invoked as if it were the operative rule, without ever being built here.

Fix (docs-only, no behaviour): docstring → "the bracket screen is the raw range quantized
upward to 0.000001 s under ROUND_HALF_EVEN (the registered rule `range_equals_screen`; no
floor is in force for this generation)"; NOTE → "(quantization; this generation registers
`range_equals_screen`, no floor)".

### SHOULD-FIX 2 — "compare the two records byte for byte" cannot succeed: the record embeds an absolute, checkout-specific path

`docs/phase_2/derivation_night_runbook.md:1721-1724`:

> "Run it twice — once from the clone, once from a second checkout at the same head —
> and compare the two records **byte for byte** before recording a verdict."

`scripts/epoch_equivalence_check.py:276` puts `"acceptance_path": str(acceptance_path)`
into the envelope dict, and `evaluate_session` copies that dict whole into the record
(`"reference_envelope": dict(envelope)`, line ~445). The value is absolute — as the
pasted run shows, `/Users/edr/code/JouleWise-wt-eq-ruling/configs/calibration/…`. Two
checkouts live at two paths by construction, so the two records differ in exactly this
field, always. The operator at 03:00 gets a non-empty diff at the moment a verdict is
being recorded and must adjudicate materiality by hand — precisely the state the
two-checkout ritual exists to avoid.

Fix, either side: runbook → "compare the two records field by field; the only field that
may differ is `reference_envelope.acceptance_path` (each checkout's own path), and the
two acceptance artifacts must have identical sha256"; or tool → record the path relative
to `--repo-root` (plus the artifact digest) and keep the absolute path in the printed
lines only. The second is the stronger witness and is a 3-line change; either closes it.

### SHOULD-FIX 3 — the §2.5 invocation block breaks the two conventions every other §2 block follows

`docs/phase_2/derivation_night_runbook.md:1710-1716`:

```
$PY scripts/epoch_equivalence_check.py \
  --session-id "$SESSION_ID" \
  --ledger "$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl" \
  --head-pin "$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json" \
  --repo-root "$MEASUREMENT_ROOT" \
  --out "$NIGHT_ROOT/epoch-equivalence-record.json"
```

1. **No `cd "$MEASUREMENT_ROOT"`.** Every other command block in this runbook opens with
   it (lines 375, 434, 664, 909, 1251, 1458, 1555, 1787, 1807). The script path here is
   relative, so the block only works if the previous block's `cd` is still in effect.
2. **The ledger and head-pin paths are re-spelled as literals** although §2.0 already
   exported `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN` (lines 1406-1407) and the sibling
   block at line 1557 uses `--ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN"`.
   §2.0's stated rationale is that these values are *recovered and verified*, not copied;
   re-spelling them creates a second place for the same path to drift.
3. Related, worth one sentence in the prose: `--acceptance` is not passed, and its default
   `DEFAULT_ACCEPTANCE_BOUND_PATH` resolves against **the checkout the script lives in**,
   not against `--repo-root`. Running the second copy from a different checkout therefore
   reads that checkout's acceptance artifact while reading `$MEASUREMENT_ROOT`'s ledger.
   This is *safe* — the artifact must authenticate through the production loader and its
   `acceptance_id` must equal `REQUIRED_ACCEPTANCE_ID` — but it is not stated, and it is
   the mechanism by which the two-checkout run is meaningful at all.

Fix: prepend `cd "$MEASUREMENT_ROOT"`, use `"$CALIBRATION_LEDGER"` / `"$LEDGER_HEAD_PIN"`,
and add the one-sentence note about `--acceptance`'s default.

### NIT 1 — the new custody-allowlist row pins the wrong line (568; the call is at 596)

`tests/fixtures/custody_read_replay_allowlist.json:+59-65` records
`"file": "scripts/epoch_equivalence_check.py", "function": "run", "ordinal": 1, "line": 568`.
The `load_calibration_ledger_snapshot(...)` call in `run` is at
`scripts/epoch_equivalence_check.py:596`; line 568 is a closing paren inside
`record_lines`. `tests/test_custody_mode_inventory.py:224-238` keys on
`(file, function, ordinal)` and validates `line` only as a positive int, so nothing
catches it — which is why the pre-existing rows have drifted too (I checked: several
point at neighbouring or unrelated lines). The row's *reason* is exact and its key is
correct; only the human-navigation field is stale, almost certainly from before fix
rounds 1/2/2b added lines. Update to 596, or (better, separately) make the inventory test
check that the pinned line is inside the call's AST span so the field stops rotting.

### NIT 2 — the identity-guard test aims at the real checkout's tracked acceptance directory

`tests/test_epoch_equivalence_check.py:436-448` builds
`target = checker.REPO_ROOT / "configs" / "calibration" / "record.json"` and patches
`FORBIDDEN_OUT_PARTS` away so only the `samefile` check can refuse. Today nothing is
written (the default ledger/session does not resolve, so the run refuses earlier anyway
if the guard ever regressed), and `assertFalse(target.exists())` asserts it. But the
failure mode of the thing under test is "writes into the tracked acceptance directory of
this checkout", and the test points it there. A `tmp` directory symlinked to a fake
acceptance dir, or an `ACCEPTANCE_DIR` patched to a temp path *plus* a same-shape
regression that the constant is not derived from the patched one, would test the same
property without aiming at tracked files. Judgment call; not worth a fix round by itself.

---

## Cross-unit consistency table

| Claim | Doc location | Code location | Consistent |
|---|---|---|---|
| Operative level screen `0.032898493715362` | runbook:1638 table; pre-reg:389; D-102 add. (decision_log:6732) | registry `_D102_N17_DERIVATION["operatives"]`, read at `epoch_equivalence_check.py:274` (`registered["preflight_level_screen_s"]`); printed value matches | y |
| Operative bracket screen `0.009724` | runbook:1639; pre-reg:390; decision_log:6732 | same registry row, `epoch_equivalence_check.py:275`; printed value matches | y |
| Budget ceiling `0.010164834757777545`, carried but not compared | runbook:1640 ("the check compares against the two screens only") | `epoch_equivalence_check.py:276` records it; `evaluate_session` compares only the two screens | y |
| Corpus n = 17, cross-checked artifact vs registry | runbook:1641; decision_log:6735 | `epoch_equivalence_check.py:257-266` refuses on disagreement | y |
| Artifact/registry disagreement on any of the three operatives ⇒ refusal | runbook:1702-1704 | `CROSSCHECKED_OPERATIVES` loop, lines 133-138 + 243-256 | y |
| m ≥ 6 required; m < 6 ⇒ INCONCLUSIVE, evaluated BEFORE the comparisons | issue 316 §2; pre-reg:430; runbook:1673-1680 | `MINIMUM_RETAINED_M = 6`, line 122; branch at `evaluate_session` (`if len(retained) < MINIMUM_RETAINED_M` → INCONCLUSIVE, returns before any Decimal work) | y |
| PASS = every retained value `<=` level screen AND spread `<=` bracket screen (both `<=`) | issue 316 §2; pre-reg:432-434; runbook:1668-1671 | `level_pass = maximum <= level_screen`; `bracket_pass = spread <= bracket_screen` (lines ~481-482) | y |
| Spread = max − min of retained values | issue 316; runbook:1626 | `spread = maximum - minimum`, Decimal on stored lexemes at `DECIMAL_WORK_PRECISION`, no float | y |
| Retained = ledger `valid` AND anchor-v3 replay resolved; `window_exhausted` / `slot_refused` are not captures | issue 316 §2; runbook:1606-1618 | `_slot_outcomes` (lines 340-390) via `_read_member_evidence` + `anchor_v3_replay_outcome`; non-finalized slots → `unused`/`no_row` | y |
| Ledger row lexeme must equal the bundle's own `b_fiducial_s`, else refuse | runbook:1615-1618, 1701-1702 | `PrepareRefusal` at lines 379-383 | y |
| Exit codes 0 PASS / 4 FAIL / 5 INCONCLUSIVE / 3 refusal-wrote-nothing | runbook:1718-1721 | `REFUSAL_EXIT=3, FAIL_EXIT=4, INCONCLUSIVE_EXIT=5` (lines 117-119); `VERDICT_EXITS`; `--help` epilog states the same four | y |
| Refuses non-terminal, non-derivation-kind, unauthenticated envelope | runbook:1719-1720 | `resolve_session` (kind + `TERMINAL_SESSION_STATES`) and `reference_envelope` (loader returns None → refusal) | y |
| Judges only against r6; any other generation refuses | runbook:1705-1706 | `REQUIRED_ACCEPTANCE_ID = ANCHOR_V3_R6_ACCEPTANCE_ID`, lines 143-147 + 214-219 | y |
| Ledger default path is under `runs/` | runbook:1712 (commit 08ccdb4a) | `DEFAULT_LEDGER_PATH = REPO_ROOT/"runs"/"calibration_observation_ledger.jsonl"` (`calibration_ledger.py:105`) | y |
| Head-pin path `configs/calibration/calibration_ledger_head.json` | runbook:1713 | `DEFAULT_HEAD_PIN_PATH` (`calibration_ledger.py:106-108`) | y |
| Writes one JSON record to `--out`, never under `configs/calibration/`, nothing else | runbook:1707-1709; docstring:68-73 | `_refuse_out_path` (case-folded parts + `samefile` identity), checked before any read; single `write_text` | y |
| Two-checkout records comparable byte for byte | runbook:1721-1724 | record embeds absolute `acceptance_path` (line 276) | **n — should-fix 2** |
| Bracket-screen/raw-range gap is quantization, no floor in force (`range_equals_screen`) | runbook:1655-1663; pre-reg:411-420; decision_log:6740-6745; contract `calibration_ledger.md:268-276` | docstring:47-50 and printed NOTE:313-316 attribute it to the never-zero floor | **n — should-fix 1** |
| §2 blocks run from `$MEASUREMENT_ROOT` using `$CALIBRATION_LEDGER`/`$LEDGER_HEAD_PIN` | runbook:1401-1407, 1555-1557 and eight other blocks | §2.5 block:1710-1716 does neither | **n — should-fix 3** |
| Custody read-replay exemption recorded with call site | allowlist row reason | call at `epoch_equivalence_check.py:596`, row says 568 | **n — nit 1** |

Merge-ability sweep otherwise clean: no `TODO`/`FIXME`/`breakpoint`/stray `print(` in the
tests; no hand-typed operative digits anywhere in `scripts/epoch_equivalence_check.py` or
`tests/test_epoch_equivalence_check.py` (every constant is read from the registry/artifact —
grep for `0.009724|0.032898|0.010164|0.010818` in both files returns nothing); the literals
appear only in the three prose units, which is their home. `tests.test_mint_policy_resolver_guard`,
`tests.test_docs_freshness`, `tests.test_custody_mode_inventory` pass (39 tests, above).
The runbook's deletion of the old §2.3 blindness fence is not a loss: the term is rebuilt
at §Terms:162-166 and :202, the FAIL-route resumption is explicit at :1501, and the
glossary rows at :2190 and :2193 distinguish "blind" (every rule fixed before data) from
"blindness fence" (the code-enforced `prepare-candidate` refusal). No overbuild worth
pruning: the constants table, the per-slot outcome listing and the two-source cross-check
are each load-bearing for the addendum the PASS branch must write.

---

## Mutation claims assessed by reading (two of the seat's)

**Claim A — F1 cure: cutting the generation pin (`if False and acceptance_id != REQUIRED_ACCEPTANCE_ID`) is killed by
`test_another_authenticated_generation_is_refused_as_the_reference` (`tests/test_epoch_equivalence_check.py:384-406`).**
Would really fail. The test points `--acceptance` at the n19 predecessor
`configs/calibration/calibration_acceptance_d079_v2.json` — a genuinely authenticating
artifact, so the loader does not refuse it — with twelve retained values of `0.033`, and
asserts three things: `code == REFUSAL_EXIT` (3), `record is None`, and, decisively,
`assertIn("issue 316 fixes the reference envelope", text)` plus
`assertNotIn("EPOCH_EQUIVALENCE:", text)`. With the pin cut, control reaches
`acceptance_generation_operatives` for the predecessor id and the run either judges
(exit 0 or 4, verdict line printed) or refuses with a *different* message; on every branch
the message assertion fails. The counterfactual input is real and production-shaped: the
predecessor's level screen is the n19 corpus's, which `0.033` clears, so the cut converts
a FAIL into a PASS — the named counterfactual, not a today's-artifact cure. Kill is sound.

**Claim B — F2 cure: `casefold()` reverted to `lower()` is killed by
`test_an_out_path_under_a_unicode_case_alias_refuses` (`:422-434`); dropping the `samefile`
identity check is killed by `test_an_out_path_that_is_the_acceptance_directory_by_identity_refuses` (`:436-448`).**
Both would really fail, though the first kills on the message, not the exit code, and that
distinction matters. `"configſ".lower()` leaves U+017F unchanged (only `casefold()`
maps LONG S → `s`), so under the reverted mutation the parts scan misses; the identity arm
is then skipped too, because `parent.exists()` is False for the not-yet-created temp
directory. The run continues into `load_calibration_ledger_snapshot` and refuses there for
an unrelated reason — which still returns 3, so `assertEqual(code, REFUSAL_EXIT)` would
*pass*. The kill comes entirely from
`assertIn("never writes into an acceptance directory", stream.getvalue())`. That assertion
is present and load-bearing; the test is sound, but it is one assertion away from being a
false-negative, and the same is true of `:408` and `:436`. Worth knowing if anyone edits
these tests. The identity test is the round-2b shape and is correct: it derives its target
from `checker.REPO_ROOT` rather than from `checker.ACCEPTANCE_DIR`, so the regression
cannot be neutralised by the same constant the mutation would patch — which is exactly
the defect round 2 had and 2b fixed, and it is genuinely fixed here.

---

## Recommendation

Land after the three should-fix items; all three are prose/one-line edits with no
behaviour change and no re-audit surface beyond a docs-freshness re-run. If the magistrate
prefers to land as-is, should-fix 1 must at minimum be corrected before the printed NOTE is
quoted into the D-102 continuation addendum, and should-fix 2 before the two-checkout
comparison is attempted at the desk on the equivalence night.
