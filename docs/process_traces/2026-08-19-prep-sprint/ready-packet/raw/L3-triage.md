# RAW TRIAGE EXTRACT — L3-CAPTURE-TELEMETRY-xhigh

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L3-CAPTURE-TELEMETRY-xhigh`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 25/29 (evidence_universe_count=29)
- findings: 5; falsifiers: 3

## FINDINGS (verbatim)

### F1 [should_fix] Measured-run (adapter/controller) path has no post-teardown sampler census; kill-escalation orphan samples invisibly through the rest of a window
- file_line: `joulewise/adapters/powermetrics.py:1655-1663 (_stop_process); contrast scripts/validate_powermetrics_fiducial.py:562-578 (_sampler_lifetime + census)`
- failure_scenario (verbatim): During a funded window, powermetrics hangs >10 s past SIGTERM at member k's stop; _stop_process SIGKILLs sudo, which cannot forward it; the root powermetrics survives (executed falsifier F-B), keeps sampling at 100 ms into an unlinked file, and loads the machine through members k+1..N and their idle baselines. Only the fiducial script has the #127 detect-and-report census; the controller path has none, and the arm-time T0 monitor census (arm_readiness_evidence_t0.py:1350) runs only at arm — nothing between members detects it, so contaminated bundles do NOT fail closed against consumption.

### F2 [should_fix] ED-qualification Step 2 points at a checklist home that does not contain the checklist
- file_line: `docs/phase_2/ed-qualification-session.md:18-19 vs scripts/validate_powermetrics_fiducial.py:1-27`
- failure_scenario (verbatim): The doc says the #127 reliance checklist 'items live in the sampler module docstring'; the current docstring carries only the UNSUPPORTED-scope statement (the round-2 rewrite dropped the round-1 checklist). The executable items actually live in scripts/ed_session/sampler-checklist.sh, and no staging step copying it to the referenced /tmp/ed-session/ path exists in the repo. At the single batched Ed session, the operator or the preparing loop follows the pointer, finds no items, and ED-QUALIFICATION rows get closed against an unenumerated or improvised checklist — corrupting the exact closure the council READY depends on.

### F3 [should_fix] ED sampler checklist qualifies cadence at 1 Hz while every production surface runs 100 ms
- file_line: `scripts/ed_session/sampler-checklist.sh:59,106-110 (-i 1000 -n 5) vs packs power_hz=10.0, powermetrics_fiducial.py:63 (SAMPLING_INTERVAL_MS=100), window_runbook.md:638`
- failure_scenario (verbatim): Step 2's 'record cadence observations' captures five 1000 ms intervals; the cadence row closes on 1 Hz evidence. The window then runs at 100 ms, where powermetrics' realized-interval behavior on the current OS build was never observed live; a post-update realized-cadence anomaly at 100 ms (elapsed_ns integration stays correct, but rollover-gate timing, drain budgets, and window sample-count planning assume ~100 ms) surfaces only inside the funded window.

### F4 [nit] Post-JW-MET-1 residual: retained related-work draft still describes JouleWise with system-on-chip boundary language
- file_line: `docs/paper/related_work_draft.md:19`
- failure_scenario (verbatim): JW-MET-1 narrowed all five draft-v1.md sites (31ccef5), but the retained draft's 'integrates named system-on-chip power channels' (subject: JouleWise) was not swept; a future paper train copying from the retained draft reintroduces the overbroad boundary claim. (Third-party descriptions of Silicon Showdown's whole-SoC boundary are correct and not affected.)

### F5 [nit] samplers_available metadata echoes the requested list rather than a probed census
- file_line: `joulewise/adapters/powermetrics.py:1175-1179`
- failure_scenario (verbatim): After any rc-0 one-sample probe, device metadata reports samplers_available=[cpu_power,gpu_power,ane_power,thermal] with method='requested_sampler_probe'. A bundle auditor reads it as a probed census; if the thermal sampler were silently absent (thermal_pressure is optional in the parser), the metadata would still claim it available. The label is honest but the field name invites over-reading.

## WORK ORDERS (verbatim)

- WO-L3-1: Add the detect-and-report post-teardown sampler census to the measured-run stop path (adapter stop_sampling_with_evidence/_take_measured_capture or controller finalization), mirroring scripts/validate_powermetrics_fiducial.py's _report_powermetrics_census, and record findings into bundle metadata so a mid-window orphan is at least detectable at reduce time. Keep detect-and-report-only semantics pending WO-SAMPLER-SUPERVISOR.

- WO-L3-2: Fix docs/phase_2/ed-qualification-session.md Step 2 to name scripts/ed_session/sampler-checklist.sh as the checklist home (and either add the /tmp/ed-session staging step to the loop's prep or reference the repo path directly); align the module docstring pointer or restore an item list there.

- WO-L3-3: Add a second short capture at -i 100 (production cadence) to scripts/ed_session/sampler-checklist.sh's cadence-record step, or explicitly annotate the row as supervision-only and move cadence currency to the T0 probes.

- WO-L3-4 (nit-grade): sweep docs/paper/related_work_draft.md:19 boundary wording; rename or probe-derive samplers_available metadata.

## ED-QUALIFICATION ROWS (verbatim)

- ED-L3-1 (stable): Live sudo/powermetrics checklist — run scripts/ed_session/sampler-checklist.sh (sudo -n grant, empty pre-census, supervised 5-sample capture under _sampler_lifetime, empty post-teardown census, cadence record, parse by the pinned parser). This is the long-owed row gating reliance on #127's production sampler commit (RUN_STATE 'ED-OWED' item 3). Close only after WO-L3-2/WO-L3-3 fix the checklist's documented home and add the 100 ms leg.

- ED-L3-2 (stable): Live SIGTERM-relay termination — confirm on the current OS build that `sudo -n powermetrics` exits within the 10 s grace on SIGTERM to sudo (normal path) ; the executed falsifier F-B shows that if it ever does not, the SIGKILL escalation strands a root orphan no software census on the measured-run path detects. One observation, any tap block.

- ED-L3-3 (stable): JW-MET-3 rail probe — scripts/ed_session/rail-probe.sh ABBA keyboard-backlight arms with --samplers battery,cpu_power,gpu_power,ane_power,thermal; documentation-grade rail-inclusion differential (the LED-outside-boundary verdict already stands on code evidence).

- ED-L3-4 (stable, largely co-closed by ED-L3-1): Channel-census currency on the arm build — one live capture parsed by the pinned parser with hw_model/kern_osversion recorded and matched against the runbook's Mac15,9 / macOS 25F84 bindings; REOPENS on any OS update before the window (the parser is pinned to the Slice-2H fixture format; a format/unit change fails closed on rails but silently on units only if Apple kept mW fields parseable — currency is an empirical row, not a test-provable one).

## UNEXECUTED OBLIGATIONS (verbatim)

- tests/test_calibration_writer_crash_matrix.py NOT run at this seat (hosted-pathological per WO-CRASHMATRIX-RELIABILITY; a sibling seat was executing it live during my audit — concurrent duplicate execution would have contended; its writer-crash coverage is L2's scope).

- No live sudo powermetrics execution of any kind (environment: no sudo, no live measurement) — everything privileged is emitted as ED-QUALIFICATION rows, none silently skipped.

- joulewise/adapters/mock_telemetry.py not audited (not on the funded-window path; pack member verified pinning telemetry_backend=powermetrics).

- scripts/ed_session/rail-probe.sh read for role, not line-audited (JW-MET-3 is documentation-grade).

- quiet_guard.py / quiet_guard_process.py header-ruled out of this seat's scope (agent-session custody guard — seats 1/9 territory).

- Rich-telemetry consumers (salvage_dangler.py, floors common-mode) and reducer integration internals corroborated only at the seam (reduce.py D-018 policy: only manifest rails summed, non-manifest rows ignored) — deep audit is L4's scope.

- Long-stream soak of the admission stream cursor (_advance_stream_cursor over hours-scale files) not executed; covered by unit tests incl. the 64KiB-chunk large-stream test only.

