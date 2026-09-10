# 73 — S3 fix round 2 DELTA RE-AUDIT (execution lens, Opus refuter)

Scope: `git diff 93799321 f40e748b` (`joulewise/calibration_bracketing.py`,
`tests/test_calibration_bracketing.py`) in `/Users/edr/code/JouleWise-wt-s3-acceptance-validator`,
branch `feat/2026-09-10-epoch-s3-acceptance-validator`, HEAD `f40e748bb3924c414ed547999f6ba02de1f7120a`.
Authority: cold-gate ruling 69 §Q1/§Q2 plus addendum 11 (A4, A5). Method: cut scope DERIVED FROM THE DIFF
per A5, one atomic term per cut, one selected killer test per cut, `Ran N` parsed, source bytes restored
and hash-asserted after every cut.

## Verdict — **should_fix ×3, no blockers**

Production behaviour at HEAD is correct on every ruled input I could construct: the ruled relation, the
strict screen, the absent/malformed split, the read-back, and the fail-closed session kind all behave as
§Q1/A4 specify. The three findings are **unpinned terms and one unruled asymmetry**, not wrong answers.
Two atomic cuts SURVIVED the entire 80-test module; under A5 clause (3) a surviving atomic cut is
should_fix, and here neither term is dead — each flips a concrete ruled input, so both are *under-tested*,
not dead.

- **S1 (should_fix)** `max(predecessor, prediction)` → `predecessor` survives: no test covers the
  own-Q99-dominates direction.
- **S2 (should_fix)** `registered is None` disjunct drops with no test noticing — and the seat's
  "the removed term was dead" argument *rests on this unpinned disjunct*.
- **S3 (should_fix)** A row that NAMES `predecessor_acceptance_id` but sets `predecessor_ceiling_s = None`
  is admitted as a genesis, laundering an envelope violation with a one-field edit. Nothing refuses it.

## Hashes (identical before and after every cut; `git status --porcelain` empty at exit)

| File | sha256 |
|---|---|
| `joulewise/calibration_bracketing.py` | `944d6d324d3474efdd8d37334b50cabfd6119dff368fde7cecdc4486699965a1` |
| `tests/test_calibration_bracketing.py` | `2c03f182a8a7300ff0b2c4e971c0e359626cf27d4a8f9b2357b0320c20365818` |

The harness (`/tmp/s3delta/cut.py`) asserts `hash_after == hash_before` after each cut and aborts on
mismatch. Every row below reported `"restored": true`. The test file was never mutated.

## HEAD run (asked for verbatim)

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing
Ran 80 tests in 0.524s
OK (skipped=1)
```

## Cut table

`C.` = `tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.`; `MOD` =
`tests.test_calibration_bracketing` (the whole module, run as the survivor check for every cut).

| # | Clause (diff-derived) | Atomic cut | Selected killer test | Ran N | Result |
|---|---|---|---|---|---|
| a1 | ruled relation, selector | `predecessor is None` → `predecessor is not None` | `C.test_envelope_ceiling_equals_max_of_predecessor_and_own_q99` | 1 (MOD 80) | KILLED |
| a2 | ruled relation, operator | `max(...)` → `min(...)` | same | 1 (MOD 80) | KILLED |
| a3 | ruled relation, operand | `max(predecessor, prediction)` → `prediction` | same | 1 (MOD 80) | KILLED |
| **a4** | ruled relation, operand | `max(predecessor, prediction)` → `predecessor` | (none exists) | 1 (MOD 80) | **SURVIVED** |
| a5 | ruled relation, whole term | term deleted (isolation probe) | `…_fell_below_its_predecessor_refuses` / `…_invented_above_both_inputs_refuses` / `…_genesis_ceiling_that_is_not_its_own_q99_refuses` | 1 each | KILLED ×3 |
| b1 | strict screen | `not screen < drift` → `not screen <= drift` | `C.test_generation_row_refuses_a_screen_at_or_above_its_ceiling` | 1 (MOD 80) | KILLED |
| c1 | absence gate | `if predecessor_lexeme is not None:` → `if True:` | `C.test_absent_predecessor_ceiling_is_none_and_never_a_present_zero` | 1 (MOD 80) | KILLED |
| c2 | absence gate | `is not None` → truthiness (`if predecessor_lexeme:`) | same | 1 (MOD 80) | KILLED (2 failures) |
| c3 | absence gate | → `if not predecessor_lexeme:` | same | 1 (MOD 80) | KILLED |
| **d1** | read-back, disjunct 1 | drop `registered is None` | (none exists) | 1 (MOD 80) | **SURVIVED** |
| d2 | read-back, disjunct 2 | drop `registered != predecessor` | `C.test_predecessor_ceiling_must_match_the_predecessor_row` | 1 (MOD 80) | KILLED |
| e1 | predecessor lookup | `generation.get("predecessor_acceptance_id")` → constant `PREDECESSOR_ACCEPTANCE_ID` | same | 1 (MOD 80) | KILLED |
| f1 | fail-closed kind | `return SESSION_KIND_UNRESOLVED` → `return SESSION_KIND_BRACKET` | `C.test_unresolvable_session_is_barred_not_read_as_bracket` | 1 (MOD 80) | KILLED |
| g1 | derivation membership | drop `SESSION_KIND_DERIVATION` | `CalibrationBracketingTests.test_derivation_night_row_never_becomes_a_claim_endpoint` (+ `…_is_skipped_by_the_bundles_universe_count`) | MOD 80 | KILLED |
| g2 | derivation membership | drop `SESSION_KIND_UNRESOLVED` | `C.test_unresolvable_session_is_barred_not_read_as_bracket` | 1 (MOD 80) | KILLED |
| h1 | required keys | drop `"predecessor_ceiling_s"` from `_GENERATION_ROW_REQUIRED_KEYS` | `C.test_registered_generation_row_refuses_a_missing_required_key` | 1 (MOD 80) | KILLED (errors=1) |

Note on h1: the kill arrives as an uncaught `KeyError` from the direct subscript
`generation["predecessor_ceiling_s"]`, not a clean `False`. That is sound only because the
`_GENERATION_ROW_REQUIRED_KEYS.issubset` check precedes it — which the cut removes. Recorded as an
observation, not a finding: the pre-existing shape is unchanged by this round.

## S1 (should_fix) — the `max` is only pinned in one direction

**Cut:** `max(predecessor, prediction)` → `predecessor`. **Result:** whole module `Ran 80 … OK`.

Every envelope test in the diff uses own Q99 `0.008` with a predecessor at or above `0.0085`, so the
predecessor always wins the `max`. Ruling 69 probe 3's fourth row — "own Q99 dominates",
`P=0.0085 Q=0.009 C=0.009 → True` — has no test. Under the cut, HEAD flips on both halves of that row:

```
A4-admit-control  P=0.0085 Q=0.009 C=0.009   -> False   (ruled: True)
A4-refuse         P=0.0085 Q=0.009 C=0.0085  -> True    (ruled: False, ceiling below own corpus Q99)
```

(HEAD, unmutated, returns `True` / `False` — correct.) The second line is the one that matters: with the
cut in place a generation may register a budget ceiling BELOW its own 99 % two-draw prediction whenever a
predecessor is present, and nothing in the suite objects.

Call site: `joulewise/calibration_bracketing.py:404-406` (`_registered_generation_row_is_complete`).
Reproduce (read-only; restores itself):
```
cd /Users/edr/code/JouleWise-wt-s3-acceptance-validator
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python3 /tmp/s3delta/probe.py     # HEAD: True / False
python3 /tmp/s3delta/runa.py                                               # cut a4: Ran 80, OK
```
Fix: a fifth counterfactual — `predecessor="0.0085"`, own Q99 `0.009000`, ceiling `0.009000` admits
(own Q99 won the max); the same predecessor with ceiling `0.0085` refuses.

## S2 (should_fix) — the `registered is None` disjunct is unpinned, and the deadness argument leans on it

**Cut:** `if registered is None or registered != predecessor:` → `if registered != predecessor:`.
**Result:** whole module `Ran 80 … OK`.

`test_predecessor_ceiling_must_match_the_predecessor_row`'s "no predecessor row is registered at all"
subcase does not reach this disjunct: the successor's `predecessor` parses to a `Decimal`, so
`registered != predecessor` (`None != Decimal`) already refuses. The disjunct is reached only when BOTH
sides are `None` — an unparseable/non-string `predecessor_ceiling_s` AND an unresolvable
`predecessor_acceptance_id` — and no test constructs that pair. Concrete input:

```
predecessor_ceiling_s = 0            # present, non-string -> _decimal -> None
predecessor_acceptance_id = "no-such-generation"
ceiling == own Q99 == 0.009000, screen 0.006000
HEAD -> False (refused, correct)
under cut d1 -> True (ADMITTED as a genesis row)
```

Call site: `joulewise/calibration_bracketing.py:400`. Reproduce: `/tmp/s3delta/probe.py` line
"D1-refuse" (HEAD `False`; under the cut `True`, printed by the cut-and-probe run in this audit).

**On the seat's deadness claim: CORRECT, but load-bearing on this unpinned term.** I re-inserted
`if predecessor is None: return False` immediately after `predecessor = _decimal(predecessor_lexeme)`
(inside the `predecessor_lexeme is not None` branch) at HEAD: `Ran 80 … OK`, zero behaviour change —
so the term is indeed dead *there*. The reason is exactly the read-back disjunction: entering the branch
with `predecessor is None` means the lexeme was malformed, and then either `registered` is a `Decimal`
(so `registered != predecessor` refuses) or `registered is None` (so the first disjunct refuses). The
second of those two paths is the one no test covers. So the seat removed a term as dead on the strength
of a term nothing pins — S2's fix (add the malformed-lexeme + unresolvable-row counterfactual) closes
both at once. Note also that the term would have been WRONG, not merely dead, at top level outside the
branch: it would refuse every genesis row, including both registered ones.

## S3 (should_fix) — a named predecessor with a nulled ceiling is read as a genesis

Not a cut finding; found by reasoning over the absence gate the diff adds. `predecessor_acceptance_id`
is not in `_GENERATION_ROW_REQUIRED_KEYS` and is consulted ONLY inside the
`predecessor_lexeme is not None` branch. A row that names a predecessor and sets
`predecessor_ceiling_s = None` therefore takes the genesis arm; the lineage fence evaporates silently.

```
predecessor's registered row: maximum_budgetable_drift_s = 0.0095
successor row: predecessor_acceptance_id = <that row>, predecessor_ceiling_s = None,
               own Q99 = ceiling = 0.009000, screen 0.006000
_valid_acceptance_bound(...) -> True      # ADMITTED
```
This is precisely the "ceiling fell below its predecessor's" violation ruling 69 exists to refuse
(`test_envelope_ceiling_that_fell_below_its_predecessor_refuses` refuses the same lineage when the row is
honest), laundered by nulling one field. A4 rules the direction "non-None ceiling with no resolvable
predecessor row refuses"; the converse is unruled, and the ruling's "`None` is the truthful registration"
premise assumes an honest issuer. **No live exposure today** — both registered rows set
`predecessor_ceiling_s = None` and carry no `predecessor_acceptance_id` — so this is a future-issuance
hole, hence should_fix and not a blocker. Fix: refuse when `predecessor_ceiling_s is None` and
`predecessor_acceptance_id` is present, with a test.

Call site: `joulewise/calibration_bracketing.py:381-401`. Reproduce:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python3 /tmp/s3delta/probe2.py` (prints `-> True`).

## Asked-for checks

**Do the four counterfactual tests move the artifact AND the registered row together?** YES, and proven
by execution, not by reading. `_envelope_case` writes the retuned `operatives` into
`tuned["decimal_derivation"]["ratified_operatives"]` and the Q99 into `source_statistics`, then
`_reseal`s. Cut a5 (relation term deleted, everything else intact) makes all three refusal tests FAIL —
i.e. their inputs are ADMITTED once that single term is gone, so the `:928`/`:942` byte-identity fences
are not what kills them. That is the D2 defect cured. The admit control
(`…_equals_max_of_predecessor_and_own_q99`) reaches the clause too: it dies under a2 and a3.

**Is any test in the diff not defect-shaped?** Partially — and benignly. Simulating round-1 relation
semantics under HEAD scaffolding (compound probe, used only for this question: relation →
`drift != prediction`) leaves 78/80 passing; only
`test_envelope_ceiling_equals_max_of_predecessor_and_own_q99` and
`test_predecessor_ceiling_must_match_the_predecessor_row` fail. So
`…_fell_below_its_predecessor_refuses`, `…_invented_above_both_inputs_refuses`,
`…_genesis_ceiling_that_is_not_its_own_q99_refuses` and
`…_absent_predecessor_ceiling_is_none_and_never_a_present_zero` would also pass on round-1 semantics.
That is expected and not a finding: round 2's change to the relation is a RELAXATION (round 1 refused
those inputs for the wrong reason), and A5's requirement is isolation against the round-2 clause, which
a5 demonstrates. The relaxation itself is pinned by the admit control, and the new fence by the read-back
test. `test_unresolvable_session_is_barred_not_read_as_bracket` is defect-shaped against round 1 (f1 and
g2 both kill it, and both terms are round-2 additions).

**Import shim.** Verified identical on both sides of the seam:
`git show origin/feat/2026-09-10-epoch-s2-ledger-sessions:joulewise/calibration_ledger.py` has
`SESSION_KIND_BRACKET = "bracket"` (`:72`), `SESSION_KIND_DERIVATION = "derivation"` (`:73`),
`SESSION_KINDS = (…)` (`:74`), both in `__all__` (`:5925-5927`). The fallback restates exactly those two
values. At this checkout the ledger does NOT export the names (confirmed:
`hasattr(calibration_ledger, "SESSION_KIND_BRACKET") is False`), so the `except ImportError` arm is the
live one and `B.SESSION_KIND_BRACKET/DERIVATION/UNRESOLVED` resolve to
`bracket / derivation / unresolved-session`. `SESSION_KIND_UNRESOLVED` is bracketing-local and cannot
collide with S2's `SESSION_KINDS`. No stale `BRACKET_SESSION_KIND` / `DERIVATION_SESSION_KIND` /
`inherited_ceiling_s` reference survives anywhere in the tree (`grep -rn` over `*.py`/`*.md`/`*.json`,
zero hits). **Nit / integration-tree carry-forward:** nothing in the diff FAILS if the fallback survives
the merge, so the "delete on merge" instruction is enforced by comment only; the seat flagged this
itself. An integration-tree assertion (`from joulewise.calibration_ledger import SESSION_KIND_BRACKET`
must succeed, i.e. the try arm is live) would make it self-enforcing.

## Method notes / limits

25 min budget honoured. Cuts were applied to production source only, one exact-string anchor each
(anchor-count asserted `== 1`, so no silent multi-site edit), test selected per cut and the whole module
run as the survivor check. `Ran N` parsed from the runner for every row; no row ran 0 tests. Two probe
scripts and the harness live under `/tmp/s3delta/` and `/tmp/magistrate-96bfeca7/`; nothing was written
inside either worktree, and no git state-changing command was run.
