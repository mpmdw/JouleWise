```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Added v2 decision and replay branches, but end-to-end claim admission needs out-of-scope manifest changes and an authenticated F_est source.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "descendant",
    "head_start": "0d2b44978f7f59632ca4876e3a6f919db39d95d0",
    "head_end": "0d2b44978f7f59632ca4876e3a6f919db39d95d0",
    "upstream_end": "8bf80eccd5f492d6554887ba5fa539e99e2ff6a8",
    "branch": "feat/2026-09-24-claimgate-v2"
  },
  "pathspec": [
    "docs/contracts/analysis_plans.md",
    "docs/decision_log.md",
    "joulewise/analysis_engine/__init__.py",
    "joulewise/analysis_engine/artifact.py",
    "joulewise/analysis_engine/estimators.py",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/analysis_engine/registry.py",
    "joulewise/paper_custody.py",
    "tests/test_claimgate_v2.py"
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
        "tail": ["Ran 276 tests in 36.100s", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V2-claims",
      "kind": "other",
      "cmd": "CLAIMGATE_PERM_LIB=/tmp/claimgate_v2_perm_resume.dylib python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/run.py claims 5000 > docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/claims.jsonl",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V2-nights",
      "kind": "other",
      "cmd": "CLAIMGATE_PERM_LIB=/tmp/claimgate_v2_perm_resume.dylib python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/run.py nights 10000 > docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/nights.jsonl",
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
          "CG3 no_change_false_FAIL_range=0.0309..0.0459",
          "CG3 margin_false_PASS_range=0.0005..0.0016",
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
      "id": "extended-modules",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_analysis_claims tests.test_analysis_engine tests.test_detection_floor tests.test_epoch_equivalence_check tests.test_claimgate_v2 tests.test_paper_custody tests.test_analysis_integration tests.test_analysis_ratio_integration tests.test_axi_analysis_manifest tests.test_authentication_io tests.test_claim_side_bound",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 502 tests in 84.717s", "FAILED (failures=19, skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "canonical-suite",
      "kind": "suite",
      "cmd": "python3 -B -m unittest discover -s tests > /tmp/claimgate_v2_canonical.out 2>&1",
      "cwd": ".",
      "observed": {"result": "not_run", "exit_code": 130, "tail": ["KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Exact-key manifest validators reject v2 contrast fields before the engine can consume them. No out-of-scope path was edited.",
      "needs": "Lead-issued WRITE_SCOPE expansion for the requested manifest paths and tests."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "No authenticated same-epoch calibration wire supplies F_est, its unit, and its registered artifact binding. V2 artifact admission therefore explicitly refuses.",
      "needs": "Rule the authenticated F_est source and replay check."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Version is per contrast, but the current registry has one shared floor selector; mixed v1/v2 contrast semantics are unspecified and currently refused.",
      "needs": "Rule whether mixed-version registries require per-contrast selectors or separate registries."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Nineteen paper-custody tests report stale supply-map receipt digests after validator source changes; immutable fixtures were preserved. The repository-wide suite was interrupted after the focused gate and extended modules.",
      "needs": "Lead adjudicates receipt reissuance and reruns the canonical suite on the completed candidate."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/analysis_manifest.py",
      "joulewise/analysis_manifest_v3.py",
      "tests/test_analysis_manifest.py",
      "tests/test_analysis_manifest_v3.py"
    ],
    "reason": "Both production manifest validators enforce exact contrast keys and reject the ruled per-contrast v2 version, claim shape, and envelope registration fields.",
    "blocked_work": "End-to-end v2 manifest admission, envelope registration, and full-tier PR acceptance.",
    "minimal_change": "Add only prospective v2 contrast and envelope schema branches with focused tests; preserve v1 exact-key replay."
  }
}
```

## Change

The WIP’s CG-4(a), (b), (d), (e), and (g) work remains in place: [D-083’s addendum](/Users/edr/code/wt-278ebc9e-cgimpl/docs/decision_log.md:11339), the [versioned floor row](/Users/edr/code/wt-278ebc9e-cgimpl/docs/contracts/analysis_plans.md:29), [F_est calculation](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/detection_floor.py:858), [D-102’s prospective night rule](/Users/edr/code/wt-278ebc9e-cgimpl/docs/decision_log.md:6802), the [simulation report](/Users/edr/code/wt-278ebc9e-cgimpl/docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/README.md:1), and the [after-the-fact note for Ed](/Users/edr/code/wt-278ebc9e-cgimpl/docs/decision_log.md:12250).

For CG-4(c), I added per-contrast version and shape checks in [registry.py](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/registry.py:448), typed floor fields in [inputs.py](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/inputs.py:386), and a shared Δ−F_est calculation before raw TOST and Holm in [the engine](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/__init__.py:1407). The engine also records v2 sign-flip minimum p and uses the 90% interval for equivalence. [Artifact replay](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/artifact.py:678) and [paper custody](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/paper_custody.py:636) use those v2 fields. Until F_est has an authenticated source, artifact validation refuses v2 admission at [artifact.py](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/artifact.py:2294).

The magistrate’s R2 deferral is recorded as an open item in the floor row and D-083 addendum. [Envelope aggregation](/Users/edr/code/wt-278ebc9e-cgimpl/joulewise/analysis_engine/estimators.py:466) still refuses shared or unspecified scopes with `envelope_term_scope_unknown`, naming the missing registered `cross_envelope_independence` field. No scope or independence field was added. Changes are uncommitted.

**CG-4(f), for AP-5M v5:** register an additive J/correct primary contrast, fixed planned `K` and `n_reg`, one frozen claim shape per contrast, and CG-1/CG-2 citations; replace the block-floor sentence with window-admission reason codes. A dimensionless contrast needs a separately ruled estimator, matched floor derivation, and unit schema.

## Verification notes

V1, V2, V3, and V4 passed with the tails in the envelope. The simulation rerun reproduced the committed result files byte for byte. V3 retained the recorded September 19 verdicts: **INCONCLUSIVE at m=4** and **FAIL at m=7**.

The [per-model simulation tables](/Users/edr/code/wt-278ebc9e-cgimpl/docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/README.md:7) give every 2σ/5σ power and CG-3 detection cell. Across CG-1 models, maximum false admission was **0.04%**; 2σ power ranged **1.76–99.98%** across model, `k`, and bound settings, and 5σ power ranged **99.72–100%**. CG-2 boundary false admission was **0%**. Every fixed-r7 CG-3 generator met the 5% ceilings: no-change false FAIL **3.09–4.59%**, boundary false PASS **0.05–0.16%**. The tables also report +3σ, +5σ, ×4, and ×16 detection for each model and `m`. R5’s computed r7 values are **27.051261 ms**, **2.709555 ms**, **2.460856 ms**, **5.209350 ms**, **8.612997 ms**, and **3.403647 ms**; both the ruling’s printed figures and these computed values are preserved in the report.

## Residual risk

**NEEDS_SCOPE:** Expand `WRITE_SCOPE` to the four paths in `scope_expansion`. The supplied allowlist is exhaustive, so I left those exact-key manifest validators and their tests untouched.

**NEEDS_RULING — F_est provenance:** Should v2 carry authenticated calibration envelope means and recompute F_est from them, or bind a separately authenticated calibration sidecar? I recommend recomputation from an authenticated same-epoch calibration record, with unit and artifact ID checked at replay. This blocks claim-bearing v2 artifacts.

**NEEDS_RULING — mixed versions:** Should a registry with both v1 and v2 contrasts have per-contrast floor selectors, or must each version use a separate registry? I recommend per-contrast selectors to match the ruled per-contrast version placement. The current shared selector refuses mixed versions.

The 19 extended-suite failures arise at paper-custody fixture receipt digest checks against changed validator source; the issued fixtures were preserved. The canonical suite still needs a completed run after the scope and provenance decisions.