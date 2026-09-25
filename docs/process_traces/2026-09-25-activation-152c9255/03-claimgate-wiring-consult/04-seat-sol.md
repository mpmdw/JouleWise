```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The v2 gate needs a separately authenticated energy-null calibration artifact, versioned manifest wiring, per-contrast floor selection, and a controlled fixture-receipt reissue.",
  "workspace": {
    "base_requested": "092ac6be",
    "base_mode": "exact",
    "head_start": "092ac6bee283b06a5f801eee3c39f7346378f375",
    "head_end": "092ac6bee283b06a5f801eee3c39f7346378f375",
    "upstream_end": "3cd00c73c75d85706498e346565aac048bca089e",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "topic": "W1", "text": "The D-079 acceptance corpus contains timing fiducials, not the same-model energy-null envelope contrasts required to derive F_est."},
      {"id": "F2", "severity": "blocker", "topic": "W2", "text": "Both exact-key manifest paths need a prospective v2 schema and frozen envelope projection before v2 evidence can be admitted."},
      {"id": "F3", "severity": "blocker", "topic": "W3", "text": "The WIP's shared floor selector cannot represent mixed versions or the existing contrasts' different units."},
      {"id": "F4", "severity": "should_fix", "topic": "W4", "text": "Synthetic custody receipts must be reissued only after validator code is final and historical paper outputs are independently shown unchanged."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --stat 75d04e9e...origin/feat/2026-09-24-claimgate-v2",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["20 files changed, 1510 insertions(+), 93 deletions(-)"]},
      "expected": {"exit_code": 0, "tail_regex": "20 files changed"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --exit-code",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "This was a read-only design consult; no focused tests or hardware collection were run.",
      "needs": "The implementation lead runs the named focused tests and the ruled full-tier gate."
    }
  ]
}
```

## Findings

### W1 — F_est provenance (F1, BLOCKER)

**Design.** Mint `F_est` in a separate, versioned **energy-null calibration sidecar**, coupled to the 25G83 successor acceptance *issuance transaction*. The D-079 acceptance itself remains the timing authority: its candidate derives screens from `b_fiducial_s`, and its member table contains seconds and source hashes, not energy-null contrasts. Treating those values as J or J/correct would invent evidence. The successor candidate is expressly unissued until the governed transaction. [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:20), [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:29), [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:1100), [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:1439)

The sidecar must contain the accepted generation’s ID and byte digest; the frozen machine, macOS build, protocol, model, metric and unit; each prospectively registered same-model ABBA null envelope’s ID, block membership, source digest and **envelope-mean energy contrast**; the calculation rule; and the derived value. Authenticate the acceptance through its issued-generation registry, authenticate each immutable null source by digest, require the same epoch and exact unit, then recompute `F_est` from those contrasts at mint **and replay**. A claim registration freezes the sidecar artifact ID, digest and recorded `F_est`; the claim artifact carries that binding and the resolved value. Replay rejects any changed source, epoch, unit, ID or recomputed value. The WIP calculator already implements the ruled formula but explicitly leaves authentication and unit matching to callers; its artifact validator currently refuses all v2 floors for that reason. CG-1 requires at least five same-epoch null envelopes and excludes a timing term. [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3), `origin/feat/2026-09-24-claimgate-v2:joulewise/detection_floor.py:858–879`, `origin/feat/2026-09-24-claimgate-v2:joulewise/analysis_engine/artifact.py:2290–2304`, [joulewise/calibration_bracketing.py](/Users/edr/code/wt-152c9255-cgw-sol/joulewise/calibration_bracketing.py:144)

The 25G83 successor process is the natural **transaction and epoch anchor**, but its current timing corpus cannot mint the energy number. If prospectively registered energy-null captures do not exist for that accepted epoch and unit, retain v2 `not_resolvable`; do not backfill or substitute the block floor. For equivalence, also compare the evaluation-time resolved floor with the registered margin and refuse `equivalence_margin_not_above_floor` when `Δ − F_est ≤ B`, as ruled. [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:5), [21-coldgate-fable-claimgate-addendum-ruling.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/66-coldgate-packet-claimgate/30-addendum/21-coldgate-fable-claimgate-addendum-ruling.md:73)

**Proposed WRITE_SCOPE:** `joulewise/calibration_estimate_floor.py` (new sidecar validator), `scripts/issue_calibration_estimate_floor.py` (new candidate producer), `joulewise/calibration_bracketing.py` (issued ID/digest binding), `joulewise/detection_floor.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/analysis_engine/__init__.py`, `joulewise/analysis_engine/artifact.py`, `joulewise/paper_custody.py`, `tests/test_calibration_estimate_floor.py` (new), `tests/test_claimgate_v2.py`. The eventual issued sidecar path under `configs/calibration/` must be named in the successor transaction’s own exact write scope; no sidecar may be fabricated by this implementation PR.

**Named refusal test:** `test_v2_replay_refuses_timing_only_epoch_mismatch_or_changed_null_source`.

**Concern:** **BLOCKER** until accepted same-epoch energy-null evidence exists. **MATERIAL** if the sidecar is authenticated only by its own asserted hash rather than an issued pin and underlying source replay.

### W2 — Manifest v2 schema (F2, BLOCKER)

**Design.** Add an explicit new manifest/registry schema branch; retain the existing exact-key v1 branches and serialized v1 fixtures unchanged. In the new branch, require `claim_rule_version` on **each contrast**, exactly one `claim_shape` (`direction`, `magnitude`, `equivalence`), and an `envelope_registration` containing fixed `n_reg`, planned envelope IDs and their frozen block IDs, plus a registered cross-envelope independence assertion. Validate uniqueness, exact block coverage, source/capture linkage, retained-envelope exclusions and unit. Keep unknown or shared term scopes refusing until their wire spelling and independence proof are ruled; the WIP helper currently accepts only `independent_run` and explicitly refuses the shared case. [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3), `origin/feat/2026-09-24-claimgate-v2:joulewise/analysis_engine/estimators.py:466–505`

Apply the new keys in both `analysis_manifest.py` and `analysis_manifest_v3.py`. In v3, validate them in the **prospective** contrast, carry them into the semantic projection and finalized contrast, then recheck against authenticated realized envelopes. Merely widening `CONTRAST_KEYS` is insufficient: v3 has distinct prospective/finalized key sets and builds a projection for identity; it currently fixes `floor_field` to `floor_gate_j`. The older validator likewise has exact contrast and selector keys and a fixed block linkage. [joulewise/analysis_manifest.py](/Users/edr/code/wt-152c9255-cgw-sol/joulewise/analysis_manifest.py:108), [joulewise/analysis_manifest.py](/Users/edr/code/wt-152c9255-cgw-sol/joulewise/analysis_manifest.py:1323), [joulewise/analysis_manifest_v3.py](/Users/edr/code/wt-152c9255-cgw-sol/joulewise/analysis_manifest_v3.py:1074), [joulewise/analysis_manifest_v3.py](/Users/edr/code/wt-152c9255-cgw-sol/joulewise/analysis_manifest_v3.py:1215), [joulewise/analysis_manifest_v3.py](/Users/edr/code/wt-152c9255-cgw-sol/joulewise/analysis_manifest_v3.py:1717), [joulewise/analysis_manifest_v3.py](/Users/edr/code/wt-152c9255-cgw-sol/joulewise/analysis_manifest_v3.py:3914)

**Proposed WRITE_SCOPE:** `joulewise/analysis_manifest.py`, `joulewise/analysis_manifest_v3.py`, `joulewise/analysis_engine/registry.py`, `tests/test_analysis_manifest.py`, `tests/test_analysis_manifest_v3.py`, `tests/test_axi_analysis_manifest.py`, `tests/test_claimgate_v2.py`.

**Named refusal test:** `test_v2_manifest_refuses_missing_or_mutated_envelope_registration`; pair it with `test_v1_manifest_bytes_and_verdicts_unchanged`.

**Concern:** **BLOCKER** if registration fields appear only in a finalized artifact or are omitted from its prospective semantic hash. **MATERIAL** if the v1 exact-key path is loosened by a global union of optional v2 fields.

### W3 — Mixed v1/v2 registries (F3, BLOCKER)

**Choice: per-contrast floor selectors.** For the new schema, bind each contrast’s selector to its own `claim_rule_version`, estimand unit, calibration artifact and claim shape. Require `max(floor_abs_j,floor_cmp_j)`/`block` on v1 and `floor_est`/`estimate` on v2; prohibit a v2 selector from inheriting a root default. Keep the old root-selector schema solely for historical v1 replay. This preserves one frozen multiplicity family, including missing members, while allowing contrasts of different units. The WIP instead refuses mixed versions, keeps one root selector, and demands that its one v2 `floor_unit` match **every** estimand. `origin/feat/2026-09-24-claimgate-v2:joulewise/analysis_engine/registry.py:72–108`, `origin/feat/2026-09-24-claimgate-v2:joulewise/analysis_engine/registry.py:478–503`, [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3)

Existing paper-facing and pending AP-SPEC registrations retain their frozen v1 bytes and block-floor meaning. In particular, the checked-in AP-SPEC front registry has a J contrast and a `J/committed_output_token` contrast with `pending_p2_015`; it cannot be relabelled v2 by adding a shared `J` floor. A new AP-5M v5 registration uses the ruled additive `J/correct` estimand and a matching calibrated sidecar; existing observations do not become confirmatory v2 observations. CG-4 expressly keeps pending specs v1 until re-registration. [ap_spec_draft_front.v2.json](/Users/edr/code/wt-152c9255-cgw-sol/configs/analysis_registry/ap_spec_draft_front.v2.json:21), [ap_spec_draft_front.v2.json](/Users/edr/code/wt-152c9255-cgw-sol/configs/analysis_registry/ap_spec_draft_front.v2.json:98), [ap_spec_draft_front.v2.json](/Users/edr/code/wt-152c9255-cgw-sol/configs/analysis_registry/ap_spec_draft_front.v2.json:112), [ap_spec_draft_front.v2.json](/Users/edr/code/wt-152c9255-cgw-sol/configs/analysis_registry/ap_spec_draft_front.v2.json:133), [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:9)

**Proposed WRITE_SCOPE:** `joulewise/analysis_engine/registry.py`, `joulewise/analysis_engine/inputs.py`, `joulewise/analysis_engine/__init__.py`, `joulewise/analysis_engine/artifact.py`, `joulewise/paper_custody.py`, `joulewise/analysis_manifest.py`, `joulewise/analysis_manifest_v3.py`, `tests/test_analysis_engine.py`, `tests/test_analysis_manifest.py`, `tests/test_analysis_manifest_v3.py`, `tests/test_claimgate_v2.py`. Any new AP-5M registry gets its own exact path and prospective approval before data; the two checked-in AP-SPEC fronts are outside this edit.

**Named refusal test:** `test_mixed_registry_refuses_root_floor_inheritance_and_wrong_unit`.

**Concern:** **BLOCKER** if a shared selector survives into mixed-version evaluation. **MATERIAL** if splitting registries also splits a previously frozen Holm selection family or resets its missing members; CG-1 fixes AP-5M’s `m=5` with missing members retained. [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3)

### W4 — Paper-custody receipts (F4, MATERIAL)

The reported 19 failures are stale **synthetic fixture** receipt digests, not authority to rewrite issued paper evidence. The fixture builder computes a receipt containing `validator_source_sha256` and checks its expected digest; the supplied repin utility declares itself fixture-only and writes the fixture supply map. Production roles in that map are pending. [97b-claimgate-impl-resume-report.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/97b-claimgate-impl-resume-report.md:96), [tests/test_paper_custody.py](/Users/edr/code/wt-152c9255-cgw-sol/tests/test_paper_custody.py:160), [repin.py](/Users/edr/code/wt-152c9255-cgw-sol/tests/fixtures/paper_custody/repin.py:1), [supply_map.json](/Users/edr/code/wt-152c9255-cgw-sol/configs/paper_supply/supply_map.json:1)

**Procedure.** After all validator changes are frozen, the implementation seat runs the fixture repin utility in its authorized checkout, reviews its diff to ensure only the expected fixture receipt/inventory digests and map pins changed, and runs `tests.test_paper_custody`. The paper custodian/lead, not the fixture repinner, mints any later **production** receipt from authenticated source bytes under the clean Git anchor and replays the registered validator. The custody reader itself checks the receipt’s validator source digest and bound input list. `origin/feat/2026-09-24-claimgate-v2:joulewise/paper_custody.py:744–856`, `origin/feat/2026-09-24-claimgate-v2:joulewise/paper_custody.py:1278–1309`

**Change-detection check:** compare every existing v1 claim’s replayed numeric fields, verdict, grant and reason codes against a pinned pre-change snapshot **and** require a byte-identical diff for the paper’s rendered number-bearing files. A digest reissue passes only if both comparisons pass; changed numbers or v1 semantics require adjudication rather than new receipt hashes. This matters because a receipt digest proves binding to current validator code, not that the validator preserved historical decisions. The WIP changes the claim issuance evaluator path as well as its source census. `origin/feat/2026-09-24-claimgate-v2:joulewise/paper_custody.py:597–660`, [tests/test_paper_custody.py](/Users/edr/code/wt-152c9255-cgw-sol/tests/test_paper_custody.py:534)

**Proposed WRITE_SCOPE:** `configs/paper_supply/supply_map.json`, `tests/fixtures/paper_custody/repin.py`, `tests/test_paper_custody.py`, `tests/test_claimgate_v2.py`. Production receipt paths require a separate exact issuance scope once actual paper sources and roles are ready.

**Named refusal test:** `test_receipt_reissue_refuses_changed_v1_claim_projection_or_paper_number`.

**Concern:** **MATERIAL** if the repin script is used for production receipts or before validator source freezes. **NIT** if a report describes these 19 synthetic fixture failures as changed paper numbers.

## PR ordering

1. **Calibration successor transaction:** settle ACCEPTANCE-25G83-02; register and validate energy-null captures separately; issue the acceptance and its bound claim-floor sidecar only when both have authentic evidence. A timing-only successor leaves v2 claim use blocked. [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:20), [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3)
2. **One full-tier claim-gate PR:** land W1 consumer/replay, W2 schema, W3 per-contrast selection, and the new AP-5M registration together; reissue W4 fixture receipts **last**, then verify v1 replay and the focused integration tests. CG-4 calls for one claim-gate PR with rules before data, so these are ordered work inside that PR rather than separately activated claim-gate releases. [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:9)

## Falsifiers

The design is wrong if the 25G83 successor already contains authenticated same-model **energy** null envelope contrasts in the required unit; if a replayed sidecar changes `F_est` without a source, epoch or rule change; if any v1 artifact’s bytes or decision change; if a mixed registry selects another contrast’s floor; or if receipt-only reissue passes while a historical paper number or claim projection moves. The first condition directly tests the W1 inference from the current timing-only producer. [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:1100), [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:1439), [docs/decision_log.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/decision_log.md:11291)

## Residual risk

No same-epoch energy-null source was supplied for this consult, so sidecar issuance cannot be verified here. The WIP’s shared-term envelope scope also remains explicitly refused pending a frozen wire and independence rule. `origin/feat/2026-09-24-claimgate-v2:joulewise/analysis_engine/estimators.py:472–493`

## Expected disagreement

Other seats may prefer putting `F_est` inside the successor acceptance or enforcing separate homogeneous registries. I expect the deciding evidence to be the acceptance’s timing-only member schema and whether a split registry preserves the frozen multiplicity family. [scripts/issue_calibration_acceptance_generation.py](/Users/edr/code/wt-152c9255-cgw-sol/scripts/issue_calibration_acceptance_generation.py:1439), [91-claimgate-final-texts-v2.md](/Users/edr/code/wt-152c9255-cgw-sol/docs/process_traces/2026-09-24-activation-278ebc9e/91-claimgate-final-texts-v2.md:3)