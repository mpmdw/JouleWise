```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Use the existing session-local path grant exactly once for the plan-tree-selected floor spec, verify its SHA before census semantics, and replace synthetic census claims with frozen-pack regressions.",
  "workspace": {
    "base_requested": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "base_mode": "exact",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": "9dd3c3483f2b151ab49d5b4c64a7fe7484880eed",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The recorder must grant governed vocabulary to exactly its plan-tree-selected extraction spec",
        "recommendation": "Reuse V2AuthenticationReadSession.allow_governed_extraction_spec, explicitly thread the active session into _pack_inventory, and call the grant once only in the extraction-spec branch."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Pinned-byte verification must precede census semantics and all nonselected JSON must retain default refusal",
        "recommendation": "Compute and compare the registry SHA immediately after its authenticated read; preserve existing public refusal codes and prove the unselected sibling spec still refuses."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The current synthetic census is not evidence over the frozen pack shapes",
        "recommendation": "Add repository-backed census tests for both governed floor specs and the real GAMMA prospective manifest; retain the synthetic fixture only as an arithmetic fixture."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse origin/main && git diff --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
          "9dd3c3483f2b151ab49d5b4c64a7fe7484880eed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\).*8937dec9.*9dd3c348"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from pathlib import Path; from joulewise.authentication_io import V2AuthenticationReadSession, V2AuthenticationInputError, read_authentication_input; p=Path(\"configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json\");\\ntry:\\n  with V2AuthenticationReadSession(): read_authentication_input(p, grammar=\"json\", label=\"pack-pinned extraction spec\")\\nexcept V2AuthenticationInputError as e: print(e.reason); print(e.detail)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "v2_authentication_forbidden_json_key",
          "forbidden key 'estimator_registration' at pack-pinned extraction spec.cells[1].estimator_registration"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "v2_authentication_forbidden_json_key.*cells\\[1\\]\\.estimator_registration"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from pathlib import Path; from joulewise.authentication_io import V2AuthenticationReadSession,V2AuthenticationInputError,read_authentication_input; a=Path(\"configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json\"); b=Path(\"configs/floor_mint/d117_qwen25_7b_extraction_spec.json\"); s=V2AuthenticationReadSession(); s.__enter__(); s.allow_governed_extraction_spec(a); read_authentication_input(a,grammar=\"json\",label=\"selected\");\\ntry: read_authentication_input(b,grammar=\"json\",label=\"unselected\")\\nexcept V2AuthenticationInputError as e: print(e.reason); print(e.detail)\\ns.__exit__(None,None,None)'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "v2_authentication_forbidden_json_key",
          "forbidden key 'estimator_registration' at unselected.cells[1].estimator_registration"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "v2_authentication_forbidden_json_key.*unselected\\.cells\\[1\\]"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json configs/floor_mint/d117_qwen25_7b_extraction_spec.json configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d98ae4deb787caaf8a80f972b88b2c85ecc2f96a13092e9127c1e1a661640fd2  configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json",
          "86809f31d2c6933cda42881e10a32bc521cddec01fa941ac4613cd32b9ef49b8  configs/floor_mint/d117_qwen25_7b_extraction_spec.json",
          "e3bc0e3620be2a25c60a6dc7bcab0910997d7d97030f5e80727cd5d951559a57  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "d98ae4de.*86809f31.*e3bc0e36"
      }
    }
  ],
  "flags": [
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The requested council baseline remained clean and unchanged at 8937dec9, while origin/main advanced concurrently.",
      "needs": "Apply and reverify the design on the lead-selected implementation head."
    }
  ]
}
```

## Findings

### F1 — blocker: mirror the mint primitive, narrow the invocation

Use `V2AuthenticationReadSession.allow_governed_extraction_spec`. I disagree with creating a second recorder-specific authentication primitive: the existing method is already session-local, canonical-path scoped, JSON-only, and must run before the first read. A new boolean, directory allowlist, basename rule, or second shared API would enlarge the authority plane.

The recorder should make its use narrower than the mint’s:

1. Pass the active `authentication` session explicitly into `_pack_inventory`.
2. Authenticate and validate `plan_tree.json`, its sidecar, pack identity, and the exactly-one-source choice first.
3. Only in the floor-pack branch, derive `registry_path` with `_safe_relative_path(repository_root, ...)` and validate the plan-tree SHA literal.
4. Call `authentication.allow_governed_extraction_spec(registry_path)` exactly once.
5. Read that path through `_json_object`.
6. Immediately hash the returned bytes and compare them with the plan-tree pin before `_floor_cells` or any membership processing.
7. Never grant the GAMMA analysis manifest, reports, plan tree, bundles, or the other floor pack’s spec.

The grant may remain live until the session exits: subsequent reads of that same canonical path are constrained by the authentication registry’s first-digest and grammar invariants. No change to `joulewise/authentication_io.py` is needed.

Contract delta: no receipt schema, CLI, mint behavior, or public authentication API change. The only implementation-contract delta is that `_pack_inventory` receives the session capability and documents the plan-tree-selected extraction spec as its sole governed-vocabulary input. This executes D-133; it does not amend its scientific semantics.

### F2 — should_fix: widening threat and refusal boundaries

The grant exempts the selected file from the recursive lexical ban on `estimator_registration`; it does not weaken duplicate-key, UTF-8, finite-number, grammar, digest-stability, or path-containment checks.

| Attempt | Required result |
|---|---|
| Exact frozen selected spec | Admitted; only `cell_id`, metric, and membership flow into the receipt |
| Other floor spec in the same session | `authoritative_input_invalid`, preserving nested `v2_authentication_forbidden_json_key` detail |
| Registration in plan tree, report, bundle JSON, or GAMMA manifest | Same forbidden-key refusal |
| Selected path with changed bytes | `pack_pin_invalid` before census or bundle discovery |
| Escaping/absolute extraction path or malformed SHA | `pack_pin_invalid` |
| Duplicate keys, invalid UTF-8/JSON, nonfinite values | `authoritative_input_invalid` with the existing nested authentication reason |
| Bad schema or dropped/extra census result | `registered_cell_inventory_invalid` |
| Malformed, incomplete, or duplicated members | Existing `registered_membership_invalid` or `member_non_unique` |

No new public refusal code is warranted. Grant-construction errors must also be normalized rather than leaking `ValueError` or `RuntimeError`.

The widest content that can cross the lexical reader is any occurrence of `estimator_registration` inside the one authorized file. Unexpected bytes cannot affect a receipt under this design because the exact plan-tree SHA is checked before semantic use. A self-consistent replacement of the plan tree, sidecar, and spec remains possible to the single authority; that is the pre-existing D-120 `single_authority_hash_bound_replay.v1` limitation, not a consequence of this grant.

### F3 — should_fix: frozen census regressions

Replace the “real floor pack shapes” claim over `_registry()` with repository-backed tests over:

- `configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`, SHA `d98ae4de…`
- `configs/floor_mint/d117_qwen25_7b_extraction_spec.json`, SHA `86809f31…`
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json`, SHA `e3bc0e36…`

The first two must each yield exactly three comparative cells—decode, prefill-p128, and prefill-p256—with 40 unique members, 10 exact ABBA blocks, `d124_two_shared_edge_common_mode.v1`, and the real canonical `estimator_registration`. Assert the six exact frozen cell IDs.

The real GAMMA source has two contrasts, not the synthetic fixture’s three: decode and prefill-p256, each with 40 members. It must pass without any governed-extraction-spec grant.

Also add negative regressions proving:

- authorizing ALPHA does not authorize BETA;
- an unpinned sibling JSON still refuses the key;
- same-path byte mutation produces `pack_pin_invalid`;
- floor packs invoke the grant exactly once, while GAMMA invokes it zero times;
- the public recorder maps forbidden-key failures to `authoritative_input_invalid` and writes no receipt.

Keep the synthetic four-member/one-block fixture for numeric derivation tests, but rename its claim: it does not model frozen production shapes.

## Residual risk

This was a read-only design review at the requested `8937dec9` council baseline; no implementation or full suite was run. Final-head verification should include the focused authentication and margin-recorder modules, the canonical suite, and a no-output assertion for every refusal case.