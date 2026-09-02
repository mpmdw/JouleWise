```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The sound design is an outcome-blind finalized-manifest attachment of the emitted sidecar’s raw-byte digest; a mint-only patch cannot satisfy the current stage-1 contract.",
  "workspace": {
    "base_requested": "140ec4cc",
    "base_mode": "exact",
    "head_start": "140ec4cc46e59f2764d894dd4b3dae28fc3b7370",
    "head_end": "140ec4cc46e59f2764d894dd4b3dae28fc3b7370",
    "upstream_end": null,
    "branch": "feat/d165-dominance-closeout-core"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "A mint-only sidecar cannot satisfy the closed stage-1 consumer contract",
        "evidence": "The close-out requires manifest.evidence.dominance_replay_sidecar and checks its raw-byte digest (joulewise/dominance_closeout.py:1163-1202, 1328-1348), while finalized-manifest evidence currently permits exactly four roles (joulewise/analysis_manifest_v3.py:1134-1139, 4029-4054).",
        "recommendation": "Add a conditional, outcome-blind D165 attachment path to finalization and include that work in scope."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "The D165 attachment must be versioned/conditional rather than globally added to every historic prospective manifest",
        "evidence": "Prospective validation currently requires exactly four attachment declarations (joulewise/analysis_manifest_v3.py:2714-2761); the frozen v5 generator also emits exactly four (configs/campaigns/d117_contrast_v5/generate_configs.py:121-141).",
        "recommendation": "Permit base-four or base-four-plus-D165 according to the prospective finalization contract; make the v5 generator declare the fifth role."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Stage-2 must refuse partial replay coverage",
        "evidence": "The existing mixed synthetic mint fixture has only decode on the common-mode path and prefill on default (tests/test_mint_floor_artifact_generalized.py:6475-6482), while the close-out requires a four-cell sidecar (docs/contracts/d165_dominance_closeout.md:106-112).",
        "recommendation": "When D165 emission is requested, require four common-mode replay records before any output is written."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/d165-dominance-closeout-core",
          "140ec4cc46e59f2764d894dd4b3dae28fc3b7370"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "feat/d165-dominance-closeout-core"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only design review: no tests were run and no files were modified.",
      "needs": "Implementation round should run focused mint/finalizer/D165 tests and the canonical suite."
    }
  ]
}
```

## Findings

- **F1 (blocker):** Stage 1 already refuses a supplied sidecar unless the finalized manifest seals its path, digest, schema, and identity; current finalization rejects that extra evidence role.
- **F2 (should fix):** Adding a fifth attachment globally would invalidate frozen base-four prospective manifests; make D165 opt-in through the prospective contract and enable it in the v5 generator.
- **F3 (should fix):** D165 emission must reject a partial common-mode census, rather than minting a floor plus an incomplete sidecar.

## Q1 — Call site

`floor_mint_estimator.recompute_comparative_estimate` calls `floor_extraction._common_mode_floor_from_block_inputs` at [joulewise/floor_mint_estimator.py:465](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:465) and [joulewise/floor_mint_estimator.py:545](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:545). The human path is:

`script main` [scripts/mint_floor_artifact_generalized.py:4067](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4067) → `mint_multi_cell_floor_artifact` [3843](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3843) → active body [3889](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3889) → `_build_v2_artifacts` [3937](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3937) → `_v2_gate_postcollection` [2963](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:2963) → recomputation [2441](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:2441).

It is authenticated: the CLI opens `V2AuthenticationReadSession` [4072-4094](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4072), checks actual HEAD and a clean tree [3904-3910](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3904), reopens launch receipts [joulewise/floor_mint_estimator.py:330](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:330), and requires a ready authenticated common-mode session [413-462](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:413). The floor is evidence-bound before write [scripts/mint_floor_artifact_generalized.py:3989](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3989).

Today the shared writer emits only floor JSON and the convenience single-count statement [scripts/mint_floor_artifact.py:1963](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact.py:1963)-[1989](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact.py:1989); the generalized mint calls it at [4023-4028](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4023). That is the natural place for a third exclusive output. The floor SHA becomes authenticated later, in finalization [joulewise/analysis_manifest_v3.py:3575](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3575)-[3654](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3654).

## Q2 — Hash binding

Recommend **(ii)**: an outcome-blind finalized-manifest attachment sealing sidecar `path`, raw-byte `sha256`, `schema_version`, and `sidecar_id`, exactly as the contract requires [docs/contracts/d165_dominance_closeout.md:213](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:213)-[234](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:234).

(i) is not the current schema: the sidecar permits exactly `schema_version`, `sidecar_id`, and `cells` [docs/contracts/d165_dominance_closeout.md:100](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:100)-[112](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:112), and the mint cannot know a finalized-manifest hash. (iii) is not consumed by the builder and has no manifest-authenticated back-link.

This does not breach D-168’s fence if finalization reads only the sidecar header/identity and raw bytes for hashing—never `ratio`, `passes`, replay result, or branch. The present stage-1 validator explicitly expects this attachment [joulewise/dominance_closeout.py:1163](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1163)-[1202](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1202), while independently sealing floor bytes against `evidence.aggregate_floor_artifact.sha256` [1205-1226](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1205). `validate_d165_closeout` consumes the three exact byte channels [1385-1405](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1385) and runs both checks [1536-1548](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1536).

## Q3 — Ordering

The floor is produced first: the mint writes it at [scripts/mint_floor_artifact_generalized.py:4023](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4023)-[4028](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4028). Later, `scripts/finalize_analysis_manifest.py` takes the floor path [37](/Users/edr/code/JouleWise-wt-closeout/scripts/finalize_analysis_manifest.py:37) and invokes finalization [45-54](/Users/edr/code/JouleWise-wt-closeout/scripts/finalize_analysis_manifest.py:45); finalization writes the manifest only after authenticating the floor [joulewise/analysis_manifest_v3.py:3854](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3854)-[3884](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3884).

Therefore the sidecar needs neither a finalized-manifest hash nor a manifest-identity field. It has the stable block identities already: the mint’s spec emits `block_id` [scripts/mint_floor_artifact.py:1432](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact.py:1432)-[1469](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact.py:1469), and finalization later copies frozen `block_ids` into the finalized manifest [joulewise/analysis_manifest_v3.py:3694](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3694)-[3697](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3697). The reverse manifest attachment is the correct binding.

## Q4 — Byte identity proof

Use a before/after test in `test_common_mode_full_cli_path_writes_bound_exact_artifact` [tests/test_mint_floor_artifact_generalized.py:6563](/Users/edr/code/JouleWise-wt-closeout/tests/test_mint_floor_artifact_generalized.py:6563), with an all-common-mode variant of its authenticated fixture. Mint once without the sidecar request and once with it, then assert:

`self.assertEqual(floor_without.read_bytes(), floor_with.read_bytes())`

and equal SHA-256 values, plus a valid single sidecar. `install_synthetic_finalization_fixture` is useful for finalizer-attachment tests, but it constructs its floor directly with `build_floor_artifact` [tests/test_analysis_finalizer.py:511](/Users/edr/code/JouleWise-wt-closeout/tests/test_analysis_finalizer.py:511)-[524](/Users/edr/code/JouleWise-wt-closeout/tests/test_analysis_finalizer.py:524), so it cannot prove mint byte preservation.

## Q5 — Adapter exclusivity

Use a production-source contract test. Scan only `joulewise/` and `scripts/`: permit the adapter definition in `joulewise/dominance_closeout.py` [335-408](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:335), require exactly one non-definition call in `floor_mint_estimator.py`, and forbid raw block-record literals such as `derived_split`, `onset_sweep_j`, and `member_window_bounds_s` outside `dominance_closeout.py`.

This catches the likely failure: a later mint helper hand-builds a `derived_split` record and bypasses the adapter, even though its output happens to validate today. An import-graph assertion cannot catch that bypass; a private constructor does not prevent handwritten dicts.

## Q6 — Scope and confinement

`floor_extraction.py` must not change: the call site is the mint estimator, not extraction ([joulewise/floor_mint_estimator.py:545](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:545)). Keep the hook immediately after this call, returning replay material to the existing mint flow; preserve all extraction and detection-floor numeric code. Prove confinement with the before/after byte assertion and `git diff --exit-code -- joulewise/floor_extraction.py joulewise/detection_floor.py joulewise/dominance_closeout.py`.

`analysis_manifest_v3.py` must change, but only to declare/authenticate/project the identity-only attachment; it must not inspect outcome fields. Do not touch historic campaign packs, `TASK_QUEUE.md`, `RUN_STATE.md`, or the close-out builder.

## Recommended design

- Emit D165 only in the generalized v2 mint, with a required distinct replay-output path for the D165 mode.
- Capture block IDs, deltas, and `_CommonModeBlockInputs` immediately at the call site.
- Call `d165_replay_blocks_from_mint_inputs` exactly once per comparative cell; never hand-build blocks.
- Refuse D165 mode unless all four cells have common-mode replay material.
- Render the sidecar separately; retain floor serialization and bytes unchanged.
- Extend the shared exclusive writer to preflight and write floor, statement, and sidecar as one output set.
- Make v5 prospectively declare the D165 attachment; preserve base-four legacy manifests.
- Finalization seals only sidecar path/digest/schema/identity; no outcome parsing or validation.
- Let stage-1 perform full replay/outcome validation from the three byte streams.

## Proposed WRITE_SCOPE

```json
[
  "joulewise/floor_mint_estimator.py",
  "scripts/mint_floor_artifact.py",
  "scripts/mint_floor_artifact_generalized.py",
  "joulewise/analysis_manifest_v3.py",
  "scripts/finalize_analysis_manifest.py",
  "scripts/check_window_provenance.py",
  "configs/campaigns/d117_contrast_v5/generate_configs.py",
  "tests/test_mint_floor_artifact.py",
  "tests/test_mint_floor_artifact_generalized.py",
  "tests/test_analysis_manifest_v3.py",
  "tests/test_analysis_finalizer.py",
  "tests/test_check_window_provenance.py",
  "tests/test_d117_contrast_v5_pack.py",
  "tests/test_d165_dominance_closeout.py",
  "tests/test_d165_sidecar_emission.py",
  "docs/contracts/d165_dominance_closeout.md"
]
```

## Q7 — Ranked residual risks

1. The four-versus-five attachment-contract transition is the highest risk: a global fifth role corrupts validation of frozen historic prospective manifests, while no fifth role leaves stage 1 unsatisfied. 2. The existing mixed fixture proves generic v2 minting may not have four common-mode cells, so D165 must fail closed on incomplete replay coverage. 3. A third output worsens the existing partial-write/rollback surface; preflight all paths and clean up on write failure. 4. A finalizer that calls full sidecar validation would silently violate outcome blindness, so test that it accepts and hashes outcome-bearing bytes without interpreting them.