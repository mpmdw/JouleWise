```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Clauses 1-4 are implemented with a total code-owned exact-set derivation, shared receipt-id authority, RED/GREEN acceptance, three mutation kills, and byte-unchanged 112-path proof.",
  "workspace": {
    "base_requested": "9ada1e34",
    "base_mode": "exact",
    "head_start": "9ada1e34bc147c35abef21ca5f68277f86abbd70",
    "head_end": "9ada1e34bc147c35abef21ca5f68277f86abbd70",
    "upstream_end": "9ada1e34bc147c35abef21ca5f68277f86abbd70",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "configs/arm_readiness/d117_row_registry_v2.json",
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/15-sol-rescope-round-3-report.md",
    "joulewise/arm_readiness.py",
    "tests/test_arm_readiness_evidence.py",
    "tests/test_arm_readiness_lifecycle.py",
    "tests/test_arm_readiness_schemas.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/14-sol-rescope-round-2-report.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_derivation_is_total_across_id_and_placeholder_state",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 0.003s", "FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_derivation_is_total_across_id_and_placeholder_state",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.003s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V3-M1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_derivation_is_total_across_id_and_placeholder_state",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 0.003s", "FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)$"}
    },
    {
      "id": "V3-M2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_derivation_is_total_across_id_and_placeholder_state",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 0.003s", "FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=2\\)$"}
    },
    {
      "id": "V3-M3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_derivation_is_total_across_id_and_placeholder_state",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 0.003s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 0.090s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 37 tests.*\\nOK$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_evidence",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 12 tests in 1.497s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 12 tests.*\\nOK$"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_lifecycle",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 67 tests in 71.763s", "OK (skipped=4)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 67 tests.*\\nOK \\(skipped=4\\)$"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_family_marker",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 29 tests in 5.807s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 29 tests.*\\nOK$"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_receipt_histsem",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 65 tests in 1869.636s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 65 tests.*\\nOK \\(skipped=1\\)$"}
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "cmp <(git show HEAD:configs/arm_readiness/d117_row_registry_v2.json | sed -n '212,325p') <(sed -n '212,325p' configs/arm_readiness/d117_row_registry_v2.json)",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V11",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/15-sol-rescope-round-3-report.md\"); s=p.read_text(encoding=\"utf-8\"); end=s.index(\"\\n```\\n\",8); raw=s[8:end]; json.loads(raw); assert len(raw.encode()) <= 8192; print(\"report_contract=valid\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["report_contract=valid"]},
      "expected": {"exit_code": 0, "tail_regex": "^report_contract=valid$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The implementation evidence and clause map are ready for the magistrate's lead-owned decision-log adoption step.",
      "needs": "Magistrate reviews this report and writes the new decision entry; this seat did not touch docs/decision_log.md."
    }
  ]
}
```

## Change

The retired output-manifest digest, dict return, fixed freeze ordinal, and registry-id/`Mapping` applicability gate are gone. The lifecycle candidate now equals a tuple derived from one code-owned eight-family specification and exact pack/receipt maps. The tracked lifecycle schema is `.v2`; its three receipt IDs are `freeze-0004`; family marker structure validates receipt-internal path/ordinal consistency, while family replay binds each profile to the registry-selected receipt ID. Lifecycle and evidence fixtures now call the production derivation.

D-151 condition 1 is byte-unchanged: the baseline and working-tree serialized lines 212-325 compare equal, both SHA-256 `6f2a8b1076ad1cde42846bb3108463611089d896c83745947cf6a8a7ced2c4ce`; parsed count remains 112, sorted and unique.

## Clause map

| Clause / proposition | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| 1 — eight closed families live in code | `joulewise/arm_readiness.py:638` | `tests/test_arm_readiness_schemas.py:499` | Delete or duplicate one family tuple; the production derivation refuses or differs from the tracked 112. |
| 1 — derivation returns paths, not a digest-pinned manifest dict | `joulewise/arm_readiness.py:1786` | `tests/test_arm_readiness_lifecycle.py:141`; `tests/test_arm_readiness_evidence.py:54` | Restore the manifest dict/output digest; fixture equality/type use fails. |
| 2 — lifecycle schema alone advances to `.v2` | `joulewise/arm_readiness.py:69`; `configs/arm_readiness/d117_row_registry_v2.json:516` | `tests/test_arm_readiness_schemas.py:481` | Restore either `.v1`; tracked registry load refuses or schema assertion fails. |
| 2 — exact three-profile receipt-id map | `joulewise/arm_readiness.py:630`; `configs/arm_readiness/d117_row_registry_v2.json:532` | `tests/test_arm_readiness_schemas.py:491` | Remove/rename a key or change an ID; exact-key/derivation equality refuses. |
| 2 — family replay uses the same profile-selected receipt ID | `joulewise/arm_readiness.py:11392`; `joulewise/arm_readiness.py:11423` | `tests/test_arm_readiness_lifecycle.py:513` | Restore `freeze-0004` at replay; the test's ALPHA=`freeze-0005` mismatch is no longer caught. |
| 3 — resolved/resolved derives 112; reserved/reserved derives `()` | `joulewise/arm_readiness.py:1706`; `joulewise/arm_readiness.py:1765` | `tests/test_arm_readiness_schemas.py:488`; `tests/test_arm_readiness_evidence.py:536` | Remove either state; resolved count/equality or placeholder validation fails. |
| 3 — mixed state refuses with stable token | `joulewise/arm_readiness.py:1708` | `tests/test_arm_readiness_schemas.py:589` | Delete the mixed-state branch; the stable mixed-state diagnostic changes. |
| 3 — candidate equality is unconditional and reports extra/missing | `joulewise/arm_readiness.py:2012` | `tests/test_arm_readiness_schemas.py:549` | Gate equality on id/resolvedness or tautologize it; the ruled acceptance method goes RED. |
| 4 — one acceptance method, two named subtests | `tests/test_arm_readiness_schemas.py:549` | same method at `:562` and `:579` | Fresh-id extra or reserved non-empty candidate is admitted. |

## Verification notes

Initial RED, before production edits:

```text
[fresh registry identity] AssertionError: ArmReadinessError not raised
[fully reserved derivation inputs] readiness_unknown_key != readiness_row_registry_mismatch
Ran 1 test in 0.003s
FAILED (failures=2)
```

Three temporary mutants were applied one at a time and fully reverted:

```text
M1 restore `isinstance(pack_ids, Mapping) and registry_id == ...` gate:
  [fresh registry identity] ArmReadinessError not raised
  [fully reserved derivation inputs] ArmReadinessError not raised
  FAILED (failures=2)
M2 replace equality predicate with `False and ...`:
  [fresh registry identity] ArmReadinessError not raised
  [fully reserved derivation inputs] ArmReadinessError not raised
  FAILED (failures=2)
M3 replace unconditional equality with `if derived_paths and ...`:
  [fully reserved derivation inputs] ArmReadinessError not raised
  FAILED (failures=1)
```

The full repository suite was not run because the binding preflight restricted test selection to the three named modules and directly owned modules, sequentially. The attempted process-health inspection during the long receipt-histsem run was sandbox-refused (`ps: operation not permitted`) and did not affect verification.
