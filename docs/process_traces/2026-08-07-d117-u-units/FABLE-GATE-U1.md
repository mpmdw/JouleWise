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

## Prior-layer overlap statement
FIX-1..8 + FIX-6b closures were spot-verified against the merged code (pin-route
refusal, claim exclusivity, aborted-PRE universe retention with the stale-trigger
early return, terminal-state candidate gating, journal recovery idempotence
shape) — all present as reported. F1, F2, F4, F5 do not appear in any U1 trace;
they are this gate's new ground. F3 is the gate's answer to a question the
implementation lenses were structurally not asked.

## Recommended disposition
Accept the merge (nothing here voids evidence). Queue before night 1:
- F1 + F4 as one small PR (recovery entry point + journal-aware terminal pin +
  recovery-aware refusal text) — these are the strand-a-night items.
- F2 as a 5-line predicate fix OR a ratification entry — decide, don't drift.
- F5 shared normalization + one `main()`-path symlink regression.
- F3 runbook section, rehearsed once.
- F6/F7 fold into any later touch of these files; none justify a dedicated PR.

---
## CORROBORATION (magistrate note, 2026-08-07)

The independent post-merge cross-unit integration review (see
POSTMERGE-INTEGRATION-REVIEW.md) reached this gate's F5 finding by a
different route: it constructed a U1 -> U3 binding directly and found the
symlink-path case FAILS while the canonical-path control PASSES. It also
identified WHY every prior layer missed it — the test fixtures normalize
both sides with resolve(), so the disagreement is invisible in tests and
appears only against a real symlinked root. On macOS all of /tmp is
symlinked, which is where quiet-window scratch paths live.

Two independent apex-tier reviews converging on the same defect by
different methods raises F5 from MEDIUM to a night-critical fix. It is
already in the running U1 gate-debt fix round as FIX-F5.

Otherwise the integration review corroborates cross-unit agreement:
terminal derivation 76 + 3x5 = 91; binding_digest vs
bracket_binding_sha256 domains intentionally distinct; the 0.010818
allowance arithmetic agreeing across U1/U3/U4 (rule STRINGS differ —
symbolic in U1, literal-expanded in U3 — worth unifying later); issued
prefix consistently 76 with 30/2/6 dispositions; U4's private-seam
dependencies intact after the sequential merge. Full suite on merged
main: Ran 2733, OK, exit 0.
