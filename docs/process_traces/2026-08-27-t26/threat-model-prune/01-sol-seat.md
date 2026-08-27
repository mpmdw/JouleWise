# Sol seat — THREAT-MODEL-PRUNE-01 (gpt-5.6-sol xhigh, read-only; relayed by the codex director). Verbatim.

Sol's answer (thread `01a044b2-b9f0-7000-af09-4ab98f31f0f4`, read-only sandbox, xhigh, no edits, envelope present and final), verbatim:

---

## Positions

I treated repeated reason branches as one enforcing mechanism. Every refusal falls into these families:

- **A — keep fail-closed:** bundle/schema/runtime validity; immutable raw evidence; calibration and clock-anchor authentication; powermetrics capture physics; environment, thermal, idle, cooldown, teardown and duration admission; reduction/attribution bounds; whole-window membership and supersession; floor construction/transport; claim-evidence and paper replay. Examples: calibration has no fallback ([reduce.py](/Users/edr/code/JouleWise/joulewise/reduce.py:1171)); environment gaps refuse ([environment_admission.py](/Users/edr/code/JouleWise/joulewise/environment_admission.py:404)); floor transport forbids extrapolation ([detection_floor.py](/Users/edr/code/JouleWise/joulewise/detection_floor.py:4295)). The D117 workflow's archive, 190-member custody, and proof-leg failures are also A ([d117-production-proof.yml](/Users/edr/code/JouleWise/.github/workflows/d117-production-proof.yml:130)).

- **B — keep fail-closed:** generated campaign/config/order/prompt plans; frozen plan/stack identities; fixed `n`, `m`, alpha, hypotheses and floor dependencies; prospective/finalized analysis manifests; freeze/arm/mint admission; changed-set and step-6 confirmation through collection. The prospective validator covers unresolved slots, multiplicity and floor dependencies ([analysis_manifest_v3.py](/Users/edr/code/JouleWise/joulewise/analysis_manifest_v3.py:1885)) and is now called before collection ([run_campaign.py](/Users/edr/code/JouleWise/scripts/run_campaign.py:1401)); mint has a distinct preregistration gate ([mint_floor_artifact_generalized.py](/Users/edr/code/JouleWise/scripts/mint_floor_artifact_generalized.py:2656)).

- **D — ambiguous/non-threat-model:** publication privacy, destructive `reauthor_clean` safety, bundle crash-atomicity, bridge leases/scope, ordinary path containment, compiler/schema correctness, CI sharding and process cleanup. These protect privacy, data loss, concurrency or software correctness—not A/B and not merely hostile operator tamper. Do not weaken them under D-161 without separate rulings.

## Disagreements

The strongest "C is B in disguise" argument is the historical-semantics pinset: its head, historical-pack, plan and post-authoring-delta fields ([arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:3205)) can prove that analysis bytes preceded evidence authoring ([arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:2974)). Keep that temporal proof as B; prune only the reviewed-file byte pin, no-update rule, clone policy and redundant tripwires.

## Open questions

None. D-161 supplies sufficient authority; D-class operational-safety items remain outside this prune.

## Recommendation

Ranked C prune list (cost saved/risk to A/B):

1. **RETIRE** reducer SHA plus 13-file direct-I/O AST gate ([test_authentication_io.py](/Users/edr/code/JouleWise/tests/test_authentication_io.py:345)); high edit coupling/low risk.
2. **RETIRE** exact public-module namespace census ([test_arm_readiness_evidence_author.py](/Users/edr/code/JouleWise/tests/test_arm_readiness_evidence_author.py:456)).
3. **RETIRE** v1 validator module byte pin ([test_analysis_manifest_v3.py](/Users/edr/code/JouleWise/tests/test_analysis_manifest_v3.py:387)).
4. **RETIRE** four custody-tool sidecar tripwires ([test_family_marker.py](/Users/edr/code/JouleWise/tests/test_family_marker.py:768)).
5. **WARN-RECORD** executing-tool hashes and forbidden-flag source scan ([test_family_marker.py](/Users/edr/code/JouleWise/tests/test_family_marker.py:655)).
6. **REFRESH LANE** for histsem rows; retire "no update," retain reviewed diff ([test_receipt_histsem.py](/Users/edr/code/JouleWise/tests/test_receipt_histsem.py:195)).
7. **WARN-RECORD** shallow/full-history and current-`origin/main` policy ([arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:3086)).
8. **RETIRE/DO NOT IMPLEMENT** S3 D4 promisor no-fetch refusal: current `cat-file blob` may lazy-fetch ([arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:3157)); the proposed cost is pure clone policing.
9. **WARN-RECORD** post-freeze four-way-clean/current-head checks; **KEEP** them at freeze/mint as B ([arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:11422)).
10. **WARN-RECORD** repeat-read ABA/same-UID race; keep strict parsing and contained regular-file checks as A ([authentication_io.py](/Users/edr/code/JouleWise/joulewise/authentication_io.py:365)).
11. **REGENERATE-AND-RECORD** generated state instead of blocking CI ([gen_state.py](/Users/edr/code/JouleWise/scripts/gen_state.py:800)).
12. **RETIRE** exact CI timing/evidence-range and exact test-count pins ([ci.yml](/Users/edr/code/JouleWise/.github/workflows/ci.yml:123)).
13. **RETIRE** exact blocked-skip census; downgrade global reason-emitter census, but keep W11's DATA/CONTRACT partition ([test_s0_blocked_enumeration.py](/Users/edr/code/JouleWise/tests/test_s0_blocked_enumeration.py:47)).
14. **RETIRE** byte-identical bridge prose and duplicate-wire scanners ([test_bridge.py](/Users/edr/code/JouleWise/tests/test_bridge.py:1583)).
15. **RETIRE** docs/site wording and model-name freshness blockers ([test_docs_freshness.py](/Users/edr/code/JouleWise/tests/test_docs_freshness.py:175)).

Item 6 specifically caused three edits and two mint blocks ([decision_log.md](/Users/edr/code/JouleWise/docs/decision_log.md:188)); process proliferation yielded 122 unenforced clauses ([CHECKPOINT-2026-08-27.md](/Users/edr/code/JouleWise/docs/process_traces/2026-08-27-t26/CHECKPOINT-2026-08-27.md:28)).

**Do not prune 4–10, the step-6 successor pin/count checks, or W11's reason partition before `_v4`**: estate 11 and the frozen runbook consume them. Land only the reviewed refresh lane now; weaken those mechanisms after transaction closure.

Paper §7: **"The repository is tamper-evident for the operator's own benefit, not tamper-proof against anyone."**

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Completed read-only threat-model classification and ranked 15-item prune recommendation; core physics/evidence and preregistration gates remain fail-closed.","pathspec":[],"verification":["Inspected current HEAD source, tests, workflows, D-161, transaction state, and bridge protocol with rg/nl/git; worktree remained clean","No tests run: read-only code-judgment consult"],"flags":["no_edits","read_only","no_claude_hop"]}
