```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented Q-R1-5's producer-owned reported-energy projection, authenticated parent-byte derivation, mismatch validation, and fully resealed-child regression.",
  "workspace": {
    "base_requested": "1d908fe514337cb2db136e2f06a255fac9e0f42f",
    "base_mode": "exact",
    "head_start": "1d908fe514337cb2db136e2f06a255fac9e0f42f",
    "head_end": "1d908fe514337cb2db136e2f06a255fac9e0f42f",
    "upstream_end": "1d908fe514337cb2db136e2f06a255fac9e0f42f",
    "branch": "feat/2026-09-04-d123-reported-mean"
  },
  "pathspec": [
    "docs/paper/results-fill-registry.md",
    "docs/process_traces/2026-09-04-d123-supplier/06-sol-fix-round-2-report.md",
    "joulewise/bundle_read.py",
    "joulewise/floor_extraction.py",
    "joulewise/reported_phase_energy.py",
    "tests/test_reported_phase_energy.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-d123-supplier/05-consult-sol-structural.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_reported_phase_energy",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 20.774s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_floor_extraction.D117MintConsumptionProfileTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 0.031s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 2.730s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "python3 -m py_compile joulewise/bundle_read.py joulewise/floor_extraction.py joulewise/reported_phase_energy.py scripts/build_reported_phase_energy.py tests/test_reported_phase_energy.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "shasum -a 256 tests/fixtures/reported_phase_energy/preexisting_floor_output.json tests/fixtures/results_prose_render/synthetic_alpha_floor.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "79e346d1171a05f5b17eaa86d27964393d49b9aee7849906c69f32630a12365f  tests/fixtures/reported_phase_energy/preexisting_floor_output.json",
          "79e346d1171a05f5b17eaa86d27964393d49b9aee7849906c69f32630a12365f  tests/fixtures/results_prose_render/synthetic_alpha_floor.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^(79e346d1171a05f5b17eaa86d27964393d49b9aee7849906c69f32630a12365f  .+\\n){1}79e346d1171a05f5b17eaa86d27964393d49b9aee7849906c69f32630a12365f  .+$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical repository suite was not run because the supplied preflight rule restricted this seat to the named reported-energy, touched floor-extraction, and registry tests.",
      "needs": "Lead may run broader verification outside this restricted seat."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The cure is verified with authenticated synthetic bundle parents; no live hardware or quiet-window evidence was produced.",
      "needs": "Lead retains any live-gate verification."
    }
  ]
}
```

## Change

Q-R1-5 now has one production projector. Source material cannot contain a caller-supplied projection; the producer derives member identities, custody digests, phase points, anchor-shift endpoints, token denominators, cell reductions, intervals, and per-token values from the authenticated bundle-byte loaders shared with floor extraction. Source, artifact, and issuance paths recompute that parent/value relation, and any resealed child difference returns `reported_energy_projection_derivation_mismatch` before outer content-address equality.

The exact ruling regression, `test_fixed_authenticated_parents_determine_one_reported_energy_projection`, constructs fixed authenticated parents, proves deterministic projection, fully reseals a changed child/source/artifact/issuance, and confirms the named relation refusal. The registry wording now records the producer-owned derivation. The existing CLI already reaches the changed source producer, so it required no edit.

## Verification notes

Red evidence was captured before implementation: the exact ruling regression exited 1 with `AttributeError` because `build_reported_phase_energy_projection` did not exist. V1 is the post-cure green run containing that test. V2 plus V6 show the shared loader extension did not alter the checked-in detection-floor bytes.

The full canonical suite was intentionally not run under the prompt's preflight restriction.

## Residual risk

This implementation seat used synthetic authenticated bundle parents, not live hardware or quiet-window collection.
