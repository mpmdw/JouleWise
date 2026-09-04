```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Production-label closure mutants were killed, but engine-reason mapping lacks a regression and the new contract paragraph is not self-defining.",
  "workspace": {
    "base_requested": "3ac6cffb",
    "base_mode": "exact",
    "head_start": "7c87fa71e37e1c11562dd66b88afb0c89f6fabf6",
    "head_end": "7c87fa71e37e1c11562dd66b88afb0c89f6fabf6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 2,
      "nit": 0
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "New identity labels have no test pinning their required floor_transport_inapplicable engine mapping"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "New contract label paragraph leaves U11 receipt and frozen declaration unglossed and is not standalone"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "env TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.test_detection_floor",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 159 tests in 1.927s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 159 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "env TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.test_analysis_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 15 tests in 20.534s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 15 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.test_analysis_claims",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 59 tests in 0.217s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 59 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "env TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.test_identity_pins",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 41 tests in 6.951s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 41 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "env TMPDIR=<scratch> PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q tests.test_d165_dominance_closeout tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 53 tests in 7.302s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 53 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c '<compute SHA-256 of canonical_json_bytes(generator.dominance_criterion_registration())>'",
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
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The requested single-process six-module command was started twice but this runner returned at about 30 seconds without its completion tail. Its constituent modules passed separately: 159+15+59+41+53 = 327 tests, skipped=1.",
      "needs": "Rerun the exact single-process command in an unrestricted foreground terminal only if one combined tail is required."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "This was fixture/in-memory execution only; no live P-8 freeze/verify or hardware work was run.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — should_fix

`_floor_engine_reasons` currently maps both new labels through its default branch to `floor_transport_inapplicable`, as ruled. A mutant mapping both instead to `floor_row_missing` survived all four new production-label tests. Search found no test of `_floor_engine_reasons` or its new-label mapping.

Add a focused assertion for both labels through `_floor_engine_reasons` (ideally also one claim-output path).

### F2 — should_fix

The new paragraph does state the two high-level labels, but it is not standalone as requested. “U11 receipt” has no prior exact definition in the contract, and “frozen declaration” first appears in this paragraph. The first sentence containing an unglossed term is:

> “If successor launch lineage exists but the gate cannot finish the authentication sequence above—for example, the lineage rows are incomplete or disagree, the pack digest, U8 freeze receipt, U11 receipt, or a sidecar does not authenticate, the projection is not frozen, the selected unit is missing or nonunique, inventoried config bytes fail their hash, the re-derived set is empty or has the wrong digest, or parsing/validation fails—the floor resolution is refused with `consumer_identity_set_unauthenticated`.”

A reader can infer the intended split from the surrounding section, but cannot reconstruct it from that paragraph alone without resolving “authentication sequence above” and “U11 receipt.”

## A1 — counterfactual replay

All mutations were in-memory against production functions. `git diff --exit-code` passed after every replay.

| Mutant | Production site | Biting test(s) | Result |
|---|---|---|---|
| (a) Return `()` for unauthenticated set | `inputs.py:4087` | Four `test_production_*` tests | KILLED; unauthenticated test failed |
| (b) Swap the two labels | `inputs.py:4087,4089,4091` | Four production tests | KILLED; 3 failures |
| (c) Legacy multi-identity/no declaration returns `()` | `inputs.py:4090-4091` | Four production tests | KILLED; legacy test failed |
| (d) Drop carried refusal, falling through historical unavailable resolution | `__init__.py:397,410-447` | Four production tests | KILLED; 3 failures |
| (e) Build refusal with `consumer_term_unknown` | `__init__.py:422` | Four production tests | KILLED; 3 failures |
| (f) Remove both codes from `TRANSPORT_REASON_CODES` | `detection_floor.py:293-311` | Census test; four production tests | KILLED by `TestTransportRule.test_reason_code_set_is_closed_v1_set`; four production tests SURVIVED |

The runtime assert at `detection_floor.py:4416` is not the killer for (f): that function only emits its own transport-rule reasons, never either new analysis-input label. The exact census test is the relevant guard.

## A2 — authentication exits

Each case used `FrozenConsumerIdentitySetTests`’ generated pack builder and `_resolve_contrast_floor(..., request_factory=None)`.

| Exit | How induced | Label observed |
|---|---|---|
| Pack digest mismatch | Replaced lineage `pack_sha256` with 64 zeroes | `("consumer_identity_set_unauthenticated",)` |
| Projection not frozen | Set temporary pack projection state to `unfrozen` | `("consumer_identity_set_unauthenticated",)` |
| Inventoried config hash mismatch | Flipped one temporary inventory-config byte | `("consumer_identity_set_unauthenticated",)` |
| Caught exception | Injected `ValueError` at re-derived identity hashing | `("consumer_identity_set_unauthenticated",)` |

All four returned `status="refused"` with no crash.

## A3 — new-round execution checks

`FloorRequest` is `@dataclass(frozen=True)`, not a `NamedTuple`; a real request cannot satisfy `isinstance(request_or_refusal, tuple)`.

The public wrapper preserves `FloorRequest | None`. The only direct caller outside `__init__.py` is test-only (`tests/test_analysis_integration.py:2726`); three historical-refusal wrapper tests kill a mutant that leaks the internal tuple instead of returning `None`.

The `request_factory` branch remains first and unchanged in effect. Its request-returning and `None` seams passed:

- `test_attribution_limited_floor_is_claim_bearing_in_final_artifact`
- `test_private_stochastic_seam_changes_recorded_policy_identity`
- `test_private_stochastic_seam_changes_recorded_policy_identity_with_production_telemetry_identity`

Own mutants:

| Mutant | Result |
|---|---|
| Public wrapper leaks the internal tuple on refusal | KILLED by 3 historical-refusal tests |
| Map both new labels to `floor_row_missing` instead of default `floor_transport_inapplicable` | SURVIVED all 4 production-label tests; F1 |

Executed current mapping:

```text
consumer_identity_set_unauthenticated -> floor_transport_inapplicable
consumer_identity_undeclared -> floor_transport_inapplicable
```

## A4 — prose and spec order

The contract has prior definitions for U8, U11, launch lineage, sidecar, configuration inventory, and member scientific identity. It does not define the composite “U11 receipt” before line 605, nor “frozen declaration” before line 613. This is F2.

Section 6.3 calls the vocabulary a “closed set”; it states no alphabetical, rule-based, or other ordering requirement. Inserting the two codes before `consumer_term_unknown` does not violate a stated order.

## A5 — suite tails

The separately completed constituent invocations total the expected 327 tests:

```text
tests.test_detection_floor: Ran 159 tests ... OK (skipped=1)
tests.test_analysis_inputs: Ran 15 tests ... OK
tests.test_analysis_claims: Ran 59 tests ... OK
tests.test_identity_pins: Ran 41 tests ... OK
tests.test_d165_dominance_closeout + tests.test_docs_freshness: Ran 53 tests ... OK
```

Total: `327`, `OK (skipped=1)`.

## Digest evidence

`tests.test_d165_dominance_closeout` passed, including its pinned-byte assertion. Direct recomputation at this head produced:

```text
1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b
```

## Residual risk

The combined one-process suite tail was not observed because of the runner foreground cutoff; equivalent constituent module totals passed. No live pack or hardware validation was attempted.

## What this pass did NOT check

This pass did not re-audit round 1, run `unittest discover`, alter checkout bytes, or perform the live P-8/all-three-pack closure.