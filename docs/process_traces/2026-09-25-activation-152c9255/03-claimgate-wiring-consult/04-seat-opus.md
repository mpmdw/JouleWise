# Opus 5.5 seat: CLAIMGATE-WIRING-01 (blind)

Everything here was read on `092ac6be` and on the WIP branch `origin/feat/2026-09-24-claimgate-v2@3cd00c73` (cited as "WIP"). I wrote nothing to the repository and ran no tests. Every citation is to code I read.

## 0. Three facts that change the question's framing

- **Fact 1: the calibration acceptance cannot produce F_est.** The D-079 acceptance, including its 25G83 successor, is a timing calibration. Its identity epoch is a 59-pulse powermetrics protocol (`"pulse_protocol_id": "powermetrics_pulse_fiducial_v3"`, `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:20-26`). Its members are `b_fiducial_s` values in seconds (`:53`). It holds no joules and no same-model ABBA null contrasts. The joule-scale null contrasts live in the P2-015 detection-floor artifact's `comparative` component (`joulewise/detection_floor.py:1131-1153` and `:2060`). The contract row names that artifact as the floor's source: "from the P2-015 calibration artifact" (`docs/contracts/analysis_plans.md:29`). So the acceptance is the **epoch authority** for F_est, not its producer. Floor producers already bind to it through the v2 pinset's `calibration_acceptance` row (`detection_floor.py:2274-2286`).
- **Fact 2: one finalized v3 manifest covers one quiet window, which is one envelope.** It carries a single bracket binding with a single `window_id` (`joulewise/analysis_manifest_v3.py:3656-3659`) and a single `aggregate_floor_artifact` (`:1160-1165`). `analyze_claims` takes one manifest (`joulewise/analysis_engine/__init__.py:1653`). CG-1's estimand needs k ≥ 5 envelopes, so a faithful v2 claim needs a **cross-manifest (envelope-set) layer**.
  - The WIP v2 path instead estimates over *blocks inside one manifest*: `complete_blocks < 5` at WIP `__init__.py:781,1018`, and `estimate_paired_blocks` is fed block observations. It never calls `aggregate_envelope_observation` (WIP `estimators.py:466`). That treats blocks as independent replicates, which ruling 20 M1 rejected (`66-coldgate-packet-claimgate/20-…ruling.md:64`).
  - Today this is fenced only by the blanket refusal at WIP `artifact.py:2294`.
  - Wiring CG-1 is **possible**, but not in the shape the WIP took.
- **Fact 3: no paper number is custody-bound today.** All five supply-map roles are `test_fixture_non_issuing` (`configs/paper_supply/supply_map.json`, `roles.fixture.*`), and the production roles are `pending_desk_day`. The 19 stale digests are fixture receipts only.

---

## W1: where F_est comes from

**Design (executable):**

1. **New artifact** `joulewise.estimate_floor_artifact.v1`, stored at `configs/calibration/estimate_floor/<artifact_id>.json`. It has exact keys:
   - `schema_version`, `artifact_id`
   - `derivation_rule_id` = `"cg1_f_est.v1"`
   - `unit` (`"J"` only; see concern B-1)
   - `metric`, `window_class`, `backend`, `condition_family_id`
   - `epoch`: `{acceptance_id, acceptance_file_sha256, identity_epoch}`, where `identity_epoch` is a verbatim copy of the six-field vector
   - `envelopes[]`: rows of `{envelope_id, floor_artifact_id, floor_artifact_sha256, calibration_cell_id, n_blocks, block_deltas_j[], envelope_mean_j}`
   - `k_cal`, `mean_cal`, `s_cal`, `t_critical`, `guard_factor`, `floor_est`
   - `provenance`: `{project_commit}`
2. **Minting.** The new script `scripts/mint_estimate_floor_artifact.py` mints the artifact through `joulewise/estimate_floor.py::mint_estimate_floor(floor_paths, pinset_paths, evidence_roots, *, metric, window_class, condition_family_id)`. For each input floor artifact:
   - (a) Authenticate the bytes with `authenticate_floor_artifact_bytes` (`inputs.py:881`) and bind them with `bind_floor_artifact_evidence(mode="issuing")` (`inputs.py:1610`). The selected cell must have zero problems.
   - (b) `envelope_id` = `provenance.launch_lineage.window_id` (`detection_floor.py:2128-2146`). If the lineage is absent, refuse with `estimate_floor_envelope_identity_missing`.
   - (c) Read `block_deltas_j` from the comparative record and set `envelope_mean_j = fsum/n`.
   - (d) Resolve the producer's `calibration_acceptance.acceptance_id` from the pinset. It must be in `ISSUED_ACCEPTANCE_REGISTRY` (`calibration_bracketing.py:147`) and be identical across all envelopes.
   - (e) Envelope ids must be distinct.
   - (f) If k_cal < 5, write no artifact and exit with `not_resolvable`.
   - (g) Compute `floor_est` with the WIP's `estimate_scale_floor` (WIP `detection_floor.py:858`).
3. **Authentication.** Add a code-pinned registry `ISSUED_ESTIMATE_FLOOR_REGISTRY = {artifact_id: {"file_sha256": …}}` in `joulewise/estimate_floor.py`. It follows the same pattern and assurance level as `ISSUED_ACCEPTANCE_REGISTRY` (`calibration_bracketing.py:1148-1156`). A pin enters only through a reviewed PR. A caller-asserted `floor_est` is never evidence.
4. **Registration binding.** Every v2 registration names `estimate_floor: {artifact_id, sha256, floor_est, floor_unit}`, frozen **before data for every claim shape**, not only CG-2's (see concern M-1).
5. **Replay (`authenticate_estimate_floor_bytes`), used by the envelope-set evaluator and by custody:**
   - (i) The sha must equal the registry pin and the registration's sha.
   - (ii) Recompute each `envelope_mean_j` from `block_deltas_j` and `floor_est` from the envelope means. Require `isclose(rel_tol=1e-12)` against both the artifact's value and the registered value. This is the same arithmetic-replay tolerance `artifact.py` uses throughout, not a science threshold.
   - (iii) `unit` must equal the estimand unit.
   - (iv) For each claim envelope, the acceptance its aggregate floor pinset binds must resolve to an `identity_epoch` equal to `epoch.identity_epoch`.
   - (v) F_est envelope ids must be disjoint from claim envelope ids.
   - (vi) When evidence roots are supplied, re-authenticate each referenced floor artifact by sha and re-derive `block_deltas_j`.
6. **How the acceptance lane fits.** The ACCEPTANCE-25G83-02 successor defines the epoch. A 25G83 F_est exists only after at least five floor-calibrated quiet windows have been judged under that issued acceptance. The r7 acceptance (epoch 25F84) can never supply a 25G83 claim.

**WRITE_SCOPE:** `joulewise/estimate_floor.py` (new), `scripts/mint_estimate_floor_artifact.py` (new), `configs/calibration/estimate_floor/` (new, empty until the first mint PR), `tests/test_estimate_floor.py` (new), `joulewise/detection_floor.py` (only `estimate_scale_floor`, carried from the WIP).

**Refusals, as named tests in `tests/test_estimate_floor.py`:**
- `test_refuses_caller_asserted_floor_est`: an unpinned sha gives `floor_est_unauthenticated`.
- `test_refuses_recompute_mismatch`: one edited `envelope_mean_j` or `floor_est` gives `floor_est_recompute_mismatch`.
- `test_refuses_cross_epoch_floor`: a 25F84 F_est against a 25G83 envelope gives `floor_est_epoch_mismatch`.
- `test_refuses_k_cal_below_five`: gives `not_resolvable`, and no artifact is written.
- `test_refuses_mixed_acceptance_envelopes`
- `test_refuses_missing_window_identity`
- `test_refuses_unit_mismatch`: a J/correct estimand against a J artifact gives `floor_unit_mismatch`.
- `test_refuses_calibration_claim_overlap`: gives `floor_est_envelope_overlaps_claim`.
- `test_refuses_timing_acceptance_as_floor_source`: passing the acceptance JSON fails the schema.

**Concerns:**
- **B-1 (BLOCKER for AP-5M v5's primary contrast, not for the wiring).** No J/correct null producer exists. Floor observations carry only `metric_value_j` (`detection_floor.py:2105-2121`), and no calibration records correctness. CG-4(f) makes J/correct the AP-5M v5 primary estimand. That primary cannot be admitted until one of two things happens:
  - (a) a graded-workload null calibration plus a J/correct producer is ruled; or
  - (b) AP-5M v5 registers J.

  A seat must never convert F_est by dividing J by the mean correct count. That is new science, not wiring.
- **M-1 (MATERIAL).** CG-2 explicitly requires F_est before data. CG-1 (direction) does not say so. Freezing the F_est artifact id at registration for every shape is my recommendation. Otherwise the set of calibration windows can be chosen after the claim data are seen.
- **M-2 (MATERIAL, open).** CG-1 does not rule on calibration envelopes with unequal `n_blocks`. I recommend a fixed `n_cal` argument at mint: shorter envelopes are excluded and listed, mirroring n_reg. This needs a one-line magistrate ruling.
- **M-3 (MATERIAL).** The comparative component may be the D-124 two-edge common-mode estimate (D-125 §1). Confirm that its `block_deltas_j` are the "same-model ABBA null contrasts" CG-1 means, and not a differenced residual.
- **N-1 (NIT).** The 25G83 acceptance schema needs no change for this.

## W2: manifest v2 schema

**Design:**

1. **`joulewise/analysis_manifest.py` (v1): no change.** v1 entries carry no window or envelope identity (`:75-89`; contrasts `:108-124`), so no CG-1 envelope can be formed from them. The v2 keys stay unknown keys and refuse. This keeps v1 behaviour byte-identical by construction.
2. **`joulewise/analysis_manifest_v3.py`: add one optional, all-or-none group** `V2_CLAIM_KEYS = {"claim_rule_version", "claim_shape", "claim_registration"}` to `_PROSPECTIVE_CONTRAST_KEYS` (`:1074`) and `_FINALIZED_CONTRAST_KEYS` (`:1215`). When the group is present:
   - `claim_rule_version == "v2"` exactly. Absence means v1, and an explicit `"v1"` stays an unknown-key refusal, so v1 has exactly one spelling.
   - `claim_shape` is `"direction"` or `"equivalence"`. `"magnitude"` refuses with `claim_shape_unimplemented` until the τ and shifted-null path exists (concern M-5).
   - `claim_registration` has exact keys `{registration_id, sha256, contrast_id}`.
   - The finalized manifest's group must be byte-equal to the prospective one. If not, refuse with `analysis_finalization_claim_registration_mismatch`.
   - The window's `floor_selector` is **unchanged**: it stays v1 and governs window admission and diagnostics. The claim floor lives in the registration.
3. **New registration schema** `joulewise.claim_registration.v2`, in the new module `joulewise/claim_registration.py`. Keys:
   - `schema_version`, `registration_id`, `plan_id`, `claim_rule_version: "v2"`
   - `multiplicity: {method: "holm", alpha: 0.05, m, missing_kept: true}`
   - `estimate_floor` (as in W1)
   - `contrasts[]`: `{contrast_id, claim_shape, metric, condition_a_id, condition_b_id, hypothesized_direction, equivalence: {margin} | null, n_reg, k_planned ≥ 5, term_scopes: {name: "independent_run"}}`
   - `envelope_admission: "prospective_manifest_names_registration.v1"`

   Validation: `equivalence.margin > floor_est` strictly (the B check happens at evaluation, per CG-2). `n_reg` must equal the window manifests' `planned_n_blocks` (`analysis_manifest_v3.py:2300`). Any scope other than `independent_run` refuses with `envelope_term_scope_unknown` (the R2 deferral stands).
4. **Window engine.** A contrast carrying the v2 group gets a non-admitting evaluation with the new reason code `envelope_member_only`, and `claim_ready_for_l2_l3` is false. Delete the WIP's window-level v2 admission branches in `artifact.py` and `paper_custody.py`, and restore their base bytes. The CI90, `floor_est` and `minimum_attainable_p` fields move to the envelope-set artifact.
5. **Envelope-set evaluator.** New module `joulewise/analysis_engine/envelope_set.py`: `analyze_envelope_set(registration_path, windows, estimate_floor_path, *, strict_validator)`.
   - Envelopes are the windows whose *prospective* manifest names this registration, in capture order.
   - An envelope is retained iff it has n_reg complete blocks. Excluded envelopes are listed.
   - k < 5 gives `not_estimable`.
   - Per-block observations come from the existing per-window preparation (`_prepare_contrast_v3`) on authenticated inputs, then pass through `aggregate_envelope_observation`, then `estimate_paired_blocks(k envelopes, confidence)`.
   - Then apply CG-1 conditions 1–3 or CG-2, with Holm at the frozen m across the registration, and the sign-flip diagnostic computed on the **k envelopes**.
   - It writes the artifact `joulewise.claim_verdicts_envelope_set.v1`, with its own exact-key validator in the same module.

**WRITE_SCOPE:** `joulewise/analysis_manifest_v3.py`, `tests/test_analysis_manifest_v3.py`, `tests/test_analysis_manifest.py` (only the refusal and golden tests), `joulewise/claim_registration.py` (new), `tests/test_claim_registration.py` (new), `joulewise/analysis_engine/envelope_set.py` (new), `tests/test_envelope_set.py` (new), `joulewise/analysis_engine/__init__.py`, `joulewise/analysis_engine/claims.py` (reason code), `joulewise/analysis_engine/reason_kinds.py`, `joulewise/analysis_engine/artifact.py` and `joulewise/paper_custody.py` (reverting the WIP v2 branches).

**Refusals, as named tests:**
- **`test_single_window_v2_contrast_never_admits`**: a 10-block window whose block-level t would admit still yields `envelope_member_only`. This is the headline test.
- `test_v2_group_all_or_none`
- `test_explicit_v1_token_refused`
- `test_magnitude_refused_until_implemented`
- `test_finalized_group_must_equal_prospective`
- `test_envelope_not_preregistered`: a window that does not name the registration is ignored and listed.
- `test_short_envelope_excluded_and_listed`
- `test_k_below_five_not_estimable`
- `test_v1_manifest_refuses_claim_rule_version_key`
- `test_v1_manifest_behaviour_golden`: see W4.

**Concerns:**
- **B-2 (BLOCKER on the WIP as wired).** The WIP's block-level v2 admission (Fact 2) must be removed, not un-fenced. Adding the v2 manifest fields and deleting the `artifact.py:2294` refusal would admit blocks as replicates.
- **M-4.** WIP `registry.py:463` strips `claim_rule_version` and `claim_shape` before the template-freeze comparison, so those fields are never frozen by the template. Revert (see W3).
- **M-5.** Magnitude is unwired. The evaluated shape is never `"magnitude"` (WIP `__init__.py:1402`; `claims.py:313-316`), so a registered magnitude contrast silently becomes exploratory. It must refuse at registration instead.
- **M-6.** The sign-flip minimum p (WIP `__init__.py:86`) is computed over blocks. It must be computed over envelopes.

## W3: mixed v1/v2 registries

**Decision:** registration documents are **version-pure**, which means separate registries per version. Per-contrast floor selectors are kept where they already exist: manifest v1 `:123` and v3 `:295`. No new mixed-selector logic is added anywhere.

Reasons:
- (a) The only registry-level shared selector is `joulewise.analysis_registry.v2` (`registry.py`). It freezes exactly two contrasts against the `_expected_contrasts` template, so mixing versions would mean editing a frozen template.
- (b) v2 needs registration-level objects that have no per-contrast or per-window meaning: the F_est binding, `k_planned`, `n_reg` and m.
- (c) One Holm family mixing block-level v1 p-values with envelope-level v2 p-values is incoherent.

**Executable steps:**
1. Restore `joulewise/analysis_engine/registry.py` to its base bytes. The WIP `V2_CONTRAST_KEYS`/`V2_FLOOR_KEYS` and the mixed-version refusal are dropped.
2. v2 contrasts exist only in `joulewise.claim_registration.v2` (W2 §3). Its validator refuses any contrast whose version is not v2, and refuses a multiplicity family containing a contrast from another registration, with `multiplicity_family_mixed_rule_versions`.
3. **What the existing registries become:**
   - `ap_spec_draft_front.v2.json` and `ap_spec_native_mtp_front.v2.json` (`analysis_registry.v2`, `pending_p2_015`, floor `max(floor_abs_j,floor_cmp_j)`) and `slice_2m_ap2.v1.json` (`analysis_registry.v1`, `planned_n_blocks` 5) all stay **v1, byte-identical, replay-only**.
   - None issues a paper claim today (ruling 20 `:32,:83`).
   - Their mean-scale contrasts become claim-bearing only by re-registering as a new `claim_registration.v2` document that cites the old registry by sha.
   - Add a closed allowlist `V1_CLAIM_REGISTRY_SHA256S` holding exactly these three file digests. Any other v1-schema registry presented for claims refuses with `claim_rule_version_v1_closed`. This stops a new registration choosing v1 to avoid F_est. v1 remains the ruled rule for single-block claims, and none is registered today.

**WRITE_SCOPE:** `joulewise/analysis_engine/registry.py` (revert), `joulewise/analysis_manifest.py` (only the allowlist constant and its check in `validate_analysis_registry`, `:485`), `tests/test_analysis_manifest.py`, `tests/test_analysis_registry*.py` (whichever file holds the `registry.v2` tests), `joulewise/claim_registration.py`.

**Refusals, as named tests:**
- **`test_registry_v2_validator_bytes_unchanged`**: `registry.py` blob equals base.
- `test_v1_registry_allowlist_closed`
- `test_existing_three_registries_validate_unchanged`
- `test_v2_registration_rejects_v1_contrast`
- `test_holm_family_refuses_mixed_versions`

**Concerns:**
- **M-7.** The allowlist is stricter than the ruled text. Without it, CG-4(b)'s "mean claims use F_est" is unenforced for any new v1 registration.
- **N-2.** The WIP seat preferred per-contrast selectors. Under Fact 2 that preference solves a problem that stops existing once v2 lives at registration level.

## W4: paper-custody receipt reissue

**Mechanics.** `_validator_source_sha256` hashes the family, the policy constants, every census member's source and the **whole owner modules** (`paper_custody.py:840-858`). Any edit to `claims.py`, `artifact.py`, `estimators.py` and the other owner modules therefore changes every family's receipt. The receipt's fields are exactly `{family, inputs, replay_codes, schema_version, status, validator, validator_source_sha256}` (`:1265-1299`). With inputs fixed, the only free field is `validator_source_sha256`. The test fixture rebuilds receipts and asserts the supply map's pinned digests (`tests/test_paper_custody.py:160-175`), and that assertion is where the 19 failures come from. The repo has repinned this way several times before: `6e380f55`, `21331ac9`, `ed44276a` ("hash-only repin").

**Procedure (executable):**
1. **PR-0, before any validator change.** `scripts/capture_claim_replay_golden.py` writes `tests/golden/claimgate_v1_replay.json`, in canonical JSON, containing:
   - (a) per fixture family, `_replay_family`'s `(authentic, admitted, grants, validator_codes)`;
   - (b) for every checked-in claim-verdict artifact (`docs/paper/fill-rehearsal/*.json` plus the test fixtures), the `validate_claim_verdicts` error list and each contrast's `evaluate_claim` output;
   - (c) the validator outcomes for every checked-in manifest and registry;
   - (d) the v1 epoch replays (09-19 nights: INCONCLUSIVE m=4, FAIL m=7).

   The test pins the golden's git **blob sha** as a code constant.
2. **Minting.** The *implementation seat* mints the receipts as the last commit of the source-changing PR, titled "hash-only repin". It runs `scripts/repin_paper_supply_receipts.py --write`, which builds receipts with the same builder as the test. Move that builder into a shared helper so the test and the script cannot diverge. The script rewrites only `roles.*.receipt.expected_sha256` and `roles.*.inventory.expected_sha256`. Nobody hand-edits digests. The magistrate verifies with the checks below, and the cold gate reads their output.
3. **The distinguishing check.** A reissue is legitimate iff both of these hold:
   - (i) **`test_supply_map_repin_is_hash_only`**: the supply map at HEAD differs from the one at the PR-0 commit only at those JSON paths. Every `inputs[].expected_sha256`, `source_census`, `pending_roles` value and path is identical, and every rebuilt receipt has `replay_codes == []` and `status == "PASS"`.
   - (ii) **`test_claimgate_v1_replay_golden_unchanged`**: fresh replay is byte-equal to the golden, and the golden's blob equals the pinned blob.

   Masking a real change must show up as either a non-digest diff in the map or a golden mismatch. A golden regenerated in the same PR as the source change fails the blob pin, so any golden refresh needs its own separately reviewed PR.
4. **Proof that no paper number moved.** Fact 3 means no issued number flows through custody. The golden in (ii) covers every checked-in verdict artifact the paper's rehearsal renders from.

**WRITE_SCOPE:** `configs/paper_supply/supply_map.json` (digest fields only), `scripts/repin_paper_supply_receipts.py` (new), `scripts/capture_claim_replay_golden.py` (new, PR-0), `tests/golden/claimgate_v1_replay.json` (new, PR-0), `tests/test_paper_custody.py` (builder moved to a shared helper, e.g. `tests/_paper_custody_fixture.py`), `tests/test_paper_custody_repin.py` (new).

**Refusals, as named tests:**
- **`test_repin_refuses_non_digest_map_change`**: in a temporary copy, mutate one input sha; `--check` must exit non-zero with `paper_custody_repin_not_hash_only`.
- `test_golden_blob_pinned`: editing the golden fails.
- `test_receipt_rebuild_matches_pin`

**Concerns:**
- **M-8.** Once v2 claims are custody-issued, add `claim_registration`, `envelope_set` and `estimate_floor` to the `claim_evidence` owner census (`paper_custody.py:822-831`). That is a second repin under the same checks. Until then, `_claim_issuance_gate` must refuse artifacts marked v2, restoring the base bytes and removing the WIP's `paper_custody.py:633-659` branch.
- **N-3.** Whole-module pinning makes every engine PR a repin. That is acceptable because the check is mechanical.

## PR ordering

1. **PR-0, golden capture (quick tier, no source change).** W4 §1.
2. **PR-1, CG-4 core (full tier).** This is CG-4's "one PR", covering items (a)–(g):
   - the WIP `0d2b4497` components: D-083/D-102 addenda, the analysis-plans row, `estimate_scale_floor`, the confidence parameter and envelope helper, the claims v2 codes, CG-3, and simulation 94;
   - the W2 manifest-v3 group, `claim_registration.v2` and `envelope_member_only`;
   - the W3 revert of `registry.py` and the allowlist;
   - the WIP window-level v2 admission removed;
   - AP-5M v5 text with bracketed F_est fields (CG-4(f));
   - the last commit is the hash-only repin.

   v2 admission is structurally unreachable at this point.
3. **PR-2, the F_est producer.** W1 modules, script and an empty pin registry.
4. **PR-3, the envelope-set evaluator and artifact validator, plus the custody census addition** and its second repin.
5. **Data-side, in order:** ACCEPTANCE-25G83-02 issued → at least five floor-calibrated 25G83 windows → mint the F_est artifact → **PR-4** pins it → AP-5M v5 registration frozen, naming the pin → claim windows → envelope-set claim.

If the magistrate reads CG-4's "one PR" as covering PR-2 and PR-3, fold them into PR-1 and keep the order inside it.

## What would show this design wrong

- A finalized v3 manifest that can legitimately bind two or more windows would make per-manifest envelopes possible and remove the need for PR-3. My evidence against this: one bracket and one floor attachment (`analysis_manifest_v3.py:1160-1165,3656`).
- Real P2-015 floor artifacts that lack `launch_lineage.window_id` (it is optional, `detection_floor.py:2128`) would mean W1's envelope identity needs another source.
- If the judge meant CG-1's "same-epoch accepted calibration" to be the D-079 acceptance corpus, CG-1 cannot be implemented, because that corpus is in seconds. That would be a BLOCKER for Fable. My reading is the P2-015 floor calibration judged under the accepted epoch.
- If any supply-map role is issuing at PR time, a hash-only repin is not enough.
- Any mismatch against the PR-0 golden in PR-1 means the WIP changed v1 behaviour.
- If D-124's comparative estimator is not a null contrast in CG-1's sense (M-3), F_est needs a ruling first.

## Expected disagreement

- The other seats will probably accept the framing that the acceptance generation produces F_est. I hold that it produces seconds and can only be the epoch authority.
- They will probably add v2 fields per contrast inside one manifest and admit there. I hold that one manifest is one window, so the claim must be admitted in a cross-manifest layer.
- Several may follow the WIP seat's per-contrast selectors. I propose version-pure registrations plus a closed v1 allowlist.
- Some will read "one PR" literally. Some will not require F_est before data for direction claims, which is where I am stricter than CG-1's text.
- The J/correct F_est producer gap (B-1) may be missed entirely.
