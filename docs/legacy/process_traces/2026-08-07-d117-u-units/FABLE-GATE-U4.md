# Apex gate ruling — U4 (the one that was missing)

The Opus final-head review noted correctly that U1 and U3 each have a
FABLE-GATE record and U4 has none, and that no ruling ever accepted the
PARTIAL items in U4's delta. This file supplies both.

## Lead error, recorded plainly

U4's delta verdict was **not CLEAN**. It reported the two headline defect
classes dead (mutation-verified) and one residual L5 coverage gap — and it
ALSO reported **FIX-C, FIX-E and FIX-F as PARTIAL**. The magistrate acted
on the L5 item only, then opened and merged the PR. No ruling was recorded
on the three PARTIALs; "FIX-D closed" entered the record when the honest
status was "closed as implemented, not as specified."

This is the second instance today of the magistrate accepting a delta's
headline while its qualifiers went unread (the first: U3's delta-2 CLEAN,
which the Opus counter-review overturned). Both are recorded, and D-118
item 5 now requires the same-signature statement to be read as a whole,
not just its verdict word.

## Ruling on the outstanding items

**F1 — FIX-D reopened (should-fix).** The delta asked for a binding
NAMING foreign-root endpoints; the implemented fix supplies a correct
binding with a foreign CALLER-SIDE runs_root. Different vectors, and the
consequence is measured: enforcement site S3 (binding-vs-session
agreement, calibration_bracketing.py ~L660) has **zero coverage anywhere
in the calibration suite** — removing it alone leaves 110 tests green.
Close with a fourth arm using the file's existing `_rehash_binding`.

**F3 — staged tests must assert production behavior (should-fix).** The
three U2-gated tests are correctly gated (explicit skip reason, skipped=3
every run) but their bodies compare fixture to literal and touch no
production code. When U2 lands and the decorators come off, they become
three instantly-green tests asserting nothing. Rewrite the bodies now
against the interfaces U2 will provide, so removing a decorator is a real
activation.

**FIX-C / FIX-E / FIX-F PARTIAL — ACCEPTED AS PARTIAL, with the residue
named** rather than silently promoted to closed. They are test-coverage
depth items on a test-only unit, none affects production code, and the
unit's two headline classes are mutation-verified dead. The residue is
recorded here and queued; it does not block a night.

**F4 — declared, not fixed (pre-existing).** Every discovery test in the
repo stubs `_candidate_from_observation`, so its cross-authentication
block (SHA vs receipt, content_id re-derivation, bound/capture/T1/epoch
agreement) has no coverage anywhere. Pre-existing and fixture-forced, but
previously undeclared. Now declared; closing it is its own unit.

**F2 — noted, no action.** The L5 fix bought no NET repo-level coverage
(an existing bracketing test already killed the S1+S2 pair), but U4 should
carry its own integration-level L5 assertion. The fix stands; only its
framing overstated.

**F6/F7/F8 — queue as nits** (bare 3/6 literals where named constants
exist — the exact drift class that caused FIX-A; dead scenario values;
an undriven committed-pin branch).

## Verification credit

The reviewer verified the L5 claim by running a full mutation matrix over
the three enforcement sites (S1/S2/S3 and all pairs), reproducing the
commit's own failure signature verbatim, confirming the pre-fix tree
survived the same mutation, and reverting. That is the standard for a
"mutation-verified" claim in this project.
