Reading additional input from stdin...
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: xhigh
reasoning summaries: none
session id: 019fde5e-afb8-7d70-934e-0ddd8778058d
--------
user
DELTA RE-AUDIT of the U1 gate-debt fix round (read-only; write no files; FINAL MESSAGE in neutral engineering language — per-item disposition table first, then conclusions; no code quotes beyond file:line). Branch impl/d117-u1-gate-debt at HEAD vs origin/main.
Source findings: docs/process_traces/2026-08-07-d117-u-units/FABLE-GATE-U1.md (the apex diff gate; F1/F2/F4/F5/F6a) and POSTMERGE-INTEGRATION-REVIEW.md (independent corroboration of the path-normalization defect). Read both first.
CHARGE — verify each closure by reproducing the ORIGINAL failing scenario, not by reading the new tests:
(1) F1: simulate a crash after the ledger append but before the journal clear via subprocess, then run the writer's ordinary post-slot retry. Before the fix it refused with a false 'capture does not match the exact reserved bracket session slot' and never healed. Does it now heal, and does the refusal text name the real condition when it legitimately refuses?
(2) F2: finalize a session window, THEN evaluate an ordinary-bracketed historical window. Before the fix the first finalized session made bindings mandatory for every window in the registered universe, silently. Does the historical window still evaluate? AND — critically — verify the anti-withholding property was NOT lost: construct a case where a candidate is withheld from the supplied set and confirm it is still detected and refused.
(3) F4: at the exact terminal moment with journal residue present, confirm the head-pin read neither emits a pin over a stale journal nor reports a wrong 'malformed'.
(4) F5: with a symlinked runs_root (the real macOS /tmp case), confirm reservation and capture now agree; confirm the regression covers main(), not only the library path.
(5) F6a: the racing slot-claim refusal emits operator prose, not a taxonomy code.
(6) HUNT INTRODUCED DEFECTS — especially: does the new standalone recovery entry point create a path to heal a journal that should NOT be healed (an abandoned or foreign operation)? Does the F2 window-keyed predicate open a way for a window to bracket with a candidate belonging to a DIFFERENT window (that is L5 — it must still refuse)? Did unifying path normalization change behavior for any already-recorded custody path?
(7) SAME-SIGNATURE per class (strand-a-night recovery; retroactive coupling; journal-blind read; path asymmetry): survives yes/no each.
Report the focused ledger/bracketing/fiducial suite tails. CLEAN needs a checks-performed line.
codex
I’ll audit the branch as a read-only delta review and reproduce the pre-fix failure modes with disposable state outside the repository. I’m starting with the two required source findings, then I’ll map each claim to the implementation and run the original scenarios independently of the new regression tests.
exec
/bin/zsh -lc "sed -n '1,260p' docs/process_traces/2026-08-07-d117-u-units/FABLE-GATE-U1.md && sed -n '1,320p' docs/process_traces/2026-08-07-d117-u-units/POSTMERGE-INTEGRATION-REVIEW.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 exited 1 in 0ms:
# APEX DIFF GATE — U1 (PR #111, merge 0564216), retroactive

Gate instance: fresh Fable, no loop context. Inputs: full implementation diff
(`git diff 0564216^ 0564216 -- joulewise/ scripts/`, 2061 insertions), the merged
files at 0564216, and the U1 process traces (contract audit, exec audit, FIX-1..8,
delta, FIX-6b, delta-2 CLEAN). Prior-layer findings were read first; everything
below is new ground unless marked otherwise.

## VERDICT: SOUND-WITH-DEBT

No path was found by which bad evidence is admitted, a slot is double-used, an
open or aborted session leaks a candidate, or a torn ledger is silently consumed.
Every interleaving I walked lands on the refuse side. The debt is operational and
structural, not evidentiary — but two items (F1, F2) are the kind that strand a
night or a consumption path, and both are cheap to fix now and expensive to
discover at 2am or at re-evaluation time.

---

## Question 1 — right design, or workaround frozen into contract? (argued)

**The primitive underneath is right. The arity frozen into it is the workaround.**

Strip the vocabulary and what U1 actually built is a *transaction*: a governed,
pre-declared, bounded extension of the physical ledger head past the committed
pin, closed by exactly one terminal pin. `is_governed_open_bracket_extension`
(calibration_ledger.py, snapshot property) is the transaction-visibility rule;
`terminal_head_pin_for_session` is the commit point. That is the correct answer
to the real problem — head-pin equality is the ledger's core defense (evaluation
only ever consumes human-reviewed committed state), and the alternatives were
worse: weakening the pin check destroys the custody property; a mid-window git
commit contaminates the quiet measurement. Bounded-extension-then-terminal-pin
preserves both. As a primitive, I would ratify it.

What is frozen is the transaction's *contents*: exactly one open session
ledger-wide, exactly two slots named `pre`/`post` at the schema-key level
(`set(slots) == {pre, post}` in `_valid_session_receipt_shape`), exact
pre-before-post ordering (`expected_slot = SLOTS[len(finals)]`), one claim per
slot forever (`existing` check in `claim_bracket_session_slot`), and
atomic-abort as the only failure handling. Three consequences:

1. **Three observations / a mid-window drift check** (plausible for the ICPE
   revision of a metrology paper): new schema version, parallel arms in
   `_bracket_sessions_and_observations`, new abort shape, new binding endpoint
   set. The exhaustive key-set validation style — which is the module's house
   style and correct — makes every extension a schema fork, never a parameter.
2. **A retry slot — the one that will actually hurt.** A transient PRE failure
   before the workload runs (powermetrics never ready — a path that exists in
   this writer *because it has happened*) is metrologically harmless to retry:
   nothing has been measured yet. The design's answer is: finalize-invalid →
   auto-abort → `terminal_head_pin_for_session` → **git-commit a new pin** →
   re-reserve a fresh session with fresh attempt IDs and custody dirs → re-arm.
   The recovery ceremony includes precisely the mid-night git commit the design
   exists to avoid, performed manually, at 2am, on the machine that must stay
   quiet. With three irreplaceable nights and a historically flaky sampler, the
   probability of landing on this ceiling is not small.
3. **Cross-window coupling** (F2 below): the binding-mandatory rule was keyed to
   the wrong predicate, so the first session-based night retroactively changes
   the evaluation contract for every ordinary-bracketed window in the ledger.

**Ruling I recommend to the magistrate:** keep the design — under paper-first
economics with a ratified memo and three nights, freezing two-slot is a
defensible call, and two *is* the metrological arity of a bracket, not an
accident. But record the ceiling as a named limitation with the retry cost
spelled out, and pre-stage the retry ceremony in the night runbook (second
session identity pre-validated via the dry-run path, pin-commit script ready)
so that hitting the ceiling costs ten mechanical minutes, not an improvised
governance decision mid-window. That converts the frozen arity from a trap into
a priced constraint.

---

## Ranked findings

### F1 — HIGH (operational): the most likely crash residue strands the night behind an undocumented incantation, with a misleading refusal
- Crash window: after a successful ledger append+fsync but before
  `_clear_append_journal` (calibration_ledger.py:2417-2421 region) — the widest
  residue window in the append sequence, and it includes the fully-successful-
  append case.
- Residue: journal file present, ledger complete. Loader
  (`load_calibration_ledger_snapshot` → `_parse_ledger` with journal,
  calibration_ledger.py:1291) adds `calibration_ledger_recovery_required`
  unconditionally, even for a complete tail. Snapshot invalid — correctly
  fail-closed.
- The trap: recovery lives ONLY inside `_locked_append`
  (calibration_ledger.py:2401); there is no standalone recovery entry point
  anywhere in `scripts/`. The writer's `begin()` validates via
  `_validate_reserved_bracket_slot` BEFORE its first append, and
  `is_governed_open_bracket_extension` requires the refusal set to be exactly
  `{bracket_session_open, head_mismatch}` — `recovery_required` breaks it. So
  the post-slot retry refuses at scripts/validate_powermetrics_fiducial.py:348
  with **"capture does not match the exact reserved bracket session slot"** —
  which is false; the slot matches perfectly — and never reaches the append
  that would heal. The only in-repo escape today: run the reservation CLI with
  `--execute` so that it *fails* on head-mismatch AFTER `_locked_append` has
  silently healed the journal, then retry the writer. Nobody at 2am derives
  that.
- Remediation (small): (a) a `scripts/recover_calibration_ledger.py` that takes
  the lock, runs `_recover_journaled_append`, and reports the evidence path — or
  have bracket `begin()` perform validation inside the locked append (claim's
  `build`) so recovery precedes validation; (b) when `recovery_required` is in
  the snapshot reasons, every downstream refusal must SAY SO and name the tool.
  ~40 lines total.

### F2 — HIGH (design coupling, likely missed by both lenses): binding becomes mandatory ledger-wide, retroactively, on the first finalized session
- `has_session_candidates` (calibration_bracketing.py:1268) is
  `any(candidate.bracket_session_id is not None for candidate in candidates)` —
  and `candidates` is necessarily the FULL registered universe, because the
  anti-withholding rule (`supplied_valid != registered_valid`, cb.py:1240)
  refuses anything less. Therefore: the moment the first D-117 session
  finalizes in the live ledger, EVERY subsequent `evaluate_calibration_bracket`
  call — including one for an ordinary-bracketed historical window (the a9/a10
  lineage) — returns `calibration_bracket_binding_missing`, and no binding can
  ever exist for a window that has no session. Prior ordinary windows become
  structurally unevaluable in the live ledger, silently, as a side effect of the
  first new night.
- This may even be the intended future ("session-only from here"), but it is
  nowhere ratified, and any re-evaluation path that touches pre-D-117 windows
  (CAL-REBRACKET-01 consumption work is still open) will hit it as a surprise
  refusal with a reason string that misdirects ("binding missing" — no, the
  *era* is mixed).
- Remediation: key the binding requirement to the window under evaluation, not
  the ledger — require a binding iff the window-matching candidate set (or the
  selected endpoints) contains session observations. ~5-line predicate change.
  Alternatively, ratify session-only-forward in a decision-log entry and add an
  explicit refusal reason (`calibration_bracket_pre_session_window`) so the
  refusal tells the truth. Either is acceptable; the current silent coupling is
  not.

### F3 — MEDIUM (the Q1 debt, as a finding): no-retry ceiling
As argued above. Not a code change — a decision-log limitation entry plus a
runbook section: pre-staged second session identity (validated via the CLI
dry-run), scripted terminal-pin commit, rehearsed once before night 1.

### F4 — MEDIUM: `terminal_head_pin_for_session` is journal-blind — the read side has two parallel truth semantics
- calibration_ledger.py:2798 parses raw bytes with `_parse_ledger(raw)` and no
  journal. Two consequences at exactly the terminal moment (crash during/after
  the post-finalization or abort append): (a) torn tail → refusal says
  `calibration_ledger_malformed` — wrong; it is a journal-authenticated torn
  append, i.e. `recovery_required`; (b) complete tail + stale journal → this
  function happily emits a terminal pin while every subsequent snapshot load
  refuses with `recovery_required`, so the operator commits a pin that then
  appears broken. Both fail closed eventually, but the journal was supposed to
  be THE truth-completion rule; a reader that ignores it reintroduces the
  two-sources-of-truth problem the delta rounds fought over (FIX-6/6b closed
  the write side; the read side kept a hole).
- Remediation: `_read_append_journal` + pass journal into `_parse_ledger` here,
  and refuse with the recovery reason. ~6 lines.

### F5 — MEDIUM: custody-path normalization asymmetry — `resolve()` vs `absolute()`
- Reservation normalizes custody with `Path(...).absolute()`
  (calibration_ledger.py:2493, no symlink resolution); the writer's main() binds
  `custody_locator = str(out_dir.resolve())`
  (scripts/validate_powermetrics_fiducial.py:598, full symlink resolution). The
  new exact-equality check in `_validate_reserved_bracket_slot` makes this
  asymmetry load-bearing for the first time. On macOS, `/tmp` and `/var` are
  symlinks into `/private` — any rehearsal or run rooted through a symlinked
  path refuses PRE capture with the generic F1 message. The integration tests
  drive `_CaptureLedgerLifecycle` directly with raw strings
  (tests/test_powermetrics_fiducial.py:958-1000) and never exercise `main()`'s
  `resolve()`, so the asymmetry is untested exactly where it bites.
- Remediation: one shared normalization function used by reservation,
  validation, and the writer. ~10 lines.

### F6 — MEDIUM-LOW: refusal quality at 2am (Q4 verdict: messages say what failed, mostly, and almost never what to do)
- `_validate_reserved_bracket_slot` (validate_powermetrics_fiducial.py:348)
  collapses ~10 distinct causes — not-governed-extension (incl. F1's recovery
  state), wrong slot order, attempt mismatch, custody mismatch (incl. F5),
  identity-epoch drift (e.g. macOS auto-updated os_build since reservation),
  t1 drift — into ONE message with no field named. An epoch drift and a stale
  journal produce identical text. Remediation: enumerate the first failing
  predicate and name field + reserved-vs-observed values (values here are paths
  and build strings, not secrets).
- `claim_bracket_session_slot` raises the taxonomy CODE as prose
  (`"calibration_ledger_bracket_slot_claimed"`, calibration_ledger.py:~2626)
  while its siblings raise sentences — one refusal surface, two dialects.
- Recovery evidence (`.recovery-<opid>.json`) is written durably and read by
  NOTHING — no loader, custody check, or verifier consumes it. "Governed and
  evidenced" is currently write-only governance. Either bind recovery evidence
  into custody verification or document it as forensic-only.
- Crash inside `_atomic_private_write` leaks `.{name}.XXXXXX` temp litter beside
  a custody artifact; loaders ignore it, auditors will not. Sweep on recovery.
- Credit where due: the reservation CLI's dry-run/execute parity, the explicit
  `--execute` arm switch, and `terminal_head_pin_status:
  "deferred_until_post_finalization"` in its output are genuinely good 2am
  ergonomics.

### F7 — LOW: prune list (Q2), with line estimates
Total surplus is modest for +1283 — the bulk is exhaustive fail-closed schema
validation in the module's established style, which I do not count as surplus.
The real surplus is *redundant re-verification and parallel raw-receipt digging*,
not speculative generality:
1. **Dead first-pass classification** in `_attempts_and_observations`: the
   ordinary loop populates `content_classification`, which is then
   `.clear()`ed (calibration_ledger.py:1184) and fully recomputed over the
   combined list. Pass 1's classification block is dead weight whose conflicts
   pass 2 re-finds. **−15 lines.**
2. **`observation_stale_triggers` comprehension** (calibration_bracketing.py:
   1425-1437): filters a list for one exact string it may have just appended;
   it is `if TRIGGER in observed_triggers`. **−8 lines.**
3. **Third verification of bound-session candidate identity** (cb.py, loop after
   binding acceptance): already enforced by (a) candidate construction from
   observations and (b) the registered/supplied field-equality check. Defense in
   depth is arguable; if kept, comment it as such. **−20 lines (optional).**
4. **`_validate_reserved_bracket_slot` digs raw receipts** for reserved slot
   specs because `CalibrationBracketSession` doesn't carry them. Put the
   reserved slot specs (custody/epoch/t1) on the dataclass; the writer-side
   open-receipt scan and the duplicated order/attempt checks collapse.
   **−25 lines net (refactor, not delete).**
5. **`claim_id`** is minted, journaled, and never verified by anything —
   finalization does not check that the finalizer holds the claim. Either make
   it load-bearing (finalize verifies claim_id → genuinely closes the
   claim-to-finalize identity gap) or mark it forensic-only in the schema
   comment. **+4 lines to strengthen, or 0 and a comment.**
6. Six `del observations` / `del bracket_sessions` sites → `_` unpacking.
   Cosmetic.

**Would I want to own this diff?** Yes, with the refactor in item 4 and the F1/F4
fixes. It is over-verified rather than under-verified — the rare direction to
err — and its failure modes are refusals, not admissions. What I would not want
to own is the 2am runbook as it stands today: that is where this unit is thin.

---

## Question 3 — the write-ahead journal, interleavings walked
Shape: redo-WAL with **journal-as-commitment** semantics — once the journal is
durable, the receipt WILL exist; recovery completes, never rolls back. Walked:
- Journal complete, ledger untouched → loader materializes the intended receipt
  with `recovery_required` (fail-closed); recovery appends the full payload.
  Note the philosophical consequence: a receipt that never touched the ledger
  is materialized from the sidecar. Under the module's declared trust model
  (no malicious trusted writer) and given the exclusivity claims that may
  already depend on that receipt, redo is the right choice over undo. Accepted.
- Torn tail matching journal prefix → suffix-only completion, evidence,
  clear. Correct; append-only preserved.
- Complete tail + journal → zero-byte "recovery" with evidence, clear. Correct
  (evidence event name "governed-torn-tail-recovery" with 0 recovered bytes is
  a slight misnomer; harmless, deterministic — delta-2 covered adjacent cases).
- Crash after evidence, before clear → idempotent (FIX-6b; delta-2 CLEAN — I
  did not re-litigate, the regression set is convincing).
- Stale journal + later unrelated appends → genuine mismatch, fail-closed
  refusal, unreachable through `_locked_append` discipline. Correct.
- Self-hashed journal (`operation_id`) provides integrity, not authenticity —
  consistent with the declared trust model; fine.
So: **the sidecar is the right shape**, with two residual seams — the
journal-blind reader (F4) and the unreachable-recovery trap (F1). Both are
uniformity bugs at the edges of an otherwise sound core, not flaws in the core.

## Question 5 — coherence
Follows the house style faithfully: refusal taxonomy extended in place,
exhaustive key-set schema validation, raise-vs-return split matches existing
convention (writers raise `CalibrationLedgerError`; evaluation returns reason
tuples), `bracket_*` field prefix on `CalibrationCandidate`/`LedgerObservation`
is consistent. New vocabulary (capability, slot, claim, governed extension)
comes from the ratified memo, not invention. Two wrinkles: "finalized" as a
session STATE means "both slots filled, any disposition" — an invalid post
yields a `finalized` session that can never bind (correct behavior; misleading
name; a docstring line would do); and the taxonomy-code-as-message inconsistency
noted in F6.

sed: docs/process_traces/2026-08-07-d117-u-units/POSTMERGE-INTEGRATION-REVIEW.md: No such file or directory

codex
The apex gate is loaded. The corroboration filename is not at the path as written, so I’m locating its repository path now and will read it before any implementation inspection.
exec
/bin/zsh -lc "rg --files | rg '("'^|/)POSTMERGE-INTEGRATION-REVIEW'"\\.md"'$'"'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 exited 1 in 0ms:
exec
/bin/zsh -lc "find docs -iname '*postmerge*' -o -iname '*integration*review*'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
docs/process_traces/2026-08-07-d117-u-units/OPUS-POSTMERGE-U1U3.md

exec
/bin/zsh -lc "sed -n '1,360p' docs/process_traces/2026-08-07-d117-u-units/OPUS-POSTMERGE-U1U3.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '361,760p' docs/process_traces/2026-08-07-d117-u-units/OPUS-POSTMERGE-U1U3.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
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

codex
Both source findings are now read; the corroboration is stored as `OPUS-POSTMERGE-U1U3.md`, not under the requested filename. I’ll next establish workspace/branch state and the repository’s review gates, then build independent reproducers for F1/F2/F4/F5/F6a and adversarial probes for the introduced-defect hunt.
exec
/bin/zsh -lc "git status --short --branch && git rev-parse HEAD && git rev-parse origin/main && git log --oneline --decorate --max-count=12 origin/main..HEAD && rg -n '"'^## (ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next|Current Queue|Do-Not-Do-Yet)|''^# (ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next|Current Queue|Do-Not-Do-Yet)'"' RUN_STATE.md TASK_QUEUE.md && rg -n 'Mission M0|"'^## M0|''^### M0'"' docs/agent_playbook.md && sed -n '1,260p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
## impl/d117-u1-gate-debt...origin/impl/d117-u1-gate-debt
880b6bcf64254900946f88e09011a1596261d0e7
ca8eea908aee6bd752a2f7824e75e54bef8112ee
880b6bc (HEAD -> impl/d117-u1-gate-debt, origin/impl/d117-u1-gate-debt) U1 gate-debt fixes (apex Fable diff gate + corroborating integration review): F1 standalone recovery entry point with recovery-aware refusal text (closes the strand-a-night trap where the writer's retry refused with a false message and never reached the healing code); F2 session-candidacy keyed to the window under evaluation, not the global universe (stops the first finalized session from silently making bindings mandatory for every historical window; anti-withholding preserved by keeping the registered-vs-supplied equality check ahead of the window predicate); F4 journal-aware terminal head-pin reads; F5 unified path normalization with a symlinked-root regression; F6a operator prose on the racing slot-claim refusal
RUN_STATE.md:2077:## ACTIVE_STOP_CARD
RUN_STATE.md:2216:## Current Project Status
RUN_STATE.md:2790:## Known Workspace State
TASK_QUEUE.md:306:## Current Queue
26:1. Run Mission M0 (preflight) — always.
50:## Mission M0: Preflight (every session)
# The Orchestration Process

How this project is actually built: a human researcher directing a
multi-model AI system whose workflow is itself a deliberate, versioned,
self-instrumenting piece of engineering. This document is the single
in-repo description of that process. (The executable playbooks live
outside the repository as reusable "skills" so they transfer to future
projects; this page describes what they do and where their evidence
lands in this repo.) Binding role and process changes live in
`docs/decision_log.md`; this page avoids copying volatile model versions.

## Roles: a lead, independent implementers/reviewers, and a human at the top

- **Ed (researcher)** sets research direction, methodology
  non-negotiables (raw-evidence bundles, dual-basis capture with gross-energy
  headlines, named
  measurement boundaries, no unauditable claims), hardware/access
  decisions, and — critically — *process policy*: every rule below
  traces to a standing instruction issued after an observed failure or
  opportunity. External-facing claims and merge authority derive from
  him (he granted the lead conditional self-merge authority on
  2026-07-08 once the review gate had proven itself).
- **The designated lead** owns
  decomposition, triage, design adjudication, every final diff gate,
  all live/hardware verification, merge decisions, bookkeeping, and
  process evolution. Other agents save lead capacity without inheriting
  final authority; all escalation paths terminate at the lead.
- **Independent implementation and review agents** do the heavy reading and
  writing: implementation against pinned specs, adversarial review
  lenses, test writing, test *auditing* (never of its own tests — a
  fresh instance audits), docs drafting, and review of the lead's own
  consequential decisions. Cross-model review is load-bearing by
  design: the attributed per-layer catch record (below) shows the two
  roles consistently catching different classes of defect.
- **Specialist agents** handle bounded sweeps (for example, docs
  consistency) and, when a stream genuinely needs
  mid-stream judgment, as a stream director — a role that is now the
  exception rather than the default (see Topology).
- **Image-heavy analysis uses the designated image-capable review route** per
  C-012, after the site-observatory stream's image-critique rounds.
- **Invited-peer validation is allowed to overturn lead designs**; C-014
  recorded two lead designs overturned by an invited peer before
  implementation.

## The loop, end to end

Every substantial session runs one conductor procedure:

1. **Intake** — read `RUN_STATE.md` (the intake pointer), the task
   queue, the latest run report; never re-decide anything the decision
   log settled.
2. **Decompose** — split work into genuinely independent streams
   (disjoint expected diff footprints), one git worktree + branch each;
   assign each stream a review tier by *cost of being wrong*
   (measurement-semantics and contract-bearing work gets the full
   pipeline; docs get a light tier). Preflight gates: hardware-shaped
   streams require a confirmed device inventory; anything pinned
   without live validation carries a PROVISIONAL label; measurement
   sessions require a no-agent "quiet machine" lock.
3. **Per-stream pipeline** — for each reviewable unit: an invited
   design-argument round (the implementer must argue trade-offs before
   coding), implementation, then a layered review stack:
   2–3 fresh-instance counterreview lenses over the diff → lead triage
   with recorded dispositions → fixes → a dedicated test-amplification
   round (an independent writer adds edge-case tests) → a
   writer≠reviewer test audit (a fresh instance hunts tautological,
   vacuous, or wrong-expectation tests) → the lead's diff gate.
4. **Lead live gates** — never delegated: the lead runs the real flow
   (real corpus, real CLI, real hardware where present). This layer has
   repeatedly caught blockers no other layer saw, including defects
   whose own tests were green because the tests encoded the same wrong
   assumption as the code.
5. **Merge gate** — multi-commit series land as branch + PR. Before any
   merge: a pre-merge oversight pass by 2–3 fresh reviewers with
   distinct angles (deep regression hunt; claim-to-evidence trace;
   merge-order simulation across sibling PRs), lead triage, fixes, CI
   green. **Final-head rule:** any commit that lands after the last
   review round gets one more fresh review before merge — no commit
   merges unreviewed, however small (its first application caught a
   crash path in a "trivial" post-review fix).
6. **Integration review** — after parallel streams merge, one dedicated
   review hunts *interaction* defects no single-stream review can see.
   Its catches are definitionally unique (first outing: two).
7. **Bookkeeping** — a single session record (run report) with a
   verbatim process-trace appendix; the intake pointer and queue
   refreshed; a delegated docs-consistency sweep before the final
   commit (its latest pass found 15 real drift items; earlier passes
   found 5–6). Large documentation batches add the pre-commit
   docs-verify mode; the `consistency-sweep` skill owns that shape,
   including the D-043 supersession check.
8. **Same-session distillation** — lessons fold into the process
   playbooks the same session they are learned. Measured effect: one
   failure mode recurred five times before its fix was distilled, zero
   times after. The current operation-loop also runs its §0
   primary-deliverable check and §8 shipped-check before the session is
   considered done.
9. **Post-landing verification and close-out** — landed work gets the
   matching verification workflow with severity-tiered refuters. Sessions
   that change front-facing state refresh `docs/site/DRIFT.md`; no agent
   regenerates or deploys the site. Automation informs and Ed deploys
   manually, per D-068 and `RUN_STATE.md` end-of-work step 8.
10. **Meta-review (the final step)** — event-driven, not calendar-driven:
    when a review layer stops earning its keep, when an intervention
    repeats despite a folded fix, or when the user asks, the loop is
    reviewed with its own evidence discipline (see Topology for the
    consensus one such review produced). After large workloads the
    post-large-workload meta-reassessment (owned by operation-loop §10)
    always fires, and it runs LAST.

### Stop cards and paused work

When a session stops with live work in progress, the lead creates or
updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
that card is the single restart authority and overrides every lower
"what next" list, queue rank, mission guide, and run-report default.

A stop card must name:

- the resume authority and exact artifact pointer,
- the reason for stopping,
- worktrees, branches, PRs, and off-repo artifacts that must not be
  cleaned accidentally,
- status terms for each paused item,
- the first resume action, and
- the clearance criteria.

Use these status terms for paused work:

| Term | Meaning |
|---|---|
| `APPLIED_UNVERIFIED` | A worker reports code or docs are applied, but the lead has not gated the diff. Not merge-safe. |
| `LEAD_GATED` | The lead has reviewed and run the required local/live checks for the item. |
| `PR_OPEN_CI_GREEN` | A PR exists and CI is green, but merge authority has not yet fired. |
| `MERGED` | The accepted work has landed on main. |
| `UNREAD_UNADJUDICATED` | A report/synthesis exists but has not been consumed into decisions, queue rows, or rejected findings. |
| `ADJUDICATED` | Findings have explicit accept/reject/defer disposition and downstream artifacts are updated. |

Before an intentional pause, do the minimal stop sync even if full
bookkeeping cannot fit: update only `RUN_STATE.md`'s stop card and the
rank-0 queue row. That is enough to prevent accidental bypass.

## The artifact system (where rigor becomes auditable)

Each fact has exactly one home; everything else points at it:

| Artifact | Role |
|---|---|
| `docs/decision_log.md` | Binding design decisions, each with alternatives considered, consequences, and revisit conditions. The log is the count authority; nothing re-decides these silently. |
| `docs/council_log.md` | The deliberation record: review-council positions, reasoning exchanged, who prevailed, overridden dissents — so a future reader can reconstruct *why*, not just *what*. The log is the range/count authority. |
| `docs/contracts/` | Claim/evidence contracts: `claims_ladder.md` (D-037) plus `analysis_plans.md` (D-038) form the claim gate; strict validation is the evidence ticket. |
| `docs/stream_logs/` | Per-stream decision ledgers, committed WITH the code they justify: every non-trivial in-stream decision (`A-1..A-30`, `B-1..B-46`, …) with mandatory evidence pointers; wrong pins are SUPERSEDED in place, never erased. |
| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
| `docs/process/state_kernel.json` | Source of truth for work selection: active gates, dependencies, and machine-state lanes ([QUIET-MAC] / [AGENT] / [ED-EXTERNAL]). |
| `TASK_QUEUE.md` | Generated detailed queue projection plus dated history; do not hand-copy its live rows into reader docs. |
| `RUN_STATE.md` | Intake pointer with the generated restart projection. History lives in run reports. |
| `docs/risk_register.md` | Live risks with triggers and mitigation states. |

Instrumentation ledgers close the loop on the process itself:

- **Per-layer yield:** every review layer's unique catches are
  attributed and tallied per session under D-061 (C-027; replaces the
  earlier two-zero-sessions auto-drop, which the integration-review
  zero/zero/five sequence falsified): applicability is decided by
  PRE-DECLARED mechanical predicates; outcomes are classified
  accepted-unique-defect / duplicate / clean-verification /
  false-positive-suppression (suppression is not a catch); severity
  weights are fixed before the session; three applicable exposures
  TRIGGER an expected-loss review decision, never automatic deletion;
  safety/final-head/integration layers are never auto-dropped on
  zero-defect streaks. (One layer, the default specialist review lens, was
  dropped under the old rule before D-061.)
- **Delegation calibration:** every delegated unit gets a row — task
  altitude (pinned-spec / design-freedom / judgment-call), outcome
  (assigned by the lead after the gate, never self-labeled), catches,
  and lead rework minutes, with prompt-defects separated from
  model-defects. Delegation boundaries move on this evidence, not
  vibes. Current signal: pinned-spec delegation runs essentially
  defect-free; the serious defects cluster in volunteered additions and
  design-freedom wire contracts — which is exactly where the full lens
- **Invocation manifest:** substantial delegated/tool/skill runs get a
  lightweight manifest row per invocation. Minimum fields:
  `run_id`, `parent_report`, `role_or_lens`, `model`, `wrapper`,
  `session_id`, `prompt_sha256`, `prompt_path`, `output_path`, `status`,
  `consumed_by`, `disposition`, and `commit_or_pr`. Raw logs can stay
  out of git; every ephemeral artifact still needs a committed pointer
  row with `path`, `sha256` or stable id, `promoted_to`, and
  `not_promoted_reason`.

## Council discipline

Councils are expensive instruments. Use a full council for methodology,
measurement validity, schema/contract changes, claim boundaries, hardware
protocols, or explicit user requests. For ordinary implementation, use a
small number of targeted lenses plus lead adjudication.

Every high-impact council must leave a durable scorecard:

- unique catches by severity,
- accepted/rejected/deferred/false-positive counts,
- lead triage and rework time when practical,
- shipped artifacts,
- queue rows created or re-ranked,
- decision-log IDs promoted, and
- a disposition table: finding → ruling → owner → artifact/queue/decision
  target → closure check.

Deferred decision-log promotion is itself a tracked obligation, not
ambient prose in a report.

## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)

The following policy text is the R2-ratified section, landed verbatim per
audit work order WO-022 (`docs/reviews/2026-07-13-comprehensive-audit/`).

SPEND GUARDRAILS (capstone benchmark bands) — provisional calibration constants; review after two completed arcs; sunset at capstone submission.

1. ACCOUNTING SOURCE. Sol spend: `codex-usage` local accounting (the standing snapshot convention), corroborated by codex-run-v3 manifest `token_usage` rows where populated. The extraction window must cover the full arc — sum incremental snapshots for multi-day arcs; a single trailing-24h view is insufficient. Fable spend: estimated from local usage accounting; each snapshot names its method and price-table version. Price table v2026-07 (pinned until amended): GPT-5.6-sol $5/$30 per M in/out, cached input $0.50; Fable 5 $10/$50, cache reads $1. All figures are estimates, not billing truth, and are recorded as such. Missing data is recorded as `accounting_unknown`, never as zero.

2. DENOMINATOR AND CACHED-TOKEN TREATMENT. Token bands count total tokens (cached + uncached, all directions) exactly as codex-usage reports them — cached tokens are never excluded (exclusion invites cache-heavy gaming). Dollar figures apply cached pricing honestly. Cross-family aggregate ceilings bind in combined estimated dollars, because raw cross-family token sums are not commensurable (C-028: Sol ~180x the token volume, Fable ~3.4x the cost).

3. BOUNDARIES AND ATTRIBUTION. An arc = one council-log C-row, opened at its first delegated session, closed at its closeout snapshot. A work order = one WO/task id. Failed calls, retries, resumes, refuters, fix rounds, delta re-audits, lead usage, and subagents all count against the initiating WO and arc. Arcs and WOs may not be split, renamed, or reopened to reset counters.

4. BANDS. Each dimension is independent. SOFT crossing = record-and-continue: flag in the spend snapshot plus a one-line justification in the council row. HARD crossing = pause-and-ask Ed before any NEW delegated work in that category; in-flight sessions finish; quiet-machine measurement is never interrupted.

   | Scope | Soft | Hard |
   |---|---|---|
   | Sol high session | 6M tokens | 12M |
   | Sol xhigh session | 8M | 16M |
   | Sol ultra session | 40M | 60M |
   | Bench-effort WO | 10M / 3 Sol sessions / ~$40 combined | 20M / 6 / ~$80 |
   | Session-effort WO | 30M / 8 Sol sessions / ~$100 combined | 60M / 12 / ~$200 |
   | Arc | 100M / 25 Sol sessions / ~$400 combined / 6 Sol active-hours / 2 elapsed days | 200M / 40 / ~$800 / 12 h / 4 days |

   WO dollar figures are best-effort: when per-WO Fable attribution is accounting_unknown, the token/session pair binds. Ultra: at most 2 INTENDED ultra sessions per arc, each with a pre-run recorded statement of why xhigh is insufficient and what bounded subagent work it will perform; an unintended ultra is recorded as an anomaly and still counts.

   Calibration anchors (recorded so recalibration stays honest): healthy xhigh ≈ 2.3–3.5M tokens/session (C-030 post effort-fix; C-028 average); the recorded broken state averaged ~9M. C-028 (330.6M / 59 sessions / ~$1,050 / ~17.5h) crosses every substantive arc HARD dimension — it is the anti-example. The 2026-07-13 comprehensive audit (~30 Sol sessions + ~70 Fable agents, Ed-authorized) crosses arc SOFT on session count only — the intended "exceptional: justify and continue" outcome.

5. CHECKPOINTS (procedural; owner = the Fable lead). (a) At arc open: predeclare one accepted deliverable increment for the arc — a corpus/measurement result, analysis/figure/report increment, evaluator requirement, or cited advancement of a D-060 gate — and classify planned delegated work as deliverable-facing or process-facing (mixed sessions count as process-facing unless separately attributable). (b) Before each next delegated call: check the completed session against its tier band (a lightweight glance, not a full snapshot); no runtime killing is promised — evaluation happens on completed sessions before any resume, replacement, or new call. (c) At WO close and arc close: take the spend snapshot and evaluate all bands. One missed checkpoint blocks new process-facing delegation until reconciled.

6. DELIVERABLE-PROGRESS TRIPWIRE (binds while ANY D-060 gate is unmet). If process-facing combined estimated cost exceeds 33% of arc cost OR $250 — whichever occurs first — HARD pause-and-ask Ed before further process-facing delegation. Independently, an arc that closes with process-facing spend but NO accepted deliverable increment pauses further non-exempt process work even if the 33% threshold was not crossed.

7. EXCEPTIONS AND OVERRIDES. Gate-closing work is deliverable-facing by definition. Correctness-defect and data-preservation work may override the allocation tripwire but is always fully counted. Ed direction is NOT a blanket exemption (the finding's own exemplar — bridge v1/v1.1 — was Ed-directed): it is a recorded override carrying an incremental budget and an expiry, and its spend counts.

8. NAMED-FAILURE BAR FOR PROCESS INNOVATION. Any NEW process layer, tool, skill, wrapper version, or contract version requires a decision-log entry citing: (a) a named recorded failure it addresses, (b) why existing controls did not cover it, (c) the smallest new layer that does, (d) its applicability predicate, (e) its marginal budget, (f) a sunset/retirement condition. Absent that entry, it is D-060 breadth and waits for the gates.

9. KEEP-DEFENDER GUARANTEE. No cap consequence auto-deletes a review layer. Layers with recorded unique catches survive any cap; a cap response batches, rescopes, or seeks Ed approval — never silently drops catch-bearing gates (final-head, integration, lead-live, claim/evidence safeguards).

10. MECHANISM. This policy is PROCEDURAL, not mechanical: no checker script is built now (adding process code during an overengineering correction is self-defeating; the arithmetic is a handful of numbers already recorded at existing snapshot points). Two recorded accounting discrepancies or skipped checkpoints across two arcs constitute the named failure that authorizes an executable checker with tests — via the §8 bar.

11. RECALIBRATION AND OWNERSHIP. Band values are calibration constants: the lead may amend SOFT values at arc close with evidence via a one-line decision-log amendment; HARD values and this section's structure are Ed-owned. Scheduled review after two completed arcs. The whole policy sunsets at capstone submission.

Court amendments (T09, folded at the register): canonical session
inclusion uses manifest-corroborated sessions with known token records;
resume rows are deduplicated; non-manifest sessions are reported only as
a labeled upper bound. The 2026-07-13 audit anchor in section 4 is
estimated/accounting_unknown until an audit-close spend snapshot receipts
it (docs/reviews/2026-07-13-comprehensive-audit/receipts/
WO-022-audit-close-spend.json); only a receipted anchor may be used for
recalibration.


exec
/bin/zsh -lc "sed -n '50,145p' docs/agent_playbook.md && sed -n '2077,2248p' RUN_STATE.md && sed -n '2790,2895p' RUN_STATE.md && sed -n '300,420p' TASK_QUEUE.md && rg -n 'Do-Not-Do|DO NOT DO|Do Not Do|What Is Next|What is next|Next exact|NEXT' TASK_QUEUE.md RUN_STATE.md | head -80" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
## Mission M0: Preflight (every session)

1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
   if present, "Current Project Status", "Known Workspace State", and
   "What Is Next". If the stop card is ACTIVE, it overrides this
   playbook and the task queue until cleared.
2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
   only at phase starts or when the project structure changes. Consult
   `docs/decision_log.md` by targeted decision ID, not as a whole-file
   intake step.
   If the session involves delegation, review, or multi-stream work, also
   read `docs/orchestration.md` (the process layer) — not optional for
   landing code.
4. Check workspace state with `git status --short --branch`; inspect
   recent commits only when the handoff or mission needs them.
5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   (skipped=10)` with zero expected failures as of 2026-07-08 after
   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   optional-jsonschema test. A red suite is itself the mission: stop and fix
   or report.
6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   when a trigger fires, or if >14 days passed since the last run report
   with no break recorded in `docs/milestones.md`.
7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   write a dated run report in `docs/run_reports/`, update the phase exit
   checklist for anything that closed, and `PROJECT_STATUS.md` if
   advisor-visible state changed. Commit when the user asks or has
   standing-approved it.

Environment cautions:

- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
  see `Operation not permitted` on reads inside the repo, stop, wait for
  the lock to clear, re-run the suite, and record the incident.
- CI installs no extras; every new test must pass on a bare Python
  (lazy imports, `skipUnless` for optional deps — D-009).
- Schema changes are additive-only until v0.2 (R-015/D-008).

---

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
  failures implemented on top of it. 2N.6's CLI verb rides along.
- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
  (token-count fallback), 2N.9 (v0.2 compatibility note).

If a session ends mid-slice, a completed commit group is a clean
handoff point — say which group landed in `RUN_STATE.md`.

Per-item detail (each item = tests green before the next; items 1+2
change the controller/adapter contract and go first):

### 2N.1 `RunContext` seam + raw evidence

- Today: `RunBundleWriter._ensure_layout` creates `raw/` (bundle.py
  ~line 160) but no method writes into it, and adapters never see the
  bundle path — so a real telemetry adapter cannot honor D-002 ("raw
  file retained verbatim").
- Change: implement **D-024** (already decided — read it first): an
  immutable `RunContext` dataclass (config, clock, run_id, bundle_path,
  raw_dir, logs_dir, outputs_dir, optional node_role=None) constructed
  by the controller after bundle creation and passed to adapter
  lifecycle methods (exact placement — per-method parameter vs
  construction-time — is yours to pin; record the choice as a D-024
  amendment note). Add `RunBundleWriter.raw_path(name)`/`write_raw` as
  the writer-side counterpart (validated, collision-checked). Update
  `docs/contracts/adapter_contracts.md` in the same run. Do NOT hand
  adapters the writer itself — D-024 rejects that option; context is
  data, not capability.
- Tests: mock telemetry writes a fixture raw file via the context;
  bundle contains it; immutability (no overwrite after finalize); the
  no-raw-output mock path still passes; mocks ignore unused context
  fields (single lifecycle code path preserved).

### 2N.2 Measured window excludes sampler startup

- Today: `stage_started(measured_run)` is timestamped before
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05). Latest report: [16h runway checkpoint 2026-08-03: D-108..D-112 minted; kernel pins 60; CAL-BRACKET held at 2e61ff9 (rule-11 gate owed for B1 round 2); winB license exhausted as drawn (r06 disposition parked, WINB-R06-DISPOSITION-01); mint chain D-110-blocked; CLAIMS_STATUS §1 honestly NONE; checkpoint block at the top of RUN_STATE is the successor resume script.](docs/run_reports/2026-08-03-16h-runway.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q2 `P2-006`: Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.

### [AGENT]

- READY — A0 `P2-035`: RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).

<!-- END GENERATED: state-kernel run-state-intake -->

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

The RESUME list from the 2026-07-17 checkpoint is fully executed. The
relaunched execution-lens review, fix rounds 1-2, and their delta
re-audits had already run earlier on 2026-07-18 (commits `1aebf14`,
`6d80039`); this session closed the surviving P1 (child accepted any
JSON object as the frozen cooldown anchor) plus every finding from four
further delta re-audits, as fix rounds 3-8 in commit `ad0920b`:
canonical anchor validator (`joulewise/cooldown_anchor.py`) enforced
fail-closed at parent/CLI/controller boundaries; collision-safe,
crash-atomic, flock-serialized rejection-verdict custody
(`experiments/rejections/`); physical-domain baseline validation (the
`inf`-anchor fail-open gate is closed); discriminating process-race
regression. Suite green lead-side at every round boundary, final
`Ran 1746 tests`, `OK (skipped=12)`. Awake-half live probe validation
passed on real hardware (zero probe errors); the Ventura screensaver is
now disabled on the machine (`idleTime = 0`). PR #77 carries the gate
narrative; merge is Ed's call. Full record:
`docs/run_reports/2026-07-18-d077-fix-rounds.md`. Tooling: codex-run-v3
xhigh review-genre sessions ended with null final messages 4x
(bridge-resume recovered each; personal-tooling defect, recorded in the
run report and the global codex-delegation skill field notes, not the
repo queue).

## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task

The actual Claude Code fallback route is `scripts/codex-bridge`, not the MCP
server for recent audited work. The wrapper now sends `new` and `review` turns
through a dedicated app-owned Codex desktop task when the local host id is
configured. This is the same local-conversation state the native pet consumes;
the prior observer-only diagnosis was incorrect because the pet never reads
`~/.codex/claude-spawned/index.jsonl`. A live Sol/high smoke appeared in the
Codex app as thread `019f77a6-3612-7332-9f5e-be9fbde56be5`, turn
`019f77a9-2827-7de1-accf-ac2eda21927e`, and returned
`JOULEWISE_NATIVE_PET_BRIDGE_OK` through the script. Adaptive effort remains
unchanged: `high` fallback/default, `xhigh` only on named hard-task triggers,
and `ultra` only for sessions that must spawn subagents. Full record:
`docs/run_reports/2026-07-18-claude-codex-pet-observer.md`.

Committed 2026-07-18 on `impl/env-guard-cooldown` (after the D-077
packet boundary `6d80039`) with a lead execution review at the bench:
IPC socket ownership/permission checks, PID-checked host-task lock,
interrupt-on-terminate, no-network sandbox policy, and one-hop rule all
verified in `scripts/codex-app-bridge.mjs`; real-socket fake-router
tests plus observer lifecycle tests included; canonical suite green
lead-side (`Ran 1722 tests`, `OK (skipped=12)`). The same commit
carries the doctor-driven CLAUDE.md trims (global + repo; content
deduplicated into `.claude/skills/codex/SKILL.md`, which is the
operating home) and stamp-only `docs/site/*.html` provenance refresh.

## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending

Window A floors contamination diagnosed from primary data: macOS Ventura
*video* screensaver on an awake display contaminated 43/50 suite-calibration
bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on
unlock — pmset assertion log corroborated to the second). The six "low"
su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative
suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The
professor's power-source hypothesis is refuted (AC/140 W/100% throughout).
Details: memory note + `docs/run_reports/2026-07-17-environment-guard.md`.

Branch `impl/env-guard-cooldown` (pushed, commit e2813ee) holds the D-077
response: environment-guard preflight (+`--arm-quiet-mode`), per-run idle
admission gate, cooldown v2, unwaivable `environment_admission_failed` claim
barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh,
thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh
(thread 019f7362-6627, resumed via codex-bridge after an MCP transport
timeout); session-close scope check SCOPE_OK; full suite green lead-side
(OK, 12 skips). Lead bench fix included: `pmset -g systemstate` parser now
accepts the live "Capabilities are:" form (was null → fail-closed on real
hardware); fixtures pinned to verbatim live output.

RESUME (in order):
1. Relaunch the adversarial review round (was stopped mid-run at checkpoint):
   fresh read-only Sol xhigh, execution lens, over `git diff main...impl/env-guard-cooldown`
   (prompt shape in `.codex-bridge/` prompt snapshots); lead holds the
   contract lens (done for cooldown_gate/claim-barrier/anchor hunks).
2. Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.
3. Live-validate flagged probes during next quiet-window prep:
   `pmset -g systemstate` display-asleep form + screensaver-engaged probe
   while a screensaver is actually running (run report flags
   `live_validation_provisional`).
4. PR per operation-loop §5 gate shape; then re-run suite ABBA calibration
   under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for
   suite comparative cells must be recomputed/caveated pending re-run.

Status: **CLEARED 2026-07-11.** Every clearance criterion met: all
checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037
audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion +
delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening
PRs #50-#53 merged after the cross-stream integration review over the
combined tree (38 pre-merge cross-stream failures caught and fixed; 1
review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 →
queue row P2-049); DOC-008 kernel refreshed at final head (schema v2,
authority field, branch impl/doc008-kernel awaiting PR); bookkeeping
arc complete (run report, C-028 council entry with layer catch-rates
and ~57-invocation spend record, D-064 ratified incl. manifest v3 +
claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled;
consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008
MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.

## Superseded stop card (CP-5)

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

## Current Project Status

**Mint era OPEN AND FIRST MINT LANDED (2026-07-30): main `da83337`. The
data exists and passes, and the code path that turns it into a published
floor now exists and has been exercised — `df-ph-decode-floor-mint1` is
mainline.**

### The central measurement fact (read before any measurement decision)

The instrument is **attribution-limited (~1 J), not noise-limited
(~0.3 J)** — D-078 clause 11, Ed-ratified. Floors publish LABELLED with
the widened number; the point floor is a repeatability diagnostic that
may never be the published claim floor. The anchor term appears in
**both** the floor and each claim's decision interval, so the effective
clearable effect is floor + claim-side bound ≈ 5 J for phase contrasts,
and neither term may later be deleted as an apparent double count. Do
not launch an instrument-tightening program; it was measured and
eliminated.

### Collection state

| Window | Contents | Verdict | Notes |
|---|---|---|---|
| a9, a10 | earlier corpora | **PASSED** | a10 supplies the absolute component |
| **B** (`04_phase_prefill_abba`) | 40 prefill ABBA members, 59/59 collected clean | **FAILED** | `instrument_calibration_mismatch`, bracket drift 11.581436 ms; preserved, not claim-bearing |
| **C** (`05_phase_decode_abba`) | 40 decode ABBA members, 59/59 collected | **PASSED** | bracket drift 1.279 ms; first comparative window in project history to pass |
| **D** (absolute) | 30 claim members, 49/49 collected | **PASSED** | bracket drift 0.484 ms, tightest of the campaign |
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is OPEN and unblocked as of 2026-08-02 (gauntlet closed PR #93; D-088 no-mint condition lifted), so these figures live only in prose plus the out-of-repo custody extraction until that mint runs |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95); the gated claim now rides `MINT-GENERALIZE-01` then the D-095 chain |

**2026-08-07 supersession (D-117):** the historical a10/re-mint and old
C/D plan are retired. Claim authority can now arise only from the
prospective alpha, beta, and gamma windows; the separately named Window C
## Known Workspace State

- (2026-08-02, CURRENT) `main` and `origin/main` at `bcbc10b`; working
  tree clean except the untracked private `CLAUDE.local.md` (Ed's;
  never commit) and `.desk/` (adjudication custody; never commit).
  PR #93 merged (the c3 branch is closed). Branch
  `impl/d100-bii-binding` exists in the session worktree
  `scratchpad/d100bii` holding the UNCOMMITTED, audit-pending
  D100-BII-BINDING-01 diff (envelope protocol failure; see §9).
- (2026-07-31, historical) `main` and `origin/main` were both at `6ed1625`:
  the PR #89 merge `7ee680c` (D5-J) plus the close-out commits
  `49c1876`, `0d0bd0b`, and `6ed1625`. Branch `impl/mint-tool` is MERGED
  (verified `git merge-base --is-ancestor impl/mint-tool main`), as are
  `impl/floor-mint` and `impl/floor-label-clean`; all three may be
  deleted. Their scratchpad worktrees are still registered (`minttool`
  plus ~11 review/pin worktrees under the `9c166892…` session dir, and
  prunable entries under `ad48bfae…` and `d714f367…`) — `git worktree
  prune` plus explicit removal is owed as housekeeping. The working tree
  is clean except for the untracked private `CLAUDE.local.md` (Ed's
  file; never commit it).
- (2026-07-28 late, historical) `main` and `origin/main` were at that
  session's bookkeeping commit atop the PR #87 merge `058c918`. Branch
  `impl/mint-tool` (pushed, then UNMERGED) held the 9-commit mint series
  `2a0ecbc..697f741` in worktree
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool`;
  canonical suite at its head `1d83d68` is UNVERIFIED (rerun was in
  flight at checkpoint). Branch `impl/floor-mint` is merged via PR #87
  and may be deleted. NOTE: a concurrent session force-rewrote main
  history this evening (content preserved; see run report Anomalies) —
  verify `git log` freshness before building on a cached head.
- (2026-07-27, historical) `main` and `origin/main` were at `7337b33`. Branch
  `impl/floor-mint` @ `617060a` is pushed and NOT merged; it carries the
  pre-mint floor schema hardening. Window C (+bound) and a10 (+bound)
  remain FULLY resident in the working tree (mint #1 inputs); windows B/D
  and all other runs corpora are locally pruned to small evidence files
  (traces archived + verified in iCloud, see "Disk" above), and custody
  material lives OUTSIDE the repo at `~/JouleWise-window-custody/` — an
  agent searching only the repo will wrongly report quarantined evidence
  missing. Disk has 115 GB free; a window writes ~6 GB. The next quiet-window operator must start
  from a separate clean, merged-main measurement checkout per
  `docs/phase_2/window_runbook.md`.
- The generated state-kernel regions in this file and `TASK_QUEUE.md` are
  IN SYNC with `docs/process/state_kernel.json`
  (`python3 scripts/gen_state.py --check` exits 0), and the kernel's own
  content was refreshed on 2026-08-01 (desk adjudication session):
  stamped `updated: 2026-08-01`, `latest_report` points at
  `docs/run_reports/2026-08-01-desk-adjudication-session.md`, the MET
  rows are folded in, the completed
  `FLOOR-LABEL-01`, `STACK-ID-BIND-01`, `P2-015`, and
  `COOLDOWN-JOIN-DA1-01` rows are retired to
  `TASK_QUEUE.md`'s completed table, and the post-mint intake
  (`COOLDOWN-JOIN-GAUNTLET-01`, `MINT-GENERALIZE-01`,
  `MANIFEST-CONTRAST-01`, `SUPERSESSION-DUP-REFUSAL-01`,
  `QA-10A-JOIN-OMISSION`, `QA-10B-EXISTING-RETRY`) is folded in. Any
  further change means editing the kernel and then running
  `python3 scripts/gen_state.py` — never hand-editing the generated
  regions.
- (2026-07-25, historical) `main` and `origin/main` were at `c3e2647`,
  the PR #85 merge; PR #79's repair and PR #85's SCREEN+BUDGET
  implementation both landed with green final PR-head CI.
- The generated state-kernel blocks are authoritative for work selection.
  Hand-authored `RUN_STATE.md` and `TASK_QUEUE.md` text remains authoritative
  only for its own factual, policy, and historical domains;
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

The comprehensive whole-project audit is the declared gate (Ed,
2026-07-13): method proposal pending Ed's approval, then the audit runs
and its findings are adjudicated before any further feature work. After
that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE,
then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads
P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet
windows. `TASK_QUEUE.md` remains the ordering authority.

Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from
C-027 apply at live promotion), wall meter (P1-003), topology (P1-004),
calendar mapping (P1-008).

## Reference Decisions And Blockers (non-selection context)

These pointers retain external-dependency context but do not rank or select
work. The generated region controls task selection.

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
| EXACT-SET-REGRESSION-01 | P2 Next Slice | [AGENT] | Review finding **S2** — exact-set regression. **Detail owed** (same caveat as B2): the ledger names the row but not its content. Likely adjacent to D-086 root cause 1 (exact-set vs governed-subset matching when `--evaluation-basis-sha256` is omitted), but that adjacency is **inference and must be confirmed against the packet**, not assumed. | Not yet acceptance-specified — promote to READY only after the S2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph |
| COLLECTOR-NIT-B1 | P4 Polish | [AGENT] | Review finding **B1** collector nit (distinct from the refuted B1 `device.boundary` placeholder finding — do not conflate). **Detail owed**, same caveat as B2/S2. | Not yet acceptance-specified. | Session ledger, F2 disposition paragraph |
| SITE-ROADMAP-PAGINATE-01 | P3 Tooling | [AGENT] | Paginate or shard the site roadmap page: `roadmap.html` emits one card per live kernel row and now sits at 29,620 of the 30,000-byte capsule shard budget (98.7%) after the 2026-07-30 kernel fold — the NEXT intake fold breaks `CapsulePackError`. | `build_site` succeeds with at least 10 additional live kernel rows; no shard exceeds budget; existing roadmap content preserved. | Kernel-refresh finding 2026-07-30 (session report) |
| DOC-RUNSDIR-ABS-01 | P4 Polish | [AGENT] | Tool contract doc note: the extraction CLI's `--runs-dir` **must be an absolute path**. Document it at the tool contract, and consider a fail-closed check rather than leaving it as operator lore. | Doc note landed; optionally a refusal on a relative `--runs-dir` with a regression. | [D-086](docs/decision_log.md) (queued from lieutenant findings) |
| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |

## Current Queue

The generated region below is the sole live queue and source of truth for
work selection. Edit the kernel and regenerate; do not hand-edit its rows.

Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see `docs/contracts/analysis_plans.md` §Required fields.

Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see `docs/specs/c027/rpt-001_report_vertical_slice.md` §0.4 and `docs/contracts/publication_privacy.md` §Publication boundary.

<!-- BEGIN GENERATED: state-kernel current-queue -->
<!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. -->

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05).

Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY [ED-EXTERNAL] | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY [ED-EXTERNAL] | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY [ED-EXTERNAL] | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY [ED-EXTERNAL] | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY [ED-EXTERNAL] | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY [QUIET-MAC] | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC] | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY [QUIET-MAC] | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) [QUIET-MAC] | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |
| A0 | P2-035 | P3 Research Expansion | READY [AGENT] | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 [AGENT] | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY [AGENT] | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY [AGENT] | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY [AGENT] | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY [AGENT] | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY [AGENT] | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) [AGENT] | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY [AGENT] | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY [AGENT] | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY [AGENT] | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT] | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT] | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) [AGENT] | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) [AGENT] | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 [AGENT] | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 [AGENT] | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) [AGENT] | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY [AGENT] | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY [AGENT] | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY [AGENT] | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT] | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY [AGENT] | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY [AGENT] | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY [AGENT] | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 [AGENT] | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED [AGENT] | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED [AGENT] | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED [AGENT] | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED [AGENT] | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED [AGENT] | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED [AGENT] | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY [AGENT] | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY [AGENT] | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY [AGENT] | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY [AGENT] | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY [AGENT] | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY [AGENT] | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
| A52 | D080-TRIGGER-01 | P3 Hardening Candidates | BLOCKED — D-080-amendment (Ed ratifies the trigger cadence and the runner (cron routine vs manual)) [AGENT] | Wire D-080's standing fresh-eyes sweep to a REAL trigger (calendar cron or every-N-merged-PRs), run as a separate concurrent read-only instance per the Ed-validated 2026-08-03 pattern, findings delivered mid-flight; reconcile D-080 clause 4(ii)'s stale zero-unique-catch citation. | The fresh-eyes sweep fires without anyone remembering it, on a ratified cadence, as a concurrent read-only instance. Evidence: A ratified trigger exists (cron routine or PR-count hook) and has fired at least once; D-080 clause 4(ii)'s stale citation is reconciled by amendment. Authority: [D-080 + the 2026-08-03 sweep finding (never fired) + Ed's concurrent-audit validation](docs/decision_log.md). Acceptance: [D080-TRIGGER-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-03: minted from the two-week soundness sweep's finding that D-080 has never fired, plus Ed's validated concurrent-audit pattern (memory: concurrent-fable-audit-pattern). Non-blocking hardening. |
| A53 | CGV-HARDEN-01 | P3 Hardening Candidates | READY [AGENT] | Harden runner-owned receipt persistence after validator --receipt-out removal: use a dirfd-relative receipt write that closes receipt-write TOCTOU and supplies fsync plus directory-sync atomicity. | The convening runner durably persists validator receipts through a dirfd-relative, crash-atomic, fsync-complete write path. Evidence: The convening runner persists the validator receipt with a dirfd-relative write that closes the receipt-write TOCTOU; Receipt publication is atomic and includes file fsync plus parent-directory sync; Regression tests distinguish path replacement, durability failure, and successful atomic publication. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 receipt-persistence disposition](docs/process_traces/2026-08-05-cgv-f3-consult/SYNTHESIS.md). Acceptance: [CGV-HARDEN-01 acceptance](docs/process/state_kernel.json). Fence: Keep this row a sibling of COLDGATE-HANDOFF-01 and never merge them: durable receipt storage and validated-byte judge handoff have different contracts, tests, and failure consequences (2026-08-05 F3 consult Q2 dissent). Note: 2026-08-05: runner-scoped because PR #103 removed the validator's --receipt-out; deliberately registered as a sibling of, never folded into, COLDGATE-HANDOFF-01. |

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

### [ED-EXTERNAL] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |

### [QUIET-MAC] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |

### [AGENT] lane

| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| A0 | P2-035 | P3 Research Expansion | READY | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
RUN_STATE.md:1761:6. NEXT (in order):
RUN_STATE.md:1970:Historical NEXT (superseded by the block above): (1) close the two
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
TASK_QUEUE.md:302:| SITE-ROADMAP-PAGINATE-01 | P3 Tooling | [AGENT] | Paginate or shard the site roadmap page: `roadmap.html` emits one card per live kernel row and now sits at 29,620 of the 30,000-byte capsule shard budget (98.7%) after the 2026-07-30 kernel fold — the NEXT intake fold breaks `CapsulePackError`. | `build_site` succeeds with at least 10 additional live kernel rows; no shard exceeds budget; existing roadmap content preserved. | Kernel-refresh finding 2026-07-30 (session report) |

exec
/bin/zsh -lc "rg -n -i '"'^## .*what.*next|''^## .*next|''^what is next|''^## current do-not-do-yet list'"' RUN_STATE.md TASK_QUEUE.md && sed -n '210,306p' TASK_QUEUE.md && git diff --stat origin/main...HEAD && git diff --name-status origin/main...HEAD" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
RUN_STATE.md:2857:## Historical Next-Work Snapshot (superseded 2026-07-15)
- CI-003 developer polish (console script, macOS CI job, Ruff, coverage thresholds) — SHELF, trigger: G6-equivalent reference release (hardening adjudication C10).
- DOC-010 historical-archive audit — SHELF, trigger: DOC-008 state kernel proven in use (hardening adjudication C11).

## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update live status, rank, dependencies, and new tasks in
  `docs/process/state_kernel.json`.
- Remove terminal tasks from the kernel only after their owning completion
  evidence supports closure; preserve the dated Completed row here.
- Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
  restart rows.
- Keep hand-authored edits here to policy, completed/history records, and
  non-selection context.

## Intake Batch Owed To The Kernel (2026-07-30/31)

**PARTIALLY FOLDED 2026-07-30.** Six rows —
`COOLDOWN-JOIN-GAUNTLET-01`, `QA-10A-JOIN-OMISSION`,
`QA-10B-EXISTING-RETRY`, `MINT-GENERALIZE-01`, `MANIFEST-CONTRAST-01`,
and `SUPERSESSION-DUP-REFUSAL-01` — were folded into
`docs/process/state_kernel.json` on 2026-07-30; their staged rows were
removed from this table. Of the six, only `MINT-GENERALIZE-01` and
`SUPERSESSION-DUP-REFUSAL-01` remain LIVE as of 2026-08-02: the
gauntlet trio retired with PR #93 and `MANIFEST-CONTRAST-01` with
PR #95 (see the completed table).
`COOLDOWN-JOIN-DA1-01` followed on 2026-07-31 (D-093), in the same pass
that retired `P2-015` to the completed table and closed
`QUEUE-RECONCILE-01`; both of those staged rows were removed too. It was
short-lived as a live row: DA-1 closed later the same day inside the
gauntlet's commit 2 and `COOLDOWN-JOIN-DA1-01` is now retired to the
completed table (PR #91, `67d268a`).

**The rows that remain below are STAGED, not live**, and stay staged by
magistrate scope decision 2026-07-30 (the P2/P3/P4 residue is not
competing for this window's selection). Work selection is the generated
region below; nothing here competes with it until the magistrate folds a
row into `docs/process/state_kernel.json` and runs
`python3 scripts/gen_state.py`. They are recorded here — hand-authored,
outside the generated markers — so the 2026-07-29/30 arc's owed rows
cannot be lost between the ruling and the kernel refresh (kernel refresh
is magistrate-owned).

Sources: `docs/decision_log.md` D-083..D-093; `docs/council_log.md` C-039
addendum + addendum II; the delegated related-work sweep
(`docs/run_reports/2026-07-30-sweep-techniques.md`); the
`splitwise_decode_v1` campaign doc §2
(`docs/phase_2/splitwise_decode_campaign.md`, on main since `27ffc91`).

| ID | Priority | Lane | Task | Evidence / Acceptance | Authority |
|---|---|---|---|---|---|
| QA-1-COOLDOWN-LAUNDER | P0 Safety | [AGENT] | **CLOSED at `16c7af0` (FIX-10, 2026-07-30).** The fail-open declared-occurrence edge the FIX-9 delta re-audit found (a member declaring `bundle_ids: ["x", "x"]` with only one usable `physical_members` row resolved via the one-row fast path without the supersession matcher) is closed by declared-occurrence tallying; both defect-shaped regressions failed pre-fix and pass post-fix. The FIX-10 delta re-audit confirmed this shape closed while finding the two successor edges now carried as the LIVE kernel rows `QA-10A-JOIN-OMISSION` and `QA-10B-EXISTING-RETRY` (folded 2026-07-30; see the generated region below). | Closed: fast path licensed only at declared count exactly 1; regressions in `SupersessionAwareCooldownJoinTests`; lead-verified 48/48 focused. | [D-086/D-088](docs/decision_log.md); FIX-10 delta re-audit 2026-07-30 |
| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MDE-ADOPT-01 | P2 Next Slice | [AGENT] | Powered MDE for the **repeatability arm** + workload-sizing inversion: replace the informal repeatability statistic with δ\* = 2.80·σ_D/√m (α = 0.05, power 0.80) over ABBA pair differences, and size the pilot with m ≥ 2.80²·σ_D²/δ². Desk work on existing data; makes the ad hoc "+5 J claim-side" principled. | Floor computation carries a powered MDE for the repeatability arm with its α and power stated. **Hard boundary, do not cross:** this does NOT apply to the systematic arm — RSS composition is valid only for independent random components, and RSS-ing a worst-case attribution bound as if it were an SD is anti-conservative. `max(repeatability, corner) + drift` stays. | [Sweep-techniques top-10 #1 + §5](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MIN-WINDOW-RULE-01 | P2 Next Slice | [AGENT] | Minimum-window rule + loop-to-60 s for short phases: declare a duration-conditional validity domain (N× the powermetrics cadence; SPEC's 60 s reached by looping the workload if shorter) and **fail-close** phases below it. Attacks the attribution-dominated 6–14 J floors directly, since edge error amortizes with window length. | A declared, enforced validity domain with phases below it refused rather than reported. Note the coupling: changing workload duration resizes the science, so any loop-to-60 s change is a pre-registration change and therefore Ed's call (see `FLOOR-WORKLOAD-SIZING-01`). | [Sweep-techniques top-10 #3](docs/run_reports/2026-07-30-sweep-techniques.md) |
| BATTERY-CROSSCHECK-01 | P2 Next Slice | [QUIET-MAC] | Internal dual-instrument cross-check **before** any wall meter: validate powermetrics integrals against an independent on-device channel (battery/SMC drain over long windows; channel-sum vs package reconciliation) and publish the agreement bound **with its validity domain**. Narrows "never externally validated" without a purchase. | A published agreement bound with its stated validity domain. Caution carried from the same memo: embedded telemetry (BMC/SMC) must NOT be treated as a trusted second reference without its own characterization — the bound is a cross-check, not a calibration. | [Sweep-techniques top-10 #4](docs/run_reports/2026-07-30-sweep-techniques.md) |
| REFUSAL-VOCAB-RATIFY-01 | P1 Phase Gate | [AGENT] + magistrate | Ratification question, deferred out of cold gate F1: reordering the separation-validation phases would **alter refusal precedence**, which D-087 placed in "vocabulary-ratification territory". The refusal vocabulary needs a ruling before any reorder is attempted. | A ruling on the refusal vocabulary and precedence, recorded in the decision log; only then may a phase reorder be proposed. | [D-087](docs/decision_log.md); refusal-scope spec v1 (`ea16730`, on main via PR #88) |
| MOCK-SAMPLER-PROV-01 | P4 Polish | [AGENT] | (Cold-gate finding **F2**.) The mock runtime should emit **truthful sampler provenance**; today the integration tests rewrite metadata to inject a sampler — a test-honesty item. | Mock runtime emits real sampler provenance and the metadata-rewriting test helper is deleted. Mitigated meanwhile: mock bundles are already refused at claim binding by `MOCK_TELEMETRY_CLAIM_REFUSAL`, so there is no claim exposure. | [D-087](docs/decision_log.md) (F2 disposition) |
| COOLDOWN-JOIN-FIXTURE-01 | P4 Polish | [AGENT] | (FIX-9 delta re-audit finding **QA-2**.) No repository fixture composes the **real** supersession validator/reader with the cooldown join; the FIX-9 regressions stub the reader, which is adequate for join/matcher behavior and insufficient as custody-path closure. | A real validator-reader-join fixture exercising the composed custody path end-to-end. | [C-039 addendum](docs/council_log.md); FIX-9 delta re-audit QA-2 |
| MINT-TOCTOU-01 | P4 Polish | [AGENT] | (Audit finding **Audit-F1**, adjudicated QUEUE.) TOCTOU between the mint's pre-check and its authenticated artifact read. Requires concurrent mutation of a frozen input; a different signature from the FIX-8 defect class. | Either the read is made atomic with the pre-check, or the exposure is recorded as an accepted limitation with its precondition stated. | Session ledger, staged-mint section; D-087 sibling dispositions |
| FLOOR-ARTIFACT-SHA-PIN-01 | P2 Next Slice | [AGENT] | Review finding **B2** — artifact-SHA pin. **Detail owed:** the finding's text lives in the review packet, not in the session ledger; whoever promotes this row must restate the defect from the packet before it can be READY per the Ready/Shelf rule. | Not yet acceptance-specified — promote to READY only after the B2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph ("register at bookkeeping with … B2 artifact-SHA-pin row") |
| EXACT-SET-REGRESSION-01 | P2 Next Slice | [AGENT] | Review finding **S2** — exact-set regression. **Detail owed** (same caveat as B2): the ledger names the row but not its content. Likely adjacent to D-086 root cause 1 (exact-set vs governed-subset matching when `--evaluation-basis-sha256` is omitted), but that adjacency is **inference and must be confirmed against the packet**, not assumed. | Not yet acceptance-specified — promote to READY only after the S2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph |
| COLLECTOR-NIT-B1 | P4 Polish | [AGENT] | Review finding **B1** collector nit (distinct from the refuted B1 `device.boundary` placeholder finding — do not conflate). **Detail owed**, same caveat as B2/S2. | Not yet acceptance-specified. | Session ledger, F2 disposition paragraph |
| SITE-ROADMAP-PAGINATE-01 | P3 Tooling | [AGENT] | Paginate or shard the site roadmap page: `roadmap.html` emits one card per live kernel row and now sits at 29,620 of the 30,000-byte capsule shard budget (98.7%) after the 2026-07-30 kernel fold — the NEXT intake fold breaks `CapsulePackError`. | `build_site` succeeds with at least 10 additional live kernel rows; no shard exceeds budget; existing roadmap content preserved. | Kernel-refresh finding 2026-07-30 (session report) |
| DOC-RUNSDIR-ABS-01 | P4 Polish | [AGENT] | Tool contract doc note: the extraction CLI's `--runs-dir` **must be an absolute path**. Document it at the tool contract, and consider a fail-closed check rather than leaving it as operator lore. | Doc note landed; optionally a refusal on a relative `--runs-dir` with a regression. | [D-086](docs/decision_log.md) (queued from lieutenant findings) |
| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |

## Current Queue
 joulewise/calibration_bracketing.py       |  44 +++++--
 joulewise/calibration_ledger.py           |  72 +++++++++-
 scripts/validate_powermetrics_fiducial.py |  22 +++-
 tests/test_calibration_bracketing.py      |  53 ++++++++
 tests/test_calibration_ledger.py          |  95 ++++++++++++++
 tests/test_powermetrics_fiducial.py       | 209 +++++++++++++++++++++++++++++-
 6 files changed, 474 insertions(+), 21 deletions(-)
M	joulewise/calibration_bracketing.py
M	joulewise/calibration_ledger.py
M	scripts/validate_powermetrics_fiducial.py
M	tests/test_calibration_bracketing.py
M	tests/test_calibration_ledger.py
M	tests/test_powermetrics_fiducial.py

exec
/bin/zsh -lc 'git diff --unified=100 origin/main...HEAD -- joulewise/calibration_ledger.py joulewise/calibration_bracketing.py scripts/validate_powermetrics_fiducial.py' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
diff --git a/joulewise/calibration_bracketing.py b/joulewise/calibration_bracketing.py
index ca87dbc..29b87bc 100644
--- a/joulewise/calibration_bracketing.py
+++ b/joulewise/calibration_bracketing.py
@@ -1168,270 +1168,292 @@ def evaluate_calibration_bracket(
             "claim_eligible": artifact_role == "issued",
             "derivation_sha256": artifact["derivation_sha256"],
         },
         "freshness": {
             "status": freshness_status,
             "basis": "exact_identity_epoch",
             "expected_identity_epoch": dict(identity_epoch),
             "observed_identity_epoch": observed_identity,
             "trigger_guard_protocol_sha256": prospective["protocol_sha256"],
             "trigger_guard_estimator_code_sha256": dict(
                 prospective["estimator_code_sha256"]
             ),
             "stale_fields": stale_fields,
             "calendar_expiry": None,
         },
         "prospective_rederivation": {
             "observation_rule": prospective["trigger_observation_rule"],
             "candidate_set_boundary": (
                 "authenticated_calibration_ledger_snapshot_only"
             ),
             "global_runs_root_scan": False,
             "mandatory_triggers": list(prospective["triggers"]),
             "observed_triggers": [],
         },
         "numeric_semantics": {
             "comparisons": "decimal",
             "reducer_boundary": "binary64_recorded_below",
         },
         "ledger_snapshot": {
             "ledger_schema": ledger_snapshot.ledger_schema,
             "sequence": ledger_snapshot.head_sequence,
             "head_digest": ledger_snapshot.head_digest,
             "baseline_sequence": ledger_snapshot.baseline_sequence,
             "baseline_digest": ledger_snapshot.baseline_digest,
             "load_count": 1,
         },
         "preflight": None,
         "drift": None,
     }
     if stale_fields:
         return result, ("calibration_acceptance_bound_stale",)
     observations_by_attempt = ledger_snapshot.observation_by_attempt
     finalized_session_ids = {
         session.session_id
         for session in ledger_snapshot.bracket_sessions
         if session.state == "finalized"
     }
     registered_valid = {
         (
             observation.attempt_id,
             observation.content_id,
             observation.receipt_digest,
         )
         for observation in ledger_snapshot.observations
         if observation.disposition == "valid"
         and not observation.is_historical_import
         and (
             observation.bracket_session_id is None
             or observation.bracket_session_id in finalized_session_ids
         )
     }
     supplied_valid = {
         (
             candidate.attempt_id,
             candidate.content_id,
             candidate.ledger_receipt_digest,
         )
         for candidate in candidates
     }
     # Even the low-level evaluator requires the complete ledger enumeration.
     # This prevents a caller from narrowing the registered universe to a
     # favorable subset while still passing per-candidate membership checks.
     if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
         return result, ("calibration_ledger_off_ledger_artifact",)
     for candidate in candidates:
         observation = (
             observations_by_attempt.get(candidate.attempt_id)
             if isinstance(candidate.attempt_id, str)
             else None
         )
         if (
             observation is None
             or observation.disposition != "valid"
             or candidate.content_id != observation.content_id
             or candidate.ledger_receipt_digest != observation.receipt_digest
             or candidate.manifest_sha256
             != observation.artifact_sha256.get("manifest.json")
             or candidate.evidence_sha256
             != observation.artifact_sha256.get("instrument_evidence.json")
             or candidate.bracket_session_id != observation.bracket_session_id
             or candidate.bracket_slot != observation.bracket_slot
             or candidate.bracket_window_id != observation.bracket_window_id
             or candidate.bracket_plan_id != observation.bracket_plan_id
             or candidate.bracket_plan_sha256
             != observation.bracket_plan_sha256
             or candidate.bracket_evidence_root_id
             != observation.bracket_evidence_root_id
             or candidate.bracket_runs_root != observation.bracket_runs_root
         ):
             return result, ("calibration_ledger_off_ledger_artifact",)
-    has_session_candidates = any(
-        candidate.bracket_session_id is not None for candidate in candidates
+    # A complete session pair makes the binding mandatory only for a window
+    # that pair can causally and freshly bracket.  ``candidates`` still spans
+    # the full registered universe above, preserving the anti-withholding
+    # equality check without coupling historical ordinary windows to later
+    # session observations.
+    matching = [
+        candidate
+        for candidate in candidates
+        if candidate.protocol_id == PROTOCOL_ID
+        and all(
+            candidate.bindings.get(field) == bindings.get(field)
+            for field in V2_BINDING_FIELDS
+        )
+    ]
+    window_session_pre_ids = {
+        candidate.bracket_session_id
+        for candidate in matching
+        if candidate.bracket_session_id is not None
+        and candidate.bracket_slot == "pre"
+        and candidate.capture_wall_time_s <= window_start_s
+        and window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
+    }
+    window_session_post_ids = {
+        candidate.bracket_session_id
+        for candidate in matching
+        if candidate.bracket_session_id is not None
+        and candidate.bracket_slot == "post"
+        and candidate.capture_wall_time_s >= window_end_s
+        and candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
+    }
+    has_session_candidates = (
+        bool(window_session_pre_ids & window_session_post_ids)
+        or bracket_binding is not None
     )
     bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
     if has_session_candidates:
         if (
             bracket_binding is None
             or not all(
                 isinstance(value, str) and bool(value)
                 for value in (
                     bracket_window_id,
                     bracket_plan_id,
                     bracket_plan_sha256,
                     bracket_evidence_root_id,
                 )
             )
             or bracket_runs_root is None
         ):
             return result, ("calibration_bracket_binding_missing",)
         expected_runs_root = str(Path(bracket_runs_root).absolute())
         bound_observations = validate_calibration_bracket_binding(
             bracket_binding,
             ledger_snapshot,
             window_id=bracket_window_id,
             plan_id=bracket_plan_id,
             plan_sha256=bracket_plan_sha256,
             evidence_root_id=bracket_evidence_root_id,
             runs_root=expected_runs_root,
         )
         if bound_observations is None:
             return result, ("calibration_bracket_binding_invalid",)
         result["bracket_binding"] = {
             "schema_version": BRACKET_BINDING_SCHEMA,
             "binding_digest": bracket_binding["binding_digest"],
             "session_id": bracket_binding["session_id"],
             "window_id": bracket_binding["window_id"],
             "plan_id": bracket_binding["plan_id"],
             "plan_sha256": bracket_binding["plan_sha256"],
             "evidence_root_id": bracket_binding["evidence_root_id"],
             "runs_root": bracket_binding["runs_root"],
         }
         bound_session_id = str(bracket_binding["session_id"])
         for candidate in candidates:
             if candidate.bracket_session_id != bound_session_id:
                 continue
             if (
                 candidate.bracket_window_id,
                 candidate.bracket_plan_id,
                 candidate.bracket_plan_sha256,
                 candidate.bracket_evidence_root_id,
                 candidate.bracket_runs_root,
             ) != (
                 bracket_window_id,
                 bracket_plan_id,
                 bracket_plan_sha256,
                 bracket_evidence_root_id,
                 expected_runs_root,
             ):
                 return result, ("calibration_bracket_binding_invalid",)
     # v2 remains an authenticated validation/reduction artifact, but only the
     # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
-    matching = [
-        candidate
-        for candidate in candidates
-        if candidate.protocol_id == PROTOCOL_ID
-        and all(
-            candidate.bindings.get(field) == bindings.get(field)
-            for field in V2_BINDING_FIELDS
-        )
-    ]
     matching_decimals: dict[int, Decimal] = {}
     for candidate in matching:
         candidate_decimal = _candidate_decimal(candidate)
         if candidate_decimal is None or candidate_decimal < 0:
             return result, ("instrument_calibration_invalid",)
         matching_decimals[id(candidate)] = candidate_decimal
     corpus_members = artifact["derivation_corpus"]["members"]
     observed_triggers = result["acceptance"]["prospective_rederivation"][
         "observed_triggers"
     ]
     if (
         protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
         or _current_estimator_code_sha256()
         != dict(prospective["estimator_code_sha256"])
     ):
         observed_triggers.append("protocol_or_estimator_byte_change")
     prior_ids = {
         observation["content_id"]
         for observation in artifact["prior_observation_set"]["observations"]
     }
     distinct_observations = {
         observation.content_id: observation
         for observation in ledger_snapshot.observations
         if observation.content_id is not None
     }
     distinct_live_observations = {
         content_id: observation
         for content_id, observation in distinct_observations.items()
         if not observation.is_historical_import
     }
     new_observations = [
         observation
         for content_id, observation in sorted(distinct_live_observations.items())
         if content_id not in prior_ids
     ]
     new_observations.extend(
         sorted(
             (
                 observation
                 for observation in ledger_snapshot.post_cutoff_live_observations(
                     cutoff["sequence"]
                 )
                 if observation.content_id is None
             ),
             key=lambda observation: (observation.sequence, observation.attempt_id),
         )
     )
     if any(
         observation.classification_disposition
         not in {"valid", "systematic-invalid", "ordinary-invalid"}
         for observation in new_observations
     ):
         return result, ("calibration_observation_unclassifiable",)
     valid_same_epoch = [
         observation
         for observation in distinct_observations.values()
         if observation.disposition == "valid"
         and dict(observation.identity_epoch) == dict(identity_epoch)
     ]
     if len(valid_same_epoch) >= 38:
         observed_triggers.append("corpus_doubles_from_19_to_38")
     corpus_values = [
         Decimal(member["b_fiducial_s"]) for member in corpus_members
     ]
     new_valid_values = [
         value
         for observation in new_observations
         if observation.disposition == "valid"
         and dict(observation.identity_epoch) == dict(identity_epoch)
         and (value := _decimal(observation.exact_bound_lexeme_s)) is not None
     ]
     if any(value < min(corpus_values) or value > max(corpus_values) for value in new_valid_values):
         observed_triggers.append(
             "new_valid_same_identity_capture_expands_observed_range"
         )
     if any(
         observation.disposition == "systematic-invalid"
         and dict(observation.identity_epoch) == dict(identity_epoch)
         for observation in new_observations
     ):
         observed_triggers.append(
             "new_systematic_failure_challenges_preflight_screen"
         )
     # R2 trigger evaluation ranges over the observation universe, not the
     # narrower bracket-candidate set.  A governed aborted PRE can therefore
     # stale the acceptance artifact even when no eligible endpoint pair is
     # available for this window.
     observation_stale_triggers = [
         trigger
         for trigger in observed_triggers
         if trigger == "new_systematic_failure_challenges_preflight_screen"
     ]
     if observation_stale_triggers:
         result["acceptance"]["freshness"].update(
             {
                 "status": "stale",
                 "reason": "prospective_rederivation_required",
                 "stale_triggers": observation_stale_triggers,
             }
         )
diff --git a/joulewise/calibration_ledger.py b/joulewise/calibration_ledger.py
index 39b551a..5836bd9 100644
--- a/joulewise/calibration_ledger.py
+++ b/joulewise/calibration_ledger.py
@@ -104,200 +104,216 @@ MANIFEST_BOUND_ARTIFACTS = tuple(
 EVIDENCE_BOUND_ARTIFACTS = (
     "raw/powermetrics.plist",
     "events.jsonl",
     "power_trace.csv",
 )
 _SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
 
 # Stable refusal taxonomy.  Consumers propagate these exact spellings into
 # claim barriers; no malformed or unresolved history is silently omitted.
 REFUSAL_TAXONOMY: Mapping[str, str] = MappingProxyType(
     {
         "calibration_ledger_missing": "the pinned non-genesis ledger is absent",
         "calibration_ledger_malformed": "ledger, receipt, or head-pin schema is malformed",
         "calibration_ledger_chain_conflict": "sequence or predecessor linkage is not one linear chain",
         "calibration_ledger_attempt_conflict": "an attempt has duplicate or conflicting state transitions",
         "calibration_ledger_bracket_session_conflict": "a bracket session has duplicate, reordered, or conflicting state transitions",
         "calibration_ledger_bracket_slot_claimed": "a bracket session slot already has an exclusive writer claim",
         "calibration_ledger_bracket_session_open": "a bracket session has not finalized both slots or recorded a governed abort",
         "calibration_ledger_content_conflict": "one content identity has conflicting authenticated classifications",
         "calibration_ledger_pending": "at least one reservation is unresolved",
         "calibration_ledger_head_uncommitted": "the head pin differs from the Git HEAD bytes",
         "calibration_ledger_head_mismatch": "the physical head differs from the committed pin",
         "calibration_ledger_rollback": "the physical ledger is a proper prefix of the pinned head",
         "calibration_ledger_recovery_required": "the final ledger line is a journal-authenticated torn append requiring governed recovery",
         "calibration_ledger_baseline_missing": "the acceptance cutoff is not in the current chain",
         "calibration_ledger_custody_invalid": "receipt-bound evidence bytes are absent or hash-invalid",
         "calibration_ledger_snapshot_required": "claim evaluation did not receive one immutable snapshot",
         "calibration_ledger_off_ledger_artifact": "a calibration artifact is not registered in the snapshot",
         "calibration_observation_unclassifiable": "a governed observation has no ruled disposition",
     }
 )
 
 
 class CalibrationLedgerError(ValueError):
     """A writer-side ledger operation cannot preserve the D-109 contract."""
 
 
 def _jsonable(value: Any) -> Any:
     if isinstance(value, Mapping):
         return {key: _jsonable(item) for key, item in value.items()}
     if isinstance(value, (list, tuple)):
         return [_jsonable(item) for item in value]
     return value
 
 
 def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
     return json.dumps(
         _jsonable(value),
         sort_keys=True,
         separators=(",", ":"),
         ensure_ascii=False,
         allow_nan=False,
     ).encode("utf-8")
 
 
 def canonical_sha256(value: Mapping[str, Any]) -> str:
     return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
 
 
 def _is_sha256(value: object) -> bool:
     return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None
 
 
 def _normalized_vector(
     value: Mapping[str, Any] | None,
     fields: Sequence[str],
 ) -> dict[str, Any]:
     source = value if isinstance(value, Mapping) else {}
     return {field: source.get(field) for field in fields}
 
 
 def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
     """Return the path-independent identity of canonical primary bytes.
 
     The authenticated evidence document and its manifest are the canonical
     byte pair.  A copied custody tree therefore retains the same identity.
     Other receipt hashes remain custody checks but do not manufacture a new
     observation when a derived representation is regenerated.
     """
 
     identity = {
         name: artifact_sha256.get(name) for name in CONTENT_ID_ARTIFACTS
     }
     if any(not _is_sha256(value) for value in identity.values()):
         return None
     return canonical_sha256(identity)
 
 
 def artifact_hashes(custody_dir: Path) -> dict[str, str]:
     """Hash every governed artifact present in one finalized custody tree."""
 
     root = Path(custody_dir)
     result: dict[str, str] = {}
     for relative in GOVERNED_ARTIFACTS:
         path = root / relative
         if path.is_file():
             result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
     return result
 
 
+def normalize_calibration_custody_path(path: Path | str) -> str:
+    """Return the lexical absolute spelling used by reservation and capture.
+
+    Custody identity is an exact ledger binding.  Resolving symlinks in only
+    one writer would therefore change that identity even when both spellings
+    name the same directory.
+    """
+
+    try:
+        return str(Path(path).absolute())
+    except (OSError, TypeError, ValueError) as exc:
+        raise CalibrationLedgerError(
+            "calibration custody path is malformed"
+        ) from exc
+
+
 def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
     return {key: value for key, value in receipt.items() if key != "receipt_digest"}
 
 
 def _receipt_digest(receipt: Mapping[str, Any]) -> str:
     return canonical_sha256(receipt_core(receipt))
 
 
 @dataclass(frozen=True)
 class LedgerObservation:
     sequence: int
     receipt_digest: str
     attempt_id: str
     content_id: str | None
     artifact_sha256: Mapping[str, str]
     identity_epoch: Mapping[str, Any]
     t1_bindings: Mapping[str, Any]
     capture_wall_time_s: str | None
     exact_bound_lexeme_s: str | None
     disposition: str
     custody_locator: str
     observation_kind: str = "live-capture"
     bracket_session_id: str | None = None
     bracket_slot: str | None = None
     bracket_window_id: str | None = None
     bracket_plan_id: str | None = None
     bracket_plan_sha256: str | None = None
     bracket_evidence_root_id: str | None = None
     bracket_runs_root: str | None = None
 
     @property
     def classification_disposition(self) -> str:
         """Map the writer terminal state onto the R2 observation schema."""
 
         return (
             "unresolved" if self.disposition == "abandoned" else self.disposition
         )
 
     @property
     def is_historical_import(self) -> bool:
         return self.observation_kind == "historical-import"
 
 
 @dataclass(frozen=True)
 class CalibrationLedgerSnapshot:
     """One immutable, fully checked view threaded through an evaluation."""
 
     ledger_schema: str
     ledger_path: Path
     head_sequence: int
     head_digest: str
     receipts: tuple[Mapping[str, Any], ...]
     observations: tuple[LedgerObservation, ...]
     refusal_reasons: tuple[str, ...]
     bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
     baseline_sequence: int | None = None
     baseline_digest: str | None = None
     committed_head_sequence: int | None = None
     committed_head_digest: str | None = None
 
     @property
     def valid(self) -> bool:
         return not self.refusal_reasons
 
     @property
     def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
         return MappingProxyType(
             {observation.attempt_id: observation for observation in self.observations}
         )
 
     @property
     def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
         return MappingProxyType(
             {session.session_id: session for session in self.bracket_sessions}
         )
 
     @property
     def is_governed_open_bracket_extension(self) -> bool:
         """Whether the physical/pin gap is exactly one reserved open session."""
 
         allowed = {
             "calibration_ledger_bracket_session_open",
             "calibration_ledger_head_mismatch",
         }
         if (
             set(self.refusal_reasons) != allowed
             or self.committed_head_sequence is None
             or self.committed_head_digest is None
         ):
             return False
         open_sessions = [
             session for session in self.bracket_sessions if session.state == "open"
         ]
         if len(open_sessions) != 1:
             return False
         session = open_sessions[0]
         if session.capability_sequence != self.committed_head_sequence + 1:
             return False
         tail = self.receipts[self.committed_head_sequence :]
         return bool(
@@ -2339,560 +2355,602 @@ def _clear_append_journal(ledger_path: Path) -> None:
     try:
         _append_journal_path(ledger_path).unlink()
         _fsync_parent_directory(Path(ledger_path).parent)
     except OSError as exc:
         raise CalibrationLedgerError("append journal could not be cleared") from exc
 
 
 def _recover_journaled_append(
     ledger_path: Path,
     handle: BinaryIO,
     raw: bytes,
 ) -> bytes:
     journal, malformed = _read_append_journal(ledger_path)
     if malformed:
         raise CalibrationLedgerError("append recovery journal is malformed")
     if journal is None:
         return raw
     completed = _journal_completed_raw(raw, journal)
     if completed is None:
         raise CalibrationLedgerError(
             "torn ledger tail does not match the append recovery journal"
         )
     offset = int(journal["ledger_offset"])
     payload = str(journal["payload"]).encode("utf-8")
     observed = len(raw) - offset
     missing = payload[observed:]
     if missing:
         handle.seek(0, os.SEEK_END)
         _write_ledger_append_payload(handle, missing)
         handle.flush()
         os.fsync(handle.fileno())
     handle.seek(0)
     completed = handle.read()
     if _journal_completed_raw(completed, journal) != completed:
         raise CalibrationLedgerError(
             "append recovery did not complete the ledger tail"
         )
     _record_append_recovery(
         ledger_path,
         journal,
         ledger_tail=completed[offset:],
     )
     _clear_append_journal(ledger_path)
     return completed
 
 
 def _locked_append(
     ledger_path: Path,
     build: Any,
 ) -> Mapping[str, Any]:
     ledger_path = Path(ledger_path)
     ledger_path.parent.mkdir(parents=True, exist_ok=True)
     lock_descriptor = _open_ledger_lock(ledger_path)
     try:
         fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
         descriptor = os.open(
             ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
         )
         try:
             with os.fdopen(descriptor, "r+b", closefd=False) as handle:
                 handle.seek(0)
                 raw = handle.read()
                 raw = _recover_journaled_append(ledger_path, handle, raw)
                 receipts, reasons = _parse_ledger(raw)
                 if reasons:
                     raise CalibrationLedgerError(", ".join(sorted(reasons)))
                 receipt = build(receipts)
                 if not _valid_receipt_shape(receipt):
                     raise CalibrationLedgerError(
                         "writer constructed a malformed receipt"
                     )
                 payload = canonical_json_bytes(receipt) + b"\n"
                 _prepare_append_journal(
                     ledger_path,
                     ledger_offset=len(raw),
                     predecessor_digest=str(
                         receipts[-1]["receipt_digest"]
                         if receipts
                         else GENESIS_DIGEST
                     ),
                     payload=payload,
                 )
                 handle.seek(0, os.SEEK_END)
                 try:
                     _write_ledger_append_payload(handle, payload)
                     handle.flush()
                     os.fsync(handle.fileno())
                 except Exception:
                     # The durable journal is intentionally retained.  No
                     # ledger byte is removed; a later governed writer can
                     # complete only the journal-matching suffix.
                     raise
                 _clear_append_journal(ledger_path)
                 return _frozen_mapping(receipt)
         finally:
             os.close(descriptor)
     finally:
         os.close(lock_descriptor)
 
 
+def recover_calibration_ledger_append(ledger_path: Path) -> Path | None:
+    """Complete one authenticated journaled append without adding a receipt.
+
+    The stable ledger lock is held through suffix completion, recovery
+    evidence publication, and journal removal.  ``None`` means no recovery
+    journal was present; otherwise the returned path is the durable evidence
+    object for the completed operation.
+    """
+
+    ledger_path = Path(ledger_path)
+    ledger_path.parent.mkdir(parents=True, exist_ok=True)
+    lock_descriptor = _open_ledger_lock(ledger_path)
+    try:
+        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
+        journal, malformed = _read_append_journal(ledger_path)
+        if malformed:
+            raise CalibrationLedgerError("append recovery journal is malformed")
+        if journal is None:
+            return None
+        descriptor = os.open(
+            ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
+        )
+        try:
+            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
+                handle.seek(0)
+                raw = handle.read()
+                _recover_journaled_append(ledger_path, handle, raw)
+        finally:
+            os.close(descriptor)
+        return _append_recovery_path(ledger_path, str(journal["operation_id"]))
+    finally:
+        os.close(lock_descriptor)
+
+
 def _authenticated_head_pin(
     head_pin_path: Path,
     *,
     require_committed_pin: bool,
     repo_root: Path,
 ) -> tuple[int, str]:
     pin_path = Path(head_pin_path)
     try:
         pin_raw = pin_path.read_bytes()
         pin_value = json.loads(pin_raw)
     except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
         raise CalibrationLedgerError("head pin is unreadable") from exc
     pin = _head_pin(pin_value)
     if pin is None:
         raise CalibrationLedgerError("head pin is malformed")
     if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
         raise CalibrationLedgerError("head pin is not committed at Git HEAD")
     return pin
 
 
 def validate_bracket_session_reservation_inputs(
     *,
     session_id: str,
     window_id: str,
     plan_id: str,
     plan_sha256: str,
     evidence_root_id: str,
     runs_root: Path | str,
     slots: Mapping[str, Mapping[str, Any]],
 ) -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
     """Apply the exact same capability-input validation for dry-run/execute."""
 
     try:
-        normalized_runs_root = str(Path(runs_root).absolute())
-    except (OSError, TypeError, ValueError) as exc:
+        normalized_runs_root = normalize_calibration_custody_path(runs_root)
+    except CalibrationLedgerError as exc:
         raise CalibrationLedgerError("bracket session runs_root is malformed") from exc
     session_identity = {
         "session_id": session_id,
         "window_id": window_id,
         "plan_id": plan_id,
         "plan_sha256": plan_sha256,
         "evidence_root_id": evidence_root_id,
         "runs_root": normalized_runs_root,
     }
     normalized_slots: dict[str, dict[str, Any]] = {}
     if not isinstance(slots, Mapping) or set(slots) != set(BRACKET_SESSION_SLOTS):
         raise CalibrationLedgerError("bracket session must reserve exactly pre and post")
     validation_root = Path(normalized_runs_root) / "instrument_validation"
     for role in BRACKET_SESSION_SLOTS:
         source = slots.get(role)
         if not isinstance(source, Mapping):
             raise CalibrationLedgerError(f"{role} slot is malformed")
         custody_value = source.get("custody_locator")
         try:
-            custody = Path(str(custody_value)).absolute()
+            custody = Path(normalize_calibration_custody_path(custody_value))
             custody.relative_to(validation_root)
-        except (OSError, TypeError, ValueError) as exc:
+        except (CalibrationLedgerError, OSError, TypeError, ValueError) as exc:
             raise CalibrationLedgerError(
                 f"{role} custody locator is outside runs_root/instrument_validation"
             ) from exc
         normalized_slots[role] = {
             "attempt_id": source.get("attempt_id"),
             "custody_locator": str(custody),
             "identity_epoch": _normalized_vector(
                 source.get("identity_epoch"), IDENTITY_EPOCH_FIELDS
             ),
             "t1_bindings": _normalized_vector(source.get("t1_bindings"), T1_FIELDS),
             "expected_time_role": role,
         }
     if not _valid_session_identity(session_identity) or any(
         not _valid_session_slot_reservation(normalized_slots[role], role)
         for role in BRACKET_SESSION_SLOTS
     ):
         raise CalibrationLedgerError("bracket session reservation is malformed")
     if normalized_slots["pre"]["attempt_id"] == normalized_slots["post"]["attempt_id"]:
         raise CalibrationLedgerError("bracket session slot attempts must be distinct")
     return _frozen_mapping(session_identity), _frozen_mapping(normalized_slots)
 
 
 def append_bracket_session_receipt(
     ledger_path: Path,
     *,
     session_id: str,
     window_id: str,
     plan_id: str,
     plan_sha256: str,
     evidence_root_id: str,
     runs_root: Path | str,
     slots: Mapping[str, Mapping[str, Any]],
     head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
     require_committed_pin: bool = True,
     repo_root: Path = REPO_ROOT,
 ) -> Mapping[str, Any]:
     """Atomically reserve exactly one immutable pre/post bracket capability.
 
     Physical-head equality with the committed pin is checked here, at open,
     and deliberately not checked again while either already-reserved slot is
     finalized. Claim evaluation remains impossible until the terminal head
     pin is emitted, reviewed, and committed.
     """
 
     session_identity, normalized_slots = validate_bracket_session_reservation_inputs(
         session_id=session_id,
         window_id=window_id,
         plan_id=plan_id,
         plan_sha256=plan_sha256,
         evidence_root_id=evidence_root_id,
         runs_root=runs_root,
         slots=slots,
     )
     pin = _authenticated_head_pin(
         Path(head_pin_path),
         require_committed_pin=require_committed_pin,
         repo_root=Path(repo_root),
     )
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         if (len(receipts), predecessor) != pin:
             raise CalibrationLedgerError(
                 "physical ledger head differs from the committed pin"
             )
         observations, sessions, reasons = _attempts_and_observations(receipts)
         del observations
         if reasons:
             raise CalibrationLedgerError(", ".join(sorted(reasons)))
         reserved_attempts = {
             attempt_id
             for session in sessions
             for attempt_id in session.slot_attempt_ids.values()
         }
         ordinary_attempts = {
             str(receipt["attempt_id"])
             for receipt in receipts
             if receipt.get("schema_version") == RECEIPT_SCHEMA
         }
         proposed_attempts = {
             normalized_slots[role]["attempt_id"] for role in BRACKET_SESSION_SLOTS
         }
         if (
             any(session.session_id == session_id for session in sessions)
             or proposed_attempts & (reserved_attempts | ordinary_attempts)
         ):
             raise CalibrationLedgerError("bracket session identity conflicts with ledger")
         return _new_bracket_session_record(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event=BRACKET_SESSION_OPEN_EVENT,
             session_identity=session_identity,
             fields={"slots": normalized_slots},
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def claim_bracket_session_slot(
     ledger_path: Path,
     *,
     session_id: str,
     slot: str,
     attempt_id: str,
     claim_id: str,
 ) -> Mapping[str, Any]:
     """Append one process-death-stable exclusive claim for a reserved slot."""
 
     if slot not in BRACKET_SESSION_SLOTS:
         raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
     if not isinstance(claim_id, str) or not claim_id:
         raise CalibrationLedgerError("bracket slot claim_id must be nonempty")
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
         observations, sessions, reasons = _attempts_and_observations(receipts)
         del observations
         non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
         if non_open_reasons:
             raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
         session = next(
             (item for item in sessions if item.session_id == session_id), None
         )
         if session is None or session.state != "open":
             raise CalibrationLedgerError("bracket session is not open")
         expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
         if slot != expected_slot or session.slot_attempt_ids.get(slot) != attempt_id:
             raise CalibrationLedgerError(
                 f"bracket session slot must claim in order: expected {expected_slot}"
             )
         existing = [
             receipt
             for receipt in receipts
             if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
             and receipt.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
             and receipt.get("session_id") == session_id
             and receipt.get("slot") == slot
         ]
         if existing:
-            raise CalibrationLedgerError("calibration_ledger_bracket_slot_claimed")
+            raise CalibrationLedgerError(
+                REFUSAL_TAXONOMY["calibration_ledger_bracket_slot_claimed"]
+            )
         open_receipt = next(
             receipt
             for receipt in receipts
             if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
             and receipt.get("session_id") == session_id
         )
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         return _new_bracket_session_record(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event=BRACKET_SESSION_SLOT_CLAIM_EVENT,
             session_identity={
                 field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
             },
             fields={
                 "slot": slot,
                 "attempt_id": attempt_id,
                 "claim_id": claim_id,
             },
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def finalize_bracket_session_slot(
     ledger_path: Path,
     *,
     session_id: str,
     slot: str,
     disposition: str,
     custody_locator: str,
     artifact_sha256: Mapping[str, str] | None = None,
     identity_epoch: Mapping[str, Any] | None = None,
     t1_bindings: Mapping[str, Any] | None = None,
     capture_wall_time_s: str | None = None,
     exact_bound_lexeme_s: str | None = None,
 ) -> Mapping[str, Any]:
     """Fill exactly one reserved session slot in mandatory pre/post order."""
 
     if slot not in BRACKET_SESSION_SLOTS:
         raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
     if disposition not in FINAL_DISPOSITIONS:
         raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
     artifacts = dict(artifact_sha256 or {})
     content_id = content_id_from_artifact_hashes(artifacts)
     normalized_epoch = _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS)
     normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
         observations, sessions, reasons = _attempts_and_observations(receipts)
         del observations
         non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
         if non_open_reasons:
             raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
         by_id = {session.session_id: session for session in sessions}
         session = by_id.get(session_id)
         if session is None or session.state != "open":
             raise CalibrationLedgerError("bracket session is not open")
         expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
         if slot != expected_slot or slot in session.finalized_slots:
             raise CalibrationLedgerError(
                 f"bracket session slot must finalize in order: expected {expected_slot}"
             )
         open_receipt = next(
             receipt
             for receipt in receipts
             if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
             and receipt.get("session_id") == session_id
         )
         reserved = open_receipt["slots"][slot]
         if (
             reserved["custody_locator"] != custody_locator
             or dict(reserved["identity_epoch"]) != normalized_epoch
             or dict(reserved["t1_bindings"]) != normalized_t1
         ):
             raise CalibrationLedgerError(
                 "slot finalization conflicts with the reserved session binding"
             )
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         return _new_bracket_session_record(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event=BRACKET_SESSION_FINALIZATION_EVENT,
             session_identity={
                 field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
             },
             fields={
                 "slot": slot,
                 "attempt_id": reserved["attempt_id"],
                 "content_id": content_id,
                 "artifact_sha256": dict(sorted(artifacts.items())),
                 "identity_epoch": normalized_epoch,
                 "t1_bindings": normalized_t1,
                 "capture_wall_time_s": capture_wall_time_s,
                 "exact_bound_lexeme_s": exact_bound_lexeme_s,
                 "disposition": disposition,
                 "custody_locator": custody_locator,
             },
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def abort_bracket_session(
     ledger_path: Path,
     *,
     session_id: str,
     reason: str,
 ) -> Mapping[str, Any]:
     """Append a governed terminal closure without deleting partial receipts."""
 
     if not isinstance(reason, str) or not reason:
         raise CalibrationLedgerError("bracket session abort reason must be nonempty")
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
         observations, sessions, reasons = _attempts_and_observations(receipts)
         del observations
         non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
         if non_open_reasons:
             raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
         session = next(
             (item for item in sessions if item.session_id == session_id), None
         )
         if session is None or session.state != "open":
             raise CalibrationLedgerError("bracket session is not open")
         open_receipt = next(
             receipt
             for receipt in receipts
             if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
             and receipt.get("session_id") == session_id
         )
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         finalized_slots = list(session.finalized_slots)
         return _new_bracket_session_record(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event=BRACKET_SESSION_ABORT_EVENT,
             session_identity={
                 field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
             },
             fields={
                 "finalized_slots": finalized_slots,
                 "unused_slots": [
                     role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
                 ],
                 "reason": reason,
             },
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def terminal_head_pin_for_session(
     ledger_path: Path,
     *,
     session_id: str,
 ) -> dict[str, Any]:
     """Return the sole terminal pin candidate after post or governed abort."""
 
     try:
         raw = Path(ledger_path).read_bytes()
     except OSError as exc:
         raise CalibrationLedgerError("ledger is unreadable") from exc
-    receipts, parse_reasons = _parse_ledger(raw)
+    append_journal, malformed_journal = _read_append_journal(Path(ledger_path))
+    receipts, parse_reasons = _parse_ledger(
+        raw,
+        append_journal=append_journal,
+    )
+    if malformed_journal:
+        parse_reasons.add("calibration_ledger_malformed")
     observations, sessions, state_reasons = _attempts_and_observations(receipts)
     del observations
     reasons = parse_reasons | state_reasons
     if reasons:
         raise CalibrationLedgerError(", ".join(sorted(reasons)))
     session = next((item for item in sessions if item.session_id == session_id), None)
     if session is None or session.state == "open":
         raise CalibrationLedgerError("bracket session is not terminal")
     terminal_digest = (
         session.finalized_slots["post"].receipt_digest
         if session.state == "finalized"
         else session.abort_receipt_digest
     )
     final = receipts[-1] if receipts else None
     if final is None or final["receipt_digest"] != terminal_digest:
         raise CalibrationLedgerError("session closure is not the terminal ledger head")
     return _head_pin_for_valid_receipt(final)
 
 
 def append_pending_receipt(
     ledger_path: Path,
     *,
     attempt_id: str,
     custody_locator: str,
     identity_epoch: Mapping[str, Any] | None = None,
     t1_bindings: Mapping[str, Any] | None = None,
     head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
     require_committed_pin: bool = True,
     repo_root: Path = REPO_ROOT,
 ) -> Mapping[str, Any]:
     """Reserve an attempt before any capture directory or sampler exists.
 
     This closes workflow omission, unregistered evidence, and rollback or
     stale-head consumption; it does not defend against a malicious trusted
     writer or a rewrite of both Git and the full ledger history.
     """
 
     if not isinstance(attempt_id, str) or not attempt_id:
         raise CalibrationLedgerError("attempt_id must be nonempty")
     pin_path = Path(head_pin_path)
     try:
         pin_raw = pin_path.read_bytes()
         pin_value = json.loads(pin_raw)
     except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
         raise CalibrationLedgerError("head pin is unreadable") from exc
     pin = _head_pin(pin_value)
     if pin is None:
         raise CalibrationLedgerError("head pin is malformed")
     if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
         raise CalibrationLedgerError("head pin is not committed at Git HEAD")
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
         sequence = len(receipts) + 1
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         if (len(receipts), predecessor) != pin:
             raise CalibrationLedgerError(
                 "physical ledger head differs from the committed pin"
             )
         observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
         del observations
         del bracket_sessions
         if reasons or any(
             row.get("attempt_id") == attempt_id
             or any(
                 isinstance(slot, Mapping) and slot.get("attempt_id") == attempt_id
                 for slot in (
                     row.get("slots", {}).values()
                     if isinstance(row.get("slots"), Mapping)
                     else ()
                 )
             )
             for row in receipts
         ):
             raise CalibrationLedgerError(
                 ", ".join(sorted(reasons or {"calibration_ledger_attempt_conflict"}))
             )
         return _new_receipt(
             sequence=sequence,
             predecessor_digest=str(predecessor),
             event="reservation",
             attempt_id=attempt_id,
             content_id=None,
             artifacts={},
             identity_epoch=identity_epoch,
             t1_bindings=t1_bindings,
             capture_wall_time_s=None,
             exact_bound_lexeme_s=None,
             disposition="pending",
             custody_locator=custody_locator,
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def finalize_attempt_receipt(
     ledger_path: Path,
     *,
     attempt_id: str,
     disposition: str,
     custody_locator: str,
@@ -2927,104 +2985,106 @@ def finalize_attempt_receipt(
             for row in receipts
             if row.get("attempt_id") == attempt_id and row["event"] == "finalization"
         ]
         if len(reservations) != 1 or finals:
             raise CalibrationLedgerError("attempt is not uniquely pending")
         reservation = reservations[0]
         normalized_epoch = _normalized_vector(
             identity_epoch, IDENTITY_EPOCH_FIELDS
         )
         normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)
         if (
             dict(reservation["identity_epoch"]) != normalized_epoch
             or dict(reservation["t1_bindings"]) != normalized_t1
             or reservation["custody_locator"] != custody_locator
         ):
             raise CalibrationLedgerError(
                 "finalization conflicts with the reserved attempt binding"
             )
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         return _new_receipt(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event="finalization",
             attempt_id=attempt_id,
             content_id=content_id,
             artifacts=artifacts,
             identity_epoch=identity_epoch,
             t1_bindings=t1_bindings,
             capture_wall_time_s=capture_wall_time_s,
             exact_bound_lexeme_s=exact_bound_lexeme_s,
             disposition=disposition,
             custody_locator=custody_locator,
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def _head_pin_for_valid_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
     if not _valid_receipt_shape(receipt):
         raise CalibrationLedgerError("cannot pin a malformed receipt")
     return {
         "sequence": int(receipt["sequence"]),
         "head_digest": str(receipt["receipt_digest"]),
         "ledger_schema": LEDGER_SCHEMA,
     }
 
 
 def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
     """Emit a pin for an ordinary receipt, never a mid-session receipt."""
 
     if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
         raise CalibrationLedgerError(
             "bracket session receipts require terminal_head_pin_for_session"
         )
     return _head_pin_for_valid_receipt(receipt)
 
 
 __all__ = [
     "ALL_DISPOSITIONS",
     "BRACKET_SESSION_ABORT_EVENT",
     "BRACKET_SESSION_FINALIZATION_EVENT",
     "BRACKET_SESSION_OPEN_EVENT",
     "BRACKET_SESSION_SLOT_CLAIM_EVENT",
     "BRACKET_SESSION_SCHEMA",
     "BRACKET_SESSION_SLOTS",
     "CONTENT_ID_ARTIFACTS",
     "DEFAULT_HEAD_PIN_PATH",
     "DEFAULT_LEDGER_PATH",
     "FINAL_DISPOSITIONS",
     "GENESIS_DIGEST",
     "GOVERNED_ARTIFACTS",
     "HISTORICAL_IMPORT_EVENT_PREFIX",
     "HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA",
     "HISTORICAL_IMPORT_FINALIZATION_EVENT",
     "HISTORICAL_IMPORT_RESERVATION_EVENT",
     "HISTORICAL_IMPORT_TABLE_SCHEMA",
     "IDENTITY_EPOCH_FIELDS",
     "LEDGER_SCHEMA",
     "RECEIPT_SCHEMA",
     "REFUSAL_TAXONOMY",
     "CalibrationLedgerError",
     "CalibrationBracketSession",
     "CalibrationLedgerSnapshot",
     "HistoricalImportDurabilityUncertain",
     "HistoricalImportPlan",
     "LedgerObservation",
     "append_pending_receipt",
     "append_bracket_session_receipt",
     "claim_bracket_session_slot",
     "abort_bracket_session",
     "artifact_hashes",
     "bootstrap_historical_import",
     "custody_manifest_bytes",
     "canonical_sha256",
     "content_id_from_artifact_hashes",
     "finalize_attempt_receipt",
     "finalize_bracket_session_slot",
     "generate_historical_custody_manifest",
     "head_pin_for_receipt",
     "load_calibration_ledger_snapshot",
+    "normalize_calibration_custody_path",
     "prepare_historical_import",
+    "recover_calibration_ledger_append",
     "terminal_head_pin_for_session",
     "validate_bracket_session_reservation_inputs",
 ]
diff --git a/scripts/validate_powermetrics_fiducial.py b/scripts/validate_powermetrics_fiducial.py
index 31725f6..3799f85 100644
--- a/scripts/validate_powermetrics_fiducial.py
+++ b/scripts/validate_powermetrics_fiducial.py
@@ -1,164 +1,166 @@
 #!/usr/bin/env python3
 """Lead-owned [QUIET-MAC] pulse-fiducial calibration run (D-078).
 
 The current claim-bearing protocol is frozen in
 configs/calibration/powermetrics_fiducial/protocol_v3.json and documented in
 docs/contracts/powermetrics_fiducial.md. Historical protocol files remain
 byte-frozen validation identities.
 
 - preallocated 4096x4096 FP16 MLX matmuls, mx.eval GPU fencing;
 - 3 warmup pulses, then k=59 pulses of 1.0 s each;
 - deterministic low-discrepancy spacing 1.5 + vanDerCorput_2(j) s
   (avoids 10 Hz phase lock);
 - >= 5 s baseline before and after the pulse train;
 - events pulse_command_on/off carry full paired ClockStamps;
 - primary rail gpu_power; CPU+GPU combined is corroboration only;
 - gates: plateau >= 10 W over baseline, robust SNR >= 10, all pulses
   detected, no spurious plateaus - otherwise the artifact is invalid.
 
 NEVER run this while another agent session is active on the machine
 ([QUIET-MAC] discipline); the run is refused without --allow-live.
 """
 
 from __future__ import annotations
 
 import argparse
 import atexit
 import hashlib
 import json
 import math
 import subprocess
 import sys
 import time
 import uuid
 from dataclasses import asdict, replace
 from decimal import Decimal
 from pathlib import Path
 from typing import Any, Mapping
 
 REPO_ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(REPO_ROOT))
 
 from joulewise.adapters.powermetrics import (  # noqa: E402
     POWER_METRICS,
     SAMPLERS,
     anchor_records_from_powermetrics,
     parse_powermetrics_records,
     samples_from_records,
 )
 from joulewise.clock import SystemClock  # noqa: E402
 from joulewise.calibration_ledger import (  # noqa: E402
     BRACKET_SESSION_OPEN_EVENT,
     BRACKET_SESSION_SCHEMA,
     BRACKET_SESSION_SLOTS,
     DEFAULT_LEDGER_PATH,
     DEFAULT_HEAD_PIN_PATH,
     CalibrationLedgerError,
     abort_bracket_session,
     append_pending_receipt,
     artifact_hashes as ledger_artifact_hashes,
     claim_bracket_session_slot,
     finalize_attempt_receipt,
     finalize_bracket_session_slot,
     head_pin_for_receipt,
     load_calibration_ledger_snapshot,
+    normalize_calibration_custody_path,
+    recover_calibration_ledger_append,
     terminal_head_pin_for_session,
 )
 from joulewise.powermetrics_fiducial import (  # noqa: E402
     BASELINE_S,
     LEGACY_PROTOCOL_ID,
     PROTOCOL_ID,
     PROTOCOL_V2_ID,
     PROTOCOL_V2_PULSE_COUNT,
     RESIDUAL_REGION_METHOD,
     PULSE_COUNT,
     PULSE_DURATION_S,
     SAMPLING_INTERVAL_MS,
     CommandedPulse,
     TraceInterval,
     WARMUP_PULSE_COUNT,
     allocate_matmul_buffers,
     capture_wall_time_from_events,
     clock_stamp_half_width_s,
     detect_pulses,
     instrument_evidence,
     protocol_definition_matches,
     pulse_schedule,
     run_matmul_pulse,
     trim_trace_after_pulses,
     rederive_detection_from_artifacts,
 )
 from joulewise.uncertainty_evidence import (  # noqa: E402
     CLOCK_METHOD_V2,
     derive_powermetrics_clock_evidence_v2,
 )
 
 PROTOCOL_PATH = (
     REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v3.json"
 )
 PROTOCOL_V2_PATH = (
     REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v2.json"
 )
 ROLLOVER_GATE_TIMEOUT_REASON = "pulse_calibration_rollover_gate_timeout"
 PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")
 
 
 def sha256_path(path: Path) -> str:
     return hashlib.sha256(path.read_bytes()).hexdigest()
 
 
 def _sysctl_identity(name: str) -> str:
     """Read a reservation-time macOS identity before capture begins."""
 
     value = subprocess.run(
         ["/usr/sbin/sysctl", "-n", name],
         check=True,
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,
         text=True,
     ).stdout.strip()
     if not value:
         raise RuntimeError(f"empty reservation identity: {name}")
     return value
 
 
 def verify_frozen_protocol(path: Path = PROTOCOL_PATH) -> bool:
     """Load and field-bind the frozen JSON to executable module constants."""
 
     try:
         payload = json.loads(path.read_text(encoding="utf-8"))
     except (OSError, UnicodeDecodeError, json.JSONDecodeError):
         return False
     return protocol_definition_matches(payload)
 
 
 def _terminate_powermetrics(process: subprocess.Popen) -> None:
     """Best-effort bounded termination for a calibration sampler."""
 
     process.terminate()
     try:
         process.communicate(timeout=10.0)
     except subprocess.TimeoutExpired:
         process.kill()
         process.communicate()
 
 
 def wait_for_preworkload_rollover(
     capture_path: Path,
     process: subprocess.Popen,
     *,
     timeout_s: float = 15.0,
     poll_s: float = 0.05,
 ) -> None:
     """Require an advancing native plist timestamp before any workload.
 
     Timeout is a governed refusal, not permission to fall through. The
     sampler is terminated here so callers cannot accidentally continue with
     baseline, warmup, or pulse work after the gate fails.
     """
 
     deadline = time.monotonic() + timeout_s
     while time.monotonic() < deadline:
         try:
             records = parse_powermetrics_records(capture_path.read_bytes())
         except (OSError, ValueError):
@@ -209,490 +211,506 @@ def rederive_artifact(source_dir: Path, output: Path) -> dict[str, object]:
         stored.get("protocol_id") not in {LEGACY_PROTOCOL_ID, PROTOCOL_V2_ID}
         or stored.get("pulse_count") != PROTOCOL_V2_PULSE_COUNT
     ):
         raise ValueError("re-derivation requires compatible 40-pulse v1/v2 evidence")
     raw_by_name: dict[str, bytes] = {}
     for relative in (
         "raw/powermetrics.plist",
         "events.jsonl",
         "instrument_evidence.json",
     ):
         expected = artifacts.get(relative)
         candidate = source_dir / relative
         try:
             raw = candidate.read_bytes()
         except OSError as exc:
             raise ValueError(f"source artifact missing: {relative}") from exc
         if (
             not isinstance(expected, str)
             or hashlib.sha256(raw).hexdigest() != expected
         ):
             raise ValueError(f"source artifact hash mismatch: {relative}")
         raw_by_name[relative] = raw
     stored_hashes = stored.get("artifact_sha256")
     if not isinstance(stored_hashes, dict):
         raise ValueError("source evidence omits primary artifact hashes")
     for relative in ("raw/powermetrics.plist", "events.jsonl"):
         if hashlib.sha256(raw_by_name[relative]).hexdigest() != stored_hashes.get(
             relative
         ):
             raise ValueError(f"source evidence hash mismatch: {relative}")
     fresh = rederive_detection_from_artifacts(
         raw_by_name["raw/powermetrics.plist"],
         raw_by_name["events.jsonl"],
         stored.get("clock_anchor"),
         protocol_id=str(stored.get("protocol_id")),
     )
     stored_bound = stored.get("b_fiducial_s")
     if (
         isinstance(stored_bound, bool)
         or not isinstance(stored_bound, int | float)
         or fresh.b_fiducial_s is None
     ):
         raise ValueError("source calibration bound is malformed")
     fresh = replace(
         fresh,
         b_fiducial_s=max(float(stored_bound), float(fresh.b_fiducial_s)),
     )
     bindings = dict(stored.get("bindings", {}))
     bindings.update(
         {
             "pulse_protocol_id": PROTOCOL_V2_ID,
             "estimator_revision": RESIDUAL_REGION_METHOD,
             "protocol_sha256": sha256_path(PROTOCOL_V2_PATH),
         }
     )
     validation_id = str(stored.get("validation_id") or source_dir.name) + "-v2"
     payload = instrument_evidence(
         fresh,
         bindings=bindings,
         validation_id=validation_id,
         artifact_sha256={
             relative: hashlib.sha256(raw_by_name[relative]).hexdigest()
             for relative in ("raw/powermetrics.plist", "events.jsonl")
         },
         capture_wall_time_s=capture_wall_time_from_events(
             raw_by_name["events.jsonl"]
         ),
         protocol_id=PROTOCOL_V2_ID,
         protocol_pulse_count=PROTOCOL_V2_PULSE_COUNT,
     )
     payload["clock_anchor"] = stored.get("clock_anchor")
     payload["clock_anchor_resolved"] = True
     output.parent.mkdir(parents=True, exist_ok=True)
     # Exclusive create: re-derivation must never clobber an existing evidence
     # artifact (same rule as the extraction and campaign-log outputs).
     with output.open("x", encoding="utf-8") as handle:
         handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
     return payload
 
 
 def _validate_reserved_bracket_slot(
     ledger_path: Path,
     head_pin_path: Path,
     *,
     session_id: str,
     slot: str,
     attempt_id: str,
     custody_locator: str,
     identity_epoch: Mapping[str, Any],
     t1_bindings: Mapping[str, Any],
     require_committed_pin: bool = True,
 ) -> None:
     """Authenticate the exact predeclared slot before capture state exists."""
 
     snapshot = load_calibration_ledger_snapshot(
         ledger_path,
         head_pin_path,
         require_committed_pin=require_committed_pin,
         verify_custody=True,
     )
+    if "calibration_ledger_recovery_required" in snapshot.refusal_reasons:
+        raise CalibrationLedgerError(
+            "calibration ledger append recovery is required; retry this capture "
+            "command so governed recovery completes before slot validation"
+        )
     session = snapshot.bracket_session_by_id.get(session_id)
     finalized_slots = set(session.finalized_slots) if session is not None else set()
     expected_slot = (
         "pre"
         if not finalized_slots
         else "post"
         if finalized_slots == {"pre"}
         else None
     )
     open_receipt = next(
         (
             receipt
             for receipt in snapshot.receipts
             if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
             and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
             and receipt.get("session_id") == session_id
         ),
         None,
     )
     reserved = (
         open_receipt.get("slots", {}).get(slot)
         if isinstance(open_receipt, Mapping)
         and isinstance(open_receipt.get("slots"), Mapping)
         else None
     )
     if (
         not snapshot.is_governed_open_bracket_extension
         or session is None
         or session.state != "open"
         or slot not in BRACKET_SESSION_SLOTS
         or slot != expected_slot
         or session.slot_attempt_ids.get(slot) != attempt_id
         or not isinstance(reserved, Mapping)
         or reserved.get("attempt_id") != attempt_id
         or reserved.get("custody_locator") != custody_locator
         or dict(reserved.get("identity_epoch", {})) != dict(identity_epoch)
         or dict(reserved.get("t1_bindings", {})) != dict(t1_bindings)
     ):
         raise CalibrationLedgerError(
             "capture does not match the exact reserved bracket session slot"
         )
 
 
 class _CaptureLedgerLifecycle:
     """Route one writer attempt through ordinary or bracket-session APIs."""
 
     def __init__(
         self,
         *,
         ledger_path: Path,
         head_pin_path: Path,
         attempt_id: str,
         custody_locator: str,
         identity_epoch: Mapping[str, Any],
         t1_bindings: Mapping[str, Any],
         session_id: str | None = None,
         slot: str | None = None,
         require_committed_pin: bool = True,
     ) -> None:
         if (session_id is None) != (slot is None):
             raise CalibrationLedgerError(
                 "bracket session id and slot must be supplied together"
             )
         self.ledger_path = Path(ledger_path)
         self.head_pin_path = Path(head_pin_path)
         self.attempt_id = attempt_id
-        self.custody_locator = custody_locator
+        self.custody_locator = normalize_calibration_custody_path(
+            custody_locator
+        )
         self.identity_epoch: Mapping[str, Any] = identity_epoch
         self.t1_bindings: Mapping[str, Any] = t1_bindings
         self.capture_wall_time_s: str | None = None
         self.exact_bound_lexeme_s: str | None = None
         self.session_id = session_id
         self.slot = slot
         self.require_committed_pin = require_committed_pin
         self.claim_id = uuid.uuid4().hex
         self.begun = False
         self.closed = False
 
     @property
     def is_bracket_session(self) -> bool:
         return self.session_id is not None
 
     def begin(self) -> None:
         """Reserve ordinarily, or authenticate a previously reserved slot."""
 
         if self.begun:
             raise CalibrationLedgerError("capture ledger lifecycle already began")
         if self.is_bracket_session:
             assert self.session_id is not None and self.slot is not None
+            try:
+                recover_calibration_ledger_append(self.ledger_path)
+            except CalibrationLedgerError as exc:
+                raise CalibrationLedgerError(
+                    "calibration ledger append recovery is required but automatic "
+                    "governed recovery did not complete; preserve the ledger and "
+                    "journal, then retry this capture command after resolving the "
+                    f"reported recovery condition: {exc}"
+                ) from exc
             _validate_reserved_bracket_slot(
                 self.ledger_path,
                 self.head_pin_path,
                 session_id=self.session_id,
                 slot=self.slot,
                 attempt_id=self.attempt_id,
                 custody_locator=self.custody_locator,
                 identity_epoch=self.identity_epoch,
                 t1_bindings=self.t1_bindings,
                 require_committed_pin=self.require_committed_pin,
             )
             claim_bracket_session_slot(
                 self.ledger_path,
                 session_id=self.session_id,
                 slot=self.slot,
                 attempt_id=self.attempt_id,
                 claim_id=self.claim_id,
             )
         else:
             append_pending_receipt(
                 self.ledger_path,
                 attempt_id=self.attempt_id,
                 custody_locator=self.custody_locator,
                 identity_epoch=self.identity_epoch,
                 t1_bindings=self.t1_bindings,
                 head_pin_path=self.head_pin_path,
                 require_committed_pin=self.require_committed_pin,
             )
         self.begun = True
 
     def abandon(self, reason: str) -> Mapping[str, Any] | None:
         """Best-effort governed closure for an interrupted writer."""
 
         if not self.begun or self.closed:
             return None
         if self.is_bracket_session:
             assert self.session_id is not None
             receipt = abort_bracket_session(
                 self.ledger_path,
                 session_id=self.session_id,
                 reason=reason,
             )
         else:
             receipt = finalize_attempt_receipt(
                 self.ledger_path,
                 attempt_id=self.attempt_id,
                 disposition="abandoned",
                 custody_locator=self.custody_locator,
                 artifact_sha256=ledger_artifact_hashes(
                     Path(self.custody_locator)
                 ),
                 identity_epoch=self.identity_epoch,
                 t1_bindings=self.t1_bindings,
                 capture_wall_time_s=self.capture_wall_time_s,
                 exact_bound_lexeme_s=self.exact_bound_lexeme_s,
             )
         self.closed = True
         return receipt
 
     def finalize(
         self, disposition: str
     ) -> tuple[Mapping[str, Any], dict[str, Any] | None]:
         """Finalize the exact attempt and return any terminal head candidate."""
 
         if not self.begun or self.closed:
             raise CalibrationLedgerError("capture ledger lifecycle is not open")
         artifacts = ledger_artifact_hashes(Path(self.custody_locator))
         if self.is_bracket_session:
             assert self.session_id is not None and self.slot is not None
             receipt = finalize_bracket_session_slot(
                 self.ledger_path,
                 session_id=self.session_id,
                 slot=self.slot,
                 disposition=disposition,
                 custody_locator=self.custody_locator,
                 artifact_sha256=artifacts,
                 identity_epoch=self.identity_epoch,
                 t1_bindings=self.t1_bindings,
                 capture_wall_time_s=self.capture_wall_time_s,
                 exact_bound_lexeme_s=self.exact_bound_lexeme_s,
             )
             if self.slot == "pre" and disposition != "valid":
                 receipt = abort_bracket_session(
                     self.ledger_path,
                     session_id=self.session_id,
                     reason=f"pre_capture_{disposition}",
                 )
             self.closed = True
             head_pin = (
                 None
                 if self.slot == "pre" and disposition == "valid"
                 else terminal_head_pin_for_session(
                     self.ledger_path, session_id=self.session_id
                 )
             )
             return receipt, head_pin
         receipt = finalize_attempt_receipt(
             self.ledger_path,
             attempt_id=self.attempt_id,
             disposition=disposition,
             custody_locator=self.custody_locator,
             artifact_sha256=artifacts,
             identity_epoch=self.identity_epoch,
             t1_bindings=self.t1_bindings,
             capture_wall_time_s=self.capture_wall_time_s,
             exact_bound_lexeme_s=self.exact_bound_lexeme_s,
         )
         self.closed = True
         return receipt, head_pin_for_receipt(receipt)
 
 
 def main(argv: list[str] | None = None) -> int:
     parser = argparse.ArgumentParser(description=__doc__)
     parser.add_argument(
         "--allow-live",
         action="store_true",
         help="explicitly confirm a lead-owned quiet-machine live run",
     )
     parser.add_argument(
         "--output-root",
         type=Path,
         default=REPO_ROOT / "runs" / "instrument_validation",
     )
     parser.add_argument("--rederive-from", type=Path)
     parser.add_argument("--output", type=Path)
     parser.add_argument("--pulse-count", type=int, default=PULSE_COUNT)
     parser.add_argument(
         "--session-id",
         help="predeclared two-slot bracket session id (requires --slot and --attempt-id)",
     )
     parser.add_argument(
         "--slot",
         choices=BRACKET_SESSION_SLOTS,
         help="exact predeclared bracket slot to capture",
     )
     parser.add_argument(
         "--attempt-id",
         help="exact attempt id already reserved for the bracket slot",
     )
     parser.add_argument(
         "--power-policy",
         default=None,
         help="operator-recorded power policy identity (e.g. 'ac_high_power'); required",
     )
     args = parser.parse_args(argv)
     bracket_values = (args.session_id, args.slot, args.attempt_id)
     bracket_mode = all(value is not None and value != "" for value in bracket_values)
     if any(value is not None for value in bracket_values) and not bracket_mode:
         print(
             "refusing: --session-id, --slot, and --attempt-id must be supplied together",
             file=sys.stderr,
         )
         return 2
     if bracket_mode and (args.rederive_from is not None or args.output is not None):
         print(
             "refusing: bracket session parameters apply only to live capture",
             file=sys.stderr,
         )
         return 2
     if not verify_frozen_protocol():
         print(
             "refusing: frozen powermetrics fiducial protocol is missing, "
             "incomplete, or disagrees with executable constants",
             file=sys.stderr,
         )
         return 2
     if args.rederive_from is not None:
         if args.output is None:
             print("refusing: --rederive-from requires --output", file=sys.stderr)
             return 2
         try:
             payload = rederive_artifact(args.rederive_from, args.output)
         except ValueError as exc:
             print(f"refusing: {exc}", file=sys.stderr)
             return 2
         print(json.dumps({"status": payload["status"], "output": str(args.output)}))
         return 0 if payload["status"] == "valid" else 1
     if args.output is not None:
         print("refusing: --output requires --rederive-from", file=sys.stderr)
         return 2
     if not args.allow_live:
         print(
             "refusing: live [QUIET-MAC] calibration is lead-owned; "
             "pass --allow-live on a quiet machine",
             file=sys.stderr,
         )
         return 77
     if not args.power_policy:
         print("refusing: --power-policy is a binding field", file=sys.stderr)
         return 2
 
     import mlx.core as mx  # noqa: PLC0415
 
     clock = SystemClock()
     validation_id = (
         args.attempt_id
         if bracket_mode
         else time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
     )
     out_dir = args.output_root / validation_id
-    custody_locator = str(out_dir.resolve())
+    custody_locator = normalize_calibration_custody_path(out_dir)
     planned_epoch = {
         "os_build": _sysctl_identity("kern.osversion"),
         "hardware_model": _sysctl_identity("hw.model"),
         "power_policy": args.power_policy,
         "sampling_interval_ms": SAMPLING_INTERVAL_MS,
         "estimator_revision": RESIDUAL_REGION_METHOD,
         "pulse_protocol_id": PROTOCOL_ID,
     }
     planned_t1 = {
         **planned_epoch,
         "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
         "anchor_method_version": CLOCK_METHOD_V2,
         "mlx_version": getattr(mx, "__version__", None),
         "protocol_sha256": sha256_path(PROTOCOL_PATH),
     }
     # D-109 reservation-first: ordinary captures append here; D-117 bracket
     # captures authenticate the exact slot that the bookend tool already
     # reserved. Both paths run before directory creation, sampler launch, and
     # all hardware capture.
     ledger_lifecycle = _CaptureLedgerLifecycle(
         ledger_path=DEFAULT_LEDGER_PATH,
         head_pin_path=DEFAULT_HEAD_PIN_PATH,
         attempt_id=validation_id,
         custody_locator=custody_locator,
         identity_epoch=planned_epoch,
         t1_bindings=planned_t1,
         session_id=args.session_id if bracket_mode else None,
         slot=args.slot if bracket_mode else None,
     )
     try:
         ledger_lifecycle.begin()
     except CalibrationLedgerError as exc:
         print(f"refusing: {exc}", file=sys.stderr)
         return 2
 
     def finalize_abandoned(
         reason: str = "writer_exit_before_slot_finalization",
     ) -> None:
         """Best effort; a failed closure leaves a fail-closed pending/open state."""
 
         try:
             ledger_lifecycle.abandon(reason)
         except Exception:  # noqa: BLE001 - pending/open is mandatory fail-closed state
             return
 
     # An actual interpreter-level uncaught exception/interrupt finalizes when
     # possible. A hard crash between these two appends intentionally leaves
     # ``pending``, which every downstream snapshot refuses.
     atexit.register(finalize_abandoned)
     (out_dir / "raw").mkdir(parents=True, exist_ok=False)
     capture_path = out_dir / "raw" / "powermetrics.plist"
     events_path = out_dir / "events.jsonl"
     events = events_path.open("w", encoding="utf-8")
 
     def emit(event_type: str, metadata: dict) -> None:
         events.write(
             json.dumps(
                 {
                     "timestamp_s": clock.now(),
                     "event_type": event_type,
                     "phase": "instrument_validation",
                     "message": event_type,
                     "metadata": metadata,
                 },
                 sort_keys=True,
             )
             + "\n"
         )
         events.flush()
 
     buffers = allocate_matmul_buffers()
     command = [
         "sudo",
         "-n",
         POWER_METRICS,
         "-b",
         "0",
         "-i",
         str(SAMPLING_INTERVAL_MS),
         "--samplers",
         SAMPLERS,
         "--format",
         "plist",
         "-o",
         str(capture_path),
     ]
     pre_spawn = clock.stamp()
     process = subprocess.Popen(
         command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
     )
     first_parse = None
     deadline = time.monotonic() + 15.0
     while time.monotonic() < deadline:
         if capture_path.exists() and capture_path.stat().st_size > 0:
             first_frame = capture_path.read_bytes().split(b"\0", 1)[0]
             if first_frame.strip():
                 try:
                     parse_powermetrics_records(first_frame)
                 except ValueError:
                     pass

exec
/bin/zsh -lc "git diff --unified=30 origin/main...HEAD -- joulewise/calibration_ledger.py | sed -n '1,620p' && git diff --unified=30 origin/main...HEAD -- scripts/validate_powermetrics_fiducial.py | sed -n '1,360p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
diff --git a/joulewise/calibration_ledger.py b/joulewise/calibration_ledger.py
index 39b551a..5836bd9 100644
--- a/joulewise/calibration_ledger.py
+++ b/joulewise/calibration_ledger.py
@@ -174,60 +174,76 @@ def _normalized_vector(
 
 def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
     """Return the path-independent identity of canonical primary bytes.
 
     The authenticated evidence document and its manifest are the canonical
     byte pair.  A copied custody tree therefore retains the same identity.
     Other receipt hashes remain custody checks but do not manufacture a new
     observation when a derived representation is regenerated.
     """
 
     identity = {
         name: artifact_sha256.get(name) for name in CONTENT_ID_ARTIFACTS
     }
     if any(not _is_sha256(value) for value in identity.values()):
         return None
     return canonical_sha256(identity)
 
 
 def artifact_hashes(custody_dir: Path) -> dict[str, str]:
     """Hash every governed artifact present in one finalized custody tree."""
 
     root = Path(custody_dir)
     result: dict[str, str] = {}
     for relative in GOVERNED_ARTIFACTS:
         path = root / relative
         if path.is_file():
             result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
     return result
 
 
+def normalize_calibration_custody_path(path: Path | str) -> str:
+    """Return the lexical absolute spelling used by reservation and capture.
+
+    Custody identity is an exact ledger binding.  Resolving symlinks in only
+    one writer would therefore change that identity even when both spellings
+    name the same directory.
+    """
+
+    try:
+        return str(Path(path).absolute())
+    except (OSError, TypeError, ValueError) as exc:
+        raise CalibrationLedgerError(
+            "calibration custody path is malformed"
+        ) from exc
+
+
 def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
     return {key: value for key, value in receipt.items() if key != "receipt_digest"}
 
 
 def _receipt_digest(receipt: Mapping[str, Any]) -> str:
     return canonical_sha256(receipt_core(receipt))
 
 
 @dataclass(frozen=True)
 class LedgerObservation:
     sequence: int
     receipt_digest: str
     attempt_id: str
     content_id: str | None
     artifact_sha256: Mapping[str, str]
     identity_epoch: Mapping[str, Any]
     t1_bindings: Mapping[str, Any]
     capture_wall_time_s: str | None
     exact_bound_lexeme_s: str | None
     disposition: str
     custody_locator: str
     observation_kind: str = "live-capture"
     bracket_session_id: str | None = None
     bracket_slot: str | None = None
     bracket_window_id: str | None = None
     bracket_plan_id: str | None = None
     bracket_plan_sha256: str | None = None
     bracket_evidence_root_id: str | None = None
     bracket_runs_root: str | None = None
 
@@ -2409,117 +2425,151 @@ def _locked_append(
                     )
                 payload = canonical_json_bytes(receipt) + b"\n"
                 _prepare_append_journal(
                     ledger_path,
                     ledger_offset=len(raw),
                     predecessor_digest=str(
                         receipts[-1]["receipt_digest"]
                         if receipts
                         else GENESIS_DIGEST
                     ),
                     payload=payload,
                 )
                 handle.seek(0, os.SEEK_END)
                 try:
                     _write_ledger_append_payload(handle, payload)
                     handle.flush()
                     os.fsync(handle.fileno())
                 except Exception:
                     # The durable journal is intentionally retained.  No
                     # ledger byte is removed; a later governed writer can
                     # complete only the journal-matching suffix.
                     raise
                 _clear_append_journal(ledger_path)
                 return _frozen_mapping(receipt)
         finally:
             os.close(descriptor)
     finally:
         os.close(lock_descriptor)
 
 
+def recover_calibration_ledger_append(ledger_path: Path) -> Path | None:
+    """Complete one authenticated journaled append without adding a receipt.
+
+    The stable ledger lock is held through suffix completion, recovery
+    evidence publication, and journal removal.  ``None`` means no recovery
+    journal was present; otherwise the returned path is the durable evidence
+    object for the completed operation.
+    """
+
+    ledger_path = Path(ledger_path)
+    ledger_path.parent.mkdir(parents=True, exist_ok=True)
+    lock_descriptor = _open_ledger_lock(ledger_path)
+    try:
+        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
+        journal, malformed = _read_append_journal(ledger_path)
+        if malformed:
+            raise CalibrationLedgerError("append recovery journal is malformed")
+        if journal is None:
+            return None
+        descriptor = os.open(
+            ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
+        )
+        try:
+            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
+                handle.seek(0)
+                raw = handle.read()
+                _recover_journaled_append(ledger_path, handle, raw)
+        finally:
+            os.close(descriptor)
+        return _append_recovery_path(ledger_path, str(journal["operation_id"]))
+    finally:
+        os.close(lock_descriptor)
+
+
 def _authenticated_head_pin(
     head_pin_path: Path,
     *,
     require_committed_pin: bool,
     repo_root: Path,
 ) -> tuple[int, str]:
     pin_path = Path(head_pin_path)
     try:
         pin_raw = pin_path.read_bytes()
         pin_value = json.loads(pin_raw)
     except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
         raise CalibrationLedgerError("head pin is unreadable") from exc
     pin = _head_pin(pin_value)
     if pin is None:
         raise CalibrationLedgerError("head pin is malformed")
     if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
         raise CalibrationLedgerError("head pin is not committed at Git HEAD")
     return pin
 
 
 def validate_bracket_session_reservation_inputs(
     *,
     session_id: str,
     window_id: str,
     plan_id: str,
     plan_sha256: str,
     evidence_root_id: str,
     runs_root: Path | str,
     slots: Mapping[str, Mapping[str, Any]],
 ) -> tuple[Mapping[str, Any], Mapping[str, Mapping[str, Any]]]:
     """Apply the exact same capability-input validation for dry-run/execute."""
 
     try:
-        normalized_runs_root = str(Path(runs_root).absolute())
-    except (OSError, TypeError, ValueError) as exc:
+        normalized_runs_root = normalize_calibration_custody_path(runs_root)
+    except CalibrationLedgerError as exc:
         raise CalibrationLedgerError("bracket session runs_root is malformed") from exc
     session_identity = {
         "session_id": session_id,
         "window_id": window_id,
         "plan_id": plan_id,
         "plan_sha256": plan_sha256,
         "evidence_root_id": evidence_root_id,
         "runs_root": normalized_runs_root,
     }
     normalized_slots: dict[str, dict[str, Any]] = {}
     if not isinstance(slots, Mapping) or set(slots) != set(BRACKET_SESSION_SLOTS):
         raise CalibrationLedgerError("bracket session must reserve exactly pre and post")
     validation_root = Path(normalized_runs_root) / "instrument_validation"
     for role in BRACKET_SESSION_SLOTS:
         source = slots.get(role)
         if not isinstance(source, Mapping):
             raise CalibrationLedgerError(f"{role} slot is malformed")
         custody_value = source.get("custody_locator")
         try:
-            custody = Path(str(custody_value)).absolute()
+            custody = Path(normalize_calibration_custody_path(custody_value))
             custody.relative_to(validation_root)
-        except (OSError, TypeError, ValueError) as exc:
+        except (CalibrationLedgerError, OSError, TypeError, ValueError) as exc:
             raise CalibrationLedgerError(
                 f"{role} custody locator is outside runs_root/instrument_validation"
             ) from exc
         normalized_slots[role] = {
             "attempt_id": source.get("attempt_id"),
             "custody_locator": str(custody),
             "identity_epoch": _normalized_vector(
                 source.get("identity_epoch"), IDENTITY_EPOCH_FIELDS
             ),
             "t1_bindings": _normalized_vector(source.get("t1_bindings"), T1_FIELDS),
             "expected_time_role": role,
         }
     if not _valid_session_identity(session_identity) or any(
         not _valid_session_slot_reservation(normalized_slots[role], role)
         for role in BRACKET_SESSION_SLOTS
     ):
         raise CalibrationLedgerError("bracket session reservation is malformed")
     if normalized_slots["pre"]["attempt_id"] == normalized_slots["post"]["attempt_id"]:
         raise CalibrationLedgerError("bracket session slot attempts must be distinct")
     return _frozen_mapping(session_identity), _frozen_mapping(normalized_slots)
 
 
 def append_bracket_session_receipt(
     ledger_path: Path,
     *,
     session_id: str,
     window_id: str,
     plan_id: str,
     plan_sha256: str,
     evidence_root_id: str,
@@ -2604,61 +2654,63 @@ def claim_bracket_session_slot(
     if slot not in BRACKET_SESSION_SLOTS:
         raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
     if not isinstance(claim_id, str) or not claim_id:
         raise CalibrationLedgerError("bracket slot claim_id must be nonempty")
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
         observations, sessions, reasons = _attempts_and_observations(receipts)
         del observations
         non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
         if non_open_reasons:
             raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
         session = next(
             (item for item in sessions if item.session_id == session_id), None
         )
         if session is None or session.state != "open":
             raise CalibrationLedgerError("bracket session is not open")
         expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
         if slot != expected_slot or session.slot_attempt_ids.get(slot) != attempt_id:
             raise CalibrationLedgerError(
                 f"bracket session slot must claim in order: expected {expected_slot}"
             )
         existing = [
             receipt
             for receipt in receipts
             if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
             and receipt.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
             and receipt.get("session_id") == session_id
             and receipt.get("slot") == slot
         ]
         if existing:
-            raise CalibrationLedgerError("calibration_ledger_bracket_slot_claimed")
+            raise CalibrationLedgerError(
+                REFUSAL_TAXONOMY["calibration_ledger_bracket_slot_claimed"]
+            )
         open_receipt = next(
             receipt
             for receipt in receipts
             if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
             and receipt.get("session_id") == session_id
         )
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         return _new_bracket_session_record(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event=BRACKET_SESSION_SLOT_CLAIM_EVENT,
             session_identity={
                 field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
             },
             fields={
                 "slot": slot,
                 "attempt_id": attempt_id,
                 "claim_id": claim_id,
             },
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def finalize_bracket_session_slot(
     ledger_path: Path,
     *,
     session_id: str,
     slot: str,
     disposition: str,
@@ -2768,61 +2820,67 @@ def abort_bracket_session(
         return _new_bracket_session_record(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event=BRACKET_SESSION_ABORT_EVENT,
             session_identity={
                 field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
             },
             fields={
                 "finalized_slots": finalized_slots,
                 "unused_slots": [
                     role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
                 ],
                 "reason": reason,
             },
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def terminal_head_pin_for_session(
     ledger_path: Path,
     *,
     session_id: str,
 ) -> dict[str, Any]:
     """Return the sole terminal pin candidate after post or governed abort."""
 
     try:
         raw = Path(ledger_path).read_bytes()
     except OSError as exc:
         raise CalibrationLedgerError("ledger is unreadable") from exc
-    receipts, parse_reasons = _parse_ledger(raw)
+    append_journal, malformed_journal = _read_append_journal(Path(ledger_path))
+    receipts, parse_reasons = _parse_ledger(
+        raw,
+        append_journal=append_journal,
+    )
+    if malformed_journal:
+        parse_reasons.add("calibration_ledger_malformed")
     observations, sessions, state_reasons = _attempts_and_observations(receipts)
     del observations
     reasons = parse_reasons | state_reasons
     if reasons:
         raise CalibrationLedgerError(", ".join(sorted(reasons)))
     session = next((item for item in sessions if item.session_id == session_id), None)
     if session is None or session.state == "open":
         raise CalibrationLedgerError("bracket session is not terminal")
     terminal_digest = (
         session.finalized_slots["post"].receipt_digest
         if session.state == "finalized"
         else session.abort_receipt_digest
     )
     final = receipts[-1] if receipts else None
     if final is None or final["receipt_digest"] != terminal_digest:
         raise CalibrationLedgerError("session closure is not the terminal ledger head")
     return _head_pin_for_valid_receipt(final)
 
 
 def append_pending_receipt(
     ledger_path: Path,
     *,
     attempt_id: str,
     custody_locator: str,
     identity_epoch: Mapping[str, Any] | None = None,
     t1_bindings: Mapping[str, Any] | None = None,
     head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
     require_committed_pin: bool = True,
     repo_root: Path = REPO_ROOT,
 ) -> Mapping[str, Any]:
@@ -2997,34 +3055,36 @@ __all__ = [
     "GOVERNED_ARTIFACTS",
     "HISTORICAL_IMPORT_EVENT_PREFIX",
     "HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA",
     "HISTORICAL_IMPORT_FINALIZATION_EVENT",
     "HISTORICAL_IMPORT_RESERVATION_EVENT",
     "HISTORICAL_IMPORT_TABLE_SCHEMA",
     "IDENTITY_EPOCH_FIELDS",
     "LEDGER_SCHEMA",
     "RECEIPT_SCHEMA",
     "REFUSAL_TAXONOMY",
     "CalibrationLedgerError",
     "CalibrationBracketSession",
     "CalibrationLedgerSnapshot",
     "HistoricalImportDurabilityUncertain",
     "HistoricalImportPlan",
     "LedgerObservation",
     "append_pending_receipt",
     "append_bracket_session_receipt",
     "claim_bracket_session_slot",
     "abort_bracket_session",
     "artifact_hashes",
     "bootstrap_historical_import",
     "custody_manifest_bytes",
     "canonical_sha256",
     "content_id_from_artifact_hashes",
     "finalize_attempt_receipt",
     "finalize_bracket_session_slot",
     "generate_historical_custody_manifest",
     "head_pin_for_receipt",
     "load_calibration_ledger_snapshot",
+    "normalize_calibration_custody_path",
     "prepare_historical_import",
+    "recover_calibration_ledger_append",
     "terminal_head_pin_for_session",
     "validate_bracket_session_reservation_inputs",
 ]
diff --git a/scripts/validate_powermetrics_fiducial.py b/scripts/validate_powermetrics_fiducial.py
index 31725f6..3799f85 100644
--- a/scripts/validate_powermetrics_fiducial.py
+++ b/scripts/validate_powermetrics_fiducial.py
@@ -35,60 +35,62 @@ from dataclasses import asdict, replace
 from decimal import Decimal
 from pathlib import Path
 from typing import Any, Mapping
 
 REPO_ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(REPO_ROOT))
 
 from joulewise.adapters.powermetrics import (  # noqa: E402
     POWER_METRICS,
     SAMPLERS,
     anchor_records_from_powermetrics,
     parse_powermetrics_records,
     samples_from_records,
 )
 from joulewise.clock import SystemClock  # noqa: E402
 from joulewise.calibration_ledger import (  # noqa: E402
     BRACKET_SESSION_OPEN_EVENT,
     BRACKET_SESSION_SCHEMA,
     BRACKET_SESSION_SLOTS,
     DEFAULT_LEDGER_PATH,
     DEFAULT_HEAD_PIN_PATH,
     CalibrationLedgerError,
     abort_bracket_session,
     append_pending_receipt,
     artifact_hashes as ledger_artifact_hashes,
     claim_bracket_session_slot,
     finalize_attempt_receipt,
     finalize_bracket_session_slot,
     head_pin_for_receipt,
     load_calibration_ledger_snapshot,
+    normalize_calibration_custody_path,
+    recover_calibration_ledger_append,
     terminal_head_pin_for_session,
 )
 from joulewise.powermetrics_fiducial import (  # noqa: E402
     BASELINE_S,
     LEGACY_PROTOCOL_ID,
     PROTOCOL_ID,
     PROTOCOL_V2_ID,
     PROTOCOL_V2_PULSE_COUNT,
     RESIDUAL_REGION_METHOD,
     PULSE_COUNT,
     PULSE_DURATION_S,
     SAMPLING_INTERVAL_MS,
     CommandedPulse,
     TraceInterval,
     WARMUP_PULSE_COUNT,
     allocate_matmul_buffers,
     capture_wall_time_from_events,
     clock_stamp_half_width_s,
     detect_pulses,
     instrument_evidence,
     protocol_definition_matches,
     pulse_schedule,
     run_matmul_pulse,
     trim_trace_after_pulses,
     rederive_detection_from_artifacts,
 )
 from joulewise.uncertainty_evidence import (  # noqa: E402
     CLOCK_METHOD_V2,
     derive_powermetrics_clock_evidence_v2,
 )
@@ -279,60 +281,65 @@ def rederive_artifact(source_dir: Path, output: Path) -> dict[str, object]:
     payload["clock_anchor"] = stored.get("clock_anchor")
     payload["clock_anchor_resolved"] = True
     output.parent.mkdir(parents=True, exist_ok=True)
     # Exclusive create: re-derivation must never clobber an existing evidence
     # artifact (same rule as the extraction and campaign-log outputs).
     with output.open("x", encoding="utf-8") as handle:
         handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
     return payload
 
 
 def _validate_reserved_bracket_slot(
     ledger_path: Path,
     head_pin_path: Path,
     *,
     session_id: str,
     slot: str,
     attempt_id: str,
     custody_locator: str,
     identity_epoch: Mapping[str, Any],
     t1_bindings: Mapping[str, Any],
     require_committed_pin: bool = True,
 ) -> None:
     """Authenticate the exact predeclared slot before capture state exists."""
 
     snapshot = load_calibration_ledger_snapshot(
         ledger_path,
         head_pin_path,
         require_committed_pin=require_committed_pin,
         verify_custody=True,
     )
+    if "calibration_ledger_recovery_required" in snapshot.refusal_reasons:
+        raise CalibrationLedgerError(
+            "calibration ledger append recovery is required; retry this capture "
+            "command so governed recovery completes before slot validation"
+        )
     session = snapshot.bracket_session_by_id.get(session_id)
     finalized_slots = set(session.finalized_slots) if session is not None else set()
     expected_slot = (
         "pre"
         if not finalized_slots
         else "post"
         if finalized_slots == {"pre"}
         else None
     )
     open_receipt = next(
         (
             receipt
             for receipt in snapshot.receipts
             if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
             and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
             and receipt.get("session_id") == session_id
         ),
         None,
     )
     reserved = (
         open_receipt.get("slots", {}).get(slot)
         if isinstance(open_receipt, Mapping)
         and isinstance(open_receipt.get("slots"), Mapping)
         else None
     )
     if (
         not snapshot.is_governed_open_bracket_extension
         or session is None
         or session.state != "open"
         or slot not in BRACKET_SESSION_SLOTS
@@ -345,83 +352,94 @@ def _validate_reserved_bracket_slot(
         or dict(reserved.get("t1_bindings", {})) != dict(t1_bindings)
     ):
         raise CalibrationLedgerError(
             "capture does not match the exact reserved bracket session slot"
         )
 
 
 class _CaptureLedgerLifecycle:
     """Route one writer attempt through ordinary or bracket-session APIs."""
 
     def __init__(
         self,
         *,
         ledger_path: Path,
         head_pin_path: Path,
         attempt_id: str,
         custody_locator: str,
         identity_epoch: Mapping[str, Any],
         t1_bindings: Mapping[str, Any],
         session_id: str | None = None,
         slot: str | None = None,
         require_committed_pin: bool = True,
     ) -> None:
         if (session_id is None) != (slot is None):
             raise CalibrationLedgerError(
                 "bracket session id and slot must be supplied together"
             )
         self.ledger_path = Path(ledger_path)
         self.head_pin_path = Path(head_pin_path)
         self.attempt_id = attempt_id
-        self.custody_locator = custody_locator
+        self.custody_locator = normalize_calibration_custody_path(
+            custody_locator
+        )
         self.identity_epoch: Mapping[str, Any] = identity_epoch
         self.t1_bindings: Mapping[str, Any] = t1_bindings
         self.capture_wall_time_s: str | None = None
         self.exact_bound_lexeme_s: str | None = None
         self.session_id = session_id
         self.slot = slot
         self.require_committed_pin = require_committed_pin
         self.claim_id = uuid.uuid4().hex
         self.begun = False
         self.closed = False
 
     @property
     def is_bracket_session(self) -> bool:
         return self.session_id is not None
 
     def begin(self) -> None:
         """Reserve ordinarily, or authenticate a previously reserved slot."""
 
         if self.begun:
             raise CalibrationLedgerError("capture ledger lifecycle already began")
         if self.is_bracket_session:
             assert self.session_id is not None and self.slot is not None
+            try:
+                recover_calibration_ledger_append(self.ledger_path)
+            except CalibrationLedgerError as exc:
+                raise CalibrationLedgerError(
+                    "calibration ledger append recovery is required but automatic "
+                    "governed recovery did not complete; preserve the ledger and "
+                    "journal, then retry this capture command after resolving the "
+                    f"reported recovery condition: {exc}"
+                ) from exc
             _validate_reserved_bracket_slot(
                 self.ledger_path,
                 self.head_pin_path,
                 session_id=self.session_id,
                 slot=self.slot,
                 attempt_id=self.attempt_id,
                 custody_locator=self.custody_locator,
                 identity_epoch=self.identity_epoch,
                 t1_bindings=self.t1_bindings,
                 require_committed_pin=self.require_committed_pin,
             )
             claim_bracket_session_slot(
                 self.ledger_path,
                 session_id=self.session_id,
                 slot=self.slot,
                 attempt_id=self.attempt_id,
                 claim_id=self.claim_id,
             )
         else:
             append_pending_receipt(
                 self.ledger_path,
                 attempt_id=self.attempt_id,
                 custody_locator=self.custody_locator,
                 identity_epoch=self.identity_epoch,
                 t1_bindings=self.t1_bindings,
                 head_pin_path=self.head_pin_path,
                 require_committed_pin=self.require_committed_pin,
             )
         self.begun = True
 
@@ -568,61 +586,61 @@ def main(argv: list[str] | None = None) -> int:
         try:
             payload = rederive_artifact(args.rederive_from, args.output)
         except ValueError as exc:
             print(f"refusing: {exc}", file=sys.stderr)
             return 2
         print(json.dumps({"status": payload["status"], "output": str(args.output)}))
         return 0 if payload["status"] == "valid" else 1
     if args.output is not None:
         print("refusing: --output requires --rederive-from", file=sys.stderr)
         return 2
     if not args.allow_live:
         print(
             "refusing: live [QUIET-MAC] calibration is lead-owned; "
             "pass --allow-live on a quiet machine",
             file=sys.stderr,
         )
         return 77
     if not args.power_policy:
         print("refusing: --power-policy is a binding field", file=sys.stderr)
         return 2
 
     import mlx.core as mx  # noqa: PLC0415
 
     clock = SystemClock()
     validation_id = (
         args.attempt_id
         if bracket_mode
         else time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
     )
     out_dir = args.output_root / validation_id
-    custody_locator = str(out_dir.resolve())
+    custody_locator = normalize_calibration_custody_path(out_dir)
     planned_epoch = {
         "os_build": _sysctl_identity("kern.osversion"),
         "hardware_model": _sysctl_identity("hw.model"),
         "power_policy": args.power_policy,
         "sampling_interval_ms": SAMPLING_INTERVAL_MS,
         "estimator_revision": RESIDUAL_REGION_METHOD,
         "pulse_protocol_id": PROTOCOL_ID,
     }
     planned_t1 = {
         **planned_epoch,
         "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
         "anchor_method_version": CLOCK_METHOD_V2,
         "mlx_version": getattr(mx, "__version__", None),
         "protocol_sha256": sha256_path(PROTOCOL_PATH),
     }
     # D-109 reservation-first: ordinary captures append here; D-117 bracket
     # captures authenticate the exact slot that the bookend tool already
     # reserved. Both paths run before directory creation, sampler launch, and
     # all hardware capture.
     ledger_lifecycle = _CaptureLedgerLifecycle(
         ledger_path=DEFAULT_LEDGER_PATH,
         head_pin_path=DEFAULT_HEAD_PIN_PATH,
         attempt_id=validation_id,
         custody_locator=custody_locator,
         identity_epoch=planned_epoch,
         t1_bindings=planned_t1,
         session_id=args.session_id if bracket_mode else None,
         slot=args.slot if bracket_mode else None,
     )
     try:

codex
The implementation delta is compact and isolates four behavior changes: pre-validation recovery, window-local session detection, journal-aware terminal-pin parsing, and lexical absolute path normalization. I’m now inspecting the surrounding contracts—not the new tests—to determine the exact disposable fixtures and the refusal boundaries each probe must exercise.
exec
/bin/zsh -lc "rg -n '"'^def (_prepare_append_journal|_read_append_journal|_recover_journaled_append|_journal_completed_raw|_parse_ledger|append_bracket_session_receipt|claim_bracket_session_slot|finalize_bracket_session_slot|terminal_head_pin_for_session|load_calibration_ledger_snapshot)|''^class CalibrationCandidate|''^def (evaluate_calibration_bracket|validate_calibration_bracket_binding|mint_calibration_bracket_binding)|BRACKET_BINDING_SCHEMA|V2_BINDING_FIELDS'"' joulewise/calibration_ledger.py joulewise/calibration_bracketing.py && sed -n '780,900p' joulewise/calibration_ledger.py && sed -n '2290,2445p' joulewise/calibration_ledger.py && sed -n '460,730p' joulewise/calibration_bracketing.py && sed -n '840,1020p' joulewise/calibration_bracketing.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
joulewise/calibration_bracketing.py:33:    V2_BINDING_FIELDS,
joulewise/calibration_bracketing.py:42:BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
joulewise/calibration_bracketing.py:77:class CalibrationCandidate:
joulewise/calibration_bracketing.py:585:        "schema_version": BRACKET_BINDING_SCHEMA,
joulewise/calibration_bracketing.py:612:def validate_calibration_bracket_binding(
joulewise/calibration_bracketing.py:627:        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
joulewise/calibration_bracketing.py:798:        or any(bindings.get(field) in (None, "") for field in V2_BINDING_FIELDS)
joulewise/calibration_bracketing.py:905:            for field in V2_BINDING_FIELDS
joulewise/calibration_bracketing.py:1015:def evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1279:            for field in V2_BINDING_FIELDS
joulewise/calibration_bracketing.py:1331:            "schema_version": BRACKET_BINDING_SCHEMA,
joulewise/calibration_bracketing.py:1672:        any(binding.get(field) != expected.get(field) for field in V2_BINDING_FIELDS)
joulewise/calibration_bracketing.py:1733:    "BRACKET_BINDING_SCHEMA",
joulewise/calibration_ledger.py:41:from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
joulewise/calibration_ledger.py:82:T1_FIELDS = tuple(V2_BINDING_FIELDS)
joulewise/calibration_ledger.py:842:def _read_append_journal(ledger_path: Path) -> tuple[Mapping[str, Any] | None, bool]:
joulewise/calibration_ledger.py:859:def _journal_completed_raw(
joulewise/calibration_ledger.py:885:def _parse_ledger(
joulewise/calibration_ledger.py:1249:def load_calibration_ledger_snapshot(
joulewise/calibration_ledger.py:2287:def _prepare_append_journal(
joulewise/calibration_ledger.py:2362:def _recover_journaled_append(
joulewise/calibration_ledger.py:2568:def append_bracket_session_receipt(
joulewise/calibration_ledger.py:2644:def claim_bracket_session_slot(
joulewise/calibration_ledger.py:2711:def finalize_bracket_session_slot(
joulewise/calibration_ledger.py:2839:def terminal_head_pin_for_session(
    except (OSError, ValueError):
        return None
    try:
        completed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=repo_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout


def _append_journal_path(ledger_path: Path) -> Path:
    ledger = Path(ledger_path)
    return ledger.with_name(f"{ledger.name}.append-journal")


def _append_recovery_path(ledger_path: Path, operation_id: str) -> Path:
    ledger = Path(ledger_path)
    return ledger.with_name(f"{ledger.name}.recovery-{operation_id}.json")


def _journal_core(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "operation_id"}


def _valid_append_journal(value: object) -> bool:
    if not isinstance(value, Mapping) or set(value) != {
        "schema_version",
        "event",
        "ledger_offset",
        "predecessor_digest",
        "payload",
        "payload_sha256",
        "operation_id",
    }:
        return False
    offset = value.get("ledger_offset")
    payload_text = value.get("payload")
    if (
        value.get("schema_version") != APPEND_JOURNAL_SCHEMA
        or value.get("event") != "prepare-append"
        or isinstance(offset, bool)
        or not isinstance(offset, int)
        or offset < 0
        or not _is_sha256(value.get("predecessor_digest"))
        or not isinstance(payload_text, str)
        or not payload_text.endswith("\n")
        or not _is_sha256(value.get("payload_sha256"))
        or not _is_sha256(value.get("operation_id"))
    ):
        return False
    payload = payload_text.encode("utf-8")
    return (
        hashlib.sha256(payload).hexdigest() == value.get("payload_sha256")
        and canonical_sha256(_journal_core(value)) == value.get("operation_id")
    )


def _read_append_journal(ledger_path: Path) -> tuple[Mapping[str, Any] | None, bool]:
    path = _append_journal_path(ledger_path)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return None, False
    except OSError:
        return None, True
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, True
    if not _valid_append_journal(value):
        return None, True
    return _frozen_mapping(value), False


def _journal_completed_raw(
    raw: bytes, journal: Mapping[str, Any]
) -> bytes | None:
    """Return the intended complete bytes only for one exact torn suffix."""

    offset = int(journal["ledger_offset"])
    payload = str(journal["payload"]).encode("utf-8")
    if offset > len(raw):
        return None
    prefix = raw[:offset]
    suffix = raw[offset:]
    if offset and not prefix.endswith(b"\n"):
        return None
    prefix_receipts, prefix_reasons = _parse_ledger(prefix)
    predecessor = (
        str(prefix_receipts[-1]["receipt_digest"])
        if prefix_receipts
        else GENESIS_DIGEST
    )
    if prefix_reasons or predecessor != journal["predecessor_digest"]:
        return None
    if not payload.startswith(suffix):
        return None
    return prefix + payload


def _parse_ledger(
    raw: bytes,
    *,
    append_journal: Mapping[str, Any] | None = None,
) -> tuple[list[Mapping[str, Any]], set[str]]:
    receipts: list[Mapping[str, Any]] = []
    reasons: set[str] = set()
    if append_journal is not None:
        completed = _journal_completed_raw(raw, append_journal)
        if completed is None:
            return receipts, {"calibration_ledger_malformed"}
        raw = completed
        reasons.add("calibration_ledger_recovery_required")
    if not raw:
        return receipts, reasons
    try:
    ledger_offset: int,
    predecessor_digest: str,
    payload: bytes,
) -> Mapping[str, Any]:
    journal: dict[str, Any] = {
        "schema_version": APPEND_JOURNAL_SCHEMA,
        "event": "prepare-append",
        "ledger_offset": ledger_offset,
        "predecessor_digest": predecessor_digest,
        "payload": payload.decode("utf-8"),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }
    journal["operation_id"] = canonical_sha256(journal)
    path = _append_journal_path(ledger_path)
    if path.exists():
        raise CalibrationLedgerError("an append recovery journal is already active")
    _atomic_private_write(path, canonical_json_bytes(journal) + b"\n")
    return _frozen_mapping(journal)


def _write_ledger_append_payload(handle: BinaryIO, payload: bytes) -> None:
    """Single injectable append boundary used by torn-write regressions."""

    written = handle.write(payload)
    if written != len(payload):
        raise OSError("short ledger append")


def _record_append_recovery(
    ledger_path: Path,
    journal: Mapping[str, Any],
    *,
    ledger_tail: bytes,
) -> None:
    payload_bytes = str(journal["payload"]).encode("utf-8")
    if ledger_tail != payload_bytes:
        raise CalibrationLedgerError(
            "append recovery evidence cannot describe an incomplete ledger tail"
        )
    evidence = {
        "schema_version": APPEND_RECOVERY_SCHEMA,
        "event": "governed-torn-tail-recovery",
        "operation_id": journal["operation_id"],
        "ledger_offset": journal["ledger_offset"],
        "predecessor_digest": journal["predecessor_digest"],
        "payload_sha256": journal["payload_sha256"],
        "observed_suffix_bytes": len(ledger_tail),
        "recovered_bytes": len(payload_bytes) - len(ledger_tail),
        "rule": "append_only_complete_journal_matching_suffix",
    }
    path = _append_recovery_path(ledger_path, str(journal["operation_id"]))
    payload = canonical_json_bytes(evidence) + b"\n"
    if path.exists():
        try:
            if path.read_bytes() == payload:
                return
        except OSError as exc:
            raise CalibrationLedgerError(
                "append recovery evidence is unreadable"
            ) from exc
        raise CalibrationLedgerError("append recovery evidence conflicts")
    _atomic_private_write(path, payload)


def _clear_append_journal(ledger_path: Path) -> None:
    try:
        _append_journal_path(ledger_path).unlink()
        _fsync_parent_directory(Path(ledger_path).parent)
    except OSError as exc:
        raise CalibrationLedgerError("append journal could not be cleared") from exc


def _recover_journaled_append(
    ledger_path: Path,
    handle: BinaryIO,
    raw: bytes,
) -> bytes:
    journal, malformed = _read_append_journal(ledger_path)
    if malformed:
        raise CalibrationLedgerError("append recovery journal is malformed")
    if journal is None:
        return raw
    completed = _journal_completed_raw(raw, journal)
    if completed is None:
        raise CalibrationLedgerError(
            "torn ledger tail does not match the append recovery journal"
        )
    offset = int(journal["ledger_offset"])
    payload = str(journal["payload"]).encode("utf-8")
    observed = len(raw) - offset
    missing = payload[observed:]
    if missing:
        handle.seek(0, os.SEEK_END)
        _write_ledger_append_payload(handle, missing)
        handle.flush()
        os.fsync(handle.fileno())
    handle.seek(0)
    completed = handle.read()
    if _journal_completed_raw(completed, journal) != completed:
        raise CalibrationLedgerError(
            "append recovery did not complete the ledger tail"
        )
    _record_append_recovery(
        ledger_path,
        journal,
        ledger_tail=completed[offset:],
    )
    _clear_append_journal(ledger_path)
    return completed


def _locked_append(
    ledger_path: Path,
    build: Any,
) -> Mapping[str, Any]:
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    lock_descriptor = _open_ledger_lock(ledger_path)
    try:
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        descriptor = os.open(
            ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
        )
        try:
            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
                handle.seek(0)
                raw = handle.read()
                raw = _recover_journaled_append(ledger_path, handle, raw)
                receipts, reasons = _parse_ledger(raw)
                if reasons:
                    raise CalibrationLedgerError(", ".join(sorted(reasons)))
                receipt = build(receipts)
                if not _valid_receipt_shape(receipt):
                    raise CalibrationLedgerError(
                        "writer constructed a malformed receipt"
                    )
                payload = canonical_json_bytes(receipt) + b"\n"
                _prepare_append_journal(
                    ledger_path,
                    ledger_offset=len(raw),
                    predecessor_digest=str(
                        receipts[-1]["receipt_digest"]
                        if receipts
                        else GENESIS_DIGEST
                    ),
                    payload=payload,
                )
                handle.seek(0, os.SEEK_END)
                try:
                    _write_ledger_append_payload(handle, payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                except Exception:
                    # The durable journal is intentionally retained.  No
                    # ledger byte is removed; a later governed writer can
                    # complete only the journal-matching suffix.
) -> dict[str, Any] | None:
    """Parse acceptance bytes only when their role-indexed pin authenticates."""

    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    # Any file route is authenticated by one of the two reviewed exact-byte
    # states: the genesis fixture retained for pre-issuance tests, or the
    # deterministically emitted issued artifact. A caller cannot turn an
    # alternate self-consistent document into authority by choosing a path.
    expected_sha256 = {
        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
        "issued": ISSUED_ACCEPTANCE_BOUND_SHA256,
    }.get(value.get("artifact_role") if isinstance(value, Mapping) else None)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        return None
    if not _valid_acceptance_bound(value):
        return None
    return dict(value)


def _authenticated_explicit_acceptance_bound(
    value: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Authenticate an in-memory artifact against the checked-in byte pin."""

    pinned = load_calibration_acceptance_bound()
    if pinned is None or dict(value) != pinned:
        return None
    return pinned


def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
    """Return the reviewed exact-byte pin for a validated artifact role."""

    return (
        ISSUED_ACCEPTANCE_BOUND_SHA256
        if artifact.get("artifact_role") == "issued"
        else DEFAULT_ACCEPTANCE_BOUND_SHA256
    )


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


_BRACKET_BINDING_KEYS = {
    "schema_version",
    "ledger_schema",
    "session_id",
    "window_id",
    "plan_id",
    "plan_sha256",
    "evidence_root_id",
    "runs_root",
    "capability_receipt_digest",
    "terminal_head",
    "endpoints",
    "binding_digest",
}
_BRACKET_ENDPOINT_KEYS = {
    "attempt_id",
    "receipt_digest",
    "content_digest",
}


def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in binding.items() if key != "binding_digest"}


def build_calibration_bracket_binding(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
) -> dict[str, Any]:
    """Bind one frozen window to its exact finalized session endpoints."""

    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
        raise ValueError("bracket binding requires a valid pinned ledger snapshot")
    session = ledger_snapshot.bracket_session_by_id.get(session_id)
    expected_identity = (
        window_id,
        plan_id,
        plan_sha256,
        evidence_root_id,
        str(Path(runs_root).absolute()),
    )
    if (
        session is None
        or session.state != "finalized"
        or (
            session.window_id,
            session.plan_id,
            session.plan_sha256,
            session.evidence_root_id,
            session.runs_root,
        )
        != expected_identity
    ):
        raise ValueError("bracket session does not match the frozen window identity")
    pre = session.finalized_slots.get("pre")
    post = session.finalized_slots.get("post")
    if (
        pre is None
        or post is None
        or pre.disposition != "valid"
        or post.disposition != "valid"
        or pre.content_id is None
        or post.content_id is None
        or post.sequence != ledger_snapshot.head_sequence
        or post.receipt_digest != ledger_snapshot.head_digest
    ):
        raise ValueError("bracket session endpoints are not valid at the terminal head")
    binding: dict[str, Any] = {
        "schema_version": BRACKET_BINDING_SCHEMA,
        "ledger_schema": LEDGER_SCHEMA,
        "session_id": session.session_id,
        "window_id": session.window_id,
        "plan_id": session.plan_id,
        "plan_sha256": session.plan_sha256,
        "evidence_root_id": session.evidence_root_id,
        "runs_root": session.runs_root,
        "capability_receipt_digest": session.capability_receipt_digest,
        "terminal_head": {
            "sequence": post.sequence,
            "head_digest": post.receipt_digest,
            "ledger_schema": LEDGER_SCHEMA,
        },
        "endpoints": {
            role: {
                "attempt_id": observation.attempt_id,
                "receipt_digest": observation.receipt_digest,
                "content_digest": observation.content_id,
            }
            for role, observation in (("pre", pre), ("post", post))
        },
    }
    binding["binding_digest"] = _canonical_sha256(binding)
    return binding


def validate_calibration_bracket_binding(
    binding: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    window_id: str | None = None,
    plan_id: str | None = None,
    plan_sha256: str | None = None,
    evidence_root_id: str | None = None,
    runs_root: Path | str | None = None,
) -> tuple[LedgerObservation, LedgerObservation] | None:
    """Return the exact authenticated pair, or ``None`` on any substitution."""

    if (
        not isinstance(binding, Mapping)
        or set(binding) != _BRACKET_BINDING_KEYS
        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
        or binding.get("ledger_schema") != LEDGER_SCHEMA
        or not _valid_sha256(binding.get("plan_sha256"))
        or not _valid_sha256(binding.get("capability_receipt_digest"))
        or not _valid_sha256(binding.get("binding_digest"))
        or binding.get("binding_digest") != _canonical_sha256(_binding_core(binding))
        or not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
    ):
        return None
    if any(
        not isinstance(value, str) or not value
        for value in (window_id, plan_id, plan_sha256, evidence_root_id)
    ) or runs_root is None:
        return None
    expected_runs_root = str(Path(runs_root).absolute())
    for field, expected in (
        ("window_id", window_id),
        ("plan_id", plan_id),
        ("plan_sha256", plan_sha256),
        ("evidence_root_id", evidence_root_id),
        ("runs_root", expected_runs_root),
    ):
        if binding.get(field) != expected:
            return None
    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
    if (
        session is None
        or session.state != "finalized"
        or binding.get("window_id") != session.window_id
        or binding.get("plan_id") != session.plan_id
        or binding.get("plan_sha256") != session.plan_sha256
        or binding.get("evidence_root_id") != session.evidence_root_id
        or binding.get("runs_root") != session.runs_root
        or binding.get("capability_receipt_digest")
        != session.capability_receipt_digest
    ):
        return None
    terminal = binding.get("terminal_head")
    endpoints = binding.get("endpoints")
    if (
        not isinstance(terminal, Mapping)
        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
        or terminal.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(terminal.get("sequence"), bool)
        or not isinstance(terminal.get("sequence"), int)
        or not _valid_sha256(terminal.get("head_digest"))
        or not isinstance(endpoints, Mapping)
        or set(endpoints) != {"pre", "post"}
    ):
        return None
    resolved: list[LedgerObservation] = []
    for role in ("pre", "post"):
        endpoint = endpoints.get(role)
        observation = session.finalized_slots.get(role)
        if (
            not isinstance(endpoint, Mapping)
            or set(endpoint) != _BRACKET_ENDPOINT_KEYS
            or observation is None
            or observation.disposition != "valid"
            or observation.content_id is None
            or endpoint.get("attempt_id") != observation.attempt_id
            or endpoint.get("receipt_digest") != observation.receipt_digest
            or endpoint.get("content_digest") != observation.content_id
        ):
            return None
        resolved.append(observation)
    post = resolved[1]
    if (
        terminal.get("sequence") != post.sequence
        or terminal.get("head_digest") != post.receipt_digest
        or post.sequence > len(ledger_snapshot.receipts)
        or ledger_snapshot.receipts[post.sequence - 1].get("receipt_digest")
        != post.receipt_digest
    ):
        return None
    return resolved[0], resolved[1]


def _binding_evidence_authentic(
    evidence: Mapping[str, Any], bindings: Mapping[str, Any]
) -> bool:
    binding_evidence = evidence.get("binding_evidence")
    binary = (
        binding_evidence.get("powermetrics_binary")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    power_policy = (
        binding_evidence.get("power_policy")
        if isinstance(binding_evidence, Mapping)
        else None
    )
    # Canonical form MUST match the generation (powermetrics_fiducial) and
    # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
    # P2 — the ASCII-default form made authentic non-ASCII binding vectors
    # unmatchable as bracket candidates).
    canonical = json.dumps(
        dict(bindings),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
            parse_float=str,
            parse_int=str,
        )
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    stored_lexeme = (
        decimal_evidence.get("b_fiducial_s")
        if isinstance(decimal_evidence, Mapping)
        else None
    )
    stored_decimal = _decimal(stored_lexeme)
    if (
        stored_decimal is not None
        and float(stored_decimal) == float(effective_bound)
    ):
        effective_bound_lexeme = stored_lexeme
    else:
        # A physical re-fit can widen beyond the stored scalar. Its returned
        # representation becomes the re-derivation source lexeme; no later
        # acceptance comparison converts that value through binary64 again.
        effective_bound_lexeme = str(float(effective_bound))
    return CalibrationCandidate(
        relative_path=relative,
        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
        protocol_id=str(protocol_id),
        capture_wall_time_s=float(capture),
        b_fiducial_s=effective_bound_lexeme,
        bindings=dict(bindings),
    )


def _candidate_from_observation(
    observation: LedgerObservation,
) -> CalibrationCandidate | None:
    """Authenticate one valid ledger observation from its custody locator."""

    if observation.disposition != "valid" or observation.content_id is None:
        return None
    custody = Path(observation.custody_locator)
    candidate = load_calibration_candidate(
        custody,
        runs_root=custody.parent.parent,
    )
    if candidate is None:
        return None
    bound = _candidate_decimal(candidate)
    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
    try:
        receipt_capture = float(observation.capture_wall_time_s)
    except (TypeError, ValueError):
        return None
    if (
        candidate.manifest_sha256
        != observation.artifact_sha256.get("manifest.json")
        or candidate.evidence_sha256
        != observation.artifact_sha256.get("instrument_evidence.json")
        or content_id_from_artifact_hashes(observation.artifact_sha256)
        != observation.content_id
        or bound is None
        or receipt_bound is None
        or bound != receipt_bound
        or candidate.capture_wall_time_s != receipt_capture
        or any(
            candidate.bindings.get(field) != observation.t1_bindings.get(field)
            for field in V2_BINDING_FIELDS
        )
        or any(
            candidate.bindings.get(field) != observation.identity_epoch.get(field)
            for field in ACCEPTANCE_IDENTITY_FIELDS
        )
    ):
        return None
    return replace(
        candidate,
        relative_path=observation.custody_locator,
        attempt_id=observation.attempt_id,
        content_id=observation.content_id,
        ledger_receipt_digest=observation.receipt_digest,
        bracket_session_id=observation.bracket_session_id,
        bracket_slot=observation.bracket_slot,
        bracket_window_id=observation.bracket_window_id,
        bracket_plan_id=observation.bracket_plan_id,
        bracket_plan_sha256=observation.bracket_plan_sha256,
        bracket_evidence_root_id=observation.bracket_evidence_root_id,
        bracket_runs_root=observation.bracket_runs_root,
    )


def discover_calibration_candidates(
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> tuple[CalibrationCandidate, ...]:
    """Enumerate valid endpoints from the sole ledger authority.

    The mechanism closes workflow omission, unregistered evidence, and
    rollback/stale-head consumption; it does not defend against a malicious
    trusted writer or a rewrite of both Git and full ledger history.
    """

    if (
        not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
        or not ledger_snapshot.valid
        and not ledger_snapshot.is_governed_open_bracket_extension
    ):
        return ()
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    candidates: list[CalibrationCandidate] = []
    for observation in ledger_snapshot.observations:
        if (
            observation.disposition != "valid"
            or observation.is_historical_import
            or observation.bracket_session_id is not None
            and observation.bracket_session_id not in finalized_session_ids
        ):
            continue
        candidate = _candidate_from_observation(observation)
        if candidate is None:
            return ()
        candidates.append(candidate)
    return tuple(candidates)


def _prior_set_matches_import_cutoff_prefix(
    artifact: Mapping[str, Any],
    ledger_snapshot: CalibrationLedgerSnapshot,
) -> bool:
    """Bind issuance prior-set data to the import-marked cutoff prefix."""

    cutoff = artifact["ledger_cutoff"]
    prefix = tuple(
        observation
        for observation in ledger_snapshot.observations
        if observation.sequence <= cutoff["sequence"]
    )
    # The checked-in schema fixture predates issuance and deliberately has a
    # genesis cutoff. Production issuance, or any fixture containing imported
    # prefix rows, must satisfy the exact marker-bound comparison below.
    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
        return True
    if any(not observation.is_historical_import for observation in prefix):
        return False
    catalog = artifact["prior_observation_set"]["epoch_catalog"]
    expected = {
        (
            row["attempt_id"],
            row["content_id"],
            row["disposition"],
            row["epoch_id"],
        )
        for row in artifact["prior_observation_set"]["observations"]
    }
    observed: set[tuple[str, str, str, str]] = set()
    for observation in prefix:
        epoch_ids = [
            epoch_id
            for epoch_id, epoch in catalog.items()
            if dict(epoch) == dict(observation.identity_epoch)
        ]
        if observation.content_id is None or len(epoch_ids) != 1:
            return False
        observed.add(
            (
                observation.attempt_id,
                observation.content_id,
                observation.classification_disposition,
                epoch_ids[0],
            )
        )
    return observed == expected and len(observed) == len(prefix)


def evaluate_calibration_bracket(
    candidates: Sequence[CalibrationCandidate],
    *,
    window_start_s: float,
    window_end_s: float,
    bindings: Mapping[str, Any],

exec
/bin/zsh -lc "sed -n '2520,2865p' joulewise/calibration_ledger.py && sed -n '1015,1375p' joulewise/calibration_bracketing.py && git show origin/main:tests/test_calibration_ledger.py | rg -n '"'^class |''^    def _|append_bracket_session_receipt|head_pin'"' | head -160 && git show origin/main:tests/test_calibration_bracketing.py | rg -n '"'^class |''^    def _|CalibrationCandidate'"\\(' | head -180" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:

    try:
        normalized_runs_root = normalize_calibration_custody_path(runs_root)
    except CalibrationLedgerError as exc:
        raise CalibrationLedgerError("bracket session runs_root is malformed") from exc
    session_identity = {
        "session_id": session_id,
        "window_id": window_id,
        "plan_id": plan_id,
        "plan_sha256": plan_sha256,
        "evidence_root_id": evidence_root_id,
        "runs_root": normalized_runs_root,
    }
    normalized_slots: dict[str, dict[str, Any]] = {}
    if not isinstance(slots, Mapping) or set(slots) != set(BRACKET_SESSION_SLOTS):
        raise CalibrationLedgerError("bracket session must reserve exactly pre and post")
    validation_root = Path(normalized_runs_root) / "instrument_validation"
    for role in BRACKET_SESSION_SLOTS:
        source = slots.get(role)
        if not isinstance(source, Mapping):
            raise CalibrationLedgerError(f"{role} slot is malformed")
        custody_value = source.get("custody_locator")
        try:
            custody = Path(normalize_calibration_custody_path(custody_value))
            custody.relative_to(validation_root)
        except (CalibrationLedgerError, OSError, TypeError, ValueError) as exc:
            raise CalibrationLedgerError(
                f"{role} custody locator is outside runs_root/instrument_validation"
            ) from exc
        normalized_slots[role] = {
            "attempt_id": source.get("attempt_id"),
            "custody_locator": str(custody),
            "identity_epoch": _normalized_vector(
                source.get("identity_epoch"), IDENTITY_EPOCH_FIELDS
            ),
            "t1_bindings": _normalized_vector(source.get("t1_bindings"), T1_FIELDS),
            "expected_time_role": role,
        }
    if not _valid_session_identity(session_identity) or any(
        not _valid_session_slot_reservation(normalized_slots[role], role)
        for role in BRACKET_SESSION_SLOTS
    ):
        raise CalibrationLedgerError("bracket session reservation is malformed")
    if normalized_slots["pre"]["attempt_id"] == normalized_slots["post"]["attempt_id"]:
        raise CalibrationLedgerError("bracket session slot attempts must be distinct")
    return _frozen_mapping(session_identity), _frozen_mapping(normalized_slots)


def append_bracket_session_receipt(
    ledger_path: Path,
    *,
    session_id: str,
    window_id: str,
    plan_id: str,
    plan_sha256: str,
    evidence_root_id: str,
    runs_root: Path | str,
    slots: Mapping[str, Mapping[str, Any]],
    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
    require_committed_pin: bool = True,
    repo_root: Path = REPO_ROOT,
) -> Mapping[str, Any]:
    """Atomically reserve exactly one immutable pre/post bracket capability.

    Physical-head equality with the committed pin is checked here, at open,
    and deliberately not checked again while either already-reserved slot is
    finalized. Claim evaluation remains impossible until the terminal head
    pin is emitted, reviewed, and committed.
    """

    session_identity, normalized_slots = validate_bracket_session_reservation_inputs(
        session_id=session_id,
        window_id=window_id,
        plan_id=plan_id,
        plan_sha256=plan_sha256,
        evidence_root_id=evidence_root_id,
        runs_root=runs_root,
        slots=slots,
    )
    pin = _authenticated_head_pin(
        Path(head_pin_path),
        require_committed_pin=require_committed_pin,
        repo_root=Path(repo_root),
    )

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        if (len(receipts), predecessor) != pin:
            raise CalibrationLedgerError(
                "physical ledger head differs from the committed pin"
            )
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        if reasons:
            raise CalibrationLedgerError(", ".join(sorted(reasons)))
        reserved_attempts = {
            attempt_id
            for session in sessions
            for attempt_id in session.slot_attempt_ids.values()
        }
        ordinary_attempts = {
            str(receipt["attempt_id"])
            for receipt in receipts
            if receipt.get("schema_version") == RECEIPT_SCHEMA
        }
        proposed_attempts = {
            normalized_slots[role]["attempt_id"] for role in BRACKET_SESSION_SLOTS
        }
        if (
            any(session.session_id == session_id for session in sessions)
            or proposed_attempts & (reserved_attempts | ordinary_attempts)
        ):
            raise CalibrationLedgerError("bracket session identity conflicts with ledger")
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_OPEN_EVENT,
            session_identity=session_identity,
            fields={"slots": normalized_slots},
        )

    return _locked_append(Path(ledger_path), build)


def claim_bracket_session_slot(
    ledger_path: Path,
    *,
    session_id: str,
    slot: str,
    attempt_id: str,
    claim_id: str,
) -> Mapping[str, Any]:
    """Append one process-death-stable exclusive claim for a reserved slot."""

    if slot not in BRACKET_SESSION_SLOTS:
        raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
    if not isinstance(claim_id, str) or not claim_id:
        raise CalibrationLedgerError("bracket slot claim_id must be nonempty")

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
        session = next(
            (item for item in sessions if item.session_id == session_id), None
        )
        if session is None or session.state != "open":
            raise CalibrationLedgerError("bracket session is not open")
        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if slot != expected_slot or session.slot_attempt_ids.get(slot) != attempt_id:
            raise CalibrationLedgerError(
                f"bracket session slot must claim in order: expected {expected_slot}"
            )
        existing = [
            receipt
            for receipt in receipts
            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
            and receipt.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
            and receipt.get("session_id") == session_id
            and receipt.get("slot") == slot
        ]
        if existing:
            raise CalibrationLedgerError(
                REFUSAL_TAXONOMY["calibration_ledger_bracket_slot_claimed"]
            )
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_SLOT_CLAIM_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "slot": slot,
                "attempt_id": attempt_id,
                "claim_id": claim_id,
            },
        )

    return _locked_append(Path(ledger_path), build)


def finalize_bracket_session_slot(
    ledger_path: Path,
    *,
    session_id: str,
    slot: str,
    disposition: str,
    custody_locator: str,
    artifact_sha256: Mapping[str, str] | None = None,
    identity_epoch: Mapping[str, Any] | None = None,
    t1_bindings: Mapping[str, Any] | None = None,
    capture_wall_time_s: str | None = None,
    exact_bound_lexeme_s: str | None = None,
) -> Mapping[str, Any]:
    """Fill exactly one reserved session slot in mandatory pre/post order."""

    if slot not in BRACKET_SESSION_SLOTS:
        raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
    if disposition not in FINAL_DISPOSITIONS:
        raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
    artifacts = dict(artifact_sha256 or {})
    content_id = content_id_from_artifact_hashes(artifacts)
    normalized_epoch = _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS)
    normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
        by_id = {session.session_id: session for session in sessions}
        session = by_id.get(session_id)
        if session is None or session.state != "open":
            raise CalibrationLedgerError("bracket session is not open")
        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
        if slot != expected_slot or slot in session.finalized_slots:
            raise CalibrationLedgerError(
                f"bracket session slot must finalize in order: expected {expected_slot}"
            )
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        reserved = open_receipt["slots"][slot]
        if (
            reserved["custody_locator"] != custody_locator
            or dict(reserved["identity_epoch"]) != normalized_epoch
            or dict(reserved["t1_bindings"]) != normalized_t1
        ):
            raise CalibrationLedgerError(
                "slot finalization conflicts with the reserved session binding"
            )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_FINALIZATION_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "slot": slot,
                "attempt_id": reserved["attempt_id"],
                "content_id": content_id,
                "artifact_sha256": dict(sorted(artifacts.items())),
                "identity_epoch": normalized_epoch,
                "t1_bindings": normalized_t1,
                "capture_wall_time_s": capture_wall_time_s,
                "exact_bound_lexeme_s": exact_bound_lexeme_s,
                "disposition": disposition,
                "custody_locator": custody_locator,
            },
        )

    return _locked_append(Path(ledger_path), build)


def abort_bracket_session(
    ledger_path: Path,
    *,
    session_id: str,
    reason: str,
) -> Mapping[str, Any]:
    """Append a governed terminal closure without deleting partial receipts."""

    if not isinstance(reason, str) or not reason:
        raise CalibrationLedgerError("bracket session abort reason must be nonempty")

    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        observations, sessions, reasons = _attempts_and_observations(receipts)
        del observations
        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
        if non_open_reasons:
            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
        session = next(
            (item for item in sessions if item.session_id == session_id), None
        )
        if session is None or session.state != "open":
            raise CalibrationLedgerError("bracket session is not open")
        open_receipt = next(
            receipt
            for receipt in receipts
            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
            and receipt.get("session_id") == session_id
        )
        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
        finalized_slots = list(session.finalized_slots)
        return _new_bracket_session_record(
            sequence=len(receipts) + 1,
            predecessor_digest=str(predecessor),
            event=BRACKET_SESSION_ABORT_EVENT,
            session_identity={
                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
            },
            fields={
                "finalized_slots": finalized_slots,
                "unused_slots": [
                    role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
                ],
                "reason": reason,
            },
        )

    return _locked_append(Path(ledger_path), build)


def terminal_head_pin_for_session(
    ledger_path: Path,
    *,
    session_id: str,
) -> dict[str, Any]:
    """Return the sole terminal pin candidate after post or governed abort."""

    try:
        raw = Path(ledger_path).read_bytes()
    except OSError as exc:
        raise CalibrationLedgerError("ledger is unreadable") from exc
    append_journal, malformed_journal = _read_append_journal(Path(ledger_path))
    receipts, parse_reasons = _parse_ledger(
        raw,
        append_journal=append_journal,
    )
    if malformed_journal:
        parse_reasons.add("calibration_ledger_malformed")
    observations, sessions, state_reasons = _attempts_and_observations(receipts)
    del observations
    reasons = parse_reasons | state_reasons
    if reasons:
        raise CalibrationLedgerError(", ".join(sorted(reasons)))
    session = next((item for item in sessions if item.session_id == session_id), None)
    if session is None or session.state == "open":
        raise CalibrationLedgerError("bracket session is not terminal")
    terminal_digest = (
def evaluate_calibration_bracket(
    candidates: Sequence[CalibrationCandidate],
    *,
    window_start_s: float,
    window_end_s: float,
    bindings: Mapping[str, Any],
    policy: CalibrationBracketingPolicy,
    acceptance_bound: Mapping[str, Any] | None = None,
    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
    bracket_binding: Mapping[str, Any] | None = None,
    bracket_window_id: str | None = None,
    bracket_plan_id: str | None = None,
    bracket_plan_sha256: str | None = None,
    bracket_evidence_root_id: str | None = None,
    bracket_runs_root: Path | str | None = None,
    _allow_unissued_fixture: bool = False,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Select a causal bracket and apply the provenance-bound D-079 budget."""

    result: dict[str, Any] = {
        "schema_version": BRACKET_SCHEMA,
        "policy": {
            "require_bracket": policy.require_bracket,
            "calibration_bracket_max_drift_s": (
                policy.calibration_bracket_max_drift_s
            ),
        },
        "window_start_s": window_start_s,
        "window_end_s": window_end_s,
        "pre": None,
        "post": None,
        "endpoint_max_b_fiducial_s": None,
        "calibration_drift_allowance_s": None,
        "b_fiducial_s": None,
        "drift_s": None,
        "acceptance": None,
        "bracket_binding": None,
        "status": "not_required" if not policy.require_bracket else "failed",
    }
    if not policy.require_bracket:
        return result, ()
    if (
        not math.isfinite(window_start_s)
        or not math.isfinite(window_end_s)
        or window_start_s >= window_end_s
    ):
        return result, ("instrument_calibration_bracket_missing",)

    using_default_bound = acceptance_bound is None
    artifact = (
        load_calibration_acceptance_bound()
        if using_default_bound
        else _authenticated_explicit_acceptance_bound(acceptance_bound)
    )
    if artifact is None:
        result["acceptance"] = {
            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
            "artifact": None,
            "freshness": {
                "status": "stale",
                "reason": "acceptance_artifact_missing_or_invalid",
            },
        }
        return result, ("calibration_acceptance_bound_stale",)
    artifact_role = artifact["artifact_role"]
    artifact_sha256 = _acceptance_artifact_sha256(artifact)
    if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
        result["acceptance"] = {
            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
            "artifact": {
                "acceptance_id": artifact["acceptance_id"],
                "artifact_sha256": artifact_sha256,
                "authentication": "checked_in_genesis_fixture_byte_sha256_pin",
                "artifact_role": artifact_role,
                "claim_eligible": False,
            },
            "freshness": {
                "status": "stale",
                "reason": "acceptance_artifact_unissued_fixture",
            },
        }
        return result, ("calibration_acceptance_bound_stale",)
    cutoff = artifact["ledger_cutoff"]
    result["acceptance"] = {
        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
        "artifact": {
            "acceptance_id": artifact["acceptance_id"],
            "artifact_sha256": artifact_sha256,
            "authentication": (
                "checked_in_issued_artifact_byte_sha256_pin"
                if artifact_role == "issued"
                else "checked_in_genesis_fixture_byte_sha256_pin"
            ),
            "artifact_role": artifact_role,
            "claim_eligible": False,
        },
        "freshness": {
            "status": "stale",
            "reason": "acceptance_artifact_ledger_authentication_pending",
        },
    }
    if ledger_snapshot is None:
        return result, ("calibration_ledger_snapshot_required",)
    if ledger_snapshot.refusal_reasons:
        return result, tuple(ledger_snapshot.refusal_reasons)
    if (
        ledger_snapshot.baseline_sequence != cutoff["sequence"]
        or ledger_snapshot.baseline_digest != cutoff["head_digest"]
        or ledger_snapshot.ledger_schema != cutoff["ledger_schema"]
        or artifact_role == "issued"
        and (
            ledger_snapshot.head_sequence <= 0
            or ledger_snapshot.head_digest == "0" * 64
        )
    ):
        return result, ("calibration_ledger_baseline_missing",)
    if not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot):
        return result, ("calibration_ledger_baseline_missing",)
    identity_epoch = artifact["identity_epoch"]
    prospective = artifact["prospective_rederivation"]
    result["policy"].update(
        {
            "calibration_bracket_max_drift_s_role": (
                "legacy_obsolete_not_an_acceptance_comparator"
            ),
            "acceptance_bound_id": artifact["acceptance_id"],
            "operative_bracket_screen_decimal_s": (
                artifact["decimal_derivation"]["ratified_operatives"][
                    "bracket_screen_s"
                ]
            ),
        }
    )
    observed_identity = {
        field: bindings.get(field) for field in ACCEPTANCE_IDENTITY_FIELDS
    }
    stale_fields = [
        field
        for field in ACCEPTANCE_IDENTITY_FIELDS
        if observed_identity.get(field) != identity_epoch.get(field)
    ]
    freshness_status = "stale" if stale_fields else "fresh"
    result["acceptance"] = {
        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
        "artifact": {
            "acceptance_id": artifact["acceptance_id"],
            "artifact_sha256": artifact_sha256,
            "authentication": (
                "checked_in_issued_artifact_byte_sha256_pin"
                if artifact_role == "issued"
                else "checked_in_genesis_fixture_byte_sha256_pin"
            ),
            "artifact_role": artifact_role,
            "claim_eligible": artifact_role == "issued",
            "derivation_sha256": artifact["derivation_sha256"],
        },
        "freshness": {
            "status": freshness_status,
            "basis": "exact_identity_epoch",
            "expected_identity_epoch": dict(identity_epoch),
            "observed_identity_epoch": observed_identity,
            "trigger_guard_protocol_sha256": prospective["protocol_sha256"],
            "trigger_guard_estimator_code_sha256": dict(
                prospective["estimator_code_sha256"]
            ),
            "stale_fields": stale_fields,
            "calendar_expiry": None,
        },
        "prospective_rederivation": {
            "observation_rule": prospective["trigger_observation_rule"],
            "candidate_set_boundary": (
                "authenticated_calibration_ledger_snapshot_only"
            ),
            "global_runs_root_scan": False,
            "mandatory_triggers": list(prospective["triggers"]),
            "observed_triggers": [],
        },
        "numeric_semantics": {
            "comparisons": "decimal",
            "reducer_boundary": "binary64_recorded_below",
        },
        "ledger_snapshot": {
            "ledger_schema": ledger_snapshot.ledger_schema,
            "sequence": ledger_snapshot.head_sequence,
            "head_digest": ledger_snapshot.head_digest,
            "baseline_sequence": ledger_snapshot.baseline_sequence,
            "baseline_digest": ledger_snapshot.baseline_digest,
            "load_count": 1,
        },
        "preflight": None,
        "drift": None,
    }
    if stale_fields:
        return result, ("calibration_acceptance_bound_stale",)
    observations_by_attempt = ledger_snapshot.observation_by_attempt
    finalized_session_ids = {
        session.session_id
        for session in ledger_snapshot.bracket_sessions
        if session.state == "finalized"
    }
    registered_valid = {
        (
            observation.attempt_id,
            observation.content_id,
            observation.receipt_digest,
        )
        for observation in ledger_snapshot.observations
        if observation.disposition == "valid"
        and not observation.is_historical_import
        and (
            observation.bracket_session_id is None
            or observation.bracket_session_id in finalized_session_ids
        )
    }
    supplied_valid = {
        (
            candidate.attempt_id,
            candidate.content_id,
            candidate.ledger_receipt_digest,
        )
        for candidate in candidates
    }
    # Even the low-level evaluator requires the complete ledger enumeration.
    # This prevents a caller from narrowing the registered universe to a
    # favorable subset while still passing per-candidate membership checks.
    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
        return result, ("calibration_ledger_off_ledger_artifact",)
    for candidate in candidates:
        observation = (
            observations_by_attempt.get(candidate.attempt_id)
            if isinstance(candidate.attempt_id, str)
            else None
        )
        if (
            observation is None
            or observation.disposition != "valid"
            or candidate.content_id != observation.content_id
            or candidate.ledger_receipt_digest != observation.receipt_digest
            or candidate.manifest_sha256
            != observation.artifact_sha256.get("manifest.json")
            or candidate.evidence_sha256
            != observation.artifact_sha256.get("instrument_evidence.json")
            or candidate.bracket_session_id != observation.bracket_session_id
            or candidate.bracket_slot != observation.bracket_slot
            or candidate.bracket_window_id != observation.bracket_window_id
            or candidate.bracket_plan_id != observation.bracket_plan_id
            or candidate.bracket_plan_sha256
            != observation.bracket_plan_sha256
            or candidate.bracket_evidence_root_id
            != observation.bracket_evidence_root_id
            or candidate.bracket_runs_root != observation.bracket_runs_root
        ):
            return result, ("calibration_ledger_off_ledger_artifact",)
    # A complete session pair makes the binding mandatory only for a window
    # that pair can causally and freshly bracket.  ``candidates`` still spans
    # the full registered universe above, preserving the anti-withholding
    # equality check without coupling historical ordinary windows to later
    # session observations.
    matching = [
        candidate
        for candidate in candidates
        if candidate.protocol_id == PROTOCOL_ID
        and all(
            candidate.bindings.get(field) == bindings.get(field)
            for field in V2_BINDING_FIELDS
        )
    ]
    window_session_pre_ids = {
        candidate.bracket_session_id
        for candidate in matching
        if candidate.bracket_session_id is not None
        and candidate.bracket_slot == "pre"
        and candidate.capture_wall_time_s <= window_start_s
        and window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
    }
    window_session_post_ids = {
        candidate.bracket_session_id
        for candidate in matching
        if candidate.bracket_session_id is not None
        and candidate.bracket_slot == "post"
        and candidate.capture_wall_time_s >= window_end_s
        and candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
    }
    has_session_candidates = (
        bool(window_session_pre_ids & window_session_post_ids)
        or bracket_binding is not None
    )
    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
    if has_session_candidates:
        if (
            bracket_binding is None
            or not all(
                isinstance(value, str) and bool(value)
                for value in (
                    bracket_window_id,
                    bracket_plan_id,
                    bracket_plan_sha256,
                    bracket_evidence_root_id,
                )
            )
            or bracket_runs_root is None
        ):
            return result, ("calibration_bracket_binding_missing",)
        expected_runs_root = str(Path(bracket_runs_root).absolute())
        bound_observations = validate_calibration_bracket_binding(
            bracket_binding,
            ledger_snapshot,
            window_id=bracket_window_id,
            plan_id=bracket_plan_id,
            plan_sha256=bracket_plan_sha256,
            evidence_root_id=bracket_evidence_root_id,
            runs_root=expected_runs_root,
        )
        if bound_observations is None:
            return result, ("calibration_bracket_binding_invalid",)
        result["bracket_binding"] = {
            "schema_version": BRACKET_BINDING_SCHEMA,
            "binding_digest": bracket_binding["binding_digest"],
            "session_id": bracket_binding["session_id"],
            "window_id": bracket_binding["window_id"],
            "plan_id": bracket_binding["plan_id"],
            "plan_sha256": bracket_binding["plan_sha256"],
            "evidence_root_id": bracket_binding["evidence_root_id"],
            "runs_root": bracket_binding["runs_root"],
        }
        bound_session_id = str(bracket_binding["session_id"])
        for candidate in candidates:
            if candidate.bracket_session_id != bound_session_id:
                continue
            if (
                candidate.bracket_window_id,
                candidate.bracket_plan_id,
                candidate.bracket_plan_sha256,
                candidate.bracket_evidence_root_id,
                candidate.bracket_runs_root,
            ) != (
                bracket_window_id,
                bracket_plan_id,
                bracket_plan_sha256,
                bracket_evidence_root_id,
                expected_runs_root,
            ):
                return result, ("calibration_bracket_binding_invalid",)
    # v2 remains an authenticated validation/reduction artifact, but only the
    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
    matching_decimals: dict[int, Decimal] = {}
    for candidate in matching:
        candidate_decimal = _candidate_decimal(candidate)
        if candidate_decimal is None or candidate_decimal < 0:
            return result, ("instrument_calibration_invalid",)
        matching_decimals[id(candidate)] = candidate_decimal
    corpus_members = artifact["derivation_corpus"]["members"]
    observed_triggers = result["acceptance"]["prospective_rederivation"][
        "observed_triggers"
    ]
    if (
        protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
        or _current_estimator_code_sha256()
        != dict(prospective["estimator_code_sha256"])
    ):
        observed_triggers.append("protocol_or_estimator_byte_change")
45:    append_bracket_session_receipt,
57:    head_pin_for_receipt,
60:    terminal_head_pin_for_session,
84:class CalibrationLedgerTests(unittest.TestCase):
111:    def _write_pin(self, value: dict) -> None:
114:    def _isolated_cli_checkout(self) -> tuple[Path, Path]:
161:    def _custody(self, attempt_id: str) -> Path:
177:    def _reserve(self, attempt_id: str, custody: Path):
184:            head_pin_path=self.pin,
188:    def _finalize(self, attempt_id: str, custody: Path, disposition: str = "valid"):
201:    def _snapshot(self, *, verify_custody: bool = True):
211:    def _open_bracket_session(self, session_id: str = "session-alpha"):
212:        return append_bracket_session_receipt(
244:            head_pin_path=self.pin,
248:    def _finalize_bracket_slot(self, session_id: str, slot: str):
268:    def _historical_custody(
318:    def _historical_fixture(self):
354:    def _historical_import_args(self, table: dict, custodies: list[Path]) -> dict:
379:        self._write_pin(head_pin_for_receipt(pending))
445:            terminal_head_pin_for_session(
457:    def _create_torn_session_finalization(self) -> dict:
490:    def _abort_session_in_subprocess(self, *, kill_before_clear: bool):
545:            terminal_head_pin_for_session(
593:                head_pin_path=self.pin,
605:            head_pin_path=self.pin,
635:        self._write_pin(head_pin_for_receipt(final))
663:        self._write_pin(head_pin_for_receipt(sibling))
679:        self._write_pin(head_pin_for_receipt(final))
697:        self._write_pin(head_pin_for_receipt(final))
730:        pin = terminal_head_pin_for_session(
785:    def test_generic_head_pin_refuses_session_open_and_pre_receipts(self) -> None:
788:            CalibrationLedgerError, "terminal_head_pin_for_session"
790:            head_pin_for_receipt(capability)
793:            CalibrationLedgerError, "terminal_head_pin_for_session"
795:            head_pin_for_receipt(pre)
820:            terminal_head_pin_for_session(
876:            terminal_head_pin_for_session(
953:        self.assertEqual(output["terminal_head_pin"], None)
1003:            terminal_head_pin_for_session(
1008:            terminal_head_pin_for_session(
1019:            head_pin_path=self.pin,
1024:            terminal_head_pin_for_session(
1035:            terminal_head_pin_for_session(
1069:            CalibrationLedgerError, "terminal_head_pin_for_session"
1071:            head_pin_for_receipt(conflicting)
1124:        script, head_pin = self._isolated_cli_checkout()
1141:            str(head_pin),
1199:        script, head_pin = self._isolated_cli_checkout()
1221:            str(head_pin),
1534:                head_pin_path=self.pin,
1574:                head_pin_path=self.pin,
1592:                head_pin_path=self.pin,
1616:                    head_pin_path=self.pin,
1638:                    head_pin_path=self.pin,
1670:                    head_pin_path=self.pin,
1687:                head_pin_path=self.pin,
1698:        self._write_pin(dict(plan.head_pin))
1702:                head_pin_path=self.pin,
1840:                    head_pin_path=self.pin,
1883:                        head_pin_path=self.pin,
1955:                head_pin_path=self.pin,
1990:    head_pin_path=Path({str(self.pin)!r}),
2006:            head_pin_path=self.pin,
2039:                    head_pin_path=self.pin,
2055:            head_pin_path=self.pin,
2062:        self._write_pin(dict(plan.head_pin))
2085:        self._write_pin(head_pin_for_receipt(final))
385:class CalibrationBracketingTests(unittest.TestCase):
859:        return CalibrationCandidate(
871:    def _bound_session_fixture(self):

exec
/bin/zsh -lc "git show origin/main:tests/test_calibration_ledger.py | sed -n '84,275p' && git show origin/main:tests/test_calibration_bracketing.py | sed -n '385,940p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
class CalibrationLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "ledger.jsonl"
        self.pin = self.root / "head.json"
        self._write_pin(
            {
                "sequence": 0,
                "head_digest": GENESIS_DIGEST,
                "ledger_schema": LEDGER_SCHEMA,
            }
        )
        self.epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self.t1 = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.t1.update(self.epoch)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_pin(self, value: dict) -> None:
        self.pin.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def _isolated_cli_checkout(self) -> tuple[Path, Path]:
        """Copy the CLI into a tiny repo with a committed genesis head pin."""

        source_root = Path(__file__).resolve().parents[1]
        repo = self.root / "cli-repo"
        shutil.copytree(source_root / "joulewise", repo / "joulewise")
        (repo / "scripts").mkdir()
        shutil.copy2(
            source_root / "scripts" / "calibration_ledger_bootstrap.py",
            repo / "scripts" / "calibration_ledger_bootstrap.py",
        )
        pin = repo / "configs" / "calibration" / "calibration_ledger_head.json"
        pin.parent.mkdir(parents=True)
        pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "tests@joulewise.invalid"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "JouleWise tests"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "add", pin.relative_to(repo).as_posix()],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-qm", "pin synthetic genesis head"],
            cwd=repo,
            check=True,
        )
        return repo / "scripts" / "calibration_ledger_bootstrap.py", pin

    def _custody(self, attempt_id: str) -> Path:
        path = self.root / "another-root" / "instrument_validation" / attempt_id
        (path / "raw").mkdir(parents=True)
        (path / "raw" / "powermetrics.plist").write_bytes(b"raw-" + attempt_id.encode())
        (path / "events.jsonl").write_text(
            '{"timestamp_s": 99.0}\n', encoding="utf-8"
        )
        (path / "instrument_evidence.json").write_text(
            json.dumps({"b_fiducial_s": 0.025, "attempt": attempt_id}) + "\n",
            encoding="utf-8",
        )
        (path / "manifest.json").write_text(
            json.dumps({"attempt": attempt_id}) + "\n", encoding="utf-8"
        )
        return path

    def _reserve(self, attempt_id: str, custody: Path):
        return append_pending_receipt(
            self.ledger,
            attempt_id=attempt_id,
            custody_locator=str(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            head_pin_path=self.pin,
            require_committed_pin=False,
        )

    def _finalize(self, attempt_id: str, custody: Path, disposition: str = "valid"):
        return finalize_attempt_receipt(
            self.ledger,
            attempt_id=attempt_id,
            disposition=disposition,
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s="0.025",
        )

    def _snapshot(self, *, verify_custody: bool = True):
        return load_calibration_ledger_snapshot(
            self.ledger,
            self.pin,
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
            require_committed_pin=False,
            verify_custody=verify_custody,
        )

    def _open_bracket_session(self, session_id: str = "session-alpha"):
        return append_bracket_session_receipt(
            self.ledger,
            session_id=session_id,
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root=self.root / "another-root",
            slots={
                "pre": {
                    "attempt_id": f"{session_id}-pre",
                    "custody_locator": str(
                        self.root
                        / "another-root"
                        / "instrument_validation"
                        / f"{session_id}-pre"
                    ),
                    "identity_epoch": self.epoch,
                    "t1_bindings": self.t1,
                },
                "post": {
                    "attempt_id": f"{session_id}-post",
                    "custody_locator": str(
                        self.root
                        / "another-root"
                        / "instrument_validation"
                        / f"{session_id}-post"
                    ),
                    "identity_epoch": self.epoch,
                    "t1_bindings": self.t1,
                },
            },
            head_pin_path=self.pin,
            require_committed_pin=False,
        )

    def _finalize_bracket_slot(self, session_id: str, slot: str):
        attempt_id = f"{session_id}-{slot}"
        custody = (
            self.root / "another-root" / "instrument_validation" / attempt_id
        )
        if not custody.exists():
            custody = self._custody(attempt_id)
        return finalize_bracket_session_slot(
            self.ledger,
            session_id=session_id,
            slot=slot,
            disposition="valid",
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=self.epoch,
            t1_bindings=self.t1,
            capture_wall_time_s="99.0" if slot == "pre" else "111.0",
            exact_bound_lexeme_s="0.025",
        )

    def _historical_custody(
        self,
        checkout: Path,
        run_name: str,
        attempt_id: str,
        token: str,
    ) -> Path:
        custody = checkout / run_name / "instrument_validation" / attempt_id
class CalibrationBracketingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bindings = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        self.bindings.update(
            {
                "hardware_model": "Mac15,9",
                "os_build": "25F84",
                "sampling_interval_ms": 100,
                "pulse_protocol_id": PROTOCOL_ID,
                "power_policy": "ac_high_power",
                "estimator_revision": RESIDUAL_REGION_METHOD,
                "protocol_sha256": PROTOCOL_V3_SHA256,
            }
        )
        self.policy = CalibrationBracketingPolicy(
            require_bracket=True,
            calibration_bracket_max_drift_s=0.010,
        )

    def test_explicit_unissued_fixture_cannot_license_claim_evaluation(self) -> None:
        snapshot, candidates = _fixture_snapshot(
            [
                self.candidate("pre", 99.0, "0.025"),
                self.candidate("post", 111.0, "0.026"),
            ]
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=1_000.0,
                window_end_s=1_100.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(
            result["acceptance"]["freshness"]["reason"],
            "acceptance_artifact_unissued_fixture",
        )

    def test_live_issued_anchor_authenticates_and_matches_committed_head_pin(
        self,
    ) -> None:
        raw = DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes()
        artifact = load_calibration_acceptance_bound()
        pin = json.loads(DEFAULT_HEAD_PIN_PATH.read_bytes())

        self.assertIsNotNone(artifact)
        self.assertEqual(artifact["artifact_role"], "issued")
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(), ISSUED_ACCEPTANCE_BOUND_SHA256
        )
        self.assertTrue(_valid_acceptance_bound(artifact))
        self.assertTrue(artifact["issuance"]["claim_eligible"])
        self.assertEqual(
            {
                key: artifact["ledger_cutoff"][key]
                for key in ("sequence", "head_digest", "ledger_schema")
            },
            pin,
        )
        self.assertEqual(pin["sequence"], 76)
        self.assertEqual(
            pin["head_digest"],
            "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
        )

    def test_issued_artifact_authenticates_and_becomes_claim_eligible(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = _synthetic_issued_snapshot(artifact)
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))
        self.assertTrue(result["acceptance"]["artifact"]["claim_eligible"])
        self.assertEqual(
            result["acceptance"]["artifact"]["artifact_role"], "issued"
        )

    def test_issued_artifact_wrong_head_digest_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = _synthetic_issued_snapshot(artifact)
        artifact["ledger_cutoff"]["head_digest"] = "f" * 64
        artifact["prior_observation_set"]["cutoff"]["head_digest"] = "f" * 64
        artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertTrue(_valid_acceptance_bound(artifact))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_missing_ledger_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=None,
            )

        self.assertEqual(reasons, ("calibration_ledger_snapshot_required",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_committed_head_mismatch_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = replace(
            _synthetic_issued_snapshot(artifact),
            refusal_reasons=("calibration_ledger_head_mismatch",),
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_ledger_head_mismatch",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_prior_set_divergence_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        snapshot = _synthetic_issued_snapshot(artifact)
        artifact["prior_observation_set"]["observations"][19]["content_id"] = (
            hashlib.sha256(b"divergent-prior-member").hexdigest()
        )
        artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertTrue(_valid_acceptance_bound(artifact))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=snapshot,
            )

        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))
        self.assertFalse(result["acceptance"]["artifact"]["claim_eligible"])

    def test_issued_artifact_stale_derivation_sha256_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        artifact["derivation_sha256"] = "0" * 64
        self.assertFalse(_valid_acceptance_bound(artifact))
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=None,
        ):
            result, reasons = _evaluate_calibration_bracket(
                (),
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=artifact["identity_epoch"],
                policy=self.policy,
                ledger_snapshot=_synthetic_issued_snapshot(
                    _synthetic_issued_artifact()
                ),
            )

        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertIsNone(result["acceptance"]["artifact"])

    def test_unknown_acceptance_artifact_role_refuses(self) -> None:
        artifact = _synthetic_issued_artifact()
        artifact["artifact_role"] = "unknown"
        artifact["derivation_sha256"] = _canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertFalse(_valid_acceptance_bound(artifact))

    @unittest.skipUnless(
        _REAL_D079_TABLE.is_file() and _REAL_D079_CUSTODY_MANIFEST.is_file(),
        "lead-reviewed D-079 import inputs are unavailable",
    )
    def test_production_path_authenticates_real_76_receipt_import_prefix(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ledger = repo / "runs" / "calibration_observation_ledger.jsonl"
            pin = repo / "configs" / "calibration" / "calibration_ledger_head.json"
            pin.parent.mkdir(parents=True)
            pin.write_text(
                json.dumps(
                    {
                        "sequence": 0,
                        "head_digest": GENESIS_DIGEST,
                        "ledger_schema": LEDGER_SCHEMA,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            plan = bootstrap_historical_import(
                ledger,
                head_pin_path=pin,
                checkout_root=Path("/Users/edr"),
                disposition_table_raw=_REAL_D079_TABLE.read_bytes(),
                expected_disposition_table_sha256=_REAL_D079_TABLE_SHA256,
                custody_manifest_raw=_REAL_D079_CUSTODY_MANIFEST.read_bytes(),
                expected_custody_manifest_sha256=(
                    _REAL_D079_CUSTODY_MANIFEST_SHA256
                ),
                execute=False,
                require_committed_pin=False,
                repo_root=repo,
            )
            source_raw = _unissued_acceptance_fixture_bytes()
            source = _unissued_acceptance_fixture()
            issued = _issued_acceptance_artifact(
                plan,
                source,
                source_artifact_raw=source_raw,
            )
            self.assertEqual(
                issued["derivation_corpus"], source["derivation_corpus"]
            )
            issued_path = repo / "issued-acceptance.json"
            issued_path.write_bytes(_issued_artifact_bytes(issued))
            loaded = load_calibration_acceptance_bound(issued_path)
            self.assertEqual(loaded, issued)

            ledger.parent.mkdir(parents=True)
            ledger.write_bytes(plan.ledger_bytes)
            pin.write_text(json.dumps(dict(plan.head_pin)) + "\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "tests@joulewise.invalid"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "JouleWise tests"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "add", pin.relative_to(repo).as_posix()],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-qm", "pin test ledger head"],
                cwd=repo,
                check=True,
            )
            snapshot = load_calibration_ledger_snapshot(
                ledger,
                pin,
                baseline_sequence=plan.final_sequence,
                baseline_digest=plan.head_digest,
                require_committed_pin=True,
                verify_custody=True,
                repo_root=repo,
            )
            self.assertEqual(snapshot.refusal_reasons, ())
            self.assertEqual(len(snapshot.observations), 38)
            self.assertTrue(all(row.is_historical_import for row in snapshot.observations))
            with patch(
                "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
                return_value=loaded,
            ):
                result, reasons = _evaluate_calibration_bracket(
                    (),
                    window_start_s=100.0,
                    window_end_s=110.0,
                    bindings=issued["identity_epoch"],
                    policy=self.policy,
                    ledger_snapshot=snapshot,
                )

        self.assertEqual(reasons, ("instrument_calibration_bracket_missing",))
        self.assertTrue(result["acceptance"]["artifact"]["claim_eligible"])
        self.assertEqual(
            result["acceptance"]["ledger_snapshot"]["baseline_sequence"], 76
        )

    def test_import_marker_is_excluded_by_discovery_and_trigger_paths(self) -> None:
        candidates = [
            self.candidate("pre", 99.0, "0.025"),
            self.candidate("post", 111.0, "0.026"),
        ]
        snapshot, registered = _fixture_snapshot(candidates)
        imported_hashes = {
            "manifest.json": "12" * 32,
            "instrument_evidence.json": "34" * 32,
        }
        imported = LedgerObservation(
            sequence=snapshot.head_sequence + 2,
            receipt_digest="56" * 32,
            attempt_id="historical-range-expander",
            content_id=content_id_from_artifact_hashes(imported_hashes),
            artifact_sha256=MappingProxyType(imported_hashes),
            identity_epoch=MappingProxyType(
                {
                    field: self.bindings[field]
                    for field in (
                        "os_build",
                        "hardware_model",
                        "power_policy",
                        "sampling_interval_ms",
                        "estimator_revision",
                        "pulse_protocol_id",
                    )
                }
            ),
            t1_bindings=MappingProxyType(
                {field: self.bindings[field] for field in V2_BINDING_FIELDS}
            ),
            capture_wall_time_s="105.0",
            exact_bound_lexeme_s="9.0",
            disposition="valid",
            custody_locator="/reviewed/historical-range-expander",
            observation_kind="historical-import",
        )
        snapshot = replace(
            snapshot,
            observations=(*snapshot.observations, imported),
            head_sequence=imported.sequence,
            head_digest=imported.receipt_digest,
        )
        by_attempt = {
            candidate.attempt_id: candidate for candidate in registered
        }
        with patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=lambda observation: by_attempt.get(observation.attempt_id),
        ) as authenticate:
            discovered = discover_calibration_candidates(snapshot)
        self.assertEqual(discovered, tuple(registered))
        self.assertNotIn(
            imported.attempt_id,
            [call.args[0].attempt_id for call in authenticate.call_args_list],
        )

        result, reasons = _evaluate_with_unissued_acceptance(
            discovered,
            window_start_s=100.0,
            window_end_s=110.0,
            bindings=self.bindings,
            policy=self.policy,
            ledger_snapshot=snapshot,
            _allow_unissued_fixture=True,
        )
        self.assertEqual(reasons, ())
        self.assertNotIn(
            "new_valid_same_identity_capture_expands_observed_range",
            result["acceptance"]["prospective_rederivation"]["observed_triggers"],
        )

    def test_acceptance_prior_set_must_equal_import_marked_cutoff_prefix(self) -> None:
        artifact = _unissued_acceptance_fixture()
        snapshot, registered = _fixture_snapshot(
            [
                self.candidate("pre", 99.0, "0.025"),
                self.candidate("post", 111.0, "0.026"),
            ]
        )
        imported = replace(
            snapshot.observations[0],
            observation_kind="historical-import",
        )
        artifact["ledger_cutoff"]["sequence"] = imported.sequence
        artifact["ledger_cutoff"]["head_digest"] = imported.receipt_digest
        snapshot = replace(
            snapshot,
            observations=(imported, *snapshot.observations[1:]),
            baseline_sequence=imported.sequence,
            baseline_digest=imported.receipt_digest,
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=artifact,
        ):
            _result, reasons = _evaluate_calibration_bracket(
                registered[1:],
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_ledger_baseline_missing",))

    def candidate(
        self,
        name: str,
        capture_s: float,
        bound_s: Decimal | str | float,
        *,
        protocol_id: str = PROTOCOL_ID,
        bindings: dict | None = None,
    ) -> CalibrationCandidate:
        corpus_alias = {
            "pre": "20260722T145535-e941c821",
            "post": "20260722T194118-9dc0749d",
            "pre-v3": "20260722T214220-1acdbbc0",
            "post-v3": "20260722T215127-eeef661a",
        }
        new_observation = name in {
            "range-expander",
            "current-pre",
            "current-post",
            "window-b-new-systematic-pre",
            "window-b-post",
        }
        manifest_sha256 = (
            hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
            if new_observation
            else "ab" * 32
        )
        evidence_sha256 = (
            hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
            if new_observation
            else "cd" * 32
        )
        return CalibrationCandidate(
            relative_path=(
                f"instrument_validation/{corpus_alias.get(name, name)}"
            ),
            manifest_sha256=manifest_sha256,
            evidence_sha256=evidence_sha256,
            protocol_id=protocol_id,
            capture_wall_time_s=capture_s,
            b_fiducial_s=bound_s,
            bindings=self.bindings if bindings is None else bindings,
        )

    def _bound_session_fixture(self):
        specifications = (
            ("neighbor-pre", 98.0, "0.025", None, None, 1),
            ("neighbor-post", 112.0, "0.026", None, None, 2),
            ("session-pre", 99.0, "0.024", "session-alpha", "pre", 4),
            ("session-post", 111.0, "0.027", "session-alpha", "post", 5),
        )
        observations = []
        candidates = []
        for name, capture, bound, session_id, slot, sequence in specifications:
            manifest = hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
            evidence = hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
            hashes = {
                "manifest.json": manifest,
                "instrument_evidence.json": evidence,
            }
            content_id = content_id_from_artifact_hashes(hashes)
            receipt_digest = hashlib.sha256(f"receipt:{name}".encode()).hexdigest()
            attempt_id = f"attempt-{name}"
            candidate = replace(
                self.candidate(name, capture, bound),
                manifest_sha256=manifest,
                evidence_sha256=evidence,
                attempt_id=attempt_id,
                content_id=content_id,
                ledger_receipt_digest=receipt_digest,
                bracket_session_id=session_id,
                bracket_slot=slot,
                bracket_window_id="window-alpha" if session_id else None,
                bracket_plan_id="plan-alpha" if session_id else None,
                bracket_plan_sha256="a" * 64 if session_id else None,
                bracket_evidence_root_id="evidence-alpha" if session_id else None,
                bracket_runs_root="/synthetic/root-alpha" if session_id else None,
            )
            candidates.append(candidate)
            observations.append(
                LedgerObservation(
                    sequence=sequence,
                    receipt_digest=receipt_digest,
                    attempt_id=attempt_id,
                    content_id=content_id,
                    artifact_sha256=MappingProxyType(hashes),
                    identity_epoch=MappingProxyType(
                        {
                            field: self.bindings[field]
                            for field in (
                                "os_build",
                                "hardware_model",
                                "power_policy",
                                "sampling_interval_ms",
                                "estimator_revision",
                                "pulse_protocol_id",
                            )
                        }
                    ),
                    t1_bindings=MappingProxyType(dict(self.bindings)),
                    capture_wall_time_s=str(capture),
                    exact_bound_lexeme_s=bound,
                    disposition="valid",
                    custody_locator=f"/synthetic/{name}",
                    observation_kind=(
                        "bracket-session-finalized" if session_id else "live-capture"
                    ),
                    bracket_session_id=session_id,
                    bracket_slot=slot,
                    bracket_window_id="window-alpha" if session_id else None,
                    bracket_plan_id="plan-alpha" if session_id else None,
                    bracket_plan_sha256="a" * 64 if session_id else None,
                    bracket_evidence_root_id="evidence-alpha" if session_id else None,
                    bracket_runs_root=(

exec
/bin/zsh -lc "git show origin/main:tests/test_calibration_bracketing.py | sed -n '940,1080p' && git show origin/main:tests/test_calibration_bracketing.py | sed -n '1,385p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
                    bracket_runs_root=(
                        "/synthetic/root-alpha" if session_id else None
                    ),
                )
            )
        by_slot = {
            observation.bracket_slot: observation
            for observation in observations
            if observation.bracket_slot is not None
        }
        capability_digest = hashlib.sha256(b"capability-alpha").hexdigest()
        session = CalibrationBracketSession(
            session_id="session-alpha",
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
            capability_receipt_digest=capability_digest,
            capability_sequence=3,
            slot_attempt_ids=MappingProxyType(
                {slot: observation.attempt_id for slot, observation in by_slot.items()}
            ),
            state="finalized",
            finalized_slots=MappingProxyType(by_slot),
        )
        receipt_digests = [
            observations[0].receipt_digest,
            observations[1].receipt_digest,
            capability_digest,
            by_slot["pre"].receipt_digest,
            by_slot["post"].receipt_digest,
        ]
        snapshot = CalibrationLedgerSnapshot(
            ledger_schema=LEDGER_SCHEMA,
            ledger_path=Path("synthetic-session-ledger.jsonl"),
            head_sequence=5,
            head_digest=by_slot["post"].receipt_digest,
            receipts=tuple(
                MappingProxyType({"receipt_digest": digest})
                for digest in receipt_digests
            ),
            observations=tuple(sorted(observations, key=lambda item: item.sequence)),
            refusal_reasons=(),
            bracket_sessions=(session,),
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
        )
        binding = build_calibration_bracket_binding(
            snapshot,
            session_id="session-alpha",
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
        )
        return snapshot, candidates, binding

    def test_exact_session_binding_selects_reserved_pair_not_neighbors(self) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        resolved = validate_calibration_bracket_binding(
            binding,
            snapshot,
            window_id="window-alpha",
            plan_id="plan-alpha",
            plan_sha256="a" * 64,
            evidence_root_id="evidence-alpha",
            runs_root="/synthetic/root-alpha",
        )
        self.assertIsNotNone(resolved)
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-alpha",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ())
        self.assertEqual(result["pre"]["attempt_id"], "attempt-session-pre")
        self.assertEqual(result["post"]["attempt_id"], "attempt-session-post")
        self.assertEqual(
            result["bracket_binding"]["binding_digest"],
            binding["binding_digest"],
        )

    def test_l5_later_same_t1_calibration_from_another_runs_root_cannot_be_borrowed(
        self,
    ) -> None:
        snapshot, candidates, binding = self._bound_session_fixture()
        later_other_root = replace(
            candidates[-1],
            relative_path="/synthetic/root-beta/instrument_validation/later-post",
            bracket_runs_root="/synthetic/root-beta",
        )
        supplied = [*candidates[:-1], later_other_root]
        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                supplied,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
                bracket_window_id="window-alpha",
                bracket_plan_id="plan-alpha",
                bracket_plan_sha256="a" * 64,
                bracket_evidence_root_id="evidence-alpha",
                bracket_runs_root="/synthetic/root-alpha",
                _allow_unissued_fixture=True,
            )
        self.assertEqual(reasons, ("calibration_ledger_off_ledger_artifact",))

        with patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ):
            _result, reasons = _evaluate_calibration_bracket(
                candidates,
                window_start_s=100.0,
                window_end_s=110.0,
                bindings=self.bindings,
                policy=self.policy,
                ledger_snapshot=snapshot,
                bracket_binding=binding,
"""Defect-shaped regressions for claim-bearing calibration bracketing."""

from __future__ import annotations

import base64
import hashlib
import json
import math
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import subprocess
import tempfile
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

from joulewise.calibration_bracketing import (
    ACCEPTANCE_BOUND_SCHEMA,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    ISSUED_ACCEPTANCE_BOUND_SHA256,
    CalibrationCandidate,
    _canonical_sha256,
    _valid_acceptance_bound,
    build_calibration_bracket_binding,
    calibration_bracket_for_bundles,
    discover_calibration_candidates,
    evaluate_calibration_bracket as _evaluate_calibration_bracket,
    load_calibration_acceptance_bound,
    load_calibration_candidate,
    validate_calibration_bracket_binding,
)
from joulewise.calibration_ledger import (
    DEFAULT_HEAD_PIN_PATH,
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    CalibrationBracketSession,
    LedgerObservation,
    bootstrap_historical_import,
    content_id_from_artifact_hashes,
    load_calibration_ledger_snapshot,
)
from joulewise.powermetrics_fiducial import (
    MAX_AGE_S,
    PROTOCOL_ID,
    PROTOCOL_V2_ID,
    PROTOCOL_V3_SHA256,
    PULSE_COUNT,
    REGION_COVERAGE_RESOLUTION_S,
    RESIDUAL_REGION_METHOD,
    V2_BINDING_FIELDS,
)
from joulewise.schemas import CalibrationBracketingPolicy
from scripts.calibration_ledger_bootstrap import (
    _issued_acceptance_artifact,
    _issued_artifact_bytes,
)


_REAL_D079_TABLE = Path("/private/tmp/d079-ledger-dispositions.json")
_REAL_D079_CUSTODY_MANIFEST = Path(
    "/private/tmp/d079-custody-manifest.lead.json"
)
_REAL_D079_TABLE_SHA256 = (
    "5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a"
)
_REAL_D079_CUSTODY_MANIFEST_SHA256 = (
    "99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078"
)
_UNISSUED_ACCEPTANCE_FIXTURE_SHA256 = (
    "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
)
_UNISSUED_ACCEPTANCE_FIXTURE_B85 = b"""
c-qZd*={3Ac75-!AoSD?7pr4m#!oh827a(-fI-_YMk8?};zlXExoDWAstb+!cc0)+i4;Y(3UC2cDv_BPH}1L1Igt^+e>WQ44f&p@
)IIWI=;yP$KaK8wnXe}NxgYprrb(X`w8R%3<;)LDnq}_Nd^IZ{AJxa&|F&E$_~WCz`_P_sbWLB{ql)mcyYQ4p)y-tw+*mmGZFt-
^;J*LGXZZBbV=2`7g6%Ky4*&moGt^?)SIWz7F`sZ7YCDguN!@DJ55tPf=K1aaZBShJ`{r@Ol9sDB*4=8>Y^yz&-
Oalp^Mv|o$CLh3pVos^nhd=Ca=|og{I#}h^ba+{^{atLezf3!uKEQJqX|<P!L@jNUOQkkucHNh9zEQD8TveoXjVq|G~DCb#C5*l(
Zgb1R(XBx-
fE2abv=&>mruOt@@hG+^=L8}k2lj3Tl4NQa##9KJS>}y;t&4Wxnyg=#@UyHWu69JJZ}EKxn&n4&2wACc2Ird84vx?&F0IFy2Jdt-
TZg+-
MgVLJX`k5FC9P3^ZmgO^Px+tezFcdW&aw?ZpeFDl+T2*rt`v+_Vs^Jmi9y3UGOmfjA=d0Cw>0XzNXyW_n+>&_2;{b2AV!h`q`(hp
Do+;Cf&3}kQ6(o!`c0mmh(lo;K%-
uPq@CD%!i>HRtTg=o*bS4kInKul3{Pj3NhBau$<@lWSd88Gp4*;AZEJF6}5+(dOYD#9~^_*h6jfC9vLPS1l|UOgNuL?&k8L%{_UY
(w7Je!lgV~$JpWUJ_ZYs#YJ=7<E5L}fD$P%e9&_BM;0#kjOz@<_s^#73!w&g;3>?yJQo4LkvroHp+nB$ZHJ*O(W%{z@XP3_Sa|i$
Rr2{Ih+-x75>0upIm>zO#*iHqxy*Rx;&leA?p)2!-$k5freA>y_E$5vMr=tvCh9!c1+2^iOKWPt#F%!5E$pu$%MS-
|qA}1Eiv%B@JKkvZYO=!3$WnJ@QWU5isV5N4fw8_>n=~|06Ix6xyYpIJN5mlyCwFuQ#OH^wlEz>@W4*toA>B9iO?`+>^=8q@Qvx}
RL59>fzlC$*LCnaTM8@*(ga@Da!6=jLSm!yrS<cOS((Iu%VXr~1m?MWYebr^4joLwvlF^&v<Y|v!h4(Gj*s>o<kGCKQOv-
Vm?silpQrIKD~FH6wH31cGXR3vE*KIRxg_UDG90?ZL;C-dBmr-
NXoU@I4utrXf&E~$E%3X$<9hmwu3x@JW(1xLYTVUrfH(Puh09ujM{pOBR@1QSc4SaQ-XnX0p`<XjcfJMXf~M#7~=IHgF{0@qnpwU
p90X*comb)Uh9ob5ItdR*lvoVVG0w~qbMF22T(dbExFeIr@k^N4@TlU3m|`rOaT{PXzVN9#1kjnpqb;A^DsXqP*qO*P%dR~tpf?J
rZFrqfj3h1vegZKYB|IpLN1Ng8Xl9dk4?2POB8Y!jKU7O3h4Eixm3*M3~AW<$5J5=~(Dlpp)quw1OBFmRLYYtQ`nnnBW`Lay7q_$
UBshyih>oYhL1<IATs>nn2VC{r29S+a}~aT2vNrIu`UOd9!Xh-
;3~S6?|7CbC5rFPu;T!4()u;*TGHG>=_I9E~JRAfF7v#&TuExkL8Zj5NzBW{KQz$P|gxiB43fOhA&BfCx&Olc&4wKwm$+8Xb5{hB
0DRctr0_=&0Ajb9t0A@F--4aB#IU0<Mkj3O*uORY+1vqKHzI(I{d@rQ&=+t#Va4jLXa@HZ`%VJ_4HTz4S&2BVUhC@=mkGbA?vc7S
Ab3cpr)Ga?XW96d|Qp5L=OwQQ(8xYGJAsl~CMo$EQt1iLq?ODrIpKKKj-
8yfDhS^wClY6fGT$cHXON>BDfgq~O^SfT=bMqu2l_bd-
={LN8E&g)<R(6lmm*sAxqNRnn##;L#}XH5ym6RjROYNl1#KsF;Lts!EOY638)%u2iiPWgo4G1#>}<p|`+erSfCMR&`F&P4Ji-
;JG-;x%5%!twMP1g*6WIzJgB#x$vPT6tfgvt|16%6MR?$S~97|HWWN&g9k0~0r>-
J;ziBYvLO3<e1x;eyr|l}<SL<R$1G&7K2eZPYYqAlax2LRq`*qlQ~Y0M@(2mk>D%#9N^3Qa7{q3&zZE{0M>(557Ou1o6)r^lxt2c
F8&1VmL10THtPc*&2x;O%VqJ@m-WpX(EIu>HQ7JxITV-+_vNf-Vhmkls6f2ypqDo~$F+SCdZYFAy)!0DJgGWVcfQC>49MF-
bY*P)D-vAHFsEFgBoKaT#o8YlKc=T0xE{}39eZ0f;&{85Ox6#2~!N-E`kut2k7pN@)q!s<EWc-HWg655W!J<?^q_lSqT$5{H4>zW
YA2;CB61zexlw5Id^s0g+qZ>g$WFJan(5T;jTmOU(G9(lM3S^8a{#JbSPeOsChB4{@xO$G?1fLg2Ifsw&R%?Sa5)xHW`78Kjw0#|
%BT%VIBC#X3S(N~`R#0UOG!@%gtXD}Tsj5<$UDF}nqs*1p<Ku!ua#-jV78!!rK)|s9{f~iFq!MB>-
d6|CX1pjaK;J1So*EjHl=%(#SS73+7qE<w1AQxeE{}2!ACT0>4O~R4z~8Ivtu{B*fcB$^grf{!v<wL%M||1RsB$Hc>D(l-
jJAT~Q}Jl)EYuD7fD#6d4mGW~3PC10;Ag1WC=YQIBjO<=tia@Ta-gBsOCd!Ho(#VQ9~ls(Zfp=xQ6+N|KJL}{yfDhy`lg(cPJ|Gw
u}WUcpF~wwR2rnF^2D*CvXM42X#i~rZ34_GS_%H^!Pbj&s+eG0ChG#ld`tdBV_l(S8OewYw52B0OrwFBG>s3U<$&R#>?znG)tcc$
jyWJ#${X+jSw!P5!Z4~Oe=B@0k8-xYStuW;W0Oi2C|$z`@Y@XXB%M@HI_zb#35-
g5lssEdBV}X|2lQ)*l~}=w!KYC5(5evXug9lqBqk<MMJQ;E)~@vqCWYj2HZhY)Y;-
ooO6%Detw8lt(?n53a&N)MdM(B&gZM~uTYd94;B#@5v-
Pd5+u&9OGGUFmh7S}7qm?)S5gd3@($!bZLZ%3zN{o`Eye+1*UM5*tj*_5>G;>ly+(56r%&5FoXDBP3qZ1_taJhsb@o>;hVnRvN(L
<xceu7p-gR+j3Y0C$<<D(!PO&l|x>>&oe5k4=Ba<;yCU=)H15`;q7Yy1re7A;WB5Cs`R$Q1<^=SrwLlCd6-
gO)GJzzB41TU7*G0o}%ptYy4Gp5mDSxtFpIkU-jiz>z5#WFaU{&Vm#A&?+88a<Zy1hc!>srsk^XE%<;axv`d}x)N{0C)|L~#Zk_#
?f@5OCDc+|Jh1u-
KBei=9I{9`%Vbo{ma`Jj!qnOj3+NRnNE4xZBjkt?kyUm%8Bj1^`38QiV~v`?)RbZ&gl_A7##f;rZoo)@kBU)>j8+IDE~G}KgDyp$
niPb-6(94HkWlJz3`vJ#Y1KEu=fzRZ);Dxo2d&o@;iS4IPfacYj&?#biAE1m&8mT-
N4jcCRRADDLN!HI(FW0y+WI$(CThvu0uO^Rm*~Mq94IsDXF)JjYpT)CMeq&C(U2OavCv}~V4)f!RRudn$lVH${R!1qqHz;6o0RD`
c^Y@{n3v&sag=lLXl0}g63SGy8?MpotWfX0Z9Li{Uz~)*uNjiG_=KtlMXYOyNk&K>@L-
DwY44mYR0%pszM;I~K2%+*$;;wEn}ZV;dNeo%Di9JHkw!U1rs!5nvjjL1It-
dvmMRm!0Us$L1;+w}F?*lC6+V|oIfqXO5ljq)Lj<UOeXae-Bv5zOpvd-iPg@<qs>y<CgV~u>3{_~6nuP}wW=P8H6=EH7B|y*KK(7
I`PG~zIXRR*=bTVbZouh}*Nm-E%R|E21BifJmV5|5SstElG+4Tl|P?Dt@3&;bsF#E0Wxjf1_d?G}tLasqm;D@+I-
?Gku+Y$jpddi>&wggBNG8&i}i@!qU_AWCS!JvguA~84zX%z|pyn()fQ(KT{(2<f2>Zg<$%vk^x*_Pj2B+Rd9DxmS0td}ksNT#Y#)
3q)127JI|5!ppo;T_+Gj}$wA>{Wm+4|7)k1P_c*!y#u-
wy!N;SFm0P4+X*t85Gc<+pi3_L6?GO*!IE);T@Vh@#G828iaqVxvb6Ua>ljwH?$qD2@0qtN0?PEwup$j1|h6;a)CvAu@RwxjTN4w
%d)J4q|t;o0OZhu{W$t;b0YW60J=QPS%M%SQ6bee*f=8a8i9+!qy&e9JS$3u92IVBI2MWoDX3j>s%<S`>w-
gX4<3cHX?}7pd2z!6HmI4FfTfD2qBF*+x<C#?UX@fE88A=<QhHw~6jV};E1VXAL9{EWJwThi8%Mio+BTQt%`gKmkG9gB?!r2|59^
!l#QLLqvA#Qs$h$nBEt_xmyJ)7oyq~XQa^vOiGtK6+9*^yQ8RoO^e?J4r$M(&KT_CJ~`#NfScSf6M3_tv^-@DQ_8g!YKG?{-
ocHnxy;OVBW7dLjjYIE1CH+a2jlh=D~^!g*4y$-
>;L+}XXlU*7|&~8{E88j_s?`u(63Ia=n$TFx01$qkXx+;hIi8>caQISZ=l0h0}Va4$14!ooNo!f0A_^lrv=0kt7MWuaC%Oy`Ame+
QO9O~l}tI@m(R;RX%mN^7ubFHZ5(C^R{qT-
2yQNjf17nltB_9{!)idq9Y%ly7pKiSi8(P}6(l`Fw<5kf>pQ0#)P9?=VBFw9EBHbc@El~B8ydIC7Lt>rY4S>M&_r*HZ%TU|Vd7^D
yEn~*k8URqPz`k*C94)~1^mQr$Fk}9UHSEA>D@t9a`d+qqHR-
e8Azi2fG14CrG6sRpkrU<8&XtdAF!DuB+2qjxc`CN4>;OAi3E?W)30-
gWPzJBsr_@dQTM1?E_qnE0pS3ywwCL%aMxN;Ic3+S`zp!+OA1_&zzDNsb?3Vfa4*Xk#4OD|_*V^jj!=CV^!fR|dd>=;M{p+SRE&E
N@A2`yE7c?{j^BI_Uuv<_nG9j$);4)LPZOt7|EMv{34H&#S&2}&W3JqWx7FC<3!z*m-
A;Zs>45pqq?Owg(CYxR>iYZt9<n_)uns=YtXt?FrHFDf8Ya%_aNus1aZTvav3!&nr`QW5QyDAw|>RzH2;bU8v=rpc&dB8Vvb^cqn
Sj5CaohS*_~WFbKwu>>va6d^hgB|;c>CBCoKPu{{@t|5dl@S55Sc8<C2^Fzmh8$+=uC(a_ylMPXTwOUSX;TSp^1zu!{E5kcmefn<
VqSZ!*(zbn&)1{zFBx1=askV7H;8~EBRa<yBMFTYp3?O6?bqK+>7dOAF)lXOKFIo+Lo=nQxXfVUv+-
?Zno6yKZgbtP#lR`ig=Tj@E)?sdKEhMruC^GMC_31kHMXR+XMt6ov_mC~YIvImvB(Rr|nTjQ$uiL!dBgoD%`g|fQjkK6s$@(3we!
jYU(dtxvR?@e%^I8dV2LYR`Mw2N?u=AiL6=pNlOy0-R-
WQ?t39oagKE0>a&lf!}S}jFok!nSWMvGJsoK<C{LyKOHH35cHyao+3goJIay}c-gRtH%WoZr{#Crg2s;~Ejf2xAl5Qnf+h6T(-
WwY5oSRSL+5_8h&C2~{cK!YE9YZ2_yjdw5@~pDd7F<{`2wQ_;_}1s5TUKCP`WAgCs_r6>eQ+d9L6QMnoQC`9M+HwZuygLz-
8pR5{Pv>Lr7W)wEzDgv0G2oNJuRsa-
{e`H)xMcdL&G+;hKWpJzLJ!({>^$PcUTK!}x<)ye@@1=~WkisCqAtJo<nGAST+hd7zR4F5hQCdn{qBqJ|L&kyvpbFk(b%KyB<NNu
f%va0j)^87BjeniZKhO4;JzWJs6aTgLlL_?tth6<xYp3Y;*LCyR<jejr-Tu>l_6UD$)~<fvdiGBvtv<AMp53qR>){B^v-
4nSGS9zqyKK2w9S-EJ58ajS_`F>+tsTM}V}@MX(Yx{S(YxIdrg1xicXCkgU-A8y5oX21eDa7}H!F3c_0YrNXx{E<*y@270~ZY6m-
W26we!3635?;1EZ@bA`>Czy=r}e}f=<+<(=>-GK%<o!v&gJ<-
LA&}d~{wU_fwj5=gxY~R#SYMyMd=PTVl@ZfZ5)#T}YhpZ#?B;Kab6)4cC6y-m+hvnf9}Ox|+UX$MOEs+qO^NP3gCj5iahT-Cudz{
@=UxDX{(HrGU^y0_ydCeXEX6eodKX?QqwCP~EQmoi0fsP*=Qvw;dtP^!kmP23bGZyFQ_`S(RF}W3vd5<EI{9xc<JaJnfF${p0Wd{
kK1N|M74C`Pc3*|MQo>jh6G#KM{4y)pUeGpZ<}f;n_;_W;F{FF0Y=8Q0PvWf_7Gm_QL4@&0H{6={J=i+HU!I-
WBBY9!wFSU2TB&L1h*GXoK6yo$>jd(5g{O=R_1XYOv$e)zK5rtz9)dTeIB6l~mosgfb5=Iru2(&bszwxOFAj9E{EL=>sj=qT{<b`
q;%M)7?GsB=hIx+`|tZo}>KH`q*h&pkMI*IOK^NHr3_03LVPU$7iMI<1Sf`rn{ZW0rWPL;|tcFK1uMCH+{R3xI2S<u=~ip=OS-
=$aAx(`wnwERJtp(I{<chnnz_a3i0Ooo`%7$o$qfsiTYERFF5>y<F47=ihGyZLB%DdNjuAnlo}3RLGQ39>H4fI9Nk>d)0Z!#`u<*
;Oy-~0^kSDvc-r^-
^TXTce0VzXAI>I0%b}C!z!Tl^OSKQ+Y0HyOe)yN;w>F#M4mKU)<gRtRvd;O8VcJV2dHE3O(KfUU`mU48K|*~wlt~o%3{}$JY|Eww
xssE@c(^y)B&{zRG*l=P+v(Q3@4kNbfA+zM4g
"""


def _unissued_acceptance_fixture_bytes() -> bytes:
    """Return the exact pre-issuance fixture bytes, independent of repo state."""

    encoded = b"".join(_UNISSUED_ACCEPTANCE_FIXTURE_B85.split())
    raw = zlib.decompress(base64.b85decode(encoded))
    assert hashlib.sha256(raw).hexdigest() == _UNISSUED_ACCEPTANCE_FIXTURE_SHA256
    return raw


def _unissued_acceptance_fixture() -> dict:
    artifact = json.loads(_unissued_acceptance_fixture_bytes())
    assert _valid_acceptance_bound(artifact)
    return artifact


def _synthetic_issued_artifact() -> dict:
    """Return a schema-valid issued artifact for isolated consumer tests."""

    artifact = _unissued_acceptance_fixture()
    prior = artifact["prior_observation_set"]
    observations = [
        row for row in prior["observations"] if row["disposition"] == "valid"
    ]
    assert len(observations) == 19
    additions = (
        ("valid", 11),
        ("systematic-invalid", 2),
        ("ordinary-invalid", 6),
    )
    for disposition, count in additions:
        for index in range(count):
            token = f"synthetic-issued-{disposition}-{index}"
            observations.append(
                {
                    "content_id": hashlib.sha256(token.encode()).hexdigest(),
                    "epoch_id": "d079_epoch",
                    "disposition": disposition,
                    "attempt_id": token,
                }
            )
    head_digest = hashlib.sha256(b"synthetic-issued-head").hexdigest()
    artifact["schema_version"] = ACCEPTANCE_BOUND_SCHEMA
    artifact["artifact_role"] = "issued"
    artifact["issuance"] = {
        "status": "issued",
        "claim_eligible": True,
        "reason": "synthetic issued-artifact consumer regression",
    }
    artifact["ledger_cutoff"] = {
        "sequence": 76,
        "head_digest": head_digest,
        "ledger_schema": LEDGER_SCHEMA,
        "role": "issued_acceptance_baseline",
    }
    prior["cutoff"] = {
        key: artifact["ledger_cutoff"][key]
        for key in ("sequence", "head_digest", "ledger_schema")
    }
    prior["observations"] = observations
    artifact["backfill_candidate"].update(
        {
            "status": "issued",
            "candidate_inventory": {
                "ordinary-invalid": 6,
                "systematic-invalid": 2,
                "valid": 30,
            },
            "production_issuance_blocked": False,
            "required_verification": "complete: synthetic consumer regression",
        }
    )
    artifact["derivation_sha256"] = _canonical_sha256(
        {
            key: value
            for key, value in artifact.items()
            if key != "derivation_sha256"
        }
    )
    assert _valid_acceptance_bound(artifact)
    return artifact


def _synthetic_issued_snapshot(
    artifact: dict,
) -> CalibrationLedgerSnapshot:
    epoch = artifact["prior_observation_set"]["epoch_catalog"]["d079_epoch"]
    observations = tuple(
        LedgerObservation(
            sequence=2 * index,
            receipt_digest=hashlib.sha256(
                f"issued-receipt-{index}".encode()
            ).hexdigest(),
            attempt_id=row["attempt_id"],
            content_id=row["content_id"],
            artifact_sha256=MappingProxyType({}),
            identity_epoch=MappingProxyType(dict(epoch)),
            t1_bindings=MappingProxyType({field: None for field in V2_BINDING_FIELDS}),
            capture_wall_time_s="1.0",
            exact_bound_lexeme_s="0.025",
            disposition=row["disposition"],
            custody_locator=f"/synthetic-issued/{row['attempt_id']}",
            observation_kind="historical-import",
        )
        for index, row in enumerate(
            artifact["prior_observation_set"]["observations"], start=1
        )
    )
    cutoff = artifact["ledger_cutoff"]
    return CalibrationLedgerSnapshot(
        ledger_schema=LEDGER_SCHEMA,
        ledger_path=Path("synthetic-issued-ledger.jsonl"),
        head_sequence=cutoff["sequence"],
        head_digest=cutoff["head_digest"],
        receipts=(),
        observations=observations,
        refusal_reasons=(),
        baseline_sequence=cutoff["sequence"],
        baseline_digest=cutoff["head_digest"],
    )


def _fixture_snapshot(
    candidates: list[CalibrationCandidate],
    *,
    extra_observations: tuple[LedgerObservation, ...] = (),
) -> tuple[CalibrationLedgerSnapshot, list[CalibrationCandidate]]:
    """Build an explicitly synthetic authenticated snapshot for unit tests."""

    normalized: list[CalibrationCandidate] = []
    observations: list[LedgerObservation] = []
    for index, candidate in enumerate(candidates):
        attempt_id = candidate.attempt_id or f"fixture-attempt-{index}-{candidate.relative_path}"
        hashes = {
            "manifest.json": candidate.manifest_sha256,
            "instrument_evidence.json": candidate.evidence_sha256,
        }
        content_id = candidate.content_id or content_id_from_artifact_hashes(hashes)
        assert content_id is not None
        digest = candidate.ledger_receipt_digest or hashlib.sha256(
            attempt_id.encode("utf-8")
        ).hexdigest()
        bound = str(candidate.b_fiducial_s)
        normalized_candidate = replace(
            candidate,
            attempt_id=attempt_id,
            content_id=content_id,
            ledger_receipt_digest=digest,
        )
        normalized.append(normalized_candidate)
        observations.append(
            LedgerObservation(
                sequence=index + 2,
                receipt_digest=digest,
                attempt_id=attempt_id,
                content_id=content_id,
                artifact_sha256=MappingProxyType(hashes),
                identity_epoch=MappingProxyType(
                    {
                        field: candidate.bindings.get(field)
                        for field in (
                            "os_build",
                            "hardware_model",
                            "power_policy",
                            "sampling_interval_ms",
                            "estimator_revision",
                            "pulse_protocol_id",
                        )
                    }
                ),
                t1_bindings=MappingProxyType(
                    {field: candidate.bindings.get(field) for field in V2_BINDING_FIELDS}
                ),
                capture_wall_time_s=str(candidate.capture_wall_time_s),
                exact_bound_lexeme_s=bound,
                disposition="valid",
                custody_locator=candidate.relative_path,
            )
        )
    all_observations = (*observations, *extra_observations)
    return (
        CalibrationLedgerSnapshot(
            ledger_schema=LEDGER_SCHEMA,
            ledger_path=Path("fixture-ledger.jsonl"),
            head_sequence=len(all_observations) * 2,
            head_digest=(
                all_observations[-1].receipt_digest
                if all_observations
                else GENESIS_DIGEST
            ),
            receipts=(),
            observations=tuple(all_observations),
            refusal_reasons=(),
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
        ),
        normalized,
    )


def _evaluate_with_unissued_acceptance(
    candidates: list[CalibrationCandidate] | tuple[CalibrationCandidate, ...],
    **kwargs: object,
) -> tuple[dict, tuple[str, ...]]:
    """Evaluate against the exact genesis fixture, never the live anchor."""

    with patch(
        "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
        return_value=_unissued_acceptance_fixture(),
    ):
        return _evaluate_calibration_bracket(candidates, **kwargs)


def evaluate_calibration_bracket(
    candidates: list[CalibrationCandidate], **kwargs: object
) -> tuple[dict, tuple[str, ...]]:
    snapshot, normalized = _fixture_snapshot(list(candidates))
    return _evaluate_with_unissued_acceptance(
        normalized,
        ledger_snapshot=snapshot,
        _allow_unissued_fixture=True,
        **kwargs,
    )


class CalibrationBracketingTests(unittest.TestCase):

exec
/bin/zsh -lc "rg -n 'schema_fixture_unissued|joulewise.calibration_acceptance_bound.v' configs tests/fixtures docs | head -80 && find configs tests/fixtures -iname '*acceptance*' -o -iname '*calibration*bound*' | head -80" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:409:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:2705:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:1528:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:2676:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:520:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:701:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:1200:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:5512:docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:72:{"parentUuid":"c551196e-7b86-4e8f-8e18-4e49908276bc","isSidechain":true,"promptId":"70846291-da47-443c-8a9a-b0e660a3b23b","agentId":"a46e6644985dd75fd","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_01UKuUzVnpqsccysDfmcK5Pk","type":"tool_result","content":"=== impl worktree loader: issued path ===\n175:    role = value.get(\"artifact_role\")\n176:    if role == \"schema_fixture_unissued\":\n180:            and issuance.get(\"status\") == \"unratified_fixture\"\n181:            and issuance.get(\"claim_eligible\") is False\n189:            and backfill.get(\"production_issuance_blocked\") is True\n198:    elif role == \"issued\":\n202:            and issuance.get(\"status\") == \"issued\"\n203:            and issuance.get(\"claim_eligible\") is True\n210:            and cutoff.get(\"role\") == \"issued_acceptance_baseline\"\n212:            and backfill.get(\"status\") == \"issued\"\n213:            and backfill.get(\"production_issuance_blocked\") is False\n224:        or value.get(\"acceptance_id\") != \"d079_calibration_acceptance_v2_n19\"\n226:        or value.get(\"derivation_sha256\") != _canonical_sha256(core)\n323:    if role == \"issued\":\n454:    # deterministically emitted issued artifact. A caller cannot turn an\n457:        \"schema_fixture_unissued\": DEFAULT_ACCEPTANCE_BOUND_SHA256,\n458:        \"issued\": ISSUED_ACCEPTANCE_BOUND_SHA256,\n459:    }.get(value.get(\"artifact_role\") if isinstance(value, Mapping) else None)\n483:        if artifact.get(\"artifact_role\") == \"issued\"\n750:    if not prefix and artifact.get(\"artifact_role\") == \"schema_fixture_unissued\":\n793:    _allow_unissued_fixture: bool = False,\n841:    artifact_role = artifact[\"artifact_role\"]\n843:    if artifact_role == \"schema_fixture_unissued\" and not _allow_unissued_fixture:\n847:                \"acceptance_id\": artifact[\"acceptance_id\"],\n850:                \"artifact_role\": artifact_role,\n851:                \"claim_eligible\": False,\n855:                \"reason\": \"acceptance_artifact_unissued_fixture\",\n863:            \"acceptance_id\": artifact[\"acceptance_id\"],\n866:                \"checked_in_issued_artifact_byte_sha256_pin\"\n867:                if artifact_role == \"issued\"\n870:            \"artifact_role\": artifact_role,\n871:            \"claim_eligible\": False,\n886:        or artifact_role == \"issued\"\n902:            \"acceptance_bound_id\": artifact[\"acceptance_id\"],\n922:            \"acceptance_id\": artifact[\"acceptance_id\"],\n925:                \"checked_in_issued_artifact_byte_sha256_pin\"\n926:                if artifact_role == \"issued\"\n929:            \"artifact_role\": artifact_role,\n930:            \"claim_eligible\": artifact_role == \"issued\",\n1262:    _allow_unissued_fixture: bool = False,\n1274:            _allow_unissued_fixture=_allow_unissued_fixture,\n1298:            _allow_unissued_fixture=_allow_unissued_fixture,\n1313:            _allow_unissued_fixture=_allow_unissued_fixture,\n1333:                _allow_unissued_fixture=_allow_unissued_fixture,\n1343:        _allow_unissued_fixture=_allow_unissued_fixture,\n\n=== is impl/issuance-consumer merged into main? ===\n+ impl/issuance-consumer\n--- git log main for issuance-consumer merge ---\n665fd58 coldgate: D-079 issuance HELD (split verdict, Sol contract-lens caught unloadable-artifact + digest blockers); issuance re-scoped as consumer implementation; syllabus anchor recorded\n63f43a6 fix(ledger): audit closures F1-F5 — reviewed-data custody manifest, consumer-enforced import marker, bound table identity, execute-time reauthentication, mutant-killing regressions\n5f5f2b3 feat(ledger): deterministic authenticated genesis-only historical-import bootstrap (D-079 issuance prep, B2 closure)\n18aba3c RUN_STATE: Ed directive batch — effort cap lifted, fast-tier spec in flight, D-113 ruled (c), overnight issuance authorized\n41deedb docs(bridge): land the t3-doctrine gate amendments in contract §4/§6/§7/§8 + consumer skills (T3-AMEND-01 draft round)\n5f8b4b8 D-100 repair fix round 1: mechanical custody universe (runs root required), content-aware zero-byte sweep, closed-inventory b-ii classification, explicit dispatch at every claim consumer, membership-to-row binding; ruled falsifier regressions\n20f0007 Checkpoint 2026-08-01: metrology window B collected + salvage-closed; both window verdicts FAILED as-issued (distinct machinery questions -> desk adjudication); bird-SIGSTOP protocol validated; streaming-during-idle-gate hazard recorded","is_error":false}]},"uuid":"a86ed91d-7142-481a-bf43-3f33d54af429","timestamp":"2026-08-06T10:46:47.965Z","toolUseResult":{"stdout":"=== impl worktree loader: issued path ===\n175:    role = value.get(\"artifact_role\")\n176:    if role == \"schema_fixture_unissued\":\n180:            and issuance.get(\"status\") == \"unratified_fixture\"\n181:            and issuance.get(\"claim_eligible\") is False\n189:            and backfill.get(\"production_issuance_blocked\") is True\n198:    elif role == \"issued\":\n202:            and issuance.get(\"status\") == \"issued\"\n203:            and issuance.get(\"claim_eligible\") is True\n210:            and cutoff.get(\"role\") == \"issued_acceptance_baseline\"\n212:            and backfill.get(\"status\") == \"issued\"\n213:            and backfill.get(\"production_issuance_blocked\") is False\n224:        or value.get(\"acceptance_id\") != \"d079_calibration_acceptance_v2_n19\"\n226:        or value.get(\"derivation_sha256\") != _canonical_sha256(core)\n323:    if role == \"issued\":\n454:    # deterministically emitted issued artifact. A caller cannot turn an\n457:        \"schema_fixture_unissued\": DEFAULT_ACCEPTANCE_BOUND_SHA256,\n458:        \"issued\": ISSUED_ACCEPTANCE_BOUND_SHA256,\n459:    }.get(value.get(\"artifact_role\") if isinstance(value, Mapping) else None)\n483:        if artifact.get(\"artifact_role\") == \"issued\"\n750:    if not prefix and artifact.get(\"artifact_role\") == \"schema_fixture_unissued\":\n793:    _allow_unissued_fixture: bool = False,\n841:    artifact_role = artifact[\"artifact_role\"]\n843:    if artifact_role == \"schema_fixture_unissued\" and not _allow_unissued_fixture:\n847:                \"acceptance_id\": artifact[\"acceptance_id\"],\n850:                \"artifact_role\": artifact_role,\n851:                \"claim_eligible\": False,\n855:                \"reason\": \"acceptance_artifact_unissued_fixture\",\n863:            \"acceptance_id\": artifact[\"acceptance_id\"],\n866:                \"checked_in_issued_artifact_byte_sha256_pin\"\n867:                if artifact_role == \"issued\"\n870:            \"artifact_role\": artifact_role,\n871:            \"claim_eligible\": False,\n886:        or artifact_role == \"issued\"\n902:            \"acceptance_bound_id\": artifact[\"acceptance_id\"],\n922:            \"acceptance_id\": artifact[\"acceptance_id\"],\n925:                \"checked_in_issued_artifact_byte_sha256_pin\"\n926:                if artifact_role == \"issued\"\n929:            \"artifact_role\": artifact_role,\n930:            \"claim_eligible\": artifact_role == \"issued\",\n1262:    _allow_unissued_fixture: bool = False,\n1274:            _allow_unissued_fixture=_allow_unissued_fixture,\n1298:            _allow_unissued_fixture=_allow_unissued_fixture,\n1313:            _allow_unissued_fixture=_allow_unissued_fixture,\n1333:                _allow_unissued_fixture=_allow_unissued_fixture,\n1343:        _allow_unissued_fixture=_allow_unissued_fixture,\n\n=== is impl/issuance-consumer merged into main? ===\n+ impl/issuance-consumer\n--- git log main for issuance-consumer merge ---\n665fd58 coldgate: D-079 issuance HELD (split verdict, Sol contract-lens caught unloadable-artifact + digest blockers); issuance re-scoped as consumer implementation; syllabus anchor recorded\n63f43a6 fix(ledger): audit closures F1-F5 — reviewed-data custody manifest, consumer-enforced import marker, bound table identity, execute-time reauthentication, mutant-killing regressions\n5f5f2b3 feat(ledger): deterministic authenticated genesis-only historical-import bootstrap (D-079 issuance prep, B2 closure)\n18aba3c RUN_STATE: Ed directive batch — effort cap lifted, fast-tier spec in flight, D-113 ruled (c), overnight issuance authorized\n41deedb docs(bridge): land the t3-doctrine gate amendments in contract §4/§6/§7/§8 + consumer skills (T3-AMEND-01 draft round)\n5f8b4b8 D-100 repair fix round 1: mechanical custody universe (runs root required), content-aware zero-byte sweep, closed-inventory b-ii classification, explicit dispatch at every claim consumer, membership-to-row binding; ruled falsifier regressions\n20f0007 Checkpoint 2026-08-01: metrology window B collected + salvage-closed; both window verdicts FAILED as-issued (distinct machinery questions -> desk adjudication); bird-SIGSTOP protocol validated; streaming-during-idle-gate hazard recorded","stderr":"","interrupted":false,"isImage":false,"noOutputExpected":false},"sourceToolAssistantUUID":"c551196e-7b86-4e8f-8e18-4e49908276bc","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:798:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-spec-decode-energy.md:1813:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-spec-decode-energy.md:4374:docs/decision_log.md:7496:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1583:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:247:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5286:docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-execute-summary.json:77:{"artifact":{"acceptance_id":"d079_calibration_acceptance_v2_n19","artifact_role":"issued","backfill_candidate":{"candidate_inventory":{"ordinary-invalid":6,"systematic-invalid":2,"valid":30},"production_issuance_blocked":false,"required_verification":"complete: lead-owned raw-physics and artifact-hash verification","status":"issued","superseded_id_only_blind_exclusions":["20260726T000039-491995f3","20260726T031222-e0ce33f5"]},"decimal_derivation":{"numeric_semantics":"decimal_source_lexemes","presentation_values":{"d079_range_12_places_s":{"label":"presentation_only_not_a_comparator","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000001 s","value":"0.010817749309"}},"ratified_operatives":{"allowance_rule":"max(observed_drift_s,bracket_screen_s)","bracket_screen_s":"0.010818","embedding_count":1,"max_budgetable_excess_s":"0.001275166090593858","maximum_budgetable_drift_s":"0.012093166090593858","operative_bound_rule":"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s","preflight_level_screen_s":"0.033558756679900"},"rounding":{"mode":"ROUND_HALF_EVEN","operative_bracket_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000001","source":"decimal_derivation.source_statistics.range_s","value_s":"0.010818"},"preflight_level_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000000000000001","source":"decimal_derivation.source_statistics.maximum_s","value_s":"0.033558756679900"}},"source_statistics":{"maximum_member_id":"20260722T222332-901c5c13","maximum_s":"0.03355875667989999","mean_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.026950033977532761"},"minimum_member_id":"20260722T215127-eeef661a","minimum_s":"0.022741007370546462","prediction_95_two_draw_s":"0.008826584887500717","prediction_99_two_draw_s":"0.012093166090593858","range_s":"0.010817749309353528","sample_sd_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.002970761365307205"}}},"decision_ids":["D-102","D-109"],"derivation_corpus":{"members":[{"b_fiducial_s":"0.03018980442653224","instrument_evidence_sha256":"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a","manifest_sha256":"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7","member_id":"20260722T145535-e941c821","source_directory":"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821"},{"b_fiducial_s":"0.026300679324099796","instrument_evidence_sha256":"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f","manifest_sha256":"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041","member_id":"20260722T194118-9dc0749d","source_directory":"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d"},{"b_fiducial_s":"0.03312014638436772","instrument_evidence_sha256":"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea","manifest_sha256":"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1","member_id":"20260722T214220-1acdbbc0","source_directory":"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0"},{"b_fiducial_s":"0.022741007370546462","instrument_evidence_sha256":"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024","manifest_sha256":"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5","member_id":"20260722T215127-eeef661a","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a"},{"b_fiducial_s":"0.03355875667989999","instrument_evidence_sha256":"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe","manifest_sha256":"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54","member_id":"20260722T222332-901c5c13","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13"},{"b_fiducial_s":"0.027654085293084385","instrument_evidence_sha256":"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7","manifest_sha256":"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70","member_id":"20260722T232509-82642517","source_directory":"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517"},{"b_fiducial_s":"0.024753340330112727","instrument_evidence_sha256":"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c","manifest_sha256":"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d","member_id":"20260723T023058-8732d1c9","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9"},{"b_fiducial_s":"0.025964638697819786","instrument_evidence_sha256":"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c","manifest_sha256":"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02","member_id":"20260723T052051-d9358c8a","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a"},{"b_fiducial_s":"0.027262160888545217","instrument_evidence_sha256":"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd","manifest_sha256":"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c","member_id":"20260723T183306-4ce692b4","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4"},{"b_fiducial_s":"0.024593263907495888","instrument_evidence_sha256":"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6","manifest_sha256":"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec","member_id":"20260723T194632-d04e038e","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e"},{"b_fiducial_s":"0.025305226022515448","instrument_evidence_sha256":"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7","manifest_sha256":"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005","member_id":"20260723T195730-bc4ba14a","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a"},{"b_fiducial_s":"0.027702588281732055","instrument_evidence_sha256":"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a","manifest_sha256":"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319","member_id":"20260723T221449-e9ae755e","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e"},{"b_fiducial_s":"0.026173651901677253","instrument_evidence_sha256":"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803","manifest_sha256":"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe","member_id":"20260723T223406-314f6d9e","source_directory":"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e"},{"b_fiducial_s":"0.02547564583006129","instrument_evidence_sha256":"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736","manifest_sha256":"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e","member_id":"20260724T014109-57844352","source_directory":"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352"},{"b_fiducial_s":"0.023241581438247116","instrument_evidence_sha256":"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be","manifest_sha256":"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9","member_id":"20260725T005132-a64711b7","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7"},{"b_fiducial_s":"0.028891617940876635","instrument_evidence_sha256":"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5","manifest_sha256":"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0","member_id":"20260725T011533-0b5ec77c","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c"},{"b_fiducial_s":"0.029197264796726408","instrument_evidence_sha256":"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da","manifest_sha256":"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185","member_id":"20260725T022712-0a9534f5","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5"},{"b_fiducial_s":"0.024879191521227362","instrument_evidence_sha256":"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e","manifest_sha256":"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a","member_id":"20260725T030533-d3f076e5","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5"},{"b_fiducial_s":"0.025045994537554683","instrument_evidence_sha256":"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2","manifest_sha256":"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704","member_id":"20260725T060617-97c5cba6","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6"}],"n":19,"selection":"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch"},"derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","identity_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100},"issuance":{"claim_eligible":true,"reason":"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff","status":"issued"},"ledger_cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","role":"issued_acceptance_baseline","sequence":76},"prior_observation_set":{"content_identity_method":"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))","cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","sequence":76},"epoch_catalog":{"d079_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100}},"observations":[{"attempt_id":"20260722T145535-e941c821","content_id":"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T194118-9dc0749d","content_id":"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T213749-563b9849","content_id":"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T214220-1acdbbc0","content_id":"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T215127-eeef661a","content_id":"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T222332-901c5c13","content_id":"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T232509-82642517","content_id":"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T023058-8732d1c9","content_id":"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T052051-d9358c8a","content_id":"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T183306-4ce692b4","content_id":"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T194632-d04e038e","content_id":"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T195730-bc4ba14a","content_id":"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T221449-e9ae755e","content_id":"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T223406-314f6d9e","content_id":"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260724T014109-57844352","content_id":"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T005132-a64711b7","content_id":"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T011533-0b5ec77c","content_id":"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T022712-0a9534f5","content_id":"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T030533-d3f076e5","content_id":"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T055825-b10cb348","content_id":"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T060617-97c5cba6","content_id":"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T000039-491995f3","content_id":"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710","disposition":"systematic-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T031222-e0ce33f5","content_id":"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225227-1f550773","content_id":"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225920-ab4272f5","content_id":"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T015824-45feb516","content_id":"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T020611-4a409a30","content_id":"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T050047-95e2f87e","content_id":"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260729T204105-39d25f8a","content_id":"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T014035-124df355","content_id":"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T210703-f76b5771","content_id":"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T012210-374020b6","content_id":"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T161713-b8b08280","content_id":"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T214355-126fc2ab","content_id":"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010113-e859f3aa","content_id":"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010805-ff3fdc88","content_id":"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T014059-8c3bfe9e","content_id":"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T064830-c76f5d1c","content_id":"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448","disposition":"systematic-invalid","epoch_id":"d079_epoch"}]},"prospective_rederivation":{"calendar_expiry":null,"estimator_code_sha256":{"joulewise/adapters/powermetrics.py":"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca","joulewise/powermetrics_fiducial.py":"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3","joulewise/reduce.py":"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615","joulewise/uncertainty_evidence.py":"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7"},"protocol_sha256":"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1","trigger_observation_rule":"judge_under_prior_artifact_never_self_fit","triggers":["identity_field_change","protocol_or_estimator_byte_change","new_valid_same_identity_capture_expands_observed_range","corpus_doubles_from_19_to_38","new_systematic_failure_challenges_preflight_screen"]},"schema_version":"joulewise.calibration_acceptance_bound.v2"},"artifact_file_content":"{\n  \"schema_version\": \"joulewise.calibration_acceptance_bound.v2\",\n  \"acceptance_id\": \"d079_calibration_acceptance_v2_n19\",\n  \"decision_ids\": [\n    \"D-102\",\n    \"D-109\"\n  ],\n  \"artifact_role\": \"issued\",\n  \"issuance\": {\n    \"status\": \"issued\",\n    \"claim_eligible\": true,\n    \"reason\": \"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff\"\n  },\n  \"ledger_cutoff\": {\n    \"sequence\": 76,\n    \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n    \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\",\n    \"role\": \"issued_acceptance_baseline\"\n  },\n  \"identity_epoch\": {\n    \"os_build\": \"25F84\",\n    \"hardware_model\": \"Mac15,9\",\n    \"power_policy\": \"ac_high_power\",\n    \"sampling_interval_ms\": 100,\n    \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n    \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n  },\n  \"prospective_rederivation\": {\n    \"calendar_expiry\": null,\n    \"trigger_observation_rule\": \"judge_under_prior_artifact_never_self_fit\",\n    \"triggers\": [\n      \"identity_field_change\",\n      \"protocol_or_estimator_byte_change\",\n      \"new_valid_same_identity_capture_expands_observed_range\",\n      \"corpus_doubles_from_19_to_38\",\n      \"new_systematic_failure_challenges_preflight_screen\"\n    ],\n    \"protocol_sha256\": \"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1\",\n    \"estimator_code_sha256\": {\n      \"joulewise/powermetrics_fiducial.py\": \"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3\",\n      \"joulewise/uncertainty_evidence.py\": \"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7\",\n      \"joulewise/adapters/powermetrics.py\": \"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca\",\n      \"joulewise/reduce.py\": \"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615\"\n    }\n  },\n  \"derivation_corpus\": {\n    \"selection\": \"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch\",\n    \"n\": 19,\n    \"members\": [\n      {\n        \"member_id\": \"20260722T145535-e941c821\",\n        \"source_directory\": \"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821\",\n        \"b_fiducial_s\": \"0.03018980442653224\",\n        \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n        \"instrument_evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\"\n      },\n      {\n        \"member_id\": \"20260722T194118-9dc0749d\",\n        \"source_directory\": \"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d\",\n        \"b_fiducial_s\": \"0.026300679324099796\",\n        \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n        \"instrument_evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\"\n      },\n      {\n        \"member_id\": \"20260722T214220-1acdbbc0\",\n        \"source_directory\": \"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0\",\n        \"b_fiducial_s\": \"0.03312014638436772\",\n        \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n        \"instrument_evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\"\n      },\n      {\n        \"member_id\": \"20260722T215127-eeef661a\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a\",\n        \"b_fiducial_s\": \"0.022741007370546462\",\n        \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n        \"instrument_evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\"\n      },\n      {\n        \"member_id\": \"20260722T222332-901c5c13\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13\",\n        \"b_fiducial_s\": \"0.03355875667989999\",\n        \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n        \"instrument_evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\"\n      },\n      {\n        \"member_id\": \"20260722T232509-82642517\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517\",\n        \"b_fiducial_s\": \"0.027654085293084385\",\n        \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n        \"instrument_evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\"\n      },\n      {\n        \"member_id\": \"20260723T023058-8732d1c9\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9\",\n        \"b_fiducial_s\": \"0.024753340330112727\",\n        \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n        \"instrument_evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\"\n      },\n      {\n        \"member_id\": \"20260723T052051-d9358c8a\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a\",\n        \"b_fiducial_s\": \"0.025964638697819786\",\n        \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n        \"instrument_evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\"\n      },\n      {\n        \"member_id\": \"20260723T183306-4ce692b4\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4\",\n        \"b_fiducial_s\": \"0.027262160888545217\",\n        \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n        \"instrument_evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\"\n      },\n      {\n        \"member_id\": \"20260723T194632-d04e038e\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e\",\n        \"b_fiducial_s\": \"0.024593263907495888\",\n        \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n        \"instrument_evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\"\n      },\n      {\n        \"member_id\": \"20260723T195730-bc4ba14a\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a\",\n        \"b_fiducial_s\": \"0.025305226022515448\",\n        \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n        \"instrument_evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\"\n      },\n      {\n        \"member_id\": \"20260723T221449-e9ae755e\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e\",\n        \"b_fiducial_s\": \"0.027702588281732055\",\n        \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n        \"instrument_evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\"\n      },\n      {\n        \"member_id\": \"20260723T223406-314f6d9e\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e\",\n        \"b_fiducial_s\": \"0.026173651901677253\",\n        \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n        \"instrument_evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\"\n      },\n      {\n        \"member_id\": \"20260724T014109-57844352\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352\",\n        \"b_fiducial_s\": \"0.02547564583006129\",\n        \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n        \"instrument_evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\"\n      },\n      {\n        \"member_id\": \"20260725T005132-a64711b7\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7\",\n        \"b_fiducial_s\": \"0.023241581438247116\",\n        \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n        \"instrument_evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\"\n      },\n      {\n        \"member_id\": \"20260725T011533-0b5ec77c\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c\",\n        \"b_fiducial_s\": \"0.028891617940876635\",\n        \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n        \"instrument_evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\"\n      },\n      {\n        \"member_id\": \"20260725T022712-0a9534f5\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5\",\n        \"b_fiducial_s\": \"0.029197264796726408\",\n        \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n        \"instrument_evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\"\n      },\n      {\n        \"member_id\": \"20260725T030533-d3f076e5\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5\",\n        \"b_fiducial_s\": \"0.024879191521227362\",\n        \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n        \"instrument_evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\"\n      },\n      {\n        \"member_id\": \"20260725T060617-97c5cba6\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6\",\n        \"b_fiducial_s\": \"0.025045994537554683\",\n        \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n        \"instrument_evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\"\n      }\n    ]\n  },\n  \"prior_observation_set\": {\n    \"cutoff\": {\n      \"sequence\": 76,\n      \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n      \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\"\n    },\n    \"content_identity_method\": \"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))\",\n    \"epoch_catalog\": {\n      \"d079_epoch\": {\n        \"os_build\": \"25F84\",\n        \"hardware_model\": \"Mac15,9\",\n        \"power_policy\": \"ac_high_power\",\n        \"sampling_interval_ms\": 100,\n        \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n        \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n      }\n    },\n    \"observations\": [\n      {\n        \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T145535-e941c821\"\n      },\n      {\n        \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T194118-9dc0749d\"\n      },\n      {\n        \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260722T213749-563b9849\"\n      },\n      {\n        \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T214220-1acdbbc0\"\n      },\n      {\n        \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T215127-eeef661a\"\n      },\n      {\n        \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T222332-901c5c13\"\n      },\n      {\n        \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T232509-82642517\"\n      },\n      {\n        \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T023058-8732d1c9\"\n      },\n      {\n        \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T052051-d9358c8a\"\n      },\n      {\n        \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T183306-4ce692b4\"\n      },\n      {\n        \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T194632-d04e038e\"\n      },\n      {\n        \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T195730-bc4ba14a\"\n      },\n      {\n        \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T221449-e9ae755e\"\n      },\n      {\n        \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T223406-314f6d9e\"\n      },\n      {\n        \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260724T014109-57844352\"\n      },\n      {\n        \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T005132-a64711b7\"\n      },\n      {\n        \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T011533-0b5ec77c\"\n      },\n      {\n        \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T022712-0a9534f5\"\n      },\n      {\n        \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T030533-d3f076e5\"\n      },\n      {\n        \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260725T055825-b10cb348\"\n      },\n      {\n        \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T060617-97c5cba6\"\n      },\n      {\n        \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260726T000039-491995f3\"\n      },\n      {\n        \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T031222-e0ce33f5\"\n      },\n      {\n        \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260726T225227-1f550773\"\n      },\n      {\n        \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T225920-ab4272f5\"\n      },\n      {\n        \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T015824-45feb516\"\n      },\n      {\n        \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T020611-4a409a30\"\n      },\n      {\n        \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T050047-95e2f87e\"\n      },\n      {\n        \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260729T204105-39d25f8a\"\n      },\n      {\n        \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T014035-124df355\"\n      },\n      {\n        \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T210703-f76b5771\"\n      },\n      {\n        \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T012210-374020b6\"\n      },\n      {\n        \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T161713-b8b08280\"\n      },\n      {\n        \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260731T214355-126fc2ab\"\n      },\n      {\n        \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010113-e859f3aa\"\n      },\n      {\n        \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010805-ff3fdc88\"\n      },\n      {\n        \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260801T014059-8c3bfe9e\"\n      },\n      {\n        \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260801T064830-c76f5d1c\"\n      }\n    ]\n  },\n  \"backfill_candidate\": {\n    \"status\": \"issued\",\n    \"candidate_inventory\": {\n      \"ordinary-invalid\": 6,\n      \"systematic-invalid\": 2,\n      \"valid\": 30\n    },\n    \"production_issuance_blocked\": false,\n    \"required_verification\": \"complete: lead-owned raw-physics and artifact-hash verification\",\n    \"superseded_id_only_blind_exclusions\": [\n      \"20260726T000039-491995f3\",\n      \"20260726T031222-e0ce33f5\"\n    ]\n  },\n  \"decimal_derivation\": {\n    \"numeric_semantics\": \"decimal_source_lexemes\",\n    \"source_statistics\": {\n      \"minimum_s\": \"0.022741007370546462\",\n      \"minimum_member_id\": \"20260722T215127-eeef661a\",\n      \"maximum_s\": \"0.03355875667989999\",\n      \"maximum_member_id\": \"20260722T222332-901c5c13\",\n      \"range_s\": \"0.010817749309353528\",\n      \"mean_presentation_s\": {\n        \"value\": \"0.026950033977532761\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"sample_sd_presentation_s\": {\n        \"value\": \"0.002970761365307205\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"prediction_95_two_draw_s\": \"0.008826584887500717\",\n      \"prediction_99_two_draw_s\": \"0.012093166090593858\"\n    },\n    \"presentation_values\": {\n      \"d079_range_12_places_s\": {\n        \"value\": \"0.010817749309\",\n        \"label\": \"presentation_only_not_a_comparator\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000001 s\"\n      }\n    },\n    \"rounding\": {\n      \"mode\": \"ROUND_HALF_EVEN\",\n      \"operative_bracket_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.range_s\",\n        \"quantum_s\": \"0.000001\",\n        \"value_s\": \"0.010818\",\n        \"numeric_role\": \"operative_comparator\"\n      },\n      \"preflight_level_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.maximum_s\",\n        \"quantum_s\": \"0.000000000000001\",\n        \"value_s\": \"0.033558756679900\",\n        \"numeric_role\": \"operative_comparator\"\n      }\n    },\n    \"ratified_operatives\": {\n      \"bracket_screen_s\": \"0.010818\",\n      \"preflight_level_screen_s\": \"0.033558756679900\",\n      \"max_budgetable_excess_s\": \"0.001275166090593858\",\n      \"maximum_budgetable_drift_s\": \"0.012093166090593858\",\n      \"allowance_rule\": \"max(observed_drift_s,bracket_screen_s)\",\n      \"operative_bound_rule\": \"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s\",\n      \"embedding_count\": 1\n    }\n  },\n  \"derivation_sha256\": \"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02\"\n}\n","artifact_file_sha256":"316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985","derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","record":"issued-acceptance-artifact","schema_version":"joulewise.calibration_acceptance_issuance_dry_run.v1"}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5479:docs/process_traces/2026-08-05-d113-rigor-consult/CONSULT-REPORT.md:140:        "current_disposition": "NO-GO at the inspected head. The production calibration-acceptance file is still explicitly schema_fixture_unissued and claim_eligible false; MINT-GENERALIZE-01 conditions (b) and (c) remain in flight; QUIET-GUARD-01 has failed audits and is not landed or active; the current MET-WINDOW-C-01 scope still assumes Window B supplies most C2/C4 members; fresh ED-5A and settled adapter identity remain pending.",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:241:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5712:docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:6:{"parentUuid":"5b9cfd00-18f5-4ade-a27c-f8e74632c36a","isSidechain":true,"promptId":"5c9e22f4-f072-4d90-ba34-2746cfa6a676","agentId":"ad24a0f43262b600c","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_01Dudks6Z24dNhWCgWDZM5Q3","type":"tool_result","content":"1\t# COLD-EYES ISSUANCE PACKET — D-079 calibration acceptance artifact + ledger genesis import\n2\t\n3\tYou are a COLD reviewer: no prior context from the session that produced\n4\tthis. Rule under rule-11 on whether this IRREVERSIBLE issuance is correct\n5\tto EXECUTE. The human principal (Ed) has authorized the issuance decision;\n6\tyour job is NOT whether to issue but whether the assembled artifact is\n7\tCORRECT — mechanical/correctness errors a loop-immersed agent can't see.\n8\tVerdict: PROCEED or HOLD (with the specific defect). Read primary sources\n9\tyourself; do not trust this packet's numbers without checking.\n10\t\n11\t## What is about to happen (irreversible)\n12\t\n13\t1. `scripts/calibration_ledger_bootstrap.py --execute` writes the real\n14\t   `configs/calibration/calibration_observation_ledger` (currently\n15\t   absent; head pin at genesis seq 0 / all-zeros).\n16\t2. The printed head pin (seq 76, head below) is committed to\n17\t   `configs/calibration/calibration_ledger_head.json`.\n18\t3. `configs/calibration/calibration_acceptance_d079_v2.json` flips\n19\t   `artifact_role` schema_fixture_unissued → issued, cutoff = (seq 76,\n20\t   head), prior_observation_set filled per the ledger's import-marked\n21\t   prefix.\n22\t4. A decision-log entry (D-116) records the issuance.\n23\t\n24\tThis artifact is the authentication anchor for ALL future floor-mint\n25\tclaims. An error here silently taints every downstream claim.\n26\t\n27\t## Assembled facts (VERIFY each against the cited primary source)\n28\t\n29\t- Disposition table: `/private/tmp/d079-ledger-dispositions.json`,\n30\t  sha256 `5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a`,\n31\t  38 members = 30 valid / 2 systematic-invalid / 6 ordinary-invalid.\n32\t- The 2 systematic-invalid members (`20260726T000039-491995f3`,\n33\t  `20260801T064830-c76f5d1c`) were lead-ruled systematic (bounds exceed\n34\t  the 0.033558756679900 preflight screen; D-102 names the first a\n35\t  systematic failure). VERIFY this ruling against\n36\t  `docs/decision_log.md` D-102 and the verification report's per-member\n37\t  physics (report: `docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md`).\n38\t- Custody manifest: `/private/tmp/d079-custody-manifest.lead.json`,\n39\t  sha256 `99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078`,\n40\t  lead-regenerated (byte-identical to the delegated generation).\n41\t- Candidate head: `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`\n42\t  at sequence 76. REPRODUCE it yourself with a dry-run (read-only,\n43\t  writes nothing):\n44\t  `python3 scripts/calibration_ledger_bootstrap.py --disposition-table /private/tmp/d079-ledger-dispositions.json --expected-table-sha256 5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a --custody-manifest /private/tmp/d079-custody-manifest.lead.json --expected-custody-manifest-sha256 99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078 --checkout-root /Users/edr`\n45\t- derivation_corpus stays n=19, derivation_sha256\n46\t  `3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d`\n47\t  (unchanged; the issuance edits the acceptance file so its OWN file\n48\t  hash changes — that is expected, the n=19 statistics do not).\n49\t- Binding requirements: D-109 R1.4 + R2.1-8 (docs/decision_log.md).\n50\t- The bootstrap code passed a 4-round adversarial gaunttet ending in an\n51\t  ACCEPT delta audit (record:\n52\t  `/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/ledgerboot-delta4.md`).\n53\t\n54\t## Your checks (rule and report each)\n55\t\n56\t1. Reproduce the head. Does it equal 08456d50…@76? If not → HOLD.\n57\t2. Spot-verify the B1 disposition ruling: are the two systematic-invalid\n58\t   members genuinely bound-exceeding per the raw physics in the\n59\t   verification report, and is systematic-invalid the correct ledger\n60\t   disposition (vs valid) under D-102's screen? A wrong disposition\n61\t   changes the head and the corpus-doubling count.\n62\t3. D-109 R2 conformance of the plan: prior_observation_set completeness\n63\t   (all 38 content-distinct, epoch+disposition), content identity from\n64\t   primary-byte hashes, the import marker excluded from post-cutoff\n65\t   populations, cutoff = exact (seq, head).\n66\t4. Any reason the genesis import should NOT be the authoritative ledger\n67\t   (root-universe completeness now that custody is manifest-pinned;\n68\t   the manifest references iCloud-backup copies for 22 members — is that\n69\t   acceptable provenance for the authoritative ledger, or must those\n70\t   copies live in the primary checkout first?).\n71\t5. Anything else that would make this issuance unsound.\n72\t\n73\t## Output\n74\t\n75\tA clear PROCEED or HOLD with per-check findings and the reproduced head.\n76\tIf HOLD, name the exact defect and the primary evidence. This is the\n77\tlast check before an irreversible write to the claim-authentication\n78\tanchor — be exacting.\n79\t"}]},"uuid":"a105451f-04e9-4b7d-ac9a-5f72f990ff91","timestamp":"2026-08-06T08:35:11.582Z","toolUseResult":{"type":"text","file":{"filePath":"/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/d079-issuance-packet.md","content":"# COLD-EYES ISSUANCE PACKET — D-079 calibration acceptance artifact + ledger genesis import\n\nYou are a COLD reviewer: no prior context from the session that produced\nthis. Rule under rule-11 on whether this IRREVERSIBLE issuance is correct\nto EXECUTE. The human principal (Ed) has authorized the issuance decision;\nyour job is NOT whether to issue but whether the assembled artifact is\nCORRECT — mechanical/correctness errors a loop-immersed agent can't see.\nVerdict: PROCEED or HOLD (with the specific defect). Read primary sources\nyourself; do not trust this packet's numbers without checking.\n\n## What is about to happen (irreversible)\n\n1. `scripts/calibration_ledger_bootstrap.py --execute` writes the real\n   `configs/calibration/calibration_observation_ledger` (currently\n   absent; head pin at genesis seq 0 / all-zeros).\n2. The printed head pin (seq 76, head below) is committed to\n   `configs/calibration/calibration_ledger_head.json`.\n3. `configs/calibration/calibration_acceptance_d079_v2.json` flips\n   `artifact_role` schema_fixture_unissued → issued, cutoff = (seq 76,\n   head), prior_observation_set filled per the ledger's import-marked\n   prefix.\n4. A decision-log entry (D-116) records the issuance.\n\nThis artifact is the authentication anchor for ALL future floor-mint\nclaims. An error here silently taints every downstream claim.\n\n## Assembled facts (VERIFY each against the cited primary source)\n\n- Disposition table: `/private/tmp/d079-ledger-dispositions.json`,\n  sha256 `5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a`,\n  38 members = 30 valid / 2 systematic-invalid / 6 ordinary-invalid.\n- The 2 systematic-invalid members (`20260726T000039-491995f3`,\n  `20260801T064830-c76f5d1c`) were lead-ruled systematic (bounds exceed\n  the 0.033558756679900 preflight screen; D-102 names the first a\n  systematic failure). VERIFY this ruling against\n  `docs/decision_log.md` D-102 and the verification report's per-member\n  physics (report: `docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md`).\n- Custody manifest: `/private/tmp/d079-custody-manifest.lead.json`,\n  sha256 `99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078`,\n  lead-regenerated (byte-identical to the delegated generation).\n- Candidate head: `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`\n  at sequence 76. REPRODUCE it yourself with a dry-run (read-only,\n  writes nothing):\n  `python3 scripts/calibration_ledger_bootstrap.py --disposition-table /private/tmp/d079-ledger-dispositions.json --expected-table-sha256 5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a --custody-manifest /private/tmp/d079-custody-manifest.lead.json --expected-custody-manifest-sha256 99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078 --checkout-root /Users/edr`\n- derivation_corpus stays n=19, derivation_sha256\n  `3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d`\n  (unchanged; the issuance edits the acceptance file so its OWN file\n  hash changes — that is expected, the n=19 statistics do not).\n- Binding requirements: D-109 R1.4 + R2.1-8 (docs/decision_log.md).\n- The bootstrap code passed a 4-round adversarial gaunttet ending in an\n  ACCEPT delta audit (record:\n  `/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/ledgerboot-delta4.md`).\n\n## Your checks (rule and report each)\n\n1. Reproduce the head. Does it equal 08456d50…@76? If not → HOLD.\n2. Spot-verify the B1 disposition ruling: are the two systematic-invalid\n   members genuinely bound-exceeding per the raw physics in the\n   verification report, and is systematic-invalid the correct ledger\n   disposition (vs valid) under D-102's screen? A wrong disposition\n   changes the head and the corpus-doubling count.\n3. D-109 R2 conformance of the plan: prior_observation_set completeness\n   (all 38 content-distinct, epoch+disposition), content identity from\n   primary-byte hashes, the import marker excluded from post-cutoff\n   populations, cutoff = exact (seq, head).\n4. Any reason the genesis import should NOT be the authoritative ledger\n   (root-universe completeness now that custody is manifest-pinned;\n   the manifest references iCloud-backup copies for 22 members — is that\n   acceptable provenance for the authoritative ledger, or must those\n   copies live in the primary checkout first?).\n5. Anything else that would make this issuance unsound.\n\n## Output\n\nA clear PROCEED or HOLD with per-check findings and the reproduced head.\nIf HOLD, name the exact defect and the primary evidence. This is the\nlast check before an irreversible write to the claim-authentication\nanchor — be exacting.\n","numLines":79,"startLine":1,"totalLines":79}},"sourceToolAssistantUUID":"5b9cfd00-18f5-4ade-a27c-f8e74632c36a","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5740:docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:59:{"parentUuid":"07b9c6e1-cf97-433c-a130-aed8bf8cac71","isSidechain":true,"agentId":"ad24a0f43262b600c","message":{"model":"claude-opus-4-8","id":"msg_011CdmCDLdurdj31n8c7k4fH","type":"message","role":"assistant","content":[{"type":"text","text":"All checks complete. Let me record the final confirmations: only members 22 & 38 among the VERIFIED-VALID set exceed the screen (no missed systematic call), and the derivation hash is unchanged.\n\nVerdict follows.\n\n---\n\n**VERDICT: PROCEED** — with two advisory notes for magistrate awareness (neither blocks; both are correctness-neutral or conservative).\n\n**Reproduced head (dry-run, wrote nothing):**\n`08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7` at sequence 76. Bit-for-bit equal to the packet's candidate head. The dry-run summary self-reports `executed:false`, `outcome:planned`, `receipt_count:76`, and the head-pin content `{sequence:76, head_digest:08456d50…, ledger_schema:joulewise.calibration_observation_ledger.v1}`. Both input digests matched (`5da820aa…` table, `99cbf3df…` custody manifest).\n\n**Per-check findings:**\n\n- **Check 1 — Head reproduction: PASS.** Reproduced exactly. The head embeds the iCloud absolute custody locators and the systematic-invalid disposition on the final (seq-76) receipt, so byte-identity of the head confirms the disposition ruling, the ordering, the custody selection, and all 38 authenticated artifact hashes simultaneously. (Note: this head differs from the two \"illustrative\" heads in the verification report — `cb410907…` and `8e80b6e9…` — because those used an unauthorized synthetic reservation/finalization assumption; the report explicitly labeled them non-authoritative. The bootstrap's `historical-import-v1` transaction is the authoritative computation.)\n\n- **Check 2 — B1 disposition ruling: PASS (ruling is correct and conservative).** The two systematic-invalid members are `20260726T000039-491995f3` (bound 0.035435840879704805) and `20260801T064830-c76f5d1c` (bound 0.0350400833260715). Both exceed the ratified preflight screen 0.033558756679900. Primary corroboration: `docs/decision_log.md` (D-102, ~lines 6298-6301) states verbatim that window B's pre-calibration `0.035435840879704805 s (verified in primary evidence) exceeds the pre-flight level screen, and D-079 cl.2's systematic failure is never budgetable` — that is member 491995f3 by exact value. The verification report replays both as physically VALID but bound-exceeding, and the production writer (`validate_powermetrics_fiducial.py:664-671`) maps a valid-but-over-screen capture to systematic-invalid. Selecting systematic-invalid (vs the candidate-tool's \"valid\") is the doctrine-consistent choice. I independently confirmed that among all VERIFIED-VALID members, exactly these two exceed the screen — the max remaining valid bound is member `901c5c13` at 0.03355875667989999, just under the screen (that member is the corpus ceiling). No missed systematic call; no over-flagging.\n\n- **Check 3 — D-109 R2 conformance: PASS.** Disposition table = 38 members, all content-distinct (38 unique content_ids), single identity epoch at table level matching d079_epoch (os_build 25F84, Mac15,9, ac_high_power, 100 ms, joint_loss_sublevel_interval_branch_v2, powermetrics_pulse_fiducial_v3). Table content_ids and dispositions match the verification report's per-member exactly, with only members 22 and 38 flipped to systematic-invalid (R2.7's raw-physics ruling superseding the candidate labels — as R2.7 mandates). Final counts 30 valid / 2 systematic-invalid / 6 ordinary-invalid, all in the allowed disposition set (R2.3 records systematic + ordinary + valid separately). Cutoff = exact receipt (seq 76 = member 38's finalization) satisfying R2.1. derivation_corpus stays n=19 with derivation_sha256 `3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d` (verified in the current acceptance file — unchanged). Reservation receipts carry null content_id / pending disposition, so they cannot leak into the post-cutoff \"new\" subtraction.\n\n- **Check 4 — genesis-import authoritativeness / iCloud provenance: ACCEPTABLE.** The raw instrument-evidence run trees are **git-ignored** in the checkout (`git check-ignore` matches `runs*/instrument_validation`; zero tracked files under any `instrument_validation`). Raw evidence is never version-controlled by repo convention — the iCloud `com~apple~CloudDocs/JouleWise-backup` tree is the designated `raw_archive` (verification-report inventory). All 38 custody dirs currently exist and their bytes authenticate (the head would not reproduce otherwise). Integrity of the claim-authentication anchor rests on the **committed hash chain** (ledger + head-pin in git), which binds every artifact_sha256; the `custody_locator` is a provenance pointer, not the integrity root. Since the in-checkout copies are themselves untracked working files (same durability class), requiring them \"in the primary checkout first\" would add nothing durable. So iCloud provenance is acceptable for the authoritative ledger.\n\n- **Check 5 — other soundness: PASS.** Current pre-issuance state is consistent with the packet: head pin = genesis seq 0 / all-zeros; ledger file absent; acceptance `artifact_role = schema_fixture_unissued`, no cutoff.\n\n**Advisory notes (non-blocking):**\n\n1. **Packet undercounts custody provenance.** The packet's check-4 says \"iCloud-backup copies for 22 of the 38 members.\" In fact **all 38** custody locators are iCloud `JouleWise-backup` paths (0 point into the checkout). This does not change the verdict — the provenance assessment above applies to all 38 — but the \"22\" figure in the packet is inaccurate and should not be relied on in the D-116 log entry.\n\n2. **D-109 R2.8's literal \"six further\" is superseded to \"eight further.\"** R2.8 as written stated the corpus-doubling consequence as \"six further valid observations trigger re-derivation,\" predicated on the candidate-inventory 32-valid count. The (correct) systematic-invalid ruling makes it 30 valid → eight further needed. This is internally consistent because R2.7 explicitly subordinates the candidate inventory to the raw-physics ruling, and both counts yield `trigger_now = false` today — no claim-authentication consequence. Worth a one-line note in the issuance record so the \"six\" in R2.8's prose isn't later mistaken for a live count.\n\nNothing found rises to a HOLD. The irreversible write is correct to execute."}],"stop_reason":"end_turn","stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":6190,"cache_read_input_tokens":72704,"output_tokens":4454,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":6190},"inference_geo":"not_available","iterations":[{"input_tokens":2,"output_tokens":4454,"cache_read_input_tokens":72704,"cache_creation_input_tokens":6190,"cache_creation":{"ephemeral_5m_input_tokens":6190,"ephemeral_1h_input_tokens":0},"type":"message"}],"speed":"standard"},"diagnostics":null},"requestId":"req_011CdmCDKedQPCyg9RpRMtsW","attributionAgent":"general-purpose","type":"assistant","uuid":"20a22ec2-b8ee-45c1-ab63-99153ea692ed","timestamp":"2026-08-06T08:40:51.650Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:1311:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:5353:joulewise/calibration_bracketing.py:42:ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:5354:joulewise/calibration_bracketing.py:44:    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:1195:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-contamination-characterization.md:1953:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-prefill-scaling-laws.md:1448:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md:1338:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md:4370:./docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-execute-summary.json:77:{"artifact":{"acceptance_id":"d079_calibration_acceptance_v2_n19","artifact_role":"issued","backfill_candidate":{"candidate_inventory":{"ordinary-invalid":6,"systematic-invalid":2,"valid":30},"production_issuance_blocked":false,"required_verification":"complete: lead-owned raw-physics and artifact-hash verification","status":"issued","superseded_id_only_blind_exclusions":["20260726T000039-491995f3","20260726T031222-e0ce33f5"]},"decimal_derivation":{"numeric_semantics":"decimal_source_lexemes","presentation_values":{"d079_range_12_places_s":{"label":"presentation_only_not_a_comparator","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000001 s","value":"0.010817749309"}},"ratified_operatives":{"allowance_rule":"max(observed_drift_s,bracket_screen_s)","bracket_screen_s":"0.010818","embedding_count":1,"max_budgetable_excess_s":"0.001275166090593858","maximum_budgetable_drift_s":"0.012093166090593858","operative_bound_rule":"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s","preflight_level_screen_s":"0.033558756679900"},"rounding":{"mode":"ROUND_HALF_EVEN","operative_bracket_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000001","source":"decimal_derivation.source_statistics.range_s","value_s":"0.010818"},"preflight_level_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000000000000001","source":"decimal_derivation.source_statistics.maximum_s","value_s":"0.033558756679900"}},"source_statistics":{"maximum_member_id":"20260722T222332-901c5c13","maximum_s":"0.03355875667989999","mean_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.026950033977532761"},"minimum_member_id":"20260722T215127-eeef661a","minimum_s":"0.022741007370546462","prediction_95_two_draw_s":"0.008826584887500717","prediction_99_two_draw_s":"0.012093166090593858","range_s":"0.010817749309353528","sample_sd_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.002970761365307205"}}},"decision_ids":["D-102","D-109"],"derivation_corpus":{"members":[{"b_fiducial_s":"0.03018980442653224","instrument_evidence_sha256":"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a","manifest_sha256":"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7","member_id":"20260722T145535-e941c821","source_directory":"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821"},{"b_fiducial_s":"0.026300679324099796","instrument_evidence_sha256":"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f","manifest_sha256":"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041","member_id":"20260722T194118-9dc0749d","source_directory":"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d"},{"b_fiducial_s":"0.03312014638436772","instrument_evidence_sha256":"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea","manifest_sha256":"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1","member_id":"20260722T214220-1acdbbc0","source_directory":"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0"},{"b_fiducial_s":"0.022741007370546462","instrument_evidence_sha256":"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024","manifest_sha256":"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5","member_id":"20260722T215127-eeef661a","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a"},{"b_fiducial_s":"0.03355875667989999","instrument_evidence_sha256":"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe","manifest_sha256":"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54","member_id":"20260722T222332-901c5c13","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13"},{"b_fiducial_s":"0.027654085293084385","instrument_evidence_sha256":"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7","manifest_sha256":"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70","member_id":"20260722T232509-82642517","source_directory":"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517"},{"b_fiducial_s":"0.024753340330112727","instrument_evidence_sha256":"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c","manifest_sha256":"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d","member_id":"20260723T023058-8732d1c9","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9"},{"b_fiducial_s":"0.025964638697819786","instrument_evidence_sha256":"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c","manifest_sha256":"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02","member_id":"20260723T052051-d9358c8a","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a"},{"b_fiducial_s":"0.027262160888545217","instrument_evidence_sha256":"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd","manifest_sha256":"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c","member_id":"20260723T183306-4ce692b4","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4"},{"b_fiducial_s":"0.024593263907495888","instrument_evidence_sha256":"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6","manifest_sha256":"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec","member_id":"20260723T194632-d04e038e","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e"},{"b_fiducial_s":"0.025305226022515448","instrument_evidence_sha256":"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7","manifest_sha256":"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005","member_id":"20260723T195730-bc4ba14a","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a"},{"b_fiducial_s":"0.027702588281732055","instrument_evidence_sha256":"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a","manifest_sha256":"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319","member_id":"20260723T221449-e9ae755e","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e"},{"b_fiducial_s":"0.026173651901677253","instrument_evidence_sha256":"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803","manifest_sha256":"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe","member_id":"20260723T223406-314f6d9e","source_directory":"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e"},{"b_fiducial_s":"0.02547564583006129","instrument_evidence_sha256":"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736","manifest_sha256":"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e","member_id":"20260724T014109-57844352","source_directory":"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352"},{"b_fiducial_s":"0.023241581438247116","instrument_evidence_sha256":"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be","manifest_sha256":"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9","member_id":"20260725T005132-a64711b7","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7"},{"b_fiducial_s":"0.028891617940876635","instrument_evidence_sha256":"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5","manifest_sha256":"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0","member_id":"20260725T011533-0b5ec77c","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c"},{"b_fiducial_s":"0.029197264796726408","instrument_evidence_sha256":"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da","manifest_sha256":"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185","member_id":"20260725T022712-0a9534f5","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5"},{"b_fiducial_s":"0.024879191521227362","instrument_evidence_sha256":"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e","manifest_sha256":"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a","member_id":"20260725T030533-d3f076e5","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5"},{"b_fiducial_s":"0.025045994537554683","instrument_evidence_sha256":"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2","manifest_sha256":"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704","member_id":"20260725T060617-97c5cba6","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6"}],"n":19,"selection":"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch"},"derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","identity_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100},"issuance":{"claim_eligible":true,"reason":"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff","status":"issued"},"ledger_cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","role":"issued_acceptance_baseline","sequence":76},"prior_observation_set":{"content_identity_method":"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))","cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","sequence":76},"epoch_catalog":{"d079_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100}},"observations":[{"attempt_id":"20260722T145535-e941c821","content_id":"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T194118-9dc0749d","content_id":"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T213749-563b9849","content_id":"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T214220-1acdbbc0","content_id":"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T215127-eeef661a","content_id":"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T222332-901c5c13","content_id":"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T232509-82642517","content_id":"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T023058-8732d1c9","content_id":"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T052051-d9358c8a","content_id":"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T183306-4ce692b4","content_id":"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T194632-d04e038e","content_id":"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T195730-bc4ba14a","content_id":"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T221449-e9ae755e","content_id":"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T223406-314f6d9e","content_id":"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260724T014109-57844352","content_id":"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T005132-a64711b7","content_id":"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T011533-0b5ec77c","content_id":"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T022712-0a9534f5","content_id":"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T030533-d3f076e5","content_id":"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T055825-b10cb348","content_id":"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T060617-97c5cba6","content_id":"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T000039-491995f3","content_id":"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710","disposition":"systematic-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T031222-e0ce33f5","content_id":"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225227-1f550773","content_id":"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225920-ab4272f5","content_id":"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T015824-45feb516","content_id":"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T020611-4a409a30","content_id":"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T050047-95e2f87e","content_id":"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260729T204105-39d25f8a","content_id":"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T014035-124df355","content_id":"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T210703-f76b5771","content_id":"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T012210-374020b6","content_id":"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T161713-b8b08280","content_id":"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T214355-126fc2ab","content_id":"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010113-e859f3aa","content_id":"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010805-ff3fdc88","content_id":"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T014059-8c3bfe9e","content_id":"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T064830-c76f5d1c","content_id":"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448","disposition":"systematic-invalid","epoch_id":"d079_epoch"}]},"prospective_rederivation":{"calendar_expiry":null,"estimator_code_sha256":{"joulewise/adapters/powermetrics.py":"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca","joulewise/powermetrics_fiducial.py":"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3","joulewise/reduce.py":"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615","joulewise/uncertainty_evidence.py":"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7"},"protocol_sha256":"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1","trigger_observation_rule":"judge_under_prior_artifact_never_self_fit","triggers":["identity_field_change","protocol_or_estimator_byte_change","new_valid_same_identity_capture_expands_observed_range","corpus_doubles_from_19_to_38","new_systematic_failure_challenges_preflight_screen"]},"schema_version":"joulewise.calibration_acceptance_bound.v2"},"artifact_file_content":"{\n  \"schema_version\": \"joulewise.calibration_acceptance_bound.v2\",\n  \"acceptance_id\": \"d079_calibration_acceptance_v2_n19\",\n  \"decision_ids\": [\n    \"D-102\",\n    \"D-109\"\n  ],\n  \"artifact_role\": \"issued\",\n  \"issuance\": {\n    \"status\": \"issued\",\n    \"claim_eligible\": true,\n    \"reason\": \"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff\"\n  },\n  \"ledger_cutoff\": {\n    \"sequence\": 76,\n    \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n    \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\",\n    \"role\": \"issued_acceptance_baseline\"\n  },\n  \"identity_epoch\": {\n    \"os_build\": \"25F84\",\n    \"hardware_model\": \"Mac15,9\",\n    \"power_policy\": \"ac_high_power\",\n    \"sampling_interval_ms\": 100,\n    \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n    \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n  },\n  \"prospective_rederivation\": {\n    \"calendar_expiry\": null,\n    \"trigger_observation_rule\": \"judge_under_prior_artifact_never_self_fit\",\n    \"triggers\": [\n      \"identity_field_change\",\n      \"protocol_or_estimator_byte_change\",\n      \"new_valid_same_identity_capture_expands_observed_range\",\n      \"corpus_doubles_from_19_to_38\",\n      \"new_systematic_failure_challenges_preflight_screen\"\n    ],\n    \"protocol_sha256\": \"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1\",\n    \"estimator_code_sha256\": {\n      \"joulewise/powermetrics_fiducial.py\": \"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3\",\n      \"joulewise/uncertainty_evidence.py\": \"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7\",\n      \"joulewise/adapters/powermetrics.py\": \"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca\",\n      \"joulewise/reduce.py\": \"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615\"\n    }\n  },\n  \"derivation_corpus\": {\n    \"selection\": \"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch\",\n    \"n\": 19,\n    \"members\": [\n      {\n        \"member_id\": \"20260722T145535-e941c821\",\n        \"source_directory\": \"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821\",\n        \"b_fiducial_s\": \"0.03018980442653224\",\n        \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n        \"instrument_evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\"\n      },\n      {\n        \"member_id\": \"20260722T194118-9dc0749d\",\n        \"source_directory\": \"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d\",\n        \"b_fiducial_s\": \"0.026300679324099796\",\n        \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n        \"instrument_evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\"\n      },\n      {\n        \"member_id\": \"20260722T214220-1acdbbc0\",\n        \"source_directory\": \"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0\",\n        \"b_fiducial_s\": \"0.03312014638436772\",\n        \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n        \"instrument_evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\"\n      },\n      {\n        \"member_id\": \"20260722T215127-eeef661a\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a\",\n        \"b_fiducial_s\": \"0.022741007370546462\",\n        \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n        \"instrument_evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\"\n      },\n      {\n        \"member_id\": \"20260722T222332-901c5c13\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13\",\n        \"b_fiducial_s\": \"0.03355875667989999\",\n        \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n        \"instrument_evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\"\n      },\n      {\n        \"member_id\": \"20260722T232509-82642517\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517\",\n        \"b_fiducial_s\": \"0.027654085293084385\",\n        \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n        \"instrument_evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\"\n      },\n      {\n        \"member_id\": \"20260723T023058-8732d1c9\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9\",\n        \"b_fiducial_s\": \"0.024753340330112727\",\n        \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n        \"instrument_evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\"\n      },\n      {\n        \"member_id\": \"20260723T052051-d9358c8a\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a\",\n        \"b_fiducial_s\": \"0.025964638697819786\",\n        \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n        \"instrument_evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\"\n      },\n      {\n        \"member_id\": \"20260723T183306-4ce692b4\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4\",\n        \"b_fiducial_s\": \"0.027262160888545217\",\n        \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n        \"instrument_evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\"\n      },\n      {\n        \"member_id\": \"20260723T194632-d04e038e\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e\",\n        \"b_fiducial_s\": \"0.024593263907495888\",\n        \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n        \"instrument_evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\"\n      },\n      {\n        \"member_id\": \"20260723T195730-bc4ba14a\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a\",\n        \"b_fiducial_s\": \"0.025305226022515448\",\n        \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n        \"instrument_evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\"\n      },\n      {\n        \"member_id\": \"20260723T221449-e9ae755e\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e\",\n        \"b_fiducial_s\": \"0.027702588281732055\",\n        \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n        \"instrument_evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\"\n      },\n      {\n        \"member_id\": \"20260723T223406-314f6d9e\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e\",\n        \"b_fiducial_s\": \"0.026173651901677253\",\n        \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n        \"instrument_evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\"\n      },\n      {\n        \"member_id\": \"20260724T014109-57844352\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352\",\n        \"b_fiducial_s\": \"0.02547564583006129\",\n        \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n        \"instrument_evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\"\n      },\n      {\n        \"member_id\": \"20260725T005132-a64711b7\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7\",\n        \"b_fiducial_s\": \"0.023241581438247116\",\n        \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n        \"instrument_evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\"\n      },\n      {\n        \"member_id\": \"20260725T011533-0b5ec77c\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c\",\n        \"b_fiducial_s\": \"0.028891617940876635\",\n        \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n        \"instrument_evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\"\n      },\n      {\n        \"member_id\": \"20260725T022712-0a9534f5\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5\",\n        \"b_fiducial_s\": \"0.029197264796726408\",\n        \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n        \"instrument_evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\"\n      },\n      {\n        \"member_id\": \"20260725T030533-d3f076e5\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5\",\n        \"b_fiducial_s\": \"0.024879191521227362\",\n        \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n        \"instrument_evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\"\n      },\n      {\n        \"member_id\": \"20260725T060617-97c5cba6\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6\",\n        \"b_fiducial_s\": \"0.025045994537554683\",\n        \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n        \"instrument_evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\"\n      }\n    ]\n  },\n  \"prior_observation_set\": {\n    \"cutoff\": {\n      \"sequence\": 76,\n      \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n      \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\"\n    },\n    \"content_identity_method\": \"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))\",\n    \"epoch_catalog\": {\n      \"d079_epoch\": {\n        \"os_build\": \"25F84\",\n        \"hardware_model\": \"Mac15,9\",\n        \"power_policy\": \"ac_high_power\",\n        \"sampling_interval_ms\": 100,\n        \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n        \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n      }\n    },\n    \"observations\": [\n      {\n        \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T145535-e941c821\"\n      },\n      {\n        \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T194118-9dc0749d\"\n      },\n      {\n        \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260722T213749-563b9849\"\n      },\n      {\n        \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T214220-1acdbbc0\"\n      },\n      {\n        \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T215127-eeef661a\"\n      },\n      {\n        \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T222332-901c5c13\"\n      },\n      {\n        \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T232509-82642517\"\n      },\n      {\n        \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T023058-8732d1c9\"\n      },\n      {\n        \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T052051-d9358c8a\"\n      },\n      {\n        \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T183306-4ce692b4\"\n      },\n      {\n        \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T194632-d04e038e\"\n      },\n      {\n        \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T195730-bc4ba14a\"\n      },\n      {\n        \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T221449-e9ae755e\"\n      },\n      {\n        \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T223406-314f6d9e\"\n      },\n      {\n        \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260724T014109-57844352\"\n      },\n      {\n        \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T005132-a64711b7\"\n      },\n      {\n        \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T011533-0b5ec77c\"\n      },\n      {\n        \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T022712-0a9534f5\"\n      },\n      {\n        \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T030533-d3f076e5\"\n      },\n      {\n        \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260725T055825-b10cb348\"\n      },\n      {\n        \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T060617-97c5cba6\"\n      },\n      {\n        \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260726T000039-491995f3\"\n      },\n      {\n        \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T031222-e0ce33f5\"\n      },\n      {\n        \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260726T225227-1f550773\"\n      },\n      {\n        \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T225920-ab4272f5\"\n      },\n      {\n        \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T015824-45feb516\"\n      },\n      {\n        \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T020611-4a409a30\"\n      },\n      {\n        \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T050047-95e2f87e\"\n      },\n      {\n        \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260729T204105-39d25f8a\"\n      },\n      {\n        \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T014035-124df355\"\n      },\n      {\n        \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T210703-f76b5771\"\n      },\n      {\n        \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T012210-374020b6\"\n      },\n      {\n        \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T161713-b8b08280\"\n      },\n      {\n        \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260731T214355-126fc2ab\"\n      },\n      {\n        \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010113-e859f3aa\"\n      },\n      {\n        \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010805-ff3fdc88\"\n      },\n      {\n        \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260801T014059-8c3bfe9e\"\n      },\n      {\n        \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260801T064830-c76f5d1c\"\n      }\n    ]\n  },\n  \"backfill_candidate\": {\n    \"status\": \"issued\",\n    \"candidate_inventory\": {\n      \"ordinary-invalid\": 6,\n      \"systematic-invalid\": 2,\n      \"valid\": 30\n    },\n    \"production_issuance_blocked\": false,\n    \"required_verification\": \"complete: lead-owned raw-physics and artifact-hash verification\",\n    \"superseded_id_only_blind_exclusions\": [\n      \"20260726T000039-491995f3\",\n      \"20260726T031222-e0ce33f5\"\n    ]\n  },\n  \"decimal_derivation\": {\n    \"numeric_semantics\": \"decimal_source_lexemes\",\n    \"source_statistics\": {\n      \"minimum_s\": \"0.022741007370546462\",\n      \"minimum_member_id\": \"20260722T215127-eeef661a\",\n      \"maximum_s\": \"0.03355875667989999\",\n      \"maximum_member_id\": \"20260722T222332-901c5c13\",\n      \"range_s\": \"0.010817749309353528\",\n      \"mean_presentation_s\": {\n        \"value\": \"0.026950033977532761\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"sample_sd_presentation_s\": {\n        \"value\": \"0.002970761365307205\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"prediction_95_two_draw_s\": \"0.008826584887500717\",\n      \"prediction_99_two_draw_s\": \"0.012093166090593858\"\n    },\n    \"presentation_values\": {\n      \"d079_range_12_places_s\": {\n        \"value\": \"0.010817749309\",\n        \"label\": \"presentation_only_not_a_comparator\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000001 s\"\n      }\n    },\n    \"rounding\": {\n      \"mode\": \"ROUND_HALF_EVEN\",\n      \"operative_bracket_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.range_s\",\n        \"quantum_s\": \"0.000001\",\n        \"value_s\": \"0.010818\",\n        \"numeric_role\": \"operative_comparator\"\n      },\n      \"preflight_level_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.maximum_s\",\n        \"quantum_s\": \"0.000000000000001\",\n        \"value_s\": \"0.033558756679900\",\n        \"numeric_role\": \"operative_comparator\"\n      }\n    },\n    \"ratified_operatives\": {\n      \"bracket_screen_s\": \"0.010818\",\n      \"preflight_level_screen_s\": \"0.033558756679900\",\n      \"max_budgetable_excess_s\": \"0.001275166090593858\",\n      \"maximum_budgetable_drift_s\": \"0.012093166090593858\",\n      \"allowance_rule\": \"max(observed_drift_s,bracket_screen_s)\",\n      \"operative_bound_rule\": \"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s\",\n      \"embedding_count\": 1\n    }\n  },\n  \"derivation_sha256\": \"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02\"\n}\n","artifact_file_sha256":"316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985","derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","record":"issued-acceptance-artifact","schema_version":"joulewise.calibration_acceptance_issuance_dry_run.v1"}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-refusal-as-result.md:1368:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:1254:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:7180:    43	ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:7182:    45	    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:7326:   189	    if role == "schema_fixture_unissued":
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:7608:   470	        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:8442:   949	    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:8541:  1048	    if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:15805:{"artifact":{"acceptance_id":"d079_calibration_acceptance_v2_n19","artifact_role":"issued","backfill_candidate":{"candidate_inventory":{"ordinary-invalid":6,"systematic-invalid":2,"valid":30},"production_issuance_blocked":false,"required_verification":"complete: lead-owned raw-physics and artifact-hash verification","status":"issued","superseded_id_only_blind_exclusions":["20260726T000039-491995f3","20260726T031222-e0ce33f5"]},"decimal_derivation":{"numeric_semantics":"decimal_source_lexemes","presentation_values":{"d079_range_12_places_s":{"label":"presentation_only_not_a_comparator","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000001 s","value":"0.010817749309"}},"ratified_operatives":{"allowance_rule":"max(observed_drift_s,bracket_screen_s)","bracket_screen_s":"0.010818","embedding_count":1,"max_budgetable_excess_s":"0.001275166090593858","maximum_budgetable_drift_s":"0.012093166090593858","operative_bound_rule":"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s","preflight_level_screen_s":"0.033558756679900"},"rounding":{"mode":"ROUND_HALF_EVEN","operative_bracket_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000001","source":"decimal_derivation.source_statistics.range_s","value_s":"0.010818"},"preflight_level_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000000000000001","source":"decimal_derivation.source_statistics.maximum_s","value_s":"0.033558756679900"}},"source_statistics":{"maximum_member_id":"20260722T222332-901c5c13","maximum_s":"0.03355875667989999","mean_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.026950033977532761"},"minimum_member_id":"20260722T215127-eeef661a","minimum_s":"0.022741007370546462","prediction_95_two_draw_s":"0.008826584887500717","prediction_99_two_draw_s":"0.012093166090593858","range_s":"0.010817749309353528","sample_sd_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.002970761365307205"}}},"decision_ids":["D-102","D-109"],"derivation_corpus":{"members":[{"b_fiducial_s":"0.03018980442653224","instrument_evidence_sha256":"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a","manifest_sha256":"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7","member_id":"20260722T145535-e941c821","source_directory":"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821"},{"b_fiducial_s":"0.026300679324099796","instrument_evidence_sha256":"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f","manifest_sha256":"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041","member_id":"20260722T194118-9dc0749d","source_directory":"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d"},{"b_fiducial_s":"0.03312014638436772","instrument_evidence_sha256":"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea","manifest_sha256":"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1","member_id":"20260722T214220-1acdbbc0","source_directory":"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0"},{"b_fiducial_s":"0.022741007370546462","instrument_evidence_sha256":"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024","manifest_sha256":"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5","member_id":"20260722T215127-eeef661a","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a"},{"b_fiducial_s":"0.03355875667989999","instrument_evidence_sha256":"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe","manifest_sha256":"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54","member_id":"20260722T222332-901c5c13","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13"},{"b_fiducial_s":"0.027654085293084385","instrument_evidence_sha256":"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7","manifest_sha256":"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70","member_id":"20260722T232509-82642517","source_directory":"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517"},{"b_fiducial_s":"0.024753340330112727","instrument_evidence_sha256":"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c","manifest_sha256":"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d","member_id":"20260723T023058-8732d1c9","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9"},{"b_fiducial_s":"0.025964638697819786","instrument_evidence_sha256":"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c","manifest_sha256":"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02","member_id":"20260723T052051-d9358c8a","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a"},{"b_fiducial_s":"0.027262160888545217","instrument_evidence_sha256":"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd","manifest_sha256":"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c","member_id":"20260723T183306-4ce692b4","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4"},{"b_fiducial_s":"0.024593263907495888","instrument_evidence_sha256":"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6","manifest_sha256":"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec","member_id":"20260723T194632-d04e038e","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e"},{"b_fiducial_s":"0.025305226022515448","instrument_evidence_sha256":"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7","manifest_sha256":"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005","member_id":"20260723T195730-bc4ba14a","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a"},{"b_fiducial_s":"0.027702588281732055","instrument_evidence_sha256":"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a","manifest_sha256":"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319","member_id":"20260723T221449-e9ae755e","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e"},{"b_fiducial_s":"0.026173651901677253","instrument_evidence_sha256":"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803","manifest_sha256":"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe","member_id":"20260723T223406-314f6d9e","source_directory":"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e"},{"b_fiducial_s":"0.02547564583006129","instrument_evidence_sha256":"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736","manifest_sha256":"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e","member_id":"20260724T014109-57844352","source_directory":"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352"},{"b_fiducial_s":"0.023241581438247116","instrument_evidence_sha256":"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be","manifest_sha256":"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9","member_id":"20260725T005132-a64711b7","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7"},{"b_fiducial_s":"0.028891617940876635","instrument_evidence_sha256":"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5","manifest_sha256":"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0","member_id":"20260725T011533-0b5ec77c","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c"},{"b_fiducial_s":"0.029197264796726408","instrument_evidence_sha256":"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da","manifest_sha256":"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185","member_id":"20260725T022712-0a9534f5","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5"},{"b_fiducial_s":"0.024879191521227362","instrument_evidence_sha256":"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e","manifest_sha256":"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a","member_id":"20260725T030533-d3f076e5","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5"},{"b_fiducial_s":"0.025045994537554683","instrument_evidence_sha256":"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2","manifest_sha256":"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704","member_id":"20260725T060617-97c5cba6","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6"}],"n":19,"selection":"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch"},"derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","identity_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100},"issuance":{"claim_eligible":true,"reason":"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff","status":"issued"},"ledger_cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","role":"issued_acceptance_baseline","sequence":76},"prior_observation_set":{"content_identity_method":"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))","cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","sequence":76},"epoch_catalog":{"d079_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100}},"observations":[{"attempt_id":"20260722T145535-e941c821","content_id":"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T194118-9dc0749d","content_id":"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T213749-563b9849","content_id":"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T214220-1acdbbc0","content_id":"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T215127-eeef661a","content_id":"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T222332-901c5c13","content_id":"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T232509-82642517","content_id":"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T023058-8732d1c9","content_id":"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T052051-d9358c8a","content_id":"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T183306-4ce692b4","content_id":"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T194632-d04e038e","content_id":"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T195730-bc4ba14a","content_id":"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T221449-e9ae755e","content_id":"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T223406-314f6d9e","content_id":"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260724T014109-57844352","content_id":"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T005132-a64711b7","content_id":"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T011533-0b5ec77c","content_id":"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T022712-0a9534f5","content_id":"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T030533-d3f076e5","content_id":"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T055825-b10cb348","content_id":"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T060617-97c5cba6","content_id":"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T000039-491995f3","content_id":"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710","disposition":"systematic-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T031222-e0ce33f5","content_id":"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225227-1f550773","content_id":"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225920-ab4272f5","content_id":"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T015824-45feb516","content_id":"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T020611-4a409a30","content_id":"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T050047-95e2f87e","content_id":"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260729T204105-39d25f8a","content_id":"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T014035-124df355","content_id":"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T210703-f76b5771","content_id":"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T012210-374020b6","content_id":"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T161713-b8b08280","content_id":"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T214355-126fc2ab","content_id":"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010113-e859f3aa","content_id":"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010805-ff3fdc88","content_id":"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T014059-8c3bfe9e","content_id":"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T064830-c76f5d1c","content_id":"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448","disposition":"systematic-invalid","epoch_id":"d079_epoch"}]},"prospective_rederivation":{"calendar_expiry":null,"estimator_code_sha256":{"joulewise/adapters/powermetrics.py":"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca","joulewise/powermetrics_fiducial.py":"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3","joulewise/reduce.py":"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615","joulewise/uncertainty_evidence.py":"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7"},"protocol_sha256":"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1","trigger_observation_rule":"judge_under_prior_artifact_never_self_fit","triggers":["identity_field_change","protocol_or_estimator_byte_change","new_valid_same_identity_capture_expands_observed_range","corpus_doubles_from_19_to_38","new_systematic_failure_challenges_preflight_screen"]},"schema_version":"joulewise.calibration_acceptance_bound.v2"},"artifact_file_content":"{\n  \"schema_version\": \"joulewise.calibration_acceptance_bound.v2\",\n  \"acceptance_id\": \"d079_calibration_acceptance_v2_n19\",\n  \"decision_ids\": [\n    \"D-102\",\n    \"D-109\"\n  ],\n  \"artifact_role\": \"issued\",\n  \"issuance\": {\n    \"status\": \"issued\",\n    \"claim_eligible\": true,\n    \"reason\": \"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff\"\n  },\n  \"ledger_cutoff\": {\n    \"sequence\": 76,\n    \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n    \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\",\n    \"role\": \"issued_acceptance_baseline\"\n  },\n  \"identity_epoch\": {\n    \"os_build\": \"25F84\",\n    \"hardware_model\": \"Mac15,9\",\n    \"power_policy\": \"ac_high_power\",\n    \"sampling_interval_ms\": 100,\n    \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n    \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n  },\n  \"prospective_rederivation\": {\n    \"calendar_expiry\": null,\n    \"trigger_observation_rule\": \"judge_under_prior_artifact_never_self_fit\",\n    \"triggers\": [\n      \"identity_field_change\",\n      \"protocol_or_estimator_byte_change\",\n      \"new_valid_same_identity_capture_expands_observed_range\",\n      \"corpus_doubles_from_19_to_38\",\n      \"new_systematic_failure_challenges_preflight_screen\"\n    ],\n    \"protocol_sha256\": \"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1\",\n    \"estimator_code_sha256\": {\n      \"joulewise/powermetrics_fiducial.py\": \"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3\",\n      \"joulewise/uncertainty_evidence.py\": \"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7\",\n      \"joulewise/adapters/powermetrics.py\": \"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca\",\n      \"joulewise/reduce.py\": \"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615\"\n    }\n  },\n  \"derivation_corpus\": {\n    \"selection\": \"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch\",\n    \"n\": 19,\n    \"members\": [\n      {\n        \"member_id\": \"20260722T145535-e941c821\",\n        \"source_directory\": \"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821\",\n        \"b_fiducial_s\": \"0.03018980442653224\",\n        \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n        \"instrument_evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\"\n      },\n      {\n        \"member_id\": \"20260722T194118-9dc0749d\",\n        \"source_directory\": \"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d\",\n        \"b_fiducial_s\": \"0.026300679324099796\",\n        \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n        \"instrument_evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\"\n      },\n      {\n        \"member_id\": \"20260722T214220-1acdbbc0\",\n        \"source_directory\": \"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0\",\n        \"b_fiducial_s\": \"0.03312014638436772\",\n        \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n        \"instrument_evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\"\n      },\n      {\n        \"member_id\": \"20260722T215127-eeef661a\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a\",\n        \"b_fiducial_s\": \"0.022741007370546462\",\n        \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n        \"instrument_evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\"\n      },\n      {\n        \"member_id\": \"20260722T222332-901c5c13\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13\",\n        \"b_fiducial_s\": \"0.03355875667989999\",\n        \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n        \"instrument_evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\"\n      },\n      {\n        \"member_id\": \"20260722T232509-82642517\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517\",\n        \"b_fiducial_s\": \"0.027654085293084385\",\n        \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n        \"instrument_evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\"\n      },\n      {\n        \"member_id\": \"20260723T023058-8732d1c9\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9\",\n        \"b_fiducial_s\": \"0.024753340330112727\",\n        \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n        \"instrument_evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\"\n      },\n      {\n        \"member_id\": \"20260723T052051-d9358c8a\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a\",\n        \"b_fiducial_s\": \"0.025964638697819786\",\n        \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n        \"instrument_evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\"\n      },\n      {\n        \"member_id\": \"20260723T183306-4ce692b4\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4\",\n        \"b_fiducial_s\": \"0.027262160888545217\",\n        \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n        \"instrument_evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\"\n      },\n      {\n        \"member_id\": \"20260723T194632-d04e038e\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e\",\n        \"b_fiducial_s\": \"0.024593263907495888\",\n        \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n        \"instrument_evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\"\n      },\n      {\n        \"member_id\": \"20260723T195730-bc4ba14a\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a\",\n        \"b_fiducial_s\": \"0.025305226022515448\",\n        \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n        \"instrument_evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\"\n      },\n      {\n        \"member_id\": \"20260723T221449-e9ae755e\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e\",\n        \"b_fiducial_s\": \"0.027702588281732055\",\n        \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n        \"instrument_evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\"\n      },\n      {\n        \"member_id\": \"20260723T223406-314f6d9e\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e\",\n        \"b_fiducial_s\": \"0.026173651901677253\",\n        \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n        \"instrument_evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\"\n      },\n      {\n        \"member_id\": \"20260724T014109-57844352\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352\",\n        \"b_fiducial_s\": \"0.02547564583006129\",\n        \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n        \"instrument_evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\"\n      },\n      {\n        \"member_id\": \"20260725T005132-a64711b7\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7\",\n        \"b_fiducial_s\": \"0.023241581438247116\",\n        \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n        \"instrument_evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\"\n      },\n      {\n        \"member_id\": \"20260725T011533-0b5ec77c\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c\",\n        \"b_fiducial_s\": \"0.028891617940876635\",\n        \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n        \"instrument_evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\"\n      },\n      {\n        \"member_id\": \"20260725T022712-0a9534f5\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5\",\n        \"b_fiducial_s\": \"0.029197264796726408\",\n        \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n        \"instrument_evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\"\n      },\n      {\n        \"member_id\": \"20260725T030533-d3f076e5\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5\",\n        \"b_fiducial_s\": \"0.024879191521227362\",\n        \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n        \"instrument_evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\"\n      },\n      {\n        \"member_id\": \"20260725T060617-97c5cba6\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6\",\n        \"b_fiducial_s\": \"0.025045994537554683\",\n        \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n        \"instrument_evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\"\n      }\n    ]\n  },\n  \"prior_observation_set\": {\n    \"cutoff\": {\n      \"sequence\": 76,\n      \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n      \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\"\n    },\n    \"content_identity_method\": \"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))\",\n    \"epoch_catalog\": {\n      \"d079_epoch\": {\n        \"os_build\": \"25F84\",\n        \"hardware_model\": \"Mac15,9\",\n        \"power_policy\": \"ac_high_power\",\n        \"sampling_interval_ms\": 100,\n        \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n        \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n      }\n    },\n    \"observations\": [\n      {\n        \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T145535-e941c821\"\n      },\n      {\n        \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T194118-9dc0749d\"\n      },\n      {\n        \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260722T213749-563b9849\"\n      },\n      {\n        \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T214220-1acdbbc0\"\n      },\n      {\n        \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T215127-eeef661a\"\n      },\n      {\n        \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T222332-901c5c13\"\n      },\n      {\n        \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T232509-82642517\"\n      },\n      {\n        \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T023058-8732d1c9\"\n      },\n      {\n        \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T052051-d9358c8a\"\n      },\n      {\n        \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T183306-4ce692b4\"\n      },\n      {\n        \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T194632-d04e038e\"\n      },\n      {\n        \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T195730-bc4ba14a\"\n      },\n      {\n        \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T221449-e9ae755e\"\n      },\n      {\n        \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T223406-314f6d9e\"\n      },\n      {\n        \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260724T014109-57844352\"\n      },\n      {\n        \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T005132-a64711b7\"\n      },\n      {\n        \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T011533-0b5ec77c\"\n      },\n      {\n        \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T022712-0a9534f5\"\n      },\n      {\n        \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T030533-d3f076e5\"\n      },\n      {\n        \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260725T055825-b10cb348\"\n      },\n      {\n        \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T060617-97c5cba6\"\n      },\n      {\n        \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260726T000039-491995f3\"\n      },\n      {\n        \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T031222-e0ce33f5\"\n      },\n      {\n        \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260726T225227-1f550773\"\n      },\n      {\n        \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T225920-ab4272f5\"\n      },\n      {\n        \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T015824-45feb516\"\n      },\n      {\n        \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T020611-4a409a30\"\n      },\n      {\n        \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T050047-95e2f87e\"\n      },\n      {\n        \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260729T204105-39d25f8a\"\n      },\n      {\n        \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T014035-124df355\"\n      },\n      {\n        \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T210703-f76b5771\"\n      },\n      {\n        \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T012210-374020b6\"\n      },\n      {\n        \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T161713-b8b08280\"\n      },\n      {\n        \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260731T214355-126fc2ab\"\n      },\n      {\n        \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010113-e859f3aa\"\n      },\n      {\n        \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010805-ff3fdc88\"\n      },\n      {\n        \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260801T014059-8c3bfe9e\"\n      },\n      {\n        \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260801T064830-c76f5d1c\"\n      }\n    ]\n  },\n  \"backfill_candidate\": {\n    \"status\": \"issued\",\n    \"candidate_inventory\": {\n      \"ordinary-invalid\": 6,\n      \"systematic-invalid\": 2,\n      \"valid\": 30\n    },\n    \"production_issuance_blocked\": false,\n    \"required_verification\": \"complete: lead-owned raw-physics and artifact-hash verification\",\n    \"superseded_id_only_blind_exclusions\": [\n      \"20260726T000039-491995f3\",\n      \"20260726T031222-e0ce33f5\"\n    ]\n  },\n  \"decimal_derivation\": {\n    \"numeric_semantics\": \"decimal_source_lexemes\",\n    \"source_statistics\": {\n      \"minimum_s\": \"0.022741007370546462\",\n      \"minimum_member_id\": \"20260722T215127-eeef661a\",\n      \"maximum_s\": \"0.03355875667989999\",\n      \"maximum_member_id\": \"20260722T222332-901c5c13\",\n      \"range_s\": \"0.010817749309353528\",\n      \"mean_presentation_s\": {\n        \"value\": \"0.026950033977532761\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"sample_sd_presentation_s\": {\n        \"value\": \"0.002970761365307205\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"prediction_95_two_draw_s\": \"0.008826584887500717\",\n      \"prediction_99_two_draw_s\": \"0.012093166090593858\"\n    },\n    \"presentation_values\": {\n      \"d079_range_12_places_s\": {\n        \"value\": \"0.010817749309\",\n        \"label\": \"presentation_only_not_a_comparator\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000001 s\"\n      }\n    },\n    \"rounding\": {\n      \"mode\": \"ROUND_HALF_EVEN\",\n      \"operative_bracket_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.range_s\",\n        \"quantum_s\": \"0.000001\",\n        \"value_s\": \"0.010818\",\n        \"numeric_role\": \"operative_comparator\"\n      },\n      \"preflight_level_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.maximum_s\",\n        \"quantum_s\": \"0.000000000000001\",\n        \"value_s\": \"0.033558756679900\",\n        \"numeric_role\": \"operative_comparator\"\n      }\n    },\n    \"ratified_operatives\": {\n      \"bracket_screen_s\": \"0.010818\",\n      \"preflight_level_screen_s\": \"0.033558756679900\",\n      \"max_budgetable_excess_s\": \"0.001275166090593858\",\n      \"maximum_budgetable_drift_s\": \"0.012093166090593858\",\n      \"allowance_rule\": \"max(observed_drift_s,bracket_screen_s)\",\n      \"operative_bound_rule\": \"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s\",\n      \"embedding_count\": 1\n    }\n  },\n  \"derivation_sha256\": \"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02\"\n}\n","artifact_file_sha256":"316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985","derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","record":"issued-acceptance-artifact","schema_version":"joulewise.calibration_acceptance_issuance_dry_run.v1"}
docs/process_traces/2026-08-07-d117-u-units/U3-DELTA2-VERDICT.md:6492:   457	        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
docs/process_traces/2026-08-07-d117-u-units/U3-DELTA2-VERDICT.md:9849:            "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/process_traces/2026-08-07-d117-u-units/U3-DELTA2-VERDICT.md:10301:   969	            "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:2439:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5712:docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:6:{"parentUuid":"5b9cfd00-18f5-4ade-a27c-f8e74632c36a","isSidechain":true,"promptId":"5c9e22f4-f072-4d90-ba34-2746cfa6a676","agentId":"ad24a0f43262b600c","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_01Dudks6Z24dNhWCgWDZM5Q3","type":"tool_result","content":"1\t# COLD-EYES ISSUANCE PACKET — D-079 calibration acceptance artifact + ledger genesis import\n2\t\n3\tYou are a COLD reviewer: no prior context from the session that produced\n4\tthis. Rule under rule-11 on whether this IRREVERSIBLE issuance is correct\n5\tto EXECUTE. The human principal (Ed) has authorized the issuance decision;\n6\tyour job is NOT whether to issue but whether the assembled artifact is\n7\tCORRECT — mechanical/correctness errors a loop-immersed agent can't see.\n8\tVerdict: PROCEED or HOLD (with the specific defect). Read primary sources\n9\tyourself; do not trust this packet's numbers without checking.\n10\t\n11\t## What is about to happen (irreversible)\n12\t\n13\t1. `scripts/calibration_ledger_bootstrap.py --execute` writes the real\n14\t   `configs/calibration/calibration_observation_ledger` (currently\n15\t   absent; head pin at genesis seq 0 / all-zeros).\n16\t2. The printed head pin (seq 76, head below) is committed to\n17\t   `configs/calibration/calibration_ledger_head.json`.\n18\t3. `configs/calibration/calibration_acceptance_d079_v2.json` flips\n19\t   `artifact_role` schema_fixture_unissued → issued, cutoff = (seq 76,\n20\t   head), prior_observation_set filled per the ledger's import-marked\n21\t   prefix.\n22\t4. A decision-log entry (D-116) records the issuance.\n23\t\n24\tThis artifact is the authentication anchor for ALL future floor-mint\n25\tclaims. An error here silently taints every downstream claim.\n26\t\n27\t## Assembled facts (VERIFY each against the cited primary source)\n28\t\n29\t- Disposition table: `/private/tmp/d079-ledger-dispositions.json`,\n30\t  sha256 `5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a`,\n31\t  38 members = 30 valid / 2 systematic-invalid / 6 ordinary-invalid.\n32\t- The 2 systematic-invalid members (`20260726T000039-491995f3`,\n33\t  `20260801T064830-c76f5d1c`) were lead-ruled systematic (bounds exceed\n34\t  the 0.033558756679900 preflight screen; D-102 names the first a\n35\t  systematic failure). VERIFY this ruling against\n36\t  `docs/decision_log.md` D-102 and the verification report's per-member\n37\t  physics (report: `docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md`).\n38\t- Custody manifest: `/private/tmp/d079-custody-manifest.lead.json`,\n39\t  sha256 `99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078`,\n40\t  lead-regenerated (byte-identical to the delegated generation).\n41\t- Candidate head: `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`\n42\t  at sequence 76. REPRODUCE it yourself with a dry-run (read-only,\n43\t  writes nothing):\n44\t  `python3 scripts/calibration_ledger_bootstrap.py --disposition-table /private/tmp/d079-ledger-dispositions.json --expected-table-sha256 5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a --custody-manifest /private/tmp/d079-custody-manifest.lead.json --expected-custody-manifest-sha256 99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078 --checkout-root /Users/edr`\n45\t- derivation_corpus stays n=19, derivation_sha256\n46\t  `3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d`\n47\t  (unchanged; the issuance edits the acceptance file so its OWN file\n48\t  hash changes — that is expected, the n=19 statistics do not).\n49\t- Binding requirements: D-109 R1.4 + R2.1-8 (docs/decision_log.md).\n50\t- The bootstrap code passed a 4-round adversarial gaunttet ending in an\n51\t  ACCEPT delta audit (record:\n52\t  `/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/ledgerboot-delta4.md`).\n53\t\n54\t## Your checks (rule and report each)\n55\t\n56\t1. Reproduce the head. Does it equal 08456d50…@76? If not → HOLD.\n57\t2. Spot-verify the B1 disposition ruling: are the two systematic-invalid\n58\t   members genuinely bound-exceeding per the raw physics in the\n59\t   verification report, and is systematic-invalid the correct ledger\n60\t   disposition (vs valid) under D-102's screen? A wrong disposition\n61\t   changes the head and the corpus-doubling count.\n62\t3. D-109 R2 conformance of the plan: prior_observation_set completeness\n63\t   (all 38 content-distinct, epoch+disposition), content identity from\n64\t   primary-byte hashes, the import marker excluded from post-cutoff\n65\t   populations, cutoff = exact (seq, head).\n66\t4. Any reason the genesis import should NOT be the authoritative ledger\n67\t   (root-universe completeness now that custody is manifest-pinned;\n68\t   the manifest references iCloud-backup copies for 22 members — is that\n69\t   acceptable provenance for the authoritative ledger, or must those\n70\t   copies live in the primary checkout first?).\n71\t5. Anything else that would make this issuance unsound.\n72\t\n73\t## Output\n74\t\n75\tA clear PROCEED or HOLD with per-check findings and the reproduced head.\n76\tIf HOLD, name the exact defect and the primary evidence. This is the\n77\tlast check before an irreversible write to the claim-authentication\n78\tanchor — be exacting.\n79\t"}]},"uuid":"a105451f-04e9-4b7d-ac9a-5f72f990ff91","timestamp":"2026-08-06T08:35:11.582Z","toolUseResult":{"type":"text","file":{"filePath":"/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/d079-issuance-packet.md","content":"# COLD-EYES ISSUANCE PACKET — D-079 calibration acceptance artifact + ledger genesis import\n\nYou are a COLD reviewer: no prior context from the session that produced\nthis. Rule under rule-11 on whether this IRREVERSIBLE issuance is correct\nto EXECUTE. The human principal (Ed) has authorized the issuance decision;\nyour job is NOT whether to issue but whether the assembled artifact is\nCORRECT — mechanical/correctness errors a loop-immersed agent can't see.\nVerdict: PROCEED or HOLD (with the specific defect). Read primary sources\nyourself; do not trust this packet's numbers without checking.\n\n## What is about to happen (irreversible)\n\n1. `scripts/calibration_ledger_bootstrap.py --execute` writes the real\n   `configs/calibration/calibration_observation_ledger` (currently\n   absent; head pin at genesis seq 0 / all-zeros).\n2. The printed head pin (seq 76, head below) is committed to\n   `configs/calibration/calibration_ledger_head.json`.\n3. `configs/calibration/calibration_acceptance_d079_v2.json` flips\n   `artifact_role` schema_fixture_unissued → issued, cutoff = (seq 76,\n   head), prior_observation_set filled per the ledger's import-marked\n   prefix.\n4. A decision-log entry (D-116) records the issuance.\n\nThis artifact is the authentication anchor for ALL future floor-mint\nclaims. An error here silently taints every downstream claim.\n\n## Assembled facts (VERIFY each against the cited primary source)\n\n- Disposition table: `/private/tmp/d079-ledger-dispositions.json`,\n  sha256 `5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a`,\n  38 members = 30 valid / 2 systematic-invalid / 6 ordinary-invalid.\n- The 2 systematic-invalid members (`20260726T000039-491995f3`,\n  `20260801T064830-c76f5d1c`) were lead-ruled systematic (bounds exceed\n  the 0.033558756679900 preflight screen; D-102 names the first a\n  systematic failure). VERIFY this ruling against\n  `docs/decision_log.md` D-102 and the verification report's per-member\n  physics (report: `docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md`).\n- Custody manifest: `/private/tmp/d079-custody-manifest.lead.json`,\n  sha256 `99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078`,\n  lead-regenerated (byte-identical to the delegated generation).\n- Candidate head: `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`\n  at sequence 76. REPRODUCE it yourself with a dry-run (read-only,\n  writes nothing):\n  `python3 scripts/calibration_ledger_bootstrap.py --disposition-table /private/tmp/d079-ledger-dispositions.json --expected-table-sha256 5da820aa5c649e5991b934230cd75e8c99daa8dcea22f3f1b3e3db89c80f2a6a --custody-manifest /private/tmp/d079-custody-manifest.lead.json --expected-custody-manifest-sha256 99cbf3df7aef3b81839f40272a529eb137bf2f21276e2a1d07788c764035f078 --checkout-root /Users/edr`\n- derivation_corpus stays n=19, derivation_sha256\n  `3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d`\n  (unchanged; the issuance edits the acceptance file so its OWN file\n  hash changes — that is expected, the n=19 statistics do not).\n- Binding requirements: D-109 R1.4 + R2.1-8 (docs/decision_log.md).\n- The bootstrap code passed a 4-round adversarial gaunttet ending in an\n  ACCEPT delta audit (record:\n  `/private/tmp/claude-501/-Users-edr-code-JouleWise/df9ee343-36aa-42b0-8bbf-cc7598ecfdb3/scratchpad/ledgerboot-delta4.md`).\n\n## Your checks (rule and report each)\n\n1. Reproduce the head. Does it equal 08456d50…@76? If not → HOLD.\n2. Spot-verify the B1 disposition ruling: are the two systematic-invalid\n   members genuinely bound-exceeding per the raw physics in the\n   verification report, and is systematic-invalid the correct ledger\n   disposition (vs valid) under D-102's screen? A wrong disposition\n   changes the head and the corpus-doubling count.\n3. D-109 R2 conformance of the plan: prior_observation_set completeness\n   (all 38 content-distinct, epoch+disposition), content identity from\n   primary-byte hashes, the import marker excluded from post-cutoff\n   populations, cutoff = exact (seq, head).\n4. Any reason the genesis import should NOT be the authoritative ledger\n   (root-universe completeness now that custody is manifest-pinned;\n   the manifest references iCloud-backup copies for 22 members — is that\n   acceptable provenance for the authoritative ledger, or must those\n   copies live in the primary checkout first?).\n5. Anything else that would make this issuance unsound.\n\n## Output\n\nA clear PROCEED or HOLD with per-check findings and the reproduced head.\nIf HOLD, name the exact defect and the primary evidence. This is the\nlast check before an irreversible write to the claim-authentication\nanchor — be exacting.\n","numLines":79,"startLine":1,"totalLines":79}},"sourceToolAssistantUUID":"5b9cfd00-18f5-4ade-a27c-f8e74632c36a","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:2440:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5740:docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:59:{"parentUuid":"07b9c6e1-cf97-433c-a130-aed8bf8cac71","isSidechain":true,"agentId":"ad24a0f43262b600c","message":{"model":"claude-opus-4-8","id":"msg_011CdmCDLdurdj31n8c7k4fH","type":"message","role":"assistant","content":[{"type":"text","text":"All checks complete. Let me record the final confirmations: only members 22 & 38 among the VERIFIED-VALID set exceed the screen (no missed systematic call), and the derivation hash is unchanged.\n\nVerdict follows.\n\n---\n\n**VERDICT: PROCEED** — with two advisory notes for magistrate awareness (neither blocks; both are correctness-neutral or conservative).\n\n**Reproduced head (dry-run, wrote nothing):**\n`08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7` at sequence 76. Bit-for-bit equal to the packet's candidate head. The dry-run summary self-reports `executed:false`, `outcome:planned`, `receipt_count:76`, and the head-pin content `{sequence:76, head_digest:08456d50…, ledger_schema:joulewise.calibration_observation_ledger.v1}`. Both input digests matched (`5da820aa…` table, `99cbf3df…` custody manifest).\n\n**Per-check findings:**\n\n- **Check 1 — Head reproduction: PASS.** Reproduced exactly. The head embeds the iCloud absolute custody locators and the systematic-invalid disposition on the final (seq-76) receipt, so byte-identity of the head confirms the disposition ruling, the ordering, the custody selection, and all 38 authenticated artifact hashes simultaneously. (Note: this head differs from the two \"illustrative\" heads in the verification report — `cb410907…` and `8e80b6e9…` — because those used an unauthorized synthetic reservation/finalization assumption; the report explicitly labeled them non-authoritative. The bootstrap's `historical-import-v1` transaction is the authoritative computation.)\n\n- **Check 2 — B1 disposition ruling: PASS (ruling is correct and conservative).** The two systematic-invalid members are `20260726T000039-491995f3` (bound 0.035435840879704805) and `20260801T064830-c76f5d1c` (bound 0.0350400833260715). Both exceed the ratified preflight screen 0.033558756679900. Primary corroboration: `docs/decision_log.md` (D-102, ~lines 6298-6301) states verbatim that window B's pre-calibration `0.035435840879704805 s (verified in primary evidence) exceeds the pre-flight level screen, and D-079 cl.2's systematic failure is never budgetable` — that is member 491995f3 by exact value. The verification report replays both as physically VALID but bound-exceeding, and the production writer (`validate_powermetrics_fiducial.py:664-671`) maps a valid-but-over-screen capture to systematic-invalid. Selecting systematic-invalid (vs the candidate-tool's \"valid\") is the doctrine-consistent choice. I independently confirmed that among all VERIFIED-VALID members, exactly these two exceed the screen — the max remaining valid bound is member `901c5c13` at 0.03355875667989999, just under the screen (that member is the corpus ceiling). No missed systematic call; no over-flagging.\n\n- **Check 3 — D-109 R2 conformance: PASS.** Disposition table = 38 members, all content-distinct (38 unique content_ids), single identity epoch at table level matching d079_epoch (os_build 25F84, Mac15,9, ac_high_power, 100 ms, joint_loss_sublevel_interval_branch_v2, powermetrics_pulse_fiducial_v3). Table content_ids and dispositions match the verification report's per-member exactly, with only members 22 and 38 flipped to systematic-invalid (R2.7's raw-physics ruling superseding the candidate labels — as R2.7 mandates). Final counts 30 valid / 2 systematic-invalid / 6 ordinary-invalid, all in the allowed disposition set (R2.3 records systematic + ordinary + valid separately). Cutoff = exact receipt (seq 76 = member 38's finalization) satisfying R2.1. derivation_corpus stays n=19 with derivation_sha256 `3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d` (verified in the current acceptance file — unchanged). Reservation receipts carry null content_id / pending disposition, so they cannot leak into the post-cutoff \"new\" subtraction.\n\n- **Check 4 — genesis-import authoritativeness / iCloud provenance: ACCEPTABLE.** The raw instrument-evidence run trees are **git-ignored** in the checkout (`git check-ignore` matches `runs*/instrument_validation`; zero tracked files under any `instrument_validation`). Raw evidence is never version-controlled by repo convention — the iCloud `com~apple~CloudDocs/JouleWise-backup` tree is the designated `raw_archive` (verification-report inventory). All 38 custody dirs currently exist and their bytes authenticate (the head would not reproduce otherwise). Integrity of the claim-authentication anchor rests on the **committed hash chain** (ledger + head-pin in git), which binds every artifact_sha256; the `custody_locator` is a provenance pointer, not the integrity root. Since the in-checkout copies are themselves untracked working files (same durability class), requiring them \"in the primary checkout first\" would add nothing durable. So iCloud provenance is acceptable for the authoritative ledger.\n\n- **Check 5 — other soundness: PASS.** Current pre-issuance state is consistent with the packet: head pin = genesis seq 0 / all-zeros; ledger file absent; acceptance `artifact_role = schema_fixture_unissued`, no cutoff.\n\n**Advisory notes (non-blocking):**\n\n1. **Packet undercounts custody provenance.** The packet's check-4 says \"iCloud-backup copies for 22 of the 38 members.\" In fact **all 38** custody locators are iCloud `JouleWise-backup` paths (0 point into the checkout). This does not change the verdict — the provenance assessment above applies to all 38 — but the \"22\" figure in the packet is inaccurate and should not be relied on in the D-116 log entry.\n\n2. **D-109 R2.8's literal \"six further\" is superseded to \"eight further.\"** R2.8 as written stated the corpus-doubling consequence as \"six further valid observations trigger re-derivation,\" predicated on the candidate-inventory 32-valid count. The (correct) systematic-invalid ruling makes it 30 valid → eight further needed. This is internally consistent because R2.7 explicitly subordinates the candidate inventory to the raw-physics ruling, and both counts yield `trigger_now = false` today — no claim-authentication consequence. Worth a one-line note in the issuance record so the \"six\" in R2.8's prose isn't later mistaken for a live count.\n\nNothing found rises to a HOLD. The irreversible write is correct to execute."}],"stop_reason":"end_turn","stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":6190,"cache_read_input_tokens":72704,"output_tokens":4454,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":6190},"inference_geo":"not_available","iterations":[{"input_tokens":2,"output_tokens":4454,"cache_read_input_tokens":72704,"cache_creation_input_tokens":6190,"cache_creation":{"ephemeral_5m_input_tokens":6190,"ephemeral_1h_input_tokens":0},"type":"message"}],"speed":"standard"},"diagnostics":null},"requestId":"req_011CdmCDKedQPCyg9RpRMtsW","attributionAgent":"general-purpose","type":"assistant","uuid":"20a22ec2-b8ee-45c1-ab63-99153ea692ed","timestamp":"2026-08-06T08:40:51.650Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:2698:docs/process_traces/2026-08-07-night-hardening/AUDIT-RUNNER.md:15884:docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:111:{"parentUuid":"47eb3b6c-e1d3-4e09-98c4-9b1d407df89d","isSidechain":true,"agentId":"a46e6644985dd75fd","message":{"model":"claude-opus-4-8","id":"msg_011CdmNPRgxc2Avvid6j8SgY","type":"message","role":"assistant","content":[{"type":"text","text":"Verdict determined. Compiling the cold-gate report.\n\n## COLD-GATE #2 VERDICT: **HOLD** — narrow, on the OPERATION only; artifact CONTENT and head are fully verified PROCEED-grade.\n\nI independently reproduced every load-bearing value from primary sources (no reliance on prior reviewers). Content passes cleanly; the HOLD is on a single unstated operational precondition that, taken as the packet describes it, bricks the claim anchor.\n\n### Checks that PASS (independently verified)\n\n- **File identity.** REVIEW.json SHA-256 = `316113960c59…8985`, matches the packet, and equals the impl consumer's `ISSUED_ACCEPTANCE_BOUND_SHA256` byte pin exactly (`joulewise/calibration_bracketing.py:56` on `impl/issuance-consumer`).\n- **Head reproduced from scratch.** Ran the bootstrap dry-run against the ruled disposition table (`/private/tmp/d079-ledger-dispositions.json`, sha `5da820aa…`) and custody manifest (`/private/tmp/d079-custody-manifest.lead.json`, sha `99cbf3df…`, both shas as cited). Result: `final_sequence=76`, `head_digest=08456d5076c18a…094d7` — exact match to the artifact's `ledger_cutoff` and `prior_observation_set.cutoff`. Final receipt (seq 76) = `c76f5d1c`, systematic-invalid, bound `0.0350400833260715`. Custody manifest = 38 members; disposition table = 38 rows.\n- **Dispositions 30/2/6.** Table counts exactly 30 valid / 2 systematic-invalid / 6 ordinary-invalid; systematic members = `20260726T000039-491995f3`, `20260801T064830-c76f5d1c`. Table attempt_ids, dispositions, AND content_ids are byte-identical to the artifact's `prior_observation_set`.\n- **B1 ruling correct vs D-102.** Both systematic bounds (`0.035435840879704805`, `0.0350400833260715`) exceed the ratified preflight screen `0.033558756679900`; D-102 (decision_log.md:6298-6301) explicitly rules the first member's pre-cal value a systematic failure \"never budgetable.\" Ruling sound.\n- **R2.8 counting.** 30 valid < 38 → no re-derivation trigger; issuance does not self-trigger. Correct.\n- **derivation_sha256.** Recomputed `_canonical_sha256(core)` = `4f6633d5…d23f02` = the artifact's whole-artifact hash. This is the correct NEW value (prior gate's F2 resolved).\n- **derivation_corpus.** n=19, byte-identical to the ratified fixture's corpus, zero Window-B members in the threshold basis.\n- **Consumer acceptance.** `_valid_acceptance_bound()` returns **True** under the intended consumer (`impl/issuance-consumer`); `identity_epoch=d079_epoch`, `artifact_role=issued`, `claim_eligible=true`, `cutoff.role=issued_acceptance_baseline` all conform.\n\n### The HOLD (operation, blocker)\n\n**The only valid loader for these bytes lives solely on unmerged branch `impl/issuance-consumer`; the packet's described execute does not land it, and on the current `main` checkout the write bricks the anchor.**\n\n- Main HEAD `c82a463` has NO issued-artifact consumer: no `ISSUED_ACCEPTANCE_BOUND_SHA256` constant and no `role == \"issued\"` path — `calibration_bracketing.py:173` still hard-requires `artifact_role == \"schema_fixture_unissued\"`. The consumer commit `1b78902` is contained only in `impl/issuance-consumer` (local + origin), not `main`.\n- Proof of brick: running main's `_valid_acceptance_bound()` on the exact issued bytes returns **False**, and main's byte pin is still the fixture's `9a264c5…`.\n- The packet's execute enumerates: bootstrap `--execute` → head-pin commit → write issued bytes to `configs/calibration/calibration_acceptance_d079_v2.json` → D-116. It names working directory `/Users/edr/code/JouleWise` (= main) and includes **no step landing the consumer**. Executed there, it replaces a loader-valid fixture with a loader-invalid issued artifact; production acceptance then refuses the anchor (and D-109 R1.4 anti-rollback refuses on the seq-76 pin), leaving an inconsistent state. This is the same F1 class the prior cold gate's Sol contract-lens refuter HELD on (`docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md`), unresolved by the operation as described.\n\n**Remedy (no change to the reviewed bytes required):** execute the bootstrap inside the `impl/issuance-consumer` worktree and land consumer + committed head-pin (seq 76 / `08456d50…`) + issued artifact as ONE atomic merge to main (or merge the consumer to main first), then re-confirm main's `_valid_acceptance_bound()` accepts the written bytes and authenticates against `ISSUED_ACCEPTANCE_BOUND_SHA256`. Clear the HOLD by confirming co-landing; the content gate is already satisfied.\n\n### Two notes for the magistrate (neither is a content defect)\n\n1. **Packet check-1 phrasing is inaccurate, artifact is correct.** `3cece3b2…` appears nowhere in the artifact and there is no \"preserved sub-field.\" That is correct: `3cece3b2` was the *fixture's* whole-artifact `derivation_sha256`; the issued artifact's whole-artifact hash legitimately becomes `4f6633d5…`, and the consumer *requires* `derivation_sha256 == canonical(core)` — embedding `3cece3b2` would FAIL the loader. The packet's expectation here is wrong; the bytes are right.\n2. **\"No Window-B member\" is true only for the threshold basis.** The n=19 `derivation_corpus` is Window-A-only (verified). But `prior_observation_set` correctly includes 6 observations with `window_metrologyB` custody — 2 of them valid (`e0ce33f5`, `8c3bfe9e`) — as mandated by D-109 R2.3/R2.8 completeness. These are fiducial calibration observations (general machinery survives per D-113), are excluded from the frozen n=19 threshold, and do not influence the bound. By design, not a violation — flagged only because the packet's flat \"no Window-B member present\" is literally false for the completeness record.\n\nPrimary sources consulted: the REVIEW.json; `docs/decision_log.md` D-102 (6278-6337), D-109 R2 (7052-7079), D-110 (7081-7126), D-113 (7240+); `VERIFICATION-REPORT.md`; `SOL-CONTRACT-LENS-HOLD.md`; live loader code on both `main` (`joulewise/calibration_bracketing.py`) and `impl/issuance-consumer`; and a self-run bootstrap dry-run."}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":830,"cache_read_input_tokens":134085,"cache_creation":{"ephemeral_5m_input_tokens":830,"ephemeral_1h_input_tokens":0},"output_tokens":2,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmNPNUyidjFY7Zr2dTAd","attributionAgent":"general-purpose","type":"assistant","uuid":"05cc7892-a85c-4095-b4d4-f5251068c865","timestamp":"2026-08-06T10:54:49.813Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:2708:./docs/process_traces/2026-08-07-night-hardening/AUDIT-RUNNER.md:15884:docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:111:{"parentUuid":"47eb3b6c-e1d3-4e09-98c4-9b1d407df89d","isSidechain":true,"agentId":"a46e6644985dd75fd","message":{"model":"claude-opus-4-8","id":"msg_011CdmNPRgxc2Avvid6j8SgY","type":"message","role":"assistant","content":[{"type":"text","text":"Verdict determined. Compiling the cold-gate report.\n\n## COLD-GATE #2 VERDICT: **HOLD** — narrow, on the OPERATION only; artifact CONTENT and head are fully verified PROCEED-grade.\n\nI independently reproduced every load-bearing value from primary sources (no reliance on prior reviewers). Content passes cleanly; the HOLD is on a single unstated operational precondition that, taken as the packet describes it, bricks the claim anchor.\n\n### Checks that PASS (independently verified)\n\n- **File identity.** REVIEW.json SHA-256 = `316113960c59…8985`, matches the packet, and equals the impl consumer's `ISSUED_ACCEPTANCE_BOUND_SHA256` byte pin exactly (`joulewise/calibration_bracketing.py:56` on `impl/issuance-consumer`).\n- **Head reproduced from scratch.** Ran the bootstrap dry-run against the ruled disposition table (`/private/tmp/d079-ledger-dispositions.json`, sha `5da820aa…`) and custody manifest (`/private/tmp/d079-custody-manifest.lead.json`, sha `99cbf3df…`, both shas as cited). Result: `final_sequence=76`, `head_digest=08456d5076c18a…094d7` — exact match to the artifact's `ledger_cutoff` and `prior_observation_set.cutoff`. Final receipt (seq 76) = `c76f5d1c`, systematic-invalid, bound `0.0350400833260715`. Custody manifest = 38 members; disposition table = 38 rows.\n- **Dispositions 30/2/6.** Table counts exactly 30 valid / 2 systematic-invalid / 6 ordinary-invalid; systematic members = `20260726T000039-491995f3`, `20260801T064830-c76f5d1c`. Table attempt_ids, dispositions, AND content_ids are byte-identical to the artifact's `prior_observation_set`.\n- **B1 ruling correct vs D-102.** Both systematic bounds (`0.035435840879704805`, `0.0350400833260715`) exceed the ratified preflight screen `0.033558756679900`; D-102 (decision_log.md:6298-6301) explicitly rules the first member's pre-cal value a systematic failure \"never budgetable.\" Ruling sound.\n- **R2.8 counting.** 30 valid < 38 → no re-derivation trigger; issuance does not self-trigger. Correct.\n- **derivation_sha256.** Recomputed `_canonical_sha256(core)` = `4f6633d5…d23f02` = the artifact's whole-artifact hash. This is the correct NEW value (prior gate's F2 resolved).\n- **derivation_corpus.** n=19, byte-identical to the ratified fixture's corpus, zero Window-B members in the threshold basis.\n- **Consumer acceptance.** `_valid_acceptance_bound()` returns **True** under the intended consumer (`impl/issuance-consumer`); `identity_epoch=d079_epoch`, `artifact_role=issued`, `claim_eligible=true`, `cutoff.role=issued_acceptance_baseline` all conform.\n\n### The HOLD (operation, blocker)\n\n**The only valid loader for these bytes lives solely on unmerged branch `impl/issuance-consumer`; the packet's described execute does not land it, and on the current `main` checkout the write bricks the anchor.**\n\n- Main HEAD `c82a463` has NO issued-artifact consumer: no `ISSUED_ACCEPTANCE_BOUND_SHA256` constant and no `role == \"issued\"` path — `calibration_bracketing.py:173` still hard-requires `artifact_role == \"schema_fixture_unissued\"`. The consumer commit `1b78902` is contained only in `impl/issuance-consumer` (local + origin), not `main`.\n- Proof of brick: running main's `_valid_acceptance_bound()` on the exact issued bytes returns **False**, and main's byte pin is still the fixture's `9a264c5…`.\n- The packet's execute enumerates: bootstrap `--execute` → head-pin commit → write issued bytes to `configs/calibration/calibration_acceptance_d079_v2.json` → D-116. It names working directory `/Users/edr/code/JouleWise` (= main) and includes **no step landing the consumer**. Executed there, it replaces a loader-valid fixture with a loader-invalid issued artifact; production acceptance then refuses the anchor (and D-109 R1.4 anti-rollback refuses on the seq-76 pin), leaving an inconsistent state. This is the same F1 class the prior cold gate's Sol contract-lens refuter HELD on (`docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md`), unresolved by the operation as described.\n\n**Remedy (no change to the reviewed bytes required):** execute the bootstrap inside the `impl/issuance-consumer` worktree and land consumer + committed head-pin (seq 76 / `08456d50…`) + issued artifact as ONE atomic merge to main (or merge the consumer to main first), then re-confirm main's `_valid_acceptance_bound()` accepts the written bytes and authenticates against `ISSUED_ACCEPTANCE_BOUND_SHA256`. Clear the HOLD by confirming co-landing; the content gate is already satisfied.\n\n### Two notes for the magistrate (neither is a content defect)\n\n1. **Packet check-1 phrasing is inaccurate, artifact is correct.** `3cece3b2…` appears nowhere in the artifact and there is no \"preserved sub-field.\" That is correct: `3cece3b2` was the *fixture's* whole-artifact `derivation_sha256`; the issued artifact's whole-artifact hash legitimately becomes `4f6633d5…`, and the consumer *requires* `derivation_sha256 == canonical(core)` — embedding `3cece3b2` would FAIL the loader. The packet's expectation here is wrong; the bytes are right.\n2. **\"No Window-B member\" is true only for the threshold basis.** The n=19 `derivation_corpus` is Window-A-only (verified). But `prior_observation_set` correctly includes 6 observations with `window_metrologyB` custody — 2 of them valid (`e0ce33f5`, `8c3bfe9e`) — as mandated by D-109 R2.3/R2.8 completeness. These are fiducial calibration observations (general machinery survives per D-113), are excluded from the frozen n=19 threshold, and do not influence the bound. By design, not a violation — flagged only because the packet's flat \"no Window-B member present\" is literally false for the completeness record.\n\nPrimary sources consulted: the REVIEW.json; `docs/decision_log.md` D-102 (6278-6337), D-109 R2 (7052-7079), D-110 (7081-7126), D-113 (7240+); `VERIFICATION-REPORT.md`; `SOL-CONTRACT-LENS-HOLD.md`; live loader code on both `main` (`joulewise/calibration_bracketing.py`) and `impl/issuance-consumer`; and a self-run bootstrap dry-run."}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":830,"cache_read_input_tokens":134085,"cache_creation":{"ephemeral_5m_input_tokens":830,"ephemeral_1h_input_tokens":0},"output_tokens":2,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmNPNUyidjFY7Zr2dTAd","attributionAgent":"general-purpose","type":"assistant","uuid":"05cc7892-a85c-4095-b4d4-f5251068c865","timestamp":"2026-08-06T10:54:49.813Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:3206:  7497	- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:5431:docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:116:        "detail": "calibration_bracketing.py byte-pins the current fixture, requires artifact_role=schema_fixture_unissued, unratified_fixture status, claim_eligible=false, cutoff sequence 0/all-zero digest, and production_issuance_blocked=true. Production evaluation then unconditionally refuses the artifact as an unissued fixture. The packet proposes only ledger execution, head-pin update, artifact edit and D-116; it omits the required reviewed loader/schema/pin transition and supplies no exact final artifact bytes."
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:6243:`joulewise.calibration_acceptance_bound.v2.fixture.v1`, role
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:6244:`schema_fixture_unissued`, and file SHA-256
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:6248:`joulewise.calibration_acceptance_bound.v2`, role `issued`, and exact emitted
docs/process_traces/2026-08-07-d117-u-units/U1-DELTA2-VERDICT.md:9695:  7497	- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/phase_2/window_c_operator_checklist.md:30:- [ ] **Issue the production calibration-acceptance artifact.** The current file is explicitly `schema_fixture_unissued`, with a genesis ledger cutoff and `claim_eligible: false`. Complete its consumer implementation, exact-byte review, issuance, ledger/head-pin binding, and production-path verification.
docs/process_traces/2026-08-07-d117-u-units/U3-DELTA-VERDICT.md:33728:   457	        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
docs/process_traces/2026-08-07-d117-u-units/U3-DELTA-VERDICT.md:35185:   969	            "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/process_traces/2026-08-07-d117-u-units/U3-DELTA-VERDICT.md:36047:   969	            "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/contracts/calibration_ledger.md:187:`joulewise.calibration_acceptance_bound.v2.fixture.v1`, role
docs/contracts/calibration_ledger.md:188:`schema_fixture_unissued`, and file SHA-256
docs/contracts/calibration_ledger.md:192:`joulewise.calibration_acceptance_bound.v2`, role `issued`, and exact emitted
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1543:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1664:joulewise/calibration_bracketing.py:42:ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1665:joulewise/calibration_bracketing.py:44:    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1670:joulewise/calibration_bracketing.py:176:    if role == "schema_fixture_unissued":
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1685:joulewise/calibration_bracketing.py:457:        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1694:joulewise/calibration_bracketing.py:750:    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1700:joulewise/calibration_bracketing.py:843:    if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:1737:configs/calibration/calibration_acceptance_d079_v2.json:2:  "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:2249:  "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:2537:  "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:2651:  "schema_version": "joulewise.calibration_acceptance_bound.v2",
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:2827:ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:2829:    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:2961:    if role == "schema_fixture_unissued":
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:3242:        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:3536:    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:3629:    if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:4002:    if role == "schema_fixture_unissued":
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:4834:        "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:5051:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:15805:{"artifact":{"acceptance_id":"d079_calibration_acceptance_v2_n19","artifact_role":"issued","backfill_candidate":{"candidate_inventory":{"ordinary-invalid":6,"systematic-invalid":2,"valid":30},"production_issuance_blocked":false,"required_verification":"complete: lead-owned raw-physics and artifact-hash verification","status":"issued","superseded_id_only_blind_exclusions":["20260726T000039-491995f3","20260726T031222-e0ce33f5"]},"decimal_derivation":{"numeric_semantics":"decimal_source_lexemes","presentation_values":{"d079_range_12_places_s":{"label":"presentation_only_not_a_comparator","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000001 s","value":"0.010817749309"}},"ratified_operatives":{"allowance_rule":"max(observed_drift_s,bracket_screen_s)","bracket_screen_s":"0.010818","embedding_count":1,"max_budgetable_excess_s":"0.001275166090593858","maximum_budgetable_drift_s":"0.012093166090593858","operative_bound_rule":"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s","preflight_level_screen_s":"0.033558756679900"},"rounding":{"mode":"ROUND_HALF_EVEN","operative_bracket_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000001","source":"decimal_derivation.source_statistics.range_s","value_s":"0.010818"},"preflight_level_screen":{"numeric_role":"operative_comparator","quantum_s":"0.000000000000001","source":"decimal_derivation.source_statistics.maximum_s","value_s":"0.033558756679900"}},"source_statistics":{"maximum_member_id":"20260722T222332-901c5c13","maximum_s":"0.03355875667989999","mean_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.026950033977532761"},"minimum_member_id":"20260722T215127-eeef661a","minimum_s":"0.022741007370546462","prediction_95_two_draw_s":"0.008826584887500717","prediction_99_two_draw_s":"0.012093166090593858","range_s":"0.010817749309353528","sample_sd_presentation_s":{"label":"rounded_presentation","rounding_rule":"ROUND_HALF_EVEN to quantum 0.000000000000000001 s","value":"0.002970761365307205"}}},"decision_ids":["D-102","D-109"],"derivation_corpus":{"members":[{"b_fiducial_s":"0.03018980442653224","instrument_evidence_sha256":"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a","manifest_sha256":"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7","member_id":"20260722T145535-e941c821","source_directory":"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821"},{"b_fiducial_s":"0.026300679324099796","instrument_evidence_sha256":"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f","manifest_sha256":"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041","member_id":"20260722T194118-9dc0749d","source_directory":"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d"},{"b_fiducial_s":"0.03312014638436772","instrument_evidence_sha256":"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea","manifest_sha256":"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1","member_id":"20260722T214220-1acdbbc0","source_directory":"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0"},{"b_fiducial_s":"0.022741007370546462","instrument_evidence_sha256":"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024","manifest_sha256":"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5","member_id":"20260722T215127-eeef661a","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a"},{"b_fiducial_s":"0.03355875667989999","instrument_evidence_sha256":"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe","manifest_sha256":"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54","member_id":"20260722T222332-901c5c13","source_directory":"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13"},{"b_fiducial_s":"0.027654085293084385","instrument_evidence_sha256":"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7","manifest_sha256":"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70","member_id":"20260722T232509-82642517","source_directory":"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517"},{"b_fiducial_s":"0.024753340330112727","instrument_evidence_sha256":"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c","manifest_sha256":"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d","member_id":"20260723T023058-8732d1c9","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9"},{"b_fiducial_s":"0.025964638697819786","instrument_evidence_sha256":"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c","manifest_sha256":"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02","member_id":"20260723T052051-d9358c8a","source_directory":"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a"},{"b_fiducial_s":"0.027262160888545217","instrument_evidence_sha256":"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd","manifest_sha256":"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c","member_id":"20260723T183306-4ce692b4","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4"},{"b_fiducial_s":"0.024593263907495888","instrument_evidence_sha256":"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6","manifest_sha256":"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec","member_id":"20260723T194632-d04e038e","source_directory":"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e"},{"b_fiducial_s":"0.025305226022515448","instrument_evidence_sha256":"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7","manifest_sha256":"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005","member_id":"20260723T195730-bc4ba14a","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a"},{"b_fiducial_s":"0.027702588281732055","instrument_evidence_sha256":"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a","manifest_sha256":"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319","member_id":"20260723T221449-e9ae755e","source_directory":"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e"},{"b_fiducial_s":"0.026173651901677253","instrument_evidence_sha256":"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803","manifest_sha256":"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe","member_id":"20260723T223406-314f6d9e","source_directory":"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e"},{"b_fiducial_s":"0.02547564583006129","instrument_evidence_sha256":"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736","manifest_sha256":"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e","member_id":"20260724T014109-57844352","source_directory":"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352"},{"b_fiducial_s":"0.023241581438247116","instrument_evidence_sha256":"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be","manifest_sha256":"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9","member_id":"20260725T005132-a64711b7","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7"},{"b_fiducial_s":"0.028891617940876635","instrument_evidence_sha256":"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5","manifest_sha256":"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0","member_id":"20260725T011533-0b5ec77c","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c"},{"b_fiducial_s":"0.029197264796726408","instrument_evidence_sha256":"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da","manifest_sha256":"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185","member_id":"20260725T022712-0a9534f5","source_directory":"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5"},{"b_fiducial_s":"0.024879191521227362","instrument_evidence_sha256":"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e","manifest_sha256":"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a","member_id":"20260725T030533-d3f076e5","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5"},{"b_fiducial_s":"0.025045994537554683","instrument_evidence_sha256":"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2","manifest_sha256":"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704","member_id":"20260725T060617-97c5cba6","source_directory":"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6"}],"n":19,"selection":"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch"},"derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","identity_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100},"issuance":{"claim_eligible":true,"reason":"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff","status":"issued"},"ledger_cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","role":"issued_acceptance_baseline","sequence":76},"prior_observation_set":{"content_identity_method":"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))","cutoff":{"head_digest":"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7","ledger_schema":"joulewise.calibration_observation_ledger.v1","sequence":76},"epoch_catalog":{"d079_epoch":{"estimator_revision":"joint_loss_sublevel_interval_branch_v2","hardware_model":"Mac15,9","os_build":"25F84","power_policy":"ac_high_power","pulse_protocol_id":"powermetrics_pulse_fiducial_v3","sampling_interval_ms":100}},"observations":[{"attempt_id":"20260722T145535-e941c821","content_id":"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T194118-9dc0749d","content_id":"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T213749-563b9849","content_id":"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T214220-1acdbbc0","content_id":"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T215127-eeef661a","content_id":"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T222332-901c5c13","content_id":"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260722T232509-82642517","content_id":"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T023058-8732d1c9","content_id":"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T052051-d9358c8a","content_id":"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T183306-4ce692b4","content_id":"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T194632-d04e038e","content_id":"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T195730-bc4ba14a","content_id":"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T221449-e9ae755e","content_id":"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260723T223406-314f6d9e","content_id":"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260724T014109-57844352","content_id":"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T005132-a64711b7","content_id":"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T011533-0b5ec77c","content_id":"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T022712-0a9534f5","content_id":"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T030533-d3f076e5","content_id":"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T055825-b10cb348","content_id":"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260725T060617-97c5cba6","content_id":"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T000039-491995f3","content_id":"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710","disposition":"systematic-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T031222-e0ce33f5","content_id":"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225227-1f550773","content_id":"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260726T225920-ab4272f5","content_id":"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T015824-45feb516","content_id":"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T020611-4a409a30","content_id":"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260727T050047-95e2f87e","content_id":"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260729T204105-39d25f8a","content_id":"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T014035-124df355","content_id":"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260730T210703-f76b5771","content_id":"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T012210-374020b6","content_id":"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T161713-b8b08280","content_id":"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260731T214355-126fc2ab","content_id":"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010113-e859f3aa","content_id":"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T010805-ff3fdc88","content_id":"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21","disposition":"ordinary-invalid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T014059-8c3bfe9e","content_id":"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca","disposition":"valid","epoch_id":"d079_epoch"},{"attempt_id":"20260801T064830-c76f5d1c","content_id":"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448","disposition":"systematic-invalid","epoch_id":"d079_epoch"}]},"prospective_rederivation":{"calendar_expiry":null,"estimator_code_sha256":{"joulewise/adapters/powermetrics.py":"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca","joulewise/powermetrics_fiducial.py":"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3","joulewise/reduce.py":"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615","joulewise/uncertainty_evidence.py":"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7"},"protocol_sha256":"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1","trigger_observation_rule":"judge_under_prior_artifact_never_self_fit","triggers":["identity_field_change","protocol_or_estimator_byte_change","new_valid_same_identity_capture_expands_observed_range","corpus_doubles_from_19_to_38","new_systematic_failure_challenges_preflight_screen"]},"schema_version":"joulewise.calibration_acceptance_bound.v2"},"artifact_file_content":"{\n  \"schema_version\": \"joulewise.calibration_acceptance_bound.v2\",\n  \"acceptance_id\": \"d079_calibration_acceptance_v2_n19\",\n  \"decision_ids\": [\n    \"D-102\",\n    \"D-109\"\n  ],\n  \"artifact_role\": \"issued\",\n  \"issuance\": {\n    \"status\": \"issued\",\n    \"claim_eligible\": true,\n    \"reason\": \"D-109 R2 raw-physics and artifact-hash verification is bound by the authenticated historical-import cutoff\"\n  },\n  \"ledger_cutoff\": {\n    \"sequence\": 76,\n    \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n    \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\",\n    \"role\": \"issued_acceptance_baseline\"\n  },\n  \"identity_epoch\": {\n    \"os_build\": \"25F84\",\n    \"hardware_model\": \"Mac15,9\",\n    \"power_policy\": \"ac_high_power\",\n    \"sampling_interval_ms\": 100,\n    \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n    \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n  },\n  \"prospective_rederivation\": {\n    \"calendar_expiry\": null,\n    \"trigger_observation_rule\": \"judge_under_prior_artifact_never_self_fit\",\n    \"triggers\": [\n      \"identity_field_change\",\n      \"protocol_or_estimator_byte_change\",\n      \"new_valid_same_identity_capture_expands_observed_range\",\n      \"corpus_doubles_from_19_to_38\",\n      \"new_systematic_failure_challenges_preflight_screen\"\n    ],\n    \"protocol_sha256\": \"9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1\",\n    \"estimator_code_sha256\": {\n      \"joulewise/powermetrics_fiducial.py\": \"21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3\",\n      \"joulewise/uncertainty_evidence.py\": \"77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7\",\n      \"joulewise/adapters/powermetrics.py\": \"7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca\",\n      \"joulewise/reduce.py\": \"5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615\"\n    }\n  },\n  \"derivation_corpus\": {\n    \"selection\": \"valid protocol-v3 captures before the excluded window-B judged pair, exact identity epoch\",\n    \"n\": 19,\n    \"members\": [\n      {\n        \"member_id\": \"20260722T145535-e941c821\",\n        \"source_directory\": \"runs_window_a_20260722/instrument_validation/20260722T145535-e941c821\",\n        \"b_fiducial_s\": \"0.03018980442653224\",\n        \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n        \"instrument_evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\"\n      },\n      {\n        \"member_id\": \"20260722T194118-9dc0749d\",\n        \"source_directory\": \"runs_window_a2_20260722/instrument_validation/20260722T194118-9dc0749d\",\n        \"b_fiducial_s\": \"0.026300679324099796\",\n        \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n        \"instrument_evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\"\n      },\n      {\n        \"member_id\": \"20260722T214220-1acdbbc0\",\n        \"source_directory\": \"runs_window_a3_20260722/instrument_validation/20260722T214220-1acdbbc0\",\n        \"b_fiducial_s\": \"0.03312014638436772\",\n        \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n        \"instrument_evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\"\n      },\n      {\n        \"member_id\": \"20260722T215127-eeef661a\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T215127-eeef661a\",\n        \"b_fiducial_s\": \"0.022741007370546462\",\n        \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n        \"instrument_evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\"\n      },\n      {\n        \"member_id\": \"20260722T222332-901c5c13\",\n        \"source_directory\": \"runs_window_a4_20260722/instrument_validation/20260722T222332-901c5c13\",\n        \"b_fiducial_s\": \"0.03355875667989999\",\n        \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n        \"instrument_evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\"\n      },\n      {\n        \"member_id\": \"20260722T232509-82642517\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260722T232509-82642517\",\n        \"b_fiducial_s\": \"0.027654085293084385\",\n        \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n        \"instrument_evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\"\n      },\n      {\n        \"member_id\": \"20260723T023058-8732d1c9\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T023058-8732d1c9\",\n        \"b_fiducial_s\": \"0.024753340330112727\",\n        \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n        \"instrument_evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\"\n      },\n      {\n        \"member_id\": \"20260723T052051-d9358c8a\",\n        \"source_directory\": \"runs_window_a5_20260723/instrument_validation/20260723T052051-d9358c8a\",\n        \"b_fiducial_s\": \"0.025964638697819786\",\n        \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n        \"instrument_evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\"\n      },\n      {\n        \"member_id\": \"20260723T183306-4ce692b4\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T183306-4ce692b4\",\n        \"b_fiducial_s\": \"0.027262160888545217\",\n        \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n        \"instrument_evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\"\n      },\n      {\n        \"member_id\": \"20260723T194632-d04e038e\",\n        \"source_directory\": \"runs_window_a6_20260723/instrument_validation/20260723T194632-d04e038e\",\n        \"b_fiducial_s\": \"0.024593263907495888\",\n        \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n        \"instrument_evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\"\n      },\n      {\n        \"member_id\": \"20260723T195730-bc4ba14a\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T195730-bc4ba14a\",\n        \"b_fiducial_s\": \"0.025305226022515448\",\n        \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n        \"instrument_evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\"\n      },\n      {\n        \"member_id\": \"20260723T221449-e9ae755e\",\n        \"source_directory\": \"runs_window_a7_20260723/instrument_validation/20260723T221449-e9ae755e\",\n        \"b_fiducial_s\": \"0.027702588281732055\",\n        \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n        \"instrument_evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\"\n      },\n      {\n        \"member_id\": \"20260723T223406-314f6d9e\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260723T223406-314f6d9e\",\n        \"b_fiducial_s\": \"0.026173651901677253\",\n        \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n        \"instrument_evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\"\n      },\n      {\n        \"member_id\": \"20260724T014109-57844352\",\n        \"source_directory\": \"runs_window_a8_20260723/instrument_validation/20260724T014109-57844352\",\n        \"b_fiducial_s\": \"0.02547564583006129\",\n        \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n        \"instrument_evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\"\n      },\n      {\n        \"member_id\": \"20260725T005132-a64711b7\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T005132-a64711b7\",\n        \"b_fiducial_s\": \"0.023241581438247116\",\n        \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n        \"instrument_evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\"\n      },\n      {\n        \"member_id\": \"20260725T011533-0b5ec77c\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T011533-0b5ec77c\",\n        \"b_fiducial_s\": \"0.028891617940876635\",\n        \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n        \"instrument_evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\"\n      },\n      {\n        \"member_id\": \"20260725T022712-0a9534f5\",\n        \"source_directory\": \"runs_window_a9_20260724/instrument_validation/20260725T022712-0a9534f5\",\n        \"b_fiducial_s\": \"0.029197264796726408\",\n        \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n        \"instrument_evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\"\n      },\n      {\n        \"member_id\": \"20260725T030533-d3f076e5\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T030533-d3f076e5\",\n        \"b_fiducial_s\": \"0.024879191521227362\",\n        \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n        \"instrument_evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\"\n      },\n      {\n        \"member_id\": \"20260725T060617-97c5cba6\",\n        \"source_directory\": \"runs_window_a10_20260725/instrument_validation/20260725T060617-97c5cba6\",\n        \"b_fiducial_s\": \"0.025045994537554683\",\n        \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n        \"instrument_evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\"\n      }\n    ]\n  },\n  \"prior_observation_set\": {\n    \"cutoff\": {\n      \"sequence\": 76,\n      \"head_digest\": \"08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7\",\n      \"ledger_schema\": \"joulewise.calibration_observation_ledger.v1\"\n    },\n    \"content_identity_method\": \"sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))\",\n    \"epoch_catalog\": {\n      \"d079_epoch\": {\n        \"os_build\": \"25F84\",\n        \"hardware_model\": \"Mac15,9\",\n        \"power_policy\": \"ac_high_power\",\n        \"sampling_interval_ms\": 100,\n        \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n        \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n      }\n    },\n    \"observations\": [\n      {\n        \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T145535-e941c821\"\n      },\n      {\n        \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T194118-9dc0749d\"\n      },\n      {\n        \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260722T213749-563b9849\"\n      },\n      {\n        \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T214220-1acdbbc0\"\n      },\n      {\n        \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T215127-eeef661a\"\n      },\n      {\n        \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T222332-901c5c13\"\n      },\n      {\n        \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260722T232509-82642517\"\n      },\n      {\n        \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T023058-8732d1c9\"\n      },\n      {\n        \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T052051-d9358c8a\"\n      },\n      {\n        \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T183306-4ce692b4\"\n      },\n      {\n        \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T194632-d04e038e\"\n      },\n      {\n        \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T195730-bc4ba14a\"\n      },\n      {\n        \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T221449-e9ae755e\"\n      },\n      {\n        \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260723T223406-314f6d9e\"\n      },\n      {\n        \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260724T014109-57844352\"\n      },\n      {\n        \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T005132-a64711b7\"\n      },\n      {\n        \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T011533-0b5ec77c\"\n      },\n      {\n        \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T022712-0a9534f5\"\n      },\n      {\n        \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T030533-d3f076e5\"\n      },\n      {\n        \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260725T055825-b10cb348\"\n      },\n      {\n        \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260725T060617-97c5cba6\"\n      },\n      {\n        \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260726T000039-491995f3\"\n      },\n      {\n        \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T031222-e0ce33f5\"\n      },\n      {\n        \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260726T225227-1f550773\"\n      },\n      {\n        \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260726T225920-ab4272f5\"\n      },\n      {\n        \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T015824-45feb516\"\n      },\n      {\n        \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T020611-4a409a30\"\n      },\n      {\n        \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260727T050047-95e2f87e\"\n      },\n      {\n        \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260729T204105-39d25f8a\"\n      },\n      {\n        \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T014035-124df355\"\n      },\n      {\n        \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260730T210703-f76b5771\"\n      },\n      {\n        \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T012210-374020b6\"\n      },\n      {\n        \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260731T161713-b8b08280\"\n      },\n      {\n        \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260731T214355-126fc2ab\"\n      },\n      {\n        \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010113-e859f3aa\"\n      },\n      {\n        \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"ordinary-invalid\",\n        \"attempt_id\": \"20260801T010805-ff3fdc88\"\n      },\n      {\n        \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"valid\",\n        \"attempt_id\": \"20260801T014059-8c3bfe9e\"\n      },\n      {\n        \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n        \"epoch_id\": \"d079_epoch\",\n        \"disposition\": \"systematic-invalid\",\n        \"attempt_id\": \"20260801T064830-c76f5d1c\"\n      }\n    ]\n  },\n  \"backfill_candidate\": {\n    \"status\": \"issued\",\n    \"candidate_inventory\": {\n      \"ordinary-invalid\": 6,\n      \"systematic-invalid\": 2,\n      \"valid\": 30\n    },\n    \"production_issuance_blocked\": false,\n    \"required_verification\": \"complete: lead-owned raw-physics and artifact-hash verification\",\n    \"superseded_id_only_blind_exclusions\": [\n      \"20260726T000039-491995f3\",\n      \"20260726T031222-e0ce33f5\"\n    ]\n  },\n  \"decimal_derivation\": {\n    \"numeric_semantics\": \"decimal_source_lexemes\",\n    \"source_statistics\": {\n      \"minimum_s\": \"0.022741007370546462\",\n      \"minimum_member_id\": \"20260722T215127-eeef661a\",\n      \"maximum_s\": \"0.03355875667989999\",\n      \"maximum_member_id\": \"20260722T222332-901c5c13\",\n      \"range_s\": \"0.010817749309353528\",\n      \"mean_presentation_s\": {\n        \"value\": \"0.026950033977532761\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"sample_sd_presentation_s\": {\n        \"value\": \"0.002970761365307205\",\n        \"label\": \"rounded_presentation\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000000000001 s\"\n      },\n      \"prediction_95_two_draw_s\": \"0.008826584887500717\",\n      \"prediction_99_two_draw_s\": \"0.012093166090593858\"\n    },\n    \"presentation_values\": {\n      \"d079_range_12_places_s\": {\n        \"value\": \"0.010817749309\",\n        \"label\": \"presentation_only_not_a_comparator\",\n        \"rounding_rule\": \"ROUND_HALF_EVEN to quantum 0.000000000001 s\"\n      }\n    },\n    \"rounding\": {\n      \"mode\": \"ROUND_HALF_EVEN\",\n      \"operative_bracket_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.range_s\",\n        \"quantum_s\": \"0.000001\",\n        \"value_s\": \"0.010818\",\n        \"numeric_role\": \"operative_comparator\"\n      },\n      \"preflight_level_screen\": {\n        \"source\": \"decimal_derivation.source_statistics.maximum_s\",\n        \"quantum_s\": \"0.000000000000001\",\n        \"value_s\": \"0.033558756679900\",\n        \"numeric_role\": \"operative_comparator\"\n      }\n    },\n    \"ratified_operatives\": {\n      \"bracket_screen_s\": \"0.010818\",\n      \"preflight_level_screen_s\": \"0.033558756679900\",\n      \"max_budgetable_excess_s\": \"0.001275166090593858\",\n      \"maximum_budgetable_drift_s\": \"0.012093166090593858\",\n      \"allowance_rule\": \"max(observed_drift_s,bracket_screen_s)\",\n      \"operative_bound_rule\": \"max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s\",\n      \"embedding_count\": 1\n    }\n  },\n  \"derivation_sha256\": \"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02\"\n}\n","artifact_file_sha256":"316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985","derivation_sha256":"4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02","record":"issued-acceptance-artifact","schema_version":"joulewise.calibration_acceptance_issuance_dry_run.v1"}
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:5504:docs/process_traces/2026-08-07-night-hardening/AUDIT-RUNNER.md:15884:docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:111:{"parentUuid":"47eb3b6c-e1d3-4e09-98c4-9b1d407df89d","isSidechain":true,"agentId":"a46e6644985dd75fd","message":{"model":"claude-opus-4-8","id":"msg_011CdmNPRgxc2Avvid6j8SgY","type":"message","role":"assistant","content":[{"type":"text","text":"Verdict determined. Compiling the cold-gate report.\n\n## COLD-GATE #2 VERDICT: **HOLD** — narrow, on the OPERATION only; artifact CONTENT and head are fully verified PROCEED-grade.\n\nI independently reproduced every load-bearing value from primary sources (no reliance on prior reviewers). Content passes cleanly; the HOLD is on a single unstated operational precondition that, taken as the packet describes it, bricks the claim anchor.\n\n### Checks that PASS (independently verified)\n\n- **File identity.** REVIEW.json SHA-256 = `316113960c59…8985`, matches the packet, and equals the impl consumer's `ISSUED_ACCEPTANCE_BOUND_SHA256` byte pin exactly (`joulewise/calibration_bracketing.py:56` on `impl/issuance-consumer`).\n- **Head reproduced from scratch.** Ran the bootstrap dry-run against the ruled disposition table (`/private/tmp/d079-ledger-dispositions.json`, sha `5da820aa…`) and custody manifest (`/private/tmp/d079-custody-manifest.lead.json`, sha `99cbf3df…`, both shas as cited). Result: `final_sequence=76`, `head_digest=08456d5076c18a…094d7` — exact match to the artifact's `ledger_cutoff` and `prior_observation_set.cutoff`. Final receipt (seq 76) = `c76f5d1c`, systematic-invalid, bound `0.0350400833260715`. Custody manifest = 38 members; disposition table = 38 rows.\n- **Dispositions 30/2/6.** Table counts exactly 30 valid / 2 systematic-invalid / 6 ordinary-invalid; systematic members = `20260726T000039-491995f3`, `20260801T064830-c76f5d1c`. Table attempt_ids, dispositions, AND content_ids are byte-identical to the artifact's `prior_observation_set`.\n- **B1 ruling correct vs D-102.** Both systematic bounds (`0.035435840879704805`, `0.0350400833260715`) exceed the ratified preflight screen `0.033558756679900`; D-102 (decision_log.md:6298-6301) explicitly rules the first member's pre-cal value a systematic failure \"never budgetable.\" Ruling sound.\n- **R2.8 counting.** 30 valid < 38 → no re-derivation trigger; issuance does not self-trigger. Correct.\n- **derivation_sha256.** Recomputed `_canonical_sha256(core)` = `4f6633d5…d23f02` = the artifact's whole-artifact hash. This is the correct NEW value (prior gate's F2 resolved).\n- **derivation_corpus.** n=19, byte-identical to the ratified fixture's corpus, zero Window-B members in the threshold basis.\n- **Consumer acceptance.** `_valid_acceptance_bound()` returns **True** under the intended consumer (`impl/issuance-consumer`); `identity_epoch=d079_epoch`, `artifact_role=issued`, `claim_eligible=true`, `cutoff.role=issued_acceptance_baseline` all conform.\n\n### The HOLD (operation, blocker)\n\n**The only valid loader for these bytes lives solely on unmerged branch `impl/issuance-consumer`; the packet's described execute does not land it, and on the current `main` checkout the write bricks the anchor.**\n\n- Main HEAD `c82a463` has NO issued-artifact consumer: no `ISSUED_ACCEPTANCE_BOUND_SHA256` constant and no `role == \"issued\"` path — `calibration_bracketing.py:173` still hard-requires `artifact_role == \"schema_fixture_unissued\"`. The consumer commit `1b78902` is contained only in `impl/issuance-consumer` (local + origin), not `main`.\n- Proof of brick: running main's `_valid_acceptance_bound()` on the exact issued bytes returns **False**, and main's byte pin is still the fixture's `9a264c5…`.\n- The packet's execute enumerates: bootstrap `--execute` → head-pin commit → write issued bytes to `configs/calibration/calibration_acceptance_d079_v2.json` → D-116. It names working directory `/Users/edr/code/JouleWise` (= main) and includes **no step landing the consumer**. Executed there, it replaces a loader-valid fixture with a loader-invalid issued artifact; production acceptance then refuses the anchor (and D-109 R1.4 anti-rollback refuses on the seq-76 pin), leaving an inconsistent state. This is the same F1 class the prior cold gate's Sol contract-lens refuter HELD on (`docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md`), unresolved by the operation as described.\n\n**Remedy (no change to the reviewed bytes required):** execute the bootstrap inside the `impl/issuance-consumer` worktree and land consumer + committed head-pin (seq 76 / `08456d50…`) + issued artifact as ONE atomic merge to main (or merge the consumer to main first), then re-confirm main's `_valid_acceptance_bound()` accepts the written bytes and authenticates against `ISSUED_ACCEPTANCE_BOUND_SHA256`. Clear the HOLD by confirming co-landing; the content gate is already satisfied.\n\n### Two notes for the magistrate (neither is a content defect)\n\n1. **Packet check-1 phrasing is inaccurate, artifact is correct.** `3cece3b2…` appears nowhere in the artifact and there is no \"preserved sub-field.\" That is correct: `3cece3b2` was the *fixture's* whole-artifact `derivation_sha256`; the issued artifact's whole-artifact hash legitimately becomes `4f6633d5…`, and the consumer *requires* `derivation_sha256 == canonical(core)` — embedding `3cece3b2` would FAIL the loader. The packet's expectation here is wrong; the bytes are right.\n2. **\"No Window-B member\" is true only for the threshold basis.** The n=19 `derivation_corpus` is Window-A-only (verified). But `prior_observation_set` correctly includes 6 observations with `window_metrologyB` custody — 2 of them valid (`e0ce33f5`, `8c3bfe9e`) — as mandated by D-109 R2.3/R2.8 completeness. These are fiducial calibration observations (general machinery survives per D-113), are excluded from the frozen n=19 threshold, and do not influence the bound. By design, not a violation — flagged only because the packet's flat \"no Window-B member present\" is literally false for the completeness record.\n\nPrimary sources consulted: the REVIEW.json; `docs/decision_log.md` D-102 (6278-6337), D-109 R2 (7052-7079), D-110 (7081-7126), D-113 (7240+); `VERIFICATION-REPORT.md`; `SOL-CONTRACT-LENS-HOLD.md`; live loader code on both `main` (`joulewise/calibration_bracketing.py`) and `impl/issuance-consumer`; and a self-run bootstrap dry-run."}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":830,"cache_read_input_tokens":134085,"cache_creation":{"ephemeral_5m_input_tokens":830,"ephemeral_1h_input_tokens":0},"output_tokens":2,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmNPNUyidjFY7Zr2dTAd","attributionAgent":"general-purpose","type":"assistant","uuid":"05cc7892-a85c-4095-b4d4-f5251068c865","timestamp":"2026-08-06T10:54:49.813Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:5892:docs/process_traces/2026-08-07-night-hardening/AUDIT-RUNNER.md:15884:docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:111:{"parentUuid":"47eb3b6c-e1d3-4e09-98c4-9b1d407df89d","isSidechain":true,"agentId":"a46e6644985dd75fd","message":{"model":"claude-opus-4-8","id":"msg_011CdmNPRgxc2Avvid6j8SgY","type":"message","role":"assistant","content":[{"type":"text","text":"Verdict determined. Compiling the cold-gate report.\n\n## COLD-GATE #2 VERDICT: **HOLD** — narrow, on the OPERATION only; artifact CONTENT and head are fully verified PROCEED-grade.\n\nI independently reproduced every load-bearing value from primary sources (no reliance on prior reviewers). Content passes cleanly; the HOLD is on a single unstated operational precondition that, taken as the packet describes it, bricks the claim anchor.\n\n### Checks that PASS (independently verified)\n\n- **File identity.** REVIEW.json SHA-256 = `316113960c59…8985`, matches the packet, and equals the impl consumer's `ISSUED_ACCEPTANCE_BOUND_SHA256` byte pin exactly (`joulewise/calibration_bracketing.py:56` on `impl/issuance-consumer`).\n- **Head reproduced from scratch.** Ran the bootstrap dry-run against the ruled disposition table (`/private/tmp/d079-ledger-dispositions.json`, sha `5da820aa…`) and custody manifest (`/private/tmp/d079-custody-manifest.lead.json`, sha `99cbf3df…`, both shas as cited). Result: `final_sequence=76`, `head_digest=08456d5076c18a…094d7` — exact match to the artifact's `ledger_cutoff` and `prior_observation_set.cutoff`. Final receipt (seq 76) = `c76f5d1c`, systematic-invalid, bound `0.0350400833260715`. Custody manifest = 38 members; disposition table = 38 rows.\n- **Dispositions 30/2/6.** Table counts exactly 30 valid / 2 systematic-invalid / 6 ordinary-invalid; systematic members = `20260726T000039-491995f3`, `20260801T064830-c76f5d1c`. Table attempt_ids, dispositions, AND content_ids are byte-identical to the artifact's `prior_observation_set`.\n- **B1 ruling correct vs D-102.** Both systematic bounds (`0.035435840879704805`, `0.0350400833260715`) exceed the ratified preflight screen `0.033558756679900`; D-102 (decision_log.md:6298-6301) explicitly rules the first member's pre-cal value a systematic failure \"never budgetable.\" Ruling sound.\n- **R2.8 counting.** 30 valid < 38 → no re-derivation trigger; issuance does not self-trigger. Correct.\n- **derivation_sha256.** Recomputed `_canonical_sha256(core)` = `4f6633d5…d23f02` = the artifact's whole-artifact hash. This is the correct NEW value (prior gate's F2 resolved).\n- **derivation_corpus.** n=19, byte-identical to the ratified fixture's corpus, zero Window-B members in the threshold basis.\n- **Consumer acceptance.** `_valid_acceptance_bound()` returns **True** under the intended consumer (`impl/issuance-consumer`); `identity_epoch=d079_epoch`, `artifact_role=issued`, `claim_eligible=true`, `cutoff.role=issued_acceptance_baseline` all conform.\n\n### The HOLD (operation, blocker)\n\n**The only valid loader for these bytes lives solely on unmerged branch `impl/issuance-consumer`; the packet's described execute does not land it, and on the current `main` checkout the write bricks the anchor.**\n\n- Main HEAD `c82a463` has NO issued-artifact consumer: no `ISSUED_ACCEPTANCE_BOUND_SHA256` constant and no `role == \"issued\"` path — `calibration_bracketing.py:173` still hard-requires `artifact_role == \"schema_fixture_unissued\"`. The consumer commit `1b78902` is contained only in `impl/issuance-consumer` (local + origin), not `main`.\n- Proof of brick: running main's `_valid_acceptance_bound()` on the exact issued bytes returns **False**, and main's byte pin is still the fixture's `9a264c5…`.\n- The packet's execute enumerates: bootstrap `--execute` → head-pin commit → write issued bytes to `configs/calibration/calibration_acceptance_d079_v2.json` → D-116. It names working directory `/Users/edr/code/JouleWise` (= main) and includes **no step landing the consumer**. Executed there, it replaces a loader-valid fixture with a loader-invalid issued artifact; production acceptance then refuses the anchor (and D-109 R1.4 anti-rollback refuses on the seq-76 pin), leaving an inconsistent state. This is the same F1 class the prior cold gate's Sol contract-lens refuter HELD on (`docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md`), unresolved by the operation as described.\n\n**Remedy (no change to the reviewed bytes required):** execute the bootstrap inside the `impl/issuance-consumer` worktree and land consumer + committed head-pin (seq 76 / `08456d50…`) + issued artifact as ONE atomic merge to main (or merge the consumer to main first), then re-confirm main's `_valid_acceptance_bound()` accepts the written bytes and authenticates against `ISSUED_ACCEPTANCE_BOUND_SHA256`. Clear the HOLD by confirming co-landing; the content gate is already satisfied.\n\n### Two notes for the magistrate (neither is a content defect)\n\n1. **Packet check-1 phrasing is inaccurate, artifact is correct.** `3cece3b2…` appears nowhere in the artifact and there is no \"preserved sub-field.\" That is correct: `3cece3b2` was the *fixture's* whole-artifact `derivation_sha256`; the issued artifact's whole-artifact hash legitimately becomes `4f6633d5…`, and the consumer *requires* `derivation_sha256 == canonical(core)` — embedding `3cece3b2` would FAIL the loader. The packet's expectation here is wrong; the bytes are right.\n2. **\"No Window-B member\" is true only for the threshold basis.** The n=19 `derivation_corpus` is Window-A-only (verified). But `prior_observation_set` correctly includes 6 observations with `window_metrologyB` custody — 2 of them valid (`e0ce33f5`, `8c3bfe9e`) — as mandated by D-109 R2.3/R2.8 completeness. These are fiducial calibration observations (general machinery survives per D-113), are excluded from the frozen n=19 threshold, and do not influence the bound. By design, not a violation — flagged only because the packet's flat \"no Window-B member present\" is literally false for the completeness record.\n\nPrimary sources consulted: the REVIEW.json; `docs/decision_log.md` D-102 (6278-6337), D-109 R2 (7052-7079), D-110 (7081-7126), D-113 (7240+); `VERIFICATION-REPORT.md`; `SOL-CONTRACT-LENS-HOLD.md`; live loader code on both `main` (`joulewise/calibration_bracketing.py`) and `impl/issuance-consumer`; and a self-run bootstrap dry-run."}],"stop_reason":null,"stop_sequence":null,"stop_details":null,"usage":{"input_tokens":2,"cache_creation_input_tokens":830,"cache_read_input_tokens":134085,"cache_creation":{"ephemeral_5m_input_tokens":830,"ephemeral_1h_input_tokens":0},"output_tokens":2,"service_tier":"standard","inference_geo":"not_available"},"diagnostics":null},"requestId":"req_011CdmNPNUyidjFY7Zr2dTAd","attributionAgent":"general-purpose","type":"assistant","uuid":"05cc7892-a85c-4095-b4d4-f5251068c865","timestamp":"2026-08-06T10:54:49.813Z","effort":"high","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:5984:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:979:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:7029:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md:7057:7497:- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
configs/calibration/calibration_acceptance_d079_v2.json

exec
/bin/zsh -lc 'git log --oneline --follow -- configs/calibration/calibration_acceptance_d079_v2.json | head -20' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 47ms:
a816036 D-116: D-079 acceptance artifact ISSUED — issued config + committed head-pin (seq 76/08456d50) + coldgate custody [TEST RECONCILIATION PENDING]
8383113 D-109: A-min combined CAL-BRACKET fix round — reservation-first receipt ledger, head pin, F1+F2, R2 schema

exec
/bin/zsh -lc "rg -n 'normalize_calibration_custody_path|custody_locator.*absolute|Path\\(.*custody.*\\)\\.resolve|Path\\(.*custody.*\\)\\.absolute' joulewise scripts | head -120 && git diff --check origin/main...HEAD && git status --short" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
scripts/validate_powermetrics_fiducial.py:65:    normalize_calibration_custody_path,
scripts/validate_powermetrics_fiducial.py:382:        self.custody_locator = normalize_calibration_custody_path(
scripts/validate_powermetrics_fiducial.py:616:    custody_locator = normalize_calibration_custody_path(out_dir)
joulewise/calibration_ledger.py:204:def normalize_calibration_custody_path(path: Path | str) -> str:
joulewise/calibration_ledger.py:2522:        normalized_runs_root = normalize_calibration_custody_path(runs_root)
joulewise/calibration_ledger.py:2543:            custody = Path(normalize_calibration_custody_path(custody_value))
joulewise/calibration_ledger.py:3085:    "normalize_calibration_custody_path",
joulewise/adapters/node_client.py:907:        expected_custody_path = Path(str(record["custody_path"])).resolve()

codex
The first adversarial seam is now clear: recovery distinguishes malformed/mismatched journals, but it does not distinguish a completed/torn append from a journal whose payload never touched the ledger. I’m probing both the intended crash residue and that zero-byte/foreign-operation boundary under the real lock/journal APIs.
exec
/bin/zsh -lc "python3 - <<'PY'
from __future__ import annotations
import json, multiprocessing as mp, os, shutil, tempfile
from pathlib import Path

import joulewise.calibration_ledger as cl
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from scripts.validate_powermetrics_fiducial import _CaptureLedgerLifecycle

CTX = mp.get_context('fork')

def vectors():
    epoch = {
        'os_build': '25F84', 'hardware_model': 'Mac15,9',
        'power_policy': 'ac_high_power', 'sampling_interval_ms': 100,
        'estimator_revision': 'joint_loss_sublevel_interval_branch_v2',
        'pulse_protocol_id': 'powermetrics_pulse_fiducial_v3',
    }
    t1 = {field: f'value-{field}' for field in V2_BINDING_FIELDS}
    t1.update(epoch)
    return epoch, t1

def write_pin(path):
    path.write_text(json.dumps({'sequence': 0, 'head_digest': cl.GENESIS_DIGEST, 'ledger_schema': cl.LEDGER_SCHEMA})+'\\n')

def custody(path, token):
    (path/'raw').mkdir(parents=True, exist_ok=True)
    (path/'raw'/'powermetrics.plist').write_bytes(('raw-'+token).encode())
    (path/'events.jsonl').write_text('{\"timestamp_s\":99.0}\\n')
    (path/'instrument_evidence.json').write_text(json.dumps({'b_fiducial_s':0.025,'attempt':token})+'\\n')
    (path/'manifest.json').write_text(json.dumps({'attempt':token})+'\\n')
    return path

def setup(root: Path, sid: str):
    epoch, t1 = vectors(); ledger=root/'ledger.jsonl'; pin=root/'head.json'; write_pin(pin)
    runs=root/'runs'; iv=runs/'instrument_validation'
    slots={role:{'attempt_id':f'{sid}-{role}','custody_locator':str(iv/f'{sid}-{role}'),'identity_epoch':epoch,'t1_bindings':t1} for role in ('pre','post')}
    cl.append_bracket_session_receipt(ledger, session_id=sid, window_id=f'window-{sid}', plan_id=f'plan-{sid}', plan_sha256='a'*64, evidence_root_id=f'evidence-{sid}', runs_root=runs, slots=slots, head_pin_path=pin, require_committed_pin=False)
    return ledger,pin,runs,epoch,t1

def claim(ledger,sid,slot):
    return cl.claim_bracket_session_slot(ledger, session_id=sid, slot=slot, attempt_id=f'{sid}-{slot}', claim_id=f'claim-{sid}-{slot}')

def finalize(ledger,runs,sid,slot,epoch,t1):
    p=custody(runs/'instrument_validation'/f'{sid}-{slot}', f'{sid}-{slot}')
    return cl.finalize_bracket_session_slot(ledger, session_id=sid, slot=slot, disposition='valid', custody_locator=str(p), artifact_sha256=cl.artifact_hashes(p), identity_epoch=epoch, t1_bindings=t1, capture_wall_time_s='99.0' if slot=='pre' else '111.0', exact_bound_lexeme_s='0.025')

def crash_finalize_complete(ledger,runs,sid,slot,epoch,t1):
    cl._clear_append_journal=lambda _p: os._exit(91)
    finalize(ledger,runs,sid,slot,epoch,t1)

def crash_finalize_torn(ledger,runs,sid,slot,epoch,t1):
    def torn(handle,payload):
        n=max(1,len(payload)//2); handle.write(payload[:n]); handle.flush(); os.fsync(handle.fileno()); os._exit(92)
    cl._write_ledger_append_payload=torn
    finalize(ledger,runs,sid,slot,epoch,t1)

def crash_abort_before_write(ledger,sid):
    cl._write_ledger_append_payload=lambda _h,_p: os._exit(93)
    cl.abort_bracket_session(ledger,session_id=sid,reason='foreign-never-started-abort')

def race_claim(ledger,sid,barrier,q,token):
    barrier.wait()
    try:
        cl.claim_bracket_session_slot(ledger,session_id=sid,slot='pre',attempt_id=f'{sid}-pre',claim_id=f'racer-{token}')
        q.put((token,'ok'))
    except Exception as e:
        q.put((token,f'{type(e).__name__}: {e}'))

out={}
with tempfile.TemporaryDirectory(prefix='u1-audit-') as td:
    base=Path(td)
    # F1: complete PRE final append, crash before clear, then ordinary POST begin.
    root=base/'f1'; root.mkdir(); sid='f1'; ledger,pin,runs,epoch,t1=setup(root,sid); claim(ledger,sid,'pre')
    p=CTX.Process(target=crash_finalize_complete,args=(ledger,runs,sid,'pre',epoch,t1)); p.start(); p.join()
    before=cl.load_calibration_ledger_snapshot(ledger,pin,baseline_sequence=0,baseline_digest=cl.GENESIS_DIGEST,require_committed_pin=False,verify_custody=True)
    life=_CaptureLedgerLifecycle(ledger_path=ledger,head_pin_path=pin,attempt_id=f'{sid}-post',custody_locator=str(runs/'instrument_validation'/f'{sid}-post'),identity_epoch=epoch,t1_bindings=t1,session_id=sid,slot='post',require_committed_pin=False)
    life.begin()
    after=cl.load_calibration_ledger_snapshot(ledger,pin,baseline_sequence=0,baseline_digest=cl.GENESIS_DIGEST,require_committed_pin=False,verify_custody=True)
    out['F1_heal']={'crash_exit':p.exitcode,'before_reasons':list(before.refusal_reasons),'retry_begun':life.begun,'journal_exists_after':cl._append_journal_path(ledger).exists(),'recovery_evidence_count':len(list(root.glob('ledger.jsonl.recovery-*.json'))),'after_session_state':after.bracket_session_by_id[sid].state,'post_claim_present':any(r.get('event')==cl.BRACKET_SESSION_SLOT_CLAIM_EVENT and r.get('slot')=='post' for r in after.receipts)}

    # F1 legitimate refusal: malformed recovery sidecar is named, not misreported as slot mismatch.
    root=base/'f1-refuse'; root.mkdir(); sid='f1r'; ledger,pin,runs,epoch,t1=setup(root,sid); claim(ledger,sid,'pre'); finalize(ledger,runs,sid,'pre',epoch,t1)
    cl._append_journal_path(ledger).write_text('{}\\n')
    life=_CaptureLedgerLifecycle(ledger_path=ledger,head_pin_path=pin,attempt_id=f'{sid}-post',custody_locator=str(runs/'instrument_validation'/f'{sid}-post'),identity_epoch=epoch,t1_bindings=t1,session_id=sid,slot='post',require_committed_pin=False)
    try: life.begin(); msg='NO_REFUSAL'
    except Exception as e: msg=str(e)
    out['F1_legitimate_refusal']={'message':msg,'names_malformed':('journal is malformed' in msg),'old_false_slot_text':('exact reserved bracket session slot' in msg)}

    # F4 complete terminal tail + stale journal.
    root=base/'f4-full'; root.mkdir(); sid='f4full'; ledger,pin,runs,epoch,t1=setup(root,sid); claim(ledger,sid,'pre'); finalize(ledger,runs,sid,'pre',epoch,t1); claim(ledger,sid,'post')
    p=CTX.Process(target=crash_finalize_complete,args=(ledger,runs,sid,'post',epoch,t1)); p.start(); p.join()
    try: pinval=cl.terminal_head_pin_for_session(ledger,session_id=sid); status={'emitted':True,'value':pinval}
    except Exception as e: status={'emitted':False,'message':str(e)}
    out['F4_complete_tail']=status|{'crash_exit':p.exitcode,'journal_exists':cl._append_journal_path(ledger).exists()}

    # F4 partial terminal tail + valid journal.
    root=base/'f4-torn'; root.mkdir(); sid='f4torn'; ledger,pin,runs,epoch,t1=setup(root,sid); claim(ledger,sid,'pre'); finalize(ledger,runs,sid,'pre',epoch,t1); claim(ledger,sid,'post')
    p=CTX.Process(target=crash_finalize_torn,args=(ledger,runs,sid,'post',epoch,t1)); p.start(); p.join()
    try: pinval=cl.terminal_head_pin_for_session(ledger,session_id=sid); status={'emitted':True,'value':pinval}
    except Exception as e: status={'emitted':False,'message':str(e)}
    out['F4_torn_tail']=status|{'crash_exit':p.exitcode,'journal_exists':cl._append_journal_path(ledger).exists()}

    # F6a actual concurrent race.
    root=base/'f6'; root.mkdir(); sid='f6'; ledger,pin,runs,epoch,t1=setup(root,sid)
    barrier=CTX.Barrier(3); q=CTX.Queue(); ps=[CTX.Process(target=race_claim,args=(ledger,sid,barrier,q,str(i))) for i in range(2)]
    [p.start() for p in ps]; barrier.wait(); results=[q.get(timeout=5) for _ in ps]; [p.join() for p in ps]
    out['F6a_race']={'results':sorted(results),'taxonomy_code_exposed':any('calibration_ledger_bracket_slot_claimed' in x[1] for x in results),'operator_prose_exposed':any('exclusive writer claim' in x[1] for x in results)}

    # Introduced seam: a journal produced for a copied/foreign ledger, with zero ledger payload bytes,
    # is replayed into the target by the new standalone entry point.
    root=base/'foreign'; root.mkdir(); sid='foreign'; ledger,pin,runs,epoch,t1=setup(root,sid); claim(ledger,sid,'pre'); finalize(ledger,runs,sid,'pre',epoch,t1)
    foreign=root/'foreign-ledger.jsonl'; shutil.copy2(ledger,foreign)
    p=CTX.Process(target=crash_abort_before_write,args=(foreign,sid)); p.start(); p.join()
    foreign_journal=cl._append_journal_path(foreign); target_journal=cl._append_journal_path(ledger); shutil.copy2(foreign_journal,target_journal)
    before_bytes=ledger.read_bytes(); evidence=cl.recover_calibration_ledger_append(ledger); after_bytes=ledger.read_bytes()
    snap=cl.load_calibration_ledger_snapshot(ledger,pin,baseline_sequence=0,baseline_digest=cl.GENESIS_DIGEST,require_committed_pin=False,verify_custody=True)
    out['introduced_foreign_zero_byte_replay']={'foreign_crash_exit':p.exitcode,'target_payload_bytes_before':len(before_bytes),'target_payload_bytes_after':len(after_bytes),'bytes_appended':len(after_bytes)-len(before_bytes),'standalone_returned_evidence':str(evidence) if evidence else None,'journal_cleared':not target_journal.exists(),'target_session_state_after':snap.bracket_session_by_id[sid].state,'abort_reason_after':next((r.get('reason') for r in snap.receipts if r.get('event')==cl.BRACKET_SESSION_ABORT_EVENT),None)}

print(json.dumps(out,indent=2,sort_keys=True))
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 5ms:
exec
/bin/zsh -lc "python3 - <<'PY'
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
print(V2_BINDING_FIELDS)
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
('hardware_model', 'os_build', 'powermetrics_sha256', 'sampling_interval_ms', 'anchor_method_version', 'mlx_version', 'pulse_protocol_id', 'power_policy', 'estimator_revision', 'protocol_sha256')

exec
/bin/zsh -lc "python3 - <<'PY'
from __future__ import annotations
import hashlib, json, subprocess, tempfile
from pathlib import Path
from unittest.mock import patch

from joulewise.calibration_bracketing import CalibrationCandidate, build_calibration_bracket_binding, evaluate_calibration_bracket, _valid_acceptance_bound
import joulewise.calibration_ledger as cl
from joulewise.powermetrics_fiducial import PROTOCOL_ID, PROTOCOL_V3_SHA256, RESIDUAL_REGION_METHOD, V2_BINDING_FIELDS
from joulewise.schemas import CalibrationBracketingPolicy

artifact=json.loads(subprocess.check_output(['git','show','a816036"'^:configs/calibration/calibration_acceptance_d079_v2.json'"']))
assert artifact['artifact_role']=='schema_fixture_unissued' and _valid_acceptance_bound(artifact)
bindings=dict(artifact['identity_epoch'])
bindings.update({'powermetrics_sha256':'1'*64,'anchor_method_version':'powermetrics_clock_anchor_v2','mlx_version':'audit-fixture','protocol_sha256':PROTOCOL_V3_SHA256,'pulse_protocol_id':PROTOCOL_ID,'estimator_revision':RESIDUAL_REGION_METHOD})
epoch={field:bindings[field] for field in cl.IDENTITY_EPOCH_FIELDS}
t1={field:bindings[field] for field in V2_BINDING_FIELDS}
policy=CalibrationBracketingPolicy(require_bracket=True,calibration_bracket_max_drift_s=0.010)

def pinwrite(path,value): path.write_text(json.dumps(value)+'\\n')
def mkcust(path,token):
    (path/'raw').mkdir(parents=True)
    (path/'raw'/'powermetrics.plist').write_bytes(('raw-'+token).encode())
    (path/'events.jsonl').write_text('{\"timestamp_s\":99.0}\\n')
    (path/'instrument_evidence.json').write_text(json.dumps({'b_fiducial_s':0.025,'attempt':token})+'\\n')
    (path/'manifest.json').write_text(json.dumps({'attempt':token})+'\\n')
    return path

def ordinary(ledger,pin,runs,attempt,capture,bound):
    c=mkcust(runs/'instrument_validation'/attempt,attempt)
    cl.append_pending_receipt(ledger,attempt_id=attempt,custody_locator=str(c),identity_epoch=epoch,t1_bindings=t1,head_pin_path=pin,require_committed_pin=False)
    final=cl.finalize_attempt_receipt(ledger,attempt_id=attempt,disposition='valid',custody_locator=str(c),artifact_sha256=cl.artifact_hashes(c),identity_epoch=epoch,t1_bindings=t1,capture_wall_time_s=str(capture),exact_bound_lexeme_s=str(bound))
    pinwrite(pin,cl.head_pin_for_receipt(final))

def candidate(obs):
    return CalibrationCandidate(relative_path=obs.custody_locator,manifest_sha256=obs.artifact_sha256['manifest.json'],evidence_sha256=obs.artifact_sha256['instrument_evidence.json'],protocol_id=PROTOCOL_ID,capture_wall_time_s=float(obs.capture_wall_time_s),b_fiducial_s=obs.exact_bound_lexeme_s,bindings=bindings,attempt_id=obs.attempt_id,content_id=obs.content_id,ledger_receipt_digest=obs.receipt_digest,bracket_session_id=obs.bracket_session_id,bracket_slot=obs.bracket_slot,bracket_window_id=obs.bracket_window_id,bracket_plan_id=obs.bracket_plan_id,bracket_plan_sha256=obs.bracket_plan_sha256,bracket_evidence_root_id=obs.bracket_evidence_root_id,bracket_runs_root=obs.bracket_runs_root)

with tempfile.TemporaryDirectory(prefix='u1-f2-audit-') as td:
    root=Path(td); ledger=root/'ledger.jsonl'; pin=root/'head.json'; runs=root/'runs'
    pinwrite(pin,{'sequence':0,'head_digest':cl.GENESIS_DIGEST,'ledger_schema':cl.LEDGER_SCHEMA})
    ordinary(ledger,pin,runs,'historical-pre',99.0,'0.025')
    ordinary(ledger,pin,runs,'historical-post',111.0,'0.026')
    sid='later-session'; slots={role:{'attempt_id':f'{sid}-{role}','custody_locator':str(runs/'instrument_validation'/f'{sid}-{role}'),'identity_epoch':epoch,'t1_bindings':t1} for role in ('pre','post')}
    cl.append_bracket_session_receipt(ledger,session_id=sid,window_id='window-beta',plan_id='plan-beta',plan_sha256='b'*64,evidence_root_id='evidence-beta',runs_root=runs,slots=slots,head_pin_path=pin,require_committed_pin=False)
    for role,capture,bound in [('pre',999.0,'0.024'),('post',1111.0,'0.027')]:
        cl.claim_bracket_session_slot(ledger,session_id=sid,slot=role,attempt_id=f'{sid}-{role}',claim_id=f'claim-{role}')
        c=mkcust(runs/'instrument_validation'/f'{sid}-{role}',f'{sid}-{role}')
        cl.finalize_bracket_session_slot(ledger,session_id=sid,slot=role,disposition='valid',custody_locator=str(c),artifact_sha256=cl.artifact_hashes(c),identity_epoch=epoch,t1_bindings=t1,capture_wall_time_s=str(capture),exact_bound_lexeme_s=bound)
    pinwrite(pin,cl.terminal_head_pin_for_session(ledger,session_id=sid))
    snap=cl.load_calibration_ledger_snapshot(ledger,pin,baseline_sequence=0,baseline_digest=cl.GENESIS_DIGEST,require_committed_pin=False,verify_custody=True)
    candidates=[candidate(o) for o in snap.observations if o.disposition=='valid' and not o.is_historical_import]
    with patch('joulewise.calibration_bracketing.load_calibration_acceptance_bound',return_value=artifact):
        historical_result,historical_reasons=evaluate_calibration_bracket(candidates,window_start_s=100.0,window_end_s=110.0,bindings=bindings,policy=policy,ledger_snapshot=snap,_allow_unissued_fixture=True)
        _,withheld_reasons=evaluate_calibration_bracket(candidates[:-1],window_start_s=100.0,window_end_s=110.0,bindings=bindings,policy=policy,ledger_snapshot=snap,_allow_unissued_fixture=True)
    beta_binding=build_calibration_bracket_binding(snap,session_id=sid,window_id='window-beta',plan_id='plan-beta',plan_sha256='b'*64,evidence_root_id='evidence-beta',runs_root=runs)
    with patch('joulewise.calibration_bracketing.load_calibration_acceptance_bound',return_value=artifact):
        _,cross_missing=evaluate_calibration_bracket(candidates,window_start_s=1000.0,window_end_s=1100.0,bindings=bindings,policy=policy,ledger_snapshot=snap,_allow_unissued_fixture=True)
        _,cross_invalid=evaluate_calibration_bracket(candidates,window_start_s=1000.0,window_end_s=1100.0,bindings=bindings,policy=policy,ledger_snapshot=snap,bracket_binding=beta_binding,bracket_window_id='window-alpha',bracket_plan_id='plan-alpha',bracket_plan_sha256='a'*64,bracket_evidence_root_id='evidence-alpha',bracket_runs_root=runs,_allow_unissued_fixture=True)
    print(json.dumps({
      'snapshot_reasons':list(snap.refusal_reasons),
      'session_state':snap.bracket_session_by_id[sid].state,
      'historical_after_session':{'reasons':list(historical_reasons),'status':historical_result['status'],'pre':historical_result['pre']['attempt_id'] if historical_result['pre'] else None,'post':historical_result['post']['attempt_id'] if historical_result['post'] else None,'binding':historical_result['bracket_binding']},
      'anti_withholding':{'supplied':len(candidates)-1,'registered':len(candidates),'reasons':list(withheld_reasons)},
      'cross_window_l5':{'without_binding':list(cross_missing),'foreign_beta_binding_claimed_as_alpha':list(cross_invalid)}
    },indent=2,sort_keys=True))
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
{
  "anti_withholding": {
    "reasons": [
      "calibration_ledger_off_ledger_artifact"
    ],
    "registered": 4,
    "supplied": 3
  },
  "cross_window_l5": {
    "foreign_beta_binding_claimed_as_alpha": [
      "calibration_bracket_binding_invalid"
    ],
    "without_binding": [
      "calibration_bracket_binding_missing"
    ]
  },
  "historical_after_session": {
    "binding": null,
    "post": "historical-post",
    "pre": "historical-pre",
    "reasons": [],
    "status": "passed"
  },
  "session_state": "finalized",
  "snapshot_reasons": []
}

codex
The core closures reproduce cleanly: F1 heals the complete-tail residue; F2 preserves both historical evaluation and anti-withholding; F4 returns only `recovery_required`; and F6a produces prose under an actual two-process race. The introduced-defect probe is not clean: the standalone recovery API replayed a zero-byte foreign abort intent into another ledger, cleared the journal, and moved the target session to `aborted`. I’m completing path/main coverage and compatibility checks before assigning severity.
exec
/bin/zsh -lc "python3 - <<'PY'
from __future__ import annotations
import json, sys, tempfile, types
from pathlib import Path
from unittest.mock import patch

import joulewise.calibration_ledger as cl
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
import scripts.validate_powermetrics_fiducial as writer

epoch={'os_build':'25F84','hardware_model':'Mac15,9','power_policy':'ac_high_power','sampling_interval_ms':100,'estimator_revision':'joint_loss_sublevel_interval_branch_v2','pulse_protocol_id':'powermetrics_pulse_fiducial_v3'}
t1={field:f'value-{field}' for field in V2_BINDING_FIELDS}; t1.update(epoch)

def pinwrite(path): path.write_text(json.dumps({'sequence':0,'head_digest':cl.GENESIS_DIGEST,'ledger_schema':cl.LEDGER_SCHEMA})+'\\n')

with tempfile.TemporaryDirectory(prefix='u1-f5-audit-') as td:
    root=Path(td); real=root/'real-runs'; real.mkdir(); alias=root/'symlink-runs'; alias.symlink_to(real,target_is_directory=True)
    ledger=root/'ledger.jsonl'; pin=root/'head.json'; pinwrite(pin)
    sid='symlink-session'; slots={role:{'attempt_id':f'{sid}-{role}','custody_locator':str(alias/'instrument_validation'/f'{sid}-{role}'),'identity_epoch':epoch,'t1_bindings':t1} for role in ('pre','post')}
    cap=cl.append_bracket_session_receipt(ledger,session_id=sid,window_id='window-symlink',plan_id='plan-symlink',plan_sha256='a'*64,evidence_root_id='evidence-symlink',runs_root=alias,slots=slots,head_pin_path=pin,require_committed_pin=False)
    life=writer._CaptureLedgerLifecycle(ledger_path=ledger,head_pin_path=pin,attempt_id=f'{sid}-pre',custody_locator=str(alias/'instrument_validation'/f'{sid}-pre'),identity_epoch=epoch,t1_bindings=t1,session_id=sid,slot='pre',require_committed_pin=False)
    life.begin()

    captured={}
    class StopLifecycle:
        def __init__(self,**kwargs): captured.update(kwargs)
        def begin(self): raise cl.CalibrationLedgerError('audit stop after main lifecycle construction')
    mlx=types.ModuleType('mlx'); mlx.__path__=[]
    core=types.ModuleType('mlx.core'); core.__version__='audit'
    mlx.core=core
    old_mlx=sys.modules.get('mlx'); old_core=sys.modules.get('mlx.core')
    sys.modules['mlx']=mlx; sys.modules['mlx.core']=core
    try:
        with patch.object(writer,'_CaptureLedgerLifecycle',StopLifecycle), patch.object(writer,'verify_frozen_protocol',return_value=True), patch.object(writer,'_sysctl_identity',side_effect=lambda name: {'kern.osversion':'25F84','hw.model':'Mac15,9'}[name]), patch.object(writer,'sha256_path',return_value='f'*64):
            rc=writer.main(['--allow-live','--power-policy','ac_high_power','--output-root',str(alias/'instrument_validation'),'--session-id','main-session','--slot','pre','--attempt-id','main-pre'])
    finally:
        if old_mlx is None: sys.modules.pop('mlx',None)
        else: sys.modules['mlx']=old_mlx
        if old_core is None: sys.modules.pop('mlx.core',None)
        else: sys.modules['mlx.core']=old_core

    reserved=cap['slots']['pre']['custody_locator']
    main_expected=cl.normalize_calibration_custody_path(alias/'instrument_validation'/'main-pre')
    print(json.dumps({
      'library_symlink_case':{
        'alias':str(alias),'alias_resolves_to':str(alias.resolve()),
        'reserved_custody':reserved,'lifecycle_custody':life.custody_locator,
        'reservation_and_capture_equal':reserved==life.custody_locator,
        'writer_begin_claimed':life.begun,
        'symlink_spelling_preserved':str(alias) in reserved,
      },
      'main_path_case':{
        'return_code':rc,
        'captured_custody':captured.get('custody_locator'),
        'expected_lexical_custody':main_expected,
        'main_uses_shared_normalization':captured.get('custody_locator')==main_expected,
        'main_preserves_symlink_spelling':str(alias) in str(captured.get('custody_locator')),
      }
    },indent=2,sort_keys=True))
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
refusing: audit stop after main lifecycle construction
{
  "library_symlink_case": {
    "alias": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-f5-audit-ur4wshm4/symlink-runs",
    "alias_resolves_to": "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-f5-audit-ur4wshm4/real-runs",
    "lifecycle_custody": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-f5-audit-ur4wshm4/symlink-runs/instrument_validation/symlink-session-pre",
    "reservation_and_capture_equal": true,
    "reserved_custody": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-f5-audit-ur4wshm4/symlink-runs/instrument_validation/symlink-session-pre",
    "symlink_spelling_preserved": true,
    "writer_begin_claimed": true
  },
  "main_path_case": {
    "captured_custody": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-f5-audit-ur4wshm4/symlink-runs/instrument_validation/main-pre",
    "expected_lexical_custody": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-f5-audit-ur4wshm4/symlink-runs/instrument_validation/main-pre",
    "main_preserves_symlink_spelling": true,
    "main_uses_shared_normalization": true,
    "return_code": 2
  }
}

exec
/bin/zsh -lc "rg -n 'calibration_bracket_session|bracket-session-open' runs configs/calibration 2>/dev/null | head -80 || true && python3 - <<'PY'
from pathlib import Path
from joulewise.calibration_ledger import normalize_calibration_custody_path
samples=['relative/path','./relative/path','../up/path','/tmp/joulewise/example','/private/tmp/joulewise/example','~/literal-tilde']
for s in samples:
    old=str(Path(s).absolute())
    new=normalize_calibration_custody_path(s)
    print(f'{s"'!r}'"\\told={old"'!r}'"\\tnew={new"'!r}'"\\tequal={old==new}')
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
'relative/path'	old='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/relative/path'	new='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/relative/path'	equal=True
'./relative/path'	old='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/relative/path'	new='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/relative/path'	equal=True
'../up/path'	old='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/../up/path'	new='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/../up/path'	equal=True
'/tmp/joulewise/example'	old='/tmp/joulewise/example'	new='/tmp/joulewise/example'	equal=True
'/private/tmp/joulewise/example'	old='/private/tmp/joulewise/example'	new='/private/tmp/joulewise/example'	equal=True
'~/literal-tilde'	old='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/~/literal-tilde'	new='/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/~/literal-tilde'	equal=True

exec
/bin/zsh -lc 'git diff --unified=45 origin/main...HEAD -- tests/test_calibration_ledger.py tests/test_calibration_bracketing.py tests/test_powermetrics_fiducial.py' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
diff --git a/tests/test_calibration_bracketing.py b/tests/test_calibration_bracketing.py
index e381dc6..9b50d86 100644
--- a/tests/test_calibration_bracketing.py
+++ b/tests/test_calibration_bracketing.py
@@ -1111,90 +1111,143 @@ class CalibrationBracketingTests(unittest.TestCase):
         substituted["endpoints"]["pre"] = {
             "attempt_id": candidates[0].attempt_id,
             "receipt_digest": candidates[0].ledger_receipt_digest,
             "content_digest": candidates[0].content_id,
         }
         substituted["binding_digest"] = _canonical_sha256(
             {
                 key: value
                 for key, value in substituted.items()
                 if key != "binding_digest"
             }
         )
         self.assertIsNone(
             validate_calibration_bracket_binding(
                 substituted,
                 snapshot,
                 window_id="window-alpha",
                 plan_id="plan-alpha",
                 plan_sha256="a" * 64,
                 evidence_root_id="evidence-alpha",
                 runs_root="/synthetic/root-alpha",
             )
         )
 
         cross_window = json.loads(json.dumps(binding))
         cross_window["window_id"] = "window-beta"
         cross_window["binding_digest"] = _canonical_sha256(
             {
                 key: value
                 for key, value in cross_window.items()
                 if key != "binding_digest"
             }
         )
         self.assertIsNone(
             validate_calibration_bracket_binding(
                 cross_window,
                 snapshot,
                 window_id="window-alpha",
                 plan_id="plan-alpha",
                 plan_sha256="a" * 64,
                 evidence_root_id="evidence-alpha",
                 runs_root="/synthetic/root-alpha",
             )
         )
 
+    def test_ordinary_historical_window_still_evaluates_after_session_finalization(
+        self,
+    ) -> None:
+        snapshot, candidates, _binding = self._bound_session_fixture()
+        historical_times = {
+            "attempt-neighbor-pre": 89.0,
+            "attempt-neighbor-post": 96.0,
+        }
+        candidates = [
+            replace(
+                candidate,
+                capture_wall_time_s=historical_times.get(
+                    candidate.attempt_id,
+                    candidate.capture_wall_time_s,
+                ),
+            )
+            for candidate in candidates
+        ]
+        snapshot = replace(
+            snapshot,
+            observations=tuple(
+                replace(
+                    observation,
+                    capture_wall_time_s=str(
+                        historical_times.get(
+                            observation.attempt_id,
+                            observation.capture_wall_time_s,
+                        )
+                    ),
+                )
+                for observation in snapshot.observations
+            ),
+        )
+
+        with patch(
+            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
+            return_value=_unissued_acceptance_fixture(),
+        ):
+            result, reasons = _evaluate_calibration_bracket(
+                candidates,
+                window_start_s=90.0,
+                window_end_s=95.0,
+                bindings=self.bindings,
+                policy=self.policy,
+                ledger_snapshot=snapshot,
+                _allow_unissued_fixture=True,
+            )
+
+        self.assertEqual(reasons, ())
+        self.assertEqual(result["status"], "passed")
+        self.assertEqual(result["pre"]["attempt_id"], "attempt-neighbor-pre")
+        self.assertEqual(result["post"]["attempt_id"], "attempt-neighbor-post")
+
     def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
         snapshot, candidates, _binding = self._bound_session_fixture()
         session = snapshot.bracket_sessions[0]
         open_session = replace(
             session,
             state="open",
             finalized_slots=MappingProxyType({"pre": session.finalized_slots["pre"]}),
         )
         open_snapshot = replace(
             snapshot,
             observations=tuple(
                 observation
                 for observation in snapshot.observations
                 if observation.bracket_slot != "post"
             ),
             bracket_sessions=(open_session,),
             head_sequence=4,
             head_digest=session.finalized_slots["pre"].receipt_digest,
             receipts=(
                 *snapshot.receipts[:2],
                 MappingProxyType(
                     {
                         "event": "bracket-session-open",
                         "session_id": "session-alpha",
                         "predecessor_digest": snapshot.receipts[1]["receipt_digest"],
                         "receipt_digest": session.capability_receipt_digest,
                     }
                 ),
                 MappingProxyType(
                     {
                         "event": "bracket-session-slot-finalization",
                         "session_id": "session-alpha",
                         "receipt_digest": session.finalized_slots["pre"].receipt_digest,
                     }
                 ),
             ),
             refusal_reasons=(
                 "calibration_ledger_bracket_session_open",
                 "calibration_ledger_head_mismatch",
             ),
             committed_head_sequence=2,
             committed_head_digest=snapshot.receipts[1]["receipt_digest"],
         )
         by_attempt = {candidate.attempt_id: candidate for candidate in candidates}
         with patch(
diff --git a/tests/test_calibration_ledger.py b/tests/test_calibration_ledger.py
index 6de4916..c31214d 100644
--- a/tests/test_calibration_ledger.py
+++ b/tests/test_calibration_ledger.py
@@ -466,162 +466,257 @@ class CalibrationLedgerTests(unittest.TestCase):
             raise OSError("simulated process death during ledger append")
 
         with mock.patch.object(
             calibration_ledger,
             "_write_ledger_append_payload",
             side_effect=tear_final_line,
         ):
             with self.assertRaisesRegex(OSError, "simulated process death"):
                 finalize_bracket_session_slot(
                     self.ledger,
                     session_id="session-alpha",
                     slot="pre",
                     disposition="systematic-invalid",
                     custody_locator=str(custody),
                     artifact_sha256=artifact_hashes(custody),
                     identity_epoch=self.epoch,
                     t1_bindings=self.t1,
                     capture_wall_time_s="99.0",
                     exact_bound_lexeme_s="0.035435840879704805",
                 )
         return json.loads(
             calibration_ledger._append_journal_path(self.ledger).read_bytes()
         )
 
     def _abort_session_in_subprocess(self, *, kill_before_clear: bool):
         source_root = Path(__file__).resolve().parents[1]
         kill_patch = (
             """
 def kill_before_clear(_ledger_path):
     os.kill(os.getpid(), signal.SIGKILL)
 module._clear_append_journal = kill_before_clear
 """
             if kill_before_clear
             else ""
         )
         code = f"""
 import os, signal
 from pathlib import Path
 import joulewise.calibration_ledger as module
 {kill_patch}
 module.abort_bracket_session(
     Path({str(self.ledger)!r}),
     session_id="session-alpha",
     reason="recover_torn_systematic_pre",
 )
+"""
+        return subprocess.run(
+            [sys.executable, "-c", code],
+            cwd=source_root,
+            check=False,
+            capture_output=True,
+        )
+
+    def _finalize_post_in_subprocess_before_journal_clear(self):
+        source_root = Path(__file__).resolve().parents[1]
+        custody = self._custody("session-alpha-post")
+        code = f"""
+import os, signal
+from pathlib import Path
+import joulewise.calibration_ledger as module
+def kill_before_clear(_ledger_path):
+    os.kill(os.getpid(), signal.SIGKILL)
+module._clear_append_journal = kill_before_clear
+module.finalize_bracket_session_slot(
+    Path({str(self.ledger)!r}),
+    session_id="session-alpha",
+    slot="post",
+    disposition="valid",
+    custody_locator={str(custody)!r},
+    artifact_sha256=module.artifact_hashes(Path({str(custody)!r})),
+    identity_epoch={self.epoch!r},
+    t1_bindings={self.t1!r},
+    capture_wall_time_s="111.0",
+    exact_bound_lexeme_s="0.025",
+)
 """
         return subprocess.run(
             [sys.executable, "-c", code],
             cwd=source_root,
             check=False,
             capture_output=True,
         )
 
     def test_recovery_is_idempotent_after_process_death_before_journal_clear(
         self,
     ) -> None:
         journal = self._create_torn_session_finalization()
 
         killed = self._abort_session_in_subprocess(kill_before_clear=True)
         self.assertEqual(killed.returncode, -signal.SIGKILL)
         journal_path = calibration_ledger._append_journal_path(self.ledger)
         self.assertTrue(journal_path.exists())
         evidence_path = calibration_ledger._append_recovery_path(
             self.ledger, journal["operation_id"]
         )
         evidence_before_retry = evidence_path.read_bytes()
         evidence = json.loads(evidence_before_retry)
         self.assertEqual(
             evidence["observed_suffix_bytes"],
             len(journal["payload"].encode("utf-8")),
         )
         self.assertEqual(evidence["recovered_bytes"], 0)
 
         retried = self._abort_session_in_subprocess(kill_before_clear=False)
         self.assertEqual(retried.returncode, 0, retried.stderr.decode())
         self.assertFalse(journal_path.exists())
         self.assertEqual(evidence_path.read_bytes(), evidence_before_retry)
 
         self._write_pin(
             terminal_head_pin_for_session(
                 self.ledger, session_id="session-alpha"
             )
         )
         recovered = self._snapshot()
         self.assertEqual(recovered.refusal_reasons, ())
         self.assertEqual(recovered.bracket_sessions[0].state, "aborted")
         self.assertEqual(
             recovered.observations[0].disposition,
             "systematic-invalid",
         )
 
     def test_recovery_refuses_conflicting_existing_evidence(self) -> None:
         journal = self._create_torn_session_finalization()
         killed = self._abort_session_in_subprocess(kill_before_clear=True)
         self.assertEqual(killed.returncode, -signal.SIGKILL)
         journal_path = calibration_ledger._append_journal_path(self.ledger)
         evidence_path = calibration_ledger._append_recovery_path(
             self.ledger, journal["operation_id"]
         )
         evidence = json.loads(evidence_path.read_bytes())
         evidence["recovered_bytes"] = 1
         mismatched = canonical_json_bytes(evidence) + b"\n"
         evidence_path.write_bytes(mismatched)
         ledger_before_retry = self.ledger.read_bytes()
 
         with self.assertRaisesRegex(
             CalibrationLedgerError, "append recovery evidence conflicts"
         ):
             abort_bracket_session(
                 self.ledger,
                 session_id="session-alpha",
                 reason="recover_torn_systematic_pre",
             )
         self.assertTrue(journal_path.exists())
         self.assertEqual(self.ledger.read_bytes(), ledger_before_retry)
         self.assertEqual(evidence_path.read_bytes(), mismatched)
 
+    def test_terminal_session_pin_refuses_complete_tail_with_stale_journal(
+        self,
+    ) -> None:
+        self._open_bracket_session()
+        self._finalize_bracket_slot("session-alpha", "pre")
+        killed = self._finalize_post_in_subprocess_before_journal_clear()
+        self.assertEqual(killed.returncode, -signal.SIGKILL)
+        self.assertTrue(
+            calibration_ledger._append_journal_path(self.ledger).exists()
+        )
+
+        with self.assertRaisesRegex(
+            CalibrationLedgerError,
+            "calibration_ledger_recovery_required",
+        ):
+            terminal_head_pin_for_session(
+                self.ledger,
+                session_id="session-alpha",
+            )
+
+    def test_standalone_recovery_heals_journal_without_adding_a_receipt(
+        self,
+    ) -> None:
+        self._open_bracket_session()
+        self._finalize_bracket_slot("session-alpha", "pre")
+        killed = self._finalize_post_in_subprocess_before_journal_clear()
+        self.assertEqual(killed.returncode, -signal.SIGKILL)
+        receipt_count_before = len(self.ledger.read_bytes().splitlines())
+
+        evidence_path = calibration_ledger.recover_calibration_ledger_append(
+            self.ledger
+        )
+
+        self.assertIsNotNone(evidence_path)
+        assert evidence_path is not None
+        self.assertTrue(evidence_path.is_file())
+        self.assertFalse(
+            calibration_ledger._append_journal_path(self.ledger).exists()
+        )
+        self.assertEqual(
+            len(self.ledger.read_bytes().splitlines()),
+            receipt_count_before,
+        )
+        self.assertEqual(
+            terminal_head_pin_for_session(
+                self.ledger,
+                session_id="session-alpha",
+            )["sequence"],
+            receipt_count_before,
+        )
+
+    def test_terminal_session_pin_classifies_journal_authenticated_torn_tail(
+        self,
+    ) -> None:
+        self._create_torn_session_finalization()
+
+        with self.assertRaisesRegex(
+            CalibrationLedgerError,
+            "calibration_ledger_recovery_required",
+        ):
+            terminal_head_pin_for_session(
+                self.ledger,
+                session_id="session-alpha",
+            )
+
     def test_reservation_requires_complete_epoch_and_full_t1(self) -> None:
         with self.assertRaisesRegex(
             CalibrationLedgerError, "malformed receipt"
         ):
             append_pending_receipt(
                 self.ledger,
                 attempt_id="partial-reservation",
                 custody_locator=str(self.root / "partial"),
                 identity_epoch={"power_policy": "ac_high_power"},
                 t1_bindings={"power_policy": "ac_high_power"},
                 head_pin_path=self.pin,
                 require_committed_pin=False,
             )
 
     def test_production_writer_reserves_or_validates_before_capture_state_or_sampler(
         self,
     ) -> None:
         from scripts import validate_powermetrics_fiducial as writer
 
         custody = self.root / "behavioral-order" / "instrument_validation" / "attempt"
         lifecycle = writer._CaptureLedgerLifecycle(
             ledger_path=self.ledger,
             head_pin_path=self.pin,
             attempt_id="behavioral-order-attempt",
             custody_locator=str(custody),
             identity_epoch=self.epoch,
             t1_bindings=self.t1,
             require_committed_pin=False,
         )
         real_append = writer.append_pending_receipt
         observed_before_capture_state: list[bool] = []
 
         def observe_reservation(*args, **kwargs):
             observed_before_capture_state.append(not custody.exists())
             return real_append(*args, **kwargs)
 
         with mock.patch.object(
             writer,
             "append_pending_receipt",
             side_effect=observe_reservation,
         ):
             lifecycle.begin()
         self.assertEqual(observed_before_capture_state, [True])
         self.assertFalse(custody.exists())
         first = json.loads(self.ledger.read_text().splitlines()[0])
diff --git a/tests/test_powermetrics_fiducial.py b/tests/test_powermetrics_fiducial.py
index dd339c9..b0d6514 100644
--- a/tests/test_powermetrics_fiducial.py
+++ b/tests/test_powermetrics_fiducial.py
@@ -1,65 +1,66 @@
 """Synthetic pulse-detector tests for the D-078 fiducial harness.
 
 All traces are deterministic (sinusoidal pseudo-noise, no RNG): each test
 knows the true pulse edges and asserts the estimator's error and residual
 bounds against them.
 """
 
 from __future__ import annotations
 
 import math
 import json
 import hashlib
+import signal
 import subprocess
 import tempfile
 import threading
 import unittest
 import sys
 from dataclasses import replace
 from pathlib import Path
-from types import SimpleNamespace
+from types import ModuleType, SimpleNamespace
 from unittest.mock import patch
 
 from joulewise import calibration_ledger as ledger_module
 from joulewise import powermetrics_fiducial as fiducial_module
 from joulewise.powermetrics_fiducial import (
     BINDING_FIELDS,
     LEGACY_PROTOCOL_ID,
     PROTOCOL_ID,
     PROTOCOL_V2_ID,
     PROTOCOL_V2_SHA256,
     PROTOCOL_V3_SHA256,
     PULSE_COUNT,
     RESIDUAL_REGION_METHOD,
     CommandedPulse,
     TraceInterval,
     authenticate_protocol_schedule,
     detect_pulses,
     instrument_evidence,
     protocol_definition,
     pulse_gap_s,
     pulse_schedule,
     van_der_corput,
     window_license_min_duration_s,
 )
 from scripts.validate_powermetrics_fiducial import (
     trim_trace_after_warmups,
     verify_frozen_protocol,
 )
 from scripts import validate_powermetrics_fiducial as validation_script
 
 CADENCE_S = 0.1
 BASELINE_W = 2.0
 AMPLITUDE_W = 20.0
 
 
 def overlap_fraction(start_s: float, end_s: float, on_s: float, off_s: float) -> float:
     width = end_s - start_s
     if width <= 0:
         return 0.0
     return max(0.0, min(end_s, off_s) - max(start_s, on_s)) / width
 
 
 def synthetic_trace(
     true_pulses: list[tuple[float, float]],
     *,
@@ -1043,91 +1044,96 @@ class WriterLedgerIntegrationTests(unittest.TestCase):
         self,
     ) -> None:
         with tempfile.TemporaryDirectory() as tmp:
             ledger, pin, epoch, t1, custody, _capability = self._open_session(
                 Path(tmp)
             )
             lifecycles = [
                 self._lifecycle(ledger, pin, epoch, t1, custody, "pre")
                 for _index in range(2)
             ]
             barrier = threading.Barrier(2)
             real_validate = validation_script._validate_reserved_bracket_slot
 
             def synchronize_after_validation(*args, **kwargs):
                 real_validate(*args, **kwargs)
                 barrier.wait(timeout=5)
 
             outcomes: list[tuple[str, object]] = []
 
             def arm(lifecycle):
                 try:
                     lifecycle.begin()
                 except Exception as exc:  # noqa: BLE001 - asserted below
                     outcomes.append(("refused", exc))
                 else:
                     outcomes.append(("accepted", lifecycle))
 
             with patch.object(
                 validation_script,
                 "_validate_reserved_bracket_slot",
                 side_effect=synchronize_after_validation,
             ):
                 threads = [
                     threading.Thread(target=arm, args=(lifecycle,))
                     for lifecycle in lifecycles
                 ]
                 for thread in threads:
                     thread.start()
                 for thread in threads:
                     thread.join(timeout=10)
 
             accepted = [value for status, value in outcomes if status == "accepted"]
             refused = [value for status, value in outcomes if status == "refused"]
             self.assertEqual(len(accepted), 1)
             self.assertEqual(len(refused), 1)
-            self.assertIn("calibration_ledger_bracket_slot_claimed", str(refused[0]))
+            self.assertIn(
+                ledger_module.REFUSAL_TAXONOMY[
+                    "calibration_ledger_bracket_slot_claimed"
+                ],
+                str(refused[0]),
+            )
             loser = next(lifecycle for lifecycle in lifecycles if not lifecycle.begun)
             self.assertIsNone(loser.abandon("losing_writer_exit"))
             receipts = [json.loads(line) for line in ledger.read_text().splitlines()]
             self.assertFalse(
                 any(
                     receipt.get("event") == ledger_module.BRACKET_SESSION_ABORT_EVENT
                     for receipt in receipts
                 )
             )
             winner = accepted[0]
             abort = winner.abandon("winning_writer_governed_abort")
             self.assertEqual(abort["event"], ledger_module.BRACKET_SESSION_ABORT_EVENT)
 
     def test_session_writer_process_death_leaves_claim_then_governed_abort_recovers(
         self,
     ) -> None:
         with tempfile.TemporaryDirectory() as tmp:
             ledger, pin, epoch, t1, custody, _capability = self._open_session(
                 Path(tmp)
             )
             pre = self._lifecycle(ledger, pin, epoch, t1, custody, "pre")
             with (
                 patch.object(validation_script, "append_pending_receipt") as reserve,
                 patch.object(validation_script, "finalize_attempt_receipt") as ordinary,
             ):
                 pre.begin()
                 (custody["pre"] / "raw").mkdir(parents=True)
                 (custody["pre"] / "raw" / "powermetrics.plist").write_bytes(
                     b"raw"
                 )
                 (custody["pre"] / "events.jsonl").write_text("{}\n")
                 (custody["pre"] / "power_trace.csv").write_text("header\n")
                 (custody["pre"] / "instrument_evidence.json").write_text("{}\n")
                 (custody["pre"] / "manifest.json").write_text("{}\n")
                 pre.capture_wall_time_s = "99.0"
                 pre.exact_bound_lexeme_s = "0.025"
                 _pre_receipt, pre_head = pre.finalize("valid")
                 self.assertIsNone(pre_head)
 
             code = f"""
 import os
 from pathlib import Path
 from scripts.validate_powermetrics_fiducial import _CaptureLedgerLifecycle
 lifecycle = _CaptureLedgerLifecycle(
     ledger_path=Path({str(ledger)!r}),
@@ -1139,48 +1145,247 @@ lifecycle = _CaptureLedgerLifecycle(
     session_id='session-writer',
     slot='post',
     require_committed_pin=False,
 )
 lifecycle.begin()
 os._exit(23)
 """
             died = subprocess.run(
                 [sys.executable, "-c", code],
                 cwd=Path(__file__).resolve().parents[1],
                 check=False,
             )
             self.assertEqual(died.returncode, 23)
             crashed = ledger_module.load_calibration_ledger_snapshot(
                 ledger,
                 pin,
                 require_committed_pin=False,
                 verify_custody=True,
             )
             self.assertIn(
                 "calibration_ledger_bracket_session_open",
                 crashed.refusal_reasons,
             )
             abort = ledger_module.abort_bracket_session(
                 ledger,
                 session_id="session-writer",
                 reason="post_writer_process_died_after_claim",
             )
             reserve.assert_not_called()
             ordinary.assert_not_called()
             self.assertIsNotNone(abort)
             self.assertEqual(abort["event"], ledger_module.BRACKET_SESSION_ABORT_EVENT)
             self.assertEqual(abort["session_id"], "session-writer")
             self.assertEqual(tuple(abort["finalized_slots"]), ("pre",))
             self.assertEqual(tuple(abort["unused_slots"]), ("post",))
             self.assertEqual(
                 abort["reason"], "post_writer_process_died_after_claim"
             )
             self.assertEqual(
                 ledger_module.terminal_head_pin_for_session(
                     ledger, session_id="session-writer"
                 )["sequence"],
                 5,
             )
 
+    def test_post_slot_retry_recovers_crash_after_pre_append_before_clear(
+        self,
+    ) -> None:
+        with tempfile.TemporaryDirectory() as tmp:
+            ledger, pin, epoch, t1, custody, _capability = self._open_session(
+                Path(tmp)
+            )
+            pre = self._lifecycle(ledger, pin, epoch, t1, custody, "pre")
+            pre.begin()
+            (custody["pre"] / "raw").mkdir(parents=True)
+            (custody["pre"] / "raw" / "powermetrics.plist").write_bytes(b"raw")
+            (custody["pre"] / "events.jsonl").write_text("{}\n")
+            (custody["pre"] / "power_trace.csv").write_text("header\n")
+            (custody["pre"] / "instrument_evidence.json").write_text("{}\n")
+            (custody["pre"] / "manifest.json").write_text("{}\n")
+
+            code = f"""
+import os, signal
+from pathlib import Path
+import joulewise.calibration_ledger as module
+def kill_before_clear(_ledger_path):
+    os.kill(os.getpid(), signal.SIGKILL)
+module._clear_append_journal = kill_before_clear
+module.finalize_bracket_session_slot(
+    Path({str(ledger)!r}),
+    session_id="session-writer",
+    slot="pre",
+    disposition="valid",
+    custody_locator={str(custody['pre'])!r},
+    artifact_sha256=module.artifact_hashes(Path({str(custody['pre'])!r})),
+    identity_epoch={epoch!r},
+    t1_bindings={t1!r},
+    capture_wall_time_s="99.0",
+    exact_bound_lexeme_s="0.025",
+)
+"""
+            died = subprocess.run(
+                [sys.executable, "-c", code],
+                cwd=Path(__file__).resolve().parents[1],
+                check=False,
+            )
+            self.assertEqual(died.returncode, -signal.SIGKILL)
+            stranded = ledger_module.load_calibration_ledger_snapshot(
+                ledger,
+                pin,
+                require_committed_pin=False,
+                verify_custody=True,
+            )
+            self.assertIn(
+                "calibration_ledger_recovery_required",
+                stranded.refusal_reasons,
+            )
+            journal = json.loads(
+                ledger_module._append_journal_path(ledger).read_bytes()
+            )
+            with self.assertRaisesRegex(
+                ledger_module.CalibrationLedgerError,
+                "append recovery is required; retry this capture command",
+            ):
+                validation_script._validate_reserved_bracket_slot(
+                    ledger,
+                    pin,
+                    session_id="session-writer",
+                    slot="post",
+                    attempt_id="session-writer-post",
+                    custody_locator=str(custody["post"]),
+                    identity_epoch=epoch,
+                    t1_bindings=t1,
+                    require_committed_pin=False,
+                )
+
+            post = self._lifecycle(ledger, pin, epoch, t1, custody, "post")
+            post.begin()
+
+            self.assertTrue(post.begun)
+            self.assertFalse(ledger_module._append_journal_path(ledger).exists())
+            self.assertTrue(
+                ledger_module._append_recovery_path(
+                    ledger,
+                    journal["operation_id"],
+                ).is_file()
+            )
+            receipts = [json.loads(line) for line in ledger.read_text().splitlines()]
+            self.assertEqual(
+                receipts[-1]["event"],
+                ledger_module.BRACKET_SESSION_SLOT_CLAIM_EVENT,
+            )
+            self.assertEqual(receipts[-1]["slot"], "post")
+
+    def test_main_preserves_symlinked_custody_spelling_used_by_reservation(
+        self,
+    ) -> None:
+        with tempfile.TemporaryDirectory() as tmp:
+            root = Path(tmp)
+            physical_root = root / "physical-runs"
+            physical_root.mkdir()
+            symlinked_root = root / "symlinked-runs"
+            symlinked_root.symlink_to(physical_root, target_is_directory=True)
+            output_root = symlinked_root / "instrument_validation"
+            attempt_id = "session-writer-pre"
+            epoch = {
+                "os_build": "25F84",
+                "hardware_model": "Mac15,9",
+                "power_policy": "ac_high_power",
+                "sampling_interval_ms": 100,
+                "estimator_revision": RESIDUAL_REGION_METHOD,
+                "pulse_protocol_id": PROTOCOL_ID,
+            }
+            t1 = {field: f"value-{field}" for field in ledger_module.T1_FIELDS}
+            t1.update(epoch)
+            _session, normalized_slots = (
+                ledger_module.validate_bracket_session_reservation_inputs(
+                    session_id="session-writer",
+                    window_id="window-writer",
+                    plan_id="plan-writer",
+                    plan_sha256="a" * 64,
+                    evidence_root_id="evidence-writer",
+                    runs_root=symlinked_root,
+                    slots={
+                        slot: {
+                            "attempt_id": f"session-writer-{slot}",
+                            "custody_locator": str(
+                                output_root / f"session-writer-{slot}"
+                            ),
+                            "identity_epoch": epoch,
+                            "t1_bindings": t1,
+                        }
+                        for slot in ledger_module.BRACKET_SESSION_SLOTS
+                    },
+                )
+            )
+            expected_custody = normalized_slots["pre"]["custody_locator"]
+            observed: dict[str, str] = {}
+
+            class StopAfterCustodyCapture:
+                def __init__(self, **kwargs):
+                    observed["custody_locator"] = kwargs["custody_locator"]
+
+                def begin(self):
+                    raise ledger_module.CalibrationLedgerError(
+                        "stop after custody-path regression observation"
+                    )
+
+            mlx_package = ModuleType("mlx")
+            mlx_core = ModuleType("mlx.core")
+            mlx_core.__version__ = "synthetic"
+            mlx_package.core = mlx_core
+            with (
+                patch.dict(
+                    sys.modules,
+                    {"mlx": mlx_package, "mlx.core": mlx_core},
+                ),
+                patch.object(
+                    validation_script,
+                    "verify_frozen_protocol",
+                    return_value=True,
+                ),
+                patch.object(
+                    validation_script,
+                    "_sysctl_identity",
+                    side_effect=lambda name: (
+                        "25F84" if name == "kern.osversion" else "Mac15,9"
+                    ),
+                ),
+                patch.object(
+                    validation_script,
+                    "sha256_path",
+                    return_value="a" * 64,
+                ),
+                patch.object(
+                    validation_script,
+                    "SystemClock",
+                    return_value=SimpleNamespace(now=lambda: 0.0),
+                ),
+                patch.object(
+                    validation_script,
+                    "_CaptureLedgerLifecycle",
+                    StopAfterCustodyCapture,
+                ),
+            ):
+                return_code = validation_script.main(
+                    [
+                        "--allow-live",
+                        "--output-root",
+                        str(output_root),
+                        "--session-id",
+                        "session-writer",
+                        "--slot",
+                        "pre",
+                        "--attempt-id",
+                        attempt_id,
+                        "--power-policy",
+                        "ac_high_power",
+                    ]
+                )
+
+            self.assertEqual(return_code, 2)
+            self.assertEqual(observed["custody_locator"], expected_custody)
+
 
 if __name__ == "__main__":
     unittest.main()

codex
The new test set does exercise `main()` directly with a symlinked output root, and my independent mocked-main probe agrees with it. Compatibility is otherwise lexical: the helper is byte-for-byte equivalent to the reservation path’s prior `Path.absolute()` behavior; no checked-in bracket-session receipts exist to migrate. One operational edge remains—an old real-path reservation invoked through a symlink alias now refuses where the former resolving writer would have matched—but same-spelling retries and existing finalized custody loads are unchanged. I’m running the requested focused suites now.
exec
/bin/zsh -lc 'python3 -m unittest tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_powermetrics_fiducial' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 41583ms:
.......................................................................................................refusing: frozen powermetrics fiducial protocol is missing, incomplete, or disagrees with executable constants
................refusing: stop after custody-path regression observation
....
----------------------------------------------------------------------
Ran 133 tests in 41.596s

OK

codex
Focused suites are green: `Ran 133 tests in 41.596s — OK`. Their stderr tail includes only the two expected mocked-CLI refusals. I’m also running the repository’s canonical suite because this is a branch-level gate review; meanwhile I’m tracing the foreign-replay finding against the journal contract and checking the final diff for any second introduced defect.
exec
/bin/zsh -lc 'python3 -m unittest discover -s tests' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
codex
The canonical suite is still progressing normally; the output so far is expected fixture traffic and skips, with no failures. The foreign-replay issue is localized to the new recovery surface and automatic call site, not to F2/F4/F5/F6a.
codex
Canonical verification remains green in flight; the run has passed the large early integration block and is now in the long test tail. I’m preserving the exact final tail for the report rather than inferring from progress dots.
codex
The canonical run has reached the later campaign/worker modules with only the repository’s declared corpus/socket skips. No regression failure has appeared.
codex
The suite is in a known slow module and continues to advance without errors. The audit conclusion will therefore separate “closures verified” from the new zero-byte/foreign replay blocker rather than treating a green suite as dispositive.
codex
Still running, still clean. The slow tail is producing individual test completions rather than bulk output; I’ll keep the run attached until its final count and status are available.
codex
The canonical suite has now passed through the modified fiducial tests—including the expected mocked `main()` refusal—and remains green. The remaining modules are unrelated tail coverage.
codex
The remaining output continues to be expected negative-path CLI usage/warnings from tests, not suite failures. I’m waiting for the authoritative unittest summary.
codex
Canonical verification remains clean after the campaign-runner negative cases. No repository files have been modified; all reproductions used temporary directories.
 succeeded in 623284ms:
...................................................................................................................................................................................................................................................................................................................................................................................failed draft-off-000 attempt=0: [Errno 2] No such file or directory: '/definitely/missing/joulewise'
..failed draft-off-000 attempt=0: dispatch_failed_before_bundle_creation
..............bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template status=succeeded
.bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template status=succeeded
..................................................................s.....s.............ok draft-off-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template
ok draft-on-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template
ok draft-on-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template
ok draft-off-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template
AXI attempt ledger: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpoyykx8wc/axi_attempt_evidence/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/attempt_ledger.jsonl sha256=d83a00097b769a35de23d615aa84df365361411b8bafaae26883ae87313560af
ok draft-off-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template
ok draft-on-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template
ok draft-on-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template
ok draft-off-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template
AXI attempt ledger: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_evidence/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/attempt_ledger.jsonl sha256=d83a00097b769a35de23d615aa84df365361411b8bafaae26883ae87313560af
AXI attempt ledger: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpdalsjiup/axi_attempt_evidence/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/attempt_ledger.jsonl sha256=d83a00097b769a35de23d615aa84df365361411b8bafaae26883ae87313560af
.........................................................ssssssssssssssssssssss.........................................................................................................................................................................................................................................s.........s........s........................................................................................................................................................................................sss.............................................................................ACCEPTANCE GATE SKIP: six frozen legacy corpus bundles require the retained runs/ corpus
s.................................................................................................................................................ACCEPTANCE GATE SKIP: determinism gate requires the retained runs/ corpus
s.......................s...........................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................unsafe worker path: artifacts path is not a contained non-root path
................................NV-5 ACCEPTANCE GATE SKIP: localhost sockets unavailable; real client-worker subprocess parity was not exercised (PermissionError: [Errno 1] Operation not permitted)
s...................................ssssssssssssssssssssssssssssssssssssssssss..................................................................................................refusing: frozen powermetrics fiducial protocol is missing, incomplete, or disagrees with executable constants
................refusing: stop after custody-path regression observation
.............................................................................................................s................................................................................................................................s......ssssssss.....s...s..s................................WARNING: no order_manifest.json found; falling back to sorted config order. D-014 forbids silent sorted model blocks.
....warning: preserved 27 torn campaign-log bytes at /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpqza6p6sg/campaign_log.jsonl.torn-20260807T224959499024Z-3b23836bf203
.........warning: FAILED to preserve 12 torn campaign-log bytes to /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp0pl7khxg/campaign_log.jsonl.torn-20260807T225002510964Z-8f5927bdb239 (PermissionError('injected sidecar failure')); append refused, log untouched
........usage: python3.13 -m unittest [-h] [--runs-dir RUNS_DIR] [--log LOG]
                              [--dry-run] [--backup [BACKUP]]
                              [--shakedown-gate {production_uncertainty_v1}]
                              [--max-failures MAX_FAILURES]
                              [--cli-cmd CLI_CMD] [--waivers WAIVERS]
                              [--ack-config-warnings]
                              [--campaign-policy CAMPAIGN_POLICY]
                              [--instrument-calibration-dir INSTRUMENT_CALIBRATION_DIR]
                              [--instrument-power-policy INSTRUMENT_POWER_POLICY]
                              [--arm-quiet-mode]
                              [--arm-countdown-s ARM_COUNTDOWN_S]
                              [--environment-override ENVIRONMENT_OVERRIDE]
                              [--check-prompt-hashes BUNDLE_DIR SIDECAR_JSON]
                              [--whole-window-verdict]
                              [--consumption-semantics-id {d078_minted_envelopes_v1,d078_authenticated_max_bracket_rederivation_v1,salvage_dangler_exclusion_v1}]
                              [--window-membership-binding WINDOW_MEMBERSHIP_BINDING]
                              [--salvage-closure SALVAGE_CLOSURE]
                              [--neg8-drift-bound NEG8_DRIFT_BOUND]
                              [--derive-neg8-drift-bound CORPUS_JSON]
                              [--neg8-drift-bound-output ARTIFACT_JSON]
                              [--record-supersession BUNDLE_ID]
                              [--quarantine-path QUARANTINE_PATH]
                              [--reason REASON]
                              [config_dir]
python3.13 -m unittest: error: salvage-dangler semantics require --window-membership-binding and --salvage-closure
usage: python3.13 -m unittest [-h] [--runs-dir RUNS_DIR] [--log LOG]
                              [--dry-run] [--backup [BACKUP]]
                              [--shakedown-gate {production_uncertainty_v1}]
                              [--max-failures MAX_FAILURES]
                              [--cli-cmd CLI_CMD] [--waivers WAIVERS]
                              [--ack-config-warnings]
                              [--campaign-policy CAMPAIGN_POLICY]
                              [--instrument-calibration-dir INSTRUMENT_CALIBRATION_DIR]
                              [--instrument-power-policy INSTRUMENT_POWER_POLICY]
                              [--arm-quiet-mode]
                              [--arm-countdown-s ARM_COUNTDOWN_S]
                              [--environment-override ENVIRONMENT_OVERRIDE]
                              [--check-prompt-hashes BUNDLE_DIR SIDECAR_JSON]
                              [--whole-window-verdict]
                              [--consumption-semantics-id {d078_minted_envelopes_v1,d078_authenticated_max_bracket_rederivation_v1,salvage_dangler_exclusion_v1}]
                              [--window-membership-binding WINDOW_MEMBERSHIP_BINDING]
                              [--salvage-closure SALVAGE_CLOSURE]
                              [--neg8-drift-bound NEG8_DRIFT_BOUND]
                              [--derive-neg8-drift-bound CORPUS_JSON]
                              [--neg8-drift-bound-output ARTIFACT_JSON]
                              [--record-supersession BUNDLE_ID]
                              [--quarantine-path QUARANTINE_PATH]
                              [--reason REASON]
                              [config_dir]
python3.13 -m unittest: error: --waivers is forbidden under salvage-dangler semantics
....................................................warning: preserved 7 torn campaign-log bytes at /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp7m68qkhc/campaign_log.jsonl.torn-20260807T225103791722Z-e867134bb1b6
..bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template status=succeeded
..bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template status=succeeded
bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template status=succeeded
...............................................WARNING: no order_manifest.json found; falling back to sorted config order. D-014 forbids silent sorted model blocks.
error: environment preflight failed: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
........................................WARNING: no order_manifest.json found; falling back to sorted config order. D-014 forbids silent sorted model blocks.
ENVIRONMENT PREFLIGHT FAILED: display_power_state='any_awake' (fail)
override binding: snapshot_sha256=5b63e0cbf4d66ec48f8079ce252379be0cf8695c79ecd857bab10f430f64228a findings_sha256=5f82754478db0b19396360a005dcdc309d3e7d994261b0c31ddab68833771ccf
..............................................................s..................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 2739 tests in 622.872s

OK (skipped=90)
Config files to execute:
  /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp3fn6gbe1/configs/one.json
WARNING: This campaign needs a quiet machine with no other workloads.
WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.
NEG-8 WHOLE-WINDOW VERDICT: passed
  decision: passed
NEG-8 WHOLE-WINDOW VERDICT: passed
  decision: passed
NEG-8 WHOLE-WINDOW VERDICT: failed
  decision: failed
  condition: instrument_calibration_bracket_missing
  condition: neg8_bracket_ambiguous_reference
  condition: neg8_bracket_missing
  condition: neg8_bracket_reference_invalid
  condition: neg8_drift_bound_underived
  condition: neg8_idle_sub_drift_bound_underived
  condition: whole_window_bundle_invalid
NEG-8 WHOLE-WINDOW VERDICT: failed
  decision: failed
  condition: adapter_observations_missing
  condition: instrument_calibration_bracket_missing
  condition: neg8_bracket_missing
  condition: neg8_bracket_reference_invalid
  condition: neg8_drift_bound_underived
  condition: neg8_idle_sub_drift_bound_underived
  condition: whole_window_bundle_invalid
  condition: whole_window_campaign_membership_unresolved
NEG-8 WHOLE-WINDOW VERDICT: flagged
  decision: passed
ok draft-off-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template
ok draft-on-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template
ok draft-on-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template
ok draft-off-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template
AXI attempt ledger: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpc1gicsai/runs/axi_attempt_evidence/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/attempt_ledger.jsonl sha256=d83a00097b769a35de23d615aa84df365361411b8bafaae26883ae87313560af
ok draft-off-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-000/a0/axi-ap-spec-draft-template
ok draft-on-000 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-000/a0/axi-ap-spec-draft-template
ok draft-on-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-on-001/a0/axi-ap-spec-draft-template
ok draft-off-001 attempt=0: bundle=/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_bundles/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/draft-off-001/a0/axi-ap-spec-draft-template
AXI attempt ledger: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp742g1fpn/runs/axi_attempt_evidence/am-b0565dc0b68f55e132c38dbf5ba91140f7d5c10bb44ae2950de988ccd2362066/attempt_ledger.jsonl sha256=d83a00097b769a35de23d615aa84df365361411b8bafaae26883ae87313560af
Config files to execute:
  /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmp97lo871z/configs/one.json
WARNING: This campaign needs a quiet machine with no other workloads.
WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.
Config files to execute:
  /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpzd01fudj/configs/one.json
WARNING: This campaign needs a quiet machine with no other workloads.
WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.

codex
The suite is in another silent slow test but the process is alive. I’ll report only its final exit code and unittest tail once complete.
codex
Canonical verification is complete: `Ran 2739 tests in 622.872s — OK (skipped=90)`. I’m doing one final per-module focused run so the handoff can give separate ledger, bracketing, and fiducial tails, then I’ll verify the worktree stayed clean and issue the disposition table.
exec
/bin/zsh -lc 'python3 -m unittest tests.test_calibration_ledger' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
exec
/bin/zsh -lc 'python3 -m unittest tests.test_powermetrics_fiducial' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
exec
/bin/zsh -lc 'python3 -m unittest tests.test_calibration_bracketing' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 3426ms:
.........
----------------------------------------------------------------------
Ran 40 tests in 3.470s

OK

 succeeded in 9836ms:
.........................................
----------------------------------------------------------------------
Ran 51 tests in 9.876s

OK

 succeeded in 29357ms:
......................refusing: frozen powermetrics fiducial protocol is missing, incomplete, or disagrees with executable constants
................refusing: stop after custody-path regression observation
....
----------------------------------------------------------------------
Ran 42 tests in 29.383s

OK

exec
/bin/zsh -lc "nl -ba joulewise/calibration_ledger.py | sed -n '198,220p;850,884p;2448,2505p;2660,2690p;2834,2868p' && nl -ba joulewise/calibration_bracketing.py | sed -n '1228,1324p' && nl -ba scripts/validate_powermetrics_fiducial.py | sed -n '295,430p;606,624p' && nl -ba tests/test_powermetrics_fiducial.py | sed -n '1280,1395p' && git status --short --branch && git diff --check origin/main...HEAD" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
   198	        path = root / relative
   199	        if path.is_file():
   200	            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
   201	    return result
   202	
   203	
   204	def normalize_calibration_custody_path(path: Path | str) -> str:
   205	    """Return the lexical absolute spelling used by reservation and capture.
   206	
   207	    Custody identity is an exact ledger binding.  Resolving symlinks in only
   208	    one writer would therefore change that identity even when both spellings
   209	    name the same directory.
   210	    """
   211	
   212	    try:
   213	        return str(Path(path).absolute())
   214	    except (OSError, TypeError, ValueError) as exc:
   215	        raise CalibrationLedgerError(
   216	            "calibration custody path is malformed"
   217	        ) from exc
   218	
   219	
   220	def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
   850	    try:
   851	        value = json.loads(raw)
   852	    except (UnicodeDecodeError, json.JSONDecodeError):
   853	        return None, True
   854	    if not _valid_append_journal(value):
   855	        return None, True
   856	    return _frozen_mapping(value), False
   857	
   858	
   859	def _journal_completed_raw(
   860	    raw: bytes, journal: Mapping[str, Any]
   861	) -> bytes | None:
   862	    """Return the intended complete bytes only for one exact torn suffix."""
   863	
   864	    offset = int(journal["ledger_offset"])
   865	    payload = str(journal["payload"]).encode("utf-8")
   866	    if offset > len(raw):
   867	        return None
   868	    prefix = raw[:offset]
   869	    suffix = raw[offset:]
   870	    if offset and not prefix.endswith(b"\n"):
   871	        return None
   872	    prefix_receipts, prefix_reasons = _parse_ledger(prefix)
   873	    predecessor = (
   874	        str(prefix_receipts[-1]["receipt_digest"])
   875	        if prefix_receipts
   876	        else GENESIS_DIGEST
   877	    )
   878	    if prefix_reasons or predecessor != journal["predecessor_digest"]:
   879	        return None
   880	    if not payload.startswith(suffix):
   881	        return None
   882	    return prefix + payload
   883	
   884	
  2448	                return _frozen_mapping(receipt)
  2449	        finally:
  2450	            os.close(descriptor)
  2451	    finally:
  2452	        os.close(lock_descriptor)
  2453	
  2454	
  2455	def recover_calibration_ledger_append(ledger_path: Path) -> Path | None:
  2456	    """Complete one authenticated journaled append without adding a receipt.
  2457	
  2458	    The stable ledger lock is held through suffix completion, recovery
  2459	    evidence publication, and journal removal.  ``None`` means no recovery
  2460	    journal was present; otherwise the returned path is the durable evidence
  2461	    object for the completed operation.
  2462	    """
  2463	
  2464	    ledger_path = Path(ledger_path)
  2465	    ledger_path.parent.mkdir(parents=True, exist_ok=True)
  2466	    lock_descriptor = _open_ledger_lock(ledger_path)
  2467	    try:
  2468	        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
  2469	        journal, malformed = _read_append_journal(ledger_path)
  2470	        if malformed:
  2471	            raise CalibrationLedgerError("append recovery journal is malformed")
  2472	        if journal is None:
  2473	            return None
  2474	        descriptor = os.open(
  2475	            ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
  2476	        )
  2477	        try:
  2478	            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
  2479	                handle.seek(0)
  2480	                raw = handle.read()
  2481	                _recover_journaled_append(ledger_path, handle, raw)
  2482	        finally:
  2483	            os.close(descriptor)
  2484	        return _append_recovery_path(ledger_path, str(journal["operation_id"]))
  2485	    finally:
  2486	        os.close(lock_descriptor)
  2487	
  2488	
  2489	def _authenticated_head_pin(
  2490	    head_pin_path: Path,
  2491	    *,
  2492	    require_committed_pin: bool,
  2493	    repo_root: Path,
  2494	) -> tuple[int, str]:
  2495	    pin_path = Path(head_pin_path)
  2496	    try:
  2497	        pin_raw = pin_path.read_bytes()
  2498	        pin_value = json.loads(pin_raw)
  2499	    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
  2500	        raise CalibrationLedgerError("head pin is unreadable") from exc
  2501	    pin = _head_pin(pin_value)
  2502	    if pin is None:
  2503	        raise CalibrationLedgerError("head pin is malformed")
  2504	    if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
  2505	        raise CalibrationLedgerError("head pin is not committed at Git HEAD")
  2660	        observations, sessions, reasons = _attempts_and_observations(receipts)
  2661	        del observations
  2662	        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
  2663	        if non_open_reasons:
  2664	            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
  2665	        session = next(
  2666	            (item for item in sessions if item.session_id == session_id), None
  2667	        )
  2668	        if session is None or session.state != "open":
  2669	            raise CalibrationLedgerError("bracket session is not open")
  2670	        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
  2671	        if slot != expected_slot or session.slot_attempt_ids.get(slot) != attempt_id:
  2672	            raise CalibrationLedgerError(
  2673	                f"bracket session slot must claim in order: expected {expected_slot}"
  2674	            )
  2675	        existing = [
  2676	            receipt
  2677	            for receipt in receipts
  2678	            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
  2679	            and receipt.get("event") == BRACKET_SESSION_SLOT_CLAIM_EVENT
  2680	            and receipt.get("session_id") == session_id
  2681	            and receipt.get("slot") == slot
  2682	        ]
  2683	        if existing:
  2684	            raise CalibrationLedgerError(
  2685	                REFUSAL_TAXONOMY["calibration_ledger_bracket_slot_claimed"]
  2686	            )
  2687	        open_receipt = next(
  2688	            receipt
  2689	            for receipt in receipts
  2690	            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
  2834	        )
  2835	
  2836	    return _locked_append(Path(ledger_path), build)
  2837	
  2838	
  2839	def terminal_head_pin_for_session(
  2840	    ledger_path: Path,
  2841	    *,
  2842	    session_id: str,
  2843	) -> dict[str, Any]:
  2844	    """Return the sole terminal pin candidate after post or governed abort."""
  2845	
  2846	    try:
  2847	        raw = Path(ledger_path).read_bytes()
  2848	    except OSError as exc:
  2849	        raise CalibrationLedgerError("ledger is unreadable") from exc
  2850	    append_journal, malformed_journal = _read_append_journal(Path(ledger_path))
  2851	    receipts, parse_reasons = _parse_ledger(
  2852	        raw,
  2853	        append_journal=append_journal,
  2854	    )
  2855	    if malformed_journal:
  2856	        parse_reasons.add("calibration_ledger_malformed")
  2857	    observations, sessions, state_reasons = _attempts_and_observations(receipts)
  2858	    del observations
  2859	    reasons = parse_reasons | state_reasons
  2860	    if reasons:
  2861	        raise CalibrationLedgerError(", ".join(sorted(reasons)))
  2862	    session = next((item for item in sessions if item.session_id == session_id), None)
  2863	    if session is None or session.state == "open":
  2864	        raise CalibrationLedgerError("bracket session is not terminal")
  2865	    terminal_digest = (
  2866	        session.finalized_slots["post"].receipt_digest
  2867	        if session.state == "finalized"
  2868	        else session.abort_receipt_digest
  1228	    }
  1229	    supplied_valid = {
  1230	        (
  1231	            candidate.attempt_id,
  1232	            candidate.content_id,
  1233	            candidate.ledger_receipt_digest,
  1234	        )
  1235	        for candidate in candidates
  1236	    }
  1237	    # Even the low-level evaluator requires the complete ledger enumeration.
  1238	    # This prevents a caller from narrowing the registered universe to a
  1239	    # favorable subset while still passing per-candidate membership checks.
  1240	    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
  1241	        return result, ("calibration_ledger_off_ledger_artifact",)
  1242	    for candidate in candidates:
  1243	        observation = (
  1244	            observations_by_attempt.get(candidate.attempt_id)
  1245	            if isinstance(candidate.attempt_id, str)
  1246	            else None
  1247	        )
  1248	        if (
  1249	            observation is None
  1250	            or observation.disposition != "valid"
  1251	            or candidate.content_id != observation.content_id
  1252	            or candidate.ledger_receipt_digest != observation.receipt_digest
  1253	            or candidate.manifest_sha256
  1254	            != observation.artifact_sha256.get("manifest.json")
  1255	            or candidate.evidence_sha256
  1256	            != observation.artifact_sha256.get("instrument_evidence.json")
  1257	            or candidate.bracket_session_id != observation.bracket_session_id
  1258	            or candidate.bracket_slot != observation.bracket_slot
  1259	            or candidate.bracket_window_id != observation.bracket_window_id
  1260	            or candidate.bracket_plan_id != observation.bracket_plan_id
  1261	            or candidate.bracket_plan_sha256
  1262	            != observation.bracket_plan_sha256
  1263	            or candidate.bracket_evidence_root_id
  1264	            != observation.bracket_evidence_root_id
  1265	            or candidate.bracket_runs_root != observation.bracket_runs_root
  1266	        ):
  1267	            return result, ("calibration_ledger_off_ledger_artifact",)
  1268	    # A complete session pair makes the binding mandatory only for a window
  1269	    # that pair can causally and freshly bracket.  ``candidates`` still spans
  1270	    # the full registered universe above, preserving the anti-withholding
  1271	    # equality check without coupling historical ordinary windows to later
  1272	    # session observations.
  1273	    matching = [
  1274	        candidate
  1275	        for candidate in candidates
  1276	        if candidate.protocol_id == PROTOCOL_ID
  1277	        and all(
  1278	            candidate.bindings.get(field) == bindings.get(field)
  1279	            for field in V2_BINDING_FIELDS
  1280	        )
  1281	    ]
  1282	    window_session_pre_ids = {
  1283	        candidate.bracket_session_id
  1284	        for candidate in matching
  1285	        if candidate.bracket_session_id is not None
  1286	        and candidate.bracket_slot == "pre"
  1287	        and candidate.capture_wall_time_s <= window_start_s
  1288	        and window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
  1289	    }
  1290	    window_session_post_ids = {
  1291	        candidate.bracket_session_id
  1292	        for candidate in matching
  1293	        if candidate.bracket_session_id is not None
  1294	        and candidate.bracket_slot == "post"
  1295	        and candidate.capture_wall_time_s >= window_end_s
  1296	        and candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
  1297	    }
  1298	    has_session_candidates = (
  1299	        bool(window_session_pre_ids & window_session_post_ids)
  1300	        or bracket_binding is not None
  1301	    )
  1302	    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
  1303	    if has_session_candidates:
  1304	        if (
  1305	            bracket_binding is None
  1306	            or not all(
  1307	                isinstance(value, str) and bool(value)
  1308	                for value in (
  1309	                    bracket_window_id,
  1310	                    bracket_plan_id,
  1311	                    bracket_plan_sha256,
  1312	                    bracket_evidence_root_id,
  1313	                )
  1314	            )
  1315	            or bracket_runs_root is None
  1316	        ):
  1317	            return result, ("calibration_bracket_binding_missing",)
  1318	        expected_runs_root = str(Path(bracket_runs_root).absolute())
  1319	        bound_observations = validate_calibration_bracket_binding(
  1320	            bracket_binding,
  1321	            ledger_snapshot,
  1322	            window_id=bracket_window_id,
  1323	            plan_id=bracket_plan_id,
  1324	            plan_sha256=bracket_plan_sha256,
   295	    session_id: str,
   296	    slot: str,
   297	    attempt_id: str,
   298	    custody_locator: str,
   299	    identity_epoch: Mapping[str, Any],
   300	    t1_bindings: Mapping[str, Any],
   301	    require_committed_pin: bool = True,
   302	) -> None:
   303	    """Authenticate the exact predeclared slot before capture state exists."""
   304	
   305	    snapshot = load_calibration_ledger_snapshot(
   306	        ledger_path,
   307	        head_pin_path,
   308	        require_committed_pin=require_committed_pin,
   309	        verify_custody=True,
   310	    )
   311	    if "calibration_ledger_recovery_required" in snapshot.refusal_reasons:
   312	        raise CalibrationLedgerError(
   313	            "calibration ledger append recovery is required; retry this capture "
   314	            "command so governed recovery completes before slot validation"
   315	        )
   316	    session = snapshot.bracket_session_by_id.get(session_id)
   317	    finalized_slots = set(session.finalized_slots) if session is not None else set()
   318	    expected_slot = (
   319	        "pre"
   320	        if not finalized_slots
   321	        else "post"
   322	        if finalized_slots == {"pre"}
   323	        else None
   324	    )
   325	    open_receipt = next(
   326	        (
   327	            receipt
   328	            for receipt in snapshot.receipts
   329	            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
   330	            and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
   331	            and receipt.get("session_id") == session_id
   332	        ),
   333	        None,
   334	    )
   335	    reserved = (
   336	        open_receipt.get("slots", {}).get(slot)
   337	        if isinstance(open_receipt, Mapping)
   338	        and isinstance(open_receipt.get("slots"), Mapping)
   339	        else None
   340	    )
   341	    if (
   342	        not snapshot.is_governed_open_bracket_extension
   343	        or session is None
   344	        or session.state != "open"
   345	        or slot not in BRACKET_SESSION_SLOTS
   346	        or slot != expected_slot
   347	        or session.slot_attempt_ids.get(slot) != attempt_id
   348	        or not isinstance(reserved, Mapping)
   349	        or reserved.get("attempt_id") != attempt_id
   350	        or reserved.get("custody_locator") != custody_locator
   351	        or dict(reserved.get("identity_epoch", {})) != dict(identity_epoch)
   352	        or dict(reserved.get("t1_bindings", {})) != dict(t1_bindings)
   353	    ):
   354	        raise CalibrationLedgerError(
   355	            "capture does not match the exact reserved bracket session slot"
   356	        )
   357	
   358	
   359	class _CaptureLedgerLifecycle:
   360	    """Route one writer attempt through ordinary or bracket-session APIs."""
   361	
   362	    def __init__(
   363	        self,
   364	        *,
   365	        ledger_path: Path,
   366	        head_pin_path: Path,
   367	        attempt_id: str,
   368	        custody_locator: str,
   369	        identity_epoch: Mapping[str, Any],
   370	        t1_bindings: Mapping[str, Any],
   371	        session_id: str | None = None,
   372	        slot: str | None = None,
   373	        require_committed_pin: bool = True,
   374	    ) -> None:
   375	        if (session_id is None) != (slot is None):
   376	            raise CalibrationLedgerError(
   377	                "bracket session id and slot must be supplied together"
   378	            )
   379	        self.ledger_path = Path(ledger_path)
   380	        self.head_pin_path = Path(head_pin_path)
   381	        self.attempt_id = attempt_id
   382	        self.custody_locator = normalize_calibration_custody_path(
   383	            custody_locator
   384	        )
   385	        self.identity_epoch: Mapping[str, Any] = identity_epoch
   386	        self.t1_bindings: Mapping[str, Any] = t1_bindings
   387	        self.capture_wall_time_s: str | None = None
   388	        self.exact_bound_lexeme_s: str | None = None
   389	        self.session_id = session_id
   390	        self.slot = slot
   391	        self.require_committed_pin = require_committed_pin
   392	        self.claim_id = uuid.uuid4().hex
   393	        self.begun = False
   394	        self.closed = False
   395	
   396	    @property
   397	    def is_bracket_session(self) -> bool:
   398	        return self.session_id is not None
   399	
   400	    def begin(self) -> None:
   401	        """Reserve ordinarily, or authenticate a previously reserved slot."""
   402	
   403	        if self.begun:
   404	            raise CalibrationLedgerError("capture ledger lifecycle already began")
   405	        if self.is_bracket_session:
   406	            assert self.session_id is not None and self.slot is not None
   407	            try:
   408	                recover_calibration_ledger_append(self.ledger_path)
   409	            except CalibrationLedgerError as exc:
   410	                raise CalibrationLedgerError(
   411	                    "calibration ledger append recovery is required but automatic "
   412	                    "governed recovery did not complete; preserve the ledger and "
   413	                    "journal, then retry this capture command after resolving the "
   414	                    f"reported recovery condition: {exc}"
   415	                ) from exc
   416	            _validate_reserved_bracket_slot(
   417	                self.ledger_path,
   418	                self.head_pin_path,
   419	                session_id=self.session_id,
   420	                slot=self.slot,
   421	                attempt_id=self.attempt_id,
   422	                custody_locator=self.custody_locator,
   423	                identity_epoch=self.identity_epoch,
   424	                t1_bindings=self.t1_bindings,
   425	                require_committed_pin=self.require_committed_pin,
   426	            )
   427	            claim_bracket_session_slot(
   428	                self.ledger_path,
   429	                session_id=self.session_id,
   430	                slot=self.slot,
   606	
   607	    import mlx.core as mx  # noqa: PLC0415
   608	
   609	    clock = SystemClock()
   610	    validation_id = (
   611	        args.attempt_id
   612	        if bracket_mode
   613	        else time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
   614	    )
   615	    out_dir = args.output_root / validation_id
   616	    custody_locator = normalize_calibration_custody_path(out_dir)
   617	    planned_epoch = {
   618	        "os_build": _sysctl_identity("kern.osversion"),
   619	        "hardware_model": _sysctl_identity("hw.model"),
   620	        "power_policy": args.power_policy,
   621	        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
   622	        "estimator_revision": RESIDUAL_REGION_METHOD,
   623	        "pulse_protocol_id": PROTOCOL_ID,
   624	    }
  1280	        self,
  1281	    ) -> None:
  1282	        with tempfile.TemporaryDirectory() as tmp:
  1283	            root = Path(tmp)
  1284	            physical_root = root / "physical-runs"
  1285	            physical_root.mkdir()
  1286	            symlinked_root = root / "symlinked-runs"
  1287	            symlinked_root.symlink_to(physical_root, target_is_directory=True)
  1288	            output_root = symlinked_root / "instrument_validation"
  1289	            attempt_id = "session-writer-pre"
  1290	            epoch = {
  1291	                "os_build": "25F84",
  1292	                "hardware_model": "Mac15,9",
  1293	                "power_policy": "ac_high_power",
  1294	                "sampling_interval_ms": 100,
  1295	                "estimator_revision": RESIDUAL_REGION_METHOD,
  1296	                "pulse_protocol_id": PROTOCOL_ID,
  1297	            }
  1298	            t1 = {field: f"value-{field}" for field in ledger_module.T1_FIELDS}
  1299	            t1.update(epoch)
  1300	            _session, normalized_slots = (
  1301	                ledger_module.validate_bracket_session_reservation_inputs(
  1302	                    session_id="session-writer",
  1303	                    window_id="window-writer",
  1304	                    plan_id="plan-writer",
  1305	                    plan_sha256="a" * 64,
  1306	                    evidence_root_id="evidence-writer",
  1307	                    runs_root=symlinked_root,
  1308	                    slots={
  1309	                        slot: {
  1310	                            "attempt_id": f"session-writer-{slot}",
  1311	                            "custody_locator": str(
  1312	                                output_root / f"session-writer-{slot}"
  1313	                            ),
  1314	                            "identity_epoch": epoch,
  1315	                            "t1_bindings": t1,
  1316	                        }
  1317	                        for slot in ledger_module.BRACKET_SESSION_SLOTS
  1318	                    },
  1319	                )
  1320	            )
  1321	            expected_custody = normalized_slots["pre"]["custody_locator"]
  1322	            observed: dict[str, str] = {}
  1323	
  1324	            class StopAfterCustodyCapture:
  1325	                def __init__(self, **kwargs):
  1326	                    observed["custody_locator"] = kwargs["custody_locator"]
  1327	
  1328	                def begin(self):
  1329	                    raise ledger_module.CalibrationLedgerError(
  1330	                        "stop after custody-path regression observation"
  1331	                    )
  1332	
  1333	            mlx_package = ModuleType("mlx")
  1334	            mlx_core = ModuleType("mlx.core")
  1335	            mlx_core.__version__ = "synthetic"
  1336	            mlx_package.core = mlx_core
  1337	            with (
  1338	                patch.dict(
  1339	                    sys.modules,
  1340	                    {"mlx": mlx_package, "mlx.core": mlx_core},
  1341	                ),
  1342	                patch.object(
  1343	                    validation_script,
  1344	                    "verify_frozen_protocol",
  1345	                    return_value=True,
  1346	                ),
  1347	                patch.object(
  1348	                    validation_script,
  1349	                    "_sysctl_identity",
  1350	                    side_effect=lambda name: (
  1351	                        "25F84" if name == "kern.osversion" else "Mac15,9"
  1352	                    ),
  1353	                ),
  1354	                patch.object(
  1355	                    validation_script,
  1356	                    "sha256_path",
  1357	                    return_value="a" * 64,
  1358	                ),
  1359	                patch.object(
  1360	                    validation_script,
  1361	                    "SystemClock",
  1362	                    return_value=SimpleNamespace(now=lambda: 0.0),
  1363	                ),
  1364	                patch.object(
  1365	                    validation_script,
  1366	                    "_CaptureLedgerLifecycle",
  1367	                    StopAfterCustodyCapture,
  1368	                ),
  1369	            ):
  1370	                return_code = validation_script.main(
  1371	                    [
  1372	                        "--allow-live",
  1373	                        "--output-root",
  1374	                        str(output_root),
  1375	                        "--session-id",
  1376	                        "session-writer",
  1377	                        "--slot",
  1378	                        "pre",
  1379	                        "--attempt-id",
  1380	                        attempt_id,
  1381	                        "--power-policy",
  1382	                        "ac_high_power",
  1383	                    ]
  1384	                )
  1385	
  1386	            self.assertEqual(return_code, 2)
  1387	            self.assertEqual(observed["custody_locator"], expected_custody)
  1388	
  1389	
  1390	if __name__ == "__main__":
  1391	    unittest.main()
## impl/d117-u1-gate-debt...origin/impl/d117-u1-gate-debt

exec
/bin/zsh -lc "nl -ba joulewise/calibration_ledger.py | sed -n '2355,2410p' && nl -ba tests/test_calibration_ledger.py | sed -n '540,680p' && nl -ba tests/test_calibration_bracketing.py | sed -n '1150,1225p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
  2355	    try:
  2356	        _append_journal_path(ledger_path).unlink()
  2357	        _fsync_parent_directory(Path(ledger_path).parent)
  2358	    except OSError as exc:
  2359	        raise CalibrationLedgerError("append journal could not be cleared") from exc
  2360	
  2361	
  2362	def _recover_journaled_append(
  2363	    ledger_path: Path,
  2364	    handle: BinaryIO,
  2365	    raw: bytes,
  2366	) -> bytes:
  2367	    journal, malformed = _read_append_journal(ledger_path)
  2368	    if malformed:
  2369	        raise CalibrationLedgerError("append recovery journal is malformed")
  2370	    if journal is None:
  2371	        return raw
  2372	    completed = _journal_completed_raw(raw, journal)
  2373	    if completed is None:
  2374	        raise CalibrationLedgerError(
  2375	            "torn ledger tail does not match the append recovery journal"
  2376	        )
  2377	    offset = int(journal["ledger_offset"])
  2378	    payload = str(journal["payload"]).encode("utf-8")
  2379	    observed = len(raw) - offset
  2380	    missing = payload[observed:]
  2381	    if missing:
  2382	        handle.seek(0, os.SEEK_END)
  2383	        _write_ledger_append_payload(handle, missing)
  2384	        handle.flush()
  2385	        os.fsync(handle.fileno())
  2386	    handle.seek(0)
  2387	    completed = handle.read()
  2388	    if _journal_completed_raw(completed, journal) != completed:
  2389	        raise CalibrationLedgerError(
  2390	            "append recovery did not complete the ledger tail"
  2391	        )
  2392	    _record_append_recovery(
  2393	        ledger_path,
  2394	        journal,
  2395	        ledger_tail=completed[offset:],
  2396	    )
  2397	    _clear_append_journal(ledger_path)
  2398	    return completed
  2399	
  2400	
  2401	def _locked_append(
  2402	    ledger_path: Path,
  2403	    build: Any,
  2404	) -> Mapping[str, Any]:
  2405	    ledger_path = Path(ledger_path)
  2406	    ledger_path.parent.mkdir(parents=True, exist_ok=True)
  2407	    lock_descriptor = _open_ledger_lock(ledger_path)
  2408	    try:
  2409	        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
  2410	        descriptor = os.open(
   540	)
   541	"""
   542	        return subprocess.run(
   543	            [sys.executable, "-c", code],
   544	            cwd=source_root,
   545	            check=False,
   546	            capture_output=True,
   547	        )
   548	
   549	    def test_recovery_is_idempotent_after_process_death_before_journal_clear(
   550	        self,
   551	    ) -> None:
   552	        journal = self._create_torn_session_finalization()
   553	
   554	        killed = self._abort_session_in_subprocess(kill_before_clear=True)
   555	        self.assertEqual(killed.returncode, -signal.SIGKILL)
   556	        journal_path = calibration_ledger._append_journal_path(self.ledger)
   557	        self.assertTrue(journal_path.exists())
   558	        evidence_path = calibration_ledger._append_recovery_path(
   559	            self.ledger, journal["operation_id"]
   560	        )
   561	        evidence_before_retry = evidence_path.read_bytes()
   562	        evidence = json.loads(evidence_before_retry)
   563	        self.assertEqual(
   564	            evidence["observed_suffix_bytes"],
   565	            len(journal["payload"].encode("utf-8")),
   566	        )
   567	        self.assertEqual(evidence["recovered_bytes"], 0)
   568	
   569	        retried = self._abort_session_in_subprocess(kill_before_clear=False)
   570	        self.assertEqual(retried.returncode, 0, retried.stderr.decode())
   571	        self.assertFalse(journal_path.exists())
   572	        self.assertEqual(evidence_path.read_bytes(), evidence_before_retry)
   573	
   574	        self._write_pin(
   575	            terminal_head_pin_for_session(
   576	                self.ledger, session_id="session-alpha"
   577	            )
   578	        )
   579	        recovered = self._snapshot()
   580	        self.assertEqual(recovered.refusal_reasons, ())
   581	        self.assertEqual(recovered.bracket_sessions[0].state, "aborted")
   582	        self.assertEqual(
   583	            recovered.observations[0].disposition,
   584	            "systematic-invalid",
   585	        )
   586	
   587	    def test_recovery_refuses_conflicting_existing_evidence(self) -> None:
   588	        journal = self._create_torn_session_finalization()
   589	        killed = self._abort_session_in_subprocess(kill_before_clear=True)
   590	        self.assertEqual(killed.returncode, -signal.SIGKILL)
   591	        journal_path = calibration_ledger._append_journal_path(self.ledger)
   592	        evidence_path = calibration_ledger._append_recovery_path(
   593	            self.ledger, journal["operation_id"]
   594	        )
   595	        evidence = json.loads(evidence_path.read_bytes())
   596	        evidence["recovered_bytes"] = 1
   597	        mismatched = canonical_json_bytes(evidence) + b"\n"
   598	        evidence_path.write_bytes(mismatched)
   599	        ledger_before_retry = self.ledger.read_bytes()
   600	
   601	        with self.assertRaisesRegex(
   602	            CalibrationLedgerError, "append recovery evidence conflicts"
   603	        ):
   604	            abort_bracket_session(
   605	                self.ledger,
   606	                session_id="session-alpha",
   607	                reason="recover_torn_systematic_pre",
   608	            )
   609	        self.assertTrue(journal_path.exists())
   610	        self.assertEqual(self.ledger.read_bytes(), ledger_before_retry)
   611	        self.assertEqual(evidence_path.read_bytes(), mismatched)
   612	
   613	    def test_terminal_session_pin_refuses_complete_tail_with_stale_journal(
   614	        self,
   615	    ) -> None:
   616	        self._open_bracket_session()
   617	        self._finalize_bracket_slot("session-alpha", "pre")
   618	        killed = self._finalize_post_in_subprocess_before_journal_clear()
   619	        self.assertEqual(killed.returncode, -signal.SIGKILL)
   620	        self.assertTrue(
   621	            calibration_ledger._append_journal_path(self.ledger).exists()
   622	        )
   623	
   624	        with self.assertRaisesRegex(
   625	            CalibrationLedgerError,
   626	            "calibration_ledger_recovery_required",
   627	        ):
   628	            terminal_head_pin_for_session(
   629	                self.ledger,
   630	                session_id="session-alpha",
   631	            )
   632	
   633	    def test_standalone_recovery_heals_journal_without_adding_a_receipt(
   634	        self,
   635	    ) -> None:
   636	        self._open_bracket_session()
   637	        self._finalize_bracket_slot("session-alpha", "pre")
   638	        killed = self._finalize_post_in_subprocess_before_journal_clear()
   639	        self.assertEqual(killed.returncode, -signal.SIGKILL)
   640	        receipt_count_before = len(self.ledger.read_bytes().splitlines())
   641	
   642	        evidence_path = calibration_ledger.recover_calibration_ledger_append(
   643	            self.ledger
   644	        )
   645	
   646	        self.assertIsNotNone(evidence_path)
   647	        assert evidence_path is not None
   648	        self.assertTrue(evidence_path.is_file())
   649	        self.assertFalse(
   650	            calibration_ledger._append_journal_path(self.ledger).exists()
   651	        )
   652	        self.assertEqual(
   653	            len(self.ledger.read_bytes().splitlines()),
   654	            receipt_count_before,
   655	        )
   656	        self.assertEqual(
   657	            terminal_head_pin_for_session(
   658	                self.ledger,
   659	                session_id="session-alpha",
   660	            )["sequence"],
   661	            receipt_count_before,
   662	        )
   663	
   664	    def test_terminal_session_pin_classifies_journal_authenticated_torn_tail(
   665	        self,
   666	    ) -> None:
   667	        self._create_torn_session_finalization()
   668	
   669	        with self.assertRaisesRegex(
   670	            CalibrationLedgerError,
   671	            "calibration_ledger_recovery_required",
   672	        ):
   673	            terminal_head_pin_for_session(
   674	                self.ledger,
   675	                session_id="session-alpha",
   676	            )
   677	
   678	    def test_reservation_requires_complete_epoch_and_full_t1(self) -> None:
   679	        with self.assertRaisesRegex(
   680	            CalibrationLedgerError, "malformed receipt"
  1150	                plan_sha256="a" * 64,
  1151	                evidence_root_id="evidence-alpha",
  1152	                runs_root="/synthetic/root-alpha",
  1153	            )
  1154	        )
  1155	
  1156	    def test_ordinary_historical_window_still_evaluates_after_session_finalization(
  1157	        self,
  1158	    ) -> None:
  1159	        snapshot, candidates, _binding = self._bound_session_fixture()
  1160	        historical_times = {
  1161	            "attempt-neighbor-pre": 89.0,
  1162	            "attempt-neighbor-post": 96.0,
  1163	        }
  1164	        candidates = [
  1165	            replace(
  1166	                candidate,
  1167	                capture_wall_time_s=historical_times.get(
  1168	                    candidate.attempt_id,
  1169	                    candidate.capture_wall_time_s,
  1170	                ),
  1171	            )
  1172	            for candidate in candidates
  1173	        ]
  1174	        snapshot = replace(
  1175	            snapshot,
  1176	            observations=tuple(
  1177	                replace(
  1178	                    observation,
  1179	                    capture_wall_time_s=str(
  1180	                        historical_times.get(
  1181	                            observation.attempt_id,
  1182	                            observation.capture_wall_time_s,
  1183	                        )
  1184	                    ),
  1185	                )
  1186	                for observation in snapshot.observations
  1187	            ),
  1188	        )
  1189	
  1190	        with patch(
  1191	            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
  1192	            return_value=_unissued_acceptance_fixture(),
  1193	        ):
  1194	            result, reasons = _evaluate_calibration_bracket(
  1195	                candidates,
  1196	                window_start_s=90.0,
  1197	                window_end_s=95.0,
  1198	                bindings=self.bindings,
  1199	                policy=self.policy,
  1200	                ledger_snapshot=snapshot,
  1201	                _allow_unissued_fixture=True,
  1202	            )
  1203	
  1204	        self.assertEqual(reasons, ())
  1205	        self.assertEqual(result["status"], "passed")
  1206	        self.assertEqual(result["pre"]["attempt_id"], "attempt-neighbor-pre")
  1207	        self.assertEqual(result["post"]["attempt_id"], "attempt-neighbor-post")
  1208	
  1209	    def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
  1210	        snapshot, candidates, _binding = self._bound_session_fixture()
  1211	        session = snapshot.bracket_sessions[0]
  1212	        open_session = replace(
  1213	            session,
  1214	            state="open",
  1215	            finalized_slots=MappingProxyType({"pre": session.finalized_slots["pre"]}),
  1216	        )
  1217	        open_snapshot = replace(
  1218	            snapshot,
  1219	            observations=tuple(
  1220	                observation
  1221	                for observation in snapshot.observations
  1222	                if observation.bracket_slot != "post"
  1223	            ),
  1224	            bracket_sessions=(open_session,),
  1225	            head_sequence=4,

codex
All requested tests are complete and the repository remains clean. One final compatibility probe confirms whether the path fix only repairs alias-recorded sessions or also changes retry behavior for a pre-existing real-path reservation invoked through an alias; this determines whether that point is a defect or a migration note.
exec
/bin/zsh -lc "python3 - <<'PY'
import json,tempfile
from pathlib import Path
import joulewise.calibration_ledger as cl
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from scripts.validate_powermetrics_fiducial import _CaptureLedgerLifecycle

epoch={'os_build':'25F84','hardware_model':'Mac15,9','power_policy':'ac_high_power','sampling_interval_ms':100,'estimator_revision':'joint_loss_sublevel_interval_branch_v2','pulse_protocol_id':'powermetrics_pulse_fiducial_v3'}
t1={field:f'value-{field}' for field in V2_BINDING_FIELDS};t1.update(epoch)
with tempfile.TemporaryDirectory(prefix='u1-path-compat-') as td:
 root=Path(td); real=root/'real';real.mkdir();alias=root/'alias';alias.symlink_to(real,target_is_directory=True)
 ledger=root/'ledger';pin=root/'pin';pin.write_text(json.dumps({'sequence':0,'head_digest':cl.GENESIS_DIGEST,'ledger_schema':cl.LEDGER_SCHEMA})+'\\n')
 sid='compat';slots={r:{'attempt_id':f'{sid}-{r}','custody_locator':str(real/'instrument_validation'/f'{sid}-{r}'),'identity_epoch':epoch,'t1_bindings':t1} for r in ('pre','post')}
 cap=cl.append_bracket_session_receipt(ledger,session_id=sid,window_id='w',plan_id='p',plan_sha256='a'*64,evidence_root_id='e',runs_root=real,slots=slots,head_pin_path=pin,require_committed_pin=False)
 invoked=alias/'instrument_validation'/f'{sid}-pre'
 life=_CaptureLedgerLifecycle(ledger_path=ledger,head_pin_path=pin,attempt_id=f'{sid}-pre',custody_locator=str(invoked),identity_epoch=epoch,t1_bindings=t1,session_id=sid,slot='pre',require_committed_pin=False)
 try: life.begin(); result='accepted'
 except Exception as exc: result=str(exc)
 print(json.dumps({'recorded':cap['slots']['pre']['custody_locator'],'invoked_alias':str(invoked),'old_resolve_spelling':str(invoked.resolve()),'new_absolute_spelling':life.custody_locator,'new_result':result},indent=2))
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
{
  "recorded": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-yw3yolud/real/instrument_validation/compat-pre",
  "invoked_alias": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-yw3yolud/alias/instrument_validation/compat-pre",
  "old_resolve_spelling": "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-yw3yolud/real/instrument_validation/compat-pre",
  "new_absolute_spelling": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-yw3yolud/alias/instrument_validation/compat-pre",
  "new_result": "capture does not match the exact reserved bracket session slot"
}

exec
/bin/zsh -lc "python3 - <<'PY'
import json,tempfile
from pathlib import Path
import joulewise.calibration_ledger as cl
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from scripts.validate_powermetrics_fiducial import _CaptureLedgerLifecycle

epoch={'os_build':'25F84','hardware_model':'Mac15,9','power_policy':'ac_high_power','sampling_interval_ms':100,'estimator_revision':'joint_loss_sublevel_interval_branch_v2','pulse_protocol_id':'powermetrics_pulse_fiducial_v3'}
t1={field:f'value-{field}' for field in V2_BINDING_FIELDS};t1.update(epoch)
with tempfile.TemporaryDirectory(prefix='u1-path-compat-') as td:
 root=Path(td); real=root/'real';real.mkdir();canonical=real.resolve();alias=root/'alias';alias.symlink_to(real,target_is_directory=True)
 ledger=root/'ledger';pin=root/'pin';pin.write_text(json.dumps({'sequence':0,'head_digest':cl.GENESIS_DIGEST,'ledger_schema':cl.LEDGER_SCHEMA})+'\\n')
 sid='compat';slots={r:{'attempt_id':f'{sid}-{r}','custody_locator':str(canonical/'instrument_validation'/f'{sid}-{r}'),'identity_epoch':epoch,'t1_bindings':t1} for r in ('pre','post')}
 cap=cl.append_bracket_session_receipt(ledger,session_id=sid,window_id='w',plan_id='p',plan_sha256='a'*64,evidence_root_id='e',runs_root=canonical,slots=slots,head_pin_path=pin,require_committed_pin=False)
 invoked=alias/'instrument_validation'/f'{sid}-pre'; life=_CaptureLedgerLifecycle(ledger_path=ledger,head_pin_path=pin,attempt_id=f'{sid}-pre',custody_locator=str(invoked),identity_epoch=epoch,t1_bindings=t1,session_id=sid,slot='pre',require_committed_pin=False)
 try: life.begin(); result='accepted'
 except Exception as exc: result=str(exc)
 print(json.dumps({'recorded_canonical':cap['slots']['pre']['custody_locator'],'invoked_alias':str(invoked),'old_writer_resolve':str(invoked.resolve()),'old_would_match':str(invoked.resolve())==cap['slots']['pre']['custody_locator'],'new_writer_absolute':life.custody_locator,'new_matches':life.custody_locator==cap['slots']['pre']['custody_locator'],'new_result':result},indent=2))
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix
 succeeded in 0ms:
{
  "recorded_canonical": "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-npi8x8h6/real/instrument_validation/compat-pre",
  "invoked_alias": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-npi8x8h6/alias/instrument_validation/compat-pre",
  "old_writer_resolve": "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-npi8x8h6/real/instrument_validation/compat-pre",
  "old_would_match": true,
  "new_writer_absolute": "/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/u1-path-compat-npi8x8h6/alias/instrument_validation/compat-pre",
  "new_matches": false,
  "new_result": "capture does not match the exact reserved bracket session slot"
}

codex
| Charge | Disposition | Reproduced result |
|---|---|---|
| 1 — F1 | VERIFIED for original signature | A subprocess died after PRE finalization was fsynced but before journal clear. The normal POST writer retry removed the journal, emitted recovery evidence, and claimed POST. A malformed journal refused with the actual recovery condition, not the former false slot-mismatch text. |
| 2 — F2 | VERIFIED | After a later session was finalized, the historical ordinary window passed using its original endpoints with no binding. Withholding one of four registered candidates refused with calibration_ledger_off_ledger_artifact. |
| 3 — F4 | VERIFIED | Both a complete terminal tail with stale journal and a journal-authenticated partial tail emitted no pin and reported calibration_ledger_recovery_required—not malformed. |
| 4 — F5 | VERIFIED, compatibility note | Reservation and capture preserved the same symlink spelling and the writer claimed the slot. The regression exercises main(), not only the lifecycle library. |
| 5 — F6a | VERIFIED | In a two-process claim race, one writer succeeded and the other received operator prose: “a bracket session slot already has an exclusive writer claim.” No taxonomy code was exposed. |
| 6a — recovery hunt | BLOCKER — HIGH | The new standalone/automatic recovery route replays a zero-byte foreign journal. The probe appended 727 bytes from a foreign abort intent, returned recovery evidence, cleared the journal, and changed the target session to aborted. |
| 6b — L5 hunt | VERIFIED | A beta-window session temporally bracketing an alpha window refused as binding-invalid when presented as alpha; omitting the binding refused as binding-missing. |
| 6c — recorded-path hunt | BEHAVIOR CHANGE | A canonical real-path reservation invoked later through a symlink alias would previously match after resolve; it now refuses because lexical absolute spellings differ. No repository-held open bracket receipts were found, but out-of-repository capabilities require exact-spelling retries. |
| 7 — same-signature survival | NO / NO / NO / NO | Original strand-a-night recovery: no. Retroactive coupling: no. Journal-blind read: no. Path asymmetry: no. The foreign/zero-byte replay is a different recovery signature. |

## Conclusions

Verdict: **HOLD**. F1, F2, F4, F5, and F6a close their original defects, but the recovery change exposes a blocking state-mutation path.

The underlying zero-byte redo behavior predates this branch, but it is now directly public and automatically invoked before slot validation at [calibration_ledger.py:2455](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_ledger.py:2455) and [validate_powermetrics_fiducial.py:400](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/scripts/validate_powermetrics_fiducial.py:400). Empty suffixes are accepted and the missing payload is appended at [calibration_ledger.py:859](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_ledger.py:859) and [calibration_ledger.py:2362](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_ledger.py:2362). The current standalone regression covers only a complete tail, not a never-started or foreign operation, at [test_calibration_ledger.py:633](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/tests/test_calibration_ledger.py:633).

Required closure: do not automatically replay a journal with zero observed payload bytes; report it as an unstarted/abandoned intent or require explicit recovery authority. Recovery should also validate the expected operation/session and reconstructed chain before clearing the journal. Add never-started-abort and copied-foreign-journal regressions.

The F2 ordering is sound: complete-universe equality remains before the window-local predicate at [calibration_bracketing.py:1240](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_bracketing.py:1240). The F5 regression reaches main() at [test_powermetrics_fiducial.py:1280](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/tests/test_powermetrics_fiducial.py:1280).

Focused suite tails:

- Ledger: Ran 51 tests in 9.876s — OK.
- Bracketing: Ran 40 tests in 3.470s — OK.
- Fiducial: Ran 42 tests in 29.383s — OK.
- Combined focused run: Ran 133 tests in 41.596s — OK.
- Canonical suite: Ran 2739 tests in 622.872s — OK, skipped=90.

Checks performed: read both source findings first—the corroborating review is stored as `OPUS-POSTMERGE-U1U3.md`; inspected HEAD 880b6bc against origin/main ca8eea9; ran independent subprocess-crash, concurrent-race, historical-window, anti-withholding, L5, symlink/main, foreign-journal, and path-compatibility probes in temporary directories; ran focused and canonical suites; ran diff whitespace validation; final worktree remained clean.
tokens used
218,388
| Charge | Disposition | Reproduced result |
|---|---|---|
| 1 — F1 | VERIFIED for original signature | A subprocess died after PRE finalization was fsynced but before journal clear. The normal POST writer retry removed the journal, emitted recovery evidence, and claimed POST. A malformed journal refused with the actual recovery condition, not the former false slot-mismatch text. |
| 2 — F2 | VERIFIED | After a later session was finalized, the historical ordinary window passed using its original endpoints with no binding. Withholding one of four registered candidates refused with calibration_ledger_off_ledger_artifact. |
| 3 — F4 | VERIFIED | Both a complete terminal tail with stale journal and a journal-authenticated partial tail emitted no pin and reported calibration_ledger_recovery_required—not malformed. |
| 4 — F5 | VERIFIED, compatibility note | Reservation and capture preserved the same symlink spelling and the writer claimed the slot. The regression exercises main(), not only the lifecycle library. |
| 5 — F6a | VERIFIED | In a two-process claim race, one writer succeeded and the other received operator prose: “a bracket session slot already has an exclusive writer claim.” No taxonomy code was exposed. |
| 6a — recovery hunt | BLOCKER — HIGH | The new standalone/automatic recovery route replays a zero-byte foreign journal. The probe appended 727 bytes from a foreign abort intent, returned recovery evidence, cleared the journal, and changed the target session to aborted. |
| 6b — L5 hunt | VERIFIED | A beta-window session temporally bracketing an alpha window refused as binding-invalid when presented as alpha; omitting the binding refused as binding-missing. |
| 6c — recorded-path hunt | BEHAVIOR CHANGE | A canonical real-path reservation invoked later through a symlink alias would previously match after resolve; it now refuses because lexical absolute spellings differ. No repository-held open bracket receipts were found, but out-of-repository capabilities require exact-spelling retries. |
| 7 — same-signature survival | NO / NO / NO / NO | Original strand-a-night recovery: no. Retroactive coupling: no. Journal-blind read: no. Path asymmetry: no. The foreign/zero-byte replay is a different recovery signature. |

## Conclusions

Verdict: **HOLD**. F1, F2, F4, F5, and F6a close their original defects, but the recovery change exposes a blocking state-mutation path.

The underlying zero-byte redo behavior predates this branch, but it is now directly public and automatically invoked before slot validation at [calibration_ledger.py:2455](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_ledger.py:2455) and [validate_powermetrics_fiducial.py:400](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/scripts/validate_powermetrics_fiducial.py:400). Empty suffixes are accepted and the missing payload is appended at [calibration_ledger.py:859](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_ledger.py:859) and [calibration_ledger.py:2362](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_ledger.py:2362). The current standalone regression covers only a complete tail, not a never-started or foreign operation, at [test_calibration_ledger.py:633](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/tests/test_calibration_ledger.py:633).

Required closure: do not automatically replay a journal with zero observed payload bytes; report it as an unstarted/abandoned intent or require explicit recovery authority. Recovery should also validate the expected operation/session and reconstructed chain before clearing the journal. Add never-started-abort and copied-foreign-journal regressions.

The F2 ordering is sound: complete-universe equality remains before the window-local predicate at [calibration_bracketing.py:1240](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/joulewise/calibration_bracketing.py:1240). The F5 regression reaches main() at [test_powermetrics_fiducial.py:1280](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1fix/tests/test_powermetrics_fiducial.py:1280).

Focused suite tails:

- Ledger: Ran 51 tests in 9.876s — OK.
- Bracketing: Ran 40 tests in 3.470s — OK.
- Fiducial: Ran 42 tests in 29.383s — OK.
- Combined focused run: Ran 133 tests in 41.596s — OK.
- Canonical suite: Ran 2739 tests in 622.872s — OK, skipped=90.

Checks performed: read both source findings first—the corroborating review is stored as `OPUS-POSTMERGE-U1U3.md`; inspected HEAD 880b6bc against origin/main ca8eea9; ran independent subprocess-crash, concurrent-race, historical-window, anti-withholding, L5, symlink/main, foreign-journal, and path-compatibility probes in temporary directories; ran focused and canonical suites; ran diff whitespace validation; final worktree remained clean.
