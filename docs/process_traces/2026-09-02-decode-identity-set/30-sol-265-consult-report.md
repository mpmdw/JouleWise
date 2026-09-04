# Sol 265 (gpt-5.6-sol xhigh, read-only, wt-decode-id3 @ e3f52884) — design consult report on packet 29

Custodied verbatim from the seat's report file (scratchpad paths redacted).

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S1/S2/S3 are first-round should-fixes: adopt digest-preserving re-rooting, common-profile-only plan metadata, and a corrected—not verbatim—S1 paragraph; no rule-11 cold gate is triggered.",
  "workspace": {
    "base_requested": "e3f52884",
    "base_mode": "exact",
    "head_start": "e3f5288499d8f24ff25ae39540c884a2221fdaaf",
    "head_end": "e3f5288499d8f24ff25ae39540c884a2221fdaaf",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 3,
      "nit": 0
    },
    "findings": [
      {
        "id": "S3",
        "severity": "should_fix",
        "title": "Adopt option (a), but a floor-gate-only re-root is insufficient because bundle-lineage replay resolves the old absolute pack root first"
      },
      {
        "id": "S2",
        "severity": "should_fix",
        "title": "Remove the ruled decode prompt literal and leave the shared plan-tree workload as the common profile alone"
      },
      {
        "id": "S1",
        "severity": "should_fix",
        "title": "Correct the contract denial, but do not land the dictated replacement verbatim because its execution order is false"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=<scratchpad>/tmp265 python3 -B -m unittest -v tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 47 tests in 8.123s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 47 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json",
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
        "tail_regex": "^1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n 'stack_scope|measurement_arms' joulewise/ scripts/",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": []
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
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
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The S1 dictated paragraph cannot land verbatim, and the S3 brief must include the earlier launch-lineage replay path if clone portability is the intended closure.",
      "needs": "Magistrate should amend those two implementation instructions before the fix round."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The generated-pack floor seam was executed, but no complete moved-custody bundle was constructed through authenticate_bundle_launch_lineage.",
      "needs": "The S3 fix round should add an end-to-end relocated-bundle regression or explicitly limit its portability claim."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No full suite, P-8 pack freeze, hardware operation, or quiet-machine activity was performed.",
      "needs": "Run the prescribed delta re-audit, fresh final-head pass, and lead-owned P-8 closure after merge."
    }
  ]
}
```

## Findings

- **S3 — UPHOLD with expanded integration scope.** Option (a) preserves the ruled digest and identity bindings. However, changing only `_frozen_consumer_identity_set` will not make real moved bundles portable: `_read_bundle` calls `authenticate_bundle_launch_lineage` first (`inputs.py:2773–2782`), and `_replay_consumed_arm` strictly resolves the old arm-recorded `pack_root` at `arm_readiness.py:9333–9352`.

- **S2 — UPHOLD.** The surviving `DECODE_PROMPT_TOKENS["A"]` is the uninstalled R-2 clause. The shared plan-tree field should contain only the genuinely common decode workload.

- **S1 — UPHOLD, but amend the cure.** The current contract falsely denies a manifest-file check. The proposed replacement correctly recognizes that check but reverses actual execution order and incompletely defines its unauthenticated case.

## Q1

### Option

Pick **(a)**, with one integration condition: re-rooting must also apply when authenticated bundle lineage replays the consumed arm, not merely at `inputs.py:3897`.

A trustworthy target is:

1. A Git repository selected from the analysis environment, not from the untrusted absolute prefix.
2. The pack at the authenticated/canonical repository-relative location—preferably `configs/campaigns/<authenticated pack_id>`.
3. A `HEAD` containing that pack.
4. No untracked, missing, symlinked, special, mode-drifted, or byte-drifted entry beneath it.
5. A `committed_pack_tree_sha256` equal to the lineage’s authenticated `pack_sha256`.

The repository root need not—and should not—equal an absolute root recorded in lineage. Requiring that equality recreates the portability defect. The security identities are the canonical relative location and committed-tree digest.

### Executed production-seam evidence

The probe used `_generated_frozen_gate_pack`, `_generated_exact_case`, and `_production_floor_resolution`:

```text
CASE1 recorded_pack_root=<scratchpad>/tmp265/decode-id3-q1-final-g3s49m_2/recorded-checkout/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5
CASE1 status=refused reasons=('consumer_identity_set_unauthenticated',)
CASE2 matching_suffix_copy=<scratchpad>/tmp265/decode-id3-q1-final-g3s49m_2/second-checkout/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5 exists=True
CASE2 recorded_pack_root_still=<scratchpad>/tmp265/decode-id3-q1-final-g3s49m_2/recorded-checkout/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5
CASE2 status=refused reasons=('consumer_identity_set_unauthenticated',)
CASE2 copy_digest=readiness_pack_not_committed: Git proof failed: fatal: not a git repository (or any of the parent directories): .git
CASE3 lineage_points_to_plain_copy status=refused reasons=('consumer_identity_set_unauthenticated',)
CASE4 committed_digest_matches=True
CASE4 status=exact reasons=()
```

Thus:

- A matching-suffix copy is ignored while production follows the recorded missing path.
- Even when lineage points directly at a plain copy, `committed_pack_tree_sha256` cannot authenticate it.
- Once the copy is committed under the same repository-relative path in a Git repository, its tree digest equals the source digest and the existing seam returns `exact`.

### Forgery analysis

Under (a), a consumer gains no ability to substitute different pack semantics:

- A different relative pack is rejected by the suffix/canonical-location check.
- A plain or dirty copy is rejected by `committed_pack_tree_sha256`.
- Different committed paths, modes, lengths, or contents change the digest.
- An identity outside the authenticated frozen set remains rejected by R-6’s subset check.

The only newly accepted state is the same committed pack tree at the same repository-relative location in another checkout. Indeed, Case 4 shows that today’s gate already accepts that tree if the injected lineage is manually pointed at it; (a) makes the absolute-prefix relocation automatic for authenticated lineage.

A production consumer cannot simply forge that prefix: bundle loading compares embedded lineage with its authenticated root locator and replays the consumption/arm chain (`arm_readiness.py:10656–10669`). Even if a prefix mutation reached the re-root algorithm, the prefix would no longer select the target.

The remaining cryptographic counterfactual is a SHA-256 collision yielding different tree bytes under the same digest. That assumption already exists today and is not introduced by (a).

### Upstream integration catch

A patch only at `_frozen_consumer_identity_set` does not deliver fresh-clone analysis. Before constructing `BundleEvidence`, `_read_bundle` authenticates lineage. `_replay_consumed_arm` currently performs:

```text
recorded_pack_root = Path(str(arm["pack"]["pack_root"])).resolve(strict=True)
authenticated_pack = _pack_record(recorded_pack_root)
```

Only afterward does it call `_pack_mapping_mismatch_kind`, whose successor policy already supports repository-relative comparison. The strict resolution prevents that policy from helping when the original path is absent. S3 therefore needs consistent re-rooting at this earlier boundary too.

### Rule 11

Option (a) is an implementation choice inside R-6/F-B, not a reinterpretation. The controlling R-6 sentence is:

> “(a) `inputs.py:3881` — consumer evidence identities must be non-empty and a SUBSET of the frozen consumer unit's declared set (read from the frozen receipt bound by the U8 readiness record); any identity outside the set refuses; the exact-cell route (`:3905-3916`) stays single-identity.”

That sentence fixes the authenticated set and subset verdict, not a machine-absolute locator. F-B fixes the external binding as the lineage digest versus committed-tree digest. Re-rooting retains both.

The biting counterfactual should:

1. Leave authenticated lineage stamped with an unavailable absolute root.
2. Put the identical committed pack at the canonical relative location in a second Git checkout.
3. Require production resolution `exact`/`()`.
4. Change and commit one pack blob while retaining the original lineage digest and require `consumer_identity_set_unauthenticated`.

Restoring `Path(recorded_root).resolve(strict=True)` must kill the positive relocation leg; disabling the digest comparison must kill the negative leg.

## Q2

### Grep for consumers

```text
$ rg -n 'stack_scope|measurement_arms' joulewise/ scripts/
$ echo $?
1
```

There are no consumers under `joulewise/` or `scripts/`. The only repository test hit is the unrelated older-pack inspection at `tests/test_d117_floor_qwen25_7b_plan.py:1141`; it does not interpret this `_v5` nested decode workload.

### Recommendation

`stack_scope.measurement_arms.decode.workload` should carry the **common profile alone**:

```json
{"name":"real_prompts_v1_chat_rendered","output_tokens":512,"repetitions":1,"warmup_runs":1}
```

It should not carry `suite_manifest_set`, because that set is per identity unit and differs between A and B through its manifest references and effective digests. The plan-tree node is shared by both arms. Making it per-arm would duplicate the authoritative per-unit declarations already stored in `identity_pin_projection`, with no consumer requiring that duplication.

Executed with the decode prompt literal removed in memory:

```text
decode_plan_workload={"name":"real_prompts_v1_chat_rendered","output_tokens":512,"repetitions":1,"warmup_runs":1}
registration_bytes_equal=True
registration_sha256=1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b
```

### Digest bytes

`tests.test_d165_dominance_closeout` passed all 47 tests, including `test_generator_imports_shared_core_and_registration_bytes_are_unchanged`.

The pinned digest hashes exactly:

- `PINNED_DOMINANCE_CRITERION_BYTES`;
- 2,032 UTF-8 bytes;
- the compact, sorted-key JSON serialization of `generator.dominance_criterion_registration()`;
- `separators=(",", ":")`, no spaces and no trailing newline;
- first byte `{`, final byte `}`;
- byte-identical to `d166_dominance_criterion_registration.json`.

It does **not** hash `generate_configs.py`, `workload_for`, or `plan_tree.json`. Therefore removing the decode prompt literal and changing only the descriptive plan workload can preserve `1c0a4a…783a2b`.

## Q3

### Clause verification

| Dictated clause | Verdict | Production evidence |
|---|---|---|
| Two kinds of pack bytes are authenticated before declarations are compared | TRUE | Config raw bytes: `_read_unit_configs` at `1592`, implementation `1436–1457`; manifests: `1610–1630`; first declaration comparison: `1635–1654`. |
| Every declared manifest member is visited | TRUE | Member validation and duplicate rejection `1499–1535`; digest-keyed map `1602–1609`; iteration `1610`. |
| Uses the declared `suite_manifest_ref` | TRUE | `1611–1612`. |
| Resolves it as a regular file below the pack root | TRUE in behavior, imprecise prose | `_declared_manifest_path` `1541–1568`; strict below-root resolution and regular non-symlink check `_resolve_config_path` `1245–1258`. “Regular, non-symlink file” would be exact. |
| Recomputes the manifest SHA-256 | TRUE | `1613–1614`. |
| Unreadable manifest refuses with `readiness_identity_environment_dirty` and the stated message | TRUE for file-resolution/read failures | Resolution rewrap `1563–1568`; read failure `1615–1620`. |
| Digest mismatch refuses with the same reason/message | TRUE | `1621–1630`. |
| Manifest refusal occurs “before any configuration is read” | **CONTRADICTED** | `_read_unit_configs` is called at `1592`; it reads each file at `1439`, before `declared_by_manifest` exists. |
| “Second,” config raw bytes are authenticated against inventory digests | Action TRUE; chronology **CONTRADICTED** | The operation is `1436–1451`, invoked first at `1592`. |
| Unauthenticated manifest binding means only bad manifest hash or unmatched config pair | **CONTRADICTED/incomplete** | An unreadable or unresolvable manifest also emits “declared suite manifest is unauthenticated” at `1563–1568` or `1615–1620`, without an observed mismatching hash. |
| The manifest failure is before step 1 | **CONTRADICTED** | The raw-read/digest portion of current step 1 already ran through `1592 → 1436–1451`. |
| The configuration digest/reference-pair failure is step 4 | TRUE | `1657–1670` matches current contract step 4. |

`declared_by_manifest` is built at `1602–1609` before the explicit `for config in configs` declaration-comparison loop at `1635`, but after all configuration files have already been read, hashed, and JSON-parsed at `1592`. The packet’s parenthetical conflates “before the configuration loop” with “before any configuration is read.”

### Freeze-procedure insertion point

Yes, the numbered procedure needs the omitted manifest-file check. It must **not** be inserted before current step 1.

For exact executable ordering, split both the current step 1 and suite branch of step 3:

1. Read each inventory file, compare its raw digest, and JSON-parse it.
2. Validate the declared manifest-set members and derive the declared common profile.
3. **Insert manifest-file resolution/read/digest authentication here.**
4. Type each configuration through `BenchmarkConfig` and perform the declaration/common-profile comparisons.
5. Continue with manifest-pair and census checks.

Textually, the inserted step belongs after current line 458 (“obtain the declared common workload profile”) and before lines 459–462 begin projecting and comparing emitted workloads. Old steps 4–6 must then be renumbered.

### First-use table

| Term in proposed text | First use / prior definition | Result |
|---|---|---|
| `identity projection` | Canonical term `identity-pin projection` is glossed at `3–8`, defined at `16–25` | PASS if canonical spelling is retained |
| `pack root` | `campaign pack` is defined as a directory at `34–35`; exact term “pack root” has no prior definition | FIX: say “campaign-pack directory (the pack root)” |
| `declared suite-manifest member` | Canonical defined term is `declared manifest member`, `90–98` | FIX: use the canonical term |
| `suite_manifest_ref` / `suite_manifest_sha256` | `86–98` | PASS |
| `regular file` | No prior definition | FIX: inline “regular, non-symlink file whose resolved path remains below the pack root” |
| SHA-256 | `22–24` | PASS |
| declaration | `83–85` | PASS |
| configuration inventory / inventory digest | `112–115`, schema detail `309–310`, procedure `451–452` | PASS |
| `readiness_identity_environment_dirty` | Operational use at `421–424`; formal reason table at `728` | Existing fixed literal; locally state “reason code” |
| unauthenticated manifest binding | Defined inline in the proposed paragraph | First-use shape passes, but the definition is factually incomplete |
| step 1 / step 4 | Immediately preceding procedure `451–468` | PASS once renumbering is corrected |

## Q4

No cold gate is required before the fix round.

Rule 11’s relevant triggers are a second fix round on the same defect or reinterpretation of a prior verdict. S1, S2, and S3 are each first-round findings. Option (a) retains the ruled subset verdict and F-B’s committed-tree digest binding; correcting the locator and the earlier replay integration does not reinterpret either.

The acceptable sequence is therefore:

1. Magistrate amends the S1 dictated wording and S3 scope.
2. One Sol fix round for S1/S2/S3.
3. Delta re-audit with the relocation positive/negative counterfactual.
4. Fresh final-head pass.
5. Merge.
6. Lead-owned P-8 regeneration and freeze/verify of all three `_v5` packs.

## Residual risk

The helper-based production-floor probe starts with already-constructed `BundleEvidence`. Source inspection found the earlier absolute-root dependency, but this pass did not execute a fully authenticated moved bundle with consumption, arm, locator, and lifecycle receipts. That end-to-end test is necessary before claiming clone portability rather than only floor-seam portability.

## What this pass did NOT check

- No full test suite or `unittest discover`.
- No mutation testing or implementation patch.
- No real P-8 regeneration/freeze.
- No hardware, measurement, network, or quiet-Mac operation.
- No installed-wheel/non-checkout analysis scenario; option (a) necessarily requires a Git checkout capable of proving the committed pack tree.
- No independent audit of unrelated Opus nits S4–S7.