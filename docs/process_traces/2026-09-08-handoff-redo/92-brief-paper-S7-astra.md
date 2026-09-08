**GENRE:** implementation  
**Mission:** Prepare the successor fill/migration inventory and current operating guidance, with first-use regression checks, without applying parked substitutions.

**Forcing problem:** `docs/paper/round7/fill-checklist.md:3` requires a fresh working copy and hash-bearing ledger. `docs/paper/round7/structural-edits.md:3` parks substitutions until live campaign-fill adjudication. `docs/paper/fill-rehearsal/branch-selection.md:29` advertises outcomes rejected by the current selector.

**WRITE_SCOPE:**
```json
[
  "docs/paper/round7/fill-checklist.md",
  "docs/paper/fill-rehearsal/branch-selection.md",
  "docs/paper/round7/successor-migration-inventory.md",
  "tests/test_paper_successor_migration.py"
]
```

**NEW:** `docs/paper/round7/successor-migration-inventory.md`; `tests/test_paper_successor_migration.py`.

**Deliverables and regressions:**

- Correct active instructions to describe the current methods/diagnostic selector. Label successor operations as pending adopted S1/S6 contracts.
- Inventory stale anchors, retired rows, transfer slots, prompt-ensemble assumptions, and common-time wording in the parked sheets. Record current semantic targets and required adjudications; do not edit or mechanically apply those sheets.
- Define future batch gates: fresh successor copy, complete supplier/placement checks, input/output hashes and replacement ledger, preserved historical replay fences, then assembled-paper first-use and Abstract checks.
- Use `docs/paper/round7/built-terms-lexicon.md` and `docs/paper/protocol/first-use-audit-ledger.md` as read-only sources for relocated first uses. Inventory operands, units, signs, sampling units, thresholds, figure encodings, and synthetic labels.
- Regressions reject active instructions to select A/B/REFUSAL today, fill retired rows, edit the frozen draft, bypass the ledger, or treat prospective counts as observed.
- A small synthetic relocation case must put a technical term before its construction and fail; its corrected control must pass. **Counterfactual:** checking only the old paragraph location or mechanically approving the parked sheet must not satisfy the migration check.
- Reconcile the inventory with adopted S1/S6 outputs before final closure; keep real text substitution explicitly pending live fill adjudication.

**Acceptance — named modules only:** `tests.test_paper_successor_migration`.

**Constraints:** D-173 `open_paper_input` remains mandatory for eventual empirical suppliers. No frozen-input or paper-text edits, measurement collection, repository-wide suite, or git commit. Preserve historical evidence and replay requirements; do not run external-corpus replay as this desk acceptance. Use scope/ruling early returns for unresolved work.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; `verdict.implementation=implemented|partial|no_change`, `verdict.acceptance=ready|pending_verification|needs_ruling`. State that migration preparation does not constitute empirical fill.
