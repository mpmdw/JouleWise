# Draft kernel row — T0-REHEARSAL-PRODUCERS-01

**Status of this file:** a DRAFT row for the magistrate to register. It is not a
kernel row yet, and nothing here binds until it is one. Written 2026-08-26 by
the T0-UNATTENDED-01 stream at the magistrate's instruction, from that row's
first rehearsal-evaluator audit.

**Proposed id:** `T0-REHEARSAL-PRODUCERS-01`
**Proposed lane:** agent · **Proposed priority:** p1_phase_gate
**Proposed dependencies:** `T0-UNATTENDED-01` (its evaluator is the consumer
these producers must satisfy)

---

## The forcing problem, in one paragraph

`T0-UNATTENDED-01` landed a mechanical evaluator for the ruled ten-gate
supervised rehearsal. An **evaluator** here is a program that reads custodied
bytes and returns a verdict; it never performs the rehearsal. Its first
independent audit returned REFUTE, and the structural finding was not a bug in
the evaluator's logic: **no producer writes the records seven of its ten gates
need.** A **producer** is a program that runs during the window and writes
evidence — `scripts/capture_t0_step.py`, `joulewise/arm_readiness_evidence_t0.py`,
`scripts/collect_clock_reference.py`, and whatever mechanically issues the D-149
receipt. Against real evidence those seven gates can therefore only ever return
`UNRULED`, which the evaluator's honesty rule correctly refuses to count as a
pass. The instrument exists; the thing it measures is not being recorded.

Closing that gap means re-opening the T-0 author and the capture ceremony to
emit new records. That is exactly why it is a separate row: it is
producer-side work on the most safety-critical modules in the repository, and
`T0-UNATTENDED-01`'s ruled scope is the T-0 *evidence* change, not the
rehearsal instrumentation.

## Goal

Make the ruled ten-gate supervised rehearsal actually evaluable against real
window evidence, by having the T-0 producers record the gate-bearing facts they
do not record today — so that a live rehearsal returns PASS or FAIL on
mechanism rather than `INCOMPLETE` on absence.

## Acceptance evidence (proposed)

1. Every gate the evaluator marks `UNRULED` for missing evidence has a named
   producer writing that evidence, and a live-shaped fixture built only from
   what the producers actually emit evaluates to PASS or FAIL — never
   `INCOMPLETE` for absence. The evaluator's existing
   `REHEARSAL_PRODUCER_WORK_ORDER` table (`joulewise/t0_rehearsal.py`) is the
   enumerated checklist: every entry is either discharged by a producer change
   or struck with a recorded reason.
2. The six gates that today accept **self-declared** evidence instead
   authenticate it, and each authentication is defect-shaped: G2's census is
   exhaustive over the on-disk T-0 namespace rather than a declared manifest;
   G3's HIDIdleTime witness carries argv, raw stdout, boot session and an
   in-sequence monotonic stamp, all checked; G5 evaluates D-149 C1–C5 from
   underlying evidence rather than declared statuses; G6 grounds the
   production-root set in the repository and proves ledger/roots/backup
   dedication as real paths; G8's agent-process matching catches hyphenated,
   suffixed and path-qualified spellings (`codex-helper`, `claude-code`,
   `/usr/local/bin/codex-run`); G10's positive control carries raw command
   output, timestamp, boot session and a hash binding.
3. The honesty rule survives untouched: anything unevaluable is `UNRULED` or
   `FAIL`, never `PASS`; overall `PASS` requires every gate `PASS`; `INCOMPLETE`
   never counts as success. A regression proves a fully passing bundle with one
   gate unevaluable does not return `PASS`.
4. No producer change weakens a T-0 refusal or alters the published
   `clock.correct_and_prior_state.v1` PROBE value's key set; the live
   `REASON_CODE_COVERAGE` gate stays at registered 55 / produced 45 / dynamic 10
   with the `dynamic` set unchanged, and no new reason code is added in either
   vocabulary without the exhaustive registration path in the T0 delta
   document's §4.5.

## Fences (proposed)

- **This row re-opens the T-0 author and the capture ceremony
  (`joulewise/arm_readiness_evidence_t0.py`, `scripts/capture_t0_step.py`) and
  therefore runs the full C-028 gauntlet**: enforced `WRITE_SCOPE`, independent
  audit that never self-grades, severity-tiered refuters with distinct lenses,
  and a delta re-audit of every fix round. Mutation-shaped auditing is
  mandatory: the T0 core round's five blockers were ALL found by deleting a
  gate and observing that its named test still passed.
- **Additive only.** New records are added; no existing T-0 record's schema,
  key set, or refusal is changed. A producer change that alters what the
  arm-side predicate consumes is out of scope and returns to the magistrate.
- **G7 is not this row's.** The production consumer of the D-149 GO receipt is
  ruled to `UNATTENDED-LAUNCH-01` (2026-08-26). This row must not build it and
  must not let G7 stop reporting `UNRULED`.
- **The 5 s issuance bound is COLD-GATE-PENDING** and must not be
  reinterpreted, relaxed, or implemented here — including as "predicate
  recency".
- **Ed-hands items stay Ed's**: the live rehearsal sitting, the privileged
  anchor positive control, and the sudoers install/exercise are surfaced as
  NEEDS-ED, never assumed.

## Authority

- `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`
  (the ruled ten-gate rehearsal)
- `docs/process_traces/2026-08-23-t22/t0-unattended/debate-sol-critique.md` §2(c)
  (the ruled table itself, ten rows with their pass conditions)
- `docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md`
  (RF-26..RF-35 and the §5 rule that a green happy-path gate is not evidence a
  refusal fires)

## Starting material

The killed fix round for the six self-declaration blockers is preserved as a
diff at `scratchpad/t26/s2/p14-PARTIAL-KILLED.diff` (it left 21/31 tests failing
and was reverted, so it is a starting point, not a patch to apply). The
evaluator's `REHEARSAL_PRODUCER_WORK_ORDER` table already names, per gate, the
record needed, the producer that would have to write it, and the field names.
