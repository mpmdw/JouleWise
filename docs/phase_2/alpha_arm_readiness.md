# Window ALPHA arm readiness — checked human view

<!-- Standing rule (D-1 recurrence class, 3rd occurrence 2026-08-12): any
checkpoint re-anchor of this document MUST resweep every gate row's status
cell against main in the same commit — a banner-only re-anchor is the defect,
not a smaller version of the fix. -->

**Checkpoint:** 2026-08-15, post-PR #152 main (`fac87d1`; #152 payload
`a61ac92`). **Current verdict: NOT READY. Do not arm Window ALPHA.** The
2026-08-15 readiness council recorded 0 READY / 11 NOT-READY, and the live
`WINDOW-COUNCIL-GATE` permits no quiet-machine selection until a reconvened
READY-candidate council records no NOT-READY or UNVERIFIED verdict and closes
the required operator-qualification rows with evidence.

Window ALPHA is the first prospective D-117 night: the Qwen2.5 1.5B decode
floor with prefill floor cells. The authoritative row set is
`configs/arm_readiness/d117_row_registry_v2.json` (the ruled live registry;
the frozen `_v1`–`_v3` packs pin the archival `d117_row_registry_v1.json`
coordinate in their immutable plan trees); this page is a checked,
plain-language view of its ALPHA profile. A row appearing here does not make
it pass. Only authenticated evidence consumed by the D-134 generator can do
that.

Readiness has two stages. At pack freeze, the completed frozen pack pins only
the non-authorizing freeze receipt's path and SHA-256. It declares the future
arm receipt's schema and custody namespace, but never that future receipt's
filename or digest. Only at T-0, from the completed and unchanged pack, does
the generator recheck the freeze rows and live rows and create the external arm
receipt under window custody. A freeze receipt always says that arming is not
applicable. Only an unexpired, unsuperseded external arm receipt may carry
`GO`, and it remains necessary rather than sufficient: the lead's verification
and the operator's physical foreground action are not delegated.

For the 2026-08-13 frozen pack, the D-134 freeze receipt and plan-tree pin are
authoritative over the byte-frozen legacy
`unfrozen_draft` status/README wording. The generator's freeze-aware wording
applies only to future regenerated packs, per the 2026-08-14 M-2 ruling; this
checked view never licenses changing a committed frozen pack byte.

Those receipts remain a non-authorizing record of what passed at `49dcc49`;
they are not a current arm license. Main has advanced through #150, #151, and
#152, council Phase 1 still has open repairs, and Phase 2 requires one atomic
successor-family re-freeze before the re-audit and READY-candidate sitting.

Each readiness receipt carries a boot-session identifier. If the Mac reboots
between freeze and arm, verification automatically rejects receipts from the
earlier boot session and requires new verification.

The collection procedure remains the
[Quiet-Mac Claim-Window Run-Book](window_runbook.md). This page does not
replace it.

## Current gate checklist

Every status cell below was reswept against post-#152 main, the committed
freeze receipts, and the council verdict. A prior `PASS` is reported as dated
evidence only; it does not override the council gate or the required successor
re-freeze.

| Gate | Status (2026-08-15) | What makes it green | Who acts | Source |
|---|---|---|---|---|
| Recovery and calibration-ledger arming path | **IMPLEMENTED; exact-head replay pending.** PR #118 landed the recovery path, and #152 landed the strict R2 plan resolver plus the D-127 network-time route. Neither merge is perishable arm evidence. | Re-run the governed recovery, resolver, and ledger checks against the final successor pack and exact reviewed measurement head. | Lead | PR #118; PR #152 (`a61ac92`); D-127; D-121. |
| Manual arming and recovery procedure | **IMPLEMENTED; prior rehearsal passed; successor dress rehearsal pending.** The 2026-08-13 `dry-run-0001` passed all four hash-bound checks at `49dcc49`; #152 then amended the runbook and T-0 path. | Complete the expanded operator qualification and full dress rehearsal against the successor pack and exact reviewed head. | Lead + Ed | `docs/process_traces/2026-08-13-freeze-execution/dryrun-alpha.json`; PR #152; council verdict. |
| Mint trust bar | **CLOSED; proof re-run deferred.** PR #122 landed the trust behavior; #129 split the decisive proof; hosted runs `31541829071` and `31518739878` succeeded, discharging D-130's second-independent-execution condition and expiring its temporary citation discipline. The matrix is currently NOT runnable at current main (fixture drift); automatic triggering waits on WO-PROOF-RUNNABILITY-REPAIR. | Preserve the trust behavior; the repair work order restores automatic proof execution. | Discharged (repair queued) | PR #122 (`ae6af48`); PR #129 (`7a76a29`); D-130 closure note + 2026-08-16 addendum. |
| Writer uses the authenticated acceptance value | **GO** (2026-08-12, PR #142 merged 5be400e). The writer authenticates the issued acceptance artifact (byte-pinned sha) and derives the comparator at runtime under the artifact's own rounding rule; the frozen chain literal is checked two-way against the acceptance-derived value, then the writer derivation path is executed and required to return that same value. Six named fail-closed refusals occur before MLX import/lease/custody; CH-1 deleted the writer's copied scalar. | — | Discharged | PR #142 D-121 comment; `docs/strategy/2026-08-08-40h-plan.md` Phase A item A3. |
| Multi-cell mint and pin vocabulary | **IMPLEMENTED; successor verification pending.** The multi-cell base and #140's governed estimator vocabulary are on main and were `PASS` in the 2026-08-13 freeze receipt. | Re-run focused and integration checks at the final successor head and bind the successor pack bytes. | Lead | PR #140 (`e11b1ad`); `freeze-0001.json`, the multicell-mint receipt row. |
| Common-mode contrast estimator identity | **REGISTERED IN THE FROZEN PACKS; no paper-regime swap yet.** Six shared-edge comparative floor cells select `d124_two_shared_edge_common_mode.v1`, whose retained-cell result is **1.8695016260131627 J** versus the 8.611855 J conservative composition. Retained results from this cycle still use the conservative composition; the paper swap waits for the first post-freeze mint. | Preserve the selector through the successor re-freeze and execute the registered paper swap only at its queue trigger. | Lead | PR #140; PR #144 (`dc162bc`); committed `calibration_plan.json` files; D-133. |
| Arm-time identity-pin projection | **PASS in all three 2026-08-13 freeze receipts; successor projection pending.** PR #131 landed and U11 projections were frozen for ALPHA, BETA, and GAMMA. | Re-project and bind the identities during the one ruled successor-family re-freeze. | Lead | PR #131 (`14879e4`); freeze log; three `freeze-0001.json` receipts. |
| Receipt-oracle freshness | **PASS in the 2026-08-13 freeze receipts; successor derivation pending.** The replay-derived oracle remained byte-identical after PR #122. | Re-derive if the final ledger read/write surface changes and bind the result at successor freeze. | Lead | PR #125; the receipt-oracle row in the three freeze receipts. |
| Three-window regression | **PASS in the 2026-08-13 freeze receipts; successor replay pending.** The current committed ALPHA receipt records `freeze-three-window-regression-v1` as passing evidence. | Re-run and bind the regression against the final successor family and reviewed head. | Lead | The three-window-regression row in the three `freeze-0001.json` receipts. |
| Successor-family lifecycle | **PHASE-0 RULINGS COMPLETE; Phase-2 execution pending.** The council ruled content-bound evidence and `FROZEN_PLAN`, then ordered one atomic successor-family re-freeze after Phase 1. | Finish Phase 1, then re-freeze the family once under the ruled route. | Lead + Ed for the irreversible freeze | Council verdict, Phases 0 and 2. |
| Reason-code plumbing | **IMPLEMENTED; final successor rehearsal pending.** The prior freeze receipt passed the row, and #152 added the T-0 acquisition refusal vocabulary. | Verify registry coverage and emitted refusal fields at the final successor rehearsal. | Lead | PR #116; PR #152; the reason-code-plumbing receipt row. |
| ALPHA campaign pack and extraction specification | **FROZEN/PASS at `49dcc49`, but not selectable and due for successor re-freeze.** | Complete Phase 1 and the ruled atomic re-freeze; then pass the re-audit and READY-candidate council. | Lead | ALPHA `freeze-0001.json`; `WINDOW-COUNCIL-GATE`; council verdict. |
| BETA and GAMMA pack family | **FROZEN/PASS at `49dcc49`, but not selectable and due for successor re-freeze.** | Freeze all three successor packs together, then complete the governed re-audit and council sequence. | Lead | BETA/GAMMA `freeze-0001.json`; council verdict. |
| Frozen readiness validator and record | **PRIOR PASS; successor record pending.** The three freeze receipts passed and `dry-run-0001` passed all four hash-bound checks at `49dcc49`. | Generate and rehearse the successor receipts against the final exact head. | Lead | Freeze log; `dryrun-alpha.json`; three `freeze-0001.json` receipts. |
| Reviewed measurement checkout | **OLD CHECKOUT CLEAN BUT STALE.** `/Users/edr/JouleWise-measurement-20260813` is clean at `49dcc49`, not post-#152 main, and cannot be the final reviewed checkout. | Create or advance a separate clean checkout only after all blocking work and the successor re-freeze settle the exact head. | Lead | Read-only `git status`/`rev-parse` of the measurement checkout; PR #152. |
| Terminal merge review | **PENDING final successor head.** #152 received D-121 review, but consumption-edge, launch-binding, detect-pulse-budget, and other council obligations remain. | Complete the remaining work, then review the exact final head last; any later fix repeats the gate. | Lead | `RUN_STATE.md` T8 successor order; D-121. |

- **#150 (`47d2645`)** installed the live `WINDOW-COUNCIL-GATE`; no
  quiet-machine task is selectable after the NOT-READY verdict.
- **#151 (`00ec3b7`)** authorized the margin recorder's narrow governed
  vocabulary; its separate grant-identity race remains a registered future
  work order and does not alter the current council gate.
- **#152 (`a61ac92`)** landed the nine-input T-0 capture tool, strict R2 plan
  resolver, D-127 network-time route, and refusal vocabulary. It produces no
  current T-0 evidence by being merged.
- **Current Phase-1 blockers** include the consumption edge, launch binding,
  detection-pulse budget, L2 re-audit, and census repair after operator evidence.
  Closing them still does not itself entitle READY; the ordered Phase 2-4
  re-freeze, re-audit, and READY-candidate sitting remain mandatory.

## Freeze-evaluable rows

These rows are evaluated at freeze and again at arm. Only two registered
conditional rules permit `NOT_APPLICABLE`: successor acceptance while the
issued acceptance artifact remains selected, and the four helper-installation
rows when the manual clock route is used. Every other row is required.

| Stable row ID | Checkpoint status and physical meaning |
|---|---|
| `clock.restore_recipe` | **PRIOR PASS; successor recheck required.** ALPHA `freeze-0001` records `freeze-doctrine-pin-v1` as passing; #152 landed the D-127 route that must be bound into the successor procedure. |
| `desk.acceptance_owner` | **PRIOR PASS; successor recheck required.** ALPHA `freeze-0001` passed after PR #142 removed the copied scalar and bound the authenticated owner value. |
| `desk.acceptance_successor` | **NOT_APPLICABLE in the prior receipt.** The issued artifact remained selected; any selected successor must carry its own authenticated pass before member one. |
| `desk.arming_procedure` | **PRIOR PASS; successor recheck required.** The old receipt and dry run passed, but #152 changed the runbook/T-0 route and the new exact-head rehearsal is pending. |
| `desk.current_pack` | **PRIOR PASS; successor re-freeze required.** The current committed ALPHA receipt passed at `49dcc49`; the council ordered one later atomic family re-freeze. |
| `desk.estimator_identity` | **PRIOR PASS; selector remains registered.** Six floor-pack shared-edge comparative cells select `d124_two_shared_edge_common_mode.v1`; the successor pack must preserve and rebind it. |
| `desk.identity_pin_projection` | **PRIOR PASS.** U11 projections are frozen in all three receipts; the successor family requires fresh projections bound to its bytes. |
| `desk.mint_trust` | **PRIOR PASS; D-130 condition now closed.** The prior receipt passed, and #129 plus hosted runs `31541829071`/`31518739878` discharged the temporary venue condition. |
| `desk.multicell_mint` | **PRIOR PASS.** The receipt passed this row and #140 supplies the governed estimator vocabulary; verify again at the successor head. |
| `desk.pack_family` | **PRIOR PASS for all three packs; successor family pending.** The three receipts passed against `49dcc49`; Phase 2 requires a new atomic family freeze. |
| `desk.reason_code_plumbing` | **PRIOR PASS; successor replay required.** The old row passed and #152 added T-0 acquisition refusals that must be covered at the final rehearsal. |
| `desk.receipt_oracle` | **PRIOR PASS; successor derivation check required.** The replay-derived oracle passed in all three receipts. |
| `desk.recovery_ledger_path` | **PRIOR PASS; successor replay required.** PR #118's path passed at freeze; #152's strict resolver and clock route must pass at the final head. |
| `desk.three_window_regression` | **PRIOR PASS; successor replay required.** All three receipts record `freeze-three-window-regression-v1` as passing evidence. |

## Arm-only rows

These facts cannot be stamped at freeze. Missing or stale live evidence means
`REFUSE`, never an operator-entered “unknown” machine value.

| Stable row ID | Checkpoint status and physical meaning |
|---|---|
| `clock.correct_and_prior_state` | **LIVE EVIDENCE PENDING.** #152 supplies the capture step and D-127 route; Ed must still provide the independent-clock observation and the tool must capture prior automatic-time state at T-0. |
| `clock.network_time_off` | **LIVE EVIDENCE PENDING.** #152 can capture the governed command result, but the fresh probe has not run for a successor attempt. |
| `desk.reviewed_checkout` | **PENDING.** The old checkout is clean at `49dcc49`, not current main; the final checkout must match local main and origin/main with no tracked or untracked changes. |
| `desk.terminal_review` | **PENDING.** #152 was reviewed at its final head, but the full Phase-1/Phase-2 successor head does not yet exist. |
| `desk.under_lease_rehearsal` | **PRIOR PASS ONLY.** `dry-run-0001` passed at `49dcc49`; the council-ordered full dress rehearsal against the successor pack remains pending and cannot itself authorize arming. |
| `privilege.activation_fence` | **IMPLEMENTATION LANDED; OPERATOR EVIDENCE PENDING.** #152 stages the D-127 helper route; installation and the separate Ed-visible activation exercise remain in the batched qualification session. |
| `privilege.fresh_authorization` | **IMPLEMENTATION LANDED; OPERATOR EVIDENCE PENDING.** The reviewed `sudo -k` and fresh-authorization sequence has not been exercised for the successor attempt. |
| `privilege.installed_bytes` | **STAGED BY #152; INSTALL EVIDENCE PENDING.** Installed bytes must equal the reviewed `scripts/joulewise-network-time.sudoers` digest. |
| `privilege.isolated_interpreter` | **ROUTE LANDED; LIVE PROOF PENDING.** The installed helper must still prove isolated-interpreter operation; manual-route `NOT_APPLICABLE` remains governed by the registry. |
| `t0.background_quiet` | **LIVE EVIDENCE PENDING.** #152 supplies the capture producer, but the real quiet-state census and the council's census-semantics repair are not complete. |
| `t0.campaign_lock_absent` | **LIVE EVIDENCE PENDING.** The producer exists; no successor-attempt lock census has been captured. |
| `t0.display_thermal_idle` | **LIVE EVIDENCE PENDING.** The producer exists, but the completed wait, thermal/display state, and operator-visual keyboard-backlight evidence must be fresh. |
| `t0.fresh_roots_waivers` | **LIVE EVIDENCE PENDING.** #152 captures and binds the inputs; successor custody roots and the exact empty waiver bytes do not yet exist. |
| `t0.ledger_reservation` | **CODE PATH LANDED; POSITIVE REHEARSAL BLOCKED ON SUCCESSOR PACK.** #152 landed the strict R2 resolver; ALPHA/BETA generator `--plan` reconciliation is assigned to the atomic successor freeze before live reservation evidence can pass. |
| `t0.machine_readiness` | **LIVE EVIDENCE PENDING.** The machine check and capture route exist, but they must run against the successor pack after the council gate clears; `READY` never licenses arming. |
| `t0.no_stray_keepawake` | **LIVE EVIDENCE PENDING.** Any earlier observation is expired; the fresh census must follow the repaired census semantics. |
| `t0.offline_inputs` | **LIVE EVIDENCE PENDING.** The final model, tokenizer, configuration, scripts, and environment must match frozen local inputs without a network fetch. |
| `t0.passwordless_powermetrics` | **OPERATOR QUALIFICATION PENDING.** The D-127 route landed in #152; Ed must install/exercise it and the exact passwordless measurement probe must exit zero. |
| `t0.power_path` | **LIVE EVIDENCE PENDING.** Supply, cable, external AC, power negotiation, `ac_high_power`, and low-power-mode state must be captured for the attempt. |
| `t0.single_launch_capability` | **BLOCKED ON WO-LAUNCH-BINDING.** The one-shot capability exists conceptually, but consumption is not yet bound to immediate frozen-chain execution and downstream authenticated lineage. |
| `t0.storage_backup_capacity` | **LIVE EVIDENCE PENDING.** The attempt still requires at least 20 GB free and two distinct writable destinations with the frozen capacity. |

Any refusal ends the attempt before launch. Preserve the authenticated evidence
and send the exact closed refusal code to the lead.
