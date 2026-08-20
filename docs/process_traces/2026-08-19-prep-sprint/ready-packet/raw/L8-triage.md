# RAW TRIAGE EXTRACT — L8-OPERATOR-RECOVERY-HUMAN-FACTORS

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L8-OPERATOR-RECOVERY-HUMAN-FACTORS`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 21/24 (evidence_universe_count=24)
- findings: 15; falsifiers: 8

## FINDINGS (verbatim)

### F1 [blocker] No shipped producer for the T-0 input files the evidence author requires
- file_line: `joulewise/arm_readiness_evidence_t0.py:448-499,595-724 vs docs/phase_2/window_runbook.md:802-838`
- failure_scenario (verbatim): Ed completes E-4…E-9 exactly as the runbook/packet write them, runs the T-0 author, and gets REFUSE evidence_author_t0_clock_attestation_missing (executed): the author consumes nine byte-canonical JSON inputs (six command captures with monotonic timestamps + clock-attestation + arm-context + launch-manifest) that no tool, no runbook step, and no packet step produces; the only 2am path forward is hand-fabricating canonical JSON with invented monotonic_ns values, which the receipts cannot distinguish from honest capture

### F2 [blocker] The frozen E-7b command cannot prove the ≥10-minute idle the author enforces
- file_line: `scripts/prewindow_check.sh:36-37,177-198 vs joulewise/arm_readiness_evidence_t0.py:49,954-957 vs runbook:366-373,780-789`
- failure_scenario (verbatim): On a well-prepared (clean) machine, `prewindow_check.sh --wait` exits READY after 3 checks × 30 s ≈ 61 s (per-check cost measured at 0.156 s); the T-0 author refuses any prewindow capture shorter than 600 s, so the better Ed prepares the machine the more certainly authoring refuses — and if the author did not enforce it, the window would launch into the XProtect idle-daemon band that cost window a9's first member, now unrecoverable because the one-launch capability makes relaunch a newly frozen session

### F3 [blocker] CLOCK_PROBE needs sudo -n systemsetup, which D-004's powermetrics-only sudoers cannot satisfy
- file_line: `joulewise/arm_readiness_evidence_t0.py:884-905; docs/decision_log.md:316; runbook:509-514`
- failure_scenario (verbatim): At authoring time (>10 min after E-4/E-5 because E-7b's wait sits between), the interactive sudo timestamp is cold and the sudoers NOPASSWD entry covers only /usr/bin/powermetrics, so the fresh `sudo -n systemsetup -getusingnetworktime` probe exits nonzero → clock.network_time_off underivable → author REFUSE → no GO receipt, with no documented recovery at night

### F4 [blocker] Committed freeze receipt is stale — the ALPHA pack cannot arm at the audit baseline
- file_line: `configs/campaigns/d117_floor_qwen25_1p5b_v1/arm_readiness.freeze.receipts/freeze-0001.json (pack_identity.pack_root=/Users/edr/JouleWise-measurement-20260813/…) vs joulewise/arm_readiness.py:3604-3610`
- failure_scenario (verbatim): Executed: every `generate_arm_readiness.py arm` invocation at the baseline head refuses readiness_freeze_receipt_mismatch before row evaluation, because freeze-0001.json binds the pre-#149 measurement-tree pack identity while the committed digest is now f4c02c8a…; the pack also still self-describes 'unfrozen draft / not armable' (M-2), which §5C's entry gate treats as NO-GO — a re-freeze plus magistrate ruling must precede any night

### F5 [blocker] The FINAL arm packet's tap script is stale against the baseline runbook and would run the wrong night sequence
- file_line: `~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md §3 (frozen tree 49dcc49a, digest 6246b618) vs runbook:802-838 and manifest head ac3fe1d2/digest f4c02c8a`
- failure_scenario (verbatim): The packet is expressly 'written to be executed without reading the runbook', yet it contains no T-0 authoring E-step, no 20-minute volatile horizon, no re-author rule, and expects §0.6's 'no shipped authoring route' refusal that no longer matches the shipped tooling; a tired Ed following it verbatim goes E-9 → E-9a and dead-ends (or worse, improvises) at the exact point the current runbook inserts the author step

### F6 [blocker] Runbook §4 window.env example and §6 chain template fail the T-0 author's own machine contract
- file_line: `runbook:181-206 ($-values, WINDOW_CUSTODY_ROOT/BACKUP_DEST naming, FROZEN_PLAN=custody reservation JSON) and runbook:971 (REPO=${MEASUREMENT_REPO:-…}) vs joulewise/arm_readiness_evidence_t0.py:571-593,652-676,1138-1156`
- failure_scenario (verbatim): A freeze-step that copies the runbook's own example produces window.env with $-containing values (parser refuses as ambiguous), missing CUSTODY_ROOT/CLAIM_BACKUP_DEST/BOUND_BACKUP_DEST keys, a FROZEN_PLAN that is not the pack's calibration_plan.json (E-8 capture argv then fails the reviewed-literal check), and a chain whose REPO line fails the exact-binding regex — four independent guaranteed authoring refusals discovered only at night

### F7 [blocker] Launch without arm/consume ceremony is not machine-caught at launch or by any downstream consumer
- file_line: `runbook:964-1148 (window-chain.zsh performs no receipt check); grep: arm_readiness.consumptions referenced only in joulewise/arm_readiness.py and arm_readiness_evidence_t0.py`
- failure_scenario (verbatim): Ed (or a rushed magistrate) skips E-9a/b/c after the E-9 reservation and runs the launch recipe: the chain settles, calibrates and collects a normal-looking window with no refusal anywhere; the only gate on the missing arm/consumption lineage is human close-out item 5 — the required launch-license output neither traces through a machine consumer nor fails closed (cross-confirm consumer side with L5/L6/L7/L10)

### F8 [should_fix] Arm CLI demands the ARM_CONTEXT JSON inline while the authenticated arm-context.json already sits in custody
- file_line: `scripts/generate_arm_readiness.py:58-70; runbook:834-848`
- failure_scenario (verbatim): Inside the 20-minute volatile fuse Ed must supply a ~700-character exact-key JSON object on the command line; any drift from the t0.inputs arm-context breaks cross-binding, and the obvious workaround `--arm-context "$(cat …)"` is nowhere documented — accept the custody path or freeze the cat-substitution literal in the packet

### F9 [should_fix] The 5-minute arm-receipt validity fuse is documented nowhere the operator can see
- file_line: `joulewise/arm_readiness.py:3596 (validity_ns=300_000_000_000), :3952-3955; absent from runbook §5C and the packet`
- failure_scenario (verbatim): Ed pauses six minutes between E-9a and E-9c to phone the magistrate with the receipt sha; verify/consume refuse readiness_record_expired; nothing tells him a re-arm inside the surviving 20-minute evidence horizon is the licensed recovery, so the night ends on a recoverable refusal

### F10 [should_fix] Re-author cleanup is a raw rm -r on custody paths with no shape verification
- file_line: `runbook:823-827`
- failure_scenario (verbatim): At 2am after a reboot, a mistyped $PACK_ID that resolves to a sibling pack's custody removes that pack's T-0 namespaces irreversibly with no confirmation and no receipt; the only guard is the prose instruction to 'first verify' (executed: the unset-vars variant is harmless, the wrong-existing-path variant has no catch)

### F11 [should_fix] Morning restore (E-16) before the magistrate finishes has no machine catch
- file_line: `runbook:557-568; packet §3.5`
- failure_scenario (verbatim): Ed restores network time at tap 2 before the magistrate reports verdict+margin+backups complete; systemsetup succeeds silently, the wall clock may slew under the still-running clock-anchored close-out reads, and only honestly-recorded §12 item-20 timestamps could ever reveal it — the two-tap gap is purely procedural

### F12 [should_fix] In-horizon TOCTOU: post-authoring process starts are not re-probed at arm/verify/consume
- file_line: `joulewise/arm_readiness_evidence_t0.py:47 (design comment); verify/consume re-check only horizon+boot+roots`
- failure_scenario (verbatim): Ed starts a browser 'just to check the time' after authoring; all receipts stay valid for the remaining horizon and ARM/consume pass; the bounded 20-minute window is a deliberate design trade but the runbook's prohibition ('do not start any new … process') has no teeth inside it — the recut packet must carry the prohibition as an explicit ABORT row

### F13 [nit] prewindow check 8's agent pattern omits claude/t3 and check 4 WARN-only without admin
- file_line: `scripts/prewindow_check.sh:102-110,155`
- failure_scenario (verbatim): Executed: check 8 printed OK while this live Claude session ran; between E-7b and authoring, only prewindow guards the machine and it cannot see a forgotten claude/t3 process (the T-0 census later catches it)

### F14 [nit] E-14 do-not-return-before time is hand arithmetic at T-0
- file_line: `packet §3.4 E-14; plan 6.28 h = 6 h 16.8 m`
- failure_scenario (verbatim): A 2am mental addition of 6.28 h invites an early return; the recut packet should carry a `date -v+377M` literal

### F15 [nit] ED-session census pattern is substring-based and false-positive-prone (fails closed)
- file_line: `scripts/ed_session/rail-probe.sh:48, sampler-checklist.sh:44`
- failure_scenario (verbatim): Executed: any process whose argv merely contains 'powermetrics' (test fixtures, a plist path) refuses the qualification run; harmless for soundness but a qualification session run beside any dev activity will refuse spuriously

## WORK ORDERS (verbatim)

- WO-L8-1: Ship the operator capture wrapper — a tracked script that runs each E-step command, records the byte-canonical capture JSON (argv/cwd/exit/stdout/stderr/started+finished_monotonic_ns/boot_session_id, exact _COMMAND_SCHEMA) plus clock-attestation.json, arm-context.json and launch-manifest.json into ARM_READINESS_CUSTODY_ROOT/PACK_ID/arm_readiness.t0.inputs/ — and rewrite runbook §5C E-4…E-9 to use it; without it the fifteen-row author cannot be honestly satisfied and invites hand-forged monotonic timestamps

- WO-L8-2: Give prewindow_check.sh --wait a minimum-wall-clock floor (refuse READY before 600 s) so the frozen E-7b literal can actually prove the ≥10-minute idle the T-0 author enforces; re-freeze the command literal afterward

- WO-L8-3: Resolve the CLOCK_PROBE privilege route (scoped sudoers read entry or documented sudo -v warm-up) and rehearse it (ED-Q-L8-1)

- WO-L8-4: Re-freeze the ALPHA pack at the final audited head (current freeze-0001.json is pre-#149 schema bound to the 2026-08-13 measurement tree → every arm refuses readiness_freeze_receipt_mismatch), and obtain the magistrate ruling on the pack's 'unfrozen draft / not armable' self-description (packet M-2/D-13)

- WO-L8-5: Recut the FINAL arm packet at the final head — its tap script omits T-0 authoring, the 20-minute volatile horizon, the 5-minute arm-receipt fuse and the re-author rule; include paste-ready E-9a/b/c literals (arm-context via $(cat …/arm-context.json)), and a date(1) one-liner for the E-14 do-not-return-before time

- WO-L8-6: Make runbook §4/§6 templates byte-consistent with the T-0 author contract: window.env must carry literal (no-$) values including CUSTODY_ROOT, CLAIM_BACKUP_DEST, BOUND_BACKUP_DEST; FROZEN_PLAN must be the pack's calibration_plan.json; the chain REPO line must be the bare reviewed-checkout literal (the ${MEASUREMENT_REPO:-…} fallback fails the author's exact-binding regex) — or generate window.env/window-chain.zsh mechanically from the pack

- WO-L8-7: Machine-enforce the launch license: window-chain.zsh preamble (or the first claim consumer) must require the matching arm_readiness.consumptions receipt for this pack/boot before proceeding — today a launch with zero arm ceremony runs a normal-looking window and nothing downstream reads the consumption namespace

- WO-L8-8: Replace the re-author /bin/rm -r prose with a governed `reauthor-clean` operation that verifies the two T-0 namespace shapes before deleting

## ED-QUALIFICATION ROWS (verbatim)

- ED-Q-L8-1 (sudo): decide and prove the privileged read path for the T-0 CLOCK_PROBE — either a scoped read-only sudoers entry for `/usr/sbin/systemsetup -getusingnetworktime` or a ratified `sudo -v` warm-up literal immediately before the T-0 author — and exercise it once in a tap block; D-004's powermetrics-only NOPASSWD plus a >10-min-cold sudo timestamp otherwise guarantees an authoring refusal at night

- ED-Q-L8-2 (sudo + Ed): full arm-sequence dress rehearsal on the recut packet — E-4→E-9 under the capture wrapper, T-0 authoring, arm→verify→consume against scratch custody/synthetic roots, with a real ≥10-minute prewindow wait — timed against the 20-minute volatile horizon and 5-minute arm-receipt fuse

- ED-Q-L8-3 (sudo, already chartered as steps 2-3): live sampler-checklist and keyboard-backlight rail-probe executions on a quiet machine (dry-run staging verified in this audit; the live arms and teardown censuses still need sudo)

- ED-Q-L8-4 (sudo): live quiet_mac_prep.sh run to confirm its three OK literals (passwordless powermetrics, displays asleep, screensaver disengaged) match what the T-0 author's _quiet_capture requires verbatim

## UNEXECUTED OBLIGATIONS (verbatim)

- scripts/quiet_mac_prep.sh live execution (transient display sleep + sudo -n powermetrics probe) — static review only; live run needs sudo and violates the quiet-machine/agent boundary

- Live sudo paths of rail-probe.sh and sampler-checklist.sh (the actual ABBA captures and supervised 5-sample check) — no sudo in this sandbox; ED-QUALIFICATION rows

- E-9 reservation behavior against a ledger copy (double-reserve, live-writer refusals) — code-read and shipped-test evidence only; primary ownership is the L2 seat

- Runbook §10 refusal-row completeness for the 2am operator (packet O-9's missing one-page extract) — read but not row-by-row audited; flagged to L2/L6/L7

- Morning §9/§11 magistrate procedures beyond ordering review — L10 sacrificial-lifecycle scope

- The real dry-run receipt and skeleton in ~/JouleWise-window-custody were read but deliberately not touched or re-verified in place

