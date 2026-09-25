# Magistrate proposal: PR-0 escalation (Opus 5.5, activation 152c9255)

**Trigger.** The standing escalation trigger has fired. Round 0 (lens B-1) and round 1 (delta SF-A) failed with the same signature: the golden pins v1 decision branches by hand-enumerated inputs, and a fresh reviewer's new mutations keep surviving (round 0: 7 of 9 survived; after round 1: 7 of 10 new ones survive once the confound is removed). A third round of "add the rows the last reviewer found" is the anti-pattern. The next spend is this consult.

**Proposal S (the structural cure).** Replace coverage by enumeration with a mechanical acceptance, the harness-as-gate method.
- (i) A named list of v1 decision functions: `evaluate_claim`, `holm_adjust`, `_inside_equivalence`, the window floor selector at `analysis_engine/__init__.py` ≈:400-415, the decision branches of `validate_claim_verdicts`, `_claim_issuance_gate`, and the epoch-equivalence check.
- (ii) The golden test measures **100 % branch coverage** of those functions from the golden's inputs alone, using `coverage.py` branch mode in a subprocess, or `sys.settrace` if coverage is unavailable. It fails listing any uncovered arc.
- (iii) An **operand-collapse mutation sweep** script (every comparison operator flipped strict/non-strict, every `max`/`min` collapsed to each operand, every guard deleted) over the same functions must report **zero survivors**. It runs with the custody digest assertion neutralised, so the kill comes from the golden comparison.
- Acceptance is mechanical: 100 % branches and 0 survivors. No reviewer's list is authoritative.

**Proposal D-1.** Accept the delta auditor's fix:
- remove the injected `evidence_class` and the validator mock;
- record the real production outcome `{"raised": "KeyError", "key": "evidence_class"}`;
- make the invalid case invalid only by `claim_verdicts_id`;
- write "no unmocked admitting v1 path exists at PR-0" into `selection_rules`;
- register the production defect as lane V1-ISSUANCE-GATE-EVIDENCE-CLASS-01: `_claim_issuance_gate` reads `artifact["evidence_class"]` while the v1 wire carries `inputs.evidence_class`, and it crashes rather than refusing typed. The fix is outside PR-0 and needs its own gate. Until it lands, no v1 issuance can occur, which is fail-closed but by crash.

**Proposal D-2 (the WR-6 deadlock): option (a), split the golden.**
- `invariant` holds `claim_matrix`, `claim_verdicts`, validator outcomes and epoch replays. These must be byte-identical across the CG-4 PR, and the refresh isolation applies to them.
- `wr6_transition` holds, for every window-engine and issuance scenario, its PRE-WR-6 outcome plus the expected post-WR-6 outcome, derived by a stated rule. The rule: a contrast whose manifest id is neither in `v1_golden_manifest_ids` nor a front-registry `collection_manifest_id` gains `claim_rule_version_v1_closed` and `claim_ready_for_l2_l3 = false`, and nothing else changes.
- The CG-4 PR's test asserts that the post outcome equals the declared transition applied to the pre outcome. This fixes the WR-6 effect prospectively in PR-0, so the CG-4 PR never refreshes the golden.
- Options (b) (splitwise joins the v1 set) and (c) (reroute via a front-registry id) are rejected. (b) would admit a manifest WR-6 means to close. (c) tests a path the scenario does not represent.

**SF-A to SF-C of the delta:** subsumed by S.

**Tier.** This is the escalation consult for PR-0. After it, the fix is one round implementing S, D-1 and D-2, with a delta re-audit.
