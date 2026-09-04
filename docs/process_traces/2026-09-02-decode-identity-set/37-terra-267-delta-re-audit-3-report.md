# terra 267 (gpt-5.6-terra xhigh, read-only, wt-decode-id3 @ fbedfb04) — delta re-audit of fix round 3

Custodied verbatim (temp paths redacted). Verdict 0/1/0: F-N4 (first-use defect in the S3 lineage paragraph — FOURTH consecutive prose defect in this section); all execution cures bite.

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All execution cures bite, but the new lineage paragraph repeats the contract first-use defect by introducing several terms before defining them.",
  "workspace": {
    "base_requested": "791a2522513dc0de91c786025ba52a3f20031037",
    "base_mode": "descendant",
    "head_start": "fbedfb040805828a0b8a48bb6455dba57c0555a6",
    "head_end": "fbedfb040805828a0b8a48bb6455dba57c0555a6",
    "upstream_end": "fbedfb040805828a0b8a48bb6455dba57c0555a6",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 0
    },
    "findings": [
      {
        "id": "F-N4",
        "severity": "should_fix",
        "title": "The new S3 lineage paragraph violates the contract first-use rule: it uses launch manifest, consumption receipt, window root, lifecycle receipts, and the new refusal labels before their definitions."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=<audit-tmp> python3 -B -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 487 tests in 112.259s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 487 tests in .*\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=<audit-tmp> python3 -B -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 47 tests in 8.026s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 47 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json && git diff --check && git diff -- docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b  configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1c0a4a119fa06984"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "This read-only pass did not perform P-8 regeneration/freeze/arm verification or construct a complete moved successor bundle through all absolute lineage receipts.",
      "needs": "Lead-owned P-8 and integration replay after disposition."
    }
  ]
}
```

Reviewed head: `fbedfb040805828a0b8a48bb6455dba57c0555a6`. The checkout remained clean and no checkout file was written.

## Findings

### F-N4 — should_fix

The S3 paragraph is factually sound, but misses the stated first-use standard. It introduces `consumption receipt`, `launch manifest`, `window root`, `lifecycle receipts`, `launch_binding_mismatch`, and `launch_consumption_missing` at [identity_pin_projection.md](/Users/edr/code/JouleWise-wt-decode-id3/docs/contracts/identity_pin_projection.md:612). `launch manifest` is first defined only later at line 671; the other lineage-specific terms are not defined there at first use. Sol 266’s first-use table omitted the entire new lineage text.

## A. Execution lens

### A1 — S2

Restoring the removed literal in memory killed the new assertion:

```text
AssertionError: {'nam[52 chars]1, 'warmup_runs': 1, 'output_tokens': 512, 'prompt_tokens': 42} != {'nam[52 chars]1, 'warmup_runs': 1, 'output_tokens': 512}
  {'name': 'real_prompts_v1_chat_rendered',
   'output_tokens': 512,
-  'prompt_tokens': 42,
   'repetitions': 1,
   'warmup_runs': 1}

----------------------------------------------------------------------
Ran 1 test in 0.473s

FAILED (failures=1)
```

The assertion block at [test_d117_contrast_v5_pack.py](/Users/edr/code/JouleWise-wt-decode-id3/tests/test_d117_contrast_v5_pack.py:867) kills all requested independent in-memory pack mutants:

- Plan decode workload missing `output_tokens`: **KILLED** at line 867.
- Declared decode profile missing `suite_manifest_set`: **KILLED** at line 895.
- Declared decode profile with non-null `prompt_tokens: 42`: **KILLED** at line 897.

`WorkloadProfile` permits these nullable typed fields: `prompt_tokens`, `output_tokens`, `prompt_text`, `dataset_ref`, `suite_manifest_ref`, `suite_manifest_sha256`, `generator_sidecar_ref`, `prompt_token_evidence_policy`, and `prompt_token_expectation` ([schemas.py](/Users/edr/code/JouleWise-wt-decode-id3/joulewise/schemas.py:898)). `name`, `repetitions`, and `warmup_runs` are non-null.

For a decode unit, the paired suite-manifest fields are non-null; `prompt_tokens`, `prompt_text`, and `dataset_ref` must be null because the suite reference is its one prompt source; `prompt_token_expectation` requires non-null prompt text. Generic optional fields may be non-null in other valid workloads, but the assertion retains every non-null key. Thus it cannot wrongly pass an extra non-null decode declaration; under R-2’s exact four-key common-profile ruling, such a declaration correctly fails.

`DECODE_PROMPT_TOKENS[arm]` remains emitted in the per-model prompt candidate at generator line 1551, but emitted decode configs carry no `prompt_tokens`:

```text
A …/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b08-a2.json
{"name":"real_prompts_v1_chat_rendered","output_tokens":512,"repetitions":1,"suite_manifest_ref":"configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-1p7b/08_pantry_dinner.json","suite_manifest_sha256":"abb40dce…","warmup_runs":1}
B …/d117c-qwen3-1p7b-vs-qwen3-8b-v5-decode-contrast-b07-b1.json
{"name":"real_prompts_v1_chat_rendered","output_tokens":512,"repetitions":1,"suite_manifest_ref":"configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/decode_prompt_manifests/qwen3-8b/07_falsifiability.json","suite_manifest_sha256":"06cdc9f7…","warmup_runs":1}
```

This resolves the Fable/Sol apparent contradiction: per-arm token counts remain in `decode_workload_candidate`, not in emitted decode config workloads.

D-166 remains `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`; `tests.test_d165_dominance_closeout` ran 47 tests, OK.

### A2 — S3 direct seam

Removing `OSError` from the catch tuple in memory kills the new test:

```text
FileNotFoundError: [Errno 2] No such file or directory: '<audit-tmp>'

----------------------------------------------------------------------
Ran 1 test in 1.848s

FAILED (errors=1)
```

Changing line 3897 to `resolve(strict=False)` leaves the test **PASS**:

```text
Ran 1 test in 1.831s

OK
```

That test pins the refusal conversion around the downstream committed-tree check, not strict resolution specifically: `committed_pack_tree_sha256(missing_path)` also raises and is caught as `OSError`.

### A3 — round-2 tests

F-B, with the committed-tree comparison changed to `if False:`, is **KILLED**:

```text
AssertionError: 'exact' != 'refused'
- exact
+ refused

----------------------------------------------------------------------
Ran 1 test in 4.055s

FAILED (failures=1)
```

R2-B, with the entire frozen-set gate body replaced by `return frozenset()`, is **KILLED**:

```text
AssertionError: 'consumer_identity_set_unauthenticated' unexpectedly found in ('consumer_identity_set_unauthenticated',)

----------------------------------------------------------------------
Ran 1 test in 1.821s

FAILED (failures=1)
```

## B1. Freeze procedure and ordering

Every changed factual clause is proven; none is overclaimed or underclaimed.

| Text clause | Grade | Proving code |
|---|---|---|
| Read each inventoried config’s raw bytes | PROVEN | `identity_pins.py:1592,1436-1441` |
| Require the inventory SHA-256 | PROVEN | `:1440,1446-1451` |
| Parse a JSON object | PROVEN | `:1441-1455` |
| Type later, per configuration | PROVEN | `_declared_identity_from_config` `:1262-1278`, invoked `:1635-1636`; direct `BenchmarkConfig` construction `:1675` |
| Branch on `suite_manifest_set` | PROVEN | `:1472-1481,1594-1601` |
| Validate exact three-field members | PROVEN | `:1499-1531` |
| Remove only `suite_manifest_set` for the declared common profile | PROVEN | `:1536-1538` |
| Require a relative POSIX reference | PROVEN | `:1505-1517` |
| Retain only the suffix after the pack directory name | PROVEN | `:1544-1560` |
| Require a regular non-symlink below pack root | PROVEN | `:1541-1568 → _resolve_config_path :1239-1259` |
| Read each manifest and compare its SHA-256 | PROVEN | `:1610-1630` |
| Unresolvable, unreadable, or mismatching manifests use the named dirty refusal | PROVEN | `:1563-1568,1615-1630` |
| Manifest authentication precedes every config declaration comparison | PROVEN | manifest loop `:1610-1630` precedes declaration loop `:1635-1654` |
| Remove only the two per-member fields from observed typed workload | PROVEN | `project_identity_unit_common_profile :261-269`, called `:1640-1644` |
| Compare observed common workload and all non-workload declaration fields | PROVEN | `:1646-1654` |
| Authenticate config and declared-manifest bytes before declarations | PROVEN | config `:1436-1451`; manifest `:1610-1630`; comparison `:1635-1654` |
| Treat exact manifest digest/reference pairing as step 4 | PROVEN | `:1658-1670` |

Fresh ordering probe:

```text
(1) manifest bytes tampered only -> readiness_identity_environment_dirty | declared suite manifest is unauthenticated: …
(2) config bytes AND manifest tampered -> readiness_identity_environment_dirty | config bytes changed for 01_decode_contrast_blocks_01_05/…
(3) config bytes only -> readiness_identity_environment_dirty | config bytes changed for 01_decode_contrast_blocks_01_05/…
(4) declaration drift AND manifest tampered -> readiness_identity_environment_dirty | declared suite manifest is unauthenticated: …
(5) declaration drift only -> readiness_identity_environment_dirty | identity unit 'A/decode' config declaration differs from pack
```

The executed order is therefore: config raw-byte authentication → manifest-file authentication → typed declaration comparison → digest/reference pair check.

## B2. Lineage-layer paragraph

| Clause | Proving code |
|---|---|
| Arm records a resolved absolute pack root | `arm_readiness.py:5242-5259` |
| Bundle loading authenticates lineage before `BundleEvidence` construction | `inputs.py:2768-2782,2827-2830` |
| Consumption receipt is read/authenticated first | `arm_readiness.py:8960-8985,10127-10144` |
| Consumed arm replays and resolves recorded root strictly | `:9304-9352` |
| Launch manifest resolves/authenticates | `:8988-9028,10187-10198,10222` |
| Window root resolves strictly | `:10200-10205` |
| Lifecycle receipts are read/authenticated | `:10233-10252,9794-9811` |
| Direct gate missing-root handling | `inputs.py:3897-3899,4039-4048,4082-4089` |

Executed hops:

```text
consumption-receipt hop -> launch_consumption_missing | launch-lineage receipt is absent: …/arm-0001.consumed.json: [Errno 2] No such file or directory
_replay_consumed_arm missing pack_root -> launch_binding_mismatch | consumed arm pack root cannot be authenticated: [Errno 2] No such file or directory
```

“The same label as any pack it cannot authenticate” is true for the direct frozen-set gate: each `frozenset()` exit maps through lines 4082–4087 to `consumer_identity_set_unauthenticated`. Those exits cover mixed/missing lineage, missing or inconsistent roots/hashes, strict-root or committed-tree failure, invalid plan/projection, invalid freeze binding/bytes/sidecar, invalid U11 binding, invalid frozen projection receipt, missing/mismatched receipt unit, inventory byte/JSON failure, bad identity-set digest, and all caught gate exceptions. It does not describe upstream lineage failures, which halt at input loading with `launch_consumption_missing` or `launch_binding_mismatch`.

## B3. First-use audit and cold read

| New text | Term | First definition / result |
|---|---|---|
| Freeze step 1 | `BenchmarkConfig` | First used and functionally glossed inline at 453–454; adequate. |
| Freeze step 3 | `suite_manifest_set`, declared manifest member, common workload | Defined at 86–98; adequate. |
| Freeze step 3 | repository-relative suffix handling; regular non-symlink file | Defined operationally inline at 461–465; adequate. |
| Authentication paragraph | inventory digest; exact declared pair; unauthenticated manifest binding | Inventory at 112–115; pair at 99–103; binding defined inline at 496–501. |
| S3 lineage paragraph | machine-absolute pack path | New construction at 609; understandable from the sentence but not formally defined. |
| S3 lineage paragraph | consumption receipt | First used at 612; generic receipt is defined at 48, specific consumption record appears only later at 672–673. |
| S3 lineage paragraph | launch manifest | First used at 612; definition follows only at 671–672. |
| S3 lineage paragraph | window root; lifecycle receipts | First used at 612; no first-use gloss. |
| S3 lineage paragraph | `launch_binding_mismatch`, `launch_consumption_missing` | First used at 614–615 without a local definition. |
| S3 lineage paragraph | `consumer_identity_set_unauthenticated` | First used at 620; its eight-step meaning follows at 634–659. |

Sol’s table missed all S3 lineage first uses. It also cited lines 90–93 as the definition of “repository-relative manifest path”; those lines define a relative POSIX reference, while the repository-relative suffix behavior is only explained inline at 461–464.

Cold read: yes, a reader can state why a bundle from a clone never reaches `consumer_identity_set_unauthenticated`: bundle loading authenticates lineage first, strictly resolves arming-time absolute roots, and refuses during input loading if they are absent. The defect is first-use pedagogy, not that causal explanation.

## B4. D-171a addendum

Verified against `06-ruling-171a.md`:

- `R-1 (exact identities stay exact).`
- `R-5 (unit config-set digest; no new key).`

The addendum at [decision_log.md](/Users/edr/code/JouleWise-wt-decode-id3/docs/decision_log.md:8464) is correct.

## C. Same-signature statement

| Class | Result | Evidence |
|---|---|---|
| Closure without a biting test, F-B | NO | The `if False` committed-tree mutant fails at the production resolution seam. |
| First-use/ordering prose, F-N/F2/S1 | YES — fourth consecutive | F-N4: new S3 terms are introduced before definition; Sol’s table omitted the paragraph. |
| Uninstalled ruling clause, S2 | NO | Literal-restoration and all three shape mutants are killed; emitted configs retain no decode `prompt_tokens`. |

## D. Suite tail

```text
----------------------------------------------------------------------
Ran 487 tests in 112.259s

OK (skipped=1)
```

## Residual risk

No P-8 regeneration/freeze/arm verification or full moved-bundle lineage replay was performed.

## What this pass did NOT check

No `unittest discover`, no hardware or quiet-Mac work, no production campaign operation, and no implementation changes.