# L1 AUTHORITY PLANE — instrument-readiness audit report (xhigh seat)

**Charter:** docs/process/instrument-readiness-audit-charter.md (v2 RATIFIED, read first; anti-ritual packet complete below).
**Audit baseline:** docs/process/audit-baseline-manifest.json — HEAD `ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b` (= origin/main at manifest). Worktree head at audit time: `8937dec` (three post-baseline commits touching only README.md, RUN_STATE.md outside its generated region, and the manifest itself; `docs/process/state_kernel.json`, all three packs, and every gating module hash byte-identical to the baseline — verified below — so this seat's results are not voided by the drift; the sitting should confirm).
**Environment:** worktree sandbox, no network/sudo/live measurement; python3 = 3.13 (CI runs 3.11/3.14). Tree left byte-identical (`git status --porcelain` empty at exit; all probe artifacts under the session scratchpad).

## 1. Evidence universe (enumerated, before findings)

The control plane as a component:

1. docs/process/state_kernel.json (3,146 lines; sha `f85ea964…` = manifest) — EXAMINED (structure, all quiet_mac rows, targeted agent rows; 100% machine-validated via generator, ~40% read textually)
2. docs/process/state_kernel.schema.json — EXAMINED (full)
3. scripts/gen_state.py (826 lines; validator/canonicalizer/renderer, the kernel's sole code consumer) — EXAMINED (full)
4. RUN_STATE.md generated region (lines 3414–3439) — EXAMINED
5. TASK_QUEUE.md generated region (452–613) and the hand-written sections outside it (201, 635, 659) — EXAMINED
6. .github/workflows/ci.yml `gen_state --check` wiring — EXAMINED
7. tests/test_gen_state.py — EXECUTED (40 tests OK)
8. joulewise/arm_readiness.py (4,178 lines; D-134 two-stage receipts, D-137 boot binding, D-121 arm enforcement) — EXAMINED (~1,400 lines: constants/vocabularies, boot-session derivation, committed_pack_tree_sha256, freeze load/replay, row evaluation and predicates, arm generate/verify/consume, verify_receipt)
9. configs/arm_readiness/d117_row_registry_v1.json (D-134 cl.3 sole row authority; sha `d248fdc5…` = manifest) — EXAMINED (full: 3 profiles × 35 rows)
10. joulewise/identity_pins.py (2,072 lines; U11) — PARTIAL (CLI surface + executed probe + suite; internals not line-read)
11. scripts/project_identity_pins.py — EXAMINED (full) + EXECUTED
12. scripts/generate_arm_readiness.py — EXAMINED (CLI surface: freeze/dry-run/arm/verify/consume; no pin-accepting argument)
13. joulewise/arm_readiness_evidence.py (1,781 lines; freeze-side evidence author) — NOT LINE-READ (covered via executed suites + the authentication replay code in item 8)
14. joulewise/arm_readiness_evidence_t0.py (2,043 lines; arm-side author) — PARTIAL (row inventory; terminal-review derivation read in full)
15. scripts/author_arm_readiness_evidence.py, scripts/author_arm_evidence_t0.py — EXAMINED (CLI surfaces)
16. scripts/validate_gate_packet.py (cold-gate packet grammar) — EXAMINED (contract header)
17. Three D-117 packs (plan_tree + arm_attachments + freeze receipts + U11 projection receipts + evidence receipts + sources) — EXAMINED (targeted) + digests EXECUTED
18. docs/process/audit-baseline-manifest.json — EXAMINED (full); all 8 digests verified
19. Decision-log bindings: D-117 (+2026-08-12 amendment), D-118, D-121, D-131 (+refusal-registry amendment), D-132, D-133 (+cl.4 ratification, implementation notes, F1–F12 addendum), D-134, D-135–D-136, D-137, the 46-code D-078 registry amendment, M-1/M-2 rulings, window-gating directive, interaction contract — EXAMINED
20. tests.test_arm_readiness_lifecycle / _registry / test_identity_pins — EXECUTED (42 tests OK)
21. scripts/reserve_calibration_window_bracket.py — NOT EXAMINED (its consumer predicate `t0.ledger_reservation.v1` binding plan_sha256 was verified instead)
22. FREEZE-FCM01.md (standing prohibition banner) — EXAMINED
23. .github/workflows/d117-production-proof.yml — EXAMINED (header/trigger posture)
24. TASK_QUEUE/RUN_STATE marker geometry vs hand-written content — EXAMINED

## 2. Coverage

**20 of 24** items examined (2 partial: identity_pins internals, evidence_t0 internals; 2 not read: arm_readiness_evidence.py line-level, reserve_calibration_window_bracket.py). Unexecuted obligations, plainly:

- joulewise/arm_readiness_evidence.py not read line-by-line (its outputs were authenticated via the replay code and executed suites, not its authoring logic).
- scripts/reserve_calibration_window_bracket.py not read; the ledger-reservation authority chain is verified only at its consumption predicate.
- joulewise/identity_pins.py internals not line-read; verified via CLI probe + 42-test suite.
- Full freeze-receipt semantic replay (`_load_freeze_reference` end-to-end) and dry-run generation not executable here: model bytes absent and evidence is boot/monotonic-bound to the production machine → ED-QUAL-L1-1.
- The `updated`-field truth check is manual; no automated staleness detector was built.

## 3. Executed probes

### Positive (mechanism works, shown by running it)
- `python3 scripts/gen_state.py --check` → exit 0 at the audited head (kernel canonical; both generated regions drift-free). CI runs the same check on every push/PR (ci.yml:26).
- All 8 manifest digests reproduced byte-exact: kernel, row registry, runbook (docs/phase_2/window_runbook.md), freeze manifest (docs/phase_2/three_night_freeze_manifest.md), acceptance artifact (configs/calibration/calibration_acceptance_d079_v2.json), and all three pack digests via `committed_pack_tree_sha256` — the 1.5B pack digest also reproduced from a fresh scratch git repo (content-derived, not repo-bound).
- Freeze receipts: all three packs PASS, 14 rows, 0 refusals, plan-tree pin exact (path+sha); arm attachment declares the namespace slot with **no** future arm path/sha (D-134 cl.2 / D-117 amendment as written).
- D-133 cl.4 re-spec present in frozen bytes: estimator identity derives `d124_two_shared_edge_common_mode.v1` from the frozen plan; `cli_estimator_id_accepted: false`.
- Boot-session ground truth: live `kern.bootsessionuuid` equals the freeze receipts' `boot_session_id` (case-canonicalized by arm_readiness.py:729) — no reboot since freeze; D-137's derive-never-supply confirmed in code (:690–737) and data.
- 82 tests green: test_gen_state (40), arm_readiness lifecycle + registry + identity_pins (42).

### Negative / READY-falsification (minimum two required; fifteen executed)
1. **Seven illegal kernel states** (blocked-without-dep; queued-with-pending-hard-start; gate naming non-live task; duplicate lane rank; stop_card mismatch; dependency cycle; stop card outside docs/stop_cards/) → **all REFUSED** with exact diagnostics.
2. **Non-canonical kernel bytes** → `--check` exit 2 ("kernel bytes are not canonical").
3. **Forged row inside the generated region** (scratch copy) → exit 1 DRIFT; **duplicated marker pair** → exit 2 refusal.
4. **Pack tamper battery** (scratch git repo seeded with the real 1.5B pack): uncommitted byte-flip → `readiness_pack_digest_mismatch`; committed byte-flip → digest rotates (`f4c02c8a…` → `d24e68fe…`, so every frozen pin would mismatch); stray uncommitted namespace file → `readiness_pack_not_committed`; non-conforming committed receipt filename → `readiness_receipt_namespace_anomalous`.
5. **U11 without model bytes** (real CLI, real pack, scratch custody root) → REFUSE `readiness_identity_artifact_unreadable`; receipt written only under custody (pack read-only). (Printed exit code was masked by a head pipe; the receipt status is authoritative.)
6. **Arm-path READY-falsification — found a real launch blocker:** census of all pack evidence receipts vs live clocks: same boot session, but **all 33 freeze evidence receipts across the three packs are past `valid_until_monotonic_ns`** (earliest lapsed ~3.1 h before the probe; live monotonic ~1997.9e12 ns vs min 1986.8e12). Traced in code: `generate_arm_receipt` inherits `min(evidence expirations)` into the arm receipt (:3710–3717) → `verify_arm_receipt` refuses `readiness_record_expired` (:3952–3955) → `consume_launch_capability` can never fire. Fail-closed — but the audited frozen bytes cannot arm.
7. **Gate positive control:** a WINDOW-COUNCIL-GATE over quiet_mac (allowed_task_ids []) removes P2-006 from `selectable_task_ids` — the machinery for blocker B2's fix exists and works.

## 4. Decision-ID bindings — enforced vs written

- **D-131 (identity projection):** ENFORCED. Exact-key no-self-hash receipt schema; append-only `identity_pin_projection.receipts/` with GNU sidecars; derive-never-enter holds at every CLI (no pin-accepting argument on project_identity_pins.py / generate_arm_readiness.py); non-conforming receipt filenames refuse (fix-round-4 rule, probed); U8 consumes U11 at arm (`_run_identity_arm_reverification` forces `desk.identity_pin_projection` reasons); all five IDENTITY refusal codes present in the closed 46-code registry.
- **D-134 (two-stage receipts):** ENFORCED. Freeze receipt non-authorizing (loaded `require_pass=False` at arm; non-PASS appends `readiness_dependency_refused` → NO_GO); frozen bytes declare the arm slot, never future arm sha (verified in all three plan trees); registry is the sole row authority (sha-bound into every receipt; `readiness_row_registry_mismatch` on divergence); UNKNOWN absent from all closed vocabularies; dry-run can never occupy the arm slot (schema check at `_read_arm_with_sidecar` + `verify_receipt` refusal); PACK-sourced evidence structurally cannot satisfy `t0.single_launch_capability` (:2646–2655); ledger reservation must bind the pack's plan sha (:2636–2645); consumption is exactly-once via exclusive create, race loser → `readiness_record_consumed`; verify replays rows/refusals from authenticated evidence and refuses stale head/pack/registry/freeze bindings (:3755–3913).
- **D-137 (boot-bound expiry):** ENFORCED for arm receipts and arm-side evidence; boot session machine-derived, never operator-supplied. **Nuance found:** pack-side freeze evidence is checked for boot session but not directly for monotonic expiry at load; the expiry bites via inheritance into the arm receipt's validity — which is what makes finding B1 fail closed rather than fail open.
- **D-121 (terminal review):** ENFORCED at arm — `desk.terminal_review` derives from exact HEAD commit trailers (`JouleWise-Terminal-Review: PASS` + `-Tree-Oid` + `-Pack-Sha256` matching the live tree and pack digest; evidence_t0.py:913–943). NOT mechanically enforced at merge (see S1: D-118's ledger).
- **D-117 (packs) / D-133 (re-spec):** ENFORCED in frozen bytes (digests match manifest; tighter estimator derived from frozen plan). The kernel's description of this state is FALSE (B3).
- **Window-gating directive 2026-08-13 (council precedes any window):** **NOT enforced anywhere in the authority plane** (B2). The kernel's gate machinery exists precisely for this and carries no gate.

## 5. Findings (severity-tiered)

**B1 (blocker) — Frozen packs cannot arm: all 33 freeze evidence receipts monotonically expired on the un-rebooted arming machine.** configs/campaigns/*/arm_readiness.evidence/*; arm_readiness.py:3710–3717, 3948–3955. Scenario: tonight's arm generates a receipt born expired; verify refuses `readiness_record_expired`; consume never fires. Correctly fail-closed, but the funded window is unlaunchable under the audited bytes, and the standing 'NO REBOOT before T-0' constraint is insufficient — no reboot happened and the capability still lapsed (the window slip outlived the evidence validity horizon). The remedy (re-author evidence → reissue freeze receipt → re-pin plan tree → recommit) rotates the committed pack digests and **voids the manifest's pack digests under charter amendment 12** — the sitting must schedule the re-freeze and baseline re-pin explicitly.

**B2 (blocker) — Kernel fails open for quiet-window selection.** state_kernel.json `active_global_gates: []`; RUN_STATE.md:3433 renders "READY — Q2 P2-006: Window A two-model campaign" in [QUIET-MAC]. Ed's council gate exists only in decision-log prose; the actual funded program (three frozen packs) has no kernel row; P2-006 is a D-117-superseded program whose outputs would not trace to the current claim path. Probe-proven: the machinery suppresses the row the moment a gate is added — pure data gap.

**B3 (blocker) — Selection authority bifurcated; kernel content asserts falsehoods.** WO-MINT-ESTIMATOR-VOCAB (TASK_QUEUE.md:201), WO-COLLECTION-MARGIN-01 (:635), WO-ARM-EVIDENCE-AUTHOR-01 (:659, "LAUNCH-BLOCKING") are hand-written outside the generated region, invisible to `--check`, with no kernel rows — against DOC-008's single-authority contract. Meanwhile /tasks/D117-U11-IDPIN-PROJECTION still says "queued… Checked-in packs remain unprojected" at a head whose packs carry PASS projection + freeze receipts, and FLOOR-COMMONMODE-01 renders READY [AGENT] despite the D-133 disposition.

**S1 (should_fix) — D-118's "mechanical enforcement" of the gate ledger does not exist** (no checker in .github/ or scripts/); merge gating is agent discipline — the prose-only failure mode D-118's own trigger recorded.

**S2 (should_fix) — kernel.updated (2026-08-08) and latest_report (T3, 2026-08-09) are false**, and only date-format is validated; the render carries a false freshness signal.

**S3 (should_fix) — FREEZE-FCM01.md's prohibition banner ("Do not… register in any pack"; "only Ed may relicense") was never annotated after D-133 cl.4 EXECUTE**, while the packs lawfully register the estimator; the repo's own dated-supersession convention was not applied.

**N1 (nit) — plan_tree.json:793 `draft_status: "unfrozen_draft"` persists in frozen bytes**; no code consumer (verified); the M-2 scoped override is now permanent for these packs.

**N2 (nit) — gen_state.py:372 binds post-2M authority by label substring** ("D-041" in label) — lint-grade only.

## 6. Verdict: **NOT-READY** (component: authority plane), with work orders

The **machinery** is genuinely strong — every constructed illegal state, tamper, forgery, and namespace anomaly I threw at it refused with typed codes, the receipt chains replay from authenticated bytes, and the fail directions are uniformly closed. What is NOT ready is the **authority data and its maintenance**: the packs' arm capability has silently expired (B1), the kernel fails open for the exact action this audit gates (B2), and the selection authority has bifurcated into prose (B3).

**Work orders:**
- **WO-L1-1 (B1):** Ruled disposition for the expired freeze evidence: re-author pack evidence + reissue freeze receipts + re-pin plan trees + recommit on the production machine (ED-QUAL-L1-2), or amend the evidence-validity design by decision (e.g., freeze-side evidence bound to boot session only, monotonic expiry reserved for arm-side); then re-pin the audit-baseline manifest (amendment 12) and re-discharge the §5C committed-pack verification.
- **WO-L1-2 (B2):** Add WINDOW-COUNCIL-GATE to `active_global_gates` (scope quiet_mac, `allowed_task_ids: []`, authority = 2026-08-13 directive, clearance = council READY + T-0 GO); regenerate; remove only on the council verdict.
- **WO-L1-3 (B3):** Kernel truth pass: bump `updated`; correct `latest_report`; reconcile D117-U11-IDPIN-PROJECTION (landed — record evidence) and FLOOR-COMMONMODE-01 (D-133 disposition); enroll WO-ARM-EVIDENCE-AUTHOR-01 / WO-COLLECTION-MARGIN-01 / WO-MINT-ESTIMATOR-VOCAB as kernel rows (satisfied-with-evidence where landed); demote the hand-written TASK_QUEUE sections to pointers at their kernel rows.
- **WO-L1-4 (S1):** Build the PR gate-ledger lint, or amend D-118's mechanical-enforcement clause to state the truth (procedural enforcement).
- **WO-L1-5 (S3):** Dated supersession banner on FREEZE-FCM01.md citing the D-133 cl.4 execution ratification.

## 7. ED-QUALIFICATION rows

- **ED-QUAL-L1-1:** Same-boot production replay of the freeze chain: `generate_arm_readiness.py verify` per pack + `project_identity_pins.py verify` with real model bytes on the production Mac (stable capability; sandbox refuses fail-closed without model bytes — observed).
- **ED-QUAL-L1-2:** Execute the B1 re-author/re-freeze on the production machine once ruled (evidence receipts derive boot/monotonic identity from the arming host; reboot decisions are Ed's).

*Probe artifacts: scratchpad/l1/{kernel_falsifiers.py, drift_probes.py, pack_probes.py, tamper_probe.py, custody/}. Tree byte-identical at exit (`git status --porcelain` empty).*