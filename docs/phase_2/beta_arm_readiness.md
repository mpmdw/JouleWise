# Window BETA arm readiness — checked human view

Window BETA is the prospective Qwen2.5 7B floor night. The authoritative row
set is `configs/arm_readiness/d117_row_registry_v1.json`; this page is a
checked human view of the BETA profile. No BETA row status is established by
committed evidence at this checkpoint.

Pack freeze may evaluate only the first table and writes a non-authorizing
freeze receipt. T-0 replays those results, evaluates the second table from
fresh evidence, and writes an external arm receipt. Missing evidence refuses.

## Freeze-evaluable rows

| Stable row ID | Required fact |
|---|---|
| `clock.restore_recipe` | Frozen close-out recipe and ordering. |
| `desk.acceptance_owner` | Writer reads the authenticated active acceptance artifact. |
| `desk.acceptance_successor` | Conditional successor proof; not applicable only while the issued D-079 artifact is selected. |
| `desk.arming_procedure` | Final runbook sections and launch recipe match their doctrine pins. |
| `desk.current_pack` | Generator, validators, sidecars, attempt policy, and committed pack digest agree. |
| `desk.estimator_identity` | Estimator identity derives from the frozen plan and admitted mint registry. |
| `desk.identity_pin_projection` | The D-131 identity-pin freeze proof and later arm re-verification agree. |
| `desk.mint_trust` | D-120 trust receipt passes at the bound HEAD and pack digest. |
| `desk.multicell_mint` | Pinsets and mint schemas byte-match committed sources. |
| `desk.pack_family` | All three packs bind one reviewed HEAD and consistent identities. |
| `desk.reason_code_plumbing` | Every produced readiness refusal belongs to the closed vocabulary. |
| `desk.receipt_oracle` | Re-derived ledger oracle exactly equals the pack oracle. |
| `desk.recovery_ledger_path` | Recovery and ledger focused suite passes at the bound HEAD. |
| `desk.three_window_regression` | ALPHA/BETA/GAMMA live-ledger regression passes at the same HEAD. |

## Arm-only rows

| Stable row ID | Required fact |
|---|---|
| `clock.correct_and_prior_state` | Independent clock comparison and captured prior state. |
| `clock.network_time_off` | Fresh probe shows network time off. |
| `desk.reviewed_checkout` | HEAD, local main, and origin/main match with a clean tree. |
| `desk.terminal_review` | Terminal review binds the same HEAD tree and pack digest. |
| `desk.under_lease_rehearsal` | Same-head rehearsal uses the real reservation and both writers under lease. |
| `privilege.activation_fence` | Conditional helper proof of inactive installation before separate activation. |
| `privilege.fresh_authorization` | Conditional helper proof of fresh administrator authorization. |
| `privilege.installed_bytes` | Conditional helper proof that installed and reviewed bytes match. |
| `privilege.isolated_interpreter` | Conditional helper proof of isolated interpreter operation. |
| `t0.background_quiet` | Fresh maintenance census and closed observation pass. |
| `t0.campaign_lock_absent` | No live, stale, or unreadable campaign lock. |
| `t0.display_thermal_idle` | Display, screensaver, thermal, and idle checks pass. |
| `t0.fresh_roots_waivers` | Distinct fresh roots and exact empty waiver bytes. |
| `t0.ledger_reservation` | Real reservation is phase-correct and binds the plan SHA. |
| `t0.machine_readiness` | Frozen wait command is current and returns `READY`. |
| `t0.no_stray_keepawake` | Fresh process census finds no unrelated keep-awake or agent process. |
| `t0.offline_inputs` | Frozen local inputs match and no network fetch occurred. |
| `t0.passwordless_powermetrics` | Exact reviewed passwordless probe exits zero. |
| `t0.power_path` | Supply, negotiation, AC state, and policy match. |
| `t0.single_launch_capability` | An unused atomic one-shot launch capability is available. |
| `t0.storage_backup_capacity` | Two distinct writable backup destinations have capacity. |

No row in this page currently authorizes BETA. Authenticated receipts must
establish every applicable row before physical launch.
