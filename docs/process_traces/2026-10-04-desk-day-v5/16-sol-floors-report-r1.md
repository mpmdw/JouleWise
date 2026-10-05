```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_SCOPE: pin-derived lengths and live acceptance implemented; 5 independent tests and 18 importer tests pass, but non-512 pack generation requires prospective reported-energy registration changes.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "exact",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": "feat/2026-10-04-v5-floor-prefill-from-pin"
  },
  "pathspec": [
    "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
    "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
    "tests/test_d117_floor_qwen3_v5_generate.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-floors PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_floor_qwen3_v5_generate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=6)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-floors PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_prefill_pin_parses_and_validates_selection_record tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_each_ladder_rung_realizes_pin_and_derived_identities tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_non_ladder_prefill_length_refuses tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_reconfiguration_publishes_only_authenticated_length tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_acceptance_binding_is_registry_live_default_and_cutoff",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-floors PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_campaign_generator_core tests.test_generator_head_pin_relation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-floors PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_floor_qwen25_1p5b_plan.D179V5ReportedEnergyRegistrationTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-floors PYTHONDONTWRITEBYTECODE=1 python3 -B configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --check",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["generation failed: prefill_prompt_pin_unresolved: pass --prefill-prompt-pin with the issued G2-a pin"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "verified"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp/dd5-floors PYTHONDONTWRITEBYTECODE=1 python3 -B configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py --check",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["generation failed: prefill_prompt_pin_unresolved: pass --prefill-prompt-pin with the issued G2-a pin"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "verified"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-floors PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/dd5-floors/suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": null,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V8",
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
      "text": "The required non-512 reported-cell identities are rejected by joulewise/paper_reported_energy.py:29; its registration manifest at :163 and floor census at :282 also hardcode p512. No out-of-scope repository file was modified.",
      "needs": "Grant the requested scope and rule on prospective ladder registrations while preserving historical registration replay."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The generator module ran 18 tests with six errors: both models at 1024, 2048 and 4096 fail at the reported-energy registry. The legacy reported-energy importer ran one test with two errors because it supplies no authenticated pin.",
      "needs": "Complete the registration repair and configure a fixture pin in tests/test_d117_floor_qwen25_1p5b_plan.py:1658, then rerun the checks."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "blocking",
      "text": "The canonical suite was launched but has no completion result. It remains running as PID 64464; the sandbox denied SIGINT with Operation not permitted. V7's not_run means verification is incomplete, not that the command was never launched.",
      "needs": "Stop or finish PID 64464 and inspect /tmp/dd5-floors/suite.log before quiet-machine work."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Uncommitted: git add was denied creation of /Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-floors/index.lock. Nothing was pushed.",
      "needs": "Lead reviews and commits the authorized diff."
    },
    {
      "id": "F5",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Both committed floor roots contain only generate_configs.py. There are no committed pins or generated outputs to byte-compare. Both default --check commands refuse an unresolved pin; checks supplied with a synthetic 512 pin report missing pack inventory.",
      "needs": "Generate later from the real issued pin after resolving F1."
    },
    {
      "id": "F6",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Existing refused/collect-at-4096 handling remains an explicit refusal. Neither floor can represent the D-166 block-3 end-state authority branch that substitutes registration and harvest bindings for a selection record.",
      "needs": "A separate ruled extension is needed if the issuer emits that branch."
    },
    {
      "id": "F7",
      "kind": "scope_deviation",
      "level": "nonblocking",
      "text": "The baseline check used default temporary directories and initially placed its log outside the designated scratch directory; the log was moved under /tmp/dd5-floors. Subsequent commands set TMPDIR there, although the existing importer helper hardcodes dir=/tmp.",
      "needs": ""
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/paper_reported_energy.py",
      "docs/contracts/paper_reported_energy.md",
      "tests/test_paper_reported_energy.py",
      "tests/test_d117_floor_qwen25_1p5b_plan.py",
      "tests/test_campaign_generator_core.py"
    ],
    "reason": "The reported-energy contract registers only p512 identities, and importer fixtures assume a fixed prefill length or historical ledger cutoff.",
    "blocked_work": "Complete pack generation at 1024, 2048 and 4096, downstream reported-energy validation, and green final verification.",
    "minimal_change": "Prospectively support pin-bound ladder identities and registration digests while retaining historical 512 replay; supply authenticated fixture pins and select appropriate ledger-head fixtures for live floors."
  }
}
```

## Change

Both floors now publish the prefill length only after all existing pin checks pass. They require an integer ladder rung and matching selected, collection, and prompt token counts. Derived identities follow that length; registered pack IDs remain unchanged. Unsupported reported-cell identities refuse before any pack writes.

The complete identifier occurrence inventory, including source locations for both generators, is in [length-identifiers.tsv](/tmp/dd5-floors/length-identifiers.tsv). It covers plan, family, workload, stage, member, block, calibration-cell, reported-cell, artifact-cell, transport-group, consumer-family, and identity-unit names. Forced 512-token output policies remain unchanged.

Both generators yield these planning projections:

| Prefill tokens | Minutes | Hours | Seconds |
|---:|---:|---:|---:|
| 512 | 376.8 | 6.28 | 22,608 |
| 1024 | 753.6 | 12.56 | 45,216 |
| 2048 | 1,507.2 | 25.12 | 90,432 |
| 4096 | 3,014.4 | 50.24 | 180,864 |

The formula scales the inherited whole-window estimate by `length / 512`, retaining 20% headroom. It includes fixed and decode overhead; these are planning numbers, not measurements or validated upper bounds.

The acceptance binding is:

| Field | Value |
|---|---|
| ID | `d079_calibration_acceptance_v2_n24_25g83_r2` |
| Artifact SHA-256 | `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660` |
| Derivation SHA-256 | `10965d36527c73217154efdbd75ab923412685f3e79526bd31f33e6f9142e5c0` |
| Cutoff digest, sequence 376 | `a5b825b7dd77856be8d612be759be84f925a32f6e671481c2662bb03cbf57014` |

Registry authority: [artifact pin](/Users/edr/code/JouleWise-wt-dd5-floors/joulewise/calibration_bracketing.py:159), [registry entry](/Users/edr/code/JouleWise-wt-dd5-floors/joulewise/calibration_bracketing.py:219), and [live-default assignment](/Users/edr/code/JouleWise-wt-dd5-floors/joulewise/calibration_bracketing.py:231). The authenticated artifact supplies its [cutoff](/Users/edr/code/JouleWise-wt-dd5-floors/configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json:14) and [derivation digest](/Users/edr/code/JouleWise-wt-dd5-floors/configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json:1635).

## Verification notes

The blocker is the [p512-only reported-energy contract](/Users/edr/code/JouleWise-wt-dd5-floors/docs/contracts/paper_reported_energy.md:44). Recommendation: prospectively register ladder-specific identities while preserving historical 512 registrations and digests. Do not alias longer prompts to a reported cell named `p512`.

Other findings outside scope:

- [No-pin importer](/Users/edr/code/JouleWise-wt-dd5-floors/tests/test_d117_floor_qwen25_1p5b_plan.py:1658): must supply a synthetic authenticated pin.
- [Historical ledger fixture](/Users/edr/code/JouleWise-wt-dd5-floors/tests/test_campaign_generator_core.py:29): sequence 76 cannot serve as the new live floor cutoff.
- [Duration receipts](/Users/edr/code/JouleWise-wt-dd5-floors/joulewise/window_duration_margins.py:586): consume observed phase windows, so require no planning-length change.
- [Night-plan limits](/Users/edr/code/JouleWise-wt-dd5-floors/joulewise/night_gate.py:457): independently authored; no consumer automatically copies the floor’s runtime budget.

No committed generated pack bytes changed: none exist at this base. Synthetic 512 packs generated under scratch embed the new acceptance directly in `extraction_spec.json` and `plan_tree.json`.

## Residual risk

The work is **uncommitted**. The sandbox denied both Git’s index lock and the stop signal; canonical-suite PID **64464 remains running**. The lead must stop or finish it before quiet-machine work, then resolve the scope request and rerun final verification.