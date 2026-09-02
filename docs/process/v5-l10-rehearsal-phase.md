# `_v5` L10 sacrificial rehearsal — ladder phase

## A. Purpose, authority, and terms

The adopted L10 schedule re-runs the full claim flow at the reviewed Git head
before the claim-bearing window is spent. Its authorized close is a replay at
that same head using the authenticated generated pack
([decision_log.md:9156–9158](../decision_log.md),
[decision_log.md:9176–9178](../decision_log.md)).

The historical item 2 asked for a synthetic exact-80-member directory of run bundles.
D-160 F-1 shows that no synthetic bundle can pass the claim code path without
a production code change ([04-MAGISTRATE-RULING.md:10–17](../process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md));
ruling 89 R-1 therefore replaces that item with the real-corpus ladder below
([89-RULING-l10-corpus-precondition.md:39–45](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

ED-L10-1 was never executed and has no closure record, so the retained a9/a10
append-only evidence directory is not an L10 corpus source ([ROW-L10.md:501](../process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L10.md)).

These definitions precede the procedure:

- **Strict validation** proves a stored summary follows from raw evidence.
- **Reduction** rebuilds the summary without changing the bundle.
- A **floor** is the smallest false effect the instrument can create.
  **Floor extraction** turns registered member cells into false-effect floors;
  **mint** authenticates those inputs and issues one aggregate floor artifact.
- **Finalization** binds post-collection identities without reading an effect
  estimate.
- **Bracket binding** is the file that binds the two calibration endpoints to
  the plan, ledger, and run-bundle directory (the **runs root**) before the verdict. A
  **whole-window verdict**
  is the machine-quiet decision over the full collection interval, carrying its
  evaluation basis and the bundle ids that the finalizer (the code that performs
  finalization) must cover.
  NR-14 is the ratified placement rule: both files live under the runs root and
  are built before H5 step 1 ([SHAKEDOWN-G2-RUNSHEET.md:22](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md),
  [04-MAGISTRATE-RULING.md:103–166](../process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md)).
- A **verdict basis** is the hash-bound set of bundle occurrences, calibration
  bracket identity, and consumption semantics carried by the whole-window
  verdict ([whole_window.py:2237–2242](../../joulewise/whole_window.py)).
- A **member cover** is the exact frozen set of plan members that the verdict
  and evaluation basis must name. The frozen plan has 80 members in ten blocks
  (`N_BLOCKS = 10`, four members per block) ([generate_configs.py:181–182](../../configs/campaigns/d117_contrast_v5/generate_configs.py));
  the finalizer states that the passed basis must cover all 80
  ([analysis_manifest_v3.py:3048–3049](../../joulewise/analysis_manifest_v3.py)).
  G2-b is one A/B/B/A block, hence one of those ten blocks. Refusal at this
  gate is the desired L10-A outcome: it proves custody, frozen semantics,
  verdict-basis, bracket-byte, and ledger-head checks all passed before the
  finalizer discovered that one block cannot cover 80 members
  ([SHAKEDOWN-G2-RUNSHEET.md:1150–1158](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md),
  [89-RULING-l10-corpus-precondition.md:39–49](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).
- A **tree hash** here is SHA-256 over the sorted relative-path/file-digest
  pairs in a directory; it changes when a file byte or relative path changes.
- The **Claim gate** is the final governed code path that computes registered
  contrasts and decides the paper-claim ceiling; **Results fills** are the
  registered paper sentences rendered from its validated inputs. The **claim edge** is the ordered flow in
  [v5-artifact-flow.md](v5-artifact-flow.md): Strict validation, Reduction,
  Floor extraction, Mint, Finalization, Claim gate, and Results fills.
- The **transaction head** is the Git SHA recorded in the rehearsal record;
  the command below compares it with `git rev-parse HEAD`. The **production
  pack** is the authenticated generated `_v5` configuration directory,
  including its prospective manifest and plan tree, at that head.
  The transaction acceptance requires the reviewed head that passed
  G2-b (`state_kernel.json` `/tasks/V5-TRANSACTION-01/acceptance`,
  [decision_log.md:9176–9178](../decision_log.md)).
- **Custody** is the append-only directory outside the repository holding
  authenticated inputs, outputs, transcripts, and hashes. A **custody root**
  is the root passed to a copy-safe checker. A **scratch custody copy** is its
  disposable descendant used for writes; finalization never writes the source
  root ([real-transaction-runbook.md:1359–1370](../process_traces/2026-08-22-t20/real-transaction-runbook.md),
  [SHAKEDOWN-G2-RUNSHEET.md:1124–1134](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)).
- **Sacrificial** means qualification evidence, not campaign claim evidence.
  `QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE` is a new literal for this phase,
  not a token inherited from the ALPHA rehearsal card
  ([89-RULING-l10-corpus-precondition.md:80–90](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).
- A **spent window** is the `[QUIET-MAC]` collection for the claim-bearing
  transaction night; D-167(1) distinguishes diagnostic windows at lead
  discretion from the transaction on Ed's GO ([decision_log.md:10409](../decision_log.md)).
- **BENCH** means the magistrate runs a desk command with no `sudo`, no
  `[QUIET-MAC]` collection, and writes only below `$L10_CUSTODY_ROOT`; a
  **FIRST CHECK** is a named production artifact/adapter existence check made
  before its part. Both are this phase's own refusals
  ([89-RULING-l10-corpus-precondition.md:69–78](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).
- **BOUNDARY-PROVEN** labels a command whose exact flags and fail-closed
  boundary are recorded in the corresponding artifact-flow row; the rows are
  cited at each PASS/FAIL rule below.

The ladder uses three physical corpora. The **G2-b shakedown corpus** is one
real A/B/B/A block on its own non-claim root. The **floor-producer corpus** is
the real corpus collected by the transaction's ALPHA and BETA floor arms. The
**campaign corpus** is the complete claim-bearing corpus after its last
consuming arm. Ruling 89 R-1 assigns these distinct roles
([89-RULING-l10-corpus-precondition.md:39–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

## B. FIRST CHECKS

**FIRST CHECK** means a named production artifact or adapter whose presence is
checked before the affected ladder part begins. These checks and the per-step
head check are this phase's own refusals
([89-RULING-l10-corpus-precondition.md:80–90](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

The generator source and the generated output pack are different directories:
`$PACK_GENERATOR_ROOT` is `configs/campaigns/d117_contrast_v5`, while
`$PACK_ROOT` is the generated
`configs/campaigns/d117_contrast_qwen3_1p7b_vs_8b_v5`. The §C1 block is entered
only after the generator has emitted and checked the latter
([generate_configs.py:3000](../../configs/campaigns/d117_contrast_v5/generate_configs.py),
[SHAKEDOWN-G2-RUNSHEET.md:178–183](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)).

| Required input or adapter | Exact `rg` probe | Owner | Passing observation |
|---|---|---|---|
| `_v5` extraction spec, `joulewise.detection_floor_extraction_spec.v1` | `rg -n 'detection_floor_extraction_spec' configs/campaigns/d117_contrast_v5` | needs an owner row | The owner stages the matched artifact at `$EXTRACTION_SPEC`. |
| `_v5` final pinset and v2 input manifest | `rg -n 'joulewise\.(floor_mint_pinset|floor_mint_inputs)\.v2' configs/campaigns/d117_contrast_v5` | needs an owner row | The owner stages the matched files at `$FINAL_PINSET` and `$V2_INPUT_MANIFEST`. |
| Mint-artifact adapter for `dominance_ratio`, `replay_common_mode_dominance`, or `R_cm` | `rg -n 'dominance_ratio|replay_common_mode_dominance|R_cm' joulewise scripts` | `D165-SIDECAR-EMIT-01` | A production call site reads the issued floor artifact and emits the bound close-out artifact. |
| `joulewise.claim_verdicts.v1` to `joulewise.results_fill_input.v1` adapter | `rg -n 'claim_verdicts|claim-verdict' scripts --glob '*.py'` | `RENDERER-V5-SUCCESSOR-01` | A successor call site outside the frozen renderer produces `$RESULTS_FILL_INPUT`. |

A missing input, owner, or required match is **BLOCKED** for the affected part;
do not substitute fixtures, smoke artifacts, or an older generation
([89-RULING-l10-corpus-precondition.md:80–90](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).
The missing G2-a config producer is outside this phase because it precedes pack
generation: the only current source is a runsheet-rendering helper, not a
producer ([gen_g2_phase_d.py:54](../../scripts/gen_g2_phase_d.py)). R-6's
conflict about a pre-window floor artifact versus the ALPHA/BETA floor corpus
remains with `V5-G2B-SHAKEDOWN-01`, not this docs lane
([89-RULING-l10-corpus-precondition.md:92–95](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

## C. Execution record

### C1. Fixed inputs, custody, and lane

The runbook supplies the external campaign root and the G2-b root only after
their producing events; neither value is derivable before those events.
`CAMPAIGN_ROOT` is not derivable until transaction custody is created by
`V5-TRANSACTION-01`; source: `89-RULING-l10-corpus-precondition.md:53–58`.
`RUNS_ROOT` is not derivable until `V5-G2B-SHAKEDOWN-01` emits its real root;
source: `89-RULING-l10-corpus-precondition.md:39–45`; the current dependency is
`/tasks/L10-A-G2B-CONTRACT-PREFIX-01/dependencies/0` in `state_kernel.json`.
The following block is the complete setup at the reviewed head:

```sh
export REPO="$(/usr/bin/git rev-parse --show-toplevel)"
export PY="$REPO/.venv/bin/python"
: "${CAMPAIGN_ROOT:?not derivable until the transaction custody root is created}"
: "${RUNS_ROOT:?not derivable until V5-G2B-SHAKEDOWN-01 emits the real G2-b root}"
export ANALYSIS_ROOT="$CAMPAIGN_ROOT/analysis"
export CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"
export CLAIMS_ROOT="$CAMPAIGN_ROOT/claims"
export L10_CUSTODY_ROOT="$CUSTODY_ROOT/l10-sacrificial-rehearsal"
export PACK_GENERATOR_ROOT="$REPO/configs/campaigns/d117_contrast_v5"
export PACK_ROOT="$REPO/configs/campaigns/d117_contrast_qwen3_1p7b_vs_8b_v5"
export CAMPAIGN_RUNS_ROOT="$CUSTODY_ROOT/runs/campaign"
export PRODUCER_RUNS_ROOT="$CUSTODY_ROOT/runs/floor-producer"
export REDUCTION_ROOT="$L10_CUSTODY_ROOT/reductions"
export REHEARSAL_RECORD="$L10_CUSTODY_ROOT/l10-sacrificial-rehearsal-record.json"
export EXTRACTION_SPEC="$CUSTODY_ROOT/prospective/detection_floor_extraction_spec.json"
export FINAL_PINSET="$CUSTODY_ROOT/prospective/floor-pinset-v2.json"
export V2_INPUT_MANIFEST="$CUSTODY_ROOT/prospective/floor-mint-inputs-v2.json"
export CALIBRATION_LEDGER="$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl"
export CALIBRATION_CUSTODY_STORE="$CUSTODY_ROOT/calibration-store"
export RESULTS_FILL_INPUT="$L10_CUSTODY_ROOT/results-fill-input.json"
cd "$REPO"
export TRANSACTION_HEAD="$(/usr/bin/git rev-parse HEAD)"
export PROJECT_COMMIT="$TRANSACTION_HEAD"
test -z "$(/usr/bin/git status --porcelain=v1 --untracked-files=all)"
test "$TRANSACTION_HEAD" = "$(/usr/bin/git rev-parse refs/heads/main)"
test "$TRANSACTION_HEAD" = "$(/usr/bin/git rev-parse refs/remotes/origin/main)"
test -d "$PACK_ROOT/arm_readiness.freeze.receipts"
export PACK_SHA256="$($PY -c 'import sys; from joulewise.arm_readiness import committed_pack_tree_sha256; print(committed_pack_tree_sha256(sys.argv[1]))' "$PACK_ROOT")"
export COLLECTION_MANIFEST_ID="$(/usr/bin/jq -er '.manifest_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export EVIDENCE_ROOT_ID="$(/usr/bin/jq -er '.evidence_root_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export L10_PART="${L10_PART:-L10-A}"
if [ "$L10_PART" = L10-A ]; then
  test ! -e "$L10_CUSTODY_ROOT"
  /bin/mkdir -p "$L10_CUSTODY_ROOT/transcripts" "$REDUCTION_ROOT"
fi
```

Before L10-A, the magistrate must have completed the runbook's authenticated
staging unit: the production pack is copied into
`$CUSTODY_ROOT/prospective`, the selected floor artifact into
`$CUSTODY_ROOT/floors`, and the completed calibration ledger plus head pin
into `$CUSTODY_ROOT/calibration` ([SHAKEDOWN-G2-RUNSHEET.md:587–602](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)).
The L10-A staging commands below copy those exact transaction-custodied source
directories, so the magistrate can identify both the owner and the source of
each finalizer input before the refusal checker starts.

The two FIRST CHECK floor inputs are not present in the source pack at this
head ([v5-artifact-flow.md:29–30](v5-artifact-flow.md)). Their exact custody paths above are fixed for the transaction; their
bytes are not derivable until their owner rows emit them, which is why the
checks must pass before L10-B; source for the extraction-spec event:
`extract_detection_floors.py:57–60`, and source for the pinset/input event:
`mint_floor_artifact_generalized.py:4033–4039`. The floor-mint consumer
requires the v2 fields
`producer_plans[].cells[].absolute.evaluation_basis_sha256` and
`producer_plans[].cells[].absolute.consumption_semantics_id`
([mint_floor_artifact_generalized.py:827–842](../../scripts/mint_floor_artifact_generalized.py),
[mint_floor_artifact_generalized.py:519–572](../../scripts/mint_floor_artifact_generalized.py)).
The calibration store is the directory whose `manifest.json` carries the
ledger-derived head and content declarations
([calibration_ledger.py:1855–1863](../../joulewise/calibration_ledger.py)).
The successor results-fill file is not derivable until
`RENDERER-V5-SUCCESSOR-01` emits it; source:
`v5-artifact-flow.md:24`; its required schema is recorded in the Results-fills
row of [v5-artifact-flow.md:24](v5-artifact-flow.md).

`RUNS_ROOT` is the G2-b shakedown runs root: real, strict-valid, same-head
telemetry from the authenticated `_v5` contrast pack, with one A/B/B/A block
and `bracket-binding.json` before `whole-window-verdict.json` beneath that
root in NR-14 order. It is qualification-only. The G2-b root remains
byte-unchanged while L10-A records its tree hash before and after
(`state_kernel.json` `/tasks/L10-A-G2B-CONTRACT-PREFIX-01/acceptance`,
[89-RULING-l10-corpus-precondition.md:39–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

`PRODUCER_RUNS_ROOT` is the separate floor-producer corpus written by the
transaction's ALPHA and BETA arms. It is not derivable until those arms finish;
source: `89-RULING-l10-corpus-precondition.md:50–52`. It is used only by
L10-B; `CAMPAIGN_RUNS_ROOT` is not derivable until the last consuming arm
finishes; source: `89-RULING-l10-corpus-precondition.md:53–54`
([89-RULING-l10-corpus-precondition.md:39–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

The G2-b immutability fence remains verbatim: the root is never consumed by a
floor, mint, or claim. L10-A performs only strict validation, reduction, and a
refusing finalizer on a scratch copy; it records the before/after tree hash
(`state_kernel.json` `/tasks/V5-G2B-SHAKEDOWN-01/fences/2`,
[89-RULING-l10-corpus-precondition.md:60–67](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

Before L10-A, write the G2-b tree hash to
`$L10_CUSTODY_ROOT/g2b-tree-before.sha256`; repeat the same command after its
finalization check, write `g2b-tree-after.sha256`, and compare the two files.
A changed hash is **FAIL** ([89-RULING-l10-corpus-precondition.md:60–67](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

```sh
g2b_tree_hash() {
  (
    cd "$1"
    /usr/bin/find . -type f -exec /usr/bin/shasum -a 256 {} + |
      LC_ALL=C /usr/bin/sort | /usr/bin/shasum -a 256
  )
}
g2b_tree_hash "$RUNS_ROOT" > "$L10_CUSTODY_ROOT/g2b-tree-before.sha256"
```

Before each numbered command, run
`test "$(/usr/bin/git rev-parse HEAD)" = "$TRANSACTION_HEAD"`; a mismatch is
this phase's own refusal ([89-RULING-l10-corpus-precondition.md:80–90](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).
Every L10 command is **BENCH**: the magistrate executes it with no `sudo`, no
`[QUIET-MAC]` collection, and writes only below `$L10_CUSTODY_ROOT`
([89-RULING-l10-corpus-precondition.md:74–78](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).
**BOUNDARY-PROVEN** is the label for the exact command/fail-closed boundary
named by the corresponding row in [v5-artifact-flow.md:16–24](v5-artifact-flow.md).

### C2. The three-part ladder

#### L10-A — pre-window G2-b contract prefix

L10-A runs steps 1, 2, and 5 before the claim-bearing window. It gates
`V5-TRANSACTION-01` but does not close the whole L10 row
([89-RULING-l10-corpus-precondition.md:39–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md),
`state_kernel.json` `/tasks/L10-A-G2B-CONTRACT-PREFIX-01/acceptance`).

The G2-b root is staged before step 5. The magistrate stages each input as
follows: `RUNS_ROOT` to `l10-a-staging/g2b`, the complete prospective pack
subtree from `$CUSTODY_ROOT/prospective` to `l10-a-staging/prospective`, the
complete calibration subtree to `l10-a-staging/calibration`, and the floor
inputs to `l10-a-staging/floors`. Thus the custody root passed to the checker
contains every finalizer input, not only the G2-b root:

```sh
export L10_A_STAGING_ROOT="$L10_CUSTODY_ROOT/l10-a-staging"
/bin/mkdir -p "$L10_A_STAGING_ROOT/g2b" \
  "$L10_A_STAGING_ROOT/prospective" "$L10_A_STAGING_ROOT/calibration" \
  "$L10_A_STAGING_ROOT/floors" "$L10_A_STAGING_ROOT/analysis-output"
/usr/bin/ditto "$RUNS_ROOT/." "$L10_A_STAGING_ROOT/g2b/"
/usr/bin/ditto "$CUSTODY_ROOT/prospective/." "$L10_A_STAGING_ROOT/prospective/"
/usr/bin/ditto "$CUSTODY_ROOT/calibration/." "$L10_A_STAGING_ROOT/calibration/"
/usr/bin/ditto "$CUSTODY_ROOT/floors/." "$L10_A_STAGING_ROOT/floors/"
g2b_tree_hash "$RUNS_ROOT" > "$L10_CUSTODY_ROOT/g2b-tree-staged.sha256"
g2b_tree_hash "$L10_A_STAGING_ROOT/g2b" > "$L10_CUSTODY_ROOT/g2b-tree-staged-copy.sha256"
/usr/bin/cmp "$L10_CUSTODY_ROOT/g2b-tree-staged.sha256" \
  "$L10_CUSTODY_ROOT/g2b-tree-staged-copy.sha256"
for required in \
  "$L10_A_STAGING_ROOT/prospective/analysis_manifest_v3.json" \
  "$L10_A_STAGING_ROOT/prospective/plan_tree.json" \
  "$L10_A_STAGING_ROOT/g2b/whole-window-verdict.json" \
  "$L10_A_STAGING_ROOT/g2b/bracket-binding.json" \
  "$L10_A_STAGING_ROOT/calibration/calibration_observation_ledger.jsonl" \
  "$L10_A_STAGING_ROOT/floors/d117-v5-aggregate-floor.json"; do
  test -f "$required"
done
```

The reader must see those six files and the complete three staged subtrees
before invoking step 5. If any staged pack-relative input is absent, the
checker returns `analysis_finalization_prospective_invalid`; that is an
incomplete-staging bug and this procedure scores it **FAIL**, not a failed
member-cover proof ([SHAKEDOWN-G2-RUNSHEET.md:1152–1156](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)).
The containment rule is explicit in `_copy_path`: it calls
`relative_to(custody_root)` at
[check_window_provenance.py:467–474](../../scripts/check_window_provenance.py),
and every finalizer input is passed through `_copy_path` at
[check_window_provenance.py:505–515](../../scripts/check_window_provenance.py).

1. **Strict validation — L10-A / BENCH / BOUNDARY-PROVEN.** Enumerate the
   actual `run_id` values from the G2-b campaign manifests, then validate each:

   ```sh
   export G2B_RUN_IDS="$L10_CUSTODY_ROOT/g2b-run-ids.txt"
   for manifest in "$RUNS_ROOT"/campaign_manifests/*.json; do
     test -f "$manifest"
     /usr/bin/jq -er '.members[]?.bundle_ids[]?' "$manifest"
   done | LC_ALL=C /usr/bin/sort -u > "$G2B_RUN_IDS"
   test -s "$G2B_RUN_IDS"
   while IFS= read -r RUN_ID; do
     test -n "$RUN_ID"
     (
       cd "$RUNS_ROOT/$RUN_ID"
       /usr/bin/find . -type f -exec /usr/bin/shasum -a 256 {} +
     ) >> "$L10_CUSTODY_ROOT/transcripts/l10-a-strict-validation.txt"
     "$PY" -m joulewise validate-bundle "$RUNS_ROOT/$RUN_ID" --strict \
       >> "$L10_CUSTODY_ROOT/transcripts/l10-a-strict-validation.txt"
   done < "$G2B_RUN_IDS"
   ```

   Record the input paths and SHA-256 digests with the transcript. A missing or
   strict-invalid member is **FAIL** ([v5-artifact-flow.md:16](v5-artifact-flow.md)).

2. **Reduction — L10-A / BENCH / BOUNDARY-PROVEN.** For each strict-valid
   `RUN_ID`, run:

   ```sh
   while IFS= read -r RUN_ID; do
     test -n "$RUN_ID"
     "$PY" -m joulewise reduce "$RUNS_ROOT/$RUN_ID" \
       --output "$REDUCTION_ROOT/$RUN_ID.summary_metrics.rereduced.json"
   done < "$G2B_RUN_IDS"
   ```

   A missing, overwritten, or in-bundle output is **FAIL**
   ([v5-artifact-flow.md:17](v5-artifact-flow.md)).

#### 5. Finalization exact refusal — L10-A / BENCH / BOUNDARY-PROVEN

The staged root is the `--custody-root`; the G2-b source root is never passed
as a finalizer input. The scratch directory is a sibling of the staged root,
so the checker can copy the staged custody without changing the source:

```sh
export L10_A_SCRATCH_ROOT="$L10_CUSTODY_ROOT/l10-a-scratch"
/bin/mkdir -p "$L10_A_SCRATCH_ROOT"
"$PY" scripts/check_window_provenance.py --expect-finalize-refusal \
  --scratch-dir "$L10_A_SCRATCH_ROOT" \
  --prospective-manifest "$L10_A_STAGING_ROOT/prospective/analysis_manifest_v3.json" \
  --plan-tree "$L10_A_STAGING_ROOT/prospective/plan_tree.json" \
  --custody-root "$L10_A_STAGING_ROOT" \
  --runs-root "$L10_A_STAGING_ROOT/g2b" \
  --whole-window-verdict "$L10_A_STAGING_ROOT/g2b/whole-window-verdict.json" \
  --bracket-binding "$L10_A_STAGING_ROOT/g2b/bracket-binding.json" \
  --calibration-ledger "$L10_A_STAGING_ROOT/calibration/calibration_observation_ledger.jsonl" \
  --aggregate-floor-artifact "$L10_A_STAGING_ROOT/floors/d117-v5-aggregate-floor.json" \
  --output-dir "$L10_A_STAGING_ROOT/analysis-output" \
  > "$L10_CUSTODY_ROOT/transcripts/l10-a-finalization.txt"
g2b_tree_hash "$RUNS_ROOT" > "$L10_CUSTODY_ROOT/g2b-tree-after.sha256"
/usr/bin/cmp "$L10_CUSTODY_ROOT/g2b-tree-before.sha256" \
  "$L10_CUSTODY_ROOT/g2b-tree-after.sha256"
```

The checker copies the staging custody below `$L10_A_SCRATCH_ROOT` before it
invokes the finalizer. L10-A **PASS** is the singleton observed reason
`analysis_finalization_member_cover_mismatch`, the verified finalizer branches
being [analysis_manifest_v3.py:2986](../../joulewise/analysis_manifest_v3.py)
and [analysis_manifest_v3.py:3048–3049](../../joulewise/analysis_manifest_v3.py).
Any other reason, a successful finalization, a nonzero tree comparison, or a
write outside L10 custody is **FAIL** ([89-RULING-l10-corpus-precondition.md:39–49](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

#### L10-B — floor-producer extraction and rehearsal mint

L10-B begins in a fresh shell after the ALPHA/BETA floor arms. Re-export every
variable used by this part; the producer corpus is the transaction-custodied
path below, not G2-b:

```sh
export REPO="$(/usr/bin/git rev-parse --show-toplevel)"
export PY="$REPO/.venv/bin/python"
: "${CAMPAIGN_ROOT:?the runbook campaign root is required}"
export ANALYSIS_ROOT="$CAMPAIGN_ROOT/analysis"
export CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"
export L10_CUSTODY_ROOT="$CUSTODY_ROOT/l10-sacrificial-rehearsal"
export PACK_ROOT="$REPO/configs/campaigns/d117_contrast_qwen3_1p7b_vs_8b_v5"
export PRODUCER_RUNS_ROOT="$CUSTODY_ROOT/runs/floor-producer"
export L10_B_PRODUCER_SCRATCH="$L10_CUSTODY_ROOT/l10-b-scratch/producer-runs"
export EXTRACTION_SPEC="$CUSTODY_ROOT/prospective/detection_floor_extraction_spec.json"
export FINAL_PINSET="$CUSTODY_ROOT/prospective/floor-pinset-v2.json"
export V2_INPUT_MANIFEST="$CUSTODY_ROOT/prospective/floor-mint-inputs-v2.json"
export CALIBRATION_CUSTODY_STORE="$CUSTODY_ROOT/calibration-store"
export CALIBRATION_LEDGER="$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl"
export COLLECTION_MANIFEST_ID="$(/usr/bin/jq -er '.manifest_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export EVALUATION_BASIS_SHA256="$(/usr/bin/jq -er '.producer_plans[0].cells[0].absolute.evaluation_basis_sha256' "$FINAL_PINSET")"
export CONSUMPTION_SEMANTICS_ID="$(/usr/bin/jq -er '.producer_plans[0].cells[0].absolute.consumption_semantics_id' "$FINAL_PINSET")"
export FINAL_PINSET_SHA256="$(/usr/bin/shasum -a 256 "$FINAL_PINSET" | /usr/bin/awk '{print $1}')"
export PROJECT_COMMIT="$(/usr/bin/git -C "$REPO" rev-parse HEAD)"
test -d "$PRODUCER_RUNS_ROOT"
test -f "$EXTRACTION_SPEC"
test -f "$FINAL_PINSET"
test -f "$V2_INPUT_MANIFEST"
test -f "$CALIBRATION_LEDGER"
test -f "$CALIBRATION_CUSTODY_STORE/manifest.json"
cd "$REPO"
```

The commands above derive `COLLECTION_MANIFEST_ID` from
`analysis_manifest_v3.json.manifest_id`; they derive both semantics values from
the authenticated pinset fields named above; and they derive
`FINAL_PINSET_SHA256` from the exact pinset bytes supplied to mint. The paths
and fields are therefore executable rather than a request to “set from
authenticated inputs.” Copy the real floor-producer corpus to scratch custody
before step 3 ([89-RULING-l10-corpus-precondition.md:50–52](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)):

```sh
/usr/bin/ditto "$PRODUCER_RUNS_ROOT/." "$L10_B_PRODUCER_SCRATCH/"
```

3. **Floor extraction — L10-B / BENCH / BOUNDARY-PROVEN.** Run:

   ```sh
   export EXTRACTION_REPORT="$L10_CUSTODY_ROOT/l10-b-floor-extraction.json"
   "$PY" scripts/extract_detection_floors.py \
     --runs-root "$L10_B_PRODUCER_SCRATCH" --spec "$EXTRACTION_SPEC" \
     --out "$EXTRACTION_REPORT" --manifest-id "$COLLECTION_MANIFEST_ID" \
     --evaluation-basis-sha256 "$EVALUATION_BASIS_SHA256" \
     --consumption-semantics-id "$CONSUMPTION_SEMANTICS_ID" --hash-bundles
   ```

   An absent report is **FAIL** ([v5-artifact-flow.md:19](v5-artifact-flow.md)).

4. **Mint — L10-B / BENCH / BOUNDARY-PROVEN.** Run:

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
   mismatch is **FAIL** ([v5-artifact-flow.md:20](v5-artifact-flow.md)).

#### L10-C — full edge on the complete campaign corpus

L10-C begins in a fresh shell after the last consuming arm. Re-export every
variable used below. It consumes the production floor artifact emitted by the
production Mint row at `$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json`,
not L10-B's rehearsal mint at
`$L10_CUSTODY_ROOT/l10-b-aggregate-floor.json`; the production output path is
the Mint row's declared consumer handoff ([v5-artifact-flow.md:20](v5-artifact-flow.md)).

```sh
export REPO="$(/usr/bin/git rev-parse --show-toplevel)"
export PY="$REPO/.venv/bin/python"
: "${CAMPAIGN_ROOT:?the runbook campaign root is required}"
export ANALYSIS_ROOT="$CAMPAIGN_ROOT/analysis"
export CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"
export CLAIMS_ROOT="$CAMPAIGN_ROOT/claims"
export L10_CUSTODY_ROOT="$CUSTODY_ROOT/l10-sacrificial-rehearsal"
export PACK_ROOT="$REPO/configs/campaigns/d117_contrast_qwen3_1p7b_vs_8b_v5"
export CAMPAIGN_RUNS_ROOT="$CUSTODY_ROOT/runs/campaign"
export PRODUCER_RUNS_ROOT="$CUSTODY_ROOT/runs/floor-producer"
export L10_C_RUNS_SCRATCH="$L10_CUSTODY_ROOT/l10-c-scratch/campaign-runs"
export L10_C_ANALYSIS_SCRATCH="$L10_CUSTODY_ROOT/l10-c-scratch/analysis"
export CALIBRATION_LEDGER="$CUSTODY_ROOT/calibration/calibration_observation_ledger.jsonl"
export AGGREGATE_FLOOR_ARTIFACT="$CUSTODY_ROOT/floors/d117-v5-aggregate-floor.json"
export EVIDENCE_ROOT_ID="$(/usr/bin/jq -er '.evidence_root_id' "$PACK_ROOT/analysis_manifest_v3.json")"
export RESULTS_FILL_INPUT="$L10_CUSTODY_ROOT/results-fill-input.json"
export PROJECT_COMMIT="$(/usr/bin/git -C "$REPO" rev-parse HEAD)"
test -d "$CAMPAIGN_RUNS_ROOT"
test -f "$AGGREGATE_FLOOR_ARTIFACT"
test -f "$CALIBRATION_LEDGER"
test -f "$RESULTS_FILL_INPUT"  # otherwise blocked until the successor emits it
/usr/bin/ditto "$CAMPAIGN_RUNS_ROOT/." "$L10_C_RUNS_SCRATCH/"
/bin/mkdir -p "$L10_C_ANALYSIS_SCRATCH"
cd "$REPO"
```

The campaign corpus is copied to scratch custody before positive finalization
([89-RULING-l10-corpus-precondition.md:50–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).
`EVIDENCE_ROOT_ID` is read from the authenticated prospective manifest's
`.evidence_root_id` field; `CALIBRATION_LEDGER` is the exact runbook path
under transaction custody ([real-transaction-runbook.md:1359–1370](../process_traces/2026-08-22-t20/real-transaction-runbook.md)).
The results-fill input is not derivable until the named successor emits the
fixed path; the source renderer accepts a path via `render_from_manifest`
([render_results_fills.py:945](../../scripts/render_results_fills.py)).

5. **Finalization positive form — L10-C / BENCH / BOUNDARY-PROVEN.** Capture
   the CLI's JSON output so the finalized path is executable, not a bare
   filename:

   ```sh
   export L10_C_FINALIZATION_TRANSCRIPT="$L10_CUSTODY_ROOT/transcripts/l10-c-finalization.json"
   "$PY" scripts/finalize_analysis_manifest.py \
     --prospective-manifest "$PACK_ROOT/analysis_manifest_v3.json" \
     --plan-tree "$PACK_ROOT/plan_tree.json" \
     --custody-root "$L10_C_ANALYSIS_SCRATCH" --runs-root "$L10_C_RUNS_SCRATCH" \
     --whole-window-verdict "$L10_C_RUNS_SCRATCH/whole-window-verdict.json" \
     --bracket-binding "$L10_C_RUNS_SCRATCH/bracket-binding.json" \
     --calibration-ledger "$CALIBRATION_LEDGER" \
     --aggregate-floor-artifact "$AGGREGATE_FLOOR_ARTIFACT" \
     --output-dir "$L10_C_ANALYSIS_SCRATCH" \
     > "$L10_C_FINALIZATION_TRANSCRIPT"
   export FINALIZED_MANIFEST="$(/usr/bin/jq -er '.output' "$L10_C_FINALIZATION_TRANSCRIPT")"
   test -f "$FINALIZED_MANIFEST"
   ```

   A missing finalized manifest is **FAIL** ([v5-artifact-flow.md:22](v5-artifact-flow.md)).

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
   ([v5-artifact-flow.md:23](v5-artifact-flow.md)).

7. **Results fills — L10-C / BENCH / BOUNDARY-PROVEN.** Run the successor's
   fixed input through the renderer:

   ```sh
   export RESULTS_FILLS_MD="$L10_CUSTODY_ROOT/l10-c-results-fills.md"
   "$PY" scripts/render_results_fills.py "$RESULTS_FILL_INPUT" > "$RESULTS_FILLS_MD"
   "$PY" scripts/render_results_fills.py --validate-rendered "$RESULTS_FILLS_MD"
   ```

   Missing output, `STOP_FILL`, a leftover fill token, or validation failure is
   **FAIL** ([v5-artifact-flow.md:24](v5-artifact-flow.md)).

### C3. Ratified record and part results

The magistrate must ratify this record contract before execution; that
authorization licenses the part-level **PASS** and **FAIL** rules below
([89-RULING-l10-corpus-precondition.md:80–90](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

Use `l10-sacrificial-rehearsal-record.json` at `$REHEARSAL_RECORD`. Each part
record carries the following fields; `proof_scope` identifies the physical
corpus and ladder portion represented by that record. Its permitted values are
`L10_A_G2B_CONTRACT_PREFIX`, `L10_B_FLOOR_PRODUCER`, and `L10_C_FULL_EDGE`
([89-RULING-l10-corpus-precondition.md:39–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

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
hashes match. Any other finalization reason or a successful finalization is
**FAIL** (`state_kernel.json` `/tasks/L10-A-G2B-CONTRACT-PREFIX-01/acceptance`,
[analysis_manifest_v3.py:2986,3048](../../joulewise/analysis_manifest_v3.py)).
The L10-B record is **PASS** when scratch-corpus extraction and rehearsal mint
each emit their governed artifacts. The L10-C record is **PASS** when positive
finalization, Claim gate, and Results fills each emit their governed artifacts
before publication ([89-RULING-l10-corpus-precondition.md:50–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

The ladder reaches overall **PASS** after all three part records pass. A head
change, pack-digest change, missing record field, artifact outside L10 custody,
or an unregistered refusal is **FAIL** ([89-RULING-l10-corpus-precondition.md:39–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

## D. Sequencing

The current kernel state names the gate and its dependencies. `L10-A-G2B-CONTRACT-PREFIX-01`
has acceptance at `state_kernel.json` `/tasks/L10-A-G2B-CONTRACT-PREFIX-01/acceptance`;
its acceptance requires strict validation/reduction, the singleton refusal, and
the equal before/after tree hashes. `V5-TRANSACTION-01` has a hard start
dependency on that row at `/tasks/V5-TRANSACTION-01/dependencies/0`; the
dependency requires the ratified L10-A record before the first claim-bearing
arm. The parent `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01` has acceptance at
`/tasks/L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01/acceptance` and dependencies at
`/tasks/L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01/dependencies`: its hard close
dependency is `V5-TRANSACTION-01`, its hard start dependency is L10-A, and its
acceptance says all three records are required, so L10-A alone does not close
the parent; because L10-C is the final record after the last consuming arm,
the parent cannot close before L10-C. These rows are present at this head
([89-RULING-l10-corpus-precondition.md:39–58](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md)).

For this sequence, “spent window” means the claim-bearing window under
D-167(1), not an earlier diagnostic collection ([decision_log.md:10409](../decision_log.md)).

## E. Limits and refusals

This phase adds its own refusals: the per-step transaction-head re-check and
the FIRST-CHECK block. It schedules and records those checks; it does not alter
the governed claim edge or repair a missing producer, adapter, or artifact
([89-RULING-l10-corpus-precondition.md:80–90](../process_traces/2026-09-01-fresh-model-review/89-RULING-l10-corpus-precondition.md),
`state_kernel.json` `/tasks/L10-A-G2B-CONTRACT-PREFIX-01/fences/0`).

Preserve a detected defect and route it to its owning kernel row; a defect with
no owner is a request for an owner row, not an L10 repair
(`state_kernel.json` `/tasks/L10-A-G2B-CONTRACT-PREFIX-01/fences/0`).
