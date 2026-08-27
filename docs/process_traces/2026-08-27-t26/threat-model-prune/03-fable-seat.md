# Blind Fable seat — THREAT-MODEL-PRUNE-01 (Fable 5, read-only). Verbatim.

**THREAT-MODEL-PRUNE-01 — blind Fable seat (read-only; from code)**

Method: four partitioned surveys (collection core, provenance/identity, scripts+CI, tests) plus spot-checks. Every file:line below was read. ~2,200 raise sites exist; this lists mechanisms, not sites.

### A. PHYSICS/EVIDENCE — keep fail-closed
- Clock anchor: `floor_extraction.py:186` `clock_anchor_unresolved`; `quiet_window_clock.sh:75-101`; `check_paper_replay_fence.py:374-437,557-559` (absent corpus = exit 3, never pass).
- Fiducial/cadence/sampler: `powermetrics_fiducial.py:506`; `adapters/powermetrics.py:1306-1404,1731-2275`; `calibration_exits.py:98`; `sampler_teardown.py:362`; `ed_session/*.sh`.
- Calibration bracket / floor absence / transport-family: `floor_extraction.py:171-204`; `detection_floor.py:445,4295-4330`; `analysis_engine/artifact.py:2281-2646`.
- Idle/thermal/environment admission: `idle_admission.py:70`; `environment_admission.py:22`; `schemas.py:415,428`; `run_campaign.py:3821-3852,4052`; `prewindow_check.sh:76-204`; `window_status.sh:42-46`.
- Cooldown/anchor-shift envelope: `cooldown.py`, `floor_extraction.py:181-188,2055`; `analysis_engine/__init__.py:948-960`.
- Window physics/idle baseline: `reduce.py:243-305,2913-3522`; `window_duration_margins.py:97`; `load_transition_alignment.py:47`.
- Evidence-fixture digests: `test_analysis_claims.py:126`, `test_reduce.py:2092`, `verify_calibration_acceptance_corpus.py:25-63`; `d117-production-proof.yml:211-234`.

### B. PRE-REGISTRATION — keep fail-closed
- Plan bytes/plan tree pinned pre-collection: `arm_readiness.py:2443`; `calibration_exits.py:76-77`; `analysis_manifest_v3.py:303-329,3673` (prospective→finalized identity); `build_v4_histsem_pinset.py:143-144,154-179,196,267` (pre-authoring coordinate, freeze-0004, 11 receipts, 3 packs).
- m/n/α frozen: `multiplicity.py:25-151`; `registry.py:59-93,376,425`; `analysis_manifest.py:515-1068`; `ratio.py:271-283`.
- Floors not transported / composition frozen: `mint_floor_artifact_generalized.py:696-1073,1417`; `schema_v2.json` `not const 7.377086`.
- Reservation before capture / re-derive before output: `calibration_ledger.py` `RESERVATION_*`; `calibration_exits.py:88-93`; `output_identity.py:660-854`.
- Frozen pack-tree tests: `test_d117_decode_contrast_plan.py:825-839`, `test_d117_floor_*_plan.py`, `test_d117_v3_family.py:284`, `test_floor_mint_pinsets_schema.py:48-77`, `test_validate_gate_packet.py:167-316`.
- Claims prose discipline: `claims_lint.py:1785-1830`.

### C. OPERATOR-TAMPER — only actor is the trusted operator / same-UID process

| # | Mechanism (file:line) | Cost | Disposition |
|---|---|---|---|
| C1 | Histsem pinset: byte-pin + "no update lane" — `test_receipt_histsem.py:195-201` (literal `PINSET_SHA256`, `assertNotIn("--update")`), `:186-194` (token scan forbidding `fetch/unshallow/--update/checkout`); refusals `arm_readiness.py:3294-3352,3736-3913` | THE three hand edits + two blocked mints this week (D-161) | WARN-AND-RECORD via S14 refresh lane; test → "no UNREVIEWED update" |
| C2 | Shallow/promisor refusals `arm_readiness.py:3086-3095`, `identity_pins.py:932-948`; `ci.yml:17-21 fetch-depth:0` exists only for this | S3 D4 (WAVE-ROWS.md:16): a blobless clone lazy-fetches and PASSES anyway — the guard is already porous | KEEP as-is (cheap; also B: ordering proof of receipts). Do not build the D4 fix pre-night |
| C3 | Reviewed-tool tripwires: `_family_tool_reference` `arm_readiness.py:10933-11029` (`tool_mismatch`), `test_family_marker.py:768` (four `.sha256` sidecars; docstring: "nothing downstream reads these files") | Every edit to 4 scripts = sidecar regen + test edit | Sidecar test → RETIRE; production-lane `git show HEAD` bytes-equality → WARN-AND-RECORD |
| C4 | Mint-core interface pin `mint_floor_artifact_generalized.py:1443-1499` (30 globals + 8 signatures, `sys.modules` pop) | Any refactor of `mint_floor_artifact.py` refuses the mint | WARN-AND-RECORD (pinset `--pinset-sha256` at :1390-1414 stays — B) |
| C5 | `reduce.py` source-byte pin `test_authentication_io.py:78,349`; AST direct-read scan `:623-716` | Any reducer edit trips grandfather | RETIRE the source pin; keep the AST scan as warning |
| C6 | `gen_state.py --check` blocks, never regenerates (`:801-825`, `ci.yml:26`); `test_gen_state.py:346` exact live task-ID set (~150 literal lines) | Every queue mutation = test edit; part of the 122-clause backlog friction | ID-set test → RETIRE; `--check` → keep but auto-regenerate in CI with diff |
| C7 | Dirty-tree / reviewed-main refusals `arm_readiness.py:5161-5180,8187-8291`, `scheduler_gates.py:801-824` (G4), `identity_pins.py:788-810`, `release_check.py:47-56` | Blocks arm/mint on any untracked file (the "`git status` empty" trap) | KEEP for arm/freeze (also B: the frozen head IS the pre-registration coordinate); `release_check` → WARN |
| C8 | Symlink/`S_ISREG`/`O_NOFOLLOW`/path-escape guards (~40 sites: `arm_readiness.py:4931…8875`, `authentication_io.py:287-300`, `analysis_manifest_v3.py:1454-1507`, `analysis_engine/inputs.py:568-719`, `identity_pins.py:1211-1223`, `hydrate_d117_fixture.py`) | ~Zero; never fired on honest use | KEEP (free; also catches accidental cross-root reads = A) |
| C9 | Write-once / `O_EXCL` / no-overwrite lanes (`bundle.py:625-1130`, `arm_readiness.py:5054`, `identity_pins.py:1817`, `analysis_manifest_v3.py:3688`, `publication_privacy.py:1006`, `powermetrics.py:930`) | Zero on honest use | KEEP (A: evidence immutability) |
| C10 | TOCTOU re-checks (`provenance.py:139,250`; `authentication_io.py:375`; `arm_readiness_evidence.py:3469`; `arm_readiness_evidence_t0.py:46-52` freshness bounds; `publication_privacy.py:1033`) | The 20-min/6-h/1-h freshness bounds cost real re-runs at T-0 | Freshness bounds → WARN post-night; digest-stability → keep (bug catcher) |
| C11 | Launch-context / handoff-token guards (`arm_readiness.py:9175-9218,9366-9395`; `launch_window.py:134-267`; `readiness_record_consumed` :8591) | Runbook E-10 depends on them | KEEP through night; then WARN |
| C12 | Quiet-guard PID-custody / kinfo_proc ABI (`quiet_guard_process.py:226-590`), privileged-helper "root may not be an agent child" (`quiet_guard_privileged.py:94-172`) | Non-zero maintenance; `quiet_guard.py:83-88 arm` is a permanently dead lane | Dead lane → RETIRE; the rest KEEP (A: contamination census) |
| C13 | Registered campaign-policy tracked-file match `whole_window.py:3604-3617,5245` | Blocks a legit new policy until tracked | WARN |
| C14 | Forbidden-key / duplicate-key JSON (`authentication_io.py:142,211`; `determinism_gate.py:705`) | Zero | KEEP (A: ambiguous bytes) |
| C15 | Doc/prose tripwires: `test_launcher_argv_regression.py:26-52` (scrapes runbook fence), `test_calibration_exits.py:1511`, `test_capture_t0_step.py:787` (decision-log mention count), `test_quiet_guard.py:190,1443-1520`, `test_bridge.py:1590-1650`, `test_docs_freshness.py:186-272` | Docs edits go red; contributes to the 122 unenforced clauses (S9 census) by taxing enforcement authorship | RETIRE all but argv-regression (D-158 R-4 needs it) |
| C16 | Byte pins on editable configs/goldens: `test_schemas.py:843`, `test_suite.py:128`, `test_axi_*` SHAs, `test_arm_readiness_schemas.py:541`, `gensuite:172` bank hash, `ci.yml:131,196` timing ranges | Every example-config or golden edit | Convert to recompute-and-diff |
| C17 | Closed reason-code vocabularies (`identity_pins.py:172`, `registry.py:153`, `arm_readiness.py:1032-1128`) | Adding a code = registry edit | KEEP (developer-drift guard, cheap) |

### D. AMBIGUOUS
- `MOCK_TELEMETRY_CLAIM_REFUSAL` (`floor_extraction.py:212`): honest-mistake barrier vs relabelling guard — keep.
- `TRANSPORT_RULING_PENDING_REFUSAL` (`analysis_engine/__init__.py:1676`) and two-look refusal (`artifact.py:3405`): policy holds, neither A/B/C.
- Regeneration-vs-echo (`arm_readiness_evidence.py:1052-1273` allowlisted generator digests): B in intent, C in mechanism.
- `whole_window.py:2911` supersession override: the one licensed operator escape hatch.

### (i) Ranked prune list
1. C1 histsem no-update lane (S14). 2. C3 sidecar test. 3. C6 exact task-ID set. 4. C4 mint-core interface pin. 5. C5 reduce.py source pin. 6. C15 prose tripwires. 7. C16 config/golden byte pins → recompute. 8. C10 freshness bounds. 9. C13 policy-file match. 10. C12 dead `arm` lane. 11. `release_check` clean-tree. 12. `ci.yml:53-59,131,196` timing/exclusive asserts. 13. `test_capture_t0_step.py:787` decision-log count. 14. `test_calibration_exits.py:1749` self-AST scan. 15. `gensuite` bank hash.

### (ii) Must NOT prune before `_v4`
Anything in `arm_readiness.py`, `arm_readiness_evidence*.py`, `identity_pins.py`, `launch_window.py`, `capture_t0_step.py`: estate-11's S-0 runsheet anchors are **line-number-dependent** (`d139-families/01-estate-11-delta.md:28-40`), and runbook E-9/E-10 + step-6 recomputation (`window_runbook.md:840-900,984-1090`) consume C7, C11, the freshness bounds, and the histsem PASS. Also `test_launcher_argv_regression.py` (D-158 R-4) and `verify_receipt_histsem.py` in `ci.yml:28`. Everything in tests/ and scripts/ outside those files is safe now.

### (iii) §7 sentence
"The repository is tamper-evident for the operator's own benefit — every artifact carries a digest so drift and bugs surface — but it is not tamper-proof against anyone, and a single trusted operator is assumed."

### (iv) Strongest "C is really A/B" argument
C7's dirty-tree/`origin/main` refusal: the reviewed head is the pre-registration coordinate itself — a pack whose bytes differ from the published commit has no frozen plan, so this is B wearing a tamper costume. Corollary: C1's pinset mismatch against the pre-authoring coordinate (`build_v4_histsem_pinset.py:143`) is also B; only the *update-lane prohibition* is C.
