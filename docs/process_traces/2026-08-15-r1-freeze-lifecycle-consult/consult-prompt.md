DESIGN CONSULT — R1: freeze-evidence lifecycle (rule-2 pre-decision consult; explicit license to
disagree with the magistrate's framing; 1 round; your design judgment is wanted, not deference).

WRITE_SCOPE: []

READ-ONLY consult; no repo modifications; probe outputs to $TMPDIR only.

CONTEXT (read these primaries first):
- docs/process_traces/2026-08-15-readiness-council/council-verdict.md (the ruled program; R1 is Phase 0)
- docs/process_traces/2026-08-15-readiness-council/refuter-outputs/sol-refuter-A-execution.md and
  refuter-verdicts.md §A-contract (the two-lens adjudication of the expiry cluster)
- docs/decision_log.md entries D-131, D-134, D-137 (contract text)
- joulewise/arm_readiness.py (freeze/evidence/arm lifecycle; note freeze-0001 hardcoding and the
  min-expiry inheritance at ~3710) and joulewise/arm_readiness_evidence.py (24h horizon constant)

THE QUESTION: all 33 frozen generic PACK evidence receipts expired by monotonic age (window slip;
no reboot). Both refuter lenses agree: in-place re-authoring on the same pack ID is not
D-131-valid (changed freeze evidence requires a successor pack + custody root), and the 24h
horizon + min-expiry inheritance are IMPLEMENTATION POLICY, not contract text. Two candidate
designs:
  (A) DURABLE FREEZE-TIME EVIDENCE: stable desk-authored evidence (doctrine pins, registry
      bindings, plan-tree digests) becomes boot-session-bound but NOT wall/monotonic-horizon
      bound; only genuinely perishable T-0 evidence carries short horizons. Smaller operational
      surface; arms survive window slips; requires re-ruling what "evidence freshness" means
      per receipt class.
  (B) SUCCESSOR-PACK LIFECYCLE: keep current semantics; build a real successor-pack/reissue tool
      (freeze-000N, new custody root, supersession chain), a governed freeze-refresh lane in the
      runbook (≤24h before arm, same boot session), and accept a re-freeze + baseline-supersession
      cycle before EVERY window night.
  (C) any hybrid or third design you judge better — say so plainly.

DELIVER: (1) your recommended design with rationale grounded in the actual threat model (what does
evidence expiry actually protect against, per receipt class?); (2) the exact contract deltas it
needs (which decisions amend, which clauses); (3) the implementation shape (tools, receipt schema
changes, runbook lane); (4) failure modes of the rejected option(s); (5) what the re-freeze
Phase-2 execution looks like under your design, including baseline supersession interaction;
(6) open questions only Ed or the magistrate can rule.
