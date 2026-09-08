WRITE_SCOPE: ["docs/contracts/paper_comparison_placements.md", "docs/contracts/paper_supply_custody.md", "docs/paper/results-fill-registry.md", "tests/test_paper_comparison_placements.py"]

**GENRE:** implementation  
**Mission:** Produce the proposed successor placement and custody specification for crosswalk obligations X1–X22, with executable table-agreement checks. Preserve current fallback behavior pending lead adoption.

**Forcing problem:** `docs/contracts/paper_supply_custody.md:101` requires every claim-bearing placement to have an explicit family/role binding, while its current table grants no comparison placements. `docs/paper/results-fill-registry.md:970` retains retired successor outcome slots. Their existence does not authorize reactivation.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_comparison_placements.md",
  "docs/contracts/paper_supply_custody.md",
  "docs/paper/results-fill-registry.md",
  "tests/test_paper_comparison_placements.py"
]
```

**NEW:** `docs/contracts/paper_comparison_placements.md`; `tests/test_paper_comparison_placements.py`.

**Deliverables and regressions:**

- A proposed placement table covering every X1–X22 obligation: semantic location, exact token/site identity, artifact field, family/role, required grant, applicability, missing-evidence behavior, and adoption status. Distinguish synthetic/schematic material from empirical placements.
- Explicitly mark floor-cell, measured-dependence, and characterization routes unresolved where no adopted family/grant exists. Do not invent a sixth family or infer grants from a related authenticated artifact.
- Add proposed successor rows alongside preserved dated retirement history. Keep proposals non-fillable until adoption; separate proposal tables from the live custody-bound census.
- Agreement regressions reject a missing obligation, duplicate placement, mismatched family/role, retired row treated as active, or empirical row with only a synthetic supplier. **Counterfactual:** deleting one obligation or changing one supplier in only one table must fail; the current retired rows must remain non-fillable.
- Include explicit schematic and synthetic dispositions for P1 and the P.2 illustrations, plus archive and availability obligations that cannot be licensed by a partial family census.

**Acceptance — named modules only:** `tests.test_paper_comparison_placements`.

**Constraints:** D-173: every empirical supplier obtains evidence through `open_paper_input`; this seat grants no production authority. Do not modify frozen measurement inputs or current paper text. No measurement collection, repository-wide suite, or git commit. Do not expand scope for bookkeeping. Return `NEEDS_RULING` for unresolved authority and `NEEDS_SCOPE` for necessary unlisted writes.

**Return contract:** First fenced JSON object: `schema="claude-codex-report/v1"`, `genre="implementation"`, UTF-8 size **<8192 bytes**. Use `verdict.implementation=implemented|partial|no_change` and `verdict.acceptance=ready|pending_verification|needs_ruling`; report actual changed paths, verification, and flags. Contract preparation can be complete while adoption remains pending.
