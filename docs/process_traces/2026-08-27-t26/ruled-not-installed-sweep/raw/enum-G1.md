# S9 enumeration — G1: D-117 … D-121

Source read verbatim: `docs/decision_log.md` index rows 142-146; bodies
7666-7726 (D-117), 8710-8732 (D-117 amendment / D-134), 7727-7795 (D-118),
7796-7831 (D-119), 7832-7869 (D-120), 7870-7904 (D-121). D-125 (8112-8137)
read for supersession only.

---

### D-117 · clause 1a
- clause (verbatim): "the never-zero `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3) BINDS every mint under this entry."  (the never-zero *mechanic*)
- source: docs/decision_log.md:7681-7684
- status: A
- evidence: scripts/mint_floor_artifact_generalized.py:2389-2400 — the mint recomputes `_v2_allowance_projection(...)` from the authenticated pre/post endpoints and raises `postcollection_evidence_mismatch: cached calibration allowance differs from authenticated endpoint derivation` when the pinned value disagrees.
- evidence: scripts/mint_floor_artifact_generalized.py:2198-2228 — `_v2_allowance_projection` derives `applied_allowance_s` / `bracket_screen_s` from the ISSUED acceptance via `issued_calibration_allowance_projection(...)` and re-renders `allowance_rule = f"max(observed_drift_s,{bracket_screen_s})"`; a non-derivable allowance raises.
- evidence: scripts/mint_floor_artifact_generalized.py:2577-2595 — step 10 compares `allowance_rule`, `bracket_screen_s`, `applied_allowance_s`, `observed_drift_s` against independently frozen pinset literals; comment states "There is no fill/default path; the closed pinset parser has already required all."
- evidence: joulewise/calibration_bracketing.py:282-290 — `acceptance_allowance_rule()` renders `max(observed_drift_s,<registered screen>)` from the generation registry, never from caller input.
- evidence: tests/test_mint_policy_resolver_guard.py:24 — `self.assertNotIn("0.010818", source)` (the resolver may not hard-code the literal).
- producer: `scripts/mint_floor_artifact_generalized.py` (`_issue_v2_multi_cell_floor_artifact` → `_v2_allowance_projection`)
- transaction_relevant: yes — this is the floor-mint allowance that every claim-bearing floor carries.

### D-117 · clause 1b
- clause (verbatim): "`A_s = max(observed_drift_s, 0.010818)`"  (the specific genesis literal as the binding screen)
- source: docs/decision_log.md:7682-7683
- status: D — superseded/amended
- evidence: docs/decision_log.md:8120-8127 (D-125 clause 2) — "**D-117 clause 1 is AMENDED for successor artifacts** from 'every mint uses max(drift, 0.010818)' to 'genesis lower bound + lineage-envelope rule'; the genesis literal remains binding as the floor and for every mint under the issued artifact."
- evidence (unenforced amended form, flagged not graded — D-125 belongs to another agent): `grep -rni "lineage|monotone|lower_bound" joulewise scripts --include='*.py'` returns only launch-lineage/campaign-provenance hits — nothing implements a monotone screen envelope or a `>= 0.010818` lower bound. joulewise/calibration_bracketing.py:172 sets `ACTIVE_ACCEPTANCE_ID = ANCHOR_V3_R6_ACCEPTANCE_ID`, whose registered `_D102_N17_DERIVATION` operative is `"bracket_screen_s": "0.009724"` (joulewise/calibration_bracketing.py:205-211) — BELOW the 0.010818 genesis screen the amendment names as the lower bound. D-145 (docs/decision_log.md:168) records the n=17 screens as deliberately "TIGHTENED", so this may be an intended reading of "strengthen"; either way no code compares a successor screen to the genesis bound.
- producer: `scripts/mint_floor_artifact_generalized.py` via `joulewise/calibration_bracketing.acceptance_bracket_screen_s`
- transaction_relevant: yes — the allowance floor on every minted comparative floor.
- note: D superseding cite is D-125 cl.2, docs/decision_log.md:8120-8127. The successor half of the amended rule has no producer-side check; hand to whoever owns D-125.

### D-117 · clause 1c
- clause (verbatim): "mint #1 and derivatives remain non-claim-bearing"
- source: docs/decision_log.md:7679-7681
- status: B — INSTALLED, NO PRODUCER-SIDE CHECK
- evidence: `grep -rn "mint1|mint #1|MINT1" joulewise scripts --include='*.py'` → one hit, scripts/mint_floor_artifact.py:2007 (`"""Authenticate, gate, construct, rebind, validate, and write mint #1."""`). No consumer or producer marks mint-#1 artifacts as claim-ineligible.
- evidence: joulewise/detection_floor.py:3019-3022 — the only version discrimination at claim consumption is `if provenance["mint_tool_version"] != _FLOOR_MINT_TOOL_VERSION_V2: errors.append(... "producer_calibration_plans: allowed only for the v2 multi-plan mint")` — a v1/mint-#1 shaped artifact is otherwise accepted.
- evidence: joulewise/detection_floor.py:2987-2988 — `elif assurance is not None: ... "assurance: allowed only for the v2 mint"` — i.e. absence of the v2 assurance block is legal, not refusing.
- evidence: joulewise/analysis_engine/inputs.py:930-939, 1207-1215 — the claim edge authenticates whatever floor artifact path it is handed; no allowlist of claim-bearing artifact ids/digests.
- producer: none found — nothing refuses a mint-#1 artifact at claim consumption.
- transaction_relevant: yes — claim edge / consumption edge.

### D-117 · clause 2
- clause (verbatim): "**Replacement: three compact prospective claim windows** — fresh 1.5B decode floor, fresh 7B decode floor, fresh 1.5B-vs-7B contrast — each with fresh §5A, live pre/post calibration receipts appended to the issued ledger, own verdict + head-pin + custody."
- source: docs/decision_log.md:7685-7695
- status: A
- evidence: `ls configs/campaigns` — `d117_floor_qwen25_1p5b_v3`, `d117_floor_qwen25_7b_v3`, `d117_contrast_qwen25_1p5b_vs_7b_v3` (plus retained v1/v2 generations).
- evidence: docs/process/state_kernel.json tasks `D117-W-ALPHA` / `D117-W-BETA` / `D117-W-GAMMA` (goals at lines 1018, 1069, 1120: "Run the frozen ALPHA pack … BETA … after ALPHA … GAMMA … after BETA").
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json `stage_graph[0].kind == "bracket_reservation"` invoking `--ledger`/`--head-pin configs/calibration/calibration_ledger_head.json`/`--plan .../calibration_plan.json` — the live pre/post bracket is a frozen pack stage, not an operator habit.
- evidence: scripts/mint_floor_artifact_generalized.py:2412-2424 (`_v2_authenticate_bracket_binding`) and :2577-2595 — the mint refuses unless the bracket binding, verdict cross-check, and `terminal_ledger_head_sha256` all authenticate.
- evidence (§5A): docs/phase_2/window_runbook.md:471 "## 5A. Pre-window clock stabilization (administrator step; Ed performs it)"; scripts/launch_window.py:113-140 refuses launch without a validated, freshly verified arm receipt (`launch_consumption_invalid`).
- producer: `configs/campaigns/d117_*_v3/generate_configs.py` (pack bytes) + `scripts/mint_floor_artifact_generalized.py` (claim artifact)
- transaction_relevant: yes — these are the three windows of the real transaction.

### D-117 · clause 3a
- clause (verbatim): "prefill FLOOR cells ride both floor windows (cheap, same members' prefill phase)."
- source: docs/decision_log.md:7696-7698
- status: A
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:52 — `PLAN_ID = "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3"`; :556-567 declare stages `04_phase_prefill_p256_absolute`, `05/06_phase_prefill_p256_abba_blocks_*`.
- evidence: docs/process/state_kernel.json:1018 — ALPHA goal names "its prefill floor rider"; :1069 the same for BETA.
- producer: `configs/campaigns/d117_floor_qwen25_*_v3/generate_configs.py`
- transaction_relevant: yes — pack contents of the alpha/beta windows.

### D-117 · clause 3b
- clause (verbatim): "The model contrast is DECODE-ONLY by default … A prospectively frozen ≥256-token prefill contrast arm remains an OPEN ED OPTION … not adopted here."
- source: docs/decision_log.md:7698-7705
- status: D — superseded
- evidence: docs/decision_log.md:147 (D-122) — "Ruling 4 RULED BY ED (reverses the standing recommendation): the paper is NOT decode-only — the contrast window (gamma) grows a prospectively frozen 256-token prefill ABBA arm".
- evidence (the supersession is realized in bytes): configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:476-485 — subcampaigns `03_prefill_p256_contrast_blocks_01_05` / `04_prefill_p256_contrast_blocks_06_10` with `"measurement_arm": "prefill_p256"`.
- producer: `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py`
- transaction_relevant: yes — gamma pack scope.
- note: superseded by D-122, docs/decision_log.md:147.

### D-117 · clause 4
- clause (verbatim): "**D-113 rewire:** its readiness dependency on the historical re-mint completing is REMOVED. The three-window P1 closure PRECEDES the broader MET-WINDOW-C-01 C2/C4/C5 replacement campaign".
- source: docs/decision_log.md:7706-7710
- status: B — INSTALLED (half), NO PRODUCER-SIDE CHECK
- evidence (removal half, installed): docs/process/state_kernel.json `tasks/MET-WINDOW-C-01/dependencies` lists only the FROZEN-PLAN-READINESS-RECORD arm-receipt dependency and ED-5A — no historical re-mint dependency remains.
- evidence (ordering half, NOT installed): docs/process/state_kernel.json — `MET-WINDOW-C-01` has `"rank": 1` in lane `quiet_mac`, while `D117-W-ALPHA/BETA/GAMMA` carry ranks 2/3/4 in the same lane and priority (`p1_phase_gate`). The kernel ordering says C-01 first, i.e. the opposite of the ruled precedence.
- evidence: docs/process/state_kernel.json `tasks/MET-WINDOW-C-01/authority` = `{"label": "D-113 clauses 7-9 …"}` and its `status_note` mentions only D-113 — neither the row nor its note records the D-117 rewire.
- evidence: TASK_QUEUE.md:577 and TASK_QUEUE.md:688 (the MET-WINDOW-C-01 row appears twice) cite only D-113 clauses 7-9; neither carries the D-117 precedence.
- producer: `docs/process/state_kernel.json` / `TASK_QUEUE.md` (hand-maintained; no generator or validator enforces the precedence)
- transaction_relevant: yes — window scheduling; a queue reader picking rank order would run C-01 before the three claim windows.

### D-117 · clause 5
- clause (verbatim): "**Naming:** 'Window D' is unavailable (collides with `runs_window_d_20260726` and D-113's reserved terminology); the three windows receive new immutable plan/root identifiers at plan freeze."
- source: docs/decision_log.md:7711-7714
- status: A
- evidence: `grep -rn "window_d|Window D" configs/campaigns/d117_*/plan_tree.json` → no matches.
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json `roots` = `{"bound_root_leaf": "runs_d117_floor_qwen25_1p5b_v3_bound", "claim_root_leaf": "runs_d117_floor_qwen25_1p5b_v3"}`.
- evidence (freshness enforced at the T-0 producer): joulewise/arm_readiness.py:7414-7426, :7484, :7502-7519 — `readiness_root_not_fresh` refusals on the `t0.fresh_roots_waivers` row, keyed off `roots.claim_root_leaf`; :7435 `readiness_waiver_set_nonempty`.
- evidence: configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.sha256 (sidecar) — the plan tree, and therefore the root leaves, is digest-frozen.
- producer: `configs/campaigns/d117_*_v3/generate_configs.py` (freeze) + `joulewise/arm_readiness.py` (T-0 freshness refusal)
- transaction_relevant: yes — arm readiness / window identity.

### D-117 · clause 6
- clause (verbatim): "**Option 1 (finite-allowlist historical candidacy) is PRESERVED as a versioned contingency ONLY**, requiring a rule-11 cold gate before any implementation … The historical corpora remain untouched on disk, non-claim-bearing per D-110 cl.1, logs sha-verified."
- source: docs/decision_log.md:7715-7720
- status: A (the prohibition half — realized by absence, shown below); the "non-claim-bearing" half is the same gap as clause 1c (B).
- evidence: `grep -rn "allowlist" joulewise/calibration_ledger.py joulewise/calibration_bracketing.py scripts/mint_floor_artifact_generalized.py` → only joulewise/calibration_bracketing.py:1277 (a capture-era allowlist) and the mint's `transport_allowlists` pins (scripts/mint_floor_artifact_generalized.py:989-1070) — no historical-candidacy allowlist exists.
- evidence: joulewise/calibration_ledger.py:2378 `_inspect_historical_candidate`, :2490 `_discover_historical_candidates` exist only inside the historical-IMPORT path (`joulewise.calibration_historical_import_table.v1`, :77), not in live candidate discovery (joulewise/calibration_bracketing.py:1284 `discover_calibration_candidates`).
- producer: none needed — the clause forbids an implementation, and none exists.
- transaction_relevant: no — a cold-gated contingency that was deliberately not built.

### D-117 · clause 7 (desk queue; enumerated sub-items)
- clause (verbatim): "**Unblocked desk queue** (consult §4): freeze three window plans + budgets; 1.5B decode floor plan from the proven 10-absolute/40-null design; generalized mint pinsets with per-plan six-decimal literals (the D-084 hard literal `7.377086` refuses any corrected mint under every option — closure is per-plan supply via the generalized path); extraction specs / order manifests / evidence-root ids / contrast manifest; synthetic three-window live-ledger integration regression; D-102 successor-artifact packet; results/methods prose placeholders."
- source: docs/decision_log.md:7721-7726
- status: A (all sub-items located)
- evidence (frozen plans + budgets): configs/campaigns/d117_*_v3/plan_tree.json carry `runtime_budget` and `stage_graph` keys, with `plan_tree.sha256` sidecars.
- evidence (six-decimal literals): scripts/mint_floor_artifact_generalized.py:98-99 `_SIX_DECIMAL_RE`/`_SIX_DECIMAL_QUANTUM`, applied at :2565-2576 when rendering the operative comparator; scripts/floor_mint_pinsets/schema_v2.json:740-743, :1025-1028 pin the per-plan literals as JSON-schema `const`s.
- evidence (D-084 retired literal refuses): scripts/mint_floor_artifact_generalized.py:97 `RETIRED_OPERATIVE_FLOOR_LITERAL = "7.377086"`; :442-444 `if value == RETIRED_OPERATIVE_FLOOR_LITERAL: raise MintError(f"{label} reuses retired literal …")`; test tests/test_mint_floor_artifact_generalized.py:9593 asserts `MintError, "reuses retired literal 7.377086"`.
- evidence (extraction specs / manifests / roots): configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json and d117_qwen25_7b_v3_extraction_spec.json; configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/{order_manifest.json, analysis_manifest_v3.json, consumer_family_declaration.json}.
- evidence (three-window regression): tests/test_calibration_live_three_window.py plus tests/fixtures/calibration_live_three_window/scenario.json.
- evidence (D-102 successor packet): configs/calibration/calibration_acceptance_d079_v2_r2.json (the `d079_calibration_acceptance_v2_n19_r2` successor generation registered at joulewise/calibration_bracketing.py:74).
- evidence (prose placeholders): docs/paper/draft-v1.md §6 "Demonstration results" (:384-425) and docs/paper/results-fill-registry.md.
- producer: `configs/campaigns/d117_*_v3/generate_configs.py`, `scripts/mint_floor_artifact_generalized.py`
- transaction_relevant: yes — pack bytes, pinsets and mint literals of the real transaction.

---

### D-117 amendment (D-134, 2026-08-12) · clause a1
- clause (verbatim): "The frozen `plan_tree.json` declares an `arm_attachments.arm_readiness` slot containing the D-134 contract/schema ID, the authoritative row-registry path/digest/profile, the pack-contained freeze-receipt path and digest, the deterministic external arm-receipt namespace, and the committed-pack digest algorithm."
- source: docs/decision_log.md:8712-8718
- status: A
- evidence: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/plan_tree.json `arm_attachments.arm_readiness` = `{contract_id: "D-134", required_before_arm: true, row_registry: {path: "configs/arm_readiness/d117_row_registry_v1.json", sha256: d248fdc5…, registry_id: "d117-row-registry-v1", plan_profile: "GAMMA"}, freeze_receipt: {path: "arm_readiness.freeze.receipts/freeze-0003.json", sha256: f32bd3a8…}, arm_receipt_namespace: "arm_readiness.receipts/arm-<4+ digits>.json", pack_digest_algorithm: "joulewise.committed_pack_tree_sha256.v1"}`.
- evidence: joulewise/arm_readiness.py:3930-3949 — `_require_exact_keys(value, {contract_id, required_before_arm, row_registry, freeze_receipt, arm_receipt_namespace, pack_digest_algorithm}, "arm_attachments.arm_readiness")` then raises `ArmReadinessError("readiness_row_registry_mismatch", "plan arm-readiness declaration differs from D-134")` on any deviation.
- producer: `configs/campaigns/d117_*_v3/generate_configs.py` (writes the slot) + `joulewise/arm_readiness.py` (refuses a wrong slot at arm time)
- transaction_relevant: yes — arm readiness.

### D-117 amendment · clause a2
- clause (verbatim): "The frozen plan never contains a future arm receipt's path or SHA-256."
- source: docs/decision_log.md:8718-8722
- status: A
- evidence: joulewise/arm_readiness.py:3938 — the exact-keys set admits only `freeze_receipt` (whose sub-keys are exactly `{path, sha256}`, :3949-3952); any arm-receipt path/digest inside the slot is an `extra` key and refuses.
- evidence: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/plan_tree.json — the slot holds `arm_receipt_namespace` (a pattern string), not a receipt path or digest.
- producer: `joulewise/arm_readiness.py` `_validate_plan_arm_readiness_declaration`
- transaction_relevant: yes — arm readiness / freeze bytes.

### D-117 amendment · clause a3
- clause (verbatim): "After all pack bytes are committed, the external arm receipt binds the completed pack digest and live evidence under `CUSTODY_ROOT/PACK_ID/arm_readiness.receipts/`."
- source: docs/decision_log.md:8723-8727
- status: A
- evidence: joulewise/arm_readiness.py:8041-8044 — `if namespace.name != "arm_readiness.receipts": … "arm receipt is outside arm_readiness.receipts"` (refusal).
- evidence: joulewise/arm_readiness.py:7584 `arm_namespace = custody_pack_root / "arm_readiness.receipts"`; joulewise/arm_readiness_evidence_t0.py:1560 same construction on the T-0 path.
- evidence: scripts/launch_window.py:173-183 — the launcher resolves the arm receipt and refuses one "outside the selected pack custody root".
- producer: `scripts/author_arm_readiness_evidence.py` / `joulewise/arm_readiness.py` (writes) + `scripts/launch_window.py` (refuses at consumption)
- transaction_relevant: yes — arm/arm-readiness and the launch edge.

### D-117 amendment · clause a4
- clause (verbatim): "The pack-pinned freeze receipt is non-authorizing."
- source: docs/decision_log.md:8723
- status: A
- evidence: joulewise/arm_readiness.py:6757 — `"""Write or idempotently authenticate the pack's non-authorizing receipt."""`
- evidence: joulewise/arm_readiness.py:7414-7519 — GO requires the separate `t0.*` row set (fresh roots, empty waivers, ledger reservation …); the freeze receipt alone never yields an arm receipt.
- producer: `joulewise/arm_readiness.py`
- transaction_relevant: yes — arm readiness.

---

### D-118 · clause 1
- clause (verbatim): "**THE GATE (all of it, every time; no item is discretionary):**" followed by enumerated items 1-11 (independent audit; paired distinct lenses; lead-written FIX contract; delta re-audit of every fix round; same-signature statement; Opus counter-review; apex Fable diff gate; overbuild/merge-ability prune; lead full-suite replay on the integration tree; final-head rule; CI green + post-merge cross-unit integration review).
- source: docs/decision_log.md:7745-7789
- status: C — NOT INSTALLED (outside the decision log itself)
- evidence: `grep -rni "gate ledger|gate_ledger"` over the repo excluding `docs/` → only RUN_STATE.md:635, :2860, :2873, :2912. No script, test, CI job, or checklist enumerates the items.
- evidence: `ls -a .github` → only `workflows/`; `find . -iname "*PULL_REQUEST_TEMPLATE*"` → no matches. There is no PR template to carry the items.
- evidence: `grep -n "gate|ledger" .github/workflows/ci.yml` → lines 246, 261, 388, 419, all about the determinism gate / required-check policy; nothing checks a merge gate ledger.
- evidence: `grep -rn "D-118" docs/orchestration.md docs/agent_playbook.md ~/.claude/skills/` → no matches in the process docs or skills that agents actually load. The operational gate shape they DO load, ~/.claude/skills/operation-loop/SKILL.md:255-274 (§5 Lead gates), is the older four-part (a)-(d) shape plus the final-head rule — it does not contain items 2, 5, 6, 7, 8, 9, or 11, and never mentions a ledger.
- producer: none found — merges are performed by `gh` at agent/operator discretion.
- transaction_relevant: yes — every _v4 transaction PR merges through this gate; an unenforced gate is the merge-time analogue of the D-157 shape.

### D-118 · clause 2
- clause (verbatim): "every PR description must carry a GATE LEDGER listing items 1-11 with the evidence path or commit for each, and any item marked NOT-RUN blocks the merge."
- source: docs/decision_log.md:7790-7794
- status: C — NOT INSTALLED
- evidence: same greps as clause 1 — no PR template, no CI job, no script parses a PR body for a gate ledger; the only occurrences of the phrase outside the decision log are narrative RUN_STATE.md lines (:2912 "checked by a per-PR GATE LEDGER; any NOT-RUN item blocks merge").
- producer: none found — the "mechanical enforcement" the clause names has no mechanism.
- transaction_relevant: yes — gates the merges that produce transaction code.

### D-118 · clause 3
- clause (verbatim): "A PR without a complete gate ledger is not merge-eligible regardless of CI state."
- source: docs/decision_log.md:7792-7793
- status: C — NOT INSTALLED
- evidence: .github/workflows/ci.yml has no ledger job; there is no branch-protection-shaped required check for a ledger (`grep -n "gate|ledger" .github/workflows/ci.yml` returns only determinism-gate lines 246/261/388/419).
- producer: none found.
- transaction_relevant: yes.

### D-118 · clause 4
- clause (verbatim): "The D-072 self-merge authority is CONDITIONED on this ledger being complete — it was never a license to merge on green alone."
- source: docs/decision_log.md:7793-7794
- status: C — NOT INSTALLED
- evidence: nothing conditions the merge path on a ledger; the only self-merge machinery is the untracked settings.local.json permission rule referenced in the user's memory, and `grep -rni "gate ledger"` finds no check.
- producer: none found.
- transaction_relevant: yes.

---

### D-119 · clause 1
- clause (verbatim): "The magistrate rules these directly and records them, without waiting on Ed."
- source: docs/decision_log.md:7805-7808
- status: B — INSTALLED, NO PRODUCER-SIDE CHECK
- evidence: rulings are in fact recorded — docs/decision_log.md:8238 ("D-119 conservative wording"), RUN_STATE.md:2733 ("`b0ee307` (D-119 conservative qualifiers + plain-language…)"), docs/council_log.md:3053.
- evidence: no artifact requires the recording — `grep -n "D-119|disclosure" scripts/render_results_fills.py scripts/make_figures.py` → no matches.
- producer: the magistrate by hand; no script or test.
- transaction_relevant: no — wording rulings, no measurement or byte effect.

### D-119 · clause 2
- clause (verbatim): "**The standing rule for those rulings: CONSERVATIVE BY DEFAULT.** When two honest phrasings are available, take the weaker one. … Where a stronger phrasing is actually warranted by evidence, it may be used — but the evidence is named in the same breath."
- source: docs/decision_log.md:7810-7817
- status: B — INSTALLED (as prose requirements on paper surfaces), NO PRODUCER-SIDE CHECK
- evidence: docs/paper/figures-plan.md:6 — "Captions must keep the D-119 conservative disclosure line"; :40 "**Mandatory D-119 disclosure line.**"
- evidence: docs/paper/results-fill-registry.md:120 ("`AUTH` — docs/decision_log.md, D-119 and D-121 through D-124. D-119 requires…"), :550 ("Keep D-119 conservative wording attached to every rendered figure, table…").
- evidence (no check at the producer): `grep -n "D-119|disclosure" scripts/render_results_fills.py scripts/make_figures.py` → no matches; scripts/claims_lint.py is structural only (its docstring: "Structural linter for JouleWise claims discipline artifacts"; no wording-strength vocabulary — `grep -n "demonstrated|designed|custody|third-party|verifiab" scripts/claims_lint.py` returns nothing).
- producer: `scripts/render_results_fills.py` / `scripts/make_figures.py` — neither refuses a figure or fill missing the mandatory disclosure line.
- transaction_relevant: yes — claim edge (published claim wording), though it moves no bytes.

### D-119 · clause 3
- clause (verbatim): "**What is NOT delegated** (unchanged, still Ed's): what to MEASURE, what to fund with quiet nights, scope decisions, venue and calendar, anything irreversible, and any ruling that changes what the project claims to have DONE rather than how it says it."
- source: docs/decision_log.md:7819-7823
- status: not an implementation clause (pure authority boundary; no artifact demanded)
- evidence: n/a
- producer: n/a
- transaction_relevant: no.

---

### D-120 · clause 1
- clause (verbatim): "`floor_mint_postcollection` is DELETED from production and fixture vocabulary; no producer is assigned; a report containing it (or any unknown key) REFUSES under a closed D-117 mint-consumption profile."
- source: docs/decision_log.md:7848-7851
- status: A
- evidence: `grep -rn "floor_mint_postcollection" .` (excluding .git) → zero hits in `joulewise/` or `scripts/`; the only live-code-adjacent hits are attack tests (tests/test_mint_floor_artifact_generalized.py:8369, :8447, :8456, :8609, :8651; tests/test_floor_extraction.py:515) and documentation (docs/phase_2/floor_mint_contract.md:175 "has no producer and is not part of the extraction …").
- evidence: scripts/mint_floor_artifact_generalized.py:2410-2420 — "Steps 8-9: the report is a closed cache. It may contain only governed extractor keys" → `profile_errors = validate_d117_mint_consumption_report(component.report)` → `raise MintError("postcollection_evidence_mismatch: closed D-117 extraction report profile refused: …")`.
- evidence (validator has a real producer-side caller, not just tests): `grep -rn "validate_d117_mint_consumption_report" joulewise scripts tests configs` → definition joulewise/floor_extraction.py:1571; production caller scripts/mint_floor_artifact_generalized.py:55 (import) and :2415 (call); all remaining hits are tests.
- evidence (test that would fail if removed): tests/test_mint_floor_artifact_generalized.py:8445-8449 — `run_refusal("coordinated-step8", "floor_mint_postcollection", …)`.
- producer: `scripts/mint_floor_artifact_generalized.py` `_issue_v2_multi_cell_floor_artifact` (steps 8-9)
- transaction_relevant: yes — the _v4-era floor mint.

### D-120 · clause 2
- clause (verbatim): "The mint verifies every pin against its DOMAIN OWNER and treats the extraction report as a cache requiring reauthentication, never an oracle. Verifier calculation is mandatory; pin generation is forbidden (missing pins refuse)."
- source: docs/decision_log.md:7852-7855
- status: A
- evidence: scripts/mint_floor_artifact_generalized.py:2427-2460 — after the profile check the mint builds a `_fresh_original_core()`, recomputes `absolute_false_effect_floor(...)` from authenticated member values and widths, and calls `mint_estimator.recompute_comparative_estimate(...)`, raising `postcollection_evidence_mismatch: comparative estimator recomputation refused` on any disagreement.
- evidence: scripts/mint_floor_artifact_generalized.py:2389-2400 — the cached calibration allowance is compared against the freshly authenticated endpoint derivation.
- evidence (missing pins refuse): scripts/mint_floor_artifact_generalized.py:324-341 `_object(value, label, expected_keys)` raises `"{label} schema mismatch: missing=[…]; extra=[…]"`; used for every pin object (e.g. :528-545, :609-627, :790-798); :2577-2579 comment "There is no fill/default path; the closed pinset parser has already required all."
- evidence (ledger/bracket domain owner): scripts/mint_floor_artifact_generalized.py:2412-2441 `_v2_authenticate_bracket_binding` → `validate_calibration_bracket_binding(...)`, refusing `bracket binding failed authenticated validation`.
- producer: `scripts/mint_floor_artifact_generalized.py`
- transaction_relevant: yes — the mint that produces claim-bearing floor bytes.

### D-120 · clause 3
- clause (verbatim): "The mint derives project commit/tree state by running git itself and refuses a dirty tree; origin/main containment of the mint commit is recorded evidence (unknown tolerated, never a gate)."
- source: docs/decision_log.md:7856-7858
- status: A
- evidence: scripts/mint_floor_artifact_generalized.py:1308-1345 `_actual_v2_git_state()` — runs `git rev-parse --verify HEAD` and `git status --porcelain --untracked-files=all`; `raise MintError("v2 issuance requires a clean Git working tree (dirty: …)")`; comment ":1337-1338 origin/main containment is recorded evidence, never a gate: an unresolvable upstream … records unknown" and the function returns `None` for containment on an unresolvable upstream.
- evidence: scripts/mint_floor_artifact_generalized.py:3904-3911 — `actual_head, origin_main_contains_head = _actual_v2_git_state()`; `if project_commit != actual_head: raise MintError("claimed project commit differs from the actual v2 mint Git HEAD")`; `if project_tree_state != "clean": raise MintError(...)` — the operator-supplied `--project-tree-state` (:4054) cannot lie.
- evidence (test that would fail if removed): tests/test_mint_floor_artifact_generalized.py:7768-7770 — `assertRaises(generalized.MintError, "clean Git working tree")` against `generalized._actual_v2_git_state()`.
- producer: `scripts/mint_floor_artifact_generalized.py` `_issue_v2_multi_cell_floor_artifact`
- transaction_relevant: yes — provenance stamped into minted claim bytes.

### D-120 · clause 4
- clause (verbatim): "Every v2 artifact carries the REQUIRED assurance qualifier (`single_authority_hash_bound_replay.v1`, independent_attestation false) stating what the system establishes and does not establish."
- source: docs/decision_log.md:7859-7861
- status: A
- evidence (producer emits): scripts/mint_floor_artifact_generalized.py:83-95 `V2_ASSURANCE_PROFILE = {"profile_id": "single_authority_hash_bound_replay.v1", "independent_attestation": False, "establishes": [...], "does_not_establish": [...]}`; written at :2855, :3066, :3270 (`"assurance": copy.deepcopy(V2_ASSURANCE_PROFILE)`).
- evidence (consumer refuses a wrong value): joulewise/detection_floor.py:1994 `_V2_ASSURANCE_PROFILE`, :1943-1948 `assurance` in the v2 provenance key set, :2975-2988 — `assurance != _V2_ASSURANCE_PROFILE` → `"must equal the canonical … single_authority_hash_bound_replay.v1 profile"`, and `elif assurance is not None: "allowed only for the v2 mint"`.
- evidence (present in real pack bytes): configs/campaigns/d117_floor_qwen25_1p5b_v1/arm_readiness.evidence/evidence-mint-trust.json:4 `"model": "single_authority_hash_bound_replay.v1"` (same in every d117 pack's readiness evidence and freeze receipts); joulewise/arm_readiness.py:119 uses the same model string.
- producer: `scripts/mint_floor_artifact_generalized.py` `_build_v2_artifacts`
- transaction_relevant: yes — every v2 mint artifact consumed at the claim edge.

### D-120 · clause 5
- clause (verbatim): "The honest trust claim is single-authority, hash-bound, fail-closed consistency — never operator independence (ADJUDICATION-TRUST-MODEL.md controls; the paper's §5/§11 language updated in the same change)."
- source: docs/decision_log.md:7862-7865
- status: B — INSTALLED (prose present), NO PRODUCER-SIDE CHECK
- evidence: docs/paper/draft-v1.md:445 (§7 Discussion and limitations) — "**Where the captures came from rests on trusting the operator.** … The system establishes machine-checked internal consistency and tamper evidence relative to disclosed bytes, not third-party-verified provenance."
- evidence: docs/paper/draft-v1.md:505 (§9 Evidence and code availability) — "This is experimenter-verified evidence designed for independent reanalysis; no uninvolved party has yet performed that reanalysis."
- evidence: docs/process_traces/2026-08-07-d117-u-units/ADJUDICATION-TRUST-MODEL.md exists (the controlling memo).
- evidence (no check): `grep -rln "single_authority_hash_bound_replay|single-authority" docs/paper` → no matches; the paper never names the machine-readable qualifier, and nothing verifies the paper against `V2_ASSURANCE_PROFILE`.
- producer: `docs/paper/draft-v1.md` (hand-written); no linter binds paper prose to the artifact's assurance block.
- transaction_relevant: yes — claim edge (the published trust statement).
- note: the clause names "§5/§11"; the current draft's section numbering has moved (the language now lives in §7 and §9). Recorded as installed under the new numbering.

### D-120 · clause 6
- clause (verbatim): "**Consequence:** the v2 mint remains BARRED from issuing until the executing branch passes the full D-118 gate and merges; U10 depends on this entry."
- source: docs/decision_log.md:7867-7869
- status: AMBIGUOUS — a temporal process bar, since discharged; no artifact enforces it
- evidence: the executing branch's code is on main — scripts/mint_floor_artifact_generalized.py:63 `V2_MINT_TOOL_VERSION = "joulewise.floor_mint.generalized.v2"` and the whole v2 issuance path exist at HEAD, so the bar's condition ("lands through the gate and merges") is satisfied by the tree state.
- evidence (no mechanical bar existed): no flag, env var, or guard in scripts/mint_floor_artifact_generalized.py conditions issuance on a gate ledger (`grep -rni "gate ledger|gate_ledger"` → nothing in scripts/).
- producer: n/a — process bar, never coded.
- transaction_relevant: yes — it gated the mint used by the transaction.
- note: best reading — a one-time sequencing condition that has been discharged, not a standing check. Flagged rather than graded A/B/C because no artifact was ever demanded.

---

### D-121 · clause 1
- clause (verbatim): "Nothing merges to main until the magistrate (the directing Fable instance) has personally reviewed the exact merge candidate — the final head, its full diff, and its completed gate ledger — AFTER every other gate item has finished."
- source: docs/decision_log.md:7875-7879
- status: C — NOT INSTALLED
- evidence: `grep -rn "Magistrate final review|item 12"` over the repo excluding process traces → only RUN_STATE.md:2648 (narrative) and docs/decision_log.md:146, :7881, :7884, :7891, :7901 (the decision itself). No template, script, CI job, or checklist.
- evidence: `ls -a .github` → `workflows/` only; `find . -iname "*PULL_REQUEST_TEMPLATE*"` → no matches.
- evidence: ~/.claude/skills/operation-loop/SKILL.md:255-274 (§5 Lead gates) — the loaded process doc's merge gate ends at "(d) CI green on the FINAL head" plus the final-head rule; it never mentions a terminal magistrate item or a ledger.
- producer: none found.
- transaction_relevant: yes — governs the merges of transaction code.

### D-121 · clause 2
- clause (verbatim): "**Terminal:** it is D-118 item 12, sequenced strictly after items 1-11 (including CI). A fix landing after it re-triggers it (the final-head rule composes: any new commit restarts at item 4's delta and ends at item 12 again)."
- source: docs/decision_log.md:7880-7884
- status: C — NOT INSTALLED
- evidence: same greps as clause 1; there is no ledger artifact in which an item 12 could be sequenced, and no automation observes commits landing after a review.
- producer: none found.
- transaction_relevant: yes.

### D-121 · clause 3
- clause (verbatim): "**Non-delegable:** delegated Fable subagent diff/final-head passes remain valid as EARLIER ledger items; they never satisfy item 12. The magistrate adjudicates and signs the ledger."
- source: docs/decision_log.md:7888-7892
- status: C — NOT INSTALLED
- evidence: no signing surface exists — `grep -rni "gate ledger|gate_ledger"` finds no ledger file, template, or schema anywhere in the repo outside RUN_STATE narrative.
- producer: none found.
- transaction_relevant: yes.

### D-121 · clause 4
- clause (verbatim): "**Ledger form:** item 12 reads 'Magistrate final review — <head sha>, <verdict>, <one-line disposition of any deferred items>.'"
- source: docs/decision_log.md:7901-7903
- status: C — NOT INSTALLED
- evidence: `grep -rn "Magistrate final review"` (excluding docs/process_traces) → RUN_STATE.md:2648 and the decision log only; no PR template or checklist carries the string, and no validator parses it.
- producer: none found.
- transaction_relevant: yes.
