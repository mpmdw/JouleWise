```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "FLOOR-BIND-01 is partially superseded at mint time, but source-derived width authentication and complete governed membership remain unenforced at claim consumption.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "51ed8817126ce18a0b9460612f44124520df109d",
    "head_end": "51ed8817126ce18a0b9460612f44124520df109d",
    "upstream_end": "51ed8817126ce18a0b9460612f44124520df109d",
    "branch": "impl/floor-bind-01"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "FLOOR-BIND-01",
        "action": "start_now",
        "classification": "partially_superseded",
        "live_remainder": "At claim-bearing consumption, authenticate a senior-governed extraction specification, replay extraction gates and widths from the governed source members, require exact complete campaign membership, compare the replay to the supplied floor artifact, and add end-to-end width-substitution and member-omission regressions."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/floor-bind-01...origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## impl/floor-bind-01\\.\\.\\.origin/main$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "51ed8817126ce18a0b9460612f44124520df109d"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^51ed8817126ce18a0b9460612f44124520df109d$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git rev-parse origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "51ed8817126ce18a0b9460612f44124520df109d"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^51ed8817126ce18a0b9460612f44124520df109d$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "No claim-consumption check authenticates extraction-report bytes, rederives admissible widths from governed source bytes, or proves complete governed campaign membership.",
      "needs": "Keep FLOOR-BIND-01 open and implement the claim-consumption replay gate before treating exact floor claims as independently licensed."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests were run, as explicitly required by the read-only scout assignment.",
      "needs": ""
    }
  ]
}
```

## Q1. Acceptance classification at claim consumption

| Item | Classification | Finding |
|---|---|---|
| E1 | **PARTIALLY SATISFIED** | Consumption authenticates the floor JSON bytes and internal schema/math, then reopens and validates each artifact-listed source bundle, configuration, metric value, ordering, and campaign-log occurrence ([inputs.py:853](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:853), [inputs.py:1816](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1816), [inputs.py:1897](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1897), [inputs.py:1945](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1945)). It does **not** open/authenticate the extraction report or extraction specification, nor replay extraction gates and source-derived widths. |
| E2 | **PARTIALLY SATISFIED** | An internally inconsistent stored width/corner is refused: `_validate_estimate_math` recomputes the exact corner from the artifact’s own `admissible_half_widths_j` and compares derived values ([detection_floor.py:3106](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:3106), [detection_floor.py:3143](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:3143)). Listed-member source/hash/order deviations are also refused ([inputs.py:1816](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1816), [inputs.py:1522](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1522)). But an internally consistent understated width and an internally consistent omitted member are not refused. |
| E3 | **NOT SATISFIED** | There is no end-to-end claim-consumption regression that supplies a consistently recomputed width-substituted artifact or a consistently recomputed member-omitting artifact. Existing regressions exercise mint/extraction gates or weaker consumption attacks; see Q4. |

The original CR9-1 diagnosis remains textually exact for the consumption edge: the validator derives widened values from artifact-internal widths, while evidence binding does not derive source widths or require complete membership ([decision_log.md:4530](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/decision_log.md:4530), [decision_log.md:4544](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/decision_log.md:4544)). The registered E1–E3 requirements remain present in the state kernel ([state_kernel.json:1612](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/process/state_kernel.json:1612)).

The S5/D-117 work materially protects artifacts produced by the mint, but those checks run in mint/extraction code. A claim run handed an existing JSON does not invoke them.

## Q2. Actual claim-consumption edge

The operative path is:

1. CLI `_cmd_analyze_claims` passes the manifest, evidence roots, and floor path into `analyze_claims` ([cli.py:2003](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/cli.py:2003), [cli.py:2283](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/cli.py:2283)).
2. `analyze_claims` calls `load_analysis_inputs` ([analysis_engine/__init__.py:1625](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/__init__.py:1625)).
3. `load_analysis_inputs` reads and authenticates the floor file, optionally checks the finalized-manifest floor attachment, then calls `bind_floor_artifact_evidence` ([inputs.py:3001](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:3001), [inputs.py:3045](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:3045), [inputs.py:3103](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:3103)).
4. `_load_authenticated_floor_artifact` reads the file; `authenticate_floor_artifact_bytes` hashes it, parses it, and invokes `validate_floor_artifact` ([inputs.py:853](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:853), [inputs.py:930](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:930)).
5. `validate_floor_artifact` performs schema and artifact-internal mathematical validation ([detection_floor.py:4146](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:4146)).
6. `bind_floor_artifact_evidence` checks order/campaign evidence, then source-binds only the members enumerated by the artifact ([inputs.py:1376](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1376), [inputs.py:1563](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1563), [inputs.py:1728](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1728)).
7. Production floor resolution uses only `binding.bound_cell_ids`; binding failures refuse the production floor ([analysis_engine/__init__.py:364](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/__init__.py:364), [analysis_engine/__init__.py:402](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/__init__.py:402), [inputs.py:3788](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:3788)).
8. The claims evaluator consumes the resolved scalar floor; it does not revisit extraction provenance ([claims.py:257](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/claims.py:257)).
9. The resulting claim artifact embeds the floor bytes and floor SHA. Its validator reruns floor-byte/schema authentication, not extraction replay ([analysis_engine/__init__.py:1821](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/__init__.py:1821), [artifact.py:987](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/artifact.py:987)).

Direct answers:

**(a) Extraction-report bytes:** no. Claim consumption does not open the extraction report. The report SHA in component provenance is only syntax-checked as a hex digest; it is not compared with freshly read report bytes or an independent senior pin ([detection_floor.py:3423](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:3423), [detection_floor.py:3472](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:3472)). The files reread by the campaign-order binder are `order_manifest.json` and `campaign_log.jsonl` ([inputs.py:1452](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1452), [inputs.py:1474](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1474)).

The finalized manifest pins the aggregate floor artifact’s bytes, ID, and schema, not its extraction report ([analysis_manifest_v3.py:3564](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_manifest_v3.py:3564), [inputs.py:827](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:827)).

**(b) Widths:** taken from artifact-internal fields. `_validate_estimate_math` reads `record["admissible_half_widths_j"]` and recomputes the corner from that array ([detection_floor.py:3106](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:3106)). The binder reopens source bundles and compares metrics/configuration identities, but never invokes the source-width derivation in `floor_extraction.py` ([inputs.py:1816](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1816), [floor_extraction.py:2042](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/floor_extraction.py:2042), [floor_extraction.py:2274](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/floor_extraction.py:2274)).

**(c) Complete governed membership:** not enforced. `_campaign_order_binding_problems` proves that each artifact-listed member occurs exactly once and in artifact order, but never checks the converse—that every governed admitted member appears in the artifact ([inputs.py:1522](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1522)). It does not consume `extraction_spec_members`, `expected_n`, `evaluation_basis_members`, or report membership dispositions. Those checks exist on the extraction/mint side ([floor_extraction.py:2969](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/floor_extraction.py:2969), [mint_floor_artifact_generalized.py:1946](/Users/edr/code/JouleWise-wt-s7-floor-bind/scripts/mint_floor_artifact_generalized.py:1946)).

## Q3. Adversarial thought experiments

### S — Width substitution

Take a valid floor artifact, understate one component’s `admissible_half_widths_j`, then consistently recompute its corner, estimate, cell/group/transport floors, artifact ID, and any outer attachment hashes.

**Result: no extraction-shaped refusal at claim consumption.**

`validate_floor_artifact` accepts because `_validate_estimate_math` recomputes against the attacker-supplied width array itself ([detection_floor.py:3106](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:3106)). Source binding checks the listed member’s metric/configuration/hash, not the admissible width derivation ([inputs.py:1816](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1816)).

An unchanged finalized manifest would refuse the substituted floor at `_enforce_finalized_floor_attachment` because its aggregate SHA/ID changed ([inputs.py:827](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:827)). That is an attachment-integrity defense, not CR9-1 closure: if the substituted floor is supplied when the manifest is finalized, the finalizer validates only its internal floor semantics and then pins the substituted bytes ([analysis_manifest_v3.py:3490](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_manifest_v3.py:3490), [analysis_manifest_v3.py:3564](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_manifest_v3.py:3564)).

Required check: before a component’s cells enter `bound_cell_ids` at [inputs.py:1945](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1945), replay that component’s extraction from authenticated governed source bytes and reject unless every replayed admissible width and resulting corner/floor equals the artifact.

### O — Member omission

Remove one governed admitted member, then consistently recompute component membership, widths, estimates, floors, provenance arrays, and hashes.

**Result: no completeness refusal at claim consumption.**

The binder constructs the expected sequence from the already-reduced artifact and proves only that those members occur in the campaign log ([inputs.py:1376](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1376), [inputs.py:1532](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:1532)). A governed member absent from the artifact is never enumerated and therefore never checked.

Required check: in the same pre-binding extraction replay, require exact equality among the senior-governed extraction-spec membership, replayed admitted membership/dispositions, and artifact component membership. Refuse before adding any affected cell to `bound_cell_ids`.

## Q4. Existing regressions

Exact or near-exact producer-side width attacks:

- `test_width_substitution_is_rejected_element_for_element` — old **MINT** path ([test_mint_floor_artifact.py:588](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_mint_floor_artifact.py:588)).
- `test_substituted_comparative_allowance_is_rejected` — old **MINT** path ([test_mint_floor_artifact.py:1358](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_mint_floor_artifact.py:1358)).
- `test_absolute_authentication_uses_unmodified_pinned_width_verifier` — generalized **MINT** path ([test_mint_floor_artifact_generalized.py:6362](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_mint_floor_artifact_generalized.py:6362)).
- `test_opposite_estimator_widths_refuse_in_both_directions` — generalized **MINT** path ([test_mint_floor_artifact_generalized.py:6858](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_mint_floor_artifact_generalized.py:6858)).
- `test_postcollection_common_mode_width_type_and_one_ulp_gates` — generalized **MINT** path ([test_mint_floor_artifact_generalized.py:7039](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_mint_floor_artifact_generalized.py:7039)).
- `test_common_mode_binding_accepts_only_exact_rederived_width`, `test_one_ulp_downward_common_mode_width_refuses`, `test_common_mode_string_width_refuses_after_full_binder`, and `test_common_mode_absolute_width_refusal_is_never_swallowed` — **MINT** estimator/binder path ([test_floor_mint_estimator.py:633](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_mint_estimator.py:633), [test_floor_mint_estimator.py:661](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_mint_estimator.py:661), [test_floor_mint_estimator.py:694](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_mint_estimator.py:694), [test_floor_mint_estimator.py:718](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_mint_estimator.py:718)).

Exact producer-side membership attacks:

- `test_omitting_a_campaign_member_refuses_the_extraction` — **EXTRACTION/MINT-side**, not consumption ([test_floor_extraction.py:5900](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_extraction.py:5900)).
- `test_omission_within_addressed_campaign_still_refuses` — **EXTRACTION/MINT-side** ([test_floor_extraction.py:5976](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_extraction.py:5976)).
- `test_omitted_null_manifest_member_refuses_as_unattributable` — **EXTRACTION/MINT-side** ([test_floor_extraction.py:6014](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_extraction.py:6014)).
- `test_common_mode_session_is_fresh_and_uses_full_spec_membership` — **MINT** estimator path ([test_floor_mint_estimator.py:368](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_floor_mint_estimator.py:368)).

Adjacent consumption tests that do **not** pin S/O:

- `test_widened_floor_record_round_trips_and_rejects_tampering` reaches the floor validator but attacks an internally inconsistent record, not a consistently recomputed width substitution ([test_detection_floor.py:2965](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_detection_floor.py:2965)).
- `test_v3_embedded_floor_bytes_are_hash_and_schema_bound` authenticates embedded floor bytes/schema, not extraction derivation ([test_analysis_integration.py:1435](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_analysis_integration.py:1435)).
- `test_cli_binds_distinct_calibration_bundles_and_preserves_mock_refusal` and its production-telemetry variant exercise the **CONSUMPTION** binder’s source identity/metric/order protections, not width replay or complete membership ([test_analysis_integration.py:3580](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_analysis_integration.py:3580), [test_analysis_integration.py:3585](/Users/edr/code/JouleWise-wt-s7-floor-bind/tests/test_analysis_integration.py:3585)).

Therefore, there is no existing claim-consumption regression of the exact S or O shape.

## Q5. Verdict

**(b) PARTIALLY SUPERSEDED.**

What was superseded:

- S5 W3 added component-scoped provenance and pins for the extraction report, extraction spec, order manifest, and campaign log ([floor_mint_contract.md:50](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/phase_2/floor_mint_contract.md:50)).
- Q4 requires exact element-for-element report-width closure ([floor_mint_contract.md:21](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/phase_2/floor_mint_contract.md:21)).
- W6 requires the mint to rebind members to source bytes and verify report widths and membership before builder calls ([floor_mint_contract.md:103](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/phase_2/floor_mint_contract.md:103)).
- D-117 made the report a cache and required fresh source authentication, complete evaluation membership, and source-derived widths during generalized v2 minting ([floor_mint_contract.md:230](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/phase_2/floor_mint_contract.md:230)).
- D-120 records the corresponding mint trust closure ([decision_log.md:7829](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/decision_log.md:7829), [decision_log.md:7845](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/decision_log.md:7845)).

Those decisions and implementations supersede the **producer/mint portion of E1 and E2**. They do not supersede E3 or the claim-consumption half of E1/E2.

Live remainder:

> Before licensing any claim from a supplied floor artifact, independently authenticate the senior-governed extraction specification, replay extraction gates and admissible widths from the governed source members, require exact complete membership/dispositions, compare the replayed component result with the artifact, and add end-to-end S/O regressions.

## Q6. Minimal sound implementation

This can be fixed without changing or reminting any frozen floor pack.

The cure should be **additive-optional for general artifact loading, but hard-required for claim-bearing consumption**. Older floor artifacts may remain readable/validatable and usable under the registered nonclaim limitation; a production claim must either present sufficient governed extraction evidence for replay or remain refused. That matches L1’s “standalone use remains nonclaim” fence ([decision_log.md:4550](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/decision_log.md:4550), [state_kernel.json:1638](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/process/state_kernel.json:1638)).

Minimal file scope:

- `joulewise/detection_floor.py`: expose the already authenticated repository pinset’s component extraction-spec identity, expected member set/count, and evaluation basis to the consumer. Do not add fields to the floor artifact.
- `joulewise/analysis_engine/inputs.py`: accept per-component governed extraction-spec evidence; authenticate it against the senior pinset and artifact provenance; replay `floor_extraction` against the existing evidence roots; compare admitted members, widths, corners, and operative floors before populating `bound_cell_ids`.
- `joulewise/analysis_engine/__init__.py`: thread the replay evidence through `analyze_claims`.
- `joulewise/cli.py`: add the bounded per-root/component extraction-spec input.
- `tests/test_analysis_integration.py`: add the two defect-shaped end-to-end regressions.
- Optionally `tests/test_analysis_engine.py` for focused refusal-code coverage.

No change is needed in `scripts/mint_floor_artifact_generalized.py`, the frozen floor JSONs, or their `artifact_id`/SHA identities.

Proposed exact refusal reasons, added to the existing floor-binding reason-code registry near [inputs.py:387](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:387):

- `floor_extraction_evidence_required`
- `floor_extraction_spec_hash_mismatch`
- `floor_extraction_replay_refused`
- `floor_width_source_mismatch`
- `floor_campaign_membership_mismatch`

If report bytes are also transported for audit binding:

- `floor_extraction_report_hash_mismatch`

Required regressions:

- `test_cli_claim_consumption_rejects_internally_consistent_width_substitution`
- `test_cli_claim_consumption_rejects_governed_member_omission`

Both should recompute all artifact-internal derived fields and outer floor/finalized-manifest hashes so that the test reaches the new extraction replay gate instead of passing merely because an attachment hash was stale.

## Q7. Deviations and anomalies

- The prompt’s phrase “only compared pin-to-pin inside the artifact” is slightly too generous for the extraction report: at consumption its SHA is syntax-checked, but report bytes are not read and no independent report pin is compared ([detection_floor.py:3472](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:3472)).
- Finalized-v3 attachment pinning now prevents replacing a floor after finalization without also replacing/refinalizing the manifest. This narrows the attack window but does not cure CR9-1 because finalization itself does not replay extraction ([inputs.py:827](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/inputs.py:827), [analysis_manifest_v3.py:3490](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_manifest_v3.py:3490)).
- The claim artifact validator authenticates embedded floor bytes and internal floor validity but cannot independently replay the external extraction evidence ([artifact.py:987](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/analysis_engine/artifact.py:987)).
- The repository pinsets contain richer governed membership information, but the current floor-side projection reduces them chiefly to family/root identity rather than using their extraction membership at consumption ([detection_floor.py:2601](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:2601), [detection_floor.py:2700](/Users/edr/code/JouleWise-wt-s7-floor-bind/joulewise/detection_floor.py:2700)).
- There is no conflict with `detection_floor.md`: it explicitly says its eligibility-scoped requirement is narrower and that broader custody binding remains FLOOR-BIND-01 ([detection_floor.md:753](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/phase_2/detection_floor.md:753), [detection_floor.md:759](/Users/edr/code/JouleWise-wt-s7-floor-bind/docs/phase_2/detection_floor.md:759)).
- Named decisions and code agree once scope is distinguished correctly: D-117/D-120 close the generalized **mint** trust boundary; they do not state or implement a consumer-side replay gate. No decision-log conflict was found.