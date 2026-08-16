```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Use one marker-gated successor-family transaction: land the staged estimator branch first inside the transaction, reissue D-079 and every live pin, generate and freshly evidence all three successor packs, obtain Ed's itemized approval, then publish the family marker last.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "0409d75c40488ea3888ffbd7466f4e45dfba31df",
    "head_end": "0409d75c40488ea3888ffbd7466f4e45dfba31df",
    "upstream_end": "0409d75c40488ea3888ffbd7466f4e45dfba31df",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Publication must be one marker-gated family operation",
        "recommendation": "Do all reversible preparation on a private transaction branch, create the cross-authenticating family marker only after every pack byte is final, and make reachability of that marker from origin/main the sole irreversible activation event."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Calibration stage-2 stamping belongs on the staged estimator branch before transaction assembly",
        "recommendation": "Finish and audit it as a descendant of 5449e58, then merge that branch as the first state-changing operation inside the private Phase-2 transaction."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "D-079 needs a genuine successor issuance and complete dual-generation pin migration",
        "recommendation": "Re-derive from the authenticated n=19/38-observation corpus at the integrated estimator head, preserve the old issuance and frozen consumers, and add a versioned successor artifact plus every new live pin in one migration commit."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The approval packet needs an early choice checkpoint and a final exact-byte publication confirmation",
        "recommendation": "Have Ed select every R1 clause-6 reserved semantic before final generation, then require a final GO over the exact candidate tree, pack digests, receipts, marker, D-079 delta, and Phase-3 manifest identity."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Phase-3 baseline supersession and live E-10 must not be folded into pack publication",
        "recommendation": "Publish the successor family first, supersede the baseline manifest afterward, and leave quiet-machine/live E-10 execution to a clean Ed-controlled session after the standing launch gate permits it."
      }
    ],
    "irreversible_point": "The instant the final marker-bearing commit becomes reachable from origin/main.",
    "recommended_pack_id_option": "Uniform _v2 successor IDs, subject to Ed's reserved ruling.",
    "recommended_freeze_numbering_option": "Cross-root chain-monotonic freeze-0002 with explicit predecessor bindings, subject to Ed's reserved ruling."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "for a in docs/process_traces/2026-08-15-readiness-council/council-verdict.md:102 docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md:73 docs/decision_log.md:9667 docs/process_traces/2026-08-15-launch-lineage-consult/consult.md:236 docs/process_traces/2026-08-15-launch-f3-consult/consult.md:225 RUN_STATE.md:3630 TASK_QUEUE.md:506 joulewise/calibration_bracketing.py:568 joulewise/arm_readiness.py:3398 scripts/calibration_ledger_bootstrap.py:327 scripts/project_identity_pins.py:23 scripts/generate_arm_readiness.py:92 configs/calibration/calibration_acceptance_d079_v2.json:1 docs/process/audit-baseline-manifest.json:1; do f=${a%:*}; n=${a##*:}; test -f \"$f\" && test \"$(wc -l < \"$f\")\" -ge \"$n\" || exit 1; done; echo 'anchor_files=14 result=PASS'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["anchor_files=14 result=PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "anchor_files=14 result=PASS"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD; git rev-parse origin/main; git rev-parse impl/wo-detect-pulses-budget; git diff --name-only \"$(git merge-base origin/main impl/wo-detect-pulses-budget)\"..impl/wo-detect-pulses-budget",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["tests/test_powermetrics_fiducial.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_powermetrics_fiducial.py"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; roots=[pathlib.Path(\"configs/campaigns/d117_floor_qwen25_1p5b_v1\"),pathlib.Path(\"configs/campaigns/d117_floor_qwen25_7b_v1\"),pathlib.Path(\"configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1\")]; [print(p.name+\"=\"+json.loads((p/\"plan_tree.json\").read_text())[\"plan\"][\"path\"]) for p in roots]'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d117_floor_qwen25_1p5b_v1=configs/campaigns/d117_floor_qwen25_1p5b_v1/calibration_plan.json",
          "d117_floor_qwen25_7b_v1=configs/campaigns/d117_floor_qwen25_7b_v1/calibration_plan.json",
          "d117_contrast_qwen25_1p5b_vs_7b_v1=calibration_plan.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "d117_contrast_qwen25_1p5b_vs_7b_v1=calibration_plan.json"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py --check",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": ["generation failed: [Errno 2] No usable temporary directory found"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "checked-in bytes match"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R1 clause 6 reserves the listed semantics, successor naming/numbering, marker contract, irreversible publication, and Phase-3 baseline identity to Ed.",
      "needs": "Ed must approve every listed row and the exact final publication packet before origin/main activation."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only consultation sandbox exposes no writable temporary directory, so generator --check and mutation-capable suites could not execute.",
      "needs": "Replay the specified generator checks and canonical suite in the writable re-freeze worktree."
    }
  ]
}
```

## Findings

### F1 — Blocker: one marker-gated family transaction

The governing order is unambiguous: re-freeze once, atomically, and last among pack-byte changes; publication is rule-11 irreversible and requires Ed ([council verdict](docs/process_traces/2026-08-15-readiness-council/council-verdict.md):97; [R1 ruling](docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md):55; [decision log](docs/decision_log.md):9114).

The transaction branch may contain reviewable intermediate commits, including a temporarily red D-079 state. Atomicity is at the protected merge boundary: none of those commits activates a successor family until the complete family marker becomes reachable from `origin/main`.

#### Ordered transaction

1. **Pin the transaction base and open an unpublished integration branch.**

   - Changes: none to pack bytes. Record `origin/main=0409d75c40488ea3888ffbd7466f4e45dfba31df`, the staged-branch ancestor `5449e588fd35107c99cee5a6e65ab4c873db507f`, clean status, merge base, and candidate merge method.
   - Verify:

     ```sh
     git fetch origin
     test "$(git rev-parse origin/main)" = 0409d75c40488ea3888ffbd7466f4e45dfba31df
     git merge-base --is-ancestor 5449e588fd35107c99cee5a6e65ab4c873db507f impl/wo-detect-pulses-budget
     test -z "$(git status --porcelain)"
     ```

   - Invalidates: any prior review if `origin/main` moves or the staged branch ceases to descend from `5449e58`.
   - Rollback: abandon the unpublished transaction branch. `origin/main` and all v1 packs remain untouched.

2. **Finish calibration-side stage-2 stamping on the staged branch.**

   - Changes: add calibration-writer stamping of the authenticated config path and raw digest, enforce outer/inner equality, and consume launch-lineage at writer start. This should be a descendant of `5449e58`, because the staged work and stamping overlap `scripts/validate_powermetrics_fiducial.py`; splitting them creates an avoidable conflict and two C-028 surfaces. The deferral and same-branch coordination are explicit at [decision log](docs/decision_log.md):9521 and [RUN_STATE](RUN_STATE.md):34.
   - Verify:

     ```sh
     PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
       tests.test_powermetrics_fiducial \
       tests.test_calibration_exits \
       tests.test_calibration_writer_crash_matrix \
       tests.test_calibration_live_three_window
     PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
     ```

     Also produce a combined C-028 delta from the original `5449e58` branch point through the final staged head.
   - Invalidates: the staged branch’s old review digest. It does not create a second D-079 staleness event: the estimator change already deliberately invalidates D-079.
   - Rollback: repair or replace the unpublished stage-2 commit before transaction assembly. Do not merge a partial variant to main.

3. **Land successor lifecycle and launch-lineage machinery before any successor pack bytes.**

   - Changes: implement and test:

     - R1 content-bound receipt classes, governed changed-set enumeration, complete read routing, exact-key schemas, refusal vocabulary, environment-fingerprint recording, and validator-before-horizon-removal.
     - Freeze-receipt v2 and a cross-pack family-marker schema.
     - Dual-generation read routing so predecessor packs remain verifiable.
     - Exact launch derivation descriptors, including `axi_attempt_v1`, layout `TOP/axi_attempt_bundles/<manifest-id>/<entry-id>/a<ordinal>`, `TOP = parents[3]`, exact locator projection, and authentication of manifest/config/entry/digest/attempt grammar ([launch F3](docs/process_traces/2026-08-15-launch-f3-consult/consult.md):203; [decision log](docs/decision_log.md):9592).
     - A governed D-079 successor reissue command. Do not repurpose the existing bootstrap path, which is pinned to initial issuance ([calibration bootstrap](scripts/calibration_ledger_bootstrap.py):145).
   - Verify:

     ```sh
     PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
       tests.test_arm_readiness_lifecycle \
       tests.test_arm_readiness_schemas \
       tests.test_arm_readiness_registry \
       tests.test_arm_readiness_successor_family \
       tests.test_launch_lineage
     PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
     ```

     The new tests must include unrecorded-read refusal, non-enumerated plan-tree mutation refusal, unknown-key refusal, partial-family refusal, mixed-generation refusal, fake intermediate AXI locator refusal, and predecessor-pack preservation.
   - Invalidates: any earlier R1 schema draft, refusal registry, or marker fixture.
   - Rollback: revise tooling on the private branch. No pack has been generated or activated.

4. **Merge the completed staged branch inside the private transaction, before D-079 derivation.**

   - Changes:

     ```sh
     git merge --no-ff impl/wo-detect-pulses-budget
     ```

     This is the first transaction state change. It brings the nine-file delta rooted at `5449e58`, plus calibration stage-2. It must not land independently on main: D-138 requires this branch to merge only inside the transaction that reissues D-079 and every dependent pin ([decision log](docs/decision_log.md):9609).
   - Verify: run the canonical suite once in the intentionally stale state. Require every failure to be the governed D-079 estimator-pin mismatch fan-out and no unrelated failure. Compare the list against D-138’s live invariant rather than blindly re-keying tests.
   - Invalidates: the issued D-079 acceptance because `joulewise/powermetrics_fiducial.py` is one of its four estimator-source pins. Consequently, every successor consumer of that issuance is stale.
   - Rollback: discard and recreate the unpublished transaction branch. Do not “fix” this checkpoint by pointing live tests at synthetic fixtures.

5. **Reissue D-079 from the integrated estimator head and migrate all successor pins together.**

   - Changes: the transaction lead—not a pack generator—derives a new versioned acceptance artifact from:

     - The authenticated committed D-079 ledger/head.
     - The complete 38-observation prior set at sequence 76.
     - The ruled `n=19` threshold corpus and custody/disposition records.
     - Exact bytes of all four estimator sources at the integrated transaction head.

     The tool interface should resemble:

     ```sh
     python3 scripts/reissue_calibration_acceptance.py \
       --predecessor configs/calibration/calibration_acceptance_d079_v2.json \
       --ledger runs/calibration_observation_ledger.jsonl \
       --ledger-head configs/calibration/calibration_ledger_head.json \
       --custody-manifest docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-custody-manifest.json \
       --disposition-table docs/process_traces/2026-08-06-d079-issuance-coldgate/ISSUANCE-disposition-table.json \
       --output "$TX_STAGE/calibration_acceptance_successor.json"
     ```

     Preserve `configs/calibration/calibration_acceptance_d079_v2.json` and the existing frozen extraction specs. Add successor-versioned artifacts instead.

     One D-079 migration commit must include:

     - The successor acceptance path, ID, file SHA, derivation digest, estimator pin map, ledger/head bindings, and custody bindings.
     - A registry/map in `joulewise/calibration_bracketing.py` supporting both predecessor and successor; do not merely replace the singular old constant ([calibration bracketing](joulewise/calibration_bracketing.py):44).
     - The successor ID in ARM’s issued-acceptance routing ([ARM readiness](joulewise/arm_readiness.py):2675).
     - New versioned 1.5B and 7B extraction specs; the old specs remain historical.
     - Successor generator constants and acceptance-owner inputs for all three packs.
     - Every successor T-0 author/consumer pin.
     - Exact-pin, stale-pin, old-pack, new-pack, and fixture tests.

   - Verify:

     ```sh
     python3 scripts/reissue_calibration_acceptance.py --check \
       --artifact "$TX_STAGE/calibration_acceptance_successor.json"
     PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
       tests.test_calibration_ledger \
       tests.test_calibration_bracketing \
       tests.test_floor_extraction \
       tests.test_floor_mint_estimator \
       tests.test_arm_readiness_evidence_author \
       tests.test_powermetrics_fiducial
     rg -n 'd079_calibration_acceptance_v2_n19|calibration_acceptance_d079_v2.json' \
       joulewise scripts configs tests
     ```

     Produce a member-by-member predecessor/successor delta for all 19 accepted observations. Equal scientific outputs are allowed but must be independently re-derived; unequal membership or thresholds require an explicit science delta and cold review.
   - Invalidates: all D-079 candidate output if any of the four estimator files, ledger/head, corpus, custody inputs, or reissue tool changes afterward.
   - Rollback: discard the migration commit and candidate artifact. The predecessor issuance remains byte-for-byte valid for predecessor packs.

6. **Prepare dry-run successor families and the Ed choice packet.**

   - Changes: generate candidates outside canonical pack roots for each viable Ed naming/numbering choice. No candidate is published.

     Pack-ID options—Ed reserved:

     - **A, recommended:** uniformly rotate `_v1` to `_v2`.
     - **B:** use an explicit succession suffix such as `_s1`.
     - **C:** use a dated successor suffix. Strong custody clarity, but it embeds scheduling into identity.

     Freeze numbering options—Ed reserved:

     - **A, recommended:** `freeze-0002` in every new root, with explicit `freeze-0001` predecessor bindings.
     - **B:** generation-qualified receipt IDs plus an explicit predecessor ordinal.
     - **C:** restart at `freeze-0001` in new roots. Valid only with strong chain bindings, but operationally ambiguous and not recommended.

     Every choice must rotate consistently across pack IDs, directories, plan IDs, evidence roots, custody roots, family ID, and tags. R1 expressly reserves both questions ([R1 ruling](docs/process_traces/2026-08-15-r1-freeze-lifecycle-consult/coldgate-adjudicator-ruling.md):73).

     Generator requirements:

     - Alpha and beta emit `plan.path: "calibration_plan.json"` and always put `--plan <absolute execution-boundary path>` into the successor reservation argv. Their current committed values are full repository paths, while gamma already conforms; this is the precise R2 defect ([decision log](docs/decision_log.md):8940; current alpha site [generate_configs.py](configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py):1308; beta site [generate_configs.py](configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py):908).
     - `launch_lineage_required` appears in every successor collection config, including successor copies of shared bound/reference configurations.
     - Plan trees freeze the ordinary and AXI derivation descriptors.
     - All T-0 source hashes are re-derived at the exact successor content head; no current mint-trust pin is copied ([decision log](docs/decision_log.md):9667).
     - `draft_status` is generator-derived and freeze-aware. M-2 retires per successor pack only when that is true; retain only one informational operator note ([decision log](docs/decision_log.md):9154).

   - Verify:

     ```sh
     python3 configs/campaigns/<alpha-successor>/generate_configs.py --output-root "$TX_STAGE"
     python3 configs/campaigns/<beta-successor>/generate_configs.py --output-root "$TX_STAGE"
     python3 configs/campaigns/<gamma-successor>/generate_configs.py --output-root "$TX_STAGE"
     python3 configs/campaigns/<alpha-successor>/generate_configs.py --check --output-root "$TX_STAGE"
     python3 configs/campaigns/<beta-successor>/generate_configs.py --check --output-root "$TX_STAGE"
     python3 configs/campaigns/<gamma-successor>/generate_configs.py --check --output-root "$TX_STAGE"
     jq -e '.plan.path == "calibration_plan.json"' "$TX_STAGE"/configs/campaigns/*/plan_tree.json
     python3 scripts/generate_arm_readiness.py verify-family \
       --root "$TX_STAGE" --require-launch-lineage --check-t0-sources
     ```

   - Invalidates: all candidates if Ed changes an identity/numbering choice, the transaction head moves, or any generator/source byte changes.
   - Rollback: discard the external staging directory; no repository or published state is affected.

7. **Lock Ed’s semantic choices, then begin pack-byte generation—last.**

   - Changes: apply the selected identifiers and policies, then generate the three canonical successor roots together. From this point onward, no lifecycle, generator, estimator, writer, mint, or other pack-input code changes are allowed.
   - Verify: generator `--check` for all three; exact inventory equality; old-pack byte hashes unchanged; no duplicate IDs/custody roots; all successor configs carry the lineage flag; real-pack FROZEN_PLAN resolver tests pass.
   - Invalidates: all provisional pack digests, manifests, evidence, and receipts whenever any pack byte changes.
   - Rollback: discard all three successor roots together and regenerate. Never preserve one candidate while rebuilding another.

8. **Freshly re-author all 33 content receipts and successor evidence.**

   - Changes: re-derive every prior evidence row under the successor schema and exact reviewed content head. None of the 33 v1 receipts is copied, revalidated, reinterpreted, or grandfathered. Apply the ruled taxonomy: `RE_DERIVABLE` rows are derived at ARM and store no validity; execution-bound rows retain their binding/horizon until Ed’s environment ruling says otherwise ([decision log](docs/decision_log.md):9082).
   - Verify:

     ```sh
     python3 scripts/author_arm_readiness_evidence.py author-family \
       --family-spec configs/campaigns/<successor-family-spec>.json
     python3 scripts/author_arm_readiness_evidence.py verify-family \
       --family-spec configs/campaigns/<successor-family-spec>.json \
       --require-complete-read-routing \
       --require-changed-set-enumeration
     ```

     Require exactly 33 fresh successor rows, zero v1 receipt consumption, exact class-policy registry matches, complete dependency manifests, and recorded environment facts where required.
   - Invalidates: all 33 new receipts if their derivation head, dependency manifest, changed-set registry, policy registry, or any governed dependency changes.
   - Rollback: discard the complete successor evidence set and re-author all affected rows. Never patch a receipt in place.

9. **Generate U11 projections, freeze-receipt v2 records, and the family marker candidate.**

   - Changes:

     - Produce all three identity projections using the D-134 enumerated-slot mechanism.
     - Produce `freeze-0002` or Ed’s selected equivalent for all three roots.
     - Bind each receipt to its predecessor pack ID/path/digest, predecessor freeze receipt path/SHA, predecessor identity projection, predecessor evidence root, successor family/role, exact successor pack digest and algorithm, and family-marker path.
     - Create one marker outside the pack roots only after all pack bytes are final. Receipts should bind the marker path/family identity rather than its SHA to avoid a hash cycle.
     - The marker should list all three roles, pack IDs/paths/digests, digest algorithm, predecessor bindings, v2 receipt and projection hashes, evidence roots, reviewed content parent/tree, and activation rule. Missing, duplicate, mixed-generation, or mismatched members must refuse.

   - Verify:

     ```sh
     python3 scripts/project_identity_pins.py freeze --family-spec <family-spec>
     python3 scripts/generate_arm_readiness.py freeze-family --family-spec <family-spec>
     python3 scripts/generate_arm_readiness.py verify-family \
       --family-marker <marker-path> \
       --require-predecessors \
       --require-complete-family \
       --require-pack-digest-algorithm
     PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
     ```

     Run independent deltas for R1, D-079, FROZEN_PLAN, launch lineage/AXI, T-0 source pins, M-2, projections, receipts, and marker graph.
   - Invalidates: any receipt, projection, pack digest, or marker if a single pack byte changes. The correct response is to discard and rebuild the entire three-pack finalization layer.
   - Rollback: keep the PR unpublished or close it. The current family remains the only active family.

10. **Ed’s exact-byte approval and irreversible publication.**

   Ed must review the exact candidate commit/tree and approve R1 clause 6 item by item ([decision log](docs/decision_log.md):9117):

   1. Freshness semantics for every evidence row and the exact class-policy mapping.
   2. Horizons, ARM-to-consume budget, and which volatile predicates re-probe at consumption.
   3. Interpreter/platform fingerprint comparison semantics and divergence disposition.
   4. Exact refusal-code spellings and type labels.
   5. All successor pack IDs, family/custody IDs, and cross-chain freeze numbering.
   6. Freeze-receipt v2 predecessor-binding set, marker schema/path, complete-family predicate, and activation semantics.
   7. The exact one-time successor publication plus the exact Phase-3 baseline-manifest identity/path/schema.

   The packet should additionally show:

   - The final D-079 corpus/delta and every migrated pin.
   - The staged-branch merge commit and combined C-028 delta.
   - All three generator checks and plan-path/argv proof.
   - T-0 source inventory and hashes.
   - Launch-lineage config census and AXI release-gate matrix.
   - All 33 fresh receipt records.
   - Pack, projection, freeze-receipt, evidence-root, and marker hashes.
   - Canonical suite, focused suites, fresh cold review, and unresolved production-science rows.

   Immediately before publication:

   ```sh
   git fetch origin
   test "$(git rev-parse origin/main)" = "$BASE_HEAD"
   gh pr checks <phase2-pr> --watch
   git diff --exit-code "$ED_REVIEWED_COMMIT^{tree}" HEAD^{tree}
   ```

   **Exact irreversible point:** execution of the protected merge/fast-forward that first makes the complete family marker reachable from `origin/main`, for example:

   ```sh
   gh pr merge <phase2-pr> --merge
   ```

   Before that moment, rollback is abandonment of the unpublished PR. After it, do not revert, delete, repair, or overwrite the active successor packs: D-131 requires another successor family with new IDs and custody roots.

   Post-merge verification:

   ```sh
   git fetch origin
   test "$(git rev-parse origin/main^{tree})" = "$ED_APPROVED_PUBLICATION_TREE"
   python3 scripts/generate_arm_readiness.py verify-family \
     --family-marker <marker-path> --require-origin-main
   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
   ```

### F2 — Calibration stage-2 placement

The calibration-side writer work should be prepared **before** transaction assembly but on `impl/wo-detect-pulses-budget`, not independently on `main`. It then enters main only through step 4 of the transaction. This:

- Keeps the overlapping validation-script work in one branch.
- Gives it its own C-028 review before the larger family diff.
- Ensures the D-079 reissue sees the final integrated estimator/writer head.
- Avoids discovering a writer conflict after evidence authoring has started.

The staged branch’s current nine-path footprint was verified at `5449e58`; the repository itself records why the calibration writer was fenced out of the earlier campaign-side work ([T9 report](docs/run_reports/2026-08-16-t9-session.md):403).

### F3 — D-079 choreography and pin graph

D-079 must be a new issuance, not a new hash pasted into the old artifact. D-138 identifies the four governed estimator inputs and forbids fixture re-keying ([decision log](docs/decision_log.md):9609). The old acceptance, old extraction specs, old plan trees, and historical evidence remain byte-stable.

The successor migration must be dual-generation:

- Old pack → old acceptance path/ID/SHA → old extraction specs.
- Successor pack → successor acceptance path/ID/SHA → successor extraction specs.

The current live pin surfaces include `joulewise/calibration_bracketing.py`, `joulewise/arm_readiness.py`, both floor extraction specs, all three pack generators/plan trees/acceptance-owner inputs, T-0 evidence authoring, and exact-pin tests. Historical decision logs, reports, paper prose, fixtures intended to prove the old issuance, and predecessor pack bytes are not migration targets.

If re-derivation changes the accepted 19-member set, thresholds, or any science-facing output, stop the transaction for a D-079 cold review. That is not an ordinary pin refresh.

### F4 — Preparation and approval-session shape

Nearly everything can be prepared before Ed’s final GO:

- Calibration stage-2 and its C-028 audit.
- R1 schema/tooling/refusal/read-routing implementation.
- AXI descriptor and release-gate tests.
- D-079 reissue tooling and corpus authentication.
- Merge simulation and conflict resolution.
- Candidate D-079 issuance and member delta.
- Generator repairs and successor templates.
- ID/numbering variants.
- Dry-run successor roots, evidence enumeration, marker validation, and packet templates.
- Focused tests, full suite, and delta-review scripts.

What must wait for Ed:

- Locking reserved policy semantics.
- Locking pack IDs, family/custody IDs, and freeze numbering.
- Locking receipt-v2 and marker semantics.
- Final canonical generation using those choices.
- Final exact-byte confirmation.
- Publication to `origin/main`.
- Phase-3 baseline identity.
- Any physical launch or other Ed-only action.

Recommended shape: four logical sessions, not one long undifferentiated sitting.

1. Staged-branch calibration completion and focused audit.
2. Private transaction assembly, D-079 derivation, generators, and dry-run family.
3. Ed approval session: choices first, exact candidate confirmation second.
4. Protected publication and post-publication verification.

Phase 3 is a fifth, separately auditable session.

### F5 — Phase 3 and live-lineage boundary

After successful publication, create a **successor** baseline manifest; do not retrofit the current v1 manifest. It must add `pack_digest_algorithm`, the chain-template coverage note, predecessor-manifest binding, all successor pack/receipt/projection/evidence/marker identities, and the reviewed/effective publication head. Then run the focused L1/L5/L7 re-audit plus complete coverage enumeration, as required by [council verdict](docs/process_traces/2026-08-15-readiness-council/council-verdict.md):68 and :102.

The launch-lineage Phase-2 list also asks for fresh `window.env`, chain, launch manifest, T-0 evidence, ARM receipt, and live E-10 ([launch-lineage consult](docs/process_traces/2026-08-15-launch-lineage-consult/consult.md):228). Split that safely:

- Inside re-freeze: freeze the mechanism, config flags, locator descriptors, bindings, and exact T-0 **source** hashes.
- After publication: create fresh environment/chain/T-0/ARM artifacts against the published successor head in a clean lead-controlled session.
- Live E-10 remains behind the standing council/Ed launch gate. It cannot be silently treated as a prerequisite that authorizes a funded launch during an agent session.

## Residual risk

A botched unpublished candidate costs review time and requires rebuilding all three successor roots. A botched **published** family consumes the one planned successor generation: the repository cannot repair or revert it in place and would need a successor-of-successor, new IDs/custody roots, another Ed approval, new cold review, another baseline supersession, and repetition of affected audits.

Delta re-audits should be independently signed off for:

- Staged estimator plus calibration-writer integration.
- D-079 corpus derivation and complete pin graph.
- R1 class policies, changed-set registry, read routing, and refusal vocabulary.
- Alpha/beta `plan.path` and `--plan` reconciliation.
- Launch-lineage config census and AXI descriptor projection.
- T-0 source supersession.
- M-2 retirement conditions.
- U11 projection and freeze-v2 predecessor bindings.
- Complete-family marker/hash graph.
- Phase-3 baseline supersession and coverage universe.

Standing escalation/cold gates fire on:

- Any second fix round or repeated failure signature.
- Any contract/schema or refusal-vocabulary change after cold review.
- Any contradiction in decisive proof.
- Any unexpected D-079 scientific-output change.
- Any mutation after the final reviewed content head.
- Any origin/main drift before publication.
- Any incomplete or mixed-generation family result.
- Any attempt to grandfather a v1 receipt.
- Any attempt to run quiet-machine measurement, powermetrics capture, production campaign, or live E-10 while an agent session is active.