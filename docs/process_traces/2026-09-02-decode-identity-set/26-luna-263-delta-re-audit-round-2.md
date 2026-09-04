# luna 263 (xhigh, read-only, detached at `629a333e`) — delta re-audit of fix round 2, custodied verbatim (scratchpad paths redacted)

Brief: `<scratchpad>/decode-delta-3.md`, reproduced as file 26a. Disposition: file 27.

---

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "Round 2 cures bind the forged pack to its launch digest, exercise the real frozen gate, pin the ruled mapping, and produce no same-signature defect.",
  "workspace": {
    "base_requested": "7cfd0b59",
    "base_mode": "exact",
    "head_start": "7cfd0b5916ef915d477845676c1ce1fcffd9d816",
    "head_end": "629a333edfdc2870b6a391b9cab9c8082b428a65",
    "upstream_end": null,
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
      "kind": "suite",
      "cmd": "TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 446 tests in 89.325s",
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
      "cmd": "TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_generator_imports_shared_core_and_registration_bytes_are_unchanged",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.000s",
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
      "kind": "inspection",
      "cmd": "python3 -c '... sha256(frozen_json_bytes(g.dominance_criterion_registration())) ...'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "in-memory exec of R2-A if False mutant",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'exact' != 'refused'",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "AssertionError: 'exact' != 'refused'"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "in-memory exec of unconditional frozen-gate return frozenset() mutant",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'consumer_identity_set_unauthenticated' unexpectedly found",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "consumer_identity_set_unauthenticated.*FAILED"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "in-memory exec of both identity-label-to-floor_row_missing mutant",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.326s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    }
  ],
  "flags": []
}
```

## Findings

None.

### A1 — R2-A

The fixture matches `20a-coldF-forgery_probe.py.txt`:

- Mutates `A/decode` config bytes once.
- Updates receipt inventory digest, receipt/config-set digest, projection/config-set digest, projection inventory digest.
- Re-renders the identity receipt and sidecar.
- Updates and re-renders the U8 freeze receipt and sidecar.
- Updates both plan-tree bindings and commits.
- Preserves the honest lineage digest.
- `_generated_exact_case()` re-reads the forged inventory; the test asserts the drift tag count is exactly `1`.

The exact-cell production seam is used through `_production_floor_resolution(..., request_factory=None)`; the transport case is checked with `floor_request_for_evidence(...) is None`.

Counterfactual, `inputs.py:3898` replaced in memory with `if False:`:

```text
AssertionError: 'exact' != 'refused'
- exact
+ refused

----------------------------------------------------------------------
Ran 1 test in 3.801s

FAILED (failures=1)
```

The re-stamped control is present and accepts the drifted identity. A control variant with `"0" * 64` instead of the forged digest failed at the control assertion:

```text
AssertionError: 'refused' != 'exact'
- refused
+ exact

----------------------------------------------------------------------
Ran 1 test in 7.676s

FAILED (failures=1)
```

Additional mutants:

- Compare the committed tree to `pack_roots` instead of `pack_hashes`: KILLED.

```text
AssertionError: 'c6d662437abccc610fb5fc825c4cbd31a0b6e2e2297002bef8b5900132bfabd8' not found in frozenset()
```

- Remove `resolve(strict=True)`: SURVIVES on this valid-path fixture.

```text
Ran 1 test in 7.670s

OK
```

The survivor is limited to missing-root coverage; it does not weaken the named forgery cure.

### A2 — R2-B

The new test contains no patch of `_frozen_consumer_identity_set`. It reaches the real gate, obtains a transport request with the expected `c...` family digest, then adds a same-condition exact cell and confirms the exact-cell route is skipped.

Gate mutant, unconditional `return frozenset()`:

```text
AssertionError: 'consumer_identity_set_unauthenticated' unexpectedly found in ('consumer_identity_set_unauthenticated',)

----------------------------------------------------------------------
Ran 1 test in 1.715s

FAILED (failures=1)
```

The mocked sibling additionally tests the outside-subset refusal (`refused` with only the first identity declared) and asserts scientific identity is not recomputed via a mock side effect. The new real-gate test does not repeat those assertions; the outside-subset behavior is covered by the named label test.

### A3 — R2-C

Both labels map to `floor_transport_inapplicable`. R-M3 states:

> “`_floor_engine_reasons` ... maps unknown codes to `floor_transport_inapplicable` — decide whether the two new codes should map there (default: yes, they are transport-inapplicable) ... do not add a new engine reason.”

Mapping either label to `floor_row_missing` was killed; both subtests failed with the expected list mismatch:

```text
Ran 1 test in 0.326s

FAILED (failures=2)
```

### A4 — R2-D

The two proof tests pass:

```text
Ran 2 tests in 0.001s

OK
```

The dominance argument is sound. The call at `identity_pins.py:1701` is inside `if suite_declaration is not None` at line 1676.

With no suite declaration:

- `declared_by_manifest`, `manifest_counts`, and `manifest_scientific_hashes` remain empty.
- `scientific_hashes` still collects identities.
- The `elif` at line 1713 requires exactly one scientific identity.
- The cardinality helper is not called.

When the helper is reachable, the preceding checks enforce census equality and one identity per manifest class. `scientific_config_identity()` retains both `suite_manifest_ref` and `suite_manifest_sha256`, so distinct manifest bindings produce distinct scientific identities. No `F-G: REACHABLE` path exists.

### A5 — Round-1/1b regressions

Under the original generic-refusal counterfactual:

- Unauthenticated frozen-set label test — KILLED.
- Outside-authenticated-set label test — KILLED.
- Legacy multi-identity label test — KILLED.
- Authenticated control — SURVIVES, as expected.
- F-D tampered-pack test with immediate `return frozenset()` — KILLED.

Exact combined tail:

```text
Ran 4 tests in 8.466s

FAILED (failures=3)
```

F-D tail:

```text
AssertionError: unexpectedly None

----------------------------------------------------------------------
Ran 1 test in 1.706s

FAILED (failures=1)
```

## B1 — numbered-step audit

| Step | Grade | Evidence |
|---|---|---|
| 1 | PROVEN | `inputs.py:3870–3895` requires lineage on every row and one root/digest pair. |
| 2 | PROVEN | `inputs.py:3897–3899`; `arm_readiness.py:2750–2874`. Untracked, missing, modified, mode-different, or byte-different files fail. |
| 3 | PROVEN | `inputs.py:3900–3921` validates the plan tree, frozen state, and exact freeze reference keys. |
| 4 | PROVEN | `inputs.py:3922–3966` authenticates U8 bytes, sidecar, PASS status, and exactly one U11 binding. |
| 5 | PROVEN | `inputs.py:3967–3993` authenticates the frozen identity receipt, sidecar, kind, and PASS status. |
| 6 | PROVEN | `inputs.py:3994–4016` requires one matching receipt unit and one projection unit with equal config-set digest. |
| 7 | PROVEN | `inputs.py:4017–4031` hashes every inventoried file and parses it as an object. |
| 8 | PROVEN | `inputs.py:4032–4038` requires a nonempty identity set and matching folded digest. |

The committed-tree gloss is accurate. `committed_pack_tree_sha256()` explicitly inventories disk paths, rejects extras/missing entries at lines 2833–2847, compares bytes/mode at 2861–2865, and folds sorted paths, Git mode, byte length, and content digest at 2849–2873.

The lineage phrase is accurate at chain level: arm generation computes `pack_sha256` through `_pack_record()`; consumption and lifecycle receipts carry it forward; authenticated lineage exposes it at `arm_readiness.py:10369`. `bundle.py:123–147` obtains only authenticated lineage, while caller-supplied lineage fields are rejected at `bundle.py:1056–1062`. Strictly, the nested lineage reference object carries the receipt chain; the authenticated wrapper carries the propagated pack digest.

## B2 — first-use rulings

| Row | Ruling |
|---|---|
| Committed file tree | No gap. The bench gloss defines it inline at lines 609–613. |
| Plan tree | No gap. `plan_tree.json` is a filename/value first introduced at lines 34–35; its envelope is defined in §3 at 178–211. |
| `projection_receipt` binding | No gap. It is a value in an exhaustive key list at 181, then defined at 192–193. |
| Consumer binding | No gap. `consumer_bindings` is first a value in the exhaustive unit key list at 200, then its rows are defined at 203–204. |

Own first-use audit:

| Term | First use | Definition/build |
|---|---:|---:|
| Analysis gate | 602 | §6.3 heading, 563–579 |
| Successor launch lineage | 605 | 569–570, 583–588 |
| Launch-lineage record | 607 | 569–570 |
| Evidence row | 607 | 161–165, 567–568 |
| Pack root | 608 | 34–35, 440 |
| 64-hex pack digest | 608 | 22–24, 569–570 |
| Committed file tree | 609 | Inline gloss 609–613; code 2750–2874 |
| Path/mode/length/content/path order | 610 | Inline gloss 609–613; code 2849–2873 |
| `committed_pack_tree_sha256` | 611 | Code 2750–2874 |
| Plan tree | 614 | 178–211 |
| Frozen projection/state | 615 | 187–193, 209–211 |
| Freeze-receipt reference | 615 | 490–495; U8 definition 565–568 |
| U8 freeze receipt | 616 | 565–568 |
| PASS status | 616 | 150–151 |
| Sidecar | 617 | 172–174 |
| `u11-freeze-projection` / PACK | 618 | 567–568 |
| `projection_receipt` binding | 619 | 181–193, 494–495 |
| Frozen identity receipt | 620 | 488–495, 567–570 |
| Receipt unit | 622 | Identity-unit definition 77–82; receipt-unit schema 695–701 |
| Consumer binding | 622 | 199–204, 308–309 |
| Condition family | 623 | 574–576 |
| Projection unit | 623 | 300–312 |
| `config_set_sha256` | 624 | 109–111, 357–371 |
| Inventoried config file | 625 | 112–115, 451–452 |
| Inventory digest | 625 | 112–115, 310 |
| JSON object | 627 | Canonical JSON 137–139; code 4028–4030 |
| Scientific identity | 626 | 104–108, 347–355 |
| Frozen set | 632 | 594–598 |
| `consumer_identity_undeclared` | 634 | Defined by the same sentence at 632–634 |
| Legacy evidence | 635 | 598–600 |

The seat’s table omitted the gate/identity-failure framing, launch-lineage record, the 64-hex qualifier, the committed-tree framing components, `committed_pack_tree_sha256`, PASS/namespace values, JSON-object parsing, and the second refusal label. All are either previously defined or built inline; none is a first-use defect.

## B3 — cold reader replication

Yes. From the text alone, a forged but internally consistent pack with an honest lineage produces `consumer_identity_set_unauthenticated`: its internal steps 3–8 can pass, but step 2 fails because its committed-tree digest differs from the launch-bound digest. A forged consumer identity against an authenticated pack reaches the later membership check and produces `consumer_identity_undeclared`.

No sentence requires the former “sequence above” wording or unstated code knowledge.

## C — same-signature statement

- F-B closure-without-biting-test class: NO. The `if False` mutation fails at the exact production seam.
- F-N/F2 first-use prose class: NO. The four disputed rows are resolved by the adopted value/filename rule, and the rewritten paragraph enumerates the mechanism in gate order.

The standing escalation signature is not present; no round 3 or consult is indicated.

## D — suite tails

Full requested suite:

```text
----------------------------------------------------------------------
Ran 446 tests in 89.325s

OK (skipped=1)
```

D-165 focused test:

```text
test_generator_imports_shared_core_and_registration_bytes_are_unchanged ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

D-165 digest:

```text
1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b
```

## Residual risk

The `resolve(strict=True)` survivor is not exercised by the valid forged-pack fixture. The real implementation retains strict resolution and the named cure remains killed.

All execution was synthetic/in-memory; no live P-8 pack closure, hardware run, or production launch was performed.

## What this pass did NOT check

No checkout files were modified. I did not run `unittest discover`, alter production code, perform live hardware validation, or execute the P-8 campaign closure.