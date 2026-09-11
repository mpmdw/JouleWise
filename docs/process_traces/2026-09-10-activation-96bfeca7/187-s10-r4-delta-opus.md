# 187 — S10 round 4 DELTA re-audit (Opus, read-only)

Target `426385467cc1f89f3902f1df70b3e6832e26a24a` ("S10 round 4"), parent/round 3
`6d838a102fa867338e91c398b8adf44cbfb09603`, branch `feat/2026-09-10-epoch-continuation`.
Everything executed from a read-only export at `/tmp/s10-r4-export`
(`git archive $R4 | tar -x`), `PYTHONDONTWRITEBYTECODE=1`, no `timeout` wrapper.
Nothing written in any repo, no git write command; the S10 worktree,
`/Users/edr/code/JouleWise`, `/Users/edr/night-custody` and every other worktree
untouched. Only this file was written.

**Verdict: CLEAN on the brief — 0 blockers, 0 should-fix on delta 179's SF-1
(it is CLOSED), 1 should-fix that is documentation-only, 3 nits.**
Every one of the brief's seven questions was re-executed, not read.

---

## (6) Regression + mutation, first (everything below depends on it)

```
cd /tmp/s10-r4-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  tests.test_epoch_continuation tests.test_calibration_bracketing \
  tests.test_validate_powermetrics_fiducial_derivation_only 2>&1 | tail -3
```
```
Ran 161 tests in 102.969s

OK (skipped=1)
```
rc 0. (The seat's V1 reported 193 because it added `test_docs_freshness` +
`test_mint_policy_resolver_guard`; I ran `tests.test_docs_freshness`
separately — `Ran 31 tests`, `OK`, rc 0, so the contract edit does not break
freshness pins.)

Mutation runner in the export (mutates the export only):
```
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py
→ cuts=42 killed=42 survivors=0 source_sha256_restored=true   (rc 0)
```
The seat's 42/42 reproduces. The 18 new cuts are honest and branch-isolating:
each screen separately (`value <= level` → `True`/`level <= level`/`value <= value`;
`max-min <= bracket` → `True`/`bracket <= bracket`/`max-min <= max-min`), the
boundary direction (`<=` → `<`, killed by the equality test), the operand
collapse in BOTH directions (`max(values)`→`min(values)` and
`min(values)`→`max(values)` — the rule from the 09-10 operand-collapse lesson),
the "no minimum count" clauses, the precision constant (`80 + sum(...)` → `28`),
the issuer's collection line (`all_valid.append(lexeme)` → resolved-only) and its
refusal, plus N1's isolated `hidden_finalized_row` cut and N2's key-set cut.
`envelope_holds_over_all_valid` is patched in both modules by the runner
(`tests/fixtures/epoch_continuation/mutation_cuts.py:119-123`), so the issuer cannot evade a cut by import aliasing.

---

## (1) Forgery (a) re-executed — REFUSED

`/tmp/s10_r4_loader_demo.py`, delta 179's fixture rebuilt against the r4 export
(12 declared slots, 9 filled, session aborted `window_exhausted`, six captures at
`0.025`, three at `level + 1 quantum`, three at `0.025`):

```
[prepare fail-night] rc=4 wrote_file=False           m=9 verdict=fail max=0.032898493715363
  forged stats m=6 natural_verdict=pass -> file claims pass
  [a-unresolved-madeup-detail] file_verdict=pass file_m=6 loaded=0
      refusal=['unresolved_valid_row_exceeds_envelope']
      | no-snapshot: loaded=0 refusal=['unresolved_valid_row_exceeds_envelope']
  [b-relabel-ordinary-invalid] loaded=0 refusal=['acknowledged_row_disagrees']
  [B1-hide-three-rows]         loaded=0 refusal=['hidden_finalized_row']
```
The delta-179 acceptance is gone. The refusal fires **with and without a ledger
snapshot** — it is the first verdict-bearing content check in this reader that
does not depend on the snapshot (see N2). Neighbours (b) and B1 still refuse on
the snapshot path, so round 4 added a lane without removing one.

`prepare-candidate` on the same shape of night (one unresolved row over the
screen), `/tmp/s10_r4_boundary_demo.py`:
```
[over-level] rc=3 wrote_file=False stdout_bytes=0
  stderr='REFUSED: unresolved_valid_row_exceeds_envelope: slots.d12;
          the desk reports it to Ed for a written ruling'
```
rc 3, empty stdout, no file, slot named. (The nine-row FAIL night itself still
exits 4 with the record on stdout and no file, as before — the tool's
unresolved-envelope refusal is the *new* exit for the unresolved shape.)

## (2) Honest night, one valid-but-unresolved row INSIDE the envelope — CONFIRMED

```
[at-level] rc=0 wrote_file=True  m=11 verdict=pass
  written: unresolved=[('d12', '0.032898493715362')]     (12 valid rows, 11 resolved)
  [load at-level] file_verdict=pass m=11 loaded=1 refusal=[]
```
Authenticates, `m` excludes the unresolved row, `prepare-candidate` writes the
candidate. A second honest shape (11 rows at `0.025`, one unresolved at
`0.0262`) also prepared rc 0 with `m=11`.

## (3) Boundary — CONFIRMED, all three, executed

Rule values from the registry: `level = 0.032898493715362`, `bracket = 0.009724`.

| case | construction | result |
|---|---|---|
| exactly at the level screen | 11 resolved at `level − bracket`, unresolved at `level` (both screens at exact equality) | prepare rc 0, file written, loads with zero refusals |
| one quantum above (`1e-15`) | same, unresolved at `level + 1e-15` | prepare rc 3, no file, `unresolved_valid_row_exceeds_envelope: slots.d12`; forging the same file at the loader → refusal `unresolved_valid_row_exceeds_envelope` |
| unresolved row alone widens the spread | 11 resolved at `level − bracket − 1e-15` (level screen holds for every row), unresolved at `level` → all-valid spread `0.009724000000001 > 0.009724` | prepare rc 3, no file, slot named; the loader forgery of the equivalent honest FAIL-by-range night (high row re-labelled unresolved, `m` 12→11, retained range `0E-15`, level branch holding) → refusal `unresolved_valid_row_exceeds_envelope` |

So both screens are independently live, the comparison is `<=` (equality passes),
and the mutation table kills the `<` variants. The seat's own tests cover the
same three points plus a combined-extrema case (`d11`+`d12` each inside the
bracket alone, jointly outside) and a below-minimum case.

## (4) `equivalence_statistics` — UNCHANGED in semantics

`git diff $R4^ $R4 -- joulewise/calibration_epoch_continuation.py` touches only
`SLOT_KEYS`, the new `envelope_holds_over_all_valid`, and
`authenticate_epoch_continuation`. The function body, its `m`, min/max/range,
`MINIMUM_RETAINED` gate and verdict ladder are byte-identical; it is still fed
exactly the RETAINED lexemes (`disposition == "valid" and anchor_v3_resolved`),
and the loader still re-derives all five fields and compares them with type to
the file. The new check is a separate `_require` placed *before* it, exactly as
the brief specified. `INCONCLUSIVE` still keys on `m < 6`, executed:
a night of 5 resolved + 7 unresolved (all inside the envelope) prepares rc 5,
`m=5`, `verdict=inconclusive`, no file.

## (5) Strict key set — CONFIRMED, and the contract equals the code

```
[extra-key]                    loaded=0 refusal=['slots.keys']
[missing-key (anchor_v3_detail)]  loaded=0 refusal=['slots.keys']
[missing-key on an unfinalized slot] loaded=0 refusal=['slots.keys']
```
Mechanical comparison of the contract's list against `SLOT_KEYS`:
```
contract keys: ['anchor_v3_detail','anchor_v3_resolved','attempt_id','b_fiducial_s',
                'content_id','disposition','instrument_evidence_sha256',
                'manifest_sha256','slot']
code  keys   : (identical)          EQUAL = True
```
The check is ordered correctly — `isinstance(slots, list)`, then per-slot
`isinstance(slot, dict) and set(slot) == SLOT_KEYS`, and only then
`[slot["slot"] for slot in slots] == declared` — so a malformed `slots` cannot
raise `KeyError`/`TypeError` before the named refusal. The seat's test sweeps all
12 slots × (each of 9 keys deleted + one extra key) = 120 subtests.

---

## (7) SAME-SIGNATURE STATEMENT — FAIL→PASS is closed; INCONCLUSIVE→PASS is not

Walking every field of `evidence.slots[*]` again at round 4
(`joulewise/calibration_epoch_continuation.py`, line numbers read from the export):

| field | status at r4 | where |
|---|---|---|
| *(key set)* | **NEW — checked**: every slot object must carry exactly the nine documented keys; extra or missing refuse `slots.keys` | `:220-222` (`SLOT_KEYS`, `:32-36`) |
| `slot` | checked — equals `evidence.declared_slots`, which equals `session.declared_slots`; membership both directions | `:218, :223, :268, :275-280` |
| `attempt_id` (finalized) | checked — `(slot, attempt_id)` set equality with the ledger session, per-row identity, session ownership | `:271-277, :283-285` |
| `attempt_id` (unfinalized) | checked — must be null and the slot ledger-unfinalized | `:237-242, :275-276` |
| `content_id` | recomputed from the two hashes and ledger-compared | `:245, :286` |
| `manifest_sha256` / `instrument_evidence_sha256` | effectively checked — SHA-256 preimages of `content_id` | `:244-245, :286` |
| `disposition` (finalized) | ledger-compared for every finalized row, retained or not — **snapshot path only** (see N2) | `:287-288` |
| `disposition` (unfinalized) | checked — `window_exhausted`/`no_row`, only when aborted | `:237-242` |
| `b_fiducial_s` (valid) | ledger-compared to `exact_bound_lexeme_s` (snapshot path), **and now bound by the envelope on EVERY valid row regardless of resolution**; a valid row must now supply a finite non-negative decimal | `:249-255, :288` |
| `b_fiducial_s` (unfinalized) | checked — must be null | `:237-242` |
| `anchor_v3_resolved` | **STILL FILE-ASSERTED** — but the exploitable direction has narrowed: `true→false` can now only *lower* `m` (never evade a screen), while `false→true` can *raise* `m` | `:232, :252-253` |
| `anchor_v3_detail` | file-asserted; must be null when resolved, non-empty when a valid row is unresolved; content unverified | `:233-236` |

Derived quantities (`m`, min, max, range, verdict) are still re-derived and
compared; the file's verdict must additionally be literally `"pass"` (`:195`),
so FAIL and INCONCLUSIVE continuations never load at all.

**Can any field still flip FAIL→PASS? No.** A FAIL is by definition a valid set
that breaks a screen; every valid row's bound is now inside the envelope check,
and each of those lexemes is ledger-pinned (snapshot path) and disclosed in
plain text. Excluding a row by asserting non-resolution no longer removes it
from the screens; re-labelling its disposition is caught by
`acknowledged_row_disagrees`; deleting the row is caught by `hidden_finalized_row`
and the two converse set checks. All three re-executed above.

**Can it flip INCONCLUSIVE→PASS? YES — executed.** A night of 5 resolved +
4 unresolved valid rows, all inside the envelope, honestly exits `rc 5`
`m=5 inconclusive` and writes nothing. Flipping ONE unresolved row's
`anchor_v3_resolved` to `true` (and its detail to null), re-deriving the
statistics, and re-sealing gives:
```
[promote-one-unresolved] file_verdict=pass file_m=6 loaded=1 refusal=[]
  *** ACCEPTED *** m=6 verdict=pass cross_check=verified_terminal_derivation_session
```
What that requires, precisely:
1. **Bypassing the tool entirely.** `scripts/issue_epoch_continuation.py`
   computes `resolved, detail = anchor_v3_replay_outcome(evidence)` from the
   capture's primary bytes (`scripts/issue_epoch_continuation.py:105`); an issued candidate can never contain the
   promotion. The forger must hand-write the JSON and recompute
   `derivation_sha256`.
2. **Getting the file registered.** `EPOCH_CONTINUATION_REGISTRY` pins the
   file's SHA-256; authentication refuses `continuation_unregistered` /
   `continuation_file_sha256` otherwise. That is a tracked, owner-reviewed edit.
3. **Promoting only rows that pass the envelope and belong to the continued
   epoch.** The promoted row's bound is ledger-pinned and already inside both
   screens, and promotion newly subjects it to `acknowledged_identity_epoch`
   (`:289-290`), so it must genuinely be a same-epoch capture.

So the residue is bounded to: *a registered, hand-edited file can claim that an
anchor-v3 replay succeeded for a capture where it did not, raising `m` over the
six-row minimum using bounds that are all real, all ledger-pinned, all inside the
published envelope, and all from the continued epoch.* It cannot change a single
published number, only the count of captures asserted to have a validated clock
anchor. That is materially weaker than the FAIL→PASS class and is the direction
the magistrate's ruling deliberately left open (the loader cannot replay bytes).
Same signature? No: the r3 signature was "exclusion can hide a failing bound",
and that is dead. This is a different, narrower shape.

---

## SHOULD-FIX (documentation only)

### SF-1' — the contract states the closed direction and is silent on the open one

`docs/contracts/epoch_continuation.md` (new paragraph): "Resolution can now
reduce `m` but cannot produce that verdict flip." A reader takes that as *no*
resolution-driven verdict flip. The surviving direction —
asserting resolution on rows that did not resolve raises `m` and can turn an
INCONCLUSIVE night into a PASS — is not named anywhere in the contract, and by
the writing standard's first-use test the sentence does unpaid work: "that
verdict flip" silently means only FAIL→PASS. One sentence fixes it, e.g. "The
converse direction remains file-asserted: a registered file that claims
resolution for a capture whose replay did not resolve raises `m` and can turn an
INCONCLUSIVE night into a PASS. Only the issuer's replay of primary bytes and
the owner's registration review bound that; every bound so promoted is still
ledger-pinned and inside the envelope." No code change — there is no
machine-checkable close available to a reader that cannot replay bytes.

## NITS

**N1 — the prepare-side gate is conditional where the loader's is unconditional.**
`scripts/issue_epoch_continuation.py:136-140` refuses only when
`bool(unresolved_valid) and not envelope_holds_over_all_valid(...)`; the loader
requires the envelope unconditionally. Today these are equivalent: with every
valid row resolved, `all_valid == retained`, so an envelope violation is exactly
a `fail`/`inconclusive` verdict, which exits 4/5 and writes no file, and the
loader independently requires `verdict == "pass"`. I checked each arm. But the
equivalence is a *theorem about `equivalence_statistics`*, not a local property;
if the statistics rule is ever relaxed, the conditional gate silently stops
covering. Dropping `bool(unresolved_valid) and` costs nothing and removes the
coupling (the refusal message would then need a slot list that can be empty).

**N2 — the capture-preflight path still authenticates without a ledger, and two
older forgeries load there.** `scripts/validate_powermetrics_fiducial.py:402`
calls `acceptance_judged_epochs(artifact, ledger_snapshot=None, …)` (basis
`registry_pins_only`, the round-2 design, recorded in both capture artifacts).
Executed on that path: `[B1-hide-three-rows] loaded=1 refusal=[]` and
`[b-relabel-ordinary-invalid] loaded=1 refusal=[]` — i.e. hidden rows and
re-labelled dispositions are NOT caught when the snapshot is absent; only
`ledger_cross_check == "skipped_no_ledger_snapshot"` records the degradation.
Pre-existing and out of brief 181's scope; I raise it only because round 4's
envelope check is the first verdict-bearing content check that survives on that
path, which makes the remaining asymmetry worth a one-line note in the contract
(or a future round requiring a snapshot wherever a judged epoch gates a
capture). The acceptance-evaluation path
(`joulewise/calibration_bracketing.py:2058`) does pass the snapshot.

**N3 — a `valid` ledger row with a null bound is now refused with a generic
detail.** The loader now calls `_decimal(slot["b_fiducial_s"], "slots.b_fiducial_s")`
for every valid row (previously only for retained ones), and the issuer does the
same at `scripts/issue_epoch_continuation.py:123-124`. `joulewise/calibration_ledger.py:975` (the finalized-receipt shape check) permits a finalized row
with `disposition == "valid"` and `exact_bound_lexeme_s is None`, so such a night
now exits rc 3 with detail `slots.dNN.b_fiducial_s` rather than a named
envelope/ledger-shape reason. The tightening is correct and is stated in the
contract ("Every valid row must therefore supply a finite, nonnegative decimal
bound") and tested; only the operator-facing detail string is opaque.

Refuter 170's N1 (`check` picks the acceptance from the untrusted candidate),
N2 (`no_row` candidate), N3 (hand-typed operative digits in contract prose)
remain open as filed; round 4 did not touch them. Delta 179's N1 (isolated cut
for the unfinalized-absence converse line, now `:275-276`) and N2 (strict key set) are both CLOSED.

## Footprint

Read-only. Export `/tmp/s10-r4-export`; scratch scripts
`/tmp/s10_r4_loader_demo.py`, `/tmp/s10_r4_boundary_demo.py`; logs
`/tmp/s10-r4-tests.log`, `/tmp/s10-r4-mutation.log`. Export source hash after
the mutation run: `joulewise/calibration_epoch_continuation.py` =
`604ae356467b2c7ed9fbab37668d0889f29d8266a9635ba8995128a963a58250`
(runner reported `source_sha256_restored=true`). No repository was written to
and no git write command was run.
