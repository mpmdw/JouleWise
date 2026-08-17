# Phase-2 atomic re-freeze — execution runsheet (staged 2026-08-17)

The ordered execution document for the transaction. Authority: the plan
consult (docs/process_traces/2026-08-16-phase2-plan-consult/) as adopted;
D-138/D-139; the R1 ruling. Every input is gauntleted (delta-ACCEPT) at the
pinned heads below. The executor follows this order; any deviation, failed
verification, or science-facing delta STOPS the transaction (F3
stop-condition → cold review).

## Pinned inputs (all delta-ACCEPTED)

| Lane | Branch | Head |
|---|---|---|
| Estimator payload (budget + flake + calib stage-2) | impl/wo-detect-pulses-budget | e22e658 |
| R1 freeze-evidence lifecycle | impl/r1-freeze-lifecycle | (delta-2 head, origin) |
| D-079 reissue tooling | impl/d079-reissue-prep | e83a61f |
| Successor generators | impl/successor-generator-repairs | 6ddeb7d |
| Docs/paper currency | PR #158 | (merge on green) |

## Order of execution

1. **Merge the lanes to main**, in order: #158 docs → R1 → generators →
   D-079 tooling → the estimator payload branch (this is the D-138 moment:
   the canonical suite's acceptance-staleness fan-out APPEARS here and is
   cured at step 3 — the two steps land in one push window, never separately
   CI-gated). Integration tree first if any merge conflicts.
2. **Generate the `_v2` successor family** (generators, successor mode,
   preserve OFF for the new IDs only): d117_floor_qwen25_1p5b_v2,
   d117_floor_qwen25_7b_v2, d117_contrast_qwen25_1p5b_vs_7b_v2 — with
   launch_lineage_required, plan.path reconciliation, and self-consistent
   embedded identity (all delta-proven).
3. **Reissue D-079**: run scripts/reissue_calibration_acceptance.py against
   the merged head; require 19/19 + PROCEED (any STOP → halt, cold review);
   strip the candidate marker via the issuance step; update every dependent
   pin + test in the same commit (the tooling's member-delta report is the
   license record).
4. **Install the D-139-approved reserved values** via the R1 registry
   (uniform `_v2` IDs; freeze-0002 chain-monotonic with predecessor
   bindings; existing operational horizons). NO code edits (delta-proven
   installable).
5. **Freeze the family**: fresh receipts (freeze-0002) + R1 content-bound
   evidence, one atomic family transaction, NO grandfathering.
6. **ED CONFIRMATION (the irreversible point):** present Ed the exact-byte
   summary (pack tree hashes, receipt hashes, the family marker bytes);
   publish the marker ONLY on his explicit yes. Until then everything is
   revertible.
7. **Post-publication:** canonical suite green at the published head
   (staleness fan-out must be GONE); Phase-3 baseline-manifest SUPERSESSION
   (+pack_digest_algorithm + chain-template note) as its own follow-up —
   NOT inside the publication step (plan F5).

## Then

Phase-3 focused re-audit (adversarial coverage re-enumeration) →
READY-candidate council (fresh cold pairing; requires Ed's qualification
rows from tonight's checklist) → D-139 shakedown runs → claim windows.
