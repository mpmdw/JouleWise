# RAW TRIAGE EXTRACT — L9-environmental-controls-census

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L9-environmental-controls-census`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 14/16 (evidence_universe_count=16)
- findings: 8; falsifiers: 4

## FINDINGS (verbatim)

### F1 [blocker] t0.background_quiet (MAINTENANCE_CENSUS) is unpassable on the real machine — arm always refuses
- file_line: `joulewise/arm_readiness_evidence_t0.py:963-980`
- failure_scenario (verbatim): ALPHA arm night: agents closed, machine genuinely quiet. author_arm_evidence_t0.py runs _maintenance_probe; pgrep -lf matches permanently resident Spotlight.app, mds_stores, XProtect XPC services, mediaanalysisd, photoanalysisd, softwareupdated, backupd-helper (~20 matches observed live); _expect_absent raises underivable → no T-0 evidence → no arm receipt → NO-GO on every attempt. Fail-closed (no false data risk) but the window can never launch. CI never saw this: tests fake the probe executor with exit_code=1 (tests/test_arm_readiness_evidence_t0.py:561).

### F2 [blocker] t0.no_stray_keepawake (PROCESS_CENSUS) is unpassable — browser/monitor patterns match permanent system daemons
- file_line: `joulewise/arm_readiness_evidence_t0.py:1344-1360`
- failure_scenario (verbatim): Same arm night: 'Safari|...' matches 9 always-resident Safari LaunchAgents with Safari closed; 'watch' substring in the monitor pattern matches watchdogd (permanent) and watchlistd. _expect_absent refuses → arm NO-GO forever. The keep-awake (pgrep -x caffeinate) and agent (codex|claude|t3) probes are correct and verified effective live; only the browser and monitor patterns over-match.

### F3 [should_fix] prewindow_check.sh agent census misses claude / codex mcp-server / t3 — printed OK while three agent processes were live
- file_line: `scripts/prewindow_check.sh:155`
- failure_scenario (verbatim): E-7b: operator runs the frozen prewindow_check --wait believing it certifies the agent-free ≥10-minute idle; pattern 'codex exec|codex-run|run_campaign|window-chain' matches none of the actual agent processes (observed live: OK printed with a claude session, codex mcp-server, and caffeinate running), so READY can be granted on an agent-contaminated machine; the only enforcing catch is PROCESS_CENSUS minutes later at T-0 authoring.

### F4 [should_fix] No single-home hazard register; consult-mandated hazards entirely absent: radios, notifications, peripherals, remote sessions, third-party LaunchAgents
- file_line: `docs/phase_2/window_runbook.md:1160 (§7, nearest anchor — the register is distributed)`
- failure_scenario (verbatim): Charter amendment 8 (from the consult's minimum list) requires rows for network/Bluetooth radios, notifications/media devices, external peripherals, concurrent users/remote sessions. None exists anywhere: live machine shows 3 login sessions (who), 14 third-party launchd jobs including the periodic us.zoom.updater, and active radios — a Zoom updater firing mid-member during the workload phase is invisible to every gate (CPU admission is pre-run idle-baseline only) and is bounded only at window scale by NEG-8 references; today that residual is not even documented as uncontrolled.

### F5 [should_fix] Mid-workload background contamination has no member-level detector and no documented disposition
- file_line: `joulewise/idle_admission.py:392-467`
- failure_scenario (verbatim): evaluate_cpu_idle_admission gates the PRE-RUN idle baseline (p95 combined power ≤ 1.0 W); environment re-probes bracket but do not cover the workload phase. A one-shot daemon burst inside a member's measurement phase silently inflates that member's energy; only window-scale drift (NEG-8 triplet/midpoint) can catch a sustained version. This is a legitimate design tradeoff under the D-078 attribution limit — but it must be a DOCUMENTED-UNCONTROLLED register row and a paper limitation, not silence.

### F6 [nit] JW-MET-2's four census literals have no named custody destination in the §12 close-out list
- file_line: `docs/phase_2/window_runbook.md:1509-1544`
- failure_scenario (verbatim): Operator records keyboard_backlight.level=0 etc. per §5A but §12 never enumerates where they land; a close-out can be 'complete' without them, weakening the JW-MET-2 audit trail.

### F7 [nit] Battery charge state is censused but has no gate or disposition
- file_line: `joulewise/arm_readiness_evidence_t0.py:1457-1498`
- failure_scenario (verbatim): POWER_PREFLIGHT passes with is_charging=true; charging mid-window adds SMC/charger thermal load that differs from the not-charging state a bound corpus may have been minted under — an uncontrolled, undocumented within-window state change.

### F8 [nit] Lid state is operator-discipline only, never probed
- file_line: `docs/phase_2/window_runbook.md:42`
- failure_scenario (verbatim): A lid change alters the thermal envelope mid-window; only the downstream thermal-pressure gate would notice, and only if pressure leaves Nominal.

## WORK ORDERS (verbatim)

- WO-L9-1: Re-shape t0.background_quiet's MAINTENANCE_CENSUS from absence-required pgrep to an activity-based census (CPU-threshold like prewindow_check's, or a curated transient-only process list). This weakens a probe, so it needs a magistrate/cold ruling; include a regression fixture built from the real resident-process table (ED-Q-L9-3) so CI can no longer pass on faked-empty pgrep output.

- WO-L9-2: Fix PROCESS_CENSUS browser and monitor patterns (anchor tokens; exclude permanent daemons watchdogd/watchlistd/Safari support agents, or move to activity-based). Keep the keep-awake and agent probes byte-identical — both verified effective live.

- WO-L9-3: Align prewindow_check.sh check #8 with the T-0 agent census (add claude|codex mcp|t3), so E-7b READY cannot be granted with agents running.

- WO-L9-4: Author the one-home hazard register with per-hazard disposition (controlled / censused / DOCUMENTED-UNCONTROLLED), adding the absent rows: Wi-Fi/Bluetooth radios, notifications/media devices, external peripherals, concurrent users/remote sessions, third-party LaunchAgents, ambient temperature, battery charge state, lid state, and the mid-workload contamination residual; wire that residual into the paper's limitation text.

## ED-QUALIFICATION ROWS (verbatim)

- ED-Q-L9-1 (staged): JW-MET-2 System Settings keyboard-backlight census — level 0, auto-adjust off, inactivity Never, verification=operator_visual (ed-qualification-session.md step 4; no CLI exists for the level, operator visual is the only probe)

- ED-Q-L9-2 (staged): JW-MET-3 keyboard-backlight rail-inclusion differential probe — sudo powermetrics ABBA max/off arms (ed-qualification-session.md step 3; documentation-grade, boundary verdict already stands on code evidence)

- ED-Q-L9-3 (new, stable capability, no sudo): quiet-state resident-process baseline — with all fleets/agents closed on the real machine, capture the four PROCESS_CENSUS and one MAINTENANCE_CENSUS pgrep outputs and commit them as the regression fixture that the WO-L9-1/2 pattern fixes must pass against; this is the only way to prove the fixed censuses PASS in the state they will actually run in

## UNEXECUTED OBLIGATIONS (verbatim)

- quiet_mac_prep.sh full execution (quits user apps and sleeps the display — not sandbox-safe from an agent session; step-7 probes replicated read-only instead)

- --arm-quiet-mode live re-probe path inside run_campaign (requires display sleep + live campaign; code path read, not run)

- sudo-gated probes: systemsetup -getusingnetworktime read, sudo -n powermetrics (no sudo in sandbox; covered by capture lens + ED rows)

- quiet_guard engine internals (Commit-1 is contractually inactive and non-armable; contract read, engine not audited)

- whole_window.py adapter-wattage-continuity and controller.py enforcement wiring examined at grep/inventory level only

- full audit of tests/test_arm_readiness_evidence_t0.py fixtures beyond confirming the probe executor is faked with empty-pgrep results

