```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Use an independently authenticated energy-calibration artifact, per-contrast selectors, complete envelope wiring, and semantic replay before receipt refresh.",
  "workspace": {
    "base_requested": "092ac6be",
    "base_mode": "exact",
    "head_start": "092ac6bee283b06a5f801eee3c39f7346378f375",
    "head_end": "092ac6bee283b06a5f801eee3c39f7346378f375",
    "upstream_end": "75d04e9ee7b6ee23df25fed0a30478a45f97090b",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "summary": "Timing-calibration acceptance does not itself supply the energy-null corpus required for F_est."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "summary": "The WIP production engine does not call envelope aggregation; schema acceptance alone would expose incorrect v2 inference."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "summary": "Resolve floors per contrast while preserving the complete frozen multiplicity family."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "summary": "Synthetic receipt repinning cannot establish paper-number neutrality, and the current helper overwrites pending production roles."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD origin/feat/2026-09-24-claimgate-v2 origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "092ac6bee283b06a5f801eee3c39f7346378f375",
          "3cd00c73c75d85706498e346565aac048bca089e",
          "75d04e9ee7b6ee23df25fed0a30478a45f97090b"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "75d04e9ee7b6ee23df25fed0a30478a45f97090b"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check 75d04e9e...origin/feat/2026-09-24-claimgate-v2",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B -c 'import ast, subprocess; s=subprocess.check_output([\"git\",\"show\",\"3cd00c73:joulewise/analysis_engine/__init__.py\"],text=True); assert not any(isinstance(n,ast.Name) and n.id==\"aggregate_envelope_observation\" for n in ast.walk(ast.parse(s))); print(\"WIP_ENGINE_HAS_NO_ENVELOPE_HELPER_REFERENCE\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["WIP_ENGINE_HAS_NO_ENVELOPE_HELPER_REFERENCE"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "WIP_ENGINE_HAS_NO_ENVELOPE_HELPER_REFERENCE"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only design review and static checks only; no unit suite, custody replay, issuance, or hardware validation was performed.",
      "needs": "Lead verifies the completed implementation and production evidence before activation."
    }
  ]
}
```

## Findings

Citations prefixed `WIP:` refer to commit `3cd00c73`; other code citations refer to checkout `092ac6be`. WRITE_SCOPE lists below are **proposed implementation scopes**, not writes performed here.

### W1 — F_est provenance

**F1 — BLOCKER: acceptance provenance and F_est observations are different things.** CG-1 requires envelope-mean **same-model ABBA energy contrasts**. The acceptance issuer currently extracts `b_fiducial_s`; r7 is explicitly a **25F84 timing corpus**. Neither its seconds nor its member count can become F_est or `k_cal`. Sources: `docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3`; `scripts/issue_calibration_acceptance_generation.py:1077`; `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:20`.

**Design to implement**

1. Choose a **separately authenticated energy-calibration artifact**, recomputed at replay. These are complementary choices: the sidecar carries the record; recomputation verifies its numerical result.

2. Add `joulewise/calibration_claim_floor.py` as the shared producer/validator. Add a `prepare-claim-floor` subcommand to `scripts/issue_calibration_acceptance_generation.py`. It consumes:
   - an authenticated issued acceptance generation;
   - the prospectively frozen null-calibration registration;
   - authenticated same-epoch ABBA source bundles and their window/admission evidence.

   The successor acceptance lane coordinates issuance, but its fiducial member table supplies **no energy observations**. If ACCEPTANCE-25G83-02 supplies only timing acceptance, that acceptance may finish while v2 claim-floor availability remains unresolved.

3. Emit schema `joulewise.claim_floor_calibration.v1` with exact fields for artifact identity; acceptance ID and file SHA; complete epoch/protocol identity; registration ID/hash; metric, window, unit and estimator identity; source-byte bindings; envelope membership; retained/excluded observations and reasons; `k_cal`, mean, sample SD, guard, t quantile and F_est; derivation-code bindings. Store block operands as well as derived envelope means. No timing allowance enters F_est.

4. Authenticate the artifact through an independently committed generation-indexed registry, proposed at `configs/calibration/claim_floor_registry.v1.json`. Each issued entry pins artifact ID/file SHA and acceptance ID/file SHA. The sidecar references the acceptance; the acceptance need not hash the sidecar, avoiding a circular digest. A hash supplied solely by the claim is insufficient. This follows the existing acceptance trust pattern, which selects the expected file digest from a registered generation before validating the document: `joulewise/calibration_bracketing.py:1143`.

5. Replay must authenticate the registry entry, acceptance, registration and source bytes; verify same epoch, same-model ABBA identity, membership and eligibility; reconstruct block contrasts and envelope means; then call `estimate_scale_floor`. Compare all derived fields and the registered F_est against that result. Do not resolve through “current ACTIVE” or substitute a newer generation. The WIP calculator explicitly leaves authentication and unit matching to callers: `WIP:joulewise/detection_floor.py:858`.

6. Resolve once **per contrast**, with `floor_class="estimate"` and an exactly matching unit. Persist artifact ID/SHA and registration-time F_est through manifest, verdict and custody replay. A missing binding, `k_cal<5`, wrong epoch, unsupported metric or missing scored denominator yields `not_resolvable`; never fall back to F_block. Equivalence still checks `Δ−F_est>B` using the authenticated evaluation value. The addendum explicitly requires refusal when re-derived F_est invalidates the registered margin: `docs/process_traces/2026-09-24-activation-278ebc9e/66-coldgate-packet-claimgate/30-addendum/21-coldgate-fable-claimgate-addendum-ruling.md:73`.

**Proposed WRITE_SCOPE**

`joulewise/calibration_claim_floor.py` (new); `scripts/issue_calibration_acceptance_generation.py`; `configs/calibration/claim_floor_registry.v1.json` (new, initially without invented issued entries); `joulewise/detection_floor.py`; `joulewise/analysis_engine/inputs.py`; `joulewise/analysis_engine/artifact.py`; `tests/test_calibration_claim_floor.py` (new); `tests/test_issue_calibration_acceptance_generation.py`; `tests/test_claimgate_v2.py`; `docs/contracts/analysis_plans.md`; `docs/decision_log.md`. Consumer changes also use W2/W4 scopes.

**Named refusal tests**

- `test_fiducial_acceptance_without_energy_null_corpus_is_not_resolvable`
- `test_self_resealed_claim_floor_without_issued_registry_pin_refuses`
- `test_claim_floor_wrong_epoch_unit_or_acceptance_binding_refuses`
- `test_four_calibration_envelopes_refuse_despite_many_blocks`
- `test_equivalence_rederived_floor_exhausting_margin_refuses`

**Concern tiers:** BLOCKER until an actual eligible energy corpus is authenticated. MATERIAL: do not import D-125’s lineage-monotone timing-screen arithmetic or D-126’s timing-corpus size into CG-1’s F_est formula; their scope is successor screen/budget arithmetic (`docs/decision_log.md:8465`, `:8492`). NIT: use unit-neutral field names for new fields, not another `_j` alias for J/correct.

### W2 — Manifest v2 schema and production wiring

**F2 — BLOCKER: this exceeds adding three accepted keys.** The WIP defines the aggregation helper but estimates directly over block observations in both production paths. It also selects only direction/equivalence at evaluation and returns the unshifted raw p whenever equivalence is absent. Thus magnitude is not fully wired either. Sources: `WIP:joulewise/analysis_engine/estimators.py:466`; `WIP:joulewise/analysis_engine/__init__.py:788`, `:1100`, `:1401`, `:1418`.

**Design to implement**

1. Retain each legacy exact-key branch unchanged. Missing `claim_rule_version` means historical v1 **only in that legacy branch**. Do not insert defaults into historical serialized manifests. Unknown versions, partial v2 fields and version/field mismatches refuse.

2. Add explicit v2 branches in both validators. The versioned extension is:

   - `claim_rule_version: "v2"`
   - `claim_shape: "direction" | "magnitude" | "equivalence"`
   - `envelope_registration: {planned_k, n_reg, envelopes}`
   - `envelopes` contains exact `{envelope_id, window_id, block_ids}` rows.
   - The per-contrast floor selector gains the authenticated artifact binding and registration-time F_est specified in W1.

   Require integer, non-Boolean `planned_k≥5`, positive integer `n_reg`, unique envelopes, exactly `n_reg` registered block IDs per envelope, and exhaustive non-overlapping coverage of the contrast’s blocks. Bind `window_id` to authenticated capture/window evidence; caller-chosen labels cannot turn one window into several replicates.

3. Freeze the sign and shape-specific parameters. Direction has neither margin nor magnitude threshold. Equivalence uses the existing `equivalence` object with `method="tost_v2"` and finite positive registered margin. Magnitude gets a v2-only `magnitude` object with exact `{threshold, unit}` fields; require `threshold≥registered F_est`. Preserve legacy `mde` meaning.

4. Modify **all** applicable stages: legacy-style contrast validation, v3 prospective validation, finalized validation, builders, registry comparison, semantic projection and finalization replay. The prospective projection already copies complete contrasts, whereas the finalized projection reconstructs a fixed field list; merely accepting extra keys would lose the round-trip contract. Sources: `joulewise/analysis_manifest.py:1264`; `joulewise/analysis_manifest_v3.py:2440`, `:1666`, `:1717`, `:3914`.

5. In the v2 branch, derive block/member counts from the frozen registration. Retain legacy v3’s literal two-contrast/80-member/20-block checks only for its historical design. They cannot silently constrain every future envelope design. Source: `joulewise/analysis_manifest_v3.py:2765`.

6. Wire aggregation before estimation in both production preparation paths. Exclude incomplete envelopes, record their excluded blocks/reasons, and estimate over the retained envelope observations. Use `n=k`, `df=k−1`; `k<5` is `not_estimable`. The legacy `fixed_n_plan_incomplete` path must not blanket-veto the incomplete-envelope exclusions CG-1 expressly permits. Preserve unrelated admission failures. The current blanket checks are at `WIP:joulewise/analysis_engine/__init__.py:779`.

7. Apply this same replicate definition to replay, diagnostics and sensitivity. Keep shared/unknown stochastic scopes refused pending the already-recorded independence-wire ruling; do not invent a scope token. Also remove the helper’s unruled `n_reg≥2` restriction: CG-1 specifies a fixed count but no such lower bound. Sources: `WIP:joulewise/analysis_engine/estimators.py:480`; `docs/process_traces/2026-09-24-activation-278ebc9e/97b-claimgate-impl-resume-report.md:162`.

8. Implement magnitude’s shifted-null p and near-endpoint test; equivalence uses the same Δ_eff for TOST, Holm and interval containment. Record `interval_confidence` for every v2 estimate: 0.95 for direction/magnitude, 0.90 for equivalence. Version the claim-side-bound carrier too: it currently copies CI95 alongside the decision interval and diagnoses widening against CI95. Sources: ruled CG-1/CG-2 at `91-claimgate-final-texts-v2.md:3` and `:5` in the cited trace directory; `joulewise/analysis_engine/claim_side_bound.py:143`, `:213`.

9. Accept J/correct only through an authenticated registered additive operand/score path matching its calibration. A unit string is not that implementation. In particular, do not relabel the v3 finalizer’s hard-coded J output or silently reuse the J/token ratio path (`joulewise/analysis_manifest_v3.py:3920`; `joulewise/analysis_manifest.py:1320`).

**Proposed WRITE_SCOPE**

`joulewise/analysis_manifest.py`; `joulewise/analysis_manifest_v3.py`; `joulewise/analysis_engine/__init__.py`; `joulewise/analysis_engine/registry.py`; `joulewise/analysis_engine/estimators.py`; `joulewise/analysis_engine/claims.py`; `joulewise/analysis_engine/artifact.py`; `joulewise/analysis_engine/sensitivity.py`; `joulewise/analysis_engine/claim_side_bound.py`; `tests/test_analysis_manifest.py`; `tests/test_analysis_manifest_v3.py`; `tests/test_analysis_engine.py`; `tests/test_analysis_integration.py`; `tests/test_analysis_claims.py`; `tests/test_claim_side_bound.py`; `tests/test_claimgate_v2.py`; W1’s contract files.

**Named refusal/regression tests**

- `test_v2_many_blocks_in_four_windows_is_not_estimable`
- `test_v2_incomplete_envelope_excluded_five_complete_envelopes_remain_estimable`
- `test_v2_duplicate_window_labels_cannot_inflate_k`
- `test_v2_finalization_preserves_all_frozen_claim_semantics`
- `test_v2_magnitude_uses_shifted_null_and_registered_threshold`
- `test_v2_equivalence_custody_uses_ci90_plus_bound`
- `test_legacy_manifest_acceptance_errors_and_serialization_unchanged`

**Concern tiers:** BLOCKER until production aggregation and replay agree. MATERIAL: magnitude, unit conversion and side-bound carriers belong in the integration closure. NIT: retain block counts as diagnostics with explicit names; do not print them as the inferential sample size.

### W3 — Mixed v1/v2 registries

**F3 — MATERIAL: choose per-contrast selectors, retaining family-wide multiplicity.** The WIP places version per contrast but requires one version across a shared selector. Existing manifests already carry selectors per contrast, and Holm already preserves frozen `m` with missing hypotheses. Sources: `WIP:joulewise/analysis_engine/registry.py:478`; `joulewise/analysis_manifest.py:123`; `joulewise/analysis_engine/multiplicity.py:54`.

**Design to implement**

- Keep historical all-v1 registries on their existing exact schema, including their shared selector.
- Introduce an explicit successor registry schema, `joulewise.analysis_registry.v3`. Every contrast in this schema declares its version and owns its selector. Remove the registry-wide selector from this new schema; reject both-present or missing-selector documents.
- For v1 contrasts in the successor schema, require the legacy block selector and semantics. For v2, require W1’s estimate selector. Resolve and cache using the complete contrast/estimand/artifact binding, never merely the family or epoch.
- Compute each contrast’s raw p under its own version, then run **one** adjustment over the complete frozen family. Version is not a new selection opportunity and never splits `m`. Missing contrasts remain present as `None`.
- Existing claim-bearing registrations and issued artifacts remain historical v1; do not retrofit them. The two `pending_p2_015` AP-SPEC front registries also remain v1 until prospectively re-registered. CG-4 explicitly preserves those specs; their pending fields are at `configs/analysis_registry/ap_spec_draft_front.v2.json:142` and `configs/analysis_registry/ap_spec_native_mtp_front.v2.json:142`.
- AP-5M v5 is a **new prospective registration**, with fresh observations and its ruled additive J/correct primary estimand, not a migration of already observed outcomes. Preserve its five-hypothesis denominator. This is required by CG-1/CG-4: `docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3`, `:9`.

**Proposed WRITE_SCOPE**

`joulewise/analysis_engine/registry.py`; `joulewise/analysis_engine/__init__.py`; `joulewise/analysis_engine/inputs.py`; both manifest modules from W2; `tests/test_axi_analysis_manifest.py`; `tests/test_analysis_integration.py`; `tests/test_claimgate_v2.py`; W1’s contract files. Existing registry JSON files receive **no edits**. Actual AP-5M registration artifacts require their own exact path list once the owning prospective registration is ready.

**Named tests**

- `test_mixed_versions_select_correct_floor_without_cross_contrast_cache_reuse`
- `test_mixed_versions_share_frozen_holm_m_with_missing_hypotheses`
- `test_successor_registry_rejects_ambiguous_global_and_local_selectors`
- `test_pending_front_registry_remains_v1`

**Concern tiers:** BLOCKER if separation changes family membership or `m`; MATERIAL otherwise. NIT: distinguish registry schema version from claim-rule version in diagnostics.

### W4 — Paper-custody receipts

**F4 — MATERIAL: fix fixture receipts, but do not call that numerical neutrality.** The failing fixture constructor hashes synthetic inputs marked `synthetic-no-measurement-value` and asserts receipt digest equality. Those fixtures contain no paper measurements. Further, the repin helper overwrites `pending_roles` with one entry, while the current map contains two. Sources: `tests/test_paper_custody.py:123`, `:161`; `tests/fixtures/paper_custody/repin.py:24`; `configs/paper_supply/supply_map.json:2`.

**Reissue procedure**

1. The **lead owns issuance and final verification**. An implementation seat may repair the fixture generator and prepare candidate receipts; it must not hand-edit hashes until tests turn green.
2. Freeze the reviewed candidate source revision. Narrow `repin.py` to update only synthetic roles’ receipt digests and the inventory digests that depend on them. Preserve every input hash, source census, grant policy, pending role and production entry. Remove its unrelated fixture rewriting.
3. Before repinning, run a new check named **`paper_receipt_reissue_semantic_equivalence`**:
   - Run baseline and candidate against the **same immutable inputs**.
   - For historical v1, compare estimates, uncertainty components, intervals, floors, eligibility/exclusions, raw/adjusted p-values, frozen `m`, outcomes, reason codes, custody grants and rendered paper values.
   - Require exact equality of deterministic semantic output. Permit differences only at explicitly enumerated receipt/source-binding and consequent inventory-digest paths.
   - Include a deliberate one-number mutation: the check must fail even when receipts are freshly minted.
4. Only after that check passes, generate fixture pins and run the named custody/integration modules. Keep `test_gate_sources_change_receipt_digest` effective: it proves source mutations invalidate old receipts; it does **not** prove the new science is equivalent (`tests/test_paper_custody.py:930`).
5. For any production receipt requiring refresh, preserve its predecessor and mint a new generation through the owning production replay/issuance path. Require the same semantic comparison over actual source evidence. Missing evidence means **neutrality unverified**, never “fixture tests passed.” Paper custody already replays finalized manifests, verdicts and side bounds before granting claims (`joulewise/paper_custody.py:597`).
6. Extend the receipt source census to cover the new calibration authenticator, envelope aggregation and version dispatch. Otherwise changing those suppliers could leave receipts apparently current. The existing census is explicitly closed and owner-based (`joulewise/paper_custody.py:731`).

**Proposed WRITE_SCOPE**

`joulewise/paper_custody.py`; `tests/fixtures/paper_custody/repin.py`; `configs/paper_supply/supply_map.json`; `tests/test_paper_custody.py`; `scripts/check_paper_receipt_reissue.py` (new); `tests/test_paper_receipt_reissue.py` (new); W2’s side-bound files. Production successor receipt paths must be enumerated by the lead before that separate issuance task; no wildcard permission over issued evidence.

**Named tests**

- `test_receipt_reissue_preserves_all_pending_roles_and_input_hashes`
- `test_receipt_reissue_rejects_changed_paper_number_after_repin`
- `test_receipt_reissue_rejects_changed_claim_grant_with_same_numbers`
- `test_gate_sources_change_receipt_digest` — retained.

**Concern tiers:** BLOCKER for production reissue without semantic replay; MATERIAL for unsafe fixture repinning. NIT: describe the nineteen failures as stale **synthetic fixture receipt pins**, not nineteen changed paper results.

## PR ordering

1. **Acceptance-lane prerequisite:** finish the acceptance ruling and its independently required successor implementation. Establish the actual accepted generation and eligible null-calibration inputs; do not infer either from this consult.
2. **One full-tier CG-4 integration PR:** include W1–W4, the existing WIP, versioned contracts, complete production/replay tests, simulation evidence and receipt-refresh evidence. Review in that order; generate receipt pins last. Do not merge four independently activating wiring PRs: CG-4 explicitly says one PR with the components versioned together (`docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:9`).
3. **Prospective issuance/capture activation:** freeze the new claim registration only after its real calibration binding exists. Keep the current unconditional v2 refusal until its replacement authentication and inference gates pass end to end (`WIP:joulewise/analysis_engine/artifact.py:2290`).

## Falsifiers

Reject this design if any of these experiments succeeds:

- A caller changes calibration means, reseals local hashes and obtains admission without a new trusted issuance.
- Five labels on one capture window produce `k=5`.
- Twenty blocks in four envelopes yield an estimable v2 claim.
- Removing an incomplete sixth envelope prevents estimation from five otherwise eligible complete envelopes solely through the legacy block-count veto.
- Splitting a mixed-version registry changes adjusted p-values while the registered family remains unchanged.
- Δ equals F_est+B and equivalence is admitted.
- A changed historical paper number or custody grant survives the semantic-neutrality check after repinning.
- V1 accepted/rejected documents, numerical outputs or serialized bytes change outside the explicitly refreshed receipt bindings.

## Residual risk

The 25G83 council’s outcome and live null-calibration corpus were outside this review. No supplied evidence establishes that the successor has five eligible energy-null envelopes. Reported WIP suite counts were not rerun. Shared-scope independence and the concrete J/correct operand supplier remain activation dependencies, not permission to improvise science.

## Expected disagreement

Other seats may embed F_est inside acceptance; I prefer a separately pinned energy record because the present acceptance corpus is timing-only.  
They may split registries by version; that adds family-reassembly obligations without resolving a scientific need.  
They may characterize W2 as schema work; the uncoupled aggregation helper makes it an inference blocker.  
They may accept repinning as neutrality evidence; synthetic receipts cannot establish unchanged paper numbers.