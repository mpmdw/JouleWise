# 2026-07-22 → 24 — First live collection under the repaired instrument: two nights, four bracketed windows, three collection-path repairs, and the NEG-8 gate adjudication

Ed-directed continuation of the D-078 Phase-0 sign-off (PR #79 merged
2026-07-22): merge, then collect. This report records the first
production collection attempts under the repaired instrument, the
live-found defects they exposed, and the state of the claim path.

## Arc summary

The instrument's measurement physics performed superbly; its
collection *machinery* surfaced four defect groups that only live
execution could expose. Each was diagnosed forensically (Sol xhigh,
evidence-locked), fixed under lead rulings, adversarially reviewed,
and merged same-night:

- **PR #80 — collection-path repair:** retry-attempt idle provenance
  (canonical-name promotion of the final admitted attempt) and the
  admission→window thermal-coverage gap (sole-sampler design: one
  continuous power+thermal sampler; idle baselines as byte-verbatim
  slices). An interim two-process overlap design was killed by delta
  re-audit for biasing the idle estimand before the sole-sampler
  ruling landed.
- **PR #81 — idle-slice cursor:** forensics on 11 burned members
  boundary-locked admission contamination to the slicer itself: real
  powermetrics cadence is ~120 ms vs the requested 100 ms, so a fixed
  30.1 s sleep woke early and full-stream plist parsing ran inside the
  measured idle support (first >2 W sample at attempt+30.1 s in every
  member). Replaced with incremental byte-cursor NUL-boundary tracking;
  no reads/parses during slice support.
- **PR #82 — whole-window verdict repair (D-078 clause 9):**
  diagnostic-cascade decoupling; explicit hash-sealed occurrence
  supersession (default refusal preserved); waiver consumption in the
  verdict path; basis-scoped verdicts (latest-wins stays rejected).
- **Operational discoveries:** concurrent agent sessions and the
  orchestrator's own wake-up turns measurably contaminate admission
  (the guard refused correctly every time); post-subcampaign churn
  needs settle periods; stale campaign locks and slot-occupying failed
  bundles need explicit hygiene (now: lock pid-checks, quarantine +
  supersession artifacts).

## Collected corpora (all strict-collected, currently non-claim-bearing as windows)

| Window | Span (UTC) | Members | Complete cells | Verdict |
|---|---|---|---|---|
| a5 | 07-23 04:45→13:57 | 108 | NEG-8 start, request-abs 20/20, phase-abs 30/30, decode-ABBA 40/40 | failed — real drift (stale end ref, −0.778 J workload-level) + one true clock-anchor refusal |
| a6 | 07-24 01:33→02:46 | 19 | NEG-8 pair | failed — corner-statistic gate (point drift +0.115 J) + aborted-member fragments |
| a7 | 07-24 02:57→05:33 | 42 | NEG-8 start, phase-abs 30/30 | failed — end reference admission refusal (correct) |
| a8 | 07-24 05:34→08:40 | 60 | NEG-8 pair, suite-abs 10/10, long-request 20/20 | failed — corner-statistic gate (point drift **+0.0067 J over 2.96 h**) |

Three valid protocol-v3 calibrations bracketed a5 (24.8–26.0 ms);
each of a6/a7/a8 minted its own pre/post pair. Quarantines preserved
(`runs_window_a5_quarantine/`); nothing deleted.

## The decisive adjudication (Sol xhigh, 2026-07-24)

The NEG-8 drift gate as implemented compares the two reference cells'
admissible-set envelopes at **opposite corners** (stacked ~0.9–1.5 J)
against an underived 0.05 J bound — structurally unpassable even for a
physically perfect window. a8's actual point repeatability, 0.0067 J
on ~38.5 J references (0.017 %), is the best evidence yet that the
repaired instrument is sound. Lead ruling (Ed ratification pending,
implementation in flight):

1. The gate's estimand is **point drift**; the corner statistic
   becomes a reported diagnostic (it already lives, correctly, in the
   floor uncertainty composition — gating on it double-counts).
2. The bound is **derived** from a settled-reference corpus (n≥10,
   predeclared estimator, hash-sealed bound artifact); until derived,
   the gate refuses `neg8_drift_bound_underived`.
3. a5 stays dead (real drift); a7 recollects its end reference; a6/a8
   re-verdict under the derived bound with explicit waivers for their
   aborted-member fragments.

## Path to the first claim-bearing floors

1. NEG-8 estimand amendment lands (in flight).
2. Next quiet window: settled-reference corpus (n≥10 NEG-8 members,
   ~1–2 h) → derive the bound → re-verdict a8 (and a6).
3. Remaining cells: prefill-ABBA, request-ABBA, request-core (a7 lost
   its copy), suite-ABBA remainder, short-prefill — one to two compact
   bracketed windows.
4. Governed extraction (per L1 same-custody rule) → P2-037 claim
   adjudication → the first promoted floor table.

A diagnostic (non-claim) extraction over the four corpora is running;
its table previews the numbers and cross-night repeatability.
