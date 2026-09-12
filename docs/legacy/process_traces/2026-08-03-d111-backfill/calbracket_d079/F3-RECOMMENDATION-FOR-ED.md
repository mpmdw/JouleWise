# CAL-BRACKET-D079-01 F3 — refined recommendation after fix investigation (2026-08-03)

Ed asked to investigate fixes beyond the A-vs-B binary. Result: there IS
a better option, and the "C" middle path I floated does NOT work.
Full investigation: F3-fix-investigation.md (this dir).

## The refined recommendation: A-MIN (writer-enforced receipt ledger)

Repository tracing found there is exactly ONE production writer of
calibration artifacts (scripts/validate_powermetrics_fiducial.py). That
single choke point changes everything: completeness can be enforced at
the WRITE boundary — every valid or failed capture atomically publishes
a compact receipt into a canonical ledger — instead of scanning
arbitrary directories at read time or trusting a caller's claim that its
list is complete. This is the SOUND version of Option A but WITHOUT the
"registry service threaded through everything" weight the first consult
feared: one writer updates the ledger; the acceptance artifact pins the
ledger's baseline head; evaluation requires baseline ⊆ current authentic
ledger head, judges new entries under the prior artifact, and REFUSES if
the ledger head is missing/truncated/rolled-back. It fails CLOSED on an
unobserved range-expander, and it is a faithful IMPLEMENTATION of D-102
(no weakening amendment needed — unlike B).

Why the cheaper ideas fail:
- **C-bare (my earlier middle option): does NOT work.** A caller-supplied
  root list + hashes authenticates WHAT WAS LISTED, not that an omitted
  root doesn't exist. Same actor controls the evidence and the
  completeness claim → no independent trust root → does not fail closed.
- **B (narrow D-102): still needs your signed amendment** and still
  leaves the real hole (an expander in an unscanned root keeps
  licensing); it's only "sound" by redefining that root as out of scope.
- **A (full registry threaded through every consumer): sound but L-cost**
  new infra; A-min gets the same soundness at far less surface.

## Two rulings you still owe under A-min (both claim-soundness; D-102 is silent)
1. **Registry authority boundary (R1):** what makes the ledger
   authoritative — its issuer identity, retention, anti-rollback head,
   and the rule that an OFF-ledger calibration artifact is invalid.
   (Without "ledger membership = part of calibration validity," an
   off-ledger artifact is still a hole.)
2. **The prior-observation set (R2) — a real correctness fix regardless
   of option:** the artifact must carry an authenticated
   `prior_observation_set` = EVERY content-distinct observation known
   when D-102 was accepted (valid + blind holdouts + authenticated
   systematic/invalid attempts), DISTINCT from the n=19 derivation
   corpus. "New" (trigger) then = current − prior_observation_set, NOT
   current − derivation_corpus — otherwise known window-B holdouts and
   later captures get mis-flagged as newly-discovered. The current
   artifact's `blind_exclusions` has only 2 directory IDs — insufficient.
   You need to ratify the issuance cutoff + the content-identity
   inventory of what was already known at D-102. (The investigation
   found a 32-valid / 6-invalid unique same-epoch inventory from stored
   manifests + content hashes; a raw-physics re-fit is
   implementation-time backfill, not needed for the ruling.)

## Cost / sequencing
A-min is Medium (one writer + a small ledger schema + the artifact's
baseline-head field + the F1/F2 fixes already ruled + splitting trigger-
observation from local T1 selection). It lands as the SINGLE combined
CAL-BRACKET fix round after you rule R1+R2, becoming D-109. My lean flips
from the earlier "B for the timeline" to **A-min**: it's sound, it's a
faithful D-102 implementation (no amendment), and the one-writer choke
point makes it far cheaper than the registry the first consult imagined.
B remains the fallback if you'd rather sign a bounded-scope amendment
than build the ledger.
