# RUN CARD — shakedown-v3 first light (instrument verification, NON-CLAIM)

Purpose (D-139 SHAKEDOWN-FIRST directive): the first quiet block after
READY-candidate clears is minimal instrument-verification capture under
the CURRENT pipeline (anchor-v3 capture, r6 acceptance, `_v3` family) —
diagnostic evidence only, never claim-bearing. Claims start only after
this card's in-band check passes.

## Preconditions (all five D-149 GO conditions; receipt per the template)

docs/process/d149-go-receipt-template.md — filled, custodied, GO.
Additionally for this card: the merge wave has landed on main (the
window must run frozen-main bytes, not a branch), and the custody root
is fresh under ~/JouleWise-window-custody/ (new dated dir; driver +
pristine-ledger pattern per
docs/process_traces/2026-08-18-t10-t11-working-notes/shakedown-driver.sh
— clone updated to the merged head FIRST, as the T11 night plan
specified for its shakedown clone).

## The block (single capture class, strictly sequential)

1. Census + GO receipt (attach outputs to custody root).
2. ONE fixed-work calibration capture (protocol v3, 59 pulses) under the
   live r6 acceptance — the same class as the 2026-08-18 first light.
3. Immediate reduction at the custody clone: derive b_fiducial under the
   CURRENT estimator.
4. IN-BAND CHECK: the derived b_fiducial lies inside the r6 corpus band
   [0.0232, 0.0329] s — the artifact's own member min/max
   (min 0.02317490442656863, max 0.03289849371536248; quote exact bytes
   in the record). NOTE the 2026-08-18 first light (0.0309 s) was
   in-band under the SUPERSEDED estimator and band — this is the first
   in-band test that is v3-native end to end.
5. Idle baseline (ten minutes) with the graphics-rail silence check, as
   on 2026-08-18.
6. Custody close: hashes, backup, refusal log (empty or not — recorded).

## Refusal handling (D-078 binds)

Any refusal (budget, anchor, admission) ENDS the block. Diagnose from
the recorded reason read-only; no re-arm without a diagnosed, removed
cause; the refusal is itself reportable instrument evidence (the paper's
§5 pattern: refused-first-diagnosed-then is the instrument working).

## Outcomes

- IN-BAND → the alpha floor window is next (its own card; own GO
  receipt); the paper's characterization section gains the v3-native
  verification event.
- OUT-OF-BAND or refused → STOP the window lane; the result goes to a
  council consult before any further capture (out-of-band under v3 would
  be the first such event on the corrected instrument — treat as a
  finding, not a nuisance).
