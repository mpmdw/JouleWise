# Window BETA arm readiness — checked human view

Window BETA is the prospective Qwen2.5 7B floor night. The authoritative row
set is `configs/arm_readiness/d117_row_registry_v1.json`; this page is a
checked human view of the BETA profile. No BETA row status is established by
committed evidence at this checkpoint.

At pack freeze, the completed frozen pack pins only the non-authorizing freeze
receipt's path and SHA-256. It declares the future arm receipt's schema and
custody namespace, but never that future receipt's filename or digest. Only at
T-0, from the completed and unchanged pack, does the generator replay the first
table, evaluate the second table from fresh evidence, and create the external
arm receipt. Missing evidence refuses.

Each readiness receipt carries a boot-session identifier. If the Mac reboots
between freeze and arm, verification automatically rejects receipts from the
earlier boot session and requires new verification.

The collection procedure remains the
[Quiet-Mac Claim-Window Run-Book](window_runbook.md). This page does not
replace it.

## Freeze-evaluable rows

| Stable row ID | Required fact |
|---|---|
| `clock.restore_recipe` | The frozen close-out recipe restores network time only after measurement completion, the verdict, and both backups, and then verifies the restored state. |
| `desk.acceptance_owner` | The writer reads the authenticated active acceptance artifact; a copied scalar or unknown key refuses. |
| `desk.acceptance_successor` | A successor needs its own authenticated passing receipt selected before member one. This row is not applicable only while the issued D-079 artifact remains selected. |
| `desk.arming_procedure` | Committed hashes of runbook sections 5, 5A, 5B, 5C, 6, and 10 and the frozen launch recipe equal the pack's recorded hashes. |
| `desk.current_pack` | The generator check, validators, sidecars, extraction specification, attempt policy, and committed pack digest all describe the same completed BETA pack. |
| `desk.estimator_identity` | The exact estimator identity is derived from the frozen plan and admitted mint registry, never typed by the operator. |
| `desk.identity_pin_projection` | The freeze proof and arm-time recheck required by decision D-131 bind the same model, runtime, and configuration identity. |
| `desk.mint_trust` | The mint-trust profile proof required by decision D-120 says `PASS` at the exact reviewed commit and pack digest. |
| `desk.multicell_mint` | Pack pinsets and mint schemas byte-match their committed sources, and the focused integration receipt passes. |
| `desk.pack_family` | ALPHA, BETA, and GAMMA bind the same reviewed commit and mutually consistent model and floor-transport identities. |
| `desk.reason_code_plumbing` | Registry coverage and rehearsal evidence prove every possible readiness refusal carries one code from the closed refusal list. |
| `desk.receipt_oracle` | Replay of the committed calibration-ledger implementation produces exactly the oracle frozen in the pack. |
| `desk.recovery_ledger_path` | The recovery and calibration-ledger focused tests pass at the exact commit bound to the pack. |
| `desk.three_window_regression` | `tests/test_calibration_live_three_window.py` passes the ALPHA/BETA/GAMMA live-ledger cadence at that same commit. |

## Arm-only rows

| Stable row ID | Required fact |
|---|---|
| `clock.correct_and_prior_state` | The operator compares the clock with an independent trusted source, corrects it if needed, and the machine records the prior automatic-network-time state. |
| `clock.network_time_off` | A fresh system probe records that automatic network time is off; no hand-entered row status is accepted. |
| `desk.reviewed_checkout` | The checkout proves that HEAD, local main, and origin/main are the same commit and tree and that no tracked or untracked file is present. |
| `desk.terminal_review` | The context-holding lead's final review binds this exact commit tree and BETA pack digest; any later change invalidates it. |
| `desk.under_lease_rehearsal` | The same-head dry run exercises the real validator, real reservation command with `--execute`, and the production ledger and both phase-correct writers under the actual lease against a synthetic root. It never starts live measurement capture and can never authorize arming. |
| `privilege.activation_fence` | Not applicable on the manual clock route. If the helper route is used, installation evidence proves the helper was inactive before a separate operator-visible activation. |
| `privilege.fresh_authorization` | Not applicable on the manual clock route. Helper installation records `sudo -k` followed by fresh interactive authorization for the one reviewed install command. |
| `privilege.installed_bytes` | Not applicable on the manual clock route. On the helper route, every installed file digest equals its reviewed staged digest. |
| `privilege.isolated_interpreter` | Not applicable on the manual clock route. On the helper route, the installed helper proves that site initialization, user-site packages, and environment hooks are disabled. |
| `t0.background_quiet` | A fresh census shows Time Machine, software updates, indexing, downloads, and cloud uploads are finished or paused, followed by the required closed observation. |
| `t0.campaign_lock_absent` | A fresh probe finds no campaign lock. A live owner stops the attempt, and an unreadable or stale lock refuses rather than being deleted blindly. |
| `t0.display_thermal_idle` | The reviewed preparation and completed wait prove the displays are asleep, the screensaver is disengaged, thermal pressure is nominal, and the Mac stayed untouched for at least ten minutes. |
| `t0.fresh_roots_waivers` | The frozen absolute claim, bound, custody, and quarantine roots are distinct and fresh, and the attempt's waiver file bytes decode exactly to an empty list. |
| `t0.ledger_reservation` | The live diagnostic and real reservation command with `--execute` bind the frozen plan SHA and record both the pre-reserve authorization event and `status: reserved`. |
| `t0.machine_readiness` | The frozen pre-window command must return `READY` for the same BETA plan and roots. It is **not** the arming gate and cannot substitute for one; the calibration-ledger diagnostic and real reservation command with `--execute` are separate and mandatory. No automated word — `READY`, `ready`, or `clean` — licenses arming. Even a complete `GO` arm receipt is necessary but not sufficient: lead verification and the operator's separate physical launch action are still required. |
| `t0.no_stray_keepawake` | A fresh census finds no unrelated keep-awake, agent, browser, monitor, watcher, tail, or campaign process before the one reviewed launch wrapper starts. |
| `t0.offline_inputs` | The local model, tokenizer, configurations, scripts, and runtime environment byte-match the BETA pack's frozen inventory, and no network fetch occurs. |
| `t0.passwordless_powermetrics` | The exact passwordless measurement probe frozen in the BETA pack exits zero before the final settle. |
| `t0.power_path` | The approved 140 W supply and cable are connected to external AC, power negotiation reports 140 W, the policy is `ac_high_power`, and low-power mode is off. |
| `t0.single_launch_capability` | An unused atomic capability is available for the exact frozen foreground command. Consuming it records permission for exactly one later launch and never executes one. After successful consumption, the operator separately runs the frozen foreground command exactly once. Do not kill a running verdict, even if it takes more than two minutes. |
| `t0.storage_backup_capacity` | The machine meets the BETA pack's frozen free-space minimum, and both frozen backup destinations exist, are distinct and writable, and meet their frozen capacity minimum. |

No row in this page currently authorizes BETA. Authenticated receipts must
establish every applicable row before physical launch, but receipts do not
perform or authorize that separate operator action.
