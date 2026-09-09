WRITE_SCOPE: ["docs/contracts/paper_reported_energy.md","docs/contracts/paper_supply_custody.md","docs/paper/results-fill-registry.md","configs/paper_supply/supply_map.json","joulewise/paper_reported_energy.py","joulewise/paper_custody.py","joulewise/paper_rendering.py","tests/test_paper_reported_energy.py","configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py","configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py","tests/test_d117_floor_qwen25_1p5b_plan.py","docs/decision_log.md"]

# Paper desk lane S2 — reported-energy supplier increment, RELAUNCH with rulings (gpt-6-astra, HIGH, genre implementation)
Base: paper integration head e241e0b7 on branch feat/2026-09-08-paper-S2. Your intake run returned NEEDS_RULING (F1–F6); every ruling is now in the three-seat synthesis at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99be-coldgate-packet-paper-s2-semantics/13-magistrate-synthesis.md
(read it first; the seat rulings 10/11/12 beside it are evidence, the synthesis governs). RULINGS IN BRIEF: F1 launch-baseline anchors are superseded for this runner-owned lane (the wrapper snapshots its own baseline; do not block on BASELINE_MANIFEST/DIGEST). F2 mean = equal weight over the complete ordered 50-member universe, no admission filter, any missing/invalid member refuses the cell; independence unit = 20 (10 repeats + 10 complete ABBA blocks). F3 endpoints = m ∓ (h + B) with the STRATIFIED variance V = 0.2²·s_r²/10 + 0.8²·s_b²/10, ν = 9, and B = Σ kind averages of the registered deterministic bounds (absent kind → refuse); attribution floor published beside, never composed; the detection_floor.py prediction term excluded by name. F4 per-token = ΣE_i/ΣT_i over the same 50 members through a NEW phase_ratio_estimand object (existing ratio estimand untouched); fallback/absent/zero denominators refuse without dropping members. F5 register NOW in both v5 generators + the contract; numbers wait for the frozen spec; registration digest must predate the spec. Bind every registration to a cell_id (decode, prefill-p42, prefill-p512); the X5 rows stay RETIRED_FALLBACK — restore no placement. Add decision-log entry D-179 (dated 2026-09-08) recording rulings 1–7 of the synthesis verbatim-in-substance.
Additional magistrate constraints: (i) D-173 custody seam is the ONLY evidence entry; (ii) the synthetic control MUST compute the stratified half-width and show it differs from the pooled s/√20 form when s_r ≠ s_b (a named regression); (iii) mutation regressions include: 49-member mean (refuse), block-mean weighting 0.5/0.5 (value changes), zeroed bound kind (endpoints move), absent bound kind (refuse), prediction-term substitution (refuse by name), configured-token denominator (refuse), mean-of-ratios (value changes on the decode cell), reordered/duplicated member (refuse); (iv) acceptance rc-gated to a log: tests.test_paper_reported_energy tests.test_d117_floor_qwen25_1p5b_plan tests.test_paper_custody tests.test_gen_state tests.test_docs_freshness (drop nonexistent modules and say so; if gen_state EXPECTED_IDS/count pins fail because of D-179, update the pins in tests/test_gen_state.py ONLY IF it is in scope — it is not — so report NEEDS_SCOPE with the exact pin instead); (v) no commit; header < 8192 bytes; report per deliverable with file:line and the counterfactual per regression.

The brief-writer's original S2 brief follows verbatim for the deliverable shape:
## BRIEF S2

**GENRE:** implementation  
**Mission:** Build the reported-energy supplier’s bounded schema/projection increment and adversarial synthetic tests; make unresolved statistical choices explicit before registering an issuing gate.

**Forcing problem:** `joulewise/paper_rendering.py:41` expects `extraction_report.reported_energy_cells`, but `docs/paper/results-fill-registry.md:368` explicitly says the reported-mean schema, admitted member basis, composed intervals, and per-token fields remain undefined. `docs/contracts/paper_supply_custody.md:283` requires exact ordered members and all strict-bundle inputs.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_reported_energy.md",
  "docs/contracts/paper_supply_custody.md",
  "docs/paper/results-fill-registry.md",
  "configs/paper_supply/supply_map.json",
  "joulewise/paper_reported_energy.py",
  "joulewise/paper_custody.py",
  "joulewise/paper_rendering.py",
  "tests/test_paper_reported_energy.py"
]
```

**NEW:** `docs/contracts/paper_reported_energy.md`; `joulewise/paper_reported_energy.py`; `tests/test_paper_reported_energy.py`.

**Deliverables and regressions:**

- A proposed closed projection contract for the four model/phase cells and their twenty mean/endpoint/per-token/count outputs. Identify exact ordered membership, energy boundary, interval construction, and observed-token denominator.
- Implement independently settled identity, census, shape, and provenance checks now. If the owning contracts do not uniquely determine the mean basis, interval composition, or per-token aggregation, return a bounded `NEEDS_RULING` with alternatives; do not choose these by convenience.
- Keep the existing closed mint-consumption report schema intact. Use a distinct projection rather than inserting an invented field into an authenticated report.
- Authenticate selection/prompt pin, model, phase, frozen extraction specification, whole-window basis, and every strict member through the existing custody flow. Include new validators in the transitive source census.
- Mutation regressions: omitted/duplicated/reordered member, swapped model/phase, stale prompt pin, incorrect interval endpoint, fabricated token denominator, and count copied from a floor component. **Counterfactual:** each individually corrupted input must refuse even when its mean looks plausible; a complete synthetic control must produce the independently calculated projection.
- Preserve fixture roles as non-issuing. Map edits may document pending roles; do not add invented production digests or register the production energy gate before contract adoption.

**Acceptance — named modules only:** `tests.test_paper_reported_energy`.

**Constraints:** All paper evidence enters through `open_paper_input`; callers supply no evidence dict/path/digest bypass. No frozen measurement-input changes, collection, repository-wide suite, or git commit. Synthetic tests confer no production acceptance. No out-of-scope bookkeeping; use scope/ruling early returns when needed.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; `verdict.implementation=implemented|partial|no_change`, `verdict.acceptance=ready|pending_verification|needs_ruling`. Enumerate unresolved semantic fields rather than claiming an issuing supplier is complete.

