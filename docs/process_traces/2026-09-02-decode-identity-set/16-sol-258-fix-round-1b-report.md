```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented distinct production refusal labels for unauthenticated frozen identity sets and undeclared consumer identities.",
  "workspace": {
    "base_requested": "3ac6cffb",
    "base_mode": "exact",
    "head_start": "3ac6cffb1541bd9f2e8b7cfee2aa4ead8ca0474a",
    "head_end": "3ac6cffb1541bd9f2e8b7cfee2aa4ead8ca0474a",
    "upstream_end": "3ac6cffb1541bd9f2e8b7cfee2aa4ead8ca0474a",
    "branch": "fix/2026-09-02-decode-identity-set"
  },
  "pathspec": [
    "docs/contracts/identity_pin_projection.md",
    "docs/specs/c027/p2-039_floor_artifact.md",
    "joulewise/analysis_engine/__init__.py",
    "joulewise/analysis_engine/inputs.py",
    "joulewise/detection_floor.py",
    "tests/test_analysis_inputs.py",
    "tests/test_detection_floor.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env TMPDIR=<scratchpad>/tmp258/decode-id-r1b-pre python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_unauthenticated_frozen_identity_set_with_named_reason tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_identity_outside_authenticated_set_with_named_reason tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_legacy_multi_identity_without_declaration_with_named_reason tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_accepts_same_authenticated_fixture_without_receipt_perturbation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "('consumer_term_unknown',) != ('consumer_identity_set_unauthenticated',)",
          "('consumer_term_unknown',) != ('consumer_identity_undeclared',)",
          "('consumer_term_unknown',) != ('consumer_identity_undeclared',)",
          "Ran 4 tests in 9.729s",
          "FAILED (failures=3)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=3\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env TMPDIR=<scratchpad>/tmp258/decode-id-r1b-post python3 -m unittest tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_unauthenticated_frozen_identity_set_with_named_reason tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_identity_outside_authenticated_set_with_named_reason tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_refuses_legacy_multi_identity_without_declaration_with_named_reason tests.test_analysis_inputs.FrozenConsumerIdentitySetTests.test_production_accepts_same_authenticated_fixture_without_receipt_perturbation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 9.198s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env TMPDIR=<scratchpad>/tmp258/decode-id-r1b-suite python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_d165_dominance_closeout tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 327 tests in 36.739s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 327 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs/contracts/identity_pin_projection.md | 14 ++",
          "docs/specs/c027/p2-039_floor_artifact.md | 2 +",
          "joulewise/analysis_engine/__init__.py | 35 ++++-",
          "joulewise/analysis_engine/inputs.py | 55 +++++---",
          "joulewise/detection_floor.py | 2 +",
          "tests/test_analysis_inputs.py | 204 ++++++++++++++++++++++++++++++",
          "tests/test_detection_floor.py | 2 +",
          "7 files changed, 290 insertions(+), 24 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "7 files changed"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n 'return frozenset\\(\\)|declared_consumer_identities|consumer_identity_set_unauthenticated' joulewise/analysis_engine/inputs.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "3878-4048: 21 return frozenset() authentication exits",
          "4082: declared_consumer_identities = _frozen_consumer_identity_set(",
          "4085: if declared_consumer_identities is not None:",
          "4086: if not declared_consumer_identities:",
          "4087: return (\"consumer_identity_set_unauthenticated\",)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "consumer_identity_set_unauthenticated"
      }
    },
    {
      "id": "V6",
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
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff -- configs/campaigns/d117_contrast_v5/generate_configs.py docs/paper/draft-v1.md",
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
  "flags": []
}
```

## Change

R-M1: Added exactly the two ruled codes to the governed census in [detection_floor.py](/Users/edr/code/JouleWise-wt-decode-id/joulewise/detection_floor.py:293).

R-M2: Extended the exact-set census test in [test_detection_floor.py](/Users/edr/code/JouleWise-wt-decode-id/tests/test_detection_floor.py:3695) and the specification list in [p2-039_floor_artifact.md](/Users/edr/code/JouleWise-wt-decode-id/docs/specs/c027/p2-039_floor_artifact.md:610). The additive-compatibility sentence and `TRANSPORT_RULE_ID` remain unchanged.

R-M3: Added `_floor_request_or_refusal`, returning `FloorRequest | tuple[str, ...]`, in [inputs.py](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:4051). An empty tuple represents every historical generic refusal; only the two identity cases carry named tuples. The public wrapper at line 4193 preserves `FloorRequest | None`. The production caller consumes the tuple and constructs the refused resolution in [__init__.py](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/__init__.py:380). This was the smallest shape that preserved the test seam and existing generic behavior.

Both new codes intentionally follow `_floor_engine_reasons`’ default branch to `floor_transport_inapplicable` at [__init__.py](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/__init__.py:207); no new engine reason was added.

R-M4: Added the three RED-first refusal tests and authenticated counterfactual in [test_analysis_inputs.py](/Users/edr/code/JouleWise-wt-decode-id/tests/test_analysis_inputs.py:633). They call `_resolve_contrast_floor` with `request_factory=None`. The assertion around line 2188 of `test_analysis_claims.py` was left unchanged because its fixture genuinely exercises an uncalibrated idle-drift consumer term, not identity authentication.

R-M5: Added the replicable mechanism-and-label paragraph in [identity_pin_projection.md](/Users/edr/code/JouleWise-wt-decode-id/docs/contracts/identity_pin_projection.md:602) and its executable-evidence row at line 968.

## Verification notes

Pre-production RED tails for R-M4(a)–(c):

```text
FAIL: test_production_refuses_unauthenticated_frozen_identity_set_with_named_reason
AssertionError: ('consumer_term_unknown',) != ('consumer_identity_set_unauthenticated',)

FAIL: test_production_refuses_identity_outside_authenticated_set_with_named_reason
AssertionError: ('consumer_term_unknown',) != ('consumer_identity_undeclared',)

FAIL: test_production_refuses_legacy_multi_identity_without_declaration_with_named_reason
AssertionError: ('consumer_term_unknown',) != ('consumer_identity_undeclared',)

Ran 4 tests in 9.729s
FAILED (failures=3)
```

The fourth, unperturbed control passed during that same RED run. The required named suite subsequently passed, including the dominance-digest pin and documentation-freshness checks.