# Window ALPHA arm readiness — checked human view

**Checkpoint:** T4-late, 2026-08-11 (supersedes the earlier T4, T3, and T1
lines). **Current verdict: NO-GO. Do not arm Window ALPHA.**

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
