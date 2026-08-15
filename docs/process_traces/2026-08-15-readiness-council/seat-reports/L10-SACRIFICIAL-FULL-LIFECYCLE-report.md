# L10 — SACRIFICIAL FULL LIFECYCLE (xhigh) — seat report

**Audit baseline:** `docs/process/audit-baseline-manifest.json` (schema `joulewise.audit_baseline_manifest.v1`), manifest `head_commit ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b`. Worktree HEAD at execution: `8937dec9bd7be8f6d87694a739089ac8434b8bc9`. Drift between them verified by `git diff --stat ac3fe1d..HEAD`: **only** `README.md`, `RUN_STATE.md`, and the baseline manifest itself — none in this lens's scope, so results bind to the baseline. Frozen pack digests, row-registry sha, runbook sha (`25a4e809…` = `docs/phase_2/window_runbook.md`, located by hash), and acceptance sha cited from the manifest. Tree left byte-identical: `git status --porcelain` empty at exit; all rehearsal artifacts under the session scratchpad (`…/scratchpad/l10/`).

**Seat question:** drive a synthetic-but-shape-true window through reduce → verdict → floors → mint → claim consumption at the frozen configuration; prove the AFTER-window path exists and fail-closes BEFORE a window is spent; classify every refusal (correct vs gap); where synthetic data cannot legally pass, name the real-data property demanded.

**Component verdict: NOT-READY** — the machinery from collection through mint exists, runs, and fail-closes with enumerated, honest refusals at every gate (excellent), but the LAST edge — claim consumption of the frozen D-117 packs — is unbuilt (blocker F1), and two frozen §11 runbook commands refuse as written (F2, F3).

## 1. Evidence universe (enumerated before findings; 18 items)

1. Production collection surface `scripts/run_campaign.py` (stage mode) with mock runtime+telemetry adapters (synthetic-window author)
2. Environment preflight gate at frozen policy `configs/campaign_policies/quiet_mac_p2_production.json`
3. Bundle writer + `joulewise validate-bundle --strict`
4. `joulewise reduce` (re-reduction + immutability guard)
5. NEG-8 dual-family drift-bound mint (`--derive-neg8-drift-bound` + governed `configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json`)
6. Whole-window verdict (`--whole-window-verdict` at the frozen policy; row append; membership resolution incl. start/end reference-role requirement, `scripts/run_campaign.py:4950-5180`)
7. §9 D-100 salvage-dangler verdict dispatch
8. §10 `--record-supersession` flow
9. §11 duration-margins recorder `scripts/record_window_duration_margins.py` (+ `joulewise/window_duration_margins.py`) at frozen pack roots
10. §11 backup `scripts/backup_runs.sh`
11. §11 governed extraction `scripts/extract_detection_floors.py` + frozen spec `configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`
12. Floor mint v1 generalized `scripts/mint_floor_artifact_generalized.py` + `scripts/floor_mint_pinsets/mint1.json` + committed artifact `df-ph-decode-floor-mint1.json`
13. Floor mint v2 multi-cell aggregate route (`--v2-input-manifest`, `scripts/floor_mint_pinsets/schema_v2.json`)
14. Claim consumer `joulewise analyze-claims` (`joulewise/analysis_engine/*`, floor revalidation, structured outcomes)
15. Frozen packs' analysis manifests (3× `analysis_manifest_v3.json`, schema `joulewise.analysis_manifest.v3.prospective`) + `consumer_family_declaration.json` + final-v3 wire `joulewise/analysis_manifest_v3.py`
16. Pass-path proof suites: `tests/test_whole_window{,_selection}.py`, `tests/test_floor_extraction.py`, `tests/test_mint_floor_artifact_generalized.py`, `tests/test_analysis_claims.py`, `tests/test_analysis_integration.py`, `tests/test_window_duration_margins.py`
17. Runbook §§8–11 post-collection command surface (`docs/phase_2/window_runbook.md`)
18. Waiver→flagged verdict path (`--waivers`)

## 2. Coverage

**15 / 18 examined-and-executed.** Unexecuted obligations, plainly: #7 salvage dispatch (no synthetic salvage closure authorable without defeating its own authentication — correct), #8 supersession recording, #13 v2 aggregate CLI mint (suite-covered only), #18 waiver path; the CLI-level PASSED-basis chain is impossible from a sandbox (→ ED-QUALIFICATION ED-L10-1). Item 15 examined statically + by executed consumer refusal.

## 3. Rehearsal transcript (commands as pasted; venv = main checkout `.venv`, code = this worktree)

**Synthesis (positive).** 4 mock-family configs authored from `configs/examples/mock_local.json` (run IDs `l10-synth-decode-b01…b04`); collected via
`scripts/run_campaign.py <stage_dir> --runs-dir …/runs_window --log …/campaign_log.jsonl --campaign-policy tests/fixtures/campaign_policy_test.json --max-failures 1` → 4× `status=succeeded`, campaign log + provenance manifest written; each bundle `validate-bundle --strict` **valid**.

**Frozen-policy preflight (negative).** Same command with `--campaign-policy configs/campaign_policies/quiet_mac_p2_production.json` → `ENVIRONMENT PREFLIGHT FAILED: display_power_state='any_awake'`, exit 1, zero members. **Correct refusal**; property demanded: quiet-machine environment (displays asleep, AC, screensaver off…).

**Reduce.** `joulewise reduce <bundle> --output …/rereduce-b01.json` → artifact written (positive). `--output` inside the bundle → exit 2 `reduction output must be outside the immutable input bundle` (**correct**).

**NEG-8 bound mint.** `scripts/run_campaign.py --derive-neg8-drift-bound configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json --neg8-drift-bound-output … --runs-dir …/runs_window` → `error: NEG-8 corpus member is invalid, duplicated, or unsafe`. **Correct**; demands the 12 named settled reference members, strict-valid, in the bound root.

**Whole-window verdict (frozen §9 command).** `scripts/run_campaign.py --whole-window-verdict --runs-dir …/runs_window --log …/campaign_log.jsonl --campaign-policy configs/campaign_policies/quiet_mac_p2_production.json --neg8-drift-bound <absent path>` → exit 1, **failed row appended** (schema `joulewise.idle_admission_whole_window_verdict.v1`, policy sha `b0d7b228…`, basis sha `6902d456…`) with 10 enumerated conditions. **All correct refusals.** Real-data properties demanded, per condition: known adapter wattage (AC supply identity); ≥30 powermetrics CPU baseline samples per member; GPU idle admission; the final idle-admission attempt ledger; a protocol-v3 calibration bracket under `RUNS_ROOT/instrument_validation/`; NEG-8 start/end reference members; the dual-family derived bound artifact; campaign-manifest membership containing manifest-declared **start and end reference roles** (3+1+3 triplet) — verified in `scripts/run_campaign.py:5060-5072` (candidate requires `has_start and has_end`).

**Extraction (frozen spec).** Exact §11 runbook form (no `--consumption-semantics-id`) → argparse exit 2 (**finding F2**; refusal itself is correct CLI hygiene). Corrected form fed the FAILED basis sha + `d078_minted_envelopes_v1` → exit 1, all 6 frozen cells refused fail-closed (`whole_window_neg8_verdict_missing`, `bundle_missing`, `cpu_admission_core_missing`, `adapter_continuity_evidence_missing`), report written with `all_cells_extractable: false`. **Correct**: a failed verdict row for the exact named basis does NOT satisfy extraction; it demands a PASSED authenticated basis plus the spec's pinned member set (bundle IDs + config sha256 per member).

**Mint (v1 generalized, mint1 pinset).** Partial argv → exit 2 enumerating the 7 missing required pins (**correct completeness gate**). Full 19-argument invocation (pinset sha `4c58e646…`, plan located by pinned sha `e529a062…` = `configs/campaigns/p2_015_floors/calibration_plan.json`, both order manifests, both specs) with the refused synthetic report as both components → exit 2 `extraction report carries global refusal records` (**correct**). Wrong `--pinset-sha256` → exit 2 expected-vs-observed (**correct**).

**Margins recorder (§11 first command).** `--pack-identity` with runbook `$WINDOW_ID` convention and with the pack dirname → both `{"reason": "pack_identity_invalid", "status": "REFUSE"}`; with the true plan-derived `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` → advanced to `{"reason": "member_missing", "detail": "registered member 'd117c15v7-decode-contrast-b01-a1' is absent"}`. Refusals **correct** (REFUSE stops close-out, nothing written); the runbook/tool identity mismatch is **finding F3**.

**Backup.** `bash scripts/backup_runs.sh …/runs_window …/backup_dest` → exit 0, full copy (miscounts `campaign_manifests/` as a bundle: **nit F5**).

**Claim consumption.** (a) Gamma pack's own manifest → `error: unsupported analysis manifest schema_version: 'joulewise.analysis_manifest.v3.prospective'` (**blocker F1**, below). (b) Final splitwise v3 manifest + committed floor + synthetic root → exit 0, `claim_verdicts.json` with **honest structured refusal**: `outcome: not_estimable`, 14 reason codes, `claim_ready_for_l2_l3: false` (**correct**: no claim minted, every failed gate enumerated). (c) Floor artifact with `guarded_floor_j` tampered −1.0 J → exit 2 `stored guarded_floor_j does not match recomputed value`, nothing written (**correct**: consumer re-derives floors from artifact evidence). (d) Bundle summary byte-tamper → strict validation refuses via fresh re-reduction comparison (**correct**).

**Pass-path proof (positive, executed).** All seven governed suites at this HEAD: 15+251+176 = **442 tests passed** (+452 subtests, 2 platform skips) covering passed-verdict bases, admitted extraction incl. the checked-in production-path golden (`tests/fixtures/d117_postcollection_trust/extraction_report.json`), v1+v2 mint, and estimable claim consumption.

## 4. Refusal classification (charter requirement)

14 distinct refusal events observed. **12 CORRECT** (each names its gate and the real-data property demanded — see transcript). **2 expose gaps** while still failing closed: the §11 extraction argparse refusal (F2 — runbook command defect) and the prospective-manifest schema refusal (F1 — the refusal is right; the missing edge behind it is the blocker). None observed fail-open; no refusal was silent; every refusal left prior evidence intact.

## 5. Findings

- **F1 (BLOCKER).** The frozen packs' claim-consumption edge is unbuilt. All three packs ship `joulewise.analysis_manifest.v3.prospective`; `analyze-claims` refuses it (executed; `joulewise/analysis_engine/inputs.py:556-568`). The final-v3 wire is hard-pinned to splitwise: `validate_analysis_manifest_v3` requires `design_id: splitwise_decode_cross_model_abba_v1`, the splitwise generator path/plan sha, exactly two stages, n=10 (`joulewise/analysis_manifest_v3.py:630-663`); `build_analysis_manifest_v3` on the gamma pack refuses `root order-manifest bytes differ from the ratified pin` (executed). The U7 spec (DRAFT-U5U7.md §Prospective analysis-manifest repair) names `build_prospective_analysis_manifest_v3` / `validate_prospective_analysis_manifest_v3` plus five required postcollection attachments — **zero implementations exist** (repo-wide grep), and no TASK_QUEUE row tracks the edge (MANIFEST-CONTRAST-01 closed splitwise-only). Failure scenario: the gamma window is spent; its required contrast claim has **no governed consumer**; post-hoc code landing would collide with L1 custody discipline and the charter's trace-through-a-claim-consumer requirement.
- **F2 (SHOULD-FIX).** Runbook §11 extraction command refuses as frozen (missing `--consumption-semantics-id`). `docs/phase_2/window_runbook.md:1485-1491` vs `scripts/extract_detection_floors.py:100-106`.
- **F3 (SHOULD-FIX).** Runbook §11 margins-recorder `--pack-identity "$WINDOW_ID"` can never satisfy the recorder's plan-derived `window_id` requirement (`joulewise/window_duration_margins.py:374-379`); all three packs' true identities are `plan-d117-…-v1`, not the §4 `window_a9_YYYYMMDD` convention.
- **F4 (SHOULD-FIX).** L1 (extraction and floor-consuming analysis in one custody session; TASK_QUEUE FLOOR-BIND-01 fence, READY not closed) structurally conflicts with gamma's consumption of alpha/beta floors minted in earlier sessions. Needs FLOOR-BIND-01 closure or a prospective ruling **before** the windows.
- **F5 (NIT).** `backup_runs.sh:25-36` counts `campaign_manifests/` as a bundle (reported 5 for a 4-member window) — operator-facing miscount vs §12's count-by-bundle-ID rule.

## 6. Verdict and work orders

**NOT-READY.** The after-window path from collection through mint is real, executable, and fail-closed with enumerated honest refusals — the sacrificial rehearsal validated exactly the behavior a funded window needs from those stages. It is NOT-READY because the terminal claim-consumption edge for the frozen packs does not exist (F1), two frozen close-out commands refuse as written (F2, F3), and the L1/cross-window contradiction is unruled (F4). Work orders WO-1…WO-4 in the structured output; WO-1 must land (and be re-audited) before any window is spent. ED-QUALIFICATION ED-L10-1: desk replay of the full chain over a retained real corpus (Ed-held custody) to supply the CLI-level PASSED-basis positive proof.
