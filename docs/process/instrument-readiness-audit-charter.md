# INSTRUMENT-READINESS AUDIT CHARTER — v2, RATIFIED 2026-08-14

Ratification: magistrate adoption of the design consult's thirteen
amendments IN FULL (consult custodied at
docs/process_traces/2026-08-14-readiness-charter-consult/consult.md; the
draft it rejected is retained as *-DRAFT.md beside this file). Authority:
Ed's window-gating directive (decision log, 2026-08-13 late). Windows are
not scarce; the audit takes what it takes.

## The question

"If a funded quiet window ran under the frozen packs and current runbook,
would every REQUIRED OUTPUT either trace through a claim consumer or fail
closed against consumption — and if not, what exactly is missing?"
(Amendment 1: the enumerated required-artifact universe replaces 'every
byte'.)

## Audit baseline (amendment 2)

An immutable AUDIT-BASELINE MANIFEST is committed before any lens
launches, binding: HEAD + origin/main, all three pack digests, the row
registry sha, the acceptance artifact sha, the runbook + chain-template
shas, the state-kernel sha, and the governing decision IDs. Every lens
cites it; any drift from it invalidates affected lens results
(amendment 12's final-head invalidation).

## The fleet (amendments 3-9; ten launch-gating seats + one non-gating)

1. AUTHORITY PLANE (xhigh): state kernel, gating machinery, decision-ID
   bindings, projection/receipt authority chains — the control plane
   itself audited as a component.
2. CALIBRATION ACQUISITION (xhigh): fiducial writer, authenticated
   acceptance, bracket reservation, ledger, recovery, writer lifecycle.
3. CAPTURE + TELEMETRY (xhigh): sampler lifecycle, child supervision,
   cadence, parser, channel census, the CPU+GPU+ANE boundary.
4. QUANTITATIVE CLAIM PIPELINE (xhigh): reducer, verdicts, floors,
   common-mode estimator, mint, analysis consumption, both-gates logic.
5. PACK/READINESS/CUSTODY (xhigh): generators, frozen bytes, evidence
   production, U11, freeze/arm/consume receipts, external custody.
6-7. PRODUCER-CONSUMER SEAMS (2 × high, DISTINCT contract/execution
   readers, independent from audit start): the complete obligation graph
   — every producer's outputs mapped to consumers, zero-gap census
   (amendments 5-6; the five-layer producer-gap chain is the type
   specimen).
8. OPERATOR + RECOVERY HUMAN FACTORS (xhigh): the tired-operator
   rehearsal and error-injection matrix — what a fatigued operator can
   do wrong that no receipt catches (amendment 7).
9. ENVIRONMENTAL CONTROLS CENSUS (high): the hazard register and a
   completeness disposition — display, keyboard, screensaver, network,
   thermal, clock, charger, background daemons (amendment 8).
10. SACRIFICIAL FULL LIFECYCLE (xhigh): a disposable end-to-end
   post-collection rehearsal — synthetic collected window driven through
   reduce → verdict → mint → claim consumption, proving the AFTER-window
   path BEFORE a window is spent (amendment 9).
11. (NON-GATING) RETAINED CHARACTERIZATION BASIS (high): a9/a10 as the
   publication-basis audit, outside the launch-GO aggregation
   (amendment 13).

## Anti-ritual discipline (F8, binding on every lens)

Every lens report must carry: its enumerated evidence universe; a
coverage numerator/denominator; executed POSITIVE and NEGATIVE probes
(minimum executed falsifiers — a READY-falsification attempt is
mandatory); unexecuted obligations listed; concrete failure scenarios
per finding. A zero-finding report without the full packet is
UNVERIFIED, not READY. C-028 refuters verify findings; the sitting
additionally adjudicates COVERAGE and the falsely-clean risk on primary
evidence.

## Ed rows (amendment 10)

Hardware/privilege rows split into: ED-QUALIFICATION (stable
capabilities — sudo powermetrics behavior, sampler child supervision
live, the JW-MET-3 rail probe — performed BEFORE the sitting, in any tap
block; stable evidence cannot be deferred) and T0 (genuinely perishable
same-night observations — live census at arm, clock stabilization).
Only T0 rows may remain open at the sitting.

## Verdict form (amendments 11-12)

READY-WITH-CONDITIONS is DELETED. Per component: READY / NOT-READY(+work
orders) / UNVERIFIED. Council READY requires: no NOT-READY, no
UNVERIFIED, all ED-QUALIFICATION rows closed with evidence. T-0 GO is a
SEPARATE, later closure bound to the arm-night's perishable rows — the
council's READY never implies it. EVERY council READY verdict requires
the rule-11 cold pairing (fresh Fable adjudicator + Opus contract
refuter) over a sealed, mechanically-assembled packet; sealed-packet
custody under docs/process_traces/<date>-readiness-council/ with
mandatory contents enumerated in the packet index; final-head
invalidation — any repo change after the baseline manifest voids
affected lens results.

## Sequencing

The fleet launches after the arm-author lands and the chain-fix batch
merges (the baseline should include them). Fleet shape per the consult:
ten seats as listed, refuters on demand, no ultra sessions.
