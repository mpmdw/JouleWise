DESIGN RULING CONSULT — R2: FROZEN_PLAN identity (council-verdict Phase 0; 1 round; license to disagree).

WRITE_SCOPE: []

READ-ONLY; probes to $TMPDIR only.

CONTEXT: docs/process_traces/2026-08-15-readiness-council/council-verdict.md (R2);
refuter-outputs/sol-refuter-B-contract.md F6 + sol-refuter-B-execution.md F6 (the four env/chain
mismatches + the doubled plan-path defect: plan_tree.json stores a repo-relative plan path,
arm_readiness_evidence_t0.py:~1149 joins it onto pack_root -> nonexistent doubled path; test
fixture uses bare filename so the suite masks it); docs/phase_2/window_runbook.md §4 window.env
example + §6 chain template + E-8; joulewise/arm_readiness_evidence_t0.py parsing/binding contract.

QUESTION: rule the ONE identity of FROZEN_PLAN across all surfaces — is it (a) the pack's
committed calibration_plan.json (pack-root-relative), (b) the custody reservation-plan JSON, or
(c) something else — and the exact path-resolution rule (repo-relative vs pack-root-relative vs
resolved-literal) every consumer must share. DELIVER: the ruled identity + resolution rule; the
per-surface fix list (runbook §4/§6/E-8, author parser, plan_tree producer, test fixtures) with
which side changes (prose vs parser) per site; the real-pack regression test shape; failure modes
of the rejected readings.
