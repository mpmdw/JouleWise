```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Re-audit completed: one clause-map blocker and three should-fix findings remain.",
  "workspace": {
    "base_requested": "1a60808974dea46c54e11dc3fc6900ab6230644d",
    "base_mode": "exact",
    "head_start": "3ac6cffb1541bd9f2e8b7cfee2aa4ead8ca0474a",
    "head_end": "3ac6cffb1541bd9f2e8b7cfee2aa4ead8ca0474a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 1,
      "should_fix": 3,
      "nit": 0
    },
    "findings": [
      {
        "id": "F-B",
        "severity": "blocker",
        "title": "Committed-pack digest counterfactual survives its named stale-receipt test"
      },
      {
        "id": "F-G",
        "severity": "should_fix",
        "title": "Cardinality kill is helper-only synthetic evidence"
      },
      {
        "id": "F-COUPLING",
        "severity": "should_fix",
        "title": "Multi-identity transport test mocks the production frozen-set gate"
      },
      {
        "id": "F-N",
        "severity": "should_fix",
        "title": "U11 first appears unglossed inside the work-order identifier"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=<scratchpad>/sol-decode-audit PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_contrast_v5_pack tests.test_identity_pins tests.test_analysis_inputs tests.test_d165_dominance_closeout tests.test_night_gate tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 188 tests in 39.776s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 188 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/sol-decode-audit PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 47 tests in 8.262s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 47 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "TMPDIR=<scratchpad>/sol-decode-audit PYTHONDONTWRITEBYTECODE=1 python3 -c 'import hashlib; from configs.campaigns.d117_contrast_v5 import generate_configs as g; from joulewise.analysis_manifest_v3 import canonical_json_bytes; print(hashlib.sha256(canonical_json_bytes(g.dominance_criterion_registration())).hexdigest())'",
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
      "kind": "inspection",
      "cmd": "git diff --exit-code && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "F-B's named stale-receipt test still passes when committed-pack digest comparison is disabled.",
      "needs": "Add an isolated stale pack_sha256 or plan-tree mutation test."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "F-G is killed only through direct invocation of the mutated cardinality helper; the generated freeze path has no independent mismatch fixture.",
      "needs": "Add an end-to-end cardinality mismatch fixture or explicitly classify the helper test as unit-only."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "F-M was intentionally not audited; no live or quiet-machine validation was performed.",
      "needs": ""
    }
  ]
}
```

## Findings

- F-B — blocker. Disabling `committed_pack_tree_sha256` at `joulewise/analysis_engine/inputs.py:3898` still passes `test_generated_pack_gate_and_caller_refuse_stale_receipt_bytes`; that test’s tampered receipt is independently caught by the receipt-byte digest check.

- F-G — should-fix. Disabling `_distinct_manifest_identity_refusal_reason` is killed only by directly testing that helper with synthetic sets. It does not prove the production freeze path reaches the mismatch.

- F-COUPLING — should-fix. `test_multi_identity_transport_requires_declared_subset_and_skips_exact_cell` mocks `_frozen_consumer_identity_set`, so it can pass even if the real U8/frozen-receipt gate is eviscerated.

- F-N — should-fix. U11 is first embedded unglossed in the earlier work-order bullet: “`work_order` is `D117-U11-IDPIN-PROJECTION`;”. The definitions at lines 565–579 precede the analysis-consumption prose, and the gate is otherwise reconstructible.

## A1 — clause-map replay

| Row | Mutation applied | Production site | Named test | Result |
|---|---|---|---|---|
| F-A | Disabled declared-manifest byte hash comparison | `identity_pins.py:1621` | Freeze and verify manifest-tamper tests | KILLED |
| F-B | Disabled committed pack-tree digest comparison | `inputs.py:3898` | Stale receipt gate/caller test | SURVIVED |
| F-C | Nested same-condition refusal under single identity | `inputs.py:4148` | Multi-identity transport test | KILLED |
| F-D | Immediate `return frozenset()` from frozen-set helper | `inputs.py:3870` | Generated gate, config-set, no-lineage tests | KILLED |
| F-E | Folded declaration counts from staged emitted configs | Generator declaration path | Rule-derived declaration test | KILLED |
| F-F | Changed exact census to emitted `>=` declared | `identity_pins.py:1681` | Extra byte-identical member test | KILLED |
| F-G | Cardinality helper always returned `None` | `identity_pins.py:1571` | Synthetic cardinality test | KILLED — helper-only |
| F-H | Disabled member runtime-pin and stack equality | `identity_pins.py:1845` | Runtime-pin drift test | KILLED |
| F-I | Disabled current/frozen runtime-triple comparison | `identity_pins.py:2453` | Runtime-triple and metadata-drift tests | KILLED |
| F-J | Made GAMMA roster validator a no-op | Generator `validate_gamma_identity_unit_roster` | Three-unit roster test | KILLED |
| F-K | Changed rotation modulo eight to modulo seven | Generator `decode_prompt_index` | Rotation test | KILLED |
| F-O | Filtered missing `pack_root` rows out of the set | `inputs.py:3870` | Missing-pack-root test | KILLED |
| F-P | Recomputed identity hash from raw config | `inputs.py:4079` | Multi-identity transport test | KILLED |

Every mutation was restored byte-exactly; each temporary clone passed `git diff --exit-code`.

## A2 — additional mutants

- `M-OWN-PROJECTION-RECEIPT-BINDING`: removed the projection-versus-frozen-receipt `config_set_sha256` equality check. A projection-only forged binding caused the end-to-end gate to return a request. KILLED.

- `M-OWN-EFFECTIVE-MANIFEST-RENDERER`: replaced `render_suite_manifest_bytes` with the old raw renderer. Generated freeze then refused the manifest as unauthenticated. KILLED.

The new `frozenset()` refusal paths remain fail-closed: the caller treats non-`None` empty sets as refusal. Freeze and verify both call `_derive_projection_units`; no one-sided census/common-profile path was found.

## A3 — prose closures

F-L is corrected: the three documents now state `<N>`, identify 512 for `_v5`, and preserve 256 only as the superseded `_v3` value.

F-N is not fully closed under strict first-use reading because U11 occurs in the earlier fixed work-order identifier before its plain-language definition. After the definitions block, the analysis gate specifies the receipt chain, subset rule, exact-cell restriction, and transport-only multi-identity route.

## A4 — focused suite tail

The requested command passed:

`Ran 188 tests in 39.776s`

`OK`

## Digest evidence

The dedicated D-165 module passed 47 tests, and direct canonical computation produced:

`1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`

## Residual risk

No live hardware or quiet-window validation was performed. F-M was intentionally excluded, and the all-three-pack regeneration/closure campaign was not rerun here.

## What this pass did NOT check

- `python3 -m unittest discover`
- F-M or `/Users/edr/code/JouleWise-wt-decode-id`
- Live measurement, launch, or hardware gates
- Repository writes, commits, merges, or deployments