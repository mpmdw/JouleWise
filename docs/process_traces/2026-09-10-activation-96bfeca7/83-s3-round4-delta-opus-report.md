# 83 — S3 fix round 4 DELTA RE-AUDIT (execution lens, Opus) — 2026-09-10

Tree: `/Users/edr/code/JouleWise-wt-s3-acceptance-validator`, branch
`feat/2026-09-10-epoch-s3-acceptance-validator`, HEAD `030ceb5f` (parent `57d0044d`).
No git state changed; `git status --porcelain` empty at start and at end.
Canonical `/Users/edr/code/JouleWise` never touched. No `[QUIET-MAC]` measurement.

## VERDICT: **should_fix** (one survivor)

The round did what it was asked, and did it correctly: the envelope check matches
the pre-registration term for term, the rule name is outcome-independent per record 82,
`d125_ruling` is conditional and correctly gated, the six issued rows are untouched.
**12 of 13 isolation cuts were killed. One survived**, and it is in the round's own
load-bearing expression: the RANGE branch of the envelope rule is entirely untested,
and the surviving mutant admits an UNDERSTATED screen.

## Baseline

| item | value |
|---|---|
| `joulewise/calibration_bracketing.py` sha256, before AND after all cuts | `f30e62ed0e9df76be2ff1aee46dc14929c0d1a44107fa2bf21c3bdb375983946` |
| `tests/test_calibration_bracketing.py` sha256, before AND after (never mutated) | `1905a2aac889dc443fc1ffc229e552d9daf8aaab5bac4463542308036948eec9` |
| (d) `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing` at HEAD | **Ran 88 tests in 0.593s — OK (skipped=1)**, rc 0 |
| same, re-run after every cut was restored | **Ran 88 tests in 0.383s — OK (skipped=1)**, rc 0 |

Every cut was applied to production only, one at a time, run with
`PYTHONDONTWRITEBYTECODE=1`, then restored byte-for-byte; the harness asserts the
pre-cut sha256 and reports the post-restore sha256 (`restored=True` on all 13).

## Cut table (isolation rule, diff-derived scope)

| # | cut | selected test | result |
|---|---|---|---|
| C1 | `D125_SCREEN_FLOOR_S` `0.010818` → `0.010817` | `…test_floored_envelope_screen_rule_admits_a_floor_bound_generation` | **KILLED** — Ran 1 test, FAILED (failures=1) |
| C2 | `max(quantized_range, D125_SCREEN_FLOOR_S)` → `min(…)` | same | **KILLED** — Ran 1 test, FAILED (failures=1) |
| C3 | envelope check → range-equals check (`quantized_range == screen`) | same | **KILLED** — Ran 1 test, FAILED (failures=1) |
| C4 | drop `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` from `_REGISTERED_SCREEN_RULES` | same | **KILLED** — Ran 1 test, FAILED (failures=1) |
| C5 | delete the whole `d125_ruling` conditional clause | `…test_envelope_generation_requires_a_non_empty_d125_ruling` | **KILLED** — Ran 1 test, FAILED (failures=4, all four subTests) |
| C5b | `_D125_RULING_REQUIRED_SCREEN_RULES` → `frozenset()` | same | **KILLED** — Ran 1 test, FAILED (failures=4) |
| C6 | invert the gate (`not in` → `in`) | whole module | **KILLED** — Ran 88 tests, FAILED (failures=92) |
| C7 | accept the empty string (drop `and bool(...)`) | `…requires_a_non_empty_d125_ruling` | **KILLED** — Ran 1 test, FAILED (failures=1) |
| C8 | accept a non-string (`isinstance(..., str)` → `is not None`) | same | **KILLED** — Ran 1 test, FAILED (failures=1) |
| C9 | `else: return False` → `else: screen_matches_rule = True` | `…test_unimplemented_screen_rule_refuses_instead_of_falling_back` | **KILLED** — Ran 1 test, FAILED (failures=1) |
| C11 | `BRACKET_SCREEN_QUANTUM_S` `1e-6` → `1e-5` | whole module | **KILLED** — Ran 88 tests, FAILED (failures=92) |
| C12 | `PREFLIGHT_LEVEL_SCREEN_QUANTUM_S` `1e-15` → `1e-13` | whole module | **KILLED** — Ran 88 tests, FAILED (failures=13) |
| **C10** | **envelope RANGE branch removed: `max(quantized_range, D125_SCREEN_FLOOR_S) == screen` → `D125_SCREEN_FLOOR_S == screen`** | **whole module** | **SURVIVED — Ran 88 tests, OK (skipped=1)** |

## F1 — should_fix: the envelope rule's RANGE branch is untested (C10 survivor)

Every added test drives `_floored_envelope_case`, whose corpus range is fixed at
`0.006000` — always BELOW the floor. No test ever exercises the envelope name with a
range ABOVE the floor, which is the branch the pre-registration expects to be the
common outcome (`S = max(new range quantized to 1e-6 ROUND_HALF_EVEN, 0.010818)`;
the new 25G83 corpus's range is unknown and either side may realize).

Consequence, demonstrated both ways with the same fixture:

- **true code:** an envelope row with range `0.025000` and `bracket_screen_s`
  pinned at the floor `0.010818` → `_valid_acceptance_bound` returns **False** (correct:
  the screen must be the range once the range wins).
- **C10 mutant:** the same row returns **True** — a screen UNDERSTATED by 0.014182 s
  against its own corpus is admitted — and the full 88-test module stays green.

So the fence that refuses an understated envelope screen exists in production but is
held by no test at all. Under the isolation rule that is a should_fix, not a nit: it is
the exact defect class (screen understatement) the envelope rule was registered to bar.

Cure: one test with corpus member values whose quantized range exceeds `0.010818`,
under `SCREEN_RULE_FLOORED_RANGE_ENVELOPE`, asserting (i) admit when the screen equals
the range, (ii) refuse when the screen equals the floor. Recipe verified working — the
fixture must also recompute `decimal_derivation.source_statistics`
(`minimum_s`, `maximum_s`, `range_s`, `mean_presentation_s.value`,
`sample_sd_presentation_s.value`, and the min/max member ids) before `_reseal`,
because the validator recomputes them at `calibration_bracketing.py:986-1003`;
without that the fixture refuses for an unrelated reason and proves nothing.

Reproduce the survivor:

```bash
cd /Users/edr/code/JouleWise-wt-s3-acceptance-validator
python3 - <<'EOF'
import pathlib
p = pathlib.Path("joulewise/calibration_bracketing.py")
p.write_bytes(p.read_text().replace(
  "screen_matches_rule = max(quantized_range, D125_SCREEN_FLOOR_S) == screen",
  "screen_matches_rule = D125_SCREEN_FLOOR_S == screen").encode())
EOF
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing   # Ran 88 … OK
git checkout -- joulewise/calibration_bracketing.py
```

## (a) Six issued rows + genesis fixture: byte-identical — PASS

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.\
test_every_issued_generation_and_genesis_fixture_load_byte_identically -v
→ Ran 1 test in 0.008s — OK
```
That test sweeps every `configs/calibration/calibration_acceptance_*.json`, checks the
registry `file_sha256` per file, asserts `artifact == json.loads(raw)`, asserts
`_valid_acceptance_bound`, and pins `_acceptance_artifact_sha256(fixture) ==
GENESIS_FIXTURE_ACCEPTANCE_SHA256`.

## (b) No issued row's screen_rule / screen / level screen moved — PASS

`git diff 57d0044d 030ceb5f -- joulewise/ | grep -n '"screen_rule"\|bracket_screen_s'`
returns only validator-code lines (registry membership, the new conditional, the
`screen = Decimal(...)` read, the old `!=` guard removed, the new `screen_rule = …`
read). No derivation-table literal, no operative value, no `preflight_level_screen_s`
appears in the diff. `test_every_registered_generation_row_carries_the_full_schema`
still asserts `screen_rule == range_equals_screen` for all six rows and passes.

## (c) S4's row at f31884d7 against this tree — mixed

Probe: out-of-tree scratch module `/tmp/scratch_s4_seam.py`, run with
`PYTHONPATH=/tmp python3 -m unittest scratch_s4_seam` from the worktree; the
derivations table is patched only through the tests' own `_registered_generation`
context manager. Nothing in the repo was modified.

| S4 row variant | `_registered_generation_row_is_complete` |
|---|---|
| **as S4 emits it** (`epoch_catalog_ids = sorted(...)`, `registration_session_ids = list(...)` — i.e. lists), envelope rule, `d125_ruling` present | **REFUSE** |
| same row with both fields as tuples, envelope rule, `d125_ruling` present | **ADMIT** |
| same, tuples, envelope rule, `d125_ruling` removed | **REFUSE** (correct; the new gate) |

End-to-end through `_valid_acceptance_bound`, full 2×2 of rule name × screen:

| screen_rule | corpus range | screen | result |
|---|---|---|---|
| `range_equals_screen` | 0.006000 | 0.010818 (floored) | refuse ✓ |
| `range_equals_screen` | 0.025000 | 0.025000 (= range) | admit ✓ |
| `floored_range_envelope_screen` | 0.006000 | 0.010818 (floor binds) | admit ✓ |
| `floored_range_envelope_screen` | 0.025000 | 0.025000 (range wins) | admit ✓ (production correct — but see F1: untested) |

**Answer to the brief's question:** once S4 names the envelope rule unconditionally and
carries `d125_ruling`, its row DOES validate against this tree — **provided the two
sequence fields arrive as tuples.** As committed at `f31884d7` they are Python lists
and S3's `isinstance(catalog_ids, tuple)` / `isinstance(session_ids, tuple)` fences
refuse the row. That is the one remaining hard seam defect, and it is silent: the
refusal reason is not distinguished from any other completeness failure.

### F2 — should_fix (S4 side, seam): list vs tuple

`scripts/issue_calibration_acceptance_generation.py:678-693` emits
`"epoch_catalog_ids": sorted(epoch_catalog)` and `"registration_session_ids":
list(session_ids)`. S3 requires tuples (deliberately — the row is meant to be
immutable and hashable). S4's fix round must emit tuples, or the registration step
that installs the row must convert. Recommend S4 emits tuples so the emitted row
is the registered row.

### F3 — confirmed outstanding (S4 side, already scheduled by record 82)

- `…prepare_candidate.py:594-598` still names the rule by OUTCOME
  (`SCREEN_RULE_FLOORED_RANGE_ENVELOPE if floor_bound else SCREEN_RULE_RANGE_EQUALS_SCREEN`),
  which record 82 overruled. S3 round 4 is the half that makes the fix possible;
  S4's fix round owes the unconditional name.
- `…:757-760` `"screen_rule_registered_in_validator": (screen_rule ==
  SCREEN_RULE_RANGE_EQUALS_SCREEN)` is now STALE — the envelope name IS registered as
  of `030ceb5f`, so this diagnostic will print a false "not registered" warning
  (`:523-524`) for exactly the generation the pre-registration expects. Should become a
  membership test against the imported `_REGISTERED_SCREEN_RULES` vocabulary.

Neither is an S3 defect; both are named so the seam does not close on them.

## Nit (no action required)

The `d125_ruling` clause relies on unparenthesized `A or B and C` precedence:

```python
generation["screen_rule"] not in _D125_RULING_REQUIRED_SCREEN_RULES
or isinstance(generation.get("d125_ruling"), str)
and bool(generation.get("d125_ruling"))
```

Semantics are correct (`and` binds tighter) and all four inversions of it were killed
(C5, C5b, C7, C8). Parentheses around the `isinstance … and bool …` pair would make the
grouping visible to the next reader.

## Authority checked

- Pre-registration (`origin/feat/2026-09-10-epoch-s6-docs-prereg:configs/calibration/preregistration_d079_epoch_25g83_rev1.md`,
  the Analysis paragraph): "bracket screen S = max(new range quantized to 1e-6 s
  ROUND_HALF_EVEN, 0.010818) … The generation records the predecessor ceiling and an
  explicit d125_ruling reference; issuance refuses while that reference is absent."
  The implementation matches term for term, including `ROUND_HALF_EVEN` and the quantum.
- Cold gate 46 V7 (`10-coldgate-fable-ruling.md:41`): the generation row carries an
  explicit `d125_ruling` and the issuer refuses while it is absent. Honoured, and
  correctly made conditional (the six pre-envelope rows carry none and still validate —
  `test_range_equals_screen_rows_need_no_d125_ruling`).
- Record 82: the rule NAME describes the pre-registered rule, not which branch won.
  Honoured in code and in the registered comment at `calibration_bracketing.py:234-239`.

## Files

- Production under audit: `/Users/edr/code/JouleWise-wt-s3-acceptance-validator/joulewise/calibration_bracketing.py`
- Tests under audit: `/Users/edr/code/JouleWise-wt-s3-acceptance-validator/tests/test_calibration_bracketing.py`
- Cut harness (scratch, out of tree): `/tmp/mutcut.py`, `/tmp/cuts1.json`, `/tmp/cuts2.json`
- Seam probe (scratch, out of tree): `/tmp/scratch_s4_seam.py`

## Integrity caveat

Two `__pycache__/*.pyc` files carry mtimes inside this audit's window (12:15:34,
12:17:03) even though `PYTHONDONTWRITEBYTECODE=1` was set on every subprocess I
launched; they are `.gitignore`d (`.gitignore:1 __pycache__/`) and are keyed to the
restored source, so the tree is clean (`git status --porcelain` empty) and no cached
mutant bytecode can be loaded. Both tracked files hash to their pre-audit values and
`HEAD` is still `030ceb5f`.
