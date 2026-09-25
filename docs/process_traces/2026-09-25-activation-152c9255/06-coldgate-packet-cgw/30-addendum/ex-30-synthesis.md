# 03/30 — Magistrate synthesis, design consult CLAIMGATE-WIRING-01 (Opus 5.5, activation 152c9255)

Inputs: the question [00](00-question.md) and three blind seats: Sol 6.0 [04-seat-sol](04-seat-sol.md), Astra 6 [04-seat-astra](04-seat-astra.md) and Opus 5.5 [04-seat-opus](04-seat-opus.md). All three ran read-only at `092ac6be` against WIP `origin/feat/2026-09-24-claimgate-v2@3cd00c73` and finished at ≈04:37–04:41 PDT 09-25. This synthesis is argument for the cold judge, not authority.

## 0. Terms used below

- **Envelope.** One quiet measurement window's worth of paired blocks for one contrast. CG-1's estimand is the mean over k ≥ 5 *envelopes*, not over blocks: blocks inside one window share that window's conditions and are not independent replicates (ruling 66/20 M1).
- **F_est.** The v2 detection floor. It is computed from k_cal ≥ 5 same-model ABBA *null* envelopes, meaning the same model on both arms, so any difference is instrument noise.
- **Timing acceptance.** The D-079 calibration acceptance (r7, and the 25G83 successor being decided in council ACCEPTANCE-25G83-02). Its members are per-capture clock-anchor bounds, in **seconds**.
- **Golden.** A canonical JSON snapshot of every v1 claim decision and validator outcome, taken before any source change and pinned by its git blob sha, so that a later change to it is visible.

## 1. Unanimous (proposed as ruled)

- **A1 — The timing acceptance cannot produce F_est.** It is the *epoch authority*, not the producer.
  - Its members are `b_fiducial_s` in seconds (`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:20-26,53`; issuer `:1077,:1439`), and it holds no joules and no null contrasts.
  - F_est is minted into a **separate artifact**. It is authenticated by a **code- or registry-pinned** issued digest, never by its own asserted hash; it binds the acceptance id and its sha plus the six-field identity epoch; and it is **recomputed at replay** from its stored block operands. That recomputation is the arithmetic-replay tolerance (`rel_tol 1e-12`), not a science threshold.
  - Missing, unpinned, wrong epoch, wrong unit, or k_cal < 5 each give `not_resolvable`. There is never a fallback to the block floor.
  - The acceptance needs no schema change. The WIP's `estimate_scale_floor` (WIP `detection_floor.py:858`) is kept as the calculator.
- **A2 — v1 stays byte-identical.** `analysis_manifest.py`'s exact-key v1 path is unchanged, and v2 fields refuse there as unknown keys. Historical registries (`ap_spec_draft_front.v2.json`, `ap_spec_native_mtp_front.v2.json`, `slice_2m_ap2.v1.json`) get no edits and stay v1, replay-only. AP-5M v5 is a new prospective registration, never a migration of observed outcomes.
- **A3 — The 19 failures are synthetic fixture receipts.** All supply-map roles are `test_fixture_non_issuing` or pending, so no issued paper number is custody-bound today (Opus Fact 3; Sol; Astra). The reissue is mechanical, but a fresh receipt digest proves only binding to the current validator code, not that historical decisions are preserved. The reissue therefore needs a semantic-equivalence check (W4).
- **A4 — Shared term scopes stay refused**, as already ruled (a typed refusal), pending the independence-wire ruling.

## 2. BLOCKER found by two seats on the WIP as wired

- **B-W2 — Block-level v2 admission.** The WIP estimates v2 over *blocks inside one manifest*: `complete_blocks < 5` at WIP `__init__.py:781,1018`, and `estimate_paired_blocks` is fed block observations. It never calls `aggregate_envelope_observation` (WIP `estimators.py:466`). That is blocks-as-replicates, which ruling 66/20 M1 rejected (Opus, Astra). Today only the blanket refusal at WIP `artifact.py:2294` fences it. Adding the v2 manifest fields and lifting that refusal would admit an invalid claim.
  - Opus Fact 2: a finalized v3 manifest carries one bracket binding and one `window_id` (`analysis_manifest_v3.py:3656-3659`, `:1160-1165`), and `analyze_claims` takes one manifest. So one manifest is one envelope, and a faithful v2 claim needs a **cross-manifest envelope-set layer**.
  - Astra instead places `envelope_registration.envelopes[{envelope_id, window_id, block_ids}]` inside the manifest, with `window_id` bound to authenticated capture evidence. That presumes a manifest can span windows, which Opus's cited code says it cannot.
  - **Proposal:** Opus's envelope-set evaluator (`joulewise/analysis_engine/envelope_set.py`, artifact `joulewise.claim_verdicts_envelope_set.v1`). A single-window v2 contrast gets the non-admitting reason `envelope_member_only`, and the WIP's window-level v2 admission branches in `artifact.py` and `paper_custody.py` are **removed**, not un-fenced. Astra's falsifiers become named tests: five labels on one window cannot make k = 5, and 20 blocks in 4 envelopes are not estimable.

## 3. Splits (the magistrate's proposal and the dissent)

- **S-W1 — Where the F_est null envelopes come from.**
  - Opus: the existing P2-015 detection-floor artifacts' `comparative` component, whose `block_deltas_j` are same-model null contrasts. The contract row already names "the P2-015 calibration artifact" as the floor source (`docs/contracts/analysis_plans.md:29`). Envelope identity is `provenance.launch_lineage.window_id` (`detection_floor.py:2128-2146`). A new mint script and a code-pinned `ISSUED_ESTIMATE_FLOOR_REGISTRY` follow the `ISSUED_ACCEPTANCE_REGISTRY` pattern.
  - Sol and Astra: a new, prospectively registered energy-null calibration, with Astra's `prepare-claim-floor` subcommand and a JSON registry file.
  - **Proposal: Opus's source**, because it reuses the producer the contract already names, conditional on Opus's own M-3 being ruled first: are the D-124 two-edge common-mode `block_deltas_j` "same-model ABBA null contrasts" in CG-1's sense, or a differenced residual? Take Astra's "store block operands, not only means" and Sol's "freeze the sidecar id at registration".
  - **M-1 (Opus): freeze the F_est artifact id before data for every claim shape**, not only CG-2's. Otherwise the calibration windows can be chosen after the claim data are seen. Proposed as ruled; it is stricter than CG-1's letter and consistent with its purpose.
  - **M-2 (Opus):** calibration envelopes of unequal `n_blocks`. Fix `n_cal` at mint, and exclude and list shorter envelopes. This needs a one-line ruling.
- **S-W3 — Mixed v1/v2.**
  - Sol and Astra: per-contrast selectors in a new registry schema, with one Holm family whose m is never split by version.
  - Opus: version-pure registrations, with v2 living only in the new `joulewise.claim_registration.v2` document. `registry.py` is restored to its base bytes, and a closed allowlist `V1_CLAIM_REGISTRY_SHA256S` holds exactly the three current v1 registry digests, so a new registration cannot choose v1 to avoid F_est. Mixing block-level v1 p-values and envelope-level v2 p-values in one Holm family is incoherent.
  - **Proposal: Opus's version-pure design plus the allowlist.** No registered family today mixes versions: AP-5M v5 is all-v2 by construction, and the existing three are all-v1. So Astra's concern (splitting must not change m) cannot fire, while the allowlist closes a real loophole that the per-contrast design leaves open. Dissent recorded (Sol, Astra).
- **S-W4 — Receipt reissue check.**
  - Opus: **PR-0** captures a golden (per-family replay tuples; every checked-in claim-verdict artifact's validation and `evaluate_claim` output; manifest and registry validator outcomes; the 09-19 epoch replays), pinned by blob sha before any source change. Then a hash-only repin via a new script that shares one receipt builder with the test, plus `test_supply_map_repin_is_hash_only` and `test_claimgate_v1_replay_golden_unchanged`.
  - Astra: a semantic-equivalence check with a **deliberate one-number mutation** that must fail after the repin. It also found that `tests/fixtures/paper_custody/repin.py:24` overwrites `pending_roles` with one entry while the map has two, and that the receipt source census must be extended to the new modules (`paper_custody.py:731`).
  - Sol: a snapshot comparison plus a byte-identical diff of number-bearing files.
  - **Proposal: all three combined.** PR-0 golden (Opus), the mutation test (Astra), the narrowed `repin.py` that preserves `pending_roles` (Astra), and the census extension when v2 artifacts become custody-issued (Opus M-8, Astra step 6).
- **S-PR — PR shape.** CG-4 rules "one full-tier PR, components versioned together" (`91-claimgate-final-texts-v2.md:9`); Sol and Astra follow it literally. Opus proposes PR-0 through PR-3, and would fold them if the text is read literally. **Proposal:** PR-0, the golden capture (quick tier; no source change; a precondition, not a claim-gate component), then **one** CG-4 PR containing W1–W4 in dependency order, with the hash-only repin as its last commit. v2 admission stays structurally unreachable until an F_est artifact is pinned by a later data-side PR.

## 4. New science questions surfaced (not wiring; for the judge to route)

- **Q-B1 (Opus B-1): no J/correct null producer exists.** Floor observations carry `metric_value_j` only (`detection_floor.py:2105-2121`), and no calibration records correctness. CG-4(f) makes J/correct AP-5M v5's primary estimand, so that primary cannot be admitted until either (a) a graded-workload null calibration with a J/correct producer is ruled, or (b) AP-5M v5 registers J. Dividing J by mean correct count would be new science. Astra independently flagged "missing scored denominator ⇒ not_resolvable" and "a unit string is not an implementation".
  - This affects the **headline** (difficulty-axis energy per correct answer), so it goes to the four-model council (D-184), not to a wiring seat.
  - **Proposal:** the judge rules whether (a) or (b) must be decided before the CG-4 PR merges, or whether the PR can land with J/correct refusing `not_resolvable`. The magistrate's proposal is the latter: the refusal is fail-closed, and the science choice goes to the council next.
- **Q-M3 (Opus M-3):** whether the D-124 comparative estimate is a null contrast in CG-1's sense. It gates S-W1.
- **Magnitude (Opus M-5, Astra step 8).** The WIP never evaluates `"magnitude"` (WIP `__init__.py:1402`), so a registered magnitude contrast silently becomes exploratory. **Proposal:** refuse `claim_shape_unimplemented` at registration until the shifted-null path is built (Opus), rather than building it now (Astra), because no registered contrast needs it.

## 5. Proposed order

1. PR-0, the golden.
2. One CG-4 PR:
   - the kept WIP components from `0d2b4497` (D-083/D-102 addenda, analysis-plans row, `estimate_scale_floor`, claims v2 codes, CG-3, simulation 94);
   - W2: the manifest-v3 all-or-none v2 group, `claim_registration.v2`, `envelope_member_only`, the envelope-set evaluator, and removal of the block-level admission;
   - W3: the `registry.py` revert and the allowlist;
   - W1: the F_est artifact modules and the empty pin registry;
   - W4: the census extension, and the repin last.
3. Data-side: the 25G83 acceptance is issued, then at least five floor-calibrated 25G83 windows, then the F_est mint, then a pin PR, then the AP-5M v5 registration frozen with the pin named, then claim windows, then the envelope-set claim.

## 6. Plain summary for Ed (≤ 6 lines)

1. The new claim rule needs a noise floor measured in joules. The calibration we are re-deciding measures clock timing in seconds, so the floor needs its own small, pinned record, re-checked every time it is used.
2. The half-built code counted measurement blocks inside one window as if they were independent repeats. Two reviewers caught this, and it would have overstated confidence. The fix counts whole windows, as ruled.
3. The paper's planned "energy per correct answer" measure has no noise-floor source yet. That is a science question, and it goes back to the council.
4. Nothing already in the paper changes. A snapshot taken before any code change proves it.
