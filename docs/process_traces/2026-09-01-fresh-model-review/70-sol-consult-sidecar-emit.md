```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend manifest-sealed sidecar bytes with identity-only finalization; mint capture belongs in floor_mint_estimator, and the current post-finalization test injection exposes a noncanonical-manifest blocker.",
  "workspace": {
    "base_requested": "140ec4cc",
    "base_mode": "exact",
    "head_start": "140ec4cc46e59f2764d894dd4b3dae28fc3b7370",
    "head_end": "140ec4cc46e59f2764d894dd4b3dae28fc3b7370",
    "upstream_end": "140ec4cc46e59f2764d894dd4b3dae28fc3b7370",
    "branch": "feat/d165-dominance-closeout-core"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "candidate_ii_manifest_attachment",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Current stage-1 tests authenticate a noncanonical finalized manifest",
        "location": "tests/test_d165_dominance_closeout.py:129-145; joulewise/dominance_closeout.py:1290-1312",
        "text": "The test injects dominance_replay_sidecar after production finalization without recomputing manifest_id. The close-out validator checks only that manifest_id is nonempty, so it accepts a finalized manifest that analysis_manifest_v3 would reject as not content-derived. Stage 2 must produce the attachment inside finalization and should make close-out reject a stale content identity."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Candidate ii is already required by the stage-1 consumer",
        "location": "joulewise/dominance_closeout.py:1163-1226; docs/contracts/d165_dominance_closeout.md:213-226",
        "text": "The close-out requires evidence.dominance_replay_sidecar with exact file-byte digest and identity. Candidate i contradicts the closed three-field sidecar top level and provides no back-pointer authenticating the sidecar; a detached digest adds no authenticated authority."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Emission must avoid both duplicate recomputation output and partial three-file issuance",
        "location": "scripts/mint_floor_artifact_generalized.py:3937-4028; joulewise/floor_mint_estimator.py:588-670; scripts/mint_floor_artifact.py:1963-1989",
        "text": "Common-mode recomputation runs during construction and again during binding. Sidecar material should be captured from the construction recomputation only, while binding independently replays it. Floor, statement, and sidecar need one exclusive-write rollback transaction."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch && rg -n \"def recompute_comparative_estimate|_common_mode_floor_from_block_inputs\\(|write_outputs_exclusive\\(|dominance_replay_sidecar|aggregate_floor_artifact.*sha256|def calculate_manifest_id|manifest_id.*calculate_manifest_id\" joulewise/floor_mint_estimator.py scripts/mint_floor_artifact_generalized.py scripts/mint_floor_artifact.py joulewise/analysis_manifest_v3.py joulewise/dominance_closeout.py tests/test_d165_dominance_closeout.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scripts/mint_floor_artifact_generalized.py:4025:        output_core.write_outputs_exclusive(artifact, floor_path, statement_path)",
          "joulewise/analysis_manifest_v3.py:3763:    manifest[\"manifest_id\"] = calculate_manifest_id(manifest)",
          "joulewise/analysis_manifest_v3.py:4131:    if value.get(\"manifest_id\") != calculate_manifest_id(value):"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "analysis_manifest_v3.py:4131:.*calculate_manifest_id"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout tests.test_floor_mint_estimator tests.test_analysis_finalizer",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-closeout']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox exposed no writable temporary directory, so focused unittest execution could not start.",
      "needs": "Lead reruns the focused and canonical suites in the implementation worktree."
    },
    {
      "id": "FL2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Adopt candidate ii as a conditional D165 finalized-evidence attachment while preserving the existing four prospective required attachments.",
      "needs": "Magistrate adjudication before implementation."
    }
  ]
}
```

## Findings

- **F1 — blocker:** The current test helper adds the sidecar attachment after finalization and does not recompute `manifest_id` ([test_d165_dominance_closeout.py:129](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:129)). `calculate_manifest_id` hashes the whole manifest body ([analysis_manifest_v3.py:383](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:383)), and the authoritative validator rejects stale identities ([analysis_manifest_v3.py:4131](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:4131)); the close-out checks only that the supplied ID is nonempty ([dominance_closeout.py:1309](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1309)). Stage 2 must replace this injection with production finalization and add a content-derived-ID check at the close-out boundary.

- **F2 — should-fix:** Candidate (ii) is the only design compatible with stage 1. The consumer already demands `evidence.dominance_replay_sidecar` and checks its exact byte digest and identity ([dominance_closeout.py:1163](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1163)). The contract likewise specifies that attachment ([d165_dominance_closeout.md:213](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:213)).

- **F3 — should-fix:** Sidecar creation must be single-source and issuance atomic. The same estimator recomputation is called during construction ([mint_floor_artifact_generalized.py:2441](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:2441)) and again during evidence binding ([floor_mint_estimator.py:660](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:660)). Only the first should furnish emitted records; the second remains an independent verification replay.

## Q1 — Call site

The mint-specific caller of `floor_extraction._common_mode_floor_from_block_inputs` is `joulewise.floor_mint_estimator.recompute_comparative_estimate` ([floor_mint_estimator.py:465](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:465)); it reconstructs authenticated per-block inputs at line 538 and calls the floor helper at [floor_mint_estimator.py:545](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:545).

The human-run chain is:

1. `scripts/mint_floor_artifact_generalized.py:main` ([line 4067](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4067)).
2. `mint_multi_cell_floor_artifact` ([line 4079](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4079)).
3. `_mint_multi_cell_floor_artifact_active` ([line 3889](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3889)).
4. `_build_v2_artifacts` ([line 3937](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3937)).
5. `_v2_gate_postcollection` ([line 2963](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:2963)).
6. `mint_estimator.recompute_comparative_estimate` ([line 2441](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:2441)).
7. `_common_mode_floor_from_block_inputs` ([floor_mint_estimator.py:545](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_mint_estimator.py:545)).

The generic extraction path also calls that helper from `extract_comparative_cell` ([floor_extraction.py:2766](/Users/edr/code/JouleWise-wt-closeout/joulewise/floor_extraction.py:2766)), but that is not the stage-2 mint call site.

The mint is authenticated today: it requires the claimed commit to equal actual HEAD, requires a clean tree ([mint_floor_artifact_generalized.py:3904](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3904)), authenticates its v2 inputs ([line 3922](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3922)), rebinds each cell to evidence ([line 3989](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:3989)), and validates before writing ([line 4016](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4016)). It authenticates input custody receipts, including pre/post receipt and ledger-head digests ([line 2541](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:2541)), but issues no independent mint receipt or floor-file digest.

Today it writes exactly two files: the floor artifact and a convenience single-count statement. Their payloads and exclusive rollback behavior are at [mint_floor_artifact.py:1963](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact.py:1963). The floor’s exact file digest is issued later, when finalization records `evidence.aggregate_floor_artifact.sha256` ([analysis_manifest_v3.py:3649](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3649)).

The natural registration points are therefore:

- Add `--d165-replay-out` beside `--out` and `--single-count-out` ([mint_floor_artifact_generalized.py:4035](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4035)).
- Pass the third output through the v2 mint APIs.
- Extend the exclusive writer call at [mint_floor_artifact_generalized.py:4025](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4025) into one rollback transaction for floor, statement, and sidecar.

## Q2 — Hash binding

Recommend **candidate (ii): the finalized manifest seals the sidecar’s exact file-byte SHA-256 beside the floor attachment**.

Candidate (i) is not the current schema. The sidecar has exactly `schema_version`, `sidecar_id`, and `cells` ([d165_dominance_closeout.md:100](/Users/edr/code/JouleWise-wt-closeout/docs/contracts/d165_dominance_closeout.md:100); [dominance_closeout.py:65](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:65)). Adding `lineage` would be a schema change, and nothing would authenticate the replaceable sidecar bytes. Candidate (iii) merely relocates the digest without giving it an authenticated parent.

Finalization may hash the raw bytes and read only `schema_version` and `sidecar_id`. It must not invoke `validate_d165_replay_sidecar`, inspect `cells`, or branch on ratios or pass flags. This is identity-only attachment work, analogous to the existing floor digest at [analysis_manifest_v3.py:3575](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3575), and respects the outcome-blind fence.

Stage 1 already expects:

- Exact manifest/floor/sidecar byte channels in `validate_d165_closeout` ([dominance_closeout.py:1385](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1385)).
- A manifest-side sidecar attachment and exact byte digest ([line 1163](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1163)).
- The supplied floor bytes to equal the manifest’s sealed floor digest ([line 1205](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1205)).
- Independent top-level hashes of the finalized-manifest and sidecar bytes ([line 1414](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:1414)).

I recommend keeping the four prospective `required_attachments` unchanged ([analysis_manifest_v3.py:1101](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:1101)). Treat the replay attachment as a conditional D165 finalized-evidence extension: the frozen `dominance_criterion` registration requires it, while historical non-D165 manifests retain their current four-attachment wire.

## Q3 — Ordering

The floor artifact is produced **before** finalization. The mint writes it at [mint_floor_artifact_generalized.py:4025](/Users/edr/code/JouleWise-wt-closeout/scripts/mint_floor_artifact_generalized.py:4025). The separate finalizer CLI later requires that file as `--aggregate-floor-artifact` ([finalize_analysis_manifest.py:37](/Users/edr/code/JouleWise-wt-closeout/scripts/finalize_analysis_manifest.py:37)), reads and hashes it, builds the finalized manifest, calculates its ID ([analysis_manifest_v3.py:3763](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3763)), and finally writes it ([analysis_manifest_v3.py:3884](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:3884)).

The sidecar must not carry the finalized manifest SHA or finalized `manifest_id`. Neither exists at mint time, and `calculate_manifest_id` hashes the manifest body containing the sidecar attachment ([analysis_manifest_v3.py:383](/Users/edr/code/JouleWise-wt-closeout/joulewise/analysis_manifest_v3.py:383)); pointing the sidecar back at that identity creates a digest cycle.

Under the recommended design, the sidecar needs no manifest lineage field. The finalized manifest supplies the authoritative direction of binding: finalized manifest → exact sidecar bytes. If a human-readable mint identity is desired, derive `sidecar_id` from pre-existing mint identities such as the floor `artifact_id` and collection/prospective manifest identity, never from the finalized manifest.

## Q4 — Byte-identity proof shape

Do not use `install_synthetic_finalization_fixture` as the primary mint byte proof: it hand-builds a synthetic floor with `build_floor_artifact` and writes it directly ([test_analysis_finalizer.py:511](/Users/edr/code/JouleWise-wt-closeout/tests/test_analysis_finalizer.py:511)); it does not execute the mint.

Use the actual common-mode mint fixture `freeze_mixed_estimator_v2_pinset` already exercised by `test_common_mode_full_cli_path_writes_bound_exact_artifact` ([test_mint_floor_artifact_generalized.py:6563](/Users/edr/code/JouleWise-wt-closeout/tests/test_mint_floor_artifact_generalized.py:6563)).

Proposed test:

- Name: `test_d165_sidecar_emission_preserves_floor_bytes`.
- Commit the pre-stage-2 `floor_path.read_bytes()` as `tests/goldens/d165_stage2_floor.json`.
- Run the updated mint with `--d165-replay-out`.
- Assert `self.assertEqual(floor_path.read_bytes(), golden_path.read_bytes())`.
- Also assert the sidecar exists, passes `validate_d165_replay_sidecar`, and the existing component hash constants remain unchanged.

Use `install_synthetic_finalization_fixture` separately for the custody test: production finalization must emit the sidecar attachment, its SHA must equal `sha256(sidecar_path.read_bytes())`, and `manifest["manifest_id"] == calculate_manifest_id(manifest)`. Delete the current post-finalization injection helper.

## Q5 — Adapter exclusivity

Use an **AST-based repository guard**, stronger than raw grep.

Scan Python files under `joulewise/` and `scripts/` and reject any dictionary-construction site outside `d165_replay_blocks_from_mint_inputs` containing the distinctive block-producer key set:

`block_id`, `delta_j`, `onset_sweep_j`, `offset_sweep_j`, `zero_point_contrast_j`, `bundle_residual_half_widths_j`, `member_window_bounds_s`, `member_envelope_integral_sum_j`, `derived_split`.

Also assert that the mint path calls `d165_replay_blocks_from_mint_inputs`. The sanctioned adapter already performs the exact construction and split derivation at [dominance_closeout.py:335](/Users/edr/code/JouleWise-wt-closeout/joulewise/dominance_closeout.py:335); the existing tests cover malformed inputs but not exclusivity ([test_d165_dominance_closeout.py:1284](/Users/edr/code/JouleWise-wt-closeout/tests/test_d165_dominance_closeout.py:1284)).

Failure scenario: a future maintainer hand-builds replay blocks in `mint_floor_artifact_generalized.py`, omits `member_envelope_integral_sum_j`, or derives `derived_split` by duplicated arithmetic. The AST test fails with the offending file and line. An import-graph assertion or private function would not detect that copy.

## Q6 — Proposed implementation WRITE_SCOPE

The mint call site is in `joulewise/floor_mint_estimator.py`, not `floor_extraction.py`; therefore `floor_extraction.py` requires no stage-2 edit. `analysis_manifest_v3.py` does require a tightly confined change for identity-only attachment and canonical manifest-ID generation.

```json
[
  "joulewise/dominance_closeout.py",
  "joulewise/floor_mint_estimator.py",
  "joulewise/analysis_manifest_v3.py",
  "scripts/mint_floor_artifact.py",
  "scripts/mint_floor_artifact_generalized.py",
  "scripts/finalize_analysis_manifest.py",
  "tests/test_d165_dominance_closeout.py",
  "tests/test_floor_mint_estimator.py",
  "tests/test_mint_floor_artifact.py",
  "tests/test_mint_floor_artifact_generalized.py",
  "tests/test_analysis_manifest_v3.py",
  "tests/test_analysis_finalizer.py",
  "tests/goldens/d165_stage2_floor.json",
  "tests/goldens/d165_stage2_replay_sidecar.json",
  "docs/contracts/d165_dominance_closeout.md"
]
```

Must not be touched:

- `joulewise/floor_extraction.py`, including `_common_mode_floor_from_block_inputs` and all numeric paths.
- `joulewise/detection_floor.py`.
- `configs/campaigns/d117_contrast_v5/generate_configs.py`.
- `tests/test_d117_contrast_v5_pack.py` and its frozen registration bytes.
- `scripts/floor_mint_pinsets/schema_v2.json` and existing pinset instances.
- `scripts/build_d165_dominance_closeout.py`.
- `TASK_QUEUE.md`, `RUN_STATE.md`, `docs/process/state_kernel.json`, and run reports; those remain lead-owned.

Confinement proof: zero diff in `floor_extraction.py` and `detection_floor.py`; unchanged D165 registration golden; unchanged component hashes; exact floor-byte golden; and focused plus canonical suites.

## Q7 — Additional risks, ranked

**(1)** Highest: the current stage-1 fixture proves acceptance using a noncanonical finalized manifest, so a self-consistent forged manifest/sidecar/close-out chain presently lacks a local content-identity rejection. **(2)** A third output added outside the existing rollback transaction can leave an issued floor without its sidecar, or an orphan sidecar without its floor. **(3)** The mint recomputes common mode twice, creating a risk of emitting twice or selecting the binder replay rather than the original authenticated construction result. **(4)** Evolving the generic four-attachment prospective contract would perturb frozen manifest semantics and `_v5` bytes unnecessarily; use a conditional D165 evidence extension. **(5)** `sidecar_id` currently has only a nonempty-string rule, so deterministic naming and collision refusal should be specified before live custody. **(6)** Reading the full replay validator during finalization would silently breach outcome blindness even if no explicit branch were selected.

## Recommended design

- Adopt candidate (ii): the finalized manifest seals the exact sidecar bytes.
- Keep the sidecar’s closed three-field top level; add no `lineage`.
- Capture replay blocks at the authenticated mint recomputation using only the sanctioned adapter.
- Carry captured records forward; never emit from the binder’s second replay.
- Build and validate one four-cell sidecar before any output write.
- Write floor, statement, and sidecar through one O_EXCL rollback transaction.
- Preserve the floor object and renderer byte-for-byte.
- Make D165 registration require the sidecar at finalization; preserve historical four-attachment manifests.
- Finalization reads only sidecar path, raw bytes, schema, and ID.
- Recompute the finalized manifest ID with the attachment present.
- Make close-out reject a stale/non-content-derived finalized manifest ID.
- Golden-pin both the unchanged floor bytes and the new sidecar bytes.

## Residual risk

Focused tests could not start because the read-only environment exposed no writable temporary directory. The conclusions above are based on source inspection at the exact clean requested head; the implementation round must rerun focused tests and `python3 -m unittest discover -s tests`.