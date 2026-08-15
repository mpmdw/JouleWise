DESIGN CONSULT — WO-MARGIN-RECORDER-AUTHZ contract (rule-2 pre-decision; council-verdict Phase 0 /
Opus W6 — this widens an authentication allowlist inside the authority plane, so the design gets
cold review before code; 1 round; license to disagree).

WRITE_SCOPE: []

READ-ONLY; probes to $TMPDIR only.

CONTEXT: docs/process_traces/2026-08-15-readiness-council/council-verdict.md; refuter-outputs/
sol-refuter-ECF-contract.md F2 + sol-refuter-ECF-execution.md F2 (executed: the recorder's
V2AuthenticationReadSession refuses the pack-pinned extraction spec on forbidden key
'estimator_registration' — REFUSE authoritative_input_invalid — halting §11 close-out; only the
mint authorizes governed vocabulary via allow_governed_extraction_spec; the committed census tests
model cell shapes WITHOUT the estimator vocabulary, so the suite is green over the broken seam);
joulewise/window_duration_margins.py (:394 spec read, :897 session); joulewise/authentication_io.py
(:179,:214); scripts/mint_floor_artifact_generalized.py:1758-1759,3683 (the mint's authorization
pattern); decision log D-133 (re-spec + close-out gate rulings).

QUESTION: design the recorder's governed-vocabulary authorization so it reads EXACTLY the one
plan-tree-pinned extraction-spec path with estimator_registration admitted, without widening the
authentication posture anywhere else. DELIVER: the authorization mechanism (mirror the mint's
allow_governed_extraction_spec vs a narrower path-scoped grant — argue which); the threat analysis
of the widening (what could now be smuggled through the recorder's read path and what refuses it);
the census-test correction (REAL frozen cell shapes so the seam can never silently break again —
name the exact frozen specs to model); refusal reason-codes; contract deltas if any.
