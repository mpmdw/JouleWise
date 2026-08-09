# Window ALPHA arm readiness — GO / NO-GO

**Checkpoint:** T1, 2026-08-08 night.

**Current verdict: NO-GO. Do not arm Window ALPHA.** Recovery has not
merged, the mint trust change has not merged, the receipt counts used by the
packs are stale, and the packs and readiness record are not frozen.

Window **ALPHA** is the first prospective D-117 night: the 1.5B decode floor
with prefill floor cells. **Lead** means the project lead. **Merge event**
means the named change has passed all review, continuous-integration, and
terminal lead-review gates and has landed on `main`. A **receipt oracle** is
the frozen expected receipt count and order used to check a calibration
ledger session.

This page is a decision aid. The collection procedure remains the
[Quiet-Mac Claim-Window Run-Book](window_runbook.md); this page does not
replace or amend it.

## Desk gates — all must be green before Ed starts the night

| Gate | T1 status | What makes it green | Who acts | Source |
|---|---|---|---|---|
| Recovery and calibration-ledger arming path | **NO-GO.** The ruled G2/G4/G6 fix round had not started and branch `impl/d117-ledger-recovery` was at `e265c9c`. | Land the three ruled production fixes with executed probes; run the scoped delta, lead replay, integration check, pull-request checks, and terminal review; merge to `main`. | Lead, then merge event | `RUN_STATE.md`, “T1 SESSION FINAL CHECKPOINT,” item 1; recovery cold-gate ruling named there. |
| Manual arming and recovery procedure | **NO-GO.** The recovery cold gate requires a D-117 run-book amendment and documented manual procedure. The reference run-book has neither a D-117 manual procedure nor the cold gate’s new recovery refusal flow. | Lead writes and live-verifies the manual procedure, then lands it with the recovery unit. The procedure must tell Ed exactly how to arm, refuse, preserve, and recover. | Lead | Recovery cold-gate ruling §2(b), cited by `RUN_STATE.md` T1 item 1; current `window_runbook.md` §§5–6 and §10. |
| Mint trust bar | **NO-GO.** Trust round 2c ran, but the work was uncommitted and branch `impl/d117-postcollection-trust` remained unmerged. | Lead harvests and verifies the proofs, publishes the reviewed fixture release, completes the ruled history rewrite and 16-question delta, then passes the pull-request and terminal review gates and merges. | Lead, then merge event | `RUN_STATE.md`, T1 item 2. |
| Writer uses the authenticated acceptance value | **NO-GO.** The copied-scalar removal was queued, not landed. | Land the writer change that reads the authenticated active acceptance artifact instead of a copied constant. | Lead, then merge event | `docs/strategy/2026-08-08-40h-plan.md`, Phase A item A3. |
| Multi-cell mint and pin vocabulary | **GO at T1 for the merged base, but must survive the final integration head.** The D-117 U3 unit was already merged. | Re-run its focused and integration checks at the final reviewed head; do not arm if the vocabulary or pins drift. | Lead | `RUN_STATE.md`, “STATE IN ONE BREATH” (U1/U3/U4 merged); D-117 clause 7. |
| Common-mode contrast estimator identity | **NO-GO for pack freeze.** The D-124/D-125 estimator implementation was queued after trust. | Merge the two-shared-edge implementation and its registration conditions before any pack hash freezes. | Lead, then merge event | D-124; D-125 clause 1; 40-hour plan A4. |
| Arm-time identity-pin projection | **NO-GO.** The projection tool was queued after trust. | Merge the projection tool and freeze its receipts into the ALPHA pack. | Lead, then merge event | `RUN_STATE.md` T1 continuation notes; 40-hour plan A5 and Phase B B2. |
| Receipt-oracle freshness | **NO-GO.** Recovery changes five logical operations to ten physical records; the old “5-receipt/91” expectations are stale. | Re-derive counts and order from the merged recovery behavior, using derived counts rather than positional constants. Freeze the new oracle into the pack. | Lead | `RUN_STATE.md`, receipt-cadence note and successor queue; 40-hour plan B1. |
| Three-window regression | **NO-GO for the final cadence.** The older U4 unit merged, but the landed recovery cadence requires U4 amendments. | Run the amended synthetic ALPHA/BETA/GAMMA ledger regression against the merged recovery behavior. | Lead | `RUN_STATE.md` T1 continuation; 40-hour plan B3. |
| Successor-engine cold gate | **NOT AN ALPHA ARM BLOCKER under the newer authority.** It remains frozen at count 3 for a post-window cold gate; the issued D-079 artifact governs these windows. | Keep the frozen work out of the night path; resolve it post-window without changing the issued artifact used by ALPHA. | Lead | `RUN_STATE.md` T1 item 3; D-126; 40-hour plan A6. The packet’s older “U2 before night 1” line is superseded here. |
| Reason-code plumbing | **GO for the three-night code path.** The code lane is on `main`; the separate specification-governance lane remains open. | Confirm the emitted refusal field is present in the final pack rehearsal. Do not treat the open specification lane as permission to change refusal meanings at night. | Lead | `RUN_STATE.md`, D-121-era reason-code block (PR #116 merged). |
| ALPHA campaign pack and extraction specification | **NO-GO.** U5 was not generated or hash-frozen at T1. | Generate the D-117 ALPHA pack after recovery lands; include decode and prefill floor cells, reported-energy cells only if the byte-identity check passes, stage-launch recipes, exact roots, failure policy, hashes, and the fresh receipt oracle. | Lead | `RUN_STATE.md` successor queue; D-117 clauses 2, 3, and 7; D-123 clause 1; 40-hour plan B2. |
| BETA and GAMMA pack family | **NO-GO.** U5–U7 were unfrozen. They are a family because their identities and later floor transport interlock. | Freeze all three packs against the same reviewed head. GAMMA must include the D-122 256-token prefill arm and the D-125 estimator identity. | Lead | `RUN_STATE.md` successor queue; D-122; D-125; 40-hour plan B2. |
| Frozen readiness validator and record | **NO-GO.** The packet requires it, but Phase B had not been reached at T1. | Generate the record, run the validator with no warning or exception, and rehearse the under-lease gate end to end on a synthetic root. | Lead | Three-night packet, “HARD GATES before night 1”; 40-hour plan B5. |
| Reviewed measurement checkout | **NO-GO until the blocking merges finish.** T1 recorded clean `main`, but that head does not contain the required recovery and trust merges. | After every blocking merge, create a separate clean measurement checkout at the exact reviewed `main` commit and record its hash. | Lead, then merge event | `RUN_STATE.md`, T1 items 1–2 and Known Workspace State; `window_runbook.md` §1. |
| Terminal merge review | **NO-GO while any required unit is unmerged.** | For every merge candidate, complete all earlier checks and continuous integration, then have the context-holding lead review the exact final head last. Any later fix repeats the gate. | Lead | D-121. |

## Privileged setup and clock gates

The D-115 installation capability applies if the reviewed quiet-guard or
autonomous network-time helper is used. It does not license general root
access. Manual §5A operation remains Ed’s path unless the later capability is
separately installed and activated.

| Gate | T1 status | What makes it green | Who acts | Source |
|---|---|---|---|---|
| Fresh administrator authorization | **UNKNOWN.** It can only be observed at installation time. | Run `sudo -k`, then obtain fresh interactive authorization for the one reviewed install command. | Ed | D-115 clause 2(a); D-127 clause 3. |
| Installed bytes are authenticated | **UNKNOWN.** T1 does not record a completed install. | Match every staged artifact to its pinned reviewed digest before root-owned installation. | Ed verifies; lead supplies reviewed digests | D-115 clause 2(b). |
| Helper interpreter is isolated | **UNKNOWN.** T1 does not record a completed install. | Verify genuine isolated execution: no site initialization, user site, or environment hooks. | Lead verifies; Ed installs | D-115 clause 2(c). |
| Installed capability remains inactive until the Ed-visible activation step | **UNKNOWN / NOT REQUIRED for the manual ALPHA route.** | If automation is used, prove the installed state is inactive first, then perform the separately reviewed Ed-visible activation. Otherwise use manual §5A. | Ed and lead | D-115 clause 3; D-127 clauses 3–5. |
| Clock is correct and the prior network-time state is recorded | **UNKNOWN until T-0.** | Compare against an independent trusted source, correct if needed, and record `systemsetup -getusingnetworktime`. | Ed | `window_runbook.md` §5A. |
| Automatic network time is off and the machine has settled | **UNKNOWN until T-0.** | Run the reviewed manual or installed fixed command to turn network time off, record the time, then leave the machine untouched for the frozen settle period. | Ed | `window_runbook.md` §5A; D-127 clause 3 if automation is used. |
| Restore procedure is ready | **UNKNOWN until the final packet freezes.** | The frozen close-out must turn network time on only after `measurement_complete`, the verdict, and both backups, and must verify the restored state. | Lead freezes; Ed executes | `window_runbook.md` §5A; three-night packet, ALPHA close-out. |

## T-0 quiet-machine gates

All of these are live observations. T1 cannot make them green in advance;
**UNKNOWN means NO-GO at the machine until Ed records a pass.**

| Gate | T1 status | What makes it green | Who acts | Source |
|---|---|---|---|---|
| No stray keep-awake process, including `caffeinate` | **GO at the T1 checkpoint, but that observation expires before arm.** T1 says nothing was in flight and the session’s `caffeinate` ended. | At T-0, inspect a new final census and stop every unrelated `caffeinate`, agent, browser, automation, monitor, watcher, tail, campaign, or other poller. Only the one reviewed foreground launch may start afterward. | Ed | `RUN_STATE.md` T1 opening and prior checkpoint close; `window_runbook.md` §§1 and 5. |
| Approved power path | **UNKNOWN.** | Confirm the approved 140 W supply and cable, external AC, 140 W negotiation, `ac_high_power`, and low-power mode off; do not change them. | Ed | Three-night packet, ALPHA arm sequence; `window_runbook.md` §5. |
| Background maintenance is quiet | **UNKNOWN.** | Finish or pause Time Machine, updates, indexing, downloads, and cloud uploads; record the final census. | Ed | Three-night packet, ALPHA arm sequence; `window_runbook.md` §5. |
| Display, screensaver, thermal state, and idle drain | **UNKNOWN.** | Pass `quiet_mac_prep.sh`; require displays asleep, screensaver disengaged, nominal thermal pressure, then leave the Mac untouched for at least ten minutes. | Ed | `window_runbook.md` §§5 and 7. |
| Passwordless measurement access | **UNKNOWN.** | Prove `sudo -n /usr/bin/powermetrics ...` succeeds before the final settle. | Ed | `window_runbook.md` §5. |
| Offline inputs | **UNKNOWN.** | Load the pinned model, tokenizer, configurations, scripts, and virtual environment locally without downloads. | Lead prepares; Ed confirms record | Three-night packet, ALPHA preparation. |
| Storage and backup capacity | **UNKNOWN.** | Record at least 20 GB free and enough capacity at both separate backup destinations. | Ed | Three-night packet, ALPHA preparation. |
| Fresh absolute roots and empty waiver list | **UNKNOWN until pack freeze and T-0.** | Use named absolute claim, bound, custody, quarantine, and backup paths; prove claim and bound roots are fresh and `waivers.json` is exactly `[]`. | Lead freezes; Ed verifies | Three-night packet, ALPHA preparation; `window_runbook.md` §4. |
| No live or stale campaign lock | **UNKNOWN until T-0.** | Prove `campaign.lock` is absent. If present, check its process ID; stop for a live owner and quarantine a proven dead lock. Never delete an unreadable lock blindly. | Ed | Three-night packet hard gates; `window_runbook.md` §10. |
| Final readiness command | **NO-GO until every row above is green.** | Run the frozen readiness command with the frozen timeout and ALPHA label; require `READY` with no warning or exception. | Ed | Three-night packet, ALPHA arm sequence. |
| Single foreground launch | **NOT YET ARMED.** | Launch exactly once from the ordinary foreground shell using the absolute frozen plan root. Do not kill a running verdict, even if it takes more than two minutes. | Ed | Three-night packet hard gates and ALPHA arm sequence; `window_runbook.md` §6. |

**Arm rule:** Ed may arm only when every applicable row above reads **GO**
and the final readiness command returns `READY`. Any **NO-GO** or **UNKNOWN**
ends the attempt before launch; preserve evidence and send the exact refusal
to the lead.
