# Cold-gate packet: D-169 STAGE 3 — unattended PACK-BOUND launch (design ruling before any implementation scope)

Assembled mechanically by the interactive magistrate at 2026-09-08 ~09:10 PDT. Rule-11 trigger: a proposed
architecture for an irreversible, claim-bearing path (unattended pack-bound measurement nights) — the kind of
decision the magistrate must not take alone.

## Question
Stage 3 of D-169 must let the night driver run a TRANSACTION_PACK night unattended: prepare the pack, issue an
evidence-backed D-149 GO receipt (conditions C1–C5), consume it in the sole launcher with durable binding, keep the
confirmation-pair custody, and close the T-0 rehearsal obligations — without weakening any fail-closed fence (T-0
evidence, pre-registration, quiet-Mac census, custody, D-165 honesty of receipt classes). Exhibit A (an Astra high
consult, read-only, file:line evidence) enumerates five missing mechanisms (R1–R5) and one reconciliation (R6) and
proposes the smallest sound design: "a pack-specific orchestration path in the existing night driver, one
authenticated D-149 receipt contract, and enforcement inside the existing launch-capability consumer", retaining
the scheduler, watchdog, courier, atomic launch consumption, anonymous-FD handoff and frozen pack chain; D-171
already delegates E-10 invocation, transaction GO and step-6 confirmation, so per-window Ed permission is not the
missing mechanism.

## Decisions the judge must rule (from exhibit A flag F1 and findings R1–R6)
1. Receipt binding: what the D-149 GO receipt must bind (pack digest, ARM identity, T-0 evidence set, plan id,
   measurement_root/head, validity window) and how the launcher authenticates it INSIDE `_consume_launch_capability`
   (not only at the CLI), records it in the atomic consumption record, and replays it through `verify_consumed_launch`.
2. G2-b authorization (R5): G2-b is pack-bound but qualifies the transaction it precedes; rule how its receipt class is
   authorized without either granting it a measurement GO it has not earned or blocking it behind the very GO it
   produces evidence for.
3. Confirmation custody (R3): where the unattended confirmation pair lives, who writes it, and how the inheritance
   route survives a magistrate relaunch.
4. Rehearsal execution authority (R4): what closes the T-0 rehearsal obligation with authenticated producer evidence;
   can G2-a (DIAGNOSTIC_NO_PACK) discharge any of it, and which parts need a pack-bound rehearsal.
5. Dependency installation (R6): the kernel rows to create/retarget (UNATTENDED-LAUNCH-01, S9-06-WINDOW-T0-GO-RECEIPT-
   GATE-01, D169-STAGE3-01, NIGHT-REHEARSAL-01 successors) so decided ≠ done cannot recur.
6. The implementation order and gate shape (seats, scopes, tests, replay obligations, cold gates) for the minimal
   design — or a different design if the judge finds the consult's smaller than sound.

## Charge
For each decision: UPHOLD the consult's proposal, AMEND (exact text), or REJECT with the alternative. Test each
against the failure the fences exist to prevent: a night that measures without a custodied, evidence-backed GO; a
receipt that can be forged or replayed; a census bypass; a pre-registration drift. Answer the packet's six items in
order; executed probes where feasible (read-only); NOT EXECUTED otherwise. Write the ruling to
./coldgate-packet-3/10-coldgate-fable-ruling.md.

## Exhibits
A consult report (Astra high, 2026-09-08); B readiness scout (trace 27); C stage-1 ruling head (first 120 lines of
MAGISTRATE-RULING-UNATTENDED-STAGE1.md; read the whole file at this checkout); D kernel rows naming D-169 / launch;
E decision-log pointers (read those D-149/D-167/D-169/D-171 entries at this checkout).
