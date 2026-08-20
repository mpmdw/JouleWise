# D-144 pre-merge seat pass — magistrate ruling (merge gate 3 of 4)

Date 2026-08-20. Packet:
docs/process_traces/2026-08-19-r1-r2-codesign/16-d144-seatpass-packet.md.
Artifact: the implemented D-146+D-147 S0–S5 transaction, diff
7d4454e..afb7d57 (code+config; docs covered by the satisfied
fresh-pass gate). Seats: terra (xhigh, execution-weighted) + Opus 5
(contract lens), independent; one bounded debate response (terra over
the Opus findings; the terra report was clean so carried no debate
surface). Custody: terra-seat-report.md, opus-seat-report.md,
terra-d144-debate-response.md (this directory).

## VERDICT: GO — merge gate 3 is GREEN

Both seats independently recommend GO with ZERO blockers. The
strongest ground (Opus, executed): the r5→r6 drift class this pass
was convened to hunt — a fix round silently falsifying a design-time
verification — DOES NOT RECUR at the merge head, proven by
recomputation (all four D-079 estimator pins hash to r6's
estimator_code_sha256; empty git log over those files since 3038eeb;
0 evidence-pin mismatches). Frozen surfaces recompute digit-for-digit
against the T10 table (both seats, independently); the stored-v2
claim-barrier walk refuses in all three lanes (terra); the S3
per-lane mutation-kill passes 2/2/2 (Opus); the _v2→_v3 generator
delta is exactly the three ruled edit sites (Opus, full diff).
The known canonical residue's root was independently confirmed by
Opus exactly as classified (and is FIXED at 60ddb03, gauntlet record
in 00-fix-gauntlet-synthesis.md).

## Findings disposition (post-debate severities)

SHOULD-FIX — registered as queue row D144-SEATPASS-FOLLOWUPS, NOT
riding the wave:
- SF-1 (S5 reporting gap): the mixed-era superseded-observation
  rejection reaches no production surface (diagnostics out-param has
  no production caller; reason gated behind `if not candidates:`).
  Terra EXECUTED the mixed fixture (status=passed, reasons=()) —
  defect confirmed — AND executed the counter to Opus's ride-along
  request: dropping the guard would put the era reason into
  whole-window's global refusal set and refuse VALID v3 claims when
  retained history exists; passing the unused param alone does
  nothing. The correct shape is a non-gating persisted report
  channel per R1 S5 — designed work, not a wave rider. Claim
  soundness is unaffected today (stored-v2 barriers fail closed).
- SF-3: no registry-sync test binding schema_v2.json's
  generation→screen conditional to the Python registries
  (defence-in-depth loss only; Python gate primary).
- SF-5: the no-copied-scalar guard is a 3-file allowlist vs R2
  S1(i)'s mint-lane-wide policy (clean today; fragile).

NITS (recorded; no action this wave): SF-2 (twin era predicates —
downgraded: constants coincide and invalid bindings cannot enter a
valid observation; future-policy test optional), SF-4 (controller
event-order move — downgraded: capture remains post-cleanup; only
buffered event ordering changed), N-1 dead import, N-2 mutable map,
N-3 count comment (ALREADY CURED at d33f34f), N-4 synthetic-oracle
narrowing, N-6 stale bare --check replay instruction (inherited).
N-5 is reclassified VERIFICATION GAP (unreproduced ad-hoc
order-dependence; suspect cross-module cache; retained as a note,
not a defect).

## Coverage instrumentation (council log input)

Terra's clean first pass covered frozen-surface recomputation + the
claim-barrier walk; it did not run Opus's caller-census/reachability,
schema-sync, lifecycle-order, guard-boundary, kernel-test-seam,
cache-order, or emitted-command-replay checks — stated plainly in its
debate response. Layer catches this pass: Opus contract lens 11
findings (1 confirmed should-fix with claim-adjacent surface, 2
should-fix, rest nits/gaps); terra execution lens: the SF-1
fix-shape refutation (prevented a false-refusal defect riding the
merge wave) + severity corrections ×3. Both lenses earned their seats;
the debate round demonstrably changed the outcome (SF-1 ride-along
DENIED on executed evidence).

## Gate state after this ruling

Gate 1: fix landed (60ddb03) + kernel/custody commit (d33f34f);
canonical at d33f34f in flight at ruling time — gate 1 closes on its
FULL GREEN. Gate 2: satisfied (fresh-pass clean through b92b43d).
Gate 3: GREEN (this ruling). Gate 4: the merge wave proceeds under
D-148.2 when gate 1 reports, with the custody/bookkeeping commits
focused-verified per the T16 precedent.
