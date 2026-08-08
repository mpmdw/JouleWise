# Opus post-merge counter-review — D-117 U1 (0564216) and U3 (d6683bf)

Two lenses supplied that the pre-merge gate skipped: **Lens A — overbuild / merge-ability
prune** and **Lens B — what the Sol contract+execution lenses structurally would not catch**.
Read at HEAD after pull. Prior records read via an extraction pass (findings inventory only,
no transcripts).

---

## VERDICTS

| Unit | Verdict |
|---|---|
| **U1** — two-slot bracket session + writer + journal | **MERGED-WITH-DEBT** |
| **U3** — pinset v2 + four-cell authenticated mint | **MERGED-WITH-DEBT — but the central review claim is not true yet.** The v2 mint must be barred from issuing any artifact until U3-1 is closed. If "merged" implied the authentication story was finished, that reading is wrong and the delta-2 CLEAN verdict overstated closure. |

Neither unit is unsafe as merged. Both are fail-closed: U1's refusals hold under the probes I
ran on the code path, and U3's v2 mint cannot mint a *false* artifact because at present it
cannot mint *at all*. The debt is real in both, and in U3 it is load-bearing.

**The process finding first, because it outranks the code findings:** across ~9,200 insertions,
twelve review records, four adversarial lenses and four delta re-audits, **not one lens ever
asked whether the code should be smaller.** The extraction over the prior records confirms zero
hits for overbuild/simplify/prune/dead-code in every verdict block. Every fix contract pushed in
one direction — more enforcement — and the diff grew monotonically across three fix rounds with
nothing ever removed. That is precisely the failure mode the standing prune gate exists to catch,
and it was skipped on the largest two-unit diff of the project.

---

## LENS B — RANKED FINDINGS

### U3-1 (BLOCKER, gates use) — the authentication anchor has no producer and no authenticator

`scripts/mint_floor_artifact_generalized.py:1709-1775` (`_v2_extraction_postcollection_record`)

FIX-1/FIX-2 made the v2 mint stop deriving its own comparison literals and instead compare the
pinset's pinned values against "the authenticated extraction report's recorded values." The
authority it compares against is `component.report["floor_mint_postcollection"]`.

That block is **produced by nothing in the repository.**

```
$ grep -rn floor_mint_postcollection joulewise/ scripts/ | grep -v mint_floor_artifact_generalized
(no hits)
$ grep -rn floor_mint_postcollection docs/    # design memo, decision log, extraction schema
(no hits — only process traces quoting the mint's own source)
```

The only writer of the block anywhere is the test fixture at
`tests/test_mint_floor_artifact_generalized.py:660` (`_v2_postcollection`).

Worse, the v1 core's `_authenticate_component` (`scripts/mint_floor_artifact.py:1040-1072`) does
**not** close the extraction report's top-level key set — it checks named fields. So
`floor_mint_postcollection` is accepted as a free extra key. The consequence:

- the mint's "independent authority" is a JSON blob that whoever writes the pinset also writes
  into the report by hand;
- the report's own hash pin is authored by that same person, so adding the block and updating
  the pin are one act;
- **F1's self-attestation defect has been relocated one level down, not eliminated.** The audit
  scenario (fabricate all hashes, repair self-hashes) now requires one extra hand-edit.

The delta-1 verdict *named this exactly*: "the new extraction-report postcollection block is not
emitted by the extraction pipeline at `joulewise/floor_extraction.py:1813-1861` and is not
authenticated by the normal report checks at `scripts/mint_floor_artifact.py:1040-1210`. It is
accepted as authority." Delta-2 returned CLEAN and the unit merged. Nothing in the design memo,
the decision log, or any chartered unit (including U10, which is scoped to *pinsets and
artifacts*) assigns anyone the job of emitting it.

**Remediation (ordered):**
1. Register the block in the extraction report schema and emit it from `joulewise/floor_extraction.py`
   as a derived-from-primary-evidence record, so its numbers come from the extraction arithmetic
   rather than from an author.
2. Add it to the governed report checks in `scripts/mint_floor_artifact.py` so a report carrying
   an unrecognised or hand-inserted block refuses.
3. Until (1) and (2) land, the v2 mint is **not permitted to issue**. Put that in the decision log,
   not just in a review file.

This is a **rule-11 mandatory-consult trigger already met and missed**: same defect class (F1
self-attestation), second fix round, and a delta verdict that reinterpreted a not-closed finding
as closed.

---

### U1-1 (HIGH) — a transient crash during PRE costs the entire quiet window, with no retry path

`joulewise/calibration_ledger.py:2594-2655` (`claim_bracket_session_slot`),
`scripts/validate_powermetrics_fiducial.py:428-460` (`abandon`)

Once a writer appends a slot claim, `claim_bracket_session_slot` refuses any further claim for
that `(session_id, slot)` unconditionally (`:2628-2634`). There is **no claim release, no
supersession receipt, no expiry.** The only forward move from an orphaned claim is
`abort_bracket_session`, which is terminal for the **whole session** — pre *and* post.

The ordinary (non-bracket) path does not have this problem: a failed attempt closes with
`disposition="abandoned"` and the operator simply reserves another attempt id. The bracket path
removed that affordance without replacing it.

Operationally: at 2am, a SIGKILL, a kernel panic, or a `powermetrics` hang during PRE means the
operator must mint a **new** session with **new** attempt ids (`:2570-2582` refuses reuse of any
reserved or ordinary attempt id) and restart the bookend sequence — on a window whose whole value
is that it is quiet and time-bounded. A single transient fault costs a night.

I do not think the two-slot session is the wrong shape — binding both endpoints under one
unchanged committed pin is the right answer to F1 and the memo's §5A sequence is sound. But the
*non-retryability* is an accident of the fix round (FIX-4 asked for exclusivity, and exclusivity
was implemented as irrevocability), not a designed property, and it is the kind of thing that is
painful to change once artifacts exist under the v1 session schema.

**Remediation:** add a governed `bracket-session-slot-claim-release` event carrying the superseded
`claim_id` and a reason, permitted only for an unfinalized slot. ~40 lines in the ledger, one
validator branch, two regressions. Do it before the first real window, not after.

---

### U1-2 (HIGH) — `claim_id` is written but never read; the claim is not bound to the finalization

`joulewise/calibration_ledger.py:2600`, `:2652`, `:2659-2735`

The exclusive claim carries a `claim_id`. It is validated as a nonempty string
(`:581-582`), written into the receipt (`:2652`), and **never compared to anything, ever.**
Exclusivity is enforced purely by the *presence* of any claim for `(session_id, slot)`
(`:2628-2634`).

`finalize_bracket_session_slot` does not require the finalizer to present a claim, and does not
check that a claim exists at all. Within `_CaptureLedgerLifecycle` the ordering is safe because
`begin()` always claims before `finalize()`. As a *ledger API contract* it is not: any caller can
finalize a slot another process holds the claim on, and the ledger will accept it. FIX-4's
"lock-file-with-identity" intent produced the identity field and dropped the binding.

**Remediation:** either (a) require `claim_id` on `finalize_bracket_session_slot` and refuse
unless it matches the outstanding claim for that slot — ~8 lines plus one regression — or
(b) delete the field. Shipping a written-only identity field is the worst of the three options,
because it *reads* as if the binding exists.

---

### U1-3 (HIGH) — the write-ahead journal is a redo log that materialises appends that never began, silently

`joulewise/calibration_ledger.py:843-866` (`_journal_completed_raw`),
`:2344-2384` (`_recover_journaled_append`), `:1-23` (module docstring)

`_journal_completed_raw` accepts `suffix == b""` — `payload.startswith(b"")` is `True` (`:864`).
Two consequences the contract and execution lenses would not surface, because both are about what
the mechanism *means* rather than whether it holds its stated invariant:

**(a) False-alarm refusal on an intact ledger.** A writer that fsyncs the journal and dies before
touching the ledger leaves a *perfectly complete, untorn* ledger file. The loader
(`:1291-1296`) applies the journal anyway and reports
`calibration_ledger_recovery_required` — "the final ledger line is a journal-authenticated torn
append requiring governed recovery." Nothing is torn. The operator at 2am is told the ledger is
damaged when it is not, and `head_sequence` over-reports by one receipt that does not exist on
disk. The module docstring describes only torn-*tail* recovery; the code also does *never-started*
recovery, and the refusal string is wrong for that case.

**(b) Silent replay of a dead process's intent.** `_recover_journaled_append` runs inside
`_locked_append`, unconditionally, before every append, and prints nothing. If the dead writer's
journaled payload was an `abort_bracket_session` receipt, then the *next* governed command —
whatever it is, run by an operator who has no idea — commits that abort as its first act and kills
a live session. The recovery evidence file is written to disk; no human is told.

**Remediation:**
1. Distinguish `suffix == b""` from a genuine partial suffix. Nothing was committed; the correct
   governed action is to record the abandoned intent and clear it, or at minimum refuse with a
   *different, accurate* reason (`calibration_ledger_append_intent_abandoned`).
2. Make `_locked_append` return or log the recovery it performed so every CLI on the path can
   print `recovered journaled append <operation_id> before proceeding`. ~15 lines.
3. Fix the docstring at `:16-22` to describe both recovery cases.

---

### U1-4 (MEDIUM-HIGH) — a hidden production flag disables the D-109 commit-authentication gate

`scripts/reserve_calibration_window_bracket.py:63-67`

```python
parser.add_argument(
    "--allow-uncommitted-pin-for-test",
    action="store_true",
    help=argparse.SUPPRESS,
)
```

This ships in the production reservation tool, is invisible to `--help`, and sets
`require_committed_pin=False` — turning off "the head pin must equal the committed Git bytes,"
which is one of the three defences the ledger docstring claims (`calibration_ledger.py:1-7`:
"rollback or stale-head consumption"). The emitted reservation JSON records **no marker** that the
capability was created under the bypass, so the receipt is indistinguishable from an authenticated
one afterwards.

It exists solely so two tests can drive the CLI (`tests/test_calibration_ledger.py:941`, `:981`).
Every other test in the suite calls the library with `require_committed_pin=False` directly.

**Remediation:** delete the flag; have those two tests call `append_bracket_session_receipt`
directly like the other 18 sites do. If the CLI surface genuinely needs testing, gate the flag on
an environment variable *and* stamp `"pin_authentication": "bypassed"` into the output object.
~6 lines net removal.

---

### U1-5 (MEDIUM) — an aborted bracket slot loses the evidence the ordinary path deliberately keeps

`joulewise/calibration_ledger.py:2738-2785` (`abort_bracket_session`),
`scripts/validate_powermetrics_fiducial.py:428-460`

The ordinary abandon path finalizes with `disposition="abandoned"`, `artifact_sha256`, a
`content_id`, and a custody locator — and `_valid_receipt_shape:721-726` carries an explicit
comment about *why*: "When canonical primary bytes exist, preserve their authentic content
identity."

`abort_bracket_session` records only `finalized_slots`, `unused_slots`, and a free-text `reason`.
The partial capture directory under `runs_root/instrument_validation/<attempt_id>` — which may
contain a truncated `powermetrics.plist` — is left with **no receipt binding its content at all.**
The ledger's own principle (every calibration artifact is registered) is honoured in the ordinary
path and dropped in the bracket path, for the same physical situation.

**Remediation:** have `abort_bracket_session` accept optional per-slot artifact hashes and custody
locators for unfinalized slots and record them. ~20 lines, one regression.

---

### U1-6 (MEDIUM) — one refusal string speaks a different language than its siblings, and it's the one operators will hit

`joulewise/calibration_ledger.py:2634`

```python
raise CalibrationLedgerError("calibration_ledger_bracket_slot_claimed")
```

Every other writer-side raise in the module — all 109 of them — is prose:
`"bracket session is not open"`, `"attempt is not uniquely pending"`, `"head pin is not committed
at Git HEAD"`. This single site raises a bare taxonomy key. The taxonomy is the *reader*-side
vocabulary (`REFUSAL_TAXONOMY:112-133`), propagated into claim barriers; it is not the writer's.

The irony is that this is the highest-stakes message in the unit: it is what a second writer sees
when two processes race for a slot, at night, in the situation U1-1 makes unrecoverable. The
operator gets `calibration_ledger_bracket_slot_claimed` and no indication of what to do.

**Remediation:** `"bracket session slot {slot!r} already holds an exclusive writer claim; run
abort_bracket_session to close the session or check for a live writer"`. One line. Given U1-1, the
message should name the actual escape hatch.

---

### U1-7 (LOW-MEDIUM) — the fail-closed set-equality in `is_governed_open_bracket_extension` is brittle

`joulewise/calibration_ledger.py:281-308`, consumed at
`joulewise/calibration_bracketing.py:941` and `scripts/validate_powermetrics_fiducial.py:335`

The property requires `set(self.refusal_reasons) == {"calibration_ledger_bracket_session_open",
"calibration_ledger_head_mismatch"}` **exactly**. Any third reason — including the false-alarm
`calibration_ledger_recovery_required` from U1-3 — makes it `False`, which bricks mid-window
discovery until a governed writer runs. Fail-closed, so not a correctness bug; but it means every
future refusal reason added to the ledger silently narrows this gate, with no test that would
notice. And a *committed* pin at the session-open receipt (no head_mismatch, session still open)
also returns `False`, which is a surprising asymmetry a fresh reader will not predict.

Related, at `calibration_bracketing.py:939-943`:

```python
if (
    not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
    or not ledger_snapshot.valid
    and not ledger_snapshot.is_governed_open_bracket_extension
):
```

This is correct under Python precedence (`A or (B and C)`), and it is the *only* place in the
codebase where a claim-side gate mixes `or`/`and` unparenthesised. On a security-relevant
admission check that is asking for a future edit to break it silently. Parenthesise it.

**Remediation:** express the property as an allowlist check (`set(reasons) <= allowed and
"..._bracket_session_open" in reasons`) with an explicit comment on why head_mismatch is tolerated;
parenthesise the gate. ~5 lines.

---

### U1-8 (LOW) — a regression gap the fix rounds never picked up

The U1 execution audit recorded: *"Writer coverage exercises wrong attempt only. Wrong session and
wrong slot are absent at writer level. Direct probes show current code refuses all three, but
regression protection is incomplete."* This never entered `U1-FIX-CONTRACT.md` and never appeared
in any delta closure table. It is the only prior finding that fell off the board entirely rather
than being fixed, waived, or deferred. Two tests in
`tests/test_powermetrics_fiducial.py`; ~30 lines.

---

## LENS A — OVERBUILD / MERGE-ABILITY PRUNE

**Would a maintainer want to own this diff?** For U1: yes, with the seams below sanded.
For U3: **no, not in this shape** — the mint script is now 3,400 lines containing two complete,
parallel mint implementations plus a 919-line specification of the same contract that no
production code reads.

### PRUNE-1 — `scripts/floor_mint_pinsets/schema_v2.json` (919 lines) is not enforced by anything

Sole reference outside the file itself: `tests/test_mint_floor_artifact_generalized.py:1528`, and
that test only asserts **two `const` strings differ from each other**. It never validates a pinset
against the schema. `jsonschema` is not a project dependency (it appears once, as an optional
`find_spec` guard in `tests/test_axi_schemas.py:40`).

Meanwhile the *actual* contract is re-specified in Python across `_parse_v2_pinset`
(`:594-970`, 376 lines), `_parse_v2_component`, `_parse_v2_postcollection`, and
`_v2_gate_*`. Two hand-maintained specifications of one contract, no sync mechanism, one of them
on no execution path at all.

This compounds a hazard the project has already ruled on. `MAGISTRATE-DISPOSITIONS.md:209-215`
(binding rule R1) states the cardinality limits are *"hardcoded in THREE places (schema_v2.json,
the generalized mint, AND the consumer detection_floor.py)"* and freezes the entire file set until
U10 closes, because *"touching that file set before U10 puts the capstone's nights hostage to a
second paper."* U3 is the commit that created the second and third of those places:
`schema_v2.json:626-627,680-681,723-724,731-732,834-835,842-843,850-851,877-878,907-908`
(minItems/maxItems 2 and 4), the mint's `:3055-3084`, and
`joulewise/detection_floor.py:1660,1707,1893,1900-1914,2922`.

Note the shape of it: a unit named "**generalized** mint", carrying a 919-line generic schema, that
is in fact hardwired to exactly two producers × two roles × four cells in three unsynchronised
files. It did not generalize; it added a second special case with a general-looking wrapper.

**Prune:** delete `schema_v2.json` (**−919**) and keep the Python parser as the single normative
contract; *or* make it normative — add `jsonschema` as a dependency, validate every pinset against
it at load, and delete the overlapping shape checks from `_parse_v2_pinset` (**−250 to −300** from
the mint). Do not keep both. Whichever survives must derive the 2/2/4 cardinality from one
declared constant that `detection_floor.py` imports.

### PRUNE-2 — `_authenticated_head_pin` was added and then not used at the site it duplicates

`joulewise/calibration_ledger.py:2439-2456` is a new helper extracted by the fix round. It is
called from exactly one place (`:2530-2534`). The identical 11-line block it was extracted *from*
still sits inline at `:2838-2848` in `append_pending_receipt`, and a third near-copy at
`:2015-2025` in `_require_genesis_bootstrap_state`.

**Prune:** route `append_pending_receipt` through the helper. **−11**, and one fewer place where
"head pin is not committed at Git HEAD" can drift.

### PRUNE-3 — `_valid_chain_fields` likewise applied only to the new path

`:498-511` is a new helper. `_valid_receipt_shape` (`:645-690`) still spells out the same six
chain checks inline for ordinary receipts.

**Prune:** apply the helper to both. **−12**.

### PRUNE-4 — the session finalization validator is a near-transcription of the ordinary one

`:596-632` (the tail of `_valid_session_receipt_shape`) reproduces, field for field, the
finalization validation at `:652-745`: same disposition/artifacts/epoch/t1/capture/bound/content_id
logic, same `abandoned` special case, same "content_id == content_id_from_artifact_hashes"
resolution. Only the key set differs.

**Prune:** factor the shared body into `_valid_finalization_fields(receipt)` and call it from both.
**−40**, and the two paths can no longer drift on the abandoned-content-identity rule — which is
exactly the rule carrying a load-bearing comment.

### PRUNE-5 — three places walk `open_receipt["slots"]` raw, because the dataclass does not carry it

`CalibrationBracketSession` (`:341-356`) exposes `slot_attempt_ids` but not the reserved
custody/epoch/t1 bindings. So three separate call sites re-derive them from raw receipt JSON:
`calibration_ledger.py:996`, `:1012`, `:2700-2712`, and — worst — a **script** at
`scripts/validate_powermetrics_fiducial.py:318-336`, which hand-rolls a `next(...)` scan for the
open receipt and pokes into `.get("slots", {}).get(slot)`.

Any change to the open-receipt slot shape must now be mirrored into a CLI script. That is the
single most change-hostile seam in U1.

**Prune:** add `reserved_slots: Mapping[str, Mapping[str, Any]]` to the dataclass and delete the
four raw walks. **−35**, and the script stops knowing the wire format.

### PRUNE-6 — the pre/post ordering rule is implemented twice, differently

Ledger: `BRACKET_SESSION_SLOTS[len(session.finalized_slots)]` (`:2620`, `:2694`).
Script: an `if/else` ladder (`:311-317`) producing `None` for the exhausted case.

Two encodings of one invariant, in two modules, with different failure modes (`IndexError` vs
`None`). Neither is currently reachable in the bad state, which is precisely why this will rot.

**Prune:** export `next_expected_slot(session)` from the ledger; the script calls it. **−10**.

### PRUNE-7 — U3's test fixture is a 1,400-line second implementation

`tests/test_mint_floor_artifact_generalized.py` is 2,971 lines, of which **lines 63-1400 are
module-level fixture machinery** before the first test class: `_write_bundle`,
`_install_component_fixture`, `_role_components`, `_v2_component_pin`, `_v2_postcollection`,
`_synthetic_bracket_evidence`, `synthetic_v2_fixture`, `_repair_v2_pinset_self_hashes`,
`freeze_synthetic_v2_pinset`, `install_v2_cli_fixture`. 39 tests sit on top.

The audits already noted the independence problem — *"its construction still calls implementation
internals at tests/test_mint_floor_artifact_generalized.py:605-635"* — and FIX-7b's answer was to
add hand-derived golden constants **on top of** the synthetic builder rather than in place of it.
So the file now carries both oracles, and the synthetic one still shells out to the code under
test.

**Prune:** freeze one canonical four-cell fixture to disk as a checked-in golden directory, and
delete the runtime builders that reproduce it. Estimated **−600 to −800**, with a *net gain* in
discriminating power because the fixture stops depending on the implementation.

### PRUNE-8 (note, not a prune) — 5 module reloads per mint

`_fresh_original_core()` (`:1205-1220`) execs `scripts/mint_floor_artifact.py` as a fresh anonymous
module and signature-fingerprints it. U3 calls it once at `:2924` plus once per cell via
`_configured_core` (`:3094`) — five full module loads and five interface audits per mint. This
machinery is **pre-existing**, not U3's, so I am not charging it to this diff; but U3 multiplied its
invocation by five and a maintainer will meet it first here.

---

## PRUNE LIST — SUMMARY

| # | Action | File:line | Est. lines |
|---|---|---|---|
| PRUNE-1 | Delete `schema_v2.json`, or make it normative and delete the overlapping Python shape checks | `scripts/floor_mint_pinsets/schema_v2.json` (whole); `mint_floor_artifact_generalized.py:594-970` | **−919** or **−300** |
| PRUNE-7 | Replace the runtime v2 fixture builders with a checked-in golden fixture | `tests/test_mint_floor_artifact_generalized.py:63-1400` | **−600…−800** |
| PRUNE-4 | Factor shared finalization validation | `calibration_ledger.py:596-632` ∥ `:652-745` | **−40** |
| PRUNE-5 | Put reserved slot bindings on `CalibrationBracketSession`; delete 4 raw walks | `calibration_ledger.py:341,996,1012,2700`; `validate_powermetrics_fiducial.py:318-336` | **−35** |
| PRUNE-3 | Apply `_valid_chain_fields` to the ordinary path | `calibration_ledger.py:645-690` | **−12** |
| PRUNE-2 | Route `append_pending_receipt` through `_authenticated_head_pin` | `calibration_ledger.py:2838-2848` | **−11** |
| PRUNE-6 | Single `next_expected_slot()` | `validate_powermetrics_fiducial.py:311-317` | **−10** |
| U1-4 | Delete the hidden pin-bypass flag; tests call the library | `reserve_calibration_window_bracket.py:63-67` | **−6** |
| | | **Total** | **≈ −1,630 to −1,830** (≈18–20% of the merged diff) |

Everything on that list is a *collapse*, not a capability loss. None of it weakens a refusal;
three items (PRUNE-4, PRUNE-5, PRUNE-7) strictly strengthen the code by removing a place where two
copies of one rule can drift.

---

## WHAT I DID **NOT** FIND

Stating this plainly so the verdicts are not read as harsher than they are:

- **U1's core design is right.** Reserving both endpoints under one capability, checking
  physical-head == committed-pin only at open, and deferring the terminal pin until post is the
  correct answer to F1 and to the memo's §5A sequence. It is not a workaround wearing a contract's
  clothes. The one place I suspected an escape hatch —
  `is_governed_open_bracket_extension` — is correctly scoped: it admits *discovery* mid-session
  (`calibration_bracketing.py:941`) but **not** binding (`:548`, `:634` both require strict
  `.valid`), and the open session's own observations are excluded from candidates by
  `finalized_session_ids` (`:945-961`). That is the right split.
- **The write-ahead journal design is sound** on its stated invariant: no ledger byte is ever
  deleted, recovery completes only a journal-authenticated suffix, and recovery leaves durable
  evidence. My U1-3 finding is about a case the design did not consider, not a hole in the case it
  did.
- **The exact bracket binding does what it claims.** `validate_calibration_bracket_binding`
  (`:610-700`) refuses neighbour substitution, cross-window identity, non-terminal heads, and
  unfinalized sessions, and it re-resolves both endpoints against the snapshot rather than trusting
  the binding document. The L5 closure is real.
- **U3's `_authenticate_v2_inputs` is genuinely careful** — re-reads the acceptance file after
  authentication to catch TOCTOU (`:2942-2951`), refuses evidence-root aliasing (`:3110-3116`),
  refuses duplicate JSON keys and non-finite constants at parse. That is good work. It is upstream
  of U3-1, not a substitute for it.

---

## RECOMMENDED ACTIONS, IN ORDER

1. **Bar the v2 mint from issuance** until U3-1 (1) and (2) land. Decision-log entry, not a review file.
2. **U1-1 claim release** before the first live window. A night is the unit of loss here.
3. **U1-2**: bind or delete `claim_id`.
4. **U1-3**: distinguish never-started from torn, and surface recovery to the operator.
5. **U1-4, U1-6**: two small deletions/rewordings; do them at the bench (below the delegation threshold).
6. **PRUNE-1 and PRUNE-7** together as one delegated sweep — they are ~85% of the reclaimable lines
   and neither touches a refusal.
7. **Process**: the prune gate is not optional and the delta-2 CLEAN on U3 needs a written
   correction. A delta re-audit that inherits the fix round's own framing cannot see a finding the
   fix round relocated rather than closed — which is exactly what happened to F1.
