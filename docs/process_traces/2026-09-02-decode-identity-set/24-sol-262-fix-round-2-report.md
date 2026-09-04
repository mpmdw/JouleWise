# Sol 262 (xhigh, implementation) — fix round 2 report, custodied verbatim (scratchpad paths redacted)

Brief: file 23. Landed at `bd2cae3e`; magistrate bench corrections at `9c1dc717` (file 25 records them and the bench-executed counterfactuals).

---

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented all R2 test pins and the dictated contract paragraph; 446 tests pass and all three named mutants are killed.",
  "workspace": {
    "base_requested": "b9b55e90",
    "base_mode": "descendant",
    "head_start": "7cfd0b5916ef915d477845676c1ce1fcffd9d816",
    "head_end": "7cfd0b5916ef915d477845676c1ce1fcffd9d816",
    "upstream_end": "7cfd0b5916ef915d477845676c1ce1fcffd9d816",
    "branch": "fix/2026-09-02-decode-identity-set"
  },
  "pathspec": [
    "tests/test_analysis_inputs.py",
    "tests/test_identity_pins.py",
    "tests/test_analysis_integration.py",
    "docs/contracts/identity_pin_projection.md"
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
      "cmd": "env TMPDIR=<scratchpad>/tmp262/r2-tests PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 446 tests in 97.424s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 446 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env TMPDIR=<scratchpad>/tmp262/r2-tests PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_generator_imports_shared_core_and_registration_bytes_are_unchanged",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.000s",
          "OK",
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
      }
    },
    {
      "id": "V3",
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
    },
    {
      "id": "V4",
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
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The mandated first-use audit found four pre-existing or dictated definition-order gaps: plan tree, projection_receipt binding, consumer binding, and committed file tree.",
      "needs": "Delta re-audit adjudication; no unsanctioned contract expansion was made."
    }
  ]
}
```

## Change

### R2-A

Biting test: [tests/test_analysis_inputs.py:768](/Users/edr/code/JouleWise-wt-decode-id/tests/test_analysis_inputs.py:768).

It ports the custodied 14-step forgery, preserves the honest lineage digest, asserts the exact-cell refusal and transport `None`, then re-stamps the same forged pack and proves the drifted identity is accepted.

Counterfactual: re-executed `_frozen_consumer_identity_set` with the line-3898 comparison replaced by `if False:`.

```text
AssertionError: 'exact' != 'refused'
- exact
+ refused

----------------------------------------------------------------------
Ran 1 test in 4.176s

FAILED (failures=1)
```

### R2-B

Biting test: [tests/test_analysis_inputs.py:1031](/Users/edr/code/JouleWise-wt-decode-id/tests/test_analysis_inputs.py:1031).

The generated pack’s real gate authenticates both evidence identities, admits transport, and refuses once a same-condition exact cell is introduced. No gate mock is used.

Counterfactual: replaced the gate in memory with `lambda ...: frozenset()`.

```text
AssertionError: 'consumer_identity_set_unauthenticated' unexpectedly found in ('consumer_identity_set_unauthenticated',)

----------------------------------------------------------------------
Ran 1 test in 2.003s

FAILED (failures=1)
```

### R2-C

Biting test: [tests/test_analysis_integration.py:654](/Users/edr/code/JouleWise-wt-decode-id/tests/test_analysis_integration.py:654).

Both ratified labels explicitly map to `floor_transport_inapplicable`.

Counterfactual: re-executed `_floor_engine_reasons` with both labels routed through the `floor_row_missing` branch.

```text
(reason_code='consumer_identity_set_unauthenticated') ... FAIL
(reason_code='consumer_identity_undeclared') ... FAIL

AssertionError: Lists differ: ['floor_abs_missing', 'floor_cmp_missing', 'floor_row_missing'] != ['floor_abs_missing', 'floor_cmp_missing', 'floor_transport_inapplicable']

----------------------------------------------------------------------
Ran 1 test in 0.356s

FAILED (failures=2)
```

### R2-D

Dominance proof: [tests/test_identity_pins.py:422](/Users/edr/code/JouleWise-wt-decode-id/tests/test_identity_pins.py:422). Defensive-helper documentation: [tests/test_identity_pins.py:407](/Users/edr/code/JouleWise-wt-decode-id/tests/test_identity_pins.py:407).

Branch taken: **F-G: DOMINATED**. Two schema-validated configurations differing only in manifest reference/digest retain those fields in scientific identity and produce different hashes.

`NOT PINNED: no mutant was dictated for R2-D; the requested execution proof passed.`

### R2-E

The dictated paragraph was inserted verbatim at [identity_pin_projection.md:602](/Users/edr/code/JouleWise-wt-decode-id/docs/contracts/identity_pin_projection.md:602). The executable-evidence row did not quote the replaced prose, so it was not changed.

`NOT PINNED: no contract-text counterfactual was dictated; tests.test_docs_freshness passed in V1.`

## Verification notes

### R2-E step verification

| Step | Production proof |
|---|---|
| 1 | Every row must carry lineage; roots and 64-hex digests must each be singular: [inputs.py:3870–3895](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:3870) |
| 2 | Root resolves and committed-tree digest must equal lineage digest: [inputs.py:3897–3899](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:3897) |
| 3 | Plan tree, frozen projection, and exact `path`/`sha256` freeze reference: [inputs.py:3900–3921](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:3900) |
| 4 | U8 bytes, sidecar, PASS receipt, singleton evidence row, namespace/status, and projection binding: [inputs.py:3922–3966](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:3922) |
| 5 | Frozen receipt bytes, sidecar, kind, and PASS status: [inputs.py:3967–3993](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:3967) |
| 6 | Unique family-bound receipt unit and matching projection unit/config-set digest: [inputs.py:3994–4016](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:3994) |
| 7 | Inventory byte digest and JSON-object parsing: [inputs.py:4017–4031](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:4017) |
| 8 | Nonempty re-derived identity set and folded config-set digest: [inputs.py:4032–4038](/Users/edr/code/JouleWise-wt-decode-id/joulewise/analysis_engine/inputs.py:4032) |

Caught parsing/validation failures return the empty authenticated-set sentinel at lines 4039–4048. That sentinel maps to `consumer_identity_set_unauthenticated` at lines 4082–4087. Membership and legacy multi-identity failures map to `consumer_identity_undeclared` at lines 4088–4091.

### First-use table

Lines refer to `docs/contracts/identity_pin_projection.md`.

| Noun phrase | First use | Defined/built | Result |
|---|---:|---:|---|
| pack root | 440 (`pack_root`) | 34–35 | OK |
| pack digest | 570 | 569–570 | OK |
| committed file tree | 604 | missing | **FIRST-USE-GAP** |
| plan tree | 34 (`plan_tree.json`) | 178–211 | **FIRST-USE-GAP** |
| freeze-receipt reference | 604 | 604 | OK |
| U8 freeze receipt | 568 | 565–568 | OK |
| sidecar | 172 | 172–174 | OK |
| evidence row | 567–568 | 567–568 | OK |
| `projection_receipt` binding | 181 | 192–193 | **FIRST-USE-GAP** |
| frozen identity receipt | 588 | 488–495 | OK |
| receipt unit | 589 | 77–82, 488–495 | OK |
| consumer binding | 200 (`consumer_bindings`) | 203–204 | **FIRST-USE-GAP** |
| condition family | 575 | 574–579 | OK |
| projection unit | 604 | 191–201, 300–302 | OK |
| `config_set_sha256` | 110 | 109–111, 357–370 | OK |
| inventoried config file | 604 | 112–115, 451–452 | OK |
| scientific identity | 104 | 104–108 | OK |
| frozen set | 594–595 | 589–592 | OK |
| successor launch lineage | 583–584 | 569–570 | OK |
| legacy evidence | 598 | 598–600 | OK |

Suite tail:

```text
----------------------------------------------------------------------
Ran 446 tests in 97.424s

OK (skipped=1)
```

D-165 invariant:

```text
Ran 1 test in 0.000s

OK
1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b
```

## Residual risk

The four `FIRST-USE-GAP` rows were reported without expanding or rewriting the dictated paragraph. No production, live-hardware, quiet-machine, commit, or merge action was performed.