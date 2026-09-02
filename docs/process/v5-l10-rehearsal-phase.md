# `_v5` L10 sacrificial rehearsal — PRE-WINDOW phase

## A. What this phase is, in the ruled words

The original L10 definition is preserved here verbatim from the 2026-08-15
consumption-edge consult:

> L10 should run this `[AGENT]` sacrificial lifecycle entirely under `$TMPDIR` before gamma collection:
>
> 1. Build the prospective manifest twice from the same pack; require byte equality, valid plan-tree pinning and identical semantic hashes.
> 2. Use production writers/validators to create a synthetic exact-80-member corpus, passed whole-window verdict, exact evaluation basis, bracket binding, finalized ledger and aggregate floor artifact covering both frozen selectors.
> 3. Finalize twice; require byte-identical idempotence and a valid finalized manifest.
> 4. Run the real `analyze-claims` CLI on the finalized manifest. Require exactly the two frozen contrast IDs and the exact frozen family/multiplicity structure.
> 5. Run two scientific scenarios: one above the decision bar and one below it. Both must finalize; only the claim outcome may differ.
> 6. Independently compute the expected semantic projection rather than calling the production projector as the test oracle.
> 7. Mutate orientation, metric, estimator, test, family membership, `m`, block/member identity, configuration SHA and floor dependency—one at a time and coupled on both sides while recomputing local IDs. Every case must still refuse because the frozen pack/tree digest or independent semantic projection disagrees.
> 8. Exercise missing/failed verdict, missing/extra member, wrong evaluation basis, wrong bracket, stale ledger head, wrong floor bytes, absent prefill floor, unknown/duplicate keys, non-finite JSON, path escape/symlink, partial output, conflicting existing output, and direct prospective-manifest consumption.
> 9. Re-run the historical v3 builder/validator and existing analysis fixture to prove no byte or behavior drift.
> 10. Emit an immutable rehearsal receipt pinning HEAD, pack/tree/prospective hashes, finalizer and consumer code hashes, finalized-manifest and claim-artifact hashes, both contrast IDs, family semantic hash, and the complete refusal matrix.

The later adopted contract supplies the binding schedule: “the L10 sacrificial
rehearsal re-runs the full edge at the same head before any window is spent.”
The production-pack qualification is also explicit: the authorized close is a
“same-HEAD, production-pack L10 sacrificial replay.” These words are in the
[WO-CONSUMPTION-EDGE adoption and RULING-REQUIRED item (d)](../decision_log.md).

For this `_v5` phase, the terms mean the following before any procedure uses
them:

- The **claim edge** is the complete command sequence in the
  [`_v5` artifact-flow table](v5-artifact-flow.md), beginning with **Strict
  validation** and continuing through **Reduction**, **Floor extraction**,
  **Mint**, **Finalization**, **Claim gate**, and **Results fills**, in that
  order. “Full edge” means that no named step is skipped merely because a later
  command could be invoked directly.
- A **production pack** is the authenticated `_v5` pack directory generated and
  checked at the transaction head, with its real prospective manifest and plan
  tree. It is not a mock, synthetic, `pipeline_smoke`, smoke-scoped, or reduced
  family. D-160 R-1 says a synthetic clean leg is not the pre-night proof; the
  kernel fence therefore does not allow such a leg to discharge L10. See
  [D-160 R-1](../process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md).
- The **transaction head** is the one Git commit whose bytes the claim-bearing
  transaction is allowed to execute. **Same head** means that `git rev-parse
  HEAD` returns that identical full SHA before every step and that the record
  pins it once as `transaction_head_git_sha`. The transaction's published-head
  record identifies the commit; the production pack's `plan_tree.json`,
  `analysis_manifest_v3.json`, and `arm_readiness.freeze.receipts/freeze-*.json`
  then bind the authenticated pack identity and plan at that commit. It is not the later
  **fixation commit**, which means the first commit after campaign close and
  carries the successor-pinset SHA plus its loud-fail guard. D-153 A1 and A6
  place that fixation after the last consuming arm; the rehearsal therefore
  runs at the fixed transaction head, not at a guessed future fixation head.
  See the [fixation and changed-set ruling](../process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md)
  and the [historical transaction vocabulary](../process_traces/2026-08-22-t20/real-transaction-runbook.md).
- **Custody** is the append-only, outside-repository directory that preserves
  authenticated inputs, outputs, transcripts, and their hashes. The established
  layout is `CAMPAIGN_ROOT`, `ANALYSIS_ROOT="$CAMPAIGN_ROOT/analysis"`,
  `CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"`, and a sibling `CLAIMS_ROOT`; the
  L10 record lives below `CUSTODY_ROOT`. This follows the
  [transaction-custody convention](../process_traces/2026-08-22-t20/real-transaction-runbook.md).
  `scripts/window_status.sh` likewise keeps the commit-freeze sentinel outside
  the repository because repository-local custody would create changed-set
  residue.
- **Sacrificial** means the run is qualification choreography evidence, never
  claim evidence. Every output and the record carry the literal label
  `QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE`, live below the rehearsal custody
  directory, and are never copied into the claim-bearing transaction's
  analysis or claims directories. This is the same evidence-use distinction as
  the [ALPHA rehearsal card](rehearsal-operator-card.md). The separate custody
  path is the refusal boundary: an operator must refuse any request to cite,
  publish, or substitute a rehearsal output as campaign claim evidence.
- A **spent window** is a `[QUIET-MAC]` collection launched for the `_v5`
  claim-bearing night. **Before any window is spent** means after the
  transaction head and production pack are fixed, but before the first such
  collection command starts. The rehearsal itself is desk work: it launches no
  collection and consumes no quiet-machine window.

This mechanism is forced by S9-01 and S9-07, not by a desire for another smoke
test. S9-01 found that collection did not join to an analysis-manifest identity;
S9-07 found that the finalizer had no operator step. Together they describe a
claim edge that had never been driven end to end against its real pack. For
example, a copied procedure that jumps from Mint to Claim gate would expose
S9-07 only after a paid night, whereas this rehearsal stops at Finalization,
records the missing artifact as FAIL, and routes the defect before collection.
The source findings and the missing schedule are
[S9-01, S9-07, and S9-12](../process_traces/2026-08-27-t26/ruled-not-installed-sweep/SHORTLIST.md).

## B. Inputs the rehearsal needs that do not exist yet

These are **FIRST CHECKS**. Run them at the transaction head before setting up
any rehearsal output. A check passes only when its named production artifact or
adapter exists and its owning row's acceptance is satisfied; a no-match result
confirms that the check is still blocked. The exact absence probes below are
copied from the `_v5` artifact-flow document.

| Required input or adapter | Exact `rg` probe | Owning kernel row | Passing observation |
|---|---|---|---|
| `_v5` extraction spec, schema `joulewise.detection_floor_extraction_spec.v1` | `rg -n 'detection_floor_extraction_spec' configs/campaigns/d117_contrast_v5` | **no owning row — NEEDS-ROW** | At least one match identifies the authenticated `_v5` spec consumed as `$EXTRACTION_SPEC`. |
| `_v5` final pinset plus v2 input manifest, schemas `joulewise.floor_mint_pinset.v2` and `joulewise.floor_mint_inputs.v2` | `rg -n 'joulewise\.(floor_mint_pinset|floor_mint_inputs)\.v2' configs/campaigns/d117_contrast_v5` | **no owning row — NEEDS-ROW** | Matches identify both distinct authenticated inputs consumed as `$FINAL_PINSET` and `$V2_INPUT_MANIFEST`; one without the other is FAIL. |
| Mint-artifact adapter that feeds `dominance_ratio` and `replay_common_mode_dominance` / `R_cm` | `rg -n 'dominance_ratio|replay_common_mode_dominance|R_cm' joulewise scripts` | `D165-SIDECAR-EMIT-01` (after `D165-CLOSEOUT-CORE-01`) | A production call site reads `joulewise.detection_floor_artifact.v2` and emits the separately bound replay/close-out artifact required by the owner. |
| `joulewise.claim_verdicts.v1` to `joulewise.results_fill_input.v1` adapter | `rg -n 'claim_verdicts|claim-verdict' scripts/render_results_fills.py` | `RENDERER-V5-SUCCESSOR-01` | The frozen 109-key renderer remains unchanged; the owner must instead provide and document the successor adapter, so also run `rg -n 'claim_verdicts|claim-verdict' scripts --glob '*.py'` and require a match outside `render_results_fills.py`. |

The exact probes currently return no matches. **This phase is BLOCKED until
every FIRST CHECK passes.** Do not substitute fixtures, smoke artifacts, or an
older generation to make a check appear green.

The flow document's missing G2-a config producer is not another L10 FIRST CHECK:
it lies before Pack generation, while the ruled claim edge begins at Strict
validation after the authenticated production pack already exists.

## C. Execution record

### C1. Fixed inputs and custody paths

On Ed's machine, in the clean production checkout, export the following literal
roles. A **rehearsal custody root** is the append-only subdirectory dedicated to
this qualification run; it is deliberately not the production analysis root or
claims root.

```sh
export REPO='/absolute/path/to/the/production-checkout'
export PY="$REPO/.venv/bin/python"
export CAMPAIGN_ROOT='/absolute/path/to/the-v5-transaction-custody'
export ANALYSIS_ROOT="$CAMPAIGN_ROOT/analysis"
export CUSTODY_ROOT="$ANALYSIS_ROOT/transaction"
export CLAIMS_ROOT="$CAMPAIGN_ROOT/claims"
export L10_CUSTODY_ROOT="$CUSTODY_ROOT/l10-sacrificial-rehearsal"
export PACK_ROOT="$REPO/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
export RUNS_ROOT='/absolute/path/to/the-read-only-production-pack-bound-replay-corpus'
export PRODUCER_RUNS_ROOT='/absolute/path/to/the-read-only-authenticated-floor-producer-corpus'
export REDUCTION_ROOT="$L10_CUSTODY_ROOT/reductions"
export ANALYSIS_CUSTODY_ROOT="$L10_CUSTODY_ROOT/analysis"
export EXTRACTION_SPEC='/absolute/path/from-FIRST-CHECK-1'
export EXTRACTION_REPORT="$L10_CUSTODY_ROOT/floor-extraction.json"
export FINAL_PINSET='/absolute/path/from-FIRST-CHECK-2'
export V2_INPUT_MANIFEST='/absolute/path/from-FIRST-CHECK-2'
export AGGREGATE_FLOOR_ARTIFACT="$L10_CUSTODY_ROOT/aggregate-floor.json"
export SINGLE_COUNT_STATEMENT="$L10_CUSTODY_ROOT/single-count.txt"
export FINALIZED_MANIFEST="$ANALYSIS_CUSTODY_ROOT/PROSPECTIVE_MANIFEST_ID.finalized.json"
export CLAIM_VERDICTS="$L10_CUSTODY_ROOT/claim-verdicts.json"
export RESULTS_FILL_INPUT="$L10_CUSTODY_ROOT/results-fill-input.json"
export RESULTS_FILLS_MD="$L10_CUSTODY_ROOT/results-fills.md"
export REHEARSAL_RECORD="$L10_CUSTODY_ROOT/l10-sacrificial-rehearsal-record.json"
cd "$REPO"
export TRANSACTION_HEAD="$(/usr/bin/git rev-parse HEAD)"
export PROJECT_COMMIT="$TRANSACTION_HEAD"
test -z "$(/usr/bin/git status --porcelain=v1 --untracked-files=all)"
test "$TRANSACTION_HEAD" = "$(/usr/bin/git rev-parse refs/heads/main)"
test "$TRANSACTION_HEAD" = "$(/usr/bin/git rev-parse refs/remotes/origin/main)"
test -d "$PACK_ROOT/arm_readiness.freeze.receipts"
export PACK_SHA256="$("$PY" -c 'import sys; from joulewise.arm_readiness import committed_pack_tree_sha256; print(committed_pack_tree_sha256(sys.argv[1]))' "$PACK_ROOT")"
test ! -e "$L10_CUSTODY_ROOT"
/bin/mkdir -p "$L10_CUSTODY_ROOT/transcripts" "$ANALYSIS_CUSTODY_ROOT"
```

The two corpus roots must contain real, strict-valid, claim-eligible evidence
bound to the authenticated production pack; a synthetic or smoke-scoped corpus
is a failed precondition under D-160 R-1. The setup records the published common
head as `TRANSACTION_HEAD`, requires freeze-receipt custody for the pack,
computes the pack digest with `committed_pack_tree_sha256`, and refuses to reuse
an older rehearsal directory. Before each numbered step, repeat
`test "$(/usr/bin/git rev-parse HEAD)" = "$TRANSACTION_HEAD"` and stop on any
mismatch. No command below needs `sudo`, and none is a `[QUIET-MAC]` collection.

> **OPEN RULING — corpus precondition (magistrate, 2026-09-01).** The paragraph
> above cannot be satisfied before a window is spent: evidence "bound to the
> authenticated production pack" exists only after the `_v5` transaction has
> collected it, and this phase is sequenced BEFORE that transaction (§D). The
> kernel row's fence ("same head, production pack; synthetic does not
> discharge") and D-160 R-1/R-2 leave three candidate corpora, none of which
> satisfies every clause: (i) D-160 R-2's live ~20-minute run on a real tiny
> quarantined family generation (real evidence, not the production pack);
> (ii) the retained a9/a10 corpus used by ED-L10-1 (real, claim-eligible,
> Qwen2.5 `_v3` pack, not `_v5`); (iii) the production pack itself (only
> after the window — then the rehearsal is no longer a rehearsal). Which corpus
> discharges this phase, and under which relaxation of the fence, is a
> reinterpretation of a ruled fence and is therefore consulted (Sol xhigh +
> Opus contract lens), not ruled solo. Until that ruling lands, `RUNS_ROOT`
> and `PRODUCER_RUNS_ROOT` are unset and C2 must not start.

The **BOUNDARY-PROVEN** label means the command shape and fail-closed boundary
are already represented by the governed flow and tests. **ED-FIRST** means its
first execution on the production checkout and outside-repository custody must
be done by Ed. All seven production executions below are ED-FIRST; their command
interfaces are boundary-proven, but a fixture run is not their execution.

### C2. Operator steps

1. **Strict validation — ED-FIRST.** Input: each production-pack run bundle at
   `$RUNS_ROOT/$RUN_ID`. For every manifest-declared run ID, run:

   ```sh
   "$PY" -m joulewise validate-bundle "$RUNS_ROOT/$RUN_ID" --strict
   ```

   Emitted artifact: no JSON artifact; exit `0` and `valid bundle: ...` are
   captured in `$L10_CUSTODY_ROOT/transcripts/strict-validation.txt`. Custody:
   transcript plus the SHA-256 and original custody path of every read-only
   input bundle. Any missing or strict-invalid declared member is FAIL.

2. **Reduction — ED-FIRST.** Input: each strict-valid bundle. For every same
   `$RUN_ID`, run the flow-table command with the rehearsal reduction root:

   ```sh
   /bin/mkdir -p "$REDUCTION_ROOT"; "$PY" -m joulewise reduce "$RUNS_ROOT/$RUN_ID" --output "$REDUCTION_ROOT/$RUN_ID.summary_metrics.rereduced.json"
   ```

   Emitted artifact: `$REDUCTION_ROOT/$RUN_ID.summary_metrics.rereduced.json`,
   summary schema `0.1`. Custody: `L10_CUSTODY_ROOT/reductions/`. A missing,
   overwritten, or in-bundle output is FAIL.

3. **Floor extraction — ED-FIRST.** Input: `$PRODUCER_RUNS_ROOT`, the FIRST
   CHECK 1 spec, and the authenticated whole-window basis. Set
   `COLLECTION_MANIFEST_ID`, `EVALUATION_BASIS_SHA256`, and
   `CONSUMPTION_SEMANTICS_ID` from those authenticated inputs, then run:

   ```sh
   "$PY" scripts/extract_detection_floors.py --runs-root "$PRODUCER_RUNS_ROOT" --spec "$EXTRACTION_SPEC" --out "$EXTRACTION_REPORT" --manifest-id "$COLLECTION_MANIFEST_ID" --evaluation-basis-sha256 "$EVALUATION_BASIS_SHA256" --consumption-semantics-id "$CONSUMPTION_SEMANTICS_ID" --hash-bundles
   ```

   Emitted artifact: `$EXTRACTION_REPORT`, schema
   `joulewise.detection_floor_extraction.v1`. Custody:
   `L10_CUSTODY_ROOT/floor-extraction.json`. A report that is not emitted is
   FAIL; a report that honestly records non-extractable cells still supplies
   evidence but cannot satisfy a later step that requires extractable cells.

4. **Mint — ED-FIRST.** Input: the FIRST CHECK 2 pinset and input manifest,
   their named extraction/calibration evidence, and the transaction-head SHA as
   `PROJECT_COMMIT`. Set `FINAL_PINSET_SHA256`, `CALIBRATION_CUSTODY_STORE`, and
   `CONSUMPTION_SEMANTICS_ID` from those authenticated inputs, then run:

   ```sh
   "$PY" scripts/mint_floor_artifact_generalized.py --pinset "$FINAL_PINSET" --pinset-sha256 "$FINAL_PINSET_SHA256" --v2-input-manifest "$V2_INPUT_MANIFEST" --calibration-custody-store "$CALIBRATION_CUSTODY_STORE" --out "$AGGREGATE_FLOOR_ARTIFACT" --single-count-out "$SINGLE_COUNT_STATEMENT" --project-commit "$PROJECT_COMMIT" --project-tree-state clean --consumption-semantics-id "$CONSUMPTION_SEMANTICS_ID"
   ```

   Emitted artifacts: `$AGGREGATE_FLOOR_ARTIFACT`, schema
   `joulewise.detection_floor_artifact.v2`, and `$SINGLE_COUNT_STATEMENT`.
   Custody: the L10 root. Missing output, output-exists refusal, dirty-tree
   acceptance, or a pin/input mismatch is FAIL.

5. **Finalization — ED-FIRST.** Input: the production prospective manifest and
   plan tree, production-pack-bound runs, authenticated verdict, bracket,
   ledger, and the rehearsal aggregate floor. Set `CALIBRATION_LEDGER` to the
   authenticated ledger selected by the transaction, then run:

   ```sh
   "$PY" scripts/finalize_analysis_manifest.py --prospective-manifest "$PACK_ROOT/analysis_manifest_v3.json" --plan-tree "$PACK_ROOT/plan_tree.json" --custody-root "$ANALYSIS_CUSTODY_ROOT" --runs-root "$RUNS_ROOT" --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" --bracket-binding "$RUNS_ROOT/bracket-binding.json" --calibration-ledger "$CALIBRATION_LEDGER" --aggregate-floor-artifact "$AGGREGATE_FLOOR_ARTIFACT" --output-dir "$ANALYSIS_CUSTODY_ROOT"
   ```

   Emitted artifact:
   `$ANALYSIS_CUSTODY_ROOT/<prospective_manifest_id>.finalized.json`, schema
   `joulewise.analysis_manifest.v3.finalized`; replace the placeholder in
   `FINALIZED_MANIFEST` with that emitted filename. Custody: the rehearsal
   analysis directory only. No finalized artifact is FAIL.

6. **Claim gate — ED-FIRST.** Input: the finalized manifest, production corpus,
   aggregate floor, and every evidence root declared by that manifest. Set
   `EVIDENCE_ROOT_ID` to the declared ID and repeat `--evidence-root ID=PATH`
   for every declared root, then run:

   ```sh
   "$PY" -m joulewise analyze-claims --analysis-manifest "$FINALIZED_MANIFEST" --runs-root "$RUNS_ROOT" --evidence-root "$EVIDENCE_ROOT_ID=$PRODUCER_RUNS_ROOT" --floor-artifact "$AGGREGATE_FLOOR_ARTIFACT" --output "$CLAIM_VERDICTS"
   ```

   Emitted artifact: `$CLAIM_VERDICTS`, schema
   `joulewise.claim_verdicts.v1`. Custody: the L10 root, never `CLAIMS_ROOT`.
   Any registered scientific verdict is acceptable, including a structured
   refusal or `not_estimable` outcome, provided the command emits the governed
   verdict artifact. A crash, unregistered refusal spelling, or absent artifact
   is FAIL.

7. **Results fills — ED-FIRST.** Input: the governed FIRST CHECK 4 adapter's
   `$RESULTS_FILL_INPUT`, which must name this run's issued verdict, floor, and
   extraction artifacts. Run:

   ```sh
   "$PY" scripts/render_results_fills.py "$RESULTS_FILL_INPUT" > "$RESULTS_FILLS_MD"; "$PY" scripts/render_results_fills.py --validate-rendered "$RESULTS_FILLS_MD"
   ```

   If `RENDERER-V5-SUCCESSOR-01` installs a differently named successor command,
   the owner must first update the authoritative artifact-flow row; do not guess
   a replacement here. Emitted artifact: validated Markdown at
   `$RESULTS_FILLS_MD`. Custody: the L10 root, marked
   `QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE`; it is never copied into the paper.
   Missing output, `STOP_FILL`, a leftover fill token, or validation failure is
   FAIL.

### C3. PASS, FAIL, and the proposed record

The rehearsal is **PASS** only when every named step emits its required
artifact (or the Strict-validation success transcript), every emitted artifact
is hashed and inventoried, and the Claim gate emits a governed verdict artifact.
The verdict's scientific direction does not decide rehearsal PASS: a supported,
unsupported, `not_estimable`, or registered refusal result can all prove that
the edge executed. A crash, an unregistered refusal spelling, a missing
artifact, a head change, a pack-hash change, or a write outside rehearsal
custody is **FAIL**. Preserve the evidence and route the defect to its owning
kernel row; if no row owns it, request one. L10 does not fix the defect.

Proposed immutable filename:
`l10-sacrificial-rehearsal-record.json`, stored at `$REHEARSAL_RECORD` and
labelled `QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE`. The magistrate must ratify the
record contract before execution. Its minimum fields are:

```json
{
  "record_type": "L10-SACRIFICIAL-REHEARSAL",
  "evidence_use": "QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE",
  "transaction_head_git_sha": "40-hex Git commit",
  "production_pack_path": "repository-relative pack path",
  "production_pack_sha256": "64-hex authenticated pack digest",
  "operator": "human operator identity",
  "started_at_utc": "RFC 3339 timestamp",
  "completed_at_utc": "RFC 3339 timestamp",
  "overall_result": "PASS or FAIL",
  "steps": [
    {
      "step": "Strict validation",
      "result": "PASS or FAIL",
      "command": "exact executed command",
      "input_artifact_sha256": ["64-hex digests"],
      "emitted_artifact_path": ["custody-relative paths"],
      "emitted_artifact_sha256": ["64-hex digests"],
      "exit_code": 0,
      "refusal_or_verdict": null
    }
  ]
}
```

The `steps` array has one record for each of the seven steps and therefore
supplies the required per-step artifact digests and PASS/FAIL result. The
operator and both timestamps make the human execution and its ordering
auditable.

## D. Sequencing

`V5-TRANSACTION-01` is the kernel's exact spelling: **no `_v5` window is
launched before the custodied `l10-sacrificial-rehearsal-record.json` exists at
the transaction head with `overall_result: PASS`.**

## E. What this doc does not do

This document schedules and records the ruled phase; it does not change the
claim edge, add or weaken a refusal, or discharge the missing extraction spec,
final pinset/input manifest, dominance adapter, or results adapter. Any defect
found by the rehearsal is preserved and routed to its owning kernel row, never
fixed in this lane.
