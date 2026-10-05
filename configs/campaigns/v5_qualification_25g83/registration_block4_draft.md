# Registration V5-QUAL-25G83-B4: measurement block 4, the qualification block for the `_v5` claim family

**Status: DRAFT, 2026-10-05. Unsealed.** This file authorizes no arm and discharges no live gate. It is written
by the desk-day orchestrator seat (Opus 5.5) under lead ruling 76 and its addendum A
(`docs/process_traces/2026-10-04-desk-day-v5/76-r1-fold-ruling.md`), after the blind consult in brief 75 and both
answers beside it. A cold Fable judge and an independent Opus refuter seal it (§12). Ruling 76 changes D-176
decision 4 prospectively; until this seal, D-176 stands as written, and Ed may veto (§14).

A `FILL[...]` token marks a binding that is not yet fixed. It is never a default. No arm may happen while a FILL
that is due before that arm is open. Preparation and review are agent work; execution is `[QUIET-MAC]` work that
starts only after every agent seat has exited. Companion records in the same trace directory:
`42-block4-required-code.md` (what code each predicate needs), `44-block4-sizing.md` (window sizing) and
`47-block4-terminal-refresh-coverage.md` (which head changes after the block stay covered).

## 1. What this block is for

Before any claim-bearing `_v5` window, three things have to be shown on the real machine:

1. The unattended pack-bound launch works end to end: T-0 evidence, ARM, a purpose-bound GO, one-use consumption,
   the launcher and the A6 launch-realization recheck. This path is merged and unit-tested (#303, #307, #475) but
   has never run live. Measurement blocks 1 to 3 ran unattended through `scripts/run_night.py`, but as derivation
   and probe nights, not as `TRANSACTION_PACK` nights.
2. The unattended-execution gates that protect a number hold on a real window: no agent or operator activity
   during T-0 or capture, the clock anchor stays bounded, evidence survives (the D-176 decision-4 gates).
3. The real `_v5` launch-to-claim prefix works on the GAMMA pack: one non-claim A/B/B/A block, its bracket binding
   and whole-window verdict, the desk checker, and the finalizer refusing exactly as registered for an incomplete
   campaign (D-162, D-167: "G2-b").

G2-a (block 3) fixed a protocol parameter, the prefill length. It discharged none of these gates.

## 2. The occurrences

The block runs in this order, each step only after the previous one has passed:

**G10 physical control → `a1` → `a2` → `s1`.** Recovery is limited to §7: a fresh `s1` after a no-science tooling
failure, or at most one `s2`.

| Occurrence | What it is | What it must hand back |
|---|---|---|
| G10 control | The privileged-anchor positive control (§5), outside every armed or capture span. | The exact eight-key control record with its raw supports. |
| `a1` | An arm-only control on a throwaway real-GAMMA ARM context: fresh T-0, purpose `G2B_SHAKEDOWN`, `claim_eligible=false`, `permitted_blocks=1`. It arms once and never launches: no consumption, no bundle, no `night/chain.started`. | A genuine PASS/GO ARM, then the canonical verifier refusing `readiness_record_expired` after the ARM's own validity horizon, with proof that nothing launched. |
| `a2` | The same arm-only recipe with its own identity, authorization, custody and fresh T-0, started after `a1`'s expiry check. It exists to give Q110 its third real receipt bundle (§8). | The same expiry and no-launch proof. |
| `s1` | One consuming launch of the frozen GAMMA pack `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` as a `TRANSACTION_PACK` night, purpose `G2B_SHAKEDOWN`, `claim_eligible=false`, `permitted_blocks=1`: the first frozen science stage, exactly one A/B/B/A science block, then the governed post-science path. | Two separate verdicts (§7): the structural G2-b verdict and the decision-4 qualification verdict. |

No receipt, capability, namespace or T-0 evidence is shared between occurrences. The controls are not consuming
recovery allowances. Their waits come from their own receipts and boot, never from a guessed delay. `s1` uses
`scripts/run_night.py run --plan ...`, never the `rehearse` subcommand. There is no separate rehearsal pack,
profile, ledger or clone, and no live G6 or G7 control (ruling 76).

All occurrences run at one reviewed code head **H**, which is meant to be the ALPHA/BETA/GAMMA claim head. H
contains the producer fixes #472, #473 and #476, the one-block stop #474, the A6 recheck #475, the issued pin and
packs #477, the network-time policy #479 and the block-4 qualification code
(`feat/2026-10-05-v5-qualification-code`). §12 binds H by full SHA and file digests, not by branch or PR names.

## 3. Operating conditions and fixed inputs

1. **Machine.** The M3 Max (Mac15,9), macOS build 25G83, on AC power with the battery at float, `ac_high_power`,
   powermetrics interval 100 ms. Nobody acts at T-0 or during a consuming chain. The driver and every governed
   subprocess read stdin from `/dev/null`. The first agent census and the repeated 30-second censuses keep their
   argv and results. All agent seats exit by t0 − 8 min; harvest seats return only after completion, courier and
   dead-man boundaries are safe, and exit again before the next occurrence.
2. **Calibration acceptance.** `d079_calibration_acceptance_v2_n24_25g83_r2`
   (`configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, SHA-256
   `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`). Both `s1` brackets use its freshness,
   screen and drift rules. No older acceptance may stand in.
3. **Workload.** `mlx-community/Qwen3-1.7B-4bit` and `mlx-community/Qwen3-8B-4bit` with the revisions, tokenizer
   and file hashes in `configs/model_panels/qwen3_4bit.json` at H. The frozen order manifest gives
   small/large/large/small; `FILL[S1-ROSTER]` lists the exact first-stage member ids. Prompt bytes, the issued
   prefill length, thinking-off greedy decode, forced 512 output tokens, prompt-0 assignment and family m=2 keep
   their D-166 meaning. No subset pack and no shortened workload.
4. **Issued pin bundle.** `configs/campaigns/d117_contrast_v5/prefill_pin/` (landing in #477):
   `prefill-prompt-pin.json` SHA-256 `d1209f6d5998e4a48ac0dae7ed04a8f6a2c5ec9950d768f0df9ef8839a32dccb`;
   `selection.json` SHA-256 `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`;
   `prefill-prompt-ladder.json` SHA-256 `43a77ea99cb2ac1f087f19d2f672444727b3e73a839e5dcfd8db1198d1352885`.
   These bytes are authenticated at H. Selection is never rerun.
5. **Campaign policy.** `configs/campaign_policies/quiet_mac_p2_production.json`, `FILL[PRODUCTION-POLICY-SHA256]`.
   Its admission thresholds, retry count, dwell and abort rules stand; block 3's 300-second backoff is not
   imported. The NEG-8 bound corpus, the start, midpoint and end references and the settles are frozen in
   `FILL[S1-COMPLETE-AUXILIARY-ROSTER]`. They are separate from the four science members.
6. **Calibration ledger.** The physical ledger authenticates with `verify_custody=True` against the committed pin
   at H. At drafting the pin is sequence 402, head digest
   `3ce1676c530452df301e8f09d97905487b06b8ed8887d7c7a728a08fd5310c08`; the retained seed is block 3's SELECT
   re-harvest `derived/terminal-ledger.jsonl` (SHA-256
   `6ee89e5a1b83c88d865a65cca71177d19a4b23b47d6af2979f92a6840857530e`). The actual source at H is
   `FILL[PRODUCTION-LEDGER-SEED]`. The live head is not the acceptance cutoff (sequence 376); brackets read the
   cutoff view (the #467 lesson). `s1`'s ARM, GO, consumption and runs sit in shakedown custody, isolated from claim
   roots.
7. **Battery float, directive #421, every occurrence.** Fresh authenticated raw ioreg plus the shared
   `joulewise/battery_float.py` observation at arm, immediately before publication or install, and at T-0. PASS
   needs ExternalConnected=Yes, IsCharging=No, signed InstantAmperage within ±200 mA and UpdateTime no older than
   180 s; missing, stale or malformed bytes cannot pass. Every bracket, science member and obligated auxiliary
   capture in `s1` has its pre/post raw pair outside the clock-anchor stamps and the sampler lifetime, with
   identity, digests and replay authentication, applied to every attempt including failed or superseded ones. The
   controls launch nothing and so have no capture pairs. `FILL[BATTERY-EVIDENCE-MAP]` binds the paths. A custody
   failure is REFUSED; an authentic non-pass reading cannot qualify and has no tooling allowance (§7). Endpoint
   pairs cannot see an excursion that falls entirely between two observations; that limitation stays disclosed.

Changing any of these after the seal is a new rule (§11), not an arm-time choice.

## 4. Window shape, deadlines and sizing

**Controls.** Author a fresh T-0 set, ARM once, keep the PASS/GO result and its exact expiry, and never install or
invoke a consuming launcher. At or after the ARM's capability deadline plus 1 ns (the ARM deadline is the
earlier of 300 s after evaluation and every evidence deadline), the canonical verifier must refuse
`readiness_record_expired`. Then prove there was no consumption, chain start, sampler or bundle. The control
does not wait for its six-hour nonvolatile evidence horizon: nothing from it is ever reused, and that wait would
cost about six idle hours per control without protecting anything. The next occurrence's first T-0 capture starts
only after the previous control's perishable evidence has expired, that is after the latest of its ARM deadline, its
GO deadline and every volatile T-0 evidence deadline (a horizon of 1200 s from the evidence origin), so the next
occurrence's check set is fresh in the sense of the D-149 fence. `FILL[ARM-CONTROL-DEADLINE-RECIPE]` carries these
computed deadlines and the expiry, check and courier caps. `a1` completes before `a2` starts, and `a2` before
`s1`'s T-0 and clean dwell.

**`s1`.** One launch. A settled OFF receipt and a 600-second clean dwell; the pre settle and the pre bracket with the
acceptance-derived screen; NEG-8 bound work and start references; the first before-midpoint science stage with
`scripts/run_campaign.py --max-blocks 1` (#474); the midpoint and end references; the post bracket in the same
session; finalization and the ratified physical-ahead STOP. There is no after-midpoint science, no fifth science
member, no manual SIGINT or polling kill and no second launch. The stage-stop return code and terminal record
(`FILL[ONE-BLOCK-STOP-RC-AND-RECORD]`) are bound separately from the outer chain's return code
(`FILL[S1-SUCCESSFUL-CHAIN-RC]`); the historical rc 130 is not adopted. Reference and bound stages never receive
the science block limit.

At STOP the chain keeps the exact terminal candidate. It does not advance a tracked pin, emit launch completion,
write a bracket binding or verdict, or finalize analysis. After the quiet window the governed desk step runs: the
reviewed ledger refresh and restaging, the two verified backups, close-out and the network-time-OFF stand-down
(addendum A), then the harvests. STOP by itself does not make G9 complete.

**Sizing.** `44-block4-sizing.md` holds the numbers. The method is fixed here. Each component is a source-bound
allowance `{seconds, source:{path, sha256}, source_pointer}` drawn from block-3 archives (reading them as
diagnostics is allowed after block 3) and the committed GAMMA configs, committed under
`configs/campaigns/v5_qualification_25g83/`. No `s1` byte is used for sizing. The writer sizes exactly the stages
the rendered one-block G2-b chain runs, and nothing it does not dispatch.

- `E_ABBA = 2·E_small + 2·E_large`, each member estimate covering load, warmup, the stage's input and forced
  decode, cooldown, idle admission and the policy's bounded retry.
- `NIGHT_PROGRAMMED_SPAN_S_s1 = ceil(T_pack_t0 + T_fixed_settles + T_pre_post_calibration +
  T_bound_and_references + E_ABBA + T_stage_custody + T_terminal_shutdown)`, each term counted once.
- `WINDOW_MAX_S_s1 = 60·ceil((NIGHT_PROGRAMMED_SPAN_S_s1 + 2700)/60)`. The 2700-second clean-dwell cap is added
  once, outside the programmed span. The writer emits these literals and enforces a latest chain start of
  `t0 + WINDOW_MAX_S − NIGHT_PROGRAMMED_SPAN_S`. A chain still running at expiry is RECOVER, never a partial PASS.
  Completion, courier and dead-man bounds: `FILL[PER-OCCURRENCE-SHUTDOWN-CAPS]`.

**Clock design check (addendum A).** Every member's effective clock-anchor bound must be at most 5 ms at harvest;
that admission is unchanged. The design-time question is whether the planned streams can plausibly meet it. The
check uses observed effective bounds of comparable streams on this machine, models and OS build: block 3's SELECT
re-harvest holds 50 anchor records, all `bounded`, the largest 4.02 ms. The stacked worst case (largest observed
half-width plus the largest drift rate over a 613-second envelope that also counts the separate cooldown sampler)
comes to 8.5 ms. It is reported as a diagnostic, not used as a gate, because it combines three worst cases that do
not occur together in one stream. The margin between 4.02 ms and 5 ms is thin and is disclosed to the cold gate.

## 5. Network time, and the G10 control

Network time stays **OFF** across and between occurrences and after restore. A sync would step the clock that
timestamps every power sample. Each control and each consuming attempt gets its own write-once OFF receipt on its
own boot, admitted by the shared reader (setter exit 0 and normalized `setUsingNetworkTime: Off` or
`Network Time is already off`). Its first capture or author boundary is at least 600 s after the receipt on both
clocks. Receipts are never reused. T-0's clock-disable capture and the clock row authenticate the same state
through G4; neither authorizes ON. Freeze and ARM derive this doctrine through `clock.network_time_policy` (#479).

**Why G10 exists.** G4 passes when the RAW clock anchor stays within 5 ms. G10 shows that the T-0 author really
refuses when the anchor has moved more than 5 ms; without it, a G4 PASS has never been shown able to fail.

**The physical control precedes `a1`'s T-0** and sits outside every armed or capture span. It is Ed-owned, as
D-176 decision 4 requires, and runs `scripts/ed_session/capture_t0_anchor_positive_control.py`
(`FILL[G10-CONTROL-CLI]`, recipe 46):

1. The helper writes machine-authored CLOCK_REALTIME and CLOCK_MONOTONIC_RAW before-stamps and the real author
   inputs into their own control custody.
2. It turns network time ON with the arm step's reviewed vector, imported from
   `scripts/capture_t0_step.py::_arm_reference` (`/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime on`,
   the existing D-127 grant), keeps argv, stdout, stderr, return code and stamps, and polls the RAW anchor for a
   movement above 5 ms within a bounded deadline (120 s default, 300 s maximum). OFF runs in a `finally`. No new
   sudoers grant and no other way of setting the clock.
3. If the anchor moved more than 5,000,000 ns, it runs the real T-0 author on the changed sequence and requires
   exactly `evidence_author_t0_clock_attestation_underivable` with no PASS namespace. A movement of 5 ms or less
   discharges nothing: the attempt is preserved and goes to the lead, and it is not retried in a loop.
4. It writes the exact eight-key record (`schema_version`, `performed_by`, `outside_t0_sequence=true`,
   `network_time_reenabled=true`, `forced_resync=true`, `anchor_before_ns`, `anchor_after_ns`,
   `author_refusal_reason_code`) with its raw transcripts, inputs, boot id, digests and refusal and absence proof:
   `FILL[G10-CONTROL-RECORD]`.
5. It archives the OFF receipt. Every later occurrence obtains its own OFF receipt and dwell.

Software falsifiers additionally replay the real author and arm predicates at 5 ms ± 1 ns with their exact refusal
codes. They do not replace the physical control. Without an authenticated G10 record, `s1`'s qualification
cannot pass.

## 6. What each verdict checks

**Decision-4 qualification on `s1`'s own evidence.** The existing evaluators in `joulewise/t0_rehearsal.py` run on
records that observation producers write during `s1` and the desk step. `FILL[S1-QUALIFICATION-PRODUCER-MAP]` binds
each record's path, schema, digest and producer.

| Gate | What it protects | Required evidence |
|---|---|---|
| G1 execution | A hang or prompt costs a window | Each governed process has a registered expected outcome: the agent census passes on `pgrep` exit exactly 1 with empty stdout, every other process on exit 0. fd 0 at `/dev/null`, no timeout, `sequence_completed`, with pid/argv/exit custody. Exhaustive exec-descendant prompt tracing is not required: with fd 0 at `/dev/null` a prompting child gets EOF and shows up as an abnormal exit or an incomplete chain. |
| G2 T-0 namespace | An attestation standing in for a probe | The exact fifteen ARM_ONLY receipts and captures, the canonical source and receipt census, zero operator-attestation facts, a machine PROBE clock fact, hashes and membership matching the GO. |
| G3 HID idle | Operator activity at T-0 | A raw `HIDIdleTime` witness covering the actual RAW-clock T-0 span. |
| G4 clock | Clock steps inside energy windows | Real fixed-roster reference bytes, clock-disable and settled OFF evidence, and the existing recomputation: 600–3600 s T-0 span, 30 s repeat-reference cap, 5 ms RAW bound. |
| G5 GO and consumption | Wrong pack, stale ARM, double launch | The current 26-key pack GO, ARM and one v3 consumption, with authenticated plan, authorization, confirmation and census; replay at the recorded boot and instant, C1–C5. |
| G6, G7 | (retired) | `NOT_APPLICABLE`, basis `retired_by_ruling_76`, never PASS. The merged unit regression that refuses a fully valid rehearsal receipt by class stays. |
| G8 process lineage | Agent load in captured power | The agent's pid, argv and observed exit before the chain and capture, the real chain and capture boundaries, and zero-agent censuses throughout. An agent cannot certify its own future exit. |
| G9 lifecycle | Evidence loss; clock left ON | Ordered, hash-bound COMPLETE records for launch, capability_consumption and capture (from the night), and claim_backup and bound_backup (two verified copies of the `s1` custody and runs roots to two distinct destinations), close_out (Phase G post-run assertions plus the OFF receipt identity) and restore (network time observed OFF, stand-down), the last four from the post-STOP desk step (addendum A). Courier, relaunch and dead-man facts are kept. |
| G10 | G4's ability to fail | §5's physical control plus the software falsifiers, authenticated by the qualification harvest. |

Observation producers only observe. A producer fault cannot abort the chain or turn the structural verdict into
RECOVER.

**Controls (`a1`, `a2`).** A genuine PASS/GO ARM, then `readiness_record_expired`; no launcher, consumption,
sampler, bundle or chain start; expiries ordered before the next T-0; authentic Q110, #421 and OFF inputs. An
occurrence cannot pass merely because nothing happened.

**Structural `s1` (G2-b).** All four science bundles succeeded and are strictly valid on re-reduction from raw
bytes, with the exact first-block identities and order and `uncertainty_evidence.clock_anchor.status=bounded`. No
fifth or partial science member, no second occurrence, no leftover campaign lock. The auxiliary, bound and
reference captures are enumerated and face their own validation and battery obligations ("four science members" is
not "four bundles"). Both authenticated bracket endpoints, the session enclosure and the acceptance decision pass
against `n24_25g83_r2`; `physical_ahead` is a custody state, not a bracket PASS. The bracket binding is built
before exactly one authoritative passed whole-window row, and the verdict file is an exact copy of that row. The
desk checker passes `NR14-LAYOUT` with no FAIL, and S11-A4 is either exercised PASS or the registered
`present_stages=0 assertion_not_exercised` SKIP.

**Folded L10-A.** Strict-validate once and reduce once into restricted L10 custody. Then finalize once through the
refusing checker against a complete staged scratch copy of the real prefix, never the source. `--output-dir` is the
staging custody root, the same root as `--custody-root` (the finalizer requires it,
`joulewise/analysis_manifest_v3.py`; recipe `docs/process/v5-l10-rehearsal-phase.md` §L10-A corrected). Exactly
`{analysis_finalization_member_cover_mismatch}` passes; a successful finalization or any other reason fails;
`analysis_finalization_attachment_missing` stops for a written ruling and never licenses staging a floor. Both
`floors/` directories exist and are empty before and after, and the aggregate-floor argument names an absent
artifact. Equal before and after G2-b tree hashes prove the source was not written. The record carries
`proof_scope=L10_A_G2B_CONTRACT_PREFIX`; the lead ratifies it before the first claim arm. It does not prove the
finalizer's later bracket, ledger or floor legs (L10-C).

## 7. Verdicts, recovery and END STATE

Harvests read authenticated immutable archives, never a narrative.

**Structural G2-b verdict**, in this order: a harvest archive, authentication or tool fault is **REFUSED**;
otherwise no `night/chain.started` (and a closed or proven-gone `launch.pending` group, #475) is **NULL**; otherwise
§6's structural predicates with the registered stop and chain return codes and the non-claim, one-use, clock, OFF
and battery obligations give **PASS**; every other started occurrence is **RECOVER** with an immutable named cause
and cause class.

**Qualification verdict.** PASS only when G1, G2, G3, G4, G5, G8, G9 and G10 pass and G6 and G7 read
NOT_APPLICABLE. UNRULED or INCOMPLETE never passes. A producer fault makes this verdict REFUSED or FAIL and touches
nothing else. A qualification FAIL beside a structural PASS goes to the lead: a producer repaired through R3 is
re-run on the same bytes where possible; a gate that genuinely failed live (an agent present, an unbounded clock, HID
activity) is END STATE. A structural PASS alone does not hand off qualification.

**REFUSED** is repaired through standing R3, and the identical source bytes are re-harvested into a distinct derived
archive; the earlier record is kept. It is not a science outcome and authorizes no capture.

**NULL** keeps the ARM, the refusal and absence proof and the attempted window. A re-arm needs the cause removed and
a new plan id, authorization and T-0. **The same refusal code twice in a row goes to a consult (Sol plus Opus), not
a third arm.** No same-plan retry, no overwritten refusal, no hidden automatic re-arm. A failed control is kept and
remediated the same way, with a newly registered identity before any consuming arm.

**`recover_no_science` (ruling 76 decision 6).** If a named pack-path or launch tooling cause fired after
`chain.started` but before the first science member's sampler started, that attempt holds no science bytes and
D-078 has nothing to pool or top up. It is kept, cured through R3 and re-armed as a fresh `s1` (new plan id,
authorization and T-0) without spending the `s2` allowance. The harvest must authenticate the cause ordering and
the absence of any science sampler start. It stays RECOVER; it does not become NULL.

**At most one `s2`**, only when `s1` is RECOVER because of a named tooling defect removed through reviewed R3 that
makes the code agree with this text, within §12. It has its own authorization, roots, T-0 and complete one-block
roster. `s1` is kept unchanged. Nothing is pooled, replaced, topped up or rerun (D-078).

**Instrument or physics RECOVER has no `s2`:** a clock failure, acceptance or bracket physics, an authentic battery
non-pass, a machine or environment failure during the started chain. The systematic-clock trigger stands: **at
least five members with a recorded anchor status (excluding `not recorded`), and more than half of them not
`bounded`**, counted over the occurrence's actual science, reference and bound records, with the denominator
reported. Five is not lowered to fit four science members. A tooling explanation does not override this trigger.

**END STATE:** the block stops; no transaction opens and nothing further arms under this registration; Ed is
emailed; the next step is a design record naming the cause, with a consult and a cold gate. It applies to a genuine
live qualification failure, an instrument or physics RECOVER, an `s1` RECOVER without an eligible tooling cause, a
code-head conflict that needs new design, and an `s2` RECOVER. There is no fallback and no open-ended re-arm loop.

## 8. Producers, outputs and Q110

The integration branch fixes these interfaces before seal; this table grants no write authority.

| Role | Interface | Output |
|---|---|---|
| Plan writer | `FILL[PLAN-WRITER-CLI]` | Canonical `s1` (and allowed `s2`) plans through `NightPlan.from_mapping` and `write_night_plan`, binding plan, pack, chain, authorization, confirmation, backup destinations and sizing. |
| Arm-only controls | `FILL[ARM-ONLY-CLI]`, `FILL[ARM-ABORT-CHECK-CLI]` | `a1`/`a2` contexts and an authenticated `arm-abort-control.json` each. |
| Qualification | `FILL[QUALIFICATION-OBSERVE-CLI]`, `FILL[DESK-CLOSEOUT-CLI]`, `FILL[QUALIFICATION-HARVEST-CLI]` | Observation records, the desk step's backup, close-out and restore records, and the qualification verdict. |
| G2-b harvest | `FILL[G2B-HARVEST-CLI]` | `harvest.json`, bracket, whole-window, desk and L10 proofs, tree hashes, restricted re-reductions and the L10-A record. A re-harvest authenticates the existing verdict row and never appends another. |
| Terminal refresh | `FILL[TERMINAL-REFRESH-CLI]` | The guarded pin advance, readiness and freeze refresh and record 47's changed-path proof. |
| Q110 | `FILL[Q110-RECORD-CLI]`, `FILL[Q110-RECORD-PATH]` | At least three real bundles from `a1`, `a2` and `s1` (a NULL `s1` attempt's ARM receipt may substitute), with receipt ids, paths, hashes and boots. |

Q110's formula is unchanged: `validity_origin = valid_until_monotonic_ns − _validity_horizon_ns(kind)` and
`elapsed = validity_origin − t_batch_finished`, where `t_batch_finished` is the existing
`clock.correct_and_prior_state` repeat-reference-batch-finished monotonic stamp. Q110 is a limitation through G2-b,
not a launch gate: it closes with at least three real bundles and every elapsed value below 600 s, or a cold gate
re-rules it **before ALPHA**. Nothing here relaxes the 600 s.

Public outputs carry only paths, hashes, identities, rosters, counts, status and reason codes, and the required
control and liveness facts. A160 closes on the `s1` qualification harvest PASS (installed after seal, §14).

## 9. Scope

PASS on both `s1` verdicts hands off to the remaining claim prerequisites. It does not open the transaction.

Outside this block: the ALPHA/BETA/GAMMA claim registration and analysis plan; **directive #416's pre-arm triple
audit** at the frozen claim head (which contains #465), finished before the first claim-bearing window; the
outcome-independent environmental diagnostic from Sol's consult §5, which belongs in the claim registration;
ALPHA/BETA floor collection and mint; GAMMA claim collection; L10-B and L10-C; the transfer fiducial; scored `_v6`.
No byte from this block becomes claim, floor, mint or replacement evidence. All three `_v5` pack and freeze
identities are bound here, but only GAMMA launches science. A later `CAMPAIGN_TRANSACTION` authorization (D-171 §3)
needs the custodied G2-b PASS and every other prerequisite; `G2B_SHAKEDOWN` never discharges
`V5-TRANSACTION-GO-01`.

## 10. Blindness

`s1` runs the real claim workload, so it produces real energies. Until the claim analysis plan is sealed, harvests
release structure only: **no energy, power or per-member duration** in stdout, stderr, email, public JSON, tables or
review summaries. Hashes, paths, and readiness, control and Q110 timing are allowed. Log tails are filtered. For
every purpose other than `CAMPAIGN_TRANSACTION`, `scripts/run_night.py` leaves the raw chain stdout and stderr out of
the pushed courier record (ruling 76 decision 9), because those logs carry member durations; they stay in restricted
local custody.

The re-reduced per-member metrics go to `<s1-harvest>/withheld/s1-reductions.json` (and the `s2` analog). Raw
bundles, traces, original summaries, calibration numeric diagnostics and unfiltered validation and reduction
transcripts also stay restricted, and no other artifact may carry the same fields. `FILL[BLIND-CUSTODY-MAP]` fixes
locations and access. Nobody designing or sealing the claim plan opens those metrics first. Automation may read them
to validate, reduce and evaluate fixed predicates, but it writes out structure only. The lead names RECOVER causes
from structural, admission, bracket, clock and custody facts. Any needed access to restricted numbers is custodied
and disclosed to the cold gate, and never used to tune the claim analysis. Release needs the sealed plan's identity
and a recorded release event: `FILL[CLAIM-PLAN-RELEASE-BINDING]`.

## 11. Changes after the seal

Nothing in §§2–10 changes for an occurrence that has been armed or completed. A change to a rule, threshold,
purpose, roster, recovery allowance or blindness condition needs a prospective cold-gate erratum. A fix that only
makes code agree with this text goes through gated R3, with Fable's final pass for measurement or qualification
code; old bytes and old verdicts are kept and a distinct derived re-harvest is written. A started physical failure
never becomes NULL. If it is unclear whether a cause is tooling or physics, the lead rules before any recovery arm.

## 12. Seal, the pinned head, and which head changes stay covered

The seal record (`FILL[BLOCK4-SEAL-RECORD-PATH]`) names the cold Fable judgment and the independent Opus refutation,
this file's SHA-256, H and its source digests, the real rendered plans and chains, the filled controls, the sizing
and the regression evidence. A later records commit cannot hide a code change.

**Pinned at H** (exact paths and SHA-256s in `FILL[SEALED-FILE-INVENTORY]`; a directory name is not a pin): this
file and records 42, 44, 47 and 76; the qualification plan writer, arm-only control, observation producers, desk
close-out, both harvests and the G10 helper; `joulewise/night_plan_writer.py`, `joulewise/night_gate.py`,
`scripts/run_night.py`, `scripts/launch_window.py`, `joulewise/arm_readiness.py`,
`joulewise/arm_readiness_evidence.py`, `joulewise/arm_readiness_evidence_t0.py`, `joulewise/t0_rehearsal.py`,
`scripts/capture_t0_step.py`, `scripts/gen_g2_phase_d.py`, `scripts/run_campaign.py`, `joulewise/controller.py`;
the calibration capture, ledger, bracket, binding, verdict, battery and OFF readers; the strict validator, reducer,
scratch finalizer and checker; the three `_v5` generators and generated pack trees with their identity and
readiness sources, freeze receipts, sidecars and historical pinset; the panel, policy, pin bundle and acceptance;
`configs/production_custody_inventory.json`; the launchd templates and installer; and the two chain sources
`docs/phase_2/window_runbook.md` and `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`.

`a1`, `a2` and the first `s1` arm at exactly H. Block 3's broad permission to arm at unrelated descendants is not
imported. Before the first occurrence, records-only seal and arm commits may move to a final H only with proof that
no pinned executable, generated config or chain source changed.

After the occurrences, a later head H′ stays covered only by: (i) reviewed ledger-pin advances from this block,
with exact seed and terminal custody and the readiness and freeze refresh they require; (ii) gated R3 fixes that
make code agree with this text; (iii) records-only changes under `docs/`, `tests/`, RUN_STATE or TASK_QUEUE that
leave every pinned executable, generated config and chain source unchanged. Each extension has an explicit
changed-path and digest map before a later arm.

**Terminal refresh coverage is settled (ruling 76).** The post-`s1` desk refresh moves only the ledger pin and
re-authors readiness and freeze records. Executables, generated pack configs and chain sources do not change,
because the packs pin the acceptance cutoff, not the live ledger head. So H′ = H plus those records is covered by
`s1`'s qualification, proven by record 47's `git diff --name-only H H′` against its exact allowlist
(`FILL[TERMINAL-REFRESH-CHANGED-PATH-MAP]`). New readiness and freeze hashes are reviewed as new; no later arm uses the
old freeze.

An R3 recovery head needs `FILL[RECOVERY-HEAD-EXTENSION-IF-NEEDED]` before a fresh `s1` or the `s2`. If it changes a
launch or measurement path that `s1` exercised, H does not automatically qualify it: the lead and a cold gate decide
coverage before any recovery or claim arm. Any other head difference or operating-condition change needs a new seal.

## 13. Binding register

| Binding | Field | Due |
|---|---|---|
| H, integration gates, this file's hash, cold pair | `FILL[H-FULL-SHA-AND-INTEGRATION-GATES]`, `FILL[REGISTRATION-SHA256-AND-COLD-PAIR]` | Seal |
| Pin bundle | §3.4 digests, authenticated at H | Seal |
| ALPHA | `configs/campaigns/d117_floor_qwen3-1p7b_v5`, `FILL[ALPHA-PACK-DIGEST-AND-FREEZE]`; predecessor `d117_floor_qwen25_1p5b_v3`, expected `freeze-0004` | Seal |
| BETA | `configs/campaigns/d117_floor_qwen3-8b_v5`, `FILL[BETA-PACK-DIGEST-AND-FREEZE]`; predecessor `d117_floor_qwen25_7b_v3`, expected `freeze-0004` | Seal |
| GAMMA | `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`, `FILL[GAMMA-PACK-DIGEST-AND-FREEZE]`; predecessor `d117_contrast_qwen25_1p5b_vs_7b_v3`, expected `freeze-0004` | Seal |
| Desk proof, family, history, identity, battery S3/S4 disposition | `FILL[DESK-PROOF-AND-FAMILY-BINDINGS]` | Seal |
| Step-6 confirmation | `d117_step6_confirmation_table_v5.json`; `FILL[STEP6-CUSTODY-PATHS-AND-RECORD-SHA256]`; hC stays in custody only | Each arm |
| Authorizations | `FILL[A1-AUTHORIZATION]`, `FILL[A2-AUTHORIZATION]`, `FILL[S1-AUTHORIZATION]`: the seven contract §4 keys, mode 0600, create-once | Each arm |
| Ids, T-0, ordinal, ARM/GO/consumption, rosters | `FILL[PER-OCCURRENCE-ID-AND-RECEIPT-MAP]`, §3 rosters | Interfaces at seal; bytes at runtime |
| Roots and production census | `FILL[ROOTS-AND-CUSTODY-MAP]` | Recipe at seal; each arm |
| Backups | `FILL[BACKUP-DESTINATIONS-AND-VERIFICATION]` | Recipe at seal; desk step |
| Qualification and G10 | §6 producer map; §5 control record; `FILL[L10-A-RATIFICATION-RECORD-PATH]` | Producers at seal; G10 before `a1`; ratification before claim |
| Interfaces, return codes, policy, sizing | §8 FILLs; §4 deadlines and stop codes; §3.5 policy hash | Seal; rendered each arm |
| Ledger, battery, OFF | §3.6–3.7; `FILL[PER-OCCURRENCE-OFF-RECEIPTS]` | Recipe at seal; fresh each window |
| Restricted metrics, release, Q110 | §10, §8 | Mechanism at seal; release after claim seal; Q110 before ALPHA |
| File inventory, terminal and recovery maps | §12 | Inventory at seal; maps before a later arm |

## 14. Erratum to D-176 decision 4 (prospective; effective only through this seal)

Ruling 76 governs; D-176 stands until the seal. In short:

1. The decision-4 qualification night is `s1` (purpose `G2B_SHAKEDOWN`, non-claim). No rehearsal pack, profile,
   ledger or clone is built.
2. Live gates on `s1`: G1, G2, G3, G4, G5, G8, G9, plus G10's separate physical control and software falsifiers.
3. G6 and G7 retire as live gates (no rehearsal authority or roots exist for them to test); the G7 unit regression
   stays; the evaluator records them NOT_APPLICABLE, never PASS.
4. G1 uses registered per-process expected outcomes (census exit 1 with empty stdout; others exit 0).
5. `s1` has two verdicts, and observation producers never abort the chain or change the structural verdict.
6. A no-science tooling RECOVER re-arms as a fresh `s1` without spending `s2`.
7. `a1` stays; `a2` supplies Q110's third receipt bundle.
8. Kernel edges, installed only after seal: A160 closes on `s1`'s qualification PASS; Q3 drops its
   NIGHT-PACK-REHEARSAL-01 hard-start; A161 closes as superseded; D-176 decision 4 gets a dated erratum pointing to
   ruling 76.
9. Non-claim courier records exclude raw chain logs.

**Recorded dissent (Sol, on decision 3):** keep G6 and G7 as desk controls, with `g7-control` amended to accept the
non-claim template. Not adopted: with no rehearsal authority in existence there is nothing for them to catch, and the
amended template would never exist in production.
