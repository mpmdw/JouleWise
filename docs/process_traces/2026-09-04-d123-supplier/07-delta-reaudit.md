```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Fix round 2 is NOT LANDABLE: B1/F1's self-sealed caller-authority signature survives at the frozen-spec and bundle-validation boundary; all other prior findings are cured.",
  "workspace": {
    "base_requested": "daebf8fc",
    "base_mode": "exact",
    "head_start": "daebf8fc18aa6083080e70513658a6b22a576044",
    "head_end": "daebf8fc18aa6083080e70513658a6b22a576044",
    "upstream_end": "daebf8fc18aa6083080e70513658a6b22a576044",
    "branch": "feat/2026-09-04-d123-reported-mean"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-d123-supplier/07-delta-reaudit.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "same_signature": "YES — decisive: B1/F1's self-sealed caller authority survives at the frozen-spec and bundle-validation seam.",
    "reaudit": [
      {"id": "execution-B1", "result": "NOT CURED", "evidence": "V4: 19 strict-validator errors are accepted; a self-resealed spec changes the selected mean 202.55→52.55 with all other parents unchanged."},
      {"id": "execution-B2", "result": "CURED", "evidence": "V1/V4: the 49+1 mixed-source case issues and records both sources."},
      {"id": "execution-B3", "result": "CURED", "evidence": "V1/V4: both duplicate-alpha orders STOP_FILL alpha and preserve beta."},
      {"id": "execution-S1", "result": "CURED", "evidence": "V1/V4: resealed missing custody returns the named derivation mismatch; no zero digest."},
      {"id": "execution-S2", "result": "CURED", "evidence": "V1 directly gets the named derivation mismatch below outer gates."},
      {"id": "contract-F1", "result": "NOT CURED", "evidence": "Same V4 self-sealed-spec/strict-invalid-bundle evidence as B1."},
      {"id": "contract-F2", "result": "CURED", "evidence": "V1/V4: t95 is rejected with issuance_composition_rule_not_current."},
      {"id": "contract-F3", "result": "CURED", "evidence": "V1 checks all 20 rows; V3 passes both registry suites."},
      {"id": "contract-F4", "result": "CURED", "evidence": "Same executed mixed-source evidence as execution-B2."},
      {"id": "contract-F5", "result": "CURED", "evidence": "V1/V4: fully resealed energy arithmetic returns the named derivation mismatch."},
      {"id": "contract-F6", "result": "CURED", "evidence": "Same executed both-order duplicate counterfactual as execution-B3."},
      {"id": "contract-F7", "result": "CURED", "evidence": "Same executed missing-custody counterfactual as execution-S1."}
    ],
    "findings": [
      {
        "id": "R2-B1",
        "severity": "blocker",
        "file": "joulewise/reported_phase_energy.py:308-413,473-611; joulewise/floor_extraction.py:1846-1996",
        "text": "The producer still has no authenticated authority for the frozen reported-energy universe and does not validate member bundles: parent wrappers are caller documents checked only against caller-supplied self-hashes, while the member loader performs partial reads instead of strict bundle validation.",
        "counterfactual": "V4 reseals only extraction_spec.reported_energy_cells, swaps the decode and selected-prefill 50-member lists, and obtains an issued 52.55 J selected-prefill mean instead of 202.55 J with every other parent wrapper unchanged; the accepted fixture bundle independently has 19 strict-validator problems.",
        "cure_shape": "Load the frozen spec from an authoritative path/digest under the authentication session, bind its exact ordered reported_energy_cells bytes, and require strict validation of every bundle before derivation; reject a self-resealed universe and the existing strict-invalid synthetic bundle."
      }
    ],
    "new_defects": []
  },
  "verification": [
    {"id": "V1", "kind": "test", "cmd": "python3 -m unittest tests.test_reported_phase_energy", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 21.620s", "OK"]}, "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests in .*s[\\s\\S]*OK"}},
    {"id": "V2", "kind": "test", "cmd": "python3 -m unittest tests.test_floor_extraction.D117MintConsumptionProfileTests", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 10 tests in 0.031s", "OK"]}, "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*s[\\s\\S]*OK"}},
    {"id": "V3", "kind": "test", "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 2.723s", "OK"]}, "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests in .*s[\\s\\S]*OK"}},
    {"id": "V4", "kind": "test", "cmd": "python3 -c 'import copy,json,tempfile; from pathlib import Path; import joulewise.reported_phase_energy as c; from joulewise.cli import validate_bundle as v; import tests.test_reported_phase_energy as t; b=json.loads(t.BLUEPRINT.read_text()); d=tempfile.TemporaryDirectory(); r=Path(d.name); m=t._source_material_from_blueprint(b[\"packs\"][0],b[\"selected_prefill_tokens\"],r); s=c.build_reported_phase_energy_source(t._source_bytes(m)); o=m[\"whole_window_evaluation_basis\"][\"document\"][\"member_occurrences\"][0]; q=v(r/o[\"bundle_path\"],strict=True); a=copy.deepcopy(m); x=a[\"extraction_spec\"][\"document\"][\"reported_energy_cells\"]; x[0][\"members\"],x[2][\"members\"]=x[2][\"members\"],x[0][\"members\"]; t._reseal_wrapper(a,\"extraction_spec\"); z=c.build_reported_phase_energy_source(t._source_bytes(a)); print(\"strict\",len(q),\"source\",c.validate_reported_phase_energy_source(s),\"means\",s[\"reported_energy_projection\"][\"document\"][\"reported_energy_cells\"][2][\"mean_j_per_request\"],z[\"reported_energy_projection\"][\"document\"][\"reported_energy_cells\"][2][\"mean_j_per_request\"],\"same\",all(m[k]==a[k] for k in (\"extraction_report\",\"whole_window_evaluation_basis\",\"g2a_selection\",\"prompt_pin\"))); d.cleanup()'", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["strict 19 source [] means 202.55 52.55 same True"]}, "expected": {"exit_code": 0, "tail_regex": "strict 19 source \\[\\] means 202\\.55 52\\.55 same True"}},
    {"id": "V5", "kind": "inspection", "cmd": "git show HEAD", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": ["registry = REGISTRY.read_text(encoding=\"utf-8\")", "for token in expected:"]}, "expected": {"exit_code": 0, "tail_regex": "for token in expected:"}},
    {"id": "V6", "kind": "inspection", "cmd": "git diff --quiet origin/main -- scripts/render_results_fills.py configs/campaigns/d117_contrast_v5/generate_configs.py configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py tests/fixtures/results_prose_render/synthetic_alpha_floor.json", "cwd": ".", "observed": {"result": "pass", "exit_code": 0, "tail": []}, "expected": {"exit_code": 0, "tail_regex": "^$"}}
  ],
  "flags": [
    {"id": "F1", "kind": "verification_gap", "level": "nonblocking", "text": "The canonical suite was excluded by the preflight rule and was not run.", "needs": "Lead may run broader verification after the blocker is cured."},
    {"id": "F2", "kind": "baseline_drift", "level": "nonblocking", "text": "Ruling addenda 09 and 10 are absent from daebf8fc's tree; their committed versions were inspected from repository history and are unrelated to R1.", "needs": "Preserve those later addenda when integrating this branch."}
  ]
}
```

## Findings

### R2-B1 — blocker — NOT CURED

The numeric child is now producer-derived, but its authority is still caller-sealed. `_wrapped_document` checks an embedded document against the digest supplied beside it and never reads the named path. `_validated_reported_energy_registration` authenticates only the floor `cells` projection; the caller-controlled `reported_energy_cells` universe is not pinned by that relation. The member loader then parses selected surfaces but never calls `validate_bundle(..., strict=True)`.

The temporary-tree V4 counterfactual resealed only the embedded extraction spec and exchanged the decode and selected-prefill member lists. The production source and artifact accepted the change and issued the selected-prefill gross mean as 52.55 J instead of 202.55 J; report, whole-window basis, G2-a, and prompt-pin wrappers stayed identical. The same source accepted a member bundle with 19 strict-validator errors. This is B1/F1's self-sealed authority signature at the next parent seam, so same-signature is decisively **YES** and the branch is not landable. All mutations were confined to temporary directories and removed; no repository evidence was changed.

No independent new defect was found.

Against `origin/main`, the relevant diff is confined to the ruled D-123 producer/validator path and registry rows DS-09/10/12/13/14/16/17/18/20/21/22/24. The frozen renderer, three `_v5` generators, and preexisting floor fixture are unchanged. Addenda 09/10 were inspected from committed objects `e3c809c9`/`5827379c` because they are absent from this pinned branch; neither amends R1.

## Residual risk

Verification was fixture-only and restricted to the permitted suites; the canonical suite and live/quiet-machine evidence were not run.
