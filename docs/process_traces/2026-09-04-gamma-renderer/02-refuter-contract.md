```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {"id":"B1","severity":"blocker","title":"The v2 producer crashes on governed refusals","file_line":"joulewise/analysis_engine/__init__.py:1594","text":"An absent estimate makes deterministic.terms=[], then claim_side_bound_from_terms raises at line 1603. Existing refusal producer cases error before issuance.","counterfactual":"A legitimate not-estimable/pre-estimation refusal cannot produce v2, contradicting R2 and tests/test_analysis_integration.py:1560,2140-2169.","cure_shape":"Source the registered clock-anchor term independently of estimator success, or obtain a ruled refusal wire; restore the existing producer tests."},
      {"id":"B2","severity":"blocker","title":"Refused G2-a becomes a 4096 selection","file_line":"joulewise/results_fill_gamma.py:223","text":"The refused branch returns collection_prefill_tokens=4096; lines 586-627 then render p4096.","counterfactual":"A pinned refused-G2-a/p4096 case rendered PG-08 as supported, while packet line 265 requires unresolved-G2-a STOP_FILL.","cure_shape":"Make non-selected G2-a terminal before length selection and add the refused-G2-a case."},
      {"id":"B3","severity":"blocker","title":"Refusal prose lacks issued authority","file_line":"joulewise/results_fill_gamma.py:399","text":"Missing contrast directly selects 'required ... verdict absent'; the API at lines 555-563 has no authenticated earlier-stop reason channel.","counterfactual":"Upstream absence is mislabeled and the ruled earlier-stop branch cannot render, contrary to registry lines 903,912 and packet line 263.","cure_shape":"Authenticate governing refusal stage/reason and never choose prose from contrast absence alone."},
      {"id":"B4","severity":"blocker","title":"Valid partial outcomes cannot reach ruled text","file_line":"joulewise/results_fill_gamma.py:413","text":"Lines 417-446 require all numbers before claim_evaluation at 488-541, making coded partial/refusal branches unreachable when numbers are absent.","counterfactual":"Valid not_estimable or refused-floor artifacts lose required verdict/gate text promised by registry lines 383-385,397-399.","cure_shape":"Render issued outcome/refusal state first, gate numeric tokens independently, and add exact partial-state tests."},
      {"id":"S1","severity":"should_fix","title":"The registry still declares the newly registered prefill family nonexistent","file_line":"docs/paper/results-fill-registry.md:363","text":"Lines 363-368 say the prefill token family does not exist and PG rows remain STOP_FILL/TOKEN_FAMILY_MISSING, while lines 386-399 and 906-912 register that family and bind the PG rows under R2.","counterfactual":"Two readers following the same registry can reach opposite authority decisions about whether the prefill keys exist.","cure_shape":"Replace the stale section introduction with the R2-issued family/status and retain only VALUE_UNISSUED/UNRESOLVED-UNTIL-G2A where applicable."},
      {"id":"S2","severity":"should_fix","title":"Registered consumers remain on v1","file_line":"docs/contracts/claims_ladder.md:21","text":"The ladder and v5-artifact-flow.md:23,32 still name v1; scripts/render_results_fills.py:574-578,975-978 refuses B, and the new function has no non-test caller.","counterfactual":"Producer-v2 remains unreachable through the registered publication path.","cure_shape":"Amend v1-read/v2-current contracts and connect the authenticated successor adapter, or keep this seat explicitly non-production."}
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "R2 field and token names match, but producer refusal crashes, refused G2-a renders, governed refusal prose is unavailable, and registry/consumer contracts remain inconsistent.",
  "workspace": {"base_requested":"908eabc3","base_mode":"exact","head_start":"908eabc3fd23793eaf08287e3322fef26a2b961c","head_end":"908eabc3fd23793eaf08287e3322fef26a2b961c","upstream_end":"c74c7e6a7448be34e7de54ba839004c2ace6cc03","branch":null},
  "pathspec": ["docs/process_traces/2026-09-04-gamma-renderer/02-refuter-contract.md"],
  "unowned_dirty": [],
  "verification": [
    {"id":"V1","kind":"test","cmd":"python3 -m unittest tests.test_results_fill_gamma tests.test_analysis_engine_artifact","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 0.340s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 3 tests[\\s\\S]*OK"}},
    {"id":"V2","kind":"test","cmd":"R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 13 tests in 2.717s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 13 tests[\\s\\S]*OK"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest tests.test_analysis_integration.AnalysisIntegrationTests.test_v3_abba_engine_and_d093_refusal_precedence tests.test_analysis_integration.AnalysisIntegrationTests.test_complete_strict_current_bundle_set_derives_deterministic_fail_closed_artifact","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["ClaimArtifactError: claim-verdict v2 requires exactly one finite nonnegative E_clock_anchor_shift_bound_j deterministic term","Ran 2 tests in 1.099s","FAILED (errors=2)"]},"expected":{"exit_code":0,"tail_regex":"Ran 2 tests[\\s\\S]*OK"}},
    {"id":"V4","kind":"inspection","cmd":"git diff --quiet origin/main..HEAD -- docs/paper/draft-v1.md docs/paper/fill-rehearsal tests/fixtures/results_prose_render","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V5","kind":"inspection","cmd":"git diff --name-status origin/main..HEAD -- tests/fixtures/results_fill_gamma","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["A\ttests/fixtures/results_fill_gamma/symbolic-2048-cases.json"]},"expected":{"exit_code":0,"tail_regex":"^A\\stests/fixtures/results_fill_gamma/symbolic-2048-cases.json$"}}
  ],
  "flags": [
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"The canonical full suite was prohibited by the user preflight; only the allowed focused modules and registry tests ran.","needs":"Lead reruns the broader suite after fixes."},
    {"id":"F2","kind":"baseline_drift","level":"nonblocking","text":"origin/main is c74c7e6a while the required detached landing HEAD is 908eabc3; review used origin/main..HEAD only with the nine landing pathspecs identified by the seat commit/report.","needs":""}
  ]
}
```

## Findings

### B1 — blocker — The v2 producer crashes instead of issuing governed refusal artifacts

- File: `joulewise/analysis_engine/__init__.py:1594-1603`; enforcing helper: `joulewise/analysis_engine/artifact.py:421-429`.
- Text: an absent estimate creates an empty deterministic-term list, then the required-bound projection raises before a refusal artifact can issue.
- Counterfactual: both permitted producer integration checks terminate with `ClaimArtifactError`; the old governed `not_estimable`/refusal outcomes disappear rather than migrating to v2.
- Cure shape: make the registered named term available independently of estimator success, or obtain a ruling for a distinct refusal representation; keep the v2 sibling closed and required.

### B2 — blocker — A refused G2-a record is treated as an issued 4096 selection

- File: `joulewise/results_fill_gamma.py:223-239,586-627`.
- Text: the refused branch returns its collection fallback as if selected.
- Counterfactual: the refuter's pinned refused-G2-a/p4096 case rendered a supported PG-08 sentence instead of global `STOP_FILL`.
- Cure shape: reject every G2-a status other than `selected` before any prompt length is exposed; test the refused record byte path.

### B3 — blocker — Refusal prose lacks issued authority

- File: `joulewise/results_fill_gamma.py:399-405,555-563`; registry: `docs/paper/results-fill-registry.md:903,912`.
- Text: contrast absence alone chooses the missing-verdict sentence, while no API input can carry a governed before-comparison stage/reason.
- Counterfactual: unrelated upstream absence is mislabeled, and the ruled earlier-stop sentence cannot be produced.
- Cure shape: authenticate the governing refusal source and branch only on its issued stage/reason.

### B4 — blocker — Valid partial outcomes cannot reach their ruled text

- File: `joulewise/results_fill_gamma.py:413-446,488-541`; registry: `docs/paper/results-fill-registry.md:383-385,397-399`.
- Text: mandatory numeric parents are checked before issued outcome state, making `not_estimable`, `not_resolvable`, and gate-unavailable renderings unreachable when their numbers are legitimately absent.
- Counterfactual: valid refusal/partial artifacts lose professor-facing state instead of keeping numeric cells stopped and rendering issued outcomes.
- Cure shape: evaluate authenticated outcome/refusal state first, then gate each numeric token independently; add exact branch tests.

### S1 — should_fix — Registry prose contradicts its own R2 rows

- File: `docs/paper/results-fill-registry.md:363-368` versus `:386-399,906-912`.
- Text: the introduction says the prefill family is missing and PG stays `STOP_FILL`, but the tables register it.
- Counterfactual: consumers can reach opposite contract decisions from one authority file.
- Cure shape: replace the stale introduction with the issued-family and value-unissued status.

### S2 — should_fix — Producer-v2 is unreconciled with registered consumers

- File: `docs/contracts/claims_ladder.md:21-25`; `docs/process/v5-artifact-flow.md:23,32`; `scripts/render_results_fills.py:574-578,975-978`.
- Text: binding/current flow prose still names v1, the executable paper renderer still refuses B, and the new function has only test callers.
- Counterfactual: production emits v2 into a publication path that still documents and executes the old stop.
- Cure shape: update v1-read/v2-current contracts and land the authenticated successor adapter, or keep this seat explicitly non-production until it exists.

The five-field `claim_side_bound` object, all 14 decode and 14 prefill token names, the numeric DS-28..33/PG-01..08 bindings, available pass/fail/supported phrases, and D-166 count-4 sentence otherwise match R2. Numeric values are read from issued E/F/B/endpoints and only the registered magnitude, max cross-check, clearance/shortfall/ratio, and F+B derivations are computed; no additional numeric default was found beyond B2's misuse of the refused 4096 collection fallback.

## Residual risk

The full suite was excluded by preflight. Frozen draft and rehearsal fixtures are unchanged under `origin/main..HEAD`; the only fixture change is the isolated addition `tests/fixtures/results_fill_gamma/symbolic-2048-cases.json`.
