```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S1 should not merge while its integration full suite has 533 outcomes; retain strict mock refusal, repair fixtures, and repin paper receipts before a fresh merge gate.",
  "workspace": {
    "base_requested": "42e2af3e460af1aef021ec2b5004a1121cdd4b52",
    "base_mode": "informational",
    "head_start": "c7593edbcaacdd2c7bbf0175ad315fdbafe5e275",
    "head_end": "c7593edbcaacdd2c7bbf0175ad315fdbafe5e275",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": "feat/2026-09-26-bfgs-s1-bundles"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"B1","severity":"blocker","file":"scripts/run_campaign.py","line":9032,"text":"The integration full suite is red with 115 failures and 418 errors; the earlier targeted-suite MERGE ruling is overtaken by this evidence."},
      {"id":"B2","severity":"blocker","file":"joulewise/bundle_read.py","line":345,"text":"G2 mock members are correctly refused by claim-bearing window checks; legacy expectations must be classified and repaired without admitting not_applicable as a pass."},
      {"id":"B3","severity":"blocker","file":"configs/paper_supply/supply_map.json","line":115,"text":"G9 has stale receipt and dependent inventory pins for three paper-custody fixture families after S1 changed validator sources."},
      {"id":"B4","severity":"blocker","file":"tests/test_calibration_live_three_window.py","line":120,"text":"G1, G3–G8, G10, and downstream G11 require authenticated synthetic evidence or precise refusal assertions across 36 test modules."},
      {"id":"S1","severity":"should_fix","file":"docs/agent_playbook.md","line":37,"text":"Move the full integration suite before each remaining S1 fix-head gate and before merge."}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"inspection","cmd":"git rev-parse HEAD origin/main","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["c7593edbcaacdd2c7bbf0175ad315fdbafe5e275","e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1"]},
      "expected":{"exit_code":0,"tail_regex":"c7593edbcaacdd2c7bbf0175ad315fdbafe5e275"}
    },
    {
      "id":"V2","kind":"inspection","cmd":"/opt/homebrew/bin/python3 -B -c 'import json,collections; p=\"/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/62-regression-inventory.jsonl\"; x=[json.loads(s) for s in open(p)]; print(len(x),dict(sorted(collections.Counter(r[\"group\"] for r in x).items())))' ","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["533 {'G1': 135, 'G10': 11, 'G11': 36, 'G2': 98, 'G3': 62, 'G4': 40, 'G5': 81, 'G6': 20, 'G7': 17, 'G8': 10, 'G9': 23}"]},
      "expected":{"exit_code":0,"tail_regex":"^533 .*'G2': 98.*'G9': 23"}
    },
    {
      "id":"V3","kind":"inspection","cmd":"git status --short --branch","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## feat/2026-09-26-bfgs-s1-bundles...origin/feat/2026-09-26-bfgs-s1-bundles"]},
      "expected":{"exit_code":0,"tail_regex":"^## feat/2026-09-26-bfgs-s1-bundles"}
    }
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"The original S1 write scope excludes paper supply-map pins; adding the repin requires a lead-authorized integration scope and fresh final-head review.","needs":"Authorize a repin writer and review the combined merge candidate."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"This read-only consult checked the inventory and code but did not rerun the full suite; the 115/418 result and main-green baseline are supplied by the integration run and scout.","needs":""}
  ]
}
```

## Findings

**B1 — BLOCKER: keep S1 unmerged at this head.** I confirmed S1 at `c7593edb`, the integration tree at `42e2af3e`, and all 533 entries in the [scout inventory](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/62-regression-inventory.jsonl). The [scout report](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/62-regression-scout-report.md:87) records 115 failures and 418 errors on the integration full suite. The earlier [final pass](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/51-fable-finalpass-ruling.md:137) explicitly relied on targeted suites and deferred a full run until after merge. The new result changes that merge decision. I see no reason yet to split S1: the groups have bounded repairs, while splitting its gate and source pins would create more intermediate states to review.

**B2 — BLOCKER: retain mock refusal at window and claim completion.** [Final texts v1.1 §7–8](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:113) says a mock controller writes `not_applicable` without a probe and the bundle reader admits that state. Its [§12](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:125) says a consumer claiming numbers refuses the **whole window** on `not_applicable`; §18 preserves mock *bundle reduction*. The current refusal in [bundle_read.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/bundle_read.py:345) follows that boundary. [run_campaign.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/scripts/run_campaign.py:9032) reaches it during completion.

My choice for S1 closure is to change G2 tests that expect a successful window or claim verdict to expect the named refusal and absence of a successful claim artifact, while retaining positive mock bundle-reduction tests. This requires no production change and keeps the ruled gate strict. A useful non-claim campaign completion record may still be worth designing, but it needs an explicit ruling of which fields can be written and how `not_applicable` remains visible; it must never let mock energy enter final analysis or a whole-window claim.

**B3 — BLOCKER: repin G9 in the same merge unit as final S1 source bytes.** The three affected roles are `fixture.d165_closeout`, `fixture.reported_energy_parents`, and `fixture.whole_window_verdict` in [supply_map.json](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/configs/paper_supply/supply_map.json:115). The receipt hashes the current validator source, including owning modules; [paper_custody.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/joulewise/paper_custody.py:731) defines that census, and [test_paper_custody.py](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_paper_custody.py:161) shows that a changed receipt also changes its inventory and map pins. Receipts corroborate the Git-anchored map; they do not create authority ([contract](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/docs/contracts/paper_supply_custody.md:24)).

The lead may make the repin, or explicitly scope a separate writer to it. S1’s original `WRITE_SCOPE` does not grant that file. First freeze the production source diff; then independently calculate the three validator-source digests, regenerate canonical synthetic receipts, regenerate inventories containing those receipt digests, and update their expected hashes in the supply map. Review the source change and the full digest chain, including stale-source and tampered-receipt refusals. These are **non-issuing fixture roles**, but their custody machinery sits beside claim-bearing paper inputs, so an independent reviewer and the lead’s final combined-diff review are warranted. Land the repin with S1 in one PR or another atomic merge unit that presents a green main state. A repin before or after S1 as a standalone main merge leaves one intermediate head stale.

**B4 — BLOCKER: repair fixtures in parallel, with disjoint file ownership.** The inventory assigns 376 primary outcomes to G1, G3–G8 and G10, plus 36 G11 outcomes that need another run after their parents are fixed ([scout groups](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/62-regression-scout-report.md:91)). Four seats are justified by the 36 affected modules. Each list below is an exact proposed `WRITE_SCOPE` under `tests/`; the named in-file builders belong to the same seat.

| Seat | Test files under `tests/` | Fixture ownership |
|---|---|---|
| Campaign and CLI | `test_analysis_integration.py`, `test_audit_amplification.py`, `test_cli.py`, `test_cli_run.py`, `test_launch_window.py`, `test_package_bundle_pack.py`, `test_partial_record_enclosure.py`, `test_pipeline_smoke_tail.py`, `test_powermetrics.py`, `test_run_campaign.py` | Owns `test_run_campaign.py`’s `_write_bundle` and campaign builders; also handles overlapping G2 expectations. For G2-only coverage add `test_experiment.py`, `test_collector_analysis_manifest_id.py`, `test_corpus_strict_validation.py`. |
| Window and analysis | `test_aggregate.py`, `test_analysis_claims.py`, `test_analysis_finalizer.py`, `test_check_window_provenance.py`, `test_d165_dominance_closeout.py`, `test_dominance_closeout.py`, `test_floor_extraction.py`, `test_phase_share.py`, `test_whole_window.py`, `test_whole_window_selection.py`, `test_window_duration_margins.py` | Owns the bundle builders inside those modules. |
| Artifacts and minters | `test_custody_mode_inventory.py`, `test_d117_floor_qwen25_1p5b_plan.py`, `test_d117_floor_qwen25_7b_plan.py`, `test_detection_floor.py`, `test_floor_mint_estimator.py`, `test_mint_floor_artifact.py`, `test_mint_floor_artifact_generalized.py`, `test_uncertainty_p2029.py` | Owns local artifact and floor-fixture builders. |
| Calibration and attachment | `test_arm_readiness_dry_run.py`, `test_arm_readiness_evidence_author.py`, `test_bracket_binding_cli.py`, `test_calibration_bracketing.py`, `test_calibration_live_three_window.py`, `test_epoch_continuation.py`, `test_p2038_production_path.py`, `receipt_corpus.py` | Owns the [three-window synthetic custody builder](/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96/tests/test_calibration_live_three_window.py:120) and the shared receipt helper. |

Ordered work within those scopes:

1. Classify each failing test as a valid positive fixture or an intentional malformed-input negative test. Preserve the latter’s defect and assert the *earliest ruled refusal*.
2. For positive bundle fixtures, create complete metadata, events and config; bind `metadata.config_sha256` to the exact config bytes; provide an authenticated pre/post battery pair and its raw bytes where the member is claim-bearing. Do not add synthetic IDs to the closed historical set.
3. For calibration fixtures, write parseable `instrument_evidence.json`, make ledger locators resolve to its exact digest, add valid capture pairs where required, and rebuild dependent hashes and receipts. For attachment fixtures, supply the pair and update manifest hashes.
4. For synthetic powermetrics controller tests, inject a deterministic passing battery runner. Keep a negative check that a real non-mock default runner still probes and refuses on failure.
5. Rerun the affected modules, then the integration full suite. Triage G11 by its new first failure; only then adjust exact output or refusal-precedence assertions. Preserve negative controls for deleted raw files, mismatched digests, charging, absent custody bytes, and mock claim refusal. Do not replace them with broad “some exception” assertions or production exemptions.

**S1 — SHOULD-FIX: make the full suite a pre-merge gate on every integrated fix head.** Keep focused checks for fast diagnosis, then run `/opt/homebrew/bin/python3 -B -m unittest discover -s tests` on the exact combined tree after each fix head is integrated, including the receipt repin, and again on the final merge candidate. That one sequence change closes the gap left when all prior gates selected only targeted modules ([final-pass A4](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/51-fable-finalpass-ruling.md:137)). No NIT finding changes the merge decision.

## Residual risk

I did not rerun the suite in this read-only consult. The scout paired representative failures against main, but a fresh full-suite pass on the final integrated head is still required. G11 may expose an independent output-contract question after primary repairs. The scout also reports one `/tmp` hard-link fixture issue on both trees; use a same-filesystem temporary location or a copy when replaying that test, without treating the environment error as an S1 pass.

RECOMMEND: Hold S1’s merge; retain strict `not_applicable` window refusal, repair fixtures in disjoint seats, repin the three paper roles with final source bytes, then require a green full integration suite and fresh lead review.