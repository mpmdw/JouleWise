# 77 — S3 fix round 3, DELTA RE-AUDIT (execution lens, Opus)

- Round under audit: `57d0044d` vs `f40e748b` (worktree `/Users/edr/code/JouleWise-wt-s3-acceptance-validator`, branch `feat/2026-09-10-epoch-s3-acceptance-validator`)
- Scope: diff-derived (A5 isolation rule) — `joulewise/calibration_bracketing.py` (one new joint-presence guard + docstring), `tests/test_calibration_bracketing.py` (3 new tests + `_envelope_case` fixture fix)
- Prior report: `73-s3-r2-delta-opus-report.md` (findings S1, S2, S3)
- Read-only: no git state changes; every mutation cut restored and sha256-asserted; canonical `/Users/edr/code/JouleWise` untouched (HEAD `cc171556`, clean). No `[QUIET-MAC]` work.

## VERDICT: CLEAN

All three round-2 findings (S1, S2, S3) are cured with isolating counterfactuals. Every atomic cut in the diff-derived scope is killed. No new defect at any severity; two observations recorded below, neither a should_fix.

## Hashes

At HEAD `57d0044d`, before and after every cut (all restores verified byte-identical):

| file | sha256 |
| --- | --- |
| `joulewise/calibration_bracketing.py` | `51ae8ad43ae3c61aca6326029c9af7afa79040c9a5a3d8b1a86ee83a3a7c38cf` |
| `tests/test_calibration_bracketing.py` | `46d2357afa68fecf43e1af5b6c547d3d26968bff7c5397f29895b877ec94c8f5` |

`RESTORE_OK` printed on all 6 cuts (hash before == hash after each run); worktree `git status --porcelain` empty afterwards.

## Whole module at HEAD

```
cd /Users/edr/code/JouleWise-wt-s3-acceptance-validator
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing
```
→ **Ran 83 tests in 0.420s — OK (skipped=1)**, rc 0. (The two `custody_locator_unreachable reason=timeout` lines on stderr are an expected diagnostic emitted by a passing custody test, not a failure.)

## Byte-identical artifact sweep (seat's cited fence)

Test name is `GenerationKeyedIssuanceValidationTests.test_every_issued_generation_and_genesis_fixture_load_byte_identically` — it sweeps every `configs/calibration/calibration_acceptance_*.json`, asserts count == `ISSUED_ACCEPTANCE_REGISTRY`, per-file sha256 == the registry pin, round-trips the load against `json.loads(raw)`, and requires `_valid_acceptance_bound` true for each; then the genesis fixture under `GENESIS_FIXTURE_ACCEPTANCE_SHA256`.

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.test_every_issued_generation_and_genesis_fixture_load_byte_identically \
  tests.test_calibration_bracketing.CalibrationBracketingTests.test_genesis_fixture_bytes_authenticate_under_their_own_pin
```
→ **Ran 2 tests — OK**. The new guard re-keys no issued byte and refuses no issued row.

(Note for the record: my first invocation of this pair errored because I addressed the genesis-pin test to the wrong class; it lives in `CalibrationBracketingTests` at test file line 643, not in `GenerationKeyedIssuanceValidationTests`. The corrected command above is the one that ran.)

## Cut table

Harness: `/tmp/s3r3_cut.py <cut>` — applies one textual cut (asserted unique), runs the whole module, restores the original bytes in a `finally`, re-hashes. "Result" is the set of tests that FAIL/ERROR under the cut.

| # | Clause | Cut | Selected test | Ran N | Result |
| --- | --- | --- | --- | --- | --- |
| C1a | new joint-presence guard | delete the 4-line `if` block | `test_lineage_fields_are_jointly_present_or_jointly_absent` | 83 | KILLED, **isolating** — that test alone fails (rc 1) |
| C1b | new joint-presence guard | `is not None` → `is None` | same | 83 | KILLED, not isolating — 75 tests fail (see obs. 1) |
| C2 | `max(predecessor, prediction)` | → `predecessor` | `test_envelope_ceiling_equals_own_q99_when_own_q99_dominates` | 83 | KILLED, **isolating** — that test alone fails (cures **S1**) |
| C3 | `registered is None or …` | drop the `registered is None` disjunct | `test_malformed_ceiling_with_an_unresolvable_predecessor_refuses` | 83 | KILLED — that test + `test_absent_predecessor_ceiling_is_none_and_never_a_present_zero` (see obs. 2; cures **S2**) |
| C4 | absent-before-malformed ordering (downstream of the guard; A4 clause) | `if predecessor_lexeme is not None:` → `if _decimal(predecessor_lexeme) is not None:` | `test_absent_predecessor_ceiling_is_none_and_never_a_present_zero` | 83 | KILLED (+ the new unresolvable test) — the fixture fix did NOT hollow out the A4 ordering |
| C5 | `registered != predecessor` half | drop it, keep `registered is None` | `test_predecessor_ceiling_must_match_the_predecessor_row` | 83 | KILLED, **isolating** |
| C6 | genesis arm `prediction if predecessor is None` (downstream of the new guard) | `prediction` → `drift` | `test_genesis_ceiling_that_is_not_its_own_q99_refuses` | 83 | KILLED, **isolating** — the guard did not shadow the genesis equation |

C4–C6 are the "clauses downstream of a fence the diff adds or moves" required by A5; they are in scope because the new guard sits upstream of the predecessor branch, the equation, and the genesis arm, and because the fixture fix changes which arm several pre-existing tests now travel.

## S3 — fixture fix verification (id-without-ceiling rows)

Every construction of the two lineage fields in the test file:

- line 3597 `row["predecessor_ceiling_s"] = predecessor` and 3601/3603 — the `_envelope_case` fixture: id popped when `predecessor is None`, set to `_PREDECESSOR_FIXTURE_ID` otherwise. Jointly present/absent by construction.
- line 3686 `broken["predecessor_ceiling_s"] = malformed` — derived from a **genesis** case, so the id has been popped: ceiling malformed, no id. Guard does not apply.
- line 3750 `broken["predecessor_ceiling_s"] = 0` with `predecessor_acceptance_id = "no-such-generation"` — ceiling present-but-malformed, id present. Guard does not apply (guard requires ceiling `is None`).
- line 3764 `nulled["predecessor_ceiling_s"] = None` with the id retained — **the launder test, the only id-without-ceiling row in the suite.**
- pops at 3712 / 3783 (`unnamed`) and 3793 (`genesis`) are the converse direction (ceiling present, id removed) and a true genesis, both already fenced.

Repo-wide, `predecessor_acceptance_id` appears only in `joulewise/calibration_bracketing.py` (docstring 359, guard 393, lookup 405, comment 295) — it appears in **no** production derivation row: both `_D102_N19_DERIVATION` and `_D102_N17_DERIVATION` carry `predecessor_ceiling_s: None` and omit the id key entirely, so the guard cannot fire on either. Confirmed empirically by the byte-identical sweep passing.

## Ruling 69 §Q1 / addendum A4 dispositions

Read `_registered_generation_row_is_complete` end to end (lines 339–459). Against ruling 69 §Q1's ruled relation and its four isolating counterfactuals:

| Ruled input (§Q1 "Isolating counterfactuals") | Ruled disposition | HEAD disposition | Pinned by |
| --- | --- | --- | --- |
| `P=0.0095, Q99=0.008, C=0.009` (ceiling fell below predecessor's) | refuse | refuse, via `drift != max(predecessor, prediction)` | `test_envelope_ceiling_that_fell_below_its_predecessor_refuses` |
| `P=0.0085, Q99=0.008, C=0.009` (headroom invented above both) | refuse | refuse, same clause | `test_envelope_ceiling_invented_above_both_inputs_refuses` |
| `P=None, Q99=0.008, C=0.009` (genesis ceiling ≠ own Q99) | refuse | refuse, via the genesis arm — **C6 proves this arm is still the refusing clause after the guard**, not the guard | `test_genesis_ceiling_that_is_not_its_own_q99_refuses` |
| `P=0.009, Q99=0.008, C=0.009` (admit control the old clause wrongly refused) | ADMIT | admits | `test_predecessor_ceiling_must_match_the_predecessor_row` (first block) |

Plus the §Q1 cl.2 statement that both rows registered today set `predecessor_ceiling_s = None`: still true and still admitted (sweep OK). §Q1 cl.3's universal `screen < ceiling` half is untouched by this round.

**No ruled input is mis-dispositioned by round 3.**

A4 consistency: A4 says (a) a non-None `predecessor_ceiling_s` also names the predecessor's acceptance id and is compared against that registered row's `operatives.maximum_budgetable_drift_s`, with a non-resolvable predecessor refusing (HEAD: lines 404–418, `registered is None or registered != predecessor` — both halves independently pinned, C3 and C5); and (b) absence is tested `is None` BEFORE `_decimal`, a present non-string or unparseable value refusing (HEAD: line 385/388 ordering, pinned by C4).

The new joint-presence guard is the **converse** of A4(a) — named predecessor ⇒ non-None ceiling — which A4 does not state and does not contradict. It is a strict tightening within the ruled semantics: under §Q1 cl.2 `None` means "not derived under the envelope rule", and such a generation names no predecessor at all, so the id-without-ceiling row is not a shape the ruling licenses. Consistency check on both directions at HEAD: ceiling-without-id refuses (via `.get(None)` → unresolvable, pinned at test line 3712 and again at 3783); id-without-ceiling refuses (new guard, pinned at 3764); neither-present admits (pinned at 3793 and by the six issued artifacts); both-present is governed by the read-back comparison. The four quadrants are complete and each is pinned by a test.

## Observations (neither is a finding)

1. **C1b is a global-breaking mutation, by construction, not a coverage gap.** Flipping `is not None` → `is None` turns the guard into "refuse any row whose ceiling is None and whose id is also None", i.e. refuse every genesis row — which is what all six issued artifacts and both registered derivations are. 75 tests fail. The atomic cut that tests the guard's *own* behaviour is C1a (deletion), and that one is exactly isolating.

2. **C3 fails two tests, not one, and the second is a side effect of the fixture fix — benign.** `test_absent_predecessor_ceiling_is_none_and_never_a_present_zero` (line 3671) builds its `broken` rows from a genesis `_envelope_case`, which after round 3 no longer carries the id. For the `malformed = 0` subtest the lexeme parses to `None` and the unnamed predecessor resolves to `None`, so with the disjunct removed `None != None` is False and the row is admitted — hence the extra failure. Two consequences, both checked: (i) my S2 finding was correct at round 2 (with the id always set, that test could not have reached the `registered is None` branch), so the new test was needed, not redundant; (ii) the pre-existing test's stated subject ("silently convert an envelope successor into a genesis one") is now travelled with no predecessor *named*, but the A4 ordering it exists to pin is still killed on its own by C4, and the previously-covered shape "resolvable predecessor + present-`0` ceiling" still refuses at HEAD through `registered != predecessor` (C5-pinned). No coverage was lost; only the comment at line 3674–3677 is now slightly ahead of the fixture it describes. Nit, not raised as should_fix.

3. **Pre-existing, unreachable, not from this diff:** `_D102_GENERATION_DERIVATIONS.get(generation.get("predecessor_acceptance_id"))` at line 404–406 would raise `TypeError` rather than refuse if a row carried an unhashable id (a list/dict). Row bytes come only from the module-level `_D102_GENERATION_DERIVATIONS` literal and the test-only `_registered_generation` patch hook — never from artifact JSON (`:711`, `:1801`, `:2232` all key the module dict by `acceptance_id`) — so the input is not attacker-controlled. This line is unchanged since round 2 and is outside the diff-derived scope; recorded only so it is not re-discovered.

## Reproducing commands

```bash
cd /Users/edr/code/JouleWise-wt-s3-acceptance-validator
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing      # Ran 83, OK (skipped=1)
python3 /tmp/s3r3_cut.py C1a_delete_guard        # -> only the launder test fails, RESTORE_OK
python3 /tmp/s3r3_cut.py C2_max_to_predecessor   # -> only the own-Q99-dominates test fails
python3 /tmp/s3r3_cut.py C3_drop_registered_none # -> unresolvable-predecessor test (+ obs. 2)
python3 /tmp/s3r3_cut.py C4_malformed_as_absent
python3 /tmp/s3r3_cut.py C5_drop_mismatch_half
python3 /tmp/s3r3_cut.py C6_genesis_arm
```

No finding requires a fix round. S1, S2, S3 are closed.
