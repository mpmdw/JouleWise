# Escalation 2: unexecuted-proof at COUNT 2 + convergent under-proving signature (2026-08-08 afternoon)

**Trigger** (standing rule 11, armed in writing by GAUNTLET-TRIAGE and
the T0 checkpoint): the fresh delta re-audit of the FIX-1..13 round
(`DELTA-1-PROMPT.md` → `DELTA-1-REPORT.md`, Sol xhigh, verdict FAIL)
found the **unexecuted-proof class ALIVE at same-signature COUNT 2**
(P1-2: the three corrected-writer witnesses call ledger readiness
directly instead of executing the corrected writer; a temporary-copy
mutation making the real writer's `--allow-live` check always refuse
survived the QUIET_MAC_AUTH_REQUIRED witness). Per the standing rule
the next spend is a CONSULT, never a third fix formulation.

**Convergent signature folded into the same escalation** (each is a
second consecutive round failing the same way — another missed site or
another failed formulation — so none licenses a loop fix on its own):

- P1-1 / FIX-2: lease identity keyed by `realpath` only; hard-linked
  aliases (same st_dev/st_ino) still acquire two concurrent writer
  leases. Second failed formulation of the identity contract (round 1:
  lexical; fix: realpath).
- P1-3 / FIX-5: the FINALIZATION_BINDING_CONFLICT preservation witness
  fingerprints AFTER the first refusal handler runs; a
  refusal-handler-corrupts-custody mutation survives. Second round in
  which preservation is asserted over the wrong span.
- P2-1 / FIX-12: the standing positional-receipt lint matches only
  variables literally named `*receipt*`; `business_rows[1:]` and
  `marker_removed[1]` pass. Second round in which the prohibited
  positional shape survives detection.
- P1-4 (first occurrence, folded for design coherence): the crash
  harness starts writers with plain `subprocess.run` (no
  start_new_session / process-group kill / addCleanup); the writer's
  self-SIGKILL leaves its real sampler child alive (probe:
  `sampler_alive_after_writer_sigkill=true`; POST-SUITE process-group
  survivors observed on both focused and full runs). This confirms the
  bench observation in the T0 checkpoint notes (8 orphaned children,
  lead-killed). Delta evidence also bounds the damage: a clean-room
  full suite matched the fix round's counts (2770 OK, skipped=90,
  +2.83s) — no timing distortion materialized, but the exposure is
  structural (1s readiness deadlines, 50ms rollover, 5s/10s waits).

**Class verdicts recorded:** unexecuted-proof ALIVE (count 2);
**inspect-as-permission DEAD** (tree-wide sweep: the sole production
`ready_to_arm` projection is gated by `enforcing_under_lease`;
diagnostic routes cannot feed an arming path).

**MAGISTRATE RULING R-FIX9 (delta flag R1, ruled here):** FIX-9's
authorization of env/config-controlled crash points at REAL production
write sites STANDS (real-site kills are the discriminating point), AND
the delta's production-inertness requirement ALSO stands. They compose:
crash hooks must be DOUBLE-KEYED so that ambient environment alone can
never arm them on an ordinary invocation — the consult designs the
exact mechanism (test-context token or equivalent), plus the standing
inertness regression (ordinary invocation with the ambient variable set
must not crash and must surface a diagnostic).

**Non-blocking flags adjudicated:** R3 diff-scope discrepancy (12 vs 15
files) is benign — the three gauntlet records ride the fix commit;
trailing whitespace in Lens B is a historical record, left as-is.

**Next spend:** one bounded Sol xhigh design consult
(`ESCALATION-2-CONSULT-PROMPT.md` → `ESCALATION-2-CONSULT.md` when
harvested) demanding TERMINATING designs for the five items; then ONE
consult-shaped dictated fix round (FIX-14..) with defect-shaped
regressions; then a fresh delta. The arming blocker stays up
throughout.
