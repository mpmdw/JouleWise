FIX ROUND 2 — WO-LAUNCH-BINDING F3 + NDF1, branch impl/wo-launch-binding (head 72cd698). The escalation consult ruled and the lead ADOPTED both recommendations (consult report at .consult-f3-report.md in your working directory root — read it first). Implement EXACTLY the adopted design; if any part proves unsound in implementation, NEEDS_RULING — do not improvise a third formulation.

WRITE_SCOPE: ["joulewise/arm_readiness.py", "scripts/launch_window.py", "scripts/run_campaign.py", "tests/test_arm_readiness.py", "tests/test_launch_window.py", "tests/test_run_campaign.py", "docs/decision_log.md"]

F3 — ADOPT_PRIVATE_REQUIRED_CONTEXT_API:
1. DELETE the public-named consumption wrapper entirely and BOTH caller-frame identity guards (arm_readiness.py:4751, :4884) — forgeable checks must not exist even as decoration; nothing may represent caller identity as security.
2. Retain ONE module-private consumer (underscore-named, absent from __all__) whose signature REQUIRES the complete launch inputs — the authenticated launch manifest, arm receipt, window.env/chain digests, and roots — and performs CALLEE-SIDE REAUTHENTICATION of all of them before consuming; accidental invocation without the assembled context is structurally impossible (missing/invalid inputs refuse with the existing registered codes).
3. The atomic no-clobber consumption primary remains the ONLY real enforcement (single-use linearization); state this in the code comment at the consumer and in the decision-log entry.
4. Append the decision-log entry recording the adopted design + the HONEST REGISTERED LIMITATION: deliberate in-process invocation with forged-but-complete inputs is the hostile same-UID/same-interpreter family, out of this mechanism's scope, carried on Ed's batched risk-appetite list (same family as the recorder race + T-0 provenance).
5. Regressions: (a) the old public name is GONE (AttributeError/import failure asserted); (b) the private consumer with complete valid context consumes exactly once and the second attempt dies on the no-clobber primary; (c) missing/mismatched context inputs refuse with registered codes BEFORE any consumption side effect; (d) launch_window.py end-to-end still green.

NDF1 — DEFER_WITH_PHASE_2_RELEASE_GATE:
6. At the AXI dispatch path, when the campaign is marker-bearing (launch_lineage_required), refuse fail-closed with a registered code (reuse launch_binding_mismatch or register a narrow launch_lineage_axi_unsupported under D-078 — pick the honest one and register it in the same decision-log entry) BEFORE any child dispatch; non-marker AXI campaigns unaffected. No ancestor search, no locator replication.
7. The decision-log entry records the Phase-2 mechanism the consult named (exact AXI layout projection + authenticated successor-schema derivation descriptor) as the release gate.
8. Regression: a marker-bearing AXI fixture refuses at dispatch with the registered code; a non-marker AXI fixture proceeds exactly as before.

VERIFY: nine focused suites unpiped, tails pasted. Leave uncommitted; list changed files.
