# RAW TRIAGE EXTRACT — L1-AUTHORITY-PLANE

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L1-AUTHORITY-PLANE`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 20/24 (evidence_universe_count=24)
- findings: 8; falsifiers: 7

## FINDINGS (verbatim)

### F1 [blocker] Frozen packs cannot arm: all 33 freeze evidence receipts have lapsed their monotonic validity on the un-rebooted arming machine
- file_line: `configs/campaigns/*/arm_readiness.evidence/*.json; joulewise/arm_readiness.py:3710-3717,3948-3955`
- failure_scenario (verbatim): Ed attempts tonight's slipped Window ALPHA arm: generate_arm_receipt authenticates the pack freeze evidence (boot session matches — no reboot occurred), but the arm receipt's valid_until is min-inherited from evidence expirations that are already in the past (earliest 1986799611717708 ns vs live ~1997.9e12 ns), so verify_arm_receipt refuses readiness_record_expired and consume_launch_capability can never fire. The direction is correctly fail-closed, but the funded window is unlaunchable under the audited bytes; the recorded standing constraint ('NO REBOOT before T-0 or the evidence re-authors') is insufficient — no reboot happened and the capability still died of monotonic age from the window slip. Remedy (re-author evidence, reissue freeze receipt, re-pin plan tree, recommit) changes pack bytes, rotates the committed pack digests, and voids the audit-baseline manifest's pack digests under charter amendment 12 — the council must schedule this re-freeze before or at GO.

### F2 [blocker] Authoritative work-selection state fails open for quiet-window selection: no council gate, and a superseded campaign renders READY [QUIET-MAC]
- file_line: `docs/process/state_kernel.json (active_global_gates: []); RUN_STATE.md:3433`
- failure_scenario (verbatim): A successor session or tired operator obeys RUN_STATE's generated region, which today renders 'READY — Q2 P2-006: Window A two-model campaign' with zero active global gates — despite Ed's 2026-08-13 window-gating directive (windows sit behind the council verdict) and despite D-117 having superseded the Window-A program. A quiet night gets spent on a campaign whose outputs do not trace to the current claim path, bypassing the council gate entirely, because the gate exists only in decision-log prose while the kernel's purpose-built gate machinery (proven working by probe) carries no gate row. The actual funded program (three frozen D-117 packs) has no kernel row at all.

### F3 [blocker] Work-selection authority is bifurcated: launch-blocking work orders live as hand-written prose outside the generated region while kernel rows assert falsehoods
- file_line: `TASK_QUEUE.md:201,635,659 (outside markers 452-613); docs/process/state_kernel.json /tasks/D117-U11-IDPIN-PROJECTION`
- failure_scenario (verbatim): WO-MINT-ESTIMATOR-VOCAB, WO-COLLECTION-MARGIN-01, and WO-ARM-EVIDENCE-AUTHOR-01 ('LAUNCH-BLOCKING for any window night') were 'registered in TASK_QUEUE' as hand-written sections outside the marker-fenced generated region — invisible to gen_state --check and absent from the kernel, violating DOC-008's single-authority contract. Simultaneously the kernel's D117-U11-IDPIN-PROJECTION row still reads 'queued... Checked-in packs remain unprojected' at a head whose packs carry PASS projection and freeze receipts, and FLOOR-COMMONMODE-01 renders 'READY [AGENT]' despite its D-133 desk-thread disposition. A session trusting the declared AUTHORITATIVE_WORK_SELECTION_STATE misses launch-blocking obligations or resumes disposed work; a session trusting the prose contradicts the kernel.

### F4 [should_fix] D-118's 'mechanical enforcement' of the merge gate ledger does not exist anywhere in the repo
- file_line: `docs/decision_log.md:7753-7759; .github/workflows/ (no checker)`
- failure_scenario (verbatim): D-118 states 'every PR description must carry a GATE LEDGER... any item marked NOT-RUN blocks the merge' and frames this as mechanical, but grep finds no gate-ledger checker in CI or scripts — enforcement is agent discipline, the exact prose-only failure mode D-118's own trigger recorded. A PR merges on green CI with an incomplete ledger and nothing mechanical objects. (Contrast: D-121's terminal review IS machine-bound for windows via exact commit trailers — arm_readiness_evidence_t0.py:913-943.)

### F5 [should_fix] kernel.updated and latest_report are false, and no invariant forces them to move
- file_line: `docs/process/state_kernel.json (updated: 2026-08-08; latest_report label: T3 2026-08-09)`
- failure_scenario (verbatim): The kernel says updated 2026-08-08 while its own row notes cite 2026-08-11/12 events, and latest_report describes the T3 2026-08-09 session six sessions ago; the validator checks only date format, so the render carries a false freshness signal that consumers use to weigh trust in the generated views.

### F6 [should_fix] FREEZE-FCM01.md's standing prohibition was never amended after D-133 cl.4 executed the re-spec
- file_line: `FREEZE-FCM01.md:1-8 (banner: 'Do not fix, do not consume, do not register in any pack')`
- failure_scenario (verbatim): The root-level FROZEN banner still bars pack registration of the estimator and says only Ed may relicense, while the frozen packs lawfully register d124_two_shared_edge_common_mode.v1 under Ed's later cl.4 EXECUTE ratification. A successor session reading the banner as binding either stalls the lane or concludes the packs violate a standing freeze order; the repo's own convention (dated supersession notes on consult docs) was not applied here.

### F7 [nit] Frozen pack bytes still carry draft_status 'unfrozen_draft' — the M-2 scoped override remains the operative instrument indefinitely
- file_line: `configs/campaigns/d117_floor_qwen25_1p5b_v1/plan_tree.json:793`
- failure_scenario (verbatim): No code consumes draft_status (verified by grep), so this is cosmetic, but because the bytes are now frozen the M-2 'until the generator fix lands' override can never be retired for these packs without a reissue; the §5C human gate must permanently rely on the recorded override.

### F8 [nit] gen_state invariant 8's D-041 authority binding is a label-substring match
- file_line: `scripts/gen_state.py:372`
- failure_scenario (verbatim): The post-2M authority check passes if the string 'D-041' merely appears in the authority label; a mislabeled pointer to any document mentioning D-041 satisfies it. Low stakes — it is a lint over hand-written labels, not a gate.

## WORK ORDERS (verbatim)

- WO-L1-1 (blocker B1): ruled disposition for the expired pack freeze evidence — re-author evidence + reissue freeze receipts + re-pin plan trees + recommit on the production machine, or amend the evidence-validity design by decision (freeze-side evidence bound to boot session only, monotonic expiry reserved for arm-side); then re-pin the audit-baseline manifest per charter amendment 12 and re-discharge the §5C committed-pack verification

- WO-L1-2 (blocker B2): add WINDOW-COUNCIL-GATE to state_kernel.json active_global_gates (scope quiet_mac, allowed_task_ids [], authority = 2026-08-13 window-gating directive, clearance = council READY + T-0 GO); regenerate views; remove only on the council verdict

- WO-L1-3 (blocker B3): kernel truth pass — bump updated, correct latest_report, reconcile D117-U11-IDPIN-PROJECTION and FLOOR-COMMONMODE-01 to landed/disposed reality, enroll WO-ARM-EVIDENCE-AUTHOR-01 / WO-COLLECTION-MARGIN-01 / WO-MINT-ESTIMATOR-VOCAB as kernel rows with satisfied evidence where landed, and demote the hand-written TASK_QUEUE sections to pointers at their kernel rows

- WO-L1-4 (should-fix S1): build the D-118 PR gate-ledger mechanical lint in CI, or amend D-118 to state enforcement is procedural

- WO-L1-5 (should-fix S3): add a dated supersession banner to FREEZE-FCM01.md citing the D-133 cl.4 execution ratification

## ED-QUALIFICATION ROWS (verbatim)

- ED-QUAL-L1-1 (stable capability, before the sitting): same-boot production replay of the freeze chain — run scripts/generate_arm_readiness.py verify against each pack's freeze receipt and scripts/project_identity_pins.py verify with the real model bytes on the production Mac (boot session da90818c-9c31-45d0-8813-deae65fba143). The sandbox cannot discharge this: model bytes are absent, so U11 refuses readiness_identity_artifact_unreadable (observed, fail-closed).

- ED-QUAL-L1-2 (stable capability, after the B1 disposition is ruled): re-author the pack-side freeze evidence (scripts/author_arm_readiness_evidence.py), reissue freeze receipts, update plan-tree pins, and recommit on the production machine — must run there because evidence receipts derive kern.bootsessionuuid and monotonic time from the arming host; any reboot decision is Ed's.

## UNEXECUTED OBLIGATIONS (verbatim)

- joulewise/arm_readiness_evidence.py (freeze-side evidence author, 1,781 lines) not read line-by-line — its outputs were authenticated via the replay/authentication code and executed suites, not its authoring logic

- scripts/reserve_calibration_window_bracket.py not read — the ledger-reservation authority chain verified only at its consumption predicate (t0.ledger_reservation.v1 binding plan_sha256)

- joulewise/identity_pins.py internals not line-read — verified via executed CLI probe and the 42-test suite

- Full freeze-receipt semantic replay (_load_freeze_reference end-to-end) and dry-run receipt generation not executable in this sandbox (model bytes absent; evidence boot/monotonic-bound to the production machine) — deferred to ED-QUAL-L1-1

- No automated staleness detector for kernel.updated was built; the truth check was manual

