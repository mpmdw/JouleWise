```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Closed S1, N1, S3 and mechanically repinned S2; all 211 named-module tests passed.",
  "workspace": {
    "base_requested": "bb7090e2",
    "base_mode": "exact",
    "head_start": "bb7090e2b8d4cfe30effbfb7e89cef802277d448",
    "head_end": "bb7090e2b8d4cfe30effbfb7e89cef802277d448",
    "upstream_end": "bb7090e2b8d4cfe30effbfb7e89cef802277d448",
    "branch": "fix/2026-09-09-night-gate-stub-chain"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "tests/test_night_gate.py",
    "docs/contracts/pack_night_go_receipt.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_night_gate tests.test_run_night tests.test_docs_freshness tests.test_gen_state > /tmp/night-gate-stub-chain-fix-round-1-tests.log 2>&1\nnight_gate_test_rc=$?\nprintf '\\nrc=%s\\n' \"$night_gate_test_rc\" >> /tmp/night-gate-stub-chain-fix-round-1-tests.log\ntail -n 6 /tmp/night-gate-stub-chain-fix-round-1-tests.log\nexit \"$night_gate_test_rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 211 tests in 10.164s",
          "",
          "OK",
          "",
          "rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 211 tests in [0-9.]+s\\n\\nOK\\n\\nrc=0"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
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
  "flags": []
}
```

## Change

- **S1:** Stub C5 detail now matches the dictated sentence exactly. `assertEqual` pins both that sentence and the byte-identical non-stub sentence.
- **N1:** Stub measured data retains both plan chain paths, null digests and the stub marker. Both paths are asserted; evidence remains unchanged without chain citations.
- **S3:** Added the plain `FakeProbeSource(chain_digest="0" * 64)` regression, asserting `REHEARSAL_ONLY`, no refusal and neither chain path read. Counterfactual: an implementation that reads the chain when it exists would fail this test with `night_chain_digest_mismatch`.
- **S2:** Repinned after all code/test edits, using symbol definitions and original content from `83ab38ed` for bare references. **139 total occurrences: 63 repinned, 76 unchanged, 0 frozen, 0 unresolved.** All eleven known-displaced pins are resolved.
- **S4, N2, N3, N4:** No changes.

Repin table groups repeated occurrences of the same target. Paths: **G** = `joulewise/night_gate.py`; **TG** = `tests/test_night_gate.py`; **TR** = `tests/test_run_night.py`.

| File | Old → new | Symbol or content |
|---|---|---|
| G | 1103–1113 → 1117–1127 | Conditional `night_refused_class_unbuilt` fence |
| G | 1357 → 1371 | `validate_receipt` |
| TG | 402 → 414 | `test_a_green_diagnostic_plan_yields_a_valid_go_receipt` |
| TG | 420 → 481 | `test_a_transaction_plan_is_refused_until_stage_three_exists` |
| TG | 943 → 1004 | `test_valid_v3_pack_without_driver_arguments_lifts_unbuilt_fence` |
| TR | 1865 → 1910 | `test_driver_self_authors_arm_before_go_and_pins_all_eight_flags` |
| TR | 1929 → 1974 | `test_gate_reauthenticates_c1_and_c2_despite_forged_driver_pass_rows` |
| TR | 1969 → 2014 | `test_pack_standard_refusal_receipt_preserves_each_actual_cause` |
| TR | 2000 → 2045 | `test_gate_checks_authorization_fields_and_confirmation_bytes` |
| TR | 2030 → 2075 | `test_no_go_on_arm_refusal` |
| TR | 2048 → 2093 | `test_pack_digest_mismatch_at_preparation_and_go_refuses_without_go` |
| TR | 2065 → 2110 | `test_each_plan_record_digest_and_pinned_plan_swap_refuse` |
| TR | 2077 → 2122 | `test_selected_old_arm_and_higher_receipt_and_consumption_refuse` |
| TR | 2090 → 2135 | `test_second_manifest_missing_symlink_and_attested_digest_refuse` |
| TR | 2113 → 2158 | `test_machine_refusal_and_refused_receipt_never_publish_go` |
| TR | 2124 → 2169 | `test_pack_root_must_match_the_written_arm_root_and_digest` |
| TR | 2132 → 2177 | `test_t0_inventory_cannot_omit_add_or_substitute_author_or_capture_bytes` |
| TR | 2156 → 2201 | `PackNightProducerTests.test_go_producer_enforces_two_by_two_purpose_window_table` |
| TR | 2197 → 2242 | `test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule` |
| TR | 2261 → 2306 | `test_pack_gate_requires_absolute_strict_custody_root` |

Exact acceptance log tail:

```text
----------------------------------------------------------------------
Ran 211 tests in 10.164s

OK

rc=0
```

`git diff --check`: empty output, rc=0. No commit made. Next step: lead final diff review.