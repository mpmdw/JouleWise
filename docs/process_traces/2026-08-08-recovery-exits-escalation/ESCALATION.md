# ESCALATION — the ungoverned-refusal class at count 2, across layers (2026-08-08)

**Ruling: the standing escalation trigger FIRES on the recovery branch.
No fix round 2. The next spend is a consult on EXIT COMPLETENESS as a
system property.**

## The count

1. **Audit round 1** (recovery branch): reproduced a deletion-only
   state in the LEDGER layer (junk + orphaned chain-shaped finalization:
   repair refused, abandon-tail refused). Fixed in round 1; the
   tripwire delta verified those sites dead and ruled the class
   terminated *at the ledger protocol layer* — correctly, as far as it
   looked.
2. **Opus counter-review, same head** (`c0e0257`): the class alive at a
   NEW site one layer up, PROVEN BY EXECUTED PROBES (custodied in the
   reviewer's report): the WRITER's per-process `claim_id`
   (uuid4-per-process, validate_powermetrics_fiducial.py:387) is
   excluded from the ledger operation key but included in the
   idempotency equality (calibration_ledger.py:~3420). After the
   design's own canonical crash (die between intent fsync and target
   fsync), recovery deterministically completes the target — the
   protocol WORKS — and then every restarted process refuses forever
   ("operation key conflicts with its durable target commitment", a
   fail-fast marker, no retry). All three governed exits proven
   non-functional for this state: repair reports clean; abandon-tail
   silently no-ops on empty residue; the writer's governed abort is
   unreachable pre-`begun`. The only working exit
   (`abort_bracket_session`) has no CLI and no runbook mention.
3. **Companion blocker (B2):** the runbook D-117 amendment — the
   arming-blocker discharge — was appended as a `###` under
   `## 13. Open questions for Ed`, whose banner reads "Nothing in this
   section is in force. Do not act on any of it during a window."

## Why this is structural, not a site bug

Three DIFFERENT components have now each independently produced a
refused state with no governed exit: the sidecar journal (rounds 1-3,
old design), the new ledger protocol (audit round 1), and now the
writer/CLI/runbook layer above a sound protocol. The class regenerates
at LAYER BOUNDARIES: each layer's exits are verified within the layer,
and the composition is never verified as a system. Patching claim_id
(bench-sized, shape already identified by the reviewer: derive it
deterministically from (session_id, slot, attempt_id) or drop it from
the idempotency equality) would close site four of a class that has
now demonstrated it will find site five.

## Consult charge (launched with this record)

Design the invariant that makes the class UNCONSTRUCTIBLE: for every
refusal any layer can emit on the unattended path (ledger, writer,
recovery CLI, runbook procedure), there must exist a governed exit
reachable by an operator with only the runbook and the CLI — and that
property must be ENFORCED, not reviewed into existence: an exhaustive
machine-checkable inventory (refusal -> exit mapping) with a test that
fails when a new refusal lacks a mapped exit, plus the crash-matrix
extended to the WRITER layer (process death at every writer stage, then
a FRESH process with FRESH ephemeral state must reach completion or a
governed exit — the exact probe shape the reviewer used). The consult
also rules: claim_id's correct shape; whether fail-fast markers may
ever cover idempotency conflicts; the runbook amendment's correct
placement per its own convention; and what the readiness gate must
verify so a wedged state is caught at ARM time, never at 2am.

## Interim disposition

The recovery branch stays open, un-PR'd. Its (b)-direction soundness is
banked (the reviewer's consumer sweep found NO path that admits a
control receipt as calibration evidence — the custody core is clean).
The arming blocker remains OPEN. Should-fixes S1-S5 and the three CLI
prune items ride the post-consult round.
