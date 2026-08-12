# Window ALPHA arm readiness — checked human view

<!-- Standing rule (D-1 recurrence class, 3rd occurrence 2026-08-12): any
checkpoint re-anchor of this document MUST resweep every gate row's status
cell against main in the same commit — a banner-only re-anchor is the defect,
not a smaller version of the fix. -->

**Checkpoint:** T4-late, 2026-08-11 (supersedes the earlier T4, T3 and T1
lines. Recovery merged — PR #118, 2026-08-09. Mint trust merged — PR #122,
2026-08-11. D-133 cold-gate disposition — 2026-08-11.) **Current verdict:
NO-GO. Do not arm Window ALPHA.**

Window ALPHA is the first prospective D-117 night: the Qwen2.5 1.5B decode
floor with prefill floor cells. The authoritative row set is
`configs/arm_readiness/d117_row_registry_v1.json`; this page is a checked,
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

Each readiness receipt carries a boot-session identifier. If the Mac reboots
between freeze and arm, verification automatically rejects receipts from the
earlier boot session and requires new verification.

The collection procedure remains the
[Quiet-Mac Claim-Window Run-Book](window_runbook.md). This page does not
replace it.

## Preserved checkpoint facts

At the current T4-late checkpoint, the D-131 identity-pin projection was
implemented but still in PR #131, the Ed-funded Q8 work item's 256-token
prefill floor cells were unbuilt, and the packs and plan-specific readiness
receipts were not frozen. These and the facts below are dated status facts, not
present-tense evidence of a pass. T1 means the earlier checkpoint named T1 in
the campaign record.

### Legacy T4 checklist view (preserved chronology)

The following origin/main rows are retained intact as the dated pre-D-134
checklist view. They do not replace the stable-ID registry view below and do
not authorize arming.

| Gate | Status (T4, 2026-08-11) | What makes it green | Who acts | Source |
|---|---|---|---|---|
| Recovery and calibration-ledger arming path | **GO — merge event complete.** PR #118 merged 2026-08-09. The ruled G2/G4/G6 production fixes, executed probes, scoped delta, lead replay, integration check, CI, and D-121 terminal review all completed. | Preserve the merged behavior and re-run its required checks at the final reviewed measurement head. | Lead | PR #118; recovery cold-gate ruling; D-121. |
| Manual arming and recovery procedure | **GO for the document; PENDING for its live verification.** The D-117 manual arming procedure landed with PR #118: `window_runbook.md` §5C plus the §5, §6, and §10 D-117 amendments, including the recovery refusal flow. What remains is the §5C lead live verification: the lead personally runs the frozen readiness-validator command and complete under-lease synthetic rehearsal on the reviewed measurement checkout. That is desk work on a landed procedure, not a missing document. | Complete and record the non-delegable §5C lead live verification on the exact reviewed measurement checkout. | Lead | PR #118; `window_runbook.md` §5C and the §5, §6, and §10 D-117 amendments. |
| Mint trust bar | **GO — merge event complete.** PR #122 merged 2026-08-11 at `ae6af48` under the D-130 decisive-venue ruling; the 16-question relocation delta answered 16/16. Citation discipline per D-130 remains in force until the hosted-green condition closes. | Preserve the merged trust behavior and D-130 citation discipline at the final reviewed head. | Lead | PR #122 (`ae6af48`); `docs/decision_log.md`, D-130. |
| Writer uses the authenticated acceptance value | **GO** (2026-08-12, PR #142 merged 5be400e). The writer authenticates the issued acceptance artifact (byte-pinned sha) and derives the comparator under the artifact's own rounding rule with a three-way consistency check; six named fail-closed refusals before MLX import/lease/custody; derived value verified bit-identical to the deleted literal at the merge gate. | — | Discharged | PR #142 D-121 comment; `docs/strategy/2026-08-08-40h-plan.md` Phase A item A3. |
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

- **Historical — PR #118:** The ruled fixes, executed probes, scoped delta,
  lead replay, integration check, continuous integration, and terminal lead
  review all completed. Their required checks must run again at the final
  measurement commit.
- **Historical — procedure verdict:** The procedure document itself had a
  `GO` verdict; only its non-delegable live verification was pending. The merge
  included runbook sections 5, 5C, 6, and 10 and the recovery-refusal flow.
- **Historical merge fact; condition still active — PR #122:** Mint trust
  merged at `ae6af48` on 2026-08-11 under D-130, and its 16-question relocation
  delta answered 16/16. The citation-discipline condition remains active until
  the hosted-green condition closes.
- **Current relationship — estimator:** D-133 returned this pack cycle to the
  worst-case default. Estimator work continues as a separate desk thread that
  does not gate pack freeze.
- **Historical — receipt oracle:** PR #125's oracle covers 10 physical receipts
  and 5 logical operations per finalized bracket session. It was derived by
  replay, not written by hand. The later calibration-ledger read change did not
  alter that derivation path; the replay at `c61f840` remained 3,172 canonical
  bytes with SHA-256
  `088bab77a7843d82e6485df2840d304f2fdf8ecf372006049c60e37367f491c0`.
- **Historical — three-window unit:** It merged in PR #113, and its exact test
  is `tests/test_calibration_live_three_window.py`. No amendment for
  dispositions 1–6 exists or was verified against the later recovery changes.
- **Superseded instruction — successor work:** Successor work remains frozen at
  count three for a post-window cold gate. The issued acceptance artifact
  governs these windows; the older instruction to finish successor work before
  night one is superseded.
- **Historical — runtime refusal path:** PR #116 merged the three-night runtime
  refusal path. The separate specification lane remains open, but it does not
  permit anyone to change refusal meanings during a measurement night.
- **Historical T1 — ALPHA pack:** The pack was neither generated nor
  hash-frozen. It still required the named decode and prefill floor cells,
  reported-energy cells only if their byte-identity condition passed, stage
  launch recipes, exact roots, failure policy, hashes, and a fresh oracle.
- **Historical T1 — pack family:** ALPHA, BETA, and GAMMA were all unfrozen.
  They form one family because their model identities and floor transport
  interlock. GAMMA still required the 256-token prefill arm and the selected
  estimator identity.
- **Historical T1 — checkout:** The checkout was clean, but it predated the
  required recovery and mint-trust merges, so it was not a measurement
  checkout.

## Freeze-evaluable rows

These rows are evaluated at freeze and again at arm. Only two registered
conditional rules permit `NOT_APPLICABLE`: successor acceptance while the
issued acceptance artifact remains selected, and the four helper-installation
rows when the manual clock route is used. Every other row is required.

| Stable row ID | Checkpoint status and physical meaning |
|---|---|
| `clock.restore_recipe` | Not established by committed evidence. The frozen close-out must restore network time only after measurement completion, verdict, and both backups. |
| `desk.acceptance_owner` | NO-GO at the checkpoint: the copied-scalar removal was queued, not landed. The writer must read the authenticated active acceptance artifact. |
| `desk.acceptance_successor` | Not applicable while the issued D-079 artifact remains selected. A successor would require its own authenticated passing receipt before member one. |
| `desk.arming_procedure` | The document merged in PR #118; its exact final-head hashes and the non-delegable under-lease live verification were not yet established. |
| `desk.current_pack` | NO-GO at the checkpoint. The ALPHA pack and extraction specification were not yet frozen. Generator checks, validators, sidecars, and the committed pack digest must all agree. |
| `desk.estimator_identity` | D-133 selected the worst-case default for this cycle. The exact estimator identity still has to be derived from the frozen plan and admitted mint registry. |
| `desk.identity_pin_projection` | NO-GO at the checkpoint. The D-131 identity-pin projection was in PR #131 and its freeze and arm receipts were not yet available. |
| `desk.mint_trust` | PR #122 merged; the D-120 profile proof still has to be replayed at the exact final HEAD and pack digest. |
| `desk.multicell_mint` | The merged base was green at T1; its schemas and pinsets still have to byte-match the final committed sources. |
| `desk.pack_family` | NO-GO at the checkpoint. ALPHA, BETA, and GAMMA had not been frozen against one reviewed HEAD. |
| `desk.reason_code_plumbing` | The three-night code path was merged; final registry coverage and rehearsal evidence remained required. |
| `desk.receipt_oracle` | The oracle replay was byte-identical after PR #122. Any later ledger read/write change requires another derivation. |
| `desk.recovery_ledger_path` | PR #118 merged the recovery and ledger arming fixes; the focused suite must pass again at the bound final HEAD. |
| `desk.three_window_regression` | NO-GO / unverified for the final cadence. The earlier three-window regression test was later touched by recovery commit `4495609`; no separate final-cadence verification was recorded. |

## Arm-only rows

These facts cannot be stamped at freeze. Missing or stale live evidence means
`REFUSE`, never an operator-entered “unknown” machine value.

| Stable row ID | Checkpoint status and physical meaning |
|---|---|
| `clock.correct_and_prior_state` | Not established by committed evidence. Ed must compare the clock with an independent source and capture the prior automatic-time state. |
| `clock.network_time_off` | Not established by committed evidence. A fresh probe must show automatic network time is off; the former wording implying a second hand-counted settle is retired. |
| `desk.reviewed_checkout` | NO-GO until all blocking merges finish. The measurement checkout must prove HEAD, local main, and origin/main are identical with no tracked or untracked changes. |
| `desk.terminal_review` | NO-GO while a required unit is unmerged. The context-holding lead reviews the exact final head after every earlier gate. |
| `desk.under_lease_rehearsal` | NO-GO at the checkpoint. The dry run exercises the real validator, the real reservation command with `--execute`, and the production ledger and both phase-correct writers under the actual lease against a synthetic root. It never starts live measurement capture and can never authorize arming. |
| `privilege.activation_fence` | Not established by committed evidence; not applicable on the manual route. If the helper is used, evidence must show installation was inactive before a separate Ed-visible activation. |
| `privilege.fresh_authorization` | Not established by committed evidence; not applicable on the manual route. Helper installation requires the reviewed `sudo -k` and fresh authorization sequence. |
| `privilege.installed_bytes` | Not established by committed evidence; not applicable on the manual route. Installed bytes must equal the reviewed staged digests. |
| `privilege.isolated_interpreter` | Not established by committed evidence; not applicable on the manual route. The installed helper must prove genuine isolated interpreter operation. |
| `t0.background_quiet` | Not established by committed evidence. Time Machine, updates, indexing, downloads, and cloud uploads must be quiet in a fresh census. |
| `t0.campaign_lock_absent` | Not established by committed evidence. A live owner stops the attempt; an unreadable or stale lock also refuses rather than being deleted blindly. |
| `t0.display_thermal_idle` | Not established by committed evidence. The reviewed preparation and completed wait must prove display, screensaver, thermal pressure, and idle state. |
| `t0.fresh_roots_waivers` | Not established by committed evidence. Absolute claim, bound, custody, and quarantine roots must be distinct and fresh, and the actual attempt waiver bytes must decode exactly to `[]`. |
| `t0.ledger_reservation` | Not established by committed evidence. The live diagnostic and real reservation command must bind the plan SHA and record the pre-reserve authorization event plus `status: reserved`. |
| `t0.machine_readiness` | Not established by committed evidence. The frozen pre-window command must return `READY` for the same plan and roots. It is **not** the arming gate and cannot substitute for one; the calibration-ledger diagnostic and real reservation command with `--execute` are separate and mandatory. No automated word — `READY`, `ready`, or `clean` — licenses arming. Even a complete `GO` arm receipt is necessary but not sufficient: lead verification and the operator's separate physical launch action are still required. |
| `t0.no_stray_keepawake` | The T1 observation was green but expired. A fresh census must show no unrelated keep-awake, agent, browser, monitor, watcher, tail, or campaign process before the one reviewed wrapper starts. |
| `t0.offline_inputs` | Not established by committed evidence. Model, tokenizer, configurations, scripts, and environment must match frozen local inputs with no network fetch. |
| `t0.passwordless_powermetrics` | Not established by committed evidence. The exact reviewed passwordless measurement probe must exit zero. |
| `t0.power_path` | Not established by committed evidence. The 140 W supply and cable, external AC, 140 W negotiation, `ac_high_power`, and low-power-mode-off state must match the frozen policy. |
| `t0.single_launch_capability` | Not yet armed. The pre-launch record proves an unused, atomically consumable one-shot capability for the exact frozen foreground command. Consuming it records permission for exactly one later launch and never executes one. After successful consumption, the operator separately runs the frozen foreground command exactly once. Do not kill a running verdict, even if it takes more than two minutes. |
| `t0.storage_backup_capacity` | Not established by committed evidence. The checkpoint required at least 20 GB free, and both distinct backup destinations must exist, be writable, and have the frozen required capacity. |

Any refusal ends the attempt before launch. Preserve the authenticated evidence
and send the exact closed refusal code to the lead.
