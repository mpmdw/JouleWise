```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The exact Qwen3 _v5 identities are derivable now, but the numeric family-generation coupling and R-9 kernel dependencies must be included; successor pinset bytes remain desk-day-bound.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "85d952d824fac813e73d078c5173054e37bf7d90",
    "head_end": "85d952d824fac813e73d078c5173054e37bf7d90",
    "upstream_end": "85d952d824fac813e73d078c5173054e37bf7d90",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "R-9 is not represented in the current kernel",
        "detail": "TRANSACTION-RULED-ARTIFACTS-01 still has no dependencies and names _v4; V5-DESK-DAY-01 does not depend on V5-IDENTITY-REPARAM-01. The bench-owned kernel edit must precede desk day."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The transfer includes a numeric generation parameter absent from the grep",
        "detail": "family_publication_first_generation is copied into marker.family_generation. Changing only d117-v4 strings would emit family_id d117-v5 with family_generation 4. The registry value and coherence tests must move to 5."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Identity wiring and successor pinset bytes have different landing boundaries",
        "detail": "The v5 path and successor IDs can land now while absent; the pinset bytes require generated, evidenced, freeze-0004-bound packs and therefore wait for V5-DESK-DAY-01."
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "The build_v4_histsem_pinset.py basename is a nonblocking Ed naming question",
        "detail": "Its behavior is registry-derived and can build the v5 roster without a rename. Renaming affects authenticated sidecars, refresh-tool enumeration, contracts, and tests."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1 -uall && git rev-parse HEAD && git rev-parse @{upstream}",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "porcelain output empty",
          "85d952d824fac813e73d078c5173054e37bf7d90",
          "85d952d824fac813e73d078c5173054e37bf7d90"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "85d952d824fac813e73d078c5173054e37bf7d90"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -l -i 'd117-v4|_v4\\b|pinset_v4|v4_v1' joulewise scripts tests configs/arm_readiness docs/contracts | wc -l; rg -n -i 'd117-v4|_v4\\b|pinset_v4|v4_v1' joulewise scripts tests configs/arm_readiness docs/contracts | wc -l",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "27 files",
          "253 matching lines"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "27 files.*253 matching lines"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R-9's kernel dependency edits remain bench-owned and are absent at this head.",
      "needs": "Add V5-IDENTITY-REPARAM-01 and the ruled start dependencies in docs/process/state_kernel.json, then regenerate state projections."
    },
    {
      "id": "FL2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The build_v4_histsem_pinset.py rename remains an Ed naming decision.",
      "needs": "Keep the legacy basename for this implementation unless Ed explicitly authorizes the rename."
    },
    {
      "id": "FL3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only scout; no generator or test suite was run.",
      "needs": "Run the proposed focused and canonical checks in the implementation sessions."
    }
  ]
}
```

## Findings

### F1 — R-9 kernel dependency is absent

At this head:

- `TRANSACTION-RULED-ARTIFACTS-01.dependencies` is empty and its goal still says `_v4`.
- `V5-DESK-DAY-01` depends on G2-a, but not `V5-IDENTITY-REPARAM-01`.

R-9 therefore needs its bench-owned kernel edit before desk day. Per the ruling, `docs/process/state_kernel.json` belongs in no Sol implementation scope.

### F2 — `_v5` also requires the numeric generation to become 5

`build_family_publication_marker` serializes:

```text
family_generation = family_publication_first_generation
```

and the validator requires equality. Consequently, changing only `family_id` to `d117-v5` while leaving the registry threshold at 4 creates an incoherent marker: `d117-v5`, generation 4.

The coherent transfer is:

- `family_publication_first_generation`: `5`
- marker `family_generation`: derived as `5`
- family-publication gate: still engages for the `_v5` roster
- actual pack predecessor: the ruled `_v3` pack
- freeze receipt: still `freeze-0004`, because receipt ordinals advance from the predecessor’s `freeze-0003`; pack suffixes need not be adjacent.

### F3 — identity can land now; pinset bytes cannot

The path, roster, family ID, marker/table names, and all refusal checks can be reparameterized before G2-a. The pinset file cannot be created yet because its rows bind committed pack and receipt bytes that do not exist.

### F4 — tool rename is optional and nonblocking

Keep `scripts/build_v4_histsem_pinset.py` as a legacy basename unless Ed rules otherwise. Its production roster comes from the registry, so the existing filename does not prevent it from building `_v5` rows.

A rename would touch:

- `scripts/build_v4_histsem_pinset.py` and its `.sha256` sidecar
- `scripts/refresh_receipt_histsem_pinset.py`’s authenticated tool tuple
- `docs/contracts/receipt_histsem_verifier.md:68`
- `tests/test_family_marker.py:816`
- `tests/test_receipt_histsem.py:176,191,2010,2020,2163`

Historical process traces naming the old tool must remain unchanged.

### A. Complete inventory

Ranges denote every matching line in the range.

| Site | Classification | Disposition |
|---|---|---|
| `docs/contracts/d117_step6_confirmation_table.md:44,108,111,118,124,130,150,174,307` | LIVE-PARAMETER | Transfer family, filenames, roster, pinset path, and normative generation wording to `_v5`. |
| `configs/arm_readiness/d117_row_registry_v2.json:213-324,533-535` | LIVE-PARAMETER | Replace all 112 allowlist identities and the three-member roster; count remains 112. |
| `joulewise/arm_readiness.py:76,77,2865,2979,7413,10718,10777,10854-10856,10987,11015,11081,11086,11415,11443` | LIVE-PARAMETER | Transfer marker/table names, pinset path, family ID, roster, transaction ID, and current-order prose. |
| `scripts/build_v4_histsem_pinset.py:2,139,285` | LIVE-PARAMETER | Update current-transaction prose to `_v5`; retain `freeze-0004`. Updating bytes requires its sidecar refresh. |
| `scripts/build_v4_histsem_pinset.py` basename | TOOL-NAME | Keep pending Ed; rename footprint is listed under F4. |
| `docs/contracts/analysis_plans.md:103` | LIVE-PARAMETER | Current generation-time example becomes `_v5`. |
| `tests/test_check_window_provenance.py:540-543` | HISTORICAL-RECORD | Leave: it authenticates literal content in the dated G2 runsheet trace. |
| `docs/contracts/receipt_histsem_verifier.md:19,310,312,314` | LIVE-PARAMETER | Enumerated successor and current sequencing become `_v5`. |
| `tests/test_reauthor_clean.py:87,174` | HISTORICAL-RECORD | Leave: arbitrary synthetic fixture identity. |
| `tests/test_d117_decode_contrast_plan.py:1448,1455` | LIVE-PARAMETER | Update the description of the live installed registry. |
| `tests/test_d117_decode_contrast_plan.py:2523,2525,2537` | HISTORICAL-RECORD | Leave: deliberate generation-4 output used in a generic v3→v4 regression. |
| `tests/test_gen_state.py:148,392,410,416` | HISTORICAL-RECORD | Leave: dated queue-count/event chronology. |
| `tests/test_arm_readiness_evidence_packauth.py:72,543,550` | HISTORICAL-RECORD | Leave: deliberate generated-v4 fixture testing generic derivation-mode behavior. |
| `tests/test_arm_readiness_lifecycle.py:52,55,56,147,1056-1058,1950,1958,2388,2773,2790,2895,2902,2904` | LIVE-PARAMETER | Repoint live-roster fixtures and descriptions to Qwen3 `_v5`; add a coherent non-adjacent `_v5`→`_v3` row. |
| `tests/test_arm_readiness_schemas.py:432,483` | LIVE-PARAMETER | Update live-pack wording and exact successor path. |
| `tests/test_arm_readiness_integration.py:49,53-55` | LIVE-PARAMETER | Replace the live synthetic roster with exact Qwen3 `_v5` IDs. |
| `tests/test_arm_readiness_dry_run.py:366-368` | LIVE-PARAMETER | Replace the live family map. |
| `scripts/verify_family_marker.py:71,97` | LIVE-PARAMETER | Refusal receipts must identify `d117-v5`; line 2’s plain `v4` docstring is also coupled. |
| `tests/test_arm_readiness_registry.py:149` | LIVE-PARAMETER | Live-registry wording becomes `_v5`. |
| `tests/test_family_marker.py:90,116-118,136,153,154,179,463,477,549,623,656,674,861,909,1131,1205,1225,1459` | LIVE-PARAMETER | Rebuild golden/current fixtures around family 5 and the Qwen3 roster; retain generic historical identities only where separately named. |
| `tests/test_launch_window.py:452-454` | LIVE-PARAMETER | Replace the live family map. |
| `tests/test_paper_build.py:78` | LIVE-PARAMETER | Update with the coupled current source `docs/paper/draft-v1.md:7`. |
| `tests/test_s0_blocked_enumeration.py:102` | HISTORICAL-RECORD | Leave: historical blocked-reason vocabulary; the current asserted S0 count is zero. |
| `tests/test_receipt_histsem.py:56,66-68,136,158,2030` | LIVE-PARAMETER | Transfer successor path, exact IDs, temporary enumerated path, and current transaction wording. |
| `tests/test_receipt_histsem.py:161,162,167,2051` | HISTORICAL-RECORD | Leave: deliberately synthetic v4 rows/pack used for generic chain and pre-authoring tests. |
| `scripts/paper_prefill_resolvability_projection.py:91,92,103,112,393,530-532,730` | HISTORICAL-RECORD | Leave: these variables identify the measured Qwen2.5 predecessor corpus used by the projection. |
| `tests/fixtures/packauth_recorded_freeze/manifest.json:3,10` | FIXTURE-BYTES | Leave byte-for-byte: recorded estate evidence. |
| `tests/test_arm_readiness_evidence_author.py:1242-1244,1250` | LIVE-PARAMETER | Replace the live successor-family fixture. |
| `tests/test_d117_gamma_d139a2_families.py:157,357,358,547,573` | HISTORICAL-RECORD | Leave: intentional paired v4/v5 generic-generation regression. |
| `scripts/paper_terms_lint.py:90` | HISTORICAL-RECORD | Retain `_v4` as forbidden legacy vocabulary; add `_v5` separately only if the paper lint’s current policy requires it. |

### B. Exact derived `_v5` values

Source: `configs/model_panels/qwen3_4bit.json`.

| Arm | Panel `model_id` | D-164 repository | `_identifier_token` |
|---|---|---|---|
| A / ALPHA | `qwen3-1p7b` | `mlx-community/Qwen3-1.7B-4bit` | `qwen3-1p7b` |
| B / BETA | `qwen3-8b` | `mlx-community/Qwen3-8B-4bit` | `qwen3-8b` |

`_identifier_token` only replaces underscores with hyphens, so both tokens are unchanged.

Generator derivation:

```text
contrast = f"d117_contrast_{MODEL_IDS['A']}_vs_{MODEL_IDS['B']}_v5"
floor[A] = f"d117_floor_{MODEL_IDS['A']}_v5"
floor[B] = f"d117_floor_{MODEL_IDS['B']}_v5"
```

Therefore the exact roster is:

```text
ALPHA  d117_floor_qwen3-1p7b_v5
BETA   d117_floor_qwen3-8b_v5
GAMMA  d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5
```

The remaining canonical values are:

```text
family_id                       d117-v5
family_generation               5
family_publication threshold    5
marker filename                 d117_family_publication_v5.json
confirmation-table filename     d117_step6_confirmation_table_v5.json
successor pinset path           configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json
freeze receipt                  freeze-0004
```

Pinned now:

- both model IDs and revisions
- identical tokenizer hash
- chat-template hash and thinking-off policy
- decode rendering pinset
- all three pack IDs

Still unpinned:

- selected `prefill_length`
- the matching `joulewise.prefill_prompt_pin.v2`
- all generated pack bytes and their digests
- historical/current Git coordinates used by the histsem builder
- the successor pinset digest `hS`

The unresolved inputs affect pack bytes and plan identities, but not any pack ID above.

### C. Landing boundary

Can land now:

- registry roster and its 112-entry exact allowlist
- registry generation threshold `5`
- library family ID, filenames, tuple path, marker/table validators and builders
- verifier refusal-receipt family ID
- exact Qwen3 roster fixtures and positive coherent tests
- contracts
- builder prose and authenticated tool sidecars
- paper placeholder/test coupling
- future `--write-successor-test-pin` support, if assigned to the transaction-artifact session rather than this identity session

Desk-day-bound:

- the three generated pack directories
- evidence authoring and U11 projections
- PASS `freeze-0004` for each pack
- `legacy_receipt_histsem_pinset_v5_v1.json`
- `hS`
- the later fixation literal `SUCCESSOR_PINSET_SHA256 = "<hS>"`

The pinset builder requires:

1. the immutable v1 base pinset;
2. exact historical and current commit OIDs;
3. three committed pack roots matching the registry;
4. a pre-authoring historical tree for each pack;
5. current disk bytes equal to committed pack bytes;
6. plan trees binding PASS v2 `freeze-0004`;
7. a non-null authenticated predecessor;
8. exactly eleven generic PACK receipts per pack, all bound to the historical coordinate;
9. only the allowed post-authoring delta;
10. a create-only output path.

The `_v5` path and `SUCCESSOR_PACK_IDS` can be wired now. The loader intentionally ignores an absent enumerated successor, so:

- the refresh lane remains operational on the v1 member;
- selecting the absent `_v5` member explicitly still refuses;
- no new skip should be introduced;
- the existing presence-conditional shape test remains its existing skip until desk-day bytes appear;
- the later R-2 fixation test must be nonconditional and fail on absence, but cannot be installed with a real digest before `hS` exists.

### D. Proposed sessions

#### Session S0-A — identity reparameterization now

Exhaustive `WRITE_SCOPE`:

```json
[
  "configs/arm_readiness/d117_row_registry_v2.json",
  "joulewise/arm_readiness.py",
  "scripts/build_v4_histsem_pinset.py",
  "scripts/build_v4_histsem_pinset.py.sha256",
  "scripts/verify_family_marker.py",
  "scripts/verify_family_marker.py.sha256",
  "docs/contracts/d117_step6_confirmation_table.md",
  "docs/contracts/receipt_histsem_verifier.md",
  "docs/contracts/analysis_plans.md",
  "docs/paper/draft-v1.md",
  "tests/test_d117_decode_contrast_plan.py",
  "tests/test_arm_readiness_integration.py",
  "tests/test_arm_readiness_registry.py",
  "tests/test_arm_readiness_schemas.py",
  "tests/test_arm_readiness_lifecycle.py",
  "tests/test_arm_readiness_dry_run.py",
  "tests/test_arm_readiness_evidence_author.py",
  "tests/test_launch_window.py",
  "tests/test_family_marker.py",
  "tests/test_receipt_histsem.py",
  "tests/test_paper_build.py"
]
```

Do not include the builder rename, kernel, historical traces, recorded fixture, generator, or successor pinset bytes.

Tool sidecars must be generated after the changed tool blobs are committed:

```sh
python3 scripts/refresh_receipt_histsem_pinset.py \
  --repository-root . \
  --refresh-tool-sidecars
```

Acceptance:

```sh
python3 -m unittest \
  tests.test_arm_readiness_schemas \
  tests.test_arm_readiness_registry \
  tests.test_arm_readiness_integration \
  tests.test_arm_readiness_lifecycle \
  tests.test_arm_readiness_dry_run \
  tests.test_arm_readiness_evidence_author \
  tests.test_family_marker \
  tests.test_receipt_histsem \
  tests.test_launch_window \
  tests.test_d117_decode_contrast_plan \
  tests.test_paper_build
python3 scripts/verify_receipt_histsem.py --repository-root .
python3 -m unittest discover -s tests
```

Mutation requirements:

| Counterfactual | Production call site | Expected refusal/failure | Positive coherent row |
|---|---|---|---|
| `family_id = d117-v4` with otherwise-v5 marker | `validate_family_publication_marker` | `marker_schema_mismatch` | Family `d117-v5`, generation 5, exact Qwen3 roster passes. |
| Marker generation remains 4 | `_gate_family_publication` → marker validator | `marker_schema_mismatch` | Registry threshold and marker generation both 5 pass. |
| One Qwen2.5/v4 member remains | marker validator | `roster_mismatch` | ALPHA/BETA/GAMMA exact v5 projection passes. |
| Confirmation names old family, marker, or pinset | `validate_step6_confirmation_table` | `confirmation_mismatch` | One exact v5 table passes. |
| Stale v4 allowlist path attempts subtraction | `validate_r1_evidence_lifecycle` | `readiness_r1_dependency_changed_set` | Exact v5 path plus valid digest-conditional confirmation clears that edge. |
| Explicit selector uses old v4 pinset path | `_load_histsem_pinset` / verifier CLI | `histsem_pinset_invalid` | A temporary enumerated v5 member loads successfully. |
| Synthetic live v5 pack supplies a fabricated or absent v4 predecessor | `generate_freeze_receipt` | `readiness_successor_chain_invalid` | A coherent v5 pack authenticated against the ruled v3 predecessor reaches PASS `freeze-0004`. |
| Verifier failure receipt still reports `d117-v4` | `scripts/verify_family_marker.py:main` | assertion failure in CLI regression | Both refusal branches report `d117-v5`. |

#### Session S0-B — desk-day pack and pinset materialization

Starts only after G2-a selection and prompt pin issuance.

Exhaustive `WRITE_SCOPE`:

```json
[
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/**",
  "configs/campaigns/d117_floor_qwen3-8b_v5/**",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/**",
  "configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json"
]
```

Generator commands, using the issued desk-day variables:

```sh
export PREFILL_LENGTH="$(/usr/bin/jq -er \
  '.collection_prefill_tokens' \
  "$G2A_TRANSCRIPT_ROOT/d166-prefill-selection.json")"

python3 configs/campaigns/d117_contrast_v5/generate_configs.py \
  --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b \
  --model-b qwen3-8b \
  --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$PREFILL_LENGTH" \
  --prefill-prompt-pin "$PREFILL_PROMPT_PIN"

python3 configs/campaigns/d117_contrast_v5/generate_configs.py \
  --check \
  --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b \
  --model-b qwen3-8b \
  --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$PREFILL_LENGTH" \
  --prefill-prompt-pin "$PREFILL_PROMPT_PIN"
```

After evidence authoring, U11, and all three committed PASS freezes:

```sh
python3 scripts/build_v4_histsem_pinset.py \
  --repository . \
  --base-pinset configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json \
  --historical-head "$EVIDENCE_DERIVATION_HEAD" \
  --current-head "$(git rev-parse HEAD)" \
  --pack-root configs/campaigns/d117_floor_qwen3-1p7b_v5 \
  --pack-root configs/campaigns/d117_floor_qwen3-8b_v5 \
  --pack-root configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5 \
  --output configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json

python3 scripts/verify_receipt_histsem.py \
  --repository-root . \
  --pinset configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json

python3 -m unittest tests.test_receipt_histsem tests.test_family_marker
python3 -m unittest discover -s tests
```

Mutation requirements:

| Counterfactual | Production call site | Expected refusal | Positive coherent row |
|---|---|---|---|
| Missing prefill length | `configure_model_pair` | `prefill_length_unresolved` | One selected ladder value plus matching prompt pin generates/checks. |
| Missing or wrong prompt pin | `configure_model_pair` | `prefill_prompt_pin_unresolved` or pin-specific mismatch | Issued v2 prompt pin passes. |
| Pack-root set omits or substitutes a roster member | histsem builder `build` | `histsem_pinset_invalid` | Exact three-pack Qwen3 roster builds. |
| Historical head already contains authoring custody | builder `_row` | `histsem_pinset_invalid` | Projection-only historical coordinate passes. |
| Plan tree binds the wrong freeze path/status/schema | builder `_row` | `histsem_pinset_invalid` | PASS v2 `freeze-0004` with predecessor passes. |
| A pack binds 10 or 12 generic receipts | builder `_row` | `histsem_pinset_invalid` | Eleven per pack yields 33 total. |
| Existing output is overwritten | builder create-only write | `histsem_pinset_invalid` | First creation succeeds; replay refuses without mutation. |
| Pinset has a stale v4 ID/path | chain loader/verifier | `histsem_pinset_invalid` or downstream membership refusal | Canonical three-row v5 pinset verifies and activates the existing shape test. |

The lead must separately execute the Estate 12 throwaway-clone proof; it is a live desk-day gate, not delegated final verification.

### E. R-8/R-9 disposition

No disagreement with the selected identities or the requirement to land source changes before the `_v5` evidence-derivation head.

Qualifications:

1. R-8 must not be implemented as a repository-wide text replacement. The historical traces, recorded fixture bytes, Qwen2.5 predecessor projection, and deliberate v4/v5 generic-generation tests must remain.
2. The numeric threshold `4 → 5` is a required non-grep coupling.
3. `freeze-0004` does not become `freeze-0005`; it is the next receipt ordinal after the actual `_v3` predecessor.
4. R-9 applies to code, tests, contracts, and runbook machinery. It cannot require the successor pinset bytes before desk day because those bytes derive from the desk-day packs; the allowlist/digest-conditional design exists for that post-head artifact.
5. R-8’s cited hyphenated-pack-ID problem is already corrected at this head: `docs/process/v5-artifact-flow.md:9` uses the canonical underscore form.

## Residual risk

No tests or generator were run in this read-only review. Outside the requested 27-file inventory, `docs/phase_2/window_runbook.md` still contains live-looking `_v4` examples and old checkout paths; classification and replacement should occur in the ruled runbook stream because the `_v5` custody-root spelling remains an Ed question.