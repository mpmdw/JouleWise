# Sol seat — live-proof path (gpt-5.6-sol high, read-only; relayed). Verbatim.

Sol thread id: `01a047a4-79ad-75c0-a173-ed9a8205edec` (read-only, effort high, sandbox read-only, reverse Claude server disabled; no edits, no measurement). Sol's answer verbatim:

---

## Positions

**B is not sound and has no minimal flag-only cure.** A diagnostic policy makes `claim_licensing` false, while finalization requires a verdict that is both `passed` and claim-licensing ([run_campaign.py](/Users/edr/code/JouleWise/scripts/run_campaign.py:6310), [analysis_manifest_v3.py](/Users/edr/code/JouleWise/joulewise/analysis_manifest_v3.py:3299)). Even if that barrier were changed, one complete block against the real fixed-10 manifest first adds `insufficient_complete_blocks`, then `fixed_n_plan_incomplete` ([__init__.py](/Users/edr/code/JouleWise/joulewise/analysis_engine/__init__.py:694)). Both are CONTRACT because the DATA set contains neither ([reason_kinds.py](/Users/edr/code/JouleWise/joulewise/analysis_engine/reason_kinds.py:36), [claims.py](/Users/edr/code/JouleWise/joulewise/analysis_engine/claims.py:85)). The prospective finalizer additionally requires ten blocks, 40 members per contrast, both arms, and 80 total members ([analysis_manifest_v3.py](/Users/edr/code/JouleWise/joulewise/analysis_manifest_v3.py:2508), [analysis_manifest_v3.py](/Users/edr/code/JouleWise/joulewise/analysis_manifest_v3.py:2596)). `--diagnostic-occurrence` cannot cure those contracts.

A separate shakedown runs root would isolate occurrence and verdict accounting: membership, supersessions, and verdict lookup are all rooted in that root and its `campaign_log.jsonl` ([run_campaign.py](/Users/edr/code/JouleWise/scripts/run_campaign.py:5553), [whole_window.py](/Users/edr/code/JouleWise/joulewise/whole_window.py:5524)). But an extra `_v4` arm is not harmless transactionally: arms expire by boot/time and later arms can supersede them ([arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:8575)); campaign close requires executed arms to equal the published plan, with any extra/superseded arm requiring Ed's ruling ([real-transaction-runbook.md](/Users/edr/code/JouleWise/docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1261)). D-153 also keeps the changed-set window open through the last consuming arm and makes any mid-campaign non-config cure a new family ([decision_log.md](/Users/edr/code/JouleWise/docs/decision_log.md:180)).

A byte-for-byte custody copy is not relocatable: finalized manifests authenticate the bracket's absolute runs root beneath custody ([inputs.py](/Users/edr/code/JouleWise/joulewise/analysis_engine/inputs.py:739)). Finalization itself must write into `custody_root` ([analysis_manifest_v3.py](/Users/edr/code/JouleWise/joulewise/analysis_manifest_v3.py:3752)). After finalization, however, `analyze-claims` can read custody without modifying it and must write `claim_verdicts.json` outside the runs/evidence roots ([__init__.py](/Users/edr/code/JouleWise/joulewise/analysis_engine/__init__.py:97)).

**A, amended, is the cheapest sound path: approximately 7–10 Sol-days plus a complete estate-11 rerun and the 20–60-minute quarantined live run.** Minimal touched production files/functions:

- Three `generate_configs.py` files: `GenerationIdentity`, identity threading, `build_runs`/`build_science`, plan/stage/manifest/extraction builders, inventories, `generate`, `parse_args`, `main`. Gamma currently fixes 10 blocks, two arms, and 80 members ([generate_configs.py](/Users/edr/code/JouleWise/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:92)).
- `joulewise/arm_readiness.py`: schema validators, `_plan_profile`, `_pack_generation`, `generate_freeze_receipt`, `generate_arm_receipt`, verification/consumption replay, and `_gate_family_publication`; current registry and successor/marker gates are explicit ([arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:4097), [arm_readiness.py](/Users/edr/code/JouleWise/joulewise/arm_readiness.py:7335)).
- `scripts/generate_arm_readiness.py`, `capture_t0_step.py`, and `launch_window.py`: parser/context propagation and one-use authenticated diagnostic-license consumption.
- `joulewise/analysis_manifest_v3.py`, `analysis_engine/__init__.py`, and `reason_kinds.py`: authenticated diagnostic-only one-block finalization/evaluation that ends DATA-only without relaxing production semantics.
- `scripts/mint_floor_artifact_generalized.py`: diagnostic v2 pinset/input-manifest route. Today v2 requires exactly two producer plans and four cells ([mint_floor_artifact_generalized.py](/Users/edr/code/JouleWise/scripts/mint_floor_artifact_generalized.py:696)).
- Focused corresponding generator, readiness/T-0/launch, mint, finalizer, engine, and pipeline-tail tests.

It must not alter `d117_row_registry_v2.json`, `_v4` packs, marker/pinset bytes, production floor rules, production claim admission, or `_v4` custody. Use the fresh smoke checkout and a content-addressed, one-use, quarantine-root-bound GENESIS license. Estate 11 must rerun because generator/freeze admission changed; current precedent already requires estate 11 for mint-path changes ([decision_log.md](/Users/edr/code/JouleWise/docs/decision_log.md:184)).

## Disagreements

B gives the strongest predictive evidence—same pack, marker, arm, collector, and analysis path—but cannot itself satisfy this gate. A proves the same implementation chain on a different authenticated family, so its strongest weakness is precisely that the new diagnostic admission could become a bypass or conceal `_v4`-specific defects.

## Open questions

No sound third path is cheaper. Collecting all 80 real gamma members under production policy could reach DATA, but that is effectively the campaign window itself, contradicting the required pre-window proof.

## Recommendation

Choose A with the amendments above. The proof and shakedown may occur the same night only sequentially: proof fully passes and finalizes first, then the ruled pre-campaign reboot, then the `_v4` shakedown. They cannot be the same arm, occurrence, verdict, or custody tree.

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Recommend amended diagnostic-family path A; shakedown-as-proof cannot reach the required DATA-only claim edge and would create transaction-accounting risk.","pathspec":[],"verification":["Read-only trace of current generator, readiness, whole-window, finalizer, mint, analysis, transaction, and reason-partition code; no commands executed beyond source inspection.","Working tree observed clean on main; no files modified and no measurement started."],"flags":["no_edits","no_measurement","no_claude_call","bridge_hop_exhausted"]}
