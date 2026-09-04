```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 2 cures the renderer-local bypass, but the canonical join still authorizes floor cells unrelated to the A/B arms; not landable.",
  "workspace": {"base_requested":"18b4f9c3ab3b9331cd7b7fc5cf44c539d293ec25","base_mode":"exact","head_start":"18b4f9c3ab3b9331cd7b7fc5cf44c539d293ec25","head_end":"18b4f9c3ab3b9331cd7b7fc5cf44c539d293ec25","upstream_end":"18b4f9c3ab3b9331cd7b7fc5cf44c539d293ec25","branch":"feat/2026-09-04-gamma-claim-renderer"},
  "pathspec": ["docs/process_traces/2026-09-04-gamma-renderer/07-delta-reaudit-round-2.md"],
  "unowned_dirty": [],
  "verdict": {
    "result": "NOT_LANDABLE",
    "same_signature": "YES — F1 is the same floor-lineage authorization signature: authenticated floor bytes still do not prove that the selected cells authorize the named A/B arms.",
    "findings": [
      {"id":"F1","severity":"blocker","title":"The canonical join accepts floor cells unrelated to the A/B arms","file_line":"joulewise/analysis_engine/artifact.py:2298-2335","text":"The new seam checks that each source cell exists, is eligible, and equals the claim-side numeric copy, but never binds that cell's condition_family_id to the corresponding ordered arm gate. Authenticated unrelated cells can therefore supply a lower F and authorize a supported verdict.","counterfactual":"The landed fixture validates with arm families cond-a/cond-b but embedded source-cell families cf-1/cf-2 and renders PG-08 supported. A four-cell replay selected unrelated cells with max gate 1.2 instead of the applicable cells' 12.0; validation remained empty and PG-08 rendered supported.","cure_shape":"At the canonical pre-render seam, bind each ordered exact resolution to the corresponding arm gate and require the authenticated cell's scientific/request identity, beginning with key.condition_family_id, to equal the arm's registered identity; pin the authenticated wrong-cell substitution."}
    ],
    "dispositions": [
      {"id":"contract-B1","result":"CURED","evidence":"V2/V3: production v1 refusal paths and sidecar validator pass under the superseding addendum."},
      {"id":"contract-B2","result":"CURED","evidence":"V1: refused G2-a remains terminal."},
      {"id":"contract-B3","result":"CURED","evidence":"V1: contrast absence does not issue refusal prose."},
      {"id":"contract-B4","result":"CURED","evidence":"V1: valid partial outcomes remain reachable."},
      {"id":"contract-S1","result":"CURED","evidence":"V4: both registry checks pass."},
      {"id":"contract-S2","result":"CURED","evidence":"V6: v1 producer, claims ladder, artifact flow, and frozen publication renderer are unchanged from origin/main."},
      {"id":"execution-B1","result":"NOT CURED","evidence":"V1 stops the old copied-value forgery, but V5 proves an authenticated wrong-cell substitution still supplies rendered F."},
      {"id":"execution-B2","result":"CURED","evidence":"V1: missing contrasts stop."},
      {"id":"execution-B3","result":"CURED","evidence":"V1: partial/refusal branches render only after canonical validation."},
      {"id":"execution-B4","result":"CURED","evidence":"V3: both named producer integration regressions pass."},
      {"id":"execution-S1","result":"CURED","evidence":"V1 includes boundary and re-content-addressed attacks."},
      {"id":"delta-F1","result":"CURED","evidence":"V1: the selected-prefill/not-estimable copied-floor mutation now yields structured all-STOP_FILL."},
      {"id":"consult-F1","result":"NOT CURED","evidence":"V5: authorization moved to the canonical seam but remains incomplete for source-cell applicability."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_results_fill_gamma","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 1.412s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 2 tests in .*s[\\s\\S]*OK"}},
    {"id":"V2","kind":"test","cmd":"python3 -m unittest tests.test_analysis_engine_artifact tests.test_claim_side_bound","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 5 tests in 0.089s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 5 tests in .*s[\\s\\S]*OK"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_analysis_integration.AnalysisIntegrationTests.test_v3_abba_engine_and_d093_refusal_precedence tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 1.306s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 2 tests in .*s[\\s\\S]*OK"}},
    {"id":"V4","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 13 tests in 2.730s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 13 tests in .*s[\\s\\S]*OK"}},
    {"id":"V5","kind":"other","cmd":"python3 -c 'import base64,json,sys; from tests.test_results_fill_gamma import _base_gamma_artifact,_render; from joulewise.analysis_engine.artifact import validate_claim_verdicts; a=_base_gamma_artifact({\"claim_side_bound_j\":0.25,\"estimate_j\":30.0,\"overlap_count\":5}); f=json.loads(base64.b64decode(a[\"inputs\"][\"floor_artifact\"][\"embedded_bytes_base64\"])); e=validate_claim_verdicts(a); ac=[g[\"condition_family_id\"] for g in a[\"contrasts\"][0][\"floor\"][\"arm_gates\"]]; fc=[c[\"key\"][\"condition_family_id\"] for c in f[\"cells\"]]; print(e); print(ac); print(fc); print(_render(a)[\"rows\"][\"PG-08\"]); sys.exit(1 if not e and ac != fc else 0)'","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["[]","['cond-a', 'cond-b']","['cf-1', 'cf-2']","supported — Qwen3-8B used more prompt-processing energy per request than Qwen3-1.7B under the registered comparison"]},"expected":{"exit_code":0,"tail_regex":".*(floor_lineage|condition_family).*"}},
    {"id":"V6","kind":"inspection","cmd":"git diff --exit-code origin/main -- joulewise/analysis_engine/__init__.py scripts/render_results_fills.py docs/contracts/claims_ladder.md docs/process/v5-artifact-flow.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V7","kind":"inspection","cmd":"git show --check --oneline HEAD && git show --check --oneline 146e7ac2","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["18b4f9c3 gamma-renderer: fix round 2 (Sol xhigh) under R2-FL-1 floor-lineage authorization","146e7ac2 gamma-renderer: fix round 1 (resumed under the R2 sidecar amendment) (Sol xhigh)"]},"expected":{"exit_code":0,"tail_regex":"18b4f9c3[\\s\\S]*146e7ac2"}}
  ],
  "flags": [
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"The preflight prohibited the canonical full suite and tests outside the named renderer, producer/validator, and registry checks.","needs":"Lead reruns broader verification only after the blocker is cured."}
  ]
}
```

## Findings

### F1 — blocker — the canonical join accepts floor cells unrelated to the A/B arms

At `joulewise/analysis_engine/artifact.py:2298-2335`, the new join proves cell existence, eligibility, and copied component equality. It never compares the authenticated cell's `key.condition_family_id` with the corresponding ordered `arm_gates[].condition_family_id` checked at `:2517-2540`. V5 executes the defect in the landed fixture: validator `[]`, arms `cond-a/cond-b`, source cells `cf-1/cf-2`, and a supported PG-08 verdict. An extended four-cell replay selected authenticated unrelated cells with max gate 1.2 instead of the applicable cells' 12.0 and again rendered support. Thus an R2-FL-1 cell-ID/applicability mismatch is not terminal.

The old re-content-addressed copied-value attack and the not-estimable sibling bypass are cured, but the authorization invariant is not. **Same-signature: YES, decisively** — authenticated floor bytes still fail to prove that rendered F belongs to the named arms.

`git show HEAD` and prior fix commit `146e7ac2` were inspected. Against `origin/main`, the v1 producer, claims ladder, `_v5` flow, and frozen publication renderer are unchanged; only the R2-permitted sidecar, gamma renderer, registry/guide, and R2-FL validator surface differ.

## Residual risk

No canonical suite or live/hardware evidence was run; the prescribed evidence is fixture/counterfactual-only.
