WRITE_SCOPE: ["docs/contracts/paper_reported_energy.md","docs/contracts/paper_supply_custody.md","docs/paper/results-fill-registry.md","configs/paper_supply/supply_map.json","joulewise/paper_reported_energy.py","joulewise/paper_custody.py","joulewise/paper_rendering.py","tests/test_paper_reported_energy.py"]

# Paper desk lane S2 — reported-energy supplier increment (gpt-6-astra, HIGH, genre implementation)
Base: paper integration head e241e0b7 on branch feat/2026-09-08-paper-S2 (S1 placements contract docs/contracts/paper_comparison_placements.md and S6 rendering contract docs/contracts/paper_comparison_rendering.md are ADOPTED-AS-PROPOSED on this head: treat their placement rows and token families as the targets your projection must feed, and cite the rows you bind to). The brief below is the brief-writer's (trace 90 §BRIEF S2) verbatim; the magistrate adds: (i) the D-173 custody seam is the ONLY evidence entry (open_paper_input roles); (ii) every unresolved statistical choice (mean basis, interval composition, per-token aggregation) is returned as NEEDS_RULING with alternatives and the file:line evidence for each, NEVER chosen; (iii) acceptance is rc-gated to a log, never piped; (iv) no commit; header < 8192 bytes; report per deliverable with file:line and the counterfactual per mutation regression.

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

