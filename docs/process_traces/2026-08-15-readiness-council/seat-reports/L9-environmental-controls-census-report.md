# L9 — ENVIRONMENTAL CONTROLS CENSUS (high) — readiness-fleet seat report

**Baseline:** docs/process/audit-baseline-manifest.json (head_commit `ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b`). Worktree HEAD `8937dec9`; post-baseline commits touch only README.md, RUN_STATE.md, and the manifest itself — no L9-scope artifact drifted. Runbook SHA-256 re-verified equal to the manifest's `runbook_sha256` (`25a4e809…`). Probes executed live on the actual measurement machine (Mac15,9 / 25F84, per the census itself).

**Verdict: NOT-READY** (two arm-blocking census defects, both fail-closed; work orders below).

## 1. Evidence universe (enumerated before findings)

1. docs/phase_2/window_runbook.md (§1, §5, §5A/JW-MET-2, §5B, §5C, §6 chain, §7, §8–§12) — read in full
2. scripts/quiet_mac_prep.sh — read in full; step-7 probes replicated read-only
3. scripts/prewindow_check.sh — read in full; **executed live**
4. scripts/quiet_window_clock.sh — read (status/disable safety; MAX_OFFSET_S refusal)
5. joulewise/environment.py (snapshot census, policy evaluator, guard observation) — read; **executed live**
6. joulewise/arm_readiness_evidence_t0.py (probe executor, MAINTENANCE_CENSUS, PROCESS_CENSUS, MACHINE_PREFLIGHT, POWER_PREFLIGHT, CLOCK_ATTESTATION/CLOCK_PROBE, OFFLINE_INPUT_INVENTORY, POWERMETRICS_PROBE derivations) — read; census argvs **executed live**
7. configs/arm_readiness/d117_row_registry_v1.json (35 rows → evidence kinds) — enumerated
8. configs/campaign_policies/quiet_mac_p2_production.json — read in full
9. joulewise/idle_admission.py `evaluate_cpu_idle_admission` (per-member CPU backstop) — read
10. joulewise/environment_admission.py — function-inventory survey
11. joulewise/whole_window.py adapter-wattage continuity — grep-level (partial)
12. joulewise/controller.py enforcement wiring — grep-level (partial)
13. docs/contracts/quiet_guard.md + quiet_guard scripts — contract read (Commit-1 inactive, non-armable; engine not audited)
14. docs/phase_2/ed-qualification-session.md; docs/phase_2/alpha_arm_readiness.md (row notes); docs/strategy/2026-08-14-70h-plan.md (JW-MET-1/2/3 context) — read
15. tests/test_arm_readiness_evidence_t0.py — targeted check of probe mocking only
16. Live machine state (process table, launchd, who, pmset assertions, ioreg, environment snapshot) — probed read-only

**Coverage: 14 of 16 examined** (11 and 12 partial). Unexecuted obligations: quiet_mac_prep full run (mutates session/display), `--arm-quiet-mode` live re-probe, sudo-gated probes (systemsetup, powermetrics), quiet_guard engine internals, full t0-test-fixture audit.

## 2. The hazard register, dispositioned

| Hazard | Disposition | Mechanism (verified) |
|---|---|---|
| Display | CONTROLLED + CENSUSED | Policy `require_displays_asleep` + per-display asleep evidence (macOS-26 systemstate caveat handled via framebuffer inventory); `--arm-quiet-mode` re-probe every invocation; transient `displaysleepnow` only. Live: census reported `any_awake`, policy refused. |
| Keyboard backlight (JW-MET-2, as landed) | CONTROLLED (operator) + CENSUSED (operator_visual) + residual DOCUMENTED | Runbook §5A four literals; prewindow NOTE; quiet_mac_prep ioreg inventory (**live: capability present**); ed-qual step 4. No CLI for level — documented. Nit: literals lack a §12 custody slot. |
| Screensaver | CONTROLLED + CENSUSED | defaults + HIDIdleTime derivation; policy `require_screensaver_disengaged`; persistent-settings changes forbidden. Live: delay=0, disengaged. |
| Clock manipulation (§5A) / time daemons | CONTROLLED + CENSUSED, residual DOCUMENTED | Ed-only `systemsetup off` with exact-key CLOCK_ATTESTATION (argv + monotonic-ordering checks) and fresh CLOCK_PROBE requiring "Network Time: Off"; quiet_window_clock refuses to pin a >0.5 s-wrong clock; 5 ms anchor predicate never waived; `timed` attribution honestly recorded as unproven. |
| Thermal | CONTROLLED + CENSUSED | Policy Nominal + cooldown-v2 + T-0 probe requiring no warnings and CPU/GPU speed limits = 100. Ambient temperature itself: uncontrolled, bounded by Nominal gate + NEG-8 drift refs — needs an explicit register row (nit-class). |
| Charger policy | CONTROLLED + CENSUSED | POWER_PREFLIGHT (AC + low-power off + connected known-wattage adapter; live: 140 W pd); adapter-wattage continuity in whole-window verdict; supply identity in NEG-8 bound bindings. Charge state censused but ungated (nit). |
| Background daemons / launchd | CENSUSED, **but arm census defective** | Named maintenance list + prewindow CPU thresholds + per-member idle admission (p95 combined ≤ 1.0 W). **BLOCKER: T-0 absence probe can never pass** (below). 14 third-party launchd jobs (incl. periodic us.zoom.updater) on no register at all. |
| Caffeinate census | CONTROLLED | One-reviewed-caffeinate rule (§6); T-0 `pgrep -x caffeinate` (live: detected the running one); pmset assertions censused. Row hosting it is blocked by sibling patterns (below). |
| Other agents | CONTROLLED at T-0; prewindow layer weak | T-0 agent pattern `codex|claude|t3` verified effective live (16 matches). prewindow #8 missed all of them while printing OK (should-fix). |
| Remote sessions / concurrent users | **NOT ON REGISTER** | Live: `who` shows 3 login sessions. Nothing censuses sshd/Screen Sharing/users. |
| Radios (Wi-Fi/BT), notifications, external peripherals | **NOT ON REGISTER** | Consult minimum list includes them; no row, no control, no documentation. Sub-threshold network churn (apsd/nsurlsessiond/cloudd/bird) rides only on the generic CPU backstop. |
| Memory / storage | CENSUSED | Snapshot memory-pressure fields; prewindow 20 GB floor. Ungated beyond disk — acceptable (CPU backstop). |
| Lid state | Operator discipline only | §1/§10 rows; no probe (nit). |

**Completeness disposition** — what could perturb the cpu+gpu+ane rails and is not on the register: third-party periodic LaunchAgents, incoming network traffic on live radios, remote logins, charging-state transitions, ambient temperature, lid state, and any **mid-workload** one-shot daemon burst. The per-member CPU admission gate is pre-run idle-baseline only; the workload phase is bounded solely at window scale by the NEG-8 reference triplet/midpoint and drift allowance. That is a defensible design under the D-078 attribution limit — but it is currently undocumented, and the consult-mandated hazards above have no rows anywhere.

## 3. Executed positive probes

1. `collect_environment_snapshot()` live — truthful contaminated-state report (display `any_awake`, load 4.26, `timed_running=true`, AC 140 W, thermal nominal, zero errors).
2. `evaluate_environment_policy(live)` → `eligible=false` (`display_not_all_asleep`); synthetic clean snapshot → `eligible=true`.
3. `prewindow_check.sh` → NOT READY, exit 1 (load gate fired).
4. `ioreg` KeyboardBacklight capability present (JW-MET-2 inventory works here).
5. T-0 keep-awake and agent pgrep probes detect the live caffeinate and agent fleet — detection demonstrably works.
6. Clock receipt derivations enforce sudo+systemsetup argv identity and monotonic artifact ordering (code-verified).

## 4. Executed falsifiers (READY-falsification attempts)

1. **Exact `_maintenance_probe` argv, live** (pattern assembled so my own argv can't self-match): exit 0, ~20 matches — most permanently resident (Spotlight.app, mds_stores, XProtect XPC ×3, mediaanalysisd, photoanalysisd, softwareupdated, backupd-helper). `_expect_absent` (arm_readiness_evidence_t0.py:963-965) requires exit 1 + empty stdout ⇒ **t0.background_quiet refuses on every arm attempt, even on a genuinely quiet machine.** Fail-closed, launch-blocking.
2. **Exact PROCESS_CENSUS argvs, live**: browser pattern matched 9 resident Safari LaunchAgents (Safari closed); monitor pattern's `watch` substring matched permanent watchdogd + watchlistd ⇒ **t0.no_stray_keepawake refuses on every arm attempt.** CI never saw either: tests fake the probe executor with empty-pgrep `exit_code=1` (tests/test_arm_readiness_evidence_t0.py:561).
3. **Lie attempt on the policy evaluator**: nulled the three critical fields → `eligible=false`, statuses `unknown` — `critical_unknown_fail_closed` held; could not make it pass on missing evidence.
4. **prewindow on a contaminated machine**: blocked on load — but check #8 printed "OK: no agent or measurement process running" with claude + codex mcp-server + caffeinate live. Partial falsification succeeded (finding F3).

## 5. Findings (severity-tiered)

- **BLOCKER F1** — `t0.background_quiet` unpassable (joulewise/arm_readiness_evidence_t0.py:963-980). Scenario: ALPHA arm night, agents closed, machine quiet; T-0 authoring raises `underivable` on resident macOS daemons → no arm receipt → NO-GO on every attempt. Fail-closed; window unrunnable.
- **BLOCKER F2** — `t0.no_stray_keepawake` unpassable (arm_readiness_evidence_t0.py:1344-1360): browser/monitor patterns match permanent daemons. Same scenario. Keep-awake/agent probes are correct — only the two patterns over-match.
- **SHOULD-FIX F3** — prewindow_check.sh:155 agent census misses claude/codex mcp/t3 (observed lying OK, live). E-7b READY can certify the ≥10-min idle with agents running; only T-0 catches it later.
- **SHOULD-FIX F4** — no one-home hazard register; consult-mandated hazards absent entirely (radios, notifications, peripherals, remote sessions — live: 3 sessions; third-party LaunchAgents — live: 14 incl. periodic us.zoom.updater). A mid-member Zoom-updater burst is invisible to every member-level gate and today not even documented as uncontrolled.
- **SHOULD-FIX F5** — mid-workload contamination has no member-level detector (idle_admission.py:392-467 gates pre-run baseline only); needs a DOCUMENTED-UNCONTROLLED row + paper limitation wording, not silence.
- **NIT F6** — JW-MET-2's four census literals lack a named custody slot in §12 (runbook:1509-1544).
- **NIT F7** — charge state censused, not gated/dispositioned (arm_readiness_evidence_t0.py:1457-1498).
- **NIT F8** — lid state discipline-only, no probe (runbook:42).

## 6. Work orders

- **WO-L9-1**: re-shape MAINTENANCE_CENSUS to activity-based (CPU-threshold, as prewindow already does) or curated transient-only list — probe weakening ⇒ needs a ruling; add a live-resident-table regression fixture so faked-empty pgrep can't re-mask it.
- **WO-L9-2**: fix PROCESS_CENSUS browser/monitor patterns (anchor tokens; exclude watchdogd/watchlistd/Safari agents); keep keep-awake/agent probes byte-identical.
- **WO-L9-3**: align prewindow #8 with the T-0 agent pattern.
- **WO-L9-4**: author the one-home hazard register with the missing rows, each dispositioned; wire the mid-workload residual into the paper limitation text.

## 7. ED-QUALIFICATION rows

- **ED-Q-L9-1** (staged, ed-qual step 4): JW-MET-2 System Settings keyboard-backlight census — operator_visual, no CLI exists.
- **ED-Q-L9-2** (staged, ed-qual step 3): JW-MET-3 rail-inclusion differential probe (sudo powermetrics, ABBA) — documentation-grade.
- **ED-Q-L9-3** (new, no sudo, needs only the quiet machine state): capture the five census pgrep outputs with all fleets closed, as the regression baseline the WO-L9-1/2 fixes must pass against.

## 8. Exit hygiene

`git status --short` empty; worktree byte-identical at HEAD `8937dec9`; all probe scripts written to the session scratchpad only.