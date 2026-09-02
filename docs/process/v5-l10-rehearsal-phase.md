# `_v5` L10 sacrificial rehearsal — ladder phase

## A. Purpose, authority, and terms

The adopted L10 schedule says that the sacrificial rehearsal re-runs the full
edge at the same head before a window is spent; its authorized close is a
same-HEAD, production-pack replay ([decision log:9156–9158](../decision_log.md#L9156),
[decision log:9176–9178](../decision_log.md#L9176)).

The historical ruled item 2 said, “Use production writers/validators to create
a synthetic exact-80-member corpus.” D-160 F-1 proved that formulation
unexecutable on merged code, because no synthetic bundle can become
claim-consumable without a production-code change; ruling 89 R-1 therefore
replaces it with the real-corpus ladder below
([D-160 F-1](../process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md#L10),
`docs/process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md:39-58`).

ED-L10-1 was never executed and has no closure record, so retained a9/a10
custody is not an L10 corpus source ([ROW-L10:501](
../process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L10.md#L501)).

- The **claim edge** is the ordered `_v5` artifact-flow sequence: Strict
  validation, Reduction, Floor extraction, Mint, Finalization, Claim gate, and
  Results fills ([artifact flow](v5-artifact-flow.md),
  `89-RULING-l10-corpus-precondition.md:39-58`).
- A **production pack** is the authenticated `_v5` configuration directory,
  including its prospective manifest and plan tree, at the transaction head
  ([kernel fence](state_kernel.json#L1927), [decision log:9176–9178](../decision_log.md#L9176)).
- The **transaction head** is the Git commit recorded as
  `transaction_head_git_sha`; a same-head check compares the checkout's
  `git rev-parse HEAD` output with that value ([ruling 89 R-5](
  ../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80)).
- **Custody** is the append-only, outside-repository directory holding the
  authenticated inputs, outputs, transcripts, and hashes for this work
  ([transaction custody](../process_traces/2026-08-22-t20/real-transaction-runbook.md)).
- A **scratch custody copy** is a disposable copy below
  `$L10_CUSTODY_ROOT`; finalization writes there instead of to a source
  custody directory ([G2-b F2](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md#L1124)).
- **Sacrificial** means qualification evidence, not campaign claim evidence.
  `QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE` is a new literal for this phase,
  rather than a token inherited from the ALPHA rehearsal card
  ([ruling 89 R-5](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80)).
- A **spent window** is the `[QUIET-MAC]` collection for the claim-bearing
  transaction night; D-167(1) distinguishes diagnostic windows at lead
  discretion from the transaction on Ed's GO
  ([D-167(1)](../decision_log.md#L10407)).

The ladder uses three physical corpora. The **G2-b shakedown corpus** is one
real A/B/B/A block on its own non-claim root. The **floor-producer corpus** is
the real corpus collected by the transaction's ALPHA and BETA floor arms. The
**campaign corpus** is the complete claim-bearing corpus after its last
consuming arm. Ruling 89 R-1 assigns these distinct roles
(`89-RULING-l10-corpus-precondition.md:39-58`).

## B. FIRST CHECKS

**FIRST CHECK** means a named production artifact or adapter whose presence is
checked before the affected ladder part begins. These checks and the per-step
head check are this phase's own refusals ([ruling 89 R-5](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80)).

| Required input or adapter | Exact `rg` probe | Owner | Passing observation |
|---|---|---|---|
| `_v5` extraction spec, `joulewise.detection_floor_extraction_spec.v1` | `rg -n 'detection_floor_extraction_spec' configs/campaigns/d117_contrast_v5` | needs an owner row | A match identifies `$EXTRACTION_SPEC`. |
| `_v5` final pinset and v2 input manifest | `rg -n 'joulewise\.(floor_mint_pinset|floor_mint_inputs)\.v2' configs/campaigns/d117_contrast_v5` | needs an owner row | Matches identify `$FINAL_PINSET` and `$V2_INPUT_MANIFEST`. |
| Mint-artifact adapter for `dominance_ratio`, `replay_common_mode_dominance`, or `R_cm` | `rg -n 'dominance_ratio|replay_common_mode_dominance|R_cm' joulewise scripts` | `D165-SIDECAR-EMIT-01` | A production call site reads the issued floor artifact and emits the bound close-out artifact. |
| `joulewise.claim_verdicts.v1` to `joulewise.results_fill_input.v1` adapter | `rg -n 'claim_verdicts|claim-verdict' scripts --glob '*.py'` | `RENDERER-V5-SUCCESSOR-01` | A successor call site outside the frozen renderer produces the fill input. |

A missing input, owner, or required match is **BLOCKED** for the affected part;
do not substitute fixtures, smoke artifacts, or an older generation
([ruling 89 R-5](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80),
[kernel fence](state_kernel.json#L1927)). The missing G2-a config producer is
outside this phase because it precedes pack generation
([ruling 89 R-5](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80)).

## C. Execution record

### C1. Fixed inputs, custody, and lane

Set the durable roles at the reviewed transaction head. `RUNS_ROOT` is set
before L10-A; `PRODUCER_RUNS_ROOT` and `CAMPAIGN_RUNS_ROOT` are set when their
respective post-collection parts begin.

```sh
export REPO='/absolute/path/to/the-production-checkout'
export PY="$REPO/.venv/bin/python"
export CAMPAIGN_ROOT='/absolute/path/to/the-v5-transaction-custody'
export ANALYSIS_ROOT="$CAMPAIGN_ROOT/analysis"
export CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"
export CLAIMS_ROOT="$CAMPAIGN_ROOT/claims"
export L10_CUSTODY_ROOT="$CUSTODY_ROOT/l10-sacrificial-rehearsal"
export PACK_ROOT="$REPO/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
export RUNS_ROOT='/absolute/path/to/the-G2-b-shakedown-runs-root'
export REDUCTION_ROOT="$L10_CUSTODY_ROOT/reductions"
export REHEARSAL_RECORD="$L10_CUSTODY_ROOT/l10-sacrificial-rehearsal-record.json"
export EXTRACTION_SPEC='/absolute/path/from-FIRST-CHECK-1'
export FINAL_PINSET='/absolute/path/from-FIRST-CHECK-2'
export V2_INPUT_MANIFEST='/absolute/path/from-FIRST-CHECK-2'
export CALIBRATION_LEDGER='/absolute/path/to/the-transaction-selected-ledger.jsonl'
export EVIDENCE_ROOT_ID='declared-floor-producer-evidence-root-id'
export RESULTS_FILL_INPUT='/absolute/path/from-FIRST-CHECK-4'
cd "$REPO"
export TRANSACTION_HEAD="$(/usr/bin/git rev-parse HEAD)"
export PROJECT_COMMIT="$TRANSACTION_HEAD"
test -z "$(/usr/bin/git status --porcelain=v1 --untracked-files=all)"
test "$TRANSACTION_HEAD" = "$(/usr/bin/git rev-parse refs/heads/main)"
test "$TRANSACTION_HEAD" = "$(/usr/bin/git rev-parse refs/remotes/origin/main)"
test -d "$PACK_ROOT/arm_readiness.freeze.receipts"
export PACK_SHA256="$("$PY" -c 'import sys; from joulewise.arm_readiness import committed_pack_tree_sha256; print(committed_pack_tree_sha256(sys.argv[1]))' "$PACK_ROOT")"
test ! -e "$L10_CUSTODY_ROOT"
/bin/mkdir -p "$L10_CUSTODY_ROOT/transcripts" "$REDUCTION_ROOT"
```

`RUNS_ROOT` is the G2-b shakedown runs root: real, strict-valid, same-head
telemetry from the authenticated `_v5` contrast pack, with one A/B/B/A block
and `bracket-binding.json` before `whole-window-verdict.json` beneath that root
in NR-14 order. It is qualification-only, and ruling 89 R-1 keeps the L10-A read
byte-unchanged while recording its tree hash before and after
([G2-b acceptance](state_kernel.json#L4883), [ruling 89 R-1 and R-2](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).

`PRODUCER_RUNS_ROOT` is the separate floor-producer corpus collected by the
transaction's ALPHA and BETA arms. It does not exist pre-window and is used by
L10-B only, while `CAMPAIGN_RUNS_ROOT` is the complete campaign corpus used by
L10-C ([ruling 89 R-1](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).

No synthetic or smoke-scoped corpus discharges this phase: the kernel fence
requires the same head and production pack, and D-160 R-1 prohibits a
synthetic clean leg ([kernel fence](state_kernel.json#L1927), [D-160 R-1](
../process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md#L50)).

Before L10-A, write the G2-b tree hash to
`$L10_CUSTODY_ROOT/g2b-tree-before.sha256`; repeat the same command after its
finalization check, write `g2b-tree-after.sha256`, and compare the two files.
A changed hash is **FAIL** ([ruling 89 R-2](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L60)).

```sh
g2b_tree_hash() {
  /usr/bin/find "$RUNS_ROOT" -type f -exec /usr/bin/shasum -a 256 {} + |
    LC_ALL=C /usr/bin/sort | /usr/bin/shasum -a 256
}
g2b_tree_hash > "$L10_CUSTODY_ROOT/g2b-tree-before.sha256"
```

Before each numbered command, run
`test "$(/usr/bin/git rev-parse HEAD)" = "$TRANSACTION_HEAD"`; a mismatch is
this phase's own refusal ([ruling 89 R-5](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80)).

Every L10 command is **BENCH**: the magistrate executes it at the bench with
no `sudo`, no `[QUIET-MAC]` collection, and writes only below
`$L10_CUSTODY_ROOT` ([ruling 89 R-4](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L74)).
**BOUNDARY-PROVEN** means the command shape and fail-closed boundary already
exist in the governed flow and tests ([artifact flow](v5-artifact-flow.md)).

### C2. The three-part ladder

#### L10-A — pre-window G2-b contract prefix

L10-A runs steps 1, 2, and 5 before the claim-bearing window. It gates
`V5-TRANSACTION-01` but does not close the whole L10 row
([ruling 89 R-1](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).

1. **Strict validation — L10-A / BENCH / BOUNDARY-PROVEN.** For each
   manifest-declared `$RUN_ID`, run:

   ```sh
   "$PY" -m joulewise validate-bundle "$RUNS_ROOT/$RUN_ID" --strict \
     >> "$L10_CUSTODY_ROOT/transcripts/l10-a-strict-validation.txt"
   ```

   Record the input paths and SHA-256 digests with the transcript. A missing or
   strict-invalid member is **FAIL** ([artifact flow:12](v5-artifact-flow.md#L12)).

2. **Reduction — L10-A / BENCH / BOUNDARY-PROVEN.** For each strict-valid
   `$RUN_ID`, run:

   ```sh
   "$PY" -m joulewise reduce "$RUNS_ROOT/$RUN_ID" \
     --output "$REDUCTION_ROOT/$RUN_ID.summary_metrics.rereduced.json"
   ```

   A missing, overwritten, or in-bundle output is **FAIL**
   ([artifact flow:13](v5-artifact-flow.md#L13)).

5. **Finalization exact refusal — L10-A / BENCH / BOUNDARY-PROVEN.** Make the
   scratch directory below `$L10_CUSTODY_ROOT`, then run the G2-b checker on
   its scratch custody copy:

   ```sh
   export L10_A_SCRATCH_ROOT="$L10_CUSTODY_ROOT/l10-a-scratch"
   /bin/mkdir -p "$L10_A_SCRATCH_ROOT"
   "$PY" scripts/check_window_provenance.py --expect-finalize-refusal \
     --scratch-dir "$L10_A_SCRATCH_ROOT" \
     --prospective-manifest "$CUSTODY_ROOT/prospective/analysis_manifest_v3.json" \
     --plan-tree "$CUSTODY_ROOT/prospective/plan_tree.json" \
     --custody-root "$CUSTODY_ROOT" \
     --runs-root "$RUNS_ROOT" \
     --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" \
     --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
     --calibration-ledger "$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl" \
     --aggregate-floor-artifact "$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json" \
     --output-dir "$CUSTODY_ROOT" \
     > "$L10_CUSTODY_ROOT/transcripts/l10-a-finalization.txt"
   g2b_tree_hash > "$L10_CUSTODY_ROOT/g2b-tree-after.sha256"
   /usr/bin/cmp "$L10_CUSTODY_ROOT/g2b-tree-before.sha256" \
     "$L10_CUSTODY_ROOT/g2b-tree-after.sha256"
   ```

   The checker copies the source custody into `$L10_A_SCRATCH_ROOT` before it
   invokes the finalizer; the source custody paths in the command are read
   inputs ([G2-b F2](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md#L1124)).

   L10-A **PASS** is the singleton observed reason
   `analysis_finalization_member_cover_mismatch` ([ruling 89 R-1](
   ../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).
   Any other reason, a successful
   finalization, a nonzero tree comparison, or a write outside L10 custody is
   **FAIL** (`joulewise/analysis_manifest_v3.py:2590,2598`,
   [current finalizer member-cover branch:2986,3048](../joulewise/analysis_manifest_v3.py#L2986),
   [G2-b F2](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md#L1124),
   [ruling 89 R-1 and R-2](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).

#### L10-B — floor-producer extraction and rehearsal mint

L10-B runs steps 3 and 4 after the ALPHA/BETA floor arms and immediately before
the real production extraction and mint. Copy the real floor-producer corpus
to a scratch directory below `$L10_CUSTODY_ROOT` before step 3
([ruling 89 R-1](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L50)).

```sh
export PRODUCER_RUNS_ROOT='/absolute/path/to/the-real-floor-producer-corpus'
export L10_B_PRODUCER_SCRATCH="$L10_CUSTODY_ROOT/l10-b-scratch/producer-runs"
/usr/bin/ditto "$PRODUCER_RUNS_ROOT" "$L10_B_PRODUCER_SCRATCH"
```

3. **Floor extraction — L10-B / BENCH / BOUNDARY-PROVEN.** Set
   `COLLECTION_MANIFEST_ID`, `EVALUATION_BASIS_SHA256`, and
   `CONSUMPTION_SEMANTICS_ID` from the authenticated inputs, then run:

   ```sh
   export EXTRACTION_REPORT="$L10_CUSTODY_ROOT/l10-b-floor-extraction.json"
   "$PY" scripts/extract_detection_floors.py \
     --runs-root "$L10_B_PRODUCER_SCRATCH" --spec "$EXTRACTION_SPEC" \
     --out "$EXTRACTION_REPORT" --manifest-id "$COLLECTION_MANIFEST_ID" \
     --evaluation-basis-sha256 "$EVALUATION_BASIS_SHA256" \
     --consumption-semantics-id "$CONSUMPTION_SEMANTICS_ID" --hash-bundles
   ```

   An absent report is **FAIL** ([artifact flow:14](v5-artifact-flow.md#L14)).

4. **Mint — L10-B / BENCH / BOUNDARY-PROVEN.** Set
   `FINAL_PINSET_SHA256` and `CALIBRATION_CUSTODY_STORE` from the authenticated
   inputs, then run:

   ```sh
   export AGGREGATE_FLOOR_ARTIFACT="$L10_CUSTODY_ROOT/l10-b-aggregate-floor.json"
   export SINGLE_COUNT_STATEMENT="$L10_CUSTODY_ROOT/l10-b-single-count.txt"
   "$PY" scripts/mint_floor_artifact_generalized.py \
     --pinset "$FINAL_PINSET" --pinset-sha256 "$FINAL_PINSET_SHA256" \
     --v2-input-manifest "$V2_INPUT_MANIFEST" \
     --calibration-custody-store "$CALIBRATION_CUSTODY_STORE" \
     --out "$AGGREGATE_FLOOR_ARTIFACT" --single-count-out "$SINGLE_COUNT_STATEMENT" \
     --project-commit "$PROJECT_COMMIT" --project-tree-state clean \
     --consumption-semantics-id "$CONSUMPTION_SEMANTICS_ID"
   ```

   A missing output, output-exists refusal, dirty-tree acceptance, or pin/input
   mismatch is **FAIL** ([artifact flow:15](v5-artifact-flow.md#L15)).

#### L10-C — full edge on the complete campaign corpus

L10-C runs steps 5, 6, and 7 after the last consuming arm and before a claim is
published. Copy the campaign corpus to scratch custody before finalization
([ruling 89 R-1](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L53)).

```sh
export CAMPAIGN_RUNS_ROOT='/absolute/path/to/the-complete-campaign-runs-root'
export L10_C_RUNS_SCRATCH="$L10_CUSTODY_ROOT/l10-c-scratch/campaign-runs"
export L10_C_ANALYSIS_SCRATCH="$L10_CUSTODY_ROOT/l10-c-scratch/analysis"
/usr/bin/ditto "$CAMPAIGN_RUNS_ROOT" "$L10_C_RUNS_SCRATCH"
/bin/mkdir -p "$L10_C_ANALYSIS_SCRATCH"
```

5. **Finalization positive form — L10-C / BENCH / BOUNDARY-PROVEN.** Run:

   ```sh
   "$PY" scripts/finalize_analysis_manifest.py \
     --prospective-manifest "$PACK_ROOT/analysis_manifest_v3.json" \
     --plan-tree "$PACK_ROOT/plan_tree.json" \
     --custody-root "$L10_C_ANALYSIS_SCRATCH" --runs-root "$L10_C_RUNS_SCRATCH" \
     --whole-window-verdict "$L10_C_RUNS_SCRATCH/whole-window-verdict.json" \
     --bracket-binding "$L10_C_RUNS_SCRATCH/bracket-binding.json" \
     --calibration-ledger "$CALIBRATION_LEDGER" \
     --aggregate-floor-artifact "$AGGREGATE_FLOOR_ARTIFACT" \
     --output-dir "$L10_C_ANALYSIS_SCRATCH"
   ```

   Set `FINALIZED_MANIFEST` to the emitted finalized-manifest path. A missing
   finalized manifest is **FAIL** ([artifact flow:16](v5-artifact-flow.md#L16)).

6. **Claim gate — L10-C / BENCH / BOUNDARY-PROVEN.** Run the governed command
   against the scratch corpus:

   ```sh
   export CLAIM_VERDICTS="$L10_CUSTODY_ROOT/l10-c-claim-verdicts.json"
   "$PY" -m joulewise analyze-claims --analysis-manifest "$FINALIZED_MANIFEST" \
     --runs-root "$L10_C_RUNS_SCRATCH" \
     --evidence-root "$EVIDENCE_ROOT_ID=$PRODUCER_RUNS_ROOT" \
     --floor-artifact "$AGGREGATE_FLOOR_ARTIFACT" --output "$CLAIM_VERDICTS"
   ```

   A crash, an unregistered refusal, or an absent verdict artifact is **FAIL**
   ([artifact flow:17](v5-artifact-flow.md#L17)).

7. **Results fills — L10-C / BENCH / BOUNDARY-PROVEN.** The successor adapter
   supplies `$RESULTS_FILL_INPUT`; then run:

   ```sh
   export RESULTS_FILLS_MD="$L10_CUSTODY_ROOT/l10-c-results-fills.md"
   "$PY" scripts/render_results_fills.py "$RESULTS_FILL_INPUT" > "$RESULTS_FILLS_MD"
   "$PY" scripts/render_results_fills.py --validate-rendered "$RESULTS_FILLS_MD"
   ```

   Missing output, `STOP_FILL`, a leftover fill token, or validation failure is
   **FAIL** ([artifact flow:18](v5-artifact-flow.md#L18)).

### C3. Ratified record and part results

The magistrate must ratify this record contract before execution; that
authorization licenses the part-level **PASS** and **FAIL** rules below
([ruling 89 R-5](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80)).

Use `l10-sacrificial-rehearsal-record.json` at `$REHEARSAL_RECORD`. Each part
record carries the following fields; `proof_scope` identifies the physical
corpus and ladder portion represented by that record. Its permitted values are
`L10_A_G2B_CONTRACT_PREFIX`, `L10_B_FLOOR_PRODUCER`, and `L10_C_FULL_EDGE`
([ruling 89 R-1](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).

```json
{
  "record_type": "L10-SACRIFICIAL-REHEARSAL",
  "evidence_use": "QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE",
  "proof_scope": "L10_A_G2B_CONTRACT_PREFIX",
  "transaction_head_git_sha": "40-hex Git commit",
  "production_pack_path": "repository-relative pack path",
  "production_pack_sha256": "64-hex authenticated pack digest",
  "operator": "magistrate identity",
  "started_at_utc": "RFC 3339 timestamp",
  "completed_at_utc": "RFC 3339 timestamp",
  "part_result": "PASS or FAIL",
  "overall_result": "PASS or FAIL after all three part records",
  "steps": [
    {
      "step": "number and name",
      "result": "PASS or FAIL",
      "command": "exact executed command",
      "input_artifact_sha256": ["64-hex digests"],
      "emitted_artifact_path": ["L10-custody-relative paths"],
      "emitted_artifact_sha256": ["64-hex digests"],
      "exit_code": 0,
      "refusal_or_verdict": "string or null"
    }
  ]
}
```

The L10-A record is **PASS** when steps 1 and 2 succeed, step 5 observes
exactly `analysis_finalization_member_cover_mismatch`, and the two G2-b tree
hashes match ([ruling 89 R-1](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).
Any other finalization reason or a successful finalization is
**FAIL** ([ruling 89 R-1 and R-2](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39),
`joulewise/analysis_manifest_v3.py:2590,2598`,
[current finalizer member-cover branch:2986,3048](../joulewise/analysis_manifest_v3.py#L2986)).

The L10-B record is **PASS** when the scratch-corpus extraction and rehearsal
mint each emit their governed artifacts ([ruling 89 R-1](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L50)).
The L10-C record is **PASS** when
positive finalization, Claim gate, and Results fills each emit their governed
artifacts before publication ([ruling 89 R-1](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L53)).

The ladder reaches overall **PASS** after the three part records pass
([ruling 89 R-1](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).
A head
change, pack-digest change, missing record field, artifact outside L10 custody,
or an unregistered refusal is **FAIL** ([ruling 89 R-1 and R-5](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).

## D. Sequencing

`V5-TRANSACTION-01` carries no L10 clause in the kernel today. Ruling 89 R-1
installs L10-A as a bench kernel edit before the claim-bearing transaction,
places L10-B after the floor arms and before the real mint, and places L10-C
after the last consuming arm and before publication
([V5 transaction acceptance](state_kernel.json#L5022), [ruling 89 R-1](
../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L39)).

For this sequence, “spent window” means the claim-bearing window under D-167(1),
not an earlier diagnostic collection ([D-167(1)](../decision_log.md#L10407)).

## E. Limits and refusals

This phase adds its own refusals: the per-step transaction-head re-check and
the FIRST-CHECK block. It schedules and records those checks; it does not alter
the governed claim edge or repair a missing producer, adapter, or artifact
([ruling 89 R-5](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md#L80),
[kernel L10 fence](state_kernel.json#L1936)).

Preserve a detected defect and route it to its owning kernel row; a defect with
no owner is a request for an owner row, not an L10 repair
([kernel L10 fence](state_kernel.json#L1936)).
