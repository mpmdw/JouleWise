```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Scoped claim-gate components, v2 epoch rule, and desk simulations are complete; full claim admission is blocked by the write allowlist.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "head_end": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "upstream_end": "eec7acaa4ee3018bd5f7118aa03ba7868e8c779b",
    "branch": "feat/2026-09-24-claimgate-v2"
  },
  "pathspec": [
    "docs/contracts/analysis_plans.md",
    "docs/decision_log.md",
    "joulewise/analysis_engine/claims.py",
    "joulewise/analysis_engine/estimators.py",
    "joulewise/detection_floor.py",
    "scripts/epoch_equivalence_check.py",
    "tests/test_epoch_equivalence_check.py",
    "tests/test_claimgate_v2.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/README.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/claims.jsonl",
    "docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/nights.jsonl",
    "docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/models.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/run.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/perm.c",
    "docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/summarize.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_analysis_claims tests.test_analysis_engine tests.test_detection_floor tests.test_epoch_equivalence_check tests.test_claimgate_v2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 274 tests in 37.408s", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V2-claims",
      "kind": "other",
      "cmd": "CLAIMGATE_PERM_LIB=/tmp/claimgate_v2_perm.dylib python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/run.py claims 5000 > docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/claims.jsonl",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V2-nights",
      "kind": "other",
      "cmd": "CLAIMGATE_PERM_LIB=/tmp/claimgate_v2_perm.dylib python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/run.py nights 10000 > docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/nights.jsonl",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/summarize.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CG1 cells=24 N=5000 max_false_admission=0.0004",
          "CG2 cells=24 N=5000 max_boundary_false_admission=0.0000",
          "CG3 fixed_r7 cells=48 null_boundary_N=10000 permutations=2000",
          "CG3 no_change_false_FAIL_range=0.0309..0.0459",
          "CG3 margin_false_PASS_range=0.0005..0.0016",
          "CG3 simulated_old cells=48 N=2000 sensitivity_only",
          "SIMULATION_CHECKS_PASS"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "SIMULATION_CHECKS_PASS"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_v1_replays_both_recorded_2026_09_19_nights",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.000s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "canonical-suite",
      "kind": "suite",
      "cmd": "python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "CG-4(c) requires engine, registry, floor-input, sensitivity, artifact, and custody writes outside WRITE_SCOPE. No out-of-scope file was edited.",
      "needs": "Lead-issued resumed prompt expanding the exact paths below."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R2 supplies shared-term semantics but no correlation_scope wire spelling or authenticated source for cross-envelope independence; the helper refuses that scope.",
      "needs": "Rule the frozen wire token and where independence is registered and checked."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The canonical suite was interrupted after roughly 550 of approximately 6800 tests; it had emitted no failure summary. Focused V1 passed.",
      "needs": "Rerun the canonical suite on the completed candidate."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced four commits beyond the unchanged branch HEAD during this session.",
      "needs": "Lead checks integration against the new main."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/analysis_engine/inputs.py",
      "joulewise/analysis_engine/registry.py",
      "joulewise/analysis_engine/__init__.py",
      "joulewise/analysis_engine/artifact.py",
      "joulewise/analysis_engine/sensitivity.py",
      "joulewise/paper_custody.py"
    ],
    "reason": "CG-4(c) and refuter R1–R3 require these production consumers and validators to version the floor, effective-margin Holm path, sign-flip diagnostic, interval fields, and fixed-envelope eligibility together.",
    "blocked_work": "End-to-end v2 claim admission and artifact replay; full-tier PR acceptance.",
    "minimal_change": "Add only the v2 schema and decision branches while retaining v1 replay."
  }
}
```

## Change

- **CG-4(a), (d):** Added the dated [D-083 addendum](/Users/edr/code/wt-278ebc9e-cgimpl/docs/decision_log.md:11338) and the CG-1 [estimate-scale floor calculator](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/detection_floor.py:858). The [D-102 addendum](/Users/edr/code/wt-278ebc9e-cgimpl/docs/decision_log.md:6802) records the night-rule constants and prospective version boundary.
- **CG-4(b), (c):** Versioned the [analysis-plan floor row](/Users/edr/code/wt-278ebc9e-cgimpl/docs/contracts/analysis_plans.md:29). Added a 90% estimator interval and an independent-run envelope helper in [estimators.py](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/estimators.py:463), plus the v2 effective-margin and refusal path in [claims.py](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/claims.py:264). The helper refuses unruled shared scopes. The [epoch checker](/Users/edr/code/wt-278ebc9e-cgimpl/scripts/epoch_equivalence_check.py:538) implements prospective CG-3 v2 with v1 selectable for replay.
- **CG-4(e):** The [simulation report and per-model tables](/Users/edr/code/wt-278ebc9e-cgimpl/docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/README.md:1) record 24 claim cells and 48 fixed-r7 night cells. Maximum direction false admission was **0.04%**; equivalence boundary false admission was **0%**. At 2σ, direction power spans **1.76–99.98%** across the registered models, envelope counts, and bound settings; at 5σ it spans **99.72–100%**. Every fixed-r7 generator at both m values met the 5% ceilings: no-change false FAIL **3.09–4.59%**, boundary false PASS **0.05–0.16%**. The report gives each model’s +3σ, +5σ, ×4, and ×16 detection and the simulated-old sensitivity.
- **CG-4(g):** Added [after-the-fact text for Ed](/Users/edr/code/wt-278ebc9e-cgimpl/docs/decision_log.md:12246). Delivery remains with the lead. R5’s original illustrative r7 figures and the corrected figures are both recorded in the simulation report.

**CG-4(f), reserved for AP-5M v5:** Register an additive J/correct primary contrast; exclude the dimensionless alternative under refuter R4 pending a separate estimator and unit ruling; freeze `K`, `n_reg`, and one claim shape per contrast; cite CG-1/CG-2; replace the “block window must clear floor_gate_j” sentence with the window-admission reason codes. No AP-5M file was edited.

## Verification notes

V1, V2, V3, and V4 passed as shown in the envelope. V3 replayed the checked-in September 19 nights to **INCONCLUSIVE (m=4)** and **FAIL (m=7)**. The simulation is CPU-only evidence; the full production v2 admission path remains incomplete. The repository-wide suite was interrupted before a verdict. All changes are uncommitted, as required by the sandbox.

## Residual risk

**NEEDS_RULING — R2:** Which frozen `correlation_scope` value denotes an identical contribution shared within one envelope, and which registered field proves independence across envelopes? Options: add explicit scope and independence fields, or defer shared terms. **Recommendation:** rule explicit fields; retain the current refusal until they exist. This blocks shared-term aggregation.

**NEEDS_RULING — version placement:** The binding text names one `claim_rule_version` but does not place it in the existing exact-key registry schema. Options: per-contrast, registry-wide, or both. **Recommendation:** freeze it per contrast so different registered contrasts cannot inherit a version implicitly. This blocks the out-of-scope schema wiring.