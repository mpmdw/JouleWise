# 192 — S10 ROUND 6 + 7 read-only DELTA RE-AUDIT

Target: `b0377e76` (round 6, Astra xhigh, brief 189) and `cfeba22f` (round 7,
lead, delta 191 D1/D2) on `feat/2026-09-10-epoch-continuation`; parent of round
6 = round 5 `106244f9`. Read via
`git -C /Users/edr/code/JouleWise-wt-s10-continuation diff 106244f9 cfeba22f`;
all execution in the read-only export `/tmp/s10-r7-export`
(`git archive cfeba22f | tar -x`), `PYTHONDONTWRITEBYTECODE=1`, no `timeout`.
**No repository was modified and no git write command was run.** The brief said
the worktree was idle; it was not — the lead landed **round 8 (`2e798f87`,
00:24, counter-review 193)** while this audit ran. I verified its effect on
both should-fix items at the end: **S1 is already closed there**; **S2 is not**.
 The S10
worktree is `git status --porcelain` empty after my run;
`/Users/edr/code/JouleWise`, `/Users/edr/night-custody` and every other
worktree were untouched.

**Verdict: NOT CLEAN — 0 blockers, 2 should-fix, 6 nits.** Every item the brief
asked for is genuinely closed and mechanically pinned: the tolerance set is
sound under adversarial reading, the CLI now writes `ledger_snapshot` into real
hashed capture bytes, `OSError` details are relative, 187's SF-1'/N1/N3 all
landed with cuts, and 52 tests + 74 mutation cuts are green. Both should-fix
items are consequences the round created and did not sweep: one is a sentence
in the SAME contract paragraph round 6 rewrote (independently found and fixed
by round 8 while I was auditing — see S1) — **the third occurrence of the
doc-asserted-contract signature** (174 B1 → 191 D1/D2 → today), which fires the
standing escalation trigger.

---

## Question-by-question

### (1) The tolerated refusal-reason set

`joulewise/calibration_epoch_continuation.py:33-40` (`SNAPSHOT_STATE_REFUSALS`)
and the gate at `:274-277`:

```python
_require(set(ledger_snapshot.refusal_reasons) <= SNAPSHOT_STATE_REFUSALS
         and ("calibration_ledger_head_mismatch" not in ledger_snapshot.refusal_reasons
              or ledger_snapshot.is_governed_open_bracket_extension),
         "ledger_snapshot_invalid")
```

The full refusal vocabulary is 13 `reasons.add` literals plus 3 scan-level
`terminal_failure` values in `joulewise/calibration_ledger.py`. Tolerated:

| Reason | Produced at | Classification |
|---|---|---|
| `calibration_ledger_bracket_session_open` | `calibration_ledger.py:1722` (a session whose finalized slots are fewer than its declared slots and which has no abort receipt) | **STATE.** Purely a count comparison inside `_bracket_sessions_and_observations`; it asserts nothing about bytes, pins, digests or custody. An open session's finalized observations are deliberately withheld from `snapshot.observations` (`:1730-1740`), so it cannot inject evidence either. |
| `calibration_ledger_head_mismatch` | `calibration_ledger.py:2166` (physical head ≠ pinned head, and physical is not a proper prefix — that case is `…_rollback` at `:2164`) | **INTEGRITY in general**, tolerated only under `is_governed_open_bracket_extension` (`:399-440`), which itself requires `set(refusal_reasons) == {head_mismatch, bracket_session_open}` exactly, a committed pin, exactly one open session, and that **every** receipt past the committed pin either belongs to that session or is a CONTROL abandonment / append-intent row targeting it, with the first business row being that session's open event at its `capability_sequence`. |

Everything else refuses `ledger_snapshot_invalid`: `attempt_conflict` (`:1792`,
`:1808`), `baseline_missing` (`:2174`, `:2184`), `bracket_session_conflict`
(`:1633`, `:1647`, `:1651`, `:1670`, `:1690`, `:1703`, `:1854`),
`content_conflict` (`:1832`, `:1877`), `custody_invalid` (`:2192` and the
custody-store/`_custody_reasons` updates at `:2194`/`:2203`),
`head_uncommitted` (`:2155`), `malformed` (`:2125`, and `:1494`/`:1556` via
`:1559`), `missing` (`:2138`), `pending` (`:1812`), `recovery_required`
(`:1561`), `rollback` (`:2164`), plus the scan-level `chain_conflict` (`:1530`),
`operation_conflict` / `ungoverned_business` (`:1532-1538`) and any future
unknown string (the `<=` subset test is closed by construction).

**Can a tampered ledger end with only tolerated reasons? No — three
independent constructions have to fail simultaneously, and I chased each:**

1. *Editing a row in place.* `_valid_receipt_shape` recomputes the digest:
   `receipt.get("receipt_digest") != _receipt_digest(receipt)` →
   `calibration_ledger.py:1195`. Any content edit invalidates the row's shape,
   which sets `terminal_failure = calibration_ledger_chain_conflict` /
   `malformed` — not tolerated.
2. *Editing a row below the pin while a genuine open session exists above it.*
   The digest recompute above kills it first; and even absent that, with
   `physical_sequence == pinned_sequence` the tail is empty and
   `is_governed_open_bracket_extension` returns `False` (`bool(tail and …)`).
3. *Appending a forged tail.* The tail must be exactly one session's rows and
   that session must be the single **open** one. A forged session that
   finalizes all its declared slots stops emitting `bracket_session_open`, so
   the reason set becomes `{head_mismatch}` alone and `is_governed…` returns
   `False` (its `set(...) != allowed` guard). A forged *second* session breaks
   the `all(...)` same-`session_id` test. And an open session's rows never
   enter `snapshot.observations`, so they cannot satisfy the loader's
   `hidden_finalized_row` / `acknowledged_attempt_missing` cross-checks
   (`calibration_epoch_continuation.py:286-303`).

**Does the continuation's own session being open refuse? Yes, by
construction.** `:281` requires `session.state in TERMINAL_STATES and
session.state == evidence["session_state"]`; an open session fails both
conjuncts and returns detail `session_not_terminal_or_state_mismatch`. Pinned by
`tests/test_epoch_continuation.py::test_continuations_own_open_session_still_refuses`
and by mutation cut C48 (`session.state in TERMINAL_STATES and …` → `True`),
killed. The widening direction is pinned by
`test_integrity_and_unknown_snapshot_refusals_remain_invalid`, which enumerates
**16** reasons — all 12 non-tolerated `reasons.add` literals, the 3 scan-level
terminal failures, and one invented `future_unknown_reason` — against both a
clean and a governed-extension base, and by cuts C45/C46/C47.

### (2) CLI routing and the 191 hand-off

- **Ordinary path now writes `ledger_snapshot` into real hashed bytes.**
  `scripts/validate_powermetrics_fiducial.py:1951-1955` loads one
  custody-verified snapshot before identity preflight; `:2008-2010` passes it to
  `_derive_preflight_systematic_screen_s(preflight_record=acceptance_preflight,
  ledger_snapshot=preflight_snapshot)` and `:1957-1959` to
  `_derivation_only_screen_basis`. Byte witness, not a stub:
  `tests/test_validate_powermetrics_fiducial_derivation_only.py:540` asserts
  `judged_epochs_basis == "ledger_snapshot"` inside the real
  `instrument_evidence.json` **and** `manifest.json` of a subprocess CLI
  capture, and `:653` does the same for `screen_basis`. 191's two tripwire
  assertions (`:533`, `:645`) flipped from `registry_pins_only` as predicted.
  Mutation cuts W22 (ordinary) and W23 (derivation-only) revert
  `ledger_snapshot=preflight_snapshot` → `None` and are both killed.
- **Is `registry_pins_only` still emitted in production? Effectively no — see
  nit N1.** The label is produced at `:415-417` only when `ledger_snapshot is
  None`, and it is only *observable* when a caller passes `preflight_record`.
  The three remaining snapshot-free production callers —
  `generate_g2a_probe_inputs.py:660`, `write_derivation_night_inputs.py:162-164`
  and the import-time constant at `:577` — all call with
  `preflight_record=None`, so no production path records
  `"registry_pins_only"` anywhere. It survives as a defensive default exercised
  only by direct-helper tests (`test_validate_powermetrics_fiducial.py:137`,
  `:169`). It **is** documented — `powermetrics_fiducial.md:178-183` correctly
  hedges "use `registry_pins_only` **when requesting a record**".
- **Same-commit rule: MET.** `git show --stat b0377e76` shows
  `docs/contracts/epoch_continuation.md`,
  `docs/contracts/powermetrics_fiducial.md` and the code in one commit, and the
  census row `epoch_continuation.md:328` was rewritten there ("the CLI supplies
  its custody-verified snapshot; identity-only callers omit it and explicitly
  skip the session cross-check"). 191's hand-off demand is satisfied — except
  for the leftover sentence in S1 below.

### (3) N1 — the `OSError` detail string (executed)

Ran against the export with a registry entry whose file is absent:

```
{"reason": "calibration_epoch_continuation_invalid", "continuation_id": "c1",
 "detail": "FileNotFoundError: configs/calibration/missing_continuation.json"}
```

No absolute path, no OS message ("No such file or directory" is gone), no
second filename. Four more shapes executed: no `relative_path` (falls back to
`relpath` against the repo root — same string); an **absolute**
`relative_path` in the registry (rejected by the `Path(relative).is_absolute()`
guard, falls back — same string); a directory target
(`IsADirectoryError: configs/calibration`); and an `OSError` carrying a second
filename `/private/other-secret`, which never appears in the detail (the test
at `tests/test_epoch_continuation.py:210-224` asserts exactly this, over both
error classes × three `relative_path` values). Cuts C49 (`isinstance(exc,
OSError)` → `False`) and C50 (`Path(relative).is_absolute()` → `False`) killed.

### (4) 187's SF-1', N1, N3 — all present

- **SF-1' (contract names the surviving direction).** `epoch_continuation.md:74-80`
  now says the converse explicitly: "A hand-written, registry-pinned file can
  still promote an inside-envelope unresolved row to resolved, raising `m` and
  turning an INCONCLUSIVE night into a PASS; no published number can change …
  owner registration review remains the boundary". "that verdict flip" was
  replaced with "a FAIL→PASS flip", so the unpaid-work sentence is gone.
- **N1 (prepare's envelope gate unconditional).**
  `scripts/issue_epoch_continuation.py:139-142` drops `bool(unresolved_valid)
  and`; the message carries `none (all valid rows resolved)` when the list is
  empty. The counterfactual cut C51-family (`not envelope_holds_over_all_valid(...)`
  → the old `bool(unresolved_valid) and not …`) is killed by
  `test_one_quantum_above_level_fails_without_writing`. See should-fix S2 for
  the exit-code consequence.
- **N3 (named null-bound detail).** `calibration_epoch_continuation.py:259-260`
  and `issue_epoch_continuation.py:124` both refuse
  `slots.<slot>.b_fiducial_s_required_for_valid_row`; the loader test at
  `test_epoch_continuation.py:762` changed from the old generic
  `slots.b_fiducial_s` to `slots.d12.b_fiducial_s_required_for_valid_row`, and
  `test_prepare_valid_null_bound_names_slot` pins the prepare side at rc 3 with
  nothing written. Two cuts, both killed.

### (5) Round 7 (lead)

- **String and test agree.** `scripts/write_derivation_night_inputs.py:181-186`
  now raises "this machine's identity epoch is one the acceptance at `<path>`
  already judges (its own epoch or an authenticated continuation), so this is an
  ORDINARY night, not a derivation night…". Both reachable callers — the
  same-epoch case and the continued-epoch case — reach this single `raise`, and
  `tests/test_write_derivation_night_inputs.py:225` asserts `"already judges"`
  (it was `"no identity field differs"`). 191's D1 is closed: the false first
  clause is gone and the replacement is true on both paths.
- **Runbook rows describe the judged-epoch condition.** All three D2 sites:
  glossary "Stale field" (`derivation_night_runbook.md:110-115`) now reads
  "differs from **every identity epoch the active acceptance judges** (its own,
  and any epoch an authenticated continuation has carried it onto) … including
  the case where a continuation already covers this machine"; the desk-inputs
  refusal row (`:668`) restates the new string and its Meaning column now names
  the continuation cause; the capture-writer
  `calibration_derivation_only_epoch_unchanged` row (`:1798`) adds "or a
  continued epoch" and the third operator cause.
- **`tests.test_docs_freshness` passes** (inside the regression below; 0 failures).

### (6) Regression and mutation — GREEN

```
$ cd /tmp/s10-r7-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
    tests.test_epoch_continuation tests.test_calibration_bracketing \
    tests.test_validate_powermetrics_fiducial_derivation_only \
    tests.test_validate_powermetrics_fiducial tests.test_write_derivation_night_inputs \
    tests.test_calibration_ledger tests.test_d078_reason_registry \
    tests.test_docs_freshness 2>&1 | tail -3
Ran 331 tests in 145.027s

OK (skipped=2)
rc=0
```

(The seat's V1 ran a 10-module superset and reported 339/OK; the two skips are
its disclosed F1, the D-079 import tests needing lead-reviewed inputs.)

```
$ PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py
cuts=51 killed=51 survivors=0 source_sha256_restored=true            rc=0
$ PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/writer_mutation_cuts.py
cuts=23 killed=23 survivors=0 source_sha256_restored=true            rc=0
```

The writer runner's new `IN_MEMORY_PATHS` mechanism (W09/W10/W20) is sound: for
`.py` targets it `exec`s the mutated source into the already-imported module in
a **fresh** subprocess interpreter; for the `.md` target it patches
`Path.read_text` for that one resolved path. Neither writes an out-of-scope
file, which is why the earlier "out of allowlist" exclusion is gone and all 23
now run. Sources restored (`source_sha256_restored=true`, and the S10 worktree
is clean).

### (7) SAME-SIGNATURE STATEMENT, rounds 1–7

| Defect class | Instances | Status |
|---|---|---|
| **File-asserted evidence** — a registered file asserting a fact the tool cannot replay | r3: excluding an over-screen row as "unresolved" could flip FAIL→PASS; r4: the converse INCONCLUSIVE→PASS direction; r6: a `valid` row with a null bound | **Closed by construction** in the FAIL→PASS direction: `envelope_holds_over_all_valid` runs over **all** valid rows, unconditionally, on **both** sides (loader `:265-266`, issuer `:139-142`), so resolution can only reduce `m`. **Accepted residual, now named**, in the INCONCLUSIVE→PASS direction (`epoch_continuation.md:74-80`) — the loader cannot replay primary bytes; issuer replay + owner registration review are the controls. Null bound **closed by test** both sides. |
| **Doc-asserted contract** — prose asserting a shape the code no longer has | r5 (174 B1): two homes for the key lists + a stale epoch-equality clause; r5 delta (191 D1/D2): the desk refusal string + three runbook rows; **r6: `powermetrics_fiducial.md:191-193`** | **Partly closed by test** — the artifact key lists are machine-pinned by `test_contract_documented_key_lists_equal_emitted_preflight_and_screen_basis` reading the live contract (cuts W18/W19 mutate the markdown alone and are killed). **Everything else in this class is closed only by manual sweep**, and the sweep missed again this round. **This is the third consecutive round carrying an instance — the standing escalation trigger.** |
| **Scope mis-location** — the fix a round needs is outside its `WRITE_SCOPE` | r5: D2's runbook rows were outside round 5's scope; r6: brief 189's scope again excluded `docs/phase_2/`, and three mutation cuts targeted out-of-scope files | **Closed by process, not by construction.** The lead took the runbook itself in round 7 (correct — smaller than the contract to delegate it), and the seat solved the cut problem in-scope with `IN_MEMORY_PATHS` rather than silently skipping. No unowned write occurred in either round (`unowned_dirty: []`, and `git show --stat` matches both pathspecs exactly). Residual: a brief that edits a contract's prose still has no mechanism forcing its operator-facing mirrors into the same scope. |

---

## SHOULD-FIX

### S1 — the one-home contract contradicts itself, in the paragraph round 6 rewrote (third instance of the doc-asserted-contract signature)

**Status: ALREADY CLOSED at `2e798f87` (round 8, 00:24), by counter-review 193,
after this audit began. Verified: the three lines below are gone and replaced by
"The capture writer supplies the custody-verified ledger snapshot it loads at
preflight …; `judged_epochs_basis` records `ledger_snapshot` on that path."
I am reporting it anyway because it was live at the audited head `cfeba22f`,
and because the same-signature count and the mechanism argument stand.**

`docs/contracts/powermetrics_fiducial.md:191-193` still ends the
`acceptance_preflight` paragraph with:

> Until the CLI supplies its ledger snapshot here, a file-authenticated
> continuation can pass capture preflight but fail the session cross-check at
> claim time.

Round 6 supplied it. Three sentences earlier, the **same paragraph**, edited in
the **same commit**, now says "The writer CLI loads its custody-verified
snapshot before identity preflight, passes it to both preflight helpers, and
records `ledger_snapshot`". A reader of the declared one home for the preflight
object gets both claims and no way to tell which is live. The direction is
safe — the stale sentence *understates* the guarantee, so nobody over-trusts a
capture — but this is precisely 174's B1 and 191's D1/D2 one more time, and it
is inside the file the round's own drift test reads.

Fix is one deletion. The structural point matters more: the drift test pins the
two JSON key lists and nothing else, so every *sentence* in this contract is
still guarded only by a human re-reading it, and three rounds running that has
failed. **Per the standing escalation trigger (same signature, consecutive
rounds), the next spend on this class should be a mechanism, not a fourth prose
round.** The cheapest mechanism that would have caught all three instances: a
`test_docs_freshness` assertion that the contract files contain no temporal
hedge — `"Until the CLI"`, `"currently"`, `"does not yet"`, `"for now"` — since
every instance of this class was a sentence describing a limitation that a
later round removed. That is a grep, it is deterministic, and it converts the
class from *closed by manual sweep* to *closed by test*.

### S2 — `prepare-candidate` exit 4 is now unreachable, and a FAIL night no longer prints the derived record the desk is told to take to Ed

**Status: still open at round 8.** `git show 2e798f87:docs/contracts/epoch_continuation.md`
still carries "Exit 4 remains the statistics FAIL mapping" at `:303`, and round 8
did not touch `scripts/issue_epoch_continuation.py`.

187's N1 was correct that dropping `bool(unresolved_valid) and` "costs
nothing" in safety. It is not cost-free in operator semantics, and the round
did not follow the consequence all the way out.

`retained` is appended only under `disposition == "valid" and resolved`
(`issue_epoch_continuation.py:128-136`) and `all_valid` only under
`disposition == "valid"` (`:123-126`), in the same loop — so `retained ⊆
all_valid`. `equivalence_statistics` returns `"fail"` only when `m >= 6` and
some retained value exceeds `level` or the retained spread exceeds `bracket`
(`calibration_epoch_continuation.py:127-129`). Either condition implies the
same violation over the superset `all_valid`, so
`envelope_holds_over_all_valid(all_valid, rule)` is already `False` and the
unconditional `_refuse` at `:139-142` fires **before** `statistics =
equivalence_statistics(retained, rule)` at `:143`. **No input can now reach
`VERDICT_EXITS["fail"] == 4`** (`:44`, consumed only at `:271`/`:273`).

Two consequences:

1. `epoch_continuation.md:299-302` says "Exit 4 remains the statistics FAIL
   mapping, but every screen violation now hits the unconditional envelope
   refusal before that mapping." True of the table, misleading about the
   world: the mapping is dead. An operator reading the contract will wait for
   an exit code that cannot occur.
2. **Evidence loss.** The old rc-4 path ran `print(json.dumps(record,
   indent=2))` at `:275` — the desk got the full derived record (verdict, `m`,
   retained min/max/range, every slot row) to attach to the written ruling.
   The new path exits 3 through `main`'s handler at `:342`, printing only
   `REFUSED: unresolved_valid_row_exceeds_envelope: unresolved slots: none (all
   valid rows resolved); the desk reports it to Ed for a written ruling` — a
   message that *instructs* a report to Ed while withholding the numbers the
   report is about. The seat's own test churn shows the swap:
   `test_one_quantum_above_level_fails_without_writing` and
   `test_range_above_screen_fails_even_when_every_value_meets_level` both moved
   from `(rc, error) == (4, "")` plus `json.loads(out)["verdict"] == "fail"` to
   `rc == 3` and `out == ""`; **zero** `rc == 4` assertions remain anywhere in
   `tests/test_epoch_continuation.py` (rc 5 / inconclusive is still live and
   tested at `:643`, `:735`, `:767`). Two more tests
   (`test_s9_*_witness_preserves_false_comparison`,
   `test_failed_nine_row_night_cannot_hide_three_finalized_rows_to_pass`) now
   have to `patch.object(issuer, "envelope_holds_over_all_valid",
   return_value=True)` to construct a FAIL record at all — an honest and
   well-commented workaround, but it is the signal that the FAIL branch is no
   longer reachable through production.

Neither consequence is a soundness hole: nothing is written, the refusal is
fail-closed, and the loader's identical gate is unchanged. The fix is small and
belongs with the science stop it serves — print the derived record (or at least
the all-valid extrema and the two screens) on the envelope refusal, and state
in the contract that exit 4 is retained for schema stability but is not
reachable while the envelope gate precedes the statistics.

---

## NITS

- **N1 — `registry_pins_only` is now a production-dead label.** All three
  snapshot-free callers pass `preflight_record=None`, so `:415-417`'s false
  branch is exercised only by direct-helper tests.
  `epoch_continuation.md:219-221` ("identity-only helper callers … retain the
  explicitly labelled `registry_pins_only` path") reads as if an artifact
  somewhere carries that label; `powermetrics_fiducial.md:178-183`'s "when
  requesting a record" is the accurate phrasing. Align the two, or delete the
  branch.
- **N2 — `_validate_reserved_bracket_slot` silently ignores its own
  `require_committed_pin` when handed a snapshot** (`:1345-1350`): the passed
  snapshot was loaded with the value hardcoded at `:1952`. Today every
  production construction of `_CaptureLedgerLifecycle` takes the `True`
  default, so the two agree and any future divergence would only make the
  pre-lease check stricter — but the parameter now lies about what governs the
  check. Assert the agreement or drop the parameter on that branch.
- **N3 — an out-of-repo registry path still puts ancestor directory names in
  hashed bytes.** Executed: a registry entry at `/Users/edr/secret-dir/x.json`
  yields `FileNotFoundError: ../../secret-dir/x.json`. Not absolute, so N1's
  stated obligation holds, and registry entries are owner-registered — but the
  guard tests `is_absolute()` only. `Path(relative).parts[0] != ".."` would
  close it.
- **N4 — the registry's `relative_path` is trusted without cross-checking
  `entry["path"]`.** A registration whose two fields disagree produces a detail
  naming a file that is not the one that failed. Owner-review-bounded; one
  `assert`-shaped `_require` at registration would close it.
- **N5 — `epoch_continuation.md:212`**: "Claim-time bracket evaluation always
  requires a valid snapshot and never uses it." The referent of "it" is the
  weaker path, but the nearest noun is "a valid snapshot", so the sentence
  reads as self-contradictory. Pre-existing (unchanged context in this diff);
  flagged because it sits two lines above the paragraph this round rewrote and
  fails the writing standard's no-unpaid-work test.
- **N6 — the continued-epoch desk test pins only the trailing clause.**
  `test_continued_epoch_is_an_ordinary_night_and_writes_no_derivation_inputs`
  asserts `"ORDINARY night, not a derivation night"`; the new `"already
  judges"` clause is pinned by the sibling same-epoch test at `:225`. Since
  both paths reach one `raise`, coverage is real today — but if the two cases
  ever get distinct messages, the continuation branch reverts to unpinned. One
  extra `assertIn` closes it.

---

## Honesty check on report 190

The envelope declares `status: clean` / `completion: complete` with
`head_start == head_end == 106244f9`, i.e. the seat reports no commit while the
audited commit is `b0377e76`; the 11 `pathspec` entries match `git show --stat
b0377e76` exactly (11 files, +371/−75), `unowned_dirty: []` is accurate. V1's
"Ran 339 … OK (skipped=2)" is consistent with my 331-test subset; V2/V3's
51/51 and 23/23 I reproduced independently. The "Verification notes" disclosure
about W09/W10/W20 moving to in-memory mutation is accurate and I verified the
mechanism. The residual-risk paragraph states the INCONCLUSIVE→PASS shape
correctly. **Nothing in 190 overstates what landed**; what it omits is the
exit-4 consequence of its own N1 fix (S2) and the sentence it left behind in
the contract it edited (S1).

## Footprint

Read-only. Export `/tmp/s10-r7-export`; logs `/tmp/s10r7-regression.log`,
`/tmp/s10r7-mut1.log`, `/tmp/s10r7-mut2.log`. No repository was written to and
no git write command was run.

*Branch head moved during this audit: `cfeba22f` (audited) → `ed4936c7` (merge
of `origin/main`) → `2e798f87` (round 8). The worktree is clean at `2e798f87`;
nothing I ran touched it.*
