# 199 — S10 rounds 9+10 READ-ONLY FRESH-EYES REVIEW (gate row 10)

Target: `0a1917fb` (round 9) and `4c04f53e` (round 10) on
`feat/2026-09-10-epoch-continuation`; baseline `2e798f87` (round 8, fresh-eyes 196).
Diff read with `git -C /Users/edr/code/JouleWise-wt-s10-continuation diff 2e798f87 4c04f53e`;
**all execution in the read-only export `/tmp/s10-r10-export`** (`git archive 4c04f53e | tar -x`),
`PYTHONDONTWRITEBYTECODE=1`, no `timeout`. One comparison run in the pre-existing
`/tmp/s10-r8-export`. **No repository, worktree or checkout was modified; no git write command
was run.** `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` and every other worktree were
untouched. The only file I wrote is this report.

**Verdict: NOT CLEAN — 0 blockers, 2 should-fix, 3 nits.** Every behaviour the brief asks about is
correct in the code and I executed each one; 196's Finding B (blocker) and Finding A (should-fix)
are both genuinely closed. The two should-fix items are consequences round 9 created and neither
round swept: a contract paragraph that still states the behaviour round 9 deliberately removed
(**the fourth occurrence of the doc-asserted-contract signature** — 174 B1 → 191 D1/D2 → 196 A →
here), and the loader/issuer **mutation gate is RED** at this head (`survivors=1`, runner rc 1)
because round 9 turned cut C49 into an equivalent mutant.

---

## (1) Round 9 — exit 4, exit 3, exit 5, and the deliberate tool/loader divergence

All four executed through the real CLI (`issuer.main`) in the export, on synthetic fixture nights
built by `tests/fixtures/epoch_bootstrap/build.py`. `level_screen_s = 0.032898493715362`,
`bracket_screen_s = 0.009724`.

**(a) Exit 4 is reachable and the printed record carries the numbers. CONFIRMED.**
Night = 3 slots at `0.033898493715362` (level + 0.001) + 9 at `0.025`, all `valid`, all resolved:

```
rc = 4   stderr empty   candidate written = False
verdict fail   m 12   retained_min_s 0.025   retained_max_s 0.033898493715362
retained_range_s 0.008898493715362   evidence.slots = 12 entries
```

Each of the 12 slot entries carries `slot, attempt_id, content_id, manifest_sha256,
instrument_evidence_sha256, disposition, anchor_v3_resolved, anchor_v3_detail, b_fiducial_s`
(`scripts/issue_epoch_continuation.py:115-125`), so the per-slot outcomes, `m`, both extrema and the
range all reach the desk. Print-then-return without writing:
`scripts/issue_epoch_continuation.py:296-299` (`if rc: print(...); return rc`).

**(b) The envelope refusal still fires on delta 179's forgery (a) shape. CONFIRMED — exit 3.**
Night = 6 finalized `valid` resolved rows at `0.025` + 3 `valid` rows at level + 0.001 carrying
`unresolved_detail="affine_clock_fit_empty"`, `fill_slots=9`, `abort_reason="window_exhausted"`
(retained m = 6 → PASS, one unresolved valid bound over the level screen):

```
rc = 3   stdout empty   candidate written = False
REFUSED: unresolved_valid_row_exceeds_envelope: unresolved slots: slots.d07, slots.d08, slots.d09;
the desk reports it to Ed for a written ruling
```

So the round-3 → 179 defence (an "unresolved" label that would flip FAIL→PASS) is intact.

**(c) The loader's rule is UNCHANGED and the divergence is exactly as the brief states.**
`git diff 2e798f87 4c04f53e` touches four files and `joulewise/calibration_epoch_continuation.py`
is not one of them. The loader gate is still unconditional and sits *before* the statistics recompute:
`joulewise/calibration_epoch_continuation.py:265-266`
(`_require(envelope_holds_over_all_valid(lexemes_all_valid, rule), "unresolved_valid_row_exceeds_envelope")`),
with or without a ledger snapshot, over every disclosed `valid` bound, resolved or not.

Precise statement of the divergence, which is sound:

> The **loader** refuses any continuation FILE whose disclosed valid bounds break the envelope,
> unconditionally — it is validating bytes that already exist and could have been hand-written.
> The **tool** applies the same envelope check only on the branch where it would otherwise WRITE a
> candidate, i.e. when the retained values PASS. A FAIL (rc 4) or INCONCLUSIVE (rc 5) night writes
> nothing, so there is no artifact for the envelope check to protect; refusing there only withheld
> the night's numbers from the desk.

The two are consistent because the tool's gate is strictly *inside* the loader's: whenever
`verdict == "pass"` and the all-valid envelope fails, `unresolved_valid` is necessarily non-empty
(every `valid` + resolved row is appended to both `all_valid` and `retained` at
`scripts/issue_epoch_continuation.py:128-142`, so if no valid row were unresolved the two multisets
would be equal and a PASS would imply the envelope holds). The refusal therefore always names at
least one slot. And a FAIL/INCONCLUSIVE record hand-copied into a file still cannot authenticate:
`joulewise/calibration_epoch_continuation.py:204` requires `verdict == "pass"`, and `:265` re-applies
the envelope.

**Does the contract say the same? The new sentence does; an older paragraph 220 lines above still
says the opposite — see SF-1.** The new text is
`docs/contracts/epoch_continuation.md:303-306`: "Exit 4 is the statistics FAIL mapping and prints
the derived record. The envelope refusal (exit 3) applies only when the retained values PASS while
an unresolved valid bound sits outside the envelope: a FAIL or INCONCLUSIVE night always reaches the
desk with its numbers." That is accurate and matches the executed behaviour.

**(d) INCONCLUSIVE with an unresolved over-screen bound prints its record at rc 5. CONFIRMED.**
Night = 5 `valid` resolved at `0.025` + 7 `valid` unresolved at level + 0.001:

```
rc = 5   stderr empty   candidate written = False
verdict inconclusive   m 5   retained_min_s 0.025   retained_range_s 0.000
valid-and-unresolved slots visible in the record = 7
```

**Could such a night ever be continued? No — confirmed twice over.** Nothing is written (checked
`out.exists() == False`); `prepare_candidate` returns before the write block on any non-zero rc
(`:296-299`). Even if the printed JSON were saved by hand, `check --candidate` requires an issued,
registry-pinned file (`:308-318`) and `authenticate_epoch_continuation` refuses at
`joulewise/calibration_epoch_continuation.py:204` (`verdict`) and `:265`
(`unresolved_valid_row_exceeds_envelope`).

---

## (2) Round 10 — the desk-tool witness carries and is checked on both provenance fields

Executed end-to-end in the export: the real `scripts/epoch_equivalence_check.py` run over a fixture
ledger with `--out`, then its record fed to `prepare-candidate --equivalence-record`.

```
desk rc 0
reference_envelope keys = [acceptance_file_sha256, acceptance_id, acceptance_path, bracket_screen_s,
  corpus_n, level_screen_s, maximum_budgetable_drift_s, raw_corpus_maximum_s, raw_corpus_range_s,
  screen_rule]
clean witness                     -> rc 0, stderr empty          (196 FINDING B CLOSED)
tamper acceptance_file_sha256     -> rc 3  REFUSED: equivalence_record.reference_envelope.acceptance_file_sha256
tamper screen_rule                -> rc 3  REFUSED: equivalence_record.reference_envelope.screen_rule
drop BOTH (older v1 record)       -> rc 0
drop acceptance_file_sha256 only  -> rc 0
drop screen_rule only             -> rc 0
screen_rule present but null      -> rc 3  REFUSED: ...reference_envelope.screen_rule
```

Every answer the brief asks for is yes. The tolerance is a genuine omission-tolerance, not a
value-tolerance: a present-but-wrong or present-but-null value refuses by name.

**Is `optional_checked` limited to exactly those two keys under `reference_envelope`? YES.**
`scripts/issue_epoch_continuation.py:249-254` — a single-entry dict keyed
`"equivalence_record.reference_envelope"` mapping to `{"acceptance_file_sha256", "screen_rule"}`,
read with `.get(field, set())`, so every other level of the recursion gets the empty set. Verified
negatively: dropping a science field still refuses by name —

```
drop reference_envelope.corpus_n                  -> rc 3 REFUSED: ...reference_envelope.corpus_n
drop reference_envelope.level_screen_s            -> rc 3 REFUSED: ...reference_envelope.level_screen_s
drop reference_envelope.maximum_budgetable_drift_s-> rc 3 REFUSED: ...reference_envelope.maximum_budgetable_drift_s
drop top-level m                                  -> rc 3 REFUSED: equivalence_record.m
unknown reference_envelope.extra_field            -> rc 3 REFUSED: ...reference_envelope.extra_field
```

**The two checked values are real cross-model provenance, not tautologies.** The desk tool computes
`acceptance_file_sha256` by hashing the acceptance FILE bytes
(`scripts/epoch_equivalence_check.py:293`) and reads `screen_rule` from the validator's registered
generation row (`:278-281, :294`). The issuer independently supplies the REGISTRY-pinned
`file_sha256` (`joulewise/calibration_bracketing.py:1218-1224` via `record["acceptance_file_sha256"]`)
and the registered rule name (`scripts/issue_epoch_continuation.py:206`). Equality therefore asserts
that the bytes the desk tool actually read hash to the registry pin the issuer trusts — the real
content of the check.

**The direct subscript at `:206` cannot raise.** `_D102_GENERATION_DERIVATIONS[artifact["acceptance_id"]]["screen_rule"]`
is reached only for an `artifact_role == "issued"` artifact (`:76`), and the acceptance loader
refuses to authenticate an issued artifact with no complete registered generation row
(`joulewise/calibration_bracketing.py:747-749`, `_registered_generation_row_is_complete` requiring
`screen_rule` in `_REGISTERED_SCREEN_RULES` at `:478`). Not a defect; noted because the desk tool
guards the same read with an explicit refusal and the issuer does not.

**196's Finding A (should-fix) is closed.** `docs/phase_2/derivation_night_runbook.md:2203` now
reads "differs from every epoch the active acceptance judges (its own, and any an authenticated
continuation carried it onto)", matching §Terms at `:145-150`. `test_docs_freshness` is green.

---

## SHOULD-FIX

### SF-1 — the contract still states the behaviour round 9 removed, 220 lines above the sentence that removed it

`docs/contracts/epoch_continuation.md:84-93` (unchanged by both rounds):

> "If the all-valid envelope fails, preparation **unconditionally refuses** with
> `unresolved_valid_row_exceeds_envelope`, names the unresolved slots (**or says
> `none (all valid rows resolved)`**), **exits 3**, and writes nothing … **This refusal also applies
> below the retained-count minimum.** … the prepare envelope gate **now refuses every screen
> violation before that calculation**."

Four separate false statements at this head, each contradicted by executed behaviour above and by
the tool's own contract paragraph at `:303-306`:

1. "unconditionally refuses" — the gate is now conditioned on `statistics["verdict"] == "pass"`
   (`scripts/issue_epoch_continuation.py:143-153`).
2. "exits 3" for an all-valid envelope failure — an all-resolved over-level night exits **4**
   (executed: rc 4).
3. "also applies below the retained-count minimum" — the INCONCLUSIVE case executed above exits
   **5** with its record; the refusal explicitly does not apply there.
4. "`none (all valid rows resolved)`" — round 9 deleted that fallback from the message
   (`:151`, now a bare `", ".join(unresolved_valid)`). The string survives **only** in this contract
   line: `grep -rn "none (all valid rows resolved)" scripts joulewise tests docs` returns exactly
   `docs/contracts/epoch_continuation.md:86`.

This is the same signature as 174 B1, 191 D1/D2 and 196 Finding A: a round rewrites one paragraph of
a contract and leaves an earlier paragraph of the SAME contract asserting the old rule. Fourth
occurrence; per the standing escalation trigger this is structural, not a typo — the repeated
failure is that the doc edit is scoped to the paragraph the author was reading rather than to
`grep` over the claim. Fix is 2 sentences in one file. (Everything else in that paragraph — the
loader half at `:88-90`, the "resolution can reduce m but cannot produce a FAIL→PASS flip"
reasoning at `:75-79` — remains TRUE and should stay.)

### SF-2 — round 9 broke the continuation mutation gate; it is RED at this head and round 10 did not notice

```
$ cd /tmp/s10-r10-export && PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py
C49 SURVIVED derive_record: 'not envelope_holds_over_all_valid(all_valid, rule)'
    -> 'bool(unresolved_valid) and not envelope_holds_over_all_valid(all_valid, rule)'
    | test_one_quantum_above_level_fails_without_writing
cuts=51 killed=50 survivors=1 source_sha256_restored=true
RUNNER_RC=1
```

The same cut at round 8 is **KILLED** (re-ran C49 alone in `/tmp/s10-r8-export`: `killed = True`), so
round 9 is what flipped it. Cause: C49 (`tests/fixtures/epoch_continuation/mutation_cuts.py:113-115`)
was pinned by `test_one_quantum_above_level_fails_without_writing`, whose assertion round 9 re-pointed
from rc 3 to rc 4 (`tests/test_epoch_continuation.py:617-618`). Under the new gate the mutant is
**equivalent**: `verdict == "pass"` already implies `unresolved_valid` is non-empty (argument in §1c),
so adding `bool(unresolved_valid) and …` changes nothing and no test can kill it.

Not a live hole — I verified both directions of the NEW condition are killed by existing tests:

| mutation of `scripts/issue_epoch_continuation.py:150` | result |
|---|---|
| drop the `verdict == "pass"` guard (restore round-8 behaviour) | KILLED by `test_unresolved_over_screen_rows_below_minimum_stay_inconclusive_with_the_record`, `test_a_failing_night_prints_its_derived_record_and_exits_4_without_writing`, `test_one_quantum_above_level_fails_without_writing` |
| whole gate → `False` (defence removed) | KILLED by `test_prepare_refuses_unresolved_valid_row_widening_range_without_writing` |

So the exposure is the gate artifact, not the code: the runner ships exiting 1, and the next round
that runs it will read a red result whose survivor is a false alarm — exactly the condition under
which a real survivor gets waved through. Fix: retire/re-point C49 onto the new condition (the two
rows in the table above are ready-made cuts). Note the runner is invoked by no test and no CI file
(`grep -rn mutation_cuts tests scripts .github` → nothing), so only a manual run catches this; that
is why round 9 and round 10 both missed it.

---

## NITS

- **N1** `tests/test_epoch_continuation.py:12` — `from contextlib import redirect_stdout` duplicates
  line 5 (`from contextlib import contextmanager, redirect_stdout, redirect_stderr`). Round 9
  added it; delete.
- **N2** `tests/test_epoch_continuation.py:68-70` vs `:935-939` — `run_cli` is now exactly
  `run_cli_of(issuer.main, args)` with `redirect_stderr` added back; the round-10 helper duplicates
  the round-1 one. `run_cli` should delegate. Also `run_cli_of` is defined at `:935`, i.e. between
  two tests and after its only caller at `:914`, and `epoch_equivalence_check` is imported inside the
  test body at `:911` while every other module is imported at file scope.
- **N3** The contract's `--equivalence-record` paragraph (`docs/contracts/epoch_continuation.md:310-319`)
  says "Unknown fields refuse; only the explicitly identified path and tool/publication provenance
  may be ignored" and never mentions round 10's new *omission* tolerance for
  `acceptance_file_sha256` / `screen_rule`. A reader cannot tell from the contract that a witness
  lacking them is accepted while one carrying them is checked. One sentence, same file as SF-1.
- (Not a finding) The empty-`unresolved_valid` message shape
  (`"unresolved slots: ; the desk reports…"`) is now formally unreachable, as argued in §1c; I only
  observed it by forcing a mutant. It becomes dead text once SF-1's contract line is fixed.

---

## (4) Regression and mutation runs — pasted verbatim

```
$ cd /tmp/s10-r10-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_epoch_continuation tests.test_epoch_equivalence_check tests.test_docs_freshness 2>&1 | tail -3
Ran 120 tests in 215.952s

OK
```

```
$ cd /tmp/s10-r10-export && PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py
cuts=51 killed=50 survivors=1 source_sha256_restored=true      (runner exit code 1 — see SF-2)
```
