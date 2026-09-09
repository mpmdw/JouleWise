```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented D-179 registrations, closed projection kernel and synthetic regressions; acceptance requires one transient test-path scope expansion.",
  "workspace": {
    "base_requested": "e241e0b7",
    "base_mode": "exact",
    "head_start": "e241e0b79c353302401fc160884ab1d9ef4c6265",
    "head_end": "e241e0b79c353302401fc160884ab1d9ef4c6265",
    "upstream_end": null,
    "branch": "feat/2026-09-08-paper-S2"
  },
  "pathspec": [
    "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
    "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
    "configs/paper_supply/supply_map.json",
    "docs/contracts/paper_reported_energy.md",
    "docs/contracts/paper_supply_custody.md",
    "docs/decision_log.md",
    "docs/paper/results-fill-registry.md",
    "joulewise/paper_custody.py",
    "joulewise/paper_rendering.py",
    "joulewise/paper_reported_energy.py",
    "tests/test_d117_floor_qwen25_1p5b_plan.py",
    "tests/test_paper_reported_energy.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/paper-s2-acceptance.py > /private/tmp/paper-s2-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 145 tests in 58.974s",
          "FAILED (errors=1)",
          "ACCEPTANCE_RC=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ACCEPTANCE_RC=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: the mandated custody test attempts to create an unlisted repository probe. The scope guard blocked it before creation; no out-of-scope edit occurred.",
      "needs": "Authorize temporary creation and deletion of tests/fixtures/paper_custody/.untracked-nongoverned-anchor-probe, then rerun acceptance."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Projection arithmetic and synthetic custody replay are implemented. Production parent/strict-bundle replay and registration-before-spec ordering proof remain incomplete; no reported-energy issuance gate or production digest was added.",
      "needs": "Complete production provenance joins and ordering proof before registering an issuing gate."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/fixtures/paper_custody/.untracked-nongoverned-anchor-probe"
    ],
    "reason": "tests/test_paper_custody.py:523 creates this probe in the requested acceptance module.",
    "blocked_work": "One custody test and an overall successful acceptance return code.",
    "minimal_change": "Permit only the existing test's temporary probe creation and deletion."
  }
}
```

## Change

- **Contract and twenty prospective outputs:** [paper_reported_energy.md:90](/Users/edr/code/JouleWise-wt-paper-S2/docs/contracts/paper_reported_energy.md:90). The [kernel:208](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_reported_energy.py:208) implements the fifty-member mean, stratified interval, deterministic bounds and observed-token ratio.
- **Executable registrations:** installed in both [1.7B:2116](/Users/edr/code/JouleWise-wt-paper-S2/configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2116) and [8B:2116](/Users/edr/code/JouleWise-wt-paper-S2/configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py:2116) generators, with [generator regressions:1633](/Users/edr/code/JouleWise-wt-paper-S2/tests/test_d117_floor_qwen25_1p5b_plan.py:1633). Removing a registration refuses validation while leaving floor validation unchanged.
- **Custody separation:** [source census:735](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_custody.py:735), [fixture replay:1298](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_custody.py:1298), and [renderer:41](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_rendering.py:41) use a separate projection; the closed mint report remains unchanged. [Supply-map:2](/Users/edr/code/JouleWise-wt-paper-S2/configs/paper_supply/supply_map.json:2) changes add the pending 8B role and refresh synthetic receipt pins.
- **Policy:** [D-179:11161](/Users/edr/code/JouleWise-wt-paper-S2/docs/decision_log.md:11161) records rulings 1–7. [Registry:375](/Users/edr/code/JouleWise-wt-paper-S2/docs/paper/results-fill-registry.md:375) and [custody contract:290](/Users/edr/code/JouleWise-wt-paper-S2/docs/contracts/paper_supply_custody.md:290) preserve retired placements and issuance restrictions.

Regression counterfactuals in [test_paper_reported_energy.py](/Users/edr/code/JouleWise-wt-paper-S2/tests/test_paper_reported_energy.py):

| Lines | Corruption or alternative → observed distinction |
|---|---|
| 81 | Pooled half-width differs from independently calculated stratified half-width. |
| 98, 103 | Missing observation or registered member → refusal; no 49-member mean. |
| 108 | Weights 0.5/0.5 produce 32 J instead of 42.5 J; altered registration refuses. |
| 115, 124 | Zeroing a bound moves each endpoint by 0.2 J; removing the kind refuses. |
| 129 | Prediction-term substitution → refusal by name. |
| 139, 191 | Configured, fallback, missing, malformed, zero or scope-drifted tokens → ratio refusal; mean preserved. |
| 152 | Mean of ratios changes decode value; substituted result refuses recomputation. |
| 160, 225 | Reordered/duplicated members, including coordinated report reordering → refusal. |
| 171, 201 | Swapped model/phase, stale selection/prompt/basis pins or invalid member → refusal. |
| 180 | Incorrect endpoints, fabricated denominator, copied floor count or extra field → refusal. |
| 207 | Attribution floor changed to 1000 J → endpoints unchanged. |
| 214 | New phase-ratio object remains rejected by the existing B8 validator. |
| 234 | Both models and both prefill registrations reproduce observed-token totals. |
| 242, 249 | Owner census present; issuance gate absent; fixture rendering and public evidence bypasses refuse. |

## Verification notes

[Final acceptance log](/private/tmp/paper-s2-acceptance.log): **144 passed; one scope-blocked error**. All five requested modules exist; none were dropped. `test_gen_state` passed all 43 tests and `test_docs_freshness` passed all 31; no pin changes are needed.

The initial broad write guard misclassified temporary fixture operations. The corrected final run blocks only the actual unlisted repository probe. HEAD is unchanged; all twelve changed paths are authorized.

## Residual risk

No arithmetic semantic fields remain unresolved. Production authentication of actual parents and strict members, upstream bound-allocation joins, and registration-before-spec proof remain unimplemented, as enumerated in [the contract:136](/Users/edr/code/JouleWise-wt-paper-S2/docs/contracts/paper_reported_energy.md:136). Synthetic checks confer no production acceptance.

Next step: authorize the exact transient probe path and rerun acceptance; complete production replay before registering issuance.