# COLD-GATE VERDICT — window B survivor-consumption refusal
(Cold Fable adjudicator, fresh context; delivered 2026-08-03 night after
probe-process death + harvest-from-disk resume. Verbatim.)

## Classification: (i) CORRECT MACHINERY ON REAL EVIDENCE STATE

The refusal `clock_anchor_unresolved, environment_admission_missing` at
`scripts/run_campaign.py:5197-5200` is the fail-closed consumption
machinery correctly refusing to discharge one surviving member whose
primary evidence genuinely cannot support authenticated consumption.
Not a dispatch defect. Not operator error.

## Faithful probe record (read-only, completed exit 0)

Reproduced the session's exact preparation path — load_campaign_policy
-> _whole_window_campaign_membership with the real membership binding
and salvage closure -> _whole_window_member evaluations ->
AuthenticatedConsumptionSession(salvage_dangler_exclusion_v1)._prepare
with the real policy binding:

    policy sha256 = b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd (matches closure)
    membership: n_sources = 70, selection conditions = [] (membership resolves CLEAN — D-100 repair works)
    included=70 waived=0 excluded=0
    session.ready = False
    refusal_reasons = ['clock_anchor_unresolved', 'environment_admission_missing'] (exact match)

The magistrate's crude probe failed to reproduce because it used
policy=None and a naive bundle set; with the governed inputs,
reproduction is exact.

## Per-bundle evidence — sole cause is mtadd-p2048o0128-r06

1. Corpus text scan (70 bundles): exactly one bundle's stored
   summary_metrics.json contains either reason string — r06.
2. Per-bundle classification probe (_classify_precheck_refusals +
   _current_strict_summary over all 70): all 70 current-strict (reducer
   0.5.2 in CURRENT_MINT_REDUCER_VERSIONS, whole_window.py:71); exactly
   one bundle yields global refusals — r06 with exactly
   ['clock_anchor_unresolved','environment_admission_missing']; the
   other 69 carry only local-addressable refusals, which by design
   never refuse a session (whole_window.py:594-601).
3. Control-flow proof that no live-authentication failure occurred:
   _prepare fails at whole_window.py:555-557 with stage-1 (bracket +
   calibration-authentication) reasons BEFORE precheck classification.
   environment_admission_missing is only producible at stage 2. Its
   presence proves stage 1 passed clean over all 70 bundles — nulls
   included. Both reasons are stage-2 classifications of r06's stored
   window_evidence_precheck, promoted global because neither is in
   _METRIC_LOCAL_PRECHECK_REASONS (whole_window.py:143-158; deliberate
   closed allowlist — these are bundle-level, not per-metric, defects).
4. The evidence is real and physical: r06 metadata ->
   uncertainty_evidence.clock_anchor = {reason: clock_anchor_unresolved,
   detail: native_intersection_empty, method:
   powermetrics_native_second_censored_intersection_v1, status: unknown}
   — a genuine anchor-resolution failure at collection, recorded as the
   fail-closed barrier (reduce.py:1190/1734: never a silent fallback).
   gross_request precheck: eligible false, clock_anchor_bound_s null,
   reasons [clock_anchor_unresolved, clock_bound_unrecorded,
   environment_admission_missing]. Sibling r05 is clean. The
   environment_admission_missing entry stems from
   current_environment_refusals (environment_admission.py:116-204), a
   causal temporal-binding validator whose interval containments depend
   on the wall<->monotonic mapping the failed anchor supplies — r06's
   admission ledger itself is well-formed (2 attempts, final admitted,
   cpu_admission present), so this is binding failure, most plausibly
   downstream of the same anchor pathology.
5. Latency: the original 2026-08-01 FAILED row (line 120, minted
   semantics) carries only the five window-level cascade conditions;
   r06's per-bundle defect was masked by the membership cascade and
   first became reachable when the repaired membership resolved clean
   (probe: selection conditions = []). The deviation-escape fired
   exactly as designed — the STOP was itself correct machinery.

## Refuter corroboration and dissent

(a) exact reproduction — corroborated independently (identical output).
(b) falsify-by-removal 69/69 — not rerun; per-bundle attribution is
logically equivalent and convergent by different method.
(c) dispatch-defect refutation — corroborated (D-100 addendum
decision_log.md:6267-6270 defines the COMPOUND semantic; hypothesis
(ii)'s mechanism also factually false: failing bundle is a measured
mtadd bundle, not a null; stage-1-clean proves no anchor requirement
misapplied to any null).
(d) NEG-8 bound expired — corroborated from the artifact (derived_at_s
2026-08-01 ~10:42 UTC + max_age_s 86400 -> expired 2026-08-02). MILD
DISSENT on framing: neg8_drift_bound_stale is INSIDE the audited
cascade set; alone it would have produced another governed FAILED row,
not a cold-gate stop; the bound is re-mintable
(run_derive_neg8_drift_bound). Staging-staleness for the next attempt,
not part of this refusal's cause.

## Prescribed next step

- No repair row — no code defect. No corrected command.
- Record an EVIDENCE GAP against mtadd-p2048o0128-r06 (clock-anchor
  resolution failure at collection, latent since 2026-08-01, masked by
  the membership cascade; pin the current_environment_refusals
  sub-branch in a follow-up; note the spelling collision).
- The license question returns to the magistrate -> Ed as a NEW ruling.
  No existing channel removes r06 (exclusion cap ONE per window, spent
  on r08; r06 not a dangler; waivers forbidden under salvage).
  Candidate channels a ruling could weigh — this gate grants none:
  per-member waiver row (machinery-native, run_campaign.py:5170-5171/
  5186), membership re-binding, or abandoning window B re-evaluation
  for window C re-collection. Decision-relevant asymmetry: r06 sits in
  the already claim-barred p2048o0128 cell (7 < frozen min_n 8 —
  excluding r06 resurrects nothing there), yet whole-window consumption
  is all-or-nothing, so one member of a dead cell holds the license's
  real stake (six other additivity cells + both null rungs) hostage.

## What D-100's license means under this ruling

Conditions 1-7 genuinely satisfied; condition 8's governed run refused
correctly; deviation-escape functioned. The license is neither voided
nor discharged — EXHAUSTED AS CURRENTLY DRAWN: unreachable while r06 is
a member. Original FAILED verdict continues to govern default
consumption by construction. No stop signal reinterpreted.

## Dissent-worthy uncertainty

1. Spelling collision: environment_admission_missing has two distinct
   producers; D-100's cascade classification was correct for the
   producer it examined; future classifications must treat spellings as
   non-unique to producer.
2. Unpinned sub-branch for r06's environment refusal (temporal-binding
   downstream of the anchor most plausible; independent admission-
   evidence defect not excluded). Does not affect classification.
3. The probe process appeared dead ~2h before completing; output
   authentic (exit 0, on-disk) but the reproduction was slow-running.
