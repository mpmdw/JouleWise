# RAW TRIAGE EXTRACT — L5-PACK-READINESS-CUSTODY

Source: docs/process_traces/2026-08-15-readiness-council/triage.json (seat entry `L5-PACK-READINESS-CUSTODY`)
Seat report: docs/process_traces/2026-08-15-readiness-council/seat-reports/

- seat verdict as reported: **NOT_READY**
- coverage: 16/18 (evidence_universe_count=18)
- findings: 5; falsifiers: 8

## FINDINGS (verbatim)

### F1 [should_fix] Floor-pack plan tests self-pollute the frozen packs and fail deterministically from a clean tree; CI-green status unexplained
- file_line: `tests/test_d117_floor_qwen25_1p5b_plan.py:30-35,259-264 (same pattern tests/test_d117_floor_qwen25_7b_plan.py:256)`
- failure_scenario (verbatim): python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan from a byte-clean tree: the module-import exec of the pack generator writes __pycache__/generate_configs.*.pyc INTO the frozen pack directory and the inventory test (rglob without a __pycache__ filter) fails — reproduced on python3.13 and CI's python3.11. Consequences: (a) the pack-integrity literal-pin layer (the main automated catch for committed plan_tree drift, per falsifier F6) is red or red-masked in CI — how #149 passed CI is unexplained and needs the CI log pulled; (b) any pre-arm plan-test run in the measurement checkout leaves __pycache__ inside the frozen pack, after which every committed_pack_tree_sha256 caller (t0 author, arm, consume) REFUSES 'untracked pack directory' until it is manually removed — a 3am tripwire (refusal executed live). The contrast test already carries the known fix (tests/test_d117_decode_contrast_plan.py:59-65, commit e286e75).

### F2 [should_fix] Generator --check echo hole in preserve mode: plan_tree.json, plan_tree.sha256, producer_contract.json are compared against themselves
- file_line: `configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:1803-1813,1987-1998 (7B :2185-2193, contrast :1683-1697)`
- failure_scenario (verbatim): With PRESERVE_CURRENT_FROZEN_BYTES true (the current state of all three frozen packs), generate() echoes the on-disk plan_tree.json/plan_tree.sha256/producer_contract.json into the 'generated' output, so --check's regeneration-drift comparison is void for exactly the pack-authority root files while still printing 'verified'. Executed: a committed sidecar-consistent plan_tree science-row tamper passes --check AND the freeze-reference replay (F6); the D-134 freeze receipt binds calibration_plan, registry, and evidence but NOT plan_tree bytes. Remaining catches are the plan-test literal (compromised per finding 1), the off-repo baseline manifest, and merge review. Work order: bind a plan_tree digest at freeze (e.g., hash of plan_tree minus the receipt attachment, recorded in the freeze receipt or projection receipt) or restore genuine regeneration comparison for the frozen members of these files.

### F3 [should_fix] Pre-arm sequence unregistered: measurement checkout must advance and the §5C dry-run must be re-executed at the final head (dry-run-0001 is stale by binding)
- file_line: `RUN_STATE.md:67-70 (ED-OWED), docs/process_traces/2026-08-13-freeze-execution/freeze-log.md (X-8), joulewise/arm_readiness.py:3402-3425`
- failure_scenario (verbatim): The measurement checkout sits at 49dcc49, which predates the arm-critical t0 evidence author (#149/ac3fe1d) — arming there fails immediately (script absent). After updating it, _latest_dry_run_binding requires the dry-run receipt to bind the CURRENT reviewed head + committed pack digest; dry-run-0001 binds 49dcc49/6246b618… so any arm at the baseline head refuses readiness_dry_run_stale (mechanically fail-closed, verified in code). Neither RUN_STATE's ED-OWED line ('chained ALPHA arm if GO'), the 70h plan, nor the ED-QUALIFICATION script registers the required steps: (1) fetch/advance the measurement checkout to the final reviewed head containing the t0 author, (2) re-execute the §5C under-lease dry-run there under the night's custody root, (3) then E-steps/t0/arm. The freeze log's X-8 wording ('the D-134 freeze + dry-run pair discharges the frozen readiness-validator role') invites an operator to believe the existing dry-run carries over; it does not.

### F4 [nit] --check prints 'verified unfrozen draft' on frozen packs
- file_line: `configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py:149-157,2168-2171`
- failure_scenario (verbatim): freeze_aware_status intentionally returns the byte-frozen legacy DRAFT_STATUS for the current frozen packs (M-2 byte preservation), so a frozen pack's successful check announces itself as an unfrozen draft — cosmetic operator-confusion risk already acknowledged by M-2 and alpha_arm_readiness.md.

### F5 [nit] M-2 decision-log remedy wording diverges from the implemented preserve-bytes behavior
- file_line: `docs/decision_log.md:8881-8891 vs docs/phase_2/alpha_arm_readiness.md:31-35`
- failure_scenario (verbatim): The decision log's remedy says the chain-fix batch 'regenerates the sidecar-consistent text via the canonical path', which reads as regenerating the frozen packs' text; the landed behavior (correctly) preserves frozen bytes and applies freeze-aware wording only to future packs, as alpha_arm_readiness.md states. A future session acting on the decision-log wording could try to rewrite frozen pack bytes; consistency-sweep material.

## WORK ORDERS (verbatim)

- WO-L5-1: Port the contrast test's __pycache__ exclusion (tests/test_d117_decode_contrast_plan.py:59-65) to both floor-pack plan tests, add a pack-pollution cleanup note to the runbook pre-arm section, and pull the CI log to determine how the failing modules reported green (if CI was red or skipped, record the process defect in the council log).

- WO-L5-2: Close the preserve-mode --check echo hole: bind plan_tree bytes at freeze (receipt-side digest of plan_tree-minus-attachment, or projection-receipt-side) OR restore genuine regeneration comparison for the frozen packs' plan_tree/producer_contract members; regression-test with the F6 tamper shape.

- WO-L5-3: Register the pre-arm sequence in RUN_STATE ED-OWED and the runbook D-117 amendment: advance the measurement checkout to the final reviewed head (>= ac3fe1d, contains the t0 author), re-execute the §5C under-lease dry-run at that head under the night's custody root, and only then begin E-steps; annotate the freeze log's X-8 line with the staleness caveat.

## ED-QUALIFICATION ROWS (verbatim)

- ED-QUAL-L5-1 (stable capability, any tap block): one non-window rehearsal of the t0 clock-attestation input handshake — Ed captures real `sudo systemsetup -getusingnetworktime` / `-setusingnetworktime off` outputs per runbook E-4/E-5 into a scratch arm_readiness.t0.inputs namespace and the lead validates them against the t0 author's capture validators (joulewise/arm_readiness_evidence_t0.py:838-861 _systemsetup_argv / _derive_clock_attestation). The authored tests use synthetic captures only; the first real sudo-output shape mismatch must not surface at T-0.

## UNEXECUTED OBLIGATIONS (verbatim)

- CI log verification for the floor-pack plan-test shard (no network in the audit sandbox): whether #149's CI genuinely ran and passed tests.test_d117_floor_qwen25_{1p5b,7b}_plan — finding 1 makes this the highest-value follow-up; a refuter with network should pull the actions log.

- Live execution of the arm-night receipt chain (generate_dry_run_receipt at the final head, author_arm_readiness_evidence_t0, generate_arm_receipt/verify/consume, U11 verify_frozen_projection with real model bytes): these require the measurement checkout at the final head, quiet machine, sudo captures, and custody writes — covered here only by the 58-test author/dry-run/lifecycle/integration suites and by code reading; they are the runbook's own T-0/lead work.

- Deep line-level read of joulewise/identity_pins.py internals (1,900+ lines): audited via its 25 passing tests, the frozen projection receipts' byte/pin verification, and the plan-tree inventory falsifier (F2 catch layer), not a full read.

- The arm-packet document under ~/JouleWise-window-custody/t4-session-20260810/ was located but not content-audited (seat 6-7 seam territory).

