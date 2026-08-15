# L6 SEAM READER A — Producer→Consumer Obligation Graph (contract reader)

**Charter:** docs/process/instrument-readiness-audit-charter.md v2 (read first; F8 packet below).
**Audit baseline:** docs/process/audit-baseline-manifest.json, `head_commit ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b` = origin/main. Worktree HEAD is `8937dec`; `git diff ac3fe1d..8937dec --stat` touches ONLY README.md, RUN_STATE.md and the manifest itself — no code, contract, pack, registry or tooling bytes differ, so this lens's results are **not voided** by the post-manifest commits. Recomputed and matched against the manifest: state_kernel.json, d117_row_registry_v1.json (sha `d248fdc5…`), window_runbook.md (sha `25a4e809…`), acceptance artifact configs/calibration/calibration_acceptance_d079_v2.json (sha `31611396…`). Worktree left byte-identical (`git status --porcelain` empty at exit; all probes ran in $TMPDIR copies, cleaned).

**Method:** contracts/rulings first (runbook §§4–13 incl. D-134/D-117/D-100/D-079 amendments, D-117 plan-freeze DESIGN-MEMO, row registry, T6 five-layer specimen record, FINAL arm packet), then code verification of every seam, then executed probes.

## 1. Evidence universe (enumerated before findings)

40 artifact-class nodes across five planes of the chain (pack → arm → collection → post → governance). Node list = column 1 of the graph table in §3; the schema-ID census over `joulewise/`+`scripts/` (~120 IDs) was used as the enumeration cross-check, with off-chain families (AXI spikes, load-transition, wo003/wo005, publication capsule) excluded as out of this council's window-chain scope.

## 2. Coverage

**34 / 40 nodes examined** = producer and consumer located and at least spot-verified in code against the contract; 6 partial (frozen-plan instance off-repo/by-design absent; salvage artifacts lead-authored-by-design; claims-index deep trace; deep internals of ledger/capture/verdict owned by seats L2–L4; duplicate node; conditional privilege path). Unexecuted obligations listed plainly in the structured field (CLI-level freeze/arm/consume runs, live collection producers, synthetic extraction→mint, plan-identity question handed to L2).

## 3. THE OBLIGATION GRAPH

Legend: **P**=producer, **C**=consumer. ✔=verified in code this audit; ⊙=probed by execution; ✖=gap (finding); ◇=by-design human/absent.

| # | Artifact class (schema) | Producer | Consumer | Status |
|---|---|---|---|---|
| 1 | Campaign pack bytes ×3 (plan_tree.json, configs, order_manifest, condition_families, producer_contract) | pack generators (committed generate_configs.py) | run_campaign stages; arm_readiness `_plan_tree`; record_window_duration_margins; doctor; M-2 `--check` | ✔ |
| 2 | Row registry (arm_readiness_row_registry.v1, sha=manifest) | desk-committed config | arm_readiness.load_registry (freeze/dry-run/arm/verify) | ✔⊙ |
| 3 | arm_readiness.sources/* (arm_readiness_evidence_source.v1) | desk (committed) | pack evidence author; fact source re-auth at freeze/arm (`source_sha256` replay) | ✔ |
| 4 | PACK evidence receipts ×11 (arm_readiness_evidence_receipt.v1) | scripts/author_arm_readiness_evidence.py — **T6 X-1 gap CLOSED** | freeze eval; arm via freeze-receipt replay | ✔⊙ P2/F1/F2/F3 |
| 5 | U11 identity projection receipt (projection-0001.json) | scripts/project_identity_pins.py | freeze `_load_frozen_identity_evidence`; arm `_run_identity_arm_reverification` | ✔⊙ |
| 6 | Freeze receipt freeze-0001.json (arm_readiness_freeze_receipt.v1) | generate_arm_readiness.py freeze | plan_tree pin; `generate_arm_receipt` → `_load_freeze_reference` + `_freeze_evidence_for_arm` | ✔⊙ P2a/P2c |
| 7 | Committed-pack tree digest (committed_pack_tree_sha256.v1; includes evidence + receipts + sidecars per §4) | arm_readiness.committed_pack_tree_sha256 | dry-run/arm/verify/consume authentication | ✔ |
| 8 | Acceptance artifact (calibration_acceptance_bound.v2, sha `31611396…` = manifest) | desk issuance (historical) | §5B screen constant derivation (chain PRE_CAL_FIDUCIAL_MAX_S); acceptance evaluation code (L2/L4 deep) | ✔ sha |
| 9 | Extraction specs ×2 (configs/floor_mint/d117_*_extraction_spec.json) | desk (#144 re-spec) | extract_detection_floors --spec | ✔ |
| 10 | FROZEN_PLAN + window.env + stage lists + window-chain.zsh | §4/§6 desk freeze (operator, off-repo) | reservation CLI; session-status; chain; readiness plan-sha binding | ◇ (no instance yet, by design) |
| 11 | ALPHA/BETA/GAMMA Markdown matrices | mechanics | humans only — explicitly non-authoritative (§5C) | ◇ |
| 12 | **T-0 input files** — clock-attestation.json, arm-context.json, launch-manifest.json, 6 command captures (t0_command_capture.v1 etc.) | **✖ NONE — no tool, no runbook step, no packet step (B1)** | author_arm_evidence_t0 (fails closed — probed) | ✖⊙ P3 |
| 13 | T-0 sources (arm_readiness.t0.sources) | t0 author | evidence fact source re-auth at arm | ✔ |
| 14 | T-0 evidence receipts ×15, WINDOW_CUSTODY namespace | scripts/author_arm_evidence_t0.py — **T6 §0.6 gap CLOSED** | generate_arm_receipt `_discover_evidence` | ✔⊙ P1 |
| 15 | Dry-run receipt (dry-run-NNNN.json) | generate_arm_readiness.py dry-run | arm `_latest_dry_run_binding` → desk.under_lease_rehearsal; §5C lead verification; §12 | ✔ |
| 16 | Arm receipt arm-NNNN.json (300 s + min(evidence horizons) validity) | generate_arm_receipt | verify_arm_receipt; consume (boot + horizon + supersession + namespace checks) | ✔ |
| 17 | Launch-consumption receipt (.consumed.json) | consume_launch_capability (atomic, no-clobber) | double-consume fence; §12 close-out. **No launch-time machine consumer — BY DESIGN** (cold-gate ruling: arm authority is human, the capability licenses, never performs) | ✔◇ |
| 18 | Calibration ledger + head pin | reserve/writer/recover lifecycle | session-status; fiducial writer; t0 LEDGER_RESERVATION evidence | ✔ (deep=L2) |
| 19 | Bracket reservation/session rows | reserve_calibration_window_bracket.py --execute | writer lifecycle; session-status; readiness | ✔ (deep=L2) |
| 20 | Calibration capture custody (instrument_evidence.json, protocol v3) | validate_powermetrics_fiducial.py --allow-live | chain §5B screen (jq b_fiducial_s); §8 checks; verdict bracket; extraction/mint bracket binding | ✔ (deep=L3/L4) |
| 21 | NEG-8 corpus + settled manifest + neg8-drift-bound.json | chain bound stage + run_campaign --derive-neg8-drift-bound | --whole-window-verdict --neg8-drift-bound | ✔ |
| 22 | Run bundles (events.v2, powermetrics, provenance, dispatch_receipts, …) | controller via run_campaign stages | whole_window evidence maps; floor_extraction; aggregate | ✔ spot |
| 23 | campaign_log.jsonl | run_campaign | whole_window_refusal_reasons (authenticated jsonl read) | ✔ |
| 24 | Whole-window verdict row (idle_admission_whole_window_verdict.v1) | run_campaign --whole-window-verdict | extraction: exact basis sha + full bundle coverage + semantics-id filtering + provenance refusals | ✔ |
| 25 | Waivers.json (optional) | frozen basis (desk) | verdict --waivers → `flagged` (never claim-bearing) | ✔ |
| 26 | Operator logs (window-chain.log, slot logs) | chain | close-out/audit (human) | ◇ |
| 27 | Duration-margins receipt (window_duration_margins_receipt.v1) | record_window_duration_margins.py | **✖ no machine consumer** (writer + tests only); §12 human record (N1) | ✖ |
| 28 | **Postcollection backup receipts** (§12: path + SHA-256 per root) | **✖ NONE — backup_runs.sh emits an unhashed backup.log line only (S3)** | §12 close-out | ✖ |
| 29 | Salvage artifacts (salvage_closure.v1, whole_window_membership_binding.v1, exclusions) | lead-authored, exceptional D-100 path only — no tool, **by design** (runbook: lead-verified before the licensed re-evaluation) | run_campaign salvage mode; salvage_dangler loaders | ◇ |
| 30 | detection-floor-extraction.json (detection_floor_extraction.v1) | extract_detection_floors.py | mint (validate_d117_mint_consumption_report); results fills | ✔ |
| 31 | **Stage-1 desk pins (floor_mint_pin_requirements.v2)** | **✖ NONE EXECUTED — no committed instance (S2)** | only a non-mintable guard in the mint | ✖ |
| 32 | Final pinsets v2 ×3 + combined floor artifact (U10) | postcollection desk (future) | mint; gamma consumer pins; validate_floor_artifact; claims | ◇ correctly absent |
| 33 | Floor artifacts (floor_mint.generalized.v2) | mint tool | gamma consumer pinset; render_results_fills; claims docs | ✔ partial |
| 34 | results_fill_input.v1 → paper fills | desk dictated-fills | render_results_fills.py | ✔ |
| 35 | CLAIMS_STATUS / claims index | desk | claims_lint / release_check | partial |
| 36 | State kernel (sha=manifest) | desk governance | gate tooling | ✔ sha |
| 37 | Audit-baseline manifest | fleet launch | this fleet | ✔ |
| 38 | **FINAL arm packet** (off-repo custody, cited by manifest) | T6 mechanic | operator on the night | **✖ STALE (S4): no T-0 E-step; 'expect a refusal unless §0.6' — §0.6 is closed at this baseline** |
| 39 | Freeze log / FREEZE-FCM01.md / STOPPED-FCM01.md | freeze lane | audit | ✔ |
| 40 | d124 common-mode parameters | domain-hashed constants in detection_floor.py (not a produced artifact) | mint/extraction | ✔ |

**Zero-gap census over the readiness registry (P1, executed):** all 35 rows have a producer route; the five-layer specimen's two producer gaps (X-1, §0.6) are CLOSED at this baseline. The only kind with no producer anywhere is PRIVILEGE_INSTALLATION — N/A under the frozen MANUAL clock route (N2).

## 4. Executed probes

**Positive:** P1 registry×producer census (script over `_DERIVERS`/`_ROW_KIND`/registry JSON → NO rows without producer); P2a `validate_freeze_receipt` on committed freeze-0001.json → PASS/14 rows/12 items; P2b byte+sidecar replay of all 12 evidence items → 0 failures; P2c plan-tree pin == receipt sha → True; F2-live boot check → freeze boot `da90818c…` **is still the current boot** (no reboot since freeze); manifest sha recomputation ×4 → all match.

**Falsifiers (all refused, i.e. fail-closed proven):** F1 tampered evidence byte → `readiness_evidence_digest_mismatch`; F2b forced boot mismatch → `readiness_record_expired`; F2c forced past-horizon → `readiness_record_expired`; F3 deleted DOCTRINE_PIN kind → both dependent rows REFUSE; **P3 the documented night procedure itself** — t0 author invoked exactly per §5C with custody as the runbook leaves it → `evidence_author_t0_clock_attestation_missing`. **F2d live fact:** the committed freeze evidence is ALREADY horizon-expired on this very boot (monotonic now 1,996,764 s > valid_until 1,986,799 s, ≈2.8 h past at probe time).

## 5. Findings (file:line + failure scenarios in the structured findings field)

- **B1 (blocker).** The T-0 author's nine input artifacts have **no producer**: no capture tool writes `joulewise.arm_readiness_t0_command_capture.v1`/attestation/launch-manifest; `arm_readiness.t0.inputs/` appears in no operative document; the FINAL arm packet predates the author. Layer 6 of the T6 five-layer specimen class: *the producer-gap moved one seam upstream, into the inputs of the producer that closed §0.6.* Fails closed (P3) — a guaranteed NO-GO, and a standing temptation for hand-crafted JSON at 2 a.m.
- **B2 (blocker).** Committed freeze evidence is boot-bound AND already horizon-expired (F2d); the arm receipt inherits the expiry (min-fold) and verify/consume refuse. Every future funded window requires the full freeze-refresh lane (re-author → re-freeze → commit → review → re-dry-run, same boot, ≤24 h before ARM) — a lane no runbook section names, whose commits also void the audit baseline per amendment 12.
- **S2 (should-fix).** Stage-1 `floor_mint_pin_requirements.v2` (D-117 two-stage mint freeze) has no committed instance; absence is not failed closed — pre-registration value silently lost.
- **S3 (should-fix).** §12's hashed postcollection backup receipts have no producer (backup_runs.sh: unhashed log line; single-root §11 command vs two-root §12 obligation).
- **S4 (should-fix).** FINAL arm packet stale vs the baseline runbook (no T-0 E-step; obsolete §0.6 expectation).
- **N1 (nit).** Duration-margins receipt: no machine consumer; §11 ordering unenforced.
- **N2 (nit).** PRIVILEGE_INSTALLATION kind: no producer; safe only while clock_route stays MANUAL.
- **N3 (nit).** Arm-time freeze-evidence replay skips the horizon check; defense lives one hop downstream (min-fold + verify/consume). Real today, but thinner than it looks.

**Consumption-soundness statement (the council's question, answered for this lens):** across everything probed, **no missing, stale, tampered, or foreign artifact was silently consumed — every seam refused**. The gaps are all producer-side absences that guarantee refusal (B1, B2, S3) or lost pre-registration (S2), not consumption unsoundness. The chain fails closed; it currently cannot ARM.

## 6. Verdict

**NOT-READY**, with work orders WO-L6-1…5 (structured field): T-0 input capture helper + §5C amendment; governed freeze-refresh lane; packet regeneration; stage-1 pinset closure; hashed backup receipts. Two ED-QUALIFICATION rows emitted (live T-0 authoring under real sudo; timed freeze-refresh rehearsal). No READY-WITH-CONDITIONS exists; the packet above is complete per F8.

*Worktree byte-identical at exit; probes ran under $TMPDIR and were removed.*