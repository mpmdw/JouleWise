# READINESS COUNCIL SITTING PACKET — mechanically assembled 2026-08-14 (T7 session)

Assembly: scripted extraction from fleet run wf_29eee330-1db journal; zero editorial text in sections 2-6. Section sha16s bind the custodied inputs.

## 1. Baseline + provenance
- audit-baseline-manifest: head_commit ac3fe1d; working head at fleet+refuter launch: 8937dec9bd7be8f6d87694a739089ac8434b8bc9
- fleet: 11/11 seats returned, 2,411,618 subagent tokens, 1083 tool uses, 46.7 min wall
- seat reports custodied: fleet-harvest/L*-report.md (sha16 per file below)
  - L1-AUTHORITY-PLANE: a352d956c8681657
  - L10-SACRIFICIAL-FULL-LIFECYCLE: c8f2e0530da08faa
  - L11-retained-characterization-basis: 484a6a0421fd421a
  - L2-CALIBRATION-ACQUISITION: 54b6e67c24f752e5
  - L3-CAPTURE-TELEMETRY-xhigh: 2ee51138ea4dcf7f
  - L4-quantitative-claim-pipeline: 8f4434e3e3447de5
  - L5-PACK-READINESS-CUSTODY: ec83d2a3d6a1ee55
  - L6-SEAM-READER-A: 054da78691dc175b
  - L7-SEAM-READER-B-EXECUTION: 1657a255f951b7f4
  - L8-OPERATOR-RECOVERY-HUMAN-FACTORS: 80cd36a6d19f95f4
  - L9-environmental-controls-census: 8ed06561c5301636

## 2. Seat verdict table
| lens | gating | verdict | coverage | blockers | should-fix | nits | falsifiers | unexec | ed-qual |
|---|---|---|---|---|---|---|---|---|---|
| L6-SEAM-READER-A | GATING | NOT_READY | 34/40 | 2 | 3 | 3 | 5 | 6 | 2 |
| L1-AUTHORITY-PLANE | GATING | NOT_READY | 20/24 | 3 | 3 | 2 | 7 | 5 | 2 |
| L5-PACK-READINESS-CUSTODY | GATING | NOT_READY | 16/18 | 0 | 3 | 2 | 8 | 4 | 1 |
| L2-CALIBRATION-ACQUISITION | GATING | READY | 15/16 | 0 | 2 | 2 | 4 | 5 | 2 |
| L3-CAPTURE-TELEMETRY-xhigh | GATING | NOT_READY | 25/29 | 0 | 3 | 2 | 3 | 7 | 4 |
| L7-SEAM-READER-B-EXECUTION | GATING | NOT_READY | 21/25 | 0 | 2 | 1 | 7 | 7 | 3 |
| L10-SACRIFICIAL-FULL-LIFECYCLE | GATING | NOT_READY | 15/18 | 1 | 3 | 1 | 13 | 5 | 1 |
| L4-quantitative-claim-pipeline | GATING | NOT_READY | 24/27 | 1 | 2 | 1 | 4 | 5 | 1 |
| L9-environmental-controls-census | GATING | NOT_READY | 14/16 | 2 | 3 | 3 | 4 | 6 | 3 |
| L8-OPERATOR-RECOVERY-HUMAN-FACTORS | GATING | NOT_READY | 21/24 | 7 | 5 | 3 | 8 | 6 | 4 |
| L11-retained-characterization-basis | non-gating | NOT_READY | 14/16 | 0 | 3 | 2 | 5 | 6 | 0 |

Aggregation per charter: READY requires no NOT-READY + no UNVERIFIED + all ED-QUAL rows closed. Raw aggregate: 1 READY / 10 NOT_READY -> council verdict candidate: NOT-READY(+work orders).

## 3. Blocker findings (16, verbatim) — refuter verdicts pending, slots below
### L6-SEAM-READER-A B1: B1 — The T-0 evidence author's own inputs have no producer: no tool, no runbook step, no packet step
at: joulewise/arm_readiness_evidence_t0.py:42,132-139,506,556,601; docs/phase_2/window_runbook.md:812-827
scenario: The funded night reaches §5C's post-E-9 authoring step; author_arm_evidence_t0.py refuses evidence_author_t0_clock_attestation_missing (demonstrated live in probe P3) because nothing has created CUSTODY/PACK_ID/arm_readiness.t0.inputs/ — the author requires clock-attestation.json, arm-context.json, launch-manifest.json and six command captures (clock-prior-state, clock-disable, quiet-mac-prep, prewindow-check, ledger-readiness, ledger-reservation) as canonical JSON with boot-bound monotonic-ns fields no human can hand-produce; no repo tool writes joulewise.arm_readiness_t0_command_capture.v1 (grep: only the author itself references the schema), the runbook never names arm_readiness.t0.inputs, and the FINAL arm packet predates the author entirely. Night ends NO-GO — or worse, the operator hand-crafts nine JSON files at 2 a.m., the exact anti-pattern the readiness machinery exists to prevent.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L6-SEAM-READER-A B2: B2 — Committed freeze evidence is already past its 24 h monotonic horizon; every future window requires an undocumented full freeze-refresh lane
at: joulewise/arm_readiness.py:2943-2975,3712-3719; docs/phase_2/window_runbook.md:726-742,812-830
scenario: Live reading on the freeze boot session: now-monotonic 1,996,764 s > valid_until 1,986,799 s — all 11 generic PACK evidence receipts frozen 2026-08-13 are expired. generate_arm_receipt folds evidence expirations into the arm receipt's valid_until (min(...)), so any arm receipt issued now is expired at birth; verify/consume then refuse readiness_record_expired (arm_readiness.py:3952-3955). Cure = re-author 11 receipts + new freeze receipt + plan-tree re-pin + commit + review + fresh dry-run, same boot session as ARM and ≤24 h before it — a cycle no operative document names: §4 presents freeze as 'before quiet time' desk work, §5C's re-author rm covers only the two T-0 namespaces, and the reboot-fence paragraph says only 'generate new receipts'. Fails closed at every probe point, so no consumption unsoundness — but a required output (a valid GO arm receipt) currently has no producible path under the frozen packs + current runbook alone, and the refresh commits void the audit baseline per charter amendment 12.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L1-AUTHORITY-PLANE B1: Frozen packs cannot arm: all 33 freeze evidence receipts have lapsed their monotonic validity on the un-rebooted arming machine
at: configs/campaigns/*/arm_readiness.evidence/*.json; joulewise/arm_readiness.py:3710-3717,3948-3955
scenario: Ed attempts tonight's slipped Window ALPHA arm: generate_arm_receipt authenticates the pack freeze evidence (boot session matches — no reboot occurred), but the arm receipt's valid_until is min-inherited from evidence expirations that are already in the past (earliest 1986799611717708 ns vs live ~1997.9e12 ns), so verify_arm_receipt refuses readiness_record_expired and consume_launch_capability can never fire. The direction is correctly fail-closed, but the funded window is unlaunchable under the audited bytes; the recorded standing constraint ('NO REBOOT before T-0 or the evidence re-authors') is insufficient — no reboot happened and the capability still died of monotonic age from the window slip. Remedy (re-author evidence, reissue freeze receipt, re-pin plan tree, recommit) changes pack bytes, rotates the committed pack digests, and voids the audit-baseline manifest's pack digests under charter amendment 12 — the council must schedule this re-freeze before or at GO.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L1-AUTHORITY-PLANE B2: Authoritative work-selection state fails open for quiet-window selection: no council gate, and a superseded campaign renders READY [QUIET-MAC]
at: docs/process/state_kernel.json (active_global_gates: []); RUN_STATE.md:3433
scenario: A successor session or tired operator obeys RUN_STATE's generated region, which today renders 'READY — Q2 P2-006: Window A two-model campaign' with zero active global gates — despite Ed's 2026-08-13 window-gating directive (windows sit behind the council verdict) and despite D-117 having superseded the Window-A program. A quiet night gets spent on a campaign whose outputs do not trace to the current claim path, bypassing the council gate entirely, because the gate exists only in decision-log prose while the kernel's purpose-built gate machinery (proven working by probe) carries no gate row. The actual funded program (three frozen D-117 packs) has no kernel row at all.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L1-AUTHORITY-PLANE B3: Work-selection authority is bifurcated: launch-blocking work orders live as hand-written prose outside the generated region while kernel rows assert falsehoods
at: TASK_QUEUE.md:201,635,659 (outside markers 452-613); docs/process/state_kernel.json /tasks/D117-U11-IDPIN-PROJECTION
scenario: WO-MINT-ESTIMATOR-VOCAB, WO-COLLECTION-MARGIN-01, and WO-ARM-EVIDENCE-AUTHOR-01 ('LAUNCH-BLOCKING for any window night') were 'registered in TASK_QUEUE' as hand-written sections outside the marker-fenced generated region — invisible to gen_state --check and absent from the kernel, violating DOC-008's single-authority contract. Simultaneously the kernel's D117-U11-IDPIN-PROJECTION row still reads 'queued... Checked-in packs remain unprojected' at a head whose packs carry PASS projection and freeze receipts, and FLOOR-COMMONMODE-01 renders 'READY [AGENT]' despite its D-133 desk-thread disposition. A session trusting the declared AUTHORITATIVE_WORK_SELECTION_STATE misses launch-blocking obligations or resumes disposed work; a session trusting the prose contradicts the kernel.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L10-SACRIFICIAL-FULL-LIFECYCLE B1: Frozen packs' claim-consumption edge is unbuilt: analyze-claims refuses the packs' v3.prospective manifests, the U7-designed prospective builder/validator do not exist, and the final-v3 wire is hard-pinned to splitwise
at: joulewise/analysis_engine/inputs.py:556-568; joulewise/analysis_manifest_v3.py:613,630-663; configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:2
scenario: The funded gamma window collects clean, the verdict passes, alpha/beta floors mint into the aggregate — and the contrast claim cannot be consumed: analyze-claims refuses 'unsupported analysis manifest schema_version: joulewise.analysis_manifest.v3.prospective' (executed); validate_analysis_manifest_v3 hard-requires design_id splitwise_decode_cross_model_abba_v1, the splitwise generator path/plan sha, exactly two stages and n=10, so no hand-authored final D-117 manifest can validate either; grep finds zero implementations of the U7-specified build_prospective_analysis_manifest_v3 / validate_prospective_analysis_manifest_v3 and no postcollection-attachment finalizer; no TASK_QUEUE row tracks this edge. The window is spent and its REQUIRED OUTPUT cannot trace through a claim consumer without landing new code post-hoc, colliding with L1 same-session custody discipline.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L4-quantitative-claim-pipeline B1: Margin recorder cannot read the re-specced frozen floor-pack extraction specs — ALPHA/BETA close-out halts deterministically at runbook section 11
at: joulewise/window_duration_margins.py:897 (session) + :394 (spec read); cause joulewise/authentication_io.py:179,214; missing authorization mirror of scripts/mint_floor_artifact_generalized.py:1758-1759,3683
scenario: A funded quiet window collects ALPHA cleanly; the operator runs the exact runbook section-11 command; the recorder opens its V2AuthenticationReadSession and reads the pack-pinned spec, which since the D-133 cl.4 re-spec carries estimator_registration in all comparative cells; the session's reserved-vocabulary rule refuses (executed: REFUSE authoritative_input_invalid, exit 2, no receipt); 'REFUSE stops close-out without writing a receipt' — backup/extraction never run under the mandated order, the window cannot be called claim-bearing, and the standing constraint 'collection close-out gates on the WO-COLLECTION-MARGIN-01 receipt' is unsatisfiable on every attempt. Only the mint authorizes governed-spec vocabulary (allow_governed_extraction_spec); the recorder never does. The committed census tests (tests/test_window_duration_margins.py:213,514) model 'real floor pack cell shapes' WITHOUT the estimator vocabulary, so the suite is green while the real seam is broken — the charter's producer-gap type specimen.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L9-environmental-controls-census B1: t0.background_quiet (MAINTENANCE_CENSUS) is unpassable on the real machine — arm always refuses
at: joulewise/arm_readiness_evidence_t0.py:963-980
scenario: ALPHA arm night: agents closed, machine genuinely quiet. author_arm_evidence_t0.py runs _maintenance_probe; pgrep -lf matches permanently resident Spotlight.app, mds_stores, XProtect XPC services, mediaanalysisd, photoanalysisd, softwareupdated, backupd-helper (~20 matches observed live); _expect_absent raises underivable → no T-0 evidence → no arm receipt → NO-GO on every attempt. Fail-closed (no false data risk) but the window can never launch. CI never saw this: tests fake the probe executor with exit_code=1 (tests/test_arm_readiness_evidence_t0.py:561).
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L9-environmental-controls-census B2: t0.no_stray_keepawake (PROCESS_CENSUS) is unpassable — browser/monitor patterns match permanent system daemons
at: joulewise/arm_readiness_evidence_t0.py:1344-1360
scenario: Same arm night: 'Safari|...' matches 9 always-resident Safari LaunchAgents with Safari closed; 'watch' substring in the monitor pattern matches watchdogd (permanent) and watchlistd. _expect_absent refuses → arm NO-GO forever. The keep-awake (pgrep -x caffeinate) and agent (codex|claude|t3) probes are correct and verified effective live; only the browser and monitor patterns over-match.
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B1: No shipped producer for the T-0 input files the evidence author requires
at: joulewise/arm_readiness_evidence_t0.py:448-499,595-724 vs docs/phase_2/window_runbook.md:802-838
scenario: Ed completes E-4…E-9 exactly as the runbook/packet write them, runs the T-0 author, and gets REFUSE evidence_author_t0_clock_attestation_missing (executed): the author consumes nine byte-canonical JSON inputs (six command captures with monotonic timestamps + clock-attestation + arm-context + launch-manifest) that no tool, no runbook step, and no packet step produces; the only 2am path forward is hand-fabricating canonical JSON with invented monotonic_ns values, which the receipts cannot distinguish from honest capture
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B2: The frozen E-7b command cannot prove the ≥10-minute idle the author enforces
at: scripts/prewindow_check.sh:36-37,177-198 vs joulewise/arm_readiness_evidence_t0.py:49,954-957 vs runbook:366-373,780-789
scenario: On a well-prepared (clean) machine, `prewindow_check.sh --wait` exits READY after 3 checks × 30 s ≈ 61 s (per-check cost measured at 0.156 s); the T-0 author refuses any prewindow capture shorter than 600 s, so the better Ed prepares the machine the more certainly authoring refuses — and if the author did not enforce it, the window would launch into the XProtect idle-daemon band that cost window a9's first member, now unrecoverable because the one-launch capability makes relaunch a newly frozen session
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B3: CLOCK_PROBE needs sudo -n systemsetup, which D-004's powermetrics-only sudoers cannot satisfy
at: joulewise/arm_readiness_evidence_t0.py:884-905; docs/decision_log.md:316; runbook:509-514
scenario: At authoring time (>10 min after E-4/E-5 because E-7b's wait sits between), the interactive sudo timestamp is cold and the sudoers NOPASSWD entry covers only /usr/bin/powermetrics, so the fresh `sudo -n systemsetup -getusingnetworktime` probe exits nonzero → clock.network_time_off underivable → author REFUSE → no GO receipt, with no documented recovery at night
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B4: Committed freeze receipt is stale — the ALPHA pack cannot arm at the audit baseline
at: configs/campaigns/d117_floor_qwen25_1p5b_v1/arm_readiness.freeze.receipts/freeze-0001.json (pack_identity.pack_root=/Users/edr/JouleWise-measurement-20260813/…) vs joulewise/arm_readiness.py:3604-3610
scenario: Executed: every `generate_arm_readiness.py arm` invocation at the baseline head refuses readiness_freeze_receipt_mismatch before row evaluation, because freeze-0001.json binds the pre-#149 measurement-tree pack identity while the committed digest is now f4c02c8a…; the pack also still self-describes 'unfrozen draft / not armable' (M-2), which §5C's entry gate treats as NO-GO — a re-freeze plus magistrate ruling must precede any night
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B5: The FINAL arm packet's tap script is stale against the baseline runbook and would run the wrong night sequence
at: ~/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md §3 (frozen tree 49dcc49a, digest 6246b618) vs runbook:802-838 and manifest head ac3fe1d2/digest f4c02c8a
scenario: The packet is expressly 'written to be executed without reading the runbook', yet it contains no T-0 authoring E-step, no 20-minute volatile horizon, no re-author rule, and expects §0.6's 'no shipped authoring route' refusal that no longer matches the shipped tooling; a tired Ed following it verbatim goes E-9 → E-9a and dead-ends (or worse, improvises) at the exact point the current runbook inserts the author step
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B6: Runbook §4 window.env example and §6 chain template fail the T-0 author's own machine contract
at: runbook:181-206 ($-values, WINDOW_CUSTODY_ROOT/BACKUP_DEST naming, FROZEN_PLAN=custody reservation JSON) and runbook:971 (REPO=${MEASUREMENT_REPO:-…}) vs joulewise/arm_readiness_evidence_t0.py:571-593,652-676,1138-1156
scenario: A freeze-step that copies the runbook's own example produces window.env with $-containing values (parser refuses as ambiguous), missing CUSTODY_ROOT/CLAIM_BACKUP_DEST/BOUND_BACKUP_DEST keys, a FROZEN_PLAN that is not the pack's calibration_plan.json (E-8 capture argv then fails the reviewed-literal check), and a chain whose REPO line fails the exact-binding regex — four independent guaranteed authoring refusals discovered only at night
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

### L8-OPERATOR-RECOVERY-HUMAN-FACTORS B7: Launch without arm/consume ceremony is not machine-caught at launch or by any downstream consumer
at: runbook:964-1148 (window-chain.zsh performs no receipt check); grep: arm_readiness.consumptions referenced only in joulewise/arm_readiness.py and arm_readiness_evidence_t0.py
scenario: Ed (or a rushed magistrate) skips E-9a/b/c after the E-9 reservation and runs the launch recipe: the chain settles, calibrates and collects a normal-looking window with no refusal anywhere; the only gate on the missing arm/consumption lineage is human close-out item 5 — the required launch-license output neither traces through a machine consumer nor fails closed (cross-confirm consumer side with L5/L6/L7/L10)
REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

## 4. Should-fix (32) + nits — full text in seat reports; titles only here
- [should_fix] [L6] S2 — D-117 two-stage mint freeze: the stage-1 desk pin artifact (floor_mint_pin_requirements.v2) has no committed instance and nothing fails closed on its absence
- [should_fix] [L6] S3 — §12's postcollection backup receipts have no producer: backup_runs.sh emits no receipt and no hash
- [should_fix] [L6] S4 — The FINAL arm packet (the operator's night document, cited by the audit-baseline manifest) is stale against the baseline runbook
- [nit] [L6] N1 — window_duration_margins_receipt.v1 has no machine consumer; §11 ordering is unenforced
- [nit] [L6] N2 — PRIVILEGE_INSTALLATION evidence kind has no producer anywhere in the repo
- [nit] [L6] N3 — The arm-time freeze-evidence replay skips the monotonic-horizon check; defense is one hop downstream
- [should_fix] [L1] D-118's 'mechanical enforcement' of the merge gate ledger does not exist anywhere in the repo
- [should_fix] [L1] kernel.updated and latest_report are false, and no invariant forces them to move
- [should_fix] [L1] FREEZE-FCM01.md's standing prohibition was never amended after D-133 cl.4 executed the re-spec
- [nit] [L1] Frozen pack bytes still carry draft_status 'unfrozen_draft' — the M-2 scoped override remains the operative instrument indefinitely
- [nit] [L1] gen_state invariant 8's D-041 authority binding is a label-substring match
- [should_fix] [L5] Floor-pack plan tests self-pollute the frozen packs and fail deterministically from a clean tree; CI-green status unexplained
- [should_fix] [L5] Generator --check echo hole in preserve mode: plan_tree.json, plan_tree.sha256, producer_contract.json are compared against themselves
- [should_fix] [L5] Pre-arm sequence unregistered: measurement checkout must advance and the §5C dry-run must be re-executed at the final head (dry-run-0001 is stale by binding)
- [nit] [L5] --check prints 'verified unfrozen draft' on frozen packs
- [nit] [L5] M-2 decision-log remedy wording diverges from the implemented preserve-bytes behavior
- [should_fix] [L2] detect_pulses region projection has no work budget — non-termination on degenerate traces while holding the writer lease
- [should_fix] [L2] readiness/session-status crash with an unregistered raw traceback when the ledger parent directory is missing
- [nit] [L2] Runbook needs_pin_commit bullet is unscoped vs the by-design PHYSICAL_AHEAD pre-slot relation
- [nit] [L2] Idempotent re-reservation returns status:reserved without re-printing calibration_pre_reserve_authorized
- [should_fix] [L3] Measured-run (adapter/controller) path has no post-teardown sampler census; kill-escalation orphan samples invisibly through the rest of a window
- [should_fix] [L3] ED-qualification Step 2 points at a checklist home that does not contain the checklist
- [should_fix] [L3] ED sampler checklist qualifies cadence at 1 Hz while every production surface runs 100 ms
- [nit] [L3] Post-JW-MET-1 residual: retained related-work draft still describes JouleWise with system-on-chip boundary language
- [nit] [L3] samplers_available metadata echoes the requested list rather than a probed census
- [should_fix] [L7] Frozen PACK-namespace evidence is consumed at arm/verify/consume without its declared monotonic horizon being checked — and all 33 frozen receipts' horizons have ALREADY lapsed
- [should_fix] [L7] Mandatory pre-arm sequence is undocumented: the runbook's E-step tool does not exist at the frozen measurement-checkout head, and advancing the checkout stales the recorded §5C dry-run receipt
- [nit] [L7] `joulewise reduce` writes its re-reduction artifact into the invoker's CWD by default
- [should_fix] [L10] Runbook §11 extraction command as frozen refuses at argparse: --evaluation-basis-sha256 without the co-required --consumption-semantics-id
- [should_fix] [L10] Runbook §11 margins-recorder identity mismatch: --pack-identity "$WINDOW_ID" (window_a9_YYYYMMDD convention per §4) can never satisfy the recorder's plan-derived window_id requirement
- [should_fix] [L10] L1 same-custody-session limitation structurally conflicts with the three-window design's cross-session floor consumption; FLOOR-BIND-01 is READY but unclosed
- [nit] [L10] backup_runs.sh counts campaign_manifests/ as a bundle in operator-facing output (reported 5 bundles for a 4-member window)
- [should_fix] [L4] GAMMA contrast both-gates consumption route is unbuilt: prospective manifest refused by the loader, sole frozen-v3 builder hard-pinned to the splitwise campaign
- [should_fix] [L4] Margin-receipt consumption never mechanically binds to the FROZEN pack: a repinned truncated pack yields a plausible PASS and the receipt validator accepts a truncated sha-repaired receipt
- [nit] [L4] validate_floor_artifact's recomputation tolerance accepts a one-ULP-understated floor; tamper-evidence rides on byte custody, not numeric revalidation
- [should_fix] [L9] prewindow_check.sh agent census misses claude / codex mcp-server / t3 — printed OK while three agent processes were live
- [should_fix] [L9] No single-home hazard register; consult-mandated hazards entirely absent: radios, notifications, peripherals, remote sessions, third-party LaunchAgents
- [should_fix] [L9] Mid-workload background contamination has no member-level detector and no documented disposition
- [nit] [L9] JW-MET-2's four census literals have no named custody destination in the §12 close-out list
- [nit] [L9] Battery charge state is censused but has no gate or disposition
- [nit] [L9] Lid state is operator-discipline only, never probed
- [should_fix] [L8] Arm CLI demands the ARM_CONTEXT JSON inline while the authenticated arm-context.json already sits in custody
- [should_fix] [L8] The 5-minute arm-receipt validity fuse is documented nowhere the operator can see
- [should_fix] [L8] Re-author cleanup is a raw rm -r on custody paths with no shape verification
- [should_fix] [L8] Morning restore (E-16) before the magistrate finishes has no machine catch
- [should_fix] [L8] In-horizon TOCTOU: post-authoring process starts are not re-probed at arm/verify/consume
- [nit] [L8] prewindow check 8's agent pattern omits claude/t3 and check 4 WARN-only without admin
- [nit] [L8] E-14 do-not-return-before time is hand arithmetic at T-0
- [nit] [L8] ED-session census pattern is substring-based and false-positive-prone (fails closed)
- [should_fix] [L11] Paper presents the ±31 ms / 33 W / ~1 J triple as 'the measured corpus figure'; it is a single-member maximum plus a derived quotient
- [should_fix] [L11] Paper attributes the phase mis-attribution evidence to 'the a9 and a10 windows'; a9 contains zero phase-absolute members
- [should_fix] [L11] Whole-window PASSED verdicts for a9/a10 exist only as close-out prose; no verdict artifact is retained anywhere findable
- [nit] [L11] a9 MANIFEST.sha256 lists ./backup.log, which is neither resident nor covered by PRUNED.md's enumeration
- [nit] [L11] Two D-054 decision-log prose details do not reproduce exactly from the retained bundles

## 5. ED-QUALIFICATION rows (verbatim, 23)
- [L6] ED-QUAL-L6-1 (stable capability, any tap block): execute the T-0 authoring path live on the measurement Mac — once the B1 capture helper exists, run the six E-step captures + clock attestation + launch manifest into arm_readiness.t0.inputs/ and author_arm_evidence_t0.py end-to-end under real passwordless-sudo powermetrics (POWERMETRICS_PROBE) and real systemsetup state (CLOCK_PROBE), confirming all 15 receipts author and a same-boot `generate_arm_readiness.py arm` reaches row evaluation. This lens could only prove the refusal side (P3) from the sandbox; the PASS side of the arm-plane producer seam needs Ed's machine and sudo.
- [L6] ED-QUAL-L6-2 (stable capability, desk, no sudo but Ed's checkout): one full freeze-refresh rehearsal timed against the 24 h/same-boot coupling of B2 — re-author pack evidence, re-freeze, commit, dry-run, and measure the wall-clock of the lane so the window-day schedule in the WO2 runbook amendment is grounded in an observed duration, not an estimate.
- [L1] ED-QUAL-L1-1 (stable capability, before the sitting): same-boot production replay of the freeze chain — run scripts/generate_arm_readiness.py verify against each pack's freeze receipt and scripts/project_identity_pins.py verify with the real model bytes on the production Mac (boot session da90818c-9c31-45d0-8813-deae65fba143). The sandbox cannot discharge this: model bytes are absent, so U11 refuses readiness_identity_artifact_unreadable (observed, fail-closed).
- [L1] ED-QUAL-L1-2 (stable capability, after the B1 disposition is ruled): re-author the pack-side freeze evidence (scripts/author_arm_readiness_evidence.py), reissue freeze receipts, update plan-tree pins, and recommit on the production machine — must run there because evidence receipts derive kern.bootsessionuuid and monotonic time from the arming host; any reboot decision is Ed's.
- [L5] ED-QUAL-L5-1 (stable capability, any tap block): one non-window rehearsal of the t0 clock-attestation input handshake — Ed captures real `sudo systemsetup -getusingnetworktime` / `-setusingnetworktime off` outputs per runbook E-4/E-5 into a scratch arm_readiness.t0.inputs namespace and the lead validates them against the t0 author's capture validators (joulewise/arm_readiness_evidence_t0.py:838-861 _systemsetup_argv / _derive_clock_attestation). The authored tests use synthetic captures only; the first real sudo-output shape mismatch must not surface at T-0.
- [L2] EDQ-L2-1 (stable capability): execute tests.test_calibration_writer_crash_matrix to completion on the quiet bench at the audit-baseline head and record pass + wall time. On the audited host it cannot complete (finding L2-1); CI exclusive-job green at the baseline head corroborates but a bench execution closes the row with local evidence.
- [L2] EDQ-L2-2 (stable capability; runbook-mandated non-delegable): the SS5C lead live verification on the exact reviewed measurement checkout — frozen plan's literal readiness-validator command plus the complete under-lease synthetic rehearsal (real reservation CLI --execute + production writer lifecycle through BOTH slots against a synthetic root), requiring the D-134 dry-run receipt PASS/NOT_APPLICABLE with the reviewed HEAD + committed-pack digest. This audit replayed the equivalent in scratch; the runbook requires it on the production checkout with the frozen plan, which no sandboxed seat can perform.
- [L3] ED-L3-1 (stable): Live sudo/powermetrics checklist — run scripts/ed_session/sampler-checklist.sh (sudo -n grant, empty pre-census, supervised 5-sample capture under _sampler_lifetime, empty post-teardown census, cadence record, parse by the pinned parser). This is the long-owed row gating reliance on #127's production sampler commit (RUN_STATE 'ED-OWED' item 3). Close only after WO-L3-2/WO-L3-3 fix the checklist's documented home and add the 100 ms leg.
- [L3] ED-L3-2 (stable): Live SIGTERM-relay termination — confirm on the current OS build that `sudo -n powermetrics` exits within the 10 s grace on SIGTERM to sudo (normal path) ; the executed falsifier F-B shows that if it ever does not, the SIGKILL escalation strands a root orphan no software census on the measured-run path detects. One observation, any tap block.
- [L3] ED-L3-3 (stable): JW-MET-3 rail probe — scripts/ed_session/rail-probe.sh ABBA keyboard-backlight arms with --samplers battery,cpu_power,gpu_power,ane_power,thermal; documentation-grade rail-inclusion differential (the LED-outside-boundary verdict already stands on code evidence).
- [L3] ED-L3-4 (stable, largely co-closed by ED-L3-1): Channel-census currency on the arm build — one live capture parsed by the pinned parser with hw_model/kern_osversion recorded and matched against the runbook's Mac15,9 / macOS 25F84 bindings; REOPENS on any OS update before the window (the parser is pinned to the Slice-2H fixture format; a format/unit change fails closed on rails but silently on units only if Apple kept mW fields parseable — currency is an empirical row, not a test-provable one).
- [L7] ED-L7-1: prewindow_check.sh --wait to READY plus quiet_mac_prep.sh on the freed quiet machine (stable capability; my execution proves the gate correctly BLOCKS while any agent fleet runs, so READY can only be demonstrated in an Ed/quiet block)
- [L7] ED-L7-2: fresh §5C lead dry-run PASS at the final reviewed head on the measurement checkout — executes the real reservation CLI --execute and the production ledger-writer lifecycle through both slots under lease (the recorded dry-run-0001 is head-stale after any checkout advance; a new PASS receipt binding the final head/digest is required desk evidence before arm)
- [L7] ED-L7-3: live sudo powermetrics fiducial calibration seam (validate_powermetrics_fiducial --allow-live producing instrument_evidence.json consumed by the chain's §5B jq screen) — unexercisable without sudo + quiet machine; covered by the charter's sampler checklist but named here because it is the one producer->consumer edge in the §6 chain I could not execute or observe in any test
- [L10] ED-L10-1 (stable capability, any tap block, no live measurement): one desk replay of the complete post-collection chain against a RETAINED real window corpus (a9/a10 custody, Ed-held off-repo) — whole-window verdict (expect passed), duration-margins recorder, backup, governed extraction with the matching spec and basis sha — pasting every command and exit code. This supplies the CLI-level PASSED-basis positive proof that no sandboxed desk rehearsal can produce, because a passing basis requires real calibration-bracket, NEG-8 corpus, and reference-triplet evidence that only a live sudo/powermetrics window can mint.
- [L4] ED-QUAL-L4-1 (network capability, not hardware/sudo — emitted so it is not silently skipped): execute scripts/replay_d117_decisive.sh at the audited head in any tap block with network — anonymous release download, digest gate, governed hydration, census byte-compare, then the single decisive no-skip mint test (~3h35m on the M3 Max). Stable evidence; closes the two skipped decisive tests and the full-fixture leg of the mint's exact-equality proof.
- [L9] ED-Q-L9-1 (staged): JW-MET-2 System Settings keyboard-backlight census — level 0, auto-adjust off, inactivity Never, verification=operator_visual (ed-qualification-session.md step 4; no CLI exists for the level, operator visual is the only probe)
- [L9] ED-Q-L9-2 (staged): JW-MET-3 keyboard-backlight rail-inclusion differential probe — sudo powermetrics ABBA max/off arms (ed-qualification-session.md step 3; documentation-grade, boundary verdict already stands on code evidence)
- [L9] ED-Q-L9-3 (new, stable capability, no sudo): quiet-state resident-process baseline — with all fleets/agents closed on the real machine, capture the four PROCESS_CENSUS and one MAINTENANCE_CENSUS pgrep outputs and commit them as the regression fixture that the WO-L9-1/2 pattern fixes must pass against; this is the only way to prove the fixed censuses PASS in the state they will actually run in
- [L8] ED-Q-L8-1 (sudo): decide and prove the privileged read path for the T-0 CLOCK_PROBE — either a scoped read-only sudoers entry for `/usr/sbin/systemsetup -getusingnetworktime` or a ratified `sudo -v` warm-up literal immediately before the T-0 author — and exercise it once in a tap block; D-004's powermetrics-only NOPASSWD plus a >10-min-cold sudo timestamp otherwise guarantees an authoring refusal at night
- [L8] ED-Q-L8-2 (sudo + Ed): full arm-sequence dress rehearsal on the recut packet — E-4→E-9 under the capture wrapper, T-0 authoring, arm→verify→consume against scratch custody/synthetic roots, with a real ≥10-minute prewindow wait — timed against the 20-minute volatile horizon and 5-minute arm-receipt fuse
- [L8] ED-Q-L8-3 (sudo, already chartered as steps 2-3): live sampler-checklist and keyboard-backlight rail-probe executions on a quiet machine (dry-run staging verified in this audit; the live arms and teardown censuses still need sudo)
- [L8] ED-Q-L8-4 (sudo): live quiet_mac_prep.sh run to confirm its three OK literals (passwordless powermetrics, displays asleep, screensaver disengaged) match what the T-0 author's _quiet_capture requires verbatim

## 6. Unexecuted obligations (coverage adjudication input)
- [L6] Did not execute generate_arm_readiness.py freeze/dry-run/arm/consume as CLIs end-to-end (freeze mutates pack bytes; arm requires the B1 inputs that do not exist; tree had to stay byte-identical) — authentication internals were exercised by direct calls instead
- [L6] Did not run the collection-plane producers live (run_campaign, validate_powermetrics_fiducial, reserve_calibration_window_bracket) — no live measurement permitted; their seams verified by contract+code reading only, deep audit owned by seats L2/L3/L4
- [L6] Did not execute extraction→mint on a synthetic window (seat L10's sacrificial lifecycle owns this); mint consumption verified by import/code reading only
- [L6] Did not deep-trace the claims-index/claims-lint consumption seam beyond identifying producer and consumer files (post-paper plane, thinner risk)
- [L6] Did not resolve whether the t0.ledger_reservation predicate's expected_plan_sha256 (pack plan_tree sha) and the reservation's FROZEN_PLAN sha are the same identity — flagged to seat L2 (calibration acquisition) rather than guessed
- [L6] Could not read the FROZEN_PLAN/window.env instance (off-repo by design; none exists yet for the next window)
- [L1] joulewise/arm_readiness_evidence.py (freeze-side evidence author, 1,781 lines) not read line-by-line — its outputs were authenticated via the replay/authentication code and executed suites, not its authoring logic
- [L1] scripts/reserve_calibration_window_bracket.py not read — the ledger-reservation authority chain verified only at its consumption predicate (t0.ledger_reservation.v1 binding plan_sha256)
- [L1] joulewise/identity_pins.py internals not line-read — verified via executed CLI probe and the 42-test suite
- [L1] Full freeze-receipt semantic replay (_load_freeze_reference end-to-end) and dry-run receipt generation not executable in this sandbox (model bytes absent; evidence boot/monotonic-bound to the production machine) — deferred to ED-QUAL-L1-1
- [L1] No automated staleness detector for kernel.updated was built; the truth check was manual
- [L5] CI log verification for the floor-pack plan-test shard (no network in the audit sandbox): whether #149's CI genuinely ran and passed tests.test_d117_floor_qwen25_{1p5b,7b}_plan — finding 1 makes this the highest-value follow-up; a refuter with network should pull the actions log.
- [L5] Live execution of the arm-night receipt chain (generate_dry_run_receipt at the final head, author_arm_readiness_evidence_t0, generate_arm_receipt/verify/consume, U11 verify_frozen_projection with real model bytes): these require the measurement checkout at the final head, quiet machine, sudo captures, and custody writes — covered here only by the 58-test author/dry-run/lifecycle/integration suites and by code reading; they are the runbook's own T-0/lead work.
- [L5] Deep line-level read of joulewise/identity_pins.py internals (1,900+ lines): audited via its 25 passing tests, the frozen projection receipts' byte/pin verification, and the plan-tree inventory falsifier (F2 catch layer), not a full read.
- [L5] The arm-packet document under ~/JouleWise-window-custody/t4-session-20260810/ was located but not content-audited (seat 6-7 seam territory).
- [L2] Full tests.test_calibration_writer_crash_matrix module on THIS host (16 tests; 6 executed locally, all governed-exit/lease/capability classes PASS): completion is blocked by finding L2-1's degenerate-cost case exceeding the harness's 600 s subprocess ceiling. Corroboration: CI runs it as a dedicated exclusive job (ci.yml:115) and PR #149 — the baseline head — merged green.
- [L2] Two documented suite skips requiring lead-reviewed D-079 import fixtures at /private/tmp (absent here): test_production_path_authenticates_real_76_receipt_import_prefix, test_d079_issued_artifact_mode_is_deterministic_and_write_explicit.
- [L2] calibration_ledger.py historical-import/bootstrap block (~lines 2205-2727) and snapshot/parse internals read behaviorally (their tests green), not line-by-line.
- [L2] joulewise/calibration_bracketing.py evaluation half (evaluate_calibration_bracket, calibration_bracket_for_bundles) — L4 quantitative-pipeline seat's scope; only the acceptance-authentication half audited here.
- [L2] Real-time-scale live writer run and sudo powermetrics behavior — hardware; ED rows / seat L3.
- [L3] tests/test_calibration_writer_crash_matrix.py NOT run at this seat (hosted-pathological per WO-CRASHMATRIX-RELIABILITY; a sibling seat was executing it live during my audit — concurrent duplicate execution would have contended; its writer-crash coverage is L2's scope).
- [L3] No live sudo powermetrics execution of any kind (environment: no sudo, no live measurement) — everything privileged is emitted as ED-QUALIFICATION rows, none silently skipped.
- [L3] joulewise/adapters/mock_telemetry.py not audited (not on the funded-window path; pack member verified pinning telemetry_backend=powermetrics).
- [L3] scripts/ed_session/rail-probe.sh read for role, not line-audited (JW-MET-3 is documentation-grade).
- [L3] quiet_guard.py / quiet_guard_process.py header-ruled out of this seat's scope (agent-session custody guard — seats 1/9 territory).
- [L3] Rich-telemetry consumers (salvage_dangler.py, floors common-mode) and reducer integration internals corroborated only at the seam (reduce.py D-018 policy: only manifest rails summed, non-manifest rows ignored) — deep audit is L4's scope.
- [L3] Long-stream soak of the admission stream cursor (_advance_stream_cursor over hours-scale files) not executed; covered by unit tests incl. the 64KiB-chunk large-stream test only.
- [L7] Live capture path: validate_powermetrics_fiducial --allow-live, MLX member collection, --arm-quiet-mode display arming (no sudo / no live measurement in this sandbox) — ED rows
- [L7] tests.test_calibration_exits (2,036 s) and tests.test_calibration_writer_crash_matrix (5,317 s) — CI-exclusive modules not re-run in this seat's budget; last known green on the #149 merge CI
- [L7] The decisive full-fixture mint proof (replay_d117_decisive.sh / test_coordinated_report_and_pin_change_refuses_against_floor_evidence) — requires a GitHub release download; no network. Skip marker observed and documented in batch B
- [L7] Whole-window verdict and extract_detection_floors CLIs against a real collected corpus (runs/ corpora are off-repo); exercised only through their test fixtures
- [L7] reserve_calibration_window_bracket.py --execute against the production ledger (exercised only inside the dry-run generator and tests)
- [L7] quiet_mac_prep.sh (mutates display state)
- [L7] a9/a10 retained characterization basis — seat 11's scope, excluded from my universe count
- [L10] §9 D-100 salvage-dangler verdict dispatch (--consumption-semantics-id salvage_dangler_exclusion_v1 with membership binding + salvage closure) — not exercised at the CLI (no synthetic salvage closure); covered only by suite evidence
- [L10] §10 --record-supersession quarantine/supersession flow — not exercised at the CLI
- [L10] v2 multi-cell aggregate mint route (--v2-input-manifest + schema_v2 pinset), the route the gamma consumption depends on — not exercised at the CLI; covered by tests/test_mint_floor_artifact_generalized.py (passed)
- [L10] Waiver path: --waivers producing a 'flagged' verdict and extraction refusing the flagged basis — not exercised
- [L10] CLI-level PASSED-basis end-to-end (verdict passed → margins PASS → extraction admitted → mint minted) — impossible from the desk without a real window corpus; see ED-QUALIFICATION row
- [L4] Full canonical suite (python3 -m unittest discover -s tests) on BOTH interpreters at the baseline head — I executed 13 focused in-scope modules on python3.13 and 2 on python3.11; repo CI green at ac3fe1d corroborates the rest but is not my execution.
- [L4] The decisive full-fixture production proof (scripts/replay_d117_decisive.sh; test_coordinated_report_and_pin_change_refuses_against_floor_evidence and the split-partition test, the 2 skips in my mint suite run) — requires network download of the custody-store release asset and ~3h35m; not executable in this no-network sandbox.
- [L4] Deep line-audit of joulewise/reduce.py (3983 lines) and joulewise/whole_window.py (5348 lines) beyond interface depth — covered by their full test modules (123/15/56 OK), by the margin recorder's live reuse of reducer internals, and by the verdict-writer/basis-reader seam check I did execute; the numeric interior was not line-read.
- [L4] End-to-end synthetic collected-window rehearsal through reduce -> verdict -> mint -> claim consumption — seat 10's charter (SACRIFICIAL FULL LIFECYCLE); not duplicated here. Note seat 10 must expect my finding 1 to fire if its rehearsal includes the section-11 margin step on a registration-bearing spec.
- [L4] MET-VERDICT-ADJ-01 adjudication status of the whole-window verdict machinery — historical gate, not re-adjudicated by this seat.
- [L9] quiet_mac_prep.sh full execution (quits user apps and sleeps the display — not sandbox-safe from an agent session; step-7 probes replicated read-only instead)
- [L9] --arm-quiet-mode live re-probe path inside run_campaign (requires display sleep + live campaign; code path read, not run)
- [L9] sudo-gated probes: systemsetup -getusingnetworktime read, sudo -n powermetrics (no sudo in sandbox; covered by capture lens + ED rows)
- [L9] quiet_guard engine internals (Commit-1 is contractually inactive and non-armable; contract read, engine not audited)
- [L9] whole_window.py adapter-wattage-continuity and controller.py enforcement wiring examined at grep/inventory level only
- [L9] full audit of tests/test_arm_readiness_evidence_t0.py fixtures beyond confirming the probe executor is faked with empty-pgrep results
- [L8] scripts/quiet_mac_prep.sh live execution (transient display sleep + sudo -n powermetrics probe) — static review only; live run needs sudo and violates the quiet-machine/agent boundary
- [L8] Live sudo paths of rail-probe.sh and sampler-checklist.sh (the actual ABBA captures and supervised 5-sample check) — no sudo in this sandbox; ED-QUALIFICATION rows
- [L8] E-9 reservation behavior against a ledger copy (double-reserve, live-writer refusals) — code-read and shipped-test evidence only; primary ownership is the L2 seat
- [L8] Runbook §10 refusal-row completeness for the 2am operator (packet O-9's missing one-page extract) — read but not row-by-row audited; flagged to L2/L6/L7
- [L8] Morning §9/§11 magistrate procedures beyond ordering review — L10 sacrificial-lifecycle scope
- [L8] The real dry-run receipt and skeleton in ~/JouleWise-window-custody were read but deliberately not touched or re-verified in place
- [L11] Full power-trace re-integration for the remaining 29 a10 phase members (1/30 done exactly; the other 29 envelopes were accepted from sha-bound summaries whose digests I verified against the custody extraction).
- [L11] Code audit of the reducer-side envelope method implementation (common_trace_shift_plus_independent_edge_corners_v3) in joulewise/reduce.py — I re-derived its output numerically for one member but did not read the implementation.
- [L11] Deep audit of joulewise/whole_window.py verdict machinery (surveyed for schema/semantics only; the verdict artifact itself is absent — finding SF3).
- [L11] a9 custody operator logs (window-chain/calibration logs) read in detail; a10's were read.
- [L11] campaign_log.jsonl deep audit and raw plist parsing for the reference members.
- [L11] Byte-parity verification of the iCloud archive mirrors against local dirs (layout and existence checked only; a9 parity rests on the PRUNED.md-documented verification).

## 7. Magistrate dispositions submitted for cold review
# MAGISTRATE DISPOSITIONS FOR THE READINESS SITTING — 2026-08-14 (T7 successor session)

Both items below were raised by the C-058 drafting mechanic (⚑ OPEN flags,
c058-draft.md). They are MANDATORY CONTENTS of the sealed sitting packet:
the cold pairing adjudicates both. Written before fleet harvest; the fleet
(run wf_29eee330-1db) was NOT stopped over either — rationale below is the
thing under review.

## Disposition 1 — Baseline drift (manifest head ac3fe1d vs fleet worktrees at 8937dec)

Claim under review: charter amendment 2/12 says any drift from the
baseline manifest invalidates affected lens results; the eleven fleet
worktrees are checked out at 8937dec, three commits past the manifest's
head_commit ac3fe1d.

Magistrate disposition: ZERO lens results are affected, by direct
mechanical application of the rule — not by reinterpretation.

Mechanical facts (verify with `git diff --stat ac3fe1d..8937dec` and
`git show --stat` per commit):
1. Commits after head_commit: 694442c (adds
   docs/process/audit-baseline-manifest.json — the manifest itself),
   d279a7c (README.md + RUN_STATE.md), 8937dec (RUN_STATE.md).
2. Total changed files vs the pinned head: README.md, RUN_STATE.md,
   audit-baseline-manifest.json. No code, no chain artifact, no pack
   byte, no runbook, no contract, no decision-log text.
3. The invalidation rule's own scope is "voids AFFECTED lens results."
   README.md and RUN_STATE.md are session-state surfaces in no lens's
   evidence universe (L1 control plane, L2-L5 chain code/artifacts,
   L6/L7 producer-consumer artifact classes, L8 runbook+packet+scripts,
   L9 hazard register, L10 pipeline, L11 a9/a10 corpus). The manifest is
   cited by every lens but is the REFERENCE, not an audited artifact.
4. Manifest-after-its-own-head is charter-BY-CONSTRUCTION (amendment 2:
   the manifest is "committed before any lens launches, binding HEAD" —
   a worktree at head_commit exactly would not contain the manifest the
   lens must cite). The charter therefore anticipates lens trees at
   manifest-commit-or-later; the drift rule governs changes AFTER the
   manifest, of which there are exactly two, both confined to the two
   session-state files above.
5. RUN_STATE's own T7 instruction ("verify main = baseline head + this
   checkpoint commit; re-pin if doc-only commits landed after") is
   satisfied: nothing landed after 8937dec (verified `git status -sb`:
   main == origin/main == 8937dec at fleet launch).

Standing consequence accepted by this disposition: the COMMIT FREEZE —
no commit of any kind lands on main between fleet launch and harvest, so
the set {README.md, RUN_STATE.md, manifest} remains the complete and
final post-baseline delta for the fleet's whole run. Any commit before
harvest voids this disposition and the affected seats re-run.

If the cold pairing REJECTS this disposition, the remedy is: re-pin the
manifest at the current head and re-run every seat whose universe the
pairing judges touched (worst case: full fleet re-run; windows are not
scarce, per the charter preamble).

## Disposition 2 — M-2 retroactive cold review (rule-11 trigger missed)

Fact pattern (decision log, "M-2 RULED (magistrate)", 2026-08-14): M-2
ruled the frozen packs' draft_status/"not armable" text generator-owned
and OVERRODE the §5C gate's placeholder-text NO-GO reading for exactly
that field, transitional until the chain-fix batch landed freeze-aware
generator text (it landed in #149).

The mechanic's finding, CONFIRMED by the magistrate: rule 11 lists "any
reversal or reinterpretation of a stop signal or verdict" as a MANDATORY
cold-pairing trigger. M-2 overrode a NO-GO reading. No cold-gate
artifact exists for it. The trigger was missed — this is acknowledged as
a process defect, not argued around.

Disposition: M-2 is submitted for RETROACTIVE adjudication by this
sitting's cold pairing (which has exactly the rule-11 required shape:
fresh Fable adjudicator + Opus contract refuter). Scope for the pairing:
(a) was the override sound on the merits; (b) is the landed remedy
(freeze-aware generator status text, #149) sound — note lens L5 is
independently auditing the frozen packs' current text; (c) does any
consumption that relied on the transitional override need re-review.
Exposure is bounded: the override was scoped to one field, transitional,
and is now moot in operation — but a rejected M-2 would void the packs'
regenerated status text and route back through the generator gate.

Process follow-up regardless of outcome: the C-058 entry records the
zero-cold-gates-in-span anomaly; the miss pattern (magistrate ruling
under time pressure at packet-finalization) goes to the council entry's
process-findings section.

## Packet routing

Both dispositions + the c058-draft ⚑ items + the mechanic's record
anomalies (span correction, manifest-gap widening 3→6 concentrated in
review-class runs, #149 body staleness, CLOSED-not-merged PR counts)
are packet inputs. Nothing here lands on main before harvest.


## 8. Consistency-sweep findings (scout, partially triaged: digest blocker REFUTED by lead)
custodied: consistency-sweep-findings.md sha16 e04a282cb4632228

## 9. Refuter verdicts (ALL NINE HARVESTED — supersedes the pending slots in section 3)

# Refuter verdicts (folding into sitting packet §3)

## A-contract (Sol xhigh, envelope DISCUSSION, tree clean) — HARVESTED
- L1-B1 expiry: CONFIRMED. Remedy corrected: in-place re-author NOT contract-valid (D-131 requires
  successor pack+custody root). Open ruling: durable-freeze-evidence vs successor-pack tool.
  24h horizon is implementation policy, not D-134/D-137 contract text.
- L6-B2 refresh lane: CONFIRMED w/ qualification (partial prose exists; freeze CLI cannot reissue —
  freeze-0001 hardcoded, mutated:false short-circuit; no successor-pack command anywhere).
- L8-B4 freeze-receipt mismatch: REFUTED. Mismatch was wrong-path artifact (receipt binds canonical
  measurement-checkout absolute path; identity_matches=True all three packs at canonical path;
  committed digest not a comparison input; M-2 already governs placeholder text).
  CAVEAT: canonical-path arm probe degraded to readiness_io_error at boot lookup (read-only sandbox);
  execution lens to replay. Severity: dies as independent blocker; wrong-checkout refusal = correct fail-closed.
- Lead corroboration performed by relay agent: 33/33 receipts expired (range matches), _pack_identity
  (arm_readiness.py:1963-1984) has no digest field. Both held.

## L2-falseclean (Sol xhigh, envelope valid; worktree deleted mid-run by harness cleanup — ruled
## environment audit-trail gap, probes continued read-only on main at same HEAD, verified clean) — HARVESTED
READY DOES NOT SURVIVE. L2 -> NOT-READY.
- NEW BLOCKER L2-1 (raised from L2's own should-fix): detect_pulses region projection has NO finite
  work budget; frozen chain calls it synchronously UNDER THE WRITER LEASE (validate_powermetrics_fiducial.py:846
  acquire, :1509 call, :1037 release; runbook:1017 no watchdog; powermetrics_fiducial.py:555 unbounded loop).
  Remedy: bounded evaluation/wall budget -> registered invalid-evidence + governed abort.
- NEW BLOCKER L2-COV-1: coverage 15/16 REFUTED — self-selected universe; omitted contracts, bootstrap/
  backfill scripts, 23-test three-window lifecycle module; crash matrix is 13 tests not 16; real direct
  test universe 251.
- NEW BLOCKER L2-EDQ-1: charter forbids deferred ED-QUAL at READY; live writer/sudo + crash-matrix
  qualification open.
- L2-2 missing-parent raw traceback CONFIRMED should-fix (typed refusal remedy).
- L2-3 needs_pin_commit contradiction CONFIRMED, RAISED nit->should-fix (can mechanically abort every
  correct pre-slot session).
- L2-4 idempotent-marker WO REFUTED as phantom (runbook forbids re-reserving; reprint would mislead) — drop WO-L2-4.
- Falsifiers run by refuter: ledger tamper failed closed; non-finite power sample edge survived.
- Lead-side replay by relay: crash-matrix count 13 confirmed, three-window 23 confirmed, missing-parent
  traceback reproduced.
- Residual: stateful tests sandbox-blocked; PR #149 CI not re-queried (no network).

## DG-contract (Sol xhigh, envelope findings/complete; worktree vanished mid-run, continued read-only
## on main same HEAD — env gap noted) — HARVESTED FROM DISK (refuter-DG-out.md)
- L1-B2 kernel fail-open: PARTIAL->survives as blocker (zero global gates + P2-006 READY confirmed;
  refuted portion: D-117 does not formally retire P2-006 — needs a ruling, not deletion).
- L8-B7 launch ceremony: CONFIRMED blocker (consume_launch_capability exists but never execs; chain
  has no receipt check; zero downstream consumers authenticate launch lineage). Remedy: reviewed
  launcher consume->exec + downstream provenance refusal; Ed still performs physical launch.
- L1-B3 bifurcated authority: reduced to should_fix (all three "missing" WOs are ancestors of HEAD —
  stale registration prose, not live blockers; BUT kernel carries real falsehoods: U11 row queued/
  unprojected vs PASS receipts, FCM "continues unmerged" vs merged 60d9e42). Remedy: one kernel
  reconciliation transaction; do NOT re-register shipped WOs.

## DG-execution (Sol xhigh, envelope findings/complete) — HARVESTED FROM DISK (sol-out-refuter-DG.md)
- L1-B2: CONFIRMED blocker (gen_state --check green on the contradiction; gate machinery tests pass —
  data gap not machinery gap).
- L1-B3: PARTIAL — authority-drift core called blocker by this lens (split w/ contract lens's
  should_fix; LEAD SYNTHESIS PENDING at sitting: three-WO scenario stale per both lenses).
- L8-B7: CONFIRMED blocker. Minimal WOs per both lenses: (1) kernel reconciliation, (2) atomic
  arm-consume-to-launch binding.

## RELAY FAILURE RECORD (process finding for C-058): 5 of 9 refuter relay agents wedged ~7h reading
## bridge-contract docs without launching their Sol runs; killed 2026-08-15 ~07:15, relaunched from
## lead shell per the T5 lesson (>45-min/fragile runs launch from lead shell; .status != liveness).

## B-contract (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
All six CONFIRMED; none refuted. Corrections/additions:
- F1+F2 MERGE into ONE work order: shipped T-0 acquisition/capture tool (executes/captures E-4..E-9,
  derives boot/monotonic, builds context+launch from frozen bytes; operator provides only the
  irreducible clock observation). Nine filenames are implementation preconditions, not D-134 names.
- F3 prewindow gap arithmetic verified: clean exit ~60s vs author 600s (gap 540s). Remedy: min-dwell
  in --wait; do NOT lower author threshold.
- F4 sudo systemsetup: remedy ALREADY RULED as D-127 (exact-path/argv sudoers for the two network-time
  commands) — chartered, never implemented/installed. Land + Ed installs (ED-QUAL row).
- F5 packet: issue reviewed SUCCESSOR packet; preserve old as custody (D-134 cl.9 already required
  the packet amendment).
- F6 all four env/chain mismatches reproduce + NEW PRODUCTION-ONLY DEFECT: author line 1149 joins
  plan_tree.json's repo-relative plan path onto pack_root -> doubled nonexistent path
  (pack_root/configs/campaigns/.../calibration_plan.json); test fixture uses bare filename so suite
  misses it. FROZEN_PLAN meaning needs a ruling before changing prose or parser.
- Minimal WO set (per refuter): (1) T-0 producer tool + operator step; (2) prewindow dwell + D-127
  install; (3) env/chain/manifest/plan-path contract + real-pack test; (4) successor packet after
  end-to-end pass.

## A-execution (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
- F1 (expiry) CONFIRMED executed: 33/33 generic receipts refuse readiness_record_expired via
  _authenticate_generic_evidence_item at live monotonic; remedy "partial" (concurs with contract lens:
  lifecycle design ruling needed).
- F2 (no refresh lane) CONFIRMED: producer exists, operative refresh lifecycle for a frozen pack does not.
- F3 REFUTED with two-lens concurrence: canonical-path probe executed, identity_equal True at
  /Users/edr/JouleWise-measurement-20260813 pack; mismatch reproduces only from audit scratch path.
  F3 CLOSED as artifact (correct fail-closed wrong-checkout refusal).
CLUSTER A ADJUDICATED: one launch-blocking expiry/lifecycle defect (design ruling: durable freeze
evidence vs successor-pack tool), one artifact dismissed.

## ECF-contract (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
All four CONFIRMED (L10-B1 consumption edge, L4-B1 margin recorder, L9-B1 maintenance census,
L9-B2 browser/monitor regexes). Qualifications: L1 custody discipline does not categorically bar
post-collection implementation (but heightened proof burden -> blocker stands); CI-coverage
narratives on F3/F4 qualified (sandbox denied pgrep replay/tmp — exit 3; unittest not run; static
+ earlier live L9 observations stand). Remedies ruled sound: governed prospective validator +
finalizer + queue row; recorder governed-vocabulary authorization for exactly the plan-tree-pinned
spec path; activity-based census re-shape per WO-L9-1/2.

## ECF-execution (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
All four CONFIRMED with executed probes: V2 load_manifest refuses v3.prospective schema verbatim;
V3 margin recorder REFUSE authoritative_input_invalid (forbidden key 'estimator_registration' at
pack-pinned spec.cells[1]); F3/F4 census over-match confirmed on launchd running-state + regex
analysis (live pgrep denied in sandbox — earlier live L9 observation stands). Consolidation: F3+F4
= ONE census-semantics work order. F1 wording correction noted.
CLUSTER ECF ADJUDICATED: 4/4 confirmed by both lenses (2 WOs: consumption edge; recorder
authorization; +1 census-semantics WO).

## B-execution (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
F1/F2/F3/F5/F6 CONFIRMED (F1+F2 one defect; F3 executed replay: READY in 60.09s vs 600s required;
F6 all four mismatches + doubled plan-path independently confirmed). F4 PARTIAL: privilege gap
survives; its timing premise dies (current E-7b ~1 min so sudo cache not necessarily cold — becomes
true once F3's 10-min dwell lands; land D-127 route regardless).
NEW DISCOVERY: baseline ac3fe1d lacks the three JouleWise-Terminal-Review* commit trailers the T-0
author demands (arm_readiness_evidence_t0.py:918-930) — terminal-review evidence needs an
operational producer too; folds into the integrated T-0 repair WO.
Minimal program per refuter: (1) ONE integrated T-0 acquisition/contract repair (nine-input producer,
10-min continuous wait, privileged clock route, env/manifest/plan/chain alignment, terminal-review
evidence, real-pack author->ARM->verify->consume rehearsal); (2) dependent re-freeze + packet reissue
at the exact reviewed head.

# ADJUDICATION TALLY (all 9 refuter runs harvested 2026-08-15)
- 19 blocker-level claims examined (16 fleet + 3 raised by L2 attack).
- DEAD: L8-B4 freeze-receipt mismatch (both lenses, artifact); WO-L2-4 (phantom); F4-timing premise.
- DOWNGRADE PENDING LEAD SYNTHESIS: L1-B3 authority bifurcation (contract: should_fix; execution:
  blocker-for-drift-core; three-WO scenario stale per both).
- ALL OTHER BLOCKERS CONFIRMED, several with executed refusals and remedy corrections.
- NEW DEFECTS FOUND BY REFUTERS: doubled plan-path (production-only, suite-masked); terminal-review
  trailer producer gap; L2 unbounded lease-held detector (raised); L2 coverage denominator false.


### Original manifest note
A-armfreeze-expiry x2 (contract/execution), B-t0-producer-gap x2, DG-kernel-ceremony x2, ECF-consumption-margin-census x2, L2-falseclean x1. Verdicts fold into section 3 slots on harvest.

---
PACKET SEALED 2026-08-15. sha256(self-exclusive-of-this-line) e68c7fb9fe88ed0b8cfbca5ca3bc68f2c767d9d5846f9df734dc9103ae6fc5e0
