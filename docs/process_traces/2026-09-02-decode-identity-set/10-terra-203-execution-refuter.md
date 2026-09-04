```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "Baseline and live temporary-pack checks pass; the required production mutation census is blocked by WRITE_SCOPE: [].",
  "workspace": {
    "base_requested": "1a608089",
    "base_mode": "exact",
    "head_start": "1a60808974dea46c54e11dc3fc6900ab6230644d",
    "head_end": "1a60808974dea46c54e11dc3fc6900ab6230644d",
    "upstream_end": null,
    "branch": "fix/2026-09-02-decode-identity-set"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Required production-site mutation census not authorized",
        "detail": "Every M1–M11 mutation requires a write to one of three production files, while WRITE_SCOPE is empty. No mutation was made or claimed."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Several ruled clauses have no apparent dedicated counterfactual",
        "detail": "Static test review identifies M1, M4–M6, M10, and M11 as requiring targeted tests for definitive mutation kills."
      }
    ]
  },
  "mutations": [
    {
      "id": "M1",
      "site": "configs/campaigns/d117_contrast_v5/generate_configs.py:1472-1493",
      "edit": "Derive suite_manifest_set from emitted config files rather than STAGE_SPECS/decode_prompt_index.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "No existing behavioral test necessarily distinguishes equal sane outputs; add a generator-only test that prohibits reading emitted config files while constructing the declaration."
    },
    {
      "id": "M2",
      "site": "configs/campaigns/d117_contrast_v5/generate_configs.py:1490",
      "edit": "Increment one declared_member_count.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "D117ContrastV5PackTests.test_generated_v5_pack_freezes_and_verifies"
    },
    {
      "id": "M3",
      "site": "joulewise/identity_pins.py:1597-1606",
      "edit": "Accept an emitted manifest SHA absent from declared_by_manifest.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "D117ContrastV5PackTests.test_generated_v5_pack_refuses_unlisted_decode_manifest"
    },
    {
      "id": "M4",
      "site": "joulewise/identity_pins.py:1617-1625",
      "edit": "Replace exact manifest census equality with an at-least comparison.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "No apparent existing killer; add one extra member on an already-declared manifest and require freeze refusal."
    },
    {
      "id": "M5",
      "site": "joulewise/identity_pins.py:1576-1589",
      "edit": "Disable declared common-profile equality.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "No apparent existing killer; alter only a declared common-profile field while preserving suite_manifest_set."
    },
    {
      "id": "M6",
      "site": "joulewise/identity_pins.py:1637-1645",
      "edit": "Disable distinct-identity-count equality with declared manifests.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "No apparent existing killer; patch scientific_config_identity_sha256 to collapse two manifest classes and require refusal."
    },
    {
      "id": "M7",
      "site": "joulewise/identity_pins.py:250-258",
      "edit": "M7a domain v1→v2; M7b remove sorting; M7c drop one newline separator.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "SharedDerivationTests.test_identity_unit_set_digest_uses_sorted_distinct_hashes"
    },
    {
      "id": "M8",
      "site": "joulewise/identity_pins.py:255-258",
      "edit": "Use the multi-identity digest branch for a singleton.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "SharedDerivationTests.test_single_identity_set_digest_matches_committed_v3_receipt"
    },
    {
      "id": "M9",
      "site": "joulewise/analysis_engine/inputs.py:4060-4070",
      "edit": "M9a relax subset to non-empty; M9b allow exact-cell routing for a multi-identity consumer.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "FrozenConsumerIdentitySetTests.test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell"
    },
    {
      "id": "M10",
      "site": "joulewise/identity_pins.py:1765-1785",
      "edit": "Remove the all-members-share-runtime-pins assertion.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "No apparent existing killer; patch per-member runtime derivation to disagree after declaration checks pass."
    },
    {
      "id": "M11",
      "site": "joulewise/identity_pins.py:2381",
      "edit": "Remove verification's re-derivation/R-3 mirror while retaining freeze checks.",
      "outcome": "NOT_RUN (scope blocked)",
      "planned_killer": "No apparent existing killer; construct and commit a re-bound historical frozen receipt with a declared-census mismatch, then require verify refusal."
    }
  ],
  "same_signature": "n/a (first round)",
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_identity_pins tests.test_analysis_inputs tests.test_d165_dominance_closeout tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 168 tests in 21.983s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 168 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_v5_pack_freezes_and_verifies",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.894s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "Custom fixture-derived TMPDIR harness: generate _v5 GAMMA, freeze, commit fixture, verify, and print unit digest/identity/census.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "A/decode: distinct_identity_count=8, manifest_census=[4,4,2,2,2,2,2,2]",
          "B/decode: distinct_identity_count=8, manifest_census=[4,4,2,2,2,2,2,2]",
          "A/prefill_p512 and B/prefill_p512: distinct_identity_count=1",
          "frozen=PASS; verified=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "distinct_identity_count=8.*frozen=PASS.*verified=PASS"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --porcelain && git diff --check",
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
      "text": "WRITE_SCOPE: [] prohibits every required production mutation; no files were changed.",
      "needs": "Authorize temporary writes and restoration for configs/campaigns/d117_contrast_v5/generate_configs.py, joulewise/identity_pins.py, and joulewise/analysis_engine/inputs.py."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The requested seat report at scratchpad/192-report-for-refuters.md was absent; filename and content were not found under the supplied scratchpad.",
      "needs": "Provide the report at an available path to complete the six-counterfactual subset comparison."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "configs/campaigns/d117_contrast_v5/generate_configs.py",
      "joulewise/identity_pins.py",
      "joulewise/analysis_engine/inputs.py"
    ],
    "reason": "M1–M11 explicitly require production-file mutations, followed by restoration after each named-suite run.",
    "blocked_work": "Mutation-kill census and definitive KILLED_BY/SURVIVED outcomes.",
    "minimal_change": "Permit reversible edits only to these three files; leave tests and repository reports unchanged."
  }
}
```

## Findings

- F1 blocker: the empty write scope prevents the required production mutations. Tree is clean.

- F2 should-fix: M1, M4–M6, M10, and M11 need the targeted tests named in the envelope before their required mutation kills can be demonstrated.

## Residual risk

The seat’s six counterfactuals could not be compared because its requested report file was unavailable.