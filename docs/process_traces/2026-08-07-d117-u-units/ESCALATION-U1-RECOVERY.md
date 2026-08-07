# ESCALATION — the append-recovery subsystem (2026-08-07)

**Ruling: STOP PATCHING. Split the branch. Consult on the recovery
subsystem's shape. The night-critical fixes land WITHOUT it.**

## Why this is an escalation, not a fourth fix

The append-recovery subsystem has produced a distinct defect at every
round:

1. **Round 1 (U1 original):** torn-tail unrecoverable — recovery evidence
   written but the journal not cleared left governed closure permanently
   blocked. Closed by FIX-6b (idempotent recovery).
2. **Round 2 (gate-debt F1):** recovery unreachable from the writer's
   retry path — a false refusal that never reached the healing code.
   Closed — but the fix INTRODUCED auto-replay of a zero-payload
   (never-started or foreign) journal.
3. **Round 3 (narrow hardening):** zero-byte replay closed and mutation-
   verified — but the final-head review reports **same-signature YES**:
   a foreign journal whose payload shares a positive prefix with the
   target operation can still be replayed. AND the refusal introduced a
   state with **no governed operator exit** — exactly the failure mode
   the lead charged the reviewer to hunt.

Three rounds, three defects, and the class is alive. Under rule 11's
standing trigger and D-118 item 5, the next spend is a CONSULT on the
SHAPE, not another patch. The pattern says the subsystem's design is the
problem, not its details: a sidecar journal beside an append-only custody
ledger keeps producing states that are neither safely replayable nor
safely abandonable.

## Consult charge (queued)

Does an append-only custody ledger need a sidecar redo-journal at all, or
is there a shape with no second source of truth (e.g. self-describing
append records that make a torn tail recognizable from the ledger alone)?
If a journal is retained: what binds it to its target operation such that
a foreign or stale journal can never be replayed regardless of prefix
agreement, and what is the GOVERNED, DURABLE abandonment path an operator
can take at 2am? The answer must not add an operator-privileged escape
that reopens the trust questions adjudicated today.

## Immediate disposition — SPLIT, do not hold everything

The night-critical fixes are INDEPENDENT of the recovery work and are
delta-verified clean:

- **F2** — session candidacy keyed to the window under evaluation
  (stops the first finalized session silently making bindings mandatory
  for every historical window). Anti-withholding preserved and verified.
- **F5** — unified path normalization with a symlinked-root regression,
  independently corroborated by the cross-unit integration review.
- **F4** — journal-aware terminal head-pin reads.
- **F6a** — operator prose on the racing slot-claim refusal.

These land. **F1 (the standalone recovery entry point) and the recovery
hardening HOLD** pending the consult. Rationale: F2 is a night-critical
correctness defect on main right now; holding it hostage to an unresolved
subsystem would trade a certain harm for a speculative one. The recovery
gap that F1 addressed remains open and is documented for the operator
runbook as a manual procedure until the consult closes.

**Recorded honestly:** the lead's charge to the final-head reviewer
explicitly asked whether refusing zero-byte intents could create an
unexitable state. It does. Asking the question was right; the fix should
not have been launched as "narrow" before the shape was settled.
