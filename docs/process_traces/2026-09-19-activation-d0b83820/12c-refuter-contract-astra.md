```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "C1-C4 satisfied: no contract findings; 16 focused tests and independent contract probes passed; worktree unchanged.",
  "workspace": {
    "base_requested": "2f79e633",
    "base_mode": "exact",
    "head_start": "ff788ef7f604ef53b6035780ce81c2159208cb6f",
    "head_end": "ff788ef7f604ef53b6035780ce81c2159208cb6f",
    "upstream_end": "ff788ef7f604ef53b6035780ce81c2159208cb6f",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 0,
      "nit": 0
    },
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_calibration_bracketing.CalibrationBracketingTests.test_live_issued_anchor_artifact_and_head_pin_ordering_and_schema tests.test_calibration_ledger.CalibrationLedgerTests.test_non_genesis_cutoff_authenticates_under_advanced_committed_pin tests.test_calibration_ledger.CalibrationLedgerTests.test_wrong_non_genesis_cutoff_digest_refuses_on_authenticated_chain tests.test_calibration_ledger.CalibrationLedgerTests.test_committed_pin_below_cutoff_refuses_even_with_matching_physical_head tests.test_calibration_ledger.CalibrationLedgerTests.test_proper_prefix_of_pinned_head_refuses_as_rollback tests.test_calibration_ledger.CalibrationLedgerTests.test_unpinned_physical_extension_refuses_stale_head tests.test_calibration_ledger.CalibrationLedgerTests.test_bracket_session_open_requires_exact_committed_physical_head tests.test_campaign_generator_core tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_external_pinned_input_drift_is_checked_in_derivation_mode tests.test_arm_readiness_evidence_packauth.ProjectedPackAuthenticationTests.test_preserve_echo_accepts_science_row_tamper_but_cannot_set_generator_pass > /tmp/refc-contract-focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 16 tests in 19.100s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 16 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/refc-contract-probes.py > /tmp/refc-contract-probes.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LOADER extension head=8 baseline=4 refusals=()",
          "LOADER wrong_digest head=8 baseline=4 refusals=('calibration_ledger_baseline_missing',)",
          "LOADER pin_only_rollback head=8 baseline=8 pin=4 refusals=('calibration_ledger_baseline_missing', 'calibration_ledger_head_mismatch')",
          "LOADER ledger_and_pin_rollback head=4 baseline=8 pin=4 refusals=('calibration_ledger_baseline_missing',)",
          "NON_HEAD_DRIFT acceptance: pinned input drifted: configs/calibration/calibration_acceptance_d079_v2_n17_r6.json",
          "NON_HEAD_DRIFT policy: pinned input drifted: configs/campaign_policies/quiet_mac_p2_production.json",
          "NON_HEAD_DRIFT neg8: pinned input drifted: configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json",
          "NON_HEAD_DRIFT p256: p256 prompt artifact bytes drifted",
          "CONTRACT_PROBES_PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CONTRACT_PROBES_PASS"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --stat 2f79e633 HEAD && git diff --check 2f79e633 HEAD && git status --short --branch && git rev-parse HEAD refs/remotes/origin/fix/2026-09-19-head-pin-test-drift",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " 5 files changed, 194 insertions(+), 18 deletions(-)",
          "## HEAD (no branch)",
          "ff788ef7f604ef53b6035780ce81c2159208cb6f",
          "ff788ef7f604ef53b6035780ce81c2159208cb6f"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Contract-lens review only. X1-X4 are assigned to the execution lens; full-module runs, quick tier, its complete mutation matrix, and its same-signature census were not performed here. No live ledger ancestry or hardware validation is claimed.",
      "needs": "Lead combines this report with the execution-lens results and performs final verification."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Unfixtured production generation still refuses the advanced head-file bytes, as required by ruling 07a. GENERATOR-HEAD-FILE-BYTE-PIN-01 remains deferred.",
      "needs": ""
    }
  ]
}
```

## Findings

None. The diff contains exactly five test files. Production, generators, contracts, frozen packs, and the committed pin remain unchanged; the pin is still **176 / `0f7609ae…`**.

**C1 — Satisfied.** [The rewritten test](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_calibration_bracketing.py:597) asserts schema equality, `cutoff.sequence <= pin.sequence`, digest format, and digest equality only at equal sequences. Its name says ordering/schema; its docstring explicitly says the loader enforces digest-in-chain. The **76 / `08456d50…`** literals now apply to the explicitly named r6 artifact. Independent probes accepted sequence 999 with a fresh digest and rejected a behind-cutoff pin, equal-sequence wrong digest, and wrong schema.

**C2 — Satisfied.** [The regressions](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_calibration_ledger.py:675) call the production loader with committed-pin and custody verification enabled. Observed:

| Fixture state | Refusal codes |
|---|---|
| Baseline 4, physical/committed head 8 | None |
| Wrong baseline digest | `calibration_ledger_baseline_missing` |
| Baseline 8, physical head 8, committed pin 4 | `calibration_ledger_baseline_missing`, `calibration_ledger_head_mismatch` |
| Baseline 8, shortened physical head and committed pin both 4 | Only `calibration_ledger_baseline_missing` |

The full-chain case isolates the explicit `> pinned_sequence` guard. The shortened case eliminates physical-head mismatch and refuses through baseline membership checking.

**C3 — Satisfied.** [The fixture](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_campaign_generator_core.py:123) intercepts only `sha256_file(REPO_ROOT / LEDGER_HEAD_REL)` for ALPHA/BETA; every other path delegates to the original function. Its comment names **GENERATOR-HEAD-FILE-BYTE-PIN-01**.

The bytes exactly match `git show a816036f4ea278fcc746b1220896b4b6bd084855:configs/calibration/calibration_ledger_head.json`, the provenance recorded by the seat. Independently recomputed SHA-256:

`6bbe26258165bbd11ca996324a5862c2e6e34faae7999b6c06f5e12f27ac2902`

Counterfactuals executed in `/tmp`: append a newline to each other input without updating its expected hash. Acceptance, policy, and neg8 each refused through the live ALPHA generator’s drift loop, naming the changed path. The legacy p256 prompt refused earlier with `p256 prompt artifact bytes drifted`; p256 is not an input of the v5 core cases. None was masked.

**C4 — No fence weakened.** These tests still prove the relevant fences and passed in V1:

| Fence | Test |
|---|---|
| Regeneration rejects input drift | [`test_external_pinned_input_drift_is_checked_in_derivation_mode`](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_arm_readiness_evidence_packauth.py:545); now requires the acceptance path in the refusal |
| Preserve remains echo, unable to establish generator pass | [`test_preserve_echo_accepts_science_row_tamper_but_cannot_set_generator_pass`](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_arm_readiness_evidence_packauth.py:513) |
| D-109 baseline anti-rollback | [`test_committed_pin_below_cutoff_refuses_even_with_matching_physical_head`](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_calibration_ledger.py:708) |
| Physical rollback | [`test_proper_prefix_of_pinned_head_refuses_as_rollback`](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_calibration_ledger.py:563) |
| §0.4 head-equals-pin | [`test_unpinned_physical_extension_refuses_stale_head`](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_calibration_ledger.py:573) and [`test_bracket_session_open_requires_exact_committed_physical_head`](/Users/edr/code/JouleWise-wt-refc-d0b83820/tests/test_calibration_ledger.py:921) |

## Residual risk

The real 76→176 ancestry was not checked. These are committed-byte and synthetic-ledger proofs.

Unfixtured production generation still refuses `configs/calibration/calibration_ledger_head.json`; I reproduced that refusal. This is the deferred issue accepted by ruling 07a.

X1–X4 belong to the execution lens. Next step: combine that seat’s evidence with this clean contract review at **`ff788ef7`**.