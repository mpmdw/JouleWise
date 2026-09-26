# BFG-S consult: magistrate synthesis (Opus 5.5, activation 6bec2aa6) — the proposed decisions a cold gate rules on

**Inputs.**
- Four blind seats answered the charge [00](00-charge.md): Sol 6.0 xhigh [10](10-sol.md), Astra 6 high [11](11-astra.md), Opus 5.5 [12](12-opus.md) and Fable 5.1 [13](13-fable.md).
- Scout packet: `../../2026-09-26-activation-8e43cfa7/20-bfgs/11-scout-report-relaunch-6bec2aa6.md`.
- Ruled authority: ex-01 §5.3–5.6, ex-02 §3.7/§4.11, ex-03 §8 F-1, ex-04 (the same directory).

**Status.** This is a proposal. Nothing here binds until a cold Fable gate, paired with an Opus contract refuter, rules on it. Where I depart from a majority, the reason is given.

## Unanimous (4/4): proposed as ruled text

- **D1 (Q1) Explicit phases.** The observation `phase` enumeration gains `quiet_pre`, `quiet_post`, `bundle_pre` and `bundle_post`. The v1 field set does not change. `observe()` validates `phase` against the full enumeration (Opus X11) and rejects unknown values.
  - `session_id` is the collector's session uuid for quiet envelopes, and the bundle's `metadata.json.run_id` for bundles.
  - Each reader requires its exact pair.
- **D3 (Q3) The bracket unit is the 600 s envelope only; there is no per-round probe.**
  - The **pre** read sits in `collect` after `session` is built and before `envelope_cpu_start = cpu_total()` (`:1065/1066`) and `start = clock.stamp()` (`:1067`). It is stored in `session["battery_float"]["pre"]` before the first `session.json` write (`:1087`).
  - The **post** read sits in the existing `finally` block, after `end_stamp` and `whole_envelope_observer_cpu_s` (`:1163–1164`), and before the final `session.json` write (`:1208`).
  - Raw bytes go to `raw/battery_float.{pre,post}.ioreg`. The collector's row `raw.sha256` map then digests them as a second per-row custody record. This is required and tested, not accidental (Opus 11, Fable 4).
  - The collector's `clock` monotonic source is passed to `observe`.
- **D4 (Q4) QPE-01 fails closed at the summary level.** Any quiet envelope whose authenticated pair is not `pass`, including `evidence_missing`, makes `summarize`/`pilot_summary` refuse the pilot's claim, with energy blanked (the replay precedent). The frozen exclusion list and the `69321c…` registration digest do not change.
  - This is not a silent change to the frozen protocol. It adds a monotone refusal that can only remove a claim, never admit or alter a number. It is driven by instrument state only, under Ed's binding #421.
  - A QPE v4 registration that names a battery exclusion is queued as a separate cold-gate item, not part of BFG-S (Fable).
- **D6 (Q6) Historical bundles.** A **fixed, content-pinned historical set** is keyed by `complete_bundle_sha256`: a committed constant or digest-pinned set file, closed at the BFG-S merge. It is exempt and reported as `unobserved_historical`. Every other bundle must carry an authenticated `pass` pair, or `BundleReader.metadata()` raises. The boundary is never inferred from any writable flag.
- **D8 (Q8) `calibration_bracketing`.** The gate authenticates at the loader (`_load_calibration_candidate_unbounded` `:1542`) before physics or any B access. The evaluator (`evaluate_calibration_bracket` `:1965`) re-checks. The seats split on whether the evaluator gets a carried proof or re-authenticates from bytes; I propose **re-authenticate from bytes** (Opus), because a carried proof is a second trust object. Historical and genesis candidates use the same content-pinned set as D6.
- **D10 (Q10) The WALL-METER-GAIN-01 bar remains.** Float is necessary, not sufficient, for a wall-meter energy claim.
  - The reason in numbers (Fable): 200 mA × ≈12.9 V ≈ 2.6 W of permitted battery exchange. Over a 480 s interior that is ≈1.2 kJ.
  - Two point readings neither integrate battery energy nor see an excursion between them.

## Majority, with the dissent answered

- **D2 (Q2) Custody helper, 4/4 in shape, differing in details.**
  - Add new functions to `joulewise/battery_float.py`:
    - `authenticate_pair(record, raw_root, phases, identity) → PairVerdict`, with verdicts `pass`, `confounded`, `evidence_missing` and `custody_failure`;
    - the thin wrappers `authenticate_quiet_session`, `authenticate_bundle` and `authenticate_capture`.
  - A mismatch between raw bytes and a recorded digest is `CustodyFailure`. It refuses the consumer and is never a quiet exclusion (ex-02 digest-recorded custody).
  - There is no committed verdict file for non-derivation windows.
  - **No existing derivation function changes** (Opus Q12.3): `parse`, `_structure`, `_recorded_values`, `validate_window`, `predates_battery_float`, `authenticate_committed_verdict` and `load_committed_verdict`. The only exception is the separately ruled M-1 edit to `load_committed_verdict` (lane A309). A byte or AST pin test guards these functions until the §4.11 amendment. The reason: the Revision-5 issuer recomputes with main's code and refuses on disagreement, so touching them could strand the epoch.
- **D3a (Q3, failed pre read): record and continue (Fable), against stop-the-night (Opus, Astra, Sol).**
  - Why continue: ex-01 §5.3 item 6 states the ruled writer rule, "a failing or erroring pre- or post-observation is recorded and the writer continues; no new writer exit path". A new collector exit would be booked under the frozen `collect_error` exclusion, which records a battery confound under the wrong frozen reason. That would be a false record.
  - The stop-the-night argument saves machine time only; it does not change which numbers are true. D4 already makes the whole pilot refuse.
  - The executor may log a diagnostic, but it decides nothing.
  - An early-stop optimisation, if wanted, is a later ruled change.
- **D5 (Q5) Controller.**
  - The **pre** read comes before `_stage_idle_baseline` (`:869/870`). The **post** read comes after `_stage_idle_drift_sentinel` (`:873/874`), and a failure or interrupt path also attempts a salvage post read. Every bundle that carries a pre read carries a post attempt. Failures finalize with a non-pass pair; failure-bundle finalization is preserved.
  - Applicability comes from the re-validated typed config's telemetry adapter. MOCK is `not_applicable`. A non-Mac target is `evidence_missing` until a platform predicate is registered.
- **D7 (Q7) The scored reducer takes a frozen `joulewise.scored_battery_evidence.v1`.** It is a tuple of `PairVerdict`s produced by `authenticate_bundle`, keyed `(block_id, attempt)` and bound to `complete_bundle_sha256`. It covers live and superseded windows. Missing, duplicate, unbound or non-pass entries refuse the whole reduction before scoring. The producer is the harvest step that pins the bundles (see D12.4).
- **D9 (Q9) Transaction packs (Sol and Astra, over Opus and Fable, settled by code).**
  - `joulewise/arm_readiness.py:79` `_RULED_V5_PREDECESSOR_PACK_IDS` already binds each `_v5` successor to its Qwen2.5 `_v3` predecessor, and `scripts/author_arm_readiness_evidence.py:76` consumes that map. So the Opus and Fable "`_v5` unfreezable" concern is **refuted by executed code** (magistrate `grep`, this activation).
  - The mapping:
    - `d117_floor_qwen3-1p7b_v5` ← `d117_floor_qwen25_1p5b_v3`
    - `d117_floor_qwen3-8b_v5` ← `d117_floor_qwen25_7b_v3`
    - `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` ← `d117_contrast_qwen25_1p5b_vs_7b_v3`
  - The existing `d117_contrast_v5` directory is a parameterised generator (Sol), not the pack id.
  - All nine Qwen2.5 packs are retired from future *transaction* arms by record. Their bytes and receipts are untouched. The `_v3` bytes stay the authenticated predecessors, and `d117_floor_qwen25_1p5b_v3/calibration_plan.json` stays the W1-pinned plan.
  - **Open for the gate (Fable, item 2):** if a Qwen2.5 transaction window is ever wanted again, it needs a `_v4` successor whose `calibration_plan.json` is byte-identical to `_v3`'s. No such window is planned, so no `_v4` is authored now.
- **D11 (Q11) PR split.**
  - **S1:** bundle/controller/reader/bracketing/scored-reducer code plus F-1 (this moves the readiness pins).
  - **S2:** the QPE collector/summary path (no pack pins). S1 and S2 may run in parallel in separate worktrees, since their write scopes are disjoint except for `battery_float.py`, where new helpers land in S1 first and S2 rebases.
  - **S3:** authoring and freezing the three `_v5` packs, from the S1+S2 merged head.
  - **S4:** the ex-02 §4.11 predicate/text/pin amendment, only after the Revision 5 epoch issues or stops.
  - Until S2 merges, a **mechanical arm fence** (Opus Q12.5) makes `evidence_night.check` refuse a `quiet_predicate_evidence` arm: a NightKind field `battery_brackets` is `True` for `calibration` and `False` for QPE, and S2 flips it. This lands in S1, or as a tiny S0 if S1 slips.

## New truth obligations from Q12, proposed for the BFG-S texts

1. **F-1 must add a check, not only remove one** (Opus, MATERIAL). Deleting the `"battery_float" in evidence` refusal arm at `controller.py:439–447` lets a charging pre-calibration capture attach silently. In the same PR, `_load_instrument_calibration_attachment` calls `authenticate_capture` before physics or B, with no historical exemption: attachments are fresh at run time.
2. **The window-level verdict for transaction windows** (Opus, MATERIAL). The consumer that builds the claim set (`whole_window` / `analysis_engine.inputs`) authenticates **every finalized member bundle, FAILED included**, and refuses the window on any non-pass. Without this, a charging rep is dropped as `FAILED/unknown_error` while its neighbours are kept, which is the per-slot exclusion A-R5b rejected.
3. **Direct `metadata.json` readers** (Opus X9, Sol Q12). `whole_window`, `floor_extraction` and `analysis_engine.inputs` bypass `BundleReader.metadata()`. A sweep test proves that every path that can emit a claim-bearing number passes the gate. It reuses the CONSUMER-DRIFT AST-guard seam (ex-04).
4. **A write-time custody anchor for bundles** (Opus X7). The transaction harvest pins every member's `complete_bundle_sha256` in a commit before any energy is read, the non-derivation analogue of the ex-02 head-pin commit. That pin is D7's producer.
5. **Scored-packer ceiling decisions on a confounded window** (Fable 7). A ceiling violation decided from a confounded window's `gross_j` can void a block before any battery check. Proposed: the registration states that a ceiling violation on a non-pass window is `voided`, not `terminal`. This needs a ruling before the scored campaign arms; it is outside S1–S3.
6. **Pin the one-sided staleness** (Fable 6). S1/S2 tests pin today's `update_age_s > 180` one-sided behaviour, so S4's change is visibly RED.
7. **Hermeticity budget** (Fable 5). Every controller test that runs to `reduce` on a battery-less host needs the injected runner; this is the BFG-D round-8 lesson.
8. **Historical claim numbers** (Opus Q12.6). This is germane to verity, so it is mandatory under #421 §2. Every number already in the paper, and the two QPE pilot nights, were measured with battery state unobserved.
   - Physical context: the charge cap was 80 % until Ed raised it on 2026-09-25 (issue #420), so the battery was probably held at the cap rather than charging. That is a presumption, not evidence.
   - Proposed: a separate lane, HISTORICAL-BATTERY-STATE-01, audits each claim-bearing capture interval against the retained `pmset -g log` charge history where it exists. Numbers with no retained evidence are disclosed as "battery state unobserved (pre-directive)". Numbers with evidence of charging are re-measured or withdrawn.
   - D6 makes `unobserved_historical` visible in every window-level output.
   - This is claim policy, so the cold gate rules the lane's shape and Ed gets the after-the-fact summary.

## What the cold gate is asked to rule

- **R1.** Accept, amend or reject D1–D11 and obligations 1–8 as the final texts for the S1/S2/S3 seat briefs, including write scopes and test obligations. Make particular findings on D3a (continue versus stop) and D8 (re-authenticate versus carried proof).
- **R2.** The S1/S2 WRITE_SCOPEs, starting from the scout's §Delegation list plus the new obligation paths: `joulewise/whole_window.py`, `joulewise/floor_extraction.py`, `joulewise/analysis_engine/inputs.py` (if claim-bearing), `joulewise/night_kinds.py` (the fence) and new test modules. `reduce.py`, `bundle.py`, the estimator paths and the paper-pinned scripts are **excluded**.
- **R3.** Whether obligation 5 (ceiling on confounded windows) and obligation 8 (historical numbers) are BFG-S blockers or separate lanes. My recommendation: separate lanes, each blocking what it names — the scored campaign's arm and the paper's claim renderers respectively.
