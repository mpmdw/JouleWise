# Window ALPHA arm readiness — checked human view

**Checkpoint:** T4-late, 2026-08-11 (supersedes the earlier T4, T3, and T1
lines). **Current verdict: NO-GO. Do not arm Window ALPHA.**

Window ALPHA is the first prospective D-117 night: the Qwen2.5 1.5B decode
floor with prefill floor cells. The authoritative row set is
`configs/arm_readiness/d117_row_registry_v1.json`; this page is a checked,
plain-language view of its ALPHA profile. A row appearing here does not make
it pass. Only authenticated evidence consumed by the D-134 generator can do
that.

Readiness has two stages. Pack freeze writes a non-authorizing freeze receipt
inside the pack and pins its path and SHA-256 in the final plan tree. At T-0,
the generator rechecks those rows and the live rows, then writes an external
arm receipt under window custody. A freeze receipt always says that arming is
not applicable. Only an unexpired, unsuperseded external arm receipt may carry
`GO`, and it remains necessary rather than sufficient: the lead's verification
and Ed's physical foreground action are not delegated.

The collection procedure remains the
[Quiet-Mac Claim-Window Run-Book](window_runbook.md). This page does not
replace it.

## Preserved checkpoint facts

Recovery merged in PR #118 on 2026-08-09. Mint trust merged in PR #122 at
`ae6af48` on 2026-08-11 under D-130; its 16-question relocation delta answered
16/16. PR #125 merged the receipt oracle on 2026-08-10, and the later
calibration-ledger read-surface change was checked at `c61f840`: 3,172
canonical bytes with SHA-256
`088bab77a7843d82e6485df2840d304f2fdf8ecf372006049c60e37367f491c0`,
byte-identical to the earlier oracle. D-133 resolved the estimator question for
this cycle by returning the packs to the worst-case default; the common-mode
thread no longer gates freeze. At this checkpoint the D-131 identity-pin
projection was implemented but still in PR #131, the Ed-funded Q8 work item's
256-token prefill floor cells were unbuilt, and the packs and plan-specific
readiness receipts were not frozen. Those are dated facts, not present-tense
evidence of a pass.

## Freeze-evaluable rows

These rows are evaluated at freeze and again at arm. `NOT_APPLICABLE` is legal
only for the registered successor-acceptance rule.

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
| `desk.under_lease_rehearsal` | NO-GO at the checkpoint. The real validator, real reservation command with `--execute`, and both phase-correct writers must pass against a synthetic root under the actual lease. |
| `privilege.activation_fence` | Not established by committed evidence; not applicable on the manual route. If the helper is used, evidence must show installation was inactive before a separate Ed-visible activation. |
| `privilege.fresh_authorization` | Not established by committed evidence; not applicable on the manual route. Helper installation requires the reviewed `sudo -k` and fresh authorization sequence. |
| `privilege.installed_bytes` | Not established by committed evidence; not applicable on the manual route. Installed bytes must equal the reviewed staged digests. |
| `privilege.isolated_interpreter` | Not established by committed evidence; not applicable on the manual route. The installed helper must prove genuine isolated interpreter operation. |
| `t0.background_quiet` | Not established by committed evidence. Time Machine, updates, indexing, downloads, and cloud uploads must be quiet in a fresh census. |
| `t0.campaign_lock_absent` | Not established by committed evidence. A live owner stops the attempt; an unreadable or stale lock also refuses rather than being deleted blindly. |
| `t0.display_thermal_idle` | Not established by committed evidence. The reviewed preparation and completed wait must prove display, screensaver, thermal pressure, and idle state. |
| `t0.fresh_roots_waivers` | Not established by committed evidence. Absolute claim, bound, custody, and quarantine roots must be distinct and fresh, and the actual attempt waiver bytes must decode exactly to `[]`. |
| `t0.ledger_reservation` | Not established by committed evidence. The live diagnostic and real reservation command must bind the plan SHA and record the pre-reserve authorization event plus `status: reserved`. |
| `t0.machine_readiness` | Not established by committed evidence. The frozen pre-window command must return `READY` for the same plan and roots; that word alone never arms the night. |
| `t0.no_stray_keepawake` | The T1 observation was green but expired. A fresh census must show no unrelated keep-awake, agent, browser, monitor, watcher, tail, or campaign process before the one reviewed wrapper starts. |
| `t0.offline_inputs` | Not established by committed evidence. Model, tokenizer, configurations, scripts, and environment must match frozen local inputs with no network fetch. |
| `t0.passwordless_powermetrics` | Not established by committed evidence. The exact reviewed passwordless measurement probe must exit zero. |
| `t0.power_path` | Not established by committed evidence. The 140 W supply and cable, external AC, 140 W negotiation, `ac_high_power`, and low-power-mode-off state must match the frozen policy. |
| `t0.single_launch_capability` | Not yet armed. The pre-launch record proves an unused, atomically consumable one-shot capability; it does not falsely claim that a foreground launch already happened. |
| `t0.storage_backup_capacity` | Not established by committed evidence. The checkpoint required at least 20 GB free, and both distinct backup destinations must exist, be writable, and have the frozen required capacity. |

Any refusal ends the attempt before launch. Preserve the authenticated evidence
and send the exact closed refusal code to the lead.
