# 202 — S10 round 11 + 11b READ-ONLY FRESH-EYES REVIEW (gate row 10)

Target: `7aedaa28` (round 11) and `be67a876` (round 11b) on
`feat/2026-09-10-epoch-continuation`; baseline `4c04f53e` (round 10, fresh-eyes 199).
Diff read with `git -C /Users/edr/code/JouleWise-wt-s10-continuation diff 4c04f53e be67a876`;
**all execution in the read-only export `/tmp/s10-r11-export`** (`git archive be67a876 | tar -x`),
`PYTHONDONTWRITEBYTECODE=1`, no `timeout`. **No repository, worktree or checkout was modified; no
git write command was run.** `/Users/edr/code/JouleWise`, `/Users/edr/night-custody` and every other
worktree were untouched. The only file I wrote is this report.

**Verdict: NOT CLEAN — 0 blockers, 1 should-fix, 3 nits.**
Both of 199's should-fix items are genuinely closed: the mutation gate is **GREEN** (51/51,
runner rc 0) and the stale contract paragraph is gone, including the dead
`none (all valid rows resolved)` string. The one should-fix is a single **causal clause** inside the
newly written paragraph that contradicts the sentence three lines above it and is falsified by a
passing test in this very suite.

---

## (1) The rewritten contract paragraph — TRUE except one clause

`docs/contracts/epoch_continuation.md:84-96`. Claim by claim, against the code in the export:

| Contract claim (line) | Code | Verdict |
|---|---|---|
| "The LOADER refuses … unconditionally and with or without a ledger snapshot, with detail `unresolved_valid_row_exceeds_envelope`" (`:85-88`) | `joulewise/calibration_epoch_continuation.py:265-266` — `_require(envelope_holds_over_all_valid(lexemes_all_valid, rule), …)`, no guard, no snapshot in scope; the snapshot cross-check begins at `:272` | TRUE |
| "The PREPARATION tool first computes the ruling's verdict over the retained values" (`:87-89`) | `scripts/issue_epoch_continuation.py:143` `statistics = equivalence_statistics(retained, rule)` precedes the gate at `:150` | TRUE |
| "a FAIL prints the derived record and exits 4, an INCONCLUSIVE prints it and exits 5, and neither writes a candidate" (`:89-91`) | `VERDICT_EXITS = {"pass": 0, "fail": 4, "inconclusive": 5}` (`:50`); `if rc: print(…); return rc` before the write block (`:296-299`) | TRUE |
| "Only when the retained values PASS while an unresolved valid bound breaks the envelope does preparation refuse — exit 3, … naming the unresolved slots" (`:90-93`) | gate `:150` is exactly `statistics["verdict"] == "pass" and not envelope_holds_over_all_valid(all_valid, rule)`; `ContinuationRefusal` → exit 3; message joins `unresolved_valid` (`:151-153`) | TRUE — and the slot list is provably non-empty (see below) |
| "because that is the one case where it would otherwise write a candidate **the loader would accept**" (`:93-96`) | the loader refuses precisely that file | **FALSE — SF-1** |
| "The two gates agree on every night that could be continued: a candidate is written only when both hold" (`:96`) | write happens only at `verdict == "pass"` with the envelope holding over `all_valid`, which is the loader's own predicate | TRUE |

**"naming the unresolved slots" can never print an empty list.** `verdict == "pass"` requires every
retained value `<= level` and `max-min <= bracket` (`calibration_epoch_continuation.py:127-128`),
which is exactly `envelope_holds_over_all_valid` over the retained multiset (`:102-104`). If every
valid row were resolved, `all_valid == retained` (`issue_epoch_continuation.py:129-142`), so the
envelope could not fail. Hence PASS + envelope-fail ⟹ at least one valid row unresolved. The
round-10 head's dead fallback string is therefore correctly deleted rather than reworded.

**The `none (all valid rows resolved)` string is gone repo-wide.**
`grep -rn "none (all valid rows resolved)" /tmp/s10-r11-export` → no matches (rc 1).

---

## (2) The omission-tolerance paragraph vs `_crosscheck`

`scripts/issue_epoch_continuation.py:252-254`:

```python
optional_checked = {
    "equivalence_record.reference_envelope": {"acceptance_file_sha256", "screen_rule"},
}.get(field, set())
```

Exactly two keys, under exactly one path, applied only as an **omission** skip
(`if key in optional_checked and key not in actual: continue`, `:258-259`); a present value falls
through to `_refuse(key not in actual …)` and the recursive `_crosscheck`, so a wrong or null value
refuses by name. The contract sentence at `:319-323` — "Two provenance fields the desk tool records
— the acceptance artifact's byte digest and the validator's registered screen rule — are checked
whenever the witness carries them (a wrong value refuses by name) and tolerated when an older record
omits them" — **matches the mechanism exactly**, and the "Two" carries the exclusivity. One
precision nit on the naming (N1). The file `scripts/issue_epoch_continuation.py` is byte-unchanged
between `4c04f53e` and `be67a876`, so 199's executed matrix for this behaviour still holds at this
head without re-running it.

---

## (3) Mutation gate — GREEN, C49 is the verdict guard and is killed

```
$ cd /tmp/s10-r11-export && PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile \
    tests/fixtures/epoch_continuation/mutation_cuts.py
py_compile rc=0
```

(Round 11 alone did NOT compile: `7aedaa28` left a dangling first tuple line, which `be67a876`
removes — `git show be67a876` is exactly that one-line deletion. The fix is correct and minimal.)

```
$ cd /tmp/s10-r11-export && PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py
C49 KILLED derive_record: 'statistics["verdict"] == "pass" and not envelope_holds_over_all_valid(all_valid, rule)'
    -> 'not envelope_holds_over_all_valid(all_valid, rule)' | test_a_failing_night_prints_its_derived_record_and_exits_4_without_writing
cuts=51 killed=51 survivors=0 source_sha256_restored=true
RUNNER_RC=0
```

Yes on both questions: C49 is now the **verdict-guard** cut (drop `statistics["verdict"] == "pass"`,
restoring the round-8 unconditional refusal) and it is killed by
`a_failing_night_prints_its_derived_record_and_exits_4_without_writing`. The kill is genuine, not
an error-as-kill: that test builds 3 rows at `level + 0.001` + 9 at `0.025`, all resolved
(`tests/test_epoch_continuation.py:386-397`), so the mutant refuses at rc 3 and the
`assertEqual(rc, 4)` fails — and the runner counts a kill only on
`result.failures and not result.errors` (`mutation_cuts.py:147`). **199's SF-2 is CLOSED**;
`source_sha256_restored=true` and the runner's own post-cut digest assertions confirm the export's
sources are unmodified.

---

## SHOULD-FIX

### SF-1 — `docs/contracts/epoch_continuation.md:93-96` states the loader would ACCEPT the candidate it in fact refuses

> "… because that is the one case where it would otherwise write a candidate **the loader would
> accept**."

The loader's envelope gate is unconditional over the file's disclosed valid bounds
(`joulewise/calibration_epoch_continuation.py:265-266`) — the sentence at `:85-88` of the same
paragraph says so. A candidate written under exactly this condition (retained PASS, an unresolved
valid bound outside the envelope) is therefore **refused** by the loader, not accepted. The
paragraph contradicts itself eleven lines apart.

Executed this session, not argued:
`tests.test_epoch_continuation.EpochContinuationTests.test_failed_nine_row_night_cannot_relabel_over_level_rows_unresolved`
(`tests/test_epoch_continuation.py:434-457, 459-460`) builds precisely that file — a FAIL night whose
three over-level rows are relabelled `anchor_v3_resolved=False`, resealed with
`verdict="pass"`, `m=6`, `retained_range_s="0.000"` — pins it, and asserts the loader returns
`loaded == ()` with detail `unresolved_valid_row_exceeds_envelope`, **with and without a ledger
snapshot**:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_continuation.EpochContinuationTests\
.test_failed_nine_row_night_cannot_relabel_over_level_rows_unresolved
Ran 1 test in 2.119s    OK
```

The true reason for the prepare-side gate is defence in depth plus not emitting a file at all: a
FAIL/INCONCLUSIVE night writes nothing, so PASS is the only branch where the refusal has anything to
prevent. Suggested clause: "… because that is the one case where preparation would otherwise write a
candidate at all — a file the loader would then have to refuse." One clause, one file. This is the
**fifth** instance of the doc-asserted-contract signature (174 B1 → 191 D1/D2 → 196 A → 199 SF-1 →
here); note the shape shifted — round 11 correctly swept the whole doc for the stale *rule*
(`grep` for the refusal string returns only true statements at `:59-60`, `:87-88`, `:92`, `:307-308`,
and the only other hits repo-wide are frozen process traces), and the survivor is a **rationale**
clause written fresh in the same commit. The sweep worked; what was not checked is the new prose's
own internal consistency.

---

## NITS

- **N1** `docs/contracts/epoch_continuation.md:319-323` — the two tolerated fields are named in
  prose ("the acceptance artifact's byte digest", "the validator's registered screen rule") but not
  by path. The mechanism is keyed on `equivalence_record.reference_envelope` only
  (`scripts/issue_epoch_continuation.py:253`), while a **top-level** `acceptance_file_sha256` of the
  same name also exists in the record and is governed by a different mechanism (the
  `if key in witness` recognition loop, `:288-292`). A reader cannot replicate the rule from the
  text without guessing the nesting level. Naming them
  `reference_envelope.acceptance_file_sha256` / `reference_envelope.screen_rule` fixes it.
- **N2** `tests/fixtures/epoch_continuation/mutation_cuts.py:113-115` — the cut set still has no cut
  that **deletes** the envelope test itself. Both the old C49 (add `bool(unresolved_valid) and …`)
  and the new one (drop the verdict guard) mutate the *guard*; the defence's own removal
  (condition → `False`) is unpinned. 199 verified by hand that such a mutant dies to
  `test_prepare_refuses_unresolved_valid_row_widening_range_without_writing`, so this is coverage
  bookkeeping, not a live hole — adding it makes the gate assert what the round-4 work was for.
  (Also unchanged: the runner is invoked by no test and no CI file, so the gate is manual-run only.)
- **N3** carried forward from 199 N2, untouched by round 11: `tests/test_epoch_continuation.py:67`
  `run_cli` duplicates `run_cli_of` at `:934`, which is defined after its only caller at `:913`, and
  `epoch_equivalence_check` is imported inside a test body. (199 N1, the duplicate `redirect_stdout`
  import, **is** fixed — `:5` retains the combined import and the stray line is gone.)

---

## (4) Temporal hedges describing limitations the code no longer has — NONE FOUND

Swept both files for `until | currently | does not yet | not yet | now | no longer | still | for now |
at present | planned | pending | will be | TODO`. Every hit is a true present-tense statement, not a
stale limitation:

| Hit | Status |
|---|---|
| `epoch_continuation.md:76` "Resolution can **now** reduce `m` but cannot produce a FAIL→PASS flip" | CURRENT — true at both sites; a relabelled over-screen row drops out of `retained` but the PASS branch then refuses (`issue_epoch_continuation.py:150`) and the loader refuses the file (`:265`) |
| `epoch_continuation.md:234` "Continued epochs are **no longer** new epochs for this guard" | CURRENT — describes the derivation-only epoch guard as implemented |
| `epoch_continuation.md:174, 296, 338, 340` ("pending attempt", "a later derivation session", "planned epoch") | CURRENT — all describe live behaviour, not deferred work |
| `powermetrics_fiducial.md:88-91` "**until** that variant is validated, T3 remains an explicit limitation" | CURRENT — T3 load-regime transfer is a genuine open limitation with a registered roadmap mitigation |
| `powermetrics_fiducial.md:95-97` "implemented and running, and Ed may **still** veto or amend" | CURRENT — deliberate both-hold status line for cold gate 46 |
| `powermetrics_fiducial.md:122, 179, 185, 263, 267, 391, 423` ("still authenticates/refuse/apply/require/licenses/may still run") | CURRENT — each restates a live check |
| `powermetrics_fiducial.md:358` "the **currently** supported `ac_high_power` classification" | CURRENT — one classification is in fact the only one supported |

CLEAN for this question.

---

## (5) Regression run — pasted verbatim

```
$ cd /tmp/s10-r11-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_epoch_continuation tests.test_docs_freshness 2>&1 | tail -3
Ran 94 tests in 190.308s

OK
```

rc 0. `test_docs_freshness` green, so the contract edits satisfy every pinned-doc assertion.
