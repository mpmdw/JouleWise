# Contract-lens refutation of `ex-30-synthesis.md` (CLAIMGATE-WIRING-01)

**Scope:** Opus 5.5 refuter, read-only, one foreground session. I verified the packet: `00-charge.md` has sha256 `b5c3a235…9d019`, as pinned. Base is `7ece2750`. Its `joulewise/`, `configs/` and `scripts/` trees are identical to the seats' `092ac6be`. The WIP is `origin/feat/2026-09-24-claimgate-v2` at `3cd00c73`. I ran no tests. "syn" below means `ex-30-synthesis.md`.

## Verified (no finding)

- **B-W2 is confirmed.** WIP `__init__.py:781` and `:1018` both test `complete_blocks < (5 if … "v2" else 2)`, and then pass block observations to `estimate_paired_blocks` (`:787-799`). No envelope aggregation happens on this path.
- **Opus Fact 2 is confirmed, with more evidence than it cited.**
  - The finalized evidence keys are singletons: `whole_window_verdict`, `bracket_binding`, `calibration_ledger` and `aggregate_floor_artifact` (`analysis_manifest_v3.py:1160-1165`).
  - There is one `bracket_ref = evidence["bracket_binding"]` (`:4357`) and one `window_id` (`:3659`).
  - `planned_n_blocks` must equal **10** (`:2300`).
  - `analyze_claims` takes one manifest path (`__init__.py:1653-1656`).
  - Astra's in-manifest envelope list could only work by changing the cardinality of the v3 finalized evidence. That is a redesign, not wiring. The synthesis's statement at syn:27 is correct.
- **A1 is confirmed.** The epoch has six fields (`calibration_acceptance_d079_v2_n17_r7.json:20-27`). The members are `b_fiducial_s` (`:53`). `ISSUED_ACCEPTANCE_REGISTRY` is at `calibration_bracketing.py:147`.
- **The Astra `repin.py` finding is confirmed.** `tests/fixtures/paper_custody/repin.py:24-31` writes one `pending_roles` entry, but `supply_map.json` holds two (`…qwen3-1p7b.v5` and `…qwen3-8b.v5`). All five roles are `fixture.*`.
- **S-PR, PR-0 part: AFFIRM.** A golden-capture PR that changes no claim-gate component does not break CG-4's "one PR, components versioned together" (`ex-91:9`). The condition: PR-0 may touch only `scripts/capture_claim_replay_golden.py`, `tests/golden/` and its pin test.
- **S-W3 Holm: no conflict with a frozen family.** No frozen family mixes versions. AP-5M v5 is not yet frozen, and each `ap_spec_*` registry freezes two contrasts under one `floor_selector`. Version-pure registration changes no frozen m.

---

## BLOCKER

### C-1. The W2/W3 proposal contradicts CG-4(c)'s ruled site list, and the synthesis never says it is amending a fixed text

**Where:** syn:28, :40-41, :62-63 against `ex-91:9` (CG-4(c)).

CG-4(c) rules these code sites:
- `registry.py:462-466` floor selector accepts `floor_field ∈ {max(floor_abs_j,floor_cmp_j) (v1), floor_est (v2)}` and checks `floor_unit`;
- `__init__.py:1278` passes the floor matching `floor_class` and the interval matching `interval_confidence`;
- `artifact.py` and `paper_custody.py` validators accept `ci90` fields beside `ci95` and record `interval_confidence`;
- `inputs.py` `FloorResolution` gains `floor_est`, `floor_unit` and `floor_class`.

The synthesis contradicts or omits each of these:
- It restores `registry.py` to its base bytes. Opus's own test `test_registry_v2_validator_bytes_unchanged` enforces that.
- It restores base bytes in `artifact.py` and `paper_custody.py`, and moves CI90 to the envelope-set artifact.
- It is silent on `inputs.py`. The kept-WIP list at syn:61 omits `inputs.py`, though the WIP changes it (+3 lines).

The move itself is correct. The single-window v3 manifest (C-1 facts above) makes CG-4(c)'s sites unable to host a k-envelope estimate. But ex-00:3 says a faithful-wiring impossibility must be raised *as a BLOCKER*. Presented as it is, an implementation seat faces two binding texts that exclude each other, and has to choose.

**Corrected text (for the final wiring rulings):**
> "**CG-4(c) wiring amendment** (forced by `analysis_manifest_v3.py:1160-1165,:2300,:4357`: one finalized manifest = one window = one envelope). The v2 floor selector (`floor_field = floor_est`, `floor_unit` equal to the estimand unit, `floor_class = estimate`) lives in `joulewise.claim_registration.v2` (`joulewise/claim_registration.py`). The `interval_confidence`/`ci90` fields and the floor-class dispatch live in `joulewise/analysis_engine/envelope_set.py` and its artifact `joulewise.claim_verdicts_envelope_set.v1`. They do not live at `registry.py:462-466`, `__init__.py:1278`, or the window-level `artifact.py`/`paper_custody.py` validators, which keep their base bytes except for the `envelope_member_only` refusal. `inputs.py` `FloorResolution` gains `floor_est`, `floor_unit` and `floor_class` as ruled. The window engine refuses `floor_class = estimate` with `floor_class_mismatch`, so F_est and F_block can never be swapped at either layer. Every other CG-4(c) item stands."

---

## MATERIAL

### C-2. The v1 allowlist sits at a boundary that is already closed, and the real v1 path stays open

**Where:** syn:40-41.

The allowlist does nothing where it is placed:
- `analysis_manifest.validate_analysis_registry` already refuses any `registry_id` other than `slice_2m_ap2_v1` (`analysis_manifest.py:495-496`).
- `validate_analysis_registry_v2` is frozen to its two-contrast template (`registry.py:451`) and to `condition_family_ids == ["spec_off","spec_on"]` (`:467`). No new v1 registration can pass either validator today.
- Opus's WRITE_SCOPE places the check only in `analysis_manifest.py:485` (seat :138), while `registry.py` stays at base bytes. So the two `ap_spec_*.v2.json` digests it lists are never checked.

The v1 path that *is* open:
- v3 manifests reference no registry. `grep registry joulewise/analysis_manifest_v3.py` returns nothing.
- `_claim_issuance_gate` issues claims from one finalized v3 manifest, its claim verdicts, and the block floor (`paper_custody.py:597-627`).
- Under syn:28 / Opus W2 §2, a missing v2 group *means v1*. A new AP-5M window manifest without the group would therefore get v1 admission of a block mean. The v1 engine needs at least 2 blocks (WIP `__init__.py:781`, `else 2`), so there is no v1 single-block claim path at all.
- That admission is exactly what CG-1's last sentence forbids: "F_block … never gates a mean".

**Corrected text:**
> "v1 claim admission is closed at the issuance boundary. `V1_CLAIM_REPLAY_ALLOWLIST` is the finalized-manifest digests of every checked-in v1 claim-verdict artifact and fixture enumerated in the PR-0 golden. `analyze_claims` and `_claim_issuance_gate` return non-admitting `claim_rule_version_v1_closed` for any v1 contrast whose finalized manifest digest is not on the list. The artifact is still written for replay, so A2's byte-identity holds for every listed input. The registry-digest allowlist is dropped. Test: `test_new_v3_manifest_without_v2_group_cannot_admit`."

The golden in C-2 must therefore enumerate those manifest digests.

### C-3. CG-4(d), (f) and (g) are missing from the "one PR", and (f) is moved after it

**Where:** syn:47, :60-66 against `ex-91:9`.

- CG-4 is "One PR … in this order: (a)…(g)", and (f) is the AP-5M v5 registration.
- The synthesis's PR list names only the kept WIP items plus W1–W4. It then puts "AP-5M v5 registration frozen with the pin named" in the data-side stage.
- Opus's own ordering kept (f) inside the PR, as "AP-5M v5 text with bracketed F_est fields" (seat :190). The synthesis dropped it.
- The tension between (f) and M-1/CG-2 (the F_est id must be recorded before data, but no pin exists until at least 5 calibration windows under 25G83) resolves because "before data" means before *claim* data.

**Corrected text:**
> "The CG-4 PR carries (f): the AP-5M v5 registration document (`claim_registration.v2`). It includes:
> - the J/correct primary estimand;
> - `n_reg = 10` (forced by `analysis_manifest_v3.py:2300`);
> - one claim shape per contrast;
> - CG-1/CG-2 cited by id;
> - the rewritten window-admission sentence;
> - `estimate_floor` = `{artifact_id, sha256, floor_est, floor_unit}` present with null values.
>
> The validator refuses `freeze_status: frozen` while `estimate_floor` is null (`claim_registration_floor_unbound`). The later pin PR fills only those four fields and freezes the registration before the first claim window. The PR also carries (d), D-numbered addenda for every constant including `n_reg = 10` and `n_cal` (C-5), and (g), the notice to Ed."

### C-4. S-W1 cites a contract row that names the v1 source only, and it drops the envelope-identity refusal

**Where:** syn:33, :35.

- `docs/contracts/analysis_plans.md:29` names "the P2-015 calibration artifact" as the source of `max(floor_abs_j, floor_cmp_j)`, which is v1.
- Neither CG-4(b) nor the WIP row (WIP `analysis_plans.md:29`) names any producer for F_est.
- So "reuses the producer the contract already names" is not contract authority. It is a new binding, and a sound one, that must be written into the v2 row.

The code facts, answering the charge's question:
- **Deltas: present.** `block_deltas_j` is stored per cell (`detection_floor.py:1679`).
- **Window id: optional.** `launch_lineage` (and so `window_id`) is in `_PROVENANCE_OPTIONAL_KEYS` (`:2130-2135`). Lineage uniqueness across members is enforced only when present (`floor_extraction.py:2728-2736`). An artifact without lineage can therefore pool blocks from several windows.
- **Same model within a block: not enforced.** Members carry `config_sha256` (`:2117-2125`), but no A-versus-B equality check exists. Per-producer `model_runtime_config.model_artifact_sha256` (`:2278-2280`) binds one model per producer, not per block.

**Corrected text:**
> "The v2 entry of `analysis_plans.md:29` names the source: 'F_est from the `comparative` component of issued P2-015 floor artifacts, one artifact per envelope.'
>
> The mint refuses:
> - `estimate_floor_envelope_identity_missing` if `launch_lineage` is absent;
> - `estimate_floor_envelope_duplicate` if `window_id`s repeat;
> - `estimate_floor_not_null_contrast` unless every block's A1, A2, B1 and B2 members share one `config_sha256`;
> - `estimate_floor_model_mismatch` unless all producers bind one `model_artifact_sha256`."

### C-5. Q-M3 can be answered from the code and should not go to the council; M-2 leaves the n_cal/n_reg relation open

**Where:** syn:36-37, :54.

**Q-M3.** `block_deltas_j` are raw `abba_delta = (B1+B2−A1−A2)/2` (`detection_floor.py:1449-1453`, `floor_extraction.py:2711-2713`) in both estimator branches.
- The D-124 two-shared-edge path hands the *same* raw deltas to `comparative_false_effect_floor` (`floor_extraction.py:619-620`, `:2774-2786`). It changes only the admissible half-widths.
- So the deltas are not a "differenced residual". D-124's condition of "identical covariance treatment" (`decision_log.md:8337`) is met, because F_est uses the raw deltas with no timing term and CG-1 applies B once, on the claim side.
- The only open part, whether the contrast is same-model, is a mint check (C-4).

**Corrected Q-M3 text:**
> "Q-M3 is closed on code. S-W1 does not wait for the council."

**M-2.** "Fix `n_cal` at mint" leaves the relation between `n_cal` and `n_reg` open.
- s_cal is the SD of envelope means, which scales roughly as 1/√n.
- If `n_cal > n_reg`, F_est comes out too small for claim envelopes (anti-conservative).
- The WIP simulation 94 uses 6 blocks per envelope on both sides, while v3 forces 10.

**Corrected M-2 text:**
> "`n_cal = n_reg` (= 10). Shorter calibration envelopes are excluded and listed. k_cal counts the retained ones. CG-4(e) reruns the simulation at `n_reg = n_cal = 10`."

### C-6. Q-B1 leaves out CG-4(f)'s own third option and treats (b) as a council choice

**Where:** syn:51-53 against `ex-91:9`.

- CG-4(f) already allows "a registered dimensionless margin with a derived, matched floor".
- Option (b), "AP-5M v5 registers J", would reverse a fixed ruled text (J/correct as primary). That needs a cold-gate amendment of CG-4(f), not just a council choice.
- Landing the PR with J/correct refusing is **consistent** with CG-4(f), provided (f)'s registration text is in the PR (C-3) and the refusal is typed.

**Corrected text:**
> "The CG-4 PR lands with the J/correct primary registered. Evaluation returns `not_resolvable`:
> - reason `floor_est_unbound` while the registration's `estimate_floor` is null;
> - reason `floor_unit_mismatch` if a J artifact is bound to a J/correct estimand.
>
> The council chooses among (a) a graded-workload null calibration with a J/correct producer, and (c) CG-4(f)'s registered dimensionless margin with a derived, matched floor. Choosing J-primary requires a cold-gate amendment of CG-4(f). Dividing J by the mean correct count is refused. Test: `test_jcorrect_primary_refuses_without_jcorrect_floor`."

---

## NIT

- **N-1, syn:16.** "code- or registry-pinned" leaves the seat a choice. Say "code-pinned `ISSUED_ESTIMATE_FLOOR_REGISTRY` in `joulewise/estimate_floor.py`", matching S-W1.
- **N-2, syn:17.** "wrong unit → `not_resolvable`" should name CG-4(c)'s reason code: `not_resolvable` / `floor_unit_mismatch`.
- **N-3, syn:62-64.** The in-PR order W2 → W3 → W1 puts the evaluator before the module it imports: the envelope-set replay calls W1's `authenticate_estimate_floor_bytes` (Opus seat :39, :92). Order it W1 → W2 → W3 → W4.
- **N-4, syn:41.** The split is narrower than stated. The WIP `registry.py` already refuses mixed versions within one registry ("mixed claim rule versions require separate floor selectors", WIP diff at `validate_analysis_registry_v2`). Both designs are version-pure per registry. The real dispute is where the v2 selector lives (C-1).
- **N-5, syn:55.** `claim_shape_unimplemented` is a new reason code. Add it to `reason_kinds.py`, and record the magnitude deferral in the (d) addendum. CG-1 calls magnitude "optional", so refusing it does not contradict CG-1.
- **N-6, route to the council, not wiring.** For contrasts across models (AP-5M), CG-1's "same-model null" does not say *which* model's calibration supplies F_est. C-4's `estimate_floor_model_mismatch` makes this a forced registration field. The registration must name the model, and the council should rule the rule.

## Tally

**BLOCKER:** C-1.
**MATERIAL:** C-2, C-3, C-4, C-5, C-6.
**NIT:** N-1 to N-6.
**Affirmed:** B-W2, Opus Fact 2, A1, the Astra `repin.py` finding, PR-0 as a separate PR, and no frozen-Holm conflict.
