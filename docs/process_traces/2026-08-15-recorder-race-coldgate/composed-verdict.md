# COMPOSED RECORDER-RACE GATE VERDICT (magistrate rule-9 synthesis, 2026-08-15)

Seats: coldgate-adjudicator-ruling.md (race out-of-model, regrade should-fix, license nofollow-read
redirect) vs coldgate-opus-refuter-findings.md (contract SILENT not out-of-model; F-9 standing
trigger fired; license NEITHER caller-side closure; register limitation + queue clause-2 amendment;
land F-5 + F-10). The refuter's evidence is strictly stronger (all executed, incl. an uninstrumented
race and a silent-success attack the adjudicator's static E-series did not surface), so it CONTROLS
where the seats conflict. Both seats AGREE on the two merge-relevant facts: the race is real, and
receipt integrity is intact today (every post-grant read is hash-pinned — F-6 / adjudicator §i).

## RULING

1. **NO caller-side "closure" is licensed.** The content-bind is inert (both seats). The
   fd-identity alternative is hardlink-defeated (refuter F-4). The adjudicator's nofollow-read
   redirect is a caller-side fix and the two seats did not even converge on whether it closes
   REPLAY D — which is itself the proof F-9 makes: the root cause is that
   allow_governed_extraction_spec RE-RESOLVES the caller's path inside the callee
   (authentication_io.py:352), and no caller-side patch makes that atomic. **F-9's standing
   escalation trigger is AFFIRMED: two rounds, same signature — the next spend is a ruling, not
   round three.**

2. **Threat-model ruling (conservative, per soundness-above-all):** the concurrent unprivileged
   local writer is NOT ruled out of model. The contract is silent (not exclusionary), L2's
   sibling finding was confirmed-and-withheld pending exactly this ruling, and every precedent
   (the caffeinate volatile-census blocker; the A→B→A TOCTOU design kill; the ledger lock's own
   hardlink-fail-closed hardening) grades this class blocker-and-fix. I decline to purchase a
   merge by declaring it out of model. **BUT** receipt integrity is intact today (both seats), so
   the race is NOT launch-blocking and NOT blocking the recorder's PURPOSE (curing the
   close-out-halt blocker L4-B1).

3. **The real cure is a clause-2 amendment**, not a caller-side patch: stop the grant re-resolving
   (accept a caller-verified identity verbatim, or key the grant on an fd / (st_dev,st_ino)), which
   requires editing joulewise/authentication_io.py — the authority plane. That is its OWN future
   rule-11 cold gate. **Queued as WO-RECORDER-GRANT-IDENTITY** (decision log). F-10's post-grant
   grant-delta verification folds INTO that WO (it needs the read-only accessor clause 2 currently
   forbids — landing it now with private-field coupling is the expedient the gate warns against;
   receipt integrity does not need it today). This DEFERS, not overrules, F-10 — the finding is
   valid and queued with its accessor.

4. **Land NOW (unconditional, both seats, independent of the threat-model question):** F-5 — the
   unnormalized V2AuthenticationInputError escaping _pack_inventory on a NON-adversarial path
   (_json_object calls read_authentication_input outside its try). A genuine S1-table violation
   both rounds missed. Bench fix on the branch, delta-audited.

5. **Recorder branch disposition:** MERGES on receipt-soundness — the original blocker cured
   (RECEIPT_STATUS=PASS on the real frozen pack), the round-1 static-invariance guard retained
   (closes every NON-raced alias attack), F-5 landed — WITH the race recorded as a registered
   limitation (decision log, L1 shape) and clause-1's letter-violation-under-race noted. Holding
   the close-out fix hostage to an authority-plane amendment, for a race that cannot forge a
   receipt today, is the wrong trade.

6. **ED NOTE (non-blocking, batched):** the threat-model non-exclusion in (2) is a risk-appetite
   call (lead/Ed-weighted). If Ed's appetite rules the concurrent local writer out of model on a
   single-operator machine, WO-RECORDER-GRANT-IDENTITY is unnecessary and drops to the registered
   limitation alone — saving the authority-plane amendment. Surfaced with both cold rulings at the
   batched session; nothing blocks on it.

7. **Doc-defect cleanup (mechanic packet anomaly 5):** the M-2 GATE AMENDMENT block is misfiled
   INSIDE the recorder adoption entry in docs/decision_log.md (no heading break). Corrected in the
   same edit pass — it belongs to the M-2 instrument, not the recorder.

No written dissent is filed against either seat: the refuter's controlling findings are adopted;
the adjudicator's factual E-series (race confirmed, G1 mutation) is credited; the one place the
adjudicator is not followed (licensing the nofollow redirect as a closure) is exactly where F-9
and the refuter's executed evidence override it.
