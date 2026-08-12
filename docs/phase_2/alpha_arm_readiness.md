# Window ALPHA arm readiness — GO / NO-GO

<!-- Standing rule (D-1 recurrence class, 3rd occurrence 2026-08-12): any
checkpoint re-anchor of this document MUST resweep every gate row's status
cell against main in the same commit — a banner-only re-anchor is the defect,
not a smaller version of the fix. -->

**Checkpoint:** T4-late, 2026-08-11 (supersedes the earlier T4, T3 and T1
lines. Recovery merged — PR #118, 2026-08-09. Mint trust merged — PR #122,
2026-08-11. D-133 cold-gate disposition — 2026-08-11.)

**Current verdict: NO-GO. Do not arm Window ALPHA.** Both merge-event
blockers have cleared, and D-133 resolved the estimator question for this
cycle: this fallback branch re-specs all packs to the worst-case default
estimator and pack freezing is NO LONGER barred by the estimator (freeze-plan
Q7 resolved by reversal; FCM-01 continues only as a non-freeze-gating desk
thread per D-133). Remaining NO-GO grounds: the U11 identity-pin projection
tool is implemented but not yet merged (PR #131 in gates); the Ed-funded Q8
p256 prefill floor cells are unbuilt; and neither the packs nor the
generated plan-specific arm-readiness records required by run-book §5C are
frozen.

Window **ALPHA** is the first prospective D-117 night: the 1.5B decode floor
with prefill floor cells. **Lead** means the project lead. **Merge event**
means the named change has passed all review, continuous-integration, and
terminal lead-review gates and has landed on `main`. A **receipt oracle** is
the frozen expected receipt count and order used to check a calibration
ledger session.

This page is a decision aid. The collection procedure remains the
[Quiet-Mac Claim-Window Run-Book](window_runbook.md); this page does not
replace or amend it.

This page is **not** the §5C plan-specific arm-readiness record. That record
is a per-plan artifact generated at pack freeze, named by path and SHA-256 in
the frozen plan, and carrying a stamped verdict for every applicable row
below. This page supplies the row set and reasoning; the generated record
supplies the binding stamps.

## Desk gates — all must be green before Ed starts the night

| Gate | Status (T4, 2026-08-11) | What makes it green | Who acts | Source |
|---|---|---|---|---|
| Recovery and calibration-ledger arming path | **GO — merge event complete.** PR #118 merged 2026-08-09. The ruled G2/G4/G6 production fixes, executed probes, scoped delta, lead replay, integration check, CI, and D-121 terminal review all completed. | Preserve the merged behavior and re-run its required checks at the final reviewed measurement head. | Lead | PR #118; recovery cold-gate ruling; D-121. |
| Manual arming and recovery procedure | **GO for the document; PENDING for its live verification.** The D-117 manual arming procedure landed with PR #118: `window_runbook.md` §5C plus the §5, §6, and §10 D-117 amendments, including the recovery refusal flow. What remains is the §5C lead live verification: the lead personally runs the frozen readiness-validator command and complete under-lease synthetic rehearsal on the reviewed measurement checkout. That is desk work on a landed procedure, not a missing document. | Complete and record the non-delegable §5C lead live verification on the exact reviewed measurement checkout. | Lead | PR #118; `window_runbook.md` §5C and the §5, §6, and §10 D-117 amendments. |
| Mint trust bar | **GO — merge event complete.** PR #122 merged 2026-08-11 at `ae6af48` under the D-130 decisive-venue ruling; the 16-question relocation delta answered 16/16. Citation discipline per D-130 remains in force until the hosted-green condition closes. | Preserve the merged trust behavior and D-130 citation discipline at the final reviewed head. | Lead | PR #122 (`ae6af48`); `docs/decision_log.md`, D-130. |
| Writer uses the authenticated acceptance value | **NO-GO.** The copied-scalar removal was queued, not landed. | Land the writer change that reads the authenticated active acceptance artifact instead of a copied constant. | Lead, then merge event | `docs/strategy/2026-08-08-40h-plan.md`, Phase A item A3. |
| Multi-cell mint and pin vocabulary | **GO at T1 for the merged base, but must survive the final integration head.** The D-117 U3 unit was already merged. | Re-run its focused and integration checks at the final reviewed head; do not arm if the vocabulary or pins drift. | Lead | `RUN_STATE.md`, “STATE IN ONE BREATH” (U1/U3/U4 merged); D-117 clause 7. |
| Common-mode contrast estimator identity | **NOT A FREEZE BLOCKER as of D-133 (2026-08-11); the green condition FIRED 2026-08-12.** Round 5's delta found an exact understatement, the pre-committed stopping rule executed, and the cold gate decoupled the estimator from the freeze: the fallback re-spec branch (`respec/d124-withdrawn`, PR #132) **merged 2026-08-12 as `2b43de8`** — packs freeze on the worst-case default estimator, freeze-plan Q7 is resolved by reversal, and FCM-01 may not gate the freeze lane thereafter. FCM-01 continues as an unmerged, non-gating desk thread under ALT-D120 (its full fresh delta cleared the moved arithmetic terminally — zero exact understatements in 4,096 rational cases). Re-spec back to the tighter estimator only if ALT-D120 + that delta + WO-MINT-ESTIMATOR-VOCAB all land before the freeze wave (D-133 clause 4). | Nothing — the `respec/d124-withdrawn` merge satisfied it. Preserve the default-estimator pack state through the freeze. | Lead | `docs/decision_log.md`, D-133 (`f0e7cf6`); PR #132 (`2b43de8`); freeze-plan Q7. |
| Arm-time identity-pin projection | **NO-GO — implemented and gauntlet-complete, merge in flight.** The U11 projector is built on `impl/u11-idpin-projection` (PR #131): `joulewise/identity_pins.py`, `scripts/project_identity_pins.py`, `tests/test_identity_pins.py`, all three packs re-emitting `identity_pin_projection` in the `state: "unprojected"` shape. Four fix rounds landed; the final delta returned ACCEPT; the decision-index ordering defect was fixed on-branch (`37a6e98`); the branch was merged with post-#132 main (`0415f37`, generators regenerated, plan tests green). Awaiting CI green + the D-121 terminal review, then the projected receipts freeze into the ALPHA pack. | PR #131 through CI + D-121, then freeze the projected receipts into the ALPHA pack (a §5C consumer, per D-134, must land before any arm). | Lead, then merge event | PR #131; D-131 (lands with that merge); D-134; 40-hour plan A5 / Phase B B2. |
| Receipt-oracle freshness | **GO, conditionally.** PR #125 merged 2026-08-10: `joulewise/receipt_oracle.py` plus replay-derived oracles in all three packs (10 physical receipts / 5 logical operations per finalized bracket session), derived from the authenticated merged head rather than hand-authored literals. **2026-08-11 determination: the conditional FIRED (PR #122 added custody-projection read surface to `joulewise/calibration_ledger.py` after derivation) and was evaluated — NO-REDERIVATION-NEEDED at `c61f840`: main-head replay produced 3,172 canonical bytes, SHA-256 `088bab77a7843d82e6485df2840d304f2fdf8ecf372006049c60e37367f491c0`, byte-identical to the `524a0ed` oracle and all three committed pack oracles; the new read projection does not alter the oracle's selected derivation path (Sol xhigh executed evaluation, T4-late).** | Re-derive if any later merge changes the ledger read or write surface; otherwise preserve the merged oracle in the frozen packs. | Lead | PR #125; `joulewise/receipt_oracle.py`; 40-hour plan B1. |
| Three-window regression | **NO-GO / UNVERIFIED for the final cadence.** The U4 unit merged (PR #113), and `tests/test_calibration_live_three_window.py` was subsequently touched by the recovery series itself (`4495609`). No separate 40h-B3 amendment commit exists for dispositions 1–6 against the landed cadence, and none has been verified. | Run the amended synthetic ALPHA/BETA/GAMMA ledger regression against merged recovery behavior. | Lead | PR #113; `4495609`; 40-hour plan B3. |
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

| Gate | Status (T4, 2026-08-11) | What makes it green | Who acts | Source |
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

| Gate | Status (T4, 2026-08-11) | What makes it green | Who acts | Source |
|---|---|---|---|---|
| No **stray** keep-awake process (`caffeinate` included) — the one reviewed launch is itself `caffeinate` | **GO at the T1 checkpoint, but that observation expires before arm.** T1 says nothing was in flight and the session’s `caffeinate` ended. | At T-0, inspect a new final census and stop every unrelated `caffeinate`, agent, browser, automation, monitor, watcher, tail, campaign, or other poller. Before launch, `pgrep -x caffeinate` must return nothing and exit 1. The reviewed launch (`caffeinate -is /bin/zsh …`, run-book §6) starts afterward, so exactly one `caffeinate` then exists as the chain's parent. The window is **stray-caffeinate-free, wrapped in one reviewed `caffeinate`**; never describe it as “caffeinate-free” in operator-facing text. | Ed | `RUN_STATE.md` T1 opening and prior checkpoint close; `window_runbook.md` §§1, 5, and 6. |
| Approved power path | **UNKNOWN.** | Confirm the approved 140 W supply and cable, external AC, 140 W negotiation, `ac_high_power`, and low-power mode off; do not change them. | Ed | Three-night packet, ALPHA arm sequence; `window_runbook.md` §5. |
| Background maintenance is quiet | **UNKNOWN.** | Finish or pause Time Machine, updates, indexing, downloads, and cloud uploads; record the final census. | Ed | Three-night packet, ALPHA arm sequence; `window_runbook.md` §5. |
| Display, screensaver, thermal state, and idle drain | **UNKNOWN.** | Pass `quiet_mac_prep.sh`; require displays asleep, screensaver disengaged, nominal thermal pressure, then leave the Mac untouched for at least ten minutes. | Ed | `window_runbook.md` §§5 and 7. |
| Passwordless measurement access | **UNKNOWN.** | Prove `sudo -n /usr/bin/powermetrics ...` succeeds before the final settle. | Ed | `window_runbook.md` §5. |
| Offline inputs | **UNKNOWN.** | Load the pinned model, tokenizer, configurations, scripts, and virtual environment locally without downloads. | Lead prepares; Ed confirms record | Three-night packet, ALPHA preparation. |
| Storage and backup capacity | **UNKNOWN.** | Record at least 20 GB free and enough capacity at both separate backup destinations. | Ed | Three-night packet, ALPHA preparation. |
| Fresh absolute roots and empty waiver list | **UNKNOWN until pack freeze and T-0.** | Use named absolute claim, bound, custody, quarantine, and backup paths; prove claim and bound roots are fresh and `waivers.json` is exactly `[]`. | Lead freezes; Ed verifies | Three-night packet, ALPHA preparation; `window_runbook.md` §4. |
| No live or stale campaign lock | **UNKNOWN until T-0.** | Prove `campaign.lock` is absent. If present, check its process ID; stop for a live owner and quarantine a proven dead lock. Never delete an unreadable lock blindly. | Ed | Three-night packet hard gates; `window_runbook.md` §10. |
| **Pre-window machine-readiness command** (not an arming gate) | **NO-GO until every row above is green.** | Run the frozen `bash scripts/prewindow_check.sh --wait --timeout-min <frozen> --window <frozen ALPHA label>` and require `READY`. This covers machine quietness only — contaminating daemons, load, power and clock state, runs roots, disk headroom, and active processes. It is **not** the arming gate and cannot substitute for one. The calibration-ledger gate is separate and mandatory: run-book §5C step 2 requires the §6 diagnostic-readiness command **and** the reservation command with `--execute`. No word emitted by either surface — `READY`, `ready`, or `clean` — licenses arming. | Ed | `window_runbook.md` §5C step 2; `scripts/prewindow_check.sh` header; three-night packet arm sequence. |
| Single foreground launch | **NOT YET ARMED.** | Launch exactly once from the ordinary foreground shell using the absolute frozen plan root. Do not kill a running verdict, even if it takes more than two minutes. | Ed | Three-night packet hard gates and ALPHA arm sequence; `window_runbook.md` §6. |

**Arm rule:** Ed may arm only when every applicable row above reads **GO**
and the final readiness command returns `READY`. Any **NO-GO** or **UNKNOWN**
ends the attempt before launch; preserve evidence and send the exact refusal
to the lead.
