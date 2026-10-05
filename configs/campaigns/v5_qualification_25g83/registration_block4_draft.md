# Registration V5-QUAL-25G83-B4: arm-only controls and real-GAMMA qualification (measurement block 4)

Status: **DRAFT, 2026-10-05. UNSEALED; authorizes no arm and discharges no live gate.** Rewritten under lead ruling 76, following consult brief 75 and both recorded answers in `docs/process_traces/2026-10-04-desk-day-v5/`. Ruling 76 is prospective: D-176 decision 4 stands until this registration's cold Fable judge and independent Opus refuter seal the erratum; Ed may veto (§14).

Every FILL is an unresolved binding, never a default. Preparation/review is `[AGENT]`; execution is lead-controlled `[QUIET-MAC]` after all seats exit. Required implementation interfaces come from `feat/2026-10-05-v5-qualification-code`; unresolved argv/path interfaces stay named CLI FILLs. Companion records: `42-block4-required-code.md` and `47-block4-terminal-refresh-coverage.md` in the trace directory above. These documents perform no implementation, install or capture.

## 1. Purpose and governing authority

Qualify unattended pack-bound launch and the real `_v5` launch-to-claim prefix before claim custody opens. D-176's purpose-bound GO, one-use consumption and on-disk step-6 confirmation remain; its decision-4 qualification night becomes `s1`. D-162/D-167 still require real-pack G2-b, its binding/verdict and exact refusing finalizer. G2-a discharged none of these gates.

Sequence: **G10 physical control (Ed) → `a1` (arm-only, expires) → `a2` (arm-only, expires) → `s1` (real GAMMA, two verdicts)**; recovery is only §7's fresh `s1` `recover_no_science` or at most one `s2`. `a1`, `a2` and initial `s1` use one reviewed head **H**, the intended ALPHA/BETA/GAMMA claim code head, containing producer fixes #472/#473/#476, stop #474, A6 #475, issued pin/packs #477 and the integrated ruling-76 implementation. Full SHA/file pins, not branch or PR labels, bind execution (§12).

Authority: `docs/decision_log.md` D-078, D-162, D-166/D-167, D-171, D-176; `docs/contracts/pack_night_go_receipt.md`; `docs/process/v5-l10-rehearsal-phase.md`; the G2 runsheet; queue A160, A161, Q3/Q4, A119 L10-A, Q110 and A6. Block-3 §§3–12 and its seal record are shape precedents. Directives #416/#421 retain their gates. Ruling 76 changes only the clauses recorded here and in §14.

## 2. Occurrences and launch authority

| Occurrence | Frozen boundary | Required hand-back |
|---|---|---|
| `a1` | Throwaway real-GAMMA ARM context; fresh T-0, `G2B_SHAKEDOWN`, `claim_eligible=false`, `permitted_blocks=1`. Arm once; never launch/consume, create a bundle or write `chain.started`. | Authentic PASS/GO ARM, followed by canonical `readiness_record_expired`; expiry/no-launch proof before `a2`'s T-0. |
| `a2` | Same arm-only recipe, separate identity, authorization, custody and fresh T-0, after `a1`'s expiry check. | Same expiry/absence proof before `s1`'s fresh T-0/clean dwell; supplies Q110's third receipt bundle. |
| `s1` | `TRANSACTION_PACK`, `G2B_SHAKEDOWN`, `claim_eligible=false`, `permitted_blocks=1`; frozen real pack `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`. One authenticated consuming launch, authentic first frozen stage, exactly one A/B/B/A science block and governed post-science path. | Separate structural G2-b and decision-4 qualification verdicts, authenticated binding before the authoritative verdict row, desk PASS and folded L10-A exact refusal. |

No receipt, capability, namespace or T-0 evidence is reused. Controls are not consuming recovery allowances; their waits derive from their own receipts/boots, never guessed calendar delays. `s1` arms only after both control records pass and G10 is authenticated. For Q110's third bundle, a NULL `s1` attempt's ARM receipt may substitute if one occurs (ruling 76 decision 7).

Use `scripts/run_night.py run --plan ...` for `s1`, never `rehearse`. There is no separate rehearsal pack/profile/ledger/clone or live G6/G7 control. The integration seat fixes the ARM-only producer/checker and observation/harvest interfaces before seal (§8).

## 3. Operating conditions and fixed inputs

1. **Machine:** M3 Max, Mac15,9, macOS 25G83; AC, battery float, `ac_high_power`, powermetrics interval 100 ms. No agent/operator action at T-0 or during a consuming chain. Driver/governed stdin is `/dev/null`; retain first and repeated 30 s census argv/results; all seats exit by t0 − 8 min. Harvest agents return only after completion/courier/dead-man boundaries are safe and exit before the next occurrence.
2. **Acceptance:** `d079_calibration_acceptance_v2_n24_25g83_r2`, `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, SHA-256 `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`. Both brackets use its freshness, screen and drift rules; no older acceptance substitution.
3. **Workload:** `mlx-community/Qwen3-1.7B-4bit` and `mlx-community/Qwen3-8B-4bit`, revisions/tokenizer/file hashes from `configs/model_panels/qwen3_4bit.json` at H. Frozen order gives small/large/large/small; `FILL[S1-ROSTER]` binds exact first-stage IDs. Prompt bytes, issued prefill length, thinking-off/greedy decode, forced 512 output tokens, prompt-0 assignment and family m=2 retain D-166 semantics. No subset pack or shortened workload.
4. **Issued bundle:** `configs/campaigns/d117_contrast_v5/prefill_pin/` on supplied branch `origin/desk/2026-10-04-v5-pin-and-packs` (PR #477, merging). Files: `prefill-prompt-pin.json` SHA-256 `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`; `selection.json` SHA-256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`; `prefill-prompt-ladder.json` SHA-256 `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885`. Authenticate references/issued length from these bytes at H; never rerun selection. No selected coordinate or measured value is printed here.
5. **Policy:** `configs/campaign_policies/quiet_mac_p2_production.json`, `FILL[PRODUCTION-POLICY-SHA256]`; keep admission thresholds, retry count, dwell and abort rules. Do not import block-3's 300 s backoff. Freeze NEG-8 bound corpus, start/midpoint/end references and settles in `FILL[S1-COMPLETE-AUXILIARY-ROSTER]`; these are separate from four science members.
6. **Ledger:** physical ledger authenticates with `verify_custody=True` against the committed pin; retain all referenced bytes. Draft pin: sequence 402, head digest `3ce1676c530452df301e8f09d97905487b06b8ed8887d7c7a728a08fd5310c08`; seed: block-3 SELECT re-harvest `derived/terminal-ledger.jsonl`, SHA-256 `6ee89e5a1b83c88d865a65cca71177d19a4b23b47d6af2979f92a6840857530e`. Actual H source/custody is `FILL[PRODUCTION-LEDGER-SEED]`. The live seed differs from acceptance cutoff 376; brackets use that cutoff. `s1` ARM/GO/consumption/runs are in shakedown custody isolated from claim roots, with production-ledger changes governed by §12.
7. **Battery #421:** every occurrence retains fresh authenticated raw ioreg and shared `joulewise/battery_float.py` observations at arm, immediately before publication/install and at T-0. PASS: ExternalConnected=Yes, IsCharging=No, signed InstantAmperage within ±200 mA, UpdateTime age ≤180 s; missing/stale/malformed cannot pass. Every bracket/science/obligated auxiliary capture has appropriate pre/post raw pairs outside anchor stamps and sampler lifetime, with identity/digests/replay authentication. Apply member consumption to every attempt, including failed/superseded attempts. Controls launch nothing, so have no capture-pair obligation. `FILL[BATTERY-EVIDENCE-MAP]` binds paths. Custody failure is REFUSED; authentic non-pass cannot qualify and has no tooling allowance (§7). Endpoint pairs cannot detect excursions wholly between observations; retain this limitation.

Changed operating conditions after seal require a new rule (§11).

## 4. Window, deadlines and prospective sizing

**Controls:** author fresh T-0, ARM once, retain PASS/GO and exact expiry; never invoke/install a consuming launcher. After all validity horizons end, canonical verification must refuse `readiness_record_expired`. Prove no consumption, chain start, sampler or bundles. `FILL[ARM-CONTROL-DEADLINE-RECIPE]` bounds expiry/check/courier; complete `a1` before `a2`, and `a2` before `s1` T-0/dwell.

**`s1`:** one launch; settled OFF receipt and 600 s clean dwell; pre settle/bracket with acceptance-derived screen; NEG-8 bound work/start references; authentic first before-midpoint science stage with `scripts/run_campaign.py --max-blocks 1` (#474); midpoint/end references; post bracket in the same session; finalization and ratified physical-ahead STOP. No after-midpoint science, fifth science member, manual SIGINT/polling kill or second launch. Bind `FILL[ONE-BLOCK-STOP-RC-AND-RECORD]` separately from `FILL[S1-SUCCESSFUL-CHAIN-RC]`; historical rc 130 is not adopted. Reference/bound stages must not receive the science limit.

At STOP retain the exact terminal candidate; do not advance a tracked pin, emit launch completion, write bracket binding/verdict or finalize analysis inside the night chain. Outside the quiet window, complete reviewed refresh/restaging, actual backups/close-out/OFF stand-down and qualification assembly. STOP alone cannot prove G9 COMPLETE. §12/record 47 govern refresh coverage before a later arm.

**Sizing method is settled:** a source-bound allowance adapter uses block-3 archives (diagnostic reading permitted after block 3 by its §10) and committed GAMMA configs at issued length L. Every allowance cites `{path, sha256, pointer}`. No `s1` byte is used. Estimates E_small(L), E_large(L) include load, warmup, prefill, forced decode, cooldown, idle admission and bounded policy retry. Separate fixed settles, calibration, reference/bound work, author/verify/consume overhead, custody, shutdown and backups; count each once.

- `E_ABBA(L) = 2*E_small(L) + 2*E_large(L)`; estimates/source bindings: `FILL[GAMMA-MEMBER-ESTIMATES-AND-SOURCES]`.
- `NIGHT_PROGRAMMED_SPAN_S_s1 = ceil(T_pack_t0 + T_fixed_settles + T_pre_post_calibration + T_bound_and_references + E_ABBA(L) + T_stage_custody + T_terminal_shutdown)`; `FILL[S1-COMPONENT-SPAN]` inventories every auxiliary/overhead allowance and its boundary.
- `WINDOW_MAX_S_s1 = 60*ceil((NIGHT_PROGRAMMED_SPAN_S_s1 + 2700)/60)`; `FILL[S1-WINDOW-MAX-S]`. Clean dwell cap 2700 s is added once, outside programmed span. Writer emits span literals and enforces latest chain start ≤ `t0 + WINDOW_MAX_S − NIGHT_PROGRAMMED_SPAN_S`. Running-chain expiry is RECOVER, never partial PASS. Completion/courier/dead-man bounds: `FILL[PER-OCCURRENCE-SHUTDOWN-CAPS]`.

Before seal, size the longest continuous sampler stream, including rejected idle/retry, guards, warmup and measured work; also check bracket/auxiliary streams. `FILL[LONGEST-STREAM-SIZING]` binds T_stream, diagnostic anchor half-width h, prospective drift bound rho and source hashes. Require `h + rho*T_stream ≤ 0.005 s` under the implementation's exact effective-bound convention; inspect it to avoid double-counting span. This is a design estimate, not live validation or a relaxed 5 ms admission. Actual obligated member anchors must be `bounded` (§6).

## 5. Network time and Ed's G10 control

Network time stays **OFF across/between occurrences and after restore**. Each control/consuming attempt has a fresh write-once authenticated OFF receipt on its own boot, admitted by the shared reader: setter exit 0 and normalized `setUsingNetworkTime: Off` or `Network Time is already off`. First capture/author boundary is ≥600 s after the receipt on both clocks. No exact raw-stdout equality or reused receipt. T-0 clock-disable capture/clock-row source authenticate the same state/receipt through G4; they do not authorize ON.

**Ed's physical control precedes `a1`'s T-0, outside every armed/capture span**: reviewed helper `scripts/ed_session/capture_t0_anchor_positive_control.py`, recipe 46, invocation `FILL[G10-CONTROL-CLI]`. This is the sole owner action; lead/automation owns the rest under D-171. The recipe:

1. Machine-authors CLOCK_REALTIME/CLOCK_MONOTONIC_RAW before stamps and real author inputs in separate control custody.
2. Imports the reviewed ON vector from `scripts/capture_t0_step.py::_arm_reference`: `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on`. Retains argv/stdout/stderr/rc/stamps; polls the RAW anchor for >5 ms movement within a bounded deadline (default 120 s, maximum 300 s), with **OFF in `finally`**. No new sudoers grant, arbitrary clock-setting or modified normal SNTP reference probe.
3. Demonstrates absolute movement **>5,000,000 ns** and invokes the real T-0 author on that changed sequence: exactly `evidence_author_t0_clock_attestation_underivable`, no PASS namespace. A resync with ≤5 ms movement is not PASS; preserve failure and route to the lead, never manufacture evidence.
4. Emits the exact eight-key control: `schema_version`, `performed_by="Ed"`, `outside_t0_sequence=true`, `network_time_reenabled=true`, `forced_resync=true`, `anchor_before_ns`, `anchor_after_ns`, `author_refusal_reason_code`. Retains raw transcripts/inputs, boot/digests and refusal/absence proof in `FILL[G10-CONTROL-RECORD]`/`FILL[G10-EVIDENCE-IDENTITY]`.
5. Archives OFF before block entry; each later occurrence obtains its own OFF receipt/dwell. No ON/resync between occurrences or in G9 restore.

Software falsifiers additionally replay real author/arm at 5 ms ±1 ns with exact refusal codes and no above-bound PASS namespace. Synthetic boundaries never replace Ed's physical evidence. Missing/unsuccessful G10 prevents qualification; the physical recipe is settled, its actual evidence is not yet asserted.

## 6. Validity and proof predicates

**Decision-4 qualification on `s1`'s own observed evidence:** use existing `joulewise/t0_rehearsal.py` evaluators, with only ruling-76 adaptations. `FILL[S1-QUALIFICATION-PRODUCER-MAP]` binds record paths/schemas/digests/producers; retain original absolute replay availability.

| Gate | Required predicate/evidence |
|---|---|
| G1 | Each governed process has a registered expected outcome: agent census `pgrep` exit exactly 1 with empty stdout; every other process exit 0. Observed fd 0 `/dev/null`, no timeout, `sequence_completed`; retain pid/argv/exit custody. Exhaustive exec-descendant prompt/EOF tracing is not required: abnormal exit/incomplete chain is caught by G1/G9/structural verdict. |
| G2 | Exact fifteen ARM_ONLY receipts/captures, canonical source/receipt census, zero operator-attestation facts, machine PROBE clock fact, hashes/membership matching GO. |
| G3 | Raw `HIDIdleTime` witness covers actual RAW-clock T-0 span; no typed idle assertion. |
| G4 | Authentic initial/repeat fixed-roster reference bytes, clock-disable/settled OFF evidence and existing skew/span/duration/anchor recomputation: 600–3600 s T-0 span, 30 s repeat-reference-batch cap, 5 ms RAW bound. |
| G5 | Current 26-key pack GO, ARM and one v3 consumption; authenticated plan/authorization/confirmation/census. Replay recorded boot/instant and C1–C5, never retired D149 schema/current-time expiry in place of historical replay. |
| G6/G7 | `NOT_APPLICABLE`, basis `retired_by_ruling_76`, **never PASS**. No live/desk rehearsal controls; keep merged G7 regression: fully valid rehearsal receipt refused by class. |
| G8 | Observed agent PID/argv/exit before chain/capture, actual chain/capture boundaries and ongoing zero-agent censuses. No assertion by an agent about its own future exit. |
| G9 | Authenticated ordered COMPLETE launch, capability_consumption, capture, claim_backup, bound_backup, close_out, restore; two independently verified backups of real evidence, zero T-0 actions/interventions, OFF/stand-down restore. Retain actual courier/relaunch/dead-man facts. Stage names do not confer claim eligibility. |
| G10 | §5's separate Ed physical control plus software ±1 ns falsifiers, mapped/authenticated by qualification harvest. |

Observation producers only OBSERVE; their faults cannot abort the chain or change structural G2-b to RECOVER (§7).

**Controls:** genuine PASS/GO ARM followed by `readiness_record_expired`, no launcher/consumption/sampler/bundle/start, ordered expiries before next T-0, authentic Q110/#421/OFF inputs. Inactivity alone cannot pass.

**Structural `s1`:** all four science bundles succeeded, strictly valid by re-reduction from raw bytes, exact first-block identities/order, `uncertainty_evidence.clock_anchor.status=bounded`. No fifth/partial science member, second occurrence or leftover campaign lock. Enumerated auxiliary/bound/reference captures face their own validation/battery obligations; four science members is not four total bundles. Both authenticated bracket endpoints, session enclosure and acceptance-r2 decision pass; `physical_ahead` is not bracket PASS. Build binding before exactly one authoritative passed whole-window row; verdict file is its exact copy. Desk checker passes `NR14-LAYOUT`, has no FAIL, and S11-A4 is exercised PASS or the registered `present_stages=0 assertion_not_exercised` SKIP.

**Folded L10-A:** strict validate once, reduce once into restricted L10 custody, finalize once through the refusing checker against a complete staged scratch copy of the real prefix, never the immutable source. `--output-dir` is **the staging custody root**, the same root as `--custody-root` (ruling 76 L10-A; `joulewise/analysis_manifest_v3.py`), not an `analysis-output` child. Use the corrected §L10-A recipe. Exactly `{analysis_finalization_member_cover_mismatch}` is PASS; success/any additional reason is FAIL. `analysis_finalization_attachment_missing` is STOP plus written ruling, never permission to stage a floor. Source/staging `floors/` exist and are empty before/after; aggregate-floor argument points to an absent artifact. Equal before/after G2-b tree hashes prove no source writes. Record `proof_scope=L10_A_G2B_CONTRACT_PREFIX`; lead ratifies before first claim arm. Later bracket/ledger/floor legs remain L10-C.

## 7. Two verdicts, recovery and END STATE

Mechanical harvests use authenticated immutable archives, never narrative. **Structural G2-b:** archive/authentication/harvest-tool fault → REFUSED; otherwise absent `night/chain.started` → NULL; otherwise §6 plus registered stage-stop/outer-chain rc and non-claim one-use/clock/OFF/battery obligations → PASS; every other started occurrence → RECOVER with immutable named cause/class. Controls instead have separate PASS/FAIL expiry records.

**Qualification:** PASS only when G1/G2/G3/G4/G5/G8/G9 and G10 PASS, with G6/G7 explicitly NOT_APPLICABLE. UNRULED/INCOMPLETE cannot pass. Producer fault → qualification REFUSED or FAIL; it never aborts the chain, changes structural G2-b to RECOVER or spends `s2`. Qualification FAIL with structural PASS goes to the lead: re-run an R3-cured producer on the same bytes where possible; a genuinely failed live gate (agent present, unbounded clock, HID activity) is **END STATE**. Structural PASS alone cannot hand off qualification.

REFUSED repair uses standing R3 and re-harvests identical source bytes into a distinct derived archive, preserving prior records; it is not a science outcome or capture authorization. A changed harvest interpretation does not recollect or spend `s2`.

NULL preserves ARM/refusal/absence proof and attempted window, then may re-arm only after cause removal, with new plan ID, authorization and T-0. **Same refusal code twice consecutively → consult (Sol + Opus), not a third arm.** No same-plan retry, overwritten refusal or hidden automatic re-arm. Failed controls are preserved and follow standing remediation with newly registered identity before any consuming arm.

**`recover_no_science` (ruling 76 decision 6):** a structural RECOVER of an `s1` attempt whose named pack-path or launch tooling cause fired **after `chain.started` and before the first science member's sampler started** is preserved, cured through R3 and re-armed as a fresh `s1` (new plan ID, authorization, T-0), **without consuming the one `s2` allowance**. Authenticate cause ordering and absence of science sampler starts/bytes; retain all auxiliary/other bytes. D-078 has no science to pool/top up. This stays RECOVER, never NULL merely because powermetrics is absent. Same refusal twice still goes to consult; §12 still governs any cure head.

**At most one `s2`:** only for `s1` RECOVER from a named tooling defect removed through reviewed R3, code-agrees-with-text and §12. Fresh authorization/roots/T-0 and complete one-block roster; preserve failed `s1` unchanged. Never pool, replace members, top up or rerun a stage (D-078). A same-byte producer/harvest repair is not another occurrence.

Instrument/physics RECOVER has no `s2`: clock, acceptance/bracket physics, authentic battery non-pass, machine/environment failure in the started chain or equivalent physical cause. Retain the systematic-clock trigger: **at least five members with recorded anchor status (excluding `not recorded`), and more than half not `bounded`**; use actual science/reference/bound records and report denominator. Do not lower five for four science members. Missing/invalid science anchors already bar PASS; a tooling explanation does not override this prospective trigger.

**END STATE:** stop the block; no transaction opens or further consuming occurrence arms under this registration; email Ed; next step is a **design record naming the cause, with consult + cold gate**. Applies to genuine live qualification failures, instrument/physics RECOVER, `s1` RECOVER without an eligible removed tooling cause, a code-head conflict requiring new design, or `s2` RECOVER. No qualification fallback or indefinite rearm loop. Notices/terminal emails belong to lead/driver; this draft sends none.

## 8. Producers, harvest outputs and Q110

Seal the integration seat's exact interfaces and output schemas/locations; listed roles grant no implementation write authority.

| Role / unresolved interface | Required output |
|---|---|
| `FILL[PLAN-WRITER-CLI]` | Canonical `s1`/allowed `s2` plans via `NightPlan.from_mapping` and `write_night_plan`; bind plan/pack/chain/authorization/confirmation. |
| `FILL[ARM-ONLY-CLI]`, `FILL[ARM-ABORT-CHECK-CLI]` | Staged `a1`/`a2` ARM-only contexts and authenticated `arm-abort-control.json` per custody: receipts/digests, exact expiry refusal, absence/order facts. |
| `FILL[QUALIFICATION-OBSERVE-CLI]`, `FILL[QUALIFICATION-HARVEST-CLI]` | `s1` process/HID/lineage/lifecycle/bundle assembly and separate structural qualification verdict; existing evaluators, explicit G6/G7 retirement, G10 provenance, checksum census/cause codes. |
| `FILL[G2B-HARVEST-CLI]` | `<s1-harvest>/harvest.json` (allowed `s2` analog), authentic bracket/whole-window/desk/L10 proofs/tree hashes, restricted re-reductions and `L10_A_G2B_CONTRACT_PREFIX` record. Re-harvest authenticates an existing verdict row instead of appending another. |
| `FILL[SIZING-ADAPTER-CLI]` | Source-bound §4 allowances and deadline/clock sidecars, with `{path, sha256, pointer}` for each allowance. |
| `FILL[TERMINAL-REFRESH-CLI]` | Guarded pin advance, readiness/freeze refresh/restaging and exact §12/record-47 changed-path/content proof. |
| `FILL[Q110-RECORD-CLI]` | `FILL[Q110-RECORD-PATH]`: ≥3 real bundles from `a1`, `a2`, `s1` (NULL-attempt substitution per §2); receipt IDs/paths/hashes/boots and unchanged clock-fact batch-completion source mapping. |

Q110 formula is unchanged: `validity_origin = valid_until_monotonic_ns − _validity_horizon_ns(kind)`; `elapsed = validity_origin − t_batch_finished`, where `t_batch_finished` is the existing `clock.correct_and_prior_state` value's repeat-reference-batch-finished monotonic stamp, not a new receipt key. Retain each elapsed and minimum margin below 600 s in custody. Q110 is a limitation through G2-b, not a new launch gate: close with ≥3 real bundles and **all elapsed <600 s**, or cold re-rule **before ALPHA**. Insufficient margin/live liveness refusal goes to that gate; no relaxation here.

Public outputs allow only paths/hashes, identity/roster/counts, status/reason codes and required control/liveness facts. No released energy comparison/statistic/dominance/floor/mint/claim. A160 closes on `s1` qualification harvest PASS, not documentation or structural PASS alone; §14's kernel changes are lead-owned after seal.

## 9. Scope and downstream handoff

Both `s1` verdicts PASS permits handoff to remaining claim prerequisites, not transaction opening. This block covers G10, expiring controls, real-GAMMA one-block G2-b/qualification, folded L10-A and Q110 evidence.

Outside: ALPHA/BETA/GAMMA claim registration/analysis plan; **#416 pre-arm triple audit**, at frozen claim head containing #465, finished before first claim window; **outcome-independent environmental diagnostic/disposition of Sol consult §5**, in the claim registration. Prepare these alongside qualification preparation; no agent/audit work during quiet captures. Also outside: ALPHA/BETA floor collection/mint, GAMMA claim collection, L10-B/C, transfer fiducial and scored `_v6`. No non-claim byte becomes claim/floor/mint/replacement evidence. Bind all three `_v5` pack/freeze identities, but only GAMMA launches science here.

Later authenticated `CAMPAIGN_TRANSACTION` authority under D-171 §3/D-176 requires custodied G2-b PASS and all remaining prerequisites. `G2B_SHAKEDOWN` never discharges `V5-TRANSACTION-GO-01`; retain reviewed code/acceptance identity across the claim family (§12).

## 10. Blindness

Until **ALPHA/BETA/GAMMA claim analysis plan seal**, harvest releases structural verdicts only: **no energy, power or per-member duration fields** in stdout/stderr, emails, public JSON/tables or accessible review summaries. Filter tails; hashes/paths and readiness/control/Q110 timing are permissible. Ruling 76 decision 9: for every non-`CAMPAIGN_TRANSACTION` purpose, `scripts/run_night.py` excludes raw chain stdout/stderr from the durable courier record; these logs stay restricted locally because they carry member durations.

Withhold `<s1-harvest>/withheld/s1-reductions.json` and the `s2` analog, with authenticated L10 per-member metrics/source mapping. Detailed reducer output stays under restricted L10/withheld custody. Raw bundles/traces, original summaries/metadata, calibration numeric diagnostics and unfiltered validation/reduction transcripts also stay restricted; no alternate artifact may leak withheld fields. `FILL[BLIND-CUSTODY-MAP]` fixes locations/access. G2-b tree hash comparison brackets L10 work after binding/verdict construction; those registered desk writes never authorize changing collected bytes.

Claim-plan designers/sealers (people or agents) do not open metrics, summaries, raw energy/power traces or member durations beforehand. Automation may strict validate/reduce/evaluate fixed predicates but serializes only structure. Lead names RECOVER using structural admission/bracket/clock/custody facts; necessary restricted numeric access is custodied/disclosed to cold gate and never tunes claim analysis. Release requires sealed plan identity/digest and lead release event, `FILL[CLAIM-PLAN-RELEASE-BINDING]`. Structural verdicts may be read before claim-plan seal; metric release is not an arm prerequisite.

## 11. Code agrees with text

No retroactive change to §§2–10 for armed/completed occurrences. Changed rule/threshold/purpose/roster/inference/recovery/blindness requires prospective cold erratum/design. Code-only agreement fixes follow gated R3, Fable final pass for measurement/qualification code; preserve source/old verdicts and issue distinct derived re-harvest records. REFUSED repairs use identical source bytes. A started physical failure cannot become NULL; unresolved tooling-versus-physics attribution needs a ruling before recovery arm.

## 12. Seal, pinned head and permitted head changes

`FILL[BLOCK4-SEAL-RECORD-PATH]` binds cold Fable judgment/independent Opus refutation, registration SHA-256, exact H/source hashes, real plans/chains, filled controls, sizing and regression evidence. **Records commits cannot conceal code changes; no arm with unresolved pre-seal/pre-arm FILL.**

Pin exact files at H: these three documents; final integration plan/control/observation/harvest/sizing sources and G10 helper; `joulewise/night_plan_writer.py`, `joulewise/night_gate.py`, `scripts/run_night.py`, `scripts/launch_window.py`, `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence_t0.py`, `joulewise/t0_rehearsal.py`, any used evaluator entry point, `scripts/capture_t0_step.py`, `scripts/gen_g2_phase_d.py`, `scripts/run_campaign.py`, `joulewise/controller.py`; calibration capture/ledger/bracket/binding/verdict/battery/OFF readers; strict validator/reducer/scratch finalizer/checker; three `_v5` generator sources/generated trees, identity/readiness sources, freeze receipts/sidecars/historical pinset; panel/policy/pin/acceptance; `configs/production_custody_inventory.json`; launchd templates/installer; executable chain sources `docs/phase_2/window_runbook.md` and `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`. Expand grouped entries with SHA-256s in `FILL[SEALED-FILE-INVENTORY]`; directory-only pins are insufficient.

`a1`, `a2`, initial `s1` arm at exact H. Do not import block-3's broad unrelated-descendant arm permission. Before the first occurrence, records-only seal/arm commits may establish final H only with proof that no pinned executable/generated config/chain source changes; all occurrences use that final H.

Afterwards H′ extensions remain bounded: **(i)** reviewed block ledger-pin advances with exact seed/terminal custody and necessary readiness/freeze refresh; **(ii)** gated code-agrees-with-text R3; **(iii)** records-only `docs/`, `tests/`, RUN_STATE/TASK_QUEUE changes leaving every pinned executable/generated config/chain source unchanged. Every extension has an explicit changed-path/digest map before a later arm; harvest runs at an extension only with matching required source pins/correction.

**Terminal coverage is settled by ruling 76:** H′ = H + terminal ledger pin and re-authored readiness/freeze records is covered by `s1` qualification, because packs pin acceptance cutoff, not live ledger head. Record 47 defines the exact permitted classes, freeze-reference-only plan-tree changes and `git diff --name-only H H′` check against an expanded exact allowlist. Prove unchanged executables/generated workload configs/chain sources and authenticated refreshed bindings; fill `FILL[TERMINAL-REFRESH-CHANGED-PATH-MAP]` with actual evidence before any later arm. New readiness/freeze hashes are reviewed, not called unchanged; no later arm consumes the old freeze. This is a settled coverage rule, not a new open design question.

An R3 recovery extension needs `FILL[RECOVERY-HEAD-EXTENSION-IF-NEEDED]` before a fresh `s1` or allowed `s2`. If it changes an exercised launch/measurement path, H does **not** automatically qualify that head: lead/cold gate must prospectively settle qualification coverage before recovery/claim arm. Any other head difference or operating-condition change requires new seal/design. R3 cannot override frozen-pack immutability, one-head rule or §7 allowances; no extra qualification occurrence is implied.

## 13. Binding register

Fill from authenticated bytes. Seal fixes interfaces, schemas, destinations, source bindings/rosters and output recipes; runtime receipts are fresh and authenticated at their registered stage. Future harvest/release artifacts may be absent at seal only with producer/schema/destination/predicate already fixed.

| Binding | Remaining field / fixed fact | Due |
|---|---|---|
| H, merge/gates, registration hash and cold pair | `FILL[H-FULL-SHA-AND-INTEGRATION-GATES]`; `FILL[REGISTRATION-SHA256-AND-COLD-PAIR]`; seal record §12 | Seal |
| Pin bundle | Exact §3 path/file digests; authenticate merge at H | Seal |
| ALPHA pack/freeze/predecessor | `configs/campaigns/d117_floor_qwen3-1p7b_v5`; `FILL[ALPHA-PACK-DIGEST-AND-FREEZE]`; predecessor `d117_floor_qwen25_1p5b_v3`, initial expected `freeze-0004` | Seal |
| BETA pack/freeze/predecessor | `configs/campaigns/d117_floor_qwen3-8b_v5`; `FILL[BETA-PACK-DIGEST-AND-FREEZE]`; predecessor `d117_floor_qwen25_7b_v3`, initial expected `freeze-0004` | Seal |
| GAMMA pack/freeze/predecessor | `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`; `FILL[GAMMA-PACK-DIGEST-AND-FREEZE]`; predecessor `d117_contrast_qwen25_1p5b_vs_7b_v3`, initial expected `freeze-0004` | Seal |
| Desk/family/history/identity and battery S3/S4 disposition | `FILL[DESK-PROOF-AND-FAMILY-BINDINGS]` | Seal |
| Step-6 | `d117_step6_confirmation_table_v5.json`; `FILL[STEP6-CUSTODY-PATHS-AND-RECORD-SHA256]`; `FILL[HC-IN-INDEPENDENT-CONFIRMATION-CUSTODY]` (hC custody-only) | Each arm |
| Authorization | `FILL[A1-AUTHORIZATION]`, `FILL[A2-AUTHORIZATION]`, `FILL[S1-AUTHORIZATION]`; seven exact contract §4 keys, mode 0600/create-once, locator/hash, attempt/pack/chain/purpose/non-claim/count; fresh record each allowed recovery | Each arm |
| IDs/T-0/ordinal/ARM/GO/consumption, rosters | `FILL[PER-OCCURRENCE-ID-AND-RECEIPT-MAP]`; §3 science/auxiliary rosters | Interfaces at seal; fresh runtime bytes |
| Absolute lexical roots/no-symlink/production census | `FILL[ROOTS-AND-CUSTODY-MAP]`: repository/measurement/shakedown/control, prospective/ARM/ledger/runs/quarantine/analysis/L10/scratch/staging/withheld and production roots, plan-pinned inventory | Recipe at seal; each arm |
| Independent backups/source authentication | `FILL[BACKUP-DESTINATIONS-AND-VERIFICATION]`; immutable source/derived separation and original-path replay | Recipe at seal; harvest |
| Qualification/G10 | §6 producer map; §5 control identities; `FILL[L10-A-RATIFICATION-RECORD-PATH]` | Producer recipe at seal; physical G10 before controls; ratification before claim |
| Interfaces/rc/policy/sizing | All §8 CLI FILLs, §4 deadline/span/stream and stop/outer rc bindings, §3 policy hash, timing sidecars | Seal; render each arm |
| Ledger/battery/OFF | §3 seed/battery map; `FILL[PER-OCCURRENCE-OFF-RECEIPTS]` | Source recipe at seal; fresh each window |
| Restricted metrics/release/liveness | §10 custody/release bindings; §8 Q110 destination | Mechanism at seal; release after claim seal; Q110 before ALPHA |
| File inventory/terminal/recovery maps | §12 inventory/maps; terminal method fixed by record 47 | Inventory at seal; actual extension proof before later arm |

## 14. Erratum to D-176 decision 4

**Prospective, dated 2026-10-05; effective only through this registration's seal; Ed may veto.** Ruling 76 governs (numbers below are its decisions); the original D-176 remains until seal. Exact ruling excerpts:

- **1–3:** “The D-176 decision-4 night is `s1`.” “Live gates on `s1`:” “G1, G2, G3, G4, G5, G8, G9”; “G6 and G7 retire as live gates”. Purpose stays G2B_SHAKEDOWN/non-claim; §5 carries separate G10; retain merged G7 class-refusal regression and explicit NOT_APPLICABLE basis.
- **4:** “each governed process carries a registered expected outcome.” Census exit 1/empty stdout and other exits 0 replace the all-zero interpretation; fd 0/no timeout/completed sequence remain. Exhaustive prompt/EOF tracing retires.
- **5–6:** “Two verdicts on `s1`.” “Evidence producers only OBSERVE”; “it never aborts the chain and never turns the G2-b verdict into RECOVER.” “No-science RECOVER does not spend `s2`.” §7 fixes fresh-attempt custody, science-start boundary and live-failure END STATE.
- **7:** “`a1` stays”; “`a2` also must expire with no launch.” Q110 gets the second arm-only control or the specified NULL-attempt ARM substitution.
- **8:** “Kernel edges (installed only after seal)”: A160 closes on qualification harvest PASS; Q3 drops NIGHT-PACK-REHEARSAL-01 hard-start; A161 closes SUPERSEDED; lead adds dated decision-4 erratum pointing to ruling 76. No kernel/decision-log edit is performed here.
- **9:** “Public outputs stay structural.” Raw non-CAMPAIGN_TRANSACTION chain stdout/stderr stay restricted, excluded from durable courier records (§10).

**Recorded Sol dissent (decision 3):** “keep G6/G7 as desk controls with `g7-control` amended to accept the non-claim template”; **not adopted**: no rehearsal authority exists to test and the amended template would never exist in production. The earlier advisory no-capture-recovery dissent also does not override §7's lead-authorized allowance. L10-A output root, G10 vector/deadline, terminal coverage and source-bound sizing are settled lead rulings, not open choices; factual bindings/CLI FILLs remain for integration and seal.
