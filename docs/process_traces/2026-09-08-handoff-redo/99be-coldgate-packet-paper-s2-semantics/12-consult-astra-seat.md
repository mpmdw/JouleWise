```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Preserve all-50 request weighting, model block dependence, envelope the complete mean interval, and use observed-token totals.",
  "workspace":{"base_requested":"e241e0b7","base_mode":"exact","head_start":"e241e0b79c353302401fc160884ab1d9ef4c6265","head_end":"e241e0b79c353302401fc160884ab1d9ef4c6265","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":["AGENTS.md","CLAUDE.md","coldgate-packet-s2/","coldgate-packet/"],
  "verdict":{"findings":[{"id":"F1","severity":"blocker","summary":"Register membership and clustered sampling separately."},{"id":"F2","severity":"blocker","summary":"Register complete interval composition under the amended assigned-energy estimand."},{"id":"F3","severity":"blocker","summary":"Register and independently authenticate token aggregation."}]},
  "verification":[{"id":"V1","kind":"test","cmd":"python3 -B -c 'import json; from joulewise.floor_extraction import validate_extraction_spec as v; s=json.load(open(\"configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json\")); a=v(s); s[\"reported_energy_cells\"]=[{\"members\":[],\"mean_j\":10,\"lower_j\":9,\"upper_j\":11,\"j_per_token\":0.02,\"token_source\":\"config_fallback\"}]; b=v(s); print(\"baseline_errors=\"+str(len(a))); print(\"mutated_errors=\"+str(len(b))); print(\"unchanged_validation=\"+str(a==b))'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["baseline_errors=0","mutated_errors=0","unchanged_validation=True"]},"expected":{"exit_code":0,"tail_regex":"unchanged_validation=True"}}],
  "flags":[{"id":"R1","kind":"verification_gap","level":"nonblocking","text":"Production issuance and proposed endpoint algorithm NOT EXECUTED; V1 demonstrates only structural-validator acceptance.","needs":"Lead implements and verifies adopted registration."}]
}
```

## Findings

The following quoted text is my proposed prospective registration, not an existing frozen production specification.

1. **F1 — Q1: request-weighted, stratified aggregation (refined alternative b).**  
   **Estimand:** Expected gross interval-overlap assigned phase energy per request under the fixed workload and scheduled 10-repeat/40-null-member mixture, conditional on the registered machine/window model.

   **Authority:** `docs/decision_log.md:7990` requires the same 50 members; both `configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5/generate_configs.py:2082` already specify arithmetic averaging, 50 members, and missing-member refusal. These generators materially narrow the packet’s alternatives. `docs/contracts/paper_supply_custody.md:290` requires the complete ordered census.

   **Register:** “For each cell, ordered_members is the frozen phase-specific sequence of ten absolute repeats followed by ten complete null blocks in A1/B1/B2/A2 order. Bind selected prefill length through G2-a and its prompt pin; never substitute the incidental short-prefill cell. Require all 50 unique strict bundles and governing window admission; missing, invalid, duplicate or mismatched membership refuses the cell. Preserve valid outliers. Let r be the ten repeat energies and b the ten four-member block means. Report m=0.2·mean(r)+0.8·mean(b), with bundle_count=50 and modeled_unit_count=20.”

   **Independence unit:** A standalone repeat or complete null block, with independence between these units explicitly assumed, not established by admission.  
   **Mutation:** Repeat energies 10 J and all null-member energies 20 J give **18 J**; equal weighting of the 20 units gives **15 J**.

2. **F2 — Q2: extrema of the complete mean interval, alternative b.**  
   **Estimand:** A model-based 95% interval for Q1’s mean, enclosed over registered allocation uncertainty, conditional on held-average reconstruction.

   **Authority:** `docs/contracts/measurement_methodology.md:321` settles Student-t reporting. Crucially, `docs/decision_log.md:10939` supersedes unrestricted physical-attribution claims and forbids composing the partial-record diagnostic into bounds. `joulewise/detection_floor.py:879` is prediction arithmetic.

   **Register:** “Use V=0.2²·s_r²/10+0.8²·s_b²/10 and conservative Student-t reference ν=9. The nominal interval is m±t(.975,9)√V. Form each unit’s allocation interval from freshly reconstructed member timing envelopes; block endpoints are averages of member endpoints. Use their Cartesian product as an explicitly conservative admissible enclosure, without assumed cancellation. At every vertex recompute m and V; publish the minimum lower and maximum upper endpoint. Retain nominal SDs and interval separately. Add neither a universal 1 J charge nor a floor prediction term. No additional drift correction is registered for this scheduled-window mixture; floor-specific A_k does not establish a mean-error bound. Label dependence and between-window generalization unverified.”

   **Independence unit:** Q1’s units; widening does not establish independence (`docs/paper/protocol/prospective-comparison-protocol.md:455`).  
   **Mutation:** All nominal unit energies 10 J with ±1 J envelopes: nominal-interval widening gives upper **11 J**. An admissible vertex—repeats all 11, nine block means 11, one 9—already gives **11.201945 J**. The full-envelope upper endpoint cannot be smaller.

3. **F3 — Q3: ratio of totals.**  
   **Estimand:** Assigned phase joules per observed token across the registered request mixture.

   **Authority:** `docs/paper/results-fill-registry.md:388` and `:393` require observed prompt/output tokens; `joulewise/reduce.py:3742` excludes configured fallback. S6 leaves quantity bindings unresolved (`docs/contracts/paper_comparison_rendering.md:29`).

   **Register:** “Compute per_token=ΣE_i/ΣT_i over precisely Q1’s 50 members. Authenticate positive integer runtime-observed prompt counts for prefill and output counts for decode, joined to the same bundle, request boundary, tokenizer and prompt identity. Missing, zero, malformed or unsupported-provenance counts refuse the companion value without dropping members or replacing counts; they do not redefine the energy mean.”

   **Independence unit:** Q1’s units; tokens are denominators, never independent repetitions.  
   **Mutation:** Energies (10,30) J and counts (10,100) yield **0.363636 J/token**, versus **0.65** for mean-of-ratios.

**Failure-mode test:** Yes, plausible wrong values can pass the existing structural validator: V1 demonstrates this on a historical specification in memory. Require independent source reconstruction to reject a deleted/reordered member, the nominal-only widening above, and configured-token substitution—even after derived hashes are refreshed. Production-path rejection: **NOT EXECUTED**.

**Exhibit F5:** The frozen extraction specification is prerequisite to producing numbers, not to registering these rules. Its absence is confirmed; `docs/contracts/paper_supply_custody.md:206` requires the reviewed production blob and census. Registration may precede it, but exact member binding, successor generation, freeze and D-173 admission must precede production calculation. No edits made.

Verdict: **ADOPT prospectively; numerical issuance remains blocked pending implementation and source-replay verification.**